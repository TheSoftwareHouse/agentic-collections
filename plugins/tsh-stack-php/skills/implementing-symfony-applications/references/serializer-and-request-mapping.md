# Serializer and Request Mapping in Symfony

Use this reference when you map HTTP input onto typed arguments or DTOs, shape output with the Serializer, write a custom normalizer, or choose groups and context options in a Symfony 5.4..8.x project.

## Table of Contents

- [Version Map](#version-map)
- [Request Mapping Attributes](#request-mapping-attributes)
- [Request Data on 5.4](#request-data-on-54)
- [Serializer Basics](#serializer-basics)
- [Groups, Names and Context](#groups-names-and-context)
- [Custom Normalizers](#custom-normalizers)
- [JsonStreamer](#jsonstreamer)
- [Sources](#sources)

## Version Map

| Feature | Since |
| --- | --- |
| Configurable `default_context`, `BackedEnumNormalizer` (PHP 8.1+) | 5.4 |
| Context builders; injecting `ObjectNormalizer` into a custom normalizer deprecated | 6.1 |
| `#[SerializedPath]` | 6.2 |
| `#[MapRequestPayload]`, `#[MapQueryString]`, `#[MapQueryParameter]` | 6.3 |
| `getSupportedTypes()`; `CacheableSupportsMethodInterface` deprecated; `debug:serializer`; `BackedEnumNormalizer::ALLOW_INVALID_VALUES` | 6.3 |
| `validationFailedStatusCode` | 6.4 |
| `CacheableSupportsMethodInterface`, `ArgumentValueResolverInterface` and annotation support removed; `ObjectNormalizer` final | 7.0 |
| `type` option on `#[MapRequestPayload]`, `#[MapUploadedFile]`, `DateTimeNormalizer::CAST_KEY`, `AbstractNormalizer::FILTER_BOOL` | 7.1 |
| Named serializers | 7.2 |
| `key` on `#[MapQueryString]`, `AbstractUid` in `#[MapQueryParameter]`, `NumberNormalizer`, `defaultType` on `#[DiscriminatorMap]`, JsonStreamer | 7.3 |
| `can*()` methods in `ObjectNormalizer`, `DateTimeNormalizer::FORCE_TIMEZONE_KEY` | 7.4 |
| Variadic and file payloads, expressions in `validationGroups`, `mapWhenEmpty`, `#[MapRequestHeader]`, `#[Serialize]`, `COLLECT_EXTRA_ATTRIBUTES_ERRORS`; enum class-name leak fixed | 8.1 |

## Request Mapping Attributes

**What it is.** Controller argument attributes. `#[MapQueryParameter]` maps one query parameter onto a `\BackedEnum`, `array`, `bool`, `float`, `int` or `string` argument, and from 7.3 onto objects extending `AbstractUid`. `#[MapQueryString]` maps the whole query string onto a DTO that uses validation constraints. `#[MapRequestPayload]` maps data that sits directly in the request payload, as with POST or PUT.

**When to use.** On 6.3+, when request data should arrive in the action as a typed argument or a validated DTO.

**Options.**

- `#[MapQueryParameter]`: `filter` takes PHP validate-filter constants.
- `#[MapQueryString]`: `validationGroups`, `validationFailedStatusCode` (6.4), `key` for a nested array under one key (7.3).
- `#[MapRequestPayload]`: `serializationContext`, `resolver`, `acceptFormat`, `validationGroups`, `validationFailedStatusCode` (6.4), `type` for an array of DTOs (7.1).
- 8.1: `validationGroups` accepts expressions; the `args` variable gives access to all controller arguments by name.

**Pitfalls.**

- Default validation failure status is 404 for `#[MapQueryString]` and 422 for `#[MapRequestPayload]`. Change it with `validationFailedStatusCode` on 6.4+.
- For a JSON API, declare the route with `format: 'json'` so validation errors render as a JSON response instead of an HTML page.
- For a valid DTO when the query string is empty, give the argument a default value.
- Before 8.1, enum or other custom types in DTO properties can expose internal class names to the end user on denormalization errors. On those versions use built-in types and validate with constraints.
- Mapping a nested array of specific DTOs needs `phpstan/phpdoc-parser` and `phpdocumentor/type-resolver`, plus a docblock such as `@param UserDto[] $users`.

```php
#[Route('/users', name: 'user_search', format: 'json')]
public function search(
    #[MapQueryParameter(filter: \FILTER_VALIDATE_INT)] int $age,
    #[MapQueryString(validationFailedStatusCode: Response::HTTP_UNPROCESSABLE_ENTITY)] UserDto $userDto = new UserDto(),
): Response {
}

#[Route('/users', name: 'user_create', methods: ['POST'], format: 'json')]
public function create(
    #[MapRequestPayload(validationGroups: ['create'])] UserDto $userDto,
): Response {
}

#[Route('/users/batch', name: 'user_batch', methods: ['POST'], format: 'json')]
public function batch(
    #[MapRequestPayload(type: UserDto::class)] array $users,
): Response {
}
```

```php
final class OrderDto
{
    public function __construct(
        #[Assert\Choice(callback: [OrderStatus::class, 'values'])]
        public readonly string $status,
    ) {
    }
}
```

**`#[MapUploadedFile]` (7.1).** With no file submitted it throws an `HttpException`, unless the argument is nullable (`?UploadedFile $document`). A constraint violation throws an `HttpException` and the action is not executed. Collections map onto an array or a variadic argument, and the constraint applies to every file. Options: `name`, `validationFailedStatusCode`.

**8.1 additions.**

- `#[MapRequestPayload] UserDto ...$users` turns each payload item into a DTO.
- For `multipart/form-data`, request parameters and uploaded files are merged before the payload is deserialized.
- By default the resolver returns `null` without calling the serializer when the query string or body is empty and the argument is nullable or has a default, so custom denormalizers do not run. `mapWhenEmpty: true` changes this; with `#[MapRequestPayload]` the serializer's `denormalize()` receives an empty array.
- `#[MapRequestHeader]` converts the kebab-case header name to the camelCase argument name (`accept-language` to `$acceptLanguage`), or takes `name`. A missing header on an argument with no default that is not nullable returns `400 Bad Request`.
- `#[Serialize]` on an action that returns an object accepts `code` (default `200`), `headers` and `context`. An unsupported format returns `415 Unsupported Media Type`.

```php
#[Route('/products', name: 'product_create', methods: ['POST'], format: 'json')]
#[Serialize(code: 201, headers: ['X-Custom' => 'value'], context: ['groups' => ['read']])]
public function create(
    #[MapRequestHeader(name: 'x-custom-token')] string $token,
    #[MapRequestPayload] ProductRequest $data,
): ProductCreated {
}
```

## Request Data on 5.4

The 5.4 controller page describes no mapping attributes. Request data is read from a type-hinted `Request`: `$request->query->get('page')`, `$request->request->get('page')`, `$request->files->get('foo')`, `$request->headers->get('content-type')`. Output goes through `$this->json()`, which uses the serializer when the serializer service is enabled and `json_encode` otherwise.

```php
public function show(Request $request): JsonResponse
{
    $page = $request->query->get('page');

    return $this->json(['username' => 'jane.doe', 'page' => $page]);
}
```

7.0 removed `ArgumentValueResolverInterface`; use `ValueResolverInterface`.

## Serializer Basics

**What it is.** Serialization converts data to an array first. Normalizers convert objects into arrays and back; encoders convert arrays into a format and back. Default encoders: `JsonEncoder`, `XmlEncoder`, `CsvEncoder`, `YamlEncoder`. `CustomNormalizer`, `GetSetMethodNormalizer` and `PropertyNormalizer` are opt-in through the `serializer.normalizer` tag.

**`ObjectNormalizer`.** Used for any object no other normalizer handles. It accesses properties directly or through getters, setters, hassers, issers, canners (7.4), adders and removers, and denormalizes through the constructor as well as those methods.

**Pitfalls.**

- Register `DateTimeNormalizer` when serializing `DateTime` or `DateTimeImmutable`, to avoid excessive memory usage and exposing internal details. Its default format is RFC 3339; change it with `FORMAT_KEY`. On denormalization a `!` prefix (`'!Y-m-d'`) prevents the time being filled in.
- `#[MaxDepth]` needs `AbstractObjectNormalizer::ENABLE_MAX_DEPTH => true` in the context; `MAX_DEPTH_HANDLER` sets the value at the limit.
- Circular references throw `CircularReferenceException`. `circular_reference_limit` defaults to `1`; `AbstractNormalizer::CIRCULAR_REFERENCE_HANDLER` takes a callable instead.
- `OBJECT_TO_POPULATE` updates only the top-level object; children are re-created. `DEEP_OBJECT_TO_POPULATE => true` updates single child objects in place, not arrays of objects.
- Missing constructor arguments throw `MissingConstructorArgumentsException`; `DEFAULT_CONSTRUCTOR_ARGUMENTS` supplies defaults.
- With a `PropertyTypeExtractor`, a type mismatch throws `UnexpectedValueException`; `DISABLE_TYPE_ENFORCEMENT` turns this off.
- `BackedEnumNormalizer` throws on an invalid backed-enum value; `ALLOW_INVALID_VALUES` (6.3) returns `null` instead.

**Other tools.** `UnwrappingDenormalizer::UNWRAP_PATH` (for example `'[data][person]'`) deserializes part of the input. `#[DiscriminatorMap(typeProperty: 'type', mapping: [...])]` on an interface selects the class; `defaultType` arrived in 7.3. 8.1 adds `DenormalizerInterface::COLLECT_EXTRA_ATTRIBUTES_ERRORS` and deprecates `PartialDenormalizationException::getErrors()` in favour of `getNotNormalizableValueErrors()`.

## Groups, Names and Context

**Groups.** `#[Groups(['admin-view'])]` on properties, selected with the `groups` context key as a string or array. `['groups' => '*']` serializes everything, including properties with no groups. When groups are set, the `attributes` context can only use attributes those groups allow. On 5.4 the examples use `@Groups({"show_product", "list_product"})` annotations, or YAML/XML under `config/serializer/`.

**Ignoring fields.** `#[Ignore]` marks a property or method that should never be serialized. `AbstractNormalizer::IGNORED_ATTRIBUTES` does it at runtime but becomes unmaintainable if used excessively; the docs recommend groups instead.

**Names and paths.** `#[SerializedName('customer_name')]` renames a property on serialization and deserialization. `#[SerializedPath('[profile][username]')]` (6.2) uses PropertyAccess syntax. Do not combine `SerializedPath` and `SerializedName` on the same property.

```php
final class Customer
{
    #[Groups(['public-view'])]
    #[SerializedName('customer_name')]
    public string $name;

    #[Groups(['admin-view'])]
    #[Context([DateTimeNormalizer::FORMAT_KEY => 'Y-m-d'])]
    public \DateTimeImmutable $createdAt;

    #[Ignore]
    public string $internalNote;
}

$json = $serializer->serialize($customer, 'json', ['groups' => 'public-view']);
```

**Context.**

- `framework.serializer.default_context` sets global defaults (configurable since 5.4); per-call context overrides it.
- Extra fields are ignored by default; `allow_extra_attributes: false` rejects them.
- `#[Context]` works per property or per class, with separate `normalizationContext` and `denormalizationContext`, and can be limited to groups. Context without a group is applied first, then contexts of matching groups are merged in the given order.
- Context builders (6.1) such as `DateTimeNormalizerContextBuilder`, `ObjectNormalizerContextBuilder` (`withGroups`) and `CsvEncoderContextBuilder` (`withDelimiter`) add autocompletion, validation and documentation for context options.

```php
$contextBuilder = (new DateTimeNormalizerContextBuilder())
    ->withFormat('Y-m-d H:i:s');

$json = $serializer->serialize($data, 'json', $contextBuilder->toArray());
```

**Named serializers (7.2).** Configured under `framework.serializer.named_serializers`, each with its own `name_converter` and `default_context`. Since 7.3 their normalizers are no longer registered by default.

**7.0 changes.** Doctrine annotations support is removed in favour of native attributes; `framework.serializer.enable_annotations` is replaced by `enable_attributes`.

## Custom Normalizers

**What it is.** A service implementing `NormalizerInterface` (and `DenormalizerInterface` for input) whose `supportsNormalization()` returns `true` for the data it handles.

**Pitfalls.**

- The Serializer calls `supports*()` on every registered normalizer in a loop, and results are not cached by default. `getSupportedTypes(?string $format)` (6.3) caches the decision of whether a type is supported, not the result.
- `getSupportedTypes()` keys: `object` for any class or interface, `*` for any type, a class name for that type, `native-<type>` for scalars. Values: `true` cacheable, `false` not cacheable, `null` not supported.
- `supports*()` must not assume `getSupportedTypes()` was called first.
- Injecting `ObjectNormalizer` is deprecated since 6.1; implement `NormalizerAwareInterface` with `NormalizerAwareTrait` to get the `$normalizer` property.
- `ObjectNormalizer` and `PropertyNormalizer` are final in 7.0 and FrameworkBundle no longer aliases them for autowiring. Decorate with `#[Autowire(service: 'serializer.normalizer.object')]` instead of extending, or type-hint `NormalizerInterface`.
- Registration uses the `serializer.normalizer` tag, applied by autoconfigure; higher priority runs earlier. `debug:serializer` exists from 6.3.

```php
final class TopicNormalizer implements NormalizerInterface
{
    public function __construct(
        #[Autowire(service: 'serializer.normalizer.object')]
        private readonly NormalizerInterface $normalizer,
    ) {
    }

    public function normalize(mixed $data, ?string $format = null, array $context = []): array
    {
        $normalized = $this->normalizer->normalize($data, $format, $context);
        $normalized['url'] = '/topics/' . $data->getId();

        return $normalized;
    }

    public function supportsNormalization(mixed $data, ?string $format = null, array $context = []): bool
    {
        return $data instanceof Topic;
    }

    public function getSupportedTypes(?string $format): array
    {
        return [Topic::class => true];
    }
}
```

**Versions.**

- Before 6.3, cacheability came from `CacheableSupportsMethodInterface` with `hasCacheableSupportsMethod()` returning `true`.
- 7.0 makes `getSupportedTypes()` part of `NormalizerInterface` and `DenormalizerInterface`, removes `CacheableSupportsMethodInterface`, `ContextAwareNormalizerInterface` and `ContextAwareDenormalizerInterface`, and adds `array $context = []` to `supportsNormalization()` and `supportsDenormalization()`.
- 7.0 removes `AbstractUid` denormalization from `UidNormalizer`; denormalizing into an abstract class throws `\Error`.

## JsonStreamer

**What it is.** A component (7.3, `composer require symfony/json-streamer`) that encodes PHP data to JSON streams and decodes JSON streams into PHP data incrementally, without loading everything into memory. It targets APIs, both own and third-party.

**When to use.** Large JSON payloads on 7.3+ where memory matters.

**When not to use.** Classes with a constructor or with non-public properties; it works only with DTOs made of public properties and no constructor.

**Pitfalls.**

- Decoding from a stream is memory-efficient and uses ghost objects, but is slightly slower because of lazy loading. Decoding from a string is faster but loads everything into memory and is unsuitable for large files.
- `#[ValueTransformer]` callables must be a public static method or a non-anonymous function, and should be lightweight; avoid external API or database calls.
- `#[JsonStreamable]` is optional but recommended, since it pre-generates encoding and decoding files during cache warm-up.
- Dynamic metadata loaders (decorating `json_streamer.write.property_metadata_loader`) add complexity; attribute configuration is sufficient for most cases.
- 7.4 deprecates the `nativeToStreamValueTransformers`/`streamToNativeValueTransformers` constructor parameters in favour of `valueTransformers`.

```php
#[JsonStreamable]
final class Cat
{
    #[StreamedName('@id')]
    public int $id;

    #[ValueTransformer(nativeToStream: 'strtoupper')]
    public string $name;
}

$json = $jsonStreamWriter->write($cats, Type::list(Type::object(Cat::class)));

return new StreamedResponse($json);
```

## Sources

- https://symfony.com/doc/6.4/controller.html
- https://symfony.com/doc/7.4/controller.html
- https://symfony.com/doc/8.1/controller.html
- https://symfony.com/doc/5.4/controller.html
- https://symfony.com/doc/7.4/serializer.html
- https://symfony.com/doc/8.1/serializer.html
- https://symfony.com/doc/6.4/serializer.html
- https://symfony.com/doc/5.4/serializer.html
- https://symfony.com/doc/6.4/serializer/custom_normalizer.html
- https://symfony.com/doc/7.4/serializer/streaming_json.html
- https://github.com/symfony/symfony/blob/6.3/UPGRADE-6.3.md
- https://github.com/symfony/symfony/blob/7.0/UPGRADE-7.0.md
