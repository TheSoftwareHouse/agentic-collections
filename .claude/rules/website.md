---
paths:
  - "website/**"
---

# The documentation site

`website/` is a Docusaurus site that describes the plugins in `plugins/`. **The plugins
are its single source of truth**: the site renders what the repository holds and its
build fails when a page and its sources disagree. Every sentence on it is backed by a
file in this repository.

## Content rule

- **Back every sentence with a file** — a plugin file, or a root file such as
  `README.md`, `CLAUDE.md` or `.claude-plugin/marketplace.json` — and list that file in
  the page's `sources:`. Editing a root file a page lists stales that page too. A fact you cannot confirm from a file stays
  in the page as `TODO(verify): <question>` and goes to the person reviewing.
- **Counts and component lists come from the catalog.** Render them with
  `<PluginComponents plugin="tsh-x" />` and `<PluginList family="core|discipline|stack" />`
  from `@site/src/components/PluginComponents`, or read
  `src/data/catalog.generated.json` in a component. A number typed into prose drifts
  the day a skill is added.
- **Write component names exactly as the source does.** Invoke a skill as
  `/<plugin>:<skill>` and mention an agent as `@<plugin>:<agent>`.
- **Marketing figures** (lead-time percentages, engineer and project counts) carry a
  `TODO(marketing)` comment; keep the figure, never invent one.
- **Narrative inherited from the Copilot Collections site** carries a
  `PHASE2(narrative): …` or `PHASE2(visual): …` comment until it is rewritten.
- Installation commands are rendered from `README.md`, the canonical copy; edit the
  README, never the generated partial.

## Page templates

Copy a sibling page in the same section. In brief:

- **Skill** (`docs/plugins/<plugin>/skills/<skill>.md`): title, **Plugin**, **Invoke**
  (the command, "loaded automatically", or "internal" for `user-invocable: false`),
  **Used by** (found by grepping the sources), What it covers, How it works, Related
  skills, Source (GitHub link to the `SKILL.md`).
- **Agent** (`docs/plugins/<plugin>/agents/<agent>.md`): title, **Plugin**,
  **Mention**, **Model** and **Tools** from its frontmatter, Responsibilities, What it
  returns, Used by, Source.
- **Plugin** (`docs/plugins/<plugin>/index.md`): what it owns, then
  `<PluginComponents>` for its skills and agents.

## The two guards

`node scripts/sync-catalog.mjs --check` runs as `prebuild`, so `npm run build` fails on
either:

- **Structure** — every skill and agent of every non-empty plugin has its page under
  `docs/plugins/<plugin>/{skills,agents}/<name>.md`, every non-empty plugin has an
  `index.md`, and no page describes a component that does not exist.
- **Freshness** — every hand-written page declares `sources:` (repo-root paths; a
  trailing `/` takes the whole directory) and `sources_hash:`, a sha256 over those
  files. A directory source hashes the files git would commit (tracked plus untracked,
  not ignored), so a stamp reproduces on a clean checkout; symbolic links are rejected. The
  homepage keeps its list in `src/components/home/sources.json`. A changed source makes the
  page stale.

**Stamp only after the content is updated.** A stale page means its sources changed:
read the diff, update the page to match, then `npm run docs:stamp -- <page>`. The new
hash in the PR diff tells the reviewer the page was re-read. Stamping without updating
turns the guard off for that page.

Without `--check` the same script generates the gitignored files the site reads:
`src/data/catalog.generated.json`, `docs/changelog/*` and
`docs/getting-started/_install.generated.md`.

## Dependencies

Every dependency is pinned to an exact version — no `^`, no `~`; `engines.node` is
`>=24`. The `overrides` block in `package.json` pins patched transitive packages that
Docusaurus does not yet ship. On every Docusaurus bump, re-check each override:
remove it once Docusaurus resolves a patched version on its own, and confirm
`npm audit --omit=dev` reports no high or critical.

## Deployment guard

`vercel.json` at the repo root runs `scripts/vercel-guard.mjs` before the build. It
refuses to build outside Vercel, in the Copilot Collections Vercel project, or from a
repository other than `agentic-collections` — that project deploys from its own repo
and must keep working. Google Tag Manager loads only when `GTM_CONTAINER_ID` is set.

## Commands

Run from `website/`:

```shell
npm ci                               # install
npm run start                        # dev server on http://localhost:3000
npm run build                        # guards, then the production build
npm run docs:check                   # both guards alone, without building
npm run docs:stamp -- <page>|--all   # re-stamp after updating a page
npm test                             # tests for both docs guards and the Vercel guard
npm run format:check                 # Prettier
npx tsc --noEmit                     # typecheck
```

CI runs `npm ci`, `npx tsc --noEmit`, `npm run format:check`, `npm test` and `npm run build`
on every pull request and push to `main`.
