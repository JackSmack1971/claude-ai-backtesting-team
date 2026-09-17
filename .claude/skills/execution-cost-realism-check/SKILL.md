---
name: execution-cost-realism-check
description: Checks whether a backtest declares and justifies its fill model, spread, fees, slippage, market impact, and (for leveraged/short positions) funding or borrow costs, against the stated target venue. Use when reviewing a backtest's execution assumptions or when a strategy's reported returns need a cost-realism sanity check. Trigger phrases include "check execution costs", "is this fill model realistic", "review slippage assumptions", "cost realism check". Not for leakage review (see temporal-leakage-audit) or statistical significance (see multiple-testing-correction).
---

# Execution Cost Realism Check

## Purpose

Confirms a backtest's cost model is declared and internally justified against its named venue; does not judge whether the strategy is profitable, and does not review timing/leakage or statistical significance.

## Inputs / prerequisites

- The target venue/instrument (even a general description, e.g., "US equities, retail broker" or "perpetual futures, exchange X").
- The backtest's stated fill model (e.g., next-bar open, mid-price, limit-order fill probability).
- Whatever cost assumptions the backtest declares (spread, fee schedule, slippage, market impact, funding/borrow, latency).

If the venue is unspecified, this skill cannot complete the venue-justification step — report that item `INCONCLUSIVE`.

## Workflow

1. Record the declared fill model. Mark `declared` or `missing`.
2. For each of: spread, fees, slippage, market impact, funding/borrow (only if leveraged or short), latency — record whether it is declared, and whether the declared value is justified against the named venue (e.g., a cited fee schedule, an observed spread) or merely asserted with no justification.
3. Do not invent or assume a "reasonable" cost figure on the strategy's behalf — a missing item is `missing`, not silently filled in.
4. Compile into the output table below.

## Validation

- A backtest reporting performance with a `missing` fill model is a hard stop for this checklist item: report it and let the calling agent (`bt-execution-microstructure-specialist` or `bt-backtest-engineer`) decide the consequence — this skill does not itself gate promotion.
- `justified` requires a cited source or observed data, not just a plausible-sounding number.

## Output contract

A table with one row per cost dimension (`dimension`, `declared`, `justification`, `status`), where `status` is `declared+justified`, `declared+unjustified`, or `missing`. End with a one-line summary of counts per status.

## Safety / non-authority

Confirms declaration and internal justification only — it cannot certify that the overall cost model produces realistic net returns, and it is not a substitute for `bt-risk-robustness-analyst`'s independent robustness review.

## Builder provenance

`SKILLSET_RESEARCH.md` → "Candidate: execution-cost-realism-check". Role research: `BUILD_RESEARCH.md` §5 (`bt-execution-microstructure-specialist`) and §6 (`bt-backtest-engineer`).
