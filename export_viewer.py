"""
Bundle the model parameters and run.py results into one self-contained viewer page.

    python export_viewer.py [config.json]      (run.py calls this automatically)

What goes into the page
  - KU100 HRIR subset (~4 deg grid) and its diffuse-field band gains
  - Hall, source and receiver geometry from config.json (editable in the page)
  - pyroomacoustics air-absorption coefficients and octave-band centres
  - conditions.csv rows: the Python reference for the config geometry
The page rebuilds every BRIR itself (image sources + HRIR for the early part,
statistical decay for the late part), so hall size, absorption and positions can
be changed without rerunning Python. Python stays the reference implementation.
"""
import base64
import csv
import json
import os
import sys

import numpy as np

import brir_proto as bp

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = "0.5"
LATE_SECONDS = 1.6


def hrir_subset(sofa_path, fs, step=2):
    """Every other row/column of the 2-deg FULL2DEG grid (~4 deg). Falls back to all directions."""
    import sofar
    s = sofar.read_sofa(sofa_path, verify=False, verbose=False)
    pos = np.asarray(s.SourcePosition, dtype=float)
    ir = np.asarray(s.Data_IR, dtype=float)
    keep_el = set(np.unique(np.round(pos[:, 1], 3))[::step])
    sel = np.array([(round(e, 3) in keep_el) and (round(a) % (2 * step) == 0) for a, e in zip(pos[:, 0], pos[:, 1])])
    if sel.sum() < 500:
        sel[:] = True
    az, el = np.deg2rad(pos[sel, 0]), np.deg2rad(pos[sel, 1])
    dirs = np.c_[np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)]
    sub = ir[sel]
    scale = float(np.max(np.abs(sub)))
    q = np.round(sub / scale * 32767).astype("<i2")
    return {"n": int(sel.sum()), "taps": int(sub.shape[-1]), "s": scale,
            "d": base64.b64encode(q.tobytes()).decode("ascii"), "dirs": np.round(dirs, 5).ravel().tolist()}


def hpcf_data(cfg):
    """Headphone compensation filter for the page (float32, base64), or None."""
    p = cfg["binaural"].get("headphone_filter")
    if not p or not os.path.exists(p):
        return None
    ir, name = bp.load_hpcf(p, cfg["fs"])
    return {"name": name, "d": base64.b64encode(np.asarray(ir, dtype="<f4").tobytes()).decode("ascii")}


def dir_spec(cfg, k, bands):
    """Aim and directivity of one source for the viewer: generic coverage, or polar-data tables."""
    sp = cfg["sources"][k]
    d = {"cov": sp.get("coverage", 0), "az": sp.get("aim", {}).get("az", 0), "el": sp.get("aim", {}).get("el", 0)}
    if sp.get("directivity"):
        dm = bp.dir_model(cfg, k, bands)
        dv = sp["directivity"]
        d.update({"cov": 0, "file": dv.get("name", "data") if isinstance(dv, dict) else dv})
        if dm["kind"] == "balloon":
            d["table"] = {"balloon": np.round(dm["balloon"]["db"], 2).tolist(), "diffuse": np.round(dm["diffuse"], 5).tolist()}
        else:
            d["rows"] = [list(r) for r in bp.directivity_rows(dv)]
            d["normalize"] = bp.directivity_normalize(dv)
            d["table"] = {"h": np.round(dm["tab"]["h"], 2).tolist(), "v": np.round(dm["tab"]["v"], 2).tolist(),
                          "diffuse": np.round(dm["diffuse"], 5).tolist()}
    return d


def late_tables(hr):
    """Direction-bin tables of the full HRIR set for the directional late field (brir_proto.late_dir_tables)."""
    t = bp.late_dir_tables(hr)
    b64 = lambda a: base64.b64encode(np.asarray(a, dtype="<f4").ravel().tobytes()).decode("ascii")
    sc = float(np.max(t["PL"]))
    return {"nbin": int(len(t["Om"])), "nf": int(len(t["f"])), "f": np.round(t["f"], 3).tolist(), "om": t["Om"].tolist(),
            "be": t["BE"].tolist(), "scale": sc,
            "xr": b64(t["X"].real / sc), "xi": b64(t["X"].imag / sc), "pl": b64(t["PL"] / sc), "pr": b64(t["PR"] / sc)}


