# Behavioral Design Patterns in PHP

Use this reference when replacing growing conditionals, wiring pluggable processing steps, modelling state transitions, or deciding whether an event, command, or strategy is warranted in PHP code.

## Table of Contents

[Admission Rule](#admission-rule) · [Strategy](#strategy) · [Command](#command) · [Observer](#observer) · [State](#state) · [Chain of Responsibility](#chain-of-responsibility) · [Template Method](#template-method) · [Iterator](#iterator) · [Mediator](#mediator) · [Memento](#memento) · [Visitor](#visitor) · [Interpreter](#interpreter) · [Sources](#sources)

## Admission Rule

There are ten classic behavioral patterns: Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method and Visitor. They "are concerned with algorithms and the assignment of responsibilities between objects." Several have a known overkill condition, and that condition is the admission test:

- Strategy: with only a few algorithms that rarely change, "there's no real reason to overcomplicate the program with new classes and interfaces".
- State: "Applying the pattern can be overkill if a state machine has only a few states or rarely changes."
- Iterator: "Applying the pattern can be an overkill if your app only works with simple collections."
- Command: "The code may become more complicated since you're introducing a whole new layer between senders and receivers."

Replace Conditional with Polymorphism applies when a conditional performs various actions depending on the class or interface of an object, the value of one of its fields, or the result of one of its methods. Create subclasses matching the branches of the conditional. It removes duplicate code, follows Tell-Don't-Ask, and a new variant becomes a new subclass (Open/Closed).

Symfony's EventDispatcher component "implements the Mediator and Observer design patterns". Check the framework feature listed under each pattern before writing your own.

## Strategy

**Intent.** "Define a family of algorithms, put each of them into a separate class, and make their objects interchangeable." The context delegates executing the behavior to the linked strategy object.

**Use when.**
- An object needs different variants of an algorithm and must switch between them at runtime.
- Many similar classes differ only in how they run some behavior.
- Business logic should be isolated from the implementation details of algorithms.
- A class has "a massive conditional statement that switches between different variants of the same algorithm."

**Pros.** Algorithms can be swapped at runtime; implementation details are isolated from the code that uses them; inheritance is replaced with composition; new strategies need no change to the context (Open/Closed). **Cons.** Overkill for a few rarely changing algorithms. Clients must know the differences between strategies to pick one. In languages with functional type support, the variants can be anonymous functions instead.

**Related.** Template Method is inheritance-based and static at the class level; Strategy is composition-based and works at the object level. Decorator changes an object's "skin", Strategy its "guts". State can be seen as an extension of Strategy, but strategies stay "completely independent and unaware of each other".

**Wiring in Symfony.** Tag every implementation with `#[AutoconfigureTag]` on the interface (YAML: `_instanceof`) and inject all of them with `#[AutowireIterator]` (YAML: `!tagged_iterator app.fee_calculator`). A referencing service that carries the same tag is excluded automatically.

```php
#[AutoconfigureTag('app.fee_calculator')]
interface FeeCalculator
{
    public function supports(Plan $plan): bool;

    public function fee(Plan $plan): Money;
}

final class FeeResolver
{
    /** @param iterable<FeeCalculator> $calculators */
    public function __construct(
        #[AutowireIterator('app.fee_calculator')] private iterable $calculators,
    ) {
    }

    public function fee(Plan $plan): Money
    {
        foreach ($this->calculators as $calculator) {
            if ($calculator->supports($plan)) {
                return $calculator->fee($plan);
            }
        }

        throw new NoFeeCalculator($plan);
    }
}
```

- Order tagged services with `#[AsTaggedItem(priority: ...)]`: an integer defaulting to `0`; higher is located earlier.
- To fetch one implementation lazily by ID, use `#[AutowireLocator]` and index services with `#[AsTaggedItem(index: ...)]`.
- Symfony 8.1 deprecates `getDefaultPriority()` / `default_priority_method`, `getDefault<CamelCase>Name()` and `default_index_method` in favour of `#[AsTaggedItem]`.

## Command

**Intent.** "Turns a request into a stand-alone object that contains all information about the request". This allows deferred or remote execution and storing command history.

**Use when.**
- Objects must be parameterized with operations.
- Operations must be queued, scheduled, or executed remotely.
- Operations must be reversible.

**Pros.** Invokers are decoupled from performers; new commands do not break existing client code; undo/redo, deferred execution, and assembling simple commands into a complex one become possible. **Cons.** A whole new layer between senders and receivers makes the code more complicated.

**Pitfalls.** Undo by state backup "may consume quite a lot of RAM", and some of the state can be private. Inverse operations may be "hard or even impossible to implement". Memento can save state before a command runs.

**Already provided.** Symfony Messenger "provides a message bus with the ability to send messages and then handle them immediately in your application or send them through transports (e.g. queues) to be handled later." A message class has no requirements "except that it can be serialized". Implement the handler as a class with `#[AsMessageHandler]` and an `__invoke()` type-hinted with the message class. For Doctrine entities, pass the primary key instead of the object.

```php
final class IssueInvoice
{
    public function __construct(public readonly string $invoiceId)
    {
    }
}

#[AsMessageHandler]
final class IssueInvoiceHandler
{
    public function __construct(private InvoiceRepository $invoices)
    {
    }

    public function __invoke(IssueInvoice $command): void
    {
        $this->invoices->get($command->invoiceId)->issue();
    }
}
```

- Route with `#[AsMessage('async')]` or YAML `routing`; config takes precedence. Unrouted messages are handled synchronously.
- A message is retried 3 times by default before being discarded or sent to the failure transport. `UnrecoverableMessageHandlingException` stops retries; `RecoverableMessageHandlingException` retries infinitely.
- "A single bus is a good default. Add another bus only when you need a different middleware stack, not because an architecture pattern suggests it." For example `doctrine_transaction` on a command bus but not on a query bus.

Version notes: `readonly` properties exist since PHP 8.1. `forceRetry: false` on `RecoverableMessageHandlingException` requires Symfony 8.1; below 8.1, messages that fail to decode throw `MessageDecodingFailedException` and are silently deleted from the queue.

## Observer

**Intent.** "Lets you define a subscription mechanism to notify multiple objects about any events".

**Use when.**
- Changes to one object may require changing others, and the set of those objects is unknown beforehand or changes dynamically.
- Some objects must observe others, especially for a limited time or in specific cases.

**Pros.** New subscribers need no change to the publisher; relations between objects are established at runtime. **Cons.** Subscribers are notified in random order.

**Already provided.** PHP ships `SplSubject` (`attach()`, `detach()`, `notify()`) and `SplObserver`. Symfony EventDispatcher "maintains a registry of listeners and, when an event is dispatched, it notifies all listeners registered with that event." It implements PSR-14. Doctrine entity events offer lifecycle callbacks (no services, very simple logic), entity listeners (one entity class) and lifecycle listeners (all entities); callbacks are fastest, lifecycle listeners slowest.

- Listener `priority` is an integer defaulting to `0`; higher runs earlier. Internal Symfony listeners usually range from `-256` to `256`. Priority is aggregated across listeners and subscribers; equal priorities run in registration order.
- `stopPropagation()` skips listeners not yet called; `isPropagationStopped()` reports it.
- Subscribers implement `EventSubscriberInterface::getSubscribedEvents()` and are easier to reuse; listeners are more flexible because bundles can enable or disable each one conditionally.

## State

**Intent.** "Lets an object alter its behavior when its internal state changes."

**Use when.**
- An object behaves differently depending on its current state.
- A class is polluted with massive conditionals.
- Much duplicate code exists across similar states and transitions.

**Pros.** State-specific code lives in separate classes; new states need no change to existing states or the context; the context loses bulky state-machine conditionals. **Cons.** Overkill if the state machine has only a few states or rarely changes.

**Related.** "State doesn't restrict dependencies between concrete states, letting them alter the state of the context at will." Strategy does.

**Small machine in plain PHP.** Enums (PHP 8.1) suit modelling states, and an enum method can `match ($this)`. `match` (PHP 8.0) compares strictly, has an implicit break per arm, and throws `UnhandledMatchError` when no arm matches.

```php
enum OrderStatus: string
{
    case New = 'new';
    case Paid = 'paid';
    case Shipped = 'shipped';

    public function canTransitionTo(self $target): bool
    {
        return match ($this) {
            self::New => $target === self::Paid,
            self::Paid => $target === self::Shipped,
            self::Shipped => false,
        };
    }
}
```

**Already provided.** Symfony Workflow (`composer require symfony/workflow`). "Workflows can be in more than one place at the same time, whereas state machines can't". A `workflow` uses a `multiple_state` marking store (array), a `state_machine` a `single_state` one (string).

- `can()`, `apply()`, `getEnabledTransitions()` check and apply transitions; `apply()` throws `LogicException` when not allowed.
- Guard events run on every `can()`, `apply()` and `getEnabledTransitions()`; guards accept expressions such as `"is_granted('ROLE_REVIEWER')"`.
- Each transition dispatches `guard`, `leave`, `transition`, `enter`, `entered`, `completed` and `announce`. Announce can affect performance; disable it with `Workflow::DISABLE_ANNOUNCE_EVENT`.
- `workflow:dump` helps debug the definition.

## Chain of Responsibility

**Intent.** "Lets you pass requests along a chain of handlers". Each handler either handles the request or passes it to the next.

**Use when.**
- The exact types of requests and their sequences are unknown beforehand.
- Several handlers must run in a particular order.
- The set of handlers and their order must change at runtime.

**Pros.** Control over handling order; invokers decoupled from performers (Single Responsibility); new handlers do not break client code (Open/Closed). **Cons.** Some requests may end up unhandled.

**Related.** Decorator has a similar structure, but "decorators aren't allowed to break the flow of the request", while chain handlers can stop it. Handlers can be implemented as Commands.

**Already provided.** Symfony Messenger middleware receives the envelope and is "responsible for calling the next middleware in the chain", so it can add stamps, replace the envelope, or interrupt the chain. Middleware runs on dispatch and again when a worker receives the message. Custom middleware implements `MiddlewareInterface` and runs after the default middleware, before `send_message` and `handle_message`.

## Template Method

**Intent.** "Defines the skeleton of an algorithm in the superclass but lets subclasses override specific steps". The template method calls the steps in a specific order.

**Use when.** Clients should extend only particular steps of an algorithm, not the whole algorithm.

**Pros.** Clients override only certain parts of a large algorithm; duplicate code moves into a superclass. **Cons.** Clients may be limited by the provided skeleton. A subclass suppressing a default step can violate the Liskov Substitution Principle. Template methods get harder to maintain the more steps they have.

**Pitfalls.** Subclasses may override steps but not the template method itself; make it `final`.

**Related.** Strategy is composition-based; Factory Method is a specialization of Template Method.

**Already provided.** Symfony's abstract `Voter` declares `supports()` and `voteOnAttribute()`; `voteOnAttribute()` runs only when `supports()` returns `true`, otherwise the voter abstains. Voters centralize and reuse permission logic; "if you don't reuse permissions or your rules are basic", put the logic in the controller. Symfony 8.1 allows setting voter priority with `#[AsTaggedItem]`.

## Iterator

**Intent.** "Traverse elements of a collection without exposing its underlying representation."

**Use when.**
- The collection has a complex data structure under the hood.
- Traversal code is duplicated across the app.
- Code must traverse different data structures.

**Pros.** Cleaner client code and collections; new collections and iterators can be added; the same collection can be iterated in parallel; iteration can be delayed and resumed. **Cons.** Overkill for simple collections. Less efficient than direct traversal of some specialized collections.

**Already provided.** PHP's `\Iterator` (`rewind()`, `current()`, `key()`, `next()`, `valid()`) for the iterator and `\IteratorAggregate::getIterator()` for the collection.

## Mediator

**Intent.** "Lets you reduce chaotic dependencies between objects."

**Use when.**
- Some classes are hard to change because they are tightly coupled.
- You find yourself creating tons of component subclasses.

**Pros.** Communication lives in one place (Single Responsibility); new mediators need no change to components; less coupling; easier reuse of components. **Cons.** "Over time a mediator can evolve into a God Object."

**Related.** A popular implementation of Mediator relies on Observer. Facade adds no functionality, while Mediator "centralizes communication between components of the system".

**Already provided.** A pure implementation of Mediator is uncommon in PHP; the typical real-world form is a centralized event dispatcher. Symfony EventDispatcher implements Mediator.

## Memento

**Intent.** "Lets you save and restore the previous state of an object without revealing the details of its implementation."

**Use when.**
- Snapshots of the object's state are needed to restore earlier states.
- Direct access to the object's fields, getters or setters would violate its encapsulation.

**Pros.** Snapshots without breaking encapsulation; the caretaker keeps the history, which simplifies the originator. **Cons.** Frequent mementos consume lots of RAM. Caretakers must track the originator's lifecycle to destroy obsolete mementos. Dynamic languages such as PHP cannot guarantee that a memento's state stays unchanged.

**In PHP.** Memento is rarely applicable in PHP; serialization often copies state more simply. Memento pairs with Command for undo and with Iterator for rolling back iteration state. Prototype can sometimes be a simpler alternative.

## Visitor

**Intent.** "Lets you separate algorithms from the objects on which they operate."

**Use when.**
- An operation must run on all elements of a complex object structure.
- Auxiliary behaviors should be moved out of the business logic.
- A behavior makes sense only in some classes of a hierarchy.

**Pros.** New behaviors work with objects of different classes without changing them; several versions of one behavior live in one class; a visitor can accumulate information while working. **Cons.** All visitors must be updated each time an element class is added or removed. Visitors may lack access to private fields and methods of the elements.

**In PHP.** A typical PHP use adds reporting to an existing `Company > Department > Employee` hierarchy; once the infrastructure exists, similar behaviors are added without changing the classes.

## Interpreter

Instead of an Interpreter for configurable rules, use Symfony's ExpressionLanguage, which compiles and evaluates one-line expressions "using a syntax similar to PHP and Twig". It is a good foundation for a business rule engine, letting non-developers configure things without PHP. Symfony uses it in security rules, route conditions, the `Expression` constraint and service container configuration.

- Only explicitly declared variables are available, so expressions are "a very restricted PHP sandbox"; data from end users must still be sanitized.
- `lint()` throws `SyntaxError` for invalid expressions; `IGNORE_UNKNOWN_VARIABLES` and `IGNORE_UNKNOWN_FUNCTIONS` relax the check.

## Sources

- https://refactoring.guru/design-patterns/catalog
- https://refactoring.guru/design-patterns/strategy
- https://refactoring.guru/design-patterns/strategy/php/example
- https://refactoring.guru/design-patterns/command
- https://refactoring.guru/design-patterns/command/php/example
- https://refactoring.guru/design-patterns/observer
- https://refactoring.guru/design-patterns/observer/php/example
- https://refactoring.guru/design-patterns/state
- https://refactoring.guru/design-patterns/chain-of-responsibility
- https://refactoring.guru/design-patterns/chain-of-responsibility/php/example
- https://refactoring.guru/design-patterns/template-method
- https://refactoring.guru/design-patterns/iterator
- https://refactoring.guru/design-patterns/iterator/php/example
- https://refactoring.guru/design-patterns/mediator
- https://refactoring.guru/design-patterns/mediator/php/example
- https://refactoring.guru/design-patterns/memento
- https://refactoring.guru/design-patterns/memento/php/example
- https://refactoring.guru/design-patterns/visitor
- https://refactoring.guru/design-patterns/visitor/php/example
- https://refactoring.guru/replace-conditional-with-polymorphism
- https://symfony.com/doc/current/event_dispatcher.html
- https://symfony.com/doc/current/messenger.html
- https://symfony.com/doc/current/workflow.html
- https://symfony.com/doc/current/components/expression_language.html
- https://symfony.com/doc/current/service_container/tags.html
- https://symfony.com/doc/current/security/voters.html
- https://symfony.com/doc/current/doctrine/events.html
- https://wiki.php.net/rfc/enumerations
- https://wiki.php.net/rfc/match_expression_v2
- https://www.php.net/manual/en/language.oop5.properties.php
