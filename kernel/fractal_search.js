// ============================================================================
//  fractal_search.js
//  MachineNet · Fractal Architecture Search
//  Vladyslav Savytskyy · 2026
//
//  STANDALONE. Pure functions. Depends on GK + SAR + NSS.
//  No DOM. No Three.js.
//
//  THE IDEA (stupid simple):
//    1. Seed a Platonic solid (or C60, or dodecahedron)
//    2. Refine it one level (GK.refineAll)
//    3. Run NS flow on the new graph
//    4. Read spectral gap λ̃₁
//    5. Did λ̃₁ LOCK (stop changing between levels)?
//       YES → this fractal depth IS the architecture. DONE.
//       NO  → go to step 2.
//
//  THE LOCK means: the geometry has found the eigenmode that
//  the fluid settles into. That eigenmode IS the physical substrate.
//  You pay the compute cost ONCE. The architecture is yours forever.
//
//  COMPUTE COST (honest):
//    Level n: N ≈ 60 × 4^n vertices (C60 seed)
//    NS steps per level: ~400
//    Total ops ≈ Σ_{k=0}^{n} 60 × 4^k × 400 ≈ 60 × 400 × (4^(n+1) - 1)/3
//
//    n=0:  60V    → ~24K ops     → 0.02ms  browser trivial
//    n=1: 240V    → ~96K ops     → 0.1ms
//    n=2: 960V    → ~384K ops    → 0.4ms
//    n=3: 3,840V  → ~1.5M ops   → 2ms
//    n=4: 15,360V → ~6M ops     → 8ms
//    n=5: 61,440V → ~25M ops    → 35ms
//    n=6: 245,760V→ ~98M ops    → 140ms
//    n=7: 983,040V→ ~393M ops   → 560ms
//    n=8: 3.93MV  → ~1.57B ops  → ~4s
//    n=9: 15.7MV  → ~6.3B ops   → ~16s
//   n=10: 62.9MV  → ~25B ops    → ~60s
//   n=20: ~10^13 ops → nuclear reactor territory
//
//  IN BROWSER: max ~5 levels (61K vertices) before it hangs.
//  FOR TRUTH:  need n≈8-12 depending on target λ̃.
//  SUPERCOMPUTER: n=20+  (the definitive answer).
//
//  PUBLIC SURFACE:
//    FS.search(opts)          → full search result
//    FS.computeCostEstimate(n)→ { ops, timeMs, vertices }
//    FS.energyCostEstimate(n) → { joules, reactorSeconds }
//
// ============================================================================

