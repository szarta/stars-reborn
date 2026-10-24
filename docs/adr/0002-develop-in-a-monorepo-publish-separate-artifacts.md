# 0002: Develop in one monorepo; publish separate artifacts

**Status:** Accepted, 2026-10-22.

## Context

The project began as several repositories — one each for the engine, the
reference client, the JSON Schema contract, the design docs, and an
integration repo that pulled the others in as submodules. The split was meant
to mirror the runtime separation between client, engine, and the shared
contract.

In practice the repository boundary was paying for a separation that the
architecture already enforces at runtime (ADR-0001), while charging a real
cost:

- A single logical change to the contract — add a field to a schema, emit it
  from the engine, consume it in the client — required coordinated commits
  across three repositories, with no one place to review the change whole, and
  with version skew possible between them in the meantime.
- The guardrails (pre-commit config, CI, commit policy, agent instructions)
  had to be copied into every repository and then drifted out of sync, which
  is the exact failure the "one copy of the rules" practice exists to prevent.
- With the work split across repositories, all of them went cold at once and
  each was left a commit or two short of done; the split made the whole harder
  to pick back up, not easier.

## Decision

Develop the clone in **one monorepo** (`engine/`, `client/`, `schemas/`,
`docs/`, `packaging/`) with a single guardrail layer, and **publish separate
artifacts** from it so the runtime separation is preserved where it matters:

- the engine/host binary,
- the reference client application,
- the versioned schema package that third-party clients and both components
  consume.

The runtime boundary stays exactly as in ADR-0001; only the source
organization changes. Independent release cadence comes from per-component
release tags, not from separate source trees.

Two components stay out of the monorepo on purpose: `stars_file_parser`, a
standalone library useful to anyone studying the original game's file formats,
and the private experiment-scripting repo. Research data and experiments are
not checked in.

History from the original repositories was preserved on migration (each
rewritten under its subdirectory), and the superseded repositories are
archived read-only with a pointer here.

## Consequences

- A contract change is one commit, one review, one CI run that builds producer
  and consumer against the schema together.
- There is one `.pre-commit-config.yaml`, one `AGENTS.md`/`CLAUDE.md`, and one
  `docs/adr/` — the rules have a single home.
- A later step can **generate** the Rust and Python types from the JSON Schema
  so the contract cannot drift between the two languages; until then the schema
  is the single source of truth by convention.
- Formatting in this repo uses rustfmt and ruff for Rust and Python and
  `moldy` for the neutral formats (JSON/YAML/Markdown) plus reStructuredText
  (`docs/*.rst`). RST was A/B-tested against the existing docs and adopted with
  the authored conventions preserved (underline headings, bullet style, two-
  space sentence gaps); its settings live in `moldy-rst.toml` and it runs on a
  separate `moldy-rst` pre-commit hook because RST support is still an
  unreleased moldy branch build. Moving Rust and Python onto `moldy` as well is
  a deliberate, separately A/B-tested change still to come, not part of this.
