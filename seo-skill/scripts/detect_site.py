#!/usr/bin/env python3
"""
Site türü ve teknoloji algılama (yalnızca Python 3 standart kütüphanesi).

Kullanım:
  python detect_site.py <proje_klasörü>          # insan okunur özet
  python detect_site.py <proje_klasörü> --json   # JSON

Ne yapar:
  - Framework / CMS / render stratejisini tahmin eder
  - Sitenin TÜRÜNÜ puanlayarak tahmin eder (e-ticaret, yerel işletme, SaaS, blog/içerik,
    portföy, kurumsal, ilan/pazaryeri/rehber, eğitim/kurs, haber) + kanıt gösterir
  - Dil, çok dillilik, marka adı ve olası alan adını çıkarır
  - Hangi playbook dosyasının okunması gerektiğini söyler
Güven düşükse (ilk iki tür birbirine yakınsa) bunu belirtir; Claude kullanıcıya TEK soru sormalı.

Kanıt düzeyi: tür tahmini bir HİPOTEZDİR (kod/metin sinyallerine dayalı sezgisel puanlama). Kesin hüküm değildir;
güven "yüksek" değilse kullanıcıya doğrulat.
"""
import os, re, sys, json, math, argparse
from collections import Counter


def _utf8_stdio():
    """Windows'ta stdout cp1254/cp1252 olabilir (pipe); Türkçe/sembol yazdırırken çökmesin."""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

SKIP_DIRS = {"node_modules", ".git", ".next", ".nuxt", ".svelte-kit", ".astro", "dist", "build", "out",
             ".cache", "vendor", ".venv", "venv", "__pycache__", ".claude", "coverage", ".turbo", ".vercel"}
TEXT_EXT = {".html", ".htm", ".md", ".mdx", ".txt", ".tsx", ".jsx", ".ts", ".js", ".vue", ".svelte", ".astro",
            ".liquid", ".php", ".twig", ".njk", ".ejs", ".hbs", ".json", ".yml", ".yaml", ".toml", ".py", ".rb",
            ".cshtml", ".erb", ".blade.php"}
MAX_FILE = 200_000
MAX_TOTAL = 4_000_000
MAX_FILES = 3000

