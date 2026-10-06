---
title: Topic map
created: 2026-09-28
updated: 2026-09-28
type: summary
tags: [knowledge-management, comparison, workflow]
sources:
  - raw/articles/karpathy-llm-wiki-gist.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/llm-wiki-review-companion-guide.md
summary: Pages grouped by theme rather than type, for navigating the vault by question instead of by folder.
confidence: high
---

# Topic map

`index.md` is organized by page **type**, which answers "what kind of thing is this?" This map
is organized by **question**, which answers "where do I start?" Both are needed; neither
replaces the other.

`SCHEMA.md` requires this file once the vault passes 200 compiled pages, a rule inherited from
the upstream skill's scaling guidance. ^[raw/articles/hermes-agent-llm-wiki-skill.md] It is
being created early because the vault is small enough that grouping by theme is still cheap to
maintain, and because a reader arriving cold has no reason to care about the entity/concept/
comparison distinction — a distinction that serves the agent's filing logic rather than the
human's questions. ^[raw/articles/karpathy-llm-wiki-gist.md]

The reading paths below are ordered around the four-layer trust model rather than around page
type, because that is the order in which the design justifies itself. ^[raw/articles/llm-wiki-review-companion-guide.md]

## "What is this pattern and why does it exist?"

Start here. Read in order.

1. [[llm-wiki-pattern]] — the core idea: compile knowledge once, keep it current, let it compound.
2. [[llm-wiki-vs-rag]] — the contrast with retrieve-at-query-time, stated fairly to both sides.
3. [[three-layer-wiki-architecture]] — raw / wiki / schema, and the four-layer trust extension.
4. [[andrej-karpathy]] — the person and the gist that started it.
5. [[markdown-as-knowledge-substrate]] — why plain files, and what that choice costs.

## "Why shouldn't I just let the agent write?"

The trust thread. This is the vault's central argument.

1. [[anti-slopification]] — the failure mode: fluent synthesis hardening into permanent fact.
2. [[human-in-the-loop-review-gate]] — the control: propose, stop, decide, then write.
3. [[confidence-and-contested-markers]] — keeping weak claims visibly weak.
4. [[four-ways-to-own-wiki-writes]] — direct / soft guardrail / gate / deterministic core.
5. [[why-review-gate]] — the filed argument, including the objections worth taking seriously.

## "How do I know any of it is true?"

The provenance and verification thread.

1. [[immutable-raw-layer]] — captures that cannot be edited, each pinned by SHA-256.
2. [[source-traceability]] — following a claim back to bytes, and recording what you lack.
3. [[provenance-markers]] — paragraph-level attribution, and its limits.
4. [[verification-layers]] — the enforced-by-code versus requested-of-model table.
5. [[review-companion-vs-agentic-librarian]] — when a convention stops being enough.

## "What do I run this on?"

1. [[hermes-agent]] — the reference runtime, and where the gate attaches.
2. [[llm-wiki-skill]] — the built-in procedure, with its frozen artifact hash.
3. [[llm-wiki-review-skill]] — the companion skill, with its frozen artifact hash.
4. [[nous-research]] — the upstream maintainer, and why upstream drift matters.
5. [[obsidian]] — the human's reader: vault settings, Dataview, headless sync, reviewing proposals.
6. [[open-source-agent-skills]] — the wider ecosystem, and what its convergence implies.

## "How does the wiki stay healthy as it grows?"

1. [[skipping-orientation]] — what breaks when a session starts without reading schema, index, and log.
2. [[agentic-memory-vs-compiled-wiki]] — what belongs in memory, in the wiki, and in the schema.
3. [[agent-knowledge-substrates]] — flat files versus vectors versus graphs versus tables.
4. ⚔️ **Proposed, awaiting review** — `concepts/index-first-navigation.md`: does index-first
   navigation scale, or does retrieval arrive at ~100 pages? Two sources disagree, so the page
   is not written yet. The competing claims, both readings, and the three review choices are in
   `review/2026-09-28-index-first-navigation-proposal.md`. This entry becomes a real link the
   moment a human approves it.
5. `SCHEMA.md` — thresholds, scaling rules, rotation, and the tag taxonomy.

## Reading paths by intent

| You want to… | Read |
| --- | --- |
| Set this up on your own machine | `../README.md` then `../docs/SETUP.md` |
| Understand the review gate in five minutes | [[human-in-the-loop-review-gate]] then `review/README.md` |
| Ingest a source correctly | [[immutable-raw-layer]] then [[skipping-orientation]] |
| Audit the vault | [[verification-layers]] then `python3 tools/wiki_tool.py lint` |
| See the gate actually work | `review/2026-09-28-index-first-navigation-proposal.md` — a live, undecided contradiction |
| Judge whether you need the heavier tooling | [[review-companion-vs-agentic-librarian]] |

## Related

[[llm-wiki-pattern]] · [[three-layer-wiki-architecture]] · [[verification-layers]] ·
[[human-in-the-loop-review-gate]] · [[source-traceability]]
