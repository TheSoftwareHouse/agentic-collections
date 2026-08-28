# Choosing a session

Read this before the first invocation. Choosing the wrong session produces a confident,
well-formatted dump about work nobody asked about — and because a dump looks complete,
the mistake is not visible until the maintainer has already read it.

## The tool

`${CLAUDE_PLUGIN_ROOT}/skills/session-dump/scripts/session-dump.mjs`, run with `node`.
No dependencies, no execute bit, no install step. It streams; a 1.1MB transcript
packages in well under a second.

**Two invocations, maximum.** One `--list` to choose, one `--dump` to write. If either
fails, report the failure's first line and stop. Do not hand-roll `cat`, `jq`, `grep` or
a scratch script around a failure: those routes produce an unredacted, unversioned file,
which is the one outcome this skill exists to prevent.

### Step A — list what is available

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/session-dump/scripts/session-dump.mjs" --list
```

Sessions resolve from the working directory **and every Git worktree attached to the same
repository** — a worktree gets its own project directory keyed on its path, so work done
in the main checkout is otherwise invisible from inside one.

Each entry carries the timestamp, size, user-turn count, whether the session was
compacted, and its opening message. Pass `--exclude-current <session-id>` when you know
the running session's id.

**Show the sender the shortlist and let them pick.** Two discriminators are worth
pointing out when they hesitate:

- **The tool-failure count.** A session with failures is usually the one they remember,
  because a failure is what they noticed.
- **The user-turn count.** One turn and several hundred KB is a single delegated task,
  not the conversation where they argued with a skill.

Useful flags: `--cwd <path>` to resolve a different repository, `--limit <n>` to see past
the 20 most recent, `--project-dir <path>` to name a directory outright.

### Step B — write the dump

```bash
node "${CLAUDE_PLUGIN_ROOT}/skills/session-dump/scripts/session-dump.mjs" \
  --dump <session-id> \
  --note "<the sender's own account of what went wrong>" \
  --sender "<name or chat handle>" \
  --focus "<the thread that matters, if narrower than the session>"
```

Default destination: `session-dumps/<date>-<slug>.dump.md`, relative to the working
directory, created if it does not exist. `--out <file>` overrides it.

**Not `docs/`.** A dump is not documentation: it is untracked working material with a
short life, and filing it beside real documents invites it into a commit. **Not
`.claude/` either** — Claude Code treats that directory as sensitive and refuses writes
into it even under `acceptEdits`, so a dump targeted there fails at the last step with
the whole session already read.

## Narrowing with a focus

`--focus` records what part of the session matters, in the header, for the reader. It is
a label, not a filter: the conversation section still covers the whole session, because
a maintainer usually needs what happened *before* the problem in order to explain it.

If the sender wants a genuinely narrower artifact, the honest move is a shorter session —
dump the one where the problem happened, not the ten-hour one it happened inside.

## Size, and what gets cut first

The default ceiling is 120,000 characters, which comfortably fits a maintainer's context
in one read. The conversation is rendered last and trimmed **from the middle** when the
budget runs out, because a session's opening and closing turns carry the most signal, and
the file declares how many turns were cut.

| Flag | Default | Raise it when |
| --- | --- | --- |
| `--max-chars` | 120000 | The file reports omitted turns and the omission matters |
| `--turn-chars` | 600 | A truncated user turn is the evidence, and the point is past the cut |
| `--reply-chars` | 300 | What Claude *said* is the problem, not what it did |
| `--error-chars` | 400 | A failure's message is cut before the part that names the cause |
| `--max-errors` | 12 | The session failed repeatedly and the later failures differ from the first |

Raise one flag at a time and only in response to something the file actually reported.
A larger dump is not a better one, and every character of it is content the sender has to
review before sending.

## When the script fails

Report the failure's first line and stop. The script's own failures are one line each —
no matching project directory, no such session, permission denied. A missing `node`, or a
missing script because the plugin is not installed, is the interpreter's error instead;
take its first line the same way.

There is no partial-credit path here. Unlike a retrospective, which can fall back to the
conversation in context, a dump has nothing useful to produce without the transcript —
and the fallback a maintainer would actually want is the sender describing the problem in
their own words, in chat, which needs no tooling at all. Offer that instead.
