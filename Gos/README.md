# Gos — the Goldberg kernel, in Rust

> *A fullerene is the only closed structure you can build from pentagons and
> hexagons. Euler proved it. Chemistry confirmed it. Here it is in Rust, with
> a window, a command line, and receipts.*

**Zero dependencies.** Not "few" — none. `[dependencies]` is empty and stays
empty; the four crates in the workspace are all ours. `#![forbid(unsafe_code)]`
holds across the kernel, so it can never own a window — that is why the
`unsafe` lives in one small FFI crate and nowhere else.

```
17 modules · 11 examples · 137 tests · clippy zero · fmt clean
```

---

## Quick start

```powershell
# the toolchain (once) -- see THE LINKER TRAP below, this matters
rustup toolchain install stable-x86_64-pc-windows-gnu

cd Gos
cargo +stable-x86_64-pc-windows-gnu test --workspace     # 137, must be green
cargo +stable-x86_64-pc-windows-gnu build --release --workspace

# then look at something
.\target\release\gos_viewer.exe --max
.\target\release\gos_orb.exe --max
```

### THE LINKER TRAP

`winget install Rustlang.Rustup` exits 0. `rustc --version` answers. Then the
first build fails:

```
error: linker `link.exe` not found
note: the msvc targets depend on the msvc linker
```

**`rustup` installs a compiler, not a linker.** The default Windows target
delegates linking to Microsoft's `link.exe`, which ships with Visual Studio —
a separate multi-gigabyte install that rustup neither bundles nor mentions
until link time. An installer's exit code certifies the *download*, never the
*capability*.

The GNU target bundles its own linker and needs no Visual Studio. This crate
has zero dependencies and no C FFI, so the two toolchains are interchangeable
here — that is a property of *this* crate, not a general truth.

---

## The two programs

Both do the same three things: open a window, or run a script and exit, or
refuse and say why. Both are driven by the **same methods** whether a mouse or
a script calls them, so a scripted run drives the shipped program and not a
parallel copy of it.

| | `gos_viewer` | `gos_orb` |
|---|---|---|
| subject | the Goldberg mesh, refined | a file's bytes on an icosphere |
| default input | — | its own executable |
| controls | 7 | 3 |

### Common flags

```
--max                  canvas = the client area of a full-screen window
--size 3840x2160       any canvas, no recompile. Both axes forced EVEN.
--run "<steps>"        run steps headless, write files, exit
--script <file>        the same, from a file
--help
```

Exit code is the number of failures, so it composes with `&&`.

**Why even axes:** `yuv420p` subsamples chroma 2×2, so H.264 cannot encode an
odd width or height. An odd canvas would render and shoot perfectly and then
fail only at `movie`, which is the worst place to find out. Rounding is
announced, never silent.

---

## `gos_viewer` — the mesh

```powershell
gos_viewer --run "card 1; refine all; refine 6s; inner 0.78; mid 0.32; shot bursts"
```

### Steps

`;` or newline separated, `#` comments.

| step | what |
|---|---|
| `shot <name>` | render and write `<name>.png` **from the framebuffer** |
| `card <n>` | click card *n* on the dashboard |
| `button <LABEL>` | click a button by name |
| `panel` `back` `shell` `palette` | sugar for those buttons |
| `key <c>` | press a key |
| `spin <n>` | advance the turn *n* frames — deterministic, **not a sleep** |
| `expect <View>` | the current view must be this, or FAIL |
| `status` | print the status line |
| `stats` | what the frame is made of, in OKLab |
| `controls` | every control, its value, its range, its units |

### The GENESIS control bar

| step | what |
|---|---|
| `seed c60 \| 12` | reseed. `12` is not built yet and says so |
| `refine all \| 5s \| 6s` | one refinement, priced before it is allocated |
| `undo` `reset` | step back, or back to the seed |
| `cull` | drop the far hemisphere — see **THE INTERFERENCE** below |
| `zoomin` `zoomout` | one multiplicative step; ×2 every four presses |

### Controls

Every one is a numeric box on the panel, a command-line verb, **and** a movie
channel — because they come from one table. Adding the next control is a row
plus two match arms, and it arrives animatable.

