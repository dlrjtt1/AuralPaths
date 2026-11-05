# BRAS CR3: measured RIRs vs AuralPaths (Python engine)

Data: Aspöck et al. (2020), *BRAS – Benchmark for Room Acoustical Simulation*, v3, https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0 (dodecahedron RIRs, positions, surface descriptions). Material set: fitted_estimates. This file is derived from BRAS and is CC BY-SA 4.0.

```
CR3: OBJ 2598 faces -> 2598 after decimation -> 2319 room-facing faces (279 dropped); room volume (voxels) 3188 m3 (BRAS documentation: 3330.6 m3)
surface areas (m2): ceiling 168.5, floor 342.2, plaster 449.7, seating 176.5, stagePanels 425.2, structuredPlaster 1171.6, windows 25.4; total 2759
Sabine / Eyring T (s), no air: 125 Hz 1.69 / 1.59, 250 Hz 1.55 / 1.46, 500 Hz 1.36 / 1.27, 1000 Hz 1.43 / 1.34, 2000 Hz 1.49 / 1.39, 4000 Hz 1.36 / 1.27
absorption: BRAS fitted_estimates; scattering at 1 kHz: ceiling 0.12, floor 0.07, plaster 0.07, seating 0.61, stagePanels 0.05, structuredPlaster 0.19, windows 0.05
[3D mesh] LS1: 5 receivers, 363 s
[3D mesh] LS2: 5 receivers, 394 s
calibration on LS1 (T30 sim / measured per band): 125 Hz 1.064, 250 Hz 1.037, 500 Hz 1.090, 1000 Hz 1.096, 2000 Hz 1.086, 4000 Hz 1.115
[3D mesh calibrated] LS1: 5 receivers, 368 s
[3D mesh calibrated] LS2: 5 receivers, 360 s
2.5D hall (depth axis = x, stage at small x; image sources order 2, no diffraction): 35 plan vertices, 166 surfaces, volume 3135.1 m3; positions moved into the 2.5D room: LS2 1.96->3.37
[2.5D] LS1: 5 receivers, 11 s
[2.5D] LS2: 5 receivers, 10 s
```

## Room criteria, mean over the 10 positions (simulated − measured, mean signed / mean absolute, in JND)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs 500–2k |
|---|---|---|---|---|---|---|---|---|
| EDT | measured (mean) | 1.60 | 1.36 | 1.34 | 1.31 | 1.24 | 1.05 | |
| | 3D mesh | +3.2 / 3.9 | +2.9 / 3.0 | +1.8 / 2.3 | +3.3 / 3.5 | +4.2 / 4.2 | +2.7 / 2.7 | 3.3 |
| | 3D mesh calibrated | +2.3 / 3.3 | +1.8 / 2.3 | -0.2 / 1.8 | +1.2 / 1.5 | +2.1 / 2.4 | -0.0 / 1.3 | 1.9 |
| | ↳ LS2 only (held out) | +1.8 / 2.4 | +1.6 / 2.2 | -1.3 / 1.7 | +0.8 / 1.3 | +1.7 / 1.8 | -1.0 / 1.6 | 1.6 |
| | 2.5D | +3.6 / 3.6 | +5.6 / 5.6 | +2.5 / 3.3 | +3.7 / 4.5 | +5.1 / 5.2 | +3.9 / 4.4 | 4.3 |
| T30 | measured (mean) | 1.63 | 1.45 | 1.30 | 1.34 | 1.32 | 1.06 | |
| | 3D mesh | +2.1 / 2.1 | +1.8 / 2.1 | +2.9 / 3.1 | +3.1 / 3.1 | +2.5 / 2.6 | +1.9 / 1.9 | 2.9 |
| | 3D mesh calibrated | +0.9 / 1.6 | +0.9 / 1.6 | +1.9 / 2.5 | +1.6 / 2.0 | +1.9 / 2.2 | +1.8 / 2.2 | 2.2 |
| | ↳ LS2 only (held out) | +1.0 / 1.7 | +2.2 / 2.4 | +3.7 / 4.3 | +3.0 / 3.1 | +3.7 / 3.7 | +2.7 / 3.0 | 3.7 |
| | 2.5D | +2.7 / 2.7 | +3.8 / 3.8 | +2.9 / 2.9 | +2.8 / 2.8 | +2.9 / 2.9 | +3.7 / 3.7 | 2.9 |
| C80 | measured (mean) | 0.59 | 0.86 | 1.47 | 1.71 | 1.59 | 3.24 | |
| | 3D mesh | -1.2 / 1.3 | -0.1 / 1.5 | -0.4 / 1.4 | -1.0 / 1.2 | -0.6 / 0.7 | -0.8 / 1.3 | 1.1 |
| | 3D mesh calibrated | -0.7 / 1.2 | +0.1 / 1.3 | +0.1 / 1.2 | -0.5 / 0.8 | -0.2 / 0.4 | -0.2 / 0.9 | 0.8 |
| | ↳ LS2 only (held out) | -1.1 / 1.5 | -0.4 / 0.8 | +0.8 / 1.3 | -0.0 / 0.8 | +0.1 / 0.3 | -0.3 / 1.1 | 0.8 |
| | 2.5D | -0.6 / 2.3 | -0.3 / 2.7 | -0.0 / 1.6 | -0.5 / 1.6 | -0.4 / 1.7 | -0.6 / 2.1 | 1.6 |
| C50 | measured (mean) | -2.66 | -1.16 | -1.21 | -1.16 | -1.50 | 0.37 | |
| | 3D mesh | -0.6 / 2.3 | -0.9 / 2.0 | -0.5 / 1.6 | -0.9 / 0.9 | -0.3 / 0.5 | -0.9 / 1.3 | 1.0 |
| | 3D mesh calibrated | -0.1 / 2.3 | -0.5 / 1.9 | +0.0 / 1.3 | -0.3 / 0.7 | +0.2 / 0.7 | -0.3 / 1.5 | 0.9 |
| | ↳ LS2 only (held out) | -0.0 / 2.9 | -0.9 / 1.3 | +0.1 / 1.0 | -0.3 / 0.9 | +0.5 / 0.7 | -0.4 / 1.7 | 0.9 |
| | 2.5D | +0.2 / 2.6 | -0.8 / 3.0 | +0.0 / 2.4 | -0.2 / 2.3 | +0.1 / 2.0 | -0.5 / 2.4 | 2.3 |
| Ts | measured (mean) | 111 | 97 | 94 | 92 | 91 | 70 | |
| | 3D mesh | +1.8 / 2.0 | +1.0 / 1.3 | +0.6 / 1.1 | +1.3 / 1.3 | +1.1 / 1.1 | +1.1 / 1.1 | 1.2 |
| | 3D mesh calibrated | +0.9 / 1.7 | +0.4 / 1.0 | -0.3 / 1.0 | +0.3 / 0.7 | +0.3 / 0.5 | +0.3 / 0.7 | 0.7 |
| | ↳ LS2 only (held out) | +1.3 / 1.8 | +0.6 / 1.0 | -0.7 / 1.2 | +0.2 / 0.8 | +0.0 / 0.3 | +0.3 / 1.0 | 0.8 |
| | 2.5D | +1.4 / 2.9 | +1.8 / 2.9 | +0.4 / 1.8 | +0.9 / 2.1 | +1.0 / 2.1 | +1.1 / 2.0 | 2.0 |

