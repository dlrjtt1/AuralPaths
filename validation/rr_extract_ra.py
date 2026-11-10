"""
Read the room acoustical parameters of the round-robin simulators for the three complex rooms from figure S3-1 of
SuppPub3 (Brinkmann et al. 2019, https://doi.org/10.1121/1.5096178): T20, EDT, C80 and D50 in the octave bands
125 Hz - 4 kHz, averaged over the 10 source-receiver pairs, for the measurement and the programs A - F.

    python validation/rr_extract_ra.py <supppub3.pdf> <out.csv>

The figure is vector graphics: per panel the grey JND band around the measured values (its mid line = the measured
value), the markers of the programs (A blue +, B green *, C yellow diamond, D cyan triangle, E purple star, F red
square, MATLAB markers), and the tick labels of the y axis (linear fit). Panels: left column T20 then C80, right column
EDT then D50, each for the small, medium and large room (scenes 9, 10, 11 = BRAS CR2, CR3, CR4).
"""
import csv
import re
import sys

import numpy as np
import pdfplumber

BANDS = [125, 250, 500, 1000, 2000, 4000]
ROOMS = ["CR2", "CR3", "CR4"]
COL = {(0.0, 0.4471, 0.7412): "A", (0.2667, 0.6745, 0.1882): "B", (0.9294, 0.6941, 0.1255): "C",
       (0.0, 0.7843, 0.7843): "D", (0.4941, 0.1843, 0.5569): "E", (0.7843, 0.1725, 0.0392): "F"}


def prog(col):
    if not isinstance(col, (tuple, list)) or len(col) != 3:
        return None
    for k, v in COL.items():
        if max(abs(a - b) for a, b in zip(k, col)) < 0.01:
            return v
    return None


def main():
    pdf, out = sys.argv[1], sys.argv[2]
    pg = pdfplumber.open(pdf).pages[1]
    axes = [r for r in pg.rects if r.get("fill") and str(r.get("non_stroking_color")) == "1.0"
            and 80 < r["height"] < 100 and 140 < r["width"] < 170]
    axes.sort(key=lambda r: (round(r["x0"] / 100), r["top"]))
    names = [("T20", r) for r in ROOMS] + [("C80", r) for r in ROOMS] + [("EDT", r) for r in ROOMS] + \
            [("D50", r) for r in ROOMS]
    left = sorted([a for a in axes if a["x0"] < 300], key=lambda r: r["top"])
    right = sorted([a for a in axes if a["x0"] >= 300], key=lambda r: r["top"])
    panels = list(zip(names[:6], left)) + list(zip(names[6:], right))
    polys = [c for c in pg.curves if str(c.get("non_stroking_color")) == "0.8" and c.get("fill")]
    words = [w for w in pg.extract_words() if re.fullmatch(r"-?\d+", w["text"])]
    # marker centres
    marks = []
    for ln in pg.lines:
        p = prog(ln.get("stroking_color"))
        if p in ("A", "B") and abs(ln["x1"] - ln["x0"]) < 0.05 and 3 < ln["bottom"] - ln["top"] < 6:
            marks.append((p, ln["x0"], (ln["top"] + ln["bottom"]) / 2))
    for c in pg.curves:
        p = prog(c.get("stroking_color"))
        if p in ("C", "D", "E") and (c["x1"] - c["x0"]) < 8:
            marks.append((p, (c["x0"] + c["x1"]) / 2, (c["top"] + c["bottom"]) / 2))
    for r in pg.rects:
        if prog(r.get("stroking_color")) == "F" and r["width"] < 6:
            marks.append(("F", (r["x0"] + r["x1"]) / 2, (r["top"] + r["bottom"]) / 2))
    rows = []
    for (par, room), ax in panels:
        # tick labels left of the panel, rebuilt from characters (the rotated axis title overlaps some labels and
        # splits them into words); a label centred on the panel's bottom edge belongs to the panel below
        ch = [c for c in pg.chars if ax["x0"] - 12 < c["x1"] < ax["x0"] - 0.5 and c["text"] in "-0123456789"
              and ax["top"] - 1 < (c["top"] + c["bottom"]) / 2 < ax["bottom"] - 3 and c.get("upright", True)]
        lab = []
        for top in sorted(set(round(c["top"], 1) for c in ch)):
            row = sorted([c for c in ch if abs(c["top"] - top) < 0.3], key=lambda c: c["x0"])
            grp = [row[-1]]
            for c in reversed(row[:-1]):          # contiguous run ending next to the axis
                if grp[0]["x0"] - c["x1"] < 0.8:
                    grp.insert(0, c)
                else:
                    break
            if grp[-1]["x1"] > ax["x0"] - 4:
                lab.append({"text": "".join(c["text"] for c in grp), "top": grp[0]["top"], "bottom": grp[0]["bottom"]})
        ys = np.array([(w["top"] + w["bottom"]) / 2 for w in lab])
        vs = np.array([float(w["text"]) for w in lab])
        k, b = np.polyfit(ys, vs, 1)
        res = np.abs(k * ys + b - vs).max()
        poly = [c for c in polys if ax["x0"] <= c["x0"] + 1 and c["x1"] <= ax["x1"] + 1 and ax["top"] <= c["top"] + 1
                and c["bottom"] <= ax["bottom"] + 1]
        if len(poly) != 1 or res > 1e-6 * max(1, abs(vs).max()) + 0.05:
            raise SystemExit(f"{par} {room}: {len(poly)} JND bands, tick fit residual {res:.3f}")
        pts = poly[0]["pts"]
        bx = sorted(set(round(p[0], 1) for p in pts))
        for bi, x in enumerate(bx):
            yy = [p[1] for p in pts if abs(p[0] - x) < 0.2]
            rows.append([room, par, BANDS[bi], "measured", round(k * (min(yy) + max(yy)) / 2 + b, 4)])
        legend = [r for r in pg.rects if r.get("fill") and str(r.get("non_stroking_color")) == "1.0"
                  and r["height"] < 20 and r["x0"] < ax["x1"] and r["x1"] > ax["x0"]
                  and r["top"] < ax["bottom"] and r["bottom"] > ax["top"]]       # legend boxes over the panel
        for p, x, y in marks:
            if ax["x0"] < x < ax["x1"] and ax["top"] < y < ax["bottom"] and \
                    not any(r["x0"] <= x <= r["x1"] and r["top"] <= y <= r["bottom"] for r in legend):
                bi = int(np.argmin([abs(x - q) for q in bx]))
                if abs(x - bx[bi]) < 9:                    # markers are offset sideways per program
                    rows.append([room, par, BANDS[bi], p, round(k * y + b, 4)])
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["room", "parameter", "f_hz", "curve", "value"])
        w.writerows(rows)
    from collections import Counter
    print(Counter((r[0], r[1], r[3]) for r in rows if r[3] != "measured").most_common(3), len(rows), "->", out)


if __name__ == "__main__":
    main()
