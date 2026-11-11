"""
Simplified 3-D model of the Auditorium Giovanni Arvedi (Museo del Violino, Cremona) for the blind check of
validation/arvedi_protocol.md. Writes a Wavefront OBJ (z up, metres) and prints its volume and surface areas.

    python validation/arvedi_model.py [--out out/arvedi/arvedi.obj]

Read off the published drawings (ARKPABI, on ArchDaily: https://www.archdaily.com/870937; plans of three levels,
longitudinal and transverse sections with 0-5 m scale bars) and checked against the published dimensions
(Arketipo: room 14 x 35 m, up to 14 m high above the stage, volume 5300 m3, oval stage 8.40 x 9.96 m;
https://www.arketipomagazine.it/auditorium-giovanni-arvedi-del-museo-del-violino-di-cremona-studio-arkpabi-e-nagata-acoustics/).
Read to about +-0.3 m; everything below is an engineering simplification, not survey data.

Frame: x along the hall (0 at the inner face of the end wall on the left of the plans, 35 m at the other end),
y across (0 to 14 m), z up from the stage floor. The longitudinal section is drawn mirrored to the plans (its high
seating end is the left lobe of the plans); its profile is taken over with x_plan = 35.7 - x_section, which puts the
stage centres of plan and section together.

Model:
- Box 35.0 x 14.0 m; flat ceiling at 13.4 m (the plaster between the beams undulates between about 12.6 and 14.0
  m) with six transverse beams 0.6 m wide down to 12.1 m.
- Perimeter walkway (oak parquet) at +3.8 m between the walls and the seating island.
- Seating island: one height profile along x (the rows are about straight across the hall): the high end rises to
  9.3 m at x = 3.2 m, the low end to 4.4 m at x = 34.6 m, the stage floor (z = 0) between x = 19.3 and 24.8 m; along
  the stage the ring rows rise to 1.6 m at the island edge. Step treads are not modelled (smooth rake); balcony
  overhangs, the "scroll" shell at the high end, aisles and stairs are not modelled; the island's vertical sides are
  wood shells.
- Long walls: seven tall windows each (2.4 x 7.5 m, sills at 4.4 m), the rest plaster; end walls plaster.

Result (geometry.build_mesh, 5 cm voxels): volume 4680 m3, 12 % below the published 5300 m3 (the model fills the
space under the raked seating and the balcony, and the ceiling is flat); areas: seating 339 m2, stage 44 m2,
walkway 154 m2, wood shells 207 m2, plaster walls 689 m2, windows 252 m2, ceiling with beams 709 m2.
"""
import argparse
import os

import numpy as np

L, W = 35.0, 14.0
ZG, ZC = 3.8, 13.4                      # walkway level, ceiling
BEAMS = [5.8, 10.6, 15.4, 20.2, 25.05, 29.95]
BEAM_W, BEAM_Z = 0.6, 12.1
WIN_X, WIN_W, WIN_Z = [2.6, 7.9, 12.6, 17.4, 22.2, 26.8, 32.0], 2.4, (4.4, 11.9)

