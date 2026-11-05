# Fratoni ULH: measured vs AuralPaths (Python engine)

Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria sheet (mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged.

```
ULH: OBJ 1099 faces -> 1099 after decimation -> 794 room-facing faces (295 hidden faces dropped), 1588 walls incl. back faces; room volume (voxels) 742 m3
surface areas (m2): Plaster 607.9, Seats 198.4, Windows 36.8, Wood 98.7; total 942
Sabine T (s), no air: 125 Hz 1.15, 250 Hz 1.12, 500 Hz 1.56, 1000 Hz 1.95, 2000 Hz 1.88, 4000 Hz 1.62
height above the surface below (m): S1 1.55, R1 0.56, R2 0.56, R3 0.56, R4 0.31, R5 0.25, R6 0.25, R7 0.25, R8 0.29, R9 0.40, R10 0.41, R11 0.41, R12 0.46, R13 0.46, R14 0.46, R15 0.46, R16 0.53, R17 0.63, R18 0.63, R19 0.63, R20 0.72, R21 0.74, R22 0.74, R23 0.74, R24 1.76, R25 0.96, R26 0.96
[3D mesh] S1: 26 receivers, 4011 s
2.5D hall: 36 plan vertices, 77 surfaces, volume 719.4 m3 (mesh 742.1); positions lifted above the averaged floor: none
[2.5D] S1: 26 receivers, 144 s
```

## S1, receivers: ALL THE RECEIVERS (26)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.33 | 1.31 | 1.56 | 1.84 | 1.79 | 1.44 | | |
| | 3D mesh | 1.23 (-1.6) | 1.17 (-2.1) | 1.60 (+0.6) | 1.91 (+0.7) | 1.81 (+0.2) | 1.43 (-0.1) | 0.7 | 0.9 |
| | 2.5D | 1.29 (-0.6) | 1.25 (-1.0) | 1.61 (+0.7) | 1.92 (+0.9) | 1.78 (-0.2) | 1.36 (-1.0) | 0.8 | 0.7 |
| T30 | measured | 1.56 | 1.36 | 1.62 | 1.85 | 1.83 | 1.50 | | |
| | 3D mesh | 1.39 (-2.3) | 1.28 (-1.2) | 1.70 (+0.9) | 1.94 (+1.0) | 1.84 (+0.1) | 1.43 (-0.9) | 0.9 | 1.1 |
| | 2.5D | 1.26 (-3.9) | 1.21 (-2.1) | 1.56 (-0.7) | 1.86 (+0.1) | 1.72 (-1.2) | 1.31 (-2.5) | 0.4 | 1.8 |
| C50 | measured | -1.90 | -1.50 | -2.00 | -3.40 | -3.00 | -1.90 | | |
| | 3D mesh | -0.49 (+1.4) | -0.30 (+1.2) | -2.21 (-0.2) | -3.25 (+0.2) | -2.99 (+0.0) | -1.68 (+0.2) | 0.2 | 0.5 |
| | 2.5D | -1.41 (+0.5) | -1.19 (+0.3) | -2.77 (-0.8) | -3.76 (-0.4) | -3.33 (-0.3) | -1.76 (+0.1) | 0.6 | 0.4 |
| Ts | measured | 99 | 93 | 108 | 133 | 127 | 102 | | |
| | 3D mesh | 84 (-1.5) | 81 (-1.2) | 112 (+0.4) | 135 (+0.2) | 128 (+0.1) | 100 (-0.2) | 0.3 | 0.6 |
| | 2.5D | 92 (-0.7) | 89 (-0.4) | 116 (+0.8) | 140 (+0.7) | 129 (+0.2) | 97 (-0.5) | 0.7 | 0.6 |

Not compared: STI = 0.47

Values in brackets: simulated - measured in JND (ISO 3382-1 Annex A: EDT / T30 5 %, C80 / C50 1 dB, Ts 10 ms).

2.5D conversion (obj_to_hall.py, --preserve eyring):

```
{
 "preserve": "eyring",
 "groups": {
  "aud": {
   "mesh_area_m2": 157.5,
   "hall_area_m2": 147.8,
   "mesh_absorption_area_m2": [
    37.52,
    35.41,
    25.92,
    19.47,
    18.28,
    18.67
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
   "mesh_area_m2": 433.3,
   "hall_area_m2": 240.0,
   "mesh_absorption_area_m2": [
    60.92,
    62.81,
    39.09,
    30.54,
    30.49,
    33.41
   ]
  },
  "ceil": {
   "mesh_area_m2": 309.5,
   "hall_area_m2": 184.2,
   "mesh_absorption_area_m2": [
    3.09,
    6.19,
    9.28,
    9.28,
    12.38,
    18.57
   ]
  }
 },
 "volume_mesh_m3": 742.1,
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
