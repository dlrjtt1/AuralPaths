# Fratoni ULH: measured vs AuralPaths (Python engine)

**Rerun 2026-11-19** with the mesh rules of that day (`validation/mesh_leak.md`) and the engine fixes of 2026-11-12, 20 000 rays as before. The run was made in three groups of receivers (R1-R9, R10-R18, R19-R26; one ray-tracing run each with the same seed) because of a run-time limit; with 400 rays the grouped run gave the same per-receiver file as one run for all 26. Against the tables this file held until then (794 faces, 295 dropped, volume 742 m3): 800 room faces, 251 faces behind the room's faces not counted, 780 m3; every value of the 3D mesh within 0.03 s (EDT, T30), 0.2 dB (C50) and 1 ms (Ts) of the earlier run, the 2.5D hall within 0.01 s, 0.07 dB and 1 ms; mean absolute errors changed by at most 0.2 JND.

Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria sheet (mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged.

```
ULH: OBJ 1099 faces -> 1099 after decimation -> 800 room faces (7 narrow ones kept two-sided; 251 behind the room's faces, 252.6 m2, kept but not counted; 38 not at the room dropped), 2102 walls incl. back faces; room volume (voxels) 780 m3
surface areas (m2): Plaster 610.5, Seats 197.9, Windows 36.8, Wood 99.6; total 945
Sabine T (s), no air: 125 Hz 1.21, 250 Hz 1.17, 500 Hz 1.64, 1000 Hz 2.05, 2000 Hz 1.98, 4000 Hz 1.70
height above the surface below (m): S1 1.55, R1 0.56, R2 0.56, R3 0.56, R4 0.31, R5 0.25, R6 0.25, R7 0.25, R8 0.29, R9 0.40, R10 0.41, R11 0.41, R12 0.46, R13 0.46, R14 0.46, R15 0.46, R16 0.53, R17 0.63, R18 0.63, R19 0.63, R20 0.72, R21 0.74, R22 0.74, R23 0.74, R24 1.76, R25 0.96, R26 0.96
[3D mesh] S1: 26 receivers, 11915 s (three receiver groups: 4423 + 3936 + 3556 s)
2.5D hall: 36 plan vertices, 77 surfaces, volume 719.4 m3 (mesh 780.4); positions lifted above the averaged floor: none
[2.5D] S1: 26 receivers, 185 s
```

## S1, receivers: ALL THE RECEIVERS (26)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.33 | 1.31 | 1.56 | 1.84 | 1.79 | 1.44 | | |
| | 3D mesh | 1.24 (-1.4) | 1.19 (-1.9) | 1.62 (+0.8) | 1.92 (+0.9) | 1.82 (+0.3) | 1.44 (+0.0) | 0.8 | 0.9 |
| | 2.5D | 1.28 (-0.8) | 1.23 (-1.2) | 1.61 (+0.6) | 1.93 (+0.9) | 1.78 (-0.2) | 1.35 (-1.2) | 0.8 | 0.8 |
| T30 | measured | 1.56 | 1.36 | 1.62 | 1.85 | 1.83 | 1.50 | | |
| | 3D mesh | 1.36 (-2.6) | 1.26 (-1.4) | 1.63 (+0.2) | 1.92 (+0.8) | 1.81 (-0.2) | 1.42 (-1.1) | 0.5 | 1.0 |
| | 2.5D | 1.27 (-3.8) | 1.22 (-2.0) | 1.58 (-0.5) | 1.89 (+0.4) | 1.74 (-0.9) | 1.32 (-2.4) | 0.5 | 1.7 |
| C50 | measured | -1.90 | -1.50 | -2.00 | -3.40 | -3.00 | -1.90 | | |
| | 3D mesh | -0.48 (+1.4) | -0.28 (+1.2) | -2.17 (-0.2) | -3.17 (+0.2) | -2.91 (+0.1) | -1.58 (+0.3) | 0.2 | 0.6 |
| | 2.5D | -1.39 (+0.5) | -1.15 (+0.3) | -2.74 (-0.7) | -3.73 (-0.3) | -3.29 (-0.3) | -1.70 (+0.2) | 0.5 | 0.4 |
| Ts | measured | 99 | 93 | 108 | 133 | 127 | 102 | | |
| | 3D mesh | 84 (-1.5) | 80 (-1.2) | 112 (+0.4) | 135 (+0.2) | 128 (+0.1) | 100 (-0.3) | 0.3 | 0.6 |
| | 2.5D | 92 (-0.7) | 88 (-0.5) | 116 (+0.8) | 140 (+0.7) | 129 (+0.2) | 97 (-0.6) | 0.7 | 0.6 |

Not compared: STI = 0.47

Values in brackets: simulated - measured in JND (ISO 3382-1 Annex A: EDT / T30 5 %, C80 / C50 1 dB, Ts 10 ms).

2.5D conversion (obj_to_hall.py, --preserve eyring):

```
{
 "preserve": "eyring",
 "groups": {
  "aud": {
   "mesh_area_m2": 157.0,
   "hall_area_m2": 147.8,
   "mesh_absorption_area_m2": [
    37.31,
    35.21,
    25.78,
    19.37,
    18.19,
    18.58
   ]
  },
  "stage": {
   "mesh_area_m2": 41.5,
   "hall_area_m2": 50.3,
   "mesh_absorption_area_m2": [
    2.41,
    2.62,
    2.42,
    2.06,
    2.33,
    3.0
   ]
  },
  "wall": {
   "mesh_area_m2": 434.2,
   "hall_area_m2": 240.0,
   "mesh_absorption_area_m2": [
    61.06,
    62.97,
    39.13,
    30.58,
    30.52,
    33.45
   ]
  },
  "ceil": {
   "mesh_area_m2": 312.0,
   "hall_area_m2": 184.2,
   "mesh_absorption_area_m2": [
    3.12,
    6.24,
    9.36,
    9.36,
    12.48,
    18.72
   ]
  }
 },
 "volume_mesh_m3": 780.4,
 "n_plan_vertices": 36,
 "n_floor": 25,
 "n_ceil": 17,
 "n_surfaces_2p5d": 77,
 "dims_m": [
  13.15,
  13.0,
  6.477
 ],
 "volume_2p5d_m3": 719.4
}
```
