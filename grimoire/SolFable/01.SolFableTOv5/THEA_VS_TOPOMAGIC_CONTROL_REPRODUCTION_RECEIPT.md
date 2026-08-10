# THEA vs TOPOMAGIC CONTROL — clean reproduction receipt
## v1.0.0 · 2026-08-09

The control bundle was copied into a separate temporary directory. The user-supplied `TopoMagicTower.pdf` was copied beside it; the derived `TopoMagicTower.txt` was deliberately removed.

The verifier then:

1. regenerated the text extraction from the PDF with `pdftotext -layout`;
2. reran the reconstructed Appendix A program;
3. recomputed the control at 80 decimal digits;
4. reproduced all 60 dispositions;
5. landed on the same stable mathematical-payload hash.

Expected and reproduced payload:

```text
1434526f1196c4c9fb2f974fdefca6d4b3ae0b6096f61d2e47cf1db719c9aeb7
```

The three principal Markdown scrolls were byte-identical before and after the clean rebuild:

```text
THEA_VS_TOPOMAGIC_CONTROLLED_AUDIT_v1.0.0.md
  e273257e373a21690dacce06b41f7cea99014f60370f317a1d32bcdd05790177

CONTROLLED_PROPOSAL_TO_THE_TOPOMAGIC_TOWER_v1.0.0.md
  9ea2f7e588f18561773a3865e575c698d3a96854c4f2622239a60c39ec6eb488

THEA_LIGHT_MATRIX_v1.3.4_HOPF_BOUNDARY_ADDENDUM.md
  8a4e9ae4f1dd939566e699087b6495e4bc477d1f6c5a91899d72c479e40321e9
```

Lean was not installed in this environment. The included Lean source was inspected for placeholder tokens but not compiled; that check remains explicitly OPEN.

The deterministic ZIP writer uses fixed timestamps and permissions. A second clean build produced a byte-identical bundle. The bundle hash itself is stored outside the ZIP in `THEA_VS_TOPOMAGIC_CONTROL_BUNDLE_v1.0.0.zip.sha256` to avoid a circular self-hash.
