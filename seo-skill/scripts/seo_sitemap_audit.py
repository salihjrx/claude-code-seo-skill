#!/usr/bin/env python3
"""Sitemap XML / sitemap index / text sitemap auditor (standard library only).

Reads a sitemap from a URL or from a local file, lists its entries as CSV and runs a set of
conservative, evidence-labelled checks ("Gözlendi" level: they describe what the file contains,
not whether a search engine will index, rank or even use a URL).

(Taken from SEO Apex; hardened while merging. The old CSV columns kind,loc,lastmod,changefreq,priority
are kept; new columns source,issues,alternates were appended.)
  * Network layer is netguard.py: SSRF defence on every redirect hop, size caps, bounded gunzip
    (the previous version had no SSRF guard and used an unbounded gzip.decompress).
  * DOCTYPE / ENTITY declarations are rejected (XXE / entity-expansion defence).
  * Namespace-agnostic parsing: a sitemap with a missing/wrong xmlns is still read AND reported
    (the previous version silently produced 0 rows).
  * Real checks instead of an inventory only: loc validity, localhost/staging leaks, host/scheme mismatch,
    duplicates, lastmod validity, protocol limits (50,000 URLs / 50 MB), sitemap-index misuse,
    and (optionally, --check-robots) URLs that robots.txt blocks for Googlebot.
  * --recursive follows a sitemap index (bounded), --urls-out writes a URL list for seo_url_audit.py,
    local files are supported (no network), --allow-private is needed for localhost.

Exit code: 0 = done, 1 = the sitemap could not be read OR a critical finding exists, 2 = usage error.
"""
from __future__ import annotations
import argparse, csv, json, math, os, re, sys, time
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import netguard  # noqa: E402
from seo_audit import LOCAL_HOST_RX, STAGING_HOST_RX, parse_robots  # noqa: E402

UA = netguard.UA  # backwards compatibility
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
MAX_URLS_PER_FILE = 50_000          # sitemaps.org protocol / Google limit
MAX_FILE_BYTES = 52_428_800         # 50 MiB uncompressed (same sources)
MAX_LOC_LEN = 2048                  # protocol: URLs must be < 2,048 characters
CHANGEFREQ = {"always", "hourly", "daily", "weekly", "monthly", "yearly", "never"}
CSV_FIELDS = ["kind", "loc", "lastmod", "changefreq", "priority", "source", "issues", "alternates"]
NOTICE = ("Sitemap denetimi 'Gözlendi' düzeyindedir: dosyanın içeriğini ve protokol uyumunu raporlar; bir URL'nin "
          "indeksleneceğini, sıralanacağını ya da sitemap'in kullanılacağını garanti etmez. Bulguları Search Console "
          "(Sitemaps / Sayfa indeksleme) ile birlikte yorumlayın.")

# code -> (level, message)   — levels share seo_audit.py's vocabulary
ISSUES = {
    "loc_empty": ("UYARI", "<loc> boş veya yok"),
    "loc_not_http": ("UYARI", "<loc> mutlak bir http/https URL değil"),
    "loc_credentials": ("UYARI", "<loc> içinde kullanıcı/parola var"),
    "loc_fragment": ("UYARI", "<loc> içinde # parçası var (parça, URL'yi ayırt etmez; kanonik URL'yi yazın)"),
    "loc_too_long": ("UYARI", f"<loc> {MAX_LOC_LEN} karakteri aşıyor (protokol sınırı)"),
    "loc_whitespace": ("BİLGİ", "<loc> başında/sonunda boşluk veya satır sonu var (çoğu işleyici kırpar; temizlemek daha güvenli)"),
    "loc_local": ("KRİTİK", "<loc> localhost/yerel adres içeriyor — canlıya geçmemeli"),
    "loc_staging": ("UYARI", "<loc> staging/test benzeri bir alan adı içeriyor — bilinçli mi? (Hipotez)"),
    "host_mismatch": ("UYARI", "<loc>, sitemap'in bulunduğu ana makineden farklı (protokol: tek ana makine; çapraz gönderim için robots.txt/Search Console gerekir)"),
    "host_www_mismatch": ("UYARI", "<loc> yalnızca www/www'suz farkıyla sitemap'ten ayrışıyor — tercih edilen sürümle tutarlı mı?"),
    "scheme_mismatch": ("UYARI", "<loc> sitemap'ten farklı şema kullanıyor (http/https karışık)"),
    "duplicate_loc": ("BİLGİ", "Yinelenen <loc> (aynı URL birden çok kez listelenmiş)"),
    "lastmod_invalid": ("UYARI", "<lastmod> W3C Datetime biçiminde değil (ör. 2026-10-18 veya 2026-10-18T09:30:00+03:00)"),
    "lastmod_future": ("UYARI", "<lastmod> gelecekte görünüyor"),
    "priority_invalid": ("BİLGİ", "<priority> 0.0–1.0 aralığında bir sayı değil"),
    "changefreq_invalid": ("BİLGİ", "<changefreq> geçerli değerlerden biri değil (always, hourly, daily, weekly, monthly, yearly, never)"),
    "blocked_by_robots": ("UYARI", "URL, robots.txt tarafından Googlebot için engelleniyor ama sitemap'te listelenmiş (Search Console'daki 'robots.txt tarafından engellendi' durumu)"),
}


