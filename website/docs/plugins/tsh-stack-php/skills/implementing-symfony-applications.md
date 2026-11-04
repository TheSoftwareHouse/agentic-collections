---
title: implementing-symfony-applications
sidebar_label: implementing-symfony-applications
sidebar_position: 2
description: Implementation and review of Symfony 5.4–8.x applications as a senior Symfony specialist — detects the project's version, uses only what exists in it, and justifies every framework feature.
sources:
  - plugins/tsh-stack-php/skills/implementing-symfony-applications/SKILL.md
  - plugins/tsh-stack-php/skills/implementing-symfony-applications/references/
sources_hash: "07ed2f4392b66fca89a790746b40ce90425a1705d13b40ffb60b24285b75a142"
---

# implementing-symfony-applications

**Plugin:** [tsh-stack-php](/docs/plugins/tsh-stack-php/)  
**Invoke:** `/tsh-stack-php:implementing-symfony-applications`. Claude also loads it when the work
matches its description.  
**Used by:** the [php-code-reviewer](/docs/plugins/tsh-stack-php/agents/php-code-reviewer) agent,
which preloads it.

Write and review Symfony code the way a senior Symfony specialist would: know what the framework
already provides, use the mechanism that fits the actual need, and have a reason for every feature
used. Framework-independent design (patterns, SOLID, YAGNI, refactoring, PSR-12) belongs to the
sibling skill [architecting-php-code](/docs/plugins/tsh-stack-php/skills/architecting-php-code), and
the two are applied together.

## Version baseline

The skill covers **Symfony 5.4 up to 8.x**. Many APIs were added, deprecated or removed between
those versions, so before writing or reviewing anything it determines the project's Symfony version
and states it together with the PHP version, for example
`Target: Symfony 5.4, PHP 8.1 (composer.lock)`. If the version cannot be determined, it asks the
user. It reads the version in this order: the installed `symfony/framework-bundle` in
`composer.lock`, `extra.symfony.require` in `composer.json`, the `symfony/framework-bundle`
constraint, `bin/console --version`, then configuration signs. When sources disagree,
`composer.lock` wins because it is what is installed.

Then it uses only what exists in that version:

- On an **older** version it works with what that version has (annotations, Guard, a bundle that
  later disappeared) and does not write code for a newer version.
- On a **newer** version it never introduces an API that was removed.
- For third-party bundles such as FOSUserBundle and SensioFrameworkExtraBundle it checks which
  Symfony versions each supports and what replaces it natively.

It does not upgrade Symfony, PHP or a bundle unless the user asks. Local conventions (`AGENTS.md` or
`CLAUDE.md`, `config/` format and layout, `composer.json`, how neighbouring features are built)
outrank the skill's defaults.

## What it covers

| Area | Coverage |
| :-- | :-- |
| **Version detection** | Loaded always, before writing or reviewing. Where to read the version, conflicts, when to ask, the target line; the release and support table, minor and major upgrades. |
| **Version differences** | Removals per major version and a table mapping each legacy pattern to its replacement. |
| **Third-party bundles** | Supported Symfony ranges, abandoned bundles and their native replacements. |
| **Dependency injection and services** | Autowiring, tags, iterators, decoration, locators, lazy services, factories, compiler passes. |
| **Configuration and environments** | Config formats per version, env var processors, secrets, the kernel, bundles. |
| **Events and kernel** | The event dispatcher, listeners versus subscribers, the HttpKernel lifecycle, Contracts. |
| **HTTP layer** | Routing, controllers, value resolvers, the `Map*` request-mapping attributes, error handling. |
| **Doctrine persistence** | Mapping, associations and joins, flush discipline, batching, pagination, Doctrine events, migrations, ORM 2 versus 3. |
| **Forms and validation** | Forms versus request mapping, data transformers, custom constraints, validation groups. |
| **Serializer and request mapping** | The Serializer, groups, context, custom normalizers, DTO mapping per version. |
| **Templates, translation, cache and utilities** | Twig, translations, sessions, cache pools and tags, Uid and String: when each fits and its pitfalls. |
| **Security** | Authenticators per version, voters, access control, `IsGranted`, passwords, CSRF. |
| **Messenger and async** | Messenger, Scheduler, Lock, Mailer, Notifier, Workflow, Webhook. |
| **Console, HTTP client and operations** | Console per version, HttpClient, logging, deployment, performance, HTTP cache. |
| **Testing** | Unit, kernel and web tests, container overrides, HttpClient mocks, Messenger, Mailer and console assertions, the test database. |
| **Review checklist** | Severity-tagged checks per area. |

