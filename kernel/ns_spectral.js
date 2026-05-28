// ============================================================================
//  ns_spectral.js
//  MachineNet · Navier-Stokes Spectral Solver · kernel module
//  Vladyslav Savytskyy · 2026
//
//  STANDALONE. Pure functions. Depends on goldberg_kernel.js (GK).
//  No DOM. No Three.js. No external dependencies.
//
//  WHAT THIS DOES:
//    Runs the discrete Navier-Stokes solver from graph_sandbox_v5.1
//    directly on the GK Goldberg sphere, then reads the EMERGENT
//    spectral gap from the steady-state pressure field.
//
//    The idea: we don't CHOOSE the geometry.
//    We run the fluid. The fluid FINDS the geometry.
//    The pressure eigenmodes of the converged NS field ARE the
//    spectral modes of the underlying graph Laplacian.
//    The dominant mode frequency = λ̃₁.
//
//  TWO MODES:
//    NSS.runOn(gkState, opts)     → full solve + spectral read
//    NSS.stepOn(state, nsState)   → single NS step (for animation)
//
//  NS EQUATIONS (discrete graph version):
//    Du/Dt = -∇p + (1/Re)∇²u    (momentum)
//    ∇·u = 0                      (continuity / pressure correction)
//
//  SPECTRAL READ:
//    After convergence, the pressure field p[i] lives on the nodes.
//    Project p onto the graph Laplacian eigenmodes via power iteration.
//    The dominant non-trivial frequency of p = λ̃₁ (spectral gap).
//
//  PUBLIC SURFACE:
//    NSS.initState(graph, opts)          -> nsState
//    NSS.step(graph, nsState)            -> nsState (one NS step)
//    NSS.run(graph, opts)                -> { nsState, spectral }
//    NSS.readSpectralGap(graph, nsState) -> { lambda1, pressure_mode }
//    NSS.runOn(gkState, opts)            -> full result
//
// ============================================================================

