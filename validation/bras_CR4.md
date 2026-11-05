# BRAS CR4: measured RIRs vs AuralPaths (Python engine)

Data: Aspöck et al. (2020), *BRAS – Benchmark for Room Acoustical Simulation*, v3, https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0 (dodecahedron RIRs, positions, surface descriptions). Material set: fitted_estimates. This file is derived from BRAS and is CC BY-SA 4.0.

```
CR4: OBJ 5174 faces -> 3000 after decimation -> 2656 room-facing faces (344 dropped); room volume (voxels) 8175 m3 (BRAS documentation: 8656.5 m3)
surface areas (m2): brickwall 693.8, concrete 1687.4, linoleum 596.3, parquet 180.8, seating 624.5, whitePanels 1633.7, windows 17.1, woodPanels 316.3; total 5750
Sabine / Eyring T (s), no air: 125 Hz 2.33 / 2.21, 250 Hz 2.41 / 2.30, 500 Hz 2.14 / 2.02, 1000 Hz 2.18 / 2.06, 2000 Hz 2.10 / 1.98, 4000 Hz 2.00 / 1.88
absorption: BRAS fitted_estimates; scattering at 1 kHz: brickwall 0.15, concrete 0.05, linoleum 0.06, parquet 0.06, seating 0.61, whitePanels 0.05, windows 0.05, woodPanels 0.15
[3D mesh] LS1: 5 receivers, 587 s
[3D mesh] LS2: 5 receivers, 570 s
calibration on LS1 (T30 sim / measured per band): 125 Hz 1.077, 250 Hz 1.075, 500 Hz 1.088, 1000 Hz 1.045, 2000 Hz 1.097, 4000 Hz 1.202
[3D mesh calibrated] LS1: 5 receivers, 563 s
[3D mesh calibrated] LS2: 5 receivers, 586 s
2.5D hall (depth axis = x, stage at small x; image sources order 2, no diffraction): 57 plan vertices, 143 surfaces, volume 8023.0 m3; positions moved into the 2.5D room: none; outside the 2.5D plan (left out of its statistics): none
[2.5D] LS1: 5 receivers, 9 s
[2.5D] LS2: 5 receivers, 9 s
```

## Room criteria, mean over the 10 positions (simulated − measured, mean signed / mean absolute, in JND)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs 500–2k |
|---|---|---|---|---|---|---|---|---|
| EDT | measured (mean) | 2.26 | 2.43 | 2.10 | 2.19 | 1.86 | 1.42 | |
| | 3D mesh | +4.6 / 4.8 | +2.0 / 2.7 | +2.0 / 2.7 | +1.1 / 2.4 | +1.9 / 3.0 | +2.8 / 3.2 | 2.7 |
| | 3D mesh calibrated | +2.7 / 4.4 | +0.5 / 1.7 | +0.6 / 1.4 | +0.2 / 2.1 | +0.4 / 1.7 | +1.1 / 2.0 | 1.7 |
| | ↳ LS2 only (held out) | +3.4 / 4.6 | +0.2 / 1.8 | +1.1 / 1.2 | -0.3 / 1.5 | +0.8 / 1.5 | +1.0 / 1.7 | 1.4 |
| | 2.5D | +1.9 / 4.0 | +0.4 / 1.6 | +0.6 / 2.0 | -1.3 / 2.1 | +0.8 / 1.6 | +2.7 / 3.6 | 1.9 |
| T30 | measured (mean) | 2.31 | 2.36 | 2.07 | 2.10 | 1.84 | 1.42 | |
| | 3D mesh | +2.2 / 2.4 | +1.7 / 1.7 | +2.2 / 2.2 | +2.2 / 2.4 | +2.1 / 2.1 | +3.1 / 3.1 | 2.2 |
| | 3D mesh calibrated | +0.4 / 0.9 | -0.0 / 0.9 | -0.2 / 0.9 | +0.4 / 1.2 | -0.0 / 0.9 | +0.8 / 1.9 | 1.0 |
| | ↳ LS2 only (held out) | +0.9 / 1.4 | -0.0 / 0.6 | -0.1 / 0.7 | -0.1 / 0.4 | -0.4 / 0.9 | +0.6 / 2.3 | 0.7 |
| | 2.5D | +0.9 / 1.0 | +1.1 / 1.1 | +1.0 / 1.1 | +0.0 / 0.9 | +1.3 / 1.5 | +1.8 / 1.9 | 1.2 |
| C80 | measured (mean) | -0.49 | -1.83 | 0.20 | -0.65 | -0.08 | 1.98 | |
| | 3D mesh | -1.1 / 1.8 | +0.3 / 1.1 | -0.9 / 1.2 | +0.1 / 0.9 | +0.0 / 1.0 | -0.7 / 1.3 | 1.0 |
| | 3D mesh calibrated | -0.8 / 1.9 | +0.6 / 1.8 | -0.5 / 1.8 | +0.3 / 1.3 | +0.5 / 1.4 | +0.2 / 1.5 | 1.5 |
| | ↳ LS2 only (held out) | -1.5 / 2.3 | +0.7 / 2.0 | -0.9 / 2.4 | -0.1 / 1.5 | +0.6 / 1.4 | +1.1 / 2.0 | 1.8 |
| | 2.5D | -0.4 / 1.7 | +0.7 / 1.5 | -0.6 / 1.0 | +0.5 / 0.6 | +0.3 / 0.8 | -0.4 / 1.5 | 0.8 |
| C50 | measured (mean) | -2.72 | -4.71 | -1.97 | -2.89 | -2.44 | -0.76 | |
| | 3D mesh | -0.7 / 2.0 | +1.3 / 1.8 | -0.6 / 1.2 | +0.3 / 0.7 | +0.4 / 1.1 | -0.1 / 1.6 | 1.0 |
| | 3D mesh calibrated | -0.2 / 2.4 | +1.8 / 2.2 | -0.0 / 1.6 | +0.8 / 1.5 | +1.1 / 1.5 | +0.9 / 1.7 | 1.5 |
| | ↳ LS2 only (held out) | -0.9 / 3.0 | +2.2 / 2.8 | -0.5 / 2.1 | +0.4 / 1.8 | +1.1 / 1.6 | +2.2 / 2.4 | 1.8 |
| | 2.5D | -0.1 / 1.9 | +1.7 / 2.8 | -0.3 / 1.1 | +0.8 / 1.3 | +0.7 / 1.3 | +0.2 / 2.4 | 1.3 |
| Ts | measured (mean) | 146 | 167 | 129 | 143 | 126 | 91 | |
| | 3D mesh | +3.0 / 3.0 | +0.7 / 1.1 | +2.0 / 2.0 | +0.4 / 0.9 | +0.5 / 1.3 | +1.3 / 1.5 | 1.4 |
| | 3D mesh calibrated | +1.8 / 2.1 | -0.4 / 2.2 | +0.9 / 2.2 | -0.2 / 1.5 | -0.5 / 1.6 | +0.0 / 1.5 | 1.7 |
| | ↳ LS2 only (held out) | +2.8 / 2.8 | -0.5 / 2.3 | +1.6 / 2.5 | +0.3 / 1.2 | -0.7 / 1.4 | -1.1 / 1.7 | 1.7 |
| | 2.5D | +0.8 / 1.4 | -0.8 / 1.9 | +0.8 / 1.4 | -1.2 / 1.2 | -0.3 / 1.2 | +0.5 / 1.6 | 1.3 |

