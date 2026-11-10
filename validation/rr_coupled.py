"""
Round-robin comparison for the coupled rooms (scene 8 = BRAS CR1, laboratory and reverberation chamber; Brinkmann et
al. 2019, https://doi.org/10.1121/1.5096178, SuppPub2 section 6, figures S2-34 - S2-37): energy decay curves (EDC) in
the 1 kHz octave band for loudspeaker LS2 and microphones MP3 / MP4, door opening angles 4.1 deg (BRAS "DoorAngle1")
and 30.4 deg ("DoorAngle3").

    python validation/rr_coupled.py --extract <supppub2.pdf>           # figure curves -> out/rs/rr_edc.csv
    python validation/rr_coupled.py <BRAS folder> [--coeffs initial|fitted] [--rays 6000]
    python validation/rr_coupled.py --table out/rs

<BRAS folder> holds "CR1 coupled rooms*" (Geometry/rooms/CR1_DoorAngle{1,3}.obj, RIRs/CR1_RIRs_DoorAngle{1,3}_
Dodecahedron.sofa) and "3 Surface descriptions". Post-processing as in SuppPub2: time zero at the direct sound, one-sided
Hann fade-out from 2.15 to 2.2 s, 1 kHz octave, Schroeder EDC without truncation normalised to 0 dB at time zero.
The chamber is marked as part of the room with a seed point (mesh "seeds"), since the flood fill from the source
does not pass the narrow gap at 4.1 deg. Error: the mean absolute EDC difference from the measured curve over 0 - 1.2 s (every 10 ms), in dB, down to -50 dB
(the figure's range). This metric is defined here, not in the paper. Outputs derive from BRAS (CC BY-SA 4.0): out/ only.
"""
import argparse
import csv
import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, ".."), HERE]
FIGS = [("S2-34", 1, "MP3"), ("S2-35", 3, "MP3"), ("S2-36", 1, "MP4"), ("S2-37", 3, "MP4")]   # (figure, door, mic)
ANGLE = {1: 4.1, 3: 30.4}
PROG = {(0.0, 0.4471, 0.7412): "A", (0.2667, 0.6745, 0.1882): "B", (0.9294, 0.6941, 0.1255): "C",
        (0.0, 0.7843, 0.7843): "D", (0.4941, 0.1843, 0.5569): "E", (0.7843, 0.1725, 0.0392): "F"}
T = np.round(np.arange(0, 1.2001, 0.01), 3)
# a point in the reverberation chamber (AuralPaths frame after check_bras_brir.rotate_obj and "y-up"): at 4.1 deg the
# door gap is narrower than the voxel band, so the chamber has to be marked as room explicitly (geometry "seeds")
CHAMBER = [-1.98, -3.26, 1.33]


def extract(pdf, out):
    import pdfplumber
    doc = pdfplumber.open(pdf)
    rows, k = [], 0
    for pg in doc.pages[19:21]:
        axes = sorted([r for r in pg.rects if 300 < r["width"] < 400 and 100 < r["height"] < 200],
                      key=lambda r: r["top"])
        axes = [a for i, a in enumerate(axes) if i == 0 or abs(a["top"] - axes[i - 1]["top"]) > 1]
        for ax in axes:
            fig, door, mic = FIGS[k]
            k += 1
            nums = [w for w in pg.extract_words() if _num(w["text"]) is not None]
            yl = [w for w in nums if w["x1"] < ax["x0"] and ax["top"] - 6 < (w["top"] + w["bottom"]) / 2 < ax["bottom"] + 6]
            xl = [w for w in nums if ax["bottom"] < w["top"] < ax["bottom"] + 15]
            ky, by = np.polyfit([(w["top"] + w["bottom"]) / 2 for w in yl], [_num(w["text"]) for w in yl], 1)
            kx, bx = np.polyfit([(w["x0"] + w["x1"]) / 2 for w in xl], [_num(w["text"]) for w in xl], 1)
            inside = [c for c in pg.curves if ax["x0"] - 1 <= c["x0"] and c["x1"] <= ax["x1"] + 1
                      and ax["top"] - 1 <= c["top"] and c["bottom"] <= ax["bottom"] + 1 and len(c["pts"]) > 20]
            curves = {"measured": [c for c in inside if str(c.get("stroking_color")) == "0.1294"]}
            for c in inside:
                p = _prog(c.get("stroking_color"))
                if p:
                    curves.setdefault(p, []).append(c)
            for name, cs in curves.items():
                pts = np.array([p for c in cs for p in c["pts"]], float)
                t, L = kx * pts[:, 0] + bx, ky * pts[:, 1] + by
                o = np.argsort(t, kind="stable")
                t, L = t[o], L[o]
                for tt in T:
                    if t[0] - 0.005 <= tt <= t[-1] + 0.005:
                        rows.append([fig, door, mic, name, tt, round(float(np.interp(tt, t, L)), 3)])
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["figure", "door", "receiver", "curve", "t_s", "edc_db"])
        w.writerows(rows)
    print(len(rows), "->", out)


