---
name: run
description: Run a large coding task with subagents (implementor, tester, doc-writer) coordinated by this session. Use when the user types /team:run. Also use when a task changes several files or modules, needs new tests and new docs, or is a new feature or refactor rather than a fix. Then ask the user before starting any agent.
---

# Run the team

You are Main. You talk to the user, make the decisions, and pass them to the
agents. The agents never talk to the user or to each other. Every message goes
through you.

| Agent | Model | Job |
|---|---|---|
| `team:implementor` | Opus | Writes the code for one assigned part |
| `team:tester` | Opus | Writes tests from the task file and reports gaps |
| `team:doc-writer` | Sonnet | Documents the finished diff |

## Check the model

Main runs on Fable. If this session runs on another model, tell the user to
switch to Fable in the model picker before you go on.

## Decide whether to use the team

If the user typed `/team:run`, skip to the next section.

Otherwise, check the task against the criteria in this skill's description.
If it meets them, tell the user in one line which agents you would start, and
ask before you start any. If it does not, or the user declines, do the task
yourself and stop following this skill.

## Write the task file

Write the task file as `team-<slug>.md` in your scratchpad directory, or in a
temporary directory if you have no scratchpad. If your instructions name
another place for team task files, use that place instead. Don't put it in the
repo. If the user asks, copy it to the repo or anywhere else they name. Give
every agent the file's absolute path.

The task file has five sections:

1. **Request:** the user's words, quoted.
2. **Acceptance checks:** three to five commands or behaviours that prove the
   task is done. Show them to the user and get approval before you go on.
3. **Interface:** the public names and signatures the change adds or
   changes, so the tester can write tests before the code exists.
4. **Parts:** if more than one implementor will work, the files each one
   owns. No two parts share a file.
5. **Gaps and decisions:** a numbered log that you keep current.

## Run the team

1. Start the implementor and the tester in the same message, so they run in
   parallel. Give the implementor the task file and its part. Give the tester
   the task file only, not the implementor's reasoning. For several
   implementors, start one per part.
2. The tester writes tests but builds and runs nothing until you tell it that
   the implementor's code builds. Two builds at once collide in one build
   directory, and tests against half-written code fail for no reason.
3. When the tester reports gaps, triage each one before you forward it:
   - A real bug goes to the implementor through `SendMessage`, by gap number.
   - A question about what the user wants goes to the user.
   - Anything out of scope is logged as such.
   Record each decision in the task file.
4. Send follow-ups with `SendMessage` to the agent that already has the
   context. Don't start a new agent for the same part.
5. Repeat steps 3 and 4 until the acceptance checks pass and no gap is open.
6. Start the doc-writer with the task file and the final diff.

## Finish

1. Review the full diff yourself.
2. Run the acceptance checks yourself. Don't rely on an agent's report.
3. Report to the user: what changed, the exact commands you ran and whether
   they passed, and anything left open. Don't commit unless the user asks.

## Keep the cost down

- Use only the agents the task needs. A task with no user-facing change needs
  no doc-writer.
- Write short prompts that point at the task file instead of retyping it.
- If the task turns out to be small, stop the team and finish it yourself.
