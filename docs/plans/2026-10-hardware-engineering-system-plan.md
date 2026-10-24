# Hardware engineering system plan

- **Date:** 2026-10-24
- **Status:** Active. Tasks change status as work lands; the plan itself changes only with the maintainers.
- **Scope:** the methods, standards and tools every OpenDAP device's electronics are built with: fab and craft rule sets (kicad-lib), the `odapkit` hardware tools (toolkit-hardware), the hooks (toolkit-hooks), the shared specifications and research (toolkit-hardware), and the part data conventions (parts-lib). They must work for any model or variant, not only the first.
- **Applications:** each device's plan applies this one and keeps only its own tasks. The first is the [T1 electronics plan](https://github.com/opendap-project/t1/blob/main/docs/plans/2026-10-electronics-plan.md), the source of the tasks moved here on 2026-10-24; each moved task notes its former ID (`was E…`), and the T1 plan keeps a line pointing to it.

## Quality levels

Every rule, check, verification row and certification item carries the level at which it becomes mandatory, from Q0 (bench-safe) to Q4 (reference), per [RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md). A build passes everything at its target level; what lies above is visible debt, not a blocker, and a level reached is never lost. Each device's plan sets its builds' targets.

## The engineering cycle

Each design iteration of any board runs the same local loop: constraints → ERC/DRC → simulation regression → checks across interfaces → exports for integration → fab package.

## Workstreams

Task status: `todo`, `doing`, `done`, `blocked` (with its blocker), `deferred`, `decision` (waits for the maintainers).

### HW1. Fab rule sets

The fab rule sets live in kicad-lib (KLIB-002), one per PCBWay process. The product rules live with each board and are composed on top of the fab set, because a KiCad project reads one `.kicad_dru` file. Every rule set has a test board that triggers every rule, checked with `kicad-cli pcb drc`.

| ID | Task | Repository | Status |
|---|---|---|---|
| HW1.1 | `pcbway-hdi` fab rule set and test board, from the published capabilities (research 2026-10 PCBWay); was E3.1 | kicad-lib | done (kicad-lib `bec830a`, 16/16 rules fire) |
| HW1.2 | `pcbway-flex` fab rule set and test board; was E3.2 | kicad-lib | done (kicad-lib `bec830a`, 6/6) |
| HW1.3 | `pcbway-multilayer` fab rule set and test board (accessory pieces, rigid front-module boards); was E3.3 | kicad-lib | done (kicad-lib `bec830a`, 13/13 at 18 µm and at 35 µm) |
| HW1.4 | Ask PCBWay for the HDI and flex stackups and the unpublished limits (microvia land, flex with stiffener tolerance, pogo pin placement); was E3.6 | kicad-lib | deferred: published capabilities used meanwhile (maintainers, 2026-10-24) |

### HW2. Tools (`odapkit`) and hooks

| ID | Task | Repository | Status |
|---|---|---|---|
| HW2.1 | Composition tool and check: project `.kicad_dru` = fab set + product rules, with a stale-file check in pre-commit; was E3.5 | toolkit-hardware, toolkit-hooks | done: `odapkit dru`, hook `kicad-dru-composed` (toolkit-hooks `f5edd58`, `e540f4e`) |
| HW2.2 | Simulation regression: one runner for the ngspice studies with pass/fail thresholds taken from the constraints and ADRs, vendor models fetched by script, never committed; was E4.4 | toolkit-hardware, board | done: `odapkit sim`; board checks 15 pass, 1 blocked on the LMR33630C model (board `ddaf1d5`) |
| HW2.3 | `component.yaml` schema of the [component export contract](../specs/component-export.md); was E4.7 | toolkit-hardware | done: schema and validator (toolkit-hardware `6860055`); open points in the contract |
| HW2.4 | Signal-integrity loop: stackup impedance calculation, length and skew reports from the layout, checked against each board's constraints; was E4.5 | toolkit-hardware | todo |
| HW2.5 | Fab pipeline dry run: run `fab-package` on a rule-set test board end to end; was E4.8 | toolkit-hardware | todo (HW1.1 done) |
| HW2.6 | Tag toolkit-hooks v0.4.0 and move the hardware repos to it, so `kicad-dru-composed` runs on commit; was E4.11 | toolkit-hooks | done: v0.4.0 tagged; board `2ff6252`, kicad-lib `9c0f882` moved to it; other hardware repos move as they are next edited |
| HW2.7 | Availability field in the parts-lib spec-sheet template (T1-010, T1-029), with date and source; was E4.3 | parts-lib | done: PLIB-003 (parts-lib `a3afb78`); existing sheets migrate when edited |
| HW2.8 | `odapkit variant`: per-variant BOM, pick-and-place, devicetree overlays and device description; absent-state check and its hook ([RFC 0011](https://github.com/opendap-project/rfcs/blob/main/text/0011-feature-blocks-and-variants.md)); was E10.3 | toolkit-hardware, toolkit-hooks | todo |
| HW2.9 | Virtual variants from the same variant files; was E10.4 | virtual-devices | todo |

### HW3. Standards and methods

| ID | Task | Repository | Status |
|---|---|---|---|
| HW3.1 | OpenDAP PCB craft standard with its rule set and check script (`odapkit craft`), shared by every board; was E9.2 | kicad-lib, toolkit-hardware | doing |
| HW3.2 | Industry wisdom benchmark and the phase-staged [design-review checklist](../specs/design-review-checklist.md); the T1 gaps note is the T1's application; was E9.3 | toolkit-hardware, board | doing (toolkit-hardware `ad2e367`; T1 gaps board `427d860`) |
| HW3.3 | Tag every existing item with its quality level as each document is next edited (RFC 0010); was E9.5 | all | todo |
| HW3.4 | [Electronics integration and verification method](../specs/integration-and-verification.md): principles, integration levels L0–L6, module rules M1–M4, interaction-matrix method, row format, levels and gates; separated from the T1 spec (E5.0) | toolkit-hardware | done: Draft v0.1 (2026-10-24) |
| HW3.5 | [PCB design constraints method](../specs/pcb-design-constraints-method.md): sections, categories and IDs, columns, sources, enforcement kinds, levels and severity, the net-class data file, rule composition, rule test boards; generalised from the T1 constraints (E2) | toolkit-hardware | done: Draft v0.1 (2026-10-24) |
| HW3.6 | [Compliance regime catalog](../research/2026-10-compliance-regimes.md) by product feature (radio module, Li-ion pack, headphone output, USB-C PD, accessories); separated from the T1 design-for-compliance research (E9.4) | toolkit-hardware | done (2026-10-24) |
