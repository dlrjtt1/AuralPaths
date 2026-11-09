"""
Check the Python engine against measured room impulse responses of two real halls in the BRAS database:
CR3 (chamber music hall, Konzerthaus Berlin, 3331 m3) and CR4 (auditorium, TU Berlin, 8657 m3), position by position.

    python validate_bras_cr.py <scene folder> <surface descriptions folder> --obj <CRn.obj>
                               [--coeffs fitted|initial] [--rays 6000] [--max-faces 3000] [--out validation/bras_CR3]
                               [--no-2p5d]

Data (not included): Aspoeck, Brinkmann, Ackermann, Weinzierl, Vorlaender (2020), BRAS - Benchmark for Room Acoustical
Simulation, v3, https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0 (licence stated in the SOFA files).
  <scene folder>                  = "CR3 medium room (chamber music hall)" or "CR4 large room (auditorium)"
                                    (RIRs/CRn_RIRs_Dodecahedron.sofa: 2 loudspeaker x 5 microphone positions, Pa, 44.1 kHz;
                                    positions are read from the file)
  <surface descriptions folder>   = "3 Surface descriptions" (_csv/initial_estimates, _csv/fitted_estimates)
  --obj                           = Geometry/CRn.skp exported as OBJ with the SketchUp materials kept as group names
                                    (Blender: File > Export > Wavefront OBJ, "Object Groups" and "Material Groups" on;
                                    the groups are then named ..._SU_mat_CRn_<material>...).

Materials: the BRAS third-octave absorption and scattering (20 Hz - 20 kHz) averaged arithmetically over the three
third-octaves of each octave band 125 Hz - 4 kHz (scattering per band; the engine's image sources lose (1 - s) per
reflection and are weighted for finite reflector size, reflections.py). "initial" = estimated from databases and in-situ measurements,
"fitted" = absorption adjusted by the BRAS authors so that Eyring's formula gives the measured reverberation time
(mat_CRn.txt). The fitted set is the default: it removes most of the input uncertainty, so what remains is the
engine (geometry, image sources, ray tracing).

Runs: (a) 3D mesh with the BRAS coefficients unchanged; (b) the same after a one-step calibration of this engine on
the LS1 positions (every material's -ln(1 - alpha) scaled per band by mean T30 simulated / measured), judged on the
held-out LS2 positions; (c) the 2.5D hall made from the mesh by obj_to_hall.py (what the browser page can run;
balconies are lost).

Compared per loudspeaker-microphone pair (10 per hall):
  1. EDT, T30, C80, D50 (reported as C50), Ts per octave band (ISO 3382-1), from the measured RIR (octave filter,
     noise floor subtracted, truncated where the decay meets the noise) and from the engine's energy histograms;
     differences in JND (5 % EDT / T30, 1 dB C80 / C50, 10 ms Ts).
  2. Early reflections: each first-order image source the engine predicts (>= -15 dB re direct, >= 2 ms after the
     direct sound, no other predicted reflection within 1.5 ms) against the measured energy (500 Hz - 2 kHz) in a 1 ms
     window at the predicted time, re the same window on the direct sound; controls: the same window 2 ms later and at
     random times. (A first version matched envelope peaks within +-1 ms; measured peaks above -20 dB are so dense
     that a random time matched 80-100 % of the time, so that test said nothing and was dropped.)
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
from validate_fratoni import BANDS, JND, criteria, jnd_units

OCT_EDGES = [(fc / 2 ** 0.5, fc * 2 ** 0.5) for fc in BANDS]


# ---------------------------------------------------------------- inputs
def read_bras_materials(folder, hall, which, bands=BANDS):
    """{"mat_CRn_x": {"alpha": [octaves], "s": scattering at 1 kHz octave, "s_oct": [octaves]}} from the BRAS csv
    files (third-octave data averaged per octave; default 125 Hz - 4 kHz, the BRAS data reach 20 kHz)."""
    out = {}
    for p in sorted(glob.glob(os.path.join(folder, "_csv", f"{which}_estimates", f"mat_{hall}_*.csv"))):
        rows = [[float(v) for v in ln.split(",")] for ln in open(p, encoding="utf-8").read().strip().splitlines()]
        f, a, s = (np.asarray(r) for r in rows[:3])
        alpha, scat = [], []
        for lo, hi in [(fc / 2 ** 0.5, fc * 2 ** 0.5) for fc in bands]:
            sel = (f >= lo) & (f < hi)
            alpha.append(float(np.mean(a[sel])))
            scat.append(float(np.mean(s[sel])))
        out[os.path.splitext(os.path.basename(p))[0]] = {"alpha": alpha, "s": scat[list(bands).index(1000)], "s_oct": scat}
    if not out:
        raise SystemExit(f"no mat_{hall}_*.csv in {folder}/_csv/{which}_estimates")
    return out


def read_rirs(scene):
    import sofar
    p = glob.glob(os.path.join(scene, "RIRs", "*_RIRs_Dodecahedron.sofa"))[0]
    s = sofar.read_sofa(p, verify=False, verbose=False)
    ir = np.asarray(s.Data_IR, float)[0]                 # [receiver, emitter, samples]
    E = np.asarray(s.EmitterPosition, float)[..., 0]
    R = np.asarray(s.ReceiverPosition, float)[..., 0]
    eid = np.asarray(s.EmitterID).ravel().astype(int)
    rid = np.asarray(s.ReceiverID).ravel().astype(int)
    return ir, float(np.atleast_1d(s.Data_SamplingRate)[0]), E, R, eid, rid, p


# ---------------------------------------------------------------- measured side
def measured_hist(x, fs, bands=BANDS, bin_s=bp.HIST_BIN):
    """Octave-band energy histograms of a measured RIR with the noise floor removed (energy minus the noise
    estimate from the last 0.4 s; truncated where the 10 ms smoothed energy first falls to twice the noise)."""
    from scipy.signal import butter, sosfiltfilt
    out = []
    nb = int(round(bin_s * fs))
    for fc in bands:
        sos = butter(3, [fc / 2 ** 0.5, min(fc * 2 ** 0.5, 0.45 * fs)], btype="band", fs=fs, output="sos")
        e = sosfiltfilt(sos, x) ** 2
        noise = float(np.mean(e[-int(0.4 * fs):]))
        sm = np.convolve(e, np.ones(int(0.01 * fs)) / int(0.01 * fs), mode="same")
        pk = int(np.argmax(sm))
        below = np.flatnonzero(sm[pk:] <= 2 * noise)
        tp = pk + (int(below[0]) if below.size else len(e) - pk)
        ec = np.clip(e - noise, 0, None)
        ec[tp:] = 0
        n = len(ec) // nb
        out.append(ec[: n * nb].reshape(n, nb).sum(1))
    return np.asarray(out)


def band_energy(x, fs, lo=355.0, hi=2828.0):
    """Squared band-passed RIR (500 Hz - 2 kHz octaves together) and the direct-sound sample index."""
    from scipy.signal import butter, sosfiltfilt
    sos = butter(4, [lo, hi], btype="band", fs=fs, output="sos")
    on = int(np.argmax(np.abs(x) > 0.1 * np.abs(x).max()))
    return sosfiltfilt(sos, x) ** 2, on


def window_level(y, on, fs, t, w=(0.0002, 0.0008)):
    """Energy in [t - 0.2 ms, t + 0.8 ms] after the direct sound, in dB re the same window on the direct sound."""
    a, b = int(w[0] * fs), int(w[1] * fs)
    k = on + int(round(t * fs))
    return 10 * np.log10(y[k - a: k + b].sum() / y[on - a: on + b].sum() + 1e-30)


# ---------------------------------------------------------------- predicted early reflections
def predicted_first_order(cfg, src, recs, bands_idx=(2, 3, 4)):
    """{rec: [(delay after direct s, level dB re direct)]} of visible first-order image sources (pyroomacoustics),
    energy mean over the 500 Hz, 1 kHz and 2 kHz octaves, with the engine's specular factors (finite reflector size,
    scattering loss: reflections.py) unless the configuration switches them off."""
    room = bp.make_room(cfg, 1)
    room.add_source(cfg["sources"][src]["pos"])
    room.add_microphone_array(np.array([cfg["receivers"][r] for r in recs], float).T)
    room.image_source_model()
    S = room.sources[0]
    out = {}
    for i, r in enumerate(recs):
        m = np.asarray(cfg["receivers"][r], float)
        vis = bp.visible_images(room, i)
        d0 = np.linalg.norm(m - np.asarray(cfg["sources"][src]["pos"], float))
        lst = []
        ks = np.flatnonzero(vis & (S.orders == 1))
        F = bp.specular_factors(cfg, room, ks, cfg["sources"][src]["pos"], m)    # same factors as the engine
        for j, k in enumerate(ks):
            d = np.linalg.norm(S.images[:, k] - m)
            f = F[list(bands_idx), j] if F is not None else 1.0
            e = np.mean((S.damping[list(bands_idx), k] / d) ** 2 * f) / (1 / d0 ** 2)
            lst.append(((d - d0) / cfg["c"], 10 * np.log10(e + 1e-30)))
        out[r] = sorted(lst)
    return out


def reflection_check(pred, y, on, fs, t_min=0.002, floor_db=-15.0, iso=0.0015, rng=None):
    """Isolated predicted reflections (>= floor_db re direct, later than t_min, no other predicted reflection within
    +-iso): (t, predicted dB, measured window dB, measured dB with the time shifted by +2 ms). Plus measured levels at
    random times 3-20 ms (control)."""
    rows = []
    for t, l in pred:
        if t < t_min or l < floor_db or any(abs(t - t2) <= iso for t2, _ in pred if t2 != t):
            continue
        rows.append((t, l, window_level(y, on, fs, t), window_level(y, on, fs, t + 0.002)))
    rng = rng or np.random.default_rng(0)
    rnd = [window_level(y, on, fs, t) for t in rng.uniform(0.003, 0.02, 20)]
    return rows, rnd


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scene")
    ap.add_argument("surfaces")
    ap.add_argument("--obj", required=True)
    ap.add_argument("--coeffs", default="fitted", choices=["fitted", "initial"])
    ap.add_argument("--rays", type=int, default=6000)
    ap.add_argument("--max-faces", type=int, default=3000)
    ap.add_argument("--voxel", type=float, default=0.05,
                    help="voxel size (m) for finding the room inside the mesh; memory grows as 1/voxel^3 "
                         "(CR4, 33 x 33 x 14 m: 0.05 needs > 6 GB, 0.08 about 2 GB)")
    ap.add_argument("--no-2p5d", action="store_true")
    ap.add_argument("--only-2p5d", action="store_true", help="skip the 3D runs (quick check of the 2.5D conversion)")
    ap.add_argument("--no-calibrate", action="store_true",
                    help="skip the second 3D run with absorption calibrated on the LS1 positions")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    ir, fs, E, R, eid, rid, sofa_path = read_rirs(a.scene)
    hall = re.search(r"(CR\d)", os.path.basename(sofa_path)).group(1)
    out = a.out or os.path.join("validation", f"bras_{hall}")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    lines = []

    def log(msg):
        print(msg, flush=True)
        lines.append(msg)

    mats = read_bras_materials(a.surfaces, hall, a.coeffs)
    srcs = {f"LS{e}": list(map(float, E[i])) for i, e in enumerate(eid)}
    recs = {f"MP{r}": list(map(float, R[i])) for i, r in enumerate(rid)}
    cfg = {"name": f"BRAS {hall}", "fs": 48000, "c": 343.5,
           "room": {"air_absorption": True, "dims_m": [1, 1, 1], "stage_depth_m": 0.0},
           "binaural": {"late_directional": False},
           "sources": {k: {"pos": v} for k, v in srcs.items()}, "receivers": recs,
           "geometry": {"mesh": {"obj": a.obj, "groups": {k: k for k in mats}, "max_faces": a.max_faces,
                                 "voxel": a.voxel},
                        "materials": {k: {"alpha": v["alpha"], "s": v["s_oct"]} for k, v in mats.items()},
                        "ism_order": 1, "rays": a.rays, "diffraction": False}}
    G = bp._geom(cfg)
    vol_ref = {"CR3": 3330.6, "CR4": 8656.5}.get(hall)
    log(f"{hall}: OBJ {G['n_input']} faces -> {G['n_faces']} after decimation -> "
        f"{sum(1 for s in G['S'] if s['kind'] == 'mesh')} room-facing faces ({G['n_dropped']} dropped); room volume "
        f"(voxels) {G['volume']:.0f} m3 (BRAS documentation: {vol_ref} m3)")
    log("surface areas (m2): " + ", ".join(f"{k.split('_', 2)[2]} {v:.1f}" for k, v in sorted(G["area"].items()))
        + f"; total {sum(G['area'].values()):.0f}")
    A = [sum(mats[k]["alpha"][i] * G["area"][k] for k in G["area"]) for i in range(6)]
    S_t = sum(G["area"].values())
    log("Sabine / Eyring T (s), no air: " + ", ".join(
        f"{b} Hz {0.161 * G['volume'] / A[i]:.2f} / {0.161 * G['volume'] / (-S_t * np.log(1 - A[i] / S_t)):.2f}"
        for i, b in enumerate(BANDS)))
    log(f"absorption: BRAS {a.coeffs}_estimates; scattering per octave band (shown: 1 kHz): " +
        ", ".join(f"{k.split('_', 2)[2]} {v['s']:.2f}" for k, v in mats.items()))

    # measured criteria per pair
    meas, peaks = {}, {}
    for i, r in enumerate(rid):
        for j, e in enumerate(eid):
            s_, r_ = f"LS{e}", f"MP{r}"
            d = np.linalg.norm(np.subtract(recs[r_], srcs[s_]))
            x = ir[i, j]
            on = int(np.argmax(np.abs(x) > 0.1 * np.abs(x).max())) / fs
            h = measured_hist(x, fs)
            meas[(s_, r_)] = criteria(h, on)
            peaks[(s_, r_)] = band_energy(x, fs)
            meas[(s_, r_)]["_t_dir_err_ms"] = 1000 * (on - d / cfg["c"])

    # simulated
    def run(cfg_, label):
        sim, refl = {}, {}
        for s_ in srcs:
            t = time.time()
            rr = [r for r in recs if r in cfg_["receivers"]]
            H, cen = bp.energy_hists(cfg_, s_, rr, t_max=3.0, n_rays=a.rays)
            bi = [int(np.argmin(np.abs(np.asarray(cen) - b))) for b in BANDS]
            for r_ in rr:
                d = np.linalg.norm(np.subtract(cfg_["receivers"][r_], cfg_["sources"][s_]["pos"]))
                sim[(s_, r_)] = criteria(H[r_][bi], d / cfg_["c"])
            refl.update({(s_, r_): v for r_, v in predicted_first_order(cfg_, s_, rr).items()})
            log(f"[{label}] {s_}: {len(rr)} receivers, {time.time() - t:.0f} s")
        return sim, refl

    sim3, refl3 = (None, None) if a.only_2p5d else run(cfg, "3D mesh")
    simc = reflc = None
    if not a.no_calibrate and not a.only_2p5d:
        # one-step calibration of this engine, as calibrate.py would do with measured T30: per band, scale every
        # material's absorption exponent -ln(1 - alpha) by f = mean(T30 sim / T30 measured) over the LS1 positions,
        # then run again and judge on the LS2 positions, which the calibration did not see
        cal = [k for k in meas if k[0] == "LS1"]
        f = np.nanmean([np.asarray(sim3[k]["T30"]) / np.asarray(meas[k]["T30"]) for k in cal], axis=0)
        cfgc = json.loads(json.dumps(cfg))
        for m in cfgc["geometry"]["materials"].values():
            m["alpha"] = [float(1 - (1 - al) ** fb) for al, fb in zip(m["alpha"], f)]
        log("calibration on LS1 (T30 sim / measured per band): " + ", ".join(f"{b} Hz {v:.3f}" for b, v in zip(BANDS, f)))
        bp._GEOM_CACHE.clear()
        simc, reflc = run(cfgc, "3D mesh calibrated")
    sim25 = refl25 = rep25 = None
    if not a.no_2p5d:
        import obj_to_hall
        cfg25, rep25 = obj_to_hall.convert(cfg, "x", "min", 0.0)
        cfg25["geometry"].update(ism_order=2, rays=a.rays, diffraction=False)
        import geometry
        G25 = bp._geom(cfg25)
        moved, outside = [], []
        for k in list(cfg25["receivers"]) + list(cfg25["sources"]):
            p = cfg25["sources"][k]["pos"] if k in cfg25["sources"] else cfg25["receivers"][k]
            if not geometry.inside(G25, p):
                z = geometry.prof_at(G25["floor"], p[1]) + 1.2
                if geometry.inside(G25, [p[0], p[1], z]):
                    moved.append(f"{k} {p[2]:.2f}->{z:.2f}")
                    p[2] = round(z, 3)
                elif not k.startswith(("B_", "S_amp")):
                    outside.append(k)
        rep25["volume_2p5d_m3"] = round(obj_to_hall.volume_2p5d(cfg25["geometry"], 50000), 1)
        log(f"2.5D hall (depth axis = x, stage at small x; image sources order 2, no diffraction): "
            f"{rep25['n_plan_vertices']} plan vertices, {rep25['n_surfaces_2p5d']} surfaces, volume "
            f"{rep25['volume_2p5d_m3']} m3; positions moved into the 2.5D room: {', '.join(moved) if moved else 'none'}; "
            f"outside the 2.5D plan (left out of its statistics): {', '.join(outside) if outside else 'none'}")
        for k in outside:
            if k in cfg25["receivers"]:
                del cfg25["receivers"][k]
        with open(out + "_2p5d_config.json", "w", encoding="utf-8") as f:
            note = (f"2.5D hall converted with obj_to_hall.py from the BRAS {hall} model. Derived from: Aspoeck et al. (2020), "
                    "BRAS - Benchmark for Room Acoustical Simulation, v3, https://doi.org/10.14279/depositonce-6726.3, "
                    f"CC BY-SA 4.0. Changes: geometry reduced to plan x floor/ceiling profiles (balconies lost), materials "
                    f"({a.coeffs} estimates, octave means) merged into four groups. S_amp, B_L, B_R are placeholders.")
            json.dump(dict({"_note": note}, **cfg25), f, ensure_ascii=False, indent=1)
        sim25, refl25 = run(cfg25, "2.5D")

    # ---------------------------------------------------------------- report
    rows, md = [], [f"# BRAS {hall}: measured RIRs vs AuralPaths (Python engine)", "",
                    "Data: Aspöck et al. (2020), *BRAS – Benchmark for Room Acoustical Simulation*, v3, "
                    "https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0 (dodecahedron RIRs, positions, surface "
                    f"descriptions). Material set: {a.coeffs}_estimates. This file is derived from BRAS and is CC BY-SA 4.0.",
                    "", "```", *lines, "```", ""]
    models = ([("3D mesh", sim3, refl3)] if sim3 else []) + ([("3D mesh calibrated", simc, reflc)] if simc else []) + \
             ([("2.5D", sim25, refl25)] if sim25 else [])
    md += ["## Room criteria, mean over the 10 positions (simulated − measured, mean signed / mean absolute, in JND)", "",
           "| criterion | model | " + " | ".join(f"{b} Hz" for b in BANDS) + " | mean abs 500–2k |", "|---|---|" + "---|" * 7]
    for name in ("EDT", "T30", "C80", "C50", "Ts"):
        mv = np.array([[meas[k][name][i] for i in range(6)] for k in sorted(meas)])
        md.append(f"| {name} | measured (mean) | " + " | ".join(
            (f"{v:.2f}" if name != "Ts" else f"{v:.0f}") for v in np.nanmean(mv, 0)) + " | |")
        for label, sim, _ in models:
            J = np.array([jnd_units(name, sim[k][name], np.asarray(meas[k][name])) if k in sim else np.full(6, np.nan)
                          for k in sorted(meas)])
            md.append(f"| | {label} | " + " | ".join(f"{np.nanmean(J[:, i]):+.1f} / {np.nanmean(np.abs(J[:, i])):.1f}"
                                                     for i in range(6)) + f" | {np.nanmean(np.abs(J[:, 2:5])):.1f} |")
            if label == "3D mesh calibrated":
                h = np.array([k[0] == "LS2" for k in sorted(meas)])
                Jh = J[h]
                md.append(f"| | ↳ LS2 only (held out) | " + " | ".join(
                    f"{np.nanmean(Jh[:, i]):+.1f} / {np.nanmean(np.abs(Jh[:, i])):.1f}" for i in range(6))
                    + f" | {np.nanmean(np.abs(Jh[:, 2:5])):.1f} |")
            for k, jr in zip(sorted(meas), J):
                if k not in sim:
                    continue
                for i, b in enumerate(BANDS):
                    rows.append(dict(hall=hall, coeffs=a.coeffs, pair=f"{k[0]}-{k[1]}", criterion=name, band_hz=b,
                                     model=label, measured=round(float(meas[k][name][i]), 3),
                                     simulated=round(float(sim[k][name][i]), 3), diff_jnd=round(float(jr[i]), 2)))
    md += ["", "Measured Ts in ms; EDT / T30 in s; C80 / C50 in dB. JND: ISO 3382-1 Annex A.", ""]
    md += ["## Early reflections (first-order image sources vs the measured RIR, 500 Hz–2 kHz)", "",
           "Each predicted first-order reflection that is at least −15 dB re direct, at least 2 ms after the direct sound and "
           "1.5 ms away from any other predicted one is compared with the measured energy in a 1 ms window at its predicted "
           "time (−0.2 … +0.8 ms), in dB re the same window on the direct sound. Controls: the measured level 2 ms later "
           "than predicted, and at random times 3–20 ms after the direct sound.", "",
           "| model | reflections | predicted (median dB) | measured at predicted time | measured +2 ms later | measured at random times | predicted − measured (median / IQR dB) | correlation predicted vs measured |",
           "|---|---|---|---|---|---|---|---|"]
    for label, _, refl in models:
        R_, rnd = [], []
        for k in sorted(meas):
            if k not in refl:
                continue
            y, on = peaks[k]
            rows_k, rnd_k = reflection_check(refl[k], y, on, fs)
            R_ += rows_k; rnd += rnd_k
            for t, lp, lm, ls in rows_k:
                rows.append(dict(hall=hall, coeffs=a.coeffs, pair=f"{k[0]}-{k[1]}", criterion="reflection_level_db",
                                 band_hz=round(1000 * t, 2), model=label, measured=round(lm, 2), simulated=round(lp, 2),
                                 diff_jnd=""))
        if not R_:
            md.append(f"| {label} | 0 | | | | | | |")
            continue
        R_ = np.asarray(R_)
        dlt = R_[:, 1] - R_[:, 2]
        md.append(f"| {label} | {len(R_)} | {np.median(R_[:, 1]):.1f} | {np.median(R_[:, 2]):.1f} | {np.median(R_[:, 3]):.1f} | "
                  f"{np.median(rnd):.1f} | {np.median(dlt):+.1f} / {np.percentile(dlt, 25):+.1f} … {np.percentile(dlt, 75):+.1f} | "
                  f"{np.corrcoef(R_[:, 1], R_[:, 2])[0, 1]:.2f} |")
    md += ["", "Direct-sound arrival, measured onset − distance / c (ms): " + ", ".join(
        f"{k[0]}-{k[1]} {meas[k]['_t_dir_err_ms']:+.2f}" for k in sorted(meas)), ""]
    if rep25:
        md += ["2.5D conversion (obj_to_hall.py, --preserve eyring):", "", "```", json.dumps(rep25, indent=1), "```", ""]
    with open(out + ".md", "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    with open(out + ".csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    plot(meas, models, hall, a.coeffs, out + ".png")
    print("->", out + ".md", out + ".csv", out + ".png")


def plot(meas, models, hall, coeffs, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    names = ["EDT", "T30", "C80", "C50", "Ts"]
    fig, axs = plt.subplots(1, 5, figsize=(17, 3.6))
    keys = sorted(meas)
    for ax, n in zip(axs, names):
        mv = np.array([meas[k][n] for k in keys])
        kind, jv = JND[n]
        m = np.nanmean(mv, 0)
        band = jv * m if kind == "rel" else np.full(6, jv)
        ax.fill_between(range(6), m - band, m + band, color="0.88", label="measured mean ± 1 JND")
        for row in mv:
            ax.plot(range(6), row, "-", color="0.6", lw=0.6)
        ax.plot(range(6), m, "k-o", ms=3, lw=1.5, label="measured (mean; thin: each position)")
        for (label, sim, _), col, st in zip(models, ("#c2571a", "#7a3e9d", "#2a6fb0"), ("-s", "-D", "--^")):
            ax.plot(range(6), np.nanmean([sim[k][n] for k in keys if k in sim], 0), st, color=col, ms=3, lw=1.3,
                    label=label)
        ax.set_xticks(range(6)); ax.set_xticklabels(["125", "250", "500", "1k", "2k", "4k"], fontsize=8)
        ax.set_title(f"{n} ({'s' if n in ('EDT', 'T30') else 'dB' if n.startswith('C') else 'ms'})", fontsize=9)
        ax.grid(alpha=0.3)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=len(l), fontsize=8, frameon=False)
    fig.suptitle(f"BRAS {hall}: measured RIRs (10 positions) vs AuralPaths Python engine, {coeffs} material estimates",
                 fontsize=10)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(path, dpi=110)


if __name__ == "__main__":
    main()
