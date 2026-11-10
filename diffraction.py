"""
Edge diffraction (first and second order) for AuralPaths drawn halls (Python twin of GEOM.edges / GEOM.diffract in engine_geom.js).

Method: Uniform Theory of Diffraction (UTD), Kouyoumjian & Pathak (1974), "A uniform geometrical theory of diffraction for an edge in a perfectly
conducting surface", Proc. IEEE 62, 1448-1461 (DOI not verified here; Google Scholar:
https://scholar.google.com/scholar?q=A+uniform+geometrical+theory+of+diffraction+for+an+edge+in+a+perfectly+conducting+surface), in the form used for room acoustics by Tsingos, Funkhouser, Ngan & Carlbom
(2001), SIGGRAPH, https://doi.org/10.1145/383259.383323: spherical-wave incidence, hard faces whose reflection
terms are weighted by the face reflection factors R = sqrt(1 - alpha) (a heuristic, as in Tsingos et al.).

    p_d(f) = D(f) * exp(-j k (s + s')) / sqrt(s s' (s + s'))
    D = -exp(-j pi/4) / (2 n sqrt(2 pi k) sin b0) *
        [ cot((pi + (phi - phi'))/2n) F(k L a+(phi - phi')) + cot((pi - (phi - phi'))/2n) F(k L a-(phi - phi'))
          + Rn cot((pi + (phi + phi'))/2n) F(k L a+(phi + phi')) + R0 cot((pi - (phi + phi'))/2n) F(k L a-(phi + phi')) ]
    L = s s' sin^2 b0 / (s + s'),  a+-(x) = 2 cos^2((2 n pi N+- - x) / 2),  N+- the integers closest to (x +- pi) / (2 n pi)
    F(X) = 2 j sqrt(X) exp(jX) int_sqrt(X)^inf exp(-j t^2) dt  (transition function)

Wedge: exterior (air) angle n*pi between face 0 (phi = 0) and face n (phi = n pi). Only convex edges (n > 1) are used.
F is evaluated by its power series for X <= 16 and its asymptotic series above (|error| < 1e-4 at the switch).
At a shadow or reflection boundary, a cot term is singular while F -> 0; the product has the finite limit used below,
so the diffracted field is continuous and, added to the geometrical field, removes its jump.

Scope (limitations, stated in the README): one edge per path (source -> edge -> receiver), optionally with one
specular reflection before and/or after it (refl_order=1; image source / image receiver); straight edges between two
planar faces, or thin-plate edges (n = 2) where two faces lie back to back within THIN_M (a free-standing panel, a
partition); second order (two edges in sequence, thick obstacles) in diffract2, opt-in; no higher orders (no seat
dip), diffraction from edge end points ignored, hard-face UTD with a reflection-factor heuristic. Checked against
BRAS RS5 (validation/bras_rs5.md) and RS1 - RS4, RS6, RS7 (validation/bras_rs.md). The diffracted arrival is rendered with the HRIR of the apex direction; its energy enters
the image-source histogram with its interference with the geometrical arrivals of the same boundary.
"""
from __future__ import annotations

import math

import numpy as np

DF = np.geomspace(16.0, 24000.0, 32)        # frequency grid of the complex coefficient (shared with the browser)
MIN_ANGLE_DEG = 2.0                        # skip edges whose faces are within 2 deg of coplanar
THIN_M = 0.05                              # faces closer than this, back to back, end in one thin-plate edge (n = 2)
SQPI2 = math.sqrt(math.pi) / 2


def _fresnel_tail(a):
    """int_a^inf exp(-j t^2) dt for a >= 0 (power series of int_0^a, valid for a <= 4)."""
    s, term, n = 0j, complex(a), 0
    a2 = a * a
    while True:
        add = term / (2 * n + 1)
        s += add
        if abs(add) < 1e-16 * max(1.0, abs(s)) and n > 2:
            break
        n += 1
        term *= -1j * a2 / n
        if n > 400:
            break
    return SQPI2 * complex(math.cos(math.pi / 4), -math.sin(math.pi / 4)) - s


