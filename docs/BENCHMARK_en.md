# How accurate is AuralPaths? (benchmark against public measurements)

Last run: 2026-11-20. Engine: the page's engine (the engine of the web page itself; room criteria through `engine_js.py`, BRIRs computed by the page in a headless browser) for every value of AuralPaths unless a row says otherwise. Section 4a keeps the earlier Python-engine values for comparison. 한국어: [BENCHMARK_ko.md](BENCHMARK_ko.md), 日本語: [BENCHMARK_ja.md](BENCHMARK_ja.md).

This page compares AuralPaths with rooms and halls whose measured impulse responses are public. Every number comes from
public data and the scripts in this repository and can be recomputed by anyone who has the data (section 6). The
measured data are not redistributed here.

## 1. Summary

AuralPaths was compared with measurements in 8 rooms and halls (BRAS CR1 - CR4, Detmold Konzerthaus, Arvedi Auditorium,
the Fratoni lecture hall and domed hall) and 7 reference scenes (BRAS RS1 - RS7). Scored on the same data and with the
same measures as the 2019 international round robin (Brinkmann et al. 2019, https://doi.org/10.1121/1.5096178), it lies
in the range of the six participating simulation programs (anonymous, A - F): second of seven in the reverberation and
clarity of the chamber music hall (CR3), third and sixth in the two other rooms, and with the smallest tone-colour error
(1.2 dB; post hoc). Reverberation time and the
clarity of an omnidirectional source (C80, D50) agree to within about 1 JND once the model is calibrated to a measured
reverberation time. Early spatial impression agrees in Detmold (page BRIRs, within 0.02 on average) and in BRAS CR4, and is 0.14 low in BRAS CR3 (one seat); the high frequencies of directional
loudspeakers and sound grazing over the seating are not yet supported (section 5).

### Next to the other programs, on the same data

The programs' values are quoted from the paper and its supplement or read from its figures. AuralPaths did not take part
and was scored with the same measures after seeing the measurements (post hoc, section 2).

| comparison | 6 participating programs | AuralPaths |
|---|---|---|
| median shape error of reflection spectra (15 reference cases) | 1.0 - 2.8 dB | 1.5 dB |
| mean error of reverberation and clarity (T20, EDT, C80, D50), material data only | CR2 1.8 - 5.5, CR3 2.9 - 6.4, CR4 1.3 - 4.3 JND | CR2 3.5 (6th of 7), **CR3 3.0 (2nd of 7)**, CR4 2.3 (3rd) JND |
| overestimate of low-frequency reverberation (T20, mean of three rooms) | 125 Hz +58 %, 250 Hz +35 % (mean) | 125 Hz +47 %, 250 Hz +15 % |
| source lateralization error (three rooms) | 0.2 - 14.2 deg | 0.6 - 1.1 deg |
| binaural tone colour error (37 gammatone bands) | 1.3 - 3.2 dB | **1.2 dB** |
| energy decay of coupled rooms (door 30.4 / 4.1 deg) | 2.5 - 7.5 / 4.1 - 5.1 dB | 1.2 - 7.0 / 5.3 - 6.6 dB |
| another program on the same input (RAVEN, BRAS CR3, initial materials; code-to-code, section 4b) | - | T30 1.5 - 1.8 JND (7 - 9 %) shorter than RAVEN; EDT, C80, Ts within about 1 JND |

### By use

| use | evidence (this page) | verdict |
|---|---|---|
| reverberation time, after calibration to a measured or target reverberation | T20 within 3 % (Arvedi), T30 within 3.2 % (Detmold); within 1.6 JND at positions not used for the calibration (BRAS CR3, CR4; median, two ray seeds) | usable |
| reverberation time, predicted from material data only | CR3 and CR4 near the top of the round robin; CR2 15 - 31 % short | conditional: calibrate where possible |
| clarity C80, D50, omnidirectional source | Arvedi C80 within 1 dB at 250 Hz - 4 kHz; CR3 C80 0.5 JND; Detmold C80 0.4 - 1.6 dB high | mostly usable (about 1 JND) |
| how much C80, D50, Ts change when the source changes | 500 Hz - 1 kHz within 0.5 dB on average; at 2 - 4 kHz the change comes out 1 - 2 dB too small (Arvedi, change of source type and position; a change of delay is not checked) | usable at mid frequencies, underestimated at high frequencies |
| source direction, direct-sound ITD | 0.6 - 1.1 deg; direct-sound ITD within 8 - 17 us (mean over five loudspeakers, FABIAN) | usable |
| binaural tone colour | 1.2 dB with the measurement's head (FABIAN); 4.0 dB with the page's default KU100 HRIRs (2 - 6 kHz up to 15 dB lower: another head and another equalisation, not checked further) | usable with a head set that matches the comparison |
| late spaciousness IACC_L3 | within 0.075 at 92 % of 136 pairs (Detmold) | usable |
| absolute EDT | follows the reverberation error in most rooms; 14 - 30 % long in Arvedi | conditional |
| early spaciousness IACC_E3 | 0.04 low (Detmold, 54 % within 0.075); 0.14 / 0.01 low (BRAS CR3 / CR4, BRIRs computed by the page, FABIAN head) | conditional: trends only, post hoc |
| C80, EDT of directional loudspeakers at 2 - 4 kHz | C80 1.2 - 2.8 dB low, EDT 2 - 3 times (Arvedi); the opposite, 3.0 - 3.2 dB high, EDT 12 - 23 % short (Finnish National Opera, measured directivity; growing towards the back rows) | not supported |
| sound grazing over the seating behind the first row | 5 - 11 dB too strong; 3.3 - 6.2 dB with the seat-dip model (RS7) | not supported: check by measurement |
| coupled rooms through a narrow gap | late decay 10 - 13 dB low (CR1, 4.1 deg) | not supported |
| plausibility when listened to | no listening test | not checked |

How to read this: the round-robin scores are post hoc (the participants submitted without knowing the results; here the
measurements could be seen). JND as in ISO 3382-1:2009 Annex A (EDT and T 5 %, C80 1 dB, D50 5 percentage points). All
checks are physical, not perceptual, and they do not show that laboratory perceptual findings carry over to real halls
or sound systems. Three bugs of the Python engine were fixed on 2026-11-12, and 3D models lost rays through faces the engine dropped until 2026-11-18 to 20 (`validation/mesh_leak.md`); the values on this page are after these fixes unless marked
(before and after: [CHANGELOG](../CHANGELOG.md) and the `validation/` documents).

## 2. The 2019 round robin

Brinkmann et al. (2019), "A round robin on room acoustical simulation and auralization", J. Acoust. Soc. Am. 145,
2746, https://doi.org/10.1121/1.5096178. Six programs took part (anonymous, letters A - F; B gave no results for
these scenes). AuralPaths did not take part; it is scored afterwards on the same figures. The paper compares the
spectra only as figures (sec. III.A) and gives no error measure; the shape error and its median are defined and
computed here. Their spectra in the supplementary material (SuppPub2) were read from the PDF's vector graphics and
scored against the measured curve of each figure; AuralPaths against the measured impulse response, with the same
windowing (the two measured curves agree within 0.1 - 0.9 dB).

