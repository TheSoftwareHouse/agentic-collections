# Choosing the layer

Use this reference before writing or moving any instruction. Every fact belongs to
exactly one layer, and picking the wrong one is the most expensive mistake in this
skill: the instruction still exists, still looks correct in review, and either taxes
every session forever or never loads at all.

## 1. The four layers

| Layer | Lives in | Loads | Holds |
| --- | --- | --- | --- |
| 1. Orientation | root `CLAUDE.md` or `.claude/CLAUDE.md` | Every session, in full | Repo shape, build and test commands, where the other layers are |
| 2. Conventions | `.claude/rules/*.md` with `paths:` | When Claude reads a matching file | Per-technology and per-area conventions |
| 3. Locality | `<subdir>/CLAUDE.md` | When Claude reads a file in that subtree | Conventions the directory's owners maintain, versioned with their code |
| 4. Decisions | `docs/decisions/` behind an index | When Claude follows the index | What was decided, why, and whether it still stands |

Every layer is thin and points downward. A layer that inlines what it should point
to has collapsed into the layer above it, and the whole structure stops paying off.

## 2. The routing predicate

Ask in order. Stop at the first yes.

1. **Is it a multi-step procedure?** → a skill, not a memory file. `CLAUDE.md` holds
   facts. A procedure written there is long, always loaded, and followed
   inconsistently anyway.
2. **Must it hold regardless of what Claude decides?** → a hook. Memory files are
   context, not enforcement. "Never push to main" in `CLAUDE.md` is a suggestion; a
   `PreToolUse` hook is a block.
3. **Does it apply only to files matching a pattern?** → a path-scoped rule in
   `.claude/rules/` with `paths:`.
4. **Does it apply only inside one directory, and does that directory's team own
   it?** → a nested `CLAUDE.md` there. See
   [`monorepos-and-scale.md`](./monorepos-and-scale.md) for the ownership test.
5. **Is it a decision with a rationale and a status?** → an ADR behind the index.
   See [`indexing-decision-records.md`](./indexing-decision-records.md).
6. **Does every session genuinely need it?** → root `CLAUDE.md`. This is the last
   resort, not the default.

If the answer to 6 is also no, the instruction does not belong anywhere. Drop it.

## 3. What never belongs in a memory file

Claude can read the repository. Anything derivable by reading costs context to
state and goes stale the moment the code moves:

- Directory listings and file trees
- Dependency inventories and version tables already in `package.json` or a lockfile
- Generated architecture overviews that restate what the module structure shows
- Anything a linter or formatter already enforces — the tool is the enforcement, and
  restating it in prose creates a second source of truth that will diverge

Keep instead what reading *cannot* reveal: pitfalls, rationale, conventions that
differ from the tool's defaults, and the commands a newcomer would guess wrong.

## 4. Three traps that are invisible in review

**Imports organise; they never save context.** `@path/to/file` in a `CLAUDE.md`
expands and loads at launch, in full, and imported files import recursively up to
four hops. Splitting a 400-line `CLAUDE.md` into four imported files leaves exactly
400 lines in every session. To reference a file *without* loading it, wrap the path
in backticks — import parsing skips Markdown code spans and fenced code blocks, so
`` `docs/decisions/README.md` `` stays literal and Claude reads it on demand.

**Path-scoped rules do not survive `/compact`.** Root `CLAUDE.md` is re-read from
disk and re-injected after compaction. Nested `CLAUDE.md` files and rules with
`paths:` are not — they reload only the next time Claude reads a matching file. An
instruction that must hold for a whole long session belongs in the root file even if
a narrower layer would otherwise fit.

**A rule without `paths:` costs every session.** Rules in `.claude/rules/` with no
`paths` field load at launch with the same priority as `.claude/CLAUDE.md`. Moving a
convention out of `CLAUDE.md` into a rule file saves nothing unless you also scope
it. The move that looks like tidying is often a no-op.

## 5. Rules versus skills

Both hold guidance; they differ in when the cost is paid.

| | Rule in `.claude/rules/` | Skill |
| --- | --- | --- |
| Loads | Every session, or when a matching file is read | When invoked, or when its description matches the request |
| Best for | Short standing constraints — "use 2-space indent in `src/**`" | Procedures, checklists, reference material |
| Cost when unused | The full text, if unscoped | One line of name and description |

The dividing line is length and shape, not topic. A three-line constraint is a rule.
A twelve-step release procedure is a skill even though both concern releases.

## 6. Auto memory is not yours to write

Claude Code maintains its own memory at `~/.claude/projects/<project>/memory/`,
written by Claude from your corrections. It is machine-local, is not shared through
version control, and is not a substitute for any layer above.

Never hand-author auto memory to stand in for a `CLAUDE.md`. A teammate cloning the
repository gets none of it, and the resulting behaviour difference between machines
is very hard to diagnose.
