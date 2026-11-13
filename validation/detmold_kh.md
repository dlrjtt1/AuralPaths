# Detmold Konzerthaus: simulated vs measured KU100 BRIRs (2026-11-10)

Data: Detmold SRIR database, Set C (loudspeaker orchestra on stage, dense receiver grid), Detmold University of
Music, https://zenodo.org/records/4116247 (CC BY 4.0). Model and assumptions: validation/detmold_kh.py (drawn hall from
the published plan and longitudinal section, seats located from measured direct-sound times, KH 120 as a generic
90 degree source, materials calibrated on the measured T30 of the omnidirectional IRs). Same head in both: Neumann
KU100 (the measurement's dummy head; the KU100 HRIR set in the simulation). 4 sources (S2, S3, S6, S7) x 34 seats =
136 pairs.

Calibration (T30, omnidirectional IRs, S2/S3 to 12 seats): -0.5 ... -2.7 % in all bands after 3 iterations.
Model volume 4221 m3 (published: about 4600 m3).

| metric | measured (mean) | simulated (mean) | mean difference | median abs. difference | within the reference value |
|---|---|---|---|---|---|
| IACC_L3 (80 ms - end, 500 Hz - 2 kHz) | 0.12 | 0.12 | -0.003 | 0.027 | 96 % (0.075) |
| IACC_E3 (0 - 80 ms, 500 Hz - 2 kHz) | 0.45 | 0.30 | -0.146 | 0.151 | 18 % (0.075) |
| IACC_L broadband | 0.16 | 0.27 | +0.110 | 0.113 | 19 % (0.075) |
| EDT 500 Hz / 1 kHz / 2 kHz | 1.46 / 1.41 / 1.16 s | 1.45 / 1.43 / 1.18 s | +0 / +2 / +3 % | 7 / 6 / 9 % | 35 / 45 / 27 % (5 %) |
| C80 500 Hz / 1 kHz / 2 kHz | 0.9 / 1.8 / 4.0 dB | 0.7 / 1.1 / 3.3 dB | -0.3 / -0.8 / -0.7 dB | 1.4 / 0.9 / 1.0 dB | 38 / 51 / 51 % (1 dB) |

Reference values: EDT 5 % and C80 1 dB from ISO 3382-1:2009 Annex A; IACC 0.075 as assumed in Sahin (2017), the
thesis that accompanies Set C (no primary source checked).

Reading:
- Late spaciousness per band agrees (IACC_L3). The broadband IACC_L is higher in the simulation because broadband
  IACC weights low frequencies, where the interaural coherence is high, and the simulated source is flat while the
  measured IRs contain the KH 120 response; per band the values agree.
- Early IACC (IACC_E3) is too low in the simulation: the simulated first 80 ms are interaurally less similar than
  measured, i.e. too much early lateral energy relative to the frontal direct sound. The section shows diffusers and
  loudspeaker panels on the side walls ("Diffusoren", "Lautsprecher"), modelled here as flat walls with an assumed
  scattering; the KH 120 directivity is a generic model. Not resolved.
- EDT agrees on average (bias 0 ... +3 %), with scatter of 5 - 9 % per pair; C80 is 0.3 - 0.8 dB lower in the
  simulation (slightly less clear).

## With the seat-dip model (2026-11-11)

Same configuration with `"geometry": {"seat_dip": {"on": true, "preset": "standard"}}` (docs/MODEL_en.md, *Seat
dip*): generic seats, row spacing 0.80 m by default (the Detmold row spacing is not given in the documentation used
here), back 0.80 m, opening 0.10 m; the seat dimensions were not fitted. Both runs with the current code, 136 pairs,
measured metrics as above.

| metric | measured | without seat dip: simulated / mean diff. / within ref. | with seat dip: simulated / mean diff. / within ref. |
|---|---|---|---|
| IACC_E3 | 0.45 | 0.30 / -0.146 / 18 % | **0.35 / -0.097 / 38 %** |
| IACC_E broadband | 0.43 | 0.41 / -0.015 / 66 % | 0.47 / +0.047 / 63 % |
| IACC_L3 | 0.12 | 0.12 / -0.003 / 96 % | 0.12 / -0.003 / 96 % |
| C80 500 Hz / 1 kHz / 2 kHz | 0.9 / 1.8 / 4.0 dB | -0.26 / -0.76 / -0.71 dB; 38 / 51 / 51 % | **-0.19 / -0.19 / +0.24 dB**; 38 / 49 / 58 % |
| EDT 500 Hz / 1 kHz / 2 kHz | 1.46 / 1.41 / 1.16 s | +0 / +2 / +3 %; 35 / 45 / 27 % | -0 / -1 / -6 %; 35 / 42 / 27 % |

Spectrum of the first 15 ms (direct sound and early reflections, third-octave bands 80 Hz - 2 kHz, each pair's mean
removed; the measured IRs contain the KH 120 response, the same in both runs; `early_spec.py` and `cmp_early.py`
in out/detmold_sd, not in the repository):

| | 80 - 160 Hz | 200 - 315 Hz | rms shape error (median of the pairs) |
|---|---|---|---|
| measured - simulated, without seat dip | -3.9 ... -1.5 dB | -3.3 ... -1.8 dB | 4.7 dB |
| measured - simulated, with seat dip | -1.9 ... -0.4 dB | -4.2 ... -3.6 dB | 5.0 dB |

Reading: with the seat-dip model the early IACC deficit shrinks from 0.15 to 0.10 and the C80 bias from up to
0.8 dB to 0.2 dB; the early spectrum gets closer to the measurement below 160 Hz and further away at 200 -
315 Hz, and its overall shape error is about the same. The seat dimensions are defaults, not Detmold's; the result is
a check of the default model in one hall, not evidence that it reproduces this hall's seat dip.

The seat-dip column is from T on 5.9 Hz bins (2026-11-11, later the same day). With the earlier 23 Hz bins it was:
IACC_E3 -0.090 (40 % within), C80 -0.12 / -0.13 / +0.30 dB, EDT -1 / -2 / -7 %, early-spectrum shape error 4.9 dB,
i.e. the finer grid changes the Detmold results by less than their spread over the pairs.

## After the directional-source fixes (2026-11-12)

Two engine changes found in the Arvedi diagnostic (CHANGELOG, 2026-11-12) affect this check, whose KH 120 sources are
directional and whose BRIRs are made from one multi-receiver run per source (`brir_proto.energy_hists`): (1) the
emission direction of every image source had been taken from the first receiver of the run; (2) the ray-traced energy
had been scaled by 1 / Q at all times instead of following the pattern in the launch direction. Same configuration
(`out/detmold/config_cal.json`, calibration unchanged: it uses the omnidirectional IRs), without seat dip, 136 pairs,
measured metrics as above. The seat-dip run was not repeated.

| metric | measured | before: simulated / mean diff. / within ref. | after: simulated / mean diff. / within ref. |
|---|---|---|---|
| IACC_E3 | 0.45 | 0.30 / -0.146 / 18 % | 0.29 / -0.154 / 15 % |
| IACC_L3 | 0.12 | 0.12 / -0.003 / 96 % | 0.12 / +0.002 / 94 % |
| IACC_L broadband | 0.16 | 0.27 / +0.110 / 19 % | 0.29 / +0.134 / 15 % |
| C80 500 Hz / 1 kHz / 2 kHz | 0.9 / 1.8 / 4.0 dB | -0.26 / -0.76 / -0.71 dB; 38 / 51 / 51 % | +0.06 / +0.20 / +0.61 dB; 51 / 55 / 45 % |
| EDT 500 Hz / 1 kHz / 2 kHz | 1.46 / 1.41 / 1.16 s | +0 / +2 / +3 %; 35 / 45 / 27 % | -2 / -2 / -3 %; 35 / 36 / 26 % |

Reading: the C80 bias moves from 0.3 - 0.8 dB low to 0.1 - 0.6 dB high (the early reflections of the aimed
loudspeakers are now stronger), within the 1 dB reference on average either way; EDT stays within 3 % on average.
The early-IACC deficit is unchanged: it does not come from the directivity handling.

## After the diffuse-rain fix (2026-11-12, later)

The pyroomacoustics ray tracer had counted scattered energy twice (CHANGELOG; `validation/check_rays_energy.py`):
reflected energy 1 - 3.5 dB too strong wherever surfaces scatter. Recalibrated (T30 within 3.2 % after 4 iterations;
before the fix the same materials gave a T30 3.7 - 12.9 % too short at the start, i.e. the rain had lengthened the
decay), rendered and compared again, 136 pairs, without seat dip.

| metric | measured | before (directional fixes only) | after the rain fix |
|---|---|---|---|
| IACC_E3 | 0.45 | 0.29 / -0.154 / 15 % | **0.34 / -0.106 / 35 %** |
| IACC_E broadband | 0.43 | | 0.42 / -0.001 / 62 % |
| IACC_L3 | 0.12 | 0.12 / +0.002 / 94 % | 0.13 / +0.011 / 92 % |
| C80 500 Hz / 1 kHz / 2 kHz | 0.9 / 1.8 / 4.0 dB | +0.06 / +0.20 / +0.61 dB; 51 / 55 / 45 % | +0.31 / +0.68 / +1.39 dB; 49 / 46 / 34 % |
| EDT 500 Hz / 1 kHz / 2 kHz | 1.46 / 1.41 / 1.16 s | -2 / -2 / -3 %; 35 / 36 / 26 % | -3 / -6 / -11 %; 29 / 23 / 14 % |

Reading: the early-IACC deficit, unresolved before, shrinks from 0.15 to 0.11. C80 now comes out 0.3 - 1.4 dB high and
EDT 3 - 11 % short (most at 2 kHz): the earlier close agreement of C80 and EDT was partly the double-counted
scattered energy offsetting other errors of this model (assumed scattering, flat side walls without the diffusers,
generic KH 120 directivity). The browser engine never had the rain, so its accuracy in this hall corresponds to the
new values.

## Where the early interaural correlation is lost (2026-11-13, diagnostic)

`validation/detmold_iacc_diag.py`, sources S2 and S7, 68 pairs, octave bands 500 Hz - 2 kHz, current engine. IACC per
window after the direct sound; "discrete only" = image sources without the noise that carries the ray-traced energy
they do not explain (the residual, rendered with the diffuse-field interaural coherence).

| window | IACC measured | simulated | discrete only | residual share of the simulated energy | energy re 0 - 80 ms, measured / simulated |
|---|---|---|---|---|---|
| 0 - 20 ms | 0.79 | 0.63 | 0.82 | 34 % | -2.7 / -3.3 dB |
| 20 - 50 ms | 0.35 | 0.30 | 0.58 | 78 % | -5.6 / -5.2 dB |
| 50 - 80 ms | 0.30 | 0.29 | 0.61 | 91 % | -7.6 / -7.1 dB |
| 0 - 80 ms | 0.45 | 0.34 | 0.67 | 63 % | |

The energy per window agrees within 0.6 dB and the correlation after 20 ms within 0.05. The deficit is in the first
20 ms: a third of the energy there is residual, mostly the scattered part of the floor / seating reflection that
follows the direct sound by a few ms (seating scattering 0.6), and it is rendered as diffuse noise; measured, these
20 ms are as correlated as the image sources alone.

Tests (S2, 34 pairs; not in the engine): (a) residual rendered per window (0 - 20, 20 - 50, 50 - 110 ms) with the ear
energies and coherence of the arrival directions of the scattered ray energy (`dirrays.window_direction_energy`):
IACC 0 - 80 ms 0.35 -> 0.38 (measured 0.46), 20 - 50 ms 0.30 -> 0.35 (0.36), 0 - 20 ms 0.65 -> 0.67 (0.78). (b) as (a)
and the residual of the first 20 ms arriving from the direction of the source: 0 - 20 ms 0.78 (0.78), 0 - 80 ms 0.43
(0.46). (b) is an assumption fitted to this hall; it has not been checked in another hall.

## Cross-check of the early-direction option in BRAS CR3 and CR4 (2026-11-13)

`path_brir(..., ew=early_resid_directions(...))` (CHANGELOG): the early residual with the coherence of the arrival
directions of the scattered energy, the first 20 ms from the source direction. Same engine (diffuse rain off, residual
from the direct sound on), option off / on. BRAS: `validation/check_bras_brir.py --rays 5000 --k8-mps <K8 balloon>
--materials out/bras_cal16_CRn/config_cal.json [--early-dir]`, FABIAN HRIRs, listener MP6, five loudspeakers.

| hall | IACC_E3 measured | off | on | other measures, off -> on |
|---|---|---|---|---|
| Detmold (136 pairs) | 0.45 | 0.34 | 0.41 | C80 +0.3 / +0.7 / +1.4 -> +0.4 / +1.0 / +1.6 dB; EDT -3 / -6 / -11 -> -3 / -7 / -15 % |
| BRAS CR3 | 0.52 | 0.40 | 0.44 | |ILD difference| 0.8 -> 0.3 dB; ITD unchanged; C80 bias -1.1 ... +1.1 -> -0.9 ... +1.6 dB |
| BRAS CR4 | 0.83 | 0.75 | 0.76 | C80 bias -2.1 ... -0.1 -> -1.9 ... +0.7 dB; EDT -5 ... +18 -> -12 ... +19 % |

Early spaciousness moves towards the measurement in all three halls (most in Detmold, little in CR4), the direct
sound is unchanged, C80 and EDT stay within their earlier spread. The option is on by default where the directional
late field is (`brir_proto.early_dir_on`), and in the browser page since 2026-11-13 (`GEOM.rays` option `tEarly`;
`validation/check_early_dirs_pyjs.py`). For CR4 the earlier record
(`bras_brir_CR4_FABIAN_K8data_cal16.md`, before the diffuse-rain fix) had IACC_E3 0.66: most of the gain there came
from that fix.
