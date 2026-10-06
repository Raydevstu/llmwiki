---
title: llm-wiki (Hermes built-in skill)
created: 2026-09-28
updated: 2026-09-28
type: entity
tags: [agent, tooling, open-source, knowledge-management, markdown]
sources:
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/karpathy-llm-wiki-gist.md
  - raw/articles/llm-wiki-review-qualification-report.md
summary: Version 2.1.0 of the Hermes Agent research skill that operationalizes Karpathy's LLM Wiki pattern; the frozen artifact this vault was compiled against.
confidence: high
---

# llm-wiki (Hermes built-in skill)

## Overview

The built-in [[hermes-agent]] skill that turns [[andrej-karpathy]]'s idea file into an
executable procedure. Frontmatter of the frozen capture: `name: llm-wiki`,
`version: 2.1.0`, `author: Hermes Agent`, `license: MIT`, category `research`, related
skills `obsidian` and `arxiv`. ^[raw/articles/hermes-agent-llm-wiki-skill.md]

Its own summary of the value proposition: unlike traditional RAG, which rediscovers
knowledge from scratch per query, the wiki compiles knowledge once and keeps it current —
cross-references are already there, contradictions already flagged, synthesis already
reflects everything ingested. See [[llm-wiki-vs-rag]].

**Division of labor:** the human curates sources and directs analysis; the agent
summarizes, cross-references, files, and maintains consistency.

## Frozen artifact

| Property | Value |
| --- | --- |
| Raw capture | `raw/articles/hermes-agent-llm-wiki-skill.md` |
| Body SHA-256 | `0229e37c1783fcac5b77cfb3242703666cf4aa472d2ae85b6bd5279756b515b6` |
| Size | 19,895 bytes |
| Captured | 2026-09-28 from `main` |

This digest **matches** the value frozen in
`raw/articles/llm-wiki-review-qualification-report.md` as "Hermes built-in `llm-wiki`
SHA-256". Independently recomputing it from a fresh download of upstream `main` confirms
that the qualification report was run against the same artifact version now in use — the
frozen hashes have not drifted. ^[raw/articles/llm-wiki-review-qualification-report.md]

That is a small but real demonstration of what [[immutable-raw-layer]] buys you: a
verifiable claim about *which version* of a procedure a test result applies to.

## Activation triggers

The skill activates when the user asks to create/build/start a wiki, to ingest or process a
source, asks a question while a wiki exists at the configured path, asks to lint or audit,
or references their wiki/KB/notes in a research context.
^[raw/articles/hermes-agent-llm-wiki-skill.md]

## Procedure

**Orientation (every session, before anything else).** Read `SCHEMA.md` → read `index.md`
→ scan the last 20–30 `log.md` entries. For 100+ page wikis, also search for the topic at
hand. Skipping this causes duplicate pages, missed cross-references, schema violations,
and repeated work. See [[skipping-orientation]].

**Ingest.** Capture raw with `source_url` / `ingested` / `sha256` → discuss takeaways
(skipped in automated contexts) → check what already exists → write or update pages
respecting thresholds, tags, provenance, and confidence → update `index.md` and `log.md` →
report every file touched. One source touching 5–15 pages is normal and desired.

**Query.** Read index → search if large → read relevant pages → synthesize with citations
→ file substantial answers into `queries/` or `comparisons/` → log it.

**Lint.** Twelve checks: orphans, broken wikilinks, index completeness, frontmatter
validation, staleness, contradictions, quality signals, raw source drift, page size, tag
audit, log rotation, then a severity-grouped report and a log entry.
`tools/wiki_tool.py lint` implements the mechanical subset — see [[verification-layers]].

## Hard rules it states

- Never modify `raw/`.
- Always orient first; always update `index.md` and `log.md`.
- No pages for passing mentions; no pages without ≥2 cross-references.
- Frontmatter required; tags only from the taxonomy.
- Keep pages scannable — readable in 30 seconds; split past 200 lines.
- **Ask before mass-updating**: if an ingest would touch 10+ existing pages, confirm scope.
- Handle contradictions explicitly; never silently overwrite.

^[raw/articles/hermes-agent-llm-wiki-skill.md]

Note that the last three are exactly the seams [[llm-wiki-review-skill]] formalizes into a
gate. The built-in skill's "ask before mass-updating" is a soft prompt; the review skill
makes stopping the default for *every* compiled write.

## Related tooling

The skill itself points to `llm-wiki-compiler` (Node.js CLI, same Karpathy inspiration,
Obsidian-compatible) with an explicit trade-off: the compiler owns page generation,
replacing agent judgment on page creation, and is tuned for small corpora. Use the skill
for agent-in-the-loop curation; use the compiler for batch compilation of a source
directory. ^[raw/articles/hermes-agent-llm-wiki-skill.md] See
[[open-source-agent-skills]] for the wider field.

## Related

[[hermes-agent]] · [[llm-wiki-review-skill]] · [[three-layer-wiki-architecture]] ·
[[llm-wiki-pattern]] · [[nous-research]]
