"""
Room-criteria check of the Python engine against measured halls: the Fratoni dataset (Mendeley Data,
https://doi.org/10.17632/y7xnv6xg5s.1, CC BY 4.0). Two of its four rooms fit AuralPaths: ULH (raked university
lecture hall, about 900 m3) and STC (elliptical concert hall with domed ceiling, about 950 m3).

    python validate_fratoni.py <dataset folder> ULH|STC --obj <hall.obj> [--rays 50000] [--max-faces 3000]
                               [--out validation/fratoni_ULH] [--no-2p5d | --no-3d] [--min-scatter s]
                               [--stc-doors Wood] [--preserve eyring|sabine]
    python validate_fratoni.py --replot validation/fratoni_ULH.csv      (figure only, from saved results)

The data are not included. The 3D models in the dataset are SketchUp files; export each as OBJ with the
SketchUp tags kept as groups (e.g. Blender + a SketchUp importer, File > Export > Wavefront OBJ with
"Object Groups" and "Material Groups" on) and pass the file with --obj. The script reads, from the dataset folder:
    <n>_<HALL>/Boundary conditions/<HALL>_Boundary_conditions.xlsx  (absorption and scattering used in the
        authors' geometrical-acoustics (GA) calibration, octave bands 63 Hz - 8 kHz)
    <n>_<HALL>/Measurements results/<HALL>_Room_Criteria.xlsx       (measured ISO 3382-1 criteria, averaged over
        the receivers listed per source, octave bands 125 Hz - 4 kHz)

What is compared: for each source, the engine's energy histograms (image sources to order 1 plus pyroomacoustics
ray tracing, brir_proto.energy_hists) at every listed receiver give EDT, T30, C80 or C50 and Ts per octave band;
these are averaged over the receivers (arithmetic mean, as in the measured sheets) and compared with the
measurement, in units of the just noticeable difference (JND) of ISO 3382-1 Annex A: 5 % for EDT and T30, 1 dB
for C80 / C50, 10 ms for Ts. The same is done for the drawn 2.5D hall made from the OBJ (obj_to_hall.py), which is
what the browser page runs.

Source and receiver positions are not in the dataset as numbers; they were read from the position figures in
the Room_Criteria sheets (plan for x / y, section for heights), so each is uncertain by about +- 0.3 m. The
material of each OBJ group is set below (VENUES); for STC the dataset's tags do not match its material list one to
one and the mapping is a judgement (see the notes there). The absorption values were calibrated by the dataset's
authors for a different GA program (Odeon); they are used unchanged here, so the comparison tests this engine with
the authors' inputs, not a calibration of this engine.
"""
import argparse
import csv
import glob
import json
import os
import re
import sys
import time

import numpy as np

import brir_proto as bp

BANDS = [125, 250, 500, 1000, 2000, 4000]
JND = {"EDT": ("rel", 0.05), "T30": ("rel", 0.05), "C80": ("abs", 1.0), "C50": ("abs", 1.0), "Ts": ("abs", 10.0)}

