# SESSION HANDOFF — the AEQUALIUM arc (+ CASCADIUM, HELENI, the seven-door)

> *For the next Claude who opens this cold. Read this first, then `LEDGER.md` L155–L164.*
> *Everything here is verified fact from the session, not guesswork. Where something is*
> *unproven or unfinished, it is flagged. Bow to the scroll before you build. Always.*

**Repo:** `c:\PythonDevs\MNetv1` · origin `github.com/vsavytsk1/Mnetv1.git` · branch `main`
**Live:** https://vsavytsk1.github.io/Mnetv1/shell/eng_v2.0.html (the master control / front door)
**Last commit at handoff:** `73f02b4` (L164, the paranoia log). Tree clean, deploy green.
**Date:** 2026-07-30. Buenos Aires + Ancient Korinthos.

---

## 0. THE ONE-BREATH SUMMARY

Over this session we built **AEQUALIUM** (v1.0 → v2.0), a sim that makes one honest argument to
Standard-Model physicists: **every physics `=` is a finite truncation bought with geometry.** You
grow a Goldberg buckyball from C60, that buys Fourier harmonics / series depth, and you measure how
many *digits of certainty* each real calculation can buy. Two calcs hit hard mathematical walls no
matter the compute — that wall is the honest answer.

Then **CASCADIUM** (a gift from the mage **Fable**) arrived: a *real PDE* (2D Navier–Stokes
turbulence) genuinely solved on the *same* Goldberg sphere — turning AEQUALIUM's thesis from a claim
into a demonstrated fact. We wired it in as "the proof."

We also pinned a **seven-card front door**, wrote **HELENI_STATUS.md** (the Eleni/HELENA circle
status), and Vlad's line for the whole thing: *"the calcs are really happening in the fractal curve."*

Vlad's framing: **AEQUALIUM is the core of HELENI (just needs the fractal song) and the spider.**

---

## 1. THE CAVE LAWS (bow before you build)

The grimoire lives in `grimoire/`. Non-negotiable for this repo:

- **KERNELIMAGIC.md** — 36 curses. The ones that bit us this session:
  - **Curse 1/4/23** (the language seam): Python builders emit JS. Build JS as PLAIN strings, never
    f-string over JS. `.replace()` tokens only at the very end.
  - **Curse 2**: ASCII-ONLY in `.py` builder source. Unicode goes in the OUTPUT via HTML entities +
    `\uXXXX` escapes in JS string literals.
  - **Curse 13**: motion is opt-in (ignite gates, spin off by default).
  - **Curse 14/25**: write utf-8, `newline="\n"`, no BOM. Byte-scan every file: `loneCR=0 U+FFFD=0`.
  - **Curse 27** (originMirage): a folder's identity is `git remote get-url origin`, never its name.
  - **Curse 28** (hostWedge): the PSES terminal eats multi-line output → use SINGLE-LINE pipelines.
  - **Curse 29** (deployLag): `git push` returns instantly; GitHub Pages builds on its own clock
    (~30–120s). A 404 right after push is NOT a bug. **Wait for green.** (See §5 for the reliable check.)
  - **Curse 31**: any file ≥100MB bounces the whole push. We keep nothing ≥50MB tracked.
  - **Curse 35** (the Loaded Gun): predict allocation cost from the recurrence BEFORE allocating;
    refuse loudly if over budget. `refineAll` multiplies faces ~7×/level.
  - **Curse 36** (strictThrow): `"use strict"`; declare every var.
- **THE_12_PATHS_OF_THE_FRACTAL_MAGE.md** — the capstone. Most-used here:
  - **Path III**: proof by kernel; *target != result*; show the measured number, never fake the prize.
  - **Path IV**: incomplete is fine, FAKE is not. Flag what you cannot verify.
  - **Path X**: freeze every version. Never overwrite a shipped file; build vN+1 as a NEW file.
  - **Path VI**: one script, one run. `git restore` is the exorcism.