class SitemapError(ValueError):
    """Sitemap okunamadı/ayrıştırılamadı (ağ erişimi dışındaki nedenler)."""


# ----------------------------------------------------------------------------- helpers
def _local(tag):
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


def _ns(tag):
    return tag[1:].split("}", 1)[0] if isinstance(tag, str) and tag.startswith("{") else ""


_LASTMOD_RX = re.compile(r"^(\d{4})(?:-(\d{2})(?:-(\d{2})(?:T(\d{2}):(\d{2})(?::(\d{2})(?:\.\d+)?)?(Z|[+-]\d{2}:\d{2}))?)?)?$")


def parse_lastmod(value):
    """W3C Datetime alt kümesi (YYYY, YYYY-MM, YYYY-MM-DD, ...Thh:mm[:ss[.s]]TZD) -> aware UTC datetime | None."""
    m = _LASTMOD_RX.match(value.strip())
    if not m:
        return None
    y, mo, d, hh, mi, ss, tz = m.groups()
    try:
        dt = datetime(int(y), int(mo or 1), int(d or 1), int(hh or 0), int(mi or 0), int(ss or 0))
    except ValueError:
        return None
    if tz and tz != "Z":
        th, tm = int(tz[1:3]), int(tz[4:6])
        if th > 23 or tm > 59:
            return None
        offset = timedelta(hours=th, minutes=tm)
        dt = dt - offset if tz[0] == "+" else dt + offset
    return dt.replace(tzinfo=timezone.utc)


def _strip_www(host):
    return host[4:] if host.startswith("www.") else host


# ----------------------------------------------------------------------------- parsing
def _parse_text(data):
    entries = []
    for line in data.decode("utf-8", "replace").splitlines():
        s = line.strip()
        if s:
            entries.append({"kind": "url", "loc": s, "lastmod": "", "changefreq": "", "priority": "",
                            "alternates": 0, "_ws": line != s})
    return "text", entries, []


def parse_sitemap_bytes(data):
    """-> (kind, entries, file_issues). kind: urlset | sitemapindex | text. Raises SitemapError."""
    if data.startswith(b"\xef\xbb\xbf"):
        data = data[3:]
    probe = data.lstrip()[:512]
    if not probe:
        raise SitemapError("Empty response body")
    if b"\x00" in probe[:64]:
        raise SitemapError("UTF-16/UTF-32 encoded files are not accepted (sitemaps must be UTF-8)")
    low = probe.lower()
    if low.startswith(b"<!doctype html") or low.startswith(b"<html"):
        raise SitemapError("Response is an HTML page, not a sitemap (soft-404, login or bot-protection page?)")
    if not probe.startswith(b"<"):
        return _parse_text(data)
    if re.search(rb"<!\s*(?:DOCTYPE|ENTITY)", data, re.I):
        raise SitemapError("DOCTYPE/ENTITY declarations are not accepted in sitemaps (XXE / entity-expansion defence)")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        raise SitemapError(f"XML parse error: {e}") from None
    tag = _local(root.tag)
    if tag in ("rss", "feed", "RDF"):
        raise SitemapError(f"Unexpected root element: {tag} (RSS/Atom feeds are valid Google sitemap formats but are not parsed by this tool)")
    if tag not in ("urlset", "sitemapindex"):
        raise SitemapError(f"Unexpected root element: {tag}")
    file_issues = []
    ns = _ns(root.tag)
    if ns != SITEMAP_NS:
        file_issues.append(("UYARI", "namespace_unexpected",
                            f"Kök öğenin ad alanı beklenen değil ({ns or 'tanımsız'}; beklenen {SITEMAP_NS}). "
                            "Dosya yine okundu ama protokole uygun değil; arama motorları işlemeyebilir (Search Console'da doğrulayın)"))
    want, other = ("url", "sitemap") if tag == "urlset" else ("sitemap", "url")
    entries, misplaced = [], 0
    for el in root:
        name = _local(el.tag)
        if name == other:
            misplaced += 1
            continue
        if name != want:
            continue
        fields = {"loc": "", "lastmod": "", "changefreq": "", "priority": ""}
        ws = False
        alternates = 0
        for sub in el:
            sn = _local(sub.tag)
            if sn in fields and not fields[sn]:
                raw = sub.text or ""
                fields[sn] = raw.strip()
                if sn == "loc" and raw != raw.strip():
                    ws = True
            elif sn == "link" and (sub.get("rel") or "").lower() == "alternate":
                alternates += 1
        entries.append({"kind": "url" if tag == "urlset" else "sitemap", **fields, "alternates": alternates, "_ws": ws})
    if misplaced:
        file_issues.append(("UYARI", "misplaced_element",
                            f"<{tag}> içinde {misplaced} adet <{other}> öğesi var; bunlar yok sayıldı "
                            f"({'URL' if other == 'url' else 'sitemap'} öğeleri yanlış kök altında)"))
    return tag, entries, file_issues


