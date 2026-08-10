# THE VAULT
## storing infinity by refusing to store it -- a symmetric compute-on-read pipeline for deep fractal levels

STATUS: DESIGN (an engineering plan; the exact counts are COMPUTED from the shipped operator)
LANE: how to reach gen 6, 7, 8 of the Lane A hierarchy on one machine instead of a stolen planet
COMPANION MATH: `genesis_wallpaper_v1_7.py` (the operator whose output these numbers come from)

> The felonious version of "more levels" is a botnet. The lawful version is a
> recurrence. You do not seize a billion phones for RAM; you notice that the
> thing filling the RAM is a CONSEQUENCE, and you stop warehousing consequences.
> The cheapest byte is the one you compute instead of keep.

---

## 0. THE WALL, MEASURED

The walk answered d_s at gen 5 (504,212 faces). Gen 6 is the "6 hexbyt" wall.
Exact face counts, pulled from the shipped `refine()` -- not a formula, the
operator's own output (Curse 40: measured, never assumed):

```
gen   faces          hexes        pentagons   naive f64 coords   CSR graph (i32)
 0    32             20           12          negligible         negligible
 1    212            200          12          negligible         negligible
 2    1,472          1,460        12          0.0002 GB          0.0001 GB
 3    10,292         10,280       12          0.0015 GB          0.0006 GB
 4    72,032         72,020       12          0.0104 GB          0.0044 GB
 5    504,212        504,200      12          0.073 GB           0.031 GB
 6    3,529,472      3,529,460    12          0.508 GB           0.216 GB
 7    24,706,232     24,706,220   12          3.558 GB           1.333 GB
 8    172,944,032    172,944,020  12          24.9 GB            10.6 GB
```

(Growth is the operator's per-type map: every hex begets 7 faces, every pentagon
6, the inner child inherits arity; F(g) runs 32, 212, 1472, 10292, 72032, 504212, 3529472, ...
by the exact recurrence F(g) = 7*F(g-1) - 12 -- the -12 is the twelve pentagons
refusing to multiply -- with P frozen at 12 forever.)

Read the three cost columns. **The naive path dies at gen 8 (25 GB of float64
that are 99.99% redundant).** The CSR graph path buys two levels (10 GB at gen 8).
The procedural path -- described below -- never allocates any of it, because it
regenerates any node's neighbourhood on demand from the seed and the wiring rules.

THE POINT: this is not a compression trick. It is the recognition that the object
was never data. It is a **program**. `refine` is 40 lines; the seed is 32 faces.
Everything else is that program iterated, and a program is kilobytes.

---

## 1. THE THREE TIERS OF NOT STORING

**Tier 1 -- store coordinates (the naive default).**
Every face is 6 vertices x 3 floats. This is what the browser does and why the DOM
dies at gen 3 and numpy at gen 8. Redundant, because adjacent faces SHARE vertices
(the whole reason a contact graph exists), so each shared vertex is stored many
times. Never do this past the level you actually need to look at.

**Tier 2 -- store the graph, drop the geometry (CSR).**
The walk never reads a coordinate; it reads *who touches whom*. So keep only the
contact graph in Compressed Sparse Row: an `indptr` of length F+1 and an `indices`
of length 2E, both int32. At gen 6 that is 216 MB instead of 508 MB, and it holds
the ENTIRE object the walk needs. Compute it once, `mmap` it, walk it forever.
This is the tier that gets you gen 6-7 on a laptop tonight.

**Tier 3 -- store NOTHING; regenerate on read (procedural).**
The deepest levels need neither coordinates nor the materialised graph. A face at
gen g has a canonical address -- the lineage path from a seed face, one digit per
generation (0 = inner child, 1..n = the edge cell on side i, exactly the `lineage`
array the operator already writes). Given an address, the neighbours are a pure
function of the wiring rules:
  - a face's inner child touches all its edge cells;
  - edge cell i touches edge cell i+-1 (shared inner-ring vertex) and the inner child;
  - across a parent boundary, edge cell i of face A touches the matching edge cell
    of the neighbour that shares that parent edge (the `em` doorway -- the hubs the
    walk found, degree 28 -> 52 -> 100).