# --- Tür imzaları: (regex, ağırlık). Türkçe + İngilizce.
TYPES = {
    "eticaret": {
        "ad": "E-ticaret / online mağaza",
        "playbook": "site-tipleri/eticaret.md",
        "sig": [
            (r"sepete ekle|add to cart|add-to-cart|addtocart", 4),
            (r"\b(sepet|cart|basket)\b", 2), (r"\b(checkout|ödeme|odeme|siparis|sipariş|order)\b", 2),
            (r"\b(sku|gtin|barkod|stok|in stock|out of stock|stokta)\b", 3),
            (r"\b(kargo|shipping|iade|returns?)\b", 1.5),
            (r"\"@type\"\s*:\s*\"(product|offer)\"", 4), (r"\b(price|fiyat|₺|\btl\b|\$|€)\b", 0.5),
            (r"woocommerce|shopify|ticimax|ideasoft|tsoft|ikas|magento|prestashop|opencart|bigcommerce|medusa|snipcart|saleor|commerce\.js", 6),
            (r"stripe|iyzico|paytr|paypal|param\b|craftgate", 2),
            (r"\b(kategori|category|collections?|ürünler|urunler|products?)\b", 1),
        ],
    },
    "yerel": {
        "ad": "Yerel işletme / hizmet (konuma bağlı)",
        "playbook": "site-tipleri/yerel-isletme.md",
        "sig": [
            (r"\"@type\"\s*:\s*\"(localbusiness|restaurant|dentist|medicalbusiness|store|hairsalon|legalservice|autorepair)\"", 6),
            (r"çalışma saatleri|calisma saatleri|opening hours|openinghours|working hours", 4),
            (r"google\.com/maps|maps\.google|goo\.gl/maps|maps\.app\.goo\.gl|leaflet|mapbox", 3),
            (r"tel:\+?\d|\b0?\s?\(?5\d{2}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}\b|whatsapp|wa\.me", 2),
            (r"randevu|appointment|rezervasyon|reservation|book (now|online)", 3),
            (r"\b(şube|subemiz|şubelerimiz|branch|konum|location|yol tarifi|directions|adres|address)\b", 1.5),
            (r"klinik|muayenehane|diş|dental|kuaför|güzellik|restoran|cafe|kafe|otel|hotel|avukat|hukuk|emlak|nakliyat|tesisat|çilingir|oto servis|veteriner|spa\b", 2),
            (r"\b(mahalle|ilçe|ilce|semt|bölge|bölgesi|hizmet bölgesi|service area)\b", 1.5),
        ],
    },
    "saas": {
        "ad": "SaaS / yazılım ürünü / uygulama",
        "playbook": "site-tipleri/saas.md",
        "sig": [
            (r"\"@type\"\s*:\s*\"(softwareapplication|webapplication|mobileapplication)\"", 5),
            (r"\b(pricing|fiyatlandırma|fiyatlandirma|planlar|plans)\b", 2),
            (r"free trial|ücretsiz dene|ucretsiz dene|get started|hemen başla|demo (talep|request|iste)|request a demo", 3),
            (r"\b(sign ?up|sign ?in|log ?in|giriş yap|kayıt ol|dashboard|panel)\b", 1.5),
            (r"\b(api|sdk|webhook|integrations?|entegrasyonlar?|changelog|release notes|roadmap|status page)\b", 2),
            (r"\b(docs|documentation|dokümantasyon|developer)\b", 1.5),
            (r"next-auth|clerk|auth0|supabase|firebase|stripe|lemonsqueezy|paddle|prisma|drizzle", 1.5),
            (r"\b(use cases?|kullanım senaryoları|customers|müşterilerimiz|case stud)\b", 1),
        ],
    },
    "blog": {
        "ad": "Blog / içerik / yayıncı sitesi",
        "playbook": "site-tipleri/blog-icerik.md",
        "sig": [
            (r"\"@type\"\s*:\s*\"(blogposting|article|newsarticle)\"", 4),
            (r"\b(blog|makaleler|yazılar|yazilar|posts?|articles?|yazar|author|etiket|tag|kategori arşivi|archive|rss|feed)\b", 1.5),
            (r"datepublished|published_time|pubdate|yayın tarihi|yayinlanma|okuma süresi|min read|reading time", 3),
            (r"yorumlar|comments|disqus|bülten|newsletter|abone ol|subscribe", 1.5),
            (r"gatsby-source|contentlayer|@next/mdx|astro:content|hugo|jekyll|eleventy|docusaurus|ghost|wordpress", 2),
        ],
    },
    "portfolyo": {
        "ad": "Portföy / kişisel site / freelancer",
        "playbook": "site-tipleri/portfolyo-kurumsal.md",
        "sig": [
            (r"portfolyo|portfolio|projelerim|my work|selected work|case stud|hakkımda|about me|özgeçmiş|ozgecmis|resume|\bcv\b", 4),
            (r"\b(freelance|serbest|developer|designer|tasarımcı|yazılımcı|photographer|fotoğrafçı)\b", 1.5),
            (r"github\.com|linkedin\.com/in|behance|dribbble|codepen", 1.5),
            (r"\"@type\"\s*:\s*\"person\"", 3),
            (r"hire me|bana ulaş|let'?s (work|talk)|birlikte çalışalım", 2),
        ],
    },
    "kurumsal": {
        "ad": "Kurumsal / B2B / tanıtım sitesi",
        "playbook": "site-tipleri/portfolyo-kurumsal.md",
        "sig": [
            (r"kurumsal|hakkımızda|hakkimizda|about us|vizyon|misyon|mission|vision|değerlerimiz|referanslar|references|clients|iş ortakları|partners", 3),
            (r"hizmetlerimiz|services|çözümlerimiz|solutions|sektörler|industries|ürünlerimiz|products", 1.5),
            (r"kariyer|careers|insan kaynakları|open positions|açık pozisyon", 2),
            (r"\"@type\"\s*:\s*\"(organization|corporation)\"", 2),
            (r"teklif al|get a quote|request (a )?quote|iletişime geç|contact sales|katalog|catalog", 2),
        ],
    },
    "ilan": {
        "ad": "İlan / pazaryeri / rehber / dizin / karşılaştırma",
        "playbook": "site-tipleri/ilan-pazaryeri-rehber.md",
        "sig": [
            (r"\b(ilan|ilanlar|ilan ver|listings?|classifieds?|directory|rehber|dizin|listele)\b", 4),
            (r"\b(satıcı|saticilar|seller|vendor|mağaza aç|marketplace|pazaryeri|ilan sahibi)\b", 3),
            (r"\b(karşılaştır|karsilastir|compare|en iyi|best)\b", 1),
            (r"\b(filtre|filters?|sırala|sort by|harita görünümü|map view)\b", 1.5),
            (r"\"@type\"\s*:\s*\"(itemlist|realestatelisting|jobposting|vehicle|apartment|house)\"", 4),
        ],
    },
    "egitim": {
        "ad": "Eğitim / kurs / akademi",
        "playbook": "site-tipleri/egitim-kurs.md",
        "sig": [
            (r"\b(kurs|kurslar|course|courses|eğitim|egitim|ders|lesson|müfredat|curriculum|sertifika|certificate|akademi|academy|bootcamp)\b", 3),
            (r"\"@type\"\s*:\s*\"(course|educationalorganization|courseinstance)\"", 5),
            (r"\b(eğitmen|egitmen|instructor|öğrenci|student|webinar|canlı ders|kayıt ol)\b", 2),
            (r"moodle|udemy|teachable|thinkific|learndash|lms\b", 3),
        ],
    },
    "haber": {
        "ad": "Haber / dergi / medya",
        "playbook": "site-tipleri/haber.md",
        "sig": [
            (r"\b(haber|haberler|son dakika|gündem|spor|ekonomi|magazin|editör|muhabir|breaking|newsroom)\b", 3),
            (r"\"@type\"\s*:\s*\"(newsarticle|newsmediaorganization)\"", 6),
            (r"google news|amp-|publisher center|sitemap-news|news:publication", 3),
        ],
    },
}

