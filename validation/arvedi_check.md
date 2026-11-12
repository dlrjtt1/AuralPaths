# Arvedi Auditorium, Cremona: check on a hall not used in development (2026-11-11 / 12)

Data: "The Sound of the Violin's Home" (Politecnico di Milano), https://doi.org/10.5281/zenodo.20098848 (CC BY 4.0):
65 receivers (8-capsule array), 5 stage sources. Protocol, deviations and the reasons for them:
[arvedi_protocol.md](arvedi_protocol.md). Model: [arvedi_model.py](arvedi_model.py) (from the published drawings),
check: [arvedi_check.py](arvedi_check.py). Outputs in out/ (not in the repository).

**Status: post hoc, not blind.** The blind run (protocol items 1 - 12) placed the receivers on the wrong side of the
stage (item 13) and is void. The run below uses the placement documented with the dataset and was made after the blind
results had been seen; nothing in the model was fitted to the measured RIRs except the absorption (on the measured
T30 of S0, as planned) and the ring-row floors in front of the receivers (from the documented receiver heights).

Model volume 4680 m3 (published 5300 m3). Calibration (S0, all receivers): simulated T30 within 2 % in all bands after
three iterations (initial BRAS CR3 materials: 7 - 73 % too long).

## Current engine (2026-11-12, after three fixes; post hoc)

Recomputed with all three engine fixes of 2026-11-12 (CHANGELOG): emission direction per receiver, rays launched with
the source pattern, and pyroomacoustics' diffuse rain switched off (it counted scattered energy twice and made the
reflected energy 1 - 3.5 dB too strong). Same model and procedure as below (post hoc placement, uniform calibration on
the T30 of S0: within 1.5 % after 3 iterations). Out/arvedi_posthoc_norain. The sections after this one are the
earlier engine and are kept as the record.

Bias per band, 125 Hz / 250 / 500 / 1 k / 2 k / 4 kHz:

| run | EDT | T20 | C80 (dB) | D50 |
|---|---|---|---|---|
| S0 omnidirectional | +20 / +18 / +15 / +14 / +21 / +30 % | -1 / +3 / +2 / +0 / -0 / +2 % | +2.38 / +0.19 / -0.57 / -0.05 / -0.59 / -0.85 | +0.29 / +0.06 / +0.01 / +0.05 / +0.04 / +0.01 |
| S0 seat dip | +20 / +18 / +16 / +15 / +22 / +30 % | -1 / +3 / +1 / +0 / -0 / +2 % | +2.14 / +0.30 / +0.19 / +0.13 / -0.33 / -0.62 | +0.27 / +0.06 / +0.06 / +0.06 / +0.06 / +0.03 |
| S0 4292-L polars | +21 / +19 / +15 / +16 / +17 / +27 % | -2 / +1 / -1 / -3 / -2 / +0 % | +2.41 / +0.23 / -0.49 / -0.16 / -0.60 / -0.95 | +0.29 / +0.06 / +0.02 / +0.04 / +0.02 / -0.01 |
| S1 Genelec | +65 / +22 / +20 / +20 / +79 / +196 % | +5 / -2 / -2 / -3 / -5 / +1 % | -0.82 / +2.20 / -0.65 / -0.51 / -2.07 / -2.83 | +0.06 / +0.22 / -0.01 / -0.00 / -0.06 / -0.07 |
| S2 | +49 / +17 / +19 / +28 / +98 / +124 % | +7 / +5 / -1 / -0 / -0 / +4 % | -1.07 / +2.01 / -0.71 / -0.54 / -1.86 / -2.14 | +0.08 / +0.22 / +0.00 / +0.03 / -0.03 / -0.03 |
| S3 | +41 / +24 / +25 / +33 / +97 / +98 % | +4 / +1 / +0 / +0 / +1 / +6 % | -0.52 / +2.14 / -0.56 / -0.33 / -1.40 / -1.38 | +0.11 / +0.24 / +0.02 / +0.04 / -0.01 / -0.01 |
| S4 | +62 / +20 / +24 / +26 / +86 / +134 % | +6 / -1 / -2 / -3 / -4 / +0 % | -0.49 / +2.56 / -0.29 / -0.02 / -1.20 / -1.74 | +0.08 / +0.25 / +0.02 / +0.03 / -0.02 / -0.03 |

