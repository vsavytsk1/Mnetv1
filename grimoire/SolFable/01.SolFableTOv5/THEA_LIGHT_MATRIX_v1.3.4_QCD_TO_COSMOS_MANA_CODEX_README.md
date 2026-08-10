# THEA Light Matrix v1.3.4 - QCD-to-Cosmos Mana Codex

This is the equation-dense technical companion to the short Level-12 Mana preprint. It follows the standard physics chain from local `SU(3)` color gauge symmetry through renormalization, hadrons, thermodynamics, stellar equations, compact objects, black holes, gravitational waves, galaxies, and FLRW cosmology. It then places the exact THEA Light Matrix core beside that chain with every proposed bridge explicitly typed.

## Frozen boundary

The volume uses six statuses:

- `STANDARD`: established mathematics or physics, re-derived where practical;
- `THEA-EXACT`: exact Light Matrix algebra or topology, without physical promotion;
- `COMPUTED`: reproduced by the supplied executable receipt;
- `BRIDGE-HYPOTHESIS`: a proposed map from mathematics to an observable;
- `OPEN`: a required derivation, limit, uncertainty, or test is missing;
- `CORRECTION`: a previously advertised arrow fails an invariant or provenance control.

The verifier certifies displayed identities and declared toy integrations. It does not certify a physical unification bridge.

## Main artifacts

- `THEA_LIGHT_MATRIX_v1.3.4_QCD_TO_COSMOS_MANA_CODEX.pdf` - 22-page A4 technical codex.
- `THEA_LIGHT_MATRIX_v1.3.4_QCD_TO_COSMOS_MANA_CODEX.tex` - compile-ready LaTeX source.
- `verify_qcd_to_cosmos_mana_v100.py` - 30-check SymPy/mpmath/NumPy/SciPy verifier.
- `generate_qcd_to_cosmos_mana_figures.py` - deterministic generator for seven figures.
- `build_qcd_to_cosmos_mana_v100.py` - portable build script.
- `qcd_to_cosmos_mana_v1.0.0_receipt.json` - machine-readable receipt.
- `qcd_to_cosmos_mana_v1.0.0_report.md` - human-readable check ledger.
- `THEA_LIGHT_MATRIX_v1.3.4_QCD_TO_COSMOS_DERIVATION_INDEX.md` - map of 48 derivation lanes.

## Rebuild

From the bundle directory:

```bash
python build_qcd_to_cosmos_mana_v100.py --root .
```

Required Python packages: `numpy`, `scipy`, `sympy`, `mpmath`, and `matplotlib`. The LaTeX build uses `latexmk` and pdfTeX.

## Core result of the receipt

```text
checks   30
passed   30
failed    0
```

The clean-directory replay produced byte-identical TeX, receipt, figures, and PDF.
