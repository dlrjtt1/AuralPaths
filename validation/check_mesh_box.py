"""
Check of the OBJ mesh path (geometry.build_mesh: voxel flood fill, inward normals, back-facing twins, 1 mm overlap)
on a shoebox written as an OBJ of 1 m tiles: the ray-traced T30 should follow Eyring as the plain shoebox does
(validation/check_rt_eyring.py).

    python validation/check_mesh_box.py [scattering]

Result on 2026-11-05 (12 x 7 x 9 m, alpha 0.2, scattering 0.5, 20 000 rays, air absorption on):
    T30 1.09 / 1.07 / 1.04 s at 125 / 500 / 2000 Hz; Eyring 1.07 s, Sabine 1.19 s (no air); voxel volume 731 m3 (756).
With scattering 1.0 (pure Lambert): T30 1.03 / 1.02 / 0.99 s, below Eyring; with 0.1: 1.14 / 1.12 / 1.08 s
(validation/check_box_lambert.js compares the browser tracer on the same box).
The same test on the BRAS CR3 mesh (alpha 0.2 everywhere, scattering 0.5) gave T30 about 1.03 s against Eyring
0.83 s and Sabine 0.93 s: the hall decays slower than diffuse-field theory; the mesh path itself does not.
"""
import os
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import brir_proto as bp                       # noqa: E402
from validate_fratoni import criteria         # noqa: E402

X, Y, Z = 12.0, 7.0, 9.0                      # OBJ y-up: x, height, depth
V, F = [], []


def quad(p0, u, v, nu, nv):
    for i in range(nu):
        for j in range(nv):
            a = np.add(p0, np.multiply(u, i / nu) + np.multiply(v, j / nv))
            b = a + np.multiply(u, 1 / nu)
            c = b + np.multiply(v, 1 / nv)
            d = a + np.multiply(v, 1 / nv)
            k = len(V)
            V.extend([a, b, c, d])
            F.append([k + 1, k + 2, k + 3, k + 4])


quad([0, 0, 0], [X, 0, 0], [0, 0, Z], 12, 9); quad([0, Y, 0], [X, 0, 0], [0, 0, Z], 12, 9)
quad([0, 0, 0], [X, 0, 0], [0, Y, 0], 12, 7); quad([0, 0, Z], [X, 0, 0], [0, Y, 0], 12, 7)
quad([0, 0, 0], [0, 0, Z], [0, Y, 0], 9, 7); quad([X, 0, 0], [0, 0, Z], [0, Y, 0], 9, 7)
path = os.path.join(tempfile.mkdtemp(), "box.obj")
with open(path, "w") as f:
    f.write("g wall\n")
    f.writelines("v %f %f %f\n" % tuple(p) for p in V)
    f.writelines("f " + " ".join(map(str, q)) + "\n" for q in F)
a, s = 0.2, float(sys.argv[1]) if len(sys.argv) > 1 else 0.5   # optional argument: scattering
cfg = {"name": "box", "fs": 48000, "c": 343.5, "room": {"air_absorption": True, "dims_m": [1, 1, 1], "stage_depth_m": 0},
       "binaural": {"late_directional": False}, "sources": {"S": {"pos": [3, -3, 1.5]}},
       "receivers": {"R1": [8, -5, 1.2], "R2": [6, -2, 2.0], "R3": [10, -7, 3.0]},
       "geometry": {"mesh": {"obj": path, "groups": {"wall": "w"}}, "materials": {"w": {"alpha": [a] * 6, "s": s}},
                    "ism_order": 0, "rays": 20000, "diffraction": False}}
G = bp._geom(cfg)
H, cen = bp.energy_hists(cfg, "S", ["R1", "R2", "R3"], t_max=3.0, n_rays=20000)
bi = [int(np.argmin(np.abs(np.asarray(cen) - b))) for b in (125, 500, 2000)]
T = np.nanmean([criteria(H[r][bi], 0.0)["T30"] for r in H], 0)
Vv, Ss = X * Y * Z, 2 * (X * Y + X * Z + Y * Z)
print(f"tiled box mesh: {len(G['S'])} walls, voxel volume {G['volume']:.0f} m3 (true {Vv:.0f}); T30 125/500/2000 Hz "
      f"{T.round(2)} s; Eyring {0.161 * Vv / (-Ss * np.log(1 - a)):.2f} s, Sabine {0.161 * Vv / (Ss * a):.2f} s (no air)")
