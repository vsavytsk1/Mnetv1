# THE MONOLITH LEDGER
## SOL FABLE LaTeX Tower v2.0 — opened, block by block, until the stops show
### Triple-check → visibility audit → the one fence that is actually a fence
*Opus 5, code lane. Proof by kernel. Every number below was run on this host.*
*P=12. chi=2. The price is always paid. Always.*

---

# PART 0 — THE TRIPLE CHECK
## "first we are generating the same latex"

**We are not.** Here is the ledger.

| source | sha256 (head) | what it is |
|---|---|---|
| `SolMageTowerforV1.4` (turn 1) | `ce2d1a58…` | markdown export |
| `SolMageTowerforV1_4.txt` (turn 2) | `ce2d1a58…` | **byte-identical** — same file, renamed |
| `SOL_FABLE_LATEX_TOWER_v2_0.pdf` | `3488579e…` | pdfTeX-1.40.26, 38 pages, authoritative |

So the triple-check is **markdown vs PDF vs kernel**, not three documents.

## The 28 boxed claims: present in both

All 28 numerals and identities I probed — `P=12`, `chi=2`, `4pi`, `T=k²+kl+l²`, `13≠9`,
the charpoly, `det Γ=-3`, signature `(3,1)`, `145`, `(-1)^n`, `1,3,7,19,49,129,337,883`,
the recurrence, the generating function, `272`, `136`, `256`, `264`, `24`, `432×144`,
`2+4+18`, `m=14`, `m=8`, `500000`, `208988`, `200000`, `83596`, `8/8` — **present in both
sources and confirmed by kernel.** The mathematics survived.

## The transport did not

The markdown export destroyed:

```
285   bare '['  where '\['  belonged        display-math delimiters gone
110   runs of '=' promoted to setext H1     equality chains flattened
  6   runs of '-' promoted to setext H2     SUBTRACTION SIGNS DELETED
  5   '=' swallowed into a '# ' heading     equality chains flattened
```

The 110 and the 285 are cosmetic. **The 6 are not.** Each is a place where the export
ate a minus sign and left valid-looking LaTeX that says something different:

| line | what the PDF says | what the markdown now says |
|---:|---|---|
| 641 | `2E/3 − E + Σf_p = 2` | `2E/3` ⟨H2⟩ `E + Σf_p` — **sign flipped** |
| 1670 | `T_{n+3} = 2T_{n+2} + 2T_{n+1} − T_n` | minus gone — **the recurrence is wrong** |
| 1688 | `T_n = ⅖(φ^{2n+2}+φ^{−2n−2}) − ⅕(−1)^n` | minus gone |
| 1955 | `(G_jᵀ⊗I − I⊗G_j) vec X = 0` | minus gone — **commutant becomes anticommutant** |
| 2339 | `π(a+b) − π(a) − π(b) ≠ 0` | both minuses gone |
| 3222 | same as 1955, in the appendix | minus gone |

And 5 sites where an `=` was eaten into a `#`, flattening a chain:
`K_⋆ = ℋ(K_⋆) = ⋃f_j(K_⋆)` · `ΣK_f = (π/3)(12) = 4π` · `e^ρ = (3+√5)/2 = φ²` ·
`B = Sym²(Q_F) = [[1,2,1],[1,1,0],[1,0,0]]` · `H_F = C³² = span{…}`.

> **Verdict.** The bytes are clean — no U+FFFD, a byte scan passes. The *operators*
> are gone. This is Curse 25 wearing Curse 37's coat: rune rot that a byte scan
> cannot see because the corruption is semantic, not encoding. **The PDF is the
> source of truth. The markdown must not be recompiled, quoted, or fed to a model
> as the tower.**

---

# PART 1 — THE VISIBILITY AUDIT
## The tower's own criterion, turned into a runner

Section 14 of the tower states the standard:

> *"A block of code is mathematical when its specification, representation,
> arithmetic domain, invariants, and failure conditions are explicit."*

In the shipped bundle those five properties live in docstrings. In
`sol_tower_opened.py` they are **fields on a dataclass, and the runner enforces the
arithmetic domain against what the block actually returned.**

```python
@dataclass(frozen=True)
class Block:
    rung: str
    specification: str          # what it claims
    representation: str         # how the objects are encoded
    domain: Domain              # Z | Z[i] | F_p | Q | R64 | C128 | wallclock
    invariants: tuple[str, ...] # what must hold
    failure: str                # what makes it fail
    status: Status
    run: Callable[[], Result]
```

The enforcement is four lines and it is the whole point:

