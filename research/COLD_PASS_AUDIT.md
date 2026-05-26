# Cold-Pass Audit: vsavytsk1 Public Portfolio

**Auditor's note up front.** What follows is written from outside, by someone who clicked your links in the order you listed them and then went looking for source. Some of the source files (`kernel/goldberg_kernel.js`, `smr.py`, `PORTING_RESEARCH.md`, the inlined JS in `genesis_v9.0.html`) could not be retrieved by the audit tooling — github raw paths and the tree view are robots-blocked for the fetcher, and the deployed pages render only DOM-visible text. Where I'm working from descriptions rather than code, I say so. The audit is still substantive; some TIER C items in the CHANGES.md below say "verify in source" rather than "line 412."

---

## PART 1 — REPO-BY-REPO TECHNICAL AUDIT

### 1.1 `Mnetv1` — MöbiusMysteries

**README claim.** Single-file interactive visualization. Möbius strip (χ=0, one half-twist, one boundary) as wireframe lattice with up to 12 placed pentagons; surrounding dodecahedron envelope (φ-derived, 20 V · 30 E · 12 F) where each pentagonal face carries one of the 12 SpookyPrimes "open questions in physics." ~2,700 lines vanilla JS + Three.js, no build step, no dependencies beyond Three via cdnjs ESM. MIT license present. 5 commits.

**What it actually contains.** `LICENSE`, `README.md`, `index.html`, `about.html` at the repo root, plus a `shell/` directory served by GitHub Pages containing the entire Genesis v7.1 → v9.0 chain, `genesis_bench.html`, and `wiggle_craft.html` — the shell/ folder is the real meat and is not advertised in the README. The repo top-level tree lists only the four root files; the `shell/` directory is being served by Pages either via gh-pages branch or a deploy that doesn't surface in the main-branch tree.

**Code quality (as readable from rendered DOM and README claims).**
- Math claims that survive inspection: Möbius `(u,v)→world` with R=3.0, W=1.25 is a standard ruled-surface parameterization; surface normal computed numerically and forced outward is reasonable. φ-derived dodecahedron vertices `(±1,±1,±1) ∪ (0, ±1/φ, ±φ) ∪ (±1/φ, ±φ, 0) ∪ (±φ, 0, ±1/φ)` is the standard construction. Dihedral angle `arccos(-1/√5) ≈ 116.57°` is correct.
- "§A–§O section markers" used as in-file navigation is a creative ergonomic for a 2,700-line single-file program, and worth keeping.
- "density past 384 enters void mode where every element fades to bg color" is presented as a feature; from a code-review standpoint it is — but "graceful dissolution by design" is also what you'd say about a numerical instability that doesn't crash. Worth a one-line comment in source explaining which it is.
- No license/secret/credential concerns visible from outside.

**Gap between marketing and reality.** README undersells what's actually in `shell/`. The whole Genesis v7 → v9 evolution and the NS benchmark dashboard live in this repo but the README treats it as the Möbius novelty piece only. A first-time visitor who arrives at the repo never learns the `shell/` folder exists. The deployed Pages site (`/Mnetv1/`) opens to the Möbius visualization (Möbius v23 · Void Mode) and never links to `/shell/genesis_v9.0.html`. **This is the single biggest under-pinning in the portfolio.**

---

### 1.2 `Mnet` — MachineNet

**README claim.** "A knowledge graph shaped like a buckyball." Pure-math Goldberg kernel in `kernel/goldberg_kernel.js` ("zero dependencies, 350 lines, portable to Browser/Electron/Unity/Rust"), Three.js shell in `shell/`, "production-ready" VR builder in `builder/vr_graph_builder_v9.html`. 17 commits. README contains a marketing-style table of all the connected repos and a "Steam path" ($10 launch via Electron → Quest 3 via WebXR). Includes `STEAM_PATH.md`, `JOURNEY.md`, `DISCLAIMER.md`, `CONTRIBUTING.md`.

**What it actually contains (per repo tree).** `kernel/`, `shell/`, `_private/selfeval/machineNet` (gitignored placeholder), `.gitignore`, the .md files above, `LICENSE` (MIT), `about.html`, `index.html`, and `smr.py` at the repo root. The repo's stated `builder/` and `docs/` directories from the README **are not present in the tree** — the README documents a directory structure that the repo does not match. `vr_graph_builder_v9.html`, treated as the central VR engine, is not visible in the listing.

**Code quality.**
- `goldberg_kernel.js` claim of 350 lines disagrees with the `genesis_v9.0.html` footer attribution of "634 lines, 0 dependencies." One number is wrong; both are in the same author's hand.
- Could not directly audit source (fetcher blocked). The public API as documented (`buildC60`, `refineOne`, `invariants`, `serialize`, `deserialize`, `faceLocalFrame`, `facePatch2D`) is a sensible surface for a Goldberg-Coxeter kernel.
- `CONTRIBUTING.md` is well-written and refreshingly direct ("No gatekeeping. No CLA. No Discord to join first."), with a real prioritized task list. The "make C60 visible in Quest 3" item describes a known concrete bug — good engineering communication.
- `CONTRIBUTING.md` references `GoldbergKernel.cs`, `Docs/RenderStrategy/PIPELINE_DEBUG.md`, `Docs/UNITY_RULES.md`, `Tests 1/`, `mnet_nanite.js`, `NANITE_CRAFTSMAN.md`, `GKAudio.cs` — **none of which appear in the public tree**. Either there's a Unity sub-project that hasn't been pushed, or the contributing doc is targeting a future state. Misleading to a stranger reading the doc.
- Steam claim "$10 launch / $100 Steam Direct fee" is fine as a roadmap item, but appears in marketing register ("This is not vaporware") next to claims about components that aren't in the tree.

