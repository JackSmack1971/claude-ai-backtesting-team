---
name: reproducibility-manifest
description: Deterministically fingerprints a backtest's code, config, and data inputs into a SHA-256-hashed JSON manifest, and can diff two manifests to detect drift, via a bundled script. Use when an implementation is complete and its inputs need to be recorded for later reproduction, or when checking whether a re-run's inputs match an earlier recorded run. Trigger phrases include "generate a reproducibility manifest", "fingerprint these inputs", "did anything change between these two runs". Not a substitute for bt-experiment-integrity-reviewer's independent reproducibility check.
---

# Reproducibility Manifest

## Purpose

Hashes named files/directories plus an explicit identity block (protocol/config identity, git commit and dirty state, dependency identity, runtime, and seed) into a single canonical manifest, and diffs two manifests for drift. Activated by `bt-backtest-engineer` after implementation to record what was actually run. Does not itself verify that a reproduction attempt matched — it only fingerprints inputs.

## Inputs / prerequisites

- The exact file/directory paths that constitute this run's code, config, and (if practical to hash) data inputs.
- A `--protocol-id` (required): the canonical protocol/config identity this run implements (e.g., the accepted experiment protocol's own id/path). Two runs of the *same files* under a *different* protocol id must not collapse to the same `manifest_hash`.
- Optionally: `--seed` (deterministic/random seed state), `--dependencies` (path to a requirements/lockfile to hash), `--git-commit` (override auto-detection). Git commit and dirty-state are auto-detected from the invocation's working directory when not overridden; if `git` is unavailable or the directory isn't a repo, they record `"unavailable"`/`"unknown"` rather than being silently omitted.
- `--note`: a free-text label (e.g., a human-readable run description). This is metadata only and is **not** bound into `manifest_hash` — do not rely on it for identity.

## Canonical identity schema

`manifest_hash` is a SHA-256 over exactly these fields (sorted keys): `protocol_id`, `seed`, `git_commit`, `git_dirty`, `dependencies_hash`, `runtime` (`python_version`, `platform`), `files` (per-input content hashes). `generated_at_unix` and `note` are recorded in the manifest but excluded from the hash. Changing any identity field — including `protocol_id` alone, with byte-identical files — changes `manifest_hash`.

## Workflow

1. Generate: `python3 "${CLAUDE_SKILL_DIR}/scripts/manifest.py" generate --inputs <path1> <path2> ... --protocol-id "<protocol/config identity>" [--seed <value>] [--dependencies <path>] --note "<free-text note>" --out manifest.json`. Always invoke via `${CLAUDE_SKILL_DIR}` — the current working directory is the session's working directory, not this skill's directory, so a bare `scripts/manifest.py` path resolves incorrectly except by coincidence.
2. To check for drift against an earlier run: `python3 "${CLAUDE_SKILL_DIR}/scripts/manifest.py" diff --a manifest_old.json --b manifest_new.json`. The diff reports `identity_differences` (any changed identity field) separately from `file_differences` (changed/added/removed input files), plus the top-level `identical` flag.
3. Report the manifest's top-level `manifest_hash` and, for a diff, the `identical` flag and any listed differences, to the calling agent.

## Validation

- Exit code 0: success.
- Exit code 1: a listed input path (or `--dependencies` path) does not exist, or a manifest file is malformed — report `BLOCKED` on this check; do not fabricate a hash for a missing path.
- Exit code 2: bad CLI usage (e.g., missing required `--protocol-id`).

## Output contract

The generated manifest JSON (or diff JSON), passed through unmodified. The calling agent records the manifest path and hash in its handoff's "Protocol/artifact identity" field.

## Safety / non-authority

Fingerprinting inputs is not proof of reproducibility. `bt-experiment-integrity-reviewer` must independently attempt (or verify an independent attempt at) reproducing the result — a manifest existing, even with a clean hash, cannot by itself satisfy that role's integrity gate.

## Builder provenance

`SKILLSET_RESEARCH.md` → "Candidate: reproducibility-manifest". Role research: `BUILD_RESEARCH.md` §6 (`bt-backtest-engineer`) and §10 (`bt-experiment-integrity-reviewer`).
