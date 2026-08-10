# KORINTH KERNEL v0.1 — RECEIPT

## The scroll is inspiration. This is the proof.

### Buenos Aires + Ancient Korinthos, 2026 — separate scroll, separate ledger

*No claim in this file bears on the SOL FABLE tower. Different object, different*
*receipt, no shared load-bearing wall. That separation is the point.*

---

## TALLY

```
EXACT         17
COMPUTED       5
DISCREPANCY    4
OUT_OF_SCOPE   1     (+ 10 claims no kernel can touch, listed at the end)
```

Everything is exact rational (`Fraction`) or integer arithmetic, except where an
irrational is unavoidable — those run in 60-digit `Decimal` with the error
printed. Nothing was accepted because a source said it.

---

## THE FOUR DISCREPANCIES

### 1. The Baudhāyana triple list is a selection, not an enumeration

The scroll implied completeness. It isn't. Enumerating **all** primitive
Pythagorean triples with hypotenuse ≤ 37:

```
(3,4,5) (5,12,13) (8,15,17) (20,21,29) (7,24,25) (12,35,37)
```

Baudhāyana i.49 lists five of these six. **(20,21,29) is omitted.** The five
listed are all genuinely primitive (gcd = 1, verified); (15,36,39) is correctly
non-primitive, gcd 3, = 3×(5,12,13). Whatever governed the selection, it was not
"all triples below a bound." Worth knowing before you build anything that
assumes the list is closed.

### 2. The caturaśra brick inventory gives 7.75 square puruṣas, not 7.5

Both layer inventories tile **exactly the same area**, as they must:

```
layers 1,3,5:  110×(30×30) + 85×(12×12) +  5×(12×6)              = 111,600 aṅgula²
layers 2,4:    110×(30×30) + 75×(12×12) + 10×(12×6) + 5×(18×12)  = 111,600 aṅgula²
                                                        difference =       0
```

That agreement is a strong signal the brick tables are transcribed correctly.
But `111,600 / 120² = 31/4 = **7.75** square puruṣas`, against the scroll's
stated 7½. The gap is exactly ¼ square puruṣa — too clean to be rounding. Body
square alone is 240² = 4 square puruṣas, so wings+tail carry 3.75.

**Either the caturaśra is not a 7½ altar, or one figure is mis-transcribed.**
The kernel cannot settle which. Needs Sen & Bag (INSA 1983) directly. **OPEN.**

### 3. The special-brick layer split is one short

```
98 + 41 + 71 + 47 + 138 = 395     stated total: 396     (= 360 + 36)
```

The year-symbolism total (396) is arithmetically clean. The layer breakdown
sums to 395. Off by exactly one. Transcription slip or a real feature of the
ritual count — needs Kak's original table. **OPEN.**

### 4. Anaximander's 9/18/27 is arithmetic, not geometric

Successive ratios are **2, then 3/2** — not constant. The series is `9 × (1,2,3)`:
arithmetic in units of 9. Calling it a "×9 ratio series" (as the phrasing invites)
is wrong. The doxographic pairs check out — sun 27/28, moon 18/19 — consistent
with a wheel one earth-diameter thick. The innermost 9/10 for the stars remains
Diels–Tannery extrapolation with no numerical attestation.

---

## WHAT HELD, EXACTLY

- **√2 = 577/408.** The sutra text evaluates to it exactly; error 2.124×10⁻⁶,
  **5 correct decimal places** — scroll confirmed.
- **A new exact identity the scroll didn't have:** 577/408 is *precisely one
  Newton–Raphson step* (`x → x/2 + 1/x`) from 17/12, which is the same sutra
  minus its final term. Two steps gives 665857/470832 — the scroll's extended
  value, confirmed exactly. **This is an arithmetic identity and nothing more.**
  It says nothing about whether anyone in 800 BCE possessed an iterative method.
  Written down because it is true, flagged because it is seductive.
