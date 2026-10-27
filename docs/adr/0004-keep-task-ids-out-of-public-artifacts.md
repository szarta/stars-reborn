# 0004: Keep task ids and internal tracking out of public artifacts

**Status:** Accepted, 2026-10-26.

## Context

Stars Reborn is developed in a public monorepo (ADR-0002). Work is tracked in a
local `todo-sqlite-cli` database whose task ids are meaningful only inside a
working session: an outside reader of the repo cannot resolve them, and they
leak internal process into an artifact meant to document the game and its file
formats.

`AGENTS.md` ("Public files") already states the operative rule — task ids and
task titles do not belong in documentation, ADRs, READMEs, changelogs, source
comments, test names, or fixtures. What was missing was the recorded _decision_
and its rationale, so the rule read as arbitrary; in practice ids had crept into
design docs, schema notes, and contract-test comments. This ADR records the
decision. `AGENTS.md` remains the single normative statement of the rule — this
record does not restate its wording (`AGENTS.md`'s "One copy of these rules"
keeps the rule in one place).

## Decision

Public artifacts describe _what_ a thing is and _why_, never _which work item_
produced it. The operative rule and its exact scope live in `AGENTS.md`
("Public files").

Where work still needs tracing:

- The `todo-sqlite-cli` database is the tracker, and public files do not
  reference it by id.
- A **commit message** may carry a project-qualified id for internal tracing
  (for example `(stars_reborn 123)`); a commit message is not a public artifact
  in the sense above.
- A public file that must point at related, not-yet-done work does so
  descriptively — "pending the icon convention", "a tracked follow-up" — naming
  the thing, not the ticket.

Existing public files were swept to this rule when it was recorded.

## Consequences

- Reading the repo requires no access to the private work queue; every file is
  self-contained.
- Tracing a line back to its work item goes through `git blame` to the commit
  message, which is where an id is allowed.
- A descriptive forward-reference carries less than a ticket link would. That is
  the intended trade: the artifact outlives any one session's numbering.
- This is a governance rule, not an engineering constraint. It does not affect
  the wire contract, the build, or runtime behaviour, and so has no contract
  test; `AGENTS.md` is the enforcement point.
