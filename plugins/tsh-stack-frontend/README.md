# TSH Stack: Frontend

TSH conventions for browser-targeted frontend code — TypeScript compiler
configuration for bundler-resolved applications, starting with React and Vite.

This is a **stack** plugin, not a discipline plugin. Install it into any project
with a frontend, at `project` scope, so it travels with the repo. Your discipline
plugin (`tsh-product-engineering` and friends) travels with **you**, at `user`
scope, and so does `tsh-core`.

A stack here is a **runtime target**, not a language — which is why this plugin
exists separately from `tsh-stack-nodejs`. Most TSH projects have a frontend
whatever their backend is written in, so a Go, PHP, or Java team writing React
should be able to install this without a NestJS surface arriving with it.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-stack-frontend@tsh-agentic-collections
```

## What's in it

| Skill | Invoke | Covers |
| :-- | :-- | :-- |
| `configuring-typescript-for-frontend` | `/tsh-stack-frontend:configuring-typescript-for-frontend` | Which TypeScript version to pin, the `tsconfig.json` baseline for a bundler-resolved app, the React + Vite split-config layout, typing `import.meta.env` and asset imports, path aliases that resolve in both the checker and the bundler, upgrades, and staged adoption in an existing repo |

The skill is model-invocable — Claude loads it when the work matches its
description, so you don't have to remember to type the command.

The rule it exists to enforce, if you read nothing else: **Vite does not
type-check.** `vite build` runs esbuild and Rollup, which strip types without
reading them, so a frontend repo can ship type errors indefinitely while every
build passes green. A real `tsc -b` step that fails CI is the single highest-value
thing in here.

See [`CHANGELOG.md`](CHANGELOG.md) for what changed in each version. Updates arrive
with `/plugin update`.

## Not covered yet

One skill, one toolchain, deliberately. The gaps are scope, not oversight:

- **Next.js, Angular, Svelte/SvelteKit, Vue/Nuxt** — the compiler-option guidance
  applies to all of them; the concrete layout is Vite-specific. Per-toolchain
  references are the obvious next addition.
- **Component patterns, state management, styling** — not compiler configuration.
- **Testing, linting, formatting** setup.
- **Type modelling** — unions, branded types, `unknown` over `any`. This left with
  the old `typescript-conventions` skill and will return as its own skill rather than
  being duplicated per target.

The plugin ships with one skill rather than waiting for a full set, because an
installable plugin with real content beats an empty placeholder in the Discover tab.

## Scope

The routing question for this plugin is *would this guidance change if the project
switched runtime target or framework?* If yes, it belongs here. If it would change
when the **reader** switched job, it belongs in a discipline plugin instead.

Server-side code is out of scope by construction, including the Node-executed
build-time files in a frontend repo — the skill covers how to *isolate* them in
their own `tsconfig`, not how to configure a Node service. That is
`tsh-stack-nodejs`.

## Contributing

Add a skill as `skills/<skill-name>/SKILL.md`, with supporting detail in
`skills/<skill-name>/references/<topic>.md`. Start from
[`templates/SKILL.md`](../../templates/SKILL.md) and read
[`CLAUDE.md`](../../CLAUDE.md) for the conventions and the local test loop.

Shipping a change means bumping `version` in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) and adding a
[`CHANGELOG.md`](CHANGELOG.md) entry in the same commit — without the bump,
`/plugin update` tells teammates they are already up to date and your change never
reaches them.

Three rules that bite hardest here:

- **Skill names carry no framework version.** `configuring-typescript-for-frontend`,
  not `configuring-typescript-5-for-frontend`. The name is the invocation command, so
  pinning a major forces a rename on every upgrade. Put the version in the
  `description` and in a **Version Baseline** block in `SKILL.md`.
- **Reference only files inside this plugin**, by relative path. A skill cannot
  reliably read another plugin's files, because that plugin may not be installed —
  and the failure is a silent dead link, not an error. This plugin is installed by
  teams whose backend is not JavaScript at all, so it must stand alone.
- **`configuring-typescript-for-frontend` has a near-twin** in `tsh-stack-nodejs`.
  Version policy, the strictness ladder, and the upgrade procedure exist in both, on
  purpose, because they cannot be linked across plugins. When you change one, check
  the other in the same PR — and let the target-specific parts stay different. A
  frontend reference that starts recommending `emitDecoratorMetadata` has been copied
  without being read.
