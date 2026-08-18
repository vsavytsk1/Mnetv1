# ARACNIUM — THE EXPORT CONTRACT

*What leaves the lab, in what format, for which machine, and what each one refuses to carry.*

The insight this folder is built on is that **this part is simple**. Going from idea space
to reality is not a wall of proprietary complexity — it is a **handful of very old text
formats**, most of them from the 1970s and 80s, all of them integer lattices underneath.
The machines are unforgiving but they are not mysterious. What is hard is having something
*correct* to export. We have spent the whole cave on that half.

---

## 1. THE FIVE FILES

Everything a fab or a shop needs, from us, is one of these. There is no sixth.

| # | file | format | the machine | our writer |
|---|---|---|---|---|
| 1 | `*.gbr` | **Gerber RS-274X** | photoplotter → copper | `Gos/src/fab.rs::Gerber` ✔ |
| 2 | `*.drl` | **Excellon** | the drill | `fab.rs::Excellon` ✔ |
| 3 | `*.stl` | **binary STL** | slicer → printer; CAD import | `fab.rs::stl_binary` ✔ |
| 4 | `*.dxf` | **DXF R12** | laser, waterjet, router, every CAD | `fab.rs::dxf_lines` ✔ |
| 5 | `*.step` | **STEP AP214** | real CAD interchange, solid bodies | **not built** — see §4 |

**COMPUTED**, from `cargo run --example fab_export` on the certified C60:

```
AXIOM 01   : P=12, chi=2 -- PASS, export permitted
c60_shell.stl    5884 B  = 84 + 116*50    116 = 12 pentagons*3 + 20 hexagons*4
c60_top.gbr      5402 B  2 apertures, 60 pads flashed
c60.drl          1252 B  1 tool, 60 hits
c60_outline.dxf  9266 B  86 LINE entities
90 edges -> 86 drawn, 4 dropped at the seam
gerber checksum : eb077b73f22f8e51
```

---

## 2. THE WALL — and why every one of these is integers

**EXACT.** Gerber declares its coordinate format in the header (`%FSLAX46Y46*%` = 4 integer
digits, 6 decimal digits) and every coordinate after that is a **plain integer** in units of
10⁻⁶ mm. Excellon is the same. G-code step counts are the same.

> The tower — 1s and 0s → gates → assembly → C → C++ → Python → float64 — exists so a
> **human** can hold the complexity. It terminates here, at the fab wall, back in integers
> on a lattice. **The float was never in the machine.**

So the export path has exactly one float-to-integer decision, `fab.rs::quantise()`, and it
is checked and loud. A test asserts that no coordinate line in a Gerber file may contain a
decimal point — a `.` in an `X…` line is a **test failure**, not a style note.

This is why the sphere→plane projection sits *upstream* of the wall and is labelled
DISPLAY: `atan2` and `asin` are not correctly rounded, so the projection may never be
asserted bit-exact. Once quantised, it never moves again.

---

## 3. WHAT EACH FORMAT REFUSES TO CARRY

Being clear about this is the difference between an export and a lie.

**Gerber** carries copper geometry and nothing else. No nets, no components, no stackup, no
impedance. A Gerber cannot tell a fab that two pads are the same net — that is what IPC-356
netlist files are for, **which we do not emit**. A fab will happily build a board that is
electrically wrong and geometrically perfect.

**Excellon** carries hole positions and diameters. It does **not** distinguish plated from
non-plated unless you split it into two files by convention. Ours are one file; a real order
needs the split.

**STL is the worst format we ship, and we ship it because everything reads it.** No units
(the file does not say mm or inches — we assume mm, and so does most of the world, and
"most" is doing real work in that sentence). No topology: every vertex appears three times,
so a closed surface and a pile of loose triangles are byte-indistinguishable.

> **Our closedness lives in `judge.rs`, not in the file.** The STL is a *shadow* of a
> certified object. The certificate stays home. This is not a flaw to fix — it is the
> reason the judge exists at all.

