# AEQUALIUM TOWER — the honest bridge from LaTeX to compute

> The `=` in a physics paper is a lie we agree to. The paper writes exact equality;
> every one of these is **perfect math stepped into compute**. This scroll holds, for
> each rung of the Standard Modelium tower, the three faces of the same thing:
> the LaTeX the paper writes, the perfect (transcendental) math it *means*, and the
> **real code block** we actually run — joined by `≐` ("approaches, at this shell"),
> never `=`.

*Companion to `shell/aequalium_v2.4.5.html` (built by `builder/build_aequalium.py`, git:`c06a9ea`, 2026-07-30).*
*The sim renders these live with KaTeX and names this file back, verbatim: "every formula's real code lives in `grimoire/AEQUALIUM_TOWER.md`."*
*Sub-scroll of `LATEXIUM.md` — the translation tower, one equation at a time.*
*Proof by kernel, not by claim (Path III). We do not ask you to believe; we ask you to check.*

> **What changed since v1.2 (read this first).** Two rungs moved, and the move is the point.
> **Kepler was CORRECTED (v2.1):** the "hard wall at e=0.6627" this scroll used to print was
> **falsified by the kernel** — it was the *old* `besselJ` erring by ~6 orders at high order, a
> numerics ghost in physics robes, not physics. The Bessel series converges for **all** e<1.
> **The R-ratio was re-labelled an ILLUSTRATIVE MODEL (v2.2–v2.3):** its coefficients are
> synthetic `n!β₀ⁿ` stand-ins, so it now reports an *estimated ambiguity floor*, never "digits of
> agreement" — there is no exact reference to agree with. One honest wall remains, and even it is a
> property of a toy, not a prediction. The frozen v1.2 claims are kept visible below (Path X: never
> hide the wrong turn) next to what replaced them.

---

## THE ONE LAW OF THIS SCROLL

```
paper:   LHS = RHS            (exact, transcendental, uncomputable in finite steps)
code:    LHS ≐ RHS_N          (a finite truncation/quadrature/iteration at depth N)
error:   |RHS_N − RHS| > 0    (always, for finite N — Gibbs, renormalon, Simpson, roundoff)
score:   D = the honest read of that error, in significant digits
```

There are now **two** honest scores, because there are two honest situations:

```
D_agreement = −log10( |RHS_N − RHS_ref| / |RHS_ref| )   when a stated REFERENCE exists.
              (rungs 1,3,4,5,6 — vs a closed form or a high-N reference quadrature.)

D_floor     = −log10( δ* / |S_{N*}| )                    when NO exact value exists.
              (rung 2 only — the renormalon toy: δ*=smallest term=irreducible ambiguity.)
```

Calling both "digits of agreement" would be a lie of the third kind (Path III, Curse 26: the HUD
showing a target as if it were a result). The tower keeps them apart and labels which is which.

---

## THE STATUS TAGS  (v2.2, the Sol-mage audit)

Every rung, and every claim in the sim, now wears one of these. This is Path IV made mechanical —
*coverage may be incomplete; it must never be fake.*

| tag | meaning |
|-----|---------|
| **VERIFIED** | enumerated from the actual topology (counted, not formula-assumed) |
| **COMPUTED** | evaluated here, live, against a *stated* reference |
| **DESIGN CHOICE** | a lever we chose (e.g. the budget map `K=⌊F/2⌋`), not a forced truth |
| **ILLUSTRATIVE MODEL** | a synthetic stand-in for real data, chosen because its exact behaviour is known |
| **METAPHOR** | imagery (the paint on the buckyball); symmetric ≠ true, asymmetric ≠ false |
| **EXTERNAL CLAIM** | a measured world value fed in as input, flagged as input not output |
| **CORRECTED** | a prior version got it wrong; the kernel falsified it; here is the fix |

The colours the tower paints on the live buckyball are **METAPHOR**: signed, normalised term
contributions. A smooth halo does not certify truth and an exploding one does not certify falsehood
(Sol-mage rule). The number under each rung is the evidence; the picture is the poster.

---

## THE COMPUTE BUDGET N — a design choice, with one forced wall