# ----------------------------------------------------------------------------- robots (opsiyonel kontrol)
@lru_cache(maxsize=4096)
def _pattern_rx(pattern):
    anchored = pattern.endswith("$")
    core = pattern[:-1] if anchored else pattern
    rx = ".*".join(re.escape(part) for part in core.split("*"))
    return re.compile(rx + ("$" if anchored else ""))


def robots_blocker(robots_text, token="googlebot"):
    """Google'ın en uzun-eşleşme kuralıyla url_engelli_mi(url) döndürür. Token'a ait grup yoksa '*' grubu kullanılır."""
    groups = parse_robots(robots_text)
    rules = [r for agents, rs in groups if token in agents for r in rs]
    if not rules:
        rules = [r for agents, rs in groups if "*" in agents for r in rs]
    compiled = [(kind, _pattern_rx(pat), len(pat)) for kind, pat in rules if pat]

    def blocked(url):
        p = urlparse(url)
        target = (p.path or "/") + (("?" + p.query) if p.query else "")
        best_len, best_kind = -1, "allow"
        for kind, rx, ln in compiled:
            if rx.match(target) and (ln > best_len or (ln == best_len and kind == "allow")):
                best_len, best_kind = ln, kind
        return best_kind == "disallow"

    return blocked


# ----------------------------------------------------------------------------- checks
def check_entries(entries, kind, base_url="", now=None, blocked_fn=None):
    """Her girdiye 'issues' (kod listesi) ekler; dosya düzeyi bulguları (level, code, message, count, example) döndürür."""
    now = now or datetime.now(timezone.utc)
    base = urlparse(base_url) if base_url else None
    seen = Counter()
    counts, examples = Counter(), {}

    def flag(entry, code, example=None):
        entry["issues"].append(code)
        counts[code] += 1
        examples.setdefault(code, example if example is not None else (entry["loc"] or entry.get("lastmod") or ""))

    for e in entries:
        e["issues"] = []
        loc = e["loc"]
        if e.get("_ws"):
            flag(e, "loc_whitespace")
        if not loc:
            flag(e, "loc_empty", "(boş)")
        else:
            p = urlparse(loc)
            if p.scheme not in ("http", "https") or not p.hostname:
                flag(e, "loc_not_http")
            else:
                if p.username or p.password:
                    flag(e, "loc_credentials", p.hostname)       # parolayı çıktıya yazma
                if "#" in loc:
                    flag(e, "loc_fragment")
                if len(loc) > MAX_LOC_LEN:
                    flag(e, "loc_too_long", loc[:80] + "…")
                if LOCAL_HOST_RX.match(loc):
                    flag(e, "loc_local")
                elif STAGING_HOST_RX.match(loc):
                    flag(e, "loc_staging")
                if base and base.hostname:
                    h, bh = p.hostname.lower(), base.hostname.lower()
                    if h != bh:
                        flag(e, "host_www_mismatch" if _strip_www(h) == _strip_www(bh) else "host_mismatch")
                    elif p.scheme != base.scheme:
                        flag(e, "scheme_mismatch")
                if blocked_fn is not None and e["kind"] == "url" and blocked_fn(loc):
                    flag(e, "blocked_by_robots")
            seen[loc] += 1
            if seen[loc] == 2:
                flag(e, "duplicate_loc")
            elif seen[loc] > 2:
                e["issues"].append("duplicate_loc")
                counts["duplicate_loc"] += 1
        lm = e["lastmod"]
        if lm:
            dt = parse_lastmod(lm)
            if dt is None:
                flag(e, "lastmod_invalid", lm)
            elif dt > now + timedelta(days=1):
                flag(e, "lastmod_future", lm)
        if e["priority"]:
            try:
                pv = float(e["priority"])
                if not 0.0 <= pv <= 1.0 or math.isnan(pv):
                    raise ValueError
            except ValueError:
                flag(e, "priority_invalid", e["priority"])
        if e["changefreq"] and e["changefreq"] not in CHANGEFREQ:
            flag(e, "changefreq_invalid", e["changefreq"])
    out = []
    for code, n in counts.items():
        level, msg = ISSUES[code]
        out.append((level, code, msg, n, examples.get(code, "")))
    return out


