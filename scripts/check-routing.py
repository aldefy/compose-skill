#!/usr/bin/env python3
"""Deterministic routing + budget eval for the compose-expert skill.

Checks (no network, no LLM):
  1. orphans   - every references/*.md is routed from SKILL.md
  2. dead      - every references/*.md named in SKILL.md exists
  3. budgets   - SKILL.md and each reference stay under a byte budget
  4. coverage  - every reference is the expected target of >= 1 fixture
  5. routing   - each fixture query in evals/routing.tsv resolves to its
                 expected reference(s) through the Quick Routing table, using a
                 keyword matcher that approximates how a host picks a row.
                 Expected `NONE` means the query is out of scope and must match
                 no row (guards against the skill triggering on everything).

Fixture format (tab separated, `#` comments):  query<TAB>expected[|expected...]

This does not replace the LLM-judged invocation eval; it catches the cheap,
common regressions: forgotten routing rows, orphaned files, bloat, and triggers
that silently stopped matching.
"""
import os
import re
import sys

ROOT = os.environ.get("ROUTING_ROOT") or os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
SKILL = os.path.join(ROOT, "skills", "compose-expert", "SKILL.md")
REFS = os.path.join(ROOT, "skills", "compose-expert", "references")
FIXTURES = os.path.join(ROOT, "evals", "routing.tsv")

SKILL_BUDGET = int(os.environ.get("SKILL_BUDGET", 30000))
REF_BUDGET = int(os.environ.get("REF_BUDGET", 45000))

STOP = {
    "the", "for", "how", "with", "and", "that", "this", "from", "into", "when",
    "what", "why", "does", "can", "use", "using", "make", "build", "add",
    "android", "compose", "jetpack", "app", "apps", "code", "screen", "view",
    "need", "want", "not", "are", "you", "your", "our", "get", "set", "new",
    "migration", "database", "upgrade",
}


def tokens(text):
    return {
        t for t in re.findall(r"[a-z0-9_@.]+", text.lower())
        if len(t) >= 3 and t not in STOP
    }


def load_rows():
    s = open(SKILL, encoding="utf-8").read()
    m = re.search(r"## Quick Routing(.*?)\n# Compose Expert Skill", s, re.S)
    if not m:
        sys.exit("FAIL: could not find '## Quick Routing' section in SKILL.md")
    rows = []
    for line in m.group(1).splitlines():
        r = re.match(r"- \*\*(.+?)\*\*\s*→\s*(.+)$", line)
        if not r:
            continue
        label, rest = r.group(1), r.group(2)
        targets = re.findall(r"references/([A-Za-z0-9_\-]+\.md)", rest)
        phrases = [p.strip().strip("`").lower() for p in label.split(",") if p.strip()]
        rows.append({
            "label": label,
            "targets": targets,
            "phrases": [p for p in phrases if p],
            "tokens": tokens(label),
        })
    return s, rows


def score(row, query):
    q = query.lower()
    qt = tokens(query)
    sc = len(qt & row["tokens"])
    for ph in row["phrases"]:
        if len(ph) >= 4 and ph in q:
            sc += 3
    return sc


def main():
    failures = []
    s, rows = load_rows()
    ref_files = sorted(f for f in os.listdir(REFS) if f.endswith(".md"))

    # 1. orphans
    for f in ref_files:
        if f"references/{f}" not in s:
            failures.append(f"orphan reference (not routed from SKILL.md): {f}")

    # 2. dead links
    for f in sorted(set(re.findall(r"references/([A-Za-z0-9_\-]+\.md)", s))):
        if f not in ref_files:
            failures.append(f"SKILL.md names missing reference: {f}")

    # 3. budgets
    size = os.path.getsize(SKILL)
    if size > SKILL_BUDGET:
        failures.append(f"SKILL.md is {size} bytes (budget {SKILL_BUDGET})")
    for f in ref_files:
        sz = os.path.getsize(os.path.join(REFS, f))
        if sz > REF_BUDGET:
            failures.append(f"references/{f} is {sz} bytes (budget {REF_BUDGET})")

    # 4/5. fixtures
    fixtures = []
    if not os.path.exists(FIXTURES):
        failures.append("evals/routing.tsv is missing")
    else:
        for n, line in enumerate(open(FIXTURES, encoding="utf-8"), 1):
            line = line.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 2:
                failures.append(f"routing.tsv:{n}: expected 'query<TAB>expected'")
                continue
            fixtures.append((n, parts[0].strip(), set(parts[1].strip().split("|"))))

    covered = set()
    for n, query, expected in fixtures:
        scored = [(score(r, query), r) for r in rows]
        best = max((sc for sc, _ in scored), default=0)
        if expected == {"NONE"}:
            if best > 0:
                top = [r["label"] for sc, r in scored if sc == best][:2]
                failures.append(f"routing.tsv:{n}: out-of-scope query matched a row: {query!r} -> {top}")
            continue
        covered |= expected
        if best == 0:
            failures.append(f"routing.tsv:{n}: no row matched: {query!r} (expected {sorted(expected)})")
            continue
        top_targets = set()
        for sc, r in scored:
            if sc == best:
                top_targets |= set(r["targets"])
        if not (expected & top_targets):
            failures.append(
                f"routing.tsv:{n}: {query!r} routed to {sorted(top_targets)}, expected {sorted(expected)}"
            )

    for f in ref_files:
        if f not in covered:
            failures.append(f"no routing fixture targets references/{f}")

    if failures:
        print("ROUTING EVAL FAILED")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    print(
        f"OK: {len(fixtures)} fixtures, {len(rows)} routing rows, "
        f"{len(ref_files)} references, SKILL.md {size}/{SKILL_BUDGET} bytes"
    )


if __name__ == "__main__":
    main()
