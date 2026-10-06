#!/usr/bin/env python3
"""wiki_tool.py — deterministic tooling for an LLM Wiki vault.

Layer 3 (Verification) of the four-layer model described in
raw/articles/llm-wiki-review-companion-guide.md. It mechanically enforces the subset of
SCHEMA.md that can be checked without judgment: raw-body hashes, frontmatter schemas, tag
taxonomy, wikilink resolution, path containment, provenance-marker resolution, review
proposal state and revision binding, index completeness, log format.

It deliberately does NOT try to judge whether a claim is true, whether a provenance marker
points at a source that actually supports the claim, or whether a human reviewer paid
attention. Those stay with the model and the human. See concepts/verification-layers.md.

Commands
  orient                        Print the orientation bundle (SCHEMA + index + recent log).
  hash FILE                     Print the SHA-256 of a raw file's body (frontmatter stripped).
  verify                        Recompute every raw/ hash and report mismatches.
  capture --url U --dest REL    Fetch and store a raw capture with hash frontmatter.
  capture --file F --dest REL   Store a local file as a raw capture.
  reindex                       Rebuild index.md from compiled page frontmatter.
  lint [--json] [--strict]      Run all checks. Exit 1 on errors (or on warnings if --strict).
  pending                       List review/ proposals that are not yet decided.
  propose ...                   Create a schema-validated review proposal.
  apply PROPOSAL --decision D   Apply a review decision, with revision and drift checks.

Paths are always vault-relative. Nothing writes outside the vault root.

Usage:  python3 tools/wiki_tool.py --wiki /path/to/wiki lint
Environment: WIKI_PATH overrides the default vault location.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys
import urllib.request

# --------------------------------------------------------------------------- #
# Constants — must stay in sync with wiki/SCHEMA.md
# --------------------------------------------------------------------------- #

COMPILED_DIRS = ("entities", "concepts", "comparisons", "queries", "_meta")
PAGE_TYPES = {"entity", "concept", "comparison", "query", "summary"}
CONFIDENCES = {"high", "medium", "low"}
REQUIRED_PAGE_FIELDS = ("title", "created", "updated", "type", "tags", "sources", "summary")
DECISIONS = {"pending", "approve", "reject", "revise", "defer"}
STATUSES = {"needs-review", "applied", "rejected", "deferred"}
OPERATIONS = {"create", "update", "conflict-resolution"}
ROOT_FILES = {"index", "log", "schema"}
LOG_ACTIONS = {"ingest", "update", "query", "lint", "create", "archive", "delete", "review"}
PROPOSAL_SECTIONS = (
    "# Proposed Wiki change",
    "## What will change",
    "## Proposed content",
    "## Evidence and uncertainty",
    "## Human feedback",
)
PAGE_SPLIT_HINT = 200
LOG_ROTATE_AT = 500
STALE_DAYS = 90

WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")
PROVENANCE_RE = re.compile(r"\^\[([^\]]+)\]")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LOG_ENTRY_RE = re.compile(r"^## \[(\d{4}-\d{2}-\d{2})\] (\w[\w-]*) \| (.+)$")


def today() -> str:
    return dt.date.today().isoformat()


# --------------------------------------------------------------------------- #
# Vault resolution and path safety
# --------------------------------------------------------------------------- #


def resolve_vault(cli_value: str | None) -> pathlib.Path:
    """Locate the vault root: --wiki, then $WIKI_PATH, then ../wiki next to tools/."""
    candidates: list[pathlib.Path] = []
    if cli_value:
        candidates.append(pathlib.Path(cli_value).expanduser())
    if os.environ.get("WIKI_PATH"):
        candidates.append(pathlib.Path(os.environ["WIKI_PATH"]).expanduser())
    candidates.append(pathlib.Path(__file__).resolve().parent.parent / "wiki")
    for c in candidates:
        if (c / "SCHEMA.md").is_file():
            return c.resolve()
    raise SystemExit(
        "error: no vault found. Pass --wiki /path/to/wiki or set WIKI_PATH.\n"
        "  looked in: " + ", ".join(str(c) for c in candidates)
    )


def safe_join(root: pathlib.Path, rel: str) -> pathlib.Path:
    """Join a vault-relative path, refusing escapes, absolutes, and null bytes.

    Returns a resolved path guaranteed to be inside `root`, or raises ValueError.
    Symlinks are resolved, so a symlink pointing outside the vault is caught here.
    """
    if not rel or "\x00" in rel:
        raise ValueError(f"invalid path: {rel!r}")
    p = pathlib.PurePath(rel)
    if p.is_absolute() or (len(p.parts) > 1 and p.parts[0] == os.sep):
        raise ValueError(f"path escapes vault (absolute): {rel!r}")
    if any(part == ".." for part in p.parts):
        raise ValueError(f"path escapes vault (traversal): {rel!r}")
    joined = (root / p).resolve()
    if joined != root and root not in joined.parents:
        raise ValueError(f"path escapes vault (resolved): {rel!r}")
    return joined


# --------------------------------------------------------------------------- #
# Frontmatter: a deliberately small YAML subset parser
# --------------------------------------------------------------------------- #


def split_raw_body(text: str) -> tuple[str, str] | None:
    """Split a raw capture into (frontmatter_block, body).

    Positional, not pattern-based: the body is everything after the SECOND line that is
    exactly '---', minus one leading blank separator line. This is what makes captures of
    files that themselves begin with '---' round-trip correctly (see
    concepts/immutable-raw-layer.md, 'Nested frontmatter').
    """
    if not text.startswith("---\n"):
        return None
    lines = text.split("\n")
    closes = [i for i, ln in enumerate(lines[1:], start=1) if ln.rstrip() == "---"]
    if not closes:
        return None
    end = closes[0]
    fm = "\n".join(lines[: end + 1])
    body = "\n".join(lines[end + 1 :])
    if body.startswith("\n"):  # exactly one blank separator line
        body = body[1:]
    return fm, body


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse the leading YAML-ish frontmatter. Returns (data, body_without_frontmatter).

    Supports: scalars, inline lists [a, b], block lists (- item), and one level of nesting.
    Enough for SCHEMA.md's frontmatter; not a general YAML implementation. Values are
    returned as str | list[str] | dict.
    """
    split = split_raw_body(text)
    if split is None:
        return {}, text
    fm_block, body = split
    data: dict = {}
    key_order: list[str] = []
    current_key: str | None = None
    for raw_line in fm_block.split("\n")[1:-1]:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        if line.startswith("- ") and current_key and indent >= 2:
            data[current_key].append(_scalar(line[2:].strip()))
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        key_order.append(key)
        if val == "":
            data[key] = []  # assume a block list follows; overwritten if a scalar appears
            current_key = key
        elif val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [_scalar(x.strip()) for x in inner.split(",") if x.strip()] if inner else []
            current_key = key
        elif val.startswith("{") and val.endswith("}"):
            data[key] = val
            current_key = key
        else:
            data[key] = _scalar(val)
            current_key = key
    return data, body


def _scalar(v: str):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if v.lower() in ("true", "yes"):
        return True
    if v.lower() in ("false", "no"):
        return False
    if v.lower() in ("null", "~", ""):
        return None
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    return v


def as_list(v) -> list[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v]
    return [str(v)]


