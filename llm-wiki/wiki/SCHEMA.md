# Wiki Schema

> Layer 3 of the [[three-layer-wiki-architecture]]. This file constrains how the agent
> reads, writes, and maintains every other file in this vault. Read it before any operation.
>
> **Machine-readable:** `tools/wiki_tool.py lint` enforces the rules below. `reindex`
> rebuilds `index.md` from page frontmatter. Do not hand-edit `index.md` if you plan to
> run `reindex`.

## Domain

**AI / LLM research, agents, and knowledge tooling.**

In scope: large language models and their architectures; agentic systems, skills, and
orchestration; knowledge-base and memory patterns (LLM Wiki, RAG, Zettelkasten); the
tooling those patterns run on (Obsidian, Hermes Agent, Claude Code, MCP servers);
provenance, verification, and human-review practice for AI-compiled knowledge; the
people, labs, and companies that produce the above.

Out of scope: personal journaling and health tracking, finance and investing, general
software engineering unrelated to knowledge systems, and anything where no captured
source exists. Out-of-scope mentions get no page — see **Page Thresholds**.

## Directory Layout

```
wiki/
├── SCHEMA.md            # this file — conventions, taxonomy, thresholds
├── index.md             # machine-maintained catalog (tools/wiki_tool.py reindex)
├── log.md               # append-only action log
├── raw/                 # Layer 1 — IMMUTABLE. Never edited after capture.
│   ├── articles/        #   web articles, gists, READMEs, skill files
│   ├── papers/          #   PDFs and arXiv abstract pages
│   ├── transcripts/     #   video/meeting captures and their metadata
│   └── assets/          #   images, referenced as ![[asset.png]]
├── entities/            # Layer 2 — people, orgs, products, tools, models
├── concepts/            # Layer 2 — ideas, patterns, techniques
├── comparisons/         # Layer 2 — side-by-side analyses
├── queries/             # Layer 2 — filed answers worth keeping
├── review/              # human-review proposals (never auto-applied)
└── _meta/               # topic maps, audits, vault-level analysis
```

## Conventions

- **File names:** lowercase, hyphens, no spaces, `.md` (e.g. `llm-wiki-pattern.md`).
  The file stem is the wikilink target, so stems must be unique across the whole vault.
- **Frontmatter is mandatory** on every compiled page (see below). A page without valid
  frontmatter is a lint error and must not be applied from a review proposal.
- **Wikilinks:** use `[[stem]]`, never `[[folder/stem]]` and never a path into `raw/`.
  Minimum **2 outbound links** per compiled page; check that linked pages link back.
- **Dates:** `created` is set once and never changed. `updated` is bumped on every edit.
- **Every new page** gets a `summary:` field — `reindex` builds `index.md` from it.
- **Every action** is appended to `log.md`. No silent writes.
- **Never modify `raw/`.** Corrections live in compiled pages. If a raw file must change,
  it is a new capture, and its hash changes with it.
- **Never let a path escape the vault root.** `..`, absolute paths, and symlinks out of
  the vault are rejected by `lint` and by `apply`.

### Provenance markers

On any page synthesizing **3+ sources**, end paragraphs whose claims come from one
specific source with a provenance marker:

```markdown
The wiki is a persistent, compounding artifact. ^[raw/articles/karpathy-llm-wiki-gist.md]
```

The path is vault-relative and must resolve to a real file (lint checks this). Optional
on single-source pages, where `sources:` frontmatter is enough. This is what makes
[[source-traceability]] auditable per-claim rather than per-page.

## Frontmatter

### Compiled pages (`entities/`, `concepts/`, `comparisons/`, `queries/`, `_meta/`)

```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [from the taxonomy below]
sources: [raw/articles/source-name.md]
summary: One line, <=160 chars, used verbatim in index.md.
# Optional quality signals:
confidence: high | medium | low     # how well-supported the claims are
contested: true                     # unresolved contradiction on this page
contradictions: [other-page-stem]   # pages this one conflicts with
---
```

Required: `title`, `created`, `updated`, `type`, `tags`, `sources`, `summary`.
If no tag applies, write `tags: []` — never omit the field.

`confidence` and `contested` are optional but recommended for fast-moving topics.
Lint surfaces `contested: true` and `confidence: low` for review so weak claims do not
silently harden into accepted fact — the failure mode [[anti-slopification]] exists to
prevent.

### Raw captures (`raw/**`)

