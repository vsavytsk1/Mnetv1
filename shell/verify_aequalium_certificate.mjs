#!/usr/bin/env node
// verify_aequalium_certificate.mjs — AEQUALIUM v2.4 external oracle
// -----------------------------------------------------------------------------
// Independent verifier for schema "aequalium-certificate/2".
// LAW: shares NO code with the generator. Every check below is re-implemented
// from the documented schema alone: base64, mesh decoding, topology enumeration
// from integer face rings, fan triangulation, signed volume, self-intersection,
// SHA-256 hashes (node:crypto), and Fourier replay from the embedded samples.
// Usage:  node verify_aequalium_certificate.mjs certificate.json
// -----------------------------------------------------------------------------
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const path = process.argv[2];
if (!path) { console.error('usage: node verify_aequalium_certificate.mjs cert.json'); process.exit(2); }
const cert = JSON.parse(readFileSync(path, 'utf8'));

let failures = 0;
function report(ok, name, detail = '') {
  console.log((ok ? 'PASS' : 'FAIL') + ' ' + name + (detail ? '   ' + detail : ''));
  if (!ok) failures++;
}

// ---------- own base64 ----------
function unb64(str) {
  const C = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  const map = {}; for (let i = 0; i < 64; i++) map[C[i]] = i;
  const clean = str.replace(/=+$/, ''); const out = [];
  for (let i = 0; i < clean.length; i += 4) {
    const a = map[clean[i]], b = map[clean[i + 1]], c = map[clean[i + 2]], d = map[clean[i + 3]];
    out.push((a << 2) | (b >> 4));
    if (c !== undefined) out.push(((b & 15) << 4) | (c >> 2));
    if (d !== undefined) out.push(((c & 3) << 6) | d);
  }
  return new Uint8Array(out);
}
const sha256 = (u8) => createHash('sha256').update(u8).digest('hex');

// ---------- 1. schema ----------
report(cert.schema === 'aequalium-certificate/2', 'schema', String(cert.schema));

// ---------- 2. hashes ----------
if (!cert.mesh || !cert.mesh.indexedData) { report(false, 'mesh present'); finish(); }
const meshBytes = unb64(cert.mesh.indexedData);
report(sha256(meshBytes) === cert.mesh.sha256, 'mesh sha256');
let sampBytes = null;
if (cert.target && cert.target.samples) {
  sampBytes = unb64(cert.target.samples);
  report(sha256(sampBytes) === cert.target.samplesSha256, 'target sha256');
}
console.log('SKIP kernelSha256 (generator-side identity; not independently derivable)');

// ---------- 3. own mesh decode: [V,F,gen]u32 | ragged faces u32 | positions f64 ----------
const dv = new DataView(meshBytes.buffer, meshBytes.byteOffset, meshBytes.byteLength);
const V = dv.getUint32(0, true), F = dv.getUint32(4, true);
let off = 12; const faces = [];
for (let i = 0; i < F; i++) {
  const n = dv.getUint32(off, true); off += 4;
  const r = []; for (let j = 0; j < n; j++) { r.push(dv.getUint32(off, true)); off += 4; }
  faces.push(r);
}
const P = new Float64Array(V * 3);
for (let i = 0; i < V * 3; i++) { P[i] = dv.getFloat64(off, true); off += 8; }
report(off === meshBytes.byteLength, 'mesh byte length consistent');

// ---------- 4. topology enumeration from IDs alone ----------
const dmap = new Map(); let orientFail = 0, HE = 0;
const heO = [], heD = [];
for (let i = 0; i < F; i++) {
  const r = faces[i], n = r.length;
  for (let j = 0; j < n; j++) {
    const a = r[j], b = r[(j + 1) % n], k = a + '_' + b;
    if (dmap.has(k)) orientFail++; else dmap.set(k, HE);
    heO.push(a); heD.push(b); HE++;
  }
}
let twinMiss = 0; const useen = new Set(); let E = 0;
for (let i = 0; i < HE; i++) {
  const a = heO[i], b = heD[i];
  if (!dmap.has(b + '_' + a)) twinMiss++;
  const uk = a < b ? a + '_' + b : b + '_' + a;
  if (!useen.has(uk)) { useen.add(uk); E++; }
}
report(V === cert.certificates.topology.V && E === cert.certificates.topology.E &&
       F === cert.certificates.topology.F, 'V/E/F enumeration', `V=${V} E=${E} F=${F}`);
