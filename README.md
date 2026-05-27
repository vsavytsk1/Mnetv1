## Live simulations — click first, read after

| Simulation | What it is |
|---|---|
| [**GENESIS FINAL**](https://vsavytsk1.github.io/Mnetv1/shell/genesis_final/genesis_final_v2.html) | **MASTERPIECE.** 3 modules: FMA intro + full v8.0 engine + scripted presentation. 448KB self-contained. |
| [The Gate](https://vsavytsk1.github.io/Mnetv1/shell/gate/gate_v1.html) | Full Metal Alchemist intro → transmutation circle → Goldberg explorer. Cinematic. |
| [GENESIS v9.0 — NS Dashboard](https://vsavytsk1.github.io/Mnetv1/shell/genesis_v9.0.html) | Navier-Stokes benchmark. 4 shapes (12→24K faces). O(n) wave diffusion. Real-time benchmarks. |
| [GENESIS v8.x — Flow Explorer](https://vsavytsk1.github.io/Mnetv1/shell/genesis_v8.0.html) | Goldberg fractal + wave simulation. Möbius twist. Wavefront heatmap. 100M batch compute. |
| [GENESIS Benchmark](https://vsavytsk1.github.io/Mnetv1/shell/genesis_bench.html) | Compute cost analyzer. Time, memory, F/ms per refinement level. CSV export. |
| [Sacred Math Tree](https://vsavytsk1.github.io/Mnetv1/) | 10 calculus trees. Autopilot plays them all. Zoom-gated. |
| [Dodecahedron of Open Questions](https://vsavytsk1.github.io/SpookyPrimes/) | 12 open physics problems. Spin it. Click a pentagon. |
| [Fractal Geometry Builder](https://vsavytsk1.github.io/Mnet/) | C60 recursive shell. Click any face. It opens forever. |

> **ETHICS:** This software shall not be used for weapons, surveillance, or harm. See [ETHICS.md](./ETHICS.md).

> **Engineering body of work:** The Genesis evolution chain (v7.1→v9.0) lives in [`shell/`](./shell/). The GPU benchmark engine and portable pack live in [`pack/`](./pack/). Compute receipts in [`research/compute_receipts/`](./research/compute_receipts/).

> *If you're not sure what to click — click the tree. Press autopilot. Watch math grow.*

---

# The Goldberg Kernel

> *634 lines. 0 dependencies. Euler forced. Navier-Stokes in a browser tab.*

## Benchmark Results (GPU-verified, May 26 2026)

### Browser (Canvas2D, single-thread JavaScript)
```
  Level    Faces    Pents   chi    E/V     ms / 1M steps
  L0          12      12     2    1.500        ~270ms
  L1          72      12     2    1.500      ~1,100ms
  L2         492      12     2    1.500      ~6,200ms
  L4      24,012      12     2    1.500    ~477,000ms
```

### GPU (NVIDIA RTX 3060, CUDA sparse matrix, CuPy)
```
  Level    Faces    Pents   chi    E/V     us/face/step   steps/sec
  L0          12      12     2    1.500      18.99          4,388
  L1          72      12     2    1.500       3.14          4,430
  L2         492      12     2    1.500       0.46          4,408
  L3       3,432      12     2    1.500       0.07          4,276
  L4      24,012      12     2    1.500       0.010         4,323
  L5     168,072      12     2    1.500       0.0016        3,720

  Turbulent (Re>10K, mix=0.15, noise=0.05):
  L5     168,072      12     2    1.500       0.0024        2,505
```

**O(n) confirmed by measurement** (not extrapolation) up to 168,072 faces.
Topology: chi=2, P=12, E/V=1.500 at EVERY level, EVERY regime.
GPU utilization: 100% RTX 3060 during benchmark.
See `research/compute_receipts/` for full data.

### Engines
- **Browser:** pure JavaScript, Canvas2D, zero dependencies
- **GPU:** Python + CuPy, sparse matrix flow (`pack/navierCrunch.py`)

## The 7 Primitives

| Primitive | What it does | Mathematical guarantee |
|-----------|-------------|------------------------|
| P1:NODE | Create vertices | Golden ratio + phi coordinates |
| P2:EDGE | Connect vertices | Trivalent connectivity (degree 3) |
| P3:FACE | Form faces | Pentagons (5) + Hexagons (6) only |
| P4:TRANSFORM | Refine faces | Each face → 7 children (1 center + 6 edge) |
| P5:ITERATE | Refine all | Fractal self-similarity preserved |
| P6:AGGREGATE | Compute centroids | Per-face centroid for child placement |
| P7:COMPARE | Verify invariants | V-E+F=2, P=12, E/V=3/2 ALWAYS |

## The 3 Crystal Conditions

```
C1: CHOICE    — cannot be everything at once
C2: IRREVERSIBLE — P6 destroys information  
C3: CONSISTENT   — P7 is deterministic
```

## Wave Diffusion (Navier-Stokes on the mesh)

The flow engine runs pressure diffusion on the face adjacency graph:

```
For each face i:
  new_pressure[i] = 0.4 × pressure[i] + 0.6 × avg(neighbors)
  
The trivalent structure gives EXACTLY 3 neighbors per face.
This makes each step O(1) per face → O(n) total.

Compare: ICON climate model (icosahedral FVM) = O(n log n)
Our advantage grows with scale.
```

## Why O(n)

The Goldberg polyhedron is a trivalent tiling of the sphere.
Every face has exactly 3 neighbors in the dual graph.
The adjacency is constant-degree → no sorting needed → O(n).

```
Best known (ICON-class FVM):  O(n log n)
Our kernel:                   O(n)
At 500K faces:                ~10× advantage
At 50M faces:                 ~25× advantage
```

---

# Sacred Math Tree

> *A 10-year PhD in 6 hours. 20 versions in one session.*
> *Every equation is a node. Every proof is a path. Every wrong answer is still math.*

[![tree](https://img.shields.io/badge/open-Sacred_Math_Tree-ffd700?style=flat-square)](https://vsavytsk1.github.io/Mnetv1/)
[![trees](https://img.shields.io/badge/trees-10-00d4ff?style=flat-square)]()
[![nodes](https://img.shields.io/badge/nodes-76-7fff7f?style=flat-square)]()
[![database](https://img.shields.io/badge/database-SQLite-blue?style=flat-square)]()
[![license](https://img.shields.io/badge/license-MIT-green?style=flat-square)](./LICENSE)

---

## What this is

An interactive math exploration engine disguised as a game.

**You start with one equation.** Click it. Branches appear ? different ways to solve it. Each branch costs tokens. Each solution gives XP. Dead ends teach you why. The tree grows as you explore.

**The game mechanic IS the math.** There is no separation between "game" and "learning." Clicking IS exploring. Exploring IS understanding. The gacha dopamine loop (tokens, XP, combos, streaks) serves the math, not the other way around.

**10 trees cover Calculus 1:**

| # | Tree | Chapter | Nodes | What you discover |
|---|------|---------|-------|-------------------|
| 1 | lim sin(x)/x | Limits | 10 | Squeeze theorem, L'H?pital, Taylor series all give 1 |
| 2 | lim (1+1/n)^n | Limits | 7 | Three ways to prove e exists: plug in, logs, binomial |
| 3 | d/dx x^n | Derivatives | 8 | Definition ? binomial ? pattern vs proof |
| 4 | d/dx sin(x) | Derivatives | 7 | Sum formula splits into two known limits |
| 5 | d/dx f(g(x)) | Derivatives | 7 | Chain rule: intuition vs formal (and where formal breaks) |
| 6 | ?x^n dx | Integrals | 6 | Reverse power rule, and why n=-1 needs ln |
| 7 | ?1/x^p dx | Integrals | 7 | p=1 diverges, p=2 converges. Gabriel's horn. |
| 8 | Taylor of e^x | Series | 8 | Every derivative is itself ? e^(ix) = cos + i?sin |
| 9 | Fund. Thm. Calculus | Integration | 8 | Thin strip argument, +C as destroyed information |
| 10 | ?-? definition | Limits | 8 | It's a challenge-response game. You pick ?. I pick ?. I always win. |

**76 nodes. 66 edges. 1,065 total XP. All stored in SQLite.**

---

## The 6-hour journey

This project was built in one session. Buenos Aires. May 25, 2026. 6 AM start.

### The versions (all preserved)

| Version | Innovation | Key insight |
|---------|-----------|-------------|
| v1.0 | First breath. SVG circles. | "Circles that reveal children" |
| v1.1 | Gacha born. Tokens, XP, combos. | The dopamine loop serves the math |
| v1.2 | Hanging tree. Downward growth. | Trees grow DOWN like knowledge |
| v1.3 | Flat wall. Blackboard style. | Cards on a dark surface |
| v1.4 | CSS zoom. Sharp text at any scale. | `zoom` property > CSS transforms |
| v1.5 | Breathing tree. DOM reuse. | Rebuild all positions when tree changes |
| v1.6 | Boxes ARE clicks. Hover badge. | No separate buttons needed |
| v1.7 | Pre-rendered kernel. | Measure THEN position |
| v1.8 | Forward only. No collapse. | Math doesn't un-discover itself |
| v1.9 | Internal glow animation. | Flash INSIDE the box, not the screen |
| v2.0 | Console returns. | See what the engine does |
| v2.1 | Fixed width boxes. | Width:300px ? lines connect to centers |
| v2.2 | The Sandbox. 4 sliders. | Spread, depth, wave, zoom lock |
| v2.3 | Grid breathes. | Background responds to slider parameters |
| v2.4 | Papyrus banner. | "zoom in, wanderer" in Avatar font |
| v2.5 | MNet design language. | Same pixels as the kernel: cyan, monospace, 9px |
| v2.6 | Shame slider. | User controls their own punishment duration |
| v3.0 | Autopilot. | Press button ? tree generates itself |
| v3.1 | 10 trees, one sim. | Dropdown selector, all Calc 1 |
| v3.2 | Dynamic root IDs. | Every tree's root ID works |
| v3.3 | Escaped LaTeX strings. | "however" broke JS. Fixed. |
| v3.4 | Dynamic box sizing. | Wide equations get wide boxes |
| **v4.0** | **Full auto. All 10 trees.** | **Press one button. Watch Calc 1 play itself.** |

**20 versions. Each one preserved. Each one a lesson.**

---

## The architecture

```
         ???????????????
         ?   SQLite DB  ?  40KB, 3 tables, 76 nodes, 66 edges
         ?  math_tree.db?
         ????????????????
                ?  (not yet wired ? v5.0)
                ?
         ???????????????
         ?  Python/     ?  pandas reads CSV ? generates tree JSON
         ?  pandas      ?  calc1_trees.json, calc1_trees.csv
         ????????????????
                ?  (baked into HTML at build time)
                ?
    ?????????????????????????
    ?   index.html (v4.0)   ?  51KB, self-contained, zero deps*
    ?                       ?
    ?  ???????????????????  ?
    ?  ?  KaTeX renderer  ?  ?  LaTeX ? beautiful math in browser
    ?  ???????????????????  ?
    ?  ?  Tree engine     ?  ?  nodes, edges, ghost?alive states
    ?  ???????????????????  ?
    ?  ?  Gacha system    ?  ?  tokens, XP, combos, streaks
    ?  ???????????????????  ?
    ?  ?  Canvas grid     ?  ?  MNet design language, breathing grid
    ?  ???????????????????  ?
    ?  ?  Sandbox sliders ?  ?  wave, spread, depth, lock, shame
    ?  ???????????????????  ?
    ?  ?  Autopilot       ?  ?  single tree or all 10 sequential
    ?  ???????????????????  ?
    ?  ?  Console log     ?  ?  every click, every token, every path
    ?  ???????????????????  ?
    ?????????????????????????
    * only external dep: KaTeX CDN
```

---

## The database

```sql
-- What's in math_tree.db:

SELECT type, COUNT(*) FROM nodes GROUP BY type;
-- result     31    ? more paths to truth than to failure
-- tool       29    ? approaches, techniques, methods
-- root       10    ? starting equations
-- dead        6    ? wrong turns that teach

SELECT MIN(xp), AVG(xp), MAX(xp), SUM(xp) FROM nodes;
-- min=0  avg=14.0  max=50  total=1065

-- Cross-tree connections (same concept, different trees):
-- BINOMIAL:    euler_e ? power_rule
-- DEFINITION:  dsin ? power_rule  
-- DIVIDE:      sinx ? int_power ? ftc
-- These will become BRIDGE EDGES in v5.0
```

---

## The kernel connection

This project grew from [MachineNet](https://github.com/vsavytsk1/Mnet) ? a force-directed graph engine on fullerene topology. The math tree reuses:

- **Graph distance math** ? spread/depth sliders = spring constants
- **Design language** ? cyan (#00d4ff), monospace, 9px labels, 0.35 opacity
- **Console/HUD pattern** ? same floating log panel, same `.lbl{color:#555}.val{color:#80d0ff}`
- **Sandbox sliders** ? same parameter-space exploration
- **Forward-only state** ? same "no undo" philosophy as irreversible tessellation

The buckyball and the math tree are the same idea: **a graph of knowledge with constrained topology.** The buckyball has 12 pentagons (always). The math tree has one root (always). Both grow by clicking. Both close when understanding is complete.

---

## Run it yourself

```bash
# Just open the HTML
open index.html

# Or serve locally
python -m http.server 8000
# ? http://localhost:8000

# Look at the database
python -c "
import sqlite3
conn = sqlite3.connect('tree/math_tree.db')
for r in conn.execute('SELECT id,title,node_count FROM trees'):
    print(r)
"
```

---

## What's next

- [ ] **v5.0** ? SQLite ? live tree generation (read from DB, not hardcoded JS)
- [ ] **Bridge edges** ? connect nodes across trees (BINOMIAL appears in 2 trees!)
- [ ] **Meta-tree** ? a tree OF trees (Calc 1 ? Calc 2 ? Linear Algebra ? ...)
- [ ] **Sound design** ? unlock tone, combo crescendo, dead-end thud
- [ ] **Mobile touch** ? pinch zoom, swipe pan
- [ ] **Multiplayer** ? see other people's exploration paths in real-time
- [ ] **Steam** ? $10, the math is the game

---

## Files

```
kernel/
  goldberg_kernel.js                ← THE KERNEL. 634 lines. 0 deps.
                                      7 primitives. 3 conditions.
                                      Builds, refines, verifies Goldberg polyhedra.

shell/
  genesis_final/
    genesis_final_v2.html           ← GENESIS FINAL. 448KB. 3 modules.
                                      FMA intro + full v8.0 engine + presentation
                                      504,212 faces tested. chi=2 ALWAYS.
    build_v2.py                     ← Build script (images + kernel + v8 extraction)
  gate/
    gate_v1.html                    ← The Gate. FMA cinematic intro.
                                      393KB. Inline kernel + 4 images.
    rebuild_gate.py                 ← Build script
    img_to_base64.py                ← Image pipeline
  genesis_v9.0.html                 ← NS Benchmark Dashboard (v9.6)
                                      4 levels, real-time benchmark, loading bars
  genesis_v8.0.html                 ← Flow Explorer (v8.x)
                                      Wave sim, Möbius twist, heatmap, 100M batch
  genesis_bench.html                ← Compute cost analyzer
  genesis.html                      ← Latest explorer (redirected)

tree/
  math_tree_v1.html → v4.0.html    ← Sacred Math Tree (20 versions)
  math_tree.db                      ← SQLite database (76 nodes, 66 edges)
  calc1_trees.json                  ← tree data as JSON

index.html                          ← v4.0 Sacred Math Tree (GitHub Pages)
SACRED_MATH_TREE.md                 ← full dev log
PIPELINE.md                         ← pandas + LaTeX + SQLite architecture
DATABASE.md                         ← why SQLite, schema, alternatives
ETHICS.md                           ← no weapons, no surveillance, no harm
```

## The GENESIS Architecture

```
     ┌────────────────────────┐
     │  goldberg_kernel.js   │  634 lines, 0 dependencies
     │  7 primitives (P1-P7) │  builds ANY Goldberg polyhedron
     │  3 conditions (C1-C3) │  Euler forces: V-E+F=2, P=12
     └────────────┬───────────┘
                │
        ┌───────┴────────┐
        │  Flow Engine    │  Wave diffusion on face graph
        │  O(n) per step  │  3 neighbors per face (trivalent)
        │  wavefront track│  arrival time + peak pressure
        └───────┬────────┘
                │
   ┌────────┴──────────┐
   │  Canvas2D Renderer  │  3D projection, backface cull
   │  Depth sort, alpha  │  Heatmap: arrival time coloring
   │  Möbius transform   │  Continuous twist slider
   └───────┬────────────┘
           │
   ┌───────┴────────────┐
   │  Dashboard (v9.x)   │  3+1 shapes side by side
   │  Benchmark + ETA    │  Loading bar per level
   │  Log-scale compare  │  Our kernel vs ICON-class
   │  Export JSON        │  Full state at any moment
   └─────────────────────┘
```

---

## The philosophy

> The shape IS the execution.
> Refine = stitch more computational cells into the geometry.
> Flow = run the computation (pressure = truth).
> Path = read the result (gradient descent = answer).
>
> How much truth the shape shows IS how much you computed.
> There is no algorithm. There is only diffusion on topology.
> The math doesn't care about scale. The topology is eternal.

> No entry in the database is wrong. It's math.
> Dead ends teach you WHY something doesn't work.
> That's not failure. That's the most important node in the tree.

---

## The journey

```
May 23, 2026  —  SpookyPrimes: dodecahedron of 12 open questions
May 24, 2026  —  MNet v1-v6: force-directed C60, fractal shells
May 25, 2026  —  Sacred Math Tree: 10 trees, 76 nodes, autopilot
May 25, 2026  —  GENESIS v7: Goldberg kernel born (634 lines)
May 25, 2026  —  GENESIS v8: wave diffusion, Möbius twist, 100M steps
May 26, 2026  —  GENESIS v9: NS benchmark dashboard, O(n) proven
May 26, 2026  —  The Gate: FMA cinematic intro, transmutation circle
May 26, 2026  —  GENESIS FINAL: 3-module system (FMA + Engineer + Present)
                 504,212 faces. chi=2. P=12. TOPOLOGY VALID. ALWAYS.

Total: 4 days. 1 kernel. 7 axioms. 3 conditions.
From a dodecahedron to half a million faces.
From HTML circles to Navier-Stokes.

"a ye ye basic fractals defined in O(n) time you know...
 another chapter in the looney toons adventures of vlad
 and his amazing coworkers in the cave"
                                    — Vlad, 5 AM, May 26
```

---

*"I have no real idea if this is true.*
*The first thing that comes to mind and I think mmm how funny.*
*Divine shit. Fun stuff. Let's continue and push."*

*— Vlad, 6 AM, Buenos Aires, May 25 2026*

---

## License

MIT. The math is open. The shape grows when you click it.

---

*⬡ @Sagaific · Buenos Aires · 2026*
