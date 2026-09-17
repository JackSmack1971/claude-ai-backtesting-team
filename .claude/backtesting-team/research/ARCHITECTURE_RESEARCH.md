# Build Architecture Research

## Repository snapshot

- Repository root: none. This build ran in a stateless chat/container environment with no `.git`, no source tree, and no data/storage layer to inspect.
- Working tree: not applicable (no repository).
- Languages/runtimes: unknown — not evidenced.
- Data sources/storage formats: unknown — not evidenced.
- Strategy/asset classes: none evidenced. The user's request said only "build a full backtesting team" with no market, framework, or language named.
- Holding/data frequency: unknown.
- Backtest/experiment frameworks: none evidenced.
- Existing Claude configuration: none found (no `.claude/CLAUDE.md`, `.claude/rules/`, `.claude/skills/`, `.claude/agents/`, hooks, or settings).
- Reusable validation tooling: none found.
- Unresolved project facts: target language/runtime, target market(s) (equities/futures/crypto/FX), data vendor and timestamp semantics, execution venue mechanics, existing test/lint tooling, and any pre-existing experiment or model registry.

**Mode: `FOUNDATION_MODE`.** No substantive repository exists. This build produces a portable baseline team, a minimal research-derived generic skill corpus, and an explicitly empty `.claude/rules/` corpus (see `RULESET_RESEARCH.md`). It does not claim repository-specific optimality, does not invent path-scoped rules, and does not encode framework- or market-specific thresholds.

## Claude extension mechanics

Verified against current official Anthropic documentation, accessed 2026-09-17.

