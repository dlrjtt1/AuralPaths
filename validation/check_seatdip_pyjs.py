"""
Python vs browser engine: the seat-dip transfer function (seatdip.path_transfer / engine_geom.js seatPath) for every
source and receiver of a drawn hall, with the default seat settings.

    python validation/check_seatdip_pyjs.py examples/fan_hall_config.json     (needs node on the PATH)

Prints, per pair, whether a seat dip applies (rows in the cross-section), the octave-band level change of the direct
sound, and the largest difference |T_py - T_js| over all bins.
"""
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, HERE)
import brir_proto as bp     # noqa: E402
import geometry             # noqa: E402
import seatdip              # noqa: E402

cfg = bp.load_config(sys.argv[1])
g = cfg["geometry"]
G = geometry.build(g, bp.stage_y(cfg))
prm = seatdip.seat_params(g.get("seat_dip") or {})
fs, c = cfg["fs"], cfg["c"]
pairs, py = [], []
t = time.time()
for src in bp.source_names(cfg):
    for rec in bp.receiver_names(cfg):
        S, R = cfg["sources"][src]["pos"], cfg["receivers"][rec]
        pairs.append([src, rec, S, R])
        py.append(seatdip.path_transfer(G, S, R, prm, fs, c))
tp = time.time() - t
job = dict(geom={"plan": g["plan"], "floor": g["floor"], "ceil": g["ceiling"], "stageY": bp.stage_y(cfg)},
           pairs=[[S, R] for _, _, S, R in pairs], prm=prm, fs=fs, c=c)
js = """const fs = require('fs'); const GEOM = eval(fs.readFileSync(process.argv[1], 'utf8') + ';GEOM');
const j = JSON.parse(fs.readFileSync(0, 'utf8')), G = GEOM.build(j.geom), t = Date.now();
const out = j.pairs.map(([s, r]) => { const T = GEOM.seatPath(G, s, r, j.prm, j.fs, j.c); return T ? [Array.from(T.re), Array.from(T.im)] : null; });
console.log(JSON.stringify({ out, ms: Date.now() - t }));"""
J = json.loads(subprocess.run(["node", "-e", js, os.path.join(HERE, "engine_geom.js")], input=json.dumps(job),
                              capture_output=True, text=True, check=True).stdout)
worst, n = 0.0, 0
bands = [125, 250, 500, 1000, 2000]
for (src, rec, _, _), T, Q in zip(pairs, py, J["out"]):
    if (T is None) != (Q is None):
        raise SystemExit(f"{src}-{rec}: seat dip applies in {'Python' if T is not None else 'the browser'} only")
    if T is None:
        print(f"{src}-{rec}: no seat dip")
        continue
    Tj = np.array(Q[0]) + 1j * np.array(Q[1])
    dd = float(np.max(np.abs(T - Tj)))
    worst = max(worst, dd)
    n += 1
    if dd > 1e-6:
        print(f"   {src}-{rec}: |T_py - T_js| up to {dd:.2e} at bin {int(np.argmax(np.abs(T - Tj)))}")
    e = seatdip.band_energy(T, fs, bands)
    print(f"{src}-{rec}: " + ", ".join(f"{b} Hz {10 * np.log10(v):+.1f} dB" for b, v in zip(bands, e)))
print(f"{n} of {len(pairs)} pairs with a seat dip; largest |T_py - T_js| {worst:.2e}; time Python {tp:.1f} s, "
      f"browser engine (node) {J['ms'] / 1000:.1f} s")
if worst > 1e-6:
    raise SystemExit("Python and browser differ")
