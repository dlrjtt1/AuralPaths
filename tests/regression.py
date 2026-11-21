"""
Regression checks: runs the checks that need no external data and compares their results with tests/baseline.json.
Run before every commit, and automatically on GitHub (.github/workflows/regression.yml).

    python tests/regression.py                 # all checks (about 2 minutes; needs node, pyroomacoustics)
    python tests/regression.py --quick         # skip the slow ones (calibration, Python ray tracing of the calibration)
    python tests/regression.py --only page,diffraction
    python tests/regression.py --update        # write the current values as the new baseline (after a deliberate
                                               # model change; say why in the commit message)

Checks (name: what it guards):
  page         index.html is exactly viewer_template.html + engine_geom.js (tools/build_page.py)
  page_refresh a refresh while the BRIRs of a 3D model are recomputed shows dashes, no error and no stale values
               (needs playwright; skipped without it)
  page_load    the page opens in Chromium without script errors and finishes its first computation (needs playwright;
               skipped if it is missing)
  specular     Python and browser image sources with specular factors agree (validation/check_specular_pyjs.py)
  diffraction  Python and browser UTD edge diffraction agree (validation/check_diffraction_pyjs.py)
  diffraction_plate  the same on a free-standing partition on a floor (thin-plate edges, diffraction combined with
               floor reflections; the BRAS RS5 geometry, no measured data needed)
  diffraction_order2  the same for second-order diffraction over a thick body on a floor (BRAS RS6 geometry)
  diffraction_rs  the same on the geometries of the BRAS reference scenes RS1 - RS4, RS6, RS7 (first order, as
               validation/bras_rs.py computes them; validation/check_rs_pyjs.py, no measured data needed)
  seatdip      the seat-dip transfer function (2-D BEM over the rows), Python vs browser, every pair of the fan hall
  rays_split   the browser ray tracer gives the same histogram whether rays are traced in one run or split in parts
               (worker pool)
  mesh_leak    a closed 3D model with risers narrower than the voxel band loses no rays, drops no face and has the
               right volume; the outer skin of a double-walled box is not counted in the area
               (validation/check_mesh_leak.js)
  box_js       browser ray tracer T30 on a tiled shoebox, against its baseline and its free-path prediction
               (validation/check_box_lambert.js)
  box_py       Python (pyroomacoustics) ray tracer T30 in a shoebox, against its baseline (catches changes of the
               energy floor brir_proto.RT_ENERGY_THRES and of the pyroomacoustics version)
  rays_energy  ray-traced energy of both tracers in a scattering shoebox against exact image sources: scattering must
               not create energy (validation/check_rays_energy.py; pyroomacoustics' diffuse rain is switched off)
  engine_js    engine_js.py (the browser engine called from Python) gives the page's own histograms for the fan hall,
               and reads the config as the page does (validation/check_engine_js.py; needs playwright, else skipped)
  engine_js_dir  measured directivity (polar CSV, SOFA balloon) gives the same band amplitudes in the browser engine
               as in Python when passed through engine_js.py (validation/check_engine_js_dir.py)
  calibrate    calibrate.py reaches the synthetic example T30 within 2 % in at most 6 iterations
Literature checks against measured halls (BRAS, Fratoni) need the datasets and are not run here; see validation/.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BASE = os.path.join(ROOT, "tests", "baseline.json")
PY = sys.executable


def run(cmd, timeout=900, **kw):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout, **kw)
    if r.returncode:
        raise RuntimeError((r.stdout + r.stderr)[-2000:])
    return r.stdout


def num(pattern, text):
    m = re.search(pattern, text)
    if not m:
        raise RuntimeError(f"pattern {pattern!r} not found in:\n{text[-1500:]}")
    return float(m.group(1))


# ---- checks: each returns {metric: value}
def c_page():
    r = subprocess.run([PY, "tools/build_page.py", "--check"], cwd=ROOT, capture_output=True, text=True)
    return {"up_to_date": 1.0 if r.returncode == 0 else 0.0}


def c_page_refresh():
    js = r"""
