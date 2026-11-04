---
paths:
  - "plugins/**"
  - "README.md"
  - "CLAUDE.md"
  - "LICENSE"
  - ".claude-plugin/marketplace.json"
  - ".claude/rules/project-context-contract.md"
---

# Plugin changes reach the website

Pages in `website/docs` list files under `plugins/`, and a few root files such as
`README.md` and `CLAUDE.md`, as their sources. Changing one can make a page stale, and
adding, renaming or removing a skill or agent needs a page added, renamed or removed.
Before committing, run `npm run docs:check` from `website/`, update every page it lists,
then re-stamp each with `npm run docs:stamp -- <page>`. The page update goes in the same
commit as the change; CI fails the build otherwise. Content rules:
`.claude/rules/website.md`.