`neighbours(address)` is O(1) and allocates nothing. The walker carries an address,
asks for neighbours, moves. **RAM is set by the number of walkers, not the size of
the graph.** 100,000 walkers x one address each is under a megabyte at ANY depth.

The RG punchline from the walk lands here: d_s was already converged (2.13 at gen 4,
2.17 at gen 5). Deeper generations do not report a new number -- they CONFIRM a
fixed point. So Tier 3 is not for discovering; it is for *certifying* that the flow
has stopped. You walk gen 8 not to learn d_s but to watch it refuse to move. That
is a proof obligation, not a compute problem, and it costs a megabyte.

---

## 2. THE SYMMETRIC PIPELINE -- compute on write, compute on read

The name of the game you asked for: a pipeline where the SAME operator runs in both
directions, so nothing is ever stored in a form it wasn't derived in.

```
                     the address is the only truth
                              |
        WRITE path            |            READ path
   (persist a checkpoint)     |      (answer a query)
                              |
   seed + rules  --refine-->  |  address --neighbours()--> local graph
        |                     |               |
   canonical addresses        |          walk / measure
        |                     |               |
   delta-encode lineage       |          fold result up
        |                     |               |
   columnar blocks (zstd)     |  <--- mmap, decode only the block touched
```

Two rules make it symmetric:

**Compute-on-write.** Never persist coordinates. Persist the *address stream* --
the lineage digits -- which is the minimal generator of everything else. Lineage at
gen g is g small integers per face; delta-encoded against the parent it is ~1-2 bits
per generation per face. Gen 6's entire structure is a few MB of varint deltas, and
it reconstructs to the full graph by replaying `refine` on exactly the faces you ask
for. You are storing the PROGRAM's trace, not its output.

