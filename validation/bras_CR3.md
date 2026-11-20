# BRAS CR3: measured RIRs vs AuralPaths (page's engine; 2.5D hall and energy histograms through engine_js.py)

**Computed with the page's engine since 2026-11-20** (`validate_bras_cr.py`, default `--engine js`): the energy histograms of the 3D mesh and of the 2.5D hall come from the engine of the web page through `engine_js.py`, 16 000 rays, positions combined by the median. The face counts, areas and the early-reflection part below are from the Python tools as before. Second ray seed, median absolute error (JND, mean of 500 Hz - 2 kHz; EDT / T30 / C80 / C50 / Ts): 3D mesh 2.5 / 1.8 / 0.7 / 0.8 / 0.9, held-out LS2 after calibration 1.6 / 1.6 / 0.5 / 0.6 / 0.6, 2.5D 2.9 / 2.2 / 1.0 / 1.2 / 1.1. The run with the Python engine of 2026-11-19 (16 000 rays, median): 3D mesh 2.5 / 1.5 / 0.9 / 0.8 / 1.0, held-out LS2 1.1 / 1.0 / 0.4 / 0.7 / 0.5; it is in the history of this file (commit a3d78d5).

Data: Aspöck et al. (2020), *BRAS – Benchmark for Room Acoustical Simulation*, v3, https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0 (dodecahedron RIRs, positions, surface descriptions). Material set: fitted_estimates. This file is derived from BRAS and is CC BY-SA 4.0.

```
CR3: OBJ 2598 faces -> 2598 after decimation -> 2576 room faces (258 narrow ones kept two-sided; 22 behind the room's faces, 0.4 m2, kept but not counted; 0 not at the room dropped); room volume (voxels) 3319 m3 (BRAS documentation: 3330.6 m3)
surface areas (m2): ceiling 168.5, floor 342.5, plaster 450.3, seating 178.9, stagePanels 425.2, structuredPlaster 1171.9, windows 25.4; total 2763
Sabine / Eyring T (s), no air: 125 Hz 1.75 / 1.66, 250 Hz 1.61 / 1.51, 500 Hz 1.41 / 1.31, 1000 Hz 1.49 / 1.39, 2000 Hz 1.54 / 1.44, 4000 Hz 1.41 / 1.31
absorption: BRAS fitted_estimates; scattering per octave band (shown: 1 kHz): ceiling 0.12, floor 0.07, plaster 0.07, seating 0.61, stagePanels 0.05, structuredPlaster 0.19, windows 0.05
[3D mesh] LS1: 5 receivers, 64 s
[3D mesh] LS2: 5 receivers, 60 s
calibration on LS1 (median over the positions of T30 sim / measured, per band): 125 Hz 1.136, 250 Hz 1.057, 500 Hz 1.095, 1000 Hz 1.097, 2000 Hz 1.135, 4000 Hz 1.084
[3D mesh calibrated] LS1: 5 receivers, 76 s
[3D mesh calibrated] LS2: 5 receivers, 61 s
2.5D hall (depth axis = x, stage at small x; image sources order 2, no diffraction): 35 plan vertices, 166 surfaces, volume 3135.1 m3; positions moved into the 2.5D room: LS2 1.96->3.37; outside the 2.5D plan (left out of its statistics): none
[2.5D] LS1: 5 receivers, 4 s
[2.5D] LS2: 5 receivers, 4 s
```

