# SOL Triple Math Audit — 2026-08-03

Artifacts audited:

- `shell__penrosium_v0_1.html`
- `shell__penrosium_v0_2.html`
- `shell__stitchium_v0_1.html`
- `shell__thea_light_matrix_v1_2.html`
- `shell__hawkium_v0_1.html`

Audit method:

1. Analytic re-derivation of the central equations and status labels.
2. Independent execution of the embedded JavaScript kernels under Node.js.
3. Alternate numerical checks with SciPy/SymPy-style sparse eigensolvers or closed forms where useful.

All five inline JavaScript programs pass `node --check`.

---

## Executive verdict

| Artifact | Core mathematics | Main correction |
|---|---|---|
| PENROSIUM v0.1 | Strong / essentially correct | Fix one compactified-corner label; call finite computations computed rather than exact-measured |
| PENROSIUM v0.2 | Oppenheimer–Snyder model is correct | Kernel does not yet certify the full junction conditions; inverse chart is ill-conditioned near compactified boundaries |
| STITCHIUM v0.1 | Fullerene counts and graph-depth field are correct | `E-V+S` non-tree edges are not all independent cycles; BFS actually has `S` vertex roots, not twelve roots |
| THEA v1.2 | Exact algebra, C60 spectrum, and radicals are excellent | The continuum constant is a formal asymptotic prediction plus numerical support, not yet an exact theorem for the Goldberg tower |
| HAWKIUM v0.1 | Schwarzschild thermodynamics and Leaver QNMs are strong | Euclidean proper-distance quadrature has an endpoint bug; the greybody skip rule biases fluxes and its stated bound is false |

---

# 1. PENROSIUM v0.1

## Exact core confirmed

With `2M=1`, the kernel uses

\[
f(r)=1-\frac1r,
\qquad
r_*=r+\log|r-1|,
\qquad
K=\frac{12}{r^6}.
\]

The Kruskal convention

\[
U=-e^{-u/2},
\qquad
V=e^{v/2}
\]

implies

\[
UV=(1-r)e^r.
\]

The compactification

\[
\widetilde U=\arctan U,
\qquad
\widetilde V=\arctan V,
\]

\[
X=\frac{\widetilde V-\widetilde U}{2},
\qquad
T=\frac{\widetilde V+\widetilde U}{2}
\]

is internally consistent. At the curvature singularity,

\[
r=0
\Longleftrightarrow
UV=1
\Longleftrightarrow
\tan\widetilde U\tan\widetilde V=1,
\]

which gives

\[
T=\pm\frac\pi4
\]

on the relevant branches. Straightness is gauge-dependent; spacelikeness is invariant.

The radial geodesic released from rest at `r0` is correctly parametrized by

\[
r(\eta)=\frac{r_0}{2}(1+\cos\eta),
\]

\[
\tau(\eta)=\frac{r_0^{3/2}}2(\eta+\sin\eta),
\]

\[
\tau_{r=0}=\frac\pi2r_0^{3/2}.
\]

The cancellation-free ingoing Eddington–Finkelstein derivative is also correct:

\[
\frac{dv}{d\tau}
=
\frac{1}{E+\sqrt{E^2-f}}.
\]

Independent kernel checks returned finite horizon crossings and `T -> pi/4` at the singular endpoint.

## Small correction

The log text

```text
i±=(±π/4,±π/4)
```

is ambiguous and wrong if interpreted as only two correlated-sign points. The exact right/left corners are

\[
i_R^+=\left(\frac\pi4,\frac\pi4\right),
\quad
i_R^-=\left(\frac\pi4,-\frac\pi4\right),
\]

\[
i_L^+=\left(-\frac\pi4,\frac\pi4\right),
\quad
i_L^-=\left(-\frac\pi4,-\frac\pi4\right).
\]

The `PK.frame()` object itself is correct; only the prose/log shorthand needs repair.

---

# 2. PENROSIUM v0.2

## Oppenheimer–Snyder algebra confirmed

The interior scale factor and matching radius are correct:

\[
a(\eta)=\frac{a_m}{2}(1+\cos\eta),
\qquad
a_m=R_0^{3/2},
\]

\[
\sin\chi_0=R_0^{-1/2},
\]

\[
R_{\rm surf}
=a(\eta)\sin\chi_0
=\frac{R_0}{2}(1+\cos\eta).
\]

