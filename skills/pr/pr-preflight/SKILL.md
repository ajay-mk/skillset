---
name: pr-preflight
description: Check a branch is ready to open (or update) as a pull request: commit messages follow the repo's rules, the branch is current with its base, dependency pins match the PRs they reference, no stray or generated files, and CI status. Read-only report. Use when the user asks "is this ready for a PR", "preflight", "check before I open the PR", or as the first step of pr-wrap-up.
---

# PR preflight

Report whether a branch is ready for review. Change nothing: no rebases,
amends, pushes, or deletions. Each finding names what to fix; the user decides.

## 1. Resolve the comparison

- Base: the open PR's base (`gh pr view --json baseRefName,url`) if one
  exists, else the repo's default branch (`gh repo view --json
  defaultBranchRef`). Ask if the user's words suggest another base.
- `git fetch` the base's remote first, so "current with base" is not judged
  against a stale ref.

## 2. Checks

Mark each **pass**, **fail**, or **unknown** (could not check, say why).

1. **Up to date with base.** `git rev-list --count HEAD..origin/<base>`.
   Behind is a fail only when the base changed files this branch touches or
   the repo requires linear history; otherwise note the count.
2. **Commit messages.** List `git log --format='%h %s' origin/<base>..HEAD`.
   Check them against the repo's documented conventions (CONTRIBUTING,
   AGENTS.md, CLAUDE.md, recent merged history) and the user's own
   instructions. Flag `fixup!`/`wip`/`tmp` commits, messages that describe
   something the commit's diff does not do, and unrelated work mixed into
   one commit.
3. **Stray files.** In `git diff --stat origin/<base>...HEAD`, flag build
   outputs, editor or OS files, large binaries, logs, secrets or tokens,
   leftover debug prints, and files unrelated to the change.
4. **Dependency pins.** If the diff changes a pinned version (CMake
   `*_TAG`/version files, submodules, lock files, requirements), check the
   pinned commit exists upstream (`gh api repos/<o>/<r>/commits/<sha>`), and
   if the PR text or commits cite a PR for it, that the commit is on that PR's
   branch or already merged. A pin bump should sit in its own commit, paired
   with the code that needs it.
5. **CI.** With a PR: `gh pr checks`. Without one: say CI has not run, and
   name the repo's local build/test command from its docs. Do not run long
   builds or test suites unless the user asks.

## 3. Report

A short table: check, status, evidence (command and the line that decided
it), fix. Then one line: ready, or the blocking items. Do not report "ready"
while any check is fail.
