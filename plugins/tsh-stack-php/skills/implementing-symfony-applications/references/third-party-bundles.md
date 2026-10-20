# Third-Party Bundles

Use this reference when a project depends on a popular Symfony bundle or library, when you are deciding whether to add one, or when you need to know what a bundle's current release requires and what replaces an abandoned one.

## Table of Contents

- [Rule of Thumb](#rule-of-thumb)
- [Latest Release Requirements](#latest-release-requirements)
- [FOSUserBundle](#fosuserbundle)
- [SensioFrameworkExtraBundle](#sensioframeworkextrabundle)
- [Swiftmailer](#swiftmailer)
- [API Bundles](#api-bundles)
- [Doctrine](#doctrine)
- [UI and Frontend](#ui-and-frontend)
- [Sources](#sources)

## Rule of Thumb

- **Do not add an abandoned or discouraged package to new code.** Packagist marks `sensio/framework-extra-bundle`, `symfony/swiftmailer-bundle` and `doctrine/annotations` abandoned; the FOSUserBundle README says "New projects should not use this bundle."
- **Check the `require` block of the release you install.** The table below gives only the latest release of each package; the requirements of older lines are not listed here.

## Latest Release Requirements

| Package | Release | PHP | Symfony | Status |
| --- | --- | --- | --- | --- |
| friendsofsymfony/user-bundle | v4.1.0 | ^8.2 | ^7.3 | minimal maintenance |
| sensio/framework-extra-bundle | v6.2.10 | >=7.2.5 | ^4.4\|^5.0\|^6.0 | abandoned |
| symfony/swiftmailer-bundle | v3.5.4 | >=7.1 | ^4.4\|^5.0 | abandoned |
| friendsofsymfony/rest-bundle | 3.9.0 | ^7.4\|^8.0 | ^5.4\|^6.4\|^7.0\|^8.0 | not marked abandoned |
| jms/serializer-bundle | 5.5.2 | ^7.4 \|\| ^8.0 | ^5.4 \|\| ^6.0 \|\| ^7.0 \|\| ^8.0 | not marked abandoned |
| lexik/jwt-authentication-bundle | v3.2.0 | >=8.2 | ^6.4\|^7.0\|^8.0 | not marked abandoned |
| nelmio/api-doc-bundle | v5.13.1 | 8.2+ | ^6.4 \|\| ^7.2 \|\| ^8.0 | not marked abandoned |
| api-platform/core | v5.0.4 | >=8.2 | ^7.4 \|\| ^8.0 | not marked abandoned |
| doctrine/doctrine-bundle | 3.3.2 | ^8.4 | ^6.4 \|\| ^7.0 \|\| ^8.0 | not marked abandoned |
| doctrine/annotations | 2.0.2 | ^7.2 \|\| ^8.0 | none | abandoned |
| knplabs/knp-paginator-bundle | v6.11.0 | ^8.2 | ^6.4 \|\| ^7.4 \|\| ^8.0 | not marked abandoned |
| easycorp/easyadmin-bundle | v5.7.0 | >=8.2 | 6.4, 7.x, 8.x | stable |
| symfony/webpack-encore-bundle | 2.4.2 | >=8.1.0 | ^5.4 \|\| ^6.2 \|\| ^7.0 \|\| ^8.0 | low maintenance |
| symfony/twig-bridge | v8.1.7 | >=8.4.1 | 8.1 | not marked abandoned |

## FOSUserBundle

**What it is.** It "adds support for a database-backed user system in Symfony2+", stores users through Doctrine ORM or MongoDB ODM, and "can provide the user provider for the core SecurityBundle."

**Status.** "The package only receives minimal maintenance to allow existing projects to upgrade." "Existing projects are expected to plan a migration away from this bundle." Version lines 1.x to 4.x exist; only v4.1.0 states its requirements (PHP ^8.2, Symfony components ^7.3, Twig ^2.13 || ^3.0).

**When not to use.** In a new project. The README says "It is actually much easier to implement the User entity in the project," and points to SymfonyCasts' verify-email-bundle for email verification. Symfony's own example is `class User implements UserInterface, PasswordAuthenticatedUserInterface`.

**Version differences.** Symfony 6.0 removed `getPassword()` and `getSalt()` from `UserInterface`; use `PasswordAuthenticatedUserInterface`, or `LegacyPasswordAuthenticatedUserInterface` for legacy salts. Symfony 5.3 deprecated `UserInterface::getUsername()` in favour of `getUserIdentifier()`. Symfony 8.0 removes `UserInterface::eraseCredentials()`; "Credentials should be erased through `__serialize()` instead."

## SensioFrameworkExtraBundle

**Status.** Abandoned and archived on Feb 24, 2023. Last release v6.2.10. Its `require` allows Symfony ^4.4|^5.0|^6.0, and the FOSRestBundle Packagist page says it is "not supported with Symfony >=7.0."

**Replacement.** "Please move to native PHP attribute support as added in Symfony core." "For full support, use Symfony 6.2."

**Core attributes in current Symfony.**

- `#[MapEntity]` "extends `ValueResolver`" and disables `EntityValueResolver` for a controller.
- `#[IsGranted]` runs voters, like `isGranted()` and `denyAccessUnlessGranted()`.
- `#[Template]` lets a controller return an array, handled on `kernel.view`.
- `#[Cache]` is read by `CacheAttributeListener` on `kernel.controller`.

**Pitfall (8.0).** "Automatic mapping of Doctrine entities to controller arguments has been removed. Use the `#[MapEntity]` attribute or the route mapping syntax (`{param:argument}`)."

## Swiftmailer

**Status.** `symfony/swiftmailer-bundle` is abandoned; last release v3.5.4 (PHP >=7.1, swiftmailer/swiftmailer ^6.1.3, Symfony ^4.4|^5.0; conflicts with twig/twig <1.41 or >=2.0,<2.10). Swiftmailer maintenance ended at the end of November 2021, "at the same time as the Symfony 5.4 LTS and 6.0 release."

**Replacement.** `symfony/mailer`. Mailer was first released in Symfony 4.3, and "As of Symfony 5.3, all Swiftmailer great features and more are available in Symfony Mailer." "Migrating from Swiftmailer to Symfony Mailer is a relatively easy task as the concepts are the same between the two projects."

Install with `composer require symfony/mailer` and set `MAILER_DSN=smtp://user:pass@smtp.example.com:port`.

```php
$email = new Email()
    ->from('hello@example.com')
    ->to('you@example.com')
    ->subject('Time for Symfony Mailer!')
    ->text('Sending emails is fun again!')
    ->html('<p>See Twig integration for better HTML integration!</p>');

$mailer->send($email);
```

**Pitfalls.** If Messenger is installed, "all emails will be sent asynchronously by default." A bug is reported when `symfony/mailer` and `symfony/swiftmailer-bundle` with a memory spool are in the same project (swiftmailer-bundle PR #313).

## API Bundles

### FOSRestBundle

**What it is.** "Various tools to rapidly develop RESTful API's & applications with Symfony," including "A View layer to enable output and format agnostic Controllers" and mapping exception codes to HTTP status codes.

**Versions.** 3.9.0 allows Symfony ^5.4|^6.4|^7.0|^8.0 and PHP ^7.4|^8.0. It conflicts with doctrine/annotations <1.12, jms/serializer <1.13.0, jms/serializer-bundle <2.4.3 or 3.0.0, and sensio/framework-extra-bundle <6.1. Packagist lists one security advisory. Upgrade notes are in the `UPGRADING-X.X.md` files.

**Native alternative.** `#[MapRequestPayload]` maps the request payload to a DTO; `#[MapQueryString]` maps the query string. Validation failure returns 422 by default. For JSON APIs, declare the route with `format: 'json'`.

```php
public function dashboard(#[MapRequestPayload] UserDto $userDto): Response
```

Nested arrays of DTOs need `phpstan/phpdoc-parser` and `phpdocumentor/type-resolver`. Symfony 8.1 adds variadic arguments, file mapping for `multipart/form-data` and `mapWhenEmpty`.

### JMSSerializerBundle

**Versions.** 5.5.2 requires jms/serializer ^3.31 and Symfony ^5.4 || ^6.0 || ^7.0 || ^8.0. Of the library, "The version `3.x` is the supported version"; "The `1.x` and `2.x` versions are not supported anymore."

### LexikJWTAuthenticationBundle

**What it is.** JWT authentication for a Symfony API.

**Versions.** The README: "compatible (and tested) with PHP > 8.2 and Symfony > 6.4 up to 8." v3.2.0 requires PHP >=8.2 and Symfony ^6.4|^7.0|^8.0. Lines 1.x, 2.x (up to v2.21.0) and 3.x exist.

**Native alternative.** Symfony's access token authenticator with a custom token handler.

```yaml
security:
    firewalls:
        main:
            access_token:
                token_handler: App\Security\AccessTokenHandler
```

```php
class AccessTokenHandler implements AccessTokenHandlerInterface
{
    public function getUserBadgeFrom(string $accessToken): UserBadge
    {
        $accessToken = $this->repository->findOneByValue($accessToken);
        if (null === $accessToken || !$accessToken->isValid()) {
            throw new BadCredentialsException('Invalid credentials.');
        }

        return new UserBadge($accessToken->getUserId());
    }
}
```

**Pitfalls.**

- "With self-contained access tokens such as JWT, the handler is required to verify the digital signature and understand all claims, especially `sub`, `iat`, `nbf` and `exp`."
- OIDC handlers need `symfony/http-client` (`OidcUserInfoTokenHandler`) or `web-token/jwt-library` (`OidcTokenHandler`), plus `symfony/cache` for discovery.
- The `enforce_key_usage_verification` option exists from Symfony 8.1.

### NelmioApiDocBundle

**What it is.** "Generates documentation for your REST API from attributes."

**Version differences.**

- 5.0: "The bundle now requires PHP 8.1 or higher." "Minimum Symfony version is now 6.4." "Support for annotations has been removed in favor of PHP 8 attributes."
- 4.0 "brings OpenAPI 3.0 support"; to stay on Swagger 2.0, use version 3.
- v5.13.1 requires PHP 8.2+ and Symfony ^6.4 || ^7.2 || ^8.0, plus symfony/type-info ^7.2 || ^8.0.

### API Platform

**What it is.** "An easy-to-use and powerful system to create hypermedia-driven REST and GraphQL APIs," integrated with Symfony through the bundle distributed with the library.

**Versions.** v5.0.4 requires PHP >=8.2 and Symfony ^7.4 || ^8.0, with symfony/serializer ^7.4.9 || ^8.0.9.

## Doctrine

### DoctrineBundle 3.0

- "The minimum required PHP version is now 8.4."
- "Support for the YML and annotation metadata drivers has been dropped."
- Drops `twig/twig` 2, `doctrine/dbal` 3 and `doctrine/orm` 2; this makes `DisconnectedMetadataFactory` redundant.
- `ConnectionFactory::createConnection()` no longer takes the event manager:

```diff
- $connectionFactory->createConnection($params, $config, $eventManager, $mappingTypes)
+ $connectionFactory->createConnection($params, $config, $mappingTypes)
```

3.3.2 requires doctrine/dbal ^4.0, doctrine/persistence ^4 and Symfony ^6.4 || ^7.0 || ^8.0, and conflicts with doctrine/orm <3.0 || >=4.0 and twig/twig <3.0.4 || >=5.

### ORM 3.0

- "The annotation driver and anything related to annotation has been removed."
- Code relying on `YamlDriver` or `SimpleYamlDriver` must migrate.
- `EntityManager::merge()` "will throw an exception on each call."
- The `EntityManager` constructor is public and replaces `create()`.
- "The `PARTIAL` keyword in DQL no longer exists."
- With doctrine/dbal 4, PostgreSQL uses `IDENTITY` instead of `SEQUENCE` for the AUTO strategy. To keep `SEQUENCE`:

```php
$configuration->setIdentityGenerationPreferences([
    PostgreSQLPlatform::class => ClassMetadata::GENERATOR_TYPE_SEQUENCE,
]);
```

### doctrine/annotations

**Status.** Abandoned with no replacement package suggested; "feature complete, and should receive exclusively bugfixes and security fixes." "PHP 8 introduced attributes, which are a native replacement for annotations."

**Version differences.**

- Symfony 6.4 deprecates the Doctrine annotations integration: uninstall `doctrine/annotations` or set `framework.annotations` to `false`. Routing, Serializer and Validator deprecate annotation loaders in favour of `Attribute*` loaders; `enable_annotations` options become `enable_attributes`.
- Symfony 7.0 removes Doctrine annotations support from Routing, Serializer, Validator and FrameworkBundle, and the `@required` annotation in favour of the `Required` attribute.
- Symfony 8.0 removes the class aliases in the Routing and Serializer `Annotation` namespaces.

## UI and Frontend

### KnpPaginatorBundle

**What it is.** "Paginator bundle for Symfony to automate pagination and simplify sorting." Master "is compatible with Symfony `>=6.4` versions"; it needs Twig `>=3.0` when Twig is used and Knp Pager `>=4.4`.

Install with `composer require knplabs/knp-paginator-bundle`.

```php
$pagination = $paginator->paginate(
    $query,
    $request->query->getInt('page', 1),
    10
);
```

Twig helpers: `knp_pagination_rel_links(pagination)`, `knp_pagination_render(pagination)`, `knp_pagination_sortable(pagination, 'Title', 'a.title')`.

**Pitfall.** Pass the query, not its result, to `paginate()`.

### EasyAdminBundle

**What it is.** An "Admin generator for Symfony applications."

| Line | Symfony | PHP | Status |
| --- | --- | --- | --- |
| 5.x | 6.4, 7.x, 8.x | 8.2+ | Stable version |
| 4.x | 5.4, 6.x, 7.x, 8.x | 8.1+ | Bug fixes only |
| 3.x | 4.4, 5.x | 7.2.5+ | No longer maintained |
| 2.x | 4.x, 5.x | 7.1.3+ | No longer maintained |
| 1.x | 2.x, 3.x, 4.x | 5.3.0+ | No longer maintained |

v5.7.0 requires doctrine/orm ^2.20|^3.6, doctrine/dbal ^3.10|^4.4, doctrine/doctrine-bundle ^2.18|^3.2 and twig/twig ^3.23.

Quick start: `composer require easycorp/easyadmin-bundle`, then `make:admin:dashboard` and `make:admin:crud`; the admin is at `/admin`.

### Webpack Encore versus AssetMapper

**Encore.** WebpackEncoreBundle renders the `script` and `link` tags from Encore's `entrypoints.json`. "Webpack Encore is now in low-maintenance mode (bug fixes, security patches, and `peerDependencies` updates only)." "If your project needs a bundler, we recommend migrating to Symfony Reprise."

**AssetMapper.** Introduced in Symfony 6.3; uses import maps and "makes unnecessary to use Webpack, Webpack Encore, Node.js, yarn/npm." "You don't need to build and compile the assets."

```yaml
framework:
    asset_mapper:
        paths: ['assets/']
```

Add dependencies with `php bin/console importmap:require '@hotwired/stimulus'`, which creates `importmap.php`, and put `{{ importmap() }}` inside `<head>`. In production, `asset-map:compile` copies assets into `public/assets/` with a `manifest.json`.

**When to use which.** "You can still use Webpack Encore and not use this. Or you can only use this new feature and not use Webpack Encore." TypeScript still needs Encore "because you need the building and compilation phase."

### Twig

symfony/twig-bridge v8.1.7 requires PHP >=8.4.1 and twig/twig ^3.25|^4.0. twig/twig 4 is at v4.0.0-alpha1 (PHP >=8.2); the 3.x line reaches v3.30.0. The Templating component is deprecated in Symfony 6.4 and removed in 7.0: "use Twig instead."

## Sources

- https://packagist.org/packages/friendsofsymfony/user-bundle
- https://github.com/FriendsOfSymfony/FOSUserBundle
- https://packagist.org/packages/sensio/framework-extra-bundle
- https://github.com/sensiolabs/SensioFrameworkExtraBundle
- https://packagist.org/packages/symfony/swiftmailer-bundle
- https://symfony.com/blog/the-end-of-swiftmailer
- https://packagist.org/packages/friendsofsymfony/rest-bundle
- https://github.com/FriendsOfSymfony/FOSRestBundle
- https://packagist.org/packages/jms/serializer-bundle
- https://github.com/schmittjoh/serializer
- https://packagist.org/packages/lexik/jwt-authentication-bundle
- https://github.com/lexik/LexikJWTAuthenticationBundle
- https://packagist.org/packages/nelmio/api-doc-bundle
- https://github.com/nelmio/NelmioApiDocBundle
- https://packagist.org/packages/api-platform/core
- https://github.com/api-platform/core
- https://packagist.org/packages/doctrine/doctrine-bundle
- https://github.com/doctrine/DoctrineBundle/blob/3.0.0/UPGRADE-3.0.md
- https://github.com/doctrine/orm/blob/3.0.0/UPGRADE.md
- https://packagist.org/packages/doctrine/annotations
- https://packagist.org/packages/knplabs/knp-paginator-bundle
- https://github.com/KnpLabs/KnpPaginatorBundle
- https://packagist.org/packages/easycorp/easyadmin-bundle
- https://github.com/EasyCorp/EasyAdminBundle
- https://packagist.org/packages/symfony/webpack-encore-bundle
- https://github.com/symfony/webpack-encore-bundle
- https://symfony.com/blog/new-in-symfony-6-3-assetmapper-component
- https://packagist.org/packages/symfony/twig-bridge
- https://packagist.org/packages/twig/twig
- https://symfony.com/doc/current/controller/value_resolver.html
- https://symfony.com/doc/current/controller.html
- https://symfony.com/doc/current/security/access_token.html
- https://symfony.com/doc/current/mailer.html
- https://github.com/symfony/symfony/blob/6.0/UPGRADE-6.0.md
- https://github.com/symfony/symfony/blob/5.4/UPGRADE-5.3.md
- https://github.com/symfony/symfony/blob/6.4/UPGRADE-6.4.md
- https://github.com/symfony/symfony/blob/7.0/UPGRADE-7.0.md
- https://github.com/symfony/symfony/blob/8.0/UPGRADE-8.0.md
- https://symfony.com/doc/7.4/components/http_kernel.html
- https://symfony.com/doc/current/security/voters.html
