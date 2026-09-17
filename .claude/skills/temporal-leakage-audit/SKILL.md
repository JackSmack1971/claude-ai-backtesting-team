---
name: temporal-leakage-audit
description: Audits features, labels, and train/test/holdout splits for temporal leakage (lookahead bias, unpurged overlapping labels, missing embargo) in a backtesting or financial-ML context. Use when reviewing a feature's computation window against its label's decision timestamp, or when reviewing whether a data split is purged and embargoed. Trigger phrases include "check for leakage", "review this feature timing", "is this split leaking future data", "purge and embargo review". Not for execution-cost realism (see execution-cost-realism-check) or statistical significance (see multiple-testing-correction).
---

# Temporal Leakage Audit

## Purpose

Checks whether information available only after a label's decision timestamp has entered that label's features, and whether a train/test/holdout split has been purged and embargoed against overlapping label windows. Activated by `bt-feature-label-methodologist`, `bt-experiment-designer`, and `bt-experiment-integrity-reviewer` when reviewing timing correctness. Does not activate for cost/fill realism or statistical-significance review.

## Inputs / prerequisites

- The label definition: what is being predicted, and its decision timestamp.
- The feature list with each feature's computation window (what data, over what time range, is used to compute it).
- The train/test/holdout split definition, including label horizon (how far forward a label looks).

If any of these three is missing, this skill cannot complete — report `INCONCLUSIVE` for the missing part rather than assuming a value.

## Workflow

1. For each feature, state the computation window and confirm it ends strictly before the label's decision timestamp. Mark each: `pass` (window ends before timestamp), `fail` (window extends past timestamp), or `unknown` (window not determinable from available evidence).
2. Determine the label horizon (how far forward the label's outcome is realized).
3. For each train/test or train/holdout boundary, confirm that training observations whose label window overlaps the test window are purged, and that an embargo buffer follows the test block sized to at least the label horizon (per López de Prado, *Advances in Financial Machine Learning*, 2018, chs. 7 & 12 — see `bt-feature-label-methodologist`'s builder provenance for the full citation).
4. Compile the results into the output table below.

## Validation

- If a feature's computation window cannot be determined (e.g., undocumented preprocessing), mark it `unknown` and do not infer a pass.
- If the label horizon is undocumented, the purge/embargo check cannot complete — report the split check as `INCONCLUSIVE`, not `pass`.
- Do not mark `pass` on the absence of an obvious problem; `pass` requires the computation window or purge/embargo boundary to be positively confirmed.

## Output contract

A table with one row per feature (`feature`, `computation_window`, `label_timestamp`, `status`) and one row per split boundary (`boundary`, `label_horizon`, `purge_applied`, `embargo_width`, `status`), where `status` is `pass`, `fail`, or `unknown`. End with a one-line summary: total pass/fail/unknown counts.

## Safety / non-authority

This skill produces an inspection table only. It does not certify experiment integrity and cannot itself satisfy `bt-experiment-integrity-reviewer`'s independent integrity gate — that role must perform its own independent check even when this skill reports all-`pass`.

## Builder provenance

`SKILLSET_RESEARCH.md` → "Candidate: temporal-leakage-audit". Method evidence: `BUILD_RESEARCH.md` shared evidence entry 1 (López de Prado 2018) and role research for `bt-feature-label-methodologist` (§4) and `bt-experiment-designer` (§7).
