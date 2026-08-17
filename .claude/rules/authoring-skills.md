---
paths:
  - "plugins/**/skills/**/*.md"
  - "templates/SKILL.md"
---

# Authoring a skill

A skill is instructions loaded into the *current* context, so the main agent follows
the procedure inline with full access to what the conversation already knows. Start
from `templates/SKILL.md`.

## Progressive disclosure above ~150 lines

Once `SKILL.md` passes roughly 150 lines, it carries only:

- the frontmatter
- applicability and precedence
- explicit exclusions
- the non-negotiable rules table
- a **Reference Loading** table
- the procedure

Detail moves to `references/`, one concern per file, **≤300 lines each**.

Two rules make this actually work:

1. **The Reference Loading table needs a "Load when" column.** A bare list of links
   gets skimmed; a trigger condition per row gives the model a predicate to evaluate.
   Pair it with an imperative at the point of use — "read `./references/x.md` before
   writing any controller" — because instruction-following beats table lookup, and
   the two reinforce each other.
2. **A rule that blocks review belongs in `SKILL.md`** even if a reference also
   explains it. `SKILL.md` is what is in context when the model reads no references
   at all.

## Cross-link only inside your own plugin

Reference bundled files as `./references/<topic>.md` from `SKILL.md`, or
`${CLAUDE_PLUGIN_ROOT}/…` for files shared between skills of the same plugin. Claude
Code substitutes `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_SKILL_DIR}` in plugin skill
markdown.

**Never path into another plugin.** It may not be installed, and the failure is a
silent dead link rather than an error. Knowledge that must cross-link has to be
co-located; duplicate the file if two plugins genuinely need it.

## Naming

The skill directory name *is* the skill name. Kebab-case, and **without** a `tsh-`
prefix — the plugin already namespaces it.

- Correct: `audit-page` → `/tsh-product-testing:audit-page`
- Wrong: `tsh-audit-page` → `/tsh-product-testing:tsh-audit-page`

**No framework version in the name.** `implementing-nestjs-api`, not
`implementing-nestjs-11-api`. A skill name is its invocation command, so pinning a
dependency's major forces a rename on every upgrade — breaking docs, muscle memory
and any `enabledPlugins` entry, with no deprecation mechanism. Put the version in the
`description` and in a **Version Baseline** block at the top of `SKILL.md` that tells
Claude to check `package.json` and stop if the project is outside the supported
range.

**Keep names tech-qualified.** `implementing-nestjs-api`, not `implementing-api`.
Namespacing makes `tsh-stack-java:implementing-api` and
`tsh-stack-nodejs:implementing-api` both legal, but the model routes on
*descriptions*, and two near-identical ones are a coin flip. This applies with extra
force to the two TypeScript configuration skills, which are near-twins by design:
`configuring-typescript-for-frontend` and `configuring-typescript-for-nodejs` name
their target because nothing else would tell them apart.

Verbs do real work between related skills. `managing-decision-records` and
`writing-technical-documents` both touch ADRs; `managing-` claims format and
lifecycle, `writing-` claims prose. Two skills claiming the same artifact under the
same verb would be a routing coin flip.

## Renaming a skill is a `major` bump

There is no deprecation mechanism. The name is the invocation command, so a rename
breaks docs, muscle memory and `enabledPlugins` entries at once. See
`/releasing-a-plugin-change`.