def transition(X):
    """UTD transition function F(X), X >= 0."""
    if X <= 0:
        return 0j
    if X > 16:
        x = 1 / X
        return 1 + 0.5j * x - 0.75 * x * x - 1.875j * x ** 3 + 6.5625 * x ** 4
    r = math.sqrt(X)
    return 2j * r * complex(math.cos(X), math.sin(X)) * _fresnel_tail(r)


def _npm(x, n, sign):
    return round((x + sign * math.pi) / (2 * n * math.pi))


def _term(beta, n, kL, sign):
    """cot((pi + sign*beta) / 2n) * F(kL a_sign(beta)) with its finite limit at the boundary."""
    N = _npm(beta, n, sign)
    a = 2 * math.cos((2 * n * math.pi * N - beta) / 2) ** 2
    arg = (math.pi + sign * beta) / (2 * n)
    if abs(math.sin(arg)) < 1e-9:   # on the boundary: limit n sqrt(2 pi kL) sgn(eps) exp(j pi/4), eps = pi + sign (beta - 2 pi n N)
        eps = math.pi + sign * (beta - 2 * math.pi * n * N)
        return n * math.sqrt(2 * math.pi * kL) * (1 if eps >= 0 else -1) * complex(math.cos(math.pi / 4), math.sin(math.pi / 4))
    return F_cached(kL * a) / math.tan(arg)


F_cached = transition


def utd(n, phi, phi0, s, s0, sinb, f, c, R0, Rn):
    """Complex diffracted pressure p_d (unit point source, e^{j w t} convention) at the frequencies f, without the
    propagation delay exp(-j k (s + s0)) (the renderer applies it as a time shift)."""
    out = np.zeros(len(f), complex)
    L = s * s0 * sinb * sinb / (s + s0)
    A = 1 / math.sqrt(s * s0 * (s + s0))
    for i, fi in enumerate(f):
        k = 2 * math.pi * fi / c
        kL = k * L
        t = (_term(phi - phi0, n, kL, +1) + _term(phi - phi0, n, kL, -1)
             + Rn[i] * _term(phi + phi0, n, kL, +1) + R0[i] * _term(phi + phi0, n, kL, -1))
        D = -complex(math.cos(math.pi / 4), -math.sin(math.pi / 4)) / (2 * n * math.sqrt(2 * math.pi * k) * sinb) * t
        out[i] = A * D
    return out


# ---------------------------------------------------------------- geometry helpers (surfaces from geometry.build)
def prepare(G):
    """Add plane offsets, 2D projections and bounding boxes to the surfaces (same as engine_geom.js makeSurface)."""
    for s in G["S"]:
        if "d" in s:
            continue
        n = np.asarray(s["n"], float)
        v = np.asarray(s["verts"], float)
        s["d"] = float(n @ v[0])
        ax = int(np.argmax(np.abs(n)))
        s["uv"] = [i for i in range(3) if i != ax]
        s["p2"] = v[:, s["uv"]]
        s["bb"] = (s["p2"].min(0) - 1e-7, s["p2"].max(0) + 1e-7)
    if "N" not in G:
        G["N"] = np.array([s["n"] for s in G["S"]], float)
        G["Dp"] = np.array([s["d"] for s in G["S"]], float)
    return G


