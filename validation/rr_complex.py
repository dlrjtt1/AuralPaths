"""
Round-robin comparison for the complex rooms (Brinkmann et al. 2019, https://doi.org/10.1121/1.5096178, SuppPub3
figure S3-1): T20, EDT, C80 and D50 in the octave bands 125 Hz - 4 kHz, averaged over the 10 source-receiver pairs
(dodecahedron source LS1 / LS2, microphones MP1 - MP5), for the measurement, the round-robin programs A - F (read by
validation/rr_extract_ra.py) and AuralPaths.

    python validation/rr_complex.py <BRAS folder> CR3 [--coeffs initial|fitted] [--rays 6000] [--out out/rs]
    python validation/rr_complex.py --table out/rs                  # the comparison table from the saved results

The participants had the BRAS material data and no measured responses ("best possible estimations", predictive
situation; Brinkmann et al. 2019, sec. II.C); the paper does not say whether these were the data now called
"initial" or "fitted" in BRAS (fitted = absorption adjusted to the measured reverberation times with Eyring's
formula, BRAS documentation). Both are run here; "initial" is the predictive case.

Parameters from energy histograms (engine) or from the octave-filtered measured RIR with the noise floor removed
(validate_bras_cr.measured_hist): T20 from the -5 ... -25 dB part of the Schroeder curve, EDT 0 ... -10 dB, C80 and D50
from the energy before / after 80 and 50 ms (D50 in %). JND as in the round-robin figure: 5 % for T20 and EDT, 1 dB
for C80, 5 percentage points for D50 (ISO 3382-1 Annex A). Outputs are derived from BRAS (CC BY-SA 4.0): out/ only.
"""
import argparse
import csv
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, ".."), HERE]
import brir_proto as bp                     # noqa: E402
import check_bras_brir as cb                # noqa: E402
import validate_bras_cr as vb               # noqa: E402

BANDS = [125, 250, 500, 1000, 2000, 4000]
PARS = ["T20", "EDT", "C80", "D50"]
JND = {"T20": ("rel", 0.05), "EDT": ("rel", 0.05), "C80": ("abs", 1.0), "D50": ("abs", 5.0)}


def params(h, t0, bin_s=bp.HIST_BIN):
    out = {k: [] for k in PARS}
    i0 = int(np.floor(t0 / bin_s))
    for e in h:
        e = np.asarray(e[i0:], float)
        tot = e.sum()
        t = (np.arange(len(e)) + 0.5) * bin_s
        n50, n80 = int(round(0.05 / bin_s)), int(round(0.08 / bin_s))
        out["C80"].append(10 * np.log10(e[:n80].sum() / e[n80:].sum()))
        out["D50"].append(100 * e[:n50].sum() / tot)
        edc = 10 * np.log10(np.maximum(np.cumsum(e[::-1])[::-1] / tot, 1e-30))
        for name, hi, lo in (("EDT", 0, -10), ("T20", -5, -25)):
            sel = (edc <= hi) & (edc >= lo)
            out[name].append(-60 / np.polyfit(t[sel], edc[sel], 1)[0] if sel.sum() > 10 and edc.min() < lo - 10 else np.nan)
    return {k: np.array(v) for k, v in out.items()}


def err_jnd(par, sim, meas):
    kind, j = JND[par]
    return (np.asarray(sim) - np.asarray(meas)) / (j * np.asarray(meas) if kind == "rel" else j)


