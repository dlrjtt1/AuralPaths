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
| IACC_E3 | 0.45 | 0.30 / -0.146 / 18 % | **0.36 / -0.090 / 40 %** |
| IACC_E broadband | 0.43 | 0.41 / -0.015 / 66 % | 0.48 / +0.053 / 65 % |
| IACC_L3 | 0.12 | 0.12 / -0.003 / 96 % | 0.12 / -0.003 / 96 % |
| C80 500 Hz / 1 kHz / 2 kHz | 0.9 / 1.8 / 4.0 dB | -0.26 / -0.76 / -0.71 dB; 38 / 51 / 51 % | **-0.12 / -0.13 / +0.30 dB**; 38 / 47 / 57 % |
| EDT 500 Hz / 1 kHz / 2 kHz | 1.46 / 1.41 / 1.16 s | +0 / +2 / +3 %; 35 / 45 / 27 % | -1 / -2 / -7 %; 32 / 39 / 26 % |

Spectrum of the first 15 ms (direct sound and early reflections, third-octave bands 80 Hz - 2 kHz, each pair's mean
removed; the measured IRs contain the KH 120 response, the same in both runs; `early_spec.py` and `cmp_early.py`
in out/detmold_sd, not in the repository):

| | 80 - 160 Hz | 200 - 315 Hz | rms shape error (median of the pairs) |
|---|---|---|---|
| measured - simulated, without seat dip | -3.9 ... -1.5 dB | -3.3 ... -1.8 dB | 4.7 dB |
| measured - simulated, with seat dip | -1.8 ... -0.2 dB | -3.9 ... -3.5 dB | 4.9 dB |

Reading: with the seat-dip model the early IACC deficit shrinks from 0.15 to 0.09 and the C80 bias from up to
0.8 dB to 0.1 - 0.3 dB; the early spectrum gets closer to the measurement below 160 Hz and further away at 200 -
315 Hz, and its overall shape error is about the same. The seat dimensions are defaults, not Detmold's; the result is
a check of the default model in one hall, not evidence that it reproduces this hall's seat dip.
