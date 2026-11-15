"""
BRAS CR3 / CR4: where in time do the measured and the simulated decay differ? (diagnostic, 2026-11-15)

As validation/arvedi_decay_shape.py, in two halls whose 3-D model comes with the measurement (BRAS geometry and
fitted materials, validation/bras_calibration.py): if the first 80 ms agree here, the Arvedi deficit at 20 - 80 ms
is a matter of that model, not of the engine. The page's engine (engine_js.py), omnidirectional source
(dodecahedron), 2 loudspeaker x 5 microphone positions. Absorption calibrated on the measured T30 of the LS1
positions (calibrate.py, median, as everywhere); LS2 is not used for the calibration.

    python validation/bras_decay_shape.py <out/bras_cal16_CRn> <BRAS scene folder> [--rays 20000] [--out out/bras_shape_CRn]

<out/bras_cal16_CRn>: config.json, t30_LS1.csv, t30_LS2.csv of bras_calibration.py. Outputs are BRAS derivatives
(CC BY-SA 4.0): keep them in out/.
"""
import argparse
import copy
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path[:0] = [ROOT, HERE]
import brir_proto as bp                       # noqa: E402
import engine_js                              # noqa: E402
import validate_bras_cr as vb                 # noqa: E402
from arvedi_decay_shape import BANDS, show    # noqa: E402
from detmold_decay_shape import unit          # noqa: E402
from detmold_js import positions              # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cal"); ap.add_argument("scene"); ap.add_argument("--rays", type=int, default=20000); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(ROOT, "out", "bras_shape_" + os.path.basename(os.path.normpath(a.cal))[-3:])
    os.makedirs(out, exist_ok=True)
    cfg = json.load(open(os.path.join(a.cal, "config.json")))
    cfg["geometry"]["rays"] = a.rays
    json.dump(cfg, open(os.path.join(out, "config.json"), "w"), indent=1)
    cal = os.path.join(out, "config_cal.json")
    if not os.path.exists(cal):
        subprocess.run([sys.executable, os.path.join(ROOT, "calibrate.py"), os.path.join(out, "config.json"),
                        os.path.join(a.cal, "t30_LS1.csv"), "--out", cal, "--iter", "6"], check=True, cwd=ROOT)
    cfg = copy.deepcopy(bp.load_config(cal))
    pos = {**positions(os.path.join(a.cal, "t30_LS1.csv")), **positions(os.path.join(a.cal, "t30_LS2.csv"))}
    cfg["sources"] = {**cfg["sources"], **{s: {"pos": next(p["src"] for lab, p in pos.items() if lab.startswith(s + "_"))} for s in ("LS1", "LS2")}}
    cfg["receivers"] = {lab.split("_")[1]: p["rec"] for lab, p in pos.items()}
    mps = sorted(cfg["receivers"])
    H, cen = engine_js.hists(cfg, {"LS1": mps, "LS2": mps}, n_rays=a.rays, seed=1)
    bi = [int(np.argmin(np.abs(np.asarray(cen) - b))) for b in BANDS]
    ir, fs, E, R, eid, rid, _ = vb.read_rirs(a.scene)
    M, S = {"LS1": [], "LS2": []}, {"LS1": [], "LS2": []}
    for s in ("LS1", "LS2"):
        j = list(eid).index(int(s[2:]))
        for i, r in enumerate(rid):
            x = ir[i, j]
            on = int(np.argmax(np.abs(x) > 0.1 * np.abs(x).max())) / fs
            M[s].append(unit(vb.measured_hist(x, fs), int(np.floor(on / bp.HIST_BIN))))
            p = pos[f"{s}_MP{r}"]
            t0 = np.linalg.norm(np.subtract(p["src"], p["rec"])) / cfg["c"]
            S[s].append(unit(H[(s, f"MP{r}")][bi], int(np.floor(t0 / bp.HIST_BIN))))
    show(np.mean(M["LS1"] + M["LS2"], 0), np.mean(S["LS1"] + S["LS2"], 0), "all 10 pairs (LS1: calibration positions; LS2: not used)")
    print()
    show(np.mean(M["LS2"], 0), np.mean(S["LS2"], 0), "LS2 only, 5 pairs (not used for the calibration)")


if __name__ == "__main__":
    main()
