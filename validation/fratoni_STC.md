# Fratoni STC: measured vs AuralPaths (page's engine through engine_js.py)

**Computed with the page's engine since 2026-11-20** (`validate_fratoni.py`, default `--engine js`: the energy histograms of the 3D mesh and of the 2.5D hall come from the engine of the web page through `engine_js.py`; same rays as before). With the Python engine (rerun of 2026-11-19, 6 000 rays) the 3D mesh gave T30 1.56 / 1.51 / 1.64 / 1.43 s at 500 Hz - 4 kHz for S1 (page's engine: 1.61 / 1.56 / 1.71 / 1.47; measured 1.27 / 1.32 / 1.36 / 1.19). The Python-engine file is in the history of this file (commit 558b1e6 and before).

Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria sheet (mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged.

```
STC: OBJ 19025 faces -> 2998 after decimation -> 2915 room faces (105 narrow ones kept two-sided; 83 behind the room's faces, 20.9 m2, kept but not counted; 0 not at the room dropped), 5996 walls incl. back faces; room volume (voxels) 842 m3
surface areas (m2): Ceiling 209.5, Furniture 30.2, Plasterboard (walls) 128.6, Seats 50.6, Wood 195.1; total 614
Sabine T (s), no air: 125 Hz 1.44, 250 Hz 1.50, 500 Hz 1.52, 1000 Hz 1.47, 2000 Hz 1.67, 4000 Hz 1.67
height above the surface below (m): S1 1.58, S2 1.50, R1 1.23, R2 1.23, R3 1.23, R4 1.35, R5 1.45, R6 1.45, R7 1.35, R8 1.23, R9 1.23, R10 1.23
[3D mesh] S1: 10 receivers, 552 s
[3D mesh] S2: 4 receivers, 482 s
2.5D hall: 32 plan vertices, 71 surfaces, volume 804.8 m3 (mesh 842.4); positions lifted above the averaged floor: B_L 3.18->1.58, B_R 3.18->1.58
[2.5D] S1: 10 receivers, 1 s
[2.5D] S2: 4 receivers, 1 s
```

## S1, receivers: (R1,R2,R3,R4,R5,R6,R7,R8,R9,R10) (10)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.34 | 1.32 | 1.31 | 1.31 | 1.41 | 1.27 | | |
| | 3D mesh | 1.66 (+4.7) | 1.71 (+6.0) | 1.73 (+6.4) | 1.67 (+5.6) | 1.84 (+6.1) | 1.58 (+4.9) | 6.0 | 5.6 |
| | 2.5D | 1.57 (+3.5) | 1.62 (+4.6) | 1.62 (+4.8) | 1.55 (+3.6) | 1.68 (+3.9) | 1.48 (+3.3) | 4.2 | 3.9 |
| T30 | measured | 1.09 | 1.25 | 1.27 | 1.32 | 1.36 | 1.19 | | |
| | 3D mesh | 1.54 (+8.2) | 1.60 (+5.5) | 1.61 (+5.4) | 1.56 (+3.7) | 1.71 (+5.1) | 1.47 (+4.7) | 4.5 | 5.4 |
| | 2.5D | 1.42 (+6.1) | 1.47 (+3.6) | 1.47 (+3.2) | 1.41 (+1.3) | 1.53 (+2.5) | 1.34 (+2.5) | 2.2 | 3.2 |
| C80 | measured | 0.19 | 0.05 | 1.15 | 1.43 | 1.39 | 2.02 | | |
| | 3D mesh | -0.22 (-0.4) | -0.43 (-0.5) | -0.48 (-1.6) | -0.21 (-1.6) | -0.79 (-2.2) | 0.22 (-1.8) | 1.6 | 1.4 |
| | 2.5D | 0.68 (+0.5) | 0.52 (+0.5) | 0.59 (-0.6) | 0.91 (-0.5) | 0.29 (-1.1) | 1.23 (-0.8) | 0.5 | 0.7 |
| Ts | measured | 96 | 96 | 85 | 86 | 87 | 78 | | |
| | 3D mesh | 113 (+1.7) | 117 (+2.1) | 119 (+3.4) | 114 (+2.8) | 126 (+3.9) | 107 (+2.9) | 3.1 | 2.8 |
| | 2.5D | 99 (+0.3) | 102 (+0.6) | 102 (+1.7) | 96 (+1.0) | 107 (+2.0) | 91 (+1.3) | 1.3 | 1.2 |

## S2, receivers: (R3,R4,R5,R8) (4)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.00 | 1.25 | 1.23 | 1.27 | 1.26 | 1.21 | | |
| | 3D mesh | 1.47 (+9.4) | 1.52 (+4.3) | 1.53 (+4.9) | 1.47 (+3.2) | 1.62 (+5.7) | 1.39 (+2.9) | 4.1 | 5.1 |
| | 2.5D | 1.27 (+5.4) | 1.32 (+1.0) | 1.31 (+1.4) | 1.25 (-0.2) | 1.37 (+1.8) | 1.19 (-0.3) | 0.8 | 1.7 |
| T30 | measured | 1.01 | 1.32 | 1.35 | 1.31 | 1.33 | 1.16 | | |
| | 3D mesh | 1.53 (+10.4) | 1.61 (+4.3) | 1.62 (+4.0) | 1.56 (+3.7) | 1.69 (+5.5) | 1.44 (+4.8) | 3.8 | 5.4 |
| | 2.5D | 1.39 (+7.5) | 1.44 (+1.8) | 1.44 (+1.3) | 1.37 (+0.9) | 1.50 (+2.5) | 1.30 (+2.4) | 1.1 | 2.7 |
| C80 | measured | 1.91 | 0.94 | 2.39 | 1.62 | 1.61 | 1.91 | | |
| | 3D mesh | 0.42 (-1.5) | 0.14 (-0.8) | 0.10 (-2.3) | 0.33 (-1.3) | -0.19 (-1.8) | 0.74 (-1.2) | 1.8 | 1.5 |
| | 2.5D | 2.13 (+0.2) | 1.91 (+1.0) | 1.94 (-0.5) | 2.23 (+0.6) | 1.74 (+0.1) | 2.61 (+0.7) | 0.5 | 0.5 |
| Ts | measured | 89 | 100 | 81 | 85 | 88 | 82 | | |
| | 3D mesh | 107 (+1.8) | 111 (+1.1) | 112 (+3.1) | 108 (+2.3) | 118 (+3.0) | 101 (+1.9) | 2.7 | 2.2 |
| | 2.5D | 89 (-0.0) | 92 (-0.8) | 92 (+1.1) | 88 (+0.3) | 95 (+0.7) | 83 (+0.1) | 0.7 | 0.5 |

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
