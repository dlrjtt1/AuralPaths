"""
BRAS reference scenes RS1 - RS4, RS6, RS7 with the AuralPaths arrival model, compared with the measured RIRs as in the
round robin (Brinkmann et al. 2019, https://doi.org/10.1121/1.5096178, SuppPub2: Hann window -6 / -3 ms before the
detected direct-sound peak, fade-out per scene, then the spectrum). RS5 has its own script (validation/bras_rs5.py).

    python validation/bras_rs.py <folder holding "_unz/1 Scene descriptions" or "1 Scene descriptions" and
        "3 Surface descriptions"> --scene RS2 [--variant ...] [--out out/rs]

Scenes (BRAS documentation, Aspoeck et al., https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0; geometry from
the scene drawings, positions from the SOFA files):
  RS1  single reflection on the hard floor (Rigid), a 4.2 m RockFon Sonar G patch (Absorbing, 20 mm) or the MDF
       diffusor (Diffuse, top at 0.24 m; its in-situ specular reflection loss is given as absorption), hemi-anechoic
  RS2  MDF plate 25 mm, 1 m or 2 m square, centred at (0, 0, 1.02), front face x = 0, rigid or with 20 mm RockFon;
       sources 4 m away at 30 / 45 / 60 deg; LS4 - LS6 to MP4 / MP5 behind the plate; fully anechoic (no floor)
  RS3  two 2 m MDF plates facing each other, front faces at x = 0 and x = 10 m; source x = 3 m, receiver x = 7 m
  RS4  3 x 3 MDF plates 0.68 m with 0.13 m gaps in the plane x = 0, centred at (0, 0, 1.335)
  RS6  wooden body 0.72 x 0.72 m, 4.14 m wide, centred at x = 5.5 m, on the hard floor
  RS7  15 blocks 0.12 m deep, 0.24 m high, 4.1 m wide, 0.34 m apart (0.22 m gaps), first at x = 3.958 m, hard floor
The supporting stands are left out (the documentation allows it). Sources are flat omnidirectional point sources
with the documented calibration (0.4 Pa at 1 m); the Genelec 8020c response and directivity are not modelled.

Model variants (what the arrivals contain; the engine renders each arrival with its band filter and HRIR, so the
coherent sum here is what its discrete part produces before the HRIRs):
  before     the engine before 2026-11-10: image sources with the Kirchhoff-Fresnel finite-reflector factor (energy,
             applied as sqrt to the amplitude) and the (1 - s) loss, first-order UTD at convex edges, no thin plates
  engine     the current default: as before, plus thin-plate edges (n = 2)
  ga_utd     image sources without the finite-reflector factor plus UTD at all edges incl. thin plates, diffraction
             combined with one reflection before / after (diffraction_refl 1): geometrical acoustics + diffraction
  d2         ga_utd + second-order diffraction (two edges in sequence, diffraction.diffract2, with one reflection
             before / after); without the Kirchhoff factor: with it, the UTD reflection terms and the factor both
             account for the finite face (RS6 LS3 - MP3, grazing over the 0.72 m top: -5.0 dB with, -1.3 dB without)
  box_d2     as d2 without thin-plate edges (thin plates as boxes, their two edges handled by second order)
Writes bands.csv and summary.md per scene and variant (out/ is gitignored: outputs derived from BRAS).
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
import reflections         # noqa: E402

FS = 44100
P1M = 0.4
THIRD = [100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000]
SURF = os.path.join("3 Surface descriptions", "_csv", "initial_estimates")
WIN = {"RS1": (0.030, 0.040), "RS2": (0.030, 0.040), "RS3": (0.550, 0.600), "RS4": (0.085, 0.090),
       "RS6": (0.030, 0.040), "RS7": (0.030, 0.040)}
TEMP = {"RS1": 20.3, "RS2": 17.6, "RS3": 17.3, "RS4": 17.6, "RS6": 19.9, "RS7": 19.2}
HUM = {"RS1": 41.5, "RS2": 47.0, "RS3": 49.5, "RS4": 45.5, "RS6": 40.1, "RS7": 40.3}
FOLDER = {"RS1": "RS1 single reflection (infinite plate)", "RS2": "RS2 single reflection (finite plate)",
          "RS3": "RS3 multiple reflection (parallel finite plates)", "RS4": "RS4 single reflection (reflector array)",
          "RS6": "RS6 diffraction (finite body)", "RS7": "RS7 multiple diffraction (seat dip effect)"}
CONFIGS = {"RS1": ["Rigid", "Absorbing", "Diffuse"], "RS2": ["1mPlate_rigid", "1mPlate_absorbing", "2mPlate_rigid",
           "2mPlate_absorbing"], "RS3": [""], "RS4": ["onCenter", "offCenter"], "RS6": [""], "RS7": [""]}
ORDER = {"RS1": 1, "RS2": 1, "RS3": 24, "RS4": 1, "RS6": 2, "RS7": 2}


# ---------------------------------------------------------------- geometry
def face(verts, n, mat):
    return {"verts": np.array(verts, float), "n": np.array(n, float), "mat": mat}


def box(x0, x1, y0, y1, z0, z1, mat, bottom=False, mats=None):
    """Axis-aligned box, outward normals; mats overrides per side: dict with keys -x +x -y +y +z -z."""
    m = lambda k: (mats or {}).get(k, mat)   # noqa: E731
    F = [face([[x0, y0, z0], [x0, y0, z1], [x0, y1, z1], [x0, y1, z0]], [-1, 0, 0], m("-x")),
         face([[x1, y0, z0], [x1, y1, z0], [x1, y1, z1], [x1, y0, z1]], [1, 0, 0], m("+x")),
         face([[x0, y0, z0], [x1, y0, z0], [x1, y0, z1], [x0, y0, z1]], [0, -1, 0], m("-y")),
         face([[x0, y1, z0], [x0, y1, z1], [x1, y1, z1], [x1, y1, z0]], [0, 1, 0], m("+y")),
         face([[x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], [0, 0, 1], m("+z"))]
    if bottom:
        F.append(face([[x0, y0, z0], [x0, y1, z0], [x1, y1, z0], [x1, y0, z0]], [0, 0, -1], m("-z")))
    return F


def floor(mat="tiles"):
    return face([[-20, -20, 0], [30, -20, 0], [30, 25, 0], [-20, 25, 0]], [0, 0, 1], mat)


def scene(name, cfg):
    S = []
    if name == "RS1":
        S.append(floor())
        if cfg == "Absorbing":
            S += box(3.397, 3.397 + 4.206, 0.881, 0.881 + 4.208, 0.0, 0.02, "rockfon")
        elif cfg == "Diffuse":
            S += box(3.505, 3.505 + 3.99, 0.915, 0.915 + 4.14, 0.0, 0.24, "diffusor")
    elif name == "RS2":
        a = 0.5 if cfg.startswith("1m") else 1.0
        front = "rockfon" if cfg.endswith("absorbing") else "mdf25a"
        th = 0.025 + (0.02 if cfg.endswith("absorbing") else 0.0)
        S += box(-th, 0.0, -a, a, 1.02 - a, 1.02 + a, "mdf25a", bottom=True, mats={"+x": front})
    elif name == "RS3":
        S += box(-0.025, 0.0, -1, 1, 0.02, 2.02, "mdf25a", bottom=True)
        S += box(10.0, 10.025, -1, 1, 0.02, 2.02, "mdf25a", bottom=True)
    elif name == "RS4":
        for i in (-1, 0, 1):
            for j in (-1, 0, 1):
                yc, zc = 0.81 * i, 1.335 + 0.81 * j
                S += box(-0.025, 0.0, yc - 0.34, yc + 0.34, zc - 0.34, zc + 0.34, "mdf25b", bottom=True)
    elif name == "RS6":
        S.append(floor())
        S += box(5.14, 5.86, 2.985 - 2.07, 2.985 + 2.07, 0.0, 0.72, "mdf12")
    elif name == "RS7":
        S.append(floor())
        for r in range(15):
            xc = 3.958 + 0.34 * r
            S += box(xc - 0.06, xc + 0.06, 2.985 - 2.05, 2.985 + 2.05, 0.0, 0.24, "mdf12")
    return dif.prepare({"S": S})


# ---------------------------------------------------------------- materials
MATFILE = {"tiles": "mat_Tiles", "mdf25a": "mat_MDF25mmA_plane_00deg", "mdf25b": "mat_MDF25mmB_plane_00deg",
           "mdf12": "mat_MDF12mm_plane_00deg", "rockfon": "mat_RockFonSonarG_{a:02d}deg",
           "diffusor": "mat_MDF12mm_structured_{a:02d}deg"}
ANGLES = {"rockfon": [0, 30, 45, 60], "diffusor": [30, 45, 60]}


def read_csv(root, name):
    rows = list(csv.reader(open(os.path.join(root, SURF, name + ".csv"))))
    vals = [np.array([float(x) for x in r], float) for r in rows if r]
    return vals[0], vals[1], (vals[2] if len(vals) > 2 else np.zeros_like(vals[0]))


class Mats:
    """Reflection amplitude sqrt(1 - alpha) and scattering s on a frequency grid; angle-dependent data
    (RockFon, diffusor) by the nearest measured angle of incidence."""
    def __init__(self, root, f):
        self.root, self.f, self.cache = root, np.maximum(f, 20.0), {}

    def get(self, mat, theta_deg=0.0):
        if mat in ANGLES:
            a = min(ANGLES[mat], key=lambda x: abs(x - theta_deg))
            key = MATFILE[mat].format(a=a)
        else:
            key = MATFILE[mat]
        if key not in self.cache:
            fm, al, s = read_csv(self.root, key)
            lf = np.log(self.f)
            A = np.interp(lf, np.log(fm), al)
            Sv = np.interp(lf, np.log(fm), s)
            self.cache[key] = (np.sqrt(np.clip(1 - A, 0, 1)), np.clip(Sv, 0, 1))
        return self.cache[key]


# ---------------------------------------------------------------- image sources
def images(G, S, R, order):
    """Valid specular paths up to `order` (classical image method with visibility): list of dicts with
    length, faces, reflection points, incidence directions and the a1 / a2 lengths for the Kirchhoff factor."""
    out = []
    nS = len(G["S"])

    def mirror(X, k):
        s = G["S"][k]
        n = np.asarray(s["n"], float)
        side = float(n @ X - s["d"])
        return None if side <= 1e-9 else X - 2 * side * n

    def validate(seq, imgs):
        pts = [None] * len(seq)
        tgt = R
        for i in range(len(seq) - 1, -1, -1):
            s = G["S"][seq[i]]
            n = np.asarray(s["n"], float)
            I = imgs[i]
            dv = tgt - I
            den = n @ dv
            if abs(den) < 1e-12:
                return None
            t = (s["d"] - n @ I) / den
            if not 1e-9 < t < 1 - 1e-9:
                return None
            P = I + t * dv
            if not dif.in_surface(s, P):
                return None
            nxt = (seq[i + 1],) if i + 1 < len(seq) else ()
            if dif.occluded(G, P, tgt, (seq[i],) + nxt):
                return None
            pts[i] = P
            tgt = P
        if dif.occluded(G, S, pts[0], (seq[0],)):
            return None
        return pts

    def rec(seq, imgs):
        if seq:
            pts = validate(seq, imgs)
            if pts is not None:
                chain = [S] + pts + [R]
                seglen = [float(np.linalg.norm(chain[i + 1] - chain[i])) for i in range(len(chain) - 1)]
                L = sum(seglen)
                refl = []
                for i, k in enumerate(seq):
                    u = (chain[i + 1] - chain[i]) / seglen[i]
                    n = np.asarray(G["S"][k]["n"], float)
                    a1 = sum(seglen[:i + 1])
                    refl.append(dict(k=k, P=pts[i], u=u, theta=math.degrees(math.acos(min(1.0, abs(float(u @ n))))),
                                     a1=a1, a2=L - a1))
                out.append(dict(L=L, seq=list(seq), refl=refl))
        if len(seq) >= order:
            return
        X = imgs[-1] if imgs else S
        for k in range(nS):
            if seq and k == seq[-1]:
                continue
            I = mirror(X, k)
            if I is None:
                continue
            rec(seq + [k], imgs + [I])

    rec([], [])
    return out


def images_axis(G, S, R, order):
    """RS3 only: the images along the axis of the two parallel plates (all other sequences are invalid there)."""
    out = []
    A, B = 1, 6                      # front faces: +x of the first plate box, -x of the second (see scene())
    for first in (A, B):
        seq = []
        k = first
        while len(seq) < order:
            seq.append(k)
            k = B if k == A else A
            for q in images_seq(G, S, R, seq):
                out.append(q)
    return out


def images_seq(G, S, R, seq):
    X = S
    imgs = []
    for k in seq:
        s = G["S"][k]
        n = np.asarray(s["n"], float)
        side = float(n @ X - s["d"])
        if side <= 1e-9:
            return []
        X = X - 2 * side * n
        imgs.append(X)
    pts = [None] * len(seq)
    tgt = R
    for i in range(len(seq) - 1, -1, -1):
        s = G["S"][seq[i]]
        n = np.asarray(s["n"], float)
        dv = tgt - imgs[i]
        t = (s["d"] - n @ imgs[i]) / (n @ dv)
        P = imgs[i] + t * dv
        if not (1e-9 < t < 1 - 1e-9 and dif.in_surface(s, P)):
            return []
        pts[i] = P
        tgt = P
    chain = [S] + pts + [R]
    seglen = [float(np.linalg.norm(chain[i + 1] - chain[i])) for i in range(len(chain) - 1)]
    L = sum(seglen)
    refl = []
    for i, k in enumerate(seq):
        u = (chain[i + 1] - chain[i]) / seglen[i]
        a1 = sum(seglen[:i + 1])
        refl.append(dict(k=k, P=pts[i], u=u, theta=0.0, a1=a1, a2=L - a1))
    return [dict(L=L, seq=list(seq), refl=refl)]


# ---------------------------------------------------------------- model
def air_np(f, T, rh):
    import brir_proto as bp
    return bp._iso9613_db_per_m(np.maximum(f, 1.0), temp_c=T, rh=rh) / (20 * math.log10(math.e))


def model_tf(name, G, E, S, R, f, M, c, variant, air):
    k = 2 * np.pi * f / c
    H = np.zeros(len(f), complex)
    if not dif.occluded(G, S, R):
        L = float(np.linalg.norm(R - S))
        H += np.exp(-1j * k * L - air * L) / L
    paths = images_axis(G, S, R, ORDER[name]) if name == "RS3" else images(G, S, R, ORDER[name])
    finite = variant in ("before", "engine")
    for q in paths:
        amp = np.ones(len(f))
        for r in q["refl"]:
            Ra, s = M.get(G["S"][r["k"]]["mat"], r["theta"])
            amp = amp * Ra * np.sqrt(1 - s)
            if finite:
                fg = np.geomspace(10, f[-1], 240)          # K is smooth in frequency: coarse grid, interpolated
                Kg = reflections.reflection_K(G, r["k"], r["P"], r["u"], r["a1"], r["a2"], fg, c)
                Kf = np.interp(np.log(np.maximum(f, 10.0)), np.log(fg), Kg)
                amp = amp * np.sqrt(np.clip(Kf, 0, None))
        H += amp * np.exp(-1j * k * q["L"] - air * q["L"]) / q["L"]
    narr = 0
    if E:
        old = dif.DF
        dif.DF = np.maximum(f, 1.0)
        try:
            arr = dif.diffract(G, E, S, R, c, lambda i: np.ones(1), [0.0], [1000.0],
                               refl_order=1 if variant in ("ga_utd", "d2", "box_d2") else 0)
        finally:
            dif.DF = old
        if variant in ("d2", "box_d2"):
            fg = np.geomspace(10.0, max(f[-1], 20.0), 160)   # second-order coefficients on a coarse grid
            dif.DF = fg
            try:
                # RS7: 120 edges; with image sources in all 76 faces the pair search takes hours, so no reflections
                arr2 = dif.diffract2(G, E, S, R, c, lambda i: np.ones(1), [0.0], [1000.0],
                                     refl_order=0 if name == "RS7" else 1)
            finally:
                dif.DF = old
            lf = np.log(np.maximum(f, 10.0))
            for q in arr2:
                mag = np.interp(lf, np.log(fg), np.abs(q["D"]))
                ph = np.interp(lf, np.log(fg), np.unwrap(np.angle(q["D"])))
                q["D"] = mag * np.exp(1j * ph)
            arr = arr + arr2
        for q in arr:
            Ra = np.ones(len(f))
            for j in q.get("refl", ()):
                Ra = Ra * M.get(G["S"][j]["mat"])[0]
            # hard faces in the UTD reflection terms (see the module docstring)
            H += Ra * q["D"] * np.exp(-1j * k * q["d"] - air * q["d"])
        narr = len(arr)
    return P1M * H, len(paths), narr


def window(x, fade, t0):
    """Hann fade-in -6 / -3 ms before t0, fade-out fade[0] / fade[1] after it. t0 is the geometrical direct-sound
    time, for measured and simulated alike (the round robin's "detected direct-sound peak"; anchoring at the peak of
    the measured RIR instead reproduced the round-robin measured curves worse, e.g. 2.3 instead of 0.5 dB rms for
    figure S2-22, where the direct sound leaves the loudspeaker far off axis and the reflection is the peak)."""
    pk = int(round(t0 * FS))
    t = (np.arange(len(x)) - pk) / FS
    w = np.zeros(len(x))
    up = (t >= -0.006) & (t < -0.003)
    w[up] = 0.5 - 0.5 * np.cos(np.pi * (t[up] + 0.006) / 0.003)
    w[(t >= -0.003) & (t <= fade[0])] = 1
    dn = (t > fade[0]) & (t <= fade[1])
    w[dn] = 0.5 + 0.5 * np.cos(np.pi * (t[dn] - fade[0]) / (fade[1] - fade[0]))
    return x * w


def third_levels(x, nfft):
    X = np.fft.rfft(x, nfft)
    f = np.fft.rfftfreq(nfft, 1 / FS)
    return np.array([10 * np.log10(np.mean(np.abs(X[(f >= fc * 2 ** (-1 / 6)) & (f < fc * 2 ** (1 / 6))]) ** 2) + 1e-30)
                     for fc in THIRD])


def find_scene_dir(root, name):
    for base in (os.path.join(root, "_unz", "1 Scene descriptions"), os.path.join(root, "1 Scene descriptions")):
        p = os.path.join(base, FOLDER[name])
        if os.path.isdir(p):
            return p
    raise SystemExit(f"{FOLDER[name]} not found under {root}")


def read_sofa(path):
    import h5py
    f = h5py.File(path, "r")
    ir = np.asarray(f["Data.IR"])[:, 0, :]
    E = np.asarray(f["EmitterPosition"])[0].T
    R = np.asarray(f["ReceiverPosition"])[0].T
    return ir, E, R, np.asarray(f["EmitterID"]).ravel().astype(int), np.asarray(f["ReceiverID"]).ravel().astype(int)


def run(root, name, cfg, variant, out):
    sd = find_scene_dir(root, name)
    sofa = os.path.join(sd, "RIRs", f"{name}_RIRs{'_' + cfg if cfg else ''}.sofa")
    ir, Ep, Rp, eid, rid = read_sofa(sofa)
    nfft = 1 << int(math.ceil(math.log2(ir.shape[1])))
    f = np.fft.rfftfreq(nfft, 1 / FS)
    c = 331.3 * math.sqrt(1 + TEMP[name] / 273.15)
    air = air_np(f, TEMP[name], HUM[name])
    M = Mats(root, f)
    G = scene(name, cfg)
    dif.THIN_M = 0.0 if variant in ("before", "box_d2") else 0.05
    E = dif.edges(G)
    taper = np.clip((12000 - f) / 2000, 0, 1)
    rows, summ, onset_err = [], [], []
    for i in range(len(eid)):
        S, R = np.asarray(Ep[i], float), np.asarray(Rp[i], float)
        H, nimg, ndif = model_tf(name, G, E, S, R, f, M, c, variant, air)
        xs = np.fft.irfft(H * taper, nfft)
        xm = np.zeros(nfft)
        xm[:ir.shape[1]] = ir[i]
        t0 = float(np.linalg.norm(R - S)) / c
        lm, ls = third_levels(window(xm, WIN[name], t0), nfft), third_levels(window(xs, WIN[name], t0), nfft)
        on = int(np.argmax(np.abs(xm) > 0.2 * np.abs(xm).max()))
        onset_err.append(on / FS - float(np.linalg.norm(R - S)) / c)
        los = not dif.occluded(G, S, R)
        d = lm - ls
        sel = (np.array(THIRD) >= 125) & (np.array(THIRD) <= 4000)
        dd = d[sel]
        summ.append(dict(pair=f"LS{eid[i]}-MP{rid[i]}", los=los, nimg=nimg, ndif=ndif, bias=float(np.median(dd)),
                         shape=float(np.sqrt(np.mean((dd - dd.mean()) ** 2))), mad=float(np.mean(np.abs(dd)))))
        for fc, a, b in zip(THIRD, lm, ls):
            rows.append([cfg or name, f"LS{eid[i]}", f"MP{rid[i]}", int(los), fc, round(a, 2), round(b, 2), round(a - b, 2)])
    print(f"   measured first arrival (20 % of max) minus geometrical direct time: median "
          f"{1000 * np.median(onset_err):+.2f} ms, range {1000 * min(onset_err):+.2f} .. {1000 * max(onset_err):+.2f} ms")
    os.makedirs(out, exist_ok=True)
    tag = f"{name}{'_' + cfg if cfg else ''}_{variant}"
    with open(os.path.join(out, tag + ".csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["config", "source", "receiver", "line_of_sight", "f_hz", "measured_db", "simulated_db",
                    "measured_minus_sim_db"])
        w.writerows(rows)
    return summ


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--scene", required=True, choices=sorted(FOLDER))
    ap.add_argument("--config", default=None)
    ap.add_argument("--variant", default="all", choices=["all", "before", "engine", "ga_utd", "d2", "box_d2"])
    ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "rs"))
    a = ap.parse_args()
    variants = ["before", "engine", "ga_utd"] if a.variant == "all" else [a.variant]
    for cfg in ([a.config] if a.config is not None else CONFIGS[a.scene]):
        for v in variants:
            summ = run(a.root, a.scene, cfg, v, a.out)
            for s in summ:
                print(f"{a.scene} {cfg:18s} {v:7s} {s['pair']:8s} los={int(s['los'])} img={s['nimg']:2d} dif={s['ndif']:3d} "
                      f"bias {s['bias']:+6.1f}  shape {s['shape']:4.1f}  mean|d| {s['mad']:4.1f}")
            sh = [s["shape"] for s in summ]
            md = [s["mad"] for s in summ]
            print(f"== {a.scene} {cfg} {v}: median shape {np.median(sh):.1f} dB, median mean|d| {np.median(md):.1f} dB "
                  f"({len(summ)} pairs)")


if __name__ == "__main__":
    main()
