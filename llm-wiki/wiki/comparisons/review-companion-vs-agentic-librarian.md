---
title: Review Companion vs Agentic Librarian
created: 2026-09-28
updated: 2026-09-28
type: comparison
tags: [comparison, review, verification, trust, automation]
sources:
  - raw/articles/llm-wiki-review-companion-guide.md
  - raw/articles/llm-wiki-review-skill.md
  - raw/articles/llm-wiki-review-qualification-report.md
summary: Instruction-based review convention versus deterministic tooling with transactions and receipts — when the lightweight gate is enough and when it is not.
confidence: high
---

# Review Companion vs Agentic Librarian

## What is being compared, and why

Both are layer-2/3 answers to the same question — how do you stop an agent from writing
unreviewed synthesis into the compiled wiki — at different weights. The companion guide
frames them as points on one ladder where "each layer is a valid stopping point", and warns
explicitly: **"Do not run this companion and the full Agentic Librarian as simultaneous
review authorities."** ^[raw/articles/llm-wiki-review-companion-guide.md]

The comparison matters because choosing the heavier option costs setup and latency, while
choosing the lighter one costs guarantees. Neither cost is visible until you hit it.

## Dimensions

| Dimension | Review Companion (`llm-wiki-review`) | Agentic Librarian Core |
| --- | --- | --- |
| **Nature** | Instruction-based review convention | Deterministic tools that enforce state |
| **Enforcement** | Depends on the model following the skill | Mechanically enforced paths, schemas, hashes, revisions |
| **Transactions / rollback** | No — relies on Git and on refusals producing zero deltas | Yes |
| **Receipts** | No durable receipts | Durable receipts |
| **Replay / recovery safety** | By re-inspection: reread proposal + revision, complete missing work | Guaranteed by design |
| **Stale-state checks** | Requested ("look for target drift") | Enforced |
| **Concurrency** | Not qualified — explicitly excluded from the test scope | Multiple agents supported |
| **Automation / unattended runs** | Poor fit: a gate that needs a human blocks cron | Designed for it |
| **Large review queues** | Manual, one proposal at a time | Queue-oriented |
| **Automatic Markdown processing** | No | Yes |
| **Browser Rail controls** | No | Yes |
| **Memory projection** | No | Yes (layer 4) |
| **Install cost** | One skill folder + `WIKI_PATH` | A core to deploy and operate |
| **Latency per change** | One human turn | Depends on queue policy |
| **Failure mode** | Agent proceeds without stopping | Operational complexity; over-engineering |

Sources: ^[raw/articles/llm-wiki-review-companion-guide.md] ^[raw/articles/llm-wiki-review-skill.md]
^[raw/articles/llm-wiki-review-qualification-report.md]

## When the Companion is the right choice

The guide's own decision table: choose it when "you want to approve material changes before
they become trusted" — built-in `llm-wiki` plus `llm-wiki-review`, where markdown proposals
wait for a human. ^[raw/articles/llm-wiki-review-companion-guide.md]

Concretely, it fits when: a single human curates a single vault; ingest is interactive
rather than scheduled; the volume is a few sources a week, not a few hundred a day; and you
want the review artifact to be a file you can read and edit in [[obsidian]] rather than a
queue in a service. The guide calls it "the lightweight human-in-the-loop option".

It is also the correct **starting** point. Adding the Core later is additive; removing
accrued unreviewed writes is not.

## When you need the Librarian

The guide lists the triggers: "unattended automation, multiple agents, large review queues,
browser Rail controls, memory projection, durable receipts, or deterministic guarantees."
^[raw/articles/llm-wiki-review-companion-guide.md] The skill's version: "when hashes,
receipts, replay safety, automation, or mechanically enforced policies are required."
^[raw/articles/llm-wiki-review-skill.md]

The sharpest signal is in the qualification report's exclusions. It does **not** qualify
"concurrent writers, symlink attacks" or turn "prompt instructions into deterministic
enforcement." ^[raw/articles/llm-wiki-review-qualification-report.md] So: the moment a
second agent can write the same vault, or the moment an attacker-controlled file could be
in the path, the Companion is out of its tested envelope — and the skill knows it, refusing
to run at all if `scripts/librarian_tool.py` already owns review and apply.
^[raw/articles/llm-wiki-review-skill.md]

## The middle position this vault takes

Neither pure option. The vault runs the Companion as the review convention and adds
`tools/wiki_tool.py` as a small deterministic core covering the properties that can be
checked without judgment: raw hashes, frontmatter schema, tag taxonomy, wikilink resolution,
path containment, provenance-marker resolution, proposal state consistency, revision
binding, target drift, and index/log integrity. See [[verification-layers]] for the exact
enforced-vs-requested table.

That buys most of the Librarian's *verification* value at a fraction of its operational
cost, and it does **not** buy transactions, receipts, concurrency safety, or automation.
Those remain the real reasons to move up.

The trade-off to state plainly: a partial core can create false confidence. Because `apply`
refuses a stale revision, it is tempting to assume the vault is safe — but an agent can
still write the target file directly and never call `apply`. Git is the backstop, not the
tool.

## Verdict

For this vault — one human, interactive ingest, ~30 pages — the Companion plus the
verification tool is proportionate, and the Core would be over-engineering.

Revisit when any of these becomes true: ingest moves to cron; a second agent gets write
access; the pending-proposal queue regularly exceeds what one human reviews in a sitting; or
you need an auditable receipt that a specific change was approved by a specific person at a
specific time.

## Related

[[human-in-the-loop-review-gate]] · [[verification-layers]] · [[llm-wiki-review-skill]] ·
[[three-layer-wiki-architecture]] · [[anti-slopification]]
