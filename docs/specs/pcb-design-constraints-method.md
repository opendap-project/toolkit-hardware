# PCB design constraints method

- **Status:** Draft v0.1 (2026-10-24). Written by Claude from the T1 main board's [PCB design constraints](https://github.com/opendap-project/board/blob/main/docs/specs/pcb-design-constraints.md) (v0.5), its product rules and net classes ([`hardware/rules/`](https://github.com/opendap-project/board/tree/main/hardware/rules)), the [industry wisdom gaps](https://github.com/opendap-project/board/blob/main/docs/research/2026-10-industry-wisdom-t1-gaps.md) and the kicad-lib [design rules](https://github.com/opendap-project/kicad-lib/tree/main/design-rules). It records the method those documents follow, so every OpenDAP board applies it the same way. Where it states as a rule a convention the T1 documents only imply (one meaning per category letter, stable IDs, fixed section numbering), that is decided by Claude under the maintainers' delegation (2026-10-24). Task HW3.5 of the [hardware engineering system plan](../plans/2026-10-hardware-engineering-system-plan.md).
- **Scope:** every OpenDAP board: main boards, front-module electronics, accessory pieces, flat cables, module and coupon boards.
- **Applications:** each board keeps its constraints spec in its own repository (`docs/specs/pcb-design-constraints.md`). The first is the T1 main board, linked above; examples below name it.

## 1. What a constraints spec is

One specification per board, deriving every limit its layout must respect from the product requirements, the parts and the fab, in one place. Each constraint has an ID, a minimum, a target and a maximum where they apply, its source, and the mechanism that enforces it. The spec is the source; rule files, net classes and checks are derived from it, never the other way round.

## 2. Header

Every constraints spec opens with these fields:

| Field | Content |
|---|---|
| **Status** | Version, date and what each version applied (ADRs, vendor documents, research); the plan task it belongs to; what is laid out or measured yet |
| **Method** | A link to this document |
| **Purpose** | The sentence of §1 for this board |
| **Enforced by** | The enforcement kinds of §6, with the paths of the board's rule file and net-class file |
| **Levels** | The RFC 0010 tagging of §7 |
| **Values** | The source and **UNVERIFIED** rule of §5 |

## 3. Sections

The sections follow the order in which the layout consumes them. A section that does not apply to a board stays, marked *n/a* with the reason, so every spec has the same numbering.

| § | Section | Content |
|---|---|---|
| 0 | Summary | The few facts that shape the board (build, thickness budget, where high-speed and analog values come from, how copper is sized), each with its source |
| 1 | Outline and mechanics | Inputs from the product: body, outline and tolerance, coordinate system, edge connectors, buttons, battery connector, mounting holes, fiducials. These are inputs until the product's interface files publish them |
| 2 | Height zones (z) | Maximum part height per zone and side, the tallest known parts and their zone |
| 3 | Stackup and build | Thickness, build (HDI class, via types), layer count, reference planes, dielectric, material, finish, acceptance class |
| 4 | Geometry beyond the fab rules | The board's own tighter limits over the fab rule set: track and space, vias, copper to edge, courtyards, thermal relief, silkscreen |
| 5 | Signal classes | One row per net class: signals, impedance, length and skew, via count, terminations |
| 6 | Power and current | Design current per path (the protection rating or the worst continuous case, whichever is higher; BRD-049 for the T1), minimum widths per copper weight, switching loops, switch nodes, vias per amp, decoupling |
| 7 | Analog partition and grounding | Ground strategy, partition of the analog section, reference routing, symmetry, test pads (audio for a DAP) |
| 8 | RF, protection, test and assembly | Radio module land and keep-out, antennas, EMC fix options, ESD and protection, test access, assembly variants, part data fields |
| 9 | Open items | What closes each **UNVERIFIED** value and each pending input |

## 4. Categories and IDs

IDs are `PCB-<CAT>-<nn>`: a category letter (or letters) and a two-digit number in order of creation. An ID keeps its meaning for the life of the board; a constraint that is dropped leaves its number unused. A category letter means one thing across every OpenDAP board, so the same letter on two boards names the same kind of limit.

Categories in use (T1 main board spec v0.5 and its product rules):

| Cat | Category | Typical enforcement |
|---|---|---|
| M | Outline and mechanics (inputs from the product) | DRC (edge, keep-out), REV, fab notes |
| Z | Height zones | CHK (3D height per zone) |
| S | Stackup and build | stackup, fab notes, DRC (via types), REV |
| G | Geometry beyond the fab rules | DRC |
| I | Signal classes (impedance, length, skew) | NC, CHK, SIM |
| P | Power and current | DRC (net-class widths), CHK (copper area, vias), REV, schematic |
| A | Analog (audio) partition and grounding | DRC (keep-out and courtyard areas), REV, schematic, SIM |
| R | RF | DRC (keep-out), REV |
| EMC | EMC fix options (footprints fitted or DNP) | REV |
| E | ESD and protection | CHK (distance), REV, schematic |
| T | Test access, assembly variants, part data fields | CHK (BOM fields, one pad per net), REV |
| V | Voltage spacing | DRC |
| H | Mounting holes and screw heads | DRC |
| B | Board edge and panel (parts and copper to edge, break tabs) | DRC |
| D | Design for manufacture and assembly (rework clearance, fiducials, silkscreen, test points, vias in pads) | DRC |
| L | Placement for safety (heat sources against the battery, the battery connector's unfused copper) | DRC |
| W | Routing hygiene (acute angles, copper necks, teardrops, vias per lane) | DRC |

A new kind of limit takes a new letter, recorded here first. Craft rules shared by every board carry `CRAFT-<nn>` IDs in the craft standard, not `PCB-` IDs.

## 5. Columns, values and sources

- **Tables.** Limits with a range: `ID | Constraint | Min | Target | Max | Source | Enforced by`. Signal classes: `ID | Net class | Signals | Impedance | Length and skew | Source | Enforced by`. Power paths: `ID | Path | Design current | Min width (outer) | Min width (inner) | Source | Enforced by`. Rules without a value (placement, topology, review items): `ID | Constraint | Source | Enforced by`.
- **Sources.** Every value names its source: a requirement or ADR ID, a datasheet with document number and page, a vendor layout guide, a standard with edition and clause, or the fab's published capabilities (cited as `[Pn]` against the board's fab research). Where a vendor is looser than a standard or than the product's need, the board keeps the tighter value and says why.
- **UNVERIFIED.** A value with no source is not used. **UNVERIFIED** marks values taken from a sibling part, an assumption, or a source not yet retrieved; each one names what closes it, and §9 lists it.
- **Arithmetic** is shown as such (formula, inputs, result).

