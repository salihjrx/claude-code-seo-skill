#!/usr/bin/env python3
"""
SEO denetim betiği (yalnızca Python standart kütüphanesi). Bu bir OTOMATİK TRİYAJ aracıdır.

Kullanım:
  python seo_audit.py <klasör>                       # klasördeki .html dosyalarını tarar (dist/, out/, build/, public/ veya statik site)
  python seo_audit.py --url https://site.com         # canlı sitenin ana sayfası + robots.txt + sitemap + sitemap'ten örnek sayfalar
  python seo_audit.py --url http://localhost:3000 --allow-private    # yerel geliştirme sunucusu (bilerek izin)
  python seo_audit.py <klasör> --json                # JSON çıktı

Önem düzeyleri:
  KRİTİK : yayın engelleyici olabilecek bulgu (ör. robots.txt tüm siteyi engelliyor, canonical localhost'a gidiyor)
  UYARI  : düzeltilmesi önerilir
  BİLGİ  : yönerge / iyileştirme önerisi (katı kural DEĞİLDİR)
Çıkış kodu: KRİTİK bulgu varsa 1, yoksa 0.

SINIRLAR (önemli): JavaScript çalıştırmaz; gerçek tarayıcı render'ını, tüm HTTP başlıklarını, Search Console/Analytics
verisini, indekslenme durumunu, içerik kalitesini ve backlink kalitesini DOĞRULAMAZ. Çıktıyı kanıt olarak kullan
(düzey: "Gözlendi"), nihai hüküm olarak değil. Etki ve indeksleme yorumları "Hipotez"dir.
"""
import argparse
import json
import os
import re
import sys
import time
from html.parser import HTMLParser
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import netguard  # noqa: E402

# Editoryal yönergeler. Google sabit karakter sınırı koymaz; başlık/snippet cihaza ve sorguya göre kısaltılabilir
# veya yeniden yazılabilir. Önemli olan benzersizlik, açıklık ve arama amacına uygunluktur.
TITLE_GUIDE = (30, 60)
DESC_GUIDE = (70, 160)

LEVEL_ORDER = ["KRİTİK", "UYARI", "BİLGİ"]
NOTICE = ("Otomatik triyaj: statik HTML/başlıklardan 'Gözlendi' düzeyinde bulgu üretir. JS render'ı, Search Console verisi, "
          "indeksleme, içerik kalitesi ve backlink kalitesini doğrulamaz. Bulguları kanıt olarak kullanın, nihai hüküm olarak değil.")

GENERIC_TITLES = {"react app", "vite + react", "vite + react + ts", "vite + vue", "vite app", "document", "untitled",
                  "untitled document", "index", "home", "create next app", "title", "new page", "my app"}
LOCAL_HOST_RX = re.compile(r"^https?://(localhost|127\.\d+\.\d+\.\d+|0\.0\.0\.0|\[::1\])(:\d+)?(/|$)", re.I)
STAGING_HOST_RX = re.compile(r"^https?://([^/]*\.)?(staging|stage|stg|dev|test|uat|preview|qa)\.", re.I)
HOSTING_SUBDOMAIN_RX = re.compile(
    r"^https?://[^/]+\.(vercel\.app|netlify\.app|pages\.dev|onrender\.com|herokuapp\.com|web\.app|firebaseapp\.com|github\.io|surge\.sh)(/|$)", re.I)
