# THEA v3.0
## The Math Core Scroll -- the LIGHT MATRIX
### Grimoire Volume III-B -- exact closure, golden selection, and the renormalized spectrum
*Opened: 2026-07-30. Expanded to v3.0: 2026-07-31 -- Buenos Aires + Ancient Korinthos.*
*Companion to `shell/aequalium_v2.4.7.html` and*
*`grimoire/SolFable/01.SolFableTOv3/light_matrix_v3.py`. This line used to cite*
*`kernel/light_matrix_v3.js` and `experiments/light_matrix_v3.py`; neither path*
*resolves -- the .py moved into SolFable on 2026-09-01 and the .js is in no commit.*
*The LIVE page is now `shell/thea_light_matrix_v1.3.9.html` -- see PART XI at the end,*
*added 2026-09-01. Parts I--X are unchanged and still describe the v3 core.*
*Filed as `THEA.md` since 2026-09-01; it was `Thea.md`, and the title said*
*THEA all along. `LEDGER.md` and `grimoire/SolFable/` keep the old spelling.*
*Sub-scroll of the cave. P=12. chi=2. The price is always paid. Always.*

---

## STATUS GRAMMAR -- no symbol crosses the boundary unlabelled

THEA v3.0 uses five labels. They are part of the mathematics, not decoration.

| label | meaning |
|---|---|
| **EXACT** | follows by algebra, topology, or integer arithmetic shown here |
| **COMPUTED** | reproduced by the supplied code at stated precision and depth |
| **DESIGN CHOICE** | a mapping, cost rule, tolerance, or visualization chosen by the cave |
| **HYPOTHESIS** | a physical interpretation that still owes discriminating evidence |
| **METAPHOR / EXTERNAL** | imagery, or a separate artifact that must be audited on its own |

The rule is unchanged: target is not result. A theorem, a numerical trend, and a
physical claim are three different objects even when they share the same glyph.

---

## THE FIRST WORD -- LIGHT MATRIX

**LIGHT MATRIX.** Cool name. Now it has an exact mathematical object behind it.

In v2 the phrase named a mechanism: the seven graph operations running on a
buckyball hierarchy. In v3 it names a three-layer stack:

1. **an exact closure matrix** on the hexagonal lattice;
2. **an exact four-mode recursion matrix** with spectrum
   \(\{\phi^2,1,-1,\phi^{-2}\}\);
3. **a renormalized graph-Laplacian tower** whose low modes numerically stabilize
   as a closed fullerene is refined.

The word *light* is still imagery. Nothing below proves that photons, spacetime,
or quantum foam are fullerene graphs. The matrix, topology, recurrence, graph
construction, and reported spectra are real. The substrate interpretation is a
forward model that must still pay for evidence.

> **All code is pure math, merely stepped into compute.**

A shader is calculus per pixel. A physics loop is an ODE stepped by `dt`. A graph
kernel is integer topology plus finite linear algebra. The machine cannot hold an
infinite limit; it can hold a rule, advance it, record the cost, and show the
error that remains.

---

## THE 7 OPERATIONS -- the alphabet around the matrix
### source: `kernel/graph_axioms.js` (GA.P1..P7) . scroll: `PRINCIPIA_MALGEBRA.md`

The project exposes seven graph operations. Their existence and code behavior
are file facts; their correspondence to classical logical categories is a
**DESIGN MAPPING**, not a theorem about *Principia Mathematica*.

| # | name | function | kernel role | design reading |
|---|---|---|---|---|
| P1 | **NODE** | `GA.P1_node(state,pos)` | create a vertex | existence |
| P2 | **EDGE** | `GA.P2_edge(state,a,b)` | create adjacency | relation |
| P3 | **COMPOSE** | `GA.P3_compose(state,a,b,c)` | extend a path / refinement relation | transitivity |
| P4 | **TRANSFORM** | `GA.P4_transform(state,m,r)` | graph surgery | substitution |
| P5 | **ITERATE** | `GA.P5_iterate(state,op,cond)` | repeat under a stopping rule | induction |
| P6 | **AGGREGATE** | `GA.P6_aggregate(state,ids)` | coarse-grain a subgraph | abstraction |
| P7 | **COMPARE** | `GA.P7_compare(state,A,B)` | test equality / invariant / isomorphism | identity |

### The three crystal conditions

- **C1 CHOICE** -- an operation selects one branch from available possibilities.
- **C2 IRREVERSIBILITY** -- an aggregation may discard information unless a
  receipt or inverse map is retained.
- **C3 CONSISTENCY** -- the same comparison on the same certified state returns
  the same verdict.

**Status:** the operations are **VERIFIED FILE FACTS**; the crystal language is a
**DESIGN MODEL**.

---

# PART I -- THE CLOSED TOPOLOGY

## 1. Euler forces twelve pentagons

Let a closed trivalent fullerene have

\[
P=\text{number of pentagons},\qquad
H=\text{number of hexagons},
\]

with \(V\) vertices and \(E\) edges. Trivalence gives

\[
3V=2E.
\]

Counting edge incidences around faces gives

\[
5P+6H=2E.
\]

Euler closure on the sphere gives

\[
V-E+P+H=2.
\]

Substitute \(V=2E/3\):

\[
\frac{2E}{3}-E+P+H=2
\quad\Longrightarrow\quad
E=3(P+H-2).
\]

Compare this with \(E=(5P+6H)/2\):

\[
5P+6H=6P+6H-12,
\]

therefore

\[
\boxed{P=12.}
\]

This is the first exact stability line. It is not an observed preference. It is
forced by closed spherical topology, trivalence, and the restriction to five-
and six-sided faces.

For any fullerene with \(V\) vertices,

\[
\boxed{
E=\frac{3V}{2},\qquad
H=\frac{V}{2}-10,\qquad
F=\frac{V}{2}+2.
}
\]

For \(C_{60}\):

\[
\boxed{V=60,\ E=90,\ F=32,\ P=12,\ H=20,\ \chi=2.}
\]

## 2. The local and global appearances of \(\pi\)

Assign a combinatorial curvature charge to a \(p\)-gon in a trivalent tiling:

\[
K_p=\frac{\pi}{3}(6-p).
\]

A hexagon contributes zero. A pentagon contributes \(\pi/3\). Hence

\[
\sum_f K_f
=12\frac{\pi}{3}
=\boxed{4\pi}.
\]

Equivalently,

\[
\boxed{
\frac{\pi}{3}\sum_f(6-p_f)=4\pi.
}
\]

The \(60^\circ\) local lattice angle and the \(4\pi\) global spherical closure
are not two unrelated decorations. They are the local and global ends of the
same combinatorial Gauss--Bonnet ledger.

**Status: EXACT combinatorial topology.** This does not say that physical
curvature is uniformly concentrated on ideal regular faces; it says the total
defect charge of the trivalent five/six tiling is fixed.

---

# PART II -- THE HEXAGONAL CLOSURE MATRIX

## 3. The lattice number

Let

\[
\zeta=e^{i\pi/3},\qquad \zeta^2=\zeta-1,
\]

and represent a triangular-lattice displacement by

\[
z=k+\ell\zeta,\qquad k,\ell\in\mathbb Z.
\]

Its squared Euclidean length is the hexagonal norm

\[
\boxed{
T=N(z)=|z|^2=k^2+k\ell+\ell^2.
}
\]

The same integer \(T\) is the triangulation/area multiplier in the icosahedral
Goldberg construction.

