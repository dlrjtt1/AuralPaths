"""
Seat-dip model: the direct sound over seat rows, from a two-dimensional boundary element method (BEM) of the
cross-section through the seating along the path, after the approach of Davies & Cox (2000), "Reducing seat dip
attenuation", J. Acoust. Soc. Am. 108(5), 2211-2218,
https://salford-repository.worktribe.com/output/1466149/reducing-seat-dip-attenuation (2-D BEM, rigid surfaces,
Helmholtz-Kirchhoff integral equation with the 2-D Green's function, image term for the floor). The same model runs
in the browser (engine_geom.js, seatTransfer); validation/check_seatdip_pyjs.py compares the two.

transfer(bodies, S, R, f) returns T(f) = p(R) / p_free(R): the 2-D pressure at R with the rows and the floor present,
divided by the 2-D free-field pressure of the same line source (no floor, no rows). Multiplied onto the 3-D direct
sound it stands for the direct sound and everything the floor and the rows add to it ("2.5-D" approximation:
engineering assumption, checked against the BRAS RS7 measurements in validation/rs7_seatdip_bem.py).

Cross-section of a hall (path_transfer): seats are generated from a few numbers (seat_params), because a drawing
rarely shows them. Row spacing comes from the user (or the treads of a drawn section); the rest are defaults:
  back   0.80 m  height of the seat back above the floor (Tahvanainen et al. 2020, Acta Acustica 4, 15,
                 https://doi.org/10.1051/aacus/2020016: back-rest heights 0.64 - 0.88 m full scale in their model)
  gap    0.10 m  open space under the seat (same study: 0, 0.10 and 0.24 m; a larger opening gives a shallower dip
                 at a higher frequency); presets closed 0, standard 0.10, open 0.24
  seat shape     one solid L per seat: pan 0.50 m deep with its top at 0.45 m, back 0.10 m thick (engineering
                 assumption; no source for a typical profile), rigid, unoccupied
Rows run parallel to the page x axis (to the stage front; params["normal"] gives the row normal in another frame,
e.g. a 3D model's own frame); a path at angle phi to the row normal sees the rows
stretched by 1 / cos(phi), limited to phi <= 60 deg. The audience floor under the path is replaced by its best-fit
line (raked floors become one inclined plane; steps are not modelled). The last ROWS_FRONT rows in front of the
listener, the listener's own row and ROWS_BACK rows behind are modelled. Above FMAX, T is the energy mean of |T|
over the last third octave below FMAX, with zero phase (crossfaded over that third octave). Elements are at most
HMAX long, and near-singular integrals use a composite rule; without both, low frequencies (one element per seat
face) gave spurious peaks of +50 dB. The 2-D model has rows of infinite width.
"""
import math

import numpy as np
from scipy.special import hankel1

EPW = 8                      # elements per wavelength
NQ = 2                       # Gauss points per element
FMAX = 1000.0                # Hz: highest frequency solved with the BEM
ROWS_FRONT = 8
ROWS_BACK = 1
COS_MIN = 0.5                # rows seen at more than 60 deg are treated as at 60 deg
PRESETS = {"closed": 0.0, "standard": 0.10, "open": 0.24}
DEFAULTS = {"spacing": 0.80, "back": 0.80, "gap": 0.10}
PAN_DEPTH, PAN_TOP, BACK_T, EAR_FWD = 0.50, 0.45, 0.10, 0.15
_GX, _GW = np.polynomial.legendre.leggauss(NQ)


def seat_params(spec):
    """Seat-dip settings from the config entry {"spacing", "preset" | "gap", "back"} with the defaults filled in."""
    p = dict(DEFAULTS)
    if spec.get("preset") in PRESETS:
        p["gap"] = PRESETS[spec["preset"]]
    for k in ("spacing", "back", "gap"):
        if spec.get(k) is not None:
            p[k] = float(spec[k])
    return p


HMAX = 0.05                  # m: longest element at low frequencies (half the size of the seat details)
NEAR = 2.3                   # collocation points closer than NEAR element lengths to an element's centre use
                             # (not a whole number: on a straight face the next-but-one centre is exactly 2 L away)
