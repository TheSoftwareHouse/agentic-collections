# PHP coding standard (PSR-1, PSR-12, PER)

Use this reference when writing or reviewing PHP code formatting, choosing or running a style checker, or formatting PHP syntax that PSR-12 does not cover.

## Contents

- [Working Rules](#working-rules)
- [Status and versions](#status-and-versions)
- [PSR-1 Basic Coding Standard](#psr-1-basic-coding-standard)
- [PSR-12 Extended Coding Style](#psr-12-extended-coding-style)
- [PER Coding Style](#per-coding-style)
- [Tools](#tools)
- [Sources](#sources)

## Working Rules

1. The team standard is PSR-1 plus PSR-12. Every line of PHP written or changed follows it.
2. If the repository has its own checker configuration (`phpcs.xml`, `.php-cs-fixer.php`, `ecs.php`), that configuration is the standard; follow it where it differs from PSR-12.
3. Apply PER Coding Style rules only to syntax PSR-12 does not cover, and only if the project's PHP version has that syntax. Where PER and PSR-12 conflict, follow PSR-12 unless the project's checker configuration adopts PER.
4. Format new code to the standard; do not reformat unrelated existing code in the same change.
5. Before finishing, run the project's checker in check-only mode on the changed files, if one is installed.
6. In review, report each violation as `file:line`, the rule and its section number (for example `PSR-12 §4.4`), and the corrected line. Group repeats of one rule into one finding.

## Status and versions

- PSR-2 is deprecated. PSR-12 is recommended instead.
- PSR-12 "extends, expands and replaces PSR-2" and requires adherence to PSR-1.
- PSR-12 covers syntax added to PHP after PSR-2, which includes PHP 5.5, 5.6 and 7.0. The meta document says it "should be considered a new specification".
- PER Coding Style "extends, expands and replaces PSR-12", requires adherence to PSR-1 and makes the errata to PSR-12 binding. The current version is PER Coding Style 3.1. Earlier versions: 3.0, 2.0, 1.0.
- PSR-12 and PER both state that instructions MAY be ignored if they do not exist in the PHP versions the project supports. Detect the version with [`php-version-detection.md`](./php-version-detection.md).
- RFC 2119 keywords (MUST, SHOULD, MAY) are interpreted as in RFC 2119.

Pitfall: the PSR-2 page says to end files with a single blank line. PSR-12 §2.2 says files MUST end with a non-blank line terminated by a single LF. Follow PSR-12.

## PSR-1 Basic Coding Standard

"Class" means classes, interfaces and traits (§4).

- §2.1 PHP code MUST use the long `<?php ?>` tags or the short-echo `<?= ?>` tags. Other tag variations MUST NOT be used.
- §2.2 PHP code MUST use only UTF-8 without BOM.
- §2.3 A file SHOULD either declare symbols or cause side effects, not both. Side effects include generating output, `require`/`include`, connecting to external services, modifying ini settings, emitting errors or exceptions, modifying global or static variables, and reading or writing files. A conditional declaration such as `if (! function_exists(...))` is not a side effect.
- §3 Namespaces and classes MUST follow an autoloading PSR (PSR-0 or PSR-4). Each class is in its own file, in a namespace at least one level deep, with a top-level vendor name.
- §3 Code for PHP 5.3 and later MUST use formal namespaces. Code for 5.2.x and earlier SHOULD use `Vendor_` prefixes.
- Class names MUST be `StudlyCaps`. PSR-12 §2.1 reads this as PascalCase.
- §4.1 Class constants MUST be upper case with underscore separators: `DATE_APPROVED`.
- §4.2 No rule for property naming. Whatever convention is used SHOULD be applied consistently within a vendor, package, class or method.
- §4.3 Method names MUST be `camelCase()`.

## PSR-12 Extended Coding Style

### General (§2)

- §2.2 Unix LF line endings only. Files end with a non-blank line terminated by a single LF. Omit the closing `?>` in files containing only PHP.
- §2.3 No hard line-length limit. The soft limit MUST be 120 characters. Lines SHOULD NOT exceed 80 characters; longer lines SHOULD be split.
- §2.3 No trailing whitespace. Blank lines MAY be added for readability. At most one statement per line.
- §2.4 Indent with 4 spaces per level, never tabs.
- §2.5 Reserved keywords and types MUST be lower case. Use short type keywords: `bool`, not `boolean`.

### Declare, namespace and import (§3)

- Header blocks, if present, appear in this order: `<?php`; file docblock; `declare`; `namespace`; class imports; function imports; constant imports; remaining code. Each block is separated by a single blank line and MUST NOT contain a blank line.
- When `<?php` is on the first line, it MUST be on its own line with no other statements.
- Import statements MUST never begin with a leading backslash.
- A compound namespace group MUST NOT have more than two sub-namespaces.
- Declare statements MUST NOT contain spaces inside the parentheses: `declare(strict_types=1);`.
- In files mixing markup and PHP, the strict types declaration MUST be on the first line and include an opening PHP tag.
- Block declare statements are allowed.

### Classes, properties and methods (§4)

- No comment or statement may follow a closing brace on the same line.
- Always use parentheses when instantiating: `new Foo();`.
- §4.1 `extends` and `implements` MUST be on the same line as the class name. The opening brace is on its own line, not preceded or followed by a blank line. The closing brace is on its own line, right after the last body line.
- §4.1 A split `implements` list puts the first item on the next line, one interface per line:

```php
class ClassName extends ParentClass implements
    \ArrayAccess,
    \Countable
{
}
```

- §4.2 Trait `use` MUST be on the line after the opening brace, one trait per line. If nothing follows, the closing brace comes next; otherwise add a blank line after the `use` statements:

```php
class Talker
{
    use A;
    use B {
        A::smallTalk insteadof B;
    }
}
```

- §4.3 Visibility on all properties. No `var`. One property per statement. One space between the type and the property name.
- §4.4 Visibility on all methods. No underscore prefix. No space between the method name and `(`. The opening brace is on its own line.
- §4.5 No space before a comma, one after. Arguments with default values come last. The return type colon follows `)` directly, with one space after it. No space after `?`. No space after `&` or `...`.
- §4.6 `abstract` and `final` come before visibility. `static` comes after it.
- §4.7 Calls: no space before or after the parentheses. A split argument list has one argument per line. A single multi-line argument, such as a closure or array, does not count as splitting the list.

### Control structures (§5)

- One space after the keyword, none inside the parentheses, one space before the opening brace. The body is indented once. Braces are required.
- §5.1 Use `elseif`, not `else if`. A split condition starts on a new line. Boolean operators go consistently at line starts or at line ends, never mixed.
- §5.2 `case` is indented once from `switch`. `break` is aligned with the case body. Intentional fall-through needs a `// no break` comment.
- §5.6 Multi-type catch uses `|`.

### Operators (§6)

- §6.1 No space between `++`/`--` and the operand. No spaces inside cast parentheses.
- §6.2 At least one space on each side of arithmetic, comparison, assignment, bitwise, logical, string and type operators.
- §6.3 Spaces around `?` and `:` of a ternary. The short ternary `?:` follows binary operator spacing.
- Multiple spaces are allowed for alignment.

### Closures (§7) and anonymous classes (§8)

- §7 A space after `function`, and before and after `use`. The opening brace is on the same line; the closing brace is on the line after the body. No space inside the argument or variable list parentheses. Arguments with default values come last. A closure passed as a call argument follows the same rules.
- §8 Anonymous classes follow the closure rules. The opening brace MAY share the `class` line unless the `implements` list wraps; then it goes on the line after the last interface.

## PER Coding Style

PER Coding Style covers syntax PSR-12 does not, and tightens some PSR-12 rules. Section numbers refer to PER 3.1.

### Differences from PSR-12

| Topic | PSR-12 | PER |
|---|---|---|
| Boolean operators in split conditions | Line start or line end, consistently | MUST be at the beginning (§5.1) |
| Space after a cast | Not stated | Exactly one space: `(int) $input` (§6.1) |
| Trailing commas | Not stated | Required on multi-line lists, forbidden on single-line lists (§2.6) |
| Fall-through comment | `// no break` | "a clear comment MUST be included" (§5.2) |

The PER 2.0 migration document describes the changes from PSR-12 (PER-CS 1.0) to PER-CS 2.0. Most of it is new coverage rather than changed PSR-12 rules.

### General, naming and imports

- §2.5 Union `|` and intersection `&` MUST NOT have a leading or trailing space; neither do DNF parentheses: `array|(ArrayAccess&Traversable)`. `null` MUST be last. A union of one simple type with `null` SHOULD use `?`. A split compound type has one type (or one union segment) per line, with the split symbol at the start of each line. New types and keywords in future PHP versions MUST be lower case.
- §2.6 Trailing commas apply to arrays, arguments, closure `use` lists and `match` arms.
- §2.7 Follow the php-src coding standards for naming. Abbreviations, acronyms and initialisms SHOULD be avoided wherever possible.
- §3 The `<?php` tag MUST always be lower case.

### Classes, properties and methods

- §4.3 Visibility MUST be declared on all constants. If set-visibility is given, the general visibility MAY be omitted: `protected(set) string $name;`.
- §4.4 A method with no statements or comments SHOULD have its body abbreviated to `{}` on the same line, separated by a space. The PER 2.0 migration document says the same for an empty class body: `class MyException extends \RuntimeException {}`.

```php
class Point
{
    public function __construct(private int $x, private int $y) {}
}
```

- §4.6 Modifier order: `abstract`/`final`; `public`/`protected`/`private`; `public(set)`/`protected(set)`/`private(set)`; `static`; `readonly`; type; name. All on one line, lower case, separated by one space: `final public static function bar() {}`, `private readonly int $beep;`.
- §4.7 Named arguments: no space before the colon, one space after: `somefunction($a, b: $b, c: 'c');`. The PER 2.0 migration document adds that chained calls may span lines, first method on the next line, each line indented once.
- §4.8 First-class callables: no whitespace around `...`: `$callable = $item->doSomething(...);`.
- §4.9 Property hooks: the long form opens with a brace on the property line, one space before it; the closing brace is on its own line with no comment after it; each hook body is indented once. The short form has one space on each side of `=>`. Inline hooks are allowed only with a single short hook that does not wrap, including on promoted properties.

```php
public string $myName { get => __CLASS__; }

public function __construct(
    public string $name { set => ucfirst($value); }
) {}
```

- §4.10 Interface and abstract properties state whether they support `get`, `set` or both. `get` comes before `set`. No space between the operation and its semicolon.

```php
interface Example
{
    public string $readable { get; }
    public string $writeable { set; }
    public string $both { get; set; }
}
```

### Control structures, operators and closures

- §5.1 In a split condition, the first condition MUST start on the next line, boolean operators MUST be at the beginning, and the closing parenthesis and opening brace go together on their own line.
- §5.2 The `case` body MUST NOT be wrapped in `{}`. Non-empty cases end with `break`, `return` or similar. `default` is followed by a colon.

```php
$returnValue = match ($expr) {
    0 => 'First case',
    1, 2, 3 => multipleCases(),
    default => 'Default case',
};
```

- §6.2 The pipe operator `|>` is a binary operator: `$foo = $a |> log(...) |> round(...);`.
- §6.4 A split statement puts the operator at the beginning of the new line. A split ternary MUST occupy 3 lines, never 2.

```php
$variable4 = '<foo>'
    |> strtoupper(...)
    |> htmlspecialchars(...);
```

- §7 An empty closure body MUST be `{}` on the same line. Empty-body closures SHOULD be replaced with arrow functions where possible.
- §7.1 Arrow functions: no space after `fn`, a space on each side of `=>`. If the expression wraps, `=>` goes on the second line, indented once: `$func = fn(int $x, int $y): int => $x + $y;`.
- §8 An anonymous class with no constructor arguments MUST omit `()` after `class`.

### Enums, heredoc, arrays, attributes

- §9 Enums follow class rules. Non-public methods and constants MUST be `private`, not `protected`. A backed enum has no space before the colon and one after. Cases are PascalCase, one per line. Constants MAY be PascalCase or UPPER_CASE; PascalCase is RECOMMENDED.

```php
enum Suit: string
{
    case Hearts = 'H';
    case Diamonds = 'D';
}
```

- §10 A nowdoc SHOULD be used wherever possible; a heredoc MAY be used when a nowdoc cannot work. The heredoc or nowdoc begins on the same line as its context. Body lines are indented one level past the enclosing scope.
- §11 Arrays MUST use the short syntax. The opening bracket is not on its own line. The closing bracket is on the line after the last value. At most one value assignment per line.

```php
$arr2 = [
    'multi',
    'line',
    [
        'nested',
        'array',
    ],
];
```

- §12 No space after `#[`. Omit `()` when there are no arguments. Attributes on classes, methods, functions, constants and properties go on their own line right before the structure; a docblock comes first, with no blank lines between. Parameter attributes are inline on a single-line parameter list. Multiple attributes in one block are separated by a comma and a space; a split list uses separate blocks. An attribute with a split argument list is alone in its block.

## Tools

| Tool | Check | Fix | Notes |
|---|---|---|---|
| PHP_CodeSniffer | `phpcs /path/to/code-directory` | `phpcbf` | Default standard is PSR12. Choose another with `--standard=PEAR`. Install as a dev dependency: `"squizlabs/php_codesniffer": "^4.0"`. |
| PHP-CS-Fixer | `vendor/bin/php-cs-fixer check` | `vendor/bin/php-cs-fixer fix` | `check` equals `fix --dry-run` and applies no changes. `--diff` prints changes in udiff format. Without a config, `fix .` uses `@PSR12`. `--rules` overrides the config. |
| Easy Coding Standard | `vendor/bin/ecs src tests` | `vendor/bin/ecs --fix` | Check is the default. Presets: `->withPreparedSets(psr12: true)` or `perCs: true`. |

- PHP-CS-Fixer standard sets: `@PSR1`, `@PSR2`, `@PSR12`, `@PSR12:risky`, `@Symfony`, `@Symfony:risky`, `@PhpCsFixer`, `@PhpCsFixer:risky`.
- PHP-CS-Fixer PER sets: `@PER-CS`, `@PER-CS1x0`, `@PER-CS2x0`, `@PER-CS3x0`, each with a `:risky` variant. Deprecated: `@PER`, `@PER-CS1.0`, `@PER-CS2.0`, `@PER-CS3.0` and their `:risky` variants.
- PHP-CS-Fixer exit codes are bit flags: 0 OK; 1 general error; 4 invalid syntax; 8 some files need fixing; 16 application config error; 32 fixer config error; 64 exception. Codes 4 and 8 apply to `check` and dry-run only.
- PHP-CS-Fixer CI example:

```bash
vendor/bin/php-cs-fixer check --config=.php-cs-fixer.dist.php -v --show-progress=dots --stop-on-violation --using-cache=no
```

- ECS config example:

```php
use Symplify\EasyCodingStandard\Config\ECSConfig;

return ECSConfig::configure()
    ->withPaths([__DIR__ . '/src', __DIR__ . '/tests'])
    ->withPreparedSets(psr12: true);
```

- ECS `withPreparedSets` topics: `arrays`, `spaces`, `namespaces`, `docblocks`, `controlStructures`, `comments`, `casing`, `cleanup`, or `common: true` for all. Standalone presets: `psr12`, `perCs`, `cleanCode`, `standaloneLine`, `laravel`.

## Sources

- https://www.php-fig.org/psr/psr-1/
- https://www.php-fig.org/psr/psr-12/
- https://github.com/php-fig/fig-standards/blob/master/accepted/PSR-12-extended-coding-style-guide-meta.md
- https://www.php-fig.org/psr/psr-2/
- https://www.php-fig.org/per/coding-style/
- https://github.com/php-fig/per-coding-style/blob/3.1.0/spec.md
- https://github.com/php-fig/per-coding-style/blob/master/migration-2.0.md
- https://cs.symfony.com/doc/ruleSets/index.html
- https://github.com/PHPCSStandards/PHP_CodeSniffer
- https://github.com/easy-coding-standard/easy-coding-standard
- https://raw.githubusercontent.com/PHP-CS-Fixer/PHP-CS-Fixer/master/doc/usage.rst
