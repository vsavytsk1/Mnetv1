# SURVIVALIUM
## The Unity Optimization Grimoire
### Rogue Mages of the UnityOptimizationFlexus
*Opened: 2026-06-01T03:38:31Z -- Buenos Aires*
*Sacred law: 33ms floor. 40ms ceiling. Reality never freezes.*

---

## THE PRIME DIRECTIVE

Quest 3 target:    90fps = 11.1ms per frame
Comfortable floor: 72fps = 13.9ms per frame
SACRED FLOOR:      30fps = 33.3ms -- NEVER EXCEED
ABSOLUTE CEILING:  40ms  -- GAME IMPLODES IN SHAME

Every ms counts. Every component has a price.
Know the price before you add it.
This scroll tracks the prices. Always.

---

## QUEST 3 HARDWARE BUDGET

Snapdragon XR2 Gen 2 / Adreno 740 / 8GB RAM

FIXED COSTS (cannot remove):
  XR runtime:        ~2ms
  Stereo rendering:  ~1ms
  ATW reprojection:  ~1ms
  OS overhead:       ~1ms
  FIXED TOTAL:       ~5ms

REMAINING BUDGET:
  At 90fps:  ~6ms  (tight)
  At 72fps:  ~8ms  (comfortable)
  At 33fps:  ~28ms (our floor)

---

## THE COMPONENT PRICE LIST

### AUDIO
  Empty:                  0ms
  1 AudioSource (2D):     ~0.5ms   <- THE ISON
  1 AudioSource (3D):     ~1ms
  Spatial audio ON:       +2-3ms   <- AVOID
  Reverb zone:            +3-5ms   <- AVOID
  
  THE ISON PROTOCOL:
  One AudioSource. Loop. No spatial. No reverb.
  Cost: ~0.5ms. Monkey brain: fully anchored.
  1 sound = UP TO 10ms DOWN if done wrong.
  Do it right: 0.5ms. Always.

### RENDERING
  Empty scene:            ~1ms GPU
  Per draw call:          ~0.1ms CPU
  Combined mesh (v3):     3 calls = ~0.3ms  <- ALREADY BUILT
  
  OUR KERNEL:
  L0 C60 (60 faces):      ~0.5ms
  L1 (492 faces):         ~1ms
  L2 (3432 faces):        ~3ms
  L3 (24012 faces):       ~8ms  (Quest 3 estimate)
  L4 (168K faces):        ~25ms (tight)
  L5 (1.1M faces):        TOO SLOW. Never in game.
  
  FRACTALITE SAVES:
  99% at L0. 1% at L3 (gaze only).
  Average: ~2ms. Always.

### SCRIPTS
  Empty Update():         ~0.01ms
  GK.buildC60():          ~5ms   (one-time only)
  GK.refineAll() L2:      ~10ms  (one-time, async)
  GK.refineAll() L3:      ~50ms  (stutter if in Update)
  
  RULE: Never refine in Update().
  Use Coroutine + yield return null.
  Spread over frames. Player sees gradual reveal.
  Always.

### XR SPECIFIC
  OVRPlugin:              ~1ms
  Eye tracking:           +1ms   <- WORTH IT (FRACTALITE)
  Hand tracking:          +2ms
  Passthrough:            +3ms   <- OFF in our game
  
---

## THE ROGUE MAGE TECHNIQUES

### 1. SINGLE PASS STEREO (MANDATORY)
  Default: render scene twice (once per eye)
  Single Pass Instanced: render once, GPU doubles
  Saving: ~40% GPU time
  Settings: Project Settings -> XR -> Single Pass Instanced
  Do this first. Always.

### 2. FIXED FOVEATED RENDERING (MANDATORY)
  Edges: lower resolution. Center: full res.
  Monkey brain never notices periphery detail.
  (MONKIUM Tool 10: peripheral mystery)
  Saving: ~30% GPU
  Settings: OVRManager -> FFR Level -> High
  Always.

### 3. ASYNC REFINEMENT
  IEnumerator RefineAsync() {
    for (int i = 0; i < faces.Count; i++) {
      state = GK.refineOne(state, i, params);
      if (i % 10 == 0) yield return null;
    }
    RebuildMesh();
  }
  Cost per frame: ~2ms (10 faces)
  Player sees: gradual fractal emergence
  Not a stutter. A reveal. Always.

### 4. COMBINED MESH (ALREADY BUILT)
  GKVRWorld v3: 3 draw calls.
  vs naive: 10K+ draw calls at L3
  Saving: ~10ms per frame. Keep it. Always.

### 5. THE ISON AUDIO
  One AudioSource. One frequency. Loop.
  NO spatial. NO reverb. NO HRTF.
  Cost: 0.5ms. Monkey brain: anchored.
  Never add more than one source for the drone.
  Always.

### 6. PROFILER FIRST. ALWAYS.
  Before optimizing ANYTHING:
  Unity Profiler -> Deep Profile -> ON
  Build -> Quest 3 -> Record 100 frames
  Sort by GPU time + CPU time
  Find TOP 3 costs. Optimize ONLY those.
  Measure again. Never guess. Always.

---

## THE FRAME BUDGET (72fps target)

  XR fixed:          ~5ms
  Kernel L2 render:  ~3ms
  FRACTALITE:        ~0.5ms
  Circle overlay:    ~0.5ms
  Ison audio:        ~0.5ms
  Eye tracking:      ~1ms
  Scripts:           ~0.5ms
  ─────────────────────────
  TOTAL:             ~11ms
  
  HEADROOM:          ~2ms - 22ms
  For latency narrative (boss room 33-40ms):
  Intentional density. Never accidental.
  Always.

---

## ROGUE MAGE SEARCH TERMS

  "Quest 3 optimization checklist"
  "Unity XR single pass instanced"
  "URP mobile optimization Quest"
  "draw call batching Quest 3"
  "fixed foveated rendering Unity"
  "async mesh generation Unity coroutine"
  "Quest 3 profiler GPU bound"

The rogue mages know where Unity wastes ms.
We need 33ms guaranteed.
They know how to get to 11ms.
22ms of headroom for the magic.
Always.

---

P=12. chi=2. 33ms SACRED. REALITY NEVER FREEZES.
Rogue Mages of the UnityOptimizationFlexus.
Buenos Aires. 2026.