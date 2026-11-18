# Fratoni DUS: measured vs AuralPaths (browser engine)

**Rerun on 2026-11-18 after the dropped-face fix** (`validation/mesh_leak.md`). The run before it (2026-11-07) had 2339 faces dropped (surface 7047 m², now 7627 m²) and lost 22 - 24 % of the rays (now 1.9 - 2.4 %, still above the 0.1 % limit: the results stand with that reservation). Against the earlier run, same seeds: T30 +0.9 % on average (single zone and band -5.0 … +5.3 %), EDT +0.4 % (-3.4 … +11.2 %), C80 within 0.2 dB; mean absolute error over all bands and zones T30 2.63 → 2.60 JND, EDT 3.58 → 3.50, C80 1.67 → 1.68, Ts 1.45 → 1.43. The changes are within the ray noise of 20 000 rays (`validation/ray_noise.md`).

Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria sheet (mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged. Positions and tag-to-material assignments: validate_fratoni.py (VENUES); heights are assumptions (see there).

```
DUS: OBJ 9852 faces (2307 narrow faces kept two-sided, 32 not at the room and 0 untagged ones in the surface band left out), voxel 0.080 m, room volume (voxels) 8771 m3; model built in 4 s
surface areas (m2): Marble 224, Plaster (hall) 2776, Seats (balconies) 608, Seats (stalls) 305, Stage grid 200, Stage house 1197, Velvet drapes 211, Wood 2105; total 7627
Sabine T (s), no air: 125 Hz 1.30, 250 Hz 1.12, 500 Hz 1.11, 1000 Hz 1.03, 2000 Hz 1.05, 4000 Hz 1.07
tags -> materials: Plaster_fly_tower -> Stage house, Plaster -> Plaster (hall), Wings -> Stage house, Grid -> Stage grid, Carpet -> Wood, Wood -> Wood, Marble -> Marble, Velvet -> Velvet drapes, Seats_stalls -> Seats (stalls), Seats_first_gallery -> Seats (balconies), Seats_second_gallery -> Seats (balconies)
browser engine: image sources to order 2, 20000 rays per source; S1 65 s (478 rays lost), S2 76 s (380 rays lost); total 146 s
```

## S1, STALLS (R1,R2,R3,R4,R5,R6) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.74 | 1.58 | 1.42 | 1.24 | 1.02 | 0.76 | | |
| | browser 3D | 1.79 (+0.6) | 1.60 (+0.2) | 1.58 (+2.3) | 1.45 (+3.4) | 1.38 (+7.0) | 1.26 (+13.2) | 2.8 | 4.4 |
| T30 | measured | 1.96 | 1.70 | 1.45 | 1.34 | 1.19 | 0.97 | | |
| | browser 3D | 1.62 (-3.4) | 1.40 (-3.6) | 1.40 (-0.6) | 1.38 (+0.6) | 1.28 (+1.6) | 1.14 (+3.6) | 0.6 | 2.2 |
| C80 | measured | 1.58 | 4.87 | 3.83 | 5.36 | 5.42 | 7.75 | | |
| | browser 3D | 0.95 (-0.6) | 1.98 (-2.9) | 2.07 (-1.8) | 2.69 (-2.7) | 3.06 (-2.4) | 3.92 (-3.8) | 2.2 | 2.4 |
| Ts | measured | 106 | 69 | 75 | 57 | 57 | 40 | | |
| | browser 3D | 102 (-0.3) | 86 (+1.7) | 85 (+1.0) | 77 (+1.9) | 73 (+1.6) | 63 (+2.3) | 1.5 | 1.5 |

## S1, 1st BALCONY (R7, R8, R9, R10) (4)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.68 | 1.23 | 1.12 | 1.03 | 0.89 | 0.80 | | |
| | browser 3D | 1.54 (-1.7) | 1.34 (+1.8) | 1.32 (+3.4) | 1.21 (+3.4) | 1.16 (+6.0) | 1.04 (+6.1) | 3.4 | 3.7 |
| T30 | measured | 2.06 | 1.62 | 1.46 | 1.29 | 1.14 | 0.92 | | |
| | browser 3D | 1.71 (-3.4) | 1.43 (-2.3) | 1.39 (-0.9) | 1.28 (-0.1) | 1.24 (+1.8) | 1.10 (+3.9) | 0.5 | 2.1 |
| C80 | measured | -0.92 | 2.16 | 2.30 | 2.93 | 3.75 | 4.66 | | |
| | browser 3D | 0.13 (+1.0) | 1.21 (-1.0) | 1.59 (-0.7) | 2.39 (-0.5) | 2.30 (-1.5) | 2.93 (-1.7) | 0.6 | 1.1 |
| Ts | measured | 140 | 93 | 87 | 72 | 69 | 59 | | |
| | browser 3D | 115 (-2.5) | 97 (+0.5) | 93 (+0.6) | 83 (+1.0) | 82 (+1.3) | 75 (+1.6) | 0.8 | 1.2 |

## S1, 2nd BALCONY (R13, R14, R15, R16, R17, R18) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.92 | 1.49 | 1.23 | 1.09 | 0.96 | 0.77 | | |
| | browser 3D | 1.76 (-1.7) | 1.49 (-0.0) | 1.49 (+4.2) | 1.18 (+1.6) | 1.10 (+3.0) | 0.92 (+3.8) | 2.9 | 2.4 |
| T30 | measured | 2.07 | 1.79 | 1.53 | 1.39 | 1.22 | 0.98 | | |
| | browser 3D | 1.69 (-3.6) | 1.42 (-4.1) | 1.39 (-1.8) | 1.38 (-0.2) | 1.29 (+1.2) | 1.18 (+4.2) | 1.0 | 2.5 |
| C80 | measured | -1.43 | -0.49 | 1.61 | 3.02 | 3.85 | 4.90 | | |
| | browser 3D | 1.17 (+2.6) | 2.39 (+2.9) | 2.65 (+1.0) | 3.52 (+0.5) | 3.68 (-0.2) | 4.43 (-0.5) | 0.8 | 1.3 |
| Ts | measured | 144 | 119 | 97 | 82 | 74 | 60 | | |
| | browser 3D | 113 (-3.1) | 95 (-2.4) | 93 (-0.4) | 82 (-0.0) | 79 (+0.5) | 70 (+1.1) | 0.2 | 1.3 |

## S2, STALLS (R1,R2,R3,R4,R5,R6) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 2.05 | 1.61 | 1.51 | 1.29 | 1.20 | 1.03 | | |
| | browser 3D | 1.81 (-2.4) | 1.56 (-0.5) | 1.51 (-0.0) | 1.31 (+0.4) | 1.25 (+0.8) | 1.12 (+1.8) | 0.2 | 1.0 |
| T30 | measured | 1.95 | 1.70 | 1.49 | 1.32 | 1.17 | 0.96 | | |
| | browser 3D | 1.63 (-3.3) | 1.40 (-3.5) | 1.36 (-1.8) | 1.33 (+0.1) | 1.29 (+2.0) | 1.17 (+4.3) | 1.0 | 2.5 |
| C80 | measured | -2.93 | 1.37 | 1.37 | 3.85 | 3.42 | 6.69 | | |
| | browser 3D | -0.78 (+2.2) | 0.58 (-0.8) | 0.81 (-0.6) | 1.79 (-2.1) | 2.15 (-1.3) | 2.99 (-3.7) | 1.3 | 1.8 |
| Ts | measured | 164 | 102 | 95 | 71 | 71 | 43 | | |
| | browser 3D | 125 (-3.9) | 103 (+0.0) | 98 (+0.3) | 84 (+1.3) | 80 (+0.9) | 71 (+2.8) | 0.8 | 1.5 |

## S2, 1st BALCONY (R7, R8, R9, R10) (4)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.50 | 1.34 | 1.07 | 0.87 | 0.71 | 0.63 | | |
| | browser 3D | 1.65 (+2.0) | 1.40 (+0.8) | 1.33 (+4.9) | 1.07 (+4.6) | 1.06 (+9.8) | 1.00 (+11.8) | 4.7 | 5.7 |
| T30 | measured | 1.92 | 1.69 | 1.45 | 1.27 | 1.09 | 0.90 | | |
| | browser 3D | 1.81 (-1.2) | 1.64 (-0.6) | 1.61 (+2.2) | 1.46 (+2.9) | 1.49 (+7.2) | 1.27 (+8.4) | 2.6 | 3.8 |
| C80 | measured | -0.42 | 2.25 | 3.87 | 5.48 | 7.39 | 8.29 | | |
| | browser 3D | 0.64 (+1.1) | 2.09 (-0.2) | 2.59 (-1.3) | 4.07 (-1.4) | 4.10 (-3.3) | 4.85 (-3.4) | 1.3 | 1.8 |
| Ts | measured | 119 | 90 | 73 | 59 | 45 | 39 | | |
| | browser 3D | 113 (-0.6) | 91 (+0.1) | 87 (+1.3) | 73 (+1.4) | 71 (+2.5) | 63 (+2.4) | 1.4 | 1.4 |

## S2, 2nd BALCONY (R13, R14, R15, R16, R17, R18) (6)

| criterion | model | 125 Hz | 250 Hz | 500 Hz | 1000 Hz | 2000 Hz | 4000 Hz | mean abs (JND) 500-1k | mean abs (JND) all |
|---|---|---|---|---|---|---|---|---|---|
| EDT | measured | 1.93 | 1.62 | 1.24 | 0.97 | 0.80 | 0.64 | | |
| | browser 3D | 1.72 (-2.2) | 1.36 (-3.1) | 1.32 (+1.4) | 1.15 (+3.6) | 1.05 (+6.3) | 0.84 (+6.0) | 2.5 | 3.8 |
| T30 | measured | 2.01 | 1.75 | 1.53 | 1.37 | 1.18 | 0.97 | | |
| | browser 3D | 1.76 (-2.5) | 1.52 (-2.6) | 1.47 (-0.7) | 1.34 (-0.4) | 1.36 (+3.2) | 1.25 (+5.7) | 0.6 | 2.5 |
| C80 | measured | -0.21 | -0.40 | 2.97 | 4.98 | 6.60 | 7.45 | | |
| | browser 3D | 2.43 (+2.6) | 3.96 (+4.4) | 4.29 (+1.3) | 5.58 (+0.6) | 5.90 (-0.7) | 6.69 (-0.8) | 1.0 | 1.7 |
| Ts | measured | 134 | 123 | 83 | 64 | 51 | 46 | | |
| | browser 3D | 102 (-3.2) | 81 (-4.2) | 77 (-0.6) | 64 (+0.0) | 62 (+1.1) | 55 (+1.0) | 0.3 | 1.7 |

Values in brackets: simulated - measured in JND (ISO 3382-1 Annex A: EDT / T30 5 %, C80 / C50 1 dB, Ts 10 ms).

## Summary: mean absolute difference in JND, 500 Hz - 1 kHz (all bands in brackets), over sources and zones

- EDT: 2.8 (3.5); signed 500 Hz - 1 kHz +2.8
- T30: 1.0 (2.6); signed 500 Hz - 1 kHz -0.1
- C80: 1.2 (1.7); signed 500 Hz - 1 kHz -0.6
- Ts: 0.8 (1.4); signed 500 Hz - 1 kHz +0.6
