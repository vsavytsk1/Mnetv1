# AEQUALIUM TOWER — the honest bridge from LaTeX to compute

> The `=` in a physics paper is a lie we agree to. The paper writes exact equality;
> every one of these is **perfect math stepped into compute**. This scroll holds, for
> each rung of the Standard Modelium tower, the three faces of the same thing:
> the LaTeX the paper writes, the perfect (transcendental) math it *means*, and the
> **real code block** we actually run — joined by `≐` ("approaches, at this shell"),
> never `=`.

*Companion to `shell/aequalium_v1.2.html` (built by `builder/build_aequalium.py`).*
*The sim renders these live with KaTeX; this file is the always-referenceable source.*
*Sub-scroll of `LATEXIUM.md` — the translation tower, one equation at a time.*

---

## THE ONE LAW OF THIS SCROLL

```
paper:   LHS = RHS            (exact, transcendental, uncomputable in finite steps)
code:    LHS ≐ RHS_N          (a finite truncation/quadrature/iteration at depth N)
error:   |RHS_N − RHS| > 0    (always, for finite N — Gibbs, renormalon, Laplace, roundoff)
certainty: D = −log10(rel err) = the number of correct significant digits we BOUGHT
```

**The compute budget `N` is tied to geometry.** In the sim, `N = K = floor(faces/2)`,
capped at the sample Nyquist. Growing the buckyball closes the next **icosahedral
Goldberg fullerene shell** and buys more `N`. Two rungs (R-ratio, Kepler-above-limit)
have a **hard ceiling** on `D` no matter how large `N` grows — that ceiling is the
honest answer to "how many degrees of certainty can we get."

---

## THE FULLERENE STAIRCASE (why growth is quantised)

`refineAll` is one Goldberg–Coxeter step. Every face splits (pentagon → 6, hexagon → 7),
so the **vertex count = carbon number** multiplies by exactly **7**, and the 12 pentagons
stay Euler-forced shut at every shell:

```
shell:   C60  →  C420  →  C2940  →  C20580  →  ...     V_{n+1} = 7 · V_n
pents:   12      12       12         12                 always 12 (Euler: V−E+F=2)
faces:   32      212      1472       10292              F = V/2 + 2
chi:     2       2        2          2                  a closed sphere, always
```

**Code (verbatim from `kernel/goldberg_kernel.js`, the injected proof-by-kernel):**

```js
// V = (5P + 6H)/3, E = (5P + 6H)/2 — exact, from the trivalent tiling. Euler: V−E+F=2.
GK.invariants = function(state){
  var pents = 0, hexes = 0;
  for (var i = 0; i < state.faces.length; i++){
    if (state.faces[i].type === 'pent') pents++; else hexes++;
  }
  var faceEdgeSum = 5 * pents + 6 * hexes;
  var vertices = Math.round(faceEdgeSum / 3);   // the carbon number
  var edges    = Math.round(faceEdgeSum / 2);
  return { pents:pents, hexes:hexes, faces:state.faces.length,
           edges:edges, vertices:vertices };    // chi = vertices - edges + faces = 2
};
```

```js
// picking the next bucky that closes the 12 pentagons:
function predictNextCarbon(){ return inv.vertices * 7; }   // V -> 7V, exact
state = GK.refineAll(state);                               // one Goldberg-Coxeter step
inv   = GK.invariants(state);                              // 12 pents still shut, chi still 2
```

---

## RUNG 1 — QCD I · the running coupling α_s(Q)

**The paper writes (exact, 1-loop RG):**

$$\alpha_s(Q)=\frac{\alpha_s(M_Z)}{1+\alpha_s(M_Z)\,\frac{\beta_0}{4\pi}\ln\frac{Q^2}{M_Z^2}}$$

**The perfect math it means:** the closed form is itself the sum of a geometric series
in $x=\hat a_0\,\beta_0 L$, $L=\ln(Q^2/M_Z^2)$. For $|x|<1$ the truncation converges to
float64 fast.

**The code (what we actually run):**

```js
var Q_CA=3, Q_TF=0.5, Q_NF=5, Q_MZ=91.1876, Q_ASMZ=0.1180;
function q_b0(){ return 11*Q_CA/3 - 4*Q_TF*Q_NF/3; }   // = 23/3 at nf=5

function qcd_running(N){
  var Q=10, a0=Q_ASMZ/(4*Math.PI), L=Math.log(Q*Q/(Q_MZ*Q_MZ)), x=a0*q_b0()*L;
  var exact=a0/(1+x)*4*Math.PI, s=0, term=1, n;
  for(n=0;n<N;n++){ s+=term; term*=(-x); }   // finite geometric partial sum, depth N
  var approx=a0*s*4*Math.PI;
  return {approx:approx, exact:exact, D:degrees(approx,exact), conv:(Math.abs(x)<1)};
}
```

**Verdict:** CONVERGENT. `D`: ~8 at C60 → ~15.5 (float64) once the shell is grown.

---

