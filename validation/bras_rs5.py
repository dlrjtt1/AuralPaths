"""
BRAS reference scene RS5 (diffraction at a 2.066 m high partition on a rigid floor) with the AuralPaths
diffraction model, compared with the measured RIRs the way the round robin did (Brinkmann et al. 2019,
https://doi.org/10.1121/1.5096178, SuppPub2 section 5: Hann window from -6 / -3 ms to 30 / 40 ms around the
detected direct-sound peak, then the spectrum).

    python validation/bras_rs5.py <folder holding "1 Scene descriptions" and "3 Surface descriptions">
        [--variant before|thin|thin+floor|thin+floor+tl] [--out out/rs5]

Scene (BRAS documentation, Aspoeck et al., https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0): MDF partition
25 mm thick, 2.066 m high, 4.75 m wide, front face at x = 5.487 m, centred at y = 2.985 m, on the tiled floor of the
hemi-anechoic chamber; Genelec 8020c sources 3 m in front, GRAS 40AF microphones 3 m behind, heights in the SOFA file.
The source is modelled as a flat omnidirectional point source with the documented calibration (80 dB SPL at 2 m,
on axis, 1 kHz, i.e. 0.4 Pa m); its real frequency response and directivity are not modelled (no data in this
folder), which limits absolute levels to roughly the loudspeaker's tolerance.

Variants (what is switched on):
  before            AuralPaths before 2026-11-10: direct sound and floor reflection (image sources, occlusion), and
                    first-order UTD diffraction at the convex edges of the partition box only (diffraction.THIN_M = 0)
  thin              thin-plate edges (diffraction.THIN_M, wedge index n = 2), the engine default since 2026-11-10
  thin+floor        thin, plus diffraction combined with one specular reflection before and/or after the edge
                    (diffraction.diffract refl_order=1, "geometry": {"diffraction_refl": 1} in a hall config)
  thin+floor+tl     thin+floor, plus sound transmission through the partition (mass law, limp plate; not in the
                    engine: it changes nothing here, see validation/bras_rs5.md)

Writes bands.csv (1/3-octave levels measured and simulated, 100 Hz - 5 kHz) and summary.md to --out (out/ is
gitignored: the outputs are derived from BRAS, CC BY-SA 4.0).
"""
import argparse
import csv
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..")]
import diffraction as dif   # noqa: E402

FS = 44100
NFFT = 8192
C = 343.2                    # 20.3 degC (BRAS RS5)
RHO = 1.204
P1M = 0.4                    # Pa at 1 m (80 dB SPL at 2 m)
X0, TH, H, Y0, W = 5.487, 0.025, 2.066, 2.985, 4.75
M_AREA = 18.56               # kg/m2, mat_MDF25mmB_plane
THIRD = [100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000]
SCENE = os.path.join("1 Scene descriptions", "RS5 diffraction (infinite wedge)")
SURF = os.path.join("3 Surface descriptions", "_csv", "initial_estimates")


def read_mat(root, name):
    rows = list(csv.reader(open(os.path.join(root, SURF, name + ".csv"))))
    f, a = (np.array([float(x) for x in r], float) for r in rows[:2])
    return f, a


def scene_geometry():
    """Floor (n = +z) and the partition box (outward normals; no bottom face). Surface format of geometry.build."""
    def face(verts, n, mat):
        return {"verts": np.array(verts, float), "n": np.array(n, float), "mat": mat}
    x1, y0, y1 = X0 + TH, Y0 - W / 2, Y0 + W / 2
    S = [face([[-20, -20, 0], [30, -20, 0], [30, 25, 0], [-20, 25, 0]], [0, 0, 1], "tiles"),
         face([[X0, y0, 0], [X0, y0, H], [X0, y1, H], [X0, y1, 0]], [-1, 0, 0], "mdf"),
         face([[x1, y0, 0], [x1, y1, 0], [x1, y1, H], [x1, y0, H]], [1, 0, 0], "mdf"),
         face([[X0, y0, H], [x1, y0, H], [x1, y1, H], [X0, y1, H]], [0, 0, 1], "mdf"),
         face([[X0, y0, 0], [x1, y0, 0], [x1, y0, H], [X0, y0, H]], [0, -1, 0], "mdf"),
         face([[X0, y1, 0], [X0, y1, H], [x1, y1, H], [x1, y1, 0]], [0, 1, 0], "mdf")]
    return dif.prepare({"S": S})


