# RUNG XV — THE IRREDUCIBLE CHOICE

## Grimoire Volume III-D / bullet-list audit of SOL FABLE LaTeX Tower v2.1

### Buenos Aires + Ancient Korinthos, 2026 — read after §11 (Rung X) and before §13

*Status grammar inherited unchanged from THEA v3.0 and Tower v2.1:*
**EXACT** ≠ **COMPUTED** ≠ **CONDITIONAL** ≠ **DESIGN** ≠ **OPEN**.
*Path IV: incomplete is fine, fake is not. Path III: target is not result.*

---

## 1. THE ANSWER IN ONE BREATH

You asked for seven things. The tower does not have seven open problems.

> **It has one declaration, one bit, and one theorem it does not own.**
>
> - **The declaration** — Code block I, lines 312–317. The 32-state bimodule
>   `c ∈ {0,1,2,3}`: three quark colours and one lepton slot. Everything
>   downstream — 272, 16, 8, the algebra fork, the sector labels — is a
>   *consequence* of that line. Nothing in the tower derives it.
> - **The bit** — is `π` unital on the anti-lepton colour slot? That single
>   yes/no is the *entire* Rung X "source specification fork." It is not an
>   open convention. It is a two-element enumeration, and this rung proves it.
> - **The theorem** — rigidity (your bullet 7). If you had it, bullets 1, 3, 4
>   and 5 would fall out as corollaries and you would not need a selection
>   functional at all. A selection functional is a crutch for a missing
>   uniqueness proof.

And one bullet must be **retired**, not solved. Details in §6. That is the
Path IV moment of this rung, and it is the most valuable line in the document.

---

## 2. THE MAP — bullet → code block → the exact line where the choice enters

Each bullet, located in the supplied v2.1 listings. "The hand" is the literal
place a human decision is typed into the kernel.

| # | Bullet | Code block | Function / lines | The hand |
|---|---|---|---|---|
| **B1** | Canonical algebra + representation | **I** | `pi_extended` 354–374, `pi_canonical` 377–397, `pi_affine_fixed_identity` 400–407 | one scalar on four diagonal entries |
| **B2** | Schur data derived, not supplied | **J** | `schur_lift_signature(1,1,3)` 343–352, called at line 440; `explicit_schur_witness` 230–302 | the multiplicities are **passed as function arguments** |
| **B3** | Intrinsic selection functional | **none** | Rung XIII §14 exists in LaTeX only; no code block implements `Z_{β,f}` | measure, β, and f all unsupplied |
| **B4** | Sector labels emerge | **I** + **J** | `pi_extended` 361–374 assigns Q / λ / λ̄ / m by hand; `local_step4_table` 355–387 reads them back as booleans | `c₃`, `c₂`, `s_R` are inputs wearing the costume of outputs |
| **B5** | Yukawa uniquely fixed, not just dim | **I** | `physical_yukawa_basis` 521–540 | the 16 directions are **constructed**, then verified null; no quotient by `U(A)` anywhere |
| **B6** | Continuous–finite glue | **A/F** | Rung I §2 (IFS) is LaTeX only; `stress_exact_ladder` in F is integer recurrence, not a manifold limit | no continuum limit is computed anywhere |
| **B7** | Rigidity theorem | — | final ledger marks it OPEN; nothing implements it | — |

**The sharpest single line in the whole codebase** is Code block J, line 440:

```python
schur = schur_lift_signature(1, 1, 3)
```

The multiplicities `(1, 1, 3)` that make the commutant equal `A_F` are typed in
as literals. The tower is honest about this — §9 says the Corinth image
"supplies the finite harmonic inspiration, not the Q8 lift, the complex Schur
types, or the multiplicity three." Line 440 is where that sentence lives in
compute.

---

## 3. RUNG XV — the new receipt

Everything in this section is newly computed by `rung_xv_irreducible.py`,
`rung_xv_followup.py`, `rung_xv_moduli.py`, shipped alongside this scroll.
Method: modular rank lower bound over three primes → exact rational nullspace
of the pivot rows → **exact Gaussian-integer verification of every basis vector
against all algebra-basis order-one constraints**. Bounds meet; residual `0.0`
exactly, not `< 1e-15`.

