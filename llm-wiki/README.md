# LLM Wiki — a compiled, human-gated knowledge vault

A working implementation of [Andrej Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f),
built as an [Obsidian](https://obsidian.md) vault, wired for the
[Hermes Agent](https://github.com/NousResearch/hermes-agent) `llm-wiki` skill, and gated by
the `llm-wiki-review` companion so **nothing enters the compiled wiki without a human
decision**.

Built from the workflow in *"How To Build LLM Wiki In Obsidian? 🧠 A Memory Layer For Any
Agentic AI"* ([Wanderloots](https://youtu.be/QbjAQFJJyt0)): a three-tier local memory
architecture, a file-based ingestion pipeline, a Git-backed maintenance loop, and an agentic
vault firewall.

**Domain:** AI / LLM research, agents, and knowledge tooling.
**State:** 9 hash-verified raw captures → 26 compiled pages → 1 live proposal awaiting review.
**Lint:** 0 errors, 0 warnings. **Self-test:** 95/95 passing.

```
llm-wiki/
├── README.md                     ← you are here
├── docs/SETUP.md                 ← install, configure, first run (start here if you're setting up)
├── skills/llm-wiki-review/       ← the review gate: SKILL.md + start-here.md
├── tools/
│   ├── wiki_tool.py              ← layer 3: lint, capture, verify, reindex, propose, apply, orient
│   ├── selftest.py               ← 95-case release matrix for the gate and the tooling
│   └── wiki                      ← thin shell wrapper
└── wiki/                         ← THE VAULT. Open this directory in Obsidian.
    ├── SCHEMA.md                 ← layer 3 contract: domain, conventions, tag taxonomy, thresholds
    ├── index.md                  ← machine-generated catalog (wiki_tool.py reindex)
    ├── log.md                    ← append-only action log
    ├── raw/                      ← layer 1: immutable, hash-pinned captures
    │   ├── articles/  papers/  transcripts/  assets/
    ├── entities/  concepts/  comparisons/  queries/   ← layer 2: the compiled wiki
    ├── review/                   ← proposals awaiting (or recording) a human decision
    └── _meta/topic-map.md        ← navigate by question instead of by folder
```

## The idea in four sentences

RAG rediscovers knowledge from scratch on every query; a wiki **compiles it once and keeps it
current**, so cross-references are already there and contradictions are already flagged. That
compounding is also the risk: a fluent wrong claim, once written, gets cited by everything
after it and becomes indistinguishable from a well-supported one. So the compiled layer is
write-gated — the agent proposes exact bytes into `review/`, a human decides, and only then is
anything written. And because a gate made of instructions is only as good as the model's
willingness to follow it, every property that *can* be checked by code is checked by
`wiki_tool.py`, with Git behind it.

## Start here

```bash
cd llm-wiki
python3 tools/wiki_tool.py lint      # 0 errors, 0 warnings
python3 tools/selftest.py            # 95 passed, 0 failed
python3 tools/wiki_tool.py orient    # the session-start bundle: schema + index + log + review queue
python3 tools/wiki_tool.py pending   # what is waiting on you
```

Then open `wiki/` in Obsidian and read `_meta/topic-map.md` — it orders the pages by question
rather than by folder.

**One proposal is deliberately left undecided** so you can see the gate's shape before you have
to use it:

```
wiki/review/2026-09-28-index-first-navigation-proposal.md
```

Two authoritative sources disagree about whether index-first navigation scales past ~100 pages.
The proposal preserves both claims, offers both readings, and defaults to marking the page
`contested` rather than picking a winner. Answer it with:

```bash
python3 tools/wiki_tool.py apply 2026-09-28-index-first-navigation-proposal.md --decision approve --revision 1
# or: --decision defer --feedback "capture the Agentic Memory Index benchmark first"
```

## The three operations

**Ingest** — capture immutably, propose, stop, decide, then maintain.

```bash
python3 tools/wiki_tool.py capture --url https://example.com/article \
        --dest raw/articles/example-article.md
# read SCHEMA.md, index.md, recent log.md — then draft the page and:
python3 tools/wiki_tool.py propose --target concepts/example.md --content /tmp/draft.md \
        --what "Add a concept page for X" --evidence "Two sources agree on …; unclear whether …"
python3 tools/wiki_tool.py apply 2026-09-28-example-proposal.md --decision approve --revision 1
python3 tools/wiki_tool.py lint
```

**Query** — orient, read, synthesize with citations, and file answers worth keeping.

```bash
python3 tools/wiki_tool.py orient
grep -rn "contested" wiki/concepts/
```

**Lint** — twelve checks, the mechanical subset of which is automated:

```bash
python3 tools/wiki_tool.py lint            # grouped by severity, exit 1 on errors
python3 tools/wiki_tool.py lint --json     # machine-readable
python3 tools/wiki_tool.py verify          # re-check every raw capture's hash
```

## What is actually enforced

| Enforced by code | Requested of the model |
| --- | --- |
| Raw body hashes; capture verifies itself on write | That the agent stops before writing |
| Required frontmatter; tags inside the taxonomy | That a human reads the proposal |
| Wikilink resolution; ≥2 outbound links per page | That a paragraph means what its marker implies |
| Provenance markers resolve to real files | Page-threshold judgment (create vs update) |
| No path can escape the vault | Fair contradiction resolution |
| Approval binds to an exact target **and** revision | |
| Target drift and raw drift block the write | |
| Reject / defer / revise write no compiled page | |
| Repeated approval is a zero-byte no-op | |
| Index completeness; log format and rotation | |

The right column is why Git is not optional. Full table with sources:
`wiki/concepts/verification-layers.md`.

## Provenance of this vault

Every compiled claim traces to a capture in `wiki/raw/`, each pinned by SHA-256. Two
verifications are worth calling out:

- `raw/articles/hermes-agent-llm-wiki-skill.md` recomputes to
  `0229e37c1783fcac5b77cfb3242703666cf4aa472d2ae85b6bd5279756b515b6`
- `raw/articles/llm-wiki-review-skill.md` recomputes to
  `d9c037639f7ef703427ef32cbd8eb3b1018ac1974a5c953a9a9f2f901459dc2c`

Both **match** the digests frozen in the supplied qualification report, which means the
artifacts that passed its 14-case release matrix are byte-identical to the artifacts installed
here. The installed `skills/llm-wiki-review/SKILL.md` preserves that qualified body verbatim in
its first 5,803 bytes and appends two clearly-marked local appendices after it.

One gap is recorded rather than papered over: the Wanderloots video is captured as **metadata
only** (no transcript), so nothing in this vault may be sourced to what was said in it.
`wiki/entities/wanderloots.md` carries `confidence: medium` for that reason and says so.

## Known limitations

- The gate is a convention, not a boundary. An agent with write access can bypass `apply`.
- `tools/wiki_tool.py` parses a **restricted YAML subset** (scalars, inline lists, block lists,
  one nesting level). Exotic frontmatter will not round-trip.
- Lint checks that a provenance marker's *path* resolves. It cannot check that the file
  *supports the claim*.
- Nothing detects **upstream** drift: a stored hash proves a capture was not tampered with
  locally, not that the source URL still serves the same bytes.
- Qualification covers one Hermes/model/artifact combination. It explicitly does not qualify
  other providers, weak local models, concurrent writers, or symlink attacks.
- Reviewer diligence is the unmitigated risk. A human who approves forty proposals unread has
  built a rubber stamp with an audit trail.

## Next steps

`docs/SETUP.md` — installation, `WIKI_PATH`, per-runtime skill placement, Obsidian settings,
Git, headless sync, changing the domain, and a first-run script.