# Türe göre, playbook'a EK olarak okunması önerilen referanslar (references/ altında)
EXTRA_REFS = {
    "eticaret": ["ecommerce-catalog-and-facets.md", "seo-architecture-and-url-governance.md", "schema-validation-matrix.md"],
    "yerel": ["schema-validation-matrix.md", "content-quality-and-editorial-governance.md"],
    "saas": ["javascript-rendering-debugging.md", "schema-validation-matrix.md"],
    "blog": ["content-quality-and-editorial-governance.md", "content-brief-template.md", "ai-search-and-entity-readiness.md"],
    "portfolyo": ["schema-validation-matrix.md", "content-quality-and-editorial-governance.md"],
    "kurumsal": ["schema-validation-matrix.md", "content-quality-and-editorial-governance.md"],
    "ilan": ["seo-architecture-and-url-governance.md", "content-quality-and-editorial-governance.md", "schema-validation-matrix.md"],
    "egitim": ["schema-validation-matrix.md", "content-quality-and-editorial-governance.md"],
    "haber": ["content-quality-and-editorial-governance.md", "schema-validation-matrix.md"],
}

FRAMEWORKS = [
    ("Next.js", ["next.config.js", "next.config.mjs", "next.config.ts"], r'"next"\s*:'),
    ("Nuxt", ["nuxt.config.ts", "nuxt.config.js"], r'"nuxt"\s*:'),
    ("Astro", ["astro.config.mjs", "astro.config.ts", "astro.config.js"], r'"astro"\s*:'),
    ("SvelteKit", ["svelte.config.js"], r'"@sveltejs/kit"\s*:'),
    ("Gatsby", ["gatsby-config.js", "gatsby-config.ts"], r'"gatsby"\s*:'),
    ("Remix", [], r'"@remix-run/(react|node)"\s*:'),
    ("Create React App", [], r'"react-scripts"\s*:'),
    ("Vite + React", [], r'"react"\s*:'),      # yalnız vite de varsa korunur (aşağıdaki çakışma düzeltmesi)
    ("Vite + Vue", [], r'"vue"\s*:'),          # yalnız vite de varsa korunur
    ("Angular", ["angular.json"], r'"@angular/core"\s*:'),
    ("WordPress", ["wp-config.php", "wp-content", "functions.php"], None),
    ("Shopify teması", ["sections", "templates", "config/settings_schema.json"], None),
    ("Hugo", ["hugo.toml", "hugo.yaml", "config.toml"], None),
    ("Jekyll", ["_config.yml", "Gemfile"], None),
    ("Eleventy", [".eleventy.js", "eleventy.config.js"], None),
    ("Laravel", ["artisan", "composer.json"], None),
    ("Django", ["manage.py"], None),
    ("Rails", ["config/routes.rb"], None),
    ("Statik HTML", [], None),
]


