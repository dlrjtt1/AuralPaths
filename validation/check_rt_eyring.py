"""
Sanity check of the ray tracer used by the Python engine (pyroomacoustics) in a shoebox with uniform absorption,
where the diffuse-field formulas are expected to hold: T30 from the ray-traced energy histogram vs Sabine
(0.161 V / (S alpha)) and Eyring (0.161 V / (-S ln(1 - alpha))).

    python validation/check_rt_eyring.py

Result on 2026-11-05 (pyroomacoustics 0.10.1, 20 000 rays, 12 x 9 x 7 m, no air absorption):
    alpha 0.05: s 0.1 -> 4.55 s, s 0.7 -> 4.68 s   (Sabine 4.77, Eyring 4.65)
    alpha 0.15: s 0.1 -> 1.54 s, s 0.7 -> 1.49 s   (Sabine 1.59, Eyring 1.47)
    alpha 0.30: s 0.1 -> 0.75 s, s 0.7 -> 0.69 s   (Sabine 0.80, Eyring 0.67)
With enough scattering the ray tracer follows Eyring within 1-3 %; with little scattering it lies between Eyring
and Sabine (up to +12 % over Eyring at alpha 0.3).
"""
import numpy as np
import pyroomacoustics as pra

L = np.array([12.0, 9.0, 7.0])
V, S = L.prod(), 2 * (L[0] * L[1] + L[0] * L[2] + L[1] * L[2])
for a in (0.05, 0.15, 0.3):
    for s in (0.1, 0.7):
        room = pra.ShoeBox(L, fs=16000, materials=pra.Material(a, s), max_order=0, ray_tracing=True, air_absorption=False)
        room.set_ray_tracing(n_rays=20000, receiver_radius=0.5, hist_bin_size=0.004, time_thres=4, energy_thres=1e-9)
        room.add_source([3, 3, 1.5])
        room.add_microphone([8, 5, 1.2])
        room.ray_tracing()
        e = np.asarray(room.rt_histograms[0][0][0])[0]
        edc = 10 * np.log10(np.cumsum(e[::-1])[::-1] / e.sum() + 1e-30)
        t = (np.arange(len(e)) + 0.5) * 0.004
        sel = (edc <= -5) & (edc >= -35)
        T = -60 / np.polyfit(t[sel], edc[sel], 1)[0]
        print(f"alpha {a} s {s}: ray tracing T30 {T:.2f} s, Sabine {0.161 * V / (S * a):.2f}, "
              f"Eyring {0.161 * V / (-S * np.log(1 - a)):.2f}")
