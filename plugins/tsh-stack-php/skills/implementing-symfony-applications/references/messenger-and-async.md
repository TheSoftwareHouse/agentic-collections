# Symfony Messenger and Async Components

Use this reference when a task moves work out of the request, schedules recurring jobs, needs mutual exclusion, sends email or notifications, models a status lifecycle, or receives or sends webhooks in a Symfony 5.4 to 8.x application.

## Table of Contents

- [Version gate](#version-gate)
- [Messenger](#messenger)
- [Scheduler](#scheduler)
- [Lock](#lock)
- [Mailer](#mailer)
- [Notifier](#notifier)
- [Workflow](#workflow)
- [Webhook and RemoteEvent](#webhook-and-remoteevent)
- [Sources](#sources)

## Version gate

| Feature | 5.4 | 6.4 | 7.x | 8.x |
| --- | --- | --- | --- | --- |
| Handler registration | `#[AsMessageHandler]` (PHP 8.0+) or `MessageHandlerInterface` | attribute; interfaces deprecated 6.2 | attribute only (interfaces removed 7.0) | attribute only |
| `#[AsMessage]` routing | absent | absent | 7.2 | yes |
| `DeduplicateStamp` | absent | absent | 7.3 | yes |
| `InMemoryTransport` namespace | `Transport\InMemoryTransport` | `Transport\InMemory\` (old deprecated 6.3) | old removed 7.0 | new |
| Scheduler | absent | introduced 6.3; `#[AsCronTask]`, `#[AsPeriodicTask]` 6.4 | yes | yes |
| Workflow | inject by argument name | `Registry` internal 6.2 | `GuardEvent::getContext()` removed 7.0 | `Event::getWorkflow()` removed 8.0 |

## Messenger

- **What it is.** A message bus. Messages are handled as soon as they are dispatched; to handle one asynchronously, configure a transport (`doctrine://`, `redis://`, `amqp://`, Amazon SQS, Beanstalkd, `in-memory://`, `sync://`). A message that matches no routing rule is handled synchronously.
- **When to use.** Handling a message asynchronously through a transport, with per-transport retries (delay, multiplier, jitter) and a failure transport.
- **When NOT to use.** A second bus without a concrete behavioural difference: "A single bus is a good default. Add another bus only when you need a different middleware stack." Repetitive tasks at regular intervals: Messenger cannot do them, use Scheduler.
- **Pros.** Retry strategy, failure transport with `messenger:failed:*` commands, worker limits and `messenger:stop-workers`, `debug:messenger`, `in-memory://` transport for tests.

Pitfalls:

- A message can be delivered more than once. Design handlers to be idempotent; for non-idempotent operations derive a key from the business event (`payment-{orderId}-{orderVersion}`), check it in the handler and enforce a database uniqueness constraint. A UUID generated at dispatch time is not a valid idempotency key.
- Pass the entity ID, not the entity, or you may see Entity Manager errors.
- Keep workers alive with Supervisor or systemd and bound them with `--limit`, `--memory-limit`, `--time-limit`, `--failure-limit`. On deploy run `messenger:stop-workers` after the new code is on disk and the cache is warm, before traffic shifts; on several hosts the app cache needs a shared adapter such as Redis.
- `doctrine_ping_connection` reconnects closed connections for long-running workers; `doctrine_close_connection` closes the connection after handling; `doctrine_transaction` wraps all handlers in one transaction, so handlers need not call `flush()` and any error rolls back. Add `doctrine_transaction` to a command bus, not a query bus.
- When configuring middleware manually, register `dispatch_after_current_bus` before `doctrine_transaction`, and load it on every bus.
- Message classes must be serializable. For a minor change add optional constructor arguments with defaults; for a change of meaning create a new class (`SendInvoiceV2`) and remove the old one after the queue drains.
- A `'*'` routing rule also routes Mailer's `SendEmailMessage`, which breaks when emails are not serializable.
- `UnrecoverableMessageHandlingException` skips retries but the message still reaches the failure transport. `RecoverableMessageHandlingException` retries infinitely and ignores `max_retries`. Without a failure transport, messages are discarded after the retries.
- Long-running messages may be redelivered prematurely; use `--keepalive`. For the Doctrine transport set `redeliver_timeout` (default 3600 s) above the longest message duration.
- Redis: set `delete_after_ack: true` (with a single group) or define `stream_max_entries` to avoid memory leaks.

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
    public function __construct(private readonly PaymentRepository $paymentRepository)
    {
    }

    public function __invoke(ProcessPayment $message): void
    {
        if ($this->paymentRepository->existsByIdempotencyKey($message->idempotencyKey)) {
            return;
        }

        $this->paymentRepository->process($message->orderId, $message->idempotencyKey);
    }
}
```

```yaml
framework:
    messenger:
        failure_transport: failed
        transports:
            async:
                dsn: '%env(MESSENGER_TRANSPORT_DSN)%'
                retry_strategy: { max_retries: 3, delay: 1000, multiplier: 2, max_delay: 10000, jitter: 0.1 }
            failed: 'doctrine://default?queue_name=failed'
        routing:
            App\Message\ProcessPayment: async
```

Stamps: `DelayStamp` (milliseconds), `DispatchAfterCurrentBusStamp` (`(new Envelope($event))->with(new DispatchAfterCurrentBusStamp())` is handled only after the current handler finishes; failures wrapped in `DelayedMessageHandlingException`), `HandledStamp` (handler result via `$envelope->last(HandledStamp::class)`), `TransportNamesStamp` (choose transports at runtime), `DeduplicateStamp` (skips a message whose key is queued or processing; needs the Lock component; TTL default 300 s), `PriorityStamp` (0 to 255, AMQP and Beanstalkd only). Stamps implementing `NonSendableStampInterface` never reach transports.

Versions:

- **5.4**: `#[AsMessageHandler]` recommended on PHP 8.0+, `MessageHandlerInterface` for PHP 7.4. Set `reset_on_message: true`. Transports are separate packages since 5.1 (`symfony/doctrine-messenger`, `symfony/amqp-messenger`, `symfony/redis-messenger`, `symfony/amazon-sqs-messenger`, `symfony/beanstalkd-messenger`). Set Redis `delete_after_ack` explicitly (deprecated otherwise). `StopWorkerException`, `doctrine_open_transaction_logger`.
- **6.0**: AmqpExt transport removed from core, install `symfony/amqp-messenger`; Redis `delete_after_ack` defaults to `true`.
- **6.1**: the container resets automatically between messages; `#[AsMessageHandler]` on methods; `SerializedMessageStamp`.
- **6.2**: handler interfaces deprecated; `TransportNamesStamp`; `messenger:stats`.
- **6.3**: `InMemoryTransport` moves to `Transport\InMemory\`; `stop_worker_on_signals`.
- **6.4**: `messenger:failed:remove --all`; `RunCommandMessage`, `RunProcessMessage`; `StopWorkerOnSignalsListener` deprecated in favour of `SignalableCommandInterface`.
- **7.0**: handler interfaces removed; `HandlerFailedException::getNestedExceptions()` removed, use `getWrappedExceptions()`.
- **7.2**: `#[AsMessage('async')]` (config still wins); `RecoverableMessageHandlingException(retryDelay:)`; `messenger:failed:retry` skip option.
- **7.3**: `DeduplicateStamp` and middleware; `messenger:failed:remove --class-filter`; `SentForRetryStamp`.
- **7.4**: `messenger:consume --exclude-receivers`; `MessageSentToTransportsEvent`.
- **8.0**: `getRetryDelay()` added to `RecoverableExceptionInterface`; `text` format of `messenger:stats` removed.
- **8.1**: `PriorityStamp`; `forceRetry`; `--fetch-size`; `--no-reset=N`; undecodable messages go to the failure transport instead of being deleted.

## Scheduler

- **What it is.** `RecurringMessage`s produced by a schedule and consumed by a Messenger worker on the `scheduler_<name>` transport.
- **When to use.** Recurring automation managed by the application, including dynamic schedules that cron jobs cannot express: maintenance, background processing, periodic data updates, scheduled notifications.
- **When NOT to use.** On 5.4, where the component does not exist.
- **Pros.** Cron and `every()` triggers, `JitterTrigger` to spread load, hashed cron expressions, `debug:scheduler`.

Pitfalls:

- When a worker is down, missed messages are not generated. `stateful($cache)` replays all missed runs; add `processOnlyLastMissedRun(true)` to run once.
- With several workers use `lock()`. It covers the whole schedule: one worker generates messages and the others wait, so more workers give high availability, not throughput.
- Long handlers delay the next messages; redispatch to an async transport.
- Schedule names must be unique. Memoize the schedule. Runtime changes (`add()`, `remove()`) are held in memory and not seen elsewhere until the schedule is rebuilt.
- Cron triggers need `dragonmantank/cron-expression`. `every()` does not support comma-separated weekdays; use cron.

```php
#[AsSchedule('reports')]
final class ReportSchedule implements ScheduleProviderInterface
{
    private ?Schedule $schedule = null;

    public function __construct(
        private readonly CacheInterface $cache,
        private readonly LockFactory $lockFactory,
    ) {
    }

    public function getSchedule(): Schedule
    {
        return $this->schedule ??= (new Schedule())
            ->with(RecurringMessage::cron('0 6 * * *', new SendDailyReport(), new \DateTimeZone('Europe/London')))
            ->stateful($this->cache)
            ->lock($this->lockFactory->createLock('schedule_reports'));
    }
}
```

Run with `php bin/console messenger:consume scheduler_reports`. For a single task, `#[AsCronTask('0 0 * * *', transports: 'async')]` or `#[AsPeriodicTask(frequency: '1 day')]` replaces the provider.

Versions: 6.3 introduced; 6.4 `#[AsCronTask]`, `#[AsPeriodicTask]`, timezone argument on `cron()`, `PreRunEvent`, `PostRunEvent`, `FailureEvent`.

## Lock

- **What it is.** `LockFactory` locks that stop a command running more than once at the same time, on the same or different servers. Expiring (TTL) and shared read locks (`acquireRead()`).
- **When to use.** Exclusive execution across processes and hosts; Scheduler `lock()`; Messenger `DeduplicateStamp`. For a command on one server, `LockableTrait` is enough.
- **Pros.** One API over Flock, Semaphore, Redis, Memcached, PDO, DBAL, PostgreSQL advisory, MongoDB, DynamoDB and ZooKeeper stores.

Pitfalls:

- FlockStore and SemaphoreStore are local to one machine; multiple servers need a shared store.
- Remote locks can be orphaned when a process crashes; use a TTL, release in `finally`, and call `refresh()` in long loops.
- `acquire()` twice on the same `Lock` instance in one process does not block; each service creates its own lock from `LockFactory`.
- `isAcquired()` reports only the current process. Releasing a lock you do not own does nothing and throws nothing.
- Memcached `flush()` or Redis `FLUSHDB` delete locks. Clock drift affects PdoStore, DBAL and MongoDB. `CombinedStore` is at best as reliable as its least reliable store.

```php
$lock = $this->lockFactory->createLock('pdf-creation', ttl: 30);
if (!$lock->acquire()) {
    return;
}

try {
    $this->service->method();
} finally {
    $lock->release();
}
```

Versions: 5.4 named locks in config with autowiring aliases (`$invoiceLockFactory`). 8.1 scopes `flock` and `semaphore` stores by `kernel.project_id`.

## Mailer

- **What it is.** Email over DSN transports (`smtp://`, `sendmail://default`, providers, `failover()`, `roundrobin()`), with `TemplatedEmail`. With Messenger installed, emails are sent asynchronously by default through `SendEmailMessage`.
- **When to use.** Outgoing email; route `SendEmailMessage` to an async transport.
- **When NOT to use.** `MailerInterface` when you need the `SentMessage`: inject `TransportInterface`, which always sends synchronously. `message_bus: false` disables async delivery.

Pitfalls:

- Async messages must be serializable. Replace entities in the template context with simple values, or render first with `BodyRendererInterface`.
- URL-encode DSN credentials with special characters.
- `native://default` gives no error reporting and keeps `Bcc` headers; prefer `sendmail://default`.
- With `null://null` in dev, a message routed to Messenger is still sent to the transport.
- `ping_threshold` for `ses+smtp` with Messenger must be lower than 10.
- In tests use `assertQueuedEmailCount()` with Messenger, and do not follow redirects after sending, or the message is lost.

```php
$this->mailer->send(
    (new TemplatedEmail())
        ->from('hello@example.com')
        ->to($recipient)
        ->subject('Your policy')
        ->htmlTemplate('emails/policy.html.twig')
        ->context(['policyId' => $policyId]),
);
```

Versions: 5.1 `message_bus`; 5.2 `native` transport; 5.4 `ping_threshold` for `ses+smtp`; 8.1 port in `ses+smtp` DSN.

## Notifier

- **What it is.** One API over SMS, chat, email, browser, push and desktop channels, routed by importance through `channel_policy`.
- **When to use.** Notifications sent to several channels, or whose channel depends on importance.

Pitfalls: with Messenger installed, notifications go through the bus and are never sent without a running consumer; set `message_bus: false` to send directly. A `ChatMessage` without `->transport()` goes to the first configured transport. Each channel dispatches its own message, so with a failure transport only the failed channel is retried. Use `null://null` DSNs under `when@dev` and `when@test`.

```yaml
framework:
    notifier:
        channel_policy:
            urgent: ['sms', 'chat/slack', 'email']
            high: ['chat/slack']
            medium: ['browser']
            low: ['browser']
```

Versions: 5.0 introduced; 5.2 `SentMessage`; 5.4 `MessageEvent`, `FailedMessageEvent`, `SentMessageEvent`, Nexmo deprecated for Vonage; 8.1 Prelude SMS bridge.

## Workflow

- **What it is.** A `state_machine` (`single_state` marking store) or a `workflow` (`multiple_state`), configured by `type`, with guards and transition events.
- **When to use.** A `workflow` when an object must be in several places at once; otherwise a `state_machine`.

Pitfalls: Persist a `multiple_state` marking as Doctrine `json`, never `simple_array`. Guard listeners run on every `can()`, `apply()` and `getEnabledTransitions()`; the `announce` event re-runs all guards, so disable it with `Workflow::DISABLE_ANNOUNCE_EVENT` when guards are expensive. `apply()` throws `LogicException` when the transition is not enabled; check `can()` first or catch it. Enum places: `MethodMarkingStore` converts between the enum and its backing value.

```php
public function __construct(
    #[Target('policy_application')]
    private readonly WorkflowInterface $workflow,
) {
}

public function approve(PolicyApplication $application): void
{
    if ($this->workflow->can($application, 'approve')) {
        $this->workflow->apply($application, 'approve');
    }
}
```

A transition can also carry an expression guard in config: `guard: "is_granted('ROLE_REVIEWER')"`.

Versions: on 5.4 inject by argument name (`WorkflowInterface $policyApplicationStateMachine`) and listen with string event names in a subscriber; 5.1 `DISABLE_ANNOUNCE_EVENT`; 5.2 `events_to_dispatch`; 5.4 `$marking->getContext()`. 6.2 `Registry` internal (use a tagged locator) and `setInitialPlaces()` without arguments deprecated. 7.0 `GuardEvent::getContext()` removed. 8.0 `getEnabledTransition()` added to `WorkflowInterface`, `Event::getWorkflow()` removed.

## Webhook and RemoteEvent

- **What it is.** Inbound: a request parser on the `/webhook` endpoint verifies the request and returns a `RemoteEvent` for an `#[AsRemoteEventConsumer]`. Outbound: `SendWebhookMessage` sends JSON with `Webhook-Event`, `Webhook-Id` and an HMAC-SHA256 `Webhook-Signature` (needs `symfony/http-client` and `symfony/serializer`).
- **When to use.** Receiving callbacks, including the built-in Mailer and Notifier provider parsers; sending signed webhooks through Messenger.

Pitfalls: Always set `secret` in production; with an empty secret some parsers skip verification and accept any sender. A custom `AbstractRequestParser::doParse()` must validate the signature and throw `RejectWebhookException` for invalid requests. Consumers run synchronously by default; route `ConsumeRemoteEventMessage` to an async transport. The consumer attribute name must match the routing name.

```php
$config->webhook()
    ->routing('acme_webhook')
    ->service('App\Webhook\AcmeWebhookRequestParser')
    ->secret('%env(WEBHOOK_SECRET)%');

$config->messenger()
    ->routing(ConsumeRemoteEventMessage::class)
    ->senders(['async']);
```

The consumer is a `ConsumerInterface` class with `consume(RemoteEvent $event)` and `#[AsRemoteEventConsumer('acme_webhook')]`.

Versions: 8.0 adds a `$request` argument to `RequestParserInterface::createSuccessfulResponse()`; 8.1 configurable outbound header names and `signing_algorithm`.

## Sources

- https://symfony.com/doc/current/messenger.html
- https://symfony.com/doc/5.4/messenger.html
- https://symfony.com/doc/6.4/messenger.html
- https://symfony.com/doc/7.4/messenger.html
- https://github.com/symfony/symfony/blob/7.4/src/Symfony/Component/Messenger/CHANGELOG.md
- https://symfony.com/doc/current/scheduler.html
- https://symfony.com/doc/6.4/scheduler.html
- https://symfony.com/doc/current/lock.html
- https://symfony.com/doc/5.4/lock.html
- https://symfony.com/doc/current/console/lock.html
- https://symfony.com/doc/current/mailer.html
- https://symfony.com/doc/5.4/mailer.html
- https://symfony.com/doc/current/notifier.html
- https://symfony.com/doc/5.4/notifier.html
- https://symfony.com/doc/current/workflow.html
- https://symfony.com/doc/5.4/workflow.html
- https://symfony.com/doc/current/webhook.html
- https://github.com/symfony/symfony/blob/6.0/UPGRADE-6.0.md
- https://github.com/symfony/symfony/blob/6.2/UPGRADE-6.2.md
- https://github.com/symfony/symfony/blob/6.4/UPGRADE-6.4.md
- https://github.com/symfony/symfony/blob/7.0/UPGRADE-7.0.md
- https://github.com/symfony/symfony/blob/8.0/UPGRADE-8.0.md