def file_level_findings(kind, entries):
    out = []
    n = len(entries)
    if n == 0:
        out.append(("UYARI", "empty", "Sitemap'te hiç girdi yok", 1, ""))
    if n > MAX_URLS_PER_FILE:
        out.append(("UYARI", "over_url_limit",
                    f"{n} girdi var; tek dosya sınırı {MAX_URLS_PER_FILE} (aşan dosya işlenmeyebilir — sitemap index ile bölün)", 1, ""))
    lastmods = {e["lastmod"] for e in entries if e["lastmod"]}
    with_lm = sum(1 for e in entries if e["lastmod"])
    if with_lm >= 10 and len(lastmods) == 1:
        out.append(("BİLGİ", "lastmod_identical",
                    f"Tüm {with_lm} girdide <lastmod> aynı ({next(iter(lastmods))}). Google lastmod'u yalnızca tutarlı ve doğrulanabilir "
                    "biçimde doğruysa kullanır; gerçek değişiklik tarihini yansıtmıyorsa değeri kaldırmak daha güvenlidir (Hipotez)", 1, ""))
    if any(e["priority"] or e["changefreq"] for e in entries):
        out.append(("BİLGİ", "ignored_fields_present",
                    "<priority>/<changefreq> var; Google bu alanları yok sayar. Zararsızdır, ancak bir etkisi olduğunu varsaymayın", 1, ""))
    return out


# ----------------------------------------------------------------------------- loading
def _unpack(data, truncated, max_uncompressed, size_note):
    """Gzip ise sınırlı biçimde aç; (data, notes) döndür. notes: file issue demetleri."""
    notes = []
    if data[:2] == b"\x1f\x8b":
        data, cut = netguard.bounded_gunzip(data, max_uncompressed)
        if cut:
            raise SitemapError(f"Decompressed size exceeds the {max_uncompressed} byte limit (compression-bomb defence)")
    if truncated:
        raise SitemapError(f"Download hit the {size_note} byte limit; the file is probably truncated "
                           "(raise --max-bytes; the sitemap protocol maximum is 50 MB uncompressed)")
    if len(data) > MAX_FILE_BYTES:
        notes.append(("UYARI", "over_size_limit", f"Dosya {len(data)} bayt; sınır {MAX_FILE_BYTES} (50 MB, sıkıştırılmamış) — bölün", 1, ""))
    return data, notes


def load_remote(url, *, timeout, max_bytes, max_uncompressed, allow_private, max_redirects=5):
    res = netguard.fetch(url, timeout=timeout, max_bytes=max_bytes, max_redirects=max_redirects,
                         allow_private=allow_private,
                         headers={"Accept": "application/xml,text/xml;q=0.9,text/plain;q=0.5,*/*;q=0.1"})
    if res.status != 200:
        raise SitemapError(f"HTTP {res.status}")
    data, notes = _unpack(res.body, res.truncated, max_uncompressed, max_bytes)
    ctype = res.headers.get("Content-Type", "").split(";")[0].strip().lower()
    if ctype and not any(k in ctype for k in ("xml", "gzip", "text/plain", "octet-stream")):
        notes.append(("BİLGİ", "content_type_unexpected", f"Content-Type beklenmedik: {ctype}", 1, ""))
    if res.hops:
        notes.append(("BİLGİ", "redirected", f"Sitemap URL'si {res.hops} yönlendirmeyle çözüldü: {' > '.join(u for u, _ in res.chain)} > {res.url}", 1, ""))
    return res.url, data, notes, res.status, res.hops


