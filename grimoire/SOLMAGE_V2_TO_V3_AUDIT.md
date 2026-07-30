# Hear, hear, Sol-mage — the last pre-V3 audit

I treated **v2.4.5 as a release candidate**, not as a picture. I extracted both embedded JavaScript programs, syntax-checked them, ran the exact-ID topology through four WELD generations, swept the geometric parameter, exercised every built-in corruption, added an adversarial corruption the test suite did not know about, swept every Fourier budget, and independently recomputed the six tower calculations.

This is a broad executable audit of the supplied kernel and mathematics. It is not a formal proof of every possible browser interaction or every floating-point input.

**Artifact SHA-256**

```text
86ba5a02a6a044127b61cf5cb3fef09ee679cd174ca4d8855a4330cbe7b3cbcb
```

## The verdict

**v2.4.5 is worthy of being frozen as the final V2 scroll.**

Its central accomplishments are real:

* WELD now produces a reproducible closed fullerene-map lineage.
* Topology is evaluated from integer vertex IDs rather than rounded coordinates.
* Geometry receives a separate verdict.
* The seven seeded faults are detected by the intended layer.
* Fourier fit and validation are separated.
* The renormalon no longer earns fake precision by exploding.
* Certificates include the indexed mesh, target samples, hashes, results, and correction history.

The source genuinely contains the exact-ID topology, geometry verifier, fault laboratory, and certificate/replay architecture it advertises.  

But there are four remaining structural truths:

> **The WELD topology is real.**
> **The geometry certificate is not yet complete.**
> **The exported certificate is not yet fail-closed.**
> **The tower math is mostly correct, but its common “budget” does not represent a common computational price.**

# 1. Full kernel receipt

Both embedded scripts pass JavaScript syntax checking.

```text
node --check kernel       PASS
node --check application  PASS
lone carriage returns     0
U+FFFD replacement chars  0
```

## Exact WELD lineage

| Generation |  Shell |   (V) |   (E) |  (F) | (P) |  (H) | MAP  | SURFACE     |
| ---------: | -----: | ----: | ----: | ---: | --: | ---: | ---- | ----------- |
|          0 |    C60 |    60 |    90 |   32 |  12 |   20 | PASS | PASS        |
|          1 |   C240 |   240 |   360 |  122 |  12 |  110 | PASS | PASS        |
|          2 |   C960 |   960 |  1440 |  482 |  12 |  470 | PASS | PASS        |
|          3 |  C3840 |  3840 |  5760 | 1922 |  12 | 1910 | PASS | PASS        |
|          4 | C15360 | 15360 | 23040 | 7682 |  12 | 7670 | PASS | **PARTIAL** |

The exact recurrence is:

[
V_{n+1}=4V_n,
\qquad
E_{n+1}=4E_n,
\qquad
F_{n+1}=F_n+E_n,
]

with

[
P_{n+1}=12,
\qquad
H_{n+1}=H_n+E_n.
]

That gives:

[
C60\rightarrow C240\rightarrow C960\rightarrow C3840\rightarrow C15360.
]

At C15360, the topology still passes, but the geometry routine skips its self-intersection sweep because the triangulation exceeds the internal ceiling. The current interface displays a form of “VERIFIED*”; the mathematically correct status is:

```text
MAP       VERIFIED
SURFACE   PARTIAL — SELF-INTERSECTION TEST SKIPPED
```

A skipped test is not a successful test.

## The legacy operators remain honest open candidates

| Operator from C60 | Formula-side candidate | Enumerated (V,E,F) | (\chi) | Boundary edges | Verdict |
| ----------------- | ---------------------: | -----------------: | -----: | -------------: | ------- |
| ALL               |            C420 / F212 |      510, 900, 212 |   −178 |            540 | OPEN    |
| 5s                |             C180 / F92 |       240, 450, 92 |   −118 |            360 | OPEN    |
| 6s                |            C300 / F152 |      390, 720, 152 |   −178 |            540 | OPEN    |

