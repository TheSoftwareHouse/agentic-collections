# Writing CLAUDE.md

Use this reference when creating or trimming a `CLAUDE.md`, root or nested. The
target is under 200 lines. Adherence drops as the file grows, so length is not a
style preference here — it is the property that makes the file work.

## 1. Where the file goes

| Path | Scope | Committed |
| --- | --- | --- |
| `./CLAUDE.md` or `./.claude/CLAUDE.md` | The project, for everyone | Yes |
| `./<subdir>/CLAUDE.md` | That subtree | Yes |
| `./CLAUDE.local.md` | You, in this checkout | No — gitignore it |
| `~/.claude/CLAUDE.md` | You, everywhere | No |

Root and `.claude/CLAUDE.md` are equivalent; pick one and do not create both. Files
above the working directory load in full at launch; files in subdirectories load
when Claude reads there.

`CLAUDE.local.md` exists only in the worktree where you made it. To carry personal
instructions across worktrees, import one from your home directory instead:
`@~/.claude/my-project-instructions.md`.

## 2. The content contract

A root `CLAUDE.md` answers four questions and stops:

1. **What is this repository?** One or two sentences. Not a feature tour.
2. **How do I build, test and run it?** The exact commands, verified by running
   them. Name the package manager. If commands must run from a subdirectory, say so.
3. **What would a newcomer get wrong?** The conventions that differ from the tool's
   defaults, the pitfalls, the things that look wrong but are deliberate.
4. **Where is everything else?** Pointers to the rules directory, the decision index,
   and any nested `CLAUDE.md` files.

Everything else belongs to another layer. Check it against
[`choosing-the-layer.md`](./choosing-the-layer.md) before writing it here.

## 3. What to cut

Cut on sight:

- Directory trees and file listings — Claude reads the filesystem
- Dependency lists that restate the manifest
- Architecture overviews that restate the module structure
- Anything a linter, formatter or type-checker enforces
- Procedures longer than about three steps — move them to a skill
- Aspirational rules nobody follows; they teach the model the file is unreliable
- Workarounds for older model limitations, which become pure overhead once the
  limitation is gone

The test for keeping a line: would a competent newcomer get this wrong by reading
the code alone? If no, cut it.

## 4. Write instructions the model can evaluate

Specific beats general, and checkable beats aspirational:

| Instead of | Write |
| --- | --- |
| Format code properly | Use 2-space indentation |
| Test your changes | Run `npm test` before committing |
| Keep files organised | API handlers live in `src/api/handlers/` |
| Handle errors well | Throw `AppError` subclasses; never return `null` for failure |

Group with headers and bullets rather than paragraphs. Contradictions are worse than
omissions — when two instructions conflict, the model picks one arbitrarily, so
re-read the whole file after editing any part of it.

## 5. Nested files add, they do not replace

Every discovered `CLAUDE.md` is concatenated, root-first, working-directory-last.
A nested file adds to the root file; it cannot override or switch it off. Write
nested files as pure additions and never restate the root file's content — a
restatement that drifts becomes a contradiction.

A root file in a repository with packages should orient rather than specify:

```markdown
This is a monorepo with three packages under `packages/`:

- `packages/api`: Node.js REST API — Express, TypeScript, PostgreSQL
- `packages/web`: React frontend — Vite, TypeScript, Tailwind
- `packages/shared`: TypeScript utilities used by both

Run commands from the package directory, not the repository root.
Each package has its own `package.json`, `tsconfig.json` and test suite.

Conventions live in `.claude/rules/`. Decisions are indexed in
`docs/decisions/README.md`.
```

Note both pointers on the last lines are in backticks. Written bare with a leading
`@` they would become imports and load at launch — see
[`choosing-the-layer.md`](./choosing-the-layer.md).

## 6. AGENTS.md interoperability

Claude Code reads `CLAUDE.md`, not `AGENTS.md`. When a repository already keeps
`AGENTS.md` for other tools, do not duplicate it. Import it, and add anything
Claude-specific below:

```markdown
@AGENTS.md

## Claude Code

Use plan mode for changes under `src/billing/`.
```

A symlink works when there is nothing Claude-specific to add:

```shell
ln -s AGENTS.md CLAUDE.md
```

On Windows a symlink needs Administrator rights or Developer Mode, so prefer the
import form in any repository with Windows contributors. Confirm the result with
`/context` — `CLAUDE.md` must appear under **Memory files**.

## 7. Maintenance

Treat these files as code:

- Review `CLAUDE.md` changes in pull requests, so conventions track the code
- Re-check after a major model release; instructions written around an older model's
  limitation become overhead once it is gone
- Leave maintainer notes in block-level HTML comments — they are stripped before the
  content reaches Claude's context, so they cost nothing

When the file is already too large, [`auditing-for-drift.md`](./auditing-for-drift.md)
covers trimming an existing file rather than writing a new one.
