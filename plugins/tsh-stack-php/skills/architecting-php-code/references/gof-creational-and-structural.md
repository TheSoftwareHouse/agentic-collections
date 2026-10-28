# Creational and Structural Design Patterns in PHP

Use this reference when deciding whether to introduce, keep, or remove a creational or structural design pattern in PHP code, and when checking whether PHP or Symfony already provides it.

## Table of Contents

- [Choosing a Pattern](#choosing-a-pattern)
- [Creational Patterns](#creational-patterns)
- [Structural Patterns](#structural-patterns)
- [Quick Decision Table](#quick-decision-table)
- [Sources](#sources)

## Choosing a Pattern

- Creational patterns provide object creation mechanisms that increase flexibility and reuse of existing code. Structural patterns assemble objects and classes into larger structures while keeping them flexible and efficient.
- Many designs start with Factory Method, which is less complicated and more customisable via subclasses, and evolve to Abstract Factory or Builder only when needed.
- Separate the configuration of services from their use. This principle matters more than the choice between Dependency Injection and Service Locator. With a Service Locator every user of a service depends on the locator; with injection, dependencies are visible in constructors or setters. For classes used in multiple applications, Dependency Injection is the better choice.
- Start with constructor injection: it states clearly what a valid object needs and suits immutable fields. Switch to setter injection when constructor problems appear: many parameters, multiple constructors with inheritance, or simple parameters such as strings identified only by position.
- If services cannot be stubbed easily for tests, that points to a serious design problem.

## Creational Patterns

### Factory Method

**Intent.** Provide an interface for creating objects in a superclass, while letting subclasses change the type of object created. Direct constructor calls are replaced with calls to a factory method, which still uses `new` internally.

**Use when.** Your code cannot know the exact object types or dependencies in advance. You want to extend a library or framework's internal components through subclassing. You want to reuse expensive objects, such as connections, from a pool or cache instead of rebuilding them.

**Pros.** Decouples creator from concrete products; product creation in one place (SRP); new product types without breaking client code (OCP).

**Cons.** Adds many new subclasses. Works best when introduced into an existing hierarchy of creator classes.

**Pitfalls.** Products must share a base class or interface, and the factory method must return that type. Early refactoring may leave a large `switch` or need a temporary control parameter. The creator's main job is usually business logic, not product creation.

**PHP note.** PHP supports a single constructor per class; use static methods as constructor wrappers. The constructor may be private or protected to prevent external calls. Constructor promotion requires PHP 8.0. A parent's static factory cannot initialise subclass fields because it returns the parent type.

```php
final class Product
{
    private function __construct(private ?int $id = null, private ?string $name = null)
    {
    }

    public static function fromBasicData(int $id, string $name): static
    {
        return new static($id, $name);
    }
}
```

**Symfony.** A factory is a class or callable whose main purpose is to create and return other objects, for creation logic that should not live in the object itself. Options: a static method (`factory: ['App\Email\NewsletterSenderStaticFactory', 'createNewsletterSender']`), a factory service (`['@App\Email\NewsletterSenderFactory', 'createNewsletterSender']`), an invokable factory service, or an expression (`'@=...'`). In PHP config, first-class callable syntax works (`NewsletterSenderStaticFactory::createNewsletterSender(...)`). When the method is on the created class itself, use `#[Autoconfigure(constructor: 'create')]`, `constructor: 'create'` in YAML, or `factory: [null, 'create']`. Factory arguments are autowired when autowiring is enabled. The configured `class` has no effect on the resulting service, but compiler passes may read it, so set it to a sensible value.

### Abstract Factory

**Intent.** Produce families of related objects without specifying their concrete classes.

**Use when.** Code must work with several families of related products but must not depend on their concrete classes, which may be unknown or extended later. Creating objects through the factory interface should prevent mixing incompatible variants. A class has a set of Factory Methods that blur its primary responsibility; move them into a standalone factory.

**When not to use.** Start with Factory Method and evolve to Abstract Factory only when needed.

**Pros.** Products from one factory are compatible; client not coupled to concrete products; SRP; OCP.

**Cons.** Code can become more complicated than necessary, since many new interfaces and classes are introduced.

Client code depends only on the abstract factory and product types; variants (for example Twig and PHPTemplate) are switched by passing a different factory.

### Builder

**Intent.** Construct complex objects step by step; the same construction code can produce different representations.

**Use when.** You want to avoid a telescoping constructor with many optional parameters. Different representations of a product are needed. You build Composite trees or other complex objects; steps can run recursively. Clients must not get a partially built product.

**When not to use.** The pattern only makes sense when products are quite complex and need extensive configuration. Factory Method is simpler.

**Pros.** Step-by-step, deferred or recursive construction; reuse of construction code; SRP.

**Cons.** Overall complexity increases because the pattern requires several new classes.

**Pitfalls.** The result-fetching method cannot go in the builder interface when products do not share a common interface. Decide whether a builder resets after returning a product or waits for an explicit reset. A Director holding fixed step sequences is optional; the client can call steps directly. Abstract Factory returns a product immediately, Builder allows extra steps first.

**PHP note.** A typical real-world example is an SQL query builder with chainable methods (`select`, `where`, `limit`) that return the builder; a Postgres variant overrides only `limit()`. It uses no Director, because queries vary too much to reuse a fixed sequence.

### Prototype

**Intent.** Copy existing objects without making code dependent on their classes.

**Use when.** Code should not depend on the concrete classes of objects it copies, for example objects received from third-party code through an interface. You want to replace many subclasses that differ only in initialisation by cloning preconfigured prototypes.

**When not to use.** Factory Method is less complicated; Prototype needs complicated initialisation of the cloned object. Memento may be simpler when the object has no external links.

**Pros.** Clone without coupling to concrete classes; no repeated initialisation; complex objects produced more conveniently; an alternative to inheritance for configuration presets.

**Cons.** Cloning complex objects with circular references can be very tricky.

**PHP note.** PHP provides the pattern out of the box with `clone` and `__clone()`.
- `clone` performs a shallow copy; properties that are references stay references, and nested objects are shared. Clone them inside `__clone()` when the copy must not share them. Arrays of objects are not deep-copied automatically.
- A nested object with a back-reference must be re-linked to the clone.
- The constructor does not run during cloning, so setup logic must also go in `__clone()`.
- Cloning inside the class lets it handle private fields.
- Since PHP 8.5, `clone($this, ['x' => $x])` overrides listed properties on the copy after `__clone()` runs, honouring property visibility. Readonly properties can be updated on the copy even if already set on the original.

```php
public function withX(int $x): static
{
    return clone($this, ['x' => $x]);
}
```

### Singleton

**Intent.** Ensure a class has only one instance and provide a global access point to it, through a private constructor and a static creation method that caches the first object.

**Use when.** A single shared resource, such as a database connection, must be available to all parts of a program, or you need stricter control over global variables.

**When not to use.** When tests need mocking or components depend heavily on each other.

**Pros.** One instance guaranteed; global access point; lazy initialisation.

**Cons.**
- Violates SRP: it solves two problems at once.
- Can hide poor design.
- Needs special handling in multithreaded code.
- Hard to unit test, because the private constructor and static methods resist mocking.

**Pitfalls.** The term is often applied to anything global.

**PHP note.** A typical PHP implementation keeps a static `$instances` array keyed by class name, so each subclass gets its own instance, created with `new static()`. It declares `__construct()` and `__clone()` protected and makes `__wakeup()` throw to block unserialising a second instance.

**Symfony.** All container services are shared by default: each retrieval returns the same instance. `shared: false` (or `#[Autoconfigure(shared: false)]`) gives a new instance each time the container is asked, not each time it is used; a service that receives a non-shared service in its constructor keeps that one instance, so inject a service closure to get a new one per call. Non-shared services have a performance cost that grows with their number of dependencies. `shared` is not inherited from parent services.

## Structural Patterns

### Adapter

**Intent.** Let objects with incompatible interfaces collaborate by converting one object's interface so another can use it.

**Use when.** You want to wrap a legacy, third-party or awkward class behind a translator layer. You want to add missing shared functionality to several existing subclasses without duplicating code.

**When not to use.** Sometimes it is simpler to change the service class so that it matches the rest of your code.

**Pros.** Interface and data conversion separated from business logic (SRP); new adapters without breaking clients (OCP).

**Cons.** Overall complexity increases with new interfaces and classes.

**Pitfalls.** A class adapter needs multiple inheritance and fits only languages like C++; in PHP, wrap the adaptee in an object adapter. An adapter usually wraps one object and cannot do recursive composition, which Decorator supports.

### Bridge

**Intent.** Split a large class or set of closely related classes into two hierarchies, abstraction and implementation, developed independently. Composition replaces inheritance.

**Use when.** You want to organise a monolithic class with several variants of functionality, such as different database servers. A class must extend along several independent dimensions. You need to switch implementations at runtime.

**Pros.** Platform-independent classes; clients work with high-level abstractions; OCP; SRP.

**Cons.** Applying it to a highly cohesive class can make the code more complicated.

**Pitfalls.** Often confused with Strategy (similar structure, different intent). The implementation interface need not match the abstraction's. The client links the two, usually via constructor. Bridge is usually designed up front; Adapter makes existing incompatible classes work together.

### Composite

**Intent.** Compose objects into tree structures so clients treat individual objects and groups the same way.

**Use when.** The model is a tree, client code should treat simple and complex elements uniformly, and operations pass down recursively.

**When not to use.** When the model cannot reasonably be expressed as a tree.

**Pros.** Polymorphism and recursion for trees; new element types without breaking existing code (OCP).

**Cons.** A common interface is hard to define when classes differ too much; generalising it makes it harder to understand.

**Pitfalls.** `add()`/`remove()` in the component interface lets clients treat all elements alike but violates the Interface Segregation Principle, since leaves end up with empty methods. Containers should delegate most work to children.

### Decorator

**Intent.** Attach new behaviours to objects by placing them in wrapper objects that implement the same interface as the wrapped object.

**Use when.** You need to assign extra behaviours at runtime without breaking the code that uses the objects. You want to split business logic into layers, one decorator per layer. Extending through inheritance is awkward or impossible, for example for `final` classes.

**Pros.** Extend without a subclass; add or remove responsibilities at runtime; stack several behaviours; SRP.

**Cons.** Hard to remove a specific wrapper from the stack; hard to make behaviour independent of order; layer configuration can look messy. Unlike Chain of Responsibility, decorators should not break the flow of a request.

**Symfony.** Decoration wraps an existing service; redefining a service loses the original, decorating keeps it available to the decorator. The container aliases the decorated ID to the decorator.

```php
#[AsDecorator(decorates: Mailer::class)]
final class LoggingMailer
{
    public function __construct(#[AutowireDecorated] private Mailer $inner)
    {
    }
}
```

- In YAML: `decorates: App\Mailer` with `arguments: ['@.inner']`. The inner ID is the decorator ID plus `.inner`; rename it with `decoration_inner_name`.
- With the default `services.yaml`, the inner service is injected automatically when one constructor argument is type-hinted with the decorated class.
- Tags move from the decorated service to the decorator, except built-in ones such as `kernel.event_subscriber`, `kernel.event_listener` and `kernel.reset`.
- `decoration_priority` (default 0): higher values are applied closer to the original; the lowest priority is outermost and runs first.
- `stack:` defines an ordered chain in one service and by default replaces nothing.
- `decoration_on_invalid`: `exception` (default), `ignore` (decorator removed), or `null` (argument set to null; declare it nullable).
- Symfony 8.1 introduces `#[AsTagDecorator]` / `decorates_tag` (one decorator per tagged service), and `decorates` / `decorates_tag` on stacks.

**Already provided.** Symfony HttpClient decorators: `CachingHttpClient` (RFC 9111 caching on a tag-aware cache), `RetryableHttpClient`, `ScopingHttpClient`, `ThrottlingHttpClient`, `TraceableHttpClient`, `UriTemplateHttpClient`. A custom HttpClient decorator must not call response methods such as `getStatusCode()` inside `request()`, which forces synchronous operation; use `AsyncDecoratorTrait` and `AsyncResponse`.

### Facade

**Intent.** Provide a simplified interface to a library, a framework, or any other complex set of classes.

**Use when.** You need a limited but straightforward interface, and the app needs only a small part of a large library. You want to structure a subsystem into layers, with one facade as the entry point to each layer. Business logic must not depend on third-party implementation details.

**Pros.** Isolates your code from the complexity of a subsystem; replacing or upgrading the framework only changes the facade's methods.

**Cons.** A facade can become a god object coupled to all classes of an app, and offers limited functionality compared with using the subsystem directly.

**Pitfalls.** Extract a refined facade when it grows too big. A facade introduces no new functionality. Clients may bypass it, since subsystem classes are unaware of it.

### Proxy

**Intent.** Provide a substitute or placeholder for another object, with the same interface, that controls access to it so work can run before or after a request reaches it.

**Use when.** Lazy initialisation (virtual proxy), access control (protection proxy), a remote service (remote proxy), logging requests, caching results of recurring requests, or releasing a heavy object when unused (smart reference).

**Pros.** Control the service without clients knowing; manage its lifecycle; works even when the service is not ready; OCP.

**Cons.** More classes; the service's response might be delayed.

**Already provided.**
- Symfony lazy services: the container injects a lazy ghost object with the same signature, which instantiates the real service on first access. Configure with `lazy: true`, `#[Autoconfigure(lazy: true)]`, `#[Lazy]` on the class or a single argument, or `#[Autowire(service: ..., lazy: true)]`. On PHP older than 8.4, `final` and `readonly` classes need a proxy restricted to an interface (`#[Autoconfigure(lazy: ExtensionInterface::class)]`), which allows calling only interface methods. On Symfony 5.4, lazy services require `symfony/proxy-manager-bridge`; without it the `lazy` flag is skipped.
- Service closures and service locators are alternatives to lazy services.
- PHP 8.4 native lazy objects: `ReflectionClass::newLazyGhost()` initialises in place, `newLazyProxy()` forwards to a separate real instance with a distinct identity. Intended uses include DI components providing lazy services and ORMs with lazy entities.

### Flyweight

**Intent.** Fit more objects into available RAM by sharing intrinsic (constant) state; extrinsic, context-specific state is passed by the client.

**Use when.** Only when the program must support a huge number of objects that barely fit into RAM, and the problem cannot be solved another meaningful way. The pattern is merely an optimisation.

**Pros.** Saves lots of RAM when there are tons of similar objects.

**Cons.** May trade RAM for CPU when context data must be recalculated; code becomes much more complicated; the intrinsic/extrinsic split can confuse new team members.

**Pitfalls.** Flyweights must be immutable: state set once via constructor, no setters or public fields. Unlike Singleton, there can be many flyweight instances.

**PHP note.** Rarely useful in PHP, because scripts usually do not load all data into memory at once. A flyweight factory returns an existing instance or creates a new one.

## Quick Decision Table

| Pattern | Use when | Main cost | PHP / Symfony form |
| --- | --- | --- | --- |
| Factory Method | Types unknown beforehand; framework extension point; reuse of instances | Many subclasses | Static creation methods; service `factory` / `constructor` |
| Abstract Factory | Families of related products that must stay compatible | Many interfaces and classes | Factory interface per product family |
| Builder | Telescoping constructor; several representations; Composite trees | Several new classes | Chained builder |
| Prototype | Copy without depending on concrete classes; presets | Circular references | `clone`, `__clone()`, `clone()` with properties (8.5) |
| Singleton | One shared resource for all parts of a program | SRP, hidden design problems, hard tests | Shared container services |
| Adapter | Existing class with incompatible interface | Extra classes; changing the class may be simpler | Object adapter |
| Bridge | Monolithic class with variants; independent dimensions | Complexity for cohesive classes | Abstraction plus implementation hierarchy |
| Composite | Tree structure treated uniformly | Overgeneralised interface | Recursive component |
| Decorator | Extra behaviour at runtime; `final` classes | Order dependence, wrapper removal | `#[AsDecorator]`, `decorates`, HttpClient decorators |
| Facade | Simple interface to a complex subsystem; layers | God object | Entry-point class |
| Proxy | Lazy, guarded, remote, logging, caching access | Delayed responses | Lazy services, PHP 8.4 lazy objects |
| Flyweight | Huge number of objects, RAM exhausted | CPU, complexity | Rare in PHP |

## Sources

- https://refactoring.guru/design-patterns/catalog
- https://refactoring.guru/design-patterns/factory-method
- https://refactoring.guru/design-patterns/factory-method/php/example
- https://refactoring.guru/design-patterns/abstract-factory
- https://refactoring.guru/design-patterns/abstract-factory/php/example
- https://refactoring.guru/design-patterns/builder
- https://refactoring.guru/design-patterns/builder/php/example
- https://refactoring.guru/design-patterns/prototype
- https://refactoring.guru/design-patterns/prototype/php/example
- https://refactoring.guru/design-patterns/singleton
- https://refactoring.guru/design-patterns/singleton/php/example
- https://refactoring.guru/design-patterns/adapter
- https://refactoring.guru/design-patterns/adapter/php/example
- https://refactoring.guru/design-patterns/bridge
- https://refactoring.guru/design-patterns/bridge/php/example
- https://refactoring.guru/design-patterns/composite
- https://refactoring.guru/design-patterns/composite/php/example
- https://refactoring.guru/design-patterns/decorator
- https://refactoring.guru/design-patterns/decorator/php/example
- https://refactoring.guru/design-patterns/facade
- https://refactoring.guru/design-patterns/facade/php/example
- https://refactoring.guru/design-patterns/proxy
- https://refactoring.guru/design-patterns/proxy/php/example
- https://refactoring.guru/design-patterns/flyweight
- https://refactoring.guru/design-patterns/flyweight/php/example
- https://martinfowler.com/articles/injection.html
- https://symfony.com/doc/current/service_container/factories.html
- https://symfony.com/doc/current/service_container/service_decoration.html
- https://symfony.com/doc/current/service_container/lazy_services.html
- https://symfony.com/doc/5.4/service_container/lazy_services.html
- https://symfony.com/doc/current/service_container/shared.html
- https://symfony.com/doc/current/components/http_client.html
- https://www.php.net/manual/en/language.oop5.decon.php
- https://www.php.net/manual/en/language.oop5.cloning.php
- https://www.php.net/manual/en/language.oop5.lazy-objects.php
