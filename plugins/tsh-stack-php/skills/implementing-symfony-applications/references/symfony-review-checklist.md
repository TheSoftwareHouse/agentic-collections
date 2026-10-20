# Symfony Review Checklist

Use this reference when you review Symfony 5.4..8.x code — a pull request, a changed file set or a whole feature — and need concrete, severity-tagged checks that point back to the reference owning each rule.

## Review Workflow

- [ ] Determine the Symfony and PHP versions first with [`symfony-version-detection.md`](./symfony-version-detection.md) and state them in one line; ask when they cannot be determined.
- [ ] Identify the changed artifacts and select only the applicable groups below.
- [ ] Apply every `[BLOCKER]` and `[HIGH]` check before the lower-severity ones.
- [ ] Record each finding with its location, severity, violated rule and owning reference.
- [ ] Apply the output rules at the end.

## Table of Contents

- [Version Correctness](#version-correctness)
- [Necessity and Reuse](#necessity-and-reuse)
- [Services and DI](#services-and-di)
- [Configuration](#configuration)
- [Events and Kernel](#events-and-kernel)
- [HTTP Layer and Controllers](#http-layer-and-controllers)
- [Doctrine](#doctrine)
- [Forms and Validation](#forms-and-validation)
- [Serializer and Request Mapping](#serializer-and-request-mapping)
- [Security](#security)
- [Messenger and Async](#messenger-and-async)
- [Console, HttpClient and Operations](#console-httpclient-and-operations)
- [Templates, Translation, Session and Cache](#templates-translation-session-and-cache)
- [Testing](#testing)
- [Output Rules](#output-rules)

## Version Correctness

|Severity|Check|Owning reference|
|---|---|---|
|[BLOCKER]|The detected Symfony and PHP versions are stated before any finding; when they cannot be determined, the reviewer asks.|[SKILL.md](../SKILL.md); [symfony-version-detection.md](./symfony-version-detection.md)|
|[BLOCKER]|No API, attribute, config key or bundle is used that does not exist in the detected version or was removed in it.|[SKILL.md](../SKILL.md); [symfony-version-differences.md](./symfony-version-differences.md)|
|[BLOCKER]|On 6.0+ none of: Guard (`AbstractGuardAuthenticator`, `guard:`), `getUsername()`, `IS_AUTHENTICATED_ANONYMOUSLY`/`AnonymousToken`, `UserPasswordEncoderInterface`/`Core\Encoder\`, `$this->get()`/`getDoctrine()`/`dispatchMessage()` in controllers, `isMasterRequest()`/`MASTER_REQUEST`, `service:action` controllers, `RouteCollectionBuilder`.|[symfony-version-differences.md](./symfony-version-differences.md)|
|[BLOCKER]|On 7.0+ none of: Doctrine annotations in Routing, Serializer or Validator (`@Route`, `@Assert`, `@Groups`), `ContainerAwareInterface`/`ContainerAwareTrait`, `@required`, `#[MapDecorated]`, `Command::$defaultName`, `MessageHandlerInterface`/`MessageSubscriberInterface`, `ArgumentValueResolverInterface`, `renderForm()`, `Core\Security`, `CacheableSupportsMethodInterface`, `enable_authenticator_manager`, the Templating component, Doctrine event subscribers.|[symfony-version-differences.md](./symfony-version-differences.md); [doctrine-persistence.md](./doctrine-persistence.md)|
|[BLOCKER]|On 8.0+ none of: XML config, fluent config builders or `$this` in PHP config files, `#[TaggedIterator]`/`#[TaggedLocator]`, YAML `!tagged`, `Request::get()`, `eraseCredentials()`, `hide_user_not_found`, `getDefaultName()`, `Application::add()`, callable firewall listeners, automatic entity mapping to controller arguments.|[symfony-version-differences.md](./symfony-version-differences.md); [symfony-version-detection.md](./symfony-version-detection.md)|
|[BLOCKER]|Every added or used bundle has a release whose `require` allows the detected Symfony version: no SensioFrameworkExtraBundle on 7.x (`^4.4\|^5.0\|^6.0`), no `symfony/swiftmailer-bundle` on 6.x or later (`^4.4\|^5.0`).|[third-party-bundles.md](./third-party-bundles.md)|
|[HIGH]|Voter signatures match the version: on 8.x `voteOnAttribute()` declares `?Vote $vote = null`; on 5.4 and 6.x the `Vote` argument does not exist and is not added.|[security.md](./security.md)|
|[HIGH]|Doctrine code matches the installed ORM, DBAL and DoctrineBundle majors, not the Symfony version alone: on ORM 3 or DoctrineBundle 3 no annotation or YAML mapping, `merge()`, `flush($entity)`, `'App:Entity'` aliases, `Query::iterate()`, `transactional()`, `PARTIAL`, `EntityManager::create()`, `LifecycleEventArgs`.|[doctrine-persistence.md](./doctrine-persistence.md); [third-party-bundles.md](./third-party-bundles.md)|
|[HIGH]|Language features fit the PHP version: Symfony 8 needs PHP 8.4; on a 5.4 project running PHP 7, routes use docblock annotations and handlers implement `MessageHandlerInterface` instead of attributes.|[symfony-version-detection.md](./symfony-version-detection.md); [http-layer.md](./http-layer.md); [messenger-and-async.md](./messenger-and-async.md)|
|[MEDIUM]|New code does not introduce an API deprecated in the detected version when its replacement exists there (for example `Request::get()` or XML config on 7.4, `!tagged` on 7.2+, `$defaultName` on 6.1+).|[symfony-version-differences.md](./symfony-version-differences.md)|

## Necessity and Reuse

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|No new service, listener, voter, normalizer, constraint or command duplicates one the project or the framework already provides.|[SKILL.md](../SKILL.md)|
|[HIGH]|No bundle or Composer package is added when the framework or an installed package covers the need; abandoned or discouraged packages (`sensio/framework-extra-bundle`, `symfony/swiftmailer-bundle`, `doctrine/annotations`, FOSUserBundle) never enter new code, and native alternatives (`#[MapRequestPayload]` for FOSRestBundle, the `access_token` authenticator for LexikJWT, `symfony/mailer` for Swiftmailer) are considered first.|[SKILL.md](../SKILL.md); [third-party-bundles.md](./third-party-bundles.md)|
|[MEDIUM]|Every framework feature used (event, Messenger, compiler pass, decorator, voter, custom normalizer) has a stated reason; a plain service method call is used where it does the job.|[SKILL.md](../SKILL.md)|
|[MEDIUM]|The code follows PSR-12, the project's coding standard and the PHP version rules of `architecting-php-code`.|[SKILL.md](../SKILL.md)|

## Services and DI

|Severity|Check|Owning reference|
|---|---|---|
|[BLOCKER]|No service is pulled from the container at runtime (`$container->get()`, `ContainerAwareInterface`, the whole container injected); dependencies arrive through the constructor, and runtime lookups use a service locator or subscriber.|[SKILL.md](../SKILL.md); [dependency-injection-and-services.md](./dependency-injection-and-services.md)|
|[HIGH]|Services inject `RequestStack` and call `getCurrentRequest()`; the session is never accessed in a constructor.|[dependency-injection-and-services.md](./dependency-injection-and-services.md); [templates-translation-cache-and-utilities.md](./templates-translation-cache-and-utilities.md)|
|[MEDIUM]|Services are not made public without a need; scalars are injected with `#[Autowire]`, `bind` or explicit `arguments`.|[dependency-injection-and-services.md](./dependency-injection-and-services.md)|
|[MEDIUM]|`_defaults` is redefined inside every `when@<env>` block that needs it; a service defined in an imported file is not silently overridden by the later `App\` auto-discovery.|[dependency-injection-and-services.md](./dependency-injection-and-services.md)|
|[MEDIUM]|One of several implementations is selected with a named autowiring alias or `#[Target]`, and `#[Target]` names an alias, not a service ID.|[dependency-injection-and-services.md](./dependency-injection-and-services.md)|
|[MEDIUM]|Tagged services are collected with a tagged iterator or locator, not a compiler pass written only for that.|[dependency-injection-and-services.md](./dependency-injection-and-services.md)|
|[MEDIUM]|Decoration wraps a Symfony or third-party service, or keeps unrelated features out of one class; it accounts for built-in tags (`kernel.event_subscriber`, `kernel.reset`, …) not moving to the decorator.|[dependency-injection-and-services.md](./dependency-injection-and-services.md)|
|[LOW]|A lazy service has a reason (a heavy dependency not always used), is limited with `#[Lazy]` or `#[Autowire(lazy:)]` when only one injection needs it, has `symfony/proxy-manager-bridge` on 5.4, and is not a `final`/`readonly` class on PHP below 8.4 without an interface proxy.|[dependency-injection-and-services.md](./dependency-injection-and-services.md)|
|[LOW]|A compiler pass checks `has()` and returns early, is registered in `Kernel::build()`, uses `Reference` instead of `get()`/`set()`, and does not call `resolveEnvPlaceholders(..., true)`.|[dependency-injection-and-services.md](./dependency-injection-and-services.md)|
|[LOW]|A factory exists only where creation needs logic that does not belong in the object; `#[Required]` property injection is avoided.|[dependency-injection-and-services.md](./dependency-injection-and-services.md)|

## Configuration

|Severity|Check|Owning reference|
|---|---|---|
|[BLOCKER]|No production value or credential sits in committed `.env`, parameters or config; sensitive values live in the secrets vault; `prod.decrypt.private.php` is never committed; nothing dumps `$_SERVER`, `$_ENV` or `phpinfo()`.|[configuration-and-environments.md](./configuration-and-environments.md)|
|[HIGH]|No new XML config and no fluent config builder or `$this` in `config/*.php` on 7.4+.|[configuration-and-environments.md](./configuration-and-environments.md)|
|[HIGH]|Code does not read `$_ENV` or `$_SERVER`; env vars arrive through `%env()%`, `#[Autowire(env:)]` (6.3+) or `bind`, with a processor (`int:`, `bool:`, `json:` …) where a non-string is needed.|[configuration-and-environments.md](./configuration-and-environments.md)|
|[MEDIUM]|Each value sits in the right mechanism: rarely changing values as class constants, application behaviour as `app.`-prefixed parameters, per-machine infrastructure as env vars, sensitive values in the vault; application-behaviour options are not env vars.|[configuration-and-environments.md](./configuration-and-environments.md)|
|[MEDIUM]|The web profiler is not enabled in production.|[configuration-and-environments.md](./configuration-and-environments.md)|
|[MEDIUM]|No `test` vault (test values go in `.env.test`), and no env var accidentally shares a name with a secret it would override.|[configuration-and-environments.md](./configuration-and-environments.md)|
|[LOW]|Parameters use the `app.` prefix with one or two words, double a literal `%`, and are not used to build `imports` paths.|[configuration-and-environments.md](./configuration-and-environments.md)|
|[LOW]|No bundle to organise the application's own logic and no Config component tree for application options that are not reused with rigid validation; a reusable bundle defines its services explicitly, without autowiring, with IDs prefixed by its alias.|[configuration-and-environments.md](./configuration-and-environments.md)|

## Events and Kernel

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|Business rules do not live in listeners or subscribers.|[SKILL.md](../SKILL.md)|
|[MEDIUM]|Kernel request listeners check `isMainRequest()`.|[events-and-kernel.md](./events-and-kernel.md)|
|[MEDIUM]|Listener priority was chosen after checking `debug:event-dispatcher`; `stopPropagation()` is meant to skip every later listener.|[events-and-kernel.md](./events-and-kernel.md)|
|[MEDIUM]|Work in `kernel.terminate` accounts for the server API (early flush only on PHP-FPM and FrankenPHP) and for the dev/prod difference.|[events-and-kernel.md](./events-and-kernel.md)|
|[LOW]|Data passes to listeners through a custom event class, not `GenericEvent`, outside prototypes.|[events-and-kernel.md](./events-and-kernel.md)|
|[LOW]|The dispatcher is injected through an interface, not the concrete `EventDispatcher`; the component interface is used only when listener inspection or removal is needed.|[events-and-kernel.md](./events-and-kernel.md)|
|[LOW]|A custom success status on `kernel.exception` uses `allowCustomResponseCode()`; stateful services in long-running processes implement `ResetInterface`.|[events-and-kernel.md](./events-and-kernel.md)|

## HTTP Layer and Controllers

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|Controllers stay thin: map the request, call a service, return a response; business rules live in services or entities.|[SKILL.md](../SKILL.md); [http-layer.md](./http-layer.md)|
|[HIGH]|`redirect()` never receives an unchecked user-supplied destination; it does not check its destination in any way.|[http-layer.md](./http-layer.md)|
|[HIGH]|Error pages for end users never output `exception.traceAsString`.|[http-layer.md](./http-layer.md)|
|[MEDIUM]|Routes using `Map*` attributes declare `format: 'json'` for JSON APIs so errors render as JSON, not HTML.|[http-layer.md](./http-layer.md); [serializer-and-request-mapping.md](./serializer-and-request-mapping.md)|
|[MEDIUM]|Request data is read from the right bag (`query`, `request`, `attributes`), not `Request::get()` (deprecated 7.4).|[http-layer.md](./http-layer.md)|
|[MEDIUM]|Routes have a unique `name`, `requirements` for constrained placeholders and `methods` where verbs are restricted.|[http-layer.md](./http-layer.md)|
|[MEDIUM]|Entity arguments use `#[MapEntity]` with explicit mapping or `{param:argument}` (7.1+), not `auto_mapping`.|[http-layer.md](./http-layer.md); [doctrine-persistence.md](./doctrine-persistence.md)|
|[LOW]|A custom value resolver returns an array (empty when it cannot resolve), uses priority `100`+ only when it reads request attributes, and is targeted with `#[AsTargetedValueResolver]` (6.3+) where it applies to few arguments.|[http-layer.md](./http-layer.md)|
|[LOW]|HTTP cache headers are set only on safe methods; a response that starts the session is private; headers set in the controller are expected to override `#[Cache]`.|[console-http-client-and-operations.md](./console-http-client-and-operations.md)|

## Doctrine

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|`flush()` is not called inside loops or from deep inside domain code; it runs once per use case at the application boundary (a request usually needs 0 to 2 flushes), and never from Doctrine event handlers.|[SKILL.md](../SKILL.md); [doctrine-persistence.md](./doctrine-persistence.md)|
|[HIGH]|Business rules do not live in Doctrine lifecycle callbacks or listeners; callbacks hold only very simple logic on one entity.|[SKILL.md](../SKILL.md); [doctrine-persistence.md](./doctrine-persistence.md)|
|[HIGH]|Schema changes ship as committed migrations generated with `make:migration` or `doctrine:migrations:diff`, not `doctrine:schema:update`; tables Doctrine does not manage are excluded with `schema_filter`.|[doctrine-persistence.md](./doctrine-persistence.md)|
|[MEDIUM]|Related data read for many rows is loaded with a join instead of one lazy query per row; an inverse side is mapped only when needed, since `contains()` on it can trigger heavy queries.|[doctrine-persistence.md](./doctrine-persistence.md)|
|[MEDIUM]|Relationships are set on the owning side; `OneToMany`/`ManyToMany` collections are initialised in the constructor; new related objects are cascaded or persisted; `orphanRemoval` is used where removed children must be deleted.|[doctrine-persistence.md](./doctrine-persistence.md)|
|[MEDIUM]|A query that fetch-joins a to-many collection is not limited with plain `LIMIT`/`setMaxResults()` or iterated with `toIterable()`; pagination uses Doctrine's paginator.|[doctrine-persistence.md](./doctrine-persistence.md)|
|[MEDIUM]|Bulk work uses DQL `UPDATE`/`DELETE` or batches with `flush()` and `clear()` every N items and `toIterable()`, not one fully hydrated set.|[doctrine-persistence.md](./doctrine-persistence.md)|
|[MEDIUM]|Event handlers respect Doctrine's limits: `preUpdate` changes only through `setNewValue()` and never associations; changes in `postPersist`/`postUpdate`/`postRemove` are not expected to persist; DQL `UPDATE`/`DELETE` fire no entity events.|[doctrine-persistence.md](./doctrine-persistence.md)|
|[LOW]|No reserved SQL keyword (`GROUP`, `USER`) as a table or column name; only backed enums as entity properties.|[doctrine-persistence.md](./doctrine-persistence.md)|
|[LOW]|A second entity manager has a concrete need, entities have no associations across managers, and an entity shared by managers does not use `ServiceEntityRepository`.|[doctrine-persistence.md](./doctrine-persistence.md)|

## Forms and Validation

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|External input is validated at the boundary: the object is actually passed to the validator (or a validated form or `Map*` argument); constraints alone enforce nothing.|[SKILL.md](../SKILL.md); [forms-and-validation.md](./forms-and-validation.md)|
|[HIGH]|Embedded objects carry `#[Assert\Valid]`; typed properties are initialised before validation; unmapped form fields carry their own `constraints`.|[forms-and-validation.md](./forms-and-validation.md)|
|[MEDIUM]|`createView()` is called after `handleRequest()`; on 6.2+ the form is passed to `render()` instead of `renderForm()`.|[forms-and-validation.md](./forms-and-validation.md)|
|[MEDIUM]|A transformer is attached to one field through `$builder->get()`, throws `TransformationFailedException` with a user-facing `invalid_message`, and is not used to map several fields (data mappers).|[forms-and-validation.md](./forms-and-validation.md)|
|[MEDIUM]|Form events are registered in `buildForm()`, do not modify their own form in `POST_SUBMIT`, and are not used for static conditions, conversion, validation or defaults.|[forms-and-validation.md](./forms-and-validation.md)|
|[MEDIUM]|Collections with `by_reference => false` have both adder and remover, the adder sets the owning side, and the association cascades persist.|[forms-and-validation.md](./forms-and-validation.md)|
|[LOW]|Custom constraint validators throw `UnexpectedTypeException` for a wrong constraint, return on `null`/`''`, throw `UnexpectedValueException` for unsupported values; a reusable set of built-ins extends `Compound` instead.|[forms-and-validation.md](./forms-and-validation.md)|
|[LOW]|`Default` is never listed in a group sequence (the class name is used); ordered checks on one property use `Sequentially`.|[forms-and-validation.md](./forms-and-validation.md)|
|[LOW]|On 7.3+ constraint constructors take named arguments, not options arrays; PATCH submits with `submit($data, false)`.|[forms-and-validation.md](./forms-and-validation.md)|

## Serializer and Request Mapping

|Severity|Check|Owning reference|
|---|---|---|
|[MEDIUM]|Validation failure codes match the API contract (`MapQueryString` gives 404 and `MapRequestPayload` 422 unless `validationFailedStatusCode` is set on 6.4+); an empty query string is handled by a default value.|[serializer-and-request-mapping.md](./serializer-and-request-mapping.md)|
|[MEDIUM]|Before 8.1, DTO properties use built-in types validated with constraints instead of enums or custom types, which leak internal class names on denormalization errors.|[serializer-and-request-mapping.md](./serializer-and-request-mapping.md); [http-layer.md](./http-layer.md)|
|[MEDIUM]|`allow_extra_attributes: false` is set where unknown keys must be rejected; `#[MaxDepth]` is paired with `ENABLE_MAX_DEPTH`; `DateTimeNormalizer` is registered for dates.|[serializer-and-request-mapping.md](./serializer-and-request-mapping.md)|
|[MEDIUM]|Custom normalizers implement `getSupportedTypes()` on 6.3+ (`CacheableSupportsMethodInterface` only before), use `NormalizerAwareInterface` instead of injecting `ObjectNormalizer`, decorate `serializer.normalizer.object` instead of extending it on 7.0+, and do not assume `getSupportedTypes()` ran before `supports*()`.|[serializer-and-request-mapping.md](./serializer-and-request-mapping.md)|
|[LOW]|A custom normalizer has a reason that `#[Groups]`, `#[SerializedName]`, `#[Ignore]` or `#[Context]` cannot cover; `IGNORED_ATTRIBUTES` is not overused; `#[SerializedPath]` and `#[SerializedName]` are not combined on one property.|[SKILL.md](../SKILL.md); [serializer-and-request-mapping.md](./serializer-and-request-mapping.md)|
|[LOW]|JsonStreamer is used only for DTOs with public properties and no constructor; `#[ValueTransformer]` callables make no database or API calls.|[serializer-and-request-mapping.md](./serializer-and-request-mapping.md)|

## Security

|Severity|Check|Owning reference|
|---|---|---|
|[BLOCKER]|Authorization uses the Security component (voters, `isGranted()`, `#[IsGranted]`, `access_control`), never ad-hoc role-string checks or reading `$user->getRoles()` manually.|[SKILL.md](../SKILL.md); [security.md](./security.md)|
|[BLOCKER]|State-changing operations do not use `GET` and are CSRF-protected (forms, `enable_csrf` on login forms, `isCsrfTokenValid()` or `#[IsCsrfTokenValid]` with the right `methods`); no CSRF token travels in a `GET` parameter.|[security.md](./security.md); [forms-and-validation.md](./forms-and-validation.md)|
|[HIGH]|Business rules that decide access, including roles stored in the database, live in voters, not in static `role_hierarchy` or scattered checks.|[security.md](./security.md)|
|[HIGH]|Authentication failures use `getMessageKey()`/`getMessageData()` or `CustomUserMessageAuthenticationException`, never `$exception->getMessage()`.|[security.md](./security.md)|
|[HIGH]|`SelfValidatingPassport` is used only when no credentials need checking; access token handlers check the token is valid, and for JWTs the signature and the `sub`, `iat`, `nbf` and `exp` claims.|[security.md](./security.md)|
|[HIGH]|Passwords use `password_hashers` (`auto`) with a `varchar(255)` column; custom hashers reject passwords longer than 4096 characters.|[security.md](./security.md)|
|[MEDIUM]|A firewall without `pattern` is defined last; every `access_control` path starts with `^`, remembering only the first match applies.|[security.md](./security.md)|
|[MEDIUM]|Voters implement `supportsAttribute()`/`supportsType()` with `is_a(..., true)` for Doctrine proxies, and use `AccessDecisionManager` instead of `Security::isGranted()` inside a voter.|[security.md](./security.md)|
|[MEDIUM]|Access tokens are not read from `query_string` or `request_body`; `Security::getFirewallConfig()` is not called in a constructor.|[security.md](./security.md)|
|[LOW]|Sensitive actions behind remember me require `IS_AUTHENTICATED_FULLY`; `switch_user` is limited to `ROLE_ALLOWED_TO_SWITCH` and a custom switch attribute does not start with `ROLE_`; on 8.x credentials are erased in `__serialize()`.|[security.md](./security.md)|

## Messenger and Async

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|Handlers are idempotent; a non-idempotent operation uses a key derived from the business event, checked in the handler and enforced by a database uniqueness constraint, never a UUID generated at dispatch.|[messenger-and-async.md](./messenger-and-async.md)|
|[HIGH]|Messages carry entity IDs, not entities; async email contexts hold simple values, not entities.|[messenger-and-async.md](./messenger-and-async.md); [doctrine-persistence.md](./doctrine-persistence.md)|
|[HIGH]|Webhooks have a `secret` in production, and a custom request parser checks the signature and throws `RejectWebhookException` for invalid requests.|[messenger-and-async.md](./messenger-and-async.md)|
|[MEDIUM]|A second bus exists only for a different middleware stack; `doctrine_transaction` sits on a command bus with `dispatch_after_current_bus` registered before it; long-running Doctrine workers use `doctrine_ping_connection`/`doctrine_close_connection`.|[messenger-and-async.md](./messenger-and-async.md)|
|[MEDIUM]|Async transports have a retry strategy and a failure transport; workers run under a supervisor with `--limit`/`--memory-limit`/`--time-limit` and `messenger:stop-workers` runs on deploy.|[messenger-and-async.md](./messenger-and-async.md); [console-http-client-and-operations.md](./console-http-client-and-operations.md)|
|[MEDIUM]|A changed message class stays compatible with queued messages (optional arguments with defaults, or a new class); a `'*'` routing rule does not route `SendEmailMessage` by accident.|[messenger-and-async.md](./messenger-and-async.md)|
|[MEDIUM]|Locks across hosts use a shared store, have a TTL, are released in `finally` and refreshed in long loops; `LockableTrait` is used only for one server.|[messenger-and-async.md](./messenger-and-async.md); [console-http-client-and-operations.md](./console-http-client-and-operations.md)|
|[MEDIUM]|Schedules run with `lock()` when several workers consume them, redispatch long work to an async transport, and are not used on 5.4.|[messenger-and-async.md](./messenger-and-async.md)|
|[LOW]|Workflow calls `can()` before `apply()`, persists a `multiple_state` marking as `json`, and disables the announce event when guards are expensive.|[messenger-and-async.md](./messenger-and-async.md)|
|[LOW]|`TransportInterface` is injected when the `SentMessage` is needed; notifications through Messenger have a running consumer; `sendmail://default` is preferred over `native://default`.|[messenger-and-async.md](./messenger-and-async.md)|

## Console, HttpClient and Operations

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|An HTTP client used with user-provided URIs is decorated with `NoPrivateNetworkHttpClient`.|[console-http-client-and-operations.md](./console-http-client-and-operations.md)|
|[MEDIUM]|After calling `getStatusCode()`, the status is checked by hand; `timeout` and `max_duration` are set deliberately.|[console-http-client-and-operations.md](./console-http-client-and-operations.md)|
|[MEDIUM]|Commands return `Command::SUCCESS`, `FAILURE` or `INVALID`, declare name and description in `#[AsCommand]` so they stay lazy, and handle signals through `SignalableCommandInterface`.|[console-http-client-and-operations.md](./console-http-client-and-operations.md)|
|[LOW]|Logging uses PSR-3 placeholders; long-running processes call `reset()` on the logger between jobs.|[console-http-client-and-operations.md](./console-http-client-and-operations.md)|
|[LOW]|Deployment installs with `--no-dev --optimize-autoloader`, clears the cache with `APP_DEBUG=0`, runs migrations, and empties and regenerates OPcache.|[console-http-client-and-operations.md](./console-http-client-and-operations.md)|

## Templates, Translation, Session and Cache

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|`\|raw` is used only on a trusted variable that contains HTML; `{% trans %}` output is not assumed to be escaped.|[templates-translation-cache-and-utilities.md](./templates-translation-cache-and-utilities.md)|
|[MEDIUM]|Pages for anonymous users do not read, write or check the session; Redis or Memcached session handlers account for missing locking.|[templates-translation-cache-and-utilities.md](./templates-translation-cache-and-utilities.md)|
|[MEDIUM]|`cache.system` holds only data derived from source code; tags use a `TagAwareCacheInterface` pool; `cache.app` uses a shared adapter when several servers run.|[templates-translation-cache-and-utilities.md](./templates-translation-cache-and-utilities.md)|
|[MEDIUM]|The locale is set through `_locale` or a listener before `LocaleListener`, not `$request->setLocale()` in a controller.|[templates-translation-cache-and-utilities.md](./templates-translation-cache-and-utilities.md)|
|[LOW]|Embedded controllers are used only when a fragment needs its own sub-request, otherwise Twig Components.|[templates-translation-cache-and-utilities.md](./templates-translation-cache-and-utilities.md)|
|[LOW]|UUIDs are created through `UuidFactory`, passed to queries with `UuidType::NAME`, generated with `doctrine.uuid_generator`, and v7 is preferred over v6.|[templates-translation-cache-and-utilities.md](./templates-translation-cache-and-utilities.md)|

## Testing

|Severity|Check|Owning reference|
|---|---|---|
|[HIGH]|Each test uses the fitting layer: `TestCase` for one class, `KernelTestCase` for services from the container, `WebTestCase` for the full application through HTTP.|[testing.md](./testing.md)|
|[HIGH]|Repositories are tested against a real database connection, isolated per test (for example DAMADoctrineTestBundle rollback), not unit-tested with mocks.|[testing.md](./testing.md)|
|[MEDIUM]|Code that sends HTTP requests is tested with `MockHttpClient`, so no real request is made.|[testing.md](./testing.md)|
|[MEDIUM]|Stateless firewalls are tested by sending the token or header with each request, not `loginUser()`.|[testing.md](./testing.md); [security.md](./security.md)|
|[MEDIUM]|Async transports use `in-memory://` under `when@test`; sent messages are checked before the next request; handlers are unit-tested by calling `__invoke()`.|[testing.md](./testing.md)|
|[MEDIUM]|With async mail, tests use `assertQueuedEmailCount()` and do not follow redirects after sending.|[testing.md](./testing.md)|
|[LOW]|Web tests use hardcoded URLs; console events are tested with `ApplicationTester` after `setAutoExit(false)`; password-hasher costs are lowest under `when@test`.|[testing.md](./testing.md); [security.md](./security.md)|
|[LOW]|The entity manager is closed and set to `null` in `tearDown()`; CI runs with `debug` set to `false`.|[testing.md](./testing.md)|

## Output Rules

- Group findings by severity first: `[BLOCKER]`, `[HIGH]`, `[MEDIUM]`, then `[LOW]`.
- Start the report with the target line, for example `Target: Symfony 6.4, PHP 8.1 (composer.lock)`.
- For every finding give the location as `file:line`, the violated check, the consequence, and the smallest fix that resolves it; name the owning reference.
- Report only what the code and the detected version show; never invent a finding, an API or a version fact. When unsure whether an API exists in the detected version, check the owning reference or say that it is uncertain.
- When nothing is found, say so plainly in one line; do not pad the report with confirmations.
- If a deviation is a deliberate local convention, name it and the rule it qualifies; do not silently waive a `[BLOCKER]` or `[HIGH]` check.

This checklist derives every check from the sibling references in this directory and the Non-negotiable Rules in [SKILL.md](../SKILL.md).
