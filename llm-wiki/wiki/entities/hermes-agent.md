---
title: Hermes Agent
created: 2026-09-28
updated: 2026-09-28
type: entity
tags: [agent, tooling, open-source, automation]
sources:
  - raw/articles/hermes-agent-readme.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/llm-wiki-review-companion-guide.md
summary: MIT-licensed self-improving agent by Nous Research; ships the built-in llm-wiki skill and the skill system this vault's review gate plugs into.
confidence: high
---

# Hermes Agent

## Overview

Open-source (MIT) AI agent from [[nous-research]], positioned as "the self-improving AI
agent" with a built-in learning loop: it creates skills from experience, improves them
during use, nudges itself to persist knowledge, searches its own past conversations, and
builds a deepening model of the user across sessions. ^[raw/articles/hermes-agent-readme.md]

It is the reference runtime for this vault's workflow. The [[llm-wiki-skill]] is built in;
the [[llm-wiki-review-skill]] installs alongside it as a user skill.

## Capabilities relevant to a compiled wiki

| Capability | Why it matters here |
| --- | --- |
| Skill system, `agentskills.io`-compatible | The review gate ships as a skill folder, not a fork of the built-in one |
| Agent-curated memory with periodic nudges | Memory and wiki have **different jobs** — see [[agentic-memory-vs-compiled-wiki]] |
| FTS5 session search with LLM summarization | Cross-session recall without embedding infra |
| Built-in cron scheduler | Enables unattended ingest — which is exactly when a review gate is most needed |
| Isolated subagents for parallel workstreams | Multiple writers on one vault; the reason `review/` binds proposals to an exact revision |
| Seven terminal backends (local, Docker, SSH, Singularity, Modal, Daytona, Vercel Sandbox) | Wiki can live on a server while [[obsidian]] reads it on a laptop |
| Any model provider, switchable without code changes | Review-gate reliability is model-dependent; switching models re-opens the qualification question |

^[raw/articles/hermes-agent-readme.md]

## Install

```bash
# Linux, macOS, WSL2
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

Native Windows uses a PowerShell one-liner (`install.ps1`); Android/Termux uses a signed
APT repo instead of the desktop installer. ^[raw/articles/hermes-agent-readme.md]

The wiki location is configured via `WIKI_PATH`, typically set in
`${HERMES_HOME:-~/.hermes}/.env`, defaulting to `~/wiki`. ^[raw/articles/hermes-agent-llm-wiki-skill.md]

## Where the review gate attaches

The companion guide is explicit about invocation order: **invoke the review skill first**,
because running `/llm-wiki` directly can bypass the review gate. The gate owns the
decision to create or change compiled pages; the built-in skill still owns orientation,
capture, retrieval, synthesis, provenance, contradiction surfacing, and post-write
maintenance. ^[raw/articles/llm-wiki-review-companion-guide.md]

Two operational constraints follow:

- Do not run the companion and a deterministic Agentic Librarian as **simultaneous review
  authorities** on the same change. See [[review-companion-vs-agentic-librarian]].
- The gate is a convention the model must follow, not a boundary it cannot cross. See
  [[verification-layers]] for what `tools/wiki_tool.py` does enforce mechanically.

## Related

[[nous-research]] · [[llm-wiki-skill]] · [[llm-wiki-review-skill]] ·
[[human-in-the-loop-review-gate]] · [[obsidian]]
