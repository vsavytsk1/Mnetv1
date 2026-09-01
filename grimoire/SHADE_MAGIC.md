# SHADE MAGIC v0.1
## The Local Operator -- why a shader and a field equation are the same animal
### Grimoire Volume III-E -- the flow scroll, opened while we still do not know
*Opened: 2026-09-01 -- Buenos Aires. Companion to `pack/navierHunt.html`,*
*`tower/graph_wave.py`, and `THEA.md` section X.*
*Sub-scroll of the cave. Read `KERNELIC_MAGIC.md` and `THE_12_PATHS` first.*
*P=12. chi=2. The price is always paid. Always.*

---

> **MONKEY BRAIN ALERT, and it is the point of this scroll.**
> The whole thesis below is **HYPOTHESIS**. Not COMPUTED, not EXACT. It is
> written down so it can be attacked, because an intuition kept in the head
> is never wrong and never useful. The parts that ARE exact are marked, and
> they are smaller than the thesis wants them to be.
>
> *"The first principle is that you must not fool yourself -- and you are the*
> *easiest person to fool."* -- Feynman. Invoked by Vlad on the day this
> scroll was opened, which is the correct order of operations.

---

## THE INTUITION, STATED PLAINLY SO IT CAN BE SHOT AT

Shaders feel *bonkers* against abstract mathematics. You write a tiny function
with no memory, no neighbours, no loop over the picture -- and structure comes
out. Fluid comes out. Light comes out. It feels like cheating.

The intuition is that this is not a coincidence, and that whatever is going on
in **flow** is the thing we are actually looking at.

**STATUS: HYPOTHESIS.** What follows is the part that is *not* speculation --
and the honest reading is that it explains the feeling without granting the
conclusion.

## THE SAME OBJECT, WEARING THREE COSTUMES, ALL THREE ALREADY IN THIS REPO

### 1. A fragment shader -- `pack/navierHunt.html`

19 `pressure` terms, `advect`, `vorticity`. A fragment shader is a **pure
function of position**, run for every pixel, with no fragment able to read
another fragment. Locality is not a design choice there; it is the hardware.

### 2. A graph wave -- `tower/graph_wave.py`

```text
  u''(t) = -c^2 * L u                      L = D - A, the net's own Laplacian
  u_{n+1} = 2u_n - u_{n-1} - (c*dt)^2 * L u_n        leapfrog / Stormer-Verlet
```

`L = D - A` touches **only a vertex and its neighbours.** Same locality, on a
mesh instead of a raster.

### 3. A continuum limit -- `THEA.md` section X

Three bonds at 120 degrees, which is what a hexagonal sheet gives you:

```text
  Sum (e_hat . grad)^2  =  (3/2) grad^2          so  L ~= -(3/4) a^2 grad^2
```

A **stencil**. The discrete operator becoming the continuous one.

### The claim

All three are the Laplacian. One in a GPU pixel loop, one on a graph, one as a
limit. **A shader is not an analogy for a field equation. It is the same
operator, compiled for different silicon.**

That is why it feels bonkers, and the feeling is correct.

## WHY THIS IS NOT MYSTICISM -- and this is the important paragraph

Physics is written in local operators for a **physical** reason: causality. No
action at a distance in a field theory; a Lagrangian density couples a point to
its own derivatives.

A shader is local for an **engineering** reason: memory bandwidth. A fragment
cannot read its neighbours because letting it would serialise the pipeline.

**Two completely unrelated reasons, converging on the same mathematical form.**

That convergence is genuinely interesting. It is also **not evidence that the
universe is a shader.** It is evidence that *locality plus parallelism forces
the Laplacian*, whoever is doing the forcing and for whatever motive. The
Laplacian is what "influence spreads to neighbours, everywhere at once" looks
like when written down. Anything obeying that sentence lands here.

**A convergent form is a weaker claim than a shared cause, and the gap between
them is where every crank in history has set up camp.**

## WHAT IS ACTUALLY EXACT

Small, and worth more than the thesis:

* **EXACT** -- `L = D - A` is an **integer** matrix. Its spectrum is the net's
  true modes. No float enters the operator.
