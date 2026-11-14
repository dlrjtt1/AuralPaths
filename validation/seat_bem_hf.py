"""
Seat-dip BEM with absorbing seat surfaces, up to 4 kHz (diagnostic for validation/opera_check.md).

The engine's seat-dip model (seatdip.py) solves rigid seat rows up to 1 kHz. This script solves the same 2-D
cross-section (seatdip.cross_section, the same seat shape and rows) with a locally reacting impedance on the
upholstered faces, at any frequency, and returns the octave-band energy of T = p / p_free on the direct path.

Integral equation (time convention exp(-i w t) as the Hankel functions of seatdip.py, normal n out of the body into
the fluid, normalised surface admittance beta = rho c / Z):
    dp/dn = -i k beta p    on the absorbing faces (0 on the rigid ones)
    p(x) / 2 - int p dG/dn_y dy - i k int beta G p dy = p_inc(x)
    p(R) = p_inc(R) + int p dG/dn_y dy + i k int beta G p dy
with the floor (z = 0, rigid) in the Green's function by an image term, as in seatdip.py. CHIEF points inside every
seat (seatdip.cross_section) against the interior resonances. Self element of the single layer: the small-argument
form of H0 integrated over the element; near elements: composite Gauss rule.

Absorbing faces (assumption, no source for the seats of a particular hall): the top of the seat pan, the front of the
seat back and the top of the back; the underside of the pan, the front edge of the pan and the rear of the back are
rigid. beta is real (frequency-dependent through the band's absorption coefficient), obtained from a statistical
(random-incidence) absorption coefficient by inverting the Paris formula for a real normalised impedance zeta; the
inversion has two roots (soft zeta < 1.6 and stiff zeta > 1.6), both are reported.

    python validation/seat_bem_hf.py <config_cal.json> --seats Row4_Seat145,... [--source Source2]
        [--alpha 0.64,0.64,0.63,0.64,0.74,0.66] [--nf 12] [--out out/opera_bem]
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
from scipy.special import hankel1
from scipy.optimize import brentq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, ".."), HERE]
import brir_proto as bp                       # noqa: E402
import seatdip as sd                          # noqa: E402

BANDS = [125, 250, 500, 1000, 2000, 4000]
GAMMA = 0.5772156649015329
# polygon edges of a seat in seatdip.cross_section order: 0 pan underside, 1 rear of back, 2 top of back,
# 3 front of back, 4 top of pan, 5 front edge of pan
ABSORBING_EDGES = (2, 3, 4)


def alpha_stat(zeta):
    """Random-incidence absorption of a locally reacting surface with real normalised impedance zeta (Paris)."""
    th = np.linspace(0, np.pi / 2, 2001)
    a = 4 * zeta * np.cos(th) / (zeta * np.cos(th) + 1) ** 2
    return float(np.trapezoid(a * np.sin(2 * th), th))


def zeta_from_alpha(alpha):
    """(soft, stiff) real normalised impedances with alpha_stat = alpha (alpha <= 0.95)."""
    zm = 1.567
    f = lambda z: alpha_stat(z) - alpha
    return brentq(f, 1e-3, zm), brentq(f, zm, 500.0)


def mesh(bodies, h, beta_abs):
    """Constant elements on the seat polygons (floor edges skipped): centres, normals, Gauss points, weights,
    element ends, admittance per element. Edge numbering follows the polygon as built by cross_section."""
    P, Nn, Q, W, A, B, Bt = [], [], [], [], [], [], []
    h = min(h, sd.HMAX)
    for poly in bodies:
        poly = np.asarray(poly, float)
        n = len(poly)
        a2 = sum(poly[i, 0] * poly[(i + 1) % n, 1] - poly[(i + 1) % n, 0] * poly[i, 1] for i in range(n))
        edges = [(poly[i], poly[(i + 1) % n], i) for i in range(n)]
        if a2 < 0:                                            # counter-clockwise, keep each edge's number
            edges = [(b, a, i) for a, b, i in edges[::-1]]
        for a, b, ei in edges:
            if abs(a[1]) < 1e-7 and abs(b[1]) < 1e-7:
                continue
            L = float(np.hypot(*(b - a)))
            if L < 1e-9:
                continue
            m = max(1, int(math.ceil(L / h - 1e-9)))
            t = (b - a) / L
            nrm = np.array([t[1], -t[0]])
            for j in range(m):
                p0, p1 = a + (b - a) * j / m, a + (b - a) * (j + 1) / m
                P.append((p0 + p1) / 2); Nn.append(nrm); A.append(p0); B.append(p1)
                Q.append((p0 + p1) / 2 + np.outer(sd._GX, (p1 - p0) / 2)); W.append(sd._GW * L / m / 2)
                Bt.append(beta_abs if ei in ABSORBING_EDGES else 0.0)
    return (np.array(P), np.array(Nn), np.array(Q), np.array(W), np.array(A), np.array(B), np.array(Bt))


def single_layer(k, X, P, Q, W, A, B):
    """S[i, j] = int over element j of G(X_i, y) dy, with the image term; self and near elements by a composite rule,
    the log singularity of the direct term on the own element analytically."""
    S = (sd._G(k, X[:, None, None, :], Q[None, :, :, :]) * W[None, :, :]).sum(-1)
    L = np.hypot(*(B - A).T)
    d = np.hypot(X[:, None, 0] - P[None, :, 0], X[:, None, 1] - P[None, :, 1])
    for i, j in zip(*np.nonzero(d < sd.NEAR * L[None, :])):
        if d[i, j] < 1e-9 * L[j]:                             # own element: direct term analytic, image term Gauss
            a = L[j] / 2
            direct = 0.25j * (2 * a + 2j / np.pi * (2 * a * (math.log(k * a / 2) - 1) + 2 * a * GAMMA))
            Ym = Q[j] * np.array([1, -1])
            img = (0.25j * hankel1(0, k * np.hypot(*(X[i] - Ym).T)) * W[j]).sum()
            S[i, j] = direct + img
        else:
            t = ((np.arange(sd.NSUB)[:, None] + (sd._GX[None, :] + 1) / 2) / sd.NSUB).ravel()
            Y = A[j] + np.outer(t, B[j] - A[j])
            w = np.tile(sd._GW / 2, sd.NSUB) * L[j] / sd.NSUB
            S[i, j] = (sd._G(k, X[i][None, :], Y) * w).sum()
    return S


def double_layer(k, X, P, Nn, Q, W, A, B):
    K = (sd._dGdn(k, X[:, None, None, :], Q[None, :, :, :], Nn[None, :, None, :]) * W[None, :, :]).sum(-1)
    return sd._near_fix(K, k, X, P, Nn, A, B)


def transfer(X, S2, R2, f, beta_abs, c=343.0):
    """T(f) = p(R) / p_free(R) for the cross-section X (seatdip.cross_section) with admittance beta_abs on the
    absorbing faces."""
    bodies = X["bodies"]
    # CHIEF points: the base seat's points shifted to every row (rows are the base shifted by m * du along u)
    chief = np.array([[cx + mm * X["du"], cz] for mm in X["m"] for cx, cz in X["chief"]])
    S2, R2 = np.asarray(S2, float), np.asarray(R2, float)
    out = np.zeros(len(f), complex)
    for i, fi in enumerate(f):
        k = 2 * np.pi * fi / c
        P, Nn, Q, W, A, B, Bt = mesh(bodies, c / fi / sd.EPW, beta_abs)
        K = double_layer(k, P, P, Nn, Q, W, A, B)
        Sm = single_layer(k, P, P, Q, W, A, B)
        M = 0.5 * np.eye(len(P)) - K - 1j * k * Sm * Bt[None, :]
        rhs = sd._G(k, P, S2[None, :])
        Kc = double_layer(k, chief, P, Nn, Q, W, A, B)
        Sc = single_layer(k, chief, P, Q, W, A, B)
        M = np.vstack([M, -Kc - 1j * k * Sc * Bt[None, :]])
        rhs = np.concatenate([rhs, sd._G(k, chief, S2[None, :])])
        p = np.linalg.lstsq(M, rhs, rcond=None)[0]
        KR = double_layer(k, R2[None, :], P, Nn, Q, W, A, B)
        SR = single_layer(k, R2[None, :], P, Q, W, A, B)
        pR = sd._G(k, R2[None, :], S2[None, :])[0] + (KR @ p)[0] + 1j * k * (SR * Bt[None, :] @ p)[0]
        out[i] = pR / (0.25j * hankel1(0, k * np.hypot(*(R2 - S2))))
    return out


def band_gain(X, band, beta, nf, c=343.0):
    """Mean |T|^2 over nf log-spaced frequencies in the octave band."""
    f = band * 2 ** np.linspace(-0.5, 0.5, nf + 2)[1:-1]
    return float(np.mean(np.abs(transfer(X, X["S2"], X["R2"], f, beta, c)) ** 2))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config"); ap.add_argument("--seats", required=True); ap.add_argument("--source", default="Source2")
    ap.add_argument("--alpha", default=None, help="absorption of the upholstered faces per band (default: the "
                    "calibrated seating absorption of the config, group 'aud')")
    ap.add_argument("--spacing", type=float, default=0.945); ap.add_argument("--nf", type=int, default=12)
    ap.add_argument("--bands", default="125,250,500,1000,2000,4000")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "opera_bem"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cfg = json.load(open(a.config))
    G = bp._geom(cfg)
    prm = sd.seat_params({"spacing": a.spacing})
    alpha = [float(x) for x in a.alpha.split(",")] if a.alpha else cfg["geometry"]["materials"]["aud"]["alpha"]
    bands = [int(b) for b in a.bands.split(",")]
    res = {}
    fn = os.path.join(a.out, f"bem_{a.source}.json")
    if os.path.exists(fn):
        res = json.load(open(fn))
    for seat in a.seats.split(","):
        X = sd.cross_section(G, cfg["sources"][a.source]["pos"], cfg["receivers"][seat], prm)
        if X is None:
            print(seat, "no seat rows in front"); continue
        for b in bands:
            key = f"{seat}|{b}"
            if key in res:
                continue
            al = alpha[BANDS.index(b)]
            zs = zeta_from_alpha(min(al, 0.95))
            t0 = time.time()
            g = {"rigid": band_gain(X, b, 0.0, a.nf)}
            for name, z in zip(("soft", "stiff"), zs):
                g[name] = band_gain(X, b, 1.0 / z, a.nf)
            g["alpha"], g["zeta"] = al, list(zs)
            res[key] = g
            json.dump(res, open(fn, "w"), indent=1)
            print(f"{seat} {b} Hz: rigid {10*np.log10(g['rigid']):+.1f} soft {10*np.log10(g['soft']):+.1f} "
                  f"stiff {10*np.log10(g['stiff']):+.1f} dB (alpha {al:.2f}, zeta {zs[0]:.2f}/{zs[1]:.2f}) "
                  f"{time.time()-t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
