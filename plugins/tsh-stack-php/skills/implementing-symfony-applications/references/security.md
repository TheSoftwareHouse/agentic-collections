# Symfony Security

Use this reference when a task touches authentication, authorization, firewalls, authenticators, access tokens, voters, password hashing, CSRF, login throttling, remember me or impersonation in a Symfony 5.4 to 8.x application.

## Table of Contents

- [Version gate](#version-gate)
- [Firewalls and access control](#firewalls-and-access-control)
- [Authenticators](#authenticators)
- [Access tokens](#access-tokens)
- [Voters and IsGranted](#voters-and-isgranted)
- [Passwords](#passwords)
- [CSRF](#csrf)
- [Login throttling, remember me, impersonation](#login-throttling-remember-me-impersonation)
- [Upgrade checklist](#upgrade-checklist)
- [Sources](#sources)

## Version gate

| Feature | 5.4 | 6.x | 7.x | 8.x |
| --- | --- | --- | --- | --- |
| Authenticator manager | opt-in `enable_authenticator_manager: true` (5.3) | required, missing option throws (6.0); option deprecated (6.2) | option removed (7.0) | removed |
| Guard | deprecated (5.3) | removed (6.0) | removed | removed |
| `#[IsGranted]` | via SensioFrameworkExtraBundle | core (6.2), `exceptionCode` (6.3) | closures (7.3), `$methods` (7.4) | core |
| `Security` service | `Security\Core\Security` | `SecurityBundle\Security` (6.2), core class deprecated | core class removed (7.0) | bundle class |
| `access_token` authenticator | absent | RFC 6750 (6.2), OIDC handlers (6.3) | CAS 2.0 (7.1), OAuth2 introspection (7.3) | yes |
| Voter `$vote` argument | absent | absent | voters can explain their vote (7.3) | part of the signature (8.0) |
| `eraseCredentials()` | present | present | deprecated (7.3) | removed (8.0) |
| `#[IsCsrfTokenValid]` | absent | absent | 7.1, `$tokenSource` 7.4 | yes |

## Firewalls and access control

- **What it is.** "A 'firewall' is your authentication system." Authorization is separate: `access_control`, `isGranted()`, `denyAccessUnlessGranted()`, `#[IsGranted]`, Twig `is_granted()` and voters.
- **When to use.** The `firewalls` section is "the most important section"; every authenticated area needs one. `access_control` can match on path, IP address, hostname and HTTP methods.
- **When NOT to use.** `role_hierarchy` values are static; for roles stored in the database, write a custom voter.
- **Pros.** `lazy: true` "prevents the session from being started if there is no need for authorization", which keeps requests cacheable.

Pitfalls:

- "Only one firewall is active on each request": the first `pattern` match wins. A firewall with no pattern matches all requests, so define it last.
- "Only the first access control that matches will be used." Prefix each `path` with `^` so it matches only URLs beginning with the pattern.
- For role hierarchy to work, do not read `$user->getRoles()` manually; use `isGranted('ROLE_ADMIN')`.
- On refresh, `AbstractToken` compares the return values of `getPassword()`, `getSalt()` and `getUserIdentifier()`.
- `#[CurrentUser]` works only in controller arguments.
- Do not call `Security::getFirewallConfig()` in a constructor. `UserBadge` limits the user identifier to 4096 characters to prevent session storage flooding. On 404 pages the user appears logged out.

```yaml
security:
    password_hashers:
        Symfony\Component\Security\Core\User\PasswordAuthenticatedUserInterface: 'auto'
    firewalls:
        dev:
            pattern: ^/(_(profiler|wdt)|css|images|js)/
            security: false
        main:
            lazy: true
            form_login:
                enable_csrf: true
            login_throttling:
                max_attempts: 3
    access_control:
        - { path: ^/admin/login, roles: PUBLIC_ACCESS }
        - { path: ^/admin, roles: ROLE_ADMIN }
```

Versions:

- **5.3**: the authenticator-based system arrives behind `enable_authenticator_manager: true`; not setting it is deprecated. `getUserIdentifier()` and `PasswordAuthenticatedUserInterface` are introduced; `getUsername()` is deprecated. `IS_ANONYMOUS` and `IS_AUTHENTICATED_ANONYMOUSLY` are deprecated; use `PUBLIC_ACCESS`.
- **6.0**: missing `enable_authenticator_manager: true` throws. `getUsername()`, `loadUserByUsername()`, `UsernameNotFoundException`, `AnonymousToken`, `is_anonymous()` and the anonymous attributes are removed; use `getUserIdentifier()`, `loadUserByIdentifier()`, `UserNotFoundException`, `PUBLIC_ACCESS`, `isFullFledged()` or `isAuthenticated()`. `IS_IMPERSONATOR` replaces `ROLE_PREVIOUS_ADMIN`. `User` and `UserChecker` become `InMemoryUser` and `InMemoryUserChecker`. `getPassword()` moves to `PasswordAuthenticatedUserInterface`.
- **6.2**: inject `Symfony\Bundle\SecurityBundle\Security`; it adds `getFirewallConfig()`, `login()` and `logout()`. `enable_authenticator_manager` is deprecated. `Security::ACCESS_DENIED_ERROR`, `AUTHENTICATION_ERROR` and `LAST_USERNAME` move to `SecurityRequestAttributes`.
- **6.3**: `Security::login()` returns the authenticator response.
- **6.4**: `pattern` accepts an array of regexes; `Security::login()` takes badges; `require_previous_session` has no effect.
- **7.0**: `enable_authenticator_manager` and `require_previous_session` are removed. Enabling the bundle without configuring it is not allowed. `framework.session.cookie_secure` defaults to `auto` and `cookie_samesite` to `'lax'`.
- **7.2**: `Security::login()` accepts passport attributes. **7.3**: `Security::isGrantedForUser()` checks authorization without relying on the session.
- **7.4**: `#[CurrentUser]` supports union types; `debug:security:role-hierarchy` dumps the hierarchy as a Mermaid.js flowchart.
- **8.0**: requires PHP 8.4. `eraseCredentials()` is removed from `UserInterface` and `TokenInterface`; erase credentials in `__serialize()`. `hide_user_not_found` becomes `expose_security_errors` (`true` to `'none'`, `false` to `'all'`, new `'account_status'`). `UserCheckerInterface::checkPostAuth()` gains `$token`.

## Authenticators

- **What it is.** A class implementing `AuthenticatorInterface`, usually extending `AbstractAuthenticator`, whose `authenticate()` returns a `Passport`. Built-in: Form Login, JSON Login, HTTP Basic, Login Link, Access Tokens, X.509 client certificates, remote users.
- **When to use a custom one.** When no built-in authenticator fits. For API tokens on 6.2+, check the `access_token` authenticator first.
- **Pros.** Badges add behaviour: `CsrfTokenBadge` validates CSRF during authentication, `PasswordUpgradeBadge` is added automatically with `PasswordCredentials`, `RememberMeBadge` enables remember me.

Pitfalls:

- `supports()` is called on every request; returning `false` skips the authenticator.
- `onAuthenticationSuccess()` returning `null` lets the request continue authenticated, which suits API routes. `onAuthenticationFailure()` returning `null` continues the request unauthenticated.
- Never use `$exception->getMessage()` on an `AuthenticationException`; use `getMessageKey()` and `getMessageData()`. Throw `CustomUserMessageAuthenticationException` for custom messages.
- Custom authenticators must be enabled explicitly under the firewall's `custom_authenticators`. Use `SelfValidatingPassport` only when no credentials need checking, for example API tokens.
- Without `RememberMeBadge`, remember me is not activated, regardless of other settings.
- With login throttling on, `onAuthenticationFailure()` can check for `TooManyLoginAttemptsAuthenticationException`.

```php
final class PartnerApiKeyAuthenticator extends AbstractAuthenticator
{
    public function __construct(private readonly PartnerKeyRepository $keys)
    {
    }

    public function supports(Request $request): ?bool
    {
        return $request->headers->has('X-Api-Key');
    }

    public function authenticate(Request $request): Passport
    {
        $key = $this->keys->findActive((string) $request->headers->get('X-Api-Key'))
            ?? throw new CustomUserMessageAuthenticationException('Invalid API key.');

        return new SelfValidatingPassport(new UserBadge($key->partnerIdentifier()));
    }

    public function onAuthenticationSuccess(Request $request, TokenInterface $token, string $firewallName): ?Response
    {
        return null;
    }

    public function onAuthenticationFailure(Request $request, AuthenticationException $exception): ?Response
    {
        return new JsonResponse(
            ['message' => strtr($exception->getMessageKey(), $exception->getMessageData())],
            Response::HTTP_UNAUTHORIZED,
        );
    }
}
```

Versions: Guard is deprecated in 5.3 and removed in 6.0. 6.0 replaces `createAuthenticatedToken()` with `createToken()` and removes `PassportInterface`, `UserPassportInterface` and `PassportTrait`. 6.2 applies `#[\SensitiveParameter]` to plain passwords and sensitive tokens on PHP 8.2+. 6.3 adds `RememberMeBadge` to `JsonLoginAuthenticator`. 7.4 deprecates callable firewall listeners; 8.0 removes them (extend `AbstractListener` or implement `FirewallListenerInterface`).

## Access tokens

- **What it is.** The built-in `access_token` authenticator reads a token (opaque string, JWT or SAML2) and passes it to your `AccessTokenHandlerInterface::getUserBadgeFrom()`.
- **When to use.** API authentication on 6.2+, including OIDC (6.3), CAS 2.0 (7.1) and OAuth2 token introspection (7.3).
- **When NOT to use.** On 5.4, where it does not exist; write a custom authenticator.
- **Pros.** The handler only maps a token to a `UserBadge`; stateless firewalls can omit the user provider.

Pitfalls:

- The handler must check that the token is valid. For JWTs it must verify the signature and the `sub`, `iat`, `nbf` and `exp` claims.
- The default extractor reads `Authorization: Bearer`. `query_string` and `request_body` "SHOULD NOT be used" because URLs and bodies are likely to be logged. Custom extractors run in the configured order.
- By default the request continues to the controller; change it with `success_handler` and `failure_handler`.
- The `oidc` handler needs `web-token/jwt-library`; without the GMP extension JWT verification is orders of magnitude slower.
- `loginUser()` in tests does not work with stateless firewalls; send the token or header with each request.

```yaml
security:
    firewalls:
        api:
            pattern: ^/api
            stateless: true
            access_token:
                token_handler: App\Security\ApiTokenHandler
```

```php
final class ApiTokenHandler implements AccessTokenHandlerInterface
{
    public function __construct(private readonly ApiTokenRepository $tokens)
    {
    }

    public function getUserBadgeFrom(string $accessToken): UserBadge
    {
        $token = $this->tokens->findOneByValue($accessToken);
        if (null === $token || !$token->isValid()) {
            throw new BadCredentialsException('Invalid credentials.');
        }

        return new UserBadge($token->getUserId());
    }
}
```

Versions: 8.0 replaces the OIDC `algorithm` and `key` options with `algorithms` and `keyset`. `enforce_key_usage_verification` is 8.1.

## Voters and IsGranted

- **What it is.** Voters "allow you to centralize all permission logic, then reuse them in many places". All voters are called on every `isGranted()`, `denyAccessUnlessGranted()` and access control check.
- **When to use.** Any business rule that decides access, including roles stored in the database.
- **Decision strategy.** `affirmative` (default), `consensus` (ties use `allow_if_equal_granted_denied`, default `true`), `unanimous`, `priority`. If all voters abstain, `allow_if_all_abstain` decides (default `false`).
- **Pros.** The `$vote` argument explains a decision in logs and exception pages; voters are tagged automatically with the default `services.yaml`.

Pitfalls:

- Implement `supportsAttribute()` and `supportsType()`: when they return `false`, Symfony does not call the voter again for that attribute or type. Use `is_a($subjectType, Post::class, true)` because the subject may be a Doctrine proxy.
- Inside a voter, use `AccessDecisionManager`, not `Security::isGranted()`, which may check a different token.
- `#[IsGranted]` throws `AccessDeniedException` (403); a different status code throws `HttpException`. The second `#[IsGranted]` argument names the controller argument passed to the voter.

```php
final class PolicyVoter extends Voter
{
    public const VIEW = 'POLICY_VIEW';
    public const EDIT = 'POLICY_EDIT';

    protected function supports(string $attribute, mixed $subject): bool
    {
        return \in_array($attribute, [self::VIEW, self::EDIT], true) && $subject instanceof Policy;
    }

    protected function voteOnAttribute(string $attribute, mixed $subject, TokenInterface $token, ?Vote $vote = null): bool
    {
        $user = $token->getUser();
        if (!$user instanceof User) {
            $vote?->addReason('The user is not logged in.');

            return false;
        }

        return match ($attribute) {
            self::VIEW => $subject->isVisibleTo($user),
            self::EDIT => $subject->ownerId() === $user->getId(),
        };
    }
}
```

Versions:

- **5.4**: signature `voteOnAttribute(string $attribute, $subject, TokenInterface $token): bool`. `#[IsGranted]` comes from SensioFrameworkExtraBundle. Adds `CacheableVoterInterface` and `AccessDecisionStrategyInterface`; a string strategy for `AccessDecisionManager` is deprecated.
- **6.0**: `AccessDecisionManager` requires an `AccessDecisionStrategyInterface` instance.
- **6.2**: core `#[IsGranted]`; expressions as attribute and subject. **6.3**: `exceptionCode`.
- **7.3**: voters can explain their vote; closures in `#[IsGranted]`.
- **7.4**: `Vote::$extraData`; `Security::getAccessDecision()` and `getAccessDecisionForUser()`; `$methods` argument and subclassing for `#[IsGranted]`.
- **8.0**: `$vote` is added to `Voter::voteOnAttribute()` and `VoterInterface::vote()`; `$accessDecision` to `AuthorizationCheckerInterface::isGranted()` and the decision manager and strategy interfaces. **8.1**: voter priority via `#[AsTaggedItem(priority: 10)]` (default `0`).

## Passwords

- **What it is.** The PasswordHasher component, configured under `security.password_hashers`.
- **When to use.** Hashing and verifying user passwords with `hashPassword()` and `isPasswordValid()`.
- **Pros.** `auto` selects the best available hasher (currently bcrypt); `migrate_from` rehashes old hashes on login.

Pitfalls:

- `auto` may change hash length; `varchar(255)` "should be a good setting".
- Under `when@test` use the lowest costs: `cost: 4`, `time_cost: 3`, `memory_cost: 10`.
- Rehash on login needs `PasswordUpgraderInterface` on the Doctrine user repository; a custom authenticator must use `PasswordCredentials`.
- Custom hashers must reject passwords longer than 4096 characters in `hash()` and `verify()`.
- Bcrypt cost ranges 4 to 31, default 13; each increment doubles the time. PBKDF2 is no longer recommended.

```php
$user->setPassword($this->hasher->hashPassword($user, $plainPassword));
```

Versions: `password_hashers` replaced `encoders` in 5.3, and `Core\Encoder\*` is deprecated there; 6.0 drops `Core\Encoder\*` and replaces `user:encode-password` with `user:hash-password`.

## CSRF

- **What it is.** Tokens that stop a malicious site making a user perform actions without consent. Symfony Forms check them automatically (field `_token`); manual checks use `csrf_token()` and `isCsrfTokenValid()`.
- **When to use.** State-changing operations, which must not use `GET`. Enable it on login forms with `enable_csrf: true` under `form_login`.
- **Stateful vs stateless.** Stateful tokens live in the session and are unique per user and action. Stateless tokens (`stateless_token_ids`) are validated through `Origin` and `Referer` and are on by default in Flex applications.

Pitfalls: a stateful token starts a session as soon as the form renders; use stateless tokens to cache such pages. Tokens in `GET` parameters leak through history, logs and Referer headers. `#[IsCsrfTokenValid]` checks all HTTP methods by default; methods missing from `methods` skip validation.

```php
#[Route('/items/{id}/delete', methods: ['POST'])]
#[IsCsrfTokenValid('delete-item', tokenKey: 'token')]
public function delete(Item $item): Response
{
}
```

Versions: 7.0 replaces the logout `csrf_token_generator` with `csrf_token_manager`. `#[IsCsrfTokenValid]` is 7.1; `$tokenSource` (`SOURCE_PAYLOAD`, `SOURCE_QUERY`, `SOURCE_HEADER`) is 7.4.

## Login throttling, remember me, impersonation

**Login throttling** (5.2, `interval` 5.3) needs `symfony/rate-limiter`. Default: 5 attempts per minute; `max_attempts` failures per IP plus username and `5 * max_attempts` per IP. State is in the Symfony cache by default. For a custom limiter implement `RequestRateLimiterInterface` or use `DefaultLoginRateLimiter`, whose constructor throws on an empty secret since 7.0. 7.4 adds options for a cache pool and storage service.

**Remember me** needs `RememberMeBadge`; HTTP Basic does not support it. Do not use it on shared PCs. `lifetime` defaults to one year (`31536000`). Signature-based tokens (default) are invalidated when a `signature_properties` value changes (default `password`); a field such as `forceReloginAt` invalidates all of a user's tokens. `token_provider: { doctrine: true }` stores tokens in a table so rows can be invalidated. Guard sensitive actions with `IS_AUTHENTICATED_FULLY`. Cookie defaults: `secure: false`, `httponly: true`, `samesite: null`. 5.4 deprecates the `*RememberMeServices` classes; 8.0 removes the user FQCN from the cookie.

**Impersonation** (`switch_user`) is for a restricted group holding `ROLE_ALLOWED_TO_SWITCH`. It is not compatible with mechanisms such as `REMOTE_USER`. Switch with `?_switch_user=thomas`, exit with `?_switch_user=_exit`; Twig has `impersonation_path()` and `impersonation_exit_path()`. A custom switch attribute must not start with `ROLE_`. Read the real user with `SwitchUserToken::getOriginalToken()->getUser()`. `target_route` works only in a stateful firewall. Listen to `security.switch_user`, dispatched before switching and before exiting.

## Upgrade checklist

- 5.4 to 6.x: set `enable_authenticator_manager: true`; replace Guard authenticators; `getUsername()` to `getUserIdentifier()`; implement `PasswordAuthenticatedUserInterface`; `encoders` to `password_hashers`; anonymous attributes to `PUBLIC_ACCESS`; `Core\Security` to `SecurityBundle\Security`; Sensio `IsGranted` to core.
- 6.x to 7.x: delete `enable_authenticator_manager` and `require_previous_session`.
- 7.x to 8.x: PHP 8.4; add `$vote` to every voter; move `eraseCredentials()` logic to `__serialize()`; `hide_user_not_found` to `expose_security_errors`; replace callable firewall listeners.

## Sources

- https://symfony.com/doc/5.4/security.html
- https://symfony.com/doc/6.4/security.html
- https://symfony.com/doc/current/security/voters.html
- https://symfony.com/doc/current/security/access_token.html
- https://symfony.com/doc/current/security/csrf.html
- https://symfony.com/doc/current/security/passwords.html
- https://symfony.com/doc/current/security/remember_me.html
- https://symfony.com/doc/current/security/impersonating_user.html
- https://symfony.com/doc/current/security/custom_authenticator.html
- https://symfony.com/doc/5.4/testing.html
- https://symfony.com/doc/7.4/controller/error_pages.html
- https://github.com/symfony/symfony/blob/5.4/UPGRADE-5.3.md
- https://github.com/symfony/symfony/blob/5.4/UPGRADE-5.4.md
- https://github.com/symfony/symfony/blob/6.0/UPGRADE-6.0.md
- https://github.com/symfony/symfony/blob/6.2/UPGRADE-6.2.md
- https://github.com/symfony/symfony/blob/7.0/UPGRADE-7.0.md
- https://github.com/symfony/symfony/blob/8.0/UPGRADE-8.0.md
- https://github.com/symfony/symfony/blob/7.4/src/Symfony/Component/Security/Http/CHANGELOG.md
- https://github.com/symfony/symfony/blob/7.4/src/Symfony/Bundle/SecurityBundle/CHANGELOG.md
- https://github.com/symfony/symfony/blob/7.4/src/Symfony/Component/Security/Core/CHANGELOG.md
