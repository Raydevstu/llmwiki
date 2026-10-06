---
type: llm-wiki-review
status: needs-review
decision: pending
revision: 1
operation: conflict-resolution
target: concepts/index-first-navigation.md
created: 2026-09-28
updated: 2026-09-28
sources:
  - raw/articles/karpathy-llm-wiki-gist.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/awesome-llm-wiki-readme.md
target_exists: false
target_sha256: null
proposed_sha256: a5e56170eb8a71ceb2377362d49ecca9e0174605602a921bc759f7b9e083d5f0
---

# Proposed Wiki change

## What will change

Create `concepts/index-first-navigation.md` recording an **unresolved disagreement** between
two authoritative sources about whether index-first navigation is sufficient for a large
wiki. Both claims are preserved verbatim with their dates and sources, and the page is marked
`contested: true` so lint surfaces it for review rather than letting one position harden into
wiki fact.

No existing compiled page is modified by this proposal. Three pages currently assert one side
or the other in passing — [[llm-wiki-pattern]], [[llm-wiki-vs-rag]], and
[[markdown-as-knowledge-substrate]]. If you approve, they should gain a link to the new page
in a **separate** follow-up proposal, so this decision stays narrow.

## Competing claims

**Claim A — index-first navigation is sufficient at moderate scale.**
> "This works surprisingly well at moderate scale (~100 sources, ~hundreds of pages) and
> avoids the need for embedding-based RAG infrastructure."
> — `raw/articles/karpathy-llm-wiki-gist.md`, captured 2026-09-28

**Claim B — past ~100 pages the index alone misses things, so search must be added.**
> "For large wikis (100+ pages), also run a quick `search_files` for the topic at hand before
> creating anything new."
> — `raw/articles/hermes-agent-llm-wiki-skill.md`, captured 2026-09-28

Corroborating B from a third source: several catalogued implementations add on-device
semantic search with BM25 fallback and RRF hybrid fusion to a compiled markdown vault, which
is retrieval infrastructure inside a design that claimed not to need it
(`raw/articles/awesome-llm-wiki-readme.md`).

## Proposed content

```markdown
---
title: Index-first navigation and its scale ceiling
created: 2026-09-28
updated: 2026-09-28
type: concept
tags: [knowledge-management, architecture, controversy, tooling, markdown]
sources:
  - raw/articles/karpathy-llm-wiki-gist.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/awesome-llm-wiki-readme.md
summary: Two sources disagree about whether reading index.md first suffices as a wiki grows; both positions are recorded here rather than one being chosen.
confidence: medium
contested: true
contradictions: []
---

# Index-first navigation and its scale ceiling

## Definition

**Index-first navigation** is the retrieval strategy of the [[llm-wiki-pattern]]: when
answering a query, read `index.md` first to identify relevant pages, then drill into them.
No embeddings, no vector store, no chunking policy — one maintained catalog file and an
editor. ^[raw/articles/karpathy-llm-wiki-gist.md]

It is the reason a compiled wiki needs almost no infrastructure, and therefore the reason
the pattern is attractive at all. See [[markdown-as-knowledge-substrate]].

## The disagreement

This page exists because two authoritative sources give different answers to "how far does
that scale?", and the difference matters: it decides whether a growing wiki needs retrieval
infrastructure or only discipline.

**Position A — sufficient at moderate scale.**

> "This works surprisingly well at moderate scale (~100 sources, ~hundreds of pages) and
> avoids the need for embedding-based RAG infrastructure."
> ^[raw/articles/karpathy-llm-wiki-gist.md]

**Position B — insufficient past ~100 pages.**

> "For large wikis (100+ pages), also run a quick `search_files` for the topic at hand before
> creating anything new."
> ^[raw/articles/hermes-agent-llm-wiki-skill.md]

Upstream states the same limit twice more: for query operations, "For wikis with 100+ pages,
also `search_files` across all `.md` files for key terms — **the index alone may miss
relevant content**"; and as a scaling rule, past 100 pages search the vault because the index
alone starts to miss things. ^[raw/articles/hermes-agent-llm-wiki-skill.md]

Both captures were taken on 2026-09-28, so this is not a case of a newer source superseding
an older one. It is a genuine disagreement about the design, held at the same time.

## Reading 1: these are compatible

Position A is about **retrieval for answering** — reading a catalog is enough to find the
right pages. Position B is about **deduplication before creating** — a catalog of summaries is
not enough to be confident no page already covers this entity under a different name. Those
are different tasks with different failure costs: a missed page in a query produces an
incomplete answer, while a missed page during ingest produces a permanent duplicate that
splits the evidence for one entity across two files. See [[skipping-orientation]].

Under this reading both claims are true and the `contested` marker should be removed.

## Reading 2: these conflict about the design's ceiling

Position A explicitly frames index-first navigation as what "**avoids the need for
embedding-based RAG infrastructure**". Position B reintroduces search — a retrieval mechanism
— at exactly the scale where A claims none is needed. If searching the corpus is required past
100 pages, then the infrastructure-free property is bounded at ~100 pages, and A's
"~hundreds of pages" is optimistic by roughly an order of magnitude at the top of its range.

The ecosystem leans this way. Several catalogued implementations add real retrieval to a
compiled markdown vault: one ships a local runtime with on-device semantic search
(FastEmbed/sqlite-vec), BM25 lexical fallback, RRF hybrid fusion, and incremental
changed-section indexing; another adds research-on-miss query routing that automatically
explores and ingests missing concepts. ^[raw/articles/awesome-llm-wiki-readme.md] Independent
implementers kept hitting a wall and building the thing the design said was unnecessary.

Under this reading the disagreement is real and should stay marked `contested`.

## Why it is left unresolved

No captured source **measures** the ceiling. Position A offers an estimate in parentheses;
Position B offers a rule of thumb at a round number; the implementations offer existence
proofs that some builders wanted retrieval, not evidence about where the boundary falls. The
catalogued Agentic Memory Index benchmark claims to test 12 agent memory architectures across
56 working sessions on direct recall and cross-conversation synthesis
^[raw/articles/awesome-llm-wiki-readme.md] — but it is not captured in this vault, so it is
not evidence here. See [[source-traceability]].

Choosing a side would therefore be selecting a winner without stronger evidence, which the
review convention forbids. Both positions are recorded with dates and sources instead, and
`confidence: medium` reflects that the page describes a disagreement rather than settling one.
See [[confidence-and-contested-markers]].

## Practical stance for this vault

At ~30 compiled pages and 9 raw captures, both positions agree the index suffices, so the
disagreement is not yet operative. The observable triggers that would make it operative:

- Any `index.md` section exceeding 50 entries — the schema's own split threshold, and the
  point where scanning a section stops being reliable.
- A query that misses a page which plainly existed — log these; two or three is a pattern,
  not bad luck.
- An ingest that creates a near-duplicate — evidence that deduplication by index failed,
  which is Position B's specific claim.

Until one fires, adding retrieval would be infrastructure for its own sake. See
[[llm-wiki-vs-rag]] and [[agent-knowledge-substrates]].

## Related

[[llm-wiki-pattern]] · [[llm-wiki-vs-rag]] · [[markdown-as-knowledge-substrate]] ·
[[skipping-orientation]] · [[open-source-agent-skills]] · [[agent-knowledge-substrates]]
```

