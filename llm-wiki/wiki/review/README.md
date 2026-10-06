# Review queue

This directory is **layer 2** of the [[three-layer-wiki-architecture]]: the point where a
synthesized change stops and waits for a human. Nothing here is the wiki. Nothing in here
has been trusted yet. See [[human-in-the-loop-review-gate]] for why the gate exists and
[[anti-slopification]] for what it is defending against.

## What a proposal is

One markdown file per target, named `review/YYYY-MM-DD-<target-stem>-proposal.md`:

```yaml
---
type: llm-wiki-review
status: needs-review | applied | rejected | deferred
decision: pending | approve | reject | revise | defer
revision: 1
operation: create | update | conflict-resolution
target: concepts/example.md
sources:
  - raw/articles/example-source.md
---
```

Body sections: **What will change** · **Proposed content** (the exact bytes that would be
written, inside a fenced block) · **Evidence and uncertainty** · **Human feedback**.

Only those five `decision` values are valid. Rejection and deferral change **proposal state
only** — never the target.

## How to answer one

**In conversation** — reply with `approve`, `reject`, `revise`, or `defer` and any feedback.
Simplest path.

**In [[obsidian]]** — write your choice under *Human feedback*, or change the `decision`
property in the frontmatter, then tell the agent:

```text
Continue the pending Wiki review.
```

Editing the note alone does **not** trigger anything. The agent has to be told to resume.
**Silence and elapsed time are never approval** — a proposal left `pending` for a year is
still pending.

**From the CLI**, deterministically:

```bash
python3 tools/wiki_tool.py pending                                    # what is waiting
python3 tools/wiki_tool.py apply 2026-09-28-foo-proposal.md --decision approve --revision 1
python3 tools/wiki_tool.py apply 2026-09-28-foo-proposal.md --decision defer --feedback "revisit after the Q4 sources land"
```

`apply` refuses to write unless the proposal's revision matches, the target has not drifted
since review, every cited raw capture still hash-verifies, and the proposed content still
validates against `SCHEMA.md`. See [[verification-layers]].

## Contradiction proposals are different

When `operation: conflict-resolution`, the three primary choices replace the generic
feedback line:

- **Keep both** — approve; both claims are preserved and the topic is marked `contested`.
- **Not a contradiction** — revise into context-dependent claims without `contested`, then
  stop for approval again.
- **Decide later** — defer; no compiled change.

Preferring a source or supplying a custom resolution is an *advanced* revision and requires a
reason or stronger evidence. Never silently select a winner.
^[raw/articles/llm-wiki-review-skill.md]

`review/2026-09-28-index-first-navigation-proposal.md` in this vault is a live example,
deliberately left `pending`.

## Current queue

Run `python3 tools/wiki_tool.py pending` for the authoritative list — this section is a
snapshot from vault construction on 2026-09-28 and will go stale.

| Proposal | Operation | Target | Decision |
| --- | --- | --- | --- |
| `2026-09-28-index-first-navigation-proposal.md` | conflict-resolution | `concepts/index-first-navigation.md` | **pending** — awaiting a human |
| `2026-09-28-llm-wiki-vs-rag-proposal.md` | create | `concepts/llm-wiki-vs-rag.md` | approve / applied |

## Limits

The gate is an instruction-based convention, not a deterministic security boundary; its
reliability depends on the model following the skill. Keep Git enabled, and use the full
Agentic Librarian when you need transactions, receipts, concurrency safety, or unattended
automation. ^[raw/articles/llm-wiki-review-companion-guide.md] See
[[review-companion-vs-agentic-librarian]].

## Related

[[human-in-the-loop-review-gate]] · [[llm-wiki-review-skill]] · [[verification-layers]] ·
[[anti-slopification]] · [[four-ways-to-own-wiki-writes]]