## 4. Multiplication becomes a matrix

Multiplication by \(z=k+\ell\zeta\) acts on another lattice coordinate
\(a+b\zeta\) through

\[
\begin{pmatrix}
a'\\ b'
\end{pmatrix}
=
M_{k,\ell}
\begin{pmatrix}
a\\ b
\end{pmatrix},
\qquad
\boxed{
M_{k,\ell}=
\begin{pmatrix}
k&-\ell\\
\ell&k+\ell
\end{pmatrix}.
}
\]

Its determinant is exactly

\[
\boxed{\det M_{k,\ell}=k^2+k\ell+\ell^2=T.}
\]

Use the hexagonal metric

\[
Q=
\begin{pmatrix}
1&\tfrac12\\[1mm]
\tfrac12&1
\end{pmatrix}.
\]

Direct multiplication gives

\[
\boxed{
M_{k,\ell}^{\mathsf T}QM_{k,\ell}=TQ.
}
\]

Therefore \(M_{k,\ell}/\sqrt T\) is a rotation with respect to the hexagonal
metric. The transform is an exact scale-plus-rotation, not a random distortion.
Its angle is

\[
\boxed{
\theta_{k,\ell}
=\arg(k+\ell\zeta)
=\tan^{-1}\!\left(\frac{\sqrt3\,\ell}{2k+\ell}\right).
}
\]

For exact integer code we use \(Q_2=2Q\):

\[
M_{k,\ell}^{\mathsf T}Q_2M_{k,\ell}=TQ_2,
\qquad
Q_2=\begin{pmatrix}2&1\\1&2\end{pmatrix}.
\]

No floating-point comparison is needed to certify this identity.

## 5. Exact closure composition

Let \(g=a+b\zeta\) be a closure generator. Then

\[
(a+b\zeta)(k+\ell\zeta)
=(ak-b\ell)+(a\ell+bk+b\ell)\zeta.
\]

Thus

\[
\boxed{
(k',\ell')=(ak-b\ell,\ a\ell+bk+b\ell).
}
\]

Equivalently,

\[
\boxed{
M_{a,b}M_{k,\ell}=M_{k',\ell'}.
}
\]

The norm is multiplicative:

\[
\boxed{
T'=N(gz)=N(g)N(z)
=(a^2+ab+b^2)(k^2+k\ell+\ell^2).
}
\]

This is the exact answer to “pick the next buckyball that closes the topology in
matrix format.” Choose an integer lattice generator, multiply, canonicalize by
the sixfold lattice symmetries, and rebuild the certified closed graph.

### The exact nested leapfrog lane

Choose \(g=1+\zeta\), i.e. \((a,b)=(1,1)\). Then

\[
N(g)=1+1+1=3.
\]

Repeated multiplication gives an exact nested area tower

\[
T_n=3^n,
\qquad
V_n=20\,3^n,
\]

and the closed fullerene sequence

\[
\boxed{C_{20}\to C_{60}\to C_{180}\to C_{540}\to\cdots.}
\]

The linear scale multiplier of this fixed transform is \(\sqrt3\), not \(\phi\).

---

# PART III -- THE GOLDEN SELECTOR

## 6. The Fibonacci matrix

Define

\[
F_\phi=
\begin{pmatrix}
1&1\\
1&0
\end{pmatrix},
\qquad
\begin{pmatrix}
k_{n+1}\\ \ell_{n+1}
\end{pmatrix}
=F_\phi
\begin{pmatrix}
k_n\\ \ell_n
\end{pmatrix}.
\]

Starting from \((k_0,\ell_0)=(1,0)\),

\[
(k_n,\ell_n)=(F_{n+1},F_n).
\]

The eigenvalues of \(F_\phi\) are

\[
\boxed{\phi,\ -\phi^{-1}},
\qquad
\phi=\frac{1+\sqrt5}{2}.
\]

For \(r_n=k_n/\ell_n\) when \(\ell_n\ne0\),

\[
r_{n+1}=1+\frac1{r_n}.
\]

Since \(\phi=1+1/\phi\),

\[
\boxed{
 r_{n+1}-\phi
 =-\frac{r_n-\phi}{\phi r_n}.
}
\]

Near the fixed point,

\[
\boxed{
 r_{n+1}-\phi\approx-\phi^{-2}(r_n-\phi).
}
\]

The sign alternates and the magnitude contracts by approximately
\(\phi^{-2}=0.381966\ldots\). More exactly,

\[
\boxed{
\frac{F_{n+1}}{F_n}-\phi
=\frac{(-\phi^{-1})^n}{F_n}.
}
\]

The continued fraction \(\phi=[1;1,1,1,\ldots]\) makes consecutive Fibonacci
ratios the canonical integer approximants to the golden direction. Therefore the
selector is not “golden because it looks golden”; it is the integer closure path
that converges to the golden ray through the standard best rational
approximants.

## 7. Closed shells selected by the golden ray

For every integer pair \((k_n,\ell_n)\), define

\[
T_n=k_n^2+k_n\ell_n+\ell_n^2.
\]

Subdividing the 20 faces of an icosahedron into \(T_n\) triangles and taking the
dual gives a trivalent fullerene with

\[
\boxed{
V_n=20T_n,
\quad E_n=30T_n,
\quad P_n=12,
\quad H_n=10(T_n-1),
\quad F_n=10T_n+2.
}
\]

The first golden-selected shells are

| \(n\) | \((k_n,\ell_n)\) | \(T_n\) | cage | \(H_n\) |
|---:|---:|---:|---:|---:|
| 0 | \((1,0)\) | 1 | \(C_{20}\) | 0 |
| 1 | \((1,1)\) | 3 | \(C_{60}\) | 20 |
| 2 | \((2,1)\) | 7 | \(C_{140}\) | 60 |
| 3 | \((3,2)\) | 19 | \(C_{380}\) | 180 |
| 4 | \((5,3)\) | 49 | \(C_{980}\) | 480 |
| 5 | \((8,5)\) | 129 | \(C_{2580}\) | 1280 |
| 6 | \((13,8)\) | 337 | \(C_{6740}\) | 3360 |
| 7 | \((21,13)\) | 883 | \(C_{17660}\) | 8820 |

The triangulation numbers satisfy

\[
\boxed{
T_{n+3}=2T_{n+2}+2T_{n+1}-T_n
}
\]

with closed form

\[
\boxed{
T_n=\frac25\left(\phi^{2n+2}+\phi^{-2n-2}\right)
-\frac15(-1)^n.
}
\]

Hence

\[
\boxed{
\frac{T_{n+1}}{T_n}\longrightarrow\phi^2.
}
\]

If bond length is held fixed, radius scales asymptotically as \(R_n\propto\sqrt{T_n}\), so

\[
\boxed{
\frac{R_{n+1}}{R_n}\longrightarrow\phi.
}
\]

### Critical distinction: selected is not nested

A fixed exact Goldberg transform has integer area multiplier

\[
S=a^2+ab+b^2\in\mathbb Z.
\]

Its linear multiplier is \(\sqrt S\). Exact golden nesting would require

\[
\sqrt S=\phi
\quad\Longrightarrow\quad
S=\phi^2,
\]

but \(S\) is an integer and \(\phi^2\) is irrational. Therefore

\[
\boxed{
\text{no fixed exactly nested Goldberg transform has linear ratio }\phi.
}
\]

The Fibonacci construction is a sequence of independently closed shells whose
successive ratios approach \(\phi\). This distinction must remain visible in the
v3 HUD.

