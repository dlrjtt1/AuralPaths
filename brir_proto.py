"""
경로 분리 BRIR 합성 최소 프로토타입 (직육면체 근사)

구성
  - 음향 전파: pyroomacoustics(허상법, ISM)를 수정 없이 라이브러리로 사용
  - 초기부(직접음 ~ early_window): 허상 음원마다 도래 방향의 HRIR(SOFA)을 적용해 바이노럴 합성
  - 후기부: 고차 ISM 무지향 RIR의 옥타브 대역 에너지 포락선으로 귀별 독립 잡음을 성형
            (좌우 독립 잡음이므로 후기부 양이 상관은 실제보다 낮다 -> IACC_L은 산출하지 않음)
  - 조건: 중앙 수음점 기준 명목 ITDG / 레벨비 -> 경로 B(B_L+B_R)에 지연·게인 부여
  - 지표: 무지향 RIR에서 C80, D50, Ts, EDT, T30 / 바이노럴 BRIR에서 IACC_E3
진폭 규약은 pyroomacoustics와 같다(감쇠 / 거리).
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass

import csv
import numpy as np
import pyroomacoustics as pra
from scipy import signal

AMP = "S_amp"      # 확성 음원: 직접음 경로 A + PA(B_L·B_R)로 송출
UNAMP = "S_unamp"  # 비확성 음원: 직접음만
# late-noise bank: up to the 16 kHz octave (the top band is a high-pass from its lower edge). Until 2026-11 the bank
# stopped at 8 kHz, so everything above 5.7 kHz decayed with the 8 kHz histogram (too bright a late tail at 16 kHz).
OCT_CENTERS = np.array([125, 250, 500, 1000, 2000, 4000, 8000, 16000], dtype=float)


# ---------------------------------------------------------------- 설정·실내
def load_config(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def has_geometry(cfg):
    return bool(cfg.get("geometry"))


def is_mesh(cfg):
    """3D OBJ hall (geometry.build_mesh) rather than a drawn 2.5D hall."""
    return has_geometry(cfg) and "mesh" in cfg["geometry"]


def stage_y(cfg):
    return cfg["room"]["dims_m"][1] - cfg["room"].get("stage_depth_m", 0.0)


# pyroomacoustics ray tracing: energy_thres ends a ray once its energy falls below energy_thres x its start energy,
# but the same number is also an ABSOLUTE floor for every scattered ("diffuse rain") contribution to a receiver
# (libroom_src/room.cpp, scat_ray: scat_trans.maxCoeff() > energy_thres), and a ray starts with 2 / n_rays. With 1e-9
# the rain was dropped from about 0.5 s on (earlier with more rays), so T30 came out short and fell with the ray count
# (tiled 12 x 9 x 7 m box, alpha 0.2, s 1: 1.11 / 1.04 / 0.99 s at 2000 / 20 000 / 100 000 rays; 1e-15: 1.12 s;
# validation/check_box_lambert.js). 1e-20 keeps the rain to well below -100 dB; rays then run to time_thres.
RT_ENERGY_THRES = 1e-20

_GEOM_CACHE = {}


def _geom(cfg):
    """Built hall surfaces (cached: a mesh hall is voxelised once per configuration)."""
    import geometry
    seed = next(iter(cfg["sources"][s]["pos"] for s in source_names(cfg)))
    key = json.dumps([cfg["geometry"], stage_y(cfg), seed], sort_keys=True, default=str)
    if key not in _GEOM_CACHE:
        _GEOM_CACHE[key] = geometry.build(cfg["geometry"], stage_y(cfg), seed=seed)
    return _GEOM_CACHE[key]


def make_room(cfg, max_order, rand_ism=False, ray_tracing=False):
    """ShoeBox for the default model; a polyhedral pyroomacoustics Room when config has "geometry"."""
    r = cfg["room"]
    if has_geometry(cfg):
        import geometry
        probe = pra.ShoeBox([1, 1, 1], fs=cfg["fs"])
        cen = probe.octave_bands.centers
        walls = geometry.pra_walls(_geom(cfg), cfg["geometry"]["materials"], len(cen), cen)
        room = pra.Room(walls, fs=cfg["fs"], max_order=max_order, air_absorption=r["air_absorption"], ray_tracing=ray_tracing)
        if is_mesh(cfg):
            # pyroomacoustics' inside test casts one ray and counts wall crossings, which fails on meshes with
            # overlapping solids (seat blocks) or tiny gaps; use the voxel room of geometry.build_mesh instead
            G = _geom(cfg)
            room.is_inside = lambda p, include_borders=True: geometry.inside(G, p)
    else:
        ab = r["absorption_octave"]
        mat = pra.Material({"coeffs": ab["values"], "center_freqs": ab["_bands_hz"]}, r["scattering"])
        room = pra.ShoeBox(r["dims_m"], fs=cfg["fs"], materials=mat, max_order=max_order,
                           air_absorption=r["air_absorption"], use_rand_ism=rand_ism, ray_tracing=ray_tracing)
    room.set_sound_speed(cfg["c"])
    _fix_air_above_table(room)
    return room


def _iso9613_db_per_m(f, temp_c=20.0, rh=40.0, pa_kpa=101.325):
    """Pure-tone air absorption (dB/m), ISO 9613-1:1993 eqs. (1) - (5)."""
    pr, T0, T01, T = 101.325, 293.15, 273.16, temp_c + 273.15
    h = rh * pr * 10 ** (-6.8346 * (T01 / T) ** 1.261 + 4.6151) / pa_kpa
    fro = pa_kpa / pr * (24 + 4.04e4 * h * (0.02 + h) / (0.391 + h))
    frn = pa_kpa / pr * (T / T0) ** -0.5 * (9 + 280 * h * np.exp(-4.17 * ((T / T0) ** (-1 / 3) - 1)))
    f = np.asarray(f, float)
    return 8.686 * f ** 2 * (1.84e-11 * (pr / pa_kpa) * (T / T0) ** 0.5 + (T / T0) ** -2.5 * (
        0.01275 * np.exp(-2239.1 / T) / (fro + f ** 2 / fro) + 0.1068 * np.exp(-3352.0 / T) / (frn + f ** 2 / frn)))


def _fix_air_above_table(room):
    """pyroomacoustics' air-absorption table (20 C, 30 - 50 % RH; Vorlaender 2008) ends at the 8 kHz octave; its value
    for the 16 kHz octave band is an extrapolation (0.035 /m), less than half of what ISO 9613-1 gives there, which
    left the simulated late tail far too bright at 16 kHz (BRAS CR3 / CR4: +10 ... +23 dB re measured). Bands above
    the table are set to the table's 8 kHz value times the ISO 9613-1 frequency trend (20 C, 40 % RH):
    m(f) = m(8 kHz) * a_ISO(f) / a_ISO(8 kHz); 16 kHz -> about 0.066 /m. An engineering bridge, not a measurement."""
    ab = getattr(room, "air_absorption", None)
    if ab is None or not len(ab):
        return
    cen = np.asarray(room.octave_bands.centers, float)
    tab = pra.parameters.air_absorption_table["center_freqs"]
    top = max(tab)
    i8 = int(np.argmin(np.abs(cen - top)))
    hi = cen > top * 1.01
    if not hi.any():
        return
    ab = np.asarray(ab, float).copy()
    ab[hi] = ab[i8] * _iso9613_db_per_m(cen[hi]) / _iso9613_db_per_m(top)
    room.air_absorption = ab.tolist()


def early_order(cfg):
    if not has_geometry(cfg):
        return cfg["binaural"]["ism_order_early"]
    # mesh halls: pyroomacoustics enumerates images over all wall sequences (N^order), so order 1 by default
    return cfg["geometry"].get("ism_order", 1 if is_mesh(cfg) else 4)


def receiver_names(cfg):
    return [k for k in cfg["receivers"] if not k.startswith("_")]


def source_names(cfg):
    return [k for k in cfg["sources"] if not k.startswith("_")]


def direct_time(cfg, src, rec):
    s = np.array(cfg["sources"][src]["pos"])
    m = np.array(cfg["receivers"][rec])
    return np.linalg.norm(s - m) / cfg["c"]


# ---------------------------------------------------------------- HRIR
@dataclass
class HRIRSet:
    ir: np.ndarray        # (M, 2, N)
    dirs: np.ndarray      # (M, 3) 단위벡터, 머리 좌표(x=정면, y=왼쪽, z=위)
    fs: int
    df_band_energy: np.ndarray  # (2, n_bands) 방향 평균 대역 에너지(확산음장 근사)
    bulk_delay_s: float = 0.0   # 정면 HRIR의 첫 도달 시점(데이터셋 고유의 선행 지연)
    coh_f: np.ndarray = None    # frequency grid (Hz) of the diffuse-field interaural coherence
    coh: np.ndarray = None      # diffuse-field interaural coherence on coh_f (real part, -1..1)


def load_hrir(path, fs_target):
    import sofar
    sofa = sofar.read_sofa(path, verify=False, verbose=False)
    ir = np.asarray(sofa.Data_IR, dtype=float)
    fs = int(np.atleast_1d(sofa.Data_SamplingRate)[0])
    pos = np.asarray(sofa.SourcePosition, dtype=float)
    ptype = str(getattr(sofa, "SourcePosition_Type", "spherical")).lower()
    if "cart" in ptype:
        d = pos / np.linalg.norm(pos, axis=1, keepdims=True)
    else:  # SOFA spherical: 방위각(정면 0, 왼쪽 +), 고도각, 거리
        az, el = np.deg2rad(pos[:, 0]), np.deg2rad(pos[:, 1])
        d = np.c_[np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)]
    if fs != fs_target:
        g = np.gcd(fs, fs_target)
        ir = signal.resample_poly(ir, fs_target // g, fs // g, axis=-1)
        fs = fs_target
    bands = octave_filterbank(fs)
    nfft = 4096
    H = np.abs(np.fft.rfft(ir, nfft, axis=-1)) ** 2
    f = np.fft.rfftfreq(nfft, 1 / fs)
    # 확산음장 평균: 등간격 방위·고도 격자는 극 부근이 과밀하므로 cos(고도)로 면적 가중
    wgt = np.sqrt(np.clip(1 - d[:, 2] ** 2, 0, 1)) + 1e-6
    wgt = wgt / wgt.sum()
    df = np.zeros((2, len(bands["edges"])))
    for b, (lo, hi) in enumerate(bands["edges"]):
        sel = (f >= lo) & (f < hi)
        df[:, b] = np.einsum("m,mr->r", wgt, H[:, :, sel].mean(axis=2))
    front = int(np.argmax(d @ np.array([1.0, 0.0, 0.0])))
    bulk = onset_time(ir[front], fs)
    coh_f, coh = diffuse_coherence(ir, fs, wgt)
    return HRIRSet(ir, d, fs, df, bulk, coh_f, coh)


COH_NFFT = 512


def diffuse_coherence(ir, fs, wgt, nfft=COH_NFFT):
    """Interaural coherence of an ideal diffuse field for this HRIR set: area-weighted average of the
    interaural cross-spectrum over all directions, normalised by the averaged auto-spectra,
    Gamma(f) = Re sum_m w_m H_L H_R* / sqrt(sum_m w_m |H_L|^2 * sum_m w_m |H_R|^2).
    Used as the target coherence of the late noise (see late_binaural)."""
    H = np.fft.rfft(ir, nfft, axis=-1)
    cross = np.einsum("m,mk->k", wgt, H[:, 0] * np.conj(H[:, 1]))
    pl = np.einsum("m,mk->k", wgt, np.abs(H[:, 0]) ** 2)
    pr = np.einsum("m,mk->k", wgt, np.abs(H[:, 1]) ** 2)
    g = np.clip(np.real(cross) / np.sqrt(pl * pr + 1e-30), -1.0, 1.0)
    g[0] = 1.0
    return np.fft.rfftfreq(nfft, 1 / fs), g


def coherent_pair(rng, n_len, fs, coh_f, coh):
    """Two unit-power white noises whose interaural coherence follows coh(f): independent n1, n2 are mixed
    per frequency as L = cos(a) n1 + sin(a) n2, R = cos(a) n1 - sin(a) n2 with a = arccos(Gamma) / 2,
    so that coherence = cos(2a) = Gamma and both channels keep unit power (two-channel case of the
    coherence-constrained mixing in Habets, Cohen & Gannot 2008, JASA 124(5))."""
    N1, N2 = np.fft.rfft(rng.standard_normal(n_len)), np.fft.rfft(rng.standard_normal(n_len))
    a = np.arccos(np.interp(np.fft.rfftfreq(n_len, 1 / fs), coh_f, coh)) / 2
    c, s = np.cos(a), np.sin(a)
    return np.fft.irfft(c * N1 + s * N2, n_len), np.fft.irfft(c * N1 - s * N2, n_len)


# ---------------------------------------------------------------- 대역 필터
def octave_filterbank(fs):
    cen = [fc for fc in OCT_CENTERS if fc / np.sqrt(2) < 0.45 * fs]      # bands whose lower edge is below Nyquist
    edges = []
    for i, fc in enumerate(cen):
        lo = fc / np.sqrt(2) if i > 0 else 0.0
        hi = fc * np.sqrt(2) if i < len(cen) - 1 and fc * np.sqrt(2) < fs / 2 else fs / 2
        edges.append((lo, hi))
    sos = []
    for lo, hi in edges:
        if lo == 0:
            sos.append(signal.butter(4, hi, "lowpass", fs=fs, output="sos"))
        elif hi >= fs / 2:
            sos.append(signal.butter(4, lo, "highpass", fs=fs, output="sos"))
        else:
            sos.append(signal.butter(4, [lo, hi], "bandpass", fs=fs, output="sos"))
    return {"edges": edges, "sos": sos}


def band_filter(x, fs, fc, zero_phase=True):
    """ISO 3382 지표용 단일 옥타브 대역 필터(중심 fc)."""
    sos = signal.butter(4, [fc / np.sqrt(2), fc * np.sqrt(2)], "bandpass", fs=fs, output="sos")
    return signal.sosfiltfilt(sos, x, axis=-1) if zero_phase else signal.sosfilt(sos, x, axis=-1)


# ---------------------------------------------------------------- 무지향 RIR
def omni_rirs(cfg):
    """고차 ISM 무지향 RIR. 반환: {(src, rec): rir}, 시간 0 = 음원 방사 시점."""
    fdl2 = pra.constants.get("frac_delay_length") // 2
    out = {}
    recs = receiver_names(cfg)
    for s in source_names(cfg):
        room = make_room(cfg, cfg["binaural"]["ism_order_omni"], rand_ism=False)
        room.add_source(cfg["sources"][s]["pos"])
        room.add_microphone_array(np.array([cfg["receivers"][r] for r in recs]).T)
        room.compute_rir()
        for i, r in enumerate(recs):
            out[(s, r)] = np.asarray(room.rir[i][0][fdl2:], dtype=float)
    return out


# ---------------------------------------------------------------- headphone compensation
def load_hpcf(path, fs):
    """Headphone compensation filter from the KU100 compilation (HPCF.zip, Bernschuetz 2013, CC BY 3.0):
    MATLAB struct hpcf with minPhase / linPhase impulse responses at hpcf.fs. Returns the minimum-phase
    filter, scaled to 0 dB at 1 kHz (only the shape is used; playback level is set separately)."""
    import scipy.io as sio
    h = sio.loadmat(path, squeeze_me=True, struct_as_record=False)["hpcf"]
    ir = np.asarray(h.minPhase, dtype=float)
    if int(h.fs) != fs:
        from scipy.signal import resample_poly
        from math import gcd
        g = gcd(int(fs), int(h.fs))
        ir = resample_poly(ir, fs // g, int(h.fs) // g)
    n = 8192
    H = np.abs(np.fft.rfft(ir, n))
    k = int(round(1000 * n / fs))
    return ir / max(H[k], 1e-9), str(h.hpName)


DIR_FLOOR = 10 ** (-30 / 20)


def dir_model(cfg, src, bands):
    """Generic axisymmetric loudspeaker pattern for sources with "coverage" (an engineering assumption,
    same as engine_geom.js dirModel): nominal -6 dB full angle `coverage` at and above 2 kHz, widening
    below as BW(f) = min(360, coverage * max(1, (2000 / f)^0.7)); amplitude ((1 + cos t) / 2)^n, -6 dB at BW / 2,
    floor -30 dB. "aim": {"az": deg (0 = towards -y, + towards +x), "el": deg (+ up)}.
    Returns None for omnidirectional sources."""
    sp = cfg["sources"][src]
    az, el = np.radians(sp.get("aim", {}).get("az", 0.0)), np.radians(sp.get("aim", {}).get("el", 0.0))
    u = np.array([np.sin(az) * np.cos(el), -np.cos(az) * np.cos(el), np.sin(el)])
    if sp.get("directivity"):                          # measured / published data (see load_directivity, load_balloon)
        dv = sp["directivity"]
        right = np.cross(u, [0.0, 0.0, 1.0])
        right = right / np.linalg.norm(right) if np.linalg.norm(right) > 1e-9 else np.array([1.0, 0.0, 0.0])
        dm = {"kind": "table", "u": u, "right": right, "up": np.cross(right, u)}
        if (isinstance(dv, str) and dv.lower().endswith(".sofa")) or (isinstance(dv, dict) and "balloon" in dv):
            dm["kind"], dm["balloon"] = "balloon", load_balloon(dv, bands)
        else:
            dm["tab"] = load_directivity(dv, bands)
        dm["diffuse"] = 1 / directivity_q(dm)
        return dm
    cov = float(sp.get("coverage", 0) or 0)
    if not 0 < cov < 360:
        return None
    n = []
    for f in bands:
        bw = min(360.0, cov * max(1.0, (2000.0 / f) ** 0.7))   # nominal coverage at and above 2 kHz
        n.append(0.0 if bw >= 359.9 else np.log(0.5) / np.log((1 + np.cos(np.radians(bw / 2))) / 2))
    n = np.array(n)
    return {"u": u, "n": n, "diffuse": 1 / (2 * n + 1)}


DIR_GRID = np.arange(-180, 181, 1.0)    # degrees, both engines resample the polars to this grid


def directivity_rows(spec):
    """Polar data rows [(band_hz, plane, angle_deg, level_db)] from a CSV path or from inline data
    {"name": ..., "data": [[band_hz, "h"|"v", angle_deg, level_db], ...]} (what the viewer's Copy config writes)."""
    if isinstance(spec, dict):
        return [(float(b), str(p).strip().lower()[0], float(a), float(l)) for b, p, a, l in spec["data"]]
    with open(spec, encoding="utf-8") as f:
        lines = [l for l in f if l.strip() and not l.lstrip().startswith("#")]
    return [(float(r["band_hz"]), r["plane"].strip().lower()[0], float(r["angle_deg"]), float(r["level_db"])) for r in csv.DictReader(lines)]


def directivity_normalize(spec):
    """"axis" (default: 0 dB straight ahead) or "mean" (0 dB = power mean over the horizontal polar, for
    nominally omnidirectional sources such as a dodecahedron, where "on axis" has no meaning). Set with a
    comment line "# normalize=mean" in the CSV, or "normalize": "mean" in inline data."""
    if isinstance(spec, dict):
        return spec.get("normalize", "axis")
    with open(spec, encoding="utf-8") as f:
        for l in f:
            l = l.strip().lower().replace(" ", "")
            if l.startswith("#normalize="):
                return l.split("=", 1)[1]
    return "axis"


def load_directivity(path, bands):
    """Loudspeaker polar data (CSV path or inline data, see directivity_rows) with columns band_hz, plane, angle_deg, level_db:
    plane "h" = horizontal polar (angle + towards the loudspeaker's right, seen from behind it),
    plane "v" = vertical polar (angle + up); levels in dB, normalised here to 0 dB on axis per band.
    One-sided data (0..180 only) is mirrored. Bands are interpolated to the model bands on a log
    frequency axis (clamped outside the data range). Returns {"h": [n_bands, 361], "v": [...]} in dB on
    DIR_GRID. Between the two planes the level is blended as cos^2(phi) * Lh + sin^2(phi) * Lv (in dB),
    phi = angle around the axis: an engineering assumption, exact only on the two measured planes."""
    rows = {}
    for b, pl, a, l in directivity_rows(path):
        rows.setdefault(pl, {}).setdefault(b, []).append((a, l))
    if "h" not in rows:
        raise ValueError("directivity data needs at least the horizontal polar (plane h)")
    rows.setdefault("v", rows["h"])                  # no vertical data: rotationally symmetric
    out = {}
    for pl, by_band in rows.items():
        fb = np.array(sorted(by_band))
        grid = []
        for f0 in fb:
            pts = sorted(by_band[f0])
            ang = np.array([a for a, _ in pts]); lev = np.array([l for _, l in pts])
            if ang.min() >= 0:                       # mirror one-sided data
                ang, lev = np.r_[-ang[::-1], ang], np.r_[lev[::-1], lev]
            o = np.argsort(ang); ang, lev = ang[o], lev[o]
            g = np.interp(DIR_GRID, ang, lev, period=360)
            grid.append(g - np.interp(0.0, DIR_GRID, g))
        grid = np.array(grid)
        lf = np.log(fb)
        out[pl] = np.array([[np.interp(np.log(fm), lf, grid[:, i]) for i in range(DIR_GRID.size)] for fm in bands])
    if directivity_normalize(path) == "mean":       # 0 dB = power mean over the horizontal circle, per band
        off = 10 * np.log10(np.mean(10 ** (out["h"][:, :-1] / 10), axis=1, keepdims=True))
        out = {pl: v - off for pl, v in out.items()}
    return out


BAL_STEP = 5.0                                     # degrees: balloon grid, azimuth -180..180, elevation -90..90
BAL_AZ = np.arange(-180, 180 + BAL_STEP / 2, BAL_STEP)
BAL_EL = np.arange(-90, 90 + BAL_STEP / 2, BAL_STEP)


def _sph_to_vec(pos, typ):
    pos = np.atleast_2d(np.asarray(pos, float))
    if "cart" in str(typ).lower():
        return pos / np.linalg.norm(pos, axis=1, keepdims=True)
    az, el = np.radians(pos[:, 0]), np.radians(pos[:, 1])
    return np.c_[np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)]


