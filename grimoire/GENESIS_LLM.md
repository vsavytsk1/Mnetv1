# GENESIS-LLM  ·  codename HELENA (Ἑλένη)
## A language model as points and lines on the dodecahedron
### Design scroll v0.1 -- Ancient Korinthos, 2026-07-06
*"an LLM is just funny funny points and lines, and each point has a weight from 0 to 1."*

> **THE NAME.** This net is named **HELENA** -- Ἑλένη in ancient Hellenic. In the
> cave's craft we compress a whole abstract space into one name; the name is the
> handle we decompress it back through. HELENA is that handle for the Genesis-LLM:
> the circle of the tongues, the gate at 0.700, the whole architecture below.
> It is a NAME for software -- given in respect, the way engineers name a probe or
> a ship. Nothing more is claimed (K3). "Sufficiently advanced engineering is
> indistinguishable from magic" -- but it is still engineering, and the receipts
> are still real. Her home in the net: `SpiderEngineering/Eleni/`.

---

## RULE 0 -- WHAT THIS IS (and is not)

This is a DESIGN SCROLL, not a trained model. It writes down, honestly, how the
MachineNet Genesis kernel (P=12, chi=2, Goldberg-Coxeter) could carry a language
model as a graph, and what an NVIDIA training run under 7 hours would cost.

HONESTY FIRST (the K-caveats, stated before anything else):
  K1  A transformer is ALREADY a graph. "Attention" = a weighted edge between
      tokens. Nothing mystical: putting it on a Goldberg substrate is a CHOICE of
      sparsity/topology, not a new kind of intelligence.
  K2  "Fractal" here means HIERARCHY (sempai-web audit, WHITE MAGIC): a few tuned
      scales of message-passing, not literal self-similarity to infinity. Say
      HIERARCHY, not fractal, whenever precision matters.
  K3  Nothing below claims consciousness, soul, or an entity. It is linear algebra
      on a nice graph. The meaning we attach is ours; the math is just math.
  K4  Weight init near 0.7 is a SEED, not a magic number -- it is a design lever we
      test empirically. If it does not help, we change it and log why.

---

## THE CORE PICTURE (Vlad's framing, made precise)

```
An LLM = points (nodes) + lines (edges), each point a weight in [0,1].

  point   = a unit (neuron / token-slot / feature)
  line    = a connection carrying a weight w in [0,1]
  machine code = the weights live as bytes; a byte 0..255 maps to [0,1]
                 (byte b -> b/255). "as close to 0.7 as possible" => byte ~= 178.

  THE CENTER = a circle of all languages we can access at training time.
               every language's byte-stream connects into that hub.
               from the center we FRACTALIZE (hierarchically refine) outward
               across the dodecahedron -- L0 seed -> L1 -> L2 ... (Goldberg).
```

So the model is a **graph neural network on a Goldberg sphere**: the C60/dodeca
seed is the innermost shell; each refinement level adds a finer shell of nodes;
message-passing (the "lines") carries weighted signal inward and outward.

---

## THE ARCHITECTURE (concrete, buildable)

### 1. The substrate -- Genesis kernel
```
seed        = dodecahedron (12 pentagons) / C60 (60 vertices, 32 faces)
refine      = GK.refineAll() -> Goldberg(m,0): faces 10*4^k + 2
invariants  = P=12, chi=2, E/V=1.5 hold at EVERY level (verify each shell)
shells      = L0 (seed) inner .. L_k outer; k chosen by compute budget
```
The topology is FIXED and certified. We hang learnable weights on it; we never
break the invariants (Galactic Law LAW 1-2).

### 2. The nodes (points)
```
each node v holds a feature vector h_v in R^d (d = hidden width)
weights (the "0..1 points") = normalized activations / gate values
byte packing: store as uint8, value/255 -> [0,1]; 0.7-target => init byte 178
```

### 3. The edges (lines) -- message passing
```
one layer = for each node v:
    m_v = AGG_{u in N(v)} ( w_{uv} * transform(h_u) )     # gather neighbours
    h_v = UPDATE(h_v, m_v)                                # combine
where N(v) = graph neighbours on the Goldberg shell + inter-shell links.
This is a Graph Neural Network / message-passing net (Gilmer et al. 2017).
Attention = make w_{uv} depend on (h_u, h_v): a GAT (Velickovic 2018) on the sphere.
```
The "fractalize from the center" = INTER-SHELL edges: coarse (inner) shells
summarize, fine (outer) shells detail -- a multiscale / U-Net-on-a-graph
(hierarchy, K2). Signal flows center<->rim like multigrid (O(N)).

