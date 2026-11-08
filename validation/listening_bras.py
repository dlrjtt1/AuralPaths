"""
Stimuli for a listening test of AuralPaths against measured BRIRs: BRAS CR3 / CR4, listener MP6, loudspeakers LS3-LS7,
measured BRIR (FABIAN, HATO 0) vs AuralPaths BRIR rendered with the same head (FABIAN HRIRs of the BRAS release,
tools/fabian_to_sofa.py) and the same loudspeaker (measured QSC K8 directivity and on-axis response, --k8-mps), from
check_bras_brir.py --out validation/bras_brir_<hall>_FABIAN_K8data. Design (plausibility + SAQI attribute ratings,
static binaural, one headphone) after the perceptual part of the BRAS round robin (Brinkmann et al. 2019,
https://doi.org/10.1121/1.5096178); see validation/listening_bras_protocol.md.

    python validation/listening_bras.py <BRAS folder> <dry.wav> [--tag _FABIAN_K8data] [--out out/listening_bras]
                                        [--brir-s 2.5] [--lufs -26]

For every hall and loudspeaker: measured.wav, simulated.wav, and the dry signal convolved with each. Both BRIRs are
cut to the same length (--brir-s, the simulated length) with a 50 ms cosine fade, the simulated one is shifted so its
onset matches the measured onset to the sample, and each stimulus is set to the same integrated loudness
(ITU-R BS.1770 via pyloudnorm) so that level is not a cue. No headphone compensation is applied (the same headphone
plays both versions). stimuli.csv lists per file the onsets, the shift, the gain, the loudness before and after and
a SHA-256.

Licences of the outputs: the measured BRIRs are BRAS data (CC BY-SA 4.0); stimuli made with the pyfar guitar sample
(excerpt of Flamenco2_U89.wav, TH Koeln Audio Group, CC BY-SA) are derivatives of both and stay under CC BY-SA with
both attributions. They are not bundled in the repository.
"""
import argparse
import csv
import glob
import hashlib
import os
import sys

import numpy as np
import soundfile as sf
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import brir_proto as bp                    # noqa: E402

SCENES = {"CR3": "CR3*", "CR4": "CR4*"}


def fade(x, fs, ms=50.0):
    n = int(ms / 1000 * fs)
    w = np.ones(x.shape[-1]); w[-n:] = 0.5 * (1 + np.cos(np.linspace(0, np.pi, n)))
    return x * w


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("bras"); ap.add_argument("dry")
    ap.add_argument("--tag", default="_FABIAN_K8data"); ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "listening_bras"))
    ap.add_argument("--brir-s", type=float, default=2.5); ap.add_argument("--lufs", type=float, default=-26.0)
    a = ap.parse_args()
    import pyloudnorm
    dry, fsd = sf.read(a.dry, always_2d=True); dry = dry.mean(axis=1)
    fs = 44100
    if fsd != fs:
        g = np.gcd(fsd, fs); dry = signal.resample_poly(dry, fs // g, fsd // g)
    meter = pyloudnorm.Meter(fs)
    os.makedirs(a.out, exist_ok=True)
    rows = []
    for hall in ("CR3", "CR4"):
        for k in range(3, 8):
            mp = glob.glob(os.path.join(a.bras, SCENES[hall], "BRIRs", "wav", f"{hall}_BRIR_LS{k}_MP6_HATO0.wav"))
            sp = os.path.join(HERE, f"bras_brir_{hall}{a.tag}_LS{k}_sim.wav")
            if not mp or not os.path.exists(sp):
                continue
            m, fm = sf.read(mp[0]); s, fss = sf.read(sp)
            if fm != fs or fss != fs:
                raise SystemExit("expected 44.1 kHz BRIRs")
            m, s = m.T, s.T
            n = int(a.brir_s * fs)
            tm, ts = bp.onset_time(m, fs), bp.onset_time(s, fs)
            shift = int(round((tm - ts) * fs))
            s = np.roll(np.pad(s, ((0, 0), (0, max(0, n - s.shape[1])))), shift, axis=1)
            if shift > 0:
                s[:, :shift] = 0
            elif shift < 0:
                s[:, shift:] = 0          # np.roll wrapped the start of the BRIR to the end
            m = fade(np.pad(m, ((0, 0), (0, max(0, n - m.shape[1]))))[:, :n], fs)
            s = fade(s[:, :n], fs)
            for kind, h in (("measured", m), ("simulated", s)):
                y = np.stack([signal.fftconvolve(dry, h[0]), signal.fftconvolve(dry, h[1])])
                l0 = meter.integrated_loudness(y.T)
                g = 10 ** ((a.lufs - l0) / 20); y = y * g
                peak = float(np.abs(y).max())
                name = f"{hall}_LS{k}_{kind}.wav"
                sf.write(os.path.join(a.out, name), y.T.astype(np.float32), fs, subtype="PCM_24")
                sf.write(os.path.join(a.out, f"{hall}_LS{k}_{kind}_brir.wav"), h.T.astype(np.float32), fs, subtype="FLOAT")
                rows.append(dict(file=name, hall=hall, source=f"LS{k}", kind=kind, onset_ms=round(1000 * (tm if kind == "measured" else ts), 3),
                                 shift_samples=shift if kind == "simulated" else 0, loudness_in_lufs=round(l0, 2),
                                 gain_db=round(20 * np.log10(g), 2), loudness_out_lufs=round(meter.integrated_loudness(y.T), 2),
                                 peak_dbfs=round(20 * np.log10(peak), 2),
                                 sha256=hashlib.sha256(open(os.path.join(a.out, name), "rb").read()).hexdigest()))
    with open(os.path.join(a.out, "stimuli.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"{len(rows)} stimuli in {a.out}; peak max {max(r['peak_dbfs'] for r in rows):.1f} dBFS")


if __name__ == "__main__":
    main()
