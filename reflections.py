"""
Specular reflection factors for image sources: finite reflector size (Kirchhoff-Fresnel) and scattering loss.

An image source treats every reflecting surface as an infinite plane. A real panel of limited size reflects
less at low frequencies and near its edges, and a surface with scattering coefficient s sends only (1 - s) of the
reflected energy in the specular direction (the rest is scattered, which the ray tracer carries). Both are applied
here to each reflection of an image-source path, per frequency band, as an energy factor:

    F = prod over the reflections of  (1 - s_b) * K1 * K2

K1, K2: Kirchhoff-Fresnel factors of the reflecting panel in two orthogonal sections through the reflection point,
after Rindel, J. H. (2005), "Reflection of sound from finite-size plane and curved surfaces", 150th ASA meeting,
J. Acoust. Soc. Am. 118(3), presentation https://core.ac.uk/download/13729852.pdf (see also Rindel 1992, Proc. IoA
14(2), "Acoustic design of reflectors in auditoria"):

    K = 1/2 * ((C(v2) - C(v1))^2 + (S(v2) - S(v1))^2),   v = 2 x cos(theta) / sqrt(lambda a*),
    a* = 2 a1 a2 / (a1 + a2)

C, S: Fresnel integrals; x: signed distances from the reflection point to the two panel edges along the section
(v1 from the near-side edge behind the point, v2 from the edge ahead); theta: angle of incidence, applied in the
section that contains the incidence direction (in the other section cos = 1); a1, a2: path lengths from the
source to the reflection point and from there to the receiver, along the unfolded image path (engineering choice
for higher orders: Rindel's formula is for one reflection). An infinite plane gives K = 1. K is averaged over
three frequencies per octave band (centre and +-1/3 octave).

The "panel" of a reflection is the set of connected surfaces of the hall that contains the reflection point:
surfaces that touch (within 1 cm) and whose normals differ by less than 2 deg (in practice: one plane). A mesh's
triangles of one flat wall count as one panel; beams, coffers, steps, gaps and bends split panels. A looser
tolerance (10 deg, so that gentle bends such as two rake slopes count as one panel) was tested on BRAS CR4 and
fitted the measured reflection levels worse (median error +4.1 dB instead of +2.7 dB); CR3 was unchanged.

The same algorithm (including the Fresnel integral routine) is in engine_geom.js, so the browser and Python
engines give the same factors.
"""
import math

import numpy as np

_PI = math.pi


def fresnel(x):
    """(C(x), S(x)) with C = int_0^x cos(pi t^2 / 2) dt. Power series for |x| < 3, asymptotic expansion above;
    absolute error < 2e-6 (checked against scipy.special.fresnel). Identical code in engine_geom.js."""
    ax = abs(x)
    if ax < 3.0:
        z = _PI * ax * ax / 2
        z2 = z * z
        # C = x * sum (-1)^n z^(2n) / ((2n)! (4n+1)),  S = x * sum (-1)^n z^(2n+1) / ((2n+1)! (4n+3))
        tc, ts, c, s = 1.0, z, 0.0, 0.0
        n = 0
        while True:
            c += tc / (4 * n + 1)
            s += ts / (4 * n + 3)
            tc *= -z2 / ((2 * n + 1) * (2 * n + 2))
            ts *= -z2 / ((2 * n + 2) * (2 * n + 3))
            n += 1
            if abs(tc) < 1e-17 and abs(ts) < 1e-17 or n > 60:
                break
        c, s = ax * c, ax * s
    else:
        pz = _PI * ax * ax
        u = 1.0 / (pz * pz)
        f = (1 - u * (3 - u * (105 - u * 10395))) / (_PI * ax)
        g = (1 - u * (15 - u * (945 - u * 135135))) / (_PI * pz * ax)
        z = _PI * ax * ax / 2
        c = 0.5 + f * math.sin(z) - g * math.cos(z)
        s = 0.5 - f * math.cos(z) - g * math.sin(z)
    return (c, s) if x >= 0 else (-c, -s)


def _fresnel_K(lo, hi):
    c1, s1 = fresnel(lo)
    c2, s2 = fresnel(hi)
    return 0.5 * ((c2 - c1) ** 2 + (s2 - s1) ** 2)


# ---------------------------------------------------------------- panels
def _seg_dist(p, a, b):
    ab = b - a
    t = np.clip(np.dot(p - a, ab) / max(np.dot(ab, ab), 1e-18), 0, 1)
    return np.linalg.norm(p - (a + t * ab))


def _touch(A, B, tol):
    """Two coplanar polygons (vertex arrays) touch or overlap within tol (vertex-to-edge distance either way)."""
    for P, Q in ((A, B), (B, A)):
        for p in P:
            for k in range(len(Q)):
                if _seg_dist(p, Q[k], Q[(k + 1) % len(Q)]) <= tol:
                    return True
    return False


PANEL_ANGLE_DEG = 2.0      # touching surfaces whose normals differ by less than this act as one panel (see docstring)


