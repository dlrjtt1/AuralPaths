"""
What did the dropped narrow faces of 3D models (fixed on 2026-11-18, see validation/mesh_leak.md) do to the results?

    python validation/check_leak_effect.py <config.json> <old engine_geom.js> [--rays 50000] [--seed 1]

Runs every source - receiver pair of the config with the page's engine as it is now and with an older engine file
(e.g. `git show 1e911b9:engine_geom.js > /tmp/engine_before.js`), same rays and seed, and prints T30, EDT and C80
per octave band (mean over the pairs) and the change. Needs node.
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import brir_proto as bp                      # noqa: E402
import engine_js                             # noqa: E402
import validate_fratoni as vf                # noqa: E402


def run(cfg, rays, seed, engine=None):
    js = engine_js.JS
    if engine:
        engine_js.JS = js.replace("require('./engine_geom.js')", "require(" + json.dumps(os.path.abspath(engine)) + ")")
    try:
        paths = {s: sorted(cfg["receivers"]) for s in cfg["sources"]}
        H, cen = engine_js.hists(cfg, paths, n_rays=rays, seed=seed)
    finally:
        engine_js.JS = js
    out = {}
    for (s, r), h in H.items():
        t0 = np.linalg.norm(np.subtract(cfg["sources"][s]["pos"], cfg["receivers"][r])) / cfg["c"]
        out[(s, r)] = vf.criteria(h, t0)
    return out, cen


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config"); ap.add_argument("old_engine"); ap.add_argument("--rays", type=int, default=50000); ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    cfg = bp.load_config(a.config)
    new, cen = run(cfg, a.rays, a.seed)
    old, _ = run(cfg, a.rays, a.seed, a.old_engine)
    bands = [i for i, f in enumerate(cen) if 125 <= f <= 4000]
    print(f"{os.path.basename(a.config)}: {len(new)} pairs, {a.rays} rays, seed {a.seed}; old engine: {os.path.basename(a.old_engine)}")
    print("| criterion | engine | " + " | ".join(f"{int(cen[b])} Hz" for b in bands) + " |")
    print("|---|---|" + "---|" * len(bands))
    for key, unit, rel in (("T30", "s", True), ("EDT", "s", True), ("C80", "dB", False)):
        o = np.array([old[p][key][bands] for p in old]); n = np.array([new[p][key][bands] for p in old])
        print(f"| {key} ({unit}) | before | " + " | ".join(f"{v:.2f}" for v in np.nanmean(o, 0)) + " |")
        print("| | now | " + " | ".join(f"{v:.2f}" for v in np.nanmean(n, 0)) + " |")
        d = (n / o - 1) * 100 if rel else n - o
        print(f"| | change, mean ({'%' if rel else 'dB'}) | " + " | ".join(f"{v:+.1f}" for v in np.nanmean(d, 0)) + " |")
        print("| | change, largest of a pair | " + " | ".join(f"{d[np.nanargmax(np.abs(d[:, i])), i]:+.1f}" for i in range(len(bands))) + " |")


if __name__ == "__main__":
    main()
