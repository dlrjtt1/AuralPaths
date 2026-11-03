"""
Stimulus builder for the listening tests (both stages of the study).

    python make_stimuli.py stimuli_config.json

Input: a folder of path-separated BRIRs named {seat}_{path}.wav (2-channel, time zero = emission,
no headphone EQ). The folder may come from AuralPaths (out/brir/) or from KU100 measurements; the
procedure below is the same for both, so the two stages differ only in where the BRIRs came from.

Per seat and condition (ITDG x level ratio):
  path A signal  = (sum of path_A_inputs) * BRIR_A
  path B signal  = (sum of path_B_inputs) * (BRIR_B_L + BRIR_B_R)
  ITDG           set at the reference seat from the BRIR onsets: d = ITDG - (t_B - t_A),
                 t = first sample within onset_threshold_db of the BRIR peak (earlier ear); t_B is the
                 earlier of B_L and B_R. d >= 0 delays path B; d < 0 is not realisable in a hall and is
                 implemented by delaying path A (flagged). Delays are whole samples.
  level ratio    set at the reference seat: RMS over the whole stimulus of the ear signals, path B
                 (B_L + B_R) over path A, energy averaged over both ears (proposal section 3.1).
                 The same delays and gain are used at every seat; the resulting effective ITDG
                 (via B_L and B_R) and level ratio are measured and written per stimulus.
  path A level   fixed for all conditions: one global scale factor for the whole set (headroom).
  headphone EQ   optional, applied to the final mix only (levels are defined at the ears, before EQ).

Output (output_dir): one wav per stimulus, stimuli.csv (conditions and measured values), manifest.json.
"""
import csv
import datetime
import hashlib
import json
import os
import sys

import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve

import brir_proto as bp

HERE = os.path.dirname(os.path.abspath(__file__))


def sha256(path):
    """SHA-256 of a file; for .wav files of the audio samples only (float32), because libsndfile writes a
    time stamp into the PEAK chunk of float WAV files, so identical audio would get different file hashes."""
    if path.lower().endswith(".wav"):
        import soundfile as _sf
        x, f = _sf.read(path, dtype="float32", always_2d=True)
        return hashlib.sha256(np.ascontiguousarray(x).tobytes() + str(f).encode()).hexdigest()
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_wav(path, fs=None, channels=None):
    x, f = sf.read(path, dtype="float64", always_2d=True)
    if fs is not None and f != fs:
        sys.exit(f"{path}: sample rate {f} Hz, expected {fs} Hz. Resample the file first.")
    if channels is not None and x.shape[1] != channels:
        sys.exit(f"{path}: {x.shape[1]} channels, expected {channels}.")
    return x.T, f


def onset(x, fs, thr_db):
    """Onset of a 2-channel BRIR: first sample within thr_db of the peak, earlier ear (seconds)."""
    a = np.max(np.abs(x), axis=0)
    return int(np.argmax(a >= a.max() * 10 ** (thr_db / 20))) / fs


def energy(x):
    """Energy averaged over the ears (mean of the per-channel sums of squares)."""
    return float(np.mean(np.sum(x ** 2, axis=1)))


def shifted(x, n, length):
    out = np.zeros((x.shape[0], length))
    m = max(0, min(x.shape[1], length - n))
    out[:, n:n + m] = x[:, :m]
    return out


