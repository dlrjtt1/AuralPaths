"""
Python vs page's engine on the geometries of the BRAS reference scenes RS1 - RS4, RS6, RS7 (validation/bras_rs.py):
are the edge-diffracted arrivals of diffraction.py (which bras_rs.py uses) the same as those of engine_geom.js
(GEOM.edges / GEOM.diffract, which the page uses)?
    python validation/check_rs_pyjs.py            (needs node on the PATH; no BRAS data needed)
The reference scenes are free-standing plates and bodies in an anechoic or hemi-anechoic room; the page models rooms,
so these scenes cannot be loaded into the page. bras_rs.py therefore sums the arrivals of the Python implementation of
the same formulas. This check shows that the page's implementation returns the same arrivals on these geometries:
for a grid of source and receiver positions per scene, every Python arrival must have a page arrival at the same path
length (1e-6 m), and the band energies (with the interference terms) are compared. First order with one reflection
before / after (refl_order 1; RS7: 0, as in bras_rs.py); thin-plate edges on (the default). RS5 and the second order
(RS6) are covered by check_diffraction_pyjs.py --rs5 / --rs6.
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, ".."), HERE]
import bras_rs            # noqa: E402
import diffraction        # noqa: E402

CEN = [125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0]
RB = {"tiles": [0.99, 0.99, 0.99, 0.99, 0.98, 0.98, 0.98], "mdf25a": [0.97, 0.98, 0.99, 0.99, 0.99, 0.99, 0.99],
      "mdf25b": [0.96, 0.98, 0.98, 0.99, 0.99, 0.99, 0.99], "mdf12": [0.96, 0.97, 0.98, 0.99, 0.99, 0.99, 0.99],
      "rockfon": [0.95, 0.85, 0.6, 0.4, 0.35, 0.3, 0.3], "diffusor": [0.95, 0.9, 0.8, 0.7, 0.6, 0.5, 0.5]}
FLOOR_S = [[2.487, 2.985, z] for z in (0.176, 0.8)] + [[2.487, 3.9, 0.4]]
FLOOR_R = [[8.512, 2.985, z] for z in (0.006, 0.4, 0.8)] + [[8.512, 1.5, 0.3]]
PLATE_S = [[3.46, 2.0, 1.02], [2.83, 2.83, 1.02], [2.0, 3.46, 1.3]]
PLATE_R = [[3.46, -2.0, 1.02], [-3.0, 0.5, 1.0], [-2.0, -1.0, 1.5]]
CASES = [("RS1", "Rigid", FLOOR_S, FLOOR_R), ("RS1", "Absorbing", FLOOR_S, FLOOR_R), ("RS1", "Diffuse", FLOOR_S, FLOOR_R),
         ("RS2", "1m", PLATE_S, PLATE_R), ("RS2", "2m", PLATE_S, PLATE_R), ("RS2", "1m_absorbing", PLATE_S, PLATE_R),
         ("RS3", "", [[3.0, 0.0, 1.02], [3.0, 0.4, 1.3]], [[7.0, 0.0, 1.02], [7.0, -0.5, 0.8], [12.0, 0.3, 1.0]]),
         ("RS4", "", PLATE_S, PLATE_R), ("RS6", "", FLOOR_S, FLOOR_R), ("RS7", "", FLOOR_S[:2], FLOOR_R[:3])]
JS = """const fs = require('fs'); const GEOM = eval(fs.readFileSync(process.argv[1], 'utf8') + ';GEOM');
const j = JSON.parse(fs.readFileSync(0, 'utf8')); const G = { S: j.S.map((s) => GEOM.makeSurface(s.verts, s.n, s.mat, 'wall')) };
const E = GEOM.edges(G);
console.log(JSON.stringify({ edges: E.length, arr: j.pairs.map(([s, r]) => GEOM.diffract(G, E, s, r, 343, j.mats, j.air, j.bands, 0.3, j.refl).map((q) => [q.d, q.eb])) }));"""

worst_rel = worst_abs = 0.0
total = 0
for name, cfg, S0, R0 in CASES:
    G = bras_rs.scene(name, cfg)
    E = diffraction.edges(G)
    refl = 0 if name == "RS7" else 1
    pairs = [[s, r] for s in S0 for r in R0]
    py = [[[float(q["d"]), [float(x) for x in q["eb"]]] for q in
           diffraction.diffract(G, E, s, r, 343.0, lambda k: np.array(RB[G["S"][k]["mat"]]), np.zeros(7), CEN, 0.3,
                                refl_order=refl)] for s, r in pairs]
    surf = [{"verts": s["verts"].tolist(), "n": s["n"].tolist(), "mat": s["mat"]} for s in G["S"]]
    J = json.loads(subprocess.run(["node", "-e", JS, os.path.join(HERE, "..", "engine_geom.js")], capture_output=True, text=True, check=True,
                                  input=json.dumps(dict(S=surf, pairs=pairs, mats={k: {"R": v} for k, v in RB.items()},
                                                        air=[0.0] * 7, bands=CEN, refl=refl))).stdout)
    n = miss = 0
    rel = ab = 0.0
    for a, b in zip(py, J["arr"]):
        if len(a) != len(b):
            miss += abs(len(a) - len(b))
        for d, eb in a:
            m = [q for q in b if abs(q[0] - d) < 1e-6]
            if not m:
                miss += 1
                continue
            n += 1
            e = np.array(eb); f = np.array(m[0][1])
            ab = max(ab, float(np.max(np.abs(e - f))))
            rel = max(rel, float(np.max(np.abs(e - f) / np.maximum(np.abs(e), 1e-30))))
    total += n
    worst_rel, worst_abs = max(worst_rel, rel), max(worst_abs, ab)
    print(f"{name} {cfg or '-'}: edges Python {len(E)} / page {J['edges']}, {len(pairs)} pairs, {n} diffracted arrivals, "
          f"unmatched {miss}, largest difference {ab:.3g} (relative {rel:.3g})", flush=True)
    if miss or len(E) != J["edges"]:
        sys.exit("arrivals differ")
print(f"all scenes: {total} diffracted arrivals, largest difference {worst_abs:.3g} (relative {worst_rel:.3g})")