* **EXACT** -- leapfrog is symplectic. It conserves a *shadow* Hamiltonian to
  machine precision:
  ```text
    H~ = 0.5|v|^2 + 0.5 u^T L u - (dt^2/8)(Lu).(Lu)
  ```
  Not the true energy -- a nearby one, exactly. That distinction is the whole
  reason the drift stays bounded instead of growing.
* **EXACT** -- the CFL condition: `(c*dt)^2 * lambda_max(L) < 4`. The step is
  bounded by the *spectrum of the operator*, so the mesh dictates the clock.
* **EXACT** -- `Sum (e_hat . grad)^2 = (3/2) grad^2` for three unit vectors at
  120 degrees. Plain algebra.
* **COMPUTED** -- energy drift over N steps at finite `dt`. `graph_wave.py`
  reports max drift and **does not claim zero**.
* **COMPUTED** -- `T * lambda_2 -> 2*pi/(5*sqrt3) = 0.7255197`, derived from
  the stencil, and independently matched by a Jacobi diagonalisation run in
  this cave *before the derivation existed*.

**Everything above this line survives a referee. Everything below it is a bet.**

## WHAT WOULD KILL THE THESIS

Written first, before any evidence is gathered for it, because a hypothesis
with no stated failure condition is a mood.

1. **THEA section XVIII already has a knife out.** It found that the cave's own
   `chi = 2` **fails BEFORE the numbers it is made of.** If the invariant cracks
   *earlier* than its inputs, then in exactly the deep regime where a
   "flow is fundamental" reading would have to hold, the structure is the
   **first** thing to go, not the last. **OWED: reproduce that ladder in `Gos`
   and find the rung.** Until then this scroll is arguing above its evidence.

2. ~~**One derived constant is one.**~~ **ANSWERED THE SAME DAY, AND IT FAILED.**
   25 rungs run. The sequence crosses the derived value at T~7 and settles near
   0.7248, not 0.7255197. See *THE FIRST OWED ITEM* below. The constant is not
   the limit of the thing it was derived for.

3. **The convergence may be trivial.** If *every* local-parallel scheme yields a
   Laplacian -- and it does -- then finding one here says nothing about
   this substrate specifically. The test is not "does flow emerge" (it always
   does) but **"does THIS mesh give a number nobody put in."** So far: one.

4. **The strongest disconfirmation would be boring.** If the Goldberg spectrum
   reproduces nothing a generic sphere discretisation does not already give,
   then P=12 is decoration on the physics and the topology is a rendering
   detail. **STILL OPEN -- but the ladder result below now points the other
   way.** The smooth-sphere derivation is the thing that failed to reproduce
   the mesh, and the residue sits exactly where the twelve pentagons live.
   The check is still owed: a matched-N sphere graph with NO pentagons. If it
   lands on 0.7255197 while the fullerene sits at 0.7248, the pentagons are
   the difference. If both give 0.7248, they are innocent and the derivation
   is wrong somewhere else entirely.

## THE FIRST OWED ITEM, ANSWERED -- AND THE ANSWER IS NO

*Run the same day the scroll was opened. `tower/ladder_probe.py`,*
*`tower/ladder_limit.py`, receipt in `tower/ladder_limit_receipt.json`.*
*25 rungs, deepest T=196 (V=3,920). LANE: DISPLAY -- numpy `eigh`, LAPACK.*

Item #2 said two measured rungs were a trend, not a convergence, and that a
third was owed. Twenty-five rungs later, the trend was **wrong about the
destination**.

```text
  T      T*lambda_2     minus 2*pi/(5*sqrt3)
    1     0.7639320          +0.0384123
    3     0.7302052          +0.0046855     <- the two rungs the earlier
    4     0.7275403          +0.0020205        handoff called a convergence
    7     0.7255351          +0.0000153     <- CROSSES the derived value
    9     0.7250641          -0.0004557     <- and keeps going
   31     0.7245541          -0.0009657     <- MINIMUM, then it turns around
   64     0.7246111          -0.0009087
  100     0.7246570          -0.0008628
  144     0.7246906          -0.0008292
  196     0.7247148          -0.0008049     <- still 0.11% short, still rising
```