report(twinMiss === 0, 'twin pairing', twinMiss + ' missing');
report(orientFail === 0, 'orientation (no repeated directed edge)');
// strict vertex links via next∘twin
const nextArr = new Int32Array(HE); { let base = 0;
  for (let i = 0; i < F; i++) { const n = faces[i].length;
    for (let j = 0; j < n; j++) nextArr[base + j] = base + (j + 1) % n; base += n; } }
const out = Array.from({ length: V }, () => []);
for (let i = 0; i < HE; i++) out[heO[i]].push(i);
let badLinks = 0, deg3 = 0;
if (twinMiss === 0 && orientFail === 0) {
  const startOf = new Int32Array(V).fill(-1);
  for (let h = 0; h < HE; h++) if (startOf[heO[h]] < 0) startOf[heO[h]] = h;
  for (let v = 0; v < V; v++) {
    const d = out[v].length; if (d === 3) deg3++;
    let h = startOf[v], seen = 0, guard = 0;
    do { seen++; h = nextArr[dmap.get(heD[h] + '_' + heO[h])]; } while (h !== startOf[v] && ++guard < 64);
    if (seen !== d) badLinks++;
  }
} else badLinks = -1;
report(badLinks === 0, 'vertex links single-cycle', String(badLinks));
report(deg3 === V, 'degree-3 everywhere', Math.round(100 * deg3 / V) + '%');
// connectivity
{ const adj = Array.from({ length: V }, () => []);
  for (const uk of useen) { const [a, b] = uk.split('_').map(Number); adj[a].push(b); adj[b].push(a); }
  const seen = new Uint8Array(V); let comp = 0;
  for (let i = 0; i < V; i++) if (!seen[i]) { comp++; const st = [i]; seen[i] = 1;
    while (st.length) { const u = st.pop(); for (const w of adj[u]) if (!seen[w]) { seen[w] = 1; st.push(w); } } }
  report(comp === 1, 'connectivity', comp + ' component(s)'); }
const chi = V - E + F;
report(chi === 2, 'chi = V - E + F', String(chi));
{ let P5 = 0, H6 = 0, other = 0;
  for (const r of faces) (r.length === 5 ? P5++ : r.length === 6 ? H6++ : other++);
  report(P5 === 12 && other === 0, 'face inventory', `P=${P5} H=${H6} other=${other}`); }

// ---------- 5. own geometry: fan triangulation, volume, self-intersection ----------
const tris = [];
for (const r of faces) for (let j = 1; j < r.length - 1; j++) tris.push(r[0], r[j], r[j + 1]);
const T = tris.length / 3;
let minE = 1e99, minA = 1e99, vol = 0, finite = true;
for (let i = 0; i < P.length; i++) if (!Number.isFinite(P[i])) finite = false;
for (let t = 0; t < T; t++) {
  const a = tris[3 * t], b = tris[3 * t + 1], c = tris[3 * t + 2];
  const ux = P[3 * b] - P[3 * a], uy = P[3 * b + 1] - P[3 * a + 1], uz = P[3 * b + 2] - P[3 * a + 2];
  const wx = P[3 * c] - P[3 * a], wy = P[3 * c + 1] - P[3 * a + 1], wz = P[3 * c + 2] - P[3 * a + 2];
  minE = Math.min(minE, Math.hypot(ux, uy, uz), Math.hypot(wx, wy, wz));
  minA = Math.min(minA, Math.hypot(uy * wz - uz * wy, uz * wx - ux * wz, ux * wy - uy * wx) / 2);
  vol += (P[3 * a] * (P[3 * b + 1] * P[3 * c + 2] - P[3 * b + 2] * P[3 * c + 1])
        - P[3 * a + 1] * (P[3 * b] * P[3 * c + 2] - P[3 * b + 2] * P[3 * c])
        + P[3 * a + 2] * (P[3 * b] * P[3 * c + 1] - P[3 * b + 1] * P[3 * c])) / 6;
}
report(finite && minE > 1e-9 && minA > 1e-12, 'triangulated geometry',
       `tris=${T} minEdge=${minE.toExponential(1)} minArea=${minA.toExponential(1)}`);
