# Dependency Injection and Services

Use this reference when registering, wiring, decorating, tagging or lazily loading services in a Symfony 5.4..8.x application, or when reviewing container configuration.

## Container Basics

The service container is "an object that knows how to create and connect all the objects of your application". It is PSR-11 compatible and compiled; the compiled container is cached in `var/cache/`. Services are shared (the same instance every time), created only when requested, private by default, and identified by their FQCN.

- **Use**: keep `_defaults: {autowire: true, autoconfigure: true}` and the `App\: resource: '../src/'` block. Get services from the container as few times as possible, at the entry point of the application.
- **Do not**: get private services with `$container->get()` (they can only be injected); make services public without a need; for runtime lookups use a service locator. Do not inject the whole container (`ContainerAwareInterface` and `ContainerAwareTrait` are deprecated in 6.4 and removed in 7.0).
- **Pros**: no runtime overhead with the compiled container; unused private services are removed from the final container.
- **Pitfalls**:
  - `_defaults` applies only to services in the same `services` block. Each `when@<env>` block has its own scope and does not inherit `_defaults`; redefine it there.
  - Imports are processed first and later definitions override earlier ones, so the `App\` auto-discovery can override services defined in imported files. Fix: exclude the class, redefine the service after `App\`, or move auto-discovery to an earlier import.
  - `public` is not inherited from an import.
  - Excluded paths are not tracked in `dev`; changes there do not rebuild the container.
  - Parameters cannot build `imports` paths, and parameters can only be set before compilation.
  - Scalars cannot be autowired; use `#[Autowire]` or explicit `arguments`. A literal string starting with `@` is written `'@@securepassword'`.
  - Inject `RequestStack` and call `getCurrentRequest()`.
- **Tooling**: `debug:container` (`--show-hidden`, `--tag=...`), `debug:autowiring <term>`, `lint:container` (`--resolve-env-vars`). `lint:container` runs `CheckTypeDeclarationsPass` and `CheckAliasValidityPass`, disabled by default because of their performance cost.

`#[When(env: 'dev')]` and `#[WhenNot(env: 'dev')]` register a class only in (or outside) one environment and can be stacked; `#[Exclude]` excludes one class from discovery.

```php
#[When(env: 'dev')]
final class FakeSmsSender implements SmsSenderInterface
{
}

#[Exclude]
final class SomeService
{
}
```

| 5.4 | 6.4 | 7.x | 8.x |
| --- | --- | --- | --- |
| `#[When]` (5.3) | `#[Exclude]` (6.3) | same | `exclude` option for `imports` (8.1); XML config and fluent PHP config format removed (8.0); `debug:container --show-arguments` removed (8.0) |

## Autowiring, Aliases, `#[Autowire]` and `#[Target]`

Autowiring reads constructor type-hints and looks for a service whose ID exactly matches the type. If no service matches, or the dependency is not clear, it throws an actionable exception. With a prototype definition, if only one discovered service implements an interface, the alias is created automatically.

- **Use**: an alias when the service ID differs from the type; a named autowiring alias (type plus argument name) or `#[Target]` when several services implement one interface; `#[Autowire]` for parameters, env vars and specific service IDs.
- **Do not**: rely on autowiring in public bundles; define their services explicitly. Autowiring is fine in internal company bundles. Property injection with `#[Required]` works but "has drawbacks".
- **Pros**: predictable; no runtime penalty with the compiled container.
- **Cons**: in `dev` the container may be rebuilt more often; on very large projects rebuilds can be slow enough to make autowiring impractical.
- **Pitfalls**: `#[Target]` does not accept service IDs or aliases, only named alias names (normalised to camelCase); a typo throws an exception. Optional dependency: nullable type with `null` default.

```php
final class Newsletter
{
    public function __construct(
        #[Target('shoutyTransformer')] private TransformerInterface $transformer,
        #[Autowire(service: 'monolog.logger.request')] private LoggerInterface $logger,
        #[Autowire('%kernel.project_dir%/data')] private string $dataDir,
        #[Autowire(param: 'kernel.debug')] private bool $debugMode,
        #[Autowire(env: 'bool:SOME_BOOL_ENV_VAR')] private bool $allowAttachments,
    ) {
    }
}
```

Config form, also for 5.4:

```yaml
services:
    _defaults:
        bind:
            $projectDir: '%kernel.project_dir%'
    App\Util\Rot13Transformer: ~
    App\Util\UppercaseTransformer: ~
    App\Util\TransformerInterface $shoutyTransformer: '@App\Util\UppercaseTransformer'
    App\Util\TransformerInterface: '@App\Util\Rot13Transformer'
```

