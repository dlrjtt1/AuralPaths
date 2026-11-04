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


def build(geom, stage_y, seed=None):
    """Return dict with surfaces [{verts (N,3), n (3,), mat, kind}], profiles and volume.
    A "mesh" entry selects an OBJ hall (build_mesh); `seed` is then a point inside the room."""
    if "mesh" in geom:
        return build_mesh(geom, seed)
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
    if G.get("mesh"):
        return mesh_inside(G, p)
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


# ---------------------------------------------------------------- 3D mesh halls (Wavefront OBJ)
"""
A hall can also be given as a triangle / polygon mesh (Python engine only; the browser engine stays 2.5D):

    "geometry": {"mesh": {"obj": "path/to/hall.obj", "axes": "y-up",
                          "groups": {"<OBJ group or material name>": "<material key>", ...},
                          "default": "<material key for unmatched faces>"},
                 "materials": {"<material key>": {"alpha": [...6 octave bands 125 Hz - 4 kHz...], "s": 0.1}, ...},
                 "ism_order": 1, "rays": 50000}

A group value may also be {"wall": key, "ceiling": key, "floor": key}: faces of that group are then split by their
inward normal (n_z < -0.3 ceiling, > 0.3 floor, otherwise wall), for a tag that holds walls and vaults together.
Group names are matched as case-insensitive substrings of the OBJ "g" / "o" / "usemtl" names (the SketchUp ->
Blender path writes the SketchUp tag into the group name, e.g. "_(Loose_Entity).004__(Loose_Entity)_Seats").
"axes": "y-up" (Blender / SketchUp OBJ default) maps OBJ (x, y, z) to AuralPaths (x, -z, y); "z-up" keeps them.

Mesh faces carry no reliable winding, and pyroomacoustics needs every wall normal to point out of the room (the
image-source side test and the ray-tracing reflection both use it; a flipped shoebox loses 6 of 7 first-order
images). The interior is therefore found by voxel flood fill from a point known to be inside (a source): faces
are rasterised into a voxel grid (spacing `voxel`, default 5 cm, closed by one voxel of dilation so that gaps
below ~10 cm do not leak), the free voxels connected to the seed are the room, and each face's inward normal is
the side whose offset points (2.5 voxels, spread over the face at 0.2 m) fall in the room. Faces with the room
on neither side (outer skins of thick walls, hidden faces) are dropped; a face with the room on both sides (a
free-standing panel or suspended reflector) is kept twice, once per side, 2 mm apart. The voxel set also gives
the room volume (interior voxels + half of the surface band next to them).
"""


def load_obj(path):
    """Return (V [n,3], faces [list of index lists], names [per face: 'g|o|usemtl' joined])."""
    V, F, names = [], [], []
    g, o, m = [], "", ""
    after_face = False
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.startswith("v "):
                V.append([float(x) for x in line.split()[1:4]])
            elif line.startswith("f "):
                idx = []
                for tok in line.split()[1:]:
                    i = int(tok.split("/")[0])
                    idx.append(i - 1 if i > 0 else len(V) + i)
                if len(idx) >= 3:
                    F.append(idx)
                    names.append(f"{'|'.join(g)}|{o}|{m}")
                after_face = True
            elif line.startswith("g "):
                # Blender writes "g <object>_<mesh>" then "g <object>_<material>" with no faces in between; keep
                # every group name since the last face so that the mesh name (the SketchUp tag) is not lost
                g = [line[2:].strip()] if after_face else g + [line[2:].strip()]
                after_face = False
            elif line.startswith("o "):
                o = line[2:].strip()
            elif line.startswith("usemtl "):
                m = line[7:].strip()
    return np.asarray(V, float), F, names


def _mesh_axes(V, axes):
    if axes == "z-up":
        return V.copy()
    return np.c_[V[:, 0], -V[:, 2], V[:, 1]]          # y-up OBJ -> x right, y depth, z up


def _tri_fan(F):
    tri, owner = [], []
    for k, f in enumerate(F):
        for i in range(1, len(f) - 1):
            tri.append((f[0], f[i], f[i + 1]))
            owner.append(k)
    return np.asarray(tri, int), np.asarray(owner, int)