def load_local(path, *, max_bytes, max_uncompressed):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        raw = f.read(max_bytes + 1)
    data, notes = _unpack(raw[:max_bytes], len(raw) > max_bytes or size > max_bytes, max_uncompressed, max_bytes)
    return data, notes


# ----------------------------------------------------------------------------- orchestration
def _issue_dicts(items):
    return [{"level": lv, "code": c, "message": m, "count": n, "example": ex} for lv, c, m, n, ex in items]


def audit_target(target, *, recursive=False, max_sitemaps=25, delay=0.5, timeout=15, max_bytes=25_000_000,
                 max_uncompressed=MAX_FILE_BYTES, allow_private=False, check_robots=False, max_redirects=5,
                 row_sink=None, collect_urls=False, now=None):
    """Tek bir sitemap'i (URL veya yerel dosya) denetler; --recursive ise sitemap index çocuklarını da (sınırlı).

    row_sink(row_dict) her girdi için çağrılır. Dönüş: rapor sözlüğü (files, totals, sections, urls)."""
    is_local = os.path.isfile(target)
    if not is_local:
        netguard.check_destination(target, allow_private)           # BlockedError: ağ isteği yapılmadan reddedilir
    report = {"files": [], "totals": {"files": 0, "urls": 0, "sitemaps": 0, "critical": 0, "warnings": 0, "info": 0},
              "sections": {}, "urls": []}
    sections = Counter()
    queue = [target]
    queued = {target}
    robots_cache = {}
    fetched = 0
    skipped_children = 0

    def robots_fn(sm_url, origin_dir):
        """Bu sitemap için url_engelli_mi fonksiyonu veya None (robots.txt alınamadıysa)."""
        if is_local:
            rp = os.path.join(origin_dir, "robots.txt")
            if not os.path.isfile(rp):
                return None, "robots.txt, sitemap ile aynı klasörde bulunamadı"
            with open(rp, encoding="utf-8", errors="replace") as f:
                return robots_blocker(f.read()), None
        p = urlparse(sm_url)
        origin = f"{p.scheme}://{p.netloc}"
        if origin not in robots_cache:
            try:
                time.sleep(delay) if delay else None
                r = netguard.fetch(origin + "/robots.txt", timeout=timeout, max_bytes=500_000,
                                   allow_private=allow_private, max_redirects=max_redirects)
                if r.status == 200:
                    robots_cache[origin] = (robots_blocker(r.text), None)
                elif r.status in (404, 410):
                    robots_cache[origin] = (lambda _u: False, None)      # robots.txt yok = kısıtlama yok
                else:
                    robots_cache[origin] = (None, f"robots.txt alınamadı (HTTP {r.status})")
            except (netguard.FetchError, netguard.BlockedError) as e:
                robots_cache[origin] = (None, f"robots.txt alınamadı: {e}")
        return robots_cache[origin]

    while queue:
        item = queue.pop(0)
        if fetched >= max_sitemaps and fetched > 0:
            skipped_children += 1 + len(queue)
            break
        entry = {"source": item, "final_url": item, "kind": "", "status": "", "redirects": 0, "entries": 0,
                 "issues": [], "error": None}
        report["files"].append(entry)
        fetched += 1
        try:
            if os.path.isfile(item):
                data, notes = load_local(item, max_bytes=max_bytes, max_uncompressed=max_uncompressed)
                final_url, base_for_checks, origin_dir = item, "", os.path.dirname(os.path.abspath(item))
                entry["status"] = "file"
            else:
                if fetched > 1 and delay:
                    time.sleep(delay)
                final_url, data, notes, status, hops = load_remote(item, timeout=timeout, max_bytes=max_bytes,
                                                                    max_uncompressed=max_uncompressed,
                                                                    allow_private=allow_private,
                                                                    max_redirects=max_redirects)
                entry.update(final_url=final_url, status=status, redirects=hops)
                base_for_checks, origin_dir = final_url, ""
            kind, entries, file_issues = parse_sitemap_bytes(data)
        except (SitemapError, netguard.FetchError, netguard.BlockedError, OSError) as e:
            entry["error"] = str(e)
            continue
        entry["kind"] = kind
        entry["entries"] = len(entries)
        entry["bytes"] = len(data)
        issues = [(lv, c, m, 1, "") for lv, c, m in file_issues] + list(notes)
        if is_local and not base_for_checks:                       # yerel dosyada tutarlılık için ilk geçerli URL'yi baz al
            base_for_checks = next((e["loc"] for e in entries if urlparse(e["loc"]).hostname), "")
        blocked_fn = None
        if check_robots and kind != "sitemapindex":
            fn, why = robots_fn(base_for_checks or item, origin_dir)
            if fn is None:
                issues.append(("BİLGİ", "robots_unavailable", f"robots.txt karşılaştırması yapılamadı: {why}", 1, ""))
            else:
                blocked_fn = fn
        issues += check_entries(entries, kind, base_for_checks, now=now, blocked_fn=blocked_fn)
        issues += file_level_findings(kind, entries)
        if kind == "sitemapindex" and entry["source"] != target:
            issues.append(("UYARI", "nested_index", "Sitemap index başka bir sitemap index'i listeliyor (protokol buna izin vermez)", 1, ""))
        entry["issues"] = _issue_dicts(issues)
        report["totals"]["urls"] += sum(1 for e in entries if e["kind"] == "url")
        report["totals"]["sitemaps"] += sum(1 for e in entries if e["kind"] == "sitemap")
        for e in entries:
            if e["kind"] == "url" and e["loc"]:
                seg = urlparse(e["loc"]).path.split("/")
                sections["/" + seg[1] if len(seg) > 1 and seg[1] else "/"] += 1
                if collect_urls:
                    report["urls"].append(e["loc"])
            if row_sink:
                row_sink({"kind": e["kind"], "loc": e["loc"], "lastmod": e["lastmod"], "changefreq": e["changefreq"],
                          "priority": e["priority"], "source": final_url, "issues": ";".join(dict.fromkeys(e["issues"])),
                          "alternates": e["alternates"] or ""})
        if recursive and kind == "sitemapindex" and item == target:     # yalnız kök index'in çocukları izlenir (iç içe index protokole aykırı)
            for e in entries:
                child = e["loc"]
                if not child:
                    continue
                if is_local and not urlparse(child).scheme.startswith("http"):
                    continue
                if is_local:
                    local_child = os.path.join(os.path.dirname(os.path.abspath(item)), os.path.basename(urlparse(child).path))
                    child_target = local_child if os.path.isfile(local_child) else None
                    if child_target is None:
                        entry["issues"].append({"level": "BİLGİ", "code": "child_not_local",
                                                "message": "Alt sitemap yerel klasörde bulunamadı", "count": 1,
                                                "example": os.path.basename(urlparse(child).path)})
                        continue
                else:
                    child_target = child
                if child_target not in queued:
                    queued.add(child_target)
                    queue.append(child_target)
    for f in report["files"]:
        report["totals"]["files"] += 1
        for i in f["issues"]:
            key = {"KRİTİK": "critical", "UYARI": "warnings", "BİLGİ": "info"}[i["level"]]
            report["totals"][key] += 1
    if skipped_children:
        report["totals"]["not_fetched"] = skipped_children
    report["sections"] = dict(sections.most_common(15))
    return report


