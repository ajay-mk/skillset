# team

Runs a large coding task with subagents. The main session (Main) talks to
you, writes a task file, and routes every message between the agents. Start
it with `/team:run`. Main also offers it, and asks first, when a task looks
large.

| Agent | Model | Job |
|---|---|---|
| `explorer` | Sonnet | Maps the code the task touches, read-only |
| `implementor` | Opus | Writes the code for one assigned part |
| `tester` | Opus | Writes tests from the task file and reports gaps |
| `simplifier` | Opus | Reports over-engineering and low-value tests in the finished change, read-only |
| `doc-writer` | Sonnet | Documents the finished change |

Main is meant to run on Fable. [`skills/run/SKILL.md`](skills/run/SKILL.md)
holds the protocol.

```sh
claude plugin marketplace add ajay-mk/skillset
claude plugin install team@skillset
```

## Optional skills

Each agent follows these skills when they are installed:

- `tester` and `simplifier`: [`test-audit`](../../skills/review/test-audit)
  from this repo.
- `simplifier`: `ponytail-review` from
  [ponytail](https://github.com/DietrichGebert/ponytail).
- `doc-writer`: `technical-writing` from
  [pstack](https://github.com/cursor/plugins).
