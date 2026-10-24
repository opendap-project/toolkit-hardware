# Research: compliance regimes for portable audio devices

- **Date:** 2026-10-24
- **Status:** Desk research. Engineering input only, not legal advice and not a decision. Nothing here has been tested. Separated on 2026-10-24 from the T1's design-for-compliance research, so every OpenDAP device starts from the same catalog. Task HW3.6 of the [hardware engineering system plan](../plans/2026-10-hardware-engineering-system-plan.md).
- **Question:** what each regulatory regime requires of a portable, battery-powered audio device with radios, by product feature, so a device's own design-for-compliance work only has to say what it does, misses or contradicts.
- **Applications:** each device keeps its application in its product repository. The first is the T1: [design for compliance of the T1](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-design-for-compliance.md). Examples below name the T1 where they make a rule concrete.
- **Quality levels:** each regime carries the lowest [RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md) level at which it usually becomes mandatory (Q0 bench-safe, Q1 prototype, Q2 pre-compliance, Q3 compliant, Q4 reference). A device's application sets its own levels per item.
- **Conventions:** a standard is cited by number, edition and clause where known. **UNVERIFIED** marks what was not checked against the primary text in this pass: an edition that may have been superseded in the Official Journal, a value from a secondary source, or a value from memory. A secondary source is named as such. Arithmetic is shown as such.

## 0. Features and the regimes they bring

| Product feature | Regimes | Sections | First level |
|---|---|---|---|
| Any electronic product placed on the market | EMC emissions and immunity, ESD, product safety (IEC 62368-1), chemicals and environment, technical file | §1 | Q2 |
| Radio module (Wi-Fi, Bluetooth), pre-certified | Radio spectrum, modular approval reuse, RF exposure, radio cybersecurity | §2 | Q2 (Q3 for cybersecurity) |
| Chip-down radio (for example an NFC reader) | Its own radio authorisation | §2.4 | Q3 |
| Li-ion battery pack | IEC 62368-1 Annex M and fire classes, IEC 62133-2, UN 38.3, EU Battery Regulation | §3 | Q2 (UN 38.3), Q3 |
| Headphone output | Hearing safety (IEC 62368-1 clause 10.6, EN 50332) | §4 | Q2 |
| USB-C, USB PD | EU common charger, USB Type-C and PD conformance | §5 | Q3 |
| Accessories on a host interface (HAT-like) | Every regime above, per configuration; host and accessory responsibilities | §6 | Q3 |