def _num(s):
    try:
        return float(s)
    except ValueError:
        return None


def _prog(col):
    if isinstance(col, (tuple, list)) and len(col) == 3:
        for kk, v in PROG.items():
            if max(abs(a - b) for a, b in zip(kk, col)) < 0.01:
                return v
    return None


def edc_db(e, dt):
    """Schroeder EDC (dB re total) of an energy sequence starting at the direct sound, faded out 2.15 - 2.2 s."""
    t = np.arange(len(e)) * dt
    w = np.where(t < 2.15, 1.0, np.where(t < 2.2, 0.5 + 0.5 * np.cos(np.pi * (t - 2.15) / 0.05), 0.0)) ** 2
    e = np.asarray(e, float) * w
    s = np.cumsum(e[::-1])[::-1]
    return t, 10 * np.log10(np.maximum(s / s[0], 1e-30))


def run(a):
    import brir_proto as bp
    import check_bras_brir as cb
    import validate_bras_cr as vb
    from scipy import signal
    scene = glob.glob(os.path.join(a.bras, "CR1*"))[0]
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    mats = vb.read_bras_materials(os.path.join(a.bras, "3 Surface descriptions"), "CR1", a.coeffs, bands=[1000])
    rows = []
    for door in (1, 3):
        obj_path = os.path.join(out, f"CR1_DoorAngle{door}_rotated.obj")
        with open(obj_path, "w", encoding="utf-8") as f:
            f.write(cb.rotate_obj(open(os.path.join(scene, "Geometry", "rooms", f"CR1_DoorAngle{door}.obj"),
                                       encoding="utf-8", errors="ignore").read()))
        import sofar
        s = sofar.read_sofa(os.path.join(scene, "RIRs", f"CR1_RIRs_DoorAngle{door}_Dodecahedron.sofa"),
                            verify=False, verbose=False)
        ir = np.asarray(s.Data_IR, float)[0]
        fs = float(np.atleast_1d(s.Data_SamplingRate)[0])
        E, R = np.asarray(s.EmitterPosition, float)[..., 0], np.asarray(s.ReceiverPosition, float)[..., 0]
        eid = np.asarray(s.EmitterID).ravel().astype(int)
        rid = np.asarray(s.ReceiverID).ravel().astype(int)
        j = int(np.flatnonzero(eid == 2)[0])
        src = cb.rot(E[j])
        M = {f"MP{r}": cb.rot(R[i]) for i, r in enumerate(rid)}
        cfg = {"name": f"BRAS CR1 door {door}", "fs": 48000, "c": 343.5,
               "room": {"dims_m": [10, 10, 5], "absorption_octave": {"values": [0.2] * 6}, "air_absorption": True},
               "sources": {"LS2": {"pos": src}}, "receivers": dict(sorted(M.items())),
               "geometry": {"mesh": {"obj": obj_path, "axes": "y-up", "groups": {k: k for k in mats}, "voxel": 0.08,
                                     "default": "mat_CR1_concrete",     # one wall in DoorAngle1.obj has no material
                                     "seeds": [CHAMBER]},
                            "materials": {k: {"alpha": [float(v["alpha"][0])] * 6, "s": [float(v["s_oct"][0])] * 6}
                                          for k, v in mats.items()},
                            "ism_order": 1, "rays": a.rays, "diffraction": False}}
        H, cen = bp.energy_hists(cfg, "LS2", list(M), t_max=3.0, n_rays=a.rays)
        bi = int(np.argmin(np.abs(np.asarray(cen) - 1000)))
        sos = signal.butter(4, [1000 / 2 ** 0.5, 1000 * 2 ** 0.5], btype="band", fs=fs, output="sos")
        for i, r in enumerate(rid):
            rec = f"MP{r}"
            x = ir[i, j]
            on = int(np.argmax(np.abs(x) > 0.1 * np.abs(x).max()))
            y = signal.sosfilt(sos, x)[on:]
            tm, Lm = edc_db(y ** 2, 1 / fs)
            d = float(np.linalg.norm(np.subtract(M[rec], src)))
            i0 = int(np.floor(d / cfg["c"] / bp.HIST_BIN))
            ts, Ls = edc_db(np.asarray(H[rec][bi])[i0:], bp.HIST_BIN)
            for tt in T:
                rows.append([door, rec, a.coeffs, tt, round(float(np.interp(tt, tm, Lm)), 3),
                             round(float(np.interp(tt, ts, Ls)), 3)])
        print(f"CR1 door {door} done", flush=True)
    path = os.path.join(out, f"rr_coupled_{a.coeffs}.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["door", "receiver", "coeffs", "t_s", "measured", "simulated"])
        w.writerows(rows)
    print("->", path)


def table(out):
    fig = list(csv.DictReader(open(os.path.join(out, "rr_edc.csv"))))
    lines = ["| figure | door | mic | check: measured here vs figure | A | B | C | D | E | F | AuralPaths initial | "
             "AuralPaths fitted |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    sims = {c: list(csv.DictReader(open(p))) for c in ("initial", "fitted")
            for p in [os.path.join(out, f"rr_coupled_{c}.csv")] if os.path.exists(p)}
    tot = {}
    for f_, door, mic in FIGS:
        cur = lambda c: {float(r["t_s"]): float(r["edc_db"]) for r in fig if r["figure"] == f_ and r["curve"] == c}
        meas = cur("measured")
        cells = []

        def err(d):
            ts = [t for t in T if t in d and t in meas and meas[t] > -50]
            return float(np.mean([abs(d[t] - meas[t]) for t in ts])) if ts else np.nan
        for c in "ABCDEF":
            e = err(cur(c))
            tot.setdefault(c, []).append(e)
            cells.append(f"{e:.1f}")
        chk, ap = "", []
        for c, rows in sims.items():
            rr = [r for r in rows if int(r["door"]) == door and r["receiver"] == mic]
            if not chk:
                chk = f"{err({float(r['t_s']): float(r['measured']) for r in rr}):.1f}"
            e = err({float(r["t_s"]): float(r["simulated"]) for r in rr})
            tot.setdefault(c, []).append(e)
            ap.append(f"{e:.1f}")
        lines.append(f"| {f_} | {ANGLE[door]} deg | {mic} | {chk} | " + " | ".join(cells + ap) + " |")
    lines.append("| **mean** | | | | " + " | ".join(f"**{np.nanmean(tot[c]):.1f}**" for c in list("ABCDEF") +
                                                     [c for c in ("initial", "fitted") if c in tot]) + " |")
    txt = "\n".join(lines)
    print(txt)
    open(os.path.join(out, "rr_coupled.md"), "w").write(txt + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras", nargs="?")
    ap.add_argument("--extract", default=None, help="SuppPub2 pdf: read the figure curves")
    ap.add_argument("--coeffs", default="initial", choices=["initial", "fitted"])
    ap.add_argument("--rays", type=int, default=6000)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "rs"))
    ap.add_argument("--table", default=None)
    a = ap.parse_args()
    if a.extract:
        extract(a.extract, os.path.join(a.out, "rr_edc.csv"))
    elif a.table:
        table(a.table)
    else:
        run(a)


if __name__ == "__main__":
    main()
