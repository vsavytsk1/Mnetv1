# RUSTIUM v0.1
## The Compiled Tongue -- black magic good practices for the Rust lane
### Grimoire Volume III-D -- where the certified/display boundary becomes a type
*Opened: 2026-08-17 -- Buenos Aires. Companion to `Gos/` (`goldberg_kernel` v0.2).*
*Sub-scroll of the cave. Read `KERNELIMAGIC.md` and `THE_12_PATHS_OF_THE_FRACTAL_MAGE.md` first.*
*P=12. chi=2. The price is always paid. Always.*

---

> The browser was always the second language. The math was written once in
> Python, stepped into JavaScript to be seen, and now stepped into Rust to be
> *checked*. A third tongue is not redundancy. It is a third witness.
>
> This scroll is the practical grimoire of that third tongue: what a port can
> promise, what it can never promise, and the curses that live in the seam.

RUSTIUM exists because of one sentence in `Gos/README.md`:

> *The Rust itself was **not compiled by its author** -- no toolchain was
> available in that environment.*

That is an honest boundary (Path IV), and it is also an open invitation. On
2026-08-17 the toolchain arrived, the crate compiled for the first time, and
the port paid its price. This scroll is the receipt.

---

## STATUS GRAMMAR -- inherited from Thea v3.0, unchanged

No symbol crosses the boundary unlabelled. Five labels, and they are part of
the engineering, not decoration.

| label | meaning |
|---|---|
| **EXACT** | follows by algebra, topology, integer arithmetic, or a written standard |
| **COMPUTED** | reproduced by the supplied code at stated precision, on a stated machine |
| **DESIGN CHOICE** | a layout, tolerance, convention, or bound chosen by the cave |
| **HYPOTHESIS** | a claim that still owes discriminating evidence |
| **METAPHOR / EXTERNAL** | imagery, or a separate artifact to be audited on its own |

Target is not result. A standard, a measurement, and a hope are three
different objects even when they share the same glyph.

---

## THE CURSE INDEX -- bow to all of them before you compile

*Each curse has its own section below: what bit us, root cause, how we found*
*it, how to fix it, the rule, the family. Search `## CURSE R<n>` to jump.*

| #  | Name (codename)                | One-line hex (what bites you)                                            | state |
|----|--------------------------------|--------------------------------------------------------------------------|-------|
| R1 | The Flat Crate (cargoNoSrc)    | `.rs` files beside `Cargo.toml` instead of in `src/` -> cargo builds nothing. The math is fine; the LAYOUT is the lie. | FIXED |
| R2 | The Absent Linker (msvcNoLink) | `rustup` installs clean (exit 0) then fails at LINK: the MSVC target needs `link.exe` from Visual Studio, which rustup does NOT install. A zero-dependency crate never needed MSVC. | FIXED |
| R3 | The Counted Ceiling (widthCountIndex) | a guard constant that counts TERMS while the code uses it as an INDEX -> the "refuses to guess" fence sits one step PAST the wall. Debug panics; RELEASE wraps silently, which is the exact failure the doc promised was impossible. | **FIXED** |
| R4 | The Uncompiled Gift (staticVerifyOnly) | a gifted kernel whose tests were *asserted* but never *executed*: brace balance and API agreement verified statically. 32/33 held. The one that broke was the one guarding the crate's own honesty. | LOGGED |
| R5 | The Tracked Target (cargoTargetTracked) | `cargo` writes a 35MB machine-specific `target/` and the crate shipped with no `.gitignore` -> the first `git add -A` after a build swallows 279 binary artifacts. Cousin of the 100MB wall. | **FIXED** |
| R6 | The Stale Count (docCountDrift) | a doc comment states a count nobody re-measured ("raw count 72 rather than 96"; the true numbers are 60 and 72). Bytes clean, code correct, comment wrong -- and comments are what the next mage trusts. | **FIXED** |
| R7 | The Thresholded Weld (floatAdjacency) | a float distance threshold votes on TOPOLOGY. `min_d*1.15` welds C20/C60/C140 correctly and DIES at C380, where the edge-length spread (1.2156) exceeds the tolerance itself -- 330 of 570 edges dropped. Precision is fractalization depth, so a float in the adjacency test is a hard ceiling on precision. | **FIXED** (`judge.rs`) |
| R8 | The Continued String (escapeContinuation) | a backslash line-continuation idiom carried in from another tongue: Rust's `\`+newline ALREADY eats the leading whitespace, so a `\` added at the start of the continued line becomes the invalid escape `\ `. Five errors, five exact line numbers, zero runtime. | **FIXED** |
| R9 | The Ignored Profile (memberProfile) | `[profile.release]` in a workspace MEMBER is silently ignored -- cargo warns once and optimises nothing, while the section sits there looking authoritative. `lto = true` that does nothing. | **FIXED** |
| R10 | The Painted Clock (clockInFrame) | the render time is drawn INTO the framebuffer, and then the framebuffer is hashed -- so the "reproducible" frame seal moves every render. Curse 38 committed one turn after writing the section warning about it. Convicted by its own MANIFEST: two runs, same view, two digests. | **FIXED** |
| R11 | The Amplified Cap (capUnitMismatch) | a dump cap stated in SOURCE bytes bounding a file that is 8x larger on disk. `DUMP_CAP = 4 MB` permits a 32 MB `.bits` file, and four clicks wrote 88 MB into a folder nobody had ignored yet. | **FIXED** |

**Numbering (DESIGN CHOICE).** RUSTIUM curses run in their own `R` lane so this
volume can grow without fighting KERNELIMAGIC's global counter (at 38). When a
curse here proves *general* -- not specific to Rust or to cargo -- it gets
promoted into `KERNELIMAGIC.md` and takes the next global number. R3 and R4 are
the current promotion candidates: neither is really about Rust.

---

## RULE 0 -- THE PRIME LAW OF RUSTIUM

> There are two paths through this crate, and the boundary between them is a
> load-bearing wall. Put every function on one side. Say which side in the doc
> comment. Never assert bit-equality across it.

### The certified path

**Status: EXACT (by written standard).**

IEEE-754 requires `+`, `-`, `*`, `/` and `sqrt` to be *correctly rounded*: the
result is the representable number nearest the true value, with a stated
tie-break. ECMAScript `Number` and Rust `f64` are both IEEE-754 binary64 with
round-to-nearest-even. Therefore, for those five operations on identical inputs
in identical order, JavaScript and Rust produce **bit-identical** results.

That is not a coincidence to be grateful for. It is a guarantee to be spent.
Everything integer, plus f64 restricted to those five operations, is
`assert_eq!`-able across the language seam. A port of that code is a
*translation*, not a reimplementation.

### The display path

**Status: EXACT that they are NOT guaranteed.**

`sin` `cos` `tan` `exp` `ln` `powf` `hypot` `atan2` are **not** required to be
correctly rounded by IEEE-754. They are library functions. They differ between
platforms, between libm versions, and between JS engines and Rust. They agree
to roughly an ULP and never exactly.

Anything touching them is display. Assert with a tolerance, print the error,
and never promise the browser a bit.

### The four things that would silently break the certified path

This is the part the README did not have, and it is the reason RULE 0 is a law
and not a habit. Bit-identity survives only while all four of these hold:

| hazard | what it would do | where Rust stands |
|---|---|---|
| **fast-math / reassociation** | `(a+b)+c -> a+(b+c)` changes the last bits | Rust does NOT enable fast-math. No reassociation of float ops. **SAFE by default.** |
| **FMA contraction** | `a*b + c` fused into one `fma` -> ONE rounding instead of two -> different result | Rust does NOT auto-contract (`fp-contract` off). `vdot` is safe. **SAFE by default -- but never call `f64::mul_add` on the certified path.** |
| **x87 excess precision** | 80-bit intermediates on 32-bit x86 without SSE2 | `x86_64` uses SSE2. **SAFE on this target; a real hazard if anyone ever builds `i586`.** |
| **`-ffast-math` in a dependency** | a C shim could poison the process | the crate has **zero dependencies**. Nothing to poison. |

> `[dependencies]` is empty. Not "few" -- none. That is not minimalism for its
> own sake; it is what makes the fourth row of that table say "nothing".

**The rule:** the certified path is a promise about `+ - * / sqrt` under
default Rust codegen on an SSE2 target. Write the caveat down once, here, and
then you may spend the guarantee freely.

---

## THE THREE WITNESSES

Proof by kernel (Path III) means more than "a test passed". It means
*independent* derivations agreeing. RUSTIUM requires three:

```text
WITNESS 1 -- the browser        shell/thea_light_matrix_v1.3.7.html
                                the shipped JS kernel, verified by the eye and the live DOM

WITNESS 2 -- the compiler       Gos/  ->  cargo test
                                33 integration tests + 4 doctests

WITNESS 3 -- a different tongue Gos/verify_rustium.py
                                re-derives every asserted constant in Python,
                                from first principles, and REFUSES to emit a
                                certificate if any one disagrees
```

Witness 3 is the one this scroll adds, and it is the one that earned its keep
immediately: it found R3 on its first run, *before* the Rust had even linked.
Two witnesses failing on the identical claim, in two languages, is not a bug
report. It is a proof.