def read_rirs(root):
    import h5py
    f = h5py.File(os.path.join(root, SCENE, "RIRs", "RS5_RIRs.sofa"), "r")
    ir = np.asarray(f["Data.IR"])[:, 0, :]
    E = np.asarray(f["EmitterPosition"])[0].T
    R = np.asarray(f["ReceiverPosition"])[0].T
    return ir, E, R, np.asarray(f["EmitterID"]).ravel().astype(int), np.asarray(f["ReceiverID"]).ravel().astype(int)


def air_np_per_m(f):
    import brir_proto as bp
    return bp._iso9613_db_per_m(np.maximum(f, 1.0), temp_c=20.3, rh=41.0) / (20 * math.log10(math.e))  # amplitude Np/m


def model_tf(G, E, S, R, f, refl_amp, variant):
    """Complex pressure (Pa per unit input) at the FFT frequencies f."""
    H_ = np.zeros(len(f), complex)
    air = air_np_per_m(f)
    k = 2 * np.pi * f / C

    def arrival(amp, L):
        return amp * np.exp(-1j * k * L - air * L)
    # direct sound and specular reflections (image sources of order 1; the scene has no useful higher orders)
    if not dif.occluded(G, S, R):
        H_ += arrival(1.0, np.linalg.norm(R - S)) / np.linalg.norm(R - S)
    for i, s in enumerate(G["S"]):
        r = dif._refl(G, S, R, i, None)
        if r:
            H_ += arrival(refl_amp[s["mat"]], r[0]) / r[0]
    # diffraction
    old = dif.DF
    dif.DF = np.maximum(f, 1.0)
    try:
        Rmat = lambda i: np.ones(1)   # noqa: E731  (hard faces: R = 1 in the UTD reflection terms)
        kw = {}
        if "floor" in variant:
            kw["refl_order"] = 1
        arr = dif.diffract(G, E, S, R, C, Rmat, [0.0], [1000.0], **kw)
    finally:
        dif.DF = old
    for q in arr:
        Ra = np.ones(len(f))
        for j in q.get("refl", ()):
            Ra = Ra * refl_amp[G["S"][j]["mat"]]
        H_ += Ra * q["D"] * np.exp(-1j * k * q["d"] - air * q["d"])
    if "tl" in variant:
        H_ += transmission(G, S, R, f, refl_amp, arrival)
    return P1M * H_, arr


def transmission(G, S, R, f, refl_amp, arrival):
    """Straight paths through the partition (direct and via one floor reflection on either side), limp mass law
    t = 1 / (1 + j w m'' cos(theta) / (2 rho c)) (Cremer, Heckl & Petersson, Structure-Borne Sound; the oblique form is
    the standard limp-panel result, not checked against a primary source here)."""
    out = np.zeros(len(f), complex)
    Simg = S * np.array([1, 1, -1]); Rimg = R * np.array([1, 1, -1])
    for a, b, nfl in ((S, R, 0), (Simg, R, 1), (S, Rimg, 1)):
        d = b - a
        tcross = (X0 + TH / 2 - a[0]) / d[0]
        P = a + tcross * d
        if not (0 <= P[2] <= H and Y0 - W / 2 <= P[1] <= Y0 + W / 2):
            continue
        # floor reflection point must lie on the correct side of the partition
        if nfl:
            tz = -a[2] / d[2]
            px = a[0] + tz * d[0]
            if (a is Simg and px > X0) or (b is Rimg and px < X0 + TH):
                continue
        L = np.linalg.norm(d)
        cos_t = abs(d[0]) / L
        t = 1 / (1 + 1j * 2 * np.pi * f * M_AREA * cos_t / (2 * RHO * C))
        amp = t * (refl_amp["tiles"] if nfl else 1.0)
        out += arrival(amp, L) / L
    return out


