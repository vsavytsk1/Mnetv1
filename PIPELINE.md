# THE PIPELINE — MachineNet Engineering Methodology
## Append-only. The law. Buenos Aires · May 2026

---

## THE ONE RULE

> **The builder owns the shell. The kernel is absolute. The ledger is permanent.**

If it's not built by `builder/` it doesn't exist.
If it breaks the kernel invariants it doesn't ship.
If it's not in `LEDGER.md` it didn't happen.

---

## THE GALACTIC LAW

> By galactic law, every build must satisfy all of the following.
> No exceptions. No shortcuts. The topology enforces it.

```
LAW 1 -- P = 12
  Every build must verify exactly 12 pentagons.
  GK.invariants(state).pents === 12
  If not 12 -- STOP. Do not ship. Investigate.

LAW 2 -- chi = 2
  Every build must verify V - E + F = 2.
  If not 2 -- STOP. Do not ship. Euler is never wrong.

LAW 3 -- lambda = 0.1473
  SAR-5 spectral invariant must hold within tolerance 0.02.
  If broken -- INVESTIGATE before next kernel change.

LAW 4 -- LICENSE ships with every build
  shell/spooky_warning/index.html is the canonical license.
  Every ENG build links to it or embeds it.
  The Galactic Law is on that page. It ships always.

LAW 5 -- BUILDER OWNS THE SHELL
  No HTML is hand-written in shell/ or pack/.
  Every output file has a builder/*.py that generates it.
  If you hand-edit shell/ -- you have broken the law.
  The fix: write a builder. Run it. Commit both.

LAW 6 -- NAMING CONVENTION
  H7.MAJOR.MINOR.PATCH.BUILD -- Holly-7 lineage, forever.
  MAJOR: kernel-breaking. NEVER unless invariants still hold.
  MINOR: new module. PATCH: fix. BUILD: auto-increment.
  Product names: VALE / ENG / GENESIS / GKERN / LEDGER.
  Never ship with borrowed names (JARVIS stays in L007).

LAW 7 -- THE LEDGER IS PERMANENT
  Every significant build: one LEDGER.md entry. Append only.
  Never edit existing entries. One truth. Buenos Aires 2026.
```

---

## THE STACK

```
kernel/                    ← SOURCE OF TRUTH (never hand-edited)
  M1  goldberg_kernel.js   ← C60, Goldberg sphere, refinement, invariants
  M2  graph_axioms.js      ← P1-P7 axiom verification
  M3  sar_modular.js       ← SAR-5 spectral proof (λ̃ = 0.1473)
  M4  ns_spectral.js       ← NS flow spectral gap
  M5  fractal_search.js    ← fractal architecture search + lock
  M6  mnet_nanite.js       ← physics-driven LOD DAG
  M7  math_tree_v5.0.html  ← sacred tree engine (lives in tree/)

builder/                   ← ALL BUILD MACHINERY
  build_holly7.py          ← pack/holly7.html       (dashboard, all 7 modules)
  build_genesis.py         ← shell/genesis_vX.Y.html (canvas, v7.5 format)
  build_warning.py         ← shell/spooky_warning/   (FMA intro)
  rebuild_gate.py          ← shell/gate/             (gate with images)
  patches/                 ← every patch script, forever
  hexCompTest/             ← every build archived, gitignored (local only)
  dist/HOLLY7.exe          ← one command to rule them all, gitignored

shell/                     ← GitHub Pages output (all live URLs)
pack/                      ← holly7.html + big builds (live URLs)
tree/                      ← math tree versions (live URLs)
docs/                      ← lore .md files
LEDGER.md                  ← permanent append-only build log
PIPELINE.md                ← this file (the law)
```

---

## THE INVARIANTS (kernel absolute — these never break)

```
P = 12          pentagons    Euler forces it. Always.
χ = V - E + F = 2            never breaks. never.
C60 seed        60V, 32F     where everything starts
λ̃ = 0.1473     SAR-5        spectral invariant of the Goldberg sphere
```

If a build breaks any of these → **MAJOR++ and investigate before shipping**.

---

## THE BUILD COMMANDS

```powershell
# Full dashboard (all 7 modules, tabbed UI)
python builder/build_holly7.py

# Canvas explorer (all 6 modules, v7.5 format)
python builder/build_genesis.py

# FMA warning intro
python builder/build_warning.py

# Gate with images
python builder/rebuild_gate.py

# One command (exe, opens Brave, logs build)
.\builder\dist\HOLLY7.exe
```

---

## THE VERSIONING RULE

```
H7.MAJOR.MINOR.PATCH.BUILD

H7      = Holly-7 lineage, forever
MAJOR   = kernel-breaking change (NEVER, unless proven)
MINOR   = new module added (P=12 pentagons, always 12)
PATCH   = fix/tweak (C60=60, always 60)
BUILD   = auto-increment from hexCompTest archive count
```

---

## THE MINIMAL COMPUTE PARADIGM

> Start every render/sim at the minimum. The user zooms in to unlock.

```javascript
// ALWAYS these defaults on first load:
cam = { zoom: 50, spin: 0.002, maxFaces: 1000, atom: 0.1 }

// Why:
// zoom=50     → geometry exists but sub-pixel → GPU rests
// spin=0.002  → barely moving → 1 frame every 2s at idle
// maxFaces=1000 → cutoff renders cleanly → computation flies
// atom=0.1    → minimal draw depth

// The trick: zoom out = nothing to draw = 0 GPU cost
// Zoom in = everything appears = compute on demand
// This is the fractal maker trick. It works at any scale.
```

