# Auditing for drift

Use this reference when Step 1 found existing context files. The job is to find the
claims that were true when written and are not true now, and to remove what should
never have been written. An existing file is a statement of team intent — revise it,
report what changed, and never replace it wholesale.

## 1. Establish what actually loads

Guessing what is in context is the main reason audits reach wrong conclusions.

1. Run `/context` and record everything under **Memory files**.
2. Compare that against what exists on disk: nested `CLAUDE.md` files, every file in
   `.claude/rules/`, `~/.claude/rules/`, `CLAUDE.local.md`.
3. Account for every difference. A file on disk that never appears is either
   path-scoped and untriggered, excluded by `claudeMdExcludes`, or in a location
   Claude Code does not read.

The `InstructionsLoaded` hook settles any remaining question — it logs exactly which
instruction files loaded, when, and why. It is the right tool for debugging a
path-scoped rule that appears to do nothing.

Run `/doctor` as well. It estimates the skill listing's context cost, names its
biggest contributors, and proposes trims for a committed `CLAUDE.md`: it cuts what
Claude can derive from the codebase — directory layouts, dependency lists,
architecture overviews — and keeps pitfalls, rationale and conventions that differ
from tool defaults. Treat its proposals as a candidate list, not a patch to apply.

## 2. Verify every claim

Take the existing files line by line. For each factual claim, one of three outcomes:

| Outcome | Action |
| --- | --- |
| Still true | Leave it, unless it belongs in a different layer |
| No longer true | Fix it, and note the correction in the handoff |
| Cannot be verified | Remove it, or mark it explicitly as unverified |

The claims that drift fastest, in order:

1. **Commands.** Run them. Scripts get renamed, package managers get swapped, flags
   change. This is where most drift lives.
2. **Paths.** Confirm each one exists. Directory moves rarely reach the memory file.
3. **Versions.** Check against the manifest and lockfile.
4. **"Always" and "never" rules.** Grep for violations. A rule the codebase breaks
   in twenty places is not a convention — it is either aspirational or dead, and
   either way it must not stay written as a rule.
5. **Links.** Every internal link resolves, or it is a defect.

## 3. Prune what should not be there

Independently of truth, remove:

- Facts derivable by reading the code — trees, dependency inventories, architecture
  overviews. A domain dictionary's vocabulary block is the deliberate exception —
  see §9
- Anything the linter, formatter or type-checker enforces
- Procedures longer than about three steps — relocate to a skill
- Workarounds for older model limitations. A rule forcing single-file refactors, or
  banning a technique a current model handles, is pure overhead now. Revisit these
  deliberately after each major model release.
- Duplicates. The same instruction in `CLAUDE.md` and a rule file is a future
  contradiction; keep one.

## 4. Find contradictions

When two instructions conflict, the model picks one arbitrarily, and the symptom is
inconsistency rather than a visible error. Contradictions accumulate across layers
where no single reviewer sees both sides.

Check for conflicts between:

- Root `CLAUDE.md` and a nested one that restates and then diverges from it
- Two rules whose globs overlap
- A memory file and the linter configuration
- A memory file and an accepted decision record

Nested files *add* to the root file and can never override it, so a nested file that
tries to reverse a root instruction is always a bug — fix the root, or scope it.

## 5. Re-home rather than delete

Most audit findings are placement problems, not content problems. Before deleting
something true but misplaced, run it through
[`choosing-the-layer.md`](./choosing-the-layer.md):

| Symptom | Likely fix |
| --- | --- |
| Root file over 200 lines | Move per-file-type conventions to `.claude/rules/` with `paths:` |
| Root file has per-package sections | Split into nested `CLAUDE.md` — see [`monorepos-and-scale.md`](./monorepos-and-scale.md) |
| A long procedure in `CLAUDE.md` | Move to a skill |
| A rule with no `paths:` | Add a glob, or move it to `CLAUDE.md` where readers look |
| Decisions written down but never applied | Index them — see [`indexing-decision-records.md`](./indexing-decision-records.md) |
| An index row's status disagrees with the record | Correct the row; the record is the source of truth. A row reading `Accepted` over a `Superseded` record admits a reversed decision as binding |
| An index with a status column but no binding note | Add it. Without it each reader guesses, and the common guess is that everything listed applies |
| An instruction the model ignores | Make it specific and checkable; if it must hold regardless, make it a hook |

## 6. When the instruction is ignored rather than wrong

"Claude keeps ignoring our convention" usually has one of four causes, in
descending order of likelihood:

1. **It never loaded.** Confirm with `/context` before anything else.
2. **It is too vague to evaluate.** "Format properly" cannot be checked; "use
   2-space indentation" can.
3. **Something contradicts it**, so the model is picking the other one.
4. **It was lost to compaction.** Root `CLAUDE.md` is re-read from disk and
   re-injected after `/compact`. Nested files and path-scoped rules are not — they
   reload only when a matching file is next read. An instruction that must survive a
   long session belongs in the root file.

Memory files are context, not enforcement. When something must hold regardless of
what the model decides, the answer is a `PreToolUse` hook, not stronger wording.
Rewriting a rule in capitals is not a fix.

## 7. Keep it from drifting again

- **Review memory files in pull requests.** They are the only documentation the
  model reads on every task, and they drift exactly as fast as they are unreviewed.
- **A `Stop` hook can propose updates.** It receives the session transcript path
  when Claude finishes responding, so a script can review the session and suggest
  `CLAUDE.md` changes while the gap that exposed them is still fresh.
- **Re-audit after major model releases**, targeting the workaround rules from
  section 3 first.

## 8. Report, do not silently rewrite

Hand back a summary, not just an edited file:

- What was wrong, and what it is now
- What was removed, and why
- What was moved, and to which layer
- What could not be verified, and what would settle it
- Which conventions the team needs to decide, where the code is genuinely ambiguous

An audit that quietly rewrites a file leaves nobody able to tell a correction from
an invention.

## 9. Domain dictionary drift

A domain dictionary carries two drift signatures the checks above do not cover.

- **The dictionary claims a term the code contradicts.** On a live project this can
  be intentional — a `Deprecated → <successor>` entry exists precisely because the
  code identifier is the wrong word and the dictionary is what says so. Check the
  entry's `Status` and the reconciliation record before treating the disagreement as
  staleness; do not auto-prune the vocabulary block to match the code.
- **Provenance older than the source it travelled from.** A projected copy's header
  states what it was last reconciled against; if the source has moved on since, the
  header is stale even though the term table itself may still be correct.

See [`adopting-a-domain-dictionary.md`](./adopting-a-domain-dictionary.md) §7 for why
a dictionary is exempt from §3's derivable-fact pruning: it comes from the client,
not the code, and no amount of reading `src/` recovers it.

## Sources

Claude Code documentation, verified 2026-08-17:

- [How Claude remembers your project](https://code.claude.com/docs/en/memory) — the
  troubleshooting section, and what `/doctor` proposes trimming
- [Hooks reference](https://code.claude.com/docs/en/hooks) — the `InstructionsLoaded`
  and `Stop` events

Three things above ship on Claude Code's release cadence and will drift: **`/doctor`'s
trim check** (added in v2.1.206), the **`InstructionsLoaded` hook** used in §1 to settle
what loaded, and the **`Stop` hook's** transcript payload used in §7. The compaction
behaviour in §6 — root `CLAUDE.md` re-injected, nested files and scoped rules not — is
the claim most worth re-checking, because the audit conclusions in this file depend on
it. Where the documentation disagrees with this reference, **the documentation is
right** — treat a mismatch as a signal to update this file, not as a defect in the
tool.
