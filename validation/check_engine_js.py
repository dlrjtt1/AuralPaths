"""
engine_js.py (the browser engine called from Python) against the page itself.

The config is loaded into the page (headless Chromium, tests/page_dump.js), which computes every path with its
workers. Then, per source of the page:
  1. same job: engine_js.run_job with the page's own worker parameters, positions and ray seeds; the histograms
     must be the page's (same code, same random streams): largest relative difference of a band's energy.
  2. from the config: engine_js.page_params(cfg) against the page's parameters (materials, air absorption, order,
     switches), i.e. whether a Python config means the same hall to both. Known: the page computes with its own
     speed of sound (343 m/s) and ignores "c" of a config; in 3-D halls it limits the rays to 10000 / 30000 / 50000.

    python validation/check_engine_js.py <config.json> [--json]      (needs node and playwright)
"""
import json
import os
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, ROOT)
import brir_proto as bp                       # noqa: E402
import engine_js                              # noqa: E402


def main():
    path = os.path.abspath(sys.argv[1])
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "page.json")
        r = subprocess.run(["node", os.path.join(ROOT, "tests", "page_dump.js"), os.path.abspath(ROOT), path, out],
                           capture_output=True, text=True, cwd=ROOT)
        if r.returncode:
            sys.exit(r.stderr[-1500:] or r.stdout[-500:])
        P = json.load(open(out))
    pp, paths = P["params"], P["paths"]
    # 1. the page's own job through the bridge
    job = {k: v for k, v in pp.items() if k != "seat"}
    job.update(seat=None, nSect=engine_js.RAY_SECT if any(p["dir"] for p in paths) else 0, mix=None, resid=False)
    if pp.get("seat") is not None:
        sys.exit("page run with the seat dip: not handled by this check")
    srcs = {}
    for p in paths:
        k = p["key"].split("|")[1]
        s = srcs.setdefault(k, {"pos": p["src"], "recs": [], "seed": 1000 + 7919 * p["seedIndex"], "dir": p["dir"], "keys": []})
        s["recs"].append(p["rec"]); s["keys"].append(p["key"])
    job["srcs"] = {k: {q: v[q] for q in ("pos", "recs", "seed", "dir")} for k, v in srcs.items()}
    O = engine_js.run_job(job)
    page = {p["key"]: np.array(p["hist"]) for p in paths}
    worst = 0.0
    for k, s in srcs.items():
        for i, key in enumerate(s["keys"]):
            a, b = np.array(O[k][i]["hist"]), page[key]
            worst = max(worst, float(np.max(np.abs(a.sum(1) - b.sum(1)) / np.maximum(b.sum(1), 1e-300))),
                        float(np.max(np.abs(a - b)) / np.max(b)))
    # 2. the config as Python reads it
    cfg = bp.load_config(path)
    mine = engine_js.page_params(cfg)
    diffs = []
    for k in ("air", "c", "order", "rays", "tWin", "spec", "diff", "diffRefl", "diffOrder", "bands", "fs", "HN", "HB"):
        same = json.dumps(mine[k]) == json.dumps(pp[k])
        if not same and isinstance(mine[k], (int, float, list)) and mine[k] is not None and pp[k] is not None:
            same = np.shape(mine[k]) == np.shape(pp[k]) and bool(np.allclose(np.asarray(mine[k], float), np.asarray(pp[k], float), rtol=0, atol=1e-12))
        if not same:
            diffs.append(k)
    mat_d = 0.0
    for g in pp["mats"]:
        if g in mine["mats"]:
            mat_d = max(mat_d, float(np.max(np.abs(np.array(mine["mats"][g]["R"]) - np.array(pp["mats"][g]["R"])))),
                        float(np.max(np.abs(np.atleast_1d(mine["mats"][g]["s"]) - np.atleast_1d(pp["mats"][g]["s"])))))
    missing = sorted(set(mine["mats"]) - set(pp["mats"]))        # the page also keeps its default groups
    res = {"paths": len(paths), "sources": len(srcs), "mesh": bool(pp["geom"].get("mesh")), "rays": pp["rays"],
           "max_rel_hist_diff": worst, "param_diffs": diffs, "max_material_diff": mat_d, "material_groups_missing_in_page": missing}
    if "--json" in sys.argv:
        print(json.dumps(res))
    else:
        print(f"{os.path.basename(path)}: {res['paths']} paths, {res['sources']} sources, {'3-D' if res['mesh'] else 'drawn'} hall, {res['rays']} rays")
        print(f"  1. same job: largest relative histogram difference {worst:.2e}")
        print(f"  2. config: parameters that differ {diffs or 'none'}; largest material difference {mat_d:.2e}; groups missing in the page {missing or 'none'}")


if __name__ == "__main__":
    main()
