"""
Early scattered-energy directions, browser vs Python (2026-11-13).

Python: dirrays.window_direction_energy (rays after a diffuse reflection, stochastic scattering). Browser: GEOM.rays
tEarly (scattered share 1 - prod(1 - s) of each ray, blended directions in meshes). A 20 x 14 x 9 m box mesh with
an absorbing, scattering floor (audience-like), one source, three receivers. Compared per window (0 - 20, 20 - 50,
50 - 110 ms after the direct sound): the energy (dB, Python = 0) and the interaural coherence |Gamma| that
brir_proto.late_field gives for the KU100 HRIRs, mean over 500 Hz - 2 kHz (this is what the early residual noise is
rendered with).

    python validation/check_early_dirs_pyjs.py [--hrir hrir/KU100.sofa] [--rays 20000] [--drawn <config.json> [--src S2]]

--drawn: a drawn hall from a config (plan, floor, ceiling) instead of the box mesh; there both engines scatter
stochastically (the browser blends directions only in meshes), so the statistics should agree within ray noise.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
import brir_proto as bp                       # noqa: E402
import dirrays                                # noqa: E402

L = (20.0, 14.0, 9.0)
V = [(x, y, z) for x in (0, L[0]) for y in (0, L[1]) for z in (0, L[2])]
OBJ = ("".join(f"v {x} {y} {z}\n" for x, y, z in V) + "g floor\nf 1 5 7 3\ng wall\nf 5 6 8 7\nf 1 2 6 5\nf 3 7 8 4\nf 2 4 8 6\n"
       "g ceil\nf 1 3 4 2\n")
S = [10.0, 3.0, 1.5]
R = [[10.0, 9.0, 1.2], [5.0, 11.0, 1.2], [16.0, 7.0, 1.2]]
MATS = {"floor": ([0.6] * 8, 0.7), "wall": ([0.08] * 8, 0.2), "ceil": ([0.08] * 8, 0.2)}
JS = """const fs=require('fs');const GEOM=eval(fs.readFileSync('engine_geom.js','utf8')+';GEOM');const j=JSON.parse(fs.readFileSync(0,'utf8'));
const G=j.drawn?GEOM.build(j.drawn):GEOM.buildMesh({obj:GEOM.loadObj(j.obj),groups:j.groups,voxel:0.1,axes:'z-up'},j.src);
const T=GEOM.rays(G,j.src,j.recs,{n:j.n,c:j.c,tMax:0.4,bin:0.001,seed:5,tEarly:j.te},j.mats,j.air);
console.log(JSON.stringify(T.WE.map((a)=>Array.from(a))));"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hrir", default=os.path.join(ROOT, "hrir", "KU100.sofa")); ap.add_argument("--rays", type=int, default=20000)
    ap.add_argument("--drawn", default=None); ap.add_argument("--src", default="S2")
    a = ap.parse_args()
    global S, R, MATS
    drawn = None
    if a.drawn:
        dc = bp.load_config(a.drawn)
        g = dc["geometry"]
        drawn = {"plan": g["plan"], "floor": g["floor"], "ceil": g["ceiling"],
                 "stageY": dc["room"]["dims_m"][1] - dc["room"].get("stage_depth_m", 0)}
        S = list(map(float, dc["sources"][a.src]["pos"])); R = [list(map(float, v)) for v in list(dc["receivers"].values())[::6]]
        MATS = {k: (list(v["alpha"]) + [v["alpha"][-1]] * (8 - len(v["alpha"])), float(np.mean(v.get("s", 0.0)))) for k, v in g["materials"].items()}
    cfg = {"fs": 48000, "c": 343.0, "room": {"dims_m": list(L), "absorption_octave": {"values": [0.1] * 6}, "air_absorption": True},
           "sources": {"S": {"pos": S}}, "receivers": {f"R{i}": r for i, r in enumerate(R)},
           "binaural": {"early_window_ms": 100.0, "crossfade_ms": 10.0},
           "geometry": {"mesh": {"obj": "box.obj", "obj_text": OBJ, "axes": "z-up", "groups": {k: k for k in MATS}},
                        "materials": {k: {"alpha": al, "s": [s] * 8} for k, (al, s) in MATS.items()}, "ism_order": 1}}
    if drawn:
        cfg = dc
        cfg["receivers"] = {f"R{i}": r for i, r in enumerate(R)}
    centers = bp.make_room(cfg, 0).octave_bands.centers
    air = np.asarray(bp.make_room(cfg, 0).air_absorption, float)
    G = bp._geom(cfg)
    alpha = np.array([MATS[q["mat"]][0] for q in G["S"]]); scat = np.array([MATS[q["mat"]][1] for q in G["S"]])
    te = np.array([[0.0] + [np.linalg.norm(np.subtract(r, S)) / 343.0 + e for e in (0.02, 0.05, 0.11)] for r in R])
    Wp = dirrays.window_direction_energy(G, np.array(S), np.array(R), te, alpha, scat, air, 343.0, a.rays)
    mats = {k: {"R": [float(np.sqrt(1 - x)) for x in al], "s": s} for k, (al, s) in MATS.items()}
    job = dict(drawn=drawn, obj=OBJ, groups={k: k for k in MATS}, src=S, recs=R, mats=mats, air=air.tolist(), c=343.0, n=a.rays, te=te.tolist())
    r = subprocess.run(["node", "-e", JS], input=json.dumps(job), capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        sys.exit(r.stderr[-1500:])
    nb = len(centers)
    Wj = np.array(json.loads(r.stdout)).reshape(len(R), 3, dirrays.NBIN, nb)
    hrir = bp.load_hrir(a.hrir, 48000)
    f = bp.late_dir_tables(hrir)["f"]
    sel = (f >= 355) & (f <= 2828)
    print("receiver window: energy browser - Python (dB, 500 Hz - 2 kHz) | |Gamma| Python / browser (500 Hz - 2 kHz)")
    worst = 0.0
    for i in range(len(R)):
        for k, lab in enumerate(("0-20", "20-50", "50-110")):
            bi = [1, 2, 3, 4]
            ep, ej = Wp[i, k][:, bi].sum(), Wj[i, k][:, bi].sum()
            if ep <= 0 or ej <= 0:
                print(f"  R{i} {lab:6s} no scattered energy (Python {ep:.2e}, browser {ej:.2e})"); continue
            gp = np.abs(bp.late_field(hrir, Wp[i, k], centers, 48000)[1])[sel].mean()
            gj = np.abs(bp.late_field(hrir, Wj[i, k], centers, 48000)[1])[sel].mean()
            worst = max(worst, abs(gp - gj))
            print(f"  R{i} {lab:6s} {10 * np.log10(ej / ep):+5.1f} dB | {gp:.2f} / {gj:.2f}")
    print(f"largest |Gamma| difference {worst:.2f}")


if __name__ == "__main__":
    main()