**DXF R12** carries 2D lines on named layers. We emit R12 specifically because it is the
last version everyone agrees on.

**The seam.** Our panel export drops **4 of 90 edges** — those crossing the antimeridian,
where equirectangular unwrap would plot a false line straight across the board. The count is
printed on every run. And equirectangular *stretches at the poles* (Gauss's *Theorema
Egregium* — the same theorem that forces the 12 pentagons). **A pole-crossing board must not
be sent to a fab on the strength of this projection.** A faithful panel needs a conformal or
local-patch projection, which is not built.

---

## 4. THE TWO REAL GAPS

**STEP (AP214).** The only format on the list that is genuinely hard — it is a full B-rep
solid interchange, not a triangle soup, and hand-writing one is a project. Two honest
options:

- **(a)** stay with STL and let the shop convert. Free, lossy, works today.
- **(b)** use the titans' `text-to-cad` `cad` skill (MIT, exports STEP/STL/3MF) as the
  bridge, rather than writing an AP214 writer ourselves. See `../TITANS.md`.

**Not decided.** DESIGN CHOICE pending, and (b) is only attractive because their licence is
clean MIT.

**URDF, for the leg tree.** The aracnium is 8 legs × 7 named segments — a kinematic tree,
which is exactly what URDF serialises, and `text-to-cad` ships `urdf` + `srdf`/MoveIt2 for
the IK. The open question from `../README.md` stands: does the leg get URDF (a standard with
real solvers, but **no judge** — nothing in URDF checks that a tree is closed, reachable or
sane), or its own certified format?

**The likely honest middle:** certify internally, **emit** URDF as a display-lane artifact —
the same certified/display split as RULE 0. Stated as a leaning, not a decision.

---

## 5. WHERE THIS LANDS IN THE PRODUCT REPO

The implementation repo (`vsavytsk1/SpiderEngineering`) already has the folders, and they
are **empty**:

```
aracnium/hardware/pcb/           .gitkeep only   <- files 1, 2 land here
aracnium/hardware/cad/           .gitkeep only   <- files 3, 4, 5 land here
aracnium/hardware/grimoir/PCB_MAGIC.md   0 bytes <- the scroll that explains them
aracnium/hardware/bom/bom.csv    578 B           <- exists, scaled by build_fleet.py
```

That hole is exactly this shape. **Nothing crosses until it is judged** — the one-way
contract in `../README.md` §6.

**The gate is already written and already runs.** `examples/fab_export.rs` refuses to export
anything that has not passed AXIOM 01:

```rust
assert_eq!(cert.p, 12, "AXIOM 01: P=12 or do not ship");
assert_eq!(cert.chi, 2, "AXIOM 01: chi=2 or do not ship");
```

**The missing piece is routing, and only routing.** `route.rs` — binary-heap Dijkstra over
`Mesh::adj`, pentagons excluded as destinations. One test (*a route never contains a
pentagon vertex*), one property (*`route(s,t)` and `route(t,s)` agree in length*). Once that
exists, a designed board can be routed, judged, quantised and plotted end to end without a
single new dependency.

---

## 6. AND THE SPIDER ITSELF

The parts above build the *board*. The spider also needs its geometry to reach a shop, and
that path is shorter than it looks: `aracnium.toml` already holds every dimension
(7 segments, body discs, tube stock), `build_fleet.py` already derives reach = 171.0 mm =
85.0 + 86.0 and 24 servos, and `fab.rs::dxf_lines` already writes the format a laser cutter
eats.

**The lab owes the product repo one thing here:** a reader for `aracnium.toml`, so the Rust
lane *parses* the spec rather than re-declaring the geometry. That is their invariant **R1**
extended across the repo boundary, and it is the only honest way to have two repos.

> The equal sign is the transcendental tool. Graph math is the most efficient implementation
> this reality permits, and the price is paid in information, energy and compute.
> **P=12. χ=2. There is no straight line in the machine.**