report(vol > 0, 'signed volume', vol.toFixed(4));
// grid-bucketed tri-tri
function segTri(p, q, tp) {
  const e1 = [tp[1][0] - tp[0][0], tp[1][1] - tp[0][1], tp[1][2] - tp[0][2]];
  const e2 = [tp[2][0] - tp[0][0], tp[2][1] - tp[0][1], tp[2][2] - tp[0][2]];
  const d = [q[0] - p[0], q[1] - p[1], q[2] - p[2]];
  const h = [d[1] * e2[2] - d[2] * e2[1], d[2] * e2[0] - d[0] * e2[2], d[0] * e2[1] - d[1] * e2[0]];
  const det = e1[0] * h[0] + e1[1] * h[1] + e1[2] * h[2];
  if (Math.abs(det) < 1e-14) return false;
  const f = 1 / det, s = [p[0] - tp[0][0], p[1] - tp[0][1], p[2] - tp[0][2]];
  const u = f * (s[0] * h[0] + s[1] * h[1] + s[2] * h[2]); if (u < 1e-9 || u > 1 - 1e-9) return false;
  const qv = [s[1] * e1[2] - s[2] * e1[1], s[2] * e1[0] - s[0] * e1[2], s[0] * e1[1] - s[1] * e1[0]];
  const v = f * (d[0] * qv[0] + d[1] * qv[1] + d[2] * qv[2]); if (v < 1e-9 || u + v > 1 - 1e-9) return false;
  const tt = f * (e2[0] * qv[0] + e2[1] * qv[1] + e2[2] * qv[2]);
  return tt > 1e-9 && tt < 1 - 1e-9;
}
const tp = (t) => [0, 1, 2].map(k => [P[3 * tris[3 * t + k]], P[3 * tris[3 * t + k] + 1], P[3 * tris[3 * t + k] + 2]]);
let sumExt = 0; const aabb = [];
for (let t = 0; t < T; t++) {
  const A = tp(t);
  const mn = [0, 1, 2].map(k => Math.min(A[0][k], A[1][k], A[2][k]));
  const mx = [0, 1, 2].map(k => Math.max(A[0][k], A[1][k], A[2][k]));
  aabb.push([...mn, ...mx]);
  sumExt += Math.max(mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2]);
}
const cell = Math.max(1e-6, 2.2 * sumExt / Math.max(1, T)), grid = new Map();
for (let t = 0; t < T; t++) {
  const A = aabb[t];
  for (let gx = Math.floor(A[0] / cell); gx <= Math.floor(A[3] / cell); gx++)
  for (let gy = Math.floor(A[1] / cell); gy <= Math.floor(A[4] / cell); gy++)
  for (let gz = Math.floor(A[2] / cell); gz <= Math.floor(A[5] / cell); gz++) {
    const k = gx + '_' + gy + '_' + gz;
    if (!grid.has(k)) grid.set(k, []); grid.get(k).push(t);
  }
}
const share = (t1, t2) => { for (let i = 0; i < 3; i++) for (let j = 0; j < 3; j++)
  if (tris[3 * t1 + i] === tris[3 * t2 + j]) return true; return false; };
