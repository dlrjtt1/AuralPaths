# OperaRIR, Finnish National Opera: a directional loudspeaker in a large hall (2026-11-13)

Question: with a directional loudspeaker of known directivity, does the engine get EDT and C80 right at 2 - 4 kHz in a
large hall? (Arvedi, Genelec 8020: simulated C80 1.2 - 2.8 dB too low at 2 - 4 kHz.)

Data and model (`validation/opera_model.py`, `validation/opera_check.py`):
- RIRs: OperaRIR, https://doi.org/10.5281/zenodo.8096639 (CC BY-NC 4.0; Alary & Politis, Forum Acusticum 2023,
  https://dael.euracoustics.org/confs/fa2023/data/articles/000833.pdf): two Genelec 8331A on 1.6 m stands on the empty
  stage (curtain up), 97 seats in the stalls (rows 2 - 17), Eigenmike; here the W channel of the 4th-order SN3D RIRs,
  reduced on the data side to octave-band energy histograms (`opera_hist.py`).
- Loudspeaker: Genelec 8331A, measured directivity, https://zenodo.org/records/10255555 (CC BY 4.0). The SOFA file
  declares cartesian receiver positions but holds azimuth / elevation / radius; read as such
  (`opera_check.balloon_8331a`; 2 kHz: -15 dB at 90 deg, -20 dB at 180 deg). Aimed horizontally at the audience
  (assumption).
- Geometry: plan and section of Lokki et al., Proc. IOA 37 Pt. 3 (2015), Figure 1,
  https://users.aalto.fi/~ktlokki/Publs/p6_2015.pdf, read off the vector drawing; seats and sources from the dataset.
  Simplified: balconies as solid rings, upper walls on the stalls outline, ceiling by distance from the stage only,
  no lighting bridges or reflectors, pit covered, stage house 26 m high with the wings closed, no seat rows (the
  seating is a sloped absorbing plane). Volume of the model 19 300 m3 (hall and stage house).
- Calibration: absorption of the seating and of the stage house, one factor per band, on the mean T30 of Source2 at
  every 4th seat (4 runs, within 3 - 10 %); result seating 0.61 - 0.72, stage house 0.28 - 0.37. Then both sources at
  all seats: 5000 rays, image sources order 1.

## Results (194 seat x source pairs)

| | 125 | 250 | 500 | 1k | 2k | 4k Hz |
|---|---|---|---|---|---|---|
| T30 bias | +3 % | 0 % | +1 % | +2 % | -1 % | -6 % |
| EDT bias | -8 % | -15 % | -12 % | -20 % | -23 % | -12 % |
| EDT / T30 measured | 1.02 | 0.98 | 0.87 | 0.88 | 0.92 | 0.90 |
| EDT / T30 simulated | 0.90 | 0.86 | 0.80 | 0.75 | 0.95 | 1.03 |
| C80 bias | +1.7 | +2.1 | +1.4 | +1.4 | +3.2 | +3.0 dB |
| C80 within 1 dB | 18 % | 19 % | 21 % | 21 % | 13 % | 13 % |
| D50 bias | +0.13 | +0.09 | +0.04 | +0.03 | +0.10 | +0.07 |

C80 bias by row (dB, both sources):

| row | 2 | 4 | 5 | 6 | 7 | 8 | 11 | 14 | 17 |
|---|---|---|---|---|---|---|---|---|---|
| 500 Hz | -0.7 | +0.5 | -0.9 | +0.9 | +1.0 | +1.4 | +2.2 | +2.7 | +3.6 |
| 1 kHz | +0.1 | +0.7 | +0.4 | +0.9 | +0.6 | +0.9 | +1.9 | +2.6 | +3.8 |
| 2 kHz | +0.1 | +1.3 | +2.3 | +2.1 | +1.5 | +2.9 | +4.8 | +5.2 | +7.5 |
| 4 kHz | -0.9 | +0.8 | +2.2 | +1.8 | +1.8 | +2.8 | +4.7 | +5.5 | +8.1 |

- Here the simulation has too much early energy, the opposite sign of Arvedi; there is no single directional
  high-frequency bias of the engine. With the measured directivity, the simulated C80 at 2 - 4 kHz is still off by
  more than 1 JND at most seats.
- Rows 2 - 8 are within about 1 - 2 dB, the error grows with the distance from the stage, strongest at 2 - 4 kHz
  (+7.5 / +8.1 dB at row 17). The direct sound relative to the late energy (after 200 ms) is 5 - 11 dB stronger in
  the simulation from row 5 on at 2 - 4 kHz, and the simulation has almost no energy in the first 5 - 10 ms after the
  direct sound where the measurement has a continuous early part. One reading (tested below, not supported): sound grazing
  over the seat rows is attenuated in the hall and the model has no seat rows (the weak spot "sound grazing over the seating"
  of docs/BENCHMARK); propagation across audience seating: Schultz & Watters 1964,
  https://scholar.google.com/scholar?q=Propagation+of+sound+across+audience+seating+Schultz+Watters. The simplified
  geometry (no lighting bridges or reflectors over the front stalls, solid balcony rings) is another candidate.