The mass relation closes:

\[
2M=a_m\sin^3\chi_0=1.
\]

The comoving proper time equals the exterior cycloidal geodesic time:

\[
\tau(\eta)
=
\frac{a_m}{2}(\eta+\sin\eta)
=
\frac{R_0^{3/2}}2(\eta+\sin\eta).
\]

For `R0=6`, the independent forward seam checks produced approximately

\[
\max|R_{\rm int}-R_{\rm ext}|<2\times10^{-15},
\]

\[
\max|\tau_{\rm int}-\tau_{\rm ext}|=0
\]

in Float64 arithmetic.

The surface crosses the horizon at

\[
\eta_H=\arccos\left(\frac2{R_0}-1\right).
\]

Since

\[
\cos(2\chi_0)=1-\frac2{R_0},
\]

one may simplify this to

\[
\eta_H=\pi-2\chi_0.
\]

The outgoing interior horizon ray has constant `eta-chi`, so its past endpoint at the centre is

\[
\eta_b=\eta_H-\chi_0=\pi-3\chi_0.
\]

This is the cleanest exact derivation of “the event horizon is born at the centre.”

## Junction-condition status correction

The file says “zero surface stress” and “Israel glue is seamless,” but the embedded kernel checks the areal radius, proper time, and conformal seam—not the full extrinsic-curvature equality.

The missing exact receipt is short. On the interior side,

\[
K^-_{\theta\theta}=R\cos\chi_0,
\qquad
K^-_{\tau\tau}=0.
\]

On the exterior geodesic boundary,

\[
K^+_{\theta\theta}
=R\sqrt{\dot R^2+f(R)}.
\]

For release from rest at `R0`,

\[
\dot R^2=\frac1R-\frac1{R_0},
\]

hence

\[
\dot R^2+f(R)
=1-\frac1{R_0}
=\cos^2\chi_0,
\]

and therefore

\[
K^+_{\theta\theta}=R\cos\chi_0=K^-_{\theta\theta}.
\]

The model’s zero-shell-stress claim is mathematically correct, but until these residuals are computed by the page its status should read:

```text
EXACT — standard OS matching theorem
COMPUTED — radius/proper-time seam
NOT YET KERNEL-CERTIFIED — full K_ab junction check
```

## Inverse-map conditioning issue

The forward map is good. The live inverse uses lookup tables after compactification. Near the initial and singular compactification edges, `atan` saturation and very small `F'` or `G'` amplify tiny table errors into large `(chi,eta)` errors.

In an independent grid test at `R0=6`, roundtrips near the late interior produced errors of order `5e-2` radians even while staying about ten percent away from the exact endpoint; errors become larger closer to the endpoint. This is a numerical conditioning issue, not a failure of the OS geometry.

Recommended receipt:

\[
\epsilon_{\rm inv}
=
\max\left(
|F(x_{\rm inv})-\widetilde U|,
|G(y_{\rm inv})-\widetilde V|
\right),
\]

plus a visible `ILL-CONDITIONED` status when `|F'|` or `|G'|` falls below a threshold.

---

# 3. STITCHIUM v0.1

## Fullerene and depth mathematics confirmed

For the tested golden shells, the constructor returned

\[
V=20T,
\qquad
E=30T,
\qquad
F=10T+2,
\]

\[
P=12,
\qquad
H=10(T-1),
\qquad
\chi=2,
\]

with degree three and two incident faces per edge.

The graph field

\[
d(v)=\min_{a\in A}\operatorname{dist}_G(v,a)
\]

is exactly the graph distance to the set of pentagon vertices. It is dimensionless and combinatorial, as the file states.

The live kernel confirms that `C20` and `C60` have depth zero everywhere. Within this selected golden sequence, `C140` is the first shell with a nontrivial depth field.

## Major cycle-count correction

The multi-source BFS begins with `S` distinct seed vertices. Therefore it creates a spanning forest with

\[
E_{\rm forest}=V-S.
\]

The number of edges not used for first discovery is

\[
C_{\rm non-tree}
=E-(V-S)
=E-V+S.
\]

That identity in the page is correct.

But the cycle rank of the original connected fullerene is

\[
\beta_1=E-V+1=F-1.
\]

Therefore

\[
C_{\rm non-tree}-\beta_1=S-1.
\]

