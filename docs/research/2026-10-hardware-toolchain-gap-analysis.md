# Hardware toolchain gap analysis (October 2026)

- **Date:** 2026-10-21
- **Status:** Research. Everything here is a **recommendation, not a decision**. Nothing in this document is a confirmed OpenDAP requirement or ADR.
- **Scope:** Software (and a few low-cost instruments) needed around the tools already chosen: KiCad 10 (electronics), FreeCAD 1.1 (mechanics), Blender 5.2 (renders), Python + openEMS (simulation), Rust (software and firmware).
- **Product context used:** the device description given in the research brief (credit-card handheld Linux device; stacked boards with SoC + LPDDR, audio DAC and headphone amps, battery and charger; swappable front faceplate with touch display over FPC; rear HAT interface over a flat cable plus small two-row pogo pins, possibly carrying PCIe, USB3 and MIPI CSI; HATs such as NAS, camera, multitrack recorder, oscilloscope, NanoVNA-based VNA, HackRF-based SDR, powerbank; a Commercial edition aiming at about IP65 and a DIY kit). These are working assumptions from the brief, not confirmed specifications.

## How to read this

- Versions were checked on 2026-10-21 against GitHub releases or tags, PyPI, container registries or the project's own site. Each claim carries a source link.
- **UNVERIFIED** marks a fact that could not be confirmed in this session (for example a page was blocked or no release data exists).
- "OSS" means open-source software. Commercial tools are named only as a **fallback** where no usable OSS exists, and are always labelled as such.
- Maturity scale: **Production** (used widely for real products), **Usable** (works, rough edges, small team), **Research** (academic or early, expect to fix things yourself), **Stale** (no meaningful activity for 2+ years).

## Key findings first

