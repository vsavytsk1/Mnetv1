# goldberg_kernel v0.2

> *A fullerene is the only closed structure you can build from pentagons and
> hexagons. Euler proved it. Chemistry confirmed it. Here it is in Rust.*

Zero dependencies. Four source files. 33 tests.

## Install Rust

```powershell
winget install Rustlang.Rustup
```

Restart the terminal, then check:

```powershell
rustc --version
cargo --version
```

In VS Code install **rust-analyzer** (`rust-lang.rust-analyzer`). Do not
install the old "Rust" extension -- it is deprecated and they fight.

## Build

```powershell
cd Gos
cargo test                  # the certification suite -- 33 tests
cargo test -- --nocapture   # with output
cargo doc --open            # the mathematics, rendered
```

## What is in it

| module | what | path |
|---|---|---|
| `lib` | the 13 shared rules + C60 topology + `certify` | certified |
| `ladder` | the exact integer ladder, and where float64 breaks | certified |
| `complex` | `cadd` `csub` `cmul` `cdiv` `cabs` `cpow`, stereographic projection | mostly certified |
| `rng` | deterministic `xoshiro256**` -- replaces `Math.random` | display |

## The certified path and the display path

This is the one architectural idea in the crate, and it comes straight out of
reading THEA v1.3.7.

JavaScript `Number` and Rust `f64` are both IEEE-754 binary64. For `+ - * /`
and `sqrt` both are **correctly rounded**, so results are bit-identical and the
port is a *translation*.

`sin` `cos` `exp` `ln` `powf` `hypot` are **not** bit-guaranteed -- not across
platforms, not between JS and Rust. They agree to about an ULP, never exactly.

So:

* **certified** -- integers, and f64 restricted to `+ - * / sqrt`.
  Asserted with `assert_eq!`.
* **display** -- anything transcendental. Asserted with tolerances.

Never assert bit-equality across that boundary. THEA already tracks error
explicitly (`f16round`, `casIdentityFails`, `a2NormErr`) -- this just makes the
boundary a rule instead of a habit.

Every function's doc comment says which side it is on.

## Two findings worth keeping

### 1. The float64 wall is at n = 38, not 39

The ladder is `T_n = 3*T_(n-1) - T_(n-2) - (-1)^n`, starting `1, 3`:

```
1, 3, 7, 19, 49, 129, 337, 883, 2311, 6051, 15841, 41473, ...
```

`T_39` is the first term to exceed `2^53`, which is where you would expect
float64 to fail. It fails one step earlier, at **n = 38**, because the
*intermediate* goes first:

```
3 * T_37 = 3 * 3_055_769_911_545_123 = 9_167_309_734_635_369
                                 2^53 = 9_007_199_254_740_992
```

Above `2^53` an f64 holds only even integers, so the product rounds down by
one. `T_38` exact is `8_000_109_490_224_391`; in f64 it is `...390`. The term
itself is still comfortably representable -- the multiplication that produced
it was not.

Both facts are asserted (`float64_wall_is_at_thirty_eight`,
`value_crosses_two_pow_53_one_step_after_the_wall`).

### 2. The ladder needs no `phi` at all

The browser derives these terms from `phi` with `Math.pow`, which puts a
transcendental on the certified path. The integer recurrence gives the
identical values using only `+ - *`. The exact side now never touches a float.

Integer width, measured:

| width | reaches |
|---|---:|
| f64 exact | n = 37 |
| `u64` | n = 47 |
| **`i128`** | **n = 92** |
| 256-bit | n = 184 |

`i128` is native Rust and more than doubles the float64 range with no
dependency. Past `n = 92` the ladder returns `LadderError` rather than
wrapping -- refusing to guess beats a silent wrong answer.

## The contract with the browser

`tests/certification.rs` asserts the exact table from `HELENA.md`:

```
level   T      V       E       F      P    H       chi   E/V
  0     3      60      90      32     12   20      2     1.5
  1     21     420     630     212    12   200     2     1.5
  2     147    2940    4410    1472   12   1460    2     1.5
  3     1029   20580   30870   10292  12   10280   2     1.5
```

`T = 3 * 7^k`, `V = 20T`, `E = 30T`, `F = 10T + 2`, `P = 12` forever.

Plus: all 180 directed edges belong to exactly one face (that is what proves
the surface is genuinely closed *and* orientable, not merely that the counts
add up), all vertices trivalent, all on the unit sphere, centroid at the
origin.

If a test fails, the port changed the mathematics. That is a finding, not a
nuisance -- it is the entire reason the invariants are asserted.

## What to change in THEA

**Replace `Math.random` with a seeded PRNG.** Nine calls, in `seedZ` and
`countBasins`. Right now a basin count is unreproducible: run it twice, get
two answers, and there is no test to write -- only a vibe to trust. `rng.rs`
is `xoshiro256**` in twenty lines and reimplements identically in JS with
`BigInt.asUintN(64, ...)`, so both sides can emit the same stream and a Monte
Carlo result becomes a number you can assert.

Your fullerene builder already says *"Deterministic. No Math.random."* This is
the same rule applied to the Monte Carlo.

## Status -- read this honestly

Every constant in the tests was derived independently before the Rust was
written: the C60 face-tracing (V=60, E=90, F=32, P=12, H=20, chi=2, E/V=1.5,
all trivalent), the ladder and its wall at n=38, the i128 limit at n=92, and
the six `xoshiro256**` output words.

The Rust itself was **not compiled by its author** -- no toolchain was
available in that environment. Brace balance and API agreement were verified
statically; the algorithms were verified numerically.

So treat your first `cargo test` as the real verification. If `rustc` objects,
expect small type or borrow fixes, not a design problem. The mathematics
underneath is proven.

*Incomplete is fine. Fake is not.*

## Next

- `Mesh::refine()` -- build level 1..k, not only count it
- `putImageData` -> `softbuffer` framebuffer (THEA's rasterizer)
- `jacobiEig` / `lanczosLow` -- the light matrix eigensolvers
- the Mobius heart, `chi = 0`, for HELENA

---

MIT. *P=12 . chi=2 . E/V=1.5 . the price is always paid . always*
