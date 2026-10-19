"""Testler için küçük yerel HTTP sunucusu (yalnızca 127.0.0.1, rastgele port, standart kütüphane).

Kullanım:
    def ok(h): send(h, 200, b"<html>...</html>")
    with LocalServer({"/ok": ok}) as srv:
        url = srv.base + "/ok"
"""
import http.server
import threading


def send(h, status, body=b"", ctype="text/html; charset=utf-8", headers=()):
    """Yanıt yazar. headers: [(ad, değer), ...] — aynı ad birden çok kez verilebilir."""
    h.send_response(status)
    if ctype:
        h.send_header("Content-Type", ctype)
    h.send_header("Content-Length", str(len(body)))
    for k, v in headers:
        h.send_header(k, v)
    h.end_headers()
    if h.command != "HEAD":
        h.wfile.write(body)


def redirect(h, location, status=302):
    send(h, status, b"", ctype=None, headers=[("Location", location)])


class _Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):  # testleri sessiz tut
        pass

    def do_GET(self):
        fn = self.server.routes.get(self.path.split("?", 1)[0])
        if fn is None:
            send(self, 404, b"not found", ctype="text/plain")
        else:
            fn(self)


class LocalServer:
    def __init__(self, routes):
        self.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self.srv.routes = routes
        self.thread = threading.Thread(target=self.srv.serve_forever, daemon=True)

    @property
    def base(self):
        return f"http://127.0.0.1:{self.srv.server_address[1]}"

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.srv.shutdown()
        self.srv.server_close()
        self.thread.join(timeout=5)
