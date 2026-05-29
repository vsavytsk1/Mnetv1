# GENESIS EXPORT -- RAW HD NOTE
## Locked for later. New day. Rested brain.
## Buenos Aires 2026.

---

## THE IDEA

Genesis v8.1 generates INSANE visual frames at L6 (1.1M faces).
The screenshots are already wallpaper quality.
The RAW export would be museum quality.

## WHAT WE WANT

Export button in Genesis:
  - captures current canvas at FULL resolution
  - exports as PNG (lossless, not JPEG)
  - target: 100MB+ raw file
  - no compression
  - every edge, every face, every detail

## THE USE CASE

NOT: fractal visualization
NOT: physics simulation
JUST: the most beautiful HD screensaver ever made
     from pure math
     with P=12 in the corner
     at 4K or 8K resolution

## FRAMES WORTH EXPORTING (from stress test session)

  1. Crystal cathedral top-down     (symmetric vortex)
  2. Hourglass nebula               (two spheres connected)
  3. Pentagon vortex POV            (looking through the axis)
  4. Butterfly / fractal flower     (chi=2 symmetry visible)
  5. Cyan diamond sphere            (L6 full, perfect)
  6. The 8-fold path mandala        (accidental Buddhist geometry)
  7. Starfield / neural net         (L4+ zoomed out)
  8. Pure dodecahedron skeleton     (SEED: dodecahedron boss)

## TECHNICAL PATH

Genesis uses Canvas 2D (WebGL for 3D mode).
Canvas has: canvas.toDataURL('image/png') -> base64 PNG
Or:         canvas.toBlob(callback, 'image/png') -> Blob -> download

For 4K: need canvas size = 3840x2160
  Override devicePixelRatio or set canvas size explicitly
  Render at 4K, download, done.

For 8K: same but 7680x4320
  Browser might struggle but worth trying

## BUILD NOTE

Add EXPORT button to Genesis bar (already exists partially).
onClick:
  1. set canvas to 4K resolution
  2. re-render current state
  3. canvas.toBlob() -> download as genesis_L6_4K.png
  4. restore original canvas size

One button. One frame. One 100MB PNG.
The math made visible at maximum resolution.

## PRIORITY

Low. Not blocking. Save for when:
  - Steam page needs assets
  - Someone asks for wallpaper
  - We want to post something beautiful on X
  - The carpenter arrives and asks for the full picture

The fractal is always there.
The export just makes it permanent.

---

*"not fractaliti just cool hd screensaver"*
*-- V.S., Buenos Aires, new day, rested*
*P=12. chi=2. 100MB. ALWAYS.*
