# PCBIUM — DISSECTION

Source: `shell/pcbium-v2_9_5.html` · 67,061 B · `PCBIUM · CAD nav · nanite · v2.9.5`
Subtitle, **EXACT**: *"no curves — points & lines on the grid, like pixels · same graph on
plane & C60"*

---

## 1. THE THESIS, IN ITS OWN WORDS

**EXACT**, the file's own header comment at line 190:

```js
/* PCBIUM v2.9 — PURE GRAPH SPACE. No curve is ever drawn. A trace is a path
   hopping vertex-to-vertex along the mesh edges (Dijkstra shortest path) —
   points and lines only. The "curve" is just the illusion a fine grid makes
   from a distance, exactly like pixels on a screen. Same graph on the C60 and
   the flat plane. 3 grid levels. Pure Canvas, no deps. */
```

Everything below is an elaboration of that paragraph.

---

## 2. THE BOARD IS THE BUCKYBALL

**EXACT**, line 208:

```js
// The board IS the truncated icosahedron: 12 pentagon ENDS (keep-out) + 20 hexagons,
// each hexagon cut into 6*hexSub^2 triangles = the routable grid.
```

So the substrate is not a rectangle with an outline. It is a **closed surface**, and this
is the single most consequential decision in the file:

- a rectangular board has an **edge**, so routing needs boundary logic;
- a closed board has **no edge**, so routing is pure graph search and nothing special
  happens anywhere. **DESIGN CHOICE**, and the same one the whole cave rests on (χ=2).

The 12 pentagons are **keep-out**, enforced in exactly one place — the router skips them:

**EXACT**, line 241: `if(MESH.pent[nb[k]])continue;`

**HYPOTHESIS:** the 12 pentagons are where the ports/connectors want to live. They are the
only distinguished sites on an otherwise homogeneous surface, there are exactly 12 of them
by Euler's theorem no matter how fine the mesh gets, and a fullerene's 12 pentagons are
precisely the *unavoidable* defects. A board where the connector count is a topological
invariant rather than a layout decision is a genuinely different way to think. **Untested.**

### The mesh ladder

| button | builder | frequency |
|---|---|---|
| `C60` | `buildC60(hexSub)` | direct construction from the icosahedron's 12 vertices + 20 faces |
| `C80` | `buildGoldbergDual(2, hexSub)` | geodesic → dual → triangulate |
| `C180` | `buildGoldbergDual(3, hexSub)` | " |
| `C320` | `buildGoldbergDual(4, hexSub)` | " |

and the routable grid inside each face is set by `hexSub`:

**EXACT**, line 247: `var LEVELS={coarse:1,medium:2,fine:3}, gridName="medium", gridN=LEVELS.medium;`

**This is the fractalisation knob.** Same board, same topology, same 12 pentagons — only
the sampling density changes. Exactly the cave's *"the level of precision we get is how
much we fractalize."*

### Vertex welding — the shared weakness

**EXACT**, line 220:

```js
function weld(pp){var k=Math.round(pp[0]*1e5)+","+Math.round(pp[1]*1e5)+","+Math.round(pp[2]*1e5);...}
```

Welding by **rounded float coordinates at 1e-5**. Compare `Gos/src/sphere.rs`, which welds
by **exact index pair** `(a,b)` in a map and never touches a coordinate. The Rust lane is
already the stronger of the two here: coordinate welding is a tolerance, index welding is
an identity. **This is a concrete thing the Rust port fixes rather than reproduces.**

---

## 3. A TRACE IS A LIST OF INTEGERS

**EXACT**, lines 238–242 — the entire router:

```js
function routePath(s,t){ if(s===t) return [s];
  var N=MESH.verts.length,dist=new Float64Array(N).fill(Infinity),prev=new Int32Array(N).fill(-1),done=new Uint8Array(N);dist[s]=0;
  for(var it=0;it<N;it++){var u=-1,best=Infinity;for(var i=0;i<N;i++)if(!done[i]&&dist[i]<best){best=dist[i];u=i;}
    if(u<0||u===t)break;done[u]=1;var nb=MESH.adj[u];for(var k=0;k<nb.length;k++){if(MESH.pent[nb[k]])continue;var w=vlen(vsub(MESH.verts[nb[k]],MESH.verts[u]));if(dist[u]+w<dist[nb[k]]){dist[nb[k]]=dist[u]+w;prev[nb[k]]=u;}}}
  var path=[],cur=t;while(cur!==-1){path.unshift(cur);if(cur===s)break;cur=prev[cur];}return path[0]===s?path:[s,t];}
```

Read what it returns: **`path`, an array of vertex indices.** That is the trace. There is
no curve object, no bezier, no arc, no width, no fillet. The copper is `[41, 42, 58, 77, …]`.

