---
title: Obsidian
created: 2026-09-28
updated: 2026-09-28
type: entity
tags: [tooling, obsidian, markdown, knowledge-management]
sources:
  - raw/articles/llm-wiki-review-companion-guide.md
  - raw/articles/karpathy-llm-wiki-gist.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/transcripts/wanderloots-llm-wiki-obsidian-video.md
summary: Markdown editor used as the human-side reader for a compiled wiki; its vault format, wikilinks, and graph view are why the pattern is file-based.
confidence: high
---

# Obsidian

## Overview

Markdown knowledge editor. In this pattern it is **the human's window onto the wiki**, not
the wiki's storage engine — the vault is just a directory of `.md` files that also opens in
VS Code or any editor, with no database and no special tooling required.
^[raw/articles/hermes-agent-llm-wiki-skill.md]

[[andrej-karpathy]]'s description of the working loop: agent on one side, Obsidian on the
other, edits landing live while he follows links, checks graph view, and reads updated
pages. His framing — "Obsidian is the IDE; the LLM is the programmer; the wiki is the
codebase" — is the clearest statement of the division of labor. ^[raw/articles/karpathy-llm-wiki-gist.md]

The video this vault was built from is titled *"How To Build LLM Wiki In Obsidian? A Memory
Layer For Any Agentic AI"*, and the community list describes it as mapping "the core 3-tier
local memory architecture … a file-based ingestion pipeline, a Git-backed maintenance loop,
and an agentic vault firewall wrapper." ^[raw/articles/awesome-llm-wiki-readme.md]
That "vault firewall" is [[human-in-the-loop-review-gate]].

## Why it works as the reader

- `[[wikilinks]]` render as clickable links — the cross-reference layer becomes navigable.
- **Graph View** visualizes the knowledge network, which makes orphans and clusters visible
  without running lint.
- YAML frontmatter powers **Dataview** and **Bases** queries, so `confidence`, `contested`,
  and `updated` become filterable metadata rather than prose.
- `raw/assets/` holds images referenced as `![[image.png]]`.

^[raw/articles/hermes-agent-llm-wiki-skill.md]

## Vault settings for this wiki

| Setting | Value | Reason |
| --- | --- | --- |
| Attachment folder | `raw/assets/` | Keeps binary captures inside the immutable layer |
| Wikilinks | On (default) | The whole cross-reference convention assumes it |
| Dataview plugin | Optional | e.g. `TABLE confidence, updated FROM "concepts" WHERE contested` |
| Excluded files | `raw/` (optional) | Search compiled pages only |
| Sync | Obsidian Sync, Git, or `obsidian-headless` | See below |

## Headless and remote setups

For a server-resident agent writing while a laptop reads, the built-in skill documents
`obsidian-headless` (Node.js 22+), which syncs via Obsidian Sync without a GUI:
`ob login`, `ob sync-create-remote`, `ob sync-setup --vault <id>`, then `ob sync
--continuous` under a systemd user unit with `loginctl enable-linger` so sync survives
logout. ^[raw/articles/hermes-agent-llm-wiki-skill.md]

If the Obsidian skill runs alongside this one, set `OBSIDIAN_VAULT_PATH` to the same
directory as `WIKI_PATH`.

## Reviewing proposals inside Obsidian

The review gate can be answered without talking to the agent: write the choice under the
proposal's **Human feedback** heading, or change its `decision` property, then tell the
agent to *"Continue the pending Wiki review."* Editing the note alone does not trigger
anything — silence and elapsed time are never approval.
^[raw/articles/llm-wiki-review-companion-guide.md]

That last property is a real usability constraint: a reviewer who edits the file and walks
away gets no change at all. See [[why-review-gate]].

## Related

[[llm-wiki-pattern]] · [[andrej-karpathy]] · [[markdown-as-knowledge-substrate]] ·
[[wanderloots]] · [[human-in-the-loop-review-gate]]
