---
title: Wanderloots (Callum)
created: 2026-09-28
updated: 2026-09-28
type: entity
tags: [person, obsidian, knowledge-management]
sources:
  - raw/transcripts/wanderloots-llm-wiki-obsidian-video.md
  - raw/articles/awesome-llm-wiki-readme.md
summary: Creator of the video tutorial this vault was built from; an IP lawyer and patent agent making Obsidian, web3, and AI tutorials.
confidence: medium
---

# Wanderloots (Callum)

## Overview

YouTube educator who published *"How To Build LLM Wiki In Obsidian? 🧠 A Memory Layer For
Any Agentic AI"* — the video that prompted this vault. Self-described as "Callum, aka
wanderloots", a photographer, artist, and educator working across astro and wildlife
photography, mindfulness, emerging technology, and intellectual property.
^[raw/transcripts/wanderloots-llm-wiki-obsidian-video.md]

His professional framing is unusual for this niche and worth noting: he is an **intellectual
property lawyer and patent agent**, interested in "the exploration of knowledge and the use
of tools (including AI) to help augment our knowledge systems," with an explicit disclaimer
that none of his content is legal, patent, or financial advice.
^[raw/transcripts/wanderloots-llm-wiki-obsidian-video.md]

## What the video covers

The community ecosystem list characterizes it as "the definitive video tutorial mapping out
the core 3-tier local memory architecture, showcasing how to build a file-based ingestion
pipeline, implement a Git-backed maintenance loop, and deploy an agentic vault firewall
wrapper." ^[raw/articles/awesome-llm-wiki-readme.md]

Mapped onto this vault:

| Video element (as described) | Where it lives here |
| --- | --- |
| 3-tier local memory architecture | [[three-layer-wiki-architecture]] |
| File-based ingestion pipeline | [[immutable-raw-layer]] + `tools/wiki_tool.py capture` |
| Git-backed maintenance loop | [[verification-layers]] · `docs/SETUP.md` §6 |
| Agentic vault firewall wrapper | [[human-in-the-loop-review-gate]] · [[llm-wiki-review-skill]] |

## Capture limitation — read this before citing

The raw capture at `raw/transcripts/wanderloots-llm-wiki-obsidian-video.md` is
**metadata only** (title, channel, URL, thumbnail, via the YouTube oEmbed endpoint). No
transcript was captured. Therefore:

- No claim in this wiki may be attributed to anything *said* in the video.
- The mapping table above is sourced to the third-party description in
  `raw/articles/awesome-llm-wiki-readme.md`, not to the video itself.
- `confidence: medium` on this page reflects that gap, per [[confidence-and-contested-markers]].

If you watch the video and want its actual content compiled, capture a transcript into
`raw/transcripts/` and re-ingest — that is the only way these claims get a real source.

## Related work

He also publishes on Obsidian and digital gardening (a 51-video playlist), NotebookLM,
Adobe Firefly, and Manifold/web3, plus a newsletter (*Recalibrating*). A related video in
his catalog, *"Subagents vs Agent Teams? Hermes Bots, Goal Loops & Kanban Graphs"*, covers
[[hermes-agent]] orchestration. ^[raw/transcripts/wanderloots-llm-wiki-obsidian-video.md]

## Related

[[obsidian]] · [[andrej-karpathy]] · [[llm-wiki-pattern]] · [[source-traceability]]
