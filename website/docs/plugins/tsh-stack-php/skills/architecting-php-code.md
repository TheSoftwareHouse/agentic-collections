---
title: architecting-php-code
sidebar_label: architecting-php-code
sidebar_position: 1
description: Design, implementation and review of PHP 7.4–8.5 code as a senior architect — least code, YAGNI and KISS first, justified patterns, refactoring, PSR-12.
sources:
  - plugins/tsh-stack-php/skills/architecting-php-code/SKILL.md
  - plugins/tsh-stack-php/skills/architecting-php-code/references/
sources_hash: "5b2a9513cc5416f59c150df3a482f79087d4353963359990c07df9703f5a5f41"
---

# architecting-php-code

**Plugin:** [tsh-stack-php](/docs/plugins/tsh-stack-php/)  
**Invoke:** `/tsh-stack-php:architecting-php-code`. Claude also loads it when the work matches its
description.  
**Used by:** the [php-code-reviewer](/docs/plugins/tsh-stack-php/agents/php-code-reviewer) agent,
which preloads it. [implementing-symfony-applications](/docs/plugins/tsh-stack-php/skills/implementing-symfony-applications)
builds on its PHP version rules and design principles.

Design, write and review PHP code the way a senior architect would: solve the actual task with the
least code that works, reuse what the system already has, and add structure only when a present need
forces it. The skill's premise is that the best code is the code that was never written.

Framework features (the Symfony container, events, Doctrine, Messenger, Security) belong to the
sibling skill `implementing-symfony-applications`. This skill owns the design decisions underneath
them.

## Version baseline

The skill covers **PHP 7.4 up to 8.5**. Before writing or reviewing a line, it determines the
project's target PHP version and states it in one line, for example
`Target: PHP 7.4 (composer.json config.platform.php)`. If the version cannot be determined, it asks
the user and never assumes the newest version. It then uses only syntax and functions that exist in
that version: on 7.4 there are no enums, no constructor promotion, no `match`, no attributes and no
`readonly`. It treats PHP 8.6 as unreleased and never targets it.

The project's own conventions come first: `AGENTS.md` or `CLAUDE.md`, the coding standard config
(`phpcs.xml`, `.php-cs-fixer.php`, `ecs.php`), the PHPStan or Psalm level, and how neighbouring code
is structured. Local rules outrank the skill, which applies its defaults where the repository is
silent.

## What it covers

| Area                                  | Coverage                                                                                                                                                                                                               |
| :------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **PHP version detection**             | Loaded always, before writing or reviewing. Where to read the version (`composer.json` `config.platform.php`, then `require.php`, then `composer.lock`, Docker files, `.php-version` or `.tool-versions`, the CI matrix, `php -v`), conflicts between sources, when to ask, Composer constraints, Docker tags, `setup-php` values, support and end-of-life status. |
| **PHP feature availability**          | Feature, minimum version and fallback for older versions, with the breaking changes of each version, from 7.4 to 8.5, and the Symfony polyfills that backport newer features.                                           |
| **Design principles**                 | SOLID, YAGNI, KISS, DRY, the wrong abstraction, replacing inheritance with delegation, Tell Don't Ask, the four rules of simple design.                                                                                |
| **Clean code**                        | Small functions, guard clauses, flag arguments, value objects, immutability, exceptions versus results, null handling, type declarations, `strict_types`.                                                              |
| **Code smells**                       | Smells grouped as bloaters, object-orientation abusers, change preventers, dispensables, couplers and others: their signs, why each hurts and the refactorings that fix it.                                            |
| **Refactoring catalog**               | Refactoring names and target shapes, PHP before and after examples, characterization tests, parallel change, branch by abstraction, strangler fig, deprecating public APIs.                                            |
| **Creational and structural patterns** | Factory, builder, adapter, decorator, facade, proxy, composite and related patterns: intent, when to use, pros and cons, pitfalls, and where PHP and Symfony already provide the pattern.                              |
| **Behavioral patterns**               | Strategy, command, observer, state, chain of responsibility, template method and related patterns, with an admission rule that says when a pattern is overkill, and the PHP and Symfony features that already provide them.                         |
| **Enterprise patterns**               | Transaction Script versus Domain Model, Active Record versus Data Mapper, Unit of Work, Query Object and Repository, concurrency and session state.                                                                    |
| **Architecture styles**               | Layered, hexagonal, clean, onion, CQRS, event-driven, event sourcing, modular monolith, microservices, vertical slices and DDD: the cost of each, when it is justified, patterns to reject and a decision guide that adds structure on an observed signal. |
| **Coding standard**                   | PSR-1 and PSR-12 rule by rule, PER Coding Style for syntax PSR-12 does not cover, and the checking tools PHP_CodeSniffer, PHP-CS-Fixer and Easy Coding Standard.                                                       |

