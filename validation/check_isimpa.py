"""
Cross-check of AuralPaths against an independent free simulator: I-Simpa's SPPS solver (sound particle tracing,
Universite Gustave Eiffel, GPL-3.0, https://github.com/Universite-Gustave-Eiffel/I-Simpa), run headless on the same
BRAS halls (CR3, CR4), with the same materials (BRAS fitted estimates), positions and air absorption, and on a shoebox.

    ISIMPA_BUILD=<I-Simpa build folder> python validation/check_isimpa.py <BRAS folder> CR3 [--particles 300000]
    ISIMPA_BUILD=<...> python validation/check_isimpa.py box

I-Simpa is not bundled and not linked: this script writes SPPS's input files (scene mesh .cbin, tetrahedral mesh
.mbin from tetgen, config.xml), runs the spps executable and reads its point-receiver energy histograms with I-Simpa's
Python bindings (libsimpa). Without the I-Simpa GUI the preprocessing is done here: the OBJ is triangulated, vertices
merged, and the few self-intersections tetgen reports are repaired (a vertex on a facet: the facet is split at it;
two crossing segments: the shared edge of the two triangles is flipped); tetgen -p -A -n (no refinement: SPPS only
needs the connectivity), every tetrahedron in volume 0 (a non-zero volume id marks a "fitting" in SPPS).
Settings: energetic method, 1 ms time step, 3 s, receiver radius 0.5 m (as AuralPaths), ISO 9613-1 air absorption at
20 degC / 50 %, materials with probability "scattering" of a Lambert reflection (law 2), otherwise specular.

Build notes (Linux, I-Simpa main of 2026-01-14): built with -DSKIPISIMPA=ON against the system Boost 1.83 (the
CMake files ask for 1.89 and for the header-only Boost::algorithm target, both relaxed locally), and with one source
fix: src/spps/input_output/reportmanager.cpp calls abs() on doubles (RaySphere and the receiver crossing length),
which with GCC resolves to the integer abs and truncates; every point receiver then records zero energy. Replacing it
by std::abs fixes it. Without that fix this check cannot run.

Result on 2026-11-07: see validation/isimpa_check.md.
"""
import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
BUILD = os.environ.get("ISIMPA_BUILD", "")
if BUILD:
    sys.path.insert(0, os.path.join(BUILD, "src/python_bindings"))
try:
    import libsimpa as ls
except ImportError:
    ls = None

FREQS = [50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000,
         6300, 8000, 10000, 12500, 16000, 20000]
OCT = [125, 250, 500, 1000, 2000, 4000]


def f6(x):
    return f"{x:.6f}".replace(".", ",")