| 5.4 | 6.4 | 7.x | 8.x |
| --- | --- | --- | --- |
| `#[Target]` (5.3); union and intersection types (5.4); `bind` | `#[Autowire]` (6.1), `param:`/`env:`, `#[AutowireServiceClosure]`, `#[AutowireCallable]` (6.3); compilation fails on a nonexistent `#[Target]` (6.3); `#[Target]` without arguments (6.4) | `@required` annotation removed, use `#[Required]` (7.0); `#[AutowireInline]`, `#[AutowireMethodOf]`, `#[Autowire(env:)]` cast to null or bool (7.1); `#[AsAlias]` `when` argument (7.3); `registerAliasForArgument()` `$target` (7.4) | same |

## Parameters

Key-value pairs stored in the container that centralise values used in several places and can be overridden per environment. The `app.` prefix is recommended to separate them from Symfony parameters.

- **Use**: configuration options in general ("In other cases, it's recommended to keep using configuration parameters").
- **Do not**: use them for options that depend on where the app runs or must change dynamically in production; use `%env(ENV_VAR_NAME)%`. For API keys or DB passwords use the secrets management system.
- **Pitfalls**: a literal `%` is doubled (`%%`); `%kernel.project_dir%` in `imports` does not work; names starting with a dot exist only during compilation; `parameterCannotBeEmpty()` is checked when the parameter is retrieved, not at compile time.
- **Access**: `#[Autowire(param: 'app.contents_dir')]` in services, `getParameter()` in `AbstractController`, `_defaults: bind:`, or `ContainerBagInterface` for many parameters. A default for an env var: `env(SECRET): 'some_secret'` under `parameters`.

```php
final class MessageGenerator
{
    public function __construct(
        #[Autowire(param: 'app.contents_dir')] private string $contentsDir,
    ) {
    }
}
```

## Tags, Autoconfiguration and Tagged Iterators

Tags are labels on service definitions. "Tags alone change nothing"; code must ask the container for tagged services. Tag attributes (`key`, `priority`) carry extra data per tagged service.

- **Use**: a tagged iterator to inject all services with a tag; "This avoids writing a compiler pass." `#[AutoconfigureTag]` on a base class or interface (needs `autoconfigure`); without a name the FQCN is used. For laziness, bindings or calls use `#[Autoconfigure]` instead.
- **Pros**: the iterator is lazy; services are created only when the loop reaches them.
- **Pitfalls**: in PHP config, call `instanceof` before any service registration or tags may not apply. The collecting service is excluded from its own iterator when it carries the tag (`exclude_self`; disable with `excludeSelf: false`). Priority is an integer, default `0`, higher comes earlier. Index order: `index_by` attribute, then `default_index_method`, then service ID.

```php
#[AutoconfigureTag('app.exporter')]
interface ExporterInterface
{
    public function supports(string $format): bool;
}

#[AsTaggedItem(index: 'csv', priority: 10)]
final class CsvExporter implements ExporterInterface
{
    public function supports(string $format): bool
    {
        return $format === 'csv';
    }
}

final class ExportRegistry
{
    public function __construct(
        #[AutowireIterator('app.exporter')] private iterable $exporters,
    ) {
    }
}
```

`#[AutoconfigureResourceTag]` (7.4) tags classes such as entities or DTOs that are discoverable at compile time but never instantiated.

| 5.4 | 6.4 | 7.x | 8.x |
| --- | --- | --- | --- |
| `tagged_iterator` (`tagged` removed in 5.0); tagged iterators and locators via PHP 8 attributes, `#[AsTaggedItem]` (5.3); `defaultIndexMethod`, `defaultPriorityMethod` (5.4) | `exclude` (6.1); YAML/XML `exclude`, `excludeSelf` (6.2) | `!tagged` deprecated (7.2); repeatable `#[AsTaggedItem]`, `addResourceTag()`, `findTaggedResourceIds()` (7.3); autoconfiguration attributes on abstract classes parsed, `#[AutoconfigureResourceTag]` (7.4) | `#[TaggedIterator]` replaced by `#[AutowireIterator]`; `!tagged` removed; `findTaggedResourceIds()` gains `$throwOnAbstract` |

## Service Locators and Subscribers

A service locator is a PSR-11 `ContainerInterface` (and callable) holding only the declared services and creating each one on demand. A service subscriber implements `ServiceSubscriberInterface` and declares its dependencies in `getSubscribedServices()`.

