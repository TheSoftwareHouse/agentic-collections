# Events and the HTTP Kernel

Use this reference when adding an event listener or subscriber, dispatching a custom event, hooking into the HttpKernel request lifecycle, or choosing which Symfony Contracts package to type-hint, in Symfony 5.4 to 8.x.

## Event Dispatcher

An event is a notification sent when something meaningful happens in an application, such as a user logging in, an order being placed or an error occurring. The EventDispatcher component implements the Mediator and Observer patterns. The dispatcher keeps a registry of listeners and, when an event is dispatched, notifies every listener registered for that event. It implements PSR-14: `EventDispatcherInterface` extends `Psr\EventDispatcher\EventDispatcherInterface`.

- **Use**: to extend an application without changing its existing code; to react to kernel events and events dispatched by third-party bundles; to dispatch custom events from your own code; to add before/after hooks to a method by dispatching an event at its beginning or end.
- **Custom event class**: the recommended way to pass data to listeners. Use the default `Event` class when listeners need no extra data, and `GenericEvent` only for quick prototypes or very simple needs.
- **Injection**: type-hint one of the dispatcher interfaces, not the concrete `EventDispatcher` class. `hasListeners()`, `getListeners()`, `getListenerPriority()`, `removeListener()` and `removeSubscriber()` exist on the component interface but not on the Contracts `EventDispatcherInterface`.
- **Event name**: `dispatch()` takes the event and an optional name. Without a name, the event's FQCN is the event name. `dispatch()` returns the same event object after all listeners have run.
- **Stopping propagation**: a listener can call `$event->stopPropagation()`; listeners not yet called for that event are then not called. `isPropagationStopped()` returns a boolean.
- **Pitfalls**:
  - Priority is aggregated for all listeners and subscribers, so your methods can run before or after methods from other listeners and subscribers.
  - Internal Symfony listeners usually use priorities from `-256` to `256`; check the real order with `debug:event-dispatcher`.
  - `ImmutableEventDispatcher` throws `BadMethodCallException` on any method that modifies it, such as `addListener()`.

```php
use Symfony\Contracts\EventDispatcher\Event;

final class OrderPlacedEvent extends Event
{
    public function __construct(
        private Order $order,
    ) {
    }

    public function getOrder(): Order
    {
        return $this->order;
    }
}
```

```php
namespace App\Service;

use Symfony\Contracts\EventDispatcher\EventDispatcherInterface;

class OrderService
{
    public function __construct(
        private EventDispatcherInterface $dispatcher,
    ) {
    }

    public function place(Order $order): void
    {
        $event = new OrderPlacedEvent($order);
        $this->dispatcher->dispatch($event);
    }
}
```

```bash
php bin/console debug:event-dispatcher
php bin/console debug:event-dispatcher kernel.exception
php bin/console debug:event-dispatcher kernel
php bin/console debug:event-dispatcher --dispatcher=security.event_dispatcher.main
```

Version differences:

- 4.3: the old `Event` class deprecated; 5.0: removed in favour of `Symfony\Contracts\EventDispatcher\Event`.
- 5.0: `dispatch()` signature is `dispatch($event, string $eventName = null): object`.
- 5.3: `debug:event-dispatcher` accepts partial event names and the `--dispatcher` option.
- 5.1: `LegacyEventDispatcherProxy` deprecated; 6.0: removed, use the dispatcher without the proxy.
- 8.1 documentation keeps the 7.4 text for definitions, priorities and propagation.

## Listeners vs Subscribers

A listener is any valid PHP callable registered for an event. A subscriber is a class implementing `EventSubscriberInterface`, whose static `getSubscribedEvents()` declares the events it listens to, so it always knows its events.

- **Choose**: both can be used in the same application; the choice is usually personal taste.
  - Subscribers are easier to reuse, because event knowledge lives in the class, not in the service definition. Symfony uses subscribers internally for this reason.
  - Listeners are more flexible, because bundles can enable or disable each one conditionally from configuration.
- **`#[AsEventListener]`**: configures a listener inside its class with no external configuration. It can be repeated on one class and applied to methods. `event` can be omitted when the method type-hints the event.
- **Registration**: subscribers in `src/EventSubscriber/` are loaded automatically. Without autoconfigure, add the `kernel.event_subscriber` tag; listeners use the `kernel.event_listener` tag.
- **Priority**: an integer defaulting to `0`; higher runs earlier. Same priority runs in registration order. With `addListener()`, priority is the third argument.
- **Pitfalls**:
  - Method resolution for a tagged listener: the `method` attribute, then `on` + PascalCased event name (when `event` is set), then `__invoke()`, otherwise an exception.
  - If subscriber methods are never called, check that services load from the `EventSubscriber` directory and autoconfigure is on.
  - Kernel request listeners must check `isMainRequest()` to skip sub-requests.