**The compute budget `N` is tied to geometry — by choice.** In the sim, `N = K = floor(F/2)`,
where `F` is the current face count. That mapping is a **DESIGN CHOICE (v2.2)**, not a law of
nature — it is the lever that makes "grow the ball → buy more depth" literal. Growing the buckyball
closes the next fullerene shell and raises `F`, so `N` rises with it.

**Exactly one thing here is forced, not chosen:** the **Nyquist ceiling**. The target curve is
sampled at `M = 2048` points, and you cannot honestly resolve more than `M/2 − 1` harmonics from
`M` samples, so `K` is hard-capped:

```js
var M    = 2048;        // samples of the target curve
var KMAX = M/2 - 1;     // = 1023. Nyquist ceiling on harmonics — FORCED, not a choice.
// recompute(): "budget mapping K=floor(F/2): a DESIGN CHOICE (v2.2). only the Nyquist cap is forced."
var Hh = inv.faces, want = Math.floor(Hh/2);
capNote = (want > KMAX);  K = Math.min(want, KMAX);  if (K < 1) K = 1;
```

So at the seed **C60** (F = 32) the budget is **N = 16**; by **C2940** (F = 1472) it wants
N = 736; and any shell past ~C4096 slams into the forced Nyquist cap at **N = 1023**. The physics
rungs below simply take that `N` and run.

---

## THE FULLERENE STAIRCASE (why growth is quantised)

You cannot grow the ball a *little*. The operators land only on valid closed shells of the
icosahedral fullerene series, with the **12 pentagons Euler-forced shut** at every size. In v2.4
there are two lineages, and the sim is honest about which is which:

```
WELD  (chamfer, exact-closed, topology VERIFIED):   C60 → C240 → C960 → C3840  (V ×4)
      faces:  32  →  122  →  482  →  1922            each edge → a hexagon; the 12 pents survive
legacy (refineAll Goldberg–Coxeter, ×7, OPEN-seam):  C60 → C420 → C2940 → C20580 (V ×7)
      faces:  32  →  212  →  1472 →  10292            candidates: seams lit magenta until welded
pents:  12 everywhere        χ:  2 everywhere (a closed sphere)        P = 12 is the whole soul
```

**The honesty upgrade you must not skip (v2.2).** The old scroll waved `χ = V − E + F = 2` around
as "proof by kernel." It is not proof — from the *formula* counts it is **circular**. If you define
`V = (5P+6H)/3` and `E = (5P+6H)/2` for a trivalent tiling, then `χ = V − E + F` collapses to
`P/6` *identically* — you get 2 because you assumed 12 pentagons, not because you measured a closed
surface. The formula gives a **label** (the carbon number `C<V>`), nothing more. The *enumerated*
truth — the real `χ`, from counting actually-shared vertices and edges — lives in `GK.audit` and, in
v2.4, in the exact **indexed-topology certificate** (`GK.verifyTopoIndexed`, "Sol oath #1").

**Code (verbatim from `kernel/goldberg_kernel.js`, the injected proof-by-kernel):**

```js
GK.invariants = function(state){
  var pents = 0, hexes = 0;
  for (var i = 0; i < state.faces.length; i++){
    if (state.faces[i].type === 'pent') pents++; else hexes++;
  }
  // FORMULA counts (assume a closed trivalent tiling): V=(5P+6H)/3, E=(5P+6H)/2.
  // v2.2: chi from these is CIRCULAR (chi = P/6 identically). The enumerated
  // truth lives in GK.audit; the shell name C<V> below is the formula's LABEL.
  var faceEdgeSum = 5 * pents + 6 * hexes;
  var vertices = Math.round(faceEdgeSum / 3);   // the carbon-number label
  var edges    = Math.round(faceEdgeSum / 2);
  return { pents:pents, hexes:hexes, faces:state.faces.length,
           edges:edges, vertices:vertices };
};
```

