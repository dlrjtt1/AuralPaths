"""
Higher-order specular reflection paths in large mesh halls (ray-guided image sources).

For an OBJ mesh of thousands of surfaces a complete image-source search beyond the first order is out of reach
(N^order wall sequences), so the engines stop at order 1 there, and later specular reflections end up in the
statistical late tail. In a measured hall (BRAS CR4) such reflections are audible: discrete arrivals from the median
plane (front / back / ceiling) at about 85 and 170 ms after the direct sound, which the noise tail cannot reproduce
(late IACC 0.23 - 0.38 measured, 0.07 - 0.10 simulated; validation/bras_brir_iacc_diag.md).

Method (ray-guided image sources; using rays to find the image sources that exist goes back to Vorlaender, M. (1989),
"Simulation of the transient and steady-state sound propagation in rooms using a new combined ray-tracing/image-
source algorithm", JASA 86(1), 172-178,
https://scholar.google.com/scholar?q=Vorlaender+1989+combined+ray-tracing+image-source+algorithm):
  1. Rays from the source, reflected purely specularly up to `order` times. Each segment after the k-th
     reflection (k >= 2) that passes the receiver within a radius growing with the path length nominates its
     sequence of panels (reflections.panels: touching coplanar surfaces) as a candidate.
  2. Each candidate is checked exactly like an image source: mirror the source in the panel planes, back-trace
     from the receiver, every reflection point must lie on a surface of its panel with the path arriving from the
     room side, and no leg may be blocked by another surface.
  3. Valid paths (deduplicated by image position, 1 cm) are returned with their reflection points; their energy
     factors use the same rules as the first-order images (absorption, (1 - s) scattering loss and the finite
     reflector factor of reflections.py).
The ray stage can miss a path that no ray passes closely enough; with the default ray count the radius is chosen so
that rays overlap at the receiver for the path lengths of interest (see find_paths).
"""
import math

import numpy as np

import diffraction
import reflections


def _fib(n):
    """Fibonacci sphere of n directions (deterministic; same sequence as specPaths in engine_geom.js)."""
    k = np.arange(n)
    z = 1 - 2 * (k + 0.5) / n
    ph = math.pi * (1 + math.sqrt(5)) * (k + 0.5)
    r = np.sqrt(np.maximum(0, 1 - z * z))
    return np.c_[r * np.cos(ph), r * np.sin(ph), z]


def _tris(G):
    """Fan triangulation of the surfaces (cached on G): V0, E1, E2 [n_tri, 3] and the surface of each triangle."""
    if "_tris" not in G:
        V0, E1, E2, F = [], [], [], []
        for i, s in enumerate(G["S"]):
            v = np.asarray(s["verts"], float)
            for k in range(1, len(v) - 1):
                V0.append(v[0]); E1.append(v[k] - v[0]); E2.append(v[k + 1] - v[0]); F.append(i)
        G["_tris"] = (np.array(V0), np.array(E1), np.array(E2), np.array(F))
    return G["_tris"]


def ray_hits(G, O, D, last, chunk=96, t_max=np.inf):
    """Nearest surface hit of rays O + t D (1e-7 < t < t_max), skipping each ray's surface `last`; only surfaces whose
    normal faces the ray (n . d < 0: the room side, as the ray tracers). Moeller-Trumbore on the fan-triangulated
    surfaces, all pairs, in chunks of rays. Returns (t, surface); inf / -1 for no hit."""
    V0, E1, E2, F = _tris(G)
    NF = G["N"][F]
    n = len(O)
    tb, sb = np.full(n, np.inf), np.full(n, -1)
    for a in range(0, n, chunk):
        o, d, ls = O[a:a + chunk, None, :], D[a:a + chunk, None, :], last[a:a + chunk]
        pv = np.cross(d, E2[None])
        det = np.einsum("rtk,tk->rt", pv, E1)
        ok = np.abs(det) > 1e-12
        inv = np.where(ok, 1 / np.where(ok, det, 1), 0)
        tv = o - V0[None]
        u = np.einsum("rtk,rtk->rt", tv, pv) * inv
        ok &= (u >= -1e-9) & (u <= 1 + 1e-9)
        qv = np.cross(tv, E1[None])
        v = np.einsum("rtk,rtk->rt", d, qv) * inv
        ok &= (v >= -1e-9) & (u + v <= 1 + 1e-9)
        t = np.einsum("tk,rtk->rt", E2, qv) * inv
        ok &= (t > 1e-7) & (t < t_max) & (F[None, :] != ls[:, None]) & (np.einsum("rk,tk->rt", d[:, 0, :], NF) < -1e-12)
        t = np.where(ok, t, np.inf)
        j = np.argmin(t, axis=1)
        tj = t[np.arange(len(j)), j]
        hit = np.isfinite(tj)
        tb[a:a + len(j)][hit] = tj[hit]
        sb[a:a + len(j)][hit] = F[j[hit]]
    return tb, sb


