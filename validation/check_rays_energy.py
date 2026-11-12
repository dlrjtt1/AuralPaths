"""
Energy of the ray tracing against exact image sources (2026-11-12).

A 12 x 9 x 7 m shoebox drawn as a mesh, absorption 0.2 on every face, scattering 0, 0.3 and 0.9. The reference is the
image-source model of the same box (pyroomacoustics ShoeBox, order 60, specular). Printed: ray-traced energy minus
reference energy (dB) at one receiver in three windows after the direct sound (0 - 80 ms, 80 - 300 ms, 300 - 1000 ms),
for the Python tracer (pyroomacoustics through brir_proto.make_room) and the browser tracer (engine_geom.js rays).
Scattering moves energy between directions and should not create any: the windows should stay within about 1 dB
for every scattering value (the late field of a shoebox with diffuse reflections decays a little differently
from the specular one). Before brir_proto._no_diffuse_rain the Python tracer gave +1 ... +1.9 dB at s = 0.3 and
+2.4 ... +3.5 dB at s = 0.9.

    python validation/check_rays_energy.py [--json]      (needs node on the PATH for the browser part)
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
import brir_proto as bp                       # noqa: E402
import pyroomacoustics as pra                 # noqa: E402

L = (12.0, 9.0, 7.0); S = [3.0, 3.0, 1.5]; M = [8.0, 5.0, 1.2]; A = 0.2; C = 343.0; N = 3000; HB = 0.001
SC = (0.0, 0.3, 0.9)
V = [(x, y, z) for x in (0, L[0]) for y in (0, L[1]) for z in (0, L[2])]
F = [(1, 3, 4, 2), (5, 6, 8, 7), (1, 2, 6, 5), (3, 7, 8, 4), (1, 5, 7, 3), (2, 4, 8, 6)]
OBJ = "g wall\n" + "".join(f"v {x} {y} {z}\n" for x, y, z in V) + "".join("f " + " ".join(map(str, f)) + "\n" for f in F)
JS = """const fs=require('fs');const GEOM=eval(fs.readFileSync('engine_geom.js','utf8')+';GEOM');const j=JSON.parse(fs.readFileSync(0,'utf8'));
const G=GEOM.buildMesh({obj:GEOM.loadObj(j.obj),groups:{wall:'wall'},voxel:0.1,axes:'z-up'},j.src);const out={};
for(const s of j.ss){const R=GEOM.rays(G,j.src,[j.rec],{n:20000,c:j.c,tMax:3.0,bin:0.001,seed:7},{wall:{R:[Math.sqrt(1-j.a)],s:s}},[0]);out[s]=Array.from(R.H[0][0]);}
console.log(JSON.stringify(out));"""


def reference():
    room = pra.ShoeBox(np.array(L), fs=16000, materials=pra.Material(A, 0.0), max_order=60, air_absorption=False)
    room.set_sound_speed(C)
    room.add_source(S); room.add_microphone(M); room.image_source_model()
    so = room.sources[0]
    d = np.linalg.norm(so.images - np.array(M)[:, None], axis=0)
    E = (so.damping[0] / d) ** 2
    h = np.zeros(N); idx = (d / C / HB).astype(int); k = idx < N
    np.add.at(h, idx[k], E[k])
    return h


def py_rays(s):
    cfg = {"fs": 16000, "c": C, "room": {"dims_m": list(L), "absorption_octave": {"values": [A] * 6}, "air_absorption": True},
           "sources": {"S": {"pos": S}}, "receivers": {"R": M},
           "geometry": {"mesh": {"obj": "box.obj", "obj_text": OBJ, "axes": "z-up", "groups": {"wall": "wall"}},
                        "materials": {"wall": {"alpha": [A] * 6, "s": [s] * 6}}}}
    rt = bp.make_room(cfg, 0, ray_tracing=True)
    rt.set_ray_tracing(n_rays=20000, receiver_radius=0.5, hist_bin_size=HB, time_thres=N * HB, energy_thres=bp.RT_ENERGY_THRES)
    rt.add_source(S); rt.add_microphone(M)
    pra.libroom.set_rng_seed(7)
    rt.ray_tracing()
    raw = np.asarray(rt.rt_histograms[0][0][0])[0]
    h = np.zeros(N); h[:min(N, raw.size)] = raw[:N]
    return h


def js_rays():
    r = subprocess.run(["node", "-e", JS], input=json.dumps(dict(obj=OBJ, src=S, rec=M, a=A, c=C, ss=list(SC))),
                       capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        sys.exit(r.stderr[-1500:])
    return {float(k): np.array(v) for k, v in json.loads(r.stdout).items()}


def main():
    ref = reference()
    t = (np.arange(N) + 0.5) * HB
    t0 = np.linalg.norm(np.array(S) - np.array(M)) / C
    win = ((0.0, t0 + 0.08), (t0 + 0.08, t0 + 0.3), (t0 + 0.3, t0 + 1.0))

    def diff(h):
        return [10 * np.log10(h[(t >= a) & (t < b)].sum() / ref[(t >= a) & (t < b)].sum()) for a, b in win]
    js = js_rays()
    out = {}
    for s in SC:
        p, j = diff(py_rays(s)), diff(js[s])
        out[f"py_s{s}"], out[f"js_s{s}"] = p, j
        if "--json" not in sys.argv:
            print(f"s = {s}: rays - image sources (dB), 0-80 / 80-300 / 300-1000 ms:  Python " +
                  " ".join(f"{x:+.2f}" for x in p) + "   browser " + " ".join(f"{x:+.2f}" for x in j))
    mx = max(abs(x) for v in out.values() for x in v)
    if "--json" in sys.argv:
        print(json.dumps({"max_abs_db": round(mx, 3), "py_s0.9_late_db": round(out["py_s0.9"][2], 3)}))
    else:
        print(f"largest deviation {mx:.2f} dB")


if __name__ == "__main__":
    main()
