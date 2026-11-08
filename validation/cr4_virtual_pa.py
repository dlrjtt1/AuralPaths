"""
A virtual sound-reinforcement set-up in a measured hall: BRAS CR4 (university auditorium) with a stage source and a
pair of side-wall PA loudspeakers, for stimuli with the pilot's 9 conditions (ITDG 0 / 20 / 40 ms x level ratio
-6 / 0 / +6 dB). Writes everything needed by calibrate.py, run.py and make_stimuli.py into one folder.

    python validation/cr4_virtual_pa.py <BRAS folder> --k8-mps <QSCK8_..._MPS_front_pole.csv>
                                        --dodeca <dodeca_HBK_4292L.csv> --dry <dry.wav> [--out out/cr4_pa]
then (printed at the end):
    python calibrate.py out/cr4_pa/config.json out/cr4_pa/t30_LS1.csv --out out/cr4_pa/config_cal.json
    python run.py out/cr4_pa/config_cal.json
    python make_stimuli.py out/cr4_pa/stimuli.json

What is taken from measurement and what is assumed (state this with any result):
- Hall: BRAS CR4 geometry and fitted materials (Aspoeck et al. 2020, https://doi.org/10.14279/depositonce-6726.3,
  CC BY-SA 4.0), then calibrated on the measured T30 of the BRAS RIRs from source LS1 at MP1 - MP5 (calibrate.py);
  the LS2 RIRs are left for checking (t30_LS2.csv).
- Path A (S_amp): a dodecahedron at the BRAS LS1 position (the RIR source), with the published horizontal pattern
  of the B&K 4292-L (dodeca_HBK_4292L.csv). BRAS measured with its own dodecahedron, whose pattern is not used.
- Path B (B_L, B_R): QSC K8 with its measured directivity (BRAS release, --k8-mps; pattern as a balloon). Positions
  are ASSUMED: the real CR4 has small PA loudspeakers on the side walls, shown only in a drawing of the BRAS model
  notes (CR4_ModelSimplifications.pdf, item 17) without coordinates. Here: on the side brick walls above the side
  balconies, 0.3 m from the wall, 6 m from the RIR source plane towards the audience, 4.5 m above the stage floor
  level, aimed at a point on the centre line (x = 10 m, 1.2 m high, BRAS frame). Not the real installation.
- Seats: MP1 - MP5 of the BRAS RIRs (MP1 is also the BRIR listener position MP6), ear height as measured, facing the
  stage. Reference seat for ITDG and level ratio: MP1.
- Head: KU100 HRIRs (the AuralPaths default), headphone filter HD600 as in config.json.
- Frame: AuralPaths (x right, y towards the stage), converted from the BRAS frame as in check_bras_brir.py.
Outputs are derivatives of BRAS data (CC BY-SA 4.0); keep them out of the repository.
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
import brir_proto as bp                     # noqa: E402
import check_bras_brir as cb                # noqa: E402
import validate_bras_cr as vb               # noqa: E402
from validate_fratoni import BANDS, criteria  # noqa: E402

PA_BRAS = {"B_L": (6.0, -13.34, 4.5), "B_R": (6.0, 13.34, 4.5)}   # BRAS frame: x towards the audience, -y = listener left (LS3 side)
PA_AIM_BRAS = (10.0, 0.0, 1.2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras"); ap.add_argument("--k8-mps", required=True); ap.add_argument("--dodeca", required=True)
    ap.add_argument("--dry", required=True); ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "cr4_pa"))
    ap.add_argument("--rays", type=int, default=5000)
    ap.add_argument("--hrir", default=os.path.join(HERE, "..", "hrir", "KU100.sofa"), help="KU100 SOFA (not in the repository)")
    a = ap.parse_args()
    out = os.path.abspath(a.out); os.makedirs(out, exist_ok=True)
    scene = glob.glob(os.path.join(a.bras, "CR4*"))[0]
    mats = vb.read_bras_materials(os.path.join(a.bras, "3 Surface descriptions"), "CR4", "fitted")
    obj_path = os.path.join(out, "CR4_rotated.obj")
    with open(obj_path, "w", encoding="utf-8") as f:
        f.write(cb.rotate_obj(open(os.path.join(scene, "Geometry", "CR4.obj"), encoding="utf-8", errors="ignore").read()))
    ir, fs_m, E, R, eid, rid, _ = vb.read_rirs(scene)
    S = {f"LS{e}": E[j] for j, e in enumerate(eid)}
    M = {f"MP{r}": R[i] for i, r in enumerate(rid)}
    rot = cb.rot
    fs = 48000
    import pyroomacoustics as pra
    cen = [float(x) for x in pra.ShoeBox([5, 5, 5], fs=fs, air_absorption=True).octave_bands.centers]
    k8 = cb.k8_balloon(a.k8_mps, cen)
    sources = {"S_amp": {"pos": rot(S["LS1"]), "directivity": os.path.abspath(a.dodeca), "aim": cb.aim_at(rot(S["LS1"]), rot(M["MP1"])),
                         "role": "stage source (dodecahedron at BRAS LS1)"}}
    for k, p in PA_BRAS.items():
        sources[k] = {"pos": rot(p), "directivity": k8, "aim": cb.aim_at(rot(p), rot(PA_AIM_BRAS)),
                      "role": "PA, QSC K8 measured directivity, ASSUMED side-wall position"}
    cfg = {"name": "BRAS CR4 with a virtual side-wall PA (stimuli for the pilot's 9 conditions)",
           "_note": "Hall: BRAS CR4 (CC BY-SA 4.0). PA positions are assumptions (see validation/cr4_virtual_pa.py).",
           "fs": fs, "c": 343.5,
           "room": {"dims_m": [10, 10, 5], "absorption_octave": {"values": [0.2] * 6}, "air_absorption": True},
           "sources": sources,
           "receivers": {f"MP{r}": rot(M[f"MP{r}"]) for r in sorted(rid)},
           "conditions": {"itdg_ms": [0, 20, 40], "level_ratio_db": [-6, 0, 6], "reference_receiver": "MP1"},
           "geometry": {"mesh": {"obj": obj_path, "axes": "y-up", "groups": {k: k for k in mats}, "voxel": 0.08},
                        "materials": {k: {"alpha": list(map(float, v["alpha"][:6])), "s": list(map(float, v["s_oct"][:6]))}
                                      for k, v in mats.items()},
                        "ism_order": 1, "rays": a.rays, "diffraction": False, "shared_rays": True},
           "binaural": {"sofa_path": os.path.abspath(a.hrir), "early_window_ms": 100.0, "crossfade_ms": 10.0,
                        "ism_order_early": 12, "ism_order_omni": 60,
                        "headphone_filter": os.path.join(HERE, "..", "hrir", "HPCF_Sennheiser-HD600.mat")},
           "output_dir": os.path.join(out, "run")}
    json.dump(cfg, open(os.path.join(out, "config.json"), "w"), indent=1)
    # measured T30 (and EDT) per band from the BRAS RIRs, in the AuralPaths frame
    for src in ("LS1", "LS2"):
        j = list(eid).index(int(src[2:]))
        with open(os.path.join(out, f"t30_{src}.csv"), "w", newline="") as f:
            w = csv.writer(f); w.writerow(["label", "src_x", "src_y", "src_z", "rec_x", "rec_y", "rec_z", "band_hz", "T30_s", "EDT_s"])
            for i, r in enumerate(rid):
                x = ir[i, j]; on = int(np.argmax(np.abs(x) > 0.1 * np.abs(x).max())) / fs_m
                c_ = criteria(vb.measured_hist(x, fs_m), on)
                for b, t30, edt in zip(BANDS, c_["T30"], c_["EDT"]):
                    w.writerow([f"{src}_MP{r}", *np.round(rot(S[src]), 3), *np.round(rot(M[f"MP{r}"]), 3), b, round(float(t30), 3), round(float(edt), 3)])
    stim = {"_note": "make_stimuli.py input for the CR4 virtual PA set-up (validation/cr4_virtual_pa.py).",
            "brir_dir": os.path.join(out, "run", "brir"), "brir_manifest": os.path.join(out, "run", "manifest.json"),
            "paths": {"A": "S_amp", "B_L": "B_L", "B_R": "B_R"}, "reference_seat": "MP1",
            "seats": [f"MP{r}" for r in sorted(rid)], "dry": {"src": os.path.abspath(a.dry)},
            "path_A_inputs": ["src"], "path_B_inputs": ["src"], "itdg_ms": [0, 20, 40], "level_ratio_db": [-6, 0, 6],
            "reference_stimulus": True, "onset_threshold_db": -20, "tail_s": 1.5, "fade_ms": 50, "headroom_dbfs": -1.0,
            "headphone_filter": os.path.join(HERE, "..", "hrir", "HPCF_Sennheiser-HD600.mat"), "subtype": "FLOAT",
            "output_dir": os.path.join(out, "stimuli")}
    json.dump(stim, open(os.path.join(out, "stimuli.json"), "w"), indent=1)
    for k, v in sources.items():
        print(f"{k}: {np.round(v['pos'], 2).tolist()} aim {v['aim']}")
    print("receivers:", {k: np.round(v, 2).tolist() for k, v in cfg["receivers"].items()})
    print(f"\npython calibrate.py {out}/config.json {out}/t30_LS1.csv --out {out}/config_cal.json\n"
          f"python run.py {out}/config_cal.json\npython make_stimuli.py {out}/stimuli.json")


if __name__ == "__main__":
    main()
