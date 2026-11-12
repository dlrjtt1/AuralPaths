"""Arvedi (post hoc): does the simulation get the CHANGE of the room criteria between sources right?

For every receiver and octave band, delta = metric(S_k) - metric(S0) (k = 1 ... 4; EDT, T20 as ratio in %), measured and
simulated, from the compare_<label>.csv files of arvedi_check.py. Reported per band: mean measured delta, mean simulated
delta, mean and rms of (simulated - measured delta), share of receivers within one JND (EDT 5 %, C80 1 dB, D50 0.05,
Ts 10 ms) and the correlation over receivers. The change here is a change of source (dodecahedron at the stage centre
-> aimed loudspeaker at another stage position), not of a reinforcement delay or level.

    python validation/arvedi_delta.py out/arvedi_posthoc [out/arvedi_detail ...]
"""
import csv
import os
import sys

import numpy as np

JND = {"EDT": ("rel", 5.0), "C80": ("abs", 1.0), "D50": ("abs", 0.05), "Ts": ("abs", 10.0), "T20": ("rel", 5.0)}


def read(path):
    d = {}
    for r in csv.DictReader(open(path)):
        try:
            d[(r["receiver"], r["metric"], int(r["band_hz"]))] = (float(r["measured"]), float(r["simulated"]))
        except ValueError:
            pass
    return d


def main():
    for out in sys.argv[1:]:
        s0 = read(os.path.join(out, "compare_S0_primary.csv"))
        print(f"\n== {out}")
        for k in ("S1", "S2", "S3", "S4"):
            p = os.path.join(out, f"compare_{k}_directional.csv")
            if not os.path.exists(p):
                continue
            sk = read(p)
            print(f"{k} - S0: band: meas / sim delta, error mean / rms, within 1 JND, r")
            for m, (kind, j) in JND.items():
                cells = []
                for b in (125, 250, 500, 1000, 2000, 4000):
                    dm, ds = [], []
                    for key, (a1, x1) in sk.items():
                        if key[1] != m or key[2] != b or (key[0], m, b) not in s0:
                            continue
                        a0, x0 = s0[(key[0], m, b)]
                        if not all(np.isfinite([a0, a1, x0, x1])) or (kind == "rel" and (a0 <= 0 or x0 <= 0)):
                            continue
                        if kind == "rel":
                            dm.append(100 * (a1 / a0 - 1)); ds.append(100 * (x1 / x0 - 1))
                        else:
                            dm.append(a1 - a0); ds.append(x1 - x0)
                    dm, ds = np.array(dm), np.array(ds)
                    e = ds - dm
                    r = np.corrcoef(dm, ds)[0, 1] if len(dm) > 2 and dm.std() > 0 and ds.std() > 0 else np.nan
                    u = "%" if kind == "rel" else ""
                    cells.append(f"{b}: {dm.mean():+.2f}{u}/{ds.mean():+.2f}{u} {e.mean():+.2f}/{np.sqrt((e ** 2).mean()):.2f} "
                                 f"{100 * np.mean(np.abs(e) <= j):.0f}% r{r:+.2f}")
                print(f"  {m:4s} " + "  ".join(cells))


if __name__ == "__main__":
    main()
