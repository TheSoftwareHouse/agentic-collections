# Symfony Console, HttpClient and Operations

Use this reference when a task adds or changes a console command, calls a remote HTTP API, writes logs, prepares a production deployment, tunes performance, or sets HTTP cache headers in a Symfony 5.4 to 8.x application.

## Table of Contents

- [Version gate](#version-gate)
- [Console commands](#console-commands)
- [HttpClient](#httpclient)
- [Logging](#logging)
- [Deployment](#deployment)
- [Performance](#performance)
- [HTTP cache](#http-cache)
- [Sources](#sources)

## Version gate

| Feature | Version |
| --- | --- |
| `#[AsCommand]`, `$defaultDescription` | added 5.3 |
| `Command::SUCCESS`, `Command::FAILURE` / `Command::INVALID` | 5.1 / 5.3 |
| `assertCommandIsSuccessful()`, Bash completion | 5.4 |
| `$defaultName`, `$defaultDescription` | deprecated 6.1, removed 7.0 |
| `getDefaultName()`, `getDefaultDescription()` | deprecated 7.3, removed 8.0 |
| `#[AsCommand]` class | `@final` 7.3, `final` 8.0 |
| `Application::add()` | removed 8.0, use `addCommand()` |
| `setLogger()` on HttpClient decorators | removed 8.0 |
| `NotFoundActivationStrategy` | removed 8.0, use `HttpCodeActivationStrategy` |
| XML configuration format | not supported in 8.0 |
| PHP requirement of Symfony 8 | PHP 8.4 or higher |

## Console commands

- **What it is.** A command class registered automatically through `#[AsCommand]`, or as a service tagged `console.command` without attributes. The body is `execute()` or, in the current docs, `__invoke()`, and it returns the exit status.
- **Lifecycle.** `initialize()` runs before `interact()` and `execute()`; `interact()` is not called with `--no-interaction`.
- **Exit codes.** `execute()` "must return an integer which will be used as the command exit status": `Command::SUCCESS` (0), `Command::FAILURE` (1), `Command::INVALID` (2, "incorrect usage, e.g. invalid options or missing arguments").
- **Pros.** "Commands are loaded lazily: their classes are only instantiated when the command is run", because the name is read from `#[AsCommand]` without instantiating the class. A description in `#[AsCommand]` instead of `setDescription()` lets `list` read it without instantiating the class.

Pitfalls:

- Running `list` "instantiates all commands, including lazy ones", except `LazyCommand` instances whose factory is not executed. `list`, `help` and `_complete` can require instantiating other commands.
- `CommandTester` does not dispatch console events; use `ApplicationTester` and call `$application->setAutoExit(false)` first, otherwise the application calls `exit()`.
- Console events fire only for the main command; commands called by it trigger none "unless run by the application itself".
- "Symfony doesn't handle any signal received by the command (not even SIGKILL, SIGTERM, etc)." Implement `SignalableCommandInterface` with `getSubscribedSignals()` and `handleSignal()`.
- `setAlarmInterval()` and `ConsoleAlarmEvent` require `pcntl` and are not available on Windows.
- `LockableTrait` exists "to prevent the same command from running multiple times on the same server." If the lock is not released explicitly, Symfony releases it when the command ends.
- For a single-command application, call `setAutoExit(false)` to get the result in `CommandTester` (5.2).
- With method-based commands (8.1), method names must be relative to the class-level prefix; using the full name throws an exception.

Classic style with `execute()`:

```php
#[AsCommand(
    name: 'app:create-user',
    description: 'Creates a new user.',
    hidden: false,
    aliases: ['app:add-user']
)]
class CreateUserCommand extends Command
{
    protected function configure(): void
    {
        $this->addArgument('username', InputArgument::REQUIRED, 'The username of the user.');
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $output->writeln($input->getArgument('username'));

        return Command::SUCCESS;
    }
}
```

Invokable style, as shown in the current (8.1) docs:

```php
#[AsCommand(name: 'app:create-user')]
class CreateUserCommand
{
    public function __invoke(
        #[Argument('The username of the user.')] string $username,
        OutputInterface $output,
    ): int {
        return Command::SUCCESS;
    }
}
```

Lock against parallel runs on one server:

```php
class UpdateContentsCommand extends Command
{
    use LockableTrait;

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        if (!$this->lock()) {
            $output->writeln('The command is already running in another process.');

            return Command::SUCCESS;
        }

        $this->release();

        return Command::SUCCESS;
    }
}
```

Testing:

```php
$command = $application->find('app:create-user');
$commandTester = new CommandTester($command);
$commandTester->execute(['username' => 'Wouter']);
$commandTester->assertCommandIsSuccessful();
```

Versions:

- **5.4**: the docs show `protected static $defaultName = 'app:create-user';` and `#[AsCommand]` with `name`, `description`, `hidden`, `aliases` replacing it.
- **6.1**: `$defaultName` and `$defaultDescription` deprecated.
- **7.0**: both removed; Messenger's `StopWorkerOnSigtermSignalListener` removed in favour of `SignalableCommandInterface`.
- **7.3**: `getDefaultName()` and `getDefaultDescription()` deprecated; `#[AsCommand]` marked `@final`; omitting parameter types or returning a non-integer from a closure passed to `Command::setCode()` deprecated.
- **8.0**: `getDefaultName()`, `getDefaultDescription()` and `Application::add()` removed (use `addCommand()`); `AsCommand` is `final`.
- **8.1**: method-based commands; `runCommand()` and `ExecutionResult` in `KernelTestCase` with `assertCommandIsSuccessful`, `assertCommandFailed`, `assertCommandIsInvalid`; overriding `Bundle::registerCommands()` deprecated.
- Current docs also accept aliases as `#[AsCommand(name: 'app:create-user|app:add-user|app:new-user')]`.

## HttpClient

- **What it is.** An HTTP client with lazy responses, scoped clients, retries, mocks and decorators; `Psr18Client` adapts `HttpClientInterface` to PSR-18 `ClientInterface`.
- **Scoped clients.** "Options apply only to URLs matching the `scope` regex." Each scoped client gets a service named after its config and a named autowiring alias. Options passed to `request()` override scoped defaults.
- **Decorators.** `RetryableHttpClient` (`retry_failed`), `ThrottlingHttpClient` (rate limits via `LimiterInterface` from the Rate Limiter component), `CachingHttpClient`, `NoPrivateNetworkHttpClient`, `UriTemplateHttpClient` (all framework clients are decorated by it by default).
- **When to use `NoPrivateNetworkHttpClient`.** "If you use an HttpClient together with user-provided URIs, it is probably a good idea to decorate it with a NoPrivateNetworkHttpClient."

Pitfalls:

- The request starts immediately; `getHeaders()` blocks until headers arrive, `getContent()` until the full body arrives.
- For status codes 300 to 599, `getHeaders()`, `getContent()` and `toArray()` throw `HttpExceptionInterface`; pass `false` to opt out. If none is called, the exception is thrown when the response is destructed.
- "Calling `$response->getStatusCode()` is enough to disable this behavior (but then don't miss checking the status code yourself)."
- Other exceptions: `TransportExceptionInterface`, `DecodingExceptionInterface`.
- `timeout` is idle time; `max_duration` limits "the time a full request/response can last."
- `retry_failed` defaults to up to 3 retries with exponential delay. Codes 423, 425, 429, 502, 503 are retried for any method; 500, 504, 507, 510 for idempotent methods only. `max_retries` sets the count.
- `CachingHttpClient` stores a response only after it is fully consumed.

```yaml
framework:
    http_client:
        scoped_clients:
            github:
                base_uri: 'https://api.github.com'
                headers:
                    Accept: 'application/vnd.github.v3+json'
                    Authorization: 'token %env(GITHUB_API_TOKEN)%'
```

```php
final class GithubGateway
{
    public function __construct(
        #[Target('github')] private HttpClientInterface $githubClient,
    ) {
    }
}
```

Testing: `MockHttpClient` takes a list of `MockResponse` returned in order, `MockResponse::fromFile(...)`, or a callback for dynamic responses. It implements `HttpClientInterface`, so code type-hinted with the interface uses the real client in production and the mock in tests.

Versions: 7.0 removes implementing `Http\Message\RequestFactory` from `HttplugClient`. 8.0 removes `setLogger()` on decorators (configure the logger on the wrapped client) and passing a `StoreInterface` as `$cache` to `CachingHttpClient`. 8.1 adds `max_connect_duration`, the `$allowList` argument of `NoPrivateNetworkHttpClient`, `GuzzleHttpHandler`, `DnsResolvingHttpClient`, persistent cURL connections (PHP 8.5+), and deprecates `max_ttl: null` on `CachingHttpClient`.

## Logging

- **What it is.** PSR-3 `Psr\Log\LoggerInterface` backed by Monolog handlers (`stream`, `rotating_file` with `max_files`, `syslog` and others) and channels (`app`, `doctrine`, `event`, `security`, `request`, ...), each with a `monolog.logger.XXX` service.
- **When to use placeholders.** `$logger->debug('User {userId} has logged in', ['userId' => $id])`. Placeholders help grouping and translation and are "better for security, because escaping can then be done by the implementation in a context-aware fashion."
- **Storage.** Dev writes `var/log/dev.log`. Prod logs go to STDERR, "which works best in modern containerized applications deployed to servers without disk write permissions"; set `path` to store them in a file.

Pitfalls:

- `fingers_crossed` is the prod default. It "stores all log messages during a request but only passes them to a second handler if one of the messages reaches an `action_level`."
- A handler nested in `fingers_crossed` is not part of the stack itself.
- "The `channels` configuration only works for top-level handlers"; nested handlers in group, buffer, filter and fingers crossed ignore it.
- Long-running processes: call `reset()` on the Monolog Logger "between every job or task that a long-running process is working through."
- `SHELL_VERBOSITY` sets the minimum level for built-in loggers (-1 ERROR, 1 NOTICE, 2 INFO, 3 DEBUG); they send WARNING and above to stderr.

```yaml
monolog:
    channels: ['foo', 'bar', 'foo_bar']
    handlers:
        filter_for_errors:
            type: fingers_crossed
            action_level: error
            handler: file_log
        file_log:
            type: stream
            path: "%kernel.logs_dir%/%kernel.environment%.log"
```

```php
final class FixturesLoader
{
    public function __construct(
        #[Target('foo_bar')] private LoggerInterface $logger,
    ) {
    }
}
```

Versions: MonologBundle 3.5 autowires channel loggers by argument name (`LoggerInterface $fooBarLogger` for `foo_bar`); the channel must be predefined. Current docs use `#[Target('foo_bar')]`. `#[WithMonologChannel]` on the class needs Monolog 3.5; on constructor arguments, MonologBundle 4.1. Handler `enabled: false` needs Monolog 3.11.0. 6.0 removes `ResetLoggersWorkerSubscriber` in favour of Messenger's `reset_on_message` option. 7.0 drops Monolog < 3.0. 8.0 removes `NotFoundActivationStrategy`; use `HttpCodeActivationStrategy`.

## Deployment

- **What it is.** The steps that turn a checkout into a running prod release.

Checklist:

1. Set real env vars or create `.env.prod.local`; "There is no significant advantage to either option." Optionally run `composer dump-env prod` to generate `.env.local.php`, which "overrides all other configuration files".
2. `composer install --no-dev --optimize-autoloader`. On a class-not-found error, `export APP_ENV=prod`.
3. `APP_ENV=prod APP_DEBUG=0 php bin/console cache:clear`.
4. Run database migrations, clear the APCu cache, update cron jobs, build assets.
5. `php bin/console messenger:stop-workers` "after the new code is on disk and the cache is warmed up, but before traffic shifts." On several hosts, configure the app cache with a shared adapter such as Redis.
6. Empty and regenerate OPcache.

Pitfalls: `composer require symfony/requirements-checker` checks the server. Without Composer on the server, use the `dotenv:dump` command. "Symfony v8 requires PHP v8.4 or higher."

## Performance

- **What it is.** PHP and Composer settings for production.

```ini
opcache.memory_consumption=256
opcache.max_accelerated_files=32531
opcache.interned_strings_buffer=32
opcache.validate_timestamps=0
opcache.preload=/path/to/project/config/preload.php
opcache.preload_user=www-data
realpath_cache_size=4096K
realpath_cache_ttl=600
```

Checklist: `composer dump-autoload --no-dev --classmap-authoritative` during deployment; `framework.enabled_locales` to generate only used translation files; parameter `.container.dumper.inline_factories: true`; tags `container.preload` and `container.no_preload` select preloaded classes. If `config/preload.php` is missing, run `composer recipes:update symfony/framework-bundle`.

Pitfalls:

- "After each deployment, you must empty and regenerate the OPcache." "The CLI and web processes don't share the same OPcache": restart the web server, call `opcache_reset()` through it, or use cachetool.
- "PHP disables the realpath cache when the open_basedir config option is enabled."
- `--classmap-authoritative` "prevents Composer from scanning the file system for classes that are not found in the class map."

## HTTP cache

- **What it is.** Expiration caching (`Cache-Control`, `Expires`) or validation caching (`ETag`, `Last-Modified`). `framework.http_cache: true` under `when@prod` enables the Symfony reverse proxy; debug mode adds `X-Symfony-Cache`; `trace_level` is none, short or full.
- **When to use.** "HTTP caching only works for 'safe' HTTP methods (GET, HEAD and QUERY)." POST can be cached only with explicit freshness information.
- **When not to use.** "Whenever the session is started during a request, Symfony turns the response into a private non-cacheable response." Opt out with `AbstractSessionListener::NO_AUTO_CACHE_CONTROL_HEADER`.
- **Cons.** Expiration is "Simple, but cache invalidation is more difficult"; it does not support invalidation.

Pitfalls: headers set in the controller take precedence over `#[Cache]`. The URI is the cache key unless you vary. `$response->expire()` marks the response stale; `$response->setNotModified()` forces a 304 without content.

```php
use Symfony\Component\HttpKernel\Attribute\Cache;

#[Cache(public: true, maxage: 3600, mustRevalidate: true)]
public function index(): Response
{
    return $this->render('index.html.twig');
}
```

`setCache()` accepts `public`, `private`, `max_age`, `s_maxage`, `must_revalidate`, `immutable`, `etag`, `last_modified`; all are available on `#[Cache]`.

Versions: 7.0 removes the `terminate_on_cache_hit` option from `HttpCache`.

## Sources

- https://symfony.com/doc/5.4/console.html
- https://symfony.com/doc/current/console.html
- https://symfony.com/doc/6.4/console.html
- https://symfony.com/doc/current/components/console/events.html
- https://symfony.com/doc/current/console/lazy_commands.html
- https://symfony.com/doc/5.4/console/lockable_trait.html
- https://github.com/symfony/symfony/blob/6.4/src/Symfony/Component/Console/CHANGELOG.md
- https://symfony.com/doc/current/http_client.html
- https://symfony.com/doc/current/components/http_client.html
- https://symfony.com/doc/current/logging.html
- https://symfony.com/doc/current/logging/channels_handlers.html
- https://symfony.com/doc/5.4/logging/channels_handlers.html
- https://symfony.com/doc/current/deployment.html
- https://symfony.com/doc/current/messenger.html
- https://symfony.com/doc/current/performance.html
- https://symfony.com/doc/current/http_cache.html
- https://github.com/symfony/symfony/blob/6.1/UPGRADE-6.1.md
- https://raw.githubusercontent.com/symfony/symfony/6.0/UPGRADE-6.0.md
- https://github.com/symfony/symfony/blob/7.0/UPGRADE-7.0.md
- https://github.com/symfony/symfony/blob/7.3/UPGRADE-7.3.md
- https://github.com/symfony/symfony/blob/8.0/UPGRADE-8.0.md