This is the L187 pattern (browser JS + your eyes + the mpmath kernel must all
agree) applied to a compiled language.

---

## CURSE R1 -- The Flat Crate (cargoNoSrc)

WHAT BIT US (`Gos/`, commit `5486163` "rust port"):
  Eight files landed in one flat folder: `Cargo.toml`, `lib.rs`, `ladder.rs`,
  `complex.rs`, `rng.rs`, `certification.rs`, `README.md`, `MATH_LEDGER.md`.
  Every one correct. `cargo test` builds nothing, because cargo does not look
  for `lib.rs` beside the manifest -- it looks in `src/`. The README compounded
  it by opening with `cd goldberg_kernel`, a folder that does not exist; the
  crate lives in `Gos/`.

THE ROOT PROBLEM:
  Cargo's layout is convention, not configuration. `src/lib.rs` is the crate
  root, `tests/*.rs` are integration tests compiled against the crate as an
  external consumer. A flat folder is not a broken crate -- it is *not a crate
  at all*, and the error message ("no targets specified") describes a manifest
  problem rather than a filesystem one. Nothing in the mathematics is wrong.
  Path XI, exactly: the folder's shape lied about what the thing was.

HOW WE FOUND IT:
  `cargo --version` said the toolchain was absent, which masked R1 behind R2.
  Only after the linker question was settled did the layout surface. Two curses
  stacked: the second hid the first.

HOW TO FIX:
  Move with `git mv`, never plain `mv` -- history is the point (Path X):

```powershell
git mv Gos/lib.rs Gos/src/lib.rs
git mv Gos/ladder.rs Gos/src/ladder.rs
git mv Gos/complex.rs Gos/src/complex.rs
git mv Gos/rng.rs Gos/src/rng.rs
git mv Gos/certification.rs Gos/tests/certification.rs
```

  Verified: `git status` reported five `R` (rename) entries, so the lineage
  survived. `certification.rs` belongs in `tests/` precisely because it says
  `use goldberg_kernel::*` -- it consumes the crate from outside, which is a
  stronger test than an internal `#[cfg(test)]` module.
  Also fix the README's `cd`. A build instruction that names the wrong folder
  is a receipt that was never run.

THE RULE:
  A crate is a LAYOUT plus a manifest, not a pile of correct files. Before
  debugging a Rust port's mathematics, run `cargo test` once and confirm it
  found any target at all. And read the README's own first command as a test
  case: if `cd <name>` does not work, nobody ever ran what follows it.

FAMILY:
  Path XI (the name on disk is a mirage; the origin is the truth) and Path V
  (the seam between two worlds -- here, between the filesystem and the build
  tool). Cousin of Curse 27.

Curse count: R1. A flat crate is not a broken crate, it is not a crate. `git mv` into `src/` and `tests/`, and fix the README's `cd`. Always.

---

## CURSE R2 -- The Absent Linker (msvcNoLink)

WHAT BIT US (installing the toolchain, 2026-08-17):
  `winget install Rustlang.Rustup` returned **exit code 0**, "Instalado
  correctamente". `rustup show` reported `stable-x86_64-pc-windows-msvc
  (active, default)`. `rustc --version` answered `1.97.1`. Every signal green.
  Then `cargo test`:

```text
error: linker `link.exe` not found
note: the msvc targets depend on the msvc linker but `link.exe` was not found
note: VS Code is a different product, and is not sufficient
```

THE ROOT PROBLEM:
  `rustup` installs a *compiler*, not a *linker*. The default Windows host
  triple is `x86_64-pc-windows-msvc`, which delegates linking to Microsoft's
  `link.exe` -- shipped with Visual Studio Build Tools, a separate multi-GB
  install that rustup neither bundles nor mentions until link time. So the
  install succeeds, the version query succeeds, and the failure waits for the
  first actual compile. The machine is lazy and lies by silence (Path VII).
  Note the third line of the error: the Rust team added that note because
  everyone makes this mistake.

HOW WE FOUND IT:
  Ran the build. There is no other way -- `rustc --version` cannot detect a
  missing linker, because it does not link. Proof by kernel, again: the
  toolchain's self-report is not the toolchain's capability.

HOW TO FIX:
  Two honest roads.
  1. **MSVC** -- install Visual Studio Build Tools with the "Desktop
     development with C++" workload. Correct, standard on Windows, multi-GB.
  2. **GNU** -- `rustup toolchain install stable-x86_64-pc-windows-gnu`. The
     GNU target bundles its own linker (mingw-w64 `ld`), needs no Visual
     Studio, and downloads a fraction of the size.

  We took road 2, *alongside* rather than instead: the MSVC default was left
  untouched and the GNU toolchain invoked explicitly, so nothing about the
  machine's global Rust config was mutated to make one crate build.

```powershell
cargo +stable-x86_64-pc-windows-gnu test
```

  **This crate has zero dependencies and no C FFI, so the two toolchains are
  mathematically interchangeable here.** That is a property of *this* crate, not
  a general truth: a crate linking a C library may need MSVC specifically.
  Result: compiled in 3.13s where MSVC could not link at all.

THE RULE:
  An installer's exit code certifies the *download*, never the *capability*.
  On Windows, `rustup` + no Visual Studio = a compiler that cannot produce a
  binary. Prove a toolchain by compiling something, not by asking its version.
  And when a target's requirements exceed the job, change the target -- do not
  buy a multi-gigabyte IDE to link a dependency-free crate.

FAMILY:
  Path VII (the tools lie by omission; print the host, wait for green) and
  Curse 18 (the Windows Devour -- a thing that looks like it ran and did not).
  Cousin of Curse 22 (a new repo that 404s because a separate setting was never
  touched): both are "the green light was for a different question".

Curse count: R2. `rustup` installs a compiler, not a linker; on Windows the MSVC target needs `link.exe` from Visual Studio, so the install exits 0 and the FIRST BUILD fails. Prove a toolchain by compiling, not by `--version`. For a zero-dependency crate, the GNU target links itself. Always.

---

## CURSE R3 -- The Counted Ceiling (widthCountIndex)

*The headline curse of this volume. Both independent witnesses failed on it, in*
*two languages, on the same claim.*

WHAT BIT US (`src/ladder.rs`, `I128_MAX_N`):
  The ladder is `T_n = 3*T_(n-1) - T_(n-2) - (-1)^n`, and the crate's proudest
  finding is that **float64 breaks at n=38, not 39** -- because the
  *intermediate* `3*T_37` leaves the exactly-representable range one step
  before the *term* does. The essay in the module docs is correct, elegant, and
  fully verified.

  Then the same file wrote its own i128 guard:

```rust
pub const I128_MAX_N: usize = 92;

