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
