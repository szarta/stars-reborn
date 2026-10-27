# 0004: Keep task ids and internal tracking out of public artifacts

**Status:** Accepted, 2026-10-26.

## Context

Stars Reborn is developed in a public monorepo (ADR-0002). Work is tracked in a
local `todo-sqlite-cli` database whose task ids are small integers that mean
something only inside a working session.

Those ids had steadily crept into the published tree: design docs, schema
notes, source comments, and the Rust/Python contract-test docstrings all
carried parentheticals like "(task #NNN)". Each one is a dangling reference. A
reader cloning the repo has no access to the private queue, so the number
resolves to nothing; it dates the artifact to the session that wrote it, and it
implies a link — an issue, a ticket — that does not exist. The artifact is
supposed to document the game and its file formats to anyone studying them, and
a work-queue id serves none of them.

`AGENTS.md` ("Public files") states the operative rule tersely so a contributor
meets it at the point of work. This ADR is the fuller record: the rule, worked
examples, and the alternatives that were weighed and rejected, so the decision
is not re-litigated later without that context.

## Decision

Public artifacts — documentation, ADRs, READMEs, changelogs, source comments,
test names, fixtures, papers — name _what_ a thing is and _why_ it exists, never
_which work item_ produced it. Task ids and task titles do not appear in them.

Where a trace to the originating work is genuinely needed:

- The `todo-sqlite-cli` database is the tracker. Public files never cite it by
  id.
- A **commit message** may carry a project-qualified id for internal tracing,
  for example `(stars_reborn 123)`. A commit message is version-control history,
  not a published artifact, so the trace lives there.
- A public file that must point at related, not-yet-done work does so
  descriptively: it names the capability, not the ticket.

### Worked examples

Using a placeholder id `#NNN` for illustration:

| Instead of (leaks a task id)             | Write (self-contained)                                   |
| ---------------------------------------- | -------------------------------------------------------- |
| `// anti-drift guard for task #NNN`      | `// anti-drift guard for the Race wire contract`         |
| `the icon field is reserved (task #NNN)` | `the icon field is reserved pending the icon convention` |
| `Technology Browser (todo #NNN)`         | `Technology Browser`                                     |
| `Migration status (task #NNN, #NNN).`    | `Migration status.`                                      |

Things that look like task ids but are **not**, and stay as they are, because
they resolve for any reader: research phase codes (`R0.7`, `R5.2`), external
issue or forum numbers (e.g. a starsautohost thread number), and
standards/protocol numbers (an RFC, an HTTP status).

## Alternatives considered

1. **Keep the ids, but make them resolvable** — publish the issue tracker, or
   mirror the `todo-sqlite-cli` DB into the repo. Rejected: the queue is a
   local working-session tool, not a product surface; mirroring it is ongoing
   overhead, and even a resolvable id still dates each artifact to the process
   that produced it rather than describing the thing.

2. **Allow ids in source comments, forbid them only in prose docs** — treat
   code comments as "internal". Rejected: the repo is public and (for
   `stars_file_parser`) a standalone library others read; comments are
   published too. The split is arbitrary and leaks the same way.

3. **Forbid even descriptive forward-references** — require that a doc say
   nothing about not-yet-done work. Rejected: a doc legitimately needs to say "X
   is pending" to be honest about the current state; naming the capability is
   useful and self-contained. Only the bare ticket number is noise.

The chosen rule keeps ids solely in the tracker and, optionally and
project-qualified, in commit messages, and makes every published file
self-contained and descriptive.

## Consequences

- The repo reads without any access to the private work queue; every file is
  self-contained and outlives any one session's numbering.
- Tracing a line back to its work item goes through `git blame` to the commit
  message, which is the one place an id is allowed.
- A descriptive forward-reference carries less than a live ticket link would.
  That is the accepted trade for a self-contained artifact.
- This is a governance rule, not an engineering constraint: it does not affect
  the wire contract, the build, or runtime behaviour, and so has no contract
  test. `AGENTS.md` ("Public files") is the operative restatement a contributor
  applies at the point of work and the enforcement point; this ADR is the
  reasoning behind it.
