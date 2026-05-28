# STEAM PATH ? MachineNet
*The $10 launch. Full public document. Updated 2026-05-25.*

---

## The honest one-paragraph pitch

MachineNet is a VR knowledge graph shaped like a fullerene. You build it by reading math books. Each book you finish adds hexagons to the shell. When the last concept connects, the shape closes. The geometry is not decorative ? Euler's theorem forces it. The shell *must* close into C60 or it isn't a valid degree-3 pentagon-hexagon tiling of the sphere. You can verify this yourself in 10 lines of math. We ship when the first version of that loop is playable in a Quest 3 headset.

---

## What actually works RIGHT NOW (2026-05-24)

### ? STABLE
- **Unity build (MnetUni)** on Windows 11 ? the ONLY stable runtime
- **Quest 3 via Oculus Link** ? headset connected, both controllers, 84% battery
- **VR capture** ? Quest built-in recording ? Meta app on phone ? shareable
- **goldberg_kernel.js** ? pure math, zero deps, never crashes, 350 lines
- **69 simulation logs** across v6-v6.6 ? real data, real residuals
- **Topology finding** ? ?=2 converges, ?=0 diverges ? reproducible

### ?? CRASHES / UNSTABLE
- **mnet_v7.html in browser** ? crashes on heavy refinement (27K+ nodes)
- **mnet_v6_pc.html** ? same crash pattern, browser tab dies
- **WebGL + 27K nodes + NS flow** ? Three.js r128 cannot handle it in browser
- **Browser is NOT the runtime** ? Unity is. Browser was prototyping only.

### ?? KNOWN ISSUES
- `multi_edit` tool fails on OneDrive paths with spaces ? use Python heredoc
- `create_new_file` silently truncates large files ? use Python to write
- v7 had 8 missing JS functions (toggleFreeze etc) ? patched via Python
- `preserveDrawingBuffer:true` needed on WebGLRenderer for screenshots
- Quest USB 2.0 connected (recommends USB 3.0 for better Link quality)
- v6.6 log folder has only 1 log (LOG_START only, was in WALK mode)

---

## VR Capture Workflow (CONFIRMED WORKING)

```
1. Put on Quest 3
2. Oculus Link ? see PC desktop in VR
3. Open MachineNet (Unity or browser)
4. Meta button + Trigger = screenshot
5. Hold Meta button + Trigger = video recording
6. Files save to headset ? open Meta app on phone
7. Download / share from phone
```

This is how influencers share VR game pics. Same pipeline. No special tools needed.

---

## Phase map

### Phase 0 ? Foundation ? DONE
- [x] Goldberg-Coxeter kernel (`goldberg_kernel.js`)
- [x] Three.js visualization (v6, v6_pc, v7 ? all prototypes)
- [x] VR geometry engine v9 (WebXR ready)
- [x] SQLite DB schema
- [x] Book ingestion pipeline
- [x] 12 pentagon anchors seeded
- [x] NS solver: PRESSURE + MOMENTUM + INTEGRATE + CAGE_BOUNCE
- [x] Nanite DAG engine (mnet_nanite.js ? inlined in v7)
- [x] Autopilot sequences (5 demo scripts)
- [x] VR capture pipeline confirmed (Quest 3 ? Meta app)
- [x] 69 simulation logs, topology signature proven

### Phase 1 ? Unity C# Port + VR ? IN PROGRESS
- [x] Unity C# port of goldberg_kernel.js ? **DONE. GoldbergKernel.cs certified x30+**
- [x] GKRenderer.cs v5 ? C60 visible in editor + VR controls
- [x] GKAudio.cs ? procedural audio (sin/cos/exp, zero files)
- [x] GKAutopilot.cs ? 5 scripted demo sequences
- [x] 5 APK builds deployed to Quest 3 via MTP
- [x] App launches on Quest (correct scene, grid visible)
- [ ] C60 mesh visible in VR (test objects + debug logging in v4 APK)
- [ ] NSFlow.cs (Navier-Stokes solver port from JS)
- [ ] MNetNanite.cs (cluster DAG port from JS)
- [ ] Record 10-second VR clip via Quest capture
- [ ] Post to @Sagaific

### Phase 2 ? VR Atom Panel ??
- [ ] Equation panels in 3D space (Unity TextMeshPro, not KaTeX)
- [ ] Click atom ? equation floats up
- [ ] Click pentagon ? domain overview
- [ ] Hand tracking via Meta XR SDK

### Phase 3 ? Steam ??
- [ ] Electron is DEAD ? go Unity native
- [ ] $100 Steam Direct fee
- [ ] Store page: use Quest VR screenshots as capsule art
- [ ] Launch price: $10
- [ ] Ship

### Phase 4 ? Quest 3 Native ??
- [x] Unity ? Android build ? .apk (5 builds, IL2CPP ARM64)
- [x] MTP install pipeline working (no ADB needed)
- [ ] ADB direct deploy (pending Meta org verification)
- [ ] Hand tracking: pinch to refine, spread to undo
- [ ] Submit to Meta Quest store

---

## Technical stack (REAL, not aspirational)

