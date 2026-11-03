"""
2.5D hall geometry for AuralPaths (Python port of engine_geom.js `build`).

A hall is a plan outline polygon (x, y) plus floor and ceiling profiles z(y):
    room = {(x, y, z) : (x, y) inside outline, floor(y) <= z <= ceiling(y)}
Equal consecutive y values in a profile make a vertical step (riser).

Surfaces are planar polygons with an inward normal and a material group
("aud", "stage", "wall", "ceil"). `pra_walls` returns pyroomacoustics walls; pyroomacoustics
derives the normal from the vertex order and expects it to point OUT of the room, so the
vertex order is set from the inward normal accordingly (checked: identical image lists to the
browser engine on a non-convex raked fan hall).
"""
from __future__ import annotations

import numpy as np

GROUPS = ("aud", "stage", "wall", "ceil")


def _area2(poly):
    a = 0.0
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        a += x1 * y2 - x2 * y1
    return a / 2


def _ccw(poly):
    return poly[::-1] if _area2(poly) < 0 else list(poly)


def norm_profile(pts, y0, y1):
    p = sorted([(float(a), float(b)) for a, b in pts], key=lambda q: q[0])
    if not p:
        return None
    if p[0][0] > y0 + 1e-6:
        p.insert(0, (y0, p[0][1]))
    if p[-1][0] < y1 - 1e-6:
        p.append((y1, p[-1][1]))
    out = []
    for i, (y, z) in enumerate(p):
        if y < y0 - 1e-9:
            n = p[i + 1] if i + 1 < len(p) else None
            if n and n[0] > y0:
                out.append((y0, z + (n[1] - z) * (y0 - y) / (n[0] - y)))
            continue
        if y > y1 + 1e-9:
            q = p[i - 1] if i > 0 else None
            if q and q[0] < y1 and (not out or out[-1][0] < y1 - 1e-9):
                out.append((y1, q[1] + (z - q[1]) * (y1 - q[0]) / (y - q[0])))
            break
        out.append((y, z))
    out = [list(q) for q in out]
    for i in range(1, len(out)):
        if abs(out[i][0] - out[i - 1][0]) < 1e-6:
            out[i][0] = out[i - 1][0]
    return out


def prof_at(p, y, side=1):
    if y <= p[0][0]:
        return p[0][1]
    if y >= p[-1][0]:
        return p[-1][1]
    if side > 0:
        for i in range(len(p) - 1, -1, -1):
            if p[i][0] <= y:
                n = p[i + 1] if i + 1 < len(p) else None
                if n is None or n[0] == p[i][0]:
                    return p[i][1]
                return p[i][1] + (n[1] - p[i][1]) * (y - p[i][0]) / (n[0] - p[i][0])
    else:
        for i in range(len(p)):
            if p[i][0] >= y:
                q = p[i - 1] if i > 0 else None
                if q is None or q[0] == p[i][0]:
                    return p[i][1]
                return q[1] + (p[i][1] - q[1]) * (y - q[0]) / (p[i][0] - q[0])
    return p[-1][1]


def _clip_half(poly, keep):
    out = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        fa, fb = keep(a), keep(b)
        if fa >= 0:
            out.append(a)
        if (fa >= 0) != (fb >= 0):
            t = fa / (fa - fb)
            out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
    return out


def _strip(poly, y0, y1):
    return _clip_half(_clip_half(poly, lambda p: p[1] - y0), lambda p: y1 - p[1])


def _line_cross_x(poly, y):
    xs = []
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 <= y < y2) or (y2 <= y < y1):
            xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
    xs.sort()
    return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]


