# BRAS CR3: measured RIRs vs AuralPaths (Python engine)

**Rerun 2026-11-19** with the mesh rules of that day (`validation/mesh_leak.md`): 2576 room faces instead of 2319 (279 dropped before), volume 3319 instead of 3188 m3 (BRAS documentation 3330.6 m3), 4 000 rays as before. Mean absolute errors at 500 Hz - 2 kHz, before -> now: 3D mesh EDT 3.0 -> 1.9, T30 1.8 -> 2.8, C80 0.8 -> 0.9, C50 1.0 -> 1.0, Ts 1.0 -> 0.7 JND; held-out LS2 after calibration EDT 1.8 -> 2.3, T30 0.8 -> 4.3, C80 0.7 -> 1.1, C50 0.9 -> 1.4, Ts 0.7 -> 0.9; 2.5D EDT 4.4 -> 3.7, T30 3.2 -> 3.3, C80 2.3 -> 1.7, C50 2.6 -> 1.7, Ts 2.4 -> 1.8.

**Reading the T30 rows.** At 4 000 rays the T30 of single source-receiver pairs is not stable in this engine: in this run LS1-MP1, LS1-MP2 and LS1-MP5 (uncalibrated) and LS2-MP5 (calibrated) come out at 1.7 - 2.1 s in most bands where the measurement has 1.3 - 1.4 s, while the other pairs are within about 15 %; in the run before, LS1-MP2 and LS1-MP4 of the calibrated run did the same (1.7 - 2.2 s) and no pair of the uncalibrated run. The pairs change with small changes of geometry or materials (same ray seed), so this is taken as noise of the late tail, not a property of those seats. It sets the mean-based numbers: the LS1 calibration factors (1.10 - 1.23 now, 1.04 - 1.14 before) and the held-out T30 error. The median over the 10 pairs of T30 simulated / measured is 1.06 / 1.02 / 1.05 / 1.08 / 1.03 / 1.09 (125 Hz - 4 kHz) in this run and 1.07 / 1.04 / 1.07 / 1.07 / 1.07 / 1.12 in the run before. The one-step calibration of this script uses the mean and should not be read from this run; `calibrate.py` combines positions by the median.

Data: Aspöck et al. (2020), *BRAS – Benchmark for Room Acoustical Simulation*, v3, https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0 (dodecahedron RIRs, positions, surface descriptions). Material set: fitted_estimates. This file is derived from BRAS and is CC BY-SA 4.0.

```
CR3: OBJ 2598 faces -> 2598 after decimation -> 2576 room faces (258 narrow ones kept two-sided; 22 behind the room's faces, 0.4 m2, kept but not counted; 0 not at the room dropped); room volume (voxels) 3319 m3 (BRAS documentation: 3330.6 m3)
surface areas (m2): ceiling 168.5, floor 342.5, plaster 450.3, seating 178.9, stagePanels 425.2, structuredPlaster 1171.9, windows 25.4; total 2763
Sabine / Eyring T (s), no air: 125 Hz 1.75 / 1.66, 250 Hz 1.61 / 1.51, 500 Hz 1.41 / 1.31, 1000 Hz 1.49 / 1.39, 2000 Hz 1.54 / 1.44, 4000 Hz 1.41 / 1.31
absorption: BRAS fitted_estimates; scattering per octave band (shown: 1 kHz): ceiling 0.12, floor 0.07, plaster 0.07, seating 0.61, stagePanels 0.05, structuredPlaster 0.19, windows 0.05
[3D mesh] LS1: 5 receivers, 588 s
[3D mesh] LS2: 5 receivers, 589 s
calibration on LS1 (T30 sim / measured per band): 125 Hz 1.179, 250 Hz 1.136, 500 Hz 1.223, 1000 Hz 1.230, 2000 Hz 1.234, 4000 Hz 1.104
[3D mesh calibrated] LS1: 5 receivers, 582 s
[3D mesh calibrated] LS2: 5 receivers, 564 s
2.5D hall (depth axis = x, stage at small x; image sources order 2, no diffraction): 35 plan vertices, 166 surfaces, volume 3135.1 m3; positions moved into the 2.5D room: LS2 1.96->3.37; outside the 2.5D plan (left out of its statistics): none
[2.5D] LS1: 5 receivers, 12 s
[2.5D] LS2: 5 receivers, 12 s
```

