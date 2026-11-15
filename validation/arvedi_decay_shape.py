"""
Arvedi S0: WHERE in time do the measured and the simulated decay differ? (diagnostic, 2026-11-15)

For every receiver the octave-band energy histogram from the direct sound on, normalised to unit energy; mean over
the 65 receivers. Printed per band: the energy in time windows after the direct sound (dB re total) and the
backward-integrated decay (dB) at fixed times, measured (meas_hist_*.npz of the dataset reduction) and simulated
(engine_js.py, 20000 rays).

    python validation/arvedi_decay_shape.py <calibrated config.json> <folder with meas_hist_*.npz> [--mix either|mix]
"""
import glob
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path[:0] = [ROOT, HERE]
import brir_proto as bp                       # noqa: E402
import engine_js                              # noqa: E402

BANDS = [125, 250, 500, 1000, 2000, 4000]
WIN = [0, 5, 20, 50, 80, 120, 200, 300, 500, 1000]      # ms after the direct sound
AT = [20, 50, 80, 120, 200, 300, 500]


def aligned(h, t0, n=1500):
    i0 = int(np.floor(t0 / bp.HIST_BIN))
    e = np.asarray(h, float)[:, i0:i0 + n]
    e = np.pad(e, ((0, 0), (0, n - e.shape[1])))
    return e / e.sum(1, keepdims=True)


def show(M, S, title):
    """Tables of the window energies and of the backward-integrated decay, measured / simulated [bands, 1 ms bins]."""
    print(f"{title}. Window energy, dB re total: measured / simulated (difference)")
    print("band    " + "  ".join(f"{a}-{b} ms".rjust(19) for a, b in zip(WIN[:-1], WIN[1:])))
    for i, b in enumerate(BANDS):
        row = []
        for a, c in zip(WIN[:-1], WIN[1:]):
            m, s = 10 * np.log10(M[i, a:c].sum()), 10 * np.log10(S[i, a:c].sum())
            row.append(f"{m:6.1f}/{s:6.1f} ({s - m:+.1f})")
        print(f"{b:5d}   " + "  ".join(x.rjust(19) for x in row))
    print("Backward-integrated decay of the mean histogram (dB): measured / simulated (difference)")
    print("band    " + "  ".join(f"{a} ms".rjust(19) for a in AT))
    for i, b in enumerate(BANDS):
        em, es = np.cumsum(M[i][::-1])[::-1], np.cumsum(S[i][::-1])[::-1]
        row = [f"{10 * np.log10(em[a]):6.1f}/{10 * np.log10(es[a]):6.1f} ({10 * np.log10(es[a] / em[a]):+.1f})" for a in AT]
        print(f"{b:5d}   " + "  ".join(x.rjust(19) for x in row))


def main():
    cfg = bp.load_config(sys.argv[1])
    mix = None if "--mix" not in sys.argv else sys.argv[sys.argv.index("--mix") + 1] == "mix"
    H = {}
    for f in sorted(glob.glob(os.path.join(sys.argv[2], "meas_hist_*.npz"))):
        H.update({k: v.astype(float) for k, v in np.load(f).items()})
    recs = [r for r in cfg["receivers"] if f"S0-{r}" in H]
    Hs, cen = engine_js.energy_hists(cfg, "S0", recs, t_max=2.0, n_rays=20000, seed=1, mix=mix)
    bi = [int(np.argmin(np.abs(np.asarray(cen) - b))) for b in BANDS]
    t0 = {r: np.linalg.norm(np.subtract(cfg["sources"]["S0"]["pos"], cfg["receivers"][r])) / cfg["c"] for r in recs}
    M = np.mean([aligned(H[f"S0-{r}"], t0[r]) for r in recs], 0)
    S = np.mean([aligned(Hs[r][bi], t0[r]) for r in recs], 0)
    show(M, S, f"{len(recs)} receivers, mean of the unit-energy histograms")


if __name__ == "__main__":
    main()
