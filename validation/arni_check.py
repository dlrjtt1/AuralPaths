"""
Arni variable-acoustics room (Aalto): does the engine get the early decay (EDT, EDT / T30, C80) right in a room whose
absorption sits in known places, and does it follow where the absorption is?

Data: https://doi.org/10.5281/zenodo.6985104 (CC BY 4.0), the part numClosed 46 - 55 (0 - 9 of the 55 panels open,
i.e. absorptive). The RIRs are reduced on the data side to octave-band energy histograms (1 ms bins, energy mean over
the up to 5 sweeps, onset moved to the geometric direct-sound time; arni_hist.py, as validate_bras_cr.measured_hist),
files arni_hist_nc<NN>[_p<k>].npz with keys "<combination>-<mic>", plus combinations_setup.csv of the dataset.

Model: validation/arni_model.py. Panel fronts: published absorption of the open and closed state (125 Hz assumed equal
to 250 Hz). The rest (bare walls, floor, ceiling: "shell"; folded curtains) is unknown and calibrated, one factor per
octave band on the T30 of the all-closed state (combination 0, five microphones); every other state is then
predicted without further calibration.

    python validation/arni_check.py <folder with arni_hist_*.npz, combinations_setup.csv> [--out out/arni]
        [--per-nc 4] [--rays 20000] [--skip-cal] [--resume]

Writes <out>/config.json, t30_cal.csv, config_cal.json, sim_<nc>_<comb>.npz (simulated histograms), results.csv
(measured and simulated EDT, T20, T30, C80, D50, Ts per combination, microphone and band) and prints the summary.
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
import arni_model as am                       # noqa: E402
import brir_proto as bp                       # noqa: E402
from arvedi_check import metrics              # noqa: E402
from validate_fratoni import BANDS            # noqa: E402

C = 343.0
S_FRONT, S_SHELL, S_SIDE, S_CURTAIN = 0.10, 0.05, 0.05, 0.5     # scattering: assumptions
A_SHELL, A_CURTAIN = 0.02, 0.5                                  # start values of the calibrated groups (assumptions)


def load(folder):
    H = {}
    for f in sorted(glob.glob(os.path.join(folder, "arni_hist_nc*.npz"))):
        nc = int(os.path.basename(f)[12:14])
        for k, v in np.load(f).items():
            cb, mic = k.split("-")
            H[(nc, int(cb), mic)] = v.astype(float)
    rows = [r.strip().split(";") for r in open(os.path.join(folder, "combinations_setup.csv"), encoding="utf-8-sig")]
    rows = [r for r in rows if r and r[0].isdigit()]
    setup = {int(r[0]): np.array([float(x) for x in r[1:56]]) for r in rows}   # 1 = open (absorptive)
    return H, setup


def config(setup_row, obj_text):
    mats = {"shell": {"alpha": [A_SHELL] * 6, "s": [S_SHELL] * 6},
            "curtain": {"alpha": [A_CURTAIN] * 6, "s": [S_CURTAIN] * 6},
            "side": {"alpha": list(am.ALPHA_CLOSED), "s": [S_SIDE] * 6}}
    for n in range(1, 56):
        a = am.ALPHA_OPEN if setup_row[n - 1] > 0.5 else am.ALPHA_CLOSED
        mats[f"p{n}"] = {"alpha": list(a), "s": [S_FRONT] * 6}
    return {"name": "Arni variable acoustics room (validation/arni_check.py)",
            "_note": "data https://doi.org/10.5281/zenodo.6985104 (CC BY 4.0); model validation/arni_model.py",
            "fs": 44100, "c": C,
            "room": {"dims_m": [am.L, am.W, am.H], "absorption_octave": {"values": [0.1] * 6}, "air_absorption": True},
            "sources": {"S": {"pos": list(am.SRC)}},
            "receivers": {k: list(v) for k, v in am.MICS.items()},
            "geometry": {"mesh": {"obj": "arni.obj", "obj_text": obj_text, "axes": "z-up", "groups": {k: k for k in mats}},
                         "materials": mats, "ism_order": 2, "rays": 10000, "diffraction": False}}


def with_setup(cfg_cal, setup_row):
    c = copy.deepcopy(cfg_cal)
    for n in range(1, 56):
        c["geometry"]["materials"][f"p{n}"]["alpha"] = list(am.ALPHA_OPEN if setup_row[n - 1] > 0.5 else am.ALPHA_CLOSED)
    return c


def t0(mic):
    return float(np.linalg.norm(np.subtract(am.MICS[mic], am.SRC)) / C)


def pick(H, setup, per_nc, seed=1):
    """Per number of closed panels: the combinations with the fewest and the most open ceiling panels, the rest at
    random (a fixed seed)."""
    rng = np.random.default_rng(seed)
    ceil = np.array([v[0] == "ceiling" for _, v in sorted(am.panels().items())])
    out = []
    for nc in range(46, 55):
        cbs = sorted({k[1] for k in H if k[0] == nc and all((nc, k[1], m) in H for m in am.MICS)})
        if not cbs:
            continue
        fc = np.array([setup[c][ceil].sum() for c in cbs])
        sel = [cbs[int(np.argmin(fc))], cbs[int(np.argmax(fc))]]
        rest = [c for c in cbs if c not in sel]
        sel += list(rng.choice(rest, size=min(per_nc - 2, len(rest)), replace=False))
        out += [(nc, int(c)) for c in sel]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data"); ap.add_argument("--out", default=os.path.join(ROOT, "out", "arni"))
    ap.add_argument("--per-nc", type=int, default=4); ap.add_argument("--rays", type=int, default=10000)
    ap.add_argument("--skip-cal", action="store_true"); ap.add_argument("--resume", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    H, setup = load(a.data)
    obj = am.build()
    cfg = config(setup[0], obj)
    cfg["geometry"]["rays"] = a.rays
    cal = os.path.join(a.out, "config_cal.json")
    if not a.skip_cal:
        json.dump(cfg, open(os.path.join(a.out, "config.json"), "w"), indent=1)
        with open(os.path.join(a.out, "t30_cal.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["label", "src_x", "src_y", "src_z", "rec_x", "rec_y", "rec_z", "band_hz", "T30_s", "EDT_s"])
            for mic, p in am.MICS.items():
                m = metrics(H[(55, 0, mic)], t0(mic))
                for b, t, e in zip(BANDS, m["T30"], m["EDT"]):
                    w.writerow([f"S-{mic}", *am.SRC, *p, b, round(float(t), 4), round(float(e), 4)])
        subprocess.run([sys.executable, os.path.join(ROOT, "calibrate.py"), os.path.join(a.out, "config.json"),
                        os.path.join(a.out, "t30_cal.csv"), "--adjust", "shell,curtain", "--out", cal], check=True)
    cfg_cal = bp.load_config(cal)
    runs = [(55, 0)] + pick(H, setup, a.per_nc)
    res = os.path.join(a.out, "results.csv")
    rows = []
    for nc, cb in runs:
        f = os.path.join(a.out, f"sim_{nc}_{cb}.npz")
        if not (a.resume and os.path.exists(f)):
            Hs, cen = bp.energy_hists(with_setup(cfg_cal, setup[cb]), "S", list(am.MICS), t_max=2.0, n_rays=a.rays)
            bi = [int(np.argmin(np.abs(np.asarray(cen) - b))) for b in BANDS]
            np.savez_compressed(f, **{m: np.asarray(Hs[m])[bi] for m in am.MICS})
        S = np.load(f)
        for mic in am.MICS:
            mm, ms = metrics(H[(nc, cb, mic)], t0(mic)), metrics(S[mic], t0(mic))
            for k in ("EDT", "T20", "T30", "C80", "D50", "Ts"):
                rows += [[nc, cb, mic, k, b, float(x), float(y)] for b, x, y in zip(BANDS, mm[k], ms[k])]
        print(f"numClosed {nc}, combination {cb} done", flush=True)
    with open(res, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["num_closed", "combination", "mic", "metric", "band_hz", "measured", "simulated"])
        w.writerows(rows)
    summary(res)


def summary(res):
    R = list(csv.DictReader(open(res)))
    get = lambda k: np.array([[float(r["measured"]), float(r["simulated"])] for r in R if r["metric"] == k]).reshape(-1, 6, 2)
    E, T, C8 = get("EDT"), get("T30"), get("C80")
    lab = "  ".join(f"{b:>9}" for b in BANDS)
    print(f"\n{len(E)} combination x microphone pairs; bands {lab}")
    with np.errstate(invalid="ignore"):
        print("T30 bias %     " + "  ".join(f"{v:+9.0f}" for v in 100 * np.nanmean(T[..., 1] / T[..., 0] - 1, 0)))
        print("EDT bias %     " + "  ".join(f"{v:+9.0f}" for v in 100 * np.nanmean(E[..., 1] / E[..., 0] - 1, 0)))
        print("EDT/T30 meas   " + "  ".join(f"{v:9.2f}" for v in np.nanmean(E[..., 0] / T[..., 0], 0)))
        print("EDT/T30 sim    " + "  ".join(f"{v:9.2f}" for v in np.nanmean(E[..., 1] / T[..., 1], 0)))
        d = C8[..., 1] - C8[..., 0]
        d[~np.isfinite(d)] = np.nan
        print("C80 bias dB    " + "  ".join(f"{v:+9.2f}" for v in np.nanmean(d, 0)))
        print("C80 within 1dB " + "  ".join(f"{v:8.0f}%" for v in 100 * np.nanmean(np.abs(d) <= 1, 0)))
        print("EDT within 5 % " + "  ".join(f"{v:8.0f}%" for v in 100 * np.nanmean(np.abs(E[..., 1] / E[..., 0] - 1) <= 0.05, 0)))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        summary(sys.argv[2])
    else:
        main()