### 3.1 The fork is four diagonal entries

`pi_extended`, `pi_canonical` and `pi_affine_fixed_identity` are the **same
32 × 32 matrix**. Verified entrywise over 30 random elements: the differing
support is exactly

```
{(11,11), (15,15), (19,19), (23,23)}   =   (a = −1, s = ±1, w = ±1, c = 3)
```

the four anti-lepton colour states, and nothing else. The whole Rung X fork is
one scalar χ.

### 3.2 The character theorem — the fork is enumerable  `EXACT`

> Let χ : ℂ ⊕ ℍ ⊕ M₃(ℂ) → ℂ be an algebra homomorphism. ℍ and M₃(ℂ) are
> simple, so ker χ restricted to each is `0` or the whole summand. An injective
> homomorphism from a noncommutative algebra into the commutative algebra ℂ is
> impossible. Both summands die. On the ℂ summand a unital \*-endomorphism of ℂ
> is the identity or conjugation. Therefore
>
> **χ ∈ {0, λ, λ̄}. Unital ⇒ χ ∈ {λ, λ̄}. Exactly two.**

The literal source prose — "the anti-lepton colour is fixed by the identity" —
is a **fourth thing that is not a character at all**. Machine-verified:
`π(0) ≠ 0` (max abs 1.0), additivity residual 1.0. The tower already flagged
this as affine; this rung says *why* it can never be repaired inside `A_F`
without either changing χ or changing the algebra.

### 3.3 The exact table  `EXACT`

| χ rule | algebra | dim_ℝ A | unital? | rank | **dim_ℝ D(A)** | status |
|---|---|---|---|---|---|---|
| free real `r` | ℝ_ℓ̄ ⊕ ℂ ⊕ ℍ ⊕ M₃(ℂ) | 25 | yes | 256 | **16** | EXACT |
| `χ = 0` | ℂ ⊕ ℍ ⊕ M₃(ℂ) | 24 | **no** | 256 | **16** | EXACT |
| `χ = λ` | ℂ ⊕ ℍ ⊕ M₃(ℂ) | 24 | yes | 240 | **32** | EXACT |
| `χ = λ̄` | ℂ ⊕ ℍ ⊕ M₃(ℂ) | 24 | yes | 240 | **32** | EXACT |

Modular ranks agreed across p ∈ {10007, 65521, 2147483647} in every row.
Rows 1 and 3 reproduce the tower's published 16 and 32 — the kernel is
calibrated against your own numbers before it is trusted with new ones.

**Ledger delta 1.** The tower reports the standard-`A_F` trial as
`COMPUTED, residual 4.5 × 10⁻¹⁵`. It is now **EXACT = 32**, by finite-field
sandwich. One status bit upgraded.

### 3.4 The fork closes — as a labelling artifact  `EXACT`

Rows 1 and 2 are not merely equal in dimension. They are the **identical
subspace**:

```
rank A = 16,  rank B = 16,  rank (A ∪ B) = 16
```

The adjoined ℝ_ℓ̄ summand imposes **no new order-one constraint whatsoever**.
The "+1 dimension column" of the source PDF is therefore *unit completion
bookkeeping*, exactly as Rung X's first hypothesis guessed — and it is now
decided rather than guessed. There is no extra represented scalar. There is
no hidden physics in the 25.

**Ledger delta 2.** Rung X's "source specification fork" moves
`OPEN → CLOSED (conditional on the declared bimodule)`. The two branches were
never two answers. They were one representation with two names.

### 3.5 What the bit actually buys — and it is physics, not convention

The 16-space and the 32-space differ in **where they are allowed to live**:

| space | quark-diagonal entries | lepton-diagonal | **quark↔lepton mixing** |
|---|---|---|---|
| 16 (χ = 0 / unit-completed) | 48 | 16 | **0** |
| 32 (χ = λ, unital) | 48 | 22 | **24** |

