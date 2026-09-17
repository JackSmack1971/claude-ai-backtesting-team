---
name: reproducibility-manifest
description: Deterministically fingerprints a backtest's code, config, and data inputs into a SHA-256-hashed JSON manifest, and can diff two manifests to detect drift, via a bundled script. Use when an implementation is complete and its inputs need to be recorded for later reproduction, or when checking whether a re-run's inputs match an earlier recorded run. Trigger phrases include "generate a reproducibility manifest", "fingerprint these inputs", "did anything change between these two runs". Not a substitute for bt-experiment-integrity-reviewer's independent reproducibility check.
---

# Reproducibility Manifest

## Purpose

Hashes named files/directories plus a free-text identity note into a manifest, and diffs two manifests for drift. Activated by `bt-backtest-engineer` after implementation to record what was actually run. Does not itself verify that a reproduction attempt matched — it only fingerprints inputs.

## Inputs / prerequisites

- The exact file/directory paths that constitute this run's code, config, and (if practical to hash) data inputs.
- A short identity note (e.g., protocol id, git commit, run label) to attach to the manifest.

## Workflow

1. Generate: `python3 scripts/manifest.py generate --inputs <path1> <path2> ... --note "<identity note>" --out manifest.json`.
2. To check for drift against an earlier run: `python3 scripts/manifest.py diff --a manifest_old.json --b manifest_new.json`.
3. Report the manifest's top-level `manifest_hash` and, for a diff, the `identical` flag and any listed differences, to the calling agent.

## Validation

- Exit code 0: success.
- Exit code 1: a listed input path does not exist, or a manifest file is malformed — report `BLOCKED` on this check; do not fabricate a hash for a missing path.
- Exit code 2: bad CLI usage.

## Output contract

The generated manifest JSON (or diff JSON), passed through unmodified. The calling agent records the manifest path and hash in its handoff's "Protocol/artifact identity" field.

## Safety / non-authority

Fingerprinting inputs is not proof of reproducibility. `bt-experiment-integrity-reviewer` must independently attempt (or verify an independent attempt at) reproducing the result — a manifest existing, even with a clean hash, cannot by itself satisfy that role's integrity gate.

## Builder provenance

`SKILLSET_RESEARCH.md` → "Candidate: reproducibility-manifest". Role research: `BUILD_RESEARCH.md` §6 (`bt-backtest-engineer`) and §10 (`bt-experiment-integrity-reviewer`).
