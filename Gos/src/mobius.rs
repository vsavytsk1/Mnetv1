//! `mobius` -- the sphere bent onto a Möbius band, and what that does NOT do.
//!
//! Ported from `shell/genesis_v8.5.2.html` line 4289, `sphereToMobius`.
//!
//! # THE LANE, stated first because it decides everything below
//!
//! **DISPLAY.** The map uses `atan2`, `acos`, `cos` and `sin`, none of which
//! IEEE-754 requires to be correctly rounded. A Möbius point computed here and
//! a Möbius point computed in the browser will agree to about an ULP and never
//! exactly. **Nothing on this path may carry a bit-identity claim** -- which is
//! RULE 0, and it is the reason this is a separate module from `genesis`.
//!
//! # WHAT THE TWIST ACTUALLY DOES
//!
//! It moves points. That is all it does.
//!
//! The browser's own comment says *"chi: 2 to 0. Remove 2 antipodal faces,
//! half-twist"*, and logs `chi:'2->0'`. Read the code: **no face is ever
//! removed** -- there is no `splice`, no `filter`, no reassignment of the face
//! array in the whole Möbius engine -- and `invariants()` is never called
//! inside it. The `'2->0'` is a **string literal in a log line**, not a
//! measurement.
//!
//! So the connectivity is untouched, and a mesh whose connectivity is untouched
//! has the Euler characteristic it always had. What the twist produces is a
//! **Möbius-shaped immersion of a sphere mesh**, not a Möbius topology.
//!
//! A real Möbius band needs two hexagonal faces to die -- the precursor archive
//! states the arithmetic exactly:
//!
//! ```text
//!   Sphere:  V=60 E=90 F=32  chi=2   (12 pent + 20 hex)
//!   Mobius:  V=60 E=90 F=30  chi=0   (12 pent + 18 hex -- 2 faces die)
//!   Euler forces F = E - V + chi = 90 - 60 + 0 = 30.
//!   Two hexagonal faces must die. They are the cost of the twist.
//! ```
//!
//! This module does not remove them. It bends the shell and **reports the
//! Euler characteristic it actually has**, which is the whole difference
//! between this port and the page it came from. `GALACTIC_LAW` forbids the
//! Möbius as a run; keeping it as a *studied object* is why the law is legible.

use crate::Vec3;

/// The band's geometry. Browser defaults: `R = 2.5`, `W = 0.8`.
#[derive(Clone, Copy, PartialEq, Debug)]
pub struct Band {
    /// major radius -- how far the band's centreline sits from the origin
    pub r: f64,
    /// half-width -- how far the surface reaches either side of that line
    pub w: f64,
}

impl Default for Band {
    /// The browser's constants, kept verbatim so a picture can be compared
    /// against `genesis_v8.5.2.html` without a scale factor in the way.
    fn default() -> Self {
        Band { r: 2.5, w: 0.8 }
    }
}

impl Band {
    /// A band whose reach matches a sphere of `radius`, keeping the browser's
    /// 2.5 : 0.8 proportions.
    ///
    /// **Why this exists.** The browser hardcodes `R = 2.5` because its sphere
    /// is one fixed size. Ours has `sphere_r` as a live control, default 1.6 --
    /// and measured, the default band reaches `|p| = 3.247` against the
    /// sphere's `1.600`. **The twist doubles the picture**, so the shell walks
    /// off the edge of the view and the operator has to zoom out to follow it.
    ///
    /// Reported from the render as *"the mobius is linked to the zoom"*, which
    /// is exactly what it looked like and exactly what it was.
    ///
    /// `reach = r + w`, so scaling both by `radius / (r + w)` puts the band's
    /// outermost point where the sphere's was. The twist then changes the
    /// SHAPE without changing the SIZE, which is the only way to see what the
    /// twist itself did.
    ///
    /// Note the band stays **flat**: its z extent is `w` while x and y reach
    /// `r + w`, about 4 : 1 at these proportions. A sphere looks identical from
    /// every angle and a flat ring does not, so `pitch` becomes far more
    /// visible during a twist. That is the geometry, not a bug.
    pub fn fit(radius: f64) -> Band {
        let d = Band::default();
        let reach = d.r + d.w;
        if reach <= 0.0 || radius <= 0.0 {
            return d;
        }
        let k = radius / reach;
        Band {
            r: d.r * k,
            w: d.w * k,
        }
    }

    /// The furthest a point can land: `r + w`.
    pub fn reach(&self) -> f64 {
        self.r + self.w
    }
}

/// Maps one point from the sphere onto the band.
///
/// DISPLAY LANE -- four transcendentals, no bit-identity.
///
/// The half-angle `u / 2` inside the cosine is the twist: going once around
/// (`u` to `u + 2π`) turns the cross-section over, which is what makes the
/// surface one-sided.
///
/// A point at the origin has no direction to convert, so it is sent to the
/// band's own reference point rather than producing a NaN. The browser does
/// the same, at the same threshold.
pub fn sphere_to_mobius(p: Vec3, b: Band) -> Vec3 {
    let (x, y, z) = (p[0], p[1], p[2]);
    let r = (x * x + y * y + z * z).sqrt();
    if r < 1e-10 {
        return [b.r, 0.0, 0.0];
    }
    let theta = y.atan2(x);
    let phi = (z / r).clamp(-1.0, 1.0).acos();
    let u = theta + std::f64::consts::PI;
    let v = (phi / std::f64::consts::PI - 0.5) * 2.0 * b.w;
    let ring = b.r + v * (u / 2.0).cos();
    [ring * u.cos(), ring * u.sin(), v * (u / 2.0).sin()]
}

/// Straight-line blend, `t = 0` sphere, `t = 1` band.
///
/// The browser lerps the same way, which is why the intermediate shapes match
/// in form even though the endpoints are only ULP-close.
pub fn lerp(a: Vec3, b: Vec3, t: f64) -> Vec3 {
    [
        a[0] * (1.0 - t) + b[0] * t,
        a[1] * (1.0 - t) + b[1] * t,
        a[2] * (1.0 - t) + b[2] * t,
    ]
}

/// What a Möbius band of this many vertices and edges WOULD need, if the twist
/// were a topology change rather than a bend.
///
/// `chi = 0` forces `F = E - V`. Compare against the face count you actually
/// have; the difference is how many faces would have to die.
///
/// EXACT -- integer arithmetic only.
pub fn faces_for_chi_zero(v: u64, e: u64) -> Option<u64> {
    e.checked_sub(v)
}
