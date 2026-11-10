"""
Seat-dip transfer function of seat rows on a rigid floor by a two-dimensional boundary element method (BEM), after
the approach of Davies & Cox (2000), "Reducing seat dip attenuation", J. Acoust. Soc. Am. 108, 2211,
https://doi.org/10.1121/1.1314318 (2-D BEM of the cross-section through the seating, rigid surfaces, Helmholtz-
Kirchhoff integral equation with the 2-D Green's function, half-space image term for the floor).

transfer(bodies, S, R, f) returns T(f) = p(R) / p_free(R): the 2-D pressure at R with the rows and the floor present,
divided by the 2-D free-field pressure of the same line source (no floor, no rows). Applied to the 3-D direct sound
it replaces the direct sound and everything the floor and the rows add to it near grazing incidence ("2.5-D"
approximation: valid when the paths that matter are close in length to the direct path, as for sound passing low
over the rows; an engineering assumption checked against the BRAS RS7 measurements, validation/bras_rs.py).

Geometry: a vertical cross-section, coordinates (u, z): u along the floor (in the direction of the path), z up, the
floor at z = 0 rigid. bodies = list of closed polygons (counter-clockwise in (u, z)) standing on or above the floor;
edges lying on the floor are left out (they touch the rigid floor). Constant elements, collocation at the element
centres, element length <= wavelength / ELEM_PER_WL.
"""
import numpy as np
from scipy.special import hankel1

ELEM_PER_WL = 8
NQ = 4                                   # Gauss points per element (off-diagonal)
_GX, _GW = np.polynomial.legendre.leggauss(NQ)


def _mesh(bodies, h):
    """Elements of all polygon edges not on the floor: centres [N, 2], normals (out of the body) [N, 2], Gauss points
    [N, NQ, 2], weights [N, NQ]."""
    P, Nn, Q, W = [], [], [], []
    for poly in bodies:
        poly = np.asarray(poly, float)
        if np.cross(poly[1] - poly[0], poly[2] - poly[1]) < 0:   # make counter-clockwise
            poly = poly[::-1]
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            if abs(a[1]) < 1e-9 and abs(b[1]) < 1e-9:
                continue                                         # on the floor
            L = float(np.linalg.norm(b - a))
            m = max(1, int(np.ceil(L / h)))
            t = (b - a) / L
            nrm = np.array([t[1], -t[0]])                        # outward for a counter-clockwise polygon
            for j in range(m):
                p0, p1 = a + (b - a) * j / m, a + (b - a) * (j + 1) / m
                P.append((p0 + p1) / 2)
                Nn.append(nrm)
                Q.append((p0 + p1) / 2 + np.outer(_GX, (p1 - p0) / 2))
                W.append(_GW * L / m / 2)
    return np.array(P), np.array(Nn), np.array(Q), np.array(W)


def _dGdn(k, X, Y, NY):
    """d/dn_y of the half-space Green's function G = i/4 [H0(k|x-y|) + H0(k|x-y'|)], y' = (y_u, -y_z), for points X
    [..., 2], Y [..., 2], normals NY [..., 2] (broadcast)."""
    out = 0
    for sgn in (1, -1):
        Ym = Y * np.array([1, sgn])
        Nm = NY * np.array([1, sgn])
        d = X - Ym
        r = np.sqrt((d ** 2).sum(-1))
        out = out + 0.25j * k * hankel1(1, k * r) * (d * Nm).sum(-1) / r
    return out


def _G(k, X, Y):
    out = 0
    for sgn in (1, -1):
        d = X - Y * np.array([1, sgn])
        out = out + 0.25j * hankel1(0, k * np.sqrt((d ** 2).sum(-1)))
    return out


def transfer(bodies, S, R, f, c=343.0, fmin_mesh=None):
    """T(f) at receiver(s) R ([2] or [M, 2]) for source S ([2]); f array (Hz). Returns [len(f)] or [len(f), M]."""
    S = np.asarray(S, float)
    R = np.atleast_2d(np.asarray(R, float))
    out = np.zeros((len(f), len(R)), complex)
    cache = {}
    for i, fi in enumerate(f):
        k = 2 * np.pi * fi / c
        h = c / max(fi, fmin_mesh or 0) / ELEM_PER_WL
        key = int(np.ceil(np.log2(1 / h) * 4))                  # reuse meshes in quarter-octave steps of h
        if key not in cache:
            cache[key] = _mesh(bodies, 2 ** (-key / 4))
        P, Nn, Q, W = cache[key]
        n = len(P)
        if n:
            # (1/2) p(x) - sum_j p_j int dG/dn_y dy = p_inc(x)   (rigid bodies, normals into the fluid)
            K = (_dGdn(k, P[:, None, None, :], Q[None, :, :, :], Nn[None, :, None, :]) * W[None, :, :]).sum(-1)
            A = 0.5 * np.eye(n) - K
            pinc = _G(k, P, S[None, :])
            p = np.linalg.solve(A, pinc)
            KR = (_dGdn(k, R[:, None, None, :], Q[None, :, :, :], Nn[None, :, None, :]) * W[None, :, :]).sum(-1)
            pR = _G(k, R, S[None, :]) + KR @ p
        else:
            pR = _G(k, R, S[None, :])
        dfree = np.sqrt(((R - S) ** 2).sum(-1))
        out[i] = pR / (0.25j * hankel1(0, k * dfree))
    return out[:, 0] if out.shape[1] == 1 else out