| name | range | what |
|---|---|---|
| `inner` | 0.05–0.95 | where the inner ring sits |
| `mid` | 0.05–0.95 | where the mid ring is pulled to |
| `jitter` | 0–0.20 | symmetry-breaking; 0 is off |
| `sphere` | 0.5–3.0 | projection radius when spherical |
| `yaw` | 0–2π | the turn |
| `zoom` | 0.25–6.0 | multiplier on the fitted zoom |
| `speed` | 0–0.25 | turn per frame; 0 holds it still |

```powershell
gos_viewer --run "inner 0.78; mid 0.32"     # set them
gos_viewer --run "jitter shoe"              # 'shoe' IS NOT A NUMBER
gos_viewer --run "inner nan"                # 'nan' IS NOT FINITE
gos_viewer --run "yaw 99"                   # 99 IS OUTSIDE 0..6.283185
```

On any refusal **the old value stands**. The `nan` case is the one that
matters: `"nan".parse::<f64>()` *succeeds*, so a parse check alone would have
accepted it and quietly poisoned every frame downstream.

### INNER and MID are the picture

```
MID > INNER   the ring opens         ROSETTE
MID < INNER   the ring overlaps      BURSTS
MID = INNER   the ring closes flat   maximum interference
```

The spec calls this the **crescent defect** and says plainly: *not a bug to
fix — it is the picture.* A port that "corrects" it renders different images
and has failed. The viewer opens at `0.1 / 0.1`, at `MID = INNER`.

---

## `gos_orb` — the byte topology

```powershell
gos_orb                          # streams its own machine code
gos_orb some_file.bin            # streams that instead
gos_orb --run "sweep 0-8; expect chi=2"
```

Streams a file's bytes onto a certified icosphere, one block per face. By
default that file is **its own executable**, so it draws a portrait of the
build that produced it — run it after every build and the diff is a diff of
the code's own shape.

| step | what |
|---|---|
| `level <n\|+\|->` | absolute level, or one step. `n` is 0–8 |
| `sweep <a>-<b>` | shoot every level a..b — the growth, in order |
| `spin <n>` `palette` `shot <name>` `status` `stats` | as the viewer |
| `expect <k>=<v>` | `level` `faces` `chi` `genus` |
| `yaw <v>` `speed <v>` | its two continuous controls |

```
L0        20 faces  34810 B/face  chi 2
L1        80 faces   8703 B/face  chi 2
...
L8   1310720 faces      1 B/face  chi 2
```

---

## Movies

```powershell
gos_viewer --run "card 1; refine all; movie yaw 0 6.283185 180 turn mp4"
```

```
movie <control> <lo> <hi> <frames> <name> [png|mp4|both] [fps] [crf]
```

Deterministic frame by frame: the control is **set from the frame index**,
never accumulated from a clock, so the same command rewrites the same bytes.
That only works because the render time was taken *out* of the frame — a clock
in the pixels makes a frame unreproducible.

### Priced in both currencies, before the first frame

Bytes are **exact**, not estimated: our PNG uses stored deflate, so a frame's
size is a pure function of the canvas. Time is **measured**: one real frame is
rendered and multiplied.

```
movie yaw 0 6.28 40000 epic mp4

  40000 frames @ 60 fps = 11m 06s of footage
  render ~32m 52s (one frame measured)
  disk 0 bytes -- frames are piped, never written

REFUSED - this would render for 32m 52s, past the 20m 00s ceiling. One frame
at the current 68612 faces took 49 ms, and that is measured, not guessed.
```

### `mp4` writes no frames at all

ffmpeg is started with `-f rawvideo -pix_fmt rgb24` and each framebuffer goes
straight to its stdin — the exact buffer the kernel computed. No PNG encode,
no filesystem, no round trip.

```
180 frames at 1920x1080:  intermediate would be 1.07 GB, actual is 0 BYTES
```

**We do not own H.264 and do not pretend to.** The job goes to ffmpeg — which
is libavcodec, which is the engine under VLC. `[dependencies]` is still empty:
ffmpeg is a *tool* invoked through `std::process`, found by **running** it
rather than by trusting a path. If it is absent the run says so and leaves the
exact command in `MAKE_MP4.txt`, so the chain reproduces without us.

`yuv420p` chroma-subsamples, which softens coloured edges. It is required for
the file to play in browsers, on phones and in QuickTime. The PNG frames stay
the source of truth; the mp4 is a lossy convenience.

| canvas | per frame | 60 frames |
|---|---|---|
| 1920×1080 | 5.93 MB | 0.35 GB |
| 3840×2160 | 23.73 MB | 1.39 GB |
| 7680×4320 | **94.93 MB** | 5.56 GB |

