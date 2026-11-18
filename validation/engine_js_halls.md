# Omnidirectional hall checks with the page's engine (2026-11-15)

The checks with an omnidirectional source, rerun with the browser engine through `engine_js.py` (`--engine js`, now
the default of `calibrate.py`, `arvedi_check.py`, `arni_check.py`). Fixed before the runs: the commands, models,
ray counts and positions of the documented runs; what differs is the engine and the combination of the calibration
positions (median instead of mean). "Python" is the documented run with pyroomacoustics. One seed each. In 3-D
halls the page's engine also adds the ray-guided specular paths of order 2 - 3 and image sources of order 2 (the
page's defaults); the Python runs had image sources of order 2 only.

## Arvedi Auditorium (3-D mesh), S0, 65 receivers, 20000 rays (post hoc placement, as `arvedi_check.md`)

T30 with the start materials: 2.83 / 2.09 / 2.10 / 2.26 / 2.01 / 1.47 s (125 Hz - 4 kHz); Python 2.82 / 2.08 / 2.08 /
2.23 / 1.99 / 1.48 s. Calibrated within 2.4 % after 2 iterations.

| bias, 125 / 250 / 500 / 1k / 2k / 4k Hz | page's engine | Python (`out/arvedi_posthoc_norain`) |
|---|---|---|
| EDT | +24 / +23 / +18 / +19 / +28 / +35 % | +20 / +18 / +15 / +14 / +21 / +30 % |
| T20 | -2 / +3 / +1 / +1 / +2 / +4 % | -1 / +3 / +2 / +0 / -0 / +2 % |
| C80 | +2.49 / +0.33 / -0.29 / +0.04 / -0.58 / -0.88 dB | +2.38 / +0.19 / -0.57 / -0.05 / -0.59 / -0.85 dB |
| D50 | +0.30 / +0.07 / +0.03 / +0.06 / +0.05 / +0.02 | +0.29 / +0.06 / +0.01 / +0.05 / +0.04 / +0.01 |
| share within 1 JND, EDT | 17 / 12 / 22 / 18 / 9 / 3 % | 17 / 25 / 26 / 26 / 11 / 6 % |
| share within 1 JND, C80 | 11 / 72 / 45 / 65 / 48 / 45 % | 18 / 66 / 51 / 72 / 46 / 51 % |

Same picture: T20 and C80 as before, EDT too long, by 3 - 7 points more than with pyroomacoustics. Not run with the
page's engine: the seat-dip run (seat dip in 3-D halls is not covered by the bridge); measured directivity: below. (The script also ran S1 - S4 with the generic 90 degree pattern of the config; these are not the
documented loudspeaker runs and are not reported.)

## Arni variable-acoustics room (3-D mesh), 37 states x 5 microphones, 10000 rays (as `arni_check.md`)

Calibration on the all-closed state: factors 3.90 / 1.31 / 2.97 / 3.41 / 4.09 / 6.00 (Python 4.01 / 1.35 / 3.07 /
3.63 / 4.39 / 6.47), within 2 % after 7 iterations.

| 185 pairs, 125 / 250 / 500 / 1k / 2k / 4k Hz | page's engine | Python (`out/arni`) |
|---|---|---|
| T30 bias | +14 / +25 / +10 / +4 / +3 / +1 % | +10 / +23 / +7 / -0 / -1 / -5 % |
| EDT bias | +3 / +22 / +7 / +2 / +1 / -2 % | +1 / +19 / +4 / -2 / -3 / -6 % |
| EDT / T30 simulated (measured 1.00 / 0.93 / 0.91 / 0.92 / 0.95 / 0.96) | 0.89 / 0.88 / 0.88 / 0.90 / 0.93 / 0.94 | 0.89 / 0.87 / 0.88 / 0.91 / 0.93 / 0.95 |
| C80 bias | +0.34 / -0.97 / +0.17 / +0.02 / +0.31 / -0.06 dB | +0.46 / -0.85 / +0.32 / +0.25 / +0.58 / +0.29 dB |
| C80 within 1 dB | 43 / 48 / 58 / 93 / 88 / 93 % | 40 / 49 / 55 / 91 / 80 / 92 % |
| EDT within 5 % | 26 / 12 / 29 / 60 / 77 / 48 % | 25 / 10 / 29 / 68 / 62 / 30 % |

Same picture; the decay times are 3 - 6 points longer (the states with open panels), C80 0.1 - 0.3 dB closer at
1 - 4 kHz.

