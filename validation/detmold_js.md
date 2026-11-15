# Detmold with the browser engine: either-or scattering vs mixed direction (2026-11-15, diagnostic)

`validation/detmold_js.py` (conditions fixed before the run, see its head). Drawn Detmold hall with the start
materials of `detmold_kh.py`, `engine_geom.js` in Node, 80000 rays per source, one seed. Calibration as
`calibrate.py`: omnidirectional source, one factor per octave band on all materials, T30 of the 24
omnidirectional-microphone positions (S2, S3 to 12 seats), median, within 2 %. Evaluation at the same 24 positions
with the generic 90 degree loudspeaker of the hall check; measured T30 and EDT from `t30.csv`, measured C80 from the
omnidirectional IRs with the same functions. T30 is fitted (at these positions); EDT and C80 are not, but the
positions are those of the calibration. New engine option `GEOM.rays(..., { mix: true })`: mixed direction in a drawn
hall (off by default; the page does not use it).

Calibration (1 kHz): T30 with the start materials 1.50 s (either-or), 1.33 s (mixed direction), measured 1.54 s; the
Python engine with the same materials 1.34 - 1.39 s (`ray_noise.md`). Factor on the absorption 0.97 (either-or, one
iteration) and 0.72 (mixed, five iterations); Python 0.71 - 0.73. So the mixed direction is what separates the two
engines in a drawn hall (`timing.md`), not another difference between them.

Mean difference simulation - measurement, 24 positions (share within 1 JND):

| | browser, either-or | browser, mixed direction | Python (calibrated config of `detmold_r20000_median`) |
|---|---|---|---|
| EDT 500 Hz | +9.8 % (38 %) | +10.0 % (29 %) | +7.4 % (33 %) |
| EDT 1 kHz | +2.1 % (38 %) | +1.1 % (42 %) | -1.8 % (42 %) |
| EDT 2 kHz | +8.1 % (50 %) | -0.6 % (29 %) | +1.4 % (17 %) |
| EDT 4 kHz | +1.1 % (46 %) | -8.5 % (12 %) | -7.2 % (8 %) |
| C80 500 Hz | -0.3 dB (62 %) | -0.4 dB (79 %) | -0.6 dB (67 %) |
| C80 1 kHz | -0.0 dB (67 %) | -0.3 dB (75 %) | -0.3 dB (67 %) |
| C80 2 kHz | +0.7 dB (50 %) | +0.7 dB (50 %) | +0.7 dB (58 %) |
| C80 4 kHz | +0.8 dB (54 %) | +0.8 dB (54 %) | +0.9 dB (42 %) |
| T30 500 Hz / 1 kHz / 2 kHz (fitted) | +0.7 / +0.0 / +3.0 % | +0.5 / +0.9 / +1.1 % | +0.7 / -0.6 / -6.2 % |
| EDT / T30 at 500 Hz / 1 kHz / 2 kHz / 4 kHz (measured 0.92 / 0.99 / 0.93 / 0.94) | 1.00 / 1.00 / 0.98 / 0.93 | 1.01 / 0.99 / 0.93 / 0.87 | 0.99 / 0.98 / 1.03 / 0.95 |

125 Hz: EDT -12 %, C80 +1.0 ... +1.3 dB in all three. The Python config was calibrated at 20000 rays with one trace
per position and is evaluated here with one trace per source at 80000 rays (its T30 at 2 - 4 kHz is 6 - 7 % short).

Reading:
- Once each model is calibrated on T30 by itself, C80 is the same within 0.3 dB and EDT at 500 Hz - 1 kHz within
  3 points. Neither scattering model is closer to this measurement overall: at 2 kHz the mixed direction is closer
  in EDT (-0.6 against +8.1 %), at 4 kHz the either-or model (+1.1 against -8.5 %). One seed; the mean over 24
  positions at 80000 rays has a seed noise of roughly 1 % (EDT) and 0.1 dB (C80), per position 3 % and 0.5 dB
  (`timing.md`).
- The models differ in the absorption they need (factor 0.97 against 0.72 at 1 kHz). Materials calibrated with one
  model must not be used with the other.
- EDT at 500 Hz is 7 - 10 % long in all three, i.e. not a matter of the scattering model.
- No reason from this hall to change the page's default (either-or in drawn halls).

## Decay in time windows (`validation/detmold_decay_shape.py`, 2026-11-15)

