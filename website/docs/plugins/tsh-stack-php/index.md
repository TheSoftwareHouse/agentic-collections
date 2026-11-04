---
title: 'TSH Stack: PHP'
sidebar_label: Overview
sidebar_position: 1
description: Version-aware PHP 7.4–8.5 and Symfony 5.4–8.x guidance for design, implementation and review, plus a read-only PHP code reviewer agent.
sources:
  - plugins/tsh-stack-php/.claude-plugin/plugin.json
  - plugins/tsh-stack-php/README.md
sources_hash: "5aa716c289fa964866aa1090b5f1fc14e6e9a38e09f94bf0165ad064e50d4154"
---

import PluginComponents from '@site/src/components/PluginComponents';

# TSH Stack: PHP

TSH conventions for PHP 7.4–8.5 and Symfony 5.4–8.x: version-aware design and implementation,
framework guidance with its version differences, and a code reviewer agent.

This is a **stack** plugin, not a discipline plugin. Install it into the projects that run on PHP,
at `project` scope, so it travels with the repository, which already knows what it runs on. Your
discipline plugin and `tsh-core` travel with you at `user` scope. For the install commands, see
[Installation](/docs/getting-started/installation).

## What it covers

- **PHP design and implementation.** The minimum code that solves the task, reuse before writing,
  YAGNI and KISS first, SOLID and DRY with judgement, design patterns and enterprise patterns only
  when a present need justifies them, architecture styles with their costs, code smells and
  refactoring, PSR-1 and PSR-12.
- **Symfony implementation and review.** Services and dependency injection, configuration, events,
  the HTTP layer, Doctrine, Forms, Validator, Serializer, Security, Messenger, Console and testing,
  with the differences between Symfony 5.4 and 8.x and the support status of third-party bundles
  such as FOSUserBundle and SensioFrameworkExtraBundle.
- **A reviewer agent.** Read-only review of a PHP or Symfony change, returned as a findings report.

The two skills are designed to work together: `implementing-symfony-applications` builds on the PHP
version rules and design principles of `architecting-php-code`, and the reviewer agent preloads
both.

## Components

<PluginComponents plugin="tsh-stack-php" />

## Version support

|         | Supported | When the project's version cannot be determined |
| :------ | :-------- | :---------------------------------------------- |
| PHP     | 7.4–8.5   | The skill asks                                  |
| Symfony | 5.4–8.x   | The skill asks                                  |

Older versions are worked with as they are. The skills never upgrade PHP, Symfony or a bundle unless
asked.

## Not covered yet

Deliberate gaps, listed in the plugin README as scope rather than oversight:

- **Laravel and other frameworks.** No skill of their own; `architecting-php-code` still applies to
  the PHP underneath them.
- **API Platform.** Mentioned for version support only; no implementation guidance.
- **PHP below 7.4 and Symfony below 5.4.** Outside the supported range.

## MCP servers and hooks

None bundled.

## Related

- [Plugin overview](/docs/plugins/)
- [Changelog](/docs/changelog/tsh-stack-php)
