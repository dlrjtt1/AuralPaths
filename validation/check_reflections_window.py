"""
Timing-tolerant check of first-order reflections of the browser engine on a BRAS OBJ hall, per surface material.

    python validation/check_reflections_window.py <BRAS folder> CR4 [--voxel 0.08] [--md out.md]   (needs node)

Why: check_reflections_js.py compares each predicted reflection with the measured energy in a 1 ms window at its
predicted time. If the real reflection arrives 1 ms earlier, or is smeared over a few ms by surface structure that the
model leaves out, that test reports a level error although the reflected energy is there. This script adds, for the
same isolated reflections (first order, >= -15 dB re direct, >= 2 ms after it, 1.5 ms away from any other predicted
first-order one), 500 Hz - 2 kHz, dB re the direct sound:

  point   measured energy in the 1 ms window at the predicted time (-0.2 ... +0.8 ms), as check_reflections_js.py
  wide    measured energy in -1.5 ... +2.5 ms around the predicted time, minus the median energy of the same 4 ms window
          at random times 5 - 45 ms (the diffuse background); "n/a" when nothing is left above the background
  offset  time of the strongest 1 ms window within +-1.5 ms of the predicted time, re the predicted time (ms;
          negative = measured earlier). Only for timing: a maximum over 13 windows is biased upwards, so it is not
          used as a level (the random-time control printed below shows how large that bias is).

pred - point and pred - wide are summarised per material (median, n), with the median and spread of the offsets.
A large pred - point with pred - wide near 0 and scattered offsets means the energy is there but spread in time;
a constant offset means a geometry or position mismatch; large values of both mean the level itself is wrong.
"""
import argparse
import collections
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import validate_bras_cr as vb  # noqa: E402

SCENES = {"CR3": "CR3 medium room (chamber music hall)", "CR4": "CR4 large room (auditorium)"}
JS = """const fs=require('fs');const GEOM=eval(fs.readFileSync('engine_geom.js','utf8')+';GEOM');const j=JSON.parse(fs.readFileSync(0,'utf8'));
const G=GEOM.buildMesh({obj:GEOM.loadObj(j.obj),groups:j.groups,voxel:j.voxel},Object.values(j.srcs)[0]);const out={};
for(const [name,s] of Object.entries(j.srcs)){const I=GEOM.ism(G,s,j.recs,1,0.05,j.c,j.mats,j.air,j.bands);
out[name]=I.map(L=>L.map(q=>{const w=q.seq[0];return [q.t,q.o,(q.g[2]**2+q.g[3]**2+q.g[4]**2)/3,w===undefined?null:G.S[w].mat];}));}
console.log(JSON.stringify(out));"""
WIDE = (0.0015, 0.0025)