def _in_poly2(p2, a, b):
    c = False
    j = len(p2) - 1
    for i in range(len(p2)):
        xi, yi = p2[i]
        xj, yj = p2[j]
        if (yi > b) != (yj > b) and a < (xj - xi) * (b - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def in_surface(s, p):
    a, b = p[s["uv"][0]], p[s["uv"][1]]
    lo, hi = s["bb"]
    if a < lo[0] or a > hi[0] or b < lo[1] or b > hi[1]:
        return False
    return _in_poly2(s["p2"], a, b)


def occluded(G, a, b, skip=()):
    a = np.asarray(a, float)
    d = np.asarray(b, float) - a
    den = G["N"] @ d
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (G["Dp"] - G["N"] @ a) / den
    cand = np.flatnonzero((np.abs(den) > 1e-9) & (t > 1e-6) & (t < 1 - 1e-6))
    for i in cand:
        if i in skip:
            continue
        if in_surface(G["S"][i], a + t[i] * d):
            return True
    return False


def _into(s, n, t, mid, delta=1e-3):
    """Unit vector in face s, perpendicular to the edge t at mid, pointing into the face (local test: the face
    polygon may lie on both sides of the edge line elsewhere), or None if not a boundary edge of s."""
    u = np.cross(n, t)
    a, b = in_surface(s, mid + delta * u), in_surface(s, mid - delta * u)
    return u if a and not b else -u if b and not a else None


def edges(G):
    """Convex edges shared by two surfaces: list of dicts {a, b (end points), t (unit), i0, i1 (faces), n (wedge index),
    t0 (unit vector in face 0, perpendicular to the edge, pointing into the face)}."""
    prepare(G)
    sides, owner = [], []
    for k, s in enumerate(G["S"]):
        v = np.asarray(s["verts"], float)
        for i in range(len(v)):
            p, q = v[i], v[(i + 1) % len(v)]
            if np.linalg.norm(q - p) > 1e-6:
                sides.append((p, q)); owner.append(k)
    P = np.array([s[0] for s in sides]); Q = np.array([s[1] for s in sides]); own = np.array(owner)
    T = (Q - P) / np.linalg.norm(Q - P, axis=1)[:, None]
    out = []
    cos_min = math.cos(math.radians(MIN_ANGLE_DEG))
    for i in range(len(sides)):
        j = np.arange(i + 1, len(sides))
        j = j[own[j] != own[i]]
        if not j.size:
            continue
        par = np.abs(T[j] @ T[i]) > 1 - 1e-7
        w = P[j] - P[i]
        off = np.linalg.norm(w - (w @ T[i])[:, None] * T[i], axis=1)
        j = j[par & (off < 1e-6)]
        for jj in j:
            A, B = own[i], own[jj]
            nA, nB = np.asarray(G["S"][A]["n"], float), np.asarray(G["S"][B]["n"], float)
            if abs(nA @ nB) > cos_min and nA @ nB > 0:
                continue                                   # (nearly) coplanar
            t = T[i]
            u0, u1 = sorted([0.0, (Q[i] - P[i]) @ t]); w0, w1 = sorted([(P[jj] - P[i]) @ t, (Q[jj] - P[i]) @ t])
            lo, hi = max(u0, w0), min(u1, w1)
            if hi - lo < 1e-3:
                continue
            mid = P[i] + 0.5 * (lo + hi) * t
            tA, tB = _into(G["S"][A], nA, t, mid), _into(G["S"][B], nB, t, mid)
            if tA is None or tB is None:
                continue
            if tB @ nA >= -1e-9:
                continue                                   # concave: no first-order diffraction term
            n = (math.pi + math.acos(max(-1.0, min(1.0, float(nA @ nB))))) / math.pi
            out.append(dict(a=P[i] + lo * t, b=P[i] + hi * t, t=t, i0=int(A), i1=int(B), n=n, t0=tA, n0=nA))
    if THIN_M > 0:
        out = _thin_edges(G, P, Q, own, T, out)
    return out


def _continued(G, Nn, A, p):
    """True if a face other than A, (nearly) coplanar with A and facing the same way, contains the point p (just
    across a side of A): the side is then inside a panel, not at its boundary."""
    nA = Nn[A]
    dA = G["S"][A]["d"]
    for k in np.flatnonzero(Nn @ nA > 0.9994):           # within 2 deg
        if k != A and abs(Nn[k] @ p - G["S"][k]["d"]) < 2e-3 and abs(nA @ p - dA) < 2e-3 and in_surface(G["S"][k], p):
            return True
    return False


def _touching(G, Nn, A, B, mid, nA, tA, h):
    """True if a surface other than A, B meets the edge at `mid`: it holds one of the points just beside the edge on
    either side of the plate (a panel standing on the floor, a twin-faced wall meeting the ceiling) or just beyond
    it. A thin end face between A and B holds none of them."""
    Dp = np.array([G["S"][k]["d"] for k in range(len(G["S"]))]) if "Dp" not in G else G["Dp"]
    for pr in (mid + h * nA, mid - h * nA, mid - h * tA):
        for k in np.flatnonzero(np.abs(Nn @ pr - Dp) < 2.5e-3):   # 2.5 mm: clear of the 1 / 1.5 / 3 mm steps of mesh twin faces
            if k not in (A, B) and in_surface(G["S"][k], pr):
                return True
    return False


def _thin_edges(G, P, Q, own, T, out):
    """Free-standing plates (a panel drawn as two faces back to back, or a box thinner than THIN_M): the boundary
    sides of two antiparallel faces that run parallel within THIN_M of each other, with both faces extending to the
    same side, form one thin-plate edge (exterior angle 2 pi, n = 2) on their mid line. The convex edges of a thin
    end face (e.g. the 25 mm top of a partition) are replaced by it: for a plate thin compared with the wavelength
    these two closely spaced wedges act as one half-plane edge (first-order UTD cannot combine two edges)."""
    thin = []
    Nn = np.array([np.asarray(s["n"], float) for s in G["S"]])
    for i in range(len(P)):
        A = own[i]
        nA = Nn[A]
        j = np.flatnonzero(own > A)                       # vectorised pre-selection (as in edges())
        if not j.size:
            continue
        w = P[j] - P[i]
        offn = np.linalg.norm(w - (w @ T[i])[:, None] * T[i], axis=1)
        j = j[(np.abs(T[j] @ T[i]) > 1 - 1e-7) & (offn <= THIN_M) & (Nn[own[j]] @ nA <= -1 + 1e-6)]
        for jj in j:
            B = own[jj]
            nB = Nn[B]
            if nA @ nB > -1 + 1e-6:
                continue
            t = T[i]
            w = P[jj] - P[i]
            off = w - (w @ t) * t
            if np.linalg.norm(off) > THIN_M or abs(off @ nA) < 1e-9 or np.linalg.norm(off - (off @ nA) * nA) > 1e-6:
                continue                                   # the sides must be offset along the face normal only
            u0, u1 = sorted([0.0, (Q[i] - P[i]) @ t]); w0, w1 = sorted([(P[jj] - P[i]) @ t, (Q[jj] - P[i]) @ t])
            lo, hi = max(u0, w0), min(u1, w1)
            if hi - lo < 1e-3:
                continue
            midA = P[i] + 0.5 * (lo + hi) * t
            tA, tB = _into(G["S"][A], nA, t, midA), _into(G["S"][B], nB, t, midA + off)
            if tA is None or tB is None or tA @ tB < 1 - 1e-6:
                continue
            if _continued(G, Nn, A, midA - 1e-3 * tA) or _continued(G, Nn, B, midA + off - 1e-3 * tB):
                continue                                   # interior side (e.g. a triangle diagonal), not a plate edge
            if (off @ nA) > 0:                             # back to back (not two faces looking at each other)
                continue
            a = P[i] + 0.5 * off
            mid = a + 0.5 * (lo + hi) * t
            wd = float(np.linalg.norm(off))
            if _touching(G, Nn, A, B, mid, nA, tA, wd / 2 + 2e-3):
                continue                                   # another surface meets the edge: not a free plate edge
            thin.append(dict(a=a + lo * t, b=a + hi * t, t=t, i0=int(A), i1=int(B), n=2.0, t0=tA, n0=nA, thin=True,
                             w=float(np.linalg.norm(off))))
    if not thin:
        return out
    keep = []
    for e in out:                                      # drop the wedges of the thin end faces
        absorbed = False
        for th in thin:
            if abs(e["t"] @ th["t"]) < 1 - 1e-7:
                continue
            w = e["a"] - th["a"]
            if np.linalg.norm(w - (w @ th["t"]) * th["t"]) <= th["w"] / 2 + 1e-6:
                absorbed = True
                break
        if not absorbed:
            keep.append(e)
    return keep + thin


def _angle(w, t0, n0):
    return math.atan2(float(w @ n0), float(w @ t0)) % (2 * math.pi)


def _band_freqs(bands):
    return [np.geomspace(fc / math.sqrt(2), fc * math.sqrt(2), 8) for fc in bands]


def _refl(G, S, R, k, Rb):
    """Specular reflection of S in face k reaching R: (path length, band amplitude without air) or None."""
    s = G["S"][k]
    n = np.asarray(s["n"], float)
    side = n @ S - s["d"]
    if side <= 1e-9:
        return None
    I = S - 2 * side * n
    dv = R - I
    den = n @ dv
    if abs(den) < 1e-12:
        return None
    t = (s["d"] - n @ I) / den
    if not 0 < t < 1:
        return None
    P = I + t * dv
    if not in_surface(s, P) or occluded(G, S, P, (k,)) or occluded(G, P, R, (k,)):
        return None
    return float(np.linalg.norm(dv)), Rb


def _mirror(G, X, k):
    s = G["S"][k]
    n = np.asarray(s["n"], float)
    side = float(n @ X - s["d"])
    return None if side <= 1e-9 else X - 2 * side * n


def _on_plane(G, k, e):
    s = G["S"][k]
    n = np.asarray(s["n"], float)
    return abs(n @ e["a"] - s["d"]) < 1e-6 and abs(n @ e["b"] - s["d"]) < 1e-6


def _via(G, X, Ximg, k, Qp, skip):
    """Reflection point on face k of the unfolded segment Ximg -> Qp, if the path X -> P -> Qp is valid."""
    s = G["S"][k]
    n = np.asarray(s["n"], float)
    dv = Qp - Ximg
    den = n @ dv
    if abs(den) < 1e-12:
        return None
    t = (s["d"] - n @ Ximg) / den
    if not 1e-9 < t < 1 - 1e-9:
        return None
    P = Ximg + t * dv
    if not in_surface(s, P) or occluded(G, X, P, (k,)) or occluded(G, P, Qp, (k,) + tuple(skip)):
        return None
    return P


def diffract(G, E, S, R, c, Rmat, air, bands, t_max=None, refl_order=0):
    """Diffracted arrivals at receiver R from source S.
    refl_order=1 adds the paths with one specular reflection before and/or after the edge (image source / image
    receiver; faces whose plane holds the edge are left out, their reflections are part of the UTD terms).
    Rmat(face) -> amplitude reflection factors per band (len(bands)); air: energy attenuation per metre per band.
    Returns list of dicts {d, t, h (unit vector R -> apex, world), e (unit vector S -> apex), ga (band amplitude factor:
    air), D (complex p_d on DF, without delay), eb (band energy incl. interference with the boundary partners)}."""
    S = np.asarray(S, float); R = np.asarray(R, float)
    bands = np.asarray(bands, float)
    BF = _band_freqs(bands)
    out = []
    combos = [(S, None, R, None)]
    if refl_order >= 1:
        imS = [(k, _mirror(G, S, k)) for k in range(len(G["S"]))]
        imR = [(k, _mirror(G, R, k)) for k in range(len(G["S"]))]
        imS = [(k, X) for k, X in imS if X is not None]
        imR = [(k, X) for k, X in imR if X is not None]
        combos += [(X, k, R, None) for k, X in imS] + [(S, None, X, k) for k, X in imR]
        combos += [(X, k, Y, j) for k, X in imS for j, Y in imR]
    for e, (S1, ks, R1, kr) in ((e, cb) for e in E for cb in combos):
        if any(k is not None and (k in (e["i0"], e["i1"]) or _on_plane(G, k, e)) for k in (ks, kr)):
            continue
        t, a = e["t"], e["a"]
        zs, zr = (S1 - a) @ t, (R1 - a) @ t
        ws, wr = (S1 - a) - zs * t, (R1 - a) - zr * t
        rs, rr = np.linalg.norm(ws), np.linalg.norm(wr)
        if rs < 1e-6 or rr < 1e-6:
            continue
        z = zs + (zr - zs) * rs / (rs + rr)
        if z < -1e-9 or z > (e["b"] - a) @ t + 1e-9:
            continue
        Qp = a + z * t
        s0, s1 = float(np.linalg.norm(S1 - Qp)), float(np.linalg.norm(R1 - Qp))
        L = s0 + s1
        if t_max is not None and L / c > t_max:
            continue
        n, t0, n0 = e["n"], e["t0"], e["n0"]
        ph0, ph = _angle(ws, t0, n0), _angle(wr, t0, n0)
        if ph0 > n * math.pi + 1e-9 or ph > n * math.pi + 1e-9:
            continue
        skip = (e["i0"], e["i1"])
        Ps = Pr = None
        if ks is not None:
            Ps = _via(G, S, S1, ks, Qp, skip)
            if Ps is None:
                continue
        elif occluded(G, S, Qp, skip):
            continue
        if kr is not None:
            Pr = _via(G, R, R1, kr, Qp, skip)
            if Pr is None:
                continue
        elif occluded(G, Qp, R, skip):
            continue
        sinb = rs / s0
        R0b, Rnb = np.asarray(Rmat(e["i0"]), float), np.asarray(Rmat(e["i1"]), float)
        lb = np.log(bands)
        R0f = np.interp(np.log(DF), lb, R0b); Rnf = np.interp(np.log(DF), lb, Rnb)
        D = utd(n, ph, ph0, s1, s0, sinb, DF, c, R0f, Rnf)
        ga = np.exp(-0.5 * np.asarray(air, float) * L)
        refl = [k for k in (ks, kr) if k is not None]
        for k in refl:
            ga = ga * np.asarray(Rmat(k), float)
        # band energy with the interference with the geometrical arrivals of the same boundaries (plain paths only)
        partners = []
        if not refl and not occluded(G, S, R):
            partners.append((float(np.linalg.norm(R - S)), np.ones(len(bands))))
        for k in (skip if not refl else ()):
            r = _refl(G, S, R, k, np.asarray(Rmat(k), float))
            if r:
                partners.append(r)
        eb, ed = np.zeros(len(bands)), np.zeros(len(bands))
        for b, fb in enumerate(BF):
            Db = utd(n, ph, ph0, s1, s0, sinb, fb, c, np.interp(np.log(fb), lb, R0b), np.interp(np.log(fb), lb, Rnb))
            acc = np.abs(Db) ** 2
            ed[b] = float(np.mean(acc)) * ga[b] ** 2
            for Lp, Gp in partners:
                acc = acc + 2 * np.real(Gp[b] / Lp * np.exp(-2j * np.pi * fb * (Lp - L) / c) * np.conj(Db))
            eb[b] = float(np.mean(acc)) * ga[b] ** 2
        first, last = (Ps if Ps is not None else Qp), (Pr if Pr is not None else Qp)
        out.append(dict(d=L, t=L / c, h=(last - R) / np.linalg.norm(last - R), e=(first - S) / np.linalg.norm(first - S),
                        ga=ga, D=D, eb=eb, g=np.sqrt(ed), edge=(e["i0"], e["i1"]), refl=refl))
    return out


# ---------------------------------------------------------------- second order: two edges in sequence
GRAZE = 1e-6                    # incidence within this angle (rad) of a face counts as grazing


def _keller(a, t, lo_hi, X, Y):
    """Point on the line a + z t (z in lo_hi) on the shortest path X -> point -> Y (Keller cone): z or None."""
    zx, zy = (X - a) @ t, (Y - a) @ t
    rx = np.linalg.norm((X - a) - zx * t)
    ry = np.linalg.norm((Y - a) - zy * t)
    if rx + ry < 1e-12:
        return None
    return zx + (zy - zx) * rx / (rx + ry)


def _pair_points(e1, e2, S, R, iters=60):
    """Apex points Q1 on e1 and Q2 on e2 of the shortest path S -> Q1 -> Q2 -> R (the path length is convex in the
    two edge coordinates; alternating Keller-cone updates converge to its minimum). None if outside the edges."""
    a1, t1, L1 = e1["a"], e1["t"], float((e1["b"] - e1["a"]) @ e1["t"])
    a2, t2, L2 = e2["a"], e2["t"], float((e2["b"] - e2["a"]) @ e2["t"])
    z2 = 0.5 * L2
    z1 = 0.5 * L1
    for _ in range(iters):
        Q2 = a2 + z2 * t2
        n1 = _keller(a1, t1, None, S, Q2)
        if n1 is None:
            return None
        n1 = min(max(n1, -1.0), L1 + 1.0)        # keep the iteration bounded; checked below
        Q1 = a1 + n1 * t1
        n2 = _keller(a2, t2, None, Q1, R)
        if n2 is None:
            return None
        n2 = min(max(n2, -1.0), L2 + 1.0)
        done = abs(n1 - z1) < 1e-7 and abs(n2 - z2) < 1e-7
        z1, z2 = n1, n2
        if done:
            break
    if not (-1e-9 <= z1 <= L1 + 1e-9 and -1e-9 <= z2 <= L2 + 1e-9):
        return None
    return a1 + z1 * t1, a2 + z2 * t2


def _edge_angles(e, X, Y):
    """(phi of Y, phi0 of X, sin beta0) at edge e for a ray X -> apex -> Y; None if X or Y is on the edge line."""
    a, t = e["a"], e["t"]
    wx = (X - a) - ((X - a) @ t) * t
    wy = (Y - a) - ((Y - a) @ t) * t
    if np.linalg.norm(wx) < 1e-9 or np.linalg.norm(wy) < 1e-9:
        return None
    return _angle(wy, e["t0"], e["n0"]), _angle(wx, e["t0"], e["n0"])


def diffract2(G, E, S, R, c, Rmat, air, bands, t_max=None, refl_order=0):
    """Second-order diffracted arrivals S -> edge 1 -> edge 2 -> R (e.g. over a thick obstacle), UTD applied to
    the sequence of edges (Kouyoumjian & Pathak 1974; Tsingos et al. 2001 use UTD on sequences of diffracting
    edges, https://doi.org/10.1145/383259.383323):

        p = D1 D2 / sqrt(s0 s1 s2 (s0 + s1 + s2)) * exp(-j k (s0 + s1 + s2)) [* 1/2 at grazing incidence on edge 2]

    D1 with source distance s0 and observation distance s1 (the second apex), D2 with the unfolded source distance
    s0 + s1 and observation distance s2: the field diffracted by edge 1 is treated as a spherical wave from the image
    of the source along the unfolded path (an approximation: the diffracted ray has a caustic at edge 1). When the
    ray from edge 1 runs along a face of edge 2 (the top of a thick barrier: grazing incidence) the hard-face
    coefficient is halved, Kouyoumjian & Pathak, NASA CR-2401 (1974),
    https://ntrs.nasa.gov/api/citations/19740020597/downloads/19740020597.pdf, sec. III.A. Paths whose apex
    points fall outside the edges are not counted (no end-point diffraction). refl_order=1 adds one specular
    reflection before edge 1 and / or after edge 2 (image source / receiver), as in diffract().
    Not a uniform double-diffraction solution: near grazing over both edges each receiver lies near the shadow
    boundaries of both, where double-diffraction transition functions would be needed (Albani et al. 1995); checked
    against BRAS RS6 (validation/bras_rs.md), including a receiver 8 cm above the line of the top.
    Returns arrivals in the format of diffract()."""
    S = np.asarray(S, float); R = np.asarray(R, float)
    bands = np.asarray(bands, float)
    BF = _band_freqs(bands)
    lb = np.log(bands)
    air = np.asarray(air, float)
    combos = [(S, None, R, None)]
    if refl_order >= 1:
        imS = [(k, _mirror(G, S, k)) for k in range(len(G["S"]))]
        imR = [(k, _mirror(G, R, k)) for k in range(len(G["S"]))]
        imS = [(k, X) for k, X in imS if X is not None]
        imR = [(k, X) for k, X in imR if X is not None]
        combos += [(X, k, R, None) for k, X in imS] + [(S, None, X, k) for k, X in imR]
        combos += [(X, k, Y, j) for k, X in imS for j, Y in imR]
    out = []
    for i1, e1 in enumerate(E):
        for i2, e2 in enumerate(E):
            if i1 == i2:
                continue
            for S1, ks, R1, kr in combos:
                if ks is not None and (ks in (e1["i0"], e1["i1"]) or _on_plane(G, ks, e1)):
                    continue
                if kr is not None and (kr in (e2["i0"], e2["i1"]) or _on_plane(G, kr, e2)):
                    continue
                pp = _pair_points(e1, e2, S1, R1)
                if pp is None:
                    continue
                Q1, Q2 = pp
                s0, s1, s2 = (float(np.linalg.norm(S1 - Q1)), float(np.linalg.norm(Q2 - Q1)),
                              float(np.linalg.norm(R1 - Q2)))
                if min(s0, s1, s2) < 1e-6:
                    continue
                L = s0 + s1 + s2
                if t_max is not None and L / c > t_max:
                    continue
                g1, g2 = _edge_angles(e1, S1, Q2), _edge_angles(e2, Q1, R1)
                if g1 is None or g2 is None:
                    continue
                (ph1, ph01), (ph2, ph02) = g1, g2
                if max(ph1, ph01) > e1["n"] * math.pi + 1e-9 or max(ph2, ph02) > e2["n"] * math.pi + 1e-9:
                    continue
                sk1, sk2 = (e1["i0"], e1["i1"]), (e2["i0"], e2["i1"])
                Ps = Pr = None
                if ks is not None:
                    Ps = _via(G, S, S1, ks, Q1, sk1)
                    if Ps is None:
                        continue
                elif occluded(G, S, Q1, sk1):
                    continue
                if kr is not None:
                    Pr = _via(G, R, R1, kr, Q2, sk2)
                    if Pr is None:
                        continue
                elif occluded(G, Q2, R, sk2):
                    continue
                if occluded(G, Q1, Q2, sk1 + sk2):
                    continue
                sinb1 = float(np.linalg.norm(np.cross(Q1 - S1, e1["t"]))) / s0
                sinb2 = float(np.linalg.norm(np.cross(Q2 - Q1, e2["t"]))) / s1
                graze = 0.5 if min(ph02, e2["n"] * math.pi - ph02) < GRAZE else 1.0
                R01, Rn1 = np.asarray(Rmat(e1["i0"]), float), np.asarray(Rmat(e1["i1"]), float)
                R02, Rn2 = np.asarray(Rmat(e2["i0"]), float), np.asarray(Rmat(e2["i1"]), float)
                A = graze / math.sqrt(s0 * s1 * s2 * L)

                def coef(fr):
                    lf = np.log(fr)
                    d1 = utd(e1["n"], ph1, ph01, s1, s0, sinb1, fr, c, np.interp(lf, lb, R01), np.interp(lf, lb, Rn1))
                    d1 = d1 * math.sqrt(s1 * s0 * (s1 + s0))           # strip the first-order spreading
                    s0b = s0 + s1
                    d2 = utd(e2["n"], ph2, ph02, s2, s0b, sinb2, fr, c, np.interp(lf, lb, R02), np.interp(lf, lb, Rn2))
                    d2 = d2 * math.sqrt(s2 * s0b * (s2 + s0b))
                    return A * d1 * d2
                D = coef(DF)
                ga = np.exp(-0.5 * air * L)
                refl = [k for k in (ks, kr) if k is not None]
                for k in refl:
                    ga = ga * np.asarray(Rmat(k), float)
                ed = np.array([float(np.mean(np.abs(coef(fb)) ** 2)) for fb in BF]) * ga ** 2
                first, last = (Ps if Ps is not None else Q1), (Pr if Pr is not None else Q2)
                out.append(dict(d=L, t=L / c, h=(last - R) / np.linalg.norm(last - R),
                                e=(first - S) / np.linalg.norm(first - S), ga=ga, D=D, eb=ed, g=np.sqrt(ed),
                                edge=(e1["i0"], e1["i1"], e2["i0"], e2["i1"]), refl=refl, order=2))
    return out
