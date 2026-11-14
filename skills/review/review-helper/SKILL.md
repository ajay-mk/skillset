---
name: review-helper
description: Build or refresh a standalone HTML page that explains a diff, branch, or PR file by file, with annotated diffs, review-comment traceability, and checks. Use when the user wants a page to walk through changes ("make a review page", "walk me through this diff"); not for an ordinary text review.
---

# Review Helper

Make a source-grounded page that helps the user work through a change: what it
does overall, what changed in each file and why, and where review feedback was
addressed. It explains and navigates; it does not judge the change (that is a
code review).

The bundled script does the mechanical work so it is exact and identical every
time; your job is the understanding. The workflow:

1. `scripts/review_helper.py capture` records the snapshot as JSON.
2. You read the change and write the narrative fields into that JSON.
3. `scripts/review_helper.py build` checks the JSON and embeds it into
   `assets/template.html`, producing one standalone file.

## 1. Capture the snapshot

Resolve the comparison the user means and record both endpoints. A working-copy
review normally compares `HEAD` (or the branch's merge-base) with staged and
unstaged changes together; a branch review compares its merge-base with the
branch head.

```sh
python3 scripts/review_helper.py capture --repo <repo> --base <base> [--head <head>] \
    [--untracked <path> ...] -o <snapshot>.json
```

Omit `--head` to compare against the working tree. Untracked files are included
only when named, because a blind scan of large build trees swamps the page;
list the ones that belong to the change and record the rest under `excluded`.
The script records paths, renames, status, line counts, exact patches (as
base64, so downloads are byte-exact), both endpoint sources, and SHA-256
fingerprints. It recaptures if the tree changes mid-capture.

Keep the snapshot and page outside the source checkout. Save them where the
user's instructions say; otherwise ask. Follow any conventions of the
destination folder (such as an index README) and use a dated name like
`YYYY-MM-DD-project-change.html`. Reading a diff does not authorize editing
code, running builds, committing, pushing, or posting replies.

## 2. Write the narrative

Read the repository's instructions, the patches, and enough surrounding code to
explain behavior. Do not infer rationale from filenames, commit subjects, or
earlier summaries alone; when the reason is not visible in code, the
conversation, or a review thread, say it is uncertain. Fill these fields in the
JSON:

- `title`, `subtitle`, and `pr_url` when there is one.
- `groups`: the review order, shown as numbered sidebar sections. Name each
  by what its files do for this change, in 2–4 plain words ("The new cost
  symbol", "Cost model", "cost_analysis tool", "Tests", "Example inputs"),
  not by abstract role ("Core contract", "Utility (caller)").
- Per file: `title` (under the file name in the sidebar, so a short phrase of
  about 8 words, not a sentence), `group`, `before` (the previous behavior or contract),
  `after` (the resulting behavior), `why` (the supported motivation and the
  question a reviewer should check), and `annotations`: a list of
  `{header, note}` where `header` is the start of a hunk's `@@` line. Give
  substantive behavior changes the most attention; describe mechanical changes
  in a sentence. Do not call metadata-only fixture changes regenerated results.
- `summary`, which becomes the landing page:
  - `overview`: 3–5 bullets (a list of strings) on what the change does as a
    whole, one idea each, readable without opening any file.
  - `changes`: the main behavior changes, each `{text, file, line?, side?}`.
  - `focus`: where the reviewer should look hardest (risky hunks, public API or
    contract changes, numerical changes), same shape.

  Every item links to a file, so the summary stays a map into the evidence
  rather than a separate story.
- `notes`: scope caveats worth seeing on the summary.

For domain changes, a short structural summary (tensor block shapes, schema
fields, dependency versions) in `after` or an annotation often helps; derive it
from the snapshot.

## 3. Connect review comments

When PR comments or conversation feedback are in scope, add each to
`comments`: `{id, source ("pr" or "conversation"), author, url, location,
body, concern, disposition, remote, explanation, evidence: [{file, line,
side?, label?}]}`.

- For PR comments, use the pr-comments skill: its `fetch_comments.py` gives
  the original comments and thread state, and its triage can be written
  directly in this `comments` shape. If remote access fails, label the
  evidence cached or incomplete.
- `disposition` is the local status (implemented, declined, pending); `remote`
  is the thread state (resolved, open, unknown). Keep them separate: an
  implemented fix is not an accepted or resolved comment, and a state you
  could not fetch is `unknown`.
- Link evidence to verified current lines. Use commit hashes only when checked
  against git. For an intermediate design that never reached the baseline,
  explain it rather than inventing a deleted hunk. If a target is missing or
  ambiguous, say so rather than guessing a line.

## 4. Record checks

Add test or build evidence to `checks`: `{title, status, command, date,
revision, limits, log}`. Show only results backed by actual logs, with the
revision they ran against; label results from an older revision, and keep
"not run", "failed", and "passed" distinct. Building the page does not
authorize expensive project tests.

## 5. Build and verify

```sh
python3 scripts/review_helper.py build <snapshot>.json -o <page>.html
```

The build refuses to run while any file lacks its narrative, a group is
undeclared, or a summary, comment, or evidence link points at a missing file or
line. Fix the JSON and rebuild.

Then open the page (serve it locally if the browser blocks `file://`) and
check: the summary links land on the right lines, file navigation and search
work, a deep link outside a hunk falls back to the source view, patch
downloads work, and the layout holds at phone width. If browser checks are not
possible, say so. RetuTo publish rather than keep a local file, use the host's page-hosting tool
only when the user asks; repository contents leave the machine only with that
permission. The page's "Comment" buttons call `window.claude.use('comments')`,
so they appear only when the page is published as a claude.ai artifact with
the `comments` capability (composer only, e.g. `{comments: {composer_only:
true}}`); on other hosts the page works without them. Each button anchors to an element id:
`file-<path>`, `file-<path>-hunk-<n>` (non-alphanumeric runs in the path
replaced by `-`), `summary-<overview|changes|focus>-<n>`, `comment-<id>`, or
`check-<n>`. Answer comments with the host's comment tool. After a refresh,
republish to the same page so the link and its threads stay.

ist rather than as a pin. Republish to the same file path after a refresh
so the link and its threads stay.

## Refreshing

When asked to update a page, recapture into a new snapshot, carry over the
narrative for files whose `sha256` did not change, and rewrite it for files
that did. After commits, relabel the comparison instead of still calling it an
uncommitted diff. When the user wants the old page kept, write the new one
beside it.

## Extending the template

`assets/template.html` renders any snapshot and must stay generic. Put
change-specific content in the JSON, never in the renderer. If a change truly
needs a custom widget, copy the template next to the page and extend the copy;
see [page-design.md](references/page-design.md) for the design rules the
template follows.
