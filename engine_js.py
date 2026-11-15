"""
The browser engine (engine_geom.js) from Python, through Node.

energy_hists(cfg, src, recs) returns what brir_proto.energy_hists returns (energy histograms per receiver and octave
band, 1 ms bins), but computed as the PAGE computes a path: image sources in the first 250 ms (GEOM.ism, with the
ray-guided paths of order 2 - 3 in 3-D halls), edge diffraction and the seat dip when the config switches them on
(GEOM.withDiffraction), ray tracing (GEOM.rays) and GEOM.pathHist (image energy plus the ray energy the images do not
explain; a directional source weights the images by its pattern and the early ray energy per launch sector).
validation/check_engine_js.py compares the result with the page itself.

Why: the page is the reference engine of the project; pyroomacoustics (brir_proto.energy_hists) scatters differently
in drawn halls and is 16 - 80 times slower (validation/timing.md, validation/detmold_js.md).

Sources: omnidirectional, the generic coverage pattern, or measured directivity ("directivity": polar CSV, SOFA or
inline balloon; validation/check_engine_js_dir.py). Not covered yet (NotImplementedError): the seat dip in 3-D (OBJ)
halls. Needs `node` on the PATH.
"""
import json
import os
import subprocess
import zlib

import numpy as np

import brir_proto as bp

ROOT = os.path.dirname(os.path.abspath(__file__))
HB = bp.HIST_BIN                 # 1 ms, as the page (ENG.HB)
T_WIN = 0.25                     # image sources up to 250 ms after the direct sound (page: DISCRETE_MS)
SPEC = {"order": 3, "rays": 20000}   # ray-guided specular paths in 3-D halls (page: SPEC)
RAY_SECT = 64                    # launch sectors for directional sources (page: RAY_SECT)

JS = r"""const fs=require('fs');const GEOM=require('./engine_geom.js');const j=JSON.parse(fs.readFileSync(0,'utf8'));
const G=j.geom.mesh?GEOM.buildMesh(Object.assign({},j.geom.mesh,{obj:GEOM.loadObj(j.geom.mesh.text)}),j.geom.mesh.seed):GEOM.build(j.geom),E=j.diff?GEOM.edges(G):null,out={};
for(const [name,S] of Object.entries(j.srcs)){
  const m=Object.assign({},j,{recs:S.recs}),dm=S.dir?GEOM.dirModel(S.dir,j.bands):null;
  const I=GEOM.withDiffraction(G,E,S.pos,m,GEOM.ism(G,S.pos,S.recs,j.order,j.tWin,j.c,j.mats,j.air,j.bands,j.spec));
  const RT=GEOM.rays(G,S.pos,S.recs,Object.assign({n:j.rays,c:j.c,seed:S.seed,tMax:j.HN*j.HB,nSect:dm?j.nSect:0},j.mix==null?{}:{mix:j.mix}),j.mats,j.air);
  out[name]=S.recs.map((r,k)=>{const h=GEOM.pathHist(I[k],{H:RT.H[k],HS:RT.HS?RT.HS[k]:null,sect:RT.sect,nSb:RT.nSb},dm,j.HN,j.HB);
    return {hist:h.hist.map((a)=>Array.from(a)),resid:j.resid?h.resid.map((a)=>Array.from(a)):null};});
  out[name].escaped=RT.escaped;
}
console.log(JSON.stringify(out));"""


def page_params(cfg, n_rays=None, t_max=2.5, mix=None):
    """The page's worker message for this config (geometry, materials, engine switches)."""
    g = cfg["geometry"]
    room = bp.make_room(cfg, 0)
    air = np.round(np.asarray(room.air_absorption, float), 6).tolist()      # 6 decimals, as the page's data
    nb = len(air)
    mats = {}
    for k, v in g["materials"].items():
        al = (list(v["alpha"]) + [v["alpha"][-1]] * nb)[:nb]
        s = v.get("s", 0.0)
        mats[k] = {"R": [float(np.sqrt(max(1e-6, 1 - a))) for a in al], "s": list(s) if isinstance(s, (list, tuple)) else float(s)}
    mesh = bp.is_mesh(cfg)
    if mesh:
        m = g["mesh"]
        seed = [float(x) for x in next(iter(cfg["sources"][s]["pos"] for s in bp.source_names(cfg)))]   # as brir_proto._geom
        geom = {"mesh": {**{k: v for k, v in m.items() if k not in ("obj", "obj_text")},
                         "text": m.get("obj_text") or open(m["obj"]).read(), "groups": m.get("groups", {}),
                         "default": m.get("default", "wall"), "axes": m.get("axes", "y-up"),
                         "voxel": float(m.get("voxel", 0.05)), "seed": seed}}
        order = 1 if int(m.get("page_ism_order", 0) or 0) == 1 else 2     # as the page (geometry.ism_order is the Python engine's)
    else:
        geom = {"plan": g["plan"], "floor": g["floor"], "ceil": g["ceiling"], "stageY": bp.stage_y(cfg)}
        order = int(bp.early_order(cfg))
    sd = g.get("seat_dip") or {}
    seat_on = bp.seat_dip_on(cfg)
    if seat_on and mesh:
        raise NotImplementedError("engine_js: seat dip in 3-D (OBJ) halls is not supported yet")
    return {"geom": geom, "mats": mats, "air": air, "c": float(cfg["c"]), "order": order,
            "rays": int(n_rays or g.get("rays", 50000)), "tWin": T_WIN, "spec": SPEC if mesh else None,
            "diff": (not mesh) and bool(bp.diffraction_on(cfg)), "diffRefl": int(g.get("diffraction_refl", 0) or 0),
            "diffOrder": int(g.get("diffraction_order", 0) or 0), "bands": [float(x) for x in room.octave_bands.centers],
            "seat": {k: v for k, v in sd.items() if k != "on"} if seat_on else None,
            "fs": int(cfg["fs"]), "HN": int(round(t_max / HB)), "HB": HB, "nSect": RAY_SECT, "mix": mix}


