# Redacting before sharing

Read this before telling the sender the file is ready. A dump is the one artifact in this
plugin that **leaves the machine**, and the cost of getting it wrong is not a bad
document — it is a credential in a chat history that cannot be unsent.

## What the script replaces

Redaction runs over every string before anything is written to disk: user turns,
assistant replies, tool signatures, error text and provenance fields alike. Values
matching a known secret shape become `[redacted:<kind>]`, and the file reports the tally.

| Kind | Shape |
| --- | --- |
| `private-key` | A whole `-----BEGIN … PRIVATE KEY-----` block, content and all |
| `aws-access-key-id`, `aws-identifier` | `AKIA…` and the other AWS 20-character prefixes |
| `github-token`, `gitlab-token` | `ghp_`, `gho_`, `ghu_`, `ghs_`, `ghr_`, `github_pat_`, `glpat-` |
| `slack-token` | `xoxb-`, `xoxa-`, `xoxp-`, `xoxr-`, `xoxs-` |
| `google-api-key`, `anthropic-api-key`, `stripe-key`, `api-key`, `npm-token`, `digitalocean-token` | Documented per-vendor prefixes |
| `jwt` | Three base64url segments separated by dots |
| `bearer-token` | `Bearer <16+ characters>` |
| `url-credential` | The password in `scheme://user:password@host`, keeping the rest |
| `assigned-secret` | The value in `…SECRET…`, `…TOKEN…`, `…PASSWORD…`, `…API_KEY…`, `…PRIVATE_KEY…`, `…ACCESS_KEY…`, `…CREDENTIAL…` assignments, keeping the name |

The tally counts every replacement made while rendering, including in turns the
`--max-chars` trim then cut from the middle. So a trimmed dump can report a `kind` that
is no longer in the file. It over-reports rather than under-reports, which is the
direction that keeps the sender reading.

Home-directory paths are separately rewritten to `~`, which also removes the sender's
account name from every path in the file. That is reported as a rewrite, not as a secret
replacement, because it is not one — conflating them would overstate what the scrubber
caught.

**Placeholders survive on purpose.** `API_KEY=${MY_VAR}`, `PASSWORD=<your-password-here>`,
`TOKEN=changeme` and `SECRET=null` are left intact, because an unset variable is very
often the actual bug, and redacting it destroys the evidence that it was unset.

## What it provably cannot catch

The scrubber matches shapes. These are not shapes, and no amount of pattern work makes
them into ones:

- **A secret written as prose.** "the staging password is hunter2" has no shape.
- **An internal hostname, service name or IP range.** Often the most sensitive thing in a
  session, and indistinguishable from any other string.
- **A client's name, or a project name under NDA.** The repository name and branch are in
  the header by design, because a maintainer needs them.
- **A short or low-entropy credential** — a four-digit PIN, a dictionary-word password.
- **A secret in a paraphrase.** If Claude repeated a value back in its own sentence, that
  sentence may carry it in a form no pattern matches.

Deliberately, there is **no** high-entropy heuristic. One would flag every hash, UUID and
base64 payload in the session, mangle them silently, and cost the maintainer the evidence
they came for — while still missing everything in the list above. A scrubber that is
honest about its floor is safer than one that feels thorough.

## The review gate

Mechanical redaction is the floor. **The gate is the sender reading the file.** State it
plainly, every time, and say why in one sentence — not as boilerplate, because a warning
that reads as boilerplate does not get acted on.

What the report must give them:

1. The path, so they can open it.
2. The redaction tally, so they know the scrubber ran and what it found.
3. The declared omissions, so they know what is *not* in there.
4. The instruction to read it before sending — and the reason: pattern matching cannot
   catch prose.

If the sender says they have read it, that is the end of Claude's involvement. Do not
re-audit their judgement, and do not ask twice.

## After it is sent

Two instructions, both for the sender to carry out — this command edits nothing but the
file it wrote.

**Ignore the directory.** `session-dumps/` belongs in `.gitignore`, or in
`.git/info/exclude` where the repository is not theirs to change. A dump is a transcript
sitting in a working tree, so an unignored one is a single `git add -A` from a commit —
the same publication this skill's whole procedure exists to gate, arriving by a route
nobody was watching. Committed, it also survives every later deletion in the history.

**Delete it once sent.** It has no second use: it describes one session at one moment,
and the maintainer has their own copy. A dump left in a working tree is a file whose
review gate has already been passed and will not be applied again.

## When the answer is "do not send this"

Some sessions should not be packaged at all. Say so directly rather than producing a
smaller dump as a compromise:

- The repository is under an agreement that forbids its contents leaving the client's
  environment. A transcript is contents.
- The session's substance *is* the confidential material — a credential rotation, a
  security incident, an unannounced commercial decision.
- The sender does not know what is in the session and does not want to read it. Then it
  cannot be reviewed, and an unreviewed dump is not one that can be sent.

In each case the fallback is the same and is usually enough: the sender describes the
problem in their own words, names the plugin and version, and pastes the single error
message. That needs no dump.

## If a secret is found after the fact

If the sender spots something the scrubber missed, the fix is not a smarter pattern in the
moment. In order: **delete the dump file**, treat the credential as compromised and rotate
it if it ever reached a chat window, and only then consider whether the shape was general
enough to be worth adding to the script — which is a change to this plugin, released
through its own procedure, not an edit made mid-run.
