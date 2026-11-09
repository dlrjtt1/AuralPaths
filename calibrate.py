"""
Material calibration from measured reverberation times.

    python calibrate.py <config.json> <measurements.csv> [--adjust aud,wall,ceil] [--source-directivity file.csv]
                        [--out calibrated_config.json] [--tol 0.02] [--iter 10]

measurements.csv (one row per position pair and octave band; EDT optional, used for checking only):
    label,src_x,src_y,src_z,rec_x,rec_y,rec_z,band_hz,T30_s,EDT_s

Method: per octave band (125 Hz - 4 kHz, or up to 16 kHz when the measurement file has 8 kHz / 16 kHz rows), one factor k_b scales the absorption coefficients of the adjustable
material groups (drawn hall: aud / stage / wall / ceil; OBJ mesh hall: its material keys; shoebox: the uniform
coefficient), so that the simulated T30, averaged over the calibration positions, matches the measured average.
Sabine scaling is used as the update:
k <- k * T_sim / T_meas (more absorption, shorter decay), until every band is within --tol (default 2 %, below the
5 % just-noticeable difference of reverberation given in ISO 3382-1 Annex A) or --iter iterations. Coefficients are
kept within 0.01 ... 0.95. Groups not listed in --adjust keep their values (e.g. a stage floor whose material is known).

This fits one number per band. It cannot tell which surface is wrong; several material sets can give the same T30.
Use positions for calibration that are not used for validation (proposal section 3.1).

Output: the calibrated config (materials replaced, a "_calibration" record added) and a report next to it
(<out>_report.csv / .md): measured, simulated before and after, per band and position.
"""
import argparse
import copy
import csv
import datetime
import hashlib
import json
import os
import sys

import numpy as np

import brir_proto as bp

ALL_BANDS = [125, 250, 500, 1000, 2000, 4000, 8000, 16000]
BANDS = ALL_BANDS[:6]   # replaced in main() by the bands present in the measurement file (125 Hz - 4 kHz or up to 16 kHz)
JND_T = 0.05          # ISO 3382-1 Annex A: 5 % (EDT); used here as the tolerance scale for reverberation time


def read_measurements(path):
    lines = [l for l in open(path, encoding="utf-8") if l.strip() and not l.lstrip().startswith("#")]
    rows = list(csv.DictReader(lines))
    if not rows:
        sys.exit(f"{path}: no rows")
    pos = {}
    for r in rows:
        lab = r["label"].strip()
        p = pos.setdefault(lab, {"src": [float(r["src_x"]), float(r["src_y"]), float(r["src_z"])],
                                 "rec": [float(r["rec_x"]), float(r["rec_y"]), float(r["rec_z"])], "T30": {}, "EDT": {}})
        b = int(round(float(r["band_hz"])))
        if r.get("T30_s", "").strip():
            p["T30"][b] = float(r["T30_s"])
        if r.get("EDT_s", "").strip():
            p["EDT"][b] = float(r["EDT_s"])
    return pos


def simulate(cfg, pos, src_dir):
    """Simulated T30 and EDT per band for every calibration position (omni receiver, energy histogram)."""
    out = {}
    if bp.is_mesh(cfg):
        # OBJ mesh halls: one ray-tracing run per source position shared by all its receivers (energy_hists); a run
        # per position pair would take minutes to hours each on a mesh of thousands of faces
        c = copy.deepcopy(cfg)
        srcs = {}
        for lab, p in pos.items():
            srcs.setdefault(tuple(p["src"]), []).append(lab)
        c["sources"] = {f"CAL_S{i}": {"pos": list(s), **({"directivity": src_dir} if src_dir else {})}
                        for i, s in enumerate(srcs)}
        c["receivers"] = {f"CAL_R_{lab}": pos[lab]["rec"] for lab in pos}
        for i, (s, labs) in enumerate(srcs.items()):
            H, centers = bp.energy_hists(c, f"CAL_S{i}", [f"CAL_R_{lab}" for lab in labs])
            for lab in labs:
                t0 = np.linalg.norm(np.subtract(pos[lab]["src"], pos[lab]["rec"])) / c["c"]
                out[lab] = {}
                for b in BANDS:
                    m = bp.iso3382_energy([(H[f"CAL_R_{lab}"], 0.0, 1.0)], t0, bands=(b,), centers=centers)
                    out[lab][b] = (m["T30"], m["EDT"])
        return out
    for lab, p in pos.items():
        c = copy.deepcopy(cfg)
        c["sources"] = {"CAL_S": {"pos": p["src"], **({"directivity": src_dir} if src_dir else {})}}
        c["receivers"] = {"CAL_R": p["rec"]}
        hist, centers = bp.energy_hist(c, "CAL_S", "CAL_R")
        t0 = np.linalg.norm(np.subtract(p["src"], p["rec"])) / c["c"]
        out[lab] = {}
        for b in BANDS:
            m = bp.iso3382_energy([(hist, 0.0, 1.0)], t0, bands=(b,), centers=centers)
            out[lab][b] = (m["T30"], m["EDT"])
    return out


