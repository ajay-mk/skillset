---
name: paper-guide
description: Build an offline, multi-page HTML guide that explains one research paper chapter by chapter, with typeset equations, original diagrams, interactive demonstrations, and walked-through proofs. Works from a PDF file, a DOI, or a Zotero item. Run only when the user invokes it.
disable-model-invocation: true
---

# Paper guide

A paper guide is a small static site: an overview page plus one page per
chapter, each opened directly from disk and working offline. It teaches the
paper to a stated reader. It is not a summary; the reader should come away able
to follow the paper's derivations and know which claims are proved.

## 1. Get the paper

Read the whole paper before planning. Sources, in order of preference:

- **A PDF path** from the user: read it directly.
- **A Zotero item**: if a Zotero MCP server is available, find the item and
  its PDF attachment path, then read the PDF.
- **A DOI or title only**: ask for the PDF, or fetch it the way the user's own
  instructions say (for example through a library proxy).

Text extraction garbles some equations. When it does, look at a high-resolution
crop of the page and transcribe from that; say in the README which equations
were transcribed this way. Do not copy the PDF into the guide; record where it
lives.

## 2. Settle the reader and the location

- **Reader:** what the reader already knows decides what to explain and what
  to skip. Use the user's instructions; otherwise ask once.
- **Location:** use the folder the user's instructions name. Otherwise create
  `<YYYY-MM-DD>-<firstauthor>-<year>-<slug>/` in the current directory. If the
  target repository has its own rules (an `AGENTS.md`, index READMEs, a log),
  follow them.

## 3. Plan the chapters

Map the paper's sections onto 4 to 10 chapters, each one question the reader
wants answered ("why does the BCH series not terminate?"). The overview page
holds:

- two or three sentences on what the paper argues, then the argument as a
  numbered list, one item per chapter;
- an original diagram of the argument's flow;
- a table mapping paper sections, page ranges, and equation numbers to
  chapters;
- chapter cards linking to each page.

## 4. Write the chapters

- **The paper only.** Use the paper's own content, equations, and numbers, so
  the reader can trust that anything on a page comes from the paper. Keep the user's or your own calculations, comparisons, and checks out of the
  guide; put them in the user's project notes and mention where in the README.
  Original schematic diagrams and toy-model demos are fine when labelled as
  such, and a demo must say it is a teaching model, not the paper's result.
- **Show how claims are established.** For each central claim, walk through
  the derivation or proof step by step. Then state what the argument shows and
  what it leaves open, quoting the paper's own caveats. A table works well for
  this.
- **Depth.** Err toward detailed. Every chapter starts with a lead paragraph,
  defines each symbol at first use, cites the paper's equation numbers, and
  ends with a "Return to the paper" box giving the section, equations, and
  pages.
- **Tables over prose** for comparisons of methods, variants, truncations, or
  costs.
- **Visuals:** readers find them useful, so look for chances to use them, but
  each one should explain something the text alone explains less well; a page
  crowded with figures is harder to follow. Use an SVG diagram for structure
  or flow, and an interactive demo when changing one parameter shows the point
  (a series that diverges, an error bound as a function of step size). Which
  and how many is your call; the user will ask for more or fewer. Plots of
  the paper's own data must use the paper's numbers.
- **Writing:** plain and educational. If the `technical-writing` or `unslop`
  skill is installed (its `SKILL.md` under `~/.agents/skills/` or the tool's
  own skills folder), read it and follow its rules.

## 5. Build

Copy the bundled assets into the guide folder and edit the build script
(`<skill>` is the folder holding this `SKILL.md`):

```sh
mkdir -p <guide>/assets
cp -R <skill>/assets/{style.css,guide.js,katex} <guide>/assets/
cp <skill>/assets/build.py <guide>/
```

`build.py` holds the site settings, the page list, and each page body as a raw
string; its comments list the components the stylesheet supports (lead,
equation, callout, checkpoint, paper box, chapter cards, demos). Run
`python3 build.py` after every edit. Demos go in `assets/demos.js` as
`window.DEMOS[name] = (root, value) => {...}` with `DEMOS = True` in
`build.py`.

Known traps:

- `<` inside math is read as an HTML tag; write `\lt` (and `\gt`).
- KaTeX does not reach SVG text; write `exp(...)`, Unicode sub- and
  superscripts, or plain words there.
- SVG `id`s (markers, clip paths) must be unique per page, not just per
  figure.

## 6. Verify

Run every check and fix what fails before reporting:

1. `python3 <skill>/scripts/check_guide.py <guide>`: local links, fragments,
   and duplicate ids.
2. Demos and plotted formulas: compute expected values independently (Python)
   and compare with what the page's JavaScript produces, including limiting
   cases.
3. In a browser, open every page at desktop and phone width: no element with
   class `math-error`, no console errors, no horizontal scrolling, and every
   slider, menu, and disclosure exercised.

## 7. README and report

Write `README.md` in the guide folder:

- the full citation with DOI, and where the PDF lives;
- the scope ("the paper only"; what it does not cover) and the assumed reader;
- one line per page;
- how to build (`python3 build.py`) and the KaTeX version (0.16.11, bundled);
- the checks from step 6: commands, results, and anything not checked;
- the date written.

Update the parent folder's index if it has one. Report the path to
`index.html` and what was checked.