| Regime | Instrument and main standards | What it forces in a device | First level |
|---|---|---|---|
| EMC, unintentional emissions and immunity | FCC 47 CFR Part 15 Subpart B (Class B, 15.109); ICES-003 Issue 7; EN 55032:2015+A11:2020 Class B; EN 55035:2017+A11:2020; EN 301 489-1/-17 under RED (editions **UNVERIFIED**) | Shielding and filter options, clock spreading, cable and flat-cable control, tested configurations | Q2 |
| Radio, spectrum | FCC Part 15C (15.247), 15E (15.407), modular approval 15.212; RED 2014/53/EU Art. 3.2 with EN 300 328 V2.2.2, EN 301 893 V2.1.1, EN 300 330 (NFC); ISED RSS-247 Issue 3, RSS-Gen Issue 5; Japan Radio Act (MIC); Korea Radio Waves Act (KC) (editions **UNVERIFIED**) | Module integration rules, listed antennas, regulatory domain handling in Linux, chip-down radios as variants | Q2 |
| RF exposure | EU 1999/519/EC limits via EN 62479:2010, EN 50663:2017, EN 50566:2017, EN IEC/IEEE 62209-1528:2021; FCC 47 CFR 1.1307(b)(3), 2.1093; ISED RSS-102 Issue 6 (**UNVERIFIED** edition) | SAR of a handheld; antenna placement; permissive change | Q2 (assessment), Q3 (test) |
| Radio cybersecurity | Delegated Regulation (EU) 2022/30 under RED Art. 3.3(d)(e)(f); EN 18031-1/-2/-3:2024 with the restrictions of Decision (EU) 2025/138 | No default credentials, secure updates, minimal exposed services, data deletion | Q3 |
| Product safety | IEC 62368-1:2018 (ed. 3), EU harmonised EN IEC 62368-1:2020+A11:2020; IEC 62368-1:2023 (ed. 4) exists, its EU citation **UNVERIFIED** | Energy source classes, Annex M batteries, touch temperatures, clause 10.6 acoustics | Q2 (pre-assessment), Q3 |
| Batteries | IEC 62133-2:2017 (+A1:2021); UN Manual of Tests and Criteria Part III 38.3; Regulation (EU) 2023/1542 Art. 11, 13, 17 | Certified pack, transport tests, user replacement with commercial tools, labelling, spare pack | Q2 (UN 38.3), Q3 |
| Hearing safety | IEC 62368-1 clause 10.6; EN 50332-1:2013, EN 50332-2:2013, EN 50332-3:2017 | Calibrated output levels, dose accounting, warnings and acknowledgement, safe default level | Q2 |
| Chemicals and environment | RoHS 2011/65/EU + (EU) 2015/863, EN IEC 63000:2018; REACH (EC) 1907/2006 Art. 33 and SCIP; WEEE 2012/19/EU, EN 50419; California Proposition 65 | Lead-free parts and assembly, declarations per BOM line, marking | Q2 (parts), Q3 (file) |
| USB and common charger | Directive (EU) 2022/2380 amending RED (Annex Ia), EN IEC 62680-1-3 (USB Type-C), EN IEC 62680-1-2 (USB PD); USB-IF compliance programme (voluntary) | USB-C receptacle, USB PD for charging above 5 V, charging-power label and pictogram | Q3 |
| Wi-Fi Alliance | Voluntary certification | Only if the logo is used | Q4 |
| ESD | IEC 61000-4-2:2008 at the EN 55035 / EN 301 489-1 levels | Protection placement, discharge paths, no acoustic transient | Q2 |
| Accessory ecosystem | Same regimes, per configuration | Tested configurations, host and accessory responsibilities, PS1 outputs | Q3 |

## 1. Every electronic product

### 1.1 EMC: FCC Part 15B, ICES-003, EN 55032 and EN 55035

A portable player for residential use is a Class B digital device.

- Radiated emissions from 30 MHz up to the frequency the highest internal clock sets: FCC 15.33 and CISPR 32 both extend the range to 6 GHz when internal frequencies exceed 1 GHz (LPDDR4X memory and a 2.4/5 GHz radio qualify; 15.33 rule **UNVERIFIED** in detail).
- Conducted emissions apply to AC mains ports. A battery device charged over USB-C is tested on mains only through its charger, which is not part of the device when it ships without one (**UNVERIFIED** whether a lab tests with a representative charger in the EU).
- Immunity (EN 55035): ESD (§1.2), radiated RF immunity 80 MHz–6 GHz at 3 V/m, and the audio-specific criterion: the acoustic output during immunity tests is judged against a demodulated-interference limit for audio functions (EN 55035 Annex for audio; value **UNVERIFIED**).
- Radio equipment adds EN 301 489-1/-17 under RED, with the same ESD and RF immunity levels and radio-specific performance criteria.
- FCC: Supplier's Declaration of Conformity for the host, with the compliance statement in the manual or e-label (47 CFR 2.1077, 15.19, 15.105). ISED: ICES-003 compliance label.

**Margins experienced teams keep.** Pre-scans in a non-accredited setup carry several dB of uncertainty (antenna factors, site, cables), so a pre-scan peak at least 6 dB under the Class B limit is the usual go criterion (secondary, common practice; **UNVERIFIED** as a figure from a standard). Formal results with less than about 3 dB margin are treated as a production-spread risk.

**Design levers.**

