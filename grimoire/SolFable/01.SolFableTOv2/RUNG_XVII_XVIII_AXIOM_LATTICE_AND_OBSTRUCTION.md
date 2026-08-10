# RUNG XVII–XVIII — THE AXIOM LATTICE AND THE OBSTRUCTION

## Grimoire Volume III-F / sprint task 1, built on the KORINTH code patterns

### Does not overwrite XV or XVI. Corrects both, in the open.

*Imported from KORINTH KERNEL v0.1: `record`/tally, the DISCREPANCY status, the*
*OUT_OF_SCOPE list, checks that can fail on their author, and above all —*
***enumerate, do not verify a supplied list.***

---

## 0. THE HEADLINE

> **The bit is gone. It was never a choice.**
>
> Rung XV found the Rung X fork reduces to one bit: is π unital on the
> anti-lepton slot? Rung XVI found that neither generation count nor the
> massless-photon axiom decides it. **Orientability decides it.**
>
> Of the four χ rules, exactly one is orientable: **ℝ_ℓ̄ ⊕ ℂ ⊕ ℍ ⊕ M₃(ℂ)**.
> The other three carry an exact, integer-valued obstruction. And of sixteen
> enumerated algebra extensions, exactly one both removes the obstruction and
> is a legitimate direct summand — and it is the tower's own ℝ_ℓ̄.
>
> The source-aligned reading wins. For a reason the source never gave.

---

## 1. THE AXIOM LATTICE (Rung XVII)

The tower imposed four conditions and treated them as the list. This kernel
splits the conditions by **what they constrain**, and enumerates every subset.

**MODEL-LEVEL** — properties of `(A, H, π, J, γ)` that hold or fail *before any
D exists*. These disqualify a model outright.

| χ rule | unital | order-zero | **orientable** | Poincaré |
|---|---|---|---|---|
| `free_real` (ℝ_ℓ̄ ⊕ A_F, 25) | ✔ | ✔ | **✔** | untrusted |
| `zero` (A_F, 24, non-unital) | ✘ | ✔ | ✘ | untrusted |
| `lambda` (A_F, 24) | ✔ | ✔ | ✘ | untrusted |
| `lambda_bar` (A_F, 24) | ✔ | ✔ | ✘ | untrusted |

**D-LEVEL** — every subset of the optional linear constraints, one generation /
three generations:

| χ rule | none | photon only | order-one only | both |
|---|---|---|---|---|
| `free_real` | 272 / 2352 | 64 / 540 | **16 / 144** | 8 / 72 |
| `zero` | 272 / 2352 | 64 / 540 | **16 / 144** | 8 / 72 |
| `lambda` | 272 / 2352 | 104 / 888 | **32 / 282** | 16 / 138 |
| `lambda_bar` | 272 / 2352 | **80 / 672** | 32 / 282 | 16 / 138 |

**Zero DISCREPANCY rows.** All six previously published values — 272, 16, 16,
32, 32, 8, 16 — reproduced exactly. The kernel is calibrated before it is
trusted with anything new.

**New from the enumeration:** under the photon condition *alone*, `lambda` gives
**104** and `lambda_bar` gives **80**. Rung XV showed they were the same
dimension but different subspaces. They are not even the same dimension once
you stop assuming the two characters are mirror images. Nobody had looked,
because nobody had computed the cell.

---

## 2. THE KERNEL CAUGHT ITSELF AGAIN — Poincaré duality is retired

First run reported **all four models fail Poincaré duality, det = 0.** A check
that fails identically on every input is measuring the implementation, not the
models. Inspection:

```
lambda:     [ 0 -2 -2 ]        free_real:  [ 0  2 -2  0 ]
            [ 2  0  2 ]                    [-2  0  0 -2 ]
            [ 2 -2  0 ]                    [ 2  0  0  2 ]
                                           [ 0  2 -2  0 ]
```

