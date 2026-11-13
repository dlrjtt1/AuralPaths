"""
Model of the main auditorium of the Finnish National Opera (Helsinki) for validation/opera_check.py (OperaRIR).

Sources:
- Plan and section: Lokki, Patynen, Tervo, Siltanen, Savioja / Lokki et al., "Practical application and analysis of
  full orchestra spatial impulse responses in an opera house", Proc. IOA 37 Pt. 3 (2015), Figure 1 (post-2007 state),
  https://users.aalto.fi/~ktlokki/Publs/p6_2015.pdf. Read off the vector drawing in PDF points (page 3): plan scale
  bar 0 m at x = 204.5 pt, 25 m at x = 100.0 pt (4.18 pt / m); the section is at the same scale (receivers R1 - R5
  are 16.8 pt apart in both), its stage floor at y = 217.5 pt and its 0 m line at x = 426 pt.
- Seats and sources: OperaRIR_layout.mat of https://doi.org/10.5281/zenodo.8096639 (CC BY-NC 4.0): x across the hall
  (centre 12.83 m), y from the source line towards the back. The model uses the same x; model Y = y - Y_SHIFT, where
  Y_SHIFT puts row 2 on the second drawn seat row (about 0.8 m; read off, +-0.3 m).

Frame: X across (as OperaRIR x), Y from the 0 m line of the plan (proscenium) towards the back of the hall, z up
from the stage floor.

Engineering assumptions (not in the sources): the balconies are solid rings between the stalls outline and one
circular front line, their top at the parapet height (seating not modelled); the upper outer walls follow the stalls
outline (the drawing shows them 1 - 2 m further out); ceiling a function of Y only (lighting bridges and the
retrofitted reflectors left out); pit covered at the level of the front stalls; proscenium opening 14.6 m wide and
11 m high, wall 0.6 m thick; stage house 25.6 x 19.1 m, 26 m high (the drawing ends at 24 m), side and back wings
closed; ear height 1.2 m above the stalls floor.

    python validation/opera_model.py [--out out/opera/opera.obj]
"""
import argparse
import os

import numpy as np

PT = 4.18                                   # PDF points per metre
XC = 12.83                                  # hall centre line (OperaRIR x)
Y_SHIFT = 0.8                               # model Y = OperaRIR y - Y_SHIFT
SRC_H = 1.6                                 # loudspeaker height above the stage (Alary & Politis 2023)
EAR = 1.2


def plan_xy(xp, yp):
    """Plan drawing (pt) -> model (X, Y)."""
    return XC + (yp - 170.0) / PT, (204.5 - xp) / PT


# outline of the stalls (dark line of the plan), upper half from the proscenium to the back on the centre line
HALF = [(204.5, 137), (190, 137), (178, 136), (178, 125), (165, 125), (156, 124), (152, 119), (145, 123),
        (141, 118), (134, 125), (127, 121), (120, 126), (117, 124), (113, 131), (106, 130), (100, 138), (95, 152)]
BACK_X = 93.0
# front line of the balconies (light arc of the plan)
ARC = [(106, 170), (110, 150), (120, 140), (135, 134), (150, 131), (165, 133), (172, 137)]
BALC = [(2.75, 4.4), (6.3, 7.8), (9.9, 11.4)]           # (underside, parapet top) z of the three tiers (section)
Y_BALC_END = 7.8                                         # balconies end towards the stage here

FLOOR = [(0.0, -0.84), (8.6, -0.84), (27.3, 1.08)]       # stalls floor z(Y) (section)
CEIL = [(0.0, 12.6), (7.4, 13.8), (13.4, 14.5), (15.8, 15.9), (25.8, 16.3), (27.5, 17.0)]
OPEN_W, OPEN_H, WALL_T = 14.6, 11.0, 0.6
STAGE_X = (1.59, 27.19)                                   # plan y 123 ... 230 pt
STAGE_Y = (-WALL_T, -19.7)
STAGE_H = 26.0


def outline():
    up = [plan_xy(*p) for p in HALF] + [plan_xy(BACK_X, 170.0)]
    lo = [(2 * XC - x, y) for x, y in up[-2::-1]]
    return up + lo


def zf(y):
    return float(np.interp(y, *zip(*FLOOR)))


def zc(y):
    return float(np.interp(y, *zip(*CEIL)))


