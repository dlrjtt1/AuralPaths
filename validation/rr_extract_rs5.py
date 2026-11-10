"""
Read the curves of the round-robin figures S2-28 - S2-30 (Brinkmann et al. 2019, https://doi.org/10.1121/1.5096178,
SuppPub2, scene 5 spectra: "Simulation I", "Simulation II", measurement) from the vector graphics of the PDF and
reduce them to 1/3-octave levels, so that AuralPaths can be compared with the two round-robin simulators that
handled diffraction, on the same pairs and the same measured curve.

    python validation/rr_extract_rs5.py <supppub2.pdf> <out.csv>

Axis calibration from the tick labels (100 / 200 Hz, -20 / -60 dB). Curves: red dotted = Simulation I, dark red
dashed = Simulation II, black = measurement (each figure normalised by the rms of the windowed IR, so only the
spectral shape is comparable).
"""
import csv
import sys

import numpy as np
import pdfplumber

PAIRS = [("LS1", "MP1"), ("LS2", "MP3"), ("LS4", "MP1")]
THIRD = [100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500]


def main():
    pdf, out = sys.argv[1], sys.argv[2]
    pg = pdfplumber.open(pdf).pages[17]
    words = pg.extract_words()
    lab = lambda t: sorted([w for w in words if w["text"] == t], key=lambda w: w["top"])  # noqa: E731
    rows = []
    for fi, (ls, mp) in enumerate(PAIRS):
        w100, w200, wm20, wm60 = lab("100")[fi], lab("200")[fi], lab("-20")[fi], lab("-60")[fi]
        x100, x200 = (w100["x0"] + w100["x1"]) / 2, (w200["x0"] + w200["x1"]) / 2
        y20, y60 = (wm20["top"] + wm20["bottom"]) / 2, (wm60["top"] + wm60["bottom"]) / 2
        top, bot = y20 - 30, y60 + 30
        fx = lambda x: 100 * 2 ** ((x - x100) / (x200 - x100))          # noqa: E731
        fy = lambda y: -20 - 40 * (y - y20) / (y60 - y20)                # noqa: E731
        curves = {"sim_I": [], "sim_II": [], "measured": []}
        for c in pg.curves:
            if not (top <= c["top"] and c["bottom"] <= bot):
                continue
            col = c.get("stroking_color")
            key = "measured" if not isinstance(col, (tuple, list)) else ("sim_I" if col[0] > 0.8 else "sim_II")
            curves[key] += [(fx(x), fy(y)) for x, y in c["pts"]]
        for key, pts in curves.items():
            pts = np.array(sorted(pts))
            for fc in THIRD:
                b = (pts[:, 0] >= fc * 2 ** (-1 / 6)) & (pts[:, 0] < fc * 2 ** (1 / 6))
                if b.sum() == 0:
                    continue
                # interpolate on a log grid inside the band, then energy average
                g = np.geomspace(fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6) * 0.999, 40)
                v = np.interp(np.log(g), np.log(pts[:, 0]), pts[:, 1])
                rows.append([ls, mp, key, fc, round(10 * np.log10(np.mean(10 ** (v / 10))), 2)])
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source", "receiver", "curve", "f_hz", "level_db"])
        w.writerows(rows)
    print(len(rows), "levels ->", out)


if __name__ == "__main__":
    main()
