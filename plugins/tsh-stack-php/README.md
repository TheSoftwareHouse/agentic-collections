# TSH Stack: PHP

TSH conventions for PHP 7.4–8.5 and Symfony 5.4–8.x — version-aware design and
implementation, framework guidance with its version differences, and a code reviewer
agent.

This is a **stack** plugin, not a discipline plugin. Install it into the projects that
run on PHP, at `project` scope, so it travels with the repo — the repo already knows
what it runs on. Your discipline plugin (`tsh-product-engineering` and friends)
travels with **you**, at `user` scope, and so does `tsh-core`.

## Install

```shell
/plugin marketplace add TheSoftwareHouse/agentic-collections
/plugin install tsh-stack-php@tsh-agentic-collections
```

## What's in it

| Component | Invoke | Covers |
| :-- | :-- | :-- |
| `architecting-php-code` skill | `/tsh-stack-php:architecting-php-code` | Senior PHP architect: detects the project's PHP version and uses only its features; the minimum code that solves the task, reuse before writing, YAGNI and KISS first; SOLID and DRY with judgement; GoF and Fowler's enterprise patterns only when a present need justifies them; architecture styles with their costs; code smells and refactoring; PSR-1 and PSR-12 |
| `implementing-symfony-applications` skill | `/tsh-stack-php:implementing-symfony-applications` | Senior Symfony specialist: detects the project's Symfony version and uses only what exists in it; services and DI, configuration, events, HTTP layer, Doctrine, Forms, Validator, Serializer, Security, Messenger, Console, testing; version differences 5.4 → 8.x and third-party bundle support (FOSUserBundle, SensioFrameworkExtraBundle, …) |
| `php-code-reviewer` agent | `@tsh-stack-php:php-code-reviewer` | Read-only review of a PHP or Symfony change: version correctness, unnecessary code, reuse, simplicity, design, PSR-12, plus the project's own linters, static analysis and tests, returned as a findings report |

Both skills are model-invocable — Claude loads them when the work matches their
description. They are designed to work together: `implementing-symfony-applications`
builds on the PHP version rules and design principles of `architecting-php-code`, and
links to it directly. The reviewer agent preloads both.

See [`CHANGELOG.md`](CHANGELOG.md) for what changed in each version. Updates arrive
with `/plugin update`.

## Version support

| | Supported | When the project's version cannot be determined |
| :-- | :-- | :-- |
| PHP | 7.4 – 8.5 | The skill asks |
| Symfony | 5.4 – 8.x | The skill asks |

Older versions are worked with as they are — the skills never upgrade PHP, Symfony or a
bundle unless asked.

## Not covered yet

Deliberate gaps, so they read as scope rather than oversight:

- **Laravel and other frameworks** — no skill of their own; `architecting-php-code`
  still applies to the PHP underneath them.
- **API Platform** — mentioned for version support only; no implementation guidance.
- **PHP below 7.4 and Symfony below 5.4** — outside the supported range.

## Scope

The routing question for this plugin is *would this guidance change if the project
switched language or framework?* If yes, it belongs here. If it would change when the
**reader** switched job, it belongs in a discipline plugin instead.

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

Two rules that bite hardest here:

- **Skill names carry no framework version.** Version ranges live in the
  `description` and in each skill's Version Baseline block.
- **Reference only files inside this plugin**, by relative path. A skill cannot
  reliably read another plugin's files, because that plugin may not be installed.
