# Monorepos and scale

Use this reference when the repository has packages or subsystems with different
owners. The defaults are tuned for a single small project; at scale they fill the
context window with instructions unrelated to the task, which costs tokens and
degrades the model's output.

## 1. The split trigger

One root `CLAUDE.md` covering every subsystem has two failure modes and no third
option: it grows until it costs every session dearly and adherence collapses, or it
stays short by staying generic and stops being useful.

**Split downward when the root file starts growing per-package or per-subsystem
sections.** That is the signal, and it arrives well before the 200-line limit. A
root file with an "API conventions" heading and a "Frontend conventions" heading has
already outgrown its layer, even at 80 lines.

After the split, the root file orients and the leaves specify:

- **Root** — what the repository is, where the packages are, which commands run
  where, and pointers to the other layers
- **Per-package or per-subsystem** — that area's stack, commands and conventions

In a monorepo that is one file per package. In a large single tree it is one per
subsystem — `src/db/`, `src/api/` — and everything on this page applies unchanged.

## 2. Nested CLAUDE.md or a path-scoped rule?

Both target instructions at part of the tree. They differ in where the file lives
and when it loads.

| Approach | File location | Loads when | Use when |
| --- | --- | --- | --- |
| Per-directory `CLAUDE.md` | Inside the directory, beside its code | At launch if started from that directory; on demand when Claude reads a file there | The directory's owners maintain their own conventions and want them versioned with the code |
| Path-scoped rule in `.claude/rules/` | Central `.claude/` at the repo root | When Claude works with a file matching `paths:` | Conventions are maintained centrally, or one rule applies to many scattered paths |

**The deciding question is ownership, not file count.** A rule the platform team
maintains for everyone belongs in `.claude/rules/`, however many directories it
touches. A convention the payments team owns belongs in `packages/payments/CLAUDE.md`,
where their reviewers will see it change.

Two secondary tie-breakers, when ownership does not decide it:

- A convention that follows a *file type* wherever it appears — every `*.test.ts` in
  the repo — is a rule. A convention that follows a *place* is a nested file.
- A nested `CLAUDE.md` loads for any file in its subtree; a rule fires only on its
  glob. When the constraint is about one file type inside one package, the rule is
  the sharper instrument.

## 3. Where you start Claude changes what loads

| Start from | File access | `CLAUDE.md` loaded at launch |
| --- | --- | --- |
| Repository root | Every file | Root only; subdirectory files load on demand |
| A package directory | That subtree, until you grant more | That directory's plus every ancestor's |

Starting from `packages/api/` loads the root file and `packages/api/CLAUDE.md`, and
never loads `packages/web/CLAUDE.md`. This is the cheapest scoping mechanism
available and it needs no configuration — recommend it before recommending settings.

Note that `.claude/settings.json` is **not** inherited the way `CLAUDE.md` is: it
loads only from the directory you start in. A root settings file does not apply when
you start from a package.

## 4. Excluding packages you never touch

When you do start from the root, every subdirectory's `CLAUDE.md` loads as soon as
Claude reads a file there. `claudeMdExcludes` skips files by glob, matched against
absolute paths:

```json
{
  "claudeMdExcludes": [
    "**/packages/web/**"
  ]
}
```

Useful patterns: `"**/packages/*/CLAUDE.md"` excludes every package's file while
keeping the root; `"**/packages/legacy-*/**"` excludes by name including rules.

Put this in `.claude/settings.local.json` when it is your preference rather than the
team's, and add that file to your gitignore. The list is static, not a per-task
switch — to focus on a different package tomorrow, start Claude from that package
instead of editing exclusions. Managed policy files cannot be excluded.

## 5. Per-directory skills

Any subdirectory can carry skills scoped to its own stack in
`<subdir>/.claude/skills/`. They load on demand, so a package's tooling costs
nothing during work elsewhere. Commit them beside that area's code.

A skill in the repository root's `.claude/skills/` can be scoped by file pattern
instead of by placement, using `paths:` frontmatter — the right shape for something
like a migration skill that applies to `**/migrations/**` wherever they appear.

## 6. Skill listings get crowded at scale

Claude routes by reading every discovered skill's name and description. Starting
from the root, skills accumulate from every subdirectory Claude touches during the
session, which can reach the hundreds. Names always load, but descriptions are
shortened when the listing overflows its budget — and shortening strips the keywords
routing depends on.

Practical consequences for a large repository:

- Keep descriptions short and lead with the words a request would actually contain
- Put skills many directories share in the root `.claude/skills/`, so they load from
  any starting directory
- When shared skills need version history or must work across repositories, ship
  them as a plugin — plugin skills are namespaced `plugin-name:skill-name` and never
  collide with per-directory skills
- `/doctor` estimates the listing's context cost and names its biggest contributors

## 7. When layering stops scaling

Per-directory files eventually become hard to govern: conventions drift, files go
stale, and nobody owns the root. At that point the fix is ownership, not more files.
Move reference content out of always-loaded memory files into mechanisms that load
on demand — skills for procedures, a plugin for versioned bundles a platform team
maintains centrally.

A `SessionStart` hook can close the discovery gap that creates: anything it prints
to stdout enters context before the first prompt, so a script can map the launch
directory to the plugin that area's owners maintain and tell Claude to mention it.

## Sources

Claude Code documentation, verified 2026-08-17:

- [Monorepos and large repos](https://code.claude.com/docs/en/large-codebases)
- [How Claude remembers your project](https://code.claude.com/docs/en/memory) — nested
  file discovery and `claudeMdExcludes`

Three things above ship on Claude Code's release cadence and will drift: **which files
load at launch versus on demand** as you move the start directory, the
**`claudeMdExcludes`** glob semantics and the settings layers it merges across, and the
`SessionStart` hook behaviour. Where the documentation disagrees with this reference,
**the documentation is right** — treat a mismatch as a signal to update this file, not
as a defect in the tool.
