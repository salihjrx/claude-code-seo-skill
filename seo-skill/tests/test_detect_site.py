"""detect_site.py testleri: site türü, framework etiketi, SPA notu (otomatik 'kritik' değil), ek referanslar."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "detect_site.py"


def make(root, files):
    for rel, content in files.items():
        p = Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def detect(files):
    with tempfile.TemporaryDirectory() as d:
        make(d, files)
        res = subprocess.run([sys.executable, "-I", str(SCRIPT), d, "--json"], capture_output=True, text=True, encoding="utf-8")
        return res, (json.loads(res.stdout) if res.returncode == 0 else None)


PRODUCT_LD = '<script type="application/ld+json">{"@type":"Product","name":"Ayakkabı","offers":{"@type":"Offer","price":"999"}}</script>'


class TypeDetectionTests(unittest.TestCase):
    def test_ecommerce_next_app(self):
        res, out = detect({
            "package.json": '{"name":"magaza","dependencies":{"next":"14.0.0","react":"18.2.0","stripe":"14.0.0"}}',
            "next.config.js": "module.exports = {}",
            "app/page.tsx": "export default function P(){return <div><button>Sepete ekle</button> Fiyat: 999 TL Stokta var, kargo ücretsiz, iade 14 gün</div>}",
            "app/cart/page.tsx": "export default function C(){return <div>Sepet · Ödeme · Sipariş özeti</div>}",
            "app/products/[slug]/page.tsx": "export default function Pr(){return <div>SKU: A1 barkod stok add to cart %s</div>}" % PRODUCT_LD,
        })
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(out["tahmin_edilen_tur"], "eticaret")
        self.assertEqual(out["guven"], "yüksek")
        self.assertIn("Next.js", out["teknoloji"])
        self.assertIn("site-tipleri/eticaret.md", out["playbooklar"])
        self.assertIn("ecommerce-catalog-and-facets.md", out["ek_referanslar"])
        self.assertIn("Hipotez", out["kanit_duzeyi"])

    def test_blog_content_site(self):
        post = "---\ntitle: Yazı %d\ndatePublished: 2026-01-0%d\nauthor: Ayşe\ntags: [seo]\n---\nBlog yazısı okuma süresi 5 min read. Yorumlar ve bülten abone ol."
        res, out = detect({
            "package.json": '{"name":"blog","dependencies":{"astro":"4.0.0"}}',
            "astro.config.mjs": "export default {}",
            **{f"src/content/blog/yazi-{i}.md": post % (i, i) for i in range(1, 6)},
            "src/pages/blog/index.astro": "<h1>Blog</h1> makaleler yazılar etiket kategori arşivi rss",
        })
        self.assertEqual(out["tahmin_edilen_tur"], "blog")
        self.assertIn("Astro", out["teknoloji"])
        self.assertIn("content-brief-template.md", out["ek_referanslar"])

    def test_local_business_static_site(self):
        res, out = detect({
            "index.html": ('<html lang="tr"><head><title>Diş Kliniği Kadıköy</title>'
                           '<script type="application/ld+json">{"@type":"Dentist","name":"Klinik"}</script></head><body>'
                           'Çalışma saatleri: 09-18. Randevu al: <a href="tel:+905321234567">ara</a> WhatsApp. '
                           '<a href="https://www.google.com/maps/place/x">Yol tarifi</a> Adres: Kadıköy mahalle ilçe. Diş kliniği muayenehane.</body></html>'),
            "iletisim.html": "<html><body>Randevu rezervasyon şubemiz adres konum</body></html>",
        })
        self.assertEqual(out["tahmin_edilen_tur"], "yerel")
        self.assertEqual(out["dil"], "tr")

    def test_empty_directory_exits_with_message(self):
        with tempfile.TemporaryDirectory() as d:
            res = subprocess.run([sys.executable, "-I", str(SCRIPT), d], capture_output=True, text=True, encoding="utf-8")
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("kaynak dosya bulunamadı", res.stderr)


class FrameworkTests(unittest.TestCase):
    def test_vite_react_spa_note_is_not_an_automatic_critical_finding(self):
        res, out = detect({
            "package.json": '{"name":"app","dependencies":{"react":"18.2.0","vite":"5.0.0","stripe":"1"}}',
            "vite.config.ts": "export default {}",
            "index.html": '<html><head><title>Uygulama</title></head><body><div id="root"></div></body></html>',
            "src/pages/pricing.tsx": "Pricing plans free trial get started dashboard api docs sign up",
            "src/pages/dashboard.tsx": "dashboard integrations webhook changelog",
        })
        self.assertEqual(out["teknoloji"], ["Vite + React"])
        note = " ".join(out["render_notlari"])
        self.assertNotIn("KRİTİK", note)
        self.assertIn("tek başına sorun DEĞİLDİR", note)
        self.assertIn("render edilmiş DOM", note)
        self.assertIn("javascript-rendering-debugging.md", out["katmanlar"])
        self.assertIn("site-tipleri/katmanlar.md#spa", out["katmanlar"])

    def test_create_react_app_is_not_labelled_vite(self):
        res, out = detect({
            "package.json": '{"name":"cra","dependencies":{"react":"18.2.0","react-scripts":"5.0.1"}}',
            "src/App.js": "export default function App(){return null}",
        })
        self.assertIn("Create React App", out["teknoloji"])
        self.assertNotIn("Vite + React", out["teknoloji"])

    def test_remix_is_not_also_labelled_vite_react(self):
        res, out = detect({
            "package.json": '{"name":"rx","dependencies":{"@remix-run/react":"2.0.0","react":"18.2.0"}}',
            "app/root.tsx": "export default function Root(){return null}",
        })
        self.assertEqual(out["teknoloji"], ["Remix"])

    def test_plain_react_dependency_alone_is_not_vite(self):
        res, out = detect({
            "package.json": '{"name":"x","dependencies":{"react":"18.2.0"}}',
            "src/index.js": "console.log(1)",
        })
        self.assertNotIn("Vite + React", out["teknoloji"])

    def test_nuxt_is_not_also_labelled_vite_vue(self):
        res, out = detect({
            "package.json": '{"name":"nx","dependencies":{"nuxt":"3.0.0","vue":"3.4.0","vite":"5.0.0"}}',
            "nuxt.config.ts": "export default {}",
            "app.vue": "<template><div/></template>",
        })
        self.assertEqual(out["teknoloji"], ["Nuxt"])


class LocaleTests(unittest.TestCase):
    def test_hreflang_triggers_international_references(self):
        res, out = detect({
            "index.html": ('<html lang="tr"><head><title>Ana</title>'
                           '<link rel="alternate" hreflang="tr" href="https://e.com/tr/">'
                           '<link rel="alternate" hreflang="en" href="https://e.com/en/">'
                           '<link rel="alternate" hreflang="x-default" href="https://e.com/"></head><body>merhaba</body></html>'),
            "en/index.html": "<html lang='en'><body>hello</body></html>",
        })
        self.assertEqual(out["hreflang_kodlari"], ["en", "tr", "x-default"])
        self.assertIn("international-seo-qa.md", out["katmanlar"])
        self.assertIn("global-market-research.md", out["katmanlar"])


class CliOutputTests(unittest.TestCase):
    def test_human_readable_output_labels_result_as_hypothesis_and_survives_cp1254(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            make(d, {"index.html": "<html lang='tr'><body>Sepete ekle fiyat stok kargo sepet ödeme</body></html>"})
            env = dict(os.environ, PYTHONIOENCODING="cp1254")
            res = subprocess.run([sys.executable, str(SCRIPT), d], capture_output=True, env=env)
            self.assertEqual(res.returncode, 0, res.stderr.decode("utf-8", "replace"))
            text = res.stdout.decode("utf-8")
            self.assertIn("Kanıt düzeyi: Hipotez", text)
            self.assertIn("→", text)  # cp1254'te olmayan karakter sorunsuz yazıldı


if __name__ == "__main__":
    unittest.main()