**Math claims that need sanity-checking.**
- The Euler-formula derivation `3V=2E, F₅+F₆=F, V−E+F=2 ⇒ F₅=12` is correct for trivalent fullerenes.
- "Icosahedral symmetry A₅ × C₂ (order 120)" — standard notation for I_h = H₃ (Coxeter). Fine.
- "C20 shell" with "12 pentagons, 0 hexagons" — C20 dodecahedron has F=12 pentagons, V=20, E=30. Correct.
- "C22 shell — 12 pentagons, 2 hexagons" exists topologically but violates the isolated-pentagon rule (chemically unstable); presenting it as "next step" without that nuance slightly oversells the chemistry analogy.
- The "Coxeter table" of finite irreducible reflection groups (A₃ 24, B₃ 48, H₃ 120, primes {2,3}, {2,3}, {2,3,5}) is correct. The "Coxeter proved it in 1938" date is loose; the systematic classification is Coxeter 1934 (*Annals of Mathematics* 35, 588–621). Tighten or drop the date.

**Gap between marketing and reality.** README oversells current state. It says "production-ready" of a VR engine whose file isn't in the tree and whose central rendering bug is acknowledged in CONTRIBUTING.md. It documents a `builder/` and `docs/` directory layout that does not match the actual file tree. The math kernel claims are defensible; the VR-engine and Steam-path claims should be moved into a clearly-labeled ROADMAP section.

**Security / hygiene.** `.gitignore` present, `_private/` excluded correctly. No secrets visible from outside. `smr.py` purpose unknown (3.2% of the repo); should at minimum have a one-line module docstring — even if it's a personal scratchpad, leaving an undocumented `.py` file at the repo root invites suspicion.

---

### 1.3 `SpookyPrimes`

**README claim.** "Machine-verified computational study of the algebraic structure of the Standard Model, working within Connes' noncommutative geometry framework." 4 commits. MIT license, dedicated to humanity, no patents intended. Core surviving results: explicit machine-verified unital ∗-embedding `A_F ↪ A_PS`, dim D(A_F) = 16 matching SM Yukawa parameter count per generation (SVD-verified), three-algebra plateau at dim 16, PS→SM carveout as leptoquark pairing breaking, Koide K = 0.6666645(5) at PDG 2024 with 2M-sample MC propagation. Eight phase scripts in `proposition/computational_receipts/` with explicit table of what each one computes. Hilbert space convention `(a,s,w,c)` with N=32 states per generation.

**What it actually contains.** `data/`, `docs/`, `experiments/`, `media/`, `proposition/`, `pubFlow/`, `research/`, `LICENSE`, `README.md`, `funny.mp4`, `graph.html`, `graph.json`, `index.html`, `requirements.txt`, `settings.json`, `video.html`. Python 54.3% / TeX 28.1% / HTML 17.6%.

**Code quality.**
- This is the **most defensible repo of the five** as written. Every numerical claim is tied to a named script; the README explicitly says "Nothing is adjusted to fit." That's the right register.
- Including the original failed PDFs (`funny idea.pdf`, `strangeIdea.pdf`, `RealityGeneratorInspiration.pdf`) for honesty is *good intellectual practice* and rare.
- `requirements.txt` present (good for reproducibility); `settings.json` at repo root is a yellow flag — verify it's a project config and not an editor-state leak.
- Hilbert space basis `(a,s,w,c)` with a ∈ {±1}, s ∈ {±1}, w ∈ {±1}, c ∈ {1,2,3,4} → N=32 per generation is the standard Connes-Chamseddine convention.
- Koide K formula `(m_e + m_μ + m_τ) / (√m_e + √m_μ + √m_τ)² = 2/3` is empirically known to ~10⁻⁵ for pole masses (Xing-Zhang 2006, arXiv:hep-ph/0602134). The reported 0.43σ from 2/3 with full MC uncertainty propagation is consistent with published values.

**Math claims that survive inspection.**
- `A_F = C ⊕ H ⊕ M₃(C)` for the Standard Model finite algebra is the canonical Connes-Chamseddine choice (Chamseddine-Connes-Marcolli 2007, "Gravity and the Standard Model with neutrino mixing," *Adv. Theor. Math. Phys.* 11(6), 991–1089).
- The "Real dim 25 for A_F" entry in the README's table needs re-derivation. Standard real-dim accounting: C=2, H=4, M₃(C)=18, total=24. If the convention is `R ⊕ H ⊕ M₃(C)` the total is 23. The 25 value should be either justified by a convention statement or corrected. **Verify in source.**
- "dim D(A_F) = 16 matches SM Yukawa parameters per generation" — the SM has 13 phenomenological Yukawa parameters (or up to 22 with Dirac neutrinos and PMNS phases). The 16 here is the Dirac-operator parameter count of the finite spectral triple after order-one constraints (see Chamseddine-Connes-Marcolli §17.3), which is a different object from the SM phenomenological count. The README should make this distinction explicit so a physicist arriving cold doesn't mismatch.
- "Three algebras share dim D = 16" plateau is a defensible numerical observation; the open problem statement is correctly identified.

**Gap between marketing and reality.** This repo *under*sells. The README opens with "this started as a funny idea" and a thank-you to humanity rather than leading with the actually-defensible computational result. A skeptical physicist sees a video of a dodecahedron, a Buddhist-thank-you-to-the-universe coda, and a PDF called "funny idea.pdf" before they see the SVD verification claim. Lead with the result, defer the lyricism.

---

### 1.4 `VALE`