def read(p, n=MAX_FILE):
    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(n)
    except Exception:
        return ""


def collect(root):
    files, total = [], 0
    names = set()
    routes = []
    ext_count = Counter()
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS and not d.startswith(".")]
        rel_dir = os.path.relpath(dp, root)
        for f in fn:
            ext = os.path.splitext(f)[1].lower()
            ext_count[ext] += 1
            names.add(os.path.join(rel_dir, f).replace("\\", "/").lstrip("./"))
            if ext in (".html", ".htm", ".md", ".mdx", ".tsx", ".jsx", ".vue", ".svelte", ".astro", ".liquid", ".php"):
                routes.append(os.path.join(rel_dir, f).replace("\\", "/").lstrip("./"))
            if ext in TEXT_EXT and len(files) < MAX_FILES and total < MAX_TOTAL:
                p = os.path.join(dp, f)
                try:
                    if os.path.getsize(p) > 2_000_000:
                        continue
                except OSError:
                    continue
                t = read(p)
                total += len(t)
                files.append((os.path.relpath(p, root).replace("\\", "/"), t))
    return files, names, routes, ext_count


def detect_framework(root, names, pkg_text):
    found = []
    for name, markers, dep_re in FRAMEWORKS:
        hit = False
        for m in markers:
            if os.path.exists(os.path.join(root, m)):
                hit = True
        if dep_re and pkg_text and re.search(dep_re, pkg_text):
            hit = True
        if hit and name not in ("Statik HTML",):
            found.append(name)
    # Çakışma düzeltmeleri
    has_vite = any(os.path.exists(os.path.join(root, f)) for f in
                   ("vite.config.js", "vite.config.ts", "vite.config.mjs", "vite.config.cjs")) \
        or bool(pkg_text and re.search(r'"vite"\s*:', pkg_text))
    for label in ("Vite + React", "Vite + Vue"):
        if label in found and not has_vite:
            found.remove(label)              # react/vue bağımlılığı tek başına "Vite" demek değildir
    react_meta = {"Next.js", "Remix", "Gatsby", "Astro"}
    if react_meta & set(found):
        for label in ("Vite + React", "Create React App"):
            if label in found:
                found.remove(label)          # meta-framework React'i zaten içerir
    if "Nuxt" in found and "Vite + Vue" in found:
        found.remove("Vite + Vue")
    if "Create React App" in found and "Vite + React" in found:
        found.remove("Vite + React")
    if "Laravel" in found and not os.path.exists(os.path.join(root, "artisan")):
        found.remove("Laravel")
    if "Jekyll" in found and not os.path.exists(os.path.join(root, "_config.yml")):
        found.remove("Jekyll")
    if "Shopify teması" in found and not (os.path.isdir(os.path.join(root, "sections")) and os.path.isdir(os.path.join(root, "templates"))):
        found.remove("Shopify teması")
    if "Hugo" in found and not any(n.startswith("content/") for n in names):
        found.remove("Hugo")
    if not found:
        found = ["Statik HTML"] if any(n.endswith((".html", ".htm")) for n in names) else ["Bilinmiyor"]
    return found


