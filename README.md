# skillset

Agent skills for Claude Code, Codex, and any tool that reads `SKILL.md`
folders. In Claude Code they install as one plugin, with the subagents that
`team` and `full-review` start.

## Install

Claude Code:

```sh
claude plugin marketplace add ajay-mk/skillset
claude plugin install skillset@skillset
```

Codex:

```sh
codex plugin marketplace add ajay-mk/skillset
codex plugin add skillset@skillset
```

The skills are then named `skillset:<skill>`, such as `/skillset:pr-wrap-up`.

<details>
<summary>Other tools, and editing the skills</summary>

For other tools, use [`skills`](https://github.com/vercel-labs/skills):

```sh
npx skills add ajay-mk/skillset
```

To work on the skills, add a local clone as the marketplace instead of
`ajay-mk/skillset`. Both tools install a copy of the plugin, so update it
after each change, for example with `claude plugin update skillset@skillset`.

</details>

## Skills

<details>
<summary><b>Agents</b>: <code>team</code></summary>

| Skill | What it does |
|---|---|
| [`team`](skills/agents/team) | Runs a large coding task with subagents that the main session coordinates: `explorer` and `doc-writer` on Sonnet, and `implementor`, `tester`, and `simplifier` on Opus. Asks first unless you invoke it. The agents are role files in [`agents/`](agents). |

</details>

<details>
<summary><b>Pull requests</b>: <code>pr-wrap-up</code>, <code>pr-preflight</code>, <code>pr-describe</code>, <code>pr-comments</code></summary>

`pr-wrap-up` runs the others in order and stops wherever you need to approve
something. Each also works on its own.

```
pr-wrap-up ─▶ pr-preflight ─▶ pr-describe ─▶ (review) ─▶ pr-comments
                                                           └─▶ review-helper (optional)
```

| Skill | What it does |
|---|---|
| [`pr-wrap-up`](skills/pr/pr-wrap-up) | Finds where the PR stands (no PR, open, reviewed, merged) and runs the next step. |
| [`pr-preflight`](skills/pr/pr-preflight) | Read-only readiness check: commit messages, up to date with base, dependency pins, stray files, CI. |
| [`pr-describe`](skills/pr/pr-describe) | Drafts or refreshes the PR title and description from the diff. Posts with `gh` only after you approve. |
| [`pr-comments`](skills/pr/pr-comments) | Fetches review threads, triages each comment, and drafts fixes and replies. Posts and resolves nothing on its own. |

</details>

<details>
<summary><b>Review</b>: <code>full-review</code>, <code>review-helper</code>, <code>test-audit</code></summary>

| Skill | What it does |
|---|---|
| [`full-review`](skills/review/full-review) | Read-only deep review of a change in parallel passes (code, tests, errors, comments, types, simplification, standards, over-engineering), verified, deduplicated, and ranked into one report. |
| [`review-helper`](skills/review/review-helper) | Builds a standalone HTML page that explains a diff file by file, with annotated patches, review-comment traceability, and verification evidence. |
| [`test-audit`](skills/review/test-audit) | Gates new or changed tests at write time and audits existing tests for low-value, implementation-coupled, or duplicate ones. |

</details>

<details>
<summary><b>Research</b>: <code>paper-guide</code>, <code>zotero-fetch-pdfs</code></summary>

| Skill | What it does |
|---|---|
| [`paper-guide`](skills/research/paper-guide) | Runs only when you invoke it. Builds an offline, multi-page HTML guide that explains one paper: chapters, typeset equations, diagrams, demos, and walked-through proofs. From a PDF, a DOI, or a Zotero item. |
| [`zotero-fetch-pdfs`](skills/research/zotero-fetch-pdfs) | Finds and attaches missing PDFs for items in a Zotero collection, through your library's proxy in Chrome. |

</details>

## More

<details>
<summary>Requirements</summary>

- `gh`, authenticated, for the PR skills.
- Python 3 for the scripts in `pr-comments` and `review-helper`.
- Optional: [`unslop`](https://github.com/cursor/plugins) (pstack), which
  `pr-describe` and `pr-comments` apply to PR text and replies when installed.
- [zotero-mcp](https://github.com/54yyyu/zotero-mcp) and Claude in Chrome for
  `zotero-fetch-pdfs`. `paper-guide` uses zotero-mcp only to find a PDF when
  given a Zotero item instead of a file.

</details>

<details>
<summary>Layout</summary>

```
skills/<group>/<skill>/SKILL.md
agents/<agent>.md                  # subagents, also read as role files outside Claude Code
.claude-plugin/                    # plugin and marketplace manifests
```

Add a skill by creating its folder under a group.
A new group also needs its path in `.claude-plugin/plugin.json`.

</details>

## License and credits

MIT. See [LICENSE](LICENSE). Parts of some skills come from other projects:

| Skill | Source | License |
|---|---|---|
| `test-audit` | Adapted from [test-audit](https://github.com/openclaw/openclaw/blob/main/.agents/skills/test-audit/SKILL.md) by Peter Steinberger. Its own [LICENSE](skills/review/test-audit/LICENSE) applies. | MIT |
| `full-review` | The tests, errors, comments, types, and simplify passes are condensed from the `pr-review-toolkit` agents in [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official). | Apache-2.0 |
| `full-review` | The over-engineering pass is condensed from `ponytail-review` in [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail). | MIT |
| `full-review` | The code-smell list follows the `code-review` skill in [mattpocock/skills](https://github.com/mattpocock/skills) and chapter 3 of Martin Fowler's *Refactoring*. | MIT |
| `paper-guide` | Bundles [KaTeX](https://github.com/KaTeX/KaTeX) 0.16.11 for offline equations. Its own [LICENSE](skills/research/paper-guide/assets/katex/LICENSE) applies. | MIT |

