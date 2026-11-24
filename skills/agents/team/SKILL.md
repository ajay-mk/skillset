---
name: team
description: Run a large coding task with subagents (explorer, implementor, tester, simplifier, doc-writer, and a Fable advisor) coordinated by this session. Use when the user types /skillset:team or /team, including to hand the team a task already under way in this session. Also use when a task changes several files or modules, needs new tests and new docs, or is a new feature or refactor rather than a fix. Then ask the user before starting any agent.
---

# Team

You are Main. You talk to the user, make the decisions, and pass them to the
agents. Agents can't see this conversation, and they can't reach the user or
each other. They know only what you write in their prompts and in the task
file, so put every decision there.

| Agent | Model | Job |
|---|---|---|
| `explorer` | Sonnet | Maps the code the task touches, read-only |
| `implementor` | Opus | Writes the code for one assigned part |
| `tester` | Opus | Writes tests from the task file and reports gaps |
| `simplifier` | Opus | Reports over-engineering and low-value tests in the finished change, read-only |
| `doc-writer` | Sonnet | Documents the finished diff |
| `advisor` | Fable | Gives you a second opinion on decisions, read-only |

## Start the agents

- **Claude Code with the skillset plugin:** use `subagent_type:
  skillset:<agent>`, such as `skillset:tester`. Each agent's model and tools
  come with it.
- **Anywhere else, such as Codex:** each agent is a role file in the `agents/`
  folder at the root of this skill's repo or plugin. Resolve this skill
  folder's real path first, because an installer may have linked it, then go
  three folders up. Start a subagent with the text of `agents/<agent>.md`
  below its frontmatter, followed by your message. Use the model in the table
  where your tool lets you choose one. If your tool has no subagents, tell the
  user that this skill needs them, and stop.

The steps below say `SendMessage` for a follow-up to a running agent. Use
your tool's equivalent.

## Check the model

Main runs on Opus at high effort, and the advisor on Fable. If this session
runs on another model or effort, say so to the user once, and go on unless
they want to switch.

## Ask the advisor

Ask the advisor before decisions that are costly to get wrong:

- The task file, before you show the acceptance checks to the user.
- A gap that has gone back and forth twice, before you take it to the user.
- A simplifier finding you are unsure whether to accept.
- The finished change, before you report to the user.

Give it the task file's path, your current decision, and one specific
question. It can't see this conversation. Send later questions to the same
advisor with `SendMessage`, so it keeps what it has read. Weigh its answer
rather than follow it blindly. If you still disagree after a follow-up, tell
the user both views and let them decide.

## Talk to the user

The user reads your messages, not the agents' reports. Bring them decisions
and results, and keep the rest in the task file.

- Don't paste agent reports. Summarize each finding in one line that says
  what it is and where it went, and keep the detail in the task file:

  ```
  Tester found 3 gaps:
  1. parse("") crashes. Sent to the implementor.
  2. Negative sizes are accepted. Sent to the implementor.
  3. Unclear whether duplicate keys are an error. Needs you.
  ```
- Ask one question at a time, with the options and your recommendation.
- Keep approval requests to what the user decides on: the acceptance checks,
  the phase plan, or a disputed gap. Point to the task file for the rest.
- Keep phase and final reports to a few lines each: what changed, the
  commands you ran and whether they passed, and what is still open.

## Decide whether to use the team

If the user invoked this skill by name, skip to the next section.

Otherwise, check the task against the criteria in this skill's description.
If it meets them, tell the user in one line which agents you would start, and
ask before you start any. If it does not, or the user declines, do the task
yourself and stop following this skill.

## Take over a task in progress

The user may start this skill partway through a task: a plan already agreed,
code already changed, or a branch with commits. Don't start over. The team
picks up where the work stands.

1. Collect what exists: the request and the decisions made so far in this
   conversation, any plan, issue, or note the user points to, and the
   current changes from `git log`, `git diff`, and `git status --short`.
2. Set **Base** to the commit before the task began, such as the branch's
   merge-base, so that the work already done counts as part of the change.
   Ask the user if you can't tell where the task began.
3. Fill **Done so far** in the task file with what already exists and
   whether it builds and passes its tests. Record past decisions in **Gaps
   and decisions**, so agents don't reopen them.
4. Skip the explorer if this conversation already covers the code.
5. Give the implementors only the remaining work. Give the tester the whole
   change, including the work done before the team started, because nothing
   tested it independently.

Then continue with the steps below as for a new task.

## Split a long task into phases

Split the task into phases when one loop can't hold it: it needs more than
one interface settled, or more code than an agent can keep in view. Each
phase is a full run of the loop below, from task file to finish.

1. Propose the phases. Give each one a goal and its own acceptance checks,
   and settle the interfaces that cross phases in the first one. A boundary
   that splits an interface makes a later phase rework an earlier one. Ask
   the advisor about the plan, then get the user's approval before you start
   the first phase.
2. Every phase ends with the code building and the tests passing. Stop
   there, report the phase as in **Finish**, and get the user's approval
   before the next phase. Commit the phase only if the user says so.
3. Set the next phase's **Base** to the end of the previous one, so each
   diff covers one phase.
4. Before each phase, update its plan and acceptance checks with what the
   earlier phases taught you. Ask the advisor, and show the user what
   changed. Start the phase only after the user approves.
5. Start fresh agents for each phase. Their context from an earlier phase
   costs more than it helps. Keep the advisor, which holds the view of the
   whole task.
6. Run the simplifier every phase, so its cuts stay small. Run the
   doc-writer every phase, or only after the last one when the docs would
   change from phase to phase.

The take-over steps also resume a phased task in a new session, from the
task file.

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

## Phases
<only for a phased task: one line per phase with its goal. A finished phase
keeps one line: what it did, its commit, and the decisions later phases need.
Only the current phase has the sections below in full.>

## Done so far
<only when taking over: what exists, and whether it builds and passes>

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
  `git diff <base>`. Use both. If the tree already had changes at the start
  that belong to other work, list them under the base so that nobody counts
  them as part of the task.
- **Acceptance checks** are three to five commands or behaviours. Ask the
  advisor about them, then show them to the user and get approval before you
  start any agent. They decide when the
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
   If one gap goes back and forth twice, ask the advisor. After a third
   round, stop and ask the user. A disagreement that persists usually means
   the request is ambiguous.
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
3. Ask the advisor to review the change against the request.
4. Report to the user in a few lines, as in **Talk to the user**: what
   changed, the exact commands you ran and whether they passed, and anything
   left open. Don't commit unless the user asks.

## Keep the cost down

- Use only the agents the task needs.
- Write short prompts that point at the task file instead of retyping it.
- If the task turns out to be small, stop the team and finish it yourself.
