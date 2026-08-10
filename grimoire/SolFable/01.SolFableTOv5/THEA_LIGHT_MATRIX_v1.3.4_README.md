# THEA Light Matrix v1.3.4 - Rebuild

```bash
python build_light_matrix_v134_full.py
python /home/oai/skills/pdfs/scripts/pdf_preflight.py THEA_LIGHT_MATRIX_v1.3.4_FULL_CALCULATION_TOWER.pdf
```

The builder preserves v1.3.3, appends the Hopf-boundary control, compiles with a fixed `SOURCE_DATE_EPOCH`, normalizes the PDF trailer ID from the TeX hash, finalizes Markdown metadata, validates Markdown through Pandoc, writes receipts and hashes, and emits a deterministic ZIP.