Measured Ts in ms; EDT / T30 in s; C80 / C50 in dB. JND: ISO 3382-1 Annex A.

## Early reflections (first-order image sources vs the measured RIR, 500 Hz–2 kHz)

Each predicted first-order reflection that is at least −15 dB re direct, at least 2 ms after the direct sound and 1.5 ms away from any other predicted one is compared with the measured energy in a 1 ms window at its predicted time (−0.2 … +0.8 ms), in dB re the same window on the direct sound. Controls: the measured level 2 ms later than predicted, and at random times 3–20 ms after the direct sound.

| model | reflections | predicted (median dB) | measured at predicted time | measured +2 ms later | measured at random times | predicted − measured (median / IQR dB) | correlation predicted vs measured |
|---|---|---|---|---|---|---|---|
| 3D mesh | 36 | -5.3 | -6.8 | -10.4 | -11.5 | +1.2 / +0.1 … +3.9 | 0.59 |
| 3D mesh calibrated | 36 | -5.3 | -6.8 | -10.4 | -11.5 | +1.2 / +0.1 … +3.9 | 0.59 |
| 2.5D | 27 | -5.6 | -12.0 | -10.6 | -11.5 | +3.9 / +3.4 … +8.3 | 0.30 |

Direct-sound arrival, measured onset − distance / c (ms): LS1-MP1 -0.07, LS1-MP2 +0.04, LS1-MP3 -0.21, LS1-MP4 -0.67, LS1-MP5 -0.10, LS2-MP1 -0.09, LS2-MP2 -0.27, LS2-MP3 -0.32, LS2-MP4 -0.60, LS2-MP5 -0.19

2.5D conversion (obj_to_hall.py, --preserve eyring):

```
{
 "preserve": "eyring",
 "groups": {
  "aud": {
   "mesh_area_m2": 955.1,
   "hall_area_m2": 539.8,
   "mesh_absorption_area_m2": [
    112.41,
    131.8,
    150.2,
    139.92,
    145.34,
    153.35
   ]
  },
  "wall": {
   "mesh_area_m2": 1218.6,
   "hall_area_m2": 585.2,
   "mesh_absorption_area_m2": [
    117.55,
    140.3,
    143.07,
    134.13,
    123.51,
    147.8
   ]
  },
  "ceil": {
   "mesh_area_m2": 585.3,
   "hall_area_m2": 489.4,
   "mesh_absorption_area_m2": [
    74.09,
    58.19,
    84.01,
    84.62,
    76.63,
    75.89
   ]
  }
 },
 "volume_mesh_m3": 3187.7,
 "n_plan_vertices": 35,
 "n_floor": 76,
 "n_ceil": 57,
 "n_surfaces_2p5d": 166,
 "dims_m": [
  14.85,
  28.85,
  11.012
 ],
 "volume_2p5d_m3": 3135.1
}
```