def wide_energy(y, on, fs, t):
    """Energy in [t - 1.5 ms, t + 2.5 ms] after the direct sound, linear, re the 1 ms window on the direct sound."""
    a, b = int(0.0002 * fs), int(0.0008 * fs)
    k = on + int(round(t * fs))
    return y[k - int(WIDE[0] * fs): k + int(WIDE[1] * fs)].sum() / y[on - a: on + b].sum()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras"); ap.add_argument("hall", choices=list(SCENES))
    ap.add_argument("--voxel", type=float, default=None); ap.add_argument("--md", default=None)
    a = ap.parse_args()
    voxel = a.voxel or (0.05 if a.hall == "CR3" else 0.08)
    scene = os.path.join(a.bras, SCENES[a.hall])
    mats = vb.read_bras_materials(os.path.join(a.bras, "3 Surface descriptions"), a.hall, "fitted")
    ir, fs, E, R, eid, rid, _ = vb.read_rirs(scene)
    cen = [125, 250, 500, 1000, 2000, 4000, 8000, 16000]
    mj = {k: {"R": [float(np.sqrt(1 - v["alpha"][min(i, len(v["alpha"]) - 1)])) for i in range(len(cen))], "s": v["s_oct"]} for k, v in mats.items()}
    srcs = {f"LS{e}": list(map(float, E[i])) for i, e in enumerate(eid)}; recs = [list(map(float, R[i])) for i in range(len(rid))]
    job = dict(obj=open(os.path.join(scene, "Geometry", a.hall + ".obj")).read(), groups={k: k for k in mats}, voxel=voxel,
               srcs=srcs, recs=recs, c=343.5, mats=mj, bands=cen, air=[0.0] * len(cen))
    r = subprocess.run(["node", "--max-old-space-size=6000", "-e", JS], input=json.dumps(job), capture_output=True, text=True, cwd=os.path.join(HERE, ".."))
    if r.returncode:
        sys.exit(r.stderr[-3000:])
    o = json.loads(r.stdout)
    rows, rnd = [], []
    steps = np.arange(-0.0015, 0.00151, 0.00025)
    for si, sn in enumerate(srcs):
        for k in range(len(recs)):
            L = o[sn][k]; direct = [q for q in L if q[1] == 0]
            if not direct:
                continue
            t0, e0 = direct[0][0], direct[0][2]
            pred = [(q[0] - t0, 10 * np.log10(q[2] / e0 + 1e-30), q[3]) for q in L if q[1] == 1]
            y, on = vb.band_energy(ir[k, si] if ir.ndim == 3 else ir[si * len(recs) + k], fs)
            rng = np.random.default_rng(si * 100 + k)
            for tr in rng.uniform(0.005, 0.045, 10):
                rnd.append((vb.window_level(y, on, fs, tr), wide_energy(y, on, fs, tr), max(vb.window_level(y, on, fs, tr + d) for d in steps)))
            for t, l, mat in pred:
                if t < 0.002 or l < -15 or any(abs(t - t2) <= 0.0015 for t2, _, _ in pred if t2 != t):
                    continue
                lv, dt = max((vb.window_level(y, on, fs, t + d), d) for d in steps)
                rows.append(dict(pair=f"{sn}-MP{rid[k]}", t=1000 * t, pred=l, point=vb.window_level(y, on, fs, t), wide=wide_energy(y, on, fs, t),
                                 dt=1000 * dt, mat=(mat or "?").replace(f"mat_{a.hall}_", "")))
    R_ = np.asarray(rnd); bg = float(np.median(R_[:, 1]))
    for x in rows:
        ex = x["wide"] - bg
        x["wide_db"] = 10 * np.log10(ex) if ex > 0 else None
    out = [f"# {a.hall}: first-order reflections, timing-tolerant check (browser engine, BRAS fitted materials)", "",
           f"Isolated first-order reflections: {len(rows)}. 500 Hz - 2 kHz, dB re direct sound. "
           f"Background (4 ms window, random times 5 - 45 ms): {10 * np.log10(bg):.1f} dB. "
           f"Random-time control: 1 ms window median {np.median(R_[:, 0]):.1f} dB, max within +-1.5 ms median {np.median(R_[:, 2]):.1f} dB "
           f"(bias of the max search {np.median(R_[:, 2]) - np.median(R_[:, 0]):+.1f} dB, so the max is used for timing only).", "",
           "| material | n | pred - point (median) | pred - wide (median) | wide n/a | offset median (ms) | offset IQR (ms) |",
           "|---|---|---|---|---|---|---|"]
    g = collections.defaultdict(list)
    for x in rows:
        g[x["mat"]].append(x)
    for m in sorted(g, key=lambda m: -len(g[m])):
        X = g[m]; dp = [x["pred"] - x["point"] for x in X]; dw = [x["pred"] - x["wide_db"] for x in X if x["wide_db"] is not None]
        dts = [x["dt"] for x in X]
        out.append(f"| {m} | {len(X)} | {np.median(dp):+.1f} | {np.median(dw) if dw else float('nan'):+.1f} | {len(X) - len(dw)} | "
                   f"{np.median(dts):+.2f} | {np.percentile(dts, 25):+.2f} ... {np.percentile(dts, 75):+.2f} |")
    dp = [x["pred"] - x["point"] for x in rows]; dw = [x["pred"] - x["wide_db"] for x in rows if x["wide_db"] is not None]
    out += [f"| all | {len(rows)} | {np.median(dp):+.1f} | {np.median(dw):+.1f} | {len(rows) - len(dw)} | | |", "",
            "## Reflections", "", "| pair | t (ms) | material | pred | point | wide | offset (ms) |", "|---|---|---|---|---|---|---|"]
    for x in sorted(rows, key=lambda x: (x["mat"], x["t"])):
        w = f"{x['wide_db']:.1f}" if x["wide_db"] is not None else "n/a"
        out.append(f"| {x['pair']} | {x['t']:.1f} | {x['mat']} | {x['pred']:.1f} | {x['point']:.1f} | {w} | {x['dt']:+.2f} |")
    txt = "\n".join(out) + "\n"
    print(txt)
    if a.md:
        open(a.md, "w").write(txt)


if __name__ == "__main__":
    main()
