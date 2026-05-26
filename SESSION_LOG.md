
========================================================================
SESSION: May 26, 2026 — GENESIS v9.0 → v9.8
========================================================================

TIMELINE:
  v9.0  Initial NS Benchmark Dashboard (3 levels, seed/flow/benchmark)
  v9.1  Fix invariant key names (faces not F, compute chi/E/V)
  v9.2  Fix console.log toFixed bug, version tag
  v9.3  Shapes spin at different speeds/planes, zoom out centered
  v9.4  L5 renders in animate loop, async benchmark with loading bar
  v9.5  Null guards for flow, L5 builds adjacency, draw cap 50K
  v9.6  L5→L4 (24K faces), loading bar with ETA, version v9.6
  v9.7  Reynolds regime toggles (STOKES/LAMINAR/TRANSITION/TURBULENT)
  v9.8  Fix SYNC stack overflow, regime comparison bars, WIGGLE CRAFT

BENCHMARK DATA (all runs, laptop, Chrome, single thread):
  L0:     12 faces  →     251-390ms / 1M steps  (path found: 3 cells)
  L1:     72 faces  →   1,100-1,360ms / 1M steps
  L2:    492 faces  →   5,960-7,498ms / 1M steps
  L4: 24,012 faces  → 373,192-476,992ms / 1M steps

SCALING:
  L0→L1:  6x faces,    ~4.4x time    O(n)
  L1→L2:  6.8x faces,  ~5.5x time    O(n)
  L2→L4:  48.8x faces, ~63x time     O(n) with browser overhead

  Pure O(n) prediction for L4: ~302,000ms
  Actual: ~477,000ms (1.58x overhead from event loop + rendering)

REGIME BENCHMARKS (on L2, 492 faces):
  STOKES     (Re<1):     ~250ms/1M
  LAMINAR    (Re~100):   ~1,360ms/1M  
  TRANSITION (Re~2000):  ~7,498ms/1M
  TURBULENT  (Re>10K):   ~7,498ms/1M

INVARIANTS (constant at ALL levels):
  chi   = 2       (Euler characteristic)
  P     = 12      (pentagon count)
  E/V   = 1.500   (edge/vertex ratio)

PURE CODE: 3,252 lines
  Sandwiched between twin primes 3251 and 3253

FACE COUNT PRIMES:
  12  → 1 from primes 11, 13
  72  → 1 from primes 71, 73
  492 → 1 from prime 491
  3432 → 1 from prime 3433

COOLALIENTECH:
  wiggle_craft.html     — dodecahedron warp (wiggle/warp/deswiggle)
  matter_cube.html      — 3D volumetric graph (mass/energy/info tradeoff)
  matter_cube_v1.2.html — observer/cube perspective switch + timeline
  info_graph.html       — pure topology info flow (7 graph types)

DEPLOYED:
  https://vsavytsk1.github.io/Mnetv1/shell/genesis_v9.0.html
  https://vsavytsk1.github.io/Mnetv1/shell/genesis_v8.0.html

========================================================================
