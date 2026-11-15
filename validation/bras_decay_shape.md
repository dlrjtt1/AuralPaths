# BRAS CR3 / CR4: decay in time windows (2026-11-15, diagnostic)

`validation/bras_decay_shape.py`. The two BRAS halls whose 3-D model is part of the measurement database (Aspoeck
et al. 2020, https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0), the page's engine (`engine_js.py`), 20000
rays, omnidirectional source (dodecahedron), 2 loudspeaker x 5 microphone positions; absorption calibrated on the
measured T30 of the LS1 positions (median, within 2 % at 125 Hz - 4 kHz). Mean over the 10 pairs of the unit-energy
histograms from the direct sound on. Energy per window, simulated minus measured (dB):

CR3, chamber music hall:

| band | 0 - 5 ms | 5 - 20 ms | 20 - 50 ms | 50 - 80 ms | 80 - 120 ms | 120 - 200 ms | 200 - 300 ms | 300 - 500 ms |
|---|---|---|---|---|---|---|---|---|
| 250 Hz | +1.7 | -1.1 | -0.6 | +1.4 | -0.8 | -0.2 | +0.8 | +0.5 |
| 500 Hz | +1.0 | -0.7 | -0.3 | +0.3 | +0.2 | -0.2 | -0.0 | +0.5 |
| 1 kHz | +0.1 | -0.5 | -0.3 | -0.1 | +0.3 | +0.1 | +0.4 | +0.6 |
| 2 kHz | +0.5 | -0.2 | -0.1 | -0.4 | -0.2 | +0.1 | +0.7 | +1.1 |
| 4 kHz | -1.8 | +0.0 | +0.4 | +0.4 | +0.0 | +0.1 | +0.5 | +0.7 |

CR4, auditorium:

| band | 0 - 5 ms | 5 - 20 ms | 20 - 50 ms | 50 - 80 ms | 80 - 120 ms | 120 - 200 ms | 200 - 300 ms | 300 - 500 ms |
|---|---|---|---|---|---|---|---|---|
| 250 Hz | +1.8 | -2.1 | +1.0 | -1.1 | -0.7 | -0.5 | -0.3 | +0.1 |
| 500 Hz | -1.1 | -1.3 | +0.6 | -0.4 | +0.0 | +0.1 | +0.3 | +0.9 |
| 1 kHz | -0.4 | +0.7 | +0.7 | -0.2 | +0.1 | -0.6 | -0.1 | +0.1 |
| 2 kHz | +0.8 | +0.6 | +0.1 | -0.5 | -0.1 | -0.7 | +0.0 | +0.4 |
| 4 kHz | +0.0 | +0.9 | +0.5 | -0.6 | -0.1 | -0.6 | -0.0 | +0.4 |

Backward-integrated decay of the mean histogram, 500 Hz - 2 kHz, 20 - 300 ms: within 0.5 dB (CR3 up to 120 ms,
then up to +1.2 dB at 300 ms and +1.7 dB at 500 ms: the simulated tail is a little slower although T30 is fitted),
within 0.8 dB (CR4). The LS2 pairs alone (not used for the calibration) give the same picture in CR3 (20 - 50 ms
within 0.3 dB, 50 - 80 ms up to +1.3 dB at 500 Hz - 2 kHz).

Reading:
- With the geometry of the measured hall, the engine has the energy of the first 80 ms in the right time windows
  (within about 1.3 dB at 500 Hz - 4 kHz, mean over the positions) in both halls. With Detmold (drawn from plan and
  section, `detmold_js.md`) that makes three halls; Arvedi (-4 ... -5 dB at 20 - 50 ms, `arvedi_placement.md`) is
  the exception.
- So the Arvedi deficit is a property of that model (drawn from published plans and simplified), not of how the
  engine computes early reflections. Whether the missing surfaces are absent from the drawings or were simplified
  away in the model is not decided.
- Means over positions; single positions are not tested by this.
