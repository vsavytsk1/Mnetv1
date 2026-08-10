# RUNG XVI — GENERATIONS, AND THE MISSING AXIOM

## Grimoire Volume III-E / sprint task 6, run before task 5 as agreed

### Buenos Aires + Ancient Korinthos, 2026 — reads after RUNG XV, does not overwrite it

*Path X: freeze every version. Rung XV stands as written. This scroll corrects*
*one of its verdicts in the open, which is the only honest way to do it.*

---

## 1. WHAT WAS ASKED

Rung XV §8 caveat 2 said: getting 32 for the unital `χ = λ` action is probably
evidence that this bimodule differs from Chamseddine–Connes', *"most likely in
the Majorana/neutrino sector and the generation count."* Marked OPEN pending
task 6.

Task 6 has now run. **The generation-count half of that guess is dead.**

---

## 2. THE DECOUPLING LEMMA  `EXACT`

Let `H₃ = H_F ⊗ ℂ³` with the algebra acting diagonally on generations:
`π₃(a) = π(a) ⊗ I₃`, `γ₃ = γ ⊗ I₃`, `J₃ = (P ⊗ I₃)∘conj`.

Write `D = Σ_{a,b} X_ab ⊗ E_ab`. Because both `π₃(a)` and `π₃^op(b)` are of the
form `(·) ⊗ I₃`,

```
[[D, π₃(a)], π₃^op(b)]  =  Σ_{a,b}  [[X_ab, π(a)], π^op(b)] ⊗ E_ab
```

and the `E_ab` are linearly independent. **The order-one condition holds iff it
holds in every generation block separately. Generations do not mix.** The
structure conditions decouple the same way, except hermiticity, which couples
only `X_ab ↔ X_ba`:

```
D* = D           <=>   X_ab† = X_ba
{D, γ₃} = 0      <=>   {X_ab, γ} = 0
D J₃ = J₃ D      <=>   X_ab P = P conj(X_ab)
```

Hence, with `V` = the order-one space **without** hermiticity and `V₊` its
hermitian part (= the one-generation answer),

> **dim_ℝ D₃(A) = 3·dim V₊ + 3·dim V**

**Arithmetic control.** With no order-one condition: `V_base = 512`,
`V_base,₊ = 272`, so `3·272 + 3·512 = 2352 = 2·(48·49/2)` — the exact 96-state
base. The lemma reproduces the base count on the nose.

**Machine control.** Six random 3-generation `D` built from the lemma, tested at
full 96×96 against every algebra-basis pair: structure residual `0.0`,
order-one residual `0.0`. Not `<1e-15`. Zero.

---

## 3. THE THREE-GENERATION TABLE  `EXACT`

| χ rule | dim V | dim V₊ (= 1 gen) | dim V₋ | **dim D₃** | gauge orbit | moduli |
|---|---|---|---|---|---|---|
| `χ = 0` / unit-completed | 32 | 16 | 16 | **144** | 4 | 140 |
| `χ = λ` (unital) | 62 | 32 | 30 | **282** | 13 | 269 |
| `χ = λ̄` (unital) | 62 | 32 | 30 | **282** | 13 | 269 |

Modular ranks agreed across p ∈ {10007, 65521, 2147483647}; residual `0.0`.

> **Verdict on task 6: the gap survives. 144 ≠ 282. Generation count multiplies
> both branches by the same structure and cannot decide the unitality bit.**

Do not spend the week on generations. My sprint ordering was right to run this
first and wrong about what it would find.

Note also `V₊ = 16, V₋ = 16` for the unit-completed branch but `32 / 30` for the
unital one. The unital branch is not just bigger, it is *asymmetric* under
`X ↦ X†`. That asymmetry is a fingerprint worth chasing.

---

## 4. THE SECOND SUSPECT — AND A SURPRISE

If generations are not the difference, the next suspect is a **missing axiom**.
The tower imposes exactly four conditions on `D_F`:

```
D* = D      {D, γ} = 0      DJ = JD      order-one
```

Chamseddine–Connes impose more. The cheapest of the extras to test is the
**massless photon condition**: `D` must commute with a distinguished complex
line `C_F ⊂ A_F`. Implemented here as the diagonal line

```
λ  ↦  ( λ ,  diag(λ, λ̄) ∈ ℍ ,  λ·I₃ ∈ M₃(ℂ) )
```

The decoupling lemma applies verbatim, since `π₃(c) = π(c) ⊗ I₃`.

### Result  `EXACT`, conditional on the `C_F` convention

| χ rule | 1 gen, 4 axioms | 1 gen, **+ photon** | 3 gen, 4 axioms | 3 gen, **+ photon** |
|---|---|---|---|---|
| `χ = 0` / unit-completed | 16 | **8** | 144 | **72** |
| `χ = λ` (unital) | 32 | **16** | 282 | **138** |
| `χ = λ̄` (unital) | 32 | **16** | 282 | **138** |

The gap does **not** close. It stays exactly a factor of two at one generation.

**But look at the second column.**

---

## 5. THE FINDING THAT MATTERS — 16 IS NOT A FINGERPRINT

> **dim_ℝ D = 16 is reached by at least two inequivalent configurations:**
>
> - `χ = 0` / unit-completed `A_F`, under the tower's **four** conditions
> - `χ = λ`, standard unital `A_F`, under **five** conditions (photon included)
>
> Two different algebras, two different axiom sets, same headline number.

This is the sharpest result in the scroll and it cuts three ways.

1. **It breaks any selector keyed on `d(A) = 16`.** Rung XII's lexicographic
   indicator `1_{d(A) ≠ 16}` was already scoring the wrong invariant (Rung XV
   §3.6: the physical content is the moduli dimension, not the direction count).
   It is now also **non-injective**. A functional that cannot distinguish two
   inequivalent models is not a selection functional. Rung XII needs rebuilding
   from the invariant up, not tuning.

