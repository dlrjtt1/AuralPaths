# BRAS CR4: measured RIRs vs AuralPaths (page's engine; 2.5D hall and energy histograms through engine_js.py)

**Computed with the page's engine since 2026-11-20** (`validate_bras_cr.py`, default `--engine js`): the energy histograms of the 3D mesh and of the 2.5D hall come from the engine of the web page through `engine_js.py`, 16 000 rays, positions combined by the median. The face counts, areas and the early-reflection part below are from the Python tools as before. Second ray seed, median absolute error (JND, mean of 500 Hz - 2 kHz; EDT / T30 / C80 / C50 / Ts): 3D mesh 3.2 / 3.1 / 0.9 / 0.8 / 2.1, held-out LS2 after calibration 1.1 / 0.8 / 0.9 / 0.8 / 1.2, 2.5D 2.2 / 2.0 / 1.1 / 1.2 / 1.5. The run with the Python engine of 2026-11-19 (16 000 rays, median): 3D mesh 2.4 / 2.2 / 0.7 / 0.8 / 1.6, held-out LS2 2.3 / 0.6 / 1.1 / 0.7 / 1.5; T30 of the 3D mesh before calibration is about 4 - 5 % longer with the page's engine (cause not found); it is in the history of this file (commit a3d78d5).

Data: Aspöck et al. (2020), *BRAS – Benchmark for Room Acoustical Simulation*, v3, https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0 (dodecahedron RIRs, positions, surface descriptions). Material set: fitted_estimates. This file is derived from BRAS and is CC BY-SA 4.0.

```
CR4: OBJ 5174 faces -> 3000 after decimation -> 2913 room faces (343 narrow ones kept two-sided; 87 behind the room's faces, 142.6 m2, kept but not counted; 0 not at the room dropped); room volume (voxels) 8567 m3 (BRAS documentation: 8656.5 m3)
surface areas (m2): brickwall 694.3, concrete 1687.6, linoleum 598.6, parquet 180.8, seating 624.5, whitePanels 1500.2, windows 17.1, woodPanels 316.3; total 5619
Sabine / Eyring T (s), no air: 125 Hz 2.49 / 2.36, 250 Hz 2.57 / 2.44, 500 Hz 2.27 / 2.14, 1000 Hz 2.32 / 2.20, 2000 Hz 2.24 / 2.11, 4000 Hz 2.13 / 2.01
absorption: BRAS fitted_estimates; scattering per octave band (shown: 1 kHz): brickwall 0.15, concrete 0.05, linoleum 0.06, parquet 0.06, seating 0.61, whitePanels 0.05, windows 0.05, woodPanels 0.15
[3D mesh] LS1: 5 receivers, 87 s
[3D mesh] LS2: 5 receivers, 87 s
calibration on LS1 (median over the positions of T30 sim / measured, per band): 125 Hz 1.155, 250 Hz 1.154, 500 Hz 1.136, 1000 Hz 1.148, 2000 Hz 1.168, 4000 Hz 1.160
[3D mesh calibrated] LS1: 5 receivers, 116 s
[3D mesh calibrated] LS2: 5 receivers, 80 s
2.5D hall (depth axis = x, stage at small x; image sources order 2, no diffraction): 57 plan vertices, 143 surfaces, volume 8023.0 m3; positions moved into the 2.5D room: none; outside the 2.5D plan (left out of its statistics): none
[2.5D] LS1: 5 receivers, 3 s
[2.5D] LS2: 5 receivers, 3 s
```

