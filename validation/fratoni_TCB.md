# Fratoni TCB: measured vs AuralPaths (browser engine)

Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria sheet (mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged. Positions and tag-to-material assignments: validate_fratoni.py (VENUES); heights are assumptions (see there).

```
TCB: OBJ 5997 faces (1154 hidden faces dropped), voxel 0.120 m, room volume (voxels) 25862 m3; model built in 3 s
surface areas (m2): Carpet 782, Marble 97, Plaster (boxes) 3312, Seats 249, Stage grid 477, Stage house 4207, Velvet drapes 476, Wood 1500; total 11101
Sabine T (s), no air: 125 Hz 1.69, 250 Hz 1.44, 500 Hz 1.37, 1000 Hz 1.37, 2000 Hz 1.43, 4000 Hz 1.45
tags -> materials: Plaster_(hall) -> Plaster (boxes), Plaster_(gallery) -> Plaster (boxes), Plaster_(fly_tower) -> Stage house, Floor_(boxes) -> Carpet, Floor_(gallery) -> Carpet, Carpet -> Carpet, Marble -> Marble, Wood -> Wood, Seats -> Seats, Stage_grid -> Stage grid, Curtains -> Velvet drapes, Velvet_(fly_tower) -> Velvet drapes, PVC -> Stage house
browser engine: image sources to order 2, 20000 rays per source; S2 64 s (3342 rays lost), S3 66 s (3988 rays lost); total 134 s
```

## S2, STALLS (R3,R5,R7,R8,R10,R11) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.61 | 1.71 | 1.62 | 1.57 | 1.38 | 1.11 | | |
| | browser 3D | 1.35 (-3.3) | 1.05 (-7.7) | 0.95 (-8.3) | 0.93 (-8.2) | 0.90 (-6.9) | 0.89 (-4.0) | 8.2 | 6.4 |
| T30 | measured | 1.82 | 1.70 | 1.58 | 1.48 | 1.32 | 1.12 | | |
| | browser 3D | 1.60 (-2.4) | 1.39 (-3.7) | 1.27 (-3.9) | 1.23 (-3.4) | 1.30 (-0.3) | 1.13 (+0.2) | 3.6 | 2.3 |
| C80 | measured | -2.40 | -0.46 | 1.34 | 1.09 | 1.01 | 1.40 | | |
| | browser 3D | 2.54 (+4.9) | 4.27 (+4.7) | 4.94 (+3.6) | 5.02 (+3.9) | 5.20 (+4.2) | 5.56 (+4.2) | 3.8 | 4.3 |
| Ts | measured | 157 | 107 | 119 | 101 | 100 | 97 | | |
| | browser 3D | 87 (-7.0) | 67 (-4.0) | 60 (-5.9) | 59 (-4.1) | 58 (-4.2) | 55 (-4.2) | 5.0 | 4.9 |

## S2, BOXES (R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, R22, R23) (12)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.49 | 1.43 | 1.34 | 1.27 | 1.14 | 0.97 | | |
| | browser 3D | 1.35 (-1.9) | 0.93 (-6.9) | 0.78 (-8.4) | 0.77 (-7.9) | 0.74 (-7.2) | 0.65 (-6.6) | 8.1 | 6.5 |
| T30 | measured | 1.82 | 1.69 | 1.57 | 1.46 | 1.31 | 1.12 | | |
| | browser 3D | 1.53 (-3.2) | 1.36 (-3.9) | 1.33 (-3.0) | 1.27 (-2.6) | 1.38 (+1.1) | 1.22 (+1.9) | 2.8 | 2.6 |
| C80 | measured | -0.26 | 1.53 | 1.73 | 2.36 | 2.76 | 3.27 | | |
| | browser 3D | 1.72 (+2.0) | 4.40 (+2.9) | 5.83 (+4.1) | 5.88 (+3.5) | 6.28 (+3.5) | 7.14 (+3.9) | 3.8 | 3.3 |
| Ts | measured | 136 | 105 | 97 | 91 | 84 | 77 | | |
| | browser 3D | 94 (-4.2) | 69 (-3.6) | 59 (-3.8) | 58 (-3.3) | 56 (-2.8) | 51 (-2.6) | 3.5 | 3.4 |

## S2, GALLERY (R24, R25) (2)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 2.07 | 1.80 | 1.78 | 1.57 | 1.45 | 1.24 | | |
| | browser 3D | 1.28 (-7.6) | 0.90 (-10.0) | 0.78 (-11.2) | 0.77 (-10.2) | 0.75 (-9.6) | 0.63 (-9.8) | 10.7 | 9.7 |
| T30 | measured | 1.92 | 1.68 | 1.61 | 1.52 | 1.36 | 1.14 | | |
| | browser 3D | 1.64 (-3.0) | 1.22 (-5.5) | 1.14 (-5.9) | 1.14 (-5.0) | 1.15 (-3.0) | 1.03 (-1.9) | 5.4 | 4.0 |
| C80 | measured | -1.80 | -0.80 | -0.72 | -0.01 | 0.76 | 0.80 | | |
| | browser 3D | -0.63 (+1.2) | 1.40 (+2.2) | 2.43 (+3.2) | 2.41 (+2.4) | 2.80 (+2.0) | 3.49 (+2.7) | 2.8 | 2.3 |
| Ts | measured | 128 | 148 | 126 | 120 | 105 | 95 | | |
| | browser 3D | 114 (-1.4) | 93 (-5.5) | 85 (-4.1) | 86 (-3.4) | 84 (-2.1) | 78 (-1.7) | 3.8 | 3.0 |

## S3, STALLS (R3,R5,R7,R8,R10,R11) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.50 | 1.48 | 1.52 | 1.51 | 1.48 | 1.33 | | |
| | browser 3D | 1.41 (-1.2) | 1.12 (-4.8) | 1.09 (-5.6) | 1.17 (-4.5) | 1.18 (-4.0) | 1.41 (+1.2) | 5.1 | 3.6 |
| T30 | measured | 1.93 | 1.70 | 1.55 | 1.53 | 1.45 | 1.30 | | |
| | browser 3D | 1.65 (-2.9) | 1.32 (-4.4) | 1.35 (-2.5) | 1.32 (-2.7) | 1.34 (-1.5) | 1.41 (+1.6) | 2.6 | 2.6 |
| C80 | measured | -2.00 | -1.46 | -1.43 | -1.87 | -1.29 | -0.80 | | |
| | browser 3D | -3.79 (-1.8) | -2.79 (-1.3) | -2.70 (-1.3) | -2.95 (-1.1) | -2.98 (-1.7) | -3.65 (-2.8) | 1.2 | 1.7 |
| Ts | measured | 135 | 134 | 131 | 135 | 129 | 122 | | |
| | browser 3D | 145 (+1.0) | 127 (-0.7) | 125 (-0.6) | 128 (-0.7) | 129 (-0.1) | 140 (+1.8) | 0.7 | 0.8 |

## S3, BOXES (R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, R22, R23) (12)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.55 | 1.49 | 1.49 | 1.41 | 1.38 | 1.22 | | |
| | browser 3D | 1.30 (-3.2) | 0.96 (-7.1) | 0.89 (-8.0) | 0.90 (-7.3) | 0.89 (-7.1) | 0.86 (-5.9) | 7.7 | 6.5 |
| T30 | measured | 1.94 | 1.70 | 1.57 | 1.52 | 1.44 | 1.31 | | |
| | browser 3D | 1.62 (-3.4) | 1.35 (-4.1) | 1.23 (-4.3) | 1.26 (-3.5) | 1.28 (-2.3) | 1.28 (-0.4) | 3.9 | 3.0 |
| C80 | measured | -2.09 | 0.10 | -0.51 | -0.32 | 0.26 | 1.20 | | |
| | browser 3D | -1.02 (+1.1) | 0.97 (+0.9) | 1.57 (+2.1) | 1.46 (+1.8) | 1.68 (+1.4) | 1.83 (+0.6) | 1.9 | 1.3 |
| Ts | measured | 140 | 118 | 119 | 117 | 112 | 100 | | |
| | browser 3D | 117 (-2.3) | 93 (-2.5) | 88 (-3.2) | 88 (-2.8) | 87 (-2.5) | 86 (-1.4) | 3.0 | 2.4 |

## S3, GALLERY (R24, R25) (2)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.96 | 1.96 | 1.96 | 1.77 | 1.73 | 1.53 | | |
| | browser 3D | 1.30 (-6.7) | 1.04 (-9.4) | 0.96 (-10.2) | 0.98 (-8.9) | 0.94 (-9.1) | 0.89 (-8.4) | 9.5 | 8.8 |
| T30 | measured | 2.14 | 1.80 | 1.67 | 1.63 | 1.51 | 1.36 | | |
| | browser 3D | 1.49 (-6.0) | 1.24 (-6.2) | 1.19 (-5.8) | 1.23 (-4.9) | 1.24 (-3.6) | 1.26 (-1.4) | 5.3 | 4.7 |
| C80 | measured | -2.97 | -2.22 | -1.05 | -1.10 | -2.81 | -0.72 | | |
| | browser 3D | -0.80 (+2.2) | 0.96 (+3.2) | 1.63 (+2.7) | 1.59 (+2.7) | 1.93 (+4.7) | 2.34 (+3.1) | 2.7 | 3.1 |
| Ts | measured | 169 | 154 | 138 | 131 | 149 | 118 | | |
| | browser 3D | 114 (-5.5) | 91 (-6.3) | 84 (-5.4) | 85 (-4.6) | 82 (-6.7) | 79 (-3.9) | 5.0 | 5.4 |

Values in brackets: simulated - measured in JND (ISO 3382-1 Annex A: EDT / T30 5 %, C80 / C50 1 dB, Ts 10 ms).

## Summary: mean absolute difference in JND, 500 Hz - 1 kHz (all bands in brackets), over sources and zones

- EDT: 8.2 (6.9); signed 500 Hz - 1 kHz -8.2
- T30: 4.0 (3.2); signed 500 Hz - 1 kHz -4.0
- C80: 2.7 (2.7); signed 500 Hz - 1 kHz +2.3
- Ts: 3.5 (3.3); signed 500 Hz - 1 kHz -3.5
