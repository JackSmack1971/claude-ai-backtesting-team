#!/usr/bin/env python3
"""
Deterministic reproducibility manifest generator.

Hashes a set of files/directories (SHA-256) plus an explicit identity block
into a single JSON manifest, and can diff two manifests to detect drift.
No network access.

Canonical identity schema (all fields below are bound into `manifest_hash`;
changing ANY of them, even with byte-identical input files, changes the hash):
    - protocol_id        : caller-supplied protocol/config identity string (required)
    - seed                : caller-supplied deterministic/random seed state ("unspecified" if none)
    - git_commit          : commit SHA of the working tree at generation time
                             ("unavailable" if not in a git repo / git missing;
                             caller may override via --git-commit)
    - git_dirty           : true/false, or "unknown" if it could not be determined
    - dependencies_hash   : SHA-256 of a caller-supplied dependency manifest file
                             (requirements.txt, lockfile, etc.), or "unspecified"
    - runtime             : {python_version, platform} of the machine that generated the manifest
    - files               : {path: sha256} for every hashed input path

Non-identity metadata (recorded but explicitly EXCLUDED from `manifest_hash`):
    - generated_at_unix   : wall-clock timestamp of generation
    - note                : free-text caller note

A changed protocol_id (or seed, git_commit, git_dirty, dependencies_hash, or
runtime) with byte-identical files must NOT produce the same manifest_hash --
this is a hard identity-binding requirement, not a convenience field.

Usage:
    python3 manifest.py generate --inputs path1 path2 --protocol-id "protocol-v1" \
        --seed 42 --note "human-readable note" --out manifest.json
    python3 manifest.py diff --a manifest_old.json --b manifest_new.json

Exit codes:
    0 - success
    1 - a listed input path does not exist, or a manifest file is malformed
    2 - bad CLI usage
"""
import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time


def hash_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_path(path):
    if os.path.isfile(path):
        return {path: hash_file(path)}
    if os.path.isdir(path):
        out = {}
        for root, _, files in os.walk(path):
            for fn in sorted(files):
                p = os.path.join(root, fn)
                out[p] = hash_file(p)
        return out
    raise FileNotFoundError(path)


def detect_git_commit():
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5, check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return "unavailable"
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def detect_git_dirty():
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=5, check=False,
        )
        if result.returncode == 0:
            return bool(result.stdout.strip())
        return "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def hash_dependencies(path):
    if path is None:
        return "unspecified"
    return hash_file(path)


def cmd_generate(args):
    entries = {}
    try:
        for p in args.inputs:
            entries.update(hash_path(p))
    except FileNotFoundError as e:
        print(json.dumps({"error": f"input path does not exist: {e}"}), file=sys.stderr)
        sys.exit(1)

    try:
        deps_hash = hash_dependencies(args.dependencies)
    except FileNotFoundError as e:
        print(json.dumps({"error": f"dependencies path does not exist: {e}"}), file=sys.stderr)
        sys.exit(1)

    identity = {
        "protocol_id": args.protocol_id,
        "seed": args.seed if args.seed is not None else "unspecified",
        "git_commit": args.git_commit if args.git_commit else detect_git_commit(),
        "git_dirty": detect_git_dirty() if args.git_commit is None else "unknown",
        "dependencies_hash": deps_hash,
        "runtime": {
            "python_version": platform.python_version(),
            "platform": platform.platform(),
        },
        "files": entries,
    }
    manifest_hash = hashlib.sha256(
        json.dumps(identity, sort_keys=True).encode("utf-8")
    ).hexdigest()

    manifest = {
        **identity,
        "generated_at_unix": int(time.time()),
        "note": args.note or "",
        "manifest_hash": manifest_hash,
    }

    out_str = json.dumps(manifest, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w") as f:
            f.write(out_str)
    print(out_str)
    sys.exit(0)


IDENTITY_FIELDS = ["protocol_id", "seed", "git_commit", "git_dirty", "dependencies_hash", "runtime"]


def cmd_diff(args):
    try:
        with open(args.a) as f:
            man_a = json.load(f)
        with open(args.b) as f:
            man_b = json.load(f)
    except Exception as e:
        print(json.dumps({"error": f"malformed manifest file: {e}"}), file=sys.stderr)
        sys.exit(1)

    files_a = man_a.get("files", {})
    files_b = man_b.get("files", {})
    all_paths = sorted(set(files_a) | set(files_b))
    file_diffs = []
    for p in all_paths:
        ha, hb = files_a.get(p), files_b.get(p)
        if ha != hb:
            file_diffs.append({"path": p, "hash_a": ha, "hash_b": hb, "status": "changed" if (ha and hb) else ("added" if hb and not ha else "removed")})

    identity_diffs = []
    for field in IDENTITY_FIELDS:
        va, vb = man_a.get(field), man_b.get(field)
        if va != vb:
            identity_diffs.append({"field": field, "value_a": va, "value_b": vb})

    result = {
        "manifest_hash_a": man_a.get("manifest_hash"),
        "manifest_hash_b": man_b.get("manifest_hash"),
        "identical": man_a.get("manifest_hash") == man_b.get("manifest_hash"),
        "identity_differences": identity_diffs,
        "file_differences": file_diffs,
    }
    print(json.dumps(result, indent=2))
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Reproducibility manifest generator/differ")
    sub = parser.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate")
    g.add_argument("--inputs", nargs="+", required=True)
    g.add_argument("--protocol-id", type=str, required=True, help="Canonical protocol/config identity bound into manifest_hash")
    g.add_argument("--seed", type=str, default=None, help="Deterministic/random seed state, bound into manifest_hash")
    g.add_argument("--git-commit", type=str, default=None, help="Override auto-detected git commit; also suppresses dirty-state auto-detection")
    g.add_argument("--dependencies", type=str, default=None, help="Path to a dependency manifest (requirements.txt, lockfile) to hash into dependencies_hash")
    g.add_argument("--note", type=str, default="", help="Free-text note; NOT bound into manifest_hash")
    g.add_argument("--out", type=str, default=None)
    g.set_defaults(func=cmd_generate)

    d = sub.add_parser("diff")
    d.add_argument("--a", required=True)
    d.add_argument("--b", required=True)
    d.set_defaults(func=cmd_diff)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
