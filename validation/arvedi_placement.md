# Arvedi: absorption placement and the shape of the early decay (2026-11-15, diagnostic)

Question: why is the simulated EDT of the omnidirectional source 15 - 30 % long although T20, T30 and C80 agree
(`arvedi_check.md`, `engine_js_halls.md`)? Already excluded: aim, volume, image-source order, scattering
coefficient, scattering model, engine. The page's engine through `engine_js.py`, 20000 rays, S0, 65 receivers.

## 1. Placement of the absorption (`validation/arvedi_placement.py`, fixed before the run)

Absorption of the surfaces near the source and the listeners (seating, stage, floor: 1089 m2) multiplied by r
relative to the rest (walls, ceiling, windows, shell: 3732 m2), a common factor per band recalibrated so that the
median T30 stays at the measured value (within 2 %). No coefficient reached the 0.01 / 0.95 limits.

| r | seating alpha at 1 kHz | wall alpha at 1 kHz | EDT bias 500 Hz / 1 kHz / 2 kHz | EDT / T30 at 500 Hz / 1 kHz / 2 kHz | C80 bias 500 Hz / 1 kHz / 2 kHz |
|---|---|---|---|---|---|
| 0.5 | 0.33 | 0.21 | +18.6 / +19.1 / +27.8 % | 1.07 / 1.06 / 1.07 | -0.5 / -0.1 / -0.7 dB |
| 0.71 | 0.41 | 0.19 | +17.2 / +18.3 / +27.3 % | 1.07 / 1.06 / 1.07 | -0.5 / -0.1 / -0.8 dB |
| 1 | 0.50 | 0.16 | +18.2 / +18.4 / +27.4 % | 1.07 / 1.06 / 1.06 | -0.6 / -0.1 / -0.8 dB |
| 1.41 | 0.59 | 0.14 | +16.1 / +16.8 / +25.7 % | 1.05 / 1.05 / 1.05 | -0.5 / -0.1 / -0.7 dB |
| 2 | 0.70 | 0.11 | +13.6 / +14.0 / +23.4 % | 1.03 / 1.02 / 1.02 | -0.2 / +0.2 / -0.5 dB |
| measured | | | | 0.92 / 0.90 / 0.84 | |

A factor of 4 in the placement moves the EDT bias by 5 points and EDT / T30 by 0.04; the measured ratio is 0.1 - 0.2
lower. The placement of the absorption, in this split, is not the cause.

## 2. Where in time the decays differ (`validation/arvedi_decay_shape.py`)

Mean over the 65 receivers of the unit-energy histograms from the direct sound on; calibrated config (r = 1).
Energy per window, simulated minus measured (dB):

| band | 0 - 5 ms | 5 - 20 ms | 20 - 50 ms | 50 - 80 ms | 80 - 120 ms | 120 - 200 ms | 200 - 300 ms | 300 - 500 ms |
|---|---|---|---|---|---|---|---|---|
| 250 Hz | +1.8 | +1.4 | -5.1 | -2.2 | -0.7 | -0.1 | +0.1 | +0.5 |
| 500 Hz | +0.6 | +1.7 | -3.8 | -1.9 | +0.1 | +0.2 | +0.2 | +0.4 |
| 1 kHz | +1.3 | +1.9 | -4.9 | -2.4 | -0.2 | +0.1 | +0.0 | +0.2 |
| 2 kHz | +1.6 | +1.2 | -5.3 | -2.9 | +0.3 | +0.5 | +0.3 | +0.6 |
| 4 kHz | +1.1 | +1.0 | -4.9 | -2.4 | +0.3 | +0.8 | +0.8 | +1.2 |

Backward-integrated decay of the mean histogram at 1 kHz, measured / simulated: 20 ms -2.3 / -3.6 dB, 50 ms
-3.6 / -4.2 dB, 80 ms -5.1 / -5.1 dB, 200 ms -10.1 / -10.1 dB, 500 ms -22.1 / -22.4 dB.

- From 80 ms on the two decays are the same within 0.3 dB (250 Hz - 2 kHz). The reverberant decay is right.
- The whole difference is in the first 80 ms: the simulation has 1 - 2 dB too much energy in the first 20 ms and
  4 - 5 dB too little at 20 - 50 ms, 2 - 3 dB too little at 50 - 80 ms. The sum up to 80 ms is the same, which is
  why C80 agrees.
- This is what makes EDT long: the simulated decay drops at once and then stays flat until 80 ms, the measured one
  falls steadily; a line fitted to 0 ... -10 dB is flatter on the first shape.
- So the measured hall returns reflections 20 - 80 ms after the direct sound (path differences of 7 - 27 m) that
  the model does not have, and the model has early energy (direct sound, floor / seating plane, first 20 ms) the
  hall does not. Candidates, not tested: surfaces missing or simplified in the model drawn from the published
  plans (balcony fronts, parapets, reflectors, the shape behind and above the stage); the seating plane as a
  specular reflector right after the direct sound.
- 125 Hz: the measured energy in 0 - 5 ms is 9 dB below the simulated one. The measured histograms come from
  octave-band-filtered RIRs, and at 125 Hz the filter spreads the direct sound over more than 5 ms; part of the
  C80 and D50 "error" at 125 Hz is this, not the room model (not quantified).

## Reading

The EDT error in Arvedi is an error of the early reflection pattern (which reflections arrive when in the first
80 ms), not of the absorption, the scattering or the engine's late field. A T30 + EDT calibration of the absorption
would not repair it. Comparing the decay in time windows, as here, is the direct check for any hall that has
measured RIRs.
