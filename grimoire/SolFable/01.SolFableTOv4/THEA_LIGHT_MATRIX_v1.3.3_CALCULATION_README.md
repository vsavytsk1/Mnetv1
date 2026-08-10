# THEA Light Matrix v1.3.3 - Calculation-by-Calculation Tower

This version is a new frozen audit artifact built from the v1.3.2 LaTeX tower. It does not overwrite v1.3.1, v1.3.2, LUCA v0.1, or LUCA v0.2.

## Main deliverables

- `THEA_LIGHT_MATRIX_v1.3.3_CALCULATION_TOWER.pdf` - 99-page rendered A4 tower.
- `THEA_LIGHT_MATRIX_v1.3.3_CALCULATION_TOWER.tex` - compile-ready LaTeX source.
- `THEA_LIGHT_MATRIX_v1.3.3_CALCULATION_INDEX.md` - compact index of all dedicated calculation rungs.
- `light_matrix_v1.3.3_calculation_report.md` - human-readable audit result.
- `light_matrix_v1.3.3_calculation_receipt.json` - complete machine-readable receipt, including null distributions.

## What received its own rung

- **C01-C38:** topology, Goldberg closure algebra, Fibonacci selection, chirality, the four-mode light matrix, exact C60 spectrum, the conditional continuum calculation, SU(3)/A2 normalization, Klein forms, binary precision, branch-qualified EML identities, and the LUCA/Vogel null results.
- **E01-E35:** the EML definition, terminal 1, and every displayed LUCA v0.2 primitive, each with formula, source ancestry, chain size, worst measured digits, EML-call price, pass/fail state, and branch/domain boundary.
- **G01-G18:** every THE CROWD calculation: inventory, comparison price, transforms, trap table, original null, marginal z scores, global tier correction, shared-alphabet autopsy, source deduplication, cluster-preserving null, provenance collapse, limited 2026 mass re-pin, uncertainty propagation, Schwinger contrast, and the still-sealed spectral-dimension protocol.

## Reproduced results

- Frozen v1.3.2 audit: **38/38 passed**.
- Live Goldberg/Lanczos shell receipts: **8**.
- Live LUCA v0.2 non-axiomatic calculations: **34/34 locked**.
- LUCA verification price: **44,185 EML calls**.
- THE CROWD source tables: reproduced exactly from seed `20260809`.

## Statistical correction added in v1.3.3

The source's largest row is a marginal standardized excess of approximately `2.985`. Because five nested tiers were examined, v1.3.3 compares the real maximum with the maximum tier score of every null tower:

- exceedances: `43 / 2000`
- direct empirical global p: `0.0215`
- finite-Monte-Carlo plus-one estimate: `44 / 2001 = 0.021989...`
- Monte Carlo standard error: approximately `0.00324`
- Wilson 95% interval: approximately `[0.0160, 0.0288]`

The source's physics-only and seven-representative autopsies then give global p-values `0.0950` and `0.3270`. A cluster-preserving circular log-shift null gives `0.1090`; a stricter four-generator provenance collapse gives `0.2590`. No physical identification survives these dependence controls.

## Honest boundary

The W/H/top update is deliberately a **limited re-pin**, not a claim that all 89 constants have been re-certified. It tests the load-bearing electroweak nearest neighbours with the 2026 PDG values used in the audit. The pre-registered spectral-dimension calculation in `THE_CROWD.md` remains open because the named generation-5 graph and two independent estimators were not supplied or executed here.

## Rebuild

Requirements: Python 3, NumPy, SymPy, NetworkX, Node.js, and a LaTeX installation with `latexmk`, `tcolorbox`, `pdflscape`, `booktabs`, `longtable`, `hyperref`, and standard AMS packages.

```bash
python verify_light_matrix_v133_calculations.py
python build_light_matrix_v133_calculation_tower.py
SOURCE_DATE_EPOCH=1786233600 FORCE_SOURCE_DATE=1 TZ=UTC \
latexmk -pdf -interaction=nonstopmode -halt-on-error \
  THEA_LIGHT_MATRIX_v1.3.3_CALCULATION_TOWER.tex
```

The v1.3.3 verifier invokes the frozen v1.3.2 verifier and both live JavaScript source replays. The builder reads only files beside itself and does not contain a sandbox-specific absolute path. The fixed `SOURCE_DATE_EPOCH` makes the PDF metadata deterministic; a clean-directory rebuild reproduced the TeX and PDF byte for byte.

## Stable mathematical payload

```text
1e6c813e7f6ba8e00587836d2bbbed90b5d7e8a1ee0ebba4343f17dbcf3e3cb7
```