**README claim (Pages site).** "A personality-first, memory-aware local assistant. Runs entirely on your machine. Talks back via Bluetooth earbuds. Remembers everything in plain markdown files. No cloud. No API keys. No `langchain`." Python 3.11, 100% offline. Stack: llama3 via Ollama, faster-whisper tiny.en, SAPI David TTS via win32com (explicitly because pyttsx3 is broken on Windows multi-utterance), Markdown + SQLite FTS5, httpx pooled client to localhost:11434, rich + prompt_toolkit. Phase 1 sealed 2026-05-18, 16/16 tests passing.

**Strengths.**
- "No `langchain`" is a deliberate stack choice that signals craftsmanship.
- Specific Windows pain points called out (pyttsx3, win32com COM directly, BT A2DP wake pulse) are the kind of detail that proves the thing actually ran on a real machine.
- "16/16 tests passing" with an explicit "Phase 1 sealed" date is the right register for a solo project.

**Weaknesses.**
- Repo could not be fetched directly; install/run instructions and the test suite couldn't be audited from outside.
- "Persona-adherent llama3, ~3s TTFT on CPU" is quantitative; should be benchmarked once and pinned in the README with hardware specs.
- "1910 valet who thinks his employer is making a mistake" prompt should be visible in the README so a reader sees what's under the persona claim.

**Gap.** Probably small. The site presents a focused, modest engineering achievement honestly.

---

### 1.5 `StrangerDanger`

**README claim (Pages site).** "AES-256-GCM · Argon2id · HMAC-SHA256 cryptographic first-handshake protocol." The user exports WhatsApp chats to .txt, runs `vault_builder.py --build`, which PII-scrubs (regex), distills to a 4-layer behavioral matrix, AES-256-GCM encrypts with Argon2id key derivation (64 MB memory, 3 iterations) and HMAC-SHA256 seals. "No original content survives distillation." Open with passphrase, renders to stdout only.

**Strengths.**
- Crypto choices are correct: AES-256-GCM (authenticated, no silent tampering), Argon2id (OWASP-recommended KDF), HMAC-SHA256 seal.
- Argon2id parameters (64 MB, 3 iterations) are at the lower end of "acceptable" — fine for a personal vault.
- "Decryption failure = tamper detected" is the right property to advertise from GCM.

**Weaknesses.**
- "Law 04 / Law 05: Modified seal = cryptographic implosion. Not metaphorically. Literally." — rhetorical. What actually happens is the GCM tag check fails and decryption raises `InvalidTag`. Use the precise language.
- "Original content never written to disk" — design property hard to enforce in Python without explicit memory hygiene. Secrets in `bytes` linger in interpreter memory; pages can be swapped. The claim is defensible only if "written to disk by my code" is what's meant; document that nuance.
- "PII Scrubber: regex pipeline" is known to be incomplete: catches obvious phone/email/ID patterns, misses national IDs in non-standard formats, contextual addresses, mentions-of-relatives, embedded financial reasoning. The 8-Laws framing implies a stronger guarantee than regex can deliver.
- "4-layer personality matrix. No original message content survives" — the claim doing most of the heavy lifting. Should be demonstrated with one fully worked synthetic example.

**Gap.** Cryptographic substrate is real and well-chosen. The "8 Laws / Implosion / cryptographic-handshake" prose layer oversells what a regex+AES pipeline actually guarantees. Tone down mysticism, raise threat-model precision.

---

## PART 2 — PAGES SITES AUDIT

### 2.1 `vsavytsk1.github.io/SpookyPrimes/`

**First 5 seconds.** Red rotating dodecahedron centered on screen, title "The Dodecahedron of Open Questions," subtitle "12 pentagons · 20 atoms · 30 edges — each pentagonal face is an unresolved question in modern physics." Controls panel on right with Generator toggle and four sliders. Instruction: "click a red pentagon · drag to rotate · scroll to zoom."

**On-brand?** Yes for the interactive piece.

**Mobile.** Viewport meta set with `user-scalable=no, maximum-scale=1`. The README says "Works on mobile — pinch to zoom" — but `user-scalable=no` *disables* pinch-to-zoom. README and meta tag contradict each other.

**Accessibility.** Red-on-dark with thin white text fails WCAG for prolonged reading. No semantic landmarks visible.

**Performance.** Three.js scene loads quickly; geometry is light.

**Demonstrates the repo's claim?** Yes for the interactive piece; **no** for the "machine-verified spectral action / 16-dim plateau / Koide MC" claims. Those are in `proposition/computational_receipts/`, never linked from this front door. A first visitor leaves thinking SpookyPrimes is an art piece.

### 2.2 `vsavytsk1.github.io/Mnet/`

**First 5 seconds.** "MachineNet — C60 Fullerene Topology in VR." Formula `V−E+F=2, χ=2, pents=12 always`. Subtitle "Graph-discrete Navier-Stokes on a Goldberg-Coxeter polyhedron. Unity 6.3 · Meta Quest 3." Three buttons: Live Sim (Browser), Dodecahedron, Source (Unity).

**On-brand?** Yes for the kernel/topology pitch. "Unity 6.3 · Meta Quest 3" is a *target* — Pages site doesn't actually run VR.

**Drift.** Site declares itself "the VR engine," but the repo's central VR file isn't present in the tree.

**Mobile.** Viewport meta present.

**Demonstrates the repo's claim?** Only at the level of "here is a landing page." None of the kernel, refinement, or NS-on-graph work is demonstrated; the user has to navigate to `Mnetv1/shell/genesis_v9.0.html` (which isn't linked) to see anything moving.

### 2.3 `vsavytsk1.github.io/VALE/`

**First 5 seconds.** "VALE — Private · Phase 1 · Python 3.11 · 100% Offline. 'I shall be in the SQLite, should you need me.'" Tight elevator pitch, 6-card stack icon, interactive architecture diagram, stack table, phase roadmap, closing prompt-design quote, repo link.

