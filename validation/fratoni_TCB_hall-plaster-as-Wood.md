# Fratoni TCB: measured vs AuralPaths (browser engine)

**Rerun on 2026-11-19 with the engine after the fixes of 2026-11-18 and 2026-11-19** (`validation/mesh_leak.md`); 55 - 63 of 20 000 rays lost per source (0.28 - 0.32 %, above the 0.1 % limit). Mean absolute error at 500 Hz - 1 kHz, run of 2026-11-07 → now: EDT 5.1 → 4.6, T30 2.4 → 2.5, C80 2.0 → 1.8, Ts 2.5 → 2.4 JND. The 708 faces behind the room's faces (815 m²) are not counted in the surface; the tables are the same with and without them.

Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria sheet (mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged. Positions and tag-to-material assignments: validate_fratoni.py (VENUES); heights are assumptions (see there).

```
TCB: OBJ 5997 faces (435 narrow faces kept two-sided; 708 behind the room's faces, 815 m2, kept but not counted; 4 not at the room and 0 untagged ones in the surface band left out), voxel 0.120 m, room volume (voxels) 27149 m3; model built in 17 s
surface areas (m2): Carpet 790, Marble 97, Plaster (boxes) 292, Seats 259, Stage grid 477, Stage house 4221, Velvet drapes 476, Wood 4556; total 11169
Sabine T (s), no air: 125 Hz 1.51, 250 Hz 1.46, 500 Hz 1.57, 1000 Hz 1.64, 2000 Hz 1.79, 4000 Hz 2.06
tags -> materials: Plaster_(hall) -> Wood, Plaster_(gallery) -> Plaster (boxes), Plaster_(fly_tower) -> Stage house, Floor_(boxes) -> Carpet, Floor_(gallery) -> Carpet, Carpet -> Carpet, Marble -> Marble, Wood -> Wood, Seats -> Seats, Stage_grid -> Stage grid, Curtains -> Velvet drapes, Velvet_(fly_tower) -> Velvet drapes, PVC -> Stage house
browser engine: image sources to order 2, 20000 rays per source; S2 48 s (55 rays lost), S3 55 s (63 rays lost); total 121 s
```

## S2, STALLS (R3,R5,R7,R8,R10,R11) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.61 | 1.71 | 1.62 | 1.57 | 1.38 | 1.11 | | |
| | browser 3D | 1.25 (-4.5) | 1.17 (-6.3) | 1.29 (-4.1) | 1.37 (-2.6) | 1.39 (+0.1) | 1.48 (+6.7) | 3.3 | 4.0 |
| T30 | measured | 1.82 | 1.70 | 1.58 | 1.48 | 1.32 | 1.12 | | |
| | browser 3D | 1.38 (-4.9) | 1.24 (-5.4) | 1.21 (-4.6) | 1.24 (-3.3) | 1.31 (-0.2) | 1.37 (+4.6) | 3.9 | 3.8 |
| C80 | measured | -2.40 | -0.46 | 1.34 | 1.09 | 1.01 | 1.40 | | |
| | browser 3D | 2.71 (+5.1) | 3.23 (+3.7) | 2.83 (+1.5) | 2.37 (+1.3) | 2.27 (+1.3) | 1.80 (+0.4) | 1.4 | 2.2 |
| Ts | measured | 157 | 107 | 119 | 101 | 100 | 97 | | |
| | browser 3D | 79 (-7.7) | 74 (-3.3) | 78 (-4.1) | 84 (-1.7) | 85 (-1.5) | 91 (-0.6) | 2.9 | 3.1 |

## S2, BOXES (R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, R22, R23) (12)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.49 | 1.43 | 1.34 | 1.27 | 1.14 | 0.97 | | |
| | browser 3D | 1.13 (-4.8) | 0.96 (-6.5) | 1.04 (-4.5) | 1.21 (-0.9) | 1.25 (+1.8) | 1.49 (+10.8) | 2.7 | 4.9 |
| T30 | measured | 1.82 | 1.69 | 1.57 | 1.46 | 1.31 | 1.12 | | |
| | browser 3D | 1.45 (-4.1) | 1.33 (-4.3) | 1.32 (-3.1) | 1.39 (-0.9) | 1.48 (+2.6) | 1.53 (+7.5) | 2.0 | 3.8 |
| C80 | measured | -0.26 | 1.53 | 1.73 | 2.36 | 2.76 | 3.27 | | |
| | browser 3D | 4.56 (+4.8) | 5.06 (+3.5) | 4.12 (+2.4) | 3.23 (+0.9) | 3.08 (+0.3) | 1.44 (-1.8) | 1.6 | 2.3 |
| Ts | measured | 136 | 105 | 97 | 91 | 84 | 77 | | |
| | browser 3D | 71 (-6.6) | 65 (-4.0) | 72 (-2.5) | 81 (-1.0) | 82 (-0.2) | 99 (+2.2) | 1.7 | 2.7 |

## S2, GALLERY (R24, R25) (2)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 2.07 | 1.80 | 1.78 | 1.57 | 1.45 | 1.24 | | |
| | browser 3D | 0.84 (-11.9) | 0.85 (-10.6) | 0.85 (-10.4) | 0.96 (-7.7) | 0.97 (-6.5) | 0.99 (-3.9) | 9.1 | 8.5 |
| T30 | measured | 1.92 | 1.68 | 1.61 | 1.52 | 1.36 | 1.14 | | |
| | browser 3D | 1.49 (-4.5) | 1.23 (-5.4) | 1.30 (-3.8) | 1.39 (-1.6) | 1.50 (+2.0) | 1.62 (+8.3) | 2.7 | 4.3 |
| C80 | measured | -1.80 | -0.80 | -0.72 | -0.01 | 0.76 | 0.80 | | |
| | browser 3D | 0.87 (+2.7) | 1.54 (+2.3) | 1.41 (+2.1) | 0.74 (+0.7) | 0.73 (-0.0) | 0.32 (-0.5) | 1.4 | 1.4 |
| Ts | measured | 128 | 148 | 126 | 120 | 105 | 95 | | |
| | browser 3D | 96 (-3.2) | 90 (-5.8) | 92 (-3.4) | 97 (-2.3) | 98 (-0.7) | 104 (+0.9) | 2.8 | 2.7 |

## S3, STALLS (R3,R5,R7,R8,R10,R11) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.50 | 1.48 | 1.52 | 1.51 | 1.48 | 1.33 | | |
| | browser 3D | 1.33 (-2.3) | 1.30 (-2.4) | 1.39 (-1.8) | 1.52 (+0.1) | 1.54 (+0.8) | 1.72 (+5.8) | 0.9 | 2.2 |
| T30 | measured | 1.93 | 1.70 | 1.55 | 1.53 | 1.45 | 1.30 | | |
| | browser 3D | 1.54 (-4.1) | 1.44 (-3.0) | 1.49 (-0.8) | 1.51 (-0.2) | 1.56 (+1.5) | 1.59 (+4.5) | 0.5 | 2.3 |
| C80 | measured | -2.00 | -1.46 | -1.43 | -1.87 | -1.29 | -0.80 | | |
| | browser 3D | -3.55 (-1.5) | -3.21 (-1.7) | -3.72 (-2.3) | -4.29 (-2.4) | -4.46 (-3.2) | -5.43 (-4.6) | 2.4 | 2.6 |
| Ts | measured | 135 | 134 | 131 | 135 | 129 | 122 | | |
| | browser 3D | 143 (+0.8) | 139 (+0.5) | 146 (+1.4) | 153 (+1.7) | 154 (+2.5) | 169 (+4.7) | 1.6 | 2.0 |

## S3, BOXES (R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, R22, R23) (12)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.55 | 1.49 | 1.49 | 1.41 | 1.38 | 1.22 | | |
| | browser 3D | 0.95 (-7.8) | 0.90 (-7.9) | 0.99 (-6.7) | 1.14 (-3.9) | 1.17 (-3.1) | 1.53 (+5.1) | 5.3 | 5.8 |
| T30 | measured | 1.94 | 1.70 | 1.57 | 1.52 | 1.44 | 1.31 | | |
| | browser 3D | 1.42 (-5.4) | 1.31 (-4.6) | 1.36 (-2.7) | 1.44 (-1.1) | 1.49 (+0.7) | 1.79 (+7.3) | 1.9 | 3.6 |
| C80 | measured | -2.09 | 0.10 | -0.51 | -0.32 | 0.26 | 1.20 | | |
| | browser 3D | 1.14 (+3.2) | 1.39 (+1.3) | 0.48 (+1.0) | -0.27 (+0.0) | -0.27 (-0.5) | -1.92 (-3.1) | 0.5 | 1.5 |
| Ts | measured | 140 | 118 | 119 | 117 | 112 | 100 | | |
| | browser 3D | 94 (-4.6) | 90 (-2.8) | 100 (-1.9) | 109 (-0.7) | 110 (-0.2) | 133 (+3.3) | 1.3 | 2.3 |

## S3, GALLERY (R24, R25) (2)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.96 | 1.96 | 1.96 | 1.77 | 1.73 | 1.53 | | |
| | browser 3D | 1.22 (-7.6) | 1.05 (-9.3) | 1.16 (-8.1) | 1.37 (-4.4) | 1.40 (-3.8) | 1.69 (+2.1) | 6.3 | 5.9 |
| T30 | measured | 2.14 | 1.80 | 1.67 | 1.63 | 1.51 | 1.36 | | |
| | browser 3D | 1.28 (-8.0) | 1.27 (-5.9) | 1.28 (-4.6) | 1.39 (-2.9) | 1.51 (+0.0) | 1.74 (+5.6) | 3.8 | 4.5 |
| C80 | measured | -2.97 | -2.22 | -1.05 | -1.10 | -2.81 | -0.72 | | |
| | browser 3D | 2.50 (+5.5) | 3.28 (+5.5) | 2.72 (+3.8) | 2.05 (+3.2) | 2.08 (+4.9) | 1.23 (+1.9) | 3.5 | 4.1 |
| Ts | measured | 169 | 154 | 138 | 131 | 149 | 118 | | |
| | browser 3D | 90 (-7.9) | 83 (-7.1) | 89 (-4.9) | 98 (-3.3) | 98 (-5.1) | 116 (-0.2) | 4.1 | 4.7 |

Values in brackets: simulated - measured in JND (ISO 3382-1 Annex A: EDT / T30 5 %, C80 / C50 1 dB, Ts 10 ms).

## Summary: mean absolute difference in JND, 500 Hz - 1 kHz (all bands in brackets), over sources and zones

- EDT: 4.6 (5.2); signed 500 Hz - 1 kHz -4.6
- T30: 2.5 (3.7); signed 500 Hz - 1 kHz -2.5
- C80: 1.8 (2.4); signed 500 Hz - 1 kHz +1.0
- Ts: 2.4 (2.9); signed 500 Hz - 1 kHz -1.9
