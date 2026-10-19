#!/usr/bin/env python3
"""
Güvenli HTTP getirme yardımcıları (yalnızca Python standart kütüphanesi).

Bu modül tek başına çalıştırılmaz; seo_audit.py, competitor_probe.py, seo_url_audit.py ve
seo_sitemap_audit.py tarafından kullanılır.

Ne sağlar:
  - Yalnızca mutlak http/https URL kabul eder; URL içinde kullanıcı/parola kabul etmez.
  - SSRF savunması (derinlemesine savunma): localhost ve genel olmayan IP hedeflerini (özel ağ,
    loopback, link-local, bulut meta-veri adresi vb.) reddeder. Bu, ağ seviyesindeki çıkış
    (egress) denetiminin yerine geçmez.
  - Yönlendirmeleri OTOMATİK izlemez: her adımı kendisi izler ve HER adımın hedefini yeniden
    doğrular (genel bir adresten özel bir adrese yönlendirme engellenir). Yönlendirme zincirini
    kaydeder (SEO için de değerli: zincir/döngü tespiti).
  - Boyut sınırı (varsayılan 3 MB), zaman aşımı ve yönlendirme sayısı sınırı vardır.
  - Sıkıştırılmış içerik için sınırlı (bomba korumalı) açma yardımcısı sunar.

Yerel geliştirme sunucusunu (localhost) bilerek denetlemek için allow_private=True verilir
(betiklerde --allow-private bayrağı). Varsayılan KAPALIDIR.

Bilinen sınır: ana makine adı bizim doğrulamamızla bağlantı anı arasında değişebilir (DNS rebinding).
Bu yüzden güvenilmeyen girdilerle kullanıyorsanız ağ seviyesinde de kısıtlayın.
"""
from __future__ import annotations

import ipaddress
import socket
import sys
import urllib.error
import urllib.request
import zlib
from urllib.parse import urljoin, urlparse

UA = "SEO-Skill/1.0 (diagnostic; respectful crawler)"
DEFAULT_MAX_BYTES = 3_000_000
DEFAULT_MAX_REDIRECTS = 5
REDIRECT_CODES = (301, 302, 303, 307, 308)


class BlockedError(Exception):
    """URL güvenlik politikasıyla reddedildi (ağ isteği yapılmadı)."""


class FetchError(Exception):
    """Ağ/protokol hatası (zaman aşımı, bağlantı hatası, çok fazla yönlendirme vb.)."""


def setup_stdio():
    """Windows konsol/pipe kodlaması (cp1254 vb.) yüzünden Türkçe/sembol yazdırırken çökmesin."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # eski Python veya yeniden yapılandırılamayan akış
            pass


# ---------------------------------------------------------------- hedef doğrulama
def _literal_ip(host):
    try:
        return ipaddress.ip_address(host.strip("[]").split("%", 1)[0])
    except ValueError:
        return None


def _is_public(ip):
    if ip.version == 6 and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return ip.is_global


def _is_localish(host):
    """allow_private modunda proxy'yi atlamak için: localhost, özel/loopback IP veya tek etiketli ad."""
    h = host.lower().rstrip(".")
    if h == "localhost" or h.endswith(".localhost") or "." not in h:
        return True
    ip = _literal_ip(h)
    return ip is not None and not _is_public(ip)


def _proxied(scheme, host):
    try:
        return scheme in urllib.request.getproxies() and not urllib.request.proxy_bypass(host)
    except Exception:
        return False


def check_destination(url, allow_private=False, resolver=None):
    """URL güvenli değilse BlockedError fırlatır. İstek YAPMAZ (yalnızca DNS çözümlemesi yapabilir)."""
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        raise BlockedError("Invalid URL (only absolute http/https URLs accepted)")
    if p.username or p.password:
        raise BlockedError("Invalid URL (credentials in URL are not accepted)")
    if allow_private:
        return
    host = p.hostname.lower().rstrip(".")
    if host == "localhost" or host.endswith(".localhost"):
        raise BlockedError("Blocked local hostname")
    ip = _literal_ip(host)
    if ip is not None:
        if not _is_public(ip):
            raise BlockedError("Blocked non-public IP destination")
        return
    port = p.port or (443 if p.scheme == "https" else 80)
    try:
        infos = (resolver or socket.getaddrinfo)(host, port, type=socket.SOCK_STREAM)
    except (socket.gaierror, OSError) as e:
        if _proxied(p.scheme, host):
            return  # DNS'i proxy çözer; yerel çözümleme anlamlı değil, proxy'nin kendi politikası geçerli
        raise BlockedError(f"URL validation failed: {type(e).__name__}") from None
    addresses = {item[4][0] for item in infos}
    if not addresses:
        raise BlockedError("URL validation failed: hostname did not resolve")
    for address in addresses:
        try:
            ip = ipaddress.ip_address(address.split("%", 1)[0])
        except ValueError:
            raise BlockedError("URL validation failed: unparsable address") from None
        if not _is_public(ip):
            raise BlockedError("Blocked non-public IP destination")