def render_strategy(frameworks, root, names):
    fw = " ".join(frameworks)
    notes = []
    if "Next.js" in fw:
        notes.append("Next.js: app/ veya pages/ yapısını, 'use client' yoğunluğunu ve generateMetadata kullanımını kontrol et; SSR/SSG çıktısını doğrula.")
    if any(k in fw for k in ("Vite + React", "Vite + Vue", "Angular", "Create React App")):
        notes.append("İstemci tarafı render (SPA) olabilir. Bu tek başına sorun DEĞİLDİR (Google JavaScript'i işleyebilir): "
                     "ilk HTML ile render edilmiş DOM'u karşılaştır (references/javascript-rendering-debugging.md). "
                     "Önemli içerik/link/meta yalnız JS sonrası geliyorsa ve kanıt varsa SSR/SSG/prerender öner; sırf SPA diye mimariyi yeniden yazma.")
    if "Astro" in fw or "Hugo" in fw or "Jekyll" in fw or "Eleventy" in fw or "Gatsby" in fw:
        notes.append("Statik üretim (SSG): derlenmiş çıktıyı (dist/public/_site) seo_audit.py ile denetle.")
    if "WordPress" in fw:
        notes.append("WordPress: Yoast/Rank Math ayarlarını ve tema başlık yapısını kontrol et; çekirdek dosyalara dokunma.")
    if "Shopify teması" in fw:
        notes.append("Shopify: Liquid şablonlarında canonical_url, structured_data filtresi, collection/product şablonlarını kontrol et.")
    return notes


def score_types(files):
    corpus = []
    for rel, t in files:
        low = t.lower()
        corpus.append((rel, low))
    results = {}
    for key, spec in TYPES.items():
        score = 0.0
        evidence = Counter()
        file_hits = Counter()
        for rx, w in spec["sig"]:
            r = re.compile(rx, re.I)
            total_hits = 0
            for rel, low in corpus:
                m = r.findall(low)
                if m:
                    total_hits += len(m)
                    file_hits[rel] += len(m)
            if total_hits:
                # logaritmik: 1 isabet = w, 10 isabet ≈ 2.3w, 100 ≈ 3.7w
                score += w * (1 + math.log10(total_hits) * 0.9 + (0.0 if total_hits < 2 else 0.4))
                evidence[rx[:40]] = total_hits
        results[key] = {"score": round(score, 1), "evidence_files": [f for f, _ in file_hits.most_common(4)]}
    return results


def route_signals(routes, names):
    sig = Counter()
    joined = " ".join(routes + list(names)).lower()
    pats = {
        "eticaret": r"\b(cart|sepet|checkout|product|urun|ürün|shop|magaza|store|collections?)\b",
        "yerel": r"\b(randevu|appointment|iletisim|contact|subeler|branches|locations?)\b",
        "saas": r"\b(pricing|dashboard|docs|api|changelog|integrations?|login|signup)\b",
        "blog": r"\b(blog|posts?|articles?|yazilar|makaleler|tag|tags|category|categories|authors?)\b",
        "portfolyo": r"\b(portfolio|portfolyo|projects?|projeler|works?|resume|cv|about)\b",
        "kurumsal": r"\b(hakkimizda|about-us|services|hizmetler|references|referanslar|careers|kariyer)\b",
        "ilan": r"\b(ilan|ilanlar|listings?|sellers?|vendors?|directory|rehber)\b",
        "egitim": r"\b(courses?|kurs|lessons?|ders|academy|akademi)\b",
        "haber": r"\b(haber|news|gundem|spor|ekonomi)\b",
    }
    for k, rx in pats.items():
        n = len(re.findall(rx, joined))
        if n:
            sig[k] = n
    return sig