### 2.0 In the paper's own measures

The paper's results are mostly figures and a few numbers. Each row is one measure as the paper uses it, what the
paper reports for the six programs, and AuralPaths evaluated the same way (BRAS initial material data unless noted).
The numbers for the programs are quoted from the paper or read from its supplementary figures.

| measure (paper) | the programs (paper) | AuralPaths |
|---|---|---|
| Spectra of the simple scenes (Figs. 1 - 3, SuppPub2) | compared by eye only; no number | no number either; our shape error in 2.1 |
| Coupled rooms, 1 kHz EDC, door 30.4 deg (Fig. 4) | measured transition "at approximately t = 0.3 s"; most programs "only a weakly double sloped EDC"; A both decay rates but the wrong transition time | double slope with the fitted data: transition 0.37 - 0.40 s (measured 0.25 - 0.28 s; programs 0.40 - 0.55 s), late decay rate T = 2.9 - 3.0 s (measured 3.7 s; programs 1.7 - 2.1 s, A 4.4 s). With the initial data like most programs: 0.54 - 0.58 s, 2.0 - 2.2 s. (Run of 2026-11-10, 6000 rays, before the 3D-model fixes; not recomputed) |
| Coupled rooms, door 4.1 deg (SuppPub2) | figures only | second slope 10 - 13 dB too low: EDC -51 ... -53 dB at 1.0 s (measured -38 dB), so within the figure's range (down to -50 dB) a single decay with T = 1.1 - 1.4 s (measured late T 4.0 - 4.2 s). Page's engine, 2026-11-20 (16 000 rays): EDC -48 ... -49 dB at 1.0 s (about 10 dB low); T not recomputed |
| T20, mean of 10 source-receiver pairs, octave bands (Fig. 5, S3-1) | measured T20 "on average, overestimated by 58% (125 Hz) and 35% (250 Hz)"; at 500 Hz - 2 kHz "still above the JND in most cases" | +47 % (125 Hz), +15 % (250 Hz), +1 / -4 / -14 / -15 % (500 Hz - 4 kHz), mean over the three rooms; 14 of 18 room-bands beyond the 5 % JND (programs 14 - 17). Read from S3-1, the six programs average +58 % and +35 %, as the paper says |
| Correlation of measured and simulated parameters over the 10 pairs, 1 kHz | not significant, "with the exception of C80 and D50" in the large room (r = 0.7 - 0.9) | the same pattern: large room C80 r = 0.77, D50 r = 0.85 (p < 0.05); all others not significant |
| Tone colour: energy differences in 37 gammatone bands 80 Hz - 16 kHz, BRIRs, mean over sources and ears (Fig. 6) | mean error E 1.3 dB, B and C 2.2 dB, A 3.2 dB | CR2 1.1 dB, CR3 1.3 dB, CR4 1.1 dB (BRIRs computed by the page, FABIAN HRIRs, fitted materials, K8 directivity; with materials calibrated on T30: CR3 1.3, CR4 1.2) |
| ITD of the direct sound (discussion; lateralization in SuppPub3 Fig. S3-33) | "well preserved in the simulations (except for C)"; mean absolute lateralization error A 0.2 - 0.8, B 1.0 - 1.2, E 0.6 - 0.9, C 7.2 - 14.2 deg | 0.6 - 1.1 deg (2.4) |
| Authenticity, plausibility, SAQI (listening tests, Figs. 7 - 10) | no program authentic; B, C, E plausible | not tested |