def panels(G, tol=0.01, angle_deg=None):
    """Cache on G: for every surface its panel id, and the list of surfaces per panel. Two surfaces are in one
    panel when they touch (a vertex within tol of the other's edge; meshes from CAD exports have T-junctions, so
    shared vertices are not enough) and their normals differ by less than angle_deg (default PANEL_ANGLE_DEG).
    Candidate pairs come from a sweep over the bounding boxes."""
    ang = PANEL_ANGLE_DEG if angle_deg is None else angle_deg
    if G.get("_panels_key") == (tol, ang):
        return G["_panels"]
    S = G["S"]
    n = len(S)
    N = np.array([np.asarray(s["n"], float) / np.linalg.norm(s["n"]) for s in S])
    V = [np.asarray(s["verts"], float) for s in S]
    lo = np.array([v.min(0) for v in V]) - tol
    hi = np.array([v.max(0) for v in V]) + tol
    cmin = math.cos(math.radians(ang))
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    order = np.argsort(lo[:, 0])
    active = []
    for a in order:
        active = [b for b in active if hi[b, 0] >= lo[a, 0]]
        for b in active:
            if np.dot(N[a], N[b]) < cmin or np.any(lo[a, 1:] > hi[b, 1:]) or np.any(lo[b, 1:] > hi[a, 1:]):
                continue
            if find(a) != find(b) and _touch(V[a], V[b], tol):
                parent[find(b)] = find(a)
        active.append(a)
    pid = [find(i) for i in range(n)]
    members = {}
    for i, p in enumerate(pid):
        members.setdefault(p, []).append(i)
    G["_panels"], G["_panels_key"] = (pid, members), (tol, ang)
    return G["_panels"]


