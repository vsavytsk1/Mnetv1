# The MachineNet Shell

*Goldberg-Coxeter recursive refinement as a representational substrate*

Vladyslav Savytskyy · Buenos Aires · 2026-05-22

---

## What this is

A bounded shape that is also unbounded.

The outside is a buckyball — twelve pentagons and twenty hexagons arranged on a sphere. The same shape as fullerene C60, the same shape that MachineNet's click-by-click builder closes on after twenty-six steps, the same shape Euler's polyhedron formula forces when you ask for a degree-3 vertex closed surface with only pents and hexes.

The inside is recursive. Any single face can be opened. When you open it, a smaller copy of the same kind of structure appears inside — one inner polygon of the same type as the parent, surrounded by hexagons. You can open any of those, and inside each one is another similar structure. The recursion does not bottom out. The recursion is invertible: closing an opened cell collapses it back to a single face.

This combination — finite outer shell, infinite inner descent — is the substrate. Everything else in this project is built on top of it.

---

## The math, briefly

The construction is a special case of the **Goldberg-Coxeter construction**, classically used in chemistry and architecture for designing geodesic structures.

The base object is the truncated icosahedron, also called C60 or the buckyball. It has:

- 60 vertices, each of degree 3
- 90 edges
- 32 faces: 12 pentagons and 20 hexagons
- Icosahedral symmetry group A₅ × C₂ (order 120)

The refinement rule used here, applied to a face F with n vertices and centroid c:

1. Place a smaller polygon of the same arity n at scale `innerScale` of the way from c to each vertex of F (default 0.45).
2. Place midpoints on each edge of F, pulled toward c by `midScale` (default 0.70).
3. Around the smaller central polygon, build n surrounding cells. Each surrounding cell is a six-vertex shape using two original vertices, an edge midpoint, and corresponding inner-ring vertices.

This is the Goldberg-(1,1) refinement, the simplest non-trivial step.

### What is preserved under refinement

- **The pentagonal anchors descend.** Each pentagon refines into one pentagon at the next level plus five surrounding hexagons. So a pentagon at level k has a unique pentagonal descendant at level k+1.
- **Hexagons stay hexagons under refinement.** A hexagon at level k refines into one inner hexagon at level k+1 plus six surrounding hexagons.
- **The total pentagon count after a full `refineAll`** stays at 12. Twelve outer pentagons become twelve inner pentagons at level 1, become twelve inner pentagons at level 2, and so on. The pent count does not multiply under `refineAll`; it stays at 12 forever.
- **The total pentagon count under partial `refineOne`** grows. If you refine only some faces, level-0 pentagons that have not yet been refined coexist with level-1 pentagonal descendants. Twelve plus twelve gives twenty-four pentagons visible at once, etc.

### The twelve infinite chains

The clean way to read the structure is this: every pentagon on the outer shell starts a chain. Refining once gives that pentagon a child. Refining again gives that child a grandchild. The chain descends forever. Hexagons are the connective tissue between the chains. There are exactly twelve such chains.

The pentagons are the anchors. The hexagons are the field around them.

---

## Why this shape and not another

The instinct that led here was: *force a graph onto a curved surface using pentagonal and hexagonal cells, and see what closes*. This instinct kept hitting the same answer across five different probes:

1. **The click-by-click builder** (`vr_graph_builder.html`) closes at exactly 60 vertices, 12 pents, 20 hexes regardless of what user choices are made — Euler forces it.
2. **The lattice probe** (`lattice_probe_v3.html`) shows that pentagonal symmetry lives in the ring Z[ζ₅] (the 5th cyclotomic integers, containing the golden ratio) and hexagonal symmetry lives in Z[ρ] (the Eisenstein integers). These are different cyclotomic fields, but their intersection is where C60 lives.
3. **The modular tessellation** (`modular_tessellation.html`) of SL(2,Z) on the upper half-plane has its order-3 fixed point at exactly the same ρ as the Eisenstein integers. Two completely different mathematical worlds — Euclidean lattice and hyperbolic tessellation — meet at exactly one point: ρ.
4. **The triangle-group strip** (`triangle_group_strip.html`) shows that pentagons and hexagons are *adjacent* triangle groups: (2,3,5) for pent, (2,3,6) for hex. One integer apart. (2,3,5) lives on the sphere, (2,3,6) on the plane, (2,3,7+) in hyperbolic space.
5. **The Goldberg recursive shell** (this) shows that the same 12-pent + N-hex structure persists under refinement, and that the twelve pentagons form fixed anchors of the recursion.