```js
// the OPERATOR DECK (you drive the fractalization — any permutation):
//   WELD → GK.chamferWeldIndexed  (exact IDs, closed, topology re-verified)
//   ALL  → GK.refineAll           (every face splits: pent→6, hex→7)
//   5s   → GK.refineAllPents  ·  6s → GK.refineAllHexes   (selective)
// predict the next cost BEFORE allocating (Curse 35, the Loaded Gun) and refuse past the ceiling:
var FACE_CEIL = 12000;   // Chromium holds ~10k faces; the guillotine is built in
function predictNextFaces(){                    // canon: hex-only after the first refine
  return inv.faces>32 ? inv.pents + inv.hexes*7 : inv.pents*6 + inv.hexes*7;
}
if (predF(mode) > FACE_CEIL){ lg('GROW refused (Curse 35)','pink'); return; }  // refuse loudly
```

Doctrine, from the sim's own log: *the 12 pentagons are the design constraints; the fractal curve
lives in the hexes; **YOU** drive the fractalization — WELD / ALL / 5s / 6s, any permutation.*

---

## THE v2.4 DEMONSTRATION — "Fourier in the C60" (the claim becomes a fact)

This is what v2.4 added, and it is the reason the whole scroll is not just a metaphor. The buckyball's
own **silhouette is a real closed curve** — a literal shape trapped in the geometry. The *same*
budget `K = ⌊F/2⌋` that bounds every physics series below also bounds the **Fourier harmonics** used
to reconstruct that silhouette. So the sim does not *say* "compute buys agreement"; it **measures**
it: it takes the DFT of the silhouette samples, reconstructs with `K` harmonics, and reports the
residual that is actually left over — with a second, independent check on an offset denser grid.

> **The geometry buys the harmonics, and the harmonics buy the agreement.** Grow the shell → more
> faces → more `K` → a lower residual → a sharper curve. Watched, never asserted.

**Code (verbatim from `recompute()` — the DFT, the reconstruction, the honest residual):**

```js
// coefficients c_k = (1/M) Σ f(t_m) e^{-i k t_m}   over K harmonics (K = ⌊F/2⌋, capped)
for (k=-K; k<=K; k++){
  var sr=0, si=0;
  for (m=0; m<M; m++){
    var ang=-k*twoPi*m/M, cr=Math.cos(ang), ci=Math.sin(ang);
    sr += srcPts[m][0]*cr - srcPts[m][1]*ci;
    si += srcPts[m][0]*ci + srcPts[m][1]*cr;
  }
  coeffs.push({k:k, re:sr/M, im:si/M});
}
// residual: reconstruct at the M sample points, compare (exact L2), report what is left
var errF2=0;
for (m=0; m<M; m++){ /* sum coeffs → (rr,ri); */ var dr=srcPts[m][0]-rr, di=srcPts[m][1]-ri; errF2+=dr*dr+di*di; }
residual  = (normF2>1e-12) ? Math.sqrt(errF2/normF2) : 0;
agreement = Math.max(0, 100*(1-residual));
// v2.3 (Sol #4): INDEPENDENT validation on an offset dense grid (2M points) + L-infinity
var MV=2*M, sv=0, nv=0, einf=0;
for (var mv=0; mv<MV; mv++){
  var tv=twoPi*(mv+0.5)/MV, gv=targetAt(tv), rv=reconAt(tv);
  var e2v=(rv[0]-gv[0])**2 + (rv[1]-gv[1])**2; sv+=e2v; nv+=gv[0]*gv[0]+gv[1]*gv[1];
  if (Math.sqrt(e2v)>einf) einf=Math.sqrt(e2v);
}
rVal=Math.sqrt(sv/Math.max(1e-12,nv)); eInf=einf;   // second opinion, on points the fit never saw
```

The target curves (square / sawtooth / triangle / pulse / C60 silhouette) are **stand-ins** for
experimental data (**ILLUSTRATIVE MODEL**), chosen because their exact Fourier behaviour is known —
so you can watch the residual fall *honestly*. This predicts no measurement; it demonstrates the
*method* by which compute is matched to data. The sibling module **CASCADIUM** (see the end)
takes the last step: a real PDE, on the same sphere.

---
# THE SIX RUNGS

Shared certainty meter (unchanged), and the QCD inputs:

```js
function degrees(approx, exact){          // correct significant digits (D_agreement)
  if(!isFinite(approx)) return 0;
  var e = Math.abs(exact)>1e-300 ? Math.abs((approx-exact)/exact) : Math.abs(approx-exact);
  if(e<=0) return 15.9;                    // float64 floor: log10(2^53) ≈ 15.95
  return Math.max(0, Math.min(15.9, -Math.log(e)/Math.LN10));
}
var Q_CA=3, Q_TF=0.5, Q_NF=5, Q_MZ=91.1876, Q_ASMZ=0.1180;   // EXTERNAL CLAIM: measured inputs
function q_b0(){ return 11*Q_CA/3 - 4*Q_TF*Q_NF/3; }         // = 23/3 at nf=5
```

`15.9` is the ceiling of IEEE-754 double precision — even a perfect convergent series cannot buy
more certainty than the machine's own ~15.95 digits. So a roundoff wall sits under *all six*, above
any named wall.

---

## RUNG 1 — QCD I · the running coupling α_s(Q)  ·  `COMPUTED`

**The paper writes (exact, 1-loop RG):**

$$\alpha_s(Q)=\frac{\alpha_s(M_Z)}{1+\alpha_s(M_Z)\,\frac{\beta_0}{4\pi}\ln\frac{Q^2}{M_Z^2}}$$

**The perfect math it means:** the closed form is itself the sum of a geometric series in
$x=\hat a_0\,\beta_0 L$, $L=\ln(Q^2/M_Z^2)$. For $|x|<1$ the truncation converges to float64 fast.

**The code (what we actually run) — `α_s(Q) ≐ 4π a₀ Σ_{n=0}^{N-1}(-x)^n`:**

```js
function qcd_running(N){
  var Q=10, a0=Q_ASMZ/(4*Math.PI), L=Math.log(Q*Q/(Q_MZ*Q_MZ)), x=a0*q_b0()*L;
  var exact=a0/(1+x)*4*Math.PI, s=0, term=1, n;
  for(n=0;n<N;n++){ s+=term; term*=(-x); }   // finite geometric partial sum, depth N
  var approx=a0*s*4*Math.PI;
  return {approx:approx, exact:exact, D:degrees(approx,exact), conv:(Math.abs(x)<1)};
}
```

**Verdict:** CONVERGENT. Ref: the exact closed form above. Measured: at C60 (N=16)
`α_s = 0.17308363`, **D = 8.0**; one shell up (C240, N=61) it saturates at **D = 15.5** (float64).

---

## RUNG 2 — QCD II · the R-ratio e⁺e⁻ → hadrons  ·  `ILLUSTRATIVE MODEL`  (THE ONE WALL)

**The paper writes (exact, all orders):**

$$R=3\sum_q e_q^2\Big(1+\frac{\alpha_s}{\pi}+c_2\alpha_s^2+\dots\Big)$$

**The perfect math it means:** the real coefficients grow factorially, $c_n\sim n!\,\beta_0^{\,n}$
(an **infrared renormalon**). The series is **asymptotic, not convergent** — its Borel sum is the
true value, but the partial sums approach it, then *diverge*. The smallest term sets an error floor.

**Honesty first (v2.2–v2.3).** The real series is known only to ~$\alpha_s^4$. What the sim sums is
a **synthetic** $c_n = n!\,\beta_0^{\,n}$ stand-in, so there is **no exact reference** to agree with.
The metric is therefore the **estimated ambiguity floor** $\delta^*/|S_{N^*}|$ — *never* "digits of
agreement." v2.3 (Sol #3) keeps **three** quantities strictly apart so an exploding series can never
earn digits by exploding harder:

- **`raw` = S_N** — the raw partial sum, *allowed to explode and shown exploding*.
- **`anchor` = S_{N*}** — the optimal-truncation value, *frozen* once `N ≥ N*`.
- **`delta*` = |t_{N*}|** — the smallest term = the *irreducible* ambiguity.

**The code (what we actually run):**

