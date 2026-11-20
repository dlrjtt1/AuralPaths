// Loads a config into the page (headless Chromium), waits for the BRIRs and writes them as JSON:
//   node tests/page_brirs.js <folder with index.html> <config.json> <out.json> [HRIR set .sofa]
// out: { fs, brirs: { "<seat>|<source>": [[left], [right]] } }  (time zero = emission; no PA delay or gain)
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [dir, cfg, out, hrir] = process.argv.slice(2);   // hrir (optional): SOFA HRIR set loaded with the page's "HRIR set…" before the config
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1400, height: 1000 } }); const errs = [];
  p.on('pageerror', (e) => errs.push(e.message));
  // machines without access to the CDN: H5WASM=<dist/iife/h5wasm.js of the npm package h5wasm 0.10.3> answers the page's request for the SOFA reader
  if (process.env.H5WASM) await p.route('**/h5wasm*', (r) => r.fulfill({ contentType: 'application/javascript', body: fs.readFileSync(process.env.H5WASM) }));
  await p.goto('file://' + dir + '/index.html');
  const idle = async (n) => { for (let i = 0; i < n; i++) { await p.waitForTimeout(500); if (await p.evaluate(() => document.getElementById('busy').hidden)) return true; } return false; };
  await idle(240);
  if (hrir) { await p.setInputFiles('#fHrir', hrir); let ok = false; for (let i = 0; i < 240 && !ok; i++) { await p.waitForTimeout(500); ok = await p.evaluate(() => !!(S.hrir && S.hrir.name)); }
    if (!ok) { console.error('HRIR set not loaded: ' + (await p.evaluate(() => document.getElementById('hrirNote').textContent))); process.exit(2); } await idle(240); }
  await p.setInputFiles('#fCfg', cfg); await p.waitForTimeout(1500);
  if (!(await idle(2400))) { console.error('page did not finish'); process.exit(2); }
  let ready = false;
  for (let i = 0; i < 1200 && !ready; i++) { ready = await p.evaluate(() => SEATS().every((s) => sourcesAll().every((o) => BR[s.id + '|' + o.id]))); if (!ready) await p.waitForTimeout(500); }
  if (!ready) { console.error('BRIRs not ready: ' + (await p.evaluate(() => document.getElementById('posNote').textContent))); process.exit(2); }
  const res = await p.evaluate(() => ({ fs: D.fs, hrir: S.hrir ? S.hrir.name : 'KU100', mesh: !!HALL.mesh, lost: (typeof GM !== 'undefined' && GM && GM.lostPct != null) ? GM.lostPct : null, drawn: !!HALL.geom, rays: HALL.rays, order: HALL.order, dirs: Object.fromEntries(OBJ.filter((o) => o.kind !== 'seat').map((o) => [o.id, o.dir || null])),
    brirs: Object.fromEntries(Object.entries(BR).map(([k, v]) => [k, [Array.from(v[0]), Array.from(v[1])]])) }));
  fs.writeFileSync(out, JSON.stringify(res));
  console.log(JSON.stringify({ paths: Object.keys(res.brirs).length, drawn: res.drawn, mesh: res.mesh, hrir: res.hrir, rays: res.rays, order: res.order, dirs: res.dirs, errors: errs.length, first: errs[0] || '' }));
  await b.close();
})();