def body_sha256(body: str) -> str:
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def normalize_page(text: str) -> str:
    """Canonical form of a compiled page: LF endings, no trailing blank lines, one final LF.

    Every hash of proposed or target content goes through this first. Without it, the
    trailing-newline difference between a file on disk and the same text extracted from a
    proposal fence makes propose() and apply() disagree about the digest, and a legitimate
    approval is refused as 'content changed after review'.
    """
    return text.replace("\r\n", "\n").rstrip("\n") + "\n"


# --------------------------------------------------------------------------- #
# Vault scanning
# --------------------------------------------------------------------------- #


class Page:
    def __init__(self, path: pathlib.Path, root: pathlib.Path):
        self.path = path
        self.rel = path.relative_to(root).as_posix()
        self.stem = path.stem
        self.text = path.read_text(encoding="utf-8")
        self.fm, self.body = parse_frontmatter(self.text)
        self.lines = self.text.count("\n") + 1
        self.wikilinks = [m.group(1).strip() for m in WIKILINK_RE.finditer(self.text)]
        self.markers = [m.group(1).strip() for m in PROVENANCE_RE.finditer(self.text)]


def scan(root: pathlib.Path) -> dict:
    compiled: list[Page] = []
    for d in COMPILED_DIRS:
        base = root / d
        if base.is_dir():
            for p in sorted(base.rglob("*.md")):
                compiled.append(Page(p, root))
    raw: list[Page] = []
    rbase = root / "raw"
    if rbase.is_dir():
        for p in sorted(rbase.rglob("*.md")):
            raw.append(Page(p, root))
    proposals: list[Page] = []
    pbase = root / "review"
    if pbase.is_dir():
        for p in sorted(pbase.rglob("*.md")):
            if p.stem.lower() != "readme":
                proposals.append(Page(p, root))
    stems = {p.stem: p.rel for p in compiled}
    for p in raw + proposals:
        stems.setdefault(p.stem, p.rel)
    for name in ("index.md", "log.md", "SCHEMA.md"):
        if (root / name).is_file():
            stems.setdefault(pathlib.Path(name).stem, name)
    return {
        "root": root,
        "compiled": compiled,
        "raw": raw,
        "proposals": proposals,
        "stems": stems,
        "index": root / "index.md",
        "log": root / "log.md",
        "schema": root / "SCHEMA.md",
    }


