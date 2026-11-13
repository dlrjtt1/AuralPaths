"""
Detmold Konzerthaus as a drawn hall, calibrated on measured omnidirectional IRs and compared with measured
Neumann KU100 BRIRs at the same seats (Detmold SRIR database, Set C: loudspeaker orchestra S1 - S8, dense receiver
grid; Detmold University of Music, https://zenodo.org/records/4116247, CC BY 4.0).

    python validation/detmold_kh.py setup <DetmoldSRIR_v01 folder> <section image> --hrir <KU100.sofa> [--out out/detmold]
    python calibrate.py out/detmold/config.json out/detmold/t30.csv --out out/detmold/config_cal.json --iter 4
    python validation/detmold_kh.py render out/detmold/config_cal.json [--sources S2,S3,S6,S7]
    python validation/detmold_kh.py compare <DetmoldSRIR_v01 folder> out/detmold [--meas-csv <earlier compare.csv>]

What is taken from the data and what is assumed (state this with any result):
- Plan: outline of the hall in the position figure of Set C (Documentation/DetmoldKH_POSITIONS_Dense.png), scaled
  with the 2 m spacing of the stage loudspeakers given there (52.7 px per m at 1169 px width); the organ is not
  modelled (it is inside the outline).
- Section: longitudinal section in Appendix F.2 of Sahin (2017), MSc thesis, Set C documentation: audience floor
  +5.12 m, raked rear part rising to +9.03 m, stage +6.11 m; suspended ceiling about 8.6 m above the flat audience
  floor, lower over the stage. Read off the drawing to about +-0.3 m; the zigzag ceiling elements are not modelled.
- Seats: x, y fitted to the measured direct-sound times of four loudspeakers (S2, S3, S6, S7) with this floor
  (rms residual 0.05 ms); ear height 1.12 m above the local floor (thesis). Head facing the stage.
- Loudspeakers: Neumann KH 120 A at the positions of the figure, 1.4 m (front row) and 1.8 m (rear row) above the
  stage (thesis: "approximately 1.4 and 1.8 m"; which row has which height is assumed), aimed at the middle of the
  audience; directivity: the generic 90 degree model of AuralPaths (no measured KH 120 data used).
- Materials: one absorption per surface group (audience, walls, ceiling, stage), calibrated on the measured T30 of
  the omnidirectional IRs (S2, S3 to 12 seats); scattering assumed.
- The hall's active acoustics / wave field synthesis systems are assumed off for Set C.
Outputs are derivatives of the Detmold data (CC BY 4.0, attribution required); keep them out of the repository.
"""
import argparse
import csv
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, ".."), HERE]
import brir_proto as bp            # noqa: E402

PX_PER_M_DISPLAY = 52.7            # Set C position figure shown at 1169 px width: stage loudspeakers 2 m apart
FIG_W_DISPLAY = 1169
SRC_PX = {"S1": (348, 292), "S2": (453, 292), "S3": (664, 292), "S4": (770, 292),
          "S5": (398, 188), "S6": (503, 188), "S7": (608, 188), "S8": (715, 188)}
SRC_H = {"S1": 1.4, "S2": 1.4, "S3": 1.4, "S4": 1.4, "S5": 1.8, "S6": 1.8, "S7": 1.8, "S8": 1.8}
STAGE_Y, STAGE_Z = 28.1, 0.99
# floor and ceiling (y from the rear wall towards the stage, z above the flat audience floor at +5.12 m)
FLOOR = [[0.0, 3.91], [3.15, 3.91], [16.9, 0.0], [28.1, 0.0], [28.1, 0.99], [34.3, 0.99]]
CEIL = [[0.0, 9.2], [17.4, 9.3], [21.7, 8.7], [28.0, 8.1], [34.3, 6.9]]
OMNI_SEATS = [126, 211, 285, 372, 459, 546, 131, 216, 290, 464, 158, 367]
SEATS = [10, 52, 57, 62, 67, 121, 126, 131, 158, 163, 168, 206, 211, 216, 274, 280, 285, 290, 296, 361, 367, 372,
         377, 383, 448, 454, 459, 464, 470, 535, 541, 546, 551, 557]


