# Research: contact-based battery interfaces

- **Date:** 2026-10-24
- **Status:** Desk research and method. Not a decision. Nothing here has been built or tested. Engineering input only, not legal advice.
- **Question:** how an OpenDAP device chooses and qualifies a battery interface in which the pack connects through contacts (spring, blade or pad contacts) instead of a cable and a cable connector, so the listener can replace the pack without unplugging a lead or desoldering.
- **Why:** the maintainers' aim (2026-10-24): a battery the listener replaces easily, for the right to repair and because many commercial players in this range have had battery problems; replacing the pack should not mean replacing the device.
- **Application:** each device keeps its application in its own repository. The first is the T1: [board ADR 0020](https://github.com/opendap-project/board/blob/main/docs/adr/0020-battery-connected-through-contacts.md) and the [T1 contact battery interface research](https://github.com/opendap-project/board/blob/main/docs/research/2026-10-contact-battery-t1.md).
- **Quality levels:** checks and tests below carry the lowest [RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md) level at which they become mandatory. Safety items are Q0.
- **Conventions:** every value names its source. Web sources were retrieved on 2026-10-24. **UNVERIFIED** marks a value not read in a primary source (a datasheet, the standard's text, the regulation, a patent, a service manual). Arithmetic is shown as such. Standards that were not accessible (IEC 62368-1, IEC 60601-1, EIA-364) are cited by number only.

## 0. Summary

1. **A contact interface is ordinary practice for user-replaceable packs**: camera packs, removable-battery phones (including IP67 and IP68 ones), two-way radios, power tools and drones all use flat pads or blades on the pack against springs in the host (§1). Every sealed precedent seals at the cover or the host, not at the contacts.
2. **The documented failure is loss of contact pressure, not the contact itself.** Fairphone 4 users report reboot loops after drops, from a loss of contact of about an eighth of a millimetre, cured by a shim under the battery (§1.2). The interface therefore has to be designed as a mechanical system: the pack is retained by the case, preloaded against the contacts, and the springs keep their force over the whole tolerance stack and swelling.
3. **Power is carried by several contacts in parallel**, signals by separate low-current contacts referenced to the negative terminal (DJI 4 + 4, Makita 2 + 2, Fairphone 5 2 + 2). Each power pole is sized by the method in §3.
4. **Gold against gold, with enough force and stroke.** Hard gold over nickel on both sides; tin is excluded for a contact that sees micromotion (fretting). Normal force and stroke are checked at the worst tolerance, not at nominal (§3.3).
5. **At a 2S pack's voltage a sustained arc cannot form** (minimum arc voltage of gold 15 V, TE; §4.4), so make and break under load erode contacts only by sparks. Inrush and removal under load are handled by the host's power path (a ship or load-switch FET that turns on slowly), sequencing by contact geometry, and a cover-open signal that lets the system power down in order before the pack can be reached.
6. **Standards on exposed terminals:** IEC 62133-2 clause 5.5 (contacts carry the maximum anticipated current, resist corrosion, minimise short-circuit risk, keyed or polarity-marked) and the external short-circuit tests (IEC 62133-2 7.3.2, UN 38.3 T.5) apply to the pack with its terminals as shipped. The pack therefore keeps its PCM between cells and pads, recesses its pads, and ships with a terminal cover or in a separating package.
7. **Regulation (EU) 2023/1542 Art. 11** asks for removal with commercially available tools, no heat or solvents, and spare packs for five years; a non-washable device does not qualify for the wet-environment derogation (§5). A contact interface behind a screwed cover meets Art. 11 as well as a cable does, and removes the step listeners most often get wrong (unplugging a small latched connector).

## 1. Precedents

Accessed 2026-10-24. Values not read in a primary source are marked.

### 1.1 Camera packs

| Item | Contacts | Detail | Source |
|---|---|---|---|
| Sony four-terminal pack (model **UNVERIFIED**) | 4 flat pads: control, −, temperature, + | Copper foil pads with a gold-plated layer; pad length 3 mm; widths 4.25 mm (+), 3.85 mm (−), 2.7 mm (temperature, control); gaps 1.2 mm and 1.65 mm sized so a misaligned − contact cannot land on the thermistor pad; two asymmetric recesses prevent reverse insertion; a locking portion engages a claw in the camera | US 9,799,930 (terminals 21a–21d, locking portion 51); WO 2013/171813 A1 |
| Canon battery cover switch | — | A switch detects the cover opening during a card write; the camera halts the write, keeps volatile memory powered, warns and resumes when the cover closes; a separate lock lever must be turned before the battery comes out | US 7,324,140 B2 (Fig. 5, steps S110–S118) |
| Canon LP-E6 | 4 pads: 2 power, 2 others (one thermistor, 10–20 kΩ) | **UNVERIFIED** (forum measurement) | edaboard.com thread 330217 |

Official pinouts and current ratings of the Sony NP-FW50, NP-FZ100, NP-F and Canon LP-E6 were not found.

### 1.2 Phones

| Device | Contacts and sealing | Source |
|---|---|---|
| Fairphone 4 (IP54) | Four gold spring pins on the phone. After drops, reboot loops and erratic charging; one user reports about an eighth of a millimetre of lost contact; users fix it with a paper shim under the battery to restore pressure | forum.fairphone.com threads 104289 (post 1), 95387 (posts 1–4); iFixit guide 152861 step 5 |
| Fairphone 5 (IP55) | 7 contacts from the schematic connector P2201: VBAT ×2, GND ×2, NTC, NFC ×2 (**UNVERIFIED**, user reading of the schematic). Battery goes in top edge first, then is pressed down; back cover on snap clips | forum.fairphone.com thread 107772 (posts 1, 4); iFixit guide 168819 steps 2–4 |
| Samsung Galaxy S5 (IP67) | Removable battery; rubber gasket in the removable back cover; 3.85 V, 10.78 Wh | iFixit teardown 24016 steps 3–5 |
| LG G5 | Battery on a slide-out module with many spring contacts; separating it "takes a pretty serious tug"; a spring shock absorber gives a click on insertion | iFixit teardown 61205 steps 5, 6, 9 |
| Samsung Galaxy XCover Pro | Blade type: grooves in the battery engage metal prongs in the bay first, then the battery hinges down | iFixit guide 213287 step 2 |
| Samsung Galaxy XCover 6 Pro, 7 (IP68) | The gasket on the back cover seals the battery bay; the battery's contact face is not sealed (secondary source: press) | gsmarena.com news 55945; XCover 7 hands-on |

### 1.3 Two-way radios (the same 2S class)

| Radio | Numbers | Source |
|---|---|---|
| Kenwood NX-5300 | 7.5 V ± 20 %; battery feed through a 3.15 A fuse to the RF amplifier, plus a 1 A branch fuse; transmit stops at about 5.8 V; the radio identifies the pack type; the battery terminal block is a separate part held by two screws; sealing on the radio side | Service manual B5B-7154-10, pp. 1-2, 1-3, §2.4.6.5, §2.4.7 (p. 1-16), §3.2.7 (p. 1-27) |
| Icom IC-F52D | 7.5 V; 1.8 A at 5 W transmit; IP67 | icomamerica.com, IC-F52D specifications |
| Motorola XPR 7000e | 7.5 V; IP68 (2 m, 2 h) with a removable smart battery | Data sheet p. 2 |

### 1.4 Power tools and drones

| Pack | Design | Source |
|---|---|---|
| Makita | Spring female terminals in the pack grip flat male blades of the tool at two points along the slide; signal blade bevelled; 2 positive, 2 negative and 6 signal terminals; upper and lower leaf springs of different lengths so they do not resonate together under shock | US 8,282,413 B2; US 9,577,228 B2 |
| Black & Decker / DeWalt | One positive, two negative terminals and a logic block; phosphor-bronze or beryllium-copper tongues; one negative blade "slightly offset (or longer)" so it mates first | US 7,944,174 B2 (Fig. 10) |
| DeWalt FlexVolt | An earlier sliding contact could lift off its pad and "could result in an arc"; replaced by a spring-loaded U contact | US 10,193,111 B2 (Figs. 12, 13) |
| DJI Mavic 2 | 10 contacts at 2.5 mm pitch: 4 positive, SMBus data and clock, 4 negative; 4S, 15.4 V | dji-firmware-tools wiki, WM240 battery board (secondary) |

### 1.5 Medical handhelds

No user-replaceable contact pack with published contact data was confirmed in this pass. IEC 60601-1 subclause 15.4.3 (batteries) was not accessible; its content is **UNVERIFIED**.

### 1.6 What the precedents teach

- Power over several parallel contacts per pole; signals on their own contacts, referenced to negative.
- First-make negative has a precedent (US 7,944,174 B2); none breaks power before the pack is free. Cameras instead detect the door and let the system act first (US 7,324,140 B2).
- Contact pads sized and spaced so a misaligned contact lands on nothing harmful; asymmetric recesses or blades for keying.
- Pressure loss after a drop is the recorded failure; springs of different resonance and a preloaded pack are the recorded cures.
- Sealing is a cover or host function.

## 2. Architectures

| Architecture | Host side | Pack side | Strengths | Weaknesses |
|---|---|---|---|---|
| **A. Face compression** | Compression contacts on the board, through a window in the pocket floor | Pads on the pack's face toward the board | Drop-in pack, no sliding; contacts hidden under the pack | Working height set by the gap under the pack (often under 2 mm); spring force pushes the pack toward the cover, which must hold it; contacts occupy the zone under the pocket |
| **B. End-face side contacts** | Side-acting spring contacts at the pocket end, on the board or a bracket | Recessed pads on the pack's end face (on the PCM board or its end cap) | Wipe on insertion; uses the length usually reserved for a lead exit; taller parts allowed outside the pocket footprint; the phone precedent | Pack goes in end first, then down; the spring pushes the pack against the far wall, so length tolerances enter the stroke |
| **C. Pogo array** | Spring-loaded pins (single or array) in A or B | Flat pads | High cycle life; force and height defined; staggered free heights give sequencing | Per-pin current low (2–3 A) unless high-current pins are used; pins are tall for A |
| **D. Blade and socket** | Blades or forks (power-tool style) | Spring sockets in the pack | Highest current, two-point grip, long wipe | Large; a slide-in pack and a latch; not a pocket device's form |

The choice follows the device's z budget and where its pack PCM sits. For a pocket device with the pack behind the board, B is usually the best fit; A where the gap under the pack allows 2–3 mm of working height.

## 3. Choosing the contacts

### 3.1 Current per pole

1. Take the pole's worst continuous current `I` (the device's worst case) and its protective limit `I_trip` (pack PCM trip, board fuse).
2. With `n` contacts in parallel per pole, the current per contact is not `I / n`: contact resistances differ, and the lowest takes more. Use a sharing factor `k`: `I_contact = k × I / n`, with `k = 1.25` for two contacts and `1.4` for three or more from the same reel (assumption, to be replaced by the measured spread of the chosen part: `k = n × R_max / Σ R`, worst-case after durability).
3. Apply the device's derating rule (OpenDAP: ≤ 70 % of the rated current at the worst continuous case, BRD-049 on the T1) to `I_contact`, and check that each contact also carries `k × I_trip / n` without exceeding its rating, for the time the protection needs to act.
4. Read the rating's definition: most makers rate a contact at a temperature rise (often 30 K, EIA-364-70). In a closed battery bay next to a pack that must stay below its own limit, use the rise the pack allows, not the maker's.

### 3.2 Resistance budget

- **Drop and heat:** `ΔV = I × (R_P+ + R_P−)` and `P = I² × R` per pole, with end-of-life resistance (after durability and environment), not initial.
- **Charging** is not made unsafe by resistance: a series drop only lowers the cell voltage the charger reaches during constant current, and the drop falls to zero as the current tapers. It only lengthens the constant-voltage phase.
- **Gauge:** a coulomb counter on a sense resistor in the host is not affected by contact resistance. Cell voltages measured in the host include the drop of the contacts in the current path. Either carry a separate sense contact (Kelvin) to the pack terminal, or accept the error as part of the pack impedance the gauge models, provided the resistance is stable. Instability (fretting, contamination) is what corrupts impedance-tracking gauges, so stability is the criterion, not the absolute value.

### 3.3 Mechanics

| Criterion | Method |
|---|---|
| Plating | Hard gold over nickel on both sides; gold thickness for the cycle life (0.76 µm gold is Samtec's 100-cycle reliability standard); never gold against tin |
| Normal force | Gold: about 0.3–0.4 N minimum; tin: about 1 N minimum (Samtec plating FAQ; secondary). Check force at the worst tolerance position, not at nominal |
| Stroke | Working range ≥ the tolerance stack between contact and pad (pocket, pack, pack swelling over life, assembly) plus margin; the pack is preloaded against the contacts so drops do not lift it |
| Wipe | Side-acting contacts wipe the pad on insertion, which clears films; compression contacts wipe little and rely on force |
| Retention | The case retains the pack, never the contacts. Inertial force in a drop (pack mass × deceleration) is orders of magnitude above any spring force |
| Vibration and shock | Event detection during vibration and drop (EIA-364-87 for nanosecond events, EIA-364-46 for microsecond events; both **UNVERIFIED** text); springs of different resonance where several contacts share a pole (US 9,577,228 B2) |
| Cycles | Rated cycles ≥ 10 × the expected pack swaps over life, plus factory and service; at least 500 |
| Availability | Two makers or two families with a compatible land where possible; stock checked and dated |

### 3.4 Height and placement

Place the contacts where taller parts are allowed (outside the pocket footprint), away from antenna keep-outs and heat sources, and where the board's battery path to the charger and fuse is shortest. Keep the area around the contacts free of any other net (unfused copper).

## 4. Electrical design

### 4.1 Sequencing

- **Make:** negative first, then positive, then signals (thermistor, mid-cell tap, data). **Break:** signals first, then positive, then negative. With side-acting contacts and a pack inserted end first, sequencing comes from pad length and position along the insertion path; with compression contacts, from staggered free heights or pad heights.
- Every signal line is safe in any order anyway (series resistance and clamping per the receiving part's absolute maximum), because a pack can be tilted.
- The thermistor line opening first tells the charger the pack is gone (a missing-thermistor fault) before the power contacts part.

### 4.2 Hot insertion and inrush

The host capacitance that the pack sees at the moment of contact sets the inrush. A ship FET or load switch between the pack and the charger's battery node, off until the charger has powered up and then turned on by a slow gate drive, limits the inrush to the small capacitance on the pack side (sense filters). Where the FET is already on at insertion (an adapter keeps the charger running), estimate the peak as the pack's open-circuit voltage minus the node voltage over the loop resistance, and check that its duration is far below the pack PCM's short-circuit detection delay and the fuse's melting I²t. Ceramic capacitors ring up to twice the step; check the absolute maximum of every part on the node, or damp the node (an RC snubber as the charger maker recommends).

### 4.3 Removal under load

- **Hardware:** the system loses its battery supply at once if no adapter is present. Nothing in the safety chain may depend on software (single-fault safety). The thermistor line opening first stops charging in hardware.
- **Data integrity:** a cover-open signal (a contact or sensor that changes state when the battery cover is lifted, before the pack can be reached) lets the system sync storage and power down in order, as cameras do (US 7,324,140 B2). It is a convenience for data, not a safety function.
- With an adapter present, a power-path charger keeps the system running and reports the missing battery.

### 4.4 Arcing

Minimum arc voltage: gold 15 V, palladium 15 V, silver 12 V (TE, *Contact Arc Phenomenon*). Below it a sustained arc cannot form, whatever the current. A 2S pack (≤ 8.8 V) is below all of them; 4S and higher packs (≥ 16.8 V) are not, and need the load to be off before the contacts part (a cover interlock that opens the power path in hardware). Minimum arc currents for these metals were not verified in this pass.

### 4.5 Keying and polarity

Mechanical keying in the pack and the pocket so the pack fits one way only; pads on one face only, so an inverted pack touches nothing; pad order and gaps chosen so a one-pitch misalignment cannot join the positive terminal to a signal contact (the Sony gap rule in §1.1). IEC 62133-2 clause 5.5 asks for a keyed interface or polarity marking.

### 4.6 ESD and contamination

Exposed pads are touched during every replacement. The host puts ESD protection on each signal contact at the contacts, with its return to the ground plane at the pad; the pack's PCM is the pack side's protection. The pocket keeps conductive debris away from the contacts (no loose metal parts, no screws that can fall into the bay).

## 5. The pack side

| Item | Requirement and reason |
|---|---|
| Pads | On the PCM board or a terminal board in the pack's end cap; hard gold over nickel; sized for the host contact's position tolerance; recessed below the cap surface so a flat metal object cannot bridge them (IEC 62368-1 Annex M burn hazard from carried batteries, **UNVERIFIED** clause text) |
| Protection | PCM between cells and pads (over-charge, over-discharge, over-current, short-circuit); the external short-circuit tests are run on the pack as shipped: IEC 62133-2 7.3.2 (80 ± 20 mΩ, 20 ± 5 °C, with a single fault in the protection circuit) and UN 38.3 T.5 (< 0.1 Ω, 57 ± 4 °C; case ≤ 170 °C, no rupture or fire within 6 h) (read from test reports' requirement columns, not the standards) |
| Contact rules | IEC 62133-2 clause 5.5: carry the maximum anticipated current, mechanically strong and corrosion-resistant, arranged to minimise short-circuit risk, polarity marked unless keyed |
| Keying | Asymmetric end cap or recesses that match the pocket |
| Transport | Terminal cover or separating packaging for spares (UN 38.3 and IATA packing instructions; short-circuit protection of exposed terminals in transport) |
| Label | The regulatory marks of the device's markets on the pack (on EU markets Regulation (EU) 2023/1542 Art. 13 and the WEEE bin), polarity at the pads, the pack specification identifier |
| Specification | Published, so any maker can build a replacement (right to repair; spare packs for five years after the last unit, Art. 11(7)) |

### 5.1 Regulation (EU) 2023/1542 Art. 11 (read from the official text)

- 11(1): portable batteries "readily removable and replaceable by the end-user at any time during the lifetime of the product"; removable "with the use of commercially available tools, without requiring the use of specialised tools, unless provided free of charge with the product, proprietary tools, thermal energy, or solvents".
- 11(2)(a): the derogation covers appliances designed to operate primarily in wet environments and intended to be washable or rinseable; replacement by independent professionals is still required. Commission guidelines C/2025/214 §3 map these to IPX4 to IPX7 and give toothbrushes and shavers as examples. A portable player is not such an appliance, so an IP rating does not exempt it.
- 11(6): "readily replaceable" means another compatible battery can be fitted without affecting functioning, performance or safety.
- 11(7): spare batteries available for five years after the last unit of the model is placed on the market. 11(8): software must not impede replacement.
- Art. 96(2)(a): Art. 11 applies from 18 February 2027. C/2025/214 §2.1: "commercially available tools" covers basic tools or no tools and tools classified in EN 45554:2020; the end user is an adult with no specific experience.

## 6. Qualification plan

Run on the chosen board contact and a sample of packs (or pad coupons with the pack's plating) from each pack maker.

| ID | Test | Pass criterion | Level |
|---|---|---|---|
| CB-01 | Contact resistance, initial (4-wire, dry circuit) | ≤ the device budget per contact | Q1 |
| CB-02 | Temperature rise at the worst continuous current per pole, and at the trip current for the protection's time | Within the pack's and the contact's limits; the device's derating met | Q0 (trip), Q1 |
| CB-03 | Durability: rated cycles with the real pack motion (insert end first, press down) | ΔR within the maker's limit; no plating wear-through | Q2 |
| CB-04 | Vibration and mechanical shock with event detection; device drop tests with the pack fitted | No interruption longer than the system's hold-up; no reset | Q2 |
| CB-05 | Thermal cycling, damp heat, and a corrosive-gas exposure (mixed flowing gas or H₂S, where the market needs it) | ΔR within limits | Q2 |
| CB-06 | Fretting: micromotion at the pad over the device's vibration spectrum | Resistance stable | Q3 |
| CB-07 | Insertion with and without an adapter: inrush current and voltage at every part on the battery node | Within absolute maxima; no PCM trip; fuse I²t far below melting | Q0 |
| CB-08 | Removal under the worst load, with and without an adapter | No damage; system behaviour as designed (cover-open power-down, power path takes over) | Q1 |
| CB-09 | Reverse, tilted and one-pitch-misaligned insertion attempts | No contact between the wrong poles; no damage | Q0 |
| CB-10 | ESD on the pads and the host contacts (IEC 61000-4-2) | No damage; no lasting fault | Q2 |
| CB-11 | Pack external short circuit at the pads (IEC 62133-2, UN 38.3 T.5) | Pass, in the pack makers' reports | Q2 (UN 38.3), Q3 |
| CB-12 | Gauge accuracy through the contacts after CB-03 to CB-06 | State-of-charge error within the device's target | Q3 |

## 7. Checklist for a device

1. Worst continuous current and protective limits per pole; contacts per pole by §3.1.
2. End-of-life resistance budget: drop, heat, gauge effect (§3.2); Kelvin contact or not, with the reason.
3. Architecture and z, placement, keep-outs (§2, §3.4).
4. Tolerance stack and preload; stroke and force at the worst position (§3.3).
5. Sequencing, inrush, removal under load, arcing, keying, ESD (§4).
6. Pack specification additions (§5).
7. Qualification rows with levels in the device's verification matrix (§6).

## Sources

All retrieved 2026-10-24 unless stated.

- Regulation (EU) 2023/1542, official text: <https://publications.europa.eu/resource/celex/32023R1542> (Art. 11, Art. 96).
- Commission guidelines C/2025/214 on Art. 11 (OJ C, 10.1.2025): <https://eur-lex.europa.eu/eli/C/2025/214/oj/eng> (§2.1, §3). The retrieved text of §3 reads "IP rating alone is considered as sufficient", which context suggests should read "not sufficient": to verify against the PDF (**UNVERIFIED**).
- IEC 62133-2:2017, clauses 5.5, 5.6.1, 7.3.2: requirement column of a CB test report, <https://akkuteile.de/tpl/download/HOHM_GROWN2_IEC62133.pdf>, pp. 5–10 (secondary). Changes by A1:2021 **UNVERIFIED**.
- UN Manual of Tests and Criteria, 38.3.4.5 (T.5), Rev. 6 wording, from a test summary: <https://static.lenovo.com/ww/docs/regulatory/SB10K97659_UN38.3.pdf> (secondary).
- TE Connectivity, *Contact Arc Phenomenon* (minimum arc voltages), te.com.
- Samtec, connector plating FAQs (normal force, 30 µin gold), blog.samtec.com (secondary). Advanced Plating Technologies, *Gold vs Tin* (fretting of tin) (secondary).
- Patents: US 9,799,930; WO 2013/171813 A1; US 7,324,140 B2; US 8,282,413 B2; US 9,577,228 B2; US 7,944,174 B2; US 10,193,111 B2 (patents.google.com).
- Kenwood NX-5300 service manual B5B-7154-10 (manuals.repeater-builder.com). Icom IC-F52D specifications (icomamerica.com). Motorola XPR 7000e data sheet.
- iFixit: teardowns 24016 (Galaxy S5), 61205 (LG G5); guides 152861 (Fairphone 4), 168819 (Fairphone 5), 213287 (XCover Pro). Fairphone forum threads 104289, 95387, 107772 (user reports).