Measured Ts in ms; EDT / T30 in s; C80 / C50 in dB. JND: ISO 3382-1 Annex A.

## Early reflections (first-order image sources vs the measured RIR, 500 Hz–2 kHz)

Each predicted first-order reflection that is at least −15 dB re direct, at least 2 ms after the direct sound and 1.5 ms away from any other predicted one is compared with the measured energy in a 1 ms window at its predicted time (−0.2 … +0.8 ms), in dB re the same window on the direct sound. Controls: the measured level 2 ms later than predicted, and at random times 3–20 ms after the direct sound.

| model | reflections | predicted (median dB) | measured at predicted time | measured +2 ms later | measured at random times | predicted − measured (median / IQR dB) | correlation predicted vs measured |
|---|---|---|---|---|---|---|---|
| 3D mesh | 35 | -6.7 | -13.7 | -14.3 | -21.0 | +6.5 / +2.6 … +8.9 | 0.30 |
| 3D mesh calibrated | 35 | -6.8 | -13.7 | -14.3 | -21.0 | +6.4 / +2.6 … +8.9 | 0.29 |
| 2.5D | 29 | -6.7 | -14.2 | -14.1 | -21.0 | +6.9 / +1.5 … +9.2 | 0.34 |

Direct-sound arrival, measured onset − distance / c (ms): LS1-MP1 -0.19, LS1-MP2 -0.31, LS1-MP3 -0.28, LS1-MP4 +0.07, LS1-MP5 -0.10, LS2-MP1 +0.00, LS2-MP2 -0.11, LS2-MP3 -0.19, LS2-MP4 -0.06, LS2-MP5 -0.36

2.5D conversion (obj_to_hall.py, --preserve eyring):

```
{
 "preserve": "eyring",
 "groups": {
  "aud": {
   "mesh_area_m2": 1355.8,
   "hall_area_m2": 870.1,
   "mesh_absorption_area_m2": [
    152.21,
    163.82,
    202.19,
    244.56,
    250.97,
    258.91
   ]
  },
  "wall": {
   "mesh_area_m2": 2030.8,
   "hall_area_m2": 880.5,
   "mesh_absorption_area_m2": [
    229.22,
    230.53,
    255.53,
    199.51,
    239.99,
    233.34
   ]
  },
  "ceil": {
   "mesh_area_m2": 2363.4,
   "hall_area_m2": 1141.2,
   "mesh_absorption_area_m2": [
    183.44,
    150.65,
    157.68,
    159.64,
    136.41,
    165.76
   ]
  }
 },
 "volume_mesh_m3": 8174.9,
 "n_plan_vertices": 57,
 "n_floor": 29,
 "n_ceil": 59,
 "n_surfaces_2p5d": 143,
 "dims_m": [
  32.76,
  33.04,
  12.092
 ],
 "volume_2p5d_m3": 8023.0
}
```
