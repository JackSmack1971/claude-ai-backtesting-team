# Ruleset Research

> **Provenance note:** citations below to `rule-selection.md` / `rule-contract.md` / `ruleset-manifest-contract.md` refer to the `ai-backtesting-team-builder` skill's own bundled authoring-contract docs (used during generation), not to files shipped in this output repository.

Mode: `FOUNDATION_MODE`.

## Candidate discovery

`rule-selection.md` requires every `paths:` glob to be derived from inspected repository topology or an explicit user-provided target path. Phase 1 reconnaissance (see `ARCHITECTURE_RESEARCH.md`) found no repository: no source tree, no data/storage layer, no existing directory structure of any kind. The user's request also named no target path.

Candidate instructions considered and deferred, pending a real repository:

| Candidate instruction | Why it would plausibly qualify later | Why it is deferred now |
|---|---|---|
| "Files under an experiments/results directory are append-only; never edit a past run's recorded metrics in place" | High risk (silent rewriting of historical results is a data-integrity failure), high invariance | No such path exists to scope a glob to — inventing one (e.g., `experiments/**`) would violate rule-selection.md's "do not invent paths" |
| "Files under a holdout/confirmation-data directory must never be read by discovery-stage code paths" | Directly maps to the authority invariant in `team-blueprint.md` (discovery must not see confirmation outcomes) | No holdout path exists yet; this invariant is instead encoded as an agent-level authority rule in `bt-hypothesis-researcher`, `bt-experiment-designer`, and `bt-team-orchestrator`, where it belongs regardless of repository, per the placement test ("independent role/judgment boundary" → subagent, not rule) |
| "Config/protocol files defining an accepted experiment must be treated as immutable once confirmation begins" | Same category as above | Same — no config path exists; encoded at the agent level (`bt-backtest-engineer`, `bt-experiment-integrity-reviewer`) instead, since it is a role-authority boundary, not a mere file convention |

None of these candidates clears the placement test's first requirement — a real, inspected repository path — so none proceeds to scoring. An unscoped (always-resident) rule was also considered and rejected: `rule-selection.md` requires a written universal-scope rationale showing the instruction applies to nearly every Claude Code task in the repository; in FOUNDATION_MODE there is no repository-wide task pattern to justify permanent context residency, and the underlying invariants are already carried by the agent layer (see `team-blueprint.md` authority invariants, restated in each affected agent's `## Non-authority` section).

## Selection score

Not applicable — no candidate reached scoring.

## Decision

Zero rules generated. This is a valid outcome per `rule-selection.md` and `ruleset-manifest-contract.md`: "an empty researched ruleset is better than permanent context bloat." `RULESET_MANIFEST.json` is written with an empty `generated_rules` array and the deferred candidates above recorded as `deferred_or_rejected`.

## Hard-enforcement note

None of the deferred candidates rises to a level requiring a hook/permission/test decision in FOUNDATION_MODE, since there is no live path to protect yet. Once a repository exists with an actual holdout-data directory or an actual immutable-protocol-file convention, re-run this phase and evaluate whether the boundary is important enough to warrant a hook (deterministic block) rather than a rule (instruction) — the authority invariants above are exactly the kind of "destructive/data-integrity/holdout-boundary failure" `rule-contract.md` flags for that evaluation.