- **Use**: runtime lookups; controllers injecting many services but using only some per action; command buses mapping command classes to handlers.
- **Do not**: inject the entire container; it gives broad access to services, hides real dependencies and requires services to be public.
- **Pros**: easy to test with a fake `ServiceLocator` subclass or a mock of `ContainerInterface`.
- **Pitfalls**: an optional service is prefixed with `?`; call `has()` before using it. If subscribed services are not found, check autoconfigure or add the `container.service_subscriber` tag. When a parent class (e.g. `AbstractController`) implements `ServiceSubscriberInterface`, merge `parent::getSubscribedServices()`. In helper traits use `__CLASS__.'::'.__FUNCTION__`, not `__METHOD__`, as the service ID.

```php
final class CommandBus implements ServiceSubscriberInterface
{
    public function __construct(
        private ContainerInterface $locator,
    ) {
    }

    public static function getSubscribedServices(): array
    {
        return [
            'App\FooCommand' => FooHandler::class,
            'App\BarCommand' => BarHandler::class,
        ];
    }
}
```

| 5.4 | 6.4 | 7.x | 8.x |
| --- | --- | --- | --- |
| `#[TaggedLocator]` (5.3, PHP 8); `ServiceSubscriberTrait` + `#[SubscribedService]` (5.4; the old no-argument method form deprecated) | same | same | `#[TaggedLocator]` replaced by `#[AutowireLocator]` |

## Decoration

Decoration implements the Decorator pattern. Redefining a service ID loses the original; decorating keeps it available to the decorator as `.inner` (the decorator ID plus `.inner`).

- **Use**: when the original class belongs to Symfony or a third-party package, or when unrelated features should not be mixed into one class.
- **Pitfalls**: custom tags on the decorated service move to the decorator; built-in tags (`container.service_locator`, `container.service_subscriber`, `kernel.event_subscriber`, `kernel.event_listener`, `kernel.locale_aware`, `kernel.reset`) do not. A higher `priority` (`decoration_priority`) is applied earlier, closer to the original. Type the inner argument only when the original and all decorators implement the same interface. With more than one argument of the decorated type, or without autowiring, inject `@.inner` explicitly. A compiler pass that creates definitions to decorate must run in `PassConfig::TYPE_BEFORE_OPTIMIZATION`. `decoration_on_invalid`: `exception` (default), `ignore` (decorator removed), `null` (declare the argument nullable).

```php
#[AsDecorator(decorates: Mailer::class)]
final class LoggingMailer
{
    public function __construct(
        #[AutowireDecorated] private Mailer $mailer,
        private LoggerInterface $logger,
    ) {
    }
}
```

5.4 form:

```yaml
services:
    App\DecoratingMailer:
        decorates: App\Mailer
        arguments: ['@.inner']
```

A `stack` defines a new service and by default replaces nothing; frames are listed outermost first. Priorities suit decorators spread across files or bundles; stacks suit one explicit chain (`stack: [{class: App\RateLimitingMailer, arguments: ['@.inner']}, ...]`).

| 5.4 | 6.4 | 7.x | 8.x |
| --- | --- | --- | --- |
| `decorates`, `decoration_priority`, `decoration_on_invalid`; `.inner` and `stack` (5.1) | `#[AsDecorator]` (6.1); `#[AutowireDecorated]`, `#[MapDecorated]` deprecated (6.3) | `#[MapDecorated]` removed (7.0); multiple `#[AsDecorator]` on one class (7.4) | `#[AsTagDecorator]` / `decorates_tag`, `decorates` on stacks (8.1) |

## Lazy Services and Service Closures

A lazy service is a proxy injected in place of the real service and initialised on first access. `#[AutowireServiceClosure]` injects a `\Closure` that returns the service.

- **Use**: a heavy service injected into an object that does not always use it. A service closure for lazy loading and for non-shared dependencies (a non-shared service passed to a constructor is created once and reused).
- **Pitfalls**: marking the service lazy applies everywhere; `#[Lazy]` on one argument, or `#[Autowire(service: ..., lazy: true)]`, limits it to one injection. On PHP older than 8.4, lazy services do not support `final` or `readonly` classes unless the proxy is restricted to an interface; such a proxy implements only those interfaces, so a concrete-class type-hint cannot receive it. In 5.4 the `lazy` flag is ignored without `symfony/proxy-manager-bridge`.