let inter = 0; const tested = new Set();
outer: for (const lst of grid.values())
  for (let i = 0; i < lst.length; i++) for (let j = i + 1; j < lst.length; j++) {
    const t1 = lst[i], t2 = lst[j], pk = t1 < t2 ? t1 * 1e6 + t2 : t2 * 1e6 + t1;
    if (tested.has(pk)) continue; tested.add(pk);
    if (share(t1, t2)) continue;
    const A = aabb[t1], B = aabb[t2];
    if (A[3] < B[0] || B[3] < A[0] || A[4] < B[1] || B[4] < A[1] || A[5] < B[2] || B[5] < A[2]) continue;
    const TA = tp(t1), TB = tp(t2);
    let hit = false;
    for (let e = 0; e < 3 && !hit; e++)
      hit = segTri(TA[e], TA[(e + 1) % 3], TB) || segTri(TB[e], TB[(e + 1) % 3], TA);
    if (hit && ++inter > 8) break outer;
  }
report(inter === 0, 'no self-intersections', String(inter));

// ---------- 6. Fourier replay from embedded samples ----------
if (sampBytes) {
  const flat = new Float64Array(sampBytes.buffer, sampBytes.byteOffset, sampBytes.byteLength / 8);
  const M = cert.target.M, K = cert.fourier.K, twoPi = 2 * Math.PI;
  const cr = new Float64Array(2 * K + 1), ci = new Float64Array(2 * K + 1);
  for (let k = -K; k <= K; k++) {
    let sr = 0, si = 0;
    for (let m = 0; m < M; m++) {
      const t = twoPi * m / M, re = flat[2 * m], im = flat[2 * m + 1];
      const cw = Math.cos(k * t), sw = Math.sin(k * t);
      sr += re * cw + im * sw; si += im * cw - re * sw;
    }
    cr[k + K] = sr / M; ci[k + K] = si / M;
  }
  const rec = (t) => { let re = 0, im = 0;
    for (let k = -K; k <= K; k++) { const cw = Math.cos(k * t), sw = Math.sin(k * t);
      re += cr[k + K] * cw - ci[k + K] * sw; im += cr[k + K] * sw + ci[k + K] * cw; }
    return [re, im]; };
  let s1 = 0, n1 = 0;
  for (let m = 0; m < M; m++) { const t = twoPi * m / M, r = rec(t);
    const ex = r[0] - flat[2 * m], ey = r[1] - flat[2 * m + 1];
    s1 += ex * ex + ey * ey; n1 += flat[2 * m] ** 2 + flat[2 * m + 1] ** 2; }
  const MV = 2 * M; let s2 = 0, n2 = 0, li = 0;
  for (let m = 0; m < MV; m++) {
    const t = twoPi * (m + 0.5) / MV, r = rec(t);
    const i0 = Math.floor(t / twoPi * M) % M, i1 = (i0 + 1) % M, fr = t / twoPi * M - i0;
    const gr = flat[2 * i0] * (1 - fr) + flat[2 * i1] * fr;
    const gi = flat[2 * i0 + 1] * (1 - fr) + flat[2 * i1 + 1] * fr;
    const ex = r[0] - gr, ey = r[1] - gi, e = Math.hypot(ex, ey);
    s2 += ex * ex + ey * ey; n2 += gr * gr + gi * gi; if (e > li) li = e;
  }
  const fit = Math.sqrt(s1 / Math.max(1e-12, n1)), val = Math.sqrt(s2 / Math.max(1e-12, n2));
  const tol = (a, b) => Math.abs(a - b) < 1e-6 + 1e-6 * Math.abs(b);
  report(tol(fit, cert.fourier.fitL2) && tol(val, cert.fourier.validationL2),
         'Fourier replay', `fit ${fit.toFixed(7)} vs ${cert.fourier.fitL2.toFixed(7)} · val ${val.toFixed(7)} vs ${cert.fourier.validationL2.toFixed(7)} · Linf ${li.toFixed(4)}`);
} else console.log('SKIP Fourier replay (no samples embedded)');

finish();
function finish() {
  console.log(failures === 0 ? 'CERTIFICATE VALID' : `CERTIFICATE INVALID (${failures} failure${failures === 1 ? '' : 's'})`);
  process.exit(failures === 0 ? 0 : 1);
}
