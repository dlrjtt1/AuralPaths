"""
Check the edge-diffraction model (diffraction.py, UTD) against measured impulse responses of the BRAS database,
reference scene RS5 "simple diffraction (infinite edge)": a thin partition standing on a reflecting floor.

    python validate_bras.py <RS5_RIRs.sofa> [--out bras_RS5] [--source-strength 0.4] [--pre-ms 0.5] [--tail-guard-ms 0.3]

Data (not included): Aspoeck, Brinkmann, Ackermann, Weinzierl, Vorlaender (2020), BRAS - Benchmark for Room Acoustical
Simulation, v3, https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0 (licence stated in the SOFA file).
Download "1_scene_descriptions-RS5.zip"; the RIRs are in RIRs/RS5_RIRs.sofa (16 IRs, Pa, 44.1 kHz).

Scene geometry (RS5 RIR.png / documentation): MDF partition 25 mm thick, 2.066 m high, 4.75 m wide, front face at
x = 5.487 m, centred at y = 2.985 m, on a hard tiled floor (z = 0) in a hemi-anechoic chamber. Loudspeakers
(Genelec 8020c) at x = 2.487 m, microphones at x = 8.512 m; positions are read from the SOFA file. The defaults below
are these values; change them with --edge-x / --edge-z / --y-span / --thickness for another single-edge scene.

Model (what is compared):
  partition = thin rigid half-plane (n = 2) in the plane x = front face + thickness / 2; the 25 mm thickness is not
  modelled (it splits the edge into two right-angle edges; affects mainly frequencies above ~ c / (2 * 25 mm)).
  floor = perfectly reflecting plane z = 0 (image method): geometrical paths S->R and S'->R when not blocked by the
  partition, and the four diffraction paths S->E->R, S'->E->R, S->E->R', S'->E->R' (image source / receiver in the
  floor), UTD coefficients from diffraction.utd, all summed with their delays.
  source = point source of strength --source-strength Pa at 1 m, flat in frequency: the SOFA file states that the
  loudspeaker was calibrated to 80 dB SPL at 1 kHz on axis at 2 m (0.2 Pa at 2 m -> 0.4 Pa at 1 m). The loudspeaker's
  frequency response and directivity are NOT included (their data are in a separate BRAS archive), so deviations away
  from 1 kHz contain the loudspeaker as well as the model error.
Comparison: measured and predicted IRs are cut with the same window, from the first predicted arrival - pre-ms to
the first arrival via the partition's vertical side edges (not modelled) - tail-guard-ms, and compared in third-octave
bands; bands below 2 / window length are marked as not resolved.
"""
import argparse
import csv
import math
import os
import sys

import numpy as np

import diffraction as df

THIRD = 1000 * 2.0 ** (np.arange(-10, 14) / 3)       # 100 Hz ... 20 kHz


