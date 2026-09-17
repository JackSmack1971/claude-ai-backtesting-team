# Team Blueprint

Canonical source for the 12-role dependency order, parallel-safety
boundaries, and authority invariants that `bt-team-orchestrator` routes
against and that several agents' `## Non-authority` sections restate. This
file consolidates what was previously only implicit across those individual
restatements.

## Roles

`bt-methods-researcher`, `bt-hypothesis-researcher`, `bt-data-integrity-specialist`,
`bt-feature-label-methodologist`, `bt-execution-microstructure-specialist`,
`bt-backtest-engineer`, `bt-experiment-designer`, `bt-statistical-reviewer`,
`bt-risk-robustness-analyst`, `bt-experiment-integrity-reviewer`,
`bt-evidence-reporter`, `bt-team-orchestrator`.

## Dependency order

1. `bt-methods-researcher` can feed any other role at any time (method/mechanics questions have no stage dependency).
2. `bt-hypothesis-researcher` establishes a mechanism + baseline + falsification condition before design work starts.
3. `bt-data-integrity-specialist`, `bt-feature-label-methodologist`, and `bt-execution-microstructure-specialist` research/review data, timing, and execution assumptions — these three may run in parallel with each other once a hypothesis exists.
4. `bt-experiment-designer` fixes the temporal protocol (splits, search budget, baselines) using the above, before any confirmation-stage result exists.
5. `bt-backtest-engineer` implements the accepted protocol.
6. `bt-statistical-reviewer` and `bt-risk-robustness-analyst` review confirmation-stage results — these two may run in parallel with each other.
7. `bt-experiment-integrity-reviewer` performs the final independent gate, after all of the above.
8. `bt-evidence-reporter` synthesizes the final report, only after `bt-experiment-integrity-reviewer` has issued a status.
9. `bt-team-orchestrator` routes every transition above; it never performs the analysis itself.

## Parallel-safety boundaries

Parallel-safe: data-integrity and execution-microstructure research together;
statistical-method and robustness-method research before confirmation results
exist. Never parallel-safe: two roles mutating the same methodological
contract (e.g., the experiment protocol) concurrently without an explicit
ownership decision.

## Authority invariants

- Discovery roles (`bt-hypothesis-researcher`, `bt-experiment-designer`
  pre-protocol-lock) must never be given confirmation/holdout outcomes.
- Consensus among roles is never evidence — a `PASS` requires the owning
  role's own affirmative finding.
- A skill's clean output never substitutes for a required independent
  review (e.g., `multiple-testing-correction` running is not
  `bt-experiment-integrity-reviewer` passing).
- `bt-experiment-integrity-reviewer` is the final independent gate and
  cannot be overridden by `bt-team-orchestrator` or any other role.
- `bt-team-orchestrator` does not possess the union of all agent
  authorities; it routes, it does not adjudicate.
- `bt-backtest-engineer` cannot certify its own methodological or
  integrity correctness.
- `bt-risk-robustness-analyst` can block or qualify progression but must
  never rewrite a failed result into a positive conclusion.
- `bt-evidence-reporter` cannot upgrade `INCONCLUSIVE`/`FAIL`/`BLOCKED`
  findings into confident prose, and cannot originate new findings.

## Enforcement note

These invariants are prompt-level operating discipline for every agent that
restates them, not a Claude Code runtime sandbox — no current mechanism
prevents an agent from technically violating them (see
`bt-team-orchestrator.md`'s "Runtime-mechanics correction" for the specific
case of subagent-spawn restrictions). They are enforced by each agent's own
instructions and by human review of handoffs, not by tool-level sandboxing.