def floor_z(y):
    return float(np.interp(y, [p[0] for p in FLOOR[:4]], [p[1] for p in FLOOR[:4]])) if y < STAGE_Y else STAGE_Z


def plan_from_figure(png):
    from PIL import Image
    from scipy import ndimage as nd
    from skimage import measure
    im = np.asarray(Image.open(png).convert("RGB")).astype(int)
    f = im.shape[1] / FIG_W_DISPLAY
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    grey = (abs(r - g) < 12) & (abs(g - b) < 12) & (r > 70) & (r < 150)          # the outline is drawn mid grey
    thick = nd.binary_opening(grey, structure=np.ones((5, 5)))
    lab, _ = nd.label(~nd.binary_dilation(thick, iterations=2))
    reg = lab == lab[int(1000 * f), int(600 * f)]
    holes = nd.binary_fill_holes(reg) & ~reg
    hl, hn = nd.label(holes)
    sizes = nd.sum(holes, hl, range(1, hn + 1))
    reg = nd.binary_dilation(reg | np.isin(hl, 1 + np.flatnonzero(sizes < 20000)), iterations=6)
    c = max(measure.find_contours(reg.astype(float), 0.5), key=len)
    poly = measure.approximate_polygon(c, tolerance=8)
    s = PX_PER_M_DISPLAY * f
    ymax = c[:, 0].max()
    P = [[x / s, (ymax - y) / s] for y, x in poly[:-1]]
    xmin = min(p[0] for p in P)
    to_m = lambda xd, yd: [xd * f / s - xmin, (ymax - yd * f) / s]          # noqa: E731
    return [[round(p[0] - xmin, 3), round(p[1], 3)] for p in P], to_m


