"""
Detmold Konzerthaus with the BROWSER engine: which scattering model of a drawn hall is closer to the measurement?
(diagnostic, 2026-11-15; conditions fixed before the run)

The drawn Detmold hall of validation/detmold_kh.py (start materials, not calibrated) is computed with engine_geom.js
in Node as the page does it: image sources in the first 250 ms (GEOM.ism), ray tracing (GEOM.rays), the energy
histogram of a path as the page's geomHist (image energy plus the ray energy the images do not explain; directional
source: images weighted by the pattern, early ray energy per launch sector, later 1 / Q). Two scattering models:

    either   a reflection is specular or Lambert with probability s            (the page's drawn halls)
    mix      every reflection goes in the direction s * Lambert + (1 - s) * specular (opts.mix; the page's mesh
             halls and pyroomacoustics)

For each model: absorption calibrated on the measured T30 of the 24 omnidirectional-microphone positions (S2, S3 to
12 seats; t30.csv of detmold_kh.py setup) as calibrate.py does it (omnidirectional source, one factor per octave
band 125 Hz - 4 kHz on all materials, k <- k * T_sim / T_meas, positions combined by the median, within 2 %, at
most 6 iterations). Then T30, EDT and C80 at the same 24 positions with the source as in the hall check (generic
90 degree loudspeaker aimed as in the config) against the measured values (EDT and T30 from t30.csv, C80 from the
omnidirectional IRs with the same functions). --python: the same evaluation with the Python engine and a calibrated
config (calibrate.py output).

    python validation/detmold_js.py <config.json> <t30.csv> <DetmoldSRIR_v01 folder> [--rays 80000]
        [--python <config_cal.json>] [--out out/detmold_js]
"""
import argparse
import copy
import csv
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path[:0] = [ROOT, HERE]
import brir_proto as bp                       # noqa: E402
from validate_fratoni import criteria         # noqa: E402

BANDS = [125, 250, 500, 1000, 2000, 4000]
JND = {"T30": 5.0, "EDT": 5.0, "C80": 1.0}

# geomHist and smooth10 of viewer_template.html, with ENG.HN / ENG.HB = 2500 / 1 ms
JS = r"""const fs=require('fs');const GEOM=eval(fs.readFileSync('engine_geom.js','utf8')+';GEOM');const j=JSON.parse(fs.readFileSync(0,'utf8'));
const HN=2500,HB=0.001,nb=j.air.length;
const smooth10=(a)=>{const n=a.length,o=new Float64Array(n);let s=0;for(let i=0;i<n+5;i++){if(i<n)s+=a[i];if(i-10>=0)s-=a[i-10];const k=i-5;if(k>=0&&k<n)o[k]=s/10;}return o;};
const G=GEOM.build(j.drawn),out={};
for(const [name,S] of Object.entries(j.srcs)){
  const dm=S.dir?GEOM.dirModel(S.dir,j.bands):null;
  const I=GEOM.ism(G,S.pos,S.recs,j.order,0.25,j.c,j.mats,j.air,j.bands,null);
  const RT=GEOM.rays(G,S.pos,S.recs,{n:j.n,c:j.c,seed:S.seed,nSect:dm?64:0,mix:j.mix},j.mats,j.air);
  out[name]=S.recs.map((r,k)=>{
    const list=I[k].map((q)=>{if(!dm)return q;const a=dm.amp(q.e||[0,-1,0]);return {...q,g:Array.from(q.g,(v,b)=>v*a[b])};});
    const Hi=Array.from({length:nb},()=>new Float64Array(HN));
    for(const q of list){const bin=Math.floor(q.t/HB);if(bin<HN)for(let b=0;b<nb;b++)Hi[b][bin]+=q.g[b]*q.g[b];}
    const A2=dm&&RT.HS?RT.sect.map((d)=>dm.amp(d).map((a)=>a*a)):null,HS=RT.HS?RT.HS[k]:null,hist=[];
    for(let b=0;b<nb;b++){
      const f=dm?dm.diffuse[b]:1,h=Array.from(RT.H[k][b],(v)=>v*f);
      if(A2){const nS=RT.nSb,NBr=HS.length/(A2.length*nS);for(let i=0;i<Math.min(nS,h.length);i++){let v=0;for(let q=0;q<A2.length;q++)v+=HS[(q*NBr+b)*nS+i]*A2[q][b];h[i]=v;}}
      const sr=smooth10(h),si=smooth10(Hi[b]),hh=new Array(HN);
      for(let i=0;i<HN;i++)hh[i]=Hi[b][i]+Math.max(0,sr[i]-si[i]);
      hist.push(hh);}
    return hist;});
}
console.log(JSON.stringify(out));"""


