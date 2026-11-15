"""
Arvedi: does the PLACEMENT of the absorption explain the early-decay error? (diagnostic, 2026-11-15)

Arvedi S0 (omnidirectional), 65 receivers, the page's engine (engine_js.py), 20000 rays, one seed kept for all runs.
Start: the config calibrated on T30 with one factor per band on all materials (out/arvedi_js/config_cal.json), where
the simulated EDT is longer than T30 (EDT / T30 1.08) and the measured one shorter (0.84 - 0.92).

Fixed before the run: the absorption of the surfaces near the source and the listeners (seating "aud", "stage",
"floor"; 1089 m2) is multiplied by r relative to the rest (walls, ceiling, windows, shell; 3732 m2), r = 0.5, 0.71,
1, 1.41, 2. For every r a common factor per octave band on ALL materials is recalibrated so that the median T30 of
the 65 receivers matches the measured median within 2 % (at most 6 iterations; coefficients kept in 0.01 - 0.95).
T30 is thus the same in every run; reported: EDT, EDT / T30, C80 and T20 against the measurement.

    python validation/arvedi_placement.py <calibrated config.json> <compare_S0_primary.csv of the same run> [--out out/arvedi_placement]

The measured criteria are read from the compare CSV of arvedi_check.py (columns receiver, metric, band_hz, measured).
"""
import argparse
import copy
import csv
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path[:0] = [ROOT, HERE]
import brir_proto as bp                       # noqa: E402
import engine_js                              # noqa: E402
from arvedi_check import metrics              # noqa: E402

BANDS = [125, 250, 500, 1000, 2000, 4000]
NEAR = ("aud", "stage", "floor")
RATIOS = (0.5, 0.71, 1.0, 1.41, 2.0)
RAYS, SEED = 20000, 1
JND = {"EDT": 5.0, "T20": 5.0, "T30": 5.0, "C80": 1.0}


def simulate(cfg, recs):
    H, cen = engine_js.energy_hists(cfg, "S0", recs, t_max=2.0, n_rays=RAYS, seed=SEED)
    bi = [int(np.argmin(np.abs(np.asarray(cen) - b))) for b in BANDS]
    out = {}
    for r in recs:
        t0 = np.linalg.norm(np.subtract(cfg["sources"]["S0"]["pos"], cfg["receivers"][r])) / cfg["c"]
        out[r] = metrics(H[r][bi], t0)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config"); ap.add_argument("compare"); ap.add_argument("--out", default=os.path.join(ROOT, "out", "arvedi_placement"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    lf = open(os.path.join(a.out, "run.log"), "w")

    def log(s):
        print(s, flush=True); lf.write(s + "\n"); lf.flush()
    cfg0 = bp.load_config(a.config)
    M = {}
    for row in csv.DictReader(open(a.compare)):
        M.setdefault(row["receiver"], {}).setdefault(row["metric"], {})[int(float(row["band_hz"]))] = float(row["measured"])
    recs = [r for r in cfg0["receivers"] if r in M]
    base = {k: np.asarray(v["alpha"][:6], float) for k, v in cfg0["geometry"]["materials"].items()}
    tm = np.array([np.nanmedian([M[r]["T30"][b] for r in recs]) for b in BANDS])
    log(f"{len(recs)} receivers; measured median T30 " + " ".join(f"{x:.2f}" for x in tm) + "; measured EDT / T30 "
        + " ".join(f"{np.nanmean([M[r]['EDT'][b] / M[r]['T30'][b] for r in recs]):.2f}" for b in BANDS))
    rows = []
    for ratio in RATIOS:
        k = np.ones(6)
        for it in range(6):
            c = copy.deepcopy(cfg0)
            clipped = []
            for g, al in base.items():
                raw = al * k * (ratio if g in NEAR else 1.0)
                v = np.clip(raw, 0.01, 0.95)
                if np.any(v != raw):
                    clipped.append(g)
                full = list(c["geometry"]["materials"][g]["alpha"])
                c["geometry"]["materials"][g]["alpha"] = v.round(4).tolist() + [float(v[-1].round(4))] * max(0, len(full) - 6)
            S = simulate(c, recs)
            ts = np.array([np.nanmedian([S[r]["T30"][i] for r in recs]) for i in range(6)])
            err = ts / tm - 1
            if np.all(np.abs(err) <= 0.02) or it == 5:
                break
            k = k * ts / tm
        log(f"\nr = {ratio}: {it + 1} iteration(s), T30 error % " + " ".join(f"{100 * x:+.1f}" for x in err) + "; factor "
            + " ".join(f"{x:.2f}" for x in k) + (f"; at the 0.01 / 0.95 limit: {', '.join(clipped)}" if clipped else ""))
        log("  seating alpha " + " ".join(f"{x:.2f}" for x in c["geometry"]["materials"]["aud"]["alpha"][:6])
            + " | wall alpha " + " ".join(f"{x:.2f}" for x in c["geometry"]["materials"]["wall"]["alpha"][:6]))
        for q, u in (("EDT", "%"), ("T20", "%"), ("C80", "dB")):
            line = f"  {q} bias"
            for i, b in enumerate(BANDS):
                s = np.array([S[r][q][i] for r in recs]); m = np.array([M[r][q][b] for r in recs])
                d = 100 * (s / m - 1) if u == "%" else s - m
                ok = np.isfinite(d)
                line += f"  {b}: {np.mean(d[ok]):+.1f} {u} ({100 * np.mean(np.abs(d[ok]) <= JND[q]):.0f} %)"
                rows.append({"ratio": ratio, "metric": q, "band_hz": b, "bias": float(np.mean(d[ok])), "unit": u,
                             "within_jnd": float(np.mean(np.abs(d[ok]) <= JND[q])), "factor": float(k[i]), "clipped": ",".join(clipped)})
            log(line)
        er = [np.nanmean([S[r]["EDT"][i] / S[r]["T30"][i] for r in recs]) for i in range(6)]
        log("  EDT / T30 simulated " + " ".join(f"{x:.2f}" for x in er))
        for i, b in enumerate(BANDS):
            rows.append({"ratio": ratio, "metric": "EDT/T30", "band_hz": b, "bias": float(er[i]), "unit": "", "within_jnd": "", "factor": float(k[i]), "clipped": ",".join(clipped)})
    with open(os.path.join(a.out, "summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
