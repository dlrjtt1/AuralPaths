# How accurate is AuralPaths? (benchmark against public measurements)

Last run: 2026-11-10, engine as of that date. Korean: [BENCHMARK_ko.md](BENCHMARK_ko.md), Japanese:
[BENCHMARK_ja.md](BENCHMARK_ja.md).

Every number on this page comes from public measured data and a script in this repository; anyone with the data can
rerun it (section 6). The measured data are not redistributed here. A good score on these scenes does not mean
that every hall is simulated equally well; the weak spots are listed in section 5.

## 1. Summary

| what | result | details |
|---|---|---|
| Spectra of 15 reference cases of the 2019 round robin (reflections on floors, plates, arrays, parallel plates) | median shape error **1.5 dB**; the five participating programs with results there scored 1.0 - 2.8 dB | section 2 |
| Single reflections and finite plates (BRAS RS1, RS2, RS4) | 1.2 - 3.4 dB mean abs. difference per 1/3-octave band | section 3 |
| Diffraction behind a partition and behind a thick body (BRAS RS5, RS6) | 2.6 dB (RS5), 2.3 - 2.8 dB (RS6) mean abs. difference, with the diffraction options of section 3 | section 3 |
| Rooms of the 2019 round robin (BRAS CR2 - CR4): T20, EDT, C80, D50 averaged over 10 source-receiver pairs, from the BRAS material data alone | mean error 2.2 - 4.0 JND; the six programs 1.3 - 6.4 JND (best of seven in CR3, second with C in CR4, sixth in CR2) | section 2.2 |
| Coupled rooms (CR1), energy decay at 1 kHz | door 30.4 deg: 7.6 dB with the BRAS initial data, 1.7 dB with the fitted data (programs 2.5 - 7.5 dB); door 4.1 deg: 6.6 - 8.2 dB, worse than every program (4.1 - 5.1 dB) | section 2.3 |
| Concert hall, 136 binaural source-seat pairs (Detmold Konzerthaus) | late spaciousness (IACC_L3) within 0.075 at 96 % of the pairs; EDT bias 0 - 3 %; C80 0.3 - 0.8 dB low | section 4 |
| Known weak spots | sound just above seat rows behind the first row: 5 - 11 dB too loud (3.4 - 6.7 dB off with the optional seat-dip model); early IACC too low; coupled rooms joined by a narrow gap (late decay 13 dB low) | section 5 |

Shape error: rms over 1/3-octave bands of simulated minus measured level after removing the mean difference.
Mean abs. difference: absolute levels. The loudspeaker is modelled as a flat point source with its documented
calibration; the round-robin participants had the loudspeaker's directivity data, these runs do not.

### Strengths and weaknesses at a glance

Strong:

- Direct sound and source direction: direct-sound ITD within a few microseconds; lateralization error 0.3 - 0.6 deg
  in the three round-robin rooms (programs A 0.2 - 0.8, B 1.0 - 1.2, E 0.6 - 0.9, C 7.2 - 14.2 deg).
- Tone colour of binaural responses: 1.4 dB in 37 gammatone bands in all three rooms (programs E 1.3, B and C 2.2,
  A 3.2 dB).
- Reverberation at low frequencies: T20 +34 % at 125 Hz and +7 % at 250 Hz, where the programs average +58 % and
  +35 %.
- Prediction from material data alone in medium and large halls: best of seven in CR3, second with C in CR4.
- Single reflections and finite plates: median shape error 1.5 dB (programs 1.0 - 2.8 dB).
- Late spatial impression: IACC_L3 within 0.075 at 96 % of 136 seats (Detmold).

Weak:

- Rooms coupled through a narrow opening: the late decay from the second room is about 13 dB too low (CR1, door
  4.1 deg), worse than every program.
- Small rooms with uncalibrated material data: CR2 reverberates 30 - 35 % too short (sixth of seven); calibrate to a
  measured reverberation time where one exists.
- Grazing sound over seat rows behind the first row: 5 - 11 dB too loud without the optional seat-dip model; with it
  (generic seats, 2-D) 3.4 - 6.7 dB, and the 500 Hz dip appears only in part (RS7).
- Early spatial impression in concert halls: IACC_E3 about 0.15 low; C80 slightly low (Detmold). With the seat-dip
  model (default seats) 0.09 low and C80 within 0.3 dB on average.
