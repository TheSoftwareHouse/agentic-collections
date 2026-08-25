# Jira Task Benchmark Template

This document defines the expected structure and fields for Jira epics and stories created by the business analyst agent.

---

## Epic Template

### Fields

| Field | Required | Description |
|---|---|---|
| Summary | Yes | Short, descriptive title. Format: `<Domain Area>: <Business Capability>` |
| Issue Type | Yes | `Epic` |
| Description | Yes | Structured description (see format below) |
| Acceptance Criteria | Yes | Business-oriented verifiable conditions |
| Priority | Yes | Highest / High / Medium / Low |
| Labels | No | Domain or feature area labels relevant to the project |
| Jira Key | No | Jira issue key (e.g., PROJ-123). Populated after issue creation or import. |
| Status | No | Current Jira workflow status (e.g., To Do, In Progress, Done). Populated from Jira during import or after push. Used to enforce the Protected Status Policy — tasks with a protected status are read-only. |

### Description Format

```
h2. Overview

<2-3 sentence description of what this epic delivers and why it matters>

h2. Business Value

<What business problem does this solve? What value does it create for users or the organisation?>

h2. Success Metrics

* <Measurable outcome 1>
* <Measurable outcome 2>
```

### Acceptance Criteria Format

```
(/) <Verifiable business condition 1>
(/) <Verifiable business condition 2>
(/) <Verifiable business condition 3>
```

---

## Story Template

### Fields

| Field | Required | Description |
|---|---|---|
| Summary | Yes | Short, action-oriented title. Format: `<User/Actor> can <action>` |
| Issue Type | Yes | `Story` |
| Parent | Yes | Reference to parent Epic |
| Description | Yes | Structured description (see format below) |
| Acceptance Criteria | Yes | Checklist of verifiable conditions |
| Priority | Yes | Highest / High / Medium / Low |
| Labels | No | Inherited from epic + story-specific labels |
| Story Points | No | Team estimates during refinement. Agent provides sizing guidance: Small (1-3), Medium (5-8), Large (13+) |
| Jira Key | No | Jira issue key (e.g., PROJ-123). Populated after issue creation or import. |
| Status | No | Current Jira workflow status (e.g., To Do, In Progress, Done). Populated from Jira during import or after push. Used to enforce the Protected Status Policy — tasks with a protected status are read-only. |

### Description Format

```
h2. Context

This story is part of the [<Epic Title>] epic. <1 sentence connecting this story to the epic's goal.>

h2. Source Context

<Short traceability note pointing back to the workshop material, intent brief, or baseline entry that produced this story.>

h2. User Story

As a <role>, I want <capability> so that <benefit>.

h2. Requirements

# <Specific requirement 1>
# <Specific requirement 2>
# <Specific requirement 3>

h2. Technical Notes

<High-level technical considerations discussed during the workshop. Write "No specific technical considerations discussed." if none were mentioned.>
```

### Acceptance Criteria Format

```
(/) <Verifiable condition 1>
(/) <Verifiable condition 2>
(/) <Verifiable condition 3>
```

Scenario-style criteria are also valid when written as `(/) GIVEN ... WHEN ... THEN ...`.

---

## Formatting Guidelines

### General Rules

- **Business language only**: Descriptions should be understandable by any stakeholder without technical knowledge
- **No implementation details**: Do not specify technologies, frameworks, or code patterns in stories — that is the architect's responsibility
- **Consistent tone**: Use active voice and present tense ("User can create…" not "User should be able to create…")
- **Verifiable acceptance criteria**: Every criterion must be testable with a clear pass/fail condition
- **Traceability**: Keep source context concise but present so the Jira issue can be compared back to the extracted task during post-push verification

### Priority Mapping

| Workshop Priority | Jira Priority | When to Use |
|---|---|---|
| Critical | Highest | Blocks all other work; must be done first |
| High | High | Core functionality; needed for MVP |
| Medium | Medium | Important but not blocking; can follow MVP |
| Low | Low | Nice-to-have; can be deferred |

### Labels

Labels are project-specific. Suggest labels based on the epic's domain area, but do not hardcode values. Common patterns:
- Feature area: `auth`, `payments`, `dashboard`, `reporting`
- Type: `infrastructure`, `integration`, `ui`, `backend`
- Source: `workshop-<date>` to track which workshop produced the task

### Handling Optional Fields

- If a field cannot be filled from the available materials, mark it as `TBD - to be discussed during refinement`
- Do not invent information to fill optional fields
- Flag all `TBD` fields for user review

### Jira Key Field

The `Jira Key` field is empty (`—`) when the task has not yet been pushed to Jira. It is populated automatically after issue creation or when importing existing Jira issues. When a Jira key is present, the push flow will **update** the existing issue instead of creating a new one.

- Do not manually fill this field — it is managed by the agent
- After a successful push, the agent writes the Jira key back into `jira-tasks.md`
- After a successful import, the agent populates the Jira key from the fetched issues

### Status Field

The `Status` field reflects the current Jira workflow status of the task (e.g., `To Do`, `In Progress`, `Done`, `Cancelled`, `PO APPROVE`). It is empty (`—`) for tasks that have not been pushed to or imported from Jira.

- Do not manually fill this field — it is managed by the agent
- After a successful import, the agent populates the Status from the fetched Jira issue
- After a successful push (create or update), the agent records the current status returned by Jira
- Tasks whose status is **Done**, **Cancelled**, or **PO APPROVE** are considered **protected** and are treated as read-only. The agent will not modify their content locally or push updates to Jira for them. See the Protected Status Policy in the orchestrating-business-analysis skill for full details.

### Marking a protected task

A protected task carries the `🔒` marker **in its `###` heading**, directly after
the title — see Story 1.4 in the worked example. This placement is load-bearing,
not cosmetic: the Jira write guard parses `jira-tasks.md` task blocks, and it
treats the `Jira Key` of a block as immutable when the block's heading carries
`🔒` **or** its `Status` line names a protected status. Either signal alone
protects the task; the marker exists so a human scanning the file sees it too.

---