# island outline y_low(x), y_high(x) (plan 1, middle level)
OUT_X = [1.6, 2.4, 3.4, 5.1, 8.4, 9.8, 11.0, 14.0, 15.5, 17.0, 19.3, 21.4, 24.8, 25.1, 27.0, 29.0, 32.6, 34.6]
OUT_LO = [5.5, 3.8, 2.6, 1.6, 1.5, 1.5, 1.95, 2.2, 2.3, 2.2, 2.0, 2.0, 2.5, 2.6, 2.1, 1.6, 1.7, 1.2]
OUT_HI = [8.5, 10.6, 12.1, 12.9, 12.9, 12.5, 12.3, 11.9, 11.9, 12.1, 12.3, 12.4, 12.0, 11.9, 12.2, 12.6, 12.1, 12.8]
# height profile along x (longitudinal section)
PROF_X = [1.6, 3.2, 11.2, 14.95, 16.2, 18.7, 19.3, 24.8, 25.7, 30.4, 34.6]
PROF_Z = [9.3, 9.3, 4.6, 2.75, 1.5, 0.4, 0.0, 0.0, 0.4, 2.4, 4.4]
STAGE_ZONE = (19.3, 24.8)               # stage floor between the ring rows
# post hoc (after the blind run, see validation/arvedi_protocol.md item 13): the ring rows in front of the high end
# follow the dataset's receiver heights (microphone 1.2 m above the floor: rows A1 - A5 on floors 0 ... 1.1 m at
# 3.3 ... 6.9 m from the stage centre), then the front of the high block (step to 2.75 m), then the rake as above
PROF_POSTHOC = ([1.6, 3.2, 11.2, 14.55, 14.75, 15.15, 16.05, 16.95, 17.85, 18.75, 19.3, 24.8, 25.7, 30.4, 34.6],
                [9.3, 9.3, 4.6, 2.75, 1.2, 1.1, 0.8, 0.5, 0.2, 0.0, 0.0, 0.0, 0.4, 2.4, 4.4])
RING = (3.0, 11.0, 1.6)                 # ring rows: from z 0 at y = 3 / 11 m up to 1.6 m at the island edge


def interp(x, X, Y):
    return float(np.interp(x, X, Y))


class Obj:
    def __init__(self):
        self.v, self.f = [], []

    def face(self, pts, mat):
        pts = [tuple(map(float, p)) for p in pts]
        n = np.cross(np.subtract(pts[1], pts[0]), np.subtract(pts[2], pts[0]))
        if np.linalg.norm(n) < 1e-9 and len(pts) == 3:
            return
        if len(pts) > 3:                     # a warped quad (ring rows) goes in as two triangles
            nn = n / (np.linalg.norm(n) or 1)
            if max(abs(np.dot(np.subtract(p, pts[0]), nn)) for p in pts) > 1e-6:
                for i in range(1, len(pts) - 1):
                    self.face([pts[0], pts[i], pts[i + 1]], mat)
                return
        i0 = len(self.v)
        self.v += pts
        self.f.append((mat, list(range(i0 + 1, i0 + 1 + len(pts)))))

    def write(self, path):
        with open(path, "w") as fh:
            fh.write("# Arvedi Auditorium, simplified (validation/arvedi_model.py); z up, metres\n")
            for p in self.v:
                fh.write(f"v {p[0]:.4f} {p[1]:.4f} {p[2]:.4f}\n")
            cur = None
            for mat, idx in self.f:
                if mat != cur:
                    fh.write(f"g {mat}\n")
                    cur = mat
                fh.write("f " + " ".join(map(str, idx)) + "\n")


def vside(o, xa, ya, xb, yb, za, zb, mat, split=None):
    """Vertical quad over the ground segment (xa, ya) - (xb, yb) from bottom za (pair) to top zb (pair); split: a
    height pair at which the face is cut in two (exposed and hidden parts as separate faces)."""
    za, zb = np.broadcast_to(za, 2), np.broadcast_to(zb, 2)
    cuts = [za]
    if split is not None:
        s = np.clip(np.broadcast_to(split, 2), za, zb)
        if np.any(s > za + 1e-6) and np.any(s < zb - 1e-6):
            cuts.append(s)
    cuts.append(zb)
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        if np.all(hi - lo < 1e-6):
            continue
        o.face([(xa, ya, lo[0]), (xb, yb, lo[1]), (xb, yb, hi[1]), (xa, ya, hi[0])], mat)


PARAPET = (14.6, 32.0, 0.25, 1.1)       # detail: parapets on the walkway edge between these x, thickness, height
LIP = (14.35, 14.6, 1.0)                # detail: lip on the front of the high block (x range, height above 2.75 m)
PIT = (15.0, 29.0)                      # detail: the pit walls under the walkway between these x are textured panels