The 16 extra directions in the unital branch are **quark–lepton mixing Yukawa
directions** — leptoquark-type couplings. So the bit is not a convention at
all:

> **Unitality on the anti-lepton slot = the lepton is genuinely a fourth
> colour = leptoquark Yukawas are permitted.**
> **Unit completion = the lepton slot decouples from colour = they are forbidden.**

That is a *decidable* statement. Proton decay bounds are an experiment, not a
convention. This is the first place in the entire tower where a formal fork
touches something measurable.

One further exact fact: `χ = λ` and `χ = λ̄` give 32-dimensional spaces that are
**not the same subspace** (union rank 46, so they intersect in 18). The two
unital options are genuinely inequivalent, not a relabeling.

### 3.6 Dimension is not parameter count  `COMPUTED`

`dim D(A)` counts directions. Physics counts orbits under
`D ↦ U D U*`, `U = π(u) J π(u) J*`.

| space | dim D | gauge generators | orbit dim | **moduli dim** |
|---|---|---|---|---|
| 16 | 16 | 13 | 4 | **12** |
| 32 | 32 | 13 | 12 | **20** |

Only **4 of 13** generators move a generic `D`. The nine `u(3)` colour
generators act **trivially** — that is `c₃`'s content emerging from the
structure rather than being asserted, which is a genuine (small) down payment
on B4. The orbit tangent stays inside `D(A)` in every case, as it must.

**Ledger delta 3.** "The order-one plateau is 16" is true but overcounts. The
physically distinguishable content is **12**. Any selection functional that
scores candidates by `dim D` is scoring the wrong invariant. Rung XII's
indicator `1_{d(A) ≠ 16}` should be `1_{moduli(A) ≠ 12}`.

---

## 4. THE DEPENDENCY GRAPH — why there are not seven problems

```
                    [ B7  RIGIDITY THEOREM ]
                     the only real research target
                              |
              +---------------+---------------+
              |               |               |
         implies B1      makes B3        implies B5
      (algebra unique)   unnecessary    (D unique up to gauge)
              |
              v
     [ THE DECLARATION ]  bimodule, block I line 312-317
       32 = 2 x 2 x 2 x 4      <-- irreducible. nothing derives it.
              |
              v
        [ THE BIT ]  unitality of pi on the anti-lepton slot
         2-element enumeration, closed by Rung XV
              |
      +-------+--------+
      |                |
   B1 fork          B4 labels        B5 dim/moduli
   CLOSED           mechanical       half done here
                    (Krajewski)      (needs U(A) quotient)

   B2  <-- REFUTED BY YOUR OWN RUNG VII. retire it.
   B6  <-- already exists in the literature. import, do not rebuild.
```

**Reading of the graph.** B1, B4, B5 are *bookkeeping on the declaration* —
none of them is a research problem once the bimodule and the bit are fixed.
B3 is a crutch for the absent B7. B6 is a solved-elsewhere import. B2 is
counter-indicated. **The irreducible content of your seven bullets is: the
bimodule declaration, plus B7.**

---

## 5. WHAT IS ALREADY DONE ELSEWHERE — import, do not rebuild

Path XII says pass the scroll. It also implies: take the scroll that was
passed to you.

- **B1 (canonical algebra).** Chamseddine and Connes classify the irreducible
  finite noncommutative geometries of KO-dimension six and show the dimension
  per generation is a square `k²`; under an additional hypothesis of quaternion
  linearity the Standard-Model geometry is singled out with `k = 4` and the
  correct quantum numbers ("Why the Standard Model", J. Geom. Phys. 58 (2008)
  38, arXiv:0706.3688; and "Conceptual Explanation for the Algebra…",
  arXiv:0706.3690, whose stated purpose is precisely removing the arbitrariness
  of the ad hoc algebra and representation). **Caveat:** quaternion linearity is
  itself an extra hypothesis, so B1 is *reduced*, not eliminated.