Share of the 65 receivers within one JND, S0: EDT 6 - 26 %, T20 45 - 78 %, C80 46 - 72 % (250 Hz - 4 kHz), D50 35 -
49 %. Loudspeakers: C80 12 - 55 %, D50 40 - 89 % (500 Hz - 4 kHz).

Reading:
- **Omnidirectional source:** C80 within 1 dB at 250 Hz - 4 kHz (before the fixes -1.3 ... -1.5 dB at 2 - 4 kHz), D50
  within 0.06, T20 within 3 %. EDT remains 14 - 30 % long: the measured EDT is clearly shorter than T30, the
  simulated one is not.
- **Loudspeakers:** C80 within 0.7 dB at 500 Hz - 1 kHz; at 2 - 4 kHz still 1.2 - 2.8 dB low and EDT 2 - 3 times too
  long, less than before (3 - 8 dB, 2 - 5 times). Not explained by the aim (tilt -10 ... +5 deg: within 0.35 dB), the
  volume (5206 m3 model: no improvement) or the image-source order (3 instead of 2: no change) (`arvedi_sens.py`,
  run with the engine before the rain fix). Remaining candidates: the loudspeaker data (8020A for 8020C, polars read
  off plots, blend between the two planes), and how the seating returns energy of a beam aimed at it.
- **125 - 250 Hz** behave differently in the measurement for all sources; not reproduced.
- Change between sources (S_k - S0, `arvedi_delta.py`): C80 at 500 Hz - 1 kHz within 0.5 dB on average; at
  2 - 4 kHz the simulated change is 1 - 2 dB smaller than measured (+5 ... +6 dB); EDT changes not reproduced.

## S0, omnidirectional (B&K OmniPower 4292-L modelled as a point source) (earlier engine)

Bias = simulated - measured (relative for EDT / T20); "within" = share of the 65 receivers within one JND (ISO
3382-1 Annex A: EDT, T20 5 %, C80 1 dB, D50 0.05, Ts 10 ms).

| metric | 125 Hz | 250 Hz | 500 Hz | 1 kHz | 2 kHz | 4 kHz |
|---|---|---|---|---|---|---|
| EDT measured / simulated | 1.47 / 1.73 | 1.33 / 1.60 | 1.35 / 1.56 | 1.36 / 1.62 | 1.25 / 1.58 | 1.14 / 1.49 |
| EDT bias, within 1 JND | +23%, 18 % | +22%, 9 % | +17%, 22 % | +20%, 6 % | +28%, 3 % | +32%, 2 % |
| T20 measured / simulated | 1.67 / 1.64 | 1.45 / 1.48 | 1.44 / 1.45 | 1.49 / 1.51 | 1.46 / 1.48 | 1.35 / 1.38 |
| T20 bias, within 1 JND | -1%, 48 % | +3%, 58 % | +0%, 74 % | +1%, 63 % | +2%, 75 % | +3%, 72 % |
| C80 measured / simulated | 0.33 / 2.49 | 3.14 / 3.01 | 4.08 / 3.19 | 3.53 / 2.86 | 4.21 / 2.88 | 4.85 / 3.32 |
| C80 bias, within 1 JND | +2.15 dB, 15 % | -0.14 dB, 66 % | -0.89 dB, 55 % | -0.66 dB, 63 % | -1.33 dB, 35 % | -1.54 dB, 34 % |
| D50 measured / simulated | 0.29 / 0.56 | 0.55 / 0.58 | 0.60 / 0.59 | 0.56 / 0.58 | 0.58 / 0.58 | 0.62 / 0.60 |
| D50 bias, within 1 JND | +0.27, 0 % | +0.04, 54 % | -0.00, 38 % | +0.02, 65 % | +0.00, 45 % | -0.02, 57 % |
| Ts measured / simulated | 111.03 / 81.51 | 74.15 / 72.46 | 65.32 / 69.70 | 72.08 / 74.28 | 67.98 / 73.43 | 59.25 / 67.90 |
| Ts bias, within 1 JND | -29.52 ms, 9 % | -1.70 ms, 75 % | +4.38 ms, 62 % | +2.20 ms, 77 % | +5.45 ms, 45 % | +8.65 ms, 52 % |

Variants (bias per band, 125 Hz - 4 kHz):

