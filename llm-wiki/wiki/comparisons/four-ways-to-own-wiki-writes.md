---
title: Four ways to own wiki writes
created: 2026-09-28
updated: 2026-09-28
type: comparison
tags: [comparison, review, trust, automation, verification]
sources:
  - raw/articles/llm-wiki-review-companion-guide.md
  - raw/articles/llm-wiki-review-qualification-report.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/karpathy-llm-wiki-gist.md
summary: Direct write, soft guardrail, review gate, deterministic core — the four write policies available to a compiled wiki and what each costs.
confidence: high
---

# Four ways to own wiki writes

## What is being compared, and why

Every compiled wiki has a **write policy**: what has to be true before a synthesized claim
becomes a page. The companion guide's decision table describes four, and presents them as
escalating options where "each layer is a valid stopping point."
^[raw/articles/llm-wiki-review-companion-guide.md] This page lays them side by side, because
the choice is usually made implicitly, by whatever skill happens to be installed.

## Dimensions

| | **1. Direct write** | **2. Soft guardrail** | **3. Review gate** | **4. Deterministic core** |
| --- | --- | --- | --- | --- |
| What it is | Built-in `llm-wiki` alone | Same skill, plus its own caution rules | Add `llm-wiki-review`; proposals wait for a human | Agentic Librarian: enforced state, transactions, receipts |
| Who decides a claim enters | The model | The model, nudged | A human, explicitly | A human via an enforced queue |
| Blocking? | No | No | Yes — one human turn per material change | Yes, with queue policy |
| Enforced by | Nothing | Prompt instructions | Prompt instructions + `wiki_tool.py` checks | Code outside the model |
| Unattended ingest | Fine | Fine | Blocks | Fine |
| Concurrent writers | Tolerated | Risky | Not qualified | Supported |
| Auditability | `log.md` | `log.md` | Proposal files + log + Git | Receipts + transactions + Git |
| Recovery after interruption | Rerun | Rerun | Reread proposal + revision, complete missing work | Guaranteed replay safety |
| Setup cost | None | None | One skill folder | A core to operate |
| Failure mode | Silent slop compounds | Guardrail not followed | Reviewer rubber-stamps | Over-engineering; complexity |
| Best for | Personal exploration, disposable wikis | Low-stakes domains | Curated knowledge you rely on | Teams, automation, scale |

Sources: ^[raw/articles/llm-wiki-review-companion-guide.md] ^[raw/articles/hermes-agent-llm-wiki-skill.md]

## Why option 2 is weaker than it looks

The built-in skill is not naive. It already says: handle contradictions explicitly, never
silently overwrite, mark `contradictions:` in frontmatter, flag for user review in lint,
and **"Ask before mass-updating — if an ingest would touch 10+ existing pages, confirm the
scope with the user first."** ^[raw/articles/hermes-agent-llm-wiki-skill.md]

Those are good rules and they are *conditional on compliance*. "Ask before mass-updating"
binds a model that asks; it does not bind a model that does not. The difference between
options 2 and 3 is therefore not the quality of the instructions but the **default**: under
2, writing is the default and asking is the exception; under 3, stopping is the default and
writing requires a decision. Defaults survive a bad day; exceptions do not.

Karpathy's own workflow sits between the two — he prefers "to ingest sources one at a time
and stay involved", reading summaries and guiding emphasis ^[raw/articles/karpathy-llm-wiki-gist.md]
— which is a review gate implemented as personal habit rather than as procedure. Habit does
not transfer to a cron job or to another user.

## Why option 3 is weaker than it looks

The gate is a convention. Its own documentation is the clearest source on this: "an
instruction-based review convention, not a deterministic security boundary. Its reliability
depends on the model following the skill." ^[raw/articles/llm-wiki-review-companion-guide.md]

And it has a human-side failure mode that no amount of tooling fixes: **approval fatigue**.
Forty proposals approved in a row without reading is a rubber stamp with an audit trail, and
the audit trail makes it look *more* trustworthy than option 1, not less. The qualification
report's outstanding release checks are aimed at exactly this — confirm a beginner
understands the proposal and the three contradiction choices in Obsidian, and confirm the
second explicit "continue" step is obvious. ^[raw/articles/llm-wiki-review-qualification-report.md]

Batching proposals, raising the materiality bar, and reviewing on a schedule rather than
per-change all reduce fatigue. None of them are in the captured sources as tested practice;
they are inferences. See [[anti-slopification]].

## Verdict for this vault

**Option 3, with option 4's cheap parts bolted on.** The vault installs the review skill and
adds `tools/wiki_tool.py` for hash, schema, path-containment, and revision-binding checks —
which is verification without the operational cost of a full core. Git supplies the audit
trail and the recovery path. See [[review-companion-vs-agentic-librarian]] for when that
stops being enough, and [[verification-layers]] for the enforced-versus-requested table.

The one policy choice worth making deliberately: **what counts as a material change.** If
every typo fix needs approval, fatigue arrives fast and the gate gets bypassed. If only new
pages need approval, updates to existing claims go unreviewed — which is where slop actually
accumulates. This vault currently gates everything, which is right at 30 pages and wrong at
300.

## Related

[[human-in-the-loop-review-gate]] · [[review-companion-vs-agentic-librarian]] ·
[[verification-layers]] · [[anti-slopification]] · [[llm-wiki-skill]]
