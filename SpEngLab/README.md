# SpEngLab — the Spider Engineering **Laboratory**

**The hardware lane of the cave.** Two targets, one law.

> ## ⚠ THIS IS THE LAB, NOT THE PRODUCT
>
> There are **two repos**, and they are not peers:
>
> | repo | role | what it is |
> |---|---|---|
> | **MNetv1** (here) | **the physics laboratory** | where a claim is *validated*. Sims, kernel, judge, grimoire. Things are allowed to be wrong here. |
> | **SpiderEngineering** ([github](https://github.com/vsavytsk1/SpiderEngineering)) | **the implementation** | where a validated thing is *shipped*. `aracnium.toml`, firmware, hardware, BOM, fleet. |
>
> **The flow is one-way: validate here → push there.** Nothing enters
> SpiderEngineering that has not been judged in the lab first. Nothing in the lab
> claims to be buildable.
>
> `SpEngLab/aracnium/` and `SpEngLab/pcbium/` are the lab benches for the two
> lanes that already have real folders in the other repo. Same names on purpose —
> the bench and the product line up one-to-one.
>
> See §6 for the integration contract and what is currently broken over there.

```
SpEngLab/            <- the LAB. physics validated here, shipped to the other repo.
  README.md          <- you are here: the law, the map, the reason
  TITANS.md          <- who we borrowed from, under what licence, and the WALL
  aracnium/          <- the MOVEMENT lane   (how a body gets somewhere)
    DISSECTION.md
  pcbium/            <- the BOARD lane      (how copper gets somewhere)
    DISSECTION.md
  _titans/           <- GITIGNORED. two shallow clones, 130 MB, never pushed.
```

Status grammar is Thea's, unchanged:
**EXACT** (from the source, quoted) · **COMPUTED** (derived here, arithmetic shown) ·
**DESIGN CHOICE** (we picked it, could be otherwise) · **HYPOTHESIS** (untested claim) ·
**METAPHOR-EXTERNAL** (a picture, not a proof).

---

## THE ONE LAW

> **Nothing continuous is ever built.
> Continuity is a sampling artifact of a discrete process run fast enough.**

This is not philosophy. It is the single shared invariant of both our sims, and it is
why the pair belongs in one folder. Four witnesses, all already on our disk:

### Witness 1 — PCBIUM refuses the curve

**EXACT**, from `shell/pcbium-v2_9_5.html:190`:

> *"PURE GRAPH SPACE. No curve is ever drawn. A trace is a path hopping vertex-to-vertex
> along the mesh edges (Dijkstra shortest path) — points and lines only. The 'curve' is
> just the illusion a fine grid makes from a distance, exactly like pixels on a screen."*

A trace is not a shape. It is a **list of vertex indices**. The smooth copper you think
you see is the graph, sampled by your eye.

### Witness 2 — ARACNIUM refuses the glide

**EXACT**, from `shell/aracnium_v1_4_heave.html:530,542`:

```js
const phi=(gaitClock+lg.offset)%1;
...
} else if(phi<beta){          // STANCE
```

During stance the foot **does not move at all** — it is a planted world coordinate and the
body slides over it. The body's smooth translation is manufactured entirely out of feet
that are each, individually, either nailed down or being lifted. Nothing glides. The
gliding is the sum.

### Witness 3 — the machines that would build it

**HYPOTHESIS** (the user's, and I think it is right): every machine in the chain that
makes a PCB or a leg real — stepper motor, pick-and-place gantry, laser galvo, the mill —
moves by **combining phase-offset waves**. A stepper does not rotate; it snaps between
energised coil states, and the sequence of snaps is what looks like rotation. There is no
straight line inside the machine.

So a designer who thinks in straight lines is describing something the fab cannot do, and
the CAM step silently re-discretises it. **We would rather design in the fab's own
language from the start** — hence pure graph space, hence phase offsets. This is the
reason for the whole folder.

### Witness 4 — the screen you are reading this on

**EXACT**: the pixels are not square. They are subpixel triads (typically RGB stripes),
and "square pixel" is a convenience fiction of the coordinate system. The monkey brain is
tricked twice — once into seeing a line where there are samples, once into seeing a square
where there are three coloured slots.

---

## WHY THE SILICON PORT IS HARD

**HYPOTHESIS**, and the sharpest thing this folder has to offer so far:

| | a CPU | a spider |
|---|---|---|
| clock | **one**, global, synchronous | **N coupled oscillators** |
| state advance | every element on the same edge | each leg on its own `phi` |
| coupling | the netlist, solved to fixpoint | the gait graph (an edge set) |
| in our code | `half_cycles` (Slow-Silicon) | `(gaitClock + offset) % 1` |

A CPU is a machine that has **agreed to share one phase**. A spider is a machine whose
entire competence is in **refusing to**. Tripod gait *is* two anti-phase groups; wave gait
*is* eight evenly-spread phases. Take the phase offsets away and the spider falls over.

Porting spider movement to silicon is therefore not a matter of speed or transistor count.
It is the cost of embedding **many phases into one clock** — you must either run N phase
accumulators in the synchronous fabric (area) or timeslice them (latency). That is the
hard part, and it is a *structural* cost, not an engineering-effort cost.

This is exactly why **Slow-Silicon** is the right titan to study: it shows a synchronous
machine one half-cycle at a time, so the thing we are up against is visible rather than
assumed. See `TITANS.md`.

---

## THE TWO LANES, AND WHERE THE RUST PORT MEETS THEM

Both lanes already exist as HTML sims. `Gos/` is the Rust port. The mapping:

| lane | our sim | the invariant | what `Gos/` already has |
|---|---|---|---|
| **pcbium** | `pcbium-v2_9_5.html` | a trace is a vertex-index path on a certified closed mesh | `judge.rs` (V−E+F=2), `sphere.rs`, the C60 mesh, the pre-build gate |
| **aracnium** | `aracnium_v1_4_heave.html` | a pose is N phases mod 1, on a 7-segment tree | *nothing yet* — this is the open lane |

The pcbium lane is **the same topology the Rust kernel already certifies**: PCBIUM's board
literally is the truncated icosahedron, 12 pentagons kept out, 20 hexagons routable. AXIOM 01
(`P=12`, `V−E+F=2`, or do not ship) already governs it. **DESIGN CHOICE:** the board is a
closed surface so a trace has no edge to fall off — the same reason the whole cave is built
on χ=2.

The aracnium lane has **no certified structure yet**. That is the next thing to build.

---

## 6. THE INTEGRATION CONTRACT (surveyed 2026-08-18)

The implementation repo was surveyed in full before any integration was designed.
**952 files, 118,937,856 B, `.git` only 21,785,082 B, working tree clean, `main` at
`26cf44a`.** It is in far better shape than the lab's own git (`MNetv1/.git` is ~1,037 MB).

### What is already built over there

`aracnium/` is **real**: `spec/aracnium.toml` (the canonical spider — body, 7 named leg
segments, IK reduction, actuation, gait graph, physics limits, grip), `INVARIANTS.md`
(K1–K3 + R1–R3), `tools/build_fleet.py`, `fleet/fleet.toml`, the full 14-version sim
lineage v0.6→v1.4, `docs/aracneBioMechanics.md` (31 KB), and **119 KB of electronics
scrolls** in `hardware/grimoir/` (THE_PCB_GRIMOIRE, FractalPCB, ELECTENGMAGIC,
ELECTENG_MAGIC_4to5, OsciloPCBmagic). `pcbium/` holds `PCBIUM_HANDOFF.md` and
`PCB_DESIGN_HISTORY.md` (37 KB). `Eleni/` holds the whole HELENA engine.

**COMPUTED — `build_fleet.py` runs and is correct.** Verified by execution:

```
design      : aracnium / mk1 (v1.4-heave)      fingerprint : fda403b08801
servos/unit : 24  (8 legs x 3 joints)          fleet count : 1
leg reach   : 171.0 mm  (link1 85.0 + link2 86.0)
PROOF       : all 1 units share design fda403b08801 -> IDENTICAL [OK]
```

Re-derived by hand from `spec/aracnium.toml`: link1 = 18+8+45+14 = **85.0** ✔;
link2 = 40+30+16 = **86.0** ✔; reach **171.0** ✔; servos 8×3 = **24** ✔. R1/R3 are
genuinely tool-enforced. The run wrote only into `fleet/generated/`, which is gitignored —
the repo stayed clean.

### ⚠ Three defects found, all in the *plumbing*, none in the design

**D1 — the README's quick-start command does not exist.** README §"Build one spider" and
§"Quick start" both say `py -3 tools/build_fleet.py`. There is **no `tools/` at repo root**.
Verified: `exit=2, No such file or directory`. The working command is
`py -3 aracnium/tools/build_fleet.py`.

**D2 — `build_fleet.py` at repo root is dead code that cannot run.** It is byte-identical
to `aracnium/tools/build_fleet.py` (`F096245C…`), but the script resolves its own spec with
`ROOT = Path(__file__).resolve().parent.parent`. From the root copy that resolves to
`C:\PythonDevs\`, so it looks for `C:\PythonDevs\spec\aracnium.toml`. Verified:
`ERROR: missing spec\aracnium.toml, exit=1`. **A copy of the build tool that always fails.**

**D3 — the single source of truth exists twice.** `aracnium.toml` at repo root and
`aracnium/spec/aracnium.toml` are **byte-identical** (`25B417F6…`) with nothing keeping them
so. Invariant **R1** says *"Geometry, gait, and limits are defined once, in
`spec/aracnium.toml`."* Only the `spec/` copy is ever read. The root copy is a second
place to edit that no tool checks — **R1 is not violated today, but nothing prevents it
tomorrow.** This is the exact failure mode R1 was written to prevent.

**HYPOTHESIS on cause:** all three are one event — files were moved from repo root into
`aracnium/` and the originals were never deleted, while the README kept the old paths.
Root `index.html` and `GIT_INCIDENT_001_MNETV1.md` are legitimately root-level; the other
two are residue.

**Fix (theirs to make, not ours to sneak in):** delete root `aracnium.toml` and root
`build_fleet.py`, correct the two README paths. Three deletions and two string edits. It
should ship as its own commit with its own message, because D3 deserves to be recorded as
an invariant near-miss, not buried.

### The lineage discovery that matters most

`PCBIUM_HANDOFF.md` §4 records that **v2.5 was literally the stepper-motor version** —
*"traces bow into spherical quadratic Bézier arcs (a curvature DOF), rendered as N discrete
stepper moves; 'show steps' reveal. 'A curve is points and lines.'"* — and **v2.9 then
killed every Bézier** in favour of pure Dijkstra graph paths.

So THE ONE LAW at the top of this file is not a new idea we brought back from the titans.
**It is the conclusion the pcbium lineage already reached, by building the curve and then
deleting it.** The lab's job now is to say *why* that was right, in a form the Rust kernel
can check. That is a much better position to start from than a blank page.

### The contract, stated

1. **The lab never edits the product's spec.** `spec/aracnium.toml` is theirs. The lab
   *reads* it and may propose a diff, never apply one.
2. **Only judged things cross.** A thing leaves `SpEngLab/` when it has a kernel check that
   fails loudly — the same bar as AXIOM 01. Sims and dissections stay in the lab.
3. **The `.toml` is the interface.** Both repos agree on one file format. The Rust port's
   locomotion lane should *parse* `aracnium.toml`, not re-declare the geometry — that is
   their R1 extended across the repo boundary, and the only honest way to have two repos.
4. **The 130 MB of `_titans/` never crosses either wall.** Ideas cross; payload does not.
5. **Their licence is MIT and clean. Slow-Silicon's die data is NOT.** See `TITANS.md`.
   The product repo is MIT; a CC BY-NC-SA artifact must never land in it.

---

## STATE

- [x] our own two sims dissected — `aracnium/DISSECTION.md`, `pcbium/DISSECTION.md`
- [x] titans cloned to `_titans/`, gitignored, licences recorded in `TITANS.md`
- [x] implementation repo surveyed in full; `build_fleet.py` run and its arithmetic re-derived
- [x] three plumbing defects found (D1–D3) — **reported, not silently fixed**
- [ ] hand D1–D3 to the product repo as one commit
- [ ] `hardware/pcb/` and `hardware/cad/` are **empty `.gitkeep`s**, and
      `hardware/grimoir/PCB_MAGIC.md` is **0 bytes** — that is the hole the pcbium
      graph-designer is meant to fill. It is the clearest open target in either repo.
- [ ] decide: does the aracnium leg tree get a URDF, or its own certified format?
- [ ] read `slow-silicon/site/js/format.js` against `FORMAT.md` (they must not drift)

**P=12. χ=2. There is no straight line in the machine.**
