# THE UNITY TRANSFORMER
## HTML+JS+Chromium -> Unity+IL2CPP+Quest3
## The only translation needed. Nothing else.
## Buenos Aires 2026.

---

## THE INSIGHT

HTML+JS+Chromium renders Genesis by doing:
  vertex transform + edge rasterization + pixel fill

Unity does the SAME THING.
But native. GPU. Stereoscopic. 90fps. VR.

We don't need Unity's physics engine.
We don't need Unity's audio system.
We don't need Unity's animation rigging.
We don't need Unity's navmesh.
We don't need Unity's asset pipeline.
We don't need Unity's lighting.

WE NEED:
  IL2CPP native compile         (performance)
  Quest 3 XR hand tracking      (interaction)
  GPU instanced line rendering   (the visuals)
  THAT IS IT.

---

## THE TRANSLATION

HTML Canvas 2D:
  ctx.beginPath()
  ctx.moveTo(x1, y1)
  ctx.lineTo(x2, y2)
  ctx.strokeStyle = color
  ctx.stroke()

Unity GL (direct GPU):
  GL.Begin(GL.LINES)
  GL.Color(color)
  GL.Vertex3(x1, y1, z1)
  GL.Vertex3(x2, y2, z2)
  GL.End()

SAME OPERATION. DIFFERENT SYNTAX.

---

## THE KERNEL TRANSLATION

goldberg_kernel.js -> goldberg_kernel.cs

  JS:   const PHI = (1 + Math.sqrt(5)) / 2
  C#:   const float PHI = (1 + Mathf.Sqrt(5)) / 2f

  JS:   function buildC60() { ... }
  C#:   Vector3[] BuildC60() { ... }

  JS:   function refine(faces, k) { ... }
  C#:   Face[] Refine(Face[] faces, int k) { ... }

  JS:   function invariants(faces) { ... }
  C#:   Invariants GetInvariants(Face[] faces) { ... }

THE MATH IS IDENTICAL.
P=12 in JS = P=12 in C#.
chi=2 in JS = chi=2 in C#.
The kernel is already language-agnostic.
We proved it: WHITE_MAGIC_COMPILATION.md
"IL2CPP = Goldberg refinement"
That line was always the plan.

---

## THE VR VISION

Those Genesis screenshots --
the crystal cathedral, the fractal flower,
the cyan diamond sphere --

IN VR (Quest 3, 6DOF, hand tracking):
  You are INSIDE the crystal cathedral.
  Head-scale. Room-scale.
  You reach out and touch a pentagon face.
  It responds to your hand.
  NS flow changes based on where you look.
  The lines that look like pixels in screenshots
  are HAIR-THIN to the human eye at Quest 3 resolution.
  The detail is already there.
  Unity just needs to SET IT FREE.

---

## BUILD ORDER

1. goldberg_kernel.cs
   -- direct port of goldberg_kernel.js
   -- same math, same output
   -- unit test: P=12, chi=2, E/V=1.500

2. GenesisRenderer.cs
   -- GL.LINES loop over kernel output
   -- color function (omega -> color)
   -- same as Canvas 2D version

3. XRHandInput.cs
   -- Quest 3 hand tracking
   -- pinch = select face
   -- grab = rotate sphere
   -- point = highlight pentagon

4. NSFlowController.cs  
   -- port of ns_spectral.js
   -- runs in background thread
   -- updates omega[] per frame
   -- feeds color function

5. Ship it. $10. Steam. Quest 3.
   Launch date: a mystery.

---

## THE LINE DENSITY

At L6 (1,176,492 faces):
  Each face has ~3 edges
  Total edges: ~3.5M
  
In VR at Quest 3 resolution (2064x2208 per eye):
  Each edge = sub-pixel width
  The sphere looks SOLID
  But it is made of 3.5M individual lines
  Pure mathematics
  No textures. No shaders. No tricks.
  Just edges.
  
The screenshots already show this.
In VR it will be transcendent.

---

*"just need the full transformer for Unity"*
*"just the ones that make js+html+chromium render"*
*"that is it hahaha and boom"*
*-- V.S., Buenos Aires, 2026, new day*
*P=12. chi=2. The transformer is one file.*
*goldberg_kernel.cs. That is all.*