One 8K frame is five megabytes short of the 100 MB limit that bounces an
entire push. Nothing at that size is ever tracked.

---

## What lands on disk

`runs/` holds every session. The **payload is local and gitignored**; the
*steps* travel:

| tracked | not tracked |
|---|---|
| `SESSION.json` `MANIFEST.json` `LAYOUT.json` | `*.png` `*.mp4` `*.bits` `*.bin` |
| `SHOTS.log` `DRIVE.log` `MOVIE.json` `MAKE_MP4.txt` | |

A frame is a **cache, not a record** — `--run` regenerates it byte for byte,
so the payload never needs to travel. Every scripted run prints what `runs/`
holds, and past 2 GB it names the heaviest folders oldest-first and says how
much moving them would recover.

---

## THE INTERFERENCE

There is **no depth buffer and no back-face culling** by default. Every face is
an alpha-blended wireframe, painter-ordered by depth, so far faces draw first
and near ones blend *over* them rather than occluding. What you see is the back
lattice superimposed on the front at a different projected scale — a genuine
moiré between two copies of the same mesh.

`cull` turns it off, and the difference between the two views is the point.

Sweeping the view through a full turn and measuring every frame, **every
significant rotational harmonic is even** — m = 2, 4, 6, 8, 10, 12 — with the
odd ones one to two orders of magnitude down. The first explanation offered was
that the see-through render imposes its own 2-fold symmetry. A prediction
followed: cull, and the odd harmonics should rise.

**They fell.** m=3 dropped 10×.

The real cause: the shell is **centrosymmetric** — `-v` is a vertex for every
vertex `v`, asserted in `the_c60_is_centrosymmetric`. So the projection from
`d` and from `-d` differ only by an inversion, any global scalar of them is
equal, and `f(yaw) == f(yaw + π)` for *any* renderer at all. Only even
harmonics can survive. It is a property of the shell, which is exactly why
culling did not touch it.

---

## Examples

```powershell
cargo run --release --example <name>
```

| example | what |
|---|---|
| `kaboom` | push the fractalization until the allocator gives up |
| `genesis_refine` | the browser's ladder, built as real polygons |
| `gate` `gate_cascade` | the pre-build closure gate |
| `fab_export` | Gerber, Excellon, STL, DXF — integers all the way out |
| `float_wall` | where binary64 stops resolving |
| `cross_check` | our f64 ladder against a C# VR app's binary32 |
| `paint_c60` `paint_dashboard` `orb_growth` `eml_search` | renders |

### `kaboom`, and what it found

Each depth runs in its **own process**, because a Rust allocation failure
aborts rather than unwinding and cannot be caught from inside the process that
caused it.

```
depth 7   24,706,292 faces   10.49 GB   chi=2   SURVIVED
depth 8  172,944,032 faces   DIED -- allocation of 6,106,906,624 bytes failed
                             exit 0xC0000409 -- the allocator gave up
```

Two findings came out of it:

**A face costs about 3× what the points alone suggest, and the error grows with
depth.** `pts` is flat at 144 B/face forever — six points, always — while
`lineage` gains a `usize` per level and `id` gains characters per level. At
depth 7 the ids alone are 2 GB. Ratio: 2.01× at depth 1, **3.09× at depth 7**.

**`refine` holds both generations at once**, so the peak is `old + new` ≈ 8× the
current mesh, not the size of the result. Depth 8 died asking for 6.1 GB while
already holding 10.5 — nowhere near the 84 GB the finished mesh needed. A
budget that checks only the result will pass steps that cannot run.

---

## The certified path and the display path

The one architectural idea in the crate.

JavaScript `Number` and Rust `f64` are both IEEE-754 binary64. For `+ - * /`
and `sqrt` both are **correctly rounded**, so results are bit-identical and a
port is a *translation* rather than a reimplementation.

`sin` `cos` `exp` `ln` `powf` `hypot` `cbrt` carry no such guarantee — not
across platforms, not between JS and Rust. They agree to about an ulp, never
exactly.

* **certified** — integers, and f64 restricted to `+ - * / sqrt`. Asserted
  with `assert_eq!`.
* **display** — anything transcendental. Asserted with tolerances.

Every function's doc comment says which side it is on. Never assert
bit-equality across the boundary.

### Bit-identity is a promise about the EXPRESSION