def box_quad(o, quad, z0, z1, mat):
    """Closed prism over the ground quad (4 points, counter-clockwise) from z0 to z1."""
    q = [tuple(p) for p in quad]
    o.face([(x, y, z1) for x, y in q], mat)
    o.face([(x, y, z0) for x, y in q[::-1]], mat)
    for i in range(4):
        (xa, ya), (xb, yb) = q[i], q[(i + 1) % 4]
        o.face([(xa, ya, z0), (xb, yb, z0), (xb, yb, z1), (xa, ya, z1)], mat)


def build(posthoc=False, detail=False):
    """detail (post hoc, protocol item 15): parapets, front lip, textured pit walls as their own material."""
    global PROF_X, PROF_Z
    if posthoc:
        PROF_X, PROF_Z = PROF_POSTHOC
    o = Obj()
    xs = sorted(set(OUT_X + PROF_X + list(STAGE_ZONE)))
    xs = [x for x in xs if OUT_X[0] <= x <= OUT_X[-1]]
    lo = [interp(x, OUT_X, OUT_LO) for x in xs]
    hi = [interp(x, OUT_X, OUT_HI) for x in xs]
    zp = [interp(x, PROF_X, PROF_Z) for x in xs]
    y3, y11, zr = RING
    for i in range(len(xs) - 1):
        x0, x1 = xs[i], xs[i + 1]
        stage = STAGE_ZONE[0] - 1e-9 <= x0 and x1 <= STAGE_ZONE[1] + 1e-9
        # ---- island top
        if stage:
            o.face([(x0, y3, 0), (x1, y3, 0), (x1, y11, 0), (x0, y11, 0)], "stage")
            o.face([(x0, lo[i], zr), (x1, lo[i + 1], zr), (x1, y3, 0), (x0, y3, 0)], "aud")
            o.face([(x0, y11, 0), (x1, y11, 0), (x1, hi[i + 1], zr), (x0, hi[i], zr)], "aud")
            ztop = (np.array([zr, zr]), np.array([zr, zr]))
        else:
            o.face([(x0, lo[i], zp[i]), (x1, lo[i + 1], zp[i + 1]), (x1, hi[i + 1], zp[i + 1]), (x0, hi[i], zp[i])], "aud")
            ztop = (np.array([zp[i], zp[i + 1]]), np.array([zp[i], zp[i + 1]]))
        # ---- walkway strips (y < lo, y > hi) at ZG, and the vertical faces between walkway and island
        o.face([(x0, 0, ZG), (x1, 0, ZG), (x1, lo[i + 1], ZG), (x0, lo[i], ZG)], "floor")
        o.face([(x0, hi[i], ZG), (x1, hi[i + 1], ZG), (x1, W, ZG), (x0, W, ZG)], "floor")
        for (ya, yb), zt in (((lo[i], lo[i + 1]), ztop[0]), ((hi[i], hi[i + 1]), ztop[1])):
            # island side above the walkway, walkway side above the island: one vertical face from min to max
            mat = "pitwall" if detail and np.all(zt < ZG) and PIT[0] <= x0 and x1 <= PIT[1] else "shell"
            vside(o, x0, ya, x1, yb, np.minimum(zt, ZG), np.maximum(zt, ZG), mat)
        if detail and PARAPET[0] - 1e-9 <= x0 and x1 <= PARAPET[1] + 1e-9:
            t, hgt = PARAPET[2], PARAPET[3]
            box_quad(o, [(x0, lo[i] - t), (x1, lo[i + 1] - t), (x1, lo[i + 1]), (x0, lo[i])], ZG, ZG + hgt, "shell")
            box_quad(o, [(x0, hi[i]), (x1, hi[i + 1]), (x1, hi[i + 1] + t), (x0, hi[i] + t)], ZG, ZG + hgt, "shell")
    if detail:
        xa, xb, hgt = LIP
        za = interp(xa, PROF_X, PROF_Z)
        box_quad(o, [(xa, interp(xa, OUT_X, OUT_LO)), (xb, interp(xb, OUT_X, OUT_LO)), (xb, interp(xb, OUT_X, OUT_HI)),
                     (xa, interp(xa, OUT_X, OUT_HI))], za, za + hgt, "shell")
    # steps in the island top between the stage zone (ring rows) and the profile next to it
    for xb in STAGE_ZONE:
        lo_b, hi_b = interp(xb, OUT_X, OUT_LO), interp(xb, OUT_X, OUT_HI)
        zb = interp(xb, PROF_X, PROF_Z)
        # ring strips end at zr on the island edge, the profile at zb: two triangles closing the gap
        o.face([(xb, lo_b, zb), (xb, lo_b, zr), (xb, y3, 0)], "shell")
        o.face([(xb, hi_b, zb), (xb, y11, 0), (xb, hi_b, zr)], "shell")
    # ---- ends of the island and end walkways
    x0, x1 = xs[0], xs[-1]
    for xe, ze in ((x0, zp[0]), (x1, zp[-1])):
        lo_e, hi_e = interp(xe, OUT_X, OUT_LO), interp(xe, OUT_X, OUT_HI)
        vside(o, xe, lo_e, xe, hi_e, min(ze, ZG), max(ze, ZG), "shell")
    o.face([(0, 0, ZG), (x0, 0, ZG), (x0, W, ZG), (0, W, ZG)], "floor")
    o.face([(x1, 0, ZG), (L, 0, ZG), (L, W, ZG), (x1, W, ZG)], "floor")
    # ---- walls from the walkway up to the ceiling
    for y in (0.0, W):
        xa = 0.0
        for xc in WIN_X:
            wa, wb = xc - WIN_W / 2, xc + WIN_W / 2
            o.face([(xa, y, ZG), (wa, y, ZG), (wa, y, ZC), (xa, y, ZC)], "wall")
            o.face([(wa, y, ZG), (wb, y, ZG), (wb, y, WIN_Z[0]), (wa, y, WIN_Z[0])], "wall")
            o.face([(wa, y, WIN_Z[0]), (wb, y, WIN_Z[0]), (wb, y, WIN_Z[1]), (wa, y, WIN_Z[1])], "window")
            o.face([(wa, y, WIN_Z[1]), (wb, y, WIN_Z[1]), (wb, y, ZC), (wa, y, ZC)], "wall")
            xa = wb
        o.face([(xa, y, ZG), (L, y, ZG), (L, y, ZC), (xa, y, ZC)], "wall")
    for x in (0.0, L):
        o.face([(x, 0, ZG), (x, W, ZG), (x, W, ZC), (x, 0, ZC)], "wall")
    # ---- ceiling strips between the beams, and the beams
    xa = 0.0
    for xb in BEAMS:
        a, b = xb - BEAM_W / 2, xb + BEAM_W / 2
        o.face([(xa, 0, ZC), (a, 0, ZC), (a, W, ZC), (xa, W, ZC)], "ceiling")
        o.face([(a, 0, BEAM_Z), (b, 0, BEAM_Z), (b, W, BEAM_Z), (a, W, BEAM_Z)], "ceiling")
        o.face([(a, 0, BEAM_Z), (a, W, BEAM_Z), (a, W, ZC), (a, 0, ZC)], "ceiling")
        o.face([(b, 0, BEAM_Z), (b, W, BEAM_Z), (b, W, ZC), (b, 0, ZC)], "ceiling")
        # beam ends on the long walls close the box
        o.face([(a, 0, BEAM_Z), (b, 0, BEAM_Z), (b, 0, ZC), (a, 0, ZC)], "ceiling")
        o.face([(a, W, BEAM_Z), (b, W, BEAM_Z), (b, W, ZC), (a, W, ZC)], "ceiling")
        xa = b
    o.face([(xa, 0, ZC), (L, 0, ZC), (L, W, ZC), (xa, W, ZC)], "ceiling")
    return o


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out", "arvedi", "arvedi.obj"))
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    o = build()
    o.write(a.out)
    print(f"{a.out}: {len(o.v)} vertices, {len(o.f)} faces")


if __name__ == "__main__":
    main()
