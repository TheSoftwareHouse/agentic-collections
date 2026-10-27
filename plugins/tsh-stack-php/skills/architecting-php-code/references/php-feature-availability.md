# PHP Feature Availability

Use this reference when you know the project's target PHP version and must decide whether a language feature or function may be used, and what the PHP manual names as the replacement for a deprecated construct.

Detect the target first with [`php-version-detection.md`](./php-version-detection.md). PHP 8.6 is not yet released as of writing — never target it. Its release schedule is in [`php-version-detection.md`](./php-version-detection.md#php-86-release-schedule).

## Quick Lookup

| Feature | First version | Notes |
| --- | --- | --- |
| Typed properties, arrow functions `fn`, `??=`, `1_000`, `[...$list]` | 7.4 | `fn` becomes a reserved keyword |
| `__serialize()` / `__unserialize()` | 7.4 | Supersede the `Serializable` interface |
| Union types `int\|string`, `mixed`, `static` return | 8.0 | `?T` is shorthand for `T\|null` and is not deprecated |
| Named arguments | 8.0 | Parameter names are not part of the signature contract |
| `match` | 8.0 | Strict comparison; unhandled value throws `UnhandledMatchError` |
| Nullsafe `?->` | 8.0 | Not allowed in write context or with references |
| `$object::class` | 8.0 | Same result as `get_class($object)` |
| Constructor property promotion | 8.0 | Only in non-abstract constructors |
| Attributes `#[...]` | 8.0 | Userland attributes are validated only when `newInstance()` is called |
| `throw` as an expression, `catch (E)` without variable | 8.0 | |
| `str_contains`, `str_starts_with`, `str_ends_with`, `get_debug_type` | 8.0 | Provided by `symfony/polyfill-php80` |
| Enums | 8.1 | `enum_exists` provided by `symfony/polyfill-php81` |
| `readonly` properties | 8.1 | Typed properties only, no default value |
| First-class callable `f(...)` | 8.1 | Identical to `Closure::fromCallable('f')` |
| `never` return type | 8.1 | |
| `new` in initializers | 8.1 | Not in property or class constant initializers |
| Intersection types `A&B` | 8.1 | Cannot be combined with union types on 8.1 |
| `final` class constants; string-keyed `[...$a]`; named argument after unpack | 8.1 | |
| `array_is_list()` | 8.1 | Provided by `symfony/polyfill-php81` |
| `readonly` classes | 8.2 | Parent must also be readonly |
| DNF types `(A&B)\|null`; standalone `null`, `false`; `true` | 8.2 | |
| Constants in traits | 8.2 | |
| `Random\Randomizer` | 8.2 | Default engine is `Secure` |
| `#[\SensitiveParameter]` | 8.2 | Redacts the value in backtraces |
| Typed class constants | 8.3 | All types except `void`, `callable`, `never` |
| `#[\Override]` | 8.3 | Attribute class provided by `symfony/polyfill-php83` |
| Dynamic constant fetch `C::{$name}` | 8.3 | |
| `json_validate()`, `mb_str_pad()`, `str_increment()`, `str_decrement()` | 8.3 | Provided by `symfony/polyfill-php83` |
| Readonly reinitialised during cloning; readonly anonymous classes | 8.3 | |
| Property hooks | 8.4 | Not combinable with `readonly` |
| Asymmetric visibility `public private(set)` | 8.4 | Typed properties only |
| `new Foo()->bar()` | 8.4 | Constructor parentheses still required |
| `#[\Deprecated]` | 8.4 | Class provided by `symfony/polyfill-php84` |
| `array_find`, `array_find_key`, `array_any`, `array_all`, `mb_trim`, `fpow` | 8.4 | Provided by `symfony/polyfill-php84` |
| Lazy objects | 8.4 | `ReflectionClass::newLazyGhost()` |
| Pipe operator `\|>` | 8.5 | Arrow functions in the chain need parentheses |
| `clone($object, [...])` | 8.5 | Runs `__clone()` before assigning the new values |
| `#[\NoDiscard]` and `(void)` cast | 8.5 | `NoDiscard` provided by `symfony/polyfill-php85` |
| `array_first()`, `array_last()` | 8.5 | Provided by `symfony/polyfill-php85` |
| Closures and first-class callables in constant expressions | 8.5 | |
| `final` promoted properties; asymmetric visibility on static properties; `#[\Override]` on properties | 8.5 | |
| `Uri\Rfc3986\Uri`, `Uri\WhatWg\Url` | 8.5 | Always-available URI extension |

## Polyfills

- Symfony polyfills backport features of newer PHP versions; "new ones are backported, but removed or legacy behavior is not". "A polyfill runs only when the native symbol is missing."
- Attributes are polyfilled "even when their runtime effect needs engine support, because reflection still conveys their meaning".
- A constant that only switches on behaviour that cannot be polyfilled is left undefined, so its absence can be used for feature detection.
- Do not require `symfony/polyfill` directly; require the standalone packages. List unneeded polyfills in the `replace` section of `composer.json`. `symfony/polyfill-php83` requires `php: >=7.2`.
- The `array_is_list()` RFC warns that `array_values($array) === $array` is false for some arrays containing `NAN`, and `array_keys($array) === range(0, count($array) - 1)` is wrong for the empty array.

## PHP 7.4

```php
$nums = array_map(fn($n) => $n * $factor, [1, 2, 3, 4]);
$array['key'] ??= computeDefault();
$fruits = ['banana', 'orange', ...$parts, 'watermelon'];
```

- A typed property without a default is uninitialised, not `null`; reading it throws `TypeError` unless `__get()` is defined. `unset()` returns it to the uninitialised state. A `null` default needs an explicitly nullable type. Property types are invariant in inheritance.
- Arrow functions capture used variables by value; `$fn = fn() => $x++;` leaves `$x` unchanged. `$this` is bound automatically in class methods; the `static` prefix prevents it.
- Using `null`, `bool`, `int`, `float` or a resource as an array (`$null["key"]`) emits a notice.

Deprecated on 7.4: nested ternaries without parentheses (`(1 ? 2 : 3) ? 4 : 5` is fine), `$var{$idx}` (use `$var[$idx]`), `(real)` and `is_real()` (use `(float)` and `is_float()`), `implode($parts, $glue)` (use `implode($glue, $parts)`), `array_key_exists()` on objects, `parent` without a parent class.

## PHP 8.0

```php
final class Point
{
    public function __construct(
        public float $x = 0.0,
        public float $y = 0.0,
    ) {
    }
}

$result = match ($value) {
    1, 2 => 'low',
    3 => 'high',
};
$country = $session?->user?->getAddress()?->country;
$user = $session->user ?? throw new Exception('Must have user');
htmlspecialchars($string, double_encode: false);
```

- `match` compares strictly regardless of `strict_types`, has an implicit break per arm, and throws `UnhandledMatchError` when no arm matches. `switch` compares loosely, falls through without `break` and ignores unhandled values.
- Nullsafe short-circuits the whole chain: in `$a?->b($c->d())`, `$c->d()` is not evaluated when `$a` is null. `$foo?->bar->baz = 'baz'` and `$x = &$foo?->bar` are errors.
- Named arguments must come after positional ones. Renaming a parameter in a child class can break named-argument calls. Good fits: skipping several optional parameters, boolean flags, constructors with many defaults.
- Promoted parameters need a visibility keyword (`var` is not supported); `callable` type and variadic parameters cannot be promoted; a `null` default needs `?Type`.
- `void` can never be part of a union; `false` is allowed only inside a union; `int|INT` and `bool|false` are compile-time errors.

Breaking on 8.0: `0 == "foo"`, `0 == ""` and `42 == "42foo"` are now `false`. Arithmetic on arrays, resources or non-overloaded objects throws `TypeError`. `@` no longer silences fatal errors. Methods named after their class are no longer constructors; use `__construct()`. `curl_init()` returns a `CurlHandle`; replace `is_resource()` checks with checks for `false`. PDO throws exceptions by default. `each()` is removed (use `foreach` or `ArrayIterator`), as are `create_function()` and `$array{0}`. `array_key_exists()` on objects is removed (use `isset()` or `property_exists()`). `match` and `mixed` are reserved.

## PHP 8.1

```php
enum Suit: string
{
    case Hearts = 'H';
    case Diamonds = 'D';
    case Spades = 'S';

}

$suit = Suit::tryFrom('A') ?? Suit::Spades;

$fn = $this->method(...);
$arr2 = [...$arr1, 'c' => 'd'];
```

- Enums fit a parameter restricted to a fixed set of values, states with labels separate from stored values, and round-trips to a database through a backed enum. Cases are singletons, so `===` works.
- Enums have no constructors, properties or parent classes, cannot be instantiated with `new` or cloned, and cannot be array keys (use `SplObjectStorage` or `WeakMap`). Pure enums cannot be JSON-serialised.
- A `readonly` property is initialised once, only from its declaring scope. Objects held in it can still be modified internally. Readonly static properties are not supported.
- First-class callables check visibility on creation; `new Foo(...)` and `$obj?->method(...)` are not supported.
- `new` in initializers excludes dynamic class names, anonymous classes and argument unpacking. Nested attributes become possible: `#[Assert\All(new Assert\NotNull(), new Assert\Length(max: 6))]`.

Deprecated or changed on 8.1: passing `null` to a non-nullable parameter of an internal function (`str_contains("foobar", null)`). Overriding most non-final internal methods without a compatible return type emits a deprecation; `#[\ReturnTypeWillChange]` silences it. `Serializable` without `__serialize()` / `__unserialize()`: implement only the new methods, or both if PHP below 7.4 is supported. `$a[15.5]`, `$arr = false; $arr[] = 2;`, `FILTER_SANITIZE_STRING`, `strftime()` (use `date()` or `IntlDateFormatter::format()`), `strptime()`, `mhash()` (use `hash_*()`). An optional parameter before a required one throws `ArgumentCountError`. MySQLi throws by default (restore with `mysqli_report(MYSQLI_REPORT_OFF)`); `htmlspecialchars()` defaults to `ENT_QUOTES | ENT_SUBSTITUTE`. `readonly` and `never` are reserved.

## PHP 8.2

```php
readonly class Foo
{
    public int $bar;
}

function login(string $user, #[\SensitiveParameter] string $password): void
{
}

$randomizer = new Random\Randomizer(new Random\Engine\Secure());
```

- A readonly class makes every instance property readonly and forbids dynamic properties; properties must be typed and non-static, and `#[AllowDynamicProperties]` on it is a compile error.
- DNF requires parentheses around each intersection: `(A&B)|D` is valid, `A&(B|D)` is not.
- `Randomizer` methods replace `mt_rand()` / `random_int()`, `random_bytes()`, `shuffle()` and `str_shuffle()`. The `Secure` engine cannot be seeded.
- A `#[\SensitiveParameter]` value appears in traces as `Object(SensitiveParameterValue)`.

Deprecated on 8.2: dynamic properties, unless the class has `#[\AllowDynamicProperties]`; `stdClass` and `__get()` / `__set()` are unaffected; dynamic properties become an `Error` in PHP 9.0. `"${var}"` (use `"$var"` or `"{$var}"`). Callables such as `"self::method"`, `["parent", "method"]` or `["static", "method"]`; `"A::method"` and `["A", "method"]` are unaffected. `utf8_encode()` / `utf8_decode()` and the MBString `QPrint`, `Base64`, `Uuencode` and `HTML-ENTITIES` encodings.

## PHP 8.3

```php
final class Extended extends Base
{
    #[\Override]
    protected function boo(): void
    {
    }
}

$value = Config::{$name};
var_dump(json_validate('{ "test": { "foo": "bar" } }'));
```

- Typed class constants are covariant; a child cannot widen the declared type. `strict_types` has no effect, and `float` constants accept integers.
- `#[\Override]` raises a compile-time error when no parent or interface method of that name exists. It cannot be used on `__construct()`.
- Calling `json_validate()` right before `json_decode()` parses the string twice; it uses less memory than `json_decode()` only when the decoded payload is not needed.
- `str_increment()` throws `ValueError` for empty or non-alphanumeric ASCII strings; `str_increment('ZZ')` gives `AAA`.

Deprecated on 8.3: `++` on empty, non-numeric or non-alphanumeric strings (use `str_increment()`) and `--` on empty or non-numeric strings. `get_class()` and `get_parent_class()` without arguments. `assert_options()`, `MT_RAND_PHP`, and `ReflectionProperty::setValue()` with one argument (pass `null` first for static properties).

## PHP 8.4

```php
final class Person
{
    public string $fullName {
        get => $this->firstName . ' ' . $this->lastName;
    }

    public string $firstName {
        set => ucfirst(strtolower($value));
    }

    public protected(set) string $name;
}

$value = new MyClass()->method();
```

- A primary use of hooks is to not use them yet, but keep the ability to add them later without breaking the public API. They suit validation or normalisation on write and computed read-only values.
- Prefer dedicated mutator methods for arrays modified in place, references, or indirect modification on a property with a `set` hook. Hooks are not allowed on static properties or with `readonly`; a hooked property cannot be `unset()`.
- A hooked property that never uses `$this->prop` is virtual and has no stored value. Default values bypass the `set` hook. Interfaces must state required hooks explicitly.
- Set visibility must be equal to or narrower than get visibility. A `private(set)` property is implicitly `final`. `readonly` now implies `protected(set)`.
- `new MyClass::CONSTANT` remains a syntax error; the constructor parentheses are required.
- `#[\Deprecated]` marks functions, methods and class constants and emits `E_USER_DEPRECATED`.

Deprecated on 8.4: implicitly nullable parameters; write `?T1 $a = null` or `T1|null $a = null`, never `T1 $a = null`. `trigger_error()` with `E_USER_ERROR` (throw an exception or call `exit()`). `0 ** -1` (use `fpow()`), `lcg_value()` (use `Random\Randomizer::getFloat()`), `E_STRICT`, a class named `_`, one-argument `ReflectionMethod::__construct()` (use `createFromMethodName()`), `mysqli_ping()`.

## PHP 8.5

```php
$slug = $title
    |> trim(...)
    |> (fn($str) => str_replace(' ', '-', $str))
    |> (fn($str) => str_replace('.', '', $str))
    |> strtolower(...);

readonly class Color
{
    public function __construct(
        public int $red,
        public int $alpha = 255,
    ) {
    }

    public function withAlpha(int $alpha): static
    {
        return clone($this, ['alpha' => $alpha]);
    }
}

$lastEvent = array_last($events);
$uri = Uri\Rfc3986\Uri::parse('https://php.net/releases/8.5/en.php');
```

- The pipe passes the left value to a single-parameter callable on the right. By-reference callables are not allowed there. Ternaries and `??` on the right need parentheses.
- Clone-with lifts the `readonly` restriction and runs property hooks as setters. Public readonly properties default to `protected(set)`, so changing them from outside needs `public(set)`.
- `#[\NoDiscard]` warns when a return value is unused; `(void)` marks an intentional discard and has no effect on execution by itself.
- `array_first()` and `array_last()` return `null` for an empty array, which composes with `??`.
- `Uri\...::parse()` returns `null` on failure and suits untrusted input; the constructor throws. `parse_url()` is not compliant with any standard.

Breaking on 8.5: `[$a] = 42;` warns. Casting unrepresentable floats to `int`, or `NAN` to other types, warns. `#[\Attribute]` on an abstract class, enum, interface or trait is a compile-time error unless `#[\DelayedTargetValidation]` is used. `disable_classes` is removed.

Deprecated on 8.5: `(boolean)`, `(integer)`, `(double)`, `(binary)` (use `(bool)`, `(int)`, `(float)`, `(string)`). `case X;` with a semicolon. The backtick operator as an alias for `shell_exec()`. `null` as an array offset or in `array_key_exists()` (use an empty string). `__sleep()` / `__wakeup()` are soft-deprecated in favour of `__serialize()` / `__unserialize()`. `$http_response_header` (use `http_get_last_response_headers()`), `socket_set_timeout()` (use `stream_set_timeout()`), the PDO `uri:` DSN scheme.

## Sources

- https://www.php.net/manual/en/migration74.new-features.php
- https://www.php.net/manual/en/migration74.incompatible.php
- https://www.php.net/manual/en/migration74.deprecated.php
- https://www.php.net/manual/en/migration80.new-features.php
- https://www.php.net/manual/en/migration80.incompatible.php
- https://www.php.net/manual/en/migration81.new-features.php
- https://www.php.net/manual/en/migration81.incompatible.php
- https://www.php.net/manual/en/migration81.deprecated.php
- https://www.php.net/manual/en/migration82.new-features.php
- https://www.php.net/manual/en/migration82.deprecated.php
- https://www.php.net/manual/en/migration83.new-features.php
- https://www.php.net/manual/en/migration83.deprecated.php
- https://www.php.net/manual/en/migration84.new-features.php
- https://www.php.net/manual/en/migration84.new-functions.php
- https://www.php.net/manual/en/migration84.deprecated.php
- https://www.php.net/manual/en/migration85.new-features.php
- https://www.php.net/manual/en/migration85.incompatible.php
- https://www.php.net/manual/en/migration85.deprecated.php
- https://www.php.net/releases/8.5/en.php
- https://www.php.net/manual/en/function.json-validate.php
- https://www.php.net/manual/en/function.str-increment.php
- https://www.php.net/manual/en/class.override.php
- https://wiki.php.net/rfc/match_expression_v2
- https://wiki.php.net/rfc/nullsafe_operator
- https://wiki.php.net/rfc/constructor_promotion
- https://wiki.php.net/rfc/enumerations
- https://wiki.php.net/rfc/readonly_properties_v2
- https://wiki.php.net/rfc/named_params
- https://wiki.php.net/rfc/union_types_v2
- https://wiki.php.net/rfc/attributes_v2
- https://wiki.php.net/rfc/arrow_functions_v2
- https://wiki.php.net/rfc/typed_properties_v2
- https://wiki.php.net/rfc/first_class_callable_syntax
- https://wiki.php.net/rfc/noreturn_type
- https://wiki.php.net/rfc/new_in_initializers
- https://wiki.php.net/rfc/readonly_classes
- https://wiki.php.net/rfc/dnf_types
- https://wiki.php.net/rfc/typed_class_constants
- https://wiki.php.net/rfc/property-hooks
- https://wiki.php.net/rfc/asymmetric-visibility-v2
- https://wiki.php.net/rfc/new_without_parentheses
- https://wiki.php.net/rfc/pipe-operator-v3
- https://wiki.php.net/rfc/clone_with_v2
- https://wiki.php.net/rfc/deprecate_dynamic_properties
- https://wiki.php.net/rfc/redact_parameters_in_back_traces
- https://wiki.php.net/rfc/rng_extension
- https://wiki.php.net/rfc/is_list
- https://wiki.php.net/rfc/url_parsing_api
- https://wiki.php.net/todo/php86
- https://github.com/symfony/polyfill
- https://github.com/symfony/polyfill-php80
- https://github.com/symfony/polyfill-php81
- https://github.com/symfony/polyfill-php83
- https://packagist.org/packages/symfony/polyfill-php83
- https://github.com/symfony/polyfill-php84
- https://github.com/symfony/polyfill-php85
