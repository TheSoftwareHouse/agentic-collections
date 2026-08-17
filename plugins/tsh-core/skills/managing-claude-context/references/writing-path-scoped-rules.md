# Writing path-scoped rules

Use this reference when recording a convention that applies to some files but not
all. This is the layer most repositories skip, and skipping it is why their
`CLAUDE.md` grows until nobody trusts it.

## 1. Layout

Rules are Markdown files under `.claude/rules/`, discovered recursively, one topic
per file, named for the topic:

```text
your-project/
├── .claude/
│   ├── CLAUDE.md
│   └── rules/
│       ├── code-style.md
│       ├── testing.md
│       ├── security.md
│       └── frontend/
│           └── components.md
```

Personal rules that apply to every project go in `~/.claude/rules/`. They load
before project rules, so project rules win.

## 2. Scope every rule you can

A rule with no `paths:` frontmatter loads at launch, every session, with the same
priority as `.claude/CLAUDE.md`. That is the same cost as putting the text in
`CLAUDE.md` — moving it into `.claude/rules/` and stopping there buys organisation
and nothing else.

A rule with `paths:` loads only when Claude reads a matching file:

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API development

- Every endpoint validates its input before touching the database
- Errors use the standard error response shape in `src/api/errors.ts`
- Public endpoints carry an OpenAPI documentation comment
```

Leave `paths` off only when the rule genuinely applies to every session regardless
of which files are open — and prefer putting that in `CLAUDE.md` instead, where a
reader will look for it.

## 3. Glob patterns

| Pattern | Matches |
| --- | --- |
| `**/*.ts` | All TypeScript files in any directory |
| `src/**/*` | All files under `src/` |
| `*.md` | Markdown files in the project root only |
| `src/components/*.tsx` | React components in one directory, not nested |
| `src/**/*.{ts,tsx}` | Brace expansion across extensions |

Multiple patterns are a YAML list, and any match activates the rule:

```yaml
---
paths:
  - "src/**/*.{ts,tsx}"
  - "lib/**/*.ts"
  - "tests/**/*.test.ts"
---
```

## 4. Two glob traps

**The brace-expansion budget.** Each brace group multiplies the pattern count:
`src/*.{ts,tsx}` is two patterns, `{a,b}/{c,d}/*.{ts,tsx}` is eight. A rule's whole
`paths` list shares a budget of 1,000 expanded patterns and 4 MiB. Any pattern that
would exceed it is used *unexpanded*, so its literal braces match no files and the
rule silently stops firing. Patterns without braces do not count against the budget.
Keep brace groups shallow; prefer several plain patterns over one clever nested one.

**Unescaped `[`.** Glob syntax reads `[` as the start of a bracket expression like
`[abc]`. A pattern containing a `[` that cannot be parsed that way — `photos
[2024/**` — is invalid and matches nothing. The rule's other patterns keep working,
which is what makes this hard to spot. Escape a literal bracket as `photos \[2024/**`.

## 5. Write the rule so it survives on its own

A path-scoped rule arrives in context without the rest of the file that triggered
it, and it is **not** re-injected after `/compact`. Two consequences:

- State the constraint completely. A rule that says "follow the pattern above" has
  no above.
- Anything that must hold for an entire long session belongs in root `CLAUDE.md`,
  not here — after compaction this rule is gone until a matching file is read again.

Keep each rule short. The whole point of the layer is that the cost is paid only
when relevant; a 300-line rule that fires on `**/*.ts` is a `CLAUDE.md` in disguise.

## 6. Sharing rules across repositories

`.claude/rules/` follows symlinks, and circular links are handled:

```shell
ln -s ~/shared-claude-rules .claude/rules/shared
ln -s ~/company-standards/security.md .claude/rules/security.md
```

This is convenient for personal use and a poor fit for a team — a symlink into a
path only some machines have produces silently different behaviour per developer.
For conventions a team shares, commit the files, or ship them as a plugin so they
are versioned and installed explicitly.

## 7. Verify the rule actually fires

A path-scoped rule that never triggers looks identical to one that was never
written. After creating one:

1. **Confirm the glob matches a file that exists today.** Expand it against the
   working tree and count the hits. Zero is not a passing result.
2. Start a session and run `/context` — an unscoped rule should appear under
   **Memory files** immediately; a scoped one should not.
3. Ask Claude to read a file matching the glob.
4. Run `/context` again and confirm the rule now appears.

When it does not, the glob is the first suspect: check for brace-budget overflow and
unescaped brackets before anything else. The `InstructionsLoaded` hook logs exactly
which instruction files loaded and when, which settles it — see
[`auditing-for-drift.md`](./auditing-for-drift.md).

### A glob that matches nothing is a diagnosis, not just a typo

Step 1 fails in two different ways, and they need opposite fixes.

- **The pattern is wrong** — a typo, a stale directory name, an unescaped `[`. Fix the
  pattern.
- **The files do not exist yet**, because the rule describes how to *create* them.
  That is the timing test from
  [`choosing-the-layer.md`](./choosing-the-layer.md) §4 reporting a
  mis-routed instruction. A rule fires when Claude reads a matching file, so it can
  never reach the moment a file is being written. **Move that guidance to a skill.**

The second case is the one that survives review, because the rule reads perfectly and
its glob looks reasonable. Counting the matches is what exposes it.

## Sources

Claude Code documentation, verified 2026-08-17:

- [How Claude remembers your project](https://code.claude.com/docs/en/memory) — see
  *Organize rules with `.claude/rules/`* and *Path-specific rules*

**This is the most version-sensitive reference in the skill.** Several claims above are
tied to specific releases and will drift: the **1,000-expanded-pattern and 4 MiB brace
budget**, the behaviour of an **unescaped `[`** (changed in v2.1.207), **symlinked-path
matching** (v2.1.198), the brace-overflow crash fixed in v2.1.217, and whether
on-demand rules load when `project` is excluded from `--setting-sources` (changed in
v2.1.211). Check the documentation before trusting any of them against a Claude Code
version other than the one that was current when this was written. Where the two
disagree, **the documentation is right** — treat a mismatch as a signal to update this
file, not as a defect in the tool.
