# Doctrine Persistence in Symfony

Use this reference when you map entities, write repository queries, decide where `flush()` belongs, react to persistence events, paginate, write migrations, configure more than one entity manager, or upgrade from Doctrine ORM 2 to ORM 3 in a Symfony 5.4..8.x project.

## Table of Contents

- [Version Baseline](#version-baseline)
- [Entities and Mapping](#entities-and-mapping)
- [Associations](#associations)
- [Repositories and Queries](#repositories-and-queries)
- [Flush and Unit of Work](#flush-and-unit-of-work)
- [Batch Processing](#batch-processing)
- [Pagination](#pagination)
- [Persistence Events](#persistence-events)
- [Entities in Controllers](#entities-in-controllers)
- [Doctrine in Messenger](#doctrine-in-messenger)
- [Migrations](#migrations)
- [Multiple Entity Managers](#multiple-entity-managers)
- [ORM 2 vs 3](#orm-2-vs-3)
- [Sources](#sources)

## Version Baseline

- DoctrineBundle 3.0 requires PHP 8.4, drops `doctrine/dbal` 3 and `doctrine/orm` 2, and drops the YML and annotation metadata drivers.
- DoctrineBundle 3.3.2 requires `php ^8.4`, `doctrine/dbal ^4.0`, Symfony `^6.4 || ^7.0 || ^8.0`, and conflicts with `doctrine/orm <3.0 || >=4.0`.
- ORM 3.0 removes the annotation driver and the YAML drivers. Convert with `php doctrine orm:convert-mapping xml ...`.
- Symfony 7.0 removes the integration of the Doctrine annotations library in favour of native attributes.
- Doctrine recommends upgrading to PHP 8.4 first and then directly from ORM 2.19 to 3.5 and up, so that you skip lazy ghost proxy generation and use native lazy objects.

## Entities and Mapping

**What it is.** An entity is a class whose properties are mapped to columns, usually with `#[ORM\Column(...)]` attributes. XML mapping is the alternative: add `type: xml` and `dir: '%kernel.project_dir%/config/doctrine'` in `config/packages/doctrine.yaml`.

**When to use.** Objects the application saves and fetches through the entity manager.

**When not to use.** Mass inserts, updates or deletions: an ORM is not primarily well-suited for them, and Doctrine recommends the tools of your RDBMS. See [Batch Processing](#batch-processing).

```php
#[ORM\Entity]
#[ORM\Table(name: 'groups')]
class Group
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column]
    private ?int $id = null;

    #[ORM\Column(enumType: Suit::class)]
    private Suit $suit;

    #[ORM\Column(name: 'group_name')]
    private string $name;
}
```

**Pitfalls.**

- Do not use reserved SQL keywords such as `GROUP` or `USER` as table or column names. Rename with `#[ORM\Table(name: 'groups')]` or the `name:` column option.
- Only backed enums work as entity properties, because Doctrine persists their scalar values.
- On MySQL 5.6 and earlier, a `string` column with `unique=true` must set `length` to `190`.
- Storing prices as integers (100 = $1 USD) avoids rounding issues.
- Validation auto mapping derives `NotNull` from `nullable=false` (needs PropertyInfo), `Type` from `type`, `UniqueEntity` from `unique=true` and `Length` from `length`. It does not replace the validation configuration entirely.

**Versions.**

- MakerBundle 1.44.0: `make:entity` supports only entities mapped with PHP attributes. 1.57.0 adds `--with-uuid` and `--with-ulid`.
- Clock types: `date_point` (Symfony 7.3, extends `datetime_immutable`), `day_point` and `time_point` (Symfony 7.4). Without an explicit type, Symfony autodetects `date_point` for a `DatePoint` property. Use `datetime_immutable` when you do not need the Clock component. Example: `#[ORM\Column(type: 'day_point')] public DatePoint $birthday;`.

## Associations

**What it is.** `ManyToOne` and `OneToMany` are one association seen from two sides. `ManyToMany` uses a join table that the ORM manages. `OneToOne` is similar to `ManyToOne`. The "many" side holds the foreign key and is the owning side (`inversedBy`); the "one" side carries `mappedBy`.

```php
#[ORM\OneToMany(targetEntity: Product::class, mappedBy: 'category', orphanRemoval: true)]
private Collection $products;

public function __construct()
{
    $this->products = new ArrayCollection();
}
```

**When to use an inverse side.** Only when you actually need it. The inverse side can be associated with a large number of records, and `$this->products->contains($product)` can trigger unwanted queries and very high memory use.

**Pitfalls.**

- To update a relationship in the database you must set it on the owning side, which is always where the `ManyToOne` is mapped.
- A one-to-many association has to be bidirectional unless you use a join table.
- Initialize `OneToMany` and `ManyToMany` collections in the constructor.
- A new object reachable only through a relationship that is not cascaded throws an exception on flush.
- `orphanRemoval: true` on the `OneToMany` deletes a child from the database when it is removed from the collection.
- Related data is lazily loaded. Avoid the second query with a join: `SELECT p, c FROM App\Entity\Product p INNER JOIN p.category c WHERE p.id = :id`.
- Because of the way the ORM handles removals, database-level constraints may not behave as you would intuitively assume.

**Versions.** From Doctrine 2.9, with typed properties you can omit `targetEntity` on `ManyToOne` and `OneToOne`. In ORM 3 the `OneToOne`, `ManyToOne` and `Index` attributes take `$targetEntity` as the first argument.

## Repositories and Queries

A repository is a class whose only job is to help you fetch entities of one class: `find()`, `findOneBy()`, `findBy()`, `findAll()`, plus your own methods.

- Use the Query Builder when the query is built dynamically from PHP conditions.
- A string passed to `createQuery()` looks like SQL but is DQL.
- Raw SQL returns raw data, not objects, unless you use NativeQuery.

```php
$product = $entityManager
    ->createQuery('SELECT p, c FROM App\Entity\Product p INNER JOIN p.category c WHERE p.id = :id')
    ->setParameter('id', $id)
    ->getOneOrNullResult();
```

**Versions.** ORM 3: custom repository classes must extend `EntityRepository`, and `getRepository()` no longer accepts alias notation (`'App:Product'`); pass `Product::class`.

## Flush and Unit of Work

- `persist()` runs no query. Only `flush()` writes to the database, and Doctrine never calls it implicitly. Unflushed changes are lost.
- An object loaded through Doctrine is already watched; calling `persist()` on it is not necessary.
- `remove()` runs `DELETE` only on `flush()`, and detaches the object from the identity map.
- Do not flush after every change; that is an anti-pattern. A single HTTP request usually needs 0 to 2 flushes.
- Doctrine uses transactional write-behind: a generated identifier is not guaranteed right after `persist()`.
- Before flush, entities scheduled for removal still show up in queries, and newly persisted ones do not.
- Do not pass detached entities to `persist()`; flush throws.
- `clear()` detaches every managed entity. Changes to detached entities are not synchronized.
- Deleting many rows: `CASCADE=REMOVE`, DQL `DELETE` (no hydration) or `onDelete="CASCADE"`. `CASCADE=REMOVE` bypasses the foreign key `onDelete=CASCADE` option.

**Versions.** The Symfony docs say a failed `flush()` throws `Doctrine\ORM\ORMException`; ORM 3 removes that class in favour of dedicated exception classes such as `Exception\EntityManagerClosed`. ORM 3 replaces `transactional()` with `wrapInTransaction()`.

## Batch Processing

**When to use.** Bulk inserts, updates and deletes that must go through the ORM.

- Insert in batches: `flush()` then `clear()` every N items. Larger batches reuse prepared statements more but make each flush heavier.
- Bulk updates and deletes: a DQL `UPDATE` or `DELETE` query is by far the most efficient.
- Iterate large results with `toIterable()` instead of loading everything; detach processed rows.
- `toIterable()` cannot iterate a query that fetch-joins a collection.

**Pitfalls.** An enabled SQL logger seriously affects performance during batches. Combining `toIterable()` with `postLoad` handlers is not safe.

## Pagination

Paginating DQL is not as simple as it looks: the database `LIMIT` is not enough to get correct results when you fetch-join a to-many collection. Doctrine offers two strategies.

- `OffsetPaginator`: random page access. Default `fetchJoinCollection: true` runs three queries (count, id subquery, `WHERE IN`); with `false` it runs two. `true` may affect results with aggregations. For to-one-only joins, set `PaginatorInterface::HINT_ENABLE_DISTINCT` to `false`.
- `CursorPaginator`: large datasets with previous/next navigation. Needs a deterministic `ORDER BY` with at least one item, on columns mapped to entity fields. `$queryProducesDuplicates` defaults to `true`; passing `false` on a to-many join is not detected.
- `getPageCount()` is at least `1`, even for an empty result.

```php
$page = (new OffsetPaginator())->paginate($query, Window::fromPageNumberAndSize(1, 25));
```

**Versions.** ORM 3.7 deprecates `Doctrine\ORM\Tools\Pagination\Paginator` in favour of `OffsetPaginator`. `Paginator::setUseOutputWalkers()` becomes the `useOutputWalkers` constructor argument.

## Persistence Events

| Mechanism | Scope | Services | Use for |
| --- | --- | --- | --- |
| Lifecycle callback (`#[ORM\HasLifecycleCallbacks]` + `#[ORM\PrePersist]`) | Public methods on the entity | No | Very simple logic on one entity |
| Entity listener (`#[AsEntityListener]`) | One entity class | Yes | Complex event logic for one entity |
| Lifecycle listener (`#[AsDoctrineListener]`) | All entities | Yes | Logic shared between entities; check the entity type early |

Lifecycle callbacks are faster than entity listeners, which are faster than lifecycle listeners.

```php
#[AsEntityListener(event: Events::postUpdate, method: 'postUpdate', entity: User::class)]
final class UserChangedNotifier
{
    public function postUpdate(User $user, PostUpdateEventArgs $event): void
    {
    }
}
```

Without attributes, tag the service:

```yaml
services:
    App\EventListener\UserChangedNotifier:
        tags:
            - { name: doctrine.orm.entity_listener, event: postUpdate, entity: App\Entity\User }
```

Lifecycle listeners use the `doctrine.event_listener` tag.

**Pitfalls.**

- Calling `flush()` from event handlers is strongly discouraged. It must not be called in `preFlush` (infinite loop) and cannot be called safely in `postFlush`.
- `preUpdate` does not fire for an empty changeset or a DQL `UPDATE`. Change values only with `setNewValue()`; changes to associations are never allowed there.
- `onFlush`: call `computeChangeSet()` for an entity persisted there and `recomputeSingleEntityChangeSet()` after changing one.
- Changes in `postUpdate`, `postPersist` and `postRemove` are not persisted. Relation changes in `prePersist` are not recognized. `preRemove` does not fire for a DQL `DELETE`.

**Versions.** Symfony 6.3 deprecates Doctrine subscribers in `ContainerAwareEventManager`; 7.0 removes them. Write listeners instead. ORM 3 removes `LifecycleEventArgs`; use `PrePersistEventArgs`, `PostUpdateEventArgs` and the other specific classes, and `getObjectManager()` instead of `getEntityManager()`.

## Entities in Controllers

| Version | Mechanism |
| --- | --- |
| 5.4 | SensioFrameworkExtraBundle ParamConverter. The bundle is no longer maintained and was archived in 2023; it points to native attributes and Symfony 6.2 |
| 6.2+ | `EntityValueResolver` with `#[MapEntity]` (autowiring needs DoctrineBundle 2.7.1) |
| 6.4+ | `request` variable in `MapEntity` expressions |
| 7.1+ | `{slug:product}` route syntax, `message` option, lists via `MapEntity` |
| 7.3+ | Target entity resolution: type-hint an interface |
| 8.0 | Automatic mapping of entities to controller arguments removed: use `#[MapEntity]` or `{param:argument}` |

```php
#[Route('/product/{slug:product}')]
public function show(Product $product): Response
```

A missing entity gives a 404 unless the argument is optional. Options: `id`, `mapping`, `exclude`, `stripNull`, `objectManager`, `evictCache`, `disabled`, `message`, `expr`. `doctrine.orm.controller_resolver.auto_mapping` is no longer recommended.

## Doctrine in Messenger

- Pass the entity's primary key in a message, not the entity, and re-fetch it in the handler for fresh data.
- Middleware: `doctrine_ping_connection` reconnects for long-running workers; `doctrine_close_connection` closes after handling; `doctrine_open_transaction_logger` logs unclosed transactions; `doctrine_transaction` wraps all handlers in one transaction, so handlers need not flush and any error rolls back.
- Register `dispatch_after_current_bus` before `doctrine_transaction`.
- Doctrine transport: `doctrine://<connection_name>`, table `messenger_messages`. In production you may prefer `auto_setup: false`.

## Migrations

**What it is.** DoctrineMigrationsBundle compares your mapping with the database and generates versioned migrations. It replaces `doctrine:schema:update`.

**Workflow.** `make:migration` (or `doctrine:migrations:diff`), then `doctrine:migrations:migrate`. Commit the migration files and run `migrate` on deploy; it runs only migrations not yet executed on that database (tracked in `doctrine_migration_versions`). `doctrine:migrations:up-to-date` tells you whether the schema is current. You should rarely write migrations manually.

**Options.** `transactional: true` wraps each migration in a transaction; `all_or_nothing` runs all migrations in one transaction; `check_database_platform`, `organize_migrations`, `schema_filter`.

**Pitfalls.**

- Tables Doctrine does not manage are marked for removal by `diff`. Exclude them with `schema_filter: ~^(?!t_)~`.
- "The metadata storage is not up to date" points to the server version in the connection string. MariaDB needs the `mariadb-` prefix: `DATABASE_URL=mysql://root:@127.0.0.1:3306/testtest?serverVersion=mariadb-10.4.11`.
- SQLite: "Cannot add a NOT NULL column with default value NULL"; make the column `nullable=true`.
- A schema created with `doctrine:schema:create` needs `doctrine:migrations:version --add --all` to mark migrations as run.

## Multiple Entity Managers

**When to use.** Different databases or vendors with different sets of entities, or one set of entities with separate connections or cache configuration.

**When not to use.** It is advanced and not usually required; make sure you need it before adding the complexity.

**Pitfalls.**

- Entities cannot define associations across entity managers.
- Inject a named manager with `$doctrine->getManager('customer')` or autowire `EntityManagerInterface $customerEntityManager`.
- Migrations and database commands per manager: `doctrine:migrations:diff --em=customer`, `doctrine:migrations:migrate --em=customer`, `doctrine:database:create --connection=customer`.
- An entity managed by more than one manager behaves unexpectedly with `ServiceEntityRepository`, which always uses the configured manager. Extend `EntityRepository` and fetch it through `ManagerRegistry::getRepository()`.

## ORM 2 vs 3

| Change in ORM 3 | Write instead |
| --- | --- |
| Annotation and YAML drivers removed | Attributes or XML |
| `EntityManager::merge()` throws on every call | — |
| `flush()` ignores arguments; `clear()` throws on any argument but `null` | `flush()`, `clear()` |
| Alias notation in `getRepository()` removed | `Product::class` |
| `Query::iterate()` removed | `toIterable()` |
| `transactional()` removed | `wrapInTransaction()` |
| Partial objects (`PARTIAL`, `getPartialReference()`) removed | — |
| `NOTIFY` change tracking removed | `DEFERRED_EXPLICIT` |
| `EntityManager::create()` removed | Public constructor |
| Doctrine Cache removed | PSR-6 |
| Overriding a field of a parent entity (not a mapped superclass) | Throws `MappingException` |

With `doctrine/dbal` 4 the `AUTO` strategy uses `IDENTITY` instead of `SEQUENCE`. To keep sequences on PostgreSQL:

```php
$configuration->setIdentityGenerationPreferences([
    PostgreSQLPlatform::CLASS => ClassMetadata::GENERATOR_TYPE_SEQUENCE,
]);
```

ORM 3.0 enables lazy ghosts unconditionally. ORM 3.5 deprecates not using native lazy objects on PHP 8.4+ (impossible in 4.0); enable them with `$config->enableNativeLazyObjects(true)`. ORM 3.7 deprecates the `JoinColumns` attribute.

## Sources

- https://symfony.com/doc/7.4/doctrine.html
- https://symfony.com/doc/5.4/doctrine.html
- https://symfony.com/doc/8.1/doctrine.html
- https://symfony.com/doc/6.4/doctrine.html
- https://symfony.com/doc/current/doctrine/events.html
- https://symfony.com/doc/current/doctrine/multiple_entity_managers.html
- https://symfony.com/doc/current/doctrine/associations.html
- https://symfony.com/doc/current/messenger.html
- https://symfony.com/doc/current/controller/value_resolver.html
- https://symfony.com/doc/7.4/components/clock.html
- https://symfony.com/bundles/DoctrineMigrationsBundle/current/index.html
- https://github.com/symfony/symfony/blob/6.3/UPGRADE-6.3.md
- https://github.com/symfony/symfony/blob/7.0/UPGRADE-7.0.md
- https://github.com/doctrine/orm/blob/3.0.0/UPGRADE.md
- https://github.com/doctrine/orm/blob/HEAD/UPGRADE.md
- https://raw.githubusercontent.com/doctrine/orm/8840286ffa78184ea1f396a6b9655bd6358087bf/UPGRADE.md
- https://github.com/doctrine/DoctrineBundle/blob/3.0.0/UPGRADE-3.0.md
- https://packagist.org/packages/doctrine/doctrine-bundle
- https://packagist.org/packages/sensio/framework-extra-bundle
- https://github.com/sensiolabs/SensioFrameworkExtraBundle
- https://www.doctrine-project.org/projects/doctrine-orm/en/latest/reference/association-mapping.html
- https://www.doctrine-project.org/projects/doctrine-orm/en/latest/reference/working-with-objects.html
- https://www.doctrine-project.org/projects/doctrine-orm/en/latest/reference/batch-processing.html
- https://www.doctrine-project.org/projects/doctrine-orm/en/latest/reference/events.html
- https://www.doctrine-project.org/projects/doctrine-orm/en/latest/tutorials/pagination.html