def _sample_tris(V, T, h):
    """Points on every triangle with spacing <= h (vertices, edges and interior)."""
    pts = [V[np.unique(T)]]
    a, b, c = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    L = np.maximum.reduce([np.linalg.norm(b - a, axis=1), np.linalg.norm(c - a, axis=1), np.linalg.norm(c - b, axis=1)])
    n = np.maximum(1, np.ceil(L / h).astype(int))
    for k in np.unique(n):
        sel = n == k
        i, j = np.meshgrid(np.arange(k + 1), np.arange(k + 1), indexing="ij")
        m = (i + j) <= k
        u, w = (i[m] / k)[None, :, None], (j[m] / k)[None, :, None]
        A, B, C = a[sel][:, None], b[sel][:, None], c[sel][:, None]
        pts.append((A + u * (B - A) + w * (C - A)).reshape(-1, 3))
    return np.vstack(pts)


def _newell_np(P):
    return np.array([np.sum((P[:, 1] - np.roll(P[:, 1], -1)) * (P[:, 2] + np.roll(P[:, 2], -1))),
                     np.sum((P[:, 2] - np.roll(P[:, 2], -1)) * (P[:, 0] + np.roll(P[:, 0], -1))),
                     np.sum((P[:, 0] - np.roll(P[:, 0], -1)) * (P[:, 1] + np.roll(P[:, 1], -1)))])


def voxel_room(V, T, seed, h=0.05, dilate=1):
    """Flood-fill the free space connected to `seed`. Returns dict(origin, h, inside [bool grid], volume)."""
    from scipy import ndimage
    lo, hi = V.min(0) - 3 * h, V.max(0) + 3 * h
    shape = tuple(np.ceil((hi - lo) / h).astype(int) + 1)
    solid = np.zeros(shape, bool)
    P = _sample_tris(V, T, h / 2)
    ijk = np.floor((P - lo) / h).astype(int)
    solid[ijk[:, 0], ijk[:, 1], ijk[:, 2]] = True
    if dilate:
        solid = ndimage.binary_dilation(solid, iterations=dilate)
    lab, _ = ndimage.label(~solid)
    s = tuple(np.floor((np.asarray(seed, float) - lo) / h).astype(int))
    if solid[s]:
        raise ValueError(f"mesh seed {seed} lies in the surface band; move it away from surfaces")
    room = lab == lab[s]
    if room[0, 0, 0]:
        raise ValueError("the mesh is not closed: the room leaks to the outside (gap wider than the voxel band)")
    vol = float(room.sum() + 0.5 * (ndimage.binary_dilation(room) & solid).sum()) * h ** 3
    return dict(origin=lo, h=h, inside=room, volume=vol)


def _in_room(vr, P):
    ijk = np.floor((P - vr["origin"]) / vr["h"]).astype(int)
    sh = np.array(vr["inside"].shape)
    ok = np.all((ijk >= 0) & (ijk < sh), axis=1)
    out = np.zeros(len(P), bool)
    out[ok] = vr["inside"][ijk[ok, 0], ijk[ok, 1], ijk[ok, 2]]
    return out


