# Fratoni TCB: measured vs AuralPaths (browser engine)

**Rerun on 2026-11-19 with the engine after the fixes of 2026-11-18 and 2026-11-19** (`validation/mesh_leak.md`). The run of 2026-11-07 had 1154 faces dropped and lost 17 - 20 % of the rays; now 0.27 - 0.28 % are lost (still above the 0.1 % limit: the results stand with that reservation). 708 faces (815 m²) lie behind the room's faces; they stay in the model and are not counted in the surface (11169 m²; 11101 m² in the run of 2026-11-07; the run of 2026-11-18 counted them, 11984 m²). Mean absolute error over all bands and zones, 2026-11-07 → now: T30 3.20 → 3.2 JND, EDT 6.92 → 6.5, C80 2.67 → 2.4, Ts 3.32 → 3.2.

Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria sheet (mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged. Positions and tag-to-material assignments: validate_fratoni.py (VENUES); heights are assumptions (see there).

```
TCB: OBJ 5997 faces (435 narrow faces kept two-sided; 708 behind the room's faces, 815 m2, kept but not counted; 4 not at the room and 0 untagged ones in the surface band left out), voxel 0.120 m, room volume (voxels) 27149 m3; model built in 19 s
surface areas (m2): Carpet 790, Marble 97, Plaster (boxes) 3346, Seats 259, Stage grid 477, Stage house 4221, Velvet drapes 476, Wood 1501; total 11169
Sabine T (s), no air: 125 Hz 1.77, 250 Hz 1.51, 500 Hz 1.43, 1000 Hz 1.43, 2000 Hz 1.49, 4000 Hz 1.51
tags -> materials: Plaster_(hall) -> Plaster (boxes), Plaster_(gallery) -> Plaster (boxes), Plaster_(fly_tower) -> Stage house, Floor_(boxes) -> Carpet, Floor_(gallery) -> Carpet, Carpet -> Carpet, Marble -> Marble, Wood -> Wood, Seats -> Seats, Stage_grid -> Stage grid, Curtains -> Velvet drapes, Velvet_(fly_tower) -> Velvet drapes, PVC -> Stage house
browser engine: image sources to order 2, 20000 rays per source; S2 52 s (53 rays lost), S3 54 s (55 rays lost); total 125 s
```

## S2, STALLS (R3,R5,R7,R8,R10,R11) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.61 | 1.71 | 1.62 | 1.57 | 1.38 | 1.11 | | |
| | browser 3D | 1.33 (-3.5) | 1.05 (-7.7) | 0.94 (-8.4) | 0.94 (-8.1) | 0.90 (-6.9) | 0.88 (-4.0) | 8.2 | 6.4 |
| T30 | measured | 1.82 | 1.70 | 1.58 | 1.48 | 1.32 | 1.12 | | |
| | browser 3D | 1.61 (-2.3) | 1.37 (-3.9) | 1.26 (-4.0) | 1.23 (-3.5) | 1.30 (-0.3) | 1.12 (+0.1) | 3.7 | 2.3 |
| C80 | measured | -2.40 | -0.46 | 1.34 | 1.09 | 1.01 | 1.40 | | |
| | browser 3D | 2.41 (+4.8) | 4.16 (+4.6) | 4.86 (+3.5) | 4.91 (+3.8) | 5.11 (+4.1) | 5.50 (+4.1) | 3.7 | 4.2 |
| Ts | measured | 157 | 107 | 119 | 101 | 100 | 97 | | |
| | browser 3D | 88 (-6.8) | 68 (-3.9) | 61 (-5.8) | 60 (-4.0) | 59 (-4.1) | 56 (-4.1) | 4.9 | 4.8 |

## S2, BOXES (R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, R22, R23) (12)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.49 | 1.43 | 1.34 | 1.27 | 1.14 | 0.97 | | |
| | browser 3D | 1.42 (-1.0) | 1.02 (-5.7) | 0.86 (-7.3) | 0.85 (-6.6) | 0.79 (-6.1) | 0.70 (-5.6) | 6.9 | 5.4 |
| T30 | measured | 1.82 | 1.69 | 1.57 | 1.46 | 1.31 | 1.12 | | |
| | browser 3D | 1.55 (-3.0) | 1.35 (-4.1) | 1.32 (-3.1) | 1.28 (-2.5) | 1.39 (+1.2) | 1.22 (+1.9) | 2.8 | 2.6 |
| C80 | measured | -0.26 | 1.53 | 1.73 | 2.36 | 2.76 | 3.27 | | |
| | browser 3D | 1.31 (+1.6) | 4.03 (+2.5) | 5.47 (+3.7) | 5.52 (+3.2) | 5.93 (+3.2) | 6.81 (+3.5) | 3.4 | 2.9 |
| Ts | measured | 136 | 105 | 97 | 91 | 84 | 77 | | |
| | browser 3D | 99 (-3.8) | 72 (-3.3) | 61 (-3.6) | 60 (-3.1) | 58 (-2.6) | 52 (-2.5) | 3.4 | 3.2 |

## S2, GALLERY (R24, R25) (2)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 2.07 | 1.80 | 1.78 | 1.57 | 1.45 | 1.24 | | |
| | browser 3D | 1.34 (-7.1) | 0.91 (-9.8) | 0.76 (-11.4) | 0.77 (-10.1) | 0.76 (-9.5) | 0.70 (-8.7) | 10.8 | 9.4 |
| T30 | measured | 1.92 | 1.68 | 1.61 | 1.52 | 1.36 | 1.14 | | |
| | browser 3D | 1.74 (-1.9) | 1.23 (-5.4) | 1.12 (-6.1) | 1.14 (-5.0) | 1.19 (-2.5) | 1.02 (-2.1) | 5.6 | 3.8 |
| C80 | measured | -1.80 | -0.80 | -0.72 | -0.01 | 0.76 | 0.80 | | |
| | browser 3D | -1.41 (+0.4) | 0.60 (+1.4) | 1.67 (+2.4) | 1.69 (+1.7) | 2.03 (+1.3) | 2.74 (+1.9) | 2.0 | 1.5 |
| Ts | measured | 128 | 148 | 126 | 120 | 105 | 95 | | |
| | browser 3D | 117 (-1.1) | 95 (-5.3) | 87 (-3.9) | 87 (-3.3) | 86 (-1.9) | 80 (-1.5) | 3.6 | 2.8 |

## S3, STALLS (R3,R5,R7,R8,R10,R11) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.50 | 1.48 | 1.52 | 1.51 | 1.48 | 1.33 | | |
| | browser 3D | 1.48 (-0.2) | 1.16 (-4.3) | 1.16 (-4.7) | 1.18 (-4.5) | 1.22 (-3.5) | 1.42 (+1.3) | 4.6 | 3.1 |
| T30 | measured | 1.93 | 1.70 | 1.55 | 1.53 | 1.45 | 1.30 | | |
| | browser 3D | 1.60 (-3.4) | 1.31 (-4.6) | 1.33 (-2.9) | 1.30 (-3.0) | 1.32 (-1.8) | 1.40 (+1.6) | 2.9 | 2.9 |
| C80 | measured | -2.00 | -1.46 | -1.43 | -1.87 | -1.29 | -0.80 | | |
| | browser 3D | -3.97 (-2.0) | -2.93 (-1.5) | -2.81 (-1.4) | -3.05 (-1.2) | -3.07 (-1.8) | -3.72 (-2.9) | 1.3 | 1.8 |
| Ts | measured | 135 | 134 | 131 | 135 | 129 | 122 | | |
| | browser 3D | 148 (+1.3) | 129 (-0.5) | 127 (-0.5) | 129 (-0.6) | 129 (+0.0) | 140 (+1.8) | 0.6 | 0.8 |

## S3, BOXES (R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, R22, R23) (12)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.55 | 1.49 | 1.49 | 1.41 | 1.38 | 1.22 | | |
| | browser 3D | 1.31 (-3.2) | 0.98 (-6.9) | 0.91 (-7.8) | 0.89 (-7.4) | 0.91 (-6.9) | 0.88 (-5.6) | 7.6 | 6.3 |
| T30 | measured | 1.94 | 1.70 | 1.57 | 1.52 | 1.44 | 1.31 | | |
| | browser 3D | 1.61 (-3.4) | 1.35 (-4.2) | 1.25 (-4.2) | 1.27 (-3.3) | 1.29 (-2.1) | 1.28 (-0.4) | 3.8 | 2.9 |
| C80 | measured | -2.09 | 0.10 | -0.51 | -0.32 | 0.26 | 1.20 | | |
| | browser 3D | -1.20 (+0.9) | 0.81 (+0.7) | 1.43 (+1.9) | 1.32 (+1.6) | 1.55 (+1.3) | 1.66 (+0.5) | 1.8 | 1.2 |
| Ts | measured | 140 | 118 | 119 | 117 | 112 | 100 | | |
| | browser 3D | 119 (-2.1) | 94 (-2.4) | 88 (-3.1) | 89 (-2.7) | 87 (-2.5) | 87 (-1.3) | 2.9 | 2.4 |

## S3, GALLERY (R24, R25) (2)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.96 | 1.96 | 1.96 | 1.77 | 1.73 | 1.53 | | |
| | browser 3D | 1.33 (-6.4) | 1.07 (-9.1) | 0.98 (-10.0) | 1.00 (-8.6) | 0.97 (-8.8) | 0.90 (-8.3) | 9.3 | 8.5 |
| T30 | measured | 2.14 | 1.80 | 1.67 | 1.63 | 1.51 | 1.36 | | |
| | browser 3D | 1.49 (-6.1) | 1.25 (-6.1) | 1.19 (-5.8) | 1.23 (-4.9) | 1.23 (-3.7) | 1.25 (-1.6) | 5.3 | 4.7 |
| C80 | measured | -2.97 | -2.22 | -1.05 | -1.10 | -2.81 | -0.72 | | |
| | browser 3D | -0.93 (+2.0) | 0.97 (+3.2) | 1.72 (+2.8) | 1.67 (+2.8) | 2.05 (+4.9) | 2.47 (+3.2) | 2.8 | 3.1 |
| Ts | measured | 169 | 154 | 138 | 131 | 149 | 118 | | |
| | browser 3D | 116 (-5.3) | 93 (-6.1) | 85 (-5.3) | 86 (-4.5) | 83 (-6.6) | 79 (-3.9) | 4.9 | 5.3 |

Values in brackets: simulated - measured in JND (ISO 3382-1 Annex A: EDT / T30 5 %, C80 / C50 1 dB, Ts 10 ms).

## Summary: mean absolute difference in JND, 500 Hz - 1 kHz (all bands in brackets), over sources and zones

- EDT: 7.9 (6.5); signed 500 Hz - 1 kHz -7.9
- T30: 4.0 (3.2); signed 500 Hz - 1 kHz -4.0
- C80: 2.5 (2.4); signed 500 Hz - 1 kHz +2.1
- Ts: 3.4 (3.2); signed 500 Hz - 1 kHz -3.4