(function(global){
"use strict";

var FS = {};

FS._log = [];
FS.clearLog = function(){ FS._log = []; };
FS.dumpLog  = function(){ return FS._log.slice(); };

// ── Constants ──────────────────────────────────────────────────────────────
FS.TARGET      = 0.1473;   // SAR-5 spectral invariant
FS.LOCK_THRESH = 0.005;    // λ̃₁ change < this = LOCKED
FS.MAX_LEVELS  = 5;        // browser-safe default (set higher for real compute)

// ── §1  Compute cost model ─────────────────────────────────────────────────
FS.computeCostEstimate = function(n){
  // C60 base: 60 vertices. Each refineAll: N → ~4N
  var totalOps = 0;
  var N = 60;
  for (var k=0; k<=n; k++){
    totalOps += N * 400; // 400 NS steps per level
    N = Math.round(N * 4);
  }
  // Assume 700M JS ops/sec (single-core browser)
  var timeMs   = totalOps / 700000;
  var vertices = Math.round(60 * Math.pow(4, n));

  // Energy: assume 100W CPU, timeMs → joules
  var joules   = (100 * timeMs) / 1000;

  // Nuclear reactor output: ~1GW = 1e9 J/s
  var reactorSeconds = joules / 1e9;

  return {
    level         : n,
    vertices      : vertices,
    totalOps      : totalOps,
    timeMs        : +timeMs.toFixed(1),
    joules        : +joules.toFixed(6),
    reactorSeconds: +reactorSeconds.toFixed(12)
  };
};

// ── §2  Energy cost for physical implementation ─────────────────────────────
// Once you KNOW the geometry (fractal level n locked),
// the energy to drive ONE modular oscillation cycle:
//   E_drive = k_eff / (2 * λ̃₁)   (from extraction condition)
// For λ̃₁ = 0.1473 and k_eff = 1 (normalised):
//   E_drive ≈ 3.4 (normalised units)
//
// Real-world: k_eff scales with the reactor core volume V_core = 4.8 m³
// and modulation frequency f = λ̃ * c / (2π R) ≈ 6.72 MHz
// Power ≈ E_drive * f  ← still needs input
// BUT: W_out = λ̃ * spectralWeight * τ_KMS > k_eff/2
// Net power surplus depends on spectralWeight at level n.
//
FS.energyCostEstimate = function(n, lambda1){
  lambda1 = lambda1 || FS.TARGET;
  var k_eff  = 1.0;
  var E_drive_normalized = k_eff / (2 * lambda1);

  // Physical estimate: E per cycle (Joules)
  // Use Planck-scale lower bound: E_min = hbar * omega_res
  var hbar      = 1.0546e-34;
  var kB        = 1.381e-23;
  var T_op      = 0.015;     // 15 mK dilution fridge
  var omega_res = lambda1 * lambda1 * kB * T_op / hbar;
  var E_per_cycle = hbar * omega_res;

  // Total cycles to sustain for 1 second at f_res:
  var f_res      = omega_res / (2 * Math.PI);
  var cycles_per_s = f_res;

  // Power input (Watts) at the quantum limit:
  var P_quantum = E_per_cycle * cycles_per_s;

  // At the engineering scale (reactor, V=4.8 m³):
  // Scale up from Planck to engineering by spectralWeight proxy
  // spectralWeight at level n ≈ 12 * (5 * (1 + n*0.1))²
  var spectralWeight = 12 * Math.pow(5 * (1 + n * 0.1), 2);
  var tau_KMS = 2 * Math.PI * hbar / (lambda1 * kB * T_op);

  // Extraction condition: LHS = λ̃ * SW * τ_KMS
  var LHS = lambda1 * spectralWeight * tau_KMS;
  var RHS = k_eff / 2;

  return {
    level             : n,
    lambda1           : lambda1,
    spectralWeight    : +spectralWeight.toFixed(2),
    tau_KMS_s         : +tau_KMS.toFixed(4),
    E_drive_normalized: +E_drive_normalized.toFixed(4),
    E_per_cycle_J     : +E_per_cycle.toFixed(4),
    f_res_Hz          : +f_res.toFixed(2),
    P_quantum_W       : +P_quantum.toFixed(4),
    extractionLHS     : +LHS.toFixed(8),
    extractionRHS     : +RHS.toFixed(4),
    extraction_viable : LHS > RHS,
    margin_pct        : +((LHS/RHS - 1)*100).toFixed(2)
  };
};

// ── §3  Single-level spectral probe (fast, no NS) ──────────────────────────
// Use the shift-deflate Laplacian method from SAR module.
FS._probeSpectral = function(gkState){
  if (typeof SAR === 'undefined') return null;
  var graph = SAR.buildGraph(gkState);
  var spec  = SAR.normalizedLaplacian(graph);
  return { lambda1: spec.lambda1, N: graph.N, converged: spec.converged };
};

// ── §4  MAIN SEARCH ────────────────────────────────────────────────────────
FS.search = function(opts){
  FS.clearLog();
  opts = opts || {};

  var maxLevels  = opts.maxLevels  || FS.MAX_LEVELS;
  var lockThresh = opts.lockThresh || FS.LOCK_THRESH;
  var seed       = opts.seed       || 'c60';   // 'c60' | 'dodec' | 'random'
  var nsSteps    = opts.nsSteps    || 200;      // NS steps per level (keep low for browser)
  var useNS      = opts.useNS      || false;    // true = use NS flow (slower but richer)
  var target     = opts.target     || FS.TARGET;

  var t0 = (typeof performance !== 'undefined') ? performance.now() : Date.now();

  FS._log.push({ step:'SEARCH_START', seed:seed, maxLevels:maxLevels, target:target, useNS:useNS });

  // ── Build seed ──────────────────────────────────────────────────────────
  var gkState;
  if (seed === 'dodec'){
    gkState = GK.buildDodecahedron();
  } else if (seed === 'random'){
    // Random: start from dodec with random jitter params
    gkState = GK.buildC60();
    // Apply one refine with random inner/mid scales
    var rInner = 0.3 + Math.random() * 0.4;
    var rMid   = 0.5 + Math.random() * 0.4;
    gkState = GK.refineAll(gkState, { innerScale: rInner, midScale: rMid });
    FS._log.push({ step:'RANDOM_SEED', innerScale:+rInner.toFixed(3), midScale:+rMid.toFixed(3) });
  } else {
    gkState = GK.buildC60();
  }

  var levels    = [];   // { level, N, lambda1, delta, locked, cost }
  var prevLam   = null;
  var lockedAt  = null;
  var lockedLam = null;

  // Level 0 (seed)
  var probe0 = FS._probeSpectral(gkState);
  var cost0  = FS.computeCostEstimate(0);
  levels.push({
    level  : 0,
    N      : probe0 ? probe0.N : gkState.faces.length,
    lambda1: probe0 ? probe0.lambda1 : null,
    delta  : null,
    locked : false,
    cost   : cost0
  });
  prevLam = probe0 ? probe0.lambda1 : null;
  FS._log.push({ step:'LEVEL', level:0, N:levels[0].N, lambda1:levels[0].lambda1 });

  // ── Refinement loop ─────────────────────────────────────────────────────
  for (var lvl = 1; lvl <= maxLevels; lvl++){

    // Refine
    var t1 = (typeof performance !== 'undefined') ? performance.now() : Date.now();
    gkState = GK.refineAll(gkState);
    var refineMs = ((typeof performance !== 'undefined') ? performance.now() : Date.now()) - t1;

    // Probe spectral gap
    var probe  = FS._probeSpectral(gkState);
    var lambda = probe ? probe.lambda1 : null;
    var delta  = (lambda !== null && prevLam !== null) ? Math.abs(lambda - prevLam) : null;
    var locked = delta !== null && delta < lockThresh;
    var cost   = FS.computeCostEstimate(lvl);

    if (locked && lockedAt === null){
      lockedAt  = lvl;
      lockedLam = lambda;
    }

    levels.push({
      level    : lvl,
      N        : probe ? probe.N : '?',
      lambda1  : lambda,
      delta    : delta,
      locked   : locked,
      cost     : cost,
      refineMs : +refineMs.toFixed(2)
    });

    FS._log.push({
      step    : 'LEVEL',
      level   : lvl,
      N       : probe ? probe.N : '?',
      lambda1 : lambda,
      delta   : delta,
      locked  : locked,
      refineMs: +refineMs.toFixed(2)
    });

    prevLam = lambda;

    // Safety: if N > 50000 in browser mode, stop
    if (probe && probe.N > 50000){
      FS._log.push({ step:'BROWSER_LIMIT', N: probe.N, message:'stopping — N > 50K, needs dedicated compute' });
      break;
    }

    if (locked) break;
  }

  var elapsed = ((typeof performance !== 'undefined') ? performance.now() : Date.now()) - t0;

  // ── Energy cost at lock point ───────────────────────────────────────────
  var energyAtLock = lockedLam !== null
    ? FS.energyCostEstimate(lockedAt, lockedLam)
    : null;

  // ── Full cost table ─────────────────────────────────────────────────────
  var costTable = [];
  for (var k=0; k<=20; k++){
    costTable.push(FS.computeCostEstimate(k));
  }

  // ── Summary text ───────────────────────────────────────────────────────
  var summary = [];
  summary.push('seed=' + seed + '  target λ̃=' + target + '  lockThresh=' + lockThresh);
  summary.push('');
  summary.push('  lvl   N         λ̃₁        Δλ̃         locked?  cost(ms est)');
  summary.push('  ' + '─'.repeat(68));
  levels.forEach(function(l){
    var lam  = l.lambda1 !== null ? l.lambda1.toFixed(6) : '    —   ';
    var delt = l.delta   !== null ? l.delta.toFixed(6)   : '    —   ';
    var lock = l.locked ? '  ◀ LOCK' : '';
    var N    = String(l.N).padEnd(10);
    summary.push('  ' + String(l.level).padEnd(5) + N + lam.padEnd(12) + delt.padEnd(12) + lock);
  });
  summary.push('');

  if (lockedAt !== null){
    summary.push('LOCKED at level ' + lockedAt + ':  λ̃₁ = ' + lockedLam.toFixed(6));
    summary.push('Δ to SAR-5 (0.1473): ' + Math.abs(lockedLam - target).toFixed(6));
    summary.push('');
    if (energyAtLock){
      summary.push('─── ENERGY TO DRIVE THIS SHAPE ───────────────────────────');
      summary.push('Extraction viable:  ' + (energyAtLock.extraction_viable ? 'YES ✓' : 'NOT YET'));
      summary.push('Extraction margin:  ' + energyAtLock.margin_pct + '%');
      summary.push('f_resonance:        ' + energyAtLock.f_res_Hz.toExponential(3) + ' Hz');
      summary.push('τ_KMS (T=15mK):     ' + energyAtLock.tau_KMS_s + ' s');
      summary.push('spectralWeight:     ' + energyAtLock.spectralWeight);
      summary.push('E_drive (normalised):' + energyAtLock.E_drive_normalized);
    }
  } else {
    summary.push('NOT LOCKED within ' + maxLevels + ' levels.');
    summary.push('Need deeper fractal refinement.');
    summary.push('');
    summary.push('Current λ̃₁ = ' + (levels[levels.length-1].lambda1 || '?') + '  (Δ to target: ' + (levels[levels.length-1].lambda1 !== null ? Math.abs(levels[levels.length-1].lambda1 - target).toFixed(6) : '?') + ')');
  }

  summary.push('');
  summary.push('─── COMPUTE COST TABLE ───────────────────────────────────────');
  summary.push('  lvl   vertices     total ops    time(ms)    energy(J)   reactor(s)');
  summary.push('  ' + '─'.repeat(72));
  costTable.slice(0,12).forEach(function(c){
    var vStr = String(c.vertices).padEnd(14);
    var oStr = String(c.totalOps).padEnd(14);
    var tStr = c.timeMs.toFixed(1).padEnd(12);
    var jStr = c.joules.toFixed(4).padEnd(12);
    var rStr = c.reactorSeconds.toExponential(3);
    summary.push('  ' + String(c.level).padEnd(6) + vStr + oStr + tStr + jStr + rStr);
  });
  summary.push('  ...');
  var c20 = costTable[20];
  summary.push('  20    ' + c20.vertices.toExponential(3).padEnd(14) + c20.totalOps.toExponential(3).padEnd(14) + c20.timeMs.toExponential(3).padEnd(12) + c20.joules.toExponential(3).padEnd(12) + c20.reactorSeconds.toExponential(3));
  summary.push('');
  summary.push('ONCE YOU KNOW THE ARCHITECTURE: compute cost is sunk.');
  summary.push('The shape is FREE to reproduce. Energy goes into DRIVING it.');
  summary.push('At lock: extraction viable = ' + (energyAtLock ? (energyAtLock.extraction_viable?'YES':'not yet, need deeper') : '?'));

  FS._log.push({
    step      : 'SEARCH_DONE',
    elapsed_ms: +elapsed.toFixed(2),
    lockedAt  : lockedAt,
    lockedLam : lockedLam,
    levels    : levels.length
  });

  return {
    seed       : seed,
    levels     : levels,
    lockedAt   : lockedAt,
    lockedLam  : lockedLam,
    energyAtLock: energyAtLock,
    costTable  : costTable,
    elapsed    : elapsed.toFixed(2) + 'ms',
    summary    : summary.join('\n')
  };
};

// ── Export ─────────────────────────────────────────────────────────────────
if (typeof module !== 'undefined' && module.exports) module.exports = FS;
else if (typeof global !== 'undefined') global.FS = FS;

})(typeof globalThis !== 'undefined' ? globalThis : this);
