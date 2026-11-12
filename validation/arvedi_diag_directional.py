"""Arvedi diagnostic (post hoc, after the results): where does the early-energy error of the directional sources come from?

For a subset of receivers and each source, the octave-band energy histograms (measured: the 8-capsule mean, as in
arvedi_check.py; simulated: brir_proto.energy_hists with the calibrated detailed config) are split into
    direct   t0 - 1 ms ... t0 + 3 ms
    early    t0 + 3 ms ... t0 + 80 ms
    late     after t0 + 80 ms
and each part is given as a share of the total energy (dB). A second table gives, per receiver, the direct energy of
S1 relative to S0 (dB), measured and simulated: the loudspeakers' absolute levels are unknown, so only the spread over
the receivers is meaningful; it follows the S1 polar pattern if the directivity is read and aimed correctly.

usage: python validation/arvedi_diag_directional.py <arvedi data folder> <calibrated config.json> [--every 5]
       [--sources S0,S1] [--out out/arvedi_detail/diag_directional.csv]
"""
import argparse
import csv
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, ".."), HERE]
import arvedi_check as ac                     # noqa: E402
import brir_proto as bp                       # noqa: E402
from validate_fratoni import BANDS            # noqa: E402

WIN = {"direct": (-0.001, 0.003), "early": (0.003, 0.080), "late": (0.080, 10.0)}


def parts(h, t0, search=0.0):
    """Energy shares (dB re total) of the windows in WIN, per band, from histograms h [6, n] with HIST_BIN bins.
    search > 0: t0 is moved to the broadband peak within t0 +- search (measured data: latency of the chain)."""
    if search > 0:
        i = np.arange(h.shape[1]); tc = (i + 0.5) * bp.HIST_BIN
        sel = np.abs(tc - t0) <= search
        t0 = tc[sel][np.argmax(h.sum(axis=0)[sel])]
    t = (np.arange(h.shape[1]) + 0.5) * bp.HIST_BIN - t0
    tot = h.sum(axis=1)
    return {k: 10 * np.log10(np.maximum(h[:, (t >= a) & (t < b)].sum(axis=1), 1e-30) / tot) for k, (a, b) in WIN.items()}, \
        h[:, (t >= WIN["direct"][0]) & (t < WIN["direct"][1])].sum(axis=1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data"); ap.add_argument("config")
    ap.add_argument("--every", type=int, default=5)
    ap.add_argument("--sources", default="S0,S1")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "arvedi_detail", "diag_directional.csv"))
    a = ap.parse_args()
    ac.TURN[:] = (-1.0, -1.0, 1.0)                 # post hoc placement (protocol item 13)
    src, rec, H = ac.load(a.data)
    cfg = bp.load_config(a.config)
    sub = list(rec)[::a.every]
    rows, direct = [], {}
    for s in a.sources.split(","):
        Hs, cen = bp.energy_hists(cfg, s, sub, t_max=2.0, n_rays=ac.RAYS)
        bi = [int(np.argmin(np.abs(np.asarray(cen) - b))) for b in BANDS]
        acc = {k: {"m": [], "s": []} for k in WIN}
        for r in sub:
            t0 = np.linalg.norm(src[s] - rec[r]) / ac.C
            pm, dm = parts(np.asarray(H[f"{s}-{r}"], float), t0, search=0.005)
            ps, ds = parts(np.asarray(Hs[r][bi], float), t0)
            direct[(s, r)] = (dm, ds)
            for k in WIN:
                acc[k]["m"].append(pm[k]); acc[k]["s"].append(ps[k])
                rows += [[s, r, k, b, round(float(x), 2), round(float(y), 2)] for b, x, y in zip(BANDS, pm[k], ps[k])]
        print(f"\n{s}: energy share of each window, dB re total (measured / simulated / sim - meas), mean of {len(sub)} receivers")
        for k in WIN:
            m, x = np.mean(acc[k]["m"], axis=0), np.mean(acc[k]["s"], axis=0)
            print(f"  {k:6s} " + "  ".join(f"{b}: {mi:6.1f}/{xi:6.1f} {xi - mi:+5.1f}" for b, mi, xi in zip(BANDS, m, x)))
    srcs = a.sources.split(",")
    if "S0" in srcs and len(srcs) > 1:
        for s in srcs[1:]:
            print(f"\ndirect energy {s} - S0 (dB) per receiver, offset removed (mean over receivers = 0): measured / simulated")
            dm = np.array([10 * np.log10(direct[(s, r)][0] / direct[("S0", r)][0]) for r in sub])
            ds = np.array([10 * np.log10(direct[(s, r)][1] / direct[("S0", r)][1]) for r in sub])
            dm -= dm.mean(axis=0); ds -= ds.mean(axis=0)
            for r, x, y in zip(sub, dm, ds):
                el = np.degrees(np.arctan2(rec[r][2] - src[s][2], np.linalg.norm((rec[r] - src[s])[:2])))
                print(f"  {r:6s} el {el:5.1f}  " + "  ".join(f"{b}: {xi:+5.1f}/{yi:+5.1f}" for b, xi, yi in zip(BANDS, x, y)))
            print("  rms difference per band: " + "  ".join(f"{b}: {np.sqrt(np.mean((dm[:, i] - ds[:, i]) ** 2)):.1f}"
                                                       for i, b in enumerate(BANDS)))
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["source", "receiver", "window", "band_hz", "measured_db", "simulated_db"]); w.writerows(rows)
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
