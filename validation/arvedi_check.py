"""
Blind check in the Auditorium Giovanni Arvedi, Cremona (validation/arvedi_protocol.md): the simplified model of
validation/arvedi_model.py, BRAS CR3 materials, absorption calibrated on the measured T30 of the omnidirectional
source, then EDT, T20, C80, D50, Ts compared per receiver and octave band.

Data: https://doi.org/10.5281/zenodo.20098848 (CC BY 4.0). The measured RIRs are reduced first to octave-band energy
histograms averaged over the 8 capsules (the measured_hist of validate_bras_cr.py per capsule; a copy that runs
without this repository is the hist.py written next to the data); this script reads those histograms:

    python validation/arvedi_check.py <folder with pos_sources.csv, pos_receivers.csv, meas_hist_*.npz> [--out out/arvedi]
        [--skip-cal]      reuse <out>/config_cal.json

Writes <out>/config.json, <out>/t30_S0.csv (calibration targets), <out>/config_cal.json (calibrate.py),
<out>/compare_<run>.csv and prints the summary.
"""
import argparse
import copy
import csv
import glob
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path[:0] = [ROOT, HERE]
import arvedi_model as am                     # noqa: E402
import brir_proto as bp                       # noqa: E402
from validate_fratoni import BANDS, criteria  # noqa: E402

OFFSET = np.array([22.05, 7.0, 0.0])          # dataset -> model (protocol item 8)
C = 343.0
RAYS, ISM = 20000, 3
JND = {"EDT": ("rel", 0.05), "T20": ("rel", 0.05), "T30": ("rel", 0.05), "C80": ("abs", 1.0), "D50": ("abs", 0.05),
       "Ts": ("abs", 10.0)}
CR3 = {"aud": "mat_CR3_seating", "wall": "mat_CR3_plaster", "ceiling": "mat_CR3_ceiling", "window": "mat_CR3_windows",
       "floor": "mat_CR3_floor", "stage": "mat_CR3_floor", "shell": "mat_CR3_stagePanels"}


def metrics(h, t0):
    """criteria (EDT, T30, C80, C50, Ts) plus T20 and D50 from octave histograms h [6, n] (1 ms bins)."""
    m = criteria(h, t0)
    t20 = []
    i0 = int(np.floor(t0 / bp.HIST_BIN))
    for e in h:
        e = np.asarray(e[i0:], float)
        t = (np.arange(len(e)) + 0.5) * bp.HIST_BIN
        edc = 10 * np.log10(np.maximum(np.cumsum(e[::-1])[::-1] / e.sum(), 1e-30))
        sel = (edc <= -5) & (edc >= -25)
        t20.append(-60 / np.polyfit(t[sel], edc[sel], 1)[0] if sel.sum() > 10 and edc.min() < -35 else np.nan)
    m["T20"] = np.array(t20)
    m["D50"] = 1 / (1 + 10 ** (-m["C50"] / 10))
    return m


def load(folder):
    src = {r["source"]: np.array([float(r["x"]), float(r["y"]), float(r["z"])]) + OFFSET
           for r in csv.DictReader(open(os.path.join(folder, "pos_sources.csv")), delimiter=";")}
    rec = {r["mic"]: np.array([float(r["C_x"]), float(r["C_y"]), float(r["C_z"])]) + OFFSET
           for r in csv.DictReader(open(os.path.join(folder, "pos_receivers.csv")), delimiter=";")}
    H = {}
    for f in sorted(glob.glob(os.path.join(folder, "meas_hist_*.npz"))):
        H.update(dict(np.load(f)))
    return src, rec, H


def config(src, rec, out):
    o = am.build()
    obj = os.path.join(out, "arvedi.obj")
    o.write(obj)
    mats = json.load(open(os.path.join(ROOT, "examples", "bras_cr3", "bras_cr3_config.json")))["geometry"]["materials"]
    cfg = {"name": "Auditorium Giovanni Arvedi (simplified model, blind check)",
           "_note": "validation/arvedi_protocol.md; data https://doi.org/10.5281/zenodo.20098848 (CC BY 4.0); "
                    "materials BRAS CR3 by analogy (CC BY-SA 4.0)",
           "fs": 48000, "c": C,
           "room": {"dims_m": [am.L, am.W, am.ZC], "absorption_octave": {"values": [0.2] * 6}, "air_absorption": True},
           "sources": {"S0": {"pos": src["S0"].round(4).tolist()}},
           "receivers": {k: v.round(4).tolist() for k, v in rec.items()},
           "geometry": {"mesh": {"obj": obj, "obj_text": open(obj).read(), "axes": "z-up",
                                 "groups": {k: k for k in CR3}},
                        "materials": {k: {"alpha": list(map(float, mats[v]["alpha"])), "s": list(map(float, mats[v]["s"]))}
                                      for k, v in CR3.items()},
                        "ism_order": ISM, "rays": RAYS, "diffraction": False},
           "binaural": {"sofa_path": "", "early_window_ms": 100.0, "crossfade_ms": 10.0, "ism_order_early": 12,
                        "ism_order_omni": 60}}
    for k in ("S1", "S2", "S3", "S4"):
        cfg["sources"][k] = {"pos": src[k].round(4).tolist(), "coverage": 90.0, "aim": {"az": 90.0, "el": 0.0},
                             "role": "generic 90 degree loudspeaker, aimed along +x (assumed; protocol item 11)"}
    return cfg