def balloon_from_points(dirs, power, bands_hz=None):
    """Regular balloon [n_bands, n_el, n_az] in dB re on-axis from band powers at measured directions
    dirs [P, 3] (source frame: x front, y left, z up): inverse-distance weighting of the 4 nearest
    points on the sphere (in power), then normalised to the value straight ahead."""
    from scipy.spatial import cKDTree
    A, E = np.meshgrid(np.radians(BAL_AZ), np.radians(BAL_EL))
    g = np.c_[(np.cos(E) * np.cos(A)).ravel(), (np.cos(E) * np.sin(A)).ravel(), np.sin(E).ravel()]
    d, i = cKDTree(dirs).query(g, k=min(4, len(dirs)))
    d, i = np.atleast_2d(d.T).T if d.ndim == 1 else d, i if i.ndim > 1 else i[:, None]
    w = 1 / np.maximum(d, 1e-6) ** 2
    w /= w.sum(axis=1, keepdims=True)
    out = []
    for b in range(power.shape[0]):
        pg = np.sum(w * power[b][i], axis=1).reshape(E.shape)
        front = pg[BAL_EL.size // 2, BAL_AZ.size // 2]
        out.append(10 * np.log10(np.maximum(pg, 1e-12) / max(front, 1e-30)))
    return np.array(out)


def load_balloon(spec, bands):
    """Full-sphere directivity from a SOFA file (AES69: FreeFieldDirectivityTF with Data.Real / Data.Imag
    and frequencies N, or an impulse-response convention with Data.IR) or from inline data
    {"name", "balloon": {"bands": [...], "db": [band][el][az]}} as written by the viewer.
    SOFA: directions are taken from ReceiverPosition when there are several receivers (microphones
    around the source), otherwise from SourcePosition per measurement; coordinates as stored (x front,
    y left, z up of the source). Power is averaged over the other dimension (e.g. notes) and over
    the octave band around each model band. Returns {"db": [n_bands, n_el, n_az]} on BAL_EL x BAL_AZ."""
    if isinstance(spec, dict):
        b = spec["balloon"]
        src_b, db = np.asarray(b["bands"], float), np.asarray(b["db"], float)
        lf = np.log(src_b)
        return {"db": np.array([db[int(np.argmin(np.abs(lf - np.log(f))))] for f in bands])}
    import sofar
    sf_ = sofar.read_sofa(spec, verify=False, verbose=False)
    if hasattr(sf_, "Data_Real") and np.size(sf_.Data_Real) > 1:
        H = np.asarray(sf_.Data_Real, float) + 1j * np.asarray(getattr(sf_, "Data_Imag", 0.0), float)
        f = np.atleast_1d(np.asarray(sf_.N, float))
    else:
        fs = float(np.atleast_1d(sf_.Data_SamplingRate)[0])
        ir = np.asarray(sf_.Data_IR, float)
        nfft = max(4096, 1 << int(np.ceil(np.log2(ir.shape[-1]))))
        H, f = np.fft.rfft(ir, nfft, axis=-1), np.fft.rfftfreq(nfft, 1 / fs)
    M, R = H.shape[0], H.shape[1]
    P = np.abs(H) ** 2
    if R > 1:
        rp = np.asarray(sf_.ReceiverPosition, float)
        rp = rp[:, :, 0] if rp.ndim == 3 else rp
        dirs, P = _sph_to_vec(rp[:R], getattr(sf_, "ReceiverPosition_Type", "spherical")), P.mean(axis=0)
    else:
        sp_ = np.asarray(sf_.SourcePosition, float)
        dirs, P = _sph_to_vec(sp_[:M], getattr(sf_, "SourcePosition_Type", "spherical")), P[:, 0, :]
    pw = []
    for fc in bands:
        sel = (f >= fc / np.sqrt(2)) & (f < fc * np.sqrt(2))
        if not sel.any():
            sel = np.abs(np.log(np.maximum(f, 1e-9) / fc)) == np.min(np.abs(np.log(np.maximum(f, 1e-9) / fc)))
        pw.append(P[:, sel].mean(axis=1))
    return {"db": balloon_from_points(dirs, np.array(pw))}


def _balloon_amp(dm, e):
    left = -dm["right"]
    x, y, z = dm["u"] @ e, left @ e, dm["up"] @ e
    az = np.degrees(np.arctan2(y, x)); el = np.degrees(np.arcsin(np.clip(z, -1, 1)))
    fa = (az + 180) / BAL_STEP; fe = (el + 90) / BAL_STEP
    ia = np.clip(np.floor(fa).astype(int), 0, BAL_AZ.size - 2); ie = np.clip(np.floor(fe).astype(int), 0, BAL_EL.size - 2)
    ta, te = fa - ia, fe - ie
    out = np.empty((dm["balloon"]["db"].shape[0], e.shape[1]))
    for b, G in enumerate(dm["balloon"]["db"]):
        v = (G[ie, ia] * (1 - ta) * (1 - te) + G[ie, ia + 1] * ta * (1 - te) + G[ie + 1, ia] * (1 - ta) * te + G[ie + 1, ia + 1] * ta * te)
        out[b] = np.maximum(DIR_FLOOR, 10 ** (v / 20))
    return out


def _table_amp(dm, e):
    ct = np.clip(dm["u"] @ e, -1, 1)
    th = np.degrees(np.arccos(ct))
    phi = np.arctan2(dm["up"] @ e, dm["right"] @ e)
    c2 = np.cos(phi) ** 2
    sh, sv = np.where(np.cos(phi) >= 0, 1, -1), np.where(np.sin(phi) >= 0, 1, -1)
    out = np.empty((dm["tab"]["h"].shape[0], e.shape[1]))
    for b in range(out.shape[0]):
        lh = np.interp(sh * th, DIR_GRID, dm["tab"]["h"][b])
        lv = np.interp(sv * th, DIR_GRID, dm["tab"]["v"][b])
        out[b] = np.maximum(DIR_FLOOR, 10 ** ((c2 * lh + (1 - c2) * lv) / 20))
    return out


def directivity_q(dm, n=4000):
    """Directivity factor Q per band (on-axis intensity over the mean over the sphere), Fibonacci sphere."""
    i = np.arange(n) + 0.5
    z = 1 - 2 * i / n; r = np.sqrt(1 - z ** 2); ph = np.pi * (1 + 5 ** 0.5) * i
    e = np.vstack([r * np.cos(ph), r * np.sin(ph), z])
    return 1 / np.mean(dir_amp(dm, e) ** 2, axis=1)


def dir_amp(dm, e):
    """Band amplitude factors [n_bands, N] for unit emission directions e [3, N]."""
    if dm.get("kind") == "table":
        return _table_amp(dm, e)
    if dm.get("kind") == "balloon":
        return _balloon_amp(dm, e)
    x = np.clip((1 + dm["u"] @ e) / 2, 0, 1)
    out = np.ones((dm["n"].size, e.shape[1]))
    for b, v in enumerate(dm["n"]):
        if v > 0:
            out[b] = np.maximum(DIR_FLOOR, x ** v)
    return out


def emission_dirs(cfg, room, src_pos, idx):
    """Unit vectors [3, N] in which the paths of images idx leave the source.
    Shoebox: image coordinate 2kL +/- s per axis; odd parity flips that component.
    Polyhedral room: the wall chain is rebuilt from the generating walls (parent image = reflection of the
    image in its wall) and the path is back-traced from the receiver to the first reflection point."""
    S = room.sources[0]
    m = np.asarray(room.mic_array.R[:, 0], dtype=float)
    s0 = np.asarray(src_pos, dtype=float)
    imgs = S.images[:, idx]
    if not has_geometry(cfg):
        L = np.asarray(cfg["room"]["dims_m"], dtype=float)[:, None]
        k_even = (imgs - s0[:, None]) / (2 * L)
        odd = np.abs(k_even - np.round(k_even)) > 1e-6
        e = (m[:, None] - imgs) * np.where(odd, -1.0, 1.0)
        return e / np.maximum(np.linalg.norm(e, axis=0), 1e-12)
    # polyhedral room: rebuild each image's wall sequence by growing the image tree (same pruning as the
    # browser engine: an image is reflected only in planes it lies in front of), then back-trace the path
    walls = room.walls
    nrm = np.array([np.asarray(w.normal, dtype=float) / np.linalg.norm(w.normal) for w in walls])   # outward
    org = np.array([np.asarray(w.corners, dtype=float)[:, 0] for w in walls])
    sel = np.asarray(idx, dtype=int)
    orders = S.orders[sel]
    omax = int(orders.max()) if sel.size else 0
    maxd = float(np.max(np.linalg.norm(imgs - m[:, None], axis=0))) + 1e-6 if sel.size else 0.0
    levels = [(s0[None, :], np.zeros((1, 0), dtype=int))]
    for k in range(omax):
        P, Q = levels[-1]
        newP, newQ = [], []
        for w in range(len(walls)):
            ok = (Q.shape[1] == 0) | (Q[:, -1] != w) if Q.shape[1] else np.ones(len(P), bool)
            side = (P - org[w]) @ nrm[w]
            ok = ok & (side < -1e-9)                       # in front of the plane (room side)
            if not ok.any():
                continue
            R_ = P[ok] - 2 * side[ok, None] * nrm[w]
            keep = np.linalg.norm(R_ - m, axis=1) <= maxd + 1e-6 if k == omax - 1 else np.ones(len(R_), bool)
            newP.append(R_[keep]); newQ.append(np.c_[Q[ok][keep], np.full(keep.sum(), w)])
        levels.append((np.vstack(newP) if newP else np.zeros((0, 3)), np.vstack(newQ) if newQ else np.zeros((0, k + 1), dtype=int)))
    out = np.zeros((3, sel.size))
    for col in range(sel.size):
        o, I = int(orders[col]), imgs[:, col]
        if o == 0:
            e = m - s0
        else:
            P, Q = levels[o]
            k = int(np.argmin(np.linalg.norm(P - I, axis=1)))
            seq = Q[k]
            chain = [s0]
            for w in seq:                                 # images along the sequence
                q = chain[-1]; chain.append(q - 2 * np.dot(q - org[w], nrm[w]) * nrm[w])
            p = m.copy()
            for kk in range(o, 0, -1):                    # receiver -> last wall ... -> first wall
                w, Ik = seq[kk - 1], chain[kk]
                den = np.dot(nrm[w], Ik - p)
                if abs(den) < 1e-12:
                    break
                p = p + np.dot(nrm[w], org[w] - p) / den * (Ik - p)
            e = p - s0
        out[:, col] = e / max(np.linalg.norm(e), 1e-12)
    return out


# ---------------------------------------------------------------- energy histogram (incoherent image sum)
HIST_BIN = 0.001


def specular_factors(cfg, room, sel, src_pos, rec_pos):
    """Energy factors [n_bands, len(sel)] of the image sources `sel`: finite reflector size (Kirchhoff-Fresnel) and
    scattering loss (1 - s) per reflection (reflections.py). Drawn and mesh halls only; switched off with
    "geometry": {"finite_reflectors": false} / {"specular_scatter_loss": false}. None when nothing applies."""
    if cfg is None or not has_geometry(cfg):
        return None
    g = cfg["geometry"]
    fin, sca = g.get("finite_reflectors", True), g.get("specular_scatter_loss", True)
    if not (fin or sca):
        return None
    import reflections
    return reflections.image_factors(_geom(cfg), room, sel, src_pos, rec_pos, cfg["c"], g["materials"], fin, sca)


_SEAT_CACHE = {}


def seat_dip_on(cfg):
    """Drawn and mesh halls with "geometry": {"seat_dip": {"on": true, ...}} (seatdip.py)."""
    sd = cfg.get("geometry", {}).get("seat_dip") if cfg is not None and has_geometry(cfg) else None
    return bool(sd) and sd.get("on", True)


def seat_dip_T(cfg, src_pos, rec_pos):
    """Seat-dip transfer function of the direct sound on the renderer's 1024-point bins, or None (seatdip.py)."""
    if not seat_dip_on(cfg):
        return None
    import seatdip
    prm = seatdip.seat_params(cfg["geometry"]["seat_dip"])
    if is_mesh(cfg):          # rows face the page's +y; the page frame is the model turned by rotate_deg
        ra = math.radians(float(cfg["geometry"]["mesh"].get("rotate_deg", 0) or 0))
        prm["normal"] = (math.sin(ra), math.cos(ra))
    key = json.dumps([cfg["geometry"], [float(x) for x in src_pos], [float(x) for x in rec_pos], cfg["fs"], cfg["c"]],
                     sort_keys=True, default=str)
    if key not in _SEAT_CACHE:
        _SEAT_CACHE[key] = seatdip.path_transfer(_geom(cfg), src_pos, rec_pos, prm, cfg["fs"], cfg["c"])
    return _SEAT_CACHE[key]


def seat_dip_images(cfg, room, sel, T):
    """With a seat dip on the path: mask over `sel` keeping all but the first-order reflections from the audience
    floor (their part is in T), and the index (into sel) of the direct sound."""
    S = room.sources[0]
    G = _geom(cfg)
    keep = np.array([not (S.orders[k] == 1 and S.walls[k] >= 0 and G["S"][S.walls[k]]["mat"] == "aud") for k in sel], bool)
    return keep


def _image_energy_hist(room, rec_pos, c, t_max, vis=None, cfg=None, src=None):
    S = room.sources[0]
    m = np.asarray(rec_pos, dtype=float)
    sel = np.arange(S.images.shape[1]) if vis is None else np.flatnonzero(vis)
    T = seat_dip_T(cfg, cfg["sources"][src]["pos"], rec_pos) if cfg is not None and src is not None and vis is not None \
        else None
    if T is not None:
        sel = sel[seat_dip_images(cfg, room, sel, T)]
    imgs, damp = S.images[:, sel], S.damping[:, sel]
    d = np.linalg.norm(imgs - m[:, None], axis=0)
    keep = (d / c < t_max) & (d > 1e-9)
    d, damp, sel = d[keep], damp[:, keep], sel[keep]
    E = (damp / d) ** 2 * np.exp(-np.asarray(room.air_absorption)[:, None] * d)
    if T is not None:
        import seatdip
        tb = seatdip.band_energy(T, cfg["fs"], room.octave_bands.centers)
        E[:, S.orders[sel] == 0] *= tb[:, None]
    if cfg is not None and src is not None:
        F = specular_factors(cfg, room, sel, cfg["sources"][src]["pos"], rec_pos)
        if F is not None:
            E = E * F
    dm = dir_model(cfg, src, room.octave_bands.centers) if cfg is not None and src is not None else None
    if dm is not None:
        E = E * dir_amp(dm, emission_dirs(cfg, room, cfg["sources"][src]["pos"], sel)) ** 2
    idx = np.floor(d / c / HIST_BIN).astype(int)
    hist = np.zeros((E.shape[0], int(round(t_max / HIST_BIN))))
    for b in range(E.shape[0]):
        np.add.at(hist[b], idx, E[b])
    return hist


def _smooth(h, n=10):
    k = np.ones(n) / n
    return np.stack([np.convolve(row, k, mode="same") for row in h])


_DIFF_CACHE = {}


def diffraction_on(cfg):
    # off by default for mesh halls: a tessellated curved surface has thousands of shallow "edges" that are not
    # physical wedges (UTD needs real edges between plane faces)
    return has_geometry(cfg) and cfg["geometry"].get("diffraction", not is_mesh(cfg))


def diffraction_arrivals(cfg, src, rec, centers, air, t_max):
    """UTD edge diffraction (diffraction.py) from source src to receiver rec, arrivals up to t_max (s); second order
    (diffract2) with "geometry": {"diffraction_order": 2}.
    Band quantities are on `centers` (pyroomacoustics octave bands); directivity of src applied to ga, g and eb."""
    import diffraction
    key = json.dumps([cfg["geometry"], stage_y(cfg)], sort_keys=True)
    if key not in _DIFF_CACHE:
        G = _geom(cfg)
        _DIFF_CACHE.clear()
        _DIFF_CACHE[key] = (G, diffraction.edges(G))
    G, E = _DIFF_CACHE[key]
    mats = cfg["geometry"]["materials"]
    nb = len(centers)

    def Rmat(k):
        a = list(mats[G["S"][k]["mat"]]["alpha"])
        a = [a[i] if i < len(a) else a[-1] for i in range(nb)]
        return np.sqrt(np.maximum(1e-6, 1 - np.asarray(a, float)))
    args = (G, E, cfg["sources"][src]["pos"], cfg["receivers"][rec], cfg["c"], Rmat,
            np.asarray(air, float) if air is not None and len(air) else np.zeros(nb), centers, t_max)
    ro = int(cfg["geometry"].get("diffraction_refl", 0))
    A = diffraction.diffract(*args, refl_order=ro)
    if int(cfg["geometry"].get("diffraction_order", 1)) >= 2:          # two edges in sequence (thick obstacles)
        A = A + diffraction.diffract2(*args, refl_order=ro)
    dm = dir_model(cfg, src, centers)
    if dm is not None and A:
        k = dir_amp(dm, np.array([q["e"] for q in A]).T)
        for i, q in enumerate(A):
            q["ga"] = q["ga"] * k[:, i]; q["g"] = q["g"] * k[:, i]; q["eb"] = q["eb"] * k[:, i] ** 2
    return A


# ---------------------------------------------------------------- discrete arrivals beyond the early window
_SPEC_CACHE = {}


def spec_on(cfg):
    """Higher-order specular paths found with rays (specpaths.py): OBJ mesh halls, where the image-source search
    stops at order 1. "geometry": {"spec_order": 0} switches it off (default 3)."""
    return has_geometry(cfg) and is_mesh(cfg) and int(cfg["geometry"].get("spec_order", 3)) >= 2


def discrete_ms(cfg):
    """Drawn and mesh halls: specular arrivals (images, ray-found paths, diffraction) are rendered as discrete
    arrivals up to this time after the direct sound ("geometry": {"discrete_ms": ...}, default 250 ms); only the
    energy they do not explain becomes noise there. Shoebox: None (early window only, as before)."""
    return float(cfg["geometry"].get("discrete_ms", 250.0)) if has_geometry(cfg) else None


def spec_arrivals(cfg, src, recs, centers, air):
    """{rec: [{"t", "image", "eb" [n_bands], "order"}]}: ray-found specular paths of orders 2 .. spec_order (mesh
    halls) up to discrete_ms after the direct sound, with the energy model of the first-order images (absorption,
    scattering loss, finite reflector, air, 1 / d^2, source directivity at the emission direction). The paths are
    cached per geometry and positions (they do not depend on the materials)."""
    import hashlib
    import specpaths
    G = _geom(cfg)
    g = cfg["geometry"]
    c = cfg["c"]
    s = np.asarray(cfg["sources"][src]["pos"], float)
    R = np.array([cfg["receivers"][r] for r in recs], float)
    tmx = np.linalg.norm(R - s, axis=1) / c + discrete_ms(cfg) / 1000
    order, rays = int(g.get("spec_order", 3)), int(g.get("spec_rays", 20000))
    if "_gid" not in G:
        mesh = g["mesh"]
        txt = mesh.get("obj_text") or open(mesh["obj"], encoding="utf-8", errors="ignore").read()
        G["_gid"] = hashlib.sha1((txt + json.dumps(mesh.get("axes", ""))).encode()).hexdigest()
    key = (G["_gid"], tuple(np.round(s, 6)), tuple(map(tuple, np.round(R, 6))), order, rays, round(c, 3),
           tuple(np.round(tmx, 6)))
    if key not in _SPEC_CACHE:
        _SPEC_CACHE[key] = specpaths.find_paths(G, s, R, order=order, t_max=tmx, c=c, n_rays=rays)
    found = _SPEC_CACHE[key]
    dm = dir_model(cfg, src, centers)
    fin, sca = g.get("finite_reflectors", True), g.get("specular_scatter_loss", True)
    out = {}
    for m, r in enumerate(recs):
        lst = []
        for q in found[m]:
            eb = specpaths.path_energy(G, g["materials"], q, s, R[m], centers, air, c, fin, sca)
            if dm is not None:
                e = np.asarray(q["pts"][0], float) - s
                eb = eb * dir_amp(dm, (e / np.linalg.norm(e))[:, None])[:, 0] ** 2
            lst.append({"t": q["dist"] / c, "image": np.asarray(q["image"], float), "eb": eb, "order": q["order"]})
        out[r] = lst
    return out


def _add_spec(h, arr):
    for q in arr:
        k = int(q["t"] / HIST_BIN)
        if k < h.shape[1]:
            h[:, k] += q["eb"]


def energy_hist(cfg, src, rec, t_max=2.5, return_resid=False, spec=False):
    """Octave-band energy per 1 ms bin. Returns (hist [n_bands, n_bins], band_centres).

    Shoebox: incoherent sum over the full image lattice (order <= ism_order_omni). Summing image
    energies incoherently avoids the coherent build-up of a perfectly regular shoebox lattice,
    which inflates band-filtered late energy in the synthesised waveform RIR.
    Geometry: specular images to geometry.ism_order (pyroomacoustics, visibility checked) plus the
    part of the pyroomacoustics ray-tracing histogram the images do not explain:
        H = H_ism + max(0, smooth(H_rt) - smooth(H_ism)),  10 ms smoothing.
    spec=True (mesh halls, spec_on): the ray-found higher-order specular paths count as images (spec_arrivals).
    """
    c = cfg["c"]
    if not has_geometry(cfg):
        room = make_room(cfg, cfg["binaural"]["ism_order_omni"])
        room.add_source(cfg["sources"][src]["pos"])
        room.add_microphone(cfg["receivers"][rec])
        room.image_source_model()
        h = _image_energy_hist(room, cfg["receivers"][rec], c, t_max, cfg=cfg, src=src)
        return (h, room.octave_bands.centers, None) if return_resid else (h, room.octave_bands.centers)
    g = cfg["geometry"]
    room = make_room(cfg, early_order(cfg))
    room.add_source(cfg["sources"][src]["pos"])
    room.add_microphone(cfg["receivers"][rec])
    room.image_source_model()
    h_ism = _image_energy_hist(room, cfg["receivers"][rec], c, t_max, visible_images(room, 0), cfg, src)
    if diffraction_on(cfg):                            # edge diffraction energy incl. interference at its boundaries
        for q in diffraction_arrivals(cfg, src, rec, room.octave_bands.centers, room.air_absorption, t_max):
            i = int(q["t"] / HIST_BIN)
            if i < h_ism.shape[1]:
                h_ism[:, i] += q["eb"]
        h_ism = np.maximum(h_ism, 0.0)
    if spec and spec_on(cfg):
        _add_spec(h_ism, spec_arrivals(cfg, src, [rec], room.octave_bands.centers, room.air_absorption)[rec])
    rt = make_room(cfg, 0, ray_tracing=True)
    rt.set_ray_tracing(n_rays=int(g.get("rays", 50000)), receiver_radius=0.5, hist_bin_size=HIST_BIN,
                       time_thres=t_max, energy_thres=RT_ENERGY_THRES)
    rt.add_source(cfg["sources"][src]["pos"])
    rt.add_microphone(cfg["receivers"][rec])
    import zlib
    pra.libroom.set_rng_seed(zlib.crc32(f"{src}|{rec}".encode()))   # reproducible rays per path (see manifest.json)
    rt.ray_tracing()
    h_rt = np.zeros_like(h_ism)
    raw = np.asarray(rt.rt_histograms[0][0][0])
    n = min(raw.shape[1], h_rt.shape[1])
    h_rt[:, :n] = raw[:, :n]
    # pyroomacoustics (0.10) leaves air absorption out of the ray-tracing histograms (it is applied later, when an
    # RIR is synthesised from them); apply it here per bin, distance = c t (checked: ratio with / without
    # air_absorption is exactly 1 in rt_histograms). The image-source part already includes it.
    t_c = (np.arange(h_rt.shape[1]) + 0.5) * HIST_BIN
    h_rt = h_rt * np.exp(-np.outer(np.asarray(room.air_absorption, float), c * t_c))
    dm = dir_model(cfg, src, room.octave_bands.centers)
    if dm is not None:                                 # directional source: diffuse power scales with 1 / Q
        h_rt = h_rt * dm["diffuse"][:, None]
    resid = np.maximum(0.0, _smooth(h_rt) - _smooth(h_ism))
    if return_resid:      # diffuse energy the image sources do not explain (added as noise inside the early window)
        return h_ism + resid, room.octave_bands.centers, resid
    return h_ism + resid, room.octave_bands.centers


def bank_to_band(fs, centers):
    """Index of the pyroomacoustics band nearest to each late-noise bank band."""
    out = []
    for lo, hi in octave_filterbank(fs)["edges"]:
        fc = np.sqrt(lo * hi) if lo > 0 and hi < fs / 2 else (lo * np.sqrt(2) if lo > 0 else hi / np.sqrt(2))
        out.append(int(np.argmin(np.abs(np.log(np.asarray(centers) / fc)))))
    return out


# ---------------------------------------------------------------- 바이노럴 초기부
def head_frame(cfg, rec):
    front = np.array([0.0, 1.0, 0.0])  # 무대(+y) 쪽을 정면으로 봄
    up = np.array([0.0, 0.0, 1.0])
    left = np.cross(up, front)
    return front, left, up


def visible_images(room, i=0):
    """Visibility mask of the image sources of source 0 at microphone i, each image counted once. On a mesh a
    reflection point on the shared edge of two coplanar triangles (e.g. on the symmetry plane of a hall, for a
    centred source and listener) is valid for both, and pyroomacoustics lists the same image once per triangle (or
    nearly the same, for nearly coplanar triangles). Images of the same order within 1 cm count as one (the first is
    kept; same rule as engine_geom.js ism)."""
    vis = room.visibility[0][i].astype(bool).copy()
    S = room.sources[0]
    kept = []
    for k in np.flatnonzero(vis):
        p, o = S.images[:, k], S.orders[k]
        if any(S.orders[j] == o and np.linalg.norm(S.images[:, j] - p) < 0.01 for j in kept):
            vis[k] = False
        else:
            kept.append(k)
    return vis


def early_binaural(cfg, src, rec, hrir: HRIRSet, n_len, spec=False):
    """Discrete arrivals: visible image sources, diffraction and (spec=True, mesh halls) the ray-found higher-order
    specular paths, each through the HRIR of its arrival direction. Shoebox: up to the early window (+ crossfade).
    Drawn / mesh halls: up to discrete_ms after the direct sound, and info["h_disc"] holds their energy per band
    and 1 ms bin, so that path_brir can leave it out of the noise."""
    fs, c = cfg["fs"], cfg["c"]
    b = cfg["binaural"]
    room = make_room(cfg, early_order(cfg))
    room.add_source(cfg["sources"][src]["pos"])
    room.add_microphone(cfg["receivers"][rec])
    room.image_source_model()
    S = room.sources[0]
    vis = visible_images(room, 0)
    sel = np.flatnonzero(vis)
    T = seat_dip_T(cfg, cfg["sources"][src]["pos"], cfg["receivers"][rec]) if has_geometry(cfg) else None
    if T is not None:                       # seat dip: the direct sound carries T, audience-floor reflections are in T
        sel = sel[seat_dip_images(cfg, room, sel, T)]
    imgs, damp = S.images[:, sel], S.damping[:, sel]
    m = np.array(cfg["receivers"][rec])
    v = imgs - m[:, None]
    dist = np.linalg.norm(v, axis=0)
    t_dir = dist.min() / c
    span = (b["early_window_ms"] + b["crossfade_ms"]) / 1000
    if has_geometry(cfg):
        span = max(span, discrete_ms(cfg) / 1000)
    t_end = t_dir + span
    keep = dist / c <= t_end
    v, dist, damp, sel = v[:, keep], dist[keep], damp[:, keep], sel[keep]

    # 완결성 점검: 다음 차수의 최단 도달이 창 안에 들어오는지
    max_ord_in = S.orders[sel].max()

    # 대역 진폭(감쇠/거리 + 공기흡음)
    band_f = room.octave_bands.centers
    amp = damp / dist
    if room.air_absorption is not None and len(room.air_absorption):
        amp = amp * np.exp(-0.5 * np.asarray(room.air_absorption)[:, None] * dist)
    F = specular_factors(cfg, room, sel, cfg["sources"][src]["pos"], cfg["receivers"][rec])
    if F is not None:
        amp = amp * np.sqrt(F)
    dm = dir_model(cfg, src, band_f)
    if dm is not None:
        amp = amp * dir_amp(dm, emission_dirs(cfg, room, cfg["sources"][src]["pos"], sel))

    if spec and spec_on(cfg):        # ray-found higher-order specular paths: like images (position, band amplitude)
        sp = [q for q in spec_arrivals(cfg, src, [rec], band_f, room.air_absorption)[rec] if q["t"] <= t_end]
        if sp:
            vs = np.stack([q["image"] for q in sp], axis=1) - m[:, None]
            v, dist = np.c_[v, vs], np.r_[dist, np.linalg.norm(vs, axis=0)]
            amp = np.c_[amp, np.sqrt(np.stack([q["eb"] for q in sp], axis=1))]
    diff = diffraction_arrivals(cfg, src, rec, band_f, room.air_absorption, None) if diffraction_on(cfg) else []
    if diff:
        t_dir = min(t_dir, min(q["t"] for q in diff))
        t_end = t_dir + span
        diff = [q for q in diff if q["t"] <= t_end]

    front, left, up = head_frame(cfg, rec)
    u = v / dist
    hd = np.c_[u.T @ front, u.T @ left, u.T @ up]  # 머리 좌표 단위벡터
    idx = np.argmax(hd @ hrir.dirs.T, axis=1)      # 최근접 HRIR 방향

    nfft = 1024
    pre = 128
    f = np.fft.rfftfreq(nfft, 1 / fs)
    lf = np.log(np.clip(f, 20, None))
    out = np.zeros((2, n_len))
    Hcache = {}
    for i in range(dist.size):
        k = idx[i]
        if k not in Hcache:
            h = np.zeros((2, nfft))
            L = min(hrir.ir.shape[-1], nfft - pre)
            h[:, pre:pre + L] = hrir.ir[k, :, :L]
            Hcache[k] = np.fft.rfft(h, axis=-1)
        g = np.interp(lf, np.log(band_f), amp[:, i]) if amp.shape[0] > 1 else np.full_like(f, amp[0, i])
        tau = dist[i] / c * fs
        n0 = int(np.floor(tau))
        frac = tau - n0
        X = Hcache[k] * g[None, :] * np.exp(-2j * np.pi * f * frac / fs)[None, :]
        y = np.fft.irfft(X, nfft, axis=-1)
        a = n0 - pre
        if T is not None and i < len(sel) and S.orders[sel[i]] == 0:     # seat dip: the direct sound through T
            import seatdip
            hT = seatdip.fir(T)
            y = np.stack([np.convolve(e, hT) for e in y])
            a -= seatdip.delay(T)
        lo, hi = max(a, 0), min(a + y.shape[1], n_len)
        if hi > lo:
            out[:, lo:hi] += y[:, lo - a:hi - a]
    if diff:
        import diffraction
        ldf = np.log(diffraction.DF)
        for q in diff:
            hq = np.array([q["h"] @ front, q["h"] @ left, q["h"] @ up])
            k = int(np.argmax(hrir.dirs @ hq))
            if k not in Hcache:
                h = np.zeros((2, nfft))
                L = min(hrir.ir.shape[-1], nfft - pre)
                h[:, pre:pre + L] = hrir.ir[k, :, :L]
                Hcache[k] = np.fft.rfft(h, axis=-1)
            g = np.interp(lf, np.log(band_f), q["ga"]) * (np.interp(lf, ldf, q["D"].real) + 1j * np.interp(lf, ldf, q["D"].imag))
            tau = q["t"] * fs
            n0 = int(np.floor(tau))
            X = Hcache[k] * g[None, :] * np.exp(-2j * np.pi * f * (tau - n0) / fs)[None, :]
            y = np.fft.irfft(X, nfft, axis=-1)
            a = n0 - pre
            lo, hi = max(a, 0), min(a + nfft, n_len)
            if hi > lo:
                out[:, lo:hi] += y[:, lo - a:hi - a]
    info = {"n_images": int(dist.size), "n_diffracted": len(diff), "max_order_in_window": int(max_ord_in),
            "order_limit": int(early_order(cfg)), "t_direct": t_dir}
    if has_geometry(cfg):
        hd = np.zeros((len(band_f), int(np.ceil((t_end + 0.01) / HIST_BIN))))
        idx_t = np.floor(dist / c / HIST_BIN).astype(int)
        e2 = amp ** 2
        if T is not None:
            import seatdip
            d0 = np.flatnonzero(S.orders[sel[:e2.shape[1]]] == 0) if len(sel) else []
            e2[:, d0] *= seatdip.band_energy(T, fs, band_f)[:, None]
        for bb in range(len(band_f)):
            np.add.at(hd[bb], idx_t, e2[bb])
        for q in diff:
            k = int(q["t"] / HIST_BIN)
            if k < hd.shape[1]:
                hd[:, k] += q["eb"]
        info["h_disc"] = np.maximum(hd, 0.0)
    return out, info


# ---------------------------------------------------------------- 후기부
def band_envelope(x, fs, sos, win_ms=5.0):
    y = signal.sosfiltfilt(sos, x)
    w = int(fs * win_ms / 1000)
    e = np.convolve(y ** 2, np.ones(w) / w, mode="same")
    return e  # 에너지 밀도(샘플당)


def late_dir_tables(hrir: HRIRSet):
    """Per direction bin (dirrays.BINS, head frame) sums over the HRIR directions in the bin, area weighted as in
    load_hrir: Om [nbin], BE [nbin, 2, n_bands] (band energies as in df_band_energy), X (cross spectrum L R*),
    PL, PR [nbin, COH_NFFT/2 + 1]. With energy per unit solid angle rho_d per bin, sum_d rho_d BE_d / sum_d rho_d Om_d
    is the ear energy and sum rho X / sqrt(sum rho PL * sum rho PR) the interaural coherence; rho constant gives
    exactly df_band_energy and the diffuse coherence."""
    if getattr(hrir, "_late_tab", None) is not None:
        return hrir._late_tab
    import dirrays
    d = hrir.dirs
    wgt = np.sqrt(np.clip(1 - d[:, 2] ** 2, 0, 1)) + 1e-6
    wgt = wgt / wgt.sum()
    b = np.argmax(d @ dirrays.BINS.T, axis=1)
    nb_ = dirrays.NBIN
    nfft = 4096
    P4 = np.abs(np.fft.rfft(hrir.ir, nfft, axis=-1)) ** 2
    f4 = np.fft.rfftfreq(nfft, 1 / hrir.fs)
    BEk = np.stack([P4[:, :, (f4 >= lo) & (f4 < hi)].mean(axis=2) for lo, hi in octave_filterbank(hrir.fs)["edges"]], axis=-1)
    H = np.fft.rfft(hrir.ir, COH_NFFT, axis=-1)
    tab = {"bin": b, "Om": np.bincount(b, wgt, nb_),
           "BE": np.stack([np.einsum("m,mrb->rb", wgt[b == i], BEk[b == i]) for i in range(nb_)]),
           "X": np.stack([np.einsum("m,mk->k", wgt[b == i], H[b == i, 0] * np.conj(H[b == i, 1])) for i in range(nb_)]),
           "PL": np.stack([np.einsum("m,mk->k", wgt[b == i], np.abs(H[b == i, 0]) ** 2) for i in range(nb_)]),
           "PR": np.stack([np.einsum("m,mk->k", wgt[b == i], np.abs(H[b == i, 1]) ** 2) for i in range(nb_)]),
           "f": np.fft.rfftfreq(COH_NFFT, 1 / hrir.fs)}
    hrir._late_tab = tab
    return tab


def late_field(hrir: HRIRSet, W, centers, fs):
    """Ear energies [2, n_bank_bands] and complex interaural coherence on tab["f"] for a late field with direction
    energies W [nbin, n_pra_bands] (dirrays.late_direction_energy). Bins without HRIR directions are dropped."""
    tab = late_dir_tables(hrir)
    Om = tab["Om"]
    rho = np.where(Om[:, None] > 0, W / np.maximum(Om[:, None], 1e-30), 0.0)        # [nbin, n_pra_bands]
    E = np.zeros((2, len(octave_filterbank(fs)["edges"])))
    for bi, pb in enumerate(bank_to_band(fs, centers)):
        r = rho[:, pb]
        E[:, bi] = np.einsum("d,dr->r", r, tab["BE"][:, :, bi]) / max(float(r @ Om), 1e-30)
    lc, lf = np.log(np.asarray(centers, float)), np.log(np.clip(tab["f"], 1.0, None))
    rf = np.stack([np.interp(lf, lc, rho[d]) for d in range(len(Om))])              # [nbin, nf]
    X = np.sum(rf * tab["X"], axis=0)
    g = X / np.sqrt(np.sum(rf * tab["PL"], axis=0) * np.sum(rf * tab["PR"], axis=0) + 1e-30)
    g[0] = 1.0
    return E, g


def coherent_pair_complex(rng, n_len, fs, coh_f, coh):
    """coherent_pair for a complex coherence Gamma = |Gamma| exp(j theta): a = arccos(|Gamma|) / 2 and the right
    channel turned by exp(-j theta), so that E[L R*] / sqrt(E|L|^2 E|R|^2) = Gamma."""
    N1, N2 = np.fft.rfft(rng.standard_normal(n_len)), np.fft.rfft(rng.standard_normal(n_len))
    fq = np.fft.rfftfreq(n_len, 1 / fs)
    m = np.clip(np.interp(fq, coh_f, np.abs(coh)), 0, 1)
    th = np.interp(fq, coh_f, np.unwrap(np.angle(coh)))
    a = np.arccos(m) / 2
    c, s = np.cos(a), np.sin(a)
    return np.fft.irfft(c * N1 + s * N2, n_len), np.fft.irfft((c * N1 - s * N2) * np.exp(-1j * th), n_len)


def late_binaural(cfg, hist, centers, hrir: HRIRSet, n_len, seed, dirw=None, resid=None):
    """Band noise shaped by the image-energy histogram (5 ms smoothing) and the diffuse-field HRTF gain.
    Left and right noise carry the diffuse-field interaural coherence of the HRIR set (coherent_pair);
    without it (coh is None) they are independent, which makes late interaural coherence too low."""
    fs = cfg["fs"]
    fb = octave_filterbank(fs)
    rng = np.random.default_rng(seed)
    out = np.zeros((2, n_len))
    out_r = np.zeros((2, n_len)) if resid is not None else None
    if dirw is not None:      # directional late field: ear energies and complex coherence from the arrival directions
        dfE, cg = late_field(hrir, dirw, centers, fs)
        pair_of = lambda: coherent_pair_complex(rng, n_len, fs, late_dir_tables(hrir)["f"], cg)
    else:
        dfE = hrir.df_band_energy
        pair_of = lambda: coherent_pair(rng, n_len, fs, hrir.coh_f, hrir.coh) if hrir.coh is not None \
            else (rng.standard_normal(n_len), rng.standard_normal(n_len))
    t_bin = np.minimum((np.arange(n_len) / fs / HIST_BIN).astype(int), hist.shape[1] - 1)
    for bi, (sos, (lo, hi), pb) in enumerate(zip(fb["sos"], fb["edges"], bank_to_band(fs, centers))):
        sm = np.convolve(hist[pb], np.ones(5) / 5, mode="same")
        env = sm[t_bin] / (HIST_BIN * fs) * (min(hi, fs / 2) - lo) / (fs / 2)   # energy per sample in this band
        if resid is not None:
            env_r = np.convolve(resid[pb], np.ones(5) / 5, mode="same")[t_bin] / (HIST_BIN * fs) * (min(hi, fs / 2) - lo) / (fs / 2)
        pair = pair_of()
        for ear in range(2):
            n = signal.sosfiltfilt(sos, pair[ear])
            n /= np.sqrt(np.mean(n ** 2)) + 1e-20
            out[ear] += n * np.sqrt(env * dfE[ear, bi])
            if resid is not None:          # same noise, shaped by the residual diffuse energy
                out_r[ear] += n * np.sqrt(env_r * dfE[ear, bi])
    return (out, out_r) if resid is not None else out


def crossfade_windows(n_len, fs, t_start, cf_ms):
    t = np.arange(n_len) / fs
    w = np.clip((t - t_start) / (cf_ms / 1000), 0, 1)
    w_late = np.sin(0.5 * np.pi * w) ** 2
    return 1 - w_late, w_late


def late_on(cfg):
    # the direction tracer holds a rays x surfaces matrix; for large meshes fall back to the isotropic late field
    if not has_geometry(cfg):
        return False
    default = not is_mesh(cfg) or len(_geom(cfg)["S"]) <= 3000
    return cfg["binaural"].get("late_directional", default)


def late_directions(cfg, src, recs, centers, air, n_rays=None):
    """Direction energies W [n_rec, nbin, n_bands] after the early window (dirrays.late_direction_energy), omni source.
    Seed from the path names, so the result is reproducible."""
    import dirrays, zlib
    G = _geom(cfg)
    mats = cfg["geometry"]["materials"]
    nb = len(centers)
    al = lambda m: [mats[m]["alpha"][i] if i < len(mats[m]["alpha"]) else mats[m]["alpha"][-1] for i in range(nb)]
    alpha = np.array([al(s["mat"]) for s in G["S"]])
    # per-band scattering: one probability per surface, the mean over the bands (as engine_geom.js rays for meshes)
    scat = np.array([float(np.mean(mats[s["mat"]].get("s", 0.0))) for s in G["S"]])
    S = np.asarray(cfg["sources"][src]["pos"], float)
    R = [np.asarray(cfg["receivers"][r], float) for r in recs]
    t_late = [np.linalg.norm(r - S) / cfg["c"] + cfg["binaural"]["early_window_ms"] / 1000 for r in R]
    n = int(n_rays or cfg["geometry"].get("late_dir_rays", 20000))
    return dirrays.late_direction_energy(G, S, R, t_late, alpha, scat, air, cfg["c"], n,
                                         seed=zlib.crc32(f"late|{src}".encode()))


def path_brir(cfg, src, rec, hrir, hist, centers, n_len, seed, dirw=None, resid=None, spec=False):
    """Shoebox: early * w_early + late * w_late. With resid (drawn hall: ray energy the image sources do not
    explain), noise shaped by resid is added to the early part, so the first 100 ms carry the scattered energy too
    (as in the browser: noise * (env_late * w_late + env_resid * w_early)).
    Drawn / mesh halls (discrete_ms): the discrete arrivals are not windowed (they reach discrete_ms after the
    direct sound) and the late noise carries only the energy they do not explain:
        discrete + noise(resid) * w_early + noise(max(0, hist - h_disc)) * w_late.
    spec=True: hist must come from energy_hist(..., spec=True) (the same set of paths)."""
    early, info = early_binaural(cfg, src, rec, hrir, n_len, spec=spec)
    hd = info.get("h_disc")
    if hd is not None:
        h2 = np.zeros_like(hist)
        n = min(hd.shape[1], hist.shape[1])
        h2[:, :n] = hd[:, :n]
        hist = np.maximum(hist - h2, 0.0)
    late = late_binaural(cfg, hist, centers, hrir, n_len, seed, dirw, resid)
    late_r = None
    if resid is not None:
        late, late_r = late
    t0 = info["t_direct"] + cfg["binaural"]["early_window_ms"] / 1000
    we, wl = crossfade_windows(n_len, cfg["fs"], t0, cfg["binaural"]["crossfade_ms"])
    if hd is not None:
        early_w = early + (late_r * we if late_r is not None else 0.0)
        late_w = late * wl
        sel = (we > 0) & (wl > 0)
        info["xfade_energy_ratio_early_over_late"] = float(np.sum(early_w[:, sel] ** 2) / (np.sum(late_w[:, sel] ** 2) + 1e-30))
        info["parts"] = (early_w, late_w)   # already windowed: the BRIR is their sum
        return early_w + late_w, info
    if late_r is not None:
        early = early + late_r
    # 연결부 에너지 점검(교차 구간에서 초기부/후기부 에너지 비)
    sel = (we > 0) & (wl > 0)
    ratio = float(np.sum(early[:, sel] ** 2) / (np.sum(late[:, sel] ** 2) + 1e-30))
    info["xfade_energy_ratio_early_over_late"] = ratio
    info["parts"] = (early, late)  # 뷰어가 같은 창 함수로 다시 잇기 위해 보관
    return early * we + late * wl, info


# ---------------------------------------------------------------- 조건(지연·게인)
def shift(x, n, n_len):
    y = np.zeros(x.shape[:-1] + (n_len,))
    L = min(x.shape[-1], n_len - n)
    if L > 0:
        y[..., n:n + L] = x[..., :L]
    return y


def condition_params(cfg, itdg_ms, lr_db, E_A_ref, E_B_ref):
    """중앙 기준 지연·게인(확성 음원 직접음 기준). 음수 지연은 무대 음 전체를 늦추는 것으로 구현(물리적 실현 불가 표시)."""
    ref = cfg["conditions"]["reference_receiver"]
    tA = direct_time(cfg, AMP, ref)
    tB = min(direct_time(cfg, "B_L", ref), direct_time(cfg, "B_R", ref))
    d = itdg_ms / 1000 - (tB - tA)          # B에 줄 전기적 지연(s)
    dB, dA = (d, 0.0) if d >= 0 else (0.0, -d)
    gain = np.sqrt(10 ** (lr_db / 10) * E_A_ref / E_B_ref)
    return {"delay_B_s": dB, "delay_A_s": dA, "gain_B": gain, "realizable": d >= 0}


def seat_direct(cfg, pts, centers, band_idx=(2, 3)):
    """Direct-sound geometry for many listener points pts [N, 3] (no room, no occlusion test).
    Returns direct times tA, tBL, tBR (s) and Ldir (dB): 10 log10(sum over PAs of a^2 / r^2 * rA^2),
    a^2 = PA directivity energy averaged over the 500 and 1000 Hz octaves. Ldir(seat) - Ldir(ref) is the
    direct-sound correction used for the per-seat level-ratio estimate (an engineering assumption:
    the room part of the level ratio is taken to be the same as at the reference seat)."""
    pts = np.asarray(pts, float)
    c = cfg["c"]
    pos = lambda k: np.array(cfg["sources"][k]["pos"], float)
    rA = np.linalg.norm(pts - pos(AMP), axis=1)
    out = {"tA": rA / c}
    e_pa = np.zeros(len(pts))
    for k in ("B_L", "B_R"):
        v = pts - pos(k)
        r = np.linalg.norm(v, axis=1)
        out["t" + k.replace("_", "")] = r / c
        dm = dir_model(cfg, k, centers)
        a2 = np.ones(len(pts)) if dm is None else np.mean(dir_amp(dm, (v / r[:, None]).T)[list(band_idx)] ** 2, axis=0)
        e_pa += a2 / r ** 2
    out["Ldir"] = 10 * np.log10(e_pa * rA ** 2)
    return out


# ---------------------------------------------------------------- 지표
def energy_hists(cfg, src, recs, t_max=2.5, n_rays=None, seed=None, return_resid=False, spec=False):
    """energy_hist for several receivers at once (one image-source run and one ray-tracing run shared by all
    receivers; same model as energy_hist). Used for room-criteria checks over many seats (validate_fratoni.py) and by
    run.py when geometry.shared_rays is set. Returns ({rec: hist [n_bands, n_bins]}, band_centres), with
    return_resid also {rec: resid} (as energy_hist)."""
    import zlib
    c = cfg["c"]
    g = cfg.get("geometry") or {}
    pos = [cfg["receivers"][r] for r in recs]
    res = {}
    room = make_room(cfg, early_order(cfg) if has_geometry(cfg) else cfg["binaural"]["ism_order_omni"])
    room.add_source(cfg["sources"][src]["pos"])
    room.add_microphone_array(np.array(pos, float).T)
    room.image_source_model()
    out = {}
    if not has_geometry(cfg):
        for i, r in enumerate(recs):
            out[r] = _image_energy_hist(room, pos[i], c, t_max, cfg=cfg, src=src)
        return out, room.octave_bands.centers
    rt = make_room(cfg, 0, ray_tracing=True)
    rt.set_ray_tracing(n_rays=int(n_rays or g.get("rays", 50000)), receiver_radius=0.5, hist_bin_size=HIST_BIN,
                       time_thres=t_max, energy_thres=RT_ENERGY_THRES)
    rt.add_source(cfg["sources"][src]["pos"])
    rt.add_microphone_array(np.array(pos, float).T)
    pra.libroom.set_rng_seed(int(seed) if seed is not None else zlib.crc32(f"{src}|*".encode()))
    rt.ray_tracing()
    dm = dir_model(cfg, src, room.octave_bands.centers)
    sp_arr = spec_arrivals(cfg, src, recs, room.octave_bands.centers, room.air_absorption) if spec and spec_on(cfg) else {}
    for i, r in enumerate(recs):
        h_ism = _image_energy_hist(room, pos[i], c, t_max, visible_images(room, i), cfg, src)
        if diffraction_on(cfg):
            for q in diffraction_arrivals(cfg, src, r, room.octave_bands.centers, room.air_absorption, t_max):
                k = int(q["t"] / HIST_BIN)
                if k < h_ism.shape[1]:
                    h_ism[:, k] += q["eb"]
            h_ism = np.maximum(h_ism, 0.0)
        if r in sp_arr:
            _add_spec(h_ism, sp_arr[r])
        h_rt = np.zeros_like(h_ism)
        raw = np.asarray(rt.rt_histograms[i][0][0])
        n = min(raw.shape[1], h_rt.shape[1])
        h_rt[:, :n] = raw[:, :n]
        t_c = (np.arange(h_rt.shape[1]) + 0.5) * HIST_BIN
        h_rt = h_rt * np.exp(-np.outer(np.asarray(room.air_absorption, float), c * t_c))
        if dm is not None:
            h_rt = h_rt * dm["diffuse"][:, None]
        res[r] = np.maximum(0.0, _smooth(h_rt) - _smooth(h_ism))
        out[r] = h_ism + res[r]
    return (out, room.octave_bands.centers, res) if return_resid else (out, room.octave_bands.centers)


def schroeder_db(x):
    e = np.cumsum((x ** 2)[::-1])[::-1]
    return 10 * np.log10(e / e[0] + 1e-30)


def decay_time(edc, fs, hi_db, lo_db):
    t = np.arange(len(edc)) / fs
    sel = (edc <= hi_db) & (edc >= lo_db)
    if sel.sum() < 10:
        return np.nan
    p = np.polyfit(t[sel], edc[sel], 1)
    return -60.0 / p[0]


def iso3382_omni(rir, fs, t0, bands=(500, 1000)):
    """C80, D50, Ts, EDT, T30: 각 옥타브 대역 값을 계산해 지정 대역 평균."""
    n0 = int(round(t0 * fs))
    res = {k: [] for k in ("C80", "D50", "Ts_ms", "EDT", "T30")}
    for fc in bands:
        y = band_filter(rir, fs, fc)[n0:]
        e = y ** 2
        n50, n80 = int(0.05 * fs), int(0.08 * fs)
        res["C80"].append(10 * np.log10(e[:n80].sum() / e[n80:].sum()))
        res["D50"].append(e[:n50].sum() / e.sum())
        res["Ts_ms"].append(1000 * np.sum(np.arange(len(e)) / fs * e) / e.sum())
        edc = schroeder_db(y)
        res["EDT"].append(decay_time(edc, fs, 0, -10))
        res["T30"].append(decay_time(edc, fs, -5, -35))
    return {k: float(np.nanmean(v)) for k, v in res.items()}


def iso3382_energy(parts, t0, bands=(500, 1000), centers=None):
    """C80, D50, Ts, EDT, T30 from summed energy histograms.

    parts: list of (hist [n_bands, n_bins], delay_s, power_gain). Mean over the given octave bands.
    """
    res = {k: [] for k in ("C80", "D50", "Ts_ms", "EDT", "T30")}
    n = parts[0][0].shape[1] + 200
    for fc in bands:
        b = int(np.argmin(np.abs(np.asarray(centers) - fc)))
        h = np.zeros(n)
        for hist, delay, g2 in parts:
            sh = int(round(delay / HIST_BIN))
            h[sh:sh + hist.shape[1]] += hist[b] * g2
        e = h[int(np.floor(t0 / HIST_BIN)):]
        tot = e.sum()
        res["C80"].append(10 * np.log10(e[:80].sum() / e[80:].sum()))
        res["D50"].append(e[:50].sum() / tot)
        res["Ts_ms"].append(1000 * np.sum((np.arange(len(e)) + 0.5) * HIST_BIN * e) / tot)
        edc = 10 * np.log10(np.cumsum(e[::-1])[::-1] / tot + 1e-30)
        # decay range inside the window: last 100 ms (ending 200 ms before the end) re the first 100 ms
        end = parts[0][0].shape[1] - int(np.floor(t0 / HIST_BIN))
        rng = 10 * np.log10(e[:100].sum() / (e[max(0, end - 300):end - 200].sum() + 1e-300))
        res["EDT"].append(decay_time(edc, 1 / HIST_BIN, 0, -10) if rng >= 25 else np.nan)
        res["T30"].append(decay_time(edc, 1 / HIST_BIN, -5, -35) if rng >= 45 else np.nan)
    return {k: float(np.nanmean(v)) for k, v in res.items()}


def iacc_e3(brir, fs, t0):
    n0, n80, lag = int(round(t0 * fs)), int(0.08 * fs), int(0.001 * fs)
    vals = []
    for fc in (500, 1000, 2000):
        y = band_filter(brir, fs, fc)[:, n0:n0 + n80]
        l, r = y
        cc = signal.correlate(l, r, mode="full")
        mid = len(r) - 1
        vals.append(np.max(np.abs(cc[mid - lag:mid + lag + 1])) / np.sqrt(np.sum(l ** 2) * np.sum(r ** 2)))
    return float(np.mean(vals))


def iacc_l(brir, fs, t0, t_end=None, bands=(500, 1000, 2000)):
    """IACC L (late, 80 ms after t0 to t_end or the end), mean over the octave bands (default 500 / 1k / 2k Hz), lag +-1 ms."""
    n0, lag = int(round((t0 + 0.08) * fs)), int(0.001 * fs)
    n1 = brir.shape[1] if t_end is None else int(round(t_end * fs))
    vals = []
    for fc in bands:
        l, r = band_filter(brir, fs, fc)[:, n0:n1]
        L, R = np.fft.rfft(l, 2 * len(l)), np.fft.rfft(r, 2 * len(r))
        cc = np.fft.irfft(L * np.conj(R))
        best = max(np.max(np.abs(cc[:lag + 1])), np.max(np.abs(cc[-lag:])))
        vals.append(best / np.sqrt(np.sum(l ** 2) * np.sum(r ** 2)))
    return float(np.mean(vals))


def onset_time(x, fs, thr_db=-20.0):
    """BRIR(2채널)의 첫 도달: 두 귀 중 이른 쪽, 피크 대비 thr_db 첫 초과 지점."""
    a = np.max(np.abs(x), axis=0)
    i = np.argmax(a >= a.max() * 10 ** (thr_db / 20))
    return i / fs


# ---------------------------------------------------------------- 자극 생성(드라이 음원 확보 후 사용)
def make_stimulus(dry_amp, dry_unamp, brir_amp, brir_unamp, brir_BL, brir_BR, params, fs):
    """확성 음원: 직접음(brir_amp) + PA(B_L+B_R, 지연·게인). 비확성 음원: 직접음만. dry_unamp는 None 가능."""
    nA, nB = int(round(params["delay_A_s"] * fs)), int(round(params["delay_B_s"] * fs))
    conv = lambda x, h: np.stack([signal.fftconvolve(x, h[e]) for e in range(2)])
    parts = [(conv(dry_amp, brir_amp), nA), (params["gain_B"] * conv(dry_amp, brir_BL + brir_BR), nB)]
    if dry_unamp is not None:
        parts.append((conv(dry_unamp, brir_unamp), nA))
    n = max(y.shape[1] + d for y, d in parts)
    return sum(shift(y, d, n) for y, d in parts)


# ---------------------------------------------------------------- 가시화용: 초기 도래음 목록
def image_arrivals(cfg, src, rec, window_ms=150.0, order=None):
    """허상 음원별 도래 시각(s), 방위각(deg, 왼쪽 +), 고도각(deg), 레벨(dB, 대역 평균 진폭)."""
    c = cfg["c"]
    room = make_room(cfg, order or cfg["binaural"]["ism_order_early"])
    room.add_source(cfg["sources"][src]["pos"])
    room.add_microphone(cfg["receivers"][rec])
    room.image_source_model()
    S = room.sources[0]
    vis = visible_images(room, 0)
    imgs, damp, orders = S.images[:, vis], S.damping[:, vis], S.orders[vis]
    sel = np.flatnonzero(vis)
    m = np.array(cfg["receivers"][rec])
    v = imgs - m[:, None]
    dist = np.linalg.norm(v, axis=0)
    t = dist / c
    keep = t <= t.min() + window_ms / 1000
    v, dist, damp, t, orders, sel = v[:, keep], dist[keep], damp[:, keep], t[keep], orders[keep], sel[keep]
    amp = damp / dist
    if room.air_absorption is not None and len(room.air_absorption):
        amp = amp * np.exp(-0.5 * np.asarray(room.air_absorption)[:, None] * dist)
    dm = dir_model(cfg, src, room.octave_bands.centers)
    if dm is not None:
        amp = amp * dir_amp(dm, emission_dirs(cfg, room, cfg["sources"][src]["pos"], sel))
    # image sources only; diffracted arrivals: diffraction_arrivals() (this block referenced undefined names and
    # was removed; the function has no callers in the repository)
    front, left, up = head_frame(cfg, rec)
    u = v / dist
    az = np.degrees(np.arctan2(u.T @ left, u.T @ front))
    el = np.degrees(np.arcsin(np.clip(u.T @ up, -1, 1)))
    lev = 20 * np.log10(np.sqrt(np.mean(amp ** 2, axis=0)) + 1e-12)
    return t, az, el, lev, orders
