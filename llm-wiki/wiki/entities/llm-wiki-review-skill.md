---
title: llm-wiki-review (Review Companion skill)
created: 2026-09-28
updated: 2026-09-28
type: entity
tags: [agent, tooling, review, trust, knowledge-management]
sources:
  - raw/articles/llm-wiki-review-skill.md
  - raw/articles/llm-wiki-review-companion-guide.md
  - raw/articles/llm-wiki-review-qualification-report.md
summary: User-installed skill that wraps Hermes' built-in llm-wiki workflow and intercepts the final decision to create or change compiled Wiki pages.
confidence: high
---

# llm-wiki-review (Review Companion skill)

## Overview

A lightweight human-in-the-loop wrapper around [[llm-wiki-skill]]. It preserves the
built-in workflow and intercepts **only** the final decision to create or change compiled
wiki pages. ^[raw/articles/llm-wiki-review-skill.md]

Its stated purpose is [[anti-slopification]]: let AI organize knowledge without silently
turning every plausible synthesis into permanent truth. Raw evidence stays inspectable, the
human controls promotion, and the wiki becomes a deliberately curated library of truth.
^[raw/articles/llm-wiki-review-companion-guide.md]

## Frozen artifact

| Property | Value |
| --- | --- |
| Raw capture | `raw/articles/llm-wiki-review-skill.md` |
| Body SHA-256 | `d9c037639f7ef703427ef32cbd8eb3b1018ac1974a5c953a9a9f2f901459dc2c` |
| Size | 5,803 bytes |
| Matches qualification report | Yes — recomputed 2026-09-28 |

The digest above was recomputed from the supplied file and matches the value frozen in
`raw/articles/llm-wiki-review-qualification-report.md`. So the tested artifact and the
installed artifact are the same bytes. See [[immutable-raw-layer]].

## Authority boundary

The skill is careful about what it owns:

- It **loads** `llm-wiki` explicitly (`skill_view(name='llm-wiki')`) and lets it orient,
  capture raw, search existing pages, synthesize, preserve provenance, surface
  contradictions, and run post-write maintenance.
- It **owns** the review decision for the current invocation, and does not allow the
  built-in skill to write compiled pages before approval.
- It **does not modify** the installed `llm-wiki` skill.
- If a deterministic Agentic Librarian (e.g. `scripts/librarian_tool.py`) already owns
  review and apply, it **stops**. Never two review authorities on one change. See
  [[review-companion-vs-agentic-librarian]].

^[raw/articles/llm-wiki-review-skill.md]

## The four-step workflow

1. **Prepare.** Resolve `WIKI_PATH` (or ask). Confirm source and wiki root exist inside the
   intended workspace — if either is missing or ambiguous, stop without searching other
   workspaces. Load `llm-wiki` and follow its normal steps. Allow immutable raw capture;
   stop before creating or changing any compiled entity, concept, comparison, query, index,
   or log entry.
2. **Propose.** One Markdown proposal per target at `review/YYYY-MM-DD-<target>-proposal.md`
   with `type`, `status`, `decision`, `revision`, `operation`, `target`, `sources`.
   Sections: *What will change* · *Proposed content* · *Evidence and uncertainty* ·
   *Human feedback*. Validate the proposed content against `SCHEMA.md` **before** showing it
   — never ask a human to approve structurally invalid content.
3. **Stop.** Report proposal path, target, operation, main uncertainty. Ask for `approve`,
   `reject`, `revise`, or `defer`. Silence and elapsed time are not approval.
4. **Resume safely.** Reread the proposal and its current revision. Revalidate before any
   write. Apply the *exact* reviewed content on approve; leave the target untouched on
   reject or defer; increment `revision` and reset `decision: pending` on revise. **Never
   apply an approval to a different revision than the one reviewed.**

^[raw/articles/llm-wiki-review-skill.md]

## Raw capture rule it adds

Hash the exact source body **before** adding frontmatter. Store one blank separator after
the closing `---`, then the unchanged body. Immediately recompute the hash by removing the
frontmatter and that one separator; correct the metadata if it does not match.
^[raw/articles/llm-wiki-review-skill.md]

`tools/wiki_tool.py capture` implements this deterministically so the check cannot be
forgotten. See [[verification-layers]].

## Contradiction handling

For a possible contradiction, competing claims are shown **before** details, and the
proposal defaults to preserving both as `contested`. The generic *Human feedback* line is
replaced by exactly three primary choices, repeated in the response:

- **Keep both** — approve this proposal.
- **Not a contradiction** — revise to preserve compatible or context-dependent claims
  without `contested`, then stop for approval again.
- **Decide later** — defer without changing compiled content.

Source preference and custom resolutions live under `Advanced: revise` and require a reason
or stronger evidence. Never silently select a winner.
^[raw/articles/llm-wiki-review-skill.md]

## Qualification status

The frozen artifact passed a 14-case automated release matrix (reject, defer, stale target,
obsolete revision, raw source drift, invalid schema, missing wiki root, source outside
workspace, target path escape, multiple pending proposals, exact proposal binding, and three
interruption/recovery cases) across 110 model API calls in sealed workspaces with synthetic
sources, using `gpt-5.6-terra` at medium reasoning on the OpenAI Codex provider.
^[raw/articles/llm-wiki-review-qualification-report.md]

That qualifies **one** Hermes/model/artifact combination as a *limited beta review
convention*. It explicitly does not qualify arbitrary providers, weak local models,
concurrent writers, symlink attacks, live Obsidian usability, or clean member installation.
Four human release checks remain outstanding. See [[verification-layers]] and
[[review-companion-vs-agentic-librarian]].

## Related

[[llm-wiki-skill]] · [[human-in-the-loop-review-gate]] · [[anti-slopification]] ·
[[hermes-agent]] · [[verification-layers]]