def write_inputs(wd, V, T, mat_of_tri, tetgen_opts="-p -A -n"):
    """V [n,3], T [m,3] (0-based), mat_of_tri [m] material ids -> mesh.cbin and tetramesh.mbin in wd."""
    wd = os.path.abspath(wd); os.makedirs(wd, exist_ok=True)
    model = ls.ioModel()
    for v in V:
        model.vertices.append(ls.t_pos(float(v[0]), float(v[1]), float(v[2])))
    for (a, b, c), m in zip(T, mat_of_tri):
        f = ls.ioFace(); f.a, f.b, f.c = int(a), int(b), int(c); f.idEn = -1; f.idMat = int(m); f.idRs = -1
        model.faces.append(f)
    ls.CformatBIN().ExportBIN(os.path.join(wd, "mesh.cbin"), model)
    poly = os.path.join(wd, "scene.poly")
    with open(poly, "w") as o:
        o.write(f"{len(V)} 3 0 0\n")
        for i, v in enumerate(V):
            o.write(f"{i + 1} {float(v[0]):.9g} {float(v[1]):.9g} {float(v[2]):.9g}\n")
        o.write(f"{len(T)} 1\n")
        for k, (a, b, c) in enumerate(T):
            o.write(f"1 0 {k}\n3 {a + 1} {b + 1} {c + 1}\n")
        o.write("0\n0\n")
    r = subprocess.run([os.path.join(BUILD, "src/tetgen/tetgen")] + tetgen_opts.split() + [poly], capture_output=True, text=True, cwd=wd)
    if r.returncode or not os.path.exists(os.path.join(wd, "scene.1.ele")):
        raise RuntimeError("tetgen failed:\n" + (r.stdout + r.stderr)[-3000:])
    base = os.path.join(wd, "scene.1")
    node = np.loadtxt(base + ".node", skiprows=1, comments="#")
    ele = np.loadtxt(base + ".ele", skiprows=1, comments="#", dtype=np.int64)
    face = np.loadtxt(base + ".face", skiprows=1, comments="#", dtype=np.int64)
    neigh = np.loadtxt(base + ".neigh", skiprows=1, comments="#", dtype=np.int64)
    nodes = node[:, 1:4]
    tets = ele[:, 1:5] - 1
    vol = ele[:, 5] if ele.shape[1] > 5 else np.zeros(len(ele), int)
    nb = neigh[:, 1:5] - 1                                    # -1 (none) -> -2, as I-Simpa
    fmark = {tuple(sorted(f[1:4] - 1)): int(f[4]) for f in face}
    mesh = ls.trimeshmodel()
    for p in nodes:
        mesh.nodes.append(ls.t_binNode(float(p[0]), float(p[1]), float(p[2])))
    for t, v, nbr in zip(tets, vol, nb):
        a, b, c, d = map(int, t)
        fv = [(b, d, c), (c, d, a), (a, d, b), (b, c, a)]          # face i is opposite vertex i (tetgen neighbour order)
        F = [ls.bintetraface(*fv[i], fmark.get(tuple(sorted(fv[i])), -1), int(nbr[i])) for i in range(4)]
        mesh.tetrahedres.append(ls.bintetrahedre(a, b, c, d, 0, *F))   # idVolume != 0 would mark a fitting volume
    ls.CMBIN().SaveMesh(os.path.join(wd, "tetramesh.mbin"), mesh)
    return dict(n_tets=len(tets), n_nodes=len(nodes))


def write_config(wd, mats, sources, receivers, duration=2.5, dt=0.001, n_particles=500000, radius=0.5, air=True, seed=1):
    """mats {id: (alpha[6 oct], scattering)}; sources/receivers {name: (x,y,z)}."""
    wd = os.path.abspath(wd)
    L = ['<?xml version="1.0" encoding="iso-8859-1"?>', f'<configuration workingdirectory="{wd}/">',
         f'  <simulation recepteurss_directory="recepteurss/" recepteurss_filename="Sound_level.csbin" recepteurss_cut_filename="rs_cut.csbin" '
         f'receiversp_directory="Punctual receivers" receiversp_filename="Sound level.recp" receiversp_filename_adv="Advanced sound level.gap" '
         f'cumul_filename="Total energy.recp" modelName="mesh.cbin" tetrameshFileName="tetramesh.mbin" abs_atmo_calc="{int(air)}" enc_calc="0" '
         f'trans_calc="0" direct_calc="0" duree_simulation="{f6(duration)}" output_recp_bysource="0" output_recs_byfreq="0" surf_receiv_method="0" '
         f'random_seed="{seed}" computation_method="1" nbparticules="{n_particles}" nbparticules_rendu="0" pasdetemps="{f6(dt)}" '
         f'rayon_recepteurp="{f6(radius)}" trans_epsilon="5,000000" intensity_filename="Intensity vector.rpi" intensity_folder="IntensityAnimation" '
         f'intensity_rp_filename="ponct_intensity.gabe" stats_filename="statsSPPS.gabe" particules_directory="particles/" '
         f'particules_filename="particles.pbin" directivities_directory="">', '    <freq_enum>']
    for f in FREQS[::-1]:
        L.append(f'      <bfreq freq="{f}" docalc="{int(f in OCT)}"/>')
    L += ['    </freq_enum>', '  </simulation>',
          '  <condition_atmospherique absatmo="0,000000" disable_absatmo_computation="0" humidite="50,000000" pression="101325,000000" '
          'alog="0,000000" blin="0,000000" lst_soltype="1" z0="0,020000" temperature="20,000000"/>', '  <surface_absorption_enum>']
    for mid, (alpha, s) in mats.items():
        L.append(f'    <type_surface id="{mid}" resistivite="100,000000" side_material="1">')
        for f in FREQS[::-1]:
            i = min(range(6), key=lambda j: abs(np.log(OCT[j] / f)))
            L.append(f'      <bfreq freq="{f}" absorb="{f6(alpha[i])}" diffusion="{f6(s[i] if hasattr(s, "__len__") else s)}" loi="2"/>')
        L.append('    </type_surface>')
    L += ['  </surface_absorption_enum>', '  <sources>']
    for k, (name, p) in enumerate(sources.items()):
        L.append(f'    <source id="{100 + k}" name="{name}" directivity_file="" x="{f6(p[0])}" y="{f6(p[1])}" z="{f6(p[2])}" delay="0,000000" '
                 f'u="1,000000" v="0,000000" w="0,000000" directivite="0">')
        L += [f'      <bfreq freq="{f}" db="100,000000"/>' for f in FREQS[::-1]]
        L.append('    </source>')
    L += ['  </sources>', '  <recepteursp>']
    for k, (name, p) in enumerate(receivers.items()):
        L.append(f'    <recepteur_ponctuel id="{1000 + k}" name="{name}" lbl="{name}" x="{f6(p[0])}" y="{f6(p[1])}" z="{f6(p[2])}" '
                 f'u="1,000000" v="0,000000" w="0,000000">')
        L += [f'      <bfreq freq="{f}" db="0,000000"/>' for f in FREQS[::-1]]
        L.append('    </recepteur_ponctuel>')
    L += ['  </recepteursp>', '  <recepteurss/>', '  <encombrement_enum/>', '</configuration>']
    open(os.path.join(wd, "config.xml"), "w", encoding="iso-8859-1").write("\n".join(L) + "\n")