Those operators remain useful as graph mutations and search proposals. They are not closed fullerene surfaces.

This means two surviving text statements must die before V3:

```text
“A clean refineAll keeps P=12 and chi=2 exactly.”
“P=12 and chi=2 hold at every setting.”
```

They are true for the certified WELD lineage, not for every operator.

## Fault laboratory

The built-in laboratory successfully detects all seven seeded faults:

| Fault                         | MAP  | SURFACE       |
| ----------------------------- | ---- | ------------- |
| Split one shared vertex       | FAIL | not evaluated |
| Remove one face               | FAIL | not evaluated |
| Reverse one winding           | FAIL | not evaluated |
| Duplicate one face            | FAIL | not evaluated |
| Give one edge a third face    | FAIL | not evaluated |
| Collapse one edge             | PASS | FAIL          |
| Push one face through another | PASS | FAIL          |

That is excellent architecture. It demonstrates why topology and embedding must remain distinct.

### The adversarial fault it still misses

I then moved one vertex onto the exact coordinates of a different, non-adjacent vertex while preserving the integer face rings.

The result was:

```text
MAP       PASS
SURFACE   PASS
```

even though two distinct vertex IDs occupied the same point and the surface had become self-touching.

The current geometry oracle therefore still needs tests for:

* coincident but topologically distinct vertices;
* a vertex touching a nonincident triangle;
* nonincident edge–edge contact;
* coplanar overlap;
* polygon-local bow-ties;
* local triangle inversion;
* malformed or out-of-range indices;
* zero-separation features even when no proper crossing is detected.

For V3, I would give geometry four levels rather than one binary badge:

```text
MAP          combinatorial two-manifold
IMMERSION    locally regular coordinates
EMBEDDING    globally injective, no forbidden contacts
CONVEXITY    optional stronger property
```

# 2. Fourier mathematics

The DFT and reconstruction formulas are implemented correctly for the finite sampled problem:

[
c_k=\frac1M\sum_{m=0}^{M-1}f(t_m)e^{-ikt_m},
]

[
f_K(t)=\sum_{k=-K}^{K}c_ke^{ikt}.
]

The important result is not merely that the residual falls. It is that **fit error and validation error eventually separate**.

## Full (K)-sweep at (M=2048)

| Target   | Best (K) | Best validation (L_2) | Validation at (K=1023) |   Fit at (K=1023) |
| -------- | -------: | --------------------: | ---------------------: | ----------------: |
| Square   |      631 |            0.03493716 |             0.03776520 |        0.00097656 |
| Sawtooth |      632 |            0.04280582 |             0.04626047 |        0.00084573 |
| Triangle |      851 | (2.4189\times10^{-5}) |  (2.5616\times10^{-5}) | (\approx10^{-15}) |
| Pulse    |      631 |            0.03495079 |             0.03777782 | (\approx10^{-14}) |

For the square wave:

|  Budget | Meaning                  | Validation residual |
| ------: | ------------------------ | ------------------: |
|      16 | C60 capacity             |            0.159099 |
|      61 | C240 capacity            |            0.081176 |
|     241 | C960 capacity            |            0.043437 |
| **631** | **best measured budget** |        **0.034937** |
|     961 | C3840 capacity           |            0.037027 |
|    1023 | Nyquist-adjacent cap     |            0.037765 |

So the current statement “each growth drops the residual” is only true if “residual” means the fitting-grid residual. C3840 and C15360 improve the fit while worsening independently measured validation.

That is not a flaw in the experiment. **That is perhaps the most important result in AEQUALIUM.**

## The optimum is not a fixed physical constant

For the square wave, I found:

| Sample count (M) | Best (K) |
| ---------------: | -------: |
|              512 |      157 |
|             1024 |      315 |
|             2048 |      631 |
|             4096 |     1263 |

Approximately,

[
K_{\mathrm{opt}}\approx0.308M.
]

The optimum moves when the sample grid moves.

That tells us exactly what this observed ceiling currently is:

> **A finite-sampling, interpolation, aliasing, and validation phenomenon.**

It is not presently evidence for a Planck-scale lattice or a universal computational grain.

For a fixed continuous function with exact Fourier coefficients, the orthogonal-projection (L_2) error does not become worse merely because another valid mode is included. The interior optimum appears here because the coefficients are estimated from a finite sampling grid and then tested between those samples.

This actually strengthens THEALIMITIUM. V3 can show the difference between:

```text
exact continuous coefficients
sampled coefficients
noisy experimental coefficients
regularized coefficients
finite-precision coefficients
```

The monkey brain sees “more terms.”
The laboratory sees **which information those terms were trained on**.

# 3. The Standard Modelium tower

The tower’s central design—showing the exact symbolic relation beside the finite procedure—is strong. The file explicitly distinguishes an ideal equation from the stepped form executed at the current shell. 

Here is the full mathematical verdict.

| Rung                     | Verdict                                   | Required clarification                                                     |
| ------------------------ | ----------------------------------------- | -------------------------------------------------------------------------- |
| QCD running              | Correct for the coded model               | One-loop, fixed (n_f=5); not full precision QCD                            |
| Toy renormalon           | Correct asymptotic lesson                 | Displayed coefficient normalization needs correction; use ambiguity metric |
| (\Lambda_{\mathrm{QCD}}) | Newton and closed inversion agree         | One-loop (n_f=5) scheme parameter, not a universal measured value          |
| Kepler                   | Formula and Miller Bessel kernel are good | Hidden 120-term implementation ceiling                                     |
| Comoving distance        | Simpson calculation is correct            | Numerical reference, not exact; live sequence duplicates panel counts      |
| Blackbody                | Identity and series are correct           | Dimensionless integral, not a temperature calculation                      |

## QCD I — running coupling

The implemented model is the one-loop fixed-flavor expression

[
\alpha_s(Q)
===========

\frac{\alpha_s(M_Z)}
{1+\alpha_s(M_Z)\frac{\beta_0}{4\pi}
\ln(Q^2/M_Z^2)}.
]

The finite geometric expansion converges correctly at the selected parameters.

At (Q=10\ \mathrm{GeV}),

[
\alpha_s(Q)\approx0.17308363622084.
]

The scientific label should be:

```text
ONE-LOOP FIXED-nf QCD DEMONSTRATION
```

not simply “QCD running,” because physical precision work also requires threshold matching, higher-loop coefficients, a renormalization scheme, and input uncertainty.

## QCD II — toy renormalon

The repaired behavior is sound:

[
N^\star=13,
]

[
S_{N^\star}\approx1.08571284,
]

with an estimated ambiguity of roughly (8.69\times10^{-6}) in the coded toy.

The normalization displayed in the stepped equation should, however, match the code. The code effectively uses

[
t_n=n!\left(\frac{\beta_0\alpha_s}{4\pi}\right)^n.
]

Equivalently, using (a=\alpha_s/\pi),

[
c_n=n!\left(\frac{\beta_0}{4}\right)^n.
]

The current generic label “digits of agreement” is still inappropriate for this rung. It has no trusted exact target. Its native result is:

```text
OPTIMAL TRUNCATION
ESTIMATED AMBIGUITY
RAW PARTIAL SUM
```

Also change:

> “More compute cannot help.”

to:

> **“More naïve terms in this asymptotic truncation cannot help; resummation or additional physical input constitutes a different operation.”**

## QCD III — (\Lambda_{\mathrm{QCD}})

The Newton method agrees with the coded one-loop closed inversion:

[
\Lambda
=======

M_Z\exp\left[
-\frac{2\pi}{\beta_0\alpha_s(M_Z)}
\right].
]

The result is approximately

[
87.8270801\ \mathrm{MeV}.
]

That value should be described as:

> **the one-loop, fixed-(n_f=5), convention-dependent (\Lambda) parameter produced by this model.**