HREFLANG_RX = re.compile(r"^(x-default|[a-z]{2,3}(-[A-Za-z]{4})?(-([A-Za-z]{2}|\d{3}))?)$")
AI_BOTS = ("gptbot", "oai-searchbot", "chatgpt-user", "claudebot", "claude-searchbot", "claude-user", "perplexitybot",
           "perplexity-user", "google-extended", "ccbot", "applebot-extended", "bytespider")


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.meta = {}
        self.links = []          # (rel, href, hreflang)
        self.h = {1: [], 2: [], 3: []}
        self._cur_h = None
        self.imgs = []           # attrs dict
        self.anchors = []        # (href, text, attrs)
        self._cur_a = None
        self.jsonld = []
        self._in_jsonld = False
        self._jsonld_buf = ""
        self.html_lang = ""
        self.text_chunks = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.html_lang = a.get("lang", "") or ""
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or a.get("http-equiv") or "").lower()
            if key:
                self.meta[key] = a.get("content", "") or ""
        elif tag == "link":
            self.links.append(((a.get("rel") or "").lower(), a.get("href", "") or "", a.get("hreflang", "") or ""))
        elif tag in ("h1", "h2", "h3"):
            self._cur_h = int(tag[1])
            self.h[self._cur_h].append("")
        elif tag == "img":
            self.imgs.append(a)
        elif tag == "a":
            self._cur_a = [a.get("href", "") or "", "", a]
        elif tag == "script":
            if (a.get("type") or "").lower() == "application/ld+json":
                self._in_jsonld = True
                self._jsonld_buf = ""
            else:
                self._skip += 1
        elif tag in ("style", "noscript"):
            self._skip += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in ("h1", "h2", "h3"):
            self._cur_h = None
        elif tag == "a" and self._cur_a:
            self.anchors.append(tuple(self._cur_a))
            self._cur_a = None
        elif tag == "script":
            if self._in_jsonld:
                self._in_jsonld = False
                self.jsonld.append(self._jsonld_buf)
            elif self._skip:
                self._skip -= 1
        elif tag in ("style", "noscript") and self._skip:
            self._skip -= 1

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_jsonld:
            self._jsonld_buf += data
            return
        if self._skip:
            return
        if self._cur_h:
            self.h[self._cur_h][-1] += data
        if self._cur_a is not None:
            self._cur_a[1] += data
        self.text_chunks.append(data)


def jsonld_types(blocks):
    types, errors = [], 0
    for b in blocks:
        try:
            j = json.loads(b)
        except Exception:
            errors += 1
            continue
        items = j if isinstance(j, list) else [j]
        for it in items:
            if isinstance(it, dict):
                graph = it.get("@graph")
                for x in (graph if isinstance(graph, list) else [it]):
                    t = x.get("@type") if isinstance(x, dict) else None
                    if isinstance(t, list):
                        types.extend(t)
                    elif t:
                        types.append(t)
    return types, errors