def build_mesh(geom, seed):
    """Surfaces of an OBJ hall with inward normals and material keys (same dict layout as build)."""
    spec = geom["mesh"]
    V, F, names = load_obj(spec["obj"])
    V = _mesh_axes(V, spec.get("axes", "y-up"))
    groups = {k.lower(): v for k, v in spec.get("groups", {}).items()}
    default = spec.get("default")
    n_in = len(F)
    if spec.get("max_faces") and len(F) > int(spec["max_faces"]):
        V, F, names = simplify_mesh(V, F, names, int(spec["max_faces"]))
    T, owner = _tri_fan(F)
    h = float(spec.get("voxel", 0.05))
    vr = voxel_room(V, T, seed, h)
    off = 2.5 * h                                       # beyond the dilated surface band (1.5 h half-width)
    two_sided = bool(spec.get("two_sided", True))
    inflate = float(spec.get("inflate_mm", 1.0)) / 1000
    S, dropped, unmatched = [], 0, set()
    for k, f in enumerate(F):
        P = V[f]
        n = _newell_np(P)
        A = np.linalg.norm(n) / 2
        if A < 1e-6:
            continue
        n = n / (2 * A)
        tri = T[owner == k]
        # test points spread over the face (spacing 0.2 m, at least the triangle centroids): a face partly covered by
        # another solid (a wall behind a seat block) still has room on its exposed part
        C = np.vstack([V[tri].mean(1), _sample_tris(V, tri, 0.2)])
        fwd, bwd = _in_room(vr, C + off * n).sum(), _in_room(vr, C - off * n).sum()
        if fwd == 0 and bwd == 0:
            dropped += 1
            continue
        both = min(fwd, bwd) > 0.2 * max(fwd, bwd)         # room on both sides (free-standing panel, reflector)
        nn = n if fwd >= bwd else -n
        key = next((v for g, v in groups.items() if g in names[k].lower()), default)
        if isinstance(key, dict):                           # split one OBJ group by orientation of the inward normal
            key = key.get("ceiling" if nn[2] < -0.3 else "floor" if nn[2] > 0.3 else "wall", key.get("default"))
        if key is None:
            unmatched.add(names[k])
            continue
        if inflate > 0:
            P = _inflate(P, nn, inflate)
        S.append(dict(verts=P, n=nn, mat=key, kind="mesh", area=A))
        if both or two_sided:
            # a pyroomacoustics wall is one-sided (the image test and the scattering hemisphere use its normal), so a
            # face with room on both sides gets a twin facing the other way, 2 mm behind it. With two_sided (default)
            # every face gets one: a ray that ends up behind a face (in a slot thinner than the voxel test, inside
            # a solid through a crack) is then reflected instead of being scattered through it or lost
            S.append(dict(verts=P - 0.002 * nn, n=-nn, mat=key, kind="mesh-twin", area=A))
    if unmatched:
        raise ValueError("mesh faces without a material (add them to mesh.groups or set mesh.default): "
                         + "; ".join(sorted(unmatched)[:8]))
    return dict(S=S, mesh=True, volume=vr["volume"], voxel=vr, n_dropped=dropped, n_input=n_in, n_faces=len(F),
                area={k: sum(x["area"] for x in S if x["mat"] == k and x["kind"] == "mesh") for k in {x["mat"] for x in S}},
                bbox=(V.min(0), V.max(0)))


def simplify_mesh(V, F, names, max_faces):
    """Quadric decimation of the whole mesh (fast-simplification, MIT licence; optional dependency) to about
    max_faces triangles. Vertices are welded first so that the decimation keeps the surfaces connected; each new
    triangle takes the group name of the nearest original triangle (centroid distance)."""
    import fast_simplification
    from scipy.spatial import cKDTree
    T, owner = _tri_fan(F)
    W, inv = np.unique(np.round(V, 4), axis=0, return_inverse=True)
    Tw = inv.ravel()[T]
    keep = (Tw[:, 0] != Tw[:, 1]) & (Tw[:, 1] != Tw[:, 2]) & (Tw[:, 0] != Tw[:, 2])
    Tw, owner = Tw[keep], owner[keep]
    red = max(0.0, min(0.99, 1 - max_faces / len(Tw)))
    V2, T2 = fast_simplification.simplify(W.astype(np.float32), Tw.astype(np.int32), target_reduction=red)
    V2 = np.asarray(V2, float)
    tree = cKDTree(W[Tw].mean(1))
    _, near = tree.query(V2[T2].mean(1))
    return V2, [list(t) for t in T2], [names[owner[i]] for i in near]


def _inflate(P, n, e):
    """Move every edge of a planar convex polygon outward by e (in its plane). pyroomacoustics intersects rays with
    walls in single precision; on a tessellated surface a ray through a shared edge can miss both neighbours and
    is then dropped. A 1 mm overlap closes those cracks."""
    k = len(P)
    lines = []
    for i in range(k):
        a, b = P[i], P[(i + 1) % k]
        t = b - a
        t = t / (np.linalg.norm(t) + 1e-12)
        out = np.cross(t, n)                          # in-plane, pointing away from the polygon for CCW about n
        if np.dot(out, P.mean(0) - a) > 0:
            out = -out
        lines.append((a + e * out, t))
    Q = []
    for i in range(k):
        (a1, t1), (a2, t2) = lines[i - 1], lines[i]
        # intersection of the two offset edge lines (least squares, they are coplanar)
        M = np.c_[t1, -t2]
        x, *_ = np.linalg.lstsq(M, a2 - a1, rcond=None)
        q = a1 + x[0] * t1
        if np.linalg.norm(q - P[i]) > 20 * e:        # sliver angle: fall back to a radial push
            d = P[i] - P.mean(0)
            q = P[i] + e * d / (np.linalg.norm(d) + 1e-12)
        Q.append(q)
    return np.asarray(Q)


def mesh_inside(G, p):
    return bool(_in_room(G["voxel"], np.asarray(p, float)[None])[0])