def main(cfg_path="config.json"):
    cfg = bp.load_config(cfg_path)
    out, fs = cfg["output_dir"], cfg["fs"]
    srcs, recs = bp.source_names(cfg), bp.receiver_names(cfg)

    hr = bp.load_hrir(cfg["binaural"]["sofa_path"], fs)          # full set, for diffuse-field gains
    fb = bp.octave_filterbank(fs)
    room = bp.make_room(cfg, 1)

    rows = []
    p = os.path.join(out, "conditions.csv")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))


    def kind(k):
        return "amp" if k == bp.AMP else "pa" if k in ("B_L", "B_R") else "unamp"

    data = {
        "version": VERSION, "fs": fs, "c": cfg["c"], "nLate": int(LATE_SECONDS * fs),
        "hall": {"dims": cfg["room"]["dims_m"], "stage": cfg["room"].get("stage_depth_m", 5.0),
                 "alphaBands": cfg["room"]["absorption_octave"]["_bands_hz"],
                 "alpha": cfg["room"]["absorption_octave"]["values"]},
        "praBands": room.octave_bands.centers.tolist(),
        "air": np.round(np.asarray(room.air_absorption), 6).tolist(),
        "bankEdges": [[float(lo), float(hi)] for lo, hi in fb["edges"]],
        "df": np.round(hr.df_band_energy, 6).tolist(),
        "coh": {"f": np.round(hr.coh_f, 2).tolist(), "g": np.round(hr.coh, 4).tolist()},
        "ismOrder": cfg["binaural"]["ism_order_early"], "omniOrder": cfg["binaural"]["ism_order_omni"],
        "earlyMs": cfg["binaural"]["early_window_ms"], "xfadeMs": cfg["binaural"]["crossfade_ms"],
        "sources": [{"id": k, "kind": kind(k), "pos": cfg["sources"][k]["pos"],
                     "label": cfg["sources"][k].get("label", ""),
                     **({"dir": dir_spec(cfg, k, room.octave_bands.centers)} if kind(k) == "pa" or cfg["sources"][k].get("directivity") else {})}
                    for k in srcs],
        "receivers": {r: cfg["receivers"][r] for r in recs},
        "ref": cfg["conditions"]["reference_receiver"],
        "itdg": cfg["conditions"]["itdg_ms"], "lr": cfg["conditions"]["level_ratio_db"],
        "hrir": hrir_subset(cfg["binaural"]["sofa_path"], fs),
        "rows": rows,
        "scattering": cfg["room"].get("scattering", 0.1),
        "hpcf": hpcf_data(cfg),
        "geometry": cfg.get("geometry"),
        "name": cfg.get("name", ""),
        "config": cfg,
        "configFile": os.path.basename(cfg_path),
        "seatMap": (cfg.get("seats") or {}).get("xyz"),
        "lateDir": late_tables(hr) if cfg["binaural"].get("late_directional", True) else None,
    }
    with open(os.path.join(HERE, "viewer_template.html"), encoding="utf-8") as f:
        html = f.read()
    html = html.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    with open(os.path.join(HERE, "engine_geom.js"), encoding="utf-8") as f:
        html = html.replace("/*__GEOM__*/", f.read())
    path = os.path.join(out, "viewer.html")
    os.makedirs(out, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:  # standalone file, opens with a double-click
        f.write('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
                '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
                'body{margin:0}[hidden]{display:none!important}</style></head><body>\n')
        f.write(html)
        f.write("\n</body></html>\n")
    if os.environ.get("AURALPATHS_FRAGMENT"):  # fragment for publishing as a web page
        with open(os.environ["AURALPATHS_FRAGMENT"], "w", encoding="utf-8") as f:
            f.write(html)
    print(f"{path} ({os.path.getsize(path) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main(*(sys.argv[1:] or ["config.json"]))