| run | EDT | C80 (dB) |
|---|---|---|
| S0 omnidirectional | +23% / +22% / +17% / +20% / +28% / +32% | +2.15 / -0.14 / -0.89 / -0.66 / -1.33 / -1.54 |
| S0 with the seat-dip model (default seats; rows taken as straight across the hall) | +23% / +22% / +18% / +20% / +28% / +32% | +1.95 / -0.03 / -0.24 / -0.53 / -1.15 / -1.41 |
| S0 with the 4292-L horizontal polars (B&K data sheet BP 1689) | +23% / +22% / +17% / +19% / +27% / +31% | +2.15 / -0.14 / -0.89 / -0.71 / -1.64 / -1.83 |
| void blind run, S0 (wrong side of the stage) | +24% / +25% / +21% / +21% / +31% / +36% | +1.77 / -0.54 / -1.40 / -1.15 / -1.95 / -2.24 |

## S1 - S4, Genelec 8020C (modelled with the 8020A manufacturer polars, aimed horizontally at the audience; earlier engine)

Recomputed 2026-11-12 after two engine fixes (the third, the diffuse rain, came later; see the first section) for directional sources (see the last section; CHANGELOG). Bias per band,
125 Hz - 4 kHz; in brackets the first post hoc run, before the fixes.

| source | EDT bias | C80 bias (dB) | D50 bias |
|---|---|---|---|
| S1 | +63% / +22% / +20% / +22% / +96% / +243% (+63 / +22 / +22 / +31 / +148 / +366 %) | -1.14 / +1.79 / -1.06 / -1.19 / -2.81 / -3.70 (-1.48 / +1.55 / -2.60 / -3.65 / -6.83 / -8.10) | +0.04 / +0.21 / -0.02 / -0.03 / -0.08 / -0.09 |
| S2 | +49% / +17% / +19% / +30% / +97% / +140% (+49 / +17 / +21 / +37 / +113 / +206 %) | -1.36 / +1.65 / -1.10 / -1.18 / -2.57 / -2.96 (-1.48 / +1.49 / -2.24 / -3.16 / -6.07 / -6.86) | +0.07 / +0.20 / -0.02 / -0.00 / -0.05 / -0.06 |
| S3 | +42% / +24% / +21% / +29% / +94% / +100% (+43 / +24 / +27 / +41 / +123 / +182 %) | -0.72 / +1.85 / -0.88 / -0.93 / -2.17 / -2.13 (-0.86 / +1.74 / -1.54 / -2.34 / -4.24 / -4.79) | +0.10 / +0.22 / -0.00 / +0.01 / -0.04 / -0.03 |
| S4 | +56% / +16% / +19% / +23% / +103% / +182% (+58 / +18 / +29 / +40 / +212 / +422 %) | -0.71 / +2.24 / -0.61 / -0.63 / -1.91 / -2.43 (-1.00 / +1.90 / -1.16 / -1.96 / -3.43 / -3.86) | +0.06 / +0.24 / -0.00 / +0.00 / -0.04 / -0.05 |

T20 within 7 % for all four. Measured, the loudspeakers give much more early energy than the dodecahedron at 2 - 4 kHz
(C80 9 - 11 dB against 4 - 5 dB for S0, EDT 0.5 - 0.9 s against 1.1 - 1.3 s). Before the fixes the simulation hardly
separated them; now it does, but not fully: C80 1.9 - 3.7 dB low and EDT 2 - 3.4 times too long at 2 - 4 kHz. The
earlier one-receiver test (S1 C80 at 4 kHz 7.1 dB vs S0 4.4 dB) had been right; the 65-receiver runs were not (fix 1).

## Reading (earlier engine)

- **Agrees:** decay (T20 within 3 %, 48 - 75 % of the receivers within one JND) and, for the omnidirectional source,
  the energy ratios at 250 Hz - 1 kHz (C80 bias -0.1 ... -0.9 dB, D50 within 0.04, Ts within 5 ms).
- **Does not agree:** the early decay. EDT is 17 - 32 % too long for S0 (measured EDT 1.1 - 1.5 s is clearly shorter
  than T30 1.4 - 1.6 s; simulated EDT is about T30), C80 1.3 - 1.5 dB low at 2 - 4 kHz, and for the directional
  loudspeakers the early / direct dominance at 2 - 4 kHz is too weak (after the fixes of 2026-11-12: C80 1.9 - 3.7 dB
  low, EDT 2 - 3.4 times too long; before: 3 - 8 dB, 2 - 5 times).
- **125 Hz** behaves differently in the measurement (S0: C80 0.3 dB, D50 0.29, Ts 111 ms); the model does not
  reproduce it.
