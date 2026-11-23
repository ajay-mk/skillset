---
name: run
description: Run a large coding task with subagents (explorer, implementor, tester, simplifier, doc-writer) coordinated by this session. Use when the user types /team:run. Also use when a task changes several files or modules, needs new tests and new docs, or is a new feature or refactor rather than a fix. Then ask the user before starting any agent.
---

# Run the team

You are Main. You talk to the user, make the decisions, and pass them to the
agents. Agents can't see this conversation, and they can't reach the user or
each other. They know only what you write in their prompts and in the task
file, so put every decision there.

| Agent | Model | Job |
|---|---|---|
| `team:explorer` | Sonnet | Maps the code the task touches, read-only |
| `team:implementor` | Opus | Writes the code for one assigned part |
| `team:tester` | Opus | Writes tests from the task file and reports gaps |
| `team:simplifier` | Opus | Reports over-engineering and low-value tests in the finished change, read-only |
| `team:doc-writer` | Sonnet | Documents the finished diff |

This skill is written for Main on Fable. If this session runs on another
model, say so to the user once, and go on unless they want to switch.

## Decide whether to use the team

If the user typed `/team:run`, skip to the next section.

Otherwise, check the task against the criteria in this skill's description.
If it meets them, tell the user in one line which agents you would start, and
ask before you start any. If it does not, or the user declines, do the task
yourself and stop following this skill.

## Write the task file

You need to know the code to settle the interface and the parts. Start the
explorer with the user's request, and use its report to write the task file.
This keeps the codebase out of your own context. If you already know the
code well, skip the explorer. If the interface can't be settled up front,
have one implementor propose it first, record it, and then start the tester.

Write the task file as `team-<slug>.md` in your scratchpad directory, or in a
temporary directory if you have no scratchpad. If your instructions name
another place for team task files, use that place instead. Don't put it in the
repo. If the user asks, copy it to the repo or anywhere else they name. Give
every agent the file's absolute path.

Use this template:

```markdown
# <task title>

Base: <commit hash at the start>

## Request
> <the user's words, quoted>

## Acceptance checks
1. <command or behaviour that proves the task is done>

## Interface
<public names and signatures the change adds or changes>

## Parts
- implementor-1: <files it owns>

## Gaps and decisions
1. <gap or decision>. Owner: <agent or user>. Status: <open, fixed, not a
   bug, or out of scope>.
```

- **Base** lets every agent, and you at the end, see the whole change. Agents
  don't commit, so new files appear only in `git status --short`, not in
  `git diff <base>`. Use both. If the tree already had changes at the start,
  list them under the base so that nobody counts them as part of the task.
- **Acceptance checks** are three to five commands or behaviours. Show them to
  the user and get approval before you start any agent. They decide when the
  team is done, so a vague check leads to a loop that never ends.
- **Interface** lets the tester write tests before the code exists.
- **Parts** matters only with several implementors. No two parts share a file,
  because agents in one checkout overwrite each other's edits.

## Run the team

Where agents run in the background, you are notified when each one reports.
Wait for the reports. Don't poll, and don't do an agent's part yourself while
it runs.

1. Start the implementor and the tester in the same message, so they run in
   parallel. Give the implementor the task file and its part. Give the tester
   the task file only, not the implementor's reasoning, so that its tests
   check the request rather than the code. For several implementors, start
   one per part.
2. The tester writes tests against the interface but builds and runs nothing
   yet. Two builds at once collide in one build directory, and tests against
   half-written code fail for no reason. With several implementors, tell each
   one in its prompt to hold its build. Build once yourself after all of them
   report, or let one build at a time.
3. When every implementor reports that its code builds, check the reports
   for changes to the interface, and record them in the task file. Then tell
   the tester, through `SendMessage`, to build and run its tests.
4. Triage each gap the tester reports before you forward it:
   - A bug in the code goes to the implementor, by gap number.
   - A wrong test goes back to the tester, with the reason.
   - A question about what the user wants goes to the user.
   - Anything out of scope is logged as such.
   Record each decision in the task file.
5. Send follow-ups with `SendMessage` to the agent that already has the
   context. Don't start a new agent for the same part.
6. Repeat steps 4 and 5 until the acceptance checks pass and no gap is open.
   If one gap goes back and forth three times, stop and ask the user. A
   disagreement that persists usually means the request is ambiguous.
7. Once the acceptance checks pass, start the simplifier with the task file.
   It reviews the tests as well as the code. Triage its findings as you do
   gaps. Send accepted code findings to the implementor and accepted test
   findings to the tester, log the rest, and have the tester rerun after the
   changes.
   Skip the simplifier for a change of a few lines.
8. If the change affects anything users or developers read, start the
   doc-writer with the task file. It reads the change from the base. It runs
   last, so that it documents the code that stays.

## Finish

1. Read `git diff <base>` and the new files in `git status --short` yourself.
   Check every existing test that was changed or deleted. Each one needs a
   reason in the request, not just a passing run.
2. Run the acceptance checks yourself. An agent's report is a claim, not a
   result.
3. Report to the user: what changed, the exact commands you ran and whether
   they passed, and anything left open. Don't commit unless the user asks.

## Keep the cost down

- Use only the agents the task needs.
- Write short prompts that point at the task file instead of retyping it.
- If the task turns out to be small, stop the team and finish it yourself.