---

# PART IV -- THE EXACT LIGHT MATRIX

## 8. Lift the pair recursion into quadratic shell data

Set

\[
u_n=
\begin{pmatrix}
k_n^2\\ k_n\ell_n\\ \ell_n^2
\end{pmatrix}.
\]

Since \(k'=k+\ell\) and \(\ell'=k\),

\[
\boxed{
u_{n+1}=B u_n,
\qquad
B=
\begin{pmatrix}
1&2&1\\
1&1&0\\
1&0&0
\end{pmatrix}.
}
\]

Append the invariant pentagon coordinate:

\[
s_n=
\begin{pmatrix}
k_n^2\\ k_n\ell_n\\ \ell_n^2\\ P_n
\end{pmatrix},
\qquad P_n=12.
\]

The v3 core matrix is

\[
\boxed{
s_{n+1}=\mathcal M_{\mathrm{light}}s_n,
\qquad
\mathcal M_{\mathrm{light}}=
\begin{pmatrix}
1&2&1&0\\
1&1&0&0\\
1&0&0&0\\
0&0&0&1
\end{pmatrix}.
}
\]

Its characteristic polynomial is

\[
\boxed{
\det(\lambda I-\mathcal M_{\mathrm{light}})
=(\lambda-1)(\lambda+1)(\lambda^2-3\lambda+1).
}
\]

Therefore

\[
\boxed{
\operatorname{spec}(\mathcal M_{\mathrm{light}})
=\{\phi^2,\ 1,\ -1,\ \phi^{-2}\}.
}
\]

A convenient eigenbasis is

\[
\begin{array}{c|c|l}
\lambda & \text{eigenvector} & \text{role}\\ \hline
\phi^2 & (\phi^2,\phi,1,0)^{\mathsf T} & \text{dominant area/atom growth}\\
1 & (0,0,0,1)^{\mathsf T} & \text{the fixed }P=12\text{ topological mode}\\
-1 & (-2,1,2,0)^{\mathsf T} & \text{alternating overshoot around the golden ray}\\
\phi^{-2} & (\phi^{-2},-\phi^{-1},1,0)^{\mathsf T} & \text{decaying correction / inward mode}
\end{array}
\]

This is the exact algebraic heart of the name **LIGHT MATRIX**. It has a growth
mode, an invariant mode, an alternating mode, and a contracting mode in one
integer recursion.

**Status: EXACT.** No fit was used to obtain these four eigenvalues.

---

# PART V -- TWO FRACTALIZATION LANES, NEVER CONFUSED AGAIN

## 9. Lane A -- local hexagon compute

`GK.refineAllHexes()` and related face-local operations create a hierarchy inside
the currently rendered mesh. They are useful for allocating compute, tracing a
curve, and exploring local recursive structure.

But an independently refined face does not automatically weld its boundary to
its neighbor. Therefore the output may be an **OPEN CANDIDATE** with boundary
edges, nonmanifold edges, or \(\chi\ne2\).

The v3 rule is:

```text
HEX_LOCAL / ALL / 5s / 6s
    -> hierarchy and compute budget
    -> run exact topology verifier
    -> label CLOSED only if the verifier passes
    -> otherwise label OPEN CANDIDATE and light the unpaid seams
```

Never infer closure from the formula counts alone.

## 10. Lane B -- certified shell closure

A closure operator changes the lattice coordinate and then constructs or loads a
closed indexed graph:

```text
GC_CLOSE(a,b):  (k,l) -> canonical((a+b*zeta6)(k+l*zeta6))
GOLDEN_NEXT:    (k,l) -> (k+l,k)
LEAPFROG:       exact GC area multiplier 3
WELD:           existing exact-ID chamfer lineage, verified independently
```

For every candidate, the closure certificate must verify

\[
\boxed{
P=12,
\quad \chi=2,
\quad \partial E=0,
\quad E_{\mathrm{nonmanifold}}=0,
\quad \deg(v)=3\ \forall v.
}
\]

The old sentence “C60 \(\to\) C420 is a closed shell because the formula says so”
is retired. The legacy 7x face hierarchy may be a useful graph mutation, but the
current kernel itself shows that its unwelded states are open. The certified
closed lineages are named separately.

### Existing WELD lineage

The exact-ID chamfer/WELD operator currently verifies

\[
\boxed{C_{60}\to C_{240}\to C_{960}\to C_{3840}\to\cdots}
\]

with \(V\mapsto4V\), \(P=12\), \(\chi=2\), closed twin half-edges, and degree 3.
This is a separate exact closure family from the Fibonacci selector and the
leapfrog \(3^n\) tower.

---

# PART VI -- THE STABILITY LINES

## 11. Stability line A -- topology

For every certified closed fullerene in this class,

\[
\boxed{P_n=12.}
\]

In \(\mathcal M_{\mathrm{light}}\), this is the eigenvalue-1 mode. It neither
grows nor decays.

## 12. Stability line B -- the golden projective ray

For the Fibonacci selector,

\[
\boxed{\frac{k_n}{\ell_n}\to\phi,}
\]

and deviations alternate while shrinking asymptotically by \(\phi^{-2}\).
This is a projective stability line, not a physical energy minimum.

## 13. Stability line C -- the exact C60 spectral boundary

Let \(A_{60}\) be the adjacency matrix of the combinatorial truncated
icosahedron. The supplied exact SymPy certificate factors its characteristic
polynomial as

\[
\begin{aligned}
\chi_{A_{60}}(x)={}&(x-3)(x-1)^9(x+2)^4
(x^2-x-3)^5(x^2+x-4)^4\\
&\times(x^2+x-1)^5(x^2+3x+1)^3
(x^4-3x^3-2x^2+7x+1)^3.
\end{aligned}
\]

The smallest root comes from \(x^2+3x+1\):

\[
\boxed{
\lambda_{\min}(A_{60})
=\frac{-3-\sqrt5}{2}
=-\phi^2,
}
\]

with multiplicity 3.

This is an exact occurrence of the golden ratio in the C60 graph spectrum. It is
not by itself a complete theorem of chemical stability. The adjacency matrix is
a graph/Hueckel-style object; a real molecular Hamiltonian contains additional
physics.

## 14. Stability line D -- the renormalized Laplacian tower

For a cubic fullerene graph \(G_n\), define

\[
A_n=A(G_n),
\qquad
L_n=3I-A_n.
\]

On the exact leapfrog tower

\[
G_0=C_{20},
\qquad
G_{n+1}=\operatorname{Leapfrog}(G_n),
\qquad
T_n=3^n,
\]

measure the first nonzero eigenvalue \(\lambda_2(L_n)\) and renormalize it:

\[
\boxed{
\mu_{1,n}=T_n\lambda_2(L_n).
}
\]

The supplied computation reached 43,740 vertices:

| level | \(V\) | \(T\) | \(\lambda_2(L)\) | \(T\lambda_2(L)\) |
|---:|---:|---:|---:|---:|
| 0 | 20 | 1 | 0.7639320225 | 0.7639320225 |
| 1 | 60 | 3 | 0.2434017461 | 0.7302052384 |
| 2 | 180 | 9 | 0.08056267490 | 0.7250640741 |
| 3 | 540 | 27 | 0.02683538324 | 0.7245553475 |
| 4 | 1,620 | 81 | 0.008946119207 | 0.7246356558 |
| 5 | 4,860 | 243 | 0.002982425496 | 0.7247293955 |
| 6 | 14,580 | 729 | 0.0009942087404 | 0.7247781718 |
| 7 | 43,740 | 2,187 | 0.0003314124966 | 0.7247991301 |