def _blocked(G, a, b, skip):
    """True when the segment a -> b crosses a surface other than those in `skip`."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    L = float(np.linalg.norm(b - a))
    V0, E1, E2, F = _tris(G)
    d = (b - a) / L
    pv = np.cross(d, E2)
    det = np.einsum("tk,tk->t", pv, E1)
    ok = np.abs(det) > 1e-12
    inv = np.where(ok, 1 / np.where(ok, det, 1), 0)
    tv = a - V0
    u = np.einsum("tk,tk->t", tv, pv) * inv
    qv = np.cross(tv, E1)
    v = (qv @ d) * inv
    t = np.einsum("tk,tk->t", E2, qv) * inv
    ok &= (u >= 0) & (u <= 1) & (v >= 0) & (u + v <= 1) & (t > 1e-6 * L) & (t < (1 - 1e-6) * L)   # as occluded(): relative
    if skip:
        ok &= ~np.isin(F, list(skip))
    return bool(ok.any())


def candidates(G, src, recs, order=3, t_max=0.35, c=343.0, n_rays=20000, k_radius=1.5):
    """Panel sequences (orders 2 .. order) whose specular rays pass near each receiver: [set per receiver].
    t_max: per receiver (array) or one value, seconds after emission."""
    diffraction.prepare(G)
    pid, _ = reflections.panels(G)
    pid = np.asarray(pid)
    recs = np.atleast_2d(np.asarray(recs, float))
    tmx = np.broadcast_to(np.asarray(t_max, float), (len(recs),))
    D = _fib(n_rays)
    O = np.tile(np.asarray(src, float), (n_rays, 1))
    L = np.zeros(n_rays)
    last = np.full(n_rays, -1)
    seq = np.full((n_rays, order), -1)
    alive = np.ones(n_rays, bool)
    dth = math.sqrt(4 * math.pi / n_rays)          # angular ray spacing (rad)
    Lmax = c * float(tmx.max())
    found = [set() for _ in recs]
    for b in range(order + 1):
        idx = np.flatnonzero(alive)
        if not idx.size:
            break
        t, s = ray_hits(G, O[idx], D[idx], last[idx])
        if b >= 2:                                     # segments after b reflections: do they pass a receiver?
            for m, rec in enumerate(recs):
                w = rec - O[idx]
                tc = np.einsum("ij,ij->i", w, D[idx])
                d2 = np.einsum("ij,ij->i", w, w) - tc * tc
                r = np.maximum(0.3, k_radius * (L[idx] + np.maximum(tc, 0)) * dth)
                near = (tc > 0) & (tc < t) & (d2 < r * r) & (L[idx] + tc < c * tmx[m])
                for i in np.flatnonzero(near):
                    found[m].add(tuple(int(pid[f]) for f in seq[idx[i], :b]))
        if b == order:
            break
        hit = np.isfinite(t)
        alive[idx[~hit]] = False
        idx, t, s = idx[hit], t[hit], s[hit]
        O[idx] = O[idx] + t[:, None] * D[idx]
        n = G["N"][s]
        D[idx] = D[idx] - 2 * np.einsum("ij,ij->i", D[idx], n)[:, None] * n
        L[idx] += t
        last[idx] = s
        seq[idx, b] = s
        alive[idx[L[idx] > Lmax]] = False
    return found


def validate(G, src, rec, pseq):
    """Exact check of a panel sequence. Returns (reflection points, surfaces, image) or None."""
    pid, members = reflections.panels(G)
    S = G["S"]
    src, rec = np.asarray(src, float), np.asarray(rec, float)
    planes = []
    for p in pseq:
        f = members[p][0]
        n = np.asarray(S[f]["n"], float)
        n = n / np.linalg.norm(n)
        planes.append((n, float(n @ np.asarray(S[f]["verts"], float)[0])))
    ims, im = [], src
    for n, d in planes:
        im = im - 2 * (n @ im - d) * n
        ims.append(im)
    pts, faces, p = [], [], rec
    for (n, d), im, pnl in zip(planes[::-1], ims[::-1], pseq[::-1]):
        den = float(n @ (im - p))
        if abs(den) < 1e-12:
            return None
        t = (d - float(n @ p)) / den
        if not (1e-6 < t < 1 - 1e-9):
            return None
        q = p + t * (im - p)
        f = next((m for m in members[pnl] if diffraction.in_surface(S[m], q)), None)
        if f is None:
            return None
        pts.append(q)
        faces.append(f)
        p = q
    pts, faces = pts[::-1], faces[::-1]
    path = [src] + pts + [rec]
    for k, (n, d) in enumerate(planes):        # both neighbours of a reflection point on the same side (room side)
        a, b = float(n @ path[k]) - d, float(n @ path[k + 2]) - d
        if a * b <= 0:
            return None
    for k in range(len(path) - 1):
        skip = set()
        if k > 0:
            skip.add(faces[k - 1])
        if k < len(faces):
            skip.add(faces[k])
        if _blocked(G, path[k], path[k + 1], skip):
            return None
    return pts, faces, ims[-1]


def find_paths(G, src, recs, order=3, t_max=0.35, c=343.0, n_rays=20000):
    """Valid specular paths of orders 2 .. order arriving within t_max (s after emission; per receiver or one value)
    at each receiver. Returns [list per receiver] of dicts {"order", "faces", "panels", "pts", "image", "dist"},
    sorted by arrival. One ray set per source serves all receivers."""
    recs = np.atleast_2d(np.asarray(recs, float))
    tmx = np.broadcast_to(np.asarray(t_max, float), (len(recs),))
    cand = candidates(G, src, recs, order, tmx, c, n_rays)
    res = []
    for m, rec in enumerate(recs):
        out = []
        for pseq in sorted(cand[m], key=len):
            got = validate(G, src, rec, pseq)
            if got is None:
                continue
            pts, faces, im = got
            if any(len(q["faces"]) == len(faces) and np.linalg.norm(q["image"] - im) < 0.01 for q in out):
                continue
            dist = float(np.linalg.norm(rec - im))
            if dist / c > tmx[m]:
                continue
            out.append({"order": len(faces), "faces": faces, "panels": list(pseq), "pts": pts, "image": im, "dist": dist})
        res.append(sorted(out, key=lambda q: q["dist"]))
    return res


def path_energy(G, mats, q, src, rec, centers, air, c, finite=True, scatter=True):
    """Band energy at the receiver (point source of unit power, no directivity): prod (1 - alpha) (1 - s) K / d^2
    with air absorption. Same factors as reflections.image_factors and the pyroomacoustics image damping."""
    nb = len(centers)
    src, rec = np.asarray(src, float), np.asarray(rec, float)
    path = [src] + list(q["pts"]) + [rec]
    seg = [float(np.linalg.norm(path[i + 1] - path[i])) for i in range(len(path) - 1)]
    tot = sum(seg)
    E = np.ones(nb)
    freqs = [reflections.band_freqs(f) for f in centers]
    for r, (w, P) in enumerate(zip(q["faces"], q["pts"])):
        m = mats[G["S"][w]["mat"]]
        a = list(m["alpha"])
        E *= 1 - np.array([a[i] if i < len(a) else a[-1] for i in range(nb)], float)
        if scatter:
            E *= 1 - reflections._scatter(mats, G["S"][w]["mat"], nb)
        if finite:
            a1 = sum(seg[: r + 1])
            u_in = (P - path[r]) / max(seg[r], 1e-12)
            E *= np.array([np.mean(reflections.reflection_K(G, w, P, u_in, a1, tot - a1, fr, c)) for fr in freqs])
    return E / tot ** 2 * np.exp(-np.asarray(air, float) * tot)