The paper leaves some details open; choices made here: the transition time and decay rates are from a two-line fit
to the EDC (down to -50 dB), and the tone-colour filter details are listed in `validation/rr_tonecolor.py`. The
binaural renders use fitted materials, as the BRAS binaural check does; the programs had material data only.

### 2.1 Reflection spectra

| | A | C | D | E | F | AuralPaths |
|---|---|---|---|---|---|---|
| median shape error, dB (figures) | 2.3 (9) | 1.0 (15) | 2.8 (15) | 1.3 (13) | 1.4 (13) | **1.5** (15) |

Per figure: [validation/bras_rs.md](../validation/bras_rs.md), section 2.

Which engine: the reference scenes are single plates, bodies and seat-like blocks in an anechoic or hemi-anechoic room,
not rooms, so they cannot be loaded into the page. `validation/bras_rs.py` sums the arrivals of the Python implementation
of the engine's reflection and diffraction formulas (`reflections.py`, `diffraction.py`). The page's implementation of
the same formulas gives the same arrivals on these geometries: 429 diffracted arrivals over RS1 - RS4, RS6 and RS7 agree
in path length within 10⁻⁶ m and in band energy within 0.012 % (`validation/check_rs_pyjs.py`, regression check
`diffraction_rs`, 2026-11-20; RS5 and the second order: `diffraction_plate`, `diffraction_order2`). The values are those
of the run of 2026-11-10; the code of the formulas has not changed since (the 3D-model fixes of 2026-11-18 to 20 concern
the ray tracing of room models, which these scenes do not use). They were not recomputed on 2026-11-20.

### 2.2 Rooms: reverberation and clarity

Scenes 9 - 11 of the round robin are BRAS CR2 (seminar room), CR3 (chamber music hall) and CR4 (auditorium). The
paper's supplementary figure S3-1 (SuppPub3) shows T20, EDT, C80 and D50 in the octave bands 125 Hz - 4 kHz,
averaged over the 10 source-receiver pairs, for the measurement and each program; the programs' values were read
from the figure, the measured ones computed here from the BRAS impulse responses (they agree with the figure within
0.1 - 0.4 JND). Score: mean absolute difference from the measurement in JND (5 % for T20 and EDT, 1 dB for C80,
5 percentage points for D50, as in the figure; ISO 3382-1:2009 Annex A) over the 4 parameters x 6 bands. The score
is defined here, not in the paper. AuralPaths uses the BRAS "initial" material data: the participants also had
material data only, no measured responses (sec. II.C of the paper); the paper does not say which BRAS version of the
data they received.

| room | A | B | C | D | E | F | AuralPaths |
|---|---|---|---|---|---|---|---|
| CR2 seminar room | 5.5 | 1.8 | 3.0 | 1.9 | 3.5 | 3.3 | **3.5** |
| CR3 chamber music hall | 6.4 | 4.9 | 3.6 | 2.9 | 4.4 | 4.6 | **3.0** |
| CR4 auditorium | 3.5 | 4.3 | 2.2 | 1.3 | 2.5 | 2.4 | **2.3** |

In CR2 the reverberation is 15 - 31 % too short from 250 Hz up with the initial data. With the BRAS "fitted" data
(absorption adjusted to the measured reverberation times, so not a prediction) the score is 0.8 (CR2) and 1.4 (CR3).
Computed on 2026-11-20 with the page's engine (the engine of the web page, run through `engine_js.py`), 16 000 rays,
flat point sources, after the 3D-model fixes of 2026-11-19 and 2026-11-20 (`validation/mesh_leak.md`). The scripts
themselves still call the Python engine; with it the same day: 3.7 / 2.9 / 2.3 (initial data) and 1.1 / 1.3 (fitted
data), CR2 before the fix of 2026-11-20. The run of 2026-11-10 (Python engine, 6000 rays, before the fixes) gave
4.1 / 2.8 / 2.2 and 2.4 / 1.2.

### 2.3 Coupled rooms

Scene 8 is BRAS CR1, a laboratory coupled to a reverberation chamber by a door. SuppPub2 figures S2-34 - S2-37 show
the energy decay curve (1 kHz octave) for one source and two microphones, door open 4.1 deg and 30.4 deg; the
curves were read from the vector graphics (the measured curve computed here agrees within 0.4 - 0.9 dB). Score: mean
absolute EDC difference over 0 - 1.2 s down to -50 dB, defined here. Mean of the two microphones:

| door | A | B | C | D | E | F | AuralPaths, initial data | AuralPaths, fitted data |
|---|---|---|---|---|---|---|---|---|
| 30.4 deg | 2.5 | 3.0 | 5.8 | 5.3 | 7.5 | 4.4 | **7.0** | **1.2** |
| 4.1 deg | 4.5 | 4.5 | 5.0 | 5.1 | 4.6 | 4.1 | **6.6** | **5.3** |

