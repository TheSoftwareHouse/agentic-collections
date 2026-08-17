---
paths:
  - "plugins/tsh-core/**"
---

# Core plugin admission

Read this before adding anything to `tsh-core`. Every other plugin has a claimant and
an affirmative question — *is this QA's job?*, *is this TypeScript?*. `tsh-core` is
the only one defined by a **negation**, and negatively-defined containers accrete by
default. The cost is also externalised: the contributor who could not decide gets a
home for their skill, while every teammate pays listing budget.

## The bar

Admission is by elimination **plus evidence**. All four:

1. **It fails both routing questions.** Not stack — it would not change if the repo
   switched language or framework. Not discipline — it would not change if the reader
   switched job.
2. **Generic is not core.** Core skills are *tool mechanics*: the procedure is
   dictated by the tool's own semantics (`git`, `gh`, the shell), not by TSH's opinion
   about how to work. "Write good commit messages" is generic, applies to everyone,
   and is still a **discipline** skill, because only TSH's opinion could produce it.
   **If you cannot name the tool the skill wraps, it is not core.**
3. **Evidence, not assertion.** The PR names which **three of the five disciplines**
   would invoke it in a normal month. "It's generic" is not evidence.
4. **Ties go to a discipline plugin.** When the answer is arguable, it is not core.

## The two named exceptions, and why the list is closed

`writing-technical-documents` is admitted as the house writing standard despite
wrapping no tool, because every discipline's written deliverables are judged by it.

`managing-decision-records` is admitted for the ADR format and lifecycle only,
because `managing-claude-context` — which passes the name-a-tool test outright,
wrapping Claude Code's memory subsystem — already mandates the decision index and the
status vocabulary. Splitting one artifact system across two install units would leave
a `tsh-core` installer told to keep an index with no guidance on what a record is.

Both are **named rather than generalised**. There is no "output standards" or
"artifact conventions" category to file the next thing under, and creating one is how
the test dies. `managing-decision-records` is the **last** artifact-convention skill
core admits; a third exception makes this a category, which is the failure mode the
test was written to prevent. Commit-message and PR-title conventions are outside both
and remain discipline skills.

Do not treat these two skills' presence in the directory listing as permission to
skip the test.

## No cap — a disclosure instead

**There is no maximum number of skills here.** There is an obligation to state the
cost at the moment someone chooses to pay it.

A PR adding a skill to `tsh-core` reports the plugin's **routing footprint** — the
combined `name`, `description` and `when_to_use` characters across its skills —
before and after.

Claude Code preloads that text for every installed skill in order to route on it.
`description` and `when_to_use` are truncated together at 1,536 characters per skill,
and when the whole listing overflows, descriptions are cut and routing degrades for
*every* skill in *every* plugin, not just the new one. A count of skills never
measured that — three terse skills can cost less than one verbose one. Report the
number, name the three disciplines, and let the reviewer weigh it.

## `tsh-core` is one plugin, not a family

Growth is never a reason to split into `tsh-core-*`. A prefixed family earns its keep
only when there is a variable to instantiate (`tsh-stack-<stack-name>`,
`tsh-<discipline>`), and `tsh-core`'s defining property is depending on no variable.
The only thing that could follow `tsh-core-` is a topic bucket, and a topic is not an
install decision. When this plugin feels heavy, the fix is re-homing what should
never have been admitted.

The name is doing guardrail work, so do not "clarify" it later. `common` and `shared`
are the industry's canonical junk-drawer names because they claim *mere reuse*, which
anyone can truthfully assert about anything. `core` claims *centrality*, which has to
be defended.

## Out of scope by construction

- Language or framework content → a stack plugin
- Role practice and methodology → a discipline plugin
- Company policy, onboarding or handbook prose — that is a document, not a skill
- "Utilities" and one-off automation
- Anything used by a single team or a single repo
