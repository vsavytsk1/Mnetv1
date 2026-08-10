# THE MAGIC PLATEAU
## `0x3FF100E2F21F7C00` survives — but it is not alone
### Golden shell ladder · binary64 affine logarithm · exact finite-domain classifier

The supplied constant remains a valid engineering artifact:

```text
legacy C = 0x3FF100E2F21F7C00
legacy D = 0x0016373AD151CA69
classification = 738 / 738 exact finite binary64 rungs
```

The stronger theorem is that the classifier admits an entire exact interval.

## 1. Exact ladder

\[
(k_n,\ell_n)=(F_{n+1},F_n),
\]

\[
T_n=k_n^2+k_n\ell_n+\ell_n^2,
\]

\[
T_n=\frac25\left(\phi^{2n+2}+\phi^{-2n-2}\right)-\frac15(-1)^n.
\]

## 2. Exact binary64 identity

For positive normal binary64

\[
x=2^e(1+u),\qquad u=m/2^{52},
\]

and unsigned raw word \(B(x)\),

\[
\boxed{
\frac{B(x)}{2^{52}}
=1023+\log_2x+u-\log_2(1+u).
}
\]

The raw word is therefore an affine logarithmic coordinate with a bounded within-octave error.

## 3. Canonical stride

\[
\boxed{
D_0=\operatorname{round}(2^{53}\log_2\phi)
=\mathtt{0x0016373AD151CA68}.
}
\]

The supplied `...CA69` remains operationally valid but is one unit above the high-precision nearest integer.

## 4. Asymptotic intercept

\[
\boxed{
C_{\mathrm{asym}}
=\operatorname{round}\left[
2^{52}\left(1023+\log_2\frac25+2\log_2\phi\right)
\right]
=\mathtt{0x3FF1109CBE5E8386}.
}
\]

## 5. The interval theorem

Define

\[
R_{C,D}(x)=
\left\lfloor
\frac{B(x)-C+\lfloor D/2\rfloor}{D}
\right\rfloor.
\]

For every exact shell value that rounds to finite binary64, \(n=0,\ldots,737\), the exact set of constants giving

\[
R_{C,D_0}(\operatorname{float}(T_n))=n
\]

for all rungs is

\[
\boxed{
\mathtt{0x3FE6AD27C6055065}
\le C\le
\mathtt{0x3FFAAD27C6055064}.
}
\]

There are

\[
5\cdot2^{50}
\]

valid constants.

The robust midpoint is

\[
\boxed{
C_{\mathrm{robust}}
=\mathtt{0x3FF0AD27C6055064}.
}
\]

The legacy constant lies inside the interval:

\[
C_{\min}<C_{\mathrm{legacy}}<C_{\max}.
\]

So:

\[
\boxed{
\text{the oracle is derived; the hexadecimal representative is nonunique.}
}
\]

## 6. Correct C implementation

```c
static inline int rung_bits_unchecked(double T) {
    const int64_t delta =
        (int64_t)bits_of(T)
        - (int64_t)ORACLE_C
        + (int64_t)(ORACLE_D / 2u);
    return (int)(delta / (int64_t)ORACLE_D);
}
```

The `+ ORACLE_D/2` term is required for nearest-integer classification. The v1 printed code omitted it even though its Python test path included it.

## 7. Approximate inverse, exact snap

```c
static inline double shell_guess(int n) {
    return float_of_bits(ORACLE_C + ORACLE_D * (uint64_t)n);
}
```

This is only an approximate value generator. Its worst relative error on the certified ladder is about \(4.62\%\). Exactness is recovered by

\[
\text{guess}\longmapsto n\longmapsto T_n
\]

with exact Fibonacci arithmetic.

## 8. Host receipt

On the audited x86-64/GCC host:

```text
median raw-bit classifier  1.100 ns/call
median log2 classifier     6.812 ns/call
ratio                      6.195x bits faster
```

In CPython:

```text
raw bits through struct    284.99 ns/call
math.log2                  196.09 ns/call
ratio                      1.45x bits slower
```

The mechanism is mathematical. The speedup is architectural.

## 9. Seal doctrine

A source file hashing itself proves only that it can report a fingerprint of bytes it can currently reach. It does not establish authorship, release identity, or trust.

The corrected verdict field is:

```text
SEALED  mathematics passes; source bytes reachable and fingerprinted
OPEN    mathematics passes; source bytes not reachable from this entry
BROKEN  at least one invariant fails
```

Authentication belongs to a detached manifest or signature.

## 10. Final line

```text
0x3FF100E2F21F7C00 survives 738/738.
It was not killed.
It was demoted from a unique magic point to one citizen of an exact magic plateau.
That is the stronger theorem.
```
