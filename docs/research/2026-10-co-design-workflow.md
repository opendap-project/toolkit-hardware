# OpenDAP: co-design workflow across electronics, mechanics, firmware, software and OS

- **Date:** 2026-10-21
- **Scope:** how to keep the ~26 OpenDAP repositories (board, case, faceplates, hat-standard, HATs, system, blackbird-os, toolkit, ui-components) consistent while each domain evolves on its own; which tools and processes support that.
- **Status:** desk research. Nothing here is a decision. Section 8 contains **recommendations** for the maintainers to accept, change or reject (as ADRs in the relevant repositories).
- **Convention:** **UNVERIFIED** = no primary source found, or the claim comes from general knowledge and was not re-checked today. **(secondary source)** = only press, forum or blog coverage. Versions were read on 2026-10-21 from PyPI JSON, GitHub releases/tags, kernel.org `releases.json` or `git ls-remote`, unless stated otherwise.

> **Context taken from the repositories (not inferred).** BRD-001: no custom kernel builds; a board device tree and overlays are acceptable. BRD-004/BRD-006: the SoC reaches every chip on HATs directly; high-speed buses go straight from the SoC to the HAT interface. Board ADR 0002: HAT signals leave the board over a flat cable. hat-standard ADR 0001 (Proposed): the device-side piece exposes small-pitch two-row pogo pins; high-speed ports may be exposed the same way. case ADR 0002: the faceplate interface spec lives in `case` (`docs/specs/faceplate-interface.md`, pinout/dimensions/anchoring "not defined yet"). HCS-003: a HAT replaces the basic back cover with a HAT case. The SoC is **not selected** (board research `2026-10-soc-dac-pmic.md` lists i.MX 8M Plus as the leading candidate; it is used below only as an example where tooling depends on the SoC).

---

## 0. Executive summary

| Question | Short answer |
|---|---|
| Is there an off-the-shelf open-source tool that keeps a pinout consistent across KiCad (2 boards + FPC), FreeCAD, Rust firmware and Linux DT? | **No.** Every project studied either relies on human review or writes a small generator. The proven pattern is **one machine-readable interface file per interface** (YAML/CSV) owned by one repository, with **generators** for each consumer and **checkers** that compare what each tool actually contains (KiCad netlist, FreeCAD positions, compiled DTB) back to that file. |
| Building blocks that exist today | KiCad 10.0.7 `kicad-cli` (netlist, ERC/DRC JSON, STEP, SVG, jobsets); KiPart 2.8.0 (CSV → KiCad symbols); kicad-pinout-generator (PCB → Markdown/CSV/WireViz/Rust enum); WireViz 0.4.1 (YAML → harness/FPC drawings); KiCad StepUp (FreeCAD ↔ KiCad outline and 3D placement push/pull); FreeCAD 1.1.4 headless (`FreeCADCmd`) for STEP fit checks; dt-schema 2026.9 (`dt-validate`), `dtc`/`fdtoverlay`; Zephyr-style connector **nexus nodes** (`gpio-map`) and `gpio-line-names` as the DT side of a connector abstraction. |
| Code-defined electronics (SKiDL 3.0.0, atopile 0.15.9) | Worth knowing; **not recommended as the primary schematic source** for OpenDAP now — the board is KiCad 10 and contributors expect schematics. Useful for generating *the connector side* of an interface, not the whole board. |
| Requirements traceability | Existing Markdown tables (BRD-xxx, CASE-xxx, HCS-xxx) are a sound start. Mature open tools exist (StrictDoc 0.30.3, sphinx-needs 9.0.0, OpenFastTrace 4.11.0, Doorstop 3.2; SysON v2026.9.0 / Capella 7.1.0 for models). The cross-repo problem is mainly **ID registry + reference scanning**, which a small linter solves before any heavy tool is needed. |
| Co-simulation | QEMU 11.1.x has an `imx8mp-evk` machine; Renode 1.17.0 gained i.MX 8M Plus support (Antmicro, June 2026) and can co-simulate SoC + MCU; `dts2repl` turns a DT into a Renode platform. Both are useful **only once the SoC is chosen**. dt-schema validation and generated-file drift checks are useful **now**. |
| Change management | Semantic versioning of each *interface spec* (faceplate interface, HAT standard, board↔FPC), RFCs for cross-repo changes, a machine-readable compatibility matrix, and a release manifest that pins repository revisions (extend the workspace `repos.tsv` idea; `west` 1.5.0 is the closest open tool). Avoid git submodules for 26 repos. |
| Prior art that matches OpenDAP best | **Raspberry Pi HAT+** (ID EEPROM → DT overlay name), **BeagleBoard cape compatibility layer** (`bone_*` DT symbols, `/dev/bone/*`), **Zephyr `arduino-header-r3`** (connector nexus node), **PinePhone pogo-pin back covers** (same "replace the back cover" model as HCS-003), **MNT Reform** (per-hardware-revision firmware artifacts, SoM template), **Flipper Zero** (build fails when the exposed API changes until a human bumps the version), **Precursor** (generated Rust register map + Renode in CI). |

---

## 1. Single sources of truth for cross-domain interfaces

### 1.1 The problem, made concrete

One OpenDAP interface (e.g. board → HAT flat cable → device-side pogo piece) appears in at least seven artifacts:

1. KiCad schematic of the **main board** (connector symbol, net names).
2. KiCad schematic/PCB of the **FPC** and of the **device-side piece** (hat-standard reference design).
3. KiCad schematic of **each HAT** (seven repositories).
4. **FreeCAD**: connector body positions, cable bend/slot, pogo pin field, screw anchors (`case`, `case/hat-case`, each `hat-*` case).
5. **MCU firmware** pin configuration (Rust HAL) on the board and possibly on HATs.
6. **Linux device tree**: board `.dts` (SoC pinmux, `gpio-line-names`, connector node) and per-HAT **overlays** (`blackbird-os/overlays`).
7. **Documentation**: the human-readable spec (`hat-standard/spec`, `case/docs/specs/faceplate-interface.md`) and HAT developer docs.

Any manual copy drifts. The goal is: **one file is edited by humans; everything else is generated from it or checked against it.**

### 1.2 Interface control documents (ICD)

An ICD is the classical systems-engineering answer: one document per interface, owned by one party, defining electrical (pins, signals, voltage domains, current, impedance, timing), mechanical (connector part number, position, datum, tolerances, keep-outs) and logical (protocols, IDs, discovery) aspects, under change control. The weakness of a prose ICD is that tools cannot read it. Modern practice keeps the prose but makes the **tables** machine-readable (YAML/CSV/JSON validated by a schema), and renders the prose document's tables from that file. This is exactly what the existing `case/docs/specs/faceplate-interface.md` and `hat-standard/spec/` are positioned to become.

### 1.3 Machine-readable pinout formats and generators

There is **no standard open format** for "connector pinout across boards + DT + firmware" (searched GitHub and PyPI; none found — UNVERIFIED as an absolute claim). What exists, by direction:

