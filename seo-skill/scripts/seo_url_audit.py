#!/usr/bin/env python3
"""Conservative SEO URL audit helper using only Python's standard library.

Reads URLs from a text file, fetches them with bounded concurrency (default 1),
and reports basic HTTP/HTML signals. It is not a replacement for a browser renderer,
Search Console, a production crawler, or professional judgment.

(Taken from SEO Apex; hardened while merging. Behaviour and existing CSV columns are
backwards compatible, new columns are appended at the end:)
  * Network layer is netguard.py: every redirect hop goes through the SSRF check (the previous version
    validated only the first URL while urllib followed redirects automatically). The redirect chain is recorded.
  * Auditing a local dev server on purpose needs --allow-private (default: refused).
  * Several X-Robots-Tag headers are joined; noindex and canonical_status columns were added.
  * internal_links_count now really counts internal links (it used to count every <a href>).
  * h1_count is taken from the parser, so '<h1' inside a script/comment is not counted.
"""
from __future__ import annotations
import argparse, csv, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import netguard  # noqa: E402

UA = netguard.UA  # backwards compatibility

FIELDS = ["url", "status", "final_url", "content_type", "title", "title_chars", "description",
          "h1_count", "h1", "canonical", "canonical_count", "robots", "x_robots_tag",
          "hreflang_count", "internal_links_count", "html_bytes", "error",
          "redirect_hops", "redirect_chain", "noindex", "canonical_status", "external_links_count"]


class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title_parts, self.h1_parts = [], []
        self.in_title = self.in_h1 = False
        self.h1_count = 0
        self.meta = {}
        self.canonicals = []
        self.robots = []
        self.hreflang = []
        self.links = 0
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        t = tag.lower()
        if t == "title": self.in_title = True
        if t == "h1":
            self.in_h1 = True
            self.h1_count += 1
        if t == "meta":
            name = a.get("name", "").lower()
            if name in ("description", "robots", "googlebot", "bingbot"):
                self.meta[name] = a.get("content", "")
            if name == "robots": self.robots.append(a.get("content", ""))
        if t == "link":
            rel = set(a.get("rel", "").lower().split())
            if "canonical" in rel: self.canonicals.append(a.get("href", ""))
            if "alternate" in rel and a.get("hreflang"):
                self.hreflang.append((a.get("hreflang"), a.get("href", "")))
        if t == "a" and a.get("href"):
            self.links += 1
            self.hrefs.append(a.get("href", ""))

    def handle_endtag(self, tag):
        t = tag.lower()
        if t == "title": self.in_title = False
        if t == "h1": self.in_h1 = False

    def handle_data(self, data):
        if self.in_title: self.title_parts.append(data.strip())
        if self.in_h1: self.h1_parts.append(data.strip())


def _norm(u):
    p = urlparse(u.split("#", 1)[0])
    return (f"{p.scheme.lower()}://{(p.netloc or '').lower()}{p.path.rstrip('/') or '/'}"
            + (f"?{p.query}" if p.query else ""))


def split_links(hrefs, base_url):
    """(internal, external) link counts. Fragments (#), mailto:, tel:, javascript: are not counted."""
    host = (urlparse(base_url).hostname or "").lower()
    internal = external = 0
    for h in hrefs:
        h = h.strip()
        if not h or h.startswith("#") or re.match(r"^(mailto|tel|javascript|sms|data):", h, re.I):
            continue
        p = urlparse(h)
        if not p.netloc or (p.hostname or "").lower() == host:
            internal += 1
        else:
            external += 1
    return internal, external


