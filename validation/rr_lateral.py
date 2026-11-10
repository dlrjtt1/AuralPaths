"""
Source lateralization as in the round robin (Brinkmann et al. 2019, https://doi.org/10.1121/1.5096178, SuppPub3
section 2, figure S3-33): the left/right position of each source estimated from the ITD of the direct sound, compared
with the position given by the scene geometry, for the five loudspeakers LS3 - LS7 heard at MP6 in BRAS CR3 and CR4.

    python validation/rr_lateral.py <BRAS folder> --fabian <FABIAN HRIR SOFA> --ku100 hrir/KU100.sofa
        [--sim validation]          (folder with bras_brir_CRn_FABIAN_K8data_cal16_LSk_sim.wav from check_bras_brir.py)

ITD: on the 10 times upsampled impulse response low-passed at 3 kHz (8th-order Butterworth), as in SuppPub3; then
either the onset of each ear at -20 dB re its maximum (--mode onset, the round robin's rule for the HRIRs; it read
the BRIR ITDs by eye because the automatic rule failed on some BRIRs) or the cross-correlation lag within +-1 ms
(--mode xcorr, default), applied alike to the HRIRs and to the first 3 ms of the BRIRs. Azimuth: the HRIR direction at the source's elevation
whose ITD equals the BRIR's (0.1 deg steps after linear interpolation between the HRIR directions). Measured BRIRs
(FABIAN head) are mapped with FABIAN HRIRs, the simulated ones (rendered with KU100 HRIRs) with KU100 HRIRs. Deviation:
mean absolute difference from the geometric azimuth over the five sources.
"""
import argparse
import glob
import os
import sys

import h5py
import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
MODE = "xcorr"           # "onset" (the round robin's rule for HRIRs) or "xcorr" (cross-correlation, +-1 ms)
sys.path[:0] = [HERE]
from check_bras_brir import POS, SCENES     # noqa: E402


def itd(x, fs, n=None):
    """ITD (s, positive = right ear later, i.e. source on the left) of a 2-channel IR [2, N]."""
    x = np.asarray(x, float)[:, : (n or x.shape[1])]
    up = signal.resample_poly(x, 10, 1, axis=1)
    sos = signal.butter(8, 3000, fs=10 * fs, output="sos")
    y = signal.sosfiltfilt(sos, up, axis=1)
    if MODE == "onset":
        on = [int(np.argmax(np.abs(ch) > np.abs(ch).max() * 10 ** (-20 / 20))) for ch in y]
        return (on[1] - on[0]) / (10 * fs)
    c = signal.correlate(y[1], y[0], mode="full")             # lag of the right ear re the left ear
    lags = np.arange(-len(y[0]) + 1, len(y[1]))
    m = np.abs(lags) <= int(0.001 * 10 * fs)
    return lags[m][np.argmax(c[m])] / (10 * fs)


def hrir_table(path, el):
    f = h5py.File(path, "r")
    ir = np.asarray(f["Data.IR"])
    fs = float(np.asarray(f["Data.SamplingRate"]).ravel()[0])
    pos = np.asarray(f["SourcePosition"])
    els = np.unique(np.round(pos[:, 1], 3))
    e0 = els[np.argmin(np.abs(els - el))]
    sel = np.flatnonzero((np.abs(pos[:, 1] - e0) < 1e-3) & ((pos[:, 0] % 360 <= 90.01) | (pos[:, 0] % 360 >= 269.99)))
    az = ((pos[sel, 0] + 180) % 360) - 180                      # -90 .. 90, positive = left (SOFA convention)
    it = np.array([itd(ir[i], fs) for i in sel])
    o = np.argsort(az)
    return az[o], it[o], e0


def az_from_itd(t, az, it):
    g = np.arange(-90, 90.05, 0.1)
    tg = np.interp(g, az, it)
    return float(g[np.argmin(np.abs(tg - t))])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras")
    ap.add_argument("--fabian", required=True)
    ap.add_argument("--ku100", required=True)
    ap.add_argument("--sim", default=HERE)
    ap.add_argument("--mode", default="xcorr", choices=["xcorr", "onset"])
    a = ap.parse_args()
    global MODE
    MODE = a.mode
    lines = ["| hall | source | geometry (deg) | measured BRIR (deg) | AuralPaths (deg) |", "|---|---|---|---|---|"]
    summ = []
    for hall in ("CR3", "CR4"):
        P = POS[hall]
        L = np.array(P["L"])
        dm, ds = [], []
        for k, p in P["LS"].items():
            d = np.array(p) - L
            az_g = float(np.degrees(np.arctan2(-d[1], -d[0])))     # listener faces -x, left = -y
            el = float(np.degrees(np.arctan2(d[2], np.hypot(d[0], d[1]))))
            x, fs = sf.read(os.path.join(a.bras, SCENES[hall], "BRIRs", "wav", f"{hall}_BRIR_LS{k}_MP6_HATO0.wav"))
            x = x.T
            on = int(np.argmax(np.abs(x).max(0) > 0.1 * np.abs(x).max()))
            seg = x[:, max(0, on - int(0.001 * fs)): on + int(0.003 * fs)]
            azF, itF, _ = hrir_table(a.fabian, el)
            az_m = az_from_itd(itd(seg, fs), azF, itF)
            simf = glob.glob(os.path.join(a.sim, f"bras_brir_{hall}_FABIAN_K8data_cal16_LS{k}_sim.wav"))
            az_s = np.nan
            if simf:
                y, fs2 = sf.read(simf[0])
                y = y.T
                on2 = int(np.argmax(np.abs(y).max(0) > 0.1 * np.abs(y).max()))
                azK, itK, _ = hrir_table(a.ku100, el)
                az_s = az_from_itd(itd(y[:, max(0, on2 - int(0.001 * fs2)): on2 + int(0.003 * fs2)], fs2), azK, itK)
            dm.append(abs(az_m - az_g)); ds.append(abs(az_s - az_g))
            lines.append(f"| {hall} | LS{k} | {az_g:+.1f} | {az_m:+.1f} | {az_s:+.1f} |")
        summ.append(f"{hall}: mean abs. deviation from the geometry: measured {np.mean(dm):.1f} deg, AuralPaths "
                    f"{np.nanmean(ds):.1f} deg")
    print("\n".join(lines + [""] + summ))


if __name__ == "__main__":
    main()
