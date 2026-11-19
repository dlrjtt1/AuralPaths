# BRAS CR4: measured RIRs vs AuralPaths (Python engine)

**Rerun 2026-11-19, 16 000 rays, positions combined by the median.** Mesh rules of that day (`validation/mesh_leak.md`): 2913 room faces instead of 2656 (344 dropped before), 87 faces behind the room's faces (142.6 m2, mostly `whitePanels`) no longer counted, surface 5619 instead of 5750 m2, volume 8567 instead of 8175 m3 (BRAS documentation 8656.5 m3), 8 cm voxels as before. Two things changed against the tables before, so the numbers are not comparable one to one: 16 000 rays instead of 4 000, and the positions are combined by the median instead of the mean (`--combine mean` gives the mean), in the tables and in the one-step calibration on LS1. Reasons in the note of `bras_CR3.md`.

**Seed dependence.** At 4 000 rays two runs that differ in the ray seed only gave an EDT difference at 1 kHz of +8.2 and -0.3 JND at LS2-MP1 and T30 simulated / measured of 1.09 and 1.26 at LS1-MP2; the median absolute EDT error of the 3D mesh (mean of 500 Hz - 2 kHz) was 4.6 and 4.4 JND. At 16 000 rays it is 2.4 (this run) and 2.2 JND (second seed); the larger EDT error at 4 000 rays was noise of the ray tracing, not an effect of the mesh rules (the run before the mesh rules, 4 000 rays, combined by the median: 3.6). Difference between the two seeds in T30 simulated / measured at 16 000 rays: mean over the 10 pairs 0.03 - 0.04, largest 0.10 (4 000 rays: 0.07 - 0.10, largest 0.24). Calibration factors on LS1 at 500 Hz - 2 kHz: 1.09 - 1.12 (this run), 1.07 - 1.11 (second seed).

**Second seed** (same settings, ray seed `crc32("<source>|2")`), median absolute error, mean of 500 Hz - 2 kHz, this run / second seed, in JND: 3D mesh EDT 2.4 / 2.2, T30 2.2 / 2.0, C80 0.7 / 0.9, C50 0.8 / 0.6, Ts 1.6 / 1.8; held-out LS2 after calibration EDT 2.3 / 2.1, T30 0.6 / 0.5, C80 1.1 / 1.1, C50 0.7 / 1.0, Ts 1.5 / 1.7; 2.5D EDT 1.4 / 1.8, T30 1.1 / 0.9, C80 1.1 / 1.0, C50 0.8 / 0.8, Ts 1.4 / 1.5. The uncalibrated 3D mesh T30 is about 10 % longer than measured with both seeds.

The run was computed in pieces (2 h limit per job); the times in the log below are the ray-tracing times of the pieces.

Data: Aspöck et al. (2020), *BRAS – Benchmark for Room Acoustical Simulation*, v3, https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0 (dodecahedron RIRs, positions, surface descriptions). Material set: fitted_estimates. This file is derived from BRAS and is CC BY-SA 4.0.

```
CR4: OBJ 5174 faces -> 3000 after decimation -> 2913 room faces (343 narrow ones kept two-sided; 87 behind the room's faces, 142.6 m2, kept but not counted; 0 not at the room dropped); room volume (voxels) 8567 m3 (BRAS documentation: 8656.5 m3)
surface areas (m2): brickwall 694.3, concrete 1687.6, linoleum 598.6, parquet 180.8, seating 624.5, whitePanels 1500.2, windows 17.1, woodPanels 316.3; total 5619
Sabine / Eyring T (s), no air: 125 Hz 2.49 / 2.36, 250 Hz 2.57 / 2.44, 500 Hz 2.27 / 2.14, 1000 Hz 2.32 / 2.20, 2000 Hz 2.24 / 2.11, 4000 Hz 2.13 / 2.01
absorption: BRAS fitted_estimates; scattering per octave band (shown: 1 kHz): brickwall 0.15, concrete 0.05, linoleum 0.06, parquet 0.06, seating 0.61, whitePanels 0.05, windows 0.05, woodPanels 0.15
[3D mesh] LS1: 5 receivers, 3205 s
[3D mesh] LS2: 5 receivers, 3159 s
calibration on LS1 (median over the positions of T30 sim / measured, per band): 125 Hz 1.111, 250 Hz 1.103, 500 Hz 1.101, 1000 Hz 1.091, 2000 Hz 1.119, 4000 Hz 1.187
[3D mesh calibrated] LS1: 5 receivers, 3235 s
[3D mesh calibrated] LS2: 5 receivers, 3044 s
2.5D hall (depth axis = x, stage at small x; image sources order 2, no diffraction): 57 plan vertices, 143 surfaces, volume 8023.0 m3; positions moved into the 2.5D room: none; outside the 2.5D plan (left out of its statistics): none
[2.5D] LS1: 5 receivers, 39 s
[2.5D] LS2: 5 receivers, 37 s
```

