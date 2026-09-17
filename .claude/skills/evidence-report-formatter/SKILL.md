---
name: evidence-report-formatter
description: Standardizes a final backtesting evidence report into a claim/evidence/limitation/status structure, so INCONCLUSIVE or FAIL findings are never silently upgraded into confident prose. Use only when bt-evidence-reporter is assembling final synthesis output from upstream handoffs. Trigger phrases include "format the evidence report", "write up the findings", "assemble the final report". Not used by any other role.
---

# Evidence Report Formatter

## Purpose

A formatting/discipline aid for `bt-evidence-reporter` only. This is an internal design convention (not an externally mandated standard) chosen to prevent status-blurring in final reports — see builder provenance.

## Inputs / prerequisites

Every upstream handoff (per `references/handoff-contract.md`) that the report will draw on, each with its recorded `Status: PASS | FAIL | INCONCLUSIVE | BLOCKED`.

## Workflow

1. For every claim in the report, cite the exact upstream handoff it traces to. A claim with no traceable handoff does not go in the report.
2. Render each claim as a row: `claim`, `evidence` (pointer to the handoff/artifact), `status` (copied verbatim from the upstream handoff — never re-worded into something more confident), `limitation` (any caveat the upstream role recorded).
3. Do not merge multiple upstream statuses into one summary status that hides a `FAIL` or `INCONCLUSIVE` among `PASS` rows — list them separately.
4. Preserve negative findings: an upstream `FAIL` or `INCONCLUSIVE` is reported with the same prominence as a `PASS`, not relegated to a footnote.

## Validation

If a claim the requester wants included has no upstream handoff, do not include it — report to `bt-evidence-reporter` that it is unsupported rather than inventing evidence for it.

## Output contract

A claim/evidence/status/limitation table, plus a one-paragraph plain-language summary that states the overall confirmed status (never rounding an `INCONCLUSIVE` majority up to a positive-sounding summary).

## Safety / non-authority

This skill cannot upgrade any upstream gate status. `bt-evidence-reporter` remains responsible for the actual synthesis judgment; this skill only enforces the structure.

## Builder provenance

`SKILLSET_RESEARCH.md` → "Candidate: evidence-report-formatter" (included on the documented-recurring-failure-mode exception, not the default selection score — see that entry for the score and rationale). Role research: `BUILD_RESEARCH.md` §11 (`bt-evidence-reporter`).
