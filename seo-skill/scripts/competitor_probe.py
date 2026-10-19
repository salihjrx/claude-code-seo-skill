#!/usr/bin/env python3
"""
Rakip / 1. sıradaki sayfa ölçümü (yalnızca Python 3 standart kütüphanesi).

Kullanım:
  python competitor_probe.py URL1 URL2 ...            # tablo çıktı
  python competitor_probe.py --file urller.txt --json # her satırda 1 URL; JSON çıktı
  python competitor_probe.py --self <html_dosyası_veya_url> URL1 URL2   # kendi sayfanı rakiplerle karşılaştır (boşluk analizi)
  python competitor_probe.py --self http://localhost:3000/sayfa --allow-private URL1 URL2   # yerel geliştirme sunucusu

Her sayfa için ölçer: title/description uzunluğu, H1, H2/H3 listesi, kelime sayısı, schema türleri,
görsel/alt oranı, liste/tablo, SSS ve içindekiler ipucu, canonical, dil, güncelleme tarihi, iç/dış link.
Boşluk analizi: rakiplerin ≥2'sinde geçen H2 konuları senin sayfanda yoksa "EKSİK KONU" olarak işaretler.

KANIT DÜZEYİ: çıktı "Gözlendi"dir (tek tek sayfa ölçümü). Ortak özellikler bir NEDENSELLİK kanıtı değildir;
Google'ın sıralama formülü bilinmez. Sonuçları yapı/kapsam öğrenmek ve hipotez üretmek için kullan, kural olarak değil.

GÜVENLİK: varsayılan olarak yalnızca genel (public) hedeflere bağlanır (localhost/özel ağ reddedilir, yönlendirmeler her adımda
doğrulanır). Bot doğrulaması (Cloudflare vb.) çıkan sayfaları AŞMAYA ÇALIŞMAZ; "ölçülemedi" yazar. Bu durumda sayfayı tarayıcı
aracıyla (Claude in Chrome / yerleşik tarayıcı) aç ve aynı metrikleri oradan çıkar. İstekler arası varsayılan bekleme 1 sn.
Rakip metnini kopyalama/spin yapma; yalnızca yapı ve kapsamı öğren.
"""
import sys, os, re, json, argparse, importlib.util, time
from collections import Counter
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import netguard  # noqa: E402

spec = importlib.util.spec_from_file_location("seo_audit", os.path.join(HERE, "seo_audit.py"))
sa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sa)

CHALLENGE = re.compile(r"just a moment|bir dakika lütfen|checking your browser|cf-chl|attention required|captcha|access denied|are you a robot", re.I)
STOP = set("ve ile için bir bu şu da de mi mı mu mü nasıl nedir ne ise veya ya en çok daha gibi olarak the a an of to in on for and or is are how what why vs".split())


def fetch(url, timeout=25, allow_private=False):
    res = netguard.fetch(url, timeout=timeout, allow_private=allow_private, headers={"Accept-Language": "tr,en;q=0.8"})
    return res.status, res.text


def norm_h(s):
    s = re.sub(r"\s+", " ", s).strip().lower()
    s = re.sub(r"^\d+[\).\s-]+", "", s)  # baştaki numara
    return s


def tokens(s):
    return {w for w in re.findall(r"[a-zçğıöşü0-9]{3,}", s.lower()) if w not in STOP}


