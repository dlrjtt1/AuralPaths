// AuralPaths general-geometry engine (2.5D halls).
// Runs in a browser Web Worker and in Node (for validation). No DOM access.
//
// Geometry: plan outline polygon (x, y) + floor and ceiling profiles z(y).
//   The room is { (x, y, z) : (x, y) inside the outline, floor(y) <= z <= ceiling(y) }.
//   Equal consecutive y values in a profile make a vertical step (riser).
// Surfaces become planar polygons with inward normals and a material group:
//   "aud" (floor in the audience), "stage" (floor on the stage), "wall", "ceil".
//
// Acoustics (same conventions as pyroomacoustics):
//   amplitude reflection factor per band  R_b = sqrt(1 - alpha_b), air absorption exp(-a_b d / 2) on amplitude,
//   image-source amplitude  prod(R_b) / d.
// ISM: recursive images to a given order, path validated by back-tracing through each reflecting
//   polygon and checked for occlusion by every other surface (needed for non-convex halls).
// Ray tracing: N rays of power 4*pi/N, specular or Lambert-diffuse reflection with probability equal
//   to the scattering coefficient, energy (1 - alpha_b) per hit, receiver = sphere of radius r with
//   energy contribution e * chord / V_sphere (gives 1/d^2 for the direct sound, the ISM energy unit).

