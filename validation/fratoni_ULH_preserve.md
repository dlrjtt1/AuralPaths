# Fratoni ULH: 2.5D conversion, choice of the absorption mapping (obj_to_hall.py --preserve)

T30 (s) of the 2.5D hall made from the ULH mesh, source S1, mean over the 26 receivers, 20 000 rays, same seeds;
in brackets: simulated - measured in JND (5 %). Data: G. Fratoni, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0).

| model | 125 Hz | 250 Hz | 500 Hz | 1 kHz | 2 kHz | 4 kHz |
|---|---|---|---|---|---|---|
| measured | 1.56 | 1.36 | 1.62 | 1.85 | 1.83 | 1.50 |
| 3D mesh | 1.39 (-2.3) | 1.28 (-1.2) | 1.70 (+0.9) | 1.94 (+1.0) | 1.84 (+0.1) | 1.43 (-0.9) |
| eyring (default) | 1.26 (-3.9) | 1.21 (-2.1) | 1.56 (-0.7) | 1.86 (+0.1) | 1.72 (-1.2) | 1.31 (-2.5) |
| room-eyring | 1.14 (-5.4) | 1.11 (-3.7) | 1.49 (-1.6) | 1.80 (-0.6) | 1.67 (-1.7) | 1.27 (-3.1) |
| sabine | 1.11 (-5.8) | 1.08 (-4.1) | 1.45 (-2.1) | 1.77 (-0.9) | 1.64 (-2.1) | 1.25 (-3.4) |

eyring: alpha_g = 1 - exp(-A_g / S_g); room-eyring: one factor per band keeping the room's Eyring exponent; sabine: alpha_g = A_g / S_g (A_g = absorption area of the group in the mesh, S_g = its area in the 2.5D hall). Run 2026-11-05.
