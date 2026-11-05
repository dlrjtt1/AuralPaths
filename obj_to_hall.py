"""
Convert a 3D OBJ hall (geometry.build_mesh) into a drawn 2.5D hall (plan outline x floor / ceiling profiles) that
both engines can run, including the browser page (Load config...).

    python obj_to_hall.py mesh_config.json [--out hall_2p5d.json] [--depth-axis y] [--stage-end min]
                          [--stage-depth 0] [--slice 0.25] [--tol 0.08]

mesh_config.json is an AuralPaths configuration whose "geometry" has a "mesh" entry (see geometry.py); its sources
and receivers are converted to the 2.5D coordinates as well.

What the conversion keeps (and what it cannot keep):
  - plan outline: the outline of the room's voxels projected on the floor plan (largest contour, simplified with
    tolerance --tol);
  - floor(y) and ceiling(y): for each slice of --slice metres along the depth axis, floor(y) is the plan-area
    mean of the lowest room voxel in each column (so seat blocks count as raised floor), and ceiling(y) is set so
    that the slice volume is kept: ceiling(y) = floor(y) + V_slice / A_slice. The total room volume is therefore
    kept to within the voxel and slicing error, but a dome becomes a vault extruded across the width (the 2.5D
    model cannot hold a ceiling that varies across x) and balconies / overhangs are lost;
  - materials: mesh faces are sorted by their inward normal into the four 2.5D groups (n_z > 0.3 floor: "stage"
    on the stage side of --stage-depth, else "aud"; n_z < -0.3 "ceil"; others "wall"); each group gets the
    area-weighted mean scattering and, from its absorption area in the mesh A_g(f) = sum(alpha_i(f) S_i):
      --preserve eyring (default): alpha_g = 1 - exp(-A_g / S_g,2.5D), i.e. the 2.5D group's Eyring exponent
        -S_g ln(1 - alpha_g) equals the mesh group's Sabine absorption area. Reason: in the Fratoni ULH and STC
        checks the ray-traced T30 of the 3D meshes was close to Sabine (STC 1.47 s vs 1.43 s, ULH 1 kHz 1.94 vs
        1.95 s), while a simple 2.5D hall decays like Eyring (validation/check_rt_eyring.py);
      --preserve sabine: alpha_g = A_g / S_g,2.5D (absorption area kept; Sabine estimates agree);
      --preserve room-eyring: alpha_g = k A_g / S_g,2.5D with one k per band keeping the room's Eyring exponent.
    The 2.5D hall has less surface than the mesh (ULH 942 -> 622 m2), so with the same A its mean alpha is higher.
    ULH, T30 of the 2.5D hall vs the 3D mesh at 125 Hz - 4 kHz: eyring -0.14 ... -0.07 s, room-eyring -0.25 ...
    -0.14 s, sabine -0.28 ... -0.17 s (validation/fratoni_ULH_preserve.md). All alpha capped at 0.95. Where the
    absorption sits in the room is not kept.
Axes of the output follow the drawn-hall convention: x = width, y = depth with the stage at large y, z = up.
"""
import argparse
import json
import math
import os
import sys

import numpy as np

import geometry


def _dp(pts, tol):
    """Douglas-Peucker simplification of an open polyline."""
    pts = np.asarray(pts, float)
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    ab = b - a
    L = np.linalg.norm(ab)
    if L < 1e-12:
        d = np.linalg.norm(pts - a, axis=1)
    else:
        d = np.abs(np.cross(ab, pts - a)) / L
    i = int(np.argmax(d))
    if d[i] > tol:
        return np.vstack([_dp(pts[:i + 1], tol)[:-1], _dp(pts[i:], tol)])
    return np.vstack([a, b])


def _outline(mask, x0, y0, h, tol):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    m = np.pad(mask.astype(float), 1)
    cs = plt.contour(np.arange(-1, m.shape[1] - 1), np.arange(-1, m.shape[0] - 1), m, levels=[0.5])
    paths = cs.get_paths() if hasattr(cs, "get_paths") else [p for c in cs.collections for p in c.get_paths()]
    plt.close("all")
    # one Path can hold several closed pieces (separate rooms in the mask, holes around pillars): split it into its
    # sub-polygons and keep the largest. (Taking path.vertices as one polygon joins the pieces into a
    # self-intersecting outline; found on the BRAS CR4 auditorium.)
    polys = [np.asarray(q) for p in paths for q in p.to_polygons(closed_only=False) if len(q) >= 3]
    best = max(polys, key=lambda v: abs(np.sum(v[:-1, 0] * v[1:, 1] - v[1:, 0] * v[:-1, 1])))
    P = np.c_[x0 + (best[:, 0] + 0.5) * h, y0 + (best[:, 1] + 0.5) * h]   # columns = x, rows = y
    closed = np.vstack([P, P[:1]])
    Q = _dp(closed, tol)[:-1]
    return Q