def positions(path):
    pos = {}
    for r in csv.DictReader(open(path)):
        p = pos.setdefault(r["label"], {"src": [float(r[k]) for k in ("src_x", "src_y", "src_z")],
                                        "rec": [float(r[k]) for k in ("rec_x", "rec_y", "rec_z")], "T30": {}, "EDT": {}})
        p["T30"][int(float(r["band_hz"]))] = float(r["T30_s"]); p["EDT"][int(float(r["band_hz"]))] = float(r["EDT_s"])
    return pos


def measured_c80(pos, folder):
    import soundfile as sf
    import validate_bras_cr as vb
    for lab, p in pos.items():
        s, r = lab.split("_")
        x, fs = sf.read(os.path.join(folder, "SetC_DenseKH_LSOrchestra", "Data", "Omni", f"{s}{r}.wav"))
        x = x if x.ndim == 1 else x[:, 0]
        on = int(np.argmax(np.abs(x) > 0.1 * np.abs(x).max())) / fs       # as detmold_kh.py setup
        c_ = criteria(vb.measured_hist(x, fs), on)
        p["C80"] = dict(zip(BANDS, c_["C80"]))


def js_hists(cfg, pos, mats_alpha, rays, mix, directional):
    g = cfg["geometry"]
    room = bp.make_room(cfg, 0)
    air = np.asarray(room.air_absorption, float).tolist(); nb = len(air)
    mats = {k: {"R": [float(np.sqrt(1 - x)) for x in (list(al) + [al[-1]] * nb)[:nb]],
                "s": float(np.mean(g["materials"][k].get("s", 0.0)))} for k, al in mats_alpha.items()}
    srcs = {}
    for i, s in enumerate(sorted({lab.split("_")[0] for lab in pos})):
        labs = [lab for lab in pos if lab.startswith(s + "_")]
        c = cfg["sources"][s]
        srcs[s] = {"pos": pos[labs[0]]["src"], "recs": [pos[lab]["rec"] for lab in labs], "seed": 1000 + 7919 * i,
                   "dir": {"az": c["aim"]["az"], "el": c["aim"]["el"], "cov": c["coverage"]} if directional else None,
                   "labs": labs}
    job = dict(drawn={"plan": g["plan"], "floor": g["floor"], "ceil": g["ceiling"], "stageY": bp.stage_y(cfg)},
               srcs=srcs, mats=mats, air=air, c=cfg["c"], n=rays, mix=bool(mix), order=bp.early_order(cfg),
               bands=[float(x) for x in room.octave_bands.centers])
    r = subprocess.run(["node", "--max-old-space-size=4096", "-e", JS], input=json.dumps(job), capture_output=True,
                       text=True, cwd=ROOT)
    if r.returncode:
        sys.exit(r.stderr[-1500:])
    O = json.loads(r.stdout)
    return {lab: np.array(O[s][k]) for s, v in srcs.items() for k, lab in enumerate(v["labs"])}, room.octave_bands.centers


def crit(H, pos, centers, c):
    rows = [int(np.argmin(np.abs(np.asarray(centers) - b))) for b in BANDS]
    out = {}
    for lab, h in H.items():
        m = criteria(np.asarray(h)[rows], np.linalg.norm(np.subtract(pos[lab]["src"], pos[lab]["rec"])) / c)
        out[lab] = {k: dict(zip(BANDS, m[k])) for k in ("T30", "EDT", "C80")}
    return out