def audit_html(html, label, x_robots=""):
    """Tek bir HTML metnini denetler. issues: [(düzey, mesaj, kod), ...]"""
    p = Page()
    try:
        p.feed(html)
    except Exception as e:  # bozuk HTML
        return {"page": label, "issues": [("UYARI", f"HTML ayrıştırılamadı: {e}", "html_parse_error")], "stats": {}}
    issues = []

    def add(level, msg, code):
        issues.append((level, msg, code))

    title = " ".join(p.title.split())
    desc = " ".join(p.meta.get("description", "").split())
    robots = (p.meta.get("robots", "") + " " + p.meta.get("googlebot", "")).lower()
    canons = [h for r, h, _ in p.links if "canonical" in r.split()]
    canon = canons[0] if canons else ""
    words = len(re.findall(r"\w+", " ".join(p.text_chunks)))
    h1s = [" ".join(x.split()) for x in p.h[1] if x.strip()]
    types, jerr = jsonld_types(p.jsonld)
    noindex = "noindex" in robots or "noindex" in (x_robots or "").lower()

    # --- Title (uzunluk yönergedir; benzersizlik/açıklık daha önemlidir)
    if not title:
        add("UYARI", "<title> yok (Google başlığı kendisi üretir; açıklayıcı, benzersiz bir title önerilir)", "title_missing")
    else:
        if title.lower() in GENERIC_TITLES:
            add("UYARI", f"Title varsayılan/jenerik görünüyor ('{title}'); sayfaya özgü, açıklayıcı bir title yazın", "title_generic")
        n = len(title)
        if n < TITLE_GUIDE[0]:
            add("BİLGİ", f"Title kısa ({n} krk). Yönerge ~{TITLE_GUIDE[0]}-{TITLE_GUIDE[1]}; sabit Google sınırı değildir, açıklık ve benzersizlik önemlidir", "title_short")
        elif n > TITLE_GUIDE[1]:
            add("BİLGİ", f"Title uzun ({n} krk). ~{TITLE_GUIDE[1]} üstü sonuç sayfasında kısaltılabilir; sabit sınır değildir", "title_long")
    # --- Description
    if not desc:
        add("BİLGİ", "meta description yok (Google snippet'i sayfadan üretir; sayfaya özgü özet yazmak tıklamayı destekleyebilir)", "desc_missing")
    else:
        n = len(desc)
        if n < DESC_GUIDE[0]:
            add("BİLGİ", f"Description kısa ({n} krk). Yönerge ~{DESC_GUIDE[0]}-{DESC_GUIDE[1]}; sabit sınır değildir", "desc_short")
        elif n > DESC_GUIDE[1]:
            add("BİLGİ", f"Description uzun ({n} krk). ~{DESC_GUIDE[1]} üstü kesilebilir; Google yeniden yazabilir", "desc_long")
    # --- Başlıklar (tek H1 bir sıralama şartı değildir; erişilebilir, mantıklı hiyerarşi hedeflenir)
    if len(h1s) == 0:
        add("UYARI", "Belirgin bir ana başlık (H1) yok; kullanıcı ve erişilebilirlik için önerilir (sıralama şartı değildir)", "h1_missing")
    elif len(h1s) > 1:
        add("BİLGİ", f"Birden fazla H1 ({len(h1s)}): HTML5'te geçerlidir ve sıralama sorunu değildir; belirgin bir ana başlık olduğundan emin olun", "h1_multiple")
    if not p.h[2] and words > 300:
        add("BİLGİ", "H2 yok; uzun içerik alt başlıklarla bölünebilir", "h2_missing")
    # --- Teknik meta
    if not p.html_lang:
        add("UYARI", "<html lang> yok", "lang_missing")
    if "viewport" not in p.meta:
        add("UYARI", "viewport meta yok (mobil uyum/okunabilirlik)", "viewport_missing")
    if not canon:
        add("UYARI", "canonical yok (indekslenebilir sayfalarda kendi mutlak URL'sini göstermesi önerilir)", "canonical_missing")
    else:
        if len(canons) > 1:
            add("UYARI", f"Birden fazla canonical ({len(canons)}); Google yok sayabilir", "canonical_multiple")
        if LOCAL_HOST_RX.match(canon):
            add("KRİTİK", f"canonical localhost/yerel adrese işaret ediyor ({canon}) — canlıya sızmış geliştirme ayarı olabilir", "canonical_local")
        elif STAGING_HOST_RX.match(canon):
            add("UYARI", f"canonical staging/test benzeri bir alan adına işaret ediyor ({canon}) — bilinçli mi? (Hipotez)", "canonical_staging")
        elif HOSTING_SUBDOMAIN_RX.match(canon):
            add("BİLGİ", f"canonical barındırma alt alan adına işaret ediyor ({canon}); canlı alan adı bu mu?", "canonical_hosting_domain")
        elif not re.match(r"^https?://", canon):
            add("UYARI", f"canonical mutlak URL olmalı (şu an: '{canon}')", "canonical_relative")
    if noindex:
        add("UYARI", "Sayfa noindex (meta robots veya X-Robots-Tag). Bilinçli değilse yayın engelleyicidir", "noindex")
    if "keywords" in p.meta:
        add("BİLGİ", "meta keywords gereksiz (Google kullanmaz)", "meta_keywords")
    if "og:title" not in p.meta:
        add("BİLGİ", "Open Graph (og:title) yok", "og_title_missing")
    if "og:image" not in p.meta:
        add("BİLGİ", "og:image yok (paylaşım görseli)", "og_image_missing")
    # --- hreflang (statik doğrulama; karşılıklılık için diğer sayfalar ayrıca denetlenmelidir)
    hl = [(lang, href) for r, href, lang in p.links if "alternate" in r.split() and lang]
    if hl:
        bad = [l for l, _ in hl if not HREFLANG_RX.match(l)]
        rel = [h for _, h in hl if not re.match(r"^https?://", h)]
        if bad:
            add("UYARI", f"Geçersiz hreflang kodu: {', '.join(sorted(set(bad)))}", "hreflang_invalid")
        if rel:
            add("UYARI", "hreflang href değerleri mutlak URL olmalı", "hreflang_relative")
        if canon and canon not in [h for _, h in hl]:
            add("BİLGİ", "hreflang kümesi sayfanın kendisini (canonical) içermiyor; kendine referans önerilir", "hreflang_no_self")
    # --- Görseller
    noalt = [i for i in p.imgs if i.get("alt") is None]
    nodim = [i for i in p.imgs if not (i.get("width") and i.get("height"))]
    if noalt:
        add("UYARI", f"{len(noalt)}/{len(p.imgs)} görselde alt özniteliği yok (dekoratifse alt=\"\")", "img_alt_missing")
    if len(p.imgs) > 2 and len(nodim) > len(p.imgs) // 2:
        add("BİLGİ", f"{len(nodim)} görselde width/height yok (CLS riski)", "img_dims_missing")
    # --- Linkler
    empty_a = [a for a in p.anchors if a[0] and not a[1].strip() and not a[2].get("aria-label")]
    bad_anchor = [a for a in p.anchors if a[1].strip().lower() in
                  ("tıklayın", "buraya tıklayın", "click here", "daha fazla", "devamı", "read more", "buraya")]
    if empty_a:
        add("BİLGİ", f"{len(empty_a)} linkte metin/aria-label yok", "link_empty")
    if bad_anchor:
        add("BİLGİ", f"{len(bad_anchor)} linkte genel bağlantı metni (\"devamı\", \"buraya tıklayın\"...)", "link_generic")
    if any(a[0].strip() in ("", "#", "javascript:void(0)") for a in p.anchors if a[2].get("onclick")):
        add("UYARI", "onclick ile çalışan sahte link var; gerçek <a href> kullanın", "link_fake")
    # --- Schema (her sayfada gerekmez; yalnız görünür/gerçek içeriği yansıtan, uygun türler)
    if jerr:
        add("UYARI", f"{jerr} JSON-LD bloğu geçersiz JSON", "jsonld_invalid")
    if not types:
        add("BİLGİ", "JSON-LD yok (her sayfada gerekmez; sayfa türüne uygunsa ve görünür içeriği yansıtıyorsa eklenir)", "jsonld_none")
    if {"AggregateRating", "Review"} & set(types):
        add("BİLGİ", "AggregateRating/Review işaretlemesi var: yorumların gerçek ve sayfada görünür olduğunu doğrulayın (sahte/gizli yorum spamdır)", "jsonld_review")
    if "FAQPage" in types:
        add("BİLGİ", "FAQPage: Google FAQ zengin sonucunu 7 Mayıs 2026'dan beri göstermiyor; SSS metni sayfada görünüyorsa işaretleme zararsızdır ama zengin sonuç beklenmez", "jsonld_faq")
    if "HowTo" in types:
        add("BİLGİ", "HowTo: Google'da zengin sonuç desteği büyük ölçüde kaldırıldı; zengin sonuç beklemeyin", "jsonld_howto")
    # --- İçerik
    if words < 150:
        add("BİLGİ", f"İlk HTML'de az metin ({words} kelime): ince içerik olabilir ya da içerik JS ile sonradan yükleniyor olabilir "
                     "— render edilmiş DOM'u ayrıca inceleyin (references/javascript-rendering-debugging.md)", "thin_initial_html")

    stats = {
        "title": title, "title_len": len(title),
        "desc_len": len(desc), "h1": h1s[:2], "h2": len(p.h[2]), "h3": len(p.h[3]),
        "words": words, "imgs": len(p.imgs), "schema": sorted(set(types)),
        "canonical": canon, "lang": p.html_lang, "noindex": noindex,
    }
    return {"page": label, "issues": issues, "stats": stats, "_links": [a[0] for a in p.anchors]}


