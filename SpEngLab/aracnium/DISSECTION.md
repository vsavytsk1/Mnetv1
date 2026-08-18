# ARACNIUM — DISSECTION

Source: `shell/aracnium_v1_4_heave.html` · 66,961 B ·
`ARACNIUM v1.4 THE HEAVE -- spiders push a real tungsten cube`

Family on disk: `aracnium_v1_4_heave.html` (this one), `aracnium_heavenet_v2.0.html`
(32,354 B), `aracnium_relay_v1.0.html` (35,752 B).

---

## 1. THE THESIS, IN ITS OWN WORDS

**EXACT**, the file's own header comment, lines 7–21:

```
  ARACNIUM v0.8 LOCOMOTION -- step 4 of N
  Movement defined as a GRAPH of leg phase-relationships (CPG / gait
  graph): each leg is an oscillator node, the coupling pattern is the
  edge set -> tripod / wave / tetrapod are different graphs.

  Feet are PLANTED during stance (no sliding); body slides over them;
  legs solved by 2-link IK to world foot targets. Honest speed model:
  v = stride_length x step_frequency, read out in mm/s, m/s, BL/s with
  real-spider reference. Click the ground to set point B; it walks there.

  Verified before build: IK foot-hit 0mm, ground-click round-trip 0mm.

  K1 reduced 2-link IK (bend at "knee"), no full dynamics
  K2 leg rendered as 7 named segments = HIERARCHY
  K3 single HTML, software 3D, no GPU/WebGL
```

Note **"Verified before build"** — the pre-build gate discipline, already present here
before RUSTIUM ever wrote it down. And **K1/K2/K3** are declared limits, stated up front.
This file was written by someone following the cave's own laws.

---

## 2. MOVEMENT IS A GRAPH OF PHASES

This is the heart, and it is four lines.

**EXACT**, lines 304–314:

```js
function assignGaitOffsets(lg=legs){
  const g=GAITS[gaitIdx];
  const walk=lg.filter(l=>!l.tool); const k=walk.length;
  walk.forEach((l,i)=>{
    if(g==='TRIPOD' && k===6){ l.offset=((l.pair+(l.side>0?0:1))%2)*0.5; }
    else if(g==='TETRAPOD'){ l.offset=(i%3)/3; }
    else { l.offset=i/k; }
  });
}
function dutyFactor(){ const g=GAITS[gaitIdx]; const k=legs.filter(l=>!l.tool).length||1;
  if(g==='TRIPOD'&&k===6)return 0.5; if(g==='TETRAPOD')return 0.66; return Math.max(0.5,1-1/k); }
```

**A gait is nothing but a vector of constant phase offsets.**

| gait | offsets | duty factor β |
|---|---|---|
| **TRIPOD** (k=6) | `{0, 0.5}` — two anti-phase groups | 0.5 |
| **TETRAPOD** | `{0, ⅓, ⅔}` — three groups | 0.66 |
| **WAVE** | `i/k` — k evenly spread phases | `max(0.5, 1−1/k)` |

**COMPUTED:** the tripod offset `((pair + (side>0 ? 0 : 1)) % 2) * 0.5` puts a leg in group
0 or group 1 by the parity of `pair + side`. That is exactly the alternating-tripod
checkerboard — legs 1,3,5 on one side and 2,4,6 on the other move together. ✔

**Duty factor is not free:** β is the fraction of the cycle a leg spends planted. Tripod
β=0.5 means at every instant exactly half the legs are down (3 of 6 — the tripod). Wave gait's
`1 − 1/k` means only **one** leg is up at a time: slow, maximally stable. **The gait table is
a stability/speed trade-off expressed purely as phase spacing.** No forces are involved.

### The single clock, and the single line that reads it

**EXACT**, lines 525 and 530:

```js
if(active) gaitClock=(gaitClock+P.freq*dt)%1;
...
const phi=(gaitClock+lg.offset)%1;
```

One global scalar in `[0,1)`. Each leg's own phase is that scalar **plus its constant
offset, mod 1**. That is the whole central pattern generator. **This is the aracnium's
counterpart to PCBIUM's `path` array: the state that matters is small, integer-ish, and
discrete.**

---

## 3. NOTHING GLIDES — THE WITNESS

**EXACT**, lines 542–555, the stance/swing branch:

```js
} else if(phi<beta){                                    // STANCE
  if(lg.wasSwing || !lg.foot){ lg.foot=tgt.slice(); lg.wasSwing=false; }
  lg.slip=slip;
  if(slip){ /* no grip -> slide downhill, give no support */ }
} else {                                               // SWING
  const sp=(phi-beta)/(1-beta);
  if(!lg.wasSwing){ lg.liftFrom=(lg.foot||tgt).slice(); lg.wasSwing=true; }
  const fx=lg.liftFrom[0]+(tgt[0]-lg.liftFrom[0])*sp, fz=lg.liftFrom[2]+(tgt[2]-lg.liftFrom[2])*sp;
  lg.foot=[fx, terrainH(fx,fz)+arcH*Math.sin(Math.PI*sp), fz]; lg.slip=slip;
}
```

Read the stance branch carefully: **it contains no motion.** Unless the foot is slipping,
`lg.foot` is simply *not written*. The foot is a fixed world coordinate. The body moves:

**EXACT**, line 568: `bodyPos[0]+=hd[0]*v*moveScale*dt; bodyPos[1]+=hd[2]*v*moveScale*dt;`

> **This is THE ONE LAW, demonstrated.** The body's smooth glide across the terrain is
> assembled entirely from feet that are each, at every instant, either **nailed to a
> coordinate** or **being lifted along a half-sine**. Nothing in the system moves smoothly
> and continuously in contact with the ground. The smoothness is the *sum of the phases*.

The swing arc is the only sinusoid in the locomotion, and it is a lift, not a drive:
**EXACT**, line 517: `const beta=dutyFactor(), arcH=0.16*reach();` → height `arcH·sin(π·sp)`,
zero at both ends, peak at mid-swing. Foot placement in x/z is **linear** interpolation.

**HYPOTHESIS — and this is the folder's whole reason for existing:** a stepper motor is the
same object. Coils energise in a fixed cyclic pattern of phase offsets; the rotor snaps
between discrete equilibria; the shaft *appears* to rotate continuously. Gait offsets are
to a spider what commutation phases are to a stepper. **If that mapping is exact rather
than merely analogous, then a leg driver is a gait table and the whole control problem
changes shape.** Not tested. It is the most valuable untested claim we have.

---

## 4. THE HONEST BITS

Several things this file does that most sims do not:

**Speed is not a fudge factor.** **EXACT**, line 487: `const vMax=P.stride*P.freq, omegaMax=(25*Math.PI/180)*P.freq;`
Velocity is *derived* from stride and step frequency, not set. Defaults, **EXACT** line 269:
`nLegs:8, stride:62, freq:1.5, sub:1` → **COMPUTED:** 62 mm × 1.5 Hz = **93 mm/s**. The HUD
also reports body-lengths/s against a real-spider reference (**EXACT**, line 144: *"fast
spiders ~20–50 BL/s via very high stride frequency (hydraulic legs)"*).

**Support gates motion.** **EXACT**, lines 562–569:

```js
supportFrac = walk? support/walk : 1;
const moveScale=supportFrac, turnScale=Math.max(0.3,supportFrac);
```

Only feet that are planted **and gripping** count. Lose footholds on a slope and the spider
**stalls** rather than sliding forward — the failure is emergent from the phase model, not
scripted.

**Body height is a constraint solve, not an animation.** **EXACT**, lines 573–574:

```js
if(stanceY.length){ const avg=stanceY.reduce((a,b)=>a+b,0)/stanceY.length;
  byTarget=Math.min(avg+P.ride, Math.min.apply(null,clampUp)); }
```

Ride height is the average gripping-foot height plus `ride`, **clamped so no leg is asked to
exceed its reach** (`clampUp` is per-foot: `foot.y + sqrt(reach² − horizontal²) × 0.95`).
The body is pushed down by whichever leg is most stretched. That is a real constraint.

**Slipping is modelled.** No foothold → the foot slides down the terrain normal at 70 mm/s
and contributes **zero** support.

**Seven named segments.** **EXACT**, line 272:
`const SEG=['coxa','troch','femur','patella','tibia','meta','tarsus'];`
The real arachnid segment names, in order. K2 declares this is a rendering hierarchy — the
IK is 2-link (K1), so the seven segments are drawn, not independently solved. **Stated,
not hidden.**

**Terrain is deterministic**, not noise: a dome, a hill shoulder, a sine undulation and a
logistic escarpment (lines 335–339). Reproducible runs. ✔

---

## 5. WHAT THE RUST PORT DOES NOT YET HAVE

**This lane is empty in `Gos/`.** Nothing in the Rust kernel touches locomotion. Unlike the
pcbium lane — which inherits the certified C60, the judge and the gate — aracnium starts at
zero. That is worth saying plainly rather than discovering later.

| from ARACNIUM | status in `Gos/` |
|---|---|
| `gaitClock` + per-leg constant offsets | ✘ |
| gait table (TRIPOD / TETRAPOD / WAVE) with duty factors | ✘ |
| stance/swing branch on `phi < β` | ✘ |
| 2-link IK to world foot target | ✘ |
| 7-segment leg hierarchy | ✘ |
| support-fraction gating of body velocity | ✘ |
| deterministic terrain + foothold query | ✘ |

### The first honest step

**A gait is a pure function with no floats in its essential part.** `offset` is a rational
(`0`, `1/2`, `i/3`, `i/k`); `phi < β` is a comparison; the leg's *state* is one bit —
**stance or swing**. So the first Rust artifact in this lane can be integer-exact:

```rust
// phases in units of 1/LCM, so no float ever decides stance vs swing
pub fn phase(clock: u32, offset: u32, period: u32) -> u32 { (clock + offset) % period }
pub fn planted(phi: u32, beta_num: u32, beta_den: u32, period: u32) -> bool {
    phi * beta_den < beta_num * period      // exact, no rounding
}
```

**DESIGN CHOICE, and the point:** the stance/swing decision is the one place where a float
comparison could make two runs of the same gait differ. Doing it in integers makes the gait
**bit-reproducible** — the same property `judge.rs` gives the mesh. The spider gets a judge
of its own: *at every instant, the number of planted legs must equal the gait's duty count.*
That is a checkable invariant, it is violated by any phase bug, and it is exactly the kind
of thing AXIOM 01 was written for.

**The gait table is the aracnium's `P=12`.** Find its invariant, judge it before build.
