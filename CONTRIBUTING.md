# Contributing to MachineNet

No gatekeeping. No CLA. No Discord to join first.

---

## What's actually needed right now

Ranked by impact:

### 1. Unity C# kernel port (HIGHEST IMPACT)
Port `kernel/goldberg_kernel.js` to C#.
350 lines. Pure functions. No side effects.
See [STEAM_PATH.md](./STEAM_PATH.md) for the full API spec and invariants.

### 2. WebXR hand gestures
The VR button works. Hand tracking doesn't yet.
- Pinch on a face â†’ `GK.refineOne(state, faceIdx)`
- Two-hand spread â†’ `GK.undo(state)`
- Hold palm up â†’ show face info panel
Meta Quest 3, WebXR Hand Input API.

### 3. KaTeX equation panels
Click an atom node â†’ equation floats up in 3D space.
KaTeX renders to SVG. Three.js renders SVG as a texture on a plane.
The DB schema is ready. The renderer hook is not.

### 4. Sound design
- Pentagon anchor tone: pure fifth, 528 Hz base
- Hexagon field tone: major third above anchor
- Bridge edge (gold): ascending arpeggio on connection
- C60 closure: full chord, one time, unforgettable
No Unity required â€” Web Audio API in the browser build is fine.

### 5. Capsule art
Steam store page needs:
- Header capsule: 460Ã—215px
- Main capsule: 231Ã—87px
- Library capsule: 600Ã—900px
The aesthetic: dark background, cyan wireframe fullerene, minimal text.
The vibe: Anton Vanko's workshop, not Marvel. Post-Soviet engineer. Buenos Aires basement. Real math.

---

## How to submit

1. Fork the repo
2. Make your change in a branch
3. Open a PR with one sentence describing what changed and why
4. That's it

The human commits. The AI proposes. That's the doctrine.

---

## What NOT to do

- Don't add analytics or telemetry
- Don't add cloud dependencies
- Don't break the zero-dependency kernel
- Don't add a bundler (no webpack, no vite, no rollup â€” vanilla ESM only)
- Don't submit "AI-generated content" without reading it yourself first

---

## The invariants you must not break

```javascript
// After any operation on state:
const inv = GK.invariants(state);
console.assert(inv.pentCount === 12);
console.assert(inv.vertCount - inv.edgeCount + inv.faceCount === 2);
console.assert(inv.vertexDegree === 3);
```

If these fail, the topology is broken. The PR will not merge.

---

*The shape closes or it doesn't. Either way, it's real.*

