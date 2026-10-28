# Clean Code in PHP

Use this reference when writing or reviewing PHP at the level of functions, control flow, flag arguments, value objects, immutability, error reporting, nullsafe chains, type declarations and `strict_types`.

## Table of Contents

- [Small Functions](#small-functions)
- [Guard Clauses](#guard-clauses)
- [Flag Arguments](#flag-arguments)
- [Value Objects](#value-objects)
- [Immutability](#immutability)
- [Exceptions vs Results](#exceptions-vs-results)
- [Null Handling](#null-handling)
- [Type Declarations](#type-declarations)
- [strict_types](#strict_types)
- [Sources](#sources)

## Small Functions

- **What it is:** the separation between intention and implementation. If you have to spend effort looking at a fragment of code to figure out *what* it does, extract it into a function and name the function after that "what".
- **When to use:** whenever a fragment needs reading to understand its purpose, even if the result is a single line. An intention-revealing method such as `isEmpty()` beats the idiom `count($list) === 0`.
- **Not the main guide:** length rules (a function fits on a screen) and reuse rules (code used more than once gets its own function).
- **Scale:** any function longer than about half a dozen lines starts to smell; one-line functions are normal.
- **Pitfall, names:** small functions only work if the names are good, and naming takes practice.
- **Pitfall, performance:** call cost is rarely a factor; if it ever is, inline the function later.
- **Pitfall, nested functions:** they are naturally larger, so these size observations do not apply to them.

## Guard Clauses

- **What it is:** replace a nested conditional with a sequence of early-return checks, one per special case, with the default case last.
- **When to use:** a nested `if`/`else` that only assigns a `$result` variable to return at the end.
- **Also applies to validation:** linear guard clauses read more easily than deep nested `if`/`else`.

Before:

```php
public function getPayAmount(): float
{
    if ($this->isDead) {
        $result = $this->deadAmount();
    } else {
        if ($this->isSeparated) {
            $result = $this->separatedAmount();
        } else {
            if ($this->isRetired) {
                $result = $this->retiredAmount();
            } else {
                $result = $this->normalPayAmount();
            }
        }
    }

    return $result;
}
```

After:

```php
public function getPayAmount(): float
{
    if ($this->isDead) {
        return $this->deadAmount();
    }
    if ($this->isSeparated) {
        return $this->separatedAmount();
    }
    if ($this->isRetired) {
        return $this->retiredAmount();
    }

    return $this->normalPayAmount();
}
```

## Flag Arguments

- **What it is:** a function argument that tells the function to carry out a different operation.
- **Default:** avoid them. Separate methods state the caller's intent: `regularBook($martin)` reads better than `book($martin, false)`.
- **When the caller does not need to choose:** if behaviour depends only on the object's state, derive the flag internally. You only want different methods when the caller needs to specify which one it wants.
- **When a flag is acceptable:**
  - The logic is tangled and splitting it into separate methods is messy. Keep the flag in a private method behind explicit public ones.
  - The value comes straight from a boolean data source such as a UI control: `setSwitch($value)`. Otherwise prefer `setOn()` and `setOff()`.

Hidden flag implementation:

```php
final class Concert
{
    public function regularBook(Customer $customer): Booking
    {
        return $this->hiddenBookImpl($customer, false);
    }

    public function premiumBook(Customer $customer): Booking
    {
        return $this->hiddenBookImpl($customer, true);
    }

    private function hiddenBookImpl(Customer $customer, bool $isPremium): Booking
    {
        return new Booking($customer, $isPremium);
    }
}
```

## Value Objects

- **What it is:** an object that is equal to another because of the values of its properties, such as a point equal when `x` and `y` are equal. A reference object is the opposite: identity matters more than contents.
- **When to use:** small concepts such as points, money and ranges. Replacing common primitives such as strings with value objects is often a good idea: it makes types explicit, gives validation a home and prevents operations that do not apply.
- **Context decides:** a postal address can be a value object in one system and a reference object in another.
- **Equality:** value equality means the program does not need to know whether it holds a reference to the same object in memory. Give the class an explicit `equals()` method.
- **Rule:** value objects should be immutable. See [Immutability](#immutability).

```php
final class Point
{
    public function __construct(
        public readonly int $x,
        public readonly int $y,
    ) {
    }

    public function equals(self $other): bool
    {
        return $this->x === $other->x && $this->y === $other->y;
    }
}
```

- **Pitfall, aliasing:** modifying an object shared by two holders changes it for both. Instead of modifying a shared object, create a new one.
- **Pitfall, custom equality:** other libraries do not know about your `equals()` method.

## Immutability

- **What it is:** an object whose state does not change after construction. It prevents aliasing bugs.
- **How:** usually by not providing setters. In PHP, the `readonly` modifier prevents modification of a property after initialization.
- **readonly rules:**
  - Only typed properties can be `readonly`; use `mixed` for a property without a type constraint.
  - `readonly` static properties are not supported.
  - A `readonly` property can be initialized only once, and only from the scope where it is declared. Any other assignment or modification throws an `Error`, even when the value is the same.
- **Pitfall, interior mutability:** an object stored in a `readonly` property can still be modified internally. Only reassignment of the property is blocked.

```php
final class Test
{
    public function __construct(public readonly object $obj)
    {
    }
}

$test = new Test(new stdClass());
$test->obj->foo = 1;
$test->obj = new stdClass();
```

The last line throws `Error`; the line before it is legal.

**Version differences:**

| Version | Change |
| :-- | :-- |
| 8.1 | `readonly` properties introduced. Implicitly private-set: writable only from the declaring class. |
| 8.3 | `readonly` properties can be reinitialized inside `__clone()`. |
| 8.4 | `readonly` is implicitly `protected(set)`, so child classes may set it; this can be overridden explicitly. Indirect modification inside `__clone()`, such as `$ref = &$this->prop`, is no longer allowed. |

## Exceptions vs Results

- **What it is:** a choice between throwing and collecting errors. Exceptions are reserved for unexpected events. In validation, failures are expected.
- **When to collect instead of throw:** validation. A throw stops at the first error; a Notification object collects every failure, and the caller checks `hasErrors()`. A boolean return says only that an error occurred, with no diagnostics.
- **When to throw:** truly exceptional behaviour. A missing well-known file such as `/etc/hosts` can throw; a missing path a user typed on the command line should not. Re-running validation on data that should already be valid, to catch programming errors, can also justify an exception.

```php
if ($numberOfSeats === null) {
    $notification->addError('number of seats cannot be null');

    return;
}
```

- **Pitfall, null dereference:** a naive swap of `throw` for `addError()` lets execution continue past a missing value. Return after recording the error.
- **Pitfall, behaviour change:** callers may depend on the first error message alone; a combined message breaks code that reads only the first error.
- **Pitfall, lost causes:** when the exception wrapped a cause, the notification must carry that cause too. `Exception::__construct()` takes `?Throwable $previous = null`, and `getPrevious()` returns it.
- **Pitfall, big steps:** migrate in the smallest behaviour-preserving steps, and keep the throwing method while callers move over.

## Null Handling

- **What it is:** the nullsafe operator `?->` (PHP 8.0) with full short circuiting. When the left side is `null`, the whole chain evaluates to `null`.

```php
$country = $session?->user?->getAddress()?->country;
```

- **Short circuit:** in `$foo?->bar(expensiveFunction())`, `expensiveFunction()` does not run when `$foo` is `null`.
- **When not to use:**
  - Write context is not allowed: `$foo?->bar->baz = 'baz';`.
  - Taking a reference to a nullsafe chain is not allowed: `$x = &$foo?->bar;`.
- **Not available:** there is no `?[]` operator and no nullsafe call syntax such as `$callableOrNull?()`.

## Type Declarations

- **What it is:** declarations on function arguments, return values, class properties and class constants. Every type PHP supports except `resource` can be declared.
- **Nullable:** `?T` and `T|null` are identical. Only a single base type can be marked with `?`.

```php
function f(?C $c): void
{
    var_dump($c);
}
```

- **Union pitfalls:** `false` and `true` cannot be combined; use `bool`. With `bool`, `false` or `true` cannot be added. With `object`, class types cannot be added. With `iterable`, `array` and `Traversable` cannot be added.
- **Intersection pitfalls:** only class types are allowed; `self`, `parent` and `static` are errors. `int&Traversable` and `self&Traversable` are disallowed.
- **`never` and `mixed`:** using either in a composite type is an error.
- **`void`:** returning by reference from a `void` function is deprecated as of 8.1, because such a function is contradictory.

**Version differences:**

| Version | Change |
| :-- | :-- |
| 7.1 | `void`, `iterable` and nullable types |
| 7.2 | `object` |
| 7.4 | Class property types |
| 8.0 | `mixed`, union types, return-only `static` |
| 8.1 | Return-only `never`, intersection types; by-reference return from `void` deprecated |
| 8.2 | DNF types (intersections combined with unions), literal `true`, standalone `null` and `false`; before 8.2 a union of only `false` and `null` was not allowed |
| 8.3 | Typed class, interface, trait and enum constants |

## strict_types

- **What it is:** a per-file switch between coercive and strict typing. By default PHP coerces values of the wrong type into the expected scalar type where possible. With `declare(strict_types=1);`, only a value that exactly matches the declaration is accepted; anything else throws `TypeError`.
- **Exception:** an `int` value still passes a `float` declaration.
- **Scope:** it applies to function calls made from within the file that enables it, and to return values of functions declared in it. It is defined only for scalar type declarations.
- **When to use:** when wrong scalar types should fail with `TypeError` instead of being silently coerced.

```php
<?php

declare(strict_types=1);

function sum(int $a, int $b): int
{
    return $a + $b;
}

var_dump(sum(1, 2));
var_dump(sum(1.5, 2.5));
```

In strict mode the second call throws `TypeError`. Without the declaration both calls return `int(3)`, because `1.5` and `2.5` are coerced to integers.

- **Pitfall, return values:** with strict typing, `function sum($a, $b): int` returning `1 + 2.5` throws `TypeError: sum(): Return value must be of type int, float returned`.

## Sources

- https://martinfowler.com/bliki/FunctionLength.html
- https://refactoring.com/catalog/replaceNestedConditionalWithGuardClauses.html
- https://martinfowler.com/bliki/FlagArgument.html
- https://martinfowler.com/bliki/ValueObject.html
- https://www.php.net/manual/en/language.oop5.properties.php
- https://martinfowler.com/articles/replaceThrowWithNotification.html
- https://www.php.net/manual/en/class.exception.php
- https://wiki.php.net/rfc/nullsafe_operator
- https://www.php.net/manual/en/language.types.declarations.php