- **Fix options without a respin.** EMC fixes found at pre-scan usually need footprints that are already there: common-mode filter positions (0 Ω by default) on the external high-speed pairs and the front-module and accessory interfaces; ferrite positions on accessory and front-module supplies; shield-can frames around switching converters near the radio and around the headphone stage.
- **Clock spreading.** Spread-spectrum on memory and display clocks is a software and device-tree setting where the SoC supports it; its effect on audio is nil when the DAC is the clock master. It needs a measured on/off comparison.
- **Tested configurations.** ANSI C63.4 and CISPR 32 test the equipment with its ports exercised by typical peripherals: for a player with accessories, at least no accessory, a representative accessory, charging over USB-C, USB device mode to a computer, headphones on each jack, and the radios active (§6).

### 1.2 ESD: IEC 61000-4-2

- **Levels.** EN 55035 and EN 301 489-1 test the enclosure port at ±4 kV contact and ±8 kV air (IEC 61000-4-2:2008 levels 2 and 3), performance criterion B: temporary degradation, self-recovery, no loss of stored data (levels **UNVERIFIED** against the current editions). Experienced teams pre-test handhelds at IEC 61000-4-2 level 4 (±8 kV contact, ±15 kV air) for margin (Q4).
- **Discharge points** of a handheld player: USB-C shell, jack sleeves, button caps, the display cover-glass gap, case seams, card slots, and any accessory contact field that is user-touchable when no accessory is fitted.
- **Discharge current path:** in a plastic case, connector shells and ESD diode returns need a short, low-inductance path to the ground plane.
- **Audio criterion:** an ESD event must not produce a loud transient at the headphones (acoustic shock).

### 1.3 Product safety: IEC 62368-1

**Energy source classes (IEC 62368-1:2018).**

