"""
Does the scattering coefficient change the simulated EFFECT of a reinforcement condition? (diagnostic)

For one hall, two calibrated configurations that differ only in the scattering of the hard surfaces (each calibrated
on the measured T30 by itself), a stage source A and two reinforcement loudspeakers B_L / B_R (all omnidirectional,
positions fixed in HALLS below, chosen before the run) are simulated at the hall's measurement receivers. For every
condition (delay and level of B as in run.py / brir_proto.condition_params) the change of a criterion against A alone,
Delta = metric(A + B) - metric(A), is computed per receiver and octave band (EDT as ratio in %, C80 in dB), and the
two configurations are compared:

    d = Delta(scattering 0.5) - Delta(default)        per receiver

A third run of the default configuration with another ray seed gives the ray noise of d.

    python validation/scatter_delta.py <hall> <config_default> <config_s05> --out out/scatter_delta/<hall>
        [--rays 20000]
"""
import argparse
import csv
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import brir_proto as bp                       # noqa: E402

# positions fixed before the run (engineering choices, not taken from a real installation):
# A on the stage centre line at the height of the measured sources; B_L / B_R at the front of the stage, 5.5 - 6 m
# to either side of the centre line, about 2 - 3.5 m above the stage floor.
HALLS = {
    "opera": {"A": [12.83, -0.8, 1.6], "B_L": [6.83, -0.5, 4.0], "B_R": [18.83, -0.5, 4.0]},
    "detmold": {"A": [8.9, 30.8, 2.4], "B_L": [3.4, 28.8, 4.5], "B_R": [14.4, 28.8, 4.5]},
    "arvedi": {"A": [22.0, 7.0, 1.4], "B_L": [19.8, 3.0, 3.5], "B_R": [19.8, 11.0, 3.5]},
}
ITDG_MS = [0, 30, 60]
LEVEL_DB = [0, 6]
BANDS = [500, 1000, 2000, 4000]
JND = {"EDT": 5.0, "C80": 1.0}


def setup(path, hall):
    cfg = json.load(open(path))
    p = HALLS[hall]
    cfg["sources"] = {bp.AMP: {"pos": p["A"]}, "B_L": {"pos": p["B_L"]}, "B_R": {"pos": p["B_R"]}}
    R = np.array(list(cfg["receivers"].values()), float)
    names = list(cfg["receivers"])
    ref = names[int(np.argmin(np.linalg.norm(R - R.mean(0), axis=1)))]
    cfg["conditions"] = {"itdg_ms": ITDG_MS, "level_ratio_db": LEVEL_DB, "reference_receiver": ref}
    return cfg


def simulate(cfg, rays, seed):
    recs = list(cfg["receivers"])
    hist = {}
    for s in (bp.AMP, "B_L", "B_R"):
        h, centers = bp.energy_hists(cfg, s, recs, n_rays=rays, seed=seed)
        for r in recs:
            hist[(s, r)] = h[r]
    return hist, centers


def metrics(cfg, hist, centers):
    """{(cond, receiver, metric, band): value}; cond 'A' = A alone, else (itdg, level)."""
    recs = list(cfg["receivers"])
    ref = cfg["conditions"]["reference_receiver"]
    ib = [int(np.argmin(np.abs(np.asarray(centers) - b))) for b in (500, 1000)]
    E = lambda h: float(h[ib].sum())
    E_A, E_B = E(hist[(bp.AMP, ref)]), E(hist[("B_L", ref)]) + E(hist[("B_R", ref)])
    out = {}
    for r in recs:
        t0 = bp.direct_time(cfg, bp.AMP, r)
        for b in BANDS:
            m = bp.iso3382_energy([(hist[(bp.AMP, r)], 0.0, 1.0)], t0, bands=(b,), centers=centers)
            out[("A", r, "EDT", b)], out[("A", r, "C80", b)] = m["EDT"], m["C80"]
    for itdg in ITDG_MS:
        for lr in LEVEL_DB:
            p = bp.condition_params(cfg, itdg, lr, E_A, E_B)
            g2 = p["gain_B"] ** 2
            for r in recs:
                t0 = min(bp.direct_time(cfg, bp.AMP, r) + p["delay_A_s"],
                         bp.direct_time(cfg, "B_L", r) + p["delay_B_s"], bp.direct_time(cfg, "B_R", r) + p["delay_B_s"])
                parts = [(hist[(bp.AMP, r)], p["delay_A_s"], 1.0), (hist[("B_L", r)], p["delay_B_s"], g2),
                         (hist[("B_R", r)], p["delay_B_s"], g2)]
                for b in BANDS:
                    m = bp.iso3382_energy(parts, t0, bands=(b,), centers=centers)
                    out[((itdg, lr), r, "EDT", b)], out[((itdg, lr), r, "C80", b)] = m["EDT"], m["C80"]
    return out


