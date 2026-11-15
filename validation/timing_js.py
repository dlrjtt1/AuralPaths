"""
Where does the computing time of the browser engine go? (diagnostic, 2026-11-15)

engine_geom.js in Node, single thread (the page runs the same code in a pool of workers), for the hall of a config (drawn
or OBJ mesh): build, image sources (GEOM.ism), ray tracing (GEOM.rays with the early / late direction records, as the
page's worker). With --prof the own time per function from Node's CPU profile.

    python validation/timing_js.py <config.json> <source> [--rays 20000] [--recs 0] [--prof]

--recs n: only n receivers (evenly picked; 0 = all). Python engine: validation/timing.py.
"""
import argparse
import glob
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
import brir_proto as bp                       # noqa: E402

JS = """const fs=require('fs');const GEOM=eval(fs.readFileSync('engine_geom.js','utf8')+';GEOM');const j=JSON.parse(fs.readFileSync(0,'utf8'));
const T={},t=(k,f)=>{const a=process.hrtime.bigint();const r=f();T[k]=Number(process.hrtime.bigint()-a)/1e9;return r;};
const G=t('build',()=>j.drawn?GEOM.build(j.drawn):GEOM.buildMesh(Object.assign({},j.mesh,{obj:GEOM.loadObj(j.mesh.text)}),j.src));
const d=(r)=>Math.hypot(j.src[0]-r[0],j.src[1]-r[1],j.src[2]-r[2])/j.c;
t('ism',()=>GEOM.ism(G,j.src,j.recs,j.order,0.25,j.c,j.mats,j.air,j.bands,null));
if(j.spec)t('ism with ray-guided paths of order 2 - 3 (page default in 3-D halls)',()=>GEOM.ism(G,j.src,j.recs,j.order,0.25,j.c,j.mats,j.air,j.bands,j.spec));
const tLate=j.recs.map((r)=>d(r)+0.1),tEarly=j.recs.map((r)=>[0,d(r)+0.02,d(r)+0.05,d(r)+0.11]);
t('rays, energy only',()=>GEOM.rays(G,j.src,j.recs,{n:j.n,c:j.c,seed:5},j.mats,j.air));
t('rays, with early / late directions (as the page)',()=>GEOM.rays(G,j.src,j.recs,{n:j.n,c:j.c,seed:5,tLate,tEarly},j.mats,j.air));
console.log(JSON.stringify(T));"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config"); ap.add_argument("source"); ap.add_argument("--rays", type=int, default=20000)
    ap.add_argument("--recs", type=int, default=0); ap.add_argument("--prof", action="store_true")
    a = ap.parse_args()
    cfg = bp.load_config(a.config)
    g = cfg["geometry"]
    R = [list(map(float, v)) for v in cfg["receivers"].values()]
    if a.recs:
        R = R[:: max(1, len(R) // a.recs)][: a.recs]
    room = bp.make_room(cfg, 0)
    air = np.asarray(room.air_absorption, float).tolist()
    nb = len(air)
    mats = {k: {"R": [float(np.sqrt(1 - x)) for x in (list(v["alpha"]) + [v["alpha"][-1]] * nb)[:nb]],
                "s": float(np.mean(v.get("s", 0.0)))} for k, v in g["materials"].items()}
    if bp.is_mesh(cfg):
        m = g["mesh"]
        hall = dict(drawn=None, mesh={"text": m.get("obj_text") or open(m["obj"]).read(), "groups": m.get("groups", {}),
                                      "default": m.get("default", "wall"), "axes": m.get("axes", "y-up"),
                                      "voxel": float(m.get("voxel", 0.05))})
    else:
        hall = dict(drawn={"plan": g["plan"], "floor": g["floor"], "ceil": g["ceiling"], "stageY": bp.stage_y(cfg)})
    job = dict(**hall,
               src=list(map(float, cfg["sources"][a.source]["pos"])), recs=R, mats=mats, air=air, c=cfg["c"],
               n=a.rays, order=bp.early_order(cfg), bands=[float(x) for x in room.octave_bands.centers])
    with tempfile.TemporaryDirectory() as d:
        cmd = ["node"] + (["--cpu-prof", "--cpu-prof-dir", d] if a.prof else []) + ["-e", JS]
        r = subprocess.run(cmd, input=json.dumps(job), capture_output=True, text=True, cwd=ROOT)
        if r.returncode:
            sys.exit(r.stderr[-1500:])
        T = json.loads(r.stdout.strip().splitlines()[-1])
        print(f"{len(R)} receivers, {a.rays} rays, image-source order {job['order']}, one thread")
        for k, v in T.items():
            print(f"  {v:7.1f} s  {k}")
        if a.prof:
            P = json.load(open(glob.glob(os.path.join(d, "*.cpuprofile"))[0]))
            dt = np.diff(P["timeDeltas"], prepend=0) * 0 + np.asarray(P["timeDeltas"], float)
            own = {}
            name = {n["id"]: n["callFrame"]["functionName"] or "(anonymous)" for n in P["nodes"]}
            for s, t in zip(P["samples"], dt):
                own[name[s]] = own.get(name[s], 0.0) + t / 1e6
            tot = sum(own.values())
            print("  own time per function (all stages together):")
            for k, v in sorted(own.items(), key=lambda x: -x[1])[:12]:
                print(f"    {v:7.1f} s  {100 * v / tot:5.1f} %  {k}")


if __name__ == "__main__":
    main()
