//! The exact ladder, and the wall where float64 stops telling the truth.
//!
//! THEA runs an integer ladder two ways -- exactly, and in float64 -- and
//! compares them. The point is not that float64 is bad. The point is that the
//! wall is *predictable*, and you can walk right up to it and photograph it.
//!
//! # The sequence
//!
//! ```text
//! T_0 = 1,  T_1 = 3,  T_n = 3*T_(n-1) - T_(n-2) - (-1)^n
//! 1, 3, 7, 19, 49, 129, 337, 883, 2311, 6051, 15841, 41473, ...
//! ```
//!
//! The browser version derives these from `phi` with `Math.pow`. That is
//! elegant but it puts a transcendental on the certified path. The recurrence
//! above gives the identical integers using only `+ - *`, so the exact side
//! never touches a float at all.
//!
//! # Where float64 breaks -- and it is not where you would guess
//!
//! `T_39` is the first term that exceeds `2^53`, so you would expect the f64
//! ladder to survive through `n = 38`. It does not: **the f64 recurrence
//! first disagrees at n = 38**, one step earlier.
//!
//! The reason is the intermediate. Computing `T_38` needs `3*T_37`, and
//!
//! ```text
//! 3 * T_37 = 3 * 3_055_769_911_545_123 = 9_167_309_734_635_369
//!                                  2^53 = 9_007_199_254_740_992
//! ```
//!
//! so the *product* leaves the exactly-representable range before the *term*
//! does. Above `2^53` an f64 can only hold even integers, the product rounds
//! down by one, and the error is baked in from then on.
//!
//! `T_38` exact is `8_000_109_490_224_391`; in f64 it is `...390`. Off by one,
//! and it compounds.
//!
//! # Integer width
//!
//! **Convention: `n` is an INDEX into `T_0, T_1, ...`, never a count of terms.**
//! Getting that wrong is how the table below was previously off by one on every
//! row (RUSTIUM curse R3). All values here are measured, not quoted.
//!
//! | width | last exact index | note |
//! |---|---:|---|
//! | f64 exact | n = 37 | the wall being demonstrated; disagrees at 38 |
//! | `u64` | n = 46 | |
//! | **`i128`** | **n = 91** | native Rust, no dependency -- what this uses |
//! | `u128` | n = 92 | |
//! | `i256` / `u256` | n = 183 / 184 | only needed past 91 |
//!
//! `i128` more than doubles the float64 range while keeping the crate
//! dependency-free. Anything past `n = 91` returns [`LadderError`] rather than
//! wrapping: refusing to guess beats a silent wrong answer.
//!
//! That promise is enforced by `checked_*` arithmetic in [`exact_measured`],
//! **not** by the constant. Rust wraps integers silently in release builds, so
//! a guard that is only a magic number is false in exactly the profile you
//! ship. The constant is documentation; the arithmetic is the fence.

/// The ladder overflowed the integer type. Reported, never wrapped.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct LadderError {
    /// The step at which `i128` could no longer hold the value.
    pub at: usize,
}

impl core::fmt::Display for LadderError {
    fn fmt(&self, w: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        write!(
            w,
            "ladder exceeds i128 at n = {} (max exact n = {})",
            self.at, I128_MAX_N
        )
    }
}

impl std::error::Error for LadderError {}

/// The largest **INDEX** `n` for which `T_n` is computable in `i128`.
///
/// Measured, not asserted: `T_91` fits and `T_92` exceeds `i128::MAX` by a
/// factor of 1.750. `T_0..T_91` is *ninety-two terms* -- that arithmetic is
/// exactly how this constant was previously wrong by one (RUSTIUM R3).
///
/// [`the_stated_bound_is_the_measured_bound`] proves this constant against the
/// arithmetic rather than trusting it.
///
/// [`the_stated_bound_is_the_measured_bound`]: ../../tests/certification.rs
pub const I128_MAX_N: usize = 91;

/// The first `n` at which the float64 recurrence disagrees with the exact one.
/// Not where `T_n` exceeds `2^53` (that is 39) -- one step earlier, because
/// the intermediate `3*T_(n-1)` overflows first.
pub const F64_WALL: usize = 38;

/// The last `n` the float64 recurrence still gets exactly right.
pub const F64_LAST_GOOD: usize = 37;

/// `2^53` -- above this an f64 can only represent even integers.
pub const TWO_POW_53: i128 = 9_007_199_254_740_992;

