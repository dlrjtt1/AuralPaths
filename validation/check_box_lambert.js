// Browser ray tracer (engine_geom.js) on the tiled shoebox of check_mesh_box.py (12 x 9 x 7 m as OBJ of 1 m tiles,
// alpha 0.2 everywhere, no air absorption): T30 against the prediction from the tracer's own free paths.
//
//     node validation/check_box_lambert.js            (from the repository folder)
//
// Prediction: with free path lengths of mean m and relative variance g2 = var / m^2, the number of reflections in time
// t is about normal with mean c t / m and variance c t g2 / m (central limit theorem), so the mean ray energy decays as
// E[(1 - a)^N] = exp((c t / m) (ln(1 - a) + g2 / 2 ln^2(1 - a))) and
//     T = -13.82 m / (c (ln(1 - a) + g2 / 2 ln^2(1 - a)))
// (derived here; the g2 term makes the decay slower than Eyring's -13.82 (4V/S) / (c ln(1 - a))).
//
// Result on 2026-11-06 (20 000 rays, three receivers averaged, no air absorption):
//   s = 1.0: mean free path 5.94 m (4V/S 5.93 m), g2 0.35, predicted 1.11 s, traced 1.12 s; Eyring 1.07 s
//   s = 0.5: mean free path 6.36 m, g2 0.27, predicted 1.18 s, traced 1.16 s (the field is not diffuse)
// pyroomacoustics on the same box (check_mesh_box.py 1.0) gave 1.03 s with energy_thres 1e-9, below Eyring: that
// setting is also an absolute floor for its scattered ("diffuse rain") contributions and dropped them from about
// 0.5 s on. With energy_thres 1e-20 (brir_proto.RT_ENERGY_THRES) Python gives the browser's values (s 0.5: 1.16 /
// 1.14 / 1.10 s at 125 / 500 / 2000 Hz with air absorption, both engines).
const fs = require("fs"), path = require("path");
const GEOM = eval(fs.readFileSync(path.join(__dirname, "..", "engine_geom.js"), "utf8") + ";GEOM");
const X = 12, Y = 7, Z = 9, V = [], F = [];            // OBJ y-up: x, height, depth (as check_mesh_box.py)
function quad(p0, u, v, nu, nv) {
  for (let i = 0; i < nu; i++) for (let j = 0; j < nv; j++) {
    const a = [0, 1, 2].map((k) => p0[k] + u[k] * i / nu + v[k] * j / nv), b = a.map((x, k) => x + u[k] / nu), c = b.map((x, k) => x + v[k] / nv), d = a.map((x, k) => x + v[k] / nv);
    const k0 = V.length; V.push(a, b, c, d); F.push([k0 + 1, k0 + 2, k0 + 3, k0 + 4]);
  }
}
quad([0, 0, 0], [X, 0, 0], [0, 0, Z], 12, 9); quad([0, Y, 0], [X, 0, 0], [0, 0, Z], 12, 9);
quad([0, 0, 0], [X, 0, 0], [0, Y, 0], 12, 7); quad([0, 0, Z], [X, 0, 0], [0, Y, 0], 12, 7);
quad([0, 0, 0], [0, 0, Z], [0, Y, 0], 9, 7); quad([X, 0, 0], [0, 0, Z], [0, Y, 0], 9, 7);
const objText = "g wall\n" + V.map((p) => `v ${p.join(" ")}`).join("\n") + "\n" + F.map((f) => "f " + f.join(" ")).join("\n") + "\n";
const src = [3, -3, 1.5], recs = [[8, -5, 1.2], [6, -2, 2.0], [10, -7, 3.0]], a = 0.2, c = 343.5, bin = 0.001;
const G = GEOM.buildMesh({ obj: GEOM.loadObj(objText), groups: { wall: "w" }, voxel: 0.05 }, src);
const la = Math.log(1 - a), vol = X * Y * Z, area = 2 * (X * Y + X * Z + Y * Z);
function t30(h) { // Schroeder integral, line fit -5 ... -35 dB
  const n = h.length, E = new Float64Array(n); let s = 0; for (let i = n - 1; i >= 0; i--) { s += h[i]; E[i] = s; }
  const db = Array.from(E, (v) => 10 * Math.log10(v / E[0] + 1e-30)); const pts = [];
  for (let i = 0; i < n; i++) if (db[i] <= -5 && db[i] >= -35) pts.push([i * bin, db[i]]);
  const mx = pts.reduce((q, p) => q + p[0], 0) / pts.length, my = pts.reduce((q, p) => q + p[1], 0) / pts.length;
  const k = pts.reduce((q, p) => q + (p[0] - mx) * (p[1] - my), 0) / pts.reduce((q, p) => q + (p[0] - mx) ** 2, 0);
  return -60 / k;
}
// free-path statistics: a separate tracer run that records segment lengths after the first reflection
function freePaths(s, n) {
  let st = 12345; const rnd = () => { st ^= st << 13; st >>>= 0; st ^= st >>> 17; st ^= st << 5; st >>>= 0; return st / 4294967296; };
  let sum = 0, sq = 0, cnt = 0;
  for (let k = 0; k < n; k++) {
    const z = 1 - 2 * rnd(), ph = 2 * Math.PI * rnd(), r = Math.sqrt(1 - z * z); let d = [r * Math.cos(ph), r * Math.sin(ph), z], o = src.slice(), last = -1;
    for (let b = 0; b < 60; b++) {
      let best = Infinity, bi = -1;
      for (let i = 0; i < G.S.length; i++) { if (i === last) continue; const S = G.S[i], den = S.n[0] * d[0] + S.n[1] * d[1] + S.n[2] * d[2]; if (den >= -1e-12) continue;
        const t = (S.d - (S.n[0] * o[0] + S.n[1] * o[1] + S.n[2] * o[2])) / den; if (t > 1e-9 && t < best) { const p = [o[0] + t * d[0], o[1] + t * d[1], o[2] + t * d[2]];
          const ax = S.u, ay = S.v, P = S.p2; let inP = false; for (let q = 0, w = P.length - 1; q < P.length; w = q++) { if ((P[q][1] > p[ay]) !== (P[w][1] > p[ay]) && p[ax] < (P[w][0] - P[q][0]) * (p[ay] - P[q][1]) / (P[w][1] - P[q][1]) + P[q][0]) inP = !inP; }
          if (inP) { best = t; bi = i; } } }
      if (bi < 0) break;
      if (b > 0) { sum += best; sq += best * best; cnt++; }
      o = o.map((x, q) => x + best * d[q]); const nn = G.S[bi].n;
      // same direction rule as engine_geom.js rays() for mesh halls: normalised mix s * Lambert + (1 - s) * specular
      const u1 = rnd(), u2 = rnd(), sr = Math.sqrt(u1), phi = 2 * Math.PI * u2, t1 = Math.abs(nn[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0];
      let ex = [nn[1] * t1[2] - nn[2] * t1[1], nn[2] * t1[0] - nn[0] * t1[2], nn[0] * t1[1] - nn[1] * t1[0]]; const el = Math.hypot(...ex); ex = ex.map((v) => v / el);
      const ey = [nn[1] * ex[2] - nn[2] * ex[1], nn[2] * ex[0] - nn[0] * ex[2], nn[0] * ex[1] - nn[1] * ex[0]], a3 = Math.sqrt(1 - u1);
      const lam = [0, 1, 2].map((q) => sr * Math.cos(phi) * ex[q] + sr * Math.sin(phi) * ey[q] + a3 * nn[q]);
      const dn = 2 * (d[0] * nn[0] + d[1] * nn[1] + d[2] * nn[2]), spec = d.map((v, q) => v - dn * nn[q]);
      const mix = [0, 1, 2].map((q) => s * lam[q] + (1 - s) * spec[q]), ml = Math.hypot(...mix); d = mix.map((v) => v / ml); last = bi;
    }
  }
  const m = sum / cnt; return { m, g2: sq / cnt / (m * m) - 1 };
}
for (const s of [1.0, 0.5]) {
  const R = GEOM.rays(G, src, recs, { n: 20000, c, tMax: 3, bin, seed: 3 }, { w: { R: [Math.sqrt(1 - a)], s } }, [0]);
  const T = R.H.map((h) => t30(h[0])).reduce((x, y) => x + y, 0) / recs.length, { m, g2 } = freePaths(s, 1500);
  console.log(`s = ${s}: mean free path ${m.toFixed(2)} m (4V/S ${(4 * vol / area).toFixed(2)} m), g2 ${g2.toFixed(2)}, ` +
    `predicted ${(-13.82 * m / (c * (la + g2 / 2 * la * la))).toFixed(2)} s, traced ${T.toFixed(2)} s; Eyring ${(-13.82 * 4 * vol / (c * area * la)).toFixed(2)} s`);
}
