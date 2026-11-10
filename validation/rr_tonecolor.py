"""
Tone colour as in the round robin (Brinkmann et al. 2019, https://doi.org/10.1121/1.5096178, sec. II.D and III.B.2,
Fig. 6): energetic differences between simulated and measured BRIRs in 37 auditory (gammatone) filter bands between
80 Hz and 16 kHz, averaged across the source positions and both ears, head in neutral orientation, for the BRAS rooms
CR2, CR3 and CR4 (five loudspeakers LS3 - LS7 to listener MP6; rooms without simulated BRIRs are skipped).

    python validation/rr_tonecolor.py <BRAS folder> --sim out/rs/tc [--tag ""]

<sim>/<CRn><tag>_LSk_sim.wav are written by validation/check_bras_brir.py (--out <sim>/<CRn>).

What the paper does not specify and is chosen here: band centres 1 ERB apart (Glasberg & Moore ERB-rate scale, 37
bands from 80 Hz; the paper used the gammatone filterbank of the Auditory Toolbox), 4th-order gammatone filters
(scipy.signal.gammatone, applied as power response to the spectrum), energy of the whole BRIR per band, level alignment of simulation and measurement by their
mean band level 200 Hz - 1 kHz (the round robin matched loudness by the log-magnitude average 200 Hz - 1 kHz), and the
"mean error" read as the mean over bands of the absolute difference after averaging over sources and ears (also
printed: the mean absolute difference before averaging). The round robin reports mean errors per program of
E 1.3 dB, B and C 2.2 dB, A 3.2 dB over its three rooms.
"""
import argparse
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE]
from check_bras_brir import SCENES      # noqa: E402


def centres(n=37, f0=80.0):
    e0 = 21.4 * np.log10(1 + 0.00437 * f0)
    return (10 ** ((e0 + np.arange(n)) / 21.4) - 1) / 0.00437


def band_db(x, fs, fc):
    """Band energies in dB [band, ear], from the spectrum weighted by each filter's power response (equal to the
    energy of the filtered signal by Parseval; avoids running the low-frequency IIR filters in time)."""
    n = 1 << int(np.ceil(np.log2(x.shape[1] + 1)))
    X = np.abs(np.fft.rfft(x, n, axis=1)) ** 2
    f = np.fft.rfftfreq(n, 1 / fs)
    out = []
    for c in fc:
        b, a = signal.gammatone(c, "iir", fs=fs)
        _, h = signal.freqz(b, a, worN=f, fs=fs)
        out.append(10 * np.log10((X * np.abs(h) ** 2).sum(axis=1) + 1e-30))
    return np.array(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras")
    ap.add_argument("--sim", required=True)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    fc = centres()
    ref = (fc >= 200) & (fc <= 1000)
    tot = []
    for hall in ("CR2", "CR3", "CR4"):
        if not os.path.exists(os.path.join(a.sim, f"{hall}{a.tag}_LS7_sim.wav")):
            continue
        D = []
        for k in range(3, 8):
            x, fs = sf.read(os.path.join(a.bras, SCENES[hall], "BRIRs", "wav", f"{hall}_BRIR_LS{k}_MP6_HATO0.wav"))
            y, fs2 = sf.read(os.path.join(a.sim, f"{hall}{a.tag}_LS{k}_sim.wav"))
            if fs2 != fs:
                y = signal.resample_poly(y, int(fs), int(fs2), axis=0)
            m, s = band_db(x.T, fs, fc), band_db(y.T, fs, fc)
            s += m[ref].mean() - s[ref].mean()
            D.append(s - m)
        D = np.array(D)                            # [source, band, ear]
        avg = D.mean(axis=(0, 2))
        tot.append(avg)
        print(f"{hall}: mean |difference averaged over sources and ears| {np.mean(np.abs(avg)):.1f} dB; "
              f"mean |difference| per source and ear {np.mean(np.abs(D)):.1f} dB")
        print("   band (Hz) / difference (dB): " + ", ".join(f"{f:.0f} {v:+.1f}" for f, v in zip(fc[::4], avg[::4])))
    print(f"all rooms: {np.mean(np.abs(np.array(tot))):.1f} dB")


if __name__ == "__main__":
    main()