def arc_circle():
    """Least-squares circle (centre on the centre line, radius) through the balcony front points."""
    P = np.array([plan_xy(*p) for p in ARC])
    A = np.c_[2 * P[:, 1], np.ones(len(P))]                     # centre on the centre line X = XC
    b = ((P - [XC, 0]) ** 2).sum(1)
    cy, k = np.linalg.lstsq(A, b, rcond=None)[0]
    return (XC, cy), float(np.sqrt(k + cy ** 2))


class Mesh:
    def __init__(self):
        self.v, self.f = [], []

    def face(self, pts, g):
        pts = [tuple(map(float, p)) for p in pts]
        if len(pts) < 3:
            return
        i0 = len(self.v)
        self.v += pts
        self.f.append((g, list(range(i0 + 1, i0 + 1 + len(pts)))))

    def text(self):
        out = ["# Finnish National Opera, main auditorium (validation/opera_model.py); z up, metres"]
        out += [f"v {x:.4f} {y:.4f} {z:.4f}" for x, y, z in self.v]
        for g, idx in sorted(self.f, key=lambda t: t[0]):
            out += [f"g {g}", "f " + " ".join(map(str, idx))]
        return "\n".join(out) + "\n"


def triangulate(poly):
    """shapely Polygon -> list of triangles [(x, y)] * 3 (earcut, holes allowed)."""
    import mapbox_earcut as ec
    rings = [np.asarray(poly.exterior.coords)[:-1]] + [np.asarray(r.coords)[:-1] for r in poly.interiors]
    V = np.vstack(rings)
    ends = np.cumsum([len(r) for r in rings]).astype(np.uint32)
    t = ec.triangulate_float64(V, ends).reshape(-1, 3)
    return [V[i] for i in t]


def bands(poly, breaks):
    """Pieces of poly between consecutive Y breaks (floor and ceiling are planar in each)."""
    from shapely.geometry import box
    x0, y0, x1, y1 = poly.bounds
    ys = [y0 - 1] + [b for b in breaks if y0 < b < y1] + [y1 + 1]
    out = []
    for a, b in zip(ys[:-1], ys[1:]):
        g = poly.intersection(box(x0 - 1, a, x1 + 1, b))
        out += list(getattr(g, "geoms", [g]))
    return [g for g in out if g.geom_type == "Polygon" and g.area > 1e-6]


def split_edges(pts, breaks):
    """Closed polyline with vertices inserted where it crosses a Y break."""
    out = []
    n = len(pts)
    for i in range(n):
        (xa, ya), (xb, yb) = pts[i], pts[(i + 1) % n]
        out.append((xa, ya))
        cross = sorted([b for b in breaks if min(ya, yb) < b < max(ya, yb)], reverse=yb < ya)
        for b in cross:
            t = (b - ya) / (yb - ya)
            out.append((xa + t * (xb - xa), b))
    return out


