//! # genesis -- the v8.1 refinement operator, ported
//!
//! Step 1 of the genesis port: **the growth law**, which is the part that can
//! be certified. The geometry follows in step 2, and it lands in a different
//! precision lane -- see [`the two lanes`](#the-two-lanes) below, declared
//! here rather than discovered later.
//!
//! ## The operator
//!
//! From `builder/genesis_wallpaper_v1_7.py`, itself a transcription of the
//! browser's `GK.refineFace`. A face of arity `n` becomes `n + 1` faces:
//!
//! ```text
//!   inner[i]   = project(lerp(c, pts[i], INNER_SCALE))
//!   midRing[i] = project(lerp(c, mid(pts[i], pts[j]), MID_SCALE))
//!   em         = project(mid(pts[i], pts[j]))
//!
//!   inner cell = [inner[0..n-1]]                        <- ARITY PRESERVED
//!   cell i     = [pts[i], em, pts[j], inner[j], midRing[i], inner[i]]
//! ```
//!
//! **Arity is preserved.** A pentagon yields one pentagon plus five hexagons;
//! a hexagon yields one hexagon plus six. That single sentence is the whole
//! growth law, and getting it wrong is how the source bug below happened.
//!
//! ## The growth law -- pure integers, no float anywhere
//!
//! | op | what refines | faces | pentagons |
//! |---|---|---|---|
//! | [`Op::All`] | everything | `6P + 7H` = `7F - 12` | `P` |
//! | [`Op::Hex`] | hexagons only | `P + 7H` = `7F - 72` | `P` |
//! | [`Op::Pent`] | pentagons only | `H + 6P` = `F + 5P` | `P` |
//!
//! `P` never moves. It cannot: Euler forces twelve, and the operator that
//! refines a pentagon hands back exactly one pentagon.
//!
//! ## The bug this port found
//!
//! The Python shipped `Op::Pent` as `(H + 7P, 0)` -- seven children per
//! pentagon, and `P' = 0`. A shell with no pentagons is an object Euler
//! forbids, and `predict_ops` compounded it: every later step was then priced
//! against that impossible shell.
//!
//! It survived because the file's own verification line covers `all` and
//! `6s` and *not* `5s` -- the ladder `32 -> 212 -> 1412 -> 9812 -> 68612 ->
//! 480212 -> 3361412` never exercises the pentagon branch. The browser log
//! that does exercise it disagreed all along: `2352992 --5s--> 2353052`, a
//! step of `+60 = 5P`, not `+72 = 6P`.
//!
//! Fixed in `builder/genesis_wallpaper_v1_7.py` and mirrored here. Both
//! ladders are regression tests below, so the pentagon branch can never again
//! be the untested one.
//!
//! ## The two lanes
//!
//! **CERTIFIED** -- everything in this module today. `u64` arithmetic with
//! `checked_*`, asserted with `assert_eq!` against the browser's own logs.
//!
//! **DISPLAY, and not yet built** -- the geometry. The Python operator runs in
//! **`float32`** (41 `np.float32` sites; `SPHERE_R = 1.6`, `INNER_SCALE =
//! 0.45`, `MID_SCALE = 0.70`), while this crate's [`Vec3`](crate::Vec3) is
//! `[f64; 3]`. Those are different lanes and RULE 0 forbids asserting
//! bit-equality across them. Step 2 therefore ports the geometry in `f32`, to
//! reproduce the images bit-for-bit, and says so where it lives -- rather than
//! quietly promoting to `f64` and calling the result "the same picture".

/// Which faces a refinement touches. The browser's `REFINE ALL / 6s / 5s`.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Op {
    /// every face
    All,
    /// hexagons only -- the browser's `REFINE 6s`
    Hex,
    /// pentagons only -- the browser's `REFINE 5s`
    Pent,
}

impl Op {
    /// The browser's own button label, for logs that a human will compare
    /// against a screenshot.
    pub fn label(self) -> &'static str {
        match self {
            Op::All => "all",
            Op::Hex => "6s",
            Op::Pent => "5s",
        }
    }
}

/// A generation's face census. Pentagons are tracked separately because they
/// are the invariant, not a detail.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct Census {
    /// total faces
    pub f: u64,
    /// pentagons -- twelve, forever
    pub p: u64,
}

impl Census {
    /// The C60 seed: 12 pentagons, 20 hexagons.
    pub const C60: Census = Census { f: 32, p: 12 };

    /// The dodecahedron seed: 12 pentagons, no hexagons.
    pub const DODECAHEDRON: Census = Census { f: 12, p: 12 };

    /// Hexagons: everything that is not a pentagon.
    pub const fn h(self) -> u64 {
        self.f - self.p
    }
}