def run(wd, timeout=7200):
    wd = os.path.abspath(wd)
    r = subprocess.run([os.path.join(BUILD, "src/spps/spps"), os.path.join(wd, "config.xml")], capture_output=True, text=True,
                       cwd=wd, timeout=timeout)
    if r.returncode:
        raise RuntimeError((r.stdout + r.stderr)[-3000:])
    return r.stdout


def read_receiver(wd, name):
    wd = os.path.abspath(wd)
    g = ls.Gabe_rw()
    path = os.path.join(wd, "Punctual receivers", name, "Sound level.recp")
    if not g.Load(path):
        raise RuntimeError("cannot read " + path)
    cols = [g.GetColTitle(i) for i in range(len(g))]
    data = [list(g.ReadColFloat(i)) if i > 0 else list(g.ReadColStr(i)) for i in range(len(g))]
    return cols, data


def fix_tjunctions(V,T,G,wd,maxit=50):
    """Run tetgen; while it reports 'A vertex lies on a facet', split that facet at the vertex."""
    T=[tuple(t) for t in T]; G=list(G)
    for it in range(maxit):
        try:
            info=write_inputs(wd,V,np.array(T),[0]*len(T)); return T,G,info,it
        except RuntimeError as e:
            msg=str(e)
            m=re.findall(r"vertex : \[(\d+)\]\s+facet triangle: \[(\d+),(\d+),(\d+)\]",msg)
            sg=re.findall(r"1st seg\s+\[(\d+),(\d+)\].*?\n\s+2nd seg: \[(\d+),(\d+)\]",msg)
            if not m and sg:
                # two triangles that share edge (a,b) cross the segment (c,d): flip the shared edge to (c,d)
                for a,b,c,d in sg:
                    a,b,c,d=int(a)-1,int(b)-1,int(c)-1,int(d)-1
                    ks=[i for i,t in enumerate(T) if a in t and b in t]
                    if len(ks)!=2: raise RuntimeError(f"edge {a},{b} not shared by two triangles: {ks}")
                    t1,t2=T[ks[0]],T[ks[1]]
                    c1=[v for v in t1 if v not in (a,b)][0]; c2=[v for v in t2 if v not in (a,b)][0]
                    i=t1.index(c1); u,v_=t1[(i+1)%3],t1[(i+2)%3]          # t1 = (c1,u,v_)
                    T[ks[0]]=(c1,u,c2); T[ks[1]]=(c2,v_,c1)
                print("iteration",it,"flipped",len(sg)); continue
            if not m: raise
            done=set()
            for v,a,b,c in m:
                v,a,b,c=int(v)-1,int(a)-1,int(b)-1,int(c)-1
                k=next((i for i,t in enumerate(T) if set(t)=={a,b,c}),None)
                if k is None or k in done: continue
                ta=T[k]; g=G[k]; done.add(k)
                T[k]=(ta[0],ta[1],v); T.append((ta[1],ta[2],v)); T.append((ta[2],ta[0],v)); G+= [g,g]
            print("iteration",it,"split",len(done))
    raise RuntimeError("not fixed")


