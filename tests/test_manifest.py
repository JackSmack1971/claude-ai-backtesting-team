#!/usr/bin/env python3
"""
Black-box tests for .claude/skills/reproducibility-manifest/scripts/manifest.py.

Invokes the script as a subprocess (never imports it) so exit codes,
stdout/stderr contracts, and arbitrary-cwd invocation are all verified
against the documented contract in SKILL.md.

Run: python3 tests/test_manifest.py
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO_ROOT, ".claude", "skills", "reproducibility-manifest", "scripts", "manifest.py")


def run(args, cwd):
    return subprocess.run(
        [sys.executable, SCRIPT, *args],
        cwd=cwd, capture_output=True, text=True, timeout=30,
    )


def make_input_file(tmp, name="input.txt", content="hello"):
    path = os.path.join(tmp, name)
    with open(path, "w") as f:
        f.write(content)
    return path


class TestArbitraryCwd(unittest.TestCase):
    def test_runs_from_unrelated_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = make_input_file(tmp)
            with tempfile.TemporaryDirectory() as other_cwd:
                result = run(
                    ["generate", "--inputs", input_path, "--protocol-id", "proto-1"],
                    cwd=other_cwd,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                json.loads(result.stdout)


class TestSuccessPath(unittest.TestCase):
    def test_generate_basic(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = make_input_file(tmp)
            result = run(["generate", "--inputs", input_path, "--protocol-id", "proto-1"], cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            out = json.loads(result.stdout)
            self.assertEqual(out["protocol_id"], "proto-1")
            self.assertIn(input_path, out["files"])
            self.assertEqual(len(out["manifest_hash"]), 64)

    def test_generate_writes_out_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = make_input_file(tmp)
            out_path = os.path.join(tmp, "manifest.json")
            result = run(["generate", "--inputs", input_path, "--protocol-id", "p1", "--out", out_path], cwd=tmp)
            self.assertEqual(result.returncode, 0)
            with open(out_path) as f:
                data = json.load(f)
            self.assertIn("manifest_hash", data)

    def test_diff_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = make_input_file(tmp)
            a = os.path.join(tmp, "a.json")
            b = os.path.join(tmp, "b.json")
            run(["generate", "--inputs", input_path, "--protocol-id", "p1", "--out", a], cwd=tmp)
            run(["generate", "--inputs", input_path, "--protocol-id", "p1", "--out", b], cwd=tmp)
            result = run(["diff", "--a", a, "--b", b], cwd=tmp)
            self.assertEqual(result.returncode, 0)
            out = json.loads(result.stdout)
            # generated_at_unix differs between the two runs but must not affect identity.
            self.assertTrue(out["identical"])
            self.assertEqual(out["identity_differences"], [])
            self.assertEqual(out["file_differences"], [])


class TestIdentityBinding(unittest.TestCase):
    """Core defect-4 regression: a changed protocol identity with identical
    files must NOT silently retain the same canonical run identity."""

    def test_different_protocol_id_changes_hash_with_identical_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = make_input_file(tmp)
            r1 = run(["generate", "--inputs", input_path, "--protocol-id", "protocol-v1", "--git-commit", "abc123"], cwd=tmp)
            r2 = run(["generate", "--inputs", input_path, "--protocol-id", "protocol-v2", "--git-commit", "abc123"], cwd=tmp)
            out1, out2 = json.loads(r1.stdout), json.loads(r2.stdout)
            self.assertEqual(out1["files"], out2["files"])
            self.assertNotEqual(out1["manifest_hash"], out2["manifest_hash"])

    def test_different_seed_changes_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = make_input_file(tmp)
            r1 = run(["generate", "--inputs", input_path, "--protocol-id", "p", "--seed", "1", "--git-commit", "c"], cwd=tmp)
            r2 = run(["generate", "--inputs", input_path, "--protocol-id", "p", "--seed", "2", "--git-commit", "c"], cwd=tmp)
            out1, out2 = json.loads(r1.stdout), json.loads(r2.stdout)
            self.assertNotEqual(out1["manifest_hash"], out2["manifest_hash"])

    def test_different_git_commit_changes_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = make_input_file(tmp)
            r1 = run(["generate", "--inputs", input_path, "--protocol-id", "p", "--git-commit", "aaa"], cwd=tmp)
            r2 = run(["generate", "--inputs", input_path, "--protocol-id", "p", "--git-commit", "bbb"], cwd=tmp)
            out1, out2 = json.loads(r1.stdout), json.loads(r2.stdout)
            self.assertNotEqual(out1["manifest_hash"], out2["manifest_hash"])

    def test_note_and_timestamp_excluded_from_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = make_input_file(tmp)
            r1 = run(["generate", "--inputs", input_path, "--protocol-id", "p", "--git-commit", "c", "--note", "run one"], cwd=tmp)
            r2 = run(["generate", "--inputs", input_path, "--protocol-id", "p", "--git-commit", "c", "--note", "a totally different note"], cwd=tmp)
            out1, out2 = json.loads(r1.stdout), json.loads(r2.stdout)
            self.assertNotEqual(out1["note"], out2["note"])
            self.assertEqual(out1["manifest_hash"], out2["manifest_hash"])

    def test_identical_inputs_produce_identical_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = make_input_file(tmp)
            args = ["generate", "--inputs", input_path, "--protocol-id", "p", "--seed", "7", "--git-commit", "c"]
            r1 = run(args, cwd=tmp)
            r2 = run(args, cwd=tmp)
            out1, out2 = json.loads(r1.stdout), json.loads(r2.stdout)
            self.assertEqual(out1["manifest_hash"], out2["manifest_hash"])


class TestOutputSchema(unittest.TestCase):
    def test_schema_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = make_input_file(tmp)
            result = run(["generate", "--inputs", input_path, "--protocol-id", "p"], cwd=tmp)
            out = json.loads(result.stdout)
            for key in ("protocol_id", "seed", "git_commit", "git_dirty", "dependencies_hash",
                        "runtime", "files", "generated_at_unix", "note", "manifest_hash"):
                self.assertIn(key, out)
            self.assertIn("python_version", out["runtime"])
            self.assertIn("platform", out["runtime"])


class TestMalformedInput(unittest.TestCase):
    def test_missing_input_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run(["generate", "--inputs", os.path.join(tmp, "does-not-exist"), "--protocol-id", "p"], cwd=tmp)
            self.assertEqual(result.returncode, 1)
            err = json.loads(result.stderr)
            self.assertIn("error", err)

    def test_missing_dependencies_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = make_input_file(tmp)
            result = run(["generate", "--inputs", input_path, "--protocol-id", "p", "--dependencies", os.path.join(tmp, "nope.txt")], cwd=tmp)
            self.assertEqual(result.returncode, 1)

    def test_malformed_manifest_diff(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = os.path.join(tmp, "bad.json")
            with open(bad, "w") as f:
                f.write("{not json")
            good_input = make_input_file(tmp)
            good = os.path.join(tmp, "good.json")
            run(["generate", "--inputs", good_input, "--protocol-id", "p", "--out", good], cwd=tmp)
            result = run(["diff", "--a", bad, "--b", good], cwd=tmp)
            self.assertEqual(result.returncode, 1)


class TestCliMisuse(unittest.TestCase):
    def test_missing_protocol_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            input_path = make_input_file(tmp)
            result = run(["generate", "--inputs", input_path], cwd=tmp)
            self.assertEqual(result.returncode, 2)

    def test_missing_subcommand(self):
        result = run([], cwd=REPO_ROOT)
        self.assertNotEqual(result.returncode, 0)

    def test_missing_inputs_flag(self):
        result = run(["generate", "--protocol-id", "p"], cwd=REPO_ROOT)
        self.assertEqual(result.returncode, 2)


class TestBoundaryCases(unittest.TestCase):
    def test_directory_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            sub = os.path.join(tmp, "sub")
            os.makedirs(sub)
            make_input_file(tmp, name=os.path.join("sub", "a.txt"), content="a")
            result = run(["generate", "--inputs", sub, "--protocol-id", "p"], cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            out = json.loads(result.stdout)
            self.assertEqual(len(out["files"]), 1)

    def test_diff_detects_added_and_removed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            f1 = make_input_file(tmp, name="f1.txt")
            f2 = make_input_file(tmp, name="f2.txt")
            a = os.path.join(tmp, "a.json")
            b = os.path.join(tmp, "b.json")
            run(["generate", "--inputs", f1, "--protocol-id", "p", "--out", a], cwd=tmp)
            run(["generate", "--inputs", f2, "--protocol-id", "p", "--out", b], cwd=tmp)
            result = run(["diff", "--a", a, "--b", b], cwd=tmp)
            out = json.loads(result.stdout)
            self.assertFalse(out["identical"])
            statuses = {d["status"] for d in out["file_differences"]}
            self.assertEqual(statuses, {"added", "removed"})


class TestSkillContractConsistency(unittest.TestCase):
    def test_skill_md_documents_matching_contract(self):
        skill_md = os.path.join(REPO_ROOT, ".claude", "skills", "reproducibility-manifest", "SKILL.md")
        with open(skill_md) as f:
            text = f.read()
        self.assertIn("${CLAUDE_SKILL_DIR}", text)
        self.assertIn("protocol_id", text)
        self.assertIn("manifest_hash", text)
        self.assertIn("Exit code 0", text)
        self.assertIn("Exit code 1", text)
        self.assertIn("Exit code 2", text)


if __name__ == "__main__":
    unittest.main()
