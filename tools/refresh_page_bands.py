"""
Refresh the band-dependent engine data in index.html (const D = ...) without rerunning run.py: air absorption
(brir_proto.make_room), the late-noise bank edges, the diffuse-field band energies and the directional late-field
tables of the HRIR set (export_viewer.late_tables). Everything else in the page data is kept as it is.

    python tools/refresh_page_bands.py <KU100.sofa>

Use after a change of brir_proto.OCT_CENTERS or of the air absorption; run.py / export_viewer.py write the same
fields when they rebuild the page.
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import brir_proto as bp       # noqa: E402
import export_viewer as ev    # noqa: E402


def main(sofa):
    p = os.path.join(ROOT, "index.html")
    s = open(p, encoding="utf-8").read()
    i = s.index("const D = ")
    j = s.index("\n", i)
    tail = s[i + len("const D = "):j]
    end = tail.rstrip()
    semi = end.endswith(";")
    D = json.loads(end.rstrip(";"))
    fs = D["fs"]
    import pyroomacoustics as pra
    r = pra.ShoeBox([5, 5, 5], fs=fs, air_absorption=True)
    bp._fix_air_above_table(r)
    hr = bp.load_hrir(sofa, fs)
    fb = bp.octave_filterbank(fs)
    old = {k: (len(D[k]) if k != "df" else len(D[k][0])) for k in ("air", "bankEdges", "df")}
    D["air"] = np.round(np.asarray(r.air_absorption), 6).tolist()
    D["bankEdges"] = [[float(lo), float(hi)] for lo, hi in fb["edges"]]
    D["df"] = np.round(hr.df_band_energy, 6).tolist()
    if D.get("lateDir"):
        D["lateDir"] = ev.late_tables(hr)
    new = "const D = " + json.dumps(D, separators=(",", ":"), ensure_ascii=False) + (";" if semi else "")
    open(p, "w", encoding="utf-8").write(s[:i] + new + s[j:])
    print(f"index.html: air {old['air']} -> {len(D['air'])} bands (16 kHz {D['air'][-1]}), bank {old['bankEdges']} -> "
          f"{len(D['bankEdges'])}, df {old['df']} -> {len(D['df'][0])}")


if __name__ == "__main__":
    main(sys.argv[1])
