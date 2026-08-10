# SOL FABLE LaTeX Tower v2.1 — Binary64 Oracle Audit

## Scope

This audit reviews the four supplied Opus-5 artifacts:

- `sol_tower_sealed.py`
- `THE_MAGIC_CONSTANT.md`
- `magic_constant.py`
- `rung.c`

against the existing SOL FABLE LaTeX Tower v2.0. The goal is not to preserve a dramatic claim. The goal is to preserve every part that survives exact algebra, architecture-aware execution, sanitizer checks, and provenance tests.

## Verdict

The main engineering idea survives:

\[
T_n=F_{n+1}^2+F_{n+1}F_n+F_n^2
\]

grows almost geometrically, so its binary logarithm is almost affine in the rung index. For positive normal IEEE-754 binary64 values, the raw bit pattern is itself an exact piecewise-affine proxy for \(\log_2 x\). Consequently a rung classifier can be implemented as an integer affine map on the raw 64-bit word.

The strongest corrected result is not one unique hexadecimal number. It is an exact admissible interval:

\[
\boxed{
C\in[
\mathtt{0x3FE6AD27C6055065},
\mathtt{0x3FFAAD27C6055064}
]
}
\]

for the canonical stride

\[
\boxed{
D_0=\operatorname{round}(2^{53}\log_2\phi)
=\mathtt{0x0016373AD151CA68}.
}
\]

Every integer \(C\) in that interval classifies all 738 exact golden-ladder values that remain finite when rounded to binary64:

\[
0\le n\le737.
\]

The supplied constant

\[
\mathtt{0x3FF100E2F21F7C00}
\]

is a valid member of this plateau and returns 738/738 correct classifications. It is not the unique constant produced by asymptotic derivation.

## Exact binary64 identity

Write a positive normal binary64 number as

\[
x=2^e(1+u),\qquad u=\frac{m}{2^{52}},\qquad 0\le u<1.
\]

If \(B(x)\) is its unsigned 64-bit encoding, then

\[
B(x)=2^{52}(e+1023)+m,
\]

and therefore

\[
\boxed{
\frac{B(x)}{2^{52}}
=1023+\log_2x+\psi(u),
\qquad
\psi(u)=u-\log_2(1+u).
}
\]

Thus the raw word is not literally the logarithm. The exponent bits supply the octave and the fraction bits provide a linear interpolation within that octave. The corrected classifier consumes both.

The error term obeys

\[
-0.0860713320559343\ldots\le\psi(u)\le0.
\]

## Exact ladder identity

The golden shell sequence has the closed form

\[
T_n=\frac25\left(\phi^{2n+2}+\phi^{-2n-2}\right)-\frac15(-1)^n.
\]

Factoring the leading term gives

\[
T_n=\frac25\phi^{2n+2}(1+\delta_n),
\]

with

\[
\delta_n=\phi^{-4n-4}-\frac{(-1)^n}{2\phi^{2n+2}}.
\]

Combining the exact ladder with the exact binary64 identity yields

\[
\frac{B(T_n)}{2^{52}}
=1023+\log_2\frac25+(2n+2)\log_2\phi+\varepsilon_n,
\]

where the certified total error lies inside

\[
-0.152627064429807
<\varepsilon_n<
0.129922941086050.
\]

Half of one rung spacing is

\[
\log_2\phi=0.694241913630617\ldots,
\]

so nearest-rung classification has wide analytic slack.

## Canonical constants

A 120-digit Decimal derivation gives

\[
\boxed{
D_0=\operatorname{round}(2^{53}\log_2\phi)
=\mathtt{0x0016373AD151CA68}
}
\]

and

\[
\boxed{
C_{\mathrm{asym}}
=\operatorname{round}\left[
2^{52}\left(1023+\log_2\frac25+2\log_2\phi\right)
\right]
=\mathtt{0x3FF1109CBE5E8386}.
}
\]

The supplied script used `...CA69`; that is one raw-bit unit larger because binary64 `math.log2(phi)` was rounded before multiplication by \(2^{53}\). Both strides happen to classify the finite test ladder successfully with suitable constants, but the high-precision nearest integer ends in `68`.

## Exact plateau theorem

For the classifier

\[
R_{C,D}(x)
=\left\lfloor
\frac{B(x)-C+\lfloor D/2\rfloor}{D}
\right\rfloor,
\]

let \(b_n=B(\operatorname{float}(T_n))\) and \(h=\lfloor D/2\rfloor\). The condition \(R_{C,D}(T_n)=n\) is equivalent to

\[
b_n+h-(n+1)D+1\le C\le b_n+h-nD.
\]

Intersecting these integer intervals for all \(0\le n\le737\) gives

\[
C_{\min}=\mathtt{0x3FE6AD27C6055065},
\]

\[
C_{\max}=\mathtt{0x3FFAAD27C6055064}.
\]

