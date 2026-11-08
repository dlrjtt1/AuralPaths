# BRAS CR4: early energy by surface at the binaural listener (browser engine)

`validation/early_paths.py`: voxel 0.15 m, 5174 faces, 300000 rays per source, image sources to order 2; sources with the measured K8 pattern (BRAS), LS3 - LS6 aimed at the head, LS7 horizontal. Energy: sum of the 250 Hz - 2 kHz octaves. Windows in ms after the direct sound. Materials: BRAS fitted estimates (tags without the `mat_CR4_` prefix). Run time 1674 s.

## LS3

| window (ms) | 0–3 | 3–20 | 20–50 | 50–80 |
|---|---|---|---|---|
| share of 0–80 ms, measured (%) | 74 | 10 | 10 | 7 |
| share of 0–80 ms, browser engine (%) | 64 | 0 | 27 | 9 |

**3–20 ms, rays** (14 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| seating | 100 % | 0.1, -6.9, -0.3 |

reflections: 1: 100 %; first → last surface: seating → seating 100 %

**20–50 ms, rays** (532 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| whitePanels | 51 % | -0.8, -0.4, 8.0 |
| linoleum | 38 % | -0.1, -7.6, -0.2 |
| concrete | 5 % | 1.3, 4.0, 3.1 |
| seating | 4 % | 0.5, -8.0, -0.2 |
| brickwall | 3 % | -12.9, -1.5, 0.9 |

reflections: 1: 34 %, 2: 50 %, 3: 15 %, 4: 1 %, 5: 0 %, 6+: 0 %; first → last surface: whitePanels → whitePanels 31 %, whitePanels → linoleum 26 %, parquet → whitePanels 19 %, parquet → linoleum 10 %

image sources in the window: 11, energy 56 % of the ray energy; strongest: whitePanels at 33.1 ms (16 %); parquet → whitePanels at 38.4 ms (13 %); whitePanels → linoleum at 39.9 ms (10 %); whitePanels at 25.8 ms (5 %); parquet → whitePanels at 31.7 ms (3 %)

**50–80 ms, rays** (207 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| linoleum | 30 % | -0.5, -8.4, -0.2 |
| brickwall | 26 % | 4.1, -0.2, 2.9 |
| concrete | 22 % | 3.0, -0.9, 9.4 |
| whitePanels | 17 % | -4.2, -3.8, 9.5 |
| seating | 6 % | -1.1, -8.9, -0.1 |

reflections: 1: 15 %, 2: 23 %, 3: 43 %, 4: 16 %, 5: 1 %, 6+: 2 %; first → last surface: brickwall → brickwall 14 %, parquet → concrete 13 %, parquet → whitePanels 10 %, parquet → linoleum 9 %

image sources in the window: 5, energy 15 % of the ray energy; strongest: brickwall at 56.3 ms (10 %); brickwall → seating at 56.9 ms (3 %); whitePanels → brickwall at 60.0 ms (2 %); brickwall → concrete at 66.2 ms (0 %); concrete → brickwall at 73.2 ms (0 %)

## LS4

| window (ms) | 0–3 | 3–20 | 20–50 | 50–80 |
|---|---|---|---|---|
| share of 0–80 ms, measured (%) | 75 | 9 | 9 | 7 |
| share of 0–80 ms, browser engine (%) | 60 | 1 | 25 | 13 |

**3–20 ms, rays** (15 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| seating | 100 % | -0.8, -7.2, -0.3 |

reflections: 1: 100 %; first → last surface: seating → seating 100 %

**20–50 ms, rays** (391 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| whitePanels | 51 % | -0.3, -0.1, 7.6 |
| linoleum | 30 % | -0.0, -7.4, -0.2 |
| concrete | 6 % | 1.2, 3.7, 3.4 |
| seating | 6 % | -0.1, -8.1, -0.2 |
| brickwall | 6 % | -12.8, -0.9, 0.6 |

reflections: 1: 41 %, 2: 41 %, 3: 18 %, 4: 1 %, 6+: 0 %; first → last surface: whitePanels → whitePanels 32 %, parquet → whitePanels 19 %, whitePanels → linoleum 17 %, parquet → linoleum 12 %

image sources in the window: 9, energy 79 % of the ray energy; strongest: whitePanels at 31.5 ms (24 %); parquet → whitePanels at 36.6 ms (18 %); whitePanels at 20.8 ms (14 %); whitePanels → linoleum at 38.1 ms (13 %); whitePanels → linoleum at 22.2 ms (6 %)

**50–80 ms, rays** (253 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| linoleum | 33 % | 0.0, -9.2, -0.1 |
| brickwall | 24 % | 5.3, -0.2, 4.5 |
| whitePanels | 19 % | 1.4, -5.4, 7.5 |
| concrete | 17 % | -0.1, -1.6, 9.7 |
| seating | 7 % | 0.1, -8.8, -0.1 |

reflections: 1: 13 %, 2: 24 %, 3: 45 %, 4: 11 %, 5: 6 %, 6+: 1 %; first → last surface: whitePanels → linoleum 23 %, brickwall → brickwall 10 %, concrete → brickwall 8 %, parquet → whitePanels 8 %

image sources in the window: 4, energy 7 % of the ray energy; strongest: brickwall at 51.5 ms (6 %); brickwall → seating at 52.1 ms (1 %); concrete → brickwall at 67.3 ms (0 %); brickwall → concrete at 64.9 ms (0 %)

## LS5

| window (ms) | 0–3 | 3–20 | 20–50 | 50–80 |
|---|---|---|---|---|
| share of 0–80 ms, measured (%) | 76 | 9 | 9 | 7 |
| share of 0–80 ms, browser engine (%) | 61 | 1 | 26 | 12 |

**3–20 ms, rays** (17 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| seating | 100 % | 0.7, -7.2, -0.3 |

reflections: 1: 100 %; first → last surface: seating → seating 100 %

**20–50 ms, rays** (386 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| whitePanels | 50 % | 0.4, 0.4, 7.2 |
| linoleum | 35 % | 0.0, -7.6, -0.2 |
| concrete | 6 % | -3.5, 6.0, 1.4 |
| brickwall | 6 % | 12.8, -0.8, 0.8 |
| seating | 3 % | -0.2, -7.6, -0.2 |

reflections: 1: 43 %, 2: 41 %, 3: 15 %, 4: 1 %, 6+: 0 %; first → last surface: whitePanels → whitePanels 34 %, whitePanels → linoleum 22 %, parquet → whitePanels 16 %, parquet → linoleum 10 %

image sources in the window: 9, energy 78 % of the ray energy; strongest: whitePanels at 31.5 ms (24 %); parquet → whitePanels at 36.6 ms (18 %); whitePanels at 20.8 ms (14 %); whitePanels → linoleum at 38.1 ms (12 %); whitePanels → linoleum at 22.2 ms (6 %)

**50–80 ms, rays** (225 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| linoleum | 30 % | -0.3, -9.1, -0.1 |
| brickwall | 23 % | -5.3, 0.2, 5.8 |
| concrete | 22 % | -0.8, 0.2, 9.2 |
| whitePanels | 20 % | 0.4, -5.8, 8.8 |
| seating | 5 % | -0.5, -8.1, -0.2 |

reflections: 1: 12 %, 2: 26 %, 3: 44 %, 4: 15 %, 5: 3 %, 6+: 0 %; first → last surface: whitePanels → linoleum 20 %, parquet → concrete 10 %, concrete → brickwall 9 %, parquet → whitePanels 8 %

image sources in the window: 4, energy 8 % of the ray energy; strongest: brickwall at 51.5 ms (7 %); brickwall → seating at 52.1 ms (1 %); concrete → brickwall at 67.3 ms (0 %); brickwall → concrete at 64.9 ms (0 %)

## LS6

| window (ms) | 0–3 | 3–20 | 20–50 | 50–80 |
|---|---|---|---|---|
| share of 0–80 ms, measured (%) | 77 | 6 | 11 | 7 |
| share of 0–80 ms, browser engine (%) | 63 | 1 | 27 | 9 |

**3–20 ms, rays** (20 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| seating | 100 % | 1.3, -6.7, -0.3 |

reflections: 1: 100 %; first → last surface: seating → seating 100 %

**20–50 ms, rays** (528 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| whitePanels | 54 % | 0.8, -0.3, 7.8 |
| linoleum | 32 % | 0.1, -7.5, -0.2 |
| concrete | 5 % | 1.3, 1.9, 4.2 |
| brickwall | 5 % | 12.9, -1.4, 0.9 |
| seating | 3 % | 0.1, -8.3, -0.2 |

reflections: 1: 41 %, 2: 45 %, 3: 14 %, 4: 0 %, 5: 0 %, 6+: 1 %; first → last surface: whitePanels → whitePanels 36 %, whitePanels → linoleum 23 %, parquet → whitePanels 18 %, parquet → linoleum 9 %

image sources in the window: 10, energy 56 % of the ray energy; strongest: whitePanels at 33.7 ms (17 %); parquet → whitePanels at 37.8 ms (12 %); whitePanels → linoleum at 40.4 ms (10 %); whitePanels at 26.4 ms (6 %); parquet → whitePanels at 31.1 ms (4 %)

**50–80 ms, rays** (212 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| brickwall | 39 % | -5.0, -0.5, 3.8 |
| linoleum | 25 % | -0.1, -8.5, -0.1 |
| concrete | 14 % | -2.2, -1.4, 10.4 |
| whitePanels | 12 % | 3.8, -3.0, 9.2 |
| seating | 10 % | 0.2, -8.8, -0.1 |

reflections: 1: 20 %, 2: 22 %, 3: 38 %, 4: 15 %, 5: 1 %, 6+: 2 %; first → last surface: brickwall → brickwall 19 %, parquet → brickwall 11 %, parquet → concrete 10 %, concrete → linoleum 8 %

image sources in the window: 5, energy 13 % of the ray energy; strongest: brickwall at 56.3 ms (9 %); brickwall → seating at 56.9 ms (2 %); whitePanels → brickwall at 60.0 ms (1 %); brickwall → concrete at 66.6 ms (0 %); concrete → brickwall at 73.5 ms (0 %)

## LS7

| window (ms) | 0–3 | 3–20 | 20–50 | 50–80 |
|---|---|---|---|---|
| share of 0–80 ms, measured (%) | 74 | 11 | 10 | 6 |
| share of 0–80 ms, browser engine (%) | 64 | 0 | 25 | 10 |

**3–20 ms, rays** (23 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| seating | 100 % | -0.8, -7.0, -0.3 |

reflections: 1: 100 %; first → last surface: seating → seating 100 %

**20–50 ms, rays** (473 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| whitePanels | 55 % | 0.3, 0.4, 7.1 |
| linoleum | 38 % | -0.0, -7.4, -0.3 |
| seating | 6 % | 0.6, -8.1, -0.2 |
| concrete | 1 % | -0.5, -3.5, 10.3 |

reflections: 1: 40 %, 2: 44 %, 3: 15 %, 4: 1 %, 6+: 0 %; first → last surface: whitePanels → whitePanels 40 %, whitePanels → linoleum 28 %, parquet → whitePanels 15 %, parquet → linoleum 8 %

image sources in the window: 8, energy 94 % of the ray energy; strongest: whitePanels at 32.1 ms (27 %); whitePanels → linoleum at 38.8 ms (16 %); whitePanels at 28.2 ms (15 %); parquet → whitePanels at 39.8 ms (15 %); whitePanels at 24.6 ms (7 %)

**50–80 ms, rays** (250 arrivals; share of the ray energy)

| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at 0.0, -8.5, 1.1) |
|---|---|---|
| brickwall | 28 % | 1.7, -0.7, 2.9 |
| linoleum | 27 % | 0.2, -8.7, -0.1 |
| whitePanels | 21 % | -0.7, -8.0, 8.1 |
| concrete | 17 % | -1.6, -0.8, 8.6 |
| seating | 6 % | -0.4, -8.9, -0.1 |

reflections: 1: 19 %, 2: 29 %, 3: 37 %, 4: 8 %, 5: 6 %, 6+: 1 %; first → last surface: brickwall → brickwall 14 %, whitePanels → linoleum 11 %, parquet → linoleum 8 %, parquet → whitePanels 7 %

image sources in the window: 6, energy 15 % of the ray energy; strongest: brickwall at 52.3 ms (4 %); brickwall at 52.3 ms (4 %); brickwall → seating at 53.1 ms (3 %); brickwall → seating at 53.1 ms (3 %); concrete at 57.9 ms (1 %)