def taxonomy_from_schema(schema_path: pathlib.Path) -> set[str]:
    """Read the authoritative tag list out of SCHEMA.md's '## Tag Taxonomy' section."""
    if not schema_path.is_file():
        return set()
    text = schema_path.read_text(encoding="utf-8")
    m = re.search(r"^## Tag Taxonomy\s*$(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return set()
    tags: set[str] = set()
    for line in m.group(1).split("\n"):
        if not line.lstrip().startswith("- "):
            continue
        # Strip markdown emphasis FIRST: in "- **Subject:** model, agent" the colon lives
        # inside the bold marker, and partitioning before stripping yields "** model".
        cleaned = line.lstrip()[2:].replace("**", "").replace("*", "")
        _, _, rest = cleaned.partition(":")
        for tok in re.split(r"[,·]", rest):
            tok = tok.strip().strip("`").strip()
            if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", tok or ""):
                tags.add(tok)
    return tags


def strip_code_fences(text: str) -> str:
    """Remove fenced code blocks so examples don't count as live links or claims."""
    return re.sub(r"```.*?```", "", text, flags=re.S)


def strip_code(text: str) -> str:
    """Remove fenced blocks AND inline code spans.

    Documentation pages legitimately mention `[[wikilinks]]` and `^[raw/path.md]` as
    examples. Those are typography, not live references, so link and marker checks run
    against code-stripped text. Never run this on extracted proposal content — the
    proposed page IS a fenced block, so stripping would erase it.
    """
    return re.sub(r"`[^`\n]+`", "", strip_code_fences(text))


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #


class Report:
    def __init__(self) -> None:
        self.errors: list[tuple[str, str]] = []
        self.warnings: list[tuple[str, str]] = []
        self.info: list[tuple[str, str]] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append((where, msg))

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append((where, msg))

    def note(self, where: str, msg: str) -> None:
        self.info.append((where, msg))

    def dump(self, as_json: bool, strict: bool) -> int:
        if as_json:
            print(
                json.dumps(
                    {
                        "errors": [{"where": w, "msg": m} for w, m in self.errors],
                        "warnings": [{"where": w, "msg": m} for w, m in self.warnings],
                        "info": [{"where": w, "msg": m} for w, m in self.info],
                        "ok": not self.errors and not (strict and self.warnings),
                    },
                    indent=2,
                )
            )
        else:
            for label, items in (
                ("ERROR", self.errors),
                ("WARN", self.warnings),
                ("INFO", self.info),
            ):
                if not items:
                    continue
                print(f"\n{label} ({len(items)})")
                for where, msg in items:
                    print(f"  {where}: {msg}")
            print(
                f"\n{len(self.errors)} error(s), {len(self.warnings)} warning(s), "
                f"{len(self.info)} note(s)."
            )
            if not self.errors and not self.warnings:
                print("Vault is clean.")
        if self.errors:
            return 1
        if strict and self.warnings:
            return 1
        return 0


# --------------------------------------------------------------------------- #
# Lint
# --------------------------------------------------------------------------- #


def cmd_lint(vault: pathlib.Path, args) -> int:
    rep = Report()
    v = scan(vault)
    root = v["root"]
    taxonomy = taxonomy_from_schema(v["schema"])

    if not v["schema"].is_file():
        rep.error("SCHEMA.md", "missing — the vault has no layer-3 contract")
    if not v["index"].is_file():
        rep.error("index.md", "missing")
    if not v["log"].is_file():
        rep.error("log.md", "missing")
    if not taxonomy:
        rep.warn("SCHEMA.md", "no tags parsed from '## Tag Taxonomy'; tag audit skipped")

    # --- required directories ------------------------------------------------
    for d in ("raw/articles", "raw/papers", "raw/transcripts", "raw/assets", *COMPILED_DIRS, "review"):
        if not (root / d).is_dir():
            rep.warn(d + "/", "directory missing (created on demand, but SCHEMA.md declares it)")

    # --- compiled pages ------------------------------------------------------
    inbound: dict[str, int] = {p.stem: 0 for p in v["compiled"]}
    used_tags: set[str] = set()

    for p in v["compiled"]:
        where = p.rel
        fm = p.fm

        if not fm:
            rep.error(where, "no frontmatter — required on every compiled page")
            continue

        for field in REQUIRED_PAGE_FIELDS:
            if field not in fm or fm[field] in (None, ""):
                rep.error(where, f"frontmatter missing required field '{field}'")

        ptype = fm.get("type")
        if ptype is not None and ptype not in PAGE_TYPES:
            rep.error(where, f"type '{ptype}' not in {sorted(PAGE_TYPES)}")

        for df in ("created", "updated"):
            val = fm.get(df)
            if val is not None and not DATE_RE.match(str(val)):
                rep.error(where, f"'{df}' is not YYYY-MM-DD: {val!r}")

        conf = fm.get("confidence")
        if conf is not None and conf not in CONFIDENCES:
            rep.error(where, f"confidence '{conf}' not in {sorted(CONFIDENCES)}")

        if fm.get("contested") is True and not fm.get("contradictions"):
            rep.warn(where, "contested: true but no 'contradictions' list")
        for c in as_list(fm.get("contradictions")):
            if c not in v["stems"]:
                rep.error(where, f"contradictions entry '{c}' resolves to no page")

        tags = as_list(fm.get("tags"))
        if "tags" in fm and not isinstance(fm["tags"], list):
            rep.error(where, "'tags' must be a list (use [] when no tag applies, never omit)")
        used_tags.update(tags)
        if taxonomy:
            for t in tags:
                if t not in taxonomy:
                    rep.error(where, f"tag '{t}' not in the SCHEMA.md taxonomy")

        summary = fm.get("summary")
        if isinstance(summary, str) and len(summary) > 160:
            rep.warn(where, f"summary is {len(summary)} chars; keep <= 160 for index.md")

        # Code-stripped body: documentation examples like `[[wikilinks]]` or
        # `^[raw/path.md]` are typography, not live references.
        body = strip_code(p.text)

        # sources must be raw paths that exist
        sources = as_list(fm.get("sources"))
        if not sources:
            rep.error(where, "no sources listed — every compiled page needs at least one raw source")
        raw_sources = [s for s in sources if s.startswith("raw/")]
        if sources and not raw_sources:
            rep.error(where, f"sources contain no 'raw/' path: {sources} (circular-citation risk)")
        for s in sources:
            try:
                target = safe_join(root, s)
            except ValueError as e:
                rep.error(where, f"source path invalid: {e}")
                continue
            if not target.is_file():
                rep.error(where, f"source '{s}' does not exist in the vault")
        if len(sources) >= 3 and not list(PROVENANCE_RE.finditer(body)):
            rep.warn(where, f"synthesizes {len(sources)} sources but has no ^[raw/...] provenance markers")

        # wikilinks and provenance markers
        links = [m.group(1).strip() for m in WIKILINK_RE.finditer(body)]
        outbound = 0
        for link in links:
            if link == p.stem:
                rep.warn(where, f"self-link [[{link}]] does not count as a cross-reference")
                continue
            if link.startswith("raw/"):
                rep.error(where, f"[[{link}]] points into raw/ — use a ^[...] provenance marker or sources:")
                continue
            if "/" in link:
                rep.error(where, f"[[{link}]] is not a bare stem — wikilinks must be [[stem]]")
                continue
            if link not in v["stems"]:
                rep.error(where, f"broken wikilink [[{link}]]")
                continue
            outbound += 1
            if link in inbound:
                inbound[link] += 1
        if outbound < 2:
            rep.error(where, f"only {outbound} outbound wikilink(s); SCHEMA.md requires >= 2")

        # provenance markers must resolve
        for marker in set(m.group(1).strip() for m in PROVENANCE_RE.finditer(body)):
            if not marker.startswith("raw/"):
                rep.error(where, f"provenance marker ^[{marker}] must point into raw/")
                continue
            try:
                if not safe_join(root, marker).is_file():
                    rep.error(where, f"provenance marker ^[{marker}] does not resolve to a file")
            except ValueError as e:
                rep.error(where, f"provenance marker invalid: {e}")

        if p.lines > PAGE_SPLIT_HINT:
            rep.warn(where, f"{p.lines} lines > {PAGE_SPLIT_HINT}; candidate for splitting")

    # --- orphans -------------------------------------------------------------
    for stem, count in sorted(inbound.items()):
        if count == 0:
            rep.warn(v["stems"].get(stem, stem), "orphan: no inbound wikilinks from any compiled page")

    # --- raw layer -----------------------------------------------------------
    drift = 0
    for p in v["raw"]:
        where = p.rel
        fm = p.fm
        if not fm:
            rep.error(where, "raw capture has no frontmatter (source_url/ingested/sha256 required)")
            continue
        for field in ("source_url", "ingested", "sha256"):
            if not fm.get(field):
                rep.error(where, f"raw frontmatter missing '{field}'")
        stored = str(fm.get("sha256") or "")
        split = split_raw_body(p.text)
        if split:
            actual = body_sha256(split[1])
            if stored and stored != actual:
                drift += 1
                rep.error(
                    where,
                    f"source drift: stored sha256 {stored[:12]}… != recomputed {actual[:12]}… "
                    "(raw/ is immutable — investigate before trusting this capture)",
                )
        if not str(fm.get("ingested", "")).startswith(("19", "20")):
            rep.warn(where, f"'ingested' does not look like a date: {fm.get('ingested')!r}")

    # --- index ---------------------------------------------------------------
    if v["index"].is_file():
        idx_text = strip_code(v["index"].read_text(encoding="utf-8"))
        idx_links = set(m.group(1).strip() for m in WIKILINK_RE.finditer(idx_text))
        for p in v["compiled"]:
            if p.stem not in idx_links:
                rep.error(p.rel, "not listed in index.md (run: wiki_tool.py reindex)")
        for link in idx_links:
            if link not in v["stems"]:
                rep.error("index.md", f"broken wikilink [[{link}]]")
        m = re.search(r"Total pages:\s*(\d+)", idx_text)
        if m and int(m.group(1)) != len(v["compiled"]):
            rep.error(
                "index.md",
                f"header says 'Total pages: {m.group(1)}' but {len(v['compiled'])} compiled pages exist",
            )
        for section, count in _index_section_sizes(idx_text).items():
            if count > 50:
                rep.warn("index.md", f"section '{section}' has {count} entries > 50; split it (SCHEMA.md scaling rule)")
        if len(v["compiled"]) > 200 and not (root / "_meta" / "topic-map.md").is_file():
            rep.warn("_meta/topic-map.md", "more than 200 compiled pages but no topic map")

    # --- log -----------------------------------------------------------------
    if v["log"].is_file():
        log_text = v["log"].read_text(encoding="utf-8")
        entries = [ln for ln in log_text.split("\n") if ln.startswith("## [")]
        for ln in entries:
            m = LOG_ENTRY_RE.match(ln)
            if not m:
                rep.error("log.md", f"malformed entry: {ln[:80]!r} (want '## [YYYY-MM-DD] action | subject')")
            elif m.group(2) not in LOG_ACTIONS:
                rep.error("log.md", f"unknown action '{m.group(2)}' in: {ln[:80]!r}")
        if len(entries) > LOG_ROTATE_AT:
            rep.warn("log.md", f"{len(entries)} entries > {LOG_ROTATE_AT}; rotate to log-YYYY.md")

    # --- review proposals ----------------------------------------------------
    lint_proposals(v, rep)

    # --- quality signals -----------------------------------------------------
    for p in v["compiled"]:
        sources = as_list(p.fm.get("sources"))
        if len(sources) == 1 and p.fm.get("confidence") is None:
            rep.warn(p.rel, "single source and no 'confidence' field — corroborate or set confidence: medium")
        if p.fm.get("confidence") == "low":
            rep.note(p.rel, "confidence: low — review before relying on this page")
        if p.fm.get("contested") is True:
            rep.note(p.rel, "contested: true — unresolved contradiction recorded on this page")
    if drift == 0 and v["raw"]:
        rep.note("raw/", f"all {len(v['raw'])} captures hash-verified")

    return rep.dump(args.json, args.strict)


def _index_section_sizes(text: str) -> dict[str, int]:
    sizes: dict[str, int] = {}
    current = None
    for line in text.split("\n"):
        if line.startswith("## "):
            current = line[3:].strip()
            sizes[current] = 0
        elif current and WIKILINK_RE.search(line) and line.lstrip().startswith("-"):
            sizes[current] += 1
    return sizes


def lint_proposals(v: dict, rep: Report) -> None:
    root = v["root"]
    pending_targets: dict[str, list[str]] = {}
    for p in v["proposals"]:
        where = p.rel
        fm = p.fm
        if fm.get("type") != "llm-wiki-review":
            rep.error(where, f"type must be 'llm-wiki-review', got {fm.get('type')!r}")
        dec = fm.get("decision")
        if dec not in DECISIONS:
            rep.error(where, f"decision {dec!r} not in canonical set {sorted(DECISIONS)}")
        st = fm.get("status")
        if st not in STATUSES:
            rep.error(where, f"status {st!r} not in {sorted(STATUSES)}")
        op = fm.get("operation")
        if op not in OPERATIONS:
            rep.error(where, f"operation {op!r} not in {sorted(OPERATIONS)}")
        rev = fm.get("revision")
        if not isinstance(rev, int) or rev < 1:
            rep.error(where, f"revision must be a positive int, got {rev!r}")

        expected = {"pending": "needs-review", "approve": "applied", "reject": "rejected", "defer": "deferred"}
        if dec in expected and st != expected[dec] and not (dec == "revise" and st == "needs-review"):
            rep.error(where, f"decision '{dec}' is inconsistent with status '{st}' (expected '{expected.get(dec)}')")

        target = fm.get("target")
        if not target:
            rep.error(where, "no 'target'")
        else:
            try:
                safe_join(root, str(target))
                if not str(target).startswith(COMPILED_DIRS):
                    rep.error(where, f"target '{target}' is outside the compiled dirs {COMPILED_DIRS}")
            except ValueError as e:
                rep.error(where, f"target invalid: {e}")
            if dec == "pending":
                pending_targets.setdefault(str(target), []).append(where)

        for s in as_list(fm.get("sources")):
            try:
                if not safe_join(root, s).is_file():
                    rep.error(where, f"source '{s}' does not exist")
            except ValueError as e:
                rep.error(where, f"source invalid: {e}")

        body = strip_code_fences(p.text)
        for section in PROPOSAL_SECTIONS:
            if section not in p.text and section.lstrip("# ").lower() not in body.lower():
                rep.warn(where, f"missing section '{section}'")
        if "## Proposed content" in p.text:
            proposed = _extract_proposed_content(p.text)
            if not proposed.strip():
                rep.error(where, "'## Proposed content' is empty — nothing to review")
            else:
                _validate_proposed(v, rep, where, proposed)
        if not re.search(r"^```\s*$", p.text, re.M) and "## Proposed content" in p.text:
            rep.warn(where, "proposed content should be inside a fenced block so it can be extracted verbatim")

    all_pending = [f for files in pending_targets.values() for f in files]
    if len(all_pending) > 1:
        rep.warn(
            "review/",
            f"{len(all_pending)} proposals are awaiting a decision ({', '.join(sorted(all_pending))}). "
            "Approve by exact filename and revision, never by 'approve the pending one'.",
        )
    for target, files in pending_targets.items():
        if len(files) > 1:
            for f in files:
                rep.error(f, f"multiple pending proposals target '{target}': {', '.join(files)} — an approval would be ambiguous")


def _extract_proposed_content(text: str) -> str:
    """Return the body of the first top-level fenced block under '## Proposed content'.

    Two details matter and are easy to get wrong:

    1. **Fence matching must ignore fences inside the block.** The proposed content is itself
       a markdown page that may contain ``` fences. Only a line that is exactly '```' at
       column 0 closes the block; an indented fence does not.
    2. **Section-end detection must ignore headings inside the block.** Scanning for the next
       '^## ' without suppressing the fenced region returns an empty string, because the
       proposed page's own first heading matches immediately. This bug is silent: the
       proposal looks fine and `apply` reports "nothing to apply".
    """
    lines = text.split("\n")
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == "## Proposed content")
    except StopIteration:
        return ""
    i = start + 1
    while i < len(lines) and not lines[i].startswith("```"):
        i += 1
    if i >= len(lines):
        return ""
    open_fence = lines[i]
    if not re.fullmatch(r"```[^\s`]*", open_fence.strip()):
        return ""
    i += 1
    collected: list[str] = []
    while i < len(lines) and lines[i] != "```":
        collected.append(lines[i])
        i += 1
    # text.split("\n") drops only the final terminator, so joining reproduces the fenced
    # text exactly. Adding a newline here would double it and break the hash round-trip
    # between propose() and apply().
    return "\n".join(collected)