At 4.1 deg the late, slower decay from the chamber comes out 10 - 13 dB too low (EDC at 1.0 s: -51 ... -53 dB,
measured -38 dB; Python engine, 40 000 rays, three ray sets, before the 3D-model fixes; -48 ... -49 dB with the
page's engine on 2026-11-20, 16 000 rays, from which the table above is: Python engine the same day 7.2 / 1.0 and
7.2 / 6.5, on 2026-11-10 with 6000 rays 7.6 / 1.7 and 8.2 / 6.6), so it only shows below the range of the figure. This is not ray
noise and not a closed gap: the chamber itself fills as expected (its level is 17 dB below the laboratory's), and the
energy that returns agrees within a few dB with the statistical two-room estimate for the opening of the model (about
0.2 m2). The measured coupling is stronger than the modelled gap alone gives; why (sound through the door leaf,
other leaks, diffraction at the slit) was not examined. The chamber had to be marked as part of the room with the
new mesh option `seeds`, since the flood fill from the source does not pass such a gap.

### 2.4 Source lateralization

SuppPub3 section 2 (figure S3-33) estimates the left/right position of five loudspeakers heard at one seat from
the ITD of the direct sound, and prints the mean absolute deviation from the geometric direction per program. Here
the ITD is taken by cross-correlation (the round robin read its BRIR ITDs by eye); AuralPaths rendered with the
FABIAN HRIRs, as the programs were:

| room | measured BRIR, here | measured (figure) | A | B | C | E | AuralPaths |
|---|---|---|---|---|---|---|---|
| CR2 | 1.4 deg | 2.3 deg | 0.8 deg | 1.0 deg | 14.2 deg | 0.9 deg | **1.1 deg** |
| CR3 | 0.8 deg | 1.0 deg | 0.6 deg | 1.2 deg | 7.9 deg | 0.7 deg | **0.6 deg** |
| CR4 | 0.3 deg | 0.7 deg | 0.2 deg | 1.2 deg | 7.2 deg | 0.6 deg | **0.8 deg** |

Rendered with the KU100 HRIRs instead (the page's default head), the deviation is 0.3 / 0.3 / 0.9 deg (CR2, CR3, CR4). Since 2026-11-20 the BRIRs are computed by the web page itself (`validation/check_bras_brir.py`, default `--engine page`: headless Chromium, the page's engine and binaural rendering, FABIAN HRIRs loaded with **HRIR set…**, measured K8 directivity, 16 000 rays). The values before, rendered by the Python tools before the 3D-model fixes, were 0.6 / 0.3 / 0.5 deg.

### 2.5 Not compared

The listening tests of the round robin (plausibility and the SAQI quality ratings, SuppPub3 sections 3 - 4) need
listeners and were not repeated.

## 3. BRAS reference scenes

Aspoeck et al., BRAS - Benchmark for Room Acoustical Simulation, https://doi.org/10.14279/depositonce-6726.3
(CC BY-SA 4.0). 125 Hz - 4 kHz, medians over the source-receiver pairs. Run of 2026-11-10 with the Python implementation of the engine's formulas, which the page's implementation reproduces (section 2.1, *Which engine*).

| scene | pairs | shape error | mean abs. difference | engine setting |
|---|---|---|---|---|
| RS1 reflection on the floor / an absorber / a diffusor | 10 / 9 / 10 | 2.3 / 3.1 / 3.6 dB | 2.3 / 3.2 / 3.4 dB | default |
| RS2 finite plate 1 m / 2 m (rigid) | 15 / 15 | 1.3 / 1.6 dB | 1.3 / 1.4 dB | default |
| RS3 two parallel plates (600 ms) | 1 | 1.8 dB | 2.6 dB | default |
| RS4 reflector array, on / off centre | 9 / 9 | 1.8 / 1.5 dB | 2.4 / 1.2 dB | default |
| RS5 partition 2.07 m, 11 positions behind it | 11 | 2.7 dB | 2.6 dB | `diffraction_refl` 1 |
| RS6 body 0.72 m, 8 positions behind it | 8 | 3.0 - 3.5 dB | 2.3 - 2.8 dB | `diffraction_order` 2, `diffraction_refl` 1, `finite_reflectors` false |
| RS7 15 low blocks (seat-dip set-up), source in sight | 4 | 4.6 - 6.4 dB | 3.8 - 6.4 dB | default |
| RS7, behind the first block | 4 | 5.2 - 7.4 dB | 5.6 - 9.1 dB | default (too loud, section 5) |
| RS7 source in sight / behind the first block, with the seat-dip model | 4 / 4 | 3.2 - 3.8 / 3.2 - 4.1 dB | 1.8 - 2.5 / 3.3 - 6.2 dB | `seat_dip` on (settings scaled to the 1:3.2 set-up; `validation/rs7_seatdip_bem.py`) |

With the default setting RS5 is 3.9 dB (mean abs.) and RS6 leaves 4 of 8 positions without sound; the options are
off by default because they cost time (up to tens of seconds per source-receiver pair). Details:
[validation/bras_rs.md](../validation/bras_rs.md), [validation/bras_rs5_engine.md](../validation/bras_rs5_engine.md).

## 4. Whole halls

| hall | data | result | details |
|---|---|---|---|
| Detmold Konzerthaus (about 600 seats), 4 stage sources x 34 seats, KU100 dummy head | Detmold SRIR database, https://zenodo.org/records/4116247 (CC BY 4.0) | **Page's engine** (BRIRs computed by the page, 2026-11-15; a drawn hall, so the 3D-model fixes do not apply): IACC_E3 +0.02 on average (60 % of the pairs within 0.075); IACC_L3 +0.01 (92 %); EDT -2.0 / -1.4 / -4.6 % at 500 Hz / 1 / 2 kHz (24 - 29 % within 5 %); C80 -0.1 / +0.5 / +0.9 dB (33 - 60 % within 1 dB). **Python tools (before):** IACC_L3 within 0.075 at 93 % of the pairs; IACC_E3 0.04 low on average (54 % within 0.075); EDT -3 / -7 / -15 % at 500 Hz / 1 / 2 kHz (13 - 32 % of the pairs within 5 %); C80 +0.4 / +1.0 / +1.6 dB (34 - 41 % within 1 dB); T30 within 3.2 % after calibration. With the early-direction option of 2026-11-13 (default); without it: IACC_E3 0.11 low, EDT -3 / -6 / -11 %, C80 +0.3 / +0.7 / +1.4 dB. Before the engine fixes of 2026-11-12: IACC_E3 0.15 low, EDT 0 ... +3 %, C80 0.3 - 0.8 dB low (with the seat-dip model, before the fixes: IACC_E3 0.10 low, C80 -0.2 ... +0.2 dB) | [validation/detmold_kh.md](../validation/detmold_kh.md) |
| BRAS CR3 chamber music hall, CR4 auditorium (binaural, FABIAN head) | BRAS | direct-sound ITD within 8 - 11 us and octave spectrum within 1.4 dB (BRIRs computed by the page, 2026-11-20); from the runs with the Python tools: discrete reflections 14 - 70 ms after the direct sound: measured - model -1.1 dB (median, both halls); CR4 late IACC too low at seats under a flutter between ceiling panels and aisle | [validation/bras_brir_iacc_diag.md](../validation/bras_brir_iacc_diag.md) |
| Fratoni lecture hall (ULH) and domed hall (STC) | Fratoni et al. dataset | ULH: EDT, C50 and Ts within about 1 JND and T30 within 1.7 JND at 500 Hz - 4 kHz (T30 8 % long at 500 Hz - 1 kHz); STC T30 18 - 27 % too long in the 3D model, 5 - 16 % in the 2.5D hall (calibrate first in such halls). Page's engine, 2026-11-20; Python engine before: ULH within about 1 JND, STC about 15 % long | [validation/](../validation/) `fratoni_*.md` |
| Auditorium Giovanni Arvedi, Cremona (about 470 seats round the stage), 5 stage sources x 65 receivers, 8-capsule array; simplified model from the published drawings | Politecnico di Milano, https://doi.org/10.5281/zenodo.20098848 (CC BY 4.0) | **Page's engine** (2026-11-15; the hall is excluded from further checks): omnidirectional source C80 -0.29 / +0.04 / -0.58 / -0.88 dB, EDT +18 / +19 / +28 / +35 % at 500 Hz / 1 / 2 / 4 kHz; Genelec loudspeakers C80 -1.5 ... -2.3 / -1.6 ... -3.0 dB at 2 / 4 kHz. **Python engine:** **post hoc** (the blind run placed the receivers on the wrong side and is void). After the engine fixes of 2026-11-12: omnidirectional source T20 within 3 % (45 - 78 % within 5 %), C80 -0.9 ... +0.2 dB at 250 Hz - 4 kHz, D50 within 0.06, EDT 14 - 30 % too long; Genelec loudspeakers (8020A data): C80 within 0.7 dB at 500 Hz - 1 kHz, 1.2 - 2.8 dB low at 2 - 4 kHz, EDT 2 - 3 times too long there. Before the fixes: C80 1.3 - 1.5 dB low at 2 - 4 kHz (omnidirectional), 3 - 8 dB (loudspeakers) | [validation/arvedi_check.md](../validation/arvedi_check.md) |
| Arni variable-acoustics room (Aalto, 8.9 x 6.3 x 3.6 m), 0 - 9 of 55 panels open, 37 states x 5 microphones | Arni dataset, https://doi.org/10.5281/zenodo.6985104 (CC BY 4.0) | **Page's engine** (rerun 2026-11-19 after the 3D-model fix, 185 pairs): T30 +10 / +4 / +3 / +0 %, EDT +7 / +2 / +0 / -2 %, C80 +0.17 / +0.04 / +0.32 / -0.01 dB at 500 Hz / 1 / 2 / 4 kHz; 250 Hz T30 +25 %. **Python engine (before the fix):** Bare surfaces and curtains calibrated on the all-closed state only, the other 36 states predicted: 500 Hz - 4 kHz T30 and EDT -6 ... +7 % on average, C80 within 0.6 dB; EDT/T30 simulated 0.87 - 0.95 vs measured 0.91 - 0.96 (250 Hz - 4 kHz); 250 Hz +20 % (no low-frequency panel data); absorption on the ceiling too effective in T30 (post hoc) | [validation/arni_check.md](../validation/arni_check.md) |
| Finnish National Opera main auditorium (1,350 seats), 2 Genelec 8331A on stage x 97 stalls seats | OperaRIR, https://doi.org/10.5281/zenodo.8096639 (CC BY-NC 4.0); directivity https://zenodo.org/records/10255555 | **Page's engine** (2026-11-15, unchanged in the rerun of 2026-11-19; 194 pairs): C80 +1.66 / +1.67 / +2.48 / +2.25 dB, EDT -19 / -26 / -28 / -18 % at 500 Hz / 1 / 2 / 4 kHz. **Python engine:** Simplified model from the published plan and section (Lokki et al. 2015), only seating and stage-house absorption calibrated on T30: T30 within 6 %; C80 +1.4 dB at 500 Hz - 1 kHz, +3.0 - 3.2 dB at 2 - 4 kHz (13 - 21 % within 1 dB), front rows 2 - 8 within 1 - 2 dB, row 17 +7.5 - 8.1 dB at 2 - 4 kHz; EDT 12 - 23 % short (post hoc, diagnostic). Backrests added as geometric strips (no diffraction): the growth with the row stays (row 17 +9 dB at 2 - 4 kHz), also with the seat-dip model (C80 +1 dB higher at 1 - 4 kHz); the direct sound follows the measurement, the late energy falls too steeply towards the rear; scattering 0.5 on the hard surfaces (sensitivity test) halves this; in Detmold it also brings C80 closer, in Arvedi C80 0.2 - 0.4 dB lower (EDT closer in all three), defaults unchanged | [validation/opera_check.md](../validation/opera_check.md) |

Reference values: EDT 5 % and C80 1 dB from ISO 3382-1:2009 Annex A; IACC 0.075 as assumed in the thesis that
accompanies the Detmold data (no primary source checked).

## 4a. The page's engine and the Python engine side by side

Until 2026-11-13 this page was computed with the Python engine, whose ray tracing is pyroomacoustics. Since 2026-11-15 the
Python tools can compute with the page's own engine (`engine_js.py`), since 2026-11-20 every validation script does so by
default, and sections 1 - 4 hold the page's values. The table keeps both engines for the halls of section 4 (runs of
2026-11-15; the Python values of Arni are from before the 3D-model fix). Why it matters: in a **drawn (2.5-D) hall** the two engines scatter
differently (the page: a reflection is specular or diffuse with probability s; pyroomacoustics: every reflection in
a direction mixed from both) and need different absorption for the same reverberation (Detmold, 1 kHz: factor 0.97
against 0.72). In 3-D (OBJ) halls both mix; they agreed within about 2 % on 2026-11-15, and on 2026-11-20 the page's engine gave T30 4 - 5 % longer than the Python engine in BRAS CR4 before calibration (cause not found; after calibration the two agree). Materials calibrated with one engine must
not be used in a drawn hall of the other.

