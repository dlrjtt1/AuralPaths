"""Arvedi (post hoc, diagnostic): does the scattering of the model decide whether the early decay is faster than the
late one?

The measured EDT in Arvedi is 15 - 20 % shorter than T30 (the first 10 dB fall faster), the simulated EDT is about T30.
One hypothesis: the model scatters the early energy too much, so that energy which in the hall goes straight into the
absorbing seating is spread over the hard surfaces first. This runs S0 on a subset of the receivers with the
calibrated post hoc configuration (out/arvedi_posthoc_norain) and with the scattering changed, without recalibrating:
    base        as calibrated (seating 0.21 - 0.99, other surfaces 0.05 - 0.24)
    aud_x0.3    seating scattering times 0.3
    all_0.05    every surface 0.05 (nearly specular)
    all_x2      every surface times 2 (at most 0.99)
Printed per band: EDT / T30 measured and simulated (mean over receivers of the ratio), and the bias of EDT, T30, C80.

    python validation/arvedi_scatter.py <arvedi data folder> [--every 3] [--variants base,aud_x0.3,all_0.05,all_x2]
"""
import argparse
import copy
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path[:0] = [ROOT, HERE]
import arvedi_check as ac                     # noqa: E402
import brir_proto as bp                       # noqa: E402

CAL = os.path.join(ROOT, "out", "arvedi_posthoc_norain", "config_cal.json")


def variant(cfg, name):
    c = copy.deepcopy(cfg)
    for k, m in c["geometry"]["materials"].items():
        s = np.asarray(m["s"], float)
        if name == "aud_x0.3" and k == "aud":
            s = s * 0.3
        elif name == "all_0.05":
            s = np.full_like(s, 0.05)
        elif name == "all_x2":
            s = np.minimum(s * 2, 0.99)
        m["s"] = [round(float(x), 4) for x in s]
    return c


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data"); ap.add_argument("--every", type=int, default=3)
    ap.add_argument("--variants", default="base,aud_x0.3,all_0.05,all_x2")
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "arvedi_scatter"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    ac.TURN[:] = (-1.0, -1.0, 1.0)
    src, rec, H = ac.load(a.data)
    sub = {k: rec[k] for k in list(rec)[::a.every]}
    cfg = bp.load_config(CAL)
    cfg["receivers"] = {k: v.round(4).tolist() for k, v in sub.items()}
    print(f"S0, {len(sub)} receivers; bands {ac.BANDS}", flush=True)
    for name in a.variants.split(","):
        D = ac.compare(variant(cfg, name), src, sub, H, "S0", f"S0_{name}", a.out)
        edt = np.array(D["EDT"]); t30 = np.array(D["T30"]); c80 = np.array(D["C80"])
        rm = np.nanmean(edt[:, 0] / t30[:, 0], axis=0); rs = np.nanmean(edt[:, 1] / t30[:, 1], axis=0)
        f = lambda x: " ".join(f"{v:+6.0f}" for v in x)
        print(f"\n{name}")
        print("  EDT/T30 meas " + " ".join(f"{v:6.2f}" for v in rm))
        print("  EDT/T30 sim  " + " ".join(f"{v:6.2f}" for v in rs))
        print("  EDT bias %   " + f(100 * np.nanmean((edt[:, 1] - edt[:, 0]) / edt[:, 0], axis=0)))
        print("  T30 bias %   " + f(100 * np.nanmean((t30[:, 1] - t30[:, 0]) / t30[:, 0], axis=0)))
        print("  C80 bias dB  " + " ".join(f"{v:+6.2f}" for v in np.nanmean(c80[:, 1] - c80[:, 0], axis=0)), flush=True)


if __name__ == "__main__":
    main()
