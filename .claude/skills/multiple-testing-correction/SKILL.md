---
name: multiple-testing-correction
description: Deterministically corrects a set of trial p-values for multiple comparisons using Bonferroni (family-wise) or Benjamini-Hochberg (false discovery rate) correction, via a bundled script. Use when a confirmation-stage result comes from searching over multiple configurations/trials and the reported significance needs correcting for the true trial count. Trigger phrases include "correct for multiple testing", "apply Bonferroni", "apply FDR correction", "how many of these trials are actually significant". Not for deciding which correction method fits the study design (that judgment stays with bt-statistical-reviewer) and not a substitute for bt-experiment-integrity-reviewer's independent integrity gate.
---

# Multiple Testing Correction

## Purpose

Performs the deterministic arithmetic of Bonferroni or Benjamini-Hochberg correction over a list of trial p-values. Activated by `bt-statistical-reviewer` when a confirmation-stage claim depends on the true number of trials searched. Does not decide which method is appropriate, and its output alone cannot satisfy `bt-experiment-integrity-reviewer`'s independent gate.

## Inputs / prerequisites

- The full list of trial p-values (or a derivation of p-values from reported Sharpe ratios/t-statistics), covering the true number of configurations searched — not just the ones reported as "promising."
- A chosen significance level (alpha).
- A chosen method: `bonferroni` (family-wise error control) or `bh` (false discovery rate control, per Benjamini & Hochberg 1995).

If the true trial count is contested or unknown, this skill cannot run meaningfully — the calling agent should report `INCONCLUSIVE` rather than invoke this skill with a partial trial list.

## Workflow

1. Assemble the full trial list as `{"trials": [{"id": ..., "p_value": ...}, ...]}` (see `scripts/mtc.py` docstring for the exact schema), or pass p-values inline.
2. Run: `python3 scripts/mtc.py --method <bonferroni|bh> --alpha <value> --input trials.json` (or `--pvalues v1 v2 ...` for a quick inline check).
3. Read the JSON result: `threshold` (Bonferroni only), and per-trial `reject_null` flags with `n_significant` total.
4. Report the result verbatim to the calling agent; do not hand-recompute or round the script's output.

## Validation

- Exit code 0: success, JSON result on stdout.
- Exit code 1: malformed input (bad JSON, missing `p_value`, a `p_value` outside `[0,1]`, or an empty trial list) — report `BLOCKED` on this check rather than guessing values.
- Exit code 2: bad CLI usage (invalid method or alpha) — a Claude-side usage error, fix and rerun.

## Output contract

The script's JSON output (method, alpha, n_trials, threshold, per-trial results, n_significant), passed through unmodified to the calling agent, plus a one-line note on which method was chosen and why (recorded by the calling agent, not invented by this skill).

## Safety / non-authority

This skill cannot decide whether Bonferroni or BH-FDR is the right choice for a given study design — `bt-statistical-reviewer` makes that call. It cannot certify experiment integrity; `bt-experiment-integrity-reviewer` must independently verify the trial count fed into this script was the true, complete trial count, not merely accept that the script ran.

## Builder provenance

`SKILLSET_RESEARCH.md` → "Candidate: multiple-testing-correction". Method evidence: `BUILD_RESEARCH.md` shared evidence entries 2–4 (Bailey & López de Prado 2012/2014, Harvey/Liu/Zhu 2016, Benjamini & Hochberg 1995) and role research §8 (`bt-statistical-reviewer`).
