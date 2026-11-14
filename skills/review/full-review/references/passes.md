# Review passes

One section per pass. Paste the whole section into that pass's prompt.

Attribution: the tests, errors, comments, types, and simplify briefs are
condensed and reworded from the pr-review-toolkit agents by Anthropic
(Apache-2.0, github.com/anthropics/claude-plugins-official). The ponytail
brief is condensed from ponytail-review by Dietrich Gebert (MIT,
github.com/DietrichGebert/ponytail). The smell list follows the code-review
skill in mattpocock/skills (MIT) and the catalogue in Martin Fowler's
*Refactoring*, chapter 3. All wording here is original.

## code

Find bugs: behavior that is wrong for some input or state. Project-rule
breaches belong to `standards`, style to `simplify`.

Read each changed file in full, not only the hunks, and read the commit
messages or PR description in the scope block. Then work through each item
below for every hunk. Most missed bugs sit outside the changed lines, in a
caller or in a guarantee the old code gave, so the first three items matter
most.

- **Intent**: does the change do everything the commit message, PR text, or
  docstring claims (atomic, thread-safe, inclusive, sorted, a copy), and
  nothing it rules out?
- **Removed lines**: for each deleted or replaced line, what did it guarantee
  (a lock, a check, a cleanup, an exception, an ordering)? Is that guarantee
  still provided?
- **Callers**: for each function whose signature, return value, exceptions,
  preconditions, or side effects changed, search the repository for every
  caller, including in unchanged files, and check each still works.
- **Conditions**: for each new or changed comparison or branch, try the
  boundary value, one past it, empty input, a single element, and the
  negation.
- **Failure paths**: if any call after the first mutation raises or returns
  early, is state left consistent? Are resources released?
- **State and aliasing**: returned references to internal state, mutable
  defaults or statics that persist between calls, copies that should be
  references and the reverse, mutation order, shared or concurrent access.
- **Numbers**: overflow, signed and unsigned mixing, integer division,
  floating-point comparison, and precision loss in casts or accumulation.
- **Language traps**: for C++, dangling references and views, iterator
  invalidation, use after move, undefined behavior, and assertions standing
  in for production checks. Follow any language guide the project or user
  instructions name.
- **Security and performance**: injection, unchecked trust-boundary input,
  and clear complexity regressions on hot paths.

Report every finding, saying how sure you are; verification filters later,
and a dropped real bug cannot be recovered. A bug that produces wrong
results, data loss, a crash, or a security hole is critical; a bug in a rare path with a visible error is
important. Give a concrete failure scenario for each.

## tests

Judge behavioral coverage of the diff, not line coverage. If no test files
changed, report what changed behavior has no test.

- Look for untested error paths, boundary cases, negative cases for
  validation, uncovered branches of new logic, and async or concurrent paths.
- Flag tests that check implementation details and would break under a
  harmless refactor, or that would still pass if the behavior broke.
- Existing integration tests may already cover a path; check before asking for
  a new test. Skip trivial accessors.
- For each test the diff adds or changes, apply the test-audit gate: what
  behavior or credible regression does it catch, why does existing coverage not
  already catch it, and does it need a production seam no caller uses? Flag any
  match to the junk patterns in `~/.claude/skills/test-audit/SKILL.md` (read
  that file), unless its retention bar names a contract the test independently
  guards. Suggest moving the test to the owning boundary or merging it into an
  existing table case.

A gap that risks data loss, security, or system failure is critical; one that
would let user-facing or confusing errors through is important; the rest are
suggestions. For each gap, name the failure the missing test would catch.

## errors

Find failures the code hides.

Locate every catch/except block, error callback, error-state branch, fallback
or default-on-failure value, log-and-continue path, and optional chaining or
null coalescing that could mask an error. For each, ask:

- Is the catch narrower than "everything"? List unrelated errors it could
  swallow.
- Is the error logged with enough context (operation, identifiers, state) to
  debug it later?
- Does the caller or user learn that something failed, with a message that
  says what went wrong and what to do?