def sample_urls(urls, n):
    """Eşit aralıklı, deterministik örnek (n<=0 → hepsi)."""
    urls = list(dict.fromkeys(urls))
    if n <= 0 or len(urls) <= n:
        return urls
    step = len(urls) / n
    return [urls[int(i * step)] for i in range(n)]


# ----------------------------------------------------------------------------- CLI
def print_report(report, csv_path):
    for f in report["files"]:
        head = f"Sitemap: {f['source']}"
        if f["error"]:
            print(f"{head}\n  HATA  okunamadı — {f['error']}")
            continue
        print(f"{head}  [{f['kind']}, {f['entries']} girdi, {f.get('bytes', 0)} bayt]")
        for i in sorted(f["issues"], key=lambda x: ["KRİTİK", "UYARI", "BİLGİ"].index(x["level"])):
            tail = ""
            if i["count"] > 1 or i["example"]:
                tail = f" ({i['count']} adet" + (f"; örn. {i['example']}" if i["example"] else "") + ")"
            print(f"  {i['level']:<6} {i['message']}{tail}  [{i['code']}]")
    t = report["totals"]
    print(f"\nToplam: {t['files']} dosya, {t['urls']} URL girdisi, {t['sitemaps']} alt sitemap girdisi — "
          f"{t['critical']} KRİTİK, {t['warnings']} UYARI, {t['info']} BİLGİ")
    if t.get("not_fetched"):
        print(f"NOT: {t['not_fetched']} alt sitemap getirilmedi (--max-sitemaps sınırı)")
    if report["sections"]:
        top = ", ".join(f"{k} ({v})" for k, v in list(report["sections"].items())[:8])
        print(f"URL bölümleri (ilk yol parçası): {top}")
    print(f"CSV: {csv_path}")
    print(f"NOT: {NOTICE}")


