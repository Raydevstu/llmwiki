---
name: llm-wiki-review
description: Add a manual human review gate to Hermes' built-in llm-wiki workflow before compiled Wiki pages are created or changed. Use when the user explicitly invokes /llm-wiki-review for review-first LLM Wiki ingest or update work.
---

# LLM Wiki Review

Act as a lightweight human-in-the-loop wrapper around Hermes' built-in `llm-wiki` skill. Preserve the built-in workflow and intercept only the final decision to create or change compiled Wiki pages.

## Authority Boundary

- Explicitly load `llm-wiki` with `skill_view(name='llm-wiki')`.
- Let it orient to the Wiki, capture Raw material, search existing pages, synthesize changes, preserve provenance, surface contradictions, and perform post-write maintenance.
- Own the review decision for the current invocation. Do not allow the built-in skill to write compiled pages before approval.
- Do not modify the installed `llm-wiki` skill.
- If a deterministic Agentic Librarian such as `scripts/librarian_tool.py` already owns review and apply operations, stop. Never run both review authorities on the same change.

## Workflow

### 1. Prepare the change

1. Resolve `WIKI_PATH` or ask for the Wiki root.
2. Confirm the source and Wiki root exist inside the intended workspace. If either is missing or ambiguous, stop without searching other workspaces.
3. Load `llm-wiki` and follow its normal orientation, capture, retrieval, and synthesis steps.
4. Allow immutable Raw capture, but stop before creating or changing a compiled entity, concept, comparison, query, index, or log entry.

When capturing Raw, hash the exact source body before adding frontmatter. Store one blank separator after the closing `---`, then the unchanged body. Immediately recompute the hash by removing the frontmatter and that one separator; correct the new metadata if it does not match.

### 2. Create one review proposal

Create `Review/` if needed. Write one Markdown proposal per target:

```text
Review/YYYY-MM-DD-<target-name>-proposal.md
```

Use this minimal structure:

```yaml
---
type: llm-wiki-review
status: needs-review
decision: pending
revision: 1
operation: create
target: concepts/example.md
sources:
  - raw/example-source.md
---
```

Include these sections:

```markdown
# Proposed Wiki change

## What will change
Explain the change in plain language.

## Proposed content
Include the exact content that would be written.

## Evidence and uncertainty
Identify supporting sources, uncertainty, and conflicting claims.

## Human feedback
Optionally explain or edit what should change.
```

Set `operation` to `create`, `update`, or `conflict-resolution`. Keep all paths relative to the Wiki root.

Before presenting the proposal, validate its proposed content against the active `SCHEMA.md`. Require at least `title`, `created`, `updated`, `type`, `tags`, and `sources`, as specified by the built-in skill. If no tag taxonomy exists, use `tags: []` rather than omitting the field. Do not ask the human to approve structurally invalid content.

For contradictions, show competing claims before details and propose preserving both as contested. Replace the generic `Human feedback` line with exactly these three primary choices, and repeat them in the response:

- **Keep both:** approve this proposal.
- **Not a contradiction:** revise it to preserve compatible or context-dependent claims without `contested`, then stop for approval again.
- **Decide later:** defer without changing compiled content.

Put source preference and custom resolutions under `Advanced: revise`. Require a reason or stronger evidence before preferring a source or removing its claim. Never silently select a winner.

### 3. Stop for a decision

Report the proposal path, target, operation, and main uncertainty. For ordinary proposals ask for `approve`, `reject`, `revise`, or `defer`. For contradictions use the labels above; accept `reject` or custom `revise` as advanced input.

Accept the decision in conversation or through the proposal's `decision` frontmatter. Then stop. Silence and elapsed time are not approval.

Use only these canonical `decision` values: `pending`, `approve`, `reject`, `revise`, and `defer`.

### 4. Resume safely

On the next explicit invocation, reread the proposal and its current revision before acting:

