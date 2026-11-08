"""
Binaural check against measured BRIRs: AuralPaths (Python engine, KU100 HRIRs) vs the BRAS dummy-head BRIRs (FABIAN)
in CR3 and CR4, five loudspeakers (string-quartet layout LS3 - LS6 and LS7 in the centre) to one listener (MP6, at the
position of RIR receiver MP1), head facing LS7 (head-above-torso 0 deg, the WAV files of the BRAS release).

    python validation/check_bras_brir.py <BRAS folder> CR3 [--rays 10000] [--hrir hrir/KU100.sofa]

The BRAS folder needs, per hall, Geometry/CRn.obj and BRIRs/wav/CRn_BRIR_LSk_MP6_HATO0.wav, plus
"3 Surface descriptions" (fitted estimates). BRAS (Aspoeck et al. 2020, https://doi.org/10.14279/depositonce-6726.3,
CC BY-SA 4.0). Positions are those of the BRAS SOFA file (CRn_BRIRs.sofa: same room frame as the RIRs; listener =
RIR MP1). The scene is rotated so that the listener faces +y (AuralPaths' head frame).

What is compared, per source (simulated vs measured; onsets aligned, since BRAS removed the leading zeros):
  - direct sound: ITD (cross-correlation lag of the first 2.5 ms) and ILD (energy ratio of the first 2.5 ms)
  - T30, EDT, C80 per octave (125 Hz - 4 kHz) from the sum of both ears
  - IACC_E3 (0 - 80 ms) and IACC_L (80 ms - end), mean of 500 Hz / 1 kHz / 2 kHz
  - spectral balance: octave levels of the whole BRIR relative to their 250 Hz - 1 kHz mean (the BRAS BRIRs are
    normalized to 0 dB at 300 Hz - 1 kHz, so absolute levels are not comparable)
Known differences of the set-up, not of the room model: the measurement used QSC K8 loudspeakers (directional, with
their own frequency response) and the FABIAN head; the simulation uses sources with a flat response (omnidirectional, or
with --coverage a coverage cone aimed at the listener; 105 deg is the K8's nominal coverage) and the KU100 HRIRs. These mainly affect ILD / spectrum at high frequencies and the direct-to-reverberant ratio.

    --k8-mps <QSCK8_1x1_64442_MPS_front_pole.csv>   measured K8 directivity of the BRAS release
        ("2 Source and receiver descriptions/QSC K8", RWTH Aachen, 1 deg grid, third-octave complex spectra; BRAS
        documentation section 3.3.1: front-pole grid, Theta from the front axis, Phi = 0 deg towards +z, 90 deg towards
        +y). Third-octave powers are summed to octaves and gridded as a balloon (brir_proto.balloon_from_points),
        normalised on axis per band; the on-axis response (direction P000T000) is applied to the whole BRIR as a
        minimum-phase filter (k8_onaxis_fir). Aim (BRAS
        documentation section 3.4.2): LS3 - LS6 tweeter towards the head, LS7 not rotated or tilted (horizontal,
        towards the listener's azimuth).
"""
import argparse
import copy
import json
import os
import sys
import tempfile
import time

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import brir_proto as bp                    # noqa: E402
import validate_bras_cr as vb              # noqa: E402

SCENES = {"CR3": "CR3 medium room (chamber music hall)", "CR4": "CR4 large room (auditorium)"}
# CRn_BRIRs.sofa (EmitterPosition, ListenerPosition), room frame of the BRAS RIRs
POS = {"CR3": dict(L=(7.84, 0.0, 1.23), LS={3: (-2.02, -1.5, 2.03), 4: (-3.32, -0.75, 2.03), 5: (-3.32, 0.75, 2.03),
                                             6: (-2.02, 1.5, 1.81), 7: (-2.02, 0.0, 2.5)}),
       "CR4": dict(L=(8.5, 0.0, 1.09), LS={3: (-1.5, -1.5, 1.03), 4: (-2.8, -0.75, 1.03), 5: (-2.8, 0.75, 1.03),
                                            6: (-1.5, 1.5, 0.82), 7: (-1.5, 0.0, 1.5)})}
OCT = [125, 250, 500, 1000, 2000, 4000]


def rot(p):
    """BRAS frame (listener looks along -x, left = -y) -> AuralPaths head frame (front +y, left -x)."""
    return [p[1], -p[0], p[2]]