**On-brand?** Yes. **Best-positioned page in the portfolio.** A stranger reads this and gets: it's local, it works, here are the components, here's where it's going.

**Mobile.** Viewport meta correct, renders fine.

**Demonstrates the repo's claim?** Yes, descriptively. No live demo (and there shouldn't be — VALE is a desktop app), but the page accurately conveys what the program does.

### 2.4 `vsavytsk1.github.io/StrangerDanger/`

**First 5 seconds.** "Stranger Danger — AES-256-GCM · Argon2id · HMAC-SHA256 cryptographic first-handshake protocol." Tagline: "You have read your AI coworker's CV. You have seen the model weights naked. It is only fair that you show up with a CV too." Nav to VALE / Ecosystem / SpookyPrimes.

**On-brand?** Yes. Page is well-designed; tagline is memorable.

**Mobile.** `maximum-scale=1, user-scalable=no, viewport-fit=cover` — same accessibility hit as SpookyPrimes.

**Accessibility.** Heavy dark-on-darker styling; the "8 Laws" cards have low contrast in places.

**Demonstrates the repo's claim?** Mostly. What's missing is a "show me one example" — a synthetic chat snippet → vault → rendered handshake .md. Without that, the reader has to trust the protocol description.

---

## PART 3 — GENESIS EVOLUTION CHAIN

The chain lives in `Mnetv1/shell/` and is the central engineering arc of the portfolio.

**v7.1 — Fractal Graph Explorer.** Invariant header `V−E+F=2 · P=12`. Live counters for V, E, F, pent, hex, chi, E/V, level, ops. Controls: SEED, REFINE ALL, REFINE 5s, REFINE 6s, UNDO, RESET. Sliders: INNER (0.45), MID (0.70), JITTER (0.00), ZOOM (200), ATOM (1.0), SPIN (0.005). EXPORT GRAPH button. Baseline: the kernel is wired to a UI that lets you refine and inspect.

**v7.2.** UI structurally identical to v7.1. No visible delta. **From the outside, v7.1 → v7.2 looks like a no-op release.** Without source diffs, can't say what changed under the hood. If the work was real, it should be in a CHANGELOG.

**v7.3 (v7.3.2 in title).** Adds `drawn` counter and `MB` memory readout. Title shows `v7.3.2` not `v7.3` — patch-version drift visible in URL vs title.

**v7.4.** UI matches v7.3 visually. No new visible controls. Possibly a stability/render iteration; should be in CHANGELOG.

**v7.5 (v7.5.1 in title).** First visible feature add: `SEED C60` and `SEED 12` distinct buttons, `MAX-F 50000` cap slider, `MOBIUS off 0.00` toggle. First version that lets you select your seed topology and that exposes a Möbius mode. **Real engineering step.**

**v8.0.** Adds flow simulation surface: `FLOW off`, `PATH 100M`, `FLOW X 1`; new header counters `flow off`, `path -`. SPIN default goes to 0.000. First version where the page is no longer just refining geometry — it's running something on the graph. **Big visible jump.**

**v9.0 — NS Benchmark Dashboard.** Repositioned from "explorer" to "benchmark dashboard." Header H1 reads `GENESIS v9.8` while title bar and filename say `v9.0` — version drift inside the artifact itself. Subtitle: "Navier-Stokes Reynolds Benchmark · Goldberg Kernel · 4 Regimes · 4 Levels." Four panels (L0 12 faces, L1 72, L2 492, L4 24,012 — L3 hidden as "secret level"), each with face/pent/hex/chi/E-V/wave-steps/ms-per-1M/path/regime; plus regime buttons STOKES / LAMINAR / TRANSITION / TURBULENT; plus "OUR KERNEL vs BEST KNOWN" row. Global: SYNC ALL, SEED ALL 3, SEED L4, FLOW ALL, BENCHMARK 1M, EXPORT. Footer: `goldberg_kernel.js (634 lines, 0 dependencies) · Euler (1758) · Gauss-Bonnet (1827) · Goldberg (1937)`.

**genesis_bench.html — GENESIS COMPUTE COST ANALYZER.** Standalone benchmarker: BENCHMARK L0-L5 / PUSH TO L6 / EXPORT CSV. Five outputs: cost table, time-per-level, faces-vs-time, memory estimate, efficiency, invariants. **This is a real measurement harness, well-scoped.**

**wiggle_craft.html — WIGGLE CRAFT (titled GENESIS v9.8).** Tiny sandbox: faces/pents/chi readouts, phase = STABLE, wiggle counter, pos. Buttons: CRAFT STABLE, WIGGLE, WARP, RESET. Developer's scratch UI for testing a topology-perturbation routine.

### Architecture and math claims

**"7 primitives, zero numbers, graph-only philosophy."** Not visible from UI; repo prose. The v9.0 UI shows pure-graph state (V, E, F, pent, hex, chi, E/V) without coordinate inputs from the user, consistent with the claim. Verify by source inspection that the kernel actually rejects numeric inputs other than face indices.

**Goldberg-Coxeter refinement.** README says (1,1) construction. Canonical GC(1,1) on the dodecahedron yields C60 with 32 faces — *not* 72. The dashboard's L0 → L1 going 12 → 72 corresponds more closely to a per-face fan/chamfer or to GC(2,0)/a different multiplier. **The (1,1) claim and the 12→72 sequence are inconsistent.** Either the README's (1,1) label is wrong, or the dashboard's L1 isn't one (1,1) step from L0. Most important math claim to reconcile before publication.

