"""
Direction of arrival of the late sound field (drawn halls), for the directional late reverberation.

A small ray tracer (numpy, vectorised over rays; same model as GEOM.rays in engine_geom.js: rays of power 4 pi / N,
specular or Lambert reflection with probability equal to the scattering coefficient, energy (1 - alpha) per hit,
air absorption, receiver sphere of radius r with contribution e * chord / V_sphere; r = 1 m here, twice the
histogram receiver, because the direction statistics need more hits: seed-to-seed spread of the late ILD about
0.1 dB with 20 000 rays, against 0.3-0.4 dB at 0.5 m) that records, per receiver,
the energy arriving after t_late from each of 64 direction bins (Fibonacci sphere, head frame: x front = +y world,
y left = -x world, z up) in each octave band.

The overall late energy and its decay still come from the pyroomacoustics histogram (energy_hist); only the
direction distribution is taken from here (brir_proto.late_binaural).
"""
from __future__ import annotations

import math

import numpy as np

import diffraction

NBIN = 64


def fib_dirs(n=NBIN):
    """n unit vectors on a Fibonacci sphere (same sequence as GEOM.fibDirs)."""
    i = np.arange(n) + 0.5
    z = 1 - 2 * i / n
    ph = math.pi * (1 + math.sqrt(5)) * i
    r = np.sqrt(1 - z * z)
    return np.c_[r * np.cos(ph), r * np.sin(ph), z]


BINS = fib_dirs()


def world_to_head(u):
    u = np.atleast_2d(u)
    return np.c_[u[:, 1], -u[:, 0], u[:, 2]]


def _inside(s, P):
    """Point-in-polygon for many points P (K, 3) on the plane of surface s."""
    a, b = P[:, s["uv"][0]], P[:, s["uv"][1]]
    lo, hi = s["bb"]
    ok = (a >= lo[0]) & (a <= hi[0]) & (b >= lo[1]) & (b <= hi[1])
    if not ok.any():
        return ok
    c = np.zeros(len(P), bool)
    p2 = s["p2"]
    j = len(p2) - 1
    for i in range(len(p2)):
        xi, yi = p2[i]
        xj, yj = p2[j]
        with np.errstate(divide="ignore", invalid="ignore"):
            cr = ((yi > b) != (yj > b)) & (a < (xj - xi) * (b - yi) / (yj - yi) + xi)
        c ^= cr
        j = i
    return c & ok


