---
title: Markdown as knowledge substrate
created: 2026-09-28
updated: 2026-09-28
type: concept
tags: [markdown, architecture, knowledge-management, tooling]
sources:
  - raw/articles/karpathy-llm-wiki-gist.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/awesome-llm-wiki-readme.md
summary: Why the pattern stores knowledge as plain interlinked markdown rather than a database — portability, diffability, and readability as design requirements.
confidence: high
---

# Markdown as knowledge substrate

## Definition

The wiki layer is "a directory of markdown files — open it in Obsidian, VS Code, or any
editor. No database, no special tooling required." ^[raw/articles/hermes-agent-llm-wiki-skill.md]
The community catalog describes the same choice as constructing "an interlinked, persistent
Markdown knowledge topology" out of "static source files". ^[raw/articles/awesome-llm-wiki-readme.md]

This is a substantive architectural decision, not a convenience. It determines what the
system can and cannot do.

## What plain files buy

**Diffability.** A text file under Git gives you a per-line history of every claim, who
changed it, and when. That is the backbone of the "Git-backed maintenance loop" the pattern's
tutorials describe ^[raw/articles/awesome-llm-wiki-readme.md] and the cheapest real
enforcement available to [[verification-layers]]: a refused write that changed bytes shows
up in `git status`.

**Portability and longevity.** No provider, no schema migration, no export step. The
artifact outlives the model that wrote it and the agent framework that hosted it. Several
catalogued implementations target *different* runtimes — Claude Code, Codex, Copilot CLI,
Cursor, Gemini CLI, OpenCode — against the same vault shape, which only works because the
substrate is neutral. ^[raw/articles/awesome-llm-wiki-readme.md]

**Human readability without tooling.** A reviewer can read a proposal in a text editor. This
matters more than it sounds: [[human-in-the-loop-review-gate]] asks a human to approve exact
bytes, and "exact bytes" is only meaningful if the human can see them unmediated. Karpathy's
schema note makes the same point from the other direction — the schema file is `CLAUDE.md`
for Claude Code or `AGENTS.md` for Codex, i.e. the runtime-specific name for one plain text
file. ^[raw/articles/karpathy-llm-wiki-gist.md]

**Inspectable provenance.** A `^[raw/path.md]` marker is legible to a human and greppable by
a script with no shared dependency. See [[provenance-markers]].

**Tooling that already exists.** `grep "^## \[" log.md | tail -5` gives recent activity; the
log format is designed for it. ^[raw/articles/karpathy-llm-wiki-gist.md] Frontmatter powers
Dataview and Bases queries in [[obsidian]] with no custom code.

**Graph structure for free.** Wikilinks make the vault a typed graph that Graph View renders
and lint can analyze — orphans, broken links, backlink counts — without a graph database.
One catalogued extension maps the same pattern onto Neo4j, which is an option precisely
because the markdown version already encodes the topology. ^[raw/articles/awesome-llm-wiki-readme.md]

## What it costs

**No query engine.** There is no index but the one you maintain. Upstream's answer is that
reading `index.md` first "works surprisingly well at moderate scale (~100 sources, ~hundreds
of pages)", with a search pass added past 100 pages. ^[raw/articles/hermes-agent-llm-wiki-skill.md]
That is a real ceiling, and the ecosystem's response is to bolt retrieval back on — hybrid
semantic plus BM25 with RRF fusion in one implementation. See [[llm-wiki-vs-rag]].

**Consistency is not enforced by the format.** A database rejects a row that violates its
schema; a markdown file accepts anything. Every structural guarantee has to come from an
external checker, which is why `tools/wiki_tool.py` exists and why frontmatter validation is
a lint error rather than a parse failure.

**Convention-heavy linking.** Wikilinks are resolved by file stem, so stems must be unique
across the vault and renames break inbound links silently. Obsidian updates links on rename
inside its own UI; an agent renaming a file with `mv` does not.

**Duplication is easy.** Nothing stops two pages covering the same entity under different
names. The defense is procedural — always orient before creating, search past 100 pages,
lint for orphans — not structural. ^[raw/articles/hermes-agent-llm-wiki-skill.md]

**Scale of a single file.** A page past ~200 lines stops being scannable, so the schema
forces splits. A database would paginate; markdown must be restructured by hand.

## Conventions this vault adds

- Frontmatter is a **restricted YAML subset** parsed by `wiki_tool.py`: scalars, inline
  lists, block lists, one nesting level. Anything exotic will not round-trip, so do not use it.
- Wikilinks are **bare stems** (`[[llm-wiki-pattern]]`), never paths. Lint errors on
  `[[concepts/x]]`.
- Examples in documentation pages are written in inline code or fenced blocks, because lint
  strips code before scanning for links and markers. A literal `[[foo]]` in prose is a live
  reference whether you meant it or not.
- `index.md` is **machine-generated** by `reindex` from each page's `summary:` field. Hand
  edits are overwritten. `log.md` is append-only and machine-appended by tool actions.

## Related

[[llm-wiki-pattern]] · [[three-layer-wiki-architecture]] · [[obsidian]] ·
[[llm-wiki-vs-rag]] · [[verification-layers]]
