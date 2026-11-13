"""
Model of the variable-acoustics room Arni (Aalto Acoustics Lab, Espoo) for validation/arni_check.py.

Sources (read off, not survey data):
- Room 8.9 x 6.3 x 3.6 m, shoebox; floor painted concrete; walls and ceiling carry 55 panels 0.6 x 0.4 x 2.4 m (painted
  metal fronts with slots that are open or closed, 25 cm absorber behind): 8 on each of three walls standing on the
  floor, 11 on the fourth wall hanging 0.63 m above the floor, 20 on the ceiling; curtains folded in the four corners.
  Prawda, Schlecht, Valimaki, "Dataset of impulse responses from variable acoustics room Arni at Aalto Acoustic Labs"
  (Akustiikkapaivat 2021), https://acris.aalto.fi/ws/portalfiles/portal/76717691/2021_ArniMeasurements_Akupaivat_Prawda_paper.pdf
- Panel positions, source and microphone positions: Arni_layout.jpg and Arni_panels_numbers.pdf of the dataset
  https://doi.org/10.5281/zenodo.6985104 (CC BY 4.0), read off the drawing (1 m = 195.6 px; about +-3 cm).

Frame: x along the 8.9 m side (0 at the left wall of the layout drawing), y along the 6.3 m side (0 at the wall with
the door), z up from the floor.

Assumptions (engineering, not from the sources): ceiling panels mounted flush with the ceiling (bottom face at 3.2 m);
each folded curtain a 0.5 x 0.5 m column over the full height; the door and the heating are part of the bare wall.

    python validation/arni_model.py [--out out/arni/arni.obj]
"""
import argparse
import os

import numpy as np

L, W, H = 8.9, 6.3, 3.6
PX, OX, OY = 195.6, 82.0, 1320.0           # layout drawing: px per m, inner corner (x 0, y 0)
SRC = (2.40, 1.80, 1.43)
MICS = {"1": (7.15, 2.00, 1.35), "2": (6.90, 4.81, 1.39), "3": (4.45, 3.80, 1.44), "4": (1.30, 3.15, 1.54),
        "5": (3.81, 1.45, 1.54)}
DEPTH, PW, PH = 0.4, 0.6, 2.4               # panel depth, width, height
TOP_Z0 = 0.63                              # the 11 panels on the y = 6.3 m wall hang 0.63 m above the floor
CURTAIN = 0.5

# alpha of the panel fronts, octave bands 250 Hz - 8 kHz (DELTA report, quoted in Prawda et al. 2021, see above);
# 125 Hz is not given: the 250 Hz value is used (assumption)
ALPHA_CLOSED = [0.09, 0.09, 0.05, 0.05, 0.04, 0.02]     # 125 (assumed) ... 4 kHz
ALPHA_OPEN = [0.86, 0.86, 0.77, 0.66, 0.45, 0.38]


def x_m(px):
    return (px - OX) / PX


def y_m(py):
    return (OY - py) / PX


def panels():
    """{panel number: (kind, x0, x1, y0, y1, z0, z1)}; kind: wall_y0, wall_x0, wall_x1, wall_y1, ceiling."""
    P = {}
    xb = np.linspace(x_m(200), x_m(1140), 9)                   # y = 0 wall, panels 16 (left) ... 9
    for i, n in enumerate(range(16, 8, -1)):
        P[n] = ("wall_y0", xb[i], xb[i + 1], 0.0, DEPTH, 0.0, PH)
    yb = np.linspace(y_m(1173), y_m(233), 9)                   # side walls, bottom to top
    for i in range(8):
        P[17 + i] = ("wall_x0", 0.0, DEPTH, yb[i], yb[i + 1], 0.0, PH)     # 17 bottom ... 24 top
        P[8 - i] = ("wall_x1", L - DEPTH, L, yb[i], yb[i + 1], 0.0, PH)    # 8 bottom ... 1 top
    xt = list(np.linspace(x_m(197), x_m(903), 7)), list(np.linspace(x_m(1065), x_m(1653), 6))
    for i in range(6):
        P[25 + i] = ("wall_y1", xt[0][i], xt[0][i + 1], W - DEPTH, W, TOP_Z0, TOP_Z0 + PH)
    for i in range(5):
        P[31 + i] = ("wall_y1", xt[1][i], xt[1][i + 1], W - DEPTH, W, TOP_Z0, TOP_Z0 + PH)
    rows = (y_m(663), y_m(193)), (y_m(1135), y_m(663))         # upper row (48-51, 52-55), lower row (46-43, 40-37)
    mid = (y_m(900), y_m(430))
    for cl, x0 in ((0, x_m(285)), (1, x_m(1150))):
        xs = x0 + PW * np.arange(5)
        up = [48, 49, 50, 51] if cl == 0 else [52, 53, 54, 55]
        lo = [46, 45, 44, 43] if cl == 0 else [40, 39, 38, 37]
        for i in range(4):
            P[up[i]] = ("ceiling", xs[i], xs[i + 1], rows[0][0], rows[0][1], H - DEPTH, H)
            P[lo[i]] = ("ceiling", xs[i], xs[i + 1], rows[1][0], rows[1][1], H - DEPTH, H)
        a, b = (47, 42) if cl == 0 else (41, 36)
        P[a] = ("ceiling", x0 - PW, x0, mid[0], mid[1], H - DEPTH, H)
        P[b] = ("ceiling", xs[4], xs[4] + PW, mid[0], mid[1], H - DEPTH, H)
    return P


