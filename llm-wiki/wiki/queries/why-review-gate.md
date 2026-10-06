---
title: "Query: Why does an LLM Wiki need a human review gate?"
created: 2026-09-28
updated: 2026-09-28
type: query
tags: [review, trust, knowledge-management, controversy]
sources:
  - raw/articles/llm-wiki-review-companion-guide.md
  - raw/articles/llm-wiki-review-qualification-report.md
  - raw/articles/awesome-llm-wiki-readme.md
  - raw/articles/llm-wiki-review-skill.md
  - raw/articles/karpathy-llm-wiki-gist.md
  - raw/articles/hermes-agent-llm-wiki-skill.md
summary: Filed answer — the wiki's compounding property is also its risk, so promotion into the compiled layer is the one decision worth gating.
confidence: high
---

# Query: Why does an LLM Wiki need a human review gate?

> Filed because the answer is a synthesis across four sources and would be painful to
> re-derive. Question asked during vault construction, 2026-09-28.

## Short answer

Because the [[llm-wiki-pattern]]'s central virtue — that knowledge **compounds** instead of
being re-derived per query — is mechanically identical to its central risk. A claim written
once is read many times, cross-referenced by later ingests, cited by filed query answers,
and presented with the same frontmatter, links, and index entry as everything around it.
Nothing in the artifact distinguishes a well-supported claim from a fluent guess. So the one
decision worth gating is **promotion into the compiled layer**, and that is precisely what
[[human-in-the-loop-review-gate]] intercepts.

## The argument, step by step

**1. The pattern removes the human from writing.** "You never (or rarely) write the wiki
yourself — the LLM writes and maintains all of it. You're in charge of sourcing, exploration,
and asking the right questions." ^[raw/articles/karpathy-llm-wiki-gist.md] That is the
efficiency win and the exposure: the person who would have caught a bad claim is no longer
in the write path.

**2. Compounding propagates errors, not just knowledge.** A single source "might touch 10-15
wiki pages. This is normal and desired — it's the compounding effect."
^[raw/articles/hermes-agent-llm-wiki-skill.md] The same fan-out applies to a mistake. Later
ingests then link to the page as established context, and filed query answers cite it — so
the claim acquires inbound links, which *look* like corroboration and are actually echoes.

**3. Presentation is uniform.** Every page gets the same frontmatter, wikilinks, index entry,
and log line. A reader cannot triage by appearance. Upstream's answer is the
[[confidence-and-contested-markers]] fields, whose stated purpose is that "weak claims don't
silently harden into accepted wiki fact" ^[raw/articles/hermes-agent-llm-wiki-skill.md] —
but those markers are self-reported by the process that wrote the claim.

**4. Existing guardrails are conditional on compliance.** The built-in skill already says
handle contradictions explicitly, never silently overwrite, and ask before touching 10+
pages. Good rules; they bind a model that follows them. The gate changes the **default** from
"write unless told to ask" to "stop unless told to write".

**5. So the gate's job is narrow and specific.** It is not quality control in general. It
owns one transition: synthesized content → trusted compiled page. The companion states the
goal as [[anti-slopification]]: "let AI organize knowledge without silently turning every
plausible synthesis into permanent truth. Raw evidence remains inspectable, the human
controls promotion, and the Wiki becomes a deliberately curated library of truth."
^[raw/articles/llm-wiki-review-companion-guide.md]

## What the gate adds beyond "be careful"

Three properties that careful prompting does not provide:

- **A legible artifact.** The proposal is a markdown file containing the *exact bytes* that
  would be written, so approval means something precise. It can be read in [[obsidian]],
  edited, diffed, and versioned.
- **Revision binding.** Approval attaches to one revision of one target. A later edit forces
  revision 2; an approval for revision 1 is refused; raw-source hash drift stops the
  application with a zero-byte delta. Tested behavior, not aspiration.
  ^[raw/articles/llm-wiki-review-qualification-report.md]
- **A default of disagreement visibility.** On contradictions the primary proposal is *keep
  both* and mark the topic contested, with source preference demoted to an advanced revision
  requiring a reason. The system's bias is toward preserving the disagreement rather than
  resolving it. ^[raw/articles/llm-wiki-review-skill.md]

## Objections worth taking seriously

**"It blocks automation."** True, and deliberately. Unattended ingest is exactly when nobody
is reading; the guide routes that case to the deterministic Agentic Librarian instead. See
[[review-companion-vs-agentic-librarian]].

**"The model is good enough now."** Maybe, and the gate is cheap insurance if so. But the
qualification report is explicit that it qualifies *one* Hermes/model/artifact combination
and "does not qualify arbitrary providers, weak local models, concurrent writers, symlink
attacks" — and [[hermes-agent]] lets you switch models without code changes, so "good enough"
is a moving target. ^[raw/articles/llm-wiki-review-qualification-report.md]

**"Reviewers will just approve everything."** The strongest objection, and the tooling cannot
answer it. Approval fatigue produces a rubber stamp *with an audit trail*, which reads as
more trustworthy than no gate at all. Mitigations are procedural: raise the materiality bar,
batch proposals, review on a schedule. Untested in the captured sources — this is inference.

**"It is not enforcement anyway."** Correct, and stated by its own authors: "an
instruction-based review convention, not a deterministic security boundary."
^[raw/articles/llm-wiki-review-companion-guide.md] Which is why the answer is a gate *plus*
[[verification-layers]] *plus* Git, not a gate alone.

## What would change this answer

- Evidence that a compiled wiki with no gate stays accurate at scale over months — would
  demote the gate from necessary to prudent.
- Evidence that reviewer diligence collapses under sustained proposal volume — would demote
  the gate from sufficient to theatrical, and favor a deterministic core.
- A benchmark measuring compiled-wiki claim accuracy against ground truth. The catalogued
  Agentic Memory Index claims to test 12 memory architectures on conflicting facts across 56
  sessions ^[raw/articles/awesome-llm-wiki-readme.md], but it is not captured here, so it is
  not evidence in this wiki.

## Drew on

[[human-in-the-loop-review-gate]] · [[anti-slopification]] · [[llm-wiki-pattern]] ·
[[confidence-and-contested-markers]] · [[verification-layers]] ·
[[review-companion-vs-agentic-librarian]]
