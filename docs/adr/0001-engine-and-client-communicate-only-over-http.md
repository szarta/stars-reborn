# 0001: Engine and client communicate only over HTTP; no in-process interop

**Status:** Accepted, 2026-10-22.

## Context

Stars Reborn is a client/server game: a Rust engine that owns all game state
and rules, and a Python/PySide6 reference client that presents the game and
collects a player's orders. The two have always been designed to talk only
over an HTTP + JSON API.

The project has just moved from one repository per component into a single
monorepo (ADR-0002). A monorepo removes the friction that used to keep the two
apart, which makes it easy to reach across the boundary by accident — to call
an engine function directly from client code, to share a Rust/Python binding,
or to let the client keep its own copy of a rule "just for this one screen."
Each of those would quietly dissolve the boundary the architecture depends on.

## Decision

The engine and the client communicate **only** over the HTTP API. There is no
in-process interop, no shared-memory binding, and no dependency edge between
the `engine/` and `client/` build targets.

- The engine is the gatekeeper: it validates every request (structurally,
  then against the rules, then against game-state authority) and rejects
  anything invalid, regardless of what the client sent.
- The client is a pure consumer of the API. It reads the data model (tech
  tree, hulls, traits, formulae) from `/model/` endpoints and never hardcodes
  or caches an independent copy of a rule. It may enforce a rule locally for
  responsiveness, but the engine's answer is final.
- Where the boundary is subtle — e.g. knowledge of the original game's binary
  file formats — the knowledge lives behind an explicit API or library seam,
  and unit tests cover that seam so a regression surfaces as a test failure
  rather than as silent coupling.

## Consequences

- Multiplayer (a remote engine) and single-player (a local engine on
  `localhost`) are the same client code; only the base URL differs.
- Any HTTP-capable implementation conforming to the API is a valid client, so
  third-party clients remain possible.
- The two components can be built, tested, and released as separate artifacts
  (ADR-0002) even though they are developed together.
- A convenience that would require calling across the boundary in-process is
  not a convenience we take; the cost is paid in an API round-trip, which is
  the point.
