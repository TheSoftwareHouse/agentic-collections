# Enterprise Application Patterns in PHP

Use this reference when choosing how to organise domain logic, persistence, concurrency, or session state in a PHP application, or when you need to recognise which enterprise application patterns Doctrine ORM, Laravel Eloquent or Symfony already implement.

## Table of Contents

- [Domain Logic](#domain-logic)
- [Anemic Domain Model](#anemic-domain-model)
- [Data Source Patterns](#data-source-patterns)
- [Object-Relational Behaviour](#object-relational-behaviour)
- [Object-Relational Structure and Metadata](#object-relational-structure-and-metadata)
- [Query Object and Repository](#query-object-and-repository)
- [Web Presentation and Distribution](#web-presentation-and-distribution)
- [Concurrency](#concurrency)
- [Session State](#session-state)
- [Base Patterns](#base-patterns)
- [Sources](#sources)

## Domain Logic

| Pattern | What it is | When to use | When not to use |
| --- | --- | --- | --- |
| Transaction Script | Business logic organised by procedures, one per request from the presentation; it calls the database directly or through a thin wrapper | A series of transactions that display data or validate and calculate | — |
| Domain Model | An object model of the domain that carries both behaviour and data; a network of linked objects, each a meaningful entity | Complex business logic with many rules and behavioural cases | A Domain Model is not always the best tool |
| Table Module | One instance handles the business logic for all rows of a table or view; one class per table | — | — |

- Transaction Script: shared subtasks can be split into subprocedures.
- Table Module versus Domain Model: Domain Model has one object per order, Table Module one object for all orders. A Domain Model makes database interaction hard, requiring considerable programmatic gymnastics.

**Service Layer.** Defines an application's boundary with a layer of services: it sets the operations clients can call, encapsulates business logic, controls transactions and coordinates the response in each operation.

- When to use: several interfaces (data loaders, UIs, integration gateways) need the same interactions.
- Pitfall: encoding those interactions separately in each interface duplicates logic.
- With a Domain Model, keep the Service Layer thin so that "key logic lies in the domain layer."

## Anemic Domain Model

Objects named after domain nouns, with relationships, that are "little more than bags of getters and setters"; domain logic sits in separate service objects.

- It is an anti-pattern: an anemic domain model is really just a procedural style design.
- Cons: it carries the costs of a domain model, mainly the O/R mapping layer, without the benefits. "If all your logic is in services, you've robbed yourself blind."
- Remedy: behaviour (validations, calculations, business rules) belongs in domain objects. Layering still applies: domain logic stays separate from persistence and presentation.
- Putting data-source or presentation logic in domain objects is a separate question, orthogonal to anemia.

## Data Source Patterns

**Table Data Gateway.** One object holds all SQL for a single table or view (selects, inserts, updates, deletes); other code calls its methods for every database interaction.

- Pros: SQL in one place for DBAs to tune; developers not comfortable with SQL need not write it; application code reaches the database only through the gateway.

**Row Data Gateway.** An object that acts as a gateway to a single record; one instance per row.

- When to use: business-logic objects should stay free of database code; tests should avoid slow database access; several databases with different SQL dialects.
- Pros: objects match the record structure; data source details hidden; simpler business-logic objects; faster tests; SQL differences handled in one place.

**Active Record.** An object that wraps a row in a table or view, encapsulates the database access, and adds domain logic on that data.

- Pros: everyone knows how to read and write their data to and from the database.
- Laravel Eloquent: each database table has a corresponding "Model" used to interact with that table; this is Active Record, although Eloquent does not use the term.
- Eloquent pitfall, mass assignment: it "occurs when a user passes an unexpected HTTP request field and that field changes a column in your database that you did not expect," for example `is_admin`. Models are protected by default.
  - Declare assignable attributes with `#[Fillable(['name'])]`. With `Unguarded`, "take special care to always hand-craft the arrays passed to Eloquent's `fill`, `create`, and `update` methods."
  - Unfillable attributes are "silently discarded"; call `preventSilentlyDiscardingAttributes` in `AppServiceProvider::boot()` to throw instead.
  - JSON keys must be listed in `Fillable` (`options->enabled`); nested JSON updates are not supported with `Guarded`.

**Data Mapper.** A layer of mappers that moves data between objects and a database while keeping them isolated from each other. Doctrine ORM implements it.

- When to use: the object model has a lot of business logic and uses collections or inheritance, which relational databases lack; object schema and relational schema diverge.
- Pros: domain objects need no SQL and no knowledge of the schema, and do not know the mapper exists; database and object changes do not ripple into each other.
- Cons: transferring data between the two schemas is its own source of complexity.

## Object-Relational Behaviour

**Unit of Work.** Keeps a list of objects affected by a business transaction and coordinates writing out the changes and resolving concurrency problems.

- Problems it solves: changed, new and deleted objects must be tracked; writing on every change means many "very slow" small calls, or a transaction held open across requests, which is "impractical."
- Doctrine ORM: the UnitOfWork is "a typical implementation of the Unit of Work pattern." Interact with the EntityManager, not the UnitOfWork, and avoid its INTERNAL methods.
- `persist()` and `remove()` only notify the UnitOfWork. Only `flush()` writes, and flush is never implicit; changes without a flush are lost.
- `persist()` issues no immediate INSERT (transactional write-behind). Generated identifiers exist only after a successful flush.
- `remove()` issues no immediate DELETE; removed entities still appear in queries and collections until flush.
- Flush commits the current Unit of Work and starts a new one. It updates managed entities only when a persistent field changed and inserts new ones. Its cost grows with the size of the UnitOfWork.
- Pitfall: flushing after every change is an anti-pattern; aim for 0-2 flushes per HTTP request.
- Pitfall: do not pass detached entities to `persist()`; unknown entities are treated as new.
- `EntityManager#close()` loses unpersisted changes.
- Entity states: NEW, MANAGED, REMOVED (until the next flush), DETACHED. Check with `$em->getUnitOfWork()->getEntityState($entity)`.

```php
$user = new User();
$user->setName('Mr.Right');
$em->persist($user);
$em->flush();
```

**Identity Map.** Ensures each object is loaded only once by keeping every loaded object in a map for the business transaction.

- Pros: the same record never becomes "two different objects", so updating both copies cannot conflict on write-back; fewer repeated remote calls.
- Doctrine ORM: within a PHP request, `find()`, repository finders and DQL return the same instance for the same row. Changes in memory are not overwritten by database state.
- `EntityManager#clear()` empties the map and detaches all managed entities; unit tests use it to force reloads.

**Lazy Load.** An object that does not hold all the data it needs but knows how to get it, on first use.

- When to use: loading one object would load many related objects and only a few are needed.
- Variants, which can be combined: Lazy Initialization (marker value, usually null, checked on each access), Virtual Proxy (same interface, first call loads the real object), Value Holder (`getValue()` triggers the load), Ghost (first call loads all fields).
- Cons: each variant has "various trade-offs."
- Doctrine proxies: serialising a proxy does not initialise it; an unserialised proxy is detached and cannot be initialised.

## Object-Relational Structure and Metadata

| Pattern | What it is | When to use / notes |
| --- | --- | --- |
| Identity Field | Database ID stored in the object | Needed to write data back to its row |
| Foreign Key Mapping | Object reference mapped to a foreign key | Collections of references "violate the first normal form" |
| Association Table Mapping | Extra table recording the relationship | Many-to-many; for one-to-many use Foreign Key Mapping |
| Dependent Mapping | Parent's mapper also maps the children | Children loaded and saved with the parent and not referenced by other tables |
| Embedded Value | Object's values mapped to fields of the owner's record | Small objects such as money or date ranges: "no sane person would want a table of money values" |
| Serialized LOB | Object graph saved as one serialized field | Complex graphs of small objects, such as organisation hierarchies, where joins are "slow and awkward" |
| Single Table Inheritance | One table with columns for all classes in the hierarchy | Minimises joins |
| Class Table Inheritance | One table per class | Clear object-to-table mapping |
| Concrete Table Inheritance | One table per concrete class | Each object maps to one row |
| Metadata Mapping | Mapping details held in metadata | Replaces tedious, repetitive hand-written mapping code |

**Doctrine entities.** An entity is a "lightweight, persistent domain object", any regular PHP class with restrictions. Doctrine never calls entity constructors; they run only with `new`. Change detection uses reflection and bypasses getters, setters and the constructor. Entities support inheritance and polymorphic associations and queries; persistent collections are typed `Doctrine\Common\Collections\Collection`. A mapped superclass supplies mapping to subclasses but is not an entity.

**Doctrine embeddables** implement Embedded Value: classes that are not entities, embedded in entities and queryable in DQL. Main use is value objects such as date ranges or addresses.

- Embeddables may contain only properties with basic column mapping; their columns are inlined into the owner's table.
- Column prefix defaults to the property name (`address_street`); set `columnPrefix`, or `columnPrefix: false` to drop it.
- DQL uses dot paths: `u.address.city`.
- Pitfall: when all fields are nullable, initialise the embeddable in the owner's constructor, or the property holds null instead of the object.

```php
#[Entity]
class User
{
    #[Embedded(class: Address::class)]
    private Address $address;
}

#[Embeddable]
class Address
{
    #[Column(type: 'string')]
    private string $street;

    #[Column(type: 'string')]
    private string $city;
}
```

## Query Object and Repository

**Query Object.** An object that represents a database query, written in terms of classes and fields instead of tables and columns, and forms itself into SQL.

- When to use: ad hoc queries that specialised finder methods make difficult; query writers should not need the schema.
- Pros: schema changes stay localised instead of duplicating SQL across finders; SQL complexity hidden.

**Repository.** Mediates between the domain and data mapping layers with a collection-like interface; clients submit declarative query specifications.

- When to use: a complex domain model that already uses a mapping layer such as Data Mapper; many domain classes or heavy querying that would duplicate query construction.
- Pros: query construction in one place; objects added and removed like a collection; clean one-way dependency between domain and data mapping layers.

## Web Presentation and Distribution

- **Model View Controller.** Splits user interface interaction into three roles. Pitfall: it is "one of the most quoted and most misquoted patterns."
- **Page Controller.** One input controller per logical page or action; it can be the page itself or a separate object.
- **Front Controller.** One controller handles all requests. Use for complex sites with many similar per-request tasks (security, internationalisation) or behaviour that changes at runtime. Common behaviour sits in one handler, decorators change it at runtime, and request-specific behaviour goes to command objects.
- **Template View.** Renders HTML by embedding markers in a page. Use for pages that change between requests; not for static pages.
- **Transform View.** Processes domain data element by element into HTML.
- **Two Step View.** First builds a logical presentation, then formats it. Use when many pages need a consistent look, global appearance changes must be easy, or several looks are needed.
- **Application Controller.** Central point for screen navigation and flow. Use for wizard-style or conditional screens when several input controllers would duplicate flow logic; not for simple applications.
- **Remote Facade.** A coarse-grained facade on fine-grained objects, so one call does a whole task; inter-process calls are "orders of magnitude more expensive."
  - Cons: loses fine-grained control and "makes programming harder and slows productivity."
  - Pitfalls: domain logic in the facade (it must hold none); exposing fine-grained objects remotely.
- **Data Transfer Object.** A serializable object carrying data between processes to reduce method calls. Use with expensive remote calls; a server-side assembler maps between DTO and domain objects.
  - Pitfall: do not call DTOs "value objects"; the name clashes with the Value Object pattern.

**Symfony request DTOs.** `#[MapRequestPayload]` maps a POST/PUT request payload directly to a DTO; validation failure returns 422 by default.

```php
public function dashboard(#[MapRequestPayload] UserDto $userDto): Response
{
}
```

- Options: `serializationContext`, `resolver`, `acceptFormat`, `validationGroups`, `validationFailedStatusCode`.
- Arrays: `#[MapRequestPayload(type: UserDto::class)] array $users`; nested DTO arrays need `phpstan/phpdoc-parser` and `phpdocumentor/type-resolver`.
- For JSON APIs, declare the route with `format: 'json'`.
- Symfony 8.1 adds variadic arguments, file mapping for `multipart/form-data`, `mapWhenEmpty`, and validation groups as expressions.

## Concurrency

**Optimistic Offline Lock.** Detects conflicts by validating, before commit, that a session's changes do not clash with another's.

- When to use: "the chance of conflict is low."
- Prevents lost updates and inconsistent reads.
- Pitfall: validation and update must run in one system transaction.
- Doctrine: an integer or datetime field marked `#[Version]`; "Version numbers (not timestamps) should however be preferred." A mismatch at flush throws `OptimisticLockException` and rolls back the transaction.
- Check early with the version the user saw, kept in a hidden form field or session; otherwise lost updates can occur.

```php
#[Version, Column(type: 'integer')]
private int $version;

$em->lock($entity, LockMode::OPTIMISTIC, $expectedVersion);
```

**Pessimistic Offline Lock.** Lets only one business transaction access the data at a time.

- When to use: conflicts are likely, transactions are long, or optimistic locking keeps failing late and wasting work. Try optimistic first.
- Cons: "transaction systems are not built for long transactions"; several system transactions leave concurrency to the developer.
- Doctrine delegates to database locks: `LockMode::PESSIMISTIC_WRITE` blocks concurrent reads and writes, `PESSIMISTIC_READ` blocks updates and write locks. Use via `find()`, `lock()`, `refresh()` or `Query#setLockMode()`, inside an explicit transaction with auto-commit disabled, otherwise Doctrine throws.

**Coarse-Grained Lock.** One lock for a set of related objects edited as a group, such as a customer and its addresses. Pros: no need to load every member to lock it; less lock-table contention.

**Implicit Lock.** Framework or layer supertype code acquires the locks. Pitfalls it prevents: one missed lock breaks the scheme; missing read locks; mishandled version counts silently overwrite changes; unreleased locks.

**Doctrine transactions.** A bare `flush()` wraps queued writes in its own transaction. Use explicit demarcation for custom DBAL work or methods that throw `TransactionRequiredException`. `wrapInTransaction()` flushes before commit and closes the EntityManager on exception. After an exception: roll back, close and discard the EntityManager. Entities become detached and their in-memory state is not rolled back.

## Session State

- **Client Session State.** Stores session state on the client.
- **Server Session State.** Keeps session state on a server in serialized form.
- **Database Session State.** Stores session data as committed data in the database.

## Base Patterns

| Pattern | What it is | When to use / notes |
| --- | --- | --- |
| Gateway | Wraps access to an external system behind a regular object interface | External resources with specialised APIs that may change |
| Service Stub | Local, fast, in-memory stand-in for a problematic service | Tests that depend on slow or unreliable third-party services |
| Record Set | In-memory tabular data matching an SQL result | Data-aware UI frameworks; a home for business logic outside database and UI code |
| Mapper | Sets up communication between two independent objects | Subsystems that must stay ignorant of each other or cannot be modified |
| Layer Supertype | Supertype for all types in a layer | Methods "you don't want to have duplicated throughout the system" |
| Separated Interface | Interface in one package, implementation in another | Keeps package dependency rules; plug point for Gateway |
| Registry | Well-known object for finding common objects and services | No object to navigate from. Con: "essentially a global object" |
| Value Object | Small object, like money or a date range, compared by value, not identity | — |
| Money | Monetary value handling currency and rounding | Several currencies; rounding to the smallest unit. Base libraries usually lack it |
| Special Case | Subclass with special behaviour returned instead of null | Removes repeated null checks; keeps polymorphism |
| Plugin | Links classes at configuration time | Different implementations per environment, without rebuild or redeploy |

## Sources

- https://martinfowler.com/eaaCatalog/
- https://martinfowler.com/eaaCatalog/transactionScript.html
- https://martinfowler.com/eaaCatalog/domainModel.html
- https://martinfowler.com/eaaCatalog/tableModule.html
- https://martinfowler.com/eaaCatalog/serviceLayer.html
- https://martinfowler.com/bliki/AnemicDomainModel.html
- https://martinfowler.com/eaaCatalog/tableDataGateway.html
- https://martinfowler.com/eaaCatalog/rowDataGateway.html
- https://martinfowler.com/eaaCatalog/activeRecord.html
- https://martinfowler.com/eaaCatalog/dataMapper.html
- https://martinfowler.com/eaaCatalog/unitOfWork.html
- https://martinfowler.com/eaaCatalog/identityMap.html
- https://martinfowler.com/eaaCatalog/lazyLoad.html
- https://martinfowler.com/eaaCatalog/identityField.html
- https://martinfowler.com/eaaCatalog/foreignKeyMapping.html
- https://martinfowler.com/eaaCatalog/associationTableMapping.html
- https://martinfowler.com/eaaCatalog/dependentMapping.html
- https://martinfowler.com/eaaCatalog/embeddedValue.html
- https://martinfowler.com/eaaCatalog/serializedLOB.html
- https://martinfowler.com/eaaCatalog/singleTableInheritance.html
- https://martinfowler.com/eaaCatalog/classTableInheritance.html
- https://martinfowler.com/eaaCatalog/concreteTableInheritance.html
- https://martinfowler.com/eaaCatalog/metadataMapping.html
- https://martinfowler.com/eaaCatalog/queryObject.html
- https://martinfowler.com/eaaCatalog/repository.html
- https://martinfowler.com/eaaCatalog/modelViewController.html
- https://martinfowler.com/eaaCatalog/pageController.html
- https://martinfowler.com/eaaCatalog/frontController.html
- https://martinfowler.com/eaaCatalog/templateView.html
- https://martinfowler.com/eaaCatalog/transformView.html
- https://martinfowler.com/eaaCatalog/twoStepView.html
- https://martinfowler.com/eaaCatalog/applicationController.html
- https://martinfowler.com/eaaCatalog/remoteFacade.html
- https://martinfowler.com/eaaCatalog/dataTransferObject.html
- https://martinfowler.com/eaaCatalog/optimisticOfflineLock.html
- https://martinfowler.com/eaaCatalog/pessimisticOfflineLock.html
- https://martinfowler.com/eaaCatalog/coarseGrainedLock.html
- https://martinfowler.com/eaaCatalog/implicitLock.html
- https://martinfowler.com/eaaCatalog/clientSessionState.html
- https://martinfowler.com/eaaCatalog/serverSessionState.html
- https://martinfowler.com/eaaCatalog/databaseSessionState.html
- https://martinfowler.com/eaaCatalog/gateway.html
- https://martinfowler.com/eaaCatalog/serviceStub.html
- https://martinfowler.com/eaaCatalog/recordSet.html
- https://martinfowler.com/eaaCatalog/mapper.html
- https://martinfowler.com/eaaCatalog/layerSupertype.html
- https://martinfowler.com/eaaCatalog/separatedInterface.html
- https://martinfowler.com/eaaCatalog/registry.html
- https://martinfowler.com/eaaCatalog/valueObject.html
- https://martinfowler.com/eaaCatalog/money.html
- https://martinfowler.com/eaaCatalog/specialCase.html
- https://martinfowler.com/eaaCatalog/plugin.html
- https://www.doctrine-project.org/projects/doctrine-orm/en/current/reference/working-with-objects.html
- https://www.doctrine-project.org/projects/doctrine-orm/en/current/reference/transactions-and-concurrency.html
- https://www.doctrine-project.org/projects/doctrine-orm/en/current/reference/architecture.html
- https://www.doctrine-project.org/projects/doctrine-orm/en/current/tutorials/embeddables.html
- https://laravel.com/docs/eloquent
- https://symfony.com/doc/current/controller.html
