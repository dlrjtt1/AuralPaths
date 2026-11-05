"""
Python vs browser engine: image-source energies with the specular reflection factors (finite panel size and
scattering loss, reflections.py / engine_geom.js specFactor) for the first source and receiver of a drawn hall.

    python validation/check_specular_pyjs.py examples/fan_hall_config.json 4      (needs node on the PATH)

Result on 2026-11-06 (fan hall, orders 2 / 3 / 4: 18 / 48 / 94 images): every image matched, largest relative energy
difference 1.4e-6 / 1.5e-6 / 2.3e-6.
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, HERE)
import brir_proto as bp     # noqa: E402

cfg = bp.load_config(sys.argv[1])
order = int(sys.argv[2]) if len(sys.argv) > 2 else 2
cfg["geometry"]["ism_order"] = order
src, rec = bp.source_names(cfg)[0], bp.receiver_names(cfg)[0]
room = bp.make_room(cfg, order)
room.add_source(cfg["sources"][src]["pos"])
room.add_microphone(cfg["receivers"][rec])
room.image_source_model()
S = room.sources[0]
vis = np.flatnonzero(room.visibility[0][0].astype(bool))
m = np.asarray(cfg["receivers"][rec], float)
d = np.linalg.norm(S.images[:, vis] - m[:, None], axis=0)
F = bp.specular_factors(cfg, room, vis, cfg["sources"][src]["pos"], m)
E = (S.damping[:, vis] / d) ** 2 * (F if F is not None else 1)
cen = [float(x) for x in room.octave_bands.centers]
mats = {k: {"R": [float(np.sqrt(max(1e-6, 1 - (v["alpha"][i] if i < len(v["alpha"]) else v["alpha"][-1]))))
                  for i in range(len(cen))], "s": v.get("s", 0.0)} for k, v in cfg["geometry"]["materials"].items()}
g = cfg["geometry"]
job = dict(geom={"plan": g["plan"], "floor": g["floor"], "ceil": g["ceiling"], "stageY": bp.stage_y(cfg)},
           src=cfg["sources"][src]["pos"], rec=cfg["receivers"][rec], order=order, c=cfg["c"], mats=mats,
           air=[0.0] * len(cen), bands=cen)
js = """const fs = require('fs'); const GEOM = eval(fs.readFileSync(process.argv[1], 'utf8') + ';GEOM');
const j = JSON.parse(fs.readFileSync(0, 'utf8')); const G = GEOM.build(j.geom);
const I = GEOM.ism(G, j.src, [j.rec], j.order, 10, j.c, j.mats, j.air, j.bands)[0];
console.log(JSON.stringify(I.map((q) => [q.d, Array.from(q.g).map((v) => v * v)])));"""
out = subprocess.run(["node", "-e", js, os.path.join(HERE, "engine_geom.js")], input=json.dumps(job),
                     capture_output=True, text=True, check=True).stdout
J = json.loads(out)
jd = np.array([q[0] for q in J])
used, worst = set(), 0.0
for k in range(len(d)):
    cand = [i for i in np.flatnonzero(np.abs(jd - d[k]) < 1e-4) if i not in used]
    if not cand:
        raise SystemExit(f"image at {d[k]:.4f} m has no browser counterpart")
    rel = lambda i: float(np.max(np.abs(np.array(J[i][1]) - E[:, k]) / np.maximum(E[:, k], 1e-30)))
    i = min(cand, key=rel)
    used.add(i)
    worst = max(worst, rel(i))
print(f"order {order}: {len(d)} Python images, {len(J)} browser images, all matched; largest relative energy "
      f"difference {worst:.2e}")
