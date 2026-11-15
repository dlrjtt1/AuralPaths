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
page's engine: the seat-dip run and the runs with measured directivity (4292-L, Genelec 8020A), which the bridge
does not cover yet. (The script also ran S1 - S4 with the generic 90 degree pattern of the config; these are not the
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

## Detmold Konzerthaus (drawn hall), calibration only, 24 omnidirectional-microphone positions, 80000 rays

Factors 1.20 / 1.11 / 1.06 / 1.00 / 1.00 / 1.00 after one iteration (Python, median, 20000 rays: 0.94 / 0.83 / 0.76 /
0.71 / 0.76 / 0.79): the start materials already give the measured T30 at 1 - 4 kHz with the page's either-or
scattering (`detmold_js.md`). EDT at the calibration positions (not fitted): mean absolute error 11.3 % (Python
10.9 %). The binaural comparison of `detmold_kh.md` (136 pairs, KH 120) is not rerun: BRIRs are still rendered by
the Python engine.

## Reading

- In the 3-D halls the two engines give the same T30 with the same materials (Arvedi start values within 1.5 %) and
  the same conclusions; the differences (EDT 3 - 7 points in Arvedi, decay times 3 - 6 points in Arni) are of the
  size of the added specular paths and of one seed's noise, not separated here.
- In the drawn hall the calibrated absorption differs between the engines, as found in `detmold_js.md`.
- The documented numbers of `arvedi_check.md`, `arni_check.md`, `detmold_kh.md`, `docs/BENCHMARK_*` and
  `docs/VALIDITY_*` are still those of the Python engine.
