# Authoring a hook

Use this reference when writing a hook, or when deciding whether something needs
enforcing at all. A hook runs a command, HTTP request, prompt or subagent when Claude
Code reaches a lifecycle event. It fires whether or not Claude thinks it should.

**That guarantee is the only reason to choose a hook.** Everything a hook can express,
an instruction can also express — less reliably, and at a context cost. Pick a hook
when "usually followed" is not good enough.

## 1. Before writing one

"Claude keeps ignoring this" has four causes, and only the last is a hook. Check in
order:

1. **It never loaded.** Run `/context` first. This is by far the most common cause.
2. **It is too vague to evaluate.** "Format properly" cannot be checked; "use 2-space
   indentation" can.
3. **Something contradicts it**, so the model is choosing the other instruction.
4. **It genuinely must hold every time** — now write a hook.

A hook written for cause 1 adds machinery and fixes nothing.

## 2. The events

Roughly thirty exist. These are the ones most hooks use:

| Event | Fires | Can block |
| --- | --- | --- |
| `PreToolUse` | Before a tool call runs | **Yes** |
| `PostToolUse` | After a tool call succeeds | No |
| `PostToolUseFailure` | After a tool call fails | No |
| `UserPromptSubmit` | A prompt is submitted | **Yes** |
| `SessionStart` | Session begins or resumes | No |
| `SessionEnd` | Session terminates | No |
| `Stop` | Claude finishes responding | **Yes** |
| `SubagentStart` / `SubagentStop` | A subagent spawns / finishes | Stop only |
| `PreCompact` / `PostCompact` | Around context compaction | Pre only |
| `InstructionsLoaded` | `CLAUDE.md` or a rule file loads | No |
| `FileChanged` | A watched file changes on disk | No |

Two worth knowing for reasons other than enforcement: **`InstructionsLoaded`** logs
exactly which instruction files loaded, when and why — it is the right tool for
debugging a path-scoped rule that appears to do nothing. **`Stop`** receives the
transcript path, so it can review the session that just happened.

## 3. Matchers

Tool events (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`,
`PermissionDenied`) match on tool name. Other events match on their own dimension —
`SessionStart` on how the session started, `PreCompact` on `manual` or `auto`,
`SubagentStart` on agent type.

| Matcher | Evaluated as |
| --- | --- |
| `"*"`, `""`, or omitted | Everything |
| `"Bash"` | Exact tool name |
| `"Edit\|Write"` | List — `\|` or `,` separated |
| `"mcp__memory__.*"` | Anything containing a regex metacharacter is an unanchored regex |

The last row is a real trap: a matcher you meant as a literal becomes a regex the
moment it contains a metacharacter. MCP tools are named `mcp__<server>__<tool>`.

## 4. Where hooks are registered

| Location | Scope |
| --- | --- |
| `.claude/settings.json` | The project — commit it |
| `.claude/settings.local.json` | You, this checkout — gitignored |
| `~/.claude/settings.json` | You, everywhere |
| `<plugin>/hooks/hooks.json` | Wherever the plugin is enabled |
| Skill or subagent frontmatter | Only while that skill or subagent is active |

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/lint.sh", "args": [] }
        ]
      }
    ]
  }
}
```

In a plugin, the file is `hooks/hooks.json` at the plugin root — **not** inside
`.claude-plugin/` — and paths use `${CLAUDE_PLUGIN_ROOT}`. Use the exec form, with
`args` present, whenever a path placeholder appears in the command.

Handler types: `command`, `http`, `mcp_tool`, `prompt` (a fast-model judgement), and
`agent` (a subagent). Useful options include `timeout`, `async`, and `if` for filtering
on tool input, such as `"if": "Bash(git *)"`.

## 5. Blocking

- **Exit 0** — success. On `UserPromptSubmit` and `SessionStart`, stdout is visible to
  Claude; elsewhere it goes to the debug log. Print JSON for structured control.
- **Exit 2** — blocks, on events that support blocking. The reason comes from the JSON
  decision or from stderr.
- **Anything else** — non-blocking; the action proceeds.

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Destructive command blocked by hook"
  }
}
```

`continue: false` with a `stopReason` halts the turn entirely. `additionalContext`
feeds text back for Claude to read — which is how a linting hook turns its output into
something Claude can act on.

## 6. Write hooks that fail safely

A hook runs on every matching event, so its failure modes are everyone's failure modes.

- **Default to allowing.** A hook that errors should exit 0 and let the action through,
  unless blocking on failure is the actual intent. A crash that silently denies every
  `Bash` call is very hard to diagnose from the other side.
- **Keep it fast.** It runs inline on every match. Set `timeout`, or use `async` for
  work nobody is waiting on.
- **Say why.** The `permissionDecisionReason` is the only thing the user and Claude see.
  "Blocked by policy" wastes the one channel you have.
- **Do not trigger interactive prompts or dialogs.** A hook that waits for input blocks
  the session.

## 7. Verify

1. Run `/hooks` to confirm it is registered, with the matcher and source you expect.
2. Trigger the event deliberately and check it fired — `claude --debug` shows hook
   stdout and stderr.
3. Test the **negative** case: something the matcher should *not* catch. An overly broad
   matcher is the most common hook defect, and it only shows up as friction later.

## Sources

Claude Code documentation, verified 2026-08-17:

- [Hooks reference](https://code.claude.com/docs/en/hooks) — the full event schemas,
  JSON input and output formats, and handler types
- [Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide) — the
  walkthrough, if you have not written one before

**The event table in §2 is a subset and it will go stale first.** Around thirty events
exist; the table lists the eleven most hooks use, and both the set and which of them
can block change with releases — check the reference before relying on an event not
listed here. The matcher semantics in §3 and the exit-code behaviour in §5 are equally
version-sensitive. Where the documentation disagrees with this reference, **the
documentation is right** — treat a mismatch as a signal to update this file, not as a
defect in the tool.