Rerun on 2026-11-19 after the dropped-face fix (`validation/mesh_leak.md`; the 106 panel side faces are kept now):
factors 4.00 / 1.32 / 2.97 / 3.44 / 4.12 / 6.10; T30 bias +13 / +25 / +10 / +4 / +3 / +0 %, EDT bias +3 / +22 / +7 /
+2 / +0 / -2 %, C80 bias +0.40 / -0.96 / +0.17 / +0.04 / +0.32 / -0.01 dB, C80 within 1 dB 43 / 47 / 58 / 94 / 88 /
94 %, EDT within 5 % 24 / 11 / 30 / 63 / 77 / 41 %. OperaRIR (below) rerun the same day: histograms unchanged.

## Detmold Konzerthaus (drawn hall), calibration only, 24 omnidirectional-microphone positions, 80000 rays

Factors 1.20 / 1.11 / 1.06 / 1.00 / 1.00 / 1.00 after one iteration (Python, median, 20000 rays: 0.94 / 0.83 / 0.76 /
0.71 / 0.76 / 0.79): the start materials already give the measured T30 at 1 - 4 kHz with the page's either-or
scattering (`detmold_js.md`). EDT at the calibration positions (not fitted): mean absolute error 11.3 % (Python
10.9 %). The binaural comparison of `detmold_kh.md` (136 pairs, KH 120) is not rerun: BRIRs are still rendered by
the Python engine.

## Sources with measured directivity (added the same day, after `engine_js.py` got the table model)

Arvedi (as `arvedi_check.md`: 4292-L polars for S0, Genelec 8020A manufacturer polars for S1 - S4), 65 receivers,
bias at 500 Hz / 1 kHz / 2 kHz / 4 kHz:

| run | page's engine: EDT | page's engine: C80 | Python: EDT | Python: C80 |
|---|---|---|---|---|
| S0, 4292-L polars | +18 / +21 / +24 / +34 % | -0.29 / -0.15 / -0.24 / -0.64 dB | +15 / +16 / +17 / +27 % | -0.49 / -0.16 / -0.60 / -0.95 dB |
| S1 Genelec | +18 / +20 / +93 / +246 % | -0.51 / -0.59 / -2.25 / -3.03 dB | +20 / +20 / +79 / +196 % | -0.65 / -0.51 / -2.07 / -2.83 dB |
| S2 | +23 / +35 / +119 / +169 % | -0.55 / -0.58 / -2.10 / -2.55 dB | +19 / +28 / +98 / +124 % | -0.71 / -0.54 / -1.86 / -2.14 dB |
| S3 | +23 / +31 / +103 / +117 % | -0.40 / -0.35 / -1.59 / -1.63 dB | +25 / +33 / +97 / +98 % | -0.56 / -0.33 / -1.40 / -1.38 dB |
| S4 | +21 / +27 / +92 / +146 % | -0.16 / -0.12 / -1.49 / -1.93 dB | +24 / +26 / +86 / +134 % | -0.29 / -0.02 / -1.20 / -1.74 dB |

OperaRIR (as `opera_check.md`: Genelec 8331A balloon, 97 stalls seats, two sources, 5000 rays; seating and stage
house calibrated on T30, median), all 194 pairs, 125 / 250 / 500 / 1k / 2k / 4k Hz:

| | page's engine | Python (`out/opera`) |
|---|---|---|
| T30 bias | +8 / +1 / +3 / +2 / +2 / -0 % | +3 / -0 / +1 / +2 / -1 / -6 % |
| EDT bias | -7 / -18 / -19 / -26 / -28 / -18 % | -8 / -15 / -12 / -20 / -23 / -12 % |
| EDT / T30 simulated (measured 1.02 / 0.98 / 0.87 / 0.88 / 0.92 / 0.90) | 0.89 / 0.84 / 0.73 / 0.68 / 0.69 / 0.77 | 0.90 / 0.86 / 0.80 / 0.75 / 0.95 / 1.03 |
| C80 bias | +1.86 / +2.39 / +1.66 / +1.67 / +2.48 / +2.25 dB | +1.74 / +2.13 / +1.36 / +1.39 / +3.16 / +2.98 dB |
| C80 within 1 dB | 18 / 24 / 24 / 25 / 21 / 16 % | 18 / 19 / 21 / 21 / 13 / 13 % |

Same findings with both engines: loudspeakers at 2 - 4 kHz in Arvedi (C80 1.5 - 3 dB low, EDT 2 - 3.5 times long)
and the OperaRIR clarity (C80 1.7 - 2.5 dB high, EDT 18 - 28 % short) remain open (Arvedi: excluded from further checks since, see `arvedi_check.md`; with the measured K8 directivity in BRAS CR3 / CR4 C80 at 4 kHz is within 0.4 dB, `bras_brir_CR*_FABIAN_K8data_cal16.md`), a little worse or better by
0.2 - 0.7 dB depending on the band. A directional source is handled differently by the two (the page weights the
early ray energy per launch sector, Python every ray), which is one seed's noise plus that approximation here.
Fix made on the way: the bridge now passes the histogram length to the ray tracer (with `t_max` above 2.5 s the
histogram ended early and gave no criteria; none of the runs above this section used more than 2.5 s).