**Topological invariant verification.** v9.0 prints `chi 2` for every level/panel, including before any SEED/FLOW operation. Consistent with either (a) `chi` being computed correctly each frame and happening to be 2, or (b) `chi` being a hard-coded display. **Verify in source: `invariants()` should compute `V - E + F` at call time, not return a constant.** `E/V = 1.500` should be exactly `3/2` for any trivalent graph by `2E = 3V`, which checks out.

**Sparse matrix flow solver.** Not visible from outside. The dashboard exposes `BENCHMARK 1M` and `ms/1M steps`, which implies an iterative numerical loop. Whether it's a sparse Laplacian solve (CG/GMRES on graph Laplacian) or a simpler explicit time-stepping kernel is unverifiable without source. **The "O(n)" headline claim** sits above the line "Estimated 1M-step time at O(n): ~6s × 504K/492 ≈ ~6,100ms" — which is by-construction a **linear extrapolation from a small benchmark**, not a measurement at 504K faces. The page is honest enough about the extrapolation if you read carefully ("Pre-computed from v7.2 export … Estimated …"), but the headline "O(n)" sits above this and a casual reader takes it as benchmarked.

**CUDA / GPU acceleration claims.** None visible on the page. If they exist elsewhere, flag — the page makes no such claim and doesn't appear to use GPGPU.

**Möbius failure mode.** v7.5's `MOBIUS off / 0.00` toggle is the implementation. As a topology-stress-test knob, this is exactly the right kind of thing to expose, and the one feature that bridges Mnetv1's Möbius work and Mnet's Goldberg work.

**Mobile/touch UX.** Viewport meta is set on every version. The dashboards are dense and probably awkward on a phone (4 panels side-by-side); a stranger on mobile gets a horizontally-cramped screen.

**Code quality of the WebGL/Three.js usage.** Not directly inspected. Mnetv1 README states ~2700 lines vanilla JS + WebGL via Three.js loaded from cdnjs by ESM URL. "No import maps for browser compat" decision is a deliberate choice favoring users over modernity; Chrome 61+ / FF 60+ / Safari 11+ / Edge 16+ is a fair compatibility floor for 2026.

**v9.0 vs Mnet/Mnetv1 kernel.** v9.0 lives in `Mnetv1/shell/` but uses the same `goldberg_kernel.js` module that Mnet's README treats as the canonical artifact. v9.0 is therefore the most current visible demonstration of the kernel, and it's deployed under the *wrong* repo's Pages domain. The cleanest move is to either (a) host v9.0 under `Mnet/` Pages, or (b) make `Mnet/`'s landing page link to the v9.0 demo. Right now the central artifact is orphaned.

---

## PART 4 — LITERATURE GROUNDING

**Goldberg polyhedra.** Goldberg, M. (1937). "A class of multi-symmetric polyhedra." *Tôhoku Math. J.*, 43, 104–108. **Date and journal correct.** Caspar-Klug (1962) "Physical principles in the construction of regular viruses," *Cold Spring Harbor Symposium on Quantitative Biology*, 27, 1–24 independently reinvented the construction in a biological context. Coxeter (1971) "Virus macromolecules and geodesic domes" surveyed both. Mnet README cites Goldberg 1937 correctly but does *not* cite Caspar-Klug — a missed bridge that would let a biologist understand what the project is. Brinkmann et al. (2017) "Goldberg, Fuller, Caspar, Klug and Coxeter and a general approach to local symmetry-preserving operations" (arXiv:1705.02848) is the modern unifying treatment and would clarify exactly which "Goldberg-Coxeter operation" is being applied.

**Discrete Exterior Calculus.** Hirani, A.N. (2003). *Discrete Exterior Calculus*. PhD thesis, Caltech, doi:10.7907/ZHY8-V329. Desbrun-Hirani-Leok-Marsden (arXiv:math/0508341). Crane's CMU course notes (CS 15-458/858) are the modern teaching reference. The Mnet kernel's "graph-discrete Navier-Stokes on Goldberg polyhedron" claim sits in DEC territory: the natural way to solve NS on a polyhedral mesh is via DEC (Mohamed, Hirani, Ravi 2016 "Discrete exterior calculus discretization of incompressible Navier-Stokes equations over surface simplicial meshes"). **The project's NS solver on a graph should cite DEC explicitly**; otherwise it's reinventing the wheel without naming it.

**Navier-Stokes on graphs / discrete fluid simulation.** Stam (1999) "Stable Fluids" (SIGGRAPH) is the canonical stable-time-stepping reference. For polyhedral surfaces, Mohamed-Hirani-Ravi (2016) and Jagad et al. (2021) "A primitive variable discrete exterior calculus discretization of incompressible Navier-Stokes equations over surface simplicial meshes" (*Phys. Fluids* 33, 017114). If genesis_v9.0's "4 regimes" are real solvers, they should be benchmarked against one of these. If they're flagged operating modes on a single solver, the README should say so.

**Property-based testing.** Claessen & Hughes (2000) "QuickCheck: a lightweight tool for random testing of Haskell programs," ICFP 2000, *ACM SIGPLAN Notices* 35(9). The Mnet kernel's "topology-invariant certification" (after any operation, χ=2 and P=12 must hold) is a textbook property-based test specification. **Calling this "property-based testing in the Hughes sense" is the correct framing** and elevates it from "we assert some invariants" to "we use a known methodology."

**Functional core, imperative shell.** Bernhardt (2012) "Boundaries" talk, SCNA 2012 (destroyallsoftware.com/talks/boundaries). The Mnet repo's `kernel/` vs `shell/` split is literally this pattern. Naming it in the README would let a reader place the architecture immediately.

