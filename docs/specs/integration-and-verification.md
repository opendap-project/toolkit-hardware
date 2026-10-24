# Electronics integration and verification

- **Status:** Draft v0.1 (2026-10-24), decided by Claude under the maintainers' delegation: specialised modules per domain are built, provided the integration is verified as well and never inferred from the parts. Separated on 2026-10-24 from the T1 spec of the same version, so the method serves every OpenDAP device. Task HW3.4 of the [hardware engineering system plan](../plans/2026-10-hardware-engineering-system-plan.md).
- **Scope:** the electronics of any OpenDAP device, from parts to the assembled product. Case, mechanical and physical-simulation work is out of scope; the levels that need it (L5, L6) list only their electrical evaluations.
- **Applications:** each device keeps its own modules, interaction matrix and evaluation rows in its product repository. The first is the T1: [T1 electronics integration and verification](https://github.com/opendap-project/t1/blob/main/docs/specs/electronics-integration-verification.md). Examples below name the T1 where it makes a rule concrete.
- **Levels:** rows carry RFC 0010 quality levels as described in §4.2.

## 0. Principles

1. **Parts passing does not make the whole pass.** An interaction between two domains is signed off only at the lowest level that reproduces its physical mechanism (conduction, proximity, shared ground, shared clock, heat, software timing). A mechanism that a level cannot reproduce is marked there as *not representative*, never as passed.
2. **What is tested is what ships.** Every module is built from the same hierarchical schematic sheets as the device's main board, and its layout block is copied from or into the main board's, with the same stackup class, part numbers and values. A module that diverges from the board is re-tested after the board is laid out (§2, rule M4).
3. **Every row traces to a requirement or a constraint.** Each evaluation row names the IDs it verifies (product and board requirements, PCB constraints, ADRs, open BOM items; for the T1: T1-, BRD-, PCB-, ADR, BOM §7 item) and carries the product's three thresholds (ideal, warning, hard limit; T1-048 for the T1) where the metric has them.
4. **Regression follows the dependency graph.** A change to a block reruns its L1 and L2 rows and every L3 and L4 row of each interaction it takes part in (§3).
5. **Measurement before shrinking.** A level's exit gate is evidence (data file, capture, photo), stored with the component that was tested; a result without evidence counts as not run.

## 1. Integration levels

| Level | What is integrated | Where it lives | Representative for | Not representative for | Exit gate |
|---|---|---|---|---|---|
| **L0 Part** | One part against its datasheet | parts-lib sheet, kicad-lib symbol/footprint, fab rule test boards | Pin map, land pattern, ratings, model availability | Anything about the circuit | Sheet transcribed, footprint checked against the drawing, availability dated (PLIB-003) |
| **L1 Block** | One circuit block (a hierarchical sheet; a feature block of RFC 0011) | `sim/` studies (`odapkit sim`), schematic review | Topology, values, margins, stability, levels | Layout parasitics, coupling, real part spread | Every `checks.toml` row passes; ERC clean; datasheet review checklist done |
| **L2 Domain module** | One domain on its own test board, real parts and real layout block | Module boards (§2) | Layout-dependent performance of one domain, part spread, the board's open bench items | Interactions with other domains | Every L2 row of the domain passes with evidence |
| **L3 Domain pair** | Two or more modules connected through the core module | Module stack (§2.2) | Conducted coupling (supply, ground return through defined interconnect), protocol and timing, power sequencing, software bring-up | Proximity and radiated coupling, shared copper planes, thermal coupling, final ground geometry | Every L3 row of the pair passes; conducted-coupling rows recorded as upper bounds |
| **L4 Integrated board** | The main board (first prototype) with the front module and accessory interfaces on the bench (for the T1: faceplate and HAT device-side piece) | Main-board repository | Everything electrical, including proximity, radiated and thermal coupling on the real board | Enclosure effects (antenna detuning, case thermal, ESD through the case) | Every L4 row passes; every interaction of §3 signed off |
| **L5 Product assembly** | Board, front module, battery pack and accessory interface in the case | Product repository | Electrical behaviour in the enclosure: radio in the case, ESD at the product surface, thermal at the surface, audio with the final jacks and ground | Long-term behaviour | Every L5 row passes |
| **L6 Product in use** | The device running Blackbird OS through real sessions | Product repository, toolkit-verify | Autonomy, endurance and scale, experience budgets, compliance pre-scans (for the T1: T1-039, T1-046, T1-047, T1-048) | — | Release gate: no hard limit crossed |

## 2. Domain modules (L2) and the module stack (L3)

### 2.1 Modules

A device's electronics are split into domains (power, core, audio, radio, front module, accessory interface, peripherals, and the impedance and loss coupons of its stackups). Each domain gets one module board, named `M-<DOMAIN>`, listed in the device's application with its contents, the questions it answers and the IDs it verifies. The core module (`M-CORE`: SoC, memory, storage, PMIC, boot) is the hub of the stack.

Module rules:

- **M1.** Each module is a KiCad project in the repository of the component it serves, built from the same hierarchical sheets as the main board (no re-drawn copies).
- **M2.** The core module uses the main board's stackup and fab process; the other modules use the cheapest stackup that keeps their critical layout identical (same layer adjacency under the block). A module whose performance depends on the ground and plane arrangement keeps the main board's arrangement under its block (for the T1: M-AUD under the audio block).
- **M3.** Modules connect to the core module through one documented module connector per boundary, carrying the nets that cross that boundary on the main board, with ground on every second contact and the supply returns sized for the full budget. The connector map is a machine-readable interface file, checked against the main-board netlist.
- **M4.** After the main board is laid out, a module whose layout block differs from the board's is either updated and re-tested, or its L2 results are marked *superseded by L4*.

### 2.2 Module stack (L3)

The core module is the hub: every other module attaches to it, so pairs and the full stack run real Blackbird OS. The power module powers the stack through the same rails as on the board. The stack is representative for conducted effects through its defined interconnect only; every proximity, radiated or thermal interaction is first signed off at L4.

## 3. Interaction matrix

Each device's application lists its domains and fills one upper-triangular matrix, one cell per pair of domains (and one per domain with the outside world, `EXT`: its external connectors and cables). Each cell names:

- the **coupling mechanism** (conducted supply ripple or load transients, shared ground return, proximity and radiated coupling, shared clock or timing, thermal, protocol and software timing, ESD and surge from outside);
- the **level where it is first testable**;
- the **level where it is signed off**, which is the lowest level that reproduces the mechanism (principle 1).

A pair with no mechanism is marked `—`. Every cell is signed off before the product enters L6 (§5).

## 4. Evaluation matrices

### 4.1 Row format

Columns: `ID | case | steps | expected (with thresholds) | observed | evidence`. The application's tables fix the cases and their expected values; *observed* and *evidence* are filled when the level runs, stored next to the module or board that was tested. Thresholds come from the requirement, the ADR or the constraint named; where none exists yet, the case says what sets it.

IDs: `V0-nn` (L0), `V1-nn` (L1), `V2-<module letter><nn>` (L2, for example `V2-A01` for the audio module), `V3-nn` (L3, with the pair named), `V4-nn` (L4), `V5-nn` and `V6-nn` (L5 and L6).

At L4, every L2 and L3 row is repeated on the board (the L2/L3 values become the reference), and the L4 rows are added.

### 4.2 Levels

`[Qn]` after a row ID is the RFC 0010 quality level at which the row becomes mandatory; a row without it is Q1 ([RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md) rule 1). Compliance rows come from the device's design-for-compliance work, built on the shared [compliance regime catalog](../research/2026-10-compliance-regimes.md).

### 4.3 Variants

Each hardware variant carries its own target level and runs the rows its blocks touch; results are never inherited from another variant ([RFC 0011](https://github.com/opendap-project/rfcs/blob/main/text/0011-feature-blocks-and-variants.md) rule 9).

## 5. Gates between levels

- A module goes to L3 only after its L2 rows pass or each failure has a recorded fix in the main-board design.
- The main board is released for fabrication only after every L2 bench item of its BOM is closed or carried into the board with a decision, and every L3 row that can fail on the board's design (not only on the module interconnect) has passed.
- The product enters L6 only when every interaction of §3 is signed off at its level.

## 6. Open

- Instruments and their residuals (audio analyser, TDR/VNA, current probes) are chosen with the module designs; a measurement's instrument residual must sit at least 10 dB below the expected value (**UNVERIFIED** margin, to confirm with the first instrument).
- KiCad 10 support for reusing a layout block between projects (rule M1/M4) is to be checked before the first module layout.
- Thresholds marked "set at L2" are filled from the first measurements and confirmed by the maintainers (the product's experience budgets).