## Non-negotiable rules

| Severity | Rule |
| :-- | :-- |
| MUST | State the detected Symfony and PHP versions before writing code; ask when they cannot be determined. |
| NEVER | Use an API, attribute or bundle that does not exist in the project's Symfony version, or one removed in it. |
| MUST | Reuse what the project and the framework already provide before writing a new service, listener, voter, normalizer or constraint. |
| MUST | Have a stated reason for every framework feature used. If a plain service method call does the job, use that. |
| NEVER | Add a bundle or Composer package when the framework or an installed package already covers the need. |
| MUST | Keep controllers thin. Business rules live in services or entities, never in controllers, listeners or Doctrine lifecycle callbacks. |
| NEVER | Fetch services from the container at runtime; inject dependencies through the constructor. |
| MUST | Validate external input at the boundary and check authorization with the Security component, not ad-hoc role-string checks. |
| NEVER | Call `flush()` inside loops or from deep inside domain code; flush once per use case at the application boundary. |
| MUST | Follow PSR-12 and the project's coding standard; the PHP version rules of `architecting-php-code` apply here too. |

## How it works

1. **Versions.** Detect and state the Symfony and PHP versions.
2. **Reuse first.** Search the project for an existing service, listener, voter, normalizer,
   constraint or command that already does the job, and check whether the framework covers it
   natively. If so, use it and stop.
3. **Choose the mechanism.** Read the reference for the area before writing code, for example the
   HTTP layer reference before any controller. Pick the simplest mechanism that fits and write down
   why it is needed. "It's the Symfony way" is not a reason on its own.
4. **Write it.** Use the configuration format and attribute or annotation style the project already
   uses, as far as its version allows. No unused options, speculative configuration or unrequested
   extension points.
5. **Verify.** Run what the project has: `bin/console lint:container`, `debug:router`,
   `debug:autowiring`, the test suite, static analysis and the coding standard checker, and report
   what ran and what failed.

### Review procedure

For a review the skill loads the review checklist and applies only the checks relevant to the changed
files, checking every API used against the detected version first. The checklist is grouped by area:
version correctness, necessity and reuse, services and DI, configuration, events and kernel, HTTP
layer, Doctrine, forms and validation, serializer, security, Messenger, console and HttpClient,
templates and cache, and testing. Each check carries a severity of `[BLOCKER]`, `[HIGH]`,
`[MEDIUM]` or `[LOW]`, and the report starts with the target line. Findings are grouped by severity
and give the location as `file:line`, the violated check, the consequence and the smallest fix. When
nothing is found, the report says so in one line.

## Related skills

- [architecting-php-code](/docs/plugins/tsh-stack-php/skills/architecting-php-code), which ships in
  this plugin: PHP version rules, design principles, patterns, refactoring and PSR-12.
- [tsh-product-engineering](/docs/plugins/tsh-product-engineering/), TSH's framework-independent
  implementation and review workflows. Optional; it may not be installed.

## Source

- [`SKILL.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/SKILL.md)
- References:
  - [`symfony-version-detection.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/symfony-version-detection.md)
  - [`symfony-version-differences.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/symfony-version-differences.md)
  - [`third-party-bundles.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/third-party-bundles.md)
  - [`dependency-injection-and-services.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/dependency-injection-and-services.md)
  - [`configuration-and-environments.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/configuration-and-environments.md)
  - [`events-and-kernel.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/events-and-kernel.md)
  - [`http-layer.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/http-layer.md)
  - [`doctrine-persistence.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/doctrine-persistence.md)
  - [`forms-and-validation.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/forms-and-validation.md)
  - [`serializer-and-request-mapping.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/serializer-and-request-mapping.md)
  - [`templates-translation-cache-and-utilities.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/templates-translation-cache-and-utilities.md)
  - [`security.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/security.md)
  - [`messenger-and-async.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/messenger-and-async.md)
  - [`console-http-client-and-operations.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/console-http-client-and-operations.md)
  - [`testing.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/testing.md)
  - [`symfony-review-checklist.md`](https://github.com/TheSoftwareHouse/agentic-collections/blob/main/plugins/tsh-stack-php/skills/implementing-symfony-applications/references/symfony-review-checklist.md)
