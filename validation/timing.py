"""
Where does the computing time go? (diagnostic, 2026-11-15)

Python engine: wall-clock timers around the engine's stages for (1) the room criteria path, bp.energy_hists of one source at all receivers, and (2) the
BRIR path of one source at three receivers (energy_hists with the residual, early_resid_directions, path_brir).

    python validation/timing.py <config.json> <source> [--rays 20000] [--brir] [--out out/timing/<name>.json]

Browser engine: validation/timing_js.py.
"""
import argparse
import json
import os
import sys
import time

import numpy as np  # noqa: F401
import pyroomacoustics as pra

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import brir_proto as bp                       # noqa: E402

# Stages. Every time is exclusive: the time inside a stage that is itself a stage (e.g. make_room inside
# early_binaural) counts for the inner one only, so the rows add up to the wall time.
STAGES = [("ray tracing (pyroomacoustics, C++)", pra.Room, "ray_tracing"),
          ("image sources (pyroomacoustics, C++)", pra.Room, "image_source_model"),
          ("room set-up (make_room: walls, convexity test)", bp, "make_room"),
          ("source pattern for the rays (rt_add_source)", bp, "rt_add_source"),
          ("finite-panel / scattering factors of the images (specular_factors)", bp, "specular_factors"),
          ("emission directions of the images", bp, "emission_dirs"),
          ("image energy histogram (rest)", bp, "_image_energy_hist"),
          ("ray-guided specular paths", bp, "spec_arrivals"),
          ("diffraction", bp, "diffraction_arrivals"),
          ("early residual directions (Python direction tracer)", bp, "early_resid_directions"),
          ("early binaural (images x HRIR; rest)", bp, "early_binaural"),
          ("late binaural (noise bank)", bp, "late_binaural"),
          ("early residual binaural", bp, "early_resid_binaural")]
OTHER = "other (Python glue, smoothing, numpy)"
T, STACK = {}, []


def _wrap(lab, obj, name):
    f = getattr(obj, name)

    def g(*a, **k):
        STACK.append(0.0); t = time.perf_counter()
        try:
            return f(*a, **k)
        finally:
            el = time.perf_counter() - t
            T[lab] = T.get(lab, 0.0) + el - STACK.pop()
            if STACK:
                STACK[-1] += el
    setattr(obj, name, g)


for _l, _o, _n in STAGES:
    _wrap(_l, _o, _n)


def profile(fn):
    T.clear(); t = time.perf_counter(); r = fn(); wall = time.perf_counter() - t
    rows = dict(T)
    rows[OTHER] = wall - sum(rows.values())
    return r, wall, rows, []


def show(title, wall, rows, top):
    print(f"\n{title}: {wall:.1f} s")
    for lab, t in sorted(rows.items(), key=lambda x: -x[1]):
        print(f"  {t:7.1f} s  {100 * t / wall:5.1f} %  {lab}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config"); ap.add_argument("source"); ap.add_argument("--rays", type=int, default=20000)
    ap.add_argument("--brir", action="store_true"); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    cfg = bp.load_config(a.config)
    cfg["geometry"]["rays"] = a.rays
    recs = list(cfg["receivers"])
    res = {"config": a.config, "source": a.source, "rays": a.rays, "receivers": len(recs), "mesh": bool(bp.is_mesh(cfg))}
    _, wall, rows, top = profile(lambda: bp.energy_hists(cfg, a.source, recs, n_rays=a.rays, seed=1))
    show(f"criteria path: energy_hists, {len(recs)} receivers, {a.rays} rays", wall, rows, top)
    res["criteria"] = {"wall_s": wall, "groups": rows, "top": top}
    if a.brir:
        hrir = bp.load_hrir(cfg["binaural"]["sofa_path"], cfg["fs"])
        r3 = recs[:: max(1, len(recs) // 3)][:3]
        n_len = int(1.5 * cfg["fs"])

        def brirs():
            air = bp.make_room(cfg, 0).air_absorption
            h, centers, rs = bp.energy_hists(cfg, a.source, r3, n_rays=a.rays, seed=1, return_resid=True)
            ew = bp.early_resid_directions(cfg, a.source, r3, centers, air)
            for i, r in enumerate(r3):
                bp.path_brir(cfg, a.source, r, hrir, h[r] if isinstance(h, dict) else h[i], centers, n_len, seed=i,
                             resid=rs[r] if isinstance(rs, dict) else rs[i], ew=ew[i])
        _, wall, rows, top = profile(brirs)
        show(f"BRIR path: 3 receivers, {a.rays} rays", wall, rows, top)
        res["brir"] = {"wall_s": wall, "groups": rows, "top": top}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