def late_direction_energy(G, src, recs, t_late, alpha, scat, air, c=343.0, n_rays=20000, seed=1, t_max=2.5,
                          radius=1.0, max_bounce=400):
    """Energy per receiver, direction bin and band arriving after t_late[r] (seconds).
    alpha [n_surf, nb] absorption, scat [n_surf] scattering, air [nb] energy attenuation per metre.
    Returns W [n_rec, NBIN, nb]."""
    diffraction.prepare(G)
    Nn, Dp = G["N"], G["Dp"]
    nS = len(G["S"])
    alpha = np.asarray(alpha, float)
    Rpow = 1 - alpha
    nb = alpha.shape[1]
    air = np.asarray(air, float)
    recs = np.asarray(recs, float)
    t_late = np.asarray(t_late, float)
    rng = np.random.default_rng(seed)
    k = np.arange(n_rays)
    zc = 1 - 2 * (k + rng.random(n_rays)) / n_rays
    ph = 2 * math.pi * rng.random(n_rays)
    sr = np.sqrt(np.maximum(0, 1 - zc * zc))
    D = np.c_[sr * np.cos(ph), sr * np.sin(ph), zc]
    O = np.tile(np.asarray(src, float), (n_rays, 1))
    L = np.zeros(n_rays)
    e0 = 4 * math.pi / n_rays
    E = np.full((n_rays, nb), e0)
    last = np.full(n_rays, -1)
    alive = np.ones(n_rays, bool)
    W = np.zeros((len(recs), NBIN, nb))
    Vs, r2, Lmax = 4 / 3 * math.pi * radius ** 3, radius * radius, c * t_max
    binsW = np.c_[-BINS[:, 1], BINS[:, 0], BINS[:, 2]]          # bin centres in world coordinates
    for _ in range(max_bounce):
        idx = np.flatnonzero(alive)
        if not idx.size:
            break
        o, d = O[idx], D[idx]
        den = d @ Nn.T
        with np.errstate(divide="ignore", invalid="ignore"):
            T = (Dp[None, :] - o @ Nn.T) / den
        T[(den >= -1e-12) | ~(T > 1e-9)] = np.inf
        has = last[idx] >= 0
        T[np.flatnonzero(has), last[idx][has]] = np.inf
        best = np.full(idx.size, np.inf)
        bi = np.full(idx.size, -1)
        rem = np.arange(idx.size)
        for _it in range(nS):
            j = np.argmin(T[rem], axis=1)
            tj = T[rem, j]
            fin = np.isfinite(tj)
            rem, j, tj = rem[fin], j[fin], tj[fin]
            if not rem.size:
                break
            P = o[rem] + tj[:, None] * d[rem]
            ok = np.zeros(rem.size, bool)
            for s in np.unique(j):
                m = j == s
                ok[m] = _inside(G["S"][s], P[m])
            best[rem[ok]] = tj[ok]
            bi[rem[ok]] = j[ok]
            T[rem[~ok], j[~ok]] = np.inf
            rem = rem[~ok]
            if not rem.size:
                break
        hit = bi >= 0
        alive[idx[~hit]] = False
        idx, o, d, best, bi = idx[hit], o[hit], d[hit], best[hit], bi[hit]
        if not idx.size:
            break
        # receivers along the segments
        inc = np.argmax(-d @ binsW.T, axis=1)                     # incoming direction = -d
        for m, R in enumerate(recs):
            w = R - o
            tc = np.einsum("ij,ij->i", w, d)
            d2 = np.einsum("ij,ij->i", w, w) - tc * tc
            sel = d2 < r2
            if not sel.any():
                continue
            hc = np.sqrt(np.maximum(0, r2 - d2[sel]))
            ta = np.maximum(0, tc[sel] - hc)
            tb = np.minimum(best[sel], tc[sel] + hc)
            ok = tb > ta
            dist = L[idx[sel]][ok] + (ta[ok] + tb[ok]) / 2
            tt = dist / c
            late = (tt >= t_late[m]) & (tt < t_max)
            if not late.any():
                continue
            rows = np.flatnonzero(sel)[ok][late]
            en = E[idx[rows]] * np.exp(-np.outer(dist[late], air)) * ((tb[ok] - ta[ok])[late] / Vs)[:, None]
            np.add.at(W[m], inc[rows], en)
        L[idx] += best
        O[idx] = o + best[:, None] * d
        E[idx] *= Rpow[bi]
        dead = (L[idx] >= Lmax) | (E[idx].max(axis=1) < e0 * 1e-7)
        alive[idx[dead]] = False
        # reflection
        n0 = Nn[bi]
        diff = rng.random(idx.size) < np.asarray(scat, float)[bi]
        dn = np.einsum("ij,ij->i", d, n0)
        newd = d - 2 * dn[:, None] * n0
        if diff.any():
            nd = n0[diff]
            t1 = np.where(np.abs(nd[:, :1]) < 0.9, np.array([[1.0, 0, 0]]), np.array([[0, 1.0, 0]]))
            ax = np.cross(nd, t1)
            ax /= np.linalg.norm(ax, axis=1)[:, None]
            ay = np.cross(nd, ax)
            u1, u2 = rng.random(nd.shape[0]), rng.random(nd.shape[0])
            sq, phi = np.sqrt(u1), 2 * math.pi * u2
            newd[diff] = (sq * np.cos(phi))[:, None] * ax + (sq * np.sin(phi))[:, None] * ay + np.sqrt(np.maximum(0, 1 - u1))[:, None] * nd
        D[idx] = newd
        last[idx] = bi
    return W
