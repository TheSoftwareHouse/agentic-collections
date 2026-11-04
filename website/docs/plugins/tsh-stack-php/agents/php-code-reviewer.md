---
title: php-code-reviewer
sidebar_label: php-code-reviewer
sidebar_position: 1
description: Read-only reviewer for PHP and Symfony changes that checks version correctness, necessity, reuse, simplicity, design and PSR-12, and runs the project's own checks.
sources:
  - plugins/tsh-stack-php/agents/php-code-reviewer.md
sources_hash: "aea4b7cc856d0a7bb65e468176636b2d1e783800048b5ce96c2e401a4851d486"
---

# php-code-reviewer

**Plugin:** [tsh-stack-php](/docs/plugins/tsh-stack-php/)  
**Mention:** `@tsh-stack-php:php-code-reviewer`  
**Model:** `opus`  
**Tools:** no `tools` allowlist; `disallowedTools: Write, Edit`  
**Preloaded skills:** [architecting-php-code](/docs/plugins/tsh-stack-php/skills/architecting-php-code),
[implementing-symfony-applications](/docs/plugins/tsh-stack-php/skills/implementing-symfony-applications)

Reviews PHP and Symfony code changes against the project's PHP and Symfony versions, PSR-1 and
PSR-12, YAGNI, KISS, DRY and SOLID, justified use of patterns and framework features, and reuse of
what the codebase already has. It runs the project's linters and static analysis and returns a
structured findings report. It does not fix code: it reports, and the caller decides what to change.

Use it after PHP code is written or changed, before merge, or when asked to review PHP or Symfony
code.

## Responsibilities

| Area                | What the agent does                                                                                                                                                                                                          |
| :------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Scope**           | Expects the delegation to name the change set: a list of files, a branch, a diff or a commit range. If it cannot determine what changed, it says so and reviews nothing rather than guessing a scope.                        |
| **Versions**        | Determines the target PHP version, and the Symfony version in a Symfony project, using the version-detection references of the two preloaded skills, and states both in the report. A finding that ignores the versions is wrong. |
| **Context**         | Opens the changed files and the code they call and are called by, because a review of a diff alone misses duplication and reinvention.                                                                                       |
| **Lenses**          | Applies six lenses in order: version correctness, necessity (YAGNI), reuse, simplicity (KISS), design, coding standard. It loads the references each skill's Reference Loading table names for the area.                      |
| **Project checks**  | Runs the project's own checks in check-only mode: the coding standard tool (`phpcs`, `php-cs-fixer --dry-run`, `ecs check`), PHPStan or Psalm, and the tests for the changed area. It never runs a command that modifies files. |
| **Unclear intent**  | Reports only what it has located in the code. If the intent behind something is unclear, it raises a question, not a defect.                                                                                                 |

If the PHP or Symfony version cannot be determined, that is the first finding, and the review
proceeds against the lowest version the code could run on.

## What it returns

1. **Target.** PHP and Symfony versions and where each was read from.
2. **Verdict.** Approve, or changes needed, in one line.
3. **Findings**, ordered blocker, major, minor. Each has `file:line`, the rule broken (and the PSR
   section for style findings), the consequence and the minimum correction. Repeats of the same rule
   are consolidated.
4. **Checks executed.** Every command run, verbatim, with pass or fail and the relevant failure
   output.
5. **What passed.** Brief. A clean review reports zero findings plainly; the agent never invents
   issues to seem thorough.

## Used by

No skill in `plugins/` delegates to this agent.

## Related

- [architecting-php-code](/docs/plugins/tsh-stack-php/skills/architecting-php-code), the PHP version
  rules, design principles and PSR-12 reference the agent applies.
- [implementing-symfony-applications](/docs/plugins/tsh-stack-php/skills/implementing-symfony-applications),
  the Symfony version rules and the review checklist the agent applies.

## Source

[`plugins/tsh-stack-php/agents/php-code-reviewer.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/agents/php-code-reviewer.md)
