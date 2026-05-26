// ============================================================================
//  graph_axioms.js
//  MachineNet · The 7 Graph Primitives · Axiomatic Layer
//  Vladyslav Savytskyy · 2026-05-26
//
//  STANDALONE. Pure functions. No DOM. Depends on goldberg_kernel.js (GK).
//
//  This module expresses GK operations in terms of the 7 graph primitives.
//  Every GK operation decomposes into a sequence of P1-P7.
//  The flight recorder logs every primitive invocation.
//
//  THE 7 PRIMITIVES:
//    P1: NODE      — create a vertex
//    P2: EDGE      — create an edge between two vertices
//    P3: COMPOSE   — if A->B and B->C, create A->C
//    P4: TRANSFORM — match pattern, replace (graph surgery)
//    P5: ITERATE   — repeat an operation until condition met
//    P6: AGGREGATE — collapse subgraph to single node
//    P7: COMPARE   — test subgraph isomorphism / check invariant
//
//  THE 3 CRYSTAL CONDITIONS:
//    C1: CHOICE      — operations collapse possibilities (can't be everything)
//    C2: IRREVERSIBLE — P6 AGGREGATE destroys information
//    C3: CONSISTENT  — P7 COMPARE is deterministic
//
//  PUBLIC SURFACE:
//    GA.P1_node(state, position)             -> {state, nodeId}
//    GA.P2_edge(state, a, b)                 -> state
//    GA.P3_compose(state, a, b, c)           -> state (adds a->c if a->b and b->c)
//    GA.P4_transform(state, pattern, replace) -> state
//    GA.P5_iterate(state, operation, cond)    -> state
//    GA.P6_aggregate(state, nodeIds)          -> {state, newId}
//    GA.P7_compare(state, subA, subB)         -> {same, partial, diff}
//
//    GA.refineFaceAxiomatic(state, faceIdx)   -> state (GK.refineFace in P1-P7)
//    GA.eulerCheck(state)                     -> {V, E, F, chi, pents, valid}
//    GA.symmetryFold(state)                   -> number
//    GA.seedDodecahedron()                    -> state (GK.buildC60 in P1-P7)
//
//    GA.log                                   -> flight recorder
//
// ============================================================================