It is not “the universal measured value of (\Lambda_{\mathrm{QCD}}).”

## Kepler equation

The corrected Fourier–Bessel representation is good:

[
E=M+
\sum_{n=1}^{\infty}
\frac{2}{n}J_n(ne)\sin(nM),
\qquad e<1.
]

I independently compared the Miller-recurrence Bessel implementation against high-precision values through (n=120); the sampled agreement was approximately machine precision.

But the application silently limits the series to:

```javascript
Math.min(N, 120)
```

At (e=0.95):

|                       Terms |               Agreement |
| --------------------------: | ----------------------: |
|                          16 |       about 2.20 digits |
|                          61 |       about 3.79 digits |
|                         120 |       about 4.15 digits |
| 241, current implementation | still about 4.15 digits |
|  241, true continued series |       about 4.86 digits |
|  400, true continued series |       about 7.07 digits |

Thus the correct dual status is:

```text
MATHEMATICS      CONVERGENT FOR e < 1
IMPLEMENTATION   CAPPED AT 120 BESSEL TERMS
```

The interface must not announce float64 convergence at high eccentricity merely because the shell budget became large.

## Comoving distance

The Simpson calculation is internally correct for the coded flat-(\Lambda)CDM parameters.

The 20,000-panel internal reference is:

[
D_C\approx3401.262917346913\ \mathrm{Mpc}.
]

An independent high-precision quadrature gave approximately:

[
3401.262917346901\ \mathrm{Mpc}.
]

So the reference is excellent for the present budgets—roughly 14.45 relative digits—but it remains a numerical reference.

The live trace also repeats every panel count:

```text
2 panels, 2 panels, 4 panels, 4 panels, 6 panels, 6 panels...
```

Half the displayed “terms” therefore contribute zero change. V3 should use either

[
N_{\mathrm{panels}}=2(n+1),
]

or a genuinely nested quadrature sequence such as Romberg integration.

## Blackbody integral

The calculation is correct:

[
\int_0^\infty\frac{x^3}{e^x-1},dx
=================================

# \frac{\pi^4}{15}

6\sum_{k=1}^{\infty}\frac1{k^4}.
]

The truncation tail scales as approximately

[
\frac{2}{N^3}.
]

One language correction: this computes the **dimensionless Planck integral**. It does not calculate the temperature of a quasar. Temperature enters only after observational data and an appropriate spectral model are supplied.

# 4. The certificate is close—but not sovereign yet

The exported object is a strong evidence bundle. It is not yet a strict certificate.

## Source hash weakness

The current kernel hash is constructed from the string representations of public `GK` members. Private helper functions and other relevant source bytes are excluded.

I changed a private seed normalization constant so that the generated geometry changed. The reported kernel hash remained exactly the same.

V3 must hash:

```text
full kernel module bytes
full application module bytes
full HTML artifact bytes
schema bytes
external dependency identities
```

not a projection of public functions.

## Replay is fail-open

The replay code reports hash or numerical mismatches to the log but then installs the imported mesh and announces:

```text
certified state INSTALLED
```

It also compares only part of the topology object and does not replay the tower traces. 

The V3 law must be:

```javascript
if (anyRequiredCheckFails) {
    throw new CertificateError(...);
}
// only here may state be installed
```

The imported state should be installed only after all of these agree:

* artifact hash;
* kernel hash;
* mesh hash;
* complete topology record;
* complete geometry record;
* target identity;
* fitting samples;
* validation samples;
* Fourier metrics;
* every tower trace;
* parameters;
* operator path;
* state lineage;
* declared numerical tolerances.

## Fourier replay cannot currently reproduce discontinuous targets

The certificate stores fitting samples. Replay constructs the validation target by linearly interpolating them.

For the square wave at (K=16):

```text
original validation  0.1590988160
replay validation    0.1568071556
difference          -0.0022916604
```

That is thousands of times larger than the declared replay tolerance.

Sawtooth and pulse exhibit the same problem. Triangle works because it is piecewise linear.

