# Symfony Testing

Use this reference when writing or reviewing PHPUnit tests for a Symfony 5.4 to 8.x application: choosing between unit, kernel and web tests, replacing services in the test container, mocking HTTP calls, asserting Messenger, Mailer or console behaviour, or testing against the database.

## Table of Contents

- [Version gate](#version-gate)
- [Choosing the test layer](#choosing-the-test-layer)
- [Unit tests](#unit-tests)
- [KernelTestCase](#kerneltestcase)
- [WebTestCase](#webtestcase)
- [Container overrides](#container-overrides)
- [HttpClient mocks](#httpclient-mocks)
- [Messenger](#messenger)
- [Mailer](#mailer)
- [Console](#console)
- [Database](#database)
- [Sources](#sources)

## Version gate

| Feature | Since |
| --- | --- |
| `KernelTestCase::getContainer()` as the way to get a container in tests | 5.3 |
| `loginUser()` | 5.1 |
| `loginUser()` third argument `array $tokenAttributes` | 6.4 |
| `assertResponseFormatSame()` | 5.3 |
| `assertResponseIsUnprocessable()` (HTTP 422) | 5.4 |
| `assertCheckboxChecked()`, `assertFormValue()` | 5.2 |
| Notifier assertions | 6.2 |
| `assertSelectorCount()`, `set()` on private services without a public alias, `JsonMockResponse` | 6.3 |
| `assertAnySelectorTextContains()`, `assertEmailSubjectContains()`, HttpClient assertions, relative paths in `assertResponseRedirects()` | 6.4 |
| `assertEmailAddressNotContains()` | 7.4 |
| `MockResponse::fromFile()`, `JsonMockResponse::fromFile()` | 7.1 |
| `assertSessionHasFlashMessage()`, `static::runCommand()`, factory `Closure` in `set()` for non-shared services | 8.1 |
| `MockResponse::getRequestMethod()`, `getRequestUrl()` | 5.2 |
| `InMemoryTransport` in the `Transport\InMemory` sub-namespace | old class deprecated 6.3, removed 7.0 |

## Choosing the test layer

| Layer | Base class | Tests |
| --- | --- | --- |
| Unit | `PHPUnit\Framework\TestCase` | An individual unit of source code, such as a single class |
| Integration | `KernelTestCase` | A combination of classes, usually through the service container, without covering the fully working application |
| Application | `WebTestCase` | The behaviour of the complete application through real or simulated HTTP requests |

Mirror the application structure under `tests/`: `src/Form/` maps to `tests/Form/`. Run the suite with `php bin/phpunit`, or one file with `php bin/phpunit tests/Form/UserTypeTest.php`.

## Unit tests

- **What it is.** A standard PHPUnit unit test; Symfony adds nothing to it.
- **When to use.** One class whose behaviour can be checked with its collaborators built or mocked by hand.
- **When NOT to use.** Repositories: they are meant to be tested against a real database connection.

When a unit test needs data from Doctrine, mock the repository and the entity manager that returns it:

```php
$employeeRepository = $this->createMock(EntityRepository::class);
$employeeRepository->expects($this->any())->method('find')->willReturn($employee);

$entityManager = $this->createMock(EntityManager::class);
$entityManager->expects($this->any())->method('getRepository')->willReturn($employeeRepository);

$salaryCalculator = new SalaryCalculator($entityManager);
```

Messenger handlers are unit tested by calling `__invoke()` directly with mocks, without Messenger infrastructure:

```php
$handler = new SendInvoiceHandler($repository);
$this->expectException(UnrecoverableMessageHandlingException::class);
$handler(new SendInvoice(orderId: 99));
```

## KernelTestCase

- **What it is.** Boots the Symfony kernel so an integration test can fetch services from the dependency injection container.
- **When to use.** Integration tests that need real services from the container.

```php
self::bootKernel();
$container = static::getContainer();
$newsletterGenerator = $container->get(NewsletterGenerator::class);
```

- The kernel is rebooted for each test, so tests run independently.
- `bootKernel()` accepts options: `['environment' => 'my_test_env', 'debug' => false]`.
- `static::getContainer()` returns a special test container with the public services and the non-removed private services.
- The kernel class comes from `KERNEL_CLASS=App\Kernel` in `.env.test`; overriding `getKernelClass()` or `createKernel()` takes precedence over the variable.
- Test-only configuration goes in `config/packages/test/` or under `when@test`.

Pitfalls:

- A private service that nothing uses is removed from the container and cannot be retrieved. Declare it public in `config/services_test.yaml`.
- Env files load in the order `.env`, `.env.test`, `.env.test.local`, later overriding earlier. `.env.local` is not used in the test environment.
- On CI, setting `debug` to `false` significantly improves test performance because it disables clearing the cache.

## WebTestCase

- **What it is.** Extends `KernelTestCase` with a test client that acts as a browser. `static::createClient()` calls `bootKernel()` and creates that client.
- **When to use.** Application tests that make requests and assert on the response.

```php
$client = static::createClient();
$crawler = $client->request('GET', '/');
$this->assertResponseIsSuccessful();
$this->assertSelectorTextContains('h1', 'Hello World');
```

- Hardcode request URLs. Generating them with the router will not catch URL changes that affect users.
- Custom headers: `static::createClient([], ['HTTP_HOST' => 'en.example.com'])`. Replace `-` with `_`, uppercase the name and prefix it with `HTTP_`.
- `$client->loginUser($testUser)` accepts any `UserInterface` and stores a `TestBrowserToken` in the client session. The second argument selects the firewall, `main` by default. In-memory users need a matching `when@test` provider in `config/packages/security.yaml`.
- `$client->catchExceptions(false)` lets exceptions surface so PHPUnit reports them instead of hiding them in logs.
- Response assertions include `assertResponseIsSuccessful()`, `assertResponseStatusCodeSame()`, `assertResponseRedirects()`, `assertResponseHasHeader()`, `assertResponseHeaderSame()`, `assertResponseHasCookie()`, `assertResponseCookieValueSame()`, `assertResponseFormatSame()` and `assertResponseIsUnprocessable()`. Crawler assertions include `assertSelectorTextContains()` and `assertPageTitleSame()`.
- HttpClient assertions such as `assertHttpClientRequest()` and `assertHttpClientRequestCount()` require `$client->enableProfiler()` before the request.

Pitfalls:

- `loginUser()` does not work with stateless firewalls. Add the token or header to each `request()` call instead.
- After a request, the next request makes the client reboot the kernel. `$client->disableReboot()` resets instead of rebooting, but it also clears the security token and detaches Doctrine entities.
- Calling `createClient()` while a kernel is already booted is deprecated since 4.4.

## Container overrides

- **What it is.** Replacing a service in the test container with a test double through `set()`.
- **When to use.** Kernel or web tests where one collaborator must be a mock.

```php
$container->set(NewsRepositoryInterface::class, $newsRepository);
```

Before 6.3, setting a private alias fails unless the alias is made public:

```yaml
services:
    App\Contracts\Repository\NewsRepositoryInterface:
        alias: App\Repository\NewsRepository
        public: true
```

Since 6.3, `set()` works with private services and aliases without extra configuration. Since 8.1, a non-shared service is mocked with a factory `Closure`, because each lookup creates a new instance:

```php
$container->set(Mailer::class, function (): Mailer {
    $mailer = $this->createMock(Mailer::class);
    $mailer->method('send')->willReturn(true);

    return $mailer;
});
```

## HttpClient mocks

- **What it is.** `MockHttpClient` implements `HttpClientInterface`, so code type-hinted with the interface uses the real client in production and the mock in tests.
- **When to use.** Tests of code that sends HTTP requests.
- **Pros.** No real HTTP requests are made, so tests run faster and give consistent results.

`MockResponse` objects passed to the constructor are returned in order, one per `request()` call:

```php
use Symfony\Component\HttpClient\MockHttpClient;
use Symfony\Component\HttpClient\Response\MockResponse;

$responses = [
    new MockResponse($body1, $info1),
    new MockResponse($body2, $info2),
];

$client = new MockHttpClient($responses);
```

A callback receives the method, URL and options and returns the response:

```php
$callback = function ($method, $url, $options): MockResponse {
    return new MockResponse('...');
};
```

- `MockResponse::getRequestMethod()` and `getRequestUrl()` show which request was sent.
- `JsonMockResponse` encodes the passed body to JSON. `MockResponse::fromFile('tests/fixtures/response.xml')` loads a response snapshot from a file.
- Yielding an `Exception` from a `MockResponse` body mocks a transport error (6.1). `HarFileResponseFactory` replays responses from `.har` files (6.4).

## Messenger

- **What it is.** The `in-memory://` transport keeps messages in memory instead of delivering them, so a test can assert what was sent.
- **When to use.** Kernel or web tests that check a message was dispatched to a transport.

```yaml
when@test:
    framework:
        messenger:
            transports:
                async_priority_normal: 'in-memory://'
```

```php
$transport = self::getContainer()->get('messenger.transport.async_priority_normal');
self::assertCount(1, $transport->getSent());
self::assertInstanceOf(SendOrderConfirmation::class, $transport->getSent()[0]->getMessage());
```

- `getSent()` returns the sent envelopes.
- The `serialize` option (default `false`), or the DSN `in-memory://?serialize=true`, serializes messages.

Pitfalls: in-memory transports reset automatically after each test in `KernelTestCase` and `WebTestCase`, and the test client resets them before each new request. Check sent messages before making another request, such as `$client->followRedirect()`, or call `$client->disableReboot()`.

Versions: on 5.4 the class is `Symfony\Component\Messenger\Transport\InMemoryTransport`; 6.3 deprecates it in favour of the `InMemory` sub-namespace and 7.0 removes the old class.

## Mailer

- **What it is.** Built-in assertions in classes extending `KernelTestCase` or using `MailerAssertionsTrait`.
- **When to use.** Checking that a request or service sent an email and what it contains.

```php
final class MailControllerTest extends WebTestCase
{
    public function testMailIsSentAndContentIsOk(): void
    {
        $client = static::createClient();
        $client->request('GET', '/mail/send');
        self::assertResponseIsSuccessful();

        self::assertEmailCount(1);

        $email = self::getMailerMessage();

        self::assertEmailHtmlBodyContains($email, 'Welcome');
        self::assertEmailTextBodyContains($email, 'Welcome');
    }
}
```

Pitfalls:

- Use `assertQueuedEmailCount()` instead of `assertEmailCount()` when Messenger sends the mail asynchronously.
- If the controller redirects after sending, configure the client not to follow redirects: the kernel reboots when following a redirect, and the message is lost from the mailer event handler.

## Console

- **What it is.** `CommandTester` runs one command and exposes its output; `ApplicationTester` runs a full console application. Since 8.1, `static::runCommand()` runs a command inside `KernelTestCase` and returns an `ExecutionResult`.
- **When to use.** `CommandTester` for standalone projects or when lower-level control is needed; `ApplicationTester` when console events must be dispatched.

```php
$command = $application->find('app:create-user');
$commandTester = new CommandTester($command);
$commandTester->execute(['username' => 'Wouter']);
$commandTester->assertCommandIsSuccessful();
$this->assertStringContainsString('Username: Wouter', $commandTester->getDisplay());
```

On 8.1, `$result = static::runCommand('app:create-user', ['username' => 'Wouter']);` then `$this->assertCommandIsSuccessful($result);`. Other assertions: `assertCommandFailed()`, `assertCommandIsInvalid()`, `assertCommandResultEquals()`. `ExecutionResult` offers `getOutput()`, `getErrorOutput()`, `getDisplay()` and `statusCode`; interactive input goes in the third argument of `runCommand()`.

Pitfalls:

- Console events are not dispatched with `CommandTester`; use `ApplicationTester`.
- Call `$application->setAutoExit(false)` before `new ApplicationTester($application)`, or PHPUnit's process is terminated by `exit()`. In a single-command application, `setAutoExit(false)` is also needed to get the result in `CommandTester` (5.2).
- `CommandTester` does not implement `ConsoleOutputInterface`; for output sections pass `['capture_stderr_separately' => true]` to `execute()`.

## Database

- **What it is.** Functional tests that use real repositories against a test database.
- **When to use.** Repository queries and anything else that needs a real database connection.

Put a machine-specific `DATABASE_URL` in `.env.test.local`, or in `.env.test` to share it. Give the database a `_test` suffix, such as `project_acme_test`. Load fixtures with `php bin/console --env=test doctrine:fixtures:load`.

Extend `KernelTestCase` and fetch the entity manager:

```php
$kernel = self::bootKernel();
$this->entityManager = $kernel->getContainer()
    ->get('doctrine')
    ->getManager();
```

- `DAMADoctrineTestBundle` begins a database transaction before every test and rolls it back automatically after the test finishes.

Pitfalls: close the entity manager and set it to `null` in `tearDown()` to avoid memory leaks.

## Sources

- https://symfony.com/doc/5.4/testing.html
- https://symfony.com/doc/current/testing.html
- https://symfony.com/doc/6.4/testing.html
- https://symfony.com/doc/current/testing/database.html
- https://symfony.com/doc/current/http_client.html
- https://symfony.com/doc/current/messenger.html
- https://symfony.com/doc/current/mailer.html
- https://symfony.com/doc/current/console.html
- https://github.com/symfony/symfony/blob/7.4/src/Symfony/Bundle/FrameworkBundle/CHANGELOG.md
- https://github.com/symfony/symfony/blob/7.4/src/Symfony/Component/HttpClient/CHANGELOG.md
- https://github.com/symfony/symfony/blob/7.4/src/Symfony/Component/Messenger/CHANGELOG.md
