# BRAS CR4: measured RIRs vs AuralPaths (Python engine)

Data: Aspöck et al. (2020), *BRAS – Benchmark for Room Acoustical Simulation*, v3, https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0 (dodecahedron RIRs, positions, surface descriptions). Material set: fitted_estimates. This file is derived from BRAS and is CC BY-SA 4.0.

```
CR4: OBJ 5174 faces -> 3000 after decimation -> 2656 room-facing faces (344 dropped); room volume (voxels) 8175 m3 (BRAS documentation: 8656.5 m3)
surface areas (m2): brickwall 693.8, concrete 1687.4, linoleum 596.3, parquet 180.8, seating 624.5, whitePanels 1633.7, windows 17.1, woodPanels 316.3; total 5750
Sabine / Eyring T (s), no air: 125 Hz 2.33 / 2.21, 250 Hz 2.41 / 2.30, 500 Hz 2.14 / 2.02, 1000 Hz 2.18 / 2.06, 2000 Hz 2.10 / 1.98, 4000 Hz 2.00 / 1.88
absorption: BRAS fitted_estimates; scattering per octave band (shown: 1 kHz): brickwall 0.15, concrete 0.05, linoleum 0.06, parquet 0.06, seating 0.61, whitePanels 0.05, windows 0.05, woodPanels 0.15
[3D mesh] LS1: 5 receivers, 602 s
[3D mesh] LS2: 5 receivers, 597 s
calibration on LS1 (T30 sim / measured per band): 125 Hz 1.085, 250 Hz 1.087, 500 Hz 1.057, 1000 Hz 1.034, 2000 Hz 1.079, 4000 Hz 1.161
[3D mesh calibrated] LS1: 5 receivers, 622 s
[3D mesh calibrated] LS2: 5 receivers, 585 s
2.5D hall (depth axis = x, stage at small x; image sources order 2, no diffraction): 57 plan vertices, 143 surfaces, volume 8023.0 m3; positions moved into the 2.5D room: none; outside the 2.5D plan (left out of its statistics): none
[2.5D] LS1: 5 receivers, 6 s
[2.5D] LS2: 5 receivers, 6 s
```