---

## THE 3-STEP CYCLE (how we work)

```
1. PROPOSE   — 3 concrete changes, no more, no less
2. EXECUTE   — all 3 at once, logged, committed
3. VERIFY    — open in browser OR check git log
              → if broken: stop, diagnose, revert
              → if good: append to LEDGER.md, next cycle
```

**Why 3:** enough to make real progress, small enough to debug instantly.

---

## THE GITHUB PAGES RULE

> GitHub Pages serves from **root only** (or /docs). Never /public.

```
Live URL pattern:
  vsavytsk1.github.io/Mnetv1/shell/genesis_v8.1.html  ← ROOT/shell/
  vsavytsk1.github.io/Mnetv1/pack/holly7.html          ← ROOT/pack/
  vsavytsk1.github.io/Mnetv1/tree/math_tree_v5.0.html  ← ROOT/tree/

NEVER move shell/ tree/ pack/ research/ logs/ away from root.
```

---

## THE GITIGNORE RULE

```
Never commit:
  builder/dist/        ← exe (binary, platform-specific)
  builder/_pyibuild/   ← PyInstaller artifacts
  builder/hexCompTest/ ← build archive (local only, infinite)
  BUILD_TRACE.log      ← runtime log
  *.log                ← all logs

Always commit:
  builder/*.py         ← all build scripts
  builder/patches/     ← all patch history
  kernel/*.js          ← all kernel modules
  shell/*.html         ← all generated HTML
  pack/holly7.html     ← latest dashboard build
  LEDGER.md            ← permanent record
```

---

## THE LEDGER RULE

> Every significant build gets a LEDGER.md entry. Append only. Never edit.

```markdown
### L00N · YYYY-MM-DD · what was built

**What:** one sentence
**Size:** XKB | **Modules:** list
**Live:** URL
**Why:** one sentence on why it matters
```

---

## THE FORMAT RULE (canvas explorer)

> `genesis_v7.5.html` is THE reference. All canvas builds must match exactly.

```
- canvas fullscreen, z-index:0
- HUD top-left (V, E, F, pent, hex, chi, E/V, level, ops, drawn, MB)
- axiom-log top-right (280px, scrollable)
- bottom bar: buttons + sliders
- Orbitron font for euler display
- background #050508 ALWAYS
- font: 'Courier New' monospace
- colors: #00ffd5 (teal), #ff69b4 (pink), #ffd700 (gold), #80d0ff (blue)
```

---

## THE REPOS

```
Mnetv1       ← this repo, main engineering base
Mnet         ← Unity port (future)
SpookyPrimes ← the dodecahedron of open questions
VALE         ← standalone
StrangerDanger ← standalone
```

---

## LIVE URLS (full index)

### Engineering Dashboard
```
/pack/holly7.html                 ← H7 master build (all 7 modules)
/pack/GKernV2.0.html              ← Goldberg kernel v2
/pack/GENESIS.html                ← genesis pack
/pack/navierHunt.html             ← NS hunt
/pack/navierCrunch_results.html   ← benchmark results
/pack/navierCrunch_turbulent.html ← turbulent regime
```

### Canvas Explorer (genesis format)
```
/shell/genesis_v8.1.html  ← LATEST (full kernel build, M1-M6)
/shell/genesis_v9.0.html
/shell/genesis_v8.0.html  ← used by warning intro (engine source)
/shell/genesis_v7.6.html  ← FractalEngBuilder panel
/shell/genesis_v7.5.html  ← THE REFERENCE FORMAT
/shell/genesis_v7.4.html
/shell/genesis_v7.3.html
/shell/genesis_v7.2.html
/shell/genesis_v7.1.html
/shell/genesis.html
/shell/genesis_bench.html
```

### NS Flow Simulations
```
/shell/mnet_v7.html
/shell/mnet_v6.html
/shell/mnet_v6_pc.html
/shell/mnet_sim.html
```

### Sandbox (graph_sandbox format)
```
/shell/graph_sandbox_v5.1.html   ← latest
/shell/graph_sandbox_v5.0.html
... v4.9 → v3.2 → v1
```

### MobiusNet (archive)
```
/shell/machinenet_shell_v4.4_W11D_mobius.html
/shell/machinenet_shell_v2.html
/shell/archive/machinenet_shell_v4.4_mobius.html
... v4.2 → v4.0 → v3.8 → v3.7 ... v3
```

### FMA Intro + Gate
```
/shell/spooky_warning/warning_v2.0.html  ← LATEST built by builder
/shell/spooky_warning/warning_v1.3.html
/shell/spooky_warning/index.html         ← license + links
/shell/gate/gate_v1.3.html               ← LATEST built by builder
/shell/gate/gate_v1.html
```

### Math Tree
```
/tree/math_tree_v5.0.html   ← latest (used by holly7 as M7)
/tree/math_tree_v4.3.html
... v4.2 → v4.0 → v3.4 ... v1
```

### Research
```
/research/minimal_math/genesis_dashboard_v2.0.html
/research/minimal_math/genesis_v1.6.html
... v1.5 → v1
```

### Color Math Sandbox
```
/Gsndbx3testClrsMath/v3_2_cmd.html
/Gsndbx3testClrsMath/v3_1_face_walker.html
/Gsndbx3testClrsMath/v3_0_centroid_fan.html
```

### Logs Dashboard
```
/logs/v6_dashboard.html
```

---

*Buenos Aires · May 2026 · monkey brain + meta mind*
*"The builder is black magic and so we respect every bit of it"*