def window(x, fs=FS):
    pk = int(np.argmax(np.abs(x)))
    t = (np.arange(len(x)) - pk) / fs
    w = np.zeros(len(x))
    up = (t >= -0.006) & (t < -0.003)
    w[up] = 0.5 - 0.5 * np.cos(np.pi * (t[up] + 0.006) / 0.003)
    w[(t >= -0.003) & (t <= 0.030)] = 1
    dn = (t > 0.030) & (t <= 0.040)
    w[dn] = 0.5 + 0.5 * np.cos(np.pi * (t[dn] - 0.030) / 0.010)
    return x * w


def third_levels(x):
    X = np.fft.rfft(x, NFFT)
    f = np.fft.rfftfreq(NFFT, 1 / FS)
    out = []
    for fc in THIRD:
        b = (f >= fc * 2 ** (-1 / 6)) & (f < fc * 2 ** (1 / 6))
        out.append(10 * np.log10(np.mean(np.abs(X[b]) ** 2) + 1e-30))
    return np.array(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--variant", default="thin+floor", choices=["before", "thin", "thin+floor", "thin+floor+tl"])
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(HERE, "..", "out", "rs5", a.variant.replace("+", "_"))
    os.makedirs(out, exist_ok=True)
    ir, Ep, Rp, eid, rid = read_rirs(a.root)
    fm, am = read_mat(a.root, "mat_Tiles")
    f = np.fft.rfftfreq(NFFT, 1 / FS)
    refl_amp = {"tiles": np.sqrt(1 - np.interp(np.log(np.maximum(f, 20)), np.log(fm), am))}
    fm2, am2 = read_mat(a.root, "mat_MDF25mmB_plane_00deg")
    refl_amp["mdf"] = np.sqrt(1 - np.interp(np.log(np.maximum(f, 20)), np.log(fm2), am2))
    G = scene_geometry()
    if a.variant == "before":
        dif.THIN_M = 0.0
    E = dif.edges(G)
    taper = np.clip((10000 - f) / 2000, 0, 1)          # model evaluated to 8 kHz, tapered to 10 kHz
    rows, summ = [], []
    for i in range(len(eid)):
        S, R = Ep[i], Rp[i]
        Hm, arr = model_tf(G, E, S, R, f, refl_amp, a.variant)
        xs = np.fft.irfft(Hm * taper, NFFT)
        xm = ir[i][:NFFT]
        lm, ls = third_levels(window(xm)), third_levels(window(xs))
        los = not dif.occluded(G, S, R)
        d = lm - ls
        shape = d - d.mean()
        summ.append((f"LS{eid[i]}", f"MP{rid[i]}", los, len(arr), float(np.median(d)), float(np.sqrt(np.mean(shape ** 2))),
                     float(np.abs(shape).max())))
        for fc, x1, x2 in zip(THIRD, lm, ls):
            rows.append([f"LS{eid[i]}", f"MP{rid[i]}", int(los), fc, round(x1, 2), round(x2, 2), round(x1 - x2, 2)])
    with open(os.path.join(out, "bands.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["source", "receiver", "line_of_sight", "f_hz", "measured_db", "simulated_db", "measured_minus_sim_db"])
        w.writerows(rows)
    with open(os.path.join(out, "summary.md"), "w") as fh:
        fh.write(f"# RS5, variant {a.variant}\n\n| pair | line of sight | diffracted paths | median meas - sim (dB) | "
                 "shape error rms (dB) | max (dB) |\n|---|---|---|---|---|---|\n")
        for s in summ:
            fh.write(f"| {s[0]}-{s[1]} | {'yes' if s[2] else 'no'} | {s[3]} | {s[4]:+.1f} | {s[5]:.1f} | {s[6]:.1f} |\n")
    for s in summ:
        print(f"{s[0]}-{s[1]} los={int(s[2])} n_diff={s[3]:2d} median {s[4]:+6.1f} dB  shape rms {s[5]:4.1f}  max {s[6]:4.1f}")
    nl = [s for s in summ if not s[2]]
    print(f"no line of sight ({len(nl)} pairs): |median| {np.median([abs(s[4]) for s in nl]):.1f} dB, shape rms "
          f"{np.median([s[5] for s in nl]):.1f} dB (medians over pairs)")


if __name__ == "__main__":
    main()
