## Live simulations — click first, read after

| Simulation | What it is |
|---|---|
| [GENESIS Explorer v7.5](https://vsavytsk1.github.io/Mnetv1/shell/genesis.html) | **NEW.** Goldberg fractal explorer. Two seeds (C60 + dodecahedron). Mobius transform. Backface cull. Zoom 0.5x-50,000x. Papyrus warnings. |
| [GENESIS Benchmark](https://vsavytsk1.github.io/Mnetv1/shell/genesis_bench.html) | Compute cost analyzer. Time, memory, F/ms per refinement level. CSV export. |
| [Sacred Math Tree](https://vsavytsk1.github.io/Mnetv1/) | 10 calculus trees. Autopilot plays them all. Zoom-gated. |
| [Dodecahedron of Open Questions](https://vsavytsk1.github.io/SpookyPrimes/) | 12 open physics problems. Spin it. Click a pentagon. |
| [Fractal Geometry Builder](https://vsavytsk1.github.io/Mnet/) | C60 recursive shell. Click any face. It opens forever. |

> *If you're not sure what to click ? click the tree. Press autopilot. Watch math grow.*

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
index.html                          ? v4.0 (GitHub Pages serves this)
tree/
  math_tree_v1.html ? v4.0.html    ? all 20 versions preserved
  math_tree.db                      ? SQLite database (76 nodes, 66 edges)
  calc1_trees.json                  ? tree data as JSON
  calc1_trees.csv                   ? tree index for Excel
  calculus_pandas_map.csv           ? 38 calculus?pandas operations
  calculus_pandas_map.txt           ? quick reference
  ideas/                            ? original sketches
SACRED_MATH_TREE.md                 ? full dev log (17 versions documented)
PIPELINE.md                         ? pandas + LaTeX + SQLite architecture
DATABASE.md                         ? why SQLite, schema, alternatives
```

---

## The philosophy

> No entry in the database is wrong. It's math.
> Some paths are elegant. Some are computationally expensive.
> Dead ends teach you WHY something doesn't work.
> That's not failure. That's the most important node in the tree.

> The game mechanic IS the math.
> Clicking IS exploring. Exploring IS understanding.
> The dopamine serves the theorem, not the other way around.

---

*"I have no real idea if this is true.*
*The first thing that comes to mind and I think mmm how funny.*
*Divine shit. Fun stuff. Let's continue and push."*

*? Vlad, 6 AM, Buenos Aires, May 25 2026*

*"zoom in, wanderer. read the equation before you touch it."*
*? Papyrus banner, shame slider at 10s*

*20 versions. 76 nodes. 1,065 XP. One session. The tree grows because you walked it.*

---

## License

MIT. The math is open. The tree is open. The shape grows when you click it.

---

*? @Sagaific ? Buenos Aires ? 2026*