- **Electrical (clause 5):** a USB-powered player with rails below the ES1 limits needs no basic safeguard against electric shock (for the T1, every voltage is ES1: USB PD at 9 V maximum, a 2S battery, amplifier rails ±7 V).
- **Fire (clause 6):** power sources are classed by the power available after 3 s into a worst-case load: PS1 ≤ 15 W, PS2 ≤ 100 W, PS3 above. A pack protection circuit (PCM) that trips at a known current bounds the battery circuit's class if the PCM is a reliable limiter (**UNVERIFIED** whether a PCM qualifies; otherwise PS3). PS2 circuits need V-1 or better materials near potential ignition sources, or the clearances of clause 6.4. The fab's evidence that the laminate is UL-recognised is part of the file.
- **Outputs to accessories:** an output that stays ≤ 15 W after 3 s under a single fault (its limiter shorted) is PS1 and frees every accessory from fire-enclosure evaluation for power drawn from the host. A second, independent limiter per output (a fuse or a PTC sized to open within 3 s at the upstream converter's limit) keeps it PS1 (§6).
- **Thermal (clause 9):** accessible surfaces stay within the TS1 limits of IEC 62368-1 Table 38, which depend on material and contact time; a surface held continuously for long periods is limited to about 43 °C for any material (**UNVERIFIED** value and row). The worst case combines charging, full-scale headphone output, accessories at their full budget and radio transmission.
- **Acoustics (clause 10.6):** §4.
- **Coin cells:** the coin-cell rules (IEC 62368-1 4.8; US 16 CFR 1263) apply only if the BOM has one.

**Documentation.** A CB test report and certificate (IECEE CB scheme) is the usual evidence, reusable across markets; the hazard-based safeguard analysis (energy sources, safeguards, single faults) goes in the technical file. The analysis has to show that no safety function depends on software alone.

### 1.4 Chemicals and environment

- **RoHS** (2011/65/EU, Annex II as amended by (EU) 2015/863): 10 restricted substances, 0.1 % by weight per homogeneous material (cadmium 0.01 %). Exemptions such as high-melting solder or lead in glass and ceramic parts have expiry dates (**UNVERIFIED** status per exemption). Technical documentation per EN IEC 63000:2018: supplier declarations or test reports per part. In practice: RoHS-compliant parts, lead-free assembly and a lead-free finish on every build that leaves the lab (Q2); a declaration per BOM line in the technical file (Q3), carried by a compliance field per BOM line.
- **REACH:** substances of very high concern above 0.1 % w/w per article trigger the Art. 33 information duty and a SCIP notification (Waste Framework Directive 2008/98/EC Art. 9(1)(i)). Typical carriers: cable insulation, rubber parts, gaskets. The Annex XVII restrictions to check are PAHs in rubber or plastic parts in skin contact (entry 50: buttons, gaskets) and nickel release from metal parts in prolonged skin contact (entry 27) (**UNVERIFIED** entry numbers).
- **WEEE** (2012/19/EU): crossed-out wheeled-bin mark per EN 50419 on the product, and on the pack under the Battery Regulation.
- **California Proposition 65:** a warning is needed if a listed chemical is present above the safe harbour (for example lead in brass jack contacts or DEHP in cables); suppliers' declarations decide it (**UNVERIFIED** per part).

### 1.5 Technical file and declarations (Q3)

- **General description and variants:** models, assembly variants, declared configurations (front modules, accessories), software version assessed.
- **Standards applied**, with editions.
- **Test reports:** EMC, radio (conducted from the module maker plus radiated from the device), SAR; IEC 62368-1 CB with Annex M and clause 10.6; EN 50332 measurements per output; EN 18031 assessment; USB PD pre-tests; pack IEC 62133-2 and UN 38.3.
- **Risk analyses:** IEC 62368-1 energy sources and safeguards; hearing-safety function; cybersecurity assets and threats.
- **Declarations:** EU declaration of conformity under RED (with RoHS and the Battery Regulation for the pack); FCC SDoC for the host, with the module's FCC ID on the label; ISED and ICES-003 statements; Japan and Korea marks where declared.
- **Labels and e-label:** FCC ID, IC, Japanese mark and number; CE; WEEE bin; battery marks; charging-power label and pictogram. A regulatory-information screen on the device serves the e-label where each authority allows it (**UNVERIFIED** per authority).
- **User information:** safety and hearing warnings, battery replacement procedure, RF exposure statement, the 5 GHz indoor-only restriction.
- **Supplier declarations:** RoHS, REACH and Proposition 65 per BOM line; the module's grants and reports; the pack's reports.

### 1.6 Kits

The regimes apply to a product placed on the market, kits included: 47 CFR 15.23 does not exempt marketed kits, and the EU treats a kit as a product. The quality levels set engineering gates; the market status of each edition is a maintainers' decision.

## 2. Radio module

### 2.1 Modular approval reuse (US, Canada)

47 CFR 15.212 lets a host carry a module's grant if the module is used within its grant conditions: the listed antennas (type and gain no higher), the trace design for a limited approval, and the RF exposure conditions. The host then needs only the "Contains FCC ID: …" label, a Part 15B SDoC and a check of co-located transmitters (FCC KDB 996369 is the integration guidance, number **UNVERIFIED**). A change outside the grant is a permissive change filed by the grantee (the module maker): Class I for an equivalent antenna of the same or lower gain, Class II for a new RF exposure condition. ISED follows the same pattern with "Contains IC: …" and Class 4 changes.

What a host checks against the module's certification documents: the use condition the grant covers (mobile at ≥ 20 cm, or portable), the listed antennas and cable lengths per region, the RF trace copy rules for the host board, and how the certified TX-power tables reach the driver the host ships. For the Murata Type 2EL these are in Murata CER-0248 and E2B-09-1413 (the T1's application has the table).

### 2.2 EU (RED)

There is no modular grant. A module maker may provide conducted test reports; radiated measurements and the declaration of conformity are the product maker's. Points that touch the host's design and software:

- **Adaptivity and receiver category (EN 300 328 V2.2.2, EN 301 893 V2.1.1):** they are properties of the module firmware; the host must ship the firmware the module maker tested with, or retest.
- **DFS and indoor-only bands at 5 GHz:** the 5150–5350 MHz band is indoor-only in the EU, and a device acting as an access point on DFS channels must detect radar. A general-purpose Linux device can be put in access-point mode, so the OS has to restrict access-point channels to what the module is certified for. The indoor-only restriction is stated on the packaging and in the manual (RED Art. 10(10)).
- **Regulatory domain:** Linux `cfg80211` with the wireless regulatory database sets the allowed channels and power per country. The country is a setting of the device, not of the user's network, and must not be set to a less restrictive domain than where the device is.

### 2.3 Other markets

- **Canada.** RSS-247 Issue 3 for 2.4 and 5 GHz, RSS-Gen Issue 5 for labelling and receiver rules, ICES-003 for the host (**UNVERIFIED** editions). The bilingual RSS-Gen statement goes in the manual or e-label.
- **Japan.** The Radio Act requires the technical conformity mark with the module's certification number, and the module used within its certification conditions (antenna and cable as registered). VCCI is voluntary. Whether the mark may be shown only on screen is **UNVERIFIED**.
- **Korea.** KC under the Radio Waves Act: radio conformity, KC EMC (KS C 9832 and KS C 9835, the CISPR 32/35 equivalents) and the KC battery scheme. Whether a module's KC certificate removes the host's radio tests is **UNVERIFIED**; plan for host testing.

### 2.4 Other radios in a module or on the board

- **A radio present in the module but not wired** (for example IEEE 802.15.4) stays disabled in firmware, so it adds no co-location case. Whether the module's grants cover it matters only if a later board wires it.
- **Passive NFC tag.** Powered by the reader's field. Whether a passive tag in a host is radio equipment under RED is **UNVERIFIED**; it emits nothing by itself.
- **Chip-down NFC reader** (13.56 MHz) has no pre-certification. Fitted, it needs its own authorisation: FCC 15.225 (certification), EN 300 330 and EN 301 489-3 under RED, ISED RSS-210 (**UNVERIFIED** annex), and the Japanese and Korean equivalents. As a population option, a certified variant can leave it unfitted.

### 2.5 RF exposure

**FCC.** A handheld player is a portable device (47 CFR 2.1093: used within 20 cm of the body). A portable device is exempt from SAR evaluation only below the threshold of 47 CFR 1.1307(b)(3)(i): 1 mW at any distance, or Pth from the formula of 1.1307(b)(3)(i)(B) (transcribed here, **UNVERIFIED** against the eCFR text in this pass):

- Pth = ERP20cm × (d / 20 cm)^x, with x = −log10(60 / (ERP20cm × √f)), f in GHz, ERP20cm = 3060 mW for 1.5–6 GHz, d ≥ 0.5 cm.
- At 2.45 GHz and d = 0.5 cm (arithmetic): √f = 1.565; x = −log10(60 / 4,790) = 1.90; Pth = 3060 × 0.025^1.90 ≈ **2.7 mW**.
- At 5.5 GHz and d = 0.5 cm (arithmetic): √f = 2.345; x = −log10(60 / 7,177) = 2.08; Pth = 3060 × 0.025^2.08 ≈ **1.4 mW**.

Wi-Fi and Bluetooth modules transmit tens of milliwatts conducted, so a handheld with one needs SAR testing. Limits: 1.6 W/kg over 1 g for the body, 4 W/kg over 10 g for extremities (2.1093(d)). A player in a pocket during playback is a body-worn case; a player in the hand is an extremity case.

**EU.** EN 62479:2010 exempts equipment below a low-power level (20 mW average for the general public, **UNVERIFIED** value). EN 50663:2017 is the generic assessment and EN 50566:2017 the product standard for hand-held and body-mounted devices, with SAR measured per EN IEC/IEEE 62209-1528:2021. The basic restrictions of Council Recommendation 1999/519/EC are 2 W/kg over 10 g for head and trunk and 4 W/kg for limbs.

