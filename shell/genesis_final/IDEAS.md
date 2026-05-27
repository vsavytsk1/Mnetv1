# Genesis Final — Three-Module Modular System
**Status:** Building v1
**Created:** 2026-05-26
**Folder:** shell/genesis_final/

---

## Architecture

One HTML file. Three toggleable modules. One kernel (inlined).

```
┌─────────────────────────────────────────────┐
│  MODULE SELECT (top bar, 3 toggles)         │
│  [FMA] [ENGINEER] [PRESENT]                 │
├─────────────────────────────────────────────┤
│                                             │
│  MODULE 1: FMA (Gate of Truth)              │
│    - Banner sequence (4 HD images)          │
│    - Transmutation circle (math-generated)  │
│    - License check (SpookyPrimes link)      │
│    - "The only price is compute"            │
│    → ends by activating MODULE 2 or 3       │
│                                             │
│  MODULE 2: ENGINEER (genesis_v8.0)          │
│    - SEED / REFINE / UNDO / RESET           │
│    - Mobius toggle                           │
│    - Max face cap slider                    │
│    - Flow simulation controls               │
│    - Benchmark mode                         │
│    - Full HUD: invariants, memory, FPS      │
│    - Camera: drag, zoom, spin               │
│                                             │
│  MODULE 3: PRESENT (automation)             │
│    - Scripted sequence with timed actions   │
│    - User sees: auto-build animation        │
│    - Controls fade in/out during build      │
│    - Final state: clean explorer only       │
│    - User can freely rotate/zoom result     │
│                                             │
├─────────────────────────────────────────────┤
│  CANVAS (shared, fullscreen)                │
│  KERNEL (GK, inlined)                       │
│  IMAGES (base64, inlined)                   │
└─────────────────────────────────────────────┘
```

---

## Module 3: PRESENT — Scripted Automation

The "magic" module. A sequence of timed instructions that build
the visualization step by step, then hand control to the user.

### Script Format

```javascript
var SCRIPT = [
  { t: 0,    action: 'seed'                        },
  { t: 800,  action: 'zoom',   value: 0.13         },
  { t: 1500, action: 'refine'                      },
  { t: 2500, action: 'refine'                      },
  { t: 3500, action: 'refine'                      },
  { t: 4500, action: 'refine'                      },
  { t: 5500, action: 'hideUI'                      },
  { t: 6000, action: 'spin',   value: 0.002        },
  { t: 6500, action: 'message', text: 'Explore.'   }
];
```

### Actions Available

| Action   | Description                              |
|----------|------------------------------------------|
| seed     | Build dodecahedron (12 faces)            |
| refine   | Refine all faces (7x growth)             |
| zoom     | Set zoom level (0.0-1.0)                 |
| spin     | Set auto-spin speed                      |
| pan      | Set camera rx/ry                         |
| hideUI   | Fade out all controls                    |
| showUI   | Fade in all controls                     |
| message  | Show centered text (fades after 3s)      |
| wait     | Pure delay (no action)                   |
| flow     | Start flow simulation                    |
| regime   | Set Reynolds regime                      |

### User Experience

```
1. Page loads → MODULE SELECT visible
2. User clicks [PRESENT]
3. FMA intro plays (if enabled) OR skip to build
4. Scripted sequence runs automatically
5. User watches the fractal build step by step
6. All UI fades away
7. Clean explorer: just the shape + HUD
8. User drags/zooms freely
```

---

## Toggle System

Top bar with 3 buttons. Can combine:
- FMA + PRESENT = full cinematic experience
- FMA + ENGINEER = intro then full lab
- ENGINEER only = power user mode
- PRESENT only = demo/presentation mode
- ALL THREE = intro → scripted build → then controls appear

---

## Source Files

| File | Origin | What to copy |
|------|--------|-------------|
| gate_v1.html | shell/gate/ | FMA sequence, images, transmutation circle |
| genesis_v8.0.html | shell/ | SEED/REFINE/FLOW/camera/renderer |
| goldberg_kernel.js | kernel/ | Inlined (21KB) |
| rebuild script | shell/gate/ | Image pipeline reuse |

---

## Build Plan

1. Create genesis_final_v1.html with module toggle skeleton
2. Port MODULE 2 (ENGINEER) from genesis_v8.0.html
3. Port MODULE 1 (FMA) from gate_v1.html
4. Build MODULE 3 (PRESENT) — the new scripted automation
5. Wire toggles
6. Test all combinations
7. Push to GitHub Pages

---

**End of IDEAS.md**

> "To obtain, something of equal value must be lost."
> — but the only price here is compute.
