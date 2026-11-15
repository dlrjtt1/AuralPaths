// Loads a config into the page (headless Chromium) and writes what the page computed for every path:
//   node tests/page_dump.js <folder with index.html> <config.json> <out.json>
// out: { params (the worker message: geometry, materials, air, order, rays, ...), paths: [{ key, src, rec, dir, seedIndex, hist }] }
// Used by validation/check_engine_js.py (Python bridge engine_js.py against the page).
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [dir, cfg, out] = process.argv.slice(2);
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1400, height: 1000 } }); const errs = [];
  p.on('pageerror', (e) => errs.push(e.message));
  await p.goto('file://' + dir + '/index.html');
  const idle = async (n) => { for (let i = 0; i < n; i++) { await p.waitForTimeout(500); if (await p.evaluate(() => document.getElementById('busy').hidden)) return true; } return false; };
  await idle(240);
  await p.setInputFiles('#fCfg', cfg);
  await p.waitForTimeout(1500);
  if (!(await idle(1200))) { console.error('page did not finish'); process.exit(2); }
  const res = await p.evaluate(() => {
    const M = HALL.mesh, geom = isMesh() ? { mesh: { text: M.text, groups: M.groups, default: M.def || 'wall', axes: M.axes, rot: M.rot, shift: M.shift, voxel: GM.vox.h, seed: GM.seed } }
      : { plan: HALL.geom.plan, floor: HALL.geom.floor, ceil: HALL.geom.ceil, stageY: HALL.dims[1] - HALL.stage };
    const params = { geom, mats: workerMats(), air: D.air, c: D.c, order: isMesh() ? meshOrder() : HALL.order, rays: HALL.rays, tWin: Math.max(0.16, DISCRETE_MS / 1000), spec: isMesh() ? SPEC : null,
      diff: !isMesh() && !!HALL.diff, diffRefl: HALL.diffRefl | 0, diffOrder: HALL.diffOrder | 0, bands: D.praBands, seat: seatDipParams(), fs: D.fs, HN: ENG.HN, HB: ENG.HB };
    const paths = Object.keys(GC).map((key) => { const [sid, oid] = key.split('|'), o = OBJ.find((x) => String(x.id) === oid), raw = GC[key];
      return { key, src: raw.pos, rec: raw.seat, dir: o.dir && (o.dir.table || (o.kind === 'pa' && o.dir.cov > 0)) ? o.dir : null, kind: o.kind, seedIndex: pathIndex(o), hist: geomHist(o, raw).hist.map((a) => Array.from(a)) }; });
    return { params, paths };
  });
  fs.writeFileSync(out, JSON.stringify(res));
  console.log(JSON.stringify({ paths: res.paths.length, errors: errs.length, first: errs[0] || '', rays: res.params.rays, mesh: !!res.params.geom.mesh }));
  await b.close();
})();