def convert(cfg, depth_axis="y", stage_end="min", stage_depth=0.0, slice_m=0.25, tol=0.08, preserve="eyring"):
    """Return (2.5D config dict, report dict)."""
    import brir_proto as bp
    G = bp._geom(cfg)
    vr = G["voxel"]
    room, (ox, oy, oz), h = vr["inside"], vr["origin"], vr["h"]
    di = {"x": 0, "y": 1}[depth_axis]
    # put the depth axis on grid axis 1 (y) and the width on axis 0 (x)
    R = room if di == 1 else np.transpose(room, (1, 0, 2))
    w0, d0 = (ox, oy) if di == 1 else (oy, ox)
    nx, ny, nz = R.shape
    col = R.any(2)                                       # plan mask [x, depth]
    zi = np.arange(nz)
    lo = np.where(R, zi[None, None, :], nz).min(2)       # lowest room voxel per column
    zf = oz + lo * h
    # depth coordinate of the output: stage at large y
    dpos = d0 + (np.arange(ny) + 0.5) * h
    dmin, dmax = dpos[col.any(0)].min() - h / 2, dpos[col.any(0)].max() + h / 2
    to_y = (lambda d: dmax - d) if stage_end == "min" else (lambda d: d - dmin)
    ybins = np.arange(0.0, dmax - dmin + slice_m, slice_m)
    floor, ceil = [], []
    for k in range(len(ybins) - 1):
        ya, yb = ybins[k], ybins[k + 1]
        sel = np.flatnonzero((to_y(dpos) >= ya) & (to_y(dpos) < yb))
        if not sel.size:
            continue
        c = col[:, sel]
        if not c.any():
            continue
        A = c.sum() * h * h
        Vs = R[:, sel, :].sum() * h ** 3
        f = float(np.mean(zf[:, sel][c]))
        floor.append([(ya + yb) / 2, f])
        ceil.append([(ya + yb) / 2, f + Vs / A])
    yd = dmax - dmin
    floor = [[0.0, floor[0][1]]] + floor + [[yd, floor[-1][1]]]
    ceil = [[0.0, ceil[0][1]]] + ceil + [[yd, ceil[-1][1]]]
    floor = [list(map(float, p)) for p in _dp(np.array(floor), tol / 2)]
    ceil = [list(map(float, p)) for p in _dp(np.array(ceil), tol / 2)]
    # plan outline in (width, depth) -> (x, y_out)
    P = _outline(col.T, w0, d0, h, tol)                 # contour of mask[depth, width] -> (width, depth)
    plan = [[float(p[0]), float(to_y(p[1]))] for p in P]
    zshift = -min(z for _, z in floor)
    floor = [[y, z + zshift] for y, z in floor]
    ceil = [[y, z + zshift] for y, z in ceil]
    xmin = min(p[0] for p in plan)
    plan = [[x - xmin, y] for x, y in plan]

    def to25(p):
        p = np.asarray(p, float)
        w, d = (p[0], p[1]) if di == 1 else (p[1], p[0])
        return [float(w - xmin), float(to_y(d)), float(p[2] + zshift)]

    # materials: keep equivalent absorption area per group
    mats = cfg["geometry"]["materials"]
    nb = 6
    stage_y = yd - stage_depth
    acc = {g: [np.zeros(nb), 0.0, 0.0] for g in geometry.GROUPS}     # sum alpha*S, sum S, sum s*S
    for s in G["S"]:
        if s["kind"] != "mesh":
            continue
        nz_ = s["n"][2]
        c = s["verts"].mean(0)
        if nz_ > 0.3:
            g = "stage" if stage_depth > 0 and to25(c)[1] >= stage_y else "aud"
        elif nz_ < -0.3:
            g = "ceil"
        else:
            g = "wall"
        m = mats[s["mat"]]
        a = np.array([m["alpha"][i] if i < len(m["alpha"]) else m["alpha"][-1] for i in range(nb)], float)
        acc[g][0] += a * s["area"]
        acc[g][1] += s["area"]
        acc[g][2] += m.get("s", 0.0) * s["area"]
    geom25 = {"plan": plan, "floor": floor, "ceiling": ceil}
    dims = [max(p[0] for p in plan), yd, max(z for _, z in ceil)]
    G25 = geometry.build(dict(geom25), stage_y if stage_depth > 0 else yd + 1)
    S25 = {g: 0.0 for g in geometry.GROUPS}
    for s in G25["S"]:
        n = geometry._newell(s["verts"])
        S25[s["mat"]] += float(np.linalg.norm(n) / 2)
    out_m, report = {}, {"preserve": preserve, "groups": {}}
    used = [g for g in geometry.GROUPS if S25[g] > 0 and acc[g][1] > 0]
    if preserve == "room-eyring":
        # one factor per band so that the whole room keeps its Eyring exponent (tested, not the default; see docstring)
        A_t, Sm, S2 = sum(acc[g][0] for g in used), sum(acc[g][1] for g in used), sum(S25[g] for g in used)
        k = (1 - np.exp(Sm * np.log(1 - A_t / Sm) / S2)) * S2 / A_t
        report["scale_k"] = [round(float(x), 4) for x in k]
    for g in used:
        A, S, sS = acc[g]
        if preserve == "eyring":
            alpha = 1 - np.exp(-A / S25[g])
        elif preserve == "room-eyring":
            alpha = k * A / S25[g]
        else:
            alpha = A / S25[g]
        alpha = np.minimum(0.95, alpha)
        out_m[g] = {"alpha": [round(float(x), 4) for x in alpha], "s": round(sS / S, 3)}
        report["groups"][g] = {"mesh_area_m2": round(S, 1), "hall_area_m2": round(S25[g], 1),
                               "mesh_absorption_area_m2": [round(float(x), 2) for x in A]}
    if "stage" not in out_m and "aud" in out_m:
        out_m["stage"] = dict(out_m["aud"])
    geom25["materials"] = out_m
    for k in ("ism_order", "rays", "diffraction"):
        if k in cfg["geometry"] and k != "ism_order":
            geom25[k] = cfg["geometry"][k]
    new = json.loads(json.dumps(cfg))
    new["name"] = cfg.get("name", "hall") + " (2.5D from OBJ)"
    new["geometry"] = geom25
    new["room"]["dims_m"] = [round(float(v), 3) for v in dims]
    new["room"]["stage_depth_m"] = float(stage_depth)
    for k, v in cfg["sources"].items():
        if not k.startswith("_"):
            new["sources"][k]["pos"] = [round(c, 3) for c in to25(v["pos"])]
    for k, v in cfg["receivers"].items():
        if not k.startswith("_"):
            new["receivers"][k] = [round(c, 3) for c in to25(v)]
    # what the browser page needs to load the file (Load config...): a mean absorption for the shoebox fallback and
    # the three source roles. Missing roles get placeholders: S_amp = the first source, B_L / B_R = 2 m high at the
    # stage edge, a quarter of the width in from each side (move them in the page).
    al = np.mean([m["alpha"] for m in out_m.values()], axis=0)
    new["room"]["absorption_octave"] = {"_bands_hz": [125, 250, 500, 1000, 2000, 4000],
                                        "values": [round(float(min(0.95, max(0.01, x))), 4) for x in al]}
    names = [k for k in new["sources"] if not k.startswith("_")]
    if "S_amp" not in new["sources"] and names:
        new["sources"]["S_amp"] = dict(new["sources"][names[0]], role="placeholder: copy of " + names[0])
    W = dims[0]
    yb = max(0.5, yd - max(stage_depth, 0.5))
    for k, fx in (("B_L", 0.25), ("B_R", 0.75)):
        if k not in new["sources"]:
            x = fx * W
            new["sources"][k] = {"pos": [round(x, 3), round(yb, 3), round(geometry.prof_at(floor, yb) + 2.0, 3)],
                                 "role": "placeholder PA position"}
    report.update(volume_mesh_m3=round(G["volume"], 1), n_plan_vertices=len(plan), n_floor=len(floor), n_ceil=len(ceil),
                  n_surfaces_2p5d=len(G25["S"]), dims_m=new["room"]["dims_m"])
    return new, report