- T30 after calibration within 6 %, as expected.

## Seat-row experiment (`--seats`, 2026-11-14)

Test of the reading above: backrests as thin strips on every row (`opera_model.seat_rows`: rows on the circles fitted
to the measured seats, 1.7 cm residual, row spacing 0.945 m; strip 0.25 m behind the seat position, 0.9 m above the
floor, assumptions fixed before the run; same absorption as the seating). Recalibrated (aud, stage), then both sources
at all seats, 10000 rays, image sources order 1 (`out/opera_seats2/`). A first run with 5000 rays did not converge in
T30 (+6 ... +28 %) and is not used: its longer decay alone lowered C80.

| | 125 | 250 | 500 | 1k | 2k | 4k Hz |
|---|---|---|---|---|---|---|
| T30 bias | -9 % | -11 % | -1 % | -1 % | -4 % | 0 % |
| C80 bias | +2.5 | +2.6 | +1.5 | +1.8 | +3.6 | +3.0 dB |
| C80 bias without seat rows | +1.7 | +2.1 | +1.4 | +1.4 | +3.2 | +3.0 dB |

C80 bias by row, median (dB), without / with seat rows:

| row | 2 | 4 | 5 | 6 | 7 | 8 | 11 | 14 | 17 |
|---|---|---|---|---|---|---|---|---|---|
| 2 kHz without | +0.1 | +1.3 | +2.9 | +2.1 | +1.4 | +3.8 | +5.0 | +4.7 | +8.0 |
| 2 kHz with | +0.5 | +1.8 | +1.8 | +1.6 | +4.1 | +3.6 | +5.6 | +6.0 | +9.0 |
| 4 kHz without | -0.5 | +1.1 | +2.5 | +2.1 | +1.8 | +4.3 | +5.2 | +5.6 | +8.4 |
| 4 kHz with | -0.6 | +0.9 | +1.0 | +1.0 | +3.9 | +2.7 | +5.0 | +5.4 | +9.3 |

- The seat rows do not remove the C80 bias that grows with the distance from the stage; at rows 11 - 17 it stays at
  +5 ... +9 dB at 2 - 4 kHz. The direct sound is not blocked (ears 1.2 m, backrests 0.9 m above the floor; 1 of 194
  pairs loses more than 10 dB at 1 kHz), and geometric strips without diffraction do not model the attenuation of
  sound grazing over seating. So the reading is not supported in this form; it is not ruled out for a wave-based
  model of the seating.
- Changes of a few dB at single rows (5 - 8) with and without the strips are within the scatter of the ray tracer at
  these seats (the calibration still moved T30 by up to 20 % between iterations at 10000 rays; one seat at row 17 gives
  no usable EDT fit).
- Left open: the simplified geometry above the front stalls (lighting bridges, reflectors) and the balconies.

## Engine seat-dip model (`--seat-dip`, 2026-11-14)

The engine's seat-dip model (`seatdip.py`: 2-D BEM of rigid seat rows along the path, after Davies & Cox 2000,
https://salford-repository.worktribe.com/output/1466149/reducing-seat-dip-attenuation; solved up to 1 kHz, above that
the mean of the last third octave) on the direct sound, row spacing 0.945 m, otherwise defaults; calibration of the
first run reused (the model changes only the direct sound and the first-order reflections from the seating), 5000 rays
(`out/opera_dip/`). Row 2 gets no seat dip (fewer than 2 rows in front of it in the model).

| | 125 | 250 | 500 | 1k | 2k | 4k Hz |
|---|---|---|---|---|---|---|
| C80 bias, seat-dip model | +1.4 | +1.7 | +1.7 | +2.3 | +4.3 | +4.1 dB |
| C80 bias, without | +1.7 | +2.1 | +1.4 | +1.4 | +3.2 | +3.0 dB |
| direct-sound gain of the model, rows 4 / 8 / 11 / 17 | -3.4 / -2.9 / -2.9 / -1.5 | -1.7 / -2.0 / -3.5 / -6.7 | +1.9 / +1.6 / +0.8 / -0.4 | +2.7 / +3.6 / +3.6 / +1.9 | +2.7 / +3.5 / +3.7 / +1.8 | same as 2k dB |

- The model lowers C80 by 0.2 - 0.5 dB at 125 - 250 Hz (the seat dip) and raises it by 0.9 - 1.1 dB at 1 - 4 kHz;
  the growth with the row stays (row 17: +9.0 / +9.3 dB at 2 / 4 kHz). Above 500 Hz the transfer function of rigid
  rows adds the floor reflection in phase (+2 ... +4 dB) where the image-source model had it reduced by the seating
  absorption; at 2 - 4 kHz this is the extrapolated 1 kHz value. So the model does not describe the attenuation of
  grazing sound above 1 kHz in this hall (rigid, empty rows; no absorption of the upholstery in the BEM).

