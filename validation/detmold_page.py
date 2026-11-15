"""
Detmold binaural comparison with the BRIRs of the PAGE (2026-11-15).

validation/detmold_kh.py renders its BRIRs with the Python engine. Here the same 136 pairs (S2, S3, S6, S7 x 34
seats) are computed by the page itself (headless Chromium, tests/page_brirs.js): the drawn Detmold hall with the
materials calibrated for the page's engine (calibrate.py --engine js), the loudspeakers as the page's PA sources
(generic 90 degree pattern, aimed as in the config), the embedded KU100 HRIRs, 50000 rays, image sources to order
3, every page default (directional late field, early scattered-energy windows). The page takes three seats and two
PA sources per run, so the pairs are computed in 24 runs; S_amp is a dummy at the position of the run's first PA.
The BRIRs are written as {source}{seat}.wav into <out>/brir and compared with
    python validation/detmold_kh.py compare <DetmoldSRIR folder or /nonexistent> <out> --meas-csv <earlier compare.csv>

    python validation/detmold_page.py <calibrated config.json> [--out out/detmold_page] [--sources S2,S3,S6,S7]
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config"); ap.add_argument("--out", default=os.path.join(ROOT, "out", "detmold_page"))
    ap.add_argument("--sources", default="S2,S3,S6,S7")
    a = ap.parse_args()
    cfg = json.load(open(a.config))
    os.makedirs(os.path.join(a.out, "brir"), exist_ok=True)
    srcs = a.sources.split(",")
    seats = list(cfg["receivers"])
    for i in range(0, len(srcs), 2):
        pair = srcs[i:i + 2] if len(srcs[i:i + 2]) == 2 else [srcs[i], srcs[i]]
        for j in range(0, len(seats), 3):
            grp = seats[j:j + 3]
            if all(os.path.exists(os.path.join(a.out, "brir", f"{s}{r}.wav")) for s in set(pair) for r in grp):
                continue
            ids = dict(zip(("L", "C", "R"), grp + [grp[0]] * (3 - len(grp))))
            pa = lambda s: {"pos": cfg["sources"][s]["pos"], "coverage": cfg["sources"][s]["coverage"], "aim": cfg["sources"][s]["aim"]}
            c = {"name": f"Detmold, page run {pair} x {grp}", "fs": 48000, "c": 343.0, "room": cfg["room"],
                 "sources": {"S_amp": {"pos": cfg["sources"][pair[0]]["pos"]}, "B_L": pa(pair[0]), "B_R": pa(pair[1])},
                 "receivers": {"_facing": "+y", **{k: cfg["receivers"][r] for k, r in ids.items()}},
                 "geometry": {**{k: cfg["geometry"][k] for k in ("plan", "floor", "ceiling", "materials")}, "ism_order": 3,
                              "rays": 50000, "diffraction": False}}
            pc, pj = os.path.join(a.out, "page_config.json"), os.path.join(a.out, "page_brirs.json")
            json.dump(c, open(pc, "w"))
            r = subprocess.run(["node", os.path.join(ROOT, "tests", "page_brirs.js"), ROOT, pc, pj], capture_output=True, text=True, cwd=ROOT)
            if r.returncode:
                sys.exit(r.stderr[-1500:] or r.stdout[-500:])
            info = json.loads(r.stdout.strip().splitlines()[-1])
            if info["errors"] or not info["drawn"] or not all(info["dirs"][k] and info["dirs"][k].get("cov") == 90 for k in ("B_L", "B_R")):
                sys.exit(f"page did not take the config as intended: {info}")
            B = json.load(open(pj))
            for k, s in (("B_L", pair[0]), ("B_R", pair[1])):
                for sid, rname in ids.items():
                    x = np.array(B["brirs"][f"{sid}|{k}"], np.float32)
                    sf.write(os.path.join(a.out, "brir", f"{s}{rname}.wav"), x.T, B["fs"], subtype="FLOAT")
            print(f"{pair} x {grp}: done ({info['rays']} rays, order {info['order']})", flush=True)
    os.remove(os.path.join(a.out, "page_brirs.json")) if os.path.exists(os.path.join(a.out, "page_brirs.json")) else None


if __name__ == "__main__":
    main()