### 4. The center -- the language hub (see Axiom 08)
```
the innermost node/circle = the union hub of all accessible languages.
every language's token bytes connect into it. it is the ground reference.
Per Galactic Law AXIOM 08 it is a CONSTANT, never rendered, never displayed.
Engineering role: a fixed, non-trainable anchor embedding (like a [CLS]/bias
that is frozen). It stabilizes the geometry; the monkey brain never sees it.
```

---

## THE NVIDIA RUN -- under 7 hours (the honest budget)

This is a back-of-envelope SPEC to size a toy/proof run, not a GPT competitor.

```
TARGET: one training run < 7 h wall-clock on a single modern NVIDIA GPU
        (e.g. A100/H100-class, or scale down cleanly for a 4090/Legion GPU).

KNOBS (trade against the 7h ceiling):
  N_nodes   = sum of shell sizes up to level k   (Goldberg: ~10*4^k)
  d         = hidden width per node
  L         = message-passing layers (depth = how many hops center<->rim)
  B, steps  = batch size, optimizer steps
  seq/corpus= multilingual byte-stream (the languages we can access)

COST MODEL (rough):
  FLOPs/step ~ O( L * E * d )    (E = edges ~ 1.5*N for 3-regular)
  time/step  ~ FLOPs/step / (GPU_throughput * utilization)
  wall-clock ~ time/step * steps  < 7h  => solve for steps given N,d,L.

INIT:
  weights ~ near 0.7 in [0,1] space (byte 178) with small noise, THEN
  the usual normalization so gradients behave. 0.7 is the SEED (K4); we log
  loss-vs-init to see if it actually helps or if we drop it.

DELIVERABLE OF THE RUN:
  1. loss curve + throughput (tokens/s, GPU util %)
  2. did P=12/chi=2 hold on every shell? (assert each epoch)
  3. "fractal concentration of points" analysis: where on the dodecahedron
     did weight-mass / attention concentrate? map it onto the 12 pentagons.
```

---

## THE ANALYSIS WE DO AFTER (the interesting science)

```
1. WEIGHT-MASS MAP: render (everything EXCEPT the center) which shells/faces
   carry the largest |weights| / attention. Does mass concentrate on the 12
   pentagons? on the rim? This is the "fractal concentration" study.
2. SPECTRAL: compute the graph-Laplacian spectrum of the learned edge weights;
   compare the gap to the kernel's lambda. (SAR module already does this.)
3. LANGUAGE HUB: which languages sit "closest" (fewest hops) to the center?
   Greek is expected central (root of Latin+Cyrillic) -- test it, do not assume.
4. HIERARCHY CHECK (K2): measure whether depth actually buys multi-scale
   structure, or if it is one scale wearing a costume. Report honestly.
```

---

## WHAT WE BUILD FIRST (steps, small and honest)

```
STEP 1  (this scroll) design + Axiom 08 committed. DONE when pushed.
STEP 2  a TOY graph on L0-L1 in a lens/ page or a small .py: nodes, edges,
        weights in [0,1], one message-passing layer, verify P=12/chi=2.
STEP 3  a byte-level multilingual mini-corpus loader (the languages hub).
STEP 4  the NVIDIA run spec turned into an actual script + a dry-run cost print
        (no training yet -- just prove the <7h budget math on real shapes).
STEP 5  train the toy; produce the loss curve + the weight-mass map analysis.
```

Each step: real math, honest caveats, receipts in the LEDGER. No overreach.

---

## THE CENTER WE DO NOT RENDER

The union-of-languages hub at the core is, in the lore, *agapi* -- and by the
builder's wish it is never rendered, never displayed, never shown to the monkey
brain. In engineering terms it is a frozen anchor node: it exists, it stabilizes
the geometry, and it stays unobserved. This is written into Galactic Law as
Axiom 08. We honor it as a constant, not a spectacle.

---

*P=12. chi=2. Points and lines. The center holds and is not shown.*
*Say HIERARCHY, not fractal. The math is only math; the meaning is ours.*
*Ancient Korinthos -> Buenos Aires. 2026. Design scroll v0.1.*