def build():
    from shapely.geometry import Polygon, Point
    m = Mesh()
    P = outline()
    brk = sorted({y for y, _ in FLOOR} | {y for y, _ in CEIL})
    poly = Polygon(P)
    # floor and ceiling of the auditorium
    for piece in bands(poly, brk):
        for tri in triangulate(piece):
            m.face([(x, y, zf(y)) for x, y in tri], "aud")
            m.face([(x, y, zc(y)) for x, y in tri[::-1]], "ceiling")
    # outer walls (vertical, so each sub-edge is planar), proscenium line Y = 0 handled below
    Q = split_edges(P, brk)
    for i in range(len(Q)):
        (xa, ya), (xb, yb) = Q[i], Q[(i + 1) % len(Q)]
        if abs(ya) < 1e-9 and abs(yb) < 1e-9:
            continue
        m.face([(xa, ya, zf(ya)), (xb, yb, zf(yb)), (xb, yb, zc(yb)), (xa, ya, zc(ya))], "wall")
    # proscenium wall at Y = 0 with the opening, and the portal (wall thickness) into the stage house
    xl, xr = min(x for x, y in P if abs(y) < 1e-9), max(x for x, y in P if abs(y) < 1e-9)
    ol, orr = XC - OPEN_W / 2, XC + OPEN_W / 2
    z0, zt = zf(0.0), zc(0.0)
    m.face([(xl, 0, z0), (ol, 0, z0), (ol, 0, zt), (xl, 0, zt)], "wall")
    m.face([(orr, 0, z0), (xr, 0, z0), (xr, 0, zt), (orr, 0, zt)], "wall")
    m.face([(ol, 0, OPEN_H), (orr, 0, OPEN_H), (orr, 0, zt), (ol, 0, zt)], "wall")
    m.face([(ol, 0, z0), (orr, 0, z0), (orr, 0, 0.0), (ol, 0, 0.0)], "wall")          # stage front
    yb = -WALL_T
    m.face([(ol, 0, 0), (ol, yb, 0), (orr, yb, 0), (orr, 0, 0)], "stage")              # floor of the portal
    m.face([(ol, 0, 0), (ol, 0, OPEN_H), (ol, yb, OPEN_H), (ol, yb, 0)], "wall")
    m.face([(orr, 0, 0), (orr, yb, 0), (orr, yb, OPEN_H), (orr, 0, OPEN_H)], "wall")
    m.face([(ol, 0, OPEN_H), (orr, 0, OPEN_H), (orr, yb, OPEN_H), (ol, yb, OPEN_H)], "wall")
    # stage house
    sx0, sx1 = STAGE_X
    sy0, sy1 = STAGE_Y
    m.face([(sx0, sy0, 0), (sx1, sy0, 0), (sx1, sy1, 0), (sx0, sy1, 0)], "stage")
    m.face([(sx0, sy0, STAGE_H), (sx0, sy1, STAGE_H), (sx1, sy1, STAGE_H), (sx1, sy0, STAGE_H)], "stage")
    m.face([(sx0, sy1, 0), (sx1, sy1, 0), (sx1, sy1, STAGE_H), (sx0, sy1, STAGE_H)], "stage")
    m.face([(sx0, sy0, 0), (sx0, sy1, 0), (sx0, sy1, STAGE_H), (sx0, sy0, STAGE_H)], "stage")
    m.face([(sx1, sy0, 0), (sx1, sy0, STAGE_H), (sx1, sy1, STAGE_H), (sx1, sy1, 0)], "stage")
    m.face([(sx0, sy0, 0), (ol, sy0, 0), (ol, sy0, STAGE_H), (sx0, sy0, STAGE_H)], "stage")
    m.face([(orr, sy0, 0), (sx1, sy0, 0), (sx1, sy0, STAGE_H), (orr, sy0, STAGE_H)], "stage")
    m.face([(ol, sy0, OPEN_H), (orr, sy0, OPEN_H), (orr, sy0, STAGE_H), (ol, sy0, STAGE_H)], "stage")
    # balconies: solid rings between the outline and the front circle, for Y > Y_BALC_END
    from shapely.geometry import box
    (cx, cy), r = arc_circle()
    ring = poly.difference(Point(cx, cy).buffer(r, 12)).intersection(box(-50, Y_BALC_END, 80, 80))
    parts = [g for g in getattr(ring, "geoms", [ring]) if g.geom_type == "Polygon" and g.area > 0.5]
    for zu, zt_ in BALC:
        for g in parts:
            for tri in triangulate(g):
                m.face([(x, y, zt_) for x, y in tri], "aud")
                m.face([(x, y, zu) for x, y in tri[::-1]], "soffit")
            c = list(g.exterior.coords)[:-1]
            for i in range(len(c)):
                (xa, ya), (xb, yb_) = c[i], c[(i + 1) % len(c)]
                mid = Point((xa + xb) / 2, (ya + yb_) / 2)
                if poly.exterior.distance(mid) < 1e-3:
                    continue                                 # against the outer wall
                m.face([(xa, ya, zu), (xb, yb_, zu), (xb, yb_, zt_), (xa, ya, zt_)], "front")
    return m.text()


def receivers(layout_mat):
    """OperaRIR seats -> {"R<row>S<seat>": [X, Y, z]} (ear height above the stalls floor)."""
    from matio import load_from_mat
    d = load_from_mat(layout_mat)["SeatLayout"]
    out = {}
    for _, r in d.iterrows():
        y = float(r["y"]) - Y_SHIFT
        out[f"Row{int(r['row'])}_Seat{int(r['seat'])}"] = [round(float(r["x"]), 3), round(y, 3), round(zf(y) + EAR, 3)]
    return out


def sources(layout_mat):
    from matio import load_from_mat
    S = load_from_mat(layout_mat)["Sources"]
    return {f"Source{i + 1}": [round(float(np.asarray(s[0]).ravel()[0]), 3), -Y_SHIFT, SRC_H]
            for i, s in enumerate(np.asarray(S).ravel())}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "out", "opera", "opera.obj"))
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    t = build()
    open(a.out, "w").write(t)
    (cx, cy), r = arc_circle()
    print(f"balcony front circle centre ({cx:.2f}, {cy:.2f}) m, radius {r:.2f} m")
    print("faces", t.count("\nf "), "written", a.out)


if __name__ == "__main__":
    main()
