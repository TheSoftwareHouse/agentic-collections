# Authenticated capture

How capture handles a login or access gate. One rule governs everything here:
**a genuine login through the application's real sign-in UI, with inputs the user
explicitly provided, is allowed; bypassing the gate never is.** Never seed, inject,
or fabricate cookies, tokens, `localStorage`, or `sessionStorage`; never assume a
role or identity; never exploit a gate that looks trivially circumventable — report
that as a potential security vulnerability in the escalation notes instead.

## First: use what the project already has

Do not introduce a new convention when the repository already answers the question.
Work down this ladder and stop at the first hit — each rung is cheaper for the team
than the one below it, and the last rung is the only one that asks anyone to add
anything:

1. **An auth recipe the project documents** — `CLAUDE.md`, `.claude/rules/`, or the
   plan's Technical Context naming how to sign in for local verification (which
   account, which script, which fixture). Follow it as written. Treat these files as
   a pointer to the recipe, never as a place credentials should live: a password
   committed to `CLAUDE.md` is a secret in Git, so if you find one, use it for this
   run and flag it to the caller as something to move out of the repository.
2. **An existing end-to-end auth setup** — a Playwright `global.setup`, a committed
   storage-state path, an auth fixture or helper the E2E suite already uses. This is
   the best outcome available: the project already solved this, the credentials are
   already wherever the team decided they belong, and verification inherits that
   decision instead of competing with it.
3. **Existing `.env` variables that plainly match the login form's fields** — names
   like `E2E_*`, `TEST_*`, `PLAYWRIGHT_*`, or a project-specific pair whose meaning
   is unambiguous for the fields on screen. Use them as they are; never rename or
   duplicate them under our own prefix. When a candidate is ambiguous, or plausibly
   a production credential rather than a test one, do not guess — ask through the
   caller.
4. **A seed or fixture that creates a known development account** — a documented
   seeded user is a legitimate input when the project provides one.
5. **Only when none of the above exists**, fall back to the derived contract below.

Whatever rung you land on, report it in the capture summary, so the caller can see
which mechanism authenticated the run.

## Last resort: the derived `TSH_UI_LOGIN_*` contract

When the pinned page redirects to a **standard credential form**:

1. **Derive one env var name per required field** from the live form, using this
   order of precedence for the field key: `name` → `autocomplete` → `id` → visible
   label text. Normalize the chosen key to uppercase snake case and prefix it with
   `TSH_UI_LOGIN_`. Examples: `email` → `TSH_UI_LOGIN_EMAIL`, `userName` →
   `TSH_UI_LOGIN_USER_NAME`, `company-code` → `TSH_UI_LOGIN_COMPANY_CODE`.
2. **If repo-root `.env` already provides those exact vars**, load them at runtime
   and log in as an ordinary user would (fill the real form, submit). Never print
   the values.
3. **If the vars are missing**, stop capture and return the exact derived names to
   the caller. The caller asks the user with this message pattern:

   ```text
   The page redirected to login. Add these exact vars to repo-root `.env` and tell
   me when the file is saved:
   - [DERIVED_ENV_VAR_1]=...
   - [DERIVED_ENV_VAR_2]=...
   After you save the file, I will rerun capture and reload `.env` automatically.
   ```

4. **On the rerun, reload `.env` before the auth attempt** so values the user just
   saved are picked up immediately — the user never pastes secrets into chat.

```bash
# load the local .env contract without printing values
set -a
source .env
set +a

playwright-cli open -s ui-verify
playwright-cli goto "https://example.com/sign-in" -s ui-verify
playwright-cli snapshot -s ui-verify                          # get field refs
playwright-cli fill <emailRef> "$TSH_UI_LOGIN_EMAIL" -s ui-verify
playwright-cli fill <passwordRef> "$TSH_UI_LOGIN_PASSWORD" --submit -s ui-verify
playwright-cli --raw eval "window.location.href" -s ui-verify  # confirm login landed
```

## Login once, reuse the session

After one successful real login, save the authenticated session to a secret path
**outside `specifications/**`** and reuse it in later iterations instead of logging
in again:

```bash
playwright-cli state-save /tmp/ui-auth.json -s ui-verify
# later iterations:
playwright-cli state-load /tmp/ui-auth.json -s ui-verify
playwright-cli goto "https://example.com/protected-screen" -s ui-verify
```

## Fallbacks for non-standard auth

Use a caller-provided, already-authenticated storage-state path, or direct manual
login in the open browser session, **only** when the redirected screen is not a
standard credential form (SSO chooser, MFA challenge, captcha), when the field keys
or `.env` cannot be derived or loaded reliably, or when the user explicitly prefers
it. Do not start with a broad questionnaire — the `.env` contract is the default.

## Secret handling

- Never ask the user to paste a password into chat.
- Never echo `TSH_UI_LOGIN_*` values into terminal output, artifacts, or reports.
- Treat any storage-state file as a secret: keep it out of `specifications/**`, out
  of version control, and never persist it beyond the caller-provided path.
- Never write credentials into plans, task specs, reports, or committed files.

## When auth still blocks

If login fails with the provided inputs, the gate is non-standard and no fallback
was authorized, or access remains blocked: stop, mark the pass `VERIFICATION NOT
RUN`, and escalate to the caller with what happened and what is needed. Auth
blockers are pre-verification blockers — they consume no iteration budget.
