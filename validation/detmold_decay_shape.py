"""
Detmold (drawn hall): where in time do the measured and the simulated decay differ? (diagnostic, 2026-11-15)

As validation/arvedi_decay_shape.py. The 24 omnidirectional-microphone positions of the calibration (S2, S3 to 12
seats), loudspeaker as in the hall check (generic 90 degree pattern aimed as in the config), the page's engine
(engine_js.py), 80000 rays. Per position the octave-band energy histogram from the direct sound on (measured: the
onset as in detmold_kh.py setup; simulated: the geometric direct time), normalised to unit energy; mean over the
positions. Materials: the calibrations of validation/detmold_js.py (out/detmold_js/cal_either.json, cal_mix.json).

    python validation/detmold_decay_shape.py <config.json> <t30.csv> <DetmoldSRIR_v01 folder> <cal_*.json> [--mix]
"""
import copy
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path[:0] = [ROOT, HERE]
import brir_proto as bp                       # noqa: E402
import engine_js                              # noqa: E402
import validate_bras_cr as vb                 # noqa: E402
from arvedi_decay_shape import AT, BANDS, WIN  # noqa: E402
from detmold_js import positions              # noqa: E402


def unit(e, i0, n=1500):
    e = np.asarray(e, float)[:, i0:i0 + n]
    e = np.pad(e, ((0, 0), (0, n - e.shape[1])))
    return e / e.sum(1, keepdims=True)


def main():
    import soundfile as sf
    cfg = copy.deepcopy(bp.load_config(sys.argv[1]))
    pos = positions(sys.argv[2])
    cal = json.load(open(sys.argv[4]))
    mix = "--mix" in sys.argv
    for g, al in cal["alpha"].items():
        full = cfg["geometry"]["materials"][g]["alpha"]
        cfg["geometry"]["materials"][g]["alpha"] = list(al) + [al[-1]] * max(0, len(full) - len(al))
    M, S = [], []
    for s in sorted({lab.split("_")[0] for lab in pos}):
        labs = [lab for lab in pos if lab.startswith(s + "_")]
        cfg["sources"][s]["pos"] = pos[labs[0]]["src"]
        cfg["receivers"] = {lab: pos[lab]["rec"] for lab in labs}
        H, cen = engine_js.energy_hists(cfg, s, labs, n_rays=80000, seed=1, mix=True if mix else None)
        bi = [int(np.argmin(np.abs(np.asarray(cen) - b))) for b in BANDS]
        for lab in labs:
            x, fs = sf.read(os.path.join(sys.argv[3], "SetC_DenseKH_LSOrchestra", "Data", "Omni", f"{s}{lab.split('_')[1]}.wav"))
            x = x if x.ndim == 1 else x[:, 0]
            on = int(np.argmax(np.abs(x) > 0.1 * np.abs(x).max())) / fs
            M.append(unit(vb.measured_hist(x, fs), int(np.floor(on / bp.HIST_BIN))))
            t0 = np.linalg.norm(np.subtract(pos[lab]["src"], pos[lab]["rec"])) / cfg["c"]
            S.append(unit(H[lab][bi], int(np.floor(t0 / bp.HIST_BIN))))
    M, S = np.mean(M, 0), np.mean(S, 0)
    print(f"{len(pos)} positions, {'mixed direction' if mix else 'either-or scattering'}. Window energy, dB re total: measured / simulated (difference)")
    print("band    " + "  ".join(f"{a}-{b} ms".rjust(19) for a, b in zip(WIN[:-1], WIN[1:])))
    for i, b in enumerate(BANDS):
        row = [f"{10 * np.log10(M[i, a:c].sum()):6.1f}/{10 * np.log10(S[i, a:c].sum()):6.1f} ({10 * np.log10(S[i, a:c].sum() / M[i, a:c].sum()):+.1f})"
               for a, c in zip(WIN[:-1], WIN[1:])]
        print(f"{b:5d}   " + "  ".join(x.rjust(19) for x in row))
    print("\nBackward-integrated decay of the mean histogram (dB): measured / simulated (difference)")
    print("band    " + "  ".join(f"{a} ms".rjust(19) for a in AT))
    for i, b in enumerate(BANDS):
        em, es = np.cumsum(M[i][::-1])[::-1], np.cumsum(S[i][::-1])[::-1]
        print(f"{b:5d}   " + "  ".join(f"{10 * np.log10(em[a]):6.1f}/{10 * np.log10(es[a]):6.1f} ({10 * np.log10(es[a] / em[a]):+.1f})".rjust(19) for a in AT))


if __name__ == "__main__":
    main()
