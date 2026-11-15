"""
Ray-traced room criteria of a DRAWN hall, browser engine vs Python engine, same geometry and materials (2026-11-15).

Browser: GEOM.rays of engine_geom.js in Node (a reflection is specular or Lambert with probability s). Python:
brir_proto.energy_hists (pyroomacoustics ray tracer: every reflection goes in the mixed direction s * Lambert +
(1 - s) * specular). Every 6th receiver of the config; T30, EDT, C80 per octave band, mean over the receivers.
Mesh halls are compared in check_mesh_pyjs.py (there the browser mixes the direction as pyroomacoustics does).

    python validation/check_drawn_pyjs.py <config.json> <source> [rays, default 20000]
"""
import json, subprocess, sys
import numpy as np
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import brir_proto as bp
JS = """const fs=require('fs');const GEOM=eval(fs.readFileSync('engine_geom.js','utf8')+';GEOM');const j=JSON.parse(fs.readFileSync(0,'utf8'));
const G=GEOM.build(j.drawn);const T=GEOM.rays(G,j.src,j.recs,{n:j.n,c:j.c,seed:8919},j.mats,j.air);
console.log(JSON.stringify({H:T.H.map((b)=>b.map((x)=>Array.from(x))),esc:T.escaped,area:G.area,mats:G.S.map((s)=>s.mat)}));"""
cfg = bp.load_config(sys.argv[1]); g = cfg['geometry']; src = sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 20000
names = list(cfg['receivers'])[::6]; R = [list(map(float, cfg['receivers'][k])) for k in names]; S = list(map(float, cfg['sources'][src]['pos']))
room = bp.make_room(cfg, 0); air = np.asarray(room.air_absorption, float).tolist(); nb = len(air); cen = room.octave_bands.centers
mats = {k: {"R": [float(np.sqrt(1 - x)) for x in (list(v["alpha"]) + [v["alpha"][-1]] * nb)[:nb]], "s": float(np.mean(v.get("s", 0.0)))} for k, v in g["materials"].items()}
job = dict(drawn={"plan": g["plan"], "floor": g["floor"], "ceil": g["ceiling"], "stageY": bp.stage_y(cfg)}, src=S, recs=R, mats=mats, air=air, c=cfg["c"], n=n)
r = subprocess.run(["node", "-e", JS], input=json.dumps(job), capture_output=True, text=True,
                   cwd=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if r.returncode: sys.exit(r.stderr[-800:])
O = json.loads(r.stdout); H = np.array(O["H"])
hp, _ = bp.energy_hists(cfg, src, names, n_rays=n, seed=1)
G = bp._geom(cfg)
print("escaped rays JS", O["esc"], "| surfaces JS", len(O["mats"]), "Python", len(G["S"]))
import collections
print("JS mats", collections.Counter(O["mats"])); print("Py mats", collections.Counter(q["mat"] for q in G["S"]))
for b in (250, 500, 1000, 2000):
    row = []
    for lab, hh in (("JS", [H[i] for i in range(len(R))]), ("Py", [hp[k] for k in names])):
        m = [bp.iso3382_energy([(h, 0.0, 1.0)], np.linalg.norm(np.subtract(S, R[i])) / cfg["c"], bands=(b,), centers=cen) for i, h in enumerate(hh)]
        row.append(f"{lab}: T30 {np.nanmean([x['T30'] for x in m]):.2f} EDT {np.mean([x['EDT'] for x in m]):.2f} C80 {np.mean([x['C80'] for x in m]):+.2f}")
    print(b, " | ".join(row))