### Source: Create custom subagents
- Publisher/author: Anthropic (code.claude.com)
- URL: https://code.claude.com/docs/en/sub-agents.md
- Accessed: 2026-09-17
- Source class: official-doc
- Claim class: mechanics-sensitive
- Relevant claim: Subagent files use YAML frontmatter with required `name` and `description`; optional fields include `tools` (allowlist), `disallowedTools` (denylist, applied before `tools`), `model`, `skills` (full content preloaded into the subagent's context at startup), `permissionMode`, `mcpServers`, `hooks`, `memory`, `omitClaudeMd`. A subagent not listing `skills` can still discover and invoke project/user/plugin skills through the Skill tool during execution unless `Skill` is removed from `tools`/added to `disallowedTools`. Combined subagent `description` fields have a 15,000-token budget before Claude Code warns at startup.
- Applies to: agent-layer generation (Phase 9), tool-policy decisions, skill runtime binding (preload vs on-demand)
- Design consequence: (1) every generated `bt-*` agent gets an intentional `tools:` allowlist rather than inheriting the full tool pool by default, narrowed further for independent-review roles; (2) skill preloading is reserved for skills every invocation of that agent needs, since preloaded content is injected at every startup; conditional workflows use the on-demand pattern (named trigger inside `## Skills`) instead; (3) agent `description` fields are kept to one or two sentences to protect the shared token budget.
- Limitations/disagreement: none.

### Source: Extend Claude with skills
- Publisher/author: Anthropic (code.claude.com)
- URL: https://code.claude.com/docs/en/skills
- Accessed: 2026-09-17
- Source class: official-doc
- Claim class: mechanics-sensitive
- Relevant claim: A skill is a `SKILL.md` file (required `name`, `description` frontmatter) under `.claude/skills/<name>/`, optionally with `references/` and `scripts/` subdirectories. Claude loads only the name+description at session start (~100 tokens) and loads the full body on match — progressive disclosure. `disable-model-invocation: true` removes a skill from Claude's own invocation surface (user-only, via `/skill-name`).
- Applies to: skill-layer generation (Phase 9), skill manifest/contract compliance
- Design consequence: generated skills stay narrow, single-directory (`references/`, `scripts/` one level deep, no reference-to-reference chains), and route on distinctive backtesting-domain trigger language in `description` rather than generic verbs.
- Limitations/disagreement: none.

### Source: .claude/rules Directory reference (secondary, corroborated by community bug reports)
- Publisher/author: Developers Digest, cross-checked against multiple independent GitHub issues filed against anthropics/claude-code
- URL: https://www.developersdigest.tech/guides/claude-rules-directory ; https://github.com/anthropics/claude-code/issues/13905 ; https://github.com/anthropics/claude-code/issues/22170
- Accessed: 2026-09-17
- Source class: secondary
- Claim class: mechanics-sensitive
- Relevant claim: `.claude/rules/*.md` files use a `paths:` YAML-list frontmatter field to scope a rule to matching files; an unscoped rule (no `paths`) loads on every session. Independent, unresolved community bug reports (filed against multiple recent versions) describe cases where quoted/list-form `paths:` frontmatter silently fails to load while unquoted single-line forms or the undocumented `globs:` key do load.
- Applies to: rule-layer generation (deferred in this build — see below)
- Design consequence: this build does not generate any rule file (see `RULESET_RESEARCH.md`), so the frontmatter-reliability question does not gate a production artifact here. It is recorded because a future repository-specific build consuming this research must re-verify current `paths:` loading behavior against the installed Claude Code version before trusting a generated rule to activate, rather than assuming the contract's documented format is bug-free.
- Limitations/disagreement: the official mechanics doc and the community reports disagree on reliability, not on the documented field name; this build treats the official `paths:` field name as correct per `rule-contract.md` and defers the reliability question rather than resolving it, since no rule is generated in FOUNDATION_MODE.

### Source: CLAUDE.md / project memory loading
- Publisher/author: Anthropic (code.claude.com), referenced within the sub-agents.md fetch above ("What loads at startup")
- URL: https://code.claude.com/docs/en/sub-agents.md
- Accessed: 2026-09-17
- Source class: official-doc
- Claim class: mechanics-sensitive
- Relevant claim: every non-fork subagent's startup context includes the full CLAUDE.md hierarchy (project, user, local, managed) unless `omitClaudeMd: true` is set; a subagent's system prompt does not include your conversation history.
- Applies to: placement-decision table below
- Design consequence: persistent project-wide facts belong in CLAUDE.md (out of this build's scope — none exists to edit in FOUNDATION_MODE); this build does not generate one, since no project facts are evidenced.
- Limitations/disagreement: none.

### Placement decision table

| Instruction type | Placement | Why |
|---|---|---|
| Reusable multi-step procedure with a defined trigger (e.g., temporal-leakage audit, multiple-testing correction) | Skill (`.claude/skills/`) | Progressive disclosure keeps idle cost near zero; matches "reusable workflow" placement test in `skill-selection.md` |
| Independent role authority and review boundary (e.g., "the integrity reviewer may block promotion") | Agent (`.claude/agents/`) | Authority and context isolation require a subagent, not a prompt fragment |
| Concise invariant tied to a known repository path | Path-scoped rule (`.claude/rules/`) | Deferred — no repository path exists to scope to (FOUNDATION_MODE) |
| Project-wide fact true in nearly every session | CLAUDE.md | Deferred — no such fact is evidenced yet |
| Deterministic mandatory enforcement (e.g., "never write to `holdout/`") | Hook/permission/test | Not generated by this builder; recorded as a future decision once a repository and its holdout paths exist |

## Capability graph

Evaluated the 12-role blueprint in `team-blueprint.md` as a hypothesis against FOUNDATION_MODE constraints.

| Domain | Needed for a safe portable foundation? | Independent authority required? | Can share a role? | Repository-specific specialist justified? |
|---|---|---|---|---|
| Methods research | Yes — every other role needs current, source-backed method guidance | No | No — must stay decoupled from implementation to avoid contaminating hard gates with post-hoc rationalization | No repository evidence to justify an addition |
| Hypothesis/discovery | Yes — prevents post-hoc storytelling | No, but must never see confirmation outcomes | No | No |
| Data integrity | Yes — point-in-time correctness is a stable principle independent of any specific vendor | No (informs, doesn't certify strategy) | No | No specific vendor/schema evidenced, so no extension role (e.g., a vendor-specific data agent) is justified |
| Feature/label methodology | Yes — leakage/timing errors are the single highest-frequency backtesting failure mode in the literature reviewed | No | No | No |
| Execution/microstructure | Yes — cost realism is a stable principle | No | No | No venue evidenced, so no venue-specific extension agent |
| Backtest engineering (implementation) | Yes | No — implementer cannot self-certify | No | No |
| Experiment design | Yes — owns discovery/confirmation separation | No | No | No |
| Statistical review | Yes | Yes — independent gate | No | No |
| Risk/robustness | Yes | Partial — can qualify, cannot rewrite results | No | No |
| Experiment integrity review | Yes — final independent gate before synthesis | Yes | No | No |
| Evidence reporting | Yes | No — cannot upgrade gate status | No | No |
| Orchestration | Yes | No — routes only | No | No |

**Conclusion:** the portable 12-role core is sufficient for FOUNDATION_MODE. No extension `bt-*` specialist is justified because no repository evidence (specific market, venue, vendor, or framework) exists to narrowly scope one. Adding a speculative extension role (e.g., "bt-crypto-funding-specialist") without repository evidence would violate the research-protocol's prohibition on unsupported constants and universalized mechanics, so none is generated.

## Build-decision coverage matrix

| Decision | Evidence class | Source(s) | Confidence | Artifacts affected | Unresolved question |
|---|---|---|---|---|---|
| Mode = FOUNDATION_MODE | repository-local | Reconnaissance (Phase 1) — empty container, no `.git`, no source tree | High | All | Becomes obsolete once a real repository/build target exists |
| 12-role core is sufficient, no extension role | internal-design, corroborated by capability graph above | `team-blueprint.md` (builder default) + this document's capability graph | Medium — a real repository could justify an extension role this analysis cannot foresee | Agents | Re-run Phase 2/4 once a target repository exists |
| Agent tool allowlists set per-role rather than inherited | official-mechanics | sub-agents.md (tools/disallowedTools semantics) | High | Agents | none |
| Skills preloaded only where every invocation needs them; else on-demand | official-mechanics | sub-agents.md (`skills:` full-content-at-startup semantics) | High | Agents, skill manifest | none |
| Purging/embargo/CPCV as the hard gate for temporal-leakage review | primary-research | López de Prado 2018 *Advances in Financial Machine Learning*, ch. 7 & 12 | High | `bt-feature-label-methodologist`, `bt-experiment-designer`, `bt-experiment-integrity-reviewer`, temporal-leakage-audit skill | Repository-specific label horizon/embargo width remains unresolved until real data frequency is known |
| Deflated Sharpe Ratio / Probability of Backtest Overfitting as the method for multiple-testing correction | primary-research | Bailey & López de Prado 2012 (Probabilistic Sharpe Ratio), 2014 (Deflated Sharpe Ratio); Bailey, Borwein, López de Prado & Zhu 2017 (Probability of Backtest Overfitting); Harvey, Liu & Zhu 2016 (multiple-testing problem in empirical finance) | High for the existence and validity of the methods; no repository-specific significance threshold is set | `bt-statistical-reviewer`, `bt-experiment-integrity-reviewer`, multiple-testing-correction skill | Exact significance/FDR threshold left as a documented, non-universalized choice the user must set per study |
| No `.claude/rules/` generated | internal-design + secondary mechanics evidence | This document's placement table + rule-selection.md gate | High | Ruleset manifest | Revisit once repository paths exist |
| Skill corpus limited to 5 generic, non-vendor-specific workflows | internal-design | `skill-selection.md` scoring, applied in `SKILLSET_RESEARCH.md` | Medium | Skills, skill manifest | A real repository's native tooling could justify merging or dropping candidates |

## Architecture stop condition

Architecture research is complete for this build: the target profile (`FOUNDATION_MODE`), extension-placement policy, capability graph (12-role core, no justified extension), and unresolved constraints (language, market, venue, vendor, data frequency, existing tooling) are explicit enough to determine what becomes an agent, a skill, a deferred rule, or a deferred hard-enforcement decision.