def _validate_proposed(v: dict, rep: Report, where: str, proposed: str) -> None:
    """Validate a proposal's proposed content against SCHEMA.md, before a human sees it."""
    fm, _ = parse_frontmatter(proposed)
    if not fm:
        rep.error(where, "proposed content has no frontmatter — structurally invalid, must not be approved")
        return
    for field in REQUIRED_PAGE_FIELDS:
        if field not in fm or fm[field] in (None, ""):
            rep.error(where, f"proposed content missing required frontmatter field '{field}'")
    if fm.get("type") not in PAGE_TYPES:
        rep.error(where, f"proposed content type {fm.get('type')!r} not in {sorted(PAGE_TYPES)}")
    taxonomy = taxonomy_from_schema(v["schema"])
    for t in as_list(fm.get("tags")):
        if taxonomy and t not in taxonomy:
            rep.error(where, f"proposed content uses tag '{t}' outside the taxonomy")
    for s in as_list(fm.get("sources")):
        try:
            if not safe_join(v["root"], s).is_file():
                rep.error(where, f"proposed content cites missing source '{s}'")
        except ValueError as e:
            rep.error(where, f"proposed content source invalid: {e}")
    links = [m.group(1).strip() for m in WIKILINK_RE.finditer(strip_code_fences(proposed))]
    real = [l for l in links if l in v["stems"] and "/" not in l and not l.startswith("raw/")]
    if len(set(real)) < 2:
        rep.error(where, f"proposed content has {len(set(real))} resolvable outbound wikilinks; SCHEMA.md requires >= 2")
    for l in links:
        if l.startswith("raw/") or "/" in l:
            rep.error(where, f"proposed content has a malformed wikilink [[{l}]]")


# --------------------------------------------------------------------------- #
# hash / verify
# --------------------------------------------------------------------------- #


def cmd_hash(vault: pathlib.Path, args) -> int:
    path = safe_join(vault, args.file)
    if not path.is_file():
        raise SystemExit(f"error: {args.file} not found")
    text = path.read_text(encoding="utf-8")
    split = split_raw_body(text)
    if split is None:
        print(body_sha256(text) + f"  {args.file}  (no frontmatter; hashed whole file)")
        return 0
    fm, body = split
    stored = dict(re.findall(r"^(\w+):\s*(.*)$", fm, re.M)).get("sha256", "")
    actual = body_sha256(body)
    print(actual + f"  {args.file}")
    if stored:
        print(("MATCH  " if stored == actual else "DRIFT  ") + f"stored={stored}")
        return 0 if stored == actual else 1
    return 0