```yaml
---
source_url: https://example.com/article   # or local-upload:<name> for user-supplied files
ingested: YYYY-MM-DD
sha256: <hex digest of the body only, computed after the frontmatter is stripped>
capture_note: <only when the body is not a byte-exact copy of the source>
---

<body, unchanged>
```

Exactly **one blank line** separates the closing `---` from the body. The hash covers
the body and nothing else, so re-capturing the same URL either skips (identical hash) or
flags drift (different hash). See [[immutable-raw-layer]].

### Review proposals (`review/**`)

```yaml
---
type: llm-wiki-review
status: needs-review | applied | rejected | deferred
decision: pending | approve | reject | revise | defer
revision: 1
operation: create | update | conflict-resolution
target: concepts/example.md          # vault-relative; must stay inside the vault
sources:
  - raw/articles/example-source.md
---
```

Proposal files are named `review/YYYY-MM-DD-<target-stem>-proposal.md`. Only the five
canonical `decision` values above are valid. See [[human-in-the-loop-review-gate]].

## Tag Taxonomy

Every tag on a page must appear in this list. **Add the tag here first, then use it.**
Freeform tags decay into noise. (Lint reads this section as the authoritative taxonomy —
keep tags as bare lowercase words in these bullets.)

- **Subject:** model, architecture, agent, person, company, lab, open-source, tooling, obsidian
- **Practice:** knowledge-management, provenance, verification, review, memory, automation, workflow
- **Property:** markdown, trust
- **Meta:** comparison, timeline, controversy, prediction

## Page Thresholds

- **Create a page** when an entity or concept appears in **2+ sources**, or is central to
  one source and load-bearing for the domain.
- **Add to an existing page** when a source mentions something already covered. Updating
  beats creating: a growing wiki is not a pile of near-duplicates.
- **Do NOT create a page** for passing mentions, minor details, or anything out of domain.
- **Split a page** past ~200 lines into sub-topics with cross-links (lint warns at 200).
- **Archive a page** when fully superseded: move it to `_archive/` keeping its relative
  path, remove it from `index.md`, and replace inbound wikilinks with plain text plus
  "(archived)". Log the archive action.

## Page Types

**Entity pages** (`entities/`) — one per notable person, org, product, tool, or model.
Overview · key facts and dates · relationships as wikilinks · source references.

**Concept pages** (`concepts/`) — one per idea or technique. Definition · current state of
knowledge · open questions and debates · related concepts as wikilinks.

**Comparison pages** (`comparisons/`) — what is compared and why · dimensions in a table ·
verdict or synthesis · sources. Prefer a table over prose for the dimensions.

**Query pages** (`queries/`) — a filed answer worth keeping. The question verbatim · the
answer · which pages it drew on · what would change the answer. File only answers that
would be painful to re-derive; never file trivial lookups.

## Update Policy

When new information conflicts with existing content:

1. **Check dates.** Newer sources generally supersede older ones — but only for factual
   drift, not for genuine disagreement.
2. **If genuinely contradictory,** record both positions with their dates and sources.
   Do not silently overwrite and do not silently pick a winner.
3. **Mark it in frontmatter:** `contested: true` and `contradictions: [page-stem]`.
4. **Route it through review.** Under [[human-in-the-loop-review-gate]], a contradiction
   becomes an `operation: conflict-resolution` proposal with three primary choices:
   keep both, not a contradiction, decide later. Preferring a source is an *advanced*
   revision and requires a reason or stronger evidence.
5. **Flag for user review** in the lint report.

## Scaling Rules

- Any `index.md` section past **50 entries** splits into sub-sections by first letter or
  sub-domain.
- Past **200 total entries**, add `_meta/topic-map.md` grouping pages by theme.
- Past **500 log entries**, rotate: rename `log.md` to `log-YYYY.md` and start fresh.
- Past **100 pages**, search the vault for the topic before creating anything new — the
  index alone starts to miss things.

## Obsidian Integration

This vault is an Obsidian vault as-is. Wikilinks render as links, Graph View shows the
knowledge network, and YAML frontmatter powers Dataview and Bases.

- Set Obsidian's attachment folder to `raw/assets/`.
- Keep "Wikilinks" enabled (default).
- Optional: Dataview, e.g. `TABLE confidence, updated FROM "concepts" WHERE contested`
- Optional: exclude `raw/` from search if you want compiled pages only.

## Known Limitations

The review gate is an **instruction-based convention, not a security boundary**. Its
reliability depends on the model following the skill. `tools/wiki_tool.py` adds real
mechanical enforcement for hashes, schemas, path escape, and revision binding, but it
cannot stop an agent that simply does not call it. Keep Git or another backup enabled.