def compare(cfg, src, rec, H, s, label, out):
    Hs, cen = bp.energy_hists(cfg, s, list(rec), t_max=2.0, n_rays=RAYS)
    bi = [int(np.argmin(np.abs(np.asarray(cen) - b))) for b in BANDS]
    rows, D = [], {k: [] for k in JND}
    for r in rec:
        t0 = np.linalg.norm(src[s] - rec[r]) / C
        mm, ms = metrics(H[f"{s}-{r}"], t0), metrics(Hs[r][bi], t0)
        for k in JND:
            rows += [[r, k, b, round(float(a), 4), round(float(x), 4)] for b, a, x in zip(BANDS, mm[k], ms[k])]
            D[k].append((mm[k], ms[k]))
    with open(os.path.join(out, f"compare_{label}.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["receiver", "metric", "band_hz", "measured", "simulated"])
        w.writerows(rows)
    print(f"\n{label} (source {s}, {len(rec)} receivers): measured mean / simulated mean / bias / within 1 JND / mean |error| in JND")
    for k, (kind, j) in JND.items():
        a = np.array([d[0] for d in D[k]]); x = np.array([d[1] for d in D[k]])
        err = (x - a) / a if kind == "rel" else x - a
        jn = np.abs(err) / j
        print(f"  {k:4s} " + "  ".join(
            f"{b}: {np.nanmean(a[:, i]):.2f}/{np.nanmean(x[:, i]):.2f} "
            f"{(100 * np.nanmean(err[:, i]) if kind == 'rel' else np.nanmean(err[:, i])):+.{0 if kind == 'rel' else 2}f}"
            f"{'%' if kind == 'rel' else ''} {100 * np.nanmean(jn[:, i] <= 1):.0f}% {np.nanmean(jn[:, i]):.1f}"
            for i, b in enumerate(BANDS)))
    return D


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data")
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "arvedi"))
    ap.add_argument("--skip-cal", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    src, rec, H = load(a.data)
    cfg = config(src, rec, a.out)
    json.dump(cfg, open(os.path.join(a.out, "config.json"), "w"), indent=1)
    t30 = os.path.join(a.out, "t30_S0.csv")
    with open(t30, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["label", "src_x", "src_y", "src_z", "rec_x", "rec_y", "rec_z", "band_hz", "T30_s", "EDT_s"])
        for r in rec:
            m = metrics(H[f"S0-{r}"], np.linalg.norm(src["S0"] - rec[r]) / C)
            for b, t, e in zip(BANDS, m["T30"], m["EDT"]):
                if np.isfinite(t):
                    w.writerow([f"S0_{r}", *src["S0"].round(4), *rec[r].round(4), b, round(float(t), 4),
                                round(float(e), 4) if np.isfinite(e) else ""])
    cal = os.path.join(a.out, "config_cal.json")
    if not a.skip_cal:
        subprocess.run([sys.executable, os.path.join(ROOT, "calibrate.py"), os.path.join(a.out, "config.json"), t30,
                        "--out", cal, "--iter", "6"], check=True, cwd=ROOT)
    cfg = bp.load_config(cal)
    print(f"model volume {bp._geom(cfg).get('volume', float('nan')):.0f} m3 (published 5300 m3)")
    compare(cfg, src, rec, H, "S0", "S0_primary", a.out)
    c2 = copy.deepcopy(cfg)
    c2["geometry"]["seat_dip"] = {"on": True}
    c2["geometry"]["mesh"]["rotate_deg"] = 90.0       # rows across the hall (normal along x)
    compare(c2, src, rec, H, "S0", "S0_seatdip", a.out)
    for s in ("S1", "S2", "S3", "S4"):
        compare(cfg, src, rec, H, s, f"{s}_directional", a.out)


if __name__ == "__main__":
    main()