1. **The OSS stack covers about 80% of the work.** It covers schematic, layout, fab outputs, CI, BOM, panelization, static FEA, thermal, DC power integrity, 2D and 3D EM, S-parameter work, bring-up and production test frameworks. The real gaps are **injection-mould flow simulation**, **sign-off-grade multi-GHz SI/PI** (an LPDDR4/5 + PCIe + USB3 + MIPI channel crossing FPC and pogo pins), **rigid-flex in KiCad**, **GD&T and tolerance analysis tied to the CAD model**, and **PLM**.
2. **OpenRadioss was taken down by Siemens on 1 October 2026.** The repository was deleted, not archived. The community fork **OpenCourant** (AGPL-3.0) is now the OSS route for drop and impact simulation. Treat it as young. ([Phoronix](https://phoronix.com/news/Siemens-Ends-OpenRadioss), [OpenCourant fork](https://phoronix.com/news/openradioss-opencourant), [github.com/OpenCourant/OpenCourant](https://github.com/OpenCourant/OpenCourant))
3. **KiCad has no per-region stackup yet**, so it has no native rigid-flex. You can design flex-only FPCs (faceplate and HAT cables) as separate KiCad boards with their own stackup today. A rigid-flex main board would need the "superset stackup + mechanical drawing" workaround, or a commercial tool. ([KiCad forum](https://forum.kicad.info/t/when-will-the-flex-pcb-be-supported-in-kicad/32597))
4. **The CI/release pipeline is solved with OSS.** KiCad 10's `kicad-cli` exports Gerber, drill, position, IPC-2581, ODB++, STEP, 3D PDF and more, and runs DRC with schematic parity and ERC with failing exit codes. KiBot 1.9.1 has KiCad 10 images and a GitHub Action tag `v2_k10`. ([kicad-cli docs](https://docs.kicad.org/10.0/en/cli/cli.html), [KiBot tags](https://github.com/INTI-CMNB/KiBot/tags))
5. **The lab gap is instruments, not software.** NanoVNA and LibreVNA-class instruments cannot characterise USB3 or PCIe Gen3+ channels, which need roughly 10–20 GHz. Plan to rent or borrow a ≥20 GHz VNA or TDR for the FPC and pogo characterisation, or pay a lab.

---

## 1. Mechanical

### 1.1 Part and assembly design

| Need | Recommended | Version | License | Maturity | Integration |
|---|---|---|---|---|---|
| Parametric part design | FreeCAD Part Design (already chosen) | **1.1.4** (2026-09-28) ([release](https://github.com/FreeCAD/FreeCAD/releases)) | LGPL-2.1 | Production for small products | Native |
| Assemblies | FreeCAD **Assembly** workbench (built in, Ondsel solver) | ships with 1.1 | LGPL-2.1 | Usable | Native; BOM export |
| Code-defined parts (connectors, gaskets, fixtures, parametric HAT shells) | **build123d** or **CadQuery** | build123d **0.13.0**, CadQuery **2.8.0** (PyPI) | Apache-2.0 | Usable | STEP in and out to FreeCAD; scriptable in CI |
| Fasteners and standard parts | FreeCAD *Fasteners* addon, FreeCAD-library | rolling | LGPL / mixed | Usable | Addon Manager |

**FreeCAD 1.1 Assembly status.** The 1.1 release (24 March 2026) added a simpler part-insertion tool, **motion simulation and animation of joints**, extended **BOM generation with property extraction**, and new core datum tools that work inside assemblies ([FreeCAD 1.1 overview, Fabbaloo](https://www.fabbaloo.com/?p=236104), [alternativeto](https://alternativeto.net/news/2026/3/freecad-1-1-adds-three-point-lighting-part-design-previews-and-major-fem-upgrades)). It has exploded views, and its solver handles fixed, revolute, cylindrical, slider, ball, gear, belt, screw and rack-and-pinion joints ([Assembly wiki](https://wiki.freecad.org/Assembly_Workbench/tr), [Ondsel blog](https://ondsel.com/blog/default-assembly-workbench-7)). The company that wrote the solver, Ondsel, closed in 2024; the workbench is now maintained upstream ([Ondsel goodbye](https://ondsel.com/blog/goodbye/)). Its behaviour with very large assemblies and flexible sub-assemblies in 1.1 is **UNVERIFIED** (the official 1.1 release notes page was blocked by bot protection during this research).

**Gap:** no OSS has a mature *top-down* skeleton or master-model workflow comparable to commercial MCAD. Fallback (commercial): Onshape, SolidWorks, Fusion. Recommendation: stay in FreeCAD. Keep one "skeleton" body (board outlines, connector datums, display envelope) that every part references.

### 1.2 Tolerance stack-up

| Recommended | Version | License | Maturity | Notes |
|---|---|---|---|---|
| Spreadsheet or Python worst-case + RSS + Monte Carlo (numpy/scipy) | — | — | Production (as a method) | Keep the stacks as code in the mechanical repo, reviewed like code |
| **stackcore** | 0.3.3 (2025-07, [PyPI](https://pypi.org/project/stackcore/)) | MIT | Research | 1D Monte Carlo stacks |
| **Tol-Ninja** | rolling ([GitHub](https://github.com/slehmann1/Tol-Ninja)) | **UNVERIFIED** | Research | 1D and coaxial chains, report PDF |

**Gap:** no OSS 3D tolerance analysis that reads GD&T from the CAD model. Fallback (commercial): Sigmetrix CETOL 6σ, 3DCS. For a handheld with a few critical chains (display glass to bezel, button travel, gasket compression, pogo-pin preload, HAT alignment), hand-written 1D stacks in Python are enough.

### 1.3 Structural FEA (snap-fits, screw bosses, latches, housings)

| Recommended | Version | License | Maturity | Integration |
|---|---|---|---|---|
| **FreeCAD FEM + CalculiX** | CalculiX **2.23** (2025-10-19) ([dhondt.de](https://dhondt.de/), [PrePoMax forum](https://prepomax.discourse.group/t/calculix-2-23-has-been-released/3048)) | GPL-2.0 | Production | FreeCAD 1.1 added tie constraints on shells, hard and tied contact, amplitudes and more ([FEM in 1.1](https://blog.freecad.org/2025/09/09/what-is-new-in-fem-for-freecad-1-1/)) |
| **Elmer FEM** | **release-26.2** (2026-04-28) ([GitHub](https://github.com/ElmerCSC/elmerfem/releases)) | GPL-2.0 / LGPL | Production | FreeCAD FEM solver; also multiphysics |
| **gmsh** (meshing) | **4.15.2** ([PyPI](https://pypi.org/project/gmsh/)) | GPL-2.0+ | Production | FreeCAD FEM mesher; Python API; KiCad 10 can export `.xao` for Gmsh/SALOME ([kicad-cli](https://docs.kicad.org/10.0/en/cli/cli.html)) |
| PrePoMax (CalculiX GUI) | **UNVERIFIED** | GPL-3.0 | Usable | Windows-only, an alternative pre- and post-processor |

Snap-fits and bosses need **nonlinear contact and plasticity**, which CalculiX handles. Calibrate against physical prototypes (3D-printed and then moulded), because material data for real PC/ABS grades is the weak link, not the solver.

### 1.4 Drop and impact

| Recommended | Version | License | Maturity |
|---|---|---|---|
| **OpenCourant** (community fork of OpenRadioss) | rolling tag `latest-20261011` ([GitHub](https://github.com/OpenCourant/OpenCourant)) | AGPL-3.0 | Usable solver, **fork is weeks old** |
| CalculiX explicit dynamics | 2.23 | GPL-2.0 | Usable for simple impacts |

OpenRadioss had a ready-made **cell-phone drop test** example: a 1.5 m drop onto a rigid wall with about 130 k elements ([OpenRadioss wiki](https://openradioss.atlassian.net/wiki/spaces/OPENRADIOSS/pages/11141156)), which is a close template for OpenDAP. Siemens removed the repository on 2026-10-01 ([Phoronix](https://phoronix.com/news/Siemens-Ends-OpenRadioss)). Whether the wiki stays online is **UNVERIFIED**.

**Gap:** pre-processing for explicit solvers (material cards, contact definitions) has no good OSS GUI. Fallback (commercial): LS-DYNA, Abaqus/Explicit, Ansys. Recommendation: use simulation only to rank design variants, and rely on **physical drop tests** (IEC 60068-2-31 style) for the Commercial edition.

### 1.5 Thermal (enclosure and battery)

| Need | Recommended | Version | License | Integration |
|---|---|---|---|---|
| Conduction and radiation in the enclosure | FreeCAD FEM + CalculiX or Elmer heat | see above | GPL | FreeCAD 1.1 added CalculiX gap conduction, cavity radiation and thermal contact ([FEM 1.1](https://blog.freecad.org/2025/09/09/what-is-new-in-fem-for-freecad-1-1/)) |
| Joule heating in copper or the battery path | Elmer **StaticCurrent + Heat** (new in FreeCAD 1.1) | Elmer 26.2 | GPL | Same source |
| Battery electro-thermal model (cell heat generation versus load and charge profile) | **PyBaMM** | **26.10.1.1** ([PyPI](https://pypi.org/project/pybamm/)) | BSD-3-Clause | Python; feed heat sources into Elmer |
| Natural convection | see CFD below | | | |

### 1.6 CFD (only if natural convection matters)

| Recommended | Version | License | Maturity |
|---|---|---|---|
| **OpenFOAM** (ESI/Keysight line) | **v2606** (June 2026) ([openfoam.com](https://www.openfoam.com/news/main-news/openfoam-v2606)) | GPL-3.0 | Production |
| **CfdOF** FreeCAD workbench | **v1.37.3** ([tags](https://github.com/jaheyns/CfdOF/tags)) | LGPL-3.0 | Usable |

A sealed IP65 handheld at a few watts is mostly a conduction and radiation problem. Recommendation: do CFD only if FEM plus a convection coefficient gives skin temperatures close to the limit. Fallback (commercial): Simcenter Flotherm, Ansys Icepak.

### 1.7 IP65 sealing and gasket design

- **Design:** FreeCAD (gasket groove geometry). Use the vendor's design guides for O-ring and FIP/CIPG gasket compression (typically 15–30% squeeze for elastomers; confirm per vendor).
- **Analysis:** CalculiX hyperelastic materials (Mooney-Rivlin / Neo-Hooke) for gasket compression and closure force. Elmer is an alternative.
- **Acoustic vents and membranes:** use vendor data sheets (ePTFE vents). OSS cannot simulate membrane water-entry pressure.
- **Gap:** no OSS checks ingress protection. IP65 (IEC 60529) is validated **only by test** (dust chamber + 6.3 mm water jet). Budget for a test lab. Fallback (commercial): Abaqus or Ansys for hyperelastic contact if CalculiX convergence is painful.

### 1.8 Plastics and injection moulding

| Need | OSS status | Fallback |
|---|---|---|
| Draft analysis | **Gap.** No built-in draft or undercut colour map in FreeCAD 1.1 core (**UNVERIFIED**; check the Addon Manager). Workaround: a FreeCAD Python macro that colours faces by angle to the pull direction. | Commercial MCAD (SolidWorks, Fusion, Onshape all have one) |
| Wall-thickness check | Gap in core; scriptable with OCCT ray casting through FreeCAD Python | Same |
| Mould flow (fill, weld lines, sink, warp) | **Gap.** Only research code: **openInjMoldSim** (OpenFOAM-based, filling stage) ([U. Minho](https://repositorium.sdum.uminho.pt/handle/1822/70469), [MDPI paper](https://www.mdpi.com/2311-5521/5/2/84)) | Commercial: Autodesk Moldflow, Moldex3D, SolidWorks Plastics. **In practice the moulder runs mould flow as part of DFM.** Ask PCBWay or the injection-moulding vendor for their DFM report. |

Recommendation: do not invest in OSS mould flow. Design to standard rules (uniform walls, ≥0.5–1° draft, rib at 50–60% of wall thickness). Require the toolmaker's DFM and mould-flow report as a deliverable of the tooling quote.

### 1.9 Sheet metal

**FreeCAD SheetMetal addon**: active (last push 2026-10-17), LGPL-2.1 ([GitHub](https://github.com/shaise/FreeCAD_SheetMetal)), with unfold to DXF. Version scheme unclear from the tags (**UNVERIFIED**); install it from the Addon Manager. Usable for shields, battery brackets and HAT frames.

### 1.10 CNC CAM

**FreeCAD CAM workbench** (formerly Path; 1.1 adds a new **tool library system** ([osarch](https://osarch.org/2026/03/25/freecad-1-1-released/))). Usable for 2.5D and 3D milling of prototypes and fixtures. **Gap:** 4/5-axis simultaneous and verified post-processors for specific machines. Fallback (commercial): Fusion CAM. For quotes from CNC shops (PCBWay CNC included), send **STEP + a PDF drawing**, not G-code.

### 1.11 3D-printing slicers (DIY kit)

| Slicer | Version | License |
|---|---|---|
| **OrcaSlicer** | **v2.4.2** (2026-07-07) ([GitHub](https://github.com/OrcaSlicer/OrcaSlicer/releases)) | AGPL-3.0 |
| **PrusaSlicer** | **2.9.6** (2026-06-25) ([GitHub](https://github.com/prusa3d/PrusaSlicer/releases)) | AGPL-3.0 |
| **UltiMaker Cura** | **5.13.0** (2026-05-28) ([GitHub](https://github.com/Ultimaker/Cura/releases)) | LGPL-3.0 |

Recommendation for the DIY kit: publish **STEP + 3MF with print settings** (3MF can carry slicer profiles), tested in OrcaSlicer and PrusaSlicer. Generate STL and 3MF in CI with headless FreeCAD (see §7).

### 1.12 ECAD ↔ MCAD exchange

| Path | Tool | Status |
|---|---|---|
| KiCad → FreeCAD (board + components) | **KiCad StepUp** workbench | Active (last push 2026-09-04) ([GitHub](https://github.com/easyw/kicadStepUpMod)); version **UNVERIFIED**; two-way board outline and keepout sync, plus footprint 3D model alignment |
| KiCad → any MCAD | `kicad-cli pcb export step` / `stpz` / `brep` / `xao` / `glb` | KiCad 10 ([kicad-cli](https://docs.kicad.org/10.0/en/cli/cli.html)) |
| KiCad → reviewers | `kicad-cli pcb export 3dpdf` (new in 10) | ([KiCad 10 announcement](https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/)) |
| KiCad → Blender | `kicad-cli pcb export glb`, or STEP → FreeCAD → glTF | Usable |
| IDX/IDF incremental collaboration | **Gap.** KiCad has no IDX (ProSTEP ECAD-MCAD collaboration). StepUp's outline push/pull is the OSS substitute. | |

Recommendation: the board outline, mounting holes, connector positions and keep-outs are owned in **one place** (the FreeCAD skeleton) and pushed to KiCad via StepUp. Each board release exports a STEP that the mechanical assembly re-imports.

### 1.13 Drawings and GD&T

**FreeCAD TechDraw**: usable for fabrication drawings. GD&T is limited: feature control frames are built from formatted labels, and datums from rectangular balloons with a triangle end symbol ([TechDraw GD&T wiki](https://wiki.freecad.org/TechDraw_Geometric_dimensioning_and_tolerancing)). A community GD&T workbench exists for 3D annotations ([FreeCAD-GDT](https://github.com/juanvanyo/FreeCAD-GDT)); maturity **UNVERIFIED**. **Gap:** semantic PMI/MBD (STEP AP242 with GD&T) has no OSS authoring path. Fallback (commercial): SolidWorks MBD, Creo. For injection-moulded parts, a TechDraw PDF with critical dimensions, plus STEP, is what moulders quote from.

---

## 2. Electronics

### 2.1 SPICE (analog, power, audio)

| Recommended | Version | License | Integration |
|---|---|---|---|
| **ngspice** (inside KiCad) | **47** (2026-08-11): adds Python matplotlib plotting, **WAV read/write**, small-signal noise for code models ([ngspice news](https://ngspice.sourceforge.io/news.html)) | BSD-3 / mixed | KiCad simulator; KiCad 10 bundles a recent ngspice (exact bundled version **UNVERIFIED**) |
| **Qucs-S** | **26.1.1** (2026-04-26) ([GitHub](https://github.com/ra3xdh/qucs_s/releases)) | GPL-2.0 | Front end for ngspice / Xyce / Qucsator; RF tools, filter synthesis, S-parameter simulation |
| Xyce (parallel SPICE, Sandia) | **UNVERIFIED** | GPL-3.0 | Qucs-S back end for large transient runs |
| SKiDL (netlists in Python, for test benches) | **3.0.0** (2026-10-16) ([GitHub](https://github.com/devbisme/skidl)) | MIT | Generates KiCad netlists |

The ngspice 47 WAV support lets you push a real audio file through the DAC and headphone amplifier model, then analyse THD+N with the same Python scripts used on bench captures.

### 2.2 Power integrity / PDN

| Need | Recommended | Version | License | Maturity |
|---|---|---|---|---|
| DC IR drop and current density on copper | **padne** (KiCad-native 2.5D FEM; reads KiCad projects; directives live in the schematic; ParaView export) | **v0.3** (2026-05-29) ([GitHub](https://github.com/atx/padne)) | GPL-3.0 | Usable (young) |
| DC + Joule heating in 3D | Elmer StaticCurrent + Heat via FreeCAD 1.1 | 26.2 | GPL | Usable |
| AC PDN impedance (target impedance, decoupling selection) | Python + scikit-rf, with **vendor S-parameter capacitor models** (Murata SimSurfing / KEMET K-SIM exports) and plane models from openEMS | scikit-rf 2.2.0 | BSD-3 | Usable (DIY) |
| Regulator loop and transient | ngspice with vendor PMIC models (where they exist as SPICE) | 47 | | Usable |

**Gap:** no OSS AC plane-resonance and cavity solver integrated with KiCad (the job of Sigrity PowerSI, HyperLynx PI, Ansys SIwave, Cadence Clarity). Fallback (commercial): one of these, or a design-review service. Recommendation for LPDDR4/5: follow the **SoC vendor's reference layout and PDN guidelines exactly**. They usually give target-impedance curves and decap counts. Use padne for DC, and openEMS/Palace for one or two plane-pair checks.

### 2.3 Signal integrity: LPDDR4/5, PCIe, USB3, MIPI

| Need | Recommended | Version | License | Integration |
|---|---|---|---|---|
| Impedance and stackup (2D cross-section) | **KiCad calculator** (microstrip, stripline, coplanar) for first-pass sizing; fab calculators (PCBWay, JLCPCB) for the final word | KiCad 10 | GPL | Built in |
| 2D field solve (Z0, coupling, RLGC) | **openEMS** 2D-ish ports, **Elmer** electrostatics, **FastHenry2** (R/L, skin effect), **FasterCap** (C) | openEMS-Project **v0.37.0** (2026-10-09) ([GitHub](https://github.com/thliebig/openEMS-Project/releases)); FastHenry2 **R3.6** ([GitHub](https://github.com/ediloren/FastHenry2)); FasterCap repo stale since 2019 ([GitHub](https://github.com/ediloren/FasterCap)) | GPL / LGPL | Python scripting |
| | **TNT-MMTL** (multilayer transmission line 2D/2.5D) | stale since 2015 ([GitHub](https://github.com/corecode/mmtl-tnt)); a WebAssembly port exists ([TNT-MMTL-Web](https://github.com/ferret-guy/TNT-MMTL-Web)) | GPL-2.0 | Stale but still valid physics |
| | **atlc** (arbitrary transmission line calculator) | Stale; last release **UNVERIFIED** | GPL | Legacy |
| 3D full-wave from the real layout | **gerber2ems** (Antmicro): Gerber + drill + stackup → openEMS → S-parameters, impedance; adaptive grid added in 2025 | tag **v0.99.0**, active 2026-10 ([GitHub](https://github.com/antmicro/gerber2ems), [Antmicro blog 2025](https://antmicro.com/blog/2025/07/recent-improvements-to-antmicros-signal-integrity-simulation-flow)) | Apache-2.0 | Consumes KiCad fab outputs; fits CI |
| 3D frequency-domain FEM (large or fine geometry, connectors, pogo pins) | **Palace** (AWS; driven, eigenmode and electrostatic; laptop to cluster) | **v0.18.1** (2026-09-21) ([GitHub](https://github.com/awslabs/palace/releases)) | Apache-2.0 | Meshes from gmsh; KiCad 10 `export xao`/STEP → gmsh |
| S-parameter manipulation, de-embedding, TDR, time gating, IEEE P370 | **scikit-rf** | **2.2.0** (2026-10-18) ([GitHub](https://github.com/scikit-rf/scikit-rf/releases)) | BSD-3 | Python; reads and writes Touchstone |
| Channel simulation, eye diagrams, de-embedding, TDR, virtual probing (GUI + library) | **SignalIntegrity** (now maintained by Nubis Communications, originally Teledyne LeCroy) | **1.5.2** (2026-07-29) ([GitHub](https://github.com/Nubis-Communications/SignalIntegrity)) | GPL (per PyPI) | Python; Touchstone |
| SerDes / IBIS-AMI eye and BER (PCIe, USB3) | **PyBERT** + **PyIBIS-AMI** | PyBERT **v11.1.0** (2026-10-20) ([GitHub](https://github.com/capn-freako/PyBERT/releases)); PyIBIS-AMI **10.0.0** ([PyPI](https://pypi.org/project/pyibis-ami/)) | BSD-style / **UNVERIFIED** | Loads IBIS-AMI and Touchstone channels |
| IBIS buffer simulation (LPDDR, MIPI, GPIO) | **KiCad simulator with KIBIS** (IBIS driver and receiver models in ngspice; since KiCad 8) | KiCad 10 | GPL | Built in ([KiCad forum](https://forum.kicad.info/t/using-ibis-model-in-kicad/51299)) |
| Length and **time-domain** matching | **KiCad 10 tuning**: time-domain constraints and per-layer *tuning profiles* | 10.0 | GPL | Built in ([KiCad 10 release](https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/)) |

**How it fits together:** stackup in KiCad → first-pass widths from the calculator and fab calculator → net-class rules and KiCad 10 time-domain tuning → Gerber export → **gerber2ems/openEMS** on critical nets (LPDDR byte lanes, PCIe/USB3 pairs, the HAT and faceplate breakouts) → Touchstone → **scikit-rf / SignalIntegrity** for IL/RL/crosstalk against the budget → **PyBERT** for PCIe/USB3 eye with IBIS-AMI models where the SoC vendor provides them.

#### Gaps

- **LPDDR4/5 sign-off** (DQ/DQS timing with vendor IBIS, SSO/SSN, write levelling margins) has no complete OSS flow. Fallback (commercial): Cadence Sigrity SystemSI, Siemens HyperLynx DDRx, Keysight ADS Memory Designer. Practical alternative: copy the SoC or SoM vendor's validated LPDDR layout, or use a SoM for the first revision.
- **IBIS-AMI models** for the SoC's PCIe/USB3 PHYs are often under NDA. PyBERT can run them only if you get them.
- **Compliance-grade COM / PCIe CEM checking**: no OSS equivalent of the official compliance tools (**UNVERIFIED** whether any OSS COM implementation is maintained).

### 2.4 EMC / EMI pre-compliance

| Need | Recommended | Notes |
|---|---|---|
| Design-rule review | KiCad DRC custom rules (`.kicad_dru`) for return-path, via-stitching and clearance checks; checklists | KiCad 10 has a graphical DRC rule editor ([KiCad 10](https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/)) |
| Near-field scanning | **tinySA Ultra** + near-field probes, or **HackRF** (also a planned OpenDAP HAT), driven by OSS software; an AR field-visualisation project exists ([rtl-sdr.com](https://www.rtl-sdr.com/visualizing-rf-fields-in-augmented-reality-with-a-tinysa-ultra-or-rtl-sdr-and-android-smartphone/)) | tinySA firmware ([GitHub](https://github.com/erikkaashoek/tinySA)); HackRF **v2026.01.3** ([GitHub](https://github.com/greatscottgadgets/hackrf/releases)) |
| Conducted emissions | LISN (DIY or low-cost) + tinySA / spectrum analyser | Pre-compliance only |
| Cable and enclosure resonances | openEMS / Palace models of the FPC and shield cans | |

**Gap:** a calibrated EMC receiver (CISPR detectors, a defined RBW) and an anechoic or OATS chamber. Fallback (commercial): Rigol, Siglent or Keysight spectrum analysers with EMI options for pre-compliance, plus an accredited lab for CE/FCC. A spectrum analyser with an EMI option is a better buy than more software.

### 2.5 Thermal of PCBs

- **Elmer** heat (via FreeCAD FEM). Import the board as STEP from KiCad and model copper as equivalent anisotropic conductivity per layer. FreeCAD 1.1's Elmer **StaticCurrent + Heat** coupling can model Joule heating of traces and planes.
- **padne** for current-density hot spots before full thermal work.
- **Gap:** no OSS that reads the KiCad copper geometry and builds a detailed thermal model automatically. Fallback (commercial): Simcenter Flotherm, Ansys Icepak, Celsius. Recommendation: use spreadsheet theta-JA plus an Elmer smeared-copper model, then validate with a thermal camera on the prototype.

### 2.6 RF design (SDR and VNA HATs)

| Need | Recommended | Version | License |
|---|---|---|---|
| Filter synthesis (LC, microstrip, coupled-line) | **Qucs-S** filter and transmission-line synthesis tools | 26.1.1 | GPL-2.0 |
| Planar EM (antennas, filters, transitions, SMA launch) | **openEMS** (FDTD; Python) ([docs](https://docs.openems.de/python/install.html)) | v0.37.0 | GPL-3.0 |
| Resonant structures, high-Q filters, cavities | **Palace** | v0.18.1 | Apache-2.0 |
| Network analysis, calibration (SOLT, TRL), de-embedding, matching | **scikit-rf** | 2.2.0 | BSD-3 |
| Wire antennas (quick) | NEC2 / necpp, xnec2c | **UNVERIFIED** | GPL |
| Measurement | **NanoVNA-Saver** **v0.7.3** (2025-02) ([GitHub](https://github.com/NanoVNA-Saver/nanovna-saver)); **LibreVNA** **v1.6.5** (2026-03, GPL-3.0, up to about 6 GHz) ([GitHub](https://github.com/jankae/LibreVNA)) | | GPL |

**Gap:** OSS lacks a layout-driven RF momentum-style planar solver integrated into KiCad (like Keysight ADS Momentum or Sonnet). openEMS through gerber2ems or hand-scripted geometry covers it with more effort. Fallback (commercial): Sonnet (Lite is free but closed), ADS, CST.

### 2.7 Audio analog performance (simulation and measurement)

| Need | Recommended | Version | License | Notes |
|---|---|---|---|---|
| Noise and THD in simulation | ngspice `.noise`, `.four`, transient + FFT; ngspice 47 WAV I/O | 47 | BSD | Op-amp and DAC output-stage models from vendors |
| Real-time spectrum and scope | **Friture** | **v0.54** ([GitHub](https://github.com/tlecomte/friture)) | GPL-3.0 | Usable |
| Precision THD+N (coherent averaging) | **Phonalyser** | **UNVERIFIED** (announced 2026 on diyAudio) ([thread](https://www.diyaudio.com/community/threads/phonalyser-open-source-audio-analyzer-with-coherent-averaging-fll-win-linux-mac.442117/)) | AGPL-3.0 | Research/young; needs a low-distortion ADC such as the Cosmos ADCiso |
| Scripted measurements in CI or production | Python (numpy/scipy) + ALSA/JACK via `sounddevice` | — | — | Write AES17-style THD+N, dynamic range, crosstalk and frequency-response scripts once; reuse them on the bench and in the factory |

**Gap:** a reference-grade audio analyser with an AES17 filter set and calibrated −120 dB residuals. Fallback (commercial): Audio Precision APx, QuantAsylum QA40x (lower cost). REW is free but closed-source and acoustic-oriented. Recommendation: one QA40x-class analyser for the lab, plus the Python scripts as the source of truth.

---

## 3. Flat cables / FPC and pogo pins

These interconnects (faceplate display FPC; HAT flat cable + two-row pogo pins possibly carrying PCIe / USB3 / MIPI CSI) are the highest-risk electrical item in the brief.

### 3.1 Impedance-controlled flex stackup

| Step | Tool | Notes |
|---|---|---|
| Choose a buildable stackup | **The fab's published flex stackups.** JLCPCB FPC: 1/2/4 layers, 25 and 50 µm PI, adhesive and adhesiveless, stiffeners, impedance-compatible structures ([JLCPCB capabilities](https://jlcpcb.com/capabilities/pcb-capabilities), [summary](https://www.bestpcbs.com/blog/2026/09/polyimide-flexible-circuit-companies/)). PCBWay: rigid-flex up to 16 layers, impedance control ±10% (±8% limit) on FR-4, FPC and rigid-flex ([PCBWay rigid-flex](https://www.pcbway.com/rigidflex.html), [PCBWay technologies](https://www.pcbway.ru/blog/PCB_Manufacturing_Information/Meet_New_Special_PCB_Technologies_in_PCBWay_.html)) | Get the fab's exact Dk/Df for PI and coverlay, and the hatched-ground option |
| Design the flex in KiCad | A **separate KiCad board per FPC** with its own stackup (PI + coverlay) | Works today. A rigid-flex main board is not native ([KiCad forum](https://forum.kicad.info/t/when-will-the-flex-pcb-be-supported-in-kicad/32597)) |
| Compute Z0 / Zdiff | KiCad calculator (first pass) → openEMS or Elmer 2D cross-section (exact, with **hatched ground**, which closed-form calculators handle badly) → confirm with the fab's impedance engineer | Specify impedance coupons on the fab order |

### 3.2 3D EM of FPC + connector + pogo transition

| Recommended | Why |
|---|---|
| **openEMS** (FDTD) via **gerber2ems** for the board and flex copper | Fits the existing Python + openEMS choice; produces Touchstone |
| **Palace** (FEM, frequency domain) for the **connector and pogo-pin 3D region**, meshed in **gmsh** from STEP | Curved, small geometry (pins, barrels) suits a tetrahedral FEM mesh better than FDTD staircasing |
| **scikit-rf** to **cascade** (board launch → connector → FPC → pogo → HAT board) and to de-embed fixtures (IEEE P370 classes) | Keeps each piece in its own Touchstone so you can swap parts |
| **Vendor S-parameter models** for the FPC connector (Hirose, I-PEX, Molex and others publish them for high-speed FPC connectors; availability per part is **UNVERIFIED**) | Better than modelling stamped-metal contacts yourself |

### 3.3 Crosstalk and loss budgets

- Build the budget as a **Python notebook or script in the repo**. Inputs: SoC PHY spec limits (PCIe base spec / CEM, USB 3.x channel, MIPI D-PHY or C-PHY channel spec). Outputs: per-segment allocations (main board, connector, FPC, pogo, HAT board).
- Evaluate with scikit-rf (IL, RL, NEXT/FEXT, mixed-mode Sdd21 / Scd21) and SignalIntegrity or PyBERT (eye, BER). These are the same tools as in §2.3.
- **Gap:** the official compliance channel tools (for example PCI-SIG's, or COM for IEEE 802.3) are not OSS or are tied to MATLAB (**UNVERIFIED** for the current versions). Fallback: commercial SI tools or a lab service for sign-off.

### 3.4 TDR and eye analysis (open tools)

| Mode | Tools and status |
|---|---|
| Simulated | scikit-rf time-domain (impulse/step from S-params, time gating), SignalIntegrity (TDR, virtual probing), PyBERT (eye/bathtub) |
| Measured | **Gap.** OSS software can process measured Touchstone, but you need a **≥20 GHz VNA or a sampling-scope TDR** for USB3 (5–10 Gb/s) and PCIe Gen3/4 (8–16 GT/s). LibreVNA (about 6 GHz) and NanoVNA are fine for MIPI D-PHY at lower rates, RF HAT filters and continuity, **not** for USB3/PCIe characterisation. Fallback (commercial): rent a Keysight / R&S / Copper Mountain VNA, or use the fab's TDR coupon report. |
| Live bring-up | ngscopeclient (eye rendering, protocol decode with supported scopes); see §5 |

### 3.5 Flex bend radius and mechanical life

- **Rules:** IPC-2223. Rule of thumb: **static ≈ 10× thickness** (1–2 layers), **dynamic ≥100× (1 layer), ~150× (2 layers), up to 200× (multilayer)** ([JLCPCB bend radius blog](https://jlcpcb.com/blog/flexible-pcb-bend-radius), [IPC-2223 copy](https://cdn.hackaday.io/files/1644617036299424/IPC-2223-Design-Standard-for-Flex-and-Rigid-Flex-Circuits.pdf), [Epec](https://blog.epectec.com/challenges-in-dynamic-flexible-circuit-board-design)). Faceplate swaps are "flex-to-install" (few cycles), but the **swap count over product life** sets the class. That number is not confirmed by the maintainers.
- **Analysis:** CalculiX (FreeCAD FEM) shell or beam model for copper strain in the bend. Keep copper strain below roughly 0.2–0.3% for dynamic flex (rule of thumb, **UNVERIFIED** for the specific RA copper grade; ask the fab). Use rolled-annealed copper and staggered traces, and keep vias out of the bend.
- **Validation:** physical cycle test (MIT fold test or a simple servo rig, which can be made with the FreeCAD CAM and printed fixtures).
- **Gap:** no OSS cable-routing tool for flex in an assembly (like the SolidWorks Routing flex tool). Workaround: model the folded flex as a FreeCAD sheet-metal-like body using the SheetMetal addon unfold. Fallback (commercial): SolidWorks / NX flex routing.

### 3.6 How to model pogo pins

1. **Mechanical:** spring force and travel from the vendor data sheet → tolerance stack (§1.2) to guarantee mid-stroke at all tolerances; CalculiX for the housing deflection under N × pin force.
2. **DC:** contact resistance + barrel resistance from the data sheet; include it in the padne / power-budget model for powerbank HAT currents.
3. **RF:** model each pin as a **solid coaxial-like conductor** (plunger + barrel merged; ignore the spring, or model it as a lumped inductor in series). Embed it in the actual insulator Dk with the neighbouring ground pins (a **G-S-S-G** or **G-S-G** pattern). Solve in **Palace** or **openEMS**, export Touchstone and cascade with scikit-rf. Ask vendors (Mill-Max, Preci-Dip, CFE, and others) for measured S-parameters; their high-speed pogo marketing claims GHz performance, but whether they publish Touchstone files is **UNVERIFIED** ([Mill-Max spring pins](https://mill-max.com/new_products/detail/103)).
4. **Recommendation (design, not tooling):** small two-row pogo pins are realistic for power, I²C/SPI/UART, I²S and USB 2.0. **Route PCIe / USB3 / MIPI over the impedance-controlled flat cable**, not over pogo pins, unless EM simulation and a measured prototype show margin.

---

## 4. Manufacturing and production

### 4.1 BOM, parts and inventory

| Need | Recommended | Version | License | Integration |
|---|---|---|---|---|
| Parts database, stock, builds, suppliers, BOM per revision | **InvenTree** | **1.6.1** (2026-10-21) ([GitHub](https://github.com/inventree/InvenTree/releases)); Python client **0.24.1** ([PyPI](https://pypi.org/project/inventree/)) | MIT | REST API; KiCad plugins exist |
| Create a KiCad symbol/footprint + an InvenTree part from a supplier part number | **Ki-nTree** | **1.2.1** (2026-03-25) ([GitHub](https://github.com/sparkmicro/Ki-nTree)) | GPL-3.0 | KiCad + InvenTree |
| Cost and availability spreadsheet | **KiCost** | **1.1.21** (2026-07-08) ([GitHub](https://github.com/hildogjr/KiCost)) | MIT | KiBot output `kicost`; needs distributor API keys |
| Part data API | **Nexar/Octopart** (commercial service, free tier) | — | Proprietary | Evaluation app has a **1000-part lifetime limit**; new apps start at 0; paid plans reset monthly ([Nexar part limits](https://support.nexar.com/support/solutions/articles/101000476314-part-limits-and-how-they-work)) |
| Distributor APIs | DigiKey, Mouser, LCSC/JLC (via KiCost, kicad-jlcpcb-tools) | — | Proprietary services | Free keys with rate limits (limits **UNVERIFIED**) |
| Partinfo (Kitspace) | Stale, last push 2023-01 ([GitHub](https://github.com/kitspace/partinfo)) | | | **Not recommended** |

**Gap:** lifecycle and obsolescence (EOL/NRND) alerts. OSS can only poll distributor APIs. Fallback (commercial): SiliconExpert, Octopart BOM tool, Z2Data.

### 4.2 Panelization

**KiKit** **v1.8.1** (2026-08-05), MIT ([GitHub](https://github.com/yaqwsx/KiKit/releases)). Production-grade: panels, tabs, mouse bites, V-cuts, frames and fiducials, plus `kikit fab jlcpcb|pcbway` output presets and stencil generation. Integrated in KiBot (`panelize` output).

### 4.3 Fab outputs automation

See §7 for the full pipeline. Core: `kicad-cli` (KiCad 10) + **KiBot 1.9.1** + **KiKit** + **Interactive HTML BOM v2.12.0** ([GitHub](https://github.com/openscopeproject/InteractiveHtmlBom/releases)).

### 4.4 DFM checks

| Check | Tool |
|---|---|
| Fab capability DRC | **kicad-druid** `.kicad_dru` rule sets for **JLCPCB, PCBWay and a Generic intersection**; 2L/4L/6L variants; PCBWay files include impedance net classes; generated from TOML with CI ([GitHub](https://github.com/Cimos/kicad-druid), v1.2.0, MIT). Small project (41 stars): **review each rule against the fab's current capability page before trusting it**. It has no 8–10 layer HDI rule set, which the LPDDR main board will likely need, so write those from the fab's HDI capability page. Older alternative: [tinfever JLCPCB 4L rules with unit tests](https://github.com/tinfever/KiCAD-Custom-DRC-Rules-for-JLCPCB-with-Unit-Tests) (stale 2023). |
| Fab-side DFM | PCBWay and JLCPCB both run a manual or automated engineering review after upload. Aisler shows an online board inspector. |
| Gerber visual check | KiCad GerbView; `kicad-cli` SVG/PDF renders diffed in CI |
| Assembly DFM | **Gap.** No OSS assembly DFM (component spacing for rework, paste aperture rules, thermal-pad windowing) beyond custom DRC rules. Fallback (commercial): Siemens Valor NPI, or the assembler's DFM report (PCBWay offers one). |

### 4.5 Test fixtures / bed-of-nails

| Recommended | Status |
|---|---|
| **kitfg** (KiCad Test Fixture Generator): test-point footprints → STEP fixture plates for 3D printing or CNC | MIT, last push 2025-03 ([GitHub](https://github.com/hatlabs/kitfg)); Research |
| **kicad-testpoints**: export test-pad coordinates | LGPL-3.0, v0.3.2 ([GitHub](https://github.com/snhobbs/kicad-testpoints)); Usable |
| FreeCAD + build123d to build the fixture from the exported coordinates; KiCad `export ipcd356` for the netlist | Built in |
| Off-the-shelf pogo test fixture kits | Commercial hardware (for example Ingun or QA Technology probes) |

### 4.6 Production test software

| Recommended | Version | License | Notes |
|---|---|---|---|
| **OpenHTF** (Google hardware test framework) | **1.6.3** (2026-10-08) ([GitHub](https://github.com/google/openhtf)) | Apache-2.0 | Phases, measurements with limits, operator UI, output records |
| **HardPy** | **0.25.2** ([GitHub](https://github.com/everypinio/hardpy)) | GPL-3.0 | pytest-based, with a web operator panel and a CouchDB results store |
| **pytest** + **PyVISA 1.16.2** + **PyMeasure 0.16.0** | ([PyVISA](https://github.com/pyvisa/pyvisa), [PyMeasure](https://github.com/pymeasure/pymeasure)) | MIT | Instrument drivers |
| Flashing at test | probe-rs (Rust), U-Boot / `uuu`/`rkdeveloptool`-class SoC loaders (depends on the SoC; not chosen) | | |

The device runs Linux, so most functional tests can run **on the DUT itself** (a Rust test agent) and report to the station over USB. The fixture then mainly provides power, current measurement, audio loopback and RF loopback.

### 4.7 PLM / revision management

| Recommended | Notes |
|---|---|
| **Git (+ Git LFS for STEP/meshes) + tags + GitHub Releases** as the record of truth | The release artifact set is generated by CI (§7) |
| **InvenTree** for part revisions, BOM per assembly revision, builds and serial numbers | MIT |
| KiCad 10 **design variants** for population variants (Commercial vs DIY, HAT options) | ([KiCad 10](https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/)) |
| Issue tracker for ECO/ECN | GitHub issues and projects with an ECO template |

**Gap:** no mature OSS PLM with ECO workflows, approvals and supplier collaboration. Fallback (commercial): Arena, Duro, OpenBOM, Altium 365. Recommendation: Git + InvenTree + an ECO issue template is enough until there is a contract manufacturer relationship.

---

## 5. Lab / bring-up

| Need | Recommended | Version | License | Notes |
|---|---|---|---|---|
| Logic analyser | **sigrok** (PulseView, sigrok-cli, libsigrok, protocol decoders) | **No tagged release in years**; PulseView "continuous" build 2024-08; libsigrok last push 2025-11 ([PulseView](https://github.com/sigrokproject/pulseview), [libsigrok](https://github.com/sigrokproject/libsigrok)) | GPL-3.0 | Still the de-facto OSS LA stack; build from git or use distro packages |
| Oscilloscope client (incl. eye diagrams and decoders) | **ngscopeclient** (libscopehal) | **v0.3** (2026-09-27) ([GitHub](https://github.com/ngscopeclient/scopehal-apps/releases)) | BSD-3 | Supports many Rigol, Siglent, Keysight, LeCroy, Pico scopes and others (list on the project site) |
| SWD/JTAG for MCUs (HAT microcontrollers, PMIC helpers), Rust-first | **probe-rs** | **v0.32.0** (2026-07-22) ([GitHub](https://github.com/probe-rs/probe-rs/releases)) | MIT/Apache-2.0 | `cargo flash`, `probe-rs run`, RTT, defmt |
| SoC JTAG (Cortex-A), boundary scan | **OpenOCD** | **v0.12.0** is still the latest tag (2023-01) ([tags](https://github.com/openocd-org/openocd/tags)); use git master for recent targets | GPL-2.0 | |
| Python debug and automation | pyOCD **0.46.0** ([PyPI](https://pypi.org/project/pyocd/)) | | Apache-2.0 | |
| Power profiling | **Joulescope UI** **v1.7.3** (Apache-2.0) ([GitHub](https://github.com/jetperch/pyjoulescope_ui)); Nordic **PPK2** + nRF Connect Power Profiler **v4.4.1** ([GitHub](https://github.com/NordicSemiconductor/pc-nrfconnect-ppk)) + `ppk2-api-python` (GPL-2.0) ([GitHub](https://github.com/IRNAS/ppk2-api-python)) | | Software open; the instruments are commercial hardware. PPK2 is low-cost; a Joulescope suits Linux suspend and resume profiling | |
| Bench instrument automation | PyVISA / PyMeasure / ngscopeclient | | MIT / BSD | |
| RF bench | tinySA, LibreVNA / NanoVNA + scikit-rf, HackRF | §2.6 | | |
| Thermal imaging | Vendor apps; OSS readers exist for some cameras (**UNVERIFIED**) | | | |

**Gap:** a high-bandwidth scope (≥4 GHz) for MIPI/USB3 bring-up and DDR eye capture is hardware, not software. Fallback: rent one.

---

## 6. Documentation and collaboration

| Need | Recommended | Version | License |
|---|---|---|---|
| Visual schematic/PCB diff per Git commit (web UI) | **KiRI** (KiCad Revision Inspector) | tags up to **1.2.0**; last push 2026-06 ([GitHub](https://github.com/leoheck/kiri)); KiCad 9/10 compatibility reports are mixed ([forum](https://forum.kicad.info/t/kicad-revision-inspector-kiri-problems/63325)): **test it with KiCad 10** | MIT |
| PDF diff of SCH/PCB, also a git difftool; used by KiBot `diff` output | **KiDiff** | **v2.6.0** (2026-06-01) ([GitHub](https://github.com/INTI-CMNB/KiDiff)) | GPL-2.0 |
| Image diffs of layouts | KiCad-Diff (Gasman2014) | stale since 2024 ([GitHub](https://github.com/Gasman2014/KiCad-Diff)) | MIT |
| Embedded interactive viewer of KiCad files in web docs | KiCanvas | **UNVERIFIED** (repository not found under the expected path) | MIT |
| Pinout and board drawings for docs | **PcbDraw** **v1.3.0** ([GitHub](https://github.com/yaqwsx/PcbDraw)), `kicad-cli sch/pcb export svg` | | MIT |
| Renders | Blender **5.2 LTS** (2026-07-14, supported to 2028-07) ([blender.org](https://www.blender.org/releases/5-2/)); `kicad-cli pcb render`; KiBot `blender_export` | | GPL |
| Block, timing and wiring diagrams as code | Mermaid, WaveDrom, Graphviz, draw.io (diagrams.net) | **UNVERIFIED** current versions | MIT / Apache |
| Licensing compliance of the hardware repos | **REUSE tool** **6.2.0** ([GitHub](https://github.com/fsfe/reuse-tool)); `fsfe/reuse-action` **v6.0.0** ([GitHub](https://github.com/fsfe/reuse-action)) | | GPL-3.0 / Apache-2.0 |
| Scripting KiCad from Python (new IPC API) | **kicad-python** (`kipy`) **0.8.0** ([PyPI](https://pypi.org/project/kicad-python/)) | | MIT |
| Publishing a project page with a 1-click BOM | Kitspace (v2, AGPL) ([GitHub](https://github.com/kitspace/kitspace-v2)) | | AGPL-3.0 |

KiBot can also generate a static project site (`kicad_site` output, Hugo-based, new in 1.9.0) ([KiBot docs](https://kibot.readthedocs.io/)).

---

## 7. Integration and release pipeline

Goal: **one command (locally) or one tag (in CI) produces every fab, assembly, documentation and mechanical artifact and runs every check**, so a release can be ordered from PCBWay (likely prototypes), JLCPCB or Aisler (DIY-kit friendly) without hand edits.

### 7.1 Artifact list

#### 7.1.1 Per PCB (main board, faceplate, each HAT, each FPC)

| Artifact | Format / generator | PCBWay | JLCPCB | Aisler |
|---|---|---|---|---|
| Copper, mask, silk, paste, edge | **Gerber RS-274X** (X2 attributes on) via `kicad-cli pcb export gerbers` | Required RS-274X ([PCBWay assembly reqs](https://www.pcbway.com/assembly-file-requirements.html)) | Yes | Accepts native KiCad files (no Gerbers needed) ([Aisler](https://community.aisler.net/t/kicad-10-is-live-and-100-supported-by-aisler/5567)) |
| Drill | Excellon (PTH and NPTH separate) + drill map PDF via `kicad-cli pcb export drill` | Yes | Yes | — |
| IPC-2581 | `kicad-cli pcb export ipc2581` | Acceptance **UNVERIFIED** (not on the assembly-requirements page) | **UNVERIFIED** | Aisler accepts ODB++ ([Aisler](https://community.aisler.net/t/advantages-of-uploading-pcb-board-or-odb-files/2885)) |
| ODB++ | `kicad-cli pcb export odb` | **UNVERIFIED** | **UNVERIFIED** | Yes |
| IPC-D-356 netlist (electrical test) | `kicad-cli pcb export ipcd356` | The PCBWay plugin exports an IPC netlist ([plugin](https://github.com/pcbway/PCBWay-Plug-in-for-Kicad)) | The Fabrication Toolkit exports one ([GitHub](https://github.com/bennymeg/Fabrication-Toolkit)) | — |
| Pick-and-place / CPL | `kicad-cli pcb export pos` (CSV, mm, both sides) → re-formatted per fab (column names, rotation offsets). KiBot `position` + JLC/PCBWay rotation filters | Columns: designator, X, Y, rotation, side; sample file on the requirements page | CPL columns `Designator, Mid X, Mid Y, Layer, Rotation` (format **UNVERIFIED** this session; kicad-jlcpcb-tools generates it) | — |
| BOM (assembly) | KiBot `bom` output with fab-specific column sets | **PCBWay template** ([Sample_BOM_PCBWay.xlsx](https://www.pcbway.com/img/images/pcbway/Sample_BOM_PCBWay.xlsx?v=1.1)). Turn-key needs Line#, Qty, RefDes, Part Number, Description, Package, Type (SMD/THT/Hybrid), **Manufacturer, MPN, Distributor P/N** | JLC needs **LCSC part numbers** (`Comment, Designator, Footprint, LCSC`), handled by [kicad-jlcpcb-tools](https://github.com/Bouni/kicad-jlcpcb-tools) | — |
| Interactive HTML BOM | InteractiveHtmlBom 2.12.0 (KiBot `ibom`) | Recommended as an assembly aid | Same | Same |
| Assembly drawings | `kicad-cli pcb export pdf` (Fab + Courtyard + values, top and bottom) or KiBot `pcb_print` | PCBWay asks for assembly drawings and special instructions | | |
| Schematic PDF | `kicad-cli sch export pdf` | For review and for the fab engineer | | |
| Fab notes + stackup + impedance spec | KiBot `report` (stackup table) + a hand-written `fab-notes.md` → PDF. Include materials, finished thickness, impedance targets per layer and net class with tolerance, impedance coupons, via filling (VIPPO for BGA), surface finish (ENIG for fine-pitch and pogo pads), hard gold on pogo targets if used | Required for impedance-controlled or HDI orders | | |
| Flex / rigid-flex specifics | Separate KiCad board per FPC; fab drawing with **stiffener** locations and thickness, coverlay openings, bend zones (no vias), ZIF finger thickness tolerance, EMI film / hatched ground spec | Rigid-flex up to 16L ([PCBWay](https://www.pcbway.com/rigidflex.html)) | FPC 1/2/4L ([JLCPCB](https://jlcpcb.com/capabilities/pcb-capabilities)) | **UNVERIFIED** |
| 3D PCBA | `kicad-cli pcb export step` (and `glb` for web, `3dpdf` for reviewers) | For enclosure fit checks | | |
| Panel | KiKit panel → the same set re-exported for the panel | PCBWay can panelize itself; supply your own panel when the DIY kit needs break-away tabs | | |
| Statistics | `kicad-cli pcb export stats` (board stats; KiBot `pcb_stats`) | Quote inputs | | |

#### 7.1.2 Mechanical

| Artifact | Generator |
|---|---|
| STEP per part and per assembly | FreeCAD headless (`freecadcmd` / `FreeCADCmd`; exact binary name per package **UNVERIFIED**) running a Python export script |
| STL / 3MF for the DIY kit | Same script (Mesh export); 3MF with slicer profile |
| Drawings PDF (TechDraw) for CNC and injection-moulding quotes | Same script (TechDraw page export to PDF) |
| Renders (product, exploded, docs) | Blender 5.2 headless: `blender -b scene.blend -P render.py` |
| Gasket and FPC flat patterns (DXF) | SheetMetal unfold / TechDraw DXF |

#### 7.1.3 Release bundle

A GitHub Release per hardware tag (for example `mainboard-v1.2.0`) with the zipped fab packages per fab, the docs PDFs, iBOM, STEP, renders and a `MANIFEST` with checksums and tool versions (KiCad, KiBot and image digest).

### 7.2 Checks

| Check | Tool | Fails the build on |
|---|---|---|
| ERC | `kicad-cli sch erc --exit-code-violations` | Any error (exit code 5) ([kicad-cli](https://docs.kicad.org/10.0/en/cli/cli.html)) |
| DRC + schematic parity | `kicad-cli pcb drc --schematic-parity --exit-code-violations` with the fab rule file in the project (`<project>.kicad_dru`) | Any violation or parity mismatch |
| Fab-capability rules | `kicad-druid` PCBWay / JLCPCB / Generic files, copied into the project and pinned ([GitHub](https://github.com/Cimos/kicad-druid)); HDI rules hand-written from the fab capability pages | — |
| BOM sanity | KiBot BOM filters + a Python check: every placed part has Manufacturer + MPN (PCBWay turn-key) or an LCSC number (JLC); no DNP-in-BOM mix-ups; variant consistency (KiCad 10 variants; KiBot support is **experimental** in 1.9.x ([KiBot](https://kibot.readthedocs.io/))) | Missing fields |
| Availability and lifecycle | KiCost + distributor APIs (DigiKey/Mouser/LCSC); Nexar only if a paid plan exists (free evaluation is 1000 parts **lifetime**) ([Nexar](https://support.nexar.com/support/solutions/articles/101000476314-part-limits-and-how-they-work)) | **Warn only** (network-dependent, so do not block CI) |
| REUSE lint | `reuse lint` / `fsfe/reuse-action@v6` | Missing license info |
| Review diffs | KiBot `diff` (KiDiff) on PRs (PDF diff vs the base branch); optionally KiRI for a browsable web diff | Never fails; attached to the PR |
| Visual regression | `kicad-cli pcb render` / `export svg` → image diff vs the last release (ImageMagick `compare`) | Warn |
| Mechanical | FreeCAD headless script: recompute all documents, fail on recompute errors; interference check of the PCBA STEP against the enclosure (OCCT boolean common volume > 0) | Recompute errors or collisions |
| Fab upload dry-run | Manual. No public order APIs are assumed (PCBWay and JLC APIs for automated ordering are **UNVERIFIED**) | — |

### 7.3 Tooling

| Tool | Version | Covers | Notes |
|---|---|---|---|
| **kicad-cli** (KiCad 10.0.7) | 10.0.7 (2026-10-16) ([release](https://github.com/KiCad/kicad-source-mirror/releases)) | ERC, DRC (+parity), Gerbers, drill, pos, **IPC-2581, ODB++**, IPC-D-356, STEP/STPZ/BREP/XAO/GLB/STL/PLY/VRML/U3D, **3D PDF**, SVG/PDF/DXF, render, stats, BOM, netlist, **`jobset run`** ([kicad-cli](https://docs.kicad.org/10.0/en/cli/cli.html)) | `export hpgl` is non-functional in 10.0 (same page). **Jobsets** (`.kicad_jobset`, run by `kicad-cli jobset run`) can replace part of KiBot for simple projects |
| **KiBot** | **1.9.1** (2026-07-28), AGPL-3.0 ([GitHub](https://github.com/INTI-CMNB/KiBot/releases)) | Orchestration: all of the above + BOMs (fab-specific), iBOM, KiCost, KiKit panels, PcbDraw, Blender renders, diffs (KiDiff), stackup/report, `pcb_stats`, `bom_labels`, `kicad_site`; supports KiCad 10 (variants experimental) ([KiBot docs](https://kibot.readthedocs.io/)) | Single `kibot.yaml` per board |
| KiBot images | `ghcr.io/inti-cmnb/kicad10_auto:1.9.1-1_k10.0.4_d13.2`; `ghcr.io/inti-cmnb/kicad10_auto_full:1.9.1-1_k10.0.5_d13.2_b4.2.4LTS` (the `_full` image adds Blender **4.2.4 LTS**, Pandoc, LaTeX and test tools) (tags listed from ghcr.io on 2026-10-21) | | The images **lag KiCad**: 10.0.4/10.0.5 inside vs 10.0.7 upstream. Pin the full tag, or better the **digest** |
| KiBot GitHub Action | `INTI-CMNB/KiBot@v2_k10_1_9_0` (pinned) or `@v2_k10` (moving) ([tags](https://github.com/INTI-CMNB/KiBot/tags)) | | No `v2_k10_1_9_1` tag existed on 2026-10-21. Running the container directly with a digest gives tighter pinning |
| Official KiCad image | `kicad/kicad:10.0.7` / `10.0.7-full` on Docker Hub (tags listed on 2026-10-21) | Plain kicad-cli | Use for kicad-cli-only jobs (ERC/DRC/exports) when the KiBot image lags |
| **KiKit** | 1.8.1 | Panels, fab presets, stencils | Python; also inside the KiBot images |
| **InteractiveHtmlBom** | 2.12.0 | iBOM | |
| Fab plugins (interactive use only) | **PCBWay Plug-in** v1.0.5 (MIT; updated for KiCad 10, assembly orders need MPN fields) ([GitHub](https://github.com/pcbway/PCBWay-Plug-in-for-Kicad)); **Fabrication-Toolkit** (JLCPCB) 5.3.1 (Apache-2.0) ([GitHub](https://github.com/bennymeg/Fabrication-Toolkit)); **kicad-jlcpcb-tools** 2026.04.03 (MIT; LCSC part assignment and JLC files) ([GitHub](https://github.com/Bouni/kicad-jlcpcb-tools)); **AISLER Push** ([Aisler](https://community.aisler.net/t/pcb-design-tool-support-matrix/103)) | | The CI pipeline (KiBot) is the source of truth. Plugins are convenience tools, and their output should match CI's |
| FreeCAD headless | 1.1.4 (AppImage, or conda-forge; conda-forge availability for 1.1.4 **UNVERIFIED**) | STEP/STL/3MF/PDF export, recompute and interference checks | No official FreeCAD container image is known (**UNVERIFIED**). Build a small image from the AppImage (`--appimage-extract`) |
| Blender headless | 5.2 LTS | Renders | Pin the 5.2.x tarball by checksum in the container |

### 7.4 Where each piece lives (recommendation)

| Location | What | Why |
|---|---|---|
| **Developer host** (installed) | KiCad 10.0.x GUI + plugins (PCBWay, JLC tools, iBOM, StepUp in FreeCAD), FreeCAD 1.1.x, Blender 5.2, Python env (uv / pixi) with scikit-rf, openEMS bindings, KiBot/KiKit for local runs, Docker/Podman | Interactive work |
| **Pinned in the hardware repo** | `kibot/*.kibot.yaml`, `<board>.kicad_dru` (fab rules, copied with their source version noted), `.kicad_jobset` (optional), fab templates (BOM column maps, CPL rotation tables, fab-notes template), FreeCAD and Blender export scripts, SI budget notebooks, `REUSE.toml`, `tools.lock` (tool versions + container digests) | Reviewable, versioned with the design |
| **Reproducible container / devcontainer** | `ghcr.io/inti-cmnb/kicad10_auto_full@sha256:…` for KiBot; `kicad/kicad:10.0.7@sha256:…` for plain kicad-cli; an OpenDAP-built `mech` image with FreeCAD 1.1.4 + Blender 5.2; an `sim` image with openEMS + Palace + gmsh + scikit-rf | Same outputs locally and in CI |
| **GitHub Actions** | `ci.yml` (on PR: ERC, DRC, REUSE, KiDiff, quick outputs), `release.yml` (on tag: full artifact set → GitHub Release), `sim.yml` (manual or nightly: gerber2ems runs, slow) | Release gating |

#### Pinning rules (recommendations)

- Pin container images **by digest**, not by tag. Record the human-readable tag next to the digest in `tools.lock`.
- Pin GitHub Actions **by commit SHA**, with the tag in a comment (`actions/checkout`, `fsfe/reuse-action`, the KiBot action). Current major versions of the generic actions (`actions/checkout`, `actions/upload-artifact`, a release action) are **UNVERIFIED** in this session.
- Upgrading KiCad (for example 10.0.7 → 10.0.8) is its own PR. It re-runs DRC and diffs outputs against the previous release so file-format or output drift shows up.

### 7.5 Recommended layout for an OpenDAP hardware repo (recommendation only)

```text
<board-repo>/                      # e.g. mainboard, faceplate-<name>, hat-<name>, fpc-<name>
├── REUSE.toml
├── LICENSES/
├── tools.lock                      # tool versions + container digests used by CI
├── hardware/
│   ├── <board>.kicad_pro
│   ├── <board>.kicad_sch  (+ sub-sheets)
│   ├── <board>.kicad_pcb
│   ├── <board>.kicad_dru           # fab capability rules (from kicad-druid + HDI additions)
│   ├── <board>.kicad_jobset        # optional, for kicad-cli-only flows
│   ├── lib/                        # project symbols, footprints, 3D (STEP)
│   └── sim/                        # SPICE test benches, IBIS files (if license allows)
├── kibot/
│   ├── check.kibot.yaml            # ERC, DRC, BOM sanity — used on PRs
│   ├── fab-pcbway.kibot.yaml       # Gerber/drill/IPC-356/pos/BOM in PCBWay format
│   ├── fab-jlcpcb.kibot.yaml       # same in JLC format (LCSC BOM, CPL)
│   ├── fab-aisler.kibot.yaml       # native project zip + docs
│   ├── docs.kibot.yaml             # schematic PDF, assembly PDF, iBOM, renders, STEP, 3D PDF
│   └── diff.kibot.yaml             # KiDiff vs base ref
├── fab/
│   ├── fab-notes.md                # stackup, impedance table, finish, VIPPO, coupons, flex notes
│   ├── stackup/                    # fab-confirmed stackup PDFs, impedance reports
│   └── templates/                  # BOM column maps, CPL rotation corrections per fab
├── mechanical/
│   ├── <board>-keepout.FCStd       # skeleton interface (owned by the mechanical repo, mirrored)
│   └── scripts/                    # FreeCAD headless export / interference check
├── si/
│   ├── budgets/                    # loss/crosstalk budgets (Python/notebooks)
│   ├── gerber2ems/                 # simulation configs per critical net
│   └── touchstone/                 # vendor and simulated .sNp (check license before committing)
├── test/
│   ├── fixture/                    # kitfg/FreeCAD fixture sources
│   └── production/                 # OpenHTF/HardPy test sequences
├── .devcontainer/devcontainer.json
└── .github/workflows/
    ├── ci.yml
    ├── release.yml
    └── sim.yml
```

A separate **mechanical repo** (enclosure, faceplates, gaskets, DIY-kit printables) uses the same pattern: `freecad/`, `scripts/`, `drawings/`, `.github/workflows/release.yml` → STEP/STL/3MF/PDF/renders.

### 7.6 How other open-hardware projects do it

- **ZSWatch** (dock and dev-kit hardware): KiCad + **KiBot CI/CD** with workflow stages **DRAFT → PRELIMINARY → CHECKED → RELEASED**, generating Gerber, BOM and docs per release ([ZSWatch devkit](https://awesome.ecosyste.ms/projects/github.com%2Fzswatch%2Fwatch-devkit-hw), [cadlab](https://cadlab.io/projects/dock-hw)). This is a good model for OpenDAP's board maturity labels.
- **KiCad-Project-Skeleton**: GitHub Actions + KiBot producing review Gerbers on PRs and a release set (Gerbers, JLC assembly files, schematic PDF, CSV BOM, iBOM, 3D models) on tags ([GitHub](https://github.com/bob-swinkels/KiCad-Project-Skeleton/blob/main/README.md)).
- **Antmicro**: publishes its open hardware with an OSS SI flow (gerber2ems + openEMS) running on the fab outputs ([Antmicro SI blog](https://antmicro.com/blog/2023/11/open-source-signal-integrity-analysis), [trace selection](https://antmicro.com/blog/2024/07/automated-pcb-trace-selection-for-si-simulation)). This is the closest reference for OpenDAP's high-speed work.
- **Aisler** promotes uploading native KiCad projects, which reduces the release set for that fab to the project zip + docs ([Aisler](https://community.aisler.net/t/advantages-of-uploading-pcb-board-or-odb-files/2885)).
- Common pattern: sources in Git, **outputs only in Releases** (not committed), a human-readable `CHANGELOG` per board revision, and OSHWA certification / CERN-OHL licensing for the hardware. Which hardware license to use is an **maintainers' decision** and is not proposed here.

---

## 8. Prioritized list (recommendations)

### Needed now

1. Containerised **kicad-cli 10.0.7 + KiBot 1.9.1** pipeline skeleton (§7.5) with ERC/DRC/REUSE on PRs, even before there is a real board.
2. **InvenTree** instance (or decide not to) + **Ki-nTree** for part creation; a library policy (project-local `lib/`).
3. FreeCAD **skeleton/interface model** (board outlines, connector datums, display, battery envelope) + **KiCad StepUp** on every developer host.
4. **Python env** with scikit-rf, openEMS bindings, gmsh, numpy/scipy (locked with uv or pixi).
5. Contact PCBWay (and JLC/Aisler) for **flex and HDI stackups with impedance**. These are an input to every later decision.

### At schematic stage

1. **ngspice 47** test benches for the audio chain (noise, THD, WAV through the model) and the charger and power paths; **Qucs-S 26.1.1** for RF HAT filters.
2. Collect **IBIS / IBIS-AMI / S-parameter** models (SoC, LPDDR, FPC connectors, pogo pins). Flag NDA-gated ones early.
3. KiCad 10 **design variants** for Commercial vs DIY; BOM fields required by PCBWay turn-key (Manufacturer, MPN, distributor P/N) and LCSC numbers for JLC.
4. KiDiff in PR CI (schematic PDF diffs).

### At layout

1. Fab rule files (**kicad-druid** + hand-written HDI rules) in each project.
2. KiCad 10 **time-domain tuning profiles** for LPDDR, MIPI, PCIe, USB3.
3. **gerber2ems/openEMS** on critical nets; **Palace + gmsh** for connector and pogo regions; **scikit-rf / SignalIntegrity / PyBERT** for budgets and eyes.
4. **padne** DC IR drop; Elmer thermal with smeared copper.
5. KiKit panel definitions for the DIY kit.

### At mechanical prototyping

1. CalculiX (FreeCAD FEM) for snap-fits, bosses and gasket compression; **OpenCourant** drop screening (accept the fork risk) or physical drop tests.
2. **OrcaSlicer / PrusaSlicer** profiles for the DIY kit; 3MF in releases.
3. FreeCAD **CAM** for fixtures; **kitfg / kicad-testpoints** for bed-of-nails plates.
4. FPC **bend tests** and **IP65 pre-tests** (physical); rent a ≥20 GHz VNA or TDR for FPC + pogo characterisation.

### At production

1. **OpenHTF or HardPy** station + PyVISA/PyMeasure; an on-DUT Rust test agent.
2. Lifecycle monitoring (KiCost + distributor APIs; a paid Nexar plan if needed).
3. Moulder's **DFM + mould-flow report** as a tooling deliverable (commercial, by the vendor).
4. Accredited lab for EMC (CE/FCC) and IP65 certification.
5. PLM: Git + InvenTree + ECO issue template. Reassess when a CM is chosen.

---

## 9. Tools to install on the developer host (recommendations, not decisions)

| Tool | Version (2026-10-21) | License | How (suggested) | Priority |
|---|---|---|---|---|
| KiCad | 10.0.7 | GPL-3.0 | Official installer / distro / Flatpak | Now |
| KiCad plugins: InteractiveHtmlBom, KiKit, PCBWay Plug-in, kicad-jlcpcb-tools, Fabrication-Toolkit | 2.12.0 / 1.8.1 / 1.0.5 / 2026.04.03 / 5.3.1 | MIT / MIT / MIT / MIT / Apache-2.0 | KiCad Plugin and Content Manager | Now |
| FreeCAD (+ KiCad StepUp, SheetMetal, Fasteners, CfdOF addons) | 1.1.4 | LGPL-2.1 | AppImage / installer; Addon Manager | Now |
| Blender | 5.2 LTS | GPL | Official tarball | Now (already chosen) |
| Docker or Podman | **UNVERIFIED** | Apache-2.0 | Distro | Now |
| Python toolchain (uv or pixi) | **UNVERIFIED** | MIT / BSD | — | Now |
| KiBot (local runs; CI uses the container) | 1.9.1 | AGPL-3.0 | `pipx install kibot` or container | Now |
| REUSE tool | 6.2.0 | Apache-2.0 etc. | `pipx install reuse` | Now |
| Rust + probe-rs | probe-rs 0.32.0 | MIT/Apache-2.0 | `cargo install probe-rs-tools` / installer script | Now |
| ngspice (standalone, beyond KiCad's bundled one) | 47 | BSD-3 | Distro / source | Schematic |
| Qucs-S | 26.1.1 | GPL-2.0 | Distro / AppImage | Schematic |
| InvenTree (server, shared) + Ki-nTree | 1.6.1 / 1.2.1 | MIT / GPL-3.0 | Docker compose / pip | Now (shared service) |
| KiCost | 1.1.21 | MIT | pip | Schematic |
| KiDiff / KiRI | 2.6.0 / 1.2.0 | GPL-2.0 / MIT | pip / repo; test KiRI with KiCad 10 | Schematic |
| openEMS + CSXCAD (Python) | v0.37.0 | GPL-3.0 | Build from source (Linux/macOS) | Layout |
| gerber2ems | v0.99.0 | Apache-2.0 | pip from git | Layout |
| Palace | v0.18.1 | Apache-2.0 | Spack / container | Layout |
| gmsh | 4.15.2 | GPL-2.0+ | pip | Layout |
| scikit-rf | 2.2.0 | BSD-3 | pip | Schematic/Layout |
| SignalIntegrity | 1.5.2 | GPL | pip | Layout |
| PyBERT + PyIBIS-AMI | 11.1.0 / 10.0.0 | BSD-style (**UNVERIFIED**) | pip / conda | Layout |
| padne | v0.3 | GPL-3.0 | Per project docs | Layout |
| Elmer FEM | 26.2 | GPL-2.0 / LGPL | Distro / installer | Layout / Mech |
| CalculiX | 2.23 | GPL-2.0 | Distro / FreeCAD bundle | Mech |
| OpenCourant (ex-OpenRadioss) | latest-20261011 | AGPL-3.0 | Build / container | Mech (optional) |
| OpenFOAM | v2606 | GPL-3.0 | Docker / packages | Mech (only if needed) |
| PyBaMM | 26.10.1.1 | BSD-3 | pip | Mech (battery thermal) |
| build123d / CadQuery | 0.13.0 / 2.8.0 | Apache-2.0 | pip | Mech (optional) |
| OrcaSlicer / PrusaSlicer | 2.4.2 / 2.9.6 | AGPL-3.0 | Official builds | Mech (DIY kit) |
| sigrok (PulseView, sigrok-cli) | git / distro | GPL-3.0 | Distro or build | Bring-up |
| ngscopeclient | v0.3 | BSD-3 | Official builds | Bring-up |
| OpenOCD | 0.12.0 (or git master) | GPL-2.0 | Distro / source | Bring-up |
| Joulescope UI / nRF Connect Power Profiler | 1.7.3 / 4.4.1 | Apache-2.0 / Nordic license | Official builds (only if the hardware is bought) | Bring-up |
| Friture | 0.54 | GPL-3.0 | pip / distro | Bring-up (audio) |
| NanoVNA-Saver / LibreVNA GUI | 0.7.3 / 1.6.5 | GPL | Official builds | Bring-up (RF HATs) |
| OpenHTF or HardPy, PyVISA, PyMeasure | 1.6.3 / 0.25.2 / 1.16.2 / 0.16.0 | Apache-2.0 / GPL-3.0 / MIT / MIT | pip | Production |
| kitfg / kicad-testpoints | git / 0.3.2 | MIT / LGPL-3.0 | pip from git | Production |

### Commercial fallbacks named in this report (only where OSS has a gap)

Mould flow: Autodesk Moldflow, Moldex3D, SolidWorks Plastics (or the moulder's report). Explicit drop: LS-DYNA, Abaqus/Explicit. 3D tolerance: CETOL 6σ, 3DCS. MBD/PMI: SolidWorks MBD, Creo. AC PI: Sigrity PowerSI, HyperLynx PI, SIwave, Clarity. DDR sign-off: Sigrity SystemSI, HyperLynx DDRx, ADS Memory Designer. Planar RF: ADS Momentum, Sonnet, CST. Electronics thermal: Flotherm, Icepak, Celsius. Audio: Audio Precision APx, QuantAsylum QA40x. EMC: spectrum analyser with EMI option + accredited lab. Assembly DFM: Valor NPI. Lifecycle: SiliconExpert, Z2Data, paid Nexar. PLM: Arena, Duro, OpenBOM, Altium 365. Instruments to rent: ≥20 GHz VNA / TDR, ≥4 GHz scope.

## 10. Not covered or not verified

- FreeCAD 1.1 official release notes could not be read (bot protection), so Assembly limitations, draft-analysis availability and the headless binary name are **UNVERIFIED**.
- Whether PCBWay and JLCPCB accept **IPC-2581 / ODB++** for fab and assembly orders was not confirmed. Gerber RS-274X + Excellon + CSV is the safe baseline.
- JLCPCB CPL/BOM exact column names were not re-checked this session.
- Vendor availability of S-parameters for specific FPC connectors and pogo pins was not checked. It depends on the parts, which are not chosen.
- Current versions of Xyce, PrePoMax, atlc, KiCanvas, Mermaid/WaveDrom, Docker/Podman, uv/pixi and generic GitHub Actions were not checked.
- Whether the OpenRadioss wiki and its drop-test examples stay reachable after the 2026-10-01 takedown is unknown.
