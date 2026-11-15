// Loads a config into the page (headless Chromium), waits for the BRIRs and saves the page's SOFA export:
//   node tests/page_export_sofa.js <folder with index.html> <config.json> <out.sofa> [<h5wasm.js>] [<brirs.json>]
// The page loads h5wasm from jsDelivr for the export; with <h5wasm.js> (dist/iife/h5wasm.js of the npm package
// h5wasm 0.10.3) that request is answered from the local file, for machines without access to the CDN.
// <brirs.json>: also writes the page's BRIR arrays { "<seat>|<source>": [[left], [right]] } for comparison.
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [dir, cfg, out, h5, dump] = process.argv.slice(2);
  const b = await chromium.launch(); const ctx = await b.newContext({ acceptDownloads: true, viewport: { width: 1400, height: 1000 } }); const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', (e) => errs.push(e.message));
  if (h5) await p.route('**/h5wasm*', (r) => r.fulfill({ contentType: 'application/javascript', body: fs.readFileSync(h5) }));
  await p.goto('file://' + dir + '/index.html');
  const idle = async (n) => { for (let i = 0; i < n; i++) { await p.waitForTimeout(500); if (await p.evaluate(() => document.getElementById('busy').hidden)) return true; } return false; };
  await idle(240); await p.setInputFiles('#fCfg', cfg); await p.waitForTimeout(1500);
  if (!(await idle(1200))) { console.error('page did not finish'); process.exit(2); }
  let ready = false;
  for (let i = 0; i < 600 && !ready; i++) { ready = await p.evaluate(() => SEATS().every((s) => sourcesAll().every((o) => BR[s.id + '|' + o.id]))); if (!ready) await p.waitForTimeout(500); }
  if (!ready) { console.error('BRIRs not ready'); process.exit(2); }
  const [dl] = await Promise.all([p.waitForEvent('download', { timeout: 120000 }), p.evaluate(() => exportSofa())]);
  await dl.saveAs(out);
  if (dump) fs.writeFileSync(dump, JSON.stringify(await p.evaluate(() => Object.fromEntries(Object.entries(BR).map(([k, v]) => [k, [Array.from(v[0]), Array.from(v[1])]])))));
  console.log(JSON.stringify({ file: dl.suggestedFilename(), note: await p.evaluate(() => document.getElementById('posNote').textContent), errors: errs.length, first: errs[0] || '' }));
  await b.close();
})();