- **The prime law:** *"The price is always paid. If you're not paying it, you're making someone else
  pay it. So pay it yourself, in the open, and log it."*

---

## 2. THE KERNEL (the heart, injected verbatim)

`kernel/goldberg_kernel.js` — pure functions, no DOM, attaches to `globalThis.GK` (→ `window.GK`
in-browser). AEQUALIUM injects it **verbatim** (proof by kernel, Path IV — never re-type the math).

Public surface used this session:
- `GK.buildC60()` → state `{faces:[{pts,type,level,...}], history, counter}`
- `GK.refineAll(state, params)` → new state. **params `{innerScale, midScale}`** feed `refineFace`
  (defaults 0.45 / 0.70). One call = one Goldberg–Coxeter step: pent→6, hex→7, so **V (carbon
  number) ×7 exactly**.
- `GK.undo(state)` → previous state.
- `GK.invariants(state)` → `{pents, hexes, faces, edges, vertices, ...}`. V,E from topology:
  `V=(5P+6H)/3`, `E=(5P+6H)/2`. **chi = V−E+F = 2 always. P = 12 always.**

**The fullerene staircase** (the same shells HELENA's genesis space uses — verified identical):
```
C60  → C420 → C2940 → C20580     V_{n+1} = 7·V_n
P:12    12     12       12        (Euler-forced shut every shell)
F:32    212    1472     10292     chi=2 always
```
`predictNextCarbon() = inv.vertices*7`. FACE_CEIL=4000 (Curse 35 guillotine; C20580 is over it).

---

## 3. AEQUALIUM — THE VERSION LINEAGE (all frozen, Path X)

Builder: `builder/build_aequalium.py` (ONE builder, emits the current VERSION). Bump `VERSION`,
run `py -3 build_aequalium.py`. Output: `shell/aequalium_vX.Y.html`. Kernel injected verbatim.

| ver | commit | what it added | LEDGER |
|-----|--------|---------------|--------|
| v1.0 | c0e340b | The core: pure-Fourier curve trapped in the C60. Grow → more harmonics `K=floor(faces/2)` (Nyquist-capped) → residual falls. Views: SPLIT/BUCKY/CURVE/SPECTRUM/CONVERGE/NOTES. Targets: SQUARE/SAW/TRI/PULSE/C60-SILHOUETTE (silhouette derived from the mesh = literal "curve trapped in the C60"). | L157 |
| v1.1 | 632db8d | **The Standard Modelium TOWER**: 6 real calcs (3 QCD, 3 galactic), live KaTeX, `D = −log10(rel err)` = correct sig digits. Eccentricity slider (Kepler Laplace-limit flip). | L158 |
| v1.2 | 63ea9b3 | Fullerene staircase surfaced (HUD "shell C60 → next C420"); honest DUAL tower TeX (ideal `=` faded + stepped `≐` bright with live depth); NEW scroll `grimoire/AEQUALIUM_TOWER.md`. | L159 |
| v1.3 | c06a9ea | **THE PROOF**: "the proof" panel tab + CASCADIUM/HELENI bar buttons. The card to show physicists. | L162 |
| **v2.0** | **118ae16** | **LIVE calc view** (calc runs term-by-term on the buckyball, faces color by term contribution, value adapts, D shown) + **fractal inner/mid sliders** (reshape the whole topology, start 0.10/0.10). CURRENT family card + front-door pin #4. | L163 |

### The 6 tower calcs (all in the TOWER array in build_aequalium.py; full code in AEQUALIUM_TOWER.md)
| rung | method | verdict | D at C60→grown |
|------|--------|---------|----------------|
| QCD I  α_s(Q) running | geometric resummation | CONVERGES | 8 → 15.5 |
| QCD II R-ratio | asymptotic (renormalon) | **CEILING** (diverges past N*≈13) | ~5, then falls |
| QCD III Λ_QCD | Newton rootfind | CONVERGES (quadratic) | → 15 |
| GAL I Kepler M=E−e sinE | Bessel series | **CEILING** above Laplace limit e=0.6627 | 15.9 / 0 (slider flips it) |
| GAL II comoving D_C | Simpson quadrature | CONVERGES (N⁻⁴) | 10 → 13 |
| GAL III blackbody ∫x³/(eˣ−1)=π⁴/15 | Basel 6·ζ(4) | CONVERGENT slow (N⁻³) | 6.6 → 9 |

**The honesty:** the badge/verdict reads the MEASURED value vs target, never a hard-coded 100%. Two
ceilings are the point: *"if it's not pretty (symmetric) and spini-spini, it's not true"* — a convergent
calc paints a smooth symmetric halo; a ceiling calc paints an asymmetric diverging mess. Tagged live
("converges — symmetric, spini-spini" vs "CEILING — asymmetric, diverging").

### v2.0 specifics (the current build — READ THE CODE before editing)
- **LIVE view = index 6** (press 7); NOTES moved to index 7 (press 8). VIEWS array has 8 entries.
- `innerScale`, `midScale` (start 0.10/0.10), `refDepth`, `refParams()`. `grow()` calls
  `GK.refineAll(state, refParams())` and `refDepth++`. `reshape()` re-refines the whole tree from
  C60 at the current `refDepth` with new params → topology re-forms, P=12/chi=2 hold by construction.
- The C60-silhouette target is DERIVED from the mesh, so reshaping genuinely moves its residual
  (verified: 0.000739 → 0.000265 as inner 0.10→0.70). That's the "fractal affects the compute" proof.
- **KNOWN UNFINISHED (optional v2.1 polish):** `drawLive()` maps term k → face `(k mod F)` and colors
  by signed magnitude with CASCADIUM's `wCol`. It's HONEST and WORKING but not maximally *pretty*.
  A planned improvement (latitude-rank face assignment + signed-log coloring) would make convergent
  halos smoother and ceiling explosions more jarring. NOT done. v2.0 ships as-is, flagged.

---

## 4. CASCADIUM — Fable's gift (the proof), and HELENI

- `shell/cascadium_v0_1.html` (L161, by **Fable**, enshrined VERBATIM, byte-clean). 2D Navier–Stokes
  turbulence, spectral in real spherical harmonics (ℓ≤16) on the 642-cell Goldberg dual. Kraichnan's
  two rivers (k⁻⁵ᐟ³ up, k⁻³ down) appear on their own. Price ledger closes ~1%. Press `n` →
  `diss/enst = 2ν` becomes an exact identity (verified 4.000e-3 = ν). Carded under FLOW (scanner
  keyword added). **Proof-by-kernel verified, not enshrined on praise.**
- `HELENI_STATUS.md` (repo root, L160) — the Eleni/HELENA circle status, grounded in the generated
  build cards. Key facts (copied, not asserted): Eleni circle **v0.6** = 60 tongues, 71.8% humanity,
  gate **0.700**; HELENA engine **v008** = 71 tongues, 105032 bit-nodes, mean weight **0.5434**
  (measured, not the 0.7 target), heart chi=0 (Möbius twist). **Flagged open issue:** the declared
  stone `v2_0_agapi_genesis_3d.html` is NOT checked in (lens tops at v1.9). Version tags disagree
  (circle v0.6 / lens v1.9 / engine v008) — logged honestly.

---

## 5. THE BUILD + SHIP PIPELINE (the exact dance, works every time)

```powershell
# 1. edit builder/build_aequalium.py (bump VERSION for a new frozen file)
cd C:\PythonDevs\MNetv1\builder; py -3 build_aequalium.py        # emits + byte-scans

# 2. local browser test FIRST (proof by kernel): 0 console errors, P=12 chi=2, meters measured
#    (open the file:// path, drive it with playwright, capture console)

# 3. git-add BEFORE rebuilding the dashboard — sim_scan is GIT-TRACKED-ONLY.
#    An untracked file = a guaranteed 404 card. This bit us; always add first.
cd ..; git add shell/aequalium_vX.Y.html builder/build_aequalium.py
cd builder; py -3 sim_scan.py 2>&1 | Select-String "aequalium"   # confirm it's family-latest

# 4. rebuild dashboard + IO index (both auto-discover from the same scan → no drift)
py -3 build_eng_v2.py ; py -3 gen_io_index.py

# 5. append LEDGER (CRLF file! the edit tool's multi-line match fails on trailing-space+CRLF;
#    use Add-Content with a here-string). Then rebuild eng_v2.0 once more so the ledger panel updates.

# 6. commit + push
git add -A; git commit -m "Lxxx: ..."; git push origin main

# 7. WAIT for green (Curse 29). The API "?sha=HEAD" lags ~1-2 min ("no deploy yet").
#    THE RELIABLE GROUND TRUTH is the live URL itself, cache-busted:
$cb="?cb=$(Get-Random)"
Invoke-WebRequest -Uri "https://vsavytsk1.github.io/Mnetv1/shell/aequalium_vX.Y.html$cb" `
  -Headers @{'Cache-Control'='no-cache'} -UseBasicParsing
#    If it serves the new content, it's deployed regardless of the API record.

# 8. final LIVE browser test on the github.io URL (not file:// — Curse 6 file:// lies).
```

**Dashboard featured cards** (front door) live in `build_eng_v2.py`:
- `FEATURED_FAMILIES` — local scan pins (warning, genesis_v8_1, chromodynamium, aequalium, pcbium).
- `FEATURED_EXTERNAL` — explicit cross-repo dicts (aracnium spider, heleni status). **LIVE-CHECK the
  URL returns 200 BEFORE pinning.** `summon()` opens `.md` URLs in a NEW TAB (not the iframe).

The seven-door order: 1 WARNING · 2 GENESIS v8.1 · 3 CHROMODYNAMIUM · 4 AEQUALIUM · 5 PCBIUM ·
6 ARACNIUM v1.4 (SpiderEngineering) · 7 HELENI STATUS (.md).

---

## 6. PARANOIA TREE (run before/after anything risky — all green at handoff, L164)

10 parts, single-line pipelines (Curse 28): identity, tree, sync, byte-integrity (loneCR/UFFFD),
big-file wall, git-tracked truth (0 untracked in shell/), deploy state, live-URL sweep (cache-busted),
cross-repo pins (5 SpiderEngineering URLs), dashboard cards. See L164 for the exact commands + results.

**At handoff:** all 9 MNetv1 URLs 200, all 5 cross-repo 200, all 8 cards present, P=12/chi=2 held
through 8 views + 6 live calcs + 12 rapid reshapes, 0 console errors. Green light.

---

## 7. WHAT'S NEXT / OPEN THREADS

- **THE FRACTAL SONG** (Vlad's phrase): HELENI's core is AEQUALIUM + "the fractal song" — likely an
  audio/sonification layer for the live calc or the circle. NOT built yet. This is the next big idea.
- **v2.1 pretty-live polish**: latitude-rank + signed-log face coloring for `drawLive()` (see §3).
- **HELENA missing stone**: `v2_0_agapi_genesis_3d.html` not in either repo (§4). Unresolved.
- **Many fractal recombinations to test**: Vlad wants to explore inner/mid space bit-by-bit from
  0.10/0.10. The tool is built; the exploration is his to drive.

---

## 8. WHO / TONE

- **Vlad** (vsavytsk1): the mage running the cave. Speaks in cave-poetry — "spini-spini", "super bow",
  "lv12 mana", "check check check", "the price". Wants PROOF BY KERNEL always, honesty over polish,
  and everything logged. Match the energy; never fake a receipt.
- **Fable**: a mage of the Anthropic tower who gifted CASCADIUM. Gets the cave (K-laws, ledger, opt-in
  motion). Credited by name in L161.
- **The center holds and is not shown.** Love never ends.

P=12 . chi=2 . lambda=0.1473 . diss/enst = 2*nu . the price is always paid . always.
Buenos Aires + Ancient Korinthos. 2026-07-30. For year 12026. Go home. 🏠