The extra `S-1` edges are required to connect the initially separate root components before every later edge can independently increase cycle rank.

Concrete `C140` receipt from the embedded kernel:

\[
V=140,
\quad
E=210,
\quad
F=72,
\quad
S=60,
\]

\[
E_{\rm forest}=80,
\quad
C_{\rm non-tree}=130,
\quad
\beta_1=71,
\]

\[
130-71=59=S-1.
\]

So this sentence is false for the original graph:

```text
Each closure stitch closes exactly one independent cycle.
```

Correct replacement:

```text
The S-root BFS leaves E-V+S non-tree stitches.
Exactly E-V+1=F-1 independent cycles belong to the original fullerene;
S-1 additional non-tree stitches account for joining the root components.
```

A union-find pass can classify the edges exactly:

- `component join` when the endpoints were previously in different components;
- `cycle closure` when the endpoints were already in the same component.

## Anchor-count wording

There are twelve pentagonal anchor faces, but the BFS seeds all distinct vertices on those faces.

For the tested sequence:

- `C20`: `S=20` seed vertices;
- `C60` and later isolated-pentagon shells: `S=60` seed vertices.

Thus “twelve fronts leave the anchors” is visual metaphor, not the algorithm. The algorithm begins from `S` vertex roots grouped into twelve pentagonal faces.

## Secondary status correction

The graph constructor uses Float64 geometry, a `1e6` coordinate weld, and a floating convex hull. The integer invariants of the graph produced are exact after construction, but the statement “this is the Goldberg graph for arbitrary `(k,l)`” is computational rather than a formal all-input theorem. An exact combinatorial lattice indexer would remove that caveat.

The renderer’s radial-centroid front/back test should also be `DESIGN`, not `EXACT`, because the displayed dual face rings are not guaranteed to be perfectly planar and a radial centroid is not generally the exact plane normal.

---

# 4. THEA Light Matrix v1.2

## Exact algebra confirmed

The matrix

\[
\mathcal M=
\begin{pmatrix}
1&2&1&0\\
1&1&0&0\\
1&0&0&0\\
0&0&0&1
\end{pmatrix}
\]

has exact characteristic polynomial

\[
(\lambda-1)(\lambda+1)(\lambda^2-3\lambda+1)
\]

and exact spectrum

\[
\operatorname{spec}(\mathcal M)
=
\{\phi^2,1,-1,\phi^{-2}\}.
\]

The Fibonacci-selected triangulation sequence is correct:

\[
T_n=1,3,7,19,49,129,337,883,2311,\ldots
\]

and obeys

\[
T_{n+3}=2T_{n+2}+2T_{n+1}-T_n.
\]

The live `C60` graph has 60 vertices, 90 edges, and degree three.

The exact adjacency characteristic polynomial was independently recovered as

\[
\begin{aligned}
\chi_A(x)={}&(x-3)(x-1)^9(x+2)^4
(x^2-x-3)^5(x^2+x-4)^4\\
&\times(x^2+x-1)^5(x^2+3x+1)^3
(x^4-3x^3-2x^2+7x+1)^3.
\end{aligned}
\]

Hence

\[
\lambda_{\min}(A_{C60})=-\phi^2
\]

with multiplicity three.

The exact Fiedler radical also checks:

\[
\lambda_2(L_{C60})
=
\frac94-\frac{\sqrt2}{8}
\left(\sqrt{10}+2\sqrt{19-\sqrt5}\right)
\]

\[
=0.243401746139932\ldots
\]

with multiplicity three and quartic

\[
x^4-9x^3+25x^2-22x+4=0.
\]

The next bands also match:

\[
\frac{5-\sqrt{13}}2
=0.697224362268005\ldots
\quad(\times5),
\]

followed by the `3+4` split near `1.1797507493` and `1.4384471872`.

## Scope corrections

The 4x4 matrix advances the quadratic index state

\[
s=(k^2,k\ell,\ell^2,P),
\]

for the Fibonacci-selected family. It does not by itself encode every edge of every shell, and it does not govern all Goldberg fullerenes. Replace “governs the whole family” with “governs the index/count state of the golden-selected family.”

The map

\[
\phi\xrightarrow{\rm Euler}P=12
\]

is not causal mathematics. These are two independent facts:

\[
\phi=2\cos\frac\pi5
\]

comes from regular pentagonal metric geometry, while

