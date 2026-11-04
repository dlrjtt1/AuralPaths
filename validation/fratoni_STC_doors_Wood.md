# Fratoni STC: measured vs AuralPaths (Python engine)

Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria sheet (mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged.

```
STC: OBJ 19025 faces -> 2998 after decimation -> 2815 room-facing faces (183 hidden faces dropped), 5630 walls incl. back faces; room volume (voxels) 816 m3
surface areas (m2): Ceiling 209.5, Plasterboard (walls) 128.6, Seats 50.1, Wood 222.7; total 611
Sabine T (s), no air: 125 Hz 1.47, 250 Hz 1.52, 500 Hz 1.53, 1000 Hz 1.46, 2000 Hz 1.67, 4000 Hz 1.67
height above the surface below (m): S1 1.58, S2 1.50, R1 1.23, R2 1.23, R3 1.23, R4 1.35, R5 1.45, R6 1.45, R7 1.35, R8 1.23, R9 1.23, R10 1.23
2.5D hall: 32 plan vertices, 71 surfaces, volume 804.8 m3 (mesh 816.4); positions lifted above the averaged floor: B_L 3.18->1.58, B_R 3.18->1.58
[2.5D] S1: 10 receivers, 42 s
[2.5D] S2: 4 receivers, 24 s
```

## S1, receivers: (R1,R2,R3,R4,R5,R6,R7,R8,R9,R10) (10)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.34 | 1.32 | 1.31 | 1.31 | 1.41 | 1.27 | | |
| | 2.5D | 1.75 (+6.1) | 1.78 (+7.0) | 1.77 (+7.1) | 1.68 (+5.6) | 1.83 (+5.9) | 1.59 (+5.0) | 6.3 | 6.1 |
| T30 | measured | 1.09 | 1.25 | 1.27 | 1.32 | 1.36 | 1.19 | | |
| | 2.5D | 1.54 (+8.2) | 1.57 (+5.1) | 1.56 (+4.6) | 1.48 (+2.4) | 1.60 (+3.6) | 1.40 (+3.6) | 3.5 | 4.6 |
| C80 | measured | 0.19 | 0.05 | 1.15 | 1.43 | 1.39 | 2.02 | | |
| | 2.5D | -0.52 (-0.7) | -0.65 (-0.7) | -0.61 (-1.8) | -0.20 (-1.6) | -0.80 (-2.2) | 0.18 (-1.8) | 1.7 | 1.5 |
| Ts | measured | 96 | 96 | 85 | 86 | 87 | 78 | | |
| | 2.5D | 117 (+2.1) | 120 (+2.4) | 119 (+3.4) | 111 (+2.5) | 123 (+3.6) | 104 (+2.6) | 2.9 | 2.8 |

## S2, receivers: (R3,R4,R5,R8) (4)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.00 | 1.25 | 1.23 | 1.27 | 1.26 | 1.21 | | |
| | 2.5D | 1.47 (+9.4) | 1.50 (+4.0) | 1.49 (+4.3) | 1.41 (+2.1) | 1.54 (+4.4) | 1.32 (+1.9) | 3.2 | 4.4 |
| T30 | measured | 1.01 | 1.32 | 1.35 | 1.31 | 1.33 | 1.16 | | |
| | 2.5D | 1.51 (+9.8) | 1.54 (+3.3) | 1.53 (+2.7) | 1.45 (+2.1) | 1.57 (+3.7) | 1.37 (+3.6) | 2.4 | 4.2 |
| C80 | measured | 1.91 | 0.94 | 2.39 | 1.62 | 1.61 | 1.91 | | |
| | 2.5D | 0.95 (-1.0) | 0.82 (-0.1) | 0.86 (-1.5) | 1.21 (-0.4) | 0.68 (-0.9) | 1.57 (-0.3) | 1.0 | 0.7 |
| Ts | measured | 89 | 100 | 81 | 85 | 88 | 82 | | |
| | 2.5D | 104 (+1.5) | 107 (+0.7) | 106 (+2.5) | 100 (+1.5) | 109 (+2.1) | 95 (+1.3) | 2.0 | 1.6 |

Values in brackets: simulated - measured in JND (ISO 3382-1 Annex A: EDT / T30 5 %, C80 / C50 1 dB, Ts 10 ms).

2.5D conversion (obj_to_hall.py, --preserve eyring):

```
{
 "groups": {
  "aud": {
   "mesh_area_m2": 156.7,
   "hall_area_m2": 166.8,
   "mesh_absorption_area_m2": [
    26.23,
    26.65,
    25.74,
    26.18,
    20.34,
    20.34
   ]
  },
  "wall": {
   "mesh_area_m2": 253.3,
   "hall_area_m2": 202.7,
   "mesh_absorption_area_m2": [
    45.11,
    41.83,
    42.31,
    43.74,
    38.4,
    38.4
   ]
  },
  "ceil": {
   "mesh_area_m2": 200.9,
   "hall_area_m2": 161.4,
   "mesh_absorption_area_m2": [
    18.09,
    18.09,
    18.08,
    20.09,
    20.08,
    20.08
   ]
  }
 },
 "volume_mesh_m3": 816.4,
 "n_plan_vertices": 32,
 "n_floor": 21,
 "n_ceil": 20,
 "n_surfaces_2p5d": 71,
 "dims_m": [
  11.0,
  17.65,
  6.564
 ],
 "volume_2p5d_m3": 804.8
}
```
