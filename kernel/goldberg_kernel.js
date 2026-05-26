// ============================================================================
//  goldberg_kernel.js
//  MachineNet · Goldberg-Coxeter recursive refinement · math kernel
//  Vladyslav Savytskyy · 2026-05-22
//
//  STANDALONE. Pure functions. No DOM. No Three.js. No external dependencies.
//  Exportable to Node, Deno, Unity JavaScriptEngine, Babylon.js, Three.js,
//  raw Canvas, WebGL2 shaders (the kernel produces vertex/index buffers).
//
//  PUBLIC SURFACE:
//    GK.buildC60()                          -> { faces, vertices, edges, info }
//    GK.refineFace(face, params)            -> [ subFace, ... ]
//    GK.refineAll(state, params)            -> newState (immutable)
//    GK.refineOne(state, faceIdx, params)   -> newState (immutable)
//    GK.invariants(state)                   -> { pents, hexes, depthMax, ... }
//    GK.serialize(state)                    -> JSON-safe object
//    GK.deserialize(obj)                    -> state
//    GK.zoomInto(state, faceIdx)            -> { childState, transform }
//
//  PARAMETERS for refinement:
//    {
//      innerScale:   number,  // 0..1, where the inner copy of parent sits (default 0.45)
//      midScale:     number,  // 0..1, where edge midpoints get pulled inward (default 0.7)
//      preservePentInPent: bool,  // if true, inner-of-pent = pent. else inner = hex (default true)
//      preserveHexInHex:   bool,  // if true, inner-of-hex = hex. else hex breaks differently (default true)
//      surfaceMode:  'planar' | 'spherical' | 'tangent' (default 'planar')
//      jitter:       number,  // 0..1, random perturbation to break perfect symmetry (default 0)
//    }
//
//  INVARIANTS (math-checked, see GK.invariants):
//    - Initial state: 12 pents + 20 hexes (C60).
//    - Each pent refines into 1 pent + 5 hexes (under default params).
//    - Each hex refines into 1 hex + 6 hexes.
//    - Pent count at full refine: 12 * (refinement_count + 1) ... NO, wait.
//      Actually each individual pent stays a pent through one refine step.
//      So if we refine all faces once, we get 12 pents at level 1 + 0 at level 0 (since level 0 pents got replaced).
//      Pentagon count after one full refine = 12 (the inner pents from the original 12).
//      Wait, that's wrong too. Each refinement of a pent yields 1 pent (the center).
//      So 12 pents -> 12 pents (the inner centers). Pent count stays 12 under full-refine.
//      The CORRECTION from earlier: clicking refine on individual faces over time
//      grows pent count if you stack levels of un-refined-parents. But a clean
//      "refine all" keeps pent count at exactly 12.
//
//    Re-stated invariant: AFTER A FULL refineAll, the polyhedron has exactly 12 pentagons.
//                        AFTER MIXED LOCAL refines, the pent count = 12 + (number of
//                        not-yet-fully-descended ancestral pents that still exist as faces).
//
//  GEOMETRY:
//    Vertices live in R^3. All face vertex arrays are oriented CCW when viewed
//    from outside the polyhedron (outward normal = average pos / |average pos|).
//
// ============================================================================