\[
P=12
\]

comes from Euler topology for a trivalent pentagon/hexagon sphere.

Also, `C60` is not the first fullerene. `C20` is smaller. `C60` is the smallest isolated-pentagon fullerene and the second shell in the chosen Fibonacci sequence.

The label `T8/T7` currently computes `883/337`, which is `T7/T6` under the page’s zero-based indexing.

## The continuum constant: derivation valid, theorem status not yet valid

The local continuum calculation is mathematically sound:

\[
L\approx-\frac{3a^2}{4}\Delta,
\]

\[
A_{\rm site}\approx\frac{3\sqrt3}{4}a^2,
\]

\[
20T\,A_{\rm site}\approx4\pi R^2,
\]

so for the sphere’s `l=1` mode,

\[
T\lambda_2
\stackrel{\rm formal}{\longrightarrow}
\frac{2\pi}{5\sqrt3}
=0.725519745693687\ldots
\]

This is an excellent asymptotic prediction.

What is not supplied is a spectral-convergence theorem proving that these particular combinatorial Goldberg Laplacians, with this edge-length and radius normalization, converge strongly enough for that exact scaled limit to follow.

Independent sparse eigensolver receipt for `T=883`, `V=17660`:

\[
\lambda_2
=0.000820819134\ldots
\]

with eigenpair residual of order `1e-14`, hence

\[
T\lambda_2
=0.724783295614\ldots
\]

and

\[
T\lambda_2-\frac{2\pi}{5\sqrt3}
\approx-7.36\times10^{-4}.
\]

This is compatible with a slow limit but does not prove the stated constant. Section X should be labeled:

```text
DERIVED FORMAL ASYMPTOTIC + COMPUTED SUPPORT
```

rather than unconditional `EXACT`.

The deep Lanczos cards should report an eigenpair residual

\[
\|Lv-\lambda v\|_2
\]

and an iteration-depth change

\[
|\lambda_m-\lambda_{m/2}|
\]

before receiving a certificate.

---

# 5. HAWKIUM v0.1

## Analytic Schwarzschild core confirmed

In `G=c=hbar=k_B=1`, `M=1`, the page correctly uses

\[
r_s=2M,
\qquad
\kappa=\frac1{4M},
\qquad
T_H=\frac1{8\pi M},
\]

\[
A=16\pi M^2,
\qquad
S=\frac A4=4\pi M^2,
\]

\[
r_{\rm ph}=3M,
\qquad
b_c=3\sqrt3M,
\qquad
\sigma_{\rm geo}=27\pi M^2.
\]

The peeling fit independently returns

\[
\kappa_{\rm fit}=0.249999237897,
\]

with deviation about `7.62e-7` from `1/4`.

The Leaver continued-fraction kernel is excellent. It returns

\[
M\omega_{220}
=0.373671684418
-0.088962315689i,
\]

\[
M\omega_{221}
=0.346710996879
-0.273914875291i,
\]

stable against continued-fraction depths from roughly 80 to 800.

## Euclidean proper-distance bug

The theorem is correct:

\[
\beta=8\pi M
\]

is the unique period removing the Euclidean conical defect.

The current numerical `rhoOf` has an endpoint bug. After substituting

\[
r=2M+u^2,
\]

the transformed integrand has the finite endpoint limit

\[
\lim_{u\to0}
\frac{2u}{\sqrt{f(2M+u^2)}}
=2\sqrt{2M}.
\]

The code evaluates it as zero because both numerator and the clipped denominator are zero at `u=0`. Consequently the reported ratio behaves non-monotonically and catastrophically fails around `r-2M=1e-8`.

Use the exact proper distance instead:

\[
\rho(r)
=
\sqrt{r(r-2M)}
+2M\,\operatorname{arcosh}
\sqrt{\frac r{2M}}.
\]

Then, for `beta=8piM`,

\[
\frac{C}{2\pi\rho}
=0.99999999885\ldots
\]

already at `r-2M=1e-8`.

## First-law wording

The identity

\[
\frac{dS}{dM}=8\pi M=\frac1{T_H}
\]

is exact in the model.

The page’s central-difference receipt with `h=1e-6` differs from the target by approximately

\[
9.89\times10^{-10},
\]

not machine epsilon (`2.22e-16`). Replace “at machine epsilon” with “to about `1e-9` absolute error,” or compute the symbolic derivative exactly.

