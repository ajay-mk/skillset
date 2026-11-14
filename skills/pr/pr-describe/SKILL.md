---
name: pr-describe
description: Draft or refresh a pull request's title and description from the branch diff, then create or edit the PR with gh once the user approves. Use when the user asks for a PR description, title, "write up this PR", "update the PR description after these commits", or as a step of pr-wrap-up.
---

# PR describe

Write the PR text a reviewer needs: what the change does, grouped by area,
with the cross-references that tie it to other PRs. Say only what the diff
and commits show; never invent motivation, impact, or performance claims. If
the reason for a change is not visible, leave it out or ask.

## 1. Gather

- Base and head as in pr-preflight. Existing PR: `gh pr view --json
  number,title,body,url,baseRefName`.
- Read `git log origin/<base>..HEAD` and the full diff, plus enough
  surrounding code to describe behavior, not just file names.
- Collect references: issues and PRs named in commits or branch names, PRs
  whose commits a dependency pin points at. Write them as `owner/repo#N`.
- Use the repo's PR template (`.github/pull_request_template.md` or similar)
  if it has one; it overrides the shape below.

## 2. Draft

**Title:** imperative, specific, under ~72 characters, code identifiers in
backticks. Two changes joined with a semicolon when the PR really has two
parts. No `feat:`/`fix:` prefixes unless the repo uses them.

**Body**, by default:

```markdown
<One or two sentences: what the PR does as a whole, with cross-references.>

## Change

- **<Area>:** <what changed there, as behavior>.
- **Tests:** <what is covered, and where it runs>.
- **Pins:** <dependency> `<sha>` (owner/repo#N, which <what it brings>).
```

- One bullet per area a reviewer would look at, bold label first. Merge
  mechanical changes into one bullet.
- Limitations or follow-ups only if the diff or the user states them.
- No file-by-file list, no headings beyond `## Change` unless the change
  needs them (e.g. a `## Usage` example for a new API).

**Diagram:** when the change alters a flow, an architecture, a data model, or
a state machine that a picture explains faster than text, offer in one line to
draw it; skip the offer for small or mechanical changes. If the user accepts,
use a diagram skill if one is installed (such as `diagram-design`). In the PR
body, a Mermaid block renders directly on GitHub; an exported image has to be
attached in GitHub's web editor, so say so.

**Unslop:** if the `unslop` skill is installed (its `SKILL.md` under
`~/.agents/skills/unslop/` or the tool's own skills folder), read it and apply
its rules to the title and body before showing them. The shape above and the
repo's template win where they differ; the bold area labels stay.

**Refresh:** when updating an existing description after new commits, keep
the user's own edits, change only what the new commits changed, and say what
you changed.

## 3. Post

Show the title and body in chat. Create or edit the PR only after the user
approves, with the body in a temp file (`gh pr create --title ... --body-file
<f>` or `gh pr edit <n> --title ... --body-file <f>`). Use the base from step
1 and open as draft if the user says so. Report the PR URL.