/// The exact ladder to `n`, in `i128`. Pure integer arithmetic: no `phi`, no
/// `powf`, no rounding, nothing to argue about.
///
/// Returns [`LadderError`] rather than wrapping if `n > I128_MAX_N`.
///
/// ```
/// use goldberg_kernel::ladder::exact;
/// assert_eq!(exact(8).unwrap(), vec![1, 3, 7, 19, 49, 129, 337, 883, 2311]);
/// ```
pub fn exact(n: usize) -> Result<Vec<i128>, LadderError> {
    if n > I128_MAX_N {
        return Err(LadderError { at: n });
    }
    exact_measured(n)
}

/// The ladder to `n`, bounded by the ARITHMETIC rather than by
/// [`I128_MAX_N`].
///
/// Identical to [`exact`] except that it consults no constant: every step runs
/// through `checked_mul` / `checked_sub`, so the first genuinely
/// unrepresentable term returns [`LadderError`] no matter what any constant
/// claims. This is what makes the stated bound falsifiable instead of merely
/// asserted -- and it is what keeps the "never wraps" promise true in a release
/// build, where Rust's overflow checks are off and `3 * t[k-1]` would otherwise
/// wrap in silence.
///
/// ```
/// use goldberg_kernel::ladder::{exact_measured, I128_MAX_N};
/// assert!(exact_measured(I128_MAX_N).is_ok());
/// assert!(exact_measured(I128_MAX_N + 1).is_err());   // the arithmetic says so
/// ```
pub fn exact_measured(n: usize) -> Result<Vec<i128>, LadderError> {
    let mut t: Vec<i128> = Vec::with_capacity(n + 1);
    t.push(1);
    if n == 0 {
        return Ok(t);
    }
    t.push(3);
    for k in 2..=n {
        let sign: i128 = if k % 2 == 0 { 1 } else { -1 };
        let next = t[k - 1]
            .checked_mul(3)
            .and_then(|x| x.checked_sub(t[k - 2]))
            .and_then(|x| x.checked_sub(sign))
            .ok_or(LadderError { at: k })?;
        t.push(next);
    }
    Ok(t)
}

/// The same recurrence in `f64`. This is the one that breaks, on purpose.
pub fn in_f64(n: usize) -> Vec<f64> {
    let mut t: Vec<f64> = Vec::with_capacity(n + 1);
    t.push(1.0);
    if n == 0 {
        return t;
    }
    t.push(3.0);
    for k in 2..=n {
        let sign = if k % 2 == 0 { 1.0 } else { -1.0 };
        let next = 3.0 * t[k - 1] - t[k - 2] - sign;
        t.push(next);
    }
    t
}

/// One rung, with both derivations side by side and the error between them.
#[derive(Clone, Copy, Debug)]
pub struct Rung {
    pub n: usize,
    pub exact: i128,
    pub f64_value: f64,
    /// `|f64 - exact| / exact`. Zero below the wall.
    pub rel_err: f64,
    pub agrees: bool,
    /// Whether `T_n` itself has left the exactly-representable range.
    pub above_2p53: bool,
}

/// Walk both ladders together. This is the measurement THEA displays: target
/// and result and the error, always, side by side -- never the target alone.
pub fn compare(n: usize) -> Result<Vec<Rung>, LadderError> {
    let e = exact(n)?;
    let f = in_f64(n);
    Ok((0..=n)
        .map(|i| {
            let ex = e[i];
            let fv = f[i];
            let diff = (fv - ex as f64).abs();
            Rung {
                n: i,
                exact: ex,
                f64_value: fv,
                rel_err: if ex != 0 { diff / ex as f64 } else { 0.0 },
                agrees: fv == ex as f64,
                above_2p53: ex > TWO_POW_53,
            }
        })
        .collect())
}

/// The first `n` where the two derivations disagree. Measured, not assumed.
///
/// ```
/// use goldberg_kernel::ladder::{find_wall, F64_WALL};
/// assert_eq!(find_wall(60).unwrap(), Some(F64_WALL));
/// ```
pub fn find_wall(search_to: usize) -> Result<Option<usize>, LadderError> {
    Ok(compare(search_to)?
        .into_iter()
        .find(|r| !r.agrees)
        .map(|r| r.n))
}

/// The first `n` whose value exceeds `2^53`. One step *after* the wall.
pub fn find_2p53_crossing(search_to: usize) -> Result<Option<usize>, LadderError> {
    Ok(exact(search_to)?.iter().position(|&t| t > TWO_POW_53))
}
