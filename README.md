# Toolkit hardware

Hardware tooling for OpenDAP: fab packages, FreeCAD exports, part data sync, and the [component export contract](docs/specs/component-export.md) every component follows.

Part of the [OpenDAP](https://github.com/opendap-project) Developer Toolkit, which lives in the workspace under `public/toolkit/` as one repository per tool domain.

## Layout

- `tools/fab-package.sh` — fab package from a KiCad project (runs ERC/DRC through [toolkit-hooks](https://github.com/opendap-project/toolkit-hooks), found as the sibling `../hooks` or `$OPENDAP_TOOLKIT_HOOKS`)
- `tools/freecad-export.py` — STEP and other exports from FreeCAD
- `tools/parts-sync.py` — fetches the files listed in parts-lib's `manifest.toml` into `~/.cache/opendap/parts/`
- `docs/` — requirements, the component export contract and research

## License

This repository follows the [REUSE](https://reuse.software) layout: license texts live in `LICENSES/` and `REUSE.toml` maps each path to its license.

- Default: **GNU GPL v3.0 or later** (`GPL-3.0-or-later`)
- Markdown files and `docs/`: **Creative Commons Attribution-ShareAlike 4.0** (`CC-BY-SA-4.0`)

Copyright © 2026 The OpenDAP Project.
