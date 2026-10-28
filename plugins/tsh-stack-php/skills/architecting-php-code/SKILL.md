---
name: architecting-php-code
description: "Guides design, implementation and review of PHP 7.4–8.5 code as a senior architect: the minimum code that solves the task, YAGNI and KISS first, SOLID and DRY applied with judgement, enterprise and design patterns only when a current need justifies them, refactoring, architecture choices, and PSR-12 style. Use when writing, refactoring or reviewing PHP classes, choosing a design pattern or architecture, or checking PSR-12."
when_to_use: "Trigger on: adding a PHP class, service or abstraction; \"which pattern should I use\"; replacing a long if/switch; extracting or merging code; refactoring a legacy PHP module; deciding between layered, hexagonal, CQRS or a modular monolith; Active Record vs Data Mapper; reviewing PHP code for SOLID, duplication, over-engineering or PSR-12; writing PHP that must run on an older PHP version."
---

# Architecting PHP code

Design, write and review PHP code the way a senior architect would: solve the actual
task with the least code that works, reuse what the system already has, and add
structure only when a present need forces it. **The best code is the code that was
never written.**

Framework features — the Symfony container, events, Doctrine, Messenger, Security —
belong to the sibling skill
[`implementing-symfony-applications`](../implementing-symfony-applications/SKILL.md).
This skill owns the design decisions underneath them.

## Version Baseline

This skill covers **PHP 7.4 up to 8.5**. Before writing or reviewing a single line,
determine the project's target PHP version — read
[`php-version-detection.md`](./references/php-version-detection.md) **now** — and
state it in one line. If it cannot be determined, **ask the user**; never assume the
newest version.

Then use only syntax and functions that exist in that version. Check every feature
against [`php-feature-availability.md`](./references/php-feature-availability.md):
on 7.4 there are no enums, no constructor promotion, no `match`, no attributes, no
`readonly`. PHP 8.6 is not released — never target it.

## Applicability and Precedence

Read the repository's own conventions first: `AGENTS.md`/`CLAUDE.md`, the coding
standard config (`phpcs.xml`, `.php-cs-fixer.php`, `ecs.php`), PHPStan/Psalm level,
and how neighbouring code is structured. Local rules outrank this skill; apply its
defaults where the repo is silent, and name a deliberate deviation instead of mixing
conventions.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | Before writing code, answer the four questions in Step 2. Write nothing until each has an answer backed by a search of the codebase. |
| MUST | Reuse an existing class, service, function or library that already does the job. Never write a second implementation of something the system has. |
| NEVER | Write code for a need that does not exist today (YAGNI): no "for later" parameters, interfaces with one implementation, extension points, config switches or generic base classes. |
| NEVER | Add a Composer dependency for what a few lines of code or an already-installed package can do. A new dependency needs a stated reason. |
| MUST | Choose the simplest design that works (KISS). Add a pattern or layer only when you can name the concrete, present problem it solves; say which pattern and why. |
| MUST | Make the code self-explanatory through names, small functions and types. No comments that restate what the code does. |
| NEVER | Duplicate logic. A third copy is the signal to extract; two similar-looking pieces with different reasons to change stay separate. |
| MUST | Use only language features available in the project's PHP version. |
| MUST | Follow PSR-1 and PSR-12 (PSR-2 is deprecated and superseded by PSR-12), unless the repository's own standard says otherwise. |
| NEVER | Change behaviour while refactoring. Refactor in small steps behind passing tests; write a characterization test first when none exists. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [PHP version detection](./references/php-version-detection.md) | Always, before writing or reviewing code | Working rules: where to read the version, conflicts, when to ask, target line, adapting to the version; Composer, Docker and CI details, support and EOL status |
| [PHP feature availability](./references/php-feature-availability.md) | Using any syntax or function newer than PHP 7.4 | Feature → minimum version → fallback for older versions; BC breaks per version |
| [Design principles](./references/design-principles.md) | Deciding how to structure a class or module, or justifying an abstraction | SOLID, YAGNI, the wrong abstraction, delegation over inheritance, Tell Don't Ask, the four rules of simple design |
| [Clean code](./references/clean-code.md) | Writing or reviewing any function or class | Small functions, guard clauses, flag arguments, value objects, immutability, exceptions vs results, nulls, types, `strict_types` |
| [Code smells](./references/code-smells.md) | Reviewing code or deciding whether to refactor | The 23 smells by group, their signs, why each hurts, the refactorings that fix it |
| [Refactoring catalog](./references/refactoring-catalog.md) | Changing structure without changing behaviour | Refactoring names and target shapes, PHP before/after, characterization tests, parallel change, branch by abstraction, strangler fig |
| [Creational and structural patterns](./references/gof-creational-and-structural.md) | Considering a factory, builder, adapter, decorator, facade, proxy or composite | Intent, when to use, pros and cons, pitfalls, PHP and Symfony notes |
| [Behavioral patterns](./references/gof-behavioral.md) | Replacing conditionals, or considering strategy, command, observer, state, chain, template method | Same, plus where PHP and Symfony already provide the pattern |
| [Enterprise patterns](./references/enterprise-patterns.md) | Choosing how domain logic or persistence is organised | Transaction Script vs Domain Model, Active Record vs Data Mapper, Unit of Work, Query Object and Repository |
| [Architecture styles](./references/architecture-styles.md) | Deciding module or application structure | Layered, hexagonal, CQRS, event-driven, modular monolith, microservices, DDD — cost and when justified |
| [Coding standard](./references/coding-standard.md) | Writing PHP, and in every review | PSR-1 and PSR-12 rule by rule, PER Coding Style for newer syntax, checking tools |

