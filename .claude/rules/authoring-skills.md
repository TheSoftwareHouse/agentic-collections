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
- Changing a model-invocable skill's description means running
  `python3 scripts/lint-descriptions.py` and the routing suite, and a new skill adds a
  routing case. Commands and how to read the output: `evals/README.md`; case format:
  `.claude/rules/plugin-evals.md`.
  A pair the lint flags but that is genuinely distinct goes in `allowed_pairs` of
  `scripts/description-lint.json` as `{"a", "b", "reason"}`, with IDs in the form
  `tsh-<plugin>:<skill>` or `tsh-<plugin>:@<agent>` — and only with a routing case
  proving the two route apart.
- **One exception: user-invoked entry points.** A skill with
  `disable-model-invocation: true` is a command, not a routing surface — its
  description is never preloaded, so it cannot collide with anything. It may take a
  short imperative name (`init`), because the name is what a person types.
  Everything else here still applies: kebab-case, no `tsh-` prefix, no version, and
  renaming is still a `major` bump. A model-invocable skill never qualifies —
  dropping the flag to reclaim routing means taking a conforming name first.

## Cross-linking

Reference bundled files as `./references/<topic>.md`, or `${CLAUDE_PLUGIN_ROOT}/…` for
files shared between skills of the same plugin.

**Never path into another plugin.** It may not be installed, and the failure is a
silent dead link rather than an error. Knowledge that must cross plugins has to be
co-located — duplicate the file, and let the copies diverge deliberately.

## Renaming is a `major` bump

The name is the invocation command and there is no deprecation mechanism. See
`/releasing-a-plugin-change`.
