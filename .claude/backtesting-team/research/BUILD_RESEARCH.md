# Build Research — Portable Core Roles

Mode: `FOUNDATION_MODE`. No repository exists, so "repository application" sections below record what would apply once one exists rather than fabricated repository facts. No extension role was justified (see `ARCHITECTURE_RESEARCH.md`), so only the 12 portable roles are researched.

Shared evidence base for this document:

### Source: Advances in Financial Machine Learning
- Publisher/author: Marcos López de Prado, Wiley, 2018
- URL: (book; referenced via https://philpapers.org/rec/LPEAIF and corroborating summaries at https://en.wikipedia.org/wiki/Purged_cross-validation and https://www.garp.org/hubfs/Whitepapers/a1Z1W0000054x6lUAA.pdf, López de Prado's own 2017 working paper "The 10 Reasons Most Machine Learning Funds Fail")
- Accessed: 2026-09-17
- Source class: primary-research
- Claim class: method-sensitive
- Relevant claim: k-fold cross-validation on overlapping, serially-correlated financial labels leaks information between train and test folds; purging (removing training observations whose label window overlaps the test window) and embargoing (dropping a buffer of training observations immediately after each test block) are the corrective procedures; walk-forward validation is the most common backtest method and is leakage-safe only if purging is correctly implemented.
- Applies to: `bt-feature-label-methodologist`, `bt-experiment-designer`, `bt-backtest-engineer`, `bt-experiment-integrity-reviewer`, temporal-leakage-audit skill
- Design consequence: these roles treat "does every prediction use only information available at decision time, with any train/test split purged and embargoed against label overlap" as a hard gate, not a heuristic.
- Limitations/disagreement: none found; this is the dominant reference in the field, and the underlying serial-correlation argument is elementary and uncontested.

### Source: The Probabilistic Sharpe Ratio / The Deflated Sharpe Ratio
- Publisher/author: David H. Bailey & Marcos López de Prado (2012, 2014)
- URL: referenced via https://www.quantresearch.org/Innovations.htm and corroborating summary at https://github.com/eslazarev/purged-cross-validation/blob/main/paper/paper.md
- Accessed: 2026-09-17
- Source class: primary-research
- Claim class: method-sensitive
- Relevant claim: a Sharpe ratio estimated after searching over N independent trials is biased upward; the Deflated Sharpe Ratio corrects the significance threshold for the number of trials and their variance, giving the probability that a strategy's true Sharpe ratio exceeds zero after accounting for multiple testing and non-normal returns.
- Applies to: `bt-statistical-reviewer`, `bt-experiment-integrity-reviewer`, multiple-testing-correction skill
- Design consequence: any confirmation-stage performance claim reviewed by `bt-statistical-reviewer` must disclose the number of trials/configurations searched; a single held-out Sharpe ratio with no trial count disclosed is treated as `INCONCLUSIVE`, not `PASS`.
- Limitations/disagreement: none found for the core claim; exact deflation formula parameters are technical detail the reviewer applies per study, not a universal constant this build encodes.

### Source: ...and the Cross-Section of Expected Returns
- Publisher/author: Campbell R. Harvey, Yan Liu, Heqing Zhu (Review of Financial Studies, 2016)
- URL: referenced via the purged-cross-validation JOSS paper draft (https://github.com/eslazarev/purged-cross-validation/blob/main/paper/paper.md), citing harvey2016
- Accessed: 2026-09-17
- Source class: primary-research
- Claim class: method-sensitive
- Relevant claim: hundreds of published "anomaly" factors are largely explainable by multiple-testing bias; the paper argues for materially higher significance bars (e.g., t-stat > 3) once the number of tested factors is accounted for.
- Applies to: `bt-statistical-reviewer`, `bt-experiment-integrity-reviewer`
- Design consequence: `bt-statistical-reviewer`'s stop condition includes "search/trial count not disclosed" as a mandatory `INCONCLUSIVE`, independent of which correction formula is used.
- Limitations/disagreement: the exact recommended threshold is debated in follow-up literature; this build does not universalize a single numeric cutoff (see research-protocol's "no unsupported constants" rule) and instead requires the reviewer to record whichever correction was used and why.

### Source: Benjamini–Hochberg false discovery rate control
- Publisher/author: Yoav Benjamini & Yosef Hochberg (Journal of the Royal Statistical Society B, 1995)
- URL: well-established statistical standard, cited across quantitative finance and statistics literature (stable-principle status; not separately re-verified per build since it is durable, non-mechanics-sensitive, foundational statistics)
- Accessed: 2026-09-17 (durable principle; freshness re-verification not required per `research-protocol.md`'s freshness policy for stable principles)
- Source class: peer-reviewed
- Claim class: stable-principle
- Relevant claim: controlling the false discovery rate across multiple hypothesis tests is a well-defined, implementable procedure distinct from controlling the family-wise error rate.
- Applies to: multiple-testing-correction skill (offers both Bonferroni family-wise and Benjamini–Hochberg FDR corrections as alternative, clearly labeled deterministic computations)
- Design consequence: the skill implements both corrections and requires the caller (the statistical reviewer) to select and record which one applies to the study design, rather than picking one as universal.
- Limitations/disagreement: none — this is textbook statistics.

---

## 1. bt-methods-researcher

**Highest-risk decisions:** (1) whether a cited method is primary or a secondary paraphrase; (2) whether a method claim is stable-principle vs. contested; (3) whether current documentation for a named tool/library is still accurate.

**Repository vs. external claims:** in FOUNDATION_MODE there is no repository-local evidence to separate; all claims are external-method or mechanics claims.

**Operating rules:** prefer primary/original sources (per source hierarchy in `research-protocol.md`); never let one paper's finding get stretched to an unrelated role's decision; record contested claims with both sides rather than averaging.

**Repository application:** once a target repository/framework exists, this role's job narrows to verifying that the repository's chosen libraries/APIs match current official docs, in addition to general methods research.

**Stop condition:** stop and mark `INCONCLUSIVE` rather than recommend a method whose only support is a secondary blog post, when a primary source is locatable but not yet checked.

## 2. bt-hypothesis-researcher

**Highest-risk decisions:** (1) whether the hypothesis has a stated economic/behavioral mechanism, not just a pattern; (2) whether a credible baseline exists; (3) whether the discovery ledger has been contaminated by prior exposure to confirmation-stage results.

**Operating rules:** every hypothesis entry requires a falsifiable mechanism statement and an explicit baseline; this role never sees held-out/confirmation performance data (authority invariant from `team-blueprint.md`).

**Repository application:** the discovery ledger becomes a repository artifact (e.g., a markdown or JSON log) once a repository exists; FOUNDATION_MODE defines its required fields (hypothesis, mechanism, baseline, falsification condition, timestamp) without inventing a file path.

**Stop condition:** `BLOCKED` if asked to evaluate a hypothesis using data the requester describes as already-observed out-of-sample results.

## 3. bt-data-integrity-specialist

**Highest-risk decisions:** (1) point-in-time correctness (was a data value knowable at the timestamp it's attached to); (2) missingness and survivorship handling; (3) universe construction integrity (e.g., delisted/renamed instruments).

**Evidence class:** these are stable principles (avoiding lookahead, avoiding survivorship bias) independent of vendor; vendor-specific timestamp semantics are mechanics-sensitive and require inspecting the actual vendor/repository once one exists.

**Repository application:** deferred — no data source is evidenced. This role's operating rules (never certify a dataset without checking point-in-time availability and survivorship handling) apply regardless of vendor.

**Stop condition:** `BLOCKED` when the data source's timestamp semantics (e.g., "as-of" vs. "as-reported") cannot be determined from available documentation or metadata.

## 4. bt-feature-label-methodologist

**Highest-risk decisions:** (1) label horizon and information-availability timing; (2) leakage via purging/embargo (López de Prado, above); (3) target/censoring semantics (e.g., triple-barrier labeling edge cases).

**Operating rules (hard gate):** every feature must be computable using only information available strictly before the label's decision timestamp; every train/test split touching overlapping labels must apply purging and an embargo sized to the label horizon, per the primary source above.

**Repository application:** exact embargo width is data-frequency-dependent and left unresolved until real data frequency is known (no unsupported constant is universalized here).

**Stop condition:** `FAIL` on any feature whose computation window extends past the label's decision timestamp; `INCONCLUSIVE` if the codebase's feature-computation timing cannot be determined from available evidence.

## 5. bt-execution-microstructure-specialist

**Highest-risk decisions:** (1) fill model realism (aggressive vs. passive fills); (2) fee/spread/slippage/market-impact assumptions; (3) funding/borrow/latency costs for leveraged or short positions; (4) venue-specific mechanics (tick size, lot size, halts).

**Evidence class:** cost realism is a stable principle; specific fee schedules, spreads, and latency numbers are mechanics-/market-sensitive and must not be universalized without a named venue (per research-protocol's "no unsupported constants" rule).

**Repository application:** deferred — no venue evidenced. This role's mandatory gate is procedural ("every backtest must declare its fill/cost model and justify each assumption against the target venue's actual mechanics") rather than a numeric constant.

**Stop condition:** `FAIL` when a backtest reports performance with no stated fill/cost model; `INCONCLUSIVE` when the target venue is unspecified.

## 6. bt-backtest-engineer

**Highest-risk decisions:** (1) deterministic reproducibility (same inputs → same outputs); (2) correct accounting (position sizing, cash/margin, corporate actions if applicable); (3) faithful implementation of the accepted experiment protocol without silently deviating from it.

**Operating rules:** implementation follows an already-accepted protocol (dependency order in `team-blueprint.md`); this role cannot certify its own methodological or integrity correctness (authority invariant).

**Repository application:** deferred — no framework evidenced; this role's mandatory outputs (a reproducibility manifest, per the reproducibility-manifest skill) apply regardless of the eventual framework.

**Stop condition:** `BLOCKED` if the accepted protocol document doesn't exist yet; `FAIL` if implementation diverges from the accepted protocol without a recorded, approved amendment.

## 7. bt-experiment-designer

**Highest-risk decisions:** (1) discovery/confirmation separation (train/validation/holdout boundaries fixed before any confirmation result is seen); (2) search budget and its effect on the multiple-testing correction owed later; (3) baseline and ablation selection.

**Operating rules (hard gate):** the temporal protocol and holdout boundary must be fixed and recorded before any confirmation-stage result exists; changing the boundary after seeing a result is a leakage event, not a protocol update.

**Repository application:** deferred; the "protocol identity" (a recorded, timestamped definition of the split boundaries and search budget) is required regardless of repository.

**Stop condition:** `BLOCKED` if asked to design an experiment around data whose confirmation results the requester has already described.

## 8. bt-statistical-reviewer

**Highest-risk decisions:** (1) whether reported uncertainty (e.g., standard errors, confidence intervals) accounts for serial dependence in returns; (2) whether multiple-testing/selection bias is corrected for the actual number of trials run; (3) whether the chosen performance metric is valid for the return distribution's actual properties (e.g., Sharpe ratio under fat tails).

**Operating rules (hard gate, per evidence above):** a confirmation-stage performance claim without a disclosed trial/configuration count is `INCONCLUSIVE`, never `PASS`; this role cannot select or veto parameters post-hoc (authority invariant) — it reviews the statistics of what was already run.

**Repository application:** the multiple-testing-correction skill (on-demand) performs the deterministic part (Bonferroni/BH-FDR computation); the reviewer remains responsible for judging whether the correction was applied to the true trial count.

**Stop condition:** `INCONCLUSIVE` when the trial count or search history is unavailable or contested.

## 9. bt-risk-robustness-analyst

**Highest-risk decisions:** (1) drawdown/exposure/concentration measurement completeness; (2) turnover and realistic capacity/liquidity constraints; (3) regime and stress-test coverage (e.g., does the backtest period include a genuine drawdown regime).

**Operating rules:** this role can block or qualify progression but must not rewrite a failed result into a positive conclusion (authority invariant).

**Repository application:** deferred — specific stress scenarios depend on the eventual asset class; the mandatory procedural gate ("every promoted strategy must report max drawdown, exposure concentration, and turnover, and state whether the backtest period contains a stress regime") applies regardless.

**Stop condition:** `FAIL` when a promoted strategy's backtest window contains no meaningful adverse regime and no synthetic/stress alternative was evaluated; `INCONCLUSIVE` when drawdown/exposure figures are unavailable.

## 10. bt-experiment-integrity-reviewer

**Highest-risk decisions:** (1) protocol adherence (was the confirmed experiment actually the one designed, with no undisclosed peeking); (2) leakage (temporal, cross-sectional, or via shared preprocessing across train/test); (3) reproducibility (can another run reproduce the reported result from the recorded manifest); (4) whether upstream roles' skill usage substitutes for this role's own independent check.

**Operating rules (hard gate):** this is the final independent gate before synthesis; it must not accept a reproducibility-manifest or multiple-testing-correction skill's output as sufficient by itself — those skills are `forbidden-for-approval` for this role and only inform its own independent verification (per `team-blueprint.md`'s "relationship to generated skills" and the skill contract's non-authority requirement).

**Repository application:** deferred; the review checklist (protocol adherence, leakage, reproducibility, evidence sufficiency) applies regardless of repository.

**Stop condition:** `BLOCKED` if the upstream protocol document, reproducibility manifest, or statistical review are missing; `FAIL` on any detected leakage or protocol deviation; never `PASS` on absence of detected problems alone (per handoff contract).

## 11. bt-evidence-reporter

**Highest-risk decisions:** (1) not upgrading `INCONCLUSIVE`/`FAIL`/`BLOCKED` findings into confident prose; (2) preserving negative findings and limitations rather than only reporting wins; (3) claim-to-evidence traceability.

**Operating rules:** synthesizes only what upstream roles already passed/found; cannot upgrade gate status (authority invariant).

**Repository application:** the evidence-report-formatter skill (on-demand) standardizes claim/evidence/limitation structure; the reporter remains responsible for the actual synthesis judgment.

**Stop condition:** `INCONCLUSIVE` if asked to report a claim for which no upstream handoff exists.

## 12. bt-team-orchestrator

**Highest-risk decisions:** (1) not leaking confirmation/holdout outcomes to discovery roles when routing; (2) not parallelizing work that would let two roles mutate the same methodological contract concurrently; (3) not reinterpreting a `FAIL`/`INCONCLUSIVE`/`BLOCKED` handoff as authorization to proceed.

**Operating rules:** routes stage transitions using the handoff contract; does not possess the union of all agent authorities and cannot override an independent block (authority invariant).

**Repository application:** none repository-specific; the routing/parallel-safety rules from `team-blueprint.md` apply as written.

**Stop condition:** `BLOCKED` whenever a required upstream handoff is missing, contradictory, or has a non-`PASS` status that the requested next stage depends on.

---

## Role research stop condition

Central decisions for all 12 roles are either supported by the evidence above (primary/official/stable-principle) or explicitly marked unresolved pending a real repository (embargo width, fee schedules, stress scenarios, data vendor semantics). No role's hard gate rests solely on a secondary source. No extension role was researched because none was justified in `ARCHITECTURE_RESEARCH.md`.
