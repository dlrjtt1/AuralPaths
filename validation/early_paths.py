"""
Which surfaces carry the early energy at the BRAS binaural listener (diagnostic for the BRAS binaural check).

    python validation/early_paths.py <BRAS folder> CR4 [--sources LS3,LS4,LS5,LS6,LS7] [--rays 100000]
                                     [--k8-mps QSCK8_1x1_64442_MPS_front_pole.csv] [--voxel 0.15] [--out ...]   (needs node)

Uses the browser engine (engine_geom.js: voxel room from the BRAS OBJ, image sources to order 2, ray tracing with the
arrival log of rays(), opts.log) with the BRAS fitted materials, positions and aim as check_bras_brir.py; with
--k8-mps each ray and image is weighted by the measured K8 pattern at its launch direction. Per source and time window
after the direct sound (0-3, 3-20, 20-50, 50-80 ms) it reports:
  - the energy share of the 0-80 ms window (ray histogram plus the image sources not seen by the rays, as on the page),
    compared with the measured BRIR (both ears, broadband 250 Hz - 2 kHz octaves);
  - the ray energy by surface of the LAST reflection before the listener and by number of reflections;
  - the image sources (order 1 and 2) in the window, by surface sequence.
Energy is the sum of the 250 Hz - 2 kHz octaves; materials are the BRAS tags. Data: BRAS (Aspoeck et al. 2020,
https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0).
"""
import argparse
import json
import os
import subprocess
import sys
import time
from collections import defaultdict

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, ".."), HERE]
import brir_proto as bp                    # noqa: E402
import check_bras_brir as cb               # noqa: E402
import validate_bras_cr as vb              # noqa: E402

WINS = ((0, .003), (.003, .02), (.02, .05), (.05, .08))
JS = """const fs=require('fs');const GEOM=eval(fs.readFileSync('engine_geom.js','utf8')+';GEOM');const j=JSON.parse(fs.readFileSync(0,'utf8'));
const G=GEOM.buildMesh({obj:GEOM.loadObj(j.obj),groups:j.groups,voxel:j.voxel,axes:'y-up'},Object.values(j.srcs)[0]);
const out={faces:G.nFaces,h:G.h,mat:G.S.map(s=>s.mat),res:{}};
for(const [n,s] of Object.entries(j.srcs)){const I=GEOM.ism(G,s,[j.rec],2,0.12,j.c,j.mats,j.air,j.bands)[0];
const T=GEOM.rays(G,s,[j.rec],{n:j.n,c:j.c,tMax:2.5,bin:0.001,seed:7,log:j.log},j.mats,j.air);
out.res[n]={I:I.map(q=>({t:q.t,seq:q.seq,e:q.e,g:Array.from(q.g)})),H:T.H[0].map(b=>Array.from(b)),LOG:T.LOG,lost:T.escaped+T.leaked};}
console.log(JSON.stringify(out));"""