def lang_info(files, root, names):
    tr_chars = sum(t.count(c) for _, t in files[:300] for c in "ğüşıöçĞÜŞİÖÇ")
    total = sum(len(t) for _, t in files[:300]) or 1
    ratio = tr_chars / total
    lang = "tr" if ratio > 0.004 else "en/diğer"
    m = None
    for _, t in files:
        m = re.search(r'<html[^>]*\blang=["\']([a-zA-Z-]+)', t)
        if m:
            lang = m.group(1)
            break
    multilingual = []
    joined = " ".join(names).lower()
    if re.search(r"(^|/)(locales?|i18n|translations?|lang|languages)(/|$)", joined):
        multilingual.append("locale/i18n klasörü")
    if re.search(r"(^|/)(en|tr|de|fr|es|ar|ru)/(index|page|\[)", joined):
        multilingual.append("dil dizin yapısı (/en/, /tr/ ...)")
    if any("hreflang" in t.lower() for _, t in files):
        multilingual.append("hreflang kullanımı")
    if any(re.search(r"next-intl|i18next|vue-i18n|@nuxtjs/i18n|paraglide|astro-i18n", t) for rel, t in files if rel.endswith("package.json")):
        multilingual.append("i18n kütüphanesi")
    return lang, multilingual


def brand_and_domain(files, root):
    brand, domain = None, None
    for rel, t in files:
        if rel.endswith("package.json") and "/" not in rel:
            try:
                j = json.loads(t)
                brand = j.get("name")
                if j.get("homepage"):
                    domain = j["homepage"]
            except Exception:
                pass
    cname = os.path.join(root, "CNAME")
    if os.path.exists(cname):
        domain = "https://" + read(cname).strip()
    for rel, t in files:
        if domain:
            break
        m = re.search(r"(siteUrl|site_url|SITE_URL|NEXT_PUBLIC_SITE_URL|baseURL|baseUrl|url)\s*[:=]\s*[\"']?(https?://[a-z0-9.-]+\.[a-z]{2,}[^\s\"',]*)", t)
        if m and "localhost" not in m.group(2) and "example." not in m.group(2):
            domain = m.group(2)
    for rel, t in files:
        m = re.search(r"<title[^>]*>([^<]{3,80})</title>", t, re.I)
        if m:
            brand = m.group(1).strip() if not brand else brand
            title = m.group(1).strip()
            break
    return brand, domain