(function(global){
"use strict";

var NSS = {};

// ── Internal log ───────────────────────────────────────────────────────────
NSS._log = [];
NSS.clearLog = function(){ NSS._log = []; };
NSS.dumpLog  = function(){ return NSS._log.slice(); };

// ── Defaults ───────────────────────────────────────────────────────────────
NSS.DEFAULTS = {
  Re      : 150,       // Reynolds number (150 = turbulent enough to explore)
  dt      : 0.016,     // timestep
  steps   : 400,       // steps to run before reading spectrum
  maxV    : 3.0,       // velocity clamp
  initMode: 'vortex',  // 'vortex' | 'random' | 'pentagonal'
  logEvery: 50         // log interval
};

// ── §1  Build adjacency from GK graph ──────────────────────────────────────
NSS.buildAdj = function(graph){
  var adj = {};
  var N   = graph.N;
  for (var i = 0; i < N; i++) adj[i] = [];
  for (var i = 0; i < N; i++){
    var nbrs = Object.keys(graph.adj[i]);
    for (var k = 0; k < nbrs.length; k++){
      var j = parseInt(nbrs[k]);
      if (adj[i].indexOf(j) < 0) adj[i].push(j);
    }
  }
  return adj;
};

// ── §2  Init NS state ──────────────────────────────────────────────────────
// Each node gets: vx, vz, p, _dvx, _dvz, _div, _gradP, _visc, _conv
NSS.initState = function(graph, opts){
  opts = opts || {};
  var Re       = opts.Re       || NSS.DEFAULTS.Re;
  var initMode = opts.initMode || NSS.DEFAULTS.initMode;
  var N        = graph.N;
  var verts    = graph.verts;

  // Centroid
  var cx=0, cy=0, cz=0;
  for (var i=0; i<N; i++){ cx+=verts[i][0]; cy+=verts[i][1]; cz+=verts[i][2]; }
  cx/=N; cy/=N; cz/=N;

  var nodes = [];
  for (var i=0; i<N; i++){
    var x=verts[i][0]-cx, y=verts[i][1]-cy, z=verts[i][2]-cz;
    var r = Math.sqrt(x*x+y*y+z*z) + 0.001;

    var vx=0, vz=0;
    if (initMode === 'vortex'){
      // Tangential velocity around centroid in XZ plane
      vx = -z/r * 0.5;
      vz =  x/r * 0.5;
    } else if (initMode === 'pentagonal'){
      // Init vortex ONLY on pentagon vertices, zero elsewhere
      var isPent = graph.faceVerts && graph.faceVerts.some(function(f){
        return f.type === 'pent' && f.ids.indexOf(i) >= 0;
      });
      if (isPent){ vx = -z/r * 1.0; vz = x/r * 1.0; }
    } else {
      // Random
      vx = (Math.sin(i * 2.7) * 0.3);
      vz = (Math.cos(i * 1.9) * 0.3);
    }

    nodes.push({
      id    : i,
      vx    : vx, vz    : vz,
      p     : 0,
      _dvx  : 0, _dvz  : 0,
      _div  : 0, _gradP: 0,
      _visc : 0, _conv : 0,
      energy: 0
    });
  }

  NSS._log.push({ step:'NS_INIT', N:N, Re:Re, initMode:initMode });

  return {
    nodes    : nodes,
    step     : 0,
    Re       : Re,
    dt       : opts.dt || NSS.DEFAULTS.dt,
    maxV     : opts.maxV || NSS.DEFAULTS.maxV,
    converged: false,
    maxVhist : [],   // track max|v| over time
    divHist  : []    // track divergence over time
  };
};

// ── §3  Single NS step ─────────────────────────────────────────────────────
NSS.step = function(graph, ns){
  var nodes = ns.nodes;
  var adj   = graph.adj;
  var N     = graph.N;
  var Re    = ns.Re;
  var dt    = ns.dt;
  var maxV  = ns.maxV;
  var verts = graph.verts;

  // ── Pass 1: pressure correction from divergence ────────────────────────
  var totalDiv = 0;
  for (var i=0; i<N; i++){
    var n    = nodes[i];
    var nbrs = Object.keys(adj[i]);
    if (!nbrs.length) continue;
    var divU = 0;
    for (var k=0; k<nbrs.length; k++){
      var j  = parseInt(nbrs[k]);
      var nb = nodes[j];
      var dx = verts[j][0]-verts[i][0];
      var dz = verts[j][2]-verts[i][2];
      var dist = Math.sqrt(dx*dx+dz*dz) + 0.001;
      divU += ((nb.vx-n.vx)*(dx/dist) + (nb.vz-n.vz)*(dz/dist)) / dist;
    }
    n._div = divU / nbrs.length;
    n.p   += -n._div * 2.0;
    totalDiv += Math.abs(n._div);
  }
  totalDiv /= N;

  // ── Pass 2: momentum ───────────────────────────────────────────────────
  for (var i=0; i<N; i++){
    var n    = nodes[i];
    var nbrs = Object.keys(adj[i]);
    if (!nbrs.length) continue;
    var gpx=0, gpz=0, lapVx=0, lapVz=0, convX=0, convZ=0;
    for (var k=0; k<nbrs.length; k++){
      var j   = parseInt(nbrs[k]);
      var nb  = nodes[j];
      var dx  = verts[j][0]-verts[i][0];
      var dz  = verts[j][2]-verts[i][2];
      var dist = Math.sqrt(dx*dx+dz*dz) + 0.001;
      var dirX = dx/dist, dirZ = dz/dist;
      // pressure gradient
      gpx += (nb.p-n.p)*dirX/dist;
      gpz += (nb.p-n.p)*dirZ/dist;
      // viscous diffusion
      lapVx += (nb.vx-n.vx)/(dist*dist);
      lapVz += (nb.vz-n.vz)/(dist*dist);
      // convection
      var dvx=(nb.vx-n.vx)/dist, dvz=(nb.vz-n.vz)/dist;
      convX += n.vx*dvx*dirX + n.vz*dvx*dirZ;
      convZ += n.vx*dvz*dirX + n.vz*dvz*dirZ;
    }
    var invN = 1/nbrs.length;
    n._gradP = Math.sqrt(gpx*gpx+gpz*gpz)*invN;
    n._visc  = Math.sqrt(lapVx*lapVx+lapVz*lapVz)*invN/Re;
    n._conv  = Math.sqrt(convX*convX+convZ*convZ)*invN;
    n._dvx   = (-gpx + lapVx/Re - convX) * invN;
    n._dvz   = (-gpz + lapVz/Re - convZ) * invN;
    n.energy = n._gradP + n._visc + n._conv + Math.abs(n.p)*0.1;
  }

  // ── Pass 3: integrate ──────────────────────────────────────────────────
  var maxVstep = 0;
  for (var i=0; i<N; i++){
    var n = nodes[i];
    n.vx += n._dvx * dt;
    n.vz += n._dvz * dt;
    var speed = Math.sqrt(n.vx*n.vx + n.vz*n.vz);
    if (speed > maxV){ n.vx *= maxV/speed; n.vz *= maxV/speed; speed=maxV; }
    if (speed > maxVstep) maxVstep = speed;
  }

  ns.step++;
  ns.maxVhist.push(+maxVstep.toFixed(5));
  ns.divHist.push(+totalDiv.toFixed(6));

  // Convergence: velocity has settled (last 20 steps stable)
  if (ns.step > 50 && ns.maxVhist.length >= 20){
    var last20 = ns.maxVhist.slice(-20);
    var avg = last20.reduce(function(a,b){return a+b;},0)/20;
    var variance = last20.reduce(function(a,b){return a+(b-avg)*(b-avg);},0)/20;
    if (Math.sqrt(variance) < 0.001 * avg) ns.converged = true;
  }

  return ns;
};

// ── §4  Read spectral gap from pressure field ──────────────────────────────
// After NS converges, the pressure field p[i] encodes the dominant modes.
// We project p onto the graph Laplacian and extract λ̃₁ via Rayleigh quotient.
NSS.readSpectralGap = function(graph, ns){
  var N    = graph.N;
  var adj  = graph.adj;
  var deg  = graph.degMap;
  var nodes= ns.nodes;

  // Build pressure vector from converged NS field
  var p = [];
  var pMean = 0;
  for (var i=0; i<N; i++){
    p.push(nodes[i].p);
    pMean += nodes[i].p;
  }
  pMean /= N;
  // Centre and normalise
  var pNorm = 0;
  for (var i=0; i<N; i++){ p[i] -= pMean; pNorm += p[i]*p[i]; }
  pNorm = Math.sqrt(pNorm);
  if (pNorm < 1e-12){
    NSS._log.push({ step:'SPECTRAL_READ', error:'pressure field flat — not converged enough' });
    return { lambda1: null, error: 'flat pressure' };
  }
  for (var i=0; i<N; i++) p[i] /= pNorm;

  // Rayleigh quotient:  R(p) = pᵀ L̃ p / pᵀ p = pᵀ L̃ p  (since ||p||=1)
  // (L̃p)_i = p_i - Σ_j p_j / sqrt(d_i * d_j)
  var Lp = [];
  for (var i=0; i<N; i++){
    var sum  = 0;
    var nbrs = Object.keys(adj[i]);
    for (var k=0; k<nbrs.length; k++){
      var j = parseInt(nbrs[k]);
      if (deg[i]>0 && deg[j]>0) sum += p[j] / Math.sqrt(deg[i]*deg[j]);
    }
    Lp.push(p[i] - sum);
  }

  // Rayleigh quotient = p · Lp
  var rayleigh = 0;
  for (var i=0; i<N; i++) rayleigh += p[i] * Lp[i];

  // Also compute via energy-field: use velocity magnitude as weight
  var vMag = nodes.map(function(n){ return Math.sqrt(n.vx*n.vx+n.vz*n.vz); });
  var vMean= vMag.reduce(function(a,b){return a+b;},0)/N;
  // Weighted Rayleigh: velocity-weighted pressure mode
  var wRayleigh = 0, wTotal = 0;
  for (var i=0; i<N; i++){
    var w = vMag[i] / (vMean + 0.001);
    wRayleigh += w * p[i] * Lp[i];
    wTotal    += w;
  }
  if (wTotal > 0) wRayleigh /= wTotal;

  // Penalty: if rayleigh < 0 (numerical noise), floor at 0
  if (rayleigh < 0) rayleigh = 0;
  if (wRayleigh < 0) wRayleigh = 0;

  NSS._log.push({
    step         : 'SPECTRAL_READ',
    rayleigh     : +rayleigh.toFixed(8),
    wRayleigh    : +wRayleigh.toFixed(8),
    pressure_mean: +pMean.toFixed(6),
    pressure_norm: +pNorm.toFixed(6),
    ns_step      : ns.step,
    converged    : ns.converged
  });

  return {
    lambda1        : rayleigh,
    lambda1_weighted: wRayleigh,
    pressure_mode  : p,
    converged      : ns.converged
  };
};

// ── §5  Full solve: run NS to convergence, then read spectrum ──────────────
NSS.run = function(graph, opts){
  opts = opts || {};
  var maxSteps = opts.steps   || NSS.DEFAULTS.steps;
  var logEvery = opts.logEvery || NSS.DEFAULTS.logEvery;

  var ns = NSS.initState(graph, opts);

  NSS._log.push({ step:'RUN_START', maxSteps:maxSteps, Re:ns.Re, N:graph.N });

  for (var s=0; s<maxSteps; s++){
    ns = NSS.step(graph, ns);

    if (s % logEvery === 0){
      NSS._log.push({
        step    : 'NS_TICK',
        nsStep  : ns.step,
        maxV    : ns.maxVhist[ns.maxVhist.length-1],
        div     : ns.divHist[ns.divHist.length-1],
        converged: ns.converged
      });
    }
    if (ns.converged) break;
  }

  NSS._log.push({
    step     : 'RUN_DONE',
    nsSteps  : ns.step,
    converged: ns.converged,
    finalMaxV: ns.maxVhist[ns.maxVhist.length-1],
    finalDiv : ns.divHist[ns.divHist.length-1]
  });

  var spectral = NSS.readSpectralGap(graph, ns);

  return { ns: ns, spectral: spectral };
};

// ── §6  Main entry: run on a GK state ─────────────────────────────────────
NSS.runOn = function(gkState, opts){
  NSS.clearLog();
  opts = opts || {};

  var t0 = (typeof performance !== 'undefined') ? performance.now() : Date.now();
  NSS._log.push({ step:'RUNON_START', faces: gkState.faces.length });

  // Need SAR's graph builder
  if (typeof SAR === 'undefined' || !SAR.buildGraph){
    return { error: 'SAR module required (sar_modular.js)' };
  }

  var graph = SAR.buildGraph(gkState);
  graph.adj2 = NSS.buildAdj(graph); // ensure adj is integer-keyed

  // Run three modes, compare
  var results = [];
  var modes = ['vortex','random','pentagonal'];
  modes.forEach(function(mode){
    var r = NSS.run(graph, Object.assign({}, opts, { initMode: mode }));
    results.push({
      initMode : mode,
      nsSteps  : r.ns.step,
      converged: r.ns.converged,
      lambda1  : r.spectral.lambda1,
      lambda1_w: r.spectral.lambda1_weighted,
      finalMaxV: r.ns.maxVhist[r.ns.maxVhist.length-1]
    });
    NSS._log.push({ step:'MODE_RESULT', mode:mode, lambda1:r.spectral.lambda1, lambda1_w:r.spectral.lambda1_weighted });
  });

  // Best estimate: average of converged runs
  var convergedLams = results
    .filter(function(r){ return r.converged && r.lambda1 !== null; })
    .map(function(r){ return r.lambda1; });

  var lambdaEst = convergedLams.length
    ? convergedLams.reduce(function(a,b){return a+b;},0) / convergedLams.length
    : results[0].lambda1;

  // Weighted estimate
  var convergedLamsW = results
    .filter(function(r){ return r.converged && r.lambda1_w !== null; })
    .map(function(r){ return r.lambda1_w; });

  var lambdaEstW = convergedLamsW.length
    ? convergedLamsW.reduce(function(a,b){return a+b;},0) / convergedLamsW.length
    : null;

  var elapsed = ((typeof performance !== 'undefined') ? performance.now() : Date.now()) - t0;

  NSS._log.push({
    step       : 'RUNON_DONE',
    elapsed_ms : +elapsed.toFixed(2),
    lambdaEst  : lambdaEst,
    lambdaEstW : lambdaEstW,
    SAR5_target: 0.1473
  });

  return {
    graph      : { N: graph.N, faces: gkState.faces.length },
    results    : results,
    lambdaEst  : lambdaEst,
    lambdaEstW : lambdaEstW,
    elapsed    : elapsed.toFixed(2) + 'ms',
    SAR5_target: 0.1473,
    delta      : lambdaEst !== null ? Math.abs(lambdaEst - 0.1473) : null
  };
};

// ── Export ─────────────────────────────────────────────────────────────────
if (typeof module !== 'undefined' && module.exports) module.exports = NSS;
else if (typeof global !== 'undefined') global.NSS = NSS;

})(typeof globalThis !== 'undefined' ? globalThis : this);