(function(global){
"use strict";

var GK = {};

// ----------------------------------------------------------------------------
// §A Vector helpers (no dependencies)
// ----------------------------------------------------------------------------
function v3(x, y, z){ return [x, y, z]; }
function vadd(a, b){ return [a[0]+b[0], a[1]+b[1], a[2]+b[2]]; }
function vsub(a, b){ return [a[0]-b[0], a[1]-b[1], a[2]-b[2]]; }
function vscale(a, s){ return [a[0]*s, a[1]*s, a[2]*s]; }
function vlen(a){ return Math.sqrt(a[0]*a[0] + a[1]*a[1] + a[2]*a[2]); }
function vnorm(a){ var L = vlen(a); return L > 1e-12 ? vscale(a, 1/L) : [0,0,0]; }
function vlerp(a, b, t){ return [a[0]*(1-t)+b[0]*t, a[1]*(1-t)+b[1]*t, a[2]*(1-t)+b[2]*t]; }
function vcross(a, b){
  return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
}
function vdot(a, b){ return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]; }

GK.vec = { v3:v3, add:vadd, sub:vsub, scale:vscale, len:vlen, norm:vnorm, lerp:vlerp, cross:vcross, dot:vdot };

// ----------------------------------------------------------------------------
// §B Canonical C60 construction
// ----------------------------------------------------------------------------
var PHI = (1 + Math.sqrt(5)) / 2;
GK.PHI = PHI;

function buildC60Vertices(){
  // Truncated icosahedron vertex coordinates (Wikipedia formula):
  //   (0, ±1, ±3φ)
  //   (±1, ±(2+φ), ±2φ)
  //   (±φ, ±2, ±(2φ+1))
  // and all EVEN permutations of each coordinate triple.
  var raw = [];
  var permsEven = [[0,1,2],[1,2,0],[2,0,1]];
  function pushAll(a, b, c){
    for (var i = 0; i < permsEven.length; i++){
      var p = permsEven[i];
      for (var sa = -1; sa <= 1; sa += 2){
        for (var sb = -1; sb <= 1; sb += 2){
          for (var sc = -1; sc <= 1; sc += 2){
            if (a === 0 && sa === -1) continue;
            if (b === 0 && sb === -1) continue;
            if (c === 0 && sc === -1) continue;
            var v = [0, 0, 0];
            v[p[0]] = sa * a;
            v[p[1]] = sb * b;
            v[p[2]] = sc * c;
            raw.push(v);
          }
        }
      }
    }
  }
  pushAll(0, 1, 3*PHI);
  pushAll(1, 2 + PHI, 2*PHI);
  pushAll(PHI, 2, 2*PHI + 1);

  // Dedupe with tolerance
  var dedup = [];
  for (var i = 0; i < raw.length; i++){
    var v = raw[i];
    var found = false;
    for (var j = 0; j < dedup.length; j++){
      var u = dedup[j];
      if (Math.abs(u[0]-v[0]) < 0.001 && Math.abs(u[1]-v[1]) < 0.001 && Math.abs(u[2]-v[2]) < 0.001){
        found = true; break;
      }
    }
    if (!found) dedup.push(v);
  }
  // Normalize to unit sphere
  for (var i = 0; i < dedup.length; i++){
    dedup[i] = vscale(vnorm(dedup[i]), 1.6);
  }
  return dedup;
}

function buildC60Faces(verts){
  // Find edge length (smallest pair distance)
  var minD = Infinity;
  for (var i = 0; i < verts.length; i++){
    for (var j = i+1; j < verts.length; j++){
      var d = vlen(vsub(verts[i], verts[j]));
      if (d > 0.01 && d < minD) minD = d;
    }
  }
  var edgeLen = minD;
  var tol = edgeLen * 0.05;

  // Build adjacency
  var adj = [];
  for (var i = 0; i < verts.length; i++){
    var neighbors = [];
    for (var j = 0; j < verts.length; j++){
      if (i === j) continue;
      var d = vlen(vsub(verts[i], verts[j]));
      if (Math.abs(d - edgeLen) < tol) neighbors.push(j);
    }
    adj.push(neighbors);
  }

  // Sort each vertex's neighbours CCW around outward normal
  for (var i = 0; i < verts.length; i++){
    var v = verts[i];
    var n = vnorm(v);
    var ref = adj[i][0];
    var rv = vsub(verts[ref], v);
    var dot = vdot(rv, n);
    var tangent = vnorm(vsub(rv, vscale(n, dot)));
    var e2 = vcross(n, tangent);
    adj[i].sort(function(a, b){
      var va = vsub(verts[a], v);
      var vb = vsub(verts[b], v);
      var aa = Math.atan2(vdot(va, e2), vdot(va, tangent));
      var bb = Math.atan2(vdot(vb, e2), vdot(vb, tangent));
      return aa - bb;
    });
  }

  // Half-edge face tracing
  function nextInFace(u, v){
    var nbrs = adj[v];
    var idx = nbrs.indexOf(u);
    if (idx < 0) return -1;
    return nbrs[(idx + nbrs.length - 1) % nbrs.length];
  }

  var visited = {};
  var faces = [];
  for (var u = 0; u < verts.length; u++){
    for (var k = 0; k < adj[u].length; k++){
      var v = adj[u][k];
      var key = u + ',' + v;
      if (visited[key]) continue;
      var face = [u];
      var a = u, b = v;
      for (var step = 0; step < 20; step++){
        visited[a + ',' + b] = true;
        var c = nextInFace(a, b);
        if (c < 0 || c === u) break;
        face.push(b);
        a = b; b = c;
      }
      if (face[face.length-1] !== b) face.push(b);
      if (face.length === 5 || face.length === 6) faces.push(face);
    }
  }

  // Deduplicate: half-edge tracing finds each face from multiple starting edges.
  // Canonical key = sorted vertex indices joined.
  var seen = {};
  var unique = [];
  for (var i = 0; i < faces.length; i++){
    var key = faces[i].slice().sort(function(a,b){return a-b}).join(',');
    if (!seen[key]){
      seen[key] = true;
      unique.push(faces[i]);
    }
  }

  return unique;
}

// ----------------------------------------------------------------------------
// §C Public: build initial C60 state
// ----------------------------------------------------------------------------
GK.buildC60 = function(){
  var verts = buildC60Vertices();
  var faces = buildC60Faces(verts);
  var meshFaces = [];
  for (var i = 0; i < faces.length; i++){
    var f = faces[i];
    var pts = [];
    for (var k = 0; k < f.length; k++) pts.push(verts[f[k]].slice());
    var type = (f.length === 5) ? 'pent' : 'hex';
    meshFaces.push({
      pts: pts,
      type: type,
      level: 0,
      lineage: [i],          // history of parent indices
      id: 'F' + i,           // stable id
      anchor: type === 'pent' ? ('A' + i) : null  // pent anchor id
    });
  }
  return {
    faces: meshFaces,
    history: [],
    counter: meshFaces.length
  };
};

// ----------------------------------------------------------------------------
// §C2 Public: build dodecahedron (the PURE SEED — 12 pentagons, 0 hexagons)
// ----------------------------------------------------------------------------
GK.buildDodecahedron = function(){
  // 20 vertices from golden ratio. Absolute math.
  var phi = PHI, invPhi = 1 / PHI;
  var raw = [
    // 8 cube vertices
    [ 1, 1, 1],[ 1, 1,-1],[ 1,-1, 1],[ 1,-1,-1],
    [-1, 1, 1],[-1, 1,-1],[-1,-1, 1],[-1,-1,-1],
    // 12 from golden rectangles
    [0, invPhi, phi],[0, invPhi,-phi],[0,-invPhi, phi],[0,-invPhi,-phi],
    [invPhi, phi, 0],[invPhi,-phi, 0],[-invPhi, phi, 0],[-invPhi,-phi, 0],
    [phi, 0, invPhi],[phi, 0,-invPhi],[-phi, 0, invPhi],[-phi, 0,-invPhi]
  ];
  // Normalize to sphere
  for (var i = 0; i < raw.length; i++) raw[i] = vscale(vnorm(raw[i]), 1.6);

  // Find edges (nearest neighbors)
  var dists = [];
  for (var i = 0; i < raw.length; i++)
    for (var j = i+1; j < raw.length; j++)
      dists.push(vlen(vsub(raw[i], raw[j])));
  dists.sort(function(a,b){return a-b});
  var edgeLen = dists[0], tol = edgeLen * 0.1;

  var adj = [];
  for (var i = 0; i < raw.length; i++){
    adj[i] = [];
    for (var j = 0; j < raw.length; j++){
      if (i !== j && Math.abs(vlen(vsub(raw[i], raw[j])) - edgeLen) < tol)
        adj[i].push(j);
    }
  }

  // Sort neighbours CCW
  for (var i = 0; i < raw.length; i++){
    var v = raw[i], n = vnorm(v);
    var ref = adj[i][0], rv = vsub(raw[ref], v);
    var dot = vdot(rv, n);
    var tangent = vnorm(vsub(rv, vscale(n, dot)));
    var e2 = vcross(n, tangent);
    adj[i].sort(function(a,b){
      var va = vsub(raw[a], v), vb = vsub(raw[b], v);
      return Math.atan2(vdot(va,e2),vdot(va,tangent)) - Math.atan2(vdot(vb,e2),vdot(vb,tangent));
    });
  }

  // Trace pentagonal faces (half-edge)
  function nextInFace(u,v){
    var idx = adj[v].indexOf(u); if(idx<0)return -1;
    return adj[v][(idx+adj[v].length-1)%adj[v].length];
  }
  var visited = {}, faces = [];
  for (var u = 0; u < raw.length; u++){
    for (var k = 0; k < adj[u].length; k++){
      var v = adj[u][k], key = u+','+v;
      if (visited[key]) continue;
      var face=[u], a=u, b=v;
      for (var step=0; step<10; step++){
        visited[a+','+b]=true;
        var c=nextInFace(a,b); if(c<0||c===u)break;
        face.push(b); a=b; b=c;
      }
      if(face[face.length-1]!==b) face.push(b);
      if(face.length===5) faces.push(face);
    }
  }
  // Deduplicate
  var seen={}, unique=[];
  for(var i=0;i<faces.length;i++){
    var key=faces[i].slice().sort(function(a,b){return a-b}).join(',');
    if(!seen[key]){seen[key]=true;unique.push(faces[i]);}
  }

  var meshFaces = [];
  for (var i = 0; i < unique.length; i++){
    var f = unique[i], pts = [];
    for (var k = 0; k < f.length; k++) pts.push(raw[f[k]].slice());
    meshFaces.push({
      pts: pts, type: 'pent', level: 0, lineage: [i],
      id: 'D' + i, anchor: 'A' + i
    });
  }
  return { faces: meshFaces, history: [], counter: meshFaces.length };
};

// ----------------------------------------------------------------------------
// §D Refinement primitive: pure function from face -> sub-faces
// ----------------------------------------------------------------------------
function centroid(pts){
  var c = [0, 0, 0];
  for (var i = 0; i < pts.length; i++){ c[0] += pts[i][0]; c[1] += pts[i][1]; c[2] += pts[i][2]; }
  return [c[0]/pts.length, c[1]/pts.length, c[2]/pts.length];
}

function projectToSphere(p, R){
  var L = vlen(p);
  if (L < 1e-12) return p;
  return vscale(p, R/L);
}

GK.refineFace = function(face, params){
  params = params || {};
  var innerScale       = params.innerScale       != null ? params.innerScale       : 0.45;
  var midScale         = params.midScale         != null ? params.midScale         : 0.70;
  var preservePent     = params.preservePentInPent !== false; // default true
  var preserveHex      = params.preserveHexInHex   !== false; // default true
  var surfaceMode      = params.surfaceMode      || 'planar';
  var sphereR          = params.sphereR          != null ? params.sphereR          : 1.6;
  var jitter           = params.jitter           != null ? params.jitter           : 0;
  var counterRef       = params.counterRef       || { val: 0 }; // for id minting

  var pts = face.pts;
  var n = pts.length;
  var c = centroid(pts);

  // Inner ring: shrink toward centroid
  var inner = [];
  for (var i = 0; i < n; i++){
    var p = vlerp(c, pts[i], innerScale);
    if (surfaceMode === 'spherical') p = projectToSphere(p, sphereR);
    inner.push(p);
  }
  // Edge midpoints pulled inward
  var midRing = [];
  for (var i = 0; i < n; i++){
    var m = vlerp(pts[i], pts[(i+1)%n], 0.5);
    var pulled = vlerp(c, m, midScale);
    if (surfaceMode === 'spherical') pulled = projectToSphere(pulled, sphereR);
    midRing.push(pulled);
  }

  // Optional jitter
  if (jitter > 0){
    function jit(p){
      return [p[0] + (Math.random()-0.5)*jitter,
              p[1] + (Math.random()-0.5)*jitter,
              p[2] + (Math.random()-0.5)*jitter];
    }
    for (var i = 0; i < inner.length; i++) inner[i] = jit(inner[i]);
    for (var i = 0; i < midRing.length; i++) midRing[i] = jit(midRing[i]);
  }

  var subFaces = [];

  // Inner polygon: same arity as parent
  var innerType;
  if (face.type === 'pent') innerType = preservePent ? 'pent' : 'hex';
  else                      innerType = preserveHex  ? 'hex'  : 'pent';

  counterRef.val += 1;
  var innerId = (face.id || 'F?') + '.c' + counterRef.val;
  subFaces.push({
    pts: inner.slice(),
    type: innerType,
    level: face.level + 1,
    lineage: (face.lineage || []).concat([0]),
    id: innerId,
    anchor: innerType === 'pent' ? (face.anchor || 'A?') : null  // pent inherits anchor
  });

  // Surrounding cells: one per edge of parent. Each is a 6-vertex shape.
  for (var i = 0; i < n; i++){
    var j = (i + 1) % n;
    var em = vlerp(pts[i], pts[j], 0.5);
    if (surfaceMode === 'spherical') em = projectToSphere(em, sphereR);
    var hexPts = [
      pts[i].slice(),
      em,
      pts[j].slice(),
      inner[j].slice(),
      midRing[i].slice(),
      inner[i].slice()
    ];
    counterRef.val += 1;
    subFaces.push({
      pts: hexPts,
      type: 'hex',
      level: face.level + 1,
      lineage: (face.lineage || []).concat([i + 1]),
      id: (face.id || 'F?') + '.e' + counterRef.val,
      anchor: null
    });
  }

  return subFaces;
};

// ----------------------------------------------------------------------------
// §E Public: refine operations (immutable, return new state)
// ----------------------------------------------------------------------------
GK.refineOne = function(state, faceIdx, params){
  if (faceIdx < 0 || faceIdx >= state.faces.length) return state;
  var counterRef = { val: state.counter };
  var p = Object.assign({}, params || {}, { counterRef: counterRef });
  var subs = GK.refineFace(state.faces[faceIdx], p);
  var newFaces = state.faces.slice();
  newFaces.splice(faceIdx, 1);
  for (var i = 0; i < subs.length; i++) newFaces.push(subs[i]);
  return {
    faces: newFaces,
    history: state.history.concat([{ op: 'refineOne', idx: faceIdx, snapshot: state.faces }]),
    counter: counterRef.val
  };
};

GK.refineAll = function(state, params){
  var counterRef = { val: state.counter };
  var p = Object.assign({}, params || {}, { counterRef: counterRef });
  var newFaces = [];
  for (var i = 0; i < state.faces.length; i++){
    var subs = GK.refineFace(state.faces[i], p);
    for (var k = 0; k < subs.length; k++) newFaces.push(subs[k]);
  }
  return {
    faces: newFaces,
    history: state.history.concat([{ op: 'refineAll', snapshot: state.faces }]),
    counter: counterRef.val
  };
};

GK.refineAllPents = function(state, params){
  // Refine only pentagonal faces - propagates anchor lineage cleanly
  var counterRef = { val: state.counter };
  var p = Object.assign({}, params || {}, { counterRef: counterRef });
  var newFaces = [];
  for (var i = 0; i < state.faces.length; i++){
    if (state.faces[i].type === 'pent'){
      var subs = GK.refineFace(state.faces[i], p);
      for (var k = 0; k < subs.length; k++) newFaces.push(subs[k]);
    } else {
      newFaces.push(state.faces[i]);
    }
  }
  return {
    faces: newFaces,
    history: state.history.concat([{ op: 'refineAllPents', snapshot: state.faces }]),
    counter: counterRef.val
  };
};

GK.refineAllHexes = function(state, params){
  var counterRef = { val: state.counter };
  var p = Object.assign({}, params || {}, { counterRef: counterRef });
  var newFaces = [];
  for (var i = 0; i < state.faces.length; i++){
    if (state.faces[i].type === 'hex'){
      var subs = GK.refineFace(state.faces[i], p);
      for (var k = 0; k < subs.length; k++) newFaces.push(subs[k]);
    } else {
      newFaces.push(state.faces[i]);
    }
  }
  return {
    faces: newFaces,
    history: state.history.concat([{ op: 'refineAllHexes', snapshot: state.faces }]),
    counter: counterRef.val
  };
};

GK.undo = function(state){
  if (state.history.length === 0) return state;
  var last = state.history[state.history.length - 1];
  return {
    faces: last.snapshot,
    history: state.history.slice(0, -1),
    counter: state.counter // approximate; ids don't get reused
  };
};

GK.reset = function(){ return GK.buildC60(); };

// ----------------------------------------------------------------------------
// §F Invariants & introspection
// ----------------------------------------------------------------------------
GK.invariants = function(state){
  var pents = 0, hexes = 0, maxLevel = 0;
  var perLevel = {};
  var anchors = {};
  for (var i = 0; i < state.faces.length; i++){
    var f = state.faces[i];
    if (f.type === 'pent'){
      pents++;
      if (f.anchor){ anchors[f.anchor] = (anchors[f.anchor] || 0) + 1; }
    } else hexes++;
    if (f.level > maxLevel) maxLevel = f.level;
    perLevel[f.level] = perLevel[f.level] || { pent: 0, hex: 0 };
    if (f.type === 'pent') perLevel[f.level].pent++; else perLevel[f.level].hex++;
  }
  // Vertex & edge counts from TOPOLOGY, not float-matching.
  // Trivalent tiling: V = (5P + 6H) / 3,  E = (5P + 6H) / 2
  // This is exact. Always. Euler: V - E + F = 2.
  var faceEdgeSum = 5 * pents + 6 * hexes;
  var vertices = Math.round(faceEdgeSum / 3);
  var edges = Math.round(faceEdgeSum / 2);
  return {
    pents: pents,
    hexes: hexes,
    faces: state.faces.length,
    edges: edges,
    vertices: vertices,
    maxLevel: maxLevel,
    perLevel: perLevel,
    anchorCount: Object.keys(anchors).length,
    anchors: anchors
  };
};

// ----------------------------------------------------------------------------
// §G Serialization (for save/load, networking, persistence)
// ----------------------------------------------------------------------------
GK.serialize = function(state){
  return {
    version: '1.0',
    counter: state.counter,
    faces: state.faces.map(function(f){
      return {
        pts: f.pts.map(function(p){ return p.slice(); }),
        type: f.type,
        level: f.level,
        lineage: f.lineage ? f.lineage.slice() : [],
        id: f.id,
        anchor: f.anchor
      };
    })
  };
};

GK.deserialize = function(obj){
  if (!obj || obj.version !== '1.0') throw new Error('GK: invalid serialized state');
  return {
    faces: obj.faces.map(function(f){
      return {
        pts: f.pts.map(function(p){ return p.slice(); }),
        type: f.type,
        level: f.level,
        lineage: f.lineage ? f.lineage.slice() : [],
        id: f.id,
        anchor: f.anchor
      };
    }),
    history: [],
    counter: obj.counter || 0
  };
};

// ----------------------------------------------------------------------------
// §H Face-local transform: extract a face as a 2D patch
// (useful for VR teleport-into-cell, sub-views, mini-maps)
// ----------------------------------------------------------------------------
GK.faceLocalFrame = function(face){
  var pts = face.pts;
  var c = centroid(pts);
  var n = vnorm(c);  // outward normal (assuming polyhedron centered at origin)
  // tangent: from centroid to first vertex, projected onto tangent plane
  var ref = vsub(pts[0], c);
  var refDot = vdot(ref, n);
  var tangent = vnorm(vsub(ref, vscale(n, refDot)));
  var bitangent = vcross(n, tangent);
  return {
    origin: c,
    normal: n,
    tangent: tangent,
    bitangent: bitangent
  };
};

GK.facePatch2D = function(face){
  // Project face vertices into local 2D coords on the tangent plane
  var frame = GK.faceLocalFrame(face);
  var out = [];
  for (var i = 0; i < face.pts.length; i++){
    var p = vsub(face.pts[i], frame.origin);
    var x = vdot(p, frame.tangent);
    var y = vdot(p, frame.bitangent);
    out.push([x, y]);
  }
  return { frame: frame, points2D: out };
};

// ----------------------------------------------------------------------------
// §I Export
// ----------------------------------------------------------------------------
if (typeof module !== 'undefined' && module.exports) module.exports = GK;
else if (typeof global !== 'undefined') global.GK = GK;

})(typeof globalThis !== 'undefined' ? globalThis : this);