## Procedure

Copy and track this checklist:

```text
- [ ] Step 1: Target PHP version stated
- [ ] Step 2: The four questions answered
- [ ] Step 3: Simplest design chosen, every abstraction justified
- [ ] Step 4: Code written to the version and the coding standard
- [ ] Step 5: Self-review done
```

**Step 1 — State the target version.** Follow
[`php-version-detection.md`](./references/php-version-detection.md) and print one line,
for example `Target: PHP 7.4 (composer.json config.platform.php)`.

**Step 2 — Ask the four questions, and search before answering.**

1. Is this code actually needed for the task as stated?
2. Does the system already do this, or something close enough to extend?
3. Is there an existing service, helper or installed package I should call instead?
4. What is the smallest change that fully solves it?

Search the codebase (class names, method names, similar strings) before answering 2
and 3. If something already does it, use it and stop there.

**Step 3 — Choose the design.** Start with the plainest form: a method on the class
that owns the data, then a small dedicated class. Before introducing a pattern or a
layer, read [`design-principles.md`](./references/design-principles.md) and the
matching pattern reference, and write down the present problem it solves. No problem,
no pattern. Prefer what the framework already provides over a hand-rolled pattern.
Apply YAGNI, KISS, DRY and SOLID **here, while designing, before any code exists**.
When they pull in different directions, YAGNI and KISS win over SOLID or DRY applied
to variation or duplication that does not exist yet.

**Step 4 — Write it once.** Write the code directly in its final form. Never write a
first draft to refactor afterwards — that spends the work twice. Refactor existing code
only when the task needs it. Use only features of the target version, follow
[`coding-standard.md`](./references/coding-standard.md), keep functions small and names
precise, and add `declare(strict_types=1);` where the project uses it.

**Step 5 — Self-review.** Confirm the diff holds nothing the task did not need: unused
parameters, speculative interfaces, dead branches, comments that restate code. If
Steps 2–4 were followed, there is nothing to remove. Check the diff
against [`code-smells.md`](./references/code-smells.md) and the coding standard. Run
the project's own linters and static analysis if they exist.

## Review Procedure

When reviewing PHP code, apply the same lenses in this order: correct for the target
PHP version → unnecessary code (YAGNI) → duplication or reinvention of something that
exists → needless complexity (KISS) → design principles and smells → PSR-12. For
every finding give the file and line, the rule it breaks, the consequence, and the
smallest fix. A clean review says so plainly; never invent findings.

## Related Skills

- [`implementing-symfony-applications`](../implementing-symfony-applications/SKILL.md)
  — ships in this plugin. Symfony 5.4–8.x framework features and their version
  differences.
- `tsh-product-engineering` — TSH's framework-independent implementation, debugging
  and review workflows. Optional; may not be installed.