**Canada.** RSS-102 has its own exemption thresholds, different from the FCC's (**UNVERIFIED** values for Issue 6).

**Design levers.**

- Antenna position: at the edges or the top of the device, away from the surface the hand and the body touch, and away from accessory metal. The case and front module set the distance; it should be fixed with a SAR pre-assessment before the case freezes.
- Simultaneous transmission: with dedicated antennas per radio, Wi-Fi and Bluetooth transmit at once; the SAR sum or a separation ratio is evaluated.
- Time-averaged power: SAR is assessed at the maximum time-averaged power the software allows. A per-band power back-off is a lever where the driver supports it.

### 2.6 Radio cybersecurity: RED delegated act and EN 18031

Delegated Regulation (EU) 2022/30 applies since 1 Aug 2025 to radio equipment that can communicate over the internet. EN 18031-1 covers network protection (Art. 3.3(d)) and EN 18031-2 personal data (Art. 3.3(e)). EN 18031-3 covers monetary transactions (Art. 3.3(f)) and becomes relevant if an on-device purchase is enabled. Decision (EU) 2025/138 cites them with restrictions: a design that allows no password at all cannot rely on the default-password clauses, and the presumption of conformity is lost for those points.

Themes a device answers: no default or shared credentials (developer modes and SSH included); minimal exposed services, with a port audit on the release image; secure, signed updates and the update chain described in the technical file; key storage; logging and a factory reset that deletes personal data; an asset and threat inventory. The UK PSTI regime and the EU Cyber Resilience Act cover the same ground with their own documents (support period, vulnerability contact).

## 3. Li-ion battery pack

### 3.1 IEC 62368-1 Annex M

Charging stays inside the cell's specified voltage, current and temperature window, also under a single fault (M.4, **UNVERIFIED** clause numbers in ed. 3). Typical safeguards that work without the OS: the pack PCM (over-charge, over-discharge, over-current, short circuit, balancing); charger thermal regulation and a TS window on the pack NTC; a board fuse; per-cell monitoring; a keyed connector that prevents reverse insertion and a wrong cell count. The hazard analysis states that software is not a safeguard, and shows that a corrupted charger register (a single fault) is caught by hardware. User replacement of the pack adds the IEC 62368-1 marking for replaceable batteries (risk of fire if replaced by an incorrect type) and the requirement that the replacement is safe for an ordinary person.

### 3.2 Pack regimes

| Item | Requirement |
|---|---|
| IEC 62133-2:2017 (+A1:2021) | Cell and pack safety tests |
| UN 38.3 | Transport tests, test summary available down the supply chain; air transport per IATA PI 966/967. Due as soon as units or kits ship (Q2) |
| Regulation (EU) 2023/1542 Art. 11 | From 18 Feb 2027: portable batteries removable and replaceable by the end user with commercially available tools (or tools supplied free), no heat or solvents, instructions provided, battery available as a spare part for the period the guidelines set (Commission guidelines C/2025/214; details **UNVERIFIED**) |
| Art. 13 labelling | General information label (from 18 Aug 2026), capacity label, crossed-out bin, QR code (from 18 Feb 2027) (**UNVERIFIED** dates for each item) |
| CE marking of the battery | A pack placed on the market as a spare is itself a product under the Regulation (DoC, technical documentation) (**UNVERIFIED** module) |
| Battery passport (Art. 77) | Light means of transport, industrial over 2 kWh and EV batteries only: not applicable to a portable battery |
| Japan | J62133-2 for the battery under the electrical appliance safety law (PSE) (**UNVERIFIED** category for a pack sold inside a host vs as a spare); Q3 if Japan is declared |

## 4. Headphone output

### 4.1 Scope

IEC 62368-1 clause 10.6 covers personal music players: portable, intended for ordinary persons, mainly for listening with headphones or earphones. A loudspeaker output is out of scope. A line-level output that is not intended for headphones is outside it as well (**UNVERIFIED** reading).

### 4.2 Two routes