## Room criteria, mean over the 10 positions (simulated − measured, mean signed / mean absolute, in JND)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs 500–2k |
|---|---|---|---|---|---|---|---|---|
| EDT | measured (mean) | 2.26 | 2.43 | 2.10 | 2.19 | 1.86 | 1.42 | |
| | 3D mesh | +5.7 / 6.3 | +3.2 / 3.2 | +3.9 / 4.3 | +2.8 / 2.9 | +3.7 / 3.9 | +4.5 / 4.5 | 3.7 |
| | 3D mesh calibrated | +2.9 / 3.7 | +0.7 / 1.9 | +1.6 / 2.4 | +0.9 / 1.8 | +1.8 / 2.2 | +3.7 / 4.0 | 2.1 |
| | ↳ LS2 only (held out) | +4.3 / 4.6 | +0.9 / 2.1 | +2.5 / 2.7 | +0.8 / 1.6 | +2.3 / 2.3 | +3.2 / 3.2 | 2.2 |
| | 2.5D | +3.3 / 4.0 | +1.6 / 1.6 | +2.1 / 2.1 | +0.5 / 1.2 | +2.7 / 2.9 | +4.1 / 4.6 | 2.1 |
| T30 | measured (mean) | 2.31 | 2.36 | 2.07 | 2.10 | 1.84 | 1.42 | |
| | 3D mesh | +2.6 / 2.6 | +2.0 / 2.0 | +2.1 / 2.1 | +2.0 / 2.0 | +2.3 / 2.3 | +3.9 / 3.9 | 2.1 |
| | 3D mesh calibrated | +0.7 / 1.5 | +0.3 / 0.8 | +0.7 / 1.3 | +0.9 / 1.3 | +0.5 / 0.9 | +1.2 / 1.4 | 1.2 |
| | ↳ LS2 only (held out) | +1.3 / 1.4 | +0.1 / 0.8 | +0.5 / 0.9 | +0.4 / 1.1 | +0.4 / 0.5 | +1.3 / 1.3 | 0.8 |
| | 2.5D | +0.9 / 1.5 | +1.1 / 1.1 | +1.1 / 1.4 | -0.0 / 1.0 | +1.4 / 1.5 | +2.1 / 2.1 | 1.3 |
| C80 | measured (mean) | -0.49 | -1.83 | 0.20 | -0.65 | -0.08 | 1.98 | |
| | 3D mesh | -1.0 / 1.3 | +0.4 / 2.1 | -1.0 / 1.9 | -0.2 / 1.7 | -0.2 / 1.2 | -1.1 / 2.0 | 1.6 |
| | 3D mesh calibrated | -1.1 / 2.0 | +0.2 / 1.1 | -1.2 / 1.5 | -0.6 / 0.6 | -0.4 / 1.2 | -1.0 / 1.6 | 1.1 |
| | ↳ LS2 only (held out) | -1.5 / 2.5 | +0.6 / 1.1 | -1.4 / 1.8 | -0.7 / 0.7 | -0.1 / 1.3 | +0.2 / 0.9 | 1.3 |
| | 2.5D | -1.6 / 2.0 | -0.4 / 2.0 | -1.6 / 1.7 | -0.5 / 1.2 | -0.6 / 1.4 | -1.2 / 2.0 | 1.5 |
| C50 | measured (mean) | -2.72 | -4.71 | -1.97 | -2.89 | -2.44 | -0.76 | |
| | 3D mesh | -0.8 / 2.3 | +1.2 / 2.7 | -1.0 / 2.0 | -0.2 / 2.0 | -0.2 / 1.5 | -1.0 / 2.6 | 1.8 |
| | 3D mesh calibrated | -0.7 / 2.6 | +1.3 / 1.8 | -1.0 / 1.5 | -0.4 / 0.8 | -0.2 / 1.4 | -0.6 / 1.8 | 1.2 |
| | ↳ LS2 only (held out) | -0.8 / 3.1 | +2.2 / 2.4 | -0.9 / 1.7 | -0.2 / 0.5 | +0.3 / 1.2 | +1.2 / 1.2 | 1.2 |
| | 2.5D | -1.1 / 2.0 | +0.7 / 2.5 | -1.2 / 1.7 | -0.0 / 1.2 | -0.1 / 1.3 | -0.4 / 2.1 | 1.4 |
| Ts | measured (mean) | 146 | 167 | 129 | 143 | 126 | 91 | |
| | 3D mesh | +3.3 / 3.3 | +1.1 / 2.6 | +2.6 / 3.1 | +1.4 / 2.1 | +1.4 / 1.7 | +2.2 / 2.4 | 2.3 |
| | 3D mesh calibrated | +2.4 / 2.7 | +0.2 / 1.8 | +2.3 / 2.5 | +1.2 / 1.4 | +1.0 / 2.0 | +1.5 / 1.7 | 2.0 |
| | ↳ LS2 only (held out) | +3.3 / 3.5 | +0.1 / 2.1 | +2.9 / 3.0 | +1.6 / 1.8 | +0.6 / 1.9 | +0.4 / 0.8 | 2.2 |
| | 2.5D | +2.8 / 2.8 | +1.2 / 1.9 | +2.5 / 2.6 | +0.4 / 1.2 | +1.2 / 1.8 | +1.6 / 2.3 | 1.9 |

Measured Ts in ms; EDT / T30 in s; C80 / C50 in dB. JND: ISO 3382-1 Annex A.

## Early reflections (first-order image sources vs the measured RIR, 500 Hz–2 kHz)

Each predicted first-order reflection that is at least −15 dB re direct, at least 2 ms after the direct sound and 1.5 ms away from any other predicted one is compared with the measured energy in a 1 ms window at its predicted time (−0.2 … +0.8 ms), in dB re the same window on the direct sound. Controls: the measured level 2 ms later than predicted, and at random times 3–20 ms after the direct sound.

| model | reflections | predicted (median dB) | measured at predicted time | measured +2 ms later | measured at random times | predicted − measured (median / IQR dB) | correlation predicted vs measured |
|---|---|---|---|---|---|---|---|
| 3D mesh | 28 | -9.0 | -13.5 | -14.0 | -21.0 | +4.6 / +1.9 … +7.8 | 0.46 |
| 3D mesh calibrated | 28 | -9.1 | -13.5 | -14.0 | -21.0 | +4.6 / +1.9 … +7.8 | 0.46 |
| 2.5D | 23 | -9.3 | -13.8 | -13.9 | -21.0 | +5.0 / +1.0 … +8.2 | 0.28 |

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