def calibrate_js(cfg, pos, rays, mix, log):
    base = {k: np.asarray(v["alpha"][:6], float) for k, v in cfg["geometry"]["materials"].items()}
    meas = np.array([np.nanmedian([p["T30"].get(b, np.nan) for p in pos.values()]) for b in BANDS])
    k = np.ones(6)
    for it in range(6):
        al = {m: np.clip(a * k, 0.01, 0.95).tolist() for m, a in base.items()}
        H, cen = js_hists(cfg, pos, al, rays, mix, False)
        C = crit(H, pos, cen, cfg["c"])
        T = np.array([np.nanmedian([C[lab]["T30"][b] for lab in pos]) for b in BANDS])
        err = T / meas - 1
        log(f"  iteration {it}: T30 sim {', '.join(f'{x:.2f}' for x in T)} | error % {', '.join(f'{100 * x:+.1f}' for x in err)}"
            f" | factor {', '.join(f'{x:.3f}' for x in k)}")
        if np.all(np.abs(err) <= 0.02):
            break
        k = k * T / meas
        if it == 5:
            al = {m: np.clip(a * k, 0.01, 0.95).tolist() for m, a in base.items()}
    return al, k


def report(name, C, pos, log, rows):
    log(f"{name}: mean difference simulation - measurement (share of the {len(pos)} positions within 1 JND)")
    for q, u in (("T30", "%"), ("EDT", "%"), ("C80", "dB")):
        line = f"  {q}"
        for b in BANDS:
            s = np.array([C[lab][q][b] for lab in pos]); m = np.array([pos[lab][q].get(b, np.nan) for lab in pos])
            d = (100 * (s / m - 1)) if u == "%" else s - m
            ok = np.isfinite(d)
            line += f"  {b}: {np.mean(d[ok]):+.1f} {u} ({100 * np.mean(np.abs(d[ok]) <= JND[q]):.0f} %)"
            rows.append({"run": name, "metric": q, "band_hz": b, "mean_diff": float(np.mean(d[ok])),
                         "median_abs_diff": float(np.median(np.abs(d[ok]))),
                         "within_jnd": float(np.mean(np.abs(d[ok]) <= JND[q])), "sim_mean": float(np.nanmean(s)),
                         "meas_mean": float(np.nanmean(m)), "unit": u})
        log(line)
    r = [np.nanmean([C[lab]["EDT"][b] / C[lab]["T30"][b] for lab in pos]) for b in BANDS]
    log("  EDT / T30 simulated " + " ".join(f"{x:.2f}" for x in r))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config"); ap.add_argument("t30"); ap.add_argument("data")
    ap.add_argument("--rays", type=int, default=80000); ap.add_argument("--python", default=None)
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "detmold_js"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    lf = open(os.path.join(a.out, "run.log"), "w")

    def log(s):
        print(s, flush=True); lf.write(s + "\n"); lf.flush()
    cfg = bp.load_config(a.config)
    pos = positions(a.t30)
    measured_c80(pos, a.data)
    log(f"{len(pos)} positions; measured medians T30 " + ", ".join(f"{np.nanmedian([p['T30'].get(b, np.nan) for p in pos.values()]):.2f}" for b in BANDS)
        + " | EDT/T30 measured " + " ".join(f"{np.nanmean([p['EDT'][b] / p['T30'][b] for p in pos.values() if b in p['T30']]):.2f}" for b in BANDS))
    rows = []
    for name, mix in (("browser, either-or scattering", False), ("browser, mixed direction", True)):
        log(f"\n{name}: calibration, {a.rays} rays, omnidirectional source")
        al, k = calibrate_js(cfg, pos, a.rays, mix, log)
        json.dump({"alpha": al, "factor": k.tolist()}, open(os.path.join(a.out, f"cal_{'mix' if mix else 'either'}.json"), "w"), indent=1)
        H, cen = js_hists(cfg, pos, al, a.rays, mix, True)
        report(name, crit(H, pos, cen, cfg["c"]), pos, log, rows)
    if a.python:
        c = copy.deepcopy(bp.load_config(a.python))
        H = {}
        for s in sorted({lab.split("_")[0] for lab in pos}):
            labs = [lab for lab in pos if lab.startswith(s + "_")]
            c["receivers"] = {lab: pos[lab]["rec"] for lab in labs}
            h, cen = bp.energy_hists(c, s, labs, n_rays=a.rays, seed=1)
            H.update(h)
        log("")
        report("Python engine (pyroomacoustics, mixed direction), " + os.path.basename(os.path.dirname(os.path.abspath(a.python))),
               crit(H, pos, cen, c["c"]), pos, log, rows)
    with open(os.path.join(a.out, "summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
