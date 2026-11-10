"""
Python vs browser engine: first-order UTD edge diffraction (diffraction.py / engine_geom.js diffract) for every source
and receiver of a drawn hall, without source directivity.
    python validation/check_diffraction_pyjs.py examples/fan_hall_config.json      (needs node on the PATH)
    python validation/check_diffraction_pyjs.py --rs5   (BRAS RS5 partition on a floor: thin-plate edges and
                                                         diffraction combined with floor reflections, refl_order 1)
    python validation/check_diffraction_pyjs.py --rs6   (BRAS RS6 body on a floor: second-order diffraction,
                                                         diffract2 / GEOM.diffract2, refl_order 1)
Every Python arrival must have a browser arrival at the same path length (1e-6 m); the band energies (with the
interference terms) are compared. Prints the number of arrivals and the largest relative and absolute differences.
"""
import copy
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, HERE)
import brir_proto as bp     # noqa: E402

if sys.argv[1] in ("--rs5", "--rs6"):
    sys.path.insert(0, os.path.join(HERE, "validation"))
    import diffraction     # noqa: E402
    cen = [125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0]
    Rb = {"tiles": [0.99, 0.99, 0.99, 0.99, 0.98, 0.98, 0.98], "mdf": [0.97, 0.98, 0.99, 0.99, 0.99, 0.99, 0.99],
          "mdf12": [0.96, 0.97, 0.98, 0.99, 0.99, 0.99, 0.99]}
    if sys.argv[1] == "--rs5":
        import bras_rs5    # noqa: E402
        G = bras_rs5.scene_geometry()
        S0 = [[2.487, 2.985, z] for z in (0.135, 1.235, 2.0, 3.0)]
        R0 = [[8.512, 2.985, z] for z in (0.006, 1.235, 2.0, 3.0)] + [[8.512, 4.6, 1.5]]
        order = 1
    else:                  # BRAS RS6: a 0.72 m body on a floor, second-order diffraction over its two top edges
        import bras_rs     # noqa: E402
        G = bras_rs.scene("RS6", "")
        S0 = [[2.487, 2.985, z] for z in (0.176, 0.8)] + [[2.487, 3.9, 0.4]]
        R0 = [[8.512, 2.985, z] for z in (0.006, 0.4, 0.8)] + [[8.512, 1.5, 0.3]]
        order = 2
    E = diffraction.edges(G)
    pairs = [[s, r] for s in S0 for r in R0]
    fn = diffraction.diffract if order == 1 else diffraction.diffract2
    py = [[[float(q["d"]), [float(x) for x in q["eb"]]] for q in
           fn(G, E, s, r, 343.0, lambda k: np.array(Rb[G["S"][k]["mat"]]), np.zeros(7), cen, 0.3,
              refl_order=1)] for s, r in pairs]
    surf = [{"verts": s["verts"].tolist(), "n": s["n"].tolist(), "mat": s["mat"]} for s in G["S"]]
    js = """const fs = require('fs'); const GEOM = eval(fs.readFileSync(process.argv[1], 'utf8') + ';GEOM');
const j = JSON.parse(fs.readFileSync(0, 'utf8')); const G = { S: j.S.map((s) => GEOM.makeSurface(s.verts, s.n, s.mat, 'wall')) };
const E = GEOM.edges(G);
const fn = j.order === 2 ? GEOM.diffract2 : GEOM.diffract;
console.log(JSON.stringify(j.pairs.map(([s, r]) => fn(G, E, s, r, 343, j.mats, j.air, j.bands, 0.3, 1).map((q) => [q.d, q.eb]))));"""
    J = json.loads(subprocess.run(["node", "-e", js, os.path.join(HERE, "engine_geom.js")], capture_output=True, text=True,
                                  check=True, input=json.dumps(dict(S=surf, pairs=pairs, mats={k: {"R": v} for k, v in Rb.items()},
                                                                    air=[0.0] * 7, bands=cen, order=order))).stdout)
    print(f"edges: Python {len(E)} ({sum(1 for e in E if e.get('thin'))} thin)")
else:
    J = None
cfg = None if J is not None else copy.deepcopy(bp.load_config(sys.argv[1]))
if J is None:
    for s in cfg["sources"].values():
        if isinstance(s, dict):
            s.pop("directivity", None)
    cen = [125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0]
    nb = len(cen)
    mats = {k: {"R": [float(np.sqrt(max(1e-6, 1 - (v["alpha"][i] if i < len(v["alpha"]) else v["alpha"][-1])))) for i in range(nb)]}
            for k, v in cfg["geometry"]["materials"].items()}
    g = cfg["geometry"]
    pairs, py = [], []
    for src in bp.source_names(cfg):
        for rec in bp.receiver_names(cfg):
            A = bp.diffraction_arrivals(cfg, src, rec, np.array(cen), np.zeros(nb), 0.3)
            pairs.append([cfg["sources"][src]["pos"], cfg["receivers"][rec]])
            py.append([[float(q["d"]), [float(x) for x in q["eb"]]] for q in A])
    job = dict(geom={"plan": g["plan"], "floor": g["floor"], "ceil": g["ceiling"], "stageY": bp.stage_y(cfg)},
               pairs=pairs, c=cfg["c"], mats=mats, air=[0.0] * nb, bands=cen)
    js = """const fs = require('fs'); const GEOM = eval(fs.readFileSync(process.argv[1], 'utf8') + ';GEOM');
    const j = JSON.parse(fs.readFileSync(0, 'utf8')); const G = GEOM.build(j.geom), E = GEOM.edges(G);
    console.log(JSON.stringify(j.pairs.map(([s, r]) => GEOM.diffract(G, E, s, r, j.c, j.mats, j.air, j.bands, 0.3).map((q) => [q.d, q.eb]))));"""
    J = json.loads(subprocess.run(["node", "-e", js, os.path.join(HERE, "engine_geom.js")], input=json.dumps(job),
                                  capture_output=True, text=True, check=True).stdout)
n, worst_rel, worst_abs = 0, 0.0, 0.0
for P, Q in zip(py, J):
    if len(P) != len(Q):
        raise SystemExit(f"arrival count differs: Python {len(P)}, browser {len(Q)}")
    qd = np.array([q[0] for q in Q]) if Q else np.zeros(0)
    for d, eb in P:
        i = int(np.argmin(np.abs(qd - d)))
        if abs(qd[i] - d) > 1e-6:
            raise SystemExit(f"diffracted path {d:.6f} m has no browser counterpart")
        a, b = np.array(eb), np.array(Q[i][1])
        scale = max(np.max(np.abs(a)), 1e-30)
        worst_abs = max(worst_abs, float(np.max(np.abs(a - b)) / scale))
        worst_rel = max(worst_rel, float(np.max(np.abs(a - b) / np.maximum(np.abs(a), 1e-12 * scale))))
        n += 1
print(f"{len(pairs)} source-receiver pairs, {n} diffracted arrivals, all matched; largest difference "
      f"{worst_abs:.2e} of the arrival's largest band energy (relative per band {worst_rel:.2e})")
