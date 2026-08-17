# Choosing the primitive

Use this reference whenever the routing table in `SKILL.md` gives more than one
plausible answer. Picking wrong is the most expensive mistake available here, because
the artifact still exists, still reads correctly, and either never loads or loads
constantly.

## 1. The three deciding questions

Everything below reduces to these. Ask them in order.

1. **When is it needed?** Before the file exists → a skill. While editing files that
   already exist → a path-scoped rule. Every session regardless → `CLAUDE.md`.
2. **Must it be guaranteed?** If the outcome cannot depend on Claude's judgement →
   a hook. Everything else is context, and context is advice.
3. **Whose context pays?** If the work produces a lot of intermediate output nobody
   will re-read → a subagent, so the main conversation only receives the result.

## 2. Timing beats subject matter

This is the trap that produces correct-looking, never-loading guidance.

A path-scoped rule loads **when Claude reads a file matching its `paths:` glob**. Not
when Claude writes one, not when a path is mentioned, not on every tool use. The
consequence:

> Guidance about how to **create** an artifact, scoped to that artifact's own path,
> never fires while the artifact is being created. It fires afterwards, when someone
> reads the finished file.

The symptom is specific and worth memorising: **the convention is honoured on edits
and ignored on creation.** Nobody suspects the rule file, because when you open an
existing example the rule is right there in context, working perfectly.

| The guidance is about | It is needed | So it is |
| --- | --- | --- |
| How to write a new API endpoint | While the endpoint is being written, before it exists | A skill |
| What to check in existing API endpoints | While reading or editing them | A path-scoped rule |
| Both | Both | A skill for the creating half, a rule for the editing half — see §6 |

Subject matter is identical in all three rows. Only timing differs, and only timing
decides.

## 3. Rule versus skill

| | Path-scoped rule | Skill |
| --- | --- | --- |
| Trigger | Claude reads a file matching `paths:` | You invoke `/name`, or the `description` matches the request |
| Fires while creating a new file | **No** | Yes |
| Cost when unused | Zero, if scoped; the full text if not | One `description` in the listing |
| Survives `/compact` | No — reloads on the next matching read | Yes — the most recent invocation is re-attached within a token budget |
| Best for | Short standing constraints on files that exist | Procedures, checklists, reference material |

Two consequences people miss:

- **A rule without `paths:` costs every session**, at the same priority as
  `.claude/CLAUDE.md`. Moving text out of `CLAUDE.md` into an unscoped rule file buys
  organisation and saves nothing.
- **A glob that matches no file today is a rule that has never fired.** Check it. If
  it matches nothing because the files do not exist yet, that is not a broken glob —
  it is the timing test telling you this should be a skill.

## 4. Skill versus subagent

Both hold reusable instructions. They differ in *where the work happens*.

| | Skill | Subagent |
| --- | --- | --- |
| Context | Loads into the current conversation | Its own isolated window |
| What comes back | Everything it does is visible | Only the final result |
| Best for | Procedures the main agent should follow inline | Work that reads many files, or runs in parallel |

Choose a **subagent** when the intermediate reasoning is noise: broad searches,
audits, independent reviews, anything that would otherwise fill the conversation with
output nobody returns to. Choose a **skill** when the work needs what the conversation
already knows, or when its output *is* the point.

They compose. A subagent can preload skills with its `skills:` field, and a skill can
run in an isolated context with `context: fork`. Reach for that when a procedure is
worth writing down *and* worth running out of sight.

## 5. Hook versus instruction

| | Hook | Instruction in a skill or memory file |
| --- | --- | --- |
| Trigger | A lifecycle event — guaranteed | Claude judging it relevant |
| Determinism | Always fires | Usually followed |
| Context cost | Zero, unless it returns output | Loaded text |

The rule: **if it must hold every time, it is a hook.** "Never edit `.env`" written
anywhere in context is a request. A `PreToolUse` hook that denies the call is
enforcement.

This is also the correct answer to "Claude keeps ignoring our convention" — *once you
have ruled out the three cheaper causes*: it never loaded (check `/context` first), it
is too vague to evaluate, or something else in context contradicts it. Rewriting a
rule in capitals is not a fix. Neither is a hook, if the instruction simply never
loaded.

## 6. A rule and a skill together

These are not exclusive, and pairing them is usually right when guidance is needed at
both creation and edit time. The split that avoids duplication:

- The **rule** holds the constraint, scoped to the files it governs, and fires
  automatically when someone edits one.
- The **skill** holds the creation procedure, and **reads the rule file as its
  reference** rather than restating it.

One copy of the content, two entry points, no drift. The failure mode to avoid is
writing the same guidance into both, which guarantees they diverge and then contradict
each other — at which point Claude picks one arbitrarily and the symptom is
inconsistency rather than an error.

## 7. When the answer is a plugin

A plugin is not an alternative to the other four; it is the **packaging layer** for
them. The trigger is distribution, never capability: a second repository needs the
same setup, or other people do.

Build the skill, subagent or hook first and use it in one place. Package it once it has
survived contact with real work. A plugin authored before its contents are proven
distributes an untested opinion, and every installer pays listing budget for it.

## 8. When the answer is "none of these"

Some things should not be built at all:

- Anything a linter, formatter or type-checker already enforces. The tool is the
  enforcement; restating it in prose creates a second source of truth that will drift.
- Anything Claude can derive by reading the repository.
- A workaround for a model limitation that no longer exists. Revisit these
  deliberately after each major model release.

Building one of these costs context forever and buys nothing. Saying so is a valid
outcome of this skill.