## Room criteria, median over the 10 positions (simulated − measured, median signed / median absolute, in JND)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | median abs, mean of 500–2k |
|---|---|---|---|---|---|---|---|---|
| EDT | measured (median) | 1.61 | 1.39 | 1.33 | 1.31 | 1.23 | 1.03 | |
| | 3D mesh | +2.1 / 2.7 | +1.5 / 1.6 | +0.9 / 1.8 | +1.8 / 1.8 | +3.7 / 3.7 | +1.5 / 1.5 | 2.4 |
| | 3D mesh calibrated | +0.0 / 1.8 | +0.4 / 1.4 | -0.6 / 1.7 | +0.2 / 0.5 | +1.4 / 1.7 | +0.4 / 0.8 | 1.3 |
| | ↳ LS2 only (held out) | -0.1 / 1.8 | +0.6 / 1.2 | -0.9 / 0.9 | +0.4 / 0.8 | +1.2 / 1.2 | +0.7 / 0.9 | 1.0 |
| | 2.5D | +2.1 / 2.1 | +4.3 / 4.3 | +2.7 / 2.7 | +3.3 / 3.3 | +5.0 / 5.0 | +3.8 / 3.8 | 3.6 |
| T30 | measured (median) | 1.62 | 1.45 | 1.31 | 1.34 | 1.32 | 1.06 | |
| | 3D mesh | +1.9 / 1.9 | +1.1 / 1.1 | +1.5 / 1.5 | +1.4 / 1.4 | +1.0 / 1.0 | +1.8 / 1.8 | 1.3 |
| | 3D mesh calibrated | -0.3 / 0.6 | +0.0 / 0.3 | +0.1 / 0.5 | +0.1 / 0.8 | -0.3 / 1.0 | +1.0 / 1.0 | 0.8 |
| | ↳ LS2 only (held out) | -0.7 / 0.7 | +0.2 / 0.6 | -0.0 / 0.1 | -0.2 / 0.5 | -0.4 / 1.1 | +1.4 / 1.4 | 0.6 |
| | 2.5D | +1.8 / 1.8 | +2.4 / 2.4 | +2.2 / 2.2 | +2.1 / 2.1 | +2.6 / 2.6 | +2.9 / 2.9 | 2.3 |
| C80 | measured (median) | 0.41 | 0.43 | 1.27 | 1.80 | 1.42 | 2.86 | |
| | 3D mesh | -0.8 / 1.1 | +0.4 / 1.3 | -0.1 / 0.7 | -0.5 / 0.5 | -0.2 / 0.5 | -0.1 / 0.4 | 0.6 |
| | 3D mesh calibrated | -0.1 / 0.7 | +0.7 / 1.4 | +0.4 / 0.6 | -0.0 / 0.3 | +0.4 / 0.6 | +0.3 / 0.6 | 0.5 |
| | ↳ LS2 only (held out) | -0.4 / 0.8 | +0.2 / 0.8 | +0.6 / 0.6 | +0.1 / 0.2 | +0.6 / 0.6 | -0.2 / 1.4 | 0.5 |
| | 2.5D | -0.2 / 1.7 | -0.7 / 1.7 | -0.4 / 1.6 | -0.1 / 0.8 | -0.4 / 1.0 | -0.3 / 1.3 | 1.1 |
| C50 | measured (median) | -1.87 | -1.69 | -1.02 | -1.64 | -1.72 | -0.25 | |
| | 3D mesh | -0.4 / 1.9 | -0.0 / 1.8 | -0.5 / 1.3 | -0.3 / 0.6 | +0.1 / 0.4 | +0.0 / 0.7 | 0.8 |
| | 3D mesh calibrated | +0.2 / 1.6 | +0.2 / 1.8 | -0.1 / 0.9 | +0.1 / 0.6 | +0.6 / 0.6 | +0.3 / 0.7 | 0.7 |
| | ↳ LS2 only (held out) | -1.0 / 2.9 | -0.6 / 1.7 | -0.2 / 0.7 | -0.1 / 0.2 | +0.5 / 0.6 | -0.4 / 1.7 | 0.5 |
| | 2.5D | +0.2 / 2.8 | -1.3 / 2.4 | +0.2 / 1.9 | -0.2 / 1.4 | -0.0 / 0.7 | -0.5 / 1.7 | 1.3 |
| Ts | measured (median) | 113 | 103 | 97 | 93 | 92 | 74 | |
| | 3D mesh | +1.1 / 1.2 | -0.1 / 0.8 | +0.2 / 0.8 | +0.8 / 0.8 | +0.5 / 0.6 | +0.6 / 0.6 | 0.7 |
| | 3D mesh calibrated | -0.2 / 0.4 | -0.6 / 0.8 | -0.5 / 0.5 | +0.0 / 0.4 | -0.4 / 0.8 | +0.1 / 0.4 | 0.6 |
| | ↳ LS2 only (held out) | -0.1 / 0.3 | +0.5 / 0.8 | -0.5 / 0.5 | +0.1 / 0.5 | -0.7 / 0.8 | +0.5 / 0.9 | 0.6 |
| | 2.5D | +1.4 / 2.4 | +1.7 / 1.7 | +0.4 / 1.1 | +0.6 / 1.2 | +1.0 / 1.3 | +0.9 / 1.3 | 1.2 |

Measured Ts in ms; EDT / T30 in s; C80 / C50 in dB. JND: ISO 3382-1 Annex A.

## Early reflections (first-order image sources vs the measured RIR, 500 Hz–2 kHz)

Each predicted first-order reflection that is at least −15 dB re direct, at least 2 ms after the direct sound and 1.5 ms away from any other predicted one is compared with the measured energy in a 1 ms window at its predicted time (−0.2 … +0.8 ms), in dB re the same window on the direct sound. Controls: the measured level 2 ms later than predicted, and at random times 3–20 ms after the direct sound.

| model | reflections | predicted (median dB) | measured at predicted time | measured +2 ms later | measured at random times | predicted − measured (median / IQR dB) | correlation predicted vs measured |
|---|---|---|---|---|---|---|---|
| 3D mesh | 36 | -5.5 | -6.8 | -10.4 | -11.5 | +1.6 / +0.1 … +3.4 | 0.55 |
| 3D mesh calibrated | 36 | -5.5 | -6.8 | -10.4 | -11.5 | +1.5 / +0.0 … +3.4 | 0.55 |
| 2.5D | 20 | -5.8 | -13.1 | -10.1 | -11.5 | +5.6 / +2.4 … +8.1 | 0.17 |

Direct-sound arrival, measured onset − distance / c (ms): LS1-MP1 -0.07, LS1-MP2 +0.04, LS1-MP3 -0.21, LS1-MP4 -0.67, LS1-MP5 -0.10, LS2-MP1 -0.09, LS2-MP2 -0.27, LS2-MP3 -0.32, LS2-MP4 -0.60, LS2-MP5 -0.19

2.5D conversion (obj_to_hall.py, --preserve eyring):

```
{
 "preserve": "eyring",
 "groups": {
  "aud": {
   "mesh_area_m2": 956.9,
   "hall_area_m2": 539.8,
   "mesh_absorption_area_m2": [
    112.72,
    132.34,
    150.74,
    140.4,
    145.91,
    153.87
   ]
  },
  "wall": {
   "mesh_area_m2": 1220.4,
   "hall_area_m2": 585.2,
   "mesh_absorption_area_m2": [
    117.87,
    140.81,
    143.59,
    134.59,
    124.05,
    148.29
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
 "volume_mesh_m3": 3319.3,
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