**COMPUTED — the one real flaw:** this is Dijkstra with a **linear scan** for the minimum,
so it is **O(N²)**, not O(E log V). At C320/fine the vertex count runs to tens of thousands
and every single wire placement re-runs the whole thing. This is the first thing the Rust
port should improve, and it is a pure win — a binary heap changes nothing about the
semantics. **The Rust port does not need to be cleverer than the JS; it needs to be able to
afford the fine grid.**

Also note `MESH.pent[nb[k]]` is checked on the **neighbour**, so pentagon vertices are
excluded as *destinations* — the keep-out is a node property, not a region test. Clean.

---

## 4. THE PHYSICS THAT IS ACTUALLY REAL

Most of the panel is honest first-order signal integrity, not decoration.

**EXACT**, line 244: `var RI=0.80,RO=1.06,BOARD_DIAM=40,UNIT_MM=BOARD_DIAM/2,T_PD=0.0055;`

so the board is **40 mm diameter**, and `T_PD = 0.0055 ns/mm` — propagation delay, which is
about right for FR-4 microstrip (**HYPOTHESIS**: ~5.5 ns/m implies εᵣ_eff ≈ 2.7; plausible
for microstrip, low for stripline).

**EXACT**, line 245: `function critLen(){return (tRise/6)/T_PD;}`

That is the standard **electrically-long** rule of thumb: a trace matters as a transmission
line once its delay exceeds ~1/6 of the rise time. The panel reads out `knee`, `critical
arc-length` (30.3 mm at the default 1.00 ns edge), and `electrically-long traces  n/m`.

**COMPUTED check:** (1.00 ns / 6) / 0.0055 ns/mm = **30.30 mm**. The displayed default
`30.3 mm` is correct. ✔

Trace length is measured as **great-circle arc**, which is the right measure on a sphere:

**EXACT**, line 276: `function arcMM(via,vib){ return Math.acos(...vdot(...))*UNIT_MM; }`

**Caveat the file states itself**, and honestly — **EXACT**, from the Smith tab:
*"Per-trace Z₀ needs the dielectric stackup."* And from the Field tab:
*"K: real 3D Biot–Savart along the graph path, inductive only."* **Inductive only** — no
capacitive term. It says so. Good.

### The other tabs

| tab | what it is |
|---|---|
| **Field** | MAXWELLIUM × CHROMIUM, ∇·B = 0, Biot–Savart along the graph path |
| **12□** | classify each pentagon by its zero coordinate → 3 golden rectangles (1:φ), 30 icosahedron edges, degree 5 — an **O(1)** map |
| **Smith** | Γ = (z−1)/(z+1) — the same Möbius map as `smithium-v1_2.html` |
| **Grid** | layer separation, vertex/segment counts, *"copper length vs direct"* as a % |
| **I/O** | JSON in/out: `{ "name", "layers", "pads":[{"ref","x","y","net"}] }` |

The **12□** tab is the interesting one: it claims every pentagon has one zero coordinate
(true — icosahedron vertices are cyclic permutations of `(0, ±1, ±φ)`), which gives a
constant-time classification into 3 golden rectangles. **EXACT** claim; the geometry
supports it; not independently re-derived here.

**Layers** are concentric shells: **EXACT**, line 246: `function layerR(L){ return RI*(1 - L*layerGap); }`
A multilayer board as **nested spheres**. Vias are radial. **DESIGN CHOICE**, and a pretty one.

---

## 5. WHAT THE RUST PORT INHERITS

| from PCBIUM | status in `Gos/` |
|---|---|
| board = closed fullerene, 12 pentagons keep-out | ✔ `judge.rs`, `Mesh::c60()`, AXIOM 01 gate |
| Goldberg ladder C60→C80→C180→C320 | ✔ `sphere.rs` (icosphere lane), `Mesh::refine()` |
| trace = `Vec<usize>` of vertex indices | ✘ **not built** |
| Dijkstra over `adj`, pentagons skipped | ✘ **not built** — and should use a heap, not O(N²) |
| great-circle length in mm | ✘ not built |
| `critLen`, knee, electrically-long count | ✘ not built |
| index welding instead of 1e-5 coordinate welding | ✔ **already better in Rust** |

**The next honest step in this lane** is small and self-contained: a `route.rs` holding
`fn route(mesh, s, t) -> Option<Vec<usize>>`, binary-heap Dijkstra, pentagons excluded,
plus `fn arc_mm(mesh, a, b) -> f64`. It has one obvious test — a route must never contain a
pentagon vertex — and one obvious property: `route(s,t)` reversed equals `route(t,s)` in
length, though not necessarily in path. That is a real, checkable, one-sitting deliverable.