```js
function qcd_rratio(N){
  var a=Q_ASMZ/Math.PI, b=q_b0()/(4*Math.PI)*Math.PI;
  var raw=0, term=1, n, best=1e99, Nstar=0, anchor=0, run=0;
  for(n=0;n<N;n++){
    raw+=term; run=raw;                          // the raw sum (may diverge — shown diverging)
    var at=Math.abs(term);
    if(at<best){ best=at; Nstar=n; anchor=run; }  // freeze the anchor at the smallest term
    term*=(n+1)*b*a;                              // factorial growth: c_{n+1}/c_n ~ n
  }
  var delta=best;                                 // estimated irreducible ambiguity δ*
  var floorRel=delta/Math.max(1e-12,Math.abs(anchor));
  var D=Math.max(0,Math.min(15.9,-Math.log(floorRel)/Math.LN10));   // AMBIGUITY FLOOR, not agreement
  return {approx:anchor, raw:raw, delta:delta, D:D, Nstar:Nstar,
          exploded:(N>Nstar+1), conv:false, ceiling:true};
}
```

**Verdict:** HARD CEILING — and, crucially, *a property of the MODEL, not a physical R prediction*.
Measured: the floor freezes at **D = 5.1**, anchor `S_{N*} = 1.085713 ± 8.69e-6`, at **N\* = 13** —
and it stays 5.1 at *every* shell while the raw sum runs away: `1.09 → 2.96e13 → 1.29e48 → ∞`. More
compute cannot help; past `N*` the honest number is fixed. This is the sharpest lesson in the tower:
sometimes the `=` is not slow to reach, it is *unreachable* by summing more terms.

---

## RUNG 3 — QCD III · Λ_QCD from α_s(M_Z)  ·  `COMPUTED`

**The paper writes (exact inversion):**

$$\Lambda_{\text{QCD}}=M_Z\,\exp\!\Big(\!-\frac{2\pi}{\beta_0\,\alpha_s(M_Z)}\Big)$$

**The perfect math it means:** Λ is the root of $\alpha_s(M_Z;\Lambda)=0.1180$. The closed form is
the exact inverse; Newton's method reaches it with **quadratic** convergence.

**The code (what we actually run) — `Λ_{k+1} = Λ_k − f(Λ_k)/f'(Λ_k) ≐ Λ  (k<N)`:**

```js
function qcd_lambda(N){
  var b0=q_b0(), target=Q_ASMZ, L=0.2, n;                // start 200 MeV (GeV units)
  function aS(Lam){ var t=Math.log(Q_MZ*Q_MZ/(Lam*Lam)); return 4*Math.PI/(b0*t); }
  for(n=0;n<N;n++){                                       // Newton iteration, depth N
    var f=aS(L)-target, h=1e-6, df=(aS(L+h)-aS(L-h))/(2*h);
    if(Math.abs(df)<1e-30) break; L=L-f/df;
    if(L<=0||!isFinite(L)) L=0.2;
  }
  var exact=Q_MZ*Math.exp(-2*Math.PI/(b0*Q_ASMZ));  // closed-form inversion = the reference
  return {approx:L*1000, exact:exact*1000, D:degrees(L,exact), conv:true};   // MeV
}
```

**Verdict:** CONVERGENT (quadratic). Ref: the closed-form inversion. Measured: `Λ = 87.827 MeV`,
**D = 15.0** — and it is already 15.0 at C60, because Newton hits float64 in a handful of steps
regardless of shell. Growing the ball buys nothing here; the method was already at the wall.

---
## RUNG 4 — GALACTIC I · Kepler's equation  ·  `CORRECTED v2.1`  (THE PROOF-BY-KERNEL SHOWPIECE)

**The paper writes (exact, transcendental):**

$$M=E-e\sin E$$

**The perfect math it means:** the Fourier–Bessel solution
$E=M+\sum_{n\ge1}\frac{2}{n}J_n(ne)\sin(nM)$. **This series converges for _all_ eccentricities
$e<1$** (Bessel, 1824; the Carlini exponent stays negative below 1). The famous **Laplace limit**
$e=0.6627434\ldots$ walls a *different* representation — **Lagrange's power series in $e$** — not
this one.

