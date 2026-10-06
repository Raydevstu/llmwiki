# Setup Guide

Installing, configuring, and running this vault. Assumes Python 3.9+ (no third-party
packages) and, optionally, Git and Obsidian.

---

## 1. Put the vault somewhere permanent

```bash
# copy or clone llm-wiki/ wherever you keep it
cp -r llm-wiki ~/llm-wiki
cd ~/llm-wiki
```

Only `wiki/` is the vault. `tools/`, `skills/`, and `docs/` live beside it so the tooling and
the skill ship with the knowledge they govern.

If you would rather keep the vault inside an existing Obsidian library, copy `wiki/` there and
point `WIKI_PATH` at it — nothing else assumes a location.

## 2. Check the tooling

```bash
python3 tools/wiki_tool.py lint      # expect: 0 errors, 0 warnings
python3 tools/selftest.py            # expect: 95 passed, 0 failed
python3 tools/wiki_tool.py verify    # expect: 9/9 raw captures verified
```

If `verify` reports drift on a fresh copy, the files were altered in transit — stop and
re-copy. `raw/` is supposed to be immutable.

Optional convenience wrapper:

```bash
chmod +x tools/wiki
sudo ln -s "$(pwd)/tools/wiki" /usr/local/bin/wiki   # or add tools/ to PATH
wiki lint
```

## 3. Set `WIKI_PATH`

The built-in skill resolves the vault from `WIKI_PATH`, defaulting to `~/wiki`.

**Hermes Agent** — add to `${HERMES_HOME:-~/.hermes}/.env`:

```bash
WIKI_PATH=/home/you/llm-wiki/wiki
```

**Any shell** — add to `~/.bashrc` / `~/.zshrc`:

```bash
export WIKI_PATH="$HOME/llm-wiki/wiki"
```

`wiki_tool.py` resolves in this order: `--wiki` flag → `$WIKI_PATH` → `../wiki` relative to
`tools/`. The last one means it works with no configuration at all as long as you run it from
this project. If it cannot find a `SCHEMA.md`, it errors out and lists where it looked — it
never guesses a different workspace.

If you also use the Obsidian skill, set `OBSIDIAN_VAULT_PATH` to the same directory.

## 4. Install the review skill

Copy `skills/llm-wiki-review/` into your runtime's skills directory.

