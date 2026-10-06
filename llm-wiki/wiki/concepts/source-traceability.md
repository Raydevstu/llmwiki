---
title: Source traceability
created: 2026-09-28
updated: 2026-09-28
type: concept
tags: [provenance, verification, trust, knowledge-management]
sources:
  - raw/articles/llm-wiki-review-skill.md
  - raw/articles/llm-wiki-review-companion-guide.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/llm-wiki-review-qualification-report.md
summary: Every compiled claim can be followed back to an immutable, hash-pinned capture — and gaps in that chain stay visible instead of hidden.
confidence: high
---

# Source traceability

## Definition

The property that any claim in the compiled layer can be followed back, in a bounded number
of steps, to a specific immutable capture in `raw/`. Not "the page lists its sources" but
"this sentence came from this file, which is byte-identical to what was captured on this
date from this URL."

It is a completion check in the review skill — "Raw material remains source-traceable and
unchanged" ^[raw/articles/llm-wiki-review-skill.md] — and a pre-approval validation step in
the companion: before applying an approval it "checks source traceability" alongside schema
validity, target drift, and path containment. ^[raw/articles/llm-wiki-review-companion-guide.md]

## The chain

```
claim in a compiled page
  → ^[raw/...] provenance marker (paragraph-level)     see provenance-markers
  → sources: frontmatter (page-level)
  → raw/ file with source_url + ingested + sha256       see immutable-raw-layer
  → the external source itself
```

Each link has a distinct job, and a chain missing any of them degrades:

| Link | Answers | If missing |
| --- | --- | --- |
| [[provenance-markers]] | Which source supports this paragraph? | Reader must reread every listed source |
| `sources:` frontmatter | Which sources informed this page? | No way to find the inputs at all |
| `sha256` in raw | Is the capture still what was captured? | Silent edits and drift become undetectable |
| `source_url` | Where did this come from originally? | The chain terminates at a file with no origin |
| [[immutable-raw-layer]] | Can the origin be trusted not to have moved? | Everything above becomes advisory |

## Traceability includes recording what you *don't* have

The most instructive case in this vault is a negative one. The video capture at
`raw/transcripts/wanderloots-llm-wiki-obsidian-video.md` holds **metadata only** — title,
channel, URL, thumbnail, via oEmbed — with a `capture_note` saying so and an explicit
statement that no claims may be sourced to the video's spoken content.

Consequently [[wanderloots]] carries `confidence: medium`, and its "what the video covers"
table is sourced to a *third-party description* in `raw/articles/awesome-llm-wiki-readme.md`
rather than to the video. The gap is documented at the point of use, not buried in a raw
file nobody reads.

That is traceability working as intended. A system that only records what it knows is
indistinguishable from one that cannot tell you what it does not know.

## How it fails

1. **Unverifiable paraphrase.** The marker points at a real file that does not actually
   support the claim. Lint cannot catch this; only a reader or a verification agent can.
2. **Drift.** The source at `source_url` changed after capture. The stored hash still
   matches the local file, so lint reports nothing — the capture is faithful to *what it was*.
   Detecting upstream movement requires re-fetching and comparing, which no captured source
   automates here. Treat "the hash matches" as *not tampered with locally*, never as *still
   current upstream*.
3. **Circular citation.** Page A cites page B cites page A, with no raw source at the root.
   Orphan and backlink checks do not catch this. `lint` flags compiled pages whose
   `sources:` list contains no `raw/` path, which is the cheap approximation.
4. **Echo chambers.** One bad synthesis gets cross-referenced by later ingests until it
   looks corroborated. Multiple inbound links are not multiple sources. This is the
   propagation path described in [[anti-slopification]].

## Verification is a separate layer

Traceability makes verification *possible*; it does not perform it. The review skill is
explicit that it "provides a review convention, not deterministic enforcement," and directs
users to the full Agentic Librarian "when hashes, receipts, replay safety, automation, or
mechanically enforced policies are required." ^[raw/articles/llm-wiki-review-skill.md]

In this vault, `tools/wiki_tool.py` supplies the mechanical subset: recompute and compare
every raw hash, validate that every marker path resolves, confirm every compiled page lists
at least one `raw/` source, and refuse proposals whose target escapes the vault. What it
cannot do is decide whether a paragraph means what its marker implies. See
[[verification-layers]] and [[review-companion-vs-agentic-librarian]].

## Related

[[provenance-markers]] · [[immutable-raw-layer]] · [[verification-layers]] ·
[[anti-slopification]] · [[confidence-and-contested-markers]]
