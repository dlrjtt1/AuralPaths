"""
Browser engine (engine_geom.js) vs Python on a BRAS OBJ hall: room criteria from the browser mesh path (buildMesh,
first-order image sources, ray tracing) against the Python 3D results in validation/bras_<hall>.csv and the measured
values in the same file.

    python validation/check_mesh_pyjs.py <BRAS folder> CR3 [--voxel 0.05] [--rays 16000]   (needs node on the PATH)

<BRAS folder> holds "3 Surface descriptions" and the scene folders ("CR3 medium room (chamber music hall)", ...), as
for validate_bras_cr.py. Materials: BRAS fitted estimates; positions: the measured ones (2 sources x 5 receivers).
The early part is the image-source histogram plus the ray-traced remainder (as the page and brir_proto do).

Result on 2026-11-06 (500 Hz - 2 kHz band means over the 10 position pairs, browser vs Python with the fixed
ray-tracing energy floor, brir_proto.RT_ENERGY_THRES; browser rays with their own random stream per ray):
    CR3 (voxel 5 cm, 16 000 rays): T30 1.42 / 1.47 / 1.46 s vs 1.40 / 1.44 / 1.43 s; C80 within 0.1 dB
    CR4 (voxel 8 cm,  8 000 rays): T30 2.25 / 2.27 / 2.02 s vs 2.28 / 2.30 / 2.05 s; C80 within 0.2 dB
One ray realisation: at 10 000 rays the CR3 T30 band means moved by up to 6 % between seeds.
"""
import argparse
import csv
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import brir_proto as bp                       # noqa: E402
import validate_bras_cr as vb                 # noqa: E402
from validate_fratoni import criteria, BANDS  # noqa: E402

SCENES = {"CR3": "CR3 medium room (chamber music hall)", "CR4": "CR4 large room (auditorium)"}
JS = """const fs=require('fs');const GEOM=eval(fs.readFileSync('engine_geom.js','utf8')+';GEOM');const j=JSON.parse(fs.readFileSync(0,'utf8'));
const G=GEOM.buildMesh({obj:GEOM.loadObj(j.obj),groups:j.groups,voxel:j.voxel},Object.values(j.srcs)[0]);const out={};
for(const [name,s] of Object.entries(j.srcs)){const I=GEOM.ism(G,s,j.recs,1,10,j.c,j.mats,j.air,j.bands);
const R=GEOM.rays(G,s,j.recs,{n:j.n,c:j.c,tMax:3.0,bin:j.bin,seed:7},j.mats,j.air);
out[name]={lost:R.escaped+R.leaked,H:R.H.map(h=>h.map(b=>Array.from(b))),I:I.map(L=>L.map(q=>[q.t,Array.from(q.g).map(v=>v*v)]))};}
console.log(JSON.stringify(out));"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras"); ap.add_argument("hall", choices=list(SCENES))
    ap.add_argument("--voxel", type=float, default=None); ap.add_argument("--rays", type=int, default=16000)
    a = ap.parse_args()
    voxel = a.voxel or (0.05 if a.hall == "CR3" else 0.08)
    scene = os.path.join(a.bras, SCENES[a.hall])
    mats = vb.read_bras_materials(os.path.join(a.bras, "3 Surface descriptions"), a.hall, "fitted")
    _, _, E, R, eid, rid, _ = vb.read_rirs(scene)
    import pyroomacoustics as pra
    room = pra.ShoeBox([5, 5, 5], fs=48000, air_absorption=True)      # band centres and air absorption, as the page
    cen = [float(x) for x in room.octave_bands.centers]; air = [float(x) for x in room.air_absorption]
    mj = {k: {"R": [float(np.sqrt(1 - v["alpha"][min(i, len(v["alpha"]) - 1)])) for i in range(len(cen))], "s": v["s_oct"]} for k, v in mats.items()}
    srcs = {f"LS{e}": list(map(float, E[i])) for i, e in enumerate(eid)}; recs = {f"MP{r}": list(map(float, R[i])) for i, r in enumerate(rid)}
    job = dict(obj=open(os.path.join(scene, "Geometry", a.hall + ".obj")).read(), groups={k: k for k in mats}, voxel=voxel, srcs=srcs,
               recs=list(recs.values()), c=343.5, mats=mj, bands=cen, air=air, n=a.rays, bin=bp.HIST_BIN)
    r = subprocess.run(["node", "--max-old-space-size=6000", "-e", JS], input=json.dumps(job), capture_output=True, text=True,
                       cwd=os.path.join(HERE, ".."))
    if r.returncode:
        sys.exit(r.stderr[-3000:])
    o = json.loads(r.stdout)
    rows = [x for x in csv.DictReader(open(os.path.join(HERE, f"bras_{a.hall}.csv"))) if x["model"] == "3D mesh"]
    py = {(x["pair"], x["criterion"], int(float(x["band_hz"]))): float(x["simulated"]) for x in rows}
    me = {(x["pair"], x["criterion"], int(float(x["band_hz"]))): float(x["measured"]) for x in rows}
    bi = [cen.index(min(cen, key=lambda c: abs(c - b))) for b in BANDS]
    val = {}
    for sn, so in o.items():
        for k, (rn, rp) in enumerate(recs.items()):
            Hr = np.array(so["H"][k]); Hi = np.zeros_like(Hr)
            for t, e in so["I"][k]:
                if int(t / bp.HIST_BIN) < Hr.shape[1]:
                    Hi[:, int(t / bp.HIST_BIN)] += e
            H = Hi + np.maximum(0, bp._smooth(Hr) - bp._smooth(Hi))
            cr = criteria(H[bi], np.linalg.norm(np.subtract(rp, srcs[sn])) / 343.5)
            for c in ("T30", "EDT", "C80", "C50", "Ts"):
                for i, b in enumerate(BANDS):
                    key = (f"{sn}-{rn}", c, b)
                    if key in py:
                        val.setdefault((c, b), []).append((cr[c][i], py[key], me[key]))
    print(f"{a.hall}: voxel {voxel} m, {a.rays} rays per source; band means over position pairs (browser / Python / measured)")
    for c in ("T30", "EDT", "C80", "C50", "Ts"):
        print(f"  {c:4s} " + " | ".join(f"{b}: {np.mean([x[0] for x in val[(c, b)]]):.2f} / {np.mean([x[1] for x in val[(c, b)]]):.2f} / "
                                        f"{np.mean([x[2] for x in val[(c, b)]]):.2f}" for b in BANDS if (c, b) in val))


if __name__ == "__main__":
    main()
