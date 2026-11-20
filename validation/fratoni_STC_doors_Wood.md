# Fratoni STC: measured vs AuralPaths (page's engine through engine_js.py)

**Computed with the page's engine since 2026-11-20** (`validate_fratoni.py`, default `--engine js`: the energy histograms of the 3D mesh and of the 2.5D hall come from the engine of the web page through `engine_js.py`; same rays as before).  The Python-engine file is in the history of this file (commit 558b1e6 and before).

Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria sheet (mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged.

```
STC: OBJ 19025 faces -> 2998 after decimation -> 2915 room faces (105 narrow ones kept two-sided; 83 behind the room's faces, 20.9 m2, kept but not counted; 0 not at the room dropped), 5996 walls incl. back faces; room volume (voxels) 842 m3
surface areas (m2): Ceiling 209.5, Plasterboard (walls) 128.6, Seats 50.6, Wood 225.3; total 614
Sabine T (s), no air: 125 Hz 1.51, 250 Hz 1.56, 500 Hz 1.56, 1000 Hz 1.50, 2000 Hz 1.71, 4000 Hz 1.71
height above the surface below (m): S1 1.58, S2 1.50, R1 1.23, R2 1.23, R3 1.23, R4 1.35, R5 1.45, R6 1.45, R7 1.35, R8 1.23, R9 1.23, R10 1.23
2.5D hall: 32 plan vertices, 71 surfaces, volume 804.8 m3 (mesh 842.4); positions lifted above the averaged floor: B_L 3.18->1.58, B_R 3.18->1.58
[2.5D] S1: 10 receivers, 5 s
[2.5D] S2: 4 receivers, 4 s
```

## S1, receivers: (R1,R2,R3,R4,R5,R6,R7,R8,R9,R10) (10)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.34 | 1.32 | 1.31 | 1.31 | 1.41 | 1.27 | | |
| | 2.5D | 1.62 (+4.2) | 1.66 (+5.2) | 1.65 (+5.2) | 1.56 (+3.8) | 1.71 (+4.2) | 1.49 (+3.4) | 4.5 | 4.3 |
| T30 | measured | 1.09 | 1.25 | 1.27 | 1.32 | 1.36 | 1.19 | | |
| | 2.5D | 1.49 (+7.4) | 1.53 (+4.5) | 1.52 (+3.9) | 1.44 (+1.8) | 1.57 (+3.1) | 1.37 (+3.0) | 2.9 | 3.9 |
| C80 | measured | 0.19 | 0.05 | 1.15 | 1.43 | 1.39 | 2.02 | | |
| | 2.5D | 0.44 (+0.2) | 0.33 (+0.3) | 0.43 (-0.7) | 0.80 (-0.6) | 0.17 (-1.2) | 1.12 (-0.9) | 0.7 | 0.7 |
| Ts | measured | 96 | 96 | 85 | 86 | 87 | 78 | | |
| | 2.5D | 104 (+0.8) | 107 (+1.1) | 105 (+2.0) | 99 (+1.3) | 110 (+2.3) | 93 (+1.5) | 1.6 | 1.5 |

## S2, receivers: (R3,R4,R5,R8) (4)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.00 | 1.25 | 1.23 | 1.27 | 1.26 | 1.21 | | |
| | 2.5D | 1.36 (+7.1) | 1.39 (+2.3) | 1.38 (+2.5) | 1.31 (+0.6) | 1.43 (+2.7) | 1.24 (+0.5) | 1.5 | 2.6 |
| T30 | measured | 1.01 | 1.32 | 1.35 | 1.31 | 1.33 | 1.16 | | |
| | 2.5D | 1.45 (+8.7) | 1.49 (+2.5) | 1.48 (+1.9) | 1.40 (+1.3) | 1.53 (+3.0) | 1.33 (+2.9) | 1.6 | 3.4 |
| C80 | measured | 1.91 | 0.94 | 2.39 | 1.62 | 1.61 | 1.91 | | |
| | 2.5D | 1.70 (-0.2) | 1.54 (+0.6) | 1.61 (-0.8) | 1.93 (+0.3) | 1.41 (-0.2) | 2.29 (+0.4) | 0.5 | 0.4 |
| Ts | measured | 89 | 100 | 81 | 85 | 88 | 82 | | |
| | 2.5D | 94 (+0.5) | 97 (-0.3) | 96 (+1.5) | 91 (+0.6) | 99 (+1.1) | 86 (+0.4) | 1.0 | 0.7 |

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
    26.47,
    26.9,
    26.03,
    26.53,
    20.65,
    20.65
   ]
  },
  "wall": {
   "mesh_area_m2": 255.3,
   "hall_area_m2": 202.7,
   "mesh_absorption_area_m2": [
    45.4,
    42.13,
    42.54,
    43.93,
    38.51,
    38.51
   ]
  },
  "ceil": {
   "mesh_area_m2": 200.9,
   "hall_area_m2": 161.4,
   "mesh_absorption_area_m2": [
    18.09,
    18.09,
    18.09,
    20.09,
    20.08,
    20.08
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