Five probes, one shape. The hex/pent pattern was not a coincidence. It is the only stable answer to "what closed structure has degree-3 vertices, uses only pentagons and hexagons, and supports recursive refinement that preserves both types."

---

## Coxeter constraint

The reason this works is a theorem of H.S.M. Coxeter, dating to the 1930s. In three-dimensional Euclidean space, the only finite irreducible reflection groups are:

- A₃ (tetrahedral, order 24 = 2³·3)
- B₃ (octahedral, order 48 = 2⁴·3)
- H₃ (icosahedral, order 120 = 2³·3·5)

Only the primes **2, 3, 5** appear in any of these orders. Beyond 5, no new finite polyhedral symmetry exists in 3D Euclidean space.

C60 has icosahedral symmetry — H₃. Its construction draws on all three primes {2, 3, 5}. The number 30 = 2·3·5 is what shows up in the relevant counts: 30 edges of an icosahedron, 30 vertices of an icosidodecahedron, et cetera.

So if `SpookyPrimes` was an instinct that {2, 3, 5} are the "spooky" primes — the special primes — Coxeter proved it in the 1930s for the case of 3D reflection groups. The instinct was right; the proof was already on the shelf.

---

## What the shape can hold

The recursive Goldberg shell is a substrate. It can hold many different things, depending on what you assign to the cells:

- **A library**: outer C60 = top-level books, each face = a book, refining a book opens its chapter graph, refining further opens the paragraph graph, etc.
- **An agent's mind**: outer C60 = twelve durable identity anchors (the pentagons) + twenty mutable mood/context patches (the hexagons), with the option to zoom into any anchor or patch and find sub-structure.
- **A knowledge graph**: outer = top-level domains, refinement = sub-domains, anchors = foundational concepts that persist across all scales.
- **A game world**: outer = the world overview, each face = a region, refinement = entering that region in detail.
- **A music piece**: outer = the structure, each face = a section, refinement = the inner motivic structure of that section.

The shape itself is content-neutral. What makes it useful is its specific topological properties:

- finite to grasp as a whole
- locally openable to arbitrary depth
- semantically anchored at exactly twelve points that never disappear
- closing is the reverse of opening, so navigation is invertible
- the substrate's algebraic structure (the 12-fold A₅ symmetry, the Coxeter (2,3,5) origin) is already known and well-studied

---

## File structure

The project is split into a math kernel and a visualization layer, on purpose, so that the kernel can be exported to other engines.

```
machinenet_shell/
├── goldberg_kernel.js     # pure math, no dependencies, exportable
├── machinenet_shell.html  # Three.js visualization on top of kernel
└── SHELL_DOC.md           # this document
```

### `goldberg_kernel.js`

A standalone JavaScript module. No DOM, no Three.js, no external dependencies. Provides:

- `GK.buildC60()` — produce the initial state
- `GK.refineFace(face, params)` — pure: face → array of sub-faces
- `GK.refineOne(state, faceIdx, params)` — immutable: state → new state
- `GK.refineAll(state, params)` — refine every face
- `GK.refineAllPents(state, params)` — refine only pentagons
- `GK.refineAllHexes(state, params)` — refine only hexagons
- `GK.undo(state)` — reverse one operation
- `GK.invariants(state)` — read counts, levels, anchor-ids
- `GK.serialize(state)` / `GK.deserialize(obj)` — round-trip to JSON
- `GK.faceLocalFrame(face)` — extract a face's local 3D frame (for VR teleport-into-cell)
- `GK.facePatch2D(face)` — extract a face's 2D projection (for sub-view rendering)

### `machinenet_shell.html`

