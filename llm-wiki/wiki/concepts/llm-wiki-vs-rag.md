---
title: LLM Wiki vs RAG
created: 2026-09-28
updated: 2026-09-28
type: concept
tags: [comparison, architecture, knowledge-management, agent]
sources:
  - raw/articles/karpathy-llm-wiki-gist.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/papers/lewis-retrieval-augmented-generation-2020.md
  - raw/articles/awesome-llm-wiki-readme.md
summary: Compiled-once interlinked markdown versus retrieve-at-query-time chunks — different cost curves, different failure modes, and not actually mutually exclusive.
confidence: high
---

# LLM Wiki vs RAG

## The contrast as the source states it

> "Most people's experience with LLMs and documents looks like RAG: you upload a collection
> of files, the LLM retrieves relevant chunks at query time, and generates an answer. This
> works, but the LLM is rediscovering knowledge from scratch on every question. There's no
> accumulation." ^[raw/articles/karpathy-llm-wiki-gist.md]

> "Unlike traditional RAG (which rediscovers knowledge from scratch per query), the wiki
> compiles knowledge once and keeps it current. Cross-references are already there.
> Contradictions have already been flagged. Synthesis reflects everything ingested."
> ^[raw/articles/hermes-agent-llm-wiki-skill.md]

The axis is **when synthesis happens**: RAG defers it to query time, every query; the wiki
does it once at ingest time and maintains it.

## What RAG actually is

For fairness, the term deserves its own definition rather than the strawman version. In the
original formulation, Retrieval-Augmented Generation pairs a parametric memory (a
sequence-to-sequence model) with a non-parametric memory (a dense vector index of documents,
in the paper's case Wikipedia), retrieving relevant passages at generation time and
marginalizing over retrieved documents to produce an output. The stated motivations are
knowledge-intensiveness, and the ability to update the non-parametric memory instead of
retraining. ^[raw/papers/lewis-retrieval-augmented-generation-2020.md]

That last property — swap the index, change the knowledge, no retraining — is a genuine
advantage the wiki does not have. RAG is not a mistake; it is a different point in the
design space.

## Dimensions

| Dimension | RAG | LLM Wiki |
| --- | --- | --- |
| When synthesis happens | Every query, from scratch | Once at ingest, then maintained |
| Cost profile | Pay per query (retrieval + long context) | Pay per ingest (write + cross-reference); queries are cheap reads |
| Cross-document reasoning | Reassembled each time from chunks | Already compiled into pages with links |
| Contradiction handling | Both chunks may be retrieved; conflict is invisible unless the model notices | Explicitly flagged at ingest, marked `contested`, routed to review |
| Human auditability | Low — retrieval is opaque, chunks have no persistent identity | High — a page is a file you can read, diff, and blame |
| Browsing without a query | Not meaningful | First-class: index, graph view, backlinks |
| Scaling past a few hundred pages | Comfortable — it is what vector indexes are for | Unproven; index-first navigation is claimed sufficient only to "~hundreds of pages" |
| Freshness | Update the index | Re-ingest and update affected pages, which is manual work |
| Failure mode | Missing the right chunk; incoherent stitching | Compounding a wrong synthesis — see [[anti-slopification]] |
| Infrastructure | Embeddings, vector store, chunking policy | A directory and an editor |

Sources: ^[raw/articles/karpathy-llm-wiki-gist.md] ^[raw/articles/hermes-agent-llm-wiki-skill.md]
^[raw/articles/awesome-llm-wiki-readme.md]

## The infrastructure claim

The strongest practical argument for the wiki is that it needs almost nothing. `index.md`
read-first navigation "works surprisingly well at moderate scale (~100 sources, ~hundreds of
pages) and avoids the need for embedding-based RAG infrastructure," and the vault is "just a
directory of markdown files — open it in Obsidian, VS Code, or any editor. No database, no
special tooling required." ^[raw/articles/karpathy-llm-wiki-gist.md]
^[raw/articles/hermes-agent-llm-wiki-skill.md]

For a personal or small-team wiki that is decisive: no vector DB to run, no chunking
heuristics to tune, no embeddings to regenerate, and the artifact is portable plain text
that outlives any provider. See [[markdown-as-knowledge-substrate]].

## They are not mutually exclusive

This is the part the "RAG is dead" framing gets wrong, and the ecosystem agrees. Several
catalogued implementations add retrieval *to* a compiled wiki rather than instead of one:
one ships a local runtime with on-device semantic search (FastEmbed/sqlite-vec), BM25
lexical fallback, RRF hybrid fusion, and incremental changed-section indexing; another adds
research-on-miss query routing that explores and ingests missing concepts automatically.
^[raw/articles/awesome-llm-wiki-readme.md]

The sane composition: **compile for the knowledge you reuse, retrieve for the corpus you
don't.** A wiki page is a cache of synthesis — and like any cache it is worth having exactly
when hit rate is high and recompute is expensive. For a 50-page personal research wiki, hit
rate is near total. For 50,000 documents consulted once each, it is not.

Upstream's own scaling rule points the same way: past 100 pages, search the vault in
addition to reading the index — because the index alone starts to miss things.
^[raw/articles/hermes-agent-llm-wiki-skill.md] That is lexical search arriving in a
"no infrastructure" design, which tells you where the ceiling is.

## Verdict for this vault

This wiki has ~30 compiled pages and 9 raw sources. Index-first navigation is comfortably
sufficient; adding embeddings now would be infrastructure for its own sake. The trigger to
revisit: index sections exceeding 50 entries, or repeated cases of a query missing a page
that plainly existed. Both are observable — the first by `reindex`, the second by keeping a
log of failed lookups.

## Open questions

- **Where is the actual ceiling?** "Hundreds of pages" is an assertion, not a measurement.
  The catalogued Agentic Memory Index benchmark claims to test 12 agent memory architectures
  across 56 working sessions on recall, cross-conversation synthesis, temporal reasoning,
  conflicting facts, and erasure — but it is not captured here, so its results are not
  evidence in this wiki. ^[raw/articles/awesome-llm-wiki-readme.md]
- **Does compilation degrade model quality?** A wiki page written by a weaker model becomes
  the context a stronger model later trusts. No captured source addresses this.

## Related

[[llm-wiki-pattern]] · [[andrej-karpathy]] · [[three-layer-wiki-architecture]] ·
[[anti-slopification]] · [[markdown-as-knowledge-substrate]] ·
[[agent-knowledge-substrates]]
