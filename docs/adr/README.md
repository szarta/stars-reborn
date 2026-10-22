# Architectural Decision Records

Settled policy questions about Stars Reborn: the ones likely to come up again
as "should we change this?" in a later session that lacks the context of the
one that settled them. Read the relevant ADR before proposing to change what
it covers.

Not in the Sphinx toctree; read these files directly.

## When to write one

When a question is settled that isn't obvious from the code, isn't already
written in `docs/` or `AGENTS.md`, and is likely to be asked again. A commit
message describes one piece of work; an ADR records a standing policy that
should outlive it.

## Format

`NNNN-short-slug.md`, numbered in sequence, never renumbered or deleted. Each
file has:

- **Status**: Accepted, with the date. A later ADR may supersede an earlier
  one; the earlier one stays as the record, with a note pointing to its
  replacement, instead of being edited in place.
- **Context**: what prompted the question, in enough detail that the decision
  doesn't look arbitrary.
- **Decision**: the rule, stated so it can be applied without re-deriving the
  reasoning.
- **Consequences**: what the decision does and doesn't justify.

## Index

- [0001: Engine and client communicate only over HTTP; no in-process
  interop](0001-engine-and-client-communicate-only-over-http.md)
- [0002: Develop in one monorepo; publish separate
  artifacts](0002-develop-in-a-monorepo-publish-separate-artifacts.md)
