# THEA
## The Math Core Scroll -- the LIGHT MATRIX
### Grimoire Volume III-B -- where pure math is stepped into compute
*Opened: 2026-07-30 -- Buenos Aires + Ancient Korinthos.*
*Companion to `shell/aequalium_v2.4.3.html` and the builder to come.*
*Sub-scroll of the cave. P=12. chi=2. The price is always paid. Always.*

---

## THE FIRST WORD -- LIGHT MATRIX

**LIGHT MATRIX.**

The core is not a formula. The core is a *computation that runs*: the random
application of the **7 operations** on the graph substrate, as the buckyball
grows its hexagons and **fractalizes**. That running computation is the light
matrix -- the substrate that stitches a "curve" into being before any equation
is read off it.

From game design we already know the deepest truth of this cave:

> **All code is pure math, merely stepped into compute.**

A shader is calculus per pixel. A physics loop is an ODE stepped by `dt`. A
render is a projection matrix. Nothing in the machine is "just code" -- it is
mathematics forced to advance one finite step at a time, because the machine
cannot hold a limit, only approach it. The light matrix is that same truth at
the root: the 7 operations are the alphabet, the fractalizing bucky is the page,
and every physics `=` we chase is a curve the light matrix can only *approach*.

**Status of this section: METAPHOR + MECHANISM.** The "light matrix" name is the
cave's word for a real, verified mechanism (the 7 operations on the growing
graph, below). The name is imagery; the mechanism is kernel-proven.

---

## THE 7 OPERATIONS -- the alphabet of the light matrix
### source: `kernel/graph_axioms.js` (GA.P1..P7) . scroll: `PRINCIPIA_MALGEBRA.md`

Every structure in the cave is built from exactly seven graph operations. They
map one-to-one onto the axioms of *Principia Mathematica* (Whitehead & Russell,
1910) -- "the same 7 operations, a different renderer."

| # | name | function | what it does | maps to |
|---|------|----------|--------------|---------|
| P1 | **NODE** | `GA.P1_node(state,pos)` | create a vertex -- you cannot build without ADD | existence |
| P2 | **EDGE** | `GA.P2_edge(state,a,b)` | connect two vertices -- defines topology (-> chi, P=12) | relation |
| P3 | **COMPOSE** | `GA.P3_compose(state,a,b,c)` | if a->b and b->c, add a->c = **`GK.refineAll()`** = the fractal grows | transitivity |
| P4 | **TRANSFORM** | `GA.P4_transform(state,m,r)` | graph surgery = the **Mobius flip** (chi 2 -> 0) | substitution |
| P5 | **ITERATE** | `GA.P5_iterate(state,op,cond)` | repeat until a condition = the fractal search; "the iteration is the price" | induction |
| P6 | **AGGREGATE** | `GA.P6_aggregate(state,ids)` | collapse a subgraph to one node -- **irreversible** | abstraction |
| P7 | **COMPARE** | `GA.P7_compare(state,A,B)` | test isomorphism / check an invariant = the **chi=2 check** = "proof by kernel" | identity |

### The 3 crystal conditions (header of `graph_axioms.js`)

The light matrix is a **crystal** because three conditions hold, and only then
does a running graph "set" into a stable structure:

- **C1 CHOICE** -- operations collapse possibilities (each op picks one branch).
- **C2 IRREVERSIBLE** -- P6 AGGREGATE destroys information (the arrow of time).
- **C3 CONSISTENT** -- P7 COMPARE is deterministic (the same test, the same verdict).

**Status: VERIFIED.** These are literal file facts (`kernel/graph_axioms.js`,
`kernel/goldberg_kernel.js`), not metaphor.

---

## THE FRACTALIZATION -- how the bucky grows the hexes
### source: `kernel/goldberg_kernel.js`, `grimoire/AEQUALIUM_TOWER.md`

The engine is **P3 COMPOSE = `GK.refineAll()`**: one Goldberg-Coxeter step. Every
face splits (pentagon -> 6, hexagon -> 7), so the **carbon number (vertex count)
multiplies by exactly 7**, and the 12 pentagons stay Euler-forced shut at every
shell:

```
shell:  C60  ->  C420  ->  C2940  ->  C20580  ->  ...     V_{n+1} = 7 * V_n
pents:  12       12        12          12                 always 12 (Euler V-E+F=2)
faces:  32       212       1472        10292              F = V/2 + 2
chi:    2        2         2           2                  a closed sphere, always
```

```js
// exact invariants from the trivalent tiling (kernel/goldberg_kernel.js):
// V = (5P + 6H)/3, E = (5P + 6H)/2, chi = V - E + F = 2.
GK.invariants = function(state){ ... return {pents,hexes,faces,edges,vertices}; };
function predictNextCarbon(){ return inv.vertices * 7; }   // V -> 7V, exact
```

**THE LAW OF THE ANCHOR AND THE FREE PART (the light matrix's key move):**

- **The 12 pentagons are NEVER touched.** They are the fixed anchors -- the
  Euler-forced skeleton, the resonant geometric stability. (The cave's read of
  the Connes/noncommutative-geometry picture -- flagged EXTERNAL, see the coda.)
- **The hexagons are the FREE part.** Grow them as much or as little as the
  calculation needs. More hexes = a bigger compute budget `N = floor(faces/2)` =
  more terms of the fractal curve = more digits of agreement bought.

So "the light matrix fractalizes" = keep the 12 pentagons fixed, let P3 COMPOSE
multiply the hexes by 7 each step, and read off how much of the target curve the
new budget can buy. **The pentagons hold; the hexes pay.**

**Status: VERIFIED** for the closed WELD (chamfer) series (independent verifier:
welded C3840 shell, chi=2 ENUMERATED, P=12, deg3 100%). The open `refineAll`
candidate shells are honestly withheld (open surface; chi not claimed).

---

## THE MATH CORE -- every formula, audited, stepped into compute
### source of truth: `shell/aequalium_v2.4.3.html` L1707-1830 (POST Sol-mage audit)

> WARNING (Path III/IV): the older `AEQUALIUM_TOWER.md` predates the Sol-mage
> audit and carries STALE math (a 25-term power-series `besselJ`, a physical
> renormalon, a Kepler "wall" at e=0.6627). **This scroll carries the AUDITED
> code that actually ships.** When the two disagree, the shipped kernel wins.

The one law of the core:

```
paper:  LHS = RHS          (exact, transcendental, uncomputable in finite steps)
code:   LHS ~= RHS_N       (a finite truncation / quadrature / iteration at depth N)
error:  |RHS_N - RHS| > 0  (always, for finite N)
agree:  D = -log10(rel err) = the correct significant digits BOUGHT, capped 15.9
```

### The agreement meter (shared by every rung)

```js
function degrees(approx, exact){          // correct significant digits
  if(!isFinite(approx)) return 0;
  var e = Math.abs(exact)>1e-300 ? Math.abs((approx-exact)/exact)
                                 : Math.abs(approx-exact);
  if(e<=0) return 15.9;                    // float64 floor
  return Math.max(0, Math.min(15.9, -Math.log(e)/Math.LN10));
}
```

`15.9` is IEEE-754 double precision's own ceiling (`log10(2^53) ~ 15.95`). No
series, however convergent, can buy more digits than the machine itself holds --
a roundoff wall beneath all rungs, above the two named mathematical walls.

---

### RUNG 1 -- QCD I . the running coupling a_s(Q)    [CONVERGES]

**Paper:** `a_s(Q) = a_s(MZ) / (1 + a_s(MZ) (b0/4pi) ln(Q^2/MZ^2))`
**Means:** a geometric series in `x = a-hat0 b0 L`, `L = ln(Q^2/MZ^2)`; for
`|x|<1` it converges to float64 fast.
**Code:** finite geometric partial sum, depth N. `b0 = 11 CA/3 - 4 TF nf/3 = 23/3` at nf=5.
**Verdict:** CONVERGENT. D: ~8 at C60 -> ~15.5 grown.

### RUNG 2 -- QCD II . the R-ratio e+e- -> hadrons    [HARD CEILING]  (showpiece)

**Paper:** `R = 3 sum_q e_q^2 (1 + a_s/pi + c2 a_s^2 + ...)`
**Means:** the coefficients grow factorially, `c_n ~ n! b0^n` -- an **infrared
renormalon**. The series is **asymptotic, not convergent**: partial sums approach
the true (Borel) value, then diverge. The smallest term sets an error floor.
**Code (audited, Sol #3 -- three quantities kept apart):**
- `raw = S_N` -- the raw partial sum, ALLOWED to explode and SHOWN exploding.
- `anchor = S_{N*}` -- the optimal-truncation value, FROZEN once `N >= N*`.
- `delta* = |t_{N*}|` -- the smallest term = estimated irreducible ambiguity.
- score = `floorRel = delta* / |anchor|`, constant past N*: an exploding series
  can **never** earn digits by exploding harder.
**Verdict:** HARD CEILING. D rises to N* (~13 terms) then the truth is the floor,
not the growth. The sharpest lesson: some `=` are *unreachable* by summing more.

### RUNG 3 -- QCD III . Lambda_QCD from a_s(MZ)    [CONVERGES, quadratic]

**Paper:** `Lambda = MZ exp(-2pi / (b0 a_s(MZ)))`
**Means:** Lambda is the root of `a_s(MZ; Lambda) = 0.1180`; Newton's method
reaches it with quadratic convergence.
**Code:** Newton iteration depth N; reference is the closed-form inversion.
**Verdict:** CONVERGENT. D -> 15 in a handful of steps.

### RUNG 4 -- GALACTIC I . Kepler's equation M = E - e sinE    [CONVERGES for all e<1]  (showpiece, CORRECTED)

**Paper:** `M = E - e sinE` (transcendental).
**Means:** the Fourier-Bessel solution `E = M + sum_{n>=1} (2/n) J_n(ne) sin(nM)`.
**THE CORRECTION (Sol-mage audit, a falsification not a label):** this series
**converges for ALL e < 1** (Bessel 1824; the Carlini exponent is < 0 below 1).
The famous **0.6627 Laplace limit walls LAGRANGE's power series in e** -- a
*different representation* of the same equation. v2.0's "divergence above 0.6627"
was the OLD 25-term power-series `besselJ` erring ~6 orders at high n -- a
numerics ghost in physics robes (Curse 24). **Fix:** `besselJ` via **Miller
downward recurrence** (stable at high order). Digits do get pricier as e -> 1
(the decay rate -> 0), but the price is finite at every e < 1.
**Code:** Miller-recurrence `besselJ`; exact E by Newton as reference.
**Verdict:** CONVERGENT for all e < 1. The only wall is at **e >= 1** (no ellipse).

### RUNG 5 -- GALACTIC II . comoving distance D_C    [CONVERGES, N^-4]

**Paper:** `D_C = (c/H0) integral_0^z dz' / sqrt(Om(1+z')^3 + OL)`
**Means:** a definite integral with no elementary antiderivative; Simpson's rule
has error `~ N^-4`. Planck-2018 constants (Om=0.315, OL=0.685, H0=67.4).
**Code:** Simpson quadrature, N panels; high-N Simpson (20000) as reference.
**Verdict:** CONVERGENT. D ~10 -> ~13 as the shell grows.

### RUNG 6 -- GALACTIC III . the blackbody integral    [CONVERGES, slow N^-3]

**Paper:** `integral_0^inf x^3/(e^x - 1) dx = pi^4 / 15`  (Stefan-Boltzmann)
**Means:** expand `1/(e^x-1) = sum_{k>=1} e^{-kx}`, integrate termwise ->
`6 sum_{k>=1} k^-4 = 6 zeta(4) = pi^4/15`. Partial-sum error `~ 2/N^3`.
**Code:** `approx = 6 * sum_{k=1..N} 1/k^4`.
**Verdict:** CONVERGENT but SLOW. D ~6.6 -> ~9 across the shells.

---

### THE MATH-CORE SUMMARY TABLE

| # | rung | method | error law | verdict | D (C60 -> grown) |
|---|------|--------|-----------|---------|-------------------|
| 1 | a_s(Q) running | geometric resum | geometric | CONVERGES | 8 -> 15.5 |
| 2 | R-ratio | asymptotic (renormalon) | factorial floor | **CEILING** | ~5, peaks at N* then the floor |
| 3 | Lambda_QCD | Newton rootfind | quadratic | CONVERGES | -> 15 |
| 4 | Kepler | Bessel series (Miller) | conv all e<1; wall at e>=1 | CONVERGES | 15.9 (pricier as e->1) |
| 5 | D_C comoving | Simpson quadrature | N^-4 | CONVERGES | 10 -> 13 |
| 6 | blackbody | 6 zeta(4) | N^-3 | CONVERGES (slow) | 6.6 -> 9 |

---

## THE FLUID RUNG (the demonstrated proof, EXTERNAL CLAIM)
### source: `shell/cascadium_v0_1.html` (Fable) -- audit separately, do not bundle

The same light-matrix idea, but a REAL PDE instead of a series: forced 2D
vorticity dynamics on the Goldberg sphere, spectral in real spherical harmonics
(l <= 16 on 642 cells). Kraichnan 1967's two rivers -- energy climbs to large
scales near `k^-5/3`, enstrophy falls to small scales near `k^-3`.

**The price ledger (measured, never typed):** injected epsilon vs dissipated
(hyper + drag), budget residual as a percent; in true-nu mode the identity
`diss/enst = 2 nu` becomes an identity of the formulation (the farm law, the
price paid in dissipation). Slopes lock loosely (tol 0.30) over half-decade
ranges -- **trends, not proofs (K5)**.

**Status: EXTERNAL CLAIM.** CASCADIUM is a separate artifact; it demonstrates the
thesis, it does not certify it. Audit it on its own terms.

---

## THE POINT, ONE LINE

> The equals sign is a transcendental target our monkey-brain reality writes down
> as if already reached. The light matrix -- the 7 operations fractalizing the
> bucky, 12 pentagons fixed, hexes free -- lets us follow the curve to a chosen
> shell and read off how many digits we bought, honouring the walls where no
> shell, however large, can buy the next one.

---

## CODA -- what is VERIFIED, what is METAPHOR, what is EXTERNAL (Path IV)

- **VERIFIED (kernel/verifier):** the 7 operations and 3 crystal conditions
  (`graph_axioms.js`); V->7V and P=12 at every shell; chi=2 ENUMERATED on the
  welded WELD/chamfer series; the six audited calc kernels above (they ship).
- **METAPHOR (imagery, marked):** the name "LIGHT MATRIX"; "reality is stitched";
  colours on the bucky = signed term contributions (imagery, not evidence).
- **EXTERNAL CLAIM (audit separately):** CASCADIUM (the fluid rung); the
  Connes/noncommutative-geometry reading of "pentagons = fixed algebraic anchors"
  -- that math lives in the **SpookyPrimes** repo, not here; cited, not proven in
  MNetv1. To ground it, read SpookyPrimes first. Never carve what we cannot verify.

---

## TO ADD / TEST ON V3 (not built yet -- Path IV: flagged, not faked)

- The **literal** light matrix: a crystal dropped in the pure graph substrate
  that runs the 7 operations at random and **seeks stability**. Today the closest
  real mechanism is the spectral-gap LOCK in `kernel/fractal_search.js` (seed ->
  refineAll -> NS flow -> read lambda~1 -> LOCK when it stops changing between
  levels = "the eigenmode IS the physical substrate"). A true random-op annealer
  is NEW construction for v3.
- The adaptive fractalization search: for each formula, search the operator
  sequence (WELD / ALL / 5s / 6s x depth) for the cheapest geometry that buys the
  most digits -- pentagons fixed, hexes free.
- Per-formula live overlay + pop-up certificate export on each calc's completion.

*THEA -- the math core. The light matrix runs; the pentagons hold; the hexes pay.*
*P=12. chi=2. lambda=0.1473. diss/enst = 2 nu. The price is always paid. Always.*