| check | page's engine | Python engine (sections 1 - 4) | details |
|---|---|---|---|
| Arvedi, omnidirectional source, 500 Hz / 1 / 2 / 4 kHz | C80 -0.29 / +0.04 / -0.58 / -0.88 dB; EDT +18 / +19 / +28 / +35 % | C80 -0.57 / -0.05 / -0.59 / -0.85 dB; EDT +15 / +14 / +21 / +30 % | [engine_js_halls.md](../validation/engine_js_halls.md) |
| Arvedi, Genelec loudspeakers S1 - S4, 2 / 4 kHz | C80 -1.5 ... -2.3 / -1.6 ... -3.0 dB | C80 -1.2 ... -2.1 / -1.4 ... -2.8 dB | same |
| Arni, 37 states, 500 Hz / 1 / 2 / 4 kHz | T30 +10 / +4 / +3 / +1 %; EDT +7 / +2 / +1 / -2 %; C80 +0.17 / +0.02 / +0.31 / -0.06 dB | T30 +7 / -0 / -1 / -5 %; EDT +4 / -2 / -3 / -6 %; C80 +0.32 / +0.25 / +0.58 / +0.29 dB | same |
| OperaRIR, 194 pairs, 500 Hz / 1 / 2 / 4 kHz | C80 +1.66 / +1.67 / +2.48 / +2.25 dB; EDT -19 / -26 / -28 / -18 % | C80 +1.36 / +1.39 / +3.16 / +2.98 dB; EDT -12 / -20 / -23 / -12 % | same |
| Detmold, 24 omnidirectional-microphone positions, 500 Hz / 1 / 2 kHz (each engine calibrated by itself) | EDT +9.8 / +2.1 / +8.1 %; C80 -0.3 / -0.0 / +0.7 dB | EDT +7.4 / -1.8 / +1.4 %; C80 -0.6 / -0.3 / +0.7 dB | [detmold_js.md](../validation/detmold_js.md) |
| Detmold, binaural, 136 pairs (KU100), 500 Hz / 1 / 2 kHz; BRIRs computed by the page itself | IACC_E3 +0.02 (60 % within 0.075); IACC_L3 +0.01 (92 %); EDT -2.0 / -1.4 / -4.6 % (24 - 29 % within 5 %); C80 -0.1 / +0.5 / +0.9 dB (33 - 60 % within 1 dB) | IACC_E3 -0.04 (54 %); IACC_L3 within 0.075 at 93 %; EDT -3 / -7 / -15 %; C80 +0.4 ... +1.6 dB | [detmold_js.md](../validation/detmold_js.md) |

