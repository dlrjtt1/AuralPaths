"""
OperaRIR (Finnish National Opera, main auditorium): EDT, T30, C80, D50 with the measurement loudspeaker
(Genelec 8331A, measured directivity) against the 97 measured seats in the stalls, two stage positions.

Data:
- RIRs: OperaRIR, https://doi.org/10.5281/zenodo.8096639 (CC BY-NC 4.0); Alary & Politis, Forum Acusticum 2023,
  https://dael.euracoustics.org/confs/fa2023/data/articles/000833.pdf (empty stage, curtain up, loudspeakers on 1.6 m
  stands about 1 m behind the stage edge). Reduced on the data side to octave-band energy histograms of the W channel
  of the 4th-order SN3D RIRs (opera_hist.py: onset at 50 ms, 1 ms bins), files opera_hist_p*.npz.
- Loudspeaker: Genelec 8331A directivity, https://zenodo.org/records/10255555 (CC BY 4.0),
  LS_directivity_Calibrated_GENELEC_8331A.sofa; aimed at the audience (horizontal, assumption).
- Geometry: validation/opera_model.py.

Calibration: the absorption of the seating ("aud") and of the stage house ("stage") is scaled by one factor per band
until the mean simulated T30 of Source2 at every 4th seat is within 3 % of the measured mean (at most --iter runs);
the hard surfaces keep their start values. Then both sources at all seats are simulated once.

    python validation/opera_check.py <folder with opera_hist_p*.npz and OperaRIR_layout.mat> --sofa <8331A.sofa>
        [--out out/opera] [--rays 5000] [--ism 1] [--iter 4] [--skip-cal]

Writes <out>/config_cal.json, sim_<source>.npz, results.csv (measured / simulated per seat, source, metric, band).
"""
import argparse
import copy
import csv
import glob
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path[:0] = [ROOT, HERE]
import brir_proto as bp                       # noqa: E402
import opera_model as om                      # noqa: E402
from arvedi_check import metrics              # noqa: E402
from validate_fratoni import BANDS            # noqa: E402

C = 343.0
T0_MEAS = 0.05                                # onset position in the measured histograms
# start values (assumptions; "aud" and "stage" are calibrated)
MATS = {"aud": ([0.5, 0.6, 0.65, 0.7, 0.7, 0.7], 0.6), "wall": ([0.12, 0.10, 0.08, 0.07, 0.07, 0.07], 0.3),
        "ceiling": ([0.06] * 6, 0.2), "front": ([0.05] * 6, 0.1), "soffit": ([0.08] * 6, 0.2),
        "stage": ([0.3] * 6, 0.5)}
ADJUST = ("aud", "stage")


def balloon_8331a(sofa, out_json):
    """Octave-band balloon of the Aalto loudspeaker SOFA files (Zenodo 10255555). Their ReceiverPosition holds
    azimuth (deg, clockwise from the loudspeaker axis, as the record states), elevation (deg) and radius although the
    file declares cartesian, so the generic SOFA reader cannot be used. Power per octave band, mean over the band's
    FFT bins; written as the inline balloon form of brir_proto.load_balloon."""
    if os.path.exists(out_json):
        return json.load(open(out_json))
    import sofar
    s = sofar.read_sofa(sofa, verify=False, verbose=False)
    rp = np.asarray(s.ReceiverPosition, float).reshape(-1, 3)
    fs = float(np.atleast_1d(s.Data_SamplingRate)[0])
    ir = np.asarray(s.Data_IR, np.float32)[0]
    nfft = 1 << int(np.ceil(np.log2(ir.shape[-1])))
    f = np.fft.rfftfreq(nfft, 1 / fs)
    pw = np.zeros((len(BANDS), len(rp)))
    for i0 in range(0, len(rp), 400):
        P = np.abs(np.fft.rfft(ir[i0:i0 + 400], nfft, axis=-1)) ** 2
        for b, fc in enumerate(BANDS):
            sel = (f >= fc / np.sqrt(2)) & (f < fc * np.sqrt(2))
            pw[b, i0:i0 + 400] = P[:, sel].mean(axis=1)
    dirs = bp._sph_to_vec(np.c_[-rp[:, 0], rp[:, 1], np.ones(len(rp))], "spherical")
    db = bp.balloon_from_points(dirs, pw)
    out = {"name": "Genelec 8331A (Aalto, Zenodo 10255555, CC BY 4.0)",
           "balloon": {"bands": list(BANDS), "db": np.round(db, 2).tolist()}}
    json.dump(out, open(out_json, "w"))
    return out


def load(folder):
    H = {}
    for f in sorted(glob.glob(os.path.join(folder, "opera_hist_p*.npz"))):
        H.update({k: v.astype(float) for k, v in np.load(f).items()})
    return H


def config(layout, sofa, rays, ism):
    return {"name": "Finnish National Opera, main auditorium (validation/opera_check.py)",
            "_note": "data https://doi.org/10.5281/zenodo.8096639 (CC BY-NC 4.0); model validation/opera_model.py",
            "fs": 48000, "c": C,
            "room": {"dims_m": [30, 48, 28], "absorption_octave": {"values": [0.1] * 6}, "air_absorption": True},
            "sources": {k: {"pos": v, "aim": {"az": 180.0, "el": 0.0}, "directivity": sofa,
                            "role": "Genelec 8331A, measured directivity (Zenodo 10255555)"}
                        for k, v in om.sources(layout).items()},
            "receivers": om.receivers(layout),
            "geometry": {"mesh": {"obj": "opera.obj", "obj_text": om.build(), "axes": "z-up",
                                  "groups": {k: k for k in MATS}, "voxel": 0.1},
                         "materials": {k: {"alpha": list(a), "s": [s] * 6} for k, (a, s) in MATS.items()},
                         "ism_order": ism, "rays": rays, "diffraction": False}}


