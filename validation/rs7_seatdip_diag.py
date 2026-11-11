"""
Diagnostics for the lower edge of the seat dip in BRAS RS7 (Aspoeck et al., https://doi.org/10.14279/depositonce-6726.3,
CC BY-SA 4.0; block dimensions from the BRAS documentation, p. 22: 15 blocks 0.24 m high, 0.12 m deep, 4.1 m wide,
12 mm MDF, gaps 0.22 m). The rigid 2-D model gives a deep notch (-20 ... -40 dB) at 260 - 330 Hz that the measurement
does not show. This script computes, for one source-receiver pair and all 15 blocks:

    python validation/rs7_seatdip_diag.py three-d LS2-MP3 300,400        3-D point source vs 2-D line source
    python validation/rs7_seatdip_diag.py impedance LS2-MP3 0.03          block surfaces with absorption alpha
    python validation/rs7_seatdip_diag.py panel LS2-MP3                   MDF walls (8.91 kg/m2) on the box cavity

three-d: the 3-D field of the same y-invariant rows by the 2.5-D transform p3D = 1/(2 pi) int p2D(kappa(ky)) dky,
kappa = sqrt(k^2 - ky^2); propagating part adaptive in ky = k sin(theta) (the integrand has sharp peaks from the
rows' resonances; fixed Gauss rules do not converge), evanescent part Gauss in ky = k cosh(u).
impedance / panel: locally reacting admittance beta on the blocks, (1/2) p - K p - i k beta S p = p_inc
(e^{-i w t}); panel: Z = -i w m + i rho c cot(k d), d = 0.096 m (inside of the box), beta = rho c / Z.
Checked: beta = 0 equals seatdip.transfer_rows; an impedance half-cylinder on a floor matches the series solution
within 1e-4 dB.
Results are levels re free field of the direct sound (dB), unsmoothed; slow (minutes per frequency for three-d).
"""
import math
import os
import sys

import numpy as np
from scipy.integrate import quad_vec
from scipy.special import hankel1

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import seatdip as sd     # noqa: E402

PAIRS = {"LS1": (3.187, 0.176), "LS2": (3.187, 0.52)}
MPS = {"MP1": (9.014, 0.337), "MP2": (9.014, 0.4), "MP3": (6.228, 0.337), "MP4": (6.228, 0.4)}
C = 331.3 * math.sqrt(1 + 19.2 / 273.15)      # RS7: 19.2 deg C
RHO = 1.204
H = 0.0156                                    # element length (seatdip.HMAX at the 1:3.2 model scale)
X0 = 3.958
SEAT = [(X0 - .06, 0), (X0 + .06, 0), (X0 + .06, .24), (X0 - .06, .24)]


class Rows:
    """Identical rows (block-Toeplitz assembly as seatdip.transfer_rows); scattered field for complex k."""
    def __init__(self, seat, m, du, S, R, h):
        self.seat, self.m, self.du, self.S, self.R = np.asarray(seat, float), list(m), du, np.asarray(S, float), np.asarray(R, float)
        sd.HMAX = h
        self.M = sd._mesh([self.seat], h)
        self.n = 0
    def p_scat(self, k):
        self.n += 1
        P0, N0, Q0, W0, A0, B0 = self.M
        ns, nr, m, du = len(P0), len(self.m), self.m, self.du
        blocks = {}
        for d in sorted({a - b for a in m for b in m}):
            sh = np.array([d * du, 0.0])
            Bd = (sd._dGdn(k, (P0 + sh)[:, None, None, :], Q0[None], N0[None, :, None, :]) * W0[None]).sum(-1)
            blocks[d] = sd._near_fix(Bd, k, P0 + sh, P0, N0, A0, B0)
        A = np.zeros((nr * ns, nr * ns), complex); rhs = np.zeros(nr * ns, complex)
        for p in range(nr):
            o = p * ns
            A[o:o + ns, o:o + ns] += 0.5 * np.eye(ns)
            rhs[o:o + ns] = sd._G(k, P0 + np.array([m[p] * du, 0.0]), self.S[None, :])
            for q in range(nr):
                A[o:o + ns, q * ns:(q + 1) * ns] -= blocks[m[p] - m[q]]
        x = np.linalg.solve(A, rhs)
        out = 0
        for q in range(nr):
            sh = np.array([m[q] * du, 0.0])
            KR = (sd._dGdn(k, self.R[None, None, :], Q0 + sh, N0[:, None, :]) * W0).sum(-1)[None, :]
            KR = sd._near_fix(KR, k, self.R[None, :], P0, N0, A0, B0, sh[0])[0]
            out = out + KR @ x[q * ns:(q + 1) * ns]
        return out

def T3(rows, f, c=C, epsrel=2e-3, nu=32):
    """3-D point source over the rows (2.5-D transform), re free field."""
    k = 2 * np.pi * f / c

    def g(t):
        kap = k * math.cos(t)
        v = kap * rows.p_scat(kap)
        return np.array([v.real, v.imag])
    v, _ = quad_vec(g, 0.0, np.pi / 2, epsrel=epsrel, epsabs=1e-6, limit=400)
    prop = 2 * (v[0] + 1j * v[1])
    umax = math.asinh(60 / (k * 0.09))
    uu, wu = np.polynomial.legendre.leggauss(nu)
    uu, wu = (uu + 1) * umax / 2, wu * umax / 2
    ev = sum(2 * w * k * math.sinh(u) * rows.p_scat(1j * k * math.sinh(u)) for u, w in zip(uu, wu))
    S, R = rows.S, rows.R
    d, di = np.hypot(*(R - S)), np.hypot(R[0] - S[0], R[1] + S[1])
    pinc = np.exp(1j * k * d) / (4 * np.pi * d) + np.exp(1j * k * di) / (4 * np.pi * di)
    return (pinc + (prop + ev) / (2 * np.pi)) / (np.exp(1j * k * d) / (4 * np.pi * d))