## 6. Enforcement kinds

| Kind | Mechanism |
|---|---|
| `DRC` | The board's product rules (`.kicad_dru`), composed on top of the fab rule set (§8) |
| `NC` | A net class in the board's net-class data file (§9) |
| `CHK` | A script check on the layout (impedance, length and skew, height per zone, copper area per net, distances, BOM fields) |
| `SIM` | A simulation in the board's `sim/`, run by `odapkit sim` |
| `REV` | A review item, with its line in the [design review checklist](design-review-checklist.md), because no tool can check it |

A constraint may also name where else it is held: `schematic`, `stackup`, `fab notes`, the product's interface files, or the verification row that tests it on hardware (for example `V4-12`).

## 7. Levels and severity

- **Levels.** `[Qn]` after an ID is the [RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md) quality level at which the constraint becomes mandatory; an ID without it is Q1.
- **Rule names** carry the board, the ID and the level, because KiCad rule severities are static: `<board> PCB-<CAT>-<nn> [Qn]: <title>` (for example `T1 PCB-G-01 [Q1]: Copper clearance`). The board prefix also keeps names unique in a composed file, which refuses duplicate names.
- **Severity.** A rule at Q0 or Q1 whose value has a source is an **error**. A rule at Q2 to Q4 is a **warning**, whatever its source. A rule whose value is still **UNVERIFIED** is a **warning** at any level, and becomes an error when the value is sourced and the level is Q0 or Q1.

## 8. Rule composition

A KiCad project reads one `<project>.kicad_dru`. It is composed, never edited, from three sources in this order:

1. **Fab rules:** the fab and process rule set from kicad-lib (`design-rules/<fab>-<process>/`, for example `pcbway-hdi`), Q0;
2. **Craft rules:** the OpenDAP craft rule set from kicad-lib (`design-rules/opendap-craft/`), the DRC-checkable part of the craft standard; it uses only constraints the fab sets do not use, so it never relaxes a fab limit;
3. **Product rules:** the board's own rules, next to the board (`hardware/rules/<board>.kicad_dru`).

The project lists them in its manifest `<project>.dru.toml`; `odapkit dru compose` writes the composed file and `odapkit dru check` (the `kicad-dru-composed` pre-commit hook of toolkit-hooks) fails a commit when it is stale. KiCad applies the last matching rule for a constraint, so general rules come first and area and net-class overrides after them.

The product rules find objects by reference prefix, footprint field, pad fabrication property and rule-area name. The board's rules README lists those conventions; a footprint that does not follow them escapes its rules.

## 9. Net-class data file

One machine-readable file per board, `hardware/rules/netclasses.toml`, is the contract between the schematic and the product rules: a net in a class gets the constraints listed with it. The KiCad project's net classes are generated from it.

```toml
version = 1

[[class]]
name = "PWR_BAT"                 # the class name used by rule conditions
signals = "..."                  # which nets belong to it, in words
design_current_a = 5.0           # power classes
constraints = ["PCB-P-01"]       # the constraint IDs it carries
# impedance-controlled classes add impedance_ohm or differential_ohm;
# widths and gaps come from the stackup once the fab provides it
```

Impedance-controlled classes are named after their impedance: `<name>_<ohms>D` for differential (the T1's `USB3_90D`) and `<name>_<ohms>SE` for single-ended. The craft rules recognise exactly these two forms and exempt those classes from their general width rules.

## 10. Rule test board

Every rule file, fab, craft or product, has a generated test board that triggers every rule:

- `test/make_test_board.py` builds it with KiCad's Python from the rules file itself, so the board follows the values; generation is reproducible and the regenerated board is committed;
- one failing and one passing object per rule;
- `check_drc.py` (kicad-lib `design-rules/tools/`) runs `kicad-cli pcb drc` on it and fails unless every rule fires exactly as expected (`*.expected.json`) and nothing else does. A rules file KiCad cannot compile reports a clean board, so the check also proves the file compiled.

What DRC cannot check is listed in the rules README and carried as `CHK` or `REV` items.

## 11. Debt

Items above the board's current level stay visible: the spec's §9 and the rules README list the open values and the checks still missing, ordered by the level they unlock (RFC 0010 §3).