def volume_2p5d(geom, n=200000, seed=0):
    """Monte Carlo volume of a drawn hall (inside test of geometry.inside)."""
    G = geometry.build(dict(geom), 1e9)
    xs = [p[0] for p in G["plan"]]
    lo = np.array([min(xs), G["y0"], min(z for _, z in G["floor"])])
    hi = np.array([max(xs), G["y1"], max(z for _, z in G["ceil"])])
    rng = np.random.default_rng(seed)
    P = lo + rng.random((n, 3)) * (hi - lo)
    k = sum(geometry.inside(G, p) for p in P)
    return float(k / n * np.prod(hi - lo))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config")
    ap.add_argument("--out", default=None)
    ap.add_argument("--depth-axis", default="y", choices=["x", "y"])
    ap.add_argument("--stage-end", default="min", choices=["min", "max"])
    ap.add_argument("--stage-depth", type=float, default=0.0)
    ap.add_argument("--slice", type=float, default=0.25)
    ap.add_argument("--tol", type=float, default=0.08)
    ap.add_argument("--preserve", default="eyring", choices=["eyring", "sabine", "room-eyring"],
                    help="how mesh absorption maps to the 2.5D groups (see the docstring)")
    a = ap.parse_args()
    import brir_proto as bp
    cfg = bp.load_config(a.config)
    new, rep = convert(cfg, a.depth_axis, a.stage_end, a.stage_depth, a.slice, a.tol, a.preserve)
    rep["volume_2p5d_m3"] = round(volume_2p5d(new["geometry"], 50000), 1)
    out = a.out or os.path.splitext(a.config)[0] + "_2p5d.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(new, f, ensure_ascii=False, indent=1)
    print(json.dumps(rep, indent=1))
    print("->", out)


if __name__ == "__main__":
    main()
