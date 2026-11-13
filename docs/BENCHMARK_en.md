# How accurate is AuralPaths? (benchmark against public measurements)

Last run: 2026-11-13. 한국어: [BENCHMARK_ko.md](BENCHMARK_ko.md), 日本語: [BENCHMARK_ja.md](BENCHMARK_ja.md).

This page compares AuralPaths with rooms and halls whose measured impulse responses are public. Every number comes from
public data and the scripts in this repository and can be recomputed by anyone who has the data (section 6). The
measured data are not redistributed here.

## 1. Summary

AuralPaths was compared with measurements in 8 rooms and halls (BRAS CR1 - CR4, Detmold Konzerthaus, Arvedi Auditorium,
the Fratoni lecture hall and domed hall) and 7 reference scenes (BRAS RS1 - RS7). Scored on the same data and with the
same measures as the 2019 international round robin (Brinkmann et al. 2019, https://doi.org/10.1121/1.5096178), it lies
in the range of the six participating simulation programs (anonymous, A - F), and has the smallest error of all in the
reverberation and clarity of the chamber music hall (CR3) and in source lateralization. Reverberation time and the
clarity of an omnidirectional source (C80, D50) agree to within about 1 JND once the model is calibrated to a measured
reverberation time. Early spatial impression is slightly low (Detmold 0.04); the high frequencies of directional
loudspeakers and sound grazing over the seating are not yet supported (section 5).

### Next to the other programs, on the same data

The programs' values are quoted from the paper and its supplement or read from its figures. AuralPaths did not take part
and was scored with the same measures after seeing the measurements (post hoc, section 2).

| comparison | 6 participating programs | AuralPaths |
|---|---|---|
| median shape error of reflection spectra (15 reference cases) | 1.0 - 2.8 dB | 1.5 dB |
| mean error of reverberation and clarity (T20, EDT, C80, D50), material data only | CR2 1.8 - 5.5, CR3 2.9 - 6.4, CR4 1.3 - 4.3 JND | CR2 4.1, **CR3 2.8 (best of 7)**, CR4 2.2 (joint 2nd) JND |
| overestimate of low-frequency reverberation (T20, mean of three rooms) | 125 Hz +58 %, 250 Hz +35 % (mean) | 125 Hz +34 %, 250 Hz +7 % |
| source lateralization error (three rooms) | 0.2 - 14.2 deg | **0.3 - 0.6 deg** |
| binaural tone colour error (37 gammatone bands) | 1.3 - 3.2 dB | 1.4 dB |
| energy decay of coupled rooms (door 30.4 / 4.1 deg) | 2.5 - 7.5 / 4.1 - 5.1 dB | 1.7 - 7.6 / 6.6 - 8.2 dB |

### By use

| use | evidence (this page) | verdict |
|---|---|---|
| reverberation time, after calibration to a measured or target reverberation | T20 within 3 % (Arvedi), T30 within 3.2 % (Detmold); 0.8 JND at positions not used for the calibration (BRAS CR3, CR4) | usable |
| reverberation time, predicted from material data only | CR3 and CR4 near the top of the round robin; CR2 30 - 35 % short | conditional: calibrate where possible |
| clarity C80, D50, omnidirectional source | Arvedi C80 within 1 dB at 250 Hz - 4 kHz; CR3 C80 0.5 JND; Detmold C80 0.4 - 1.6 dB high | mostly usable (about 1 JND) |
| how much C80, D50, Ts change when the source changes | 500 Hz - 1 kHz within 0.5 dB on average; at 2 - 4 kHz the change comes out 1 - 2 dB too small (Arvedi, change of source type and position; a change of delay is not checked) | usable at mid frequencies, underestimated at high frequencies |
| source direction, direct-sound ITD | 0.3 - 0.6 deg; direct-sound ITD within 5 us (FABIAN) | usable |
| binaural tone colour | 1.4 dB | usable |
| late spaciousness IACC_L3 | within 0.075 at 92 % of 136 pairs (Detmold) | usable |
| absolute EDT | follows the reverberation error in most rooms; 14 - 30 % long in Arvedi | conditional |
| early spaciousness IACC_E3 | 0.04 low (Detmold, 54 % within 0.075); 0.08 / 0.07 low (BRAS CR3 / CR4) | conditional: trends only, post hoc |
| C80, EDT of directional loudspeakers at 2 - 4 kHz | C80 1.2 - 2.8 dB low, EDT 2 - 3 times (Arvedi); the opposite, 3.0 - 3.2 dB high, EDT 12 - 23 % short (Finnish National Opera, measured directivity; growing towards the back rows) | not supported |
| sound grazing over the seating behind the first row | 5 - 11 dB too strong; 3.3 - 6.2 dB with the seat-dip model (RS7) | not supported: check by measurement |
| coupled rooms through a narrow gap | late decay about 13 dB low (CR1, 4.1 deg) | not supported |
| plausibility when listened to | no listening test | not checked |

How to read this: the round-robin scores are post hoc (the participants submitted without knowing the results; here the
measurements could be seen). JND as in ISO 3382-1:2009 Annex A (EDT and T 5 %, C80 1 dB, D50 5 percentage points). All
checks are physical, not perceptual, and they do not show that laboratory perceptual findings carry over to real halls
or sound systems. Three bugs of the Python engine were fixed on 2026-11-12; all values on this page are after the fixes
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
| Coupled rooms, 1 kHz EDC, door 30.4 deg (Fig. 4) | measured transition "at approximately t = 0.3 s"; most programs "only a weakly double sloped EDC"; A both decay rates but the wrong transition time | double slope with the fitted data: transition 0.37 - 0.40 s (measured 0.25 - 0.28 s; programs 0.40 - 0.55 s), late decay rate T = 2.9 - 3.0 s (measured 3.7 s; programs 1.7 - 2.1 s, A 4.4 s). With the initial data like most programs: 0.54 - 0.58 s, 2.0 - 2.2 s |
| Coupled rooms, door 4.1 deg (SuppPub2) | figures only | second slope about 13 dB too low: EDC -51 ... -53 dB at 1.0 s (measured -38 dB), so within the figure's range (down to -50 dB) a single decay with T = 1.1 - 1.4 s (measured late T 4.0 - 4.2 s) |
| T20, mean of 10 source-receiver pairs, octave bands (Fig. 5, S3-1) | measured T20 "on average, overestimated by 58% (125 Hz) and 35% (250 Hz)"; at 500 Hz - 2 kHz "still above the JND in most cases" | +34 % (125 Hz), +7 % (250 Hz), -6 / -12 / -20 / -17 % (500 Hz - 4 kHz), mean over the three rooms; 14 of 18 room-bands beyond the 5 % JND (programs 14 - 17). Read from S3-1, the six programs average +58 % and +35 %, as the paper says |
| Correlation of measured and simulated parameters over the 10 pairs, 1 kHz | not significant, "with the exception of C80 and D50" in the large room (r = 0.7 - 0.9) | the same pattern: large room C80 r = 0.77, D50 r = 0.85 (p < 0.05); all others not significant |
| Tone colour: energy differences in 37 gammatone bands 80 Hz - 16 kHz, BRIRs, mean over sources and ears (Fig. 6) | mean error E 1.3 dB, B and C 2.2 dB, A 3.2 dB | CR2 1.4 dB, CR3 1.4 dB, CR4 1.4 dB (FABIAN HRIRs, fitted materials, K8 directivity) |
| ITD of the direct sound (discussion; lateralization in SuppPub3 Fig. S3-33) | "well preserved in the simulations (except for C)"; mean absolute lateralization error A 0.2 - 0.8, B 1.0 - 1.2, E 0.6 - 0.9, C 7.2 - 14.2 deg | 0.3 - 0.6 deg (2.4) |
| Authenticity, plausibility, SAQI (listening tests, Figs. 7 - 10) | no program authentic; B, C, E plausible | not tested |

The paper leaves some details open; choices made here: the transition time and decay rates are from a two-line fit
to the EDC (down to -50 dB), and the tone-colour filter details are listed in `validation/rr_tonecolor.py`. The
binaural renders use fitted materials, as the BRAS binaural check does; the programs had material data only.

### 2.1 Reflection spectra

| | A | C | D | E | F | AuralPaths |
|---|---|---|---|---|---|---|
| median shape error, dB (figures) | 2.3 (9) | 1.0 (15) | 2.8 (15) | 1.3 (13) | 1.4 (13) | **1.5** (15) |

Per figure: [validation/bras_rs.md](../validation/bras_rs.md), section 2.

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
| CR2 seminar room | 5.5 | 1.8 | 3.0 | 1.9 | 3.5 | 3.3 | **4.1** |
| CR3 chamber music hall | 6.4 | 4.9 | 3.6 | 2.9 | 4.4 | 4.6 | **2.8** |
| CR4 auditorium | 3.5 | 4.3 | 2.2 | 1.3 | 2.5 | 2.4 | **2.2** |

In CR2 the reverberation is 30 - 35 % too short from 250 Hz up with the initial data. With the BRAS "fitted" data
(absorption adjusted to the measured reverberation times, so not a prediction) the score is 2.4 (CR2) and 1.2 (CR3).
Ray tracing with 6000 rays and first-order image sources, flat point sources.

### 2.3 Coupled rooms

Scene 8 is BRAS CR1, a laboratory coupled to a reverberation chamber by a door. SuppPub2 figures S2-34 - S2-37 show
the energy decay curve (1 kHz octave) for one source and two microphones, door open 4.1 deg and 30.4 deg; the
curves were read from the vector graphics (the measured curve computed here agrees within 0.4 - 0.9 dB). Score: mean
absolute EDC difference over 0 - 1.2 s down to -50 dB, defined here. Mean of the two microphones:

| door | A | B | C | D | E | F | AuralPaths, initial data | AuralPaths, fitted data |
|---|---|---|---|---|---|---|---|---|
| 30.4 deg | 2.5 | 3.0 | 5.8 | 5.3 | 7.5 | 4.4 | **7.6** | **1.7** |
| 4.1 deg | 4.5 | 4.5 | 5.0 | 5.1 | 4.6 | 4.1 | **8.2** | **6.6** |

At 4.1 deg the late, slower decay from the chamber comes out about 13 dB too low (EDC at 1.0 s: -51 ... -53 dB,
measured -38 dB; 40 000 rays, three ray sets), so it only shows below the range of the figure. This is not ray
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
| CR2 | 1.4 deg | 2.3 deg | 0.8 deg | 1.0 deg | 14.2 deg | 0.9 deg | **0.6 deg** |
| CR3 | 0.8 deg | 1.0 deg | 0.6 deg | 1.2 deg | 7.9 deg | 0.7 deg | **0.3 deg** |
| CR4 | 0.3 deg | 0.7 deg | 0.2 deg | 1.2 deg | 7.2 deg | 0.6 deg | **0.5 deg** |

Rendered with the KU100 HRIRs instead (the page's default head), the deviation is 1.2 - 1.3 deg (CR3, CR4).

### 2.5 Not compared

The listening tests of the round robin (plausibility and the SAQI quality ratings, SuppPub3 sections 3 - 4) need
listeners and were not repeated.

## 3. BRAS reference scenes

Aspoeck et al., BRAS - Benchmark for Room Acoustical Simulation, https://doi.org/10.14279/depositonce-6726.3
(CC BY-SA 4.0). 125 Hz - 4 kHz, medians over the source-receiver pairs.

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
| Detmold Konzerthaus (about 600 seats), 4 stage sources x 34 seats, KU100 dummy head | Detmold SRIR database, https://zenodo.org/records/4116247 (CC BY 4.0) | IACC_L3 within 0.075 at 93 % of the pairs; IACC_E3 0.04 low on average (54 % within 0.075); EDT -3 / -7 / -15 % at 500 Hz / 1 / 2 kHz (13 - 32 % of the pairs within 5 %); C80 +0.4 / +1.0 / +1.6 dB (34 - 41 % within 1 dB); T30 within 3.2 % after calibration. With the early-direction option of 2026-11-13 (default); without it: IACC_E3 0.11 low, EDT -3 / -6 / -11 %, C80 +0.3 / +0.7 / +1.4 dB. Before the engine fixes of 2026-11-12: IACC_E3 0.15 low, EDT 0 ... +3 %, C80 0.3 - 0.8 dB low (with the seat-dip model, before the fixes: IACC_E3 0.10 low, C80 -0.2 ... +0.2 dB) | [validation/detmold_kh.md](../validation/detmold_kh.md) |
| BRAS CR3 chamber music hall, CR4 auditorium (binaural, FABIAN head) | BRAS | direct-sound ITD within 5 us, 2 - 4 kHz spectrum within 1.4 dB; discrete reflections 14 - 70 ms after the direct sound: measured - model -1.1 dB (median, both halls); CR4 late IACC too low at seats under a flutter between ceiling panels and aisle | [validation/bras_brir_iacc_diag.md](../validation/bras_brir_iacc_diag.md) |
| Fratoni lecture hall (ULH) and domed hall (STC) | Fratoni et al. dataset | ULH within about 1 JND at 500 Hz - 4 kHz; STC T30 about 15 % too long (calibrate first in such halls) | [validation/](../validation/) `fratoni_*.md` |
| Auditorium Giovanni Arvedi, Cremona (about 470 seats round the stage), 5 stage sources x 65 receivers, 8-capsule array; simplified model from the published drawings | Politecnico di Milano, https://doi.org/10.5281/zenodo.20098848 (CC BY 4.0) | **post hoc** (the blind run placed the receivers on the wrong side and is void). After the engine fixes of 2026-11-12: omnidirectional source T20 within 3 % (45 - 78 % within 5 %), C80 -0.9 ... +0.2 dB at 250 Hz - 4 kHz, D50 within 0.06, EDT 14 - 30 % too long; Genelec loudspeakers (8020A data): C80 within 0.7 dB at 500 Hz - 1 kHz, 1.2 - 2.8 dB low at 2 - 4 kHz, EDT 2 - 3 times too long there. Before the fixes: C80 1.3 - 1.5 dB low at 2 - 4 kHz (omnidirectional), 3 - 8 dB (loudspeakers) | [validation/arvedi_check.md](../validation/arvedi_check.md) |
| Arni variable-acoustics room (Aalto, 8.9 x 6.3 x 3.6 m), 0 - 9 of 55 panels open, 37 states x 5 microphones | Arni dataset, https://doi.org/10.5281/zenodo.6985104 (CC BY 4.0) | Bare surfaces and curtains calibrated on the all-closed state only, the other 36 states predicted: 500 Hz - 4 kHz T30 and EDT -6 ... +7 % on average, C80 within 0.6 dB; EDT/T30 simulated 0.87 - 0.95 vs measured 0.91 - 0.96 (250 Hz - 4 kHz); 250 Hz +20 % (no low-frequency panel data); absorption on the ceiling too effective in T30 (post hoc) | [validation/arni_check.md](../validation/arni_check.md) |
| Finnish National Opera main auditorium (1,350 seats), 2 Genelec 8331A on stage x 97 stalls seats | OperaRIR, https://doi.org/10.5281/zenodo.8096639 (CC BY-NC 4.0); directivity https://zenodo.org/records/10255555 | Simplified model from the published plan and section (Lokki et al. 2015), only seating and stage-house absorption calibrated on T30: T30 within 6 %; C80 +1.4 dB at 500 Hz - 1 kHz, +3.0 - 3.2 dB at 2 - 4 kHz (13 - 21 % within 1 dB), front rows 2 - 8 within 1 - 2 dB, row 17 +7.5 - 8.1 dB at 2 - 4 kHz; EDT 12 - 23 % short (post hoc, diagnostic) | [validation/opera_check.md](../validation/opera_check.md) |

Reference values: EDT 5 % and C80 1 dB from ISO 3382-1:2009 Annex A; IACC 0.075 as assumed in the thesis that
accompanies the Detmold data (no primary source checked).

## 5. Known weak spots

Each item comes from particular rooms and conditions. Where no other program was run on the same data (Detmold, Arvedi),
it is not known whether other programs show similar errors there.

- **Sound just above seat rows** (grazing incidence) behind the first row: 5 - 11 dB too loud and no seat dip (here
  about 500 Hz) without the optional seat-dip model (BRAS RS7). With it: 1.8 - 6.2 dB; the dip at 400 -
  500 Hz within 3 dB, but 315 Hz 5 - 7 dB too quiet (the simulated dip starts about a third octave low) and 200 Hz
  3 - 4 dB too loud; generic seats, two-dimensional, checked in one real hall with default seats (docs/MODEL_en.md,
  *Seat dip*). The deep notch at the lower edge of the dip is not explained (ruled out: 2-D approximation, block
  dimensions, surface absorption); read levels there qualitatively. Check such positions with measurements.
- **Early spaciousness** (IACC_E3) about 0.04 too low in a concert hall (Detmold; BRAS CR3 0.08, CR4 0.07). It was 0.11 low before the default option of 2026-11-13 that sets the interaural coherence of the early residual from the arrival directions of the scattered energy; the fix came from a post hoc diagnosis, so it is not a blind check. In exchange C80 in Detmold is 0.4 - 1.6 dB high (0.3 - 1.4 without the option) and EDT 3 - 15 % short (3 - 11 without); the earlier close agreement of C80 and EDT was partly the double-counted scattered energy (fixed 2026-11-12). The optional seat-dip model had narrowed the IACC_E3 deficit (0.15 -> 0.10, before the fixes; not repeated) but moves the first 15 ms further from the measurement at 200 - 315 Hz.
- **Early decay and direct / early balance near the stage** in a hall not used in development, modelled from published drawings (Arvedi, post hoc): EDT 14 - 30 % too long with T20 right; with directional loudspeakers C80 1.2 - 2.8 dB low and EDT 2 - 3 times too long at 2 - 4 kHz. Ruled out: aim (tilt -10 ... +5 deg), volume (model at 5206 m3), image-source order (3 instead of 2), scattering (0.05 to twice the value: EDT / T30 moves by 0.05 at most); a more detailed model with per-surface published absorption shortened the EDT error only below 1 kHz. In a small room with known absorber positions (Arni) the engine does give an EDT shorter than T30 (EDT/T30 0.87 - 0.95, measured 0.91 - 0.96; [validation/arni_check.md](../validation/arni_check.md)), so it is not a property of the engine as such. Open: the loudspeaker data (8020A for 8020C) and how seating returns a beam aimed at it ([validation/arvedi_check.md](../validation/arvedi_check.md)).
- **Flutter between parallel surfaces**: repeated reflections between finite panels are too weak at low
  frequencies with the default finite-reflector factor (RS3) and a ceiling-aisle flutter was underestimated in CR4.
- Diffraction from edge end points, third and higher orders, plates between 5 cm and a few tenths of a metre thick:
  not checked.
- **Coupled rooms joined by a narrow opening** (a door ajar): the late decay from the second room is about 13 dB too low (CR1,
  4.1 deg). Mark the second room with the mesh option `seeds`; results with a wide opening are good.
- **Material data matter more than the engine**: with the BRAS initial data, CR2 reverberates 30 - 35 % too short;
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
    python validation/rr_complex.py <BRAS folder> CR3 --coeffs initial   # CR2, CR3, CR4; then --table out/rs
    python validation/rr_coupled.py --extract <SuppPub2.pdf>; python validation/rr_coupled.py <BRAS folder>
    python validation/rr_lateral.py <BRAS folder> --fabian <FABIAN HRIR SOFA> --ku100 hrir/KU100.sofa
    python validation/detmold_kh.py ...                              # see the script's docstring

Outputs go to `out/` (not in the repository: they are derived from the measured data).
