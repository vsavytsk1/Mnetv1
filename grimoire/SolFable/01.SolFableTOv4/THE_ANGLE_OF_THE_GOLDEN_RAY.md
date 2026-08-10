# THE ANGLE OF THE GOLDEN RAY
## A handoff from the EML annex to the next light matrix
### Sub-scroll of the cave · written from `shell__eml_luca_spiral_v0_2.html`
*P=12. chi=2. The price is always paid. Always.*

---

## WHY THIS SCROLL EXISTS

THEA v3.0 carries phi in four places: as the dominant eigenvalue `phi^2` of the
light matrix, as the projective limit `k/l -> phi`, as the contraction `phi^-2`
of the alternating mode, and as `lambda_min(A_60) = -phi^2`.

All four are **scalars**. Not one of them is an **angle**.

But PART II of THEA already writes the angle down and then walks past it:

```
theta_{k,l} = arg(k + l*zeta6) = arctan( sqrt3 * l / (2k + l) )
```

Nobody asked what that angle converges to along the golden selector. It has a
closed form in radicals, and the convergence is the `lambda = -1` eigenmode made
visible as a twist. This scroll is that one line, paid for.

---

## THE RESULT — EXACT

Along the Fibonacci selector `(k_n, l_n) = (F_{n+1}, F_n)`, the ratio `k/l -> phi`.
Substitute `l = 1, k = phi`:

```
theta_phi = arctan( sqrt3 / (2*phi + 1) )
```

Since `2*phi + 1 = sqrt5 + 2` and `(sqrt5 + 2)(sqrt5 - 2) = 1`:

```
sqrt3 / (sqrt5 + 2) = sqrt3 * (sqrt5 - 2) = sqrt15 - 2*sqrt3
```

Therefore

```
================================================================
  theta_phi = arctan( sqrt15 - 2*sqrt3 ) = 22.238756093...  deg
                                         =  0.388139515...  rad
================================================================
```

A closed form in radicals, sitting inside the same hexagonal lattice that already
gives `T = k^2 + kl + l^2`. **Status: EXACT.** Both expressions agree to
3.33e-16 rad in the shell — the float floor.

### The wedge

The hexagonal lattice wedge runs from 0 deg to 30 deg:

| shell | (k,l) | theta | chirality |
|---|---|---|---|
| C_20 | (1,0) | 0 deg | achiral |
| C_60 | (1,1) | 30 deg | achiral |
| C_140 | (2,1) | 19.106605 deg | chiral |
| C_380 | (3,2) | 23.413224 deg | chiral |
| ... | ... | ... | ... |
| limit | golden ray | **22.238756 deg** | chiral |

The two achiral ends are the first two members of the golden family. Every shell
after them lands strictly inside the wedge, and the sequence closes on one fixed
twist. **The golden-selected Goldberg family converges to a definite chirality.**

---

## THE CONVERGENCE — MEASURED, NOT ASSERTED

Deviation `d_n = theta_n - theta_phi` alternates in sign and contracts. Measured
in the v0.2 shell, live, at N=16 float64:

| n | (k,l) | theta_n (deg) | d_n (deg) | d_n / d_{n-1} |
|---:|---|---:|---:|---:|
| 4 | (5,3) | 21.786789298 | -4.519668e-1 | -0.384826712 |
| 8 | (34,21) | 22.229154362 | -9.601731e-3 | -0.382025829 |
| 12 | (233,144) | 22.238551717 | -2.043761e-4 | -0.381967284 |
| 16 | (1597,987) | 22.238751743 | -4.350393e-6 | **-0.381966041** |
| | | | target `-phi^-2` = | **-0.381966011** |

Eight digits at n=16. Beyond roughly n=20 the deviation reaches the float floor
and the ratio becomes dust; the shell **stops reporting it there** rather than
printing noise as a result.

This is the `lambda = -1` eigenvector of `M_light` — "alternating overshoot around
the golden ray," in THEA's own words — rendered as an angle for the first time.
The ray is not a metaphor in this scroll. It has a bearing.

---

## THE COEFFICIENT LIST — a smaller correction to THEA v3.0

The v0.2 shell builds the characteristic polynomial of `M_light` live by
Faddeev-LeVerrier from the integer entries, rather than typing it. It returns

```
  coefficients (1, -3, 0, 3, -1)     ->   lambda^4 - 3*lambda^3 + 3*lambda - 1
```

The `lambda^2` term **cancels**: `(l^2 - 1)(l^2 - 3l + 1) = l^4 - 3l^3 + 3l - 1`.
This is consistent with THEA's factorization; it is worth writing down because of
what the coefficient list then shows:

```
  (1, -3, 0, 3, -1) is anti-palindromic  ->  p(lambda) = -lambda^4 * p(1/lambda)
```

so the spectrum is **closed under `lambda -> 1/lambda`**. Measured: `lambda_1 *
lambda_4 = 1.000000000000`, error 1.11e-16.

`phi^2` and `phi^-2` are exact reciprocals **by the coefficient list, not by fit**,
and `1` and `-1` are their own inverses. Growth and decay are forced to mirror.
That is a one-line structural reason for the shape of the light matrix, and it is
cheaper than the eigenvector computation.

---