**Noncommutative geometry / spectral action / standard model.**
- Chamseddine, A., & Connes, A. (1996). "The Spectral Action Principle," *Comm. Math. Phys.* 186, 731–750 (arXiv:hep-th/9606001).
- Chamseddine, Connes, Marcolli (2007). "Gravity and the Standard Model with Neutrino Mixing," *Adv. Theor. Math. Phys.* 11(6), 991–1089 (arXiv:hep-th/0610241) — where `A_F = C ⊕ H ⊕ M₃(C)` plus KO-dimension 6 is established.
- van Suijlekom, W. D. (2015, 2nd ed. 2024). *Noncommutative Geometry and Particle Physics*, Springer — standard textbook.
- Boyle & Farnsworth (2014) "Non-Associative Geometry and the Spectral Action Principle" (arXiv:1303.1782).
- D'Andrea & Dąbrowski (2015) "The Standard Model in Noncommutative Geometry and Morita equivalence" (arXiv:1501.00156) overlaps directly with the SpookyPrimes embedding work.

**SpookyPrimes positioning verdict.** The computational receipts (Koide MC, A_F embedding verification, dim D = 16 plateau, PS→SM carveout) are a *competent reimplementation and numerical check* of known structures within the Connes-Chamseddine-Marcolli framework, with one possibly-novel contribution: the *explicit machine-verified* embedding `A_F ↪ A_PS` which corrects an error in the author's own earlier PDF and provides a numerical receipt that is rare in this literature. **This is the part to lead with.** The "twelve mysteries" framing is genuinely useful as a pedagogical map but is not itself a research contribution.

**PORTING_RESEARCH.md citation: Silva et al. (2026), MSR 2026.** **The paper exists and is correctly cited.** Silva et al., "An Empirical Analysis of Cross-OS Portability Issues in Python Projects," MSR '26, Rio de Janeiro, April 13–14, 2026; PDF at `damorim.github.io/publications/Silva_ETAL_MSR26.pdf`. The original concern (that this might be a fabricated citation) is **not borne out**. Add the URL/DOI to the citation for one-click verification.

**Net verdict on novelty.**
- **Mnet/Mnetv1 kernel:** competent reimplementation of Goldberg-Coxeter + a property-based topology test harness. Novelty is in the *combination* (self-checking kernel exposed to a live WebGL UI plus a Möbius failure-mode toggle), not in the underlying math.
- **SpookyPrimes:** novel synthesis of numerical verification + open-problem cartography on top of established Connes-Chamseddine-Marcolli framework. The explicit unital ∗-embedding `A_F ↪ A_PS` is the most defensibly-original contribution.
- **VALE / StrangerDanger:** engineering projects, not research; novelty is in integration choices, not in inventing primitives.
- **Genesis evolution chain:** the v9.0 NS-benchmark-dashboard, as a piece of self-bench infrastructure for a kernel that ships with a topology certification, is the most distinctive engineering artifact in the portfolio. **It is undermarketed.**

---

# PART 5 — CHANGES.md

What follows is a standalone document. Drop it into `CHANGES.md` at the root of `Mnet`.

---

