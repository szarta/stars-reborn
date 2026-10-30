#!/usr/bin/env python3
"""Generate client-side Python wire types from the JSON Schema source of truth.

The schemas in ``schemas/*.json`` are the single source of truth for the
engine<->client wire contract (see docs/adr/0003). This script regenerates the
committed pydantic models under ``client/src/data/generated/`` from them so the
Python types cannot drift from the schema. The engine's Rust types are generated
separately at build time by ``engine/build.rs`` (typify).

Run it after editing any schema::

    python3 scripts/generate_types.py

The ``generate-python-types`` pre-commit hook and CI run it and fail if the
committed output is stale (``git diff --exit-code``).

Deterministic by design: timestamps are disabled and output is ruff-formatted,
so re-running on an unchanged schema produces a byte-identical file.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO / "schemas"
OUT_DIR = REPO / "client" / "src" / "data" / "generated"

# (schema stem, output module). Grows as more schemas gain client types.
SCHEMAS = [
    ("race", "race.py"),
    ("response-turn-file", "turn_file.py"),
    ("response-game", "universe_file.py"),
    ("response-create-new-game", "create_game.py"),
    ("response-model-ship-hulls", "ship_hulls.py"),
    ("response-model-buildables", "buildables.py"),
    ("response-validate-race", "validate_race.py"),
]

# datamodel-codegen warns that it does not understand the `uint32` integer
# format (added for the Rust generator); the Python fallback to `int` is
# correct, so that one line of noise is filtered out.
_IGNORE_STDERR = re.compile(r"uint32|_get_type|FutureWarning|warn_deprecated")

# The definitions-only root makes datamodel-codegen emit a meaningless
# `class Model(RootModel[Any])`; strip it (ruff then drops the dead imports).
_MODEL_CRUFT = re.compile(
    r"\n\nclass Model\(RootModel\[Any\]\):\n    root: Any\n", re.MULTILINE
)


def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    for line in proc.stderr.splitlines():
        if not _IGNORE_STDERR.search(line):
            print(line, file=sys.stderr)
    if proc.returncode != 0:
        print(proc.stdout, file=sys.stderr)
        sys.exit(proc.returncode)


def generate(stem: str, module: str) -> None:
    out = OUT_DIR / module
    _run(
        [
            "datamodel-codegen",
            "--input",
            str(SCHEMA_DIR / f"{stem}.json"),
            "--input-file-type",
            "jsonschema",
            "--output-model-type",
            "pydantic_v2.BaseModel",
            "--target-python-version",
            "3.11",
            "--use-standard-collections",
            "--use-schema-description",
            "--disable-timestamp",
            "--formatters",
            "ruff-check",
            "ruff-format",
            "--output",
            str(out),
        ]
    )
    text = out.read_text()
    text = _MODEL_CRUFT.sub("\n", text)
    out.write_text(text)
    # Re-run ruff to drop imports the cruft removal orphaned and normalize.
    _run(["ruff", "check", "--fix", "--quiet", str(out)])
    _run(["ruff", "format", "--quiet", str(out)])


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    init = OUT_DIR / "__init__.py"
    if not init.exists():
        init.write_text(
            '"""Wire types generated from ../../../../schemas/*.json.\n\n'
            "Do not edit by hand; run scripts/generate_types.py instead.\n"
            '"""\n'
        )
    for stem, module in SCHEMAS:
        generate(stem, module)
        print(
            f"generated {OUT_DIR.relative_to(REPO)}/{module} from schemas/{stem}.json"
        )


if __name__ == "__main__":
    main()
