"""
Where the IACC_E3 difference of the BRAS binaural check comes from (needs the simulated BRIRs written by
check_bras_brir.py, which are not kept in the repository).

    python validation/iacc_split.py <BRAS folder> [--tag _K8] [--out validation/bras_brir_iacc_split.md]

Per octave band (500 Hz / 1 kHz / 2 kHz), in the 0 - 80 ms window of IACC_E3 (onset - 0.5 ms):
  - IACC = max |normalised cross-correlation| over +-1 ms, as brir_proto.iacc_e3 (3rd-order Butterworth octave bands);
  - split of the normalised cross-correlation at the lag of the direct-sound peak into the part of the first 3.5 ms
    ("direct": direct sound plus anything within 3 ms of it) and the rest (cross terms included);
  - energy shares of 0 - 3 / 3 - 20 / 20 - 50 / 50 - 80 ms (broadband, both ears).
Data: BRAS (Aspoeck et al. 2020, https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0).
"""
import argparse
import glob
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import brir_proto as bp                                                    # noqa: E402

BANDS = (500, 1000, 2000)
WINS = ((0, .003), (.003, .02), (.02, .05), (.05, .08))


def split(x, fs):
    t0 = bp.onset_time(x, fs) - 0.0005
    n0, n80, lag = int(t0 * fs), int(t0 * fs) + int(0.08 * fs), int(0.001 * fs)
    rows = []
    for fc in BANDS:
        sos = signal.butter(3, [fc / np.sqrt(2), fc * np.sqrt(2)], "bandpass", fs=fs, output="sos")
        y = signal.sosfiltfilt(sos, x, axis=-1)[:, n0:n80]
        E = np.sqrt(np.sum(y[0] ** 2) * np.sum(y[1] ** 2)); mid = y.shape[1] - 1
        cc = signal.correlate(y[0], y[1], "full")[mid - lag:mid + lag + 1] / E
        d = y.copy(); d[:, int(0.0035 * fs):] = 0
        ccd = signal.correlate(d[0], d[1], "full")[mid - lag:mid + lag + 1] / E
        k = int(np.argmax(np.abs(ccd)))
        rows.append((float(np.max(np.abs(cc))), float(ccd[k]), float(cc[k] - ccd[k])))
    e = lambda a, b: np.sum(x[:, n0 + int(a * fs):n0 + int(b * fs)] ** 2)
    shares = [100 * e(a, b) / e(0, 0.08) for a, b in WINS]
    return rows, shares


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras"); ap.add_argument("--tag", default="_K8")
    ap.add_argument("--out", default=os.path.join(HERE, "bras_brir_iacc_split.md"))
    a = ap.parse_args()
    md = ["# BRAS binaural check: where the IACC_E3 difference comes from", "",
          f"Simulated: `bras_brir_<hall>{a.tag}_LSk_sim.wav` (check_bras_brir.py). Script: `validation/iacc_split.py`. Data: BRAS "
          "(Aspöck et al. 2020, https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0).", "",
          "Per band: IACC (0–80 ms) = direct (first 3.5 ms) + rest, both as normalised cross-correlation at the lag of the "
          "direct-sound peak. Energy shares: broadband, both ears, ms after onset − 0.5 ms.", ""]
    for hall in ("CR3", "CR4"):
        md += [f"## {hall}", "", "| source | | " + " | ".join(f"{b} Hz IACC = direct + rest" for b in BANDS) +
               " | energy 0–3 / 3–20 / 20–50 / 50–80 ms (%) |", "|---|---|" + "---|" * (len(BANDS) + 1)]
        for k in range(3, 8):
            sim = os.path.join(HERE, f"bras_brir_{hall}{a.tag}_LS{k}_sim.wav")
            meas = glob.glob(os.path.join(a.bras, f"{hall}*", "BRIRs", "wav", f"{hall}_BRIR_LS{k}_MP6_HATO0.wav"))
            if not meas or not os.path.exists(sim):
                continue
            for name, f in (("measured", meas[0]), ("simulated", sim)):
                x, fs = sf.read(f); rows, sh = split(x.T, fs)
                md.append(f"| {'LS%d' % k if name == 'measured' else ''} | {name} | " +
                          " | ".join(f"{v:.2f} = {d:+.2f} {r:+.2f}" for v, d, r in rows) + " | " + " / ".join(f"{s:.0f}" for s in sh) + " |")
        md.append("")
    open(a.out, "w", encoding="utf-8").write("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