```
STABLE RUNTIME:  Unity 6.3 LTS (6000.3.16f1) on Windows 11
PROTOTYPE:       mnet_v7.html (Three.js r128) ? crashes at scale
KERNEL (JS):     goldberg_kernel.js (vanilla JS, zero deps)
KERNEL (C#):     GoldbergKernel.cs (certified x30+, 18/18 tests)
RENDERER:        GKRenderer.cs v5 (URP Unlit, VR controls)
SOLVER:          Graph-discrete NS: PRESSURE + MOMENTUM + INTEGRATE + CAGE_BOUNCE
DAG:             MNetNanite ? physics-driven cluster LOD (Nanite-inspired)
BUILD:           IL2CPP, ARM64, URP, Meta OpenXR, XR Interaction Toolkit
VR HARDWARE:     Quest 3 (serial 2G97C5ZHBY017T) via USB/MTP
VR CAPTURE:      Quest built-in recording ? Meta app ? phone ? anywhere
PYTHON:          3.11 (MS Store) ? for patches, log analysis, scripting
GPU:             CUDA 12.4 available
META APP ID:     1559432698182 (org VladMnet, ID 1171537972700249)
```

---

## The key scientific finding

```
? = 2 (sphere topology):   residual 0.000091  ?  CONVERGES
? = 0 (M?bius topology):   residual 0.761927  ?  DIVERGES

Euler characteristic determines NS convergence on the graph.
Reproducible. Logged. 69 runs across 6 version folders.
```

---

## Environment Limits & Tricks

**OneDrive paths with spaces break tools:**
- `multi_edit` fails on `C:\Users\vladi\OneDrive\Desktop\python devs\...`
- Workaround: Python heredoc via PowerShell `$code | & $py`
- Or: write to `C:\Users\vladi\` then `Copy-Item`

**Python path:**
- `$py = "C:\Users\vladi\AppData\Local\Microsoft\WindowsApps\python3.11.exe"`
- `python` in PATH opens Store dialog ? always use full path
- Heredoc pattern: `$code = @'...'@ ; $code | & $py`

**Never read JSON logs directly:**
- 28-29MB each, 200K entries ? will crash terminal
- Always use Python: `json.load()` ? extract fields

**Browser crashes at scale:**
- Three.js r128 + 27K nodes + NS flow = tab crash
- This is why Unity is the real runtime
- Browser versions (v6, v7) are prototypes / demos only

**Quest 3 connection:**
- Shows as WPD (Windows Portable Device)
- USB 2.0 currently (USB 3.0 recommended)
- Air Link cert available but not in use
- Recording folder: `C:\Users\vladi\AppData\Local\Oculus\Recording\`

**File locations:**
```
MNetv1:     C:\Users\vladi\OneDrive\Desktop\python devs\MNetv1\
MnetUni:    C:\MnetUni\
JARVIS:     C:\JARVIS\
vault:      C:\vault\StrangerDanger\
machineG:   C:\machineG\  (SpookyPrimes)
Oculus:     C:\Users\vladi\AppData\Local\Oculus\
```

**CSV knowledge base:**
```
C:\Cchats\hex_bible.csv                ? 38 rows
C:\Cchats\navier_stokes_derivation.csv ? 13 rows
C:\Cchats\equations_as_code.csv        ? 3 equations
C:\Cchats\mnet_irreducible.csv         ? 11 functions
```

---

## The ADB Wall (every indie VR dev hits this)

```
SYMPTOM:  Unity builds APK (15 sec) but "No Android devices connected"
CAUSE:    Meta requires VERIFIED developer org before ADB activates
          Developer Mode toggles in headset are COSMETIC until verified
          The "Allow USB debugging" popup NEVER APPEARS until org verified
          
TIMELINE: Buy Quest -> create org -> verify org (hours/days) -> dev mode works
          There is NO instant path from "bought headset" to "deploying APK"
          
WORKAROUNDS WHILE WAITING:
  1. Meta XR Simulator (preview VR on monitor, no headset)
  2. Build APK to disk (File > Build), install later
  3. SideQuest drag-drop (once ADB works)
  4. Copy APK via MTP to Quest, install from file manager
  
OVR PROCESSES TO KILL (admin PowerShell):
  net stop OVRService
  taskkill /F /IM OVRRedir.exe
  taskkill /F /IM OVRServiceLauncher.exe
  
ADB DRIVER: Oculus ADB Driver v2.0 (installed)
ADB PATH:   C:\Program Files\Unity\Hub\Editor\6000.3.16f1\...\adb.exe
```

## What NOT to waste time on

1. ~~Electron packaging~~ ? Unity is the runtime
2. ~~Browser performance optimization~~ ? it crashes, move on
3. ~~sql.js in browser~~ ? use Unity + better-sqlite3 or SQLite4Unity
4. ~~WebXR from browser~~ ? Quest native via Unity is the path
5. ~~Re-reading entire conversation history~~ ? this MD is the source of truth

---

---

## GitHub Repos (all MIT licensed)

```
https://github.com/vsavytsk1/Mnet        ? Unity VR project (THE ACTIVE ONE)
https://github.com/vsavytsk1/Mnetv1       ? Browser prototypes (closed, history)
https://github.com/vsavytsk1/SpookyPrimes ? NCG research, dodecahedron
https://github.com/vsavytsk1/VALE         ? Local AI butler (private)
https://github.com/vsavytsk1/StrangerDanger ? Encrypted vault (private)

Live pages:
https://vsavytsk1.github.io/SpookyPrimes/ ? Dodecahedron of Open Questions
https://vsavytsk1.github.io/Mnet/         ? MachineNet v7 (browser, crashes at scale)
https://vsavytsk1.github.io/Mnetv1/       ? M?bius precursor
```

---

*Buenos Aires ? 2026-05-25*
*The cave is open. Unity is stable. The headset works.*
*5 APK builds. 30+ test runs. 50KB of documentation.*
*The C60 launches in VR. Now we make it visible.*
