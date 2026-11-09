# Dependency triage

A vulnerability advisory is a claim about a package, not about your service. The job is
to turn a scanner's list into a ranked set of actions, and the ranking is **reachability
and exploitability first, CVSS score second**. A critical-scored advisory in code you
never call is lower priority than a medium one on your request path.

Run only the scanner the project already has. Never install one to produce a number.

## The read-only scanner per ecosystem

Each of these reads the manifest or lockfile and reports; none changes a file. Use the
one whose lockfile is present.

| Ecosystem | Lockfile | Read-only audit command |
| :-- | :-- | :-- |
| npm | `package-lock.json` | `npm audit --json` |
| pnpm | `pnpm-lock.yaml` | `pnpm audit --json` |
| Yarn (Berry) | `yarn.lock` | `yarn npm audit --all --recursive --json` (`--recursive`/`-R` includes transitive dependencies; without it only direct ones are checked) |
| Python (pip) | installed env, or pinned `requirements*.txt` | `pip-audit` audits the installed environment read-only. For a requirements file, `pip-audit -r requirements.txt --no-deps` — plain `-r` resolves the file like `pip install` and can run package code, which is not a read-only audit |
| Python (Poetry/uv) | `poetry.lock`, `uv.lock` | `pip-audit` against the installed env, or `osv-scanner --lockfile=poetry.lock` (static — resolves nothing, runs nothing) |
| PHP | `composer.lock` | `composer audit --format=json` |
| Go | `go.sum` | `govulncheck ./...` (reachability-aware by design) |
| Rust | `Cargo.lock` | `cargo audit` |
| Any / multi | any supported lockfile | `osv-scanner --lockfile=<file>`, or `trivy fs --scanners vuln <dir>` |

`govulncheck` is the outlier worth noting: it analyses call graphs, so it reports only
advisories your code can actually reach. Treat its output as already reachability-filtered.

A resolving audit is not a read-only one. Any mode that resolves a manifest to decide
what to check — `pip-audit -r` without `--no-deps`, an install step before a scan —
runs package code and may mutate the environment. Audit the already-installed or locked
state instead; it is both safe and what ships.

When **no** scanner is installed for an ecosystem, say so in the report's "Not checked"
section. Do not install one, and do not hand-guess a CVE list — a code-only audit is
honest; a fabricated scan is not.

## The triage model

For each advisory the scanner reports, answer four questions in order and stop early
when the answer settles the rank.

1. **Reachable?** Does the service actually call the vulnerable code path? Answer it by
   tracing a real execution path — through the build and CI pipeline as well as the
   running service — not by the absence of a direct `import`. A package you never import
   directly can still be reached through another dependency, and a `devDependencies` tool
   (a bundler, a test runner, a dev server) processes untrusted input in CI and on
   developer machines — the Vite dev-server advisories are the worked example — so it is
   not out of reach by virtue of being dev-only. Record **not reachable** only when you
   have shown there is no path. Where you cannot establish one either way, record
   **unknown** and keep the advisory at the scanner's severity — unknown is not Low.
2. **Exploitable in this context?** A reachable advisory still needs the attacker's
   input to arrive at it. A ReDoS in a parser you only ever run on your own config is
   not exploitable; the same parser on request bodies is. A prototype-pollution gadget
   matters only if untrusted data reaches the sink. Decide whether a realistic attacker
   input reaches the vulnerable code.
3. **Severity — by consequence.** Only now weigh impact: remote code execution and auth
   bypass over data exposure over denial of service over information leak. The advisory's
   CVSS is an input, not the answer; a reachable, exploitable RCE outranks a
   higher-scored but unreachable one.
4. **Action.** The smallest step that removes the risk:
   - **Upgrade** to the fixed version when one exists — the default.
   - **Override / resolution** (npm `overrides`, pnpm `overrides`, Yarn `resolutions`,
     Poetry constraints) to force a fixed transitive version when the direct dependency
     has not released.
   - **Mitigate** when no fix exists — disable the feature, validate at the boundary so
     the input never reaches the sink, or drop the dependency.
   - **Accept and record** only when you have shown the advisory is not reachable or not
     exploitable, with the path reasoning and the condition that would change it.
     Unproven reachability is not grounds to accept — an advisory you could not trace
     stays at the scanner's severity.

## Severity mapping for the report

| Severity | Dependency case |
| :-- | :-- |
| Critical | Reachable, exploitable, remote code execution or authentication bypass on a production path |
| High | Reachable and exploitable, significant impact (data exposure, privilege escalation), or a fixed version is available and not yet applied on a request path |
| Medium | Reachable but not clearly exploitable, or exploitable only behind authentication; a fix exists |
| Low | Shown to have no execution path to the vulnerable code, or no realistic attacker input reaches it — with the path reasoning recorded. Dev-only is not Low on its own |

When reachability is **unknown** — you could not trace a path and could not rule one out
— the advisory keeps the severity the scanner assigned. "I did not find a caller" is
not "there is no caller".

## Reporting

Put the triaged advisories in the audit's **Dependencies** table, one row each:

```markdown
| Package@version | Advisory | Reachable? | Exploitable? | Severity | Action |
| lodash@4.17.19 | GHSA-xxxx (proto pollution) | yes — merge() on the request body | yes | High | Upgrade to 4.17.21 |
| esbuild@0.19.0 | GHSA-yyyy (dev-server request) | unknown — dev dependency, CI path not traced | assume yes | Medium (scanner) | Upgrade to 0.19.12 |
| tar@6.1.0 | CVE-2024-nnnn (path traversal) | no — only the build reads it, from a trusted local path (traced) | n/a | Low | Accept; revisit if it ever reads an uploaded archive |
```

Rules that keep the table honest:

- **Reachability and exploitability are your judgement, shown.** State the path in a few
  words so the reader can check it, not just "yes"/"no".
- **Separate measured from assessed.** The scanner measured the advisory; you assessed
  reachability. Do not present your assessment as the scanner's output.
- **Consolidate.** Forty advisories from one abandoned transitive package are one
  finding with the list and one action, not forty rows.
- **Name the ecosystems you could not scan** in "Not checked", so the absence of
  findings for them is never read as a clean result.
