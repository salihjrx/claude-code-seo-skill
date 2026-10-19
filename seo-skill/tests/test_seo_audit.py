"""seo_audit.py testleri: önem düzeyi politikası (PAKET-DENETIMI düzeltmeleri) ve release-blocker tespiti."""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "seo_audit.py"
spec = importlib.util.spec_from_file_location("seo_audit", SCRIPT)
sa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sa)

GOOD = """<!doctype html><html lang="tr"><head><meta charset="utf-8">
<title>Teknik SEO nedir? Adım adım kontrol listesi | Marka</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Teknik SEO nedir, nasıl yapılır? Tarama, dizine ekleme ve hız için kontrol listesi ve örnekler.">
<link rel="canonical" href="https://example.com/teknik-seo">
<meta property="og:title" content="x"><meta property="og:image" content="https://example.com/o.jpg">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article","headline":"x"}</script>
</head><body><h1>Teknik SEO nedir?</h1><h2>Giriş</h2><p>%s</p></body></html>""" % ("kelime " * 200)


def codes(result):
    return {c for _, _, c in result["issues"]}


def levels(result, code):
    return {l for l, _, c in result["issues"] if c == code}


class PagePolicyTests(unittest.TestCase):
    def test_clean_page_has_no_findings(self):
        r = sa.audit_html(GOOD, "good.html")
        self.assertEqual(r["issues"], [], r["issues"])

    def test_missing_h1_is_warning_not_critical(self):
        r = sa.audit_html(GOOD.replace("<h1>Teknik SEO nedir?</h1>", ""), "x")
        self.assertEqual(levels(r, "h1_missing"), {"UYARI"})

    def test_multiple_h1_is_info_only(self):
        r = sa.audit_html(GOOD.replace("<h2>Giriş</h2>", "<h1>İkinci</h1>"), "x")
        self.assertEqual(levels(r, "h1_multiple"), {"BİLGİ"})

    def test_missing_viewport_is_warning_not_critical(self):
        r = sa.audit_html(GOOD.replace('<meta name="viewport" content="width=device-width, initial-scale=1">', ""), "x")
        self.assertEqual(levels(r, "viewport_missing"), {"UYARI"})

    def test_title_and_description_length_are_guidelines(self):
        long_title = GOOD.replace("Teknik SEO nedir? Adım adım kontrol listesi | Marka", "A" * 90)
        r = sa.audit_html(long_title, "x")
        self.assertEqual(levels(r, "title_long"), {"BİLGİ"})
        short_title = GOOD.replace("Teknik SEO nedir? Adım adım kontrol listesi | Marka", "Kısa başlık")
        self.assertEqual(levels(sa.audit_html(short_title, "x"), "title_short"), {"BİLGİ"})
        msg = [m for _, m, c in r["issues"] if c == "title_long"][0]
        self.assertIn("sabit sınır değildir", msg)

    def test_generic_framework_title_is_flagged(self):
        r = sa.audit_html(GOOD.replace("Teknik SEO nedir? Adım adım kontrol listesi | Marka", "Vite + React"), "x")
        self.assertIn("title_generic", codes(r))

    def test_invalid_jsonld_is_warning(self):
        r = sa.audit_html(GOOD.replace('{"@context":"https://schema.org","@type":"Article","headline":"x"}', "{bozuk"), "x")
        self.assertEqual(levels(r, "jsonld_invalid"), {"UYARI"})

    def test_no_jsonld_is_info_and_not_required(self):
        html = GOOD.split('<script type="application/ld+json">')[0] + "</head><body><h1>x</h1></body></html>"
        r = sa.audit_html(html, "x")
        self.assertEqual(levels(r, "jsonld_none"), {"BİLGİ"})
        self.assertIn("her sayfada gerekmez", [m for _, m, c in r["issues"] if c == "jsonld_none"][0])

    def test_faq_markup_note_reflects_google_retirement(self):
        html = GOOD.replace('"@type":"Article"', '"@type":"FAQPage"')
        r = sa.audit_html(html, "x")
        self.assertEqual(levels(r, "jsonld_faq"), {"BİLGİ"})

    def test_thin_html_mentions_js_rendering_instead_of_calling_it_broken(self):
        spa = '<!doctype html><html lang="tr"><head><title>Uygulama paneli ve ürün tanıtımı sayfası</title></head><body><div id="root"></div></body></html>'
        r = sa.audit_html(spa, "spa.html")
        msg = [m for _, m, c in r["issues"] if c == "thin_initial_html"][0]
        self.assertIn("JS ile sonradan yükleniyor olabilir", msg)
        self.assertNotIn("KRİTİK", {l for l, _, c in r["issues"] if c == "thin_initial_html"})

    def test_canonical_to_localhost_is_critical(self):
        r = sa.audit_html(GOOD.replace("https://example.com/teknik-seo", "http://localhost:3000/teknik-seo"), "x")
        self.assertEqual(levels(r, "canonical_local"), {"KRİTİK"})

    def test_canonical_staging_and_relative(self):
        r = sa.audit_html(GOOD.replace("https://example.com/teknik-seo", "https://staging.example.com/a"), "x")
        self.assertEqual(levels(r, "canonical_staging"), {"UYARI"})
        r = sa.audit_html(GOOD.replace("https://example.com/teknik-seo", "/teknik-seo"), "x")
        self.assertEqual(levels(r, "canonical_relative"), {"UYARI"})

    def test_noindex_via_meta_and_header(self):
        meta = GOOD.replace("</head>", '<meta name="robots" content="noindex,follow"></head>')
        self.assertEqual(levels(sa.audit_html(meta, "x"), "noindex"), {"UYARI"})
        self.assertIn("noindex", codes(sa.audit_html(GOOD, "x", x_robots="noindex, nofollow")))
        self.assertTrue(sa.audit_html(GOOD, "x", x_robots="NOINDEX")["stats"]["noindex"])

    def test_hreflang_validation(self):
        bad = GOOD.replace("</head>", '<link rel="alternate" hreflang="turkce" href="/tr"></head>')
        r = sa.audit_html(bad, "x")
        self.assertIn("hreflang_invalid", codes(r))
        self.assertIn("hreflang_relative", codes(r))
        ok = GOOD.replace("</head>", '<link rel="alternate" hreflang="tr-TR" href="https://example.com/teknik-seo">'
                                     '<link rel="alternate" hreflang="x-default" href="https://example.com/"></head>')
        self.assertNotIn("hreflang_invalid", codes(sa.audit_html(ok, "x")))
        self.assertNotIn("hreflang_no_self", codes(sa.audit_html(ok, "x")))


