---
title: Agent knowledge substrates compared
created: 2026-09-28
updated: 2026-09-28
type: comparison
tags: [comparison, architecture, knowledge-management, memory, tooling]
sources:
  - raw/articles/karpathy-llm-wiki-gist.md
  - raw/articles/awesome-llm-wiki-readme.md
  - raw/papers/lewis-retrieval-augmented-generation-2020.md
summary: Flat markdown wiki, vector index, property graph, and relational store as agent knowledge substrates — what each makes easy and what each makes impossible.
confidence: medium
---

# Agent knowledge substrates compared

## What is being compared, and why

An agent that accumulates knowledge has to store it somewhere, and the substrate determines
which operations are cheap. The [[llm-wiki-pattern]] bets everything on **flat markdown
files**; the alternatives it is usually measured against are vector indexes, property graphs,
and relational stores. The bet is worth examining because it is not obvious — a directory of
text files has no query engine at all.

`confidence: medium` on this page. Only the markdown and vector sides are well-sourced
here; the graph and relational columns draw on one catalog entry and on general knowledge
that is **not** captured in `raw/`. Treat those two columns as orientation, not as evidence.
See [[source-traceability]].

## Dimensions

| Dimension | Flat markdown wiki | Vector index (RAG) | Property graph | Relational store |
| --- | --- | --- | --- | --- |
| Read by a human, unaided | ✅ directly | ❌ embeddings are opaque | ⚠️ via a viewer | ⚠️ via SQL |
| Diffable in Git | ✅ line-level | ❌ | ⚠️ exports differ | ⚠️ |
| Query without bespoke code | ⚠️ grep + index file | ✅ similarity search | ✅ traversal queries | ✅ SQL |
| Multi-hop reasoning | ✅ precompiled links | ❌ reassembled per query | ✅ strongest here | ⚠️ joins, hand-written |
| Contradiction visibility | ✅ explicit, marked `contested` | ❌ both chunks retrieved silently | ✅ conflicting edges | ⚠️ constraints only |
| Write cost | High (synthesize + cross-link) | Low (embed + insert) | Medium (extract entities/relations) | Low–medium |
| Read cost | Low | Medium–high (retrieve + long context) | Low–medium | Low |
| Update on source change | Manual, must find affected pages | Re-embed the doc | Re-extract the subgraph | `UPDATE` statement |
| Infrastructure | A directory | Embedding model + vector store | Graph DB | DBMS |
| Portable / no lock-in | ✅ plain text | ⚠️ index is provider-shaped | ❌ | ⚠️ |
| Provenance granularity | ✅ paragraph-level markers | ⚠️ chunk-level | ⚠️ edge-level if modeled | ⚠️ column-level if modeled |
| Proven scale | "~hundreds of pages" | Millions of docs | Large graphs | Very large tables |

Sources for the markdown and vector columns: ^[raw/articles/karpathy-llm-wiki-gist.md]
^[raw/papers/lewis-retrieval-augmented-generation-2020.md] ^[raw/articles/hermes-agent-llm-wiki-skill.md]

## The case for flat markdown

Its advantages are not performance advantages — they are **social and audit** advantages.
A human can read a page, review a proposal as exact bytes, diff a claim's history in Git,
and grep a provenance marker. Every one of those is a prerequisite for
[[human-in-the-loop-review-gate]], which is why the gate is natural in markdown and awkward
in a vector store: there is no legible artifact to approve.

It is also nearly free. "No database, no special tooling required" ^[raw/articles/hermes-agent-llm-wiki-skill.md]
and index-first navigation "avoids the need for embedding-based RAG infrastructure"
^[raw/articles/karpathy-llm-wiki-gist.md] mean the whole system is a folder plus an editor.

The cost is the query engine. Everything a database gives you for free — filtering, joining,
ranking — has to be reimplemented as conventions: an index file, a tag taxonomy, a lint
script, a naming rule. `tools/wiki_tool.py` is that reimplementation for one vault, and it
is several hundred lines to get a fraction of what SQL does natively.

## The case for vectors, honestly

RAG's original motivation includes **updatable non-parametric memory**: swap the index and
the model's knowledge changes, with no retraining. ^[raw/papers/lewis-retrieval-augmented-generation-2020.md]
For a corpus of 50,000 documents consulted sparsely, compiling every one into a page is
absurd; retrieving chunks is the right answer.

The wiki's critique is narrower than "RAG is bad" — it is that RAG retains nothing between
queries, so synthesis is paid for every time and never accumulates.
^[raw/articles/karpathy-llm-wiki-gist.md] That critique bites hardest for **reused**
knowledge and barely at all for one-shot lookup. See [[llm-wiki-vs-rag]].

## Hybrids are the actual answer in practice

The ecosystem does not choose one. Catalogued implementations add on-device semantic search
with BM25 fallback and RRF hybrid fusion to a compiled markdown vault; another maps the wiki
pattern onto Neo4j with entity-resolution benchmarks; a v3 extension makes markdown pages
"deterministic views of underlying truth graphs" — i.e. the graph is the store and the wiki
is the human-readable rendering. ^[raw/articles/awesome-llm-wiki-readme.md]

That last design is the most interesting, and it inverts this vault's assumption: instead of
markdown being the source of truth with links as a poor man's graph, the graph is the truth
and markdown is a projection. It solves the consistency problem (the store enforces it) at
the cost of legibility (a human now reviews a projection). Whether that trade is worth it
depends entirely on whether a human reviews at all — see
[[review-companion-vs-agentic-librarian]].

## Verdict for this vault

Flat markdown, no retrieval layer. At ~30 compiled pages and 9 captures, the index is
sufficient, the audit properties are the ones that matter most, and the infrastructure cost
is zero. The revisit triggers are measurable: index sections past 50 entries, repeated
queries missing pages that exist, or a corpus too large to compile.

Do **not** add a graph or vector layer before one of those fires. The tooling cost is real
and the benefit at this scale is nil.

## Related

[[llm-wiki-vs-rag]] · [[markdown-as-knowledge-substrate]] · [[llm-wiki-pattern]] ·
[[agentic-memory-vs-compiled-wiki]] · [[open-source-agent-skills]]