## Evidence and uncertainty

**Supporting sources.** Three captures, all hash-verified on 2026-09-28: Karpathy's gist
(Position A), the Hermes built-in skill (Position B, stated three separate times), and
`awesome-llm-wiki` (ecosystem corroboration for B). Both quotations are verbatim from the
captures and can be checked with `grep -n "surprisingly well" raw/articles/karpathy-llm-wiki-gist.md`.

**Uncertainty.**

- The proposed page's "Reading 1" and "Reading 2" are **this agent's analysis**, not claims
  made by any source. They are labelled as readings for that reason, and the provenance
  markers are attached only to the quoted source material.
- `contradictions: []` is deliberately empty. Neither existing page states the opposite
  claim; they each assert one side in passing. Naming them would overstate the conflict —
  but if you prefer them named so lint pairs the pages explicitly, say so under *Advanced:
  revise* and the follow-up proposal will set `contradictions: [llm-wiki-pattern]`.
- The ecosystem evidence for Position B is a cataloguer's **descriptions** of other
  projects, not those projects' own documentation. It shows that builders added retrieval; it
  does not show why, or at what scale. [[open-source-agent-skills]] carries
  `confidence: medium` for the same reason.
- `~100 sources, ~hundreds of pages` versus `100+ pages` may be a units mismatch rather than a
  disagreement — sources and pages are not the same count. That possibility strengthens
  Reading 1 and is not resolved by any captured source.

**Conflicting claims.** Yes — that is the subject of the proposal. The default resolution
preserves both and marks the page `contested: true`.

## Human feedback

Choose one:

- **Keep both:** approve this proposal — both claims are preserved and the topic is marked contested.
- **Not a contradiction:** revise it to preserve compatible or context-dependent claims without `contested`, then stop for approval again. (Reading 1 above is the obvious basis: A is about query retrieval, B is about pre-creation deduplication.)
- **Decide later:** defer without changing compiled content.

Advanced: revise — prefer a source or supply a custom resolution. Requires a reason or
stronger evidence. Never silently select a winner.

---

Or answer from the CLI:

```bash
python3 tools/wiki_tool.py apply 2026-09-28-index-first-navigation-proposal.md --decision approve --revision 1
python3 tools/wiki_tool.py apply 2026-09-28-index-first-navigation-proposal.md --decision defer --feedback "capture the Agentic Memory Index benchmark first"
```

Editing this note alone does not trigger anything. **Silence and elapsed time are never
approval.** This proposal has been `pending` since 2026-09-28 and will remain so until a
human decides.
