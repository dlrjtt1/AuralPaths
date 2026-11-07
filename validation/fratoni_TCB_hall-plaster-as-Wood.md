# Fratoni TCB: measured vs AuralPaths (browser engine)

Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria sheet (mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged. Positions and tag-to-material assignments: validate_fratoni.py (VENUES); heights are assumptions (see there).

```
TCB: OBJ 5997 faces (1154 hidden faces dropped), voxel 0.120 m, room volume (voxels) 25862 m3; model built in 3 s
surface areas (m2): Carpet 782, Marble 97, Plaster (boxes) 292, Seats 249, Stage grid 477, Stage house 4207, Velvet drapes 476, Wood 4520; total 11101
Sabine T (s), no air: 125 Hz 1.44, 250 Hz 1.40, 500 Hz 1.50, 1000 Hz 1.57, 2000 Hz 1.71, 4000 Hz 1.97
tags -> materials: Plaster_(hall) -> Wood, Plaster_(gallery) -> Plaster (boxes), Plaster_(fly_tower) -> Stage house, Floor_(boxes) -> Carpet, Floor_(gallery) -> Carpet, Carpet -> Carpet, Marble -> Marble, Wood -> Wood, Seats -> Seats, Stage_grid -> Stage grid, Curtains -> Velvet drapes, Velvet_(fly_tower) -> Velvet drapes, PVC -> Stage house
browser engine: image sources to order 2, 20000 rays per source; S2 73 s (3622 rays lost), S3 73 s (4526 rays lost); total 149 s
```

## S2, STALLS (R3,R5,R7,R8,R10,R11) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.61 | 1.71 | 1.62 | 1.57 | 1.38 | 1.11 | | |
| | browser 3D | 1.21 (-5.0) | 1.12 (-6.9) | 1.24 (-4.7) | 1.32 (-3.2) | 1.33 (-0.7) | 1.41 (+5.6) | 3.9 | 4.3 |
| T30 | measured | 1.82 | 1.70 | 1.58 | 1.48 | 1.32 | 1.12 | | |
| | browser 3D | 1.43 (-4.3) | 1.26 (-5.1) | 1.22 (-4.5) | 1.23 (-3.5) | 1.32 (-0.1) | 1.39 (+4.8) | 4.0 | 3.7 |
| C80 | measured | -2.40 | -0.46 | 1.34 | 1.09 | 1.01 | 1.40 | | |
| | browser 3D | 2.87 (+5.3) | 3.38 (+3.8) | 3.01 (+1.7) | 2.59 (+1.5) | 2.46 (+1.4) | 2.03 (+0.6) | 1.6 | 2.4 |
| Ts | measured | 157 | 107 | 119 | 101 | 100 | 97 | | |
| | browser 3D | 78 (-7.9) | 73 (-3.4) | 76 (-4.2) | 81 (-2.0) | 82 (-1.8) | 88 (-0.9) | 3.1 | 3.4 |

## S2, BOXES (R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, R22, R23) (12)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.49 | 1.43 | 1.34 | 1.27 | 1.14 | 0.97 | | |
| | browser 3D | 1.13 (-4.8) | 0.95 (-6.6) | 1.05 (-4.4) | 1.19 (-1.3) | 1.20 (+1.0) | 1.44 (+9.8) | 2.8 | 4.6 |
| T30 | measured | 1.82 | 1.69 | 1.57 | 1.46 | 1.31 | 1.12 | | |
| | browser 3D | 1.45 (-4.1) | 1.29 (-4.8) | 1.29 (-3.5) | 1.33 (-1.8) | 1.41 (+1.5) | 1.49 (+6.8) | 2.6 | 3.7 |
| C80 | measured | -0.26 | 1.53 | 1.73 | 2.36 | 2.76 | 3.27 | | |
| | browser 3D | 4.99 (+5.2) | 5.50 (+4.0) | 4.56 (+2.8) | 3.67 (+1.3) | 3.53 (+0.8) | 1.84 (-1.4) | 2.1 | 2.6 |
| Ts | measured | 136 | 105 | 97 | 91 | 84 | 77 | | |
| | browser 3D | 69 (-6.7) | 64 (-4.1) | 70 (-2.7) | 78 (-1.3) | 79 (-0.5) | 95 (+1.8) | 2.0 | 2.9 |

## S2, GALLERY (R24, R25) (2)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 2.07 | 1.80 | 1.78 | 1.57 | 1.45 | 1.24 | | |
| | browser 3D | 0.79 (-12.4) | 0.84 (-10.7) | 0.82 (-10.8) | 0.87 (-8.9) | 0.95 (-6.9) | 1.01 (-3.7) | 9.8 | 8.9 |
| T30 | measured | 1.92 | 1.68 | 1.61 | 1.52 | 1.36 | 1.14 | | |
| | browser 3D | 1.41 (-5.3) | 1.24 (-5.2) | 1.39 (-2.7) | 1.52 (+0.0) | 1.60 (+3.5) | 1.62 (+8.3) | 1.4 | 4.2 |
| C80 | measured | -1.80 | -0.80 | -0.72 | -0.01 | 0.76 | 0.80 | | |
| | browser 3D | 1.29 (+3.1) | 1.81 (+2.6) | 1.58 (+2.3) | 0.91 (+0.9) | 0.85 (+0.1) | 0.33 (-0.5) | 1.6 | 1.6 |
| Ts | measured | 128 | 148 | 126 | 120 | 105 | 95 | | |
| | browser 3D | 91 (-3.7) | 87 (-6.1) | 90 (-3.6) | 95 (-2.5) | 97 (-0.8) | 106 (+1.1) | 3.0 | 3.0 |

## S3, STALLS (R3,R5,R7,R8,R10,R11) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.50 | 1.48 | 1.52 | 1.51 | 1.48 | 1.33 | | |
| | browser 3D | 1.33 (-2.2) | 1.28 (-2.7) | 1.36 (-2.2) | 1.47 (-0.6) | 1.49 (+0.1) | 1.66 (+4.9) | 1.4 | 2.1 |
| T30 | measured | 1.93 | 1.70 | 1.55 | 1.53 | 1.45 | 1.30 | | |
| | browser 3D | 1.53 (-4.1) | 1.41 (-3.3) | 1.52 (-0.3) | 1.51 (-0.2) | 1.57 (+1.7) | 1.61 (+4.8) | 0.2 | 2.4 |
| C80 | measured | -2.00 | -1.46 | -1.43 | -1.87 | -1.29 | -0.80 | | |
| | browser 3D | -3.35 (-1.3) | -3.01 (-1.5) | -3.48 (-2.1) | -4.03 (-2.2) | -4.19 (-2.9) | -5.15 (-4.3) | 2.1 | 2.4 |
| Ts | measured | 135 | 134 | 131 | 135 | 129 | 122 | | |
| | browser 3D | 141 (+0.6) | 136 (+0.2) | 143 (+1.1) | 149 (+1.4) | 151 (+2.2) | 166 (+4.4) | 1.3 | 1.6 |

## S3, BOXES (R12, R13, R14, R15, R16, R17, R18, R19, R20, R21, R22, R23) (12)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.55 | 1.49 | 1.49 | 1.41 | 1.38 | 1.22 | | |
| | browser 3D | 0.97 (-7.6) | 0.92 (-7.7) | 1.00 (-6.6) | 1.12 (-4.2) | 1.16 (-3.2) | 1.53 (+5.1) | 5.4 | 5.7 |
| T30 | measured | 1.94 | 1.70 | 1.57 | 1.52 | 1.44 | 1.31 | | |
| | browser 3D | 1.38 (-5.8) | 1.28 (-4.9) | 1.34 (-3.0) | 1.44 (-1.1) | 1.48 (+0.5) | 1.62 (+4.7) | 2.1 | 3.4 |
| C80 | measured | -2.09 | 0.10 | -0.51 | -0.32 | 0.26 | 1.20 | | |
| | browser 3D | 1.16 (+3.3) | 1.43 (+1.3) | 0.54 (+1.0) | -0.15 (+0.2) | -0.18 (-0.4) | -1.75 (-3.0) | 0.6 | 1.5 |
| Ts | measured | 140 | 118 | 119 | 117 | 112 | 100 | | |
| | browser 3D | 94 (-4.6) | 90 (-2.8) | 99 (-2.0) | 108 (-0.8) | 109 (-0.2) | 131 (+3.0) | 1.4 | 2.3 |

## S3, GALLERY (R24, R25) (2)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.96 | 1.96 | 1.96 | 1.77 | 1.73 | 1.53 | | |
| | browser 3D | 1.19 (-7.8) | 1.02 (-9.6) | 1.09 (-8.9) | 1.30 (-5.3) | 1.36 (-4.3) | 1.66 (+1.7) | 7.1 | 6.3 |
| T30 | measured | 2.14 | 1.80 | 1.67 | 1.63 | 1.51 | 1.36 | | |
| | browser 3D | 1.26 (-8.2) | 1.23 (-6.3) | 1.25 (-5.0) | 1.36 (-3.3) | 1.51 (-0.0) | 1.77 (+6.1) | 4.2 | 4.8 |
| C80 | measured | -2.97 | -2.22 | -1.05 | -1.10 | -2.81 | -0.72 | | |
| | browser 3D | 2.97 (+5.9) | 3.64 (+5.9) | 3.06 (+4.1) | 2.41 (+3.5) | 2.44 (+5.3) | 1.58 (+2.3) | 3.8 | 4.5 |
| Ts | measured | 169 | 154 | 138 | 131 | 149 | 118 | | |
| | browser 3D | 87 (-8.2) | 80 (-7.4) | 86 (-5.2) | 94 (-3.7) | 95 (-5.4) | 112 (-0.6) | 4.4 | 5.1 |

Values in brackets: simulated - measured in JND (ISO 3382-1 Annex A: EDT / T30 5 %, C80 / C50 1 dB, Ts 10 ms).

## Summary: mean absolute difference in JND, 500 Hz - 1 kHz (all bands in brackets), over sources and zones

- EDT: 5.1 (5.3); signed 500 Hz - 1 kHz -5.1
- T30: 2.4 (3.7); signed 500 Hz - 1 kHz -2.4
- C80: 2.0 (2.5); signed 500 Hz - 1 kHz +1.3
- Ts: 2.5 (3.0); signed 500 Hz - 1 kHz -2.1