def cmd_verify(vault: pathlib.Path, args) -> int:
    v = scan(vault)
    bad = 0
    for p in v["raw"]:
        split = split_raw_body(p.text)
        if split is None:
            print(f"  ?? {p.rel}: no frontmatter")
            bad += 1
            continue
        stored = str(p.fm.get("sha256") or "")
        actual = body_sha256(split[1])
        ok = stored == actual
        if not ok:
            bad += 1
        print(f"  {'ok' if ok else 'DRIFT'} {p.rel}  {actual[:16]}…")
    print(f"\n{len(v['raw']) - bad}/{len(v['raw'])} raw captures verified.")
    return 1 if bad else 0


# --------------------------------------------------------------------------- #
# capture
# --------------------------------------------------------------------------- #


def _build_capture(body: str, source_url: str, note: str | None) -> str:
    body = body.replace("\r\n", "\n").rstrip("\n") + "\n"
    digest = body_sha256(body)
    fm = ["---", f"source_url: {source_url}", f"ingested: {today()}", f"sha256: {digest}"]
    if note:
        fm.append(f"capture_note: {note}")
    fm.append("---")
    return "\n".join(fm) + "\n\n" + body, digest


def cmd_capture(vault: pathlib.Path, args) -> int:
    dest_rel = args.dest
    if not dest_rel.startswith("raw/"):
        raise SystemExit("error: --dest must be inside raw/ (e.g. raw/articles/foo.md)")
    try:
        dest = safe_join(vault, dest_rel)
    except ValueError as e:
        raise SystemExit(f"error: {e}")
    if dest.exists() and not args.force:
        raise SystemExit(f"error: {dest_rel} already exists. raw/ is immutable; use --force only to replace a bad capture.")
    dest.parent.mkdir(parents=True, exist_ok=True)

    if args.url:
        req = urllib.request.Request(args.url, headers={"User-Agent": "llm-wiki/1.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read().decode("utf-8", errors="replace")
        source_url = args.url
    elif args.file:
        src = pathlib.Path(args.file).expanduser()
        if not src.is_file():
            raise SystemExit(f"error: {src} not found")
        body = src.read_text(encoding="utf-8")
        source_url = args.source_url or f"local-file:{src.name}"
    else:
        body = sys.stdin.read()
        source_url = args.source_url or "stdin"
        if not body.strip():
            raise SystemExit("error: empty capture")

    text, digest = _build_capture(body, source_url, args.note)
    dest.write_text(text, encoding="utf-8")

    # Verify immediately by re-reading from disk and stripping positionally.
    reread = dest.read_text(encoding="utf-8")
    split = split_raw_body(reread)
    if split is None:
        dest.unlink()
        raise SystemExit("error: capture failed its own frontmatter split; file removed")
    recomputed = body_sha256(split[1])
    if recomputed != digest:
        dest.unlink()
        raise SystemExit(f"error: hash verify failed ({digest[:12]} != {recomputed[:12]}); file removed")

    print(f"captured {dest_rel}")
    print(f"  sha256 {digest}")
    print(f"  bytes  {len(split[1].encode('utf-8'))}")
    print("  verify ok (re-read from disk, frontmatter stripped positionally)")
    append_log(vault, "ingest", f"Raw capture {dest_rel}", [f"raw sha256 {digest}"], quiet=args.quiet)
    return 0


# --------------------------------------------------------------------------- #
# reindex
# --------------------------------------------------------------------------- #


SECTION_FOR_TYPE = {
    "entity": "Entities",
    "concept": "Concepts",
    "comparison": "Comparisons",
    "query": "Queries",
    "summary": "Summaries",
}


def build_index(vault: pathlib.Path) -> str:
    v = scan(vault)
    buckets: dict[str, list[Page]] = {}
    for p in v["compiled"]:
        section = SECTION_FOR_TYPE.get(str(p.fm.get("type")), "Other")
        if p.rel.startswith("_meta/"):
            section = "Meta"
        buckets.setdefault(section, []).append(p)

    order = ["Entities", "Concepts", "Comparisons", "Queries", "Summaries", "Meta", "Other"]
    out = [
        "# Wiki Index",
        "",
        "> Content catalog. Every compiled page listed under its type with a one-line summary.",
        "> Read this first to find relevant pages for any query.",
        ">",
        "> **Machine-maintained.** This file is regenerated by `python3 tools/wiki_tool.py reindex`",
        "> from each page's `summary:` frontmatter. Do not hand-edit; edit the page instead.",
        f"> Last updated: {today()} | Total pages: {len(v['compiled'])}",
        "",
        "## Raw sources",
        "",
        f"- {len(v['raw'])} immutable captures in `raw/`. Not listed individually here: every compiled",
        "  page names its own captures in `sources:`, and `wiki_tool.py verify` re-checks all of them.",
        "",
        "## Review queue",
        "",
    ]
    pending = [p for p in v["proposals"] if p.fm.get("decision") == "pending"]
    decided = [p for p in v["proposals"] if p.fm.get("decision") != "pending"]
    if pending:
        for p in sorted(pending, key=lambda x: x.rel):
            out.append(
                f"- [[{p.stem}]] — `{p.fm.get('operation')}` → `{p.fm.get('target')}` "
                f"(rev {p.fm.get('revision')}, **awaiting decision**)"
            )
    else:
        out.append("- No proposals awaiting a decision.")
    if decided:
        out.append("")
        out.append("Decided:")
        for p in sorted(decided, key=lambda x: x.rel):
            out.append(f"- [[{p.stem}]] — `{p.fm.get('decision')}` / `{p.fm.get('status')}` → `{p.fm.get('target')}`")
    out.append("")

    for section in order:
        pages = buckets.get(section)
        if not pages:
            continue
        out += [f"## {section}", "", "<!-- Alphabetical within section -->", ""]
        for p in sorted(pages, key=lambda x: str(x.fm.get("title") or x.stem).lower()):
            summary = str(p.fm.get("summary") or "(no summary field — add one)").strip()
            tags = ", ".join(as_list(p.fm.get("tags")))
            conf = p.fm.get("confidence")
            badge = ""
            if p.fm.get("contested") is True:
                badge += " ⚔️contested"
            if conf in ("low", "medium"):
                badge += f" 🔎confidence:{conf}"
            out.append(f"- [[{p.stem}]] — {summary}")
            out.append(f"  - `{p.rel}` · tags: {tags or '[]'}{badge}")
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def cmd_reindex(vault: pathlib.Path, args) -> int:
    text = build_index(vault)
    index_path = vault / "index.md"
    old = index_path.read_text(encoding="utf-8") if index_path.is_file() else None
    if old == text:
        print("index.md already current; no change.")
        return 0
    index_path.write_text(text, encoding="utf-8")
    v = scan(vault)
    print(f"index.md rebuilt: {len(v['compiled'])} compiled pages, {len(v['proposals'])} proposals.")
    if not args.quiet:
        append_log(vault, "update", "index.md rebuilt by wiki_tool.py reindex", quiet=True)
    return 0


# --------------------------------------------------------------------------- #
# log
# --------------------------------------------------------------------------- #


def append_log(vault: pathlib.Path, action: str, subject: str, bullets: list[str] | None = None, quiet: bool = False) -> None:
    log = vault / "log.md"
    if not log.is_file():
        log.write_text(
            "# Wiki Log\n\n"
            "> Chronological record of all wiki actions. Append-only.\n"
            "> Format: `## [YYYY-MM-DD] action | subject`\n"
            f"> Actions: {', '.join(sorted(LOG_ACTIONS))}\n"
            f"> When this file exceeds {LOG_ROTATE_AT} entries, rotate: rename to log-YYYY.md, start fresh.\n\n",
            encoding="utf-8",
        )
    lines = [f"## [{today()}] {action} | {subject}"]
    lines += [f"- {b}" for b in (bullets or [])]
    with log.open("a", encoding="utf-8") as fh:
        fh.write("\n" + "\n".join(lines) + "\n")
    if not quiet:
        print(f"logged: [{today()}] {action} | {subject}")


def rotate_log_if_needed(vault: pathlib.Path) -> bool:
    log = vault / "log.md"
    if not log.is_file():
        return False
    text = log.read_text(encoding="utf-8")
    entries = [ln for ln in text.split("\n") if ln.startswith("## [")]
    if len(entries) <= LOG_ROTATE_AT:
        return False
    year = today()[:4]
    archive = vault / f"log-{year}.md"
    archive.write_text(text, encoding="utf-8")
    head = text.split("\n## [")[0]
    log.write_text(head + "\n", encoding="utf-8")
    print(f"log.md rotated: {len(entries)} entries moved to {archive.name}")
    return True


# --------------------------------------------------------------------------- #
# review: pending / propose / apply
# --------------------------------------------------------------------------- #


def cmd_pending(vault: pathlib.Path, args) -> int:
    v = scan(vault)
    rows = []
    for p in v["proposals"]:
        rows.append(
            {
                "proposal": p.rel,
                "target": p.fm.get("target"),
                "operation": p.fm.get("operation"),
                "revision": p.fm.get("revision"),
                "decision": p.fm.get("decision"),
                "status": p.fm.get("status"),
            }
        )
    if args.json:
        print(json.dumps(rows, indent=2))
        return 0
    if not rows:
        print("No proposals in review/.")
        return 0
    pending = [r for r in rows if r["decision"] == "pending"]
    width = max((len(str(r["proposal"])) for r in rows), default=10)
    for r in rows:
        mark = "**" if r["decision"] == "pending" else "  "
        print(
            f"{mark}{r['proposal']:<{width}}  rev {r['revision']}  {str(r['decision']):<8} "
            f"{str(r['status']):<12} {r['operation']:<19} -> {r['target']}"
        )
    print(f"\n{len(pending)} awaiting a decision, {len(rows) - len(pending)} decided.")
    if pending:
        print("Silence and elapsed time are never approval — reply with a decision or set 'decision:' and say 'Continue the pending Wiki review.'")
    return 0


def cmd_propose(vault: pathlib.Path, args) -> int:
    content_path = pathlib.Path(args.content).expanduser()
    if not content_path.is_file():
        raise SystemExit(f"error: content file {args.content} not found")
    proposed = content_path.read_text(encoding="utf-8")

    target_rel = args.target
    try:
        target_abs = safe_join(vault, target_rel)
    except ValueError as e:
        raise SystemExit(f"error: refusing proposal — {e}")
    if not target_rel.startswith(COMPILED_DIRS):
        raise SystemExit(f"error: target '{target_rel}' is outside the compiled dirs {COMPILED_DIRS}")

    # Validate BEFORE a human ever sees it. Never ask for approval of invalid content.
    rep = Report()
    v = scan(vault)
    fm, _ = parse_frontmatter(proposed)
    _validate_proposed(v, rep, "proposed content", proposed)
    if rep.errors:
        print("Refusing to create the proposal — proposed content is structurally invalid:")
        for where, msg in rep.errors:
            print(f"  {where}: {msg}")
        print("\nFix the content and re-run. No proposal file was written.")
        return 1

    stem = target_abs.stem
    date = args.date or today()
    proposal_rel = f"review/{date}-{stem}-proposal.md"
    try:
        proposal_abs = safe_join(vault, proposal_rel)
    except ValueError as e:
        raise SystemExit(f"error: {e}")

    revision = 1
    if proposal_abs.exists():
        existing_fm, _ = parse_frontmatter(proposal_abs.read_text(encoding="utf-8"))
        if args.operation == "revise" or existing_fm.get("decision") in ("revise", "pending"):
            revision = int(existing_fm.get("revision") or 1) + 1
            archive = proposal_abs.with_name(f"{proposal_abs.stem}.rev{existing_fm.get('revision') or 1}.md")
            proposal_abs.rename(archive)
            print(f"previous revision preserved at {archive.relative_to(vault)}")
        else:
            raise SystemExit(f"error: {proposal_rel} already exists with decision '{existing_fm.get('decision')}'. Use a revise flow.")

    operation = args.operation
    if operation == "create" and target_abs.exists():
        operation = "update"
        print(f"note: target already exists; operation set to 'update'")
    sources = args.sources or as_list(fm.get("sources"))
    if not sources:
        raise SystemExit("error: no sources — pass --sources raw/a.md,raw/b.md or list them in the content frontmatter")

    front = [
        "---",
        "type: llm-wiki-review",
        "status: needs-review",
        "decision: pending",
        f"revision: {revision}",
        f"operation: {operation}",
        f"target: {target_rel}",
        f"created: {today()}",
        f"updated: {today()}",
        "sources:",
    ] + [f"  - {s}" for s in sources] + [
        f"target_exists: {'true' if target_abs.exists() else 'false'}",
        f"target_sha256: {body_sha256(normalize_page(target_abs.read_text(encoding='utf-8'))) if target_abs.exists() else 'null'}",
        f"proposed_sha256: {body_sha256(normalize_page(proposed))}",
        "---",
    ]
    body = [
        "",
        "# Proposed Wiki change",
        "",
        "## What will change",
        "",
        args.what or f"{'Create' if operation == 'create' else 'Update'} `{target_rel}` (revision {revision}).",
        "",
        "## Proposed content",
        "",
        "```markdown",
        proposed if proposed.endswith("\n") else proposed + "\n",
        "```",
        "",
        "## Evidence and uncertainty",
        "",
        args.evidence or "Supporting sources are listed in frontmatter. Uncertainty: (fill in before review.)",
        "",
        "## Human feedback",
        "",
    ]
    if operation == "conflict-resolution":
        body += [
            "Choose one:",
            "",
            "- **Keep both:** approve this proposal — both claims are preserved and the topic is marked contested.",
            "- **Not a contradiction:** revise it to preserve compatible or context-dependent claims without `contested`, then stop for approval again.",
            "- **Decide later:** defer without changing compiled content.",
            "",
            "Advanced: revise — prefer a source or supply a custom resolution. Requires a reason or stronger evidence. Never silently select a winner.",
            "",
        ]
    else:
        body += [
            "Choose one: `approve` · `reject` · `revise` · `defer`",
            "",
            "Or set `decision:` in the frontmatter above, then tell the agent: \"Continue the pending Wiki review.\"",
            "Editing this note alone does not trigger anything. Silence and elapsed time are never approval.",
            "",
        ]
    proposal_abs.parent.mkdir(parents=True, exist_ok=True)
    proposal_abs.write_text("\n".join(front + body).rstrip() + "\n", encoding="utf-8")

    print(f"proposal written: {proposal_rel}")
    print(f"  target     {target_rel} ({operation})")
    print(f"  revision   {revision}")
    print(f"  proposed   sha256 {body_sha256(normalize_page(proposed))[:16]}… (canonical form)")
    print("  schema     validated against SCHEMA.md (frontmatter, tags, sources, >=2 wikilinks)")
    print("\nSTOPPED. No compiled page was created or changed.")
    append_log(vault, "review", f"Proposal {proposal_rel} created", [f"target {target_rel}", f"operation {operation}", f"revision {revision}", "status needs-review — awaiting human decision"], quiet=args.quiet)
    return 0


def cmd_apply(vault: pathlib.Path, args) -> int:
    """Apply a review decision.

    Check order matters and is deliberate. Cheapest and most fundamental first:

      1. Does the proposal exist, and is it in a state that can be decided at all?
         A terminal proposal cannot be silently re-decided, and 'pending' is not a decision.
      2. Is this the revision the human actually reviewed?
      3. Does the target still exist where the proposal says, inside the vault?
      4. Has the target drifted since review?
      5. Do all cited raw captures still hash-verify?
      6. Is the proposed content still structurally valid against SCHEMA.md?
      7. Is the proposed content byte-identical to what the human reviewed?

    Every one of these must pass before a single byte is written. Any failure exits
    non-zero with the vault untouched — a refusal must produce a zero-byte delta.
    """
    proposal_rel = args.proposal if args.proposal.startswith("review/") else f"review/{args.proposal}"
    try:
        path = safe_join(vault, proposal_rel)
    except ValueError as e:
        raise SystemExit(f"error: {e}")
    if not path.is_file():
        raise SystemExit(f"error: proposal {proposal_rel} not found")

    text = path.read_text(encoding="utf-8")
    fm, _ = parse_frontmatter(text)

    # ---- 1. decision and proposal state ---------------------------------- #
    decision = args.decision or str(fm.get("decision") or "")
    if decision not in DECISIONS:
        raise SystemExit(f"error: decision {decision!r} not in {sorted(DECISIONS)}")
    if decision == "pending":
        raise SystemExit(
            "error: decision 'pending' is not an application. Silence and elapsed time are never approval.\n"
            "       Pass --decision approve|reject|revise|defer, or set 'decision:' in the proposal\n"
            "       and re-run. Nothing was written."
        )

    current_status = str(fm.get("status") or "")
    current_decision = str(fm.get("decision") or "")
    revision = int(fm.get("revision") or 0)
    target_rel = str(fm.get("target") or "")

    if current_status in ("applied", "rejected", "deferred"):
        if decision == current_decision:
            # Idempotent replay of a completed operation: report, change nothing, log nothing.
            print(f"already {current_status}: {proposal_rel} (revision {revision}) — nothing to do.")
            print("A repeated request produces a zero-byte delta and no duplicate log entry.")
            return 0
        if decision == "revise" and current_status == "applied":
            # Legitimate revival — but it becomes a NEW pending revision, never a write.
            revived = _set_frontmatter_field(text, "status", "needs-review")
            revived = _set_frontmatter_field(revived, "decision", "pending")
            revived = _set_frontmatter_field(revived, "revision", str(revision + 1))
            revived = _set_frontmatter_field(revived, "updated", today())
            if args.feedback:
                revived = revived.rstrip("\n") + f"\n\n### Revision feedback ({today()})\n\n{args.feedback.strip()}\n"
            path.write_text(revived, encoding="utf-8")
            append_log(
                vault, "review", f"revise | {proposal_rel}",
                [f"applied revision {revision} reopened as pending revision {revision + 1}",
                 f"target {target_rel} left unchanged"], quiet=args.quiet,
            )
            print(f"revision {revision} was already applied; reopened as pending revision {revision + 1}.")
            print(f"  target unchanged: {target_rel}")
            print("  STOPPED. The new revision needs its own decision before anything is written.")
            return 0
        raise SystemExit(
            f"error: {proposal_rel} is already '{current_status}' (decision '{current_decision}').\n"
            f"       refusing to apply '{decision}' to a decided proposal.\n"
            f"       A new decision requires a new revision that a human reviews:\n"
            f"         wiki_tool.py propose --target {target_rel} --content <revised page> --operation {fm.get('operation')}\n"
            f"       Never apply an approval to a revision the human did not review."
        )

    # ---- 2. revision binding --------------------------------------------- #
    if args.revision is not None and args.revision != revision:
        raise SystemExit(
            f"error: you asked to apply revision {args.revision}, but the current proposal is revision {revision}.\n"
            "Never apply an approval to a different revision from the one the human reviewed."
        )

    # ---- 3. target containment ------------------------------------------- #
    try:
        target_abs = safe_join(vault, target_rel)
    except ValueError as e:
        raise SystemExit(f"error: refusing to apply — target invalid: {e}")
    if not target_rel.startswith(COMPILED_DIRS):
        raise SystemExit(f"error: refusing to apply — target '{target_rel}' is outside {COMPILED_DIRS}")

    # ---- 4. target drift -------------------------------------------------- #
    recorded = str(fm.get("target_sha256") or "")
    if target_abs.exists() and recorded and recorded != "null":
        actual = body_sha256(normalize_page(target_abs.read_text(encoding="utf-8")))
        if actual != recorded:
            raise SystemExit(
                f"error: target drift. '{target_rel}' changed after this proposal was reviewed\n"
                f"  recorded {recorded[:16]}…  actual {actual[:16]}…\n"
                "Create a new proposal revision against the current target. Nothing was written."
            )

    # ---- 5. raw source drift ---------------------------------------------- #
    v = scan(vault)
    raw_by_rel = {p.rel: p for p in v["raw"]}
    for src in as_list(fm.get("sources")):
        rp = raw_by_rel.get(src)
        if rp is None:
            raise SystemExit(f"error: cited source '{src}' is missing from raw/; refusing to apply")
        split = split_raw_body(rp.text)
        if split and str(rp.fm.get("sha256") or "") != body_sha256(split[1]):
            raise SystemExit(f"error: raw source drift in '{src}' (hash mismatch); refusing to apply")

    # ---- 6. schema revalidation ------------------------------------------- #
    proposed = _extract_proposed_content(text)
    if not proposed.strip():
        raise SystemExit("error: proposal has no extractable '## Proposed content' block; nothing to apply")
    rep = Report()
    _validate_proposed(v, rep, proposal_rel, proposed)
    if rep.errors:
        print("Refusing to apply — proposed content is now structurally invalid:")
        for where, msg in rep.errors:
            print(f"  {where}: {msg}")
        print("Create a corrected proposal revision and request review again. Nothing was written.")
        return 1

    # ---- 7. content binding ------------------------------------------------ #
    proposed_norm = normalize_page(proposed)
    proposed_digest = body_sha256(proposed_norm)
    recorded_proposed = str(fm.get("proposed_sha256") or "")
    if recorded_proposed and recorded_proposed != proposed_digest:
        raise SystemExit(
            f"error: the proposal's content changed after review (recorded {recorded_proposed[:16]}…, "
            f"now {proposed_digest[:16]}…). Never apply content the human did not review."
        )

    if args.dry_run:
        print(f"[dry-run] all checks passed; would apply '{decision}' to '{target_rel}' (revision {revision})")
        return 0

    # ---- apply ------------------------------------------------------------- #
    if decision == "approve":
        target_abs.parent.mkdir(parents=True, exist_ok=True)
        target_abs.write_text(proposed_norm, encoding="utf-8")
        new_status, new_decision = "applied", "approve"
        bullets = [f"target {target_rel} written from revision {revision}",
                   f"proposed sha256 {proposed_digest}",
                   "applied bytes verified identical to the reviewed proposal block"]
    elif decision == "reject":
        new_status, new_decision = "rejected", "reject"
        bullets = [f"target {target_rel} left unchanged — no compiled mutation"]
    elif decision == "defer":
        new_status, new_decision = "deferred", "defer"
        bullets = [f"target {target_rel} left unchanged — no compiled mutation"]
    else:  # revise
        new_status, new_decision = "needs-review", "revise"
        bullets = [f"target {target_rel} left unchanged",
                   "a new proposal revision is required, and its own decision, before any write"]
        if not args.feedback:
            print("note: revise without --feedback records the intent only; supply the feedback so the next revision can incorporate it.")

    updated = _set_frontmatter_field(text, "status", new_status)
    updated = _set_frontmatter_field(updated, "decision", new_decision)
    updated = _set_frontmatter_field(updated, "updated", today())
    updated = _set_frontmatter_field(updated, "applied_revision", str(revision))
    if args.feedback:
        heading = "Revision feedback" if decision == "revise" else "Human feedback"
        updated = updated.rstrip("\n") + f"\n\n### {heading} ({today()})\n\n{args.feedback.strip()}\n"
    path.write_text(updated, encoding="utf-8")

    append_log(vault, "review", f"{decision} | {proposal_rel}", bullets, quiet=args.quiet)
    print(f"decision '{decision}' applied to {proposal_rel} (revision {revision})")
    print(f"  status {new_status}")
    if decision == "approve":
        cmd_reindex(vault, argparse.Namespace(quiet=True))
        append_log(vault, "update", f"index.md rebuilt after approved write to {target_rel}", quiet=True)
        rotate_log_if_needed(vault)
        print("  post-write maintenance: index.md rebuilt, log appended, log-rotation checked")
        print("  next: run 'wiki_tool.py lint' — a new page is an orphan until something links to it")
    else:
        print(f"  target unchanged: {target_rel}")
    return 0


def _set_frontmatter_field(text: str, key: str, value: str) -> str:
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text
    end = next((i for i, ln in enumerate(lines[1:], start=1) if ln.rstrip() == "---"), None)
    if end is None:
        return text
    for i in range(1, end):
        if re.match(rf"^{re.escape(key)}:", lines[i]):
            lines[i] = f"{key}: {value}"
            return "\n".join(lines)
    lines.insert(end, f"{key}: {value}")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# orient
# --------------------------------------------------------------------------- #


def cmd_orient(vault: pathlib.Path, args) -> int:
    """Print the session-orientation bundle the built-in skill requires before any operation."""
    print(f"# Orientation — {vault}\n")
    for name in ("SCHEMA.md", "index.md"):
        p = vault / name
        print(f"\n{'=' * 72}\n## {name}\n{'=' * 72}\n")
        print(p.read_text(encoding="utf-8") if p.is_file() else f"(missing {name})")
    log = vault / "log.md"
    print(f"\n{'=' * 72}\n## log.md — last {args.lines} entry lines\n{'=' * 72}\n")
    if log.is_file():
        entries = [ln for ln in log.read_text(encoding="utf-8").split("\n") if ln.startswith("## [")]
        print(f"({len(entries)} total entries)")
        for ln in entries[-args.lines :]:
            print(ln)
    else:
        print("(missing log.md)")
    v = scan(vault)
    pend = [p for p in v["proposals"] if p.fm.get("decision") == "pending"]
    print(f"\n{'=' * 72}\n## Review queue\n{'=' * 72}")
    print(f"{len(v['raw'])} raw captures · {len(v['compiled'])} compiled pages · {len(v['proposals'])} proposals")
    if pend:
        print(f"{len(pend)} AWAITING A DECISION:")
        for p in pend:
            print(f"  {p.rel}  rev {p.fm.get('revision')}  -> {p.fm.get('target')}")
    else:
        print("Nothing awaiting a decision.")
    return 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="wiki_tool.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wiki", help="vault root (default: $WIKI_PATH, then ../wiki next to tools/)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("orient", help="print the session orientation bundle")
    s.add_argument("--lines", type=int, default=30, help="how many log entries to show (default 30)")
    s.set_defaults(func=cmd_orient)

    s = sub.add_parser("hash", help="print a raw file's body SHA-256 and compare to the stored value")
    s.add_argument("file")
    s.set_defaults(func=cmd_hash)

    s = sub.add_parser("verify", help="recompute every raw/ hash and report drift")
    s.set_defaults(func=cmd_verify)

    s = sub.add_parser("capture", help="store a URL, file, or stdin as a hash-verified raw capture")
    s.add_argument("--url")
    s.add_argument("--file")
    s.add_argument("--dest", required=True, help="vault-relative path inside raw/")
    s.add_argument("--source-url", help="origin to record when capturing a local file or stdin")
    s.add_argument("--note", help="capture_note: state this when the body is not byte-exact")
    s.add_argument("--force", action="store_true", help="replace an existing capture (raw/ is normally immutable)")
    s.add_argument("--quiet", action="store_true", help="do not append to log.md")
    s.set_defaults(func=cmd_capture)

    s = sub.add_parser("reindex", help="rebuild index.md from compiled page frontmatter")
    s.add_argument("--quiet", action="store_true")
    s.set_defaults(func=cmd_reindex)

    s = sub.add_parser("lint", help="run all mechanical checks")
    s.add_argument("--json", action="store_true")
    s.add_argument("--strict", action="store_true", help="exit non-zero on warnings too")
    s.set_defaults(func=cmd_lint)

    s = sub.add_parser("pending", help="list review proposals and their decisions")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_pending)

    s = sub.add_parser("propose", help="create a schema-validated review proposal, then stop")
    s.add_argument("--target", required=True, help="vault-relative compiled page to create/update")
    s.add_argument("--content", required=True, help="file holding the exact proposed page content")
    s.add_argument("--sources", help="comma-separated raw/ paths (default: from content frontmatter)")
    s.add_argument("--operation", choices=sorted(OPERATIONS), default="create")
    s.add_argument("--what", help="'What will change' text")
    s.add_argument("--evidence", help="'Evidence and uncertainty' text")
    s.add_argument("--date", help="override the proposal date (YYYY-MM-DD)")
    s.add_argument("--quiet", action="store_true")
    s.set_defaults(func=cmd_propose)

    s = sub.add_parser("apply", help="apply a review decision with revision, drift, and schema checks")
    s.add_argument("proposal", help="proposal path or filename inside review/")
    s.add_argument("--decision", choices=sorted(DECISIONS - {"pending"}), help="default: read from the proposal's frontmatter")
    s.add_argument("--revision", type=int, help="the revision the human actually reviewed; refuses on mismatch")
    s.add_argument("--feedback", help="human feedback to record (required in spirit for 'revise')")
    s.add_argument("--dry-run", action="store_true")
    s.add_argument("--quiet", action="store_true")
    s.set_defaults(func=cmd_apply)

    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "capture" and args.dest and not args.dest.startswith("raw/"):
        pass  # validated inside cmd_capture with a clearer message
    vault = resolve_vault(getattr(args, "wiki", None))
    return args.func(vault, args)


if __name__ == "__main__":
    sys.exit(main())
