# Skillset Research

> **Provenance note:** citations below to `skill-selection.md` / `skill-contract.md` refer to the `ai-backtesting-team-builder` skill's own bundled authoring-contract docs (used during generation), not to files shipped in this output repository. They are not runtime references any `bt-*` agent or generated skill needs to open.

Mode: `FOUNDATION_MODE`. No repository-native commands or scripts exist to wrap, so no candidate scores on "reuse an existing repository tool." Candidates below are scored on the general workflow/risk/reuse dimensions from `skill-selection.md`'s coverage prompt, using the evidence recorded in `BUILD_RESEARCH.md`.

Score legend: 0–3 each on frequency, complexity, risk, cross-role reuse, determinism leverage, routing distinctiveness, context efficiency. Default inclusion requires `frequency + complexity + risk >= 6` AND at least one of {cross-role reuse, determinism leverage, routing distinctiveness} `>= 2`.

## Candidate: temporal-leakage-audit

- **Repeated workflow / failure mode:** the single highest-frequency backtesting failure per the literature reviewed (López de Prado 2018) — a feature or split leaking future information into training.
- **Highest-risk decisions:** whether a feature's computation window respects the label's decision timestamp; whether a train/test split is purged and embargoed.
- **Claim class:** method-sensitive (primary source: López de Prado 2018, chs. 7 & 12), applied through a stable-principle checklist (no lookahead).
- **Strongest evidence:** see `BUILD_RESEARCH.md` shared evidence, entry 1.
- **Existing repository tools to reuse:** none (FOUNDATION_MODE) — recorded as procedural, not executable, for that reason (no deterministic implementation path exists to bundle yet; wrapping a specific library such as `purged-cross-validation` would assume a Python/sklearn stack this build has no evidence for).
- **Procedural vs. executable:** procedural.
- **Routing boundary:** activates when a feature, label, or train/test split definition is being reviewed for timing correctness; does not activate for execution-cost or statistical-significance questions.
- **Completion evidence:** a per-feature/per-split table stating computation window vs. label timestamp, and purge/embargo width vs. label horizon, with each row marked pass/fail/unknown.
- **Scores:** frequency 3, complexity 2, risk 3, cross-role reuse 3 (feature/label methodologist, experiment designer, integrity reviewer), determinism leverage 0 (no bundled script yet), routing distinctiveness 3, context efficiency 3.
- **Selection score check:** 3+2+3=8 >= 6 ✓; cross-role reuse 3 >= 2 ✓. **Included.**
- **Consumer agents:** on-demand for `bt-feature-label-methodologist`, `bt-experiment-designer`, `bt-experiment-integrity-reviewer`. `forbidden_for_approval_agents`: `bt-experiment-integrity-reviewer` (the skill's checklist output informs but cannot itself satisfy that role's independent integrity gate — the reviewer must independently verify).
- **Non-authority:** cannot certify experiment integrity; cannot approve promotion.

## Candidate: execution-cost-realism-check

- **Repeated workflow / failure mode:** backtests that report performance with an implicit zero-cost or unrealistic fill assumption.
- **Highest-risk decisions:** whether fill model, spread, fee, slippage, market impact, and (for leveraged/short positions) funding/borrow/latency costs are declared and justified against the target venue.
- **Claim class:** stable principle (cost realism matters) with venue-specific constants explicitly left unresolved (no unsupported constant is universalized, per research-protocol).
- **Existing repository tools to reuse:** none evidenced.
- **Procedural vs. executable:** procedural.
- **Routing boundary:** activates when reviewing a backtest's cost/fill assumptions; does not activate for leakage or statistical-significance questions.
- **Completion evidence:** a declared cost-model checklist (fill type, spread source, fee schedule, slippage model, impact model, funding/borrow if applicable) with each item marked declared/justified/missing.
- **Scores:** frequency 3, complexity 2, risk 3, cross-role reuse 2 (execution-microstructure specialist, backtest engineer), determinism leverage 0, routing distinctiveness 3, context efficiency 3.
- **Selection score check:** 3+2+3=8 >= 6 ✓; distinctiveness 3 >= 2 ✓. **Included.**
- **Consumer agents:** on-demand for `bt-execution-microstructure-specialist`, `bt-backtest-engineer`.
- **Non-authority:** cannot certify that a backtest's returns are realistic overall — only that the cost model is declared and internally justified.

## Candidate: multiple-testing-correction