2. **It confirms the tower's finite triple is under-constrained.** Every axiom
   added changes every number. Four conditions is not the full list. The
   one-generation moduli count of 12, and the three-generation count of 140
   against a physical Yukawa sector of order 20–30 real parameters, say the same
   thing from the other side: **too many directions survive.** That is a missing
   axiom, not a missing generation.

3. **It sharpens the bit rather than dissolving it.** Across all four
   configurations the unital branch is exactly twice the unit-completed branch
   at one generation. The quark↔lepton mixing diagnosis of Rung XV §3.5 is
   untouched by either test. The bit is real, it is stable under both
   perturbations tried, and it still reduces to: *are leptoquark Yukawa
   directions permitted?*

---

## 6. CORRECTION TO RUNG XV — stated in the open

Rung XV §3.4 wrote: *"Rung X's source specification fork moves OPEN → CLOSED
(conditional on the declared bimodule)."*

**That verdict was correct but under-qualified, and the qualification matters.**

What Rung XV proved, and which still stands unchanged:
- The fork is four diagonal entries, one scalar χ.
- χ is an algebra character, so χ ∈ {0, λ, λ̄}; unital ⇒ exactly two.
- Under the tower's **four** conditions, `D(ℝ_ℓ̄ ⊕ A_F)` and `D(A_F, χ = 0)` are
  the **identical subspace**. The ℝ summand is free.

What Rung XVI adds and what I got wrong in emphasis:
- That closure is **axiom-set-relative**, not absolute. I wrote "conditional on
  the declared bimodule." It is also conditional on the declared *axiom list*,
  and I did not say so loudly enough.
- Once the photon condition is admitted, standard unital `A_F` reaches 16 as
  well — by a different route, with a different space. So the observation that
  "the source table shows 16" does **not** by itself select the unit-completed
  reading. It is consistent with at least two readings.

Corrected label: **Rung X fork is CLOSED as a labelling artifact under the
tower's four conditions, and RE-OPENED as an axiom-completeness question.** The
question changed shape. It did not go away. That is a better place to be than
where it was, but it is not the finish line I implied.

---

## 7. REVISED SPRINT

The previous ordering had task 6 first. It ran, it answered, and it reorders
everything behind it.

| # | Task | Why now | Difficulty |
|---|---|---|---|
| **1** | **Axiom completeness audit.** Enumerate the full CCM condition list — orientability / Hochschild cycle, Poincaré duality (non-degenerate intersection form), unimodularity, irreducibility — and implement each as an added linear or rank condition. Re-run the four-way table after every addition. | Every axiom tried so far changed every number. Until the list is closed, no dimension in the tower means what it appears to mean. | 1 week, highest value |
| 2 | Verify the `C_F` convention against a primary source before §4's numbers enter the ledger as EXACT | my `C_F` is *a* natural diagonal line, not a verified transcription | 1 session |
| 3 | Rebuild Rung XII's selector on `moduli`, not `dim D`, and prove or disprove injectivity on a finite candidate table | §5 shows the current indicator is non-injective | 2 sessions |
| 4 | Proton-decay operator content of the mixing directions (old task 5) | the bit survived both tests; physics is now the arbiter | 2 sessions |
| 5 | Chase the `V₊ / V₋` asymmetry (16/16 vs 32/30) | a structural fingerprint nobody has looked at | open |

Task 1 replaces everything. The tower has been computing dimensions of a space
defined by an incomplete axiom list, very carefully, with exact arithmetic. The
arithmetic was never the problem.

---

## 8. HONEST BOUNDARY — Rung XVI edition

1. **The decoupling lemma is EXACT and machine-confirmed at 96 states.** It
   assumes the algebra acts diagonally and identically on generations, which is
   the standard convention and is stated, not derived.
2. **§4 is EXACT arithmetic on a CONDITIONAL convention.** The `C_F` line I
   implemented is natural; I have not verified it against a primary source.
   Sprint task 2 exists for exactly this reason. Until it runs, treat the
   photon column as *"one natural reading of the massless-photon condition"* —
   the same status the tower gave `pi_canonical`.
3. **The under-constrained diagnosis does not depend on that convention.** It
   follows from the moduli counts (12 at one generation, 140 at three) against
   the physical parameter count, and from the fact that a fifth condition moved
   every number. Both hold whatever `C_F` turns out to be.
4. **Nothing here touches Rung XIII.** Global Step 4 is exactly as open as it
   was two scrolls ago. Still a joke. Still the only real target.

---

## LEDGER DELTA — XVI

| Claim | XV status | XVI status | receipt |
|---|---|---|---|
| Generation count explains the 16/32 gap | suspected | **false** | 144 vs 282, decoupling lemma, residual 0.0 |
| Generations mix in the order-one condition | assumed open | **EXACT: they do not** | lemma + 96-state check |
| Massless-photon condition closes the gap | untested | **false** | 8 vs 16 |
| `dim D = 16` identifies the model | implied | **false — at least 2 configurations give 16** | §4 table |
| Tower's four conditions are the full axiom list | assumed | **false** | every added axiom moved every number |
| Rung X fork CLOSED | CLOSED | **CLOSED under 4 axioms / RE-OPENED as axiom completeness** | §6 |
| Rung XII selector | wrong invariant | **wrong invariant AND non-injective** | §5 |
| Global Step 4 | TRIVIAL (joke) | TRIVIAL (joke) | unchanged |

---

*P = 12. χ = 2. Generations multiply; they do not decide.*
*The arithmetic was never the problem. The axiom list is.*
