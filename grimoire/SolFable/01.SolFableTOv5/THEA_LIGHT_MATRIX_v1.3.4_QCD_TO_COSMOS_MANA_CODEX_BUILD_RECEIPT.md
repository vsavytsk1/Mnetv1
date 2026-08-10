# Build receipt - QCD-to-Cosmos Mana Codex

## Output

```text
Document                       THEA Light Matrix v1.3.4 - QCD-to-Cosmos Mana Codex
Page format                    A4
PDF pages                      22
PDF outline entries            81
Generated figures               7
Principal derivation lanes     48
Executable checks              30
Passed                         30
Failed                          0
```

## Mathematical audit

```text
STANDARD-EXACT                 16
STANDARD-COMPUTED               9
THEA-EXACT                      4
CONTROL-CORRECTION              1
```

Three corrections were made during the final equation audit before freezing the artifact:

1. For `D_mu = partial_mu - i g A_mu`, the gauge transformation carries `-(i/g)(partial_mu U)U^-1`, equivalently `+(i/g)U(partial_mu U^-1)`.
2. With `epsilon` as energy density and `Phi` dimensionless in `g_tt=-exp(2Phi)c^2`, stress-energy conservation is `dp/dr=-(epsilon+p) dPhi/dr`; the factors of `c` then reproduce the displayed TOV equation.
3. The stellar output map is explicitly TOV plus slow-rotation and tidal-response equations, rather than TOV alone.

The verifier includes explicit checks for the first two corrections and for the Gamow-peak stationary point.

## PDF validation

```text
Openable                       PASS
Encrypted                      no
Likely scanned                 no
Fonts embedded                 PASS
Form fields                    0
Overfull LaTeX boxes           0
Rendered pages                 22 / 22
Observed clipping              0
Observed overlaps              0
Broken glyphs                  0
```

Representative full-resolution pages inspected: title/status map, QCD gauge derivation, TOV and tidal sequence, Hopf/strong-CP control page, machine-receipt table, complete verifier listing, and bibliography/coda.

## Clean reproduction

A separate directory was populated only with the frozen TeX, verifier, figure generator, and builder. The complete build was rerun there. Results:

```text
TeX                            byte-identical
Machine receipt                byte-identical
PDF                            byte-identical
```

## Frozen hashes

```text
TeX
3a2343082ac8c5e54e15ab3dbd34382ddb9ce70b0cab0a80f4d6ebb8eb35f746

PDF
fd49f64303b581d697e5226bd90b71d87a8aad29b6af1c309924a23316040730

Machine receipt
6c84dd824dbd81fd3e7de3bc60fa41ed65305af3b14a65e2510146dcf1fce1d0
```

The artifact certifies its displayed identities and declared toy integrations. It does not certify a physical unification bridge.