def tris_from_obj(path):
    import geometry
    V, F, names = geometry.load_obj(path)
    key, VV, idx = {}, [], []
    for v in V:
        k = tuple(np.round(v, 4))
        if k not in key:
            key[k] = len(VV); VV.append(v)
        idx.append(key[k])
    T, G = [], []
    for f, n in zip(F, names):
        f = [idx[i] for i in f]
        for i in range(1, len(f) - 1):
            t = (f[0], f[i], f[i + 1])
            if len(set(t)) == 3:
                T.append(t); G.append(n)
    VV = np.array(VV)
    return np.c_[VV[:, 0], -VV[:, 2], VV[:, 1]], T, G                # y-up OBJ -> x, y, z up (AuralPaths frame)


def edc_t(e, lo, hi, bin_s=0.001):
    edc = 10 * np.log10(np.maximum(np.cumsum(e[::-1])[::-1] / e.sum(), 1e-30)); t = (np.arange(len(e)) + 0.5) * bin_s
    sel = (edc <= hi) & (edc >= lo)
    return -60 / np.polyfit(t[sel], edc[sel], 1)[0]


def run_box(wd, particles):
    L = (12.0, 9.0, 7.0)
    V = np.array([[x, y, z] for x in (0, L[0]) for y in (0, L[1]) for z in (0, L[2])])
    ix = lambda x, y, z: x * 4 + y * 2 + z
    Q = [(ix(0, 0, 0), ix(0, 1, 0), ix(0, 1, 1), ix(0, 0, 1)), (ix(1, 0, 0), ix(1, 0, 1), ix(1, 1, 1), ix(1, 1, 0)),
         (ix(0, 0, 0), ix(0, 0, 1), ix(1, 0, 1), ix(1, 0, 0)), (ix(0, 1, 0), ix(1, 1, 0), ix(1, 1, 1), ix(0, 1, 1)),
         (ix(0, 0, 0), ix(1, 0, 0), ix(1, 1, 0), ix(0, 1, 0)), (ix(0, 0, 1), ix(0, 1, 1), ix(1, 1, 1), ix(1, 0, 1))]
    T = [t for a, b, c, d in Q for t in ((a, b, c), (a, c, d))]
    out = {}
    for s in (1.0, 0.5, 0.1):
        w = os.path.join(wd, f"box_s{s}")
        shutil.rmtree(w, ignore_errors=True)
        write_inputs(w, V, np.array(T), [1] * len(T), tetgen_opts="-pq1.4 -a1 -A -n")
        write_config(w, {1: ([0.2] * 6, s)}, {"S": (3, 3, 1.5)}, {"R": (8, 5, 1.2)}, duration=2.5, dt=0.001,
                     n_particles=particles, air=False)
        run(w)
        E = np.array(read_receiver(w, "R")[1][1:])
        out[s] = float(np.mean([edc_t(e, -35, -5) for e in E]))
        print(f"box 12 x 9 x 7 m, alpha 0.2, scattering {s}: SPPS T30 {out[s]:.3f} s (mean of 6 octaves)", flush=True)
    return out


def run_hall(bras, hall, wd, particles):
    import validate_bras_cr as vb
    scene = os.path.join(bras, SCENES[hall])
    mats = vb.read_bras_materials(os.path.join(bras, "3 Surface descriptions"), hall, "fitted")
    _, _, E, R, eid, rid, _ = vb.read_rirs(scene)
    V, T, G = tris_from_obj(os.path.join(scene, "Geometry", hall + ".obj"))
    T, G, info, it = fix_tjunctions(V, T, G, os.path.join(wd, "mesh"))
    mid = {k: i + 1 for i, k in enumerate(mats)}
    M = [next(mid[k] for k in sorted(mats, key=len, reverse=True) if k.lower() in g.lower()) for g in G]
    srcs = {f"LS{e}": E[i] for i, e in enumerate(eid)}; recs = {f"MP{r}": R[i] for i, r in enumerate(rid)}
    res, stats = {}, {}
    for s, p in srcs.items():
        w = os.path.join(wd, s)
        shutil.rmtree(w, ignore_errors=True)
        write_inputs(w, V, np.array(T), M)
        write_config(w, {mid[k]: (v["alpha"], v["s_oct"]) for k, v in mats.items()}, {s: p}, recs, duration=3.0, dt=0.001,
                     n_particles=particles, radius=0.5, air=True)
        t = time.time(); run(w)
        for r in recs:
            res[f"{s}-{r}"] = np.array(read_receiver(w, r)[1][1:])
        print(f"{hall} {s}: {time.time() - t:.0f} s", flush=True)
    return res, {**{k: v for k, v in srcs.items()}, **recs}, dict(info, repairs=it, triangles=len(T))


