"""
Seat-dip model (seatdip.py) against BRAS RS7: 15 blocks 0.12 m deep and 0.24 m high on a hard floor, 0.34 m apart
(Aspoeck et al., https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0). The 3-D direct sound times the 2-D BEM
transfer function T(f), windowed and compared in third-octave bands with the measured RIRs as in validation/bras_rs.py.

    python validation/rs7_seatdip_bem.py <folder holding "_unz/1 Scene descriptions"> [--out out/rs]

RS7 is about a 1:3.2 model of seat rows (0.24 m blocks for ~0.8 m seat backs), so the model settings are scaled:
elements at most seatdip.HMAX / 3.2 long, BEM up to 3.2 x seatdip.FMAX, and T on the bins of a 512-point FFT at
44.1 kHz (the engine's 2048 points at 48 kHz, in the time scale of the model). Same rows as the engine: the last
ROWS_FRONT blocks in front of the receiver and ROWS_BACK behind. Also prints the result with all 15 blocks.
First checks the BEM against the series solution for a rigid half-cylinder on a rigid floor.
"""
import argparse
import math
import os
import sys

import numpy as np
from scipy.special import hankel1, jvp, h1vp

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, ".."), HERE]
import bras_rs as b      # noqa: E402
import seatdip as sd     # noqa: E402

SCALE = 3.2
NF = 512


def check_cylinder():
    """BEM vs the series solution for a rigid half-cylinder (radius 0.3 m) on a rigid floor, line source."""
    a, S0 = 0.3, np.array([-2.0, 0.5])
    Rs = np.array([[1.5, 0.3], [0.0, 0.6], [3.0, 0.05], [-0.5, 1.0]])
    th = np.linspace(0, np.pi, 400)
    semi = np.c_[a * np.cos(th), a * np.sin(th)]
    worst = 0.0
    for fr in (200, 800, 2000):
        k = 2 * np.pi * fr / 343
        T = sd.transfer([semi], S0, Rs, np.array([fr]), c=343)[0]
        ref = []
        for x in Rs:
            p = 0
            for src in (S0, S0 * np.array([1, -1])):
                rs, ps = np.hypot(*src), np.arctan2(src[1], src[0])
                r, ph = np.hypot(*x), np.arctan2(x[1], x[0])
                p += 0.25j * hankel1(0, k * np.hypot(*(x - src)))
                for n in range(80):
                    p -= 0.25j * (1 if n == 0 else 2) * jvp(n, k * a) / h1vp(n, k * a) * hankel1(n, k * rs) * \
                        hankel1(n, k * r) * np.cos(n * (ph - ps))
            ref.append(p / (0.25j * hankel1(0, k * np.hypot(*(x - S0)))))
        worst = max(worst, float(np.max(np.abs(20 * np.log10(np.abs(T) / np.abs(ref))))))
    print(f"BEM vs analytic half-cylinder: max level difference {worst:.3f} dB")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "rs"))
    a = ap.parse_args()
    check_cylinder()
    ir, E, R, eid, rid = b.read_sofa(os.path.join(b.find_scene_dir(a.root, "RS7"), "RIRs", "RS7_RIRs.sofa"))
    nfft = 1 << int(math.ceil(math.log2(ir.shape[1])))
    f = np.fft.rfftfreq(nfft, 1 / b.FS)
    c = 331.3 * math.sqrt(1 + b.TEMP["RS7"] / 273.15)
    air = b.air_np(f, b.TEMP["RS7"], b.HUM["RS7"])
    xs = [3.958 + 0.34 * r for r in range(15)]
    TH = np.array(b.THIRD)
    sel = (TH >= 125) & (TH <= 4000)
    hmax, fmax = sd.HMAX, sd.FMAX
    sd.HMAX, sd.FMAX = hmax / SCALE, fmax * SCALE
    rows_out = []
    try:
        for label, front, back in (("engine rows", sd.ROWS_FRONT, sd.ROWS_BACK), ("all 15 blocks", 99, 0)):
            print(label)
            for i in range(len(eid)):
                S, Rr = E[i], R[i]
                before = [x for x in xs if x + 0.06 <= Rr[0]]
                use = (before[-(front + 1):] + [x for x in xs if x + 0.06 > Rr[0]][:back]) if front < 99 else xs
                x0 = use[0]
                seat = [(x0 - 0.06, 0), (x0 + 0.06, 0), (x0 + 0.06, 0.24), (x0 - 0.06, 0.24)]
                m = [int(round((x - x0) / 0.34)) for x in use]
                fb = np.arange(1, int(sd.FMAX * NF / b.FS) + 1) * b.FS / NF
                T = sd._continue(sd.transfer_rows(seat, m, 0.34, [S[0], S[2]], [Rr[0], Rr[2]], fb, c), fb, NF // 2 + 1)
                h = np.roll(np.fft.irfft(T, NF), NF // 8)
                L = float(np.linalg.norm(Rr - S))
                H = b.P1M * np.exp(-1j * 2 * np.pi * f / c * L - air * L) / L * np.fft.rfft(h, nfft) * \
                    np.exp(2j * np.pi * f * (NF // 8) / b.FS)
                xsim = np.fft.irfft(H * np.clip((12000 - f) / 2000, 0, 1), nfft)
                xm = np.zeros(nfft)
                xm[:ir.shape[1]] = ir[i]
                t0 = L / c
                d = (b.third_levels(b.window(xm, b.WIN["RS7"], t0), nfft) -
                     b.third_levels(b.window(xsim, b.WIN["RS7"], t0), nfft))
                dd = d[sel]
                print(f"  LS{eid[i]}-MP{rid[i]}: median meas - sim {np.median(dd):+.1f} dB, mean abs. {np.mean(np.abs(dd)):.1f} dB")
                for fc, v in zip(TH, d):
                    rows_out.append([label, f"LS{eid[i]}", f"MP{rid[i]}", int(fc), round(float(v), 2)])
    finally:
        sd.HMAX, sd.FMAX = hmax, fmax
    os.makedirs(a.out, exist_ok=True)
    import csv
    with open(os.path.join(a.out, "RS7_seatdip.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["rows", "source", "receiver", "f_hz", "measured_minus_sim_db"])
        w.writerows(rows_out)


if __name__ == "__main__":
    main()
