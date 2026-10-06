---
title: Three-layer wiki architecture
created: 2026-09-28
updated: 2026-09-28
type: concept
tags: [architecture, knowledge-management, markdown]
sources:
  - raw/articles/karpathy-llm-wiki-gist.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/llm-wiki-review-companion-guide.md
summary: Raw sources (immutable) / the wiki (agent-owned) / the schema (the contract) — plus the optional trust, verification, and power layers added on top.
confidence: high
---

# Three-layer wiki architecture

## Definition

The structural core of the [[llm-wiki-pattern]]. Three layers, each with a different owner
and a different mutability rule:

| Layer | Contents | Owner | Mutable? |
| --- | --- | --- | --- |
| **1 — Raw sources** | Articles, papers, images, data files | Human (curates what enters) | **Never.** The model reads but never modifies |
| **2 — The wiki** | Summaries, entity pages, concept pages, comparisons, overview, synthesis | The model, entirely | Yes — created, updated, cross-referenced, kept consistent |
| **3 — The schema** | Structure, conventions, workflows for ingest/query/maintenance | Human and model, co-evolved | Deliberately, rarely |

^[raw/articles/karpathy-llm-wiki-gist.md]

Layer 3 is "the key configuration file — it's what makes the LLM a disciplined wiki
maintainer rather than a generic chatbot," and it is co-evolved over time as you learn what
works for your domain. ^[raw/articles/karpathy-llm-wiki-gist.md] In this vault it is
`SCHEMA.md`; upstream, [[llm-wiki-skill]] supplies a template covering domain, conventions,
frontmatter, tag taxonomy, page thresholds, page-type structure, and an update policy.
^[raw/articles/hermes-agent-llm-wiki-skill.md]

Karpathy notes the schema can live as `CLAUDE.md` for Claude Code or `AGENTS.md` for Codex —
the file name is runtime-specific, the role is not. See
[[markdown-as-knowledge-substrate]].

## Why the split matters

The layers have different failure modes and therefore need different protections:

- **Raw is the ground truth.** If it can be edited, nothing downstream is auditable. Hence
  hashing — see [[immutable-raw-layer]].
- **The wiki is a derived artifact.** It can always be rebuilt from raw plus schema, which
  is what makes aggressive editing safe and what makes an accidental bad write recoverable.
- **The schema is the contract.** Changing it silently changes the meaning of every page.
  Hence "add the tag to the taxonomy first, then use it", and hence lint enforcing it.

## The four-layer extension

The Review Companion guide reframes the same system as **four layers**, where the original
three sit inside layer 1:

```
Sources → 1 Intelligence (Hermes LLM Wiki) ──direct path──→ Curated Wiki
                   ↓
          2 Trust (Review Companion) → Human in the loop → Curated Wiki
                   ↓
          3 Verification (Agentic Librarian Core) → hashes · schemas · receipts · Git
                   ↓
          4 Power (optional expansions: Rail, memory projection, automation,
                   local models, Molecular Zettelkasten)
```

Crucially: **"Each layer is a valid stopping point."** The companion does not replace the
built-in skill's intelligence, and the core does not require the optional power expansions.
^[raw/articles/llm-wiki-review-companion-guide.md]

That is the design principle this vault follows. It runs layers 1–3:

| Layer | Implementation here |
| --- | --- |
| 1 Intelligence | [[llm-wiki-skill]] (upstream, unmodified) |
| 2 Trust | [[llm-wiki-review-skill]] + `wiki/review/` |
| 3 Verification | `tools/wiki_tool.py` — hashes, schema, path escape, revision binding, index, log |
| 4 Power | **Not installed.** No Rail, memory projection, automation, local models, or Zettelkasten |

See [[review-companion-vs-agentic-librarian]] for when layer 3 needs to become a full
deterministic core, and [[verification-layers]] for exactly what is and is not enforced.

## Choosing the lightest workflow that fits

The guide's decision table, condensed:

- Fast personal synthesis, direct writes acceptable → built-in `llm-wiki` alone.
- Want to approve material changes before they become trusted → add `llm-wiki-review`;
  markdown proposals wait for a human.
- Need automation, multiple agents, large queues, mechanically enforced state → Agentic
  Librarian Core: deterministic tools enforce paths, schemas, hashes, revisions,
  transactions, receipts, and recovery.
- Stable core plus one specific additional need → an optional Power expansion, added
  separately.

^[raw/articles/llm-wiki-review-companion-guide.md]

## Related

[[llm-wiki-pattern]] · [[immutable-raw-layer]] · [[verification-layers]] ·
[[human-in-the-loop-review-gate]] · [[llm-wiki-skill]] · [[topic-map]]