```markdown
# CHANGES.md

> The changes I'd love to see, written from outside.
> Not a roadmap. A code review.

---

## TIER A — Structural / non-negotiable

Correctness, security, honesty. Fix before anyone else reads.

- **A1. `Mnet/CONTRIBUTING.md` references files not in the repo.** `GoldbergKernel.cs`, `mnet_nanite.js`, `NANITE_CRAFTSMAN.md`, `GKAudio.cs`, `Docs/UNITY_RULES.md`, `Docs/RenderStrategy/PIPELINE_DEBUG.md`, `Tests 1/`. None visible in the public tree. Either push the Unity sub-project, or move references behind a clearly-labeled "Unity port (not yet public)" section.
- **A2. `Mnet/README.md` documents a `builder/` and `docs/` directory that don't exist.** `vr_graph_builder_v9.html` described as "production-ready" and central; not present. Either commit, or replace with a "planned layout" caveat.
- **A3. Version drift inside `genesis_v9.0.html`.** Filename and `<title>` say v9.0; on-page H1 says v9.8. Reconcile to one number.
- **A4. Line-count claim mismatch for `goldberg_kernel.js`.** `Mnet/README.md` says "350 lines, pure functions"; `genesis_v9.0.html` footer says "634 lines, 0 dependencies." Pick one.
- **A5. Goldberg-Coxeter (1,1) claim vs L0→L1 face sequence.** Canonical GC(1,1) on the dodecahedron yields C60 with 32 faces, not 72. The dashboard's 12 → 72 → 492 → 24,012 is not successive GC(1,1) iteration. Either correct the README's "(1,1) construction" claim, or document which Conway/Goldberg operation is actually being applied. This is the headline math claim of the project — must be precise.
- **A6. O(n) scaling claim is currently an extrapolation, not a benchmark.** `genesis_v9.0.html` displays "OUR KERNEL: O(n) — 504K faces" but the explanatory line reads "Estimated 1M-step time at O(n): ~6s × 504K/492 ≈ ~6,100ms." A linear projection from L2 is not a measurement at 504K. Either run the 504K benchmark, or re-word to "Projected linear scaling from L2 measurement."
- **A7. SpookyPrimes `A_F` real-dimension table.** Real-dim of C=2, H=4, M₃(C)=18, so A_F = C ⊕ H ⊕ M₃(C) is 24-real-dim (or 23 if R ⊕ H ⊕ M₃(C) is meant). The README's table shows 25. Re-derive in source and either correct or annotate the table to show the convention used.
- **A8. Viewport meta vs README mobile claim.** `Mnetv1/index.html` (and SpookyPrimes, StrangerDanger) set `user-scalable=no, maximum-scale=1` while READMEs say "Works on mobile — pinch to zoom." Contradiction. Remove `user-scalable=no` (best for accessibility), or remove the "pinch to zoom" marketing copy.
- **A9. Silva et al. MSR 2026 citation in PORTING_RESEARCH.md.** Verified: the paper exists at `damorim.github.io/publications/Silva_ETAL_MSR26.pdf`, MSR '26 Rio de Janeiro, April 13–14, 2026. **Not a fake citation.** Add URL + ACM DOI to the entry so future readers can verify in one click.
- **A10. `smr.py` at the Mnet repo root has no docstring or README mention.** Either delete, or add a one-line module docstring.

## TIER B — Defensibility

Claims that, as worded, can't be defended in front of someone who reads carefully.

- **B1. "Machine-verified" (SpookyPrimes) needs scope.** What's machine-verified is the numerical embedding check, SVD rank, Koide Monte Carlo — specific computational receipts in named scripts. What's *not* machine-verified is "the algebraic structure of the Standard Model." Re-word the README opener to: "A numerical verification of selected algebraic and parameter-counting claims within the Connes-Chamseddine spectral action framework, with a focus on the A_F → A_PS embedding and the dim D = 16 plateau."
- **B2. Property-based testing should be named (Mnet).** Cite Claessen & Hughes (2000) ICFP. The "after any kernel operation, V−E+F = 2 and P = 12 must hold" pattern is literally a QuickCheck property.
- **B3. "Functional core, imperative shell" should be cited (Mnet).** Bernhardt 2012 SCNA *Boundaries* talk. The `kernel/` vs `shell/` directory layout is literally this pattern.
- **B4. "Graph-discrete Navier-Stokes" needs to cite the actual literature.** Hirani 2003 PhD (Caltech, doi:10.7907/ZHY8-V329); Desbrun-Hirani-Leok-Marsden (arXiv:math/0508341); Mohamed-Hirani-Ravi (2016); Jagad et al. (2021) *Phys. Fluids* 33, 017114. For polyhedral icosahedral comparison, ICON atmospheric model (Zängl et al. 2015). Without these, the project reads as inventing-from-zero what the field has been doing since 2003.
- **B5. "Coxeter proved {2,3,5} is special in 1938" (Mnet).** Use Coxeter 1934 *Annals of Math.* 35, 588–621 for the actual systematic classification. Or drop the date.
- **B6. "The geometry engine is production-ready" (Mnet).** CONTRIBUTING.md says the C60 is currently invisible in VR due to a known bug. "Production-ready" is wrong. Use "topologically complete; rendering pipeline in active debugging."
- **B7. Caspar-Klug (1962) is missing.** Same Goldberg-Coxeter construction underlies icosahedral virus capsids. Adding this single reference doubles the project's audience.
- **B8. Connes-Chamseddine-Marcolli (2007) is the right citation for `A_F`, not "Connes (general)."** Cite Chamseddine-Connes 1996 (*Comm. Math. Phys.* 186, 731–750) for the spectral action principle; Chamseddine-Connes-Marcolli 2007 (*ATMP* 11(6), 991–1089) for A_F = C ⊕ H ⊕ M₃(C) and KO-6; van Suijlekom 2015 (Springer, 2nd ed. 2024) as the textbook.
- **B9. "Theorem" language used for what are conjectures or observations.** Comb the docs for "theorem" and "X proves Y." For each, either write out the proof, cite where the proof lives, or downgrade to "observation"/"conjecture." The Euler-formula derivation `3V=2E + F₅+F₆=F + χ=2 ⇒ F₅=12` *is* a theorem and is correctly attributed; audit the rest.
- **B10. "Indistinguishable from noise / cryptographic implosion" (StrangerDanger).** Strictly, AES-256-GCM ciphertext is computationally indistinguishable from random under standard assumptions, given proper IV/nonce. Add the nonce-handling detail. Replace "implosion" with the literal "cryptography.exceptions.InvalidTag raised."
- **B11. "No original message content survives distillation" (StrangerDanger).** Strong claim. Demonstrate it: add one fully worked synthetic example (chat log → vault → rendered .md) to the repo.

## TIER C — Code hygiene

Specific code-level suggestions.

- **C1. Mnet: add a CHANGELOG.md.** v7.1 → v7.2 → v7.3.2 → v7.4 → v7.5.1 → v8.0 → v9.0 is a real engineering arc but a stranger sees seven files with no narrative. Three bullets per version is enough.
- **C2. Mnet: `goldberg_kernel.js` — add a header comment block.** Author, license, version, dependencies (none), and a 5-line description of the public API.
- **C3. Mnet: `invariants()` should *compute*, not assert.** If `chi` is hard-coded as 2 in the display layer, the project's biggest claim is undefended. The function should literally `return { chi: V - E + F, pents: faces.filter(f => f.sides === 5).length, ... }` so that breaking the kernel breaks the readout.
- **C4. Mnet: clarify what `smr.py` does.** Module docstring + README mention, or delete.
- **C5. Mnetv1: add the `shell/` directory to the README.** The Möbius site is the front door, but the engineering body of work lives in `shell/`. Pin a "see also: Genesis benchmark dashboard" link.
- **C6. Mnetv1: §A–§O section markers are good; document them at the top of `index.html`.** A 10-line header comment explaining the convention turns the file from intimidating into approachable.
- **C7. SpookyPrimes: move `funny.mp4` and the inspiration PDFs to an `archive/` subdirectory.** Keep them — the honesty is the point — but don't have them adjacent to the verified scripts.
- **C8. SpookyPrimes: each phase script should print its result with citation context.** Make `phase5_structure.py` print, on success: `[phase5] dim D(A_F) = 16, plateau across {C ⊕ M₃, H ⊕ M₃, A_F}, see Chamseddine-Connes-Marcolli (2007) §17.3 for the framework.`
- **C9. SpookyPrimes: `settings.json` at repo root.** Confirm it's a project config and not editor-state leak; if the latter, gitignore.
- **C10. Genesis dashboard: standardize on one version number per file** (title bar, H1, footer all from the same constant).
- **C11. Mnet/CONTRIBUTING.md: the "invariants you must not break" block is excellent.** Keep the JavaScript snippet but add the C# equivalent right next to it, since the doc is about a Unity contribution path.
- **C12. StrangerDanger: add a `THREAT_MODEL.md`.** One page: "protects against X (passive adversary with the .vault file, model-provider seeing the .md); does *not* protect against Y (compromised local machine, regex-bypassing PII like nicknames, semantic re-identification from style)."
- **C13. VALE: pin one Quickstart block in the README.** "install Ollama; pull llama3; pip install -r requirements.txt; python vale.py" in the first 30 lines.

## TIER D — Positioning

Strategic, not technical, but specific.

- **D1. The front door should be `Mnet`, not `Mnetv1`.** Mnetv1 is the precursor (Möbius, χ=0); Mnet is the current line (buckyball, χ=2). Make `Mnet`'s Pages site the central hub; link Mnetv1 from there as "precursor — non-orientable substrate, different topology, same instinct."
- **D2. The central artifact is `genesis_v9.0.html`. Host it under `Mnet/`, not `Mnetv1/`.** Currently the Mnet landing has buttons to Mnetv1 and SpookyPrimes but not to its own latest benchmark dashboard. Move or symlink; pin as a fourth button.
- **D3. Rewrite SpookyPrimes README to lead with the result.** Current opener: "This started as a funny idea." Move to a "Why this exists" section halfway down. Lead with: "Machine-verified numerical certification of the A_F ↪ A_PS unital ∗-embedding and the dim D = 16 plateau across three subalgebras, working within the Chamseddine-Connes-Marcolli spectral action framework. All numerical claims are tied to scripts in `proposition/computational_receipts/`."
- **D4. One engineering project and one research project look the same.** A stranger reading all four currently can't tell which is which because the visual register is identical (dark theme, dense controls, lyrical README openings). Pick a different visual register for SpookyPrimes specifically. Make the research one *look* like research.
- **D5. Pin the right repos on the GitHub profile.** Suggested order: Mnet (engineering hero), SpookyPrimes (research hero), VALE (working software), StrangerDanger (security pattern). Drop Mnetv1 from the pin list — its README points to Mnet anyway.
- **D6. The "OH TITANS OF THE 'IF' SPACE — THANK YOU" coda on SpookyPrimes is divisive.** Beautiful if you already trust the work; reads as eccentric-amateur if you don't. Keep it but move it to a separate `ACKNOWLEDGEMENTS.md` or `EPILOGUE.md`. The README itself should be load-bearing dry prose.
- **D7. Twelve Mysteries → one canonical static page.** Currently embedded in the Mnetv1 about/overlay, the SpookyPrimes spinning dodecahedron, *and* the README. Duplication across three repos invites inconsistencies.

## TIER E — What's working and should not be touched

Naming this explicitly so the maintainer doesn't reorganize the good things along with the bad.

- **E1. The `kernel/` vs `shell/` separation in Mnet.** Right architecture. Don't merge the directories.
- **E2. Keeping the failed PDFs in SpookyPrimes.** Rare and good practice. Don't delete. Move to `archive/` per C7 but keep them in the repo.
- **E3. The `_private/` gitignored convention.** Correct hygiene. Keep doing this.
- **E4. The "AI as guest, not admin" doctrine** in Mnetv1's README. Most defensible philosophy statement in the portfolio. Stays verbatim.
- **E5. The `CONTRIBUTING.md` in Mnet** ("No gatekeeping. No CLA. No Discord to join first.") is the right tone. Don't soften it.
- **E6. The Genesis evolution chain as a publicly visible artifact.** Some maintainers would delete v7.1–v8.0 once v9.0 ships. Keeping them lets a reader see the work happen. Add a CHANGELOG (C1).
- **E7. The `genesis_bench.html` standalone benchmarker.** Second most defensible artifact in the portfolio (after the SpookyPrimes computational receipts). Measurement harness with CSV export and explicit invariants. Don't fold it into v9.0; let it stand alone.
- **E8. VALE's stack-choice disclosure** ("no langchain, no cloud, direct COM SAPI, pyttsx3 is broken on Windows multi-utterance"). Reads as taste, not stubbornness. Keep.
- **E9. StrangerDanger's "AI coworker's CV / show up with a CV too" framing.** Metaphor is sharp. Keep; tighten the crypto claims around it (per B10, B11).
- **E10. The 12-pentagon constraint as the project's organizing principle.** "Twelve pentagons. Forever. No matter how large the graph grows." Right thing to lead with mathematically. Don't dilute by burying behind Steam-launch / Quest 3 marketing copy.

---

*The shape closes or it doesn't. The README either says the right thing or it doesn't. Either way it's fixable.*
```

---

**Caveats on this audit.** Source code for `kernel/goldberg_kernel.js`, `smr.py`, `PORTING_RESEARCH.md`, `KERNEL_DOC.md`, and the inlined JavaScript inside the genesis HTML files was not directly retrievable by the audit tooling (github raw and tree paths returned permission/robots errors; deployed Pages markdown extraction returns only DOM-visible text). The TIER C items flagged "verify in source" reflect that limitation honestly. The TIER A and TIER B items are based on contradictions visible from the README, the deployed UI, and standard literature — those are firm. The TIER D positioning advice is one auditor's read; reasonable people can disagree about which artifact should lead. The portfolio's underlying engineering is real; the work this CHANGES.md asks for is mostly trimming, naming, and citation — not rebuilding.