V3 should export both:

```text
fit samples
independent validation samples
```

and also a versioned target definition:

```json
{
  "evaluator": "square/v1",
  "parameters": {},
  "fitSamplesSha256": "...",
  "validationSamplesSha256": "..."
}
```

Then replay can both regenerate the target and compare the exact samples used in the original verdict.

# 5. State and interface corrections before freezing V2

These are small compared with V3, but I would patch them into the frozen handoff or record them explicitly as known limitations.

## Exact C60 certification is not run at boot

The exact indexed seed exists and passes, but startup leaves:

```text
C60 ✓ (coord-audit only)
MAP —
SURFACE —
```

until certification is triggered later. The initial HUD confirms that state. 

Call `refreshCerts()` before the first render.

## BACK loses history

After three WELDs, the first BACK returns from C3840 to C960. The next BACK is refused because converting the indexed mesh back to render state resets the render-state history.

Use one immutable history:

```javascript
{
  eventId,
  parentId,
  operator,
  parameters,
  indexedMesh,
  meshHash,
  target,
  targetHash,
  traces,
  certificates
}
```

BACK and FORWARD should move between events rather than attempting to reconcile separate histories.

## Stale language remains

The visible source still includes:

* “pretty+symmetric = true” in the duplicated boot log;
* “topology re-formed” in slider logs;
* `refineAll` preserving (\chi=2);
* CASCADIUM described as “the proof” and a “demonstrated fact”;
* an old v2.4 log line;
* an HTML title that does not consistently reflect v2.4.5.

The runtime `openProof()` correctly calls CASCADIUM an external claim, while other panels still call it proof.   

One centralized epistemic text model should generate every label. No handwritten duplicate status text.

# 6. The thesis of the equals sign

Here is where I agree with the heart of what you are saying, while drawing the laboratory boundary precisely.

The Standard Model is not nonsense in the empirical sense. It is extraordinarily successful.

What can look nonsensical is how much machinery physicists compress into one innocent glyph:

# [

]

A paper may write

[
A=B
]

while the actual computation means something closer to:

[
A_{\text{reported}}
===================

\mathcal N_{\text{finite precision}}
!\left[
\mathcal A_{\text{algorithm}}
!\left(
B;
\mu,
\text{scheme},
\text{order},
\text{cutoff},
\text{inputs},
\text{covariance}
\right)
\right]
+
\text{unresolved error}.
]

The equals sign itself is not technically a lie. It expresses an exact relation **inside a declared mathematical model**.

The computed decimal is a finite witness to that relation.

The experimental comparison is another object again.

I would make this the V3 constitution:

> **In mathematics, equality is a relation.
> In computation, equality requires a finite witness.
> In experiment, equality becomes a compatibility claim with uncertainty.**

Or, in one line:

> **The equation may be exact. The naked numeral is incomplete.**

That is stronger than saying “all equals signs are lies.”

## The Planck-lattice hypothesis

The present AEQUALIUM results do **not** demonstrate that physical reality runs on a stepped lattice, that the C60 is a literal spacetime generator, or that the Fourier optimum has reached beneath the Planck scale.

The observed optimum moves with the sample count. That is direct evidence that the present ceiling belongs to the numerical representation.

But your larger idea can be translated into a serious experiment:

> **Can a small set of local graph operations, executed under a defined unit-cost rule, generate continuum-like observables while preserving symmetry, locality, stability, and an auditable information ledger?**

That is testable.

An x86 instruction is not a fundamental unit of computation. A semiconductor process-node label is not a fundamental lattice spacing. They are layers of engineering abstraction.

So define **one compute** independently of the host:

```text
one local node-state transition
one edge-message update
one reversible gate
one fixed-point stencil evaluation
one graph-rewrite application
```

Then x86, WebAssembly, GPU, or an NPU is merely the machine hosting the experiment.

A physical lattice-substrate hypothesis must eventually demonstrate:

