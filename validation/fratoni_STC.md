# Fratoni STC: measured vs AuralPaths (Python engine)

**Rerun 2026-11-19** with the mesh rules of that day (`validation/mesh_leak.md`: narrow faces kept two-sided, faces behind the room's faces kept but not counted) and the engine fixes of 2026-11-12, 6 000 rays as before. Against the tables this file held until then (run of 2026-11-06, 2815 faces, 183 dropped, volume 816 m3): the mesh has 2915 room faces and 842 m3; 3D mesh T30 0 - 0.04 s longer and EDT 0.02 - 0.07 s longer, C80 0.2 - 0.6 dB higher; 2.5D T30 within 0.01 s, 2.5D EDT of S1 0.02 - 0.03 s shorter, 2.5D C80 of S1 about 0.25 dB higher and of S2 about 0.15 dB lower. Mean absolute errors changed by at most 0.8 JND (3D mesh EDT of S2, 500 Hz - 1 kHz: 3.4 -> 4.2).

Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria sheet (mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged.

```
STC: OBJ 19025 faces -> 2998 after decimation -> 2915 room faces (105 narrow ones kept two-sided; 70 behind the room's faces, 18.0 m2, kept but not counted; 13 not at the room dropped), 5970 walls incl. back faces; room volume (voxels) 842 m3
surface areas (m2): Ceiling 209.5, Furniture 30.2, Plasterboard (walls) 128.6, Seats 50.6, Wood 195.1; total 614
Sabine T (s), no air: 125 Hz 1.44, 250 Hz 1.50, 500 Hz 1.52, 1000 Hz 1.47, 2000 Hz 1.67, 4000 Hz 1.67
height above the surface below (m): S1 1.58, S2 1.50, R1 1.23, R2 1.23, R3 1.23, R4 1.35, R5 1.45, R6 1.45, R7 1.35, R8 1.23, R9 1.23, R10 1.23
[3D mesh] S1: 10 receivers, 2886 s
[3D mesh] S2: 4 receivers, 2039 s
2.5D hall: 32 plan vertices, 71 surfaces, volume 804.8 m3 (mesh 842.4); positions lifted above the averaged floor: B_L 3.18->1.58, B_R 3.18->1.58
[2.5D] S1: 10 receivers, 12 s
[2.5D] S2: 4 receivers, 7 s
```

## S1, receivers: (R1,R2,R3,R4,R5,R6,R7,R8,R9,R10) (10)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.34 | 1.32 | 1.31 | 1.31 | 1.41 | 1.27 | | |
| | 3D mesh | 1.59 (+3.8) | 1.64 (+4.9) | 1.66 (+5.4) | 1.61 (+4.6) | 1.75 (+4.8) | 1.53 (+4.0) | 5.0 | 4.6 |
| | 2.5D | 1.69 (+5.3) | 1.74 (+6.3) | 1.74 (+6.6) | 1.65 (+5.3) | 1.80 (+5.6) | 1.57 (+4.8) | 5.9 | 5.6 |
| T30 | measured | 1.09 | 1.25 | 1.27 | 1.32 | 1.36 | 1.19 | | |
| | 3D mesh | 1.49 (+7.3) | 1.54 (+4.7) | 1.56 (+4.6) | 1.51 (+2.9) | 1.64 (+4.2) | 1.43 (+4.0) | 3.8 | 4.6 |
| | 2.5D | 1.50 (+7.5) | 1.54 (+4.6) | 1.54 (+4.2) | 1.46 (+2.2) | 1.59 (+3.4) | 1.39 (+3.4) | 3.2 | 4.2 |
| C80 | measured | 0.19 | 0.05 | 1.15 | 1.43 | 1.39 | 2.02 | | |
| | 3D mesh | 0.28 (+0.1) | 0.07 (+0.0) | -0.01 (-1.2) | 0.25 (-1.2) | -0.34 (-1.7) | 0.61 (-1.4) | 1.2 | 0.9 |
| | 2.5D | -0.15 (-0.3) | -0.29 (-0.3) | -0.23 (-1.4) | 0.12 (-1.3) | -0.52 (-1.9) | 0.46 (-1.6) | 1.3 | 1.1 |
| Ts | measured | 96 | 96 | 85 | 86 | 87 | 78 | | |
| | 3D mesh | 107 (+1.1) | 111 (+1.5) | 113 (+2.8) | 108 (+2.2) | 119 (+3.2) | 102 (+2.4) | 2.5 | 2.2 |
| | 2.5D | 111 (+1.5) | 114 (+1.8) | 113 (+2.8) | 107 (+2.1) | 119 (+3.2) | 101 (+2.3) | 2.5 | 2.3 |

## S2, receivers: (R3,R4,R5,R8) (4)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.00 | 1.25 | 1.23 | 1.27 | 1.26 | 1.21 | | |
| | 3D mesh | 1.47 (+9.4) | 1.52 (+4.3) | 1.54 (+5.0) | 1.49 (+3.4) | 1.63 (+5.9) | 1.41 (+3.2) | 4.2 | 5.2 |
| | 2.5D | 1.44 (+8.9) | 1.49 (+3.8) | 1.49 (+4.2) | 1.41 (+2.3) | 1.54 (+4.4) | 1.34 (+2.1) | 3.2 | 4.3 |
| T30 | measured | 1.01 | 1.32 | 1.35 | 1.31 | 1.33 | 1.16 | | |
| | 3D mesh | 1.48 (+9.3) | 1.53 (+3.1) | 1.53 (+2.6) | 1.47 (+2.5) | 1.61 (+4.2) | 1.39 (+4.0) | 2.6 | 4.3 |
| | 2.5D | 1.45 (+8.7) | 1.49 (+2.5) | 1.49 (+2.0) | 1.42 (+1.6) | 1.54 (+3.1) | 1.34 (+3.2) | 1.8 | 3.5 |
| C80 | measured | 1.91 | 0.94 | 2.39 | 1.62 | 1.61 | 1.91 | | |
| | 3D mesh | 1.09 (-0.8) | 0.80 (-0.1) | 0.73 (-1.7) | 0.96 (-0.7) | 0.38 (-1.2) | 1.28 (-0.6) | 1.2 | 0.9 |
| | 2.5D | 0.84 (-1.1) | 0.66 (-0.3) | 0.68 (-1.7) | 0.96 (-0.7) | 0.48 (-1.1) | 1.39 (-0.5) | 1.2 | 0.9 |
| Ts | measured | 89 | 100 | 81 | 85 | 88 | 82 | | |
| | 3D mesh | 102 (+1.3) | 106 (+0.6) | 107 (+2.6) | 104 (+1.9) | 114 (+2.6) | 98 (+1.6) | 2.3 | 1.8 |
| | 2.5D | 103 (+1.4) | 106 (+0.6) | 106 (+2.5) | 101 (+1.6) | 110 (+2.2) | 95 (+1.3) | 2.1 | 1.6 |

Values in brackets: simulated - measured in JND (ISO 3382-1 Annex A: EDT / T30 5 %, C80 / C50 1 dB, Ts 10 ms).

2.5D conversion (obj_to_hall.py, --preserve eyring):

```
{
 "preserve": "eyring",
 "groups": {
  "aud": {
   "mesh_area_m2": 157.8,
   "hall_area_m2": 166.8,
   "mesh_absorption_area_m2": [
    26.72,
    27.09,
    26.19,
    26.65,
    20.77,
    20.77
   ]
  },
  "wall": {
   "mesh_area_m2": 255.3,
   "hall_area_m2": 202.7,
   "mesh_absorption_area_m2": [
    49.04,
    44.92,
    44.78,
    45.61,
    40.19,
    40.19
   ]
  },
  "ceil": {
   "mesh_area_m2": 200.9,
   "hall_area_m2": 161.4,
   "mesh_absorption_area_m2": [
    18.12,
    18.12,
    18.11,
    20.1,
    20.09,
    20.09
   ]
  }
 },
 "volume_mesh_m3": 842.4,
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
