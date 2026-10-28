# Refactoring Catalog

Use this reference when you need the name, aliases and target shape of a refactoring from the refactoring.com catalog, or a safe process for changing structure without breaking clients.

## Table of Contents

- [Catalog](#catalog)
- [PHP Before and After](#php-before-and-after)
- [Characterization Tests](#characterization-tests)
- [Parallel Change](#parallel-change)
- [Branch by Abstraction](#branch-by-abstraction)
- [Strangler Fig Application](#strangler-fig-application)
- [Deprecating Public APIs](#deprecating-public-apis)
- [Technical Debt Quadrant](#technical-debt-quadrant)
- [Sources](#sources)

Most catalog pages show only a title, aliases and an example. Each entry below states the target shape the example shows; mechanics, when to use and pitfalls are given only where a page states them. Use these names in reviews so the fix is unambiguous.

## Catalog

**Basic set**
- Extract Function (alias Extract Method): move a fragment into its own function. Inverse: Inline Function.
- Inline Function (alias Inline Method): replace a call with the body, e.g. `moreThanFiveLateDeliveries($driver)` becomes `$driver->numberOfLateDeliveries > 5`.
- Extract Variable (alias Introduce Explaining Variable): name the parts of a complex expression. Inverse: Inline Variable.
- Inline Variable (alias Inline Temp): replace a variable with the expression it holds.
- Change Function Declaration (aliases Rename Function, Rename Method, Add Parameter, Remove Parameter, Change Signature): e.g. `circum($radius)` becomes `circumference($radius)`.
- Encapsulate Variable (aliases Self-Encapsulate Field, Encapsulate Field): data is read and written only through a getter and a setter.
- Rename Variable: e.g. `$a = $height * $width` becomes `$area = $height * $width`.
- Introduce Parameter Object: `amountInvoiced($startDate, $endDate)` and its siblings take one `$dateRange` instead.
- Combine Functions into Class: functions over the same data become methods of one class, e.g. `Reading`.
- Combine Functions into Transform: a function copies the input and adds the derived fields to the copy.
- Split Phase: one input is processed in two phases joined by a data structure, e.g. parse an order, then price the parsed record.

**Encapsulation**
- Encapsulate Record (alias Replace Record with Data Class): a record becomes a class with fields and accessors.
- Encapsulate Collection: the getter returns a copy; changes go through `addCourse()` and `removeCourse()` instead of a setter for the whole list.
- Replace Primitive with Object (aliases Replace Data Value with Object, Replace Type Code with Class): e.g. priority strings become a `Priority` object with `higherThan()`.
- Replace Temp with Query: replace a temporary holding an expression with a method that computes the same value.
- Extract Class: e.g. telephone fields move out of `Person` into `TelephoneNumber`. Inverse: Inline Class.
- Hide Delegate: `$person->department->manager` becomes `$person->manager()`. Inverse: Remove Middle Man, where clients call the delegate directly.
- Substitute Algorithm: e.g. a loop searching for candidate names becomes a lookup in a list of candidates.

**Moving features**
- Move Function (alias Move Method): e.g. `overdraftCharge()` moves from `Account` to `AccountType`.
- Move Field: e.g. `Customer` stops holding a discount rate and reads it from its plan.
- Move Statements into Function: repeated statements move from callers into the function they call. Inverse: Move Statements to Callers.
- Replace Inline Code with Function Call: use an existing function instead of hand-written code, e.g. `in_array('MA', $states, true)` instead of a loop.
- Slide Statements: reorder statements so related ones sit together.
- Split Loop: one loop computing two values becomes two loops.
- Replace Loop with Pipeline: a loop that filters and collects becomes a filter followed by a map.
- Remove Dead Code: e.g. delete `if (false) { ... }`.

**Organizing data**
- Split Variable (aliases Remove Assignments to Parameters, Split Temp): a temp reused for two values becomes one variable per purpose.
- Rename Field: e.g. `name()` becomes `title()`.
- Replace Derived Variable with Query: compute a derived value in a getter instead of updating a stored field in a setter.
- Change Reference to Value: replace a mutated inner object with a new instance, e.g. a new `Money`. Inverse: Change Value to Reference, e.g. load a shared `Customer` from a repository instead of constructing one.

**Simplifying conditional logic**
- Decompose Conditional: name the condition and move each branch into its own function.
- Consolidate Conditional Expression: combine checks that give the same result into one named condition (see PHP example).
- Replace Conditional with Polymorphism: a switch on a type field becomes one class per type, each with its own method.
- Replace Nested Conditional with Guard Clauses: one early `return` per special case, then the normal result.
- Introduce Special Case (alias Introduce Null Object): a check for a special value becomes a class such as `UnknownCustomer` returning the default.
- Introduce Assertion: add `assert($this->discountRate >= 0)` before code that relies on it.
- Replace Control Flag with Break (alias Remove Control Flag): remove the boolean flag recording that a loop found its target and exit with `break`.

**Refactoring APIs**
- Separate Query from Modifier: split a function that returns a value and has a side effect, e.g. `getTotalOutstandingAndSendBill()` into `totalOutstanding()` and `sendBill()`.
- Parameterize Function (alias Parameterize Method): functions differing only by a literal become one with a parameter, e.g. `raise($person, $factor)`.
- Remove Flag Argument (alias Replace Parameter with Explicit Methods): `setDimension($name, $value)` becomes `setHeight($value)` and `setWidth($value)`.
- Preserve Whole Object: pass `$room->daysTempRange` instead of `low` and `high` taken from it.
- Replace Parameter with Query (alias Replace Parameter with Method): drop a parameter the function can read from another parameter. Inverse: Replace Query with Parameter, where the caller passes the value in.
- Remove Setting Method: a class keeps the getter and loses the setter.
- Replace Constructor with Factory Function (alias Replace Constructor with Factory Method): e.g. `new Employee($data, 'E')` becomes `createEngineer($data)`.
- Replace Function with Command (alias Replace Method with Method Object): parameters move to a constructor and the body to `execute()`. Inverse: Replace Command with Function, for a command with one `execute()` method.
- Return Modified Value: a function builds and returns a local result instead of updating an outer variable.
- Replace Error Code with Exception: e.g. `return -23;` becomes `throw new OrderProcessingError(-23);`.
- Replace Exception with Precheck (alias Replace Exception with Test): check the index before access instead of catching an out-of-bounds exception.

**Dealing with inheritance**
- Pull Up Method, Pull Up Field, Pull Up Constructor Body: members or setup duplicated in subclasses move to the superclass. Inverses: Push Down Method, Push Down Field.
- Push Down Method, Push Down Field: a member moves from the superclass to the subclass that uses it.
- Replace Type Code with Subclasses (aliases Replace Type Code with State/Strategy, Extract Subclass): a type code becomes subclasses created by a factory. Inverse: Remove Subclass (alias Replace Subclass with Fields).
- Extract Superclass: classes with similar features get a shared parent, e.g. `Party` for `Department` and `Employee`.
- Collapse Hierarchy: the page shows only the starting shape, `Salesman extends Employee`.
- Replace Subclass with Delegate: a subclass becomes a delegate object the class consults.
- Replace Superclass with Delegate (alias Replace Inheritance with Delegation): e.g. `Stack extends List` becomes `Stack` holding a `List`.

## PHP Before and After

### Consolidate Conditional Expression

Use it when several checks share one outcome and represent one concept. The function name states intent and the caller reads one line. Mechanics: find the checks with the same result, join them with `||`, move them into a named function.

Before:

```php
if ($employee->seniority < 2) {
    return 0;
}
if ($employee->monthsDisabled > 12) {
    return 0;
}
if ($employee->isPartTime) {
    return 0;
}
```

After:

```php
if ($this->isNotEligibleForDisability($employee)) {
    return 0;
}

private function isNotEligibleForDisability(Employee $employee): bool
{
    return $employee->seniority < 2
        || $employee->monthsDisabled > 12
        || $employee->isPartTime;
}
```

### Decompose Conditional

```php
if ($this->isSummer($date)) {
    $charge = $this->summerCharge();
} else {
    $charge = $this->regularCharge();
}
```

Before, the condition held the raw date-range comparison against the plan's summer start and end.

### Separate Query from Modifier

Before: `getTotalOutstandingAndSendBill()` both computes and sends. After:

```php
public function totalOutstanding(): int
{
    $total = 0;
    foreach ($this->invoices as $invoice) {
        $total += $invoice->amount;
    }

    return $total;
}

public function sendBill(): void
{
    $this->mailer->sendBill($this);
}
```

Replace calls with the query and call the modifier where the side effect is needed.

### Replace Control Flag with Break

```php
foreach ($people as $person) {
    if ($person === 'Don' || $person === 'John') {
        $this->sendAlert();
        break;
    }
}
```

Before, a `$found` flag was set to `true` and every iteration was wrapped in `if (!$found)`.

### Replace Function with Command

```php
final class Scorer
{
    private Candidate $candidate;
    private MedicalExam $medicalExam;
    private ScoringGuide $scoringGuide;

    public function __construct(Candidate $candidate, MedicalExam $medicalExam, ScoringGuide $scoringGuide)
    {
        $this->candidate = $candidate;
        $this->medicalExam = $medicalExam;
        $this->scoringGuide = $scoringGuide;
    }

    public function execute(): int
    {
        return $this->scoringGuide->score($this->candidate, $this->medicalExam);
    }
}
```

Before: `score($candidate, $medicalExam, $scoringGuide)`.

## Characterization Tests

A characterization test records what existing code actually does, not what it should do. Once in production, code effectively becomes its own specification.

Steps:
1. Break dependencies so the code runs in a test harness; this is the hardest part.
2. Write a placeholder test with a dummy expected value, e.g. `self::assertNull(Pattern::formatText('plain text'))`.
3. Run it and read the failure, which shows the actual output.
4. Put the actual value into the assertion and rename the test after the observed behaviour, e.g. `testDoesNotChangeUntaggedText`.
5. Investigate surprises; if undecided, leave the test in place.

When to use: before refactoring or rewriting code you do not fully understand; when you need to know immediately whether a change altered behaviour; when intended behaviour is unknown.

When not to use: when a specification exists and you need to verify correctness; as a way to decide whether observed behaviour is intended, since the tests record behaviour and do not validate it.

Pitfalls: bugs get locked in as correct; users may depend on a quirk, so removing a "bug" breaks them; test names go stale; breaking dependencies is expensive.

## Parallel Change

Also known as expand and contract: a pattern to implement backward-incompatible changes to an interface safely.

- Expand: augment the interface to support both the old and the new version.
- Migrate: update all clients to the new version; for external clients this is the longest phase.
- Contract: remove the old version so the interface supports only the new one.

Code can be released in any phase, and clients can be tested and moved gradually. During a refactoring, implement the old method in terms of the new API, then use Inline Function to update usages. A client-side feature toggle keeps a client forward-compatible with the new supplier. For remote APIs, follow Postel's Law so consumers do not break when the payload is expanded.

When to use: long-term refactorings; changes to a published interface; database refactoring in evolutionary database design; canary and blue-green deployments; remote API evolution, instead of explicit API versioning; introducing an abstraction layer.

When not to use: with many clients, Branch by Abstraction narrows the surface of change better.

Pitfalls: during migrate the supplier supports two versions and clients can confuse which is new. Skipping contract can leave you in a worse state than you started. Deprecation notes, documentation or TODO notes help inform clients.

Example: `addCell($x, $y)` and `fetchCell($x, $y)` gain overloads taking a `Coordinate`; after migration the `$x, $y` versions and the old storage are removed.

## Branch by Abstraction

Makes a large-scale change gradually so regular releases continue during it.

1. Parts of the system depend on a module, library or framework to replace.
2. Create an abstraction layer for one section of client code and route that section through it.
3. Migrate all clients to the abstraction, improving the supplier's test coverage through it.
4. Build the new supplier behind the same abstraction and switch one client section to it; feature flags can run it in test environments and compare its behaviour with the old one.
5. Move the remaining clients, delete the old supplier, and optionally remove the abstraction.

Fits replacing a dependency many parts of the system rely on while Continuous Delivery continues. If the supplier cannot be swapped for only some clients, you have to switch all at once. Ensure the system builds and runs correctly at all times. Checking that old and new implementations return the same results for the same requests is a described variation.

## Strangler Fig Application

A gradual approach to legacy modernization: new functionality is built alongside the legacy system and behaviour moves over incrementally. Four activities, in no fixed order: understand outcomes, break the problem up along seams, deliver the parts, change the organization.

When to use: patching no longer works and wholesale modernization is needed; users need ongoing features and an earlier return on investment; existing behaviour is hard to specify.

Pitfalls: simple replacement plans usually fail; copying behaviour nobody wants; groups wanting different things; legacy systems rarely have natural seams; transitional architecture costs effort; without new development practices the new system ends up in a similar mess.

## Deprecating Public APIs

`trigger_deprecation()` from `symfony/deprecation-contracts` takes the package name, the package version that introduced the deprecation, a message, and optional `printf()` values. It raises a silenced deprecation notice without interrupting execution; a custom error handler such as Symfony's ErrorHandler can log it.

```php
/**
 * @deprecated
 */
public function getTotalOutstandingAndSendBill(): int
{
    trigger_deprecation('acme/billing', '2.4', 'Using "%s" is deprecated, use "%s" instead.', 'getTotalOutstandingAndSendBill()', 'totalOutstanding()');

    $this->sendBill();

    return $this->totalOutstanding();
}
```

The package and version values above are placeholders. Opting out is possible with an empty `function trigger_deprecation() {}`, but not recommended.

## Technical Debt Quadrant

- Prudent and deliberate: debt taken knowingly to gain value sooner, e.g. a release date.
- Reckless and deliberate: shortcuts because the team believes it cannot afford clean code.
- Reckless and inadvertent: debt incurred without the design knowledge to see it.
- Prudent and inadvertent: a better design is learned only after building; inevitable for strong teams.

The useful distinction is prudent versus reckless, not debt versus non-debt. Prudent debt can stay unpaid if its interest is small, e.g. code rarely touched. Pitfalls: arguing whether something is debt; misjudging the design payoff line; inevitable debt used as an excuse for poor code.

## Sources

- https://refactoring.com/catalog/
- https://refactoring.com/catalog/consolidateConditionalExpression.html
- https://refactoring.com/catalog/decomposeConditional.html
- https://refactoring.com/catalog/separateQueryFromModifier.html
- https://refactoring.com/catalog/replaceControlFlagWithBreak.html
- https://refactoring.com/catalog/replaceFunctionWithCommand.html
- http://michaelfeathers.silvrback.com/characterization-testing
- https://martinfowler.com/bliki/ParallelChange.html
- https://martinfowler.com/bliki/BranchByAbstraction.html
- https://martinfowler.com/bliki/StranglerFigApplication.html
- https://github.com/symfony/deprecation-contracts
- https://martinfowler.com/bliki/TechnicalDebtQuadrant.html