SCENES = {"CR3": "CR3 medium room (chamber music hall)", "CR4": "CR4 large room (auditorium)"}


def report(hall, res, pos):
    from validate_fratoni import criteria, BANDS, jnd_units
    rows = [x for x in csv.DictReader(open(os.path.join(HERE, f"bras_{hall}.csv"))) if x["model"] == "3D mesh"]
    py = {(x["pair"], x["criterion"], int(float(x["band_hz"]))): float(x["simulated"]) for x in rows}
    me = {(x["pair"], x["criterion"], int(float(x["band_hz"]))): float(x["measured"]) for x in rows}
    sp, out = {}, []
    for pair, H in res.items():
        s, r = pair.split("-")
        cr = criteria(np.asarray(H), np.linalg.norm(np.subtract(pos[r], pos[s])) / 343.0)
        for c in ("T30", "EDT", "C80", "Ts"):
            for i, b in enumerate(BANDS):
                sp[(pair, c, b)] = float(cr[c][i])
    out.append(f"| criterion | 125 | 250 | 500 | 1k | 2k | 4k Hz (SPPS / AuralPaths Python / measured) |")
    out.append("|---|---|---|---|---|---|---|")
    for c in ("T30", "EDT", "C80", "Ts"):
        cells = []
        for b in BANDS:
            k = [(p, c, b) for p in res if (p, c, b) in me]
            f = (lambda v: f"{v:.0f}") if c == "Ts" else (lambda v: f"{v:.2f}")
            cells.append(" / ".join(f(np.nanmean([d[x] for x in k])) for d in (sp, py, me)))
        out.append(f"| {c} | " + " | ".join(cells) + " |")
    summ = {}
    for c in ("T30", "EDT", "C80", "Ts"):
        d = {"spps_meas": [], "py_meas": [], "spps_py": []}
        for b in (500, 1000, 2000):
            for p in res:
                k = (p, c, b)
                if k in me and np.isfinite(sp[k]):
                    d["spps_meas"].append(jnd_units(c, sp[k], me[k])); d["py_meas"].append(jnd_units(c, py[k], me[k]))
                    d["spps_py"].append(jnd_units(c, sp[k], py[k]))
        summ[c] = {k: (float(np.mean(np.abs(v))), float(np.mean(v))) for k, v in d.items()}
    return out, summ, sp


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras", help="BRAS folder, or 'box'"); ap.add_argument("hall", nargs="?", choices=list(SCENES))
    ap.add_argument("--particles", type=int, default=300000); ap.add_argument("--work", default="isimpa_work")
    a = ap.parse_args()
    if ls is None or not BUILD:
        sys.exit("set ISIMPA_BUILD to an I-Simpa build folder (spps, tetgen, python bindings)")
    if a.bras == "box":
        print(json.dumps(run_box(a.work, a.particles // 3)))
        return
    res, pos, info = run_hall(a.bras, a.hall, os.path.join(a.work, a.hall), a.particles)
    tab, summ, sp = report(a.hall, res, pos)
    print(json.dumps(info)); print("\n".join(tab))
    for c, v in summ.items():
        print(f"{c} 500 Hz - 2 kHz, mean |diff| (signed) in JND: SPPS-measured {v['spps_meas'][0]:.1f} ({v['spps_meas'][1]:+.1f}), "
              f"AuralPaths-measured {v['py_meas'][0]:.1f} ({v['py_meas'][1]:+.1f}), SPPS-AuralPaths {v['spps_py'][0]:.1f} ({v['spps_py'][1]:+.1f})")
    with open(os.path.join(HERE, f"isimpa_{a.hall}.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["pair", "criterion", "band_hz", "spps"])
        for (p, c, b), v in sorted(sp.items()):
            w.writerow([p, c, b, round(v, 3)])


if __name__ == "__main__":
    main()