def main(argv=None):
    netguard.setup_stdio()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="sitemap URL'si (http/https) veya yerel sitemap dosyası (.xml / .xml.gz / .txt)")
    ap.add_argument("-o", "--output", default="sitemap-audit.csv")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--max-bytes", type=int, default=25_000_000, help="indirilen dosya için bayt sınırı")
    ap.add_argument("--max-uncompressed", type=int, default=MAX_FILE_BYTES, help="gzip açıldıktan sonra bayt sınırı")
    ap.add_argument("--max-redirects", type=int, default=5)
    ap.add_argument("--recursive", action="store_true", help="sitemap index içindeki alt sitemap'leri de getir (sınırlı)")
    ap.add_argument("--max-sitemaps", type=int, default=25, help="--recursive için en çok dosya sayısı")
    ap.add_argument("--delay", type=float, default=0.5, help="ardışık getirmeler arası bekleme (sn)")
    ap.add_argument("--check-robots", action="store_true", help="URL'lerin robots.txt tarafından (Googlebot) engellenip engellenmediğine bak")
    ap.add_argument("--urls-out", help="URL listesini bu dosyaya yaz (seo_url_audit.py girdisi)")
    ap.add_argument("--sample", type=int, default=0, help="--urls-out için eşit aralıklı en çok N URL (0 = hepsi)")
    ap.add_argument("--json", action="store_true", help="özeti JSON olarak stdout'a yaz")
    ap.add_argument("--allow-private", action="store_true",
                    help="localhost/özel ağ hedeflerine izin ver (yalnızca KENDİ geliştirme sunucunuz için; varsayılan: reddedilir)")
    a = ap.parse_args(argv)
    if a.timeout <= 0 or a.delay < 0 or a.max_sitemaps < 1 or a.max_bytes < 1 or a.max_uncompressed < 1 or a.sample < 0:
        ap.error("--timeout >0, --delay >=0, --max-sitemaps >=1, --max-bytes/--max-uncompressed >=1, --sample >=0 olmalı")
    if not os.path.isfile(a.target):
        u = urlparse(a.target)
        if u.scheme not in ("http", "https") or not u.netloc:
            ap.error("Mutlak bir http/https URL veya var olan bir yerel dosya verin")
    with open(a.output, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        try:
            report = audit_target(a.target, recursive=a.recursive, max_sitemaps=a.max_sitemaps, delay=a.delay,
                                  timeout=a.timeout, max_bytes=a.max_bytes, max_uncompressed=a.max_uncompressed,
                                  allow_private=a.allow_private, check_robots=a.check_robots,
                                  max_redirects=a.max_redirects, row_sink=w.writerow, collect_urls=bool(a.urls_out))
        except netguard.BlockedError as e:
            print(f"ERROR: {type(e).__name__}: {e}", file=sys.stderr)
            return 1
    if a.urls_out:
        urls = sample_urls(report["urls"], a.sample)
        with open(a.urls_out, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(urls) + ("\n" if urls else ""))
    out = {"notice": NOTICE, "files": report["files"], "totals": report["totals"], "sections": report["sections"]}
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print_report(report, a.output)
        if a.urls_out:
            print(f"URL listesi: {a.urls_out} ({len(urls)} URL) — sıradaki adım: python seo_url_audit.py {a.urls_out}")
    root_failed = bool(report["files"]) and report["files"][0]["error"]
    if root_failed:
        print(f"ERROR: {report['files'][0]['error']}", file=sys.stderr)
    return 1 if (root_failed or report["totals"]["critical"]) else 0


if __name__ == "__main__":
    sys.exit(main())