def run(cfg, src, recs, rays):
    H, cen = bp.energy_hists(cfg, src, recs, t_max=3.0, n_rays=rays)
    bi = [int(np.argmin(np.abs(np.asarray(cen) - b))) for b in BANDS]
    return {r: np.asarray(H[r])[bi] for r in recs}


def t0(cfg, src, rec):
    return float(np.linalg.norm(np.subtract(cfg["sources"][src]["pos"], cfg["receivers"][rec])) / C)


def calibrate(cfg, H, rays, n_iter, log):
    recs = list(cfg["receivers"])[::4]
    tm = np.nanmean([metrics(H[f"{r}_Source2"], T0_MEAS)["T30"] for r in recs], axis=0)
    k = np.ones(len(BANDS))
    base = {g: np.asarray(cfg["geometry"]["materials"][g]["alpha"], float) for g in ADJUST}
    for it in range(n_iter):
        c = copy.deepcopy(cfg)
        for g in ADJUST:
            c["geometry"]["materials"][g]["alpha"] = np.clip(base[g] * k, 0.01, 0.95).round(4).tolist()
        S = run(c, "Source2", recs, rays)
        ts = np.nanmean([metrics(S[r], t0(c, "Source2", r))["T30"] for r in recs], axis=0)
        log(f"calibration {it}: T30 measured {np.round(tm, 2)} simulated {np.round(ts, 2)} factor {np.round(k, 3)}")
        if np.all(np.abs(ts / tm - 1) < 0.03):
            return c
        k = k * ts / tm
    for g in ADJUST:
        c["geometry"]["materials"][g]["alpha"] = np.clip(base[g] * k, 0.01, 0.95).round(4).tolist()
    return c


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data"); ap.add_argument("--sofa", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "out", "opera"))
    ap.add_argument("--rays", type=int, default=5000); ap.add_argument("--ism", type=int, default=1)
    ap.add_argument("--iter", type=int, default=4); ap.add_argument("--skip-cal", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    log = lambda s: print(s, flush=True)
    H = load(a.data)
    bal = balloon_8331a(a.sofa, os.path.join(a.out, "genelec_8331A_balloon.json"))
    cfg = config(os.path.join(a.data, "OperaRIR_layout.mat"), bal, a.rays, a.ism)
    cal = os.path.join(a.out, "config_cal.json")
    if a.skip_cal:
        cfg = json.load(open(cal))
    else:
        cfg = calibrate(cfg, H, a.rays, a.iter, log)
        json.dump(cfg, open(cal, "w"), indent=1)
    for g in ADJUST:
        log(f"{g} alpha {cfg['geometry']['materials'][g]['alpha']}")
    rows = []
    for src in cfg["sources"]:
        f = os.path.join(a.out, f"sim_{src}.npz")
        if not os.path.exists(f):
            np.savez_compressed(f, **run(cfg, src, list(cfg["receivers"]), a.rays))
        S = np.load(f)
        for r in cfg["receivers"]:
            k = f"{r}_{src}"
            if k not in H:
                continue
            mm, ms = metrics(H[k], T0_MEAS), metrics(S[r], t0(cfg, src, r))
            for q in ("EDT", "T30", "C80", "D50", "Ts"):
                rows += [[src, r, q, b, float(x), float(y)] for b, x, y in zip(BANDS, mm[q], ms[q])]
        log(f"{src} done")
    res = os.path.join(a.out, "results.csv")
    with open(res, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["source", "seat", "metric", "band_hz", "measured", "simulated"])
        w.writerows(rows)
    summary(res)


def summary(res):
    R = list(csv.DictReader(open(res)))
    for src in sorted({r["source"] for r in R}) + ["all"]:
        g = lambda q: np.array([[float(r["measured"]), float(r["simulated"])] for r in R
                                if r["metric"] == q and src in ("all", r["source"])]).reshape(-1, len(BANDS), 2)
        E, T, C8, D = g("EDT"), g("T30"), g("C80"), g("D50")
        print(f"\n{src}: {len(E)} seats; bands {BANDS}")
        with np.errstate(invalid="ignore"):
            f = lambda v, fmt: " ".join(fmt.format(x) for x in v)
            print("T30 bias %     " + f(100 * np.nanmean(T[..., 1] / T[..., 0] - 1, 0), "{:+7.0f}"))
            print("EDT bias %     " + f(100 * np.nanmean(E[..., 1] / E[..., 0] - 1, 0), "{:+7.0f}"))
            print("EDT within 5 % " + f(100 * np.nanmean(np.abs(E[..., 1] / E[..., 0] - 1) <= 0.05, 0), "{:6.0f}%"))
            print("EDT/T30 meas   " + f(np.nanmean(E[..., 0] / T[..., 0], 0), "{:7.2f}"))
            print("EDT/T30 sim    " + f(np.nanmean(E[..., 1] / T[..., 1], 0), "{:7.2f}"))
            d = C8[..., 1] - C8[..., 0]
            print("C80 bias dB    " + f(np.nanmean(d, 0), "{:+7.2f}"))
            print("C80 within 1dB " + f(100 * np.nanmean(np.abs(d) <= 1, 0), "{:6.0f}%"))
            print("D50 bias       " + f(np.nanmean(D[..., 1] - D[..., 0], 0), "{:+7.3f}"))


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--summary":
        summary(sys.argv[2])
    else:
        main()
