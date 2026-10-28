# Symfony Version Differences

Use this reference when the detected Symfony version decides which API, attribute or config format you may use, when you meet legacy code and need to know whether it is still valid, or when a task touches code that a newer major removed.

## Table of Contents

- [Release Lines](#release-lines)
- [How Majors Relate](#how-majors-relate)
- [Upgrade Path](#upgrade-path)
- [5.4 to 6.0](#54-to-60)
- [6.4 to 7.0](#64-to-70)
- [7.4 to 8.0](#74-to-80)
- [Ecosystem Packages](#ecosystem-packages)
- [Legacy Pattern Table](#legacy-pattern-table)
- [Worked Examples](#worked-examples)
- [Sources](#sources)

## Release Lines

| Version | Requires PHP | Released | End of bug fixes | End of security fixes |
| --- | --- | --- | --- | --- |
| 5.4 | 7.2.5 or higher | November 2021 | November 2024 | February 2029 |
| 6.0 | 8.0.2 or higher | November 2021 | January 2023 (unmaintained) | January 2023 |
| 6.4 | 8.1.0 or higher | November 2023 | November 2026 | November 2027 |
| 7.0 | 8.2.0 or higher | November 2023 | July 2024 (unmaintained) | July 2024 |
| 7.4 | 8.2.0 or higher | November 2025 | November 2028 | November 2029 |
| 8.0 | 8.4.0 or higher | November 2025 | July 2026 (unmaintained) | July 2026 |
| 8.1 | 8.4.0 or higher | May 2026 | January 2027 | January 2027 |

## How Majors Relate

- Major releases are allowed to break backward compatibility. Minor versions should not contain backward-incompatible changes.
- Deprecated code still works, but is marked as deprecated.
- When the major version is released (for example 7.0.0), all deprecated features are removed. Code that stopped using them on the last minor before the major (for example 6.4) should upgrade without a problem.
- Symfony 8.0 does not include any deprecated features.
- In rare situations the next major may still contain backward-compatibility breaks, so read `UPGRADE-X.0.md`.

## Upgrade Path

1. Upgrade to the last minor of the current major (for example 5.4) to see all deprecations. If a more recent minor is available (for example 6.4), use it directly and skip the older ones.
2. Make the code deprecation free. Notices appear in the web debug toolbar in the `dev` environment. PHPUnit shows none by default, so install `composer require --dev symfony/phpunit-bridge`; once all are fixed, the command ends with `0`. Rector includes rules that fix some Symfony deprecations automatically.
3. Change every `symfony/` package constraint to the new major (for example `"symfony/console": "6.4.*"` to `"7.0.*"`). Packages with their own versioning (`symfony/polyfill-*`, `symfony/ux-*`, `symfony/*-bundle`) need no change.
4. In Flex projects, update `extra.symfony.require`, which restricts Symfony packages to one version.
5. Run `composer update "symfony/*"`; on dependency errors add `--with-all-dependencies`. Set Composer's `platform` option to the server's PHP version.
6. Run `composer recipes:update`, then fix code for the new major.

```json
{
    "extra": {
        "symfony": {
            "require": "7.0.*"
        }
    }
}
```

When something was deprecated in 6.4 and you still need to support 6.3, use weak deprecations mode:

```xml
<env name="SYMFONY_DEPRECATIONS_HELPER" value="max[total]=999999"/>
```

Pitfall: tools like Dependabot may ignore `extra.symfony.require` and upgrade Symfony dependencies.

## 5.4 to 6.0

Symfony 6.0 requires PHP 8.0.2 or higher.

| Area | Removed or changed in 6.0 | Use instead |
| --- | --- | --- |
| Security | Guard component | the authenticator system |
| Security | Not setting `enable_authenticator_manager: true` throws an exception | the authenticator system |
| Security | `AnonymousToken`; `IS_AUTHENTICATED_ANONYMOUSLY` | `PUBLIC_ACCESS` |
| Security | classes in `Core\Encoder\`; `UserPasswordEncoderInterface` alias | PasswordHasher component; `UserPasswordHasherInterface` |
| Security | `UserInterface::getUsername()` | `getUserIdentifier()` |
| Security | `getPassword()` / `getSalt()` on `UserInterface` | `PasswordAuthenticatedUserInterface`; `LegacyPasswordAuthenticatedUserInterface` for legacy salts |
| Controllers | `AbstractController::get()`, `has()`, `getDoctrine()`, `dispatchMessage()` | method or constructor injection |
| Session | `session` service, `SessionInterface` alias, `session.attribute_bag`, `session.flash_bag` | `Request::getSession()` or `RequestStack::getSession()` |
| HttpKernel | `MASTER_REQUEST`, `isMasterRequest()`, `getMasterRequest()` | `MAIN_REQUEST`, `isMainRequest()`, `getMainRequest()` |
| Routing | `service:action` controller syntax | `serviceOrFqcn::method` |
| Kernel | `RouteCollectionBuilder` | no replacement named |
| Container | `translator`, `serializer`, `validator`, `twig`, `form.factory`, `security.token_storage`, `security.authorization_checker` and others become private | injection |
| Messenger | AMQP, Doctrine and Redis transports | `symfony/amqp-messenger`, `symfony/doctrine-messenger`, `symfony/redis-messenger` |

Pitfalls:

- The Redis transport option `delete_after_ack` now defaults to `true`, and TLS is set with the `rediss://` scheme instead of `tls=1`.
- A user class with a password must implement both interfaces, for example `class User implements UserInterface, PasswordAuthenticatedUserInterface`.

```yaml
access_control:
    - { path: ^/login, roles: PUBLIC_ACCESS }
```

## 6.4 to 7.0

Symfony 7.0 requires PHP 8.2.0 or higher.

| Area | Removed or changed in 7.0 | Use instead |
| --- | --- | --- |
| Metadata | Doctrine annotations support in Routing, Serializer, Validator and FrameworkBundle | native PHP attributes |
| Metadata | `framework.validation.enable_annotations`, `framework.serializer.enable_annotations`, `routing.loader.annotation*` | `enable_attributes`, `routing.loader.attribute*` |
| Metadata | `AnnotationClassLoader`, `AnnotationDirectoryLoader`, `AnnotationFileLoader`, `AnnotationLoader` | the `Attribute*` equivalents |
| DI | `ContainerAwareInterface`, `ContainerAwareTrait` | dependency injection; a service subscriber for lazy access to services |
| DI | `@required` annotation | `Symfony\Contracts\Service\Attribute\Required` |
| DI | `#[MapDecorated]` | `#[AutowireDecorated]` |
| Console | `Command::$defaultName`, `$defaultDescription` | `#[AsCommand]` |
| Messenger | `MessageHandlerInterface`, `MessageSubscriberInterface` | `#[AsMessageHandler]` on the class or on handler methods |
| HttpKernel | `ArgumentValueResolverInterface` | `ValueResolverInterface` |
| Controllers | `renderForm()` | `render()` with the `FormInterface` passed as a parameter |
| Serializer | `CacheableSupportsMethodInterface` | `getSupportedTypes(?string $format): array` on the normalizer |
| Security | `enable_authenticator_manager` option | remove the option |
| Security | `Symfony\Component\Security\Core\Security` | `Symfony\Bundle\SecurityBundle\Security` |
| Templating | Templating component | Twig |

Pitfall: enabling SecurityBundle without configuring it is no longer allowed in 7.0.

## 7.4 to 8.0

Symfony 8.0 requires PHP 8.4 or higher.

| Area | Removed or changed in 8.0 | Use instead |
| --- | --- | --- |
| Config | XML configuration format | YAML or PHP; for routes also attributes |
| Config | fluent PHP format for semantic configuration; fluent methods in config builders | `$container->extension()` or a returned PHP array |
| Config | `$this` and the loader's internal scope in PHP config files | the `$loader` variable |
| Routes | FrameworkBundle `errors.xml`, `webhook.xml`; WebProfilerBundle `profiler.xml`, `wdt.xml` | their PHP equivalents |
| Metadata | class aliases in the `Annotation` namespace of Routing and Serializer | attributes |
| Console | `getDefaultName()`, `getDefaultDescription()` | `#[AsCommand]` (now a `final` class) |
| Console | `Application::add()` | `addCommand()` |
| DI | `#[TaggedIterator]`, `#[TaggedLocator]` | `#[AutowireIterator]`, `#[AutowireLocator]` |
| DI | YAML `!tagged` | `!tagged_iterator` |
| Security | `eraseCredentials()` on `UserInterface`, `TokenInterface`, `LdapUser` | erase credentials through `__serialize()` |
| Security | `VoterInterface::vote()` and `Voter::voteOnAttribute()` signatures | add the new `$vote` argument |
| Security | `hide_user_not_found` | `expose_security_errors` (`true` becomes `'none'`, `false` becomes `'all'`; new value `'account_status'`) |
| HttpFoundation | `Request::get()` | `->attributes`, `->query` or `->request` |
| PropertyInfo | `Type`, `getTypes()`, `getTypesFromConstructor()` | `Symfony\Component\TypeInfo\Type`, `getType()`, `getTypeFromConstructor()` |
| HttpKernel | `__sleep()` / `__wakeup()` on kernels and data collectors | `__serialize()` / `__unserialize()` |
| DoctrineBridge | auto-mapping of Doctrine entities to controller arguments | `#[MapEntity]` or the route mapping syntax `{param:argument}` |

XML configuration, deprecated in 7.4:

- Why: PHP, YAML and XML offer nearly identical capabilities and equivalent performance because all are compiled back to PHP before runtime. XML support was already disabled by default for packages and routes.
- When to use YAML: it remains the default format.
- When to use PHP: for a fully code-based configuration.
- When not to use XML: it is deprecated, unsupported from 8.0, and offers no capabilities beyond the other formats. It remains popular only because it was the officially recommended option for many years.
- Reusable bundles can convert XML to PHP with the converter linked from the 7.4 announcement.

Pitfall: in 7.4, using `$this` or its internal scope from PHP config files already throws (a BC break), before the 8.0 removal.

## Ecosystem Packages

- **Swiftmailer**: maintenance ended at the end of November 2021, together with the Symfony 5.4 LTS and 6.0 release. Symfony Mailer first shipped in 4.3 and has covered all Swiftmailer features since 5.3. Migration is relatively easy because the concepts are the same. `symfony/swiftmailer-bundle` is abandoned; its last release (3.5.4) requires `symfony/*` `^4.4|^5.0`.
- **SensioFrameworkExtraBundle**: abandoned and archived. It says to move to native PHP attribute support in Symfony core, and that full support needs Symfony 6.2. FOSRestBundle states it is not supported with Symfony 7.0 and above.
- **DoctrineBundle 3.0**: requires PHP 8.4, drops `doctrine/orm` 2, `doctrine/dbal` 3 and `twig/twig` 2, and drops the YML and annotation metadata drivers.
- **Doctrine ORM 3.0**: the annotation driver and everything related to annotations is removed. `EntityManager::merge()` throws on each call, the `EntityManager` constructor replaces `create()`, and DQL no longer has `PARTIAL`. With DBAL 4, PostgreSQL uses `IDENTITY` instead of `SEQUENCE` for the AUTO strategy.

## Legacy Pattern Table

Grep for the pattern, then compare the "Removed in" column with the detected version. A dash means the version is not stated in the sources.

| Grep for | Replacement | Deprecated | Removed in |
| --- | --- | --- | --- |
| `AbstractGuardAuthenticator`, `guard:` | authenticator system | 5.3 | 6.0 |
| `IS_AUTHENTICATED_ANONYMOUSLY`, `AnonymousToken` | `PUBLIC_ACCESS` | — | 6.0 |
| `UserPasswordEncoderInterface`, `Core\Encoder\` | `UserPasswordHasherInterface`, PasswordHasher | 5.3 | 6.0 |
| `getUsername()` | `getUserIdentifier()` | 5.3 | 6.0 |
| `isMasterRequest`, `MASTER_REQUEST`, `getMasterRequest` | `isMainRequest()`, `MAIN_REQUEST`, `getMainRequest()` | 5.3 | 6.0 |
| `$this->get(`, `getDoctrine()` in controllers | injection | — | 6.0 |
| `RouteCollectionBuilder` | — | — | 6.0 |
| `swiftmailer`, `Swift_` | `symfony/mailer` | maintenance ended November 2021 | bundle requires Symfony `^4.4\|^5.0` |
| `sensio/framework-extra-bundle` | native attributes in Symfony core | bundle abandoned | not supported with 7.0+ (FOSRestBundle) |
| `@Route`, `use Doctrine\Common\Annotations` | native PHP attributes | 6.4 | 7.0 |
| `@ORM\` | another mapping driver | — | ORM 3.0, DoctrineBundle 3.0 |
| `ContainerAwareInterface`, `ContainerAwareTrait` | dependency injection | 6.4 | 7.0 |
| `@required` | `#[Required]` | — | 7.0 |
| `#[MapDecorated]` | `#[AutowireDecorated]` | — | 7.0 |
| `protected static $defaultName` | `#[AsCommand]` (added 5.3) | 6.1 | 7.0 |
| `MessageHandlerInterface`, `MessageSubscriberInterface` | `#[AsMessageHandler]` | 6.2 | 7.0 |
| `ArgumentValueResolverInterface` | `ValueResolverInterface` | 6.2 | 7.0 |
| `renderForm(` | `render()` | 6.2 | 7.0 |
| `Core\Security` (class) | `SecurityBundle\Security` | 6.2 | 7.0 |
| `enable_authenticator_manager` | remove the option | 6.2 | 7.0 |
| `CacheableSupportsMethodInterface` | `getSupportedTypes()` | — | 7.0 |
| `Templating` component | Twig | 6.4 | 7.0 |
| `#[TaggedIterator]`, `#[TaggedLocator]` | `#[AutowireIterator]`, `#[AutowireLocator]` | — | 8.0 |
| `!tagged ` in YAML | `!tagged_iterator` | 7.2 | 8.0 |
| `*.xml` under `config/` | YAML or PHP | 7.4 | 8.0 |
| `return function (AcmeConfig $config)` | returned PHP array | 7.4 | 8.0 |
| `->add(` on `Application` | `addCommand()` | 7.4 | 8.0 |
| `getDefaultName()` | `#[AsCommand]` | — | 8.0 |
| `eraseCredentials` | `__serialize()` | — | 8.0 |
| `hide_user_not_found` | `expose_security_errors` | — | 8.0 |
| `$request->get(` | explicit bag access | 7.4 | 8.0 |

## Worked Examples

A command on 7.0+ declares its name with the attribute; `Command::$defaultName` is gone.

```php
#[AsCommand(name: 'app:create-user', description: 'Creates users')]
final class CreateUserCommand extends Command
{
}
```

On 8.0 register commands with `addCommand()`.

```php
$application->addCommand(new CreateUserCommand());
```

A message handler on 7.0+ carries the attribute instead of implementing `MessageHandlerInterface`.

```php
#[AsMessageHandler]
final class SmsNotificationHandler
{
    public function __invoke(SmsNotification $message): void
    {
    }
}
```

Tagged services on 8.0 use `#[AutowireIterator]`.

```php
public function __construct(
    #[AutowireIterator('app.my_tag')]
    private iterable $services,
) {
}
```

Semantic configuration on 7.4+ returns an array instead of calling a fluent builder.

```php
return App::config([
    'framework' => [
        'secret' => env('APP_SECRET'),
        'esi' => true,
        'session' => [
            'handler_id' => null,
            'cookie_secure' => 'auto',
            'cookie_samesite' => 'lax',
        ],
    ],
]);
```

## Sources

- https://symfony.com/doc/current/setup/upgrade_major.html
- https://symfony.com/releases
- https://github.com/symfony/symfony/blob/5.4/UPGRADE-5.3.md
- https://github.com/symfony/symfony/blob/6.0/UPGRADE-6.0.md
- https://github.com/symfony/symfony/blob/6.1/UPGRADE-6.1.md
- https://github.com/symfony/symfony/blob/6.4/UPGRADE-6.2.md
- https://github.com/symfony/symfony/blob/6.4/UPGRADE-6.4.md
- https://github.com/symfony/symfony/blob/7.0/UPGRADE-7.0.md
- https://github.com/symfony/symfony/blob/7.4/UPGRADE-7.4.md
- https://github.com/symfony/symfony/blob/8.0/UPGRADE-8.0.md
- https://github.com/symfony/symfony/blob/7.0/src/Symfony/Component/Security/Core/CHANGELOG.md
- https://github.com/symfony/symfony/blob/6.4/src/Symfony/Component/Console/CHANGELOG.md
- https://raw.githubusercontent.com/symfony/symfony/7.4/src/Symfony/Component/DependencyInjection/CHANGELOG.md
- https://symfony.com/blog/the-end-of-swiftmailer
- https://symfony.com/blog/new-in-symfony-7-4-deprecated-xml-configuration
- https://packagist.org/packages/symfony/swiftmailer-bundle
- https://packagist.org/packages/sensio/framework-extra-bundle
- https://github.com/sensiolabs/SensioFrameworkExtraBundle
- https://packagist.org/packages/friendsofsymfony/rest-bundle
- https://github.com/doctrine/DoctrineBundle/blob/3.0.0/UPGRADE-3.0.md
- https://github.com/doctrine/orm/blob/3.0.0/UPGRADE.md
- https://symfony.com/doc/current/controller/value_resolver.html
