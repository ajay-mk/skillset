---
name: full-review
description: Read-only deep review of a change in parallel passes (code, tests, errors, comments, types, simplification, standards, over-engineering), verified and ranked with a fix per finding. Use only when the user says "full review" or invokes /full-review or /skillset:full-review; not for ordinary review requests.
---

# Full review

Fan out independent, read-only review passes over one pinned diff, then verify,
deduplicate, and rank their findings, each with a suggested fix. Never edit,
write, stage, commit, or post review output externally: the user decides which
fixes to apply.

## 1. Pin one scope

Run `scripts/scope.sh [PR number | ref | range]` from the repository root. With
no argument it uses the current branch's merge-base with `main` (then `master`,
then the remote default), including uncommitted edits, falls back to the working
tree on the default branch, and lists untracked files. It prints the diff
command, base, full commit messages, the PR body and whether the PR head is
checked out (PR mode), changed files, untracked files, and the current
`git status --porcelain`, and exits non-zero on a bad ref or an empty scope.
Stop there if it fails: a bad scope caught now costs one command, caught later
it costs every pass.

Add the project's instruction and standards files (`AGENTS.md`, `CLAUDE.md`,
`CONTRIBUTING.md`, coding-standards docs), and any language guide the user's
instructions name for the diff's languages, to the scope block. Untracked files
are part of the change but absent from the diff command, so passes read them
in full. If the script prints `checkout: mismatch`, the working tree is not
the PR's head and every read of surrounding code would see the wrong version;
stop and ask the user to check the PR out.

## 2. Select passes

Passes: `code`, `tests`, `errors`, `comments`, `types`, `simplify`,
`standards`, `ponytail`. With no aspect filter, run all of them, except
`types` when the diff adds or changes no type, class, struct, interface, enum,
or type alias; report that skip. If the user names aspects, run only those.

## 3. Run the passes

Read [passes.md](references/passes.md).

**Small diffs** (under about 50 changed lines): run the selected passes
inline, working through each pass's section in turn. Eight agents on a
handful of lines cost far more than they find.

**Larger diffs**: give each pass its own subagent, all launched together (up
to the environment's limit; queue the rest). Separate agents keep one pass's
concerns from crowding out another's, which is the point of this skill. Above
about 400 changed lines, split the `code` pass into one agent per group of
related files; each still gets the whole scope block, so it can follow calls
across groups. One agent reading a large diff spreads its attention thin and
misses bugs in the second half.

Passes must read whole files and trace into callers, so use an agent that
reviews rather than one that searches:

- **Claude Code with the skillset plugin**: `subagent_type:
  skillset:review-pass`. It has no edit tools. Set `model` per pass:

  | Model | Passes |
  |---|---|
  | `opus` | `code`, `tests`, `errors` |
  | `sonnet` | `comments`, `types`, `simplify`, `standards`, `ponytail` |

  The prompt holds the scope block, the pass name, and the absolute path of
  `passes.md`.
- **Claude Code without the plugin**: `subagent_type: general-purpose`, on the
  session's own model. Not `Explore`: it reads excerpts to locate code rather
  than audit it, which is how bugs outside the hunk get missed.
- **Codex**: a read-only subagent.

Without the plugin agent, paste into each prompt the scope block, the
**Report format** section of `passes.md`, and that pass's section, in full.
The report format and the status check in step 4 keep these agents
read-only.

The `tests` pass needs the test-audit skill's `SKILL.md`, which sits in a
folder next to this skill's folder. If that file exists, give its absolute
path to the `tests` pass in every mode, or read it yourself when you run the
passes inline.

**Lead pass** (larger diffs). While the subagents run, do the `code` pass
yourself over the whole diff and tag those findings `[lead]`. Verification in
step 4 can only remove findings, so without this the subagents' recall is the
report's ceiling.

## 4. Verify

Run `git status --porcelain` again and compare it with `status-before`. Any
difference means a pass wrote something; put it at the top of the report as a
critical item naming the change.

Open the cited location for every critical and important finding and confirm
it, including that the failure scenario really happens and the suggested fix
really addresses it. Passes see only part of the picture and sometimes report
confidently wrong things, and the report is only useful if the user can trust
it. When reading does not settle a finding, run something: the project's
existing tests, or a short probe script in a temporary directory outside the
repository. Leave the repository's files untouched.

Drop findings that are unsupported, out of scope, pre-existing, or wrongly
located, and list them under **Dismissed** with a reason. "Pre-existing"
applies only when the diff neither causes nor exposes the defect: an unchanged
caller whose assumptions the diff broke is a finding. If a fix is wrong but
the finding holds, write a correct fix. Suggestions may pass unverified, since
acting on a wrong one costs little, but they keep their source.

## 5. Deduplicate and triage

Merge findings that share a file, an overlapping hunk, and a root cause, even
when the cited lines differ. Keep the clearest wording and fix, and list all
sources, for example `[ponytail + simplify]`. Agreement raises confidence but
does not turn a judgment call into a violation.

Severity:

- **Critical**: wrong behavior, data loss, security exposure, swallowed
  failure.
- **Important**: documented-standard breaches, meaningful coverage gaps,
  broken type invariants, misleading comments.
- **Suggestions**: simplifications, every ponytail finding, and every smell
  judgment.

Critical findings get a full entry, because the user has to understand and
act on them without re-deriving the problem. Important findings get the
finding plus its fix. Suggestions stay on one line.

````markdown
# Full Review — <scope>

## Critical (N)

### 1. <short title> — `file:line` [source]
**Problem:** what is wrong and why it matters.
**Failure:** the input or state, and the wrong result or crash.
**Evidence:**
```<lang>
<the offending lines>
```
**Fix:**
```<lang>
<replacement code, or the specific change>
```

## Important (N)
- `file:line` — finding [source]
  **Fix:** the change, with code when it fits on a few lines.

## Suggestions (N)
- `file:line` — finding. Fix: short form. [source]

## Dismissed (N)
- `file:line` — finding [source] — reason

## Pass status
- <pass> — ran / clean / skipped (reason)

## Verdict
<worst outstanding issue>; <ponytail net score when that pass ran>.
````

If no actionable findings survive verification, say so. Apply no fixes; offer
to apply the ones the user picks.