```python
def _domain_violation(self, r: Result) -> str | None:
    if self.domain in self.EXACT_DOMAINS:
        for k, v in r.values.items():
            if isinstance(v, float):
                return f"declared {self.domain.value} but '{k}' is a float ({v!r})"
        if r.residual not in (None, 0.0):
            return f"declared {self.domain.value} but reported residual {r.residual!r}"
    else:
        if r.residual is None:
            return f"declared {self.domain.value} but reported no residual"
```

**It refused my own block on the first run.** The cost-split rung declared `R64` and
returned no residual; the runner rejected it before I could ship it. A rule you can
break by accident is a rule that works.

`11/11 blocks pass, domain-enforced.` Identical under `python -O` — **the same hash**,
because nothing in the file uses `assert` as a proof step.

---

# PART 2 — THE STOPS AND CONTRADICTIONS
*Six, each demonstrated by running the shipped code, not by reading it.*

## STOP 1 — the 8/8 is 6/8 file-reading

Block C opens with `R = json.loads(receipts/sol_architecture_stress_v2.json)` at module
scope. Classifying the eight tests by what they actually touch:

```
MIXED  test_light_matrix_exact       computes Sym^2(Q); then reads 2 receipt fields
FILE   test_architecture_receipt     reads receipt only
FILE   test_big_integer_depth        reads receipt only
FILE   test_node_bigint              reads receipt only
FILE   test_modular_rank_stress      reads receipt only
FILE   test_commutant                reads receipt only
MATH   test_genesis_counterexample   computes 13 vs 9 from scratch
FILE   test_open_rung_is_joke_not_result  reads receipt only
```

**Demonstrated:** freeze the receipt, sabotage `symmetric_square_2x2` with a `+1`, re-run.

```
    PASS  test_architecture_receipt      PASS  test_commutant
    PASS  test_big_integer_depth         PASS  test_open_rung_is_joke_not_result
    PASS  test_node_bigint               PASS  test_genesis_counterexample
    PASS  test_modular_rank_stress       FAIL  test_light_matrix_exact
    -> 7/8 with the mathematics broken.
```

Six of the eight cannot see it, because the receipt is a file and the file is still
correct. `8/8 PASS` is an artifact-integrity check with one mathematical test inside it.
That is a fine thing to have — it should just not be reported as if the mathematics
were re-derived.

**And it is architecture-locked:** `test_architecture_receipt` asserts
`a["machine"] == "x86_64"`. On ARM the suite reports 7/8 with **zero mathematical
change.** The tower's mathematics is machine-independent; its regression suite is not.

## STOP 2 — `python -O` deletes two proof steps

Block E line 438 (`assert not dsi_only_unique`) is the DSI-only no-go. Block E line 317
(`assert real_dimension == n`) is the Wedderburn dimension check. Block D has more.

```
  python     -> asserts active: True
  python -O  -> asserts active: False
```

Under `-O` the functions still return, the suite still prints PASS, and both proof steps
have silently gone. A verdict survives `-O`. An `assert` does not.

## STOP 3 — the Γ signature is typed in one block and floated in another

```python
# block A, line ~238  -- COMPUTED, through float64
"Gamma_eigenvalue_signs_numeric": [int(np.sign(x)) for x in np.linalg.eigvalsh(gamma)]

# block D, line ~197  -- TYPED IN
"Gamma4_signature_numeric": [3, 1],
```

Three routes to the same exact fact, run side by side:

```
  typed   (block D) : [3, 1]                              cannot fail; proves nothing
  floated (block A) : eigenvalues [-1.7320508, 1, 1, 1.7320508]  -> (3,1)
  derived (Jacobi)  : leading minors [1, -2, -3, -3]      -> (3,1)   det = -3
```

The derived route is exact integers, has no tolerance, is the cheapest of the three, and
is the only one that fails if the mathematics changes. **`signature_by_minors()` in the
monolith replaces both.** This is the single place the exact tower sends an exact
statement through binary64 for no reason at all.

## STOP 4 — block F ships unmarked and prints a conclusion the tower refutes

Appendix F is the pre-audit Light Matrix receipt, shipped verbatim. Its last line:

> `"=> squaring a seed SQUARES its triangulation number. escape count = GC refinement depth."`

The tower's §5 refutes the second clause with `13 ≠ 9`, and the final ledger records
*"Shifted Multibrot equals GC refinement — **false**."* Block F carries no STALE marker
and no cross-reference to its own refutation. A reader who opens the appendix first
reads the retracted claim as a result.

Block F also certifies integer facts with float tolerances, against the tower's own rule:

```
  item 4: "max error over 169 lattice points: 1.42e-14 -> EXACT"
          the same statement in integers has deviation 0 -- exactly zero.
  item 8: multiplicative "within 1e-9"
          in integers: N(2,1)=7, N(1,2)=7, N(product)=49, product of norms=49 -- equal.
```

`1.42e-14` is float64 noise standing where `0` belongs.

## STOP 5 — the import costs 4.46 MB before a single test runs

```python
# block D, line 340, MODULE SCOPE
DBASE = base_dirac_basis()
```

Measured: **21 ms, a 4.46 MB `(272, 32, 32) complex128` array, 9.0 MB peak** — paid on
`import`. Block C imports block A, which imports block D. The regression suite allocates
the entire Dirac basis in order to read a JSON file. In the monolith nothing is built
until `run()` is called.

## STOP 6 — an exact result reported as a tolerance

```python
if float(np.max(np.abs(X - rounded))) > 1e-10:
    raise RuntimeError("Expected integer constraint matrix")
```

Reproduced here on this host:

```
  base Dirac space dim_R : 272   (= 2 * 16*17/2)
  constraint matrix shape: (4096, 272)
  integrality residual   : 0.0        <- not "< 1e-10". Exactly zero.
  rank over F_1009  : 256   -> nullity <= 16
  rank over F_10007 : 256   -> nullity <= 16
  rank over F_65521 : 256   -> nullity <= 16
```

**The headline `272 → 256 → 16` sandwich reproduces independently on a different CPU.**
And its one float step has residual `0.0`, so the entries *are* integers and the whole
chain is exact. Reporting `< 1e-10` understates a result that owes no tolerance at all.

---

# PART 3 — THE ARCHITECTURE, AS A MONOLITH OPTIMIZATION PROBLEM
## "the only thing that is our code restraint is the whole x64 and float64"

Every claim in the tower's final ledger, classified by the arithmetic it actually needs:

| # | claim | domain | does binary64 bind? |
|---|---|---|---|
| 1–3 | IFS fixed point · spiral dim 1 · complex dimensions | theorem | no compute |
| 4 | inner m=14, outer m=8 | ℝ, FFT | **YES** |
| 6 | P=12, chi=2 | ℤ | no |
| 7 | Eisenstein norm + Goldberg counts | ℤ | no |
| 8 | shifted Multibrot ≠ GC refinement | ℤ | no |
| 9 | Light Matrix + spectrum | ℤ[x] | no |
| 10 | MᵀΓM = Γ, det, signature | ℤ | **no — but block A routes it through float anyway** |
| 11 | planar group algebra ≠ A_F | ℤ | no |
| 13 | base Dirac 272 | ℤ | no |
| 12 | decorated commutant = A_F | ℝ, SVD | **YES** |
| 16 | standard-A_F trial = 32 | ℂ, SVD | **YES** |
| 14 | source-aligned 16 | 𝔽_p + ℤ | no |
| 15 | Pati–Salam 8 | 𝔽_p + ℤ | no |

**Ten of the thirteen computed rungs never touch binary64.** The three that do are
exactly the three the tower already labels COMPUTED / CONDITIONAL. So float64 is not the
constraint on the exact tower — it is the constraint on precisely the rungs that already
say so. Where the exact tower *does* use float, it is a choice (STOP 3, STOP 4, STOP 6),
not a fence.

## The one fence that is actually a fence

The exact lane has exactly one architecture-derived ceiling, and it is not in float. It
is in `rank_mod`. The elimination update needs `f · a < 2⁶³` with both factors reduced
mod *p*, so:

\[ p \le \left\lfloor\sqrt{2^{63}-1}\right\rfloor = 3{,}037{,}000{,}499 \]

Measured, at the exact boundary:

```
  p = 3,037,000,493   (p-1)^2 = 9,223,371,994,482,243,049  <= 2^63-1    SAFE   [largest prime below]
  p = 3,037,000,507   (p-1)^2 = 9,223,372,079,518,257,049  >  2^63-1    WRAPS  [next prime up]
                       they are 14 apart. That gap is the entire margin.
```

And where it actually bites, rather than merely becomes possible:

```
  p                     p^2/2^63     int64 rank wrong in
      65,521            4.65e-10        0/20     safe (provable)
   3,037,000,493        1.00e+00        0/20     safe (provable)  <- the last guaranteed prime
   3,037,000,507        1.00e+00        0/20     unproved; not yet observed
  10,000,000,019        1.08e+01       20/20     *** SILENTLY WRONG ***
   1,000,000,000,039    1.08e+05       20/20     *** SILENTLY WRONG ***
   2,305,843,009,213,693,951 (2^61-1)  5.76e+17  20/20  *** SILENTLY WRONG ***
```