- **Not known which cause.** Candidates, not tested: early reflections the simplified model leaves out (the curved
  wooden shells round the front rows, the parapet round the stage, stair and step faces, the balcony fronts; the
  receivers are 3 - 7 m from the stage centre); the calibration scaling every material by the same factor per band;
  the 12 % smaller volume and flat ceiling. In Detmold (drawn hall, end stage) the EDT bias was 0 - 3 %.
- **What this means for use.** In a hall modelled from published drawings without a calibrated early-reflection
  structure, reverberation and mid-frequency energy ratios can be expected; the early decay and the direct / early
  balance at high frequencies near the stage cannot. These are the quantities a precedence-effect study controls, so
  stimuli for such a study should use halls whose early reflections are checked against measurements.

## Detailed diagnostic run and two engine fixes (2026-11-12, after the results above)

Protocol item 15: parapets, the lip of the high block and the pit walls added to the model; materials per surface
from published values instead of a uniform calibration (seating: Gade, Springer Handbook of Acoustics ch. 9,
table 9.3, after Beranek; other surfaces: BRAS initial estimates). Out/arvedi_detail. Diagnostic, not a check.

**Prediction without calibration (S0).** T20 +23 ... +60 % at 125 Hz - 1 kHz, within 5 % at 2 - 4 kHz; EDT +24 ...
+75 %; C80 -0.4 ... -2.3 dB. **Seating-only calibration** (`calibrate.py --adjust aud`) stopped after iteration 2:
the seating reached the 0.95 limit at 125 Hz - 1 kHz with T30 still +21 ... +35 % long (2 - 4 kHz within 2 %).
With the published values for the hard surfaces and the seating as the only free absorber, the model cannot reach
the measured reverberation below 2 kHz: absorption is missing that neither the drawings nor the material values
show (or the volume or the engine is off; not separated here). The comparisons below use the seating at that limit
(set by hand from the iteration's factors; recorded in config_cal.json).

| run (bias 125 Hz / 250 / 500 / 1 k / 2 k / 4 kHz) | T20 | EDT | C80 (dB) | D50 |
|---|---|---|---|---|
| S0, uncalibrated | +60 / +45 / +31 / +23 / +2 / -5 % | +75 / +53 / +37 / +30 / +24 / +24 % | -0.41 / -1.97 / -2.32 / -1.57 / -1.39 / -1.16 | +0.14 / -0.06 / -0.08 / -0.03 / -0.00 / -0.01 |
| S0, seating at its limit | +7 / +10 / +5 / +1 / -3 / -3 % | +20 / +20 / +16 / +12 / +22 / +28 % | +2.21 / +0.04 / -0.68 / -0.03 / -1.18 / -1.47 | +0.27 / +0.05 / +0.01 / +0.05 / +0.01 / -0.02 |
| S0, seat dip | +7 / +10 / +5 / +1 / -3 / -3 % | +19 / +21 / +21 / +13 / +23 / +30 % | +1.94 / +0.23 / +0.28 / +0.25 / -0.94 / -1.29 | +0.26 / +0.06 / +0.06 / +0.06 / +0.03 / -0.01 |
| S0, 4292-L polars | +7 / +10 / +5 / +1 / -3 / -3 % | +20 / +20 / +16 / +12 / +21 / +26 % | +2.21 / +0.04 / -0.68 / -0.11 / -1.55 / -1.81 | +0.27 / +0.05 / +0.01 / +0.04 / -0.01 / -0.04 |
| S1 (after both fixes) | +24 / +9 / +5 / +6 / +3 / +5 % | +57 / +19 / +28 / +25 / +82 / +197 % | -0.75 / +2.25 / -0.48 / -0.02 / -2.20 / -2.84 | +0.06 / +0.23 / +0.00 / +0.02 / -0.06 / -0.06 |
| S2 | +25 / +15 / +6 / +6 / +4 / +6 % | +48 / +17 / +29 / +35 / +105 / +124 % | -0.75 / +2.29 / -0.35 / +0.06 / -2.05 / -2.22 | +0.10 / +0.24 / +0.02 / +0.04 / -0.04 / -0.04 |
| S3 | +14 / +6 / +5 / +3 / +6 / +9 % | +46 / +29 / +38 / +46 / +117 / +85 % | -0.21 / +2.42 / -0.24 / +0.18 / -1.64 / -1.42 | +0.13 / +0.26 / +0.03 / +0.06 / -0.02 / -0.01 |
| S4 | +16 / +6 / +3 / +1 / +3 / +6 % | +61 / +22 / +33 / +32 / +83 / +115 % | -0.42 / +2.69 / -0.02 / +0.54 / -1.26 / -1.65 | +0.08 / +0.27 / +0.03 / +0.05 / -0.02 / -0.03 |

S0: the detailed model shortens the EDT error at 125 Hz - 1 kHz (+12 ... +20 % instead of +17 ... +23 %) but not at
2 - 4 kHz (+22 ... +28 %), where T20 agrees; at 125 Hz - 1 kHz T30 stays 13 - 29 % long while T20 agrees (a slow
late decay the measurement does not have).

**Engine fixes found with the directional sources** (CHANGELOG, 2026-11-12). Splitting the simulated and measured
energy of S1 into direct sound, 3 - 80 ms and the rest (`validation/arvedi_diag_directional.py`) showed that the
simulated late share was the same for S1 and S0 (about -5 dB at 4 kHz) while the measured one fell from -6 to
-12 dB. Two causes: (1) in a run with several receivers the emission direction of every image source had been taken
from the first receiver (S1, receiver A109 on the loudspeaker axis: direct sound -16.8 dB in a three-receiver run,
-9.7 dB alone; the one-receiver test quoted above was therefore right and the 65-receiver runs were not); (2) the
ray-traced energy of a directional source had been scaled by 1 / Q at all times, which keeps the early-to-late ratio
of the rays at its omnidirectional value; rays now leave the source with the pattern's energy in their launch
direction. S1 C80 bias at 500 Hz / 1 / 2 / 4 kHz: -2.60 / -3.65 / -6.83 / -8.10 dB (first post hoc run) -> -0.76 /
-0.73 / -3.58 / -4.96 dB (fix 1) -> -0.48 / -0.02 / -2.20 / -2.84 dB (both). Detmold recomputed
([detmold_kh.md](detmold_kh.md)).

Remaining for the loudspeakers: C80 1.3 - 2.8 dB low and EDT 1.8 - 3 times too long at 2 - 4 kHz. The measured
decay there is dominated by the direct sound (C80 9 - 11 dB, EDT 0.5 - 0.8 s), where EDT reacts strongly to a small
error of the direct-to-reverberant ratio. Inputs not known: 8020A data for the 8020C, the aim (horizontal, from a
photo), the 11 % smaller model volume. 250 Hz: measured C80 of the loudspeakers 1 - 2 dB, simulated 3 - 4 dB, in all
four; not investigated.

## Early decay and scattering (2026-11-13, post hoc, diagnostic)

The measured EDT is shorter than T30 (EDT / T30 0.82 - 0.92, shortest at 2 - 4 kHz); the simulated one equals T30
(about 1.0), which is where the EDT error of S0 comes from (T30 within 3 %). Hypothesis tested: the model's scattering
spreads the early energy over the hard surfaces before it reaches the absorbing seating. `validation/arvedi_scatter.py`,
S0, 22 receivers, calibrated configuration of the current engine, scattering changed without recalibrating:

| variant | EDT / T30 simulated, 125 Hz - 4 kHz (measured 0.92 0.91 0.90 0.90 0.84 0.82) | EDT bias | T30 bias |
|---|---|---|---|
| as calibrated | 1.02 1.04 1.01 1.01 1.01 1.05 | +14 ... +30 % | +1 ... +3 % |
| seating scattering x 0.3 | 1.02 1.05 1.03 1.03 1.03 1.07 | +16 ... +33 % | +1 ... +3 % |
| all surfaces 0.05 | 1.02 1.05 1.01 1.00 1.01 1.08 | +18 ... +36 % | +1 ... +7 % |
| all surfaces x 2 (at most 0.99) | 0.98 1.00 0.98 0.98 0.98 0.99 | +7 ... +21 % | -3 ... +1 % |

Rejected: less scattering does not make the early decay faster; more scattering shortens EDT a little, but the ratio
stays at about 1.0 in every variant (it moves by 0.05 at most). Scattering is not what decides the shape of the decay
here. Remaining: the distribution of the absorption (the uniform calibration puts alpha 0.13 - 0.20 on the plaster
walls and ceiling; with the absorption concentrated on the seating, the detailed run gave a shorter EDT error below
1 kHz) and early reflecting surfaces the simplified model does not have. Not tested.