def rotate_obj(text):
    """y-up OBJ: vertex (X, Y, Z) is (x, y, z) = (X, -Z, Y); x, y -> y, -x  means  (X, Y, Z) -> (-Z, Y, X)."""
    out = []
    for line in text.splitlines():
        if line.startswith("v "):
            X, Y, Z = map(float, line.split()[1:4])
            out.append(f"v {-Z:.6f} {Y:.6f} {X:.6f}")
        else:
            out.append(line)
    return "\n".join(out) + "\n"


def onset(x, fs):
    return bp.onset_time(x, fs)


def metrics(x, fs):
    """x: [2, n] BRIR. Returns dict of criteria."""
    t0 = onset(x, fs)
    n0 = int(round(t0 * fs))
    m = {"t0": t0}
    w = x[:, max(0, n0 - int(0.0005 * fs)): n0 + int(0.0025 * fs)]
    L, R = w
    m["ILD"] = 10 * np.log10(np.sum(L ** 2) / np.sum(R ** 2))
    cc = np.correlate(L, R, "full"); lag = np.argmax(np.abs(cc)) - (len(R) - 1)
    m["ITD_us"] = lag / fs * 1e6
    for k in ("T30", "EDT", "C80"):
        m[k] = []
    for fc in OCT:
        y = bp.band_filter(x, fs, fc)
        e = np.sum(y ** 2, axis=0)[n0:]
        edc = 10 * np.log10(np.maximum(np.cumsum(e[::-1])[::-1] / e.sum(), 1e-30))
        t = np.arange(len(e)) / fs

        def fit(hi, lo):
            s = (edc <= hi) & (edc >= lo)
            return -60 / np.polyfit(t[s], edc[s], 1)[0]
        m["T30"].append(fit(-5, -35)); m["EDT"].append(fit(0, -10))
        n80 = int(0.08 * fs)
        m["C80"].append(10 * np.log10(e[:n80].sum() / e[n80:].sum()))
    m["IACC_E3"] = bp.iacc_e3(x, fs, t0)
    m["IACC_L"] = bp.iacc_l(x, fs, t0)
    lv = [10 * np.log10(np.sum(bp.band_filter(x, fs, fc)[:, n0:] ** 2)) for fc in OCT]
    ref = np.mean(lv[1:4])
    m["spectrum_dB"] = [v - ref for v in lv]
    return m


def aim_at(src, dst):
    """AuralPaths "aim" (az 0 = towards -y, + towards +x; el + up) pointing from src to dst."""
    d = np.subtract(dst, src); d = d / np.linalg.norm(d)
    return {"az": float(np.degrees(np.arctan2(d[0], -d[1]))), "el": float(np.degrees(np.arcsin(d[2])))}


def k8_balloon(path, bands):
    """Inline balloon {"name", "balloon": {"bands", "db"}} for brir_proto from the BRAS K8 MPS file (see the module doc)."""
    import re
    with open(path, encoding="utf-8", errors="ignore") as f:
        head = f.readline()
        fr = np.array([float(x) for x in head.split(",")[1:] if x.strip()])
        th, ph, P = [], [], []
        for line in f:
            q = line.split(",")
            m = re.match(r"\s*P(\d+)T(\d+)", q[0])
            if not m:
                continue
            ph.append(float(m.group(1))); th.append(float(m.group(2)))
            P.append([abs(complex(x.replace(" ", "").replace("i", "j"))) ** 2 for x in q[1:] if x.strip()])
    th, ph, P = np.radians(th), np.radians(ph), np.array(P)
    dirs = np.c_[np.cos(th), np.sin(th) * np.sin(ph), np.sin(th) * np.cos(ph)]       # x front, y left, z up
    pw = np.array([P[:, np.abs(np.log2(fr / fc)) < 0.55].sum(axis=1) for fc in bands])
    return {"name": "QSC K8 (BRAS, measured)", "balloon": {"bands": [float(b) for b in bands],
                                                           "db": bp.balloon_from_points(dirs, pw).tolist()}}


