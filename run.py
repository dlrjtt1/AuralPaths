"""
실행: python run.py [config.json]
SOFA 파일이 있으면 바이노럴 BRIR까지, 없으면 무지향 RIR·기하 지표·평면도만 산출한다.
"""
import csv
import os
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import numpy as np
import soundfile as sf

import brir_proto as bp


def main(cfg_path="config.json"):
    t_start = time.time()
    cfg = bp.load_config(cfg_path)
    fs = cfg["fs"]
    out = cfg["output_dir"]
    os.makedirs(os.path.join(out, "brir"), exist_ok=True)
    hp_path = cfg["binaural"].get("headphone_filter")
    hpcf = bp.load_hpcf(hp_path, cfg["fs"]) if hp_path and os.path.exists(hp_path) else None
    if hpcf is not None:
        os.makedirs(os.path.join(out, "brir_" + hpcf[1]), exist_ok=True)
    log = []
    say = lambda s: (print(s), log.append(s))

    recs, srcs = bp.receiver_names(cfg), bp.source_names(cfg)
    paths_B = ["B_L", "B_R"]

    # 1) 무지향 RIR
    n_len = int(2.5 * fs)
    if bp.has_geometry(cfg):
        omni = None
        say(f"[geometry] drawn hall: {len(bp._geom(cfg)['S'])} surfaces, ISM order {bp.early_order(cfg)}, "
            f"{cfg['geometry'].get('rays', 50000)} rays (pyroomacoustics)")
    else:
        omni = bp.omni_rirs(cfg)
        omni = {k: np.pad(v, (0, max(0, n_len - len(v))))[:n_len] for k, v in omni.items()}
        say(f"[omni] 고차 ISM(order {cfg['binaural']['ism_order_omni']}) RIR {len(omni)}개 산출")
    hist, resid = {}, {}
    if bp.has_geometry(cfg) and cfg["geometry"].get("shared_rays"):     # one ray-tracing run per source, all seats
        for s in srcs:
            h, centers, rs = bp.energy_hists(cfg, s, recs, return_resid=True)
            for r in recs:
                hist[(s, r)], resid[(s, r)] = h[r], rs[r]
    else:
        for r in recs:
            for s in srcs:
                hist[(s, r)], centers, resid[(s, r)] = bp.energy_hist(cfg, s, r, return_resid=True)
    say(f"[hist] octave-band image-energy histograms: {len(hist)} paths")

    # 2) 바이노럴(SOFA 있을 때)
    sofa = cfg["binaural"]["sofa_path"]
    binaural = os.path.exists(sofa)
    if bp.has_geometry(cfg) and not binaural:
        sys.exit("A drawn hall needs the KU100 SOFA file (hrir/KU100.sofa).")
    brir, info = {}, {}
    if binaural:
        hrir = bp.load_hrir(sofa, fs)
        say(f"[hrir] {sofa}: {hrir.ir.shape[0]}방향, {hrir.ir.shape[-1]}탭, fs={hrir.fs}, 정면 HRIR 선행 지연 {hrir.bulk_delay_s*1000:.2f} ms(검출 시 보정)")
        dirw = {}
        if bp.late_on(cfg):     # arrival directions of the late field (one ray-tracing run per source, all receivers)
            air = bp.make_room(cfg, 0).air_absorption
            for s in srcs:
                dirw[s] = bp.late_directions(cfg, s, recs, centers, air)
            say(f"[late] directional late field: {cfg['geometry'].get('late_dir_rays', 20000)} rays per source, "
                f"{len(dirw)} sources, 64 direction bins")
        if bp.diffraction_on(cfg):
            import diffraction
            say(f"[diffraction] first-order UTD on {len(diffraction.edges(bp._geom(cfg)))} convex edges")
        for i, r in enumerate(recs):
            for j, s in enumerate(srcs):
                brir[(s, r)], info[(s, r)] = bp.path_brir(cfg, s, r, hrir, hist[(s, r)], centers, n_len, seed=100 * i + j,
                                                          dirw=dirw[s][i] if s in dirw else None, resid=resid[(s, r)])
                sf.write(os.path.join(out, "brir", f"{r}_{s}.wav"), brir[(s, r)].T.astype(np.float32), fs, subtype="FLOAT")
                if hpcf is not None:   # same BRIR through the headphone compensation filter, for headphone listening
                    from scipy.signal import fftconvolve
                    yh = np.stack([fftconvolve(ch, hpcf[0])[: ch.size] for ch in brir[(s, r)]])
                    sf.write(os.path.join(out, "brir_" + hpcf[1], f"{r}_{s}.wav"), yh.T.astype(np.float32), fs, subtype="FLOAT")
                d = info[(s, r)]
                say(f"[brir] {r}-{s}: 허상 {d['n_images']}개, 회절 {d.get('n_diffracted', 0)}개, 창 내 최대 차수 {d['max_order_in_window']}/{d['order_limit']}, "
                    f"교차구간 초기/후기 에너지비 {d['xfade_energy_ratio_early_over_late']:.2f}")
        parts = {}
        for k, d in info.items():
            e, l = d.pop("parts")
            n_e = int(0.2 * fs)
            parts[f"{k[1]}|{k[0]}|early"] = e[:, :n_e].astype(np.float32)
            parts[f"{k[1]}|{k[0]}|late"] = l.astype(np.float32)
        np.savez_compressed(os.path.join(out, "brir_parts.npz"), **parts)
    else:
        say(f"[hrir] {sofa} 없음 -> 바이노럴 합성과 IACC_E3 생략")

    # 3) 경로별 직접음 도달 검증(기하 vs BRIR 검출)
    with open(os.path.join(out, "path_checks.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["receiver", "path", "t_direct_geom_ms", "t_onset_detected_ms", "diff_ms"])
        for r in recs:
            for s in srcs:
                tg = bp.direct_time(cfg, s, r) * 1000
                if not binaural and omni is None:
                    continue
                x = brir[(s, r)] if binaural else omni[(s, r)][None, :]
                td = (bp.onset_time(x, fs) - (hrir.bulk_delay_s if binaural else 0.0)) * 1000
                w.writerow([r, s, f"{tg:.3f}", f"{td:.3f}", f"{td - tg:.3f}"])

    # 4) 조건별 합성과 지표
    ref = cfg["conditions"]["reference_receiver"]
    E = lambda x: float(np.sum(x ** 2))
    hB = {r: (brir[("B_L", r)] + brir[("B_R", r)]) if binaural else None for r in recs}
    oB = {r: omni[("B_L", r)] + omni[("B_R", r)] for r in recs} if omni is not None else None
    if binaural:
        E_A_ref, E_B_ref = E(brir[(bp.AMP, ref)]), E(hB[ref])
        lr_basis = "binaural BRIR 에너지(양귀 합)"
    else:
        E_A_ref, E_B_ref = E(omni[(bp.AMP, ref)]), E(oB[ref])
        lr_basis = "무지향 RIR 에너지"
    say(f"[cond] 레벨비 기준: {ref} 수음점, {lr_basis}")

    rows = []
    for itdg in cfg["conditions"]["itdg_ms"]:
        for lr in cfg["conditions"]["level_ratio_db"]:
            p = bp.condition_params(cfg, itdg, lr, E_A_ref, E_B_ref)
            nA, nB = int(round(p["delay_A_s"] * fs)), int(round(p["delay_B_s"] * fs))
            for r in recs:
                tA = bp.direct_time(cfg, bp.AMP, r) + p["delay_A_s"]
                tBL = bp.direct_time(cfg, "B_L", r) + p["delay_B_s"]
                tBR = bp.direct_time(cfg, "B_R", r) + p["delay_B_s"]
                t0 = min(tA, tBL, tBR)
                g2 = p["gain_B"] ** 2
                m = bp.iso3382_energy([(hist[(bp.AMP, r)], p["delay_A_s"], 1.0), (hist[("B_L", r)], p["delay_B_s"], g2),
                                       (hist[("B_R", r)], p["delay_B_s"], g2)], t0, centers=centers)
                row = {
                    "receiver": r, "itdg_nominal_ms": itdg, "level_ratio_nominal_db": lr,
                    "delay_B_ms": round(p["delay_B_s"] * 1000, 3), "delay_A_ms": round(p["delay_A_s"] * 1000, 3),
                    "gain_B_db": round(20 * np.log10(p["gain_B"]), 2), "realizable_in_hall": p["realizable"],
                    "itdg_eff_BL_ms": round((tBL - tA) * 1000, 2), "itdg_eff_BR_ms": round((tBR - tA) * 1000, 2),
                }
                if binaural:
                    b = bp.shift(brir[(bp.AMP, r)], nA, n_len) + p["gain_B"] * bp.shift(hB[r], nB, n_len)
                    row["level_ratio_eff_db"] = round(10 * np.log10(p["gain_B"] ** 2 * E(hB[r]) / E(brir[(bp.AMP, r)])), 2)
                    row["IACC_E3"] = round(bp.iacc_e3(b, fs, t0), 3)
                    row["IACC_L"] = round(bp.iacc_l(b, fs, t0), 3)
                    row["IACC_L_125_250"] = round(bp.iacc_l(b, fs, t0, bands=(125, 250)), 3)
                else:
                    row["level_ratio_eff_db"] = round(10 * np.log10(p["gain_B"] ** 2 * E(oB[r]) / E(omni[(bp.AMP, r)])), 2)
                    row["IACC_E3"] = ""
                    row["IACC_L"] = ""
                    row["IACC_L_125_250"] = ""
                row.update({k: round(v, 3) for k, v in m.items()})
                rows.append(row)
    with open(os.path.join(out, "conditions.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    say(f"[cond] {len(rows)}행 -> conditions.csv")

    # 4b) 좌석 지도: 도면에서 딴 좌석 전체의 실효 ITDG(직접음 기하)와 레벨비 추정
    seats = (cfg.get("seats") or {}).get("xyz") or []
    if seats:
        ids = [f"S{i + 1:03d}" for i in range(len(seats))]
        sd = bp.seat_direct(cfg, seats, centers)
        rd = bp.seat_direct(cfg, [cfg["receivers"][r] for r in recs], centers)
        L_ref = rd["Ldir"][recs.index(ref)]
        srows = []
        for itdg in cfg["conditions"]["itdg_ms"]:
            for lr in cfg["conditions"]["level_ratio_db"]:
                p = bp.condition_params(cfg, itdg, lr, E_A_ref, E_B_ref)
                tA = sd["tA"] + p["delay_A_s"]
                bl, br = (sd["tBL"] + p["delay_B_s"] - tA) * 1000, (sd["tBR"] + p["delay_B_s"] - tA) * 1000
                for i, sid in enumerate(ids):
                    e = min(bl[i], br[i])
                    srows.append({"seat": sid, "x": seats[i][0], "y": seats[i][1], "z": seats[i][2],
                                  "itdg_nominal_ms": itdg, "level_ratio_nominal_db": lr,
                                  "itdg_eff_BL_ms": round(bl[i], 2), "itdg_eff_BR_ms": round(br[i], 2),
                                  "itdg_eff_ms": round(e, 2), "pa_first": bool(e < 0),
                                  "level_ratio_est_db": round(lr + sd["Ldir"][i] - L_ref, 2)})
        with open(os.path.join(out, "seat_map.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(srows[0].keys()))
            w.writeheader()
            w.writerows(srows)
        # how good is the direct-sound level estimate? compare with the BRIR energy ratio at the receivers
        errs = [lr0 + rd["Ldir"][recs.index(r["receiver"])] - L_ref - r["level_ratio_eff_db"]
                for r in rows for lr0 in [r["level_ratio_nominal_db"]]]
        say(f"[seats] {len(ids)}석 x {len(srows) // len(ids)}조건 -> seat_map.csv; "
            f"레벨비 추정(직접음 보정) vs BRIR 에너지비, 수음점 {len(recs)}곳: 최대 오차 {max(abs(e) for e in errs):.2f} dB")

    # 5) 평면도: 좌석별 실효 ITDG(가까운 PA 기준, 직접음 기하 계산)
    if not bp.has_geometry(cfg):        # the plan uses the shoebox dimensions; not drawn for OBJ / drawn halls
        plan_figure(cfg, os.path.join(out, "plan_itdg.png"))
    if binaural:
        import export_viewer
        try:
            export_viewer.main(cfg_path)
            say(f"[viewer] {os.path.join(out, 'viewer.html')} updated (open in a browser)")
        except KeyError as e:       # configs written by scripts may lack fields the page needs; BRIRs are not affected
            say(f"[viewer] not written ({e!r} missing in the config); BRIRs and manifest are")
    write_manifest(cfg_path, cfg, out, sofa if binaural else None, hp_path if hpcf is not None else None, recs, srcs)
    say(f"[manifest] {os.path.join(out, 'manifest.json')}")
    say(f"[done] {time.time() - t_start:.1f} s")
    with open(os.path.join(out, "run_log.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log))


def sha256(path):
    """SHA-256 of a file; for .wav files of the audio samples only (float32), because libsndfile writes a
    time stamp into the PEAK chunk of float WAV files, so identical audio would get different file hashes."""
    import hashlib
    if path.lower().endswith(".wav"):
        import soundfile as _sf
        x, f = _sf.read(path, dtype="float32", always_2d=True)
        return hashlib.sha256(np.ascontiguousarray(x).tobytes() + str(f).encode()).hexdigest()
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_manifest(cfg_path, cfg, out, sofa, hp_path, recs, srcs):
    """Generation record for one BRIR set: code version and checksums, the config as used, data files,
    seed scheme and a checksum per output file. Freeze this file together with the BRIRs used in an
    experiment; make_stimuli.py copies it into the stimulus set."""
    import datetime, json, platform
    import export_viewer
    here = os.path.dirname(os.path.abspath(__file__))
    code = {f: sha256(os.path.join(here, f)) for f in ("brir_proto.py", "geometry.py", "diffraction.py", "dirrays.py", "run.py", "engine_geom.js", "export_viewer.py")
            if os.path.exists(os.path.join(here, f))}
    files = {}
    for sub in sorted(os.listdir(out)):
        d = os.path.join(out, sub)
        if os.path.isdir(d) and sub.startswith("brir"):
            for f in sorted(os.listdir(d)):
                if f.endswith(".wav"):
                    files[f"{sub}/{f}"] = sha256(os.path.join(d, f))
    for f in ("conditions.csv", "seat_map.csv", "path_checks.csv"):
        if os.path.exists(os.path.join(out, f)):
            files[f] = sha256(os.path.join(out, f))
    m = {
        "kind": "AuralPaths BRIR set",
        "auralpaths_version": export_viewer.VERSION,
        "created": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "config_path": os.path.relpath(cfg_path, here) if os.path.isabs(cfg_path) else cfg_path,
        "config_sha256": sha256(cfg_path),
        "config": cfg,
        "code_sha256": code,
        "data_sha256": {k: sha256(v) for k, v in (("hrir", sofa), ("headphone_filter", hp_path)) if v},
        "python": platform.python_version(),
        "numpy": np.__version__,
        "fs": cfg["fs"], "receivers": recs, "paths": srcs,
        "time_zero": "sound emission at the source (BRIRs include the propagation delay)",
        "seed_scheme": "late noise seed = 100 * receiver index + path index (order of receivers / paths above); ray tracing seed = crc32(\"path|receiver\") per path; the browser viewer uses its own fixed seed",
        "files_sha256": files,
    }
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1)


def plan_figure(cfg, path):
    plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]
    W, D, _ = cfg["room"]["dims_m"]
    c = cfg["c"]
    A = np.array(cfg["sources"][bp.AMP]["pos"])
    BL, BR = (np.array(cfg["sources"][k]["pos"]) for k in ("B_L", "B_R"))
    ref = np.array(cfg["receivers"][cfg["conditions"]["reference_receiver"]])
    z = ref[2]
    xs, ys = np.linspace(0.5, W - 0.5, 160), np.linspace(1.0, A[1] - 3.0, 160)
    X, Y = np.meshgrid(xs, ys)
    P = np.stack([X, Y, np.full_like(X, z)], -1)
    dist = lambda S: np.linalg.norm(P - S, axis=-1)
    geo_ref = (min(np.linalg.norm(BL - ref), np.linalg.norm(BR - ref)) - np.linalg.norm(A - ref)) / c
    cmap = LinearSegmentedColormap.from_list("div", ["#c9372c", "#f0efec", "#2a78d6"])
    itdgs = cfg["conditions"]["itdg_ms"]
    fig, axes = plt.subplots(1, len(itdgs), figsize=(4.2 * len(itdgs), 4.8), sharey=True, facecolor="#fcfcfb")
    for ax, itdg in zip(axes, itdgs):
        d = itdg / 1000 - geo_ref
        dA, dB = (0.0, d) if d >= 0 else (-d, 0.0)
        eff = (np.minimum(dist(BL), dist(BR)) / c + dB - (dist(A) / c + dA)) * 1000
        im = ax.pcolormesh(X, Y, eff, cmap=cmap, norm=TwoSlopeNorm(0, -15, 45), shading="auto")
        cs = ax.contour(X, Y, eff, levels=[0], colors="#0b0b0b", linewidths=1.0)
        ax.clabel(cs, fmt="0 ms", fontsize=8)
        ax.add_patch(plt.Rectangle((0, 0), W, D, fill=False, ec="#52514e", lw=1))
        marks = [(A, "Amp")] + [(np.array(v["pos"]), "Unamp") for k, v in cfg["sources"].items()
                                   if not k.startswith("_") and k not in (bp.AMP, "B_L", "B_R")] + [(BL, "B_L"), (BR, "B_R")]
        for S, lab in marks:
            ax.plot(*S[:2], marker="s", ms=8, mfc="#0b0b0b", mec="#fcfcfb", mew=2)
            ax.annotate(lab, S[:2], xytext=(0, 8), textcoords="offset points", ha="center", fontsize=9)
        for k in bp.receiver_names(cfg):
            R = cfg["receivers"][k]
            ax.plot(R[0], R[1], "o", ms=8, mfc="#fcfcfb", mec="#0b0b0b", mew=1.5)
            ax.annotate(k, R[:2], xytext=(0, -14), textcoords="offset points", ha="center", fontsize=9)
        note = "" if d >= 0 else "\n(물리적 실현 불가: 무대 음을 늦춘 자극에서만 성립)"
        ax.set_title(f"명목 ITDG {itdg} ms (중앙 기준){note}", fontsize=10, color="#0b0b0b")
        ax.set_aspect("equal")
        ax.set_xlim(0, W); ax.set_ylim(0, D)
        ax.set_xlabel("x [m]", color="#52514e")
        ax.tick_params(colors="#52514e", labelsize=8)
        for sp in ax.spines.values():
            sp.set_visible(False)
    axes[0].set_ylabel("y [m]  (무대 ↑)", color="#52514e")
    cb = fig.colorbar(im, ax=axes, shrink=0.8, pad=0.02)
    cb.set_label("실효 ITDG [ms]  (가까운 PA − 확성 음원 직접음, 음수 = PA 선행)", color="#52514e")
    cb.outline.set_visible(False)
    fig.suptitle("좌석별 실효 ITDG — 직접음 기하 계산 (직육면체 임시 모델)", fontsize=11, color="#0b0b0b")
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main(*(sys.argv[1:] or ["config.json"]))