The width is

\[
C_{\max}-C_{\min}+1=5\cdot2^{50}.
\]

The robust midpoint is

\[
\boxed{
C_{\mathrm{robust}}
=\mathtt{0x3FF0AD27C6055064}.
}
\]

It maximizes the minimum raw-bit decision distance to the two plateau walls for the chosen stride.

## Inverse cast

The inverse bit construction

\[
G_n=\unbits(C_{\mathrm{robust}}+nD_0)
\]

is a fast approximate value generator. It is not an exact exponential. Its worst relative value error over the certified binary64 ladder is

\[
4.616127575374\times10^{-2},
\]

at \(n=1\). However,

\[
R(G_n)=n
\]

for every certified rung, so the exact recovery chain is

\[
G_n\longmapsto n\longmapsto
F_{n+1}^2+F_{n+1}F_n+F_n^2.
\]

The second arrow is exact integer recomputation. It is a discrete snap, not a Newton iteration.

## Defects found and repaired

| Supplied claim or implementation | Audit result |
|---|---|
| `0x3FF100E2F21F7C00` is the uniquely derived constant | False as stated. It is a valid member of a wide exact plateau. |
| `D = ...CA69` is the high-precision nearest integer | Corrected to `...CA68`. |
| The finite binary64 ladder contains 735 values | Corrected to 738 values, \(n=0,\ldots,737\). |
| Only exponent bits matter | False. The full raw word is consumed; mantissa bits refine the index. |
| Printed C classifier matched the verified Python classifier | False. The printed C block omitted `+D/2`, while the tests used nearest rounding. Without the term it missed 718/738 cases under floor semantics. |
| Strict C11 source was portable | Repaired by defining `_POSIX_C_SOURCE 200809L` before headers. |
| Signed overflow was checked safely | False. The original expression overflowed before the sign test. The replacement uses `__uint128_t`. |
| `shell(n)` is exact | False. It is a piecewise-linear `exp2` guess; exactness comes only after integer recomputation. |
| Self-hash proves provenance | False. It is an integrity fingerprint. Authentication requires a trusted detached manifest or signature. |
| `exec` entry paths could be safely sealed | Repaired. Source-unreachable paths now return `OPEN`, never a fake source seal. |
| `.pyc` hash may be labelled source hash | Repaired. Compiled-image fingerprint and source status are separated. |
| Bytecode hash covered the full module | Repaired. It is computed after all functions exist and normalized against path dependence. |
| Reload remains idempotent | Repaired with a persistent module sentinel. |

## Architecture results

On the audited host:

- architecture: x86-64
- CPU allocation: 5 virtual cores
- CPU model: AMD EPYC 9V74
- compiler: GCC 14.2.0
- Python: CPython 3.13.5
- binary64: 53-bit significand

The strict C11 implementation passed:

- `-Wall -Wextra -Wpedantic`
- AddressSanitizer
- UndefinedBehaviorSanitizer
- 46/46 exact int64 ladder classifications
- 46/46 `log2` reference classifications

A seven-round host benchmark with \(10^8\) calls per round measured medians:

\[
1.100\ \mathrm{ns/call}
\]

for the raw-bit route and

\[
6.812\ \mathrm{ns/call}
\]

for the `log2` route, approximately \(6.20\times\) faster on this compiled host.

In CPython, the same mechanism was slower:

\[
284.99\ \mathrm{ns/call}
\]

for `struct.pack/unpack`, versus

\[
196.09\ \mathrm{ns/call}
\]

for `math.log2`. The speedup is therefore an implementation and architecture property, not a theorem of the mathematics.

## Regression result

The release closes with:

```text
ALL 10/10 new oracle/seal tests PASS
ALL 8/8 inherited tower tests PASS
strict C11 PASS
ASan + UBSan PASS
PDF preflight PASS, 61/61 pages rendered
```

## Final status

\[
\boxed{
\begin{aligned}
\text{binary64 affine-log mechanism}&:\ \mathsf{EXACT},\\
\text{all-738 classification}&:\ \mathsf{EXACT\ ON\ DECLARED\ DOMAIN},\\
\text{legacy constant}&:\ \mathsf{VALID\ PLATEAU\ MEMBER},\\
\text{unique magic number}&:\ \mathsf{REJECTED},\\
\text{inverse shell value}&:\ \mathsf{APPROXIMATE},\\
\text{exact snapped shell}&:\ \mathsf{EXACT},\\
\text{compiled speedup}&:\ \mathsf{COMPUTED\ HOST\ RECEIPT},\\
\text{self-hash authentication}&:\ \mathsf{REJECTED},\\
\text{detached-manifest integrity}&:\ \mathsf{RELEASE\ MECHANISM}.
\end{aligned}
}
\]

The artifact became stronger by losing the mystical uniqueness claim.