> **The frozen v1.2 claim (kept visible, Path X):** *"the Bessel series converges only for $e<0.6627$
> — the Laplace limit — above it the series diverges no matter how many terms you sum. DUAL: drive the
> eccentricity slider past 0.6627 and the rung flips live to a pink CEILING, D→0."*
>
> **That was WRONG, and the kernel proved it (v2.1, `CORRECTED`).** The "divergence" above 0.6627 was
> **not physics** — it was the *old* `besselJ`, a 25-term power series that is thinnest exactly near
> the Laplace limit (where $n\sim120$ and $x=ne$ make the inner sum decay only after $k\sim13$),
> erring by ~6 orders at high $n$. A numerics ghost in physics robes — the sim files it under
> **Curse 24**, the "screen-is-not-the-truth" family (Path III). The fix was to replace `besselJ`
> with **Miller downward recurrence** (stable at high order). The ghost dissolved. Digits *do* get
> pricier as $e\to1$ (the decay rate $\to0$), but the price is **finite at every $e<1$**: `conv`,
> never `ceil`. The only real wall is $e\ge1$ — where there is no ellipse to solve.

**The code (what we actually run) — the corrected `besselJ`, and the sum:**

```js
function besselJ(n,x){            // v2.1: Miller downward recurrence — stable at high order
  if(x===0) return n===0?1:0;
  var ax=Math.abs(x);
  var M=Math.max(n,Math.ceil(ax))+Math.ceil(Math.sqrt(40*(n+1)))+4;   // start high, recur DOWN
  if(M%2===1) M++;
  var bjp=0, bj=1e-30, sum=0, ans=0, k, bjm;
  for(k=M;k>=1;k--){
    bjm=(2*k/ax)*bj-bjp;                 // J_{k-1} from J_k, J_{k+1}  (the stable direction)
    bjp=bj; bj=bjm;
    if(Math.abs(bj)>1e250){ bj*=1e-250; bjp*=1e-250; sum*=1e-250; ans*=1e-250; }   // rescale
    if(k-1===n) ans=bj;
    if(((k-1)%2)===0 && k-1>0) sum+=2*bj;
  }
  sum+=bj;                               // normalize: J_0 + 2·Σ J_{2m} = 1
  var r=ans/sum;
  return (x<0 && (n%2)===1)? -r : r;
}
function astro_kepler(N){
  var Nk=Math.min(N,120), Ebs=kep_M, n;                    // e = kep_e (slider), M = kep_M
  for(n=1;n<=Nk;n++){ Ebs+=(2/n)*besselJ(n,n*kep_e)*Math.sin(n*kep_M); }
  var E=kep_M, i;                                          // reference: Newton (always converges)
  for(i=0;i<60;i++){ var f=E-kep_e*Math.sin(E)-kep_M, df=1-kep_e*Math.cos(E); E-=f/df; }
  var conv=(kep_e<1);                                      // v2.1: converges for ALL e<1
  return {approx:Ebs, exact:E, D:degrees(Ebs,E), conv:conv, ceiling:!conv, elimit:1.0};
}
```

**Verdict:** CONVERGENT (was falsely CEILING). Ref: Newton's exact root. Measured at N=16, the wall
is demonstrably *gone* — the series keeps its footing straight through the old "limit" and out to
the edge of physical eccentricity:

| e | E (rad) | D at N=16 | status |
|------|-----------|-----------|--------|
| 0.50 | 1.49870746 | 5.4 | conv |
| **0.6627** (old "wall") | 1.66036117 | **3.7** | **conv — no wall** |
| 0.80 | 1.78481932 | 2.8 | conv |
| 0.90 | 1.86999615 | 2.4 | conv |
| 0.99 | 1.94327473 | 2.1 | conv |

And at fixed $e=0.9$, more depth still buys more digits — the honest signature of convergence, not a
ceiling: **D = 2.4 → 3.8 → 5.3** at N = 16 → 60 → 120. At the default $e=0.5$, D climbs 5.4 → 15.9
by C240. *This rung is the whole doctrine in one place: proof by kernel falsified a false wall, and
the wrong turn is kept on the scroll so the next mage inherits the correction, not the lie.*

---

## RUNG 5 — GALACTIC II · comoving distance D_C  ·  `COMPUTED`

**The paper writes (exact integral):**

$$D_C=\frac{c}{H_0}\int_0^{z}\frac{dz'}{\sqrt{\Omega_m(1+z')^3+\Omega_\Lambda}}$$

