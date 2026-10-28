---
name: implementing-symfony-applications
description: "Guides implementation and review of Symfony 5.4–8.x applications as a senior Symfony specialist: detects the project's Symfony version and uses only what exists in it, and justifies every framework feature it reaches for — services and DI, configuration, events, routing and controllers, Doctrine, Forms, Validator, Serializer, Security, Messenger, Console, testing. Use when writing, changing or reviewing code in a Symfony project."
when_to_use: "Trigger on: a Symfony controller, service, event listener or subscriber, Doctrine entity or repository, form type, validator constraint, normalizer, voter or authenticator, Messenger message or handler, console command, services.yaml or config/packages change, a Symfony test; \"how do I do X in Symfony\"; upgrading or working on Symfony 5.4/6.4/7.x/8.x; FOSUserBundle, SensioFrameworkExtraBundle or other bundle questions."
---

# Implementing Symfony applications

Write and review Symfony code the way a senior Symfony specialist would: know what the
framework already provides, use the mechanism that fits the actual need, and have a
reason for every feature used. Framework-independent design — patterns, SOLID, YAGNI,
refactoring, PSR-12 — belongs to the sibling skill
[`architecting-php-code`](../architecting-php-code/SKILL.md); apply both.

## Version Baseline

This skill covers **Symfony 5.4 up to 8.x**. Many APIs were added, deprecated or
removed between those versions, so before writing or reviewing anything, determine the
project's Symfony version — read
[`symfony-version-detection.md`](./references/symfony-version-detection.md) **now** —
and state it in one line together with the PHP version. If it cannot be determined,
**ask the user**.

Then use only what exists in that version:

- on an **older** version, work with what that version has (annotations, Guard, a
  bundle that later disappeared) — do not write code for a newer version;
- on a **newer** version, never introduce an API that was removed — check
  [`symfony-version-differences.md`](./references/symfony-version-differences.md);
- for third-party bundles (FOSUserBundle, SensioFrameworkExtraBundle, …) check
  [`third-party-bundles.md`](./references/third-party-bundles.md) for the Symfony
  versions each supports and its native replacement.

Do not upgrade Symfony, PHP or a bundle unless the user asks for it.

## Applicability and Precedence

Read the project's own conventions first: `AGENTS.md`/`CLAUDE.md`, `config/`
(format and layout), `composer.json`, the directory structure and how neighbouring
features are built. Local conventions outrank this skill; apply its defaults where the
project is silent, and name a deliberate deviation instead of mixing styles.

## Non-negotiable Rules

| Severity | Rule |
| --- | --- |
| MUST | State the detected Symfony and PHP versions before writing code; ask when they cannot be determined. |
| NEVER | Use an API, attribute or bundle that does not exist in the project's Symfony version, or one removed in it. |
| MUST | Reuse what the project and the framework already provide — an existing service, listener, voter, normalizer, constraint — before writing a new one. |
| MUST | Have a stated reason for every framework feature used (event, Messenger, compiler pass, decorator, voter, custom normalizer…). If a plain service method call does the job, use that. |
| NEVER | Add a bundle or Composer package when the framework or an installed package already covers the need. |
| MUST | Keep controllers thin: map the request, call a service, return a response. Business rules live in services or entities, never in controllers, listeners or Doctrine lifecycle callbacks. |
| NEVER | Fetch services from the container at runtime (`$container->get()`, `ContainerAwareInterface`); inject dependencies through the constructor. |
| MUST | Validate external input at the boundary and check authorization with the Security component (voters, `IsGranted`/`isGranted`), never with ad-hoc role-string checks scattered through services. |
| NEVER | Call `flush()` inside loops or from deep inside domain code; flush once per use case at the application boundary. |
| MUST | Follow PSR-12 and the project's coding standard; the PHP version rules of `architecting-php-code` apply here too. |

## Reference Loading