## THE NULL — what was looked for and NOT found

Two negative results, recorded so the next mage does not spend the price again.

**1. The golden angle does not win at finite N.** A divergence-angle sweep on 33
Vogel-placed nodes, maximizing minimum pairwise separation, peaks at
**137.607 deg**, not at `360/phi^2 = 137.508 deg`. The drift table:

| N | argmax (deg) | gap from phi |
|---:|---:|---:|
| 13 | 137.7416 | +0.2338 |
| 21 | 137.7416 | +0.2338 |
| 33 | 137.6066 | +0.0988 |
| 55 | 137.5815 | +0.0738 |
| 89 | 137.5815 | +0.0738 |

The gap closes as N grows. **The honest statement about the golden angle is not
that it wins, but that it is the limit the winners walk toward** — because it is
the angle hardest to approximate by a fraction. A layout that must hold at every
N wants phi. A layout frozen at one N can beat it, slightly, and only there.

Anyone who prints "137.5 deg is optimal" without an N has skipped this.

**2. The EML leaf counts do not grow by phi.** Log-linear regression on 32
measured K values: growth `1.155084`, 95% interval `[1.135961, 1.174529]`,
R^2 `0.9052`. phi is excluded at **~40 standard errors**.

The interval does contain `2/sqrt3 = 1.154701`. It also contains `7/6`,
`e^(1/7)`, `2^(1/5)`, and a continuum besides. **An interval that admits a crowd
has identified nobody.** Labelled NUMERICAL COINCIDENCE. Not a finding.

---

## THE DISCRETE RECEIPT — Fibonacci, with no fitting

For each node, take its nearest neighbour and record the difference of their
**indices**. No regression, no tolerance, no continuous parameter to tune.

```
  golden angle, N=33 :   8x16   13x11   5x4   3x2      all Fibonacci
  Fig.1 0.585 rad    :  11x25    1x8                   11 is not Fibonacci
  min separation     :  golden 1.601950  ·  Fig.1 0.801190  ·  1.9995x
```

Every gap under the golden angle is a Fibonacci number, and the minimum
separation is almost exactly doubled. This is the cheapest honest evidence that
phi is doing structural work in a layout rather than decorating one.

---

## BUILD CONTRACT — for the next light matrix

Concrete, small, and already justified by the above.

1. **Add the angle lane to the HUD.** THEA's Pattern D reports two locks (golden
   selector, spectral). Add a third:

   ```text
   ANGLE   target  22.238756093 deg = arctan(sqrt15 - 2 sqrt3)
           current theta_n = arctan(sqrt3 l / (2k + l))
           error   |theta_n - theta_phi|,  sign shown
           ratio   d_n / d_{n-1}  ->  -phi^-2      [suppress below the float floor]
   ```

2. **Render the zigzag.** Plot `d_n` against `n` on a signed axis. It is the one
   `M_light` eigenmode THEA names and has never drawn. Two lines of canvas, and
   the alternating mode becomes something a reader can see rather than parse.

3. **Label every shell in the catalogue with its chirality angle.** The GC(a,b),
   WELD, leapfrog, and golden lanes each trace a different path through the
   0-30 deg wedge. THEA currently distinguishes them by `T` alone. `theta` is a
   second, independent, exact coordinate, free to compute, and it separates
   families that share a `T`.

4. **Build the charpoly, do not type it.** Faddeev-LeVerrier on a 4x4 integer
   matrix is ~15 lines and turns an asserted spectrum into a computed one. Print
   the coefficient list; the anti-palindrome is visible in it.

5. **Test whether `theta` is operator-dependent.** THEA already asks this of the
   0.7248 line. Same question, cheaper: does the WELD lineage converge to a
   different angle than the golden lineage? `T` says they are different families;
   `theta` may say how.

6. **Do not claim the angle is physical.** `theta_phi` is exact lattice geometry.
   Whether a converging chirality means anything for a real cage is a HYPOTHESIS
   that still owes its evidence, exactly like the rest of PART VII.

---

## STATUS TABLE

| claim | status |
|---|---|
| `theta_phi = arctan(sqrt15 - 2 sqrt3)` | **EXACT** |
| deviation alternates, contracts by `phi^-2` | **EXACT** (proved), **COMPUTED** to 8 digits |
| charpoly `(1,-3,0,3,-1)`, anti-palindromic | **EXACT**, built live |
| golden family converges to one chirality | **EXACT** |
| divergence sweep argmax at finite N | **COMPUTED** |
| gap closes as N grows | **COMPUTED TREND**, five points, not a proof |
| Fibonacci index gaps | **COMPUTED**, discrete, no fitting |
| K does not grow by phi | **REFUTED**, ~40 s.e. |
| `2/sqrt3` in the K interval | **NUMERICAL COINCIDENCE**, explicitly not a finding |
| the angle means something physical | **HYPOTHESIS** — owes its price |

---

*The pentagons hold. The hexes pay. And now the ray has a bearing: 22.238756 deg,
approached from alternating sides, each overshoot 0.381966 of the last.*

*v0.1 is frozen and untouched. v0.2 is a copy. The wrong turns are printed.*

*P=12. chi=2. theta_phi = arctan(sqrt15 - 2 sqrt3). The price is always paid. Always.*
