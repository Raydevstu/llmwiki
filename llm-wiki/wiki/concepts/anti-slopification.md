---
title: Anti-slopification
created: 2026-09-28
updated: 2026-09-28
type: concept
tags: [trust, knowledge-management, controversy, review]
sources:
  - raw/articles/llm-wiki-review-companion-guide.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/llm-wiki-review-skill.md
  - raw/articles/karpathy-llm-wiki-gist.md
summary: The stated goal of the review gate — preventing an AI-maintained wiki from silently converting plausible-sounding synthesis into permanent, trusted fact.
confidence: medium
---

# Anti-slopification

## Definition

The Review Companion names its purpose directly: **"The goal is anti-slopification: let AI
organize knowledge without silently turning every plausible synthesis into permanent truth.
Raw evidence remains inspectable, the human controls promotion, and the Wiki becomes a
deliberately curated library of truth."** ^[raw/articles/llm-wiki-review-companion-guide.md]

"Slop" here is not low-quality prose. It is a specific epistemic failure: a claim that is
*fluently stated, structurally correct, and plausibly derived* gets written into the
compiled layer, where it acquires the authority of everything around it — frontmatter,
wikilinks, a `sources:` list, an index entry, a log line. Nothing about its presentation
marks it as weaker than its neighbors.

## Why the pattern is especially exposed to it

The [[llm-wiki-pattern]] is designed to compound. That is its whole advantage over
[[llm-wiki-vs-rag]] — and compounding is also the mechanism by which one bad synthesis
propagates:

1. A plausible claim is written to a concept page during ingest.
2. A later ingest cross-references that page, treating it as established.
3. A query synthesizes an answer from several pages including it, and the answer gets filed
   back into `queries/` — Karpathy's "good answers can be filed back into the wiki as new
   pages." ^[raw/articles/karpathy-llm-wiki-gist.md]
4. The claim now has multiple inbound links and appears in the index. It looks corroborated.
   It is not; it is *echoed*.

The pattern's own safeguards are aimed at exactly this. Upstream: "Lint surfaces
`contested: true` and `confidence: low` pages for review so weak claims don't silently
harden into accepted wiki fact." ^[raw/articles/hermes-agent-llm-wiki-skill.md] That
sentence is anti-slopification stated as a lint requirement. See
[[confidence-and-contested-markers]].

Note that the wiki's advantage over chat is also what makes the risk worse: a bad answer in
chat disappears, while a bad answer in the wiki persists and gets cited.

## The four defenses

| Defense | Mechanism | Layer |
| --- | --- | --- |
| **Inspectable evidence** | `raw/` is immutable and hash-pinned, so any claim can be traced to a byte-exact source | 1 |
| **Human-controlled promotion** | Nothing enters the compiled layer without an explicit decision; silence is never approval | 2 |
| **Mechanical verification** | Schema, hash, path-escape, and revision-binding checks that do not depend on the model complying | 3 |
| **Visible weakness** | `confidence` and `contested` frontmatter so weak claims are marked rather than blending in | 2/3 |

Sources: ^[raw/articles/llm-wiki-review-companion-guide.md] ^[raw/articles/llm-wiki-review-skill.md]
See [[three-layer-wiki-architecture]] and [[verification-layers]].

The first and third are the ones that hold up under a misbehaving model. The second depends
on the model actually stopping. The fourth depends on the model being honest about its own
uncertainty — useful, but it is a signal the same process produces, so it cannot be the
only check.

## What it does not solve

`confidence: medium` on this page, for three reasons.

- **The term is one source's framing.** "Anti-slopification" appears in the companion guide,
  not in Karpathy's gist or upstream [[llm-wiki-skill]]. It is a good name for a real
  failure mode, but the analysis on this page is partly mine, not wholly sourced.
- **The gate is not enforcement.** "This skill is an instruction-based review convention,
  not a deterministic security boundary. Its reliability depends on the model following the
  skill." ^[raw/articles/llm-wiki-review-companion-guide.md] A model that does not stop is
  not stopped by a document telling it to stop.
- **Human review has its own failure mode.** A reviewer who approves 40 proposals in a row
  without reading them has built a rubber stamp, and the wiki is now slop with an audit
  trail. Nothing in the captured sources measures reviewer diligence over time. The
  qualification report's outstanding release check — "Confirm a beginner understands the
  proposal and three contradiction choices in Obsidian" — is aimed at this.
  ^[raw/articles/llm-wiki-review-qualification-report.md]

## Practical stance

Treat the compiled layer as **proposed truth pending review**, not as truth. Concretely, in
this vault: run ingest through [[human-in-the-loop-review-gate]]; require
[[provenance-markers]] on any page synthesizing 3+ sources; keep `raw/` hash-verified so
drift is detectable; and lint on a schedule so orphans, staleness, and unmarked
single-source claims surface before they harden.

## Related

[[human-in-the-loop-review-gate]] · [[confidence-and-contested-markers]] ·
[[source-traceability]] · [[llm-wiki-pattern]] · [[verification-layers]]