| Runtime | Destination |
| --- | --- |
| Hermes Agent | `${HERMES_HOME:-~/.hermes}/skills/llm-wiki-review/` (or the active profile's `skills/`) |
| Claude Code | `.claude/skills/llm-wiki-review/` in your project, or `~/.claude/skills/llm-wiki-review/` |
| Codex / OpenCode / other | Any skills dir the host reads; otherwise keep the file in the repo and tell the agent to follow it |
| No skill system | Paste `wiki/SCHEMA.md` + `skills/llm-wiki-review/SKILL.md` into context at session start |

```bash
# Hermes example
mkdir -p ~/.hermes/skills
cp -r skills/llm-wiki-review ~/.hermes/skills/
```

Confirm the built-in `llm-wiki` skill is enabled too. The companion wraps it; it does not
replace it. On a runtime without the built-in skill, the captured copy at
`wiki/raw/articles/hermes-agent-llm-wiki-skill.md` is the procedure — read it, and read
`wiki/SCHEMA.md`, before doing anything.

**Two install rules that matter:**

1. **Invoke the review skill first.** Running `/llm-wiki` directly can bypass the gate.
2. **Never run two review authorities.** If you later install a deterministic Agentic
   Librarian that owns review and apply, the companion is supposed to stop. Do not run both
   against one vault.

### Verifying you installed the qualified artifact

```bash
python3 - <<'PY'
import hashlib, pathlib
p = pathlib.Path("skills/llm-wiki-review/SKILL.md").read_bytes()
frozen = "d9c037639f7ef703427ef32cbd8eb3b1018ac1974a5c953a9a9f2f901459dc2c"
print("upstream body intact:", hashlib.sha256(p[:5803]).hexdigest() == frozen)
PY
```

The first 5,803 bytes are the qualified upstream body, verbatim. Everything after
`# Additions for this vault` is local (tooling bindings and runtime adapters) and is **not**
covered by the qualification report. Delete the appendices and re-hash to reproduce the
qualified artifact exactly.

## 5. Initialise Git — this is the actual backstop

The review gate is an instruction-based convention. The only control that lives outside the
model is version control. Do not skip this.

```bash
cd wiki
git init
cat > .gitignore <<'EOF'
.obsidian/workspace.json
.obsidian/workspace-mobile.json
.obsidian/cache
.trash/
EOF
git add -A
git commit -m "LLM Wiki: initial vault (9 raw captures, 26 compiled pages, 1 pending proposal)"
```

The workflow that makes it useful:

```bash
git status                 # before ingest — confirm clean
# ... run the ingest ...
git status                 # after — anything unexpected is visible
git diff                   # read exactly what changed
git add -A && git commit -m "ingest: <source>"
```

A refusal that produced a byte delta shows up here, which is why the qualification matrix's
success criterion is a **zero-byte workspace delta**. Without Git you cannot tell the
difference between "the gate stopped it" and "the gate stopped it and also wrote something".

Optional, stronger: make the raw layer immutable at the filesystem level.

```bash
chmod -R a-w wiki/raw       # the agent user can no longer modify captures
chmod -R u+w wiki/raw       # undo when you legitimately need to add a capture
```

## 6. Obsidian settings

Open `wiki/` as a vault. Recommended settings:

| Setting | Value | Why |
| --- | --- | --- |
| Files & Links → Attachment folder | `raw/assets/` | Binary captures belong in the immutable layer |
| Files & Links → Wikilinks | On (default) | The entire cross-reference convention assumes it |
| Search → Excluded files | `raw/` (optional) | Search compiled pages only |
| Community plugins → Dataview | Optional | Query frontmatter, e.g. contested pages |
| Appearance → Properties in document | Visible | You will edit `decision:` by hand |

Useful Dataview queries once installed:

````
```dataview
TABLE confidence, updated, contested
FROM "concepts" OR "entities" OR "comparisons" OR "queries"
WHERE contested OR confidence = "low"
SORT updated ASC
```

```dataview
TABLE decision, status, revision, target
FROM "review"
SORT file.name DESC
```

```dataview
LIST
FROM "concepts"
WHERE length(sources) = 1 AND !confidence
```
````

The third one finds single-source pages that never declared a confidence level — the
"unmarked is not neutral" case that lint also reports.

### Reviewing a proposal in Obsidian

Open the file in `review/`, read *What will change* and *Evidence and uncertainty*, then
either write your choice under **Human feedback** or set `decision:` in the frontmatter.
Then tell the agent:

```text
Continue the pending Wiki review.
```

**Editing the note alone does not trigger anything.** This is the single most common way the
workflow silently stalls — you approve in Obsidian, walk away, and nothing happens. The
qualification report lists "confirm the second explicit 'continue' step is obvious" as an
outstanding human release check, because it is a real trap.

If you would rather not depend on the agent noticing, apply it yourself:

```bash
python3 tools/wiki_tool.py apply <proposal-filename>.md --decision approve --revision 1
```

### Headless / remote sync

If the agent runs on a server and you read on a laptop, the built-in skill documents
`obsidian-headless` (Node.js 22+), which syncs via Obsidian Sync without a GUI:

```bash
npm install -g obsidian-headless
ob login --email you@example.com --password '<password>'
ob sync-create-remote --name "LLM Wiki"
cd ~/llm-wiki/wiki && ob sync-setup --vault "<vault-id>"
ob sync                      # initial
ob sync --continuous           # foreground; put under systemd for background
```

A systemd user unit plus `sudo loginctl enable-linger $USER` keeps sync alive across logouts.
Plain Git over SSH works just as well and needs no subscription.

## 7. First run — a complete reviewed ingest

This is the whole loop, end to end.

```bash
# 1. Orient. Non-negotiable; skipping it is what causes duplicates.
python3 tools/wiki_tool.py orient

# 2. Capture the source immutably. Hashes, writes, re-reads, verifies, deletes on failure.
python3 tools/wiki_tool.py capture \
  --url https://example.com/some-article \
  --dest raw/articles/some-article.md

# 3. Check what already exists BEFORE drafting anything.
grep -rln "some topic" wiki/concepts wiki/entities wiki/comparisons wiki/queries

# 4. Draft the page in a scratch file (not in the vault).
$EDITOR /tmp/draft.md

# 5. Propose. Validates against SCHEMA.md and refuses to create a proposal for invalid
#    content — you are never asked to approve something structurally broken.
python3 tools/wiki_tool.py propose \
  --target concepts/some-topic.md \
  --content /tmp/draft.md \
  --what "Add a concept page for some-topic, covering X and Y." \
  --evidence "Two sources agree on X. Y is single-source and marked confidence: medium."

# 6. STOP. Read the proposal. Decide.
python3 tools/wiki_tool.py pending
$EDITOR wiki/review/$(date +%F)-some-topic-proposal.md

# 7. Apply. Seven ordered checks run before any byte is written.
python3 tools/wiki_tool.py apply $(date +%F)-some-topic-proposal.md --decision approve --revision 1

# 8. Maintain. The approve step already rebuilt the index and appended the log.
python3 tools/wiki_tool.py lint

# 9. Commit.
cd wiki && git add -A && git commit -m "ingest: some-article -> concepts/some-topic.md"
```

A brand-new page will be reported as an **orphan** by lint until something links to it. That
is correct and expected — add an inbound link from a related page, or accept the warning and
fix it on the next ingest.

### Contradiction runs

If the new source contradicts an existing page, propose with
`--operation conflict-resolution`. The proposal then presents three primary choices —
**keep both**, **not a contradiction**, **decide later** — and defaults to preserving both
claims with `contested: true`. Preferring a source is an *advanced* revision and needs a
reason or stronger evidence.

`wiki/review/2026-09-28-index-first-navigation-proposal.md` is a worked example.

## 8. Changing the domain

This vault's domain is AI / LLM research, agents, and knowledge tooling. To repurpose it:

1. **Rewrite `wiki/SCHEMA.md`'s `## Domain` section** — in scope, out of scope.
2. **Rewrite `## Tag Taxonomy`.** Lint reads this section as authoritative, so tags must be
   bare lowercase words in those bullets. Add a tag here *before* using it on a page.
3. **Clear `wiki/raw/`, `entities/`, `concepts/`, `comparisons/`, `queries/`, `review/`.**
   Keep the directories.
4. **Reset `wiki/log.md`** to a fresh header plus one `create | Wiki initialized` entry.
5. `python3 tools/wiki_tool.py reindex && python3 tools/wiki_tool.py lint`

Do not delete `_meta/topic-map.md`'s *structure* — rewrite its groupings for the new domain.
And do not edit `tools/wiki_tool.py`'s `COMPILED_DIRS`, `PAGE_TYPES`, or `REQUIRED_PAGE_FIELDS`
unless you also update `SCHEMA.md`; the two are a contract with each other, and
`tools/selftest.py` is what tells you when they have drifted apart.

## 9. Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `error: no vault found` | No `SCHEMA.md` at the resolved path | Pass `--wiki /abs/path/to/wiki` or set `WIKI_PATH` |
| `lint` reports `source drift` on a file you never touched | Transfer altered it, or the capture was written by something other than `capture` | Re-capture with `--force`; never hand-edit `raw/` |
| `lint` reports drift on a file whose body starts with `---` | Something stripped frontmatter by pattern instead of position | Use `wiki_tool.py hash`; `split_raw_body()` strips by the *second* `---` line |
| `apply` says `target drift` | The target changed after the proposal was reviewed | Correct behaviour. Re-propose against the current target |
| `apply` says `content changed after review` | The proposal's `## Proposed content` block was edited | Correct behaviour. Create a new revision; never apply unreviewed bytes |
| `apply` says `refusing to apply 'X' to a decided proposal` | The proposal is already applied/rejected/deferred | Correct behaviour. Use `--decision revise` to reopen as a new pending revision |
| `propose` refuses with a list of schema errors | The draft is structurally invalid | Correct behaviour — fix the draft. You should never be asked to approve invalid content |
| A new page is flagged `orphan` | Nothing links to it yet | Add an inbound link from a related page |
| `index.md` looks wrong after hand-editing | It is machine-generated | Edit the page's `summary:` frontmatter, then `reindex` |
| The agent wrote a page without a proposal | The gate is a convention, not a boundary | `git diff`, revert, and check whether the review skill was actually invoked first |

## 10. What to read next

In the vault, by question — `_meta/topic-map.md` has the full set:

- **Why gate writes at all?** `concepts/anti-slopification.md` → `queries/why-review-gate.md`
- **How does the gate work?** `concepts/human-in-the-loop-review-gate.md` → `review/README.md`
- **What's enforced vs requested?** `concepts/verification-layers.md`
- **Is this tooling enough?** `comparisons/review-companion-vs-agentic-librarian.md`
- **How do I capture sources correctly?** `concepts/immutable-raw-layer.md`
- **What breaks if I skip orientation?** `queries/skipping-orientation.md`
