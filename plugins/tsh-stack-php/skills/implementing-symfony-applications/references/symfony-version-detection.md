# Symfony Version Detection

Use this reference when you need to know which Symfony version a project runs, which lines are maintained, and what changes when the project moves to another minor or major version.

## Table of Contents

- [Working Rules](#working-rules)
- [Release Model](#release-model)
- [Release and Support Table](#release-and-support-table)
- [Version Pin in composer.json](#version-pin-in-composerjson)
- [Asking the Console](#asking-the-console)
- [Choosing the Version for a New Project](#choosing-the-version-for-a-new-project)
- [Minor Upgrades](#minor-upgrades)
- [Major Upgrades](#major-upgrades)
- [Signs of Code That Breaks on 8.0](#signs-of-code-that-breaks-on-80)
- [Sources](#sources)

## Working Rules

Which Symfony solution fits depends on the Symfony version the project runs on, so the version is known before any code is written or reviewed.

1. Determine the Symfony version (major and minor) and the PHP version first, before writing, changing or reviewing any Symfony code. For PHP, follow [`php-version-detection.md`](../../architecting-php-code/references/php-version-detection.md).
2. Look in this order and stop when the version is clear: the installed version of `symfony/framework-bundle` in `composer.lock` → `extra.symfony.require` in `composer.json` → the `symfony/framework-bundle` constraint in `composer.json` → `bin/console --version` → configuration signs (for example `enable_authenticator_manager` means 5.x).
3. When sources disagree, `composer.lock` wins because it is what is installed. Report the inconsistency in one sentence; do not fix it unless asked.
4. When the version cannot be determined, ask the user. Never assume the newest version.
5. State the target in one line before the first code change, for example `Target: Symfony 5.4, PHP 8.1 (composer.lock)`.
6. On an older version, use what that version has — annotations, Guard, a bundle that later disappeared — and never an API added later. On a newer version, never use an API that was removed. Check [`symfony-version-differences.md`](./symfony-version-differences.md).
7. For every third-party bundle, read its installed version from `composer.lock` and work with that version; check [`third-party-bundles.md`](./third-party-bundles.md) for what it supports.
8. When a better solution needs a newer Symfony or bundle version, mention it as an option and do not use it. Never upgrade Symfony or a bundle unless the user asks for it.

## Release Model

- Minor versions come out every six months, in May and November. Major versions come out every two years.
- Long-term support (LTS) versions are published every two years. 7.4, 6.4 and 5.4 are LTS; 4.4 and 3.4 were LTS.
- The LTS line 7.4 has 3 year support for bugs and security fixes, but it does not include the latest features and is harder to upgrade to newer versions.
- The current stable line (8.1) is recommended for most users, includes the latest features and is easier to upgrade to newer versions.
- Bugs are fixed in the oldest maintained branch that contains them.
- Status labels on the releases page: maintained version, security fixes only, end of life version, unreleased version.

## Release and Support Table

LTS lines have separate end dates for bug fixes and security fixes. Other lines have a single end of support date.

| Version | Released | End of bug fixes | End of security fixes | LTS | Min PHP | Status |
| --- | --- | --- | --- | --- | --- | --- |
| 5.4 | Nov 2021 | Nov 2024 | Feb 2029 | yes | 7.2.5 | security fixes only |
| 6.0 | Nov 2021 | Jan 2023 | Jan 2023 | no | 8.0.2 | unmaintained |
| 6.1 | May 2022 | Jan 2023 | Jan 2023 | no | 8.1.0 | unmaintained |
| 6.2 | Nov 2022 | Jul 2023 | Jul 2023 | no | 8.1.0 | unmaintained |
| 6.3 | May 2023 | Jan 2024 | Jan 2024 | no | 8.1.0 | unmaintained |
| 6.4 | Nov 2023 | Nov 2026 | Nov 2027 | yes | 8.1.0 | maintained |
| 7.0 | Nov 2023 | Jul 2024 | Jul 2024 | no | 8.2.0 | unmaintained |
| 7.1 | May 2024 | Jan 2025 | Jan 2025 | no | 8.2.0 | unmaintained |
| 7.2 | Nov 2024 | Jul 2025 | Jul 2025 | no | 8.2.0 | unmaintained |
| 7.3 | May 2025 | Jan 2026 | Jan 2026 | no | 8.2.0 | unmaintained |
| 7.4 | Nov 2025 | Nov 2028 | Nov 2029 | yes | 8.2.0 | maintained |
| 8.0 | Nov 2025 | Jul 2026 | Jul 2026 | no | 8.4.0 | unmaintained |
| 8.1 | May 2026 | Jan 2027 | Jan 2027 | no | 8.4.0 | current stable |
| 8.2 | Nov 2026 (planned) | Jul 2027 | Jul 2027 | no | 8.4.0 | under development |

Pitfalls:

- 8.2 is an unreleased version under development; it is not a released line.
- For 8.0 the releases page says: "Symfony 8.0 is no longer maintained. Consider upgrading to Symfony 8.1."
- 5.4 receives security fixes only; its bug fixes ended in November 2024.

## Version Pin in composer.json

What it is: the `extra.symfony.require` block in `composer.json` holds the Symfony version line for the project's `symfony/*` packages. With it in place, a `symfony/*` requirement can be `*`.

```json
{
    "require": {
        "symfony/cache": "*"
    },
    "extra": {
        "symfony": {
            "require": "7.0.*"
        }
    }
}
```

When to use: read it, together with the constraints next to each `symfony/*` library, to see which Symfony line the project allows.

Pitfalls:

- The `composer.json` file is configured to allow Symfony packages to be upgraded to patch versions only. A new minor version needs the constraint next to each `symfony/` library updated, and the `extra` block updated as well.
- A few libraries starting with `symfony/` follow their own versioning scheme and do not need to be updated, for example `symfony/monolog-bundle`. Their constraint says nothing about the Symfony line.
- Unspecific version constraints such as `dev-master` can make `composer update "symfony/*"` upgrade some non-Symfony libraries too.

## Asking the Console

What it is: when working on an existing Symfony application for the first time, this command displays information about the project.

```bash
php bin/console about
```

How the version is filled in (FrameworkBundle `Console\Application`, 7.4):

- The application name is hardcoded as `Symfony`.
- The version is taken from the installed `symfony/http-kernel` package first, then from `symfony/symfony`, otherwise from `Kernel::MAJOR_VERSION` and `Kernel::MINOR_VERSION`.
- `getLongVersion()` appends `(env: ..., debug: ...)` to the version.

When not to use: `symfony check:requirements` checks the machine and `symfony check:security` checks dependencies for known vulnerabilities; neither reports the Symfony version.

## Choosing the Version for a New Project

The command that creates new Symfony applications uses the latest stable version by default. For an LTS version, add the `--version` option.

```bash
symfony new my_project_directory --version=lts
symfony new my_project_directory --version="7.4.*"
composer create-project symfony/skeleton:"7.4.*" my_project_directory
```

Pitfalls:

- The `lts` and `next` shortcuts work only with the `symfony` binary. With Composer, give the exact version.
- The current documentation requires PHP 8.4 or higher with the Ctype, iconv, PCRE, Session, SimpleXML and Tokenizer extensions.

## Minor Upgrades

What it is: an upgrade where the middle number changes.

Pros: it should not bring significant backward compatibility changes.

Cons: some backward compatibility breaks are possible.

Steps:

1. Update the Symfony libraries via Composer: the constraint next to each `symfony/` library and the `extra.symfony.require` block.
2. Run the update.
3. Update the code to work with the new version, using the UPGRADE file of that version (for example `UPGRADE-6.4.md`) included in the Symfony directory.

```json
{
    "extra": {
        "symfony": {
            "require": "6.4.*"
        }
    }
}
```

```bash
composer update "symfony/*"
composer update "symfony/*" --with-all-dependencies
```

Use the second command only when the first one reports dependency errors.

## Major Upgrades

What it is: moving to a new first number, for example 6.4 to 7.0.

Path:

- First upgrade to the last minor version of the current major (for example 5.4) to see all the deprecations.
- If a more recent minor version is available (for example 6.4), you can use it directly and skip the older releases (6.0, 6.1 and so on).
- When the major version is released (for example 7.0.0), all deprecated features are removed. Code that stopped using deprecated features in the last version before the major (for example `6.4.*`) should upgrade without a problem.
- Resolve all deprecation notices before upgrading.
- Read `UPGRADE-X.0.md` (X is the new major version) in the Symfony repository for any backward compatibility break.

Finding deprecations:

- The web debug toolbar shows them.
- Run the tests through the PHPUnit bridge.

```bash
composer require --dev symfony/phpunit-bridge
./bin/phpunit
```

After the dependencies are updated:

```bash
composer update "symfony/*"
rm -rf var/cache/*
```

Clear the cache by removing its contents, because `cache:clear` may not work if the app cannot boot.

Recipes: after an upgrade, an updated version of a recipe may be available. `composer recipes:update` compares the recipe as installed with its latest version, creates a patch and applies it to the app.

```bash
composer recipes
composer recipes symfony/framework-bundle
composer recipes:update
composer recipes:update symfony/framework-bundle
```

## Signs of Code That Breaks on 8.0

Symfony 8 requires PHP 8.4 or higher. These items from `UPGRADE-8.0.md` no longer work on 8.0:

| Sign | 8.0 change |
| --- | --- |
| XML service or container configuration | The XML configuration format is no longer supported. |
| `errors.xml` or `webhook.xml` routing imports | Removed; use their PHP equivalent. |
| `profiler.xml` or `wdt.xml` routing imports | Removed; use their PHP equivalent. |
| Callable firewall listeners | Removed; extend `AbstractListener` or implement `FirewallListenerInterface`. |
| `session.sid_length`, `session.sid_bits_per_character` | Config options removed. |
| `router.cache_dir` | Config option removed. |
| `validation.cache` | Option removed. |
| `TranslationUpdateCommand` | Removed in favour of `TranslationExtractCommand`. |
| `debug:container --show-arguments` | Option removed. |
| `VersionAwareTest` trait in Form tests | Removed; use feature detection. |

## Sources

- https://symfony.com/releases
- https://symfony.com/releases/8.1
- https://symfony.com/releases/8.0
- https://symfony.com/releases/7.4
- https://symfony.com/releases/6.4
- https://symfony.com/releases/5.4
- https://symfony.com/doc/current/setup.html
- https://symfony.com/doc/current/setup/upgrade_minor.html
- https://symfony.com/doc/current/setup/upgrade_major.html
- https://github.com/symfony/symfony/blob/8.0/UPGRADE-8.0.md
- https://github.com/symfony/symfony/blob/7.4/src/Symfony/Bundle/FrameworkBundle/Console/Application.php