Also, `S=A/4` is exact within semiclassical Schwarzschild black-hole thermodynamics in Planck units, not an unconditional theorem about every quantum-gravity completion.

## Regge–Wheeler peak wording

The photon sphere is exactly at `r=3M`, but a finite-`l`, finite-spin Regge–Wheeler potential does not generally peak there.

For the page’s gravitational example,

\[
(l,s)=(2,2),
\]

an independent fine scan gives

\[
r_{\rm peak}\approx3.28081M.
\]

The peak approaches `3M` in the eikonal large-`l` limit. Replace “peaks at the photon sphere” with “the eikonal peak tends to the photon sphere; the finite-mode peak is nearby.”

## Isospectrality status

Axial/polar Schwarzschild isospectrality is an exact theorem, but comparing two finite-domain transmission calculations is a consistency check, not a proof. The measured differences also oscillate with cutoff before shrinking; the stated `1/r_*^2` law is not demonstrated by the two points.

Recommended status:

```text
EXACT — Chandrasekhar/Darboux isospectrality theorem
COMPUTED — finite-boundary transmission consistency check
```

## Greybody skip rule is quantitatively wrong

The code skips a mode when

```js
l >= 1 && w*w < 0.25*Vpeak && w < 0.35
```

and claims the omitted transmission is below `1e-7`.

Independent no-skip integrations found examples such as

\[
\Gamma_{l=1,s=0}(M\omega=0.1)
\approx4.85\times10^{-4},
\]

\[
\Gamma_{l=1,s=1}(M\omega=0.1)
\approx1.97\times10^{-3}.
\]

So the bound in the comment is false by several orders of magnitude.

Removing the skip changes the integrated powers approximately as follows:

| field | current skipped result | no-skip result | bias |
|---|---:|---:|---:|
| scalar, `112x8` | `7.39996e-5` | `7.43728e-5` | `-0.50%` |
| electromagnetic, `112x8` | `1.60313e-5` | `1.68109e-5` | `-4.64%` |
| gravitational axial, `112x8` | `1.88788e-6` | `1.91048e-6` | `-1.18%` |

The no-skip scalar result moves toward the standard benchmark scale near `7.44e-5`.

Delete the heuristic or replace it with a computed error bound. A skipped mode must report a nonzero upper bound and contribute that bound to the flux uncertainty.

## Numerical certification recommendation

The Wronskian/flux-conservation residual is valuable, but it is an internal consistency check, not an independent bound on the transmission error. Add a convergence grid over

\[
(h,r_*^{\max},l_{\max},n_\omega,\omega_{\min},\omega_{\max})
\]

and compare against an external benchmark only after the internal convergence table closes.

---

# Priority patch order

1. **STITCHIUM:** repair the independent-cycle claim and distinguish twelve anchor faces from `S` seed vertices.
2. **HAWKIUM:** remove the greybody skip; fix `rhoOf`; downgrade “machine epsilon”; correct finite-mode wall-peak wording.
3. **THEA:** change Section X from `EXACT` to `FORMAL ASYMPTOTIC + COMPUTED SUPPORT`; separate `phi` geometry from Euler topology; scope the matrix to the golden index family.
4. **PENROSIUM v0.2:** add the actual `K_ab` junction receipt and inverse-conditioning status.
5. **PENROSIUM v0.1:** repair the corner shorthand.

---

# Final status

The project is not collapsing under audit. The opposite happened: the strongest parts survived cleanly.

The exact survivors include:

\[
P=12,
\qquad
\chi=2,
\qquad
\operatorname{spec}(\mathcal M)=\{\phi^2,1,-1,\phi^{-2}\},
\]

\[
\lambda_{\min}(A_{C60})=-\phi^2,
\]

\[
K(2M)<\infty,
\qquad
T_H=\frac{\kappa}{2\pi},
\]

and the two independently reproduced Schwarzschild quasinormal modes.

The audit found four things that must not keep an `EXACT` badge in their current form:

- every STITCHIUM non-tree edge being an independent cycle;
- THEA’s exact scaled spectral-limit claim;
- HAWKIUM’s skipped-mode error assertion;
- PENROSIUM v0.2’s claim that the full Israel junction has already been kernel-certified.

That is a successful audit: the real structure remains, and the labels become sharper.