## Either-or scattering in the 3-D halls (`--mix either`, diagnostic; conditions fixed before the run)

The 3-D halls scatter by the mixed direction by default. Same runs with the either-or model of the drawn halls
(a reflection is specular or Lambert with probability s), each calibrated on T30 by itself.

Arvedi S0, 65 receivers (125 / 250 / 500 / 1k / 2k / 4k Hz):

| | mixed direction (default) | either-or |
|---|---|---|
| EDT bias | +24 / +23 / +18 / +19 / +28 / +35 % | +30 / +25 / +21 / +21 / +28 / +30 % |
| C80 bias | +2.49 / +0.33 / -0.29 / +0.04 / -0.58 / -0.88 dB | +2.35 / +0.53 / -0.03 / +0.35 / +0.04 / -0.10 dB |
| C80 within 1 JND | 11 / 72 / 45 / 65 / 48 / 45 % | 25 / 68 / 38 / 65 / 42 / 60 % |
| T20 bias | -2 / +3 / +1 / +1 / +2 / +4 % | +3 / +2 / -2 / -1 / -0 / +5 % |
| EDT / T30 simulated, 500 / 1k / 2k Hz (measured 0.92 / 0.90 / 0.84) | 1.08 / 1.08 / 1.08 | 1.11 / 1.08 / 1.08 |
| calibration factor | 1.69 / 1.37 / 1.42 / 1.50 / 1.35 / 1.06 | 1.62 / 1.37 / 1.43 / 1.50 / 1.38 / 1.08 |

Arni, 185 pairs (125 / 250 / 500 / 1k / 2k / 4k Hz):

| | mixed direction (default) | either-or |
|---|---|---|
| T30 bias | +14 / +25 / +10 / +4 / +3 / +1 % | +6 / +16 / +4 / -2 / -2 / -6 % |
| EDT bias | +3 / +22 / +7 / +2 / +1 / -2 % | +4 / +26 / +12 / +4 / +1 / -5 % |
| EDT / T30 simulated (measured 1.00 / 0.93 / 0.91 / 0.92 / 0.95 / 0.96) | 0.89 / 0.88 / 0.88 / 0.90 / 0.93 / 0.94 | 0.96 / 0.97 / 0.97 / 0.98 / 0.98 / 0.97 |
| C80 bias | +0.34 / -0.97 / +0.17 / +0.02 / +0.31 / -0.06 dB | +0.18 / -1.29 / -0.24 / -0.18 / +0.22 / +0.21 dB |
| C80 within 1 dB | 43 / 48 / 58 / 93 / 88 / 93 % | 49 / 36 / 50 / 93 / 91 / 95 % |
| calibration factor | 3.90 / 1.31 / 2.97 / 3.41 / 4.09 / 6.00 | 2.99 / 0.97 / 1.84 / 2.50 / 3.39 / 5.92 |

- Arvedi: the scattering model does not touch the EDT error. In both the simulated EDT is LONGER than T30 (ratio
  1.08), the measured one shorter (0.84 - 0.92). C80 at 2 - 4 kHz has less bias with the either-or model (-0.1
  against -0.9 dB at 4 kHz), the share within 1 JND does not move consistently.
- Arni: the mixed direction gives the measured relation of early to late decay (0.88 - 0.94, measured 0.91 - 0.96),
  the either-or model hardly any difference between them (0.96 - 0.98). T30 of the predicted states is off by
  about the same amount with opposite sign; C80 about the same.
- With Detmold (`detmold_js.md`, a tie): no model is closer to the measurements in all three halls. The only clear
  difference is the EDT / T30 ratio in Arni, in favour of the mixed direction. Defaults unchanged.

## Reading

- In the 3-D halls the two engines give the same T30 with the same materials (Arvedi start values within 1.5 %) and
  the same conclusions; the differences (EDT 3 - 7 points in Arvedi, decay times 3 - 6 points in Arni) are of the
  size of the added specular paths and of one seed's noise, not separated here.
- In the drawn hall the calibrated absorption differs between the engines, as found in `detmold_js.md`.
- The documented numbers of `arvedi_check.md`, `arni_check.md`, `detmold_kh.md`, `docs/BENCHMARK_*` and
  `docs/VALIDITY_*` are still those of the Python engine.
