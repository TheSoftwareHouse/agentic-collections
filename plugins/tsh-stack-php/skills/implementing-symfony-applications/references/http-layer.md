# HTTP Layer

Use this reference when adding or reviewing routes, controllers, request-to-DTO mapping, argument value resolvers, or error handling in a Symfony 5.4..8.x application.

- [Routing](#routing)
- [Controllers](#controllers)
- [Request Mapping Attributes](#request-mapping-attributes)
- [Doctrine Entities as Arguments](#doctrine-entities-as-arguments-mapentity)
- [Argument Value Resolvers](#argument-value-resolvers)
- [Error Pages and Exception Handling](#error-pages-and-exception-handling)

## Routing

`#[Route]` attributes on controller classes and methods. Symfony recommends attributes over annotations; attributes are native from PHP 8.

- **Use**:
  - `name` on routes; each route name must be unique in the application. Without it, Symfony generates a name from the controller and action.
  - `requirements` for placeholders that must match a regular expression, inline (`{page<[0-9]+>}`) or with `Requirement` constants (digits, dates, UUIDs).
  - `methods` to restrict HTTP verbs; by default a route matches any verb.
  - A class-level `#[Route]` for a shared path, name prefix and requirements.
  - `stateless: true` when the session must not be used while matching the request.
  - `env` to register a route only in one environment (`env: 'dev'`).
- **Pitfalls**:
  - The query string is not considered when matching routes.
  - With several classes in one file, only the routes of the first class load.
  - The route attribute always takes precedence over routes in YAML, XML or PHP files.
  - A default value is allowed not to match the requirement.
  - `condition` is not taken into account when generating URLs.
  - `stateless: true`: if the session is used anyway, debug mode throws `UnexpectedSessionUsageException`; otherwise a warning is logged.
  - Unknown parameters passed to `generateUrl()` become the query string; objects passed as extra parameters are not converted to string.
  - `redirect()` does not check its destination in any way.
  - HTML forms only support `GET` and `POST`.
  - `trailing_slash_on_root` is not available with PHP attributes.
- **Ordering**: higher `priority` routes are sorted first; the default is `0`.

```php
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Component\Routing\Requirement\Requirement;

#[Route('/blog', name: 'blog_')]
final class BlogController extends AbstractController
{
    #[Route('/{page}', name: 'list', requirements: ['page' => Requirement::DIGITS], methods: ['GET', 'HEAD'])]
    public function list(int $page = 1): Response
    {
        return $this->render('blog/list.html.twig', ['page' => $page]);
    }
}
```

5.4 form: attributes on PHP 8 (since 5.2), or docblock annotations through `doctrine/annotations` on PHP 7. The `type: annotation` route import also loads attributes:

```yaml
controllers:
    resource: ../../src/Controller/
    type: annotation
```

| 5.4 | 6.4 | 7.x | 8.x |
| --- | --- | --- | --- |
| attributes (5.2); `priority`, `stateless` (5.1); route aliases (5.4) | Doctrine annotations deprecated in favour of attributes | annotations removed (7.0); `{param:argument}` entity mapping (7.1); `debug:router --method` (7.3); `_query` parameter, `env` arrays, XML configuration deprecated (7.4) | `Annotation` namespace aliases removed; XML configuration removed; non-array `_query` throws `InvalidParameterException` |

Tooling: `debug:router` lists routes in evaluation order (`--show-aliases`, `--show-controllers`); `router:match /path` shows which route matches a URL.

## Controllers

A callable that reads the `Request` and must return a `Response`. Usually a method in a class extending `AbstractController`, which provides `render()`, `json()`, `redirectToRoute()`, `redirect()`, `createNotFoundException()`, `getParameter()` and `denyAccessUnlessGranted()`.

- **Use**:
  - Type-hinted action arguments for services (the controller must be a service), or regular constructor injection.
  - `#[Autowire(service: '...')]` on an argument to pick a specific service (6.1+).
  - A `Request` type-hint to receive the current request.
  - `json()` for JSON: it uses the Serializer when enabled, otherwise `json_encode`.
- **Do not**: call `get()`, `has()`, `getDoctrine()` or `dispatchMessage()` on `AbstractController` (removed in 6.0); use method or constructor injection instead.
- **Pitfalls**:
  - A non-`Response` return value must be converted by a `kernel.view` listener.
  - `Request::get()` is deprecated in 7.4 and removed in 8.0; read `$request->attributes`, `$request->query` or `$request->request` directly.
  - `createNotFoundException()` returns a `NotFoundHttpException`; throw it to produce a 404.

```php
#[Route('/lucky/number/{max}', name: 'lucky_number')]
public function number(int $max, #[Autowire(service: 'monolog.logger.request')] LoggerInterface $logger): Response
{
    $number = random_int(0, $max);

    return $this->render('lucky/number.html.twig', ['number' => $number]);
}
```

| 5.4 | 6.4 | 7.x | 8.x |
| --- | --- | --- | --- |
| `get()`, `has()`, `getDoctrine()`, `dispatchMessage()` available | those removed (6.0); `#[Autowire]` (6.1); `renderForm()` deprecated (6.2) | `renderForm()` removed, pass the form to `render()` (7.0); `Request::get()` deprecated (7.4) | `Request::get()` removed; `#[Serialize]` for return values (8.1) |

`#[Serialize]` (8.1) lets an action return an object or array that Symfony serializes by request format (JSON by default), with `code`, `headers` and `context` options; an unsupported format returns 415. It requires the Serializer component.

## Request Mapping Attributes

Controller argument attributes that map request data into typed values or DTOs and validate them.

| Attribute | Source | Validation failure default | Since |
| --- | --- | --- | --- |
| `#[MapRequestPayload]` | request body | 422 | 6.3 |
| `#[MapQueryString]` | whole query string | 404 | 6.3 |
| `#[MapQueryParameter]` | one query parameter | not stated | 6.3 |
| `#[MapUploadedFile]` | uploaded file(s) with constraints | not stated (`HttpException`) | 7.1 |
| `#[MapRequestHeader]` | one header | 400 when missing and required | 8.1 |

- **Options**:
  - `validationGroups` and `validationFailedStatusCode` on `#[MapRequestPayload]` and `#[MapQueryString]` (6.4); `validationFailedStatusCode` on `#[MapQueryParameter]` (7.1).
  - `#[MapRequestPayload]`: `serializationContext`, `resolver`, `acceptFormat`, `type` (7.1).
  - `#[MapQueryString]`: `key` for a nested array key (7.3).
  - `#[MapQueryParameter]`: types `\BackedEnum` (6.4), `array`, `bool`, `float`, `int`, `string`, `AbstractUid` (7.3); `filter` with PHP filter constants.
  - `#[MapUploadedFile]`: constraints as arguments, `name`, `validationFailedStatusCode`; nullable makes it optional, otherwise a missing file throws `HttpException`.
- **Pitfalls**:
  - Declare the route with `format: 'json'` so errors render as JSON rather than an HTML page.
  - Unsupported or missing format returns 415 (`UnsupportedMediaTypeHttpException`); a malformed body or unexpected property returns 400 (`BadRequestHttpException`).
  - A nullable or defaulted argument with an empty query string or body resolves to `null` without invoking the Serializer; 8.1 adds `mapWhenEmpty: true` to pass an empty array to `denormalize()`.
  - Mapping a nested array of DTOs needs `phpstan/phpdoc-parser` and `phpdocumentor/type-resolver`.
  - Before 8.1, denormalization errors for custom types such as enums can expose internal class names; use built-in types and validate them with constraints, for example `Assert\Choice`.
  - The resolver collects denormalization errors (`collect_denormalization_errors`); query strings and forms add `filter_bool`.

```php
final class OrderInput
{
    public function __construct(
        #[Assert\Choice(callback: [OrderStatus::class, 'values'])]
        public string $status,
    ) {
    }
}

#[Route('/api/orders', name: 'api_order_', format: 'json')]
final class OrderController extends AbstractController
{
    #[Route('', name: 'create', methods: ['POST'])]
    public function create(#[MapRequestPayload] OrderInput $input): JsonResponse
    {
        return $this->json(['status' => $input->status]);
    }

    #[Route('', name: 'list', methods: ['GET'])]
    public function list(
        #[MapQueryString] OrderFilter $filter = new OrderFilter(),
        #[MapQueryParameter(filter: \FILTER_VALIDATE_INT)] int $page = 1,
    ): JsonResponse {
        return $this->json([]);
    }
}
```

Lists: `#[MapRequestPayload(type: UserDto::class)] array $users` (7.1) or variadic `UserDto ...$users` (8.1).

| 5.4 | 6.4 | 7.x | 8.x |
| --- | --- | --- | --- |
| none | Map* (6.3); `validationFailedStatusCode`, BackedEnum in `MapQueryParameter` (6.4) | `type:` lists, `#[MapUploadedFile]` (7.1); `key:`, Uid in `MapQueryParameter` (7.3) | `#[MapRequestHeader]`, variadic payloads, file mapping in `MapRequestPayload`, `mapWhenEmpty`, `#[Serialize]` (8.1) |

## Doctrine Entities as Arguments (`#[MapEntity]`)

`EntityValueResolver` (6.2) loads an entity for a controller argument. By default it fetches by `{id}` via `find()` and throws a 404 when nothing is found.

- **Use**:
  - `{param:argument}` route syntax (7.1): `{slug:product}` runs `findOneBy(['slug' => $slug])`.
  - `#[MapEntity(mapping: [...])]` with route placeholder as key and entity property as value.
  - `#[MapEntity(id: 'product_id')]` to find by primary key from another placeholder.
  - `#[MapEntity(expr: 'repository.find(product_id)')]` with ExpressionLanguage; variables `repository`, route wildcards and `request` (6.4).
  - `?Product $product` to handle a missing entity yourself; `#[MapEntity(disabled: true)]` to switch it off for one argument.
- **Pitfalls**:
  - `auto_mapping` tries `findOneBy()` with all route wildcards that match entity properties; it is less explicit and no longer recommended.
  - The `message` option (7.1) is shown only in the development environment.
  - Interface targets need `resolve_target_entities` (7.3).

```php
#[Route('/product/{slug:product}', name: 'product_show')]
public function show(Product $product): Response
{
    return $this->render('product/show.html.twig', ['product' => $product]);
}
```

Entity lists (7.1): `#[MapEntity(class: Post::class, expr: 'repository.findBy({"author": author_id}, {}, 10)')] iterable $posts`.

5.4 form: SensioFrameworkExtraBundle queries the entity by `{id}` and returns a 404 when it is not found.

| 5.4 | 6.4 | 7.x | 8.x |
| --- | --- | --- | --- |
| SensioFrameworkExtraBundle | `EntityValueResolver` (6.2); `request` in `expr` (6.4) | `{param:argument}`, entity lists, `message` (7.1); interface targets (7.3) | automatic entity mapping removed; use `#[MapEntity]` or `{param:argument}` |

## Argument Value Resolvers

Services implementing `ValueResolverInterface` that produce controller argument values. Built-ins cover request attributes, `Request`, session, services, defaults, variadics, `BackedEnum` and Uid (6.1, 404 on an invalid value), `DateTimeInterface` with `#[MapDateTime]` (6.1), `#[CurrentUser]`, security token (6.3, 401 when required and missing), entities and PSR-7 objects.

- **Use**: `#[AsTargetedValueResolver('name')]` with `#[ValueResolver('name')]` on the argument (6.3) to run a resolver only where it is targeted; built-in resolvers are targeted by their FQCN and can be disabled with `disabled: true`.
- **Pitfalls**:
  - `resolve()` must always return an array: empty when it cannot resolve the argument, otherwise the resolved value(s).
  - Every resolver tagged `controller.argument_value_resolver` is called until one provides a value; the tag is added to every `ValueResolverInterface` service automatically.
  - `RequestAttributeValueResolver` has priority `100`; use `100` or more if your resolver reads request attributes, lower otherwise.
  - `#[CurrentUser]` is needed for a custom User class and works only in controller arguments.

```php
#[AsTargetedValueResolver('booking_id')]
final class BookingIdValueResolver implements ValueResolverInterface
{
    public function resolve(Request $request, ArgumentMetadata $argument): iterable
    {
        $value = $request->attributes->get($argument->getName());

        return is_string($value) ? [new BookingId($value)] : [];
    }
}
```

Usage: `public function index(#[ValueResolver('booking_id')] BookingId $id): Response`.

5.4 form: implement `ArgumentValueResolverInterface`.

| 5.4 | 6.4 | 7.x | 8.x |
| --- | --- | --- | --- |
| `ArgumentValueResolverInterface` | Uid, BackedEnum, DateTime resolvers (6.1); `ValueResolverInterface`, old interface deprecated (6.2); targeted resolvers (6.3) | old interface removed (7.0); `NearMissValueResolverException` (7.1); `#[CurrentUser]` union types (7.4) | same |

## Error Pages and Exception Handling

Options, from templates to full control:

1. Twig templates in `templates/bundles/TwigBundle/Exception/`: `error{status_code}.html.twig` first, then `error.html.twig` (requires `symfony/twig-pack`). Variables: `status_code`, `status_text`, `exception`.
2. Exceptions implementing `HttpExceptionInterface::getStatusCode()` to set the status; otherwise it is 500. `#[WithHttpStatus]` and `#[WithLogLevel]` on exception classes (6.3).
3. A normalizer whose `supportsNormalization()` returns `$data instanceof FlattenException` to change non-HTML output; the built-in one is `ProblemNormalizer` (requires `symfony/serializer-pack`).
4. `framework.error_controller` pointing to a custom controller, which receives `exception` and `logger` (may be `null`).
5. A `kernel.exception` listener; calling `setResponse()` on `ExceptionEvent` stops propagation and sends that response.

- **Do not**: output `{{ exception.traceAsString }}` for end users.
- **Pitfalls**:
  - Security information is not available on 404 pages; the user appears logged out there.
  - Preview error pages in dev only, at `/_error/{statusCode}` or `/_error/{statusCode}.{format}`.
- **Static pages**: `APP_ENV=prod php bin/console error:dump var/cache/prod/error_pages/` (7.3) generates pages for the web server, by default for all 4xx and 5xx codes.

| 5.4 | 6.4 | 7.x | 8.x |
| --- | --- | --- | --- |
| Twig templates, `ErrorController` (4.4) | `HttpKernel` `$handleAllThrowable` argument (6.2); `#[WithHttpStatus]`, `#[WithLogLevel]` (6.3) | `error:dump`, `errors.php` replaces `errors.xml` (7.3) | `errors.xml` routing removed; `ErrorListener::logException()` gets `$logChannel` |

## Sources

- https://symfony.com/doc/7.4/routing.html
- https://symfony.com/doc/5.4/routing.html
- https://github.com/symfony/symfony/blob/8.0/UPGRADE-8.0.md
- https://github.com/symfony/symfony/blob/7.4/UPGRADE-7.4.md
- https://github.com/symfony/symfony/blob/7.0/UPGRADE-7.0.md
- https://github.com/symfony/symfony/blob/6.4/UPGRADE-6.4.md
- https://github.com/symfony/symfony/blob/6.4/UPGRADE-6.2.md
- https://github.com/symfony/symfony/blob/6.0/UPGRADE-6.0.md
- https://symfony.com/blog/new-in-symfony-7-4-deprecated-xml-configuration
- https://symfony.com/doc/6.4/controller.html
- https://symfony.com/doc/7.4/controller.html
- https://symfony.com/doc/8.1/controller.html
- https://raw.githubusercontent.com/symfony/symfony/7.4/src/Symfony/Component/HttpKernel/Controller/ArgumentResolver/RequestPayloadValueResolver.php
- https://symfony.com/doc/6.4/controller/value_resolver.html
- https://symfony.com/doc/current/controller/value_resolver.html
- https://symfony.com/doc/7.4/doctrine.html
- https://symfony.com/doc/6.4/doctrine.html
- https://symfony.com/doc/5.4/doctrine.html
- https://symfony.com/doc/5.4/security.html
- https://symfony.com/doc/6.4/security.html
- https://github.com/symfony/symfony/blob/7.4/src/Symfony/Component/Security/Http/CHANGELOG.md
- https://symfony.com/doc/7.4/controller/error_pages.html
- https://raw.githubusercontent.com/symfony/symfony/7.4/src/Symfony/Component/HttpKernel/CHANGELOG.md