1. **Classification route** (IEC 62368-1 10.6.2, EN 50332-1 and EN 50332-2):
   - by default the output stays at RS1: 85 dB(A), or 27 mV wide-band voltage for a player sold without headphones;
   - the listener may go up to RS2 (100 dB(A), 150 mV) after acknowledging a warning;
   - the warning returns after about 20 h of listening above RS1;
   - RS2 is a ceiling.

   Values from secondary sources (150 mV corroborated by a manufacturer's user guide; 27 mV and the 20 h re-warning **UNVERIFIED** against the standard text). Sony's EU and Korean players and Android's safe-media-volume behave this way (secondary, [T1 community mods research](https://github.com/opendap-project/t1/blob/main/docs/research/ux/2026-10-community-mods-customisation.md)).
2. **Dose-based route** (IEC 62368-1:2018 10.6.3 and EN 50332-3:2017; the EU harmonised EN IEC 62368-1:2020+A11:2020 amends clauses 3.3.19 and 10.6 with the momentary exposure level and the calculated sound dose, secondary: standards catalogue listing):
   - the player integrates the momentary exposure level (MEL) into a calculated sound dose (CSD) over a rolling 7-day window, where 100 % corresponds to 80 dB(A) for 40 h a week;
   - it warns at 100 % CSD and at every further 100 %;
   - it warns each time the MEL exceeds RS2 (100 dB(A));
   - if the listener does not acknowledge, it lowers the level to RS1.

   Android's sound-dose framework implements this route and states those rules: warning on each 100 % of CSD, reduction to RS1 if unacknowledged, a momentary warning above RS2 = 100 dB(A), and the rolling 7-day window (secondary: [AOSP sound dose](https://source.android.com/docs/core/audio/sound-dose)). Whether the dose route alone is enough in the EU, with no RS2 ceiling, is **UNVERIFIED** against the A11 text and is the first question for a test lab.

EN 50332-2 measures with programme-simulation noise (IEC 60268-1), whose level at full scale is lower than a sine's, so the measured wide-band voltage is below a sine figure (by how much is **UNVERIFIED** until measured). A high-output player sits 20 dB or more above the 150 mV RS2 voltage (the T1's figures are in its application).

### 4.3 How compliant players handle it

Observed practice (secondary): a default safe level; a warning dialog the listener acknowledges to go above it; the warning re-armed after cumulative listening; in some EU and Korean variants, a lower maximum. A permanent lower maximum caps the hardware; the warning-and-acknowledgement pattern does not.

### 4.4 Hardware and software consequences

- Amplifier enables default to disabled at reset and the DAC powers up muted, so a crashed or absent OS can never drive a loud output.
- No ESD or power event may produce an acoustic transient at the jack (§1.2).
- Dose metering can be passive: it reads the signal and the volume and acts only on the volume, so bit-perfect playback is untouched.
- A safety function in open software that owners can modify: the technical file states that the shipped configuration is the one assessed.
- Bluetooth output to wireless headphones: the dose then belongs to the listening device's own compliance (**UNVERIFIED**); the player can still meter it.

## 5. USB-C, USB PD and the EU common charger

**Directive (EU) 2022/2380** (amending RED, applicable since 28 Dec 2024 for the categories listed, which include portable audio and handheld devices; scope reading **UNVERIFIED** for a DAP):

- a USB Type-C receptacle per EN IEC 62680-1-3;
- if charging needs more than 5 V, more than 3 A or more than 15 W, USB PD per EN IEC 62680-1-2, and full charging speed with any compliant charger;
- the product offered without a charger, with the pictogram showing whether a charger is included;
- a label with the minimum and maximum charging power the device needs, and "USB PD" when it supports it; the minimum is the power that still charges at full speed, measured.

**Engineering points.**

