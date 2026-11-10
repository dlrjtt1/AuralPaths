# BRAS RS5 (diffraction at a partition): the engine against the measurement and the round robin (2026-11-10)

Scene: BRAS reference scene RS5, a 25 mm MDF partition, 2.066 m high and 4.75 m wide, on the hard floor of a
hemi-anechoic chamber; 4 loudspeaker heights x 4 microphone heights, 11 of 16 pairs without line of sight (Aspoeck
et al., BRAS, https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0). Script: `validation/bras_rs5.py`. The
partition is given to the engine as geometry (a box of five faces on a floor face), not as a hand-built half-plane
as in `validate_bras.py`.

Post-processing as in the round robin (Brinkmann et al. 2019, https://doi.org/10.1121/1.5096178, SuppPub2
section 5): Hann window -6 / -3 ms to 30 / 40 ms around the detected direct-sound peak. The source is a flat point
source with the documented calibration (0.4 Pa at 1 m); the Genelec 8020c response and directivity are not
modelled (no data in this folder), so absolute levels carry the loudspeaker's tolerance, and the pairs with LS4
(0.135 m above the floor, tilted 34.6 degrees up) carry its directivity most.

## 1. What the engine did before

The convex edges of the partition box were found (two right-angle edges 25 mm apart on top, two on each side), but
first-order diffraction from one of them is blocked by the box itself for any receiver behind it. Result: **no
sound at 10 of the 11 positions without line of sight.** The earlier RS5 check (`validate_bras.py`, README) used a
hand-built half-plane with floor images and therefore did not show this.

## 2. Changes (both engines, `diffraction.py` and `engine_geom.js`, checked against each other)

- **Thin-plate edges** (default on): two faces back to back closer than 5 cm (`THIN_M`) end in one edge with
  exterior angle 2 pi (n = 2) on their mid line; the wedges of the thin end face are dropped. Edges resting on a
  surface that extends beyond both faces (a panel standing on the floor) are not edges.
- **Diffraction combined with one specular reflection before and/or after the edge** (opt-in:
  `"geometry": {"diffraction_refl": 1}`; Python `diffract(..., refl_order=1)`, browser `diffract(..., 1)`).
  Image source / image receiver, reflection point checked on the face and for occlusion; faces whose plane holds
  the edge are left out (their reflections are already the UTD reflection terms). In the drawn fan hall example the
  number of diffracted arrivals per pair goes from 11 to 269 (0.9 s per pair in Python), so it stays opt-in.
- Python vs browser on this geometry: 20 pairs, 144 arrivals, largest band-energy difference 2e-11
  (`tests/regression.py`, check `diffraction_plate`).

## 3. Measured vs simulated, 1/3-octave bands 125 Hz - 4 kHz (medians over pairs)

| variant | positions without line of sight with sound | level bias meas - sim | spectral shape error (rms, offset removed) | mean abs. difference |
|---|---|---|---|---|
| before | 1 of 11 | - | - | - |
| thin-plate edges | 11 of 11 | +0.9 dB | 3.6 dB (2.8 without LS4) | 3.9 dB (2.7) |
| + diffraction with floor reflections | 11 of 11 | -1.4 dB | 2.7 dB (2.4) | 2.6 dB (2.1) |
| + transmission through the partition (mass law) | 11 of 11 | -1.5 dB | 2.6 dB (2.6) | 2.7 dB (2.2) |

With line of sight (5 pairs) the last two variants give a shape error of 1.2 dB and a bias of -1.2 dB.

Transmission through the partition as a limp mass law (documented 18.56 kg/m2) changes nothing here: it is about
18 dB below the incident sound at 100 Hz and more above, so it is not added to the engine. It does not explain the
sound that arrives at the straight-line time at three floor-level pairs (noted in `docs/MODEL_en.md`); what does is
not known from these data.

Below about 125 Hz the measurement is 5 - 8 dB above the model (100 Hz band): the chamber's lower limit is 100 Hz
(BRAS documentation) and the 40 ms window resolves little there.

## 4. The two round-robin simulators that handled diffraction

The round robin shows spectra of "Simulation I" and "Simulation II" for three pairs (SuppPub2, figures S2-28 to
S2-30; the other participants submitted no valid result for this scene). The curves were read from the vector
graphics of the PDF (`validation/rr_extract_rs5.py`; reading checked against the measured curve computed here:
0.4 - 0.8 dB rms). Spectral shape error against the same measured curve, 1/3-octave bands 100 Hz - 2.5 kHz, rms
with the offset removed (each figure is normalised by the rms of the IR, so only the shape is comparable):

| pair | Simulation I | Simulation II | AuralPaths, thin-plate edges | AuralPaths, + floor reflections |
|---|---|---|---|---|
| LS1 - MP1 | 3.1 dB | 6.5 dB | 5.1 dB | 3.8 dB |
| LS2 - MP3 | 1.8 dB | 3.9 dB | 3.1 dB | 2.3 dB |
| LS4 - MP1 | 5.4 dB | 8.7 dB | 6.0 dB | 4.5 dB |

Both round-robin curves are smooth (no floor interference); with diffraction combined with floor reflections the
engine reproduces the interference pattern and is in the range of the better of the two simulators (better at
LS4 - MP1, worse at LS1 - MP1). Before this change it produced no sound at these three pairs.

## 5. What this does and does not show

- Established here: single-edge diffraction at a thin free-standing plate, combined with a reflecting floor, is
  modelled within about 2 - 3 dB per 1/3-octave band at 125 Hz - 4 kHz in this scene.
- Not tested: thick obstacles (two edges in sequence: RS6, seat dip RS7), finite plates and arrays (RS2, RS4),
  edges in a full hall. The BRAS scenes RS1 - RS4, RS6, RS7 and CR1 are needed for that.
- Assumptions: flat omnidirectional source (the measured loudspeaker is neither), hard faces in the UTD reflection
  terms, first-order UTD (two edges 25 mm apart merged into one).
