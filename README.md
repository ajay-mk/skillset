# skillset

Agent skills for Claude Code, Codex, and any tool that reads `SKILL.md`
folders. Each skill is a folder with a `SKILL.md` and, where needed, scripts
and references.

## Pull requests

Four skills that take a branch from finished work to a reviewed PR.
`pr-wrap-up` runs the others in order and stops wherever you need to approve
something; each also works on its own.

```
pr-wrap-up ─▶ pr-preflight ─▶ pr-describe ─▶ (review) ─▶ pr-comments
                                                           └─▶ review-helper (optional)
```

| Skill | What it does |
|---|---|
| [`pr-wrap-up`](skills/pr/pr-wrap-up) | Finds where the PR stands (no PR, open, reviewed, merged) and runs the next step. |
| [`pr-preflight`](skills/pr/pr-preflight) | Read-only readiness check: commit messages, up to date with base, dependency pins, stray files, CI. |
| [`pr-describe`](skills/pr/pr-describe) | Drafts or refreshes the PR title and description from the diff; posts with `gh` only after you approve. |
| [`pr-comments`](skills/pr/pr-comments) | Fetches review threads, triages each comment, and drafts fixes and replies; posts and resolves nothing on its own. |

## Review

| Skill | What it does |
|---|---|
| [`full-review`](skills/review/full-review) | Read-only deep review of a change: parallel passes (code, tests, errors, comments, types, simplification, standards, over-engineering), verified, deduplicated, and ranked into one report. |
| [`review-helper`](skills/review/review-helper) | Builds a standalone HTML page that explains a diff file by file, with annotated patches, review-comment traceability, and verification evidence. |
| [`test-audit`](skills/review/test-audit) | Gates new or changed tests at write time and audits existing tests for low-value, implementation-coupled, or duplicate ones. Adapted from Peter Steinberger's [test-audit](https://github.com/openclaw/openclaw/blob/main/.agents/skills/test-audit/SKILL.md) skill (MIT). |

## Research

| Skill | What it does |
|---|---|
| [`paper-guide`](skills/research/paper-guide) | Run with `/paper-guide`. Builds an offline, multi-page HTML guide that explains one paper: chapters, typeset equations, diagrams, demos, and walked-through proofs. From a PDF, a DOI, or a Zotero item. |
| [`zotero-fetch-pdfs`](skills/research/zotero-fetch-pdfs) | Finds and attaches missing PDFs for items in a Zotero collection, through your library's proxy in Chrome. |

## Plugins

The repo is also a Claude Code plugin marketplace named `skillset`.

| Plugin | What it does |
|---|---|
| [`team`](plugins/team) | Runs a large coding task with a team of subagents that the main session coordinates. |

## Install

With [`skills`](https://github.com/vercel-labs/skills), into any supported
tool:

```sh
npx skills add ajay-mk/skillset
```

Or clone and link, to edit the skills in place:

```sh
git clone git@github.com:ajay-mk/skillset.git && ./skillset/install.sh
```

`install.sh` symlinks each skill into `~/.claude/skills` and `~/.codex/skills`
for whichever tool is installed. It does not install the plugins. Re-running is safe: correct links are left
alone, links into this repo that moved are updated, and anything else in the
way is reported and skipped.

## Requirements

- `gh`, authenticated, for the PR skills.
- Python 3 for the scripts in `pr-comments` and `review-helper`.
- Optional: [`unslop`](https://github.com/cursor/plugins) (pstack), which
  `pr-describe` and `pr-comments` apply to PR text and replies when installed.
- [zotero-mcp](https://github.com/54yyyu/zotero-mcp) and Claude in Chrome for
  `zotero-fetch-pdfs`. `paper-guide` uses zotero-mcp only to find a PDF when
  given a Zotero item instead of a file.

## Layout

```
skills/<group>/<skill>/SKILL.md
plugins/<plugin>/                           # listed in .claude-plugin/marketplace.json
```

Add a skill by creating its folder under a group and re-running `install.sh`.
Add a plugin by creating its folder under `plugins/` and listing it in
`.claude-plugin/marketplace.json`.

## License and credits

MIT; see [LICENSE](LICENSE). Parts of some skills come from other projects:

| Skill | Source | License |
|---|---|---|
| `test-audit` | Adapted from [test-audit](https://github.com/openclaw/openclaw/blob/main/.agents/skills/test-audit/SKILL.md) by Peter Steinberger; its own [LICENSE](skills/review/test-audit/LICENSE) applies | MIT |
| `full-review` | The tests, errors, comments, types, and simplify passes are condensed from the `pr-review-toolkit` agents in [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Apache-2.0 |
| `full-review` | The over-engineering pass is condensed from `ponytail-review` in [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | MIT |
| `full-review` | The code-smell list follows the `code-review` skill in [mattpocock/skills](https://github.com/mattpocock/skills) and chapter 3 of Martin Fowler's *Refactoring* | MIT |
| `paper-guide` | Bundles [KaTeX](https://github.com/KaTeX/KaTeX) 0.16.11 for offline equations; its own [LICENSE](skills/research/paper-guide/assets/katex/LICENSE) applies | MIT |
