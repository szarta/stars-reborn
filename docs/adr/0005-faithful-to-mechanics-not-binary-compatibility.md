# 0005: Faithful to the original's mechanics and feel, not its binary files

**Status:** Accepted, 2026-11-04.

## Context

Stars! (1995/96) is effectively unplayable on modern systems: it is a 16-bit
Windows program and that runtime support has all but disappeared. Stars Reborn
exists so that someone who played the original can open this and say "I know how
to play this — it is the spiritual successor to a game I can no longer run."

That goal needs a sharp line, because "faithful clone" is ambiguous and the two
readings pull in opposite directions:

1. **Faithful to the _rules_** — the formulas, the turn-resolution order, the
   racial traits, the economic and combat interactions, and the look and feel
   (the panes, the icons, the Win95 aesthetic, the player's mental model).
2. **Faithful to the _artifacts_** — byte-compatible save/turn/universe files,
   so the original `stars.exe` and Stars Reborn could read each other's games.

These are not the same project. The question keeps surfacing in concrete form —
most recently: must a component's internal id match the number the original game
used? (See the technology-catalog id work.) It also shapes save format, turn
files, scanner/fog encoding, and anything where "what the original game stored"
competes with "what is clean for us to store."

The useful analogy is a board game whose original materials can no longer be
manufactured. You keep the _rules_ and the _experience_; you specify new
materials — different cardstock, different tokens — that honor the original
design intent. You do not try to make your new tokens physically interchangeable
with the originals, because no one still owns a working original set to mix them
with, and chasing that compatibility would compromise the materials you can
actually produce.

## Decision

Stars Reborn is faithful to the original's **mechanics and feel**, and is
**not** binary-compatible with the original's files.

- **In scope (reproduce faithfully):** game mechanics and formulas, the order
  and interaction of turn resolution, racial traits (PRT/LRT), the data model
  (tech tree, hulls, components, costs), and the look and feel — down to
  behavior a veteran would notice. Where Stars Reborn enhances the original, a
  **Legacy mode** preserves the original behavior. Faithfulness is measured
  against the original's _behavior_ — ideally by running a scenario in both and
  diffing resulting state (the A/B faithfulness approach) — not against its byte
  output.

- **Intentional deviations are allowed, named, and recorded — never silent.**
  Faithful-by-default does not mean bug-for-bug forever. Stars Reborn may
  deliberately depart from the original — including _declining to reproduce an
  original bug_ — when there is a clear-eyed reason. Every such departure is a
  conscious, documented decision, called out in a **CHANGELOG** (and Legacy mode
  may still offer the original behavior), as opposed to an unexamined drift,
  which is a defect. We are a long way from feature parity, so this is a growing
  record, not yet a one-page list of bullet points; the discipline of naming
  each deviation is what matters now, not the length of the list.

- **Explicitly out of scope:** reading or writing the original game's binary
  files as a runtime format. A Stars Reborn save or turn file is **not** loadable
  in original Stars!, and the runtime does **not** load original `.m1`/`.hst`/
  `.xy` files. Stars Reborn uses its own formats (JSON over HTTP; gzipped-JSON
  `.sr` saves — see ADR-0001, ADR-0003, and `docs/architecture.rst`).

- **The original's binary formats are research inputs, not runtime formats —
  and understanding them deeply is a legitimate, sometimes necessary method.**
  Many of the original's intricate rules are not written down anywhere; they are
  only observable in what the game _encodes_ and _computes_. So we use published
  community formulas where they exist and are trustworthy, and we **derive or
  reverse-engineer from the binary formats** (and from oracle runs of the real
  game) where the detail is otherwise hidden. The standalone `stars_file_parser`
  library and the oracle exist for exactly this: recovering the rules, and
  seeding reference scenarios (e.g. capturing the deterministic Tutorial Game).
  That knowledge feeds our _mechanics_; it lives behind the library/oracle seam
  (ADR-0001) and never in the runtime's load path.

- **Correspondence to original data is by meaning, not by identity.** When Stars
  Reborn must relate to something from an original file — e.g. ingesting a
  captured game into a scenario — the bridge is the **name/semantics** of the
  thing (a hull named "Space Station", a part named "Mole-skin Shield"), not its
  original numeric id or byte layout. Internal ids, enums, and schemas are Stars
  Reborn's own; clients read them from `/model/` endpoints and never assume they
  match the original game's (ADR-0001, ADR-0003).

## Consequences

- **Internal ids need not match the original's.** The engine assigns stable ids
  for its own catalog; recovering the original game's exact id numbers is not a
  requirement. (This is what unblocked the remaining-component-id question: pick
  a stable scheme, don't chase the original numbers.)
- **We are free to choose the best modern "materials."** Rust engine, Python/Qt
  client, HTTP+JSON, JSON Schema as the contract — all chosen to serve the rules
  and the feel, not constrained by the original's on-disk encoding.
- **Faithfulness is a testable, behavioral claim.** The bar is "a veteran plays
  it and it behaves as they expect," pinned where possible by A/B comparison
  against the original under the oracle — not "our bytes match." A deviation is a
  mechanics bug, found by diffing state, not by diffing files.
- **This is not a license to drift.** The mechanics _are_ the product. Where a
  rule or formula is known, we reproduce it exactly (Legacy mode is the backstop
  for enhancements), and unconfirmed sub-details are flagged for oracle
  confirmation rather than guessed.
- **It does not justify dropping the original-file research capability — the
  opposite.** Reading and fully understanding the original's binary formats
  remains essential: it is often the _only_ source of truth for an intricate
  rule, ahead of or in place of community formulas, and the basis for seeding
  scenarios. The method order is: trust a confirmed community formula where one
  exists; otherwise derive it from the binaries / the oracle; flag what stays
  unconfirmed. What this ADR forbids is only loading those formats at _runtime_,
  not studying them.
