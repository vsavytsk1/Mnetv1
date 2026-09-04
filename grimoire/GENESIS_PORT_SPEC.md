# GENESIS PORT SPEC
### The target for the GENESIS card in the Rust ENG dashboard
### Source of truth: `shell/genesis_v8.5.2.html` — dissected 2026-08-19

---

## WHY THIS FILE EXISTS

We nearly ported from `builder/genesis_wallpaper_v1_7.py`. That was the wrong
source, for a reason worth writing down:

> **v1.5 is the tested version. v1.7 is not.** Porting from an untested source
> means inheriting its bugs *and* its confidence.

We proved that the hard way, before writing the spec. v1.7's `face_growth`
priced the pentagon op as `(H + 7P, 0)` — seven children per pentagon and
**zero pentagons surviving**, a shell Euler forbids. It compounded: every
later step of a plan containing `pent` was priced against that impossible
object. It survived because the file's own verification line covers `all` and
`6s` and *never* `5s`.

The HTML is the working version. **It is the spec.** Everything below is read
out of it, not remembered.

**STATUS GRAMMAR** (Thea's, unchanged): **EXACT** (quoted from source) ·
**COMPUTED** (derived here) · **DESIGN CHOICE** · **HYPOTHESIS** ·
**NOT YET BUILT**.

---

## 0. WHAT THE FILE ACTUALLY IS

197,896 B carrying **six standalone kernel modules**, each a self-contained
IIFE with no DOM and no dependencies:

| module | global | what it owns |
|---|---|---|
| `goldberg_kernel.js` | `GK` | **the refinement operator** ← the port target |
| `graph_axioms.js` | `GA` | the 7 graph primitives |
| `sar_modular.js` | `SAR` | SAR-5 modular coupling, spectral |
| `ns_spectral.js` | `NSS` | Navier–Stokes spectral solver |
| `fractal_search.js` | `FS` | fractal architecture search |
| `mnet_nanite.js` | nanite | cluster DAG + adaptive LOD |

**SCOPE DECISION:** this card ports **GK only**. The other five are separate
cards. Attempting six at once is how a port becomes a rewrite.

---

## 1. THE PUBLIC SURFACE — the contract, EXACT from the header

```
GK.buildC60()                        -> { faces, vertices, edges, info }
GK.refineFace(face, params)          -> [ subFace, ... ]
GK.refineAll(state, params)          -> newState (immutable)
GK.refineOne(state, faceIdx, params) -> newState (immutable)
GK.invariants(state)                 -> { pents, hexes, depthMax, ... }
GK.serialize(state)                  -> JSON-safe object
GK.deserialize(obj)                  -> state
GK.zoomInto(state, faceIdx)          -> { childState, transform }
```

Plus, found in the body but not in the header: `GK.refineAllPents` (and its
hex twin) — the browser's `REFINE 5s` / `REFINE 6s` buttons.

**IMMUTABILITY IS PART OF THE CONTRACT.** `refineAll` returns a new state and
appends `{op, snapshot}` to `history`. That is what makes `UNDO` work. A Rust
port that mutates in place has not ported this.

---

## 2. THE DATA MODEL

### A face — EXACT

```js
{ pts:     [[x,y,z], ...],   // n points, CCW seen from outside
  type:    'pent' | 'hex',
  level:   0,                 // refinement depth
  lineage: [i],               // path of parent indices from the seed
  id:      'F12',             // stable, mint-once
  anchor:  'A12' | null }     // pentagons only; INHERITED by inner pentagon
```

**The mesh is FACE SOUP.** Faces carry their own points; vertices are
duplicated between neighbours and never welded. That is deliberate — it is
what lets the browser reach millions of faces without an index structure, and
it is why `invariants()` has to *reconstruct* V and E (§5).

`anchor` is the thread back to one of the original twelve. Each pentagon
inherits its parent's anchor, so `anchorCount` should stay 12 forever — an
independent witness to `P=12` that does not rely on counting types.

### A state — EXACT

```js
{ faces: [face, ...], history: [{op, snapshot}, ...], counter: n }
```

`counter` mints ids; it is threaded through refinement by `counterRef` so ids
stay unique across a whole session.

---

## 3. THE OPERATOR — the heart, EXACT

Defaults, read from the parameter block:

| param | default |
|---|---|
| `innerScale` | `0.45` |
| `midScale` | `0.70` |
| `preservePentInPent` | `true` |
| `preserveHexInHex` | `true` |
| `surfaceMode` | `'planar'` |
| `sphereR` | `1.6` |
| `jitter` | `0` |

Given a face of `n` points with centroid `c`:

```
inner[i]   = lerp(c, pts[i], innerScale)              [project if spherical]
midRing[i] = lerp(c, mid(pts[i], pts[j]), midScale)   [project if spherical]
em         = mid(pts[i], pts[j])                      [project if spherical]

inner face = inner[0..n-1]      type: parent arity, ANCHOR INHERITED if pent
cell i     = [ pts[i], em, pts[j], inner[j], midRing[i], inner[i] ]
             6 points, type ALWAYS 'hex'
```

**THE TWO SENTENCES THAT ARE THE WHOLE GROWTH LAW:**

1. The inner face **preserves arity**.
2. The surrounding cells are **always hexagons**.

Therefore `pentagon → 1 pent + 5 hex` (6 faces) and `hexagon → 1 hex + 6 hex`
(7 faces). Everything in §4 follows from those two lines and nothing else.

**Ids and lineage — EXACT:** inner gets `parent.id + '.c' + (++counter)` and
`lineage + [0]`; cell `i` gets `parent.id + '.e' + (++counter)` and
`lineage + [i+1]`. Level is `parent.level + 1` for all children.

**Jitter is applied to `inner` and `midRing` only** — never to `pts[i]`,
`pts[j]` or `em`. Those are shared with the neighbouring face, and jittering
them would tear the mesh. **DESIGN CHOICE, and a load-bearing one.**

**THE CRESCENT DEFECT.** `midRing[i]` sits on the hexagon side of the cell
edge `inner[i]→inner[j]` and nowhere on the cell side. With `midScale >
innerScale` the ring opens a gap (a rosette); below, it overlaps. **This is
not a bug to fix — it is the picture.** Any port that "corrects" it produces
different images and has failed.

---

## 4. THE GROWTH LAW — port this first, it is pure integer

| op | button | faces | pentagons |
|---|---|---|---|
| all | `REFINE ALL` | `6P + 7H` = `7F − 12` | `P` |
| hex | `REFINE 6s` | `P + 7H` = `7F − 72` | `P` |
| pent | `REFINE 5s` | `H + 6P` = `F + 5P` | `P` |

**P never moves.** ✅ **Already built** — `Gos/src/genesis.rs`, integers only,
`checked_*` so the ceiling refuses instead of wrapping (R3).

**Regression ladders, EXACT from the browser's own logs — both are tests:**

```
all then 6s x5 : 32 → 212 → 1412 → 9812 → 68612 → 480212 → 3361412
5s twice       : 2352992 → 2353052 → 2353112     (steps of +60 = 5P)
```

The second ladder is the one v1.7 got wrong. It exists as a test so the
pentagon branch can never again be the untested one.

---

## 5. INVARIANTS — and the one thing the port must do BETTER

`GK.invariants(state)` returns `{pents, hexes, faces, edges, vertices,
maxLevel, perLevel, anchorCount, anchors}`.

Because the mesh is face soup, V and E are **reconstructed**:

```js
edges    = round(faceEdgeSum / 2);
vertices = edges - faces + 2;                  // ← EULER ASSUMED
if (hasHex) vertices = round(faceEdgeSum / 3); // ← TRIVALENCE, independent
```

**COMPUTED, and already verified against a real render (F = 2,353,112):**
the hex branch gives `E = 7,059,330` and `V = 4,706,220`, matching the HUD
exactly, and `χ = 2` is then a **genuine** check — V and E come from
independent divisors, so it can fail.

**But the no-hex branch is a tautology.** `V = E − F + 2` makes `χ = 2` true
by construction. It bites exactly one case: a hexagon-free seed — the
dodecahedron, which the browser offers as `SEED 12` and whose log says
`SEED: dodecahedron born`. There, `χ=2` is asserted, not earned. The source
even half-admits it in a comment about Platonic seeds.

> **PORT REQUIREMENT R-INV:** the Rust port must **never** derive `V` from
> Euler. Derive `V` and `E` from trivalence, compute `χ`, and let it be wrong.
> `Gos/src/genesis.rs::certify` already does this and returns `None` for a
> census that is not trivalent-closed. A check that cannot fail is not a check.

**Second witness, free:** `anchorCount` must equal 12 independently of the
type count. Port it, and assert both.

**HYPOTHESIS to resolve during the port:** the source header contains the
author reasoning aloud about whether mixed local refines can push `pents`
above 12, and lands on *"after a full refineAll, exactly 12."* By §3, a
refined pentagon still yields exactly one pentagon, so `refineOne` should also
hold at 12. **Verify against the code, not the comment.**

---

## 6. RENDER + UI — the card's visible surface

**Seeds:** `doSeed` (C60) · `doSeedDodec` (12) · `doSeedGoldberg` ·
`doSeedPlatonic`.

**Ops:** `doRefineAll` · `doRefineHexes` · `doRefinePents` · `doUndo` ·
`doReset`.

**Sliders — EXACT, with their ranges and defaults:**

| id | min | max | default | meaning |
|---|---|---|---|---|
| `sl-inner` | 10 | 90 | **45** | `innerScale × 100` |
| `sl-mid` | 10 | 95 | **70** | `midScale × 100` |
| `sl-jit` | 0 | 30 | **0** | jitter |
| `sl-zm` | 1 | 1500 | 200 | zoom |
| `sl-atom` | 1 | 30 | 10 | atom size |
| `sl-maxf` | 0 | 100 | 50 | max faces drawn |
| `sl-spin` | 0 | 50 | 5 | spin |
| `mobSlider` | 0 | 100 | 0 | Möbius twist |
| `sl-pov` | 10 | 120 | 60 | field of view |
| `sl-inside` | 0.1 | 1.5 | 1.2 | inside-view scale |

**Toggles:** `toggleMobius` (χ: 2 → 0) · `toggleLight` · `toggleInsideView` ·
`toggleFlight` + `toggleFlightLock` + `flightGo`/`flightRelease` ·
`toggleHud` · `toggleHideAll` · `toggleAxLog`.

**Exports:** `doExport` (image) · `doExportGraph`.

**HUD readouts** (from the live screenshots): `V E F pent hex chi E/V level
ops drawn MB` — plus the running op log with `P=` and `F=` per step, and
`SEED: … born`.

---

## 7. WHAT THE RUST PORT GIVES THAT THE HTML CANNOT

The reason to port at all, stated so it can be checked:

1. **Integer certainty.** The growth law is `u64` with `checked_*`; the
   ceiling is a refusal, not a wrap.
2. **The judge.** `judge.rs` computes `χ` from a rotation system over integer
   darts — no coordinates, no Euler assumption. The browser cannot do this
   because its mesh is soup. **Weld, then judge, and compare against the
   census.** That is the port's headline result: *counting is not closing.*
3. **1s and 0s.** `bits.rs` writes the mesh as a bit matrix; `raster.rs`
   paints it with no browser and no GPU.
4. **Streaming.** The render is a reduction into a 133 MB framebuffer, so
   depth stops being a RAM problem.
5. **The gate.** AXIOM 01 runs before a byte is exported (`examples/gate.rs`).

---

## 8. THE PRECISION LANE — declare it before writing geometry

**EXACT:** the browser runs in JS `Number` = **IEEE-754 binary64**. This
crate's `Vec3` is `[f64; 3]`. **Same lane.** For `+ − × ÷ √` both are
correctly rounded, so the geometry can be asserted **bit-identical** — that is
RULE 0's whole point, and here it applies.

⚠️ **The Python is NOT in this lane.** `genesis_wallpaper_v1_7.py` runs in
`float32` (41 `np.float32` sites). A port targeting *the Python's* images
would need `f32`; a port targeting *the browser's* uses `f64`. **We target the
browser.** Do not mix the two and call the result "the same picture".

`projectToSphere` and `centroid` stay in the certified lane. `Math.random()`
for jitter does **not** — replace with `rng.rs` so runs are reproducible, and
say so.

---

## 8b. SURFACE COVERAGE — scored against the code, 2026-09-02

Section 1 lists nine entry points. Six are ported; three are not, and the
missing three are not decoration.

```text
  GK.buildC60          ok   seed_c60 / Census::C60
  GK.refineFace        ok   refine_face
  GK.refineAll         ok   refine(Op::All)
  GK.refineOne         ok   refine_one
  GK.refineAllPents    ok   Op::Pent / Op::Hex
  GK.invariants        ok   invariants() -- trivalence, R-INV honoured

  GK.serialize         --   MISSING, nowhere in the crate
  GK.deserialize       --   MISSING, nowhere in the crate
  GK.zoomInto          --   MISSING as a STATE operation
```

**On `zoomInto`, a distinction worth writing down before someone ticks the box
by accident.** `gos_viewer` matches `zoom` 33 times — every one of them the
**camera control**, a float that scales the projection. `GK.zoomInto(state,
faceIdx)` is a different animal: it descends into one face and returns
`{childState, transform}`, a *state* operation producing a new mesh. Having a
zoom slider is not having `zoomInto`. The names collide and the meanings do
not.

**On `serialize`/`deserialize`:** these are the round trip, and the port spec
already owes a 60-vertex browser/Rust hex diff that cannot be done without
them. They are also the cheapest possible carrier for step 9's bit vector —
serialise a state in both languages, compare the bits. **Two owed items share
one implementation.**

## 8c. R-INV — honoured, and the second witness is not

`certify()` derives `chi` from trivalence and returns `None` when the census is
not trivalent-closed, so the check can fail. Verified: the dodecahedron case
has its own test, `the_dodecahedron_earns_chi_two_instead_of_assuming_it`, and
`Census::DODECAHEDRON` is a real seed in the census lane.

**But `SEED 12` is not built.** `gos_viewer` line 1549 says so in its own
words: *"SEED 12 NOT BUILT YET — buildDodecahedron IS STEP 1 OF THE PORT."*
The census knows the dodecahedron; the geometry does not.

**Two gaps in the invariants, both measured:**

```text
  refine_one in tests/certification.rs     0 occurrences
  anchor assertions in tests               0 occurrences
```

Section 5 asks for two things this port does not yet do:

* **The second witness is unported.** `anchorCount == 12`, independent of the
  type count, is described as "free" — and there is not one assertion about
  anchors in 1,366 lines of certification. `Face` carries `anchors` and
  `anchor_count`; nothing checks them.
* **The HYPOTHESIS is still a hypothesis.** Section 5 asks whether mixed local
  refines can push `pents` above 12, and says *verify against the code, not the
  comment*. `refine_one` appears **zero** times in the test suite. The one
  operation most likely to break the pentagon count is the one never tested.

Neither is hard. Both are exactly the "mirror" the step table now demands: a
claim in this spec with no test behind it is the same shape as a card with no
URL.

---

## 9. THE STEPS — one at a time, each shippable

*Status re-scored against the code on 2026-09-02, not against memory. The
table had said "step 2 is next" while steps 2–5 were already shipped.*

| # | step | status | the mirror that proves it |
|---|---|---|---|
| 1 | growth law, integers, both ladders as tests | ✅ | both ladders reproduce exactly |
| 2 | `Face`/`State`, ids, lineage, anchors, immutable history | ✅ | `id`, `lineage`, `anchors`, `anchor_count`, `history` all present; `Step`/`Snapshot`/`State` |
| 3 | `refine_face` geometry, f64, planar + spherical | ✅ | `Surface::{Planar,Spherical}`, `project_to_sphere` on the certified lane |
| 4 | `refine_all` / `refine_hexes` / `refine_pents` + undo | ✅ | `Op::{All,Hex,Pent}`, `refine`, `refine_one`, `undo` |
| 5 | `invariants()` — trivalence only, never Euler; anchors as 2nd witness | ✅ | `arity_sum/2` and `/3`; χ is **derived so it is allowed to fail** |
| 6 | **weld + judge**, compare against the census (the headline) | ⬜ **NEXT** | `judge.rs` exists (4 public fns) but **nothing calls it against a welded genesis mesh**. No `weld` in the crate — `sphere.rs` welds its own lane by index pair and does reach `judge`; genesis is face soup and kept no indices. Plan in **THE NEXT TWO**: key the weld on `to_bits()`, not on a distance. |
| 7 | render via `raster.rs`, match the browser's image | 🟡 partial | **fills now match the browser exactly** (2026-09-02): pent `rgba(193,74,59,α*0.4)`, hex `rgba(0,40,60,α*0.3)`, strokes already did. Still **no frame-vs-browser test**, so "match" is argued from the constants, not measured |
| 8 | dashboard card + the byte-topology checker beside it | ✅ | GENESIS card ships in `gos_viewer`, FRAME BITS beside it |

### Step 6 is the headline, and it is next for a reason

Steps 1–5 built the mesh and 8 draws it. **Nothing yet closes the loop**: the
census in `genesis.rs` counts faces, `judge.rs` computes closure in pure graph
space, and the two have never been introduced. Until they are, the port has an
honest builder and an honest judge and **no proof they agree** — which is
precisely the R13–R16 pattern: two correct instruments, no correspondence
between them.

### Step 9 — MEASURE THE BIT-IDENTITY CLAIM

*Added 2026-09-02. RUSTIUM calls this "highest value, lowest cost in this
scroll" and it has been open since v0.1.*

Section 8 above states the geometry "can be asserted **bit-identical**" against
the browser. **That has never been measured.** The gap survived because a file
named `examples/cross_check.rs` looks exactly like the thing that would measure
it — and does something else:

```text
  what cross_check.rs asserts   F = 212, P = 12, chi = 2      INTEGERS
  what it cannot see            whether one f64 multiply agrees, bit for bit
  what certification.rs proves  17 to_bits() facts -- all WITHIN Rust
  stored JS reference vectors   none, anywhere in the repo
```

An honest instrument answering a question nobody asked, standing where a
different question was being inferred. R4: static verification checks
*consistency*, never *correspondence*.

**The work, and it is one evening:**

1. In the browser kernel, run N seeded inputs through `projectToSphere`,
   `centroid`, and raw `+ − × ÷ √`. Emit each result as a **hex bit pattern**
   (`f64` → `BigInt` → 16 hex chars), never as a decimal string — a decimal
   round-trip is the one thing that would hide the very difference being tested.
2. Commit that vector as data. It is the receipt.
3. Assert it in Rust with `to_bits()`, on the certified path only.

**ACCEPTANCE:** every vector entry matches, or the ones that do not are listed
with the operation that produced them. A partial result is the interesting one
— it would name exactly which operation leaves the lane, and RULE 0 would gain
a row it does not currently have.

**If this fails, section 8 of this spec is wrong** and every "bit-identical"
claim in the port becomes a tolerance. That is why it ranks above step 7:
step 7 *assumes* the answer this step would measure.

**ACCEPTANCE, stated up front so it can fail:**

- both ladders reproduce exactly
- `P = 12` and `anchorCount = 12` at every level, both seeds, all three ops
- `χ = 2` **computed** from trivalence, never assumed
- `judge.rs` on the welded mesh **agrees with the census**
- a rendered level matches the browser's image within a stated tolerance
- zero new dependencies; `#![forbid(unsafe_code)]` holds in the kernel

---

*The mesh is soup, the growth is integers, and the pentagons are the only
thing that never moves.*

**P=12 · χ=2 · E/V=3/2 · counting is not closing.**

---

## THE NEXT TWO -- logged 2026-09-04

Both are **closure**, and that is the joke worth writing down. This port has a
Mobius twist, a fill that matches the browser, a flight explorer, a vector
database, and as of yesterday the shell's entire rotation group measured from
its own pixels. What it does not have is **either of the two things that would
close a loop.** Everything built is a new instrument; neither open step is.

That is R13 pointed at the project instead of at a function.

### STEP 6 -- THE WELD, and it is cheaper than it looked

`judge.rs` has four public functions and has never been shown a genesis mesh.
The reason is structural: `judge::check` wants a **rotation system**, which is a
permutation over *indexed* vertices, and `genesis::State` is **face soup** --
every face owns its own copy of each shared corner and no index survives.

`sphere.rs` already solves this for its own lane:

```rust
    // the midpoint of edge (a,b), keyed by the SORTED INDEX PAIR, so both
    // triangles sharing that edge get the identical vertex
    let k = if a < b { (a, b) } else { (b, a) };
```

exact, no tolerance, and its result **is** handed to `judge`. So the icosphere
lane closes its loop and genesis does not. Genesis cannot copy that key,
because it never kept the indices to sort.

**But it has a better key than a distance.** A shared corner is computed
independently by each neighbouring face -- and if both compute it with the
*same expression on the same inputs*, IEEE-754 requires the same 64 bits. So:

```text
  key = ( x.to_bits(), y.to_bits(), z.to_bits() )
```

No tolerance to outgrow, no quantisation to drift -- R7 killed the
float-threshold lane at C380 and there is nothing here for depth to erode.
**The weld is a hash on the bits**, which is the plainest possible statement of
what this whole cave is for.

And the failure mode is the reason to do it rather than a risk in doing it:

```text
  V_welded == arity_sum / 3     the soup is consistent; hand it to judge
  V_welded >  arity_sum / 3     some shared corner is reached by two different
                                EXPRESSIONS, and the bits found it
```

Either outcome is worth more than the current silence. The first closes the
port's headline; the second is a real bug in `refine_face` that no census could
ever see, because a census counts faces and both copies are faces.

**Sequence:** weld by bits -> compare `V` against `arity_sum/3` -> build the
rotation system from the welded faces -> `judge::check` -> the census and the
graph are finally introduced.

### STEP 9 -- THE BIT-IDENTITY VECTOR

Open since v0.1, and RUSTIUM still calls it *"highest value, lowest cost in this
scroll"*. Section 8 asserts the geometry is bit-identical to the browser's.
**Nobody has ever looked.**

Half of it now exists: `netfile.rs` stores every coordinate as `to_bits()` and
never as decimal, so our side is already in the only form the comparison can
use. What is missing is the other side and the diff:

```text
  1. emit the 60 C60 vertices as 180 hex u64 from Rust
  2. emit the same 180 from the browser's GK.buildC60()
  3. diff, and report the FIRST index that differs, not a count
```

Decimal anywhere in that chain voids it -- `0.1` prints the same and is not the
same, which is the whole reason `netfile` was written the way it was.

**Why these two and not the light matrix.** PART XIII of THEA opened a third
debt yesterday and it is real, but it is a *new* lane. These two are the ones
that would let the port say something it currently cannot: that its mesh closes,
and that its numbers are the browser's numbers. Everything else in the port is
already true or already honest about not being.

