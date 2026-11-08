"""
Convert the FABIAN HRIRs of the BRAS release (CSV, top-pole grid) to a SOFA file that brir_proto.load_hrir reads.

    python tools/fabian_to_sofa.py <folder with HATO_0_1x1_64442_HRIR_L/R_top_pole.csv> out.sofa [--hato 0] [--step 2]

Data: BRAS, "2 Source and receiver descriptions / FABIAN HRIRs" (Aspoeck et al. 2020,
https://doi.org/10.14279/depositonce-6726.3, CC BY-SA 4.0; FABIAN: Brinkmann et al.). The SOFA file is a derivative
of CC BY-SA data: keep the attribution and the licence if you share it; it is not bundled here.

Format (BRAS documentation section on source and receiver descriptions): one line per direction, label AxxxE+yy then
256 samples at 44.1 kHz; top-pole grid, azimuth A in the horizontal plane (0 deg front), elevation E towards +z.
Left / right were checked on the data: at A = 90 deg the left ear leads by 23 samples and is 15 dB louder, so A
increases towards the left, as in SOFA spherical coordinates. HATO 0 is the head facing forward over the torso (the
BRAS CR3 / CR4 BRIRs are named ..._HATO0). --step keeps every n-th degree in A and E (the 1 deg grid has 64 442
directions; 2 deg gives about 16 000).
"""
import argparse
import os
import re

import numpy as np


def read(path):
    lab, ir = [], []
    with open(path) as f:
        for line in f:
            p = line.rstrip(",\n").split(",")
            if not p[0].startswith("A"):
                continue
            lab.append(p[0]); ir.append(np.array(p[1:], dtype=np.float32))
    return lab, np.array(ir)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder"); ap.add_argument("out"); ap.add_argument("--hato", default="0"); ap.add_argument("--step", type=int, default=2)
    a = ap.parse_args()
    import sofar
    lab, L = read(os.path.join(a.folder, f"HATO_{a.hato}_1x1_64442_HRIR_L_top_pole.csv"))
    labR, R = read(os.path.join(a.folder, f"HATO_{a.hato}_1x1_64442_HRIR_R_top_pole.csv"))
    if lab != labR:
        raise SystemExit("left and right files have different grids")
    m = [re.match(r"A(\d+)E([+-]\d+)", s) for s in lab]
    A = np.array([float(x.group(1)) for x in m]); E = np.array([float(x.group(2)) for x in m])
    keep = (A % a.step == 0) & (E % a.step == 0)
    s = sofar.Sofa("SimpleFreeFieldHRIR")
    s.Data_IR = np.stack([L[keep], R[keep]], axis=1).astype(float)
    s.Data_SamplingRate = 44100
    s.SourcePosition = np.c_[A[keep], E[keep], np.full(keep.sum(), 1.7)]
    s.SourcePosition_Type = "spherical"; s.SourcePosition_Units = "degree, degree, metre"
    s.GLOBAL_Title = f"FABIAN HRIRs, HATO {a.hato}, from BRAS (Aspoeck et al. 2020, doi:10.14279/depositonce-6726.3), CC BY-SA 4.0"
    s.GLOBAL_License = "CC BY-SA 4.0"
    s.GLOBAL_Comment = f"Converted by AuralPaths tools/fabian_to_sofa.py, every {a.step} deg of the 1 deg top-pole grid"
    sofar.write_sofa(a.out, s)
    print(a.out, int(keep.sum()), "directions")


if __name__ == "__main__":
    main()
