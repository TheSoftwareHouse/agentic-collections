# Reproducing failures

Load this when the bug does not reproduce on the first attempt, reproduces in only one
environment, or when it is unclear which test layer can express it. The goal is the
same in every case: a reliable trigger you can run on demand. Until you have one, any
change you make is unverifiable.

## 1. It fails there, not here — close the gap

A bug that reproduces in one environment and not another is caused by something that
differs between them. List the differences and eliminate them one at a time, starting
with the cheapest to check:

| Difference | How to check |
| --- | --- |
| Code version | Compare the deployed commit or artifact with your checkout. A fix already on `main` is not a reproduction failure. |
| Dependency versions | Compare lockfiles, container image digests, runtime version (`node --version`, `python --version`). A floating range resolved differently is a classic cause. |
| Configuration | Diff the environment variables, feature flags and config files the code path reads. Secrets differ by design; check only that they are present and well-formed. |
| Data | The failing record, tenant or user is often the trigger. Get its identifier from the ticket or logs and reproduce against an equivalent — never against the production row itself. |
| Load and timing | Concurrency, retries and timeouts behave differently under real traffic. See §3. |
| Platform | OS, locale, time zone, file-system case sensitivity, CPU architecture. |

Record which difference turned out to matter — it usually *is* the root cause, or
points straight at it.

## 2. Data-dependent bugs — find the shape, not the row

When the bug triggers only for certain input, the reproduction needs the input's
**shape**, not the production record itself:

1. Get the failing input from logs or the ticket, redacting anything personal.
2. Strip it down: remove fields and shorten values until the failure stops, then put
   back the last thing removed. What remains is the trigger.
3. Name the property that matters — an empty list, a null in an optional field, a
   Unicode character, a boundary value, a date across a DST change.
4. Build that shape as test data in the project's own fixtures or factories.

Never copy production data into a test or a fixture file. A redacted, minimal shape
is a better test anyway: it states the trigger instead of hiding it.

## 3. Timing-dependent bugs — make the race deterministic

Intermittent failures are almost always ordering problems: two operations whose
relative timing is not guaranteed. To reproduce one:

- **Run it many times.** Loop the suspect test — a shell loop, or the runner's own
  repeat option where it has one — and measure the failure rate. A fix is only
  verified when the same loop runs clean.
- **Control the clock.** Replace real time with the test framework's fake timers, so
  timeouts and schedules fire when the test says, not when the machine does.
- **Force the interleaving.** Insert a deterministic pause or a latch at the suspect
  point in the test double, so the bad ordering happens every time.
- **Check shared state.** Module-level caches, singletons, a database row two tests
  both write, and test order dependence. Running the failing test alone versus with
  the full file tells you quickly.

## 4. Choosing the test layer

Write the reproduction at the **lowest layer that exhibits the bug**:

| The fault is in | Test layer |
| --- | --- |
| Pure logic: a calculation, a mapping, a validation rule | Unit |
| A query, a transaction, a migration, serialization across a boundary, a queue or an external service contract | Integration, against the real dependency the project's integration suite already uses |
| The interaction of several services, or behaviour visible only in the browser | End-to-end, following the project's existing E2E setup |

A unit test with the database mocked out cannot reproduce a bug in SQL semantics or
transaction boundaries — it reproduces the mock. If the bug lives at a boundary, the
test must cross it.

Prefer the project's existing test files and helpers for the module over a new file.
The regression test belongs next to the tests a future reader will look at.

## 5. When no automated test can capture it

Some failures resist automation: a bug in infrastructure glue, a third-party outage
pattern, a timing issue you cannot force. Then:

1. Write the **manual reproduction** as numbered steps with exact inputs and the
   expected versus actual result, and put it in the report.
2. Test the **logic** you can isolate — the handler of the third-party error, the
   parser of the odd payload — even if the trigger itself stays manual.
3. Say plainly in the report that the regression guard is partial, and why.

## 6. When it does not reproduce at all

Stop changing code. Report instead:

- the symptom as pinned in step 1,
- every reproduction attempt and its result,
- the environment differences already ruled out,
- the specific evidence that would unblock it — a log line with a correlation ID, the
  failing record's identifier, the exact client version, a timestamp to search around.

If the user agrees, add **targeted, permanent** observability at the suspect path — a
structured log line or a metric that would have shown the cause — and ship that as its
own change. That is progress, and it is honest. A speculative code change labelled as
a fix is neither.
