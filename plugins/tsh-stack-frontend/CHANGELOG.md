# Changelog

All notable changes to `tsh-stack-frontend` are documented here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and the versions
are the `version` field in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed. Every entry below is
a released version, and its version bump landed in the same commit as the change it
describes.

Teammates receive these updates by running `/plugin update` — a change to this file
alone reaches nobody.

## [0.1.0] - 2026-08-12

Initial release. This plugin is one half of the split of `tsh-stack-typescript`,
which has been removed: a stack is now a **runtime target**, not a language. Most
TSH projects have a frontend whatever their backend is written in, so browser-side
guidance had to be installable on its own.

### Added

- `configuring-typescript-for-frontend`, covering the `tsconfig.json` baseline for a
  bundler-resolved browser app: `moduleResolution: bundler`, `jsx: react-jsx`,
  `lib: DOM`, emit owned by the bundler, explicit ambient `types`, and the
  strictness ladder.
- A `react-vite-project.md` reference for the split-config layout — a root config
  with `references`, a browser `tsconfig.app.json`, and a Node-resolved
  `tsconfig.node.json` for `vite.config.ts` — plus typing `import.meta.env` and asset
  imports, mirroring path aliases between the checker and the bundler, `@types/react`
  duplication, and adding a test-only project. Written against Vite 8 + React 19 and
  verified against `create-vite`'s current template.
- **A real type-check as a non-negotiable rule.** Vite, esbuild, and SWC strip types
  without checking them, so a frontend repo can ship type errors indefinitely while
  every build passes green. The skill treats getting a failing `tsc -b` into CI as
  the first thing to fix, ahead of any flag tuning, and the brownfield reference has
  a staged procedure for turning that gate on in a repo that has never had one.
- A brownfield posture stated as a non-negotiable rule: the baseline is a
  recommendation for new projects, and an existing `tsconfig.json` that differs from
  it is not a defect. Framework-managed configs (Next.js, Angular, Nuxt) are left
  alone.
- Version and upgrade guidance reflecting **TypeScript 6.0 and 7.0**, including the
  frontend-specific constraint that 7.0's native compiler does **not** support
  embedded-language tooling — Vue, Svelte, Astro, MDX, and Angular templates still
  require the 6.0 line, and `vue-tsc`/`svelte-check` are the real gate for those
  projects.

### Notes

Version policy, the strictness ladder, the upgrade procedure, and the brownfield
adoption material are duplicated from `tsh-stack-nodejs` on purpose: a skill cannot
read files in another plugin, so shared knowledge has to be co-located. The
target-specific parts are genuinely different, and are meant to stay that way. When
one copy changes, check the other.