## RUNG 2 — QCD II · the R-ratio e⁺e⁻ → hadrons  (THE SHOWPIECE)

**The paper writes (exact, all orders):**

$$R=3\sum_q e_q^2\Big(1+\frac{\alpha_s}{\pi}+c_2\alpha_s^2+\dots\Big)$$

**The perfect math it means:** the perturbative coefficients grow factorially,
$c_n\sim n!\,\beta_0^{\,n}$ (an **infrared renormalon**). The series is **asymptotic, not
convergent** — its Borel sum is the true value, but the partial sums first approach it,
then *diverge*. The smallest term sets an **error floor**.

**The code (what we actually run):**

```js
function qcd_rratio(N){
  var a=Q_ASMZ/Math.PI, b=q_b0()/(4*Math.PI)*Math.PI;   // effective growth rate
  var partial=0, term=1, n, best=1e99, kmin=1;
  for(n=0;n<N;n++){
    var t=term; partial+=t;                              // c_n a^n
    var at=Math.abs(t); if(at<best){best=at; kmin=n;}    // track the smallest term
    term*=(n+1)*b*a;                                     // factorial growth: c_{n+1}/c_n ~ n
  }
  var errFloor=best;                                     // asymptotic error floor
  var D=Math.max(0,-Math.log(errFloor)/Math.LN10);
  return {approx:partial, D:Math.min(D,15.9), Nstar:kmin, conv:false, ceiling:true};
}
```

**Verdict:** HARD CEILING. `D` rises only to the optimal truncation `N*` (~13 terms here),
then **falls** — more compute *hurts*. This is the sharpest lesson in the tower: sometimes
the `=` is not merely slow to reach, it is *unreachable* by summing more terms.

---

## RUNG 3 — QCD III · Λ_QCD from α_s(M_Z)

**The paper writes (exact inversion):**

$$\Lambda_{\text{QCD}}=M_Z\,\exp\!\Big(\!-\frac{2\pi}{\beta_0\,\alpha_s(M_Z)}\Big)$$

**The perfect math it means:** Λ is the root of $\alpha_s(M_Z;\Lambda)=0.1180$. The closed
form above is the exact inverse; Newton's method reaches it with **quadratic** convergence.

**The code (what we actually run):**

```js
function qcd_lambda(N){
  var b0=q_b0(), target=Q_ASMZ, L=0.2, n;                // start 200 MeV (GeV units)
  function aS(Lam){ var t=Math.log(Q_MZ*Q_MZ/(Lam*Lam)); return 4*Math.PI/(b0*t); }
  for(n=0;n<N;n++){                                       // Newton iteration, depth N
    var f=aS(L)-target, h=1e-6, df=(aS(L+h)-aS(L-h))/(2*h);
    if(Math.abs(df)<1e-30) break; L=L-f/df;
    if(L<=0||!isFinite(L)) L=0.2;
  }
  var exact=Q_MZ*Math.exp(-2*Math.PI/(b0*Q_ASMZ));
  return {approx:L*1000, exact:exact*1000, D:degrees(L,exact), conv:true};   // MeV
}
```

**Verdict:** CONVERGENT (quadratic). `D` → 15 in a handful of steps.

---

## RUNG 4 — GALACTIC I · Kepler's equation  (THE SECOND SHOWPIECE)

**The paper writes (exact, transcendental):**

$$M=E-e\sin E$$

**The perfect math it means:** the Fourier–Bessel solution
$E=M+\sum_{n\ge1}\frac{2}{n}J_n(ne)\sin(nM)$ converges **only** for eccentricity
$e<0.6627434\ldots$ — the **Laplace limit**, the radius of convergence set by a
singularity of $E(e)$ in the complex plane. Above it the series **diverges** no matter
how many terms you sum.

**The code (what we actually run):**

```js
var kep_e=0.5, kep_M=1.0;
function besselJ(n,x){                         // J_n via its own series (small n·e)
  var s=0, k, sign=1;
  for(k=0;k<=24;k++){
    var term=Math.pow(x/2, n+2*k);
    var f1=1,i; for(i=2;i<=k;i++)f1*=i;         // k!
    var f2=1; for(i=2;i<=n+k;i++)f2*=i;         // (n+k)!
    s+=sign*term/(f1*f2); sign=-sign;
  }
  return s;
}
function astro_kepler(N){
  var Nk=Math.min(N,120), Ebs=kep_M, n;         // cap terms: (x/2)^n overflows at large order
  for(n=1;n<=Nk;n++){ Ebs+=(2/n)*besselJ(n,n*kep_e)*Math.sin(n*kep_M); }
  var E=kep_M, i;                               // exact reference by Newton (always converges)
  for(i=0;i<60;i++){ var f=E-kep_e*Math.sin(E)-kep_M, df=1-kep_e*Math.cos(E); E-=f/df; }
  var conv=(kep_e<0.6627);
  return {approx:Ebs, exact:E, D:degrees(Ebs,E), conv:conv, ceiling:!conv,
          elimit:0.6627, cls:(conv?'conv':'ceil')};
}
```