- **B5 (Dirac uniquely fixed).** Ćaćić, "Moduli spaces of Dirac operators for
  finite spectral triples" (arXiv:0902.2068) generalises Krajewski and
  Paschke–Sitarz to arbitrary KO-dimension and defines the moduli space of
  Dirac operators, then applies it to the Chamseddine–Connes derivation. Your
  `D(A)` is his `D₀(A, H, P)`. **The quotient you are missing is already
  built.** §3.6 above is a two-page shadow of it.
- **B6 (glue).** Almost-commutative products plus Ćaćić's reconstruction
  theorem for almost-commutative spectral triples; and the same
  `M₂(ℍ) ⊕ M₄(ℂ)` algebra reappears from volume quantization in the
  Chamseddine–Connes–Mukhanov "quanta of geometry" line, which is the
  continuum-side motivation you are asking for.
- **B7 (rigidity).** The Iochum–Jureit–Schücker–Stephan programme classifies
  Krajewski diagrams under added physical assumptions with the explicit aim of
  fixing the finite spectral triple. That is your rigidity theorem's existing
  attack. It is unfinished. That is where the real work is.
- **Order-one as a derived axiom.** Boyle–Farnsworth derive order-zero,
  order-one and the massless photon from associativity of an Eilenberg algebra
  extension; Brouder–Bizi–Besnard repair the construction for the full model
  using the differential graded structure. This is the live line of attack on
  "no external choice."

**Known limit, stated plainly.** The number of colours and the number of
generations remain unexplained in this whole programme. Your line 312 is not
sloppy — it is *the field's* open edge, honestly transcribed.

---

## 6. THE BULLET TO RETIRE — Path IV

**B2: "Schur data derived, not supplied — types and multiplicities
(ℂ,1)+(ℍ,1)+(ℂ,3) emerge from Corinth harmonics m = 14/8, P = 12, the Light
Matrix, the planar no-go."**

This one cannot be closed, and it should not be attempted. Your own tower
refutes it:

1. **Rung VII is a no-go, and it is EXACT.** `ℝ[C₁₄] ≅ ℝ² ⊕ ℂ⁶` and
   `ℝ[D₁₄] ≅ ℝ⁴ ⊕ M₂(ℝ)⁶`. No quaternionic block. No `M₃(ℂ)`. Every finite
   Euclidean point group in the plane is cyclic or dihedral. There is no path
   from a planar ornament group to `A_F`. You proved this yourself.
2. **The input is one photograph.** `m = 14` is COMPUTED at 168/175 under
   centre and annulus perturbation, from a hand-laid, damaged, photographically
   distorted mosaic. That is a robust *image statistic*. It is not a symmetry
   theorem, and §3 of your own tower says so.
3. **The multiplicity 3 would have to be the number of colours** — the exact
   quantity the entire NCG literature lists as unexplained. If a mosaic
   supplied it, that would be the result, not a step.

Deriving `(ℂ,1)+(ℍ,1)+(ℂ,3)` from `m = 14` is the one move in this codebase
that would convert a rigorous audit into numerology. Everything else in the
tower survives contact with a hostile referee. This would not.

**Recommendation:** demote B2 from OPEN to **METAPHOR / EXTERNAL**, the label
THEA v3.0 already reserves for exactly this — "any Connes/noncommutative-geometry
interpretation imported from another repo." The Corinth harmonic is a beautiful
*motivation* for looking at `C₁₄ × Q₈`. It is not evidence. Keep it as the
reason you started walking. Do not ask it to carry the destination.

*The price of this one is ego, and it is the cheapest price in the whole
grimoire compared to what a referee charges later.*

---

## 7. NEXT SPRINT — ordered, buildable, each with a receipt