- **Repeated workflow / failure mode:** a confirmation-stage performance metric (e.g., Sharpe ratio) reported without correcting for the number of configurations/trials searched.
- **Highest-risk decisions:** which correction (family-wise Bonferroni vs. Benjamini–Hochberg FDR) applies to the study design; whether the trial count used is the true trial count.
- **Claim class:** method-sensitive / stable-principle, per Bailey & López de Prado (2012, 2014), Harvey/Liu/Zhu (2016), and Benjamini–Hochberg (1995) — see `BUILD_RESEARCH.md` shared evidence.
- **Existing repository tools to reuse:** none evidenced, but the computation itself (Bonferroni divide-by-N; BH step-up procedure) is a closed-form, well-specified algorithm independent of any repository — a deterministic script is justified on its own terms.
- **Procedural vs. executable:** **executable.** Bundled script `scripts/mtc.py` takes a list of p-values (or Sharpe-ratio-derived p-values) and a method flag, and returns adjusted significance decisions with documented CLI/I-O/exit codes. This meets the skill contract's determinism-reality-check: the claim is "recompute a well-defined statistical correction," and a real script performs it.
- **Routing boundary:** activates when a reviewer needs to correct a stated set of p-values/trial results for multiple comparisons; does not activate for leakage or cost-realism questions, and does not itself decide whether the strategy passes review.
- **Completion evidence:** script exit code 0 with a machine-readable table of raw vs. adjusted significance per trial; exit code 1 with a human-readable error for malformed input (e.g., missing trial count).
- **Scores:** frequency 2, complexity 2, risk 3, cross-role reuse 2 (statistical reviewer, integrity reviewer), determinism leverage 3, routing distinctiveness 3, context efficiency 3.
- **Selection score check:** 2+2+3=7 >= 6 ✓; determinism leverage 3 >= 2 ✓. **Included.**
- **Consumer agents:** on-demand for `bt-statistical-reviewer`. `forbidden_for_approval_agents`: `bt-experiment-integrity-reviewer` (the script's output is evidence the reviewer inspects; it cannot itself satisfy the reviewer's independent integrity gate).
- **Non-authority:** cannot decide which correction method is appropriate for a given study design — that judgment belongs to `bt-statistical-reviewer`; cannot certify experiment integrity.

## Candidate: reproducibility-manifest

- **Repeated workflow / failure mode:** a reported backtest result that cannot later be reproduced because the exact code version, config, and data snapshot used were not recorded.
- **Highest-risk decisions:** whether the manifest captures enough identity (content hashes, not just file names) to detect silent drift.
- **Claim class:** stable principle (reproducibility) with a deterministic implementation.
- **Existing repository tools to reuse:** none evidenced; a generic file-hashing manifest generator is repository-agnostic and deterministic on its own terms (SHA-256 over named input files/directories).
- **Procedural vs. executable:** **executable.** Bundled script `scripts/manifest.py` takes a list of file/directory paths and a free-text config/identity block, and emits a JSON manifest with SHA-256 hashes, a timestamp, and a manifest-level hash. Comparing two manifests is a deterministic diff.
- **Routing boundary:** activates when an implementation or a re-run needs its inputs fingerprinted for later verification; does not itself judge methodological correctness.
- **Completion evidence:** a JSON manifest file with per-input hashes and exit code 0; exit code 1 with a clear error if a listed path doesn't exist.
- **Scores:** frequency 2, complexity 1, risk 3, cross-role reuse 2 (backtest engineer produces it, integrity reviewer consumes it), determinism leverage 3, routing distinctiveness 2, context efficiency 3.
- **Selection score check:** 2+1+3=6 >= 6 ✓; determinism leverage 3 >= 2 ✓. **Included.**
- **Consumer agents:** on-demand for `bt-backtest-engineer` (produces the manifest). `forbidden_for_approval_agents`: `bt-experiment-integrity-reviewer` (a manifest existing is not itself proof of correctness — the reviewer must independently attempt to verify reproducibility, not merely confirm a manifest file is present).
- **Non-authority:** cannot certify that a reproduction attempt actually matched; only fingerprints inputs.

## Candidate: evidence-report-formatter

