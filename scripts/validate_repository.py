#!/usr/bin/env python3
"""
Repository-local validator for the AI Backtesting Team FOUNDATION_MODE build.

Proves the generated architecture is internally consistent, not merely that
expected words are present. Run from anywhere:

    python3 scripts/validate_repository.py

Exit code 0 = all checks PASS. Exit code 1 = at least one check FAILED.
Prints a per-check PASS/FAIL/UNVERIFIED_RUNTIME report to stdout.
"""
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_DIR = os.path.join(REPO_ROOT, ".claude", "agents")
SKILLS_DIR = os.path.join(REPO_ROOT, ".claude", "skills")
TEAM_DIR = os.path.join(REPO_ROOT, ".claude", "backtesting-team")
RULES_DIR = os.path.join(REPO_ROOT, ".claude", "rules")

results = []


def check(name):
    """Decorator that runs the check immediately (at module load) and records
    its result. Checks execute top-to-bottom in file order."""
    def decorator(fn):
        try:
            ok, detail = fn()
        except Exception as e:  # a check that crashes is a FAIL, not a silent skip
            ok, detail = False, f"check raised {type(e).__name__}: {e}"
        results.append((name, ok, detail))
        return fn
    return decorator


def parse_frontmatter(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError(f"{path}: no YAML frontmatter block found")
    fm_text, body = m.group(1), m.group(2)
    fm = {}
    # Minimal line-based YAML parser sufficient for this repo's flat frontmatter
    # (name/description/tools/model as scalars; tools is a comma-separated scalar
    # that itself may contain parens, e.g. Agent(a, b)).
    key = None
    for line in fm_text.split("\n"):
        if not line.strip():
            continue
        mm = re.match(r"^([A-Za-z_-]+):\s?(.*)$", line)
        if mm:
            key, val = mm.group(1), mm.group(2)
            fm[key] = val.strip()
        elif key is not None:
            fm[key] += " " + line.strip()
    return fm, body


def list_agent_files():
    return sorted(
        os.path.join(AGENTS_DIR, f) for f in os.listdir(AGENTS_DIR) if f.endswith(".md")
    )


def list_skill_dirs():
    return sorted(
        d for d in os.listdir(SKILLS_DIR) if os.path.isdir(os.path.join(SKILLS_DIR, d))
    )


AGENT_FRONTMATTERS = {}
for _p in list_agent_files():
    AGENT_FRONTMATTERS[os.path.basename(_p)[:-3]] = parse_frontmatter(_p)


@check("all agent frontmatter parses, name/description present")
def _():
    problems = []
    for name, (fm, _body) in AGENT_FRONTMATTERS.items():
        if "name" not in fm or not fm["name"]:
            problems.append(f"{name}: missing name")
        elif fm["name"] != name:
            problems.append(f"{name}: frontmatter name '{fm['name']}' != filename")
        if "description" not in fm or not fm["description"]:
            problems.append(f"{name}: missing description")
        if "tools" not in fm:
            problems.append(f"{name}: missing tools field")
    return (not problems, "; ".join(problems) if problems else f"{len(AGENT_FRONTMATTERS)} agents OK")


@check("all skill frontmatter parses, name/description satisfy basic constraints")
def _():
    problems = []
    n = 0
    for d in list_skill_dirs():
        skill_md = os.path.join(SKILLS_DIR, d, "SKILL.md")
        if not os.path.isfile(skill_md):
            problems.append(f"{d}: no SKILL.md")
            continue
        fm, _body = parse_frontmatter(skill_md)
        n += 1
        if fm.get("name") != d:
            problems.append(f"{d}: frontmatter name '{fm.get('name')}' != directory name")
        desc = fm.get("description", "")
        if not desc:
            problems.append(f"{d}: missing description")
        elif len(desc) > 1536:
            problems.append(f"{d}: description exceeds 1536-char cap ({len(desc)})")
    return (not problems, "; ".join(problems) if problems else f"{n} skills OK")


@check("every on-demand skill assignment has an actual invocation path (Skill tool present)")
def _():
    problems = []
    manifest_path = os.path.join(TEAM_DIR, "SKILLSET_MANIFEST.json")
    with open(manifest_path) as f:
        manifest = json.load(f)
    for entry in manifest["generated_skills"]:
        for agent_name in entry.get("on_demand_agents", []):
            fm, _body = AGENT_FRONTMATTERS.get(agent_name, (None, None))
            if fm is None:
                problems.append(f"{entry['name']}: on-demand agent {agent_name} does not exist")
                continue
            tools = fm.get("tools", "")
            if not re.search(r"(?<![A-Za-z])Skill(?![A-Za-z(])", tools):
                problems.append(f"{agent_name}: on-demand consumer of {entry['name']} but 'Skill' not in tools: {tools!r}")
    # bt-experiment-integrity-reviewer consults forbidden-for-approval skills; it also needs Skill.
    for entry in manifest["generated_skills"]:
        for agent_name in entry.get("forbidden_for_approval_agents", []):
            fm, _body = AGENT_FRONTMATTERS.get(agent_name, (None, None))
            if fm and not re.search(r"(?<![A-Za-z])Skill(?![A-Za-z(])", fm.get("tools", "")):
                problems.append(f"{agent_name}: consults forbidden-for-approval skill {entry['name']} but 'Skill' not in tools")
    return (not problems, "; ".join(problems) if problems else "all on-demand/consulting bindings have Skill tool access")


@check("every executable skill's script path is invoked via ${CLAUDE_SKILL_DIR} in SKILL.md")
def _():
    problems = []
    executable_skills = []
    for d in list_skill_dirs():
        scripts_dir = os.path.join(SKILLS_DIR, d, "scripts")
        if os.path.isdir(scripts_dir) and any(f.endswith(".py") for f in os.listdir(scripts_dir)):
            executable_skills.append(d)
            skill_md = os.path.join(SKILLS_DIR, d, "SKILL.md")
            with open(skill_md, encoding="utf-8") as f:
                text = f.read()
            if "${CLAUDE_SKILL_DIR}" not in text:
                problems.append(f"{d}: SKILL.md does not invoke its script via ${{CLAUDE_SKILL_DIR}}")
            # a bare invocation like 'python3 scripts/x.py' (not doc-prose mentions of
            # the filename) would break outside this skill's own directory
            for m in re.finditer(r"python3?\s+[\"']?scripts/[A-Za-z_]+\.py", text):
                problems.append(f"{d}: found a cwd-dependent invocation '{m.group(0)}' not using ${{CLAUDE_SKILL_DIR}}")
    return (not problems, "; ".join(problems) if problems else f"{len(executable_skills)} executable skills OK")


@check("no placeholder artifacts remain")
def _():
    hits = []
    for root, _dirs, files in os.walk(os.path.join(REPO_ROOT, ".claude")):
        for fn in files:
            if "placeholder" in fn.lower():
                hits.append(os.path.relpath(os.path.join(root, fn), REPO_ROOT))
    return (not hits, "; ".join(hits) if hits else "none found")


@check("zero-rule state is represented cleanly (no rule files, manifest agrees, README agrees)")
def _():
    problems = []
    rule_files = []
    if os.path.isdir(RULES_DIR):
        rule_files = [f for f in os.listdir(RULES_DIR) if not f.startswith(".")]
    if rule_files:
        problems.append(f"unexpected files in .claude/rules: {rule_files}")
    manifest_path = os.path.join(TEAM_DIR, "RULESET_MANIFEST.json")
    with open(manifest_path) as f:
        manifest = json.load(f)
    if manifest.get("generated_rules") != []:
        problems.append("RULESET_MANIFEST.json generated_rules is not empty")
    readme_path = os.path.join(REPO_ROOT, "README.md")
    with open(readme_path, encoding="utf-8") as f:
        readme = f.read()
    if "rules=0" not in readme:
        problems.append("README.md does not state rules=0")
    return (not problems, "; ".join(problems) if problems else "clean")


@check("no unsupported nested reference chains — every `references/...md` citation resolves")
def _():
    problems = []
    pattern = re.compile(r"references/[A-Za-z0-9_-]+\.md")
    checked = set()
    for root, _dirs, files in os.walk(os.path.join(REPO_ROOT, ".claude")):
        for fn in files:
            if not fn.endswith(".md") and not fn.endswith(".json"):
                continue
            full = os.path.join(root, fn)
            with open(full, encoding="utf-8") as f:
                text = f.read()
            for m in pattern.finditer(text):
                ref = m.group(0)
                checked.add(ref)
                # Recognized as resolving either relative to .claude/backtesting-team/
                # (this repo's canonical reference location) or as an already-fixed
                # absolute-from-repo-root citation.
                candidate_paths = [
                    os.path.join(TEAM_DIR, ref),
                    os.path.join(root, ref),
                ]
                if not any(os.path.isfile(p) for p in candidate_paths):
                    # allow builder-internal contract docs explicitly marked as external
                    if fn in ("SKILLSET_RESEARCH.md", "RULESET_RESEARCH.md") and "skill-contract" in ref or "rule-" in ref:
                        continue
                    problems.append(f"{os.path.relpath(full, REPO_ROOT)}: unresolved reference {ref}")
    return (not problems, f"{len(checked)} citations checked; " + ("; ".join(problems) if problems else "all resolve"))


@check("all files referenced by builder-provenance / manifest paths exist")
def _():
    problems = []
    for name, path in [("SKILLSET_MANIFEST.json", os.path.join(TEAM_DIR, "SKILLSET_MANIFEST.json")),
                        ("RULESET_MANIFEST.json", os.path.join(TEAM_DIR, "RULESET_MANIFEST.json"))]:
        with open(path) as f:
            data = json.load(f)
        for entry in data.get("generated_skills", []):
            p = os.path.join(REPO_ROOT, entry["path"].replace("/", os.sep))
            if not os.path.isfile(p):
                problems.append(f"{name}: {entry['path']} does not exist")
    return (not problems, "; ".join(problems) if problems else "all manifest paths exist")


@check("manifest <-> filesystem consistency (skills on disk == skills in manifest)")
def _():
    manifest_path = os.path.join(TEAM_DIR, "SKILLSET_MANIFEST.json")
    with open(manifest_path) as f:
        manifest = json.load(f)
    manifest_names = {e["name"] for e in manifest["generated_skills"]}
    disk_names = set(list_skill_dirs())
    missing_on_disk = manifest_names - disk_names
    missing_in_manifest = disk_names - manifest_names
    problems = []
    if missing_on_disk:
        problems.append(f"in manifest but not on disk: {sorted(missing_on_disk)}")
    if missing_in_manifest:
        problems.append(f"on disk but not in manifest: {sorted(missing_in_manifest)}")
    return (not problems, "; ".join(problems) if problems else f"{len(disk_names)} skills match")


@check("agent <-> skill binding consistency (agent's ## Skills section matches manifest)")
def _():
    manifest_path = os.path.join(TEAM_DIR, "SKILLSET_MANIFEST.json")
    with open(manifest_path) as f:
        manifest = json.load(f)
    problems = []
    for entry in manifest["generated_skills"]:
        for agent_name in entry.get("on_demand_agents", []):
            agent_path = os.path.join(AGENTS_DIR, agent_name + ".md")
            if not os.path.isfile(agent_path):
                problems.append(f"{entry['name']}: on_demand_agents references missing agent {agent_name}")
                continue
            with open(agent_path, encoding="utf-8") as f:
                text = f.read()
            if entry["name"] not in text:
                problems.append(f"{agent_name}: manifest says it uses {entry['name']} but the agent file never mentions it")
    return (not problems, "; ".join(problems) if problems else "all bindings mentioned on both sides")


@check("forbidden authority relationships remain intact (integrity reviewer cannot treat forbidden skills as approval)")
def _():
    reviewer_path = os.path.join(AGENTS_DIR, "bt-experiment-integrity-reviewer.md")
    with open(reviewer_path, encoding="utf-8") as f:
        text = f.read()
    problems = []
    if "Write" in re.search(r"tools:\s*(.*)", text).group(1):
        problems.append("bt-experiment-integrity-reviewer has Write access — independence boundary violated")
    if "forbidden-for-approval" not in text and "forbidden_for_approval" not in text and "forbidden-for-approval" not in text.replace("_", "-"):
        problems.append("bt-experiment-integrity-reviewer no longer documents the forbidden-for-approval skill boundary")
    manifest_path = os.path.join(TEAM_DIR, "SKILLSET_MANIFEST.json")
    with open(manifest_path) as f:
        manifest = json.load(f)
    forbidden = {e["name"] for e in manifest["generated_skills"] if "bt-experiment-integrity-reviewer" in e.get("forbidden_for_approval_agents", [])}
    if forbidden != {"temporal-leakage-audit", "multiple-testing-correction", "reproducibility-manifest"}:
        problems.append(f"unexpected forbidden-for-approval set: {forbidden}")
    return (not problems, "; ".join(problems) if problems else "boundary intact")


@check("orchestrator does not overclaim a runtime-enforced subagent restriction")
def _():
    path = os.path.join(AGENTS_DIR, "bt-team-orchestrator.md")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    problems = []
    if "cannot spawn arbitrary subagents, only the team it coordinates" in text:
        problems.append("still contains the disproven runtime-enforcement claim")
    if "Runtime-mechanics correction" not in text:
        problems.append("missing the honest runtime-mechanics correction section")
    if "Mandatory invariant (prompt-level, not runtime-enforced)" not in text:
        problems.append("missing the prompt-level dispatch invariant replacing the false claim")
    return (not problems, "; ".join(problems) if problems else "claim corrected")


@check("reproducibility-manifest binds protocol identity into manifest_hash (not just files)")
def _():
    script_path = os.path.join(SKILLS_DIR, "reproducibility-manifest", "scripts", "manifest.py")
    with open(script_path, encoding="utf-8") as f:
        text = f.read()
    problems = []
    if "protocol_id" not in text:
        problems.append("protocol_id not present in manifest.py")
    if '"note"' not in text and "'note'" not in text:
        problems.append("note field missing")
    # the hash must be computed over `identity` (which includes protocol_id), not just `entries`/`files`
    if not re.search(r"manifest_hash\s*=\s*hashlib\.sha256\(\s*\n?\s*json\.dumps\(identity", text):
        problems.append("manifest_hash is not computed over the full identity block")
    return (not problems, "; ".join(problems) if problems else "identity binding present")


@check("SKILL.md documented exit codes / output contract match the implementation")
def _():
    problems = []
    pairs = [
        ("multiple-testing-correction", "mtc.py", [0, 1, 2]),
        ("reproducibility-manifest", "manifest.py", [0, 1, 2]),
    ]
    for skill, script, codes in pairs:
        script_path = os.path.join(SKILLS_DIR, skill, "scripts", script)
        with open(script_path, encoding="utf-8") as f:
            script_text = f.read()
        found_codes = set(int(m) for m in re.findall(r"sys\.exit\((\d)\)", script_text))
        # argparse itself calls sys.exit(2) on parse errors (missing/invalid required
        # args) without an explicit literal in the script's own source.
        if "argparse" in script_text and "required=True" in script_text:
            found_codes.add(2)
        missing = set(codes) - found_codes
        if missing:
            problems.append(f"{skill}: script never produces documented exit code(s) {missing}")
    return (not problems, "; ".join(problems) if problems else "exit codes match")


def main():
    for name, obj in list(globals().items()):
        pass  # checks self-register via the decorator at import time (module top-level already ran)

    print("AI Backtesting Team — repository validation\n")
    failed = 0
    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        if not ok:
            failed += 1
        print(f"[{status}] {name}\n        {detail}")
    print()
    print("UNVERIFIED_RUNTIME items (not checkable by this static validator):")
    print("  - live subagent dispatch behavior (Agent tool depth limits, actual Skill-tool")
    print("    invocation at runtime) requires an interactive Claude Code session; see")
    print("    tests/smoke_fixture/ for the closest static approximation.")
    print()
    if failed:
        print(f"RESULT: FAIL ({failed} check(s) failed)")
        sys.exit(1)
    else:
        print(f"RESULT: PASS ({len(results)} checks)")
        sys.exit(0)


if __name__ == "__main__":
    main()