# ------------------------------------------------------------------ robots.txt
def parse_robots(text):
    groups, agents, rules, seen_rule = [], [], [], False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, val = (s.strip() for s in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if seen_rule:
                groups.append((agents, rules))
                agents, rules, seen_rule = [], [], False
            agents.append(val.lower())
        elif key in ("allow", "disallow"):
            seen_rule = True
            rules.append((key, val))
    if agents:
        groups.append((agents, rules))
    return groups


def robots_findings(text):
    out, blocked_ai = [], []
    groups = parse_robots(text)

    def blocks_root(rules):
        return any(k == "disallow" and v == "/" for k, v in rules)

    googlebot_open = any("googlebot" in agents and not blocks_root(rules) for agents, rules in groups)
    for agents, rules in groups:
        if blocks_root(rules):
            main = [a for a in agents if a in ("*", "googlebot", "bingbot")]
            has_allow = any(k == "allow" and v for k, v in rules)
            if main and main == ["*"] and googlebot_open:
                out.append(("UYARI", "robots.txt: '*' grubu tüm siteyi engelliyor, yalnız Googlebot'a izin verilmiş; diğer arama motorları (ör. Bingbot) engelli — bilinçli mi?", "robots_only_google"))
            elif main and has_allow:
                out.append(("UYARI", f"robots.txt ({', '.join(main)}) için 'Disallow: /' var; 'Allow' istisnalarına rağmen site büyük ölçüde engelli — canlıda istenen bu mu?", "robots_mostly_blocked"))
            elif main:
                out.append(("KRİTİK", f"robots.txt tüm siteyi engelliyor ({', '.join(main)}: Disallow: /) — canlıda olmamalı", "robots_blocks_all"))
            blocked_ai += [a for a in agents if any(b in a for b in AI_BOTS)]
    if blocked_ai:
        out.append(("BİLGİ", f"robots.txt bazı yapay zekâ/veri tarayıcılarını tamamen engelliyor: {', '.join(sorted(set(blocked_ai)))}. "
                             "Bilinçli bir karar mı? (AI aramalarında görünürlüğü etkileyebilir; karar sitenin sahibine aittir)", "robots_blocks_ai_bots"))
    if "sitemap:" not in text.lower():
        out.append(("UYARI", "robots.txt içinde Sitemap: satırı yok", "robots_no_sitemap"))
    return out


def leak_findings(urls, where):
    """Sitemap/canonical vb. URL listelerinde localhost veya staging izi arar."""
    out = []
    local = [u for u in urls if LOCAL_HOST_RX.match(u)]
    staging = [u for u in urls if STAGING_HOST_RX.match(u)]
    if local:
        out.append(("KRİTİK", f"{where} içinde localhost/yerel adres var ({len(local)} adet, örn. {local[0]})", "leak_local"))
    if staging:
        out.append(("UYARI", f"{where} içinde staging/test benzeri alan adı var ({len(staging)} adet, örn. {staging[0]}) — bilinçli mi? (Hipotez)", "leak_staging"))
    return out


# ------------------------------------------------------------------ site geneli
def site_checks_dir(root):
    res = []

    def has(*names):
        return any(os.path.exists(os.path.join(root, n)) for n in names)

    rp = next((os.path.join(root, n) for n in ("robots.txt", "public/robots.txt") if os.path.exists(os.path.join(root, n))), None)
    if not rp:
        res.append(("UYARI", "robots.txt bulunamadı (framework derleme/çalışma sırasında üretiyor olabilir)", "robots_missing"))
    else:
        with open(rp, encoding="utf-8", errors="replace") as f:
            res += robots_findings(f.read())
    if not has("sitemap.xml", "sitemap-index.xml", "public/sitemap.xml", "sitemap_index.xml"):
        res.append(("UYARI", "sitemap.xml bulunamadı (framework derleme sırasında üretiyor olabilir)", "sitemap_missing"))
    if not has("favicon.ico", "public/favicon.ico", "favicon.svg", "public/favicon.svg"):
        res.append(("BİLGİ", "favicon bulunamadı", "favicon_missing"))
    if not has("404.html", "public/404.html"):
        res.append(("BİLGİ", "404.html bulunamadı", "404_missing"))
    return res


def fetch_text(url, allow_private, timeout=20):
    r = netguard.fetch(url, timeout=timeout, allow_private=allow_private)
    return r


def collect_sitemap_locs(url, allow_private, depth=0, limit=500):
    """Sitemap (veya sitemap index) içindeki sayfa URL'lerini toplar. Sınırlıdır: derinlik ≤ 2, index başına ≤ 3 alt sitemap."""
    r = fetch_text(url, allow_private)
    if r.status != 200:
        raise netguard.FetchError(f"HTTP {r.status}")
    text = r.text
    locs = re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", text)
    if "<sitemapindex" in text and depth < 2:
        pages = []
        for child in locs[:3]:
            try:
                pages += collect_sitemap_locs(child, allow_private, depth + 1, limit)
            except (netguard.FetchError, netguard.BlockedError):
                continue
            if len(pages) >= limit:
                break
        return pages[:limit]
    return locs[:limit]


def site_checks_url(base, allow_private):
    res = []
    p = urlparse(base)
    root = f"{p.scheme}://{p.netloc}"
    sm_urls, locs = [], []
    if p.scheme == "http" and not LOCAL_HOST_RX.match(base):
        res.append(("UYARI", "Site HTTPS ile verilmedi; HTTPS ve tek tercih edilen sürüm (301) önerilir", "not_https"))
    try:
        r = fetch_text(root + "/robots.txt", allow_private)
        if r.status == 200:
            res += robots_findings(r.text)
            sm_urls = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", r.text)
        else:
            res.append(("UYARI", f"robots.txt alınamadı (HTTP {r.status})", "robots_http"))
    except (netguard.FetchError, netguard.BlockedError) as e:
        res.append(("UYARI", f"robots.txt alınamadı: {e}", "robots_error"))
    for sm in (sm_urls or [root + "/sitemap.xml"]):
        try:
            locs += collect_sitemap_locs(sm, allow_private)
        except (netguard.FetchError, netguard.BlockedError) as e:
            res.append(("UYARI", f"sitemap alınamadı ({sm}): {e}", "sitemap_error"))
    res += leak_findings(locs, "sitemap")
    return res, locs


def count(items, level):
    return sum(1 for it in items if it[0] == level)


def main():
    netguard.setup_stdio()
    ap = argparse.ArgumentParser(description="Otomatik SEO triyajı (statik HTML). Ayrıntı için dosyanın başındaki açıklamaya bak.")
    ap.add_argument("target", nargs="?", help="klasör yolu")
    ap.add_argument("--url")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max", type=int, default=25, help="URL modunda taranacak en çok sayfa")
    ap.add_argument("--delay", type=float, default=0.3, help="URL modunda istekler arası bekleme (sn)")
    ap.add_argument("--allow-private", action="store_true",
                    help="localhost/özel ağ adreslerine bilerek izin ver (yerel geliştirme sunucusu). Varsayılan: kapalı (SSRF koruması)")
    a = ap.parse_args()
    if not a.target and not a.url:
        ap.error("klasör veya --url verin")

    pages, site_issues = [], []
    titles, h1map = {}, {}
    if a.url:
        try:
            netguard.check_destination(a.url, a.allow_private)
        except netguard.BlockedError as e:
            sys.exit(f"ERİŞİM ENGELLENDİ: {e}. Yerel geliştirme sunucusunu bilerek denetliyorsanız --allow-private ekleyin.")
        sres, locs = site_checks_url(a.url, a.allow_private)
        site_issues += sres
        base_host = urlparse(a.url).netloc
        same_host = [u for u in locs if urlparse(u).netloc == base_host and u.rstrip("/") != a.url.rstrip("/")]
        urls = [a.url] + same_host[: max(a.max - 1, 0)]
        for i, u in enumerate(urls):
            if i:
                time.sleep(max(a.delay, 0))
            try:
                res = fetch_text(u, a.allow_private)
            except (netguard.FetchError, netguard.BlockedError) as e:
                lvl = "KRİTİK" if i == 0 else "UYARI"
                pages.append({"page": u, "issues": [(lvl, f"Alınamadı: {e}", "fetch_error")], "stats": {}})
                continue
            r = audit_html(res.text, u, x_robots=res.header("X-Robots-Tag"))
            if res.status >= 400:
                r["issues"].append(("KRİTİK" if i == 0 else "UYARI", f"HTTP {res.status}" + ("" if i == 0 else " (sitemap'teki URL hata dönüyor)"), "http_error"))
            if res.hops and i > 0:
                r["issues"].append(("UYARI", f"Sitemap URL'si yönlendiriyor ({res.hops} sıçrama → {res.url}); sitemap'e son URL konmalı", "sitemap_redirect"))
            elif res.hops > 1:
                r["issues"].append(("UYARI", f"Yönlendirme zinciri: {res.hops} sıçrama ({' → '.join(c[0] for c in res.chain)} → {res.url})", "redirect_chain"))
            if res.truncated:
                r["issues"].append(("BİLGİ", "Yanıt boyut sınırında kesildi; analiz kısmi olabilir", "truncated"))
            pages.append(r)
    else:
        root = a.target
        if not os.path.isdir(root):
            sys.exit(f"Klasör bulunamadı: {root}")
        site_issues += site_checks_dir(root)
        skip = {"node_modules", ".git", ".next", ".cache", ".venv", "vendor"}
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d not in skip]
            for f in fn:
                if f.lower().endswith((".html", ".htm")):
                    fp = os.path.join(dp, f)
                    with open(fp, encoding="utf-8", errors="replace") as fh:
                        html = fh.read()
                    if "<html" not in html.lower() and "<title" not in html.lower():
                        continue  # parça şablon
                    pages.append(audit_html(html, os.path.relpath(fp, root)))

    for r in pages:
        s = r.get("stats", {})
        if s.get("title"):
            titles.setdefault(s["title"], []).append(r["page"])
        if s.get("h1"):
            h1map.setdefault(s["h1"][0], []).append(r["page"])
    for t, ps in titles.items():
        if len(ps) > 1:
            site_issues.append(("UYARI", f"Aynı title {len(ps)} sayfada: '{t[:60]}' → {', '.join(ps[:4])}", "dup_title"))
    for t, ps in h1map.items():
        if len(ps) > 1:
            site_issues.append(("BİLGİ", f"Aynı H1 {len(ps)} sayfada: '{t[:60]}'", "dup_h1"))
    audited = [r for r in pages if r.get("stats")]
    if audited:
        n_noindex = sum(1 for r in audited if r["stats"].get("noindex"))
        if n_noindex == len(audited):
            site_issues.append(("KRİTİK", f"Denetlenen TÜM sayfalar noindex ({n_noindex}/{len(audited)}) — canlıda kalırsa site arama sonuçlarından düşer", "all_noindex"))
        elif n_noindex / len(audited) > 0.3:
            site_issues.append(("UYARI", f"Sayfaların büyük kısmı noindex ({n_noindex}/{len(audited)}) — bilinçli mi?", "many_noindex"))

    all_items = site_issues + [i for r in pages for i in r["issues"]]
    n_crit, n_warn = count(all_items, "KRİTİK"), count(all_items, "UYARI")

    if a.json:
        for r in pages:
            r.pop("_links", None)
        print(json.dumps({"site": site_issues, "pages": pages, "critical": n_crit, "warnings": n_warn, "notice": NOTICE},
                         ensure_ascii=False, indent=2))
    else:
        print(f"== SEO DENETİMİ (otomatik triyaj): {len(pages)} sayfa ==\n")
        if site_issues:
            print("-- Site geneli --")
            for l, m, _ in sorted(site_issues, key=lambda x: LEVEL_ORDER.index(x[0])):
                print(f"[{l}] {m}")
            print()
        for r in pages:
            s = r.get("stats", {})
            head = f"{r['page']}"
            if s:
                head += f"  (title {s['title_len']}, desc {s['desc_len']}, {s['words']} kelime, H2={s['h2']}, schema={','.join(s['schema']) or '-'})"
            print(head)
            if not r["issues"]:
                print("   ✓ sorun yok")
            for l, m, _ in sorted(r["issues"], key=lambda x: LEVEL_ORDER.index(x[0])):
                print(f"   [{l}] {m}")
        print(f"\nÖZET: {n_crit} kritik, {n_warn} uyarı, {len(pages)} sayfa")
        print(f"NOT: {NOTICE}")
    sys.exit(1 if n_crit else 0)


if __name__ == "__main__":
    main()