IEEE-754 gives correct rounding **per operation**, not per formula. Two
algebraically identical spellings that round a different number of times give
different doubles:

```
centroid    browser  sum / n         we had  sum * (1.0/n)     34.2% differ
project     browser  p * (R/L)       we had  (p * (1/L)) * R   41.6% differ
```

Measured over 400k random inputs each. `refineFace` calls `centroid` on every
face, so the port would have diverged at level 1 and compounded forever — and
**all 90 tests passed on both spellings.** Four tests now freeze the browser's
spelling; each asserts both that we match it *and* that the two spellings
genuinely differ, so a weak fixture fails instead of passing quietly.

---

## The integer width table, corrected

An earlier draft of this file said `u64` reaches 47, `i128` reaches 92 and
256-bit reaches 184. **All three were wrong by exactly one, in the same
direction** — the constant counted *terms* while the code used it as an
*index*, so the fence sat one step past the wall. Measured:

**Convention: `n` is an INDEX into `T_0, T_1, …`**

| width | largest `n` with `T_n` representable | largest `n` the recurrence computes |
|---|---:|---:|
| `f64` (2⁵³) | 38 | **37** |
| `u64` | **46** | 46 |
| `i128` | **91** | **91** |
| `u256` | **184** | 184 |

Two columns, because for `f64` they differ. `T_38` is representable, yet the
recurrence that produces it is already wrong, because `3·T_37` overflows first:

```
3 * T_37 = 9_167_309_734_635_369
    2^53 = 9_007_199_254_740_992      the product leaves the range first
```

That gap between "the answer fits" and "the arithmetic that got there fits" is
the whole finding of this ladder, and it is why one number was never enough.

The guard is now `checked_*` arithmetic rather than a magic number, so it is
true by construction and the constant is documentation. In release mode Rust
does not check overflow — a guard that only holds in debug is not a guard.

---

## The contract with the browser

`tests/certification.rs` asserts the exact table:

```
level   T      V       E       F      P    H       chi   E/V
  0     3      60      90      32     12   20      2     1.5
  1     21     420     630     212    12   200     2     1.5
  2     147    2940    4410    1472   12   1460    2     1.5
  3     1029   20580   30870   10292  12   10280   2     1.5
```

`T = 3·7^k`, `V = 20T`, `E = 30T`, `F = 10T + 2`, `P = 12` forever.

Plus: all 180 directed edges belong to **exactly one** face — that is what
proves the surface genuinely closed *and* orientable, rather than merely that
the counts add up — all vertices trivalent, all on the unit sphere, centroid at
the origin.

**χ is never assumed.** `V` and `E` come from independent divisors of the same
arity sum and χ is then computed, so it is allowed to come out wrong. The
browser's own `invariants()` has a branch that derives `V = E − F + 2` and then
computes `χ = V − E + F`, which is 2 for any input whatsoever. A check that
cannot fail is not a check.

If a test fails, the port changed the mathematics. That is a finding, not a
nuisance — it is the entire reason the invariants are asserted.

---

## Status — read this honestly

Everything above was measured on this machine, not asserted. What is **not**
done, stated plainly:

- `buildDodecahedron` and the seven Platonic seeds. `SEED 12` exists on the
  panel, is drawn dim, and says *NOT WIRED, NOT PRETENDING* when clicked.
- `serialize` / `deserialize`, and with them the browser↔Rust hex diff of all
  180 C60 coordinates. Correct by standard; **never measured**.
- `faceLocalFrame` / `facePatch2D`, and the inside view that needs them.
- The Möbius twist. Note for whoever ports it: the browser logs
  `MOBIUS ON: chi=2->0` while its own invariants panel keeps printing `chi 2`
  on the same screen. `applyMobiusLerp` moves **positions only** — the face
  list, arities and adjacency are untouched — so χ really is still 2 and the
  panel is right. It is a deformation, not a topology change.
- `GK.zoomInto` is in the spec's public surface, quoted from the header
  comment. It is **never defined**, in v8.1 or v8.5.2. Porting it would mean
  inventing it.
- Live drag-resize. The canvas is set once at startup on purpose; a mid-run
  change would have to reallocate the framebuffer, the DIB and every cached
  rect while a paint might be in flight.

*Incomplete is fine. Fake is not.*

---

MIT. *P=12 · χ=2 · E/V=3/2 · counting is not closing · the price is always paid*