The findings of sections 1, 4 and 5 hold with both engines. New on 2026-11-15:

- **Energy of the first 80 ms by time window** (mean over the positions, simulated minus measured, 500 Hz - 4 kHz):
  within about 1.3 dB in every window in BRAS CR3, CR4 (3-D models of the database) and Detmold (drawn hall);
  in Arvedi +1 ... +2 dB before 20 ms and -4 ... -5 dB at 20 - 50 ms, while the decay from 80 ms on agrees within
  0.3 dB ([arvedi_placement.md](../validation/arvedi_placement.md), [bras_decay_shape.md](../validation/bras_decay_shape.md)).
  The long EDT of Arvedi is therefore an error of that model's early reflection pattern; absorption placement
  (a factor of 4 changes the EDT bias by 5 points), the scattering model and the engine are ruled out.
- **Which scattering model is closer** is not decided: a tie in Detmold; in Arni the mixed direction gives the
  measured EDT / T30 (0.88 - 0.94, measured 0.91 - 0.96; either-or 0.96 - 0.98); in Arvedi the EDT error is the
  same with both. Defaults unchanged.
- **Ray noise** ([timing.md](../validation/timing.md), [ray_noise.md](../validation/ray_noise.md)): the EDT of a
  single receiver differs by 8 % between two seeds at 20000 rays, 3 % at 80000, 2 % at 320000 (page's engine,
  Detmold); hall means by less than 1 %. The page's engine needs 4 / 13 / 57 s per source for these.
