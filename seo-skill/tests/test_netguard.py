"""netguard.py testleri: SSRF savunması, yönlendirme doğrulaması, boyut/sıkıştırma sınırları."""
import email.message
import gzip
import importlib.util
import socket
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "netguard.py"
spec = importlib.util.spec_from_file_location("netguard", SCRIPT)
ng = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ng)

BOMB = gzip.compress(b"\0" * 50_000_000)  # ~50 MB sıfır, birkaç KB sıkıştırılmış


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body=b"", headers=()):
        self.send_response(code)
        for k, v in headers:
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        p = self.path
        if p == "/ok":
            self._send(200, "<html><title>Merhaba ş</title></html>".encode("utf-8"),
                       [("Content-Type", "text/html; charset=utf-8"),
                        ("X-Robots-Tag", "noindex"), ("X-Robots-Tag", "nofollow")])
        elif p == "/r1":
            self._send(301, b"", [("Location", "/ok")])
        elif p == "/chain":
            self._send(302, b"", [("Location", "/r1")])
        elif p == "/loop":
            self._send(302, b"", [("Location", "/loop")])
        elif p == "/missing":
            self._send(404, b"yok", [("Content-Type", "text/plain")])
        elif p == "/big":
            self._send(200, b"x" * 5000, [("Content-Type", "text/plain")])
        elif p == "/bomb":
            self._send(200, BOMB, [("Content-Type", "text/html"), ("Content-Encoding", "gzip")])
        else:
            self._send(404, b"")


class FakeResp:
    def __init__(self, status, headers=None, body=b""):
        self.status = self.code = status
        self.headers = email.message.Message()
        for k, v in (headers or {}).items():
            self.headers[k] = v
        self._body = body

    def read(self, n=-1):
        return self._body if n < 0 else self._body[:n]

    def close(self):
        pass


class FakeOpener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requested = []

    def open(self, req, timeout=None):
        self.requested.append(req.full_url)
        return self.responses.pop(0)


def public_resolver(host, port, type=0):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]


def private_resolver(host, port, type=0):
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.7", port))]


class DestinationTests(unittest.TestCase):
    def test_rejects_unsafe_urls(self):
        cases = {
            "file:///etc/passwd": "Invalid URL",
            "ftp://example.com/": "Invalid URL",
            "//example.com/": "Invalid URL",
            "http://user:pw@example.com/": "Invalid URL",
            "http://localhost/": "Blocked local hostname",
            "http://app.localhost/": "Blocked local hostname",
            "http://127.0.0.1:8080/": "Blocked non-public",
            "http://10.1.2.3/": "Blocked non-public",
            "http://192.168.0.10/": "Blocked non-public",
            "http://169.254.169.254/latest/meta-data/": "Blocked non-public",
            "http://[::1]/": "Blocked non-public",
            "http://[::ffff:127.0.0.1]/": "Blocked non-public",
            "http://0.0.0.0/": "Blocked non-public",
        }
        for url, expected in cases.items():
            with self.subTest(url=url):
                with self.assertRaises(ng.BlockedError) as cm:
                    ng.check_destination(url, resolver=public_resolver)
                self.assertIn(expected, str(cm.exception))

    def test_literal_public_ip_is_accepted(self):
        ng.check_destination("http://93.184.216.34/")

    def test_hostname_resolving_to_private_ip_is_blocked(self):
        with self.assertRaises(ng.BlockedError):
            ng.check_destination("https://intranet.example/", resolver=private_resolver)

    def test_hostname_resolving_to_public_ip_is_accepted(self):
        ng.check_destination("https://www.example.com/", resolver=public_resolver)

    def test_unresolvable_host_without_proxy_is_blocked(self):
        def boom(*a, **k):
            raise socket.gaierror("no dns")
        original = ng._proxied
        ng._proxied = lambda scheme, host: False
        try:
            with self.assertRaises(ng.BlockedError):
                ng.check_destination("https://nope.invalid/", resolver=boom)
        finally:
            ng._proxied = original

    def test_unresolvable_host_behind_proxy_defers_to_proxy(self):
        def boom(*a, **k):
            raise socket.gaierror("no dns")
        original = ng._proxied
        ng._proxied = lambda scheme, host: True
        try:
            ng.check_destination("https://www.example.com/", resolver=boom)  # istisna yok
        finally:
            ng._proxied = original

    def test_allow_private_opt_in(self):
        ng.check_destination("http://localhost:3000/", allow_private=True)
        ng.check_destination("http://127.0.0.1:3000/", allow_private=True)
        with self.assertRaises(ng.BlockedError):  # şema/kimlik bilgisi kontrolü yine geçerli
            ng.check_destination("file:///etc/passwd", allow_private=True)


