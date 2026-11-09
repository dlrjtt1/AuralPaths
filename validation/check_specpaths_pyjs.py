"""
Python vs browser engine: ray-guided higher-order specular paths in an OBJ mesh hall (specpaths.py /
engine_geom.js ism(..., spec)). Same mesh, source, receiver, rays and materials; compares the paths found (arrival
distance) and their band energies (absorption, scattering loss, finite reflector; no air).

    python validation/check_specpaths_pyjs.py <calibrated config.json> <src x,y,z> <rec x,y,z> [--order 3]
        [--rays 20000] [--window-ms 250]                                         (needs node on the PATH)

e.g. the BRAS CR4 calibration config of validation/bras_calibration.py with source LS7 and listener MP6 of
validation/check_bras_brir.py (AuralPaths frame).
"""
import argparse
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, HERE)
import brir_proto as bp     # noqa: E402
import specpaths            # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("config"); ap.add_argument("src"); ap.add_argument("rec")
ap.add_argument("--order", type=int, default=3); ap.add_argument("--rays", type=int, default=20000)
ap.add_argument("--window-ms", type=float, default=250.0)
a = ap.parse_args()
cfg = bp.load_config(a.config)
src = [float(v) for v in a.src.split(",")]
rec = [float(v) for v in a.rec.split(",")]
cfg["sources"] = {"S": {"pos": src}}
cfg["receivers"] = {"R": rec}
G = bp._geom(cfg)
c = cfg["c"]
cen = [float(x) for x in bp.make_room(cfg, 0).octave_bands.centers]
d0 = float(np.linalg.norm(np.subtract(rec, src)))
tmx = d0 / c + a.window_ms / 1000
P = specpaths.find_paths(G, np.array(src), np.array([rec]), order=a.order, t_max=tmx, c=c, n_rays=a.rays)[0]
mats = cfg["geometry"]["materials"]
E = [specpaths.path_energy(G, mats, q, src, rec, cen, np.zeros(len(cen)), c) for q in P]
g = cfg["geometry"]["mesh"]
mj = {k: {"R": [float(np.sqrt(max(1e-6, 1 - (v["alpha"][i] if i < len(v["alpha"]) else v["alpha"][-1]))))
                for i in range(len(cen))], "s": v.get("s", 0.0)} for k, v in mats.items()}
job = dict(obj=g.get("obj_text") or open(g["obj"], encoding="utf-8", errors="ignore").read(), groups=g.get("groups", {}),
           axes=g.get("axes", "y-up"), voxel=g.get("voxel", 0.05), src=src, rec=rec, c=c, mats=mj, air=[0.0] * len(cen),
           bands=cen, tWin=a.window_ms / 1000, spec={"order": a.order, "rays": a.rays})
js = """const fs = require('fs'); const GEOM = eval(fs.readFileSync(process.argv[1], 'utf8') + ';GEOM');
const j = JSON.parse(fs.readFileSync(0, 'utf8'));
const G = GEOM.buildMesh({ obj: GEOM.loadObj(j.obj), groups: j.groups, axes: j.axes, voxel: j.voxel }, j.src);
const I = GEOM.ism(G, j.src, [j.rec], 1, j.tWin, j.c, j.mats, j.air, j.bands, j.spec)[0].filter((q) => q.o >= 2);
console.log(JSON.stringify(I.map((q) => [q.d, q.o, Array.from(q.g).map((v) => v * v)])));"""
out = subprocess.run(["node", "--max-old-space-size=4096", "-e", js, os.path.join(HERE, "engine_geom.js")],
                     input=json.dumps(job), capture_output=True, text=True, check=True).stdout
J = json.loads(out)
pd = np.array([q["dist"] for q in P])
jd = np.array([q[0] for q in J])
used, worst, miss_js = set(), 0.0, []
for k, q in enumerate(P):
    cand = [i for i in np.flatnonzero(np.abs(jd - pd[k]) < 1e-4) if i not in used and J[i][1] == q["order"]] if len(jd) else []
    if not cand:
        miss_js.append(k)
        continue
    rel = lambda i: float(np.max(np.abs(np.array(J[i][2]) - E[k]) / np.maximum(E[k], 1e-30)))
    i = min(cand, key=rel)
    used.add(i)
    worst = max(worst, rel(i))
miss_py = [i for i in range(len(J)) if i not in used]
print(f"{len(P)} Python paths, {len(J)} browser paths; matched {len(P) - len(miss_js)}, largest relative energy "
      f"difference {worst:.2e}")
for k in miss_js:
    print(f"  only Python: {1000 * (pd[k] - d0) / c:+.2f} ms after direct, order {P[k]['order']}")
for i in miss_py:
    print(f"  only browser: {1000 * (jd[i] - d0) / c:+.2f} ms after direct, order {J[i][1]}")
sys.exit(1 if (miss_js or miss_py or worst > 1e-3) else 0)
