---
title: Immutable raw layer
created: 2026-09-28
updated: 2026-09-28
type: concept
tags: [provenance, verification, markdown, knowledge-management]
sources:
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/llm-wiki-review-skill.md
  - raw/articles/karpathy-llm-wiki-gist.md
summary: Layer 1 of the wiki — captured sources that are never edited, each carrying a SHA-256 of its body so re-ingest can skip unchanged content and flag drift.
confidence: high
---

# Immutable raw layer

## Definition

Layer 1 of the [[three-layer-wiki-architecture]]: the curated collection of source documents
— articles, papers, images, data files. **These are immutable. The LLM reads from them but
never modifies them. This is your source of truth.** ^[raw/articles/karpathy-llm-wiki-gist.md]

Upstream states it as the first pitfall: "Never modify files in `raw/` — sources are
immutable. Corrections go in wiki pages." ^[raw/articles/hermes-agent-llm-wiki-skill.md]

In this vault: `wiki/raw/{articles,papers,transcripts,assets}/`.

## Capture format

Every raw markdown capture gets frontmatter so re-ingests can detect drift:

```yaml
---
source_url: https://example.com/article
ingested: YYYY-MM-DD
sha256: <hex digest of the raw content below the frontmatter>
---
```

The hash is computed **over the body only** — everything after the closing `---`, not the
frontmatter itself. ^[raw/articles/hermes-agent-llm-wiki-skill.md]

Two conventions this vault adds, both from the review skill:

1. **Exactly one blank line** separates the closing `---` from the body.
2. **Verify immediately after writing.** Recompute the hash by removing the frontmatter and
   that one separator; if it does not match, correct the metadata before doing anything
   else. ^[raw/articles/llm-wiki-review-skill.md]

The point of rule 2 is that a capture whose hash is wrong is worse than no capture: it will
later be reported as "drift" and waste an investigation, or worse, pass verification because
nobody rechecks. `tools/wiki_tool.py capture` implements hash-then-verify as one atomic step
so the check cannot be skipped. See [[verification-layers]].

## What the hash buys

- **Idempotent re-ingest.** Same URL, same hash → skip processing. Cheap enough to do every
  time. ^[raw/articles/hermes-agent-llm-wiki-skill.md]
- **Drift detection.** Same URL, different hash → the source changed. Flag it and update
  downstream pages deliberately, not silently.
- **Tamper evidence.** If a `raw/` file was edited, its hash no longer matches. Lint reports
  this. Not a hard error, but always worth investigating, because `raw/` should never change.
- **Version pinning of procedures.** The strongest demonstration in this vault: the
  qualification report froze the SHA-256 of both skills, and recomputing them from the
  captures confirms the tested artifacts are the installed ones. See [[llm-wiki-skill]] and
  [[llm-wiki-review-skill]].

## Non-verbatim captures

Sometimes the body cannot be a byte-exact copy — a video with no transcript, an HTML page
kept as HTML, a locally supplied file. Rather than pretend, add a `capture_note` field
stating what the body actually is. This vault has two:

| File | Note |
| --- | --- |
| `raw/transcripts/wanderloots-llm-wiki-obsidian-video.md` | Metadata-only capture via oEmbed; no transcript. Body is generated, not a copy. |
| `raw/papers/lewis-retrieval-augmented-generation-2020.md` | HTML abstract page of arXiv:2005.11401, captured as-is (not the PDF). |

The consequence is a **claim limit**, not just a note: nothing in this wiki may be sourced
to what was *said* in that video, because no spoken content was captured. [[wanderloots]]
records this explicitly and sets `confidence: medium`. That is
[[source-traceability]] doing its job — the gap is visible instead of hidden.

## Nested frontmatter

Three captures in this vault are themselves markdown files that begin with `---` (the two
skill files and the qualification report, supplied with their own frontmatter). They are
stored verbatim, so the file has frontmatter, a blank line, then a body that starts with
another `---` block.

This is valid but has one trap: **strip by position, not by pattern.** Find the *second*
line that is exactly `---` and take everything after it plus one blank line. Any tool that
regex-matches "the first `---...---` block" will silently strip the source's own frontmatter
and produce a hash that cannot be reproduced. `wiki_tool.py` uses positional stripping.

## Related

[[three-layer-wiki-architecture]] · [[source-traceability]] · [[verification-layers]] ·
[[provenance-markers]] · [[llm-wiki-skill]]
