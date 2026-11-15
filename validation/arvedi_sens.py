"""Arvedi (post hoc): sensitivity of the directional-source results to inputs that are not documented.

Runs arvedi_check.compare on a subset of the receivers for variants of the post hoc configuration and prints the bias
(EDT, C80, D50 at 125 Hz - 4 kHz) per variant:
    aim     loudspeaker tilt: el = --tilts (deg, + up; the aim in the dataset is not documented)
    volume  ceiling raised so that the model volume is the published 5300 m3, absorption recalibrated on S0 (T30)
            over the same receivers (calibrate.py, all groups)
    ism3    image-source order 3 instead of 2 (fewer receivers: --every-ism)

    python validation/arvedi_sens.py <arvedi data folder> [--sources S1,S4] [--every 3] [--tilts -10,-5,5]
           [--variants aim,volume,ism3] [--out out/arvedi_sens]
"""
import argparse
import copy
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path[:0] = [ROOT, HERE]
import arvedi_check as ac                     # noqa: E402
import arvedi_model as am                     # noqa: E402
import brir_proto as bp                       # noqa: E402

POSTHOC = os.path.join(ROOT, "out", "arvedi_posthoc")


def summary(D, label):
    for k in ("EDT", "C80", "D50"):
        kind, j = ac.JND[k]
        a = np.array([d[0] for d in D[k]]); x = np.array([d[1] for d in D[k]])
        err = (x - a) / a if kind == "rel" else x - a
        print(f"  {label:18s} {k:4s} " + " ".join(
            f"{(100 * np.nanmean(err[:, i]) if kind == 'rel' else np.nanmean(err[:, i])):+7.{0 if kind == 'rel' else 2}f}"
            for i in range(len(ac.BANDS))), flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data")
    ap.add_argument("--sources", default="S1,S4"); ap.add_argument("--every", type=int, default=3)
    ap.add_argument("--every-ism", type=int, default=6); ap.add_argument("--tilts", default="-10,-5,5")
    ap.add_argument("--variants", default="aim,volume,ism3")
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "arvedi_sens"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ac.TURN[:] = (-1.0, -1.0, 1.0)
    src, rec, H = ac.load(a.data)
    sub = {k: rec[k] for k in list(rec)[::a.every]}
    cfg = bp.load_config(os.path.join(POSTHOC, "config_cal.json"))
    cfg["receivers"] = {k: v.round(4).tolist() for k, v in sub.items()}
    srcs = a.sources.split(",")
    var = a.variants.split(",")
    print(f"{len(sub)} receivers; bias per band {ac.BANDS} (EDT %, C80 dB, D50)", flush=True)
    for s in srcs:
        print(f"\n{s}", flush=True)
        summary(ac.compare(cfg, src, sub, H, s, f"{s}_base", a.out), "base (el 0)")
        if "aim" in var:
            for t in map(float, a.tilts.split(",")):
                c = copy.deepcopy(cfg); c["sources"][s]["aim"]["el"] = t
                summary(ac.compare(c, src, sub, H, s, f"{s}_el{t:+.0f}", a.out), f"tilt {t:+.0f} deg")
    if "volume" in var:
        zc0 = am.ZC
        vol0 = bp._geom(cfg).get("volume")
        am.ZC = zc0 + (5300 - vol0) / (am.L * am.W)
        c = ac.config(src, sub, a.out, True, None)
        for k in ("S1", "S2", "S3", "S4"):
            c["sources"][k] = copy.deepcopy(cfg["sources"][k])
        c["geometry"]["materials"] = copy.deepcopy(json.load(open(os.path.join(POSTHOC, "config.json")))["geometry"]["materials"])
        p = os.path.join(a.out, "config_vol.json"); json.dump(c, open(p, "w"), indent=1)
        t30 = os.path.join(a.out, "t30_S0_sub.csv")
        import csv
        with open(os.path.join(POSTHOC, "t30_S0.csv")) as f, open(t30, "w", newline="") as g:
            r = csv.reader(f); w = csv.writer(g); w.writerow(next(r))
            for row in r:
                if row[0][3:] in sub:
                    w.writerow(row)
        cal = os.path.join(a.out, "config_vol_cal.json")
        subprocess.run([sys.executable, os.path.join(ROOT, "calibrate.py"), p, t30, "--out", cal, "--iter", "4"], check=True, cwd=ROOT)
        cv = bp.load_config(cal)
        print(f"\nvolume variant: ceiling {zc0:.2f} -> {am.ZC:.2f} m, model volume {bp._geom(cv).get('volume'):.0f} m3", flush=True)
        for s in ["S0"] + srcs:
            summary(ac.compare(cv, src, sub, H, s, f"{s}_vol", a.out), f"{s} volume 5300")
        am.ZC = zc0
    if "ism3" in var:
        sub3 = {k: rec[k] for k in list(rec)[::a.every_ism]}
        c = copy.deepcopy(cfg); c["receivers"] = {k: v.round(4).tolist() for k, v in sub3.items()}
        print(f"\nimage-source order, {len(sub3)} receivers", flush=True)
        for s in srcs:
            summary(ac.compare(c, src, sub3, H, s, f"{s}_ism2_sub", a.out), f"{s} order 2")
            c3 = copy.deepcopy(c); c3["geometry"]["ism_order"] = 3
            summary(ac.compare(c3, src, sub3, H, s, f"{s}_ism3_sub", a.out), f"{s} order 3")


if __name__ == "__main__":
    main()
