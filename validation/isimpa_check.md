# AuralPaths vs I-Simpa (SPPS): same halls, same inputs

Independent free simulator: I-Simpa's SPPS solver (sound particle tracing; Universite Gustave Eiffel, GPL-3.0,
https://github.com/Universite-Gustave-Eiffel/I-Simpa, main of 2026-01-14), run headless by `validation/check_isimpa.py`
(build notes and the one source fix needed on Linux are in its docstring). Same geometry (BRAS OBJ), materials (BRAS
fitted estimates, absorption and scattering per octave), source and receiver positions (BRAS), receiver radius 0.5 m
and air absorption as the AuralPaths runs in `validation/bras_CR3.*`, `bras_CR4.*` (Python 3D mesh, image sources
order 1 + ray tracing). SPPS: energetic method, 300 000 particles per source and band, 1 ms steps, 3 s.

## Shoebox (12 x 9 x 7 m, alpha 0.2 everywhere, no air absorption), T30 mean of the six octaves

| scattering | SPPS | AuralPaths browser tracer (`check_box_lambert.js`) |
|---|---|---|
| 1.0 | 1.12 s | 1.11 s |
| 0.5 | 1.10 s | 1.15 s |
| 0.1 | 1.13 s | not run |

In a diffuse box the two tracers agree within 0–4 %. Eyring 1.07 s, Sabine 1.19 s.

## CR3 (10 position pairs; band means)

Mesh for SPPS: 2600 triangles after 1 repair(s), 3969 tetrahedra; SPPS run 457 s for both sources.

| criterion | 125 | 250 | 500 | 1k | 2k | 4k Hz (SPPS / AuralPaths Python / measured) |
|---|---|---|---|---|---|---|
| T30 | 2.14 / 1.72 / 1.63 | 1.81 / 1.53 / 1.45 | 1.70 / 1.40 / 1.30 | 1.71 / 1.44 / 1.34 | 1.56 / 1.43 / 1.32 | 1.19 / 1.19 / 1.06 |
| EDT | 1.94 / 1.83 / 1.60 | 1.61 / 1.51 / 1.36 | 1.53 / 1.42 / 1.34 | 1.58 / 1.50 / 1.31 | 1.49 / 1.45 / 1.24 | 1.16 / 1.14 / 1.05 |
| C80 | -0.54 / -0.24 / 0.59 | 0.65 / 1.08 / 0.86 | 0.89 / 1.41 / 1.47 | 0.49 / 0.93 / 1.71 | 0.74 / 1.12 / 1.59 | 2.30 / 2.45 / 3.24 |
| Ts | 135 / 125 / 111 | 111 / 102 / 97 | 106 / 96 / 94 | 111 / 103 / 92 | 106 / 100 / 91 | 82 / 81 / 70 |

Mean absolute difference (signed mean) in JND at 500 Hz – 2 kHz over the 10 pairs:

| criterion | SPPS − measured | AuralPaths − measured | SPPS − AuralPaths |
|---|---|---|---|
| T30 | 5.1 (+5.1) | 1.8 (+1.6) | 3.4 (+3.4) |
| EDT | 3.7 (+3.7) | 3.0 (+2.6) | 1.2 (+1.1) |
| C80 | 1.1 (-0.9) | 0.8 (-0.4) | 0.5 (-0.4) |
| Ts | 1.6 (+1.5) | 1.0 (+0.7) | 0.8 (+0.8) |

## CR4 (10 position pairs; band means)

Mesh for SPPS: 5158 triangles after 1 repair(s), 11449 tetrahedra; SPPS run 696 s for both sources.

| criterion | 125 | 250 | 500 | 1k | 2k | 4k Hz (SPPS / AuralPaths Python / measured) |
|---|---|---|---|---|---|---|
| T30 | 2.81 / 2.61 / 2.31 | 2.82 / 2.60 / 2.36 | 2.46 / 2.28 / 2.07 | 2.39 / 2.30 / 2.10 | 2.05 / 2.05 / 1.84 | 1.61 / 1.70 / 1.42 |
| EDT | 2.85 / 2.83 / 2.26 | 2.85 / 2.82 / 2.43 | 2.50 / 2.50 / 2.10 | 2.42 / 2.50 / 2.19 | 2.15 / 2.21 / 1.86 | 1.72 / 1.74 / 1.42 |
| C80 | -2.31 / -1.46 / -0.49 | -2.50 / -1.45 / -1.83 | -1.75 / -0.75 / 0.20 | -1.86 / -0.82 / -0.65 | -1.49 / -0.33 / -0.08 | -0.02 / 0.83 / 1.98 |
| Ts | 193 / 178 / 146 | 197 / 178 / 167 | 170 / 155 / 129 | 168 / 157 / 143 | 151 / 140 / 126 | 118 / 113 / 91 |

Mean absolute difference (signed mean) in JND at 500 Hz – 2 kHz over the 10 pairs:

| criterion | SPPS − measured | AuralPaths − measured | SPPS − AuralPaths |
|---|---|---|---|
| T30 | 3.0 (+3.0) | 2.1 (+2.1) | 1.4 (+0.8) |
| EDT | 3.0 (+3.0) | 3.7 (+3.5) | 1.9 (-0.2) |
| C80 | 1.6 (-1.5) | 1.6 (-0.5) | 1.6 (-1.1) |
| Ts | 3.0 (+3.0) | 2.3 (+1.8) | 1.8 (+1.3) |

## Reading

- Diffuse box: both tracers within 0–4 %, so the basic energy bookkeeping agrees.
- CR4: the two simulators agree with each other within about 1–2 JND (T30 SPPS about 4 % longer, EDT equal, C80 1 dB lower in SPPS).
- CR3: SPPS decays clearly slower (T30 about 17 % longer than AuralPaths, about 25 % longer than measured); the early criteria agree better (EDT 1.2 JND, C80 0.5 dB).
  The difference is specific to this hall, where most surfaces have scattering 0.05–0.15; candidates are the two reflection models
  (SPPS: a Lambert reflection with probability s; AuralPaths/pyroomacoustics: one direction blended from Lambert and specular) and the rays
  the AuralPaths browser tracer loses through gaps in the model (about 12 % of the rays over 3 s in CR3; SPPS loses about 0.01 % in its tetrahedral mesh).
  Not resolved.
- Neither simulator reproduces the measurement with these inputs (the BRAS coefficients were fitted with the Eyring formula, not for either
  program); differences between simulators of this size are expected (Brinkmann et al. 2019, https://doi.org/10.1121/1.5096178). This check
  shows that AuralPaths is not an outlier against an independent implementation in CR4 and in a diffuse box, and documents the CR3 difference.
