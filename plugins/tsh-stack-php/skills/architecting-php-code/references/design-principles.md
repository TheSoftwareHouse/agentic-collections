# Design Principles

Use this reference when choosing, defending or challenging a design decision in PHP code by appeal to SOLID, YAGNI, KISS, DRY, the wrong abstraction, replacing inheritance with delegation, Tell Don't Ask or the four rules of simple design.

## Table of Contents

- [Single Responsibility](#single-responsibility)
- [Open/Closed](#openclosed)
- [Liskov Substitution](#liskov-substitution)
- [Interface Segregation](#interface-segregation)
- [Dependency Inversion](#dependency-inversion)
- [YAGNI](#yagni)
- [KISS](#kiss)
- [DRY](#dry)
- [The Wrong Abstraction](#the-wrong-abstraction)
- [Replace Inheritance with Delegation](#replace-inheritance-with-delegation)
- [Tell, Don't Ask](#tell-dont-ask)
- [Four Rules of Simple Design](#four-rules-of-simple-design)
- [Sources](#sources)

## Single Responsibility

What it is: "each software module should have one and only one reason to change." Equivalently: "Gather together the things that change for the same reasons. Separate those things that change for different reasons." It applies separation of concerns, coupling and cohesion, and isolation of design decisions likely to change.

A reason to change is tied to people: changes to a module should come from a single, tightly coupled group representing one narrowly defined business function. An `Employee` with `calculatePay()` (finance), `reportHours()` (operations) and `save()` (technology) has three reasons to change.

When to use: whenever code that different groups care about sits together. Typical violations: SQL inside templates, HTML generated in computation modules, business rules that know the database schema. It applies to microservices too.

Pitfalls:

- Bug fixes and refactorings are changes made by programmers; the principle is about the people who request behaviour.
- Mixed responsibilities cause unintended breakage, after which stakeholders demand that a method is never changed again.

## Open/Closed

What it is: a module is open (available for extension) and closed (usable by other modules through a stable, well-defined interface). Apply it as: "You should be able to extend the behavior of a system without having to modify that system."

When to use: when requirements change and only part of the existing code is wrong; add features by writing new code. Plugin systems are the strongest form: "The system doesn't know about the plugins. The plugins know about the system." Core business rules are not bound to a feature set, interface, database or framework.

Mechanism: separate high-level policy from low-level detail, with dependencies pointing from the plugin toward the system.

Pitfalls: without it, `if` statements spread through the code; a feature that can only be added by changing many places (Shotgun Surgery) signals a violation; dependencies crossing a boundary in the wrong direction undermine it. "Simple code is both open and closed."

## Liskov Substitution

What it is: "A program that uses an interface must not be confused by an implementation of that interface." It concerns subtyping, not only inheritance, and includes implied interfaces in duck typing. When it is violated, `if`/`switch` statements proliferate in the callers.

Covariance: a child method may return a more specific type than its parent.

```php
interface AnimalShelter
{
    public function adopt(string $name): Animal;
}

class CatShelter implements AnimalShelter
{
    public function adopt(string $name): Cat
    {
        return new Cat($name);
    }
}
```

Contravariance: a child method may accept a less specific parameter type than its parent.

```php
abstract class Animal
{
    public function eat(AnimalFood $food)
    {
    }
}

class Dog extends Animal
{
    public function eat(Food $food)
    {
    }
}
```

`Dog::eat()` accepts `Food`, a supertype of `AnimalFood`. A `Cat` that does not override `eat()` still enforces `AnimalFood`, and passing `Food` fails with `TypeError: Argument 1 passed to Animal::eat() must be an instance of AnimalFood, instance of Food given`.

"More specific" means: a type removed from a union, a type added to an intersection, a class changed to a child class, or `iterable` changed to `array` or `Traversable`.

Property variance: properties are invariant by default. A property with only `get` may be covariant; one with only `set` may be contravariant. Once a property has both, it is no longer covariant or contravariant for further extension: below, `DogOwner` is allowed and `PoodleOwner` is not.

```php
interface PetOwner
{
    public Animal $pet { get; }
}

class DogOwner implements PetOwner
{
    public Dog $pet;
}

class PoodleOwner extends DogOwner
{
    public Poodle $pet;
}
```

| PHP | Variance support |
| --- | --- |
| 7.2 | Partial contravariance: type restrictions on parameters in a child method can be removed. |
| 7.4 | Full covariance and contravariance. |
| 8.4 | Abstract and virtual properties can be covariant (get only) or contravariant (set only). |
| 8.5 | A `static` return type in a parent may be overridden with `self` or the class's own type in a `final` subclass. |

## Interface Segregation

What it is: "Keep interfaces small so that users don't end up depending on things they don't need." It matters most in statically typed code; dynamically typed code is affected much less but not immune. Splitting is not always feasible or desirable.

## Dependency Inversion

What it is: "Depend in the direction of abstraction. High level modules should not depend upon low level details." Apply it across architectural boundaries, so business rules stay isolated from SQL, GUI and protocol details.

## YAGNI

What it is: "You Aren't Gonna Need It": do not build now a capability presumed to be needed in the future. A presumptive feature is any code supporting a feature that is not yet available for use, including fields or methods added before they are used.

When not to use: effort that makes the software easier to modify (refactoring), or a future-oriented choice that adds no complexity.

Costs of building a presumptive feature early: build, delay, carry and repair. About one third of features improve the metrics they target, and unused extensibility points get in the way.

Pitfalls:

- YAGNI is "only a viable strategy if the code is easy to change"; without self-testing code and continuous delivery it "becomes harmful".
- It is "not a justification for neglecting the health of your code base."

## KISS

What it is: "All design should be as simple as possible, but no simpler." Complexity leads to more errors and greater maintenance effort. Simple means understandable: "within the conceptual reach" of other readers, straightforward, requiring less analytic skill to follow.

Rule when writing code:

1. Decide the design before writing: consider at least two ways of doing the thing and pick the simpler one. Aim for the simplest result, not the quickest route.
2. Write that simplest form once, already free of duplication (see [DRY](#dry)): no superstructure, nothing fancy, an `if` statement if that does it. Do not write a draft to simplify later.

Recognise a violation: superstructure built before the core works; programming tricks; code that needs analysis to follow; output produced and then partly undone (a separator printed, then erased). Shorter code is not automatically simpler.

What to do: replace the trick with the straightforward construct, and hide unavoidable complexity so users of the code do not have to deal with it.

When not to apply it:

- Simple is not "quick and dirty", and it is no reason to discard needed features; simplifying often takes several iterations.
- Over-simplified code fails to solve part of the problem or introduces new problems.
- Do not be so greedy for today's simplest thing that tomorrow's becomes piling patches on patches; weigh the effect on the complexity of the surrounding code.
- "Simplest" has no metric, and people find different things simple. Removing features once added is very hard, so prefer not adding them.

```php
$line = '';
foreach ($names as $name) {
    $line .= $name . ', ';
}
$line = rtrim($line, ', ');
```

```php
$line = implode(', ', $names);
```

## DRY

What it is: "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system." Knowledge includes code, database schemas, documentation, test plans and the build. It is about duplicated knowledge and intent; copy-pasted lines are a small part.

Rule when writing code: give each fact (a format, a rule, a derived value, a contract) one authoritative place, and make every other use reach it.

Recognise a violation: when a single facet changes, the change has to be made in several places or formats (code and documentation, a schema and the structure holding it). Common forms in PHP:

- Code: the same formatting or rule repeated across methods.
- Documentation: a comment restating the code; fix it with a better name.
- Data: a stored value derivable from others (a length from start and end); compute it instead.
- Representation: both sides of an API or schema; mitigate with a formal spec such as OpenAPI, code generated from it, or schema introspection.
- Between developers: the same utility implemented many times; keep utilities in one known place and make reuse easy.

What to do: extract the knowledge into one named unit and call it everywhere. Expose data through methods, not public structures, so callers do not couple to the representation. Duplication is commonly removed on the third occurrence, especially when two cases are not enough to see what is common and what is unique; some refactor on the second.

When not to apply it:

- Code that looks alike but represents different knowledge is a coincidence, not duplication. `validateAge()` and `validateQuantity()` with identical bodies stay separate.
- Mechanical duplication generated from a well-known authoritative source, or enforced by the compiler, is allowed.
- If merging forces parameters and conditional paths into shared code, keep the duplication (see [The Wrong Abstraction](#the-wrong-abstraction)). Do not introduce unnecessary coupling to remove duplication.
- Deliberate duplication for performance, such as a cached value, is allowed when its impact is localised: only the owning class's methods keep it correct.
- Build a code generator only for a business benefit (for example high volatility), after producing the output by hand; it carries a maintenance cost.

```php
public function summary(float $net, float $tax): string
{
    return 'Net: ' . number_format($net, 2, '.', ',')
        . ' Tax: ' . number_format($tax, 2, '.', ',');
}
```

```php
public function summary(float $net, float $tax): string
{
    return 'Net: ' . $this->formatAmount($net) . ' Tax: ' . $this->formatAmount($tax);
}

private function formatAmount(float $amount): string
{
    return number_format($amount, 2, '.', ',');
}
```

## The Wrong Abstraction

What it is: shared code that no longer fits its current uses. Sign: "If you find yourself passing parameters and adding conditional paths through shared code, the abstraction is incorrect."

How it arises: duplication is extracted into a named abstraction; a new requirement almost fits; a parameter and conditionals are added; more requirements add more until the code is hard to understand. It persists through sunk cost: "Existing code exerts a powerful influence."

Rule: "duplication is far cheaper than the wrong abstraction". Accumulating a few conditionals to understand the problem is occasionally fine, but abandon a wrong abstraction sooner rather than later.

Remedy: "the fastest way forward is back."

1. Inline the abstracted code into every caller.
2. In each caller, use the passed parameters to determine the subset that caller needs.
3. Delete the code that caller does not need.
4. Re-isolate the remaining duplication and extract abstractions that fit the current requirements.

## Replace Inheritance with Delegation

What it is: a refactoring for a subclass that uses only part of its superclass. Create a field holding a superclass object, delegate methods to it, and remove the inheritance; the superclass becomes "the helper of the subclass, not its parent."

When to use: the subclass violates Liskov substitution; inheritance was used only to combine common code; or the subclass uses only some superclass methods, so someone will eventually call one they should not. The reverse refactoring is Replace Delegation with Inheritance.

Pros: no unneeded inherited methods; the delegate field can hold different implementations (in effect the Strategy pattern). Cons: many simple delegating methods.

Mechanics:

1. Create a field in the subclass holding the superclass object, initially the current object.
2. Change subclass methods to use that field instead of `$this`.
3. For superclass methods called by client code, create simple delegating methods.
4. Remove the inheritance declaration.
5. Initialise the field with a new superclass object.

## Tell, Don't Ask

What it is: "rather than asking an object for data and acting on that data, we should instead tell an object what to do." Behaviour moves into the object that holds the data. "Things that are tightly coupled should be in the same component."

Ask:

```php
if ($monitor->getValue() > $monitor->getLimit()) {
    $monitor->getAlarm()->warn($monitor->getName() . ' too high');
}
```

Tell:

```php
public function setValue(int $value): void
{
    $this->value = $value;
    if ($this->value > $this->limit) {
        $this->alarm->warn($this->name . ' too high');
    }
}
```

The caller writes `$monitor->setValue(3);`.

Limits: it is a stepping stone toward co-locating data and behaviour, the real goal. Objects can collaborate well by providing information, and co-location can give way to concerns such as layering: "Good design is all about trade-offs." Removing all query methods is harmful, as is convoluted telling where a query would be simpler.

## Four Rules of Simple Design

In priority order:

1. Passes the tests: "the primary aim is that it works as intended."
2. Reveals intention: "the key to enabling understanding is to express your intention in the code."
3. No duplication (DRY, SPOT, "Once and Only Once"): "the exercise of eliminating duplication is a powerful way to drive out good designs."
4. Fewest elements: "anything that doesn't serve the three prior rules should be removed."

Passing tests outranks revealing intention. The order of rules two and three matters little, because they refine each other; adding duplication for clarity usually hides a problem that should be solved instead. In rare conflicts, "empathy wins over some strictly technical metric."

Limits: "These criteria aren't perfect", but they catch obvious problems and can be checked immediately, while lifetime cost can only be judged afterwards.

## Sources

- https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html
- https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html
- https://blog.cleancoder.com/uncle-bob/2020/10/18/Solid-Relevance.html
- https://www.php.net/manual/en/language.oop5.variance.php
- https://martinfowler.com/bliki/Yagni.html
- https://wiki.c2.com/?KeepItSimple
- https://wiki.c2.com/?DoTheSimplestThingThatCouldPossiblyWork
- https://media.pragprog.com/titles/tpp20/dry.pdf
- https://wiki.c2.com/?DontRepeatYourself
- https://wiki.c2.com/?OnceAndOnlyOnce
- https://wiki.c2.com/?ThreeStrikesAndYouRefactor
- https://www.artima.com/articles/orthogonality-and-the-dry-principle
- https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction
- https://refactoring.guru/replace-inheritance-with-delegation
- https://martinfowler.com/bliki/TellDontAsk.html
- https://martinfowler.com/bliki/BeckDesignRules.html