The intersection form is **antisymmetric** — which is correct for KO-dimension
six. But **an antisymmetric matrix of odd size has determinant 0 identically.**
For a three-summand algebra the test cannot be passed by anything. It was
never discriminating.

The check now self-diagnoses and returns `UNTRUSTED` rather than voting. For
`free_real` (4×4, even, so the test *is* discriminating) it returns *degenerate*,
rank 2 of 4 — the ℝ_ℓ̄ row duplicates the M₃ row. That may be real or may be the
minimal-projection convention; it is flagged OUT_OF_SCOPE either way.

**This is the second time in three scrolls that a check failed on its author.**
That is the pattern working, not the pattern failing.

---

## 3. THE OBSTRUCTION (Rung XVIII)

Orientability, span form: is `γ ∈ span{π(a)·π^op(b)}`? Compute
`ω = γ − proj(γ)`.

| χ rule | ‖ω‖ | ‖ω‖² | support | which states |
|---|---|---|---|---|
| `free_real` | **0.0** | 0 | — | **orientable** |
| `lambda` | **2.0** | 4 | 4 states | `{11,15,27,31}` |
| `lambda_bar` | **2.0** | 4 | 4 states | `{11,15,27,31}` |
| `zero` | **2√2** | 8 | 8 states | all lepton states |

The squared norm equals the support size exactly. **Every obstructed state
contributes exactly 1.** This is an integer-valued obstruction, not a numerical
residue.

**Decoding `{11,15,27,31}`:** all have `s = −1, c = 3` — the **right-handed
lepton slots**, both particle and antiparticle. And the support is **closed
under J** (J pairs 11↔27 and 15↔31), so the obstruction is a
particle/antiparticle-symmetric object, not a one-sided defect.

The standard unital A_F cannot reach γ, and it fails precisely in the
right-handed neutrino sector — the one place everyone already knew was subtle.

---

## 4. THE ENUMERATION — sixteen candidates, one survivor

Not "does ℝ_ℓ̄ work?" but "what works?" Eight candidate real-projector
extensions on lepton states × two base rules:

| extension | base χ | fixes? | legitimate summand? |
|---|---|---|---|
| **ℝ on `{11,15,19,23}` — the tower's ℝ_ℓ̄** | **zero** | **✔** | **✔** |
| ℝ on `{11,15,19,23}` | lambda | ✔ | ✘ overlaps π(1) |
| ℝ on particle leptons `{3,7,27,31}` | lambda | ✔ | ✘ |
| ℝ on the obstruction support `{11,15,27,31}` | either | ✘ | ✘ |
| ℝ on all eight lepton states | zero | ✔ | ✘ |
| ℝ on `{11,15}` | zero | ✘ | ✔ |
| ℝ on `{19,23}` | zero | ✘ | ✔ |
| …four more | — | ✘ | — |

**Exactly one row is ✔✔.** A legitimate direct summand must be idempotent,
commute with π(A), *and* be orthogonal to π(1). For the unital rules π(1)
already covers the lepton slots, so nothing can be adjoined — the obstruction is
**irreparable** for λ and λ̄. Only χ = 0 leaves a hole, and exactly one filling
of that hole restores orientability.

Confirmed by direct construction: `χ=0` alone gives 2√2; `χ=0 + ℝ_ℓ̄` gives
**0.0**, identical to `free_real` computed directly.

> **ℝ_ℓ̄ is not a completion chosen by hand. It is the orientability obstruction
> of the standard A_F on this bimodule, made into an algebra.**

---

## 5. CORRECTIONS — twice to the same paragraph

**Rung XV §3.4 said:** *"The adjoined ℝ_ℓ̄ summand imposes no new order-one
constraint whatsoever. The '+1 dimension column' is unit-completion
bookkeeping."*

