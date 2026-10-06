---
title: Andrej Karpathy
created: 2026-09-28
updated: 2026-09-28
type: entity
tags: [person, model, open-source]
sources:
  - raw/articles/karpathy-llm-wiki-gist.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/awesome-llm-wiki-readme.md
summary: Researcher whose "LLM Wiki" gist defined the compiled-knowledge-base pattern this vault implements.
confidence: high
---

# Andrej Karpathy

## Overview

Researcher and educator, and the originator of the [[llm-wiki-pattern]] this vault
implements. He published the pattern as an *idea file* — a gist explicitly designed to be
pasted into an agent (Codex, Claude Code, OpenCode) so the agent builds out the specifics
in collaboration with the user, rather than as a finished specification. ^[raw/articles/karpathy-llm-wiki-gist.md]

## The LLM Wiki gist

`gist.github.com/karpathy/442a6bf555914893e9891c11519de94f` — captured in this vault at
`raw/articles/karpathy-llm-wiki-gist.md`.

Key claims from the gist, all traceable to that capture:

- The default LLM-and-documents experience is RAG: retrieve chunks at query time, generate
  an answer, retain nothing. "The LLM is rediscovering knowledge from scratch on every
  question. There's no accumulation." ^[raw/articles/karpathy-llm-wiki-gist.md]
- The alternative is a **persistent, compounding artifact**: the model reads a source,
  integrates it into interlinked markdown, updates entity and topic pages, notes
  contradictions, and strengthens or challenges the evolving synthesis. Knowledge is
  compiled once and kept current. See [[llm-wiki-vs-rag]].
- **Division of labor:** "You never (or rarely) write the wiki yourself — the LLM writes
  and maintains all of it. You're in charge of sourcing, exploration, and asking the right
  questions." ^[raw/articles/karpathy-llm-wiki-gist.md]
- His working setup is the model on one side and [[obsidian]] on the other, browsing
  results in real time: "Obsidian is the IDE; the LLM is the programmer; the wiki is the
  codebase." ^[raw/articles/karpathy-llm-wiki-gist.md]
- Three operations: **ingest**, **query**, **lint**. A single source may touch 10–15 wiki
  pages, and that is the intended compounding effect.
- `index.md` (content catalog) plus `log.md` (append-only chronology) "works surprisingly
  well at moderate scale (~100 sources, ~hundreds of pages) and avoids the need for
  embedding-based RAG infrastructure." ^[raw/articles/karpathy-llm-wiki-gist.md]

## Applications he names

Personal tracking · multi-week research with an evolving thesis · reading a book (a
personal Tolkien Gateway-style companion wiki) · business/team wikis fed by Slack,
transcripts and customer calls — "possibly with humans in the loop reviewing updates" ·
competitive analysis, due diligence, trip planning, course notes, hobby deep-dives.
^[raw/articles/karpathy-llm-wiki-gist.md]

That parenthetical about humans in the loop is the seed of
[[human-in-the-loop-review-gate]].

## Influence

The pattern spread fast enough to acquire its own ecosystem: a curated list
(`awesome-llm-wiki`) cataloguing gists, frameworks, compilers, MCP servers and reference
vaults; multiple architectural extensions (v2 memory lifecycles and confidence decay, v3
state-space and segmentation variants); and a built-in implementation shipped by
[[nous-research]] as the [[llm-wiki-skill]] inside [[hermes-agent]].
^[raw/articles/awesome-llm-wiki-readme.md]

## Open questions

- **Scale ceiling.** The gist's claim that index-first navigation suffices is scoped to
  "~hundreds of pages". Beyond that, whether embedding search becomes necessary is
  unresolved here — no captured source measures it.
- **Trust.** Karpathy's framing has the human curating *sources* and the model owning the
  compiled layer outright. Whether that is safe enough for consequential knowledge is the
  question [[anti-slopification]] and [[review-companion-vs-agentic-librarian]] argue about.

## Related

[[llm-wiki-pattern]] · [[three-layer-wiki-architecture]] · [[nous-research]] ·
[[obsidian]] · [[wanderloots]]