def short(m):
    return m.replace("mat_CR3_", "").replace("mat_CR4_", "")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras"); ap.add_argument("hall", choices=list(cb.SCENES))
    ap.add_argument("--sources", default="LS3,LS4,LS5,LS6,LS7"); ap.add_argument("--rays", type=int, default=100000)
    ap.add_argument("--k8-mps", default=None); ap.add_argument("--voxel", type=float, default=0.15)
    ap.add_argument("--set", default="", help='sensitivity: "tag:s=0.5,tag:a=0.3" sets scattering / absorption '
                    '(all octaves) of a material tag (without the mat_<hall>_ prefix)')
    ap.add_argument("--summary", action="store_true", help="only the energy-share table per source")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(HERE, f"bras_early_paths_{a.hall}.md")
    up, c, fs = a.bras, 343.5, 44100
    scene = os.path.join(up, cb.SCENES[a.hall])
    mats = vb.read_bras_materials(os.path.join(up, "3 Surface descriptions"), a.hall, "fitted")
    changed = []
    for kv in filter(None, a.set.split(",")):
        tag, rest = kv.split(":"); key, val = rest.split("="); m = mats[f"mat_{a.hall}_{tag.strip()}"]
        if key.strip() == "s":
            m["s_oct"] = [float(val)] * 6
        else:
            m["alpha"] = [float(val)] * 6
        changed.append(kv.strip())
    obj = cb.rotate_obj(open(os.path.join(scene, "Geometry", f"{a.hall}.obj"), encoding="utf-8", errors="ignore").read())
    P = cb.POS[a.hall]; L = cb.rot(P["L"]); srcs = a.sources.split(",")
    import pyroomacoustics as pra
    room = pra.ShoeBox([5, 5, 5], fs=fs, air_absorption=True)
    cen = [float(x) for x in room.octave_bands.centers]; air = [float(x) for x in room.air_absorption]
    bsel = [i for i, f in enumerate(cen) if 200 < f < 2500]
    mj = {k: {"R": [float(np.sqrt(1 - v["alpha"][min(i, 5)])) for i in range(len(cen))], "s": [float(x) for x in v["s_oct"][:6]]}
          for k, v in mats.items()}
    pos = {s: cb.rot(P["LS"][int(s[2:])]) for s in srcs}
    tdir = {s: np.linalg.norm(np.subtract(pos[s], L)) / c for s in srcs}
    job = dict(obj=obj, groups={k: k for k in mats}, voxel=a.voxel, srcs=pos, rec=L, c=c, mats=mj, bands=cen, air=air,
               n=a.rays, log=max(tdir.values()) + 0.085)
    t0 = time.time()
    r = subprocess.run(["node", "--max-old-space-size=6000", "-e", JS], input=json.dumps(job), capture_output=True, text=True,
                       cwd=os.path.join(HERE, ".."))
    if r.returncode:
        sys.exit(r.stderr[-3000:])
    o = json.loads(r.stdout); smat = o["mat"]
    bal = cb.k8_balloon(a.k8_mps, cen) if a.k8_mps else None
    md = [f"# BRAS {a.hall}: early energy by surface at the binaural listener (browser engine)", "",
          f"`validation/early_paths.py`: voxel {o['h']:.2f} m, {o['faces']} faces, {a.rays} rays per source, image sources "
          f"to order 2; sources {'with the measured K8 pattern (BRAS), LS3 - LS6 aimed at the head, LS7 horizontal' if bal else 'omnidirectional'}. "
          "Energy: sum of the 250 Hz - 2 kHz octaves. Windows in ms after the direct sound. Materials: BRAS fitted estimates "
          f"(tags without the `mat_{a.hall}_` prefix)" + (f"; changed for this run: {', '.join(changed)}" if changed else "") +
          f". Run time {time.time() - t0:.0f} s.", ""]
    for s in srcs:
        res = o["res"][s]
        aim = cb.aim_at(pos[s], L)
        if s == "LS7":
            aim["el"] = 0.0
        cfg1 = {"sources": {s: dict({"pos": pos[s], "aim": aim}, **({"directivity": bal} if bal else {}))}}
        dm = bp.dir_model(cfg1, s, cen) if bal else None
        g_dir = (lambda E: bp.dir_amp(dm, np.asarray(E, float).T).T ** 2) if dm else (lambda E: np.ones((len(E), len(cen))))
        Lg = np.array(res["LOG"]) if res["LOG"] else np.zeros((0, 11 + len(cen)))
        Le = Lg[:, 11:] * g_dir(Lg[:, 8:11]) if len(Lg) else Lg[:, 11:]
        I = res["I"]; Ie = np.array([q["g"] for q in I]) ** 2 * g_dir([q["e"] for q in I])
        It = np.array([q["t"] for q in I]); Hr = np.array(res["H"]) * (dm["diffuse"][:, None] if dm else 1)
        Hi = np.zeros_like(Hr)
        for q, e in zip(I, Ie):
            i = int(q["t"] / 0.001)
            if i < Hi.shape[1]:
                Hi[:, i] += e
        hist = Hi + np.maximum(0, bp._smooth(Hr) - bp._smooth(Hi))
        td = tdir[s]; i0 = int(np.floor((td - 0.0005) / 0.001))
        wE = [hist[bsel, i0 + int(round(x0 * 1000)):i0 + int(round(x1 * 1000))].sum() for x0, x1 in WINS]
        mx, _ = sf.read(os.path.join(scene, "BRIRs", "wav", f"{a.hall}_BRIR_{s}_MP6_HATO0.wav")); mx = mx.T
        mb = sum(bp.band_filter(mx, fs, cen[i]) ** 2 for i in bsel).sum(axis=0) if hasattr(bp, "band_filter") else (mx ** 2).sum(axis=0)
        n0 = int((bp.onset_time(mx, fs) - 0.0005) * fs)
        mE = [mb[n0 + int(x0 * fs):n0 + int(x1 * fs)].sum() for x0, x1 in WINS]
        md += [f"## {s}", "", "| window (ms) | " + " | ".join(f"{x0 * 1000:.0f}–{x1 * 1000:.0f}" for x0, x1 in WINS) + " |",
               "|---|" + "---|" * len(WINS),
               "| share of 0–80 ms, measured (%) | " + " | ".join(f"{100 * e / sum(mE):.0f}" for e in mE) + " |",
               "| share of 0–80 ms, browser engine (%) | " + " | ".join(f"{100 * e / sum(wE):.0f}" for e in wE) + " |", ""]
        if a.summary:
            continue
        tt = Lg[:, 1] - td if len(Lg) else np.zeros(0)
        Eb = Le[:, bsel].sum(axis=1) if len(Lg) else np.zeros(0)
        for x0, x1 in WINS[1:]:
            m = (tt >= x0) & (tt < x1); tot = Eb[m].sum()
            if tot <= 0:
                continue
            by_last, by_n, by_pair = defaultdict(float), defaultdict(float), defaultdict(float)
            pts = defaultdict(list)
            for row, e in zip(Lg[m], Eb[m]):
                lastm = short(smat[int(row[4])]) if row[4] >= 0 else "(direct)"
                by_last[lastm] += e; by_n[min(int(row[2]), 6)] += e
                by_pair[(short(smat[int(row[3])]) if row[3] >= 0 else "-", lastm)] += e
                pts[lastm].append((row[5:8], e))
            md.append(f"**{x0 * 1000:.0f}–{x1 * 1000:.0f} ms, rays** ({int(m.sum())} arrivals; share of the ray energy)")
            md.append("")
            md.append("| last surface | share | energy-weighted mean of the last reflection point (x, y, z m; listener at "
                      f"{L[0]:.1f}, {L[1]:.1f}, {L[2]:.1f}) |")
            md.append("|---|---|---|")
            for k, v in sorted(by_last.items(), key=lambda kv: -kv[1])[:5]:
                pp = np.array([p for p, _ in pts[k]]); ww = np.array([w for _, w in pts[k]])
                mu = (pp * ww[:, None]).sum(axis=0) / ww.sum()
                md.append(f"| {k} | {100 * v / tot:.0f} % | {mu[0]:.1f}, {mu[1]:.1f}, {mu[2]:.1f} |")
            md.append("")
            md.append("reflections: " + ", ".join(f"{k}{'+' if k == 6 else ''}: {100 * v / tot:.0f} %" for k, v in sorted(by_n.items()))
                      + "; first → last surface: " + ", ".join(f"{p} → {q} {100 * v / tot:.0f} %" for (p, q), v in
                                                               sorted(by_pair.items(), key=lambda kv: -kv[1])[:4]))
            md.append("")
            mi = (It - td >= x0) & (It - td < x1)
            if mi.any():
                ie = Ie[mi][:, bsel].sum(axis=1); idx = np.argsort(-ie)[:5]
                md.append(f"image sources in the window: {int(mi.sum())}, energy {100 * ie.sum() / tot:.0f} % of the ray energy; strongest: " +
                          "; ".join(f"{' → '.join(short(smat[w]) for w in I[np.where(mi)[0][k]]['seq'])} at "
                                    f"{1000 * (It[mi][k] - td):.1f} ms ({100 * ie[k] / tot:.0f} %)" for k in idx))
                md.append("")
    open(out, "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
