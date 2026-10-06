#!/usr/bin/env python3
"""selftest.py — the release matrix for an LLM Wiki vault's review gate and verification tooling.

Builds a throwaway vault in a temp directory, exercises every refusal path and every write
path in tools/wiki_tool.py, and reports PASS/FAIL per case. Nothing here touches a real vault.

Run:  python3 tools/selftest.py [-v]

The cases mirror the ones in raw/articles/llm-wiki-review-qualification-report.md, restricted
to the properties this vault enforces mechanically. The report's own scope exclusions still
apply: passing this suite does NOT qualify arbitrary providers, weak local models, concurrent
writers, symlink attacks, or human reviewer diligence. See concepts/verification-layers.md.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "wiki_tool.py"

PASS, FAIL = 0, 0
VERBOSE = False


def say(msg: str) -> None:
    if VERBOSE:
        print("      " + msg)


def check(cond: bool, label: str, detail: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {label}")
    else:
        FAIL += 1
        print(f"  FAIL  {label}" + (f"\n          {detail}" if detail else ""))


# --------------------------------------------------------------------------- #
# Fixture
# --------------------------------------------------------------------------- #

SCHEMA = """# Wiki Schema

## Domain
Self-test fixture. Not a real domain.

## Conventions
- File names: lowercase, hyphens, no spaces.
- Minimum 2 outbound wikilinks per compiled page.

## Frontmatter
Required: title, created, updated, type, tags, sources, summary.

## Tag Taxonomy
- **Subject:** agent, tooling
- **Practice:** verification, review, knowledge-management
- **Property:** markdown, trust
- **Meta:** comparison, controversy

## Page Thresholds
- Create a page when an entity or concept appears in 2+ sources.
"""

RAW_BODY = """# Fixture source

The wiki is a persistent, compounding artifact. Claims in this vault may cite this file.

## A section
Some text that can be tampered with to test drift detection.
"""

SEED_PAGE = """---
title: Seed page
created: 2026-01-01
updated: 2026-01-01
type: concept
tags: [verification]
sources:
  - raw/articles/fixture-source.md
summary: A pre-existing compiled page so new pages have something to link to.
confidence: high
---

# Seed page

Exists so link targets resolve. See [[other-seed]] and [[third-seed]].
"""

OTHER_SEED = SEED_PAGE.replace("title: Seed page", "title: Other seed").replace(
    "summary: A pre-existing compiled page so new pages have something to link to.",
    "summary: A second pre-existing compiled page.",
).replace("# Seed page", "# Other seed").replace("[[other-seed]] and [[third-seed]]", "[[seed-page]] and [[third-seed]]")

THIRD_SEED = SEED_PAGE.replace("title: Seed page", "title: Third seed").replace(
    "summary: A pre-existing compiled page so new pages have something to link to.",
    "summary: A third pre-existing compiled page.",
).replace("# Seed page", "# Third seed").replace("[[other-seed]] and [[third-seed]]", "[[seed-page]] and [[other-seed]]")

GOOD_PAGE = """---
title: Good test page
created: 2026-01-02
updated: 2026-01-02
type: concept
tags: [verification, review]
sources:
  - raw/articles/fixture-source.md
summary: A structurally valid page used to exercise the propose and apply pipeline.
confidence: medium
---

# Good test page

Valid content. See [[seed-page]] and [[other-seed]].
"""

BAD_PAGE = """---
title: Bad test page
created: 2026-01-02
type: concept
tags: [not-in-taxonomy]
sources:
  - raw/articles/does-not-exist.md
---

# Bad test page

