# Fratoni DUS: measured vs AuralPaths (browser engine)

Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria sheet (mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged. Positions and tag-to-material assignments: validate_fratoni.py (VENUES); heights are assumptions (see there).

```
DUS: OBJ 9852 faces (2339 hidden faces dropped), voxel 0.080 m, room volume (voxels) 8246 m3; model built in 4 s
surface areas (m2): Marble 204, Plaster (hall) 2616, Seats (balconies) 572, Seats (stalls) 302, Stage grid 200, Stage house 1186, Velvet drapes 211, Wood 1757; total 7047
Sabine T (s), no air: 125 Hz 1.33, 250 Hz 1.13, 500 Hz 1.11, 1000 Hz 1.02, 2000 Hz 1.04, 4000 Hz 1.06
tags -> materials: Plaster_fly_tower -> Stage house, Plaster -> Plaster (hall), Wings -> Stage house, Grid -> Stage grid, Carpet -> Wood, Wood -> Wood, Marble -> Marble, Velvet -> Velvet drapes, Seats_stalls -> Seats (stalls), Seats_first_gallery -> Seats (balconies), Seats_second_gallery -> Seats (balconies)
browser engine: image sources to order 2, 20000 rays per source; S1 160 s (4783 rays lost), S2 149 s (4407 rays lost); total 313 s
```

## S1, STALLS (R1,R2,R3,R4,R5,R6) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.74 | 1.58 | 1.42 | 1.24 | 1.02 | 0.76 | | |
| | browser 3D | 1.80 (+0.7) | 1.61 (+0.4) | 1.60 (+2.5) | 1.45 (+3.4) | 1.39 (+7.2) | 1.26 (+13.4) | 3.0 | 4.6 |
| T30 | measured | 1.96 | 1.70 | 1.45 | 1.34 | 1.19 | 0.97 | | |
| | browser 3D | 1.60 (-3.7) | 1.37 (-3.9) | 1.38 (-0.9) | 1.36 (+0.4) | 1.27 (+1.4) | 1.14 (+3.5) | 0.7 | 2.3 |
| C80 | measured | 1.58 | 4.87 | 3.83 | 5.36 | 5.42 | 7.75 | | |
| | browser 3D | 0.98 (-0.6) | 2.02 (-2.9) | 2.11 (-1.7) | 2.75 (-2.6) | 3.13 (-2.3) | 3.99 (-3.8) | 2.2 | 2.3 |
| Ts | measured | 106 | 69 | 75 | 57 | 57 | 40 | | |
| | browser 3D | 102 (-0.4) | 85 (+1.7) | 84 (+0.9) | 76 (+1.9) | 72 (+1.5) | 62 (+2.2) | 1.4 | 1.4 |

## S1, 1st BALCONY (R7, R8, R9, R10) (4)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.68 | 1.23 | 1.12 | 1.03 | 0.89 | 0.80 | | |
| | browser 3D | 1.59 (-1.2) | 1.37 (+2.3) | 1.35 (+4.0) | 1.23 (+3.7) | 1.17 (+6.1) | 1.05 (+6.2) | 3.8 | 3.9 |
| T30 | measured | 2.06 | 1.62 | 1.46 | 1.29 | 1.14 | 0.92 | | |
| | browser 3D | 1.66 (-3.9) | 1.41 (-2.6) | 1.36 (-1.3) | 1.22 (-1.0) | 1.20 (+1.1) | 1.08 (+3.5) | 1.1 | 2.2 |
| C80 | measured | -0.92 | 2.16 | 2.30 | 2.93 | 3.75 | 4.66 | | |
| | browser 3D | 0.06 (+1.0) | 1.14 (-1.0) | 1.49 (-0.8) | 2.30 (-0.6) | 2.25 (-1.5) | 2.90 (-1.8) | 0.7 | 1.1 |
| Ts | measured | 140 | 93 | 87 | 72 | 69 | 59 | | |
| | browser 3D | 115 (-2.5) | 98 (+0.5) | 94 (+0.7) | 84 (+1.1) | 83 (+1.3) | 75 (+1.6) | 0.9 | 1.3 |

## S1, 2nd BALCONY (R13, R14, R15, R16, R17, R18) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.92 | 1.49 | 1.23 | 1.09 | 0.96 | 0.77 | | |
| | browser 3D | 1.70 (-2.3) | 1.37 (-1.6) | 1.34 (+1.7) | 1.13 (+0.8) | 1.06 (+2.2) | 0.90 (+3.4) | 1.2 | 2.0 |
| T30 | measured | 2.07 | 1.79 | 1.53 | 1.39 | 1.22 | 0.98 | | |
| | browser 3D | 1.69 (-3.7) | 1.43 (-4.1) | 1.41 (-1.6) | 1.31 (-1.0) | 1.25 (+0.6) | 1.14 (+3.2) | 1.3 | 2.4 |
| C80 | measured | -1.43 | -0.49 | 1.61 | 3.02 | 3.85 | 4.90 | | |
| | browser 3D | 1.42 (+2.8) | 2.61 (+3.1) | 2.90 (+1.3) | 3.76 (+0.7) | 3.86 (+0.0) | 4.59 (-0.3) | 1.0 | 1.4 |
| Ts | measured | 144 | 119 | 97 | 82 | 74 | 60 | | |
| | browser 3D | 108 (-3.5) | 91 (-2.8) | 89 (-0.8) | 79 (-0.4) | 76 (+0.2) | 68 (+0.8) | 0.6 | 1.4 |

## S2, STALLS (R1,R2,R3,R4,R5,R6) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 2.05 | 1.61 | 1.51 | 1.29 | 1.20 | 1.03 | | |
| | browser 3D | 1.78 (-2.7) | 1.56 (-0.6) | 1.51 (+0.0) | 1.31 (+0.3) | 1.25 (+0.8) | 1.11 (+1.7) | 0.2 | 1.0 |
| T30 | measured | 1.95 | 1.70 | 1.49 | 1.32 | 1.17 | 0.96 | | |
| | browser 3D | 1.68 (-2.7) | 1.43 (-3.1) | 1.43 (-0.8) | 1.40 (+1.2) | 1.31 (+2.3) | 1.16 (+4.3) | 1.0 | 2.4 |
| C80 | measured | -2.93 | 1.37 | 1.37 | 3.85 | 3.42 | 6.69 | | |
| | browser 3D | -0.75 (+2.2) | 0.59 (-0.8) | 0.84 (-0.5) | 1.85 (-2.0) | 2.19 (-1.2) | 3.04 (-3.7) | 1.3 | 1.7 |
| Ts | measured | 164 | 102 | 95 | 71 | 71 | 43 | | |
| | browser 3D | 124 (-4.0) | 102 (-0.0) | 98 (+0.2) | 84 (+1.3) | 80 (+0.8) | 70 (+2.7) | 0.8 | 1.5 |

## S2, 1st BALCONY (R7, R8, R9, R10) (4)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.50 | 1.34 | 1.07 | 0.87 | 0.71 | 0.63 | | |
| | browser 3D | 1.66 (+2.2) | 1.41 (+1.0) | 1.35 (+5.3) | 1.07 (+4.6) | 1.05 (+9.7) | 0.99 (+11.6) | 5.0 | 5.7 |
| T30 | measured | 1.92 | 1.69 | 1.45 | 1.27 | 1.09 | 0.90 | | |
| | browser 3D | 1.78 (-1.5) | 1.60 (-1.1) | 1.58 (+1.9) | 1.46 (+2.9) | 1.48 (+7.1) | 1.27 (+8.2) | 2.4 | 3.8 |
| C80 | measured | -0.42 | 2.25 | 3.87 | 5.48 | 7.39 | 8.29 | | |
| | browser 3D | 0.60 (+1.0) | 2.05 (-0.2) | 2.52 (-1.4) | 3.99 (-1.5) | 4.07 (-3.3) | 4.83 (-3.5) | 1.4 | 1.8 |
| Ts | measured | 119 | 90 | 73 | 59 | 45 | 39 | | |
| | browser 3D | 113 (-0.6) | 92 (+0.1) | 87 (+1.4) | 73 (+1.4) | 71 (+2.5) | 63 (+2.4) | 1.4 | 1.4 |

## S2, 2nd BALCONY (R13, R14, R15, R16, R17, R18) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.93 | 1.62 | 1.24 | 0.97 | 0.80 | 0.64 | | |
| | browser 3D | 1.65 (-2.9) | 1.38 (-2.9) | 1.36 (+2.0) | 1.19 (+4.5) | 1.06 (+6.6) | 0.86 (+6.7) | 3.3 | 4.3 |
| T30 | measured | 2.01 | 1.75 | 1.53 | 1.37 | 1.18 | 0.97 | | |
| | browser 3D | 1.69 (-3.2) | 1.50 (-2.9) | 1.42 (-1.4) | 1.39 (+0.4) | 1.35 (+2.9) | 1.23 (+5.3) | 0.9 | 2.7 |
| C80 | measured | -0.21 | -0.40 | 2.97 | 4.98 | 6.60 | 7.45 | | |
| | browser 3D | 2.41 (+2.6) | 3.86 (+4.3) | 4.15 (+1.2) | 5.36 (+0.4) | 5.78 (-0.8) | 6.60 (-0.9) | 0.8 | 1.7 |
| Ts | measured | 134 | 123 | 83 | 64 | 51 | 46 | | |
| | browser 3D | 100 (-3.3) | 81 (-4.3) | 77 (-0.6) | 65 (+0.1) | 63 (+1.1) | 55 (+1.0) | 0.4 | 1.7 |

Values in brackets: simulated - measured in JND (ISO 3382-1 Annex A: EDT / T30 5 %, C80 / C50 1 dB, Ts 10 ms).

## Summary: mean absolute difference in JND, 500 Hz - 1 kHz (all bands in brackets), over sources and zones

- EDT: 2.7 (3.6); signed 500 Hz - 1 kHz +2.7
- T30: 1.2 (2.6); signed 500 Hz - 1 kHz -0.1
- C80: 1.2 (1.7); signed 500 Hz - 1 kHz -0.6
- Ts: 0.9 (1.5); signed 500 Hz - 1 kHz +0.6
