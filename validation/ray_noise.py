"""
Ray noise of the room criteria against the number of rays (diagnostic).

One hall configuration of validation/scatter_delta.py (its source A alone, its receivers), traced with several ray
counts and two ray seeds each. Per octave band: RMS over the receivers and hall mean of the seed-to-seed difference
of EDT, C80 and T30, and the hall means themselves (a drift of the means with the ray count would show a bias).
Histograms are cached in <out>/hist_r<rays>_s<seed>_<source>.npz.

    python validation/ray_noise.py <hall> <config_cal.json> --out out/noise_rays [--rays 20000,80000,320000]
        [--only <rays>:<seed>]
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, ".."), HERE]
import brir_proto as bp                       # noqa: E402
import scatter_delta as sd                    # noqa: E402


def criteria(cfg, rays, seed, out):
    recs = list(cfg["receivers"])
    h, cen = sd.piece(cfg, rays, seed, f"r{rays}_s{seed}", bp.AMP, out)
    res = {}
    for b in sd.BANDS:
        m = [bp.iso3382_energy([(h[r], 0.0, 1.0)], bp.direct_time(cfg, bp.AMP, r), bands=(b,), centers=cen)
             for r in recs]
        res[b] = {k: np.array([x[k] for x in m]) for k in ("EDT", "C80", "T30")}
    return res


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("hall", choices=sorted(sd.HALLS)); ap.add_argument("config"); ap.add_argument("--out", required=True)
    ap.add_argument("--rays", default="20000,80000,320000"); ap.add_argument("--only", default=None)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    cfg = sd.setup(a.config, a.hall)
    if a.only:
        rays, seed = (int(x) for x in a.only.split(":"))
        sd.piece(cfg, rays, seed, f"r{rays}_s{seed}", bp.AMP, a.out)
        return
    rms = lambda x: float(np.sqrt(np.nanmean(x ** 2)))
    print(f"{a.hall}, A alone, {len(cfg['receivers'])} receivers; seed 2 against seed 1: RMS over receivers / "
          f"difference of the hall means; hall means of seed 1, seed 2")
    for b in sd.BANDS:
        for rays in (int(x) for x in a.rays.split(",")):
            p, q = criteria(cfg, rays, 1, a.out)[b], criteria(cfg, rays, 2, a.out)[b]
            de, dc, dt = 100 * (q["EDT"] / p["EDT"] - 1), q["C80"] - p["C80"], 100 * (q["T30"] / p["T30"] - 1)
            mean = lambda k: f"{np.nanmean(p[k]):.3f} {np.nanmean(q[k]):.3f}"
            print(f"  {b:4d} Hz {rays:7d} rays | EDT {rms(de):5.2f} % / {np.nanmean(de):+5.2f} % | C80 {rms(dc):4.2f} / "
                  f"{np.nanmean(dc):+5.2f} dB | T30 {rms(dt):5.2f} % / {np.nanmean(dt):+5.2f} % | EDT {mean('EDT')} s, "
                  f"C80 {mean('C80')} dB, T30 {mean('T30')} s", flush=True)


if __name__ == "__main__":
    main()