class RobotsTests(unittest.TestCase):
    def find(self, text):
        return {c: l for l, _, c in sa.robots_findings(text)}

    def test_wildcard_disallow_all_is_critical(self):
        self.assertEqual(self.find("User-agent: *\nDisallow: /\nSitemap: https://e.com/s.xml")["robots_blocks_all"], "KRİTİK")

    def test_blocking_a_single_unrelated_bot_is_not_critical(self):
        found = self.find("User-agent: BadBot\nDisallow: /\n\nUser-agent: *\nDisallow:\nSitemap: https://e.com/s.xml")
        self.assertNotIn("robots_blocks_all", found)

    def test_disallow_subpath_is_fine(self):
        self.assertNotIn("robots_blocks_all", self.find("User-agent: *\nDisallow: /admin/\nSitemap: https://e.com/s.xml"))

    def test_disallow_all_with_allow_exceptions_is_warning(self):
        found = self.find("User-agent: *\nDisallow: /\nAllow: /blog/\nSitemap: https://e.com/s.xml")
        self.assertEqual(found["robots_mostly_blocked"], "UYARI")

    def test_wildcard_blocked_but_googlebot_allowed(self):
        found = self.find("User-agent: Googlebot\nDisallow:\n\nUser-agent: *\nDisallow: /\nSitemap: https://e.com/s.xml")
        self.assertEqual(found["robots_only_google"], "UYARI")
        self.assertNotIn("robots_blocks_all", found)

    def test_ai_bot_blocking_is_informational_only(self):
        found = self.find("User-agent: GPTBot\nDisallow: /\n\nUser-agent: *\nAllow: /\nSitemap: https://e.com/s.xml")
        self.assertEqual(found["robots_blocks_ai_bots"], "BİLGİ")
        self.assertNotIn("robots_blocks_all", found)

    def test_missing_sitemap_line(self):
        self.assertIn("robots_no_sitemap", self.find("User-agent: *\nDisallow:"))

    def test_comments_and_case_are_handled(self):
        found = self.find("# staging\nUSER-AGENT: *   # herkes\nDISALLOW: /   # hepsi\nSitemap: https://e.com/s.xml")
        self.assertEqual(found["robots_blocks_all"], "KRİTİK")


