#!/usr/bin/env python3
"""
Black-box tests for .claude/skills/multiple-testing-correction/scripts/mtc.py.

Invokes the script as a subprocess (never imports it) so that:
  (a) exit codes and stdout/stderr contracts are verified as documented in SKILL.md, and
  (b) the script is proven to work from an arbitrary cwd, not just the repo root.

Run: python3 tests/test_mtc.py
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, ".claude", "skills", "multiple-testing-correction", "scripts", "mtc.py")


def run(args, cwd):
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        cwd=cwd, capture_output=True, text=True, timeout=30,
    )


class TestArbitraryCwd(unittest.TestCase):
    def test_runs_from_unrelated_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run(["--method", "bonferroni", "--alpha", "0.05", "--pvalues", "0.001", "0.5"], cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            json.loads(result.stdout)


class TestSuccessPath(unittest.TestCase):
    def test_bonferroni_inline_pvalues(self):
        result = run(["--method", "bonferroni", "--alpha", "0.05", "--pvalues", "0.001", "0.02", "0.04", "0.20"], cwd=REPO_ROOT)
        self.assertEqual(result.returncode, 0)
        out = json.loads(result.stdout)
        self.assertEqual(out["method"], "bonferroni")
        self.assertEqual(out["n_trials"], 4)
        self.assertAlmostEqual(out["threshold"], 0.0125)
        self.assertEqual([r["reject_null"] for r in out["results"]], [True, False, False, False])
        self.assertEqual(out["n_significant"], 1)

    def test_bh_input_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            trials_path = os.path.join(tmp, "trials.json")
            with open(trials_path, "w") as f:
                json.dump({"trials": [
                    {"id": "a", "p_value": 0.001},
                    {"id": "b", "p_value": 0.01},
                    {"id": "c", "p_value": 0.03},
                    {"id": "d", "p_value": 0.5},
                ]}, f)
            result = run(["--method", "bh", "--alpha", "0.10", "--input", trials_path], cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            out = json.loads(result.stdout)
            self.assertEqual(out["method"], "bh")
            self.assertIsNone(out["threshold"])  # BH has no single scalar threshold
            self.assertEqual(len(out["results"]), 4)
            ids = [r["id"] for r in out["results"]]
            self.assertEqual(ids, ["a", "b", "c", "d"])


class TestOutputSchema(unittest.TestCase):
    def test_schema_keys(self):
        result = run(["--method", "bonferroni", "--alpha", "0.05", "--pvalues", "0.01"], cwd=REPO_ROOT)
        out = json.loads(result.stdout)
        for key in ("method", "alpha", "n_trials", "threshold", "results", "n_significant"):
            self.assertIn(key, out)
        for row in out["results"]:
            for key in ("id", "p_value", "reject_null"):
                self.assertIn(key, row)


class TestMalformedInput(unittest.TestCase):
    def test_bad_json_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad_path = os.path.join(tmp, "bad.json")
            with open(bad_path, "w") as f:
                f.write("{not valid json")
            result = run(["--method", "bonferroni", "--input", bad_path], cwd=tmp)
            self.assertEqual(result.returncode, 1)
            err = json.loads(result.stderr)
            self.assertIn("error", err)

    def test_missing_p_value_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "trials.json")
            with open(path, "w") as f:
                json.dump({"trials": [{"id": "a"}]}, f)
            result = run(["--method", "bonferroni", "--input", path], cwd=tmp)
            self.assertEqual(result.returncode, 1)

    def test_empty_trial_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "trials.json")
            with open(path, "w") as f:
                json.dump({"trials": []}, f)
            result = run(["--method", "bonferroni", "--input", path], cwd=tmp)
            self.assertEqual(result.returncode, 1)

    def test_pvalue_out_of_range(self):
        result = run(["--method", "bonferroni", "--pvalues", "1.5"], cwd=REPO_ROOT)
        self.assertEqual(result.returncode, 1)

    def test_no_input_provided(self):
        result = run(["--method", "bonferroni"], cwd=REPO_ROOT)
        self.assertEqual(result.returncode, 1)


class TestCliMisuse(unittest.TestCase):
    def test_invalid_method(self):
        result = run(["--method", "not-a-method", "--pvalues", "0.01"], cwd=REPO_ROOT)
        self.assertNotEqual(result.returncode, 0)

    def test_invalid_alpha(self):
        result = run(["--method", "bonferroni", "--alpha", "1.5", "--pvalues", "0.01"], cwd=REPO_ROOT)
        self.assertEqual(result.returncode, 2)

    def test_missing_method_flag(self):
        result = run(["--pvalues", "0.01"], cwd=REPO_ROOT)
        self.assertNotEqual(result.returncode, 0)


class TestDeterminism(unittest.TestCase):
    def test_repeated_runs_identical(self):
        args = ["--method", "bh", "--alpha", "0.05", "--pvalues", "0.001", "0.02", "0.3", "0.9"]
        first = run(args, cwd=REPO_ROOT)
        second = run(args, cwd=REPO_ROOT)
        self.assertEqual(first.stdout, second.stdout)


class TestBoundaryCases(unittest.TestCase):
    def test_single_trial(self):
        result = run(["--method", "bonferroni", "--alpha", "0.05", "--pvalues", "0.03"], cwd=REPO_ROOT)
        out = json.loads(result.stdout)
        self.assertEqual(out["n_trials"], 1)
        self.assertAlmostEqual(out["threshold"], 0.05)

    def test_pvalue_exactly_zero_and_one(self):
        result = run(["--method", "bonferroni", "--alpha", "0.05", "--pvalues", "0.0", "1.0"], cwd=REPO_ROOT)
        self.assertEqual(result.returncode, 0)


class TestSkillContractConsistency(unittest.TestCase):
    """SKILL.md documents exit codes 0/1/2 and the CLAUDE_SKILL_DIR invocation form."""

    def test_skill_md_documents_matching_exit_codes(self):
        skill_md = os.path.join(REPO_ROOT, ".claude", "skills", "multiple-testing-correction", "SKILL.md")
        with open(skill_md) as f:
            text = f.read()
        self.assertIn("Exit code 0", text)
        self.assertIn("Exit code 1", text)
        self.assertIn("Exit code 2", text)
        self.assertIn("${CLAUDE_SKILL_DIR}", text)


if __name__ == "__main__":
    unittest.main()