NSUB = 8                     # NSUB sub-intervals of NQ points each (near-singular integrals)


def _near_fix(K, k, X, P, Nn, A, B, sh=0.0):
    """Recompute K[i, j] (one row per point X[i], one column per element) for points near element j with a composite
    Gauss rule. A, B: element end points [N, 2]; sh: shift of the elements along u."""
    L = np.hypot(*(B - A).T)
    d = np.minimum(np.hypot(X[:, None, 0] - (P[None, :, 0] + sh), X[:, None, 1] - P[None, :, 1]),
                   np.hypot(X[:, None, 0] - (P[None, :, 0] + sh), X[:, None, 1] + P[None, :, 1]))   # or its floor image
    for i, j in zip(*np.nonzero(d < NEAR * L[None, :])):
        t = ((np.arange(NSUB)[:, None] + (_GX[None, :] + 1) / 2) / NSUB).ravel()
        Y = A[j] + np.outer(t, B[j] - A[j]) + np.array([sh, 0.0])
        w = np.tile(_GW / 2, NSUB) * L[j] / NSUB
        r = (_dGdn(k, X[i][None, :], Y, Nn[j][None, :]) * w).sum()
        K[i, j] = r
    return K


def _mesh(bodies, h):
    """Constant elements on all polygon edges not lying on the floor (z = 0); also returns the element ends."""
    P, Nn, Q, W, A, B = [], [], [], [], [], []
    h = min(h, HMAX)
    for poly in bodies:
        poly = np.asarray(poly, float)
        a2 = sum(poly[i, 0] * poly[(i + 1) % len(poly), 1] - poly[(i + 1) % len(poly), 0] * poly[i, 1]
                 for i in range(len(poly)))
        if a2 < 0:
            poly = poly[::-1]                                    # counter-clockwise
        n = len(poly)
        for i in range(n):
            a, b = poly[i], poly[(i + 1) % n]
            if abs(a[1]) < 1e-7 and abs(b[1]) < 1e-7:
                continue                                         # on the floor
            L = float(np.hypot(*(b - a)))
            if L < 1e-9:
                continue
            m = max(1, int(math.ceil(L / h - 1e-9)))              # no tie at whole numbers (0.5 m / 0.05 m)
            t = (b - a) / L
            nrm = np.array([t[1], -t[0]])                        # out of the body, into the fluid
            for j in range(m):
                p0, p1 = a + (b - a) * j / m, a + (b - a) * (j + 1) / m
                P.append((p0 + p1) / 2)
                Nn.append(nrm)
                Q.append((p0 + p1) / 2 + np.outer(_GX, (p1 - p0) / 2))
                W.append(_GW * L / m / 2)
                A.append(p0)
                B.append(p1)
    return np.array(P).reshape(-1, 2), np.array(Nn).reshape(-1, 2), np.array(Q).reshape(-1, NQ, 2), \
        np.array(W).reshape(-1, NQ), np.array(A).reshape(-1, 2), np.array(B).reshape(-1, 2)


def _dGdn(k, X, Y, NY):
    """d/dn_y of G = i/4 [H0(k|x-y|) + H0(k|x-y'|)], y' = mirror of y in the floor z = 0."""
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


def transfer(bodies, S, R, f, c=343.0, epw=None):
    """T(f) at receiver(s) R ([2] or [M, 2]) for source S ([2]); f array (Hz). Returns [len(f)] or [len(f), M]."""
    S = np.asarray(S, float)
    R = np.atleast_2d(np.asarray(R, float))
    out = np.zeros((len(f), len(R)), complex)
    for i, fi in enumerate(f):
        k = 2 * np.pi * fi / c
        P, Nn, Q, W, A_, B_ = _mesh(bodies, c / fi / (epw or EPW))
        if len(P):
            # (1/2) p(x) - sum_j p_j int dG/dn_y dy = p_inc(x)   (rigid bodies)
            K = (_dGdn(k, P[:, None, None, :], Q[None, :, :, :], Nn[None, :, None, :]) * W[None, :, :]).sum(-1)
            K = _near_fix(K, k, P, P, Nn, A_, B_)
            p = np.linalg.solve(0.5 * np.eye(len(P)) - K, _G(k, P, S[None, :]))
            KR = (_dGdn(k, R[:, None, None, :], Q[None, :, :, :], Nn[None, :, None, :]) * W[None, :, :]).sum(-1)
            KR = _near_fix(KR, k, R, P, Nn, A_, B_)
            pR = _G(k, R, S[None, :]) + KR @ p
        else:
            pR = _G(k, R, S[None, :])
        out[i] = pR / (0.25j * hankel1(0, k * np.sqrt(((R - S) ** 2).sum(-1))))
    return out[:, 0] if out.shape[1] == 1 else out