Thus the unscaled gap closes, while the scaled gap exhibits a stable numerical
line:

\[
\boxed{
T_n\lambda_2(L_n)\approx0.7248
\quad\text{at the deepest computed levels.}
}
\]

**Status: COMPUTED TREND, not an exact constant and not yet a proved limit for
this specific tower.** The code reports successive values and their difference;
it does not hard-code 0.7248 as a target.

### The low-mode band pattern

At \(V=43{,}740\), the beginning of the spectrum of \(T_nL_n\) is

| scaled eigenvalue | multiplicity |
|---:|---:|
| 0.724799130 | 3 |
| 2.167654166 | 5 |
| 4.026433004 | 3 |
| 4.596940196 | 4 |

On a smooth sphere, Laplace--Beltrami levels are proportional to
\(\ell(\ell+1)\) with multiplicity \(2\ell+1\). The computed ratios give

\[
\frac{2.167654166}{0.724799130}=2.990696\approx3
=\frac{2\cdot3}{1\cdot2}.
\]

The next seven-dimensional spherical band is split by icosahedral symmetry into
multiplicities 3 and 4. Its multiplicity-weighted center is

\[
\bar\mu_3
=\frac{3(4.026433004)+4(4.596940196)}{7}
=4.352437114,
\]

so

\[
\frac{\bar\mu_3}{0.724799130}=6.005025\approx6
=\frac{3\cdot4}{1\cdot2}.
\]

This is strong evidence that the renormalized graph operator is recovering the
low spherical harmonic pattern while retaining icosahedral splitting. It is a
numerical continuum-limit signature, not proof that the graph is physical
spacetime.

### The first-order central adjacency gap

The same run measured the graph-only central adjacency gap \(\Delta_A\). The
unscaled gap falls, while

\[
\sqrt{T_n}\,\Delta_A
\]

reached approximately \(2.02997\) at the deepest level. This is a **COMPUTED
TREND / Hueckel-style proxy**, not a molecular band-gap calculation.

## 15. The hierarchy has dimension two

The number of graph sites grows as \(V\propto T\), while the linear scale grows
as \(R\propto\sqrt T\). Therefore

\[
\boxed{
D=\lim_{n\to\infty}\frac{\log V_n}{\log R_n}=2.
}
\]

The tower is self-similar and hierarchical, but it does not acquire a
non-integer Hausdorff dimension from these counts. In THEA, *fractal* means the
recursive hierarchy unless a non-integer dimension is separately demonstrated.

---

# PART VII -- \(\phi\), \(\pi\), \(h\), AND THE HONEST WALL

## 16. What each constant is doing

\[
\boxed{
\begin{array}{rcl}
\phi &:& \text{dimensionless projective scale attractor and pentagonal ratio},\\
\pi &:& \text{angle/closure constant: }\zeta=e^{i\pi/3},\ \sum K=4\pi,\\
\hbar &:& \text{dimensionful quantum of action: }\hbar=h/(2\pi).
\end{array}
}
\]

The first two arise inside pure geometry. The third does not follow from a
dimensionless graph unless an independent physical scale is supplied.

Planck's constant has dimensions

\[
[h]=ML^2T^{-1}.
\]

Therefore an equation such as \(R_n=h\) is dimensionally invalid. A length test
must use a length, for example

\[
\boxed{
\ell_P=\sqrt{\frac{\hbar G}{c^3}}.
}
\]

Even then, using \(\ell_P\) as an indivisible cutoff is a physical hypothesis,
not a consequence of its definition.

## 17. The inward pentagram test

A regular pentagram contains a similar central pentagon with linear contraction

\[
\boxed{q=\phi^{-2}.}
\]

A face-local inward hierarchy is therefore

\[
R_j=R_0\phi^{-2j}.
\]

Setting \(R_N=\ell_P\) gives

\[
\boxed{
N=\frac{\log(R_0/\ell_P)}{2\log\phi}.
}
\]

Using an ideal C60 edge \(a=1.42\times10^{-10}\,\mathrm m\),

\[
R_0=\frac a4\sqrt{58+18\sqrt5}
\approx3.5187865\times10^{-10}\,\mathrm m.
\]

With \(\ell_P=1.616255\times10^{-35}\,\mathrm m\), the code obtains

| chosen starting length | level count with \(q=\phi^{-2}\) |
|---|---:|
| edge \(a\) | 59.677640345 |
| radius \(R_0\) | 60.620530010 |
| diameter \(2R_0\) | 61.340740056 |

The near-60 value is interesting, but its movement under a legitimate change of
starting length proves that it is not presently a topological invariant. The
correct label is

\[
\boxed{\text{NUMERICAL COINCIDENCE / HYPOTHESIS TEST, NOT DERIVATION.}}
\]

The inward pentagram is also a **face-local geometry lane**. A finite fullerene
graph itself terminates combinatorially at \(C_{20}\), or at \(C_{60}\) if the
isolated-pentagon rule is imposed; it does not contain sixty nested molecular
shells.

---

# PART VIII -- THE V3 CODE PATTERNS

## 18. Pattern A -- exact integer core first

The browser kernel uses `BigInt` for \((k,\ell,T,V,E,F,P,H)\). Floating point is
used only for ratios and spectral measurements.

```javascript
function hexNorm(p) {
  var k = BigInt(p.k), ell = BigInt(p.ell);
  return k*k + k*ell + ell*ell;
}

function topologyFromT(T) {
  T = BigInt(T);
  var V = 20n*T, E = 30n*T;
  var P = 12n, H = 10n*(T-1n), F = P+H;
  return {T:T, V:V, E:E, F:F, P:P, H:H, chi:V-E+F};
}

function goldenNext(p) {
  return {k:BigInt(p.k)+BigInt(p.ell), ell:BigInt(p.k)};
}
```

**Rule:** do not certify an integer invariant with a float tolerance when exact
integer arithmetic is available.

Full module: `light_matrix_v3.js`.

## 19. Pattern B -- exact closure multiplication

```javascript
function multiplyPairs(left, right) {
  var a=BigInt(left.k), b=BigInt(left.ell);
  var k=BigInt(right.k), ell=BigInt(right.ell);
  return {
    k:   a*k - b*ell,
    ell: a*ell + b*k + b*ell
  };
}
```

After multiplication, canonicalize under the twelve dihedral symmetries of the
hexagonal lattice and display the representative with \(k\ge\ell\ge0\).

## 20. Pattern C -- route local growth and closure growth separately

```javascript
function applyOperator(state, op) {
  if (op.kind === "HEX_LOCAL") {
    var candidate = GK.refineAllHexes(state.mesh, op.params);
    var cert = GK.verifyTopoIndexed(candidate);
    return {
      lane: "LOCAL",
      mesh: candidate,
      certificate: cert,
      label: cert.pass ? "CLOSED VERIFIED" : "OPEN CANDIDATE"
    };
  }

  if (op.kind === "GOLDEN_NEXT") {
    var nextPair = LightMatrixV3.goldenNext(state.pair);
    return requestClosedShell(nextPair); // builder or certified asset
  }

  if (op.kind === "GC_CLOSE") {
    var next = LightMatrixV3.gcStep(state.pair, op.generator);
    return requestClosedShell(next);
  }

  throw new Error("unknown operator");
}
```

