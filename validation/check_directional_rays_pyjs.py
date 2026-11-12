"""
Directional sources in the ray tracing, browser engine vs Python (2026-11-12).

Python (brir_proto.rt_add_source) launches every ray with the energy amp(d)^2 of the source pattern. The browser
engine traces once without the pattern and keeps the receiver energy before tSect per launch sector (GEOM.rays
nSect, 64 Fibonacci sectors), which the page weights by amp^2 afterwards (viewer geomHist; 1 / Q after tSect). This
check compares, for a mesh hall and a directional source, the ray-traced energy of both engines at a few receivers
in three windows (0 - 80 ms, 80 - 250 ms after the direct sound, after 250 ms), and the same for the source made
omnidirectional (the difference of the two tracers without any pattern).

    python validation/check_directional_rays_pyjs.py <config.json> <source> [--recs A101,A109,A207] [--rays 20000]

Needs node on the PATH. The config must be a mesh hall (geometry.mesh.obj_text) with a polar-table directivity.
"""
import argparse
import copy
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import brir_proto as bp                       # noqa: E402
import pyroomacoustics as pra                 # noqa: E402

JS = """const fs=require('fs');const GEOM=eval(fs.readFileSync('engine_geom.js','utf8')+';GEOM');const j=JSON.parse(fs.readFileSync(0,'utf8'));
const G=GEOM.buildMesh({obj:GEOM.loadObj(j.obj),groups:j.groups,voxel:j.voxel,axes:j.axes,rot:j.rot,shift:j.shift},j.src);
const R=GEOM.rays(G,j.src,j.recs,{n:j.n,c:j.c,tMax:2.0,bin:j.bin,seed:7,nSect:64,tSect:0.25},j.mats,j.air);
const dm=j.table?GEOM.dirModel({az:j.az,el:j.el,table:j.table},j.bands):null;
const A2=dm?R.sect.map((d)=>dm.amp(d).map((a)=>a*a)):null;
const out=R.H.map((Hm,m)=>Hm.map((h,b)=>{const o=Array.from(h,(v)=>v*(dm?j.table.diffuse[b]:1));
 if(A2){for(let t=0;t<R.nSb;t++){let v=0;for(let q=0;q<A2.length;q++)v+=R.HS[m][(q*Hm.length+b)*R.nSb+t]*A2[q][b];o[t]=v;}}return o;}));
console.log(JSON.stringify(out));"""


def windows(h, t0):
    """Band energies (dB) in t0 - 1 ms ... t0 + 80 ms, t0 + 80 ms ... 250 ms and after 250 ms (time from emission;
    250 ms = the end of the browser's launch-sector window)."""
    t = (np.arange(h.shape[1]) + 0.5) * bp.HIST_BIN
    return [10 * np.log10(np.maximum(h[:, (t >= a) & (t < b)].sum(axis=1), 1e-30))
            for a, b in ((t0 - 0.001, t0 + 0.080), (t0 + 0.080, 0.250), (0.250, 9.0))]


def py_rays(cfg, src, recs, n):
    room = bp.make_room(cfg, 0)
    rt = bp.make_room(cfg, 0, ray_tracing=True)
    rt.set_ray_tracing(n_rays=n, receiver_radius=0.5, hist_bin_size=bp.HIST_BIN, time_thres=2.0, energy_thres=bp.RT_ENERGY_THRES)
    bp.rt_add_source(rt, cfg, src, room.octave_bands.centers)
    rt.add_microphone_array(np.array([cfg["receivers"][r] for r in recs], float).T)
    pra.libroom.set_rng_seed(7)
    rt.ray_tracing()
    t_c = (np.arange(2000) + 0.5) * bp.HIST_BIN
    out = []
    for i in range(len(recs)):
        raw = np.asarray(rt.rt_histograms[i][0][0])[:, :2000]
        h = np.zeros((raw.shape[0], 2000)); h[:, :raw.shape[1]] = raw
        out.append(h * np.exp(-np.outer(np.asarray(room.air_absorption, float), cfg["c"] * t_c)))
    return out, room.octave_bands.centers, room.air_absorption


def js_rays(cfg, src, recs, n, centers, air):
    g = cfg["geometry"]
    mats = {k: {"R": [float(np.sqrt(1 - v["alpha"][min(i, len(v["alpha"]) - 1)])) for i in range(len(centers))], "s": v["s"]}
            for k, v in g["materials"].items()}
    dm = bp.dir_model(cfg, src, centers)
    job = dict(obj=g["mesh"]["obj_text"], groups=g["mesh"]["groups"], voxel=g["mesh"].get("voxel", 0.05),
               axes=g["mesh"].get("axes", "y-up"), rot=g["mesh"].get("rotate_deg", 0.0), shift=g["mesh"].get("shift", [0, 0, 0]),
               src=cfg["sources"][src]["pos"], recs=[cfg["receivers"][r] for r in recs], mats=mats, c=cfg["c"],
               air=[float(x) for x in air], bands=[float(x) for x in centers], n=n, bin=bp.HIST_BIN)
    if dm is not None:
        sp = cfg["sources"][src].get("aim", {})
        job.update(az=sp.get("az", 0.0), el=sp.get("el", 0.0),
                   table={"h": dm["tab"]["h"].tolist(), "v": dm["tab"]["v"].tolist(), "diffuse": dm["diffuse"].tolist()})
    r = subprocess.run(["node", "--max-old-space-size=6000", "-e", JS], input=json.dumps(job), capture_output=True, text=True,
                       cwd=os.path.join(HERE, ".."))
    if r.returncode:
        sys.exit(r.stderr[-2000:])
    return [np.array(x) for x in json.loads(r.stdout)]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config"); ap.add_argument("source")
    ap.add_argument("--recs", default="A101,A109,A207"); ap.add_argument("--rays", type=int, default=20000)
    a = ap.parse_args()
    cfg = bp.load_config(a.config)
    recs = a.recs.split(",")
    omni = copy.deepcopy(cfg)
    for k in ("directivity", "coverage", "aim"):
        omni["sources"][a.source].pop(k, None)
    for lab, c in (("directional", cfg), ("omnidirectional", omni)):
        P, cen, air = py_rays(c, a.source, recs, a.rays)
        J = js_rays(c, a.source, recs, a.rays, cen, air)
        print(f"\n{lab}: ray-traced energy, browser - Python (dB), 125 Hz - 4 kHz, windows t0 ... t0 + 80 ms | t0 + 80 ... 250 ms | after 250 ms")
        for r, hp, hj in zip(recs, P, J):
            t0 = np.linalg.norm(np.array(c["sources"][a.source]["pos"]) - np.array(c["receivers"][r])) / c["c"]
            wp, wj = windows(hp[:6], t0), windows(hj[:6], t0)
            print(f"  {r:6s} " + " | ".join(" ".join(f"{x:+5.1f}" for x in (j_ - p_)) for p_, j_ in zip(wp, wj)))


if __name__ == "__main__":
    main()