- **Repeated workflow / failure mode:** final reports that omit limitations, blur `INCONCLUSIVE` into implied success, or lose claim-to-evidence traceability.
- **Highest-risk decisions:** none methodological — this is a formatting/discipline aid, not a statistical or leakage judgment.
- **Claim class:** internal-design (a formatting convention this build chooses, not externally mandated) — labeled as such rather than presented as research consensus.
- **Existing repository tools to reuse:** none.
- **Procedural vs. executable:** procedural.
- **Routing boundary:** activates only when `bt-evidence-reporter` is assembling final synthesis output; not used by any other role.
- **Completion evidence:** a filled claim/evidence/limitation/status table with every claim traceable to an upstream handoff.
- **Scores:** frequency 2, complexity 1, risk 2, cross-role reuse 0 (single consumer by design), determinism leverage 0, routing distinctiveness 3, context efficiency 3.
- **Selection score check:** 2+1+2=5 < 6 by the default formula. Per `skill-selection.md`'s "concrete recurring failure mode" exception: reports that silently upgrade `INCONCLUSIVE` findings are a documented, high-consequence recurring failure mode (directly named in the handoff contract's status rules and the evidence-reporter's non-authority constraint in `team-blueprint.md`), and placement as a rule is worse (this is a multi-field checklist procedure, not a path-scoped invariant, and no CLAUDE.md-level fact exists to attach it to) and placement as agent-only prompt text is worse (it would need to be duplicated if a second reporting consumer is ever added). **Included on the documented-failure-mode exception, not the default score.**
- **Consumer agents:** on-demand for `bt-evidence-reporter` only.
- **Non-authority:** cannot upgrade any upstream gate status; purely a formatting/discipline aid.

## Rejected/deferred candidates

| Name | Reason |
|---|---|
| repository-scaffolding / project-setup | Generic coding helper, no backtesting-specific semantics — rejected per skill-selection.md rule 5 |
| git-commit-helper | Generic Git helper, no backtesting-specific semantics — rejected per rule 5 |
| vendor-specific-data-loader (e.g., a named market-data API wrapper) | No vendor evidenced in FOUNDATION_MODE; inventing one would universalize an unsupported mechanic — deferred until a repository exists |
| walk-forward-window-generator (deterministic date-window splitter) | Real candidate for a future repository-specific build once data frequency and calendar conventions are known; deferred here because a generic version without a known frequency/calendar would either be too vague to be executable or would invent a frequency not evidenced |
| stress-scenario-library (canned historical stress windows) | Rejected in FOUNDATION_MODE — asset-class-specific stress windows (e.g., named crash dates) are exactly the kind of unsupported, scope-mismatched constant `research-protocol.md` prohibits without repository/market evidence |

## Scorecard summary

| Skill | freq | complexity | risk | cross-role reuse | determinism leverage | routing distinctiveness | context efficiency | Included? |
|---|---|---|---|---|---|---|---|---|
| temporal-leakage-audit | 3 | 2 | 3 | 3 | 0 | 3 | 3 | Yes (default score) |
| execution-cost-realism-check | 3 | 2 | 3 | 2 | 0 | 3 | 3 | Yes (default score) |
| multiple-testing-correction | 2 | 2 | 3 | 2 | 3 | 3 | 3 | Yes (default score) |
| reproducibility-manifest | 2 | 1 | 3 | 2 | 3 | 2 | 3 | Yes (default score) |
| evidence-report-formatter | 2 | 1 | 2 | 0 | 0 | 3 | 3 | Yes (documented-failure-mode exception) |

This scorecard is the condensed view of the per-candidate scoring above; see each candidate's entry for the underlying rationale.

## Agent-to-skill binding matrix

The runtime binding requirement (`SKILL.md` §"Runtime binding" in `references/skill-contract.md`) is satisfied as follows — every row below is mirrored in `SKILLSET_MANIFEST.json` and in the named agent's `## Skills` section:

| Skill | preload | on-demand | forbidden-for-approval |
|---|---|---|---|
| temporal-leakage-audit | — | bt-feature-label-methodologist, bt-experiment-designer, bt-experiment-integrity-reviewer | bt-experiment-integrity-reviewer |
| execution-cost-realism-check | — | bt-execution-microstructure-specialist, bt-backtest-engineer | — |
| multiple-testing-correction | — | bt-statistical-reviewer | bt-experiment-integrity-reviewer |
| reproducibility-manifest | — | bt-backtest-engineer | bt-experiment-integrity-reviewer |
| evidence-report-formatter | — | bt-evidence-reporter | — |

No skill is preloaded: every selected skill is conditional on a specific review/implementation moment rather than needed at every startup of its consumer agent, so on-demand placement was preferred throughout (per `skill-selection.md`: "Preload sparingly... On-demand is preferred when a workflow is conditional").

## Skill research stop condition

Five skills selected, each cleared the placement test (multi-step reusable workflow, not a persistent fact, not an independent authority, not deterministic-mandatory-enforcement) and either the default selection score or a documented exception. Two are executable with real bundled scripts; three are procedural. Runtime bindings for every selected skill are recorded above and mirrored in `SKILLSET_MANIFEST.json` and the generated agent files.
