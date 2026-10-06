---
title: Open-source agent skills for LLM wikis
created: 2026-09-28
updated: 2026-09-28
type: entity
tags: [open-source, agent, tooling, knowledge-management]
sources:
  - raw/articles/awesome-llm-wiki-readme.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
summary: The installable-skill ecosystem around the LLM Wiki pattern, catalogued by awesome-llm-wiki; shows review gates and hash provenance are convergent designs.
confidence: medium
---

# Open-source agent skills for LLM wikis

## Overview

The [[llm-wiki-pattern]] has been reimplemented many times as installable agent skills. The
`awesome-llm-wiki` list catalogs them under "Agent Skills and System Rules", described as
"procedural instructions, system schemas, and behavioral configuration definitions
engineered to teach autonomous terminal models how to natively compile, link, and maintain
flat-file knowledge bases." ^[raw/articles/awesome-llm-wiki-readme.md]

This page exists because the ecosystem is evidence about the pattern: when independent
implementations converge on the same safeguards, those safeguards are probably load-bearing.

## Selected implementations

| Project | Runtime | Notable design |
| --- | --- | --- |
| DeepRefine-Skill (HKUST-KnowComp) | Claude Code, Codex, Copilot CLI, Cursor, Gemini CLI, OpenCode | Evolves and refines LLM-Wiki and Graphify knowledge graphs **at test time** via query reflection and automated graph maintenance |
| Engram (NoobAIDeveloper) | Claude Code | Captures digital touchpoints and social threads, compiling them into an interlinked Obsidian vault |
| hstack (kamens) | Claude Code | Compiles raw medical records and research into a personal disease wiki |
| karpathy-llm-wiki (Astro-Han) | `agentskills.io`-compatible clients | Packages the pattern for any conforming client — the same standard [[hermes-agent]] supports |
| LLM Wiki (praneybehl) | Claude Code, Codex, Cursor, Gemini, Pi | Local PEP-723 runtime with on-device semantic search (FastEmbed/sqlite-vec), BM25 fallback, RRF hybrid fusion, incremental changed-section indexing |
| LLM Wiki (6eanut) | Claude Code | SessionStart hooks, two-phase ingestion with **contradiction detection**, seven slash commands including `/wiki-review` |
| LLM Wiki (Oshayr) | Claude Code | Research-on-miss query routing, multi-agent maintenance (backlinks, claim verification, dedup, **9-tier staleness decay**), Cytoscape graph UI, FSRS spaced repetition |
| LLM Wiki (TrueHOOHA) | Claude Code | Explicitly aimed at mitigating **agent behavioral drift** via rigid workflow skills; triage-first ingest, automated cross-page contradiction reports, `wiki_fix` cleanup loop, **SHA-256 source provenance tracking** |

^[raw/articles/awesome-llm-wiki-readme.md]

## What the convergence tells us

Three features recur across independent builds, and all three are things this vault also
does:

1. **A review or contradiction step is treated as necessary, not optional.** 6eanut ships
   `/wiki-review` and two-phase ingestion with contradiction detection; Oshayr runs claim
   verification; TrueHOOHA emits automated cross-page contradiction reports. That is the
   same problem [[human-in-the-loop-review-gate]] addresses, arrived at from different
   directions.
2. **SHA-256 provenance is becoming standard.** TrueHOOHA tracks source provenance with
   SHA-256, exactly as [[immutable-raw-layer]] specifies here and as
   [[llm-wiki-skill]] requires upstream.
3. **Staleness needs an explicit mechanism.** Oshayr's 9-tier staleness decay and
   DeepRefine's test-time graph maintenance both assume knowledge rots and must be actively
   decayed or refreshed — the same instinct behind `confidence` decay in
   [[confidence-and-contested-markers]] and the staleness check in `wiki_tool.py lint`.

Two implementations add retrieval this vault deliberately omits: praneybehl runs hybrid
semantic + BM25 search, and Oshayr adds a graph UI. [[andrej-karpathy]]'s position is that
index-first navigation suffices to "~hundreds of pages"; past that, the trade-off in
[[llm-wiki-vs-rag]] changes. This vault has 30-ish pages, so it does not need either yet.

## Caveats

`confidence: medium`. This page synthesizes **one** source's *descriptions* of other
projects. Nothing here was verified by installing or reading those codebases; the
descriptions are the cataloguer's, and could be stale or generous. Claims about a specific
project should be re-sourced from that project's own repository before being relied on.
That is precisely the discipline [[source-traceability]] asks for.

## Related

[[llm-wiki-pattern]] · [[llm-wiki-skill]] · [[andrej-karpathy]] ·
[[immutable-raw-layer]] · [[human-in-the-loop-review-gate]]