impl std::fmt::Display for Census {
    fn fmt(&self, w: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(w, "P={} F={} (H={})", self.p, self.f, self.h())
    }
}

/// Why a generation was refused.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum GrowthError {
    /// `u64` would wrap. The recurrence is exact and the mathematics is fine
    /// at this size -- 7x per level is what ends, not the geometry.
    Overflow { step: usize, op: Op },
    /// A census with more pentagons than faces, or without twelve of them.
    Impossible(Census),
}

impl std::fmt::Display for GrowthError {
    fn fmt(&self, w: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            GrowthError::Overflow { step, op } => write!(
                w,
                "step {step} ({}) overflows u64 -- the recurrence is exact, the \
                 counter is not. 7x per level is what ends, not the math.",
                op.label()
            ),
            GrowthError::Impossible(c) => {
                write!(
                    w,
                    "impossible census {c}: Euler forces exactly 12 pentagons"
                )
            }
        }
    }
}

impl std::error::Error for GrowthError {}

/// One generation forward. **The price, before a byte is allocated.**
///
/// Pure integer arithmetic, `checked_*` throughout, so the ceiling is a
/// refusal and never a wrap (RUSTIUM R3: release builds wrap silently, and a
/// guard that only holds in debug is not a guard).
///
/// ```
/// use goldberg_kernel::genesis::{Census, Op, grow};
/// // the browser: C60 --all--> 212 faces, still twelve pentagons
/// assert_eq!(grow(Census::C60, Op::All).unwrap(), Census { f: 212, p: 12 });
/// // pentagons refine to pentagons: +5 faces each, P untouched
/// assert_eq!(grow(Census::C60, Op::Pent).unwrap(), Census { f: 92, p: 12 });
/// ```
pub fn grow(c: Census, op: Op) -> Result<Census, GrowthError> {
    if c.p != 12 || c.p > c.f {
        return Err(GrowthError::Impossible(c));
    }
    let (h, p) = (c.h(), c.p);
    // arity preserved: a face of arity n -> 1 face of arity n + n hexagons.
    // pentagon -> 1 pent + 5 hex ; hexagon -> 1 hex + 6 hex
    let f = match op {
        Op::All => p
            .checked_mul(6)
            .and_then(|a| h.checked_mul(7).and_then(|b| a.checked_add(b))),
        Op::Hex => h.checked_mul(7).and_then(|b| p.checked_add(b)),
        Op::Pent => p.checked_mul(6).and_then(|a| h.checked_add(a)),
    }
    .ok_or(GrowthError::Overflow { step: 0, op })?;
    Ok(Census { f, p })
}

/// A whole plan, priced before the first allocation. Returns every
/// intermediate generation so the cost is visible per step, not just at the
/// end -- the same courtesy the Python's `--plan` extends.
///
/// ```
/// use goldberg_kernel::genesis::{Census, Op, plan};
/// // the browser's logged run: C60, all, then 6s five times
/// let ops = [Op::All, Op::Hex, Op::Hex, Op::Hex, Op::Hex, Op::Hex];
/// let steps = plan(Census::C60, &ops).unwrap();
/// let faces: Vec<u64> = steps.iter().map(|c| c.f).collect();
/// assert_eq!(faces, vec![212, 1412, 9812, 68612, 480212, 3361412]);
/// assert!(steps.iter().all(|c| c.p == 12));
/// ```
pub fn plan(seed: Census, ops: &[Op]) -> Result<Vec<Census>, GrowthError> {
    let mut c = seed;
    let mut out = Vec::with_capacity(ops.len());
    for (i, &op) in ops.iter().enumerate() {
        c = grow(c, op).map_err(|e| match e {
            GrowthError::Overflow { .. } => GrowthError::Overflow { step: i + 1, op },
            other => other,
        })?;
        out.push(c);
    }
    Ok(out)
}

/// Vertices and edges implied by a census, for a closed trivalent shell.
///
/// `3V = 2E` and `2E = 5P + 6H`, so `V = (5P + 6H)/3` and `E = (5P + 6H)/2`.
/// Then `chi = V - E + F`, computed rather than assumed -- the whole point of
/// [`certify`].
pub fn implied(c: Census) -> Option<(u64, u64)> {
    let deg_sum = c.p.checked_mul(5)?.checked_add(c.h().checked_mul(6)?)?;
    if deg_sum % 6 != 0 {
        return None; // not a closed trivalent shell
    }
    Some((deg_sum / 3, deg_sum / 2))
}