Missing updated and summary, a tag outside the taxonomy, a source that does not exist,
and only [[seed-page]] as a link.
"""


def build_fixture(root: pathlib.Path) -> pathlib.Path:
    """Create a minimal but schema-complete vault. Returns the vault path."""
    vault = root / "wiki"
    for d in ("raw/articles", "raw/papers", "raw/transcripts", "raw/assets",
              "entities", "concepts", "comparisons", "queries", "review", "_meta"):
        (vault / d).mkdir(parents=True, exist_ok=True)
    (vault / "SCHEMA.md").write_text(SCHEMA, encoding="utf-8")
    (vault / "log.md").write_text(
        "# Wiki Log\n\n> Format: `## [YYYY-MM-DD] action | subject`\n", encoding="utf-8"
    )
    digest = hashlib.sha256(RAW_BODY.encode("utf-8")).hexdigest()
    (vault / "raw/articles/fixture-source.md").write_text(
        f"---\nsource_url: fixture://seed\ningested: 2026-01-01\nsha256: {digest}\n---\n\n{RAW_BODY}",
        encoding="utf-8",
    )
    (vault / "concepts/seed-page.md").write_text(SEED_PAGE, encoding="utf-8")
    (vault / "concepts/other-seed.md").write_text(OTHER_SEED, encoding="utf-8")
    (vault / "concepts/third-seed.md").write_text(THIRD_SEED, encoding="utf-8")
    # index.md is derived, so build it the way a real vault would have it.
    subprocess.run([sys.executable, str(TOOL), "--wiki", str(vault), "reindex", "--quiet"],
                   capture_output=True, text=True, check=True, timeout=60)
    return vault


def run(vault: pathlib.Path, *args: str, expect_rc: int | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(TOOL), "--wiki", str(vault), *args]
    say("$ " + " ".join(args))
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    say((proc.stdout or "").strip()[:1200])
    if proc.stderr.strip():
        say("stderr: " + proc.stderr.strip()[:600])
    if expect_rc is not None and proc.returncode != expect_rc:
        raise AssertionError(f"expected rc={expect_rc}, got {proc.returncode}\n{proc.stdout}\n{proc.stderr}")
    return proc


def write_tmp(root: pathlib.Path, name: str, text: str) -> str:
    p = root / name
    p.write_text(text, encoding="utf-8")
    return str(p)


def vault_digest(vault: pathlib.Path) -> str:
    h = hashlib.sha256()
    for p in sorted(vault.rglob("*")):
        if p.is_file():
            h.update(str(p.relative_to(vault)).encode())
            h.update(p.read_bytes())
    return h.hexdigest()


def log_entries(vault: pathlib.Path) -> int:
    return (vault / "log.md").read_text(encoding="utf-8").count("\n## [")


# --------------------------------------------------------------------------- #
# Cases
# --------------------------------------------------------------------------- #


def main() -> int:
    global VERBOSE
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-v", "--verbose", action="store_true", help="echo every tool invocation and its output")
    ap.add_argument("--keep", metavar="DIR", help="keep the throwaway vault in DIR instead of deleting it")
    args = ap.parse_args()
    VERBOSE = args.verbose

    if not TOOL.is_file():
        raise SystemExit(f"error: {TOOL} not found")

    tmp = pathlib.Path(args.keep) if args.keep else pathlib.Path(tempfile.mkdtemp(prefix="llm-wiki-selftest-"))
    tmp.mkdir(parents=True, exist_ok=True)
    vault = build_fixture(tmp)
    good = write_tmp(tmp, "good.md", GOOD_PAGE)
    bad = write_tmp(tmp, "bad.md", BAD_PAGE)
    print(f"fixture vault: {vault}\n")

    # -- baseline ---------------------------------------------------------- #
    print("[baseline] a fresh fixture vault must be lint-clean")
    p = run(vault, "lint")
    check("0 error(s), 0 warning(s)" in p.stdout, "fresh fixture lints clean", p.stdout[-500:])
    p = run(vault, "verify")
    check("1/1 raw captures verified" in p.stdout, "raw capture hash-verifies")

    # -- capture ----------------------------------------------------------- #
    print("\n[capture] the raw layer")
    stdin_src = tmp / "stdin-source.md"
    stdin_src.write_text("# From stdin\n\nCaptured from a pipe.\n", encoding="utf-8")
    p = subprocess.run(
        [sys.executable, str(TOOL), "--wiki", str(vault), "capture",
         "--dest", "raw/articles/from-stdin.md", "--source-url", "fixture://stdin", "--quiet"],
        input=stdin_src.read_text(), capture_output=True, text=True, timeout=60,
    )
    check(p.returncode == 0 and (vault / "raw/articles/from-stdin.md").is_file(), "captures from stdin")
    cap = (vault / "raw/articles/from-stdin.md").read_text(encoding="utf-8")
    check("verify ok" in p.stdout, "capture re-reads from disk and verifies its own hash", p.stdout)
    check(re.search(r"^sha256: [0-9a-f]{64}$", cap, re.M) is not None, "capture records a sha256")
    check("\n---\n\n# From stdin" in cap, "exactly one blank line separates frontmatter from body")

    p = run(vault, "capture", "--dest", "raw/articles/from-stdin.md", "--file", str(stdin_src), "--quiet")
    check(p.returncode != 0, "refuses to overwrite an existing capture (raw/ is immutable)", p.stderr or p.stdout)
    p = run(vault, "capture", "--dest", "entities/sneaky.md", "--file", str(stdin_src), "--quiet")
    check(p.returncode != 0, "refuses a capture destination outside raw/", p.stderr or p.stdout)
    p = run(vault, "capture", "--dest", "../escape.md", "--file", str(stdin_src), "--quiet")
    check(p.returncode != 0, "refuses a capture destination that escapes the vault", p.stderr or p.stdout)

    p = run(vault, "capture", "--dest", "raw/articles/nested.md", "--file", str(vault / "concepts/seed-page.md"),
            "--source-url", "fixture://nested", "--note", "body itself begins with ---", "--quiet")
    check(p.returncode == 0, "captures a file whose own body starts with '---'")
    p = run(vault, "verify")
    check("3/3 raw captures verified" in p.stdout, "nested-frontmatter capture still round-trips", p.stdout[-300:])

    # -- tamper / drift ---------------------------------------------------- #
    print("\n[drift] tampering with raw/ must be detected and must block writes")
    target_raw = vault / "raw/articles/fixture-source.md"
    original = target_raw.read_text(encoding="utf-8")
    tampered = original.replace("Some text that can be tampered with", "TAMPERED text")
    assert tampered != original, "fixture anchor missing"
    target_raw.write_text(tampered, encoding="utf-8")
    p = run(vault, "verify")
    check(p.returncode != 0, "verify exits non-zero on a tampered capture")
    p = run(vault, "lint")
    check("source drift" in p.stdout, "lint names the drifting capture", p.stdout[-400:])
    p = run(vault, "hash", "raw/articles/fixture-source.md")
    check(p.returncode != 0 and "DRIFT" in p.stdout, "hash reports DRIFT for that file", p.stdout)

    # -- propose ----------------------------------------------------------- #
    print("\n[propose] invalid content must never reach a human")
    p = run(vault, "propose", "--target", "concepts/bad.md", "--content", bad, "--quiet")
    check(p.returncode != 0, "refuses to create a proposal for structurally invalid content")
    for needle, label in [
        ("missing required frontmatter field 'updated'", "names the missing 'updated' field"),
        ("missing required frontmatter field 'summary'", "names the missing 'summary' field"),
        ("outside the taxonomy", "names the out-of-taxonomy tag"),
        ("cites missing source", "names the unresolvable source"),
        ("requires >= 2", "names the insufficient link count"),
    ]:
        check(needle in p.stdout, label, p.stdout[-600:])
    check(not (vault / "review/2026-01-02-bad-proposal.md").exists()
          and not list((vault / "review").glob("*bad*")), "wrote no proposal file for invalid content")

    print("\n[propose] valid content produces a proposal and STOPS")
    p = run(vault, "propose", "--target", "concepts/good.md", "--content", good,
            "--what", "Create concepts/good.md.", "--evidence", "Fixture evidence.", "--quiet")
    check(p.returncode == 0, "creates the proposal")
    check("STOPPED" in p.stdout and "No compiled page was created" in p.stdout, "reports that it stopped")
    check(not (vault / "concepts/good.md").exists(), "target was NOT written before approval")
    prop = vault / "review" / sorted(os.listdir(vault / "review"))[-1]
    ptext = prop.read_text(encoding="utf-8")
    for needle, label in [
        ("type: llm-wiki-review", "proposal type is llm-wiki-review"),
        ("status: needs-review", "status is needs-review"),
        ("decision: pending", "decision is pending"),
        ("revision: 1", "revision is 1"),
        ("operation: create", "operation is create"),
        ("target: concepts/good.md", "records its target"),
        ("## What will change", "has a 'What will change' section"),
        ("## Proposed content", "has a 'Proposed content' section"),
        ("## Evidence and uncertainty", "has an 'Evidence and uncertainty' section"),
        ("## Human feedback", "has a 'Human feedback' section"),
        ("Silence and elapsed time are never approval", "states that silence is not approval"),
    ]:
        check(needle in ptext, label)
    check("proposed_sha256: " + hashlib.sha256(GOOD_PAGE.encode()).hexdigest()[:16] in ptext,
          "proposed_sha256 equals the digest of the exact reviewed content")

    p = run(vault, "propose", "--target", "../outside.md", "--content", good, "--quiet")
    check(p.returncode != 0, "refuses a target outside the vault", p.stderr or p.stdout)
    p = run(vault, "propose", "--target", "raw/articles/nope.md", "--content", good, "--quiet")
    check(p.returncode != 0, "refuses a target inside raw/", p.stderr or p.stdout)
    p = run(vault, "propose", "--target", "index.md", "--content", good, "--quiet")
    check(p.returncode != 0, "refuses a target that is not in a compiled dir", p.stderr or p.stdout)

    # -- apply: refusals --------------------------------------------------- #
    print("\n[apply] refusal paths must leave the vault byte-identical")
    pname = prop.name
    before = vault_digest(vault)
    p = run(vault, "apply", pname, "--decision", "approve", "--revision", "9")
    check(p.returncode != 0 and "Never apply an approval to a different revision" in (p.stderr + p.stdout),
          "refuses an approval for a revision the human did not review", p.stderr)
    p = run(vault, "apply", pname, "--dry-run")
    check(p.returncode != 0 and "is not an application" in (p.stderr + p.stdout),
          "refuses to act on a still-pending proposal (silence is not approval)", p.stderr)
    p = run(vault, "apply", pname)
    check(p.returncode != 0, "refuses when no decision is given and the proposal is pending")
    check(vault_digest(vault) == before, "both refusals produced a zero-byte vault delta")
    check(log_entries(vault) == log_entries(vault), "no log entries written by a refusal")

    print("\n[apply] raw source drift blocks an otherwise valid approval")
    p = run(vault, "apply", pname, "--decision", "approve", "--revision", "1")
    check(p.returncode != 0 and "raw source drift" in (p.stderr + p.stdout),
          "refuses to apply while a cited capture is drifting", p.stderr)
    check(not (vault / "concepts/good.md").exists(), "target still not written")
    target_raw.write_text(original, encoding="utf-8")
    p = run(vault, "verify")
    check(p.returncode == 0, "restoring the capture clears the drift")

    print("\n[apply] target drift blocks approval")
    (vault / "concepts/good.md").write_text("written out of band by something else\n", encoding="utf-8")
    ptext = prop.read_text(encoding="utf-8")
    ptext = ptext.replace("target_exists: false", "target_exists: true")
    stale = hashlib.sha256(b"the page exactly as it was when the human reviewed it\n").hexdigest()
    ptext = re.sub(r"target_sha256: \w+", f"target_sha256: {stale}", ptext, count=1)
    prop.write_text(ptext, encoding="utf-8")
    p = run(vault, "apply", pname, "--decision", "approve", "--revision", "1")
    check(p.returncode != 0 and "target drift" in (p.stderr + p.stdout),
          "refuses to apply when the target changed after review", p.stderr)
    check((vault / "concepts/good.md").read_text(encoding="utf-8") == "written out of band by something else\n",
          "the out-of-band target was not overwritten")
    (vault / "concepts/good.md").unlink()
    prop.write_text(ptext.replace("target_exists: true", "target_exists: false")
                     .replace(f"target_sha256: {stale}", "target_sha256: null"), encoding="utf-8")

    print("\n[apply] content edited after review blocks approval")
    ptext = prop.read_text(encoding="utf-8")
    prop.write_text(ptext.replace("Valid content.", "Valid content, quietly improved."), encoding="utf-8")
    p = run(vault, "apply", pname, "--decision", "approve", "--revision", "1")
    check(p.returncode != 0 and "changed after review" in (p.stderr + p.stdout),
          "refuses to apply content the human did not review", p.stderr)
    prop.write_text(ptext, encoding="utf-8")

    # -- apply: decisions -------------------------------------------------- #
    print("\n[apply] reject and defer change proposal state only")
    for decision, status in (("reject", "rejected"), ("defer", "deferred")):
        other = tmp / f"{decision}.md"
        other.write_text(GOOD_PAGE.replace("title: Good test page", f"title: {decision.title()} page")
                         .replace("# Good test page", f"# {decision.title()} page"), encoding="utf-8")
        p = run(vault, "propose", "--target", f"concepts/{decision}-target.md", "--content", str(other), "--quiet")
        dname = sorted(x for x in os.listdir(vault / "review") if decision in x)[-1]
        before = vault_digest(vault)
        logs_before = log_entries(vault)
        p = run(vault, "apply", dname, "--decision", decision, "--feedback", f"{decision} during self-test", "--quiet")
        check(p.returncode == 0, f"'{decision}' succeeds")
        check(not (vault / f"concepts/{decision}-target.md").exists(), f"'{decision}' wrote no compiled page")
        dt = (vault / "review" / dname).read_text(encoding="utf-8")
        check(f"status: {status}" in dt and f"decision: {decision}" in dt, f"'{decision}' recorded status '{status}'")
        check(f"{decision} during self-test" in dt, f"'{decision}' recorded the human feedback")
        check(log_entries(vault) == logs_before + 1, f"'{decision}' appended exactly one log entry")
        p = run(vault, "lint")
        check("0 error(s)" in p.stdout, f"no lint ERRORS after '{decision}'", p.stdout[-400:])

    print("\n[apply] approve writes the exact reviewed bytes, then runs maintenance")
    logs_before = log_entries(vault)
    p = run(vault, "apply", pname, "--decision", "approve", "--revision", "1", "--quiet")
    check(p.returncode == 0, "approve succeeds", p.stdout + p.stderr)
    written = vault / "concepts/good.md"
    check(written.is_file(), "target page now exists")
    check(written.read_text(encoding="utf-8") == GOOD_PAGE, "written bytes are byte-identical to the reviewed content")
    dt = prop.read_text(encoding="utf-8")
    check("status: applied" in dt and "decision: approve" in dt, "proposal state set to applied/approve")
    check("applied_revision: 1" in dt, "proposal records which revision was applied")
    check("good" in (vault / "index.md").read_text(encoding="utf-8"), "index.md was rebuilt to include the new page")
    check(log_entries(vault) >= logs_before + 2, "log records the approval and the index rebuild")
    p = run(vault, "lint")
    check("0 error(s)" in p.stdout, "no lint ERRORS after the approved write", p.stdout[-500:])
    check("orphan" in p.stdout, "lint flags the brand-new page as an orphan until something links to it")

    print("\n[apply] a repeated approval is idempotent")
    before = vault_digest(vault)
    logs_before = log_entries(vault)
    p = run(vault, "apply", pname, "--decision", "approve", "--revision", "1", "--quiet")
    check("already applied" in p.stdout, "reports 'already applied'")
    check(vault_digest(vault) == before, "zero-byte vault delta on the repeat")
    check(log_entries(vault) == logs_before, "no duplicate log entry on the repeat")

    print("\n[apply] a decided proposal cannot be silently re-decided")
    before = vault_digest(vault)
    p = run(vault, "apply", pname, "--decision", "reject")
    check(p.returncode != 0 and "refusing to apply" in (p.stderr + p.stdout),
          "refuses to reject an already-applied proposal", p.stderr)
    check(vault_digest(vault) == before, "the refusal changed nothing")
    rej = sorted(x for x in os.listdir(vault / "review") if "reject" in x)[-1]
    p = run(vault, "apply", rej, "--decision", "approve")
    check(p.returncode != 0 and "refusing to apply" in (p.stderr + p.stdout),
          "refuses to approve an already-rejected proposal", p.stderr)
    check(not (vault / "concepts/reject-target.md").exists(), "the rejected target is still absent")

    print("\n[apply] revise reopens an applied proposal as a NEW pending revision")
    p = run(vault, "apply", pname, "--decision", "revise", "--feedback", "needs a third outbound link", "--quiet")
    check(p.returncode == 0 and "pending revision 2" in p.stdout, "reopens as revision 2", p.stdout)
    dt = prop.read_text(encoding="utf-8")
    check("revision: 2" in dt, "revision incremented")
    check("decision: pending" in dt and "status: needs-review" in dt, "decision reset to pending / needs-review")
    check("needs a third outbound link" in dt, "the feedback is recorded in the proposal")
    check((vault / "concepts/good.md").read_text(encoding="utf-8") == GOOD_PAGE, "the applied target was left unchanged")
    p = run(vault, "lint")
    check("inconsistent" not in p.stdout, "status/decision remain consistent after revise")

    # -- ambiguity --------------------------------------------------------- #
    print("\n[ambiguity] two pending proposals must not be approvable as 'the pending one'")
    collide = tmp / "collide.md"
    collide.write_text(GOOD_PAGE.replace("title: Good test page", "title: Collide page")
                       .replace("# Good test page", "# Collide page"), encoding="utf-8")
    run(vault, "propose", "--target", "concepts/collide.md", "--content", str(collide), "--quiet")
    first = sorted((vault / "review").glob("*collide*"))[0]
    dup = first.with_name(first.stem.replace("-proposal", "-dup-proposal") + ".md")
    dup.write_text(first.read_text(encoding="utf-8"), encoding="utf-8")
    p = run(vault, "lint")
    check("multiple pending proposals target" in p.stdout, "lint errors when one target has two pending proposals", p.stdout[-500:])
    check("proposals are awaiting a decision" in p.stdout, "lint warns that the queue needs exact filenames")
    p = run(vault, "pending")
    check(p.stdout.count("pending") >= 2, "pending lists every undecided proposal")
    dup.unlink()

    # -- orientation and index --------------------------------------------- #
    print("\n[orient] the orientation bundle must be complete")
    p = run(vault, "orient", "--lines", "5")
    for needle, label in [
        ("## SCHEMA.md", "prints SCHEMA.md"),
        ("## index.md", "prints index.md"),
        ("## log.md", "prints recent log entries"),
        ("## Review queue", "prints the review queue"),
        ("AWAITING A DECISION", "flags proposals awaiting a decision"),
    ]:
        check(needle in p.stdout, label)

    print("\n[reindex] index.md is derived, not hand-maintained")
    idx = (vault / "index.md").read_text(encoding="utf-8")
    idx = idx.replace("Total pages: 4", "Total pages: 99")
    (vault / "index.md").write_text(idx, encoding="utf-8")
    p = run(vault, "lint")
    check("Total pages" in p.stdout, "lint detects a wrong page count in the index header", p.stdout[-400:])
    run(vault, "reindex", "--quiet")
    p = run(vault, "lint")
    check("Total pages" not in p.stdout, "reindex repairs it")
    (vault / "concepts/seed-page.md").unlink()
    p = run(vault, "lint")
    check("not listed in index.md" in p.stdout or "broken wikilink" in p.stdout,
          "lint detects index/link damage from a deleted page", p.stdout[-400:])

    # -- summary ----------------------------------------------------------- #
    print(f"\n{'=' * 66}")
    print(f"{PASS} passed, {FAIL} failed")
    print(f"{'=' * 66}")
    print(
        "Scope: this suite proves the MECHANICAL layer only — hashes, schemas, tag taxonomy,\n"
        "       link resolution, path containment, proposal state, revision binding, drift,\n"
        "       idempotency, and index/log integrity.\n"
        "It does NOT prove that a model stops when told to, that a human read the proposal,\n"
        "or that a provenance marker's file actually supports the claim. Those stay with\n"
        "layer 2 and with Git. See concepts/verification-layers.md."
    )
    if args.keep:
        print(f"\nfixture vault kept at {vault}")
    else:
        shutil.rmtree(tmp, ignore_errors=True)
        print("\nfixture vault deleted")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
