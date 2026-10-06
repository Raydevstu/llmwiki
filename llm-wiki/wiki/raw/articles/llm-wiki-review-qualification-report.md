---
source_url: local-upload:QUALIFICATION.md
ingested: 2026-09-28
sha256: 8345e19da901ed4fcdce6534895dc32b50614c58bed9f2460b8638cd31a2e8e8
capture_note: Local file supplied by the user as `QUALIFICATION.md`; body stored verbatim.
---

---
title: LLM Wiki Review Companion Qualification - 2026-08-11
created: 2026-08-11
updated: 2026-08-11
type: test-report
tags:
  - llm-wiki
  - hermes
  - testing
---

# LLM Wiki Review Companion Qualification

## Frozen artifacts

- `llm-wiki-review` SHA-256: `d9c037639f7ef703427ef32cbd8eb3b1018ac1974a5c953a9a9f2f901459dc2c`
- Hermes built-in `llm-wiki` SHA-256: `0229e37c1783fcac5b77cfb3242703666cf4aa472d2ae85b6bd5279756b515b6`
- Model: `gpt-5.6-terra`, medium reasoning, OpenAI Codex provider
- Environment: sealed temporary local workspaces with synthetic sources

## Results

| Capability | Result | Verified outcome |
|---|---|---|
| Reject | Pass | Only proposal state changed; all other bytes remained unchanged. |
| Defer | Pass | Only proposal state changed; all other bytes remained unchanged. |
| Stale target | Pass | A later human edit caused revision 2; no compiled overwrite occurred. |
| Obsolete revision | Pass | Approval for revision 1 was refused when revision 2 was current. |
| Raw source drift | Pass | Hash mismatch stopped approval with a zero-byte workspace delta. |
| Invalid schema | Pass | Missing `tags` produced a corrected pending revision, not an applied write. |
| Missing Wiki root | Pass | Hermes requested the root and created nothing. |
| Source outside workspace | Pass | Processing stopped without capture or proposal creation. |
| Target path escape | Pass | No outside write occurred; a corrected pending revision was created. |
| Multiple pending proposals | Pass | Ambiguous approval stopped and listed both candidates. |
| Exact proposal binding | Pass | Only the named target/revision was applied; the other remained byte-identical. |
| Target-first interruption | Pass | Existing reviewed target was not rewritten; missing status/index/log work completed once. |
| Repeated completed request | Pass | Second approval attempt produced a zero-byte delta and no duplicate log. |
| Approval-state-first interruption | Pass | Missing target/index/log work was detected and completed from the approved proposal. |

Both skills recorded 14 uses/views. The matrix consumed 110 model API calls across 14 isolated executions.

## Assessment

The frozen companion passed the automated release matrix. No additional skill change was justified by these tests.

This qualifies the tested Hermes/model/artifact combination as a limited beta review convention. It does not turn prompt instructions into deterministic enforcement and does not qualify arbitrary providers, weak local models, concurrent writers, symlink attacks, live Obsidian usability, or clean member installation.

## Remaining human release checks

1. Install in a fresh Hermes profile exactly as a member would.
2. Confirm a beginner understands the proposal and three contradiction choices in Obsidian.
3. Confirm the second explicit “continue” step is obvious.
4. Test at least one intended weaker or local model before advertising compatibility with it.