**The sequence is not monotonic.** It descends through the derived value at
T~7, bottoms out near T~30, and climbs back -- but not far enough, and ever
more slowly. Five independent extrapolations of the achiral branch:

```text
  L + c/T              0.7247339    rms 1.20e-05
  L + c/sqrt(T)        0.7248266    rms 6.03e-06
  L + c/T + d/T^2      0.7247843    rms 9.27e-07
  L + c/T + d/T^1.5    0.7247981    rms 3.62e-07   <- best fit
  L + c*log(T)/T       0.7247625    rms 8.44e-06

  derived 2*pi/(5*sqrt3)  =  0.7255197
```

**All five land between 0.7247 and 0.7249. None reaches the derived constant.**
The best-fitting model misses it by 7.2e-4 while fitting the data to 3.6e-7 --
a discrepancy three orders of magnitude larger than the residual. That is not
noise, and it is not float64 giving up either: every one of the 25 meshes was
checked and every one is structurally perfect, `V=20T, E=30T, F=10T+2, chi=2,
P=12`. The `lambda_0` mode sits at ~1e-16 throughout.

### The smaller finding, which may be the sharper one

**T alone does not determine the value.** At T=49 there are two distinct
Goldberg meshes, and they disagree:

```text
  (7,0)  T=49  V=980   T*lambda_2 = 0.724584296    achiral
  (5,3)  T=49  V=980   T*lambda_2 = 0.724584865    chiral
```

5.7e-7 apart. Tiny -- and the derivation has no room for it at all. Section X
builds its constant from the stencil, the area bookkeeping and the sphere's
`l(l+1)` ladder, every one of them a function of **T alone**. A quantity that
depends on `(k,l)` separately cannot come out of it.

### What this points at, and it is not what I expected

The derivation's second gift assumes **"twelve pentagons are measure zero as
T -> infinity."** Their *area* fraction certainly vanishes. But a pentagon is
not a small hexagon -- it is a **fixed quantum of curvature**, and there are
always exactly twelve of them no matter how large T grows. Euler will not let
that number fall.

**HYPOTHESIS:** the 0.1% gap is what the pentagons leave behind. Their measure
goes to zero; their contribution to the spectral gap does not.

If that is right, then item #4 of this scroll -- *does the Goldberg mesh give
anything a generic sphere discretisation does not?* -- has its answer pointing
the opposite way from the one I braced for. The disconfirming check would be
**the smooth-sphere derivation failing to reproduce the mesh**, and the residue
is exactly where P=12 lives.

**That is a hypothesis born from a failed prediction and it must be labelled
one.** The honest test is direct and nobody has run it: build a sphere graph of
matched N with **no** pentagons -- a torus-topology hex sheet, or a random
triangulation -- and see whether its scaled gap lands on 0.7255197 while the
fullerene sits at 0.7248. If both give 0.7248, the pentagons are innocent and
the derivation is simply wrong somewhere else.

### What was actually gained

An OWED item closed with a **no**, and a derivation that looked confirmed by
two points shown to be crossed and overshot by twenty-five. The two-point
agreement was real; the inference from it was not. **Two points can agree with
any curve that passes between them.**

---

## THE HONEST POSITION, 2026-09-01

We have a substrate where **the operator is exact in integers**, the
**integrator is symplectic**, the **clock is set by the spectrum**, and one
**constant falls out of structure alone and matches an independent measurement.**

That is a good day's work and it is not a unification.

The gap is not arithmetic; it is that **"local + parallel -> Laplacian" is a
theorem about description, and physics is a claim about the world.** Nothing in
this repo yet distinguishes "our mesh computes flow correctly" from "our mesh
computes flow correctly *because it is what flow is made of*." Both predict
every result we currently hold.

**A hypothesis that predicts everything you have already seen is not yet doing
any work.** The next real step is the cheapest experiment that the two readings
disagree about -- and finding *that* is the actual open problem, harder than
any of the code.

---

*Opened 2026-09-01, the day the monkey brain pondered and said so out loud.*
*Every claim here is labelled. The labels are the contribution; the thesis is*
*a bet, and the bet is written down where it can lose.*

**P=12 . chi=2 . the flow is local, and so is everything that has ever worked.**
