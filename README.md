# Stars Reborn

An open-source, faithful clone of Stars! (1995/1996, Jeff Johnson & Jeff
McBride). The goal is a freely distributable reproduction of the original
game's mechanics, with respectful, opt-in enhancements — a "Legacy" mode
always preserves the original behavior.

## Layout

This is a monorepo. Each component is developed here and published as its own
artifact (see `docs/adr/0002`).

| Path         | Component                                                     |
| ------------ | ------------------------------------------------------------- |
| `engine/`    | Rust host + engine: HTTP API, turn processing, data authority |
| `client/`    | Python/PySide6 reference client (a pure HTTP consumer)        |
| `schemas/`   | JSON Schema contract for all shared objects and API messages  |
| `docs/`      | Sphinx design docs and decision records (`docs/adr/`)         |
| `packaging/` | Launcher and AppImage/PyInstaller build driver                |

The engine and client communicate only over HTTP (`docs/adr/0001`), so
multiplayer (a remote engine) and single-player (a local engine) are the same
client, and any conforming HTTP client is valid.

## Developing

Install the Git hooks before committing:

```sh
pre-commit install
pre-commit run --all-files
```

- Rust: `cargo build`, `cargo test --workspace`, formatted with rustfmt,
  linted with clippy (`-D warnings`).
- Python (client): linted and formatted with ruff.
- JSON/YAML/Markdown: formatted with [moldy](https://github.com/brandon-arrendondo/moldy).
- Complexity is gated by [knots](https://github.com/brandon-arrendondo/knots-pre-commit).

Commits require a DCO sign-off (`git commit -s`) and carry no AI attribution
trailer; see `AGENTS.md`.

## AI Assistance

Parts of this project were written with the assistance of AI coding agents,
under human review and direction. This note is the single place that
acknowledgment lives — individual commits do not carry AI attribution
trailers.

## License

MIT. See [LICENSE](LICENSE).