/// `chi = V - E + F`, derived from the census. **Two must hold, or the census
/// is not a sphere.**
///
/// Note what this does *not* do: it does not assume Euler and solve for `V`.
/// `V` and `E` come from trivalence, `chi` is then computed, and it is allowed
/// to come out wrong. A check that cannot fail is not a check -- the exact
/// tautology found in the browser's `Invariants()` and in `chi = E - F + 2`.
pub fn certify(c: Census) -> Option<i64> {
    let (v, e) = implied(c)?;
    Some(v as i64 - e as i64 + c.f as i64)
}

#[cfg(test)]
mod tests {
    use super::*;

    /// The browser's own log, screenshot for screenshot.
    /// `C60 -> all -> 212 -> 6s x5 -> 1412, 9812, 68612, 480212, 3361412`
    #[test]
    fn reproduces_the_browser_ladder() {
        let ops = [Op::All, Op::Hex, Op::Hex, Op::Hex, Op::Hex, Op::Hex];
        let got: Vec<u64> = plan(Census::C60, &ops)
            .unwrap()
            .iter()
            .map(|c| c.f)
            .collect();
        assert_eq!(got, vec![212, 1412, 9812, 68612, 480212, 3361412]);
    }

    /// The branch the Python never tested, which is why it was wrong.
    /// Logged: `2352992 --5s--> 2353052 --5s--> 2353112`, P=12 throughout.
    #[test]
    fn reproduces_the_pentagon_branch() {
        let c = Census {
            f: 2_352_992,
            p: 12,
        };
        let a = grow(c, Op::Pent).unwrap();
        let b = grow(a, Op::Pent).unwrap();
        assert_eq!((a.f, a.p), (2_353_052, 12));
        assert_eq!((b.f, b.p), (2_353_112, 12));
        // the step is +5P, not +6P -- the exact off-by-one that shipped
        assert_eq!(a.f - c.f, 5 * c.p);
    }

    /// The closed forms in the module table, checked against the recurrence.
    #[test]
    fn closed_forms_agree_with_the_recurrence() {
        let mut c = Census::C60;
        for _ in 0..6 {
            assert_eq!(grow(c, Op::All).unwrap().f, 7 * c.f - 12);
            assert_eq!(grow(c, Op::Hex).unwrap().f, 7 * c.f - 72);
            assert_eq!(grow(c, Op::Pent).unwrap().f, c.f + 5 * c.p);
            c = grow(c, Op::Hex).unwrap();
        }
    }

    /// P is the invariant. Every op, every depth, both seeds.
    #[test]
    fn twelve_pentagons_forever() {
        for seed in [Census::C60, Census::DODECAHEDRON] {
            for op in [Op::All, Op::Hex, Op::Pent] {
                let mut c = seed;
                for _ in 0..8 {
                    c = grow(c, op).unwrap();
                    assert_eq!(c.p, 12, "{} broke P at {c}", op.label());
                }
            }
        }
    }

    /// chi is COMPUTED from trivalence, not assumed. It must land on 2.
    #[test]
    fn chi_is_two_and_was_allowed_not_to_be() {
        let mut c = Census::C60;
        for _ in 0..10 {
            assert_eq!(certify(c), Some(2), "chi moved at {c}");
            c = grow(c, Op::All).unwrap();
        }
        // and the guard has teeth: an eleven-pentagon shell is not trivalent-closed
        assert_eq!(certify(Census { f: 32, p: 11 }), None);
    }

    /// The `Op::All` ladder is the crate's existing `goldberg_counts` ladder,
    /// arrived at by a different route. Two derivations, one sequence.
    #[test]
    fn agrees_with_the_goldberg_ladder() {
        let mut c = Census::C60;
        for k in 0..5u32 {
            assert_eq!(c.f as usize, crate::goldberg_counts(k).f, "level {k}");
            c = grow(c, Op::All).unwrap();
        }
    }

    /// The ceiling refuses; it does not wrap. R3's lesson, applied up front.
    #[test]
    fn overflow_refuses_loudly() {
        let mut c = Census::C60;
        let mut steps = 0;
        loop {
            match grow(c, Op::All) {
                Ok(n) => {
                    c = n;
                    steps += 1;
                    assert!(steps < 200, "u64 should have ended this");
                }
                Err(GrowthError::Overflow { .. }) => break,
                Err(e) => panic!("wrong refusal: {e}"),
            }
        }
        // ~7x per step, so u64 lasts around 22 generations
        assert!((18..26).contains(&steps), "ended at {steps} steps");
    }

    #[test]
    fn impossible_census_is_refused() {
        assert!(matches!(
            grow(Census { f: 32, p: 11 }, Op::All),
            Err(GrowthError::Impossible(_))
        ));
    }
}
