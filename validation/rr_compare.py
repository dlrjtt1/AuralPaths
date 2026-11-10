"""
Spectral-shape error of the round-robin simulators and of AuralPaths on the pairs shown in SuppPub2 (Brinkmann et
al. 2019, https://doi.org/10.1121/1.5096178). Inputs: the levels read from the figures (validation/rr_extract.py)
and the band levels of validation/bras_rs.py.

    python validation/rr_compare.py [out/rs]

Shape error: rms over the 1/3-octave bands shown in the figure (100 Hz - 5 kHz at most) of simulated minus measured
level, after removing the mean difference (the figures are normalised by the rms of the IR, so absolute level is not
comparable). Round-robin simulators are scored against the measured curve of the figure, AuralPaths against the
measured RIR processed here; the agreement of the two measured curves is reported as a check of the reading and of
the windowing.
"""
import csv
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))


def shape(a, b):
    d = np.asarray(a) - np.asarray(b)
    d = d - d.mean()
    return float(np.sqrt(np.mean(d ** 2)))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "out", "rs")
    rr = list(csv.DictReader(open(os.path.join(out, "rr_curves.csv"))))
    figs = sorted(set(int(r["figure"]) for r in rr))
    variants = ["before", "engine", "ga_utd"]
    lines = ["| figure | scene | pair | reading check | " + " | ".join(f"RR {x}" for x in "ACDEF") + " | " +
             " | ".join(f"AuralPaths {v}" for v in variants) + " |", "|" + "---|" * (4 + 5 + len(variants))]
    allrr, allap = {x: [] for x in "ACDEF"}, {v: [] for v in variants}
    for fg in figs:
        R = [r for r in rr if int(r["figure"]) == fg]
        sc, cfg, ls, mp = R[0]["scene"], R[0]["config"], R[0]["source"], R[0]["receiver"]
        meas = {int(r["f_hz"]): float(r["level_db"]) for r in R if r["curve"] == "measured"}
        F = [f for f in sorted(meas) if 100 <= f <= 5000]
        cells = []
        ours = {}
        for v in variants:
            p = os.path.join(out, f"{sc}{'_' + cfg if cfg else ''}_{v}.csv")
            if not os.path.exists(p):
                ours[v] = None
                continue
            rows = [r for r in csv.DictReader(open(p)) if r["source"] == ls and r["receiver"] == mp]
            ours[v] = ({int(r["f_hz"]): float(r["measured_db"]) for r in rows},
                       {int(r["f_hz"]): float(r["simulated_db"]) for r in rows})
        base = next((o for o in ours.values() if o), None)
        F = [f for f in F if base is None or f in base[0]]
        chk = f"{shape([base[0][f] for f in F], [meas[f] for f in F]):.1f}" if base else "-"
        for x in "ACDEF":
            c = {int(r["f_hz"]): float(r["level_db"]) for r in R if r["curve"] == x}
            if all(f in c for f in F) and c:
                e = shape([c[f] for f in F], [meas[f] for f in F])
                allrr[x].append(e)
                cells.append(f"{e:.1f}")
            else:
                cells.append("-")
        for v in variants:
            if ours[v]:
                e = shape([ours[v][1][f] for f in F], [ours[v][0][f] for f in F])
                allap[v].append(e)
                cells.append(f"{e:.1f}")
            else:
                cells.append("-")
        lines.append(f"| S2-{fg} | {sc} {cfg} | {ls}-{mp} | {chk} | " + " | ".join(cells) + " |")
    lines.append("| median | | | | " + " | ".join(f"{np.median(allrr[x]):.1f} ({len(allrr[x])})" if allrr[x] else "-"
                                            for x in "ACDEF") + " | " +
                 " | ".join(f"{np.median(allap[v]):.1f} ({len(allap[v])})" if allap[v] else "-" for v in variants) + " |")
    txt = "\n".join(lines)
    print(txt)
    open(os.path.join(out, "rr_compare.md"), "w").write(txt + "\n")


if __name__ == "__main__":
    main()
