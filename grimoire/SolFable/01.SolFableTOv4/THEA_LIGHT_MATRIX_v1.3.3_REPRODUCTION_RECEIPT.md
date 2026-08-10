# THEA Light Matrix v1.3.3 - Clean Reproduction Receipt

A separate-directory rebuild was performed from the staged bundle, without using the original `/mnt/data` output files.

## Replayed calculations

```text
frozen v1.3.2 checks        38 / 38 PASS
live Goldberg source         8 shell receipts
live LUCA source            34 / 34 locked
live LUCA price             44,185 EML calls
THE CROWD source tables     exact reproduction
```

## Stable mathematical payload

```text
1e6c813e7f6ba8e00587836d2bbbed90b5d7e8a1ee0ebba4343f17dbcf3e3cb7
```

## Deterministic build comparison

```text
LaTeX source SHA-256
5d4a7cec04cb0da6869ce0265664192b818c1f7b9db7d417f3b68c4c43d5659d

PDF SHA-256
404293d013e925ed5ccdd4b4813e02a83c3c0d2299fada1ba44929a5d7889464

PDF pages                         99
PDF paper                         A4
PDF preflight warnings             0
SOURCE_DATE_EPOCH         1786233600
```

The regenerated `.tex` matched byte for byte. With

```bash
SOURCE_DATE_EPOCH=1786233600 FORCE_SOURCE_DATE=1 TZ=UTC \
latexmk -pdf -interaction=nonstopmode -halt-on-error \
  THEA_LIGHT_MATRIX_v1.3.3_CALCULATION_TOWER.tex
```

the regenerated PDF also matched byte for byte.

The mathematical payload hash excludes filesystem paths and wall-clock data. The PDF uses the fixed epoch only to make document metadata deterministic; it does not enter any mathematical calculation.