| Direction | Tool | Version / status | Notes |
|---|---|---|---|
| CSV → KiCad symbol | **KiPart** ([PyPI](https://pypi.org/project/kipart/)) | 2.8.0 (2026-08-08) | "Converting rows of CSV pin data into KiCad symbols and back." Lets the interface file generate the connector symbol for every board that carries it. |
| KiCad PCB → pinout docs/code | **kicad-pinout-generator** ([GitHub](https://github.com/CGrassin/kicad-pinout-generator)) | plugin, last push 2026-04 | Outputs Markdown, HTML, CSV, **WireViz**, C/C++ enums/defines, Python dict, **Rust enum**, FPGA XDC/PDC. **No device-tree output.** Useful as a *checker* (extract what the PCB really has). |
| YAML → cable/harness drawings + BOM | **WireViz** ([GitHub](https://github.com/wireviz/WireViz)) | 0.4.1 (2024-07-13; no newer release) | YAML in, SVG/PNG/HTML + BOM out. Fits the board↔faceplate and board↔HAT flat cables: connectors, pin labels, pin-to-pin mapping (including the pin reversal of same-side vs opposite-side contact FPCs). Slow release cadence. |
| KiCad netlist parsing | **kinparse** ([PyPI](https://pypi.org/project/kinparse/)) 1.2.4; `kicad-cli sch export netlist` | — | Basis for a "does the schematic match the interface file?" checker. |
| KiCad file manipulation | **kicad-python** (official IPC API bindings, [PyPI](https://pypi.org/project/kicad-python/)) 0.8.0 (2026-08-30); kicad-skip 0.2.5 (2024, stale); kiutils 1.4.8 (2024, stale) | — | IPC API requires a running KiCad; for CI prefer `kicad-cli` exports + parsing. |
| Netlist → device tree | **none found** | — | No maintained KiCad-netlist-to-DTS generator was found (UNVERIFIED). In practice the DT fragment for a connector is generated from the *interface file*, not from the netlist, and the netlist is only checked against the same file. |
| Interface file → Rust consts | write-your-own (`build.rs` or committed generated module) | — | Prior art: Embassy's `stm32-data` generates the `stm32-metapac` crate from YAML descriptions (UNVERIFIED current layout); Precursor's `utralib` is a generated register crate per target ([xous-core/utralib](https://github.com/betrusted-io/xous-core/tree/main/utralib), contents include `precursor/`, `build.rs`; generated from SVD by `svd2utra`). |

**What the OpenDAP interface file needs to describe** (independent of tool choice): per pin — position (1..N, row A/B for pogo), signal name, signal class (power, ground, GPIO, I²C, I²S/TDM, USB 2/3 pair, PCIe lane/refclk, MIPI CSI/DSI lane), direction, voltage domain, max current, diff-pair partner and impedance target, "reserved" flag; per interface — connector part numbers on each side, pitch, cable type and contact side, mechanical datum and positions, the ID/discovery mechanism, and the interface **version**. Per *board revision*, a separate mapping file binds each signal to the SoC ball / pinmux function / GPIO bank-line. Keeping "the interface" and "how a given board implements it" in two files is what lets several board revisions (and third-party hosts, later) implement one standard.

### 1.4 Code-defined electronics: SKiDL and atopile

| Tool | Version | What it is | Fit for OpenDAP |
|---|---|---|---|
| **SKiDL** ([GitHub](https://github.com/devbisme/skidl), [PyPI](https://pypi.org/project/skidl/)) | 3.0.0 (2026-10-16) | Python library that describes circuits in code and emits KiCad netlists (and, in recent versions, schematics — UNVERIFIED for 3.0). 2.0 added `Interface` objects that can be connected directly. KiCad 10 library support in 3.0: UNVERIFIED. | Good for *generating* repetitive connector/breakout circuits from the interface file (e.g. a HAT template's connector page). Not a replacement for the hand-drawn board schematic. |
| **atopile** ([GitHub](https://github.com/atopile/atopile), [docs](https://docs.atopile.io/)) | 0.15.9 (2026-09-12, PyPI) | Language (`.ato`) + compiler that produces KiCad PCB projects, with a package registry, interfaces and constraint assertions (e.g. `330ohm +/- 5%`); projects configured by `ato.yaml`. Self-described pre-release. | Interesting for the HAT ecosystem long term ("a HAT interface is a typed module third parties import"). Risky as core flow today: pre-1.0, layout still done in KiCad, KiCad 10 compatibility UNVERIFIED. |

### 1.5 KiCad across projects

- **Hierarchical sheets shared between projects** are technically possible (a sheet file referenced by relative path from two projects) but fragile: annotation/UUID collisions and silent edits from one project affecting the other (UNVERIFIED as documented behaviour; widely reported by users). Not recommended for cross-repository sharing.
- **Shared libraries** are the robust unit: the interface-owning repository ships the connector **symbol, footprint and STEP model** (generated where possible), consumers add it to their project `sym-lib-table`/`fp-lib-table` via a path variable that points to a **pinned** copy.
- **Design Blocks** (schematic in KiCad 9, extended to the **PCB editor in KiCad 10** — [KiCad 10.0.0 release notes](https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/)) are the native way to reuse a circuit + layout snippet, e.g. "HAT-side connector + ESD + ID EEPROM" in every HAT.
- **Design Variants** (new in KiCad 10, same source) can express board revisions or assembly options sharing one schematic.
- KiCad 10 ships **STEP-only 3D models** (same source), which simplifies the MCAD round trip.
- Latest patch release: **10.0.7** (from `git ls-remote` of the KiCad GitLab; 10.0.6 announced [2026-08](https://www.kicad.org/blog/2026/08/KiCad-10.0.6-Release/)).
- Native multi-board projects (several PCBs + cable in one design with cross-board connectivity checks) are **not** mentioned in the KiCad 10 release notes; treat as unavailable (UNVERIFIED).

### 1.6 ECAD ↔ MCAD: KiCad ↔ FreeCAD

| Need | Tool / method | Notes |
|---|---|---|
| Board outline, mounting holes, keep-outs authored in MCAD and pushed to KiCad (or the reverse) | **KiCad StepUp** workbench ([FreeCAD wiki](https://wiki.freecad.org/KicadStepUp_Workbench), [KiCad external tools](https://www.kicad.org/external-tools/stepup/)); repository `easyw/kicadStepUpMod` last push 2026-09-04 | PUSH/PULL of the PCB edge as a FreeCAD sketch; push/pull of 3D model placements; load boards/footprints in FreeCAD; export STEP. Interactive (GUI) — not a CI tool. FreeCAD 1.1 compatibility: assumed from active maintenance (UNVERIFIED). |
| Board 3D for fit checks | `kicad-cli pcb export step` | Deterministic, headless; produces the STEP the case repository consumes. |
| Fit/interference check in CI | **FreeCAD 1.1.4** ([release](https://github.com/FreeCAD/FreeCAD/releases)) headless `FreeCADCmd` script, or **CadQuery 2.8.0** / **build123d 0.13.0** (OCCT-based, PyPI) | Import case STEP + board STEP, compute boolean intersection volume, measure connector-to-slot offsets against the interface file's datums. Fails the PR if volume > 0 or offset > tolerance. |
| Legacy exchange | KiCad IDFv3 export (UNVERIFIED in KiCad 10 menus); ProSTEP **IDX** (incremental ECAD/MCAD collaboration) is **not** supported by KiCad or FreeCAD (UNVERIFIED) | STEP + a shared parameter file is the practical open-source substitute. |

**Ownership rule that works in practice** (Framework publishes the expansion-card outline, hole positions and keep-outs as drawings + KiCad + STEP + DXF: [ExpansionCards](https://github.com/FrameworkComputer/ExpansionCards); the card spec gives exact hole coordinates and keep-out diameters): *mechanics owns the envelope* (outline, mounting holes, height zones, connector datum positions), *electronics owns placement inside it*. Both read the numbers from the same interface file; the STEP files are build artifacts, not sources.

### 1.7 Linux side: device tree and overlays without custom kernels

Because BRD-001 rules out custom kernel builds, the whole board-support surface is DT (+ userspace). Relevant facts:

- **Connector abstraction in DT.** The DT spec's *nexus node* / specifier-mapping mechanism (`gpio-map`, `gpio-map-mask`, `gpio-map-pass-thru`) lets an overlay reference "connector pin 7" instead of "gpio3 12". Zephyr uses it for `arduino-header-r3` so that shields work on any board ([Zephyr shields porting guide](https://docs.zephyrproject.org/latest/hardware/porting/shields.html)). Linux supports `gpio-map` in its GPIO core (UNVERIFIED for every consumer; well established for GPIO).
- **BeagleBoard cape compatibility layer**: base DTs export indexed symbols (`bone_i2c_#`, `bone_spi_#`, `bone_pwm_#`) in `bbb-bone-buses.dtsi` etc., overlays use generic names (`BONE-I2C1`), and udev rules create `/dev/bone/i2c/1` that maps to I2C1 on Black, I2C5 on AI, MAIN_I2C6 on AI-64 ([cape interface spec](https://docs.beagleboard.org/boards/capes/cape-interface-spec.html)). This is the closest existing model for "one HAT overlay works across OpenDAP board revisions".
- **Local overlay symbols for connectors.** Hervé Codina's `export-symbols` series (v1 Dec 2024, v2 Apr 2025, [LKML](https://lkml.iu.edu/hypermail/linux/kernel/2412.1/01636.html)) and his 77-patch RFC "dtb metadata and addon device-trees" (Jan 2026, [LKML](https://lkml.iu.edu/2601.1/04737.html)) target exactly the "base board + connector + add-on board" case (mikroBUS, Grove). **Mainline status in 7.3: UNVERIFIED — assume not available.**
- **Runtime overlay loading**: mainline Linux has no generic userspace (configfs) interface to apply overlays; that interface remains out of tree (UNVERIFIED for 7.3, long-standing). Practical consequence: overlays for HATs/faceplates are applied **by the bootloader** (U-Boot `fdt apply`, U-Boot "extension board" detection — [Bootlin, 2021](https://bootlin.com/pub/conferences/2021/lee/maincent-devicetree-overlay-and-uboot-extension-board-management/maincent-devicetree-overlay-and-uboot-extension-board-management.pdf)) or by a mainline driver that applies its own overlay. HAT hot-plug is therefore an open architectural question for `hat-standard` + `blackbird-os`, not a tooling detail.
- **`gpio-line-names`** expose meaningful names to userspace through the GPIO character device / libgpiod; the binding text recommends function names over `GPIO0`-style names ([LKML 2023 patch](https://lkml.iu.edu/hypermail/linux/kernel/2302.1/04065.html)). Generating `gpio-line-names` from the interface file gives `system` (Rust services) stable names across board revisions.
- Kernel reference: mainline **7.3** released 2026-10-18; stable 7.2.12; longterm 6.18.58 ([kernel.org releases.json](https://www.kernel.org/releases.json)).

---

## 2. Requirements traceability across repositories

### 2.1 Tools

| Tool | Version (2026-10-21) | Source format | Cross-repo | Code/test links | Notes |
|---|---|---|---|---|---|
| **StrictDoc** ([GitHub](https://github.com/strictdoc-project/strictdoc), [docs](https://strictdoc.readthedocs.io/)) | 0.30.3 (2026-10-18) | `.sdoc` text (also RST; ReqIF import/export) | Multi-document trees; cross-repo by checking out several repos into one tree (UNVERIFIED as a first-class feature) | `@relation(REQ-ID, scope=...)` markers in any source file; language-aware parsing for Python and C, a Rust reader exists in the code base (`reader_rust.py`) | Traceability matrices, web UI, used for Zephyr requirements demos. Strongest fully-open option for formal traceability. |
| **sphinx-needs** ([GitHub](https://github.com/useblocks/sphinx-needs)) | 9.0.0 (2026-10-14, PyPI); sphinx-test-reports 3.0.0 | RST or Markdown (MyST directives) | **Yes**: `needs_external_needs` imports another project's `needs.json` | Via `needs` items for tests, sphinx-test-reports (JUnit) | `needs_id_regex` + `needs_id_required` enforce ID shapes. Good fit if docs move to Sphinx. |
| **OpenFastTrace** ([GitHub](https://github.com/itsallcode/openfasttrace)) | 4.11.0 (2026-10-18) | **Markdown** specs (`req~name~1`) | Reads many input directories at once | Tags in code: `[impl->dsn~name~1]` | Revisioned IDs (`~1`) make "requirement changed, coverage stale" explicit. Java CLI. ID shape differs from BRD-001. |
| **Doorstop** ([GitHub](https://github.com/doorstop-dev/doorstop)) | 3.2 (2026-07-10) | One YAML file per item, in git | Parent/child documents in one tree | References to files | Simple, git-native; IDs are prefix + number (close to BRD-001). |
| **reqif** ([PyPI](https://pypi.org/project/reqif/)) | 0.1.0 (2026-08-11) | ReqIF | — | — | Exchange format if a partner uses DOORS/Polarion. |
| **Eclipse Capella** ([GitHub](https://github.com/eclipse-capella/capella)) | 7.1.0 (2026-08-03) | Arcadia model | — | — | Model-based (operational → system → logical → physical). Heavy for a small team. |
| **Eclipse SysON** ([GitHub](https://github.com/eclipse-syson/syson)) | v2026.9.0 (2026-09-09) | SysML v2 (web, Sirius Web) | API (SysML v2 API & Services spec) | — | OMG adopted SysML v2.0 / KerML 1.0 / API 1.0 in July 2025, published Sept 2025 ([OMG press release](https://www.omg.org/news/releases/pr2025/07-21-25.htm)). SysON site still says "not yet intended for production use" ([mbse-syson.org](https://mbse-syson.org/)). Pilot implementation: [SysML-v2-Release](https://github.com/systems-modeling/SysML-v2-Release) 2026-08. |

### 2.2 Linking requirement IDs to non-code artifacts

| Artifact | Where the ID can live | How CI extracts it |
|---|---|---|
| KiCad symbol / sheet | A custom **symbol field** (e.g. `Req = BRD-011`) on the parts that satisfy it (headphone jack, amp), or a field on a hierarchical sheet | `kicad-cli sch export bom --fields ...` or netlist export (fields are carried into the netlist); parse with kinparse |
| KiCad net | Net names cannot carry metadata; use a **net class** or a text/field on the connector symbol; or keep "net ↔ requirement" in the interface file | netlist + interface file |
| KiCad PCB rule | KiCad 10 graphical **custom rule editor** ([release notes](https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/)); rule names/comments can cite the ID (e.g. impedance rule for HCS-004) | parse `.kicad_dru` |
| FreeCAD feature | `Label2` (description) or a custom string property (`App::PropertyString` "Requirement") on the body/feature | `FreeCADCmd` script, or `fcinfo` text dump |
| Rust code / tests | Doc comment or attribute convention (`// Implements: BRD-010`, `#[doc = "Verifies: HCS-004"]`) | regex scan (StrictDoc `@relation`, OFT tags, or own linter) |
| DT / overlay | Comment above the node (`/* BRD-008: power-gated block */`) | regex scan |
| Bring-up / HIL results | Test IDs in JUnit XML that carry the requirement ID | sphinx-test-reports / own report |

### 2.3 Keeping IDs stable across repositories

- **One prefix per repository (or per document), registered once.** Today: `BRD` (board), `CASE` (case), `HCS` (hat-standard). A small registry (prefix → owning repository → document) prevents two repos from inventing the same prefix and lets a linter resolve `HCS-004` to a URL from anywhere.
- **IDs are never reused or renumbered.** Withdrawn requirements keep their row with status `Withdrawn`/`Superseded by X`. All four tools above follow this rule; OpenFastTrace additionally versions the item (`~2`) when the meaning changes.
- **Cross-repo references are qualified by prefix, not by path** (`HCS-004`, not `../hat-standard/...#4`), so moving files does not break links.
- **A requirement that constrains several repositories lives in the repository that owns the interface** (case ADR 0002 already applies this to the faceplate interface) and is *referenced*, never copied, by consumers.

---

## 3. Hardware/firmware/software co-simulation and early integration

### 3.1 Emulators

| Tool | Version | Relevant capability | Fit |
|---|---|---|---|
| **QEMU** | v11.1.2 (latest tag) | `imx8mp-evk` machine (4× A53, GICv3, UART, uSDHC, DesignWare PCIe, Ethernet, 2× DWC3 USB 3, GPIO, 6× I2C, SPI, watchdogs, SNVS RTC, clock tree), boots Linux with `-kernel` + `-dtb`; also `imx8mm-evk` ([docs](https://www.qemu.org/docs/master/system/arm/imx8mp-evk.html)) | If i.MX 8M Plus is chosen: boot Blackbird OS images in CI, run `system` services, test DT-dependent userspace. No audio codec or display models (UNVERIFIED). Upstream merge ~QEMU 10.0 (2025, [patch series](https://patchew.org/QEMU/20250223114708.1780-1-shentey@gmail.com)). |
| **Renode** ([GitHub](https://github.com/renode/renode)) | v1.17.0 (2026-09-07) | i.MX 8M Plus SoC + FRDM board descriptions, enough for U-Boot with MMC and Linux "with certain limitations" ([Antmicro, 2026-06](https://antmicro.com/blog/2026/06/renode-support-for-nxp-imx8m-plus)); multi-node, deterministic, models MCUs (STM32 families; RP2350 UNVERIFIED) and buses; Robot Framework tests | Co-simulate **SoC + supervisor MCU** over I²C/UART in one deterministic run — the closest open option to "board firmware + Linux talk to each other before hardware exists". Precursor used Renode for Xous CI ([Antmicro 2022](https://antmicro.com/blog/2022/03/precursor-developing-advanced-products-with-renode/), [xobs.io](https://xobs.io/precursor-and-renode/)). |
| **dts2repl** ([GitHub](https://github.com/antmicro/dts2repl)) | Antmicro, maintained | DT → Renode `.repl` platform | Feeds Renode from the **same DT** the generator produces — closes the loop "interface file → DT → emulator". |
| **cocotb** ([PyPI](https://pypi.org/project/cocotb/)) | 2.1.0 (2026-08-30) | HDL co-simulation | Only if a HAT carries an FPGA (oscilloscope/VNA HATs might). |
| Circuit sims in `board/sim` | ngspice / Qucs-S / openEMS (not version-checked here) | analog, power, SI | Out of scope of this report; mention for completeness. |

### 3.2 Device tree validation (works now, no SoC model needed)

- **dt-schema** ([PyPI dtschema](https://pypi.org/project/dtschema/)) **2026.9** (2026-09-18) provides `dt-validate`; the kernel's `make dtbs_check` runs it against `Documentation/devicetree/bindings` and also handles `.dtbo` ([scripts/Makefile.dtbs](https://gbmc.googlesource.com/linux/+/refs/heads/master/scripts/Makefile.dtbs)). Note: the GitHub "latest release" of `devicetree-org/dt-schema` shows v2022.08.1 because releases are no longer created there; tags go to v2026.09.
- Without custom kernel builds, `blackbird-os` can still: (1) check out the matching mainline tag (for `include/dt-bindings` and binding schemas), (2) compile the board DTS out of tree with `cpp` + `dtc -@`, (3) apply every overlay with `fdtoverlay` against every supported base DTB (catches overlays that reference missing labels), (4) run `dt-validate` on each merged result. Upstreaming the board DTS later makes this the kernel's own `dtbs_check`.
- **lopper** (devicetree-org, tag v1.6.0) can transform/prune DTs if the build ever needs per-domain DTs (e.g. Cortex-M7 side) — optional.

### 3.3 Hardware-in-the-loop

| Tool | Version | Use |
|---|---|---|
| **labgrid** ([PyPI](https://pypi.org/project/labgrid/)) | 26.0.1 (2026-10-14) | Pengutronix's open HIL framework: power switching, USB/SD-mux, serial, pytest integration. Fits a small bench (one board + faceplate + HAT per DUT). |
| **LAVA** ([GitLab](https://gitlab.com/lava/lava)) | 2026.10 | Linaro's board farm; heavier, kernel-CI style. |
| **probe-rs** ([GitHub](https://github.com/probe-rs/probe-rs)) | v0.32.0 (2026-07-22) | Flash/debug the Rust MCU firmware in HIL jobs; `embedded-test`-style on-target tests (UNVERIFIED crate status). |
| **pytest-embedded** 2.9.3, **Robot Framework** 7.5 | — | Test runners; Robot is what Renode uses, so tests can run against emulator first and bench later. |

### 3.4 Bring-up checklists (shape, not content)

Derived from the interface file so they cannot drift: one row per signal (power rail sequence and voltage; each I²C address responds; each GPIO line toggles and reads back via its `gpio-line-names` name; each high-speed link trains — USB 3 enumerates SuperSpeed, PCIe link width/speed, MIPI CSI frames — with HCS-004's "measured at the end" numbers recorded; ID EEPROM read; overlay applied). The same rows become HIL test cases and the evidence for requirement verification.

---

## 4. Change management across many repositories

### 4.1 Interface versioning

- Version the **interface specs**, not the repositories: `faceplate-interface` (owned by `case`), `hat-standard` (owned by `hat-standard`), and the board↔FPC/device-side link if it is specified separately.
- **SemVer adapted to hardware**: MAJOR = a conforming accessory may stop working (pin moved, connector changed, voltage changed, mechanical datum moved); MINOR = backwards-compatible addition (a previously reserved pin gets an optional function, new optional ID field); PATCH = clarification with no physical change. `0.x` = no compatibility promise (where both specs are today).
- **Carry the version in hardware** where possible: Raspberry Pi HAT+ EEPROM holds product UUID, product ID, product version, vendor, description and the **DT overlay name**; the overlay itself lives on the OS filesystem (`/boot/firmware/overlays`), not in the EEPROM; EEPROM I²C address suffix `101_00XY` encodes the HAT+ class, including a stackable class ([HAT+ specification](https://pip.raspberrypi.com/documents/RP-008281-DS-hat-plus-specification.pdf), build 2024-12-05; the original HAT spec is deprecated). BeagleBone capes carry an ID EEPROM read by U-Boot to pick overlays ([forum](https://forum.beagleboard.org/t/bbb-cape-eeprom-and-fdt-overlays/1632)). How faceplates and HATs identify themselves to OpenDAP is **not defined yet** in the repositories — an maintainers' decision.
- **Machine-enforced API versioning** (software analogue): Flipper Zero's `api_symbols.csv` carries a major.minor API version; when exposed headers change, the build **stops** until a human marks each new symbol `+`/`-` and bumps the version; the app loader refuses apps whose major version differs ([Flipper developer docs](https://developer.flipper.net/flipperzero/doxygen/apps_on_sd_card.html); firmware 1.5.1, 2026-10-15). The same idea applies to the interface file: CI computes a diff and refuses a merge whose version bump is smaller than the change class.

### 4.2 Cross-repository change proposals (RFC)

Prior art: Rust RFCs, Python PEPs, Kubernetes KEPs (one central `enhancements` repository tracking changes that land in many repositories), Zephyr RFC issues. Common shape: a numbered proposal with motivation, affected interfaces/repos, compatibility impact (which version bump), migration plan, and a tracking list of the PRs in each repo. A change to an interface file **without** an accepted RFC (beyond PATCH) is blocked by CODEOWNERS review.

### 4.3 Compatibility matrices

The matrix *board rev × faceplate (variant, rev) × HAT-standard version × each HAT rev × Blackbird OS version* explodes quickly; maintain it **derived, not hand-written**:

- Each hardware repository declares, per revision, which interface versions it **provides** or **requires** (`board rev B provides faceplate-interface 1.x, hat-standard 1.2`; `hat-radio rev A requires hat-standard >=1.1,<2`).
- Each Blackbird OS release declares which board revisions it supports and which overlays it ships.
- A tool computes the matrix; HIL results mark tuples as *tested*, *expected* (semver-compatible but untested) or *incompatible*.
- MNT Reform shows the artifact side of this: a single CI pipeline builds firmware per hardware revision with the revision in the file name (e.g. `reform2-lpc-fw/firmware-20_R3.bin`, `firmware-25_R2.bin`, `firmware-30_R1.bin`; keyboard firmware for keyboard-2/3/4 variants) ([`.gitlab-ci.yml`](https://source.mnt.re/reform/reform/-/raw/main/.gitlab-ci.yml)).

### 4.4 Release trains

Hardware revisions are slow and expensive; OS and services are fast. Common practice: **time-based releases for software** (Blackbird OS, system) and **milestone-based revisions for hardware**, joined by a **platform release** = a manifest of exact revisions that were integration-tested together (Zephyr LTS + `west` manifests; Yocto/kas; Android `repo` manifests). Each platform release publishes its compatibility rows.

### 4.5 Dependency pinning between repositories

| Mechanism | Good for | Problems at OpenDAP scale |
|---|---|---|
| **git submodules** | A few tightly-coupled, rarely-changing dependencies (e.g. a KiCad library) | Detached-HEAD confusion, recursive clones, 26 repos × N consumers becomes unmanageable; poor fit for non-developers (mechanical/electrical contributors). |
| **Manifest** (`west` 1.5.0 [PyPI](https://pypi.org/project/west/); Google `repo`; or the workspace `repos.tsv` extended with a revision column) | Pinning a whole set of repos for a platform release or an integration CI run; easy overrides for "test these three PR branches together" | Needs tooling; `west` is Zephyr-oriented but generic. |
| **Packages / release artifacts** | Interfaces consumed by many repos: a versioned tarball (interface file + generated KiCad lib + DT fragments + Rust crate + docs) attached to a GitHub release; Rust consumers pin a git tag or a crate version; KiCad consumers pin the library copy | Need a publish step in the maintainers repo's CI; clearest semantics ("hat-radio uses hat-standard 1.2.0"). |
| **Vendored generated copy + checksum** | KiCad and FreeCAD projects that must open offline in the GUI | Must be guarded by a CI check that the vendored copy matches the pinned release. |

---

## 5. How notable open projects handle it

| Project | Repo structure | Interface definition | Versioning / discovery | Integration / verification | Lesson for OpenDAP |
|---|---|---|---|---|---|
| **MNT Reform** | Many repos on [source.mnt.re](https://source.mnt.re/reform) (reform hardware+firmware, `reform-system-image`, per-SoC U-Boot repos, `reform-som-template`, handbooks, `reform-debian-packages`, `reform-test-devices`, `mnt-flash-and-test`) — read via GitLab API | Processor modules plug into the motherboard; `reform-som-template` is "a KiCAD template for creating new system-on-modules … plug new processor and memory combinations into the laptop" | Board revisions encoded in firmware artifact names | One CI builds all firmware variants; dedicated flash-and-test and test-devices repos | **Template repository for third-party modules** (→ a `hat-*` template in `toolkit/templates`), and per-revision artifacts. CERN-OHL-S-2.0 like OpenDAP. |
| **Framework** | [ExpansionCards](https://github.com/FrameworkComputer/ExpansionCards) (KiCad, STEP, DXF, CC-BY-4.0), [framework-laptop-13](https://github.com/FrameworkComputer/framework-laptop-13), [Mainboard](https://github.com/FrameworkComputer/Mainboard) (pinouts + 2D drawings) | Mechanical envelope + USB-C as the electrical interface | Interface is USB-C, so discovery is USB | Developer program, prototype before production | **Publish the envelope as drawings + STEP + DXF + KiCad template**; choose an electrical interface with existing discovery when possible. |
| **Pine64 PinePhone** | Wiki-centric | Six pogo pins on the back: INT, SDA, SCL / VBUS, VBAT, GND; add-on back covers need the same dimensions and latch positions and use I²C ([wiki](https://wiki.pine64.org/wiki/PinePhone_(Pro)_Add-ons), [keyboard](https://wiki.pine64.org/wiki/PinePhone_(Pro)_Keyboard)) | No formal versioning found (UNVERIFIED) | Community drivers per add-on | Same "replace the back cover" model as HCS-003; shows that a **too-minimal, unversioned** interface limits add-ons — OpenDAP's high-speed ambitions (HCS-004) need explicit versioning. |
| **Precursor / betrusted** | `betrusted-io/*` (hardware, `xous-core`) | SoC is RTL (LiteX) → SVD → generated Rust register crate `utralib` per target | Generated, so always matches the gateware | Renode emulation in CI for Xous ([Antmicro 2020](https://antmicro.com/blog/2020/12/precursor-and-renode)) | **Generate firmware constants from the hardware description**, and emulate before hardware. |
| **Raspberry Pi HAT+** | Spec PDF + EEPROM tools | 40-pin header; ID EEPROM on GPIO0/1 only | EEPROM: UUID, product ID/version, vendor, description, overlay name; firmware loads the named overlay from the OS | "Only boards that follow the HAT+ specification can be marketed as HAT+" | **Self-identifying accessories + overlay chosen by name**; certification by marking. |
| **BeagleBoard capes** | [Cape interface spec](https://docs.beagleboard.org/boards/capes/cape-interface-spec.html), BeagleBoard-DeviceTrees | Indexed DT symbols, generic overlay names | EEPROM per cape (up to four stacked on AI-64), U-Boot applies overlays | `/dev/bone/*` udev symlinks | **Cross-board abstraction layer** so one accessory overlay works on several host revisions. |
| **Arduino (UNO Q / Zephyr)** | Board upstream in Zephyr (`boards/arduino/uno_q`); UNO Q runs Debian on QRB2210 + Zephyr on STM32U585 ([docs](https://docs.arduino.cc/hardware/uno-q/)) | `arduino-header-r3` nexus node | Shield overlays reference the connector node | Upstream CI | **Upstreaming the board description** makes others maintain it with you; connector nexus pattern. Forum reports that Linux-side overlays on UNO Q are awkward ([forum](https://forum.arduino.cc/t/uno-q-device-tree-overlay-help-linux/1426212), secondary source). |
| **Librem 5** | Dev kit KiCad sources GPL-3.0+ ([dvk-mx8m-bsb](https://source.puri.sm/Librem5/dvk-mx8m-bsb)); phone: PDF schematics + STEP only ([Purism](https://puri.sm/posts/purism-releases-step-file-for-librem-5/)) | — | — | Mainline kernel effort | Openness of the *final* product's sources matters more than of a dev kit; release editable sources, not only PDFs. |
| **Flipper Zero** | `flipperdevices/flipperzero-firmware` (1.5.1) | GPIO header + `api_symbols.csv` for the app ABI | API major/minor, enforced by build tool and loader | — | **Build-enforced interface versioning**. |

---

## 6. Review workflow

### 6.1 Multi-disciplinary design reviews

Typical gate sequence for open hardware with external contributors (no single source; synthesis of common practice):

1. **Requirements review** — new/changed IDs, owner repo, acceptance criteria.
2. **Interface review** — any change to an interface file: electrical + mechanical + OS + firmware reviewers all required.
3. **Schematic review** — ERC clean, interface checker clean, requirement fields present.
4. **Layout + MCAD fit review** — DRC clean, STEP fit check against the current case, connector datums within tolerance.
5. **Pre-fabrication review** — fab outputs, BOM availability, DFM, visual diff vs last fabbed revision.
6. **Bring-up review** — bring-up checklist results, deviations become issues/ERRATA.
7. **Release review** — compatibility rows updated, platform manifest tagged.

Enforced with **CODEOWNERS** on interface paths (e.g. `hat-standard/spec/**` requires board + case + blackbird-os owners), PR templates with the gate checklist, and labels for cross-repo changes.

### 6.2 Visual diffs in PRs

| Domain | Open-source option | Version | Notes |
|---|---|---|---|
| KiCad schematic + PCB | **KiBot** ([GitHub](https://github.com/INTI-CMNB/KiBot)) with `diff` outputs (uses **KiDiff**, [PyPI kidiff](https://pypi.org/project/kidiff/) 2.6.0) | KiBot 1.9.1 (2026-07-28) | Also runs ERC/DRC, generates fab outputs, iBoM, 3D renders, STEP. Single YAML config per repo; Docker images. KiCad 10 support in 1.9.x: UNVERIFIED (check changelog). |
| KiCad, interactive | **KiRI** ([GitHub](https://github.com/leoheck/kiri)) | 1.0.0 tag (2021) but maintained; uses `kicad-cli` for schematics and KiCad-Diff for layout | Local browser-based revision inspector; can be published as a CI artifact. |
| KiCad, native | `kicad-cli sch export svg`, `pcb export svg`, `jobset run` (KiCad 9+) ([CLI docs](https://docs.kicad.org/9.0/en/cli/cli.html)) | 10.0.7 | Build blocks for a custom image-diff. |
| PCB presentation | **InteractiveHtmlBom** 2.12.0, **pcbdraw** 1.3.0, **KiKit** 1.8.1 (panelization, fab presets) | — | Review artifacts attached to PRs. |
| FreeCAD | **fcinfo** as git `textconv` (`*.FCStd diff=fcinfo`) gives a text diff of the document ([FreeCAD Arch Git](https://wiki.freecad.org/Arch_Git), [blog](https://blog.lambda.cx/posts/freecad-and-git/)); **GitCAD** stores uncompressed FCStd via clean filters ([GitHub](https://github.com/MikeOpsGit/GitCAD)); headless `FreeCADCmd` renders/TechDraw PDFs + STEP/STL export | FreeCAD 1.1.4 | STL files render and diff in GitHub's 3D viewer (UNVERIFIED current behaviour). Blender renders in `case/renders` can be regenerated in CI for before/after images. |
| Proprietary, for awareness | AllSpice Hub (KiCad diff/review, Gitea-based); **KiHub** (launched 2026-08-19, secondary source via search) | — | Not open source; not recommended as a dependency. |

### 6.3 Checklists

Keep checklists as Markdown in the owning repo (`docs/checklists/`), referenced from PR templates; items should be **testable** and cite requirement IDs. Automate any item a script can check (ERC/DRC, interface conformance, fit check, DT validation, REUSE compliance with `reuse` 6.2.0), so human review focuses on judgement items (signal integrity choices, ergonomics, aesthetics, serviceability).

---

## 7. Gaps and risks found

- **No open tool closes the KiCad ↔ FreeCAD ↔ DT ↔ Rust loop.** A small generator/checker suite has to be written and maintained; keep it small and schema-driven.
- **Overlay application without custom kernels** constrains HAT hot-plug and faceplate detection (bootloader-applied overlays are the safe mainline path today). The addon/connector DT work upstream is promising but not merged (UNVERIFIED).
- **WireViz** is slow-moving (0.4.1 from 2024); fine for documentation, do not make it a hard dependency of the consistency checks.
- **Emulation depends on the SoC choice**; i.MX 8M Plus has both QEMU and Renode models today, RK3576 support in either was not found (UNVERIFIED).
- **Contributor experience**: mechanical/electrical contributors work in GUIs. Every generated file they open (KiCad library, FreeCAD parameter spreadsheet) must be vendored and openable offline; CI, not the contributor, regenerates and checks.

---

## 8. Recommended co-design process and tooling for OpenDAP

> **These are recommendations, not decisions.** Each item that the maintainers accepts should become an ADR in the repository named, and requirements where appropriate. Items marked *(owner question)* need a decision the maintainers has not taken yet.

### R1. One machine-readable interface file per interface, owned by one repository

| Interface | Owner repo (per existing ADRs) | Source of truth (recommended) |
|---|---|---|
| Faceplate interface (flat cable pinout, dimensions, screw anchoring) | `case` (ADR 0002) | `case/docs/specs/faceplate-interface.yaml` + the existing `.md` rendered from it |
| HAT standard (device-side pogo field, HAT case mechanics, ID mechanism) | `hat-standard` | `hat-standard/spec/hat-interface.yaml` |
| Board → HAT flat cable / device-side piece link | `hat-standard` (it defines the device-side piece; board ADR 0002 defines that the cable exists) *(owner question: or `board`)* | `hat-standard/spec/hat-link.yaml` |
| Board-revision implementation of each interface (SoC ball, pinmux, GPIO line, MCU pin) | `board` | `board/hardware/<rev>/interfaces/*.yaml` |
| Board ↔ supervisor MCU signals | `board` | same mapping file |

Content: per-pin table as in §1.3, mechanical datums and tolerances, ID/discovery fields, and a `version:` field following R5. A **JSON Schema** for these files lives in `toolkit` (it is a host tool concern), and every owner repo validates against a pinned schema version.

### R2. Generate, don't copy

Generators (recommended home: `toolkit/crates/`, as host tools, per the toolkit README "build, flash, emulation, publish, templates") produce, from R1 files:

| Output | Consumer | Committed? |
|---|---|---|
| KiCad connector symbols (via KiPart-style CSV or direct S-expression) + footprint parameters | `board`, faceplates, `hat-standard/reference-designs`, `hat-*` | Yes, vendored per consumer, with a header naming source file + version |
| WireViz YAML → SVG of each flat cable (pin 1 orientation, contact side) | spec docs, `case` | Yes (SVG in docs) |
| FreeCAD parameter spreadsheet (CSV/JSON importable into a Spreadsheet object that sketches reference by alias) | `case`, `case/hat-case`, faceplate and HAT cases | Yes |
| DT fragments: connector nexus node (`gpio-map`), `gpio-line-names`, pinctrl groups per board rev, overlay skeletons per HAT/faceplate | `blackbird-os` (board DTS + `overlays/`) | Yes |
| Rust crate with pin/bus constants and interface version | `board/firmware`, faceplate firmware, HAT firmware, `system` (names only) | Yes, or built in `build.rs` from a pinned spec release |
| Markdown pin tables | spec `.md` files | Yes (between generated markers) |

Rule: generated files carry a "generated — do not edit" header; CI regenerates and fails on any diff (drift check).

### R3. Check what the tools actually contain

CI jobs, each in the consuming repo, comparing *real* artifacts back to the R1 file:

| Repo | Check | Tools |
|---|---|---|
| `board`, faceplates, `hat-*`, `hat-standard/reference-designs` | ERC/DRC JSON clean; **connector-netlist conformance** (each connector pin's net matches the interface signal; reserved pins unconnected or as specified); requirement fields present on tagged parts | `kicad-cli` 10.0.x, kinparse or own parser; KiBot 1.9.x for outputs/diffs |
| `case`, faceplate cases, HAT cases | **Fit check**: import the pinned board STEP release, intersection volume = 0, connector/pogo datums within tolerance of R1 | `FreeCADCmd` 1.1.x or CadQuery/build123d |
| `blackbird-os` | Build board DTS out of tree, apply **every** overlay to **every** supported base with `fdtoverlay`, `dt-validate` (dt-schema pinned) against bindings from the pinned mainline tag; overlay pin usage ⊆ interface file | dtc, fdtoverlay, dtschema 2026.x |
| firmware repos | Generated pin crate up to date; build for every supported board rev | cargo, probe-rs in HIL |
| all | REUSE compliance; requirement-ID lint (R4) | `reuse` 6.x, toolkit linter |

### R4. Traceability: start light, keep the door open

- Keep the existing Markdown requirement tables (they already work with the `/opendap:requirement` skill).
- Add a **prefix registry** (prefix → repo → document) and a toolkit **requirement linter** that: parses all tables across a workspace checkout, enforces uniqueness and the `PREFIX-NNN` shape, forbids reuse of withdrawn IDs, scans code/tests/DT comments/KiCad fields/FreeCAD properties for references (§2.2), and emits a static traceability matrix as a CI artifact.
- Conventions: KiCad symbol field `Req`; FreeCAD string property `Requirement`; code/test comment `Implements: ID` / `Verifies: ID`.
- Re-evaluate **StrictDoc** (most complete open option, ReqIF) or **sphinx-needs** (`needs_external_needs` for cross-repo) once verification evidence or external certification becomes a need. SysML v2 tooling (SysON) is not recommended yet (self-declared not production-ready).

### R5. Version interfaces, declare compatibility, pin with a manifest

- SemVer per interface spec as in §4.1; tags like `faceplate-interface-v0.3.0` in `case`, `v0.3.0` in `hat-standard`. A CI job classifies the diff of the interface file (pin moved = MAJOR, reserved→optional = MINOR, text = PATCH) and blocks under-bumped versions (Flipper-style).
- Hardware repos declare `provides`/`requires` per revision in a small `compat.yaml`; `blackbird-os` declares supported board revisions and shipped overlays; a toolkit command computes the compatibility matrix and marks tested tuples from HIL results.
- *(owner question)* How faceplates and HATs identify themselves (ID EEPROM à la HAT+, resistor strap, MCU-reported ID), since overlays must be chosen by the bootloader under BRD-001.
- **Pinning**: interface specs are consumed as **versioned release artifacts** (R2 outputs bundled); the whole product is pinned by a **platform manifest** that extends the workspace `repos.tsv` with a revision column (or adopts `west`); git submodules only where a GUI tool needs a library path and a manifest is impractical.
- **Release train**: time-based for `system`/`blackbird-os`, milestone-based for hardware, joined by platform releases that publish manifest + compatibility rows.

### R6. Cross-repo changes go through an RFC

- Numbered RFCs (KEP-like) for any MINOR/MAJOR interface change or any change touching ≥2 repos. *(owner question)* Where RFCs live: the `workspace` repository, the org `.github` repository, or a new `rfcs` repository.
- Each RFC lists affected repos and links the PRs; an **integration CI** job checks out the manifest with the RFC's branches overridden and runs R3 checks plus the emulator smoke test (R7).
- CODEOWNERS on interface files require reviewers from electronics, mechanics and OS.

### R7. Early integration, staged by what exists

1. **Now (no SoC chosen):** schema validation, generators + drift checks, KiCad ERC/DRC, DT compile + overlay apply + `dt-validate` against a placeholder/EVK base DTS, requirement lint.
2. **After SoC selection:** QEMU (and/or Renode) boot of the Blackbird OS image in CI with the generated DTB; Renode co-simulation of SoC + supervisor MCU firmware over the generated bus map (`dts2repl` from the same DT); Robot/pytest tests that later run unchanged on the bench.
3. **With first boards:** labgrid bench per hardware combination; bring-up checklists generated from the interface files; results feed the compatibility matrix and requirement verification.

### R8. Reviews

- Gate sequence of §6.1; checklists in each repo's `docs/checklists/`, linked from PR templates.
- Visual artifacts on every hardware PR: KiBot schematic/PCB diff PDFs/SVGs, iBoM, 3D renders; FreeCAD `fcinfo` textconv diff + headless before/after renders; spec PRs show the regenerated WireViz SVG and pin tables.
- Prefer open tools (KiBot, KiRI, kicad-cli, FreeCAD headless) over hosted proprietary review platforms.

### Summary map (recommended)

| Repo | Owns (source of truth) | Receives (generated / pinned) | CI checks |
|---|---|---|---|
| `toolkit` | Interface JSON Schemas, generators, requirement linter, compatibility-matrix tool, HAT/faceplate project templates | — | Unit tests of generators on fixture interfaces |
| `case` | Faceplate interface file + spec; core/back-cover/HAT-case envelope | Board STEP (pinned release), generated parameter spreadsheet | Fit check, drift check, req lint |
| `hat-standard` | HAT interface + link files, spec, compliance tests, reference designs | Generated KiCad libs for reference designs | Version-bump classifier, netlist conformance of reference designs |
| `board` | Board KiCad, per-rev interface implementation mapping, MCU firmware | Connector libs, pin crate | ERC/DRC, netlist conformance, STEP export, firmware build per rev |
| `faceplate-*` | Faceplate hardware/case/firmware | Faceplate connector lib, parameter spreadsheet, pin crate | Same as board + fit check |
| `hat-*` | HAT hardware/case/firmware/software | HAT connector lib + design block, parameter spreadsheet, pin crate, overlay skeleton | Netlist conformance, fit check, overlay applies on all supported bases |
| `blackbird-os` | Board DTS, overlays, image | Generated DT fragments (pinned spec versions) | DT build, overlay apply matrix, `dt-validate`, emulator boot (post-SoC) |
| `system` | Services, bus, SDK | Line names / interface constants | Tests against emulator (post-SoC) |
| workspace / `.github` / `rfcs` *(owner question)* | Platform manifest, RFCs, compatibility rows | — | Integration CI over the manifest |

---

## Sources (selected, all accessed 2026-10-21)

- KiCad 10.0.0 release notes: <https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/> · 10.0.6: <https://www.kicad.org/blog/2026/08/KiCad-10.0.6-Release/> · CLI: <https://docs.kicad.org/9.0/en/cli/cli.html>
- FreeCAD releases: <https://github.com/FreeCAD/FreeCAD/releases> · KiCad StepUp: <https://wiki.freecad.org/KicadStepUp_Workbench> · fcinfo/Arch Git: <https://wiki.freecad.org/Arch_Git> · GitCAD: <https://github.com/MikeOpsGit/GitCAD>
- SKiDL: <https://github.com/devbisme/skidl> · atopile: <https://github.com/atopile/atopile>, <https://docs.atopile.io/> · KiPart: <https://pypi.org/project/kipart/> · kicad-pinout-generator: <https://github.com/CGrassin/kicad-pinout-generator> · WireViz: <https://github.com/wireviz/WireViz> · kicad-python: <https://pypi.org/project/kicad-python/>
- KiBot: <https://github.com/INTI-CMNB/KiBot> · KiRI: <https://github.com/leoheck/kiri> · KiKit: <https://github.com/yaqwsx/KiKit> · InteractiveHtmlBom: <https://github.com/openscopeproject/InteractiveHtmlBom>
- StrictDoc: <https://github.com/strictdoc-project/strictdoc> · sphinx-needs: <https://github.com/useblocks/sphinx-needs> · OpenFastTrace: <https://github.com/itsallcode/openfasttrace> · Doorstop: <https://github.com/doorstop-dev/doorstop> · Capella: <https://github.com/eclipse-capella/capella> · SysON: <https://github.com/eclipse-syson/syson>, <https://mbse-syson.org/> · OMG SysML v2: <https://www.omg.org/news/releases/pr2025/07-21-25.htm>
- QEMU imx8mp-evk: <https://www.qemu.org/docs/master/system/arm/imx8mp-evk.html> · Renode: <https://github.com/renode/renode> · Renode i.MX 8M Plus: <https://antmicro.com/blog/2026/06/renode-support-for-nxp-imx8m-plus> · dts2repl: <https://github.com/antmicro/dts2repl> · labgrid: <https://pypi.org/project/labgrid/> · LAVA: <https://gitlab.com/lava/lava> · probe-rs: <https://github.com/probe-rs/probe-rs>
- dt-schema: <https://pypi.org/project/dtschema/> · Makefile.dtbs: <https://gbmc.googlesource.com/linux/+/refs/heads/master/scripts/Makefile.dtbs> · export-symbols: <https://lkml.iu.edu/hypermail/linux/kernel/2412.1/01636.html> · addon DT RFC: <https://lkml.iu.edu/2601.1/04737.html> · U-Boot extension boards: <https://bootlin.com/pub/conferences/2021/lee/maincent-devicetree-overlay-and-uboot-extension-board-management/maincent-devicetree-overlay-and-uboot-extension-board-management.pdf> · gpio-line-names: <https://lkml.iu.edu/hypermail/linux/kernel/2302.1/04065.html> · kernel releases: <https://www.kernel.org/releases.json>
- Zephyr shields / nexus nodes: <https://docs.zephyrproject.org/latest/hardware/porting/shields.html> · west: <https://pypi.org/project/west/>
- Raspberry Pi HAT+: <https://pip.raspberrypi.com/documents/RP-008281-DS-hat-plus-specification.pdf> · BeagleBoard cape spec: <https://docs.beagleboard.org/boards/capes/cape-interface-spec.html> · MNT: <https://source.mnt.re/reform>, <https://source.mnt.re/reform/reform/-/raw/main/.gitlab-ci.yml> · Framework: <https://github.com/FrameworkComputer/ExpansionCards>, <https://github.com/FrameworkComputer/Mainboard> · PinePhone add-ons: <https://wiki.pine64.org/wiki/PinePhone_(Pro)_Add-ons> · Precursor + Renode: <https://antmicro.com/blog/2022/03/precursor-developing-advanced-products-with-renode/>, <https://github.com/betrusted-io/xous-core> · Librem 5: <https://source.puri.sm/Librem5/dvk-mx8m-bsb>, <https://puri.sm/posts/purism-releases-step-file-for-librem-5/> · Arduino UNO Q: <https://docs.arduino.cc/hardware/uno-q/> · Flipper Zero: <https://developer.flipper.net/flipperzero/doxygen/apps_on_sd_card.html>, <https://github.com/flipperdevices/flipperzero-firmware>