const { chromium } = require('playwright'); const fs = require('fs'), os = require('os'), path = require('path');
(async () => {
  const obj = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'ap-')), 'box.obj');   // 20 x 8 x 12 m box, y up
  const V = [[0,0,0],[20,0,0],[20,0,-12],[0,0,-12],[0,8,0],[20,8,0],[20,8,-12],[0,8,-12]];
  fs.writeFileSync(obj, V.map((v) => 'v ' + v.join(' ')).join('\n') + '\ng floor\nf 1 2 3 4\ng wall\nf 5 8 7 6\nf 1 5 6 2\nf 2 6 7 3\nf 3 7 8 4\nf 4 8 5 1\n');
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1300, height: 1300 } }); const errs = [];
  p.on('pageerror', (e) => errs.push(e.message));
  await p.goto('file://' + process.argv[1] + '/index.html');
  const idle = async () => { for (let i = 0; i < 600; i++) { await p.waitForTimeout(500); if (await p.evaluate(() => document.getElementById('busy').hidden)) return true; } return false; };
  await idle(); await p.setInputFiles('#fObj', obj); await p.waitForTimeout(2000); await idle(); await p.evaluate(() => { HALL.rays = 10000; }); errs.length = 0;
  const t30 = () => p.evaluate(() => document.getElementById('kvMet').innerText.match(/T30\s*([^\s]+)/)?.[1] ?? '');
  await p.evaluate(() => { work(rebuildAll); setTimeout(() => dispatchEvent(new Event('resize')), 60); }); await idle();
  const before = await t30(); errs.length = 0;
  await p.evaluate(() => { for (const k in HALL.mats) HALL.mats[k].alpha = HALL.mats[k].alpha.map((a) => Math.min(0.9, a * 2)); work(rebuildAll); setTimeout(() => dispatchEvent(new Event('resize')), 60); });
  await p.waitForTimeout(400); const during = await t30(); await idle(); const after = await t30();
  console.log(JSON.stringify({ errors: errs.length, first: errs[0] || '', during, before, after }));
  await b.close();
})();"""
    try:
        out = run(["node", "-e", js, ROOT], timeout=600)
    except RuntimeError as e:
        if "Cannot find module 'playwright'" in str(e) or "Executable doesn't exist" in str(e):
            return None
        raise
    o = json.loads(out.strip().splitlines()[-1])
    if o["errors"]:
        print(f"    first script error: {o['first']}")
    print(f"    T30 before {o['before']}, while computing {o['during']}, after {o['after']}")
    return {"script_errors": float(o["errors"]), "dashes_while_computing": float(o["during"].startswith("\u2014")),
            "values_changed": float(o["before"] != o["after"])}


def c_page_load():
    js = r"""
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1400, height: 1000 } }); const errs = [];
  p.on('pageerror', (e) => errs.push(e.message));
  await p.goto('file://' + process.argv[1] + '/index.html');
  let done = false;
  for (let i = 0; i < 120 && !done; i++) { await p.waitForTimeout(500); done = await p.evaluate(() => { const b = document.getElementById('busy'); return !!b && b.hidden; }); }
  const guide = await p.evaluate(() => !!document.getElementById('guideOverlay'));
  console.log(JSON.stringify({ errors: errs.length, done: done ? 1 : 0, guide: guide ? 1 : 0, first: errs[0] || '' }));
  await b.close();
})();"""
    try:
        out = run(["node", "-e", js, ROOT], timeout=180)
    except RuntimeError as e:
        if "Cannot find module 'playwright'" in str(e) or "Executable doesn't exist" in str(e):
            return None
        raise
    o = json.loads(out.strip().splitlines()[-1])
    if o["errors"]:
        print(f"    first script error: {o['first']}")
    return {"script_errors": float(o["errors"]), "first_computation_done": float(o["done"]), "guide_present": float(o["guide"])}


def c_specular():
    out = run([PY, "validation/check_specular_pyjs.py", "examples/fan_hall_config.json", "3"])
    return {"images": num(r"(\d+) Python images", out), "max_rel_energy_diff": num(r"difference ([0-9.e+-]+)", out)}


def c_diffraction():
    out = run([PY, "validation/check_diffraction_pyjs.py", "examples/fan_hall_config.json"])
    return {"arrivals": num(r"(\d+) diffracted arrivals", out), "max_energy_diff": num(r"largest difference ([0-9.e+-]+)", out)}


def c_diffraction_plate():
    out = run([PY, "validation/check_diffraction_pyjs.py", "--rs5"])
    return {"arrivals": num(r"(\d+) diffracted arrivals", out), "thin_edges": num(r"\((\d+) thin\)", out),
            "max_energy_diff": num(r"largest difference ([0-9.e+-]+)", out)}


def c_diffraction_order2():
    out = run([PY, "validation/check_diffraction_pyjs.py", "--rs6"])
    return {"arrivals": num(r"(\d+) diffracted arrivals", out),
            "max_energy_diff": num(r"largest difference ([0-9.e+-]+)", out)}


def c_diffraction_rs():
    out = run([PY, "validation/check_rs_pyjs.py"])
    return {"arrivals": num(r"all scenes: (\d+) diffracted arrivals", out),
            "max_rel_energy_diff": num(r"all scenes: .*\(relative ([0-9.e+-]+)\)", out)}


def c_seatdip():
    out = run([PY, "validation/check_seatdip_pyjs.py", "examples/fan_hall_config.json"], timeout=900)
    return {"pairs": num(r"(\d+) of \d+ pairs with a seat dip", out),
            "max_T_diff": num(r"largest \|T_py - T_js\| ([0-9.e+-]+)", out)}


def c_rays_split():
    js = r"""