def main():
    _utf8_stdio()
    ap = argparse.ArgumentParser(description="Site türü/teknoloji/dil algılama (sezgisel; çıktı bir HİPOTEZDİR).")
    ap.add_argument("root")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    if not os.path.isdir(root):
        sys.exit("Klasör bulunamadı: " + root)
    files, names, routes, ext_count = collect(root)
    if not files:
        sys.exit("Okunabilir kaynak dosya bulunamadı. Doğru proje klasörünü verdiniz mi?")
    pkg_text = next((t for rel, t in files if rel == "package.json"), "")
    frameworks = detect_framework(root, names, pkg_text)
    scores = score_types(files)
    rs = route_signals(routes, names)
    for k, n in rs.items():
        scores[k]["score"] = round(scores[k]["score"] + min(n, 12) * 1.2, 1)  # rota adı sinyali
        scores[k]["route_hits"] = n
    ranked = sorted(scores.items(), key=lambda kv: kv[1]["score"], reverse=True)
    top, second = ranked[0], ranked[1]
    top_score, second_score = top[1]["score"], second[1]["score"]
    if top_score < 8:
        confidence = "düşük"
        note = "Yeterli sinyal yok (çok küçük/boş proje olabilir). Kullanıcıya sitenin ne tür bir site olduğunu TEK soruyla sor."
    elif second_score and top_score / max(second_score, 0.1) < 1.35:
        confidence = "orta (karma olabilir)"
        note = f"'{top[0]}' ile '{second[0]}' birbirine yakın: karma site olabilir. İkisinin playbook'unu da oku; baskın olanı kullanıcıya doğrulat (TEK soru)."
    else:
        confidence = "yüksek"
        note = "Baskın tür net."
    lang, multi = lang_info(files, root, names)
    brand, domain = brand_and_domain(files, root)
    pages_est = len([r for r in routes if not re.search(r"(^|/)(components?|layouts?|partials?|includes?|_)", r)])
    hreflang_codes = sorted({m.lower() for _, t in files for m in re.findall(r'hreflang\s*[=:]\s*["\']([A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,4})?|x-default)["\']', t)})
    render_notes = render_strategy(frameworks, root, names)
    is_mixed = confidence.startswith("orta")
    type_keys = [top[0]] + ([second[0]] if is_mixed else [])
    extra = []
    for k in type_keys:
        for ref in EXTRA_REFS.get(k, []):
            if ref not in extra:
                extra.append(ref)
    layers = []
    if multi or len(hreflang_codes) > 1:
        layers += ["site-tipleri/katmanlar.md#cok-dilli", "global-market-research.md", "international-localization-operations.md", "international-seo-qa.md"]
    if any("SPA" in n or "istemci tarafı" in n for n in render_notes):
        layers += ["site-tipleri/katmanlar.md#spa", "javascript-rendering-debugging.md"]

    out = {
        "kanit_duzeyi": "Hipotez (kod/metin sinyallerine dayalı sezgisel puanlama; kesin hüküm değildir)",
        "klasor": root,
        "tahmin_edilen_tur": top[0],
        "tur_adi": TYPES[top[0]]["ad"],
        "guven": confidence,
        "not": note,
        "playbooklar": [TYPES[top[0]]["playbook"]] + ([TYPES[second[0]]["playbook"]] if is_mixed and TYPES[second[0]]["playbook"] != TYPES[top[0]]["playbook"] else []),
        "ek_referanslar": extra,
        "siralama": [{"tur": k, "ad": TYPES[k]["ad"], "puan": v["score"], "kanit_dosyalar": v["evidence_files"]} for k, v in ranked[:5]],
        "teknoloji": frameworks,
        "render_notlari": render_notes,
        "dil": lang,
        "cok_dilli": multi,
        "hreflang_kodlari": hreflang_codes,
        "marka_tahmini": brand,
        "alan_adi_tahmini": domain,
        "sayfa_dosyasi_sayisi": pages_est,
        "katmanlar": layers,
    }
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return
    print(f"== SİTE ALGILAMA: {root} ==")
    print("Kanıt düzeyi: Hipotez (sezgisel puanlama; kesin hüküm değil)")
    print(f"Tür tahmini : {out['tur_adi']}  [{top[0]}]  (güven: {confidence})")
    print(f"Not         : {note}")
    print("Sıralama    : " + " | ".join(f"{r['tur']}={r['puan']}" for r in out["siralama"]))
    for r in out["siralama"][:2]:
        if r["kanit_dosyalar"]:
            print(f"  kanıt[{r['tur']}]: " + ", ".join(r["kanit_dosyalar"]))
    print(f"Teknoloji   : {', '.join(frameworks)}")
    for n in out["render_notlari"]:
        print(f"  - {n}")
    print(f"Dil         : {lang}   Çok dillilik: {', '.join(multi) or 'yok'}" + (f"   hreflang: {', '.join(hreflang_codes)}" if hreflang_codes else ""))
    print(f"Marka/Alan  : {brand or '?'} / {domain or '? (kodda bulunamadı → kullanıcıya sor)'}")
    print(f"Sayfa dosyası (yaklaşık): {pages_est}")
    print("Okunacak playbook: " + ", ".join("references/" + p for p in out["playbooklar"]))
    if out["ek_referanslar"]:
        print("Ek referanslar   : " + ", ".join("references/" + p for p in out["ek_referanslar"]))
    if out["katmanlar"]:
        print("Ek katmanlar     : " + ", ".join("references/" + p for p in out["katmanlar"]))


if __name__ == "__main__":
    main()
