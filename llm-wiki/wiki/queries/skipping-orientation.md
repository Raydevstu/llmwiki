---
title: "Query: What actually breaks when an agent skips orientation?"
created: 2026-09-28
updated: 2026-09-28
type: query
tags: [workflow, knowledge-management, verification, agent]
sources:
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/karpathy-llm-wiki-gist.md
  - raw/articles/llm-wiki-review-qualification-report.md
summary: Filed answer — the four named failure modes of skipping the SCHEMA/index/log read, why they compound, and what to do about it mechanically.
confidence: high
---

# Query: What actually breaks when an agent skips orientation?

> Filed because the failure modes are spread across three sources and the mechanical
> mitigations are not stated anywhere upstream. Question asked during vault construction.

## The requirement

[[llm-wiki-skill]] calls this step **CRITICAL — do this every session**. When a wiki exists,
orient before anything else: ① read `SCHEMA.md` for domain, conventions, and tag taxonomy;
② read `index.md` for what pages exist and their summaries; ③ scan the last 20–30 `log.md`
entries for recent activity. Only then ingest, query, or lint. For wikis past 100 pages, also
search the vault for the topic at hand. ^[raw/articles/hermes-agent-llm-wiki-skill.md]

## The four named failure modes

Upstream lists exactly what skipping orientation prevents:

| Failure | Mechanism | Observable symptom |
| --- | --- | --- |
| **Duplicate pages** | The agent does not know an entity page already exists, so it creates a second one under a slightly different name | Two pages on one subject; both half-complete; split inbound links |
| **Missed cross-references** | The agent does not know which related pages exist, so the new page links to nothing or to the wrong things | Orphans; pages below the ≥2-link minimum; a graph that stops connecting |
| **Schema violations** | The agent does not know the tag taxonomy or the conventions | Tags outside the taxonomy; missing frontmatter fields; path-style wikilinks |
| **Repeated work** | The agent does not read the log, so it re-ingests or re-lints | Duplicate log entries; the same source processed twice; churn with no net change |

^[raw/articles/hermes-agent-llm-wiki-skill.md]

## Why they compound rather than merely accumulate

Each failure makes orientation *harder* next time, which is what turns a shortcut into decay:

- A duplicate page splits the evidence for one entity across two files. The next agent reads
  one, sees fewer sources, and concludes the topic is thin — so it does not update it, or it
  creates a third page.
- Missed cross-references reduce inbound links, so lint reports orphans, so the next agent
  spends its turn on link repair instead of content.
- Schema drift makes the taxonomy meaningless. Once freeform tags exist, "add the tag to
  SCHEMA.md first" stops being enforceable, and tags decay into noise — the exact outcome the
  taxonomy rule exists to prevent.
- A log with duplicate entries stops being a reliable record of what has been done, so the
  next agent cannot trust it, so it re-does work anyway.

Karpathy's framing of `index.md` explains why this is load-bearing rather than bureaucratic:
the agent "reads the index first to find relevant pages, then drills into them", and that
approach "works surprisingly well at moderate scale… and avoids the need for embedding-based
RAG infrastructure." ^[raw/articles/karpathy-llm-wiki-gist.md] The index *is* the retrieval
layer. An agent that skips it is not saving a step; it is discarding the only search
mechanism the design has.

## The same failure shape in the review gate

The review skill has a directly analogous requirement, and the qualification report shows
what happens when it is honored: on resume, the agent must **reread the proposal and its
current revision before acting**, revalidate content, and inspect current state before
completing missing work. ^[raw/articles/llm-wiki-review-skill.md]

Three of the fourteen tested cases are interruption/recovery scenarios — target-first
interruption, approval-state-first interruption, and a repeated already-completed request.
All passed, and the reported outcomes are the interesting part: an existing reviewed target
"was not rewritten; missing status/index/log work completed once", and a second approval
attempt "produced a zero-byte delta and no duplicate log."
^[raw/articles/llm-wiki-review-qualification-report.md]

That is orientation under a different name: **read current state before acting, and make the
no-op case a genuine no-op.** An agent that skips it re-applies an approval, rewrites a
reviewed target, or logs the same action twice.

## What can be enforced mechanically

Orientation itself cannot be — you cannot force a model to read. But every one of its
failure modes leaves a detectable trace, which is what `tools/wiki_tool.py lint` checks:

| Failure mode | Mechanical check |
| --- | --- |
| Duplicate pages | Non-unique stems are impossible (one file per stem); orphans and low-outbound-link pages are flagged, which surfaces near-duplicates for a human |
| Missed cross-references | `< 2` resolvable outbound wikilinks is a hard error; orphans are warnings |
| Schema violations | Required frontmatter, page `type`, date format, tag-in-taxonomy, bare-stem links, resolvable provenance markers, `raw/` source presence — all errors |
| Repeated work | Malformed or unknown-action log entries are errors; `index.md` completeness and the `Total pages` count are checked, so a half-finished run is visible |

The cheap operational version of orientation is `wiki_tool.py orient`, which prints
`SCHEMA.md`, `index.md`, the last 30 log entries, and the pending review queue in one call.
It does not make the agent read it — but it removes every excuse except unwillingness, and it
turns a three-step instruction into one command that is easy to put at the top of a session.

## Practical recommendation

1. Run `orient` at the start of every session, before any ingest or query.
2. Past 100 pages, also search the vault for the topic — the index alone starts to miss.
   ^[raw/articles/hermes-agent-llm-wiki-skill.md]
3. After any interruption, re-run `orient` rather than resuming from memory of what you did.
4. Lint on a schedule, and treat a new orphan or taxonomy violation as evidence that some run
   skipped orientation — not as an isolated style nit.

## Drew on

[[llm-wiki-skill]] · [[three-layer-wiki-architecture]] · [[markdown-as-knowledge-substrate]] ·
[[verification-layers]] · [[human-in-the-loop-review-gate]]
