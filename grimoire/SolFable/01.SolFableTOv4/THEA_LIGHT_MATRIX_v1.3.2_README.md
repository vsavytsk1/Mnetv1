# THEA - The Light Matrix v1.3.2
## Full LaTeX Tower and Independent Mathematical Audit

This bundle is a new versioned artifact built from the seven supplied sources. It does not overwrite Light Matrix v1.3.1 or either frozen LUCA shell.

## Primary deliverables

- `THEA_LIGHT_MATRIX_v1.3.2_LATEX_TOWER.pdf` - 42-page A4 rendered tower.
- `THEA_LIGHT_MATRIX_v1.3.2_LATEX_TOWER.tex` - compile-ready LaTeX source.
- `THEA_LIGHT_MATRIX_v1.3.2_CHANGELOG.md` - corrections, preserved claims, and status changes.
- `THEA_LIGHT_MATRIX_v1.3.2_MANIFEST.sha256` - SHA-256 file manifest.

## Reproducibility receipts

- `verify_light_matrix_v132.py` - independent exact/symbolic/numerical audit.
- `light_matrix_v1.3.2_audit_receipt.json` - full machine-readable result.
- `light_matrix_v1.3.2_audit_report.md` - compact human-readable result.
- `verify_light_matrix_v131_live.js` - direct replay of the current HTML's Goldberg builder and Lanczos routine.
- `light_matrix_v1.3.1_live_kernel_receipt.json` - live shell/spectral output.
- `build_light_matrix_v132_tex.py` - deterministic LaTeX source builder.

## Audit result

- Checks: 38
- Passed: 38
- Failed: 0
- Stable mathematical payload SHA-256: `f883e2952f4698b6416ad13af7ec15adb60352120a2e656ba0403473574626ed`

A PASS does not mean every source sentence was preserved verbatim. Some checks establish a correction. Read the `status` and `result` fields together.

## Mathematical core preserved

The independent audit reproduces:

1. Euler's forced value `P=12` for closed trivalent pentagon/hexagon fullerenes.
2. The hexagonal norm `T=k^2+k*l+l^2`, closure determinant, metric similarity, composition, and multiplicativity.
3. The Fibonacci selector, its exact `T_n` recurrence and closed form, and projective convergence to `phi`.
4. The lifted four-mode integer matrix with characteristic polynomial
   `lambda^4 - 3 lambda^3 + 3 lambda - 1`
   and spectrum `{phi^2,1,-1,phi^-2}`.
5. The exact golden-ray angle
   `theta_phi = arctan(sqrt(15)-2 sqrt(3))`.
6. The exact C60 graph certificate, complete adjacency characteristic polynomial, minimum adjacency eigenvalue `-phi^2`, Fiedler quartic/radical, and low-band multiplicities.
7. The Klein icosahedral syzygy and its gradient equivariants.
8. The browser shell's live golden-selected Goldberg spectral receipt through `C17660`.

## Principal corrections

1. `T_{n+1}/T_n` alternates around `phi^2`; it does not increase monotonically.
2. Golden-selected shells are independently closed catalogue members, not a fixed exactly nested transform with linear multiplier `phi`.
3. `2*pi/(5*sqrt(3))` is an exact coefficient within a stated honeycomb-to-sphere matching calculation; convergence of a discrete graph family to it is not proved by that algebra.
4. The A2 root lattice and the SU(3) weight lattice are dual/commensurable hexagonal lattices with index three, not literally the same lattice under the standard normalization.
5. Random basin counts are finite numerical coverage, not an exact orbit-count theorem.
6. The original binary64 forward-error comparator rounded the exact integer before comparison. The corrected rational comparison finds the first nonzero error at level 39 and a maximum true relative error about `1.0189e-15` through level 159.
7. IEEE 754 binary256 has 237 significand bits, not a 256-bit mantissa.
8. LUCA/EML identities require a per-node domain and branch ledger. Point sampling is a numerical sieve, not a symbolic proof.
9. The live LUCA v0.2 regression contains 33 spiral nodes. The handoff scroll's published regression coefficients correspond to 32 points after excluding the initial constant `e`.
10. At finite `N=33`, the tested Vogel objective peaks near 137.6065 degrees rather than exactly at the golden angle 137.507764 degrees.

## Build

From a directory containing the bundle. The audit requires Python 3 with `numpy`, `sympy`, and `networkx`; the live replay requires Node.js; PDF generation requires a TeX Live installation with the packages listed below.

```bash
python verify_light_matrix_v132.py
node verify_light_matrix_v131_live.js
python build_light_matrix_v132_tex.py
pdflatex -interaction=nonstopmode -halt-on-error THEA_LIGHT_MATRIX_v1.3.2_LATEX_TOWER.tex
pdflatex -interaction=nonstopmode -halt-on-error THEA_LIGHT_MATRIX_v1.3.2_LATEX_TOWER.tex
pdflatex -interaction=nonstopmode -halt-on-error THEA_LIGHT_MATRIX_v1.3.2_LATEX_TOWER.tex
```

The three LaTeX passes settle the table of contents, figure list, cross-references, and page numbers. The document uses standard TeX Live packages including `amsmath`, `amssymb`, `mathtools`, `booktabs`, `longtable`, `tcolorbox`, `hyperref`, `graphicx`, `pdflscape`, and `enumitem`.

## Status grammar

- `EXACT` - follows from shown algebra, topology, integer arithmetic, or symbolic identity.
- `COMPUTED` - reproduced by a named finite algorithm at stated precision/depth.
- `DESIGN` - a mapping, tolerance, ordering, visualization, or benchmark convention.
- `HYPOTHESIS` - a physical interpretation still requiring discriminating evidence.
- `EXTERNAL/METAPHOR` - imported context or imagery that is not certified by this tower.
- `CORRECTION` / `REFUTED` - the audit changes or rejects a source formulation.

Target is not result. A theorem, a computed trend, a design mapping, and a physical claim remain different objects even when they share the same glyph.
