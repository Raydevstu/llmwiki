---
title: Nous Research
created: 2026-09-28
updated: 2026-09-28
type: entity
tags: [company, lab, open-source, agent]
sources:
  - raw/articles/hermes-agent-readme.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
summary: AI lab that builds Hermes Agent, the runtime shipping the built-in llm-wiki skill this vault is compiled for.
confidence: high
---

# Nous Research

## Overview

AI research lab and the author of [[hermes-agent]], released under the MIT license.
The lab also operates **Nous Portal**, one of the model providers the agent supports.
^[raw/articles/hermes-agent-readme.md]

## Key facts

| Fact | Value | Source |
| --- | --- | --- |
| Principal open-source product | Hermes Agent (MIT) | `raw/articles/hermes-agent-readme.md` |
| Distribution | Install script for Linux/macOS/WSL2; PowerShell one-liner for native Windows; signed APT repo for Android/Termux | ^[raw/articles/hermes-agent-readme.md] |
| Skill ecosystem | Compatible with the `agentskills.io` open standard | ^[raw/articles/hermes-agent-readme.md] |
| Research angle | Batch trajectory generation and trajectory compression for training tool-calling models | ^[raw/articles/hermes-agent-readme.md] |
| Relevance here | Ships [[llm-wiki-skill]] as a built-in research skill | ^[raw/articles/hermes-agent-llm-wiki-skill.md] |

## Why this wiki cares

Nous Research is the upstream maintainer of the skill that defines this vault's operating
procedure. Two consequences:

1. **The built-in skill is the authority on the workflow.** Orientation, capture,
   retrieval, synthesis, provenance, contradiction surfacing, and post-write maintenance
   all belong to [[llm-wiki-skill]]. The [[llm-wiki-review-skill]] deliberately does *not*
   reimplement or modify it — it intercepts only the final write decision. See
   [[human-in-the-loop-review-gate]].
2. **Upstream changes are a drift risk.** This vault froze the built-in skill as a raw
   capture with a SHA-256. If upstream `main` changes, re-capture and diff rather than
   assuming the local procedure still matches. `tools/wiki_tool.py lint` reports raw hash
   drift, but only against the stored hash — it cannot tell you upstream moved. See
   [[immutable-raw-layer]].

## Model-agnostic posture

Hermes Agent is explicitly not tied to one model: Nous Portal, OpenRouter, OpenAI, or a
self-hosted endpoint, switchable without code changes. ^[raw/articles/hermes-agent-readme.md]
That matters for this vault because the review gate's reliability is model-dependent — the
qualification report for [[llm-wiki-review-skill]] tested exactly one model and warns that
weaker or local models are unqualified. See [[verification-layers]].

## Related

[[hermes-agent]] · [[llm-wiki-skill]] · [[andrej-karpathy]] · [[open-source-agent-skills]]