def audit(url, timeout, delay, allow_private=False, max_redirects=5):
    result = {k: "" for k in FIELDS}
    result.update(url=url, title_chars=0, h1_count=0, canonical_count=0, hreflang_count=0)
    try:
        netguard.check_destination(url, allow_private)
    except netguard.BlockedError as e:
        # Old messages are kept: "Invalid URL ...", "Blocked local hostname", "Blocked non-public IP destination"
        result["error"] = str(e)
        return result
    try:
        if delay: time.sleep(delay)
        res = netguard.fetch(url, timeout=timeout, max_bytes=3_000_000, max_redirects=max_redirects,
                             allow_private=allow_private, headers={"Accept": "text/html,application/xhtml+xml"})
    except netguard.BlockedError as e:   # unsafe destination somewhere in the redirect chain
        result["error"] = f"{e} (during redirect)"
        return result
    except netguard.FetchError as e:
        result["error"] = str(e)
        return result
    content_type = res.headers.get("Content-Type", "")
    x_robots = res.header("X-Robots-Tag")
    result.update(status=res.status, final_url=res.url, content_type=content_type, x_robots_tag=x_robots,
                  html_bytes=len(res.body), redirect_hops=res.hops,
                  redirect_chain=" > ".join(f"{u} [{c}]" for u, c in res.chain))
    errors = []
    if res.truncated:
        errors.append("Response truncated at 3 MB safety limit")
    if res.status >= 400:
        errors.append(f"HTTPError: {res.status}")
    if "html" in content_type.lower():
        p = Parser()
        p.feed(res.text)
        title = " ".join(" ".join(p.title_parts).split())
        h1 = " ".join(" ".join(p.h1_parts).split())
        internal, external = split_links(p.hrefs, res.url)
        robots_all = "; ".join(p.robots)
        if not p.canonicals:
            canonical_status = "missing"
        elif len(p.canonicals) > 1:
            canonical_status = "multiple"
        else:
            canonical_status = "self" if _norm(p.canonicals[0]) == _norm(res.url) else "different"
        result.update(title=title, title_chars=len(title),
                      description=p.meta.get("description", ""),
                      h1_count=p.h1_count, h1=h1, canonical="; ".join(p.canonicals),
                      canonical_count=len(p.canonicals), robots=robots_all,
                      hreflang_count=len(p.hreflang),
                      internal_links_count=internal, external_links_count=external,
                      noindex="yes" if "noindex" in (robots_all + " " + x_robots).lower() else "no",
                      canonical_status=canonical_status)
    elif "noindex" in x_robots.lower():
        result["noindex"] = "yes"
    result["error"] = "; ".join(errors)
    return result


def main():
    netguard.setup_stdio()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="UTF-8 text file containing one URL per line")
    ap.add_argument("-o", "--output", default="seo-url-audit.csv")
    ap.add_argument("--timeout", type=float, default=10)
    ap.add_argument("--delay", type=float, default=1.0, help="delay before each request per worker")
    ap.add_argument("--workers", type=int, default=1, help="default 1; use higher values only with permission")
    ap.add_argument("--max-redirects", type=int, default=5)
    ap.add_argument("--allow-private", action="store_true",
                    help="allow localhost/private-network targets (only for YOUR OWN dev server); default: refused")
    args = ap.parse_args()
    if args.timeout <= 0 or args.delay < 0 or not 1 <= args.workers <= 4:
        ap.error("timeout must be >0, delay >=0, and workers must be between 1 and 4")
    with open(args.input, encoding="utf-8-sig") as f:
        urls = list(dict.fromkeys(x.strip() for x in f if x.strip() and not x.lstrip().startswith("#")))
    if not urls:
        ap.error("input file contains no URLs")
    order = {u: i for i, u in enumerate(urls)}
    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(audit, u, args.timeout, args.delay, args.allow_private, args.max_redirects): u
                   for u in urls}
        for future in as_completed(futures):
            rows.append(future.result())
            print(f"[{len(rows)}/{len(urls)}] {futures[future]}", file=sys.stderr)
    rows.sort(key=lambda r: order[r["url"]])
    with open(args.output, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} URL rows to {args.output}")
    bad = [r for r in rows if r["error"]]
    if bad:
        print(f"{len(bad)} row(s) have an error/limit note (see 'error' column).", file=sys.stderr)


if __name__ == "__main__":
    main()