## Room criteria, median over the 10 positions (simulated − measured, median signed / median absolute, in JND)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | median abs, mean of 500–2k |
|---|---|---|---|---|---|---|---|---|
| EDT | measured (median) | 2.19 | 2.50 | 2.11 | 2.21 | 1.84 | 1.43 | |
| | 3D mesh | +6.6 / 6.6 | +3.5 / 3.5 | +3.8 / 3.8 | +3.4 / 3.4 | +4.3 / 4.3 | +6.4 / 6.4 | 3.8 |
| | 3D mesh calibrated | +3.5 / 3.9 | +1.1 / 1.4 | +1.3 / 1.3 | +1.4 / 1.8 | +1.6 / 1.6 | +4.2 / 4.2 | 1.6 |
| | ↳ LS2 only (held out) | +5.2 / 5.2 | +0.9 / 1.3 | +3.4 / 3.4 | +0.7 / 1.3 | +2.0 / 2.0 | +4.3 / 4.3 | 2.2 |
| | 2.5D | +2.4 / 2.4 | +1.7 / 2.2 | +1.4 / 1.4 | +1.4 / 2.6 | +2.8 / 2.8 | +3.6 / 3.6 | 2.2 |
| T30 | measured (median) | 2.32 | 2.37 | 2.05 | 2.11 | 1.84 | 1.43 | |
| | 3D mesh | +3.1 / 3.1 | +3.0 / 3.0 | +3.1 / 3.1 | +3.1 / 3.1 | +2.7 / 2.7 | +3.2 / 3.2 | 3.0 |
| | 3D mesh calibrated | +0.5 / 0.7 | +0.3 / 0.6 | +0.5 / 0.7 | +0.7 / 0.9 | -0.7 / 1.0 | +1.3 / 1.3 | 0.9 |
| | ↳ LS2 only (held out) | +0.4 / 0.4 | +0.3 / 1.1 | +0.3 / 0.7 | +0.5 / 0.9 | -0.9 / 0.9 | +0.9 / 0.9 | 0.8 |
| | 2.5D | +1.4 / 1.4 | +1.7 / 1.7 | +1.5 / 1.5 | +0.9 / 0.9 | +2.2 / 2.2 | +3.5 / 3.5 | 1.5 |
| C80 | measured (median) | -0.60 | -1.99 | 0.07 | -0.66 | -0.23 | 1.92 | |
| | 3D mesh | -1.0 / 1.3 | -0.0 / 0.7 | -1.6 / 1.6 | -1.0 / 1.4 | -0.4 / 0.6 | -1.0 / 1.1 | 1.2 |
| | 3D mesh calibrated | -0.3 / 1.1 | +0.6 / 1.0 | -1.0 / 1.3 | -0.4 / 1.1 | +0.3 / 0.7 | -0.4 / 1.3 | 1.0 |
| | ↳ LS2 only (held out) | -1.9 / 1.9 | +1.2 / 1.3 | -1.2 / 1.2 | -0.9 / 0.9 | +0.3 / 0.4 | +0.2 / 1.0 | 0.9 |
| | 2.5D | -0.4 / 0.9 | +0.5 / 0.6 | -0.9 / 0.9 | -0.0 / 0.8 | -0.3 / 0.9 | -0.7 / 1.1 | 0.9 |
| C50 | measured (median) | -3.53 | -5.48 | -2.48 | -2.83 | -2.45 | -0.87 | |
| | 3D mesh | -0.3 / 1.2 | +1.5 / 1.7 | -0.9 / 1.3 | -0.7 / 1.1 | +0.3 / 0.8 | -0.3 / 1.4 | 1.1 |
| | 3D mesh calibrated | +0.4 / 1.7 | +2.1 / 2.1 | -0.3 / 1.4 | -0.2 / 0.8 | +1.0 / 1.3 | +0.2 / 2.0 | 1.2 |
| | ↳ LS2 only (held out) | +0.5 / 2.6 | +2.4 / 2.4 | -1.4 / 1.4 | -0.5 / 0.5 | +1.0 / 1.4 | +0.9 / 0.9 | 1.1 |
| | 2.5D | +0.2 / 1.0 | +1.6 / 1.6 | -0.2 / 0.8 | +0.3 / 0.6 | +0.6 / 1.1 | +0.3 / 2.1 | 0.8 |
| Ts | measured (median) | 146 | 170 | 133 | 143 | 131 | 93 | |
| | 3D mesh | +4.2 / 4.2 | +2.1 / 2.3 | +3.2 / 3.2 | +2.7 / 2.7 | +1.7 / 1.7 | +2.2 / 2.2 | 2.5 |
| | 3D mesh calibrated | +1.9 / 1.9 | -0.1 / 1.4 | +1.5 / 1.8 | +0.9 / 1.6 | -0.2 / 0.4 | +1.0 / 1.1 | 1.3 |
| | ↳ LS2 only (held out) | +2.4 / 2.4 | -0.7 / 1.7 | +2.5 / 2.5 | +1.0 / 1.0 | -0.0 / 0.5 | +0.5 / 0.5 | 1.4 |
| | 2.5D | +2.4 / 2.4 | +0.6 / 1.9 | +1.9 / 1.9 | +0.6 / 1.3 | +0.9 / 1.3 | +1.7 / 1.8 | 1.5 |

Measured Ts in ms; EDT / T30 in s; C80 / C50 in dB. JND: ISO 3382-1 Annex A.

## Early reflections (first-order image sources vs the measured RIR, 500 Hz–2 kHz)

Each predicted first-order reflection that is at least −15 dB re direct, at least 2 ms after the direct sound and 1.5 ms away from any other predicted one is compared with the measured energy in a 1 ms window at its predicted time (−0.2 … +0.8 ms), in dB re the same window on the direct sound. Controls: the measured level 2 ms later than predicted, and at random times 3–20 ms after the direct sound.

| model | reflections | predicted (median dB) | measured at predicted time | measured +2 ms later | measured at random times | predicted − measured (median / IQR dB) | correlation predicted vs measured |
|---|---|---|---|---|---|---|---|
| 3D mesh | 28 | -9.0 | -13.5 | -14.0 | -21.0 | +4.6 / +1.9 … +7.8 | 0.46 |
| 3D mesh calibrated | 28 | -9.1 | -13.5 | -14.0 | -21.0 | +4.5 / +1.8 … +7.8 | 0.46 |
| 2.5D | 23 | -9.2 | -13.8 | -13.9 | -21.0 | +5.0 / +1.0 … +8.3 | 0.28 |

Direct-sound arrival, measured onset − distance / c (ms): LS1-MP1 -0.19, LS1-MP2 -0.31, LS1-MP3 -0.28, LS1-MP4 +0.07, LS1-MP5 -0.10, LS2-MP1 +0.00, LS2-MP2 -0.11, LS2-MP3 -0.19, LS2-MP4 -0.06, LS2-MP5 -0.36

2.5D conversion (obj_to_hall.py, --preserve eyring):

```
{
 "preserve": "eyring",
 "groups": {
  "aud": {
   "mesh_area_m2": 1356.7,
   "hall_area_m2": 870.1,
   "mesh_absorption_area_m2": [
    152.29,
    163.88,
    202.24,
    244.63,
    251.04,
    258.99
   ]
  },
  "wall": {
   "mesh_area_m2": 1915.1,
   "hall_area_m2": 880.5,
   "mesh_absorption_area_m2": [
    219.77,
    223.67,
    249.44,
    191.24,
    230.9,
    223.99
   ]
  },
  "ceil": {
   "mesh_area_m2": 2347.6,
   "hall_area_m2": 1141.2,
   "mesh_absorption_area_m2": [
    182.14,
    149.7,
    156.83,
    158.51,
    135.15,
    164.47
   ]
  }
 },
 "volume_mesh_m3": 8566.9,
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
