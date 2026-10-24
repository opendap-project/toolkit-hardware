# Toolkit hardware

Hardware tooling for OpenDAP: fab packages, FreeCAD exports, part data sync, and the [component export contract](docs/specs/component-export.md) every component follows.

Part of the [OpenDAP](https://github.com/opendap-project) Developer Toolkit, which lives in the workspace under `public/toolkit/` as one repository per tool domain.

## Tools

Reached through the Developer Toolkit's command, `odapkit <tool>` (RFC 0009), from `bin/`:

- `odapkit dru compose|check` — composes a KiCad project's `<project>.kicad_dru` from the fab rule set and the product rules listed in `<project>.dru.toml`, or checks that it is up to date. It runs [toolkit-hooks](https://github.com/opendap-project/toolkit-hooks)' `kicad-dru.py`, the script of the `kicad-dru-composed` pre-commit hook, where the manifest format is documented.
- `odapkit sim [run|list|fetch]` — runs the simulation regression checks of a board's `sim/*/checks.toml` ([spec](docs/specs/simulation-checks.md)).
- `odapkit component validate` — validates `export/component.yaml` against [`schemas/component.schema.json`](schemas/component.schema.json) ([contract](docs/specs/component-export.md)).

Tests: `python3 -m unittest discover tests` (needs ngspice, uv, and toolkit-hooks as the sibling `../hooks`).

## Layout

- `bin/` — the `odapkit-*` tools
- `schemas/` — JSON Schemas (MPL-2.0)
- `tests/` — tests and their fixtures
- `tools/fab-package.sh` — fab package from a KiCad project (runs ERC/DRC through [toolkit-hooks](https://github.com/opendap-project/toolkit-hooks), found as the sibling `../hooks` or `$OPENDAP_TOOLKIT_HOOKS`)
- `tools/freecad-export.py` — STEP and other exports from FreeCAD
- `tools/parts-sync.py` — fetches the files listed in parts-lib's `manifest.toml` into `~/.cache/opendap/parts/` (`--mpn` for one part)
- `docs/` — requirements, the component export contract and research

## License

This repository follows the [REUSE](https://reuse.software) layout: license texts live in `LICENSES/` and `REUSE.toml` maps each path to its license.

- Default: **GNU GPL v3.0 or later** (`GPL-3.0-or-later`)
- Markdown files and `docs/`: **Creative Commons Attribution-ShareAlike 4.0** (`CC-BY-SA-4.0`)
- `schemas/`: **Mozilla Public License 2.0** (`MPL-2.0`)

Copyright © 2026 The OpenDAP Project.
