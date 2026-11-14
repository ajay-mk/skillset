"""Build the paper guide: python3 build.py  ->  *.html

Edit the settings, PAGES, and BODY below; leave HEAD, TAIL, and the helpers
alone unless the layout itself has to change.
"""
import os

TITLE = "Author (Year)"  # short site name, shown in the sidebar and <title>
BRAND = "Short<br>paper title"  # sidebar heading, two lines
DOI = "https://doi.org/10.xxxx/xxxxx"
AUDIENCE = "For readers who know X."  # one line, shown in the sidebar footer
WRITTEN = "YYYY-MM-DD"
DEMOS = False  # True when assets/demos.js defines window.DEMOS

PAGES = [  # (file, short nav title, eyebrow, page title, deck)
    ("index.html", "Overview", "Guided reading / Author Year",
     "Full paper title",
     "One or two sentences: what the paper argues, for this reader."),
    ("chapter1.html", "Short title", "Chapter 1", "Chapter title",
     "One sentence on what this chapter explains."),
]

HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="{deck}"><title>{title} | {site}</title><link rel="stylesheet" href="assets/katex/katex.min.css"><link rel="stylesheet" href="assets/style.css"><script defer src="assets/katex/katex.min.js"></script>{demos}<script defer src="assets/guide.js"></script></head>
<body><a class="skip" href="#content">Skip to content</a><div class="scroll-progress" aria-hidden="true"></div><header class="mobile-head"><a href="index.html">{site}</a><button id="menu" aria-controls="sidebar" aria-expanded="false">Chapters</button></header><aside class="sidebar" id="sidebar"><a class="brand" href="index.html"><small>Guided reading</small>{brand}</a><p class="intro">{site}<br>Explained with equations<br>and diagrams.</p><nav aria-label="Chapters">{nav}</nav><footer>{audience}<br>Content follows the paper only.<br><a href="{doi}">Read the paper ↗</a></footer></aside><main class="main" id="content"><article class="article"><div class="eyebrow">{eyebrow}</div><h1 class="title">{title}</h1><p class="deck">{deck}</p><noscript><p class="noscript">Enable JavaScript for typeset equations.</p></noscript>
"""
TAIL = """<div class="pager">{prev}{next}</div><p class="bottom">Guide written {written} · Summarizes the paper only · <a href="{doi}">Paper DOI</a></p></article></main></body></html>
"""


def nav(cur):
    out = []
    for i, (f, short, *_) in enumerate(PAGES):
        num = "•" if i == 0 else f"{i:02d}"
        cur_attr = ' aria-current="page"' if f == cur else ""
        out.append(f'<a href="{f}"{cur_attr}><span class="num">{num}</span><span>{short}</span></a>')
    return "".join(out)


def pager(i):
    prev = f'<a href="{PAGES[i-1][0]}"><span>Previous</span>← {PAGES[i-1][3]}</a>' if i > 0 else "<span></span>"
    nxt = f'<a href="{PAGES[i+1][0]}"><span>Next</span>{PAGES[i+1][3]} →</a>' if i + 1 < len(PAGES) else "<span></span>"
    return prev, nxt


BODY = {}

# Components the stylesheet supports, by example:
#   <p class="lead">Opening paragraph.</p>
#   Inline math <span class="math">E=\langle0|H|0\rangle</span>; display math
#   <div class="equation">...</div>. Raw strings keep backslashes intact.
#   <figure><svg ...>...</svg><figcaption>...</figcaption></figure>
#   <table><thead>...</thead><tbody>...</tbody></table>
#   <div class="callout"><strong>In short.</strong> ...</div>
#   <div class="checkpoint">A question the reader should now be able to answer.</div>
#   <div class="paper">Return to the paper: section, Eqs., pages.</div>
#   <div class="chapter-grid"><a class="chapter-card" href="...">
#     <span class="eyebrow">Chapter 1</span><h3>...</h3><p>...</p></a></div>
#   <div class="interactive" data-demo="name"><input type="range" ...>
#     <output></output><div data-chart></div></div>   (needs DEMOS = True;
#     the demo function in assets/demos.js draws its own SVG into data-chart)

BODY["index.html"] = r"""
<p class="lead">What the paper is about, in two or three sentences.</p>
"""

BODY["chapter1.html"] = r"""
<p class="lead">What this chapter explains.</p>
<div class="paper">Return to the paper: section, Eqs., pages.</div>
"""

here = os.path.dirname(os.path.abspath(__file__))
demos = '<script defer src="assets/demos.js"></script>' if DEMOS else ""
for i, (f, short, eyebrow, title, deck) in enumerate(PAGES):
    prev, nxt = pager(i)
    html = (HEAD.format(deck=deck, title=title, site=TITLE, brand=BRAND, nav=nav(f), doi=DOI,
                        eyebrow=eyebrow, audience=AUDIENCE, demos=demos)
            + BODY[f] + TAIL.format(prev=prev, next=nxt, doi=DOI, written=WRITTEN))
    with open(os.path.join(here, f), "w") as fh:
        fh.write(html)
print("built", len(PAGES), "pages")