def build(geom, stage_y):
    """Return dict with surfaces [{verts (N,3), n (3,), mat, kind}], profiles and volume."""
    plan = _ccw([tuple(map(float, p)) for p in geom["plan"]])
    ys = [p[1] for p in plan]
    y0, y1 = min(ys), max(ys)
    floor = norm_profile(geom.get("floor") or [[y0, 0.0]], y0, y1)
    ceil = norm_profile(geom.get("ceiling") or [[y0, 8.0]], y0, y1)
    if y0 < stage_y < y1 and not any(abs(p[0] - stage_y) < 1e-9 for p in floor):
        z = prof_at(floor, stage_y)
        i = next(k for k, p in enumerate(floor) if p[0] > stage_y)
        floor.insert(i, [stage_y, z])
    S = []

    def horiz(prof, up, mat_of, kind):
        for i in range(len(prof) - 1):
            (ya, za), (yb, zb) = prof[i], prof[i + 1]
            if yb - ya < 1e-9:
                if abs(zb - za) < 1e-9:
                    continue
                for xa, xb in _line_cross_x(plan, ya + 1e-9):
                    lo, hi = min(za, zb), max(za, zb)
                    ny = (1 if za > zb else -1) if up else (1 if za < zb else -1)
                    v = [[xa, ya, lo], [xb, ya, lo], [xb, ya, hi], [xa, ya, hi]]
                    S.append(dict(verts=np.array(v), n=np.array([0.0, ny, 0.0]), mat=mat_of(ya + (1e-6 if ny > 0 else -1e-6)),
                                  kind="riser" if up else "ceil-step"))
                continue
            poly = _strip(plan, ya, yb)
            if len(poly) < 3 or abs(_area2(poly)) < 1e-9:
                continue
            slope = (zb - za) / (yb - ya)
            v = [[x, y, za + slope * (y - ya)] for x, y in poly]
            n = np.array([0.0, -slope, 1.0]) if up else np.array([0.0, slope, -1.0])
            S.append(dict(verts=np.array(v), n=n / np.linalg.norm(n), mat=mat_of((ya + yb) / 2), kind=kind))

    horiz(floor, True, lambda y: "stage" if y >= stage_y - 1e-9 else "aud", "floor")
    horiz(ceil, False, lambda y: "ceil", "ceil")
    for i in range(len(plan)):
        p, q = plan[i], plan[(i + 1) % len(plan)]
        dx, dy = q[0] - p[0], q[1] - p[1]
        if np.hypot(dx, dy) < 1e-9:
            continue
        # breakpoints carry the profile's exact y (y recomputed from t can land a hair off a riser)
        ts = [(0.0, p[1]), (1.0, q[1])]
        if abs(dy) > 1e-12:
            for y, _ in floor + ceil:
                t = (y - p[1]) / dy
                if 1e-9 < t < 1 - 1e-9:
                    ts.append((t, y))
        ts.sort()
        ts = [e for j, e in enumerate(ts) if j == 0 or e[0] - ts[j - 1][0] > 1e-9]   # a riser lists its y twice
        side_in, side_out = (-1, 1) if dy >= 0 else (1, -1)
        bottom, top = [], []
        for k, (t, y) in enumerate(ts):
            x = p[0] + dx * t
            if abs(dy) < 1e-12:
                bottom.append([x, y, prof_at(floor, y)])
                top.append([x, y, prof_at(ceil, y)])
                continue
            f_in, f_out = prof_at(floor, y, side_in), prof_at(floor, y, side_out)
            c_in, c_out = prof_at(ceil, y, side_in), prof_at(ceil, y, side_out)
            if k > 0:
                bottom.append([x, y, f_in])
            if (k < len(ts) - 1 and abs(f_out - f_in) > 1e-9) or k == 0:
                bottom.append([x, y, f_out])
            if k > 0:
                top.append([x, y, c_in])
            if (k < len(ts) - 1 and abs(c_out - c_in) > 1e-9) or k == 0:
                top.append([x, y, c_out])
        v = bottom + top[::-1]
        v = [a for j, a in enumerate(v) if j == 0 or np.linalg.norm(np.subtract(a, v[j - 1])) > 1e-9]
        if len(v) < 3:
            continue
        n = np.array([-dy, dx, 0.0])
        S.append(dict(verts=np.array(v), n=n / np.linalg.norm(n), mat="wall", kind="wall"))
    return dict(S=S, plan=plan, floor=floor, ceil=ceil, y0=y0, y1=y1)


def inside(G, p):
    x, y, z = p
    c = False
    pl = G["plan"]
    j = len(pl) - 1
    for i in range(len(pl)):
        xi, yi = pl[i]
        xj, yj = pl[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c and prof_at(G["floor"], y) + 1e-6 < z < prof_at(G["ceil"], y) - 1e-6


def _newell(v):
    n = np.zeros(3)
    for i in range(len(v)):
        a, b = v[i], v[(i + 1) % len(v)]
        n += [(a[1] - b[1]) * (a[2] + b[2]), (a[2] - b[2]) * (a[0] + b[0]), (a[0] - b[0]) * (a[1] + b[1])]
    return n


def pra_walls(G, materials, n_bands, band_centres):
    """pyroomacoustics walls; materials[group] = {"alpha": [...6 octave bands from 125 Hz], "s": scattering}."""
    import pyroomacoustics as pra
    walls = []
    for s in G["S"]:
        v = s["verts"]
        if np.dot(_newell(v), s["n"]) > 0:      # make the winding normal point outward
            v = v[::-1]
        m = materials[s["mat"]]
        a = list(m["alpha"])
        a8 = [a[i] if i < len(a) else a[-1] for i in range(n_bands)]
        walls.append(pra.wall_factory(np.ascontiguousarray(v.T), a8, [m.get("s", 0.0)] * n_bands, name=s["mat"]))
    return walls
