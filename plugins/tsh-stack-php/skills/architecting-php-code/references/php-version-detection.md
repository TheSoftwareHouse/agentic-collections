# PHP Version Detection

Use this reference when you need to decide which PHP version the code you are about to write must run on, before choosing any language feature.

## Table of Contents

- [Working Rules](#working-rules)
- [Composer `require.php`](#composer-requirephp)
- [Composer Version Constraints](#composer-version-constraints)
- [Composer `config.platform`](#composer-configplatform)
- [`composer.lock`](#composerlock)
- [Project Type](#project-type)
- [Docker Image Tags](#docker-image-tags)
- [CI with `shivammathur/setup-php`](#ci-with-shivammathursetup-php)
- [Support and EOL Status](#support-and-eol-status)
- [PHP 8.6 Release Schedule](#php-86-release-schedule)
- [Sources](#sources)

## Working Rules

Every solution choice depends on the PHP version the code runs on, so the version is known before any code is written or reviewed.

1. Determine the target PHP version first, before writing, changing or reviewing any PHP code.
2. Look in this order and stop when the version is clear: `composer.json` `config.platform.php` → `composer.json` `require.php` → `composer.lock` (`platform`, `platform-overrides`) → `Dockerfile` / `docker-compose.yml` (`FROM php:<version>`) → `.php-version` / `.tool-versions` → the CI matrix → `php -v` inside the project's container.
3. For an application, the target is the version it runs on. For a library, the target is the lowest version allowed by `require.php`.
4. When sources disagree, target the lowest version the code must run on, never below the lower bound of `require.php`. Report the inconsistency in one sentence; do not fix it unless asked.
5. When the version cannot be determined, ask the user. Never assume the newest version.
6. State the target in one line before the first code change, for example `Target: PHP 8.1 (composer.json config.platform.php)`.
7. Use only syntax, functions and classes available in the target version; check [`php-feature-availability.md`](./php-feature-availability.md). When a better solution needs a newer version, mention it as an option and do not use it.
8. Never upgrade PHP or change version constraints unless the user asks for it.

## Composer `require.php`

What it is: `require` and `require-dev` in `composer.json` "also support references to specific PHP versions and PHP extensions your project needs to run successfully." `php` represents the PHP version of the user, so a constraint such as `^7.1` can be applied to it.

```json
{
    "require": {
        "php": ">=7.4",
        "ext-mbstring": "*"
    }
}
```

- To require a 64-bit PHP, require the `php-64bit` package.

## Composer Version Constraints

What the operators in `require.php` mean:

| Constraint | Equivalent range |
| --- | --- |
| `^1.2.3` | `>=1.2.3 <2.0.0` |
| `^0.3` | `>=0.3.0 <0.4.0` |
| `~1.2` | `>=1.2 <2.0.0` |
| `~1.2.3` | `>=1.2.3 <1.3.0` |
| `~1` | same as `~1.0` |
| `1.0.*` | `>=1.0 <1.1` |
| `1.0 - 2.0` | `>=1.0.0 <2.1` |
| `1.0.0 - 2.1.0` | `>=1.0.0 <=2.1.0` |
| `>=1.0 <1.1 \|\| >=1.2` | either range |

- `^` sticks closer to semantic versioning than `~`.
- A double pipe `||` is a logical OR. AND has higher precedence than OR.
- A single pipe `|` is still treated as a logical OR.

Pitfall: in a `conflict` link, `<1.0 >=1.1` states a conflict with all versions that are less than 1.0. Use `<1.0 || >=1.1` instead.

## Composer `config.platform`

What it is: the `platform` setting in the `config` section of `composer.json`. It "lets you fake platform packages (PHP and extensions) so that you can emulate a production env or define your target platform in the config."

```json
{
    "config": {
        "platform": {
            "php": "7.0.3",
            "ext-something": "4.0.3"
        }
    }
}
```

Effect: no package requiring more than PHP 7.0.3 can be installed, regardless of the actual PHP version run locally.

When to use:

- To resolve dependencies for the production PHP version rather than the local interpreter.
- To hide an extension installed locally but not on production: `{"ext-foo": false}`.

Pitfalls:

- With `{"php": "7.4"}`, no packages that define `7.4.1` as minimum will be used.
- Dependencies are no longer checked against the real interpreter. On PHP 5.6 the install succeeds because Composer assumes 7.0.3, and then the code fails at runtime.
- When using it, also run `composer check-platform-reqs` as part of the deployment strategy.
- An extension requirement can be ignored with `--ignore-platform-req=ext-foo` on `update`, `install` or `require`, but in the long run the required extensions should be installed.
- The `config` section is only used for projects.

## `composer.lock`

- Composer writes all packages and their exact versions to `composer.lock`, so that everyone working on the project is locked to the same versions of dependencies.
- Composer displays a warning on `install` if `composer.lock` has not been updated.

## Project Type

The `type` field in `composer.json`:

- `library`: the default. Files are copied to `vendor`.
- `project`: denotes a project rather than a library.
- Use a custom type only when custom logic is needed during installation.

## Docker Image Tags

What it is: the official `php` image names the PHP version in the tag.

| Pattern | Examples |
| --- | --- |
| `php:<version>-cli` | `php:8.2-cli` |
| `php:<version>-apache` | |
| `php:<version>-fpm` | `php:8-fpm` |
| `php:<version>-alpine` | `php:8.2-fpm-alpine` |

- Short tags such as `8`, `8.5` and `8.3` are listed alongside full tags.
- `latest` is listed for the 8.5.11 trixie CLI image.
- Tags such as `8.6.0RC3-cli-trixie`, `8.6-rc-cli-trixie` and `8.5.12RC1-zts-alpine3.23` are also listed.
- Names such as `bookworm` or `trixie` are Debian suite code names and indicate which Debian release the image is based on.

When to use an explicit suite: specify `bookworm` or `trixie` explicitly to minimize breakage when there are new releases of Debian.

Pitfalls:

- The "Supported tags" list on Docker Hub is trimmed; the full list is in the `docker-library/docs` README.
- When installing extensions with `pecl install`, use an explicit version number to ensure PHP version compatibility.

## CI with `shivammathur/setup-php`

What it is: the `php-version` input of the `shivammathur/setup-php` GitHub Action.

| Value | Meaning |
| --- | --- |
| `'8.5'` | That version |
| `8.x`, `7.x`, `5.x` | Floating format `d.x`, where `d` is the major version |
| `lowest` | Accepted value |
| `highest`, `latest` | Accepted values |
| `nightly` | The next release, shown as `8.6` |
| `master` | Shown as `8.7` |
| `pre-installed` | Accepted value |

A matrix sets up multiple PHP versions:

```yaml
php-versions: ['8.2', '8.3', '8.4', '8.5']
php-version: ${{ matrix.php-versions }}
```

## Support and EOL Status

Policy: each release branch is fully supported for two years from its initial stable release. After that, it is supported for two additional years for critical security issues only, with releases made as needed. After four years, the branch reaches end of life.

| Status | Meaning |
| --- | --- |
| Active support | Reported bugs and security issues are fixed and regular point releases are made. |
| Security fixes only | Supported for critical security issues only; releases only as needed. |
| End of life | No longer supported. Upgrade as soon as possible; it may be exposed to unpatched security vulnerabilities. |

Supported branches:

| Branch | Released | Active support until | Security support until | Latest release |
| --- | --- | --- | --- | --- |
| 8.2 | 8 Dec 2022 | 31 Dec 2024 | 31 Dec 2026 | 8.2.33 |
| 8.3 | 23 Nov 2023 | 31 Dec 2025 | 31 Dec 2027 | 8.3.33 |
| 8.4 | 21 Nov 2024 | 31 Dec 2026 | 31 Dec 2028 | 8.4.25 |
| 8.5 | 20 Nov 2025 | 31 Dec 2027 | 31 Dec 2029 | 8.5.10 |

The status of each branch follows from these dates.

Unsupported branches:

| Branch | End of life | Last release |
| --- | --- | --- |
| 8.1 | 31 Dec 2025 | 8.1.34 |
| 8.0 | 26 Nov 2023 | 8.0.30 |
| 7.4 | 28 Nov 2022 | 7.4.33 |
| 7.3 | 6 Dec 2021 | 7.3.33 |
| 7.2 | 30 Nov 2020 | 7.2.34 |
| 7.1 | 1 Dec 2019 | 7.1.33 |
| 7.0 | 10 Jan 2019 | 7.0.33 |
| 5.6 | 31 Dec 2018 | 5.6.40 |

Users of unsupported branches are strongly urged to upgrade, as older versions may expose them to security vulnerabilities and bugs fixed in more recent versions.

## PHP 8.6 Release Schedule

8.6 has a published release schedule with GA on Nov 19, 2026. The supported-versions and releases pages do not mention 8.6.

| Milestone | Date |
| --- | --- |
| Alpha 1, 2, 3 | Jul 02, Jul 16, Jul 30, 2026 |
| RFC merge target | Aug 11, 2026 |
| Beta 1 and soft feature freeze | Aug 13, 2026 |
| Beta 2, 3 | Aug 27, Sep 10, 2026 |
| Hard feature freeze | Sep 22, 2026 |
| RC2 (RC1 skipped) | Sep 24, 2026 |
| RC3, RC4, RC5 | Oct 08, Oct 22, Nov 05, 2026 |
| GA | Nov 19, 2026 |

- At soft feature freeze, all RFCs must have their voting concluded. After hard feature freeze, features are merged only with release manager approval.
- Individual releases may be added or removed to accommodate development progress.
- Releases are tagged on Tuesday and released on Thursday. The pre-release phase is 5 months.

## Sources

- https://www.php.net/supported-versions.php
- https://www.php.net/eol.php
- https://www.php.net/releases/
- https://wiki.php.net/todo/php86
- https://getcomposer.org/doc/01-basic-usage.md
- https://getcomposer.org/doc/04-schema.md
- https://getcomposer.org/doc/06-config.md
- https://getcomposer.org/doc/articles/versions.md
- https://hub.docker.com/_/php
- https://github.com/docker-library/docs/blob/master/php/README.md
- https://github.com/shivammathur/setup-php