- When the PD sink is negotiated by the OS, the device must still charge from a 5 V Type-C source with the OS not running (dead battery, early boot): dead-battery Rd and a charger that runs from 5 V.
- **Source role:** a device that sources power pre-tests the Type-C source rules (vSafe0V before attach, Rp advertisement, no back-feed).
- **USB-IF certification and logos** are voluntary. Certification requires the USB-IF compliance tests (Type-C functional, PD) at an authorised lab; the logos may be used only after it. Plain technical names in text are a separate question (**UNVERIFIED** USB-IF trademark rules).

## 6. Accessories on a host interface (HAT-like)

- **Each accessory is its own product.** It carries its own declaration, tests and marks. A radio accessory is its own radio equipment, and the host's grants never cover it.
- **The host is certified in declared configurations.** The technical file lists the configurations tested: without an accessory, and with a representative accessory exercising the interface (high-speed links and power at its class). EMC and SAR are tested with the worst-case representative accessory (metal near the antennas). An accessory not in the list does not void the host's own compliance. It does make the combination the user's assembly, and the accessory maker carries the accessory's compliance in that combination.
- **Host responsibilities:**
  - PS1 outputs under a single fault (§1.3), so accessories need no fire enclosure for power drawn from the host;
  - ESD at the contact field;
  - an accessory ID, so the software knows what is attached and can apply an accessory's declared limits;
  - published EMC conditions for accessory makers (emission budget at the cable, shielding of high-speed lines).
- **Accessory responsibilities:**
  - an accessory that sources power to the host meets the host's input limits;
  - an accessory with a battery carries its own battery compliance (§3);
  - a radio accessory carries its own radio and RF-exposure compliance;
  - an accessory keeps the host's antenna keep-out.

## 7. Open items

1. EU: whether EN IEC 62368-1:2020+A11:2020 accepts the dose-based route without an RS2 ceiling. First question for the test lab, with the A11 text in hand.
2. EN 50332-2 measurement details (programme-noise level relative to full scale) and the exact 27 mV and 20 h figures.
3. The FCC 1.1307(b)(3) formula transcription and the RSS-102 Issue 6 thresholds, checked against the primary texts.
4. Whether a pack PCM qualifies as the PS2 limiter.
5. Japan e-label acceptance and the KC host-testing rule.
6. Directive 2022/2380 scope reading for a DAP (expected in scope as a portable audio device with radio).

## Sources

- 47 CFR 1.1307 and 2.1093: <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-1/subpart-I/section-1.1307>, <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-2/subpart-J/subject-group-ECFR52efa600149ef42/section-2.1093>; secondary summary of the 2021 exemption rules: [Nemko](https://www.nemko.com/blog/understanding-rule-changes-for-human-exposure-to-radiofrequency-electromagnetic-fields)
- 47 CFR 15.23 (kits): <https://www.ecfr.gov/current/title-47/chapter-I/subchapter-A/part-15/subpart-A/section-15.23>
- Decision (EU) 2025/138 (EN 18031 citation and restrictions): <https://eur-lex.europa.eu/eli/dec_impl/2025/138/oj/eng>
- Commission guidelines on Battery Regulation Art. 11, C/2025/214: <https://eur-lex.europa.eu/eli/C/2025/214/oj/eng>
- Directive (EU) 2022/2380: <https://eur-lex.europa.eu/eli/dir/2022/2380/oj/eng>
- EN 50332-3:2017 scope (secondary, catalogue): <https://iteh.es/catalog/standards/sist/669af6ab-ca37-4ab1-a336-def08543a43b/sist-en-50332-3-2017>; EN IEC 62368-1:2020/A11:2020 scope (secondary, catalogue): <https://iteh.es/catalog/standards/sist/7f899651-a0c1-4092-a0d2-34161ce557d8/sist-en-iec-62368-1-2020-a11-2020>
- AOSP sound dose (secondary, an implementation of IEC 62368-1 ed. 3 and EN 50332-3): <https://source.android.com/docs/core/audio/sound-dose>
- 150 mV wide-band limit (secondary, a manufacturer's user guide citing EN 50332-2): <https://download.lenovo.com/pccbbs/pubs/t490/html_en/en/Using_headphones_or_earphones.html>
