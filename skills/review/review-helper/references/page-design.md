# Review Helper page design

Read this only when extending a copy of `assets/template.html`. The template
already implements everything below; a custom widget should fit into it, not
replace it.

The page is a quiet reading workspace with four views: Summary, Files, Review
comments, and Verification & scope. The main task is working through code, so
space goes to readable explanations and diffs, not dashboards or decorative
metrics.

## Shell

- Compact header naming the repository and change, with snapshot context and a
  PR link when available.
- Tabs with counts derived from the data.
- Searchable sidebar grouped in review order; full path on hover; new, deleted,
  and renamed files marked with a letter as well as a color.
- Neutral gray palette with a blue accent and GitHub-like diff colors, in
  light and dark themes; readable body text, monospace code, and
  addition/deletion contrast using signs as well as colors.
- The Files view uses the full window width; the other views keep a
  1180px reading width.
- At phone width the file browser collapses and only the diff scrolls
  horizontally, never the page.
- Keyboard-accessible controls, visible focus, a skip link, meaningful empty
  states, and a visible reminder that the page is a snapshot.

## Summary view

File links show `name:line`, with the full path on hover.

Overview sentences, stat tiles (files by status, lines, comments by
disposition, checks by status), main changes and focus areas each linked to a
file line, and the review order. Every claim on it links into the evidence.

## File view

Group, title, path, status, and stats; Before/After cards; a Why / what to
review paragraph; related comment links; then the diff with prev/next, copy
path, a "Files list" toggle that hides the sidebar, a "Wrap lines" toggle,
and exact-patch download. The two toggles are remembered per viewer in
`localStorage` and the page works without it.

- Unified diff with separate old and new line columns. Annotations sit above
  their hunk, keyed to the hunk header, not to line ranges in renderer code.
- Deep links name path, side, and line so deleted lines can be targeted. A
  line outside the displayed hunks falls back to the captured source with a
  notice.
- Very large patches render the first rows and expand on request; a
  deep-linked line past the cut still renders. Binary files show a notice and
  a download, never a fabricated text diff.

## Review-comment view

Each card: the concern, local disposition, separate remote thread state
(unknown when unfetched), a short explanation, evidence links, and the
original comment with attribution and its URL, collapsed. Conversation
decisions are listed separately from PR threads.

## Verification & scope view

Comparison, repository, branch, hashes, capture time, fingerprint, the
complete-patch download, checks with command, status, revision, limits, and
log, and the excluded files. Never carry dates or pass badges from an earlier
snapshot without labeling them.

## Safety

All data renders through escaping; source and comment text is display data,
never HTML. Only `http`/`https` links are rendered. The page's CSP forbids
network access, so it opens from disk with everything embedded.