* an isotropic continuum limit;
* no unacceptable preferred frame;
* recovered conservation laws;
* stable causal propagation;
* scaling behavior independent of the implementation host;
* at least one discriminating observable not inserted by construction.

That would be **LATTICIUM — ONE COMPUTE**, and its status would begin as:

```text
HYPOTHESIS / FORWARD MODEL
```

not proof of the physical substrate.

# 7. AEQUALIUM V3 — **THE EQUALITY ENGINE**

Codename: **THE GENESIS TWIST**

V3 should not be a larger V2 page. It should be an engine with a common protocol into which every scroll plugs.

## Organ I — the equality grammar

Every result must declare which relation it is claiming:

| Symbol            | Meaning in V3                              |
| ----------------- | ------------------------------------------ |
| (\equiv)          | definition or exact identity               |
| (=)               | exact relation inside the stated model     |
| (\approx)         | numerical approximation                    |
| (=_{\varepsilon}) | agrees within declared tolerance           |
| (\sim)            | asymptotic or statistical relation         |
| (\mapsto)         | algorithm or representation transformation |
| (\not\approx)     | failed comparison                          |

Every equality card should expand into:

```javascript
{
  claim,
  relationKind,
  model,
  assumptions,
  inputs,
  inputUncertainty,
  representation,
  algorithm,
  budget,
  estimate,
  reference,
  metric,
  numericalError,
  modelError,
  cost,
  terminalReason,
  status,
  receiptHash
}
```

That is Standard Modelium translated from compressed mage language into inspectable laboratory language.

## Organ II — one trace grammar for every formula

Every formula, PDE, lattice, and graph process should emit the same basic trace:

```javascript
{
  id: "kepler-bessel",
  step: 73,
  estimate: 1.309105,
  increment: -2.4e-7,

  reference: {
    kind: "high-precision-solver",
    value: 1.309106
  },

  metric: {
    kind: "relative-error",
    value: 7.1e-7
  },

  uncertainty: {
    input: 0,
    truncation: 7.1e-7,
    roundoff: 2.2e-16,
    model: null
  },

  cost: {
    additions: 12345,
    multiplications: 17890,
    transcendentals: 219,
    functionEvaluations: 73,
    bytesPeak: 8192,
    elapsedMs: 3.7
  },

  status: {
    mathematics: "convergent",
    implementation: "running",
    empirical: "not-applicable"
  }
}
```

V3 should draw four curves for every calculation:

1. estimate versus paid cost;
2. native error or ambiguity versus paid cost;
3. term magnitude versus step;
4. marginal gain per unit cost,

[
\eta_n
======

\frac{\Delta\text{score}_n}
{\Delta\text{cost}_n}.
]

The common horizontal axis should be **paid computation**, not raw (N).

A Kepler Bessel term, a Simpson panel, a Newton iteration, and a Fourier harmonic do not have the same price.

## Organ III — THEALIMITIUM error anatomy

Every final mismatch should be decomposed as far as the model allows:

[
\text{total mismatch}
=====================

\text{input uncertainty}
+
\text{model discrepancy}
+
\text{discretization}
+
\text{truncation}
+
\text{aliasing}
+
\text{roundoff}
+
\text{solver tolerance}.
]

Not all terms add linearly; the interface may show a structured budget rather than pretending they do. The essential point is that “error” should stop being one pink number.

For the Fourier laboratory, add four coefficient modes:

```text
ANALYTIC COEFFICIENTS
SAMPLED DFT
SAMPLED + NOISE
REGULARIZED / WINDOWED
```

The analytic mode is the control. It should show monotonically improving continuous (L_2) approximation.

The sampled mode should rediscover the interior optimum and show why it moves with (M).

That single comparison can explain more about high-precision computation than a page of prose.

## Organ IV — the algorithm tournament

The same mathematical target should be solved by multiple algorithms.

### Kepler

```text
Fourier–Bessel series
Newton iteration
robust high-e starter + Newton
```

### Comoving distance

```text
composite Simpson
Romberg
adaptive Gauss–Kronrod
```