def delta(m, cond, r, metric, b):
    a, x = m[("A", r, metric, b)], m[(cond, r, metric, b)]
    return 100 * (x / a - 1) if metric == "EDT" else x - a


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("hall", choices=sorted(HALLS)); ap.add_argument("config_default"); ap.add_argument("config_s05")
    ap.add_argument("--out", required=True); ap.add_argument("--rays", type=int, default=20000)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    runs = {"default": (a.config_default, 1), "s05": (a.config_s05, 1), "default_seed2": (a.config_default, 2)}
    M = {}
    for name, (path, seed) in runs.items():
        t = time.time()
        cfg = setup(path, a.hall)
        hist, centers = simulate(cfg, a.rays, seed)
        M[name] = metrics(cfg, hist, centers)
        print(f"{name}: {time.time() - t:.0f} s, reference receiver {cfg['conditions']['reference_receiver']}", flush=True)
    recs = list(cfg["receivers"])
    rows = []
    for r in recs:
        for metric in JND:
            for b in BANDS:
                rows.append({"cond": "A", "receiver": r, "metric": metric, "band_hz": b,
                             **{f"abs_{n}": M[n][("A", r, metric, b)] for n in runs}})
                for itdg in ITDG_MS:
                    for lr in LEVEL_DB:
                        c = (itdg, lr)
                        rows.append({"cond": f"itdg{itdg}_lr{lr:+d}", "receiver": r, "metric": metric, "band_hz": b,
                                     **{f"abs_{n}": M[n][(c, r, metric, b)] for n in runs},
                                     **{f"delta_{n}": delta(M[n], c, r, metric, b) for n in runs}})
    with open(os.path.join(a.out, "scatter_delta.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[-1])); w.writeheader(); w.writerows(rows)
    # summary
    print(f"\n{a.hall}: d = Delta(s 0.5) - Delta(default); noise = Delta(seed 2) - Delta(seed 1); "
          f"abs = metric(s 0.5) - metric(default) for A alone. mean / share of receivers within 1 JND")
    for metric, j in JND.items():
        u = "%" if metric == "EDT" else " dB"
        for b in BANDS:
            ab = [M["s05"][("A", r, metric, b)] - M["default"][("A", r, metric, b)] if metric == "C80" else
                  100 * (M["s05"][("A", r, metric, b)] / M["default"][("A", r, metric, b)] - 1) for r in recs]
            ab = np.array(ab, float); ab = ab[np.isfinite(ab)]
            line = f"  {metric} {b:4d}: abs {ab.mean():+.2f}{u} {100*np.mean(np.abs(ab) <= j):3.0f}% |"
            for itdg in ITDG_MS:
                for lr in LEVEL_DB:
                    c = (itdg, lr)
                    d = np.array([delta(M["s05"], c, r, metric, b) - delta(M["default"], c, r, metric, b) for r in recs])
                    n = np.array([delta(M["default_seed2"], c, r, metric, b) - delta(M["default"], c, r, metric, b)
                                  for r in recs])
                    ok = np.isfinite(d) & np.isfinite(n)
                    line += (f" {itdg}/{lr:+d}: {d[ok].mean():+.2f} {100*np.mean(np.abs(d[ok]) <= j):3.0f}%"
                             f" (n {100*np.mean(np.abs(n[ok]) <= j):3.0f}%)")
            print(line, flush=True)


if __name__ == "__main__":
    main()