# ---------------------------------------------------------------- getirme
class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Yönlendirmeyi urllib'in izlemesini engeller; 3xx, HTTPError olarak döner ve biz izleriz."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None


def make_opener(proxies=None):
    """proxies=None → ortam/sistem proxy ayarları; proxies={} → proxy kullanma (doğrudan bağlan)."""
    handlers = [_NoRedirect()]
    if proxies is not None:
        handlers.insert(0, urllib.request.ProxyHandler(proxies))
    return urllib.request.build_opener(*handlers)


def bounded_gunzip(data, limit):
    """gzip verisini en çok `limit` bayta kadar açar. (çıktı, kesildi_mi) döner. Sıkıştırma bombası korumalı."""
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        out = d.decompress(data, limit + 1)
    except zlib.error as e:
        raise FetchError(f"gzip error: {e}") from None
    truncated = len(out) > limit or bool(d.unconsumed_tail)
    return out[:limit], truncated


class Result:
    """fetch() sonucu."""

    def __init__(self, status, url, headers, body, chain, truncated):
        self.status = status          # son yanıtın HTTP durum kodu
        self.url = url                # son (yönlendirmeler sonrası) URL
        self.headers = headers        # http.client.HTTPMessage
        self.body = body              # bytes
        self.chain = chain            # [(url, durum_kodu), ...] yalnızca yönlendirme adımları
        self.truncated = truncated    # boyut sınırında kesildi mi

    @property
    def hops(self):
        return len(self.chain)

    def header(self, name):
        """Aynı başlık birden çok kez gelebilir (ör. X-Robots-Tag); hepsini birleştirir."""
        values = self.headers.get_all(name) or []
        return ", ".join(v.strip() for v in values)

    @property
    def text(self):
        charset = None
        try:
            charset = self.headers.get_content_charset()
        except Exception:
            pass
        try:
            return self.body.decode(charset or "utf-8", "replace")
        except LookupError:
            return self.body.decode("utf-8", "replace")


def fetch(url, *, timeout=15, max_bytes=DEFAULT_MAX_BYTES, max_redirects=DEFAULT_MAX_REDIRECTS,
          allow_private=False, headers=None, resolver=None, opener=None):
    """GET isteği; yönlendirmeleri güvenli biçimde izler. 4xx/5xx istisna DEĞİL, Result olarak döner.

    Raises: BlockedError (politika), FetchError (ağ hatası / çok fazla yönlendirme / döngü).
    """
    chain, seen, cur = [], set(), url
    for _ in range(max_redirects + 1):
        check_destination(cur, allow_private, resolver)
        if cur in seen:
            raise FetchError("Redirect loop detected")
        seen.add(cur)
        hdrs = {
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "identity",
        }
        if headers:
            hdrs.update(headers)
        req = urllib.request.Request(cur, headers=hdrs)
        op = opener
        if op is None:
            host = urlparse(cur).hostname or ""
            op = make_opener({}) if (allow_private and _is_localish(host)) else make_opener()
        try:
            resp = op.open(req, timeout=timeout)
        except urllib.error.HTTPError as e:   # 3xx (yönlendirme izlenmediği için), 4xx, 5xx
            resp = e
        except (urllib.error.URLError, socket.timeout, TimeoutError, OSError, ValueError) as e:
            raise FetchError(f"{type(e).__name__}: {e}") from None
        try:
            status = getattr(resp, "status", None) or resp.code
            resp_headers = resp.headers
            location = resp_headers.get("Location")
            if status in REDIRECT_CODES and location:
                chain.append((cur, status))
                cur = urljoin(cur, location.strip())
                continue
            raw = resp.read(max_bytes + 1)
        except (OSError, ValueError) as e:
            raise FetchError(f"{type(e).__name__}: {e}") from None
        finally:
            try:
                resp.close()
            except Exception:
                pass
        truncated = len(raw) > max_bytes
        raw = raw[:max_bytes]
        encoding = (resp_headers.get("Content-Encoding") or "").lower()
        if encoding in ("gzip", "x-gzip"):
            raw, cut = bounded_gunzip(raw, max_bytes)
            truncated = truncated or cut
        elif encoding == "deflate":
            try:
                raw = zlib.decompressobj().decompress(raw, max_bytes + 1)
                truncated = truncated or len(raw) > max_bytes
                raw = raw[:max_bytes]
            except zlib.error as e:
                raise FetchError(f"deflate error: {e}") from None
        return Result(status, cur, resp_headers, raw, chain, truncated)
    raise FetchError(f"Too many redirects (> {max_redirects})")


if __name__ == "__main__":
    sys.exit("netguard.py bir kütüphane modülüdür; doğrudan çalıştırılmaz.")
