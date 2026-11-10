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
| Concert hall, 136 binaural source-seat pairs (Detmold Konzerthaus) | late spaciousness (IACC_L3) within 0.075 at 96 % of the pairs; EDT bias 0 - 3 %; C80 0.3 - 0.8 dB low | section 4 |
| Known weak spots | sound just above seat rows behind the first row: 5 - 11 dB too loud; early IACC too low | section 5 |

Shape error: rms over 1/3-octave bands of simulated minus measured level after removing the mean difference.
Mean abs. difference: absolute levels. The loudspeaker is modelled as a flat point source with its documented
calibration; the round-robin participants had the loudspeaker's directivity data, these runs do not.

## 2. The 2019 round robin

Brinkmann et al. (2019), "A round robin on room acoustical simulation and auralization", J. Acoust. Soc. Am. 145,
2746, https://doi.org/10.1121/1.5096178. Six programs took part (anonymous, letters A - F; B gave no results for
these scenes). AuralPaths did not take part; it is scored afterwards on the same figures. Their spectra in the supplementary material (SuppPub2) were read from the PDF's vector graphics and
scored against the measured curve of each figure; AuralPaths against the measured impulse response, with the same
windowing (the two measured curves agree within 0.1 - 0.9 dB).

| | A | C | D | E | F | AuralPaths |
|---|---|---|---|---|---|---|
| median shape error, dB (figures) | 2.3 (9) | 1.0 (15) | 2.8 (15) | 1.3 (13) | 1.4 (13) | **1.5** (15) |

Per figure: [validation/bras_rs.md](../validation/bras_rs.md), section 2.

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

With the default setting RS5 is 3.9 dB (mean abs.) and RS6 leaves 4 of 8 positions without sound; the options are
off by default because they cost time (up to tens of seconds per source-receiver pair). Details:
[validation/bras_rs.md](../validation/bras_rs.md), [validation/bras_rs5_engine.md](../validation/bras_rs5_engine.md).

## 4. Whole halls

| hall | data | result | details |
|---|---|---|---|
| Detmold Konzerthaus (about 600 seats), 4 stage sources x 34 seats, KU100 dummy head | Detmold SRIR database, https://zenodo.org/records/4116247 (CC BY 4.0) | IACC_L3 within 0.075 at 96 % of the pairs; IACC_E3 0.15 low on average (18 % within 0.075); EDT bias 0 - 3 % (27 - 45 % of the pairs within 5 %); C80 0.3 - 0.8 dB low (38 - 51 % within 1 dB); T30 within 2.7 % after calibration | [validation/detmold_kh.md](../validation/detmold_kh.md) |
| BRAS CR3 chamber music hall, CR4 auditorium (binaural, FABIAN head) | BRAS | direct-sound ITD within 5 us, 2 - 4 kHz spectrum within 1.4 dB; discrete reflections 14 - 70 ms after the direct sound: measured - model -1.1 dB (median, both halls); CR4 late IACC too low at seats under a flutter between ceiling panels and aisle | [validation/bras_brir_iacc_diag.md](../validation/bras_brir_iacc_diag.md) |
| Fratoni lecture hall (ULH) and domed hall (STC) | Fratoni et al. dataset | ULH within about 1 JND at 500 Hz - 4 kHz; STC T30 about 15 % too long (calibrate first in such halls) | [validation/](../validation/) `fratoni_*.md` |

Reference values: EDT 5 % and C80 1 dB from ISO 3382-1:2009 Annex A; IACC 0.075 as assumed in the thesis that
accompanies the Detmold data (no primary source checked).

## 5. Known weak spots

- **Sound just above seat rows** (grazing incidence) behind the first row: 5 - 11 dB too loud; the seat dip (here
  about 500 Hz) is not produced (BRAS RS7). Check such positions with measurements.
- **Early spaciousness** (IACC_E3) about 0.15 too low in a concert hall (Detmold); C80 slightly low.
- **Flutter between parallel surfaces**: repeated reflections between finite panels are too weak at low
  frequencies with the default finite-reflector factor (RS3) and a ceiling-aisle flutter was underestimated in CR4.
- Diffraction from edge end points, third and higher orders, plates between 5 cm and a few tenths of a metre thick:
  not checked.
- No listening test yet: these checks are physical, not perceptual.

## 6. Rerun it

Data: BRAS scene descriptions RS1 - RS7 and surface descriptions, Detmold SRIR database (download from the links
above). Then:

    python validation/bras_rs.py <BRAS folder> --scene RS2          # RS1 - RS4, RS6, RS7
    python validation/bras_rs5.py <BRAS folder> --variant thin+floor
    python validation/rr_extract.py <SuppPub2.pdf> out/rs/rr_curves.csv
    python validation/rr_compare.py
    python validation/detmold_kh.py ...                              # see the script's docstring

Outputs go to `out/` (not in the repository: they are derived from the measured data).
