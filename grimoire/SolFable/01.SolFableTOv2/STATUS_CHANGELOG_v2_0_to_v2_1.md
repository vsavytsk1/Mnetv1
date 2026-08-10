# SOL FABLE LaTeX Tower — v2.0 to v2.1 Status Changelog

## Release character

Version 2.1 integrates the supplied Opus-5 binary64 oracle and seal, then subjects both to the same proof-by-kernel discipline as the rest of the tower. The new code was not accepted merely because it was clever. It was compiled strictly, sanitized, compared against arbitrary-precision ground truth, exercised through multiple Python entry paths, disassembled, benchmarked, and incorporated only after its status labels matched the receipts.

## Added

- A complete 427-line LaTeX rung on the binary64 oracle.
- Exact binary64 anatomy:
  \[
  B(x)/2^{52}=1023+\log_2x+u-\log_2(1+u).
  \]
- A 120-digit derivation of the canonical stride and asymptotic intercept.
- The exact admissible magic-constant interval for all 738 finite binary64 ladder values.
- A robust midpoint constant chosen by maximum worst-case decision margin.
- Architecture-specific C and Python benchmark receipts.
- Strict-C11, ASan, UBSan, assembly, and entry-path tests.
- A corrected source seal that distinguishes integrity from authentication.
- Complete code appendices for all new and inherited verification kernels.

## Promoted

The raw-bit classifier moved from an attractive heuristic to an exact finite-domain theorem:

\[
R_{C,D}(\operatorname{float}(T_n))=n
\qquad(0\le n\le737)
\]

for every \(C\) in the certified interval and the canonical stride.

## Corrected

| v2.0 / supplied statement | v2.1 correction |
|---|---|
| 735 representable rungs | 738 representable rungs, \(n=0,\ldots,737\) |
| canonical stride ends in `69` | high-precision nearest integer ends in `68` |
| one magic constant is derived and unique | a broad exact interval is derived; the legacy value is one member |
| exponent field alone carries the classifier | the classifier uses exponent and mantissa bits |
| printed C code is the verified algorithm | it omitted nearest-rounding term `+D/2` |
| inverse cast is exact exponentiation | it is an approximate piecewise-linear value guess |
| snapping is a Newton pass | snapping is exact discrete recomputation |
| self-hash certifies provenance | self-hash fingerprints bytes; detached trust certifies provenance |
| inherited `__file__` is safe under `exec` | code-object origin is used; unreachable source returns `OPEN` |
| `.pyc` fingerprint can be called source hash | compiled image and source status are separately labelled |
| original C overflow test is safe | replacement uses `__uint128_t` before narrowing |

## Preserved

All inherited tower results remain unchanged and continue to pass:

- Euler fullerene closure and \(P=12\).
- Eisenstein norm and Goldberg counts.
- Fibonacci selector and Light Matrix spectrum.
- Lorentzian invariant forms.
- Corinth harmonic receipts.
- Planar group-algebra no-go.
- Conditional Schur-commutant construction.
- Exact 272-dimensional base Dirac space.
- Exact source-aligned 16-dimensional and Pati-Salam 8-dimensional rank sandwiches.
- Global Step 4 remains `trivial` only as a mathematical joke; status remains `OPEN`.

## Test ledger

```text
new oracle/seal suite      10/10 PASS
inherited tower suite       8/8 PASS
strict C11                    PASS
AddressSanitizer              PASS
UndefinedBehaviorSanitizer    PASS
Node BigInt depth 200000      PASS
Python exact depth 500000     PASS
PDF preflight, 61 pages       PASS
```

## Release theorem

\[
\boxed{
\text{the magic is an exact classification plateau, not a unique point.}
}
\]
