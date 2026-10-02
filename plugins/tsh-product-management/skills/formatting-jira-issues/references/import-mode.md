# Import mode: Jira to local

An alternative entry point to the skill. Instead of formatting extracted tasks, it
fetches existing Jira issues and converts them into `jira-tasks.md` with keys
pre-populated, so an existing backlog can be iterated on locally.

Import is **read-only**. No write tool is needed and Gate 2 does not apply — it
applies later, when local changes are pushed back.

## Step I-1 — Identify the import target

Accept any of:

- a **project key** (`PROJ`) — all epics and their linked stories,
- **specific epic keys** (`PROJ-10, PROJ-15`) — those epics and their children,
- a **JQL query** — whatever it matches.

If the user has not said, ask once (`header: "Import"`, options `Whole project` /
`Specific epics` / `JQL query`).

## Step I-2 — Fetch the issues

Using the Atlassian read tools available in the session:

1. Fetch the targeted epics and stories.
2. For each epic, fetch its child stories via the parent field.
3. Collect Summary, Description, Acceptance Criteria, Priority, Labels, Issue Key,
   Parent link and Status.

## Step I-3 — Map Jira fields to the benchmark template

| Jira field | Template field | Notes |
| --- | --- | --- |
| Summary | Title (Summary) | Direct |
| Description | Description sections | Parse into the structured sections — Overview/Value/Metrics for epics, Context/User Story/Requirements/Technical Notes for stories. Restructure an unstructured description as closely as the template allows. |
| Priority | Priority | Direct (Highest/High/Medium/Low) |
| Labels | Labels | Direct |
| Issue Key | Jira Key | Populate directly (`PROJ-123`) |
| Parent link | Parent epic reference | Map to the parent epic title |
| Story Points | Story Points / Sizing Guidance | Include when estimated, otherwise TBD |
| Status | Status | Direct. This is what enforces the Protected Status Policy. |

Flag any description that cannot be cleanly restructured **in the generated file**
and collect the flags — never one popup per flagged task. They are presented in
batches of up to 4 at step I-5.

**Protected status on import.** After mapping, check each task's status. Done,
Cancelled or PO APPROVE → mark the task read-only with a `🔒` **in its `###`
heading**, directly after the title, and preserve its content exactly as fetched.
The placement matters: the write guard parses task blocks and reads the marker
from the heading (the protected `Status` value alone also protects the block).
Protected tasks are imported for visibility and must never be modified locally or
pushed back.

## Step I-4 — Generate `jira-tasks.md`

Write every imported task in the benchmark template format, each with its real
`Jira Key` populated.

## Step I-5 — Review from the file

An imported backlog can be 50+ issues, so review from the generated file rather
than a popup per task.

1. Summarize in chat: total imported, epics and stories, how many are `🔒`
   protected, and how many descriptions could not be cleanly restructured.
2. Ask one `AskUserQuestion` (`header: "Import"`): `Looks good` /
   `I'll check the file` / `Walk me through the flagged ones` /
   `Re-import with different scope`.
3. On "walk me through", present only the flagged tasks, batched up to 4 per call.

## Step I-6 — Save

Save to `specifications/<workshop-name>/jira-tasks.md`.

After import, local edits follow the per-change modification flow in
[`pushing-to-jira.md`](./pushing-to-jira.md) — each change asks whether to push it
now — or wait for a batch push under the standard Gate 2 approval.