def transfer_rows(seat, m, du, S, R, f, c=343.0, chief=None):
    """transfer() for identical rows: the polygon `seat` shifted by m[p] * du along u for each row p. The kernel
    between two rows depends only on m[p] - m[q], so each block is computed once (same result as transfer()).
    chief: points inside `seat` where the interior field must vanish (CHIEF, Schenck 1968): the integral equation of
    a closed body has no unique solution at the interior resonance frequencies of the body (for a seat 0.5 x 0.8 m
    from about 300 Hz), and the result then changes by several dB with the mesh; the extra equations are solved in
    the least-squares sense."""
    seat = np.asarray(seat, float)
    S, R = np.asarray(S, float), np.asarray(R, float)
    C0 = np.asarray(chief, float).reshape(-1, 2) if chief is not None else np.zeros((0, 2))
    nc = len(C0)
    out = np.zeros(len(f), complex)
    m = list(m)
    nr = len(m)
    for i, fi in enumerate(f):
        k = 2 * np.pi * fi / c
        P0, N0, Q0, W0, A0, B0 = _mesh([seat], c / fi / EPW)
        ns = len(P0)
        blocks, cblocks = {}, {}
        for d in sorted({a - b for a in m for b in m}):
            sh = np.array([d * du, 0.0])
            Bd = (_dGdn(k, (P0 + sh)[:, None, None, :], Q0[None, :, :, :], N0[None, :, None, :]) * W0[None, :, :]).sum(-1)
            blocks[d] = _near_fix(Bd, k, P0 + sh, P0, N0, A0, B0)
            if nc:
                Cd = (_dGdn(k, (C0 + sh)[:, None, None, :], Q0[None, :, :, :], N0[None, :, None, :]) * W0[None, :, :]).sum(-1)
                cblocks[d] = _near_fix(Cd, k, C0 + sh, P0, N0, A0, B0)
        A = np.zeros((nr * (ns + nc), nr * ns), complex)
        rhs = np.zeros(nr * (ns + nc), complex)
        for p in range(nr):
            o = p * ns
            A[o:o + ns, o:o + ns] += 0.5 * np.eye(ns)
            rhs[o:o + ns] = _G(k, P0 + np.array([m[p] * du, 0.0]), S[None, :])
            for q in range(nr):
                A[o:o + ns, q * ns:(q + 1) * ns] -= blocks[m[p] - m[q]]
            if nc:                               # interior points: -K p = p_inc there
                oc = nr * ns + p * nc
                rhs[oc:oc + nc] = _G(k, C0 + np.array([m[p] * du, 0.0]), S[None, :])
                for q in range(nr):
                    A[oc:oc + nc, q * ns:(q + 1) * ns] -= cblocks[m[p] - m[q]]
        x = np.linalg.solve(A, rhs) if not nc else np.linalg.lstsq(A, rhs, rcond=None)[0]
        pR = _G(k, R[None, :], S[None, :])[0]
        for q in range(nr):
            sh = np.array([m[q] * du, 0.0])
            KR = (_dGdn(k, R[None, None, :], Q0 + sh, N0[:, None, :]) * W0).sum(-1)[None, :]
            KR = _near_fix(KR, k, R[None, :], P0, N0, A0, B0, sh[0])[0]
            pR = pR + KR @ x[q * ns:(q + 1) * ns]
        out[i] = pR / (0.25j * hankel1(0, k * np.hypot(*(R - S))))
    return out


