"""
Steady sine test signals for the AuralPaths listening panel.

    python test_signals/make_sines.py

Writes 48 kHz / 24-bit mono WAVs, 10 s, peak -12 dBFS, 20 ms raised-cosine fades:
  sine_500Hz_10s.wav    (load as the amplified source)
  sine_1000Hz_10s.wav   (load as an unamplified source)
500 Hz and 1 kHz are the two octave bands the C80/D50/Ts/EDT/T30 values are averaged over.
"""
import os

import numpy as np
import soundfile as sf

FS = 48000
DUR = 10.0
PEAK_DBFS = -12.0
FADE = 0.02
HERE = os.path.dirname(os.path.abspath(__file__))


def sine(freq):
    t = np.arange(int(FS * DUR)) / FS
    x = np.sin(2 * np.pi * freq * t) * 10 ** (PEAK_DBFS / 20)
    n = int(FS * FADE)
    ramp = 0.5 - 0.5 * np.cos(np.pi * np.arange(n) / n)
    x[:n] *= ramp
    x[-n:] *= ramp[::-1]
    return x


if __name__ == "__main__":
    for f in (500, 1000):
        path = os.path.join(HERE, f"sine_{f}Hz_10s.wav")
        sf.write(path, sine(f), FS, subtype="PCM_24")
        print(path)
