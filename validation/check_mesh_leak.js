// A closed 3D model must not lose rays (engine_geom.js buildMesh + rays).
//
//     node validation/check_mesh_leak.js [--json] [model.obj ...]          (from the repository folder)
//
// Built-in model: a raked hall 14 x 20 m, 8 m high, with 24 steps of 0.8 m tread and 6 cm riser (written as an OBJ of
// quads, y up). The risers are narrower than the surface band of the voxel grid (5 - 10 cm voxels), which is the case
// that buildMesh got wrong until 2026-11-18: faces with no room voxel at 2.5 voxels on either side were dropped as
// "hidden", although they bound the room, and rays left through the holes (BRAS CR3 at 6.5 cm voxels: 285 of 2598
// faces, 8.1 m2, 8 - 10 % of the rays lost; DUS and TCB of the Fratoni data set: 17 - 24 %).
// Checks: no face dropped, rays lost <= 0.1 % (found no surface, entered a space the room fill did not reach, or moved
// behind the faces), volume within 2 % of the exact value. Further OBJ files given on the command line (not in the
// repository: BRAS CR3 / CR4 are CC BY-SA) are checked for the lost rays only, from the model centre.
//
// Result on 2026-11-18 (20 000 rays, 3 seeds x 3 source positions, voxel 5 / 6.5 / 10 cm):
//   steps model: 0 faces dropped, 24 narrow faces kept, rays lost 0 %, volume within 0.6 % of 1989.1 m3
//   before the fix (6.5 cm): 24 faces dropped, 2.5 % of the rays lost
const fs = require("fs"), path = require("path");
const GEOM = eval(fs.readFileSync(path.join(__dirname, "..", "engine_geom.js"), "utf8") + ";GEOM");
const W = 14, D = 20, H = 8, NS = 24, TR = 0.8, RI = 0.06, Y0 = 0.4;      // steps start 0.4 m from the front wall
function stepsObj() {
  const V = [], F = [], q = (a, b, c, d) => { const k = V.length; V.push(a, b, c, d); F.push([k + 1, k + 2, k + 3, k + 4]); };
  const P = (x, depth, height) => [x, height, -depth];                  // y up: x, height, -depth
  // floor: flat front part, then treads and risers
  q(P(0, 0, 0), P(W, 0, 0), P(W, Y0, 0), P(0, Y0, 0));
  let y = Y0, z = 0; const cols = [[0, Y0, 0]];
  for (let i = 0; i < NS; i++) { q(P(0, y, z), P(W, y, z), P(W, y, z + RI), P(0, y, z + RI)); z += RI; const y1 = i === NS - 1 ? D : y + TR; q(P(0, y, z), P(W, y, z), P(W, y1, z), P(0, y1, z)); cols.push([y, y1, z]); y = y1; }
  for (const [a, b, zz] of cols) { q(P(0, a, zz), P(0, b, zz), P(0, b, H), P(0, a, H)); q(P(W, a, zz), P(W, b, zz), P(W, b, H), P(W, a, H)); }   // side walls, one strip per step
  q(P(0, 0, 0), P(W, 0, 0), P(W, 0, H), P(0, 0, H)); q(P(0, D, z), P(W, D, z), P(W, D, H), P(0, D, H)); q(P(0, 0, H), P(W, 0, H), P(W, D, H), P(0, D, H));
  let vol = W * H * D; for (const [a, b, zz] of cols) vol -= W * (b - a) * zz;
  return { text: V.map((v) => "v " + v.join(" ")).join("\n") + "\n" + F.map((f) => "f " + f.join(" ")).join("\n") + "\n", vol };
}
const mats = { wall: { R: new Array(8).fill(Math.sqrt(0.8)), s: 0.3 } }, air = new Array(8).fill(0), N = 20000;
const out = { lost_max_pct: 0, dropped_max: 0, volume_err_max_pct: 0, narrow_min: 1e9 }, lines = [];
const M = stepsObj();
for (const voxel of [0.05, 0.065, 0.1]) {
  const G = GEOM.buildMesh({ obj: GEOM.loadObj(M.text), groups: {}, default: "wall", axes: "y-up", voxel }, [W / 2, D / 2, H / 2]);
  let lost = 0, tot = 0;
  for (const src of [[W / 2, D / 2, H / 2], [1.0, 1.5, 1.5], [W - 1, D - 1, 3.5]]) for (const seed of [1, 2, 3]) { const R = GEOM.rays(G, src, [[W / 2, 12, 2.5]], { n: N, seed }, mats, air); lost += R.escaped + R.leaked; tot += N; }
  const ev = 100 * Math.abs(G.V / M.vol - 1);
  out.lost_max_pct = Math.max(out.lost_max_pct, 100 * lost / tot); out.dropped_max = Math.max(out.dropped_max, G.nDropped); out.volume_err_max_pct = Math.max(out.volume_err_max_pct, ev); out.narrow_min = Math.min(out.narrow_min, G.nNarrow);
  lines.push(`steps model, voxel ${(voxel * 100).toFixed(1)} cm: ${G.nFaces} faces, ${G.nNarrow} narrow kept, ${G.nDropped} dropped, rays lost ${(100 * lost / tot).toFixed(3)} %, volume ${G.V.toFixed(1)} m3 (${G.volFrom}; exact ${M.vol.toFixed(1)}, ${ev.toFixed(2)} % off)`);
}
for (const f of process.argv.slice(2).filter((a) => a !== "--json")) {
  const obj = GEOM.loadObj(fs.readFileSync(f, "utf8")), lo = [0, 1, 2].map((k) => Math.min(...obj.V.map((v) => v[k]))), hi = [0, 1, 2].map((k) => Math.max(...obj.V.map((v) => v[k])));
  const c = [(lo[0] + hi[0]) / 2, -(lo[2] + hi[2]) / 2, (lo[1] + hi[1]) / 2], G = GEOM.buildMesh({ obj, groups: {}, default: "wall", axes: "y-up" }, c); let lost = 0, tot = 0;
  for (const seed of [1, 2, 3]) { const R = GEOM.rays(G, c, [c], { n: N, seed }, mats, air); lost += R.escaped + R.leaked; tot += N; }
  lines.push(`${path.basename(f)}: ${G.nFaces} faces, ${G.nNarrow} narrow kept, ${G.nDropped} dropped, voxel ${(G.h * 100).toFixed(1)} cm, volume ${G.V.toFixed(0)} m3, rays lost ${(100 * lost / tot).toFixed(3)} %`);
}
if (process.argv.includes("--json")) console.log(JSON.stringify(out)); else console.log(lines.join("\n"));