const GEOM = (() => {
  const EPS = 1e-9;

  // ---------- profiles
  function normProfile(pts, y0, y1) {
    let p = pts.map((q) => [+q[0], +q[1]]).filter((q) => Number.isFinite(q[0]) && Number.isFinite(q[1]));
    p.sort((a, b) => a[0] - b[0]);
    if (!p.length) return null;
    if (p[0][0] > y0 + 1e-6) p.unshift([y0, p[0][1]]);
    if (p[p.length - 1][0] < y1 - 1e-6) p.push([y1, p[p.length - 1][1]]);
    // clip to [y0, y1]
    const out = [];
    for (let i = 0; i < p.length; i++) {
      const [y, z] = p[i];
      if (y < y0 - 1e-9) { const n = p[i + 1]; if (n && n[0] > y0) out.push([y0, z + (n[1] - z) * (y0 - y) / (n[0] - y)]); continue; }
      if (y > y1 + 1e-9) { const q = p[i - 1]; if (q && q[0] < y1 && (!out.length || out[out.length - 1][0] < y1 - 1e-9)) out.push([y1, q[1] + (z - q[1]) * (y1 - q[0]) / (y - q[0])]); break; }
      out.push([y, z]);
    }
    // merge near-equal y into exact risers
    for (let i = 1; i < out.length; i++) if (Math.abs(out[i][0] - out[i - 1][0]) < 1e-6) out[i][0] = out[i - 1][0];
    return out;
  }
  // value at y; side = -1 left limit, +1 right limit (matters only at risers)
  function profAt(p, y, side = 1) {
    if (y <= p[0][0]) return p[0][1];
    if (y >= p[p.length - 1][0]) return p[p.length - 1][1];
    if (side > 0) { for (let i = p.length - 1; i >= 0; i--) if (p[i][0] <= y) { const n = p[i + 1]; return !n || n[0] === p[i][0] ? p[i][1] : p[i][1] + (n[1] - p[i][1]) * (y - p[i][0]) / (n[0] - p[i][0]); } }
    else { for (let i = 0; i < p.length; i++) if (p[i][0] >= y) { const q = p[i - 1]; return !q || q[0] === p[i][0] ? p[i][1] : q[1] + (p[i][1] - q[1]) * (y - q[0]) / (p[i][0] - q[0]); } }
    return p[p.length - 1][1];
  }

  // ---------- 2D helpers
  function area2(poly) { let a = 0; for (let i = 0; i < poly.length; i++) { const [x1, y1] = poly[i], [x2, y2] = poly[(i + 1) % poly.length]; a += x1 * y2 - x2 * y1; } return a / 2; }
  function ccw(poly) { return area2(poly) < 0 ? poly.slice().reverse() : poly.slice(); }
  function clipHalf(poly, keep) { // keep(p) -> signed value, keeps >= 0
    const out = [];
    for (let i = 0; i < poly.length; i++) {
      const a = poly[i], b = poly[(i + 1) % poly.length], fa = keep(a), fb = keep(b);
      if (fa >= 0) out.push(a);
      if ((fa >= 0) !== (fb >= 0)) { const t = fa / (fa - fb); out.push([a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])]); }
    }
    return out;
  }
  function stripPoly(poly, y0, y1) { return clipHalf(clipHalf(poly, (p) => p[1] - y0), (p) => y1 - p[1]); }
  function lineCrossX(poly, y) { // x intervals of the polygon on horizontal line y
    const xs = [];
    for (let i = 0; i < poly.length; i++) {
      const [x1, y1] = poly[i], [x2, y2] = poly[(i + 1) % poly.length];
      if ((y1 <= y && y2 > y) || (y2 <= y && y1 > y)) xs.push(x1 + (y - y1) * (x2 - x1) / (y2 - y1));
    }
    xs.sort((a, b) => a - b); const iv = []; for (let i = 0; i + 1 < xs.length; i += 2) iv.push([xs[i], xs[i + 1]]); return iv;
  }
  function inPoly2(poly, x, y) {
    let c = false;
    for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
      const [xi, yi] = poly[i], [xj, yj] = poly[j];
      if ((yi > y) !== (yj > y) && x < (xj - xi) * (y - yi) / (yj - yi) + xi) c = !c;
    }
    return c;
  }

  // ---------- surfaces
  function makeSurface(verts, normal, mat, kind) {
    const n = normal.slice(), L = Math.hypot(...n); n[0] /= L; n[1] /= L; n[2] /= L;
    const d = n[0] * verts[0][0] + n[1] * verts[0][1] + n[2] * verts[0][2];
    const ax = Math.abs(n[0]) >= Math.abs(n[1]) && Math.abs(n[0]) >= Math.abs(n[2]) ? 0 : Math.abs(n[1]) >= Math.abs(n[2]) ? 1 : 2;
    const u = ax === 0 ? 1 : 0, v = ax === 2 ? 1 : 2;
    const p2 = verts.map((p) => [p[u], p[v]]);
    let area = 0; for (let i = 0; i < p2.length; i++) { const a = p2[i], b = p2[(i + 1) % p2.length]; area += a[0] * b[1] - b[0] * a[1]; }
    area = Math.abs(area / 2) / Math.abs(n[ax]);
    let xmin = Infinity, xmax = -Infinity, ymin = Infinity, ymax = -Infinity;
    for (const [a, b] of p2) { xmin = Math.min(xmin, a); xmax = Math.max(xmax, a); ymin = Math.min(ymin, b); ymax = Math.max(ymax, b); }
    return { verts, n, d, u, v, p2, area, mat, kind, bb: [xmin, xmax, ymin, ymax] };
  }
  function inSurface(s, p) {
    const a = p[s.u], b = p[s.v], bb = s.bb, tol = 1e-7;
    if (a < bb[0] - tol || a > bb[1] + tol || b < bb[2] - tol || b > bb[3] + tol) return false;
    return inPoly2(s.p2, a, b);
  }

  // Build all surfaces. g = { plan:[[x,y]..], floor:[[y,z]..], ceil:[[y,z]..], stageY }
  function build(g) {
    const plan = ccw(g.plan);
    const ys = plan.map((p) => p[1]), y0 = Math.min(...ys), y1 = Math.max(...ys);
    let floor = normProfile(g.floor && g.floor.length ? g.floor : [[y0, 0]], y0, y1);
    let ceil = normProfile(g.ceil && g.ceil.length ? g.ceil : [[y0, 8]], y0, y1);
    // split floor at the stage edge so floor pieces are either audience or stage
    const sy = g.stageY;
    if (sy > y0 && sy < y1 && !floor.some((p) => Math.abs(p[0] - sy) < 1e-9)) {
      const z = profAt(floor, sy); let i = floor.findIndex((p) => p[0] > sy); floor.splice(i, 0, [sy, z]);
    }
    const S = [];
    const horiz = (prof, up, matOf, kind) => {
      for (let i = 0; i + 1 < prof.length; i++) {
        const [ya, za] = prof[i], [yb, zb] = prof[i + 1];
        if (yb - ya < 1e-9) { // riser
          if (Math.abs(zb - za) < 1e-9) continue;
          for (const [xa, xb] of lineCrossX(plan, ya + 1e-9)) {
            const lo = Math.min(za, zb), hi = Math.max(za, zb);
            // exposed face looks toward the side where the room extends past the step
            const ny = up ? (za > zb ? 1 : -1) : (za < zb ? 1 : -1);
            const verts = ny > 0 ? [[xa, ya, lo], [xb, ya, lo], [xb, ya, hi], [xa, ya, hi]] : [[xb, ya, lo], [xa, ya, lo], [xa, ya, hi], [xb, ya, hi]];
            S.push(makeSurface(verts, [0, ny, 0], matOf(ya + (ny > 0 ? 1e-6 : -1e-6)), up ? "riser" : "ceil-step"));
          }
          continue;
        }
        const poly = stripPoly(plan, ya, yb);
        if (poly.length < 3 || Math.abs(area2(poly)) < 1e-9) continue;
        const zf = (y) => za + (zb - za) * (y - ya) / (yb - ya);
        const verts = poly.map(([x, y]) => [x, y, zf(y)]);
        const slope = (zb - za) / (yb - ya);
        const n = up ? [0, -slope, 1] : [0, slope, -1];
        S.push(makeSurface(up ? verts : verts.slice().reverse(), n, matOf((ya + yb) / 2), kind));
      }
    };
    horiz(floor, true, (y) => (y >= sy - 1e-9 ? "stage" : "aud"), "floor");
    horiz(ceil, false, () => "ceil", "ceil");
    // walls: each outline edge extruded between floor and ceiling, following both profiles
    for (let i = 0; i < plan.length; i++) {
      const p = plan[i], q = plan[(i + 1) % plan.length], dx = q[0] - p[0], dy = q[1] - p[1];
      const len = Math.hypot(dx, dy); if (len < 1e-9) continue;
      const at = (t) => [p[0] + dx * t, p[1] + dy * t];
      // breakpoints carry the profile's exact y: y recomputed from t can land a hair off a riser and lose one of its ends
      const ts = [[0, p[1]], [1, q[1]]];
      if (Math.abs(dy) > 1e-12) for (const [y] of floor.concat(ceil)) { const t = (y - p[1]) / dy; if (t > 1e-9 && t < 1 - 1e-9) ts.push([t, y]); }
      ts.sort((a, b) => a[0] - b[0]);
      for (let j = ts.length - 1; j > 0; j--) if (ts[j][0] - ts[j - 1][0] < 1e-9) ts.splice(j, 1);   // a riser lists its y twice
      const dirSide = dy >= 0 ? [-1, 1] : [1, -1]; // limit side when entering / leaving a breakpoint along the edge
      const bottom = [], top = [];
      for (let k = 0; k < ts.length; k++) {
        const x = at(ts[k][0])[0], y = ts[k][1];
        const fIn = profAt(floor, y, dirSide[0]), fOut = profAt(floor, y, dirSide[1]);
        const cIn = profAt(ceil, y, dirSide[0]), cOut = profAt(ceil, y, dirSide[1]);
        if (Math.abs(dy) < 1e-12) { bottom.push([x, y, profAt(floor, y)]); top.push([x, y, profAt(ceil, y)]); continue; }
        if (k > 0) bottom.push([x, y, fIn]); if (k < ts.length - 1 && Math.abs(fOut - fIn) > 1e-9 || k === 0) bottom.push([x, y, fOut]);
        if (k > 0) top.push([x, y, cIn]); if (k < ts.length - 1 && Math.abs(cOut - cIn) > 1e-9 || k === 0) top.push([x, y, cOut]);
      }
      const verts = bottom.concat(top.reverse()).filter((v, k, a) => k === 0 || Math.hypot(v[0] - a[k - 1][0], v[1] - a[k - 1][1], v[2] - a[k - 1][2]) > 1e-9);
      if (verts.length < 3) continue;
      S.push(makeSurface(verts, [-dy, dx, 0], "wall", "wall"));
    }
    let V = 0, Sa = 0; // volume by vertical integration over the plan strips
    for (const s of S) Sa += s.area;
    { const N = 400; for (let k = 0; k < N; k++) { const y = y0 + (k + 0.5) * (y1 - y0) / N; let w = 0; for (const [a, b] of lineCrossX(plan, y)) w += b - a; V += w * (profAt(ceil, y) - profAt(floor, y)) * (y1 - y0) / N; } }
    return { S, plan, floor, ceil, y0, y1, V, area: Sa, stageY: sy };
  }

  function inside(G, p) {
    if (G.mesh) return voxInRoom(G.vox, p);
    return inPoly2(G.plan, p[0], p[1]) && p[2] > profAt(G.floor, p[1]) + 1e-6 && p[2] < profAt(G.ceil, p[1]) - 1e-6;
  }

  // ---------- OBJ mesh halls (same method as geometry.build_mesh in Python) ----------
  // parse Wavefront OBJ text: vertices, faces (index lists), and per face the group / object / material names
  function loadObj(text) {
    const V = [], F = [], names = []; let g = [], o = "", m = "", afterFace = false;
    for (const raw of text.split(/\r?\n/)) {
      const line = raw.trim();
      if (line.startsWith("v ")) { const t = line.split(/\s+/); V.push([+t[1], +t[2], +t[3]]); }
      else if (line.startsWith("f ")) {
        const idx = line.split(/\s+/).slice(1).map((tok) => { const i = parseInt(tok.split("/")[0], 10); return i > 0 ? i - 1 : V.length + i; });
        if (idx.length >= 3) { F.push(idx); names.push(g.join("|") + "|" + o + "|" + m); }
        afterFace = true;
      } else if (line.startsWith("g ")) { g = afterFace ? [line.slice(2).trim()] : g.concat([line.slice(2).trim()]); afterFace = false; }
      else if (line.startsWith("o ")) o = line.slice(2).trim();
      else if (line.startsWith("usemtl ")) m = line.slice(7).trim();
    }
    return { V, F, names };
  }
  // distinct group labels of an OBJ (for the material table): the last "g" name of each face's group list
  function objGroups(obj) { // distinct face labels (group | object | material) with face counts, for the material table
    const cnt = new Map(); for (const nm of obj.names) cnt.set(nm, (cnt.get(nm) || 0) + 1);
    return [...cnt.entries()].map(([name, n]) => ({ name, n }));
  }
  const newell = (P) => { const n = [0, 0, 0]; for (let i = 0; i < P.length; i++) { const a = P[i], b = P[(i + 1) % P.length]; n[0] += (a[1] - b[1]) * (a[2] + b[2]); n[1] += (a[2] - b[2]) * (a[0] + b[0]); n[2] += (a[0] - b[0]) * (a[1] + b[1]); } return n; };
  function sampleTri(a, b, c, h, out) { // points on a triangle with spacing <= h
    const L = Math.max(Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]), Math.hypot(c[0] - a[0], c[1] - a[1], c[2] - a[2]), Math.hypot(c[0] - b[0], c[1] - b[1], c[2] - b[2]));
    const k = Math.max(1, Math.ceil(L / h));
    for (let i = 0; i <= k; i++) for (let j = 0; i + j <= k; j++) { const u = i / k, w = j / k; out.push([a[0] + u * (b[0] - a[0]) + w * (c[0] - a[0]), a[1] + u * (b[1] - a[1]) + w * (c[1] - a[1]), a[2] + u * (b[2] - a[2]) + w * (c[2] - a[2])]); }
  }
  // flood-fill the free space connected to seed on a voxel grid (6-connected, surface band dilated by one voxel)
  function voxelRoom(V, T, seed, h) {
    const lo = [0, 1, 2].map((k) => Math.min(...V.map((v) => v[k])) - 3 * h), hi = [0, 1, 2].map((k) => Math.max(...V.map((v) => v[k])) + 3 * h);
    const nx = Math.ceil((hi[0] - lo[0]) / h) + 1, ny = Math.ceil((hi[1] - lo[1]) / h) + 1, nz = Math.ceil((hi[2] - lo[2]) / h) + 1, N = nx * ny * nz;
    const id = (i, j, k) => (i * ny + j) * nz + k;
    const solid0 = new Uint8Array(N);
    const pts = [];
    for (const [a, b, c] of T) { pts.length = 0; sampleTri(V[a], V[b], V[c], h / 2, pts); for (const p of pts) solid0[id(Math.floor((p[0] - lo[0]) / h), Math.floor((p[1] - lo[1]) / h), Math.floor((p[2] - lo[2]) / h))] = 1; }
    const solid = new Uint8Array(N);   // binary dilation, cross-shaped structure (as scipy.ndimage defaults)
    for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) for (let k = 0; k < nz; k++) {
      const q = id(i, j, k);
      if (solid0[q] || (i > 0 && solid0[q - ny * nz]) || (i < nx - 1 && solid0[q + ny * nz]) || (j > 0 && solid0[q - nz]) || (j < ny - 1 && solid0[q + nz]) || (k > 0 && solid0[q - 1]) || (k < nz - 1 && solid0[q + 1])) solid[q] = 1;
    }
    const si = Math.floor((seed[0] - lo[0]) / h), sj = Math.floor((seed[1] - lo[1]) / h), sk = Math.floor((seed[2] - lo[2]) / h);
    if (si < 0 || sj < 0 || sk < 0 || si >= nx || sj >= ny || sk >= nz) throw new Error("the first source lies outside the model");
    if (solid[id(si, sj, sk)]) throw new Error("the first source lies in the surface band of the model; move it away from surfaces");
    const room = new Uint8Array(N), queue = new Int32Array(N); let qh = 0, qt = 0;
    room[id(si, sj, sk)] = 1; queue[qt++] = id(si, sj, sk);
    while (qh < qt) {
      const q = queue[qh++], k = q % nz, j = ((q - k) / nz) % ny, i = (q - k - j * nz) / (ny * nz);
      const nb = [i > 0 ? q - ny * nz : -1, i < nx - 1 ? q + ny * nz : -1, j > 0 ? q - nz : -1, j < ny - 1 ? q + nz : -1, k > 0 ? q - 1 : -1, k < nz - 1 ? q + 1 : -1];
      for (const r of nb) if (r >= 0 && !solid[r] && !room[r]) { room[r] = 1; queue[qt++] = r; }
    }
    if (room[0]) throw new Error("the model is not closed: the room leaks to the outside (gap wider than the voxel band)");
    let nIn = qt, nBand = 0;
    for (let q = 0; q < N; q++) if (solid[q]) { const k = q % nz, j = ((q - k) / nz) % ny, i = (q - k - j * nz) / (ny * nz);
      if ((i > 0 && room[q - ny * nz] === 1) || (i < nx - 1 && room[q + ny * nz] === 1) || (j > 0 && room[q - nz] === 1) || (j < ny - 1 && room[q + nz] === 1) || (k > 0 && room[q - 1] === 1) || (k < nz - 1 && room[q + 1] === 1)) nBand++; }
    for (let q = 0; q < N; q++) if (solid[q] && !room[q]) room[q] = 2;   // 2: surface band (neither room nor enclosed void)
    return { lo, h, dims: [nx, ny, nz], room, volume: (nIn + 0.5 * nBand) * h ** 3 };
  }
  function voxInRoom(vx, p) {
    const [nx, ny, nz] = vx.dims, i = Math.floor((p[0] - vx.lo[0]) / vx.h), j = Math.floor((p[1] - vx.lo[1]) / vx.h), k = Math.floor((p[2] - vx.lo[2]) / vx.h);
    if (i < 0 || j < 0 || k < 0 || i >= nx || j >= ny || k >= nz) return false;
    return vx.room[(i * ny + j) * nz + k] === 1;
  }
  // a point in free space that the room flood fill did not reach: the void inside a solid or the outside of the hall
  function voxVoid(vx, p) {
    const [nx, ny, nz] = vx.dims, i = Math.floor((p[0] - vx.lo[0]) / vx.h), j = Math.floor((p[1] - vx.lo[1]) / vx.h), k = Math.floor((p[2] - vx.lo[2]) / vx.h);
    if (i < 0 || j < 0 || k < 0 || i >= nx || j >= ny || k >= nz) return true;
    return vx.room[(i * ny + j) * nz + k] === 0;
  }
  function inflatePoly(P, n, e) { // move every edge of a planar convex polygon outward by e (closes cracks between faces)
    const k = P.length, c = [0, 1, 2].map((a) => P.reduce((s, p) => s + p[a], 0) / k), lines = [];
    for (let i = 0; i < k; i++) {
      const a = P[i], b = P[(i + 1) % k], t0 = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], tl = Math.hypot(...t0) + 1e-12, t = t0.map((v) => v / tl);
      let out = crs(t, n); if (out[0] * (c[0] - a[0]) + out[1] * (c[1] - a[1]) + out[2] * (c[2] - a[2]) > 0) out = out.map((v) => -v);
      lines.push([[a[0] + e * out[0], a[1] + e * out[1], a[2] + e * out[2]], t]);
    }
    return P.map((p, i) => {
      const [a1, t1] = lines[(i - 1 + k) % k], [a2, t2] = lines[i];
      // least squares x1 t1 - x2 t2 = a2 - a1
      const r = [a2[0] - a1[0], a2[1] - a1[1], a2[2] - a1[2]], A11 = dot(t1, t1), A12 = -dot(t1, t2), A22 = dot(t2, t2), b1 = dot(t1, r), b2 = -dot(t2, r), det = A11 * A22 - A12 * A12;
      let q = null;
      if (Math.abs(det) > 1e-12) { const x1 = (b1 * A22 - A12 * b2) / det; q = [a1[0] + x1 * t1[0], a1[1] + x1 * t1[1], a1[2] + x1 * t1[2]]; }
      if (!q || Math.hypot(q[0] - p[0], q[1] - p[1], q[2] - p[2]) > 20 * e) { const d = [p[0] - c[0], p[1] - c[1], p[2] - c[2]], dl = Math.hypot(...d) + 1e-12; q = [p[0] + e * d[0] / dl, p[1] + e * d[1] / dl, p[2] + e * d[2] / dl]; }
      return q;
    });
  }
  // spec = { obj (parsed by loadObj), groups: { substring: materialKey }, default, axes: "y-up" | "z-up", voxel (m),
  //          twoSided (default true), inflateMm (default 1), maxVoxels (default 2e7) }, seed = first source position
  function buildMesh(spec, seed) {
    const obj = spec.obj, axes = spec.axes || "y-up";
    // page frame (optional): turn by rot degrees about z, then shift (the page moves the model to x, y, z >= 0)
    const sh = spec.shift || [0, 0, 0], ra = (spec.rot || 0) * Math.PI / 180, cr = Math.cos(ra), sr = Math.sin(ra);
    const V = obj.V.map((v) => (axes === "z-up" ? v.slice() : [v[0], -v[2], v[1]])).map((v) => [cr * v[0] - sr * v[1] + sh[0], sr * v[0] + cr * v[1] + sh[1], v[2] + sh[2]]);
    // longer names first, so that a name that is part of another one does not take its faces
    const groups = Object.entries(spec.groups || {}).map(([g, v]) => [g.toLowerCase(), v]).sort((a, b) => b[0].length - a[0].length);
    const T = [], owner = [];
    obj.F.forEach((f, k) => { for (let i = 1; i + 1 < f.length; i++) { T.push([f[0], f[i], f[i + 1]]); owner.push(k); } });
    const ext = [0, 1, 2].map((a) => Math.max(...V.map((v) => v[a])) - Math.min(...V.map((v) => v[a])));
    // voxel size: as given, but never more than 2.5 x maxVoxels cells (browser memory); auto: >= 5 cm within maxVoxels
    const box = (ext[0] + 0.3) * (ext[1] + 0.3) * (ext[2] + 0.3), mv = spec.maxVoxels || 2e7;
    const h = spec.voxel ? Math.max(spec.voxel, Math.cbrt(box / (2.5 * mv))) : Math.max(0.05, Math.cbrt(box / mv));
    const vx = voxelRoom(V, T, seed, h), off = 2.5 * h, inflate = (spec.inflateMm == null ? 1 : spec.inflateMm) / 1000, twoSided = spec.twoSided !== false;
    const triOf = new Map(); owner.forEach((k, i) => { if (!triOf.has(k)) triOf.set(k, []); triOf.get(k).push(T[i]); });
    const S = [], unmatched = new Set(); let dropped = 0;
    obj.F.forEach((f, k) => {
      const P = f.map((i) => V[i]), nw = newell(P), A = Math.hypot(...nw) / 2; if (A < 1e-6) return;
      const n = nw.map((v) => v / (2 * A)), C = [];
      for (const [a, b, c] of triOf.get(k)) { C.push([(V[a][0] + V[b][0] + V[c][0]) / 3, (V[a][1] + V[b][1] + V[c][1]) / 3, (V[a][2] + V[b][2] + V[c][2]) / 3]); }
      for (const [a, b, c] of triOf.get(k)) sampleTri(V[a], V[b], V[c], 0.2, C);
      let fwd = 0, bwd = 0; for (const p of C) { if (voxInRoom(vx, [p[0] + off * n[0], p[1] + off * n[1], p[2] + off * n[2]])) fwd++; if (voxInRoom(vx, [p[0] - off * n[0], p[1] - off * n[1], p[2] - off * n[2]])) bwd++; }
      if (fwd === 0 && bwd === 0) { dropped++; return; }
      const both = Math.min(fwd, bwd) > 0.2 * Math.max(fwd, bwd), nn = fwd >= bwd ? n : n.map((v) => -v);
      const nm = obj.names[k].toLowerCase(); let key = spec.default;
      for (const [g, v] of groups) if (nm.includes(g)) { key = v; break; }
      if (key && typeof key === "object") key = key[nn[2] < -0.3 ? "ceiling" : nn[2] > 0.3 ? "floor" : "wall"] || key.default;
      if (key == null) { unmatched.add(obj.names[k]); return; }
      const Pv = inflate > 0 ? inflatePoly(P, nn, inflate) : P;
      const s = makeSurface(Pv, nn, key, "mesh"); s.area = A; S.push(s);
      if (both || twoSided) { const t = makeSurface(Pv.map((p) => [p[0] - 0.002 * nn[0], p[1] - 0.002 * nn[1], p[2] - 0.002 * nn[2]]), nn.map((v) => -v), key, "mesh-twin"); t.area = A; t.solo = !both; S.push(t); }
    });
    if (unmatched.size) throw new Error("model faces without a material: " + [...unmatched].slice(0, 8).join("; "));
    const area = {}; for (const s of S) if (s.kind === "mesh") area[s.mat] = (area[s.mat] || 0) + s.area;
    const lo = [0, 1, 2].map((a) => Math.min(...V.map((v) => v[a]))), hi = [0, 1, 2].map((a) => Math.max(...V.map((v) => v[a])));
    const G = { S, mesh: true, vox: vx, V: vx.volume, area: Object.values(area).reduce((a, b) => a + b, 0), areaByMat: area, nDropped: dropped, nFaces: obj.F.length, bbox: [lo, hi], h };
    G.bvh = bvhBuild(G.S);
    meshViews(G);
    return G;
  }
  // plan and section views of a mesh room for the page: per voxel column the lowest and highest room voxel, the plan
  // outline as the x range of each y row (exact for outlines that are convex across x), and the floor / ceiling lines
  // as the lowest floor and highest ceiling of each y row
  function meshViews(G) {
    const vx = G.vox, [nx, ny, nz] = vx.dims, h = vx.h, cf = new Float32Array(nx * ny).fill(NaN), cc = new Float32Array(nx * ny).fill(NaN);
    for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) { const b = (i * ny + j) * nz;
      let k0 = -1, k1 = -1; for (let k = 0; k < nz; k++) if (vx.room[b + k] === 1) { if (k0 < 0) k0 = k; k1 = k; }
      if (k0 >= 0) { cf[i * ny + j] = vx.lo[2] + k0 * h; cc[i * ny + j] = vx.lo[2] + (k1 + 1) * h; } }
    vx.colFloor = cf; vx.colCeil = cc;
    const left = [], right = [], floor = [], ceil = [], step = Math.max(1, Math.round(0.25 / h));
    for (let j = 0; j < ny; j += step) {
      let i0 = -1, i1 = -1, f = Infinity, c = -Infinity;
      for (let jj = j; jj < Math.min(ny, j + step); jj++) for (let i = 0; i < nx; i++) { const q = i * ny + jj; if (!(cf[q] === cf[q])) continue;
        if (i0 < 0 || i < i0) i0 = i; if (i > i1) i1 = i; f = Math.min(f, cf[q]); c = Math.max(c, cc[q]); }
      if (i0 < 0) continue;
      const y = vx.lo[1] + (j + Math.min(step, ny - j) / 2) * h;
      left.push([vx.lo[0] + i0 * h, y]); right.push([vx.lo[0] + (i1 + 1) * h, y]); floor.push([y, f]); ceil.push([y, c]);
    }
    if (left.length) { // close the outline at the first and last row edges
      const y0 = left[0][1] - step * h / 2, y1 = left[left.length - 1][1] + step * h / 2;
      left.unshift([left[0][0], y0]); right.unshift([right[0][0], y0]); left.push([left[left.length - 1][0], y1]); right.push([right[right.length - 1][0], y1]);
    }
    G.plan = left.concat(right.reverse()); G.floor = floor; G.ceil = ceil;
    // wall faces projected on the plan (one-sided room faces, |n_z| < 0.5) for the drawing
    G.planSegs = []; for (const s of G.S) if (s.kind === "mesh" && Math.abs(s.n[2]) < 0.5) { const P = s.verts || s.P; if (!P) continue;
      let a = 0, b = 0, best = -1; for (let u = 0; u < P.length; u++) for (let v = u + 1; v < P.length; v++) { const d = (P[u][0] - P[v][0]) ** 2 + (P[u][1] - P[v][1]) ** 2; if (d > best) { best = d; a = u; b = v; } }
      if (best > 1e-4) G.planSegs.push([P[a][0], P[a][1], P[b][0], P[b][1], s.mat]); }
  }
  // lowest floor / highest ceiling (m) of the room above the plan point (x, y) of a mesh hall; null outside the room
  function meshColumn(G, x, y) {
    const vx = G.vox, [nx, ny] = vx.dims, i = Math.floor((x - vx.lo[0]) / vx.h), j = Math.floor((y - vx.lo[1]) / vx.h);
    if (i < 0 || j < 0 || i >= nx || j >= ny) return null; const q = i * ny + j, f = vx.colFloor[q];
    return f === f ? [f, vx.colCeil[q]] : null;
  }

  // ---------- bounding volume hierarchy over surfaces (mesh halls: thousands of faces) ----------
  function bvhBuild(S) {
    const n = S.length, lo = new Float64Array(3 * n), hi = new Float64Array(3 * n), ctr = new Float64Array(3 * n);
    S.forEach((s, i) => { for (let a = 0; a < 3; a++) { let mn = Infinity, mx = -Infinity; for (const v of s.verts) { mn = Math.min(mn, v[a]); mx = Math.max(mx, v[a]); } lo[3 * i + a] = mn - 1e-6; hi[3 * i + a] = mx + 1e-6; ctr[3 * i + a] = (mn + mx) / 2; } });
    const idx = Int32Array.from({ length: n }, (_, i) => i), nodes = [];   // node: [lo3, hi3, left, right, start, count]
    function make(start, end) {
      const b = [Infinity, Infinity, Infinity, -Infinity, -Infinity, -Infinity];
      for (let k = start; k < end; k++) { const i = idx[k]; for (let a = 0; a < 3; a++) { b[a] = Math.min(b[a], lo[3 * i + a]); b[3 + a] = Math.max(b[3 + a], hi[3 * i + a]); } }
      const me = nodes.length; nodes.push({ b, l: -1, r: -1, s: start, c: end - start });
      if (end - start <= 4) return me;
      let ax = 0; const ex = [b[3] - b[0], b[4] - b[1], b[5] - b[2]]; if (ex[1] > ex[ax]) ax = 1; if (ex[2] > ex[ax]) ax = 2;
      const sub = Array.from(idx.subarray(start, end)).sort((p, q) => ctr[3 * p + ax] - ctr[3 * q + ax]); idx.set(sub, start);
      const mid = (start + end) >> 1; nodes[me].l = make(start, mid); nodes[me].r = make(mid, end); nodes[me].c = 0;
      return me;
    }
    if (n) make(0, n);
    return { nodes, idx };
  }
  // visit the surfaces whose boxes the ray o + t d (0 <= t <= tmax) passes; fn(i) returns a new tmax (or undefined)
  function bvhWalk(bvh, o, d, tmax, fn) {
    const inv = [1 / d[0], 1 / d[1], 1 / d[2]], stack = [0];
    while (stack.length) {
      const nd = bvh.nodes[stack.pop()], b = nd.b; let t0 = 0, t1 = tmax;
      for (let a = 0; a < 3; a++) { let ta = (b[a] - o[a]) * inv[a], tb = (b[3 + a] - o[a]) * inv[a]; if (ta > tb) { const x = ta; ta = tb; tb = x; } if (ta > t0) t0 = ta; if (tb < t1) t1 = tb; if (t0 > t1) break; }
      if (t0 > t1) continue;
      if (nd.c) { for (let k = nd.s; k < nd.s + nd.c; k++) { const r = fn(bvh.idx[k]); if (r !== undefined) tmax = r; if (tmax < 0) return; } }
      else { stack.push(nd.l, nd.r); }
    }
  }

  // segment a->b intersects a surface (excluding the ones in skip) strictly between the ends?
  function occluded(G, a, b, skipA, skipB) {
    const dx = b[0] - a[0], dy = b[1] - a[1], dz = b[2] - a[2];
    if (G.bvh) {
      let hit = false;
      bvhWalk(G.bvh, a, [dx, dy, dz], 1, (i) => {
        if (i === skipA || i === skipB) return;
        const s = G.S[i], den = s.n[0] * dx + s.n[1] * dy + s.n[2] * dz;
        if (Math.abs(den) < EPS) return;
        const t = (s.d - (s.n[0] * a[0] + s.n[1] * a[1] + s.n[2] * a[2])) / den;
        if (t <= 1e-6 || t >= 1 - 1e-6) return;
        if (inSurface(s, [a[0] + t * dx, a[1] + t * dy, a[2] + t * dz])) { hit = true; return -1; }
      });
      return hit;
    }
    for (let i = 0; i < G.S.length; i++) {
      if (i === skipA || i === skipB) continue;
      const s = G.S[i], den = s.n[0] * dx + s.n[1] * dy + s.n[2] * dz;
      if (Math.abs(den) < EPS) continue;
      const t = (s.d - (s.n[0] * a[0] + s.n[1] * a[1] + s.n[2] * a[2])) / den;
      if (t <= 1e-6 || t >= 1 - 1e-6) continue;
      if (inSurface(s, [a[0] + t * dx, a[1] + t * dy, a[2] + t * dz])) return true;
    }
    return false;
  }

  // ---------- specular factors of image-source reflections (same algorithm as reflections.py):
  // finite reflector size (Kirchhoff-Fresnel after Rindel 2005) and scattering loss (1 - s), as energy factors
  function fresnel(x) { // [C(x), S(x)], C = int_0^x cos(pi t^2 / 2) dt; series |x| < 3, asymptotic above
    const ax = Math.abs(x); let c, s;
    if (ax < 3) {
      const z = Math.PI * ax * ax / 2, z2 = z * z; let tc = 1, ts = z, n = 0; c = 0; s = 0;
      for (;;) { c += tc / (4 * n + 1); s += ts / (4 * n + 3); tc *= -z2 / ((2 * n + 1) * (2 * n + 2)); ts *= -z2 / ((2 * n + 2) * (2 * n + 3)); n++; if (Math.abs(tc) < 1e-17 && Math.abs(ts) < 1e-17 || n > 60) break; }
      c *= ax; s *= ax;
    } else {
      const pz = Math.PI * ax * ax, u = 1 / (pz * pz), z = pz / 2;
      const f = (1 - u * (3 - u * (105 - u * 10395))) / (Math.PI * ax), g = (1 - u * (15 - u * (945 - u * 135135))) / (Math.PI * pz * ax);
      c = 0.5 + f * Math.sin(z) - g * Math.cos(z); s = 0.5 - f * Math.cos(z) - g * Math.sin(z);
    }
    return x >= 0 ? [c, s] : [-c, -s];
  }
  function fresnelK(lo, hi) { const a = fresnel(lo), b = fresnel(hi); return 0.5 * ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2); }
  function segDist(p, a, b) {
    const ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]], L2 = Math.max(ab[0] ** 2 + ab[1] ** 2 + ab[2] ** 2, 1e-18);
    const t = Math.min(1, Math.max(0, ((p[0] - a[0]) * ab[0] + (p[1] - a[1]) * ab[1] + (p[2] - a[2]) * ab[2]) / L2));
    return Math.hypot(p[0] - a[0] - t * ab[0], p[1] - a[1] - t * ab[1], p[2] - a[2] - t * ab[2]);
  }
  function touch(A, B, tol) {
    for (const [P, Q] of [[A, B], [B, A]]) for (const p of P) for (let k = 0; k < Q.length; k++) if (segDist(p, Q[k], Q[(k + 1) % Q.length]) <= tol) return true;
    return false;
  }
  // touching surfaces whose normals differ by less than PANEL_ANGLE form one panel (cached on G); sweep over bounding boxes
  const PANEL_ANGLE = 2;
  function panels(G, tol = 0.01) {
    if (G._panels) return G._panels;
    const S = G.S, n = S.length, par = S.map((_, i) => i), cmin = Math.cos(PANEL_ANGLE * Math.PI / 180);
    const find = (a) => { while (par[a] !== a) { par[a] = par[par[a]]; a = par[a]; } return a; };
    const lo = S.map((s) => [0, 1, 2].map((k) => Math.min(...s.verts.map((v) => v[k])) - tol)), hi = S.map((s) => [0, 1, 2].map((k) => Math.max(...s.verts.map((v) => v[k])) + tol));
    const order = S.map((_, i) => i).sort((a, b) => lo[a][0] - lo[b][0] || a - b);
    let active = [];
    for (const a of order) {
      active = active.filter((b) => hi[b][0] >= lo[a][0]);
      for (const b of active) {
        const A = S[a], B = S[b];
        if (A.n[0] * B.n[0] + A.n[1] * B.n[1] + A.n[2] * B.n[2] < cmin || lo[a][1] > hi[b][1] || lo[b][1] > hi[a][1] || lo[a][2] > hi[b][2] || lo[b][2] > hi[a][2]) continue;
        if (find(a) !== find(b) && touch(A.verts, B.verts, tol)) par[find(b)] = find(a);
      }
      active.push(a);
    }
    const pid = S.map((_, i) => find(i)), members = new Map();
    pid.forEach((p, i) => { if (!members.has(p)) members.set(p, []); members.get(p).push(i); });
    return (G._panels = { pid, members });
  }
  function chord(G, mem, P, e, f) { // interval [smin <= 0 <= smax] of the line P + s e inside the panel's polygons
    const iv = [];
    for (const i of mem) {
      const V = G.S[i].verts, x = V.map((v) => (v[0] - P[0]) * e[0] + (v[1] - P[1]) * e[1] + (v[2] - P[2]) * e[2]), y = V.map((v) => (v[0] - P[0]) * f[0] + (v[1] - P[1]) * f[1] + (v[2] - P[2]) * f[2]);
      const xs = [];
      for (let k = 0; k < x.length; k++) { const k2 = (k + 1) % x.length, y1 = y[k], y2 = y[k2]; if ((y1 <= 0 && 0 < y2) || (y2 <= 0 && 0 < y1)) xs.push(x[k] + (0 - y1) * (x[k2] - x[k]) / (y2 - y1)); }
      xs.sort((a, b) => a - b); for (let j = 0; j + 1 < xs.length; j += 2) iv.push([xs[j], xs[j + 1]]);
    }
    if (!iv.length) return [-1e9, 1e9];
    iv.sort((a, b) => a[0] - b[0]); const mg = [iv[0].slice()];
    for (const [a, b] of iv.slice(1)) { const L = mg[mg.length - 1]; if (a <= L[1] + 1e-3) L[1] = Math.max(L[1], b); else mg.push([a, b]); }
    for (const [a, b] of mg) if (a - 1e-3 <= 0 && 0 <= b + 1e-3) return [Math.min(a, 0), Math.max(b, 0)];
    let best = mg[0]; for (const q of mg) if (Math.min(Math.abs(q[0]), Math.abs(q[1])) < Math.min(Math.abs(best[0]), Math.abs(best[1]))) best = q;
    return [Math.min(best[0], 0), Math.max(best[1], 0)];
  }
  function reflK(G, w, P, uin, a1, a2, freqs, c) { // energy factor K1*K2 per frequency
    const { pid, members } = panels(G), n = G.S[w].n, un = uin[0] * n[0] + uin[1] * n[1] + uin[2] * n[2], cosT = Math.abs(un);
    let t = [uin[0] - un * n[0], uin[1] - un * n[1], uin[2] - un * n[2]];
    if (Math.hypot(...t) < 1e-6) t = Math.abs(n[0]) < 0.9 ? crs(n, [1, 0, 0]) : crs(n, [0, 1, 0]);
    const tl = Math.hypot(...t), e1 = [t[0] / tl, t[1] / tl, t[2] / tl], e2 = crs(n, e1), mem = members.get(pid[w]);
    const s1 = chord(G, mem, P, e1, e2), s2 = chord(G, mem, P, e2, e1), as = 2 * a1 * a2 / (a1 + a2);
    return freqs.map((fr) => { const k = 2 / Math.sqrt(c / fr * as); return fresnelK(k * s1[0] * cosT, k * s1[1] * cosT) * fresnelK(k * s2[0], k * s2[1]); });
  }
  // energy factors [nb] for a reflection path: pts = reflection points (source side first), seq = surface indices
  function specFactor(G, src, r, seq, pts, mats, bands, c) {
    const NB = bands.length, F = new Float64Array(NB).fill(1); if (!seq.length) return F;
    const path = [src].concat(pts, [r]), seg = [];
    for (let i = 0; i + 1 < path.length; i++) seg.push(Math.hypot(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1], path[i + 1][2] - path[i][2]));
    const tot = seg.reduce((a, b) => a + b, 0); let a1 = 0;
    const fq = bands.map((f) => [f * 2 ** (-1 / 3), f, f * 2 ** (1 / 3)]);
    seq.forEach((w, j) => {
      a1 += seg[j]; const P = pts[j], L = Math.max(seg[j], 1e-12), uin = [(P[0] - path[j][0]) / L, (P[1] - path[j][1]) / L, (P[2] - path[j][2]) / L];
      const sc = mats[G.S[w].mat].s, scb = Array.isArray(sc) ? sc : null;
      for (let b = 0; b < NB; b++) {
        const K = reflK(G, w, P, uin, a1, tot - a1, fq[b], c), km = (K[0] + K[1] + K[2]) / 3;
        F[b] *= (1 - (scb ? scb[Math.min(b, scb.length - 1)] : sc || 0)) * km;
      }
    });
    return F;
  }

  // ---------- image sources. mats: { name: { R:[nb], s } }, air: [nb]
  function ism(G, src, recs, order, tWindow, c, mats, air, bands) { // bands (Hz): with them, reflections get specFactor
    const NB = air.length, out = recs.map(() => []);
    const maxD = recs.map((r) => Math.hypot(src[0] - r[0], src[1] - r[1], src[2] - r[2]) + c * tWindow);
    const maxAll = Math.max(...maxD);
    // direct
    recs.forEach((r, k) => { if (!occluded(G, src, r, -1, -1)) push(k, src, [], r, [r]); });
    // pts: reflection points, source side first (for the direct sound: [receiver]); pts[0] is where the path leaves the source to
    function push(k, img, seq, r, pts) {
      const d = Math.hypot(img[0] - r[0], img[1] - r[1], img[2] - r[2]); if (d > maxD[k] || d < 1e-9) return;
      const first = pts[0], g = new Float64Array(NB), F = bands && seq.length ? specFactor(G, src, r, seq, pts, mats, bands, c) : null;
      for (let b = 0; b < NB; b++) { let a = 1; for (const w of seq) a *= mats[G.S[w].mat].R[b]; g[b] = a / d * Math.exp(-0.5 * air[b] * d) * (F ? Math.sqrt(F[b]) : 1); }
      const ex = first[0] - src[0], ey = first[1] - src[1], ez = first[2] - src[2], el = Math.hypot(ex, ey, ez) || 1;
      out[k].push({ d, t: d / c, o: seq.length, h: [(img[1] - r[1]) / d, -(img[0] - r[0]) / d, (img[2] - r[2]) / d], g, seq: seq.slice(), e: [ex / el, ey / el, ez / el] });
    }
    // validate path receiver <- ... <- image by back-tracing; images: stack of positions per order.
    // Returns the reflection points, source side first (pts[0]: where the path leaves the source to), or null.
    function audible(r, imgs, seq) {
      let p = r, prevWall = -1; const pts = [];
      for (let k = seq.length - 1; k >= 0; k--) {
        const s = G.S[seq[k]], im = imgs[k + 1];
        const dx = im[0] - p[0], dy = im[1] - p[1], dz = im[2] - p[2], den = s.n[0] * dx + s.n[1] * dy + s.n[2] * dz;
        if (Math.abs(den) < EPS) return null;
        const t = (s.d - (s.n[0] * p[0] + s.n[1] * p[1] + s.n[2] * p[2])) / den;
        if (t <= 1e-9 || t >= 1) return null;
        const q = [p[0] + t * dx, p[1] + t * dy, p[2] + t * dz];
        if (!inSurface(s, q)) return null;
        if (occluded(G, p, q, prevWall, seq[k])) return null;
        p = q; prevWall = seq[k]; pts.unshift(q);
      }
      return occluded(G, p, imgs[0], prevWall, -1) ? null : pts;
    }
    const ctr = G.mesh ? [(G.bbox[0][0] + G.bbox[1][0]) / 2, (G.bbox[0][1] + G.bbox[1][1]) / 2, 0] : [(Math.min(...G.plan.map((q) => q[0])) + Math.max(...G.plan.map((q) => q[0]))) / 2, (G.y0 + G.y1) / 2, 0];
    const span = G.mesh ? Math.hypot(G.bbox[1][0] - G.bbox[0][0], G.bbox[1][1] - G.bbox[0][1]) : Math.hypot(G.y1 - G.y0, 50);
    function rec(imgs, seq) {
      const last = imgs[imgs.length - 1];
      if (seq.length) recs.forEach((r, k) => { if (Math.hypot(last[0] - r[0], last[1] - r[1], last[2] - r[2]) > maxD[k]) return; const f = audible(r, imgs, seq); if (f) push(k, last, seq, r, f); });
      if (seq.length >= order) return;
      for (let w = 0; w < G.S.length; w++) {
        if (w === seq[seq.length - 1]) continue;
        const s = G.S[w], side = s.n[0] * last[0] + s.n[1] * last[1] + s.n[2] * last[2] - s.d;
        if (side <= 1e-9) continue; // image must be in front of the reflecting plane
        const im = [last[0] - 2 * side * s.n[0], last[1] - 2 * side * s.n[1], last[2] - 2 * side * s.n[2]];
        if (Math.hypot(im[0] - ctr[0], im[1] - ctr[1]) - span > maxAll + 50) continue;
        let nearest = Infinity; for (const r of recs) nearest = Math.min(nearest, Math.hypot(im[0] - r[0], im[1] - r[1], im[2] - r[2]));
        if (nearest > maxAll) continue;
        imgs.push(im); seq.push(w); rec(imgs, seq); imgs.pop(); seq.pop();
      }
    }
    rec([src.slice()], []);
    return out;
  }

  // Fibonacci sphere of 64 directions (same sequence as dirrays.fib_dirs)
  const FIB = (() => { const a = [], N = 64; for (let i = 0; i < N; i++) { const z = 1 - 2 * (i + 0.5) / N, ph = Math.PI * (1 + Math.sqrt(5)) * (i + 0.5), r = Math.sqrt(1 - z * z); a.push([r * Math.cos(ph), r * Math.sin(ph), z]); } return a; })();
  // ---------- ray tracing: returns per receiver [NB][nBins] energy histogram
  function rays(G, src, recs, opts, mats, air) {
    const { n = 20000, c = 343, tMax = 2.5, bin = 0.001, radius = 0.5, seed = 1, tLate = null } = opts, NB = air.length;
    const nBins = Math.round(tMax / bin), H = recs.map(() => Array.from({ length: NB }, () => new Float64Array(nBins)));
    // late-field arrival directions (as dirrays.py): energy per Fibonacci bin (head frame) and band after tLate[m]
    const W = tLate ? recs.map(() => new Float64Array(FIB.length * NB)) : null, RW = 1.0, VW = 4 / 3 * Math.PI * RW ** 3;   // incoming direction -d, head frame [-dy, dx, -dz]
    let st = seed >>> 0 || 1; const rnd = () => { st ^= st << 13; st >>>= 0; st ^= st >>> 17; st ^= st << 5; st >>>= 0; return st / 4294967296; };
    const Vs = 4 / 3 * Math.PI * radius ** 3, r2 = radius * radius, Lmax = c * tMax, e0 = 4 * Math.PI / n;
    const Rpow = {}; for (const m in mats) Rpow[m] = mats[m].R.map((r) => r * r);
    let escaped = 0, hits = 0, leaked = 0;
    const tHit = new Float64Array(G.S.length);
    for (let k = 0; k < n; k++) {
      // uniform direction (stratified in z)
      const zc = 1 - 2 * (k + rnd()) / n, ph = 2 * Math.PI * rnd(), sr = Math.sqrt(Math.max(0, 1 - zc * zc));
      let dx = sr * Math.cos(ph), dy = sr * Math.sin(ph), dz = zc;
      let ox = src[0], oy = src[1], oz = src[2], L = 0, last = -1, twinPrev = false;
      const e = new Float64Array(NB).fill(e0);
      for (let bounce = 0; bounce < 400; bounce++) {
        // nearest surface
        let best = Infinity, bi = -1;
        const test = (i) => {
          if (i === last) return;
          const s = G.S[i], den = s.n[0] * dx + s.n[1] * dy + s.n[2] * dz;
          if (den >= -1e-12) return; // moving away from the inside face
          const t = (s.d - (s.n[0] * ox + s.n[1] * oy + s.n[2] * oz)) / den;
          if (t > 1e-9 && t < best && inSurface(s, [ox + t * dx, oy + t * dy, oz + t * dz])) { best = t; bi = i; return t; }
        };
        if (G.bvh) bvhWalk(G.bvh, [ox, oy, oz], [dx, dy, dz], Infinity, test);
        else for (let i = 0; i < G.S.length; i++) test(i);
        if (bi < 0) { escaped++; break; }
        // mesh halls: a ray that got through a crack into a solid (or out of the hall) is ended here, before it
        // deposits energy. Behind a face it would bounce between the back-facing twins with little loss and, passing
        // near a receiver, add a long artificial tail (CR3: T30 +50 %). The segment is tested at 1/4, 1/2 and 3/4 of its
        // length: a point in a void that the room flood fill did not reach ends the ray. Points in the surface band are
        // not counted (a ray passing close to a seat or a rail is still in the room).
        // A ray that meets the back-facing twin of a one-sided face came through a crack in that face and is sent
        // back into the room; one that meets two such twins in a row is moving inside a solid and is ended.
        if (G.mesh && G.S[bi].solo) { if (twinPrev) { leaked++; break; } twinPrev = true; } else twinPrev = false;
        if (G.mesh && best > 3 * G.vox.h) { let lk = false;
          for (const f of [0.25, 0.5, 0.75]) if (voxVoid(G.vox, [ox + f * best * dx, oy + f * best * dy, oz + f * best * dz])) { lk = true; break; }
          if (lk) { leaked++; break; } }
        // receivers along this segment
        for (let m = 0; m < recs.length; m++) {
          const r = recs[m], wx = r[0] - ox, wy = r[1] - oy, wz = r[2] - oz, tc = wx * dx + wy * dy + wz * dz;
          const d2 = wx * wx + wy * wy + wz * wz - tc * tc;
          if (W && d2 < RW * RW) { // direction statistics: 1 m sphere (less Monte-Carlo noise; as dirrays.py)
            const hw = Math.sqrt(RW * RW - d2), a0 = Math.max(0, tc - hw), b0 = Math.min(best, tc + hw);
            if (b0 > a0) { const dw = L + (a0 + b0) / 2;
              if (dw / c >= tLate[m] && dw / c < tMax) { let bk = 0, bd = -2; for (let q = 0; q < FIB.length; q++) { const v = -dy * FIB[q][0] + dx * FIB[q][1] - dz * FIB[q][2]; if (v > bd) { bd = v; bk = q; } }
                const fw = (b0 - a0) / VW; for (let b = 0; b < NB; b++) W[m][bk * NB + b] += e[b] * Math.exp(-air[b] * dw) * fw; } }
          }
          if (d2 >= r2) continue;
          const hc = Math.sqrt(r2 - d2), ta = Math.max(0, tc - hc), tb = Math.min(best, tc + hc); if (tb <= ta) continue;
          const dist = L + (ta + tb) / 2, ib = Math.floor(dist / c / bin); if (ib >= nBins) continue;
          const f = (tb - ta) / Vs; for (let b = 0; b < NB; b++) H[m][b][ib] += e[b] * Math.exp(-air[b] * dist) * f;
          hits++;
        }
        L += best; if (L >= Lmax) break;
        ox += best * dx; oy += best * dy; oz += best * dz;
        const s = G.S[bi], P = Rpow[s.mat]; let emax = 0;
        for (let b = 0; b < NB; b++) { e[b] *= P[b]; if (e[b] > emax) emax = e[b]; }
        if (emax < e0 * 1e-7) break;
        const sc = mats[s.mat].s; let scat, blend = -1;
        if (G.mesh) { // mesh halls: as the pyroomacoustics tracer used by the Python mesh path (libroom room.cpp), the new
          // direction is the normalised mix s*Lambert + (1-s)*specular with s the mean over bands; no energy split
          let p = 0; if (Array.isArray(sc)) { for (let b = 0; b < NB; b++) p += sc[Math.min(b, sc.length - 1)]; p /= NB; } else p = sc;
          blend = p; scat = p > 0;
        } else if (Array.isArray(sc)) { // per-band scattering: one direction for all bands, chosen with the mean probability, energies reweighted (unbiased)
          let p = 0; for (let b = 0; b < NB; b++) p += sc[Math.min(b, sc.length - 1)]; p = Math.min(0.999, Math.max(0.001, p / NB));
          scat = rnd() < p;
          for (let b = 0; b < NB; b++) { const sb = sc[Math.min(b, sc.length - 1)]; e[b] *= scat ? sb / p : (1 - sb) / (1 - p); }
        } else scat = rnd() < sc;
        if (scat) { // Lambert reflection around the inward normal
          const u1 = rnd(), u2 = rnd(), sq = Math.sqrt(u1), phi = 2 * Math.PI * u2, n0 = s.n;
          const t1 = Math.abs(n0[0]) < 0.9 ? [1, 0, 0] : [0, 1, 0];
          let ax = [n0[1] * t1[2] - n0[2] * t1[1], n0[2] * t1[0] - n0[0] * t1[2], n0[0] * t1[1] - n0[1] * t1[0]]; const al = Math.hypot(...ax); ax = ax.map((v) => v / al);
          const ay = [n0[1] * ax[2] - n0[2] * ax[1], n0[2] * ax[0] - n0[0] * ax[2], n0[0] * ax[1] - n0[1] * ax[0]];
          const a1 = sq * Math.cos(phi), a2 = sq * Math.sin(phi), a3 = Math.sqrt(Math.max(0, 1 - u1));
          const lx = a1 * ax[0] + a2 * ay[0] + a3 * n0[0], ly = a1 * ax[1] + a2 * ay[1] + a3 * n0[1], lz = a1 * ax[2] + a2 * ay[2] + a3 * n0[2];
          if (blend >= 0) {
            const dn = 2 * (dx * n0[0] + dy * n0[1] + dz * n0[2]);
            const mx = blend * lx + (1 - blend) * (dx - dn * n0[0]), my = blend * ly + (1 - blend) * (dy - dn * n0[1]), mz = blend * lz + (1 - blend) * (dz - dn * n0[2]);
            const ml = Math.hypot(mx, my, mz); dx = mx / ml; dy = my / ml; dz = mz / ml;
          } else { dx = lx; dy = ly; dz = lz; }
        } else { const dn = 2 * (dx * s.n[0] + dy * s.n[1] + dz * s.n[2]); dx -= dn * s.n[0]; dy -= dn * s.n[1]; dz -= dn * s.n[2]; }
        last = bi;
      }
    }
    return { H, W, escaped, hits, n, leaked };
  }

  // ---------- loudspeaker directivity (generic, axisymmetric; an engineering assumption, not measured data)
  // cov = nominal -6 dB coverage (full angle, degrees) at and above 2 kHz; the beam widens towards low frequencies,
  // BW(f) = min(360, cov * max(1, (2000 / f)^0.7)): nominal coverage at and above 2 kHz. Amplitude pattern ((1 + cos t) / 2)^n with n set for -6 dB at BW / 2,
  // floor -30 dB. Mean energy over the sphere = 1 / (2n + 1) (used to scale the diffuse part).
  // polar-data directivity (same as brir_proto.load_directivity / _table_amp): tables h, v [band][361] in dB
  // on -180..180 deg, blended cos^2(phi) Lh + sin^2(phi) Lv around the axis; diffuse = 1 / Q from Python
  function tableModel(spec, u) {
    const rn = Math.hypot(u[0], u[1]), rt = rn > 1e-9 ? [u[1] / rn, -u[0] / rn, 0] : [1, 0, 0];   // right = u x z, up = right x u
    const up = [rt[1] * u[2] - rt[2] * u[1], rt[2] * u[0] - rt[0] * u[2], rt[0] * u[1] - rt[1] * u[0]], T = spec.table, floor = Math.pow(10, -30 / 20);
    const at = (row, a) => { const x = Math.max(-180, Math.min(180, a)) + 180, i = Math.min(359, Math.floor(x)), f = x - i; return row[i] + (row[i + 1] - row[i]) * f; };
    if (T.balloon) {   // full-sphere balloon [band][el][az] in dB, 5 deg grid (same as brir_proto._balloon_amp)
      const st = 5, nA = 73, nE = 37;
      return { u, diffuse: T.diffuse, table: true,
        amp(e) { const x = e[0] * u[0] + e[1] * u[1] + e[2] * u[2], y = -(e[0] * rt[0] + e[1] * rt[1] + e[2] * rt[2]), z = e[0] * up[0] + e[1] * up[1] + e[2] * up[2];
          const fa = (Math.atan2(y, x) * 180 / Math.PI + 180) / st, fe = (Math.asin(Math.max(-1, Math.min(1, z))) * 180 / Math.PI + 90) / st;
          const ia = Math.max(0, Math.min(nA - 2, Math.floor(fa))), ie = Math.max(0, Math.min(nE - 2, Math.floor(fe))), ta = fa - ia, te = fe - ie;
          return T.balloon.map((G) => Math.max(floor, Math.pow(10, (G[ie][ia] * (1 - ta) * (1 - te) + G[ie][ia + 1] * ta * (1 - te) + G[ie + 1][ia] * (1 - ta) * te + G[ie + 1][ia + 1] * ta * te) / 20))); } };
    }
    return { u, diffuse: T.diffuse, table: true,
      amp(e) { const ct = Math.max(-1, Math.min(1, e[0] * u[0] + e[1] * u[1] + e[2] * u[2])), th = Math.acos(ct) * 180 / Math.PI;
        const ph = Math.atan2(e[0] * up[0] + e[1] * up[1] + e[2] * up[2], e[0] * rt[0] + e[1] * rt[1] + e[2] * rt[2]), c2 = Math.cos(ph) ** 2;
        const sh = Math.cos(ph) >= 0 ? 1 : -1, sv = Math.sin(ph) >= 0 ? 1 : -1;
        return T.h.map((rowH, b) => Math.max(floor, Math.pow(10, (c2 * at(rowH, sh * th) + (1 - c2) * at(T.v[b], sv * th)) / 20))); } };
  }
  function dirModel(spec, bands) {
    if (!spec) return null;
    const az = (spec.az || 0) * Math.PI / 180, el = (spec.el || 0) * Math.PI / 180;
    const u = [Math.sin(az) * Math.cos(el), -Math.cos(az) * Math.cos(el), Math.sin(el)];
    if (spec.table) return tableModel(spec, u);
    if (!(spec.cov > 0 && spec.cov < 360)) return null;
    const n = bands.map((f) => { const bw = Math.min(360, spec.cov * Math.max(1, Math.pow(2000 / f, 0.7))); if (bw >= 359.9) return 0;
      return Math.log(0.5) / Math.log((1 + Math.cos(bw / 2 * Math.PI / 180)) / 2); });
    const floor = Math.pow(10, -30 / 20);
    return { u, n, diffuse: n.map((v) => 1 / (2 * v + 1)),
      amp(e) { const ct = e[0] * u[0] + e[1] * u[1] + e[2] * u[2], x = (1 + ct) / 2; return n.map((v) => (v === 0 ? 1 : Math.max(floor, Math.pow(Math.max(0, x), v)))); } };
  }

  // ---------- first-order edge diffraction (UTD; same method, constants and order as diffraction.py — see there for
  // the formulas and references: Kouyoumjian & Pathak 1974, Proc. IEEE 62, 1448-1461; Tsingos et al. 2001,
  // doi:10.1145/383259.383323)
  const DF = (() => { const a = []; for (let i = 0; i < 32; i++) a.push(16 * Math.pow(24000 / 16, i / 31)); return a; })();
  const MIN_ANGLE = 2 * Math.PI / 180, SQPI2 = Math.sqrt(Math.PI) / 2, C45 = Math.cos(Math.PI / 4);
  // complex helpers on [re, im]
  const cmul = (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
  function fresnelTail(a) { // int_a^inf exp(-j t^2) dt
    let sr = 0, si = 0, tr = a, ti = 0; const a2 = a * a;
    for (let n = 0; n <= 400; n++) {
      const ar = tr / (2 * n + 1), ai = ti / (2 * n + 1); sr += ar; si += ai;
      if (Math.hypot(ar, ai) < 1e-16 * Math.max(1, Math.hypot(sr, si)) && n > 2) break;
      const k = -a2 / (n + 1); const nr = -ti * k, ni = tr * k; tr = nr; ti = ni;   // term *= -j a2 / (n + 1)
    }
    return [SQPI2 * C45 - sr, -SQPI2 * C45 - si];
  }
  function transition(X) {
    if (X <= 0) return [0, 0];
    if (X > 16) { const x = 1 / X; return [1 - 0.75 * x * x + 6.5625 * x ** 4, 0.5 * x - 1.875 * x ** 3]; }
    const r = Math.sqrt(X), t = fresnelTail(r), p = cmul([-2 * r * Math.sin(X), 2 * r * Math.cos(X)], t); // 2j r e^{jX}
    return p;
  }
  function term(beta, n, kL, sign) {
    const N = Math.round((beta + sign * Math.PI) / (2 * n * Math.PI)), a = 2 * Math.cos((2 * n * Math.PI * N - beta) / 2) ** 2;
    const arg = (Math.PI + sign * beta) / (2 * n);
    if (Math.abs(Math.sin(arg)) < 1e-9) { const eps = Math.PI + sign * (beta - 2 * Math.PI * n * N), m = n * Math.sqrt(2 * Math.PI * kL) * (eps >= 0 ? 1 : -1); return [m * C45, m * C45]; }
    const F = transition(kL * a), ct = 1 / Math.tan(arg); return [F[0] * ct, F[1] * ct];
  }
  function utd(n, phi, phi0, s, s0, sinb, f, c, R0, Rn) {
    const L = s * s0 * sinb * sinb / (s + s0), A = 1 / Math.sqrt(s * s0 * (s + s0)), out = [];
    for (let i = 0; i < f.length; i++) {
      const k = 2 * Math.PI * f[i] / c, kL = k * L;
      const t1 = term(phi - phi0, n, kL, 1), t2 = term(phi - phi0, n, kL, -1), t3 = term(phi + phi0, n, kL, 1), t4 = term(phi + phi0, n, kL, -1);
      const tr = t1[0] + t2[0] + Rn[i] * t3[0] + R0[i] * t4[0], ti = t1[1] + t2[1] + Rn[i] * t3[1] + R0[i] * t4[1];
      const g = -A / (2 * n * Math.sqrt(2 * Math.PI * k) * sinb);       // times exp(-j pi/4)
      const D = cmul([C45 * g, -C45 * g], [tr, ti]); out.push(D);
    }
    return out;
  }
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2], sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const crs = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const nrm = (a) => Math.hypot(a[0], a[1], a[2]);
  function into(s, t, mid) { const u = crs(s.n, t), a = inSurface(s, [mid[0] + 1e-3 * u[0], mid[1] + 1e-3 * u[1], mid[2] + 1e-3 * u[2]]), b = inSurface(s, [mid[0] - 1e-3 * u[0], mid[1] - 1e-3 * u[1], mid[2] - 1e-3 * u[2]]);
    return a && !b ? u : b && !a ? [-u[0], -u[1], -u[2]] : null; }
  function edges(G) {
    const P = [], Q = [], own = [], T = [];
    G.S.forEach((s, k) => { const v = s.verts; for (let i = 0; i < v.length; i++) { const p = v[i], q = v[(i + 1) % v.length], d = sub(q, p), L = nrm(d); if (L > 1e-6) { P.push(p); Q.push(q); own.push(k); T.push([d[0] / L, d[1] / L, d[2] / L]); } } });
    const out = [], cosMin = Math.cos(MIN_ANGLE);
    for (let i = 0; i < P.length; i++) for (let j = i + 1; j < P.length; j++) {
      if (own[j] === own[i] || Math.abs(dot(T[j], T[i])) <= 1 - 1e-7) continue;
      const w = sub(P[j], P[i]), wt = dot(w, T[i]); if (Math.hypot(w[0] - wt * T[i][0], w[1] - wt * T[i][1], w[2] - wt * T[i][2]) >= 1e-6) continue;
      const A = own[i], B = own[j], nA = G.S[A].n, nB = G.S[B].n, cAB = dot(nA, nB);
      if (Math.abs(cAB) > cosMin && cAB > 0) continue;
      const t = T[i], u1 = dot(sub(Q[i], P[i]), t), w0 = dot(sub(P[j], P[i]), t), w1 = dot(sub(Q[j], P[i]), t);
      const lo = Math.max(Math.min(0, u1), Math.min(w0, w1)), hi = Math.min(Math.max(0, u1), Math.max(w0, w1));
      if (hi - lo < 1e-3) continue;
      const mid = [P[i][0] + 0.5 * (lo + hi) * t[0], P[i][1] + 0.5 * (lo + hi) * t[1], P[i][2] + 0.5 * (lo + hi) * t[2]];
      const tA = into(G.S[A], t, mid), tB = into(G.S[B], t, mid); if (!tA || !tB) continue;
      if (dot(tB, nA) >= -1e-9) continue; // concave
      const n = (Math.PI + Math.acos(Math.max(-1, Math.min(1, cAB)))) / Math.PI;
      out.push({ a: [P[i][0] + lo * t[0], P[i][1] + lo * t[1], P[i][2] + lo * t[2]], len: hi - lo, t, i0: A, i1: B, n, t0: tA, n0: nA });
    }
    return out;
  }
  const lerpLog = (xs, ys, x) => { const lx = Math.log(x); if (lx <= Math.log(xs[0])) return ys[0]; if (lx >= Math.log(xs[xs.length - 1])) return ys[ys.length - 1];
    let i = 0; while (Math.log(xs[i + 1]) < lx) i++; const f = (lx - Math.log(xs[i])) / (Math.log(xs[i + 1]) - Math.log(xs[i])); return ys[i] + f * (ys[i + 1] - ys[i]); };
  function reflPartner(G, S, R, k, Rb) {
    const s = G.S[k], side = dot(s.n, S) - s.d; if (side <= 1e-9) return null;
    const I = [S[0] - 2 * side * s.n[0], S[1] - 2 * side * s.n[1], S[2] - 2 * side * s.n[2]], dv = sub(R, I), den = dot(s.n, dv);
    if (Math.abs(den) < 1e-12) return null; const t = (s.d - dot(s.n, I)) / den; if (!(t > 0 && t < 1)) return null;
    const P = [I[0] + t * dv[0], I[1] + t * dv[1], I[2] + t * dv[2]];
    if (!inSurface(s, P) || occluded(G, S, P, k, -1) || occluded(G, P, R, k, -1)) return null;
    return [nrm(dv), Rb];
  }
  // diffracted arrivals at receiver R (same fields as diffraction.diffract; h in the head frame like ism())
  function diffract(G, E, S, R, c, mats, air, bands, tMax) {
    const out = [], BF = bands.map((fc) => { const a = []; for (let i = 0; i < 8; i++) a.push(fc / Math.SQRT2 * Math.pow(2, i / 7)); return a; });
    const direct = !occluded(G, S, R, -1, -1) ? nrm(sub(R, S)) : 0;
    for (const e of E) {
      const t = e.t, a = e.a, vs = sub(S, a), vr = sub(R, a), zs = dot(vs, t), zr = dot(vr, t);
      const ws = [vs[0] - zs * t[0], vs[1] - zs * t[1], vs[2] - zs * t[2]], wr = [vr[0] - zr * t[0], vr[1] - zr * t[1], vr[2] - zr * t[2]], rs = nrm(ws), rr = nrm(wr);
      if (rs < 1e-6 || rr < 1e-6) continue;
      const z = zs + (zr - zs) * rs / (rs + rr); if (z < -1e-9 || z > e.len + 1e-9) continue;
      const Qp = [a[0] + z * t[0], a[1] + z * t[1], a[2] + z * t[2]], s0 = nrm(sub(S, Qp)), s1 = nrm(sub(R, Qp)), L = s0 + s1;
      if (tMax != null && L / c > tMax) continue;
      const ang = (w) => { let x = Math.atan2(dot(w, e.n0), dot(w, e.t0)); if (x < 0) x += 2 * Math.PI; return x; };
      const ph0 = ang(ws), ph = ang(wr); if (ph0 > e.n * Math.PI + 1e-9 || ph > e.n * Math.PI + 1e-9) continue;
      if (occluded(G, S, Qp, e.i0, e.i1) || occluded(G, Qp, R, e.i0, e.i1)) continue;
      const sinb = rs / s0, R0b = mats[G.S[e.i0].mat].R, Rnb = mats[G.S[e.i1].mat].R;
      const Dl = utd(e.n, ph, ph0, s1, s0, sinb, DF, c, DF.map((f) => lerpLog(bands, R0b, f)), DF.map((f) => lerpLog(bands, Rnb, f)));
      const ga = air.map((v) => Math.exp(-0.5 * v * L));
      const partners = []; if (direct) partners.push([direct, bands.map(() => 1)]);
      for (const k of [e.i0, e.i1]) { const p = reflPartner(G, S, R, k, mats[G.S[k].mat].R); if (p) partners.push(p); }
      const eb = [], g = [];
      BF.forEach((fb, b) => {
        const Db = utd(e.n, ph, ph0, s1, s0, sinb, fb, c, fb.map((f) => lerpLog(bands, R0b, f)), fb.map((f) => lerpLog(bands, Rnb, f)));
        let acc = 0, ad = 0;
        fb.forEach((f, i) => { const d2 = Db[i][0] ** 2 + Db[i][1] ** 2; ad += d2; let x = d2;
          for (const [Lp, Gp] of partners) { const gp = Gp[b] / Lp, ph2 = -2 * Math.PI * f * (Lp - L) / c; x += 2 * gp * (Math.cos(ph2) * Db[i][0] + Math.sin(ph2) * Db[i][1]); }
          acc += x; });
        eb.push(acc / fb.length * ga[b] * ga[b]); g.push(Math.sqrt(ad / fb.length) * ga[b]);
      });
      const hw = [(Qp[0] - R[0]) / s1, (Qp[1] - R[1]) / s1, (Qp[2] - R[2]) / s1];
      out.push({ d: L, t: L / c, o: 1, dif: 1, h: [hw[1], -hw[0], hw[2]], e: [(Qp[0] - S[0]) / s0, (Qp[1] - S[1]) / s0, (Qp[2] - S[2]) / s0],
        ga, g, eb, dr: Dl.map((x) => x[0]), di: Dl.map((x) => x[1]) });
    }
    return out;
  }

  return { build, buildMesh, meshColumn, loadObj, objGroups, inside, profAt, inPoly2, ism, rays, occluded, normProfile, dirModel, edges, diffract, transition, utd, DF, FIB, fresnel, panels, specFactor };
})();
if (typeof module !== "undefined") module.exports = GEOM;