# ---------------------------------------------------------------- hall cross-section
def floor_at(G, x, y, z_from):
    """Highest upward-facing surface below z_from at (x, y): (z, mat) or None."""
    best = None
    for s in G["S"]:
        n = np.asarray(s["n"], float)
        if n[2] < 0.2:
            continue
        v0 = np.asarray(s["verts"][0], float)
        z = v0[2] - (n[0] * (x - v0[0]) + n[1] * (y - v0[1])) / n[2]
        if z >= z_from - 1e-9 or (best is not None and z <= best[0]):
            continue
        if _in_face(s, (x, y, z)):
            best = (z, s["mat"])
    return best


def _in_face(s, p):
    """Point (on the face plane) inside the face polygon: crossing test in the projection that drops the largest
    normal component."""
    v = np.asarray(s["verts"], float)
    n = np.abs(np.asarray(s["n"], float))
    ax = [i for i in range(3) if i != int(np.argmax(n))]
    x, y = p[ax[0]], p[ax[1]]
    c = False
    j = len(v) - 1
    for i in range(len(v)):
        xi, yi, xj, yj = v[i][ax[0]], v[i][ax[1]], v[j][ax[0]], v[j][ax[1]]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def cross_section(G, S, R, params):
    """2-D seat-row geometry along the path S -> R: dict(bodies, S2, R2, rows) or None when the receiver is not
    seated above an audience floor or no row lies in front of it."""
    S, R = [float(x) for x in S], [float(x) for x in R]
    vx, vy = R[0] - S[0], R[1] - S[1]
    Lh = math.hypot(vx, vy)
    if Lh < 1.0:
        return None
    dr = (vx / Lh, vy / Lh)
    nrm = params.get("normal", (0.0, 1.0))                                 # row normal in the plan (page frame: +y)
    cs = max(abs(dr[0] * nrm[0] + dr[1] * nrm[1]), COS_MIN)
    d_eff, depth, thick, fwd = params["spacing"] / cs, PAN_DEPTH / cs, BACK_T / cs, EAR_FWD / cs
    zl = lambda s: S[2] + (R[2] - S[2]) * s / Lh                            # height of the path

    def aud(s):
        q = floor_at(G, S[0] + dr[0] * s, S[1] + dr[1] * s, zl(s))
        return q[0] if q and q[1] == "aud" else None

    zr = aud(Lh)
    if zr is None or R[2] - zr > 2.5:
        return None
    own = Lh + fwd                                                          # rear of the listener's own row
    rows = []
    for k in range(ROWS_FRONT + 1):
        sb = own - k * d_eff
        if sb - depth < 0.5 or aud(sb) is None or aud(sb - depth) is None:
            break
        rows.append(sb)
    if len(rows) < 2:
        return None
    for j in range(1, ROWS_BACK + 1):
        sb = own + j * d_eff
        if aud(sb) is None or aud(sb - depth) is None:
            break
        rows.append(sb)
    s0, s1 = min(rows) - depth - 0.3, max(rows) + 0.05
    ns = max(3, int(math.ceil((s1 - s0) / 0.1)) + 1)
    ss = [s0 + (s1 - s0) * i / (ns - 1) for i in range(ns)]      # same arithmetic as the browser engine
    zz = [aud(s) for s in ss]
    pts = [(s, z) for s, z in zip(ss, zz) if z is not None]
    if len(pts) < 3:
        return None
    n, sx, sz, sxx, sxz = len(pts), 0.0, 0.0, 0.0, 0.0
    for s, z in pts:
        sx, sz, sxx, sxz = sx + s, sz + z, sxx + s * s, sxz + s * z
    b = (n * sxz - sx * sz) / (n * sxx - sx * sx)                         # least-squares line
    a = (sz - b * sx) / n
    cb, sb_ = 1 / math.sqrt(1 + b * b), b / math.sqrt(1 + b * b)

    def rot(s, z):                                                          # line z = a + b s -> w = 0
        return (s * cb + (z - a) * sb_, -s * sb_ + (z - a) * cb)

    sb0 = rows[0]
    span_pan, span_back = PAN_TOP - params["gap"], params["back"] - params["gap"]
    chief_rel = [(sb0 - depth + 0.37 * (depth - thick), params["gap"] + 0.41 * span_pan),
                 (sb0 - depth + 0.71 * (depth - thick), params["gap"] + 0.67 * span_pan),
                 (sb0 - 0.43 * thick, params["gap"] + 0.29 * span_back),
                 (sb0 - 0.61 * thick, params["gap"] + 0.77 * span_back)]
    bodies = []
    for sbk in rows:
        rel = [(sbk - depth, params["gap"]), (sbk, params["gap"]), (sbk, params["back"]), (sbk - thick, params["back"]),
               (sbk - thick, PAN_TOP), (sbk - depth, PAN_TOP)]
        bodies.append([rot(s, a + b * s + h) for s, h in rel])
    S2, R2 = rot(0.0, S[2]), rot(Lh, R[2])
    if S2[1] < 0.05 or R2[1] < 0.05:
        return None
    # every row is the same polygon shifted along u by a whole number of row pitches: the listener's own row is the
    # base, row k sits at m = (its rear - own) / d_eff pitches
    du = rot(own + d_eff, a + b * (own + d_eff))[0] - rot(own, a + b * own)[0]
    m = [int(round((sbk - own) / d_eff)) for sbk in rows]
    chief = [rot(s, a + b * s + h) for s, h in chief_rel]                   # inside the listener's own seat
    return dict(bodies=bodies, S2=S2, R2=R2, rows=len(rows), seat=bodies[0], m=m, du=du, chief=chief)


