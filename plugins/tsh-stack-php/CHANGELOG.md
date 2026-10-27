# Changelog

All notable changes to `tsh-stack-php` are documented here. The format follows
[Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/) and the versions
are the `version` field in
[`.claude-plugin/plugin.json`](.claude-plugin/plugin.json).

**One deliberate deviation: there is no `[Unreleased]` section.** The marketplace
serves plugins straight from `main`, so merging *is* releasing — an entry parked
under `[Unreleased]` would be false the moment it was pushed. Every entry below is
a released version, and its version bump landed in the same commit as the change it
describes.

Teammates receive these updates by running `/plugin update` — a change to this file
alone reaches nobody. This plugin is new, so the first install needs
`/plugin marketplace update tsh-agentic-collections` before it appears.

## [0.1.0] - 2026-10-27

Initial release.

### Added

- `architecting-php-code` — a senior PHP architect for PHP 7.4–8.5. It detects the
  project's PHP version (or asks) and uses only the features that version has. It
  writes the minimum code that solves the task: it searches for existing code to reuse
  before writing, adds no dependency without a reason, and introduces a pattern or
  layer only for a present, named need. References cover design principles (SOLID,
  YAGNI, KISS, DRY), clean code, code smells, the refactoring catalog, GoF patterns,
  Fowler's enterprise patterns, architecture styles, and PSR-1/PSR-12 rule by rule.
- `implementing-symfony-applications` — a senior Symfony specialist for Symfony
  5.4–8.x. It detects the project's Symfony version (or asks), never uses an API that
  does not exist in it or was removed from it, and justifies every framework feature
  it reaches for. References cover services and DI, configuration, events, the HTTP
  layer, Doctrine, Forms and Validator, Serializer, Security, Messenger, Console,
  testing, version differences per major release, and the supported Symfony range of
  common third-party bundles.
- `php-code-reviewer` agent — a read-only reviewer that checks a change for version
  correctness, unnecessary code, reuse, simplicity, design and PSR-12, runs the
  project's own checks in check-only mode, and returns a findings report.