That is **true at the D-level and false at the model level.** The ℝ summand is
invisible to the order-one condition — the D-spaces are the identical subspace,
Rung XV proved it and it still stands. But without it, γ is unreachable and the
data is not an orientable spectral triple at all. **The ℝ summand is invisible
to order-one and load-bearing for orientability.** The "+1" is not bookkeeping.
I called it bookkeeping. It isn't.

**Rung XVI §5 said:** *"dim D = 16 is reached by two inequivalent
configurations."* Dimensionally still true. But the second route
(`λ` + photon → 16) is **non-orientable**, so it is not a competing spectral
triple. The degeneracy that broke Rung XII's selector is broken by
orientability, not by dimension.

**Net:** Rung X's fork moves `OPEN → CLOSED (conditionally)`, and this time in a
direction, not just into a smaller box.

---

## 6. WHAT THIS DOES *NOT* CLOSE

- **Orientability here is the SPAN FORM**, `γ ∈ span{π(a)π^op(b)}`, not the full
  Hochschild-cycle condition. Everything in §3–§5 is CONDITIONAL on that
  reading. This is the single load-bearing caveat and it needs a source.
- **"Unique" means unique among the sixteen tested** — diagonal real projector
  extensions on lepton states. Complex, quaternionic, and off-diagonal
  extensions are **untested**. The enumeration is wider than a verification and
  narrower than a proof.
- **The bimodule is still declared.** `c ∈ {0,1,2,3}` is typed in at Code block I
  line 312 and nothing here derives it. The number of colours remains
  underived — here and in the literature.
- **Poincaré duality is unresolved**, not passed. The check is retired, not
  satisfied.
- **Global Step 4 is exactly as open as it was four scrolls ago.** Still the
  joke. Still the only real target.

---

## 7. ON THE CRYSTAL

The picture — *an asymmetric object in a symmetric space; the space tries to
restore symmetry and cannot* — is the one thing in this session that turned out
to be literally what the arithmetic says. The obstruction is exact, integer,
J-symmetric, and localised on four named states.

Two disciplines to keep around it:

1. **It needs no mythology.** ‖ω‖ = 2.0 on the right-handed leptons stands on
   its own receipt. Plato's boundaries and the Vedic stitching are a good reason
   to have gone looking; they are not part of the proof and must not enter the
   ledger. Different scroll, different file, no shared wall.
2. **It is not information theory.** The massless-photon condition is
   `[D, π(c)] = 0`, named for what it implies about photon mass under inner
   fluctuations. It has no relation to Landauer erasure or statistical shadows.
   That bridge does not hold weight.

And the good news you didn't expect: **no galaxy-sized lattice is required.**
The whole lattice is 272 and 512 columns. Everything in this scroll runs in
seconds on one core. Compute was never the blocker. The axiom list was — and
one axiom of it just moved.

---

## LEDGER DELTA — XVII / XVIII

| Claim | prior status | now | receipt |
|---|---|---|---|
| The unitality bit is undecidable inside the tower | XVI: unresolved | **decided by orientability** | ‖ω‖ = 0 vs 2.0 |
| ℝ_ℓ̄ is free / bookkeeping | XV: EXACT at D-level | **load-bearing at model level** | γ unreachable without it |
| ℝ_ℓ̄ was a hand-made completion | assumed | **the unique legitimate repair of 16 tested** | enumeration |
| `dim D = 16` degeneracy | XVI: non-injective | **broken by orientability** | λ+photon is non-orientable |
| λ and λ̄ are mirror images | assumed | **false — 104 vs 80 under photon alone** | lattice cell |
| Poincaré duality fails for all models | first run | **check untrusted, retired** | antisym + odd size ⇒ det 0 |
| Tower's four conditions are the full list | XVI: false | **false, and one more now supplied** | orientability |
| Global Step 4 | TRIVIAL (joke) | TRIVIAL (joke) | unchanged |

---

*P = 12. χ = 2. ‖ω‖ = 2.*
*The space tried to close and came up exactly two short, in the neutrino sector.*
*Enumerate, don't verify. Incomplete is fine. Fake is not.*