Status: post hoc (the model was built after the measured means were looked at), diagnostic. Derived histograms,
the balloon and simulated results stay in `out/opera/` (not in the repository; the RIRs are CC BY-NC).

## Absorbing seats, 2-D BEM up to 4 kHz (`validation/seat_bem_hf.py`, 2026-11-14)

The seat-dip cross-section of the engine (same seat shape, row spacing 0.945 m) solved up to 4 kHz with a locally
reacting impedance on the seat pan top, the front and the top of the back (assumption). Absorption per band = the
calibrated seating absorption of this hall (0.61 - 0.72, from T30, not from C80), converted to a real impedance with
the Paris formula; both roots (soft zeta 0.4 - 0.5, stiff zeta 5 - 7). Source2, the most central seat of rows 4 - 17,
10 frequencies per octave band. Absorption set to zero reproduces the engine's BEM (same values to 0.01 dB).

Energy gain of the direct path (|T|^2, dB), rigid / soft / stiff:

| row | 125 Hz | 1 kHz | 2 kHz | 4 kHz |
|---|---|---|---|---|
| 4 | -3.6 / -9.2 / -6.9 | +3.2 / +4.0 / +3.1 | -1.3 / -0.6 / -1.4 | +2.7 / +0.5 / +1.1 |
| 8 | -3.0 / -10.3 / -7.1 | +4.0 / +4.1 / +3.6 | -1.4 / 0.0 / -0.8 | +2.0 / +1.2 / +0.8 |
| 11 | -2.5 / -11.1 / -7.2 | +4.0 / +3.8 / +3.4 | +1.2 / +1.7 / +1.2 | +1.4 / +0.8 / +0.7 |
| 14 | -2.1 / -11.1 / -7.0 | +3.2 / +3.0 / +2.8 | +2.2 / +3.1 / +2.0 | +0.7 / +0.1 / +0.2 |
| 17 | -1.9 / -10.7 / -6.6 | +2.5 / +2.0 / +2.0 | +3.6 / +3.7 / +3.1 | +0.2 / -1.1 / -0.4 |

- Absorbing seats deepen the dip at 125 Hz but change the direct path at 2 - 4 kHz by at most 2 dB; the gain stays
  between -1.4 and +3.7 dB. The line of sight passes 0.47 - 0.56 m above the seat backs, about two first Fresnel-zone
  radii at 4 kHz (0.27 m at the row in front), so no strong high-frequency shielding is expected for this source
  height. Rows of infinite width (2-D) shield more than real seats with gaps; a 3-D model is not expected to give more
  attenuation (engineering argument, not tested).

## Direct, early and late energy by row (2026-11-14)

Measured and simulated levels of the direct sound (-1 ... +3 ms), 3 - 80 ms and after 80 ms, each relative to its own
mean over rows 2 - 4 (the RIRs share one measurement chain, so level differences between seats are meaningful;
assumption), measured minus simulated, dB:

| | row 4 | 6 | 8 | 11 | 14 | 17 |
|---|---|---|---|---|---|---|
| direct, 2 kHz, Source1 / Source2 | 0.0 / -0.1 | -0.6 / -0.6 | -1.0 / -0.9 | -1.2 / -0.6 | -1.0 / -1.0 | -2.8 / -3.1 |
| 3 - 80 ms, 2 kHz | -1.1 / -0.5 | -0.7 / -2.4 | -1.0 / -2.5 | -1.5 / -3.5 | -2.1 / -2.1 | -0.4 / -0.2 |
| after 80 ms, 2 kHz | -0.3 / +0.2 | +1.0 / -0.6 | +2.3 / +0.5 | +2.7 / +1.5 | +4.8 / +1.4 | +7.8 / +2.7 |

(4 kHz within 1 dB of 2 kHz; Source1 row 5 has a strong early reflection in the measurement, +7 dB, left out.)

- The measured direct sound falls with distance as the simulated one, within about 1 dB up to row 14 and 3 dB at
  row 17. The direct sound is not over-strong in the simulation; the reading "sound grazing over the seat rows is
  attenuated" (above) is not supported by the data.
- The C80 bias comes from the reflected sound: relative to the front rows the measurement has more energy after 80 ms
  further back (up to +8 dB at row 17, Source1) and less between 3 and 80 ms (1 - 4 dB, Source2). In the simulation
  the late energy falls more steeply with the distance from the stage than in the hall. Candidates, not tested: the
  balcony overhang over the rear stalls and the balconies as solid rings in the model, the coupling to the stage
  house, the scattering of the hall surfaces at 2 - 4 kHz (start values, not calibrated).
