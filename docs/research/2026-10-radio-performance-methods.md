# Research: measuring and benchmarking the radio performance of an OpenDAP device

- **Date:** 2026-10-24
- **Status:** Desk research and a proposed method. Not a decision; nothing here has been measured yet. Each device keeps its application, its benchmark results and its targets in its own repository. The first application is the T1: [radio performance of the T1](https://github.com/opendap-project/t1/blob/main/docs/research/2026-10-radio-performance-t1.md).
- **Question (maintainers, 2026-10-24):** OpenDAP devices should have radios that compete with, and beat, commercial devices that degrade quickly with distance or walls. Transmit power is capped by spectrum law, so the advantage has to come from engineering. This note gives the reusable part: what limits a handheld device's radio links, how to compare a device against a benchmark set, and how to measure range, throughput and latency so that every claim is reproducible at integration levels L4–L6 of the [integration and verification method](../specs/integration-and-verification.md).
- **Quality levels:** rows carry the lowest [RFC 0010](https://github.com/opendap-project/rfcs/blob/main/text/0010-quality-levels.md) level at which they become mandatory. Experience thresholds follow the three-threshold rule (ideal, warning, hard limit) that each device maps onto Q2–Q4.
- **Conventions:** **UNVERIFIED** marks a value not checked against a primary source in this pass. "(vendor claim)" marks a value whose only source is the maker. "(secondary)" names a source that reports someone else's figure. Arithmetic is shown as such. Test tools are named as instruments, not as a product software stack.

## 0. Summary

1. **The link budget decides range, and most of it is not transmit power.** Regulators cap transmit power; antenna efficiency, body and hand loss, receiver sensitivity, self-interference (desense), coexistence airtime and codec adaptation are each worth several dB and are the device maker's to win. In a measured handheld, losses in the built-in antenna dominated, up to 99 % total loss for one smartphone user, and the authors note that a better antenna would bring total losses below 50 % (Andersen, Nielsen, Pedersen 2016, §2.3).
2. **Every dB is distance.** Indoors, with ITU-R P.1238's distance coefficient N = 28–30 at 2.4 GHz, 6 dB of link budget is about 1.6× the range and 3 dB about 1.3×; in free space 6 dB doubles it (arithmetic, §1.2).
3. **Public numbers are thin.** Digital Audio Player makers do not publish Bluetooth range or output power on their specification pages (Sony NW-ZX707, FiiO M23 checked), and reviewers report range anecdotally. The only way to "beat the benchmark" verifiably is to measure a benchmark set with the same method (§3).
4. **The method has three tiers:** conducted and shielded-box measurements that are cheap and repeatable (relative comparisons, attenuation to failure), over-the-air measurements of total radiated power, sensitivity and efficiency in a lab (absolute antenna performance, with phantoms), and field courses with calibrated walls and real bodies (the experience the listener has) (§4–§6).
5. **Results are relative and absolute.** Each target is stated twice: an absolute value (Draft until calibrated on a prototype) and a ratio to the benchmark median under the same conditions. A device beats the benchmark only when both hold (§7).

## 1. What limits a handheld radio link

### 1.1 The link budget

For one direction of a link, the received power is:

`P_rx = P_tx(conducted) + G_tx(antenna, realised, in situ) − L_body − L_path − L_walls + G_rx − L_rx(desense)`

and the link holds while `P_rx ≥ S_rx(rate) + M_fade`, where `S_rx(rate)` is the sensitivity of the receiver at the modulation in use and `M_fade` a margin for multipath fading and interference.

| Term | Who controls it | Typical size | Source |
|---|---|---|---|
| Conducted transmit power | Regulation (per market) and the certified module's power table | Bluetooth: −20 to +20 dBm allowed by the specification; regional and certification caps are lower | [Bluetooth SIG, range](https://www.bluetooth.com/learn-about-bluetooth/key-attributes/range/); 47 CFR 15.247(b); ETSI EN 300 328 (§2) |
| Antenna realised gain in the device | Device maker: antenna choice, placement, keep-out, enclosure, matching | Bluetooth devices span −10 to +10 dBi (Bluetooth SIG); small built-in antennas often lose more than half the power (Andersen 2016) | Same |
| Body and hand loss | Device maker (placement relative to the grip and the pocket) and the user | Mean 3–10 dB by antenna type at 1.89 GHz, up to 10 dB spread between users (Nielsen 2001); a phone in a pocket shows 15–20 dB swings with body orientation at 2.4 GHz (Leith 2020) | §8 |
| Path and walls | The environment | Free space at 2.44 GHz and 1 m: 40.2 dB (arithmetic); a plasterboard stud wall: little; a 15 cm blockwork wall: about 20 dB at 2.4 GHz (Leith 2020) | §8 |
| Receiver sensitivity | Radio chip and module; device noise (desense) | Specification minimum −70 dBm; practical BR −94 to −95 dBm, 3-DH5 −88 to −89 dBm, LE Coded −104 to −107 dBm (module datasheets) | Bluetooth SIG; Murata E2B-09-1413 Table 16; Ezurio MT320 datasheet |
| Desense | Device maker: layout, switching regulators, DDR and SDIO harmonics, display | One dB of noise rise in the channel is one dB of sensitivity lost | Arithmetic |
| Coexistence | Device maker: shared or dedicated antennas, PTA configuration, band steering | Bluetooth and 2.4 GHz Wi-Fi on one antenna share airtime | §1.4 |
| Codec and link adaptation | Software | LDAC steps 990 → 660 → 330 kb/s; the step trades fidelity for margin | §1.4 |

The other end of the link matters as much. In Bluetooth audio the device is the source, and the headphones transmit acknowledgements and their own packets at low power (for example a FiiO headphone at 2.3 mW peak conducted, FCC ID R56-FC4002 (secondary, fccid.io)). The device can improve the reverse link only through its receive side: antenna efficiency, body loss and sensitivity count twice, transmit power counts once.

### 1.2 Range per dB

ITU-R P.1238 models indoor loss as `L = 20 log10 f(MHz) + N log10 d(m) + L_f(n) − 28` dB, with N ≈ 28 for residential and 30 for office at 1.8–2.0 GHz and N ≈ 28–30 at 5.2 GHz (values from the IEEE 802.15 overview of ITU-R P.1238, secondary; edition **UNVERIFIED**). With N = 28 a change of Δ dB moves the range by 10^(Δ/28): +3 dB → 1.28×, +6 dB → 1.64×, +10 dB → 2.27×. In free space (N = 20) +6 dB → 2.0× (arithmetic).

### 1.3 Diversity

With two antenna branches in Rayleigh fading, selection combining needs about 10 dB less mean signal than one branch for the same 1 % outage (arithmetic: one branch, P_out = 1 − e^(−x) = 0.01 → x = 0.0101; two branches, (1 − e^(−x))² = 0.01 → x = 0.105; ratio 10.2 dB). Maximal-ratio combining (2×2 Wi-Fi receivers) does slightly better. Real gains are smaller when the branches are correlated (close antennas, same polarisation) or unbalanced (one antenna under the hand), so diversity is measured, never assumed. Classic Bluetooth controllers generally have one RF path; diversity for Bluetooth then comes only from antenna placement, not from combining.

### 1.4 Airtime and codecs

A2DP streams fill a share of the Bluetooth airtime that grows with bitrate. With 3-DH5 packets (1021-byte payload, five slots plus one return slot) LDAC at 990 kb/s needs about 121 packets per second, 45 % of the airtime, leaving at most 1.2 retransmissions per packet; with 2-DH5 (679 bytes) it needs 68 % and leaves 0.46. LDAC 660 with 3-DH5 needs 30 %, LDAC 330 or SBC at 328 kb/s with 2-DH5 about 23 % (arithmetic; payload sizes from the Bluetooth Core Specification, Vol 2, Part B, **UNVERIFIED** against the text in this pass; L2CAP, AVDTP and media headers ignored). The highest bitrates therefore have little room for retransmissions, and any airtime taken by Wi-Fi on a shared antenna comes out of that room.

SoundGuys measured received signal strength at the headphones and states that "a Received Signal Strength Indication (RSSI) of higher than −60dBm guarantees real-time high bandwidth data transfer, −70dBm requires a lower bandwidth, and a connection weaker than −80dBm isn't enough for real-time data", with LDAC 990 and 660 at risk "just below −60dBm" and 330 kb/s and the standard codecs dropping packets around −80 dBm (R. Triggs, SoundGuys, 2025-10-01). The roughly 20 dB between the two thresholds is why adaptive codecs hold a link far beyond where the top bitrate fails.

| Codec | Bitrates | Loss behaviour | Source |
|---|---|---|---|
| LDAC | 990, 660, 330 kb/s; adaptive mode steps between them | Higher steps need stronger links (above) | SoundGuys 2025 (secondary for Sony's figures) |
| aptX Adaptive | 279–420 kb/s in versions up to 2.0; up to about 1.2 Mb/s for lossless in later versions; latency below about 90 ms claimed | Adapts bitrate to the link | Qualcomm (vendor claim, via secondary sources) |
| LC3 (LE Audio) | 16–320 kb/s per channel, 7.5 and 10 ms frames | Packet-loss concealment; isochronous channels with a set number of retransmissions | Bluetooth SIG and ST material (secondary) |

## 2. Spectrum-law caps

The device's own lever is engineering, but each market sets a ceiling and each certified module sets its own table below that ceiling.

| Market | Bluetooth limit | Notes | Source |
|---|---|---|---|
| USA (FCC) | Frequency hopping with ≥ 75 channels: 1 W peak conducted; other hopping systems in 2400–2483.5 MHz (for example adaptive hopping on fewer channels): 0.125 W; digital modulation (LE): 1 W; reduce by the antenna's directional gain above 6 dBi | Band edges and restricted bands limit the outer channels in practice | 47 CFR 15.247(b)(1), (b)(3), (b)(4), eCFR read 2026-10-24 |
| EU | 20 dBm EIRP; adaptivity and medium-utilisation requirements apply above 10 dBm EIRP | Equipment at or below 10 dBm EIRP is exempt from the adaptivity tests | ETSI EN 300 328 V2.2.2 (secondary: Silicon Labs and test-lab summaries) |
| Japan | Power spectral density 10 mW/MHz in 2400–2427 and 2470.75–2483.5 MHz, 3 mW/MHz in 2427–2470.75 MHz | Values for the T66 class; **UNVERIFIED** against ARIB STD-T66 itself | ib-lenhardt summary of ARIB STD-T66 (secondary) |
| All | RF exposure: the time-averaged power of a body-worn handheld is assessed by SAR; the shipped cap equals the tested one | See the compliance catalog §2.5 | [Compliance regimes](2026-10-compliance-regimes.md) |

Two consequences for any OpenDAP device:

- A module's table can differ by modulation as much as by market. Murata's Type 2EL, for example, is certified at 13 ± 3 dBm for Bluetooth BR and LE but 5 ± 3 dBm for EDR under the FCC, and at 3 ± 3 and 0 ± 3 dBm in the EU (CER-0248 Tables 9, 41). Codecs that ride on EDR (LDAC at 660 and 990 kb/s) then have less transmit power than LE Audio on the LE PHY; the benchmark records which modulation each row used.
- A module's certified table can sit well below the market ceiling. Where the device's own declaration is allowed (EU self-declaration), a regional variant can test at a higher setting, with its own conducted reports, instead of reusing the module maker's. Where the route is the module's grant (FCC, ISED, Japan), the table is fixed by the grant and a change goes through the module maker.
- The software selects the certified table from variant data and shows the limit to the user, as the product rules require (limits only for safety or spectrum law, documented and visible).

## 3. Benchmark protocol

### 3.1 The benchmark set

- **Devices:** at least three current Digital Audio Players across price tiers of the target segment, and two current phones as a reference (one each from the two main mobile platforms). Record model, firmware, radio chip where known, body material, and date.
- **Headphones:** at least two reference sinks used for every device: one over-ear headphone and one true-wireless earbud pair, both supporting the codecs under test. Record firmware. The same units are used for every device, so the sink's own link budget cancels in the comparison.
- **Access point:** one reference Wi-Fi 6 access point (2×2 or better), fixed firmware, fixed channel and width per test, no other clients; a wired iperf3 endpoint.
- **Freshness:** a benchmark result is dated; it is repeated when the set changes or once per product generation.

### 3.2 What is reported for each benchmark device

The same rows as for the device under test (§4–§6), with the median and the worst of the runs. The benchmark median per row is the reference for the relative targets (§7).

### 3.3 What public sources give today

| Kind | What it gives | Example |
|---|---|---|
| Headphone-side RSSI and codec behaviour | Signal thresholds per LDAC step, phone bitrate defaults | SoundGuys LDAC guide (2025) |
| Latency measurement | Relative latency by loopback, per codec | RTINGS headphone latency test (method only; values per product page) |
| Phone Bluetooth latency | Android averages: SBC 308 ms, aptX 316 ms, LDAC 324 ms, AAC 369 ms over four phones | [SoundGuys](https://www.soundguys.com/android-bluetooth-latency-22732/) (date not recorded on the page read) |
| Body and pocket effects | Pocket, orientation and wall effects on 2.4 GHz handsets | Leith and Farrell 2020 |
| Phone Wi-Fi at range | Galaxy S10e 160 Mb/s average, iPhone Xs 150 Mb/s at 50 ft (15 m) through walls with a Wi-Fi 6 access point | [Keenan Systems](https://www.keenansystems.com/wordpress/2019/08/06/wi-fi-6-client-range-testing/), 2019-08-06 |
| DAP range | Anecdotes only ("quite good" range); no distances, no output power on specification pages | iBasso DX180 review (Mobile Audiophile, 2024-09-07); Sony NW-ZX707 help guide; FiiO M23 specifications |

## 4. Tier 1: conducted and shielded-box measurements (L2, L4)

Cheap, repeatable and good for comparing variants and devices. They miss body effects and give relative, not absolute, antenna figures.

| ID | Measurement | Setup | Output | Level |
|---|---|---|---|---|
| RM-C1 | Conducted transmit power per band, mode and channel | Module RF port (U.FL) to a power meter or spectrum analyser through a calibrated cable | dBm against the certified table | Q1 |
| RM-C2 | Conducted sensitivity | Bluetooth RF tester (BER or PER at the specification's test conditions) and a Wi-Fi signal source or a reference access point through a step attenuator; PER ≤ 10 % for Wi-Fi | dBm per rate against the module datasheet | Q1 |
| RM-C3 | Desense | RM-C2 repeated with every other domain active (display, DDR load, charging, audio playback, HAT) | dB lost per band; budget per device | Q1 |
| RM-B1 | Attenuation to failure, Bluetooth audio | Device and reference sink in two RF-shielded boxes, coupled by antennas or probes through a programmable attenuator; stream a test signal; raise attenuation in 1 dB steps, 60 s per step | Attenuation (dB) at which the first dropout occurs, per codec and bitrate, adaptive and fixed | Q1 |
| RM-B2 | Rate versus attenuation, Wi-Fi | Same with a reference access point; iperf3 TCP, both directions, 30 s per step | Throughput curve; attenuation at 20 Mb/s and at link loss | Q1 |
| RM-B3 | Coexistence | RM-B1 with Wi-Fi streaming at a fixed rate on 2.4 GHz, then on 5 GHz, on the same device | Change in attenuation to failure (dB) | Q1 |

Box results compare devices only when the coupling is held fixed: same box, same probe position, same orientation marks, recorded with a photo. The box's coupling loss is calibrated once with a reference radio pair.

## 5. Tier 2: over-the-air measurements (L5)

Absolute performance of the device's antennas in its enclosure.

| ID | Measurement | Setup | Output | Level |
|---|---|---|---|---|
| RM-O1 | Total radiated power (TRP) and total isotropic sensitivity (TIS) per band | Anechoic chamber with a 3D positioner, CTIA-style method; free space on a low-dielectric support | dBm; TRP − conducted power gives the radiated efficiency in transmit | Q2 |
| RM-O2 | Same with a hand phantom | CTIA hand phantom (or a documented equivalent) holding the device in its normal grip | dB of hand loss per band | Q2 |
| RM-O3 | Radiation efficiency per band | Anechoic chamber or reverberation chamber | % and dB; the antenna's matched efficiency in the enclosure | Q2 |
| RM-O4 | Return loss and isolation | Vector network analyser at the antenna's U.FL with the device assembled; between antennas when there are several | S11, S21 per band | Q1 |
| RM-O5 | Body loss with people | Device in hand and in a front and back trouser pocket of at least four volunteers, as in Andersen et al. (2016); radiated power integrated with and without the person | dB of body loss, mean and spread | Q3 |

Where no chamber is available locally, RM-O1 to RM-O3 are bought from a test lab at Q2; RM-O4 needs only a network analyser and is done at every antenna or enclosure change.

## 6. Tier 3: field courses (L6)

The listener's experience. Each course is documented once (plan, photos, wall types, measured wall loss) and reused for every device and benchmark run.

### 6.1 Courses

| Course | Description | Calibration |
|---|---|---|
| LOS | Open hall or open field, device and sink at 1.2 m, clear line of sight, marks every metre | Path loss checked with a reference radio pair at 1, 5 and 10 m |
| W1 | One interior wall between device and sink; walk away from the wall on the far side | Wall loss measured with the reference pair (both sides of the wall at 1 m from it) and recorded per band |
| W2 | Two interior walls | As W1, for each wall |
| BODY | Device in the listener's front trouser pocket, then back pocket; listener wears the sink and walks a fixed indoor and outdoor loop for 30 min each | Loop drawn and timed; repeated by at least two listeners |
| COEX | Device at 3 m line of sight from the sink, Wi-Fi streaming at a fixed rate on the same device for 60 min, first on 2.4 GHz, then on 5 GHz | Access-point channel and load recorded |

Orientation counts: LOS, W1 and W2 runs repeat with the device turned 0°, 90°, 180° and 270° about its vertical axis, and report the worst orientation as well as the median.

### 6.2 What counts as a dropout

- **Acoustic detection (primary).** The device plays a test file made of a continuous pilot tone with a time code. The sink's output is captured at an ear simulator or coupler microphone (or the sink's own analogue or USB output where it has one). A dropout is any gap or discontinuity of the pilot longer than 5 ms, found by analysis of the recording; any audible glitch reported by the listener is logged too.
- **Device logs (secondary).** The device records codec, bitrate steps, retransmissions, flushed packets and RSSI with timestamps, so each acoustic dropout has a radio cause.
- **Range for a row** is the largest distance at which a 2 min dwell has no dropout, in the worst of the four orientations, in two of three runs.

### 6.3 Wi-Fi throughput at range

iperf3 TCP, single stream and four streams, downlink and uplink, 60 s, three runs per point, at the course's marked points; record RSSI, MCS and spatial streams from the device. Report the median of runs and the range at which sustained throughput falls below 20 Mb/s (lossless hi-res streaming with margin).

### 6.4 Latency

- **Bluetooth audio latency:** relative loopback, as RTINGS does: the device plays a click to the sink and, in the same instant, to a wired reference; both are recorded; the delay between them is the latency. Ten trials per codec, median and worst.
- **Wi-Fi latency under load:** round-trip time to the access point while a saturating TCP transfer runs (a flent-style "realtime response under load" test); median and 99th percentile.

## 7. Turning results into targets

Each experience row gets two criteria:

1. **Absolute:** ideal, warning and hard limit, as every experience budget. Draft until the first prototype calibrates them.
2. **Relative to the benchmark:** the device's result divided by the benchmark median under the same course and conditions. Ideal ≥ 2× (a range or throughput) or ≤ 0.5× (a latency); warning below 1.5× (above 0.67×); hard limit at or below 1.0× (at or above 1.0×), that is not beating the benchmark.

A row passes at a level only when both criteria pass. Results are dated and carry the firmware, the regional power table and the variant (feature blocks per [RFC 0011](https://github.com/opendap-project/rfcs/blob/main/text/0011-feature-blocks-and-variants.md)); results are never inherited from another variant.

## 8. Levers, generic

Ordered by the size of their usual effect where sources allow; each device quantifies them for itself.

| Lever | Effect | Basis |
|---|---|---|
| Antenna efficiency in the enclosure: placement away from metal and from the grip, keep-out, a dielectric window in any metal frame, matching tuned in the final enclosure | Several dB to more than 10 dB between a poor and a good built-in antenna | Andersen 2016 (losses up to 99 %, below 50 % with a better antenna) |
| Placement relative to hand and pocket (the end of the device that stays out of the hand and faces up in a pocket) | 3–10 dB mean body loss by antenna type; 15–20 dB swings with orientation in a pocket | Nielsen 2001; Leith 2020 |
| Regional transmit-power table at the market ceiling where the device's own declaration allows it | Up to the gap between the module's table and the market limit | §2 |
| Codec adaptation and packet types | About 20 dB between the RSSI that LDAC 990 needs and the one 330 kb/s needs | SoundGuys 2025 |
| Dedicated Bluetooth antenna instead of shared | Removes airtime contention with 2.4 GHz Wi-Fi; lets each antenna be placed for its band; needs isolation and a second keep-out | §1.4; module application notes |
| Wi-Fi 2×2 (MIMO and receive combining) | Up to about 10 dB at 1 % outage from diversity in fading, plus a second spatial stream close in | §1.3 |
| Desense control (layout, spread spectrum, clock and harmonic plan) | One dB per dB of in-channel noise | Arithmetic |
| Coexistence software: steer Wi-Fi to 5 GHz during Bluetooth audio, no background 2.4 GHz scans while streaming, PTA priorities | Recovers airtime | §1.4; measured in COEX |

## 9. Sources

- J. Ø. Nielsen, G. F. Pedersen, K. Olesen, I. Z. Kovacs, "Statistics of Measured Body Loss for Mobile Phones", IEEE Trans. Antennas Propag. 49(9), 2001, pp. 1351–1353, doi:10.1109/8.947029 (Aalborg University open copy, read 2026-10-24).
- J. B. Andersen, J. Ø. Nielsen, G. F. Pedersen, "Absorption Related to Hand-Held Devices in Data Mode", IEEE Trans. EMC 58(1), 2016, pp. 47–53, doi:10.1109/TEMC.2015.2504398 (accepted manuscript, Aalborg University, read 2026-10-24).
- D. J. Leith, S. Farrell, "Coronavirus Contact Tracing: Evaluating the Potential of Using Bluetooth Received Signal Strength for Proximity Detection", Trinity College Dublin, 2020-05-06, [arXiv:2006.06822](https://arxiv.org/abs/2006.06822).
- Bluetooth SIG, [Understanding Bluetooth range](https://www.bluetooth.com/learn-about-bluetooth/key-attributes/range/), read 2026-10-24.
- R. Triggs, [The ultimate guide to Bluetooth headphones: LDAC isn't Hi-res](https://www.soundguys.com/ldac-ultimate-bluetooth-guide-20026/), SoundGuys, 2025-10-01.
- [Android Bluetooth latency](https://www.soundguys.com/android-bluetooth-latency-22732/), SoundGuys, read 2026-10-24.
- [RTINGS headphone latency test](https://www.rtings.com/headphones/learn/latency) and its changelogs (method; page content not machine-readable in this pass).
- [Keenan Systems, Wi-Fi 6 client range testing](https://www.keenansystems.com/wordpress/2019/08/06/wi-fi-6-client-range-testing/), 2019-08-06.
- 47 CFR 15.247, [eCFR](https://www.ecfr.gov/current/title-47/section-15.247), read 2026-10-24.
- [Silicon Labs, TX power limitations for regulatory compliance (ETSI, FCC)](https://docs.silabs.com/bluetooth/6.0.0/bluetooth-fundamentals-system-performance/compliance-power-limitations) (secondary for EN 300 328).
- [IEEE 802.15 TG2, Overview of ITU-R P.1238](https://grouper.ieee.org/groups/802/15/pub/802.15%20Archives/802.15%20Archive%20pre-802WWW/2000/Sep00/00294r0P802-15_TG2-Overview-of-ITU1238.pdf) (secondary for ITU-R P.1238).
- [ib-lenhardt, ARIB STD-T66](https://ib-lenhardt.com/kb/glossary/arib-std-t66) (secondary).
- Murata, *Type 2EL/2DL Hardware Application Note* E2B-09-1413 Rev. 9.0 (2026-05-21); Ezurio, *Sona MT320 datasheet* v1.3 (sha256 `6271560926c84763ab894cc53ca324989976206f208a0b1d134dd75230ff3424`).
- Specification pages read 2026-10-24: [Sony NW-ZX706/ZX707 help guide](https://helpguide.sony.net/dmp/1302/v1/en/contents/TP1000752529.html), [FiiO M23 parameters](https://fiio.com/m23_parameters); [iBasso DX180 review](https://mobileaudiophile.com/daps/ibasso-dx180-review/), Mobile Audiophile, 2024-09-07; FCC ID R56-FC4002 on [fccid.io](https://fccid.io/R56FC4002) (secondary).
