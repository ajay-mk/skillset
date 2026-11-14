---
name: pr-comments
description: Fetch a pull request's review comments, triage each one, investigate the code, and draft a fix plan and a reply per comment, without posting or resolving anything on its own. Use when the user says "we got review comments", "address the review", "triage the PR feedback", "look at what <reviewer> said", or as a step of pr-wrap-up.
---

# PR comments

Turn review feedback into a triaged list the user can act on: what each
reviewer asked, whether it holds, what to change, and what to reply. Reading
comments does not authorize editing code, pushing, posting replies, or
resolving threads; each of those waits for the user's go-ahead.

## 1. Fetch

```sh
python3 scripts/fetch_comments.py <pr> [-R owner/repo] -o <file>.json
```

It returns review threads (path, line, `remote`: open/resolved, `outdated`,
every comment), review summaries, and conversation comments. If `truncated`
is true, say which part is incomplete. Keep the JSON outside the checkout.

By default triage open threads plus review summaries and conversation
comments that ask for something; include resolved or outdated threads only
when the user asks or a later comment reopens the point. If the user names a
reviewer or says which point matters most, start there.

## 2. Triage

For each comment, read the code it points at (on the current head, and at the
commented line if outdated) and decide:

- **concern:** the reviewer's point in one line, in your words.
- **verdict:** valid, partly valid, not valid, or unclear (needs the
  reviewer). Ground it in the code or a check you ran, not in plausibility.
- **action:** fix, explain, decline, or ask. For a fix, the files and the
  change; for a decline, the reason a reviewer would accept.
- **reply:** a short draft reply in the user's voice: what was done or why
  not, with a commit hash once one exists. No thanks-boilerplate. If the
  `unslop` skill is installed, apply its rules to the reply.

Independent comments that need real investigation can go to subagents; check
what they return against the code before using it.

## 3. Present and act

Show a table: #, reviewer, location, concern, verdict, action. Then the draft
replies. Ask which fixes to make. After the user approves:

- Make the fixes, one commit per comment or per coherent group, following the
  repo's and user's commit rules.
- Post a reply only when the user says to:
  `gh api repos/<o>/<r>/pulls/<n>/comments/<comment-id>/replies -f body=...`
  for a review thread, `gh pr comment <n> --body-file <f>` for the
  conversation.
- Resolve a thread only when the user asks; usually the reviewer resolves.

Keep the local status (implemented, declined, pending) separate from the
remote thread state (open, resolved): a fix you pushed is not a resolved
thread.

## Output for review-helper

When a review-helper page is wanted, write the triage as its `comments` list:
`{id, source: "pr", author, url, location, body, concern, disposition,
remote, explanation, evidence: [{file, line, side?}]}`, where `disposition`
is the local status and `remote` comes from the fetch.
