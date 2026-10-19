import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).parents[1] / "scripts" / "seo_url_audit.py"
spec = importlib.util.spec_from_file_location("seo_url_audit", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ParserTests(unittest.TestCase):
    def test_extracts_basic_signals(self):
        p = mod.Parser()
        p.feed("""<html><head><title>Example page</title>
        <meta name="description" content="Useful summary">
        <meta name="robots" content="index,follow">
        <link rel="canonical" href="https://example.com/a">
        <link rel="alternate" hreflang="tr-TR" href="https://example.com/tr/a">
        </head><body><h1>Primary heading</h1><a href="/b">next</a></body></html>""")
        self.assertEqual(" ".join(p.title_parts), "Example page")
        self.assertEqual(p.meta["description"], "Useful summary")
        self.assertEqual(p.canonicals, ["https://example.com/a"])
        self.assertEqual(p.hreflang[0][0], "tr-TR")
        self.assertEqual(p.links, 1)

    def test_empty_document(self):
        p = mod.Parser()
        p.feed("")
        self.assertEqual(p.canonicals, [])
        self.assertEqual(p.links, 0)

    def test_localhost_is_blocked_before_network_request(self):
        row = mod.audit("http://localhost/", timeout=1, delay=0)
        self.assertIn("Blocked local hostname", row["error"])

    def test_non_http_scheme_is_rejected(self):
        row = mod.audit("file:///etc/passwd", timeout=1, delay=0)
        self.assertIn("Invalid URL", row["error"])

if __name__ == "__main__": unittest.main()