- **Calibration**: the positions are combined by the median (the mean before). With one ray-tracing run per
  position the mean is not robust (Detmold: factor 0.74 or 1.00 at 1 kHz from the same data, depending on the ray
  count).

## 4b. Another program on the same input: RAVEN (BRAS CR3, 2026-11-20/21)

RAVEN (RWTH Aachen, Institute for Hearing Technology and Acoustics; installer 0.96; described in Schröder 2011,
https://publications.rwth-aachen.de/record/50580) was run by the author of AuralPaths on BRAS CR3 with the same geometry (`CR3.skp`, exported to RAVEN's
format: 2164 polygons, 2763.0 m², 3330.6 m³, material areas as the BRAS documentation), the BRAS initial material
estimates (octave values, one scattering value per material, the 1 kHz value), the same source and receiver positions
(read from the BRAS SOFA files; direct-sound times of the measured RIRs match within 0.18 ms rms) and no calibration.
RAVEN: image sources to order 2, 50 000 particles per band, detection sphere 0.6 m, 20 °C / 50 %, three runs.
AuralPaths: the page's engine with the page's settings (image sources to order 2, 50 000 rays, the same single
scattering value), three ray seeds. Measured RIRs, RAVEN's RIRs and AuralPaths' energy histograms are analysed with
the same code (`validate_bras_cr.criteria`). This is a code-to-code comparison: neither program is the reference.

Omnidirectional source, 10 source-receiver pairs, median over the pairs of the 500 Hz - 1 kHz mean:

| | measured | AuralPaths (3 seeds) | RAVEN | AuralPaths - RAVEN |
|---|---|---|---|---|
| T30 | 1.32 s | 1.53 - 1.56 s | 1.68 s | -1.5 ... -1.8 JND (7 - 9 % shorter) |
| EDT | 1.30 s | 1.49 - 1.50 s | 1.53 s | -0.4 ... -0.5 JND |
| C80 | 1.35 dB | 0.71 - 0.95 dB | 0.44 dB | +0.3 ... +0.5 dB |
| Ts | 94 ms | 104 - 106 ms | 112 ms | -0.6 ... -0.8 JND |

The RAVEN column is the median over its 10 pairs (from the comparison report; difference of medians, not median of
differences). Per octave band (125 Hz - 4 kHz; AuralPaths with scattering per band and 16 000 rays, one run), AuralPaths
gives the shorter T30 in every band: -2.4 / -1.6 / -3.0 / -2.1 / -1.5 / -0.8 JND, so the difference is not larger above
1 kHz than below. Directional source (Genelec 8020c, 4 orientations x 3 positions x 5 receivers; RAVEN with its own
third-octave directivity, AuralPaths with the BRAS balloon reduced to octaves on a 5 deg grid, scattering per band,
16 000 rays): both programs follow the measured change of C80 with the loudspeaker's orientation (1 and 2 kHz) with
0.61 dB (RAVEN) and 0.71 dB (AuralPaths) rms error; the level of the direct sound over the four orientations spans
less in AuralPaths than in the measurement (on axis +5.4 against +7.3 dB for LS1), but AuralPaths' value was taken
from the first 4 ms of the energy histogram, which may include the floor reflection, so this is not settled.

Reading: the two programs differ in one direction, AuralPaths decays 7 - 9 % faster in T30, while EDT, C80 and Ts
agree within about 1 JND. Which one is closer to the measurement says nothing here: the initial estimates themselves
predict too much reverberation below 1 kHz and too little at 2 kHz (Eyring 1.56 / 1.25 / 1.00 s at 500 Hz / 1 / 2 kHz
against measured 1.31 / 1.34 / 1.32 s). The cause of the 7 - 9 % has not been found; the 1 % smaller voxel volume
(3304 against 3330.6 m³) accounts for about 1 %, and the voxel size (5 or 6.5 cm) changes nothing. Limits: one hall,
one seat set, RAVEN run by the author of AuralPaths; binaural quantities were not compared.