const fs = require('fs'); const GEOM = eval(fs.readFileSync('engine_geom.js', 'utf8') + ';GEOM');
const cfg = JSON.parse(fs.readFileSync('examples/fan_hall_config.json', 'utf8')), g = cfg.geometry;
const G = GEOM.build({ plan: g.plan, floor: g.floor, ceil: g.ceiling, stageY: cfg.room.dims_m[1] - (cfg.room.stage_depth_m || 0) });
const bands = [125, 250, 500, 1000, 2000, 4000, 8000], mats = {};
for (const [k, v] of Object.entries(g.materials)) mats[k] = { R: bands.map((_, i) => Math.sqrt(1 - v.alpha[Math.min(i, v.alpha.length - 1)])), s: v.s || 0.1 };
const src = cfg.sources.S_amp.pos, recs = Object.values(cfg.receivers).slice(0, 2), air = bands.map(() => 0);
const o = { n: 3000, tMax: 1.0, seed: 7 };
const full = GEOM.rays(G, src, recs, o, mats, air).H;
const a = GEOM.rays(G, src, recs, Object.assign({}, o, { k0: 0, k1: 1300 }), mats, air).H;
const b = GEOM.rays(G, src, recs, Object.assign({}, o, { k0: 1300, k1: 3000 }), mats, air).H;
let worst = 0, tot = 0;
full.forEach((R, m) => R.forEach((h, k) => h.forEach((v, i) => { const s = a[m][k][i] + b[m][k][i]; tot += v; worst = Math.max(worst, Math.abs(s - v)); })));
console.log(JSON.stringify({ worst, tot }));"""
    o = json.loads(run(["node", "-e", js]).strip())
    return {"max_abs_diff_rel_total": o["worst"] / max(o["tot"], 1e-30), "total_energy": o["tot"]}


def c_box_js():
    out = run(["node", "validation/check_box_lambert.js"])
    r = {}
    for s, key in (("1", "s1"), ("0.5", "s05")):
        m = re.search(rf"s = {re.escape(s)}: .*?predicted ([0-9.]+) s, traced ([0-9.]+) s", out)
        if not m:
            raise RuntimeError(out[-1500:])
        r[f"T30_{key}"], r[f"traced_vs_predicted_{key}"] = float(m.group(2)), float(m.group(2)) / float(m.group(1)) - 1
    return r


def c_mesh_leak():
    return json.loads(run(["node", "validation/check_mesh_leak.js", "--json"], timeout=600).strip().splitlines()[-1])


def c_box_py():
    code = r"""