## Room criteria, mean over the 10 positions (simulated − measured, mean signed / mean absolute, in JND)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs 500–2k |
|---|---|---|---|---|---|---|---|---|
| EDT | measured (mean) | 1.60 | 1.36 | 1.34 | 1.31 | 1.24 | 1.05 | |
| | 3D mesh | +2.2 / 3.6 | +0.6 / 1.7 | -0.4 / 2.0 | +1.1 / 1.6 | +1.7 / 2.1 | +1.3 / 1.8 | 1.9 |
| | 3D mesh calibrated | +0.4 / 2.8 | +0.6 / 1.6 | -1.1 / 2.6 | +0.0 / 1.7 | +0.9 / 1.9 | +2.0 / 2.2 | 2.1 |
| | ↳ LS2 only (held out) | +1.1 / 2.7 | +1.7 / 1.8 | -0.5 / 2.6 | +1.3 / 2.0 | +2.3 / 2.3 | +3.5 / 3.5 | 2.3 |
| | 2.5D | +3.5 / 3.8 | +5.3 / 5.3 | +2.3 / 2.8 | +3.4 / 3.6 | +4.7 / 4.7 | +4.0 / 4.2 | 3.7 |
| T30 | measured (mean) | 1.63 | 1.45 | 1.30 | 1.34 | 1.32 | 1.06 | |
| | 3D mesh | +2.1 / 2.4 | +1.5 / 1.6 | +2.6 / 2.6 | +2.6 / 2.8 | +2.7 / 2.8 | +2.0 / 2.0 | 2.8 |
| | 3D mesh calibrated | -0.3 / 1.7 | -0.5 / 2.3 | -0.0 / 3.1 | +0.1 / 2.5 | +0.2 / 3.1 | +1.1 / 2.2 | 2.9 |
| | ↳ LS2 only (held out) | +0.3 / 2.6 | +0.4 / 3.0 | +1.0 / 4.7 | +0.8 / 3.8 | +1.0 / 4.3 | +2.2 / 3.6 | 4.3 |
| | 2.5D | +3.0 / 3.0 | +4.1 / 4.1 | +3.3 / 3.3 | +3.2 / 3.2 | +3.3 / 3.3 | +3.9 / 3.9 | 3.3 |
| C80 | measured (mean) | 0.59 | 0.86 | 1.47 | 1.71 | 1.59 | 3.24 | |
| | 3D mesh | -0.7 / 1.1 | +0.3 / 1.6 | +0.0 / 1.2 | -0.6 / 0.9 | -0.3 / 0.6 | -0.5 / 0.6 | 0.9 |
| | 3D mesh calibrated | -0.3 / 1.6 | +0.5 / 1.8 | +0.7 / 1.5 | +0.1 / 0.9 | +0.4 / 0.8 | -0.3 / 1.3 | 1.1 |
| | ↳ LS2 only (held out) | -1.2 / 1.7 | -0.6 / 1.0 | +0.8 / 1.5 | -0.1 / 1.1 | +0.0 / 0.7 | -1.0 / 1.6 | 1.1 |
| | 2.5D | -1.6 / 2.5 | -1.3 / 2.6 | -1.0 / 1.8 | -1.3 / 1.6 | -1.2 / 1.7 | -1.4 / 1.9 | 1.7 |
| C50 | measured (mean) | -2.66 | -1.16 | -1.21 | -1.16 | -1.50 | 0.37 | |
| | 3D mesh | +0.1 / 2.0 | -0.3 / 1.6 | +0.1 / 1.6 | -0.4 / 0.8 | +0.2 / 0.5 | -0.5 / 0.8 | 1.0 |
| | 3D mesh calibrated | +0.8 / 2.2 | +0.2 / 1.5 | +1.0 / 1.9 | +0.6 / 1.2 | +1.1 / 1.2 | +0.0 / 1.0 | 1.5 |
| | ↳ LS2 only (held out) | +0.6 / 2.7 | -0.3 / 1.0 | +0.9 / 1.8 | +0.4 / 1.3 | +1.1 / 1.1 | -0.3 / 1.0 | 1.4 |
| | 2.5D | -0.9 / 2.9 | -1.9 / 3.0 | -0.9 / 2.0 | -1.0 / 1.8 | -0.6 / 1.3 | -1.2 / 2.0 | 1.7 |
| Ts | measured (mean) | 111 | 97 | 94 | 92 | 91 | 70 | |
| | 3D mesh | +1.0 / 1.5 | +0.2 / 0.8 | -0.1 / 0.9 | +0.6 / 0.7 | +0.5 / 0.6 | +0.7 / 0.7 | 0.7 |
| | 3D mesh calibrated | -0.2 / 1.2 | -0.4 / 1.3 | -1.2 / 1.4 | -0.6 / 0.9 | -0.6 / 0.6 | +0.3 / 0.8 | 1.0 |
| | ↳ LS2 only (held out) | +0.8 / 1.1 | +0.3 / 0.7 | -1.1 / 1.4 | -0.2 / 0.8 | -0.3 / 0.4 | +0.7 / 1.1 | 0.9 |
| | 2.5D | +2.4 / 2.9 | +2.7 / 2.9 | +1.2 / 1.8 | +1.6 / 1.8 | +1.7 / 1.8 | +1.7 / 1.9 | 1.8 |

Measured Ts in ms; EDT / T30 in s; C80 / C50 in dB. JND: ISO 3382-1 Annex A.

## Early reflections (first-order image sources vs the measured RIR, 500 Hz–2 kHz)

Each predicted first-order reflection that is at least −15 dB re direct, at least 2 ms after the direct sound and 1.5 ms away from any other predicted one is compared with the measured energy in a 1 ms window at its predicted time (−0.2 … +0.8 ms), in dB re the same window on the direct sound. Controls: the measured level 2 ms later than predicted, and at random times 3–20 ms after the direct sound.

| model | reflections | predicted (median dB) | measured at predicted time | measured +2 ms later | measured at random times | predicted − measured (median / IQR dB) | correlation predicted vs measured |
|---|---|---|---|---|---|---|---|
| 3D mesh | 36 | -5.5 | -6.8 | -10.4 | -11.5 | +1.6 / +0.1 … +3.4 | 0.55 |
| 3D mesh calibrated | 36 | -5.6 | -6.8 | -10.4 | -11.5 | +1.4 / -0.1 … +3.3 | 0.55 |
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
