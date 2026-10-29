# Security review checklist — the universal baseline

Load this during Step 6 of a code review. It is the **floor**: the small set of
security classes worth checking on *any* change in *any* project, whatever the client's
bar. It is deliberately not an exhaustive standard.

Three things set its scope:

- **It is a floor, not a ceiling.** A project's own security rules — in its `CLAUDE.md`,
  its `.claude/rules/`, its decision records, or a client ruleset the task supplies —
  **outrank this list** and are applied first, exactly as project review checklists
  outrank the review skill. This baseline fills what they leave unstated; it never
  overrides them.
- **It is framework-agnostic.** The stack-specific defenses — NestJS guards, Symfony
  voters, frontend XSS sinks, Lambda IAM — live in the installed stack skill's own
  security reference. After this list, apply those too (the review skill already loads
  the stack skill when one is available).
- **A full audit is a different task.** Reviewing a change set against this baseline is
  not a penetration test or a whole-codebase posture audit. When the ask is "audit this
  service" rather than "review this change", that is its own scope with its own tools.

The rows map to the OWASP Top 10 *classes* for recognisability, not to the full
standard. Report a hit as a normal review finding: severity, evidence (file and line),
the consequence, and the minimum correction — the same contract as every other finding.
Severity follows the review's own vocabulary: **blocker** (exploitable as written),
**major** (exploitable under a plausible condition), **minor** (defense-in-depth gap).

## The baseline

Check every hit against the change. Where the project documents a justified tradeoff,
record it rather than re-reporting it.

| Class (OWASP) | What to look for in the diff | Typical severity | Minimum correction |
| :-- | :-- | :-- | :-- |
| **Broken access control** (A01) | A new endpoint, handler, or action with no authorization check; a role/permission gate that was dropped in the change. | blocker | Add an explicit authorization check at the entry point, using the framework's mechanism, not an ad-hoc role-string read. |
| **Object-level access control / IDOR** (A01) | A resource fetched by a request-supplied id without scoping to the authenticated principal — `findById(req.params.id)` with no owner/tenant check. | blocker | Scope the query by the current user or tenant, or verify ownership before acting. |
| **Mass assignment / over-posting** (A08) | A request body bound straight onto a persistence entity or domain object — `create(req.body)`, `assign(entity, input)` — so a caller can set fields the form never exposed (role, ownerId, isAdmin). | major | Bind through an explicit DTO or an allow-list of writable fields. |
| **Injection** (A03) | Untrusted input concatenated into a query, command, path, or template — string-built SQL, `exec`/`spawn` with request data, a template compiled from user input. | blocker | Parameterised queries / prepared statements; a safe builder; argument arrays, never a shell string; escape or allow-list for paths and templates. |
| **Unsafe deserialization / dynamic evaluation** (A08) | `eval`, `Function(...)`, `pickle.loads`, PHP `unserialize`, `yaml.load`, or any object-graph deserializer run on request data. | blocker | A data-only parser (`JSON.parse`, safe-load); validate into a schema; never evaluate untrusted strings. |
| **SSRF** (A10) | A server-side HTTP/DNS/file fetch whose URL, host, or port comes from the request. | major | Allow-list the destinations; reject internal address ranges and non-HTTP schemes; and disable redirect following or re-validate every hop — a validated initial URL can 30x-redirect into the internal network, so checking only the first address is not enough. |
| **Open redirect** (A01) | A redirect whose target is taken from a request parameter without validation. | minor | Allow-list redirect targets or restrict to same-origin relative paths. |
| **Sensitive data exposure** (A02) | Secrets, tokens, or PII written to logs or error messages; an entity serialized to the client with internal fields (password hash, internal flags); a stack trace or DB error returned to the caller. | major | Redact at the logging boundary; return an explicit response shape, not the entity; send a generic error to the client and keep detail server-side. |
| **Hardcoded secret** (A05) | A credential literal — API key, password, token, or private key — that grants access to a real or shared protected resource, added in the diff. This includes a real value pasted into a test, fixture, or committed config. A self-evidently fake placeholder used only in an isolated test (`password: "test-password"`, `sk_test_000…`) is not a secret — do not flag it. | blocker | Move the real value to the secret store / environment; reference it; rotate the exposed credential. |
| **Cryptographic failure** (A02) | Custom or weak crypto: `md5`/`sha1` for passwords, a non-CSPRNG (`Math.random`, `rand()`) for a token or id that must be unguessable, ECB mode, a hardcoded key or IV. | major | The framework's password hasher (bcrypt/argon2); a CSPRNG for security values; standard authenticated modes; keys from the secret store. |
| **Authentication weakness** (A07) | New auth or session code: a self-contained token (JWT) accepted without verifying its signature and expiry; an opaque session token or id not validated against server-side state; a login or OTP path with no rate limiting; a password-reset or session that does not rotate. | major | For a self-contained token, verify the signature and `exp`; for an opaque token or session id, validate it against its server-side store and honour server-side expiry and revocation. Throttle credential and reset endpoints; rotate the session on privilege change. |
| **Vulnerable dependency** (A06) | A dependency added or bumped in a manifest/lockfile to a version with a known advisory, or a new unmaintained package on a trust boundary. | major | Pin to a fixed version, or record why the advisory does not apply to this usage. |
| **Security misconfiguration** (A05) | CORS widened to `*` while credentials are allowed; debug or verbose errors enabled for a deployed path; a security header or CSRF protection removed on a state-changing route. | major | Restrict the origin; disable debug on deployed paths; keep state-changing routes CSRF-protected and non-`GET`. |

## After the baseline — the extension layers

The baseline is only the first of four layers a review may apply. Add, in order:

1. **Stack depth.** If a stack skill is available this session (NestJS, frontend,
   Python, serverless, …), load it and run its security rows — they carry what is
   specific to one runtime and framework. This is the same load the review skill already
   does for the stack's general checklist.
2. **Project rules.** If the project under review ships its own security rules, they
   are authoritative and were already applied first; name any baseline row they
   deliberately relax.
3. **A named standard, on request.** When the task names a bar — "OWASP Top 10 in
   full", "ASVS L2", "pentest prep", a client ruleset — the full audit task applies it.
   A change review stays at this baseline unless the caller asks otherwise.

## Honest limits

- This list reads a *diff*. It cannot see a vulnerability whose cause is outside the
  change — an existing missing auth check a new call now reaches. When the change makes
  such a latent issue exploitable, report it; do not treat "not in the diff" as "not a
  finding".
- Absence of a hit is not proof of safety. A clean security pass says "no issues in the
  classes above were found in this change", never "this change is secure".