def setup(a):
    sc = os.path.join(a.detmold, "SetC_DenseKH_LSOrchestra")
    plan, to_m = plan_from_figure(os.path.join(sc, "Documentation", "DetmoldKH_POSITIONS_Dense.png"))
    seats = json.load(open(a.seats))
    out = os.path.abspath(a.out)
    os.makedirs(out, exist_ok=True)
    aim_pt = np.array([9.0, 12.0, 2.5])
    sources = {}
    for k, (xd, yd) in SRC_PX.items():
        x, y = to_m(xd, yd)
        p = np.array([x, y, STAGE_Z + SRC_H[k]])
        d = aim_pt - p
        sources[k] = {"pos": np.round(p, 3).tolist(), "coverage": 90.0,
                      "aim": {"az": float(np.degrees(np.arctan2(d[0], -d[1]))),
                              "el": float(np.degrees(np.arctan2(d[2], np.hypot(d[0], d[1]))))},
                      "role": "Neumann KH 120 A, generic 90 degree model (assumed)"}
    recs = {f"R{r}": [seats[f"R{r}"][0], seats[f"R{r}"][1], round(floor_z(seats[f"R{r}"][1]) + 1.12, 3)] for r in SEATS}
    mats = {"aud": {"alpha": [0.45, 0.6, 0.7, 0.75, 0.75, 0.75, 0.75, 0.75], "s": 0.6},
            "wall": {"alpha": [0.1, 0.08, 0.06, 0.05, 0.05, 0.05, 0.05, 0.05], "s": 0.3},
            "ceil": {"alpha": [0.1, 0.08, 0.06, 0.05, 0.05, 0.05, 0.05, 0.05], "s": 0.3},
            "stage": {"alpha": [0.15, 0.1, 0.08, 0.08, 0.08, 0.08, 0.08, 0.08], "s": 0.2}}
    xs, ys = [p[0] for p in plan], [p[1] for p in plan]
    cfg = {"name": "Detmold Konzerthaus (Set C), drawn from the published plan and section",
           "_note": "Detmold SRIR database (CC BY 4.0); see validation/detmold_kh.py for what is assumed.",
           "fs": 48000, "c": 343.0,
           "room": {"dims_m": [round(max(xs), 3), round(max(ys), 3), 10.0], "stage_depth_m": round(max(ys) - STAGE_Y, 3),
                    "absorption_octave": {"values": [0.2] * 6}, "air_absorption": True},
           "sources": sources, "receivers": recs,
           "geometry": {"plan": plan, "floor": FLOOR, "ceiling": CEIL, "materials": mats, "ism_order": 3,
                        "rays": 20000, "diffraction": False},
           "binaural": {"sofa_path": os.path.abspath(a.hrir), "early_window_ms": 100.0, "crossfade_ms": 10.0,
                        "ism_order_early": 12, "ism_order_omni": 60},
           "output_dir": os.path.join(out, "run")}
    json.dump(cfg, open(os.path.join(out, "config.json"), "w"), indent=1)
    import soundfile as sf
    sys.path.insert(0, HERE)
    import validate_bras_cr as vb
    from validate_fratoni import BANDS, criteria
    with open(os.path.join(out, "t30.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["label", "src_x", "src_y", "src_z", "rec_x", "rec_y", "rec_z", "band_hz", "T30_s", "EDT_s"])
        for s in ("S2", "S3"):
            for r in OMNI_SEATS:
                p = os.path.join(sc, "Data", "Omni", f"{s}R{r}.wav")
                if not os.path.exists(p):
                    continue
                x, fs = sf.read(p)
                x = x if x.ndim == 1 else x[:, 0]
                on = int(np.argmax(np.abs(x) > 0.1 * np.abs(x).max())) / fs
                c_ = criteria(vb.measured_hist(x, fs), on)
                rp = recs[f"R{r}"]
                for bnd, t30, edt in zip(BANDS, c_["T30"], c_["EDT"]):
                    w.writerow([f"{s}_R{r}", *sources[s]["pos"], rp[0], rp[1], round(rp[2] + 0.23, 3), bnd,
                                round(float(t30), 3), round(float(edt), 3)])
    G = bp._geom(cfg)
    print(f"plan {len(plan)} vertices, volume {G.get('volume', float('nan')):.0f} m3 (published: about 4600 m3)")
    print(f"-> {out}/config.json, {out}/t30.csv")


def render(a):
    import soundfile as sf
    cfg = bp.load_config(a.config)
    out = os.path.join(os.path.dirname(os.path.abspath(a.config)), a.brir_dir)
    os.makedirs(out, exist_ok=True)
    hrir = bp.load_hrir(cfg["binaural"]["sofa_path"], cfg["fs"])
    n_len = int(1.5 * cfg["fs"])
    recs = list(cfg["receivers"])
    air = bp.make_room(cfg, 0).air_absorption
    for s in a.sources.split(","):
        h, centers, rs = bp.energy_hists(cfg, s, recs, return_resid=True)
        ew = bp.early_resid_directions(cfg, s, recs, centers, air) if a.early_dir else None
        for i, r in enumerate(recs):
            y, _ = bp.path_brir(cfg, s, r, hrir, h[r] if isinstance(h, dict) else h[i], centers, n_len, seed=i,
                                resid=rs[r] if isinstance(rs, dict) else rs[i], ew=None if ew is None else ew[i])
            sf.write(os.path.join(out, f"{s}{r}.wav"), np.asarray(y).T.astype(np.float32), cfg["fs"], subtype="FLOAT")
        print(s, "done", flush=True)


def _metrics(x, fs):
    from scipy.signal import butter, sosfiltfilt
    on = int(np.argmax(np.abs(x).max(1) > 0.1 * np.abs(x).max()))
    x = x[max(on - int(0.001 * fs), 0):]
    n80 = int(0.08 * fs)

    def iacc(y):
        l, r = y[:, 0], y[:, 1]
        n = np.sqrt((l @ l) * (r @ r))
        m = int(0.001 * fs)
        c = np.correlate(l, r, "full")
        mid = len(r) - 1
        return float(np.max(np.abs(c[mid - m:mid + m + 1])) / n)
    out = {"IACC_E": iacc(x[:n80]), "IACC_L": iacc(x[n80:]), "IACC_80_200": iacc(x[n80:int(0.2 * fs)])}
    # per octave band 500 Hz - 2 kHz, averaged: independent of the loudspeaker's spectrum, which the broadband values
    # weight (the measured IRs include the KH 120 response, the simulation a flat source)
    xb = {fc: sosfiltfilt(butter(4, [fc / 2 ** 0.5, fc * 2 ** 0.5], "band", fs=fs, output="sos"), x, axis=0)
          for fc in (500, 1000, 2000)}
    out["IACC_E3"] = float(np.mean([iacc(y[:n80]) for y in xb.values()]))
    out["IACC_L3"] = float(np.mean([iacc(y[n80:]) for y in xb.values()]))
    for fc in (500, 1000, 2000):
        e = (xb[fc] ** 2).sum(1)
        out[f"C80_{fc}"] = float(10 * np.log10(e[:n80].sum() / e[n80:].sum()))
        s = np.cumsum(e[::-1])[::-1]
        s = 10 * np.log10(s / s[0] + 1e-30)
        out[f"EDT_{fc}"] = float(6 * np.argmax(s <= -10) / fs)
    return out


def compare(a):
    import soundfile as sf
    sim_dir = os.path.join(a.outdir, a.brir_dir)
    meas_dir = os.path.join(a.detmold, "SetC_DenseKH_LSOrchestra", "Data", "DummyHead")
    known = {}
    if a.meas_csv:            # measured metrics of an earlier compare (compare.csv), instead of the measured BRIRs
        for r in csv.DictReader(open(a.meas_csv)):
            known[r["pair"]] = {k[:-5]: float(v) for k, v in r.items() if k.endswith("_meas")}
    rows = []
    for p in sorted(glob.glob(os.path.join(sim_dir, "*.wav"))):
        name = os.path.basename(p)
        mp = os.path.join(meas_dir, name)
        if name[:-4] in known:
            mm = known[name[:-4]]
        elif os.path.exists(mp):
            xm, fm = sf.read(mp)
            mm = _metrics(xm, fm)
        else:
            continue
        xs, fs = sf.read(p)
        rows.append((name[:-4], mm, _metrics(xs, fs)))
    keys = list(rows[0][1])
    with open(os.path.join(a.outdir, "compare.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pair"] + [f"{k}_{t}" for k in keys for t in ("meas", "sim")])
        for n, mm, ms in rows:
            w.writerow([n] + [round(v, 3) for k in keys for v in (mm[k], ms[k])])
    jnd = {"IACC": 0.075, "C80": 1.0, "EDT": 0.05}
    print(f"{len(rows)} pairs")
    for k in keys:
        d = np.array([ms[k] - mm[k] if not k.startswith("EDT") else ms[k] / mm[k] - 1 for _, mm, ms in rows])
        j = jnd[k.split("_")[0]]
        print(f"{k:12s} meas {np.mean([mm[k] for _, mm, _ in rows]):6.2f}  sim {np.mean([ms[k] for _, _, ms in rows]):6.2f}  "
              f"diff mean {np.mean(d):+.3f} median |diff| {np.median(np.abs(d)):.3f}  within JND ({j}) {100 * np.mean(np.abs(d) <= j):.0f} %")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    s1 = sp.add_parser("setup"); s1.add_argument("detmold"); s1.add_argument("seats")
    s1.add_argument("--hrir", required=True); s1.add_argument("--out", default=os.path.join(HERE, "..", "out", "detmold"))
    s2 = sp.add_parser("render"); s2.add_argument("config"); s2.add_argument("--sources", default="S2,S3,S6,S7")
    s2.add_argument("--early-dir", action="store_true", help="early residual with direction-dependent coherence (path_brir ew=)")
    s2.add_argument("--brir-dir", default="brir")
    s3 = sp.add_parser("compare"); s3.add_argument("detmold"); s3.add_argument("outdir")
    s3.add_argument("--brir-dir", default="brir")
    s3.add_argument("--meas-csv", default=None, help="measured metrics from an earlier compare.csv (no measured BRIRs needed)")
    a = ap.parse_args()
    {"setup": setup, "render": render, "compare": compare}[a.cmd](a)


if __name__ == "__main__":
    main()
