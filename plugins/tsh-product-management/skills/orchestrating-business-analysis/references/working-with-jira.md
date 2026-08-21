# Working with Jira

Jira access runs through the Atlassian MCP server available in the session. The
`tsh-core` plugin bundles one; a project may also configure its own. **Tool names
vary by server version and by how the server was wired up, so discover the
available tools before the first push rather than assuming their names.** Writing a
fixed tool name into a list or a matcher is how a rule ends up silently never
matching.

Workers hold no Atlassian access at all. When a worker phase needs board context,
issue payloads or read-back data, fetch it yourself and pass it into the prompt.

## Use Atlassian tools for

- Creating epics and stories after Gate 2 approval.
- Linking stories to parent epics after creation.
- Adding relationships between issues (blocked-by, related-to).
- Looking up existing issues to avoid creating duplicates.
- Fetching an existing backlog when the user wants to iterate on it.
- Updating an issue when the user changes a task that already carries a Jira key.

## Do not use them for

- Any write before Gate 2 is recorded in `.gates.md`.
- Creating a duplicate when `jira-tasks.md` already holds a key for that task.
- Updating an issue whose status is protected (Done, Cancelled, PO APPROVE).
- Searching for technical documentation or code.
- Replacing Jira as the source of truth for backlog status or ownership.

## Sequence that keeps a push safe

1. List the accessible Atlassian resources first. If more than one is accessible,
   ask the user which to use.
2. Check every task's `Jira Key` field, and present the sync summary — **created**
   (no key), **updated** (key, unprotected), **skipped** (key, protected status),
   with counts. Get approval.
3. Record Gate 2 in `.gates.md` **before** the first write call. A `PreToolUse` hook
   enforces this and denies the call otherwise.
4. Create epics first to obtain their IDs, then stories linked to them, writing each
   returned key back into `jira-tasks.md` immediately.
5. Check an issue's current status before updating it; skip and report anything
   protected.
6. Read the issues back and verify summary, parent linkage, acceptance criteria,
   description sections and current status before declaring the push successful.
7. On any failure, tell the user immediately and ask how to proceed.

When the user modifies a single task, update `jira-tasks.md` first, then ask whether
to push that change now.

## Jira iteration mode

When the user supplies issue keys, a project key or a JQL query instead of workshop
materials, skip transcript processing and extraction entirely: import through
`formatting-jira-issues`, then run quality review over the imported list and
continue from there. Import is read-only and Gate 2 does not apply to it — it
applies when local changes are pushed back.

Quality review is worth running on an imported backlog: it finds the same lifecycle,
edge-case and notification gaps in an existing backlog that it finds in a new one.
