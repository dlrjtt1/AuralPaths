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

## S0, omnidirectional (B&K OmniPower 4292-L modelled as a point source)

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

## S1 - S4, Genelec 8020C (modelled with the 8020A manufacturer polars, aimed horizontally at the audience)

| source | EDT bias | C80 bias (dB) |
|---|---|---|
| S1 | +63% / +22% / +22% / +31% / +148% / +366% | -1.48 / +1.55 / -2.60 / -3.65 / -6.83 / -8.10 |
| S2 | +49% / +17% / +21% / +37% / +113% / +206% | -1.48 / +1.49 / -2.24 / -3.16 / -6.07 / -6.86 |
| S3 | +43% / +24% / +27% / +41% / +123% / +182% | -0.86 / +1.74 / -1.54 / -2.34 / -4.24 / -4.79 |
| S4 | +58% / +18% / +29% / +40% / +212% / +422% | -1.00 / +1.90 / -1.16 / -1.96 / -3.43 / -3.86 |

Measured, the loudspeakers give much more early energy than the dodecahedron at 2 - 4 kHz (C80 9 - 11 dB against
4 - 5 dB for S0, EDT 0.5 - 0.9 s against 1.1 - 1.3 s); the simulation hardly separates them (C80 3 - 7 dB).
Aim checked as a cause and ruled out: the C80 deficit at 4 kHz is as large on the loudspeaker axis (0 - 20 deg:
-7 to -9 dB for S1 / S2) as off it. Directivity is applied by the engine (one receiver: S1 C80 at 4 kHz 7.1 dB vs
S0 4.4 dB; diffuse share 1/Q = 0.13 at 4 kHz).

## Reading

- **Agrees:** decay (T20 within 3 %, 48 - 75 % of the receivers within one JND) and, for the omnidirectional source,
  the energy ratios at 250 Hz - 1 kHz (C80 bias -0.1 ... -0.9 dB, D50 within 0.04, Ts within 5 ms).
- **Does not agree:** the early decay. EDT is 17 - 32 % too long for S0 (measured EDT 1.1 - 1.5 s is clearly shorter
  than T30 1.4 - 1.6 s; simulated EDT is about T30), C80 1.3 - 1.5 dB low at 2 - 4 kHz, and for the directional
  loudspeakers the early / direct dominance at 2 - 4 kHz is missing (C80 3 - 8 dB low, EDT 2 - 5 times too long).
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
