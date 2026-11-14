#!/usr/bin/env python3
"""Check a built paper guide: python3 check_guide.py <guide-dir>

Reports duplicate ids, and local links, fragments, scripts, and stylesheets
that do not resolve. Exits 1 on any problem. Equation rendering is checked in
a browser, not here.
"""
import html.parser
import os
import sys
from urllib.parse import urldefrag, urlparse


class Page(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.dups, self.refs = set(), [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            if a["id"] in self.ids:
                self.dups.append(a["id"])
            self.ids.add(a["id"])
        for key in ("href", "src"):
            if key in a and a[key]:
                self.refs.append(a[key])


def main(root):
    pages = {}
    for f in sorted(os.listdir(root)):
        if f.endswith(".html"):
            p = Page()
            with open(os.path.join(root, f), encoding="utf-8") as fh:
                p.feed(fh.read())
            pages[f] = p
    if not pages:
        sys.exit(f"no .html files in {root}")
    problems, links = [], 0
    for f, p in pages.items():
        problems += [f"{f}: duplicate id '{i}'" for i in p.dups]
        for ref in p.refs:
            if urlparse(ref).scheme or ref.startswith("//"):
                continue  # external
            links += 1
            path, frag = urldefrag(ref)
            target = f if not path else os.path.normpath(os.path.join(os.path.dirname(f), path))
            if not os.path.exists(os.path.join(root, target)):
                problems.append(f"{f}: missing file '{ref}'")
            elif frag and target in pages and frag not in pages[target].ids:
                problems.append(f"{f}: missing fragment '{ref}'")
    for line in problems:
        print(line)
    print(f"{len(pages)} pages, {links} local references, {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