| Reference | Load when | Covers |
| --- | --- | --- |
| [Version detection](./references/symfony-version-detection.md) | Always, before writing or reviewing code | Working rules: where to read the version, conflicts, when to ask, target line, adapting to the version; release and support table, minor and major upgrades |
| [Version differences](./references/symfony-version-differences.md) | Using any API that may differ between 5.4 and 8.x, or working in a legacy project | Removals per major version, legacy pattern → replacement table |
| [Third-party bundles](./references/third-party-bundles.md) | The project uses, or you consider, a third-party bundle | Supported Symfony ranges, abandoned bundles, native replacements |
| [Dependency injection and services](./references/dependency-injection-and-services.md) | Adding or wiring a service | Autowiring, tags, iterators, decoration, locators, lazy services, factories, compiler passes |
| [Configuration and environments](./references/configuration-and-environments.md) | Touching `config/`, env vars, secrets or bundles | Config formats per version, env processors, secrets, kernel |
| [Events and kernel](./references/events-and-kernel.md) | Reacting to framework or domain events | Event dispatcher, listeners vs subscribers, HttpKernel lifecycle, Contracts |
| [HTTP layer](./references/http-layer.md) | Adding routes, controllers or request mapping | Routing, controllers, value resolvers, `Map*` attributes, error handling |
| [Doctrine persistence](./references/doctrine-persistence.md) | Entities, repositories, queries or migrations | Mapping, associations and joins, flush discipline, batching, pagination, Doctrine events, migrations, ORM 2 vs 3 |
| [Forms and validation](./references/forms-and-validation.md) | Forms, input validation or constraints | Forms vs request mapping, transformers, custom constraints, groups |
| [Serializer and request mapping](./references/serializer-and-request-mapping.md) | JSON input/output or normalizers | Serializer, groups, context, custom normalizers, DTO mapping per version |
| [Templates, translation, cache and utilities](./references/templates-translation-cache-and-utilities.md) | Twig, translations, sessions, cache, Uid, String | When each fits and its pitfalls |
| [Security](./references/security.md) | Authentication, authorization, passwords, CSRF | Authenticators per version, voters, access control, `IsGranted` |
| [Messenger and async](./references/messenger-and-async.md) | Async work, queues, scheduling, locks, mail, workflow | Messenger, Scheduler, Lock, Mailer, Notifier, Workflow, Webhook |
| [Console, HTTP client and operations](./references/console-http-client-and-operations.md) | Commands, outgoing HTTP, logging, deployment, performance | Console per version, HttpClient, logging, HTTP cache |
| [Testing](./references/testing.md) | Writing or reviewing tests | Unit vs kernel vs web tests, container overrides, HttpClient mocks, Messenger, Mailer and console assertions, test database |
| [Review checklist](./references/symfony-review-checklist.md) | Reviewing Symfony code | Severity-tagged checks per area |

## Procedure

```text
- [ ] Step 1: Symfony and PHP versions stated
- [ ] Step 2: Existing code and framework features checked for reuse
- [ ] Step 3: Mechanism chosen, with its reason
- [ ] Step 4: Code written for the detected versions
- [ ] Step 5: Verified with the project's own tools
```

**Step 1 — Versions.** Follow
[`symfony-version-detection.md`](./references/symfony-version-detection.md) and print,
for example, `Target: Symfony 5.4, PHP 8.1 (composer.lock)`.

**Step 2 — Reuse first.** Search the project for an existing service, listener,
voter, normalizer, constraint or command that already does the job, and check whether
the framework covers it natively. If so, use it and stop there.

**Step 3 — Choose the mechanism.** Read the reference for the area **before writing
code** — for example, read [`http-layer.md`](./references/http-layer.md) before writing
any controller. Pick the simplest mechanism that fits, and write down why it is needed.
"It's the Symfony way" is not a reason on its own.

**Step 4 — Write it.** Use the configuration format and attribute or annotation style
the project already uses, as far as its version allows. Keep it minimal: no unused
options, no speculative configuration, no extension points nobody asked for.

**Step 5 — Verify.** Run what the project has: `bin/console lint:container`,
`debug:router`, `debug:autowiring`, the test suite, static analysis and the coding
standard checker. Report what ran and what failed.

## Review Procedure

Load [`symfony-review-checklist.md`](./references/symfony-review-checklist.md), apply
only the checks relevant to the changed files, and check every API used against the
detected version first. Report findings by severity with file and line, the rule
broken, the consequence and the smallest fix. Say plainly when nothing was found.

## Related Skills

- [`architecting-php-code`](../architecting-php-code/SKILL.md) — ships in this
  plugin. PHP version rules, design principles, patterns, refactoring, PSR-12.
- `tsh-product-engineering` — TSH's framework-independent implementation and review
  workflows. Optional; may not be installed.