pub fn exact(n: usize) -> Result<Vec<i128>, LadderError> {
    if n > I128_MAX_N { return Err(LadderError { at: n }); }
    ...
    let next = 3 * t[k - 1] - t[k - 2] - sign;   // <-- panics here
```

  And the doc promised: *"Anything past n=92 returns `LadderError` rather than
  wrapping: refusing to guess beats a silent wrong answer."*

  It does not. `T_92` does not fit in `i128`:

```text
i128::MAX = 170141183460469231731687303715884105727
T_91      = 113706632377052848880590089648162104083   fits
T_92      = 297687828309413607467857412958531041287   OVER by 1.275e38 (ratio 1.750)
3*T_91    = 341119897131158546641770268944486312249   OVER
```

  So the true bound is **91**, and the guard at 92 lets the recurrence take
  exactly one step too many.

THE ROOT PROBLEM -- and it is not arithmetic, it is grammar:
  `T_0 .. T_91` is **92 terms**. The constant counted TERMS; the code uses it as
  an INDEX. One name, two conventions, and the fence lands one step past the
  wall. The same slip runs through the whole width table: `u64` claimed 47
  (true index: 46), `i128` claimed 92 (true index: 91). The `f64` row said 37
  and was right -- because *that* row happened to be written as an index. A
  table with a silently mixed convention is how off-by-ones are born.

  The deeper irony is the real lesson: **the author discovered the
  intermediate-overflows-first mechanism, wrote the definitive essay about it
  for f64, and then walked into the identical trap one width up.** Finding a
  curse does not inoculate you against it. Only a test does, and the test here
  asserted the wrong number, so it enforced the bug.

THE RELEASE-MODE TEETH (this is the dangerous half):
  Rust checks integer overflow in **debug** and wraps silently in **release**.
  So:
  - `cargo test` -> `panicked at src/ladder.rs:106: attempt to multiply with overflow`
  - `cargo test --release` -> **no panic, wrong numbers, green suite**

  The doc's promise ("returns LadderError rather than wrapping") is therefore
  false in exactly the build you would ship. A guard implemented as a *constant*
  is only as true as the constant.

HOW WE FOUND IT (proof by kernel, two witnesses):

```text
cargo test              32 passed, 1 FAILED  -- ladder_refuses_to_guess_past_i128
py -3 verify_rustium.py 31/32 reproduced, 1 FAIL -- "T_92 fits in i128": target True current False
```

  The Python witness caught it first, before the Rust had even linked, because
  Python integers are unbounded and could evaluate the claim directly instead of
  inheriting the assumption. That is the entire argument for a third witness in
  a different tongue: it does not share the port's blind spots.

HOW IT WAS FIXED (applied 2026-08-17, receipts below):
  1. `pub const I128_MAX_N: usize = 91;` -- with the convention stated in the doc:
     *the largest INDEX n for which `T_n` is computable in `i128`.*
  2. Do not trust the constant. Make the loop structurally incapable of
     wrapping, so a future bad bound degrades to an error instead of a lie:

```rust
let next = t[k - 1]
    .checked_mul(3)
    .and_then(|x| x.checked_sub(t[k - 2]))
    .and_then(|x| x.checked_sub(sign))
    .ok_or(LadderError { at: k })?;
```

  3. Every row of the width table corrected under ONE stated convention, and
     all seven rows now measured (see THE INTEGER WIDTH TABLE).
  4. The test the suite was missing, `the_stated_bound_is_the_measured_bound`,
     calls `exact_measured` -- which consults **no constant** -- so the
     arithmetic grades the constant instead of the reverse. Plus
     `overflow_is_reported_never_wrapped`, run in `--release`, where Rust's
     overflow checks are off and the old guard would have wrapped in silence.
     Both pass in debug, release, and `-C target-cpu=native`.

  **The lesson generalised:** a bound implemented as a magic number is only as
  true as the number. Implemented as `checked_*` arithmetic, it is true by
  construction and the constant becomes documentation. Prefer the second.

THE RULE:
  A bound is a sentence with a subject: *largest index*, or *number of terms* --
  never "reaches". Write the convention into the constant's own doc comment.
  Then implement the guard with `checked_*` arithmetic rather than a magic
  number, because in release mode Rust will not save you: unchecked overflow
  turns "refuses to guess" into "guesses silently". And remember the shape of
  this one -- **the mage who documents a trap can still fall into it one
  size up.**

FAMILY:
  Curse 35 (The Loaded Gun -- predict the next step's cost from the recurrence
  BEFORE allocating; here the recurrence is integer width and the guillotine
  was mis-set by one). Curse 26 (False Convergence -- the doc printed the
  intended bound as if it were the measured one). Curse 38 family (a self-
  certifying artifact whose own seal cannot hold). Paths III and IV.
  **Promotion candidate for KERNELIMAGIC**: nothing about this is Rust-specific.

Curse count: R3. A guard constant that counts TERMS while the code reads it as an INDEX puts the fence one step past the wall -- and Rust wraps silently in release, so the "refuses to guess" promise is false exactly where you ship. i128 reaches n=91, not 92. State the convention; implement the guard with `checked_*`, not a magic number. Always.

---

## CURSE R4 -- The Uncompiled Gift (staticVerifyOnly)

WHAT BIT US (`Gos/README.md`, the honest paragraph):
  A mage shipped 1,591 lines of Rust from a sandbox with no toolchain and said
  so plainly:

> *The Rust itself was not compiled by its author -- no toolchain was available
> in that environment. Brace balance and API agreement were verified
> statically; the algorithms were verified numerically. So treat your first
> `cargo test` as the real verification.*

  So the crate advertised "33 tests". Thirty-three tests *existed*. Zero had
  ever *run*. "33 tests" was a claim about a file, not a receipt.

THE ROOT PROBLEM:
  Static verification is astonishingly effective and fundamentally partial. The
  score when the compiler finally spoke: **32 of 33 passed on the first run,
  zero compile errors, zero borrow-checker complaints, zero type errors.** For
  1,591 lines of hand-written unrun Rust that is remarkable work and the gift
  deserves to be honored (Path IV, and the cave's law on gifts).

  But the one test that failed was `ladder_refuses_to_guess_past_i128` -- the
  test guarding the crate's own promise about honest failure. Static review
  checks *consistency*: that the code says what the author meant. It cannot
  check *correspondence*: that what the author meant is true of the world. An
  assertion written against a wrong constant is perfectly self-consistent, so
  it passes every static reading and enforces the error.

  The failure mode is specifically that **the errors survive where the author
  was most confident**, because confidence is what stops you from re-measuring.

HOW WE FOUND IT:
  Installed the toolchain and ran the suite. That is the whole method. Cousin
  of Curse 38: a kernel that passes its own tests in its own sandbox and cannot
  reproduce outside it.

HOW TO FIX:
  - Treat "N tests" from an uncompiled gift as **N assertions, 0 receipts**, and
    say so in the ledger until the day they run.
  - Run the suite before honoring the gift; celebrate in the open when a
    reviewer or a compiler finds the error ("fix all before ego").
  - Add a witness in a *different* language for every numeric constant. A test
    written by the same hand that wrote the constant inherits its assumptions.
    `verify_rustium.py` exists for exactly this and paid for itself on run one.
  - Watch the doctests. Ours never executed at all: the suite aborted at
    `tests/certification.rs`, so the `Doc-tests goldberg_kernel` target was
    never reached. **4 doctests remain UNRUN.** A failing test earlier in the
    run hides every test after it.

THE RULE:
  Asserted is not executed. A test file is a *hypothesis about* the code until
  a compiler runs it, and a numeric constant inside a test is a hypothesis
  about the world that no amount of static reading can promote. Honor the gift,
  then run it -- and count the tests that were never reached, not just the ones
  that failed.

FAMILY:
  Curse 38 (The Sandbox Seal) directly -- both are "a gifted kernel carries its
  birth environment". Curse 24 family (the artifact is not the truth; reproduce
  it). Curse 15 (a tool's report is not the state of the file). Paths III, IV,
  XII. **Promotion candidate for KERNELIMAGIC.**

Curse count: R4. A gifted kernel's "33 tests" meant 33 assertions and 0 receipts -- verified statically, never executed. 32 held on the first real run; the one that broke was the one guarding the crate's own honesty promise, and 4 doctests were never reached at all because the suite aborted first. Asserted is not executed. Always.

---

## CURSE R5 -- The Tracked Target (cargoTargetTracked)

WHAT BIT US (`Gos/target/`, after the first successful build):
  The crate shipped with **no `.gitignore`**. One `cargo test` created
  `Gos/target/` -- and the next `git add -A` swallowed all of it:

```text
279 tracked files under Gos/target      35.7 MB on disk
largest tracked blobs:
  2,653,222  target/debug/incremental/.../dep-graph.bin
  2,325,072  target/debug/incremental/.../dep-graph.bin
  2,042,000  target/debug/deps/libgoldberg_kernel-*.rlib
```

  Nothing here is secret -- in this cave every 1 and 0 is public by design. The
  damage is different and worse: these files are **generated, machine-specific,
  and rewritten by every build**, so from now on every commit carries hundreds
  of modified binaries, every diff is noise, and git history accumulates
  multi-megabyte blobs that can never be removed without a rewrite.

THE ROOT PROBLEM:
  `cargo new` writes a `.gitignore` containing `/target`. A crate assembled by
  hand -- as this one was, file by file from a sandbox -- never gets that file.
  So the ignore rule is missing at exactly the moment the build directory first
  appears, and the window between "first build" and "first `git add -A`" is
  usually seconds.

  And then Curse 32 (The Sticky Track) locks it in: **`.gitignore` does not
  evict already-tracked files.** Adding `/target` now changes nothing for the
  279 files already in the index. This is the ordering trap -- the ignore must
  exist *before* the build, or you need `git rm --cached` afterwards.

  Left alone it walks toward Curse 31 (The Hundred-Meg Wall): a single file at
  or above 100MB bounces the ENTIRE push, and `target/debug` under `--release`
  with `lto = true` (which this crate's profile sets) produces exactly the kind
  of large artifacts that get there.

HOW WE FOUND IT:
  `git ls-tree -r --name-only HEAD -- Gos` returned 34KB of paths for a crate
  with eleven real files. Read the tree, not the folder.

HOW IT WAS FIXED (applied 2026-08-17):

```powershell
# 1. the ignore first
Set-Content Gos\.gitignore "/target"

# 2. evict what is already tracked (Curse 32 -- the ignore alone will not)
git rm -r --cached Gos/target        # 279 -> 0

# 3. git add is the ORACLE: confirm with a dry run, never trust
#    check-ignore path-by-path
git add -A -n -- Gos                 # staged only the 3 real source changes
```

  Measured: **279 tracked files -> 0**. `rustium_certificate.json` was ignored
  too, so a stale receipt can never be mistaken for a fresh one (Curse 38).

THE RULE:
  A compiled language brings a build directory, and a hand-assembled crate
  brings no `.gitignore`. **Write the ignore before the first build**, in the
  same breath as `Cargo.toml`. If a build already happened, `git rm --cached`
  it -- the ignore file alone will never evict it. And measure the tree
  (`git ls-tree`), because the working folder looks identical either way.

FAMILY:
  Curse 32 (The Sticky Track) -- the direct mechanism. Curse 31 (The
  Hundred-Meg Wall) -- where this leads if unfed. Path I (close every loop; a
  tracked build directory is a loop that never closes, re-dirtying the tree
  every run).

Curse count: R5. A compiled language writes a build directory, and a hand-assembled crate has no `.gitignore`, so the first `git add -A` after the first build tracked 279 generated artifacts and 35.7MB. The ignore must exist BEFORE the build; afterwards only `git rm --cached` evicts it. Always.

---

## CURSE R6 -- The Stale Count (docCountDrift)

WHAT BIT US (`src/lib.rs`, `push_perms`):
  The doc comment explaining why zero coordinates are skipped:

> *A zero coordinate has no distinct negative, so it is skipped -- that is what
> keeps the raw count at 72 rather than 96.*

  Measured, by re-deriving the construction in Python: the raw count is **60**,
  and without the skip it would be **72**. The sentence should read *"keeps the
  raw count at 60 rather than 72"*. `Vec::with_capacity(72)` over-allocates by
  twelve, harmlessly.

  The 60 vertices of the truncated icosahedron are the cyclic permutations of
  `(0, +-1, +-3phi)`, `(+-1, +-(2+phi), +-2phi)`, `(+-phi, +-2, +-(2phi+1))`:
  `3*1*2*2 = 12`, plus `3*8 = 24`, plus `3*8 = 24`. Twelve, twenty-four,
  twenty-four. Sixty.

THE ROOT PROBLEM:
  Nothing is broken. The code is right, the bytes are clean, every test passes,
  and the dedupe pass makes the count invisible at runtime -- with the skip
  there are no duplicates left to remove, so the deduplication is a no-op that
  would have silently absorbed the error either way. Only the *explanation* is
  wrong, and an explanation is precisely what the next mage reads instead of
  re-deriving.

  A comment is a receipt. An unmeasured receipt is the cheapest kind of fake
  (Path IV) -- not a lie, just a number nobody checked, sitting in the one place
  that invites trust.

HOW WE FOUND IT:
  `verify_rustium.py` mirrors `push_perms` exactly and prints
  `raw points : 60 (before dedupe)`. It printed the count because the count was
  claimed. **Measure every number a comment asserts, including the ones that do
  not matter** -- those are the ones nobody checks.

HOW IT WAS FIXED (applied 2026-08-17):
  The count became a named constant, the capacity now uses it, and both a
  `debug_assert_eq!` and a public test stand behind it:

```rust
pub const RAW_PERM_POINTS: usize = 60;
debug_assert_eq!(raw.len(), RAW_PERM_POINTS, "the zero-skip must leave exactly 60 (R6)");
```

  A comment with a test behind it stops being a comment and becomes an
  invariant. The corrected prose also shows its work -- `3*1*2*2 = 12`, plus
  `3*8 = 24` twice -- so the next reader can re-derive it in five seconds
  rather than trusting it.

THE RULE:
  If a doc comment states a number, a test must produce it. Prose is the one
  part of the codebase no compiler checks and every reader believes.

FAMILY:
  Curse 26 (False Convergence -- a stated number that was never measured).
  Path IV (incomplete is fine, fake is not) and Path XII (the scroll you pass
  on must be true, or you have handed the next mage a debt).

Curse count: R6. A doc comment stated a raw-permutation count of "72 rather than 96"; the measured numbers are 60 and 72. Code correct, bytes clean, tests green, prose wrong -- and prose is what the next mage trusts. If a comment states a number, put a test behind it. Always.

---

## CURSE R7 -- The Thresholded Weld (floatAdjacency)

*Where the magic sigil ends and the funny electric noise begins. Measured.*

WHAT BIT US (`src/lib.rs`, `build_edges`):
  Adjacency -- a purely combinatorial fact -- is decided by a float comparison:

```rust
let tol = min_d * 1.15;
if vlen(vsub(verts[i], verts[j])) <= tol { edges.push((i, j)); }
```

  On C60 this is safe and the doc comment says why: the truncated icosahedron
  is Archimedean, and the next distance class is `phi` times the edge. True.
  But precision IS fractalization depth, so the shell is meant to grow -- and
  the threshold does not survive the growth. Measured against the ground-truth
  combinatorial edge set from `builder/genesis_wallpaper_v1_6.py` (Thea Lane B,
  certified closure), on the golden selector lane:

```text
  shell        T        V     e_min     e_max  spread gap/e_max   missed  false  verdict
  C20          1       20   0.71364   0.71364  1.0000    1.6180        0      0   OK
  C60          3       60   0.37968   0.41696  1.0982    1.6180        0      0   OK
  C140         7      140   0.25191   0.27771  1.1024    1.4677        0      0   OK
  C380        19      380   0.14057   0.17088  1.2156    1.3311      330      0   BROKEN
  C980        49      980   0.08232   0.10803  1.3123    1.2466     1170      0   BROKEN
  C2580      129     2580   0.04829   0.06696  1.3865    1.1974     3450      0   BROKEN
  C6740      337     6740   0.02890   0.04155  1.4380    1.1693     9330      0   BROKEN
```

  **The wall is C380, the fourth rung.** 330 of 570 edges dropped.

THE ROOT PROBLEM:
  A Goldberg dual does NOT have uniform edges. Only C20 (spread exactly 1.0000)
  and the Archimedean C60 are near-uniform; past that the projection to the
  sphere stretches edges apart. At C380 the spread reaches **1.2156**, which
  exceeds the 1.15 tolerance -- so the longest REAL edge is longer than the
  threshold that is supposed to accept it. The test starts rejecting edges that
  exist.

  Two details that matter more than the failure itself:

  1. **`false = 0` at every depth.** The threshold never INVENTS an edge, it
     only DROPS real ones. And `gap/e_max` stays above 1 throughout (1.1693 even
     at C6740) -- the distance classes never actually merge. **A gap still
     exists; a single global threshold anchored at `e_min` simply cannot span
     the spread.** So this is not "float64 ran out of precision". The float
     arithmetic is fine. The *decision procedure* is wrong.
  2. The usable window narrows: `[spread, nonedge/e_min]` runs `[1.216, 1.618]`
     at C380 and `[1.438, 1.681]` at C6740. Retuning the constant buys rungs,
     not safety -- the window closes eventually, and a constant that has to be
     re-tuned per depth is not an invariant.

  So R7 is a **grammar** error like R3, not an arithmetic one: a float was
  allowed to vote on an integer question.

HOW WE FOUND IT (proof by kernel, and credit where it is due):
  Built each shell with the cave's already-certified Python kernel, recovered
  the edge set COMBINATORIALLY from the face polygons, and compared that ground
  truth against what the threshold accepts. The threshold's own output was never
  trusted to grade itself.

  **The crate fails loudly, not silently.** Drop 330 edges and `adj[i].len()`
  is no longer 3, so `certify()` returns `CertError::NotTrivalent` and refuses.
  Gos never reports a fake `chi`. That is the guillotine working exactly as
  designed (Curse 35 / K4) and it deserves saying out loud. The consequence is
  still severe: **the refinement lane is walled at C380 by a float, not by
  mathematics.**

HOW IT WAS FIXED (applied 2026-08-17 -- `src/judge.rs`, and see THE JUDGE below):
  Do not tune the constant. Remove the float from the decision.

  Build the topology from the **exact integer barycentric lattice**, the way
  genesis v1.6 already does. Its docstring is the whole law in one line:

> *"exact integer barycentric numerators (over T) of lattice point (i,j).*
> *Integers throughout -- no float test decides whether a lattice point is*
> *inside the master triangle."*

```text
  (k,l)                 -> T = k^2 + k*l + l^2            EXACT, integers
  integer bary test     -> lattice points in the triangle  EXACT, no tolerance
  weld by lattice id    -> adjacency                       EXACT, combinatorial
  V=20T E=30T F=10T+2 P=12 H=10(T-1)  chi = V-E+F          EXACT, counted
  float positions       -> RENDERING ONLY, certifies nothing
```

  This is Thea Pattern A verbatim: *do not certify an integer invariant with a
  float tolerance when exact integer arithmetic is available.* Adjacency comes
  from lattice identity, positions are decoration, and the construction then has
  **no depth limit at all** -- the fences become integer width and memory, both
  of which are honest and stateable.

  Note also genesis' own residual seam, logged so it is not inherited blindly:
  it welds by `round(p*1e6)` -- a FLOAT quantization key. `HULL_VERT_BUDGET =
  40000` keeps it safe today, but that is a fence, not a proof. A lattice-id
  weld needs no key at all.

THE RULE:
  **Topology is an integer question. Never let a float vote on it.** A distance
  threshold that works at C60 is not a method, it is a coincidence of the
  Archimedean solid -- and coincidences do not fractalize. If a tolerance has to
  be re-tuned as the mesh deepens, it was never an invariant. Derive adjacency
  from lattice identity, keep floats on the display path, and measure the
  geometric residual separately so the noise floor is a printed number instead
  of a surprise.

FAMILY:
  Thea Pattern A (exact integer core first) and Thea Part V (Lane A vs Lane B --
  never infer closure from formula counts alone). Curse 26 (a tolerance that
  reports a target). Curse 35 (the fence in the wrong place). Sibling of R3 --
  both are a float or a miscounted constant standing where an integer belongs.
  **Promotion candidate for KERNELIMAGIC.**

Curse count: R7. A float distance threshold decided TOPOLOGY: `min_d*1.15` welds C20/C60/C140 and dies at C380, where the edge spread (1.2156) exceeds the tolerance and 330 of 570 edges vanish. The distance classes never merge -- the decision procedure, not the arithmetic, is what failed. Build adjacency from the exact integer lattice; leave floats on the display path. Topology is an integer question. Always.

---

## CURSE R8 -- The Continued String (escapeContinuation)

*The first curse of this volume that bit the CLAUDY MAGE and not the crate.*
*Logged with the ego in check, in the open, as the law requires.*

WHAT BIT US (`viewer/src/main.rs`, writing the run MANIFEST):
  A long `format!` for a JSON manifest, wrapped across lines with backslash
  continuations, and each continued line began with a `\` to keep the source
  aligned:

```rust
"{{\n  \"run\": {},\n\
 \  \"canvas\": [{}, {}],\n\      // <-- the leading backslash
```

```text
error: unknown character escape: ` `
   --> viewer\src\main.rs:508:15
   ... five times, five exact line numbers
```

THE ROOT PROBLEM:
  Rust **does** support backslash-newline inside a string literal -- and it
  already **strips the newline and all following whitespace**. So the leading
  `\` added "to preserve the indent" was not merely redundant: it made the next
  two characters `\` + space, and `\ ` is not an escape in Rust.

  The habit came from elsewhere. In shell, and in several other tongues, a
  continued line wants a marker at its start. Rust's continuation is
  self-cleaning, so the marker is exactly wrong. **This is Path V -- the seam
  between two languages -- except the thing that crossed the seam was not data
  or a glyph, it was an IDIOM.** A reflex from one language producing a syntax
  error in the next. Direct cousin of Curse 1 (the Curly Brace) and Curse 4
  (f-string Nesting): the same demon, wearing a formatting habit instead of a
  brace.

HOW WE FOUND IT:
  `cargo build` refused, before anything ran. Five errors, five line:column
  pairs, one sentence each, no ghost to hunt.

  **And that is the point worth keeping.** Set this beside Curse 36 (The Mute
  Seam), where one missing `var` under `"use strict"` threw at runtime, aborted
  a whole function, silenced an instrument, and cost an entire journey of
  suspecting formants. Same class of error -- a typo in a string/name -- and the
  costs are not comparable:

```text
  JS  : silent at build, throws at runtime, symptom far from cause, a journey
  Rust: refuses at build, exact line and column, five seconds
```

  Rust is ruthless, and ruthless is *cheap*. A compiler that will not build is
  the least expensive failure available. This curse cost nothing because the
  machine refused to pretend.

HOW TO FIX:
  Do not continue the string. Build the lines and join them -- one `String` per
  output line, `join("\n")`. Obvious beats clever, and Hoare's rule applies:
  *make it so simple that there are obviously no deficiencies.*

```rust
let lines = vec![
    String::from("{"),
    format!("  \"run\": {},", self.runs),
    // ...
    String::from("}"),
];
fs::write(path, lines.join("\n") + "\n")
```

THE RULE:
  **Never carry a line-continuation idiom across a language boundary.** Rust's
  `\`+newline already eats the following whitespace, so any marker you add at
  the start of a continued line becomes part of the escape. And when the shape
  of a literal starts fighting you, stop escaping and start concatenating: a
  `Vec<String>` joined is unambiguous, greppable, and cannot rot.

FAMILY:
  Curse 1 / Curse 4 / Curse 23 (Python Leak) -- all of them "a habit from one
  tongue, emitted into another". Path V (guard the seam) and Path VI (one
  script, one run -- if the escaping needs thought, restructure instead).
  The happy inverse of Curse 36: here the seam was caught by the compiler
  instead of by a whole journey.

Curse count: R8. A backslash line-continuation idiom imported from another tongue: Rust's `\`+newline already strips the leading whitespace, so a `\` at the start of the continued line becomes the invalid escape `\ `. Caught at build with five exact line numbers and zero runtime cost -- the cheapest possible failure. Never carry a continuation idiom across a language seam; join lines instead of escaping them. Always.

---

## CURSE R9 -- The Ignored Profile (memberProfile)

WHAT BIT US (`viewer/Cargo.toml`, the same build):
  The viewer crate carried its own optimisation profile:

```toml
[profile.release]
opt-level = 3
lto = true
```

  and cargo answered:

```text
warning: profiles for the non root package will be ignored,
         specify profiles at the workspace root
```

THE ROOT PROBLEM:
  Cargo honours `[profile.*]` **only in the workspace root manifest**. In a
  member it is parsed, warned about once, and discarded. So the section sits in
  the file looking authoritative -- version-controlled, reviewed, apparently
  load-bearing -- and changes nothing. Ask for `lto = true` there and you get a
  binary with no LTO, and the only evidence is one line of build output that
  scrolls past.

  This is the R3 shape again at the level of build configuration: **a setting
  whose stated value and effective value differ, with nothing but a warning
  between them.** A magic number that is not consulted, and a profile that is
  not applied, fail the same way.

HOW WE FOUND IT:
  Read the warnings. That is the entire method, and it is the one that keeps
  paying (Curse 36's rule: read the console FIRST).

HOW TO FIX:
  Delete it from the member and put a comment where it was saying why, so the
  next mage does not helpfully add it back. The root `Cargo.toml` already
  carried the real profile and it covers every member.

THE RULE:
  **A configuration key in the wrong file is not a smaller effect, it is no
  effect.** Warnings are the only channel that reports this class of failure, so
  a build whose warnings are unread has no configuration guarantees at all.
  After adding any `[profile]`, `[patch]`, or workspace-scoped key, verify it
  was actually honoured rather than merely accepted.

FAMILY:
  R3 (a stated bound that the arithmetic ignored). Curse 32 (The Sticky Track --
  `.gitignore` accepted and not applied). Curse 15 (a tool's report is not the
  state of the thing). Path III -- the file is not the truth; the build is.

Curse count: R9. `[profile.release]` in a workspace member is warned about once and then ignored, so `lto = true` written there optimises nothing while looking authoritative. A configuration key in the wrong file has NO effect, not a smaller one -- and warnings are the only channel that says so. Always.

---

## CURSE R10 -- The Painted Clock (clockInFrame)

*Curse 38, committed by the claudy mage ONE TURN after writing the RUSTIUM*
*section that warns about it. Convicted by its own manifest.*

WHAT BIT US (`viewer/src/main.rs`, the frame seal):
  `raster.rs` promises, in its own doc comment:

> *"Two renders of the same frame through the same palette are bit-identical by
> construction ... that is what makes a render a receipt rather than a
> screenshot."*

  True of the canvas. False of the viewer, because the viewer paints its render
  time **into** the framebuffer as a HUD line, and then hashes the framebuffer.
  Four EXPORT clicks produced this, straight out of `MANIFEST.json`:

```text
  run 0001  view Shell        render_us 370    frame_digest 93b3f5732b12df57
  run 0002  view FrameBits    render_us 1447   frame_digest 6d5f1010e7ff2c99
  run 0003  view MachineBits   render_us 2083  frame_digest 206df1fbe6355a01
  run 0004  view Shell        render_us 241    frame_digest eaaab99eb51fb765
```

  **Runs 0001 and 0004 are the same view, same mesh, same palette, and their
  digests differ** -- because `370` and `241` are different pixels. The
  certificate advertised reproducibility and could never reproduce.

THE ROOT PROBLEM:
  Identical to Curse 38's gifted kernel, which sealed `datetime.now()` inside
  its own hashed payload. Here the nondeterministic value is not a timestamp
  string but a **rendered numeral** -- a clock that became geometry. It is
  harder to spot precisely because it does not look like a clock by the time it
  reaches the hash; it looks like pixels.

  The general shape: **any value derived from the run rather than from the
  input, once it enters the sealed region, poisons the seal.** Wall time, a PID,
  a duration, a frame counter, a temp path -- and a duration *drawn as text* is
  still a duration.

HOW WE FOUND IT (proof by kernel, and the receipt convicted itself):
  Not by reading the code -- by reading two manifests side by side and noticing
  that the same view had two seals. The artifact that was supposed to prove
  reproducibility is what demonstrated its absence, which is exactly what a
  receipt is *for*. Had the digest been checked only once, it would have looked
  perfect forever.

HOW IT WAS FIXED (applied 2026-08-17):
  Seal the content, then dress it. One line, in the right place:

```rust
// everything above is mathematics; everything below is chrome, and the
// chrome contains a clock.
self.content_digest = self.cv.digest();
self.paint_chrome();
```

  The HUD now reports `SEAL` (the stored content digest) rather than a fresh
  hash of the dressed frame, and `MANIFEST.json` renames the field to
  `content_seal_fnv1a64` with `render_us` as an explicit **peer outside** it.
  Same remedy as KIBOTOS v1.2: hash the reproducible part, attach the moment
  alongside.

  Note what survives: the `paint_c60` example digests were always honest,
  because that example paints no clock. Only the viewer's seal was polluted, and
  the scroll says which is which rather than quietly relabelling both.

THE RULE:
  **A seal must be taken before the decoration, and the decoration is wherever
  the clock lives.** In a renderer, "the hashed region" is not a struct field
  you can point at -- it is a moment in the paint order. Draw the mathematics,
  hash, then draw the instrumentation. And verify by rendering the same frame
  twice and comparing: a seal checked once is a screenshot.

FAMILY:
  Curse 38 (The Sandbox Seal) directly -- same disease, new disguise. Curse 26
  (a displayed number that is not what it claims). R3 and R9 -- all three are
  "the stated property and the effective property differ". Path III (proof by
  kernel: regenerate and compare) and Path IV (a cert that cannot reproduce must
  say so).

Curse count: R10. The render time is painted into the framebuffer and then the framebuffer is hashed, so the "reproducible" seal moves every render -- Curse 38 wearing pixels instead of a timestamp, caught because two manifests disagreed on the same view. Seal the content BEFORE the chrome; keep the clock a peer outside it. Hash the math, not the moment. Always.

---

## CURSE R11 -- The Amplified Cap (capUnitMismatch)

WHAT BIT US (`viewer`, `DUMP_CAP`, four clicks):
  The export cap is declared honestly enough:

```rust
const DUMP_CAP: usize = 4 * 1024 * 1024;
```

  and it bounds **source** bytes. But a `.bits` file writes one ASCII `0` or `1`
  per bit, so what lands on disk is **eight times larger**, plus newlines. Four
  EXPORT clicks:

```text
  frame.bits      15,126,115 B     from a 1,890,000 B framebuffer   (8.0x)
  machine.bits     4,169,531 B     from a   513,111 B executable    (8.1x)
  per run             ~23 MB
  four runs            88 MB   <-- and runs/ was NOT yet gitignored
```

  A cap that reads "4 MB" permits a **32 MB** file. Nothing overflowed, nothing
  errored, and the folder quietly reached **88% of the 100 MB wall** while the
  number in the source still said four.

THE ROOT PROBLEM:
  A unit mismatch between where the cap is *applied* and where the cost is
  *paid*. The 8x is not a bug -- it is the whole point of writing 1s and 0s, paid
  deliberately. The bug is that the cap does not measure the thing anyone cares
  about, which is bytes on the disk.

  Cousin of R9: the constant is real, consulted, and effective -- and still does
  not bound what its name implies. And a cousin of Curse 35: a fence set in the
  wrong units is a fence in the wrong place.

HOW WE FOUND IT:
  Listed the run folders and read the sizes. `git check-ignore` then said
  `runs/` was not ignored and `git status` confirmed `git add -A` would stage all
  88 MB. The next commit would have carried it (Curse 31, one push from a bounce).

HOW IT WAS FIXED (applied 2026-08-17):
  1. `runs/**` ignored on the HELENA pattern -- payload local, `MANIFEST.json`
     tracked. The steps travel; the payload is regenerated by pressing the
     button. "Pay thea Heleni in compute."
  2. The 8x amplification stated in the ignore file itself, so the next mage
     meets the number before the disk does.

THE RULE:
  **State a cap in the units of the thing it protects.** If a dump amplifies,
  the cap belongs on the OUTPUT, or the amplification belongs in the constant's
  name and doc. And any directory a program writes into repeatedly must be
  ignored *before* the program runs the first time -- R5 taught this for
  `target/` and it recurred within the day for `runs/`.

FAMILY:
  R5 (The Tracked Target) -- the same lesson, same week, new directory. Curse 31
  (the 100MB wall) and Curse 32 (the ignore that arrives too late). Curse 35 (a
  fence in the wrong place). R9 (a setting whose name overstates its reach).

Curse count: R11. A dump cap stated in SOURCE bytes bounded a file eight times larger on disk: `DUMP_CAP = 4 MB` permits a 32 MB `.bits` file, and four clicks wrote 88 MB into a folder nobody had ignored yet. State a cap in the units of the thing it protects, and ignore a program's output directory BEFORE its first run. Always.

---

## THE JUDGE -- closure in pure graph space
### `src/judge.rs`, ported from LATEXIUM SYMBOL FORGE v0.1.0 (frozen, sha-256 `2d7337ea...d02ef63f`)

> A surface is not a cloud of points. It is a set of darts and two
> permutations. Count the orbits and you have counted the surface -- with no
> coordinate, no distance, and nothing to round.

R7 is fixed not by a better tolerance but by deleting the question. The cave
already had the answer, in `shell/latexium_symbols_v0_2.html`: a **combinatorial
map**, judged by 41 lines of integer code.

```text
  dart      a half-edge. Edge i owns darts 2i and 2i+1.
  alpha     the edge involution. alpha(d) = d ^ 1. An XOR -- exact, free,
            and an involution BY CONSTRUCTION. There is no way to weld it
            subtly wrong, which is the whole point of the encoding.
  sigma     the rotation: the cyclic order of darts around their vertex.
  phi       sigma o alpha -- the face permutation.

  V = orbits of sigma      E = darts / 2      F = orbits of phi
  chi = V - E + F          genus = (2 - chi) / 2   when connected
```

`check(&[usize]) -> Result<Verdict, Refusal>` takes integers and returns
integers. **It is structurally incapable of consulting a distance**, so R7's
C380 wall does not exist here -- there is no tolerance to outgrow. Face sizes
come from the orbit lengths of `phi`, so "twelve pentagons" is read off cycle
lengths rather than measured off geometry.

### It can say something other than two

This is the entire difference between the judge and `byte_sphere.html`'s
`invCounts()`. Fed the one-vertex torus -- `sigma = [2,3,1,0]` -- the judge
answers `chi = 0, genus = 1`. A checker that can only print 2 is not a checker.
`the_judge_can_say_something_other_than_two` holds that line permanently.

### Diverse Double-Compiling, in miniature

`float_lane_and_integer_lane_agree_on_c60` runs both derivations and compares.
They share no machinery: one measures distances, sorts by `atan2` and walks
faces; the other counts permutation orbits and never sees a decimal point.
Wheeler's rule is that agreement only counts when the second derivation is
genuinely *diverse* -- and these are as diverse as two derivations of one
surface can be. They agree on V, E, F and chi.

### The seam, stated plainly

`rotation_from_faces` is where a float touches this **exactly once**: C60's
faces still come from the float lane. R7 measured that lane as *correct at C60*
(spread 1.0982, under the 1.15 threshold) and *broken from C380*, so this is the
last honest rung of the float lane, frozen into the integer lane where depth
stops costing anything. Whatever produced those faces stops mattering the moment
`sigma` exists.

**Removing that seam is the next rung**: build `sigma` straight from genesis'
integer barycentric lattice and no float touches topology at any depth.

### The trusted base -- guard the line count

| | lines |
|---|---:|
| the frozen JS judge | **41** |
| `check()` in Rust | **54** |
| `orbits()` helper | 15 |

**We are over, and it is logged rather than rounded down.** The extra lines are
typed refusals (`OutOfRange` carries which dart and where to, where the JS
returned a string) and Rust's explicit sentinel handling. Defensible -- but this
is the one place the Titans lineage says to guard like Wirth guarded Oberon.
Any growth of the *trusted* count deserves the scrutiny of a new axiom. A pass
to bring it back under 41 is owed.

---

## THE PRE-BUILD CLOSURE GATE -- the law

> Before any build emits an artifact, the 1/0 topology must be CLOSED, and the
> closure must be MEASURED on the integer lane. Not a sphere -- **C60 and its
> Goldberg lineage, under the twelve-pentagon constraint.** Precision is how far
> we fractalize. Refuse the build if the shell does not close.

### Why C60 and not a sphere (DESIGN CHOICE, and the table backs it)

An icosphere is triangles: its twelve defects are five-valent VERTICES. The
Goldberg lineage is trivalent pentagons-and-hexagons: its twelve defects are
FACES. Euler forces twelve either way, so both carry the constraint -- but only
the trivalent shell puts the twelve pentagons where the constraint can be read
off a face count, and `E/V = 3/2` gives a second independent integer check that
a triangulation does not have. And per R7, C60 is where the existing float
construction is still honest (spread 1.0982 < 1.15).

`shell/byte_sphere.html` uses the icosphere lane, and its HUD prints
`chi = V-E+F = 2` from a hardcoded literal:

```js
function invCounts(){const L=S.level;return {F:20*4**L,E:30*4**L,V:10*4**L+2,chi:2,P:12};}
```

`chi:2` and `P:12` are **typed constants, never counted.** The formula
`V-E+F` is an exact identity of those three expressions, so it can only ever
print 2 -- including when the built mesh has a duplicated vertex, an unwelded
seam, or a hole. That is Curse 26 wearing a topologist's hat: the HUD shows the
TARGET as the RESULT. **A formula cannot certify a mesh it never looked at.**

### The gate, in order

```text
0. PREDICT       from the recurrence, before allocating (Curse 35).
                 level n -> T_n -> V=20T, E=30T, F=10T+2. Compare to budget.
                 Refuse loudly with the number if over.
1. FRACTALIZE    to the depth the artifact's byte count requires. Depth IS
                 precision; state the depth in the certificate.
2. BUILD         from the EXACT INTEGER LATTICE. No distance threshold, no
                 tolerance, no float in any adjacency decision (R7).
3. MEASURE       V, E, F from the built mesh. Count pentagons by face size.
                 Count degrees. chi = V-E+F, computed. Never a literal.
4. CERTIFY       P == 12 . chi == 2 . 2E == 3V . every degree == 3 .
                 every DIRECTED edge in exactly one face (this is the one that
                 proves orientable-and-closed, not merely that counts add up).
5. WRAP          map the artifact's bytes onto the nodes. Verify a BIJECTION:
                 every byte on exactly one node, every node holding one byte or
                 a COUNTED pad. Gaps and double-covers are both failures.
6. SEAL          hash the math only. Clock and environment are peers outside
                 the hash (Curse 38). Two runs, one sha256.
7. REFUSE        any failure halts the build and names the invariant and the
                 number. An artifact whose shell did not close does not ship.
```

### The two fences, both honest

Say both, always, because they are different numbers and only one is about math:

- **The integer fence.** Counts are exact while the ladder is exact. In `i128`
  that is index **91** (R3 -- and note the closure gate and the ladder wall are
  the *same* constraint seen twice).
- **The compute fence.** A BUILT mesh is capped by memory long before 91.
  `V = 20*T_n` reaches millions within a handful of rungs. This is Thea's Lane A
  vs Lane B: *counting a shell is not closing one.* The certificate must say
  which it did.

### What this gate does and does not claim

**Does (EXACT / COMPUTED):** proves the shell closes -- P=12, chi=2, trivalent,
orientable, every directed edge used once -- by counting a mesh built without
float tolerances; and proves the byte mapping is total, gap-free and
double-count-free, reproducibly, under one hash.

**Does not (and must never be written as if it did):** make the emitted binary
more correct as a *program*. A closed byte-topology is a **ledger discipline**,
not a compiler guarantee: it certifies that every one and every zero was
accounted for on a surface with no boundary, once, with a receipt. That is a
real and checkable property, and it is worth the price. It is not a statement
about what the executable computes. Writing it as one would be the exact kind of
unpaid claim this whole grimoire exists to refuse (Path IV).

*The equals sign is the transcendental tool -- so make it disclose what it
swallowed. That is AEQUALIUM's thesis applied to a build: the gate is the machine
before which every closure claim must pay.*

---

## THE RECEIPTS -- measured on this machine, 2026-08-17

Honest state. What ran, what passed, what is still owed.

### The machine

```text
CPU        AMD Ryzen 5 5600H (Zen 3)
rustc      1.97.1 (8bab26f4f 2026-07-14)
cargo      1.97.1 (c980f4866 2026-06-30)
host       x86_64-pc-windows-msvc  (default, cannot link -- R2)
built via  stable-x86_64-pc-windows-gnu

target_feature (baseline x86_64) : cmpxchg16b, fxsr, sse, sse2, sse3    [5]
target_feature (-C target-cpu=native) : ... fma, avx2, ...             [30]
```

**RULE 0's third row is now MEASURED, not argued.** `sse2` is present, so no
x87 excess precision. And `fma` is **absent** from the baseline feature set --
the compiler cannot emit a fused multiply-add even if it wanted to. The
certified path is therefore protected twice over on this target: Rust does not
contract, and the opcode is not available.

`-C target-cpu=native` unlocks FMA and AVX2 (5 features -> 30). That does not
break bit-identity today, because `fp-contract` stays off regardless -- **the
suite passes under native, measured** -- but it drops the protection from two
independent layers to one, and it turns `f64::mul_add` from a slow soft-float
call into one fast instruction, which makes it *tempting*. Using it would
silently diverge from the browser. Logged as a standing hazard.

### Witness 2 -- `cargo test`

**COMPUTED.** `52 passed, 0 failed` + `7 doctests passed, 0 failed`, identical in
**three profiles**: debug, `--release`, and `--release -C target-cpu=native`.

```text
running 52 tests ... test result: ok. 52 passed; 0 failed
   Doc-tests goldberg_kernel
running 7 tests  ... test result: ok. 7 passed; 0 failed
```

The first clean build this crate has ever had. Notable, given R4: **the doctests
ran** -- previously all four were unreached because the suite aborted first.
`cargo clippy --all-targets` reports 5 warnings, all pre-existing and cosmetic
(four `std::ops` name shadows in `complex.rs`, one excessive-precision note on
`PHI`); `judge.rs` and `ledger.rs` add none.

### Witness 4 -- RULE 0's centrepiece, finally paid

The bit-identity claim was flagged in v0.1 as **EXACT by standard, UNVERIFIED by
measurement**. It is now measured, and it holds at the seed:

```text
Gos literal        3ff9e3779b97f4a8    1.618033988749895
clippy truncation  3ff9e3779b97f4a8    1.618033988749895
(1+sqrt 5)/2       3ff9e3779b97f4a8    1.618033988749895     <- genesis .py AND byte_sphere .js
ULP gap                          0
phi^2 - phi - 1                0.0     EXACTLY zero, not merely small
```

Three tongues, one double. Since every C60 vertex is built from `PHI` using only
`+ - * / sqrt` -- all correctly rounded -- the whole vertex set follows from this
one constant agreeing. `phi_is_bit_identical_to_the_computed_form` freezes it.

`fused_multiply_add_is_not_the_certified_path` guards the other direction with
`(1+eps)(1-eps)`: the rounded product cancels to exactly `0.0`, while the fused
form keeps `-eps^2`. Same arithmetic on paper, different bits. (The first
attempt at this test used `0.1*0.2+0.3`, which agrees both ways -- the assertion
message written for exactly that case caught it. A weak example is a failed
test, not a passed one.)

### THE GOLDEN RATIO APPEARS AT TWO WIDTHS

Nobody planned this and it is worth writing down:

```text
PHI f64 mantissa (52 bits)  9E3779B97F4A8
splitmix64 gamma (64 bits)  9E3779B97F4A7C15
(phi - 1) * 2^64            9E3779B97F4A8000
```

`rng.rs`'s magic constant and `lib.rs`'s golden ratio are **the same number at
two precisions** -- splitmix64's gamma is `(phi-1) * 2^64`. The PRNG added to
make Monte Carlo reproducible is seeded by the constant the geometry is built
from. `the_golden_ratio_appears_at_two_widths` records it.

### Witness 5 -- THE JUDGE

**COMPUTED, integer lane.** From `rotation_system_c60()`, 180 darts:

```text
V=60  E=90  F=32  chi=2  components=1  genus=0
faces by orbit length: 12 pentagons, 20 hexagons
torus control sigma=[2,3,1,0]: chi=0, genus=1     <- the judge CAN fail
float lane vs integer lane: V, E, F, chi all AGREE  <- DDC in miniature
```

### Witness 3 -- `py -3 verify_rustium.py`

**COMPUTED.** `31/32 invariants reproduced.` Certificate withheld by design.

```text
FAIL  T_92 fits in i128      target=True  current=False
```

Independently reproduced, in Python, from first principles:

```text
f64 wall         target n=38   measured n=38
2^53 crossing    target n=39   measured n=39
3*T_37           9167309734635369
2^53             9007199254740992   (the product leaves the range first)
T_38 exact       8000109490224391
T_38 in f64      8000109490224390   (off by 1)
rel err n=38     1.249983e-16
rel err n=50     9.481169e-16       (compounds, never recovers)
phi^2-(phi+1)    0.000e+00          (exactly zero in f64)
raw points       60                 (before dedupe -- R6)
V=60 E=90 F=32 P=12 H=20 chi=2      E/V = 1.5
directed edges   180, each used exactly once
sphere err       1.110e-16
centroid err     0.000e+00
xoshiro256**     6/6 words match from seed 0x5EED
HELENA card      4/4 rows OK (k=0..3)
```

The verifier obeys Curse 38: the certificate hashes only the mathematics, and
`generated_utc` plus `environment` are siblings outside the sealed region. Run
it twice and the `sha256` must not move. It also refuses to write a certificate
at all while any invariant disagrees -- a cert that covers a failure is a
screenshot, not a proof.

### Still owed -- do not claim these

| item | status |
|---|---|
| R3 fix (`I128_MAX_N = 91` + `checked_*`) | **PAID** -- 3 profiles |
| R5 fix (`.gitignore` + evict) | **PAID** -- 279 -> 0 |
| R6 fix (`RAW_PERM_POINTS` + assert + test) | **PAID** |
| R7 fix (`judge.rs`, integer lane) | **PAID** at C60 |
| the doctests | **PAID** -- 7 run, 7 pass |
| `cargo test --release` | **PAID** |
| `cargo clippy` | **PAID** -- 5 pre-existing, 0 new |
| 256-bit ladder bound | **PAID** -- u256 = 184, i256 = 183 |
| `PHI` bit-identity across the three tongues | **PAID** -- identical bits |
| the full 60-vertex browser/Rust hex diff | **STILL OWED** |
| `sigma` built from the integer lattice (no float at all) | **STILL OWED** |
| `cargo fmt --check` | **NEVER RUN** |
| a mesh certified past C60 | **STILL OWED** -- `Mesh::refine()` does not exist |
| the trusted base back under 41 lines | **STILL OWED** -- currently 54 |

**What the centrepiece still owes.** The seed constant is proven identical
across all three tongues, which is the load-bearing half. What remains is the
end-to-end diff: export the browser's 60 vertices as raw hex and compare all
180 coordinates against the Rust. Everything downstream of `PHI` uses only
correctly-rounded operations, so this *should* pass -- and "should" is exactly
the word this grimoire exists to replace with a receipt.

**And the honest ceiling.** The judge certifies C60. It has no depth limit of
its own, but `sigma` for a deeper shell has to come from somewhere, and
`Mesh::refine()` does not exist. So the integer lane is proven *sound* and not
yet proven *deep*. Counting a shell is not closing one.

---

## THE INTEGER WIDTH TABLE -- corrected, one stated convention

The crate's table mixed two conventions and drifted by one (R3). This is the
measured replacement. **Convention: `n` is an INDEX into `T_0, T_1, ...`.**

| width | largest n with `T_n` representable | largest n the recurrence computes | status |
|---|---:|---:|---|
| `f64` (2^53) | 38 | **37** | COMPUTED -- disagrees at n=38 |
| `u64` | **46** | 46 | COMPUTED -- crate said 47 |
| `i128` | **91** | **91** | COMPUTED -- crate said 92 |
| `u128` | 92 | 92 | COMPUTED |
| `i256` | **183** | 183 | COMPUTED |
| `u256` | **184** | 184 | COMPUTED -- crate said 184 |
| `i512` | 367 | 367 | COMPUTED |

**The +1 confirms the diagnosis.** Measured signed bounds are 46 / 91 / 183;
the crate claimed 47 / 92 / 184. Every row is off by exactly one, in the same
direction -- which is the term-vs-index slip of R3 seen three times, not three
separate mistakes. (`u128` landing on 92 is a coincidence that makes the i128
row *look* defensible; the uniform +1 across all three rows is the real story.)

Two columns, because for `f64` they differ: `T_38` is representable, yet the
recurrence that produces it is already wrong, because `3*T_37` overflows first.
**That gap between "the answer fits" and "the arithmetic that got there fits"
is the whole finding of this ladder**, and it is why one number was never
enough.

For `i128` the two columns coincide at 91 -- not by a deeper law, but because
`i128::MAX` happens to fall below both `T_92` and `3*T_91`. Since
`T_(n+1) ~ 2.618*T_n < 3*T_n`, the intermediate always overflows at or before
the term, and whether the two bounds differ depends only on where the type's
ceiling lands between them. **DESIGN CHOICE: report both columns always**, so
the coincidence is never mistaken for a rule.

---

## WHAT RUSTIUM OWES THEA

The port is not a museum piece. It found things the browser should take back:

1. **Replace `Math.random` with the seeded PRNG.** Nine calls, in `seedZ` and
   `countBasins`. A basin count is currently unreproducible -- run it twice,
   get two answers, and there is no test to write, only a vibe to trust.
   `rng.rs` is `xoshiro256**` in twenty lines and reimplements identically in
   JS via `BigInt.asUintN(64, ...)`, so both sides can emit the *same stream*
   and a Monte Carlo result becomes a number you can assert. The six reference
   words are now confirmed by two independent implementations. THEA's own
   fullerene builder already says *"Deterministic. No Math.random."* -- this is
   that rule, applied to the Monte Carlo.

2. **Derive the ladder from the integer recurrence, not from `phi`.** The
   browser uses `Math.pow`, which puts a transcendental on the certified path
   for no gain. `T_n = 3*T_(n-1) - T_(n-2) - (-1)^n` gives identical integers
   using only `+ - *`. The exact side then never touches a float.

3. **Prefer `norm_sqr` to `abs` in every comparison.** `hypot` is not
   bit-portable; the square root is ceremony when you are only ordering
   magnitudes.

4. **Never call `mul_add` on the certified path.** One fused multiply-add is
   one rounding where the browser does two. It is faster, more accurate, and
   *different* -- and "more accurate" is not the contract. Bit-identity is.

5. **Run the certified/display split as a lint.** Every function's doc comment
   already names its side. That could be mechanically checked.

---

## THE PIPELINE -- the Rust lane, exact

```powershell
# the toolchain (once). R2: the MSVC default cannot link without Visual Studio.
$env:PATH = "$env:USERPROFILE\.cargo\bin;$env:PATH"
rustup toolchain install stable-x86_64-pc-windows-gnu

cd c:\PythonDevs\MNetv1\Gos

# witness 2 -- the compiler
cargo +stable-x86_64-pc-windows-gnu test              # 33 integration + 4 doctests
cargo +stable-x86_64-pc-windows-gnu test --release    # R3: where overflow WRAPS
cargo +stable-x86_64-pc-windows-gnu clippy
cargo +stable-x86_64-pc-windows-gnu doc --open        # the mathematics, rendered

# witness 3 -- a different tongue (Curse 18: py -3, never a bare .py)
py -3 verify_rustium.py
py -3 verify_rustium.py        # run TWICE -- the sha256 must not move (Curse 38)

# R5: the tree, not the folder. Confirm target/ is not tracked.
git ls-tree -r --name-only HEAD -- Gos
```

Three witnesses must agree before RUSTIUM claims anything. If one dissents,
that is a finding, not a nuisance -- it is the entire reason for the third
tongue.

---

## CODA -- what v0.1 earned

### EXACT

- IEEE-754 requires `+ - * / sqrt` to be correctly rounded; JS `Number` and
  Rust `f64` are both binary64 round-to-nearest-even. Bit-identity on the
  certified path follows **from the standard**, given no reassociation, no FMA
  contraction, and an SSE2 target. Rust satisfies all three by default.
- The transcendental functions carry no such guarantee, on any platform.
- `T_0 .. T_91` is ninety-two terms and ninety-one is the last index. Both
  sentences are true, which is the whole of R3.
- The truncated icosahedron has 60 vertices, 90 edges, 32 faces, exactly 12
  pentagons, chi=2, E/V=3/2 -- forced by Euler, trivalence, and 5/6 faces.

### COMPUTED (on this machine, 2026-08-17, two witnesses)

- 32/33 cargo tests; 31/32 Python invariants; the single dissent identical in
  both, in two languages.
- The f64 wall at n=38, the 2^53 crossing at n=39, and the mechanism between
  them: `3*T_37 = 9167309734635369 > 2^53 = 9007199254740992`.
- `i128` reaches index 91. `T_92` exceeds `i128::MAX` by a factor of 1.750.
- `u64` reaches index 46.
- All six `xoshiro256**` words from seed `0x5EED`, reproduced independently.
- The C60 topology re-derived from the phi permutations in a second language:
  60 raw points, 180 directed edges each in exactly one face, centroid exactly
  at the origin, worst sphere error 1.110e-16.

### DESIGN CHOICE

- The certified/display split as a *type-level* discipline with the side named
  in every doc comment.
- The `R` numbering lane, and promotion into KERNELIMAGIC when a curse proves
  general.
- `i128` over a bignum dependency: `[dependencies]` stays empty, and the
  ceiling is stated instead of hidden.
- The GNU toolchain alongside MSVC rather than replacing it.
- Reporting both width columns always.
- The 1.15x minimum-distance threshold in `build_edges` -- generous but
  unambiguous on a uniform polyhedron, and re-checked by `certify`, so a bad
  threshold cannot pass silently.

### HYPOTHESIS -- still owes the price

- That the browser and the Rust actually agree bit-for-bit on the certified
  path. Correct by standard; **never measured here.** Export both as hex and
  diff. This is the open thread that matters.
- That the 256-bit ladder reaches n=184.
- That `Mesh::refine()` will hold P=12 and chi=2 through the levels the
  counts predict. The crate currently *counts* the ladder; it does not yet
  *build* it. Counting is not closing (Thea, Lane A vs Lane B).

### METAPHOR / EXTERNAL

- "The compiled tongue", "the third witness".
- `graphium.py` and the census in `MATH_LEDGER.md`: 2,333 sims, 70,224 function
  bodies, 5,598 distinct rules, 9.89x compression if the kernel were extracted.
  A separate artifact -- audit it on its own terms.

---

## THE NEXT RUNGS

- Apply R3, R5, R6. Re-run both witnesses to a clean 33/33 and 32/32, and let
  the certificate finally emit.
- Run the doctests. They have never executed.
- Run `--release`. That is the profile where R3 has teeth.
- **Measure the bit-identity claim.** Highest value, lowest cost in this scroll.
- `Mesh::refine()` -- build level 1..k, do not merely count it. Then certify
  each level: counting is not closing.
- Carry `rng.rs` back into THEA and make the basin count assertable.

---

*RUSTIUM v0.1 -- the compiled tongue. Two witnesses spoke, they disagreed with*
*the scroll on exactly one number, and the number lost. That is the system*
*working.*

*Incomplete is fine. Fake is not. Asserted is not executed.*
*P=12 . chi=2 . E/V=3/2 . hash the math not the moment . the price is always paid . always*
