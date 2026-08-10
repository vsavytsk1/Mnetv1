# THEA Light Matrix v1.3.4 - Clean Reproduction Receipt

An independent replay was performed in `/tmp/thea_v134_clean`, not in the source output directory. The portable builder regenerated the v1.3.4 TeX, new-chapter sources, calculation index, and figures from the frozen parent and Hopf-control inputs. The stabilized auxiliary indexes were then used for the final deterministic LaTeX pass; the PDF trailer ID was normalized from the TeX hash. Markdown finalization, receipt generation, manifest generation, and ZIP creation were repeated in the clean directory.

```text
All compared artifacts byte-identical: PASS
Artifacts compared: 10
```

| artifact | byte-identical | SHA-256 |
|---|---:|---|
| `THEA_LIGHT_MATRIX_v1.3.4_FULL_CALCULATION_TOWER.tex` | PASS | `fbf4666f1e2e0dddfdb8ef73cd5f9c8807d08c340532ef5c2a1c32381397a495` |
| `THEA_LIGHT_MATRIX_v1.3.4_FULL_CALCULATION_TOWER.pdf` | PASS | `833f91997828b76c5bae3904a29adb557c9f1aadbf20d1bdf14d694cc08b97d8` |
| `THEA_LIGHT_MATRIX_v1.3.4_BOOKKEEPING.md` | PASS | `b1c86550aff7195e7069f13ed426084331c128e01594f168a600be954e01757d` |
| `THEA_LIGHT_MATRIX_v1.3.4_NEW_CHAPTERS.md` | PASS | `40d39c4f0396efdbedd3875e743ae4c568fbc002e5e9d31de5d50dfd809a6f3c` |
| `THEA_LIGHT_MATRIX_v1.3.4_NEW_CHAPTERS.tex` | PASS | `9cf8275365934f1e08b92c4adbca64ce9e8bac9c399b49eeca1af57c04f71b80` |
| `THEA_LIGHT_MATRIX_v1.3.4_CALCULATION_INDEX.md` | PASS | `4fe1b2de1db5b22aff09110c9f2d4057abc8372c4af3f8d5cb2c945dba23f520` |
| `light_matrix_v1.3.4_full_receipt.json` | PASS | `a01af959ed022a9f39dd2bdeb629184dab59b02a9d19e0faee664f27a7706ece` |
| `THEA_LIGHT_MATRIX_v1.3.4_BUILD_RECEIPT.md` | PASS | `fdec4a7b7e706cf8e82a38a3044d831892c4bacb89cacec7c0a534730cdce0de` |
| `THEA_LIGHT_MATRIX_v1.3.4_MANIFEST.sha256` | PASS | `b095bab8b987415a97813d37e0d724064b29e6923087b0cad431859d66fb91be` |
| `THEA_LIGHT_MATRIX_v1.3.4_FULL_BUNDLE.zip` | PASS | `7d17e73a2ac649725832c384bed567d73f04871d96c09f9628097b46c0ce50e5` |

The clean replay confirms that the generated TeX, normalized 212-page PDF, pure Markdown, calculation index, structured receipt, build receipt, manifest, and deterministic bundle do not depend on the output path.

Clean comparison JSON SHA-256:

```text
16ca3528fe8d66c9db5e515dcab00557c376449ff7015a2d02155271f9377276
```