def measure(src, allow_private=False):
    if os.path.exists(src):
        with open(src, encoding="utf-8", errors="replace") as f:
            html = f.read()
        status = 200
    else:
        status, html = fetch(src, allow_private=allow_private)
        if status >= 400:
            return {"url": src, "ok": False, "neden": f"HTTP {status}: sayfa ölçülemedi"}
    if CHALLENGE.search(html[:6000]) and len(html) < 20000:
        return {"url": src, "ok": False, "neden": "Bot doğrulaması / engel sayfası: ölçülemedi (aşılmaya çalışılmadı). Tarayıcı aracıyla elle ölç."}
    p = sa.Page()
    p.feed(html)
    txt = " ".join(p.text_chunks)
    words = len(re.findall(r"\w+", txt))
    types, jerr = sa.jsonld_types(p.jsonld)
    h2s = [re.sub(r"\s+", " ", x).strip() for x in p.h[2] if x.strip()]
    h3s = [re.sub(r"\s+", " ", x).strip() for x in p.h[3] if x.strip()]
    low = txt.lower()
    m = re.search(r'(article:modified_time|dateModified|datePublished)["\'\s:=]+["\']?(\d{4}-\d{2}-\d{2})', html)
    anchors = p.anchors
    host = urlparse(src).hostname if "://" in src else ""
    internal = [a for a in anchors if a[0].startswith("/") or (host and host in a[0])]
    canon = next((h for r, h, _ in p.links if "canonical" in r), "")
    desc = " ".join(p.meta.get("description", "").split())
    title = " ".join(p.title.split())
    return {
        "url": src, "ok": True, "http": status,
        "title": title, "title_len": len(title), "desc_len": len(desc),
        "h1": [" ".join(x.split()) for x in p.h[1] if x.strip()][:2],
        "h2": h2s, "h3_count": len(h3s), "words": words,
        "schema": sorted(set(types)), "schema_json_hata": jerr,
        "imgs": len(p.imgs), "imgs_alt_eksik": len([i for i in p.imgs if i.get("alt") is None]),
        "lists": html.lower().count("<ul") + html.lower().count("<ol"), "tables": html.lower().count("<table"),
        "sss": bool(re.search(r"sık sorulan|sss\b|faq|frequently asked", low)) or "FAQPage" in types,
        "icindekiler": bool(re.search(r"i̇?çindekiler|table of contents|içerik tablosu", low[:6000])),
        "canonical": bool(canon), "lang": p.html_lang, "tarih": m.group(2) if m else "",
        "ic_link": len(internal), "dis_link": len(anchors) - len(internal),
        "robots": p.meta.get("robots", ""), "og": "og:title" in p.meta,
        "yil_title_desc": bool(re.search(r"20(2[4-9]|3\d)", title + desc)),
    }


def median(v):
    v = sorted(v)
    n = len(v)
    return 0 if n == 0 else (v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2)