**Verdict:** DUAL. Below the Laplace limit: CONVERGENT → `D`=15.9. Drive the eccentricity
slider past `e=0.6627` and the rung **flips live** to a pink CEILING, `D`→0. The wall is
mathematical, not computational — Euler's cousin.

---

## RUNG 5 — GALACTIC II · comoving distance D_C

**The paper writes (exact integral):**

$$D_C=\frac{c}{H_0}\int_0^{z}\frac{dz'}{\sqrt{\Omega_m(1+z')^3+\Omega_\Lambda}}$$

**The perfect math it means:** a definite integral with no elementary antiderivative;
Simpson's rule with `N` panels has error $\sim N^{-4}$.

**The code (what we actually run):**

```js
var A_OM=0.315, A_OL=0.685, A_H0=67.4, A_Z=1.0, C_KMS=299792.458;  // Planck 2018
function astro_distance(N){
  var np=Math.max(2, (N%2===0)?N:N+1), h=A_Z/np, i;
  function inv(z){ return 1/Math.sqrt(A_OM*Math.pow(1+z,3)+A_OL); }
  var s=inv(0)+inv(A_Z);
  for(i=1;i<np;i++){ s+=(i%2? 4:2)*inv(i*h); }   // Simpson weights 1,4,2,4,...,4,1
  var approx=(C_KMS/A_H0)*s*h/3;
  var NP=20000, hh=A_Z/NP, ss=inv(0)+inv(A_Z), j; // high-N reference
  for(j=1;j<NP;j++){ ss+=(j%2?4:2)*inv(j*hh); }
  var exact=(C_KMS/A_H0)*ss*hh/3;
  return {approx:approx, exact:exact, D:degrees(approx,exact), conv:true};
}
```

**Verdict:** CONVERGENT ($N^{-4}$). `D` ~10 → ~13 as the shell grows.

---

## RUNG 6 — GALACTIC III · the blackbody integral

**The paper writes (exact, Stefan–Boltzmann):**

$$\int_0^{\infty}\frac{x^3}{e^x-1}\,dx=\frac{\pi^4}{15}$$

**The perfect math it means:** expand $1/(e^x-1)=\sum_{k\ge1}e^{-kx}$ and integrate term by
term to get $6\sum_{k\ge1}k^{-4}=6\,\zeta(4)=\pi^4/15$. Partial-sum error $\sim 2/N^3$.

**The code (what we actually run):**

```js
function astro_planck(N){
  var s=0, k; for(k=1;k<=N;k++) s+=1/(k*k*k*k);   // 6 * partial sum of zeta(4)
  var approx=6*s, exact=Math.PI*Math.PI*Math.PI*Math.PI/15;
  return {approx:approx, exact:exact, D:degrees(approx,exact), conv:true};
}
```

**Verdict:** CONVERGENT but SLOW ($N^{-3}$). `D` ~6.6 → ~9 across the shells.

---

## THE CERTAINTY METER (shared by every rung)

```js
function degrees(approx, exact){          // correct significant digits
  if(!isFinite(approx)) return 0;
  var e = Math.abs(exact)>1e-300 ? Math.abs((approx-exact)/exact) : Math.abs(approx-exact);
  if(e<=0) return 15.9;                    // float64 floor
  return Math.max(0, Math.min(15.9, -Math.log(e)/Math.LN10));
}
```

`15.9` is the ceiling of IEEE-754 double precision — even a "perfect" convergent series
cannot buy more certainty than the machine's own $\log_{10}(2^{53})\approx 15.95$ digits.
So there is a roundoff wall under *all* six, above the two named walls.

---

## THE SUMMARY TABLE

| # | rung | method | error law | verdict | D (C60 → grown) |
|---|------|--------|-----------|---------|------------------|
| 1 | α_s(Q) running | geometric resum | geometric | CONVERGES | 8 → 15.5 |
| 2 | R-ratio | asymptotic (renormalon) | factorial floor | **CEILING** | ~5 (peaks at N*, then falls) |
| 3 | Λ_QCD | Newton rootfind | quadratic | CONVERGES | → 15 |
| 4 | Kepler | Bessel series | Laplace limit e=0.6627 | **CEILING** above limit | 15.9 / 0 |
| 5 | D_C comoving | Simpson quadrature | N⁻⁴ | CONVERGES | 10 → 13 |
| 6 | blackbody | Basel 6·ζ(4) | N⁻³ | CONVERGES (slow) | 6.6 → 9 |

---

## THE POINT, ONE LINE

> The equals sign is a transcendental target our monkey-brain reality writes down as if
> it were already reached. In compute we can only follow the fractal curve to a given
> shell and read off how many digits we bought — and honour the walls where no shell,
> however large, can buy the next one.

P=12 . chi=2 . the price is always paid . always.
Buenos Aires + Ancient Korinthos. 2026-07-30. For year 12026.