The exact closed graph builder may be offline. The browser can load a certified
indexed mesh and replay the topology certificate before installation.

## 21. Pattern D -- target, current, and error are separate

There are two different stability reports. Do not average them.

### Golden selector lock

\[
e_{\phi,n}=\left|\frac{k_n}{\ell_n}-\phi\right|.
\]

```javascript
var golden = LightMatrixV3.goldenReport(pair, 1e-8);
// show all four fields:
// target = phi
// current = k/ell
// error = abs(current-target)
// locked = topologyPass && error <= tolerance
```

### Spectral lock

\[
\mu_n=T_n\lambda_2(L_n),
\qquad
e_{\mu,n}=|\mu_n-\mu_{n-1}|.
\]

```javascript
var spectral = LightMatrixV3.spectralReport(previous, current, 1e-5);
// no hard-coded 0.7248 prize
// the lock is earned by successive stabilization + topology pass
```

The HUD should read, for example:

```text
TOPOLOGY   P 12 / chi 2 / boundary 0 / degree-3 100%   PASS
GOLDEN     target 1.61803398875  current 1.61797752809
           error 5.6461e-5       NOT LOCKED at tol 1e-8
SPECTRAL   current T*lambda2 0.7247991301
           delta from prior 2.0958e-5                    NOT LOCKED
```

## 22. Pattern E -- predict before allocating

Every exact closure operator has a known count multiplier. Gate the next step
before constructing the graph:

```javascript
var gate = LightMatrixV3.predictAndGate(
  currentVertices,
  areaMultiplier,
  VERTEX_BUDGET
);
if (!gate.allowed) {
  haltLoudly("next shell = "+gate.predicted+" vertices > budget "+gate.budget);
  return;
}
```

This is Curse 35 applied to the mathematical recurrence itself.

## 23. Pattern F -- offline spectrum, online receipt

Large sparse eigensolves belong in the Python lab, not on the browser main
thread. The v3 pipeline is

```text
light_matrix_v3.py
    -> exact identities
    -> construct closed graphs
    -> topology certificate
    -> sparse eigensolve
    -> JSON receipt with values, multiplicities, parameters, and status labels

AEQUALIUM v3
    -> load receipt
    -> hash / schema check
    -> replay cheap invariants
    -> display COMPUTED values, never relabel them EXACT
```

Suggested repository paths:

```text
kernel/light_matrix_v3.js
experiments/light_matrix_v3.py
tests/test_light_matrix_v3.py
receipts/light_matrix_v3_certificate.json
grimoire/THEA_v3.0.md
```

## 24. Pattern G -- minimal Python use

```python
from light_matrix_v3 import Pair, golden_next, shell_from_pair

pair = Pair(1, 0)
for level in range(8):
    shell = shell_from_pair(pair, level)
    print(level, shell.k, shell.ell, shell.vertices, shell.pentagons, shell.chi)
    pair = golden_next(pair)
```

Full spectral run:

```bash
python light_matrix_v3.py \
  --golden-levels 12 \
  --spectral-levels 8 \
  --band-count 30 \
  --exact-c60 \
  --json light_matrix_v3_certificate.json \
  --text light_matrix_v3_results.txt
```

Fast exact tests:

```bash
python -m unittest -v test_light_matrix_v3.py
node --check light_matrix_v3.js
node -e "const L=require('./light_matrix_v3.js'); console.log(L.selfTest())"
```

---

# PART IX -- COPY-READY LATEX CORE

The following block is ready for KaTeX/LaTeX reuse.

```latex
\newcommand{\phig}{\varphi}
\newcommand{\zetahex}{\zeta_6}
\newcommand{\Mlight}{\mathcal M_{\mathrm{light}}}
\newcommand{\Tgold}{T_n}

\[
\phig=\frac{1+\sqrt5}{2},
\qquad
\phig^2=\phig+1,
\qquad
\phig^{-2}=2-\phig.
\]

\[
3V=2E,
\qquad
5P+6H=2E,
\qquad
V-E+P+H=2
\quad\Longrightarrow\quad
P=12.
\]

\[
\zetahex=e^{i\pi/3},
\qquad
T=k^2+k\ell+\ell^2,
\qquad
M_{k,\ell}=\begin{pmatrix}k&-\ell\\\ell&k+\ell\end{pmatrix}.
\]

\[
\det M_{k,\ell}=T,
\qquad
M_{k,\ell}^{\mathsf T}
\begin{pmatrix}1&\tfrac12\\\tfrac12&1\end{pmatrix}
M_{k,\ell}
=T\begin{pmatrix}1&\tfrac12\\\tfrac12&1\end{pmatrix}.
\]

\[
(k',\ell')=(ak-b\ell,\ a\ell+bk+b\ell),
\qquad
T'=(a^2+ab+b^2)T.
\]

\[
\begin{pmatrix}k_{n+1}\\\ell_{n+1}\end{pmatrix}
=\begin{pmatrix}1&1\\1&0\end{pmatrix}
\begin{pmatrix}k_n\\\ell_n\end{pmatrix},
\qquad
(k_n,\ell_n)=(F_{n+1},F_n).
\]

\[
T_n=k_n^2+k_n\ell_n+\ell_n^2,
\qquad
V_n=20T_n,
\quad E_n=30T_n,
\quad P_n=12,
\quad H_n=10(T_n-1).
\]

\[
T_{n+3}=2T_{n+2}+2T_{n+1}-T_n,
\qquad
T_n=\frac25\left(\phig^{2n+2}+\phig^{-2n-2}\right)
-\frac15(-1)^n.
\]

\[
\Mlight=
\begin{pmatrix}
1&2&1&0\\
1&1&0&0\\
1&0&0&0\\
0&0&0&1
\end{pmatrix},
\qquad
\det(\lambda I-\Mlight)
=(\lambda-1)(\lambda+1)(\lambda^2-3\lambda+1).
\]

\[
\operatorname{spec}(\Mlight)
=\{\phig^2,1,-1,\phig^{-2}\}.
\]

\[
L_n=3I-A_n,
\qquad
\mu_{j,n}=T_n\lambda_j(L_n).
\]

\[
\lambda_{\min}(A_{C_{60}})
=-\phig^2
=-\frac{3+\sqrt5}{2}.
\]

\[
\frac{\pi}{3}\sum_f(6-p_f)=4\pi.
\]

\[
\ell_P=\sqrt{\frac{\hbar G}{c^3}},
\qquad
N=\frac{\log(R_0/\ell_P)}{2\log\phig}
\quad\text{for the chosen face-local scale }q=\phig^{-2}.
\]
```

---
## THE MATH CORE -- every formula, audited, stepped into compute
### source of truth: `shell/aequalium_v2.4.7.html` (shipped audited kernel)

