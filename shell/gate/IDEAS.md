# The Gate — Ideas & References
**Status:** v1.4 WORKING / v2 planned
**Created:** 2026-05-26
**Folder:** shell/gate/

---

## Concept

A narrative-driven HTML experience wrapping the Genesis fractal explorer.
Inspired by Fullmetal Alchemist's Gate of Truth.
The math IS the magic. The transmutation circle IS the kernel.
The cosmic web IS what's behind the gate.

---

## Sequence (v1 design)

```
1. LOAD     → Banner: Gate closed (HD image)
              "Do you want to begin the journey?"
              "There is a price. There is always a price."
              [ click anywhere ]

2. CLICK    → Transmutation circle animates
              Math-generated from kernel:
              - 12 pentagons in a ring (dodecahedron projected flat)
              - φ spiral from center
              - Connecting graph lines (star pattern)
              - Euler invariants rotating around the edge
              - "V-E+F=2 · P=12 · φ=(1+√5)/2 · EULER 1758 · GOLDBERG 1937"
              Auto-advances after animation completes (~5s)

3. AUTO     → Banner: Gate opens (HD image or 3D model)
              "The Gate opens for those who understand equivalent exchange."
              [ click to enter ]

4. CLICK    → Banner: Truth sitting (HD image)
              "Oh? Hello there, explorer."
              "Have you read the license?"
              → Link to SpookyPrimes: https://vsavytsk1.github.io/SpookyPrimes/
              [ I understand. Show me. ]

5. CLICK    → Banner: Equivalent exchange moment
              "The only price is compute."
              "V − E + F = 2 · P = 12 · always"
              [ pay the price ]

6. CLICK    → EXPLORER: Full cosmic web render
              - Goldberg kernel, 3 refinements (3,432 faces)
              - Edges only (no face fill) = cosmic web filaments
              - Pentagons glow pink = galaxy cluster nodes
              - Jitter on vertices = organic/natural look
              - Trail effect (rgba clear) = nebula feeling
              - Full interactivity: drag rotate, scroll zoom
              - HUD: faces, pentagons, chi=2, E/V
```

---

## 3D Gate Model (Sketchfab)

Found: https://sketchfab.com/3d-models/edwards-gate-of-truth-637928fa1f0f4384ab730133b1f0f04c

Embeddable via iframe:
```html
<iframe title="Edward's Gate of Truth"
  src="https://sketchfab.com/models/637928fa1f0f4384ab730133b1f0f04c/embed?autostart=1&ui_theme=dark"
  width="100%" height="100%" frameborder="0"
  allow="autoplay; fullscreen; xr-spatial-tracking">
</iframe>
```

Could replace or augment the static gate image in steps 1 or 3.
User can physically rotate/explore the carved gate in 3D before entering.

---

## Image Pipeline

Tool: `shell/gate/img_to_base64.py`

```
DROP images into shell/gate/img/
RUN:  python img_to_base64.py --test     (verify quality)
RUN:  python img_to_base64.py --inject   (embed into HTML)

Config: JPEG 85%, max 1200x900, LANCZOS downscale
Expect: ~50-150 KB per image, ~200-600 KB total in HTML
```

Image slots (matched by filename keywords):
```
gate_closed  → keywords: gate, closed
gate_open    → keywords: open, opening
truth        → keywords: truth, sitting, white
exchange     → keywords: exchange, edward, price
```

---

## The Transmutation Circle IS Real Math

The circle drawn in step 2 is not decoration. It is:
- 12 pentagons = the 12 faces of the dodecahedron (Euler forces this)
- φ spiral = the golden ratio that seeds all vertex coordinates
- Connecting lines = the adjacency graph (trivalent, degree 3)
- Outer ring text = the invariants (chi=2, P=12, E/V=1.500)

In FMA, a transmutation circle encodes the RULES of what you're transmuting.
Our circle encodes the RULES of the topology: V-E+F=2, always.

"This is not a metaphor. This is math pretending to be magic.
Or magic pretending to be math. The invariant doesn't care."

---

## The Cosmic Web Connection

Wikipedia (Cosmic Web / Large-Scale Structure):
- "a vast foam-like structure sometimes called the cosmic web"
- "sheets collapse into filaments"
- "filaments cross at nodes (galaxy clusters)"
- Pranav et al. (2017): cosmic web topology has chi=2

Our kernel at high refinement = visually identical to cosmic web simulations.
Same math: trivalent graph filling a closed surface under topological constraints.

```
Cosmic web:     dark matter filaments on void boundaries
Our kernel:     edges connecting faces on a sphere
Neural tissue:  axon networks under skull
All three:      minimum-material connected graphs under constraints
```

---

## FMA References (for imagery)

- The Gate of Truth: massive carved stone doors, Tree of Life / Sephirot
- Truth (white figure): featureless, sitting cross-legged, grins
- Transmutation circles: geometric, symmetric, rule-encoded
- Equivalent Exchange: "To obtain, something of equal value must be lost"
- Edward at the gate: small human before infinite knowledge

---

## Connection to Other Projects

```
Gate of Truth  →  The experience wrapper
Kernel         →  The math engine behind the gate
SpookyPrimes   →  The license / "12 open questions"
StrangerDanger →  SOUL_CRYSTAL (cognitive topology)
VALE           →  The voice that could narrate the journey
Genesis v9.0   →  The benchmark proving the math works
navierCrunch   →  The GPU proof that topology holds under turbulence
```

---

## v1.4 Status (WORKING)

```
Gate v1.4 — 411 KB, fully self-contained
  Kernel: inlined (GK, 21KB)
  Images: 4x JPEG base64 (380KB)
  Sequence: 6 phases, all working
  Explorer: 1472 faces, chi=2, P=12, E/V=1.500
  Console: full phase logging
  Dependencies: ZERO
```

---

## v2 Plan: Full Genesis UI After Intro

After the FMA sequence completes, bolt on the full genesis_v9.0 control panel:
- SEED / REFINE / UNDO / RESET buttons
- Refinement level slider
- Reynolds regime toggles (Stokes/Laminar/Transition/Turbulent)
- Flow simulation (pressure diffusion on face adjacency)
- Benchmark mode
- Camera: drag rotate, scroll zoom, auto-spin toggle
- HUD: full invariants, face count, memory estimate

Source: copy from shell/genesis_v9.0.html, strip to essentials

---

## Future Ideas

- Add audio: low rumble when gate appears, crystalline chime on transmutation
- VALE integration: voice narration through the sequence
- Multiple "truths": different kernel refinement levels = different cosmic scales
- Multiplayer: two users open the gate simultaneously (WebRTC?)
- VR version: Quest 3, physically walk through the gate
- The Tree of Life on the gate = Sacred Math Tree (10 trees = 10 sephirot?)

---

## Ethics Reminder

From ETHICS.md and SpookyPrimes license:
"This software shall not be used for weapons, surveillance, or harm."

The gate warns. The truth reveals. The explorer chooses.
Document everything. Claim nothing that isn't verified.
The monkey brain says "too funny." History says "be careful."

---

**End of IDEAS.md**

> "One is all, all is one."
> — Izumi Curtis, Fullmetal Alchemist