# Positions in metres in the engine's mesh frame (x = OBJ x, y = -OBJ z, z = OBJ y, i.e. Blender's y-up OBJ).
# ULH: plan figure scale 81.4 px/m fitted to the two window pillars; heights from the section figure (receiver
# dots above the seat rows; sources 1.55 m). R3/R4, R7/R8, ... share the height of the receiver shown in the section
# in the same row of seats.
ULH_ROWS = {1: 1.72, 2: 2.13, 3: 2.76, 4: 3.29, 5: 3.93, 6: 4.52, 7: 4.97}
ULH_POS = {   # name: (x, y, row)
    "R1": (3.26, 11.06, 1), "R2": (3.85, 7.57, 1), "R3": (3.85, 5.54, 1), "R4": (3.56, 2.21, 1),
    "R5": (4.66, 11.06, 2), "R6": (5.25, 7.57, 2), "R7": (5.25, 5.54, 2), "R8": (4.96, 2.21, 2),
    "R9": (6.06, 11.06, 3), "R10": (6.65, 7.57, 3), "R11": (6.65, 5.54, 3), "R12": (6.36, 2.21, 3),
    "R13": (7.46, 11.06, 4), "R14": (8.05, 7.33, 4), "R15": (8.05, 5.31, 4), "R16": (7.76, 2.21, 4),
    "R17": (8.86, 11.06, 5), "R18": (9.45, 7.33, 5), "R19": (9.45, 5.31, 5), "R20": (9.16, 2.21, 5),
    "R21": (10.26, 11.06, 6), "R22": (10.88, 7.33, 6), "R23": (10.88, 5.31, 6),
    "R24": (11.50, 11.52, 7), "R25": (12.29, 7.33, 7), "R26": (12.29, 5.31, 7),
}
# STC: plan figure 107.4 px/m along the major axis, 109.5 px/m across, centred on the ellipse; heights from the
# longitudinal section (main floor at z = 0: seat level receivers 1.23 m, first tier 1.69 m, second tier 2.12 m;
# S1 on the stage 1.92 m; S2 is not in the section and is set to 1.5 m). R2 is hidden under the S2 symbol in the
# plan and is placed there, at the height of R3 (mirror position).
STC_POS = {
    "R1": (0.0, 9.08, 1.23), "R2": (2.12, 9.08, 1.23), "R3": (-2.15, 9.10, 1.23), "R4": (-3.64, 9.10, 1.69),
    "R5": (-4.72, 9.08, 2.12), "R6": (-4.45, 6.37, 2.12), "R7": (-3.42, 6.38, 1.69), "R8": (-1.78, 6.35, 1.23),
    "R9": (0.0, 6.33, 1.23), "R10": (0.0, 11.81, 1.23),
}

VENUES = {
    "ULH": dict(
        folder="4_ULH", tag="ULH",
        # the four SketchUp tags are the four materials of the boundary-condition sheet
        groups={"Plaster": "Plaster", "Wood": "Wood", "Windows": "Windows", "Seats": "Seats"},
        sources={"S1": (0.93, 6.57, 1.55), "S2": (2.53, 9.64, 1.55)},
        receivers={k: (x, y, ULH_ROWS[r]) for k, (x, y, r) in ULH_POS.items()},
        depth_axis="x", stage_end="min", stage_depth=2.4),
    "STC": dict(
        folder="3_STC", tag="STC",
        # tags vs materials: shell_sidewalls holds walls and the lower vaults -> split by orientation into
        # "Plasterboard (walls)" and "Ceiling"; crown (upper dome) -> Ceiling; seat-cushion -> Seats;
        # seats-wood_stage -> Wood; floor -> Wood (the sheet has no floor material); doors_organ -> Furniture
        # (the sensitivity run --stc-doors Wood swaps it). These are the author's (AuralPaths) assignments.
        groups={"shell_sidewalls": {"wall": "Plasterboard (walls)", "ceiling": "Ceiling", "floor": "Plasterboard (walls)"},
                "crown": "Ceiling", "seat-cushion": "Seats", "seats-wood": "Wood", "floor": "Wood",
                "doors_organ": "Furniture"},
        sources={"S1": (0.0, 2.45, 1.92), "S2": (2.12, 9.15, 1.5)},
        receivers=STC_POS,
        depth_axis="y", stage_end="min", stage_depth=0.0),
}


# ---------------------------------------------------------------- dataset sheets
def read_boundary(path):
    """{material: {"alpha": [125 .. 4000 Hz], "s": scattering}} from the GA block of the sheet."""
    import openpyxl
    rows = [r for r in openpyxl.load_workbook(path, data_only=True).active.iter_rows(values_only=True)]
    start = next(i for i, r in enumerate(rows) if r[0] and str(r[0]).startswith("Absorption coefficients employed in GA"))
    hdr = rows[start + 1]
    hz = [int(str(c).split()[0]) for c in hdr if c and str(c).strip().endswith("Hz")]
    out = {}
    for r in rows[start + 2:]:
        if not r[0]:
            break
        vals = [v for v in r[1:] if isinstance(v, (int, float))]
        a = dict(zip(hz, vals[:len(hz)]))
        out[str(r[0]).strip()] = {"alpha": [float(a[b]) for b in BANDS], "s": float(vals[len(hz)])}
    return out


