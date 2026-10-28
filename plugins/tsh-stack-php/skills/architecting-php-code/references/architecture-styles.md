# Architecture Styles for PHP Applications

Use this reference when choosing or reviewing the overall structure of a PHP application or module, or when someone proposes hexagonal, CQRS, event sourcing, microservices, or DDD and you must decide whether the cost is earned.

## Table of Contents

- [Starting Point](#starting-point)
- [Styles](#styles)
- [Comparison Table](#comparison-table)
- [Decision Guide: Add Structure on Observed Signal](#decision-guide-add-structure-on-observed-signal)
- [Patterns to Reject](#patterns-to-reject)
- [Review Heuristics](#review-heuristics)
- [Sources](#sources)

## Starting Point

Many systems fit a CRUD mental model and should be built that way. The majority of software systems should be built as a single monolithic application with good modularity inside it; do not consider microservices unless the system is too complex to manage as a monolith. Build a new application as a monolith first, even if it will later benefit from microservices.

Use layering as the default shape: presentation, domain logic, and data access, with the main benefit of reducing the scope of attention. Frameworks often encourage view-model-data as top-level namespaces, which is fine for smaller systems; once a layer gets too big, split the top level into domain-oriented modules that are internally layered.

## Styles

### Layered (Presentation, Domain, Data)

- **Problem.** Separating the layers reduces the scope of attention; that reason is sufficient on its own. It implies no sequence for programming them.
- **Mechanism.** Presentation depends on the domain, the domain depends on the data source. A variation introduces a mapper between the domain and data source layers. A common variation puts a service layer between domain and presentation; more layers do not break the pattern as long as the core separations remain. Layers are logical, not physical tiers.
- **Testability.** Module boundaries expose seams that are good for testing; get as much logic as possible into an easily tested domain layer.
- **When it degrades.** As the application grows, each layer can become complex enough to need further modularisation; then split the top level by domain modules, each internally layered. Apply presentation-domain-data only at a relatively small granularity.
- **Pitfall.** Separating development teams by these layers is an antipattern.
- **Pitfall.** The most common offender in traditional layering is coupling UI and business logic to data access, and transitive dependencies are still dependencies. Data access techniques change at least every three years; this is how legacy systems become stale and are eventually rewritten.

### Hexagonal (Ports and Adapters)

- **Intent.** Let the application be driven equally by users, programs, automated tests, or batch scripts; the application is ignorant of the nature of the input device.
- **Rule.** Code pertaining to the inside must not leak into the outside.
- **Ports and adapters.** A port identifies a purposeful conversation. For each external device an adapter converts the API definition to the signals that device needs. Several adapters can plug into one port.
- **Driving and driven.** A primary actor drives the application; its natural test substitute is FIT. A secondary actor is driven by the application, for answers or notification; the natural test substitute for a database is a mock.
- **Number of ports.** A matter of intuition; many applications have only two. Prefer two, three, or four. The number six is not important.
- **Use cases.** Write them at the application boundary (the inner hexagon); they are shorter, easier to read, cheaper to maintain, and more stable over time.
- **Benefit.** The application can run in a fully isolated mode, keep working when the database is unavailable, and be linked to other applications without user involvement.

### Clean Architecture

- **Properties.** Not dependent on a feature-laden library; business rules testable without UI, database, web server, or other external element; UI changeable without changing the rest; business rules not bound to the database and unaware of the outside world. The shared objective is separation of concerns.
- **Dependency Rule.** Source code dependencies can only point inwards. Nothing in an inner circle can know anything about an outer circle, and data formats used in an outer circle are not used by an inner circle.
- **Circles.** Outer circles are mechanisms, inner circles are policies. Entities encapsulate enterprise-wide business rules; use cases implement all use cases of the system; interface adapters hold presenters, views, and controllers, and nothing inward of them knows about the database; in frameworks and drivers, the web and the database are details. More than four circles may be needed.
- **Crossing boundaries.** Resolve the flow-versus-dependency contradiction with the Dependency Inversion Principle.
- **Data across boundaries.** Simple data structures, never entities or database rows, always in the form most convenient for the inner circle.
- **Outcome.** A system that is intrinsically testable.

### Onion Architecture

- **Mechanism.** The domain model sits at the centre and is coupled only to itself. Only repository interfaces are in the application core; a class implementing them sits at the edge. All code can depend on more central layers, never on layers further out; all coupling is toward the centre, relying heavily on the Dependency Inversion Principle. The database is not the centre; it is external. The outer layer holds things that change often: UI, infrastructure, and tests.
- **Justified.** Long-lived business applications and applications with complex behaviour.
- **Not appropriate.** Small websites.

### CQRS

- **Definition.** A different model to update information than the model used to read it. CQRS builds on the Command and Query Separation Principle.
- **Motivation.** The same conceptual model for commands and queries leads to a more complex model that does neither well.
- **Smells it removes.** Many read methods on repositories with paging or sorting; getters exposing internal state to build DTOs; prefetch paths for read use cases; loading several aggregate roots to build one DTO.
- **Query side.** A thin read layer reads directly from the database and projects DTOs; its developers need to understand only the data model. The domain then focuses on processing commands, and repositories have few query methods beyond `GetById`. The change costs less than or the same as the original architecture, since a responsibility has only moved.
- **Separate stores.** Models may share one database, which acts as their communication channel, or use separate databases, with the query side as a real-time reporting database that needs a communication mechanism. Separate models raise the likelihood of eventual consistency. The choice of integration model matters because translation and synchronisation can become very expensive.
- **Consistency.** Commands are far easier to process with consistent data; most systems can be eventually consistent on the query side.
- **Benefits.** Complex domains (very much the minority case); independent scaling of read and write load; different optimisation strategies per side.
- **Risks.** A significant mental leap for all concerned, so adopt it only when the benefit justifies it. On a domain that does not match it, CQRS adds complexity, reducing productivity and increasing risk. Apply it only to specific portions of a system, such as a bounded context, not the whole system.
- **Alternative.** Demanding queries without a full CQRS domain fit can be offloaded to a reporting database.

### Event-Driven: Name the Pattern

The core problem with "event-driven" is confusing the different patterns. All of them are good in the right place and bad on the wrong terrain.

| Pattern | Pros | Cons and pitfalls |
| --- | --- | --- |
| Event Notification | Low coupling; simple to set up | The flow is not explicit in any program text and often visible only by monitoring a live system; an event used as a passive-aggressive command |
| Event-Carried State Transfer | Lower latency, no remote call to fetch data | Lots of data and copies; more complexity on the receiver, which maintains the state |
| Event Sourcing | Strong audit; historic states by replay | Replay is problematic when results depend on outside systems; event schemas change over time |
| CQRS | In complex domains, one model for reads and writes gets too complicated | Additional complexity of separate models; often misused |

Event processing need not be asynchronous, and CQRS can be used without any events. A system where every change takes twice the work to update read and write models pays a cost that is not a necessary part of either event sourcing or CQRS.

**Symfony Messenger form.**

- By default messages are handled as soon as they are dispatched. A message matching no routing rule is sent to no transport and handled immediately; `'*'` acts as a default routing rule.
- By default a failed message is retried 3 times with a delay, then discarded or sent to the failure transport. Without a `failure_transport` it is discarded. `UnrecoverableMessageHandlingException` stops retries, though the message still reaches the failure transport; `RecoverableMessageHandlingException` retries infinitely, ignoring `max_retries`. Its `forceRetry` argument requires Symfony 8.1 or later.
- A message can be delivered more than once under normal operation; design handlers to be naturally idempotent. Setting an absolute value is safe to repeat; decrementing a counter is not. Otherwise derive an idempotency key from the business data, check it before the operation, and enforce a database uniqueness constraint. A UUID generated at dispatch time is not a suitable key.
- `doctrine_transaction` wraps all handlers in one Doctrine transaction; an error in any handler causes a rollback. Add it to a command bus but not a query bus, since reads do not need the transaction overhead.
- Dispatching from inside a handler: with `DoctrineTransactionMiddleware`, a dispatched message that throws rolls back the original handler's transactions; a message dispatched to a different bus is handled even if later code in the current handler throws. `DispatchAfterCurrentBusStamp` handles the message only if the current handler does not throw. The `dispatch_after_current_bus` middleware is enabled by default, must be registered before `doctrine_transaction`, and must be loaded on all buses used.
- A single bus is a good default. Add another bus only when you need a different middleware stack, not because an architecture pattern suggests it. Without a concrete behavioural difference between buses, one is enough. Command buses usually return no results; query buses are rarely asynchronous.

```php
final class ProcessPayment
{
    public function __construct(
        public readonly int $orderId,
        public readonly string $idempotencyKey,
    ) {
    }
}

#[AsMessageHandler]
final class ProcessPaymentHandler
{
    public function __invoke(ProcessPayment $message): void
    {
        if ($this->paymentRepository->existsByIdempotencyKey($message->idempotencyKey)) {
            return;
        }
    }
}
```

```php
$event = new UserRegistered($command->getUuid());
$this->eventBus->dispatch(
    new Envelope($event)
        ->with(new DispatchAfterCurrentBusStamp())
);
```

### Event Sourcing

- **Definition.** Capture all changes to application state as a sequence of events; both the application state and an event log are persisted, and every change to domain objects is initiated by an event.
- **Benefits.** Complete rebuild by re-running events; temporal query of state at any point in time; event replay, including events received in the wrong sequence; audit log; replaying events in a test environment; an additive event log that needs minimal locking.
- **Justified.** It is the foundation for parallel models and retroactive events (accounting is a typical example). These are very hard to retrofit, so do not leave the decision to later refactoring.
- **Not a natural choice.** Packaging every change as an event is an interface style not everyone is comfortable with.
- **Costs and pitfalls.** Rebuilding from scratch is slow with many events; storing current state or snapshots is faster, and snapshots can be made in parallel without stopping the application. External systems cannot tell replays from real processing, so gateways should be disabled during replay; a gateway can remember responses to external queries. Interactions that both query and update external systems get the worst of both. Reader systems may be out of sync with the master. This can get very messy; do not go down this path unless you really need to.
- **Processing.** Transaction Scripts suit simple logic, a Domain Model more complicated logic. Domain logic should never care about the context in which events run.
- **Aggregates.** An event's version number is unique and sequential only within one aggregate, because aggregate root boundaries are consistency boundaries. Rolling snapshots bound the worst case when loading from events and can be taken asynchronously by a process monitoring the event store.

### Modular Monolith

- **Mechanism.** Design the monolith carefully, with modularity at API boundaries and in how data is stored, so a later split is simpler. Building it modular enough to split later takes a lot of discipline, perhaps too much. Gradual migration works only when the monolith starts with a relatively good modular design.
- **Caveat.** A monolith can have well-defined module boundaries, but in practice they are too easily breached.
- **Enforcement (Deptrac).** A static analysis tool for PHP to communicate, visualise, and enforce architectural decisions: define layers over classes and a communication ruleset. Install with `composer require --dev deptrac/deptrac`, generate a template with `vendor/bin/deptrac init`, configure in `deptrac.php` (YAML or PHP) in the project root, and run `vendor/bin/deptrac`. Use it in CI so a pull request cannot violate the rules. Graphviz or Mermaid.js formatters visualise layers, rules, and violations. It needs at least PHP 8.2 to run, but can analyse projects on older PHP versions that nikic/php-parser can parse.

### Microservices

- **Characteristics.** Services are out-of-process components, independently replaceable and upgradeable, organised around business capability; a team takes full responsibility for its software in production; services are as decoupled and cohesive as possible; applications tolerate the failure of services. Each service manages its own database; consistency may only be eventual, with compensating operations.
- **Benefits.** Independently deployable and scalable services; only modified services need redeploying.
- **Premium.** Automated deployment, monitoring, dealing with failure, eventual consistency; the premium can slow development considerably and often gets projects into serious trouble.
- **Justified.** A system too complex to manage as a monolith. Complexity comes from large teams and, above all, sheer size: a monolith too big to modify and deploy.
- **Drawbacks.** Remote calls cost more and force coarser-grained APIs; naive conversion of in-memory calls to RPC gives chatty communication; refactoring across services is much harder; downtime multiplies; emergent behaviour can be bad; a poor team creates a poor system either way.
- **Premature.** A new project: building microservices from scratch usually ends in serious trouble, and even experienced architects struggle to get boundaries right at the start. Starting with microservices is viable for system replacements, where stable boundaries are found early, and only when the team has reasonable microservice experience.
- **Boundaries.** Services that keep changing together should be merged; parts that change rarely belong in different services. A good in-process interface is usually not a good service interface.
- **Evolution paths.** Peel off services at the edges; replace the monolith entirely; a sacrificial architecture; start with a couple of services larger than the expected final ones. Many systems acquire too many inter-module dependencies to be split, and quick decompositions often end in a mess.

### Strangler Fig (Legacy Migration)

- Big rewrites go down in flames most of the time: replacing a serious system takes long, users cannot wait for features, and much existing behaviour is not really wanted.
- Begin with small additions, often new features, built on top of yet separate from the legacy code base, and move behaviour into the new code base gradually.
- Identify seams that let the system be split; once seams isolate a few components, replace them.
- Activities, in no fixed sequence: understand the outcomes, decide how to break the problem up, deliver the parts, change the organisation so it can continue.
- Transitional architecture (code that goes away once modernisation is complete) is worth its cost because of reduced risk and earlier value.
- Without a change in organisational culture and leadership, the new system ends up in a similar mess.

### Vertical Slices

- **Mechanism.** Build around distinct requests, grouping all concerns from front end to back; remove the barriers across layers. Couple along the axis of change: minimise coupling between slices, maximise coupling in a slice. The system breaks down into command and query requests, so CQRS comes with it.
- **Each slice picks its approach.** Start simple with a Transaction Script and refactor to patterns that emerge from code smells. New features only add code instead of changing shared code.
- **Shared code.** No shared layer abstractions such as repositories, services, or controllers, except where tools require them (controllers, ORM units of work).
- **Prerequisite.** The team understands code smells and refactoring.

### Domain-Driven Design

DDD centres development on programming a domain model and is particularly suited to complex domains; its core notions are conceptual and apply with any programming approach. Strategic design organises large domains into a network of bounded contexts. Its essentials: focus on the core domain; explore models in collaboration between domain and software practitioners; speak a ubiquitous language within an explicitly bounded context.

**Strategic:**

- **Ubiquitous Language.** The model acts as a language for developers and domain experts, embedded in the software. Within one bounded context, fractured language undermines modelling.
- **Bounded Context.** A boundary, typically a subsystem or a team's work, within which a model is defined and applicable. Total unification of a large system's model is not feasible or cost-effective; contexts may have completely different models of common concepts such as "Customer" and "Product", and may split for reasons of history and human relationships.
- **Context Map.** A single bounded context leaves problems without a global view; depict relationships between contexts with a context map.
- **Relationships.** Shared Kernel: sharing part of the model and code is an intimate interdependency that can leverage or undermine design. Customer/Supplier: the upstream team may succeed independently of the downstream team. Conformist: the upstream has no motivation to serve the downstream, which is helpless. Anticorruption Layer: when control or communication cannot support a shared kernel, partner, or customer/supplier relationship, translation becomes complex and defensive.
- **Distillation.** The core domain must be sleek and fully leveraged; justify investment elsewhere by how it supports the core. Factor out generic subdomains that are not the motivation for the project into separate modules.

**Tactical:**

| Building block | Rule |
| --- | --- |
| Entity | A thread of continuity and identity through a lifecycle while attributes change |
| Value Object | Equal by property values; immutable, replaced by a new object instead of changed, with no setters; avoids aliasing bugs. Side-effect-free operations; no identity |
| Aggregate | A cluster treated as one unit with one root; outside references go only to the root, which ensures integrity; load and save whole aggregates; transactions do not cross aggregate boundaries |
| Domain Event | Something happened that domain experts care about |
| Repository | Mediates between domain and data mapping with a collection-like interface; clients submit declarative query specifications; one-way dependency from domain to data mapping; benefits complex domain models with many domain classes or heavy querying |
| Service | A significant domain process that is not a natural responsibility of an entity or value object, as a standalone interface |

## Comparison Table

| Style | Justified when | Not when | Cost signal |
| --- | --- | --- | --- |
| Layered | Default; framework top-level layers fine for smaller systems | Top level of a system whose layers are too big | Transitive coupling to data access |
| Hexagonal | Application driven equally by users, programs, tests, or batch scripts, run in isolation | | Ports and adapters per conversation |
| Clean | Testable core independent of UI, database, and frameworks | | Simple data structures across boundaries |
| Onion | Long-lived business apps, complex behaviour | Small websites | Interfaces in the core, implementations at the edge |
| CQRS | Bounded contexts with complex domains or uneven read/write load | CRUD-shaped domains; the whole system | Two models; eventual consistency |
| Event notification | Low coupling | When the flow must be explicit in code | Hidden flow |
| Event sourcing | Parallel models, retroactive events, audit | | Replay against external systems, schema change |
| Modular monolith | Default before microservices | | Discipline; boundaries breached |
| Microservices | Complexity a monolith cannot manage | New projects; teams without microservice experience | Microservice premium |
| Vertical slices | Teams that understand code smells and refactoring | | Little shared code |
| DDD | Complex domains | | Modelling with domain experts |

## Decision Guide: Add Structure on Observed Signal

| Signal observed | Add |
| --- | --- |
| Getters exposing state for DTOs, many paged and sorted read methods on repositories, prefetch for read use cases | Thin read layer projecting DTOs |
| Read and write loads differ greatly, or one model is too complicated | CQRS in that bounded context |
| Demanding queries in a domain that does not fit CQRS | Reporting database |
| Business logic cannot be tested without UI or database | Ports with test adapters (FIT for primary actors, mocks for the database) |
| Upstream model cannot be shaped through cooperation | Anticorruption Layer |
| Same word means different things in different parts of the system | Separate bounded contexts with a context map |
| Grown application where each layer is too complex | Top-level domain modules, layered inside |
| Module boundaries breached | Enforce layers and rulesets with Deptrac in CI |
| Handler dispatches messages that must not run if it fails | `DispatchAfterCurrentBusStamp` |
| Message may be delivered twice | Idempotent handler with a business-derived key and unique constraint |
| A different middleware stack is needed | A second bus |
| System too complex for a monolith | Extract services, from the edges of the monolith |
| Legacy system needs replacement | Strangler Fig, not a big rewrite |
| Parallel models or retroactive events needed | Event sourcing, decided early |

## Patterns to Reject

- Starting a new project with microservices.
- CQRS applied to the whole system or to domains that do not match it.
- Confusing event-driven patterns, or assuming event sourcing requires asynchronous processing.
- An event used as a passive-aggressive command.
- Shared layer abstractions in vertical slices that tools do not require.
- A second Symfony Messenger bus added because an architecture pattern suggests it rather than because a different middleware stack is needed.
- A UUID generated at dispatch time used as a Messenger idempotency key.
- Passing entities or database rows across clean-architecture boundaries.
- Onion architecture for a small website.
- Development teams separated by presentation, domain, and data layers.
- A big rewrite of a legacy system.
- Transactions that cross aggregate boundaries.

## Review Heuristics

1. Name which event-driven pattern is meant before judging it; each is good in the right place and bad in the wrong one.
2. Check the dependency direction: source code dependencies point inward, toward the domain.
3. For CQRS, confirm the bounded context and whether a shared database suffices before accepting separate stores.
4. For event sourcing, check how replay treats external systems and how event schema changes are handled.
5. For microservices, check that boundaries are stable and that the team has microservice experience to carry the premium.
6. For a modular monolith, check that modularity covers both API boundaries and data storage, and that Deptrac enforces it.
7. For legacy replacement, look for seams and transitional architecture, not a rewrite.

## Sources

- https://martinfowler.com/bliki/CQRS.html
- https://martinfowler.com/bliki/MonolithFirst.html
- https://martinfowler.com/bliki/MicroservicePremium.html
- https://martinfowler.com/articles/microservices.html
- https://martinfowler.com/bliki/StranglerFigApplication.html
- https://martinfowler.com/bliki/BoundedContext.html
- https://martinfowler.com/bliki/DomainDrivenDesign.html
- https://martinfowler.com/bliki/DDD_Aggregate.html
- https://martinfowler.com/bliki/ValueObject.html
- https://martinfowler.com/bliki/PresentationDomainDataLayering.html
- https://martinfowler.com/eaaCatalog/repository.html
- https://martinfowler.com/eaaDev/EventSourcing.html
- https://martinfowler.com/articles/201701-event-driven.html
- https://alistair.cockburn.us/hexagonal-architecture
- https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html
- https://jeffreypalermo.com/2008/07/the-onion-architecture-part-1/
- https://www.jimmybogard.com/vertical-slice-architecture/
- https://cqrs.wordpress.com/wp-content/uploads/2010/11/cqrs_documents.pdf
- https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf
- https://github.com/deptrac/deptrac
- https://symfony.com/doc/current/messenger.html