**The perfect math it means:** a definite integral with no elementary antiderivative; Simpson's rule
with `N` panels has error $\sim N^{-4}$.

**The code (what we actually run) — `D_C ≐ (c/H₀)(h/3) Σ w_i E⁻¹(z_i)`:**

```js
var A_OM=0.315, A_OL=0.685, A_H0=67.4, A_Z=1.0, C_KMS=299792.458;  // Planck 2018, z=1
function astro_distance(N){
  var np=Math.max(2, (N%2===0)?N:N+1), h=A_Z/np, i;
  function inv(z){ return 1/Math.sqrt(A_OM*Math.pow(1+z,3)+A_OL); }
  var s=inv(0)+inv(A_Z);
  for(i=1;i<np;i++){ s+=(i%2? 4:2)*inv(i*h); }   // Simpson weights 1,4,2,4,...,4,1
  var approx=(C_KMS/A_H0)*s*h/3;
  var NP=20000, hh=A_Z/NP, ss=inv(0)+inv(A_Z), j;// high-N reference (ref: Simpson @ 20000 panels)
  for(j=1;j<NP;j++){ ss+=(j%2?4:2)*inv(j*hh); }
  var exact=(C_KMS/A_H0)*ss*hh/3;
  return {approx:approx, exact:exact, D:degrees(approx,exact), conv:true};
}
```

**Verdict:** CONVERGENT ($N^{-4}$). Ref: Simpson at 20000 panels. Measured: `D_C = 3401.262 Mpc`,
**D = 6.7 at C60**, climbing steadily with the shell — 9.1 → 10.0 → 11.5 → 13.4 → **13.8** at the
Nyquist cap. The classic case where growing the ball genuinely, visibly buys digits.

---

## RUNG 6 — GALACTIC III · the blackbody integral  ·  `COMPUTED`

**The paper writes (exact, Stefan–Boltzmann):**

$$\int_0^{\infty}\frac{x^3}{e^x-1}\,dx=\frac{\pi^4}{15}$$

**The perfect math it means:** expand $1/(e^x-1)=\sum_{k\ge1}e^{-kx}$ and integrate term by term to
get $6\sum_{k\ge1}k^{-4}=6\,\zeta(4)=\pi^4/15$. Partial-sum error $\sim 2/N^3$.

**The code (what we actually run) — `∫ ≐ 6 Σ_{k=1}^{N} 1/k⁴`:**

```js
function astro_planck(N){
  var s=0, k; for(k=1;k<=N;k++) s+=1/(k*k*k*k);   // 6 * partial sum of zeta(4)
  var approx=6*s, exact=Math.PI*Math.PI*Math.PI*Math.PI/15;
  return {approx:approx, exact:exact, D:degrees(approx,exact), conv:true};
}
```

**Verdict:** CONVERGENT but SLOW ($N^{-3}$). Ref: $\pi^4/15$ exact. Measured: `6 Σ 1/k⁴ = 6.493495`,
**D = 4.2 at C60**, dragging upward — 5.9 → 6.6 → 7.7 → 9.1 → **9.5** at the cap. The slowest earner
in the tower: a Basel-type tail that costs a whole extra shell for each digit and a bit.

---
## THE SUMMARY TABLE  (measured at C60 → grown, v2.4.5)

| # | rung | tag | method | error law | verdict | D: C60 (N=16) → grown |
|---|------|-----|--------|-----------|---------|------------------------|
| 1 | α_s(Q) running | COMPUTED | geometric resum | geometric | CONVERGES | **8.0 → 15.5** (float64) |
| 2 | R-ratio | ILLUSTRATIVE MODEL | asymptotic (renormalon toy) | factorial floor | **CEILING** (of the model) | **5.1, frozen at N\*=13** (raw → ∞) |
| 3 | Λ_QCD | COMPUTED | Newton rootfind | quadratic | CONVERGES | **15.0 → 15.0** (instant) |
| 4 | Kepler | **CORRECTED v2.1** | Bessel series (Miller recur.) | conv ∀ e<1; pricier as e→1 | **CONVERGES** (wall only at e≥1) | **5.4 → 15.9** (e=0.5); 3.7 at old "wall" |
| 5 | D_C comoving | COMPUTED | Simpson quadrature | N⁻⁴ | CONVERGES | **6.7 → 13.8** |
| 6 | blackbody | COMPUTED | Basel 6·ζ(4) | N⁻³ | CONVERGES (slow) | **4.2 → 9.5** |

