---
title: Human-in-the-loop review gate
created: 2026-09-28
updated: 2026-09-28
type: concept
tags: [review, trust, verification, knowledge-management, agent]
sources:
  - raw/articles/llm-wiki-review-skill.md
  - raw/articles/llm-wiki-review-qualification-report.md
  - raw/articles/llm-wiki-review-companion-guide.md
  - raw/articles/karpathy-llm-wiki-gist.md
summary: A mandatory stop between synthesis and the compiled wiki — the agent proposes in markdown, a human approves, and nothing is written until they do.
confidence: high
---

# Human-in-the-loop review gate

## Definition

A control point at which an agent that has synthesized a wiki change **stops and waits for
an explicit human decision** before creating or modifying any compiled page. The proposal is
a markdown file the human can read, edit, and version — not a modal in a UI and not a
silent write.

The motivation, in the companion guide's words: let AI organize knowledge without silently
turning every plausible synthesis into permanent truth. Raw evidence remains inspectable,
the human controls promotion, and the wiki becomes a deliberately curated library of truth.
^[raw/articles/llm-wiki-review-companion-guide.md] See [[anti-slopification]].

The idea is latent in the original pattern — [[andrej-karpathy]] describes business/team
wikis "possibly with humans in the loop reviewing updates," and says he prefers to ingest
one source at a time while staying involved ^[raw/articles/karpathy-llm-wiki-gist.md] — but
the gate makes it structural rather than a matter of personal style.

## Why a gate and not just careful prompting

[[llm-wiki-skill]] already tells the agent to handle contradictions explicitly, never
silently overwrite, and ask before touching 10+ pages. Those are good instructions and they
are *soft*: they describe what a well-behaved run does, and they bind nothing. The gate
changes the default so that **the compiled layer cannot be written without a decision**,
which converts "the agent usually asks" into "the agent must stop."

The cost is real and should be stated plainly: every material change now needs a human turn.
For a personal research wiki ingesting a few sources a week, that is a feature. For
unattended cron ingest of hundreds of sources, it is a bottleneck — which is the trade-off
in [[review-companion-vs-agentic-librarian]].

## Mechanics

**Proposal.** One file per target, `review/YYYY-MM-DD-<target-stem>-proposal.md`, with
frontmatter binding it to a target, a revision, an operation (`create` / `update` /
`conflict-resolution`), and its sources. Body sections: *What will change* · *Proposed
content* (the exact bytes that would be written) · *Evidence and uncertainty* · *Human
feedback*. ^[raw/articles/llm-wiki-review-skill.md]

**Decisions.** Five canonical values, no others: `pending`, `approve`, `reject`, `revise`,
`defer`. Ordinary proposals offer approve / reject / revise / defer.
^[raw/articles/llm-wiki-review-skill.md]

**Effects.** Approve → apply the exact reviewed content, set `status: applied`, then run
built-in maintenance (links, index, log, lint). Reject → target unchanged, `status:
rejected`. Revise → new proposal, `revision` incremented, `decision: pending`, stop again.
Defer → target unchanged, `status: deferred`. Rejection and deferral must change **only**
proposal state. ^[raw/articles/llm-wiki-review-skill.md]

**Silence is never approval.** "Silence and elapsed time are not approval." A proposal left
`pending` for a year is still pending. ^[raw/articles/llm-wiki-review-skill.md]

**Editing the note is not enough.** You may write your choice under *Human feedback* or
change the `decision` property in [[obsidian]], but that alone does not trigger the agent —
you must then say *"Continue the pending Wiki review."*
^[raw/articles/llm-wiki-review-companion-guide.md] The guide's own release checklist flags
this as a usability risk: "Confirm the second explicit 'continue' step is obvious."
^[raw/articles/llm-wiki-review-qualification-report.md]

## Revision binding — the part that actually matters

The gate's integrity depends on approving *a specific version of a specific change*:

- Revalidate the reviewed content before any write. If it is structurally invalid, do not
  apply it — create a corrected revision and request review again.
- **Never apply an approval to a different revision from the one the human reviewed.**
- If the target, source, schema, path, or revision has changed, stop or create a new pending
  revision.
- Before applying, reread the named proposal and revision, validate the proposed schema,
  check source traceability, look for **target drift**, and confirm the target remains
  inside the wiki root.

^[raw/articles/llm-wiki-review-skill.md] ^[raw/articles/llm-wiki-review-companion-guide.md]

The qualification matrix tested exactly these failure modes: a later human edit forced
revision 2 with no compiled overwrite; approval for revision 1 was refused when revision 2
was current; a raw-source hash mismatch stopped approval with a **zero-byte workspace
delta**; a target path escape produced no outside write; and with two pending proposals, an
ambiguous approval stopped and listed both candidates instead of guessing.
^[raw/articles/llm-wiki-review-qualification-report.md]

"Zero-byte workspace delta" is the right success criterion for a refusal. A gate that
declines but still writes something has failed.

## Contradictions get different choices

When the change resolves a contradiction, competing claims are shown **before** details, and
the default proposal preserves both as `contested`. The three primary choices are:

- **Keep both** — preserve both claims, mark the topic contested. Approve this proposal.
- **Not a contradiction** — create a new context-aware proposal without the contested
  marker, then ask again.
- **Decide later** — make no compiled change.

Preferring one source or requesting a custom resolution stays available as an *advanced*
revision and "should include a reason or stronger evidence". Never silently select a winner.
^[raw/articles/llm-wiki-review-companion-guide.md] ^[raw/articles/llm-wiki-review-skill.md]

This is the most interesting design choice in the gate. Ordinary review asks "is this
right?"; contradiction review asks "should this even be one claim?" — and defaults to
*keeping the disagreement visible* rather than resolving it. See
[[confidence-and-contested-markers]].

## What it is not

> "This skill is an instruction-based review convention, not a deterministic security
> boundary. Its reliability depends on the model following the skill. Keep Git or another
> backup enabled." ^[raw/articles/llm-wiki-review-companion-guide.md]

So the gate is layer 2 of [[three-layer-wiki-architecture]], and it needs layer 3
([[verification-layers]]) plus version control behind it. It also must never run alongside
another review authority on the same change. ^[raw/articles/llm-wiki-review-skill.md]

Practical consequence: **invoke the review skill first.** Running `/llm-wiki` directly can
bypass the gate. ^[raw/articles/llm-wiki-review-companion-guide.md]

## Related

[[llm-wiki-review-skill]] · [[anti-slopification]] · [[verification-layers]] ·
[[review-companion-vs-agentic-librarian]] · [[four-ways-to-own-wiki-writes]] ·
[[confidence-and-contested-markers]]
