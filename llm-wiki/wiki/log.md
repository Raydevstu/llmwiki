# Wiki Log

> Chronological record of all wiki actions. Append-only.
> Format: `## [YYYY-MM-DD] action | subject`
> Actions: archive, create, delete, ingest, lint, query, review, update
> When this file exceeds 500 entries, rotate: rename to log-YYYY.md, start fresh.
> Entries are machine-appended by `tools/wiki_tool.py` and by the agent. Never rewrite history.

## [2026-09-28] create | Wiki initialized
- Domain: AI / LLM research, agents, and knowledge tooling
- Structure created: SCHEMA.md, index.md, log.md, raw/{articles,papers,transcripts,assets}, entities, concepts, comparisons, queries, review, _meta
- Schema written from the Hermes built-in `llm-wiki` template, customized to the domain
- Verification tooling installed at tools/wiki_tool.py (orient, hash, verify, capture, reindex, lint, pending, propose, apply)
- Review companion installed at skills/llm-wiki-review/

## [2026-09-28] ingest | Karpathy, "LLM Wiki" gist
- Captured raw/articles/karpathy-llm-wiki-gist.md (sha256 dc3efe98ae62…, 11923 bytes)
- Foundational source for the whole vault: the pattern, the three layers, the three operations

## [2026-09-28] ingest | Hermes Agent built-in llm-wiki skill v2.1.0
- Captured raw/articles/hermes-agent-llm-wiki-skill.md (sha256 0229e37c1783…, 19895 bytes)
- Recomputed digest MATCHES the value frozen in the review companion's qualification report: the tested artifact and the installed artifact are the same bytes

## [2026-09-28] ingest | Hermes Agent README
- Captured raw/articles/hermes-agent-readme.md (sha256 c8c3009b1cf6…, 16818 bytes)
- Source for entities/hermes-agent.md and entities/nous-research.md

## [2026-09-28] ingest | awesome-llm-wiki community catalog
- Captured raw/articles/awesome-llm-wiki-readme.md (sha256 d685e5e13743…, 184625 bytes)
- Ecosystem evidence; also the only captured source describing the Wanderloots video's contents

## [2026-09-28] ingest | Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (arXiv:2005.11401)
- Captured raw/papers/lewis-retrieval-augmented-generation-2020.md (sha256 d8b18fb21b57…, 45832 bytes)
- capture_note recorded: HTML abstract page, not the PDF
- Included so comparisons/llm-wiki-vs-rag.md engages the real technique rather than a strawman

## [2026-09-28] ingest | Wanderloots, "How To Build LLM Wiki In Obsidian?" (video)
- Captured raw/transcripts/wanderloots-llm-wiki-obsidian-video.md (sha256 ca0a6fa2aac0…, 1573 bytes)
- capture_note recorded: oEmbed metadata only, NO TRANSCRIPT; body is generated, not a copy of the source
- Claim limit recorded in entities/wanderloots.md: nothing in this wiki may be sourced to the video's spoken content, and that page carries confidence: medium because of the gap

## [2026-09-28] ingest | llm-wiki-review skill (user-supplied SKILL.md)
- Captured raw/articles/llm-wiki-review-skill.md (sha256 d9c037639f7e…, 5803 bytes)
- Recomputed digest MATCHES the value frozen in the qualification report
- Stored verbatim including its own frontmatter; see concepts/immutable-raw-layer.md on nested frontmatter and positional stripping

## [2026-09-28] ingest | LLM Wiki Review Companion guide (user-supplied START HERE.md)
- Captured raw/articles/llm-wiki-review-companion-guide.md (sha256 9617f95d3eba…, 5411 bytes)
- Source for the four-layer model, the workflow-selection table, and the anti-slopification framing

## [2026-09-28] ingest | Review Companion qualification report (user-supplied QUALIFICATION.md)
- Captured raw/articles/llm-wiki-review-qualification-report.md (sha256 8345e19da901…, 2963 bytes)
- 14-case release matrix, 110 model API calls, gpt-5.6-terra / medium reasoning / OpenAI Codex provider
- Its explicit scope exclusions are the basis for concepts/verification-layers.md

## [2026-09-28] create | 8 entity pages
- entities/andrej-karpathy.md, nous-research.md, hermes-agent.md, obsidian.md, wanderloots.md, llm-wiki-skill.md, llm-wiki-review-skill.md, open-source-agent-skills.md

## [2026-09-28] create | 12 concept pages
- concepts/llm-wiki-pattern.md, three-layer-wiki-architecture.md, immutable-raw-layer.md, human-in-the-loop-review-gate.md, anti-slopification.md, llm-wiki-vs-rag.md, provenance-markers.md, source-traceability.md, confidence-and-contested-markers.md, agentic-memory-vs-compiled-wiki.md, verification-layers.md, markdown-as-knowledge-substrate.md

## [2026-09-28] create | 3 comparison pages
- comparisons/review-companion-vs-agentic-librarian.md, four-ways-to-own-wiki-writes.md, agent-knowledge-substrates.md

## [2026-09-28] create | 2 filed query pages
- queries/why-review-gate.md, queries/skipping-orientation.md
- Both filed because the answers synthesize 3+ sources and would be painful to re-derive

## [2026-09-28] create | _meta/topic-map.md and review/README.md
- Topic map created ahead of the 200-page threshold in SCHEMA.md: cheap to maintain now, and a cold reader has no reason to care about type-based filing
- review/README.md documents how to answer a proposal from conversation, Obsidian, or the CLI

## [2026-09-28] review | Proposal 2026-09-28-llm-wiki-vs-rag-proposal.md approved
- target concepts/llm-wiki-vs-rag.md written from revision 1
- Applied content verified byte-identical to the reviewed proposal block (digest cross-checked in both directions)
- Post-write maintenance: index rebuilt, log appended

## [2026-09-28] review | Proposal 2026-09-28-index-first-navigation-proposal.md created
- target concepts/index-first-navigation.md
- operation conflict-resolution; revision 1; status needs-review
- Two sources disagree on whether index-first navigation scales past ~100 pages; the default proposal preserves both claims and marks the page contested
- AWAITING A HUMAN DECISION. Nothing compiled was written. Silence and elapsed time are not approval

## [2026-09-28] update | index.md rebuilt from page frontmatter
- tools/wiki_tool.py reindex: 26 compiled pages, 2 proposals, 9 raw captures

## [2026-09-28] lint | 0 errors, 0 warnings
- All 9 raw captures hash-verified against their stored sha256
- Checked: required frontmatter, page types, date formats, tags against the SCHEMA.md taxonomy, wikilink resolution, >=2 outbound links per page, provenance-marker resolution, raw source presence, path containment, index completeness, log entry format, proposal state consistency, revision binding
- Two proposals in review/: one applied, one conflict-resolution awaiting a human decision

## [2026-09-28] update | index.md rebuilt by wiki_tool.py reindex
