---
title: Confidence and contested markers
created: 2026-09-28
updated: 2026-09-28
type: concept
tags: [trust, verification, knowledge-management, controversy]
sources:
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/llm-wiki-review-skill.md
  - raw/articles/awesome-llm-wiki-readme.md
summary: Frontmatter signals — confidence, contested, contradictions — that keep weak or disputed claims visibly weak instead of hardening into wiki fact.
confidence: high
---

# Confidence and contested markers

## Definition

Three optional frontmatter fields that record how much weight a page's claims can bear:

```yaml
confidence: high | medium | low     # how well-supported the claims are
contested: true                     # set when the page has unresolved contradictions
contradictions: [other-page-stem]   # pages this one conflicts with
```

Upstream's rationale, in full: "`confidence` and `contested` are optional but recommended
for opinion-heavy or fast-moving topics. Lint surfaces `contested: true` and
`confidence: low` pages for review so weak claims don't silently harden into accepted wiki
fact." ^[raw/articles/hermes-agent-llm-wiki-skill.md]

That single sentence is the entire justification. See [[anti-slopification]].

## Calibration rules used in this vault

`confidence` is about **evidential support**, not about how sure the prose sounds.

| Value | Use when |
| --- | --- |
| `high` | Claims are well-supported across multiple captured sources, or the page is essentially a faithful description of one authoritative capture. Upstream: "Don't mark `high` unless the claim is well-supported across multiple sources." |
| `medium` | One source, or several sources of unequal weight, or a page where part of the analysis is the agent's own reasoning. Also used when a needed capture is missing (e.g. [[wanderloots]], metadata-only). |
| `low` | Single weak or second-hand source, fast-moving fact likely already stale, or a page dominated by inference. |

The ingest procedure adds a specific instruction: for opinion-heavy, fast-moving, or
single-source claims, set `medium` or `low`. ^[raw/articles/hermes-agent-llm-wiki-skill.md]

Lint then flags a fourth case, which is the subtle one: **a page that cites only a single
source but has no `confidence` field at all** — a candidate for either finding corroboration
or demoting to `medium`. ^[raw/articles/hermes-agent-llm-wiki-skill.md] Unmarked is not
neutral; it reads as "no concerns", which is a claim the author never made.

## `contested` is a commitment, not a shrug

Setting `contested: true` means the page deliberately holds two claims that cannot both be
right, and no decision has been made. It pairs with
[[human-in-the-loop-review-gate]]'s contradiction flow, whose *default* proposal is to
**keep both** and mark the topic contested rather than resolve it. The alternative choices
are "not a contradiction" (revise into context-dependent claims without the marker) and
"decide later" (defer, no compiled change). Preferring a source is an advanced revision
requiring a reason or stronger evidence — "Never silently select a winner."
^[raw/articles/llm-wiki-review-skill.md]

The update policy behind this is dated, not merely diplomatic: check the dates, newer
sources generally supersede older ones; if genuinely contradictory, note **both positions
with dates and sources**; mark `contradictions: [page-name]`; flag for user review in the
lint report. ^[raw/articles/hermes-agent-llm-wiki-skill.md]

Dates matter because "newer supersedes older" is only valid for factual drift. A 2026 paper
does not refute a 2020 paper's definition; it may just disagree. Recording both with dates
lets a later reader make that judgment instead of inheriting the agent's.

## Why visible weakness beats polished uniformity

A wiki where every page looks equally authoritative is a wiki where the reader cannot
triage. Markers create a **reading order**: `contested` pages first (an unresolved
disagreement may invalidate something you are about to rely on), then `confidence: low`,
then single-source pages, then the rest.

Dataview makes this queryable in [[obsidian]]:

```
TABLE confidence, updated, sources FROM "concepts" WHERE contested OR confidence = "low"
```

## Limits — and the ecosystem's response

Markers are **self-reported by the same process that wrote the claim**. A model that
overstates its certainty in prose will also overstate `confidence`. Nothing in the captured
sources validates marker accuracy against ground truth.

Which is why several independent implementations mechanize the decay rather than trusting the
label: one ships a multi-agent maintenance engine with claim verification, deduplication,
and a **9-tier staleness decay**; another evolves knowledge graphs at test time through
query reflection; a v2 architectural extension of the pattern is explicitly focused on
"memory lifecycles" and "confidence decay". ^[raw/articles/awesome-llm-wiki-readme.md]

The shared assumption is worth naming: **confidence should fall over time unless refreshed,
not stay where it was written.** A `high` set in January is not obviously still `high` in
September. In this vault the cheap version is lint's staleness check — a page whose `updated`
date is more than 90 days older than the most recent source mentioning the same entities gets
flagged — which approximates decay without modeling it.

## Related

[[anti-slopification]] · [[human-in-the-loop-review-gate]] · [[source-traceability]] ·
[[llm-wiki-skill]] · [[verification-layers]]