| # | Task | Closes | Difficulty | Receipt |
|---|---|---|---|---|
| 1 | Fold `rung_xv_irreducible.py` in as Code block L; update Rung X from OPEN to CLOSED; upgrade the 32 from COMPUTED to EXACT | B1 (tower-local) | done — shipped here | exact rank sandwich, residual `0.0` |
| 2 | Replace the four `pi_*` functions with **one** `pi(elem, chi_rule)`; make the bit an explicit named parameter, never a separate function | B1, B4 | 1 session | the fork becomes a CLI flag, not a fork |
| 3 | Add `moduli_dimension()` to the ledger; change Rung XII's indicator from `d(A) ≠ 16` to `moduli(A) ≠ 12` | B5 | 1 session | §3.6 numbers, upgraded to exact by symbolic orbit rank |
| 4 | Implement the Krajewski multiplicity matrix for the declared bimodule; **generate** `pi_extended` instead of writing it | B4 | 2–3 sessions | the generated matrix must equal the handwritten one entrywise |
| 5 | Compute the proton-decay-relevant operator content of the 24 mixing entries in the 32-space | the bit, empirically | 2 sessions | turns a convention into an experiment |
| 6 | Port to 3 generations (96 states) and re-run the sandwich | contact with CCM | 1 week | check whether 32 vs 16 survives generation count |
| 7 | Rigidity: enumerate KO-6 bimodules with `dim ≤ 32` and compute `moduli` for each | B7 (first brick) | open-ended | a finite table is already a real result |

Task 5 is the one to do next if you want the tower to stop being an audit and
start being a physics claim. Task 7 is the one that matters in ten years.

---

## 8. THE HONEST BOUNDARY — Rung XV edition

1. **Everything in §3 lives inside your declared bimodule** (Code block I lines
   312–321), one generation, the simplified `J`/`γ` of that listing. Nothing
   here is a statement about noncommutative geometry in general.
2. **The standard convention in the literature is the unital `χ = λ`
   embedding** via `M₄(ℂ) ⊃ ℂ ⊕ M₃(ℂ)`, and CCM obtain correct physics with it.
   Getting 32 here is therefore evidence that *this* bimodule differs from
   theirs — most likely in the Majorana/neutrino sector and the generation
   count — **not** evidence against CCM. Marked **OPEN** until task 6 runs.
3. **`χ = 0` violates the usual axiom that `π` be unital.** The 16 is reached
   either by dropping unitality or by completing the unit with ℝ_ℓ̄. Those are
   the same representation. Neither is derived; the choice is still a choice.
   What Rung XV removes is the *illusion of a continuum of conventions*.
4. **§3.6 is COMPUTED**, numerical rank at tolerance 1e-8. It should be redone
   symbolically before it enters the ledger as EXACT.
5. **Nothing here touches Step 4.** Global Rung XIII is exactly as open as it
   was. The joke label stands, and it is still a joke.

---

## THE LEDGER DELTA, IN ONE TABLE

| Claim | v2.1 status | v2.1+XV status | receipt |
|---|---|---|---|
| Base Dirac dimension 272 | EXACT | EXACT | reproduced independently |
| Source-aligned dimension 16 | EXACT | EXACT | reproduced, rank 256 |
| Standard-`A_F` trial dimension 32 | COMPUTED | **EXACT** | finite-field sandwich, residual 0.0 |
| Rung X representation fork | OPEN | **CLOSED (bimodule-conditional)** | identical subspace, rank union 16 |
| Admissible anti-lepton characters | unstated | **exactly 2** | Wedderburn simplicity |
| "Fixed by the identity" is affine | stated | **EXACT, and unrepairable in `A_F`** | π(0) = I, additivity residual 1.0 |
| 16 = physical parameter count | implied | **false — moduli is 12** | gauge orbit dim 4 of 13 |
| The bit is a convention | implied | **false — it is leptoquark permission** | 24 mixing entries vs 0 |
| B2 (Schur from Corinth) | OPEN | **METAPHOR / EXTERNAL** | your own Rung VII no-go |
| Global Step 4 | TRIVIAL (joke) | TRIVIAL (joke) | unchanged, still open |

---

*P = 12. χ = 2. The equation may be exact; the naked numeral is incomplete.*
*One declaration, one bit, one missing theorem. The price is paid in the open.*