> WARNING (Path III/IV): the older `AEQUALIUM_TOWER.md` predates the Sol-mage
> audit and carries STALE math (a 25-term power-series `besselJ`, an unlabelled toy
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
a roundoff wall beneath every rung. Method-specific ceilings are reported separately and are never averaged.

---

### RUNG 1 -- QCD I . the running coupling a_s(Q)    [CONVERGES]

**Paper:** `a_s(Q) = a_s(MZ) / (1 + a_s(MZ) (b0/4pi) ln(Q^2/MZ^2))`
**Means:** a geometric series in `x = a-hat0 b0 L`, `L = ln(Q^2/MZ^2)`; for
`|x|<1` it converges to float64 fast.
**Code:** finite geometric partial sum, depth N. `b0 = 11 CA/3 - 4 TF nf/3 = 23/3` at nf=5.
**Verdict:** CONVERGENT. D: ~8 at C60 -> ~15.5 grown.

### RUNG 2 -- QCD II . R-ratio TOY renormalon model    [HARD CEILING]  (showpiece)

**Paper context:** `R = 3 sum_q e_q^2 (1 + a_s/pi + c2 a_s^2 + ...)`.
**Model used here:** synthetic coefficients `c_n = n! beta0^n` imitate a
factorially growing asymptotic series. They are **not** the known physical
R-ratio coefficients and the displayed number is **not** a QCD prediction.
**Code (audited, Sol #3 -- three quantities kept apart):**
- `raw = S_N` -- the raw partial sum, allowed to explode and shown exploding.
- `anchor = S_{N*}` -- the optimal-truncation value, frozen once `N >= N*`.
- `delta* = |t_{N*}|` -- the smallest term, used as a model ambiguity estimate.
- score = `delta* / |anchor|`, constant past N*: exploding harder can never
  manufacture more agreement.
**Verdict:** HARD CEILING **inside the illustrative model**. The lesson is about
optimal truncation and honest ambiguity accounting, not a new physical R value.

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
**Verdict:** CONVERGENT. At the v2.4.7 seed budget N=16, D is about 6.7; it rises with panel count until the numerical reference/float ceiling.

### RUNG 6 -- GALACTIC III . the blackbody integral    [CONVERGES, slow N^-3]

**Paper:** `integral_0^inf x^3/(e^x - 1) dx = pi^4 / 15`  (Stefan-Boltzmann)
**Means:** expand `1/(e^x-1) = sum_{k>=1} e^{-kx}`, integrate termwise ->
`6 sum_{k>=1} k^-4 = 6 zeta(4) = pi^4/15`. Partial-sum error `~ 2/N^3`.
**Code:** `approx = 6 * sum_{k=1..N} 1/k^4`.
**Verdict:** CONVERGENT but SLOW. At the v2.4.7 seed budget N=16, D is about 4.2 and improves only as N^-3.

---

### THE MATH-CORE SUMMARY TABLE

| # | rung | method | error law | verdict | v2.4.7 seed readout (N=16) |
|---|------|--------|-----------|---------|-----------------------------|
| 1 | a_s(Q) running | geometric resum | geometric | CONVERGES | D about 8.0 |
| 2 | R-ratio toy | synthetic asymptotic series | factorial floor | **MODEL CEILING** | ambiguity metric about 5.1 |
| 3 | Lambda_QCD | Newton rootfind | quadratic | CONVERGES | D about 15.0 |
| 4 | Kepler, e=0.50 | Bessel series (Miller) | converges for e<1 | CONVERGES | D about 5.4 |
| 5 | D_C comoving | Simpson quadrature | N^-4 | CONVERGES | D about 6.7 |
| 6 | blackbody | 6 zeta(4) | N^-3 | CONVERGES (slow) | D about 4.2 |

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

# PART X -- THE V3 POINT

## THE POINT, ONE LINE

> The light matrix is the exact integer recursion that separates growth,
> invariant topology, alternating correction, and contraction; the closed graph
> tower then turns that recursion into a renormalized spectrum whose remaining
> error is measured rather than narrated.

Or, in the cave's shorter language:

> **The pentagons hold. The hexes pay. The matrix remembers which is which.**

---

## CODA -- what v3 actually earned

### EXACT

- A closed trivalent pentagon/hexagon fullerene has exactly \(P=12\).
- The total combinatorial curvature charge is \(4\pi\).
- The hexagonal lattice norm is \(T=k^2+k\ell+\ell^2\).
- The closure matrix satisfies
  \(M_{k,\ell}^{\mathsf T}QM_{k,\ell}=TQ\).
- Closure composition is integer multiplication in the hexagonal lattice ring,
  and \(T\) is multiplicative.
- Icosahedral Goldberg shells have
  \(V=20T, E=30T, H=10(T-1), F=10T+2\).
- The Fibonacci selector converges projectively to \(\phi\).
- The lifted light matrix has spectrum
  \(\{\phi^2,1,-1,\phi^{-2}\}\).
- The exact symbolic C60 adjacency certificate has
  \(\lambda_{\min}=-\phi^2\) with multiplicity 3.

### COMPUTED

- The closed leapfrog tower was constructed through \(V=43{,}740\).
- At every computed level: connected, cubic, \(P=12\), only five/six faces,
  and \(\chi=2\).
- \(T\lambda_2(L)\) stabilized numerically near \(0.7248\).
- The first two low bands have multiplicities 3 and 5 and ratio about 2.9907.
- The next seven modes split 3+4, with weighted-center ratio about 6.0050.
- \(\sqrt T\,\Delta_A\) reached about 2.02997 on the same tower.

### DESIGN CHOICE

- Calling the four-mode recursion the **LIGHT MATRIX**.
- Mapping face/vertex budget to the number of terms a formula may spend.
- The operator deck and UI tolerances.
- Which exact closed-shell family the user explores: WELD, fixed GC, leapfrog,
  or golden-selected catalogue.
- The use of a pentagram contraction \(q=\phi^{-2}\) for a face-local inward
  thought experiment.

### HYPOTHESIS -- still owes the price

- Reality or quantum foam is generated by this graph tower.
- The stable renormalized graph spectrum is a physical field spectrum.
- The Planck scale is the termination of a golden face recursion.
- \(h\) or \(\ell_P\) can be derived from \(\phi\), \(\pi\), and fullerene
  topology without independent dimensionful input.
- The numerical constants 0.7248 or 2.03 are universal rather than
  tower/operator dependent.

### METAPHOR / EXTERNAL

- “Light stitches the curve,” “the soul of the shell,” and similar cave imagery.
- CASCADIUM as a separate PDE artifact: audit its solver and ledger separately.
- Any Connes/noncommutative-geometry interpretation imported from another repo.

---

## THE HONEST BOUNDARY ON THE LATTICE -- v3 edition

The v2 audit survives intact and becomes sharper:

1. A Fourier optimum that moves with sample count is a representation/sampling
   effect, not evidence of a Planck lattice.
2. A local face recursion is not automatically a closed polyhedron.
3. A golden-selected sequence is not the same object as an exactly nested
   Goldberg transform.
4. A graph adjacency eigenvalue is not automatically a molecular energy.
5. A converging numerical line is not an exact constant until proved.
6. A dimensionless matrix cannot produce a dimensionful \(h\) without a physical
   scale and a dynamical law.

The defensible thesis remains strong:

> Every scientific equals sign hides a representation, a finite operation,
> assumptions, costs, errors, and a verdict. A truthful artifact exposes that
> chain and makes every substrate claim pass through it.

---

## V3 BUILD CONTRACT -- ready to integrate

The mathematics and reference kernels in this update are built. The browser
visual integration is the next versioned artifact.

### Built in this receipt

- `Thea_v3.0.md` -- this complete derivation and integration contract.
- `light_matrix_v3.py` -- exact shell arithmetic, graph construction, spectra,
  exact C60 factorization, Planck-choice test, and JSON export.
- `light_matrix_v3.js` -- browser-safe BigInt core and honest lock reports.
- `test_light_matrix_v3.py` -- fast exact regression tests.
- `light_matrix_v3_certificate.json` -- machine-readable output.
- `light_matrix_v3_results.txt` -- human-readable computed receipt.

### V3 visual behavior

The AEQUALIUM v3 panel should display four independent rows:

```text
CLOSURE     exact pair (k,l), T, V/E/F/P/H, chi, certificate hash
GOLDEN      target phi, current k/l, error, tolerance, lock state
SPECTRUM    lambda2, T*lambda2, delta from prior, multiplicity bands
BOUNDARY    EXACT / COMPUTED / DESIGN / HYPOTHESIS label for every claim
```

The operator buttons should be grouped by lane:

```text
LOCAL HIERARCHY:  ALL | 5s | 6s
CLOSED SHELL:     WELD | LEAPFROG | GC(a,b) | GOLDEN NEXT
```

An open local candidate may still be rendered, but its seams must be visible and
its shell name withheld. A closed shell is installed only after the exact-ID
topology verifier passes.

### V3 experiments that remain open

- Generate actual indexed meshes for arbitrary \((k,\ell)\), not only counts.
- Compare WELD, leapfrog, and other fixed-GC families under the same spectral
  normalization.
- Test whether the 0.7248 line is operator-dependent.
- Fit finite-size corrections without pretending the extrapolated intercept is
  exact.
- Test locality, isotropy, propagation speed, conservation, and preferred-frame
  artifacts for any proposed substrate dynamics.
- Find one observable not inserted by construction that discriminates this
  forward model from ordinary continuum physics.

Until those tests pass, THEA v3 is a rigorous mathematical generator and a
spectral laboratory, not a final theory of reality.

---

## REFERENCES / EXTERNAL ANCHORS

These references support the external mathematical context. The core identities
above are also derived and reproduced directly by the supplied code.

1. P. W. Fowler, P. Hansen, and D. Stevanovic, “A Note on the Smallest
   Eigenvalue of Fullerenes,” *MATCH Communications in Mathematical and in
   Computer Chemistry* **48** (2003), 37--48.
2. T. Omori, H. Naito, and T. Tate, “Eigenvalues of the Laplacian on the
   Goldberg--Coxeter Constructions for 3- and 4-Valent Graphs,” *Electronic
   Journal of Combinatorics* **26**(3) (2019), P3.7; arXiv:1807.10891.
3. S. Li, “Transformation, Identification, and Inversion of Goldberg--Coxeter
   Fullerenes,” arXiv:2303.07890.
4. NIST, revised-SI value of the Planck constant
   \(h=6.62607015\times10^{-34}\,\mathrm{J\,s}\) exactly.
5. NIST CODATA, Planck length
   \(\ell_P=1.616255\times10^{-35}\,\mathrm m\) at the precision used in the
   supplied hypothesis test.

---

*THEA v3.0 -- the math core. The light matrix runs; closure is certified; the
pentagons hold; the hexes pay; the error remains visible.*

*P=12. chi=2. spec(M_light)={phi^2,1,-1,phi^-2}. The price is always paid. Always.*

---
---

# PART XI -- THE v1.3.x LINE, AND WHAT SECTION X SETTLED
### *added 2026-09-01, from `shell/thea_light_matrix_v1.3.9.html`*

THEA v3.0 above was written on 2026-07-31 against `aequalium_v2.4.7` and
`light_matrix_v3.py`. The page has moved on three times since. This part
records what changed, measured rather than remembered, and one number it
settles that this cave had open.

## THE LINEAGE -- and the mathematics did not change

| version | bytes | what moved |
|---|---:|---|
| `v1.3.7` | 481,650 | KaTeX from a CDN, plus ~300 KB of **pre-rendered** KaTeX SVG inline |
| `v1.3.8` | 181,929 | the CDN and the pre-rendered SVG both gone. **Self-contained, zero external links.** |
| `v1.3.9` | 209,625 | adds the **dependency DAG** over the sections |

**All nineteen `claim:` strings are byte-identical across all three.** Checked
by extracting them in order and comparing; 19/19 in both directions. So the
delivery changed twice and the mathematics did not change at all -- which is
the honest reading of a 60% size drop, and the reason to check before assuming
something was lost.

Two things worth knowing before opening them:

* **v1.3.8 and v1.3.9 have no `</body>` and no `</html>`.** v1.3.7 has both.
  All four `<script>` blocks in each file pass `node --check` (88,477 /
  17,381 / 16,501 / 15,542 chars in v1.3.8; 109,443 / same three in v1.3.9),
  so the files are **complete** and the omission is authoring, not truncation.
  They are shipped exactly as received -- byte-identical, sha256 verified --
  because a page we silently repaired would no longer be the author's v1.3.9.
* v1.3.8 dropping the CDN is a real gain and not only a size one: the page now
  has **zero external links**, so it renders from the filesystem with nothing
  to fetch and nothing to go stale.

## WHAT v1.3.9 ADDS -- the scroll learns its own shape

Nineteen sections, each now carrying a level and a dependency list:

```text
  ☀  lv0             I  lv0  <- ☀           II  lv1
  III lv1 <- II      IV lv0                  V  lv2 <- IV
  VI  lv2 <- V,IV    VII lv3 <- ☀,I         VIII lv3 <- VII,VI
  IX  lv5 <- VI      X  lv3 <- VII,VIII,III  XI lv1 <- IV
  XII lv1 <- I       XIII lv3 <- XII         XIV lv5 <- VI
  XV  lv4 <- VI,XIV  XVI lv5 <- XIV          XVII lv6 <- IX,XIV
  XVIII lv5 <- XV,XIV,II
```

Seven levels, 0 through 6. The page can now say which sections a claim rests
on, which is the difference between a list of results and a tower. **STATUS:
COMPUTED** -- the graph is in the page and drawn from it, not asserted here.

## SECTION X SETTLES A NUMBER THIS CAVE HAD OPEN

`OPEN #6` in the 2026-08-19 and 2026-08-21 handoffs asked what the true
constant is in the shell's spectral gap, against HELENI v2's `lambda_2 =
4.3484/T`.

Section X derives it from three gifts, **none of them ours**: the honeycomb
three-point stencil (three bonds at 120 degrees give \(\Sigma(\hat e\cdot
\nabla)^2 = \tfrac32\nabla^2\), so \(L \approx -\tfrac34 a^2\nabla^2\)); the
bookkeeping of area (each site owns \(\tfrac{3\sqrt3}{4}a^2\), and twelve
pentagons are measure zero as \(T\to\infty\)); and the sphere's own ladder
\(\ell(\ell+1)\) with degeneracies 3, 5, 7. Multiply the three:

$$T\cdot\lambda_2 \;\longrightarrow\; \frac{2\pi}{5\sqrt3} \;=\; 0.7255197\ldots$$

**And it agrees with what was measured here, independently, before v1.3.9
existed.** On 2026-08-20 the C60 adjacency spectrum was diagonalised in this
cave with a Jacobi rotation using only `+ - * / sqrt` -- the certified path, no
transcendentals:

| T | shell | \(\lambda_2(L)\) measured | \(T\lambda_2\) | gap from \(2\pi/5\sqrt3\) |
|---:|---|---:|---:|---:|
| 1 | C20 | \(3-\sqrt5=0.763932\) | 0.763932 | **+0.03841** |
| 3 | C60 | 0.243402 | 0.730205 | **+0.00469** |

Both above the limit, and **the gap shrank by a factor of eight in one rung.**

> **STATUS, SUPERSEDED 2026-09-01. The third rung was run, and twenty-two
> more with it. The sequence CROSSES the derived constant at T~7, bottoms out
> near T~30, and climbs back to 0.72471 at T=196 (V=3,920) -- still 0.11%
> short and rising ever more slowly. Five extrapolation models all land
> 0.7247-0.7249; none reaches 0.7255197. The  FORM holds. The CONSTANT
> does not. See  and
> . Two points agree with any curve drawn
> between them.**

And the contrast that closes the open item:

```text
  derived      2*pi/(5*sqrt3)  =  0.7255197
  HELENI v2    4.3484          =  5.994 x the derived limit
```

Within 0.1% of exactly **six times** too large. **HYPOTHESIS, and it must be
labelled one:** a factor of six is what a hexagon's neighbour count looks like,
so a per-vertex versus per-edge normalisation is the first place to look. It
may equally be coincidence at that precision. Nobody has checked, and this
scroll should not pretend otherwise.

## THE THREE SECTIONS THAT KEEP THEIR OWN MISTAKES

Worth naming, because the cave's own laws say the wrong half is usually the
finding, and this page practises it rather than citing it:

* **XIII** -- the first audit assumed the twelve vertices attract under
  \(g_{11}\). They do not; \(g_{11}\) attracts to the **twenty faces**. The
  correction is kept as the point of the section.
* **XV** -- a prediction was registered that the float64 ladder would compound
  catastrophically. It is **WRONG**, and structurally so. The refutation is
  kept instead of the prediction, *"because the record is the point."*
* **XVIII** -- and the finding that should worry us most:

> *"Four hundred sims deep and this is the first place float compute has
> cracked. ... The headline is not what you would guess: the cave's own
> invariant \(\chi = 2\) fails BEFORE the numbers it is made of."*

That last sentence belongs beside RUSTIUM R3 and the `THE TWO WALLS` section:
an invariant that fails *earlier* than its own inputs is a check whose failure
mode nobody priced. `Gos` derives \(\chi\) from trivalence precisely so it is
*allowed* to be wrong -- but it has never been run at the depth where v1.3.9
says the crack opens. **OWED: reproduce section XVIII's ladder in the Rust and
find out whether our \(\chi\) cracks at the same rung.**

## WHERE THEY LIVE

```text
  shell/thea_light_matrix_v1.3.8.html   sha256 702a4dfaf0130db4...
  shell/thea_light_matrix_v1.3.9.html   sha256 f249f65647ace8ca...
```

Both byte-identical to the files handed over. v1.1, v1.2, v1.3.1 and v1.3.7
stay frozen beside them -- Path X, the whole journey published, the dead ends
included.

The ENG dashboard was regenerated against them and the card advanced
`THEA_LIGHT_MATRIX_V1.3.7 -> V1.3.9` with all six versions still in the URL
map. Note what the scanner did *first*: it refused to card the new files while
they were untracked, because `sim_scan` holds that **TRUTH = GIT** -- Pages
will not serve an untracked file, so a card for one would be a lie. The count
moved 388 -> 390 only after `git add`.

---

*Added 2026-09-01. The mathematics did not change; the delivery got honest*
*twice, and the scroll learned its own dependency graph.*

*P=12. chi=2. T*lambda_2 -> 2*pi/(5*sqrt3). Two points are a trend.*

---
---

# PART XII -- THE DB PARADIGM, AND WHAT THE BITS SAID
### *added 2026-09-02, from `Gos/examples/net_db.rs` and `Gos/src/bits.rs`*

This scroll opens on points and lines with a value at each point. From
2026-09-02 that is not only the mathematics -- it is how the work is stored.

## THE PARADIGM

A net is no longer a thing you build and look at. It is a **row**:

```text
  inner, mid, zoom, rx, ry, rz, level          the permutation
  faces, pents, chi, coords                    the mesh          EXACT
  mantissa_ones, density, powers_of_two, ...   the bits          EXACT
  ink, l_entropy, distinct                     the picture       DISPLAY
  net_digest, image, netfile                   where to find it
```

Fixed width, so nets are comparable **without being looked at**: nearest
neighbours, clustering, *"every net whose density is under 0.1"*. The three
kinds of number are kept apart on purpose, and the lane is part of the schema
rather than a footnote about it.

**Two rules, both already load-bearing elsewhere in this cave:**

1. **The row is written only after the net certifies.** `P = 12` and
   `LANES AGREE` are asserted before a single field is emitted. A row
   describing a broken net poisons every query made against the table
   afterwards, and does it silently.
2. **The table travels; the payload does not.** One 5x5 sweep is 213 MB of
   renders and `.gosnet` files, all regenerable. `NETS.csv` is 76 KB and is the
   only part a query needs. Same rule as `helena_net/builds`, `Gos/runs`, and
   the `_private` hatch -- *keep the mirror, not the payload*.

## WHAT THE BITS SAID -- and it is a NO

The question was whether some choice of `(inner, mid)` lands the geometry
closer to ones and zeros than another. `bits::float_profile` answers it exactly,
by counting set mantissa bits: an f64 the machine holds *exactly* has a mantissa
of mostly zeros; one that had to be **rounded to fit** has a full one, because
the tail is where the error went.

100 rows, 5x5 parameters x 4 views, level 3:

```text
  mantissa density   min 0.4865   max 0.4957   spread 0.0092
  a random f64 sits at 0.5000 -- every net is within 2.7% of random
  exact powers of two: 2,140 of 185,220 coordinates = 1.16%
```

**The geometry cannot be made binary by choosing parameters.** Not at
`inner = 0.5`, not anywhere. The 1.16% that *are* exact are the seed's own
coordinates surviving, and refinement dilutes them: every refined point passes
through an average and a `project_to_sphere`, and the square root of anything
that is not a perfect square fills the mantissa.

### Why the no is worth more than a yes

It settles where a storage win can possibly come from. **You cannot make the
numbers cheaper -- they are already incompressible in this representation. You
can only store fewer of them.** Which is precisely the 5.27x that welding the
face soup into an indexed mesh offers, by removing *duplication* rather than
*entropy*.

Two independent measurements -- `memory_ladder` counting bytes, `net_db`
counting bits -- arriving at the same instruction. That agreement is the
finding; either alone would have been a number.

## THE PICTURE IS A DIFFERENT ANIMAL

```text
  L entropy   0.704 ................ 5.467      7.8x

  quietest  inner=0.95  mid=0.95  zoom=760   0.704 bits, ink 0.068
  busiest   inner=0.95  mid=0.05  zoom=260   5.467 bits, ink 0.681
```

Same `inner` in both -- only `mid` and the viewpoint differ. **What the eye
receives is enormously compressible; what the mesh IS is not.** That gap is now
a number instead of an intuition, and it is the reason the render and the mesh
are separate lanes in the schema.

## WHAT THIS OWES

* **The weld.** Both measurements now point at it and it is still step 6 of
  `GENESIS_PORT_SPEC.md`. The 5.27x is arithmetic from trivalence, not yet a
  built mesh.
* **A second sweep at another level.** Everything above is level 3. The
  dilution of exact coordinates with depth is stated from one ladder; a level-5
  sweep would either confirm the trend or break it.
* **The query side.** The table exists and nothing reads it yet. A row nobody
  queries is a row that could be wrong for months -- which is R13's whole
  lesson wearing a schema.

---

*Added 2026-09-02. Points and lines, and at each point a value: the value being*
*what it costs to write the point down. The answer to "how close to 1 and 0" is*
*0.4865, and 0.5 is a coin.*

**P=12 . chi=2 . the table travels, the payload stays home.**