```php
final class ReportController
{
    public function __construct(
        #[AutowireServiceClosure(PdfRenderer::class)] private \Closure $pdfRenderer,
        #[Lazy] private GeoIpLookup $geoIp,
        #[Lazy(TextFormatterInterface::class)] private TextFormatterInterface|HtmlFormatterInterface $formatter,
    ) {
    }
}
```

5.4 form: `lazy: true` in config or `#[Autoconfigure(lazy: true)]`, plus `composer require symfony/proxy-manager-bridge`.

| 5.4 | 6.4 | 7.x | 8.x |
| --- | --- | --- | --- |
| `lazy: true` with the ProxyManager bridge; `#[Autoconfigure(lazy:)]` | ghost objects and virtual proxies by default (6.2); lazy closures, `#[Autowire(lazy:)]` (6.3) | `#[Lazy]` (7.1); native lazy objects used when possible (7.3) | `LazyGhostTrait`, `LazyProxyTrait` removed; use native lazy objects |

## Factories

A factory is "a class or callable whose main purpose is to create and return other objects".

- **Use**: when creating an object requires special logic that should not live in the object itself, such as selecting the concrete class or running code after instantiation.
- **Pitfalls**: the `class` option has no effect on the resulting service, but compiler passes may read it. Factory method arguments are autowired when autowiring is on; otherwise use `arguments`.

```php
#[Autoconfigure(constructor: 'create')]
final class NewsletterSender
{
    public static function create(): self
    {
        return new self();
    }
}
```

Config forms: static `factory: ['App\Email\NewsletterSenderStaticFactory', 'createNewsletterSender']`; service `factory: ['@App\Email\NewsletterSenderFactory', 'createNewsletterSender']`; invokable `factory: '@App\Email\InvokableNewsletterSenderFactory'`; own class `factory: [null, 'create']`; expression `factory: '@=parameter("kernel.debug") ? service("traceable_newsletter") : service("newsletter")'` (6.1).

## Compiler Passes

Code implementing `CompilerPassInterface::process(ContainerBuilder $container): void` that changes service definitions while the container compiles.

- **Use**: changing services before use: adding or removing them, replacing arguments, tags, aliases, decoration.
- **Do not**: write one only to inject tagged services (use a tagged iterator); call `get()`/`set()` (they create instances; use `Reference`); use `resolveEnvPlaceholders(..., true)` (the cache must be cleared manually when the env var changes).
- **Pitfalls**: a missing definition breaks compilation, so check `has()` and return early. A service can carry the same tag more than once. Register in `Kernel::build()` with `addCompilerPass()`; phase (default before optimization) and priority (default `0`, higher earlier) decide order.

```php
final class ReportGeneratorPass implements CompilerPassInterface
{
    public function process(ContainerBuilder $container): void
    {
        if (!$container->has(ReportGeneratorRegistry::class)) {
            return;
        }

        $definition = $container->findDefinition(ReportGeneratorRegistry::class);

        foreach ($container->findTaggedServiceIds('app.report_generator') as $id => $tags) {
            foreach ($tags as $attributes) {
                $definition->addMethodCall('addGenerator', [new Reference($id), $attributes['format']]);
            }
        }
    }
}
```

Versions: `CheckAliasValidityPass` (7.1). 8.0 removes `getAutoconfiguredAttributes()` in favour of `getAttributeAutoconfigurators()`. 8.1 lets a kernel or bundle class implement `CompilerPassInterface` itself instead of calling `addCompilerPass($this)`.

## Sources

- https://symfony.com/doc/8.1/service_container.html
- https://symfony.com/doc/6.4/service_container/autowiring.html
- https://symfony.com/doc/7.4/service_container/tags.html
- https://symfony.com/doc/5.4/service_container/service_decoration.html
- https://symfony.com/doc/8.1/service_container/decoration.html
- https://symfony.com/doc/5.4/service_container/lazy_services.html
- https://symfony.com/doc/8.1/service_container/lazy_services.html
- https://symfony.com/doc/5.4/service_container/service_subscribers_locators.html
- https://symfony.com/doc/8.1/service_container/factories.html
- https://symfony.com/doc/8.1/service_container/compiler_passes.html
- https://symfony.com/doc/8.1/service_container/parameters.html
- https://github.com/symfony/symfony/blob/8.0/UPGRADE-8.0.md
- https://raw.githubusercontent.com/symfony/symfony/7.4/src/Symfony/Component/DependencyInjection/CHANGELOG.md
- https://github.com/symfony/symfony/blob/6.4/UPGRADE-6.4.md
- https://github.com/symfony/symfony/blob/7.0/UPGRADE-7.0.md
- https://symfony.com/doc/current/service_container/shared.html
