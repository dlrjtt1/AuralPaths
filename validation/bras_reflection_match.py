"""
Discrete reflections in measured omnidirectional RIRs vs the model's specular paths (BRAS CR3 / CR4, RIR source LS1
-> MP1 - MP5). Step 1 of the reflection-strength calibration (validation/bras_reflection_fit.py).

    python validation/bras_reflection_match.py <BRAS folder> CR4 --config out/bras_cal16_CR4/config_cal.json
        [--order 6] [--rays 20000] [--window-ms 250] [--out out/refl_CR4]

Measured: per octave band (1 and 2 kHz), energy envelope in 1 ms frames; a reflection is a frame at least 6 dB above
the median of the surrounding +-10 ms and the largest within +-2 ms; level in dB re the direct sound (first 2 ms).
Model: specular paths of orders 1 - order (specpaths.find_paths) from the RIR source position to each receiver with
an omnidirectional source, energy with absorption, (1 - s) and the finite-reflector factor (specpaths.path_energy).
A measured reflection is matched to model arrivals within +-2.5 ms (energies of coinciding paths add up).
Writes paths.pkl (model paths, reused by the fit) and matches.csv.
"""
import argparse
import csv
import glob
import os
import pickle
import sys

import numpy as np
from scipy.signal import butter, sosfiltfilt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, ".."), HERE]
import brir_proto as bp            # noqa: E402
import check_bras_brir as cb       # noqa: E402
import specpaths                   # noqa: E402
import validate_bras_cr as vb      # noqa: E402

BANDS = (1000, 2000)
TOL_MS = 2.5


def measured_peaks(x, fs, fc, t_end):
    on = int(np.argmax(np.abs(x) > 0.1 * np.abs(x).max()))
    y = sosfiltfilt(butter(4, [fc / 2 ** 0.5, fc * 2 ** 0.5], "band", fs=fs, output="sos"), x)
    e = y[on - int(0.001 * fs):] ** 2
    w = int(0.001 * fs)
    env = np.add.reduceat(e, np.arange(0, len(e), w))[: int(t_end * 1000) + 12]
    d0 = env[:3].sum()
    L = 10 * np.log10(env / d0 + 1e-30)
    pk = []
    for k in range(15, len(L) - 11):              # from 14 ms after the direct sound
        med = np.median(L[k - 10:k + 11])
        if L[k] >= med + 6 and L[k] == L[k - 2:k + 3].max():
            pk.append((k - 1.0, float(L[k])))     # ms after direct (frame 1 = direct)
    return pk


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras"); ap.add_argument("hall")
    ap.add_argument("--config", required=True); ap.add_argument("--order", type=int, default=6)
    ap.add_argument("--rays", type=int, default=20000); ap.add_argument("--window-ms", type=float, default=250.0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(HERE, "..", "out", f"refl_{a.hall}")
    os.makedirs(out, exist_ok=True)
    scene = glob.glob(os.path.join(a.bras, f"{a.hall}*"))[0]
    ir, fs, E, R, eid, rid, _ = vb.read_rirs(scene)
    cfg = bp.load_config(a.config)
    j = list(eid).index(1)
    src = np.array(cb.rot(E[j]), float)
    recs = np.array([cb.rot(R[i]) for i in range(len(rid))], float)
    cfg["sources"] = {"LS1": {"pos": src.tolist()}}
    cfg["receivers"] = {f"MP{r}": recs[i].tolist() for i, r in enumerate(rid)}
    G = bp._geom(cfg)
    c = cfg["c"]
    d0 = np.linalg.norm(recs - src, axis=1)
    pk_path = os.path.join(out, "paths.pkl")
    if os.path.exists(pk_path):
        paths = pickle.load(open(pk_path, "rb"))
    else:
        paths = specpaths.find_paths(G, src, recs, order=a.order, t_max=d0 / c + a.window_ms / 1000, c=c,
                                     n_rays=a.rays, min_order=1)
        pickle.dump(paths, open(pk_path, "wb"))
    mats = cfg["geometry"]["materials"]
    rows = []
    for i, r in enumerate(rid):
        for bi, fc in enumerate(BANDS):
            meas = measured_peaks(ir[i, j], fs, fc, a.window_ms / 1000)
            arr = []
            for q in paths[i]:
                eb = specpaths.path_energy(G, mats, q, src, recs[i], [fc], [0.0], c)[0] * d0[i] ** 2
                arr.append((1000 * (q["dist"] - d0[i]) / c, eb, q))
            for t, Lm in meas:
                near = [x for x in arr if abs(x[0] - t) <= TOL_MS]
                Es = sum(x[1] for x in near)
                mats_used = ";".join("+".join(G["S"][f]["mat"].replace(f"mat_{a.hall}_", "") for f in x[2]["faces"]) for x in near)
                rows.append([f"MP{r}", fc, round(t, 1), round(Lm, 1), round(10 * np.log10(Es), 1) if Es > 0 else "",
                             round(Lm - 10 * np.log10(Es), 1) if Es > 0 else "", len(near), mats_used])
    with open(os.path.join(out, "matches.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["receiver", "band_hz", "t_ms_after_direct", "measured_db", "model_db", "measured_minus_model_db",
                    "n_paths", "paths"])
        w.writerows(rows)
    m = [r for r in rows if r[5] != ""]
    print(f"{len(rows)} measured reflections, {len(m)} matched; measured - model: median "
          f"{np.median([r[5] for r in m]):+.1f} dB, interquartile {np.percentile([r[5] for r in m], 25):+.1f} .. "
          f"{np.percentile([r[5] for r in m], 75):+.1f} dB" if m else f"{len(rows)} measured reflections, none matched")
    print("model paths per receiver:", [len(p) for p in paths], "->", os.path.join(out, "matches.csv"))


if __name__ == "__main__":
    main()