NFFT = 2048                  # T is given on the bins of a 2048-point FFT (23 Hz at 48 kHz): with 1024 points the
                             # row resonances wrap around (BRAS RS7 at full-scale-equivalent resolution: mean
                             # abs. difference 5.1 dB with 1024 points, 4.0 dB with 2048)
PRE = NFFT // 8              # samples before the arrival in the FIR (fir), for the non-causal part of T


def bins(fs, nfft=NFFT):
    """Renderer frequency bins solved with the BEM (1 .. FMAX)."""
    k = np.arange(1, int(FMAX * nfft / fs) + 1)
    return k * fs / nfft


def path_transfer(G, S, R, params, fs, c, nfft=NFFT):
    """Complex T on the renderer's bins 0 .. nfft/2 (array of nfft/2 + 1), or None (no seat dip on this path)."""
    X = cross_section(G, S, R, params)
    if X is None:
        return None
    fb = bins(fs, nfft)
    T = transfer_rows(X["seat"], X["m"], X["du"], X["S2"], X["R2"], fb, c)
    nb = nfft // 2 + 1
    return _continue(T, fb, nb)


def _continue(T, fb, nb):
    """T on bins 0 .. nb - 1: the BEM values up to FMAX; over the last third octave below FMAX a raised-cosine (in
    log f) crossfade to a constant, the energy mean of |T| there, with zero phase, kept above FMAX (a hard switch
    rings for tens of ms); bin 0 = |T| of the first bin."""
    out = np.zeros(nb, complex)
    f0 = FMAX * 2 ** (-1 / 3)
    top = fb >= f0
    cst = math.sqrt(float(np.mean(np.abs(T[top]) ** 2)))
    w = np.where(fb <= f0, 1.0, 0.5 + 0.5 * np.cos(np.pi * np.log(fb / f0) / np.log(FMAX / f0)))
    out[1:len(fb) + 1] = w * T + (1 - w) * cst
    out[len(fb) + 1:] = cst
    out[0] = abs(T[0])
    return out


def fir(T, nfft=NFFT):
    """FIR of T: nfft taps, the arrival at sample PRE."""
    return np.roll(np.fft.irfft(T, nfft), PRE)


def band_energy(T, fs, bands, nfft=NFFT):
    """Mean |T|^2 over each octave band (f / sqrt 2 .. f sqrt 2) of the bins."""
    f = np.arange(len(T)) * fs / nfft
    out = []
    for fc in bands:
        m = (f >= fc / math.sqrt(2)) & (f < fc * math.sqrt(2))
        out.append(float(np.mean(np.abs(T[m]) ** 2)) if m.any() else 1.0)
    return np.array(out)
