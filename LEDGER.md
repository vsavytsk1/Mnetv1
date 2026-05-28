# LEDGER — MachineNet Build Log
## Append-only. Never edit existing entries. One truth.

---

### L001 · 2026-05-28 · genesis_v8.1.html — First Full Kernel Build

**What:** `builder/build_genesis.py` takes `genesis_v7.5.html` as template.
Injects M1-M6 (goldberg_kernel, graph_axioms, sar_modular, ns_spectral, fractal_search, mnet_nanite).
Outputs `shell/genesis_v8.1.html` — exact v7.5 format, all modules live.

**Size:** 138KB | **Template:** genesis_v7.5 (45KB, 1185 lines)
**Modules:** GK · GA · SAR · NSS · FS · NANITE
**Minimal compute defaults:** zoom=50, spin=0.002, maxFaces=1000
**Live:** https://vsavytsk1.github.io/Mnetv1/shell/genesis_v8.1.html

**Why this matters:**
The builder now owns the canvas explorer format.
Every future genesis version is generated, not hand-written.
Swap any module → rebuild → new version. The paradigm is locked.

---

### L002 · 2026-05-28 · builder structure locked

**builder/ owns:**
- `build_holly7.py`     → `pack/holly7.html` (dashboard, all 7 modules)
- `build_genesis.py`    → `shell/genesis_vX.Y.html` (canvas explorer, all 6 modules)
- `build_warning.py`    → `shell/spooky_warning/warning_v2.0.html` (FMA intro)
- `rebuild_gate.py`     → `shell/gate/gate_v1.3.html` (gate with images)

**kernel/ owns (source of truth, never edited manually):**
- M1 goldberg_kernel.js   — C60, Goldberg sphere, refinement, invariants
- M2 graph_axioms.js      — P1-P7 axiom verification
- M3 sar_modular.js       — SAR-5 spectral proof (λ̃ = 0.1473)
- M4 ns_spectral.js       — NS flow spectral gap
- M5 fractal_search.js    — fractal architecture search + lock
- M6 mnet_nanite.js       — physics-driven LOD DAG
- M7 (math_tree_v5.0)     — sacred math tree engine (in tree/)

**Rule:** Touch kernel/ → rebuild everything. Builder is the only path to shell/.

---

### L003 � 2026-05-28 � eng_v1.0.html � Engineering Dashboard v1.0

**What:** uilder/build_eng_dashboard.py � graph_sandbox_v5.1 EXACT format.
Injects M1-M6. 6-button ENG LAUNCHER (replaces autopilot). Kernel status HUD.
CMD input. SEED/REFINE/SAR-5/NS/FRAC SEARCH buttons in bar. Log panel.

**Size:** 132KB | **Modules:** GK � GA � SAR � NSS � FS � NAN
**Live:** https://vsavytsk1.github.io/Mnetv1/shell/eng_v1.0.html
**Why:** The engineering dashboard IS the sandbox format. Builder owns it.
Buttons 1-6 only. More added one by one.