## Non-negotiable rules

| Severity | Rule                                                                                                                                       |
| :------- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| MUST     | Answer the four questions of Step 2 before writing code, each backed by a search of the codebase.                                          |
| MUST     | Reuse an existing class, service, function or library that already does the job.                                                           |
| NEVER    | Write code for a need that does not exist today: no "for later" parameters, interfaces with one implementation, extension points, config switches or generic base classes. |
| NEVER    | Add a Composer dependency for what a few lines of code or an already-installed package can do.                                             |
| MUST     | Choose the simplest design that works, and add a pattern or layer only when a concrete, present problem can be named.                      |
| MUST | Make the code self-explanatory through names, small functions and types. No comments that restate what the code does. |
| NEVER    | Duplicate logic. A third copy is the signal to extract.                                                                                    |
| MUST     | Use only language features available in the project's PHP version, and follow PSR-1 and PSR-12 unless the repository's standard differs.   |
| NEVER    | Change behaviour while refactoring. Refactor in small steps behind passing tests, with a characterization test first when none exists.     |

## How it works

1. **State the target version.** Follow the version-detection reference and print one line.
2. **Ask the four questions, and search before answering.** Is this code needed for the task as
   stated? Does the system already do this, or something close enough to extend? Is there an existing
   service, helper or installed package to call instead? What is the smallest change that fully
   solves it? If something already does it, use it and stop.
3. **Choose the design.** Start with the plainest form: a method on the class that owns the data,
   then a small dedicated class. Before introducing a pattern or layer, write down the present
   problem it solves. No problem, no pattern. When principles pull in different directions, YAGNI
   and KISS win over SOLID or DRY applied to variation or duplication that does not exist yet.
4. **Write it once.** Write the code directly in its final form, to the target version and the
   coding standard, without a throwaway first draft.
5. **Self-review.** Confirm the diff holds nothing the task did not need, check it against the code
   smells and the coding standard, and run the project's own linters and static analysis if they
   exist.

### Review procedure

When reviewing PHP code the skill applies the same lenses in order: correct for the target PHP
version, unnecessary code (YAGNI), duplication or reinvention of something that exists, needless
complexity (KISS), design principles and smells, then PSR-12. Every finding gives the file and line,
the rule it breaks, the consequence and the smallest fix. A clean review says so plainly.

## Related skills

- [implementing-symfony-applications](/docs/plugins/tsh-stack-php/skills/implementing-symfony-applications),
  which ships in this plugin: Symfony 5.4–8.x framework features and their version differences.
- [tsh-product-engineering](/docs/plugins/tsh-product-engineering/), TSH's framework-independent
  implementation, debugging and review workflows. Optional; it may not be installed.

## Source

- [`SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/architecting-php-code/SKILL.md)
- References:
  [`php-version-detection.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/architecting-php-code/references/php-version-detection.md),
  [`php-feature-availability.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/architecting-php-code/references/php-feature-availability.md),
  [`design-principles.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/architecting-php-code/references/design-principles.md),
  [`clean-code.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/architecting-php-code/references/clean-code.md),
  [`code-smells.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/architecting-php-code/references/code-smells.md),
  [`refactoring-catalog.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/architecting-php-code/references/refactoring-catalog.md),
  [`gof-creational-and-structural.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/architecting-php-code/references/gof-creational-and-structural.md),
  [`gof-behavioral.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/architecting-php-code/references/gof-behavioral.md),
  [`enterprise-patterns.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/architecting-php-code/references/enterprise-patterns.md),
  [`architecture-styles.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/architecting-php-code/references/architecture-styles.md),
  [`coding-standard.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/architecting-php-code/references/coding-standard.md)