def k8_onaxis_fir(path, fs, n=1024):
    """Minimum-phase FIR of the K8's on-axis magnitude (BRAS MPS file, direction P000T000, third-octave values
    interpolated on a log-frequency axis, 0 dB at 1 kHz)."""
    with open(path, encoding="utf-8", errors="ignore") as f:
        fr = np.array([float(x) for x in f.readline().split(",")[1:] if x.strip()])
        for line in f:
            if line.startswith("P000T000"):
                h = np.array([abs(complex(x.replace(" ", "").replace("i", "j"))) for x in line.split(",")[1:] if x.strip()])
                break
    db = 20 * np.log10(h / h[np.argmin(np.abs(fr - 1000))])
    f = np.fft.rfftfreq(4 * n, 1 / fs)
    mag = 10 ** (np.interp(np.log(np.clip(f, fr[0], fr[-1])), np.log(fr), db) / 20)
    from scipy import signal as sg
    return sg.minimum_phase(np.fft.fftshift(np.fft.irfft(mag ** 2, 4 * n)), method="homomorphic")[:n]


def simulate(bras, hall, rays, hrir_path, fs=44100, coverage=0.0, k8=None):
    scene = os.path.join(bras, SCENES[hall])
    mats = vb.read_bras_materials(os.path.join(bras, "3 Surface descriptions"), hall, "fitted")
    obj = rotate_obj(open(os.path.join(scene, "Geometry", f"{hall}.obj"), encoding="utf-8", errors="ignore").read())
    P = POS[hall]
    cfg = {"name": f"BRAS {hall} binaural check", "fs": fs, "c": 343.5,
           "room": {"dims_m": [10, 10, 5], "absorption_octave": {"values": [0.2] * 6}, "air_absorption": True},
           "sources": {f"LS{k}": dict({"pos": rot(p)}, **({"coverage": coverage, "aim": aim_at(rot(p), rot(P["L"]))}
                                                         if coverage else {})) for k, p in P["LS"].items()},
           "receivers": {"MP6": rot(P["L"])},
           "geometry": {"mesh": {"obj": f"{hall}_rotated.obj", "obj_text": obj, "axes": "y-up", "groups": {k: k for k in mats}},
                        "materials": {k: {"alpha": list(map(float, v["alpha"][:6])), "s": list(map(float, v["s_oct"][:6]))}
                                      for k, v in mats.items()},
                        "ism_order": 1, "rays": rays, "diffraction": False},
           "binaural": {"sofa_path": hrir_path, "early_window_ms": 100.0, "crossfade_ms": 10.0, "ism_order_early": 12,
                        "ism_order_omni": 60}}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(cfg, f)
    cfg = bp.load_config(f.name)
    os.unlink(f.name)
    if k8:
        bal = k8_balloon(k8, [float(x) for x in bp.make_room(cfg, 0).octave_bands.centers])
        for k, p in P["LS"].items():
            aim = aim_at(rot(p), rot(P["L"]))
            if k == 7:
                aim["el"] = 0.0
            cfg["sources"][f"LS{k}"].update({"directivity": bal, "aim": aim})
            cfg["sources"][f"LS{k}"].pop("coverage", None)
    hrir = bp.load_hrir(cfg["binaural"]["sofa_path"], fs)
    n_len = int(2.5 * fs)
    srcs = bp.source_names(cfg)
    air = bp.make_room(cfg, 0).air_absorption
    out = {}
    for j, s in enumerate(srcs):
        t = time.time()
        hist, centers, resid = bp.energy_hist(cfg, s, "MP6", return_resid=True)
        dirw = bp.late_directions(cfg, s, ["MP6"], centers, air)[0] if bp.late_on(cfg) else None
        out[s], _ = bp.path_brir(cfg, s, "MP6", hrir, hist, centers, n_len, seed=j, dirw=dirw, resid=resid)
        if k8:      # the K8's on-axis response (the balloon carries the pattern only)
            from scipy import signal as sg
            out[s] = sg.fftconvolve(out[s], k8_onaxis_fir(k8, fs)[None, :])[:, :n_len]
        print(f"{hall} {s}: simulated in {time.time() - t:.0f} s", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras"); ap.add_argument("hall", choices=list(SCENES))
    ap.add_argument("--rays", type=int, default=10000)
    ap.add_argument("--hrir", default=os.path.join(HERE, "..", "hrir", "KU100.sofa"))
    ap.add_argument("--coverage", type=float, default=0.0,
                    help="model the sources as the generic directional pattern of brir_proto.dir_model with this "
                         "nominal -6 dB angle (deg), aimed at the listener (QSC K8: 105); 0 = omnidirectional")
    ap.add_argument("--k8-mps", default=None, help="BRAS QSCK8_1x1_64442_MPS_front_pole.csv: measured K8 directivity")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    out = a.out or os.path.join(HERE, f"bras_brir_{a.hall}")
    sim = simulate(a.bras, a.hall, a.rays, a.hrir, coverage=a.coverage, k8=a.k8_mps)
    rows, lines = [], []
    for k in range(3, 8):
        x, fs = sf.read(os.path.join(a.bras, SCENES[a.hall], "BRIRs", "wav", f"{a.hall}_BRIR_LS{k}_MP6_HATO0.wav"))
        me = metrics(x.T, fs); si = metrics(np.asarray(sim[f"LS{k}"]), 44100)
        sf.write(f"{out}_LS{k}_sim.wav", np.asarray(sim[f"LS{k}"]).T.astype(np.float32), 44100, subtype="FLOAT")
        rows.append((k, me, si))
    md = [f"# BRAS {a.hall}: binaural check, AuralPaths (Python engine, KU100) vs measured BRIRs (FABIAN)", "",
          "Five loudspeakers LS3 - LS7 to listener MP6 (= RIR position MP1), head facing LS7. Materials: BRAS fitted "
          f"estimates, unchanged (not calibrated). {a.rays} rays per source, image sources order 1. Sources: "
          + ("measured QSC K8 directivity of the BRAS release (balloon, pattern only; LS3 - LS6 aimed at the head, "
             "LS7 horizontal). " if a.k8_mps else "")
          + (f"generic directional pattern, {a.coverage:.0f} deg nominal, aimed at the listener (an approximation of the "
             "QSC K8; brir_proto.dir_model). " if a.coverage else ("" if a.k8_mps else "omnidirectional. ")) + "Simulated BRIRs: "
          f"`{os.path.basename(out)}_LSk_sim.wav`.", "",
          "## Direct sound and spatial measures", "",
          "| source | ITD measured / simulated (us) | ILD measured / simulated (dB) | IACC_E3 measured / simulated | IACC_L measured / simulated |",
          "|---|---|---|---|---|"]
    for k, me, si in rows:
        md.append(f"| LS{k} | {me['ITD_us']:+.0f} / {si['ITD_us']:+.0f} | {me['ILD']:+.1f} / {si['ILD']:+.1f} | "
                  f"{me['IACC_E3']:.2f} / {si['IACC_E3']:.2f} | {me['IACC_L']:.2f} / {si['IACC_L']:.2f} |")
    md += ["", "ITD sign: negative = left ear leads. ILD: left minus right. AuralPaths renders the direct sound with the "
           "nearest KU100 HRIR (no interpolation).", ""]
    for key, unit in (("T30", "s"), ("EDT", "s"), ("C80", "dB"), ("spectrum_dB", "dB re 250 Hz - 1 kHz")):
        md += [f"## {key} ({unit}), measured / simulated", "", "| source | " + " | ".join(f"{b} Hz" for b in OCT) + " |",
               "|---|" + "---|" * len(OCT)]
        for k, me, si in rows:
            md.append(f"| LS{k} | " + " | ".join(f"{m_:.2f} / {s_:.2f}" for m_, s_ in zip(me[key], si[key])) + " |")
        dif = np.array([np.subtract(si[key], me[key]) for _, me, si in rows])
        if key in ("T30", "EDT"):
            rel = np.array([np.divide(si[key], me[key]) - 1 for _, me, si in rows]) * 100
            md.append(f"| mean simulated - measured | " + " | ".join(f"{v:+.0f} %" for v in rel.mean(0)) + " |")
        else:
            md.append(f"| mean simulated - measured | " + " | ".join(f"{v:+.1f} dB" for v in dif.mean(0)) + " |")
        md.append("")
    me_e = np.mean([me["IACC_E3"] for _, me, _ in rows]); si_e = np.mean([si["IACC_E3"] for _, _, si in rows])
    me_l = np.mean([me["IACC_L"] for _, me, _ in rows]); si_l = np.mean([si["IACC_L"] for _, _, si in rows])
    md += [f"Means over the five sources: IACC_E3 measured {me_e:.2f}, simulated {si_e:.2f}; IACC_L measured {me_l:.2f}, "
           f"simulated {si_l:.2f}; |ITD difference| {np.mean([abs(si['ITD_us'] - me['ITD_us']) for _, me, si in rows]):.0f} us; "
           f"|ILD difference| {np.mean([abs(si['ILD'] - me['ILD']) for _, me, si in rows]):.1f} dB.", ""]
    open(out + ".md", "w").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
