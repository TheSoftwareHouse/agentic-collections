# Pushing to Jira, verifying, and refreshing the baseline

Everything here belongs to the orchestrator running in the main conversation. A
subagent has no Atlassian tools and no write tools: it produces the formatted
content, a sync summary or a verification diff, and stops.

All Jira access goes through the Atlassian MCP server available in the session.
**Discover the exact tool names before the first push rather than assuming them** —
they vary by server version, and a name that never matches fails silently. Read
tools (fetch issue, search by JQL, list resources) are safe at any point; write
tools must not be called before Gate 2 is recorded.

## Step 8 — Push approval (Gate 2)

Confirm with the user, **one question per `AskUserQuestion` call** — these are gate
decisions, not field-level clarifications:

- the target Jira project key,
- the target board or backlog,
- whether to create everything at once or in batches,
- any final adjustments.

This is the final gate. **Record the approval before calling any Jira write tool**,
in `specifications/<workshop-name>/.gates.md`:

```markdown
| 2 | jira-tasks.md | approved | 2026-08-19 14:32 — project ACME, batch push |
```

A `PreToolUse` hook reads that row and denies Atlassian write calls while it is
unapproved. If a write is blocked, do not work around it: check the ledger, and if
the gate genuinely has not been approved, go back and get approval.

## Step 9 — Create or update issues

Present a **sync summary** first and get explicit approval:

- **(a) CREATE** — tasks whose `Jira Key` is `—`: titles and count.
- **(b) UPDATE** — tasks with a key whose status is not protected: titles, keys, count.
- **(c) SKIPPED** — tasks with a key whose status is Done, Cancelled or PO APPROVE:
  titles, keys, statuses, count.

**Creating:**

1. Create all **epics** first, to obtain their Jira IDs.
2. After each epic is created, **immediately** write its returned key back into
   `jira-tasks.md` — do not batch the write-back until the end.
3. Create the **stories**, linked to their parent epics.
4. Write each story's key back immediately, the same way.
5. Add the links between stories (blocked-by, related-to).

**Updating:**

1. Check the task's status first. Done, Cancelled or PO APPROVE → skip it entirely;
   it was already counted under (c).
2. Update Summary, Description, Acceptance Criteria, Priority and Labels.
3. Do **not** change Issue Type or the parent link unless the user explicitly asks
   for re-linking.
4. If an update fails because the issue no longer exists, tell the user and offer to
   create a new one instead.

Report the final state: every key now in `jira-tasks.md`, and what was created,
updated and skipped with statuses.

## Step 10 — Post-push verification

Read the issues back from Jira and verify, per task: summary/title, parent epic
linkage for stories, acceptance criteria present, the relevant description
sections, and the current status. Surface any mismatch plainly — the push is not
"verified" until differences are resolved or the user explicitly accepts them.

## Step 11 — Archive and refresh the baseline

Once verification succeeds:

- Archive the session artifacts under
  `specifications/projects/<project-name>/sessions/<YYYY-MM-DD>-<workshop-name>/`.
  Use the workshop name as the project key when no explicit project name exists.
- Refresh `specifications/projects/<project-name>/task-baseline.md`, treating
  `Jira Key` as the primary identity: replace same-key entries with the latest
  synced content and status, add entries for newly pushed tasks, and leave Jira as
  the external source of truth.

If any creation or update fails at any point, tell the user immediately and ask how
to proceed.

## Per-change modification flow

When the user changes one task outside the main workflow ("add acceptance criteria
to Story 2.3", "change the priority of Epic 1"):

0. **Check the status.** Done, Cancelled or PO APPROVE → refuse and explain: *"This
   task has a protected status ([status]). Tasks with status Done, Cancelled, or PO
   APPROVE cannot be modified. If this status is incorrect, please update it in Jira
   first, then re-import."* Do not apply the change locally either. Stop.
1. **Update `jira-tasks.md` first.**
2. **Ask once** (`header: "Push now?"`), options `Push now` / `Keep local`.
3. **On "push now"** — update that issue by its key. A single-task push still
   requires Gate 2 in `.gates.md`; if it is not there, record the user's explicit
   approval for this task before the call. If the task has no key yet (`—`), say so
   and offer to create it.
4. **On "keep local"** — the change waits in `jira-tasks.md` for the next batch push.
