# Design review checklist

- **Status:** Draft v0.1 (2026-10-24). Written by Claude from the [industry wisdom benchmark](../research/2026-10-industry-wisdom-benchmark.md) and the review items (`REV`) of the T1 [PCB design constraints](https://github.com/opendap-project/board/blob/main/docs/specs/pcb-design-constraints.md) v0.4. Quality levels follow [RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md).
- **Scope:** every OpenDAP board (main boards, faceplate electronics, HAT pieces, flat cables, module and coupon boards). Items marked *T1* apply where the T1 constraint they name exists; other boards apply them through their own constraint of the same kind, or mark them n/a.
- **Purpose:** the one place design reviews run from. Tools check what they can (ERC, DRC, `odapkit sim`, layout scripts); this list holds what only a reviewer can judge, and points at the tool result where a tool exists.

## 1. How a review runs

1. **Phases.** Six reviews, each before the next step starts: schematic (§2), placement (§3), routing (§4), pre-fab release (§5), first article (§6), bring-up (§7). A later phase does not re-open an earlier one's items unless the design changed them.
2. **Target level.** The build declares its RFC 0010 target (Q0 bench-safe to Q4 reference). Every item at or below the target is answered; items above it are listed as debt with their state, never dropped. An item without a level is Q1 (RFC 0010 rule 1).
3. **Answers.** `pass`, `fail`, `n/a` (with the reason), or `waived` (RFC 0010 rule 6: reason, risk, the revision that closes it, the maintainers' sign-off). A pass names its evidence; an item without evidence counts as not run.
4. **Record.** The review record lives with the component (`docs/reviews/<date>-<phase>.md` in its repository), as a copy of the phase table with the answer, evidence and reviewer per row. A second person reviews every item a tool does not check (IW-SC-01).
5. **Ratchet.** An item that passed at a level stays passing in later revisions (RFC 0010 rule 4); a change that breaks it blocks, whatever its level.
6. **Sources.** `IW-…` points at the benchmark; `PCB-…` at the T1 constraints; `V…` at the T1 verification matrices; `BRD-`, `T1-` at requirements.

## 2. Schematic review

| ID | Level | Question | Evidence expected | Source |
|---|---|---|---|---|
| DRV-101 | Q0 | Does ERC run clean, with every waiver written in the schematic? | `kicad-cli sch erc` report, zero errors | Pre-commit `kicad-erc` |
| DRV-102 | Q1 | Has every IC been reviewed pin by pin against its datasheet by someone other than its author: power pins, unused pins, straps, absolute maximum, recommended application circuit? | Per-IC review table with datasheet revision and reviewer | IW-SC-01; L1 exit gate |
| DRV-103 | Q0 | Does every protection the power tree relies on exist in the schematic: fuse, pack connector polarity, eFuse per external rail, VBUS surge clamp, charger TS network? | Power tree to schematic cross-check | BRD-049, BRD-026; *T1:* PCB-E-02, PCB-E-03, ADR 0014 |
| DRV-104 | Q0 | Does every enable, reset and boot strap have a defined level from a resistor while its driver is unpowered or in reset, with rails, amplifiers and external sources off by default? | List of control nets with default and resistor | IW-SC-02 |
| DRV-105 | Q0 | Can any signal drive an unpowered domain (faceplate off, HAT absent, DAC unpowered, coprocessor off)? | Domain-crossing table: each crossing net, both supplies, the protection or sequencing that prevents back-powering | IW-SC-03 |
| DRV-106 | Q1 | Does every inter-chip net connect matching IO voltages, through a translator where they differ? | IO-domain table checked against the pin plan | IW-SC-04; *T1:* BOM §4.2 |
| DRV-107 | Q1 | Is every ceramic capacitor's effective capacitance after DC bias at least what its regulator or circuit needs? | Value per rail with the maker's DC-bias figure | IW-PI-03; *T1:* BOM §7.28 |
| DRV-108 | Q0 | Is every battery-connector pin safe whatever order the pins mate in? | Mating-order table: each first-contact pin, what it drives, the series resistor or clamp | IW-BA-03 |
| DRV-109 | Q0 | Are the insertion transients of the battery, VBUS and every hot-plugged rail inside the absolute maximum of each part on them (ceramic input ringing up to twice the input)? | Per-input worst case with the part limits | IW-PI-04 |
| DRV-110 | Q0 | Is the fuse rated for the circuit's voltage and the pack's short-circuit current, and does the pack PCM trip before it? | Fuse ratings against the pack's fault current and the PCM trip window | IW-BA-04; *T1:* ADR 0014 |
| DRV-111 | Q3 | Is the single-fault analysis of the charge path written (each fault, the layer that stops it)? | Single-fault table | IW-BA-01; IEC 62368-1 Annex M |
| DRV-112 | Q1 | Does the frequency plan list every converter's frequency range, light-load mode and the beats between them, with nothing landing in the audio band during playback? | Frequency plan table | IW-SW-03, IW-SW-04 |
| DRV-113 | Q1 | Does each converter feeding audio either run forced PWM during playback, or carry a measured or simulated proof that its light-load bursts are rejected downstream? | Mode per converter; spur budget | IW-SW-04, IW-SW-05 |
| DRV-114 | Q1 | Do the analog references agree: is every single-ended output referenced to the same ground point (the jack ground pin) through the whole chain (DAC, gain stage, output)? | Reference-point list per output | IW-GA-06; *T1:* PCB-A-03 |
| DRV-115 | Q1 | Are VA and VCP fed from independent clean supplies; VL and VD from logic? (*T1:* CS43198) | Power-tree lines | *T1:* PCB-A-05 |
| DRV-116 | Q2 | Does every cable-attached audio output have footprints for RF filtering (series element and shunt to ground) that the amplifier is stable with? | Footprints and a stability check with the filter fitted | IW-GA-08 |
| DRV-117 | Q2 | Can every peripheral be reset or power-cycled by software, and every I2C bus recovered? | Reset path per peripheral | IW-ES-03 |
| DRV-118 | Q1 | Is the clock path checked for edge rate at the receiver threshold, not only for levels? | Simulation or measurement of slew at the threshold | IW-CK-02; *T1:* ADR 0010, E1.6 |
| DRV-119 | Q1 | Are bring-up provisions in the schematic: rail isolation links, test points on reset, power-on, boot mode and PG nets, spare GPIO to pads, scope ground points? | List of provisions | IW-BU-01 to IW-BU-04; *T1:* PCB-T-01, PCB-T-02, PCB-T-03 |
| DRV-120 | Q1 | Is the board revision readable by software? | Revision source (EEPROM, straps) | IW-BU-06 |
| DRV-121 | Q1 | Has every part a Manufacturer and MPN, a dated availability, a second source or a recorded reason for none, and a variant field where optional? | BOM check output | PCB-T-04, PCB-T-05; PLIB-003; IW-SP-02 |
| DRV-122 | Q2 | Is the provenance of every part known: authorised distributor, or a recorded reason and an incoming check? | Provenance column | IW-SP-01 |
| DRV-123 | Q3 | Is every single-source or critical part on a lifecycle watch (PCN, NRND, EOL), with a buffer plan? | Watch list | IW-SP-03 |

## 3. Placement review

| ID | Level | Question | Evidence expected | Source |
|---|---|---|---|---|
| DRV-201 | Q1 | Does the outline sit inside the enclosure cavity with the clearance and tolerance the constraints set, with mounting holes at the bosses? | Outline against the interface file | *T1:* PCB-M-01, PCB-M-02, PCB-M-08 |
| DRV-202 | Q1 | Are edge parts where the product puts them (connectors, buttons)? | Placement screenshot against the requirement | *T1:* PCB-M-05, PCB-M-06 |
| DRV-203 | Q0 | Is the battery connector where the pack lead reaches it without strain, outside the pocket, with nothing sharp or tall facing the cell? | Placement and 3D check against the pocket | *T1:* PCB-M-07; IW-BA-02 |
| DRV-204 | Q1 | Does every part respect its height zone? | 3D height check per zone | *T1:* PCB-Z-01 to PCB-Z-05 |
| DRV-205 | Q1 | Are fiducials placed: three global per populated side, plus local ones at fine-pitch BGAs? | Fiducial list | *T1:* PCB-M-09 |
| DRV-206 | Q1 | Is the board partitioned so that no digital or switching return current crosses the analog area? | Partition drawing with the return paths of the large currents (return-current map) | IW-GA-01, IW-GA-03; *T1:* PCB-A-01, PCB-A-06, PCB-A-07 |
| DRV-207 | Q1 | Does each switching converter's hot loop (per its topology, including inverting ones) sit as in its datasheet or application-note layout, on one side, over unbroken ground? | Loop drawn per converter, compared with the reference layout | IW-SW-01; *T1:* PCB-P-07 |
| DRV-208 | Q1 | Do the amplifier rail decoupling capacitors return to the power ground point and away from the input and feedback references; are rail and load current paths kept off the input and feedback traces? | Placement drawing of the output stage with current paths | IW-GA-04, IW-GA-05; *T1:* PCB-A-08, PCB-A-09 |
| DRV-209 | Q1 | Are the DAC's ground pad vias, filter capacitors and reference routing placed per its datasheet? (*T1:* CS43198) | Placement against DS1156F2 §8 | *T1:* PCB-A-02, PCB-A-04 |
| DRV-210 | Q1 | Is the clock source next to the converter it clocks, with the clock net short? | Placement and net length | IW-CK-03; *T1:* PCB-I-09 |
| DRV-211 | Q1 | Is every decoupling capacitor placed for the smallest mounting loop (side, via position, plane pair)? | Placement view per supply | IW-PI-01; *T1:* PCB-P-10 |
| DRV-212 | Q1 | Is every ESD part between its connector and everything else, nearer the connector than the protected part is? | Distance per connector | IW-ES-01; *T1:* PCB-E-01 |
| DRV-213 | Q2 | Does the ESD current from each external connector have a defined ground region at the edge, away from the analog references and the SoC? | Drawing of the ESD current regions | IW-ES-02 |
| DRV-214 | Q2 | Where does the ground current between two external connectors run (USB to a computer and the headphone jack, a line output), and does it stay off the analog reference? | Drawing of the external ground-loop path | IW-GA-07; *T1:* V4-06 |
| DRV-215 | Q1 | Is the radio module, its RF path and keep-out exactly as the module vendor specifies? | Overlay with the vendor drawing | IW-RF-01; *T1:* PCB-R-01, PCB-R-02, PCB-R-03, PCB-I-07 |
| DRV-216 | Q2 | Are the antennas and their feeds away from multi-gigabit routes, connectors and flexes (USB 3, PCIe), and is metal near the antennas (shields, plates, battery) accounted for? | Distance table; antenna clearance from the vendor | IW-RF-02, IW-RF-04 |
| DRV-217 | Q1 | Are shield-can frames placed around the SoC/memory and the radio, fitted or DNP? | Frame footprints | IW-RF-03; *T1:* PCB-T-06 |
| DRV-218 | Q1 | Is there a rework keep-out around every BGA, or a written acceptance of the parts inside it? | Keep-out or note | IW-DF-06 |
| DRV-219 | Q1 | Are heavy parts and BGAs on the second reflow side, with light parts only on the first? | Side per part | IW-DF-05 |
| DRV-220 | Q1 | Are test points, scope ground points and the debug pads (UART, SWD) reachable on the assembled board, on one side where a fixture needs it? | Test-access map | IW-BU-02, IW-BU-03, IW-DF-07; *T1:* PCB-T-01, PCB-T-02, PCB-T-03 |
| DRV-221 | Q1 | Are the audio test pads on the DAC side with stubs no longer than allowed and no series parts? | Pad positions and stub lengths | *T1:* PCB-A-12; BRD-040 |

## 4. Routing review

| ID | Level | Question | Evidence expected | Source |
|---|---|---|---|---|
| DRV-301 | Q0 | Does DRC (fab rules plus product rules) run clean, with the composed rule file current? | `kicad-cli pcb drc` report; `kicad-dru-composed` hook | E3.4, E3.5 |
| DRV-302 | Q1 | Is the stack-up the fab's quoted one, and is every signal layer adjacent to a ground plane? | Fab stack-up document; layer table | IW-SR-01, IW-SR-08; *T1:* PCB-S-04 |
| DRV-303 | Q1 | Does any fast or sensitive route cross a split or a void in its reference plane? | Plane-crossing check output or reviewed screenshots | IW-SR-02 |
| DRV-304 | Q1 | Does every signal via that changes reference layer have a ground stitching via within the class's distance, symmetric for pairs; and a stitching capacitor where the reference changes between ground and power? | Check output per via | IW-SR-03, IW-SR-04 |
| DRV-305 | Q1 | Is the reference plane voided under SMD pads on fast pairs (AC capacitors, ESD parts, connector pads)? | Void list per pad | IW-HS-02 |
| DRV-306 | Q1 | Do both members of each pair and every matched lane have the same via count? | Via count report | IW-HS-04 |
| DRV-307 | Q1 | Do impedance, length and skew meet every net class? | `CHK` report (E4.5) | *T1:* PCB-I-01 to PCB-I-09 |
| DRV-308 | Q1 | Is the master clock routed on an inner layer between ground planes, with spacing to other nets and no reference change (no unstitched guard trace counted as protection)? | Route screenshot and spacing | IW-CK-03, IW-SR-05; *T1:* PCB-I-09 |
| DRV-309 | Q1 | Is the analog area free of digital and switching traces on every layer? | Keep-out DRC and screenshot | *T1:* PCB-A-07 |
| DRV-310 | Q1 | Are the DAC references routed independently to each connector's ground pin? (*T1:* REFA/REFB) | Net routing | *T1:* PCB-A-03 |
| DRV-311 | Q1 | Are the left/right and leg paths symmetric in length and topology? | `CHK` report | *T1:* PCB-A-10; T1-050 |
| DRV-312 | Q1 | Are jack-detect lines away from the audio paths and protected at the jack? | Route screenshot | *T1:* PCB-A-11 |
| DRV-313 | Q2 | What is the copper resistance of any shared single-ended return between the reference point and the load, and what crosstalk does it give (R / Z_load)? | Calculation from the routed copper | IW-GA-06 |
| DRV-314 | Q1 | Is every switch node as small as its current allows, with only ground under it on the adjacent layer? | Screenshot per converter | IW-SW-02; *T1:* PCB-P-08 |
| DRV-315 | Q1 | Do power paths meet their current and via-count minimums? | DRC (net classes) and copper-area check | *T1:* PCB-P-01 to PCB-P-06, PCB-P-09 |
| DRV-316 | Q1 | Is each TVS grounded with its own vias straight into the ground plane, with no stub on the protected line? | Screenshot per TVS | IW-ES-01; *T1:* PCB-E-01 |
| DRV-317 | Q2 | Are the ground planes stitched with a via grid, densest along the board edge? | Stitching pitch report | IW-SR-07 |
| DRV-318 | Q1 | Are the copper connections to the two pads of every small passive balanced, and exposed-pad via arrays specified with their via treatment? | Review of 0201/0402 pads; fab notes | IW-DF-02, IW-TH-03 |
| DRV-319 | Q1 | Is any via in a pad specified filled and capped? | Fab notes | IW-DF-03 |
| DRV-320 | Q1 | Do pinouts of connectors carrying fast pairs give each pair adjacent ground contacts? | Pin map | IW-HS-01 |

## 5. Pre-fab release

| ID | Level | Question | Evidence expected | Source |
|---|---|---|---|---|
| DRV-401 | Q0 | Does the fab package come from `fab-package` with ERC, DRC and the BOM checks clean, at a tagged commit? | Package manifest and check log | `/opendap:fab-package` |
| DRV-402 | Q1 | Does the fab note name the stack-up, impedance classes with coupons, finish, acceptance class, via treatments and board thickness? | Fab note | *T1:* PCB-S-01 to PCB-S-08 |
| DRV-403 | Q1 | Is the revision marked in copper as well as in software? | Gerber view | IW-PD-05, IW-BU-06 |
| DRV-404 | Q1 | Does the assembly package list variants, DNP parts and the reflow side order? | Assembly drawing and BOM | *T1:* PCB-T-04; IW-DF-05 |
| DRV-405 | Q1 | Is X-ray inspection of BGAs and bottom-terminated parts ordered for the first article? | Order or quote line | IW-DF-04 |
| DRV-406 | Q1 | Has the fab's DFM report been answered item by item? | DFM report with answers | E8.1 |
| DRV-407 | Q1 | Are all schematic, placement and routing items at the target level passed or waived, and the debt above it listed? | Review records of §2–§4 | RFC 0010 |
| DRV-408 | Q1 | Does the build declare its target level in its release notes? | Release notes | RFC 0010 rule 2 |

## 6. First article

| ID | Level | Question | Evidence expected | Source |
|---|---|---|---|---|
| DRV-501 | Q1 | Do the bare board's dimensions, thickness and impedance coupons match the fab note? | Measurements; TDR of coupons | IW-HS-06; *T1:* V2-S01 |
| DRV-502 | Q1 | Are all parts present, correct and correctly oriented, against the BOM and assembly drawing? | Photos and inspection record | IW-PD-04 |
| DRV-503 | Q1 | Do the X-ray images of hidden joints show no opens, bridges or voids beyond the acceptance class? | X-ray images | IW-DF-04 |
| DRV-504 | Q0 | Is there no short between any rail and ground, measured unpowered? | Resistance per rail | IW-BU-01 |
| DRV-505 | Q1 | Is every rework and deviation recorded against the board's serial and revision? | Rework log | IW-PD-05 |

## 7. Bring-up

| ID | Level | Question | Evidence expected | Source |
|---|---|---|---|---|
| DRV-601 | Q0 | Is first power from a current-limited bench supply, never a pack, with the limit written for each step? | Bring-up log | IW-BA-05; *T1:* ADR 0014 item 4 |
| DRV-602 | Q0 | Is each rail brought up alone through its isolation link, with its voltage, idle current and start-up waveform recorded? | Per-rail record | IW-BU-01 |
| DRV-603 | Q1 | Is the power-up sequence captured against the design sequence? | Scope capture | *T1:* E8.2; ADR 0015 item 4 |
| DRV-604 | Q1 | Is every measurement taken with its expected value written beforehand? | Bring-up log with expected and observed columns | IW-BU-05 |
| DRV-605 | Q1 | Are ripple and noise measured with a short-ground probe technique? | Method noted with each capture | IW-PI-05 |
| DRV-606 | Q1 | Is the temperature of each hot part measured and converted to junction temperature with ψJT? | Thermal record | IW-TH-02 |
| DRV-607 | Q1 | Do the debug consoles and recovery paths work (UART, SWD, MaskROM or equivalent)? | Console logs | *T1:* PCB-T-01, PCB-T-03, BRD-047 |
| DRV-608 | Q1 | Are light-load converter bursts and their spurs at the audio output measured? | Spectrum at idle and playback | IW-SW-04; *T1:* ADR 0015 |
| DRV-609 | Q2 | Has a near-field scan of the board run with every domain active? | Scan images per area | IW-ES-05 |
| DRV-610 | Q2 | Is the sustained power at the agreed use cases measured against the device's surface-area budget? | Power per use case and surface temperature | IW-TH-01; *T1:* V4-03, V4-04 |
| DRV-611 | Q2 | Have ESD strikes at every connector at the target level left no damage and no unrecovered state? | ESD log | IW-ES-02, IW-ES-03; *T1:* V4-05 |
| DRV-612 | Q3 | Has a board-level drop test run, with a decision on BGA underfill? | Drop test report | IW-DF-08 |
| DRV-613 | Q1 | Does the bring-up report state the level the board reached and its debt? | Report | RFC 0010 |

## 8. Coverage of the T1 review items

Every `REV` item of the T1 PCB design constraints v0.4 has its checklist line:

| Constraint | Checklist |
|---|---|
| PCB-M-01, PCB-M-02, PCB-M-08 | DRV-201 |
| PCB-M-05, PCB-M-06 | DRV-202 |
| PCB-M-07 | DRV-203 |
| PCB-M-09 | DRV-205 |
| PCB-S-04 | DRV-302 |
| PCB-I-07 | DRV-215 |
| PCB-I-09 | DRV-210, DRV-308 |
| PCB-P-07 | DRV-207 |
| PCB-P-08 | DRV-314 |
| PCB-P-10 | DRV-211 |
| PCB-A-01 | DRV-206 |
| PCB-A-02, PCB-A-04 | DRV-209 |
| PCB-A-03 | DRV-114, DRV-310 |
| PCB-A-05 | DRV-115 |
| PCB-A-08, PCB-A-09 | DRV-208 |
| PCB-A-11 | DRV-312 |
| PCB-A-12 | DRV-221 |
| PCB-R-01, PCB-R-02, PCB-R-03 | DRV-215 |
| PCB-E-01 | DRV-212, DRV-316 |
| PCB-E-02 | DRV-103 |
| PCB-T-01, PCB-T-03 | DRV-220, DRV-607 |
| PCB-T-06 | DRV-217 |

When the constraints add or change a `REV` item, this table and the phase table change in the same session.
