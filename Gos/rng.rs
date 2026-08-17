//! A deterministic PRNG -- the fix for `Math.random`.
//!
//! THEA calls `Math.random` nine times, in `seedZ` and `countBasins`. That
//! makes a basin count unreproducible: run it twice, get two answers, and you
//! can never assert that Rust agrees with the browser. There is no test to
//! write, only a vibe to trust.
//!
//! Your own fullerene builder already carries the comment *"Deterministic. No
//! Math.random"*. This applies the same rule to the Monte Carlo.
//!
//! Seeded, both sides produce the same stream, and a Monte Carlo result
//! becomes a *number you can assert*. That is the whole point.
//!
//! # Algorithm
//!
//! `xoshiro256**` (Blackman & Vigna), seeded through `splitmix64`. Chosen
//! because it is about twenty lines, has no dependencies, passes the standard
//! statistical batteries, and is trivial to reimplement identically in
//! JavaScript with `BigInt.asUintN(64, ...)` -- so the browser and the port
//! can be made to emit the *identical* stream.
//!
//! Not cryptographic. Never use it for anything that needs a secret.
//!
//! ```
//! use goldberg_kernel::rng::Rng;
//! let mut a = Rng::new(0x5EED);
//! let mut b = Rng::new(0x5EED);
//! assert_eq!(a.next_u64(), b.next_u64()); // the point: reproducible
//! ```

/// `xoshiro256**` with `splitmix64` seeding.
#[derive(Clone, Debug)]
pub struct Rng {
    s: [u64; 4],
}

/// One step of `splitmix64`. Used only to expand a seed into state, which is
/// what keeps a seed of `0` from producing an all-zero (and therefore stuck)
/// xoshiro state.
fn splitmix64(x: &mut u64) -> u64 {
    *x = x.wrapping_add(0x9E37_79B9_7F4A_7C15);
    let mut z = *x;
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    z ^ (z >> 31)
}

impl Rng {
    /// Seed the generator. The same seed always gives the same stream.
    pub fn new(seed: u64) -> Rng {
        let mut x = seed;
        Rng {
            s: [
                splitmix64(&mut x),
                splitmix64(&mut x),
                splitmix64(&mut x),
                splitmix64(&mut x),
            ],
        }
    }

    /// The next 64 raw bits.
    pub fn next_u64(&mut self) -> u64 {
        let result = self.s[1].wrapping_mul(5).rotate_left(7).wrapping_mul(9);
        let t = self.s[1] << 17;
        self.s[2] ^= self.s[0];
        self.s[3] ^= self.s[1];
        self.s[1] ^= self.s[2];
        self.s[0] ^= self.s[3];
        self.s[2] ^= t;
        self.s[3] = self.s[3].rotate_left(45);
        result
    }

    /// A uniform `f64` in `[0, 1)`.
    ///
    /// Takes the top 53 bits and scales by `2^-53` -- exactly the number of
    /// bits an f64 mantissa holds, so every value is representable and the
    /// distribution has no gaps or clumps.
    pub fn next_f64(&mut self) -> f64 {
        (self.next_u64() >> 11) as f64 * (1.0 / (1u64 << 53) as f64)
    }

    /// A uniform `f64` in `[lo, hi)`.
    pub fn range(&mut self, lo: f64, hi: f64) -> f64 {
        lo + (hi - lo) * self.next_f64()
    }

    /// A uniform point on the unit sphere (Archimedes' theorem: `z` uniform on
    /// `[-1, 1]`, angle uniform on `[0, 2pi)`). This is `seedZ` made
    /// reproducible.
    ///
    /// DISPLAY path: uses `sin`/`cos`/`sqrt`.
    pub fn on_sphere(&mut self) -> [f64; 3] {
        let z = self.range(-1.0, 1.0);
        let a = self.range(0.0, core::f64::consts::TAU);
        let r = (1.0 - z * z).max(0.0).sqrt();
        [r * a.cos(), r * a.sin(), z]
    }

    /// A uniform point in the square `[-h, h] x [-h, h]`.
    pub fn in_square(&mut self, h: f64) -> [f64; 2] {
        [self.range(-h, h), self.range(-h, h)]
    }
}

impl Default for Rng {
    /// Seeded with `0x5EED` -- deliberately a fixed constant, not the clock.
    /// A default that changes every run is how irreproducibility sneaks back in.
    fn default() -> Rng {
        Rng::new(0x5EED)
    }
}