class Obj:
    def __init__(self):
        self.v, self.f = [], []

    def face(self, pts, mat):
        i0 = len(self.v)
        self.v += [tuple(map(float, p)) for p in pts]
        self.f.append((mat, list(range(i0 + 1, i0 + 1 + len(pts)))))

    def text(self):
        out = ["# Arni variable acoustics room (validation/arni_model.py); z up, metres"]
        out += [f"v {p[0]:.4f} {p[1]:.4f} {p[2]:.4f}" for p in self.v]
        for mat, idx in sorted(self.f, key=lambda f: f[0]):
            out += [f"g {mat}", "f " + " ".join(map(str, idx))]
        return "\n".join(out) + "\n"


def cuboid(o, x0, x1, y0, y1, z0, z1, mats, skip=()):
    """Faces of a box; mats / skip keyed by side: x0, x1, y0, y1, z0, z1."""
    F = {"x0": [(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)],
         "x1": [(x1, y0, z0), (x1, y0, z1), (x1, y1, z1), (x1, y1, z0)],
         "y0": [(x0, y0, z0), (x0, y0, z1), (x1, y0, z1), (x1, y0, z0)],
         "y1": [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)],
         "z0": [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)],
         "z1": [(x0, y0, z1), (x0, y1, z1), (x1, y1, z1), (x1, y0, z1)]}
    for k, pts in F.items():
        if k not in skip:
            o.face(pts, mats.get(k, mats["default"]))


FRONT = {"wall_y0": "y1", "wall_y1": "y0", "wall_x0": "x1", "wall_x1": "x0", "ceiling": "z0"}
BACK = {"wall_y0": "y0", "wall_y1": "y1", "wall_x0": "x0", "wall_x1": "x1", "ceiling": "z1"}


def build():
    """OBJ text; groups: shell (floor, bare walls, ceiling), curtain, side (panel sides), p1 ... p55 (panel fronts)."""
    o = Obj()
    cuboid(o, 0, L, 0, W, 0, H, {"default": "shell"})          # room shell
    for n, (kind, x0, x1, y0, y1, z0, z1) in panels().items():
        skip = {BACK[kind]}
        if z0 == 0.0:
            skip.add("z0")                                       # standing on the floor
        cuboid(o, x0, x1, y0, y1, z0, z1, {"default": "side", FRONT[kind]: f"p{n}"}, skip)
    c = CURTAIN
    for cx, cy, sk in ((0, 0, ("x0", "y0")), (L - c, 0, ("x1", "y0")), (0, W - c, ("x0", "y1")),
                       (L - c, W - c, ("x1", "y1"))):
        cuboid(o, cx, cx + c, cy, cy + c, 0, H, {"default": "curtain"}, set(sk) | {"z0", "z1"})
    return o.text()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "out", "arni", "arni.obj"))
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    open(a.out, "w").write(build())
    P = panels()
    for k in ("wall_y0", "wall_x0", "wall_x1", "wall_y1", "ceiling"):
        print(k, sorted(n for n, v in P.items() if v[0] == k))
    print("written", a.out)


if __name__ == "__main__":
    main()
