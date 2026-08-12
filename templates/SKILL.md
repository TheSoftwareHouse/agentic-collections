---
name: audit-page
description: Runs an accessibility audit against a page or component and reports WCAG 2.2 AA violations. Use when asked to check accessibility, verify a11y before release, or interpret axe output.
---

# Audit page accessibility

Audit the target described in `$ARGUMENTS`. If no target is given, ask which page,
component, or flow to audit before doing anything else.

## Applicability and Precedence

Read the repository's own accessibility conventions first. Local rules outrank
this skill's defaults; apply these where the repo is silent, and record any
deliberate deviation rather than silently mixing conventions.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Report the WCAG success criterion for every finding, not just a description. |
| NEVER | Report a violation you have not located in the source or reproduced. |
| MUST | State plainly when nothing was found. Do not pad a clean audit with speculation. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Keyboard and focus](./references/keyboard-and-focus.md) | The target has interactive controls, dialogs, or custom widgets | Tab order, focus traps, visible focus, roving tabindex |
| [Names and semantics](./references/names-and-semantics.md) | Auditing markup structure or ARIA usage | Landmarks, heading order, accessible names, when ARIA is wrong |
| [Contrast and motion](./references/contrast-and-motion.md) | The change is visual, or involves animation | Contrast ratios, reduced-motion, non-colour indicators |

## Steps

1. Locate the markup or component source for the target.
2. Load the references relevant to what changed — read
   [`keyboard-and-focus.md`](./references/keyboard-and-focus.md) before auditing
   any interactive control.
3. Check semantic structure, keyboard operability, focus management, contrast, and
   accessible names.
4. Report each violation with its WCAG success criterion, the offending element,
   reproduction steps, and the fix.

## Reporting

Order findings by severity. State clearly when nothing was found.

<!--
=============================================================================
TEMPLATE NOTES — delete everything below this line in your real skill file.
=============================================================================

A skill is a DIRECTORY, not a loose file. Copy this to:

    plugins/<plugin>/skills/<skill-name>/SKILL.md

The directory name becomes the skill name. The full shape:

    plugins/<plugin>/skills/audit-page/
    ├── SKILL.md                       <- this file; keep it under ~150 lines
    ├── references/                    <- detail, loaded only when needed
    │   ├── keyboard-and-focus.md      <- one concern per file, <=300 lines
    │   └── names-and-semantics.md
    └── scripts/                       <- optional: helper scripts the skill runs

Name it WITHOUT the plugin prefix. Plugin skills are namespaced automatically:

    /tsh-product-testing:audit-page

-- Progressive disclosure -----------------------------------------------------

Everything in SKILL.md enters context every time the skill runs; references cost
nothing until read. So SKILL.md carries only: frontmatter, applicability and
precedence, the non-negotiable rules table, the Reference Loading table, and the
procedure. Everything else goes in references/.

TWO THINGS MAKE THIS ACTUALLY WORK, and both are easy to leave out:

1. The Reference Loading table needs its "Load when" column. A bare list of links
   gets skimmed and ignored; a trigger condition per row gives the model a
   predicate to evaluate. Then ALSO give an imperative at the point of use --
   "read ./references/x.md before writing any controller". Instruction-following
   beats table lookup, and the two reinforce each other.

2. A rule that blocks review belongs in SKILL.md even if a reference explains it
   too. SKILL.md is what's in context when the model reads no references at all.

-- Linking rules --------------------------------------------------------------

Write full relative paths from the file you are in:

    from SKILL.md          ->  ./references/<topic>.md
    between two references ->  ./<sibling>.md
    another skill, same plugin -> ../<other-skill>/SKILL.md

Never a bare filename in backticks -- the model has to guess the directory.
Never a path into ANOTHER plugin: it may not be installed, and the failure is a
silent dead link. ${CLAUDE_PLUGIN_ROOT} and ${CLAUDE_SKILL_DIR} are substituted
in plugin skill markdown if you need an absolute path within your own plugin.

-- Frontmatter ----------------------------------------------------------------

`description` is what Claude reads to decide whether to invoke the skill on its
own. Include both what it does and when to use it. `description` + `when_to_use`
are truncated together at 1,536 characters in the skill listing, so lead with the
key use case.

`when_to_use`      -- extra trigger phrases, appended to description in the listing.
`paths`            -- globs that limit AUTOMATIC activation, e.g. ["**/*.ts"].
                      Explicit /invocation still works everywhere.
`disable-model-invocation: true` -- human-only; Claude never loads it on its own.
`user-invocable: false`          -- background knowledge, hidden from the / menu.
`allowed-tools`    -- tools pre-approved for the turn that invokes the skill.

`$ARGUMENTS` interpolates whatever the user typed after the skill name, e.g.
`/tsh-product-testing:audit-page checkout page` puts "checkout page" there.

-- Versions -------------------------------------------------------------------

Skill names carry NO framework version: `implementing-nestjs-api`, never
`implementing-nestjs-11-api`. The name is the invocation command, and renaming
breaks docs, muscle memory and enabledPlugins entries with no deprecation path.
Put the version in `description` plus a Version Baseline block near the top of
SKILL.md that tells Claude to check package.json and STOP if the project is
outside the supported range.

Docs: https://code.claude.com/docs/en/skills
-->