class LeakTests(unittest.TestCase):
    def test_leak_findings(self):
        out = sa.leak_findings(["https://e.com/a", "http://localhost:3000/b", "https://staging.e.com/c"], "sitemap")
        self.assertEqual({c: l for l, _, c in out}, {"leak_local": "KRİTİK", "leak_staging": "UYARI"})
        self.assertEqual(sa.leak_findings(["https://e.com/a"], "sitemap"), [])


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-I", str(SCRIPT), *args], capture_output=True, text=True, encoding="utf-8")

    def test_directory_mode_exit_codes_and_json(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "index.html").write_text(GOOD, encoding="utf-8")
            (root / "robots.txt").write_text("User-agent: *\nDisallow:\nSitemap: https://example.com/sitemap.xml\n", encoding="utf-8")
            (root / "sitemap.xml").write_text("<urlset/>", encoding="utf-8")
            ok = self.run_cli(str(root), "--json")
            self.assertEqual(ok.returncode, 0, ok.stderr)
            data = json.loads(ok.stdout)
            self.assertEqual(data["critical"], 0)
            self.assertIn("triyaj", data["notice"])
            (root / "robots.txt").write_text("User-agent: *\nDisallow: /\n", encoding="utf-8")
            bad = self.run_cli(str(root))
            self.assertEqual(bad.returncode, 1)
            self.assertIn("tüm siteyi engelliyor", bad.stdout)
            self.assertIn("Otomatik triyaj", bad.stdout)  # sınır uyarısı çıktıda her zaman var

    def test_all_noindex_is_critical(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "index.html").write_text(GOOD.replace("</head>", '<meta name="robots" content="noindex"></head>'), encoding="utf-8")
            (root / "robots.txt").write_text("User-agent: *\nDisallow:\nSitemap: https://example.com/s.xml\n", encoding="utf-8")
            res = self.run_cli(str(root), "--json")
            self.assertEqual(res.returncode, 1)
            self.assertTrue(any(c == "all_noindex" for _, _, c in json.loads(res.stdout)["site"]))

    def test_url_mode_refuses_local_addresses_by_default(self):
        res = self.run_cli("--url", "http://127.0.0.1:9/")
        self.assertNotEqual(res.returncode, 0)
        self.assertIn("--allow-private", res.stderr + res.stdout)

    def test_pipe_with_non_utf8_locale_does_not_crash(self):
        # Windows'ta stdout cp1254/cp1252 olabilir; betik UTF-8'e geçmeli (✓, → gibi karakterler)
        env = dict(os.environ, PYTHONIOENCODING="cp1254")
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "index.html").write_text(GOOD.replace("<h1>", "<h1 data-x='✓→'>"), encoding="utf-8")
            (Path(d) / "robots.txt").write_text("User-agent: *\nDisallow:\nSitemap: https://example.com/s.xml\n", encoding="utf-8")
            res = subprocess.run([sys.executable, str(SCRIPT), d], capture_output=True, env=env)
            self.assertEqual(res.returncode, 0, res.stderr.decode("utf-8", "replace"))
            self.assertIn("✓ sorun yok".encode("utf-8"), res.stdout)  # çıktı UTF-8 olarak yazıldı


if __name__ == "__main__":
    unittest.main()