class RedirectValidationTests(unittest.TestCase):
    def test_redirect_to_private_ip_is_blocked_before_request(self):
        opener = FakeOpener([
            FakeResp(302, {"Location": "http://10.0.0.5/admin"}),
            FakeResp(200, {"Content-Type": "text/html"}, b"secret"),
        ])
        with self.assertRaises(ng.BlockedError):
            ng.fetch("http://www.example.com/", resolver=public_resolver, opener=opener)
        self.assertEqual(opener.requested, ["http://www.example.com/"])  # ikinci istek HİÇ yapılmadı

    def test_redirect_to_metadata_host_via_relative_is_still_checked(self):
        opener = FakeOpener([FakeResp(301, {"Location": "http://169.254.169.254/"})])
        with self.assertRaises(ng.BlockedError):
            ng.fetch("http://www.example.com/", resolver=public_resolver, opener=opener)

    def test_chain_is_recorded(self):
        opener = FakeOpener([
            FakeResp(301, {"Location": "https://www.example.com/a"}),
            FakeResp(302, {"Location": "/b"}),
            FakeResp(200, {"Content-Type": "text/html; charset=utf-8"}, "tamam ş".encode("utf-8")),
        ])
        r = ng.fetch("http://example.com/", resolver=public_resolver, opener=opener)
        self.assertEqual(r.status, 200)
        self.assertEqual(r.url, "https://www.example.com/b")
        self.assertEqual(r.hops, 2)
        self.assertEqual([c[1] for c in r.chain], [301, 302])
        self.assertEqual(r.text, "tamam ş")

    def test_too_many_redirects(self):
        opener = FakeOpener([FakeResp(302, {"Location": f"/{i}"}) for i in range(10)])
        with self.assertRaises(ng.FetchError):
            ng.fetch("http://www.example.com/", resolver=public_resolver, opener=opener, max_redirects=3)


class LocalServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), Handler)
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def get(self, path, **kw):
        return ng.fetch(self.base + path, allow_private=True, timeout=5, **kw)

    def test_default_policy_blocks_the_local_server(self):
        with self.assertRaises(ng.BlockedError):
            ng.fetch(self.base + "/ok", timeout=5)

    def test_basic_fetch_and_multi_value_header(self):
        r = self.get("/ok")
        self.assertEqual(r.status, 200)
        self.assertIn("Merhaba ş", r.text)
        self.assertEqual(r.header("X-Robots-Tag"), "noindex, nofollow")
        self.assertEqual(r.hops, 0)

    def test_redirect_chain_over_http(self):
        r = self.get("/chain")
        self.assertEqual((r.status, r.hops), (200, 2))
        self.assertTrue(r.url.endswith("/ok"))

    def test_redirect_loop(self):
        with self.assertRaises(ng.FetchError):
            self.get("/loop")

    def test_404_is_a_result_not_an_exception(self):
        r = self.get("/missing")
        self.assertEqual(r.status, 404)

    def test_size_cap(self):
        r = self.get("/big", max_bytes=1000)
        self.assertTrue(r.truncated)
        self.assertEqual(len(r.body), 1000)

    def test_gzip_bomb_is_capped(self):
        r = self.get("/bomb", max_bytes=1_000_000)
        self.assertTrue(r.truncated)
        self.assertLessEqual(len(r.body), 1_000_000)


class GunzipTests(unittest.TestCase):
    def test_small_payload_roundtrip(self):
        out, cut = ng.bounded_gunzip(gzip.compress(b"abc" * 10), 1000)
        self.assertEqual((out, cut), (b"abc" * 10, False))

    def test_bomb_is_truncated(self):
        out, cut = ng.bounded_gunzip(BOMB, 10_000)
        self.assertTrue(cut)
        self.assertEqual(len(out), 10_000)

    def test_corrupt_data(self):
        with self.assertRaises(ng.FetchError):
            ng.bounded_gunzip(b"not gzip", 100)


if __name__ == "__main__":
    unittest.main()
