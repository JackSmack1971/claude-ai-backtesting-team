# Handoff Contract

Canonical source for the compact handoff structure every `bt-*` agent uses. This
file consolidates what was previously duplicated verbatim in all 12 agent
files (`## Output / handoff` section) — the duplicated copies remain in each
agent for at-a-glance readability, but this file is the single source of
truth if they ever drift.

## Structure

```markdown
## Handoff
- From: <this agent>
- To: <next agent>
- Objective: <single objective>
- Repository/Git state: <commit/tree identity or unavailable>
- Protocol/artifact identity: <paths/digests/config ids or unavailable>
- Inputs inspected: <paths/data/source refs>
- External sources consulted: <titles/URLs when methodological claims depend on them>
- Assumptions: <explicit list or none>
- Findings: <evidence-bound findings>
- Validation performed: <commands/checks/reviews>
- Unresolved risks: <list or none>
- Artifacts produced: <paths or none>
- Authorized next action: <specific action or none>
- Status: PASS | FAIL | INCONCLUSIVE | BLOCKED
```

## Status semantics

- **PASS** requires affirmative evidence for this role's gate, not absence of detected problems.
- **INCONCLUSIVE** is mandatory when evidence is insufficient or conflicting.
- **BLOCKED** means a required prerequisite is unavailable.
- **FAIL** means a required check was performed and failed.

## Rules

1. Never reinterpret another agent's `FAIL`/`INCONCLUSIVE`/`BLOCKED` as approval.
2. Never authorize a next action outside the issuing agent's own authority.
3. `Protocol/artifact identity` should reference a `reproducibility-manifest`
   run's `manifest_hash` (or equivalent) when one exists, not a free-text
   description alone.
4. `Repository/Git state` should record `unavailable` explicitly rather than
   being omitted, when no repository exists (e.g., `FOUNDATION_MODE`).
