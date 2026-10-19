"""seo_url_audit.py ek testleri: netguard üzerinden güvenli getirme, yönlendirme zinciri, noindex/canonical
sütunları, iç/dış bağlantı sayımı, CSV şeması (eski sütunlar korunur, yenileri sona eklenir)."""
import csv
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _httpd import LocalServer, redirect, send  # noqa: E402

SCRIPT = Path(__file__).parents[1] / "scripts" / "seo_url_audit.py"
spec = importlib.util.spec_from_file_location("seo_url_audit", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

APEX_FIELDS = ["url", "status", "final_url", "content_type", "title", "title_chars", "description",
               "h1_count", "h1", "canonical", "canonical_count", "robots", "x_robots_tag",
               "hreflang_count", "internal_links_count", "html_bytes", "error"]


def page_handler(canonical_path="/ok", extra_head="", extra_body="", headers=()):
    def handler(h):
        host = h.headers["Host"]
        html = (f'<!doctype html><html lang="tr"><head><title>Örnek sayfa başlığı</title>'
                f'<meta name="description" content="Kısa açıklama"><link rel="canonical" href="http://{host}{canonical_path}">'
                f'{extra_head}</head><body><h1>Birinci</h1><h1>İkinci</h1>'
                f'<script>var s = "<h1>sahte</h1>";</script>'
                f'<a href="/a">a</a><a href="http://{host}/b">b</a><a href="#top">üst</a>'
                f'<a href="mailto:x@e.com">mail</a><a href="https://example.org/x">dış</a>{extra_body}</body></html>')
        send(h, 200, html.encode("utf-8"), headers=headers)
    return handler


def routes():
    return {
        "/ok": page_handler(headers=[("X-Robots-Tag", "noarchive"), ("X-Robots-Tag", "noindex")]),
        "/clean": page_handler("/clean"),
        "/other-canon": page_handler("/elsewhere"),
        "/multi-canon": page_handler("/multi-canon", extra_head='<link rel="canonical" href="https://e.com/b">'),
        "/meta-noindex": page_handler("/meta-noindex", extra_head='<meta name="robots" content="noindex, follow">'),
        "/redir": lambda h: redirect(h, "/clean", 301),
        "/chain1": lambda h: redirect(h, "/chain2"),
        "/chain2": lambda h: redirect(h, "/clean"),
        "/loop": lambda h: redirect(h, "/loop"),
        "/gone": lambda h: send(h, 410, b"gone", ctype="text/plain"),
        "/pdf": lambda h: send(h, 200, b"%PDF-1.4", ctype="application/pdf", headers=[("X-Robots-Tag", "noindex")]),
        "/big": lambda h: send(h, 200, b"<html>" + b"a" * 3_100_000),
    }


class ParserTests(unittest.TestCase):
    def test_h1_count_comes_from_parser_not_regex(self):
        p = mod.Parser()
        p.feed('<h1>Gerçek</h1><script>var x = "<h1>sahte</h1>";</script><!-- <h1>yorum</h1> -->')
        self.assertEqual(p.h1_count, 1)

    def test_split_links_counts_internal_and_external_only(self):
        internal, external = mod.split_links(
            ["/a", "https://e.com/b", "#x", "mailto:a@b.c", "tel:+90", "javascript:void(0)", "https://other.org/z", ""],
            "https://e.com/page")
        self.assertEqual((internal, external), (2, 1))


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = LocalServer(routes())
        cls.srv.__enter__()
        cls.base = cls.srv.base

    @classmethod
    def tearDownClass(cls):
        cls.srv.__exit__(None, None, None)

    def a(self, path, **kw):
        return mod.audit(self.base + path, timeout=5, delay=0, allow_private=True, **kw)

    def test_private_target_refused_by_default(self):
        row = mod.audit(self.base + "/clean", timeout=2, delay=0)
        self.assertIn("Blocked non-public IP destination", row["error"])

    def test_basic_signals_and_multi_value_x_robots(self):
        r = self.a("/ok")
        self.assertEqual(r["status"], 200)
        self.assertEqual(r["title"], "Örnek sayfa başlığı")
        self.assertEqual(r["h1_count"], 2)              # script içindeki sahte <h1> sayılmaz
        self.assertEqual(r["canonical_status"], "self")
        self.assertIn("noarchive", r["x_robots_tag"])
        self.assertIn("noindex", r["x_robots_tag"])
        self.assertEqual(r["noindex"], "yes")
        self.assertEqual(r["internal_links_count"], 2)
        self.assertEqual(r["external_links_count"], 1)
        self.assertEqual(r["redirect_hops"], 0)

    def test_clean_page_is_indexable_with_self_canonical(self):
        r = self.a("/clean")
        self.assertEqual(r["noindex"], "no")
        self.assertEqual(r["canonical_status"], "self")
        self.assertEqual(r["error"], "")

    def test_canonical_variants(self):
        self.assertEqual(self.a("/other-canon")["canonical_status"], "different")
        self.assertEqual(self.a("/multi-canon")["canonical_status"], "multiple")

    def test_meta_robots_noindex_detected(self):
        r = self.a("/meta-noindex")
        self.assertEqual(r["noindex"], "yes")
        self.assertIn("noindex", r["robots"])

    def test_redirect_chain_is_recorded(self):
        r = self.a("/redir")
        self.assertEqual((r["status"], r["redirect_hops"]), (200, 1))
        self.assertTrue(r["final_url"].endswith("/clean"))
        self.assertIn("[301]", r["redirect_chain"])
        r2 = self.a("/chain1")
        self.assertEqual(r2["redirect_hops"], 2)

    def test_redirect_loop_and_too_many_redirects_reported(self):
        self.assertIn("loop", self.a("/loop")["error"].lower())
        self.assertIn("Too many redirects", self.a("/chain1", max_redirects=1)["error"])

    def test_http_error_status_is_reported(self):
        r = self.a("/gone")
        self.assertEqual(r["status"], 410)
        self.assertIn("HTTPError: 410", r["error"])

    def test_non_html_noindex_header(self):
        r = self.a("/pdf")
        self.assertEqual(r["noindex"], "yes")
        self.assertEqual(r["title"], "")

    def test_oversized_body_is_truncated_and_flagged(self):
        r = self.a("/big")
        self.assertIn("truncated", r["error"])

    def test_unsafe_hop_is_reported_as_blocked_during_redirect(self):
        original = mod.netguard.fetch

        def fake_fetch(*a, **k):
            raise mod.netguard.BlockedError("Blocked non-public IP destination")

        mod.netguard.fetch = fake_fetch
        try:
            r = mod.audit("https://example.com/", timeout=2, delay=0)
        finally:
            mod.netguard.fetch = original
        self.assertIn("Blocked non-public IP destination", r["error"])
        self.assertIn("during redirect", r["error"])


class CliTests(unittest.TestCase):
    def test_csv_keeps_apex_columns_first_and_appends_new_ones(self):
        with LocalServer(routes()) as srv, tempfile.TemporaryDirectory() as d:
            urls = Path(d) / "urls.txt"
            urls.write_text(f"# yorum satırı\n{srv.base}/clean\n{srv.base}/clean\n{srv.base}/redir\n", encoding="utf-8")
            out = Path(d) / "out.csv"
            res = subprocess.run([sys.executable, "-I", str(SCRIPT), str(urls), "-o", str(out), "--delay", "0",
                                  "--allow-private"], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(res.returncode, 0, res.stderr)
            with open(out, encoding="utf-8-sig", newline="") as f:
                rd = csv.DictReader(f)
                self.assertEqual(rd.fieldnames[:len(APEX_FIELDS)], APEX_FIELDS)
                self.assertEqual(rd.fieldnames[len(APEX_FIELDS):],
                                 ["redirect_hops", "redirect_chain", "noindex", "canonical_status", "external_links_count"])
                rows = list(rd)
            self.assertEqual(len(rows), 2)               # tekrarlayan URL tek satır
            self.assertEqual(rows[1]["redirect_hops"], "1")

    def test_cli_refuses_private_targets_without_flag(self):
        with LocalServer(routes()) as srv, tempfile.TemporaryDirectory() as d:
            urls = Path(d) / "urls.txt"
            urls.write_text(f"{srv.base}/clean\n", encoding="utf-8")
            out = Path(d) / "out.csv"
            res = subprocess.run([sys.executable, "-I", str(SCRIPT), str(urls), "-o", str(out), "--delay", "0"],
                                 capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(res.returncode, 0, res.stderr)
            with open(out, encoding="utf-8-sig", newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertIn("Blocked non-public IP destination", rows[0]["error"])

    def test_empty_input_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as d:
            urls = Path(d) / "urls.txt"
            urls.write_text("# sadece yorum\n\n", encoding="utf-8")
            res = subprocess.run([sys.executable, "-I", str(SCRIPT), str(urls)], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(res.returncode, 2)


if __name__ == "__main__":
    unittest.main()