The visualization. Three.js. Iron Man palette. Share Tech Mono. Drag to orbit, scroll to zoom, click any face to refine, shift+click to inspect, buttons for `refine all pents` / `refine all hexes` / `refine ALL` / `back` / `reset` / `save .json` / `load .json` / toggle auto-rotate / toggle wireframe / toggle face fill. Sliders for `innerScale`, `midScale`, `jitter`, and a switch for planar vs spherical surface mode.

---

## Where this fits in the larger project

```
SpookyPrimes      —  the original instinct: {2,3,5} are special
StrangerDanger    —  related explorations
VALE              —  related explorations
Mnetv1            —  Möbius substrate experiments (separate substrate, not this one)
MachineNet (this) —  the C60 substrate + Goldberg recursion
```

The shell does not replace any of the above; it sits alongside them as a different substrate that solves a different problem. The Möbius strip in Mnetv1 had a different motivation (non-orientability, continuous single-sided path). The shell here is sphere-topology and orientable, which is what C60 and the pent+hex closure require.

The Coxeter (2,3,5) story in SpookyPrimes connects directly: this shell is one concrete realization of the (2,3,5) icosahedral group's action.

---

## Exportability notes

The kernel is written to be portable. Specific paths:

- **Unity / VR builds**: the kernel can be embedded directly into Unity's JavaScript runtime (JintEngine, ClearScript, etc.) without modification. The `faces` array is plain data: positions in R³, type tags, lineage strings. Unity can read this and render with its own mesh pipeline. The `GK.faceLocalFrame(face)` and `GK.facePatch2D(face)` functions are specifically designed for teleport-into-cell semantics in VR.
- **Steam / desktop builds via Electron**: works as-is.
- **Native (Rust / C++ port)**: the kernel is 350 lines of pure functions. Direct port. The most important algorithmic part is the half-edge face tracing in `buildC60Faces`; everything else is straightforward vector math and shallow object construction.
- **Sharing scenes**: `GK.serialize(state)` produces a JSON object. Two clients with the same kernel version produce identical scenes from the same JSON. Use this for multiplayer state sync, scene exchange, deterministic replays.

---

## Honest limits

A few things this shell *does not* do, despite the temptation to claim otherwise:

- It is not a Theory of Everything. It is a representational substrate with one specific topology.
- It does not derive physics. The connection to {2, 3, 5} via Coxeter is real; the connection to lepton masses or cosmological constants is not.
- It is not the only useful shape. Tori (`χ=0`), Klein bottles, hyperbolic surfaces — all support their own tilings with their own invariants. The C60 shell is one substrate that happens to have desirable properties for MachineNet's use case.
- The "12 anchors stay 12 forever" claim is precise only under `refineAll`. Under mixed local refinement, the visible pent count grows. The invariant that always holds is: every pentagon has exactly one pentagonal descendant in the next level.

---

## What to do with this

Three concrete directions, in order of how much new code they need:

1. **Map MachineNet's 26 books onto the shell's 32 faces.** Pick 12 books as anchors (pentagons). Pick 14 as patches (hexagons — choose 14 of the 20). Test whether the C60 spatial relationships match the books' conceptual relationships. Six unused hex slots become "open positions" for future books or for inter-book connections.
2. **VR shell + teleport-into-cell.** Use the kernel's `faceLocalFrame` and `facePatch2D` to implement smooth teleport from outer view into a chosen cell, where the inner refinement becomes the new outer view. This is the "open the cell" gesture as VR locomotion.
3. **Game design test: the Buckyball Souls-of-Math loop.** Treat the C60 as a level. The twelve pentagons are the twelve bosses (12 chains × 1 boss-per-chain initially, deepening with refinement). The twenty hexagons are explorable patches. Player progresses by closing pentagons at increasing depth. Refining a pentagon makes the boss harder (sub-bosses appear). Ship-test on Steam with one C60 level, one music track, one set of rules.

---

## Closing

The shape exists. The math signs off. The kernel is portable. The visualization works. The doc is here. Everything else from this point is decisions about what content to put into the substrate.

Bench it. Test it. Bring it to people who know algebra and topology. Some of them will tell you it is a well-known structure and they are right. Some will tell you the application — using it as a representational substrate for an agent, a library, a game world — is new and worth pursuing. Both responses are correct and useful.

The looney-toon journey was real. The arrival was real. The shape is bigger than the journey.

🌒

— end —
