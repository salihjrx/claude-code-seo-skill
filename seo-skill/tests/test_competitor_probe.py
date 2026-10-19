"""competitor_probe.py testleri: ölçüm, bot-engeli (aşılmaz), konu boşluğu analizi, güvenlik varsayılanları."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "competitor_probe.py"
spec = importlib.util.spec_from_file_location("competitor_probe", SCRIPT)
cp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cp)


def page(h2s, words=400, title="Teknik SEO nedir? Rehber 2026", extra=""):
    body = "".join(f"<h2>{h}</h2><p>{'metin ' * (words // max(len(h2s), 1))}</p>" for h in h2s)
    return (f'<!doctype html><html lang="tr"><head><title>{title}</title>'
            '<meta name="description" content="Açıklama metni burada yer alır ve yeterince uzundur diye yazılmıştır.">'
            '<link rel="canonical" href="https://e.com/a"></head>'
            f'<body><h1>Teknik SEO</h1>{body}{extra}</body></html>')


class MeasureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, html):
        p = self.dir / name
        p.write_text(html, encoding="utf-8")
        return str(p)

    def test_measures_local_file(self):
        f = self.write("a.html", page(["Robots.txt nedir", "Sitemap nedir", "Canonical nedir"],
                                      extra="<ul><li>a</li></ul><h2>Sık sorulan sorular</h2>"))
        m = cp.measure(f)
        self.assertTrue(m["ok"])
        self.assertEqual(m["h1"], ["Teknik SEO"])
        self.assertEqual(len(m["h2"]), 4)
        self.assertTrue(m["sss"])
        self.assertTrue(m["canonical"])
        self.assertTrue(m["yil_title_desc"])
        self.assertEqual(m["lang"], "tr")

    def test_bot_challenge_page_is_reported_as_unmeasurable_not_bypassed(self):
        f = self.write("c.html", "<html><head><title>Just a moment...</title></head><body>Checking your browser before accessing</body></html>")
        m = cp.measure(f)
        self.assertFalse(m["ok"])
        self.assertIn("aşılmaya çalışılmadı", m["neden"])

    def test_gap_analysis_marks_topics_shared_by_competitors(self):
        comp = [
            {"ok": True, "url": "c1", "h2": ["Robots.txt nedir", "Sitemap xml nedir", "Canonical etiketi"]},
            {"ok": True, "url": "c2", "h2": ["Robots.txt dosyası nedir", "Sitemap xml nedir", "Hız ölçümü"]},
            {"ok": True, "url": "c3", "h2": ["Robots.txt nedir ve nasıl yazılır", "Canonical etiketi nedir"]},
        ]
        mine = {"ok": True, "url": "mine", "h2": ["Sitemap xml nedir"]}
        gaps = cp.gap_analysis(mine, comp)
        by_topic = {g["konu"]: g for g in gaps}
        robots = [g for g in gaps if "obots" in g["konu"]][0]
        self.assertGreaterEqual(robots["kac_rakipte"], 3)
        self.assertFalse(robots["senin_sayfanda"])
        sitemap = [g for g in gaps if "itemap" in g["konu"]][0]
        self.assertTrue(sitemap["senin_sayfanda"])
        self.assertFalse(any("Hız ölçümü" in t for t in by_topic))  # yalnız tek rakipte geçen konu "zorunlu" sayılmaz

    def test_gap_analysis_without_competitors(self):
        self.assertEqual(cp.gap_analysis(None, [{"ok": False}]), [])


class CliTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-I", str(SCRIPT), *args], capture_output=True, text=True, encoding="utf-8")

    def test_json_output_with_files_and_self(self):
        with tempfile.TemporaryDirectory() as d:
            files = []
            for i, h2 in enumerate([["Robots dosyası", "Sitemap haritası"], ["Robots dosyası", "Canonical etiketi"]]):
                p = Path(d) / f"c{i}.html"
                p.write_text(page(h2), encoding="utf-8")
                files.append(str(p))
            me = Path(d) / "me.html"
            me.write_text(page(["Sitemap haritası"]), encoding="utf-8")
            res = self.run_cli(*files, "--self", str(me), "--json")
            self.assertEqual(res.returncode, 0, res.stderr)
            data = json.loads(res.stdout)
            self.assertIn("Gözlendi", data["kanit_duzeyi"])
            self.assertEqual(data["ozet"]["olculen"], 2)
            self.assertTrue(any(g["senin_sayfanda"] is False for g in data["konu_bosluklari"]))

    def test_private_targets_are_refused_by_default(self):
        res = self.run_cli("http://127.0.0.1:9/", "--json")
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout)
        self.assertFalse(data["sayfalar"][0]["ok"])
        self.assertIn("Blocked", data["sayfalar"][0]["neden"])

    def test_requires_at_least_one_url(self):
        self.assertNotEqual(self.run_cli().returncode, 0)


if __name__ == "__main__":
    unittest.main()