- **The enlargement rule works.** `7.5 × (1 + 2q/15) = 7.5 + q` verified exactly
  for q = 0…94. Minor correction: that's **94 enlargements across 95 sizes** —
  the scroll's "95 steps" counts sizes.
- **Plato's world-soul is exactly right.** Harmonic/arithmetic means of 1:2 give
  4/3 and 3/2; their ratio is exactly 9/8; a fourth minus two tones leaves
  exactly **256/243**; the span 1:27 is exactly four octaves plus the Pythagorean
  major sixth 27/16.
- **Five solids, all χ = 2.** Schläfli condition `(p−2)(q−2) < 4` yields exactly
  {3,3}, {3,4}, {3,5}, {4,3}, {5,3} and nothing else, each with V−E+F = 2.
- **Mānava beats Baudhāyana on circling the square:** −0.598% vs +1.725% area
  error. And the Mānava rule's implied π is **exactly 256/81** — the Rhind
  papyrus value. Arithmetic coincidence, logged as such, not as contact.

---

## THE ONE THAT NEEDS A FENCE AROUND IT

```
tower topology(T=1):  V=20  E=30  F=12  P=12  H=0  chi=2
dodecahedron:         V=20  E=30  F=12  P=12  H=0  chi=2
```

Plato's cosmic solid **is** the T=1 seed of the tower's Goldberg family. That is
a true statement about the tower's own `topology()` function and about Euclid
XIII — and it is exactly the kind of true statement that gets a scroll laughed
out of the room if it's allowed to carry weight.

**It carries none.** Two integers agreeing is not a result. The dodecahedron is
the T=1 Goldberg seed because Euler forces it, and Timaeus 55c reached for the
leftover fifth solid because there were only five. Both facts are EXACT. The
line between them is empty.

---

## THE KERNEL CAUGHT ITSELF

First run, check B6 (equilateral face → six 30-60-90 triangles) returned residual
**1.8×10⁻²**. That is not floating-point noise. I had used the wrong sub-triangle
— legs 1/4 and √3/4 instead of half-side 1/2 and inradius √3/6. Fixed; residual
now **2×10⁻⁶¹**, i.e. exact to working precision, and the 1:√3:2 leg ratio
verifies to 1.000000.

Logging it because a kernel that only ever confirms its author is not a kernel.

---

## OUT OF SCOPE FOR ANY KERNEL

Compute cannot settle these. Only sources can. Listed so they are never
mistaken for verified:

1. What Hesiod, Homer, Pherecydes, or Alcman actually wrote.
2. Whether the Derveni papyrus contains Phanes (Betegh vs. others).
3. Whether the Rhapsodic theogony preserves archaic material or Neoplatonic system.
4. The dating of Rigveda Maṇḍala 10.
5. Whether Baudhāyana predates Pythagoras.
6. Seidenberg's ritual-origin chronology vs. Robson's Plimpton 322 dating.
7. Whether the Orphic egg and Hiraṇyagarbha share an inheritance. *Typological
   similarity is not a computable quantity.*
8. Dumézil's trifunctionalism; Müller's solar mythology.
9. The translator and source language of the Dodoni *Vedes*.
10. Whether any of the above bears on the SOL tower. **It does not.**

---

## NEXT, IF YOU WANT IT

The two OPEN discrepancies (7.75 vs 7.5; 395 vs 396) are both settleable by a
single library trip: **Sen & Bag, *The Śulbasūtras* (INSA, 1983)**. Nothing else
in the file needs a source — it needs only re-running.

The buildable next artifact is the **falcon altar itself**: the caturaśra brick
layout is now fully specified and area-verified (200 bricks/layer, exact
inventory, two alternating tilings that provably cover identical area). That
renders as an actual constructible plan, not a diagram of one.

---

*P = 12. χ = 2. We do not trust. We verify by kernel.*
*Compression is cheap. Decompression is where the monkey lies to you.*