def band_db(X, f, bands):
    out = []
    for fc in bands:
        sel = (f >= fc / 2 ** (1 / 6)) & (f < fc * 2 ** (1 / 6))
        out.append(10 * np.log10(np.mean(np.abs(X[sel]) ** 2) + 1e-30) if sel.any() else np.nan)
    return np.array(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sofa")
    ap.add_argument("--edge-x", type=float, default=5.487, help="front face of the partition (m)")
    ap.add_argument("--thickness", type=float, default=0.025)
    ap.add_argument("--edge-z", type=float, default=2.066)
    ap.add_argument("--y-span", default="0.61,5.36", help="partition extent in y (m)")
    ap.add_argument("--c", type=float, default=343.4, help="speed of sound (20.3 C in the documentation)")
    ap.add_argument("--source-strength", type=float, default=0.4)
    ap.add_argument("--pre-ms", type=float, default=0.5)
    ap.add_argument("--tail-guard-ms", type=float, default=0.3)
    ap.add_argument("--out", default="bras_RS5")
    a = ap.parse_args()

    import sofar
    s = sofar.read_sofa(a.sofa, verify=False, verbose=False)
    ir = np.asarray(s.Data_IR, float)[:, 0, :]
    fs = float(np.atleast_1d(s.Data_SamplingRate)[0])
    E = np.asarray(s.EmitterPosition, float)[0].T
    R = np.asarray(s.ReceiverPosition, float)[0].T
    eid = np.asarray(s.EmitterID).ravel().astype(int)
    rid = np.asarray(s.ReceiverID).ravel().astype(int)

    xp = a.edge_x + a.thickness / 2
    y0, y1 = (float(v) for v in a.y_span.split(","))
    zt, c = a.edge_z, a.c
    t, t0, n0 = np.array([0, 1.0, 0]), np.array([0, 0, -1.0]), np.array([-1.0, 0, 0])
    img = lambda p: np.array([p[0], p[1], -p[2]])

    def blocked(P, Q):
        """unfolded straight path P -> Q (either may be a floor image) passes through the partition?"""
        if (P[0] - xp) * (Q[0] - xp) >= 0:
            return False
        u = (xp - P[0]) / (Q[0] - P[0])
        y, z = P[1] + u * (Q[1] - P[1]), abs(P[2] + u * (Q[2] - P[2]))      # fold at the floor
        return y0 <= y <= y1 and z <= zt

    def side_path(S_, R_):
        best = np.inf
        for ye in (y0, y1):
            for Sx in (S_, img(S_)):
                for Rx in (R_, img(R_)):
                    zs = np.linspace(-zt, zt, 401)
                    P = np.c_[np.full_like(zs, xp), np.full_like(zs, ye), zs]
                    best = min(best, np.min(np.linalg.norm(P - Sx, axis=1) + np.linalg.norm(P - Rx, axis=1)))
        return best

    nfft = 1 << 15
    f = np.fft.rfftfreq(nfft, 1 / fs)
    fl = np.geomspace(20, fs / 2, 400)
    rows, summary = [], []
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(4, 4, figsize=(15, 11), sharex=True, sharey=True)
    for m in range(len(ir)):
        S_, R_ = E[m], R[m]
        H = np.zeros(len(f), complex)
        arrivals = []
        for Sx in (S_, img(S_)):                                     # geometrical paths
            L = np.linalg.norm(R_ - Sx)
            if not blocked(Sx, R_):
                H += np.exp(-2j * np.pi * f * L / c) / L
                arrivals.append(L)
        for Sx in (S_, img(S_)):                                     # four diffraction paths
            for Rx in (R_, img(R_)):
                zs, zr = (Sx - [xp, 0, zt]) @ t, (Rx - [xp, 0, zt]) @ t
                ws, wr = (Sx - [xp, 0, zt]) - zs * t, (Rx - [xp, 0, zt]) - zr * t
                rs, rr = np.linalg.norm(ws), np.linalg.norm(wr)
                z = zs + (zr - zs) * rs / (rs + rr)
                Q = np.array([xp, 0, zt]) + z * t
                s0, s1 = np.linalg.norm(Sx - Q), np.linalg.norm(Rx - Q)
                ang = lambda w: math.atan2(w @ n0, w @ t0) % (2 * math.pi)
                D = df.utd(2.0, ang(wr), ang(ws), s1, s0, rs / s0, fl, c, np.ones(len(fl)), np.ones(len(fl)))
                Dm = np.interp(f, fl, D.real) + 1j * np.interp(f, fl, D.imag)
                H += Dm * np.exp(-2j * np.pi * f * (s0 + s1) / c)
                arrivals.append(s0 + s1)
        H *= a.source_strength
        H[0] = 0
        pred = np.fft.irfft(H, nfft)[: ir.shape[1]]
        t_first = min(arrivals) / c
        t_end = side_path(S_, R_) / c - a.tail_guard_ms / 1000
        i0, i1 = int((t_first - a.pre_ms / 1000) * fs), int(t_end * fs)
        w = np.zeros(ir.shape[1]); w[i0:i1] = 1
        nt = max(4, int(0.0002 * fs))
        w[i0:i0 + nt] = np.hanning(2 * nt)[:nt]; w[i1 - nt:i1] = np.hanning(2 * nt)[nt:]
        x = ir[m]
        onset = int(np.argmax(np.abs(x) > 0.2 * np.max(np.abs(x)))) / fs
        po = int(np.argmax(np.abs(pred) > 0.2 * np.max(np.abs(pred)))) / fs
        Mb = band_db(np.fft.rfft(x * w, nfft), f, THIRD)
        Pb = band_db(np.fft.rfft(pred * w, nfft), f, THIRD)
        ok = THIRD >= 2 / (t_end - t_first + a.pre_ms / 1000)
        d = Pb - Mb
        lit = not blocked(S_, R_)
        label = f"LS{eid[m]}-MP{rid[m]}"
        print(f"{label}: S z={S_[2]:.3f} R z={R_[2]:.3f} {'direct visible' if lit else 'shadow'}; first arrival "
              f"{1000 * t_first:.2f} ms (onset pred {1000 * po:.2f}, meas {1000 * onset:.2f}); window {1000 * (t_end - t_first):.1f} ms, "
              f"resolved from {THIRD[ok][0]:.0f} Hz")
        for i, fc in enumerate(THIRD):
            rows.append({"ir": label, "lit": lit, "band_hz": round(fc, 1), "measured_db": round(Mb[i], 2),
                         "predicted_db": round(Pb[i], 2), "diff_db": round(d[i], 2), "resolved": bool(ok[i])})
        sel = ok & (THIRD >= 250) & (THIRD <= 8000)
        mid = ok & (THIRD >= 500) & (THIRD <= 2000)
        summary.append((label, lit, float(np.mean(d[sel])), float(np.mean(np.abs(d[sel]))), float(np.mean(np.abs(d[mid])))))
        ax = axs[(rid[m] - 1)][(eid[m] - 1)]
        ax.semilogx(THIRD, Mb, "k-", lw=1.4, label="measured")
        ax.semilogx(THIRD, Pb, "C1--", lw=1.4, label="UTD + floor")
        ax.axvspan(THIRD[0] / 1.2, THIRD[ok][0] / 1.12, color="0.92")
        ax.set_title(f"{label} ({'lit' if lit else 'shadow'})", fontsize=9); ax.grid(alpha=0.3)
    for ax in axs[-1]:
        ax.set_xlabel("Hz")
    for ax in axs[:, 0]:
        ax.set_ylabel("dB re 1 Pa")
    axs[0][0].legend(fontsize=8)
    fig.suptitle("BRAS RS5: measured vs. UTD (thin half-plane, rigid floor, flat source calibrated at 1 kHz)", fontsize=11)
    fig.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    fig.savefig(a.out + ".png", dpi=110)
    with open(a.out + ".csv", "w", newline="", encoding="utf-8") as fo:
        wr_ = csv.DictWriter(fo, fieldnames=list(rows[0])); wr_.writeheader(); wr_.writerows(rows)
    lines = ["| IR | direct | mean diff 250 Hz-8 kHz (dB) | mean abs 250 Hz-8 kHz (dB) | mean abs 500 Hz-2 kHz (dB) |", "|---|---|---|---|---|"]
    for lab, lit, md, ma, mm in summary:
        lines.append(f"| {lab} | {'visible' if lit else 'shadow'} | {md:+.1f} | {ma:.1f} | {mm:.1f} |")
    sh = [x for x in summary if not x[1]]
    lines += ["", f"Shadow IRs ({len(sh)}): mean abs 500 Hz-2 kHz {np.mean([x[4] for x in sh]):.1f} dB, "
              f"250 Hz-8 kHz {np.mean([x[3] for x in sh]):.1f} dB; all IRs: {np.mean([x[4] for x in summary]):.1f} / "
              f"{np.mean([x[3] for x in summary]):.1f} dB"]
    open(a.out + ".md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"-> {a.out}.png, {a.out}.csv, {a.out}.md")


if __name__ == "__main__":
    main()