```php
#[AsEventListener(event: CustomEvent::class, method: 'onCustomEvent')]
#[AsEventListener(event: 'foo', priority: 42)]
#[AsEventListener(event: 'bar', method: 'onBarEvent')]
final class MyMultiListener
{
}
```

```php
final class ExceptionSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            ExceptionEvent::class => [
                ['processException', 10],
                ['logException', 0],
                ['notifyException', -10],
            ],
        ];
    }
}
```

```yaml
services:
    App\EventListener\ExceptionListener:
        tags: [kernel.event_listener]
```

```php
public function onKernelRequest(RequestEvent $event): void
{
    if (!$event->isMainRequest()) {
        return;
    }
}
```

Version differences:

- 5.3: `#[AsEventListener]` added on classes (PHP 8).
- 5.4: `#[AsEventListener]` allowed on methods.
- 7.4: union types in the `$event` argument of `#[AsEventListener]` methods, e.g. `CustomEvent|AnotherCustomEvent $event`.
- Core events can be referenced by FQCN, e.g. `RequestEvent::class => 'onKernelRequest'`; custom aliases use `AddEventAliasesPass`.

## HttpKernel Lifecycle

`HttpKernel::handle()` defines a lifecycle that starts with a `Request` and ends with a `Response`, and works by dispatching events. Each listener receives one argument, a subclass of `KernelEvent`, which provides `getRequestType()`, `getKernel()`, `getRequest()` and `isMainRequest()`. Symfony has no `preExecute()`/`postExecute()`; use `kernel.controller` and `kernel.response` instead.

| Order | Event (`KernelEvents::`) | Event class | Typical purpose |
| --- | --- | --- | --- |
| 1 | `REQUEST` | `RequestEvent` | Add information to the request, initialise parts of the system, or return a response early (e.g. a security layer denying access); `RouterListener` stores route info here |
| 2 | `CONTROLLER` | `ControllerEvent` | Initialise things or change the controller (`setController()`); read controller attributes (`getAttributes()`) |
| 3 | `CONTROLLER_ARGUMENTS` | `ControllerArgumentsEvent` | Read or replace the controller arguments (`getArguments()`, `setArguments()`) |
| 4 | `VIEW` | `ViewEvent` | Only if the controller did not return a `Response`; turn the return value into one |
| 5 | `RESPONSE` | `ResponseEvent` | Modify the `Response` just before it is sent |
| 6 | `FINISH_REQUEST` | `FinishRequestEvent` | Dispatched after `kernel.response`; reset global state, e.g. the parent request's locale after a sub-request |
| 7 | `TERMINATE` | `TerminateEvent` | Heavy action after the response is sent, such as sending emails; only if the kernel implements `TerminableInterface` |
| any | `EXCEPTION` | `ExceptionEvent` | Turn an exception thrown inside `handle()` into a response |

- **Short-circuit**: setting a response on `kernel.request`, `kernel.view` or `kernel.exception` stops propagation, so lower-priority listeners do not run. A response from `kernel.request` skips straight to `kernel.response`.
- **Sub-requests**: a sub-request usually renders a small portion of a page. Internally the only difference is that some listeners, such as security, act only on the main request.
- **Pitfalls**:
  - A controller must return something; `null` throws immediately. If neither the controller nor a `kernel.view` listener provides a `Response`, an exception is thrown.
  - Early flush before `kernel.terminate` works only with PHP-FPM and FrankenPHP. With other server APIs the response waits for every terminate listener, and changes to the `Response` made in a terminate listener are discarded.
  - With `kernel.debug = true` the response is not finalised before `kernel.terminate`, so terminate listeners may still change it; dev and prod behave differently.
  - `kernel.exception` status code: a client error, server error or redirect status already on your `Response` is kept; otherwise an `HttpExceptionInterface` exception supplies `getStatusCode()` and `getHeaders()`; otherwise 500. To send another status, call `allowCustomResponseCode()` first, and not without a good reason.
  - `ErrorListener` uses status `400` for exceptions implementing `RequestExceptionInterface`. Exceptions extending `HttpException` accept custom headers through `setHeaders()`.
  - In long-running processes, services that accumulate state implement `ResetInterface`; the kernel calls `reset()` after each request/response cycle.

