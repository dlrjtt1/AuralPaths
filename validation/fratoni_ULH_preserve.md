# Fratoni ULH: 2.5D conversion, choice of the absorption mapping (obj_to_hall.py --preserve)

T30 (s) of the 2.5D hall made from the ULH mesh, source S1, mean over the 26 receivers, 20 000 rays, same seeds;
in brackets: simulated - measured in JND (5 %). Data: G. Fratoni, Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0).

| model | 125 Hz | 250 Hz | 500 Hz | 1 kHz | 2 kHz | 4 kHz |
|---|---|---|---|---|---|---|
| measured | 1.56 | 1.36 | 1.62 | 1.85 | 1.83 | 1.50 |
| 3D mesh | 1.37 (-2.4) | 1.27 (-1.3) | 1.66 (+0.5) | 1.93 (+0.9) | 1.83 (+0.0) | 1.44 (-0.8) |
| eyring (default) | 1.27 (-3.7) | 1.22 (-2.1) | 1.58 (-0.5) | 1.89 (+0.4) | 1.75 (-0.9) | 1.32 (-2.4) |
| room-eyring | 1.16 (-5.1) | 1.12 (-3.5) | 1.50 (-1.5) | 1.82 (-0.3) | 1.69 (-1.5) | 1.28 (-2.9) |
| sabine | 1.12 (-5.6) | 1.09 (-4.0) | 1.47 (-1.9) | 1.79 (-0.6) | 1.66 (-1.9) | 1.26 (-3.2) |

eyring: alpha_g = 1 - exp(-A_g / S_g); room-eyring: one factor per band keeping the room's Eyring exponent; sabine: alpha_g = A_g / S_g (A_g = absorption area of the group in the mesh, S_g = its area in the 2.5D hall). Run 2026-11-06 with the ray-tracing energy floor fixed (brir_proto.RT_ENERGY_THRES); the 2026-11-05 run (energy_thres 1e-9) gave the same order, values 0.01-0.03 s shorter in the 2.5D rows.