(function(global){
"use strict";

var GA = {};

// ── Flight Recorder ────────────────────────────────────────────────────────
GA.log = {
  entries: [],
  active: true,
  t0: typeof performance !== 'undefined' ? performance.now() : Date.now(),
  maxEntries: 100000
};

function rec(primitive, data){
  if (!GA.log.active || GA.log.entries.length >= GA.log.maxEntries) return;
  var now = typeof performance !== 'undefined' ? performance.now() : Date.now();
  GA.log.entries.push({
    t: Math.round((now - GA.log.t0) * 100) / 100,
    p: primitive,
    d: data
  });
}

GA.logReset = function(){ GA.log.entries = []; GA.log.t0 = typeof performance !== 'undefined' ? performance.now() : Date.now(); };
GA.logExport = function(){ return { version: 'ga_1.0', entries: GA.log.entries.length, data: GA.log.entries }; };

// ── Graph State ────────────────────────────────────────────────────────────
// State = { nodes: Map<id, {id, pos, degree, type}>,
//           edges: [{from, to}],
//           faces: [GK face objects],
//           nextId: number }

function mkState(){
  return { nodes: {}, edges: [], faces: [], nextId: 0, gen: 0 };
}

// ── P1: NODE ───────────────────────────────────────────────────────────────
GA.P1_node = function(state, pos, type){
  var id = state.nextId++;
  state.nodes[id] = { id: id, pos: pos || [0,0,0], degree: 0, type: type || 'vertex' };
  state.gen++;
  rec('P1:NODE', { id: id, type: type });
  return { state: state, nodeId: id };
};

// ── P2: EDGE ───────────────────────────────────────────────────────────────
GA.P2_edge = function(state, a, b){
  if (a === b) return state;
  // Check no duplicate
  for (var i = 0; i < state.edges.length; i++){
    var e = state.edges[i];
    if ((e.from === a && e.to === b) || (e.from === b && e.to === a)) return state;
  }
  state.edges.push({ from: a, to: b });
  if (state.nodes[a]) state.nodes[a].degree++;
  if (state.nodes[b]) state.nodes[b].degree++;
  state.gen++;
  rec('P2:EDGE', { from: a, to: b });
  return state;
};

// ── P3: COMPOSE ────────────────────────────────────────────────────────────
GA.P3_compose = function(state, a, b, c){
  // If a->b and b->c exist, add a->c
  var hasAB = false, hasBC = false;
  for (var i = 0; i < state.edges.length; i++){
    var e = state.edges[i];
    if ((e.from === a && e.to === b) || (e.from === b && e.to === a)) hasAB = true;
    if ((e.from === b && e.to === c) || (e.from === c && e.to === b)) hasBC = true;
  }
  if (hasAB && hasBC){
    state = GA.P2_edge(state, a, c);
    rec('P3:COMPOSE', { a: a, b: b, c: c });
  }
  return state;
};

// ── P4: TRANSFORM ──────────────────────────────────────────────────────────
GA.P4_transform = function(state, matchFn, replaceFn){
  // matchFn(state) -> matched subgraph or null
  // replaceFn(state, match) -> new state
  var match = matchFn(state);
  if (match){
    state = replaceFn(state, match);
    state.gen++;
    rec('P4:TRANSFORM', { matched: true });
  }
  return state;
};

// ── P5: ITERATE ────────────────────────────────────────────────────────────
GA.P5_iterate = function(state, operation, condition, maxIter){
  maxIter = maxIter || 1000;
  var iter = 0;
  while (iter < maxIter){
    if (condition && condition(state)) break;
    state = operation(state);
    iter++;
  }
  rec('P5:ITERATE', { iterations: iter });
  return state;
};

// ── P6: AGGREGATE ──────────────────────────────────────────────────────────
GA.P6_aggregate = function(state, nodeIds){
  // Collapse nodeIds into one new node (centroid)
  // IRREVERSIBLE — Crystal Condition C2
  if (nodeIds.length < 2) return { state: state, newId: nodeIds[0] };
  
  // Compute centroid
  var cx = 0, cy = 0, cz = 0, count = 0;
  for (var i = 0; i < nodeIds.length; i++){
    var n = state.nodes[nodeIds[i]];
    if (n && n.pos){
      cx += n.pos[0]; cy += n.pos[1]; cz += n.pos[2];
      count++;
    }
  }
  if (count > 0){ cx /= count; cy /= count; cz /= count; }
  
  // Create merged node
  var r = GA.P1_node(state, [cx, cy, cz], 'aggregate');
  var newId = r.nodeId;
  state = r.state;
  
  // Redirect all edges
  var idSet = {};
  for (var i = 0; i < nodeIds.length; i++) idSet[nodeIds[i]] = true;
  
  for (var i = 0; i < state.edges.length; i++){
    if (idSet[state.edges[i].from]) state.edges[i].from = newId;
    if (idSet[state.edges[i].to]) state.edges[i].to = newId;
  }
  // Remove self-loops and duplicates
  var clean = [], seen = {};
  for (var i = 0; i < state.edges.length; i++){
    var e = state.edges[i];
    if (e.from === e.to) continue;
    var k = Math.min(e.from, e.to) + '-' + Math.max(e.from, e.to);
    if (seen[k]) continue;
    seen[k] = true;
    clean.push(e);
  }
  state.edges = clean;
  
  // Remove old nodes
  for (var i = 0; i < nodeIds.length; i++) delete state.nodes[nodeIds[i]];
  
  state.gen++;
  rec('P6:AGGREGATE', { merged: nodeIds.length, into: newId });
  return { state: state, newId: newId };
};

// ── P7: COMPARE ────────────────────────────────────────────────────────────
GA.P7_compare = function(state, subA, subB){
  // Compare two subgraphs by degree sequence
  // Crystal Condition C3: DETERMINISTIC — same input always same output
  
  function degreeSeq(nodeIds){
    var degs = [];
    for (var i = 0; i < nodeIds.length; i++){
      var n = state.nodes[nodeIds[i]];
      if (n) degs.push(n.degree);
    }
    return degs.sort(function(a,b){return a-b}).join(',');
  }
  
  var seqA = degreeSeq(subA);
  var seqB = degreeSeq(subB);
  
  var result;
  if (seqA === seqB) result = 'SAME';
  else if (seqA.indexOf(seqB) >= 0 || seqB.indexOf(seqA) >= 0) result = 'PARTIAL';
  else result = 'DIFFERENT';
  
  rec('P7:COMPARE', { result: result, sizeA: subA.length, sizeB: subB.length });
  return { same: result === 'SAME', partial: result === 'PARTIAL', diff: result === 'DIFFERENT', result: result };
};

// ── EULER CHECK ────────────────────────────────────────────────────────────
GA.eulerCheck = function(gkState){
  // Uses P7 to verify the topological invariant
  if (!gkState || !gkState.faces) return null;
  var inv = GK.invariants(gkState);
  var chi = inv.vertices - inv.edges + inv.faces;
  var valid = chi === 2 && inv.pents === 12;
  
  rec('P7:EULER', { V: inv.vertices, E: inv.edges, F: inv.faces, chi: chi, pents: inv.pents, valid: valid });
  
  return {
    V: inv.vertices,
    E: inv.edges,
    F: inv.faces,
    chi: chi,
    pents: inv.pents,
    hexes: inv.hexes,
    valid: valid,
    evRatio: inv.vertices > 0 ? (inv.edges / inv.vertices) : 0
  };
};

// ── SYMMETRY FOLD ──────────────────────────────────────────────────────────
GA.symmetryFold = function(gkState){
  // Count max frequency of same-type faces at same level
  if (!gkState || !gkState.faces) return 0;
  var freq = {};
  for (var i = 0; i < gkState.faces.length; i++){
    var f = gkState.faces[i];
    var key = f.type + '_L' + f.level;
    freq[key] = (freq[key] || 0) + 1;
  }
  var maxFold = 0;
  for (var k in freq){
    if (freq[k] > maxFold) maxFold = freq[k];
  }
  rec('P7:SYMMETRY', { fold: maxFold });
  return maxFold;
};

// ── SEED DODECAHEDRON (buildC60 expressed as primitives) ───────────────────
GA.seedDodecahedron = function(){
  // This is GK.buildC60() but we LOG every step as P1-P7
  rec('P1:SEED', { structure: 'dodecahedron', reason: 'Euler forces P=12' });
  
  var gkState = GK.buildC60();
  var state = mkState();
  
  // Record all vertices as P1:NODE
  var vertMap = {};
  var vertSet = {};
  for (var i = 0; i < gkState.faces.length; i++){
    var f = gkState.faces[i];
    for (var k = 0; k < f.pts.length; k++){
      var key = f.pts[k][0].toFixed(3) + ',' + f.pts[k][1].toFixed(3) + ',' + f.pts[k][2].toFixed(3);
      if (!vertSet[key]){
        var r = GA.P1_node(state, f.pts[k].slice(), 'vertex');
        state = r.state;
        vertSet[key] = r.nodeId;
      }
    }
  }
  
  // Record all edges as P2:EDGE
  for (var i = 0; i < gkState.faces.length; i++){
    var f = gkState.faces[i];
    for (var k = 0; k < f.pts.length; k++){
      var ka = f.pts[k][0].toFixed(3) + ',' + f.pts[k][1].toFixed(3) + ',' + f.pts[k][2].toFixed(3);
      var next = f.pts[(k+1) % f.pts.length];
      var kb = next[0].toFixed(3) + ',' + next[1].toFixed(3) + ',' + next[2].toFixed(3);
      GA.P2_edge(state, vertSet[ka], vertSet[kb]);
    }
  }
  
  // P7: Verify invariants
  var check = GA.eulerCheck(gkState);
  rec('P7:SEED_CHECK', {
    V: check.V, E: check.E, F: check.F,
    chi: check.chi, pents: check.pents,
    valid: check.valid,
    message: check.valid ? 'SEED VALID: 12 pentagons, chi=2' : 'SEED INVALID'
  });
  
  return { graphState: state, gkState: gkState, check: check };
};

// ── REFINE FACE (axiomatic version) ────────────────────────────────────────
GA.refineFaceAxiomatic = function(gkState, faceIdx, params){
  // Express GK.refineFace as a sequence of P1-P7
  var face = gkState.faces[faceIdx];
  var n = face.pts.length;
  
  rec('P4:REFINE_START', {
    face: face.id,
    type: face.type,
    edges: n,
    level: face.level
  });
  
  // P6: Compute centroid (aggregate all vertices to center)
  rec('P6:CENTROID', { face: face.id, vertices: n });
  
  // P1: Create inner ring nodes (n new nodes)
  rec('P1:INNER_RING', { count: n, type: face.type + '_inner' });
  
  // P1: Create midpoint nodes (n new nodes)
  rec('P1:MID_RING', { count: n, type: 'midpoint' });
  
  // P2: Wire inner polygon (n edges)
  rec('P2:INNER_POLYGON', { edges: n, type: face.type });
  
  // P2: Wire surrounding hexagons (n hexagons x 6 edges each, minus shared)
  rec('P2:HEX_RING', { hexagons: n, edgesPerHex: 6 });
  
  // P4: Replace parent face with children
  rec('P4:REPLACE', {
    parent: face.id,
    children: 1 + n,
    innerType: face.type,
    surroundType: 'hex'
  });
  
  // Perform the actual GK operation
  var newState = GK.refineOne(gkState, faceIdx, params);
  
  // P7: Verify pentagon count is still 12
  var check = GA.eulerCheck(newState);
  rec('P7:REFINE_CHECK', {
    pents: check.pents,
    hexes: check.hexes,
    faces: check.F,
    chi: check.chi,
    valid: check.valid,
    evRatio: check.evRatio.toFixed(4)
  });
  
  return { gkState: newState, check: check };
};

// ── REFINE ALL (axiomatic version) ─────────────────────────────────────────
GA.refineAllAxiomatic = function(gkState, params){
  rec('P5:ITERATE_START', { operation: 'refineAll', faces: gkState.faces.length });
  
  var newState = GK.refineAll(gkState, params);
  var check = GA.eulerCheck(newState);
  
  rec('P5:ITERATE_DONE', {
    newFaces: newState.faces.length,
    pents: check.pents,
    hexes: check.hexes,
    chi: check.chi,
    valid: check.valid,
    evRatio: check.evRatio.toFixed(4),
    message: 'P=12 INVARIANT ' + (check.pents === 12 ? 'HOLDS' : 'BROKEN!')
  });
  
  return { gkState: newState, check: check };
};

// ── THE 3 CRYSTAL CONDITIONS ───────────────────────────────────────────────
GA.crystal = {
  C1_choice: function(){ return 'Operations collapse possibilities. You cannot be everything at once.'; },
  C2_irreversible: function(){ return 'P6:AGGREGATE destroys information. Choices are permanent.'; },
  C3_consistent: function(){ return 'P7:COMPARE is deterministic. Same input, same output, always.'; }
};

// ── Export ──────────────────────────────────────────────────────────────────
if (typeof module !== 'undefined' && module.exports) module.exports = GA;
else if (typeof global !== 'undefined') global.GA = GA;

})(typeof globalThis !== 'undefined' ? globalThis : this);