def read_criteria(path):
    """[{source, receivers (list or None = all), metrics {name: [6 bands]}, single {name: value}}]."""
    import openpyxl
    rows = [r for r in openpyxl.load_workbook(path, data_only=True).active.iter_rows(values_only=True)]
    blocks, cur = [], None
    for r in rows:
        c = [x for x in r if x is not None]
        if not c:
            continue
        if c[0] == "Sound Source":
            cur = {"source": str(c[1]).strip(), "receivers": None, "metrics": {}, "single": {}}
            blocks.append(cur)
        elif c[0] == "Receivers" and cur is not None:
            txt = str(c[1])
            nums = re.findall(r"R\s*(\d+)", txt)
            cur["receivers"] = [f"R{n}" for n in nums] if nums else None
            cur["receivers_text"] = txt.strip()
        elif cur is not None and isinstance(c[0], str) and len(c) == 7:
            name = c[0].strip().replace("Ts", "Ts")
            cur["metrics"][name] = [float(v) for v in c[1:7]]
        elif cur is not None and isinstance(c[0], str) and len(c) == 2:
            cur["single"][c[0].strip()] = float(c[1])
    return blocks


def height_above(G, p):
    """Distance from p straight down to the first room-facing mesh face."""
    p = np.asarray(p, float)
    best = np.inf
    for s in G["S"]:
        if s["kind"] != "mesh" or s["n"][2] <= 0.1:
            continue
        v = s["verts"]
        if not (v[:, 0].min() <= p[0] <= v[:, 0].max() and v[:, 1].min() <= p[1] <= v[:, 1].max()):
            continue
        n = s["n"]
        z = v[0][2] - (n[0] * (p[0] - v[0][0]) + n[1] * (p[1] - v[0][1])) / n[2]
        if z > p[2] + 1e-6:
            continue
        import diffraction
        if "uv" not in s:
            diffraction.prepare({"S": [s]})
        if diffraction.in_surface(s, np.array([p[0], p[1], z])):
            best = min(best, p[2] - z)
    return best


# ---------------------------------------------------------------- criteria from energy histograms
def criteria(h, t0, bin_s=bp.HIST_BIN):
    """EDT, T30, C80, C50, Ts per band from energy histograms h [n_bands, n_bins] (direct sound at t0)."""
    out = {k: [] for k in ("EDT", "T30", "C80", "C50", "Ts")}
    i0 = int(np.floor(t0 / bin_s))
    for e in h:
        e = np.asarray(e[i0:], float)
        tot = e.sum()
        t = (np.arange(len(e)) + 0.5) * bin_s
        n50, n80 = int(round(0.05 / bin_s)), int(round(0.08 / bin_s))
        out["C80"].append(10 * np.log10(e[:n80].sum() / e[n80:].sum()))
        out["C50"].append(10 * np.log10(e[:n50].sum() / e[n50:].sum()))
        out["Ts"].append(1000 * np.sum(t * e) / tot)
        edc = 10 * np.log10(np.maximum(np.cumsum(e[::-1])[::-1] / tot, 1e-30))
        for name, hi, lo in (("EDT", 0, -10), ("T30", -5, -35)):
            sel = (edc <= hi) & (edc >= lo)
            out[name].append(-60 / np.polyfit(t[sel], edc[sel], 1)[0] if sel.sum() > 10 and edc.min() < lo - 10 else np.nan)
    return {k: np.array(v) for k, v in out.items()}


def simulate(cfg, plan, rays, label, log):
    """{source: {metric: [6]} mean over its receivers} and per-receiver values."""
    res, per = {}, []
    for s, recs in plan.items():
        t = time.time()
        H, cen = bp.energy_hists(cfg, s, recs, t_max=3.0, n_rays=rays)
        bi = [int(np.argmin(np.abs(np.asarray(cen) - b))) for b in BANDS]
        vals = []
        for r in recs:
            d = np.linalg.norm(np.subtract(cfg["receivers"][r], cfg["sources"][s]["pos"]))
            m = criteria(H[r][bi], d / cfg["c"])
            vals.append(m)
            per.append(dict(model=label, source=s, receiver=r, **{f"{k}_{b}": round(float(m[k][j]), 3)
                                                                   for k in m for j, b in enumerate(BANDS)}))
        res[s] = {k: np.nanmean([v[k] for v in vals], axis=0) for k in vals[0]}
        log(f"[{label}] {s}: {len(recs)} receivers, {time.time() - t:.0f} s")
    return res, per


