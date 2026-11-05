"""
Sanity check of the ray tracer used by the Python engine (pyroomacoustics) in a shoebox with uniform absorption,
where the diffuse-field formulas are expected to hold: T30 from the ray-traced energy histogram vs Sabine
(0.161 V / (S alpha)) and Eyring (0.161 V / (-S ln(1 - alpha))).

    python validation/check_rt_eyring.py

Result on 2026-11-06 (pyroomacoustics 0.10.1, 20 000 rays, 12 x 9 x 7 m, no air absorption, energy_thres 1e-20,
see brir_proto.RT_ENERGY_THRES):
    alpha 0.05: s 0.1 -> 4.63 s, s 0.7 -> 4.99 s   (Sabine 4.77, Eyring 4.65)
    alpha 0.15: s 0.1 -> 1.55 s, s 0.7 -> 1.60 s   (Sabine 1.59, Eyring 1.47)
    alpha 0.30: s 0.1 -> 0.75 s, s 0.7 -> 0.75 s   (Sabine 0.80, Eyring 0.67)
With strong scattering the traced T30 lies 7-12 % above Eyring, close to Sabine: the spread of the free path lengths
slows the mean decay (validation/check_box_lambert.js derives and checks this for the browser tracer, which gives the
same values on a tiled box). The earlier result with energy_thres 1e-9 (within 1-3 % of Eyring at s 0.7) was too
short: that setting dropped the scattered energy from about 0.5 s on.
"""
import os
import sys

import numpy as np
import pyroomacoustics as pra

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import brir_proto as bp  # noqa: E402  (RT_ENERGY_THRES)

L = np.array([12.0, 9.0, 7.0])
V, S = L.prod(), 2 * (L[0] * L[1] + L[0] * L[2] + L[1] * L[2])
for a in (0.05, 0.15, 0.3):
    for s in (0.1, 0.7):
        room = pra.ShoeBox(L, fs=16000, materials=pra.Material(a, s), max_order=0, ray_tracing=True, air_absorption=False)
        room.set_ray_tracing(n_rays=20000, receiver_radius=0.5, hist_bin_size=0.004, time_thres=4, energy_thres=bp.RT_ENERGY_THRES)
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