def run(a):
    scene = glob.glob(os.path.join(a.bras, f"{a.hall}*"))[0]
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    mats = vb.read_bras_materials(os.path.join(a.bras, "3 Surface descriptions"), a.hall, a.coeffs, bands=BANDS)
    obj_path = os.path.join(out, f"{a.hall}_rotated.obj")
    if not os.path.exists(obj_path):
        with open(obj_path, "w", encoding="utf-8") as f:
            f.write(cb.rotate_obj(open(os.path.join(scene, "Geometry", f"{a.hall}.obj"), encoding="utf-8",
                                       errors="ignore").read()))
    ir, fs, E, R, eid, rid, _ = vb.read_rirs(scene)
    S = {f"LS{e}": cb.rot(E[j]) for j, e in enumerate(eid)}
    M = {f"MP{r}": cb.rot(R[i]) for i, r in enumerate(rid)}
    cfg = {"name": f"BRAS {a.hall}", "fs": 48000, "c": 343.5,
           "room": {"dims_m": [10, 10, 5], "absorption_octave": {"values": [0.2] * 6}, "air_absorption": True},
           "sources": {k: {"pos": v} for k, v in S.items()}, "receivers": dict(sorted(M.items())),
           "geometry": {"mesh": {"obj": obj_path, "axes": "y-up", "groups": {k: k for k in mats}, "voxel": 0.08},
                        "materials": {k: {"alpha": list(map(float, v["alpha"])), "s": list(map(float, v["s_oct"]))}
                                      for k, v in mats.items()},
                        "ism_order": 1, "rays": a.rays, "diffraction": False}}
    rows = []
    for j, e in enumerate(eid):
        src = f"LS{e}"
        H, cen = bp.energy_hists(cfg, src, list(M), t_max=3.0, n_rays=a.rays)
        bi = [int(np.argmin(np.abs(np.asarray(cen) - b))) for b in BANDS]
        for i, r in enumerate(rid):
            rec = f"MP{r}"
            x = ir[i, j]
            on = int(np.argmax(np.abs(x) > 0.1 * np.abs(x).max())) / fs
            pm = params(vb.measured_hist(x, fs, bands=BANDS), on)
            d = float(np.linalg.norm(np.subtract(M[rec], S[src])))
            ps = params(H[rec][bi], d / cfg["c"])
            for p in PARS:
                for k, b in enumerate(BANDS):
                    rows.append([a.hall, a.coeffs, src, rec, p, b, round(float(pm[p][k]), 4), round(float(ps[p][k]), 4)])
        print(f"{a.hall} {a.coeffs} {src} done", flush=True)
    path = os.path.join(out, f"rr_complex_{a.hall}_{a.coeffs}.csv")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["room", "coeffs", "source", "receiver", "parameter", "f_hz", "measured", "simulated"])
        w.writerows(rows)
    print("->", path)


def table(out):
    rr = list(csv.DictReader(open(os.path.join(out, "rr_ra.csv"))))
    lines = []
    for path in sorted(glob.glob(os.path.join(out, "rr_complex_CR*_*.csv"))):
        rows = list(csv.DictReader(open(path)))
        room, coeffs = rows[0]["room"], rows[0]["coeffs"]
        lines.append(f"\n### {room}, AuralPaths with BRAS {coeffs} materials\n")
        lines.append("| parameter | check: measured here vs figure (mean abs., JND) | A | B | C | D | E | F | AuralPaths |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        tot = {x: [] for x in "ABCDEF"}
        tot["AP"] = []
        for p in PARS:
            mh = np.array([np.nanmean([float(r["measured"]) for r in rows if r["parameter"] == p and int(r["f_hz"]) == b])
                           for b in BANDS])
            sh = np.array([np.nanmean([float(r["simulated"]) for r in rows if r["parameter"] == p and int(r["f_hz"]) == b])
                           for b in BANDS])
            fig = {c: np.array([next((float(r["value"]) for r in rr if r["room"] == room and r["parameter"] == p
                                      and int(r["f_hz"]) == b and r["curve"] == c), np.nan) for b in BANDS])
                   for c in ["measured"] + list("ABCDEF")}
            chk = np.nanmean(np.abs(err_jnd(p, mh, fig["measured"])))
            cells = []
            for c in "ABCDEF":
                e = np.abs(err_jnd(p, fig[c], fig["measured"]))
                cells.append(f"{np.nanmean(e):.1f}" + ("" if np.isfinite(e).all() else f" ({np.isfinite(e).sum()} bands)"))
                tot[c] += list(e[np.isfinite(e)])
            e = np.abs(err_jnd(p, sh, mh))
            tot["AP"] += list(e[np.isfinite(e)])
            lines.append(f"| {p} | {chk:.1f} | " + " | ".join(cells) + f" | {np.nanmean(e):.1f} |")
        lines.append("| **all four** | | " + " | ".join(f"**{np.mean(tot[c]):.1f}**" for c in "ABCDEF")
                     + f" | **{np.mean(tot['AP']):.1f}** |")
    txt = "\n".join(lines)
    print(txt)
    open(os.path.join(out, "rr_complex.md"), "w").write(txt + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras", nargs="?")
    ap.add_argument("hall", nargs="?", choices=["CR2", "CR3", "CR4"])
    ap.add_argument("--coeffs", default="initial", choices=["initial", "fitted"])
    ap.add_argument("--rays", type=int, default=6000)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "rs"))
    ap.add_argument("--table", default=None, help="only print the comparison table from the results in this folder")
    a = ap.parse_args()
    if a.table:
        table(a.table)
    else:
        run(a)


if __name__ == "__main__":
    main()
