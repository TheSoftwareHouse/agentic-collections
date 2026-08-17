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

### The peer primitives this skill does not own

Memory files are not the whole space. Three siblings sit beside them, and the first
three questions of the predicate below exist to hand work to them:

| Primitive | Take it when |
| --- | --- |
| **Skill** | The guidance is a procedure, or is needed *before* the file it governs exists |
| **Hook** | The outcome must not depend on what Claude decides |
| **Subagent** | The work produces intermediate output nobody will re-read |

**Authoring any of those three belongs to
[`authoring-claude-extensions`](../../authoring-claude-extensions/SKILL.md).** This
skill routes to them and stops there.

## 2. The routing predicate

Ask in order. Stop at the first yes.

1. **Is it a multi-step procedure?** → a skill, not a memory file. `CLAUDE.md` holds
   facts. A procedure written there is long, always loaded, and followed
   inconsistently anyway.
2. **Must it hold regardless of what Claude decides?** → a hook. Memory files are
   context, not enforcement. "Never push to main" in `CLAUDE.md` is a suggestion; a
   `PreToolUse` hook is a block.
3. **Is it needed *before* the file it governs exists?** → a skill. Authoring,
   scaffolding, deciding where something belongs. A path-scoped rule fires when Claude
   **reads** a matching file, so guidance for *creating* one never loads at the moment
   it is needed. See §4.
4. **Does it apply only to files matching a pattern, and only while editing files
   that already exist?** → a path-scoped rule in `.claude/rules/` with `paths:`.
5. **Does it apply only inside one directory, and does that directory's team own
   it?** → a nested `CLAUDE.md` there. See
   [`monorepos-and-scale.md`](./monorepos-and-scale.md) for the ownership test.
6. **Is it a decision with a rationale and a status?** → an ADR behind the index.
   See [`indexing-decision-records.md`](./indexing-decision-records.md).
7. **Does every session genuinely need it?** → root `CLAUDE.md`. This is the last
   resort, not the default.

If the answer to 7 is also no, the instruction does not belong anywhere. Drop it.

Questions 3 and 4 are deliberately adjacent, because they differ only in **timing**
and the subject matter can be identical. "How to write a new endpoint" and "what to
check in existing endpoints" are the same topic, the same glob, and different layers.

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

## 4. Four traps that are invisible in review

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

**A path-scoped rule fires on read, not on write.** It loads when Claude *reads* a
file matching its glob — not when Claude writes one, not when a path is mentioned, not
on every tool use. So a rule at `src/api/**/*.ts` explaining how to write a new
endpoint does not load while the endpoint is being written. It loads afterwards, when
someone opens the finished file.

The symptom is worth memorising, because nothing else points at the rule file: **the
convention is honoured on edits and ignored on creation.** Open an existing example and
the rule is right there in context, working perfectly. Creation-time guidance belongs
in a skill; see §5.

## 5. Rules versus skills

Both hold guidance. They differ in *when* they arrive, which matters more than what
they contain.

| | Rule in `.claude/rules/` | Skill |
| --- | --- | --- |
| Trigger | Claude reads a file matching `paths:` | You invoke `/name`, or its description matches the request |
| Loads | Every session if unscoped; otherwise on a matching read | On demand |
| Fires while a new file is being created | **No** | Yes |
| Survives `/compact` | No — reloads on the next matching read | Yes — the most recent invocation is re-attached within a token budget |
| Best for | Short standing constraints on files that exist — "use 2-space indent in `src/**`" | Procedures, checklists, reference material, anything needed before the file exists |
| Cost when unused | The full text, if unscoped | One line of name and description |

Two dividing lines, and the second is the one people miss:

- **Length and shape.** A three-line constraint is a rule. A twelve-step release
  procedure is a skill, even though both concern releases.
- **Timing.** Guidance needed *before* the governed file exists is a skill regardless
  of length, because a rule cannot reach that moment at all.

### They pair, without duplicating

When guidance is needed at both creation and edit time, use both — and split them so
there is only one copy of the content:

- the **rule** holds the constraint, scoped to the files it governs, and fires
  automatically when someone edits one
- the **skill** holds the creation procedure and **reads the rule file as its
  reference** rather than restating it

Writing the same guidance into both guarantees they diverge, and a contradiction
between layers surfaces as inconsistency rather than as an error.

## 6. Auto memory is not yours to write

Claude Code maintains its own memory at `~/.claude/projects/<project>/memory/`,
written by Claude from your corrections. It is machine-local, is not shared through
version control, and is not a substitute for any layer above.

Never hand-author auto memory to stand in for a `CLAUDE.md`. A teammate cloning the
repository gets none of it, and the resulting behaviour difference between machines
is very hard to diagnose.