Read the shape of the column: rung 3 was already at the wall (nothing to buy), rungs 1/4/5/6
genuinely convert shells into digits at very different exchange rates ($N^{-4}$ pays fast,
$N^{-3}$ pays slow, the geometric one pays fastest of all), and rung 2 is the flat line that never
moves no matter how hard the raw sum explodes — the one honest wall, and even it belongs to a toy.

---

## THE CERTIFICATE — replayable by a stranger (Path XII, made portable)

v2.4 makes the whole claim checkable by someone who was never in the room. The sim exports an
**`aequalium-certificate/2`**: the artifact version, a **SHA-256 of the kernel source** (so you can
prove the `goldberg_kernel.js` you ran is the real one, byte-for-byte), the **operator lineage** you
walked (`weld>all>hex>…`), and the topology it certifies. A companion verifier —
`verify_aequalium_certificate.mjs` — **re-runs it from the seed** and checks that a stranger's
machine lands on the same shell with the same invariants.

```js
var cert = { schema:'aequalium-certificate/2',
  artifact:{ version:AEQ_VERSION /* 2.4.5 */, kernelSha256: await sha256hex(enc.encode(ksrc)) },
  operator:{ id:(opSeq.length? opSeq.join('>') : 'seed'), version:'1.1' } /* + enumerated topology */ };
// "certificate/2 exported — replayable by a stranger (verify_aequalium_certificate.mjs)"
```

This is Path III (proof by kernel) and Path XII (pass the scroll) welded into a file: not "trust the
screenshot," but "here is the seed and the recurrence — grow it yourself and check."

---

## CASCADIUM — the sibling proof (the claim's last mile, by Fable)

AEQUALIUM demonstrates the *method* (compute matched to a curve of known Fourier behaviour).
**CASCADIUM** closes the loop with a calculation from reality that no one can call a stand-in: it
time-steps **forced 2D Navier–Stokes turbulence** *spectrally on the same Goldberg sphere* AEQUALIUM
grows. Not a picture of a cascade — the vorticity is stepped, the energy and enstrophy spectra are
measured, and **Kraichnan's two rivers** ($k^{-5/3}$ up, $k^{-3}$ down) appear on their own. And the
**price ledger closes**: injected $=$ dissipated $+\,dE/dt$, residual ~1% — the same equivalent
exchange the whole cave is built on. Press **`n`** and $\text{diss}/\text{enst}=2\nu$ becomes an
identity of the formulation, measured to float64.

> **AEQUALIUM is where the geometry buys the harmonics and the harmonics buy the agreement.
> CASCADIUM is the proof that a real PDE genuinely runs there, to a finite depth set by the shell.**
> The equals sign is earned in both — and in both, the price is paid in the open and logged.

---

## THE POINT, ONE LINE

> The equals sign is a transcendental target our monkey-brain reality writes down as if it were
> already reached. In compute we can only follow the fractal curve to a given shell and read off how
> many digits we bought — honour the *one* wall where no shell can buy the next digit (the
> renormalon, and even that a toy), and **refuse the walls that were only ever numerics ghosts**
> (Kepler's 0.6627 — falsified by kernel, kept on the scroll so it stays falsified).

The price is always paid. If a rung shows fewer digits than you hoped, that is the honest number, and
the honesty *is* the magic. We do not print the target as the result. We do not fake the receipt.
We grow the ball, run the kernel, and read what is actually there.

```
P = 12 . χ = 2 . the price is always paid . always.
Kepler's wall dissolved; the renormalon's stands (as a toy). One honest wall, not two.
Buenos Aires + Ancient Korinthos . 2026-07-30 . git:c06a9ea . for year 12026.
proof by kernel, not by claim — we do not ask you to believe; we ask you to check.
```