## 5. Known weak spots

Each item comes from particular rooms and conditions. Where no other program was run on the same data (Detmold, Arvedi),
it is not known whether other programs show similar errors there.

- **Sound just above seat rows** (grazing incidence) behind the first row: 5 - 11 dB too loud and no seat dip (here
  about 500 Hz) without the optional seat-dip model (BRAS RS7). With it: 1.8 - 6.2 dB; the dip at 400 -
  500 Hz within 3 dB, but 315 Hz 5 - 7 dB too quiet (the simulated dip starts about a third octave low) and 200 Hz
  3 - 4 dB too loud; generic seats, two-dimensional, checked in one real hall with default seats (docs/MODEL_en.md,
  *Seat dip*). The deep notch at the lower edge of the dip is not explained (ruled out: 2-D approximation, block
  dimensions, surface absorption); read levels there qualitatively. Check such positions with measurements.
- **Early spaciousness** (IACC_E3) about 0.04 too low in a concert hall (Detmold; BRAS CR3 0.14, CR4 0.01 with the page's BRIRs and the FABIAN head). It was 0.11 low before the default option of 2026-11-13 that sets the interaural coherence of the early residual from the arrival directions of the scattered energy; the fix came from a post hoc diagnosis, so it is not a blind check. In exchange C80 in Detmold is 0.4 - 1.6 dB high (0.3 - 1.4 without the option) and EDT 3 - 15 % short (3 - 11 without); the earlier close agreement of C80 and EDT was partly the double-counted scattered energy (fixed 2026-11-12). The optional seat-dip model had narrowed the IACC_E3 deficit (0.15 -> 0.10, before the fixes; not repeated) but moves the first 15 ms further from the measurement at 200 - 315 Hz.
- **Early decay and direct / early balance near the stage** in a hall not used in development, modelled from published drawings (Arvedi, post hoc): EDT 14 - 30 % too long with T20 right; with directional loudspeakers C80 1.2 - 2.8 dB low and EDT 2 - 3 times too long at 2 - 4 kHz. Ruled out: aim (tilt -10 ... +5 deg), volume (model at 5206 m3), image-source order (3 instead of 2), scattering (0.05 to twice the value: EDT / T30 moves by 0.05 at most); a more detailed model with per-surface published absorption shortened the EDT error only below 1 kHz. In a small room with known absorber positions (Arni) the engine does give an EDT shorter than T30 (EDT/T30 0.87 - 0.95, measured 0.91 - 0.96; [validation/arni_check.md](../validation/arni_check.md)), so it is not a property of the engine as such. Open: the loudspeaker data (8020A for 8020C) and how seating returns a beam aimed at it ([validation/arvedi_check.md](../validation/arvedi_check.md)).
- **Flutter between parallel surfaces**: repeated reflections between finite panels are too weak at low
  frequencies with the default finite-reflector factor (RS3) and a ceiling-aisle flutter was underestimated in CR4.
- Diffraction from edge end points, third and higher orders, plates between 5 cm and a few tenths of a metre thick:
  not checked.
- **Coupled rooms joined by a narrow opening** (a door ajar): the late decay from the second room is 10 - 13 dB too low (CR1,
  4.1 deg). Mark the second room with the mesh option `seeds`; results with a wide opening are good.
- **Material data matter more than the engine**: with the BRAS initial data, CR2 reverberates 15 - 31 % too short;
  calibrate to a measured reverberation time where one exists.
- No listening test yet: these checks are physical, not perceptual.

## 6. Rerun it

Data: BRAS scene descriptions RS1 - RS7 and CR1 - CR4, surface descriptions, the paper's supplementary material, Detmold SRIR database (download from the links
above). Then:

    python validation/bras_rs.py <BRAS folder> --scene RS2          # RS1 - RS4, RS6, RS7
    python validation/bras_rs5.py <BRAS folder> --variant thin+floor
    python validation/rs7_seatdip_bem.py <BRAS folder>                # RS7 with the seat-dip model
    python validation/rr_extract.py <SuppPub2.pdf> out/rs/rr_curves.csv
    python validation/rr_compare.py
    python validation/rr_extract_ra.py <SuppPub3.pdf> out/rs/rr_ra.csv
    python validation/rr_complex.py <BRAS folder> CR3 --coeffs initial --rays 16000   # CR2, CR3, CR4; then --table out/rs
    python validation/rr_coupled.py --extract <SuppPub2.pdf>; python validation/rr_coupled.py <BRAS folder> --rays 16000
    python validation/check_bras_brir.py <BRAS folder> CR3 --k8-mps <K8 file> --hrir <FABIAN HRIR SOFA> --rays 16000 --out validation/bras_brir_CR3_FABIAN_K8data   # CR2, CR4 too
    python validation/rr_lateral.py <BRAS folder> --fabian <FABIAN HRIR SOFA> --ku100 hrir/KU100.sofa --pattern "bras_brir_{hall}_FABIAN_K8data_LS{k}_sim.wav" --sim-hrir fabian
    python validation/detmold_kh.py ...                              # see the script's docstring

Outputs go to `out/` (not in the repository: they are derived from the measured data).
