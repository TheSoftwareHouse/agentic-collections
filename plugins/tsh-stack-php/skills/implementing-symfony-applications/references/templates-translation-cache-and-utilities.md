# Templates, Translation, Session, Cache and Utilities in Symfony

Use this reference when you render Twig templates, translate messages, touch the session, cache data in pools with tags, generate UUIDs or ULIDs, or manipulate strings with the String component in a Symfony project.

## Table of Contents

- [Twig Templates](#twig-templates)
- [Translation](#translation)
- [Session](#session)
- [Cache Pools and Tags](#cache-pools-and-tags)
- [Uid Component](#uid-component)
- [String Component](#string-component)
- [Sources](#sources)

## Twig Templates

**What it is.** Templating with automatic output escaping, inheritance and blocks. Controllers render with `render()` (returns a `Response`), `renderView()` (returns only the contents), `renderBlock()` / `renderBlockView()` (one block), `stream()` (returns a `StreamedResponse`), or the `#[Template]` attribute on an action returning an array.

**When to use.**

- `renderBlock()` for blocks in template inheritance or for Turbo Streams.
- `stream()` to send contents to the browser while Twig renders, instead of rendering the entire template first.
- `{{ render(controller(...)) }}` only when you specifically need to run a controller as a sub-request, for example to cache that fragment separately with ESI.

**When not to use.** Embedded controllers for most reusable UI units: prefer Twig Components.

**Pros.** Safe by default through automatic output escaping. Symfony recommends three-level inheritance for medium and complex applications: `templates/base.html.twig`, `templates/layout.html.twig`, and `templates/*.html.twig`.

**Pitfalls.**

- `|raw` disables escaping; use it only for a trusted variable that contains HTML.
- With `extends`, a child template may not define content outside a block; it throws a `SyntaxError`.
- Each embedded controller is a request plus template rendering; embedding many hurts performance. If possible, cache the fragment. Fragments are served through a special URL (`fragments: { path: /_fragment }`), not a regular route.
- `stream()` sends headers before rendering, so the template cannot change them. Set cookies or start the session in the controller (for a CSRF token in the template, call `$request->getSession()->start()`). An error during rendering cannot change the status code anymore.
- Extensions built on `AbstractExtension` are all initialised before any template renders, even unused ones. Attribute-based extensions are already lazy-loaded.
- Use snake_case for files and directories (`blog_posts.html.twig`) and two extensions, the first being the output format (`index.html.twig`, `blog_posts.xml.twig`). The `_` prefix for fragments (`blog/_user_profile.html.twig`) is an optional convention.

```php
final class AppExtension
{
    #[AsTwigFilter('price')]
    public function formatPrice(float $number): string
    {
        return number_format($number, 2);
    }
}
```

Before 7.3, extend `AbstractExtension` and override `getFilters()` / `getFunctions()`. Tag the class `twig.extension`; the default `services.yaml` does it for you.

```php
final class AppExtension extends AbstractExtension
{
    public function getFilters(): array
    {
        return [new TwigFilter('price', [AppRuntime::class, 'formatPrice'])];
    }
}
```

**Versions.**

| Version | Change |
| --- | --- |
| 6.2 | `#[Template]` attribute; `app.current_route` and `app.current_route_parameters` |
| 6.3 | `app.locale` |
| 6.4 | `app.enabled_locales`; `renderBlock()` and `renderBlockView()` |
| 7.1 | `lint:twig` excludes option |
| 7.2 | `#[Template]` `block` argument |
| 7.3 | `#[AsTwigFilter]`, `#[AsTwigFunction]`, `#[AsTwigTest]` on a plain class method |

## Translation

**What it is.** The `translator` service and its `trans()` method, for example `$translator->trans('Symfony is great', locale: 'fr_FR')`. Catalog files are named `domain.locale.loader` (`messages.fr.yaml`, `messages.fr.xlf`). ICU placeholders use `{name}` instead of `%name%` and need the `+intl-icu` suffix (`messages+intl-icu.en.yaml`).

**When to use.**

- `TranslatableMessage` or the `t()` shortcut (Twig and PHP, `use function Symfony\Component\Translation\t;`) to create translatable objects. Translatable parameters are translated in the same locale as their message.
- `TranslatableInterface` on any class, such as an enum, for more control. Such objects work with the `trans` Twig filter and as translation parameters.
- `LocaleSwitcher::runWithLocale()` to run code in a given locale temporarily. It changes services tagged `kernel.locale_aware`, `\Locale::setDefault()` and the `_locale` parameter of `RequestContext`.
- Global translation parameters (`translator: globals:`) for a value repeated across messages, such as a company name.

**When not to use.** For a message that must never be translated, use `StaticMessage`.

**Pros.** Translation providers (Crowdin, Loco, Lokalise, Phrase) with `translation:push` and `translation:pull`.

**Pitfalls.**

- `$request->setLocale()` in the controller is too late for the translator. Use the `_locale` route parameter, or a listener that runs before `LocaleListener` (higher priority).
- `LocaleSwitcher` applies the locale only to the current request; it is lost after a redirect.
- The `|trans` filter escapes output (add `|raw` after it to avoid that). The `{% trans %}` tag does not escape and requires `%var%` placeholders.
- The intl polyfills support only English; install the PHP `intl` extension to translate into other languages.
- Catalogs compile to `var/cache/<env>/translations/`. With debug off, changed files are not detected: after editing existing files in production delete `var/cache/prod/translations/`; after adding new files clear the entire cache.
- `lint:yaml` and `lint:xliff` check syntax, not contents; `lint:translations` checks contents. Find gaps with `debug:translation en --only-missing` or `--only-unused`.
- `translation:pull --force` overwrites local files completely. Phrase needs a user agent in the DSN and RFC 4646 locale names (`pt-BR`).

```php
enum UserRole: string implements TranslatableInterface
{
    case Admin = 'admin';
    case Editor = 'editor';

    public function trans(TranslatorInterface $translator, ?string $locale = null): string
    {
        return $translator->trans('user_role.' . $this->value, locale: $locale);
    }
}
```

**Versions.**

| Version | Change |
| --- | --- |
| 5.2 | Translatable objects |
| 5.3 | Translation providers |
| 5.4 | `github` output format for `lint:xliff`; new catalogs need `cache:clear`; no `LocaleSwitcher` on the 5.4 page |
| 7.1 | Partial locale matching in `getPreferredLanguage()` |
| 7.2 | `lint:translations` and its `--no-fill` option |
| 7.3 | Global translation parameters |
| 7.4 | `StaticMessage` |

## Session

**What it is.** A replacement for `$_SESSION` and native PHP session functions, read through `$request->getSession()` or `RequestStack::getSession()`. Sessions start only when you read from or write to them.

**When to use.** Flash messages (meant to be used exactly once; `peek()` keeps them). Stateful CSRF protection in forms starts the session internally.

**When not to use.** Pages for anonymous users: reading, writing or even checking session data starts the session and gives every user a session cookie. Flash messages mark the response `private`; load them asynchronously, for example with a Twig Live Component, to keep the page fully cacheable.

**Pros.** Lazy start; `MigratingSessionHandler` moves between old and new save handlers without losing session data.

**Pitfalls.**

- Do not access the session in a constructor; it might not be accessible yet or cause side effects.
- `RedisSessionHandler` does not lock, and Memcached has the same limitation. Concurrent writes cause race conditions and "Invalid CSRF token" errors. Use PHP's native handler via `php.ini` (`redis.session.locking_enabled = 1`); PECL Memcached locks by default.
- `PdoSessionHandler` creates a `BLOB` column (64 KB); larger data throws or silently resets the session. Use `MEDIUMBLOB` for more space.
- The cookie lifetime can be manipulated by the client. Enforce an idle timeout on the server with `getMetadataBag()->getLastUsed()`.
- Keep `session.auto_start = 1` off; it is incompatible.

```php
public function __construct(private readonly RequestStack $requestStack)
{
}

public function rememberStep(int $step): void
{
    $this->requestStack->getSession()->set('checkout.step', $step);
}
```

```yaml
framework:
    session:
        cookie_secure: auto
        cookie_samesite: lax
```

**Versions.** 7.2 takes `gc_probability` from `php.ini` by default and deprecates `sid_length` and `sid_bits_per_character` (ignored in 8.0). 7.3 adds Valkey DSN schemes.

## Cache Pools and Tags

**What it is.** Cache pools over pre-configured adapters (`apcu`, `array`, `doctrine_dbal`, `filesystem`, `memcached`, `pdo`, `psr6`, `redis`, `redis_tag_aware`, `valkey`, `valkey_tag_aware`, `system`) and the Cache Contracts. `cache.app` is the general-purpose pool for application code; `cache.system` is used internally by Symfony.

**When to use.** `cache.system` for your own data only if entries are derivable from source code, regenerable by a `CacheWarmer`, and change only on deployment. A chain pool to combine several pools, ordered fastest to slowest.

**When not to use.** `cache.system` for data that changes at runtime.

**Pros.** Built-in stampede prevention: locking plus probabilistic early expiration through the third argument `$beta` (default `1.0`, higher recomputes earlier, `0` disables, `INF` forces). `$beta` acts only when the item has an expiration.

**Pitfalls.**

- `cache.app` defaults to the filesystem. Configure Redis when available so data survives deployments and is shared across servers.
- Custom pools use `cache.app` as adapter unless configured otherwise.
- Tags need a pool implementing `TagAwareCacheInterface` (`tags: true`, or `cache.adapter.redis_tag_aware` on Redis). Type-hinting `TagAwareCacheInterface` autowires `cache.app.taggable`.
- `FilesystemAdapter` removes expired items only when they are requested; run `cache:pool:prune`.
- `SodiumMarshaller` (decorating `cache.default_marshaller`) encrypts values, not keys. With several keys, the first reads and writes.
- There is no built-in invalidation by namespace. With `withSubNamespace()`, change the namespace instead.
- `early_expiration_message_bus` returns the cached value at once and dispatches an `EarlyExpirationMessage`; a `messenger:consume` worker must run.
- Chain adapters and `PhpFilesAdapter` are not pre-configured services.

```yaml
framework:
    cache:
        pools:
            catalog.cache:
                adapter: cache.adapter.redis_tag_aware
                default_lifetime: 60
```

```php
final class CatalogQuery
{
    public function __construct(
        private readonly TagAwareCacheInterface $cache,
        private readonly ProductReadModel $products,
    ) {
    }

    public function category(int $id): array
    {
        return $this->cache->get('category_' . $id, function (ItemInterface $item) use ($id): array {
            $item->tag(['category_' . $id]);

            return $this->products->forCategory($id);
        });
    }

    public function invalidate(int $id): void
    {
        $this->cache->invalidateTags(['category_' . $id]);
    }
}
```

**Versions.** 7.2 requires enabling Igbinary support explicitly in `DefaultMarshaller`. 7.3 adds the `valkey` and `valkey_tag_aware` adapters.

## Uid Component

**What it is.** UUID v1, v3, v4, v5, v6, v7 and v8 (v2 is not implemented) and ULID (128-bit, 26-character string) value objects, factories and Doctrine types. The factory defaults are v7 for default and time-based UUIDs, v5 for name-based and v4 for random-based.

**When to use.** ULIDs as an alternative when UUIDs are impractical. `MockUuidFactory` to control UUIDs in tests.

**When not to use.** UUIDs as primary keys are usually not recommended for performance. Only v6 and v7 solve index fragmentation; index size remains. ULID indexes are slower and larger. Prefer v7 over v6 for better entropy.

**Pitfalls.**

- Create ids through `UuidFactory` (`create()`, `randomBased()`, `nameBased($namespace)`, `timeBased($node)`) so tests can use `MockUuidFactory`. It throws when its sequence is exhausted or types do not match.
- Query parameters need the type: `setParameter('user', $user->getUuid(), UuidType::NAME)`, or `UlidType::NAME` for ULIDs.
- `UuidGenerator::class` bypasses `doctrine.uuid_generator`, so the configured UUID version is ignored. Reference `doctrine.uuid_generator`.
- `isValid()` accepts only RFC 4122 by default.
- v8 values must be generated by you.

```php
#[ORM\Entity]
class Invoice
{
    #[ORM\Id]
    #[ORM\Column(type: UuidType::NAME)]
    #[ORM\GeneratedValue(strategy: 'CUSTOM')]
    #[ORM\CustomIdGenerator('doctrine.uuid_generator')]
    private ?Uuid $id = null;
}
```

**Versions.**

| Version | Change |
| --- | --- |
| 5.1 | Uid component |
| 5.2 | `uuid` Doctrine type |
| 5.3 | `UuidFactory`; `getDateTime()` (previously `getTime()`) |
| 5.4 | `NilUlid`; factory default v6, name-based v5; v6 not yet part of the UUID standard; docs cover v1 to v6 |
| 6.2 | UUID v7 and v8; `UuidType::NAME` and `UlidType::NAME` |
| 7.1 | `toString()`; `toV6()` and `toV7()` |
| 7.2 | `isValid()` `$format` parameter and constants |
| 7.4 | Default and time-based versions become v7 (previously v6); v7 precision goes from milliseconds to microseconds |

## String Component

**What it is.** `u()` creates Unicode strings, `b()` byte strings, and `s()` picks one from the contents. Also `SluggerInterface` / `AsciiSlugger` and the English, French and Spanish inflectors.

**When to use.** `AsciiSlugger` for URLs and file or directory names, where any Unicode character is not safe.

**Pitfalls.**

- Case and similar methods return a copy of the string; use the returned value.
- Inflectors always return an array, because a unique singular or plural form is not always possible: `singularize('teeth')` gives `['tooth']`, `pluralize('person')` gives `['persons', 'people']`.
- An injected `SluggerInterface` uses the request locale. For another locale use `new AsciiSlugger('ko')` or the third argument of `slug()`. The slugger transliterates to Latin script first.
- `truncate()` defaults to `TruncateMode::Char`; `WordBefore` and `WordAfter` keep whole words.

```php
$slug = $this->slugger->slug('Wôrķšƥáçè ~~sèťtïñğš~~');
$name = u('Foo: Bar-baz.')->kebab();
```

**Versions.** 7.1 adds `localeLower()`, `localeUpper()`, `localeTitle()`. 7.2 adds `kebab()`, the `TruncateMode` parameter and `SpanishInflector`. 7.3 adds `pascal()`.

## Sources

- https://symfony.com/doc/7.4/templates.html
- https://symfony.com/doc/6.4/templates.html
- https://symfony.com/doc/7.4/translation.html
- https://symfony.com/doc/6.4/translation.html
- https://symfony.com/doc/5.4/translation.html
- https://symfony.com/doc/7.4/session.html
- https://symfony.com/doc/7.4/cache.html
- https://symfony.com/doc/7.4/components/uid.html
- https://symfony.com/doc/6.4/components/uid.html
- https://symfony.com/doc/5.4/components/uid.html
- https://symfony.com/doc/7.4/string.html
