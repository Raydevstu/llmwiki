---
title: Verification layers
created: 2026-09-28
updated: 2026-09-28
type: concept
tags: [verification, trust, automation, tooling]
sources:
  - raw/articles/llm-wiki-review-companion-guide.md
  - raw/articles/llm-wiki-review-skill.md
  - raw/articles/llm-wiki-review-qualification-report.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
summary: What is enforced by code versus requested of a model — the boundary between a review convention and a deterministic core, and where this vault actually sits.
confidence: high
---

# Verification layers

## The problem in one sentence

A prompt is a request, not a control: an instruction-based review convention is only as
reliable as the model's willingness to follow it. The companion guide says so about itself —
"not a deterministic security boundary… Keep Git or another backup enabled" — and points to
the full Agentic Librarian "when you require mechanically enforced hashes, stale-state
checks, transactions, receipts, automation, or automatic Markdown processing."
^[raw/articles/llm-wiki-review-companion-guide.md]

So the useful question is never "is the wiki verified?" but "**which properties are verified
by code, and which are merely requested of a model?**"

## The split

| Property | Enforced by `tools/wiki_tool.py` | Requested of the model |
| --- | --- | --- |
| Raw body hash matches stored hash | ✅ `verify`, `lint` | — |
| Capture hashes verified immediately after write | ✅ `capture` re-reads from disk | — |
| Required frontmatter present on compiled pages | ✅ `lint` | — |
| Tags inside the SCHEMA.md taxonomy | ✅ `lint` (parses the taxonomy section) | — |
| Wikilinks resolve; ≥2 outbound per page | ✅ `lint` | — |
| Provenance markers resolve to real files | ✅ `lint` | — |
| Every compiled page cites ≥1 `raw/` source | ✅ `lint` | — |
| Paths cannot escape the vault (traversal, absolute, symlink) | ✅ `safe_join` on every write path | — |
| Proposal binds to an exact target + revision | ✅ `apply --revision` refuses mismatch | — |
| Target drift since review | ✅ `apply` compares recorded hash | — |
| Proposed content revalidated before write | ✅ `apply` | — |
| Cited raw source still hash-verifies at apply time | ✅ `apply` refuses on drift | — |
| `index.md` complete and consistent | ✅ `reindex`, `lint` | — |
| `log.md` entry format and rotation threshold | ✅ `lint` | — |
| Two pending proposals on one target = ambiguous | ✅ `lint` error | — |
| **The agent stops before writing** | ❌ | ✅ skill instruction |
| **A human actually reads the proposal** | ❌ | ✅ |
| **A paragraph means what its marker implies** | ❌ | ✅ human / verification agent |
| **Silence is not treated as approval** | ⚠️ `apply` refuses `pending` | ✅ skill instruction |
| **Contradiction resolved fairly** | ❌ | ✅ |
| **Page threshold judgments (create vs update)** | ❌ | ✅ |

⚠️ means partial: the tool will not apply a `pending` decision, but nothing stops an agent
from editing the target file directly instead of calling `apply`.

## Why "stops before writing" cannot be enforced from inside

This is the honest limit. Any gate implemented as instructions lives in the same process
that holds the write permission. A model with file-write access can always write the file.
Enforcement therefore has to come from **outside the model**:

- **Git.** Commit before ingest; `git status` afterwards shows exactly what changed. A
  refusal that produced a byte delta is detectable, which is why the qualification matrix's
  success criterion is "zero-byte workspace delta". ^[raw/articles/llm-wiki-review-qualification-report.md]
- **Filesystem permissions.** Make `raw/` read-only for the agent user. Cheap and real.
- **A separate apply process.** `wiki_tool.py apply` is the only thing that should write a
  compiled page during a reviewed run — but that is a convention unless the agent lacks
  write access.
- **A deterministic core.** The Agentic Librarian layer: transactions, receipts, replay
  safety, stale-state checks. See [[review-companion-vs-agentic-librarian]].

## What the qualification report actually proved

Fourteen cases across 110 model API calls in sealed temporary workspaces with synthetic
sources, on `gpt-5.6-terra` (medium reasoning, OpenAI Codex provider), against frozen
artifact hashes. Every case passed, and the verification pattern is consistent: the *outcome*
is mechanical even though the *gate* is not. Raw source drift "stopped approval with a
zero-byte workspace delta"; a target path escape meant "no outside write occurred"; an
obsolete revision meant "approval for revision 1 was refused when revision 2 was current".
^[raw/articles/llm-wiki-review-qualification-report.md]

Its own scope limits are unusually blunt, and worth quoting because they define what has
*not* been verified: this "does not turn prompt instructions into deterministic enforcement
and does not qualify arbitrary providers, weak local models, concurrent writers, symlink
attacks, live Obsidian usability, or clean member installation."
^[raw/articles/llm-wiki-review-qualification-report.md]

Note what that list is: precisely the things an outside-the-model control would cover.
Concurrent writers and symlink attacks are filesystem concerns. Weak local models are a
compliance concern. Installation is a human-factors concern.

## This vault's position

Layer 1 (intelligence): [[llm-wiki-skill]], upstream, unmodified.
Layer 2 (trust): [[llm-wiki-review-skill]] + `wiki/review/`.
Layer 3 (verification): `tools/wiki_tool.py` — the ✅ column above.
Layer 4 (power): **not installed.**

Plus two controls from outside the model that cost nothing: initialize Git in the vault
(commit before each ingest, diff after), and optionally `chmod -R a-w wiki/raw` so raw
captures are immutable at the filesystem level, not just by convention. See
[[three-layer-wiki-architecture]] and `docs/SETUP.md` §6.

## Related

[[human-in-the-loop-review-gate]] · [[immutable-raw-layer]] · [[source-traceability]] ·
[[review-companion-vs-agentic-librarian]] · [[anti-slopification]]
