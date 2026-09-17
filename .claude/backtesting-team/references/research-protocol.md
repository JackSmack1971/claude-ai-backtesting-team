# Research Protocol

Canonical source for the claim-classification taxonomy and source hierarchy
`bt-methods-researcher` applies, and that `BUILD_RESEARCH.md` /
`ARCHITECTURE_RESEARCH.md` use throughout.

## Claim classes

- **repository-local** — a fact about this specific repository (language,
  framework, existing data, existing tests). Verified by direct inspection,
  never assumed.
- **mechanics-sensitive** — current behavior of a tool, library, API, or
  platform (e.g., Claude Code subagent tool-resolution semantics). Must be
  verified against current official documentation, not training-data memory,
  because these change between releases.
- **method-sensitive** — a quantitative-research or statistical method whose
  correctness the team is relying on (e.g., purging/embargo, Deflated Sharpe
  Ratio). Prefer primary/original sources or peer-reviewed literature.
- **stable-principle** — a durable, largely uncontested principle (e.g.,
  "don't use future information," "controlling FDR is distinct from
  controlling FWER"). Lower re-verification urgency than mechanics-sensitive
  claims, but still cited.
- **internal-design** — a convention this team's builder chose (e.g., the
  evidence-report-formatter's claim/evidence/status/limitation table). Must
  be labeled as internal design, never presented as external research
  consensus.

## Source hierarchy (highest to lowest preference)

1. Primary/original source (the paper, the official spec, the tool's own
   current documentation) — actually inspected, not merely cited by title.
2. Peer-reviewed literature.
3. Official documentation for the specific mechanics claim in question.
4. Corroborating secondary sources (summaries, whitepapers referencing the
   primary work) — usable to locate or corroborate a primary source, but a
   claim resting only on a secondary summary must be labeled as such (see
   "Source actually inspected" below), never labeled `primary-research` on
   the strength of the underlying work's existence alone.

## Required provenance fields

Every consequential external claim recorded in a research artifact must
state, separately:

- **Source cited** — the work being credited (e.g., "Bailey & López de Prado 2014").
- **Source actually inspected** — the specific document/page Claude fetched
  and read (may be the primary source, or may be a secondary summary/
  corroborating page — these are not the same thing and must not be
  conflated).
- **Source class** — reflects what was *actually inspected*, not what exists:
  `primary-research` only if the primary work itself was inspected;
  otherwise `secondary` (a summary/corroboration of a primary work) or
  `official-doc` (a platform's own current documentation).
- **Claim class** — one of the five classes above.
- **Exact supported claim** — the narrow claim the inspected source actually
  supports, not a broader claim the primary work is reputed to make.
- **Scope/limitations** — where the claim does not generalize (e.g.,
  venue-specific, frequency-specific, market-specific).
- **Downstream design consequence** — which agent/skill/gate this claim
  justifies, and how.

## Operating rules

- Never let one paper's finding get stretched to an unrelated decision.
- Never present an internal design choice as literature consensus.
- When only secondary sources are locatable, label the recommendation
  heuristic, not a hard gate.
- Record genuinely contested claims with both sides rather than picking a
  winner without a second source.