def get_alpha(cfg, groups):
    if bp.has_geometry(cfg):
        return {g: _pad(cfg["geometry"]["materials"][g]["alpha"]) for g in groups}
    return {"room": _pad(cfg["room"]["absorption_octave"]["values"])}


def _pad(a):
    """Coefficients for the calibrated bands; missing high bands repeat the last value (as the engine does)."""
    a = list(a)
    return np.array([a[i] if i < len(a) else a[-1] for i in range(len(BANDS))], float)


def set_alpha(cfg, base, k):
    c = copy.deepcopy(cfg)
    for g, a in base.items():
        new = np.clip(a * k, 0.01, 0.95).round(4).tolist()
        if g == "room":
            c["room"]["absorption_octave"]["values"] = new
        else:
            c["geometry"]["materials"][g]["alpha"] = new
    return c


def mean_sim(sim, key_i, bands):
    return np.array([np.nanmean([sim[l][b][key_i] for l in sim]) for b in bands])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config"); ap.add_argument("measurements")
    ap.add_argument("--adjust", default="", help="material groups to scale (default: all)")
    ap.add_argument("--source-directivity", default=None, help="directivity CSV / SOFA of the measurement source")
    ap.add_argument("--out", default=None); ap.add_argument("--tol", type=float, default=0.02); ap.add_argument("--iter", type=int, default=10)
    a = ap.parse_args()

    cfg = bp.load_config(a.config)
    pos = read_measurements(a.measurements)
    global BANDS
    present = {b for p in pos.values() for b in p["T30"]}
    BANDS = ALL_BANDS[:8] if {8000, 16000} <= present else ALL_BANDS[:6]
    meas_T = np.array([np.nanmean([p["T30"].get(b, np.nan) for p in pos.values()]) for b in BANDS])
    if np.all(np.isnan(meas_T)):
        sys.exit("no T30 values in the measurement file")
    groups = list(cfg["geometry"]["materials"]) if bp.has_geometry(cfg) else ["room"]
    if a.adjust:
        groups = [g.strip() for g in a.adjust.split(",") if g.strip()]
        bad = [g for g in groups if bp.has_geometry(cfg) and g not in cfg["geometry"]["materials"]]
        if bad:
            sys.exit(f"unknown material group(s): {bad}; available: {list(cfg['geometry']['materials'])}")
    base = get_alpha(cfg, groups)
    k = np.ones(len(BANDS))
    print(f"Calibrating {', '.join(base)} on {len(pos)} position(s); measured mean T30: " +
          ", ".join(f"{b}: {t:.2f}" for b, t in zip(BANDS, meas_T)))

    sim0 = simulate(cfg, pos, a.source_directivity)
    history, sim, cur = [], sim0, cfg
    for it in range(a.iter):
        T = mean_sim(sim, 0, BANDS)
        err = T / meas_T - 1
        history.append((it, k.copy(), T.copy()))
        print(f"  iteration {it}: T30 sim " + ", ".join(f"{t:.2f}" for t in T) + "  | error % " + ", ".join(f"{100 * e:+.1f}" for e in err))
        ok = np.isnan(err) | (np.abs(err) <= a.tol)
        if ok.all():
            break
        step = np.where(np.isnan(err), 1.0, T / meas_T)
        k = np.where(ok, k, k * step)
        cur = set_alpha(cfg, base, k)
        sim = simulate(cur, pos, a.source_directivity)
    T1 = mean_sim(sim, 0, BANDS)

    out = a.out or os.path.splitext(a.config)[0] + "_calibrated.json"
    raw = json.load(open(a.config, encoding="utf-8"))
    cal = set_alpha(raw, base, k)
    cal["_calibration"] = {
        "date": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "measurements": os.path.basename(a.measurements),
        "measurements_sha256": hashlib.sha256(open(a.measurements, "rb").read()).hexdigest(),
        "positions": list(pos), "adjusted_groups": list(base), "bands_hz": BANDS,
        "factors": [round(float(x), 4) for x in k],
        "T30_measured_mean_s": [None if np.isnan(x) else round(float(x), 3) for x in meas_T],
        "T30_sim_before_s": [round(float(x), 3) for x in mean_sim(sim0, 0, BANDS)],
        "T30_sim_after_s": [round(float(x), 3) for x in T1],
        "source_directivity": a.source_directivity,
        "note": "one absorption factor per octave band on the adjusted groups; see calibrate.py",
    }
    if any(np.isclose(np.clip(base[g] * k, 0.01, 0.95), [0.01, 0.95][j]).any() for g in base for j in (0, 1)):
        cal["_calibration"]["warning"] = "some coefficients hit the 0.01 / 0.95 limit: the geometry or the material groups may be wrong"
    json.dump(cal, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # report
    stem = os.path.splitext(out)[0]
    rep = []
    for lab, p in pos.items():
        for b in BANDS:
            rep.append({"position": lab, "band_hz": b, "T30_meas": p["T30"].get(b, ""), "T30_before": round(sim0[lab][b][0], 3),
                        "T30_after": round(sim[lab][b][0], 3), "EDT_meas": p["EDT"].get(b, ""),
                        "EDT_before": round(sim0[lab][b][1], 3), "EDT_after": round(sim[lab][b][1], 3)})
    with open(stem + "_report.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rep[0])); w.writeheader(); w.writerows(rep)
    T0 = mean_sim(sim0, 0, BANDS)
    lines = [f"# Calibration report: {os.path.basename(a.config)}", "",
             f"Measurements: {os.path.basename(a.measurements)} ({len(pos)} position(s)); adjusted: {', '.join(base)}; "
             f"tolerance {100 * a.tol:.0f} % (JND of reverberation 5 %, ISO 3382-1 Annex A)", "",
             "| band (Hz) | T30 measured (s) | sim before (s) | error before | sim after (s) | error after | factor |", "|---|---|---|---|---|---|---|"]
    for i, b in enumerate(BANDS):
        lines.append(f"| {b} | {meas_T[i]:.2f} | {T0[i]:.2f} | {100 * (T0[i] / meas_T[i] - 1):+.1f} % | {T1[i]:.2f} | {100 * (T1[i] / meas_T[i] - 1):+.1f} % | {k[i]:.3f} |")
    eds = [(lab, b) for lab, p in pos.items() for b in BANDS if b in p["EDT"]]
    if eds:
        e0 = [100 * (sim0[l][b][1] / pos[l]["EDT"][b] - 1) for l, b in eds]
        e1 = [100 * (sim[l][b][1] / pos[l]["EDT"][b] - 1) for l, b in eds]
        lines += ["", f"EDT (not fitted, check only): mean |error| {np.nanmean(np.abs(e0)):.1f} % before, {np.nanmean(np.abs(e1)):.1f} % after "
                  f"({len(eds)} values)."]
    if "warning" in cal["_calibration"]:
        lines += ["", "**Warning:** " + cal["_calibration"]["warning"]]
    lines += ["", "One factor per band cannot identify which surface is wrong. Validate at positions not used here."]
    open(stem + "_report.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"-> {out}\n-> {stem}_report.csv, {stem}_report.md")


if __name__ == "__main__":
    main()
