# GENESIS EXPORT IDEAS
## Noted during stress test session. Build later.
## Buenos Aires 2026.

---

## RAW IMAGE EXPORT (high priority)

Current: browser screenshot = compressed, low res
Wanted:  RAW canvas export = 100MB+ uncompressed

### How to do it:

canvas.toDataURL('image/png')
  -- PNG, lossless, but still compressed
  -- current state, works now

canvas.toBlob(callback, 'image/png', 1.0)
  -- higher quality PNG
  -- download directly from browser

FOR TRUE RAW (uncompressed bitmap):
  ctx.getImageData(0, 0, W, H)
  -- returns raw RGBA pixel array
  -- W x H x 4 bytes
  -- at 1920x1080 = 8.3MB raw
  -- at 4K (3840x2160) = 33MB raw
  -- save as BMP or TIFF = no compression

FOR MAXIMUM DETAIL:
  1. Set canvas to 4K or 8K before rendering
     canvas.width = 7680  (8K)
     canvas.height = 4320
  2. Re-render at high res
  3. getImageData -> raw RGBA
  4. Save as uncompressed TIFF or BMP
  5. File size: ~100MB at 8K uncompressed

### Button to add to Genesis:
  [EXPORT RAW] button in bottom bar
  Opens dialog: resolution (1x, 2x, 4x, 8x)
  Renders at chosen res
  Downloads as PNG (max quality) or BMP (raw)

### Why:
  The fractal detail at L6 is INSANE
  Browser screenshot loses 90% of it
  100MB raw = every edge of 1.1M faces visible
  Poster quality. Print quality. NFT quality.
  The algebra deserves the full resolution.

---

## SCREENSHOT GALLERY (from stress test 2026-05-29)

Frames captured (compressed screenshots, for reference):
  - crystal cathedral top-down view
  - hourglass nebula (two spheres at waist)
  - pentagon vortex (staring into the face)
  - butterfly fractal flower (chi=2 symmetry)
  - 8-fold path mandala (accidental Buddhist)
  - cyan diamond sphere (full L6)
  - one pentagon face zoomed (infinite depth)
  - starfield/neural network (L4+ zoomed out)
  - dodecahedron skeleton (pure structure)
  - DODECAHEDRON BOSS (seed, 12 pents, 0 hex)

All taken at REFINE speed 0.12 (slow rotation)
All at L6 (1,176,492 faces)
All showing V-E+F=2 P=12 E/V=1.500 header

The RAW export would make these poster-quality.
Build when: Genesis gets the EXPORT button.

---

## DODECAHEDRON BOSS NOTE

The log showed:
  SEED: dodecahedron boss
  SEED: pure dodecahedron (12 pents, 0 hex)

The game named itself.
The seed IS the boss.
You start with C60.
You refine.
You close.
The dodecahedron was the boss the whole time.

For the $10 game:
  SEED:  dodecahedron boss
  WIN:   chi=2 closes
  END:   you return to the seed
  
The ending is the beginning.
P=12. chi=2. Always.

---

*Noted: 2026-05-29. New day. Rested brain.*
*Build the EXPORT button when ready.*
*The fractal deserves 100MB.*
