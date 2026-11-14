---
name: pr-wrap-up
description: Take a branch from finished work to a reviewed pull request by running the PR skills in order: pr-preflight, pr-describe, and after review pr-comments, with an optional review-helper page. Use when the user says "wrap up this PR", "get this ready for review", "open the PR", "handle the PR", or asks for several of these steps at once.
---

# PR wrap-up

Find where the PR stands, run the next step, and stop at each point where the
user must approve something. The steps are their own skills; follow each
one's instructions rather than restating them here.

## 1. Find the stage

`gh pr view --json number,state,isDraft,reviewDecision,url` on the current
branch, plus `git status` for uncommitted work.

| State | Next |
|---|---|
| Uncommitted changes | Say so and stop; the user decides what to commit. |
| No PR | pr-preflight, then pr-describe to create it. |
| PR open, no review yet | pr-preflight, then pr-describe to refresh the text if commits landed since it was written. |
| PR has review comments | pr-comments, then pr-describe refresh if fixes changed what the PR does. |
| Merged or closed | Report and stop. |

If the user asked for one specific step, run only that.

## 2. Run the steps

- **pr-preflight** first. A failing check stops the flow until the user fixes
  it or says to proceed anyway.
- **pr-describe** next: show the draft, create or edit the PR only on approval.
  It offers a diagram when the change has a flow or structure worth drawing.
- **pr-comments** when there is feedback: triage, then fixes and replies only
  on approval.
- **unslop**, when installed, runs inside pr-describe and pr-comments on the
  PR text and replies before the user sees them.
- **review-helper** is optional. Offer it in one line when the change is large
  or spans many files, or when the user wants to walk through it; skip it
  otherwise. When pr-comments ran, pass its triage as the page's comments.

## 3. Report

End with the PR URL, what was done in this run (checks, text posted, commits,
replies), and what waits on the user or a reviewer.
