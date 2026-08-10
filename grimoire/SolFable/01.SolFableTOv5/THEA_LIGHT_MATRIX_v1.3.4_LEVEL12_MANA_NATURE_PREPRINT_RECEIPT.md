# THEA Light Matrix v1.3.4 - Level-12 Mana Nature-style preprint receipt

- Format: A4, two columns, 9 pt article body
- Pages: 3
- Status: provisional research preprint; not peer reviewed; not affiliated with Nature Portfolio
- Source basis: frozen THEA Light Matrix v1.3.4 receipts and the controlled TopoMagic audit
- New fitted parameters: none
- New numerical optimization: none
- Render verification: all 3 pages rendered at 180 dpi and visually inspected
- PDF preflight: openable, unencrypted, non-scanned
- Reproducibility: two clean pdfLaTeX rebuilds with fixed SOURCE_DATE_EPOCH were byte-identical

## SHA-256


PDF: `d9bb0837278064c02debd360c8c408218b5fa4480c6039d5270d806b5929c8d2`

TeX: `b0158bd4dd41fa61dc3c14651d69ccd2060c596e567bd602aaa771dd8206433e`

Builder: `07a40c729346e8e2f97c689dbc09bdc7a6dfe9df778ce548623c7606bb78ef51`

## Build

```bash
python build_mana_nature_preprint.py
SOURCE_DATE_EPOCH=1786320000 pdflatex -interaction=nonstopmode -halt-on-error THEA_LIGHT_MATRIX_v1.3.4_LEVEL12_MANA_NATURE_PREPRINT.tex
SOURCE_DATE_EPOCH=1786320000 pdflatex -interaction=nonstopmode -halt-on-error THEA_LIGHT_MATRIX_v1.3.4_LEVEL12_MANA_NATURE_PREPRINT.tex
```

P=12. chi=2. This is weird. Good. Now make it falsifiable.
