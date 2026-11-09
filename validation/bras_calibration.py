"""
Calibration input for a BRAS hall (CR3 or CR4): the hall as an AuralPaths config (geometry and fitted materials,
rotated into the AuralPaths frame) and the measured T30 / EDT of the BRAS RIRs from source LS1 at MP1 - MP5.

    python validation/bras_calibration.py <BRAS folder> CR3 [--out out/bras_cal_CR3] [--rays 5000]
then (printed at the end):
    python calibrate.py out/bras_cal_CR3/config.json out/bras_cal_CR3/t30_LS1.csv --out out/bras_cal_CR3/config_cal.json
and use the calibrated materials, e.g. for the binaural check:
    python validation/check_bras_brir.py <BRAS folder> CR3 --materials out/bras_cal_CR3/config_cal.json ...

The calibration uses the RIRs (dodecahedron source LS1, omnidirectional microphones), not the BRIRs, so the binaural
comparison afterwards is not fitted to itself; only the hall's average T30 per band is shared. The LS2 RIRs are
written too (t30_LS2.csv) for checking. Outputs are derivatives of BRAS data (Aspoeck et al. 2020,
https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0); keep them out of the repository.
"""
import argparse
import csv
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, ".."), HERE]
import check_bras_brir as cb                # noqa: E402
import validate_bras_cr as vb               # noqa: E402
from validate_fratoni import BANDS, criteria  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras"); ap.add_argument("hall", choices=["CR3", "CR4"])
    ap.add_argument("--out", default=None); ap.add_argument("--rays", type=int, default=5000)
    a = ap.parse_args()
    out = os.path.abspath(a.out or os.path.join(HERE, "..", "out", f"bras_cal_{a.hall}")); os.makedirs(out, exist_ok=True)
    scene = glob.glob(os.path.join(a.bras, f"{a.hall}*"))[0]
    mats = vb.read_bras_materials(os.path.join(a.bras, "3 Surface descriptions"), a.hall, "fitted")
    obj_path = os.path.join(out, f"{a.hall}_rotated.obj")
    with open(obj_path, "w", encoding="utf-8") as f:
        f.write(cb.rotate_obj(open(os.path.join(scene, "Geometry", f"{a.hall}.obj"), encoding="utf-8", errors="ignore").read()))
    ir, fs_m, E, R, eid, rid, _ = vb.read_rirs(scene)
    S = {f"LS{e}": E[j] for j, e in enumerate(eid)}
    M = {f"MP{r}": R[i] for i, r in enumerate(rid)}
    rot = cb.rot
    cfg = {"name": f"BRAS {a.hall} (calibration input)", "_note": "BRAS (CC BY-SA 4.0); validation/bras_calibration.py",
           "fs": 48000, "c": 343.5,
           "room": {"dims_m": [10, 10, 5], "absorption_octave": {"values": [0.2] * 6}, "air_absorption": True},
           "sources": {"LS1": {"pos": rot(S["LS1"])}},
           "receivers": {k: rot(v) for k, v in sorted(M.items())},
           "geometry": {"mesh": {"obj": obj_path, "axes": "y-up", "groups": {k: k for k in mats}, "voxel": 0.08},
                        "materials": {k: {"alpha": list(map(float, v["alpha"][:6])), "s": list(map(float, v["s_oct"][:6]))}
                                      for k, v in mats.items()},
                        "ism_order": 1, "rays": a.rays, "diffraction": False}}
    json.dump(cfg, open(os.path.join(out, "config.json"), "w"), indent=1)
    for src in ("LS1", "LS2"):
        j = list(eid).index(int(src[2:]))
        with open(os.path.join(out, f"t30_{src}.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["label", "src_x", "src_y", "src_z", "rec_x", "rec_y", "rec_z", "band_hz", "T30_s", "EDT_s"])
            for i, r in enumerate(rid):
                x = ir[i, j]; on = int(np.argmax(np.abs(x) > 0.1 * np.abs(x).max())) / fs_m
                c_ = criteria(vb.measured_hist(x, fs_m), on)
                for b, t30, edt in zip(BANDS, c_["T30"], c_["EDT"]):
                    w.writerow([f"{src}_MP{r}", *np.round(rot(S[src]), 3), *np.round(rot(M[f"MP{r}"]), 3), b,
                                round(float(t30), 3), round(float(edt), 3)])
    print(f"python calibrate.py {out}/config.json {out}/t30_LS1.csv --out {out}/config_cal.json")


if __name__ == "__main__":
    main()
