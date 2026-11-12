"""Detmold (diagnostic, 2026-11-13): where does the simulated early interaural correlation fall below the measured one?

For sources --sources and all seats of the calibrated config, the BRIR is rendered twice: as in the check (discrete
image-source arrivals + noise shaped by the ray-traced energy they do not explain, "residual"), and with the residual
left out of the early part (discrete arrivals only). Printed, as means over the pairs, for the octave bands 500 Hz,
1 kHz, 2 kHz (mean of the three):
    IACC in the windows 0 - 20, 20 - 50, 50 - 80 and 0 - 80 ms after the direct sound: measured, simulated, discrete only
    the share of the simulated energy in each window that is residual (rendered as binaurally incoherent noise)
    the energy of each window relative to 0 - 80 ms, measured and simulated (dB)
With --directional a third rendering: the residual of the early part as noise whose ear energies and interaural
coherence follow the arrival directions of the scattered ray energy (dirrays.window_direction_energy), separately in
the windows 0 - 20, 20 - 50 and 50 - 110 ms after the direct sound, instead of the diffuse-field coherence.

    python validation/detmold_iacc_diag.py <DetmoldSRIR_v01 folder> out/detmold/config_cal.json [--sources S2,S7]
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, ".."), HERE]
import brir_proto as bp            # noqa: E402

WIN = ((0.0, 0.020), (0.020, 0.050), (0.050, 0.080), (0.0, 0.080))
FC = (500, 1000, 2000)


def bands(x, fs):
    from scipy.signal import butter, sosfiltfilt
    on = int(np.argmax(np.abs(x).max(1) > 0.1 * np.abs(x).max()))
    x = x[max(on - int(0.001 * fs), 0):]
    return [sosfiltfilt(butter(4, [fc / 2 ** 0.5, fc * 2 ** 0.5], "band", fs=fs, output="sos"), x, axis=0) for fc in FC]


def iacc(y, fs):
    l, r = y[:, 0], y[:, 1]
    n = np.sqrt((l @ l) * (r @ r)) + 1e-30
    m = int(0.001 * fs)
    c = np.correlate(l, r, "full")
    mid = len(r) - 1
    return float(np.max(np.abs(c[mid - m:mid + m + 1])) / n)


def per_window(x, fs):
    """IACC [4 windows] (mean of 3 bands) and energy [4 windows] (sum of the 3 bands)."""
    xb = bands(x, fs)
    ic = [np.mean([iacc(y[int(a * fs):int(b * fs)], fs) for y in xb]) for a, b in WIN]
    en = [sum(float((y[int(a * fs):int(b * fs)] ** 2).sum()) for y in xb) for a, b in WIN]
    return np.array(ic), np.array(en)


EW = (0.0, 0.020, 0.050, 0.110)          # windows of the directional early residual, s after the direct sound


def directional_resid(cfg, hrir, resid, centers, W, t0, n_len, seed):
    """Early residual noise [2, n_len] (not yet windowed) with direction-dependent coherence per window of EW."""
    from scipy import signal
    fs = cfg["fs"]
    fb = bp.octave_filterbank(fs)
    rng = np.random.default_rng(seed + 7919)
    out = np.zeros((2, n_len))
    t = np.arange(n_len) / fs
    t_bin = np.minimum((t / bp.HIST_BIN).astype(int), resid.shape[1] - 1)
    for k in range(len(EW) - 1):
        m = (t >= t0 + EW[k]) & (t < t0 + EW[k + 1]) if k else (t < t0 + EW[1])
        if W[k].sum() > 0:
            dfE, cg = bp.late_field(hrir, W[k], centers, fs)
            pair = bp.coherent_pair_complex(rng, n_len, fs, bp.late_dir_tables(hrir)["f"], cg)
        else:
            dfE = hrir.df_band_energy
            pair = bp.coherent_pair(rng, n_len, fs, hrir.coh_f, hrir.coh)
        for bi, (sos, (lo, hi), pb) in enumerate(zip(fb["sos"], fb["edges"], bp.bank_to_band(fs, centers))):
            env = np.convolve(resid[pb], np.ones(5) / 5, mode="same")[t_bin] / (bp.HIST_BIN * fs) * (min(hi, fs / 2) - lo) / (fs / 2)
            for ear in range(2):
                n = signal.sosfiltfilt(sos, pair[ear])
                n /= np.sqrt(np.mean(n ** 2)) + 1e-20
                out[ear] += n * np.sqrt(env * dfE[ear, bi]) * m
    return out


def main():
    import soundfile as sf
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("detmold"); ap.add_argument("config"); ap.add_argument("--sources", default="S2,S7")
    ap.add_argument("--directional", action="store_true")
    ap.add_argument("--first-from-source", action="store_true",
                    help="with --directional: the residual of the first window (0 - 20 ms) arrives from the source direction"); ap.add_argument("--dir-rays", type=int, default=20000)
    a = ap.parse_args()
    cfg = bp.load_config(a.config)
    hrir = bp.load_hrir(cfg["binaural"]["sofa_path"], cfg["fs"])
    fs = cfg["fs"]; n_len = int(1.5 * fs)
    meas_dir = os.path.join(a.detmold, "SetC_DenseKH_LSOrchestra", "Data", "DummyHead")
    recs = list(cfg["receivers"])
    R = {k: [] for k in ("im", "is", "id", "em", "es", "share", "ir")}
    for s in a.sources.split(","):
        h, centers, rs = bp.energy_hists(cfg, s, recs, return_resid=True)
        bi = [int(np.argmin(np.abs(np.asarray(centers) - f))) for f in FC]
        if a.directional:
            import dirrays
            G = bp._geom(cfg); mats = cfg["geometry"]["materials"]; nb = len(centers)
            al = lambda m: [mats[m]["alpha"][j] if j < len(mats[m]["alpha"]) else mats[m]["alpha"][-1] for j in range(nb)]
            alpha = np.array([al(q["mat"]) for q in G["S"]])
            scat = np.array([float(np.mean(mats[q["mat"]].get("s", 0.0))) for q in G["S"]])
            S0 = np.asarray(cfg["sources"][s]["pos"], float)
            Rp = [np.asarray(cfg["receivers"][r], float) for r in recs]
            te = np.array([np.linalg.norm(p - S0) / cfg["c"] + np.array(EW) for p in Rp])
            te[:, 0] = 0.0
            WW = dirrays.window_direction_energy(G, S0, Rp, te, alpha, scat, bp.make_room(cfg, 0).air_absorption, cfg["c"], a.dir_rays)
        for i, r in enumerate(recs):
            mp = os.path.join(meas_dir, f"{s}{r}.wav")
            if not os.path.exists(mp):
                continue
            xm, fm = sf.read(mp)
            y, _ = bp.path_brir(cfg, s, r, hrir, h[r], centers, n_len, seed=i, resid=rs[r])
            yd, _ = bp.path_brir(cfg, s, r, hrir, h[r], centers, n_len, seed=i, resid=np.zeros_like(rs[r]))
            im, em = per_window(xm, fm); is_, es = per_window(np.asarray(y).T, fs); id_, _ = per_window(np.asarray(yd).T, fs)
            t0 = np.linalg.norm(np.subtract(cfg["sources"][s]["pos"], cfg["receivers"][r])) / cfg["c"]
            t = (np.arange(h[r].shape[1]) + 0.5) * bp.HIST_BIN - t0
            sh = [rs[r][bi][:, (t >= a_) & (t < b_)].sum() / max(h[r][bi][:, (t >= a_) & (t < b_)].sum(), 1e-30) for a_, b_ in WIN]
            if a.directional:
                we, _ = bp.crossfade_windows(n_len, fs, t0 + cfg["binaural"]["early_window_ms"] / 1000, cfg["binaural"]["crossfade_ms"])
                Wr = WW[i].copy()
                if a.first_from_source:      # scattered part of the direct sound's own floor / seat reflection
                    u = dirrays.world_to_head(np.subtract(cfg["sources"][s]["pos"], cfg["receivers"][r])[None, :])[0]
                    Wr[0] = 0.0
                    Wr[0, int(np.argmax(dirrays.BINS @ (u / np.linalg.norm(u))))] = WW[i][0].sum(axis=0)
                yr = np.asarray(yd) + directional_resid(cfg, hrir, rs[r], centers, Wr, t0, n_len, i) * we
                R["ir"].append(per_window(yr.T, fs)[0])
            for k, v in zip(("im", "is", "id", "em", "es", "share"), (im, is_, id_, em, es, sh)):
                R[k].append(v)
        print(s, "done", flush=True)
    R = {k: np.array(v) for k, v in R.items() if len(v)}
    lab = ["0-20 ms", "20-50 ms", "50-80 ms", "0-80 ms"]
    print(f"\n{len(R['im'])} pairs, bands 500 Hz - 2 kHz")
    print("window     IACC measured / simulated / discrete only   residual share   energy re 0-80 ms, measured / simulated (dB)")
    for j, l in enumerate(lab):
        em = 10 * np.log10(R["em"][:, j] / R["em"][:, 3]); es = 10 * np.log10(R["es"][:, j] / R["es"][:, 3])
        print(f"{l:9s}  {R['im'][:, j].mean():.2f} / {R['is'][:, j].mean():.2f} / {R['id'][:, j].mean():.2f}"
              f"                         {100 * R['share'][:, j].mean():3.0f} %            {em.mean():+.1f} / {es.mean():+.1f}"
              + (f"     directional residual: IACC {R['ir'][:, j].mean():.2f}" if "ir" in R else ""))


if __name__ == "__main__":
    main()