def T2(rows, f, c=C):
    k = 2 * np.pi * f / c
    S, R = rows.S, rows.R
    return (sd._G(k, R[None, :], S[None, :])[0] + rows.p_scat(k)) / (0.25j * hankel1(0, k * np.hypot(*(R - S))))


EUL = 0.5772156649015329

def S_mat(k, X, P, Q, W, A, B, N, sh=0.0, self_rows=None):
    """Single layer: S[i, j] = int_j G(X_i, y) dy (G with floor image)."""
    Sm = (sd._G(k, X[:, None, None, :], (Q + np.array([sh, 0.0]))[None]) * W[None]).sum(-1)
    L = np.hypot(*(B - A).T)
    d = np.hypot(X[:, None, 0] - (P[None, :, 0] + sh), X[:, None, 1] - P[None, :, 1])
    t = ((np.arange(16)[:, None] + (sd._GX[None, :] + 1) / 2) / 16).ravel()
    for i, j in zip(*np.nonzero(d < sd.NEAR * L[None, :])):
        Y = A[j] + np.outer(t, B[j] - A[j]) + np.array([sh, 0.0]); w = np.tile(sd._GW / 2, 16) * L[j] / 16
        if d[i, j] < 1e-9:   # self element: direct part analytically (small-argument H0), image part numerically
            Lj = L[j]
            direct = 0.25j * Lj * (1 + 2j / np.pi * (np.log(k * Lj / 4) + EUL - 1))
            Ym = Y * np.array([1, -1]); r = np.hypot(*(X[i] - Ym).T)
            Sm[i, j] = direct + (0.25j * hankel1(0, k * r) * w).sum()
        else:
            Sm[i, j] = (sd._G(k, X[i][None, :], Y) * w).sum()
    return Sm

def T_imp(seat, mlist, du, S, R, f, c, beta, h=H):
    """Rows with admittance beta on the block surfaces (floor rigid), re free field."""
    sd.HMAX = h
    S, R = np.asarray(S, float), np.asarray(R, float)
    P0, N0, Q0, W0, A0, B0 = sd._mesh([np.asarray(seat, float)], h)
    ns, nr = len(P0), len(mlist); k = 2 * np.pi * f / c
    A = np.zeros((nr * ns, nr * ns), complex); rhs = np.zeros(nr * ns, complex)
    blocks = {}
    for d in sorted({a - b for a in mlist for b in mlist}):
        sh = np.array([d * du, 0.0])
        K = (sd._dGdn(k, (P0 + sh)[:, None, None, :], Q0[None], N0[None, :, None, :]) * W0[None]).sum(-1)
        K = sd._near_fix(K, k, P0 + sh, P0, N0, A0, B0)
        Sd = S_mat(k, P0 + sh, P0, Q0, W0, A0, B0, N0)
        blocks[d] = K + 1j * k * beta * Sd
    for p in range(nr):
        o = p * ns; A[o:o+ns, o:o+ns] += 0.5 * np.eye(ns)
        rhs[o:o+ns] = sd._G(k, P0 + np.array([mlist[p] * du, 0.0]), S[None, :])
        for q in range(nr): A[o:o+ns, q*ns:(q+1)*ns] -= blocks[mlist[p] - mlist[q]]
    x = np.linalg.solve(A, rhs)
    pR = sd._G(k, R[None, :], S[None, :])[0]
    for q in range(nr):
        sh = mlist[q] * du
        KR = (sd._dGdn(k, R[None, None, :], Q0 + np.array([sh, 0.0]), N0[:, None, :]) * W0).sum(-1)[None, :]
        KR = sd._near_fix(KR, k, R[None, :], P0, N0, A0, B0, sh)[0]
        SR = S_mat(k, R[None, :], P0, Q0, W0, A0, B0, N0, sh)[0]
        pR = pR + (KR + 1j * k * beta * SR) @ x[q*ns:(q+1)*ns]
    return pR / (0.25j * hankel1(0, k * np.hypot(*(R - S))))


def main():
    mode, pair = sys.argv[1], sys.argv[2]
    S, R = PAIRS[pair[:3]], MPS[pair[4:]]
    if mode == "three-d":
        rows = Rows(SEAT, range(15), 0.34, S, R, H)
        for f in [float(a) for a in sys.argv[3].split(",")]:
            print(f"{f:.0f} Hz: 2-D {20 * np.log10(abs(T2(rows, f))):+.1f} dB, 3-D {20 * np.log10(abs(T3(rows, f))):+.1f} dB",
                  flush=True)
        return
    freqs = np.arange(200, 610, 20.0)
    for f in freqs:
        w = 2 * np.pi * f
        if mode == "impedance":
            a = float(sys.argv[3])
            beta = (1 - math.sqrt(1 - a)) / (1 + math.sqrt(1 - a))
        else:
            beta = RHO * C / (-1j * w * 8.91 + 1j * RHO * C / math.tan(w / C * 0.096))
        T = T_imp(SEAT, range(15), 0.34, S, R, f, C, beta)
        print(f"{f:.0f} Hz: {20 * np.log10(abs(T)):+.1f} dB", flush=True)


if __name__ == "__main__":
    main()
