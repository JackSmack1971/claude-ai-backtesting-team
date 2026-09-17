#!/usr/bin/env python3
"""
Deterministic multiple-testing correction.

Applies Bonferroni (family-wise) or Benjamini-Hochberg (false discovery rate)
correction to a list of trial p-values. No network access, no repository
assumptions -- pure arithmetic over the JSON input.

Usage:
    python3 mtc.py --method bonferroni --alpha 0.05 --pvalues 0.001 0.02 0.04 0.20
    python3 mtc.py --method bh --alpha 0.10 --input trials.json

trials.json format (used with --input instead of --pvalues):
    {"trials": [{"id": "trial_1", "p_value": 0.001}, {"id": "trial_2", "p_value": 0.04}]}

Exit codes:
    0 - success, JSON result printed to stdout
    1 - malformed input (bad JSON, missing p_value, p_value out of [0,1], empty trial list)
    2 - bad CLI usage (invalid method, invalid alpha)
"""
import argparse
import json
import sys


def bonferroni(pvals, alpha):
    n = len(pvals)
    threshold = alpha / n
    return [p <= threshold for p in pvals], threshold


def benjamini_hochberg(pvals, alpha):
    n = len(pvals)
    order = sorted(range(n), key=lambda i: pvals[i])
    reject = [False] * n
    largest_k = -1
    for rank, idx in enumerate(order, start=1):
        crit = (rank / n) * alpha
        if pvals[idx] <= crit:
            largest_k = rank
    if largest_k >= 0:
        for rank, idx in enumerate(order, start=1):
            if rank <= largest_k:
                reject[idx] = True
    return reject, None


def main():
    parser = argparse.ArgumentParser(description="Multiple-testing correction (Bonferroni / Benjamini-Hochberg)")
    parser.add_argument("--method", choices=["bonferroni", "bh"], required=True)
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--pvalues", nargs="*", type=float, help="Inline p-values")
    parser.add_argument("--input", type=str, help="Path to a JSON file with a 'trials' list")
    args = parser.parse_args()

    if not (0 < args.alpha < 1):
        print(json.dumps({"error": "alpha must be in (0, 1)"}), file=sys.stderr)
        sys.exit(2)

    ids = None
    if args.input:
        try:
            with open(args.input, "r") as f:
                data = json.load(f)
            trials = data["trials"]
            if not trials:
                raise ValueError("empty trial list")
            ids = [t.get("id", str(i)) for i, t in enumerate(trials)]
            pvals = [float(t["p_value"]) for t in trials]
        except Exception as e:
            print(json.dumps({"error": f"malformed input file: {e}"}), file=sys.stderr)
            sys.exit(1)
    elif args.pvalues:
        pvals = args.pvalues
        ids = [str(i) for i in range(len(pvals))]
    else:
        print(json.dumps({"error": "provide --pvalues or --input"}), file=sys.stderr)
        sys.exit(1)

    if any(p < 0 or p > 1 for p in pvals):
        print(json.dumps({"error": "all p-values must be in [0, 1]"}), file=sys.stderr)
        sys.exit(1)

    if args.method == "bonferroni":
        reject, threshold = bonferroni(pvals, args.alpha)
    else:
        reject, threshold = benjamini_hochberg(pvals, args.alpha)

    result = {
        "method": args.method,
        "alpha": args.alpha,
        "n_trials": len(pvals),
        "threshold": threshold,
        "results": [
            {"id": ids[i], "p_value": pvals[i], "reject_null": reject[i]}
            for i in range(len(pvals))
        ],
        "n_significant": sum(reject),
    }
    print(json.dumps(result, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
