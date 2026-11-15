"""
Measured directivity through engine_js.py: does the browser engine get the same pattern as the Python engine?

For a source with "directivity" (polar CSV, SOFA or inline balloon) engine_js.source_dir hands the page's table
model (GEOM.dirModel) the data that brir_proto.dir_model read. Compared: the band amplitude factors of both for
2000 random emission directions and an oblique aim (az 37, el -12 deg), and the diffuse-field factor 1 / Q that the
page computes from the table (4000 Fibonacci directions) against Python's.

    python validation/check_engine_js_dir.py [--json] [directivity file ...]
        default: examples/directivity_test_generic90.csv and .sofa
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
import engine_js                              # noqa: E402

JS = r"""const fs=require('fs');const GEOM=require('./engine_geom.js');const j=JSON.parse(fs.readFileSync(0,'utf8'));
const dm=GEOM.dirModel(j.spec,j.bands);const amp=j.e.map((e)=>dm.amp(e));
const n=4000,acc=j.bands.map(()=>0);for(let i=0;i<n;i++){const z=1-2*(i+0.5)/n,r=Math.sqrt(1-z*z),p=Math.PI*(1+Math.sqrt(5))*(i+0.5),a=dm.amp([r*Math.cos(p),r*Math.sin(p),z]);a.forEach((v,b)=>acc[b]+=v*v/n);}
console.log(JSON.stringify({amp,diffuse:acc}));"""


def check(path):
    cfg = {"fs": 48000, "c": 343.0, "room": {"dims_m": [5, 5, 5], "absorption_octave": {"values": [0.2] * 6}, "air_absorption": True},
           "sources": {"S": {"pos": [1, 1, 1], "aim": {"az": 37.0, "el": -12.0}, "directivity": path}}, "receivers": {}}
    bands = [125.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, 8000.0, 16000.0]
    dm = bp.dir_model(cfg, "S", np.array(bands))
    rng = np.random.default_rng(1)
    e = rng.normal(size=(3, 2000)); e /= np.linalg.norm(e, axis=0)
    py = bp.dir_amp(dm, e)                                    # [bands, N]
    r = subprocess.run(["node", "-e", JS], input=json.dumps({"spec": engine_js.source_dir(cfg, "S", bands), "bands": bands, "e": e.T.tolist()}),
                       capture_output=True, text=True, cwd=ROOT)
    if r.returncode:
        sys.exit(r.stderr[-1500:])
    O = json.loads(r.stdout)
    js = np.array(O["amp"]).T
    return {"kind": dm["kind"], "max_amp_diff_db": float(np.max(np.abs(20 * np.log10(js / py)))),
            "max_diffuse_diff_db": float(np.max(np.abs(10 * np.log10(np.array(O["diffuse"]) / np.asarray(dm["diffuse"])))))}


def main():
    files = [x for x in sys.argv[1:] if not x.startswith("--")] or [os.path.join(ROOT, "examples", "directivity_test_generic90.csv"),
                                                                    os.path.join(ROOT, "examples", "directivity_test_generic90.sofa")]
    res = {os.path.basename(f): check(f) for f in files}
    if "--json" in sys.argv:
        print(json.dumps({"max_amp_diff_db": max(v["max_amp_diff_db"] for v in res.values()),
                          "max_diffuse_diff_db": max(v["max_diffuse_diff_db"] for v in res.values()), "files": len(res)}))
    else:
        for f, v in res.items():
            print(f"{f} ({v['kind']}): largest difference of the band amplitudes {v['max_amp_diff_db']:.2e} dB, of the diffuse factor {v['max_diffuse_diff_db']:.2e} dB")


if __name__ == "__main__":
    main()