- Is the fallback asked for by the spec, or does it hide the real problem?
  Production code falling back to a mock or stub is always a finding.
- Should the error propagate instead of being handled here? Does handling it
  here skip cleanup?

An error swallowed with no log and no signal to the caller is critical.

## comments

Check every comment and docstring the diff adds or changes, and flag
non-obvious new code that has none.

- **Accuracy**: parameters, return values, described behavior, named symbols,
  handled edge cases, and complexity claims must match the code.
- **Rot**: references to removed or renamed code, stale TODOs, examples that
  no longer run, notes about temporary states.
- **Value**: remove comments that restate the code; keep and ask for comments
  that explain why, preconditions, side effects, and non-obvious algorithms.

A factually wrong or misleading comment is important. Give the replacement
wording or the reason to delete.

## types

For each type the diff adds or changes:

- List its invariants: field relationships, valid states and transitions,
  preconditions.
- Can outside code break them? Check visibility, mutable fields, and whether
  every constructor and mutator enforces them.
- Could the type system enforce an invariant now checked at runtime, or not
  checked at all?
- Is the interface minimal, or does it expose internals?

A reachable invalid state that the type is meant to prevent is important.
Suggest the smallest change that closes it.

## simplify

Report changes that make the diff's code clearer without changing behavior.
Change nothing; quote the shorter or clearer form for each finding.

- Unneeded nesting, redundant code, dead branches, needless intermediate
  variables.
- Nested ternaries or dense one-liners that read better as `if`/`switch`.
- Unclear names, and comments that restate the code.
- Places the diff departs from the project's own conventions.

Do not trade clarity for fewer lines, and keep abstractions that genuinely
organize the code. Every finding is a suggestion.

## standards

Check the diff against the project's documented standards first, then the smell
list below. Check every explicit rule in the instruction files (`AGENTS.md`,
`CLAUDE.md`, contributing and standards docs) against every hunk.

- A breach of a documented rule cites the file and rule. It can be a hard
  violation.
- A smell is always a judgment call. Label it "possible <smell>" and quote the
  hunk.
- A documented project rule overrides the smell list: if the project endorses
  something the list would flag, drop the smell.
- Skip anything a formatter, linter, or compiler already enforces.

Smells (what to look for → usual fix):

- **Mysterious Name**: a name that does not say what the thing does or holds →
  rename it.
- **Duplicated Code**: the same logic in several hunks or files → extract it
  once.
- **Feature Envy**: a function that uses another object's data more than its
  own → move it to that data.
- **Data Clumps**: the same group of fields or parameters travelling together
  → make them one type.
- **Primitive Obsession**: a string or number standing in for a domain concept
  → give the concept a small type.
- **Repeated Switches**: the same branching on the same kind recurring →
  polymorphism or one shared table.
- **Shotgun Surgery**: one logical change spread over many files → gather what
  changes together.
- **Divergent Change**: one module edited for unrelated reasons → split it.
- **Speculative Generality**: parameters, hooks, or abstractions for needs
  nobody has → delete and inline.
- **Message Chains**: long `a.b().c().d()` navigation → one method on the first
  object.
- **Middle Man**: a class or function that only forwards calls → call the
  target directly.
- **Refused Bequest**: a subclass that ignores most of what it inherits → use
  composition.

## ponytail

Find complexity the diff could remove. Complexity only: bugs, security, and
performance belong to other passes.

One line per finding: `<file>:L<line>: <tag> <what>. <replacement>.`

- `delete:` dead code, unused flexibility, speculative feature; nothing
  replaces it.
- `stdlib:` hand-written code the standard library provides; name the function.
- `native:` a dependency or code doing what the platform already does; name the
  feature.
- `yagni:` an abstraction with one implementation, config nobody sets, a layer
  with one caller.
- `shrink:` the same logic in fewer lines; show the shorter form.

Never flag a single smoke test or assert-based self-check. End with
`net: -<N> lines possible.`, or `Lean already.` if there is nothing to cut.
