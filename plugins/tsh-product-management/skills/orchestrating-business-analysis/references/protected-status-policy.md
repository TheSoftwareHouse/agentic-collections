# Protected Status Policy

This file is the **single source of truth** for the protected status list. Every
skill and worker in this workflow references it rather than keeping its own copy.
When delegating to a worker whose task touches existing tasks, paste the policy
block below into the delegation prompt verbatim — a worker starts with an empty
context and cannot read this file unless you tell it to.

## The protected statuses

- **Done**
- **Cancelled**
- **PO APPROVE**

A task — epic or story — whose Jira status matches any of these is **immutable**.

## The rules

1. **No local edits.** A protected task must not be edited in `jira-tasks.md` or
   `extracted-tasks.md`. Its content is frozen.
2. **No Jira updates.** No field of a protected issue may be changed through the
   Atlassian tools.
3. **No quality-review suggestions.** Analysis passes exclude protected tasks, and
   any suggestion generated against one is dropped before presentation.
4. **Formatting and push skip them.** List every skipped task and its status in the
   summary so the user can see what was left alone.
5. **Import includes them, read-only.** Protected tasks are imported so the user
   sees the whole backlog, marked with `🔒` in their `###` heading, and are never
   modified or pushed back.
6. **Refuse an override request**, with this wording:

   > This task has a protected status ([status]). Tasks with status Done,
   > Cancelled, or PO APPROVE cannot be modified. If this status is incorrect,
   > please update it in Jira first, then re-import.

7. **Baseline continuity.** A baseline entry reflecting a protected task is
   read-only too, and is not rewritten locally unless Jira itself changes through a
   valid import or push cycle.

## Paste-ready block for delegation prompts

```text
Protected Status Policy — tasks with Jira status Done, Cancelled, or PO APPROVE are
immutable. Exclude them from all analysis, never target them with a suggestion,
never propose an edit to their content, and list any you encountered with their
status under "Protected Tasks Excluded". If you generated a suggestion against one,
drop it before returning.
```