import sys; sys.path.insert(0, '.'); import numpy as np, pyroomacoustics as pra, brir_proto as bp
L = np.array([12., 9., 7.]); out = {}
for a, s in ((0.15, 0.7), (0.3, 0.1)):
    room = pra.ShoeBox(L, fs=16000, materials=pra.Material(a, s), max_order=0, ray_tracing=True, air_absorption=False)
    room.set_ray_tracing(n_rays=10000, receiver_radius=0.5, hist_bin_size=0.004, time_thres=3, energy_thres=bp.RT_ENERGY_THRES)
    room.add_source([3, 3, 1.5]); room.add_microphone([8, 5, 1.2]); room.ray_tracing()
    e = np.asarray(room.rt_histograms[0][0][0])[0]; edc = 10 * np.log10(np.cumsum(e[::-1])[::-1] / e.sum() + 1e-30)
    t = (np.arange(len(e)) + 0.5) * 0.004; sel = (edc <= -5) & (edc >= -35)
    out[f"T30_a{a}_s{s}"] = -60 / np.polyfit(t[sel], edc[sel], 1)[0]
print(__import__('json').dumps(out))"""
    return json.loads(run([PY, "-c", code]).strip().splitlines()[-1])


def c_rays_energy():
    return json.loads(run([PY, "validation/check_rays_energy.py", "--json"]).strip().splitlines()[-1])


def c_engine_js():
    try:
        o = json.loads(run([PY, "validation/check_engine_js.py", "examples/fan_hall_config.json", "--json"]).strip().splitlines()[-1])
    except RuntimeError as e:
        if "Cannot find module 'playwright'" in str(e) or "Executable doesn't exist" in str(e):
            return None
        raise
    return {"max_rel_hist_diff": o["max_rel_hist_diff"], "param_diffs": float(len(o["param_diffs"])),
            "max_material_diff": o["max_material_diff"], "paths": float(o["paths"])}


def c_engine_js_dir():
    o = json.loads(run([PY, "validation/check_engine_js_dir.py", "--json"]).strip().splitlines()[-1])
    return {"max_amp_diff_db": o["max_amp_diff_db"], "max_diffuse_diff_db": o["max_diffuse_diff_db"], "files": float(o["files"])}


def c_calibrate():
    with tempfile.TemporaryDirectory() as d:
        out = run([PY, "calibrate.py", "examples/fan_hall_config.json", "examples/calibration_measurements_example.csv",
                   "--out", os.path.join(d, "cal.json")], timeout=1200)
    its = re.findall(r"iteration (\d+): .*?\| error % ([^\n]+)", out)
    if not its:
        raise RuntimeError(out[-1500:])
    errs = [abs(float(x)) for x in its[-1][1].split(",")]
    return {"iterations": float(its[-1][0]), "max_abs_error_pct": max(errs)}


def c_sofa_positions():
    """SOFA directivity positions declared cartesian but holding azimuth / elevation / radius (Zenodo 10255555 style)
    are read as angles (azimuth clockwise, as the Aalto record states), in Python and on the page; real cartesian positions are left alone."""
    import warnings
    import numpy as np
    sys.path.insert(0, ROOT)
    import brir_proto as bp
    az, el = np.meshgrid(np.arange(0, 360, 10.), np.arange(-80, 91, 10.))
    ang = np.c_[az.ravel(), el.ravel(), np.ones(az.size)]
    ref = bp._sph_to_vec(ang, "spherical")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        py_bad = float(np.abs(bp._sph_to_vec(ang, "cartesian") - ref * [1, -1, 1]).max())   # clockwise azimuth
    py_cart = float(np.abs(bp._sph_to_vec(ref * 2.0, "cartesian") - ref).max())
    ring = np.c_[2 * np.cos(np.radians(np.arange(0, 360, 10.))), 2 * np.sin(np.radians(np.arange(0, 360, 10.))), np.full(36, 1.0)]
    py_ring = float(np.abs(bp._sph_to_vec(ring, "cartesian") - ring / np.linalg.norm(ring, axis=1, keepdims=True)).max())
    out = {"py_mislabelled_max_err": py_bad, "py_cartesian_max_err": py_cart, "py_ring_max_err": py_ring}
    js = r"""
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + process.argv[1] + '/index.html'); await p.waitForFunction(() => typeof sofaDirs === 'function');
  const o = await p.evaluate(() => {
    const ang = [], ref = [], d2 = Math.PI / 180;
    for (let el = -80; el <= 90; el += 10) for (let az = 0; az < 360; az += 10) { ang.push([az, el, 1]); ref.push([Math.cos(el * d2) * Math.cos(az * d2), Math.cos(el * d2) * Math.sin(az * d2), Math.sin(el * d2)]); }
    const err = (a, r) => Math.max(...a.map((c, i) => Math.max(...c.map((x, j) => Math.abs(x - r[i][j])))));
    const bad = sofaDirs(ang, 'cartesian'), cart = sofaDirs(ref.map((c) => c.map((x) => 2 * x)), 'cartesian');
    return { bad: err(bad.dirs, ref.map(([x, y, z]) => [x, -y, z])), fixed: bad.fixed ? 1 : 0, cart: err(cart.dirs, ref), cartFixed: cart.fixed ? 1 : 0 }; });
  console.log(JSON.stringify(o)); await b.close();
})();"""
    try:
        o = json.loads(run(["node", "-e", js, ROOT], timeout=120).strip().splitlines()[-1])
        out.update({"page_mislabelled_max_err": o["bad"], "page_mislabelled_flag": float(o["fixed"]),
                    "page_cartesian_max_err": o["cart"], "page_cartesian_flag": float(o["cartFixed"])})
    except RuntimeError as e:
        if not ("Cannot find module 'playwright'" in str(e) or "Executable doesn't exist" in str(e)):
            raise
    return out


CHECKS = {"page": c_page, "page_load": c_page_load, "page_refresh": c_page_refresh, "sofa_positions": c_sofa_positions, "specular": c_specular, "diffraction": c_diffraction,
          "diffraction_plate": c_diffraction_plate,
          "diffraction_order2": c_diffraction_order2, "diffraction_rs": c_diffraction_rs, "seatdip": c_seatdip,
          "rays_split": c_rays_split, "box_js": c_box_js, "mesh_leak": c_mesh_leak, "box_py": c_box_py, "rays_energy": c_rays_energy,
          "engine_js": c_engine_js, "engine_js_dir": c_engine_js_dir, "calibrate": c_calibrate}
SLOW = {"calibrate"}


def judge(name, metric, value, rule):
    """rule: {"max": x} | {"min": x} | {"value": x, "tol": t} (absolute) | {"value": x, "rtol": r} (relative)"""
    if "max" in rule and value > rule["max"]:
        return f"{value:.4g} > max {rule['max']:.4g}"
    if "min" in rule and value < rule["min"]:
        return f"{value:.4g} < min {rule['min']:.4g}"
    if "value" in rule:
        d = abs(value - rule["value"])
        lim = rule.get("tol", abs(rule["value"]) * rule.get("rtol", 0))
        if d > lim:
            return f"{value:.4g}, baseline {rule['value']:.4g} (limit +-{lim:.3g})"
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true"); ap.add_argument("--update", action="store_true")
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    base = json.load(open(BASE)) if os.path.exists(BASE) else {}
    names = a.only.split(",") if a.only else [n for n in CHECKS if not (a.quick and n in SLOW)]
    fails, skipped, results = [], [], {}
    for n in names:
        t = time.time()
        try:
            r = CHECKS[n]()
        except Exception as e:  # a crashed check is a failure
            fails.append(f"{n}: error\n{e}"); print(f"FAIL  {n}  (error)"); continue
        if r is None:
            skipped.append(n); print(f"skip  {n}  (dependency missing)"); continue
        results[n] = r
        bad = [] if a.update else [f"{m}: {msg}" for m, rule in base.get(n, {}).items() if m in r for msg in [judge(n, m, r[m], rule)] if msg]
        missing = [m for m in base.get(n, {}) if m not in r]
        bad += [f"{m}: not produced" for m in missing] if not a.update else []
        print(f"{'FAIL' if bad else 'ok  '}  {n}  ({time.time() - t:.0f} s)  " + ", ".join(f"{k}={v:.4g}" for k, v in r.items()))
        for b in bad:
            print(f"        {b}")
        if bad:
            fails.append(n)
    if a.update:
        for n, r in results.items():
            old = base.get(n, {})
            for m, v in r.items():
                rule = dict(old.get(m, {}))
                if "value" in rule or not rule:
                    rule["value"] = float(f"{v:.10g}")
                    rule.setdefault("rtol", 0.03)
                old[m] = rule
            base[n] = old
        json.dump(base, open(BASE, "w"), indent=1, sort_keys=True); print(f"baseline written: {BASE}")
        return 0
    print(f"\n{len(names) - len(fails) - len(skipped)} passed, {len(fails)} failed, {len(skipped)} skipped")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