- High frequencies of binaural responses: 4 - 6 dB too much energy at 9 - 15 kHz.
- Shadowed positions behind objects need the slower diffraction options (section 3); with the defaults, four of
  eight positions behind the RS6 object receive no sound.

How to read this: the round-robin scores are a comparison after the fact (the participants submitted blind; here
the measurements were available). The tone-colour and lateralization rows use the fitted materials. All checks are
physical; whether the result sounds plausible (the paper's listening tests) has not been tested, and none of this
shows that laboratory findings carry over to a real hall or sound system.

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
| CR2 seminar room | 5.5 | 1.8 | 3.0 | 1.9 | 3.5 | 3.3 | **4.0** |
| CR3 chamber music hall | 6.4 | 4.9 | 3.6 | 2.9 | 4.4 | 4.6 | **2.8** |
| CR4 auditorium | 3.5 | 4.3 | 2.2 | 1.3 | 2.5 | 2.4 | **2.2** |

In CR2 the reverberation is 30 - 35 % too short from 250 Hz up with the initial data. With the BRAS "fitted" data
(absorption adjusted to the measured reverberation times, so not a prediction) the score is 2.3 (CR2) and 1.2 (CR3).
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
| RS7 source in sight / behind the first block, with the seat-dip model | 4 / 4 | 3.2 - 3.8 / 3.2 - 4.1 dB | 3.0 - 3.3 / 3.4 - 6.7 dB | `seat_dip` on (settings scaled to the 1:3.2 set-up; `validation/rs7_seatdip_bem.py`) |

With the default setting RS5 is 3.9 dB (mean abs.) and RS6 leaves 4 of 8 positions without sound; the options are
off by default because they cost time (up to tens of seconds per source-receiver pair). Details:
[validation/bras_rs.md](../validation/bras_rs.md), [validation/bras_rs5_engine.md](../validation/bras_rs5_engine.md).

## 4. Whole halls

| hall | data | result | details |
|---|---|---|---|
| Detmold Konzerthaus (about 600 seats), 4 stage sources x 34 seats, KU100 dummy head | Detmold SRIR database, https://zenodo.org/records/4116247 (CC BY 4.0) | IACC_L3 within 0.075 at 96 % of the pairs; IACC_E3 0.15 low on average (18 % within 0.075); EDT bias 0 - 3 % (27 - 45 % of the pairs within 5 %); C80 0.3 - 0.8 dB low (38 - 51 % within 1 dB); T30 within 2.7 % after calibration. With the seat-dip model (default seats): IACC_E3 0.09 low (40 % within 0.075), C80 -0.1 ... +0.3 dB | [validation/detmold_kh.md](../validation/detmold_kh.md) |
| BRAS CR3 chamber music hall, CR4 auditorium (binaural, FABIAN head) | BRAS | direct-sound ITD within 5 us, 2 - 4 kHz spectrum within 1.4 dB; discrete reflections 14 - 70 ms after the direct sound: measured - model -1.1 dB (median, both halls); CR4 late IACC too low at seats under a flutter between ceiling panels and aisle | [validation/bras_brir_iacc_diag.md](../validation/bras_brir_iacc_diag.md) |
| Fratoni lecture hall (ULH) and domed hall (STC) | Fratoni et al. dataset | ULH within about 1 JND at 500 Hz - 4 kHz; STC T30 about 15 % too long (calibrate first in such halls) | [validation/](../validation/) `fratoni_*.md` |

Reference values: EDT 5 % and C80 1 dB from ISO 3382-1:2009 Annex A; IACC 0.075 as assumed in the thesis that
accompanies the Detmold data (no primary source checked).

## 5. Known weak spots

- **Sound just above seat rows** (grazing incidence) behind the first row: 5 - 11 dB too loud and no seat dip (here
  about 500 Hz) without the optional seat-dip model (BRAS RS7). With it: 3.0 - 6.7 dB, the dip only in part (400 -
  500 Hz still 5 - 7 dB too loud, 200 Hz 8 - 9 dB too loud), generic seats, two-dimensional, not yet checked in a
  real hall (docs/MODEL_en.md, *Seat dip*). Check such positions with measurements.
- **Early spaciousness** (IACC_E3) about 0.15 too low in a concert hall (Detmold); C80 slightly low. The optional
  seat-dip model narrows this to 0.09 and C80 to within 0.3 dB, but moves the first 15 ms further from the
  measurement at 200 - 315 Hz.
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