def source_dir(cfg, src, bands):
    """The page's directivity spec of a source (GEOM.dirModel): generic coverage pattern, or measured data as the
    table the page builds from the same file (polars on a 1 degree grid, or a full-sphere balloon on a 5 degree grid;
    read and resampled by brir_proto.dir_model, so both engines hold the same numbers)."""
    s = cfg["sources"][src]
    if s.get("directivity"):
        dm = bp.dir_model(cfg, src, np.asarray(bands, float))
        aim = s.get("aim") or {}
        if dm["kind"] == "balloon":
            table = {"balloon": np.asarray(dm["balloon"]["db"], float).tolist()}
        else:
            table = {"h": np.asarray(dm["tab"]["h"], float).tolist(), "v": np.asarray(dm["tab"]["v"], float).tolist()}
        table["diffuse"] = np.asarray(dm["diffuse"], float).tolist()
        return {"az": float(aim.get("az", 0.0)), "el": float(aim.get("el", 0.0)), "table": table}
    if s.get("coverage") and 0 < float(s["coverage"]) < 360:
        aim = s.get("aim") or {}
        return {"az": float(aim.get("az", 0.0)), "el": float(aim.get("el", 0.0)), "cov": float(s["coverage"])}
    return None


def run_job(job):
    """Low level: job = page_params(...) plus srcs = {name: {pos, recs, seed, dir}} and resid (bool)."""
    if job.get("seat") is not None:            # the page passes GEOM.seatParams(...); build it in Node from the same spec
        js = JS.replace("const G=", "j.seat=GEOM.seatParams(j.seat);const G=", 1)
    else:
        js = JS
    r = subprocess.run(["node", "--max-old-space-size=4096", "-e", js], input=json.dumps(job), capture_output=True,
                       text=True, cwd=ROOT)
    if r.returncode:
        raise RuntimeError("engine_js: node failed: " + r.stderr[-1500:])
    return json.loads(r.stdout.strip().splitlines()[-1])


def hists(cfg, paths, n_rays=None, seed=None, t_max=2.5, return_resid=False, mix=None):
    """paths = {source: [receiver names]}: one Node process for all sources (the hall is built once).
    Returns ({(source, receiver): hist [bands, bins]}, band centres[, {(source, receiver): resid}])."""
    job = page_params(cfg, n_rays, t_max, mix)
    job["resid"] = bool(return_resid)
    job["srcs"] = {s: {"pos": [float(x) for x in cfg["sources"][s]["pos"]],
                       "recs": [[float(x) for x in cfg["receivers"][r]] for r in recs],
                       "seed": int(seed) if seed is not None else zlib.crc32(f"{s}|*".encode()) % 2 ** 31,
                       "dir": source_dir(cfg, s, job["bands"])} for s, recs in paths.items()}
    O = run_job(job)
    H = {(s, r): np.array(O[s][k]["hist"]) for s, recs in paths.items() for k, r in enumerate(recs)}
    cen = np.array(job["bands"])
    if return_resid:
        return H, cen, {(s, r): np.array(O[s][k]["resid"]) for s, recs in paths.items() for k, r in enumerate(recs)}
    return H, cen


def energy_hists(cfg, src, recs, t_max=2.5, n_rays=None, seed=None, return_resid=False, mix=None):
    """As brir_proto.energy_hists, computed with the browser engine: ({rec: hist}, band centres[, {rec: resid}])."""
    out = hists(cfg, {src: list(recs)}, n_rays, seed, t_max, return_resid, mix)
    H = {r: out[0][(src, r)] for r in recs}
    return (H, out[1], {r: out[2][(src, r)] for r in recs}) if return_resid else (H, out[1])
