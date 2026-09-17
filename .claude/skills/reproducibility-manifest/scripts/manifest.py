#!/usr/bin/env python3
"""
Deterministic reproducibility manifest generator.

Hashes a set of files/directories (SHA-256) plus a free-text identity block
(e.g., config values, protocol id, git commit) into a single JSON manifest,
and can diff two manifests to detect drift. No network access.

Usage:
    python3 manifest.py generate --inputs path1 path2 --note "protocol v1, commit abc123" --out manifest.json
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


def cmd_generate(args):
    entries = {}
    try:
        for p in args.inputs:
            entries.update(hash_path(p))
    except FileNotFoundError as e:
        print(json.dumps({"error": f"input path does not exist: {e}"}), file=sys.stderr)
        sys.exit(1)

    manifest_body = {
        "generated_at_unix": int(time.time()),
        "note": args.note or "",
        "files": entries,
    }
    combined = hashlib.sha256(json.dumps(entries, sort_keys=True).encode("utf-8")).hexdigest()
    manifest = {**manifest_body, "manifest_hash": combined}

    out_str = json.dumps(manifest, indent=2, sort_keys=True)
    if args.out:
        with open(args.out, "w") as f:
            f.write(out_str)
    print(out_str)
    sys.exit(0)


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
    diffs = []
    for p in all_paths:
        ha, hb = files_a.get(p), files_b.get(p)
        if ha != hb:
            diffs.append({"path": p, "hash_a": ha, "hash_b": hb, "status": "changed" if (ha and hb) else ("added" if hb and not ha else "removed")})

    result = {
        "manifest_hash_a": man_a.get("manifest_hash"),
        "manifest_hash_b": man_b.get("manifest_hash"),
        "identical": man_a.get("manifest_hash") == man_b.get("manifest_hash"),
        "differences": diffs,
    }
    print(json.dumps(result, indent=2))
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Reproducibility manifest generator/differ")
    sub = parser.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate")
    g.add_argument("--inputs", nargs="+", required=True)
    g.add_argument("--note", type=str, default="")
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