def jnd_units(name, sim, meas):
    kind, j = JND[name]
    return (sim - meas) / (j * meas) if kind == "rel" else (sim - meas) / j


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dataset")
    ap.add_argument("hall", choices=sorted(VENUES))
    ap.add_argument("--obj", required=True)
    ap.add_argument("--rays", type=int, default=50000)
    ap.add_argument("--max-faces", type=int, default=3000, help="decimate larger meshes (fast-simplification)")
    ap.add_argument("--ism-order", type=int, default=1)
    ap.add_argument("--stc-doors", default="Furniture", help="material of the STC doors_organ tag (sensitivity)")
    ap.add_argument("--no-2p5d", action="store_true")
    ap.add_argument("--no-3d", action="store_true", help="run only the 2.5D hall (quick)")
    ap.add_argument("--min-scatter", type=float, default=0.0,
                    help="sensitivity run: raise every scattering coefficient to at least this value")
    ap.add_argument("--preserve", default="eyring", choices=["eyring", "sabine", "room-eyring"], help="see obj_to_hall.py")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    V = VENUES[a.hall]
    out = a.out or os.path.join("validation", f"fratoni_{a.hall}")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    lines = []

    def log(msg):
        print(msg, flush=True)
        lines.append(msg)

    base = os.path.join(a.dataset, V["folder"])
    mats = read_boundary(glob.glob(os.path.join(base, "Boundary conditions", "*.xlsx"))[0])
    blocks = read_criteria(glob.glob(os.path.join(base, "Measurements results", "*.xlsx"))[0])
    if a.min_scatter > 0:
        for m in mats.values():
            m["s"] = max(m["s"], a.min_scatter)
        log(f"sensitivity run: scattering raised to at least {a.min_scatter}")
    groups = json.loads(json.dumps(V["groups"]))
    if a.hall == "STC":
        groups["doors_organ"] = a.stc_doors
    cfg = {"name": f"Fratoni {a.hall}", "fs": 48000, "c": 343.0,
           "room": {"air_absorption": True, "dims_m": [1, 1, 1], "stage_depth_m": 0.0},
           "binaural": {"late_directional": False},
           "sources": {k: {"pos": list(v)} for k, v in V["sources"].items()},
           "receivers": {k: list(v) for k, v in V["receivers"].items()},
           "geometry": {"mesh": {"obj": a.obj, "groups": groups, "max_faces": a.max_faces},
                        "materials": mats, "ism_order": a.ism_order, "rays": a.rays, "diffraction": False}}
    G = bp._geom(cfg)
    log(f"{a.hall}: OBJ {G['n_input']} faces -> {G['n_faces']} after decimation -> {sum(1 for s in G['S'] if s['kind'] == 'mesh')} "
        f"room-facing faces ({G['n_dropped']} hidden faces dropped), {len(G['S'])} walls incl. back faces; "
        f"room volume (voxels) {G['volume']:.0f} m3")
    area = G["area"]
    S_tot = sum(area.values())
    A = {b: sum(mats[k]["alpha"][i] * area[k] for k in area) for i, b in enumerate(BANDS)}
    sab = {b: 0.161 * G["volume"] / A[b] for b in BANDS}
    log("surface areas (m2): " + ", ".join(f"{k} {v:.1f}" for k, v in sorted(area.items())) + f"; total {S_tot:.0f}")
    log("Sabine T (s), no air: " + ", ".join(f"{b} Hz {sab[b]:.2f}" for b in BANDS))
    plan = {}
    for blk in blocks:
        s = blk["source"]
        if s not in cfg["sources"]:
            continue
        plan[s] = blk["receivers"] or sorted(cfg["receivers"], key=lambda r: int(r[1:]))
    import geometry
    for s in plan:                                                    # position sanity
        for p in [cfg["sources"][s]["pos"]] + [cfg["receivers"][r] for r in plan[s]]:
            if not geometry.inside(G, p):
                raise SystemExit(f"position {p} is not inside the room model")
    log("height above the surface below (m): " + ", ".join(
        f"{k} {height_above(G, cfg['sources'][k]['pos'] if k in cfg['sources'] else cfg['receivers'][k]):.2f}"
        for k in list(plan) + sorted({r for v in plan.values() for r in v}, key=lambda r: int(r[1:]))))
    res3, per3 = (None, []) if a.no_3d else simulate(cfg, plan, a.rays, "3D mesh", log)
    res25, per25, rep25 = None, [], None
    if not a.no_2p5d:
        import obj_to_hall
        cfg25, rep25 = obj_to_hall.convert(cfg, V["depth_axis"], V["stage_end"], V["stage_depth"],
                                          preserve=a.preserve)
        cfg25["geometry"].update(ism_order=a.ism_order, rays=a.rays, diffraction=False)
        G25 = bp._geom(cfg25)
        import geometry
        moved = []
        for k in list(cfg25["receivers"]) + list(cfg25["sources"]):
            is_src = k in cfg25["sources"]
            p = cfg25["sources"][k]["pos"] if is_src else cfg25["receivers"][k]
            if not geometry.inside(G25, p):          # below the averaged floor: lift to 0.4 m above it
                z = geometry.prof_at(G25["floor"], p[1]) + 0.4
                moved.append(f"{k} {p[2]:.2f}->{z:.2f}")
                p[2] = round(z, 3)
        rep25["volume_2p5d_m3"] = round(obj_to_hall.volume_2p5d(cfg25["geometry"], 50000), 1)
        log(f"2.5D hall: {rep25['n_plan_vertices']} plan vertices, {rep25['n_surfaces_2p5d']} surfaces, volume "
            f"{rep25['volume_2p5d_m3']} m3 (mesh {rep25['volume_mesh_m3']}); positions lifted above the averaged floor: "
            + (", ".join(moved) if moved else "none"))
        with open(out + "_2p5d_config.json", "w", encoding="utf-8") as f:
            json.dump({k: v for k, v in cfg25.items()}, f, ensure_ascii=False, indent=1)
        res25, per25 = simulate(cfg25, plan, a.rays, "2.5D", log)

    # ---------------------------------------------------------------- tables, csv, figure
    rows = []
    md = [f"# Fratoni {a.hall}: measured vs AuralPaths (Python engine)", "",
          "Data: G. Fratoni, *Materials for calibrating four complex virtual environments through acoustic simulations*, "
          "Mendeley Data, https://doi.org/10.17632/y7xnv6xg5s.1 (CC BY 4.0). Measured values: the dataset's Room_Criteria "
          "sheet (mean over the listed receivers). Inputs: the dataset's GA absorption / scattering, unchanged.", "",
          "```", *lines, "```", ""]
    for blk in blocks:
        s = blk["source"]
        if s not in plan:
            continue
        md += [f"## {s}, receivers: {blk.get('receivers_text', 'all')} ({len(plan[s])})", "",
               "| criterion | model | " + " | ".join(f"{b} Hz" for b in BANDS) + " | mean abs (JND) 500-1k | mean abs (JND) all |",
               "|---|---|" + "---|" * len(BANDS) + "---|---|"]
        for name, meas in blk["metrics"].items():
            key = name.replace(" ", "")
            if key not in JND:
                continue
            md.append(f"| {name} | measured | " + " | ".join(f"{v:.2f}" if key not in ("Ts",) else f"{v:.0f}" for v in meas) + " | | |")
            for label, res in (("3D mesh", res3), ("2.5D", res25)):
                if res is None:
                    continue
                sim = res[s][key]
                j = jnd_units(key, sim, np.asarray(meas))
                md.append(f"| | {label} | " + " | ".join((f"{v:.2f}" if key != "Ts" else f"{v:.0f}") + f" ({d:+.1f})"
                                                          for v, d in zip(sim, j)) +
                          f" | {np.nanmean(np.abs(j[2:4])):.1f} | {np.nanmean(np.abs(j)):.1f} |")
                for b, mv, sv, dj in zip(BANDS, meas, sim, j):
                    rows.append(dict(hall=a.hall, source=s, criterion=key, band_hz=b, model=label, measured=mv,
                                     simulated=round(float(sv), 3), diff_jnd=round(float(dj), 2)))
        md.append("")
        if blk["single"]:
            md.append("Not compared: " + ", ".join(f"{k} = {v}" for k, v in blk["single"].items()) + "")
            md.append("")
    md += ["Values in brackets: simulated - measured in JND (ISO 3382-1 Annex A: EDT / T30 5 %, C80 / C50 1 dB, Ts 10 ms).", ""]
    if rep25:
        md += [f"2.5D conversion (obj_to_hall.py, --preserve {a.preserve}):", "", "```",
               json.dumps(rep25, indent=1), "```", ""]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    with open(out + ".csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    with open(out + "_receivers.csv", "w", newline="", encoding="utf-8") as f:
        allp = per3 + per25
        w = csv.DictWriter(f, fieldnames=list(allp[0])); w.writeheader(); w.writerows(allp)
    plot(blocks, plan, res3, res25, a.hall, out + ".png")
    print("->", out + ".md", out + ".csv", out + ".png")


def replot(csv_path):
    """Redraw the figure from a results csv written by this script (no simulation)."""
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    hall = rows[0]["hall"]
    srcs = list(dict.fromkeys(r["source"] for r in rows))
    blocks, res = [], {"3D mesh": {}, "2.5D": {}}
    for s in srcs:
        b = {"source": s, "metrics": {}}
        for r in rows:
            if r["source"] != s:
                continue
            i = BANDS.index(int(float(r["band_hz"])))
            b["metrics"].setdefault(r["criterion"], [np.nan] * 6)[i] = float(r["measured"])
            res[r["model"]].setdefault(s, {}).setdefault(r["criterion"], np.full(6, np.nan))[i] = float(r["simulated"])
        blocks.append(b)
    plan = {s: [] for s in srcs}
    plot(blocks, plan, res["3D mesh"] or None, res["2.5D"] or None, hall, os.path.splitext(csv_path)[0] + ".png")


def plot(blocks, plan, res3, res25, hall, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    blks = [b for b in blocks if b["source"] in plan]
    names = [n for n in ("EDT", "T30", "C80", "C50", "Ts") if any(n in b["metrics"] for b in blks)]
    fig, axs = plt.subplots(len(blks), len(names), figsize=(3.3 * len(names), 2.9 * len(blks)), squeeze=False)
    for i, b in enumerate(blks):
        s = b["source"]
        for j, n in enumerate(names):
            ax = axs[i][j]
            if n not in b["metrics"]:
                ax.axis("off")
                continue
            meas = np.asarray(b["metrics"][n])
            kind, jv = JND[n]
            band = jv * meas if kind == "rel" else np.full(6, jv)
            ax.fill_between(range(6), meas - band, meas + band, color="0.88", label="measured +- 1 JND")
            ax.plot(range(6), meas, "k-o", ms=3, lw=1.4, label="measured")
            if res3 is not None:
                ax.plot(range(6), res3[s][n], "-s", color="#c2571a", ms=3, lw=1.2, label="3D mesh")
            if res25 is not None:
                ax.plot(range(6), res25[s][n], "--^", color="#2a6fb0", ms=3, lw=1.2, label="2.5D")
            ax.set_xticks(range(6)); ax.set_xticklabels(["125", "250", "500", "1k", "2k", "4k"], fontsize=8)
            ax.set_title(f"{s}: {n} ({'s' if n in ('EDT', 'T30') else 'dB' if n.startswith('C') else 'ms'})", fontsize=9)
            ax.grid(alpha=0.3)
    h, l = axs[0][0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=len(l), fontsize=8, frameon=False)
    fig.suptitle(f"Fratoni {hall}: measured (receiver mean) vs AuralPaths Python engine, dataset GA inputs unchanged", fontsize=10)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--replot":
        replot(sys.argv[2])
    else:
        main()
