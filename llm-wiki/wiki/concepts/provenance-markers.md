---
title: Provenance markers
created: 2026-09-28
updated: 2026-09-28
type: concept
tags: [provenance, markdown, verification, knowledge-management]
sources:
  - raw/articles/hermes-agent-llm-wiki-skill.md
  - raw/articles/karpathy-llm-wiki-gist.md
summary: Inline caret-bracket annotations tying a paragraph's claims to one captured source, so each claim is traceable without rereading every listed file.
confidence: high
---

# Provenance markers

## Definition

An inline annotation appended to a paragraph whose claims come from one specific source.
The marker is a caret followed immediately by a bracketed vault-relative path — shown here
in code so lint does not read it as a live reference:

```markdown
The wiki is a persistent, compounding artifact. ^[raw/articles/karpathy-llm-wiki-gist.md]
```

Upstream's rule: on pages that synthesize **3+ sources**, append the marker at the end of
each paragraph whose claims trace to a particular source. "This lets a reader trace each
claim back without re-reading the whole raw file." It is optional on single-source pages,
where the `sources:` frontmatter is enough. ^[raw/articles/hermes-agent-llm-wiki-skill.md]

The ingest procedure repeats it as a step: "On pages synthesizing 3+ sources, append
`^[raw/articles/source.md]` markers to paragraphs whose claims trace to a specific source."
^[raw/articles/hermes-agent-llm-wiki-skill.md] Karpathy's gist asks for answers "with
citations" but does not specify a syntax; the marker format is the skill's contribution.
^[raw/articles/karpathy-llm-wiki-gist.md]

## Why frontmatter `sources:` is not enough

A page-level source list answers "which sources informed this page?" It cannot answer
"**which** source supports **this sentence**?" On a page compiled from five sources, a
page-level list is close to no information at all — any of the five could be responsible for
any claim, and the reader must reread all of them to find out.

That distinction is the whole content of [[source-traceability]]: page-level provenance
supports *discovery*, claim-level provenance supports *audit*. Audit is what you need when
you suspect a claim is wrong, and suspicion is exactly when you do not want to reread five
documents.

## Conventions in this vault

- Path is **vault-relative** and must resolve to a real file. `tools/wiki_tool.py lint`
  reports unresolvable markers as errors, because a marker pointing at nothing is worse than
  no marker — it looks like evidence.
- Markers go at the **end of the paragraph**, not mid-sentence, to keep prose readable.
- Blockquotes carrying a source's exact words get the marker on the closing line.
- Tables: put the marker in the cell when columns differ by source, or once after the table
  when the whole table is from one source.
- On pages where a claim is **not** from any captured source — the agent's own synthesis, an
  inference, a caveat — say so in prose ("this is my reading, not sourced") and reflect it in
  `confidence`. See [[confidence-and-contested-markers]]. [[anti-slopification]] and
  [[open-source-agent-skills]] both do this deliberately.

## Limits

- **It is a convention, not a citation graph.** Nothing mechanically verifies that the
  paragraph's claims are actually in the marked file. `lint` checks that the path exists;
  only a human or a verification agent can check that the content matches. That gap is why
  [[verification-layers]] treats claim verification as a layer-3/4 concern.
- **It gets noisy on dense pages.** A page where every paragraph needs a marker from a
  different source is a page that should probably be split, per the 200-line rule in
  `SCHEMA.md`.
- **Raw captures must be immutable for markers to mean anything.** If `raw/` could be edited
  after the fact, a marker would point at content that may not have existed when the claim
  was written. Hashing is what closes that hole — see [[immutable-raw-layer]].

## Related

[[source-traceability]] · [[immutable-raw-layer]] · [[confidence-and-contested-markers]] ·
[[llm-wiki-skill]] · [[anti-slopification]]