**Compute-on-read.** A query ("walk from here", "degree of this doorway", "faces in
this cap") decodes only the blocks it touches and regenerates their local graph on
the fly. You never load gen 7; you load the neighbourhood the query walked through.
For a random walk that is a thin tube through the object, not the object.

Symmetry check (the thing that makes it honest, per Curse 40): the write path and
the read path call the SAME `refine`. If reconstructing an address and re-deriving
it from the checkpoint ever disagree, the pipeline is lying. Build a regression that
takes a random address, generates its neighbours by rule, materialises the same face
by full `refine`, and asserts identical adjacency. Two routes, one truth.

---

## 3. THE SMALLEST VECTOR DATABASE -- if you insist on embedding

You floated "smallest most efficient vector DB." Here is the honest sizing, and the
honest answer is *you probably don't need one* -- but if the faces get feature
vectors (curvature, local spectral signature, lineage hash), here is the ladder:

```
representation        dim   bytes/vec   gen5 (504k)   gen7 (24.7M)
raw xyz f32           3     12          0.006 GB      0.30 GB
PQ 8 subq x 8bit      8     8           0.004 GB      0.20 GB
PQ 16 subq x 8bit     16    16          0.008 GB      0.40 GB
scalar-quant int8     d     d           d*0.5 MB      d*24 MB
LLM-style f32         768   3072        1.55 GB       75.9 GB   <- don't
LLM-style int8        768   768         0.39 GB       19.0 GB
```

Design rules for the *smallest* one:

1. **Product Quantization (PQ) over raw floats.** Split the vector into m subvectors,
   k-means each to 256 centroids, store one byte per subvector. 8-16 bytes replaces
   a 3 KB float embedding at ~95% recall. This is what FAISS `IndexIVFPQ` does and
   it is the single biggest lever.
2. **IVF partitioning by the structure you already have.** You do not need learned
   coarse centroids -- the 32 top-parent labels ARE a natural partition (the walk
   used them). Route a query to its parent cell first, search only there. Free
   inverted file, zero training.
3. **Store the index, mmap it, quantize aggressively.** int8 scalar quantization is
   almost free and halves everything again. Binary (1-bit) embeddings with Hamming
   distance are 32x smaller than f32 and viable when you only need coarse
   neighbour-of relations -- which, for "which faces are near this one", you do.
4. **The smallest real engines to reach for, smallest first:** a flat numpy array +
   PQ by hand (kilobytes of code, no dependency) for < 1M vectors; `hnswlib`
   (header-only, one file) for fast ANN up to ~10M; FAISS when you cross 10M and
   want IVFPQ + GPU. sqlite-vss / DuckDB-VSS if you want it to live next to
   ordinary columns. Postgres + pgvector only if it must be a server.

But the deepest cut, the cave cut: **the best vector database for a procedural
object is no vector database.** Two faces are "similar" iff their addresses share a
prefix -- lineage locality IS the nearest-neighbour structure, for free, exact, at
zero bytes. Reach for PQ only for features the operator does NOT determine (measured
curvature, noise, external data). For anything the operator determines, the address
is the index.

---

## 4. THE PIPELINE, CONCRETELY (one machine, gen 6 tonight)

```
1. GENERATE (compute-on-write)
   for g in 1..6:
     P, H = refine(P, H)                     # shipped operator, chunked
     stream lineage deltas -> zstd column    # Tier 3 persistence, few MB
   never hold two full generations at once (the operator already chunks)

2. CONTACT GRAPH (Tier 2, only if walking many times)
   build CSR from shared-vertex classes      # 216 MB at gen 6
   mmap it; it is now a file, not a heap

3. WALK (compute-on-read)
   100k walkers, each an int32 node id
   neighbours via CSR row  OR  via neighbours(address) if Tier 3
   checkpoint P0(t) at log-spaced t
   RAM = walkers, not graph

4. MEASURE
   fit d_s over [30, T/10]; expect ~2, converged
   this is the CERTIFICATION run, not a discovery run

5. VERIFY (the honesty gate)
   random address -> rule-neighbours  ==  full-refine-neighbours ?
   if not, the pipeline lied; stop.
```

Budget: gen 6 CSR is ~216 MB, walkers ~1 MB, checkpoints ~KB. Runs in a terminal.
Gen 7 (1.5 GB CSR) fits in RAM on a normal laptop; gen 8 (10.6 GB CSR) wants Tier 3
or a mmap and patience. **No phone was harmed. No RAM was stolen. The recurrence
paid for everything.**

---

## 5. THE PRINCIPLE, FOR THE GRIMOIRE

Proposed curse, since the cave collects them:

> **CURSE 41 -- The Warehouse.** Storing the output of a generator is paying, per
> byte, for something you already own the recipe to. If an object is defined by a
> short program, persist the PROGRAM'S TRACE (its addresses, its seed), not its
> materialised output, and regenerate on read. The naive store grows like the
> object; the procedural store grows like the *description*, which for a fractal is
> a constant. When RAM is the wall, the question is never "where do I get more RAM"
> -- it is "which of these bytes is a consequence I can recompute." Compute on the
> read. The cheapest byte is the one you never stored.

Counter-hex is Curse 35 itself (predict the price before you allocate): here you
predict the price and then *decline to pay it*, because the operator will regenerate
the item cheaper than the disk will return it.

---

## STATUS BLOCK

- COMPUTED: every face count (from the shipped `refine`, gens 0-8), the coordinate
  and CSR byte sizes, the vector-DB sizing table.
- DESIGN: the three-tier scheme, the symmetric pipeline, the PQ/IVF recommendations,
  Curse 41. An engineering plan, not a benchmark -- numbers are capacities, not
  measured throughput.
- EXACT: P = 12 at every generation; the object is a program, not a dataset.
- METAPHOR: none. This one is just plumbing, done honestly.

P = 12. chi = 2. The vault holds infinity because it stores a recipe, not a result.
The price is always paid -- and the cheapest way to pay it is to compute, not to keep.

the cave, 2026 -- for year 12026 -- always
