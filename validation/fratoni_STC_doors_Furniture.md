# Fratoni STC: measured vs AuralPaths (Python engine)

Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria sheet (mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged.

```
STC: OBJ 19025 faces -> 2998 after decimation -> 2815 room-facing faces (183 hidden faces dropped), 5630 walls incl. back faces; room volume (voxels) 816 m3
surface areas (m2): Ceiling 209.5, Furniture 29.1, Plasterboard (walls) 128.6, Seats 50.1, Wood 193.5; total 611
Sabine T (s), no air: 125 Hz 1.41, 250 Hz 1.47, 500 Hz 1.49, 1000 Hz 1.43, 2000 Hz 1.63, 4000 Hz 1.63
height above the surface below (m): S1 1.58, S2 1.50, R1 1.23, R2 1.23, R3 1.23, R4 1.35, R5 1.45, R6 1.45, R7 1.35, R8 1.23, R9 1.23, R10 1.23
2.5D hall: 32 plan vertices, 71 surfaces, volume 804.8 m3 (mesh 816.4); positions lifted above the averaged floor: B_L 3.18->1.58, B_R 3.18->1.58
[2.5D] S1: 10 receivers, 46 s
[2.5D] S2: 4 receivers, 25 s
```

## S1, receivers: (R1,R2,R3,R4,R5,R6,R7,R8,R9,R10) (10)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.34 | 1.32 | 1.31 | 1.31 | 1.41 | 1.27 | | |
| | 2.5D | 1.70 (+5.4) | 1.74 (+6.4) | 1.75 (+6.6) | 1.66 (+5.3) | 1.81 (+5.6) | 1.57 (+4.7) | 6.0 | 5.7 |
| T30 | measured | 1.09 | 1.25 | 1.27 | 1.32 | 1.36 | 1.19 | | |
| | 2.5D | 1.48 (+7.2) | 1.52 (+4.3) | 1.52 (+3.9) | 1.45 (+2.0) | 1.57 (+3.1) | 1.38 (+3.2) | 3.0 | 4.0 |
| C80 | measured | 0.19 | 0.05 | 1.15 | 1.43 | 1.39 | 2.02 | | |
| | 2.5D | -0.17 (-0.4) | -0.34 (-0.4) | -0.35 (-1.5) | 0.02 (-1.4) | -0.57 (-2.0) | 0.41 (-1.6) | 1.5 | 1.2 |
| Ts | measured | 96 | 96 | 85 | 86 | 87 | 78 | | |
| | 2.5D | 112 (+1.6) | 115 (+1.9) | 115 (+3.0) | 108 (+2.2) | 120 (+3.3) | 102 (+2.4) | 2.6 | 2.4 |

## S2, receivers: (R3,R4,R5,R8) (4)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.00 | 1.25 | 1.23 | 1.27 | 1.26 | 1.21 | | |
| | 2.5D | 1.44 (+8.8) | 1.48 (+3.8) | 1.48 (+4.1) | 1.41 (+2.2) | 1.54 (+4.4) | 1.33 (+2.1) | 3.2 | 4.2 |
| T30 | measured | 1.01 | 1.32 | 1.35 | 1.31 | 1.33 | 1.16 | | |
| | 2.5D | 1.45 (+8.7) | 1.49 (+2.6) | 1.49 (+2.1) | 1.42 (+1.6) | 1.54 (+3.2) | 1.34 (+3.1) | 1.9 | 3.5 |
| C80 | measured | 1.91 | 0.94 | 2.39 | 1.62 | 1.61 | 1.91 | | |
| | 2.5D | 1.02 (-0.9) | 0.84 (-0.1) | 0.84 (-1.5) | 1.16 (-0.5) | 0.63 (-1.0) | 1.52 (-0.4) | 1.0 | 0.7 |
| Ts | measured | 89 | 100 | 81 | 85 | 88 | 82 | | |
| | 2.5D | 102 (+1.3) | 105 (+0.5) | 105 (+2.4) | 100 (+1.5) | 109 (+2.1) | 95 (+1.3) | 2.0 | 1.5 |

Values in brackets: simulated - measured in JND (ISO 3382-1 Annex A: EDT / T30 5 %, C80 / C50 1 dB, Ts 10 ms).

2.5D conversion (obj_to_hall.py, --preserve eyring):

```
{
 "groups": {
  "aud": {
   "mesh_area_m2": 156.7,
   "hall_area_m2": 166.8,
   "mesh_absorption_area_m2": [
    26.49,
    26.85,
    25.9,
    26.3,
    20.45,
    20.45
   ]
  },
  "wall": {
   "mesh_area_m2": 253.3,
   "hall_area_m2": 202.7,
   "mesh_absorption_area_m2": [
    48.61,
    44.53,
    44.46,
    45.35,
    40.01,
    40.01
   ]
  },
  "ceil": {
   "mesh_area_m2": 200.9,
   "hall_area_m2": 161.4,
   "mesh_absorption_area_m2": [
    18.12,
    18.11,
    18.1,
    20.1,
    20.09,
    20.09
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