As for Arvedi (`arvedi_placement.md`, section 2): mean over the 24 positions of the unit-energy histograms from the
direct sound on, loudspeaker as in the hall check, 80000 rays, the calibrated materials above. Energy per window,
simulated minus measured (dB), page default (either-or):

| band | 0 - 5 ms | 5 - 20 ms | 20 - 50 ms | 50 - 80 ms | 80 - 120 ms | 120 - 200 ms | 200 - 300 ms | 300 - 500 ms |
|---|---|---|---|---|---|---|---|---|
| 250 Hz | +4.2 | -3.2 | -0.1 | +0.2 | +0.3 | +0.3 | +0.3 | +0.2 |
| 500 Hz | +0.0 | +0.5 | -0.5 | +0.1 | -0.1 | -0.3 | +0.5 | +0.7 |
| 1 kHz | -0.3 | +0.3 | -0.2 | +0.7 | +0.2 | -0.6 | +0.1 | +0.0 |
| 2 kHz | +1.3 | -0.9 | -0.9 | +0.4 | -0.7 | -1.1 | -0.1 | +0.0 |
| 4 kHz | +1.1 | -1.2 | -0.5 | +0.7 | -0.5 | -1.4 | -0.2 | -0.0 |

Mixed direction: within 1.2 dB in every window at 500 Hz - 4 kHz as well. Backward-integrated decay of the mean
histogram, either-or: within 0.2 dB at 500 Hz - 1 kHz and 0.8 dB at 2 - 4 kHz from 20 to 500 ms.

- In this hall the mean energy of every window of the first 80 ms is right within about 1 dB at 500 Hz - 4 kHz;
  Arvedi has -4 ... -5 dB at 20 - 50 ms. The drawn (2.5-D) model holds the reflections that matter here: a hall
  with plain side walls, one floor rake and a ceiling, which the plan and the section describe.
- 125 - 250 Hz: the measured direct sound is spread over the first 20 ms (octave filter of the measured RIR, and
  at 250 Hz possibly the seat dip); not a statement about the room model.
- Means over 24 positions: the pattern at a single seat is not tested by this (EDT per position: 38 - 50 % within
  1 JND, table above).

## Binaural comparison with the BRIRs of the page (`validation/detmold_page.py`, 2026-11-15)

The 136 pairs of `detmold_kh.md` (S2, S3, S6, S7 x 34 seats, KU100), with BRIRs computed by the page itself in
headless Chromium (24 runs of three seats and two PA sources): drawn hall, the materials calibrated for the page's
engine above (`out/detmold_jscal`), loudspeakers as the page's PA sources (generic 90 degree pattern), embedded KU100
HRIRs, 50000 rays, image sources to order 3, page defaults. Compared with `detmold_kh.py compare` and the measured
metrics of the earlier run. Conditions fixed before the run; one run.

| metric | measured (mean) | page (mean) | mean difference | median abs. difference | within the reference value |
|---|---|---|---|---|---|
| IACC_E3 (0 - 80 ms, 500 Hz - 2 kHz) | 0.45 | 0.46 | +0.018 | 0.062 | 60 % (0.075) |
| IACC_L3 (80 ms - end, 500 Hz - 2 kHz) | 0.12 | 0.13 | +0.013 | 0.028 | 92 % (0.075) |
| IACC_E broadband | 0.43 | 0.50 | +0.070 | 0.079 | 49 % (0.075) |
| IACC_L broadband | 0.16 | 0.27 | +0.113 | 0.116 | 14 % (0.075) |
| EDT 500 Hz / 1 kHz / 2 kHz | 1.46 / 1.41 / 1.16 s | 1.42 / 1.38 / 1.10 s | -2.0 / -1.4 / -4.6 % | 9.2 / 7.8 / 10.2 % | 28 / 29 / 24 % (5 %) |
| C80 500 Hz / 1 kHz / 2 kHz | 0.9 / 1.8 / 4.0 dB | 0.9 / 2.3 / 4.9 dB | -0.06 / +0.53 / +0.90 dB | 1.37 / 0.79 / 1.01 dB | 33 / 60 / 49 % (1 dB) |

Python engine, current defaults (`detmold_kh.md`, `docs/BENCHMARK_en.md`): IACC_E3 0.04 low (54 % within), EDT
-3 / -7 / -15 %, C80 +0.4 ... +1.6 dB. The page is at least as close in every band mean; the scatter over the pairs
(median absolute differences of 8 - 10 % in EDT and about 1 dB in C80) is the same. The broadband IACC values are
high for the reason given in `detmold_kh.md` (flat simulated source against the KH 120 response).
