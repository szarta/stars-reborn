#!/usr/bin/env python3
"""Check that confirmed figures in the design docs match their pinned values.

WHY THIS EXISTS

Game and research figures (hab ranges, starting population, design caps, …)
are confirmed once, from the oracle or community sources, and then quoted in
prose across several design docs. A quoted number goes stale silently: nothing
re-derives it when the confirmed value is refined, and the same figure often
appears in several files, so the copies drift apart unnoticed. This is the same
failure the schema→types pipeline (ADR-0003) removes for the wire contract, and
the same shape aurora-lint's check_project_facts.py guards for its rule counts.

WHAT IT CHECKS

docs/project_facts.json pins each such figure as the single source of truth: an
exact value plus the regex patterns and target docs where it appears. For every
pin, every match of its patterns in its target docs must equal the pinned value
— a doc quoting a different number fails, naming the file and line. Each pin
must also match at least once, so a reworded doc that drops the figure fails
loudly rather than leaving a dead pin that silently guards nothing.

SCOPE, DELIBERATELY NARROW

This checks prose against a human-curated pin list; it does not itself measure
anything. The pinned value is the confirmed finding — update the pin (and cite
the finding) when the confirmed value changes; the docs then have to follow,
which is the point. It intentionally does not try to recompute a figure from
research data: that path is the research findings, not this file.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
FACTS = DOCS / "project_facts.json"


def load_facts() -> list[dict]:
    return json.loads(FACTS.read_text())["facts"]


def line_of(text: str, offset: int) -> int:
    """1-based line number of a match offset in `text`."""
    return text.count("\n", 0, offset) + 1


def evaluate(facts: list[dict], docs_dir: Path) -> tuple[list[str], list[str], int]:
    """Pure core: returns (stale, dead, checked) for `facts` against `docs_dir`.
    `stale` is figures whose text disagrees with the pin; `dead` is pins that
    matched nothing (or whose target is missing)."""
    stale: list[str] = []
    dead: list[str] = []
    checked = 0

    for fact in facts:
        fact_id = fact["id"]
        expect = fact["value"]
        hits = 0
        for rel in fact["targets"]:
            path = docs_dir / rel
            if not path.is_file():
                dead.append(f"{fact_id}: target docs/{rel} does not exist")
                continue
            text = path.read_text()
            for pattern in fact["patterns"]:
                for m in re.finditer(pattern, text):
                    checked += 1
                    hits += 1
                    got = m.group(1)
                    if got != expect:
                        stale.append(
                            f"  docs/{rel}:{line_of(text, m.start())}  "
                            f"{fact_id} says {got!r}, pinned value is {expect!r}"
                        )
        if hits == 0:
            dead.append(
                f"{fact_id}: no target doc matched any pattern — the figure was "
                f"reworded or removed. Update the pattern or drop the pin in "
                f"docs/project_facts.json."
            )
    return stale, dead, checked


def check() -> int:
    pins = load_facts()
    stale, dead, checked = evaluate(pins, DOCS)

    if stale or dead:
        if stale:
            print(f"{len(stale)} stale figure(s) vs docs/project_facts.json:\n")
            print("\n".join(stale))
            print(
                "\nThe pin is the source of truth. Fix the doc, or update the "
                "pin if the confirmed value changed (and cite the finding)."
            )
        if dead:
            print("\n" + "\n".join(dead))
        return 1

    print(
        f"{checked} figure(s) across {len(pins)} pin(s): all match "
        f"docs/project_facts.json"
    )
    return 0


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    return check()


if __name__ == "__main__":
    sys.exit(main())
