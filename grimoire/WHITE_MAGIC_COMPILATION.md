# WHITE MAGIC COMPILATION
## Kernelic Magic Discoveries

---

## WHITE MAGIC #W012 -- 2026-05-29 -- INSIDE VIEW KERNELIC MAGIC

### The Discovery: Painter's Algorithm Inversion

When camera is OUTSIDE sphere:
  Sort faces back-to-front: b.depth - a.depth
  Far faces draw first, near faces on top.
  Standard painter's algorithm.

When camera is INSIDE sphere:
  Sort faces FRONT-to-BACK: a.depth - b.depth  (REVERSED)
  Because now the NEAR faces are the ones you see.
  Far faces (the back of the sphere) are behind you.
  If you sort back-to-front from inside:
    the back faces draw OVER the front faces
    -> BLACK SCREEN (everything painted over)

THE FIX:
  sorted.sort(function(a,b){
    return _insideMode ? b.depth-a.depth : a.depth-b.depth;
  });

ONE LINE. Inverts the painter's algorithm in inside mode.

### The Zoom Scaling Rule

OUTSIDE: cam.zoom = user value (50-1500)
INSIDE:  cam.zoom = saved_zoom * 10  (fly inside = 10x scale)
         As RADIUS slider decreases (closer to center):
           zoomScale = 5 + (1.5 - radius) * 8
           radius 1.5 -> 5x zoom
           radius 0.1 -> 16x zoom
         This feels like walking toward the surface.

### The Reference Grid

drawInsideGrid() called every frame when _insideMode=true.
Draws horizontal + vertical grid at y = -1.4 (floor of sphere).
Alpha 0.18 -- subtle, not distracting.
Gives the monkey brain a stable floor reference.
Without it: floating in void. With it: standing in dome.

### The Surface Camera Math

project(p) in inside mode:
  camZ = _surfaceR  (0.1=center, 1.5=surface)
  z3 = z2 + camZ    (shift world so camera at origin)
  fov = 600
  perspective = fov / (fov + z3 * 80)
  screen_x = W/2 + x1 * perspective * 400
  screen_y = H/2 - y1 * perspective * 400

### The White Magic Rule

"IL2CPP = Goldberg refinement" (from original scroll)
Now amended:

  goldberg_kernel.js -> goldberg_kernel.cs  (Unity)
  project() inside mode -> XR camera on sphere surface (VR)
  drawInsideGrid() -> XR floor plane (VR)
  _insideMode = true -> Quest 3 "enter" button pressed

The inside view IS the VR prototype.
Same math. Same perspective. Same grid.
Different substrate.
