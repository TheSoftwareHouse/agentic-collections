---
name: audit-page
description: Runs an accessibility audit against a page or component and reports WCAG 2.2 AA violations. Use when asked to check accessibility, verify a11y before release, or interpret axe output.
---

# Audit page accessibility

Audit the target described in `$ARGUMENTS`. If no target is given, ask which page,
component, or flow to audit before doing anything else.

## Steps

1. Locate the markup or component source for the target.
2. Check semantic structure, keyboard operability, focus management, contrast, and
   accessible names.
3. Report each violation with its WCAG success criterion, the offending element,
   reproduction steps, and the fix.

## Reporting

Order findings by severity. State clearly when nothing was found.

<!--
=============================================================================
TEMPLATE NOTES — delete everything below this line in your real skill file.
=============================================================================

A skill is a DIRECTORY, not a loose file. Copy this to:

    plugins/<plugin>/skills/<skill-name>/SKILL.md

The directory name becomes the skill name. Alongside SKILL.md you may add:

    plugins/<plugin>/skills/audit-page/
    ├── SKILL.md          <- this file
    ├── reference.md      <- optional: detail Claude loads only when needed
    └── scripts/          <- optional: helper scripts the skill can run

Name it WITHOUT the plugin prefix. Plugin skills are namespaced automatically:

    /tsh-product-testing:audit-page

`description` is what Claude reads to decide whether to invoke the skill on its
own. Include both what it does and when to use it.

`$ARGUMENTS` interpolates whatever the user typed after the skill name, e.g.
`/tsh-product-testing:audit-page checkout page` puts "checkout page" there.

Add `disable-model-invocation: true` to the frontmatter if the skill should only
ever run when a human types it, never when Claude decides to use it.

Keep SKILL.md short. Everything in it is loaded into context when the skill runs;
push long detail into `reference.md` and tell Claude to read it when relevant.

Docs: https://code.claude.com/docs/en/skills
-->
