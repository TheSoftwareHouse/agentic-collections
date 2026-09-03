# Report format

Return a Markdown report that always contains every section below, in this order,
even for `VERIFICATION NOT RUN`. Never return an empty response: when the flow is
blocked before evidence collection, return this full skeleton with explicit unknowns
marked `UNKNOWN` and an explanation of why.

```markdown
## Verification Result: [PASS | FAIL | VERIFICATION NOT RUN]

### Component

[component or section name]

**Confidence:** [HIGH | MEDIUM | LOW]

### Sources

- Figma URL: [exact URL or UNKNOWN]
- Verified page URL: [exact full pinned URL or UNKNOWN]

### Artifact Directory

- Path: [exact `specifications/.../iteration-<N>/` path or UNKNOWN]

### Artifact Status

| Artifact             | Status                    | Path or blocker          |
| -------------------- | ------------------------- | ------------------------ |
| figma-expected.png   | [present/missing/blocked] | [shared path or blocker] |
| actual.png           | [present/missing/blocked] | [path or blocker]        |
| computed-styles.json | [present/missing/blocked] | [path or blocker]        |
| a11y-snapshot.yml    | [present/missing/blocked] | [path or blocker]        |

### Differences

| Property         | Expected (Figma)    | Actual (Implementation) | Severity            |
| ---------------- | ------------------- | ----------------------- | ------------------- |
| [prop or `NONE`] | [expected or `N/A`] | [actual or `N/A`]       | [severity or `N/A`] |

### Clarification Needed

- [content/data differences that may be intentional, or `NONE`]
- [the question: should the observed values remain, or match Figma exactly?]

### Blocker Resolution

- Blocker Type: [none or the specific blocker]
- Blocking Step: [verification process step number or `NONE`]
- Next Required Action: [specific next step for the caller]

### Recommended Fixes

- [specific fix with exact values, or `NONE`]
```

Rules:

- Never omit `Verification Result`, `Component`, `Artifact Directory`,
  `Artifact Status`, or `Blocker Resolution`. If a value cannot be known, write
  `UNKNOWN` and explain why.
- **List ALL differences found across ALL verification categories.** Do not drop
  lower-severity items because critical ones exist — the engineer needs the complete
  list to fix everything in one iteration.
- Include exact values from both Figma and the implementation for every difference.
- When `Clarification Needed` is used, keep the overall result `FAIL` until the user
  confirms the content/data differences are acceptable, and do not promote those
  items into `Recommended Fixes` before that confirmation.
- `VERIFICATION NOT RUN` is used only when capture is missing or blocked. It is not
  a pass, not a clean fail, and never a gate pass. The required action is to obtain
  the live-capture artifacts or resolve the blocker, then rerun verification on
  fresh artifacts.