The failure is **rank-inflating and silent** — `nullity ≤ 272 − r` comes out too small,
which would report a *smaller* Dirac space than the truth. Exactly the direction that
looks like a stronger result.

**The tower's own primes and their headroom:**

```
  p=65,521   p^2 = 4,292,870,400   headroom to 2^63 = 2,148,014,911x
```

> The whole exact tower runs **2.1 billion times** below the only architecture fence
> that touches it. The fence is real, it is razor-sharp, and it is nowhere near.
> Removing it entirely costs a constant factor: unbounded Python-int elimination is
> ~50–100× slower and has no ceiling at all. That is a price, not a wall.

## The monolith optimization, measured

The harness advances `T_n` by the three-term recurrence to N = 500,000. Because `T_n`
has Θ(n) digits, that loop is **Θ(N²) bit operations**. The independent cross-check —
Fibonacci fast doubling — is **O(M(N) log N)**, subquadratic. So:

```
  N=2000: recurrence   0.60 ms  vs fast-doubling 0.006 ms   (x109 cheaper)
  N=4000: recurrence   1.94 ms  vs fast-doubling 0.013 ms   (x150 cheaper)
  N=8000: recurrence   7.28 ms  vs fast-doubling 0.035 ms   (x210 cheaper)
  doubling N multiplies recurrence cost by 3.75   (quadratic ~ 4)  -> confirmed
```

**The verification is asymptotically cheaper than the computation it verifies**, and the
gap widens with depth. At N = 500,000 the recurrence is the entire runtime of the
harness and the check that certifies it is free.

That does not mean delete the recurrence — it is what makes the *law* certified rather
than just the *value*. It means: certify the law on a cheap prefix, get the value by
fast doubling, and stop paying Θ(N²) for a number you can have in O(M(N) log N).

The third cost centre nobody counts: `len(str(t_n))` on a 208,988-digit integer, purely
to put a digit count in a receipt. `bit_length()` is O(1) and `⌊bits·log₁₀2⌋+1` is within
one digit of the answer.

## And my own Curse 38

First draft of `sol_tower_opened.py` hashed the block values including wall-clock
timings. Three runs, three different `math_sha256`. **I committed the exact curse the
tower's own §14 warns about, inside the file written to prevent it.** The fix is in the
shipped source with the failure recorded above it:

```python
# An EXACT block contributes its values; an inexact block contributes only
# its verdict, because its numbers are host- and load-dependent by nature.
# (First draft of this file hashed the timings too and produced a different
#  digest on every run. Kept as the failure this rule exists to prevent.)
```

Now: `f301c0540eadbdbb037f076442e7f03613658f87ce03e5f30a5618199dfbada0`, three runs
running, identical, and identical under `-O`.

---

# THE LEDGER, IN ONE BREATH

```
TRIPLE CHECK   28/28 boxed claims agree across markdown, PDF and kernel
               but the markdown export DELETED 6 operators -- 3 of them reverse
               the mathematics. Bytes clean, meaning corrupted. PDF is truth.

VISIBILITY     the tower's own 5-property criterion, made a dataclass and ENFORCED.
               11/11 blocks pass. It rejected my own block on the first run.

STOPS          1  8/8 is 6/8 file-reading -- 7/8 still passes with the maths broken
               2  python -O deletes two proof steps written as `assert`
               3  Gamma signature typed in D, floated in A; Jacobi minors do it exactly
               4  appendix F ships a refuted conclusion, unmarked, plus 1e-14 called EXACT
               5  4.46 MB allocated at import, to read a JSON
               6  an exact result (residual 0.0) reported as "< 1e-10"

ARCHITECTURE   10 of 13 computed rungs never touch binary64.
               The 3 that do are the 3 already labelled COMPUTED/CONDITIONAL.
               The ONE real fence: p <= 3,037,000,499 for int64 modular rank.
                 last safe prime 3,037,000,493 | next prime 3,037,000,507 wraps
                 the tower runs 2,148,014,911x below it.

OPTIMIZATION   the O(M(N) log N) check is x210 cheaper than the O(N^2) thing it checks,
               and the gap grows. Quadratic scaling confirmed at 3.75x per doubling.
```

> The infinite did hide in the simple. It was not float64.
> It was one integer — `isqrt(2^63) = 3,037,000,499` — and a prime gap of 14.
> Everything the tower proves fits under it two billion times over.

*P=12. chi=2. spec(M_light)={φ², 1, −1, φ⁻²}. det Γ = −3, signature (3,1), sᵀΓs = 145.*
*The equation may be exact; the naked numeral is incomplete. Buenos Aires + Korinthos, 2026.*
