"""
Room-criteria check of the browser engine (engine_geom.js, the engine of the page) against the Fratoni dataset halls
(Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1, CC BY 4.0), for the halls that the 2.5D conversion cannot
represent: TCB (historic opera house with five tiers of boxes) and DUS (opera house with two balconies).

    python validation/check_fratoni_js.py <dataset folder> TCB --obj TCB.obj [--rays 20000] [--order 2] [--out ...]
                                         [--swap "Floor_(boxes)=Wood,PVC=Velvet drapes"]       (needs node)

Same inputs and comparison as validate_fratoni.py (materials: the dataset's GA absorption / scattering unchanged;
measured: the Room_Criteria sheet, mean over the receivers listed per source and zone; JND units of ISO 3382-1 Annex
A), but run with the browser mesh path (voxel room, image sources to --order, ray tracing with BVH), which is what
the page computes for a 3D model. Positions and the tag-to-material assignments are in validate_fratoni.py (VENUES);
--swap reassigns tags for a sensitivity run. The early part is the image-source histogram plus the ray-traced
remainder, as on the page.
"""
import argparse
import csv
import glob
import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import brir_proto as bp                                                    # noqa: E402
import validate_fratoni as vf                                              # noqa: E402

JS = """const fs=require('fs');const GEOM=eval(fs.readFileSync('engine_geom.js','utf8')+';GEOM');const j=JSON.parse(fs.readFileSync(0,'utf8'));
let t=Date.now();const G=GEOM.buildMesh({obj:GEOM.loadObj(j.obj),groups:j.groups,voxel:j.voxel},Object.values(j.srcs)[0]);
const out={info:{volume:G.V,area:G.areaByMat,dropped:G.nDropped,faces:G.nFaces,h:G.h,build_s:(Date.now()-t)/1000,
  outside:Object.entries(Object.assign({},j.srcs,j.recs)).filter(([k,p])=>!GEOM.inside(G,p)).map(([k])=>k)},res:{}};
const R=Object.values(j.recs);
for(const [name,s] of Object.entries(j.srcs)){t=Date.now();const I=GEOM.ism(G,s,R,j.order,j.order>1?0.16:10,j.c,j.mats,j.air,j.bands);
const T=GEOM.rays(G,s,R,{n:j.n,c:j.c,tMax:3.0,bin:j.bin,seed:7},j.mats,j.air);
out.res[name]={lost:T.escaped+T.leaked,secs:(Date.now()-t)/1000,H:T.H.map(h=>h.map(b=>Array.from(b))),I:I.map(L=>L.map(q=>[q.t,Array.from(q.g).map(v=>v*v)]))};}
console.log(JSON.stringify(out));"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dataset"); ap.add_argument("hall", choices=["TCB", "DUS"])
    ap.add_argument("--obj", required=True); ap.add_argument("--rays", type=int, default=20000)
    ap.add_argument("--order", type=int, default=2); ap.add_argument("--voxel", type=float, default=None)
    ap.add_argument("--swap", default="", help="tag=material,... reassignments for a sensitivity run")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    V = vf.VENUES[a.hall]
    out = a.out or os.path.join(HERE, f"fratoni_{a.hall}")
    base = os.path.join(a.dataset, V["folder"])
    mats = vf.read_boundary(glob.glob(os.path.join(base, "Boundary conditions", "*.xlsx"))[0])
    blocks = vf.read_criteria(glob.glob(os.path.join(base, "Measurements results", "*.xlsx"))[0])
    groups = dict(V["groups"])
    for kv in filter(None, a.swap.split(",")):
        k, v = kv.split("="); groups[k.strip()] = v.strip()
    srcs = sorted({b["source"] for b in blocks})
    recs = sorted({r for b in blocks for r in b["receivers"]}, key=lambda r: int(r[1:]))
    import pyroomacoustics as pra
    room = pra.ShoeBox([5, 5, 5], fs=48000, air_absorption=True)            # band centres and air absorption, as the page
    cen = [float(x) for x in room.octave_bands.centers]; air = [float(x) for x in room.air_absorption]
    mj = {k: {"R": [float(np.sqrt(1 - m["alpha"][min(i, len(m["alpha"]) - 1)])) for i in range(len(cen))], "s": m["s"]}
          for k, m in mats.items()}
    c = 343.0
    job = dict(obj=open(a.obj, encoding="utf-8", errors="ignore").read(), groups=groups, voxel=a.voxel or V["voxel"],
               srcs={s: list(V["sources"][s]) for s in srcs}, recs={r: list(V["receivers"][r]) for r in recs},
               order=a.order, c=c, mats=mj, bands=cen, air=air, n=a.rays, bin=bp.HIST_BIN)
    t0 = time.time()
    r = subprocess.run(["node", "--max-old-space-size=5500", "-e", JS], input=json.dumps(job), capture_output=True, text=True,
                       cwd=os.path.join(HERE, ".."))
    if r.returncode:
        sys.exit(r.stderr[-3000:])
    o = json.loads(r.stdout)
    info = o["info"]
    if info["outside"]:
        sys.exit(f"positions outside the room model: {info['outside']}")
    bi = [cen.index(min(cen, key=lambda x: abs(x - b))) for b in vf.BANDS]
    per = {}
    for s in srcs:
        so = o["res"][s]
        for k, rn in enumerate(recs):
            Hr = np.array(so["H"][k]); Hi = np.zeros_like(Hr)
            for t, e in so["I"][k]:
                if int(t / bp.HIST_BIN) < Hr.shape[1]:
                    Hi[:, int(t / bp.HIST_BIN)] += e
            H = Hi + np.maximum(0, bp._smooth(Hr) - bp._smooth(Hi))
            per[(s, rn)] = vf.criteria(H[bi], np.linalg.norm(np.subtract(V["receivers"][rn], V["sources"][s])) / c)
    area, A = info["area"], {}
    for i, b in enumerate(vf.BANDS):
        A[b] = sum(mats[k]["alpha"][i] * v for k, v in area.items())
    lines = [f"{a.hall}: OBJ {info['faces']} faces ({info['dropped']} hidden faces dropped), voxel {info['h']:.3f} m, room volume "
             f"(voxels) {info['volume']:.0f} m3; model built in {info['build_s']:.0f} s",
             "surface areas (m2): " + ", ".join(f"{k} {v:.0f}" for k, v in sorted(area.items())) + f"; total {sum(area.values()):.0f}",
             "Sabine T (s), no air: " + ", ".join(f"{b} Hz {0.161 * info['volume'] / A[b]:.2f}" for b in vf.BANDS),
             "tags -> materials: " + ", ".join(f"{k} -> {v}" for k, v in groups.items()),
             f"browser engine: image sources to order {a.order}, {a.rays} rays per source; " +
             ", ".join(f"{s} {o['res'][s]['secs']:.0f} s ({o['res'][s]['lost']} rays lost)" for s in srcs) +
             f"; total {time.time() - t0:.0f} s"]
    md = [f"# Fratoni {a.hall}: measured vs AuralPaths (browser engine)", "",
          "Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, "
          "Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria sheet "
          "(mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged. Positions and "
          "tag-to-material assignments: validate_fratoni.py (VENUES); heights are assumptions (see there).", "",
          "```", *lines, "```", ""]
    rows, res, plot_blocks, summ = [], {}, [], []
    for blk in blocks:
        s, rl = blk["source"], blk["receivers"]
        zone = blk.get("receivers_text", "").split("(")[0].strip().title() or "all"
        label = f"{s} {zone}"
        mean = {k: np.nanmean([per[(s, rn)][k] for rn in rl], axis=0) for k in per[(s, rl[0])]}
        res[label] = mean
        plot_blocks.append({"source": label, "metrics": {k.replace(" ", ""): v for k, v in blk["metrics"].items()}})
        md += [f"## {s}, {blk.get('receivers_text', '').strip()} ({len(rl)})", "",
               "| criterion | model | " + " | ".join(f"{b} Hz" for b in vf.BANDS) + " | mean abs (JND) 500-1k | mean abs (JND) all |",
               "|---|---|" + "---|" * len(vf.BANDS) + "---|---|"]
        for name, meas in blk["metrics"].items():
            key = name.replace(" ", "")
            if key not in vf.JND:
                continue
            sim = mean[key]; j = vf.jnd_units(key, sim, np.asarray(meas))
            fmt = (lambda v: f"{v:.0f}") if key == "Ts" else (lambda v: f"{v:.2f}")
            md.append(f"| {name} | measured | " + " | ".join(fmt(v) for v in meas) + " | | |")
            md.append("| | browser 3D | " + " | ".join(f"{fmt(v)} ({d:+.1f})" for v, d in zip(sim, j)) +
                      f" | {np.nanmean(np.abs(j[2:4])):.1f} | {np.nanmean(np.abs(j)):.1f} |")
            summ.append((key, label, j))
            for b, mv, sv, dj in zip(vf.BANDS, meas, sim, j):
                rows.append(dict(hall=a.hall, source=s, zone=zone, criterion=key, band_hz=b, model="browser 3D", measured=round(mv, 3),
                                 simulated=round(float(sv), 3), diff_jnd=round(float(dj), 2)))
        md.append("")
    md += ["Values in brackets: simulated - measured in JND (ISO 3382-1 Annex A: EDT / T30 5 %, C80 / C50 1 dB, Ts 10 ms).", "",
           "## Summary: mean absolute difference in JND, 500 Hz - 1 kHz (all bands in brackets), over sources and zones", ""]
    for key in ("EDT", "T30", "C80", "C50", "Ts"):
        js = [j for k, _, j in summ if k == key]
        if js:
            md.append(f"- {key}: {np.nanmean([np.nanmean(np.abs(j[2:4])) for j in js]):.1f} "
                      f"({np.nanmean([np.nanmean(np.abs(j)) for j in js]):.1f}); signed 500 Hz - 1 kHz {np.nanmean([np.nanmean(j[2:4]) for j in js]):+.1f}")
    md.append("")
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    with open(out + ".csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with open(out + "_receivers.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["source", "receiver"] + [f"{k}_{b}" for k in ("EDT", "T30", "C80", "C50", "Ts") for b in vf.BANDS])
        for (s, rn), m in per.items():
            w.writerow([s, rn] + [round(float(m[k][i]), 3) for k in ("EDT", "T30", "C80", "C50", "Ts") for i in range(len(vf.BANDS))])
    vf.plot(plot_blocks, {b["source"]: [] for b in plot_blocks}, res, None, a.hall, out + ".png", label3="browser 3D", engine="browser engine")
    print("\n".join(lines)); print("->", out + ".md")


if __name__ == "__main__":
    main()
