---
title: Agentic memory vs compiled wiki
created: 2026-09-28
updated: 2026-09-28
type: concept
tags: [memory, agent, knowledge-management, controversy]
sources:
  - raw/articles/llm-wiki-review-companion-guide.md
  - raw/articles/hermes-agent-readme.md
  - raw/articles/karpathy-llm-wiki-gist.md
summary: Two different jobs — memory retains how you work; the wiki preserves source-traceable world knowledge. Neither should silently replace the other.
confidence: high
---

# Agentic memory vs compiled wiki

## The distinction

> "Agentic memory and the Wiki also have different jobs. Memory can retain how you work,
> preferences, and approved librarian lessons. The Wiki preserves source-traceable world
> knowledge. A memory provider should not silently replace the human-approved Wiki."
> ^[raw/articles/llm-wiki-review-companion-guide.md]

| | Agentic memory | Compiled wiki |
| --- | --- | --- |
| **Subject** | The user and the working relationship | The world |
| **Typical content** | Preferences, style, ongoing projects, lessons learned from past runs, "user prefers X" | Facts, concepts, entities, comparisons about the domain |
| **Provenance** | The conversation it came from | A hash-pinned capture in `raw/` — see [[source-traceability]] |
| **Who writes** | The agent, often autonomously | The agent, but through [[human-in-the-loop-review-gate]] |
| **Who approves** | Nobody, usually | A human, explicitly |
| **Portability** | Provider-specific store | A directory of markdown files |
| **Inspectable** | Varies; often opaque | Fully — it is text on disk |
| **Correct when wrong** | Edit the memory | Propose a change, get it reviewed, apply |

## Why the warning exists

The companion guide's sentence is defensive, and the defensiveness is informative. Memory
systems are convenient: they are automatic, they persist across sessions, and they feel like
"the agent remembers". A wiki requires an ingest step, a schema, and (with a gate) a human
decision. Under that pressure, the path of least resistance is to let memory accumulate what
should have been compiled — and then the knowledge is unsourced, unreviewed, unportable, and
invisible.

That is [[anti-slopification]] by a different route: not a bad synthesis written to the wiki,
but a good synthesis written *somewhere else* where no one curates it.

The second clause matters as much as the first: memory should not **silently** replace the
**human-approved** wiki. Two qualifiers. Replacement could be legitimate if it were explicit
and if the replacement preserved the approval property. Automatic memory does neither.

## How Hermes treats the two

[[hermes-agent]] is a useful case because it ships both, separately, and does not merge
them:

- **Agent-curated memory with periodic nudges** — the agent decides what to retain and is
  prompted to persist knowledge. ^[raw/articles/hermes-agent-readme.md]
- **FTS5 session search with LLM summarization** for cross-session recall — retrieval over
  past conversations, not a compiled artifact. ^[raw/articles/hermes-agent-readme.md]
- **Honcho dialectic user modeling** — an explicit model *of the user*, which is the memory
  side of the table above. ^[raw/articles/hermes-agent-readme.md]
- **The wiki** — a directory of markdown at `$WIKI_PATH`, owned by [[llm-wiki-skill]], with
  a schema, an index, a log, and provenance. ^[raw/articles/karpathy-llm-wiki-gist.md]

The learning loop ("creates skills from experience, improves them during use, nudges itself
to persist knowledge") is memory- and skill-shaped, not wiki-shaped. ^[raw/articles/hermes-agent-readme.md]
Note where "approved librarian lessons" would go in the guide's taxonomy: memory. A lesson
about *how to run the wiki* is procedural knowledge about the user's practice; a fact about
*the domain* belongs in the wiki.

## The gray zone, honestly

Some content is genuinely ambiguous:

- **"The user rejects claims sourced only to X."** A preference (memory) that is also a
  policy about wiki content (schema). Best home: `SCHEMA.md`, because it constrains
  compiled output and should be visible to any agent that reads the vault — memory is
  per-agent and per-provider, the schema is not.
- **"Last ingest of this URL was on date D."** Operational state. Belongs in `log.md`, which
  is append-only and parseable, not in memory. ^[raw/articles/karpathy-llm-wiki-gist.md]
- **"This concept page was deferred twice; stop proposing it."** A review outcome. Belongs
  in the proposal's own frontmatter (`decision: defer`, `status: deferred`), where the next
  run will see it during orientation.
- **A durable lesson about the domain discovered while working.** Wiki — but through a
  proposal, because it is a claim about the world and needs a source.

The rule that resolves most cases: **if it needs a source, it is wiki; if it needs a
session, it is memory; if it constrains future writes, it is schema.**

## Related

[[llm-wiki-pattern]] · [[three-layer-wiki-architecture]] · [[anti-slopification]] ·
[[hermes-agent]] · [[human-in-the-loop-review-gate]] · [[agent-knowledge-substrates]]