def _chord(G, members, P, e, f):
    """Interval (smin <= 0 <= smax) of the line P + s e (e, f in the panel plane) inside the union of the panel's
    polygons."""
    iv = []
    for i in members:
        V = np.asarray(G["S"][i]["verts"], float) - P
        x, y = V @ e, V @ f
        xs = []
        for k in range(len(x)):
            x1, y1, x2, y2 = x[k], y[k], x[(k + 1) % len(x)], y[(k + 1) % len(x)]
            if (y1 <= 0 < y2) or (y2 <= 0 < y1):
                xs.append(x1 + (0 - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        iv += [(xs[j], xs[j + 1]) for j in range(0, len(xs) - 1, 2)]
    if not iv:
        return -1e9, 1e9
    iv.sort()
    merged = [list(iv[0])]
    for a, b in iv[1:]:
        if a <= merged[-1][1] + 1e-3:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    for a, b in merged:
        if a - 1e-3 <= 0 <= b + 1e-3:
            return min(a, 0.0), max(b, 0.0)
    a, b = min(merged, key=lambda q: min(abs(q[0]), abs(q[1])))
    return min(a, 0.0), max(b, 0.0)


def reflection_K(G, wall, P, u_in, a1, a2, freqs, c):
    """Energy factor K1*K2 per frequency in `freqs` for a reflection at P on surface `wall`."""
    pid, members = panels(G)
    n = np.asarray(G["S"][wall]["n"], float)
    n = n / np.linalg.norm(n)
    cos_t = abs(float(np.dot(u_in, n)))
    t = u_in - np.dot(u_in, n) * n
    if np.linalg.norm(t) < 1e-6:
        t = np.cross(n, [1.0, 0, 0]) if abs(n[0]) < 0.9 else np.cross(n, [0, 1.0, 0])
    e1 = t / np.linalg.norm(t)
    e2 = np.cross(n, e1)
    mem = members[pid[wall]]
    s1 = _chord(G, mem, P, e1, e2)
    s2 = _chord(G, mem, P, e2, e1)
    astar = 2 * a1 * a2 / (a1 + a2)
    out = []
    for fr in freqs:
        k = 2 / math.sqrt(c / fr * astar)
        out.append(_fresnel_K(k * s1[0] * cos_t, k * s1[1] * cos_t) * _fresnel_K(k * s2[0], k * s2[1]))
    return np.array(out)


def band_freqs(fc):
    return [fc * 2 ** (-1 / 3), fc, fc * 2 ** (1 / 3)]


# ---------------------------------------------------------------- image sources (pyroomacoustics)
def _scatter(mats, mat, nb):
    s = mats[mat].get("s", 0.0)
    if isinstance(s, (list, tuple)):
        return np.array([s[i] if i < len(s) else s[-1] for i in range(nb)], float)
    return np.full(nb, float(s))


_CHAIN_CACHE = {}


def _image_chains(G, src, order):
    """All image sources of `src` up to `order` with their wall sequences, generated from the source like the
    browser engine does (an image is mirrored at every surface it lies in front of, never twice in a row at the same
    surface). pyroomacoustics keeps only the images that a receiver can hear, so a parent image is often missing from
    its list and the wall sequence cannot be read back from it; it is looked up here by position instead.
    Returns {order: (positions [n, 3], sequences [n, order], KD-tree)}."""
    from scipy.spatial import cKDTree
    key = (id(G), tuple(np.round(np.asarray(src, float), 9)), order)
    if key in _CHAIN_CACHE:
        return _CHAIN_CACHE[key]
    N = np.array([np.asarray(s["n"], float) / np.linalg.norm(s["n"]) for s in G["S"]])
    D = np.array([float(np.dot(N[i], np.asarray(G["S"][i]["verts"], float)[0])) for i in range(len(N))])
    pos = np.asarray(src, float)[None, :]
    seq = np.zeros((1, 0), int)
    out = {}
    for o in range(1, order + 1):
        P, Q = [], []
        for w in range(len(N)):
            side = pos @ N[w] - D[w]
            ok = side > 1e-9
            if seq.shape[1]:
                ok &= seq[:, -1] != w
            if not ok.any():
                continue
            P.append(pos[ok] - 2 * side[ok, None] * N[w][None, :])
            Q.append(np.c_[seq[ok], np.full(ok.sum(), w)])
        if not P:
            break
        pos, seq = np.vstack(P), np.vstack(Q)
        out[o] = (pos, seq, cKDTree(pos))
        if len(pos) > 3_000_000:
            break
    _CHAIN_CACHE.clear()
    _CHAIN_CACHE[key] = out
    return out


def _trace(G, planes, src, rec, seq):
    """Reflection points (source side first) of the path src -> seq -> rec, back-traced from the receiver through
    the images; None when a point falls outside its surface (the path does not exist for this wall sequence)."""
    import diffraction
    ims, p_ = [], np.asarray(src, float)
    for w in seq:
        n = planes[w][0]
        d = float(np.dot(n, np.asarray(G["S"][w]["verts"], float)[0]))
        p_ = p_ - 2 * (np.dot(n, p_) - d) * n
        ims.append(p_)
    pts, p = [], np.asarray(rec, float)
    for w, im in zip(seq[::-1], ims[::-1]):
        n = planes[w][0]
        d = float(np.dot(n, np.asarray(G["S"][w]["verts"], float)[0]))
        den = float(np.dot(n, im - p))
        if abs(den) < 1e-12:
            return None
        t = (d - float(np.dot(n, p))) / den
        q = p + t * (im - p)
        if not (1e-9 < t < 1) or not diffraction.in_surface(G["S"][w], q):
            return None
        pts.append(q)
        p = q
    return pts[::-1]


def image_factors(G, room, sel, src, rec, c, mats, finite=True, scatter=True):
    """Energy factors [n_bands, len(sel)] for the images `sel` of room.sources[0] heard at `rec`
    (pyroomacoustics general Room built from G by geometry.pra_walls; wall index = surface index of G)."""
    S = room.sources[0]
    cen = np.asarray(room.octave_bands.centers, float)
    nb = len(cen)
    F = np.ones((nb, len(sel)))
    if not (finite or scatter):
        return F
    imgs, orders, walls_k = np.asarray(S.images, float), np.asarray(S.orders), np.asarray(S.walls)
    chains = _image_chains(G, src, int(orders[sel].max()) if len(sel) else 0)
    import diffraction
    diffraction.prepare(G)
    planes = [(np.asarray(s["n"], float) / np.linalg.norm(s["n"]),) for s in G["S"]]
    src, rec = np.asarray(src, float), np.asarray(rec, float)
    freqs = [band_freqs(f) for f in cen]
    for j, k in enumerate(sel):
        o = int(orders[k])
        if o == 0 or o not in chains:
            continue
        pos, seqs, tree = chains[o]
        tol = 1e-3 * max(1.0, np.linalg.norm(imgs[:, k]) / 100)
        cand = tree.query_ball_point(imgs[:, k], tol)
        best = None
        for q in sorted(cand, key=lambda q: np.linalg.norm(pos[q] - imgs[:, k])):
            seq = [int(w) for w in seqs[q]]                # source side first
            if seq[-1] != int(walls_k[k]):
                continue
            got = _trace(G, planes, src, rec, seq)
            if got is not None:
                best = (seq, got)
                break
        if best is None:
            continue
        seq, pts = best
        chain = list(seq)
        path = [src] + pts + [rec]
        seg = [float(np.linalg.norm(path[i + 1] - path[i])) for i in range(len(path) - 1)]
        tot = sum(seg)
        for r, (w, P) in enumerate(zip(chain, pts)):
            a1 = sum(seg[: r + 1])
            u_in = (P - path[r]) / max(seg[r], 1e-12)
            f = np.ones(nb)
            if scatter:
                f *= 1 - _scatter(mats, G["S"][w]["mat"], nb)
            if finite:
                f *= np.array([np.mean(reflection_K(G, w, P, u_in, a1, tot - a1, fr, c)) for fr in freqs])
            F[:, j] *= f
    return F
