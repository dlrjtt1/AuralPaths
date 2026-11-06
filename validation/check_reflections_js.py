"""
Early reflections of the browser engine on a BRAS OBJ hall against the measured RIRs, image sources to order 1 or 2.

    python validation/check_reflections_js.py <BRAS folder> CR3 [--order 2] [--voxel 0.05]   (needs node)

Same test as validate_bras_cr.py (window energy): every predicted reflection that is at least -15 dB re direct, at least
2 ms after the direct sound and 1.5 ms away from any other predicted one (of any order) is compared with the measured
energy in a 1 ms window at its predicted time (-0.2 ... +0.8 ms), in dB re the same window on the direct sound,
500 Hz - 2 kHz. Controls: the same window 2 ms later, and random times 3 - 20 ms. Results are split by reflection order.
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import validate_bras_cr as vb  # noqa: E402

SCENES = {"CR3": "CR3 medium room (chamber music hall)", "CR4": "CR4 large room (auditorium)"}
JS = """const fs=require('fs');const GEOM=eval(fs.readFileSync('engine_geom.js','utf8')+';GEOM');const j=JSON.parse(fs.readFileSync(0,'utf8'));
const G=GEOM.buildMesh({obj:GEOM.loadObj(j.obj),groups:j.groups,voxel:j.voxel},Object.values(j.srcs)[0]);const out={};
for(const [name,s] of Object.entries(j.srcs)){const I=GEOM.ism(G,s,j.recs,j.order,0.05,j.c,j.mats,j.air,j.bands);
out[name]=I.map(L=>L.map(q=>[q.t,q.o,(q.g[2]**2+q.g[3]**2+q.g[4]**2)/3]));}
console.log(JSON.stringify(out));"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras"); ap.add_argument("hall", choices=list(SCENES))
    ap.add_argument("--order", type=int, default=2); ap.add_argument("--voxel", type=float, default=None)
    a = ap.parse_args()
    voxel = a.voxel or (0.05 if a.hall == "CR3" else 0.08)
    scene = os.path.join(a.bras, SCENES[a.hall])
    mats = vb.read_bras_materials(os.path.join(a.bras, "3 Surface descriptions"), a.hall, "fitted")
    ir, fs, E, R, eid, rid, _ = vb.read_rirs(scene)
    cen = [125, 250, 500, 1000, 2000, 4000, 8000, 16000]
    mj = {k: {"R": [float(np.sqrt(1 - v["alpha"][min(i, len(v["alpha"]) - 1)])) for i in range(len(cen))], "s": v["s_oct"]} for k, v in mats.items()}
    srcs = {f"LS{e}": list(map(float, E[i])) for i, e in enumerate(eid)}; recs = [list(map(float, R[i])) for i in range(len(rid))]
    job = dict(obj=open(os.path.join(scene, "Geometry", a.hall + ".obj")).read(), groups={k: k for k in mats}, voxel=voxel, srcs=srcs,
               recs=recs, order=a.order, c=343.5, mats=mj, bands=cen, air=[0.0] * len(cen))
    r = subprocess.run(["node", "--max-old-space-size=6000", "-e", JS], input=json.dumps(job), capture_output=True, text=True, cwd=os.path.join(HERE, ".."))
    if r.returncode:
        sys.exit(r.stderr[-3000:])
    o = json.loads(r.stdout)
    rows = {1: [], 2: []}; rnd = []; rng = np.random.default_rng(0)
    for si, sn in enumerate(srcs):
        for k in range(len(recs)):
            L = o[sn][k]; direct = [q for q in L if q[1] == 0]
            if not direct:
                continue
            t0, e0 = direct[0][0], direct[0][2]
            pred = [(q[0] - t0, 10 * np.log10(q[2] / e0 + 1e-30), q[1]) for q in L if q[1] > 0]
            y, on = vb.band_energy(ir[k, si] if ir.ndim == 3 else ir[si * len(recs) + k], fs)
            for t, l, od in pred:
                if t < 0.002 or l < -15 or any(abs(t - t2) <= 0.0015 for t2, _, _ in pred if t2 != t):
                    continue
                rows[od].append((t, l, vb.window_level(y, on, fs, t), vb.window_level(y, on, fs, t + 0.002)))
            rnd += [vb.window_level(y, on, fs, t) for t in rng.uniform(0.003, 0.02, 20)]
    print(f"{a.hall}: image sources to order {a.order}, isolated predicted reflections vs measured window energy (dB re direct, 500 Hz-2 kHz)")
    print(f"  random times 3-20 ms: median {np.median(rnd):.1f} dB")
    for od in (1, 2):
        X = np.asarray(rows[od])
        if not len(X):
            print(f"  order {od}: none"); continue
        d = X[:, 1] - X[:, 2]
        print(f"  order {od}: n {len(X)}, predicted median {np.median(X[:, 1]):.1f}, measured at predicted time {np.median(X[:, 2]):.1f}, "
              f"+2 ms {np.median(X[:, 3]):.1f}; predicted - measured median {np.median(d):+.1f} (IQR {np.percentile(d, 25):+.1f} ... {np.percentile(d, 75):+.1f}); "
              f"measured above the random median in {100 * np.mean(X[:, 2] > np.median(rnd)):.0f} %, above its +2 ms control in {100 * np.mean(X[:, 2] > X[:, 3]):.0f} %; "
              f"r(pred, meas) {np.corrcoef(X[:, 1], X[:, 2])[0, 1]:.2f}")


if __name__ == "__main__":
    main()