```php
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpKernel\Event\ExceptionEvent;

public function onKernelException(ExceptionEvent $event): void
{
    $exception = $event->getThrowable();
    $response = new Response();
    $event->setResponse($response);
}
```

```php
$event->allowCustomResponseCode();
$response = new Response('No Content', 204);
$event->setResponse($response);
```

```php
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpKernel\HttpKernelInterface;

$request = new Request();
$request->attributes->set('_controller', '...');

$response = $kernel->handle($request, HttpKernelInterface::SUB_REQUEST);
```

Version differences:

- 4.3: `FilterControllerEvent`, `PostResponseEvent` and `GetResponseForExceptionEvent` renamed to `ControllerEvent`, `TerminateEvent` and `ExceptionEvent`; 5.0: old names removed.
- 4.4: `ExceptionEvent::get/setException()` deprecated for `get/setThrowable()`.
- 5.3: `isMainRequest()` and `MAIN_REQUEST` replace `isMasterRequest()` and `MASTER_REQUEST`.
- 6.0: `isMasterRequest()` and `RequestStack::getMasterRequest()` removed; use `isMainRequest()` and `getMainRequest()`.
- 6.2: `ControllerEvent::getAttributes()`; 6.4: optional `$className` parameter.
- 6.3: `#[WithHttpStatus]` and `#[WithLogLevel]` define status codes and log levels on exception classes.
- 7.0: `HttpKernelInterface::MASTER_REQUEST` removed.
- 7.1: `ExceptionEvent::isKernelTerminating()`.
- 7.3: `ServicesResetterInterface`, implemented by `ServicesResetter`.
- 6.0 security events: logout handlers become a `LogoutEvent` listener; `DeauthenticatedEvent` becomes `TokenDeauthenticatedEvent`; `AuthenticationEvents::AUTHENTICATION_FAILURE` becomes `LoginFailureEvent`.

## Contracts

The Contracts component holds abstractions extracted from Symfony components, built on semantics the components proved useful and that have battle-tested implementations. They ship as separate packages: `symfony/cache-contracts`, `symfony/event-dispatcher-contracts`, `symfony/deprecation-contracts`, `symfony/http-client-contracts`, `symfony/service-contracts`, `symfony/translation-contracts`.

- **Use**: type-hint the contract interfaces to reuse any implementation that matches them. Some combine with autowiring; others act as labelling interfaces for autoconfiguration or manual tagging.
- **Design**: split by domain into sub-namespaces; small, consistent sets of interfaces, traits, normative docblocks and reference test suites; a proven implementation is required; backward compatible with existing Symfony components; built on PHP-FIG PSRs when applicable.
- **Event dispatcher contract**: `Symfony\Contracts\EventDispatcher\EventDispatcherInterface` for dispatching; `Symfony\Contracts\EventDispatcher\Event` as the event base class.
- **Pitfall**: the Contracts `EventDispatcherInterface` lacks listener inspection and removal methods; type-hint the component interface when you need them.

A package implementing a contract declares it in `provide`:

```json
{
    "provide": {
        "symfony/cache-implementation": "3.0"
    }
}
```

## Review Checklist

- [ ] Data passes to listeners through a custom event class, not `GenericEvent`, outside prototypes.
- [ ] The dispatcher is injected through an interface, not the concrete `EventDispatcher`.
- [ ] Kernel request listeners check `isMainRequest()`.
- [ ] Listener priority chosen after checking `debug:event-dispatcher`.
- [ ] `stopPropagation()` is intended to skip every later listener.
- [ ] Work in `kernel.terminate` accounts for the server API and the dev/prod difference.
- [ ] Custom success status on `kernel.exception` uses `allowCustomResponseCode()`.
- [ ] Stateful services in long-running processes implement `ResetInterface`.

## Sources

- https://symfony.com/doc/5.4/event_dispatcher.html
- https://symfony.com/doc/7.4/event_dispatcher.html
- https://symfony.com/doc/8.1/event_dispatcher.html
- https://symfony.com/doc/7.4/reference/events.html
- https://symfony.com/doc/7.4/components/http_kernel.html
- https://symfony.com/doc/7.4/components/contracts.html
- https://raw.githubusercontent.com/symfony/symfony/7.4/src/Symfony/Component/HttpKernel/CHANGELOG.md
- https://raw.githubusercontent.com/symfony/symfony/7.4/src/Symfony/Component/EventDispatcher/CHANGELOG.md
- https://raw.githubusercontent.com/symfony/symfony/6.0/UPGRADE-6.0.md
