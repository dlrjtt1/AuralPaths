"""
Read the spectra of the round-robin simulators from the vector graphics of SuppPub2 (Brinkmann et al. 2019,
https://doi.org/10.1121/1.5096178) and reduce them to 1/3-octave levels, so that AuralPaths can be compared with
them on the same pairs and against the same measured curve. Scenes 1 - 4 (figures S2-1 - S2-6, S2-10 - S2-15,
S2-19, S2-22, S2-23); scene 5 is read by validation/rr_extract_rs5.py.

    python validation/rr_extract.py <supppub2.pdf> <out.csv>

Per figure: axes calibrated from its tick labels (frequency labels 100 / 1k on a log axis, the dB labels by a
linear fit), curves identified by the legend colours (A blue, C yellow, D cyan, E purple, F red, measurement grey).
Each figure is normalised by the rms of the windowed IR, so only the spectral shape is comparable.
"""
import csv
import re
import sys

import numpy as np
import pdfplumber

COLORS = {(0.0, 0.4471, 0.7412): "A", (0.9294, 0.6941, 0.1255): "C", (0.0, 0.7843, 0.7843): "D",
          (0.4941, 0.1843, 0.5569): "E", (0.7843, 0.1725, 0.0392): "F"}
FIGS = {1: ("RS1", "Rigid", "LS2", "MP2"), 2: ("RS1", "Rigid", "LS3", "MP3"),
        3: ("RS1", "Absorbing", "LS2", "MP2"), 4: ("RS1", "Absorbing", "LS3", "MP3"),
        5: ("RS1", "Diffuse", "LS2", "MP2"), 6: ("RS1", "Diffuse", "LS3", "MP3"),
        10: ("RS2", "1mPlate_rigid", "LS2", "MP2"), 11: ("RS2", "2mPlate_rigid", "LS2", "MP2"),
        12: ("RS2", "1mPlate_absorbing", "LS2", "MP2"), 13: ("RS2", "2mPlate_absorbing", "LS2", "MP2"),
        14: ("RS2", "1mPlate_rigid", "LS5", "MP4"), 15: ("RS2", "2mPlate_rigid", "LS5", "MP4"),
        19: ("RS3", "", "LS1", "MP1"), 22: ("RS4", "onCenter", "LS2", "MP2"), 23: ("RS4", "offCenter", "LS5", "MP5")}
THIRD = [100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000]


def name_of(col):
    if not isinstance(col, (tuple, list)):
        return "measured" if col is not None and abs(float(col) - 0.1294) < 0.01 else None
    for k, v in COLORS.items():
        if max(abs(a - b) for a, b in zip(k, col)) < 0.01:
            return v
    return None


def main():
    pdf, out = sys.argv[1], sys.argv[2]
    rows = []
    for pg in pdfplumber.open(pdf).pages:
        words = pg.extract_words()
        caps = []
        for i, w in enumerate(words):
            # "Figure S2-5:" may come out as one word ("FigureS2-5:") on some pages
            txt = w["text"] + (" " + words[i + 1]["text"] if w["text"] == "Figure" and i + 1 < len(words) else "")
            m = re.match(r"Figure ?S2-(\d+):", txt)
            if m and int(m.group(1)) in FIGS:
                caps.append((int(m.group(1)), w["top"]))
        prev = 0.0
        for num, top in sorted(caps, key=lambda c: c[1]):
            reg = [w for w in words if prev < w["top"] < top]
            fx = [w for w in reg if w["text"] in ("100", "1k")]
            if len(fx) < 2:
                prev = top
                continue
            x100 = next((w["x0"] + w["x1"]) / 2 for w in fx if w["text"] == "100")
            x1k = next((w["x0"] + w["x1"]) / 2 for w in fx if w["text"] == "1k")
            ylab = [w for w in reg if re.fullmatch(r"-?\d+", w["text"]) and w["x1"] < x100 - 5]
            yv = np.array([float(w["text"]) for w in ylab])
            yp = np.array([(w["top"] + w["bottom"]) / 2 for w in ylab])
            b, a = np.polyfit(yp, yv, 1)
            xaxis_y = max(w["top"] for w in fx)
            curves = {}
            for c in pg.curves:
                if c["linewidth"] < 0.5 or not (prev < c["top"] and c["bottom"] < xaxis_y):
                    continue
                nm = name_of(c.get("stroking_color"))
                if nm is None:
                    continue
                curves.setdefault(nm, []).extend((100 * 10 ** ((x - x100) / (x1k - x100)), a + b * y) for x, y in c["pts"])
            scene, cfg, ls, mp = FIGS[num]
            for nm, pts in curves.items():
                pts = np.array(sorted(pts))
                for fc in THIRD:
                    lo, hi = fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6)
                    if lo < pts[0, 0] or hi > pts[-1, 0]:
                        continue
                    g = np.geomspace(lo, hi * 0.999, 40)
                    v = np.interp(np.log(g), np.log(pts[:, 0]), pts[:, 1])
                    rows.append([num, scene, cfg, ls, mp, nm, fc, round(10 * np.log10(np.mean(10 ** (v / 10))), 2)])
            print(f"S2-{num}: {scene} {cfg} {ls}-{mp}: curves {sorted(curves)}")
            prev = top
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["figure", "scene", "config", "source", "receiver", "curve", "f_hz", "level_db"])
        w.writerows(rows)
    print(len(rows), "levels ->", out)


if __name__ == "__main__":
    main()