### Blackbody integral

```text
zeta partial sum
Euler–Maclaurin accelerated sum
direct quadrature
closed identity
```

### QCD running

```text
finite geometric expansion
closed one-loop expression
higher-loop numerical RG, once separately audited
```

The winner should not be “the answer with the most terms.” It should be the Pareto frontier:

[
\text{minimum validated error}
\quad\text{for a given}\quad
\text{cost and memory}.
]

## Organ V — adaptive fractalization

The WELD capacities currently jump:

[
16\rightarrow61\rightarrow241\rightarrow961\rightarrow1023.
]

The square-wave optimum near (631) lies between shells.

Therefore distinguish:

[
K_{\text{capacity}}
]

from

[
K_{\text{active}}\le K_{\text{capacity}}.
]

The shell provides capacity. The optimizer decides how much of that capacity to activate.

The objective could be:

[
J(\theta)
=========

\mathcal E_{\mathrm{validation}}(\theta)
+
\lambda_C C(\theta)
+
\lambda_M M(\theta)
+
\lambda_I I(\theta),
]

where (I) imposes an infinite or very large penalty for violated invariants.

The search state should contain:

```javascript
{
  seed,
  shell,
  operatorPath,
  inner,
  mid,
  activeModes,
  sampleCount,
  algorithm,
  solverParameters
}
```

Every candidate—including rejected ones—must be exported.

Open ALL/5s/6s mutations may participate as graph experiments. They may not earn fullerene or surface status unless a later repair operation closes and certifies them.

## Organ VI — the five scroll adapters

The precise implementations should wait for the actual scroll sources, but every scroll can implement one interface:

```javascript
{
  id,
  version,
  initialize(config),
  step(state, budget),
  observableCurve(state),
  invariants(state),
  nativeMetric(state),
  cost(state),
  terminal(state),
  exportTrace(state)
}
```

### MAXWELIUM

Observable curves:

```text
field amplitude
energy density
dispersion relation
constraint residuals
```

Required invariants:

[
\nabla\cdot B=0,
\qquad
\nabla\cdot E-\rho/\varepsilon_0=0,
]

plus energy accounting and numerical stability conditions.

### CRISTALIUM

Observable curves:

```text
phonon dispersion
structure factor
reciprocal-space peaks
defect relaxation
```

Receipts must distinguish the finite lattice, boundary conditions, cell spacing, reciprocal resolution, and continuum extrapolation.

### ISINGIUM

Observable curves:

```text
energy
magnetization
susceptibility
specific heat
Binder cumulant
autocorrelation time
```

Its great THEALIMITIUM lesson is critical slowing down and finite-size scaling: more samples do not automatically mean independent information.

### NOETHERIUM

Vary a symmetry parameter and measure:

```text
action variation
current divergence
charge drift
discretization violation
```

It should demonstrate the difference between:

```text
exact discrete symmetry
approximately preserved continuum symmetry
numerically drifting conservation law
```

### THEALIMITIUM

This becomes the oracle of ceilings:

```text
condition number
truncation floor
aliasing
roundoff
catastrophic cancellation
finite-size scaling
sampling uncertainty
model discrepancy
```

It should be able to explain *why* a run ended, not merely that it ended.

## Organ VII — actual Standard Modelium

At present, the tower is a **physics-computation tower**, not strictly a Standard Model tower: half of its rungs are Kepler, cosmology, and blackbody mathematics.

There are two honest choices:

```text
rename it PHYSICSIUM
```

or add genuinely Standard Model computations, each with conventions and references attached:

```text
QED running coupling
electroweak mixing relations
Higgs-potential minimum and mass relation
neutrino oscillation probability
CKM or PMNS unitarity checks
decay widths with input covariance
cross sections with perturbative scale bands
renormalization-group flow
```

The point should not be “the Standard Model is nonsense.”

The point should be:

> **The familiar compact formula is the top layer of an enormous dependency graph.**

V3 should let the user click the equals sign and watch it decompress into:

```text
model
gauge choice
renormalization scheme
scale
perturbative order
effective cutoff
measured inputs
covariance
algorithm
precision
detector or observational model
comparison statistic
```

That would be devastatingly effective—and completely fair to the physics.

## Organ VIII — certificate/3

The final popup should export one canonical run bundle containing:

```text
full source hashes
environment
seed
immutable event history
operator path
indexed meshes
targets
fit and validation samples
all traces
all native metrics
all cost ledgers
all terminal reasons
all tests
all corrections
```

Replay must be strict and transactional:

```text
LOAD
VERIFY EVERYTHING
REJECT OR COMMIT
```

Never:

```text
log FAIL
install anyway
```

A DOM-free Node or Python verifier should independently consume the same bundle without calling the browser implementation’s verification functions.

## Organ IX — the terminal receipt popup

Every run should terminate with one explicit reason:

```text
CONVERGED
VALIDATION OPTIMUM
ASYMPTOTIC OPTIMUM
NYQUIST CEILING
IMPLEMENTATION CAP
INPUT-UNCERTAINTY FLOOR
MODEL-DISCREPANCY FLOOR
COMPUTE BUDGET
MEMORY BUDGET
TOPOLOGY FAILURE
GEOMETRY FAILURE
NUMERICAL FAILURE
USER STOP
```

The popup should show:

```text
FORMULA
RELATION TYPE
BEST ESTIMATE
BEST BUDGET
BEST VALIDATION
ERROR DECOMPOSITION
PAID COST
OPERATOR PATH
MAP STATUS
SURFACE STATUS
TERMINAL REASON
RECEIPT HASH
```

That is the equals sign earning its robes.

# 8. V3 red-test oath

I would call **THE EQUALITY ENGINE** real only when these tests pass:

1. C60 is exactly certified at boot.
2. Arbitrary BACK and FORWARD operations reproduce prior hashes.
3. A non-adjacent coincident vertex is rejected by the embedding oracle.
4. C15360 is labeled PARTIAL whenever self-intersection testing is skipped.
5. Square, sawtooth, pulse, triangle, and silhouette certificates replay themselves exactly within declared tolerances.
6. Any source, mesh, target, trace, or result tampering rejects the certificate and installs nothing.
7. Changing a private kernel helper changes the kernel hash.
8. The Kepler mathematical status and 120-term implementation status are separately visible.
9. The toy renormalon never displays “digits of agreement.”
10. No panel calls an external artifact “proof” unless that artifact and its receipt are loaded and reproduced.
11. The optimizer uses measured cost rather than pretending every (N) has equal price.
12. At (M=2048), the square-wave optimizer rediscovers (K\approx631).
13. When (M) changes, the optimizer’s chosen (K) moves accordingly.
14. Analytic Fourier coefficients do not display the sampled-grid overfitting phenomenon.
15. Every completed run exports its full trace and terminal reason.

# Final Sol-mage judgment

Your deepest workable insight is not yet:

> “We have shown that reality is a Planck lattice.”

The artifact does not show that.

It is this:

> **Every scientific equality hides a chain of representation choices, finite operations, assumptions, costs, errors, and adjudications. A truthful computational artifact should make that hidden chain visible.**

That is already a serious thesis.

V2 taught AEQUALIUM to separate target from result, formula from topology, map from surface, fit from validation, and optimal truncation from raw divergence.

V3 should make the equals sign clickable—and force it to disclose everything it swallowed.

**Do not claim the substrate yet. Build the machine before which every substrate claim must pay.**

## The frozen scrolls and receipts

[Open AEQUALIUM v2.4.5](sandbox:/mnt/data/shell__aequalium_v2.4.5.html)

[Read the Sol-mage full math audit](sandbox:/mnt/data/AEQUALIUM_v2.4.5_SOL_MATH_AUDIT.md)

[Download the raw numerical audit receipt](sandbox:/mnt/data/aequalium_v2.4.5_sol_math_audit.json)