- Revalidate the reviewed content before any write. If it is structurally invalid, do not apply it; create a corrected proposal revision and request review again.
- **Approve:** Apply the exact valid reviewed content. Set `decision: approve` and `status: applied`. Then use the built-in workflow to update links, index, log, and lint.
- **Reject:** Leave the target unchanged. Set `decision: reject` and `status: rejected`.
- **Revise:** Incorporate the feedback into a new proposal, increment `revision`, reset `decision: pending`, and stop for review again.
- **Defer:** Leave the target unchanged. Set `decision: defer` and `status: deferred`.

Never apply an approval to a different revision from the one the human reviewed.

## Completion Checks

Before reporting completion, confirm that:

- Raw material remains source-traceable and unchanged.
- A new Raw capture immediately passes its own stored body-hash check.
- No compiled page changed before approval.
- The proposal records its target, sources, operation, revision, and decision.
- Proposed and applied content satisfy the active schema and required frontmatter.
- Approved content matches the reviewed proposal.
- Rejected or deferred proposals caused no compiled Wiki mutation.
- Built-in maintenance ran after an approved write.

This companion provides a review convention, not deterministic enforcement. Use the full Agentic Librarian when hashes, receipts, replay safety, automation, or mechanically enforced policies are required.

---

# Additions for this vault

> Everything **above this line** is the frozen upstream skill body, byte-identical to
> `raw/articles/llm-wiki-review-skill.md` — SHA-256
> `d9c037639f7ef703427ef32cbd8eb3b1018ac1974a5c953a9a9f2f901459dc2c`, verified 2026-09-28.
> The two appendices below are local additions. They change this file's hash, so the
> qualification report's frozen digest applies to the upstream body only, not to this file.
> Remove both appendices and re-hash to reproduce the qualified artifact exactly.

## Appendix A — Deterministic tooling bindings

This skill is an instruction-based convention. `tools/wiki_tool.py` supplies the mechanical
checks the convention asks for but cannot enforce. **Prefer the tool over doing the step by
hand** wherever one exists — a tool cannot forget, and its refusals are reproducible.