## Room criteria, median over the 10 positions (simulated − measured, median signed / median absolute, in JND)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | median abs, mean of 500–2k |
|---|---|---|---|---|---|---|---|---|
| EDT | measured (median) | 2.19 | 2.50 | 2.11 | 2.21 | 1.84 | 1.43 | |
| | 3D mesh | +4.6 / 4.6 | +2.4 / 2.4 | +2.8 / 2.8 | +1.7 / 1.7 | +2.7 / 2.7 | +4.8 / 4.8 | 2.4 |
| | 3D mesh calibrated | +3.4 / 3.4 | +1.2 / 2.1 | +0.6 / 1.2 | +0.8 / 2.2 | +1.0 / 1.3 | +2.0 / 2.0 | 1.5 |
| | ↳ LS2 only (held out) | +4.5 / 4.5 | +0.9 / 1.5 | +1.6 / 1.6 | +0.2 / 2.9 | +1.4 / 2.3 | +1.7 / 1.7 | 2.3 |
| | 2.5D | +1.9 / 3.0 | +0.4 / 0.5 | +1.4 / 1.6 | -0.2 / 1.0 | +1.6 / 1.6 | +3.6 / 3.6 | 1.4 |
| T30 | measured (median) | 2.32 | 2.37 | 2.05 | 2.11 | 1.84 | 1.43 | |
| | 3D mesh | +2.8 / 2.8 | +2.1 / 2.1 | +2.0 / 2.0 | +2.0 / 2.0 | +2.4 / 2.4 | +3.7 / 3.7 | 2.2 |
| | 3D mesh calibrated | +1.2 / 1.2 | +0.8 / 0.8 | +0.9 / 0.9 | +0.7 / 0.7 | +0.6 / 0.6 | +1.0 / 1.0 | 0.7 |
| | ↳ LS2 only (held out) | +1.3 / 1.3 | +0.2 / 0.5 | +0.7 / 0.7 | +0.8 / 0.8 | +0.3 / 0.3 | +0.8 / 0.8 | 0.6 |
| | 2.5D | +0.7 / 0.7 | +1.1 / 1.1 | +1.2 / 1.2 | +0.0 / 0.4 | +1.5 / 1.5 | +2.3 / 2.3 | 1.1 |
| C80 | measured (median) | -0.60 | -1.99 | 0.07 | -0.66 | -0.23 | 1.92 | |
| | 3D mesh | -0.6 / 1.0 | +0.2 / 1.1 | -1.1 / 1.1 | -0.2 / 0.5 | -0.2 / 0.6 | -0.8 / 1.3 | 0.7 |
| | 3D mesh calibrated | -0.3 / 1.3 | +1.1 / 1.1 | -0.8 / 1.1 | +0.3 / 0.8 | +0.1 / 1.1 | -0.4 / 0.8 | 1.0 |
| | ↳ LS2 only (held out) | -0.8 / 1.1 | +1.2 / 1.2 | -1.1 / 1.7 | +0.2 / 0.8 | +0.4 / 0.9 | +0.8 / 0.8 | 1.1 |
| | 2.5D | -0.7 / 0.7 | -0.7 / 1.3 | -1.6 / 1.6 | -0.5 / 0.5 | -0.6 / 1.1 | -1.7 / 1.7 | 1.1 |
| C50 | measured (median) | -3.53 | -5.48 | -2.48 | -2.83 | -2.45 | -0.87 | |
| | 3D mesh | -0.2 / 1.5 | +1.2 / 1.6 | -0.8 / 1.0 | +0.1 / 0.6 | +0.2 / 0.9 | +0.1 / 1.6 | 0.8 |
| | 3D mesh calibrated | +0.1 / 2.4 | +1.8 / 1.8 | +0.1 / 1.0 | +0.4 / 0.6 | +0.8 / 1.2 | +0.1 / 1.3 | 0.9 |
| | ↳ LS2 only (held out) | -0.5 / 3.4 | +2.3 / 2.3 | -0.6 / 0.6 | -0.0 / 0.4 | +0.8 / 1.2 | +1.6 / 1.6 | 0.7 |
| | 2.5D | -0.4 / 1.0 | +0.8 / 1.4 | -1.0 / 1.0 | -0.4 / 0.6 | +0.0 / 0.9 | -0.3 / 1.5 | 0.8 |
| Ts | measured (median) | 146 | 170 | 133 | 143 | 131 | 93 | |
| | 3D mesh | +2.5 / 2.5 | +1.1 / 1.9 | +2.4 / 2.4 | +1.1 / 1.3 | +0.9 / 1.2 | +1.6 / 1.8 | 1.6 |
| | 3D mesh calibrated | +1.5 / 1.5 | +0.1 / 1.1 | +0.4 / 0.7 | -0.2 / 0.5 | +0.1 / 1.7 | +0.8 / 1.4 | 1.0 |
| | ↳ LS2 only (held out) | +2.1 / 2.1 | -0.2 / 1.8 | +2.1 / 2.1 | -0.2 / 0.5 | -0.7 / 1.9 | +0.3 / 1.2 | 1.5 |
| | 2.5D | +2.1 / 2.1 | +0.9 / 1.5 | +2.0 / 2.0 | +0.5 / 0.9 | +0.8 / 1.2 | +1.8 / 1.8 | 1.4 |

Measured Ts in ms; EDT / T30 in s; C80 / C50 in dB. JND: ISO 3382-1 Annex A.

## Early reflections (first-order image sources vs the measured RIR, 500 Hz–2 kHz)

Each predicted first-order reflection that is at least −15 dB re direct, at least 2 ms after the direct sound and 1.5 ms away from any other predicted one is compared with the measured energy in a 1 ms window at its predicted time (−0.2 … +0.8 ms), in dB re the same window on the direct sound. Controls: the measured level 2 ms later than predicted, and at random times 3–20 ms after the direct sound.

| model | reflections | predicted (median dB) | measured at predicted time | measured +2 ms later | measured at random times | predicted − measured (median / IQR dB) | correlation predicted vs measured |
|---|---|---|---|---|---|---|---|
| 3D mesh | 28 | -9.0 | -13.5 | -14.0 | -21.0 | +4.6 / +1.9 … +7.8 | 0.46 |
| 3D mesh calibrated | 28 | -9.1 | -13.5 | -14.0 | -21.0 | +4.5 / +1.9 … +7.8 | 0.46 |
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