def gap_analysis(self_m, comps):
    ok = [c for c in comps if c.get("ok")]
    if not ok:
        return []
    out = []
    # Ortak H2 konuları
    cnt = Counter()
    for c in ok:
        seen = set()
        for h in c["h2"]:
            key = frozenset(tokens(h))
            if key:
                seen.add(key)
        for key in seen:
            cnt[key] += 1
    # Benzer başlıkları grupla (Jaccard)
    reps = []
    for c in ok:
        for h in c["h2"]:
            t = tokens(h)
            if not t:
                continue
            for r in reps:
                if len(t & r["t"]) / len(t | r["t"]) >= 0.5:
                    r["sites"].add(c["url"]); break
            else:
                reps.append({"t": t, "h": h, "sites": {c["url"]}})
    common = [r for r in reps if len(r["sites"]) >= max(2, len(ok) // 2)]
    self_tokens = [tokens(h) for h in (self_m or {}).get("h2", [])] if self_m else []
    for r in sorted(common, key=lambda r: -len(r["sites"])):
        covered = any(len(r["t"] & s) / len(r["t"] | s) >= 0.4 for s in self_tokens) if self_m else None
        out.append({"konu": r["h"], "kac_rakipte": len(r["sites"]), "senin_sayfanda": covered})
    return out


def main():
    netguard.setup_stdio()
    ap = argparse.ArgumentParser(description="Rakip/1. sıra sayfa ölçümü ve konu boşluğu analizi (gözlem; nedensellik değil).")
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--file")
    ap.add_argument("--self", dest="self_src")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--delay", type=float, default=1.0, help="istekler arası bekleme (sn); varsayılan 1")
    ap.add_argument("--allow-private", action="store_true",
                    help="localhost/özel ağ adreslerine bilerek izin ver (yalnızca KENDİ yerel sunucun için). Varsayılan: kapalı")
    a = ap.parse_args()
    urls = list(a.urls)
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            urls += [l.strip() for l in f if l.strip() and not l.startswith("#")]
    if not urls:
        ap.error("en az bir URL verin")
    res = []
    for i, u in enumerate(urls):
        if i and not os.path.exists(u):
            time.sleep(max(a.delay, 0))
        try:
            res.append(measure(u, a.allow_private))
        except (netguard.BlockedError, netguard.FetchError) as e:
            res.append({"url": u, "ok": False, "neden": f"Alınamadı: {e}"})
        except Exception as e:  # beklenmeyen biçim hataları ölçümü durdurmasın
            res.append({"url": u, "ok": False, "neden": f"Alınamadı: {type(e).__name__}: {e}"})
    self_m = None
    if a.self_src:
        try:
            self_m = measure(a.self_src, a.allow_private)
        except Exception as e:
            self_m = {"url": a.self_src, "ok": False, "neden": str(e)}
    ok = [r for r in res if r.get("ok")]
    summary = {}
    if ok:
        summary = {
            "olculen": len(ok), "olculemeyen": len(res) - len(ok),
            "ortanca_kelime": median([r["words"] for r in ok]),
            "ortanca_h2": median([len(r["h2"]) for r in ok]),
            "ortanca_h3": median([r["h3_count"] for r in ok]),
            "ortanca_title_len": median([r["title_len"] for r in ok]),
            "ortanca_desc_len": median([r["desc_len"] for r in ok if r["desc_len"]] or [0]),
            "schema_turleri": dict(Counter(t for r in ok for t in r["schema"]).most_common()),
            "sss_orani": f"{sum(r['sss'] for r in ok)}/{len(ok)}",
            "icindekiler_orani": f"{sum(r['icindekiler'] for r in ok)}/{len(ok)}",
            "yil_ibaresi_orani": f"{sum(r['yil_title_desc'] for r in ok)}/{len(ok)}",
        }
    gaps = gap_analysis(self_m if self_m and self_m.get("ok") else None, res)
    if a.json:
        print(json.dumps({"kanit_duzeyi": "Gözlendi (nedensellik değil)", "sayfalar": res, "ozet": summary, "kendi": self_m,
                          "konu_bosluklari": gaps}, ensure_ascii=False, indent=2))
        return
    print(f"== RAKİP ÖLÇÜMÜ: {len(res)} sayfa ==")
    print("Kanıt düzeyi: Gözlendi (tek tek sayfa ölçümü; ortak özellikler nedensellik kanıtı değildir)\n")
    for r in res:
        if not r.get("ok"):
            print(f"✗ {r['url']}\n    {r['neden']}\n"); continue
        print(f"✓ {r['url']}")
        print(f"    title {r['title_len']} | desc {r['desc_len']} | {r['words']} kelime | H2={len(r['h2'])} H3={r['h3_count']} | görsel {r['imgs']} (alt eksik {r['imgs_alt_eksik']}) | liste {r['lists']} tablo {r['tables']}")
        print(f"    schema: {', '.join(r['schema']) or '-'} | SSS:{'E' if r['sss'] else 'H'} TOC:{'E' if r['icindekiler'] else 'H'} canonical:{'E' if r['canonical'] else 'H'} tarih:{r['tarih'] or '-'} yıl-ibaresi:{'E' if r['yil_title_desc'] else 'H'}")
        print(f"    H1: {r['h1']}")
        print("    H2: " + " | ".join(r["h2"][:14]))
        print()
    if summary:
        print("-- ÖZET (ölçülen rakiplerin ortancası; gözlem) --")
        for k, v in summary.items():
            print(f"  {k}: {v}")
    if gaps:
        print("\n-- ORTAK KONULAR (rakiplerin çoğunda geçen H2'ler) --")
        for g in gaps[:20]:
            durum = "" if g["senin_sayfanda"] is None else ("  ✓ var" if g["senin_sayfanda"] else "  ✗ EKSİK KONU")
            print(f"  [{g['kac_rakipte']} rakip] {g['konu']}{durum}")


if __name__ == "__main__":
    main()