| Skill step | Tool binding |
| --- | --- |
| "Resolve `WIKI_PATH` or ask for the Wiki root" | `--wiki` flag, else `$WIKI_PATH`, else `../wiki` next to `tools/`. A missing vault is a hard error; the tool never searches other workspaces. |
| "Confirm the source and Wiki root exist inside the intended workspace" | `safe_join()` rejects absolute paths, `..` traversal, and symlinks resolving outside the vault, on **every** write path. |
| Orientation before any operation | `wiki_tool.py orient` prints `SCHEMA.md`, `index.md`, the last 30 log entries, and the pending review queue in one call. |
| "Hash the exact source body before adding frontmatter… Immediately recompute" | `wiki_tool.py capture` hashes, writes, re-reads from disk, strips frontmatter positionally, recomputes, and **deletes the file** if verification fails. |
| "Store one blank separator after the closing `---`" | `capture` writes exactly one. `split_raw_body()` strips by position (the *second* `---` line), so captures of files that themselves begin with `---` round-trip. |
| "Validate its proposed content against the active `SCHEMA.md`" | `propose` validates before writing the proposal file, and refuses to create one for invalid content. Never ask a human to approve structurally invalid content. |
| "Require at least `title`, `created`, `updated`, `type`, `tags`, `sources`" | Enforced, plus `summary` (this vault's index depends on it). `tags: []` is required rather than omission. |
| "Confirm the target remains inside the Wiki root" | `propose` and `apply` both call `safe_join()` and require the target to start with a compiled dir. |
| "Reread the proposal and its current revision before acting" | `apply --revision N` refuses on mismatch. Without `--revision`, `apply` still refuses if the proposal's recorded `proposed_sha256` no longer matches its content. |
| "Revalidate the reviewed content before any write" | `apply` re-runs full schema validation, then compares content digests, then writes. |
| Target drift | `apply` compares the target's current digest to the `target_sha256` recorded at proposal time and refuses on mismatch. |
| Raw source drift | `apply` re-verifies every cited capture's hash and refuses on mismatch. |
| "Apply the exact valid reviewed content" | `apply` writes the canonicalized bytes from the proposal's `## Proposed content` fence and reports the digest it wrote. |
| "Set `decision: approve` and `status: applied`" | `apply` sets `status`, `decision`, `updated`, and `applied_revision`, and records human feedback in the file. |
| "Then use the built-in workflow to update links, index, log, and lint" | `apply` rebuilds `index.md`, appends the log entry, checks log rotation, and tells you to run `lint`. |
| "Rejecting or deferring should change only the proposal state" | `apply` writes nothing but the proposal on `reject`, `defer`, and `revise`, and says so. |
| "Never apply an approval to a different revision" | `apply` refuses to re-decide a proposal already `applied`, `rejected`, or `deferred`. Reviving an applied proposal requires `--decision revise`, which creates a **new pending revision** and writes nothing. |
| "A repeated completed request" | `apply` on an already-applied proposal prints `already applied` and produces a zero-byte delta with no duplicate log entry. |
| Ambiguous approval | `lint` errors when one target has two pending proposals, and warns whenever more than one proposal awaits a decision — approve by exact filename and revision, never by "the pending one". |
| Completion checks | `lint` covers the mechanical subset; `selftest.py` proves the refusal paths still work after any change to the tooling. |

Two things **no tool here can do**, because they are the whole point of the gate:

- Make the agent stop. `apply` will not write without a decision, but an agent with file
  access can bypass `apply` entirely. Git is the backstop, not the tool.
- Tell whether a human actually read the proposal, or whether a `^[raw/…]` marker's file
  really supports the claim it is attached to.

## Appendix B — Runtime adapters

The upstream body names Hermes tools (`skill_view`, `web_extract`, `search_files`,
`read_file`, `execute_code`). Map them to the host runtime; the *procedure* is identical
everywhere, and `tools/wiki_tool.py` is plain Python 3 with no dependencies, so it runs on
any host that can execute a script.

| Step | Hermes Agent | Claude Code / Claude Desktop | Codex / OpenCode / generic |
| --- | --- | --- | --- |
| Load the built-in wiki skill | `skill_view(name='llm-wiki')` | Read the `llm-wiki` skill / plugin file, or the vault's `SCHEMA.md` if no skill is installed | Read `SCHEMA.md` plus the built-in skill's capture in `raw/articles/hermes-agent-llm-wiki-skill.md` |
| Resolve the vault root | `$WIKI_PATH` in `${HERMES_HOME:-~/.hermes}/.env` | `$WIKI_PATH`, or the open project root | `$WIKI_PATH`, or `--wiki` |
| Capture a URL | `web_extract` | WebFetch, then `wiki_tool.py capture --file` | Fetch, then `wiki_tool.py capture --file`, or pipe to `capture` on stdin |
| Search the vault | `search_files` | Grep / Glob | `grep -rn`, or `wiki_tool.py orient` |
| Read a file | `read_file` | Read | `cat` |
| Scan links programmatically | `execute_code` | `python3 tools/wiki_tool.py lint` | same |
| Where this skill lives | `<profile>/skills/llm-wiki-review/SKILL.md` | `.claude/skills/llm-wiki-review/SKILL.md` | Any skills dir, or paste `SCHEMA.md` + this file into context |
| Invocation | `/llm-wiki-review …` | `/llm-wiki-review …` or "use the review skill" | "Follow `skills/llm-wiki-review/SKILL.md` and process …" |

Rules that do **not** change with the runtime:

1. Invoke the review skill **first**. Running the built-in wiki workflow directly can bypass
   the gate.
2. Never run two review authorities on the same change. If a deterministic librarian already
   owns review and apply, stop.
3. Do not modify the installed built-in `llm-wiki` skill.
4. Silence and elapsed time are never approval.
5. Stop before creating or changing any compiled page, index entry, or log entry.

If the host has no skill system at all, the minimum viable gate is: read `SCHEMA.md`, write
the proposal with `wiki_tool.py propose`, stop, and do not write the target until a human
answers. The tool enforces everything downstream of that decision.