def main(cfg_path):
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    root = os.path.dirname(os.path.abspath(cfg_path))
    P = lambda p: p if os.path.isabs(p) else os.path.normpath(os.path.join(root, p))
    seats, ref = cfg["seats"], cfg["reference_seat"]
    if ref not in seats:
        sys.exit("reference_seat must be one of seats.")
    paths = cfg.get("paths", {"A": "S_amp", "B_L": "B_L", "B_R": "B_R"})
    thr = cfg.get("onset_threshold_db", -20.0)
    out = P(cfg["output_dir"])
    os.makedirs(out, exist_ok=True)

    # BRIRs
    brir_dir, fs = P(cfg["brir_dir"]), None
    H = {}
    for s in seats:
        for k, name in paths.items():
            p = os.path.join(brir_dir, f"{s}_{name}.wav")
            if not os.path.exists(p):
                sys.exit(f"missing BRIR {p}")
            H[(s, k)], fs = read_wav(p, fs, 2)
    # dry signals (mono; a stereo file is summed to mono)
    dry = {}
    for k, p in cfg["dry"].items():
        x, _ = read_wav(P(p), fs)
        dry[k] = x.mean(axis=0)
    n_dry = max(len(v) for v in dry.values())
    mix_in = lambda keys: sum(np.pad(dry[k], (0, n_dry - len(dry[k]))) for k in keys)
    xA, xB = mix_in(cfg["path_A_inputs"]), mix_in(cfg["path_B_inputs"])

    # onsets and the delays set at the reference seat
    t = {(s, k): onset(H[(s, k)], fs, thr) for s in seats for k in paths}
    tA_ref, tB_ref = t[(ref, "A")], min(t[(ref, "B_L")], t[(ref, "B_R")])
    itdgs, lrs = cfg["itdg_ms"], cfg["level_ratio_db"]
    delays = {}
    for it in itdgs:
        d = it / 1000 - (tB_ref - tA_ref)
        nB, nA = (int(round(d * fs)), 0) if d >= 0 else (0, int(round(-d * fs)))
        delays[it] = (nA, nB, d >= 0)
    n_max = max(max(a, b) for a, b, _ in delays.values())
    length = n_dry + int(round(cfg.get("tail_s", 1.5) * fs)) + n_max
    fade = np.ones(length)
    nf = int(round(cfg.get("fade_ms", 50) / 1000 * fs))
    if nf:
        fade[-nf:] = np.cos(np.linspace(0, np.pi / 2, nf)) ** 2

    # path signals per seat (convolution once per seat)
    def conv(x, h):
        y = np.stack([fftconvolve(x, ch) for ch in h])
        return y[:, :length] if y.shape[1] >= length else np.pad(y, ((0, 0), (0, length - y.shape[1])))
    SA = {s: conv(xA, H[(s, "A")]) for s in seats}
    SB = {s: conv(xB, H[(s, "B_L")] + H[(s, "B_R")]) for s in seats}

    hp = cfg.get("headphone_filter")
    hpcf = bp.load_hpcf(P(hp), fs) if hp else None
    eq = (lambda y: np.stack([fftconvolve(ch, hpcf[0])[: ch.size] for ch in y])) if hpcf else (lambda y: y)

    # pass 1: build every stimulus (float32), measure, find the global peak
    items = []
    for s in seats:
        for it in itdgs:
            nA, nB, ok = delays[it]
            a = shifted(SA[s], nA, length) * fade
            b0 = shifted(SB[s], nB, length) * fade
            for lr in lrs:
                a_ref = shifted(SA[ref], nA, length) * fade
                b_ref = shifted(SB[ref], nB, length) * fade
                g = np.sqrt(10 ** (lr / 10) * energy(a_ref) / energy(b_ref))
                b = g * b0
                mix = a + b
                tA = t[(s, "A")] + nA / fs
                bl, br = (t[(s, "B_L")] + nB / fs - tA) * 1000, (t[(s, "B_R")] + nB / fs - tA) * 1000
                items.append({"seat": s, "itdg_nominal_ms": it, "level_ratio_nominal_db": lr,
                              "delay_A_ms": round(nA / fs * 1000, 3), "delay_B_ms": round(nB / fs * 1000, 3),
                              "gain_B_db": round(20 * np.log10(g), 3), "realizable_in_hall": ok,
                              "itdg_eff_BL_ms": round(bl, 3), "itdg_eff_BR_ms": round(br, 3),
                              "itdg_eff_ms": round(min(bl, br), 3), "pa_first": bool(min(bl, br) < 0),
                              "level_ratio_eff_db": round(10 * np.log10(energy(b) / energy(a)), 3),
                              "_y": eq(mix).astype(np.float32)})
        if cfg.get("reference_stimulus", True):     # path A alone: timbre anchor, not a test condition
            a = SA[s] * fade
            items.append({"seat": s, "itdg_nominal_ms": "", "level_ratio_nominal_db": "", "delay_A_ms": 0.0,
                          "delay_B_ms": "", "gain_B_db": "", "realizable_in_hall": "", "itdg_eff_BL_ms": "",
                          "itdg_eff_BR_ms": "", "itdg_eff_ms": "", "pa_first": "", "level_ratio_eff_db": "",
                          "reference": True, "_y": eq(a).astype(np.float32)})
    peak = max(float(np.max(np.abs(i["_y"]))) for i in items)
    scale = 10 ** (cfg.get("headroom_dbfs", -1.0) / 20) / peak

    # pass 2: write
    subtype = cfg.get("subtype", "FLOAT")
    rows = []
    for i in items:
        y = i.pop("_y") * scale
        if i.get("reference"):
            name = f"{i['seat']}_ref_pathA.wav"
        else:
            lr = i["level_ratio_nominal_db"]
            name = f"{i['seat']}_itdg{i['itdg_nominal_ms']:g}_lr{'+' if lr > 0 else '-' if lr < 0 else ''}{abs(lr):g}.wav"
        p = os.path.join(out, name)
        sf.write(p, y.T, fs, subtype=subtype)
        rms = np.sqrt(np.mean(y.astype(np.float64) ** 2))
        rows.append({"file": name, "type": "reference" if i.pop("reference", False) else "condition", **i,
                     "rms_dbfs": round(20 * np.log10(rms + 1e-30), 2),
                     "peak_dbfs": round(20 * np.log10(np.max(np.abs(y)) + 1e-30), 2), "sha256": sha256(p)})
    with open(os.path.join(out, "stimuli.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    bm = cfg.get("brir_manifest")
    man = {
        "kind": "AuralPaths stimulus set",
        "created": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "config": cfg, "config_sha256": sha256(cfg_path),
        "code_sha256": {f: sha256(os.path.join(HERE, f)) for f in ("make_stimuli.py", "brir_proto.py")},
        "fs": fs, "length_samples": length,
        "brir_files_sha256": {f"{s}_{n}.wav": sha256(os.path.join(brir_dir, f"{s}_{n}.wav")) for s in seats for n in paths.values()},
        "brir_manifest": json.load(open(P(bm), encoding="utf-8")) if bm and os.path.exists(P(bm)) else None,
        "dry_sha256": {k: sha256(P(p)) for k, p in cfg["dry"].items()},
        "headphone_filter": {"file": hp, "sha256": sha256(P(hp)), "name": hpcf[1]} if hpcf else None,
        "onsets_s": {f"{s}_{k}": round(v, 6) for (s, k), v in t.items()},
        "reference_onsets_s": {"A": tA_ref, "B": tB_ref},
        "global_scale_db": round(20 * np.log10(scale), 3),
        "definitions": {
            "itdg": "set at the reference seat from BRIR onsets (first sample within onset_threshold_db of the peak, earlier ear); whole-sample delays",
            "level_ratio": "path B (B_L + B_R) over path A, RMS over the whole stimulus of the ear signals, energy averaged over both ears, set at the reference seat before headphone EQ",
            "path_A_level": "fixed for every condition (one global scale factor)",
        },
    }
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False, indent=1)
    nc = sum(r["type"] == "condition" for r in rows)
    print(f"{nc} condition stimuli + {len(rows) - nc} references -> {out} (global scale {man['global_scale_db']:+.2f} dB)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
