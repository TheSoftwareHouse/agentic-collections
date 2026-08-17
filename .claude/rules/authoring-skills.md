---
paths:
  - "plugins/**/skills/**/*.md"
  - "templates/SKILL.md"
---

# Skills in this marketplace

Repo-specific constraints for a skill that ships from here. **The general mechanics —
frontmatter, writing a `description` that routes, progressive disclosure, the
Reference Loading table — belong to `/tsh-core:authoring-claude-extensions`.** Invoke
it rather than working from memory; this file is only the local delta.

Creating a skill from scratch? Start with `/contributing-a-plugin-component`. This
rule fires when Claude *reads* a skill file, so it cannot reach you while you are
writing a new one.

## Naming

- Kebab-case, **without** a `tsh-` prefix. The plugin already namespaces it:
  `audit-page` → `/tsh-product-testing:audit-page`, never
  `/tsh-product-testing:tsh-audit-page`.
- The skill directory name *is* the skill name.
- **No framework version in the name.** `implementing-nestjs-api`, not
  `implementing-nestjs-11-api`. The name is the invocation command, so pinning a
  dependency's major forces a rename on every upgrade — breaking docs, muscle memory
  and any `enabledPlugins` entry, with no deprecation mechanism. Put the version in
  the `description` and in a **Version Baseline** block at the top of `SKILL.md` that
  tells Claude to check `package.json` and stop if the project is outside the
  supported range.
- **Keep names tech-qualified.** `implementing-nestjs-api`, not `implementing-api`.
  Namespacing makes `tsh-stack-java:implementing-api` and
  `tsh-stack-nodejs:implementing-api` both legal, but the model routes on
  descriptions, and two near-identical ones are a coin flip. This applies with extra
  force to `configuring-typescript-for-frontend` and
  `configuring-typescript-for-nodejs`, which are near-twins by design — naming the
  target is the only thing that tells them apart.
- Verbs carry meaning between related skills. `managing-` claims format and lifecycle,
  `writing-` claims prose. Two skills claiming the same artifact under the same verb
  would be a routing coin flip.

## Cross-linking

Reference bundled files as `./references/<topic>.md`, or `${CLAUDE_PLUGIN_ROOT}/…` for
files shared between skills of the same plugin.

**Never path into another plugin.** It may not be installed, and the failure is a
silent dead link rather than an error. Knowledge that must cross plugins has to be
co-located — duplicate the file, and let the copies diverge deliberately.

## Renaming is a `major` bump

The name is the invocation command and there is no deprecation mechanism. See
`/releasing-a-plugin-change`.
