//! # genesis -- the `GK` refinement operator, ported
//!
//! **Source of truth: `shell/genesis_v8.5.2.html`, module `goldberg_kernel.js`.**
//! See `grimoire/GENESIS_PORT_SPEC.md`, which dissects it line by line.
//!
//! Measured 2026-08-20, because the version number here was wrong for a day
//! and sent a reader to the wrong file: v8.5.2's `GK` is **v8.1's `GK`
//! verbatim plus 218 lines, with zero lines removed or changed**. So v8.1 is a
//! strict subset and porting v8.5.2 costs nothing extra. The 218 added lines
//! are `_baryInt`, `_convexHull`, `_icosahedron` and their helpers -- the
//! exact integer barycentric lattice that RUSTIUM R7 prescribes as the cure
//! for a float-thresholded weld.
//!
//! Steps 1 and 2 of the port live here: **the growth law** (integers, and the
//! part that can be certified) and **the data model plus the operator**.
//!
//! ## The operator
//!
//! Ported from `GK.refineFace` in the HTML -- *not* from
//! `builder/genesis_wallpaper_v1_7.py`, which is untested and shipped the
//! pentagon bug described below. A face of arity `n` becomes `n + 1` faces:
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
//! **CERTIFIED** -- the growth law: [`Census`], [`grow`], [`plan`],
//! [`certify`]. `u64` arithmetic with `checked_*`, asserted with `assert_eq!`
//! against the browser's own logs.
//!
//! **CERTIFIED, and this is the correction that matters** -- the geometry.
//! An earlier draft of this header said step 2 would port the operator in
//! `f32` to match `genesis_wallpaper_v1_7.py`. **That was the wrong target.**
//! JS `Number` is binary64 and this crate's [`Vec3`](crate::Vec3) is
//! `[f64; 3]` -- the *same lane* -- so the browser's geometry can be asserted
//! bit-identical. The **Python** is the one in `float32`, and it is not the
//! spec. We target the browser.
//!
//! Bit-identity is a promise about the **expression**, not the value. IEEE-754
//! gives correct rounding per *operation*, so `sum/n` and `sum*(1/n)` are the
//! same number in algebra and different doubles in binary64. [`centroid`] and
//! [`project_to_sphere`] were spelled the second way and were fixed (R12);
//! all 90 tests passed on both spellings, so the four tests that now freeze
//! the browser's spelling are the only thing guarding it.
//!
//! **DISPLAY** -- [`Params::jitter`] only. The browser jitters with
//! `Math.random()`; we use the seeded [`Rng`](crate::rng::Rng) so a jittered
//! mesh is reproducible. Same shape, **different stream**: with `jitter > 0`
//! the geometry is ours, not the browser's, and no bit-identity is claimed.
//! At the default `jitter = 0` the RNG is never consulted.

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

// ===========================================================================
// STEP 2 -- THE DATA MODEL AND THE OPERATOR
//
// Ported from `GK.refineFace` / `GK.refineAll` / `GK.undo` in
// `shell/genesis_v8.5.2.html`. Immutability is part of the contract: every
// refinement returns a NEW state and appends `{op, snapshot}` to history.
// That is what makes UNDO work, and a port that mutates in place has not
// ported it.
// ===========================================================================

use crate::rng::Rng;
use crate::{centroid, project_to_sphere, vlerp, Mesh, Vec3};

/// A face's arity. The browser's `type: 'pent' | 'hex'`.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Kind {
    /// five sides -- one of the twelve Euler forces
    Pent,
    /// six sides
    Hex,
}

impl Kind {
    /// How many sides this kind has.
    pub fn sides(self) -> usize {
        match self {
            Kind::Pent => 5,
            Kind::Hex => 6,
        }
    }

    /// The browser's string, for logs and the HUD.
    pub fn label(self) -> &'static str {
        match self {
            Kind::Pent => "pent",
            Kind::Hex => "hex",
        }
    }

    /// Classify by side count. `None` for anything that is not 5 or 6 --
    /// a Goldberg shell has no other face, so nothing here defaults.
    pub fn from_sides(n: usize) -> Option<Kind> {
        match n {
            5 => Some(Kind::Pent),
            6 => Some(Kind::Hex),
            _ => None,
        }
    }
}

/// One face. **The mesh is FACE SOUP** -- faces carry their own points and
/// vertices are duplicated between neighbours, never welded.
///
/// That is deliberate, and it is what lets the browser reach millions of faces
/// with no index structure. It is also why [`State::invariants`] has to
/// *reconstruct* V and E rather than count them.
#[derive(Clone, Debug, PartialEq)]
pub struct Face {
    /// the corners, CCW seen from outside
    pub pts: Vec<Vec3>,
    /// pentagon or hexagon
    pub kind: Kind,
    /// refinement depth; the seed is 0
    pub level: u32,
    /// the path of child indices from the seed face
    pub lineage: Vec<usize>,
    /// stable, minted once: `F7`, then `F7.c33`, `F7.e34`, ...
    pub id: String,
    /// **pentagons only** -- the thread back to one of the original twelve.
    ///
    /// Each refined pentagon inherits its parent's anchor, so the number of
    /// distinct anchors must stay 12 forever. That is an independent witness
    /// to `P=12`: it does not count a `kind` label, so it cannot be fooled by
    /// the mislabelling that made `MnetUni`'s pentagon count a tautology.
    pub anchor: Option<String>,
}

/// Where refined points land. The browser's `surfaceMode`.
#[derive(Clone, Copy, PartialEq, Eq, Debug, Default)]
pub enum Surface {
    /// leave points where the lerp puts them
    #[default]
    Planar,
    /// push every refined point onto the sphere of radius [`Params::sphere_r`]
    Spherical,
}

/// The operator's parameter block. Defaults are the browser's own, read out of
/// `GK.refineFace`'s parameter list.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct Params {
    /// where the inner copy of the parent sits. Browser default `0.45`.
    pub inner_scale: f64,
    /// how far edge midpoints get pulled inward. Browser default `0.70`.
    pub mid_scale: f64,
    /// if true, the inner face of a pentagon is a pentagon. Default `true`.
    pub preserve_pent_in_pent: bool,
    /// if true, the inner face of a hexagon is a hexagon. Default `true`.
    pub preserve_hex_in_hex: bool,
    /// planar or spherical. Default planar.
    pub surface: Surface,
    /// the sphere radius used when `surface` is spherical. Default `1.6`.
    pub sphere_r: f64,
    /// symmetry-breaking perturbation. Default `0` -- **and at 0 the RNG is
    /// never consulted**, which is what keeps the default path bit-identical
    /// to the browser.
    pub jitter: f64,
}

impl Default for Params {
    fn default() -> Self {
        Params {
            inner_scale: 0.45,
            mid_scale: 0.70,
            preserve_pent_in_pent: true,
            preserve_hex_in_hex: true,
            surface: Surface::Planar,
            sphere_r: 1.6,
            jitter: 0.0,
        }
    }
}

/// Refine one face into `n + 1` children: one inner face of the parent's own
/// arity, plus one hexagon per parent edge.
///
/// **The two sentences that are the whole growth law:** the inner face
/// preserves arity, and the surrounding cells are always hexagons.
///
/// ```text
///   inner[i]   = proj(lerp(c, pts[i], inner_scale))
///   midRing[i] = proj(lerp(c, mid(pts[i], pts[j]), mid_scale))
///   em         = proj(mid(pts[i], pts[j]))
///
///   inner  = [inner[0..n-1]]                          <- ARITY PRESERVED
///   cell i = [pts[i], em, pts[j], inner[j], midRing[i], inner[i]]
/// ```
///
/// **Jitter touches `inner` and `midRing` ONLY** -- never `pts[i]`, `pts[j]`
/// or `em`. Those three are shared with the neighbouring face, and jittering
/// them would tear the mesh. DESIGN CHOICE, and load-bearing.
///
/// **THE CRESCENT DEFECT.** `midRing[i]` sits on the hexagon side of the cell
/// edge and nowhere on the cell side, so with `mid_scale > inner_scale` the
/// ring opens a rosette gap. **That is not a bug -- it is the picture.** A
/// port that "corrects" it renders different images and has failed.
///
/// `rng` is consulted only when `jitter > 0`.
pub fn refine_face(face: &Face, p: &Params, counter: &mut u64, rng: &mut Rng) -> Vec<Face> {
    let pts = &face.pts;
    let n = pts.len();
    let c = centroid(pts);

    let proj = |v: Vec3| match p.surface {
        Surface::Planar => v,
        Surface::Spherical => project_to_sphere(v, p.sphere_r),
    };

    // the inner ring: every corner pulled toward the centroid
    let mut inner: Vec<Vec3> = Vec::with_capacity(n);
    for pt in pts.iter() {
        inner.push(proj(vlerp(c, *pt, p.inner_scale)));
    }

    // the mid ring: every edge midpoint, then pulled inward
    let mut mid_ring: Vec<Vec3> = Vec::with_capacity(n);
    for i in 0..n {
        let m = vlerp(pts[i], pts[(i + 1) % n], 0.5);
        mid_ring.push(proj(vlerp(c, m, p.mid_scale)));
    }

    // DISPLAY LANE. The browser uses Math.random() here, which makes a
    // jittered mesh unreproducible; we use the seeded stream instead, so this
    // is OURS and not the browser's. No bit-identity is claimed when jitter>0.
    if p.jitter > 0.0 {
        for v in inner.iter_mut().chain(mid_ring.iter_mut()) {
            for c in v.iter_mut() {
                *c += (rng.next_f64() - 0.5) * p.jitter;
            }
        }
    }

    let mut out = Vec::with_capacity(n + 1);

    // the inner face -- arity preserved, and a pentagon INHERITS its anchor
    let inner_kind = match face.kind {
        Kind::Pent => {
            if p.preserve_pent_in_pent {
                Kind::Pent
            } else {
                Kind::Hex
            }
        }
        Kind::Hex => {
            if p.preserve_hex_in_hex {
                Kind::Hex
            } else {
                Kind::Pent
            }
        }
    };
    *counter += 1;
    let mut lineage = face.lineage.clone();
    lineage.push(0);
    out.push(Face {
        pts: inner.clone(),
        kind: inner_kind,
        level: face.level + 1,
        lineage,
        id: format!("{}.c{}", face.id, counter),
        anchor: if inner_kind == Kind::Pent {
            Some(face.anchor.clone().unwrap_or_else(|| "A?".to_string()))
        } else {
            None
        },
    });

    // one hexagonal cell per parent edge -- ALWAYS a hexagon, whatever the
    // parent was. That is the second half of the growth law.
    for i in 0..n {
        let j = (i + 1) % n;
        let em = proj(vlerp(pts[i], pts[j], 0.5));
        *counter += 1;
        let mut lineage = face.lineage.clone();
        lineage.push(i + 1);
        out.push(Face {
            pts: vec![pts[i], em, pts[j], inner[j], mid_ring[i], inner[i]],
            kind: Kind::Hex,
            level: face.level + 1,
            lineage,
            id: format!("{}.e{}", face.id, counter),
            anchor: None,
        });
    }

    out
}

/// What a history entry records.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Step {
    /// `REFINE ALL` / `REFINE 6s` / `REFINE 5s`
    Refine(Op),
    /// one face, by index -- the browser's `refineOne`
    One(usize),
}

/// One undo point: the operation, and the face list as it was *before* it.
#[derive(Clone, Debug)]
pub struct Snapshot {
    /// what was done
    pub step: Step,
    /// the faces before it was done
    pub faces: Vec<Face>,
}

/// The whole mesh, its undo stack, and the id counter.
///
/// **THE PRICE, stated before it is paid (Curse 35).** A snapshot is a full
/// clone of the face list, so history costs what the mesh costs. A face of
/// arity `n` holds `n` points at 24 bytes each, so a 2,353,112-face render
/// carries roughly `2.35e6 * 6 * 24 = 339 MB` **per undo step**. That is the
/// browser's design and we port it rather than silently improving it -- but
/// [`State::snapshot_bytes`] exists so the number can be printed before the
/// allocation instead of discovered during it.
#[derive(Clone, Debug)]
pub struct State {
    /// the face soup
    pub faces: Vec<Face>,
    /// the undo stack, oldest first
    pub history: Vec<Snapshot>,
    /// mints ids; threaded through a whole refinement pass
    pub counter: u64,
}

/// Why a face soup could not be measured.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum InvError {
    /// the arity sum is odd, so it cannot be twice an edge count
    NotClosed {
        /// the measured sum of face arities
        arity_sum: u64,
    },
    /// the arity sum is not divisible by three, so the shell is not trivalent
    NotTrivalent {
        /// the measured sum of face arities
        arity_sum: u64,
    },
}

impl std::fmt::Display for InvError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            InvError::NotClosed { arity_sum } => write!(
                f,
                "arity sum {arity_sum} is odd -- every edge is shared by two faces on a \
                 closed surface, so this soup is not closed"
            ),
            InvError::NotTrivalent { arity_sum } => write!(
                f,
                "arity sum {arity_sum} is not divisible by 3 -- a trivalent shell meets \
                 three faces at every vertex, so this soup is not trivalent"
            ),
        }
    }
}

impl std::error::Error for InvError {}

/// Everything measured from a face soup. **Nothing here is a literal.**
#[derive(Clone, PartialEq, Eq, Debug)]
pub struct Invariants {
    /// faces, counted
    pub faces: u64,
    /// pentagons, counted by side count
    pub pents: u64,
    /// hexagons, counted by side count
    pub hexes: u64,
    /// `arity_sum / 2`
    pub edges: u64,
    /// `arity_sum / 3` -- **trivalence, never Euler**
    pub vertices: u64,
    /// `V - E + F`, computed, and allowed to be wrong
    pub chi: i64,
    /// the deepest refinement level present
    pub max_level: u32,
    /// distinct anchors -- the second, independent witness to `P = 12`
    pub anchor_count: usize,
}

impl std::fmt::Display for Invariants {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "V={} E={} F={} P={} H={} chi={} anchors={} depth={}",
            self.vertices,
            self.edges,
            self.faces,
            self.pents,
            self.hexes,
            self.chi,
            self.anchor_count,
            self.max_level
        )
    }
}

/// A mesh's heap cost, counted field by field rather than estimated.
///
/// Every number here is walked from the built structure, so it is exact up to
/// allocator bookkeeping. That last part is not negligible: a `Face` makes
/// FOUR allocations (pts, lineage, id, anchor) and the overhead is per
/// allocation, not per byte -- at depth 7 that is 74 million allocations.
#[derive(Default, Clone, Copy, PartialEq, Eq, Debug)]
pub struct Bytes {
    /// how many faces this describes
    pub faces: u64,
    /// `size_of::<Face>()` per face -- the part that is not on the heap twice
    pub inline: u64,
    /// the corner points. FLAT at 144 B/face: six points, always.
    pub pts: u64,
    /// the lineage path. GROWS one `usize` per level.
    pub lineage: u64,
    /// the id string. GROWS a few characters per level.
    pub ids: u64,
    /// pentagons only, so twelve strings however deep it goes
    pub anchors: u64,
    /// allocations made, which is a cost in its own right
    pub allocs: u64,
}

impl Bytes {
    /// Everything.
    pub fn total(&self) -> u64 {
        self.inline + self.pts + self.lineage + self.ids + self.anchors
    }
    /// Bytes per face, the number worth comparing across depths.
    pub fn per_face(&self) -> f64 {
        self.total() as f64 / self.faces.max(1) as f64
    }
}

impl std::fmt::Display for Bytes {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "{:.1} MB ({:.0} B/face: pts {:.0}, inline {:.0}, lineage {:.0}, ids {:.0})",
            self.total() as f64 / 1_048_576.0,
            self.per_face(),
            self.pts as f64 / self.faces.max(1) as f64,
            self.inline as f64 / self.faces.max(1) as f64,
            self.lineage as f64 / self.faces.max(1) as f64,
            self.ids as f64 / self.faces.max(1) as f64
        )
    }
}

impl State {
    /// The certified C60 seed: 12 pentagons, 20 hexagons, twelve anchors.
    ///
    /// Built from [`Mesh::c60`], which both lanes have already certified --
    /// the float lane and the integer judge agree on V, E, F and chi before a
    /// single face is refined.
    ///
    /// **HONEST BOUNDARY:** face *order* and each face's *starting corner* are
    /// this crate's, not the browser's. They agree on every count and on the
    /// geometry of each individual face, but a face-by-face hex diff against
    /// `GK.buildC60()` has not been run. That is step 6.
    pub fn seed_c60() -> State {
        let m = Mesh::c60();
        let mut faces = Vec::with_capacity(m.faces.len());
        let mut anchors = 0u32;
        for (i, f) in m.faces.iter().enumerate() {
            let kind = Kind::from_sides(f.len())
                .expect("the certified C60 has only pentagons and hexagons");
            let anchor = if kind == Kind::Pent {
                let a = format!("A{anchors}");
                anchors += 1;
                Some(a)
            } else {
                None
            };
            faces.push(Face {
                pts: f.iter().map(|&v| m.verts[v]).collect(),
                kind,
                level: 0,
                lineage: vec![i],
                id: format!("F{i}"),
                anchor,
            });
        }
        State {
            faces,
            history: Vec::new(),
            counter: 0,
        }
    }

    /// The census of this state, counted from the faces themselves.
    pub fn census(&self) -> Census {
        let p = self.faces.iter().filter(|f| f.kind == Kind::Pent).count() as u64;
        Census {
            f: self.faces.len() as u64,
            p,
        }
    }

    /// What [`grow`] predicts this state will become. Pure integers, computed
    /// **before** any allocation -- so a refinement that would not fit can be
    /// refused with the number rather than discovered by the allocator.
    pub fn predict(&self, op: Op) -> Result<Census, GrowthError> {
        grow(self.census(), op)
    }

    /// What this mesh really costs on the heap, field by field.
    ///
    /// **The old version of this counted the points and nothing else**, on the
    /// stated grounds that they "dominate everything else in a `Face`". They
    /// do not. Measured by `examples/kaboom`, which builds real meshes and
    /// walks them:
    ///
    /// ```text
    ///   depth   faces        pts only       real     ratio
    ///       1     212      142.6 B/f    286.8 B/f    2.01x
    ///       3   10292      144.0 B/f    321.3 B/f    2.23x
    ///       5  504212      144.0 B/f    379.7 B/f    2.64x
    ///       7  24.7M       144.0 B/f    445.4 B/f    3.09x
    /// ```
    ///
    /// And the error GROWS WITH DEPTH, which is the wrong direction for a
    /// number a budget is built on. `pts` is flat at 144 B/face forever --
    /// six points, always -- while `lineage` gains one `usize` per level and
    /// `id` gains a few characters per level (`F7.c33.e34.e35...`). At depth 7
    /// the ids alone are 2 GB.
    pub fn heap_bytes(&self) -> Bytes {
        let mut b = Bytes {
            faces: self.faces.len() as u64,
            inline: self.faces.len() as u64 * std::mem::size_of::<Face>() as u64,
            ..Default::default()
        };
        for f in &self.faces {
            b.pts += f.pts.capacity() as u64 * std::mem::size_of::<Vec3>() as u64;
            b.lineage += f.lineage.capacity() as u64 * std::mem::size_of::<usize>() as u64;
            b.ids += f.id.capacity() as u64;
            b.allocs += 3;
            if let Some(a) = &f.anchor {
                b.anchors += a.capacity() as u64;
                b.allocs += 1;
            }
        }
        b
    }

    /// Bytes one undo snapshot of the current face list would cost.
    ///
    /// A snapshot is a full `Vec<Face>` clone, so it clones the points, the
    /// lineage, the id and the anchor -- all of it. This now counts all of it.
    pub fn snapshot_bytes(&self) -> u64 {
        self.heap_bytes().total()
    }

    /// Peak heap while `refine` is running, which is what actually decides
    /// whether a step is possible.
    ///
    /// **`refine` holds BOTH generations at once**: `self.faces` is still
    /// alive while the new `Vec` is being filled, and it has to be -- the old
    /// faces are the input. So the peak is `old + new`, and since `Op::All`
    /// multiplies faces by about seven, that is roughly `8x` the current mesh.
    ///
    /// This is not theory. `kaboom` at depth 8 died asking for 6.1 GB while
    /// already holding 10.5 GB, on a machine with 14 GB free -- it never got
    /// close to the 84 GB the finished mesh would have needed, because it had
    /// to carry the old one the whole way.
    ///
    /// A budget that checks only the RESULT will therefore pass steps that
    /// cannot run.
    pub fn refine_peak_bytes(&self, op: Op) -> Option<u64> {
        let now = self.snapshot_bytes();
        let next = grow(self.census(), op).ok()?;
        let per_face = now.checked_div(self.faces.len().max(1) as u64)?;
        Some(now + next.f * per_face)
    }

    /// Refine every face the op touches. **Immutable** -- returns a new state
    /// and pushes the old face list onto history.
    ///
    /// ```
    /// use goldberg_kernel::genesis::{Op, Params, State};
    /// use goldberg_kernel::rng::Rng;
    ///
    /// let mut rng = Rng::new(0x5EED);
    /// let s = State::seed_c60();
    /// assert_eq!(s.faces.len(), 32);
    ///
    /// let t = s.refine(Op::All, &Params::default(), &mut rng);
    /// // the browser's own ladder: 32 -> 212, and P never moves
    /// assert_eq!(t.faces.len(), 212);
    /// assert_eq!(t.invariants().unwrap().pents, 12);
    /// // the seed is untouched -- immutability is the contract
    /// assert_eq!(s.faces.len(), 32);
    /// ```
    pub fn refine(&self, op: Op, p: &Params, rng: &mut Rng) -> State {
        let mut counter = self.counter;
        let mut faces = Vec::new();
        for f in &self.faces {
            let touched = match op {
                Op::All => true,
                Op::Hex => f.kind == Kind::Hex,
                Op::Pent => f.kind == Kind::Pent,
            };
            if touched {
                faces.extend(refine_face(f, p, &mut counter, rng));
            } else {
                faces.push(f.clone());
            }
        }
        let mut history = self.history.clone();
        history.push(Snapshot {
            step: Step::Refine(op),
            faces: self.faces.clone(),
        });
        State {
            faces,
            history,
            counter,
        }
    }

    /// Refine exactly one face. `None` if the index is past the end -- the
    /// browser silently returns the state unchanged; we say so in the type.
    pub fn refine_one(&self, idx: usize, p: &Params, rng: &mut Rng) -> Option<State> {
        let target = self.faces.get(idx)?;
        let mut counter = self.counter;
        let subs = refine_face(target, p, &mut counter, rng);
        let mut faces = Vec::with_capacity(self.faces.len() + subs.len() - 1);
        faces.extend_from_slice(&self.faces[..idx]);
        faces.extend(subs);
        faces.extend_from_slice(&self.faces[idx + 1..]);
        let mut history = self.history.clone();
        history.push(Snapshot {
            step: Step::One(idx),
            faces: self.faces.clone(),
        });
        Some(State {
            faces,
            history,
            counter,
        })
    }

    /// Step back one refinement. `None` at the seed.
    ///
    /// **The counter is NOT rolled back**, and that is the browser's own
    /// choice, stated in its own comment:
    ///
    /// ```text
    /// counter: state.counter // approximate; ids do not get reused
    /// ```
    ///
    /// Ported as written. An id minted on a branch that was undone is simply
    /// never minted again, which is the correct trade: monotone ids across a
    /// whole session beat a tidy counter.
    pub fn undo(&self) -> Option<State> {
        let mut history = self.history.clone();
        let snap = history.pop()?;
        Some(State {
            faces: snap.faces,
            history,
            counter: self.counter,
        })
    }

    /// Measure the shell. **This is R-INV, the requirement that matters most.**
    ///
    /// The browser reconstructs `V` two ways and picks:
    ///
    /// ```text
    /// edges    = round(faceEdgeSum / 2);
    /// vertices = edges - faces + 2;                  <- EULER ASSUMED
    /// if (hasHex) vertices = round(faceEdgeSum / 3); <- TRIVALENCE
    /// ```
    ///
    /// The first branch is a **tautology**: substituting `V = E - F + 2` into
    /// `chi = V - E + F` gives 2 for any input whatsoever, so on a hexagon-free
    /// seed -- the dodecahedron, the browser's `SEED 12` -- `chi = 2` is
    /// asserted rather than earned.
    ///
    /// **This port only ever uses trivalence.** `V` and `E` come from
    /// independent divisors of the same arity sum, `chi` is then computed, and
    /// it is allowed to come out wrong. A check that cannot fail is not a check.
    ///
    /// It also refuses instead of rounding: `round(x/2)` quietly accepts an odd
    /// sum, which is exactly how a torn mesh would pass unnoticed.
    pub fn invariants(&self) -> Result<Invariants, InvError> {
        let arity_sum: u64 = self.faces.iter().map(|f| f.pts.len() as u64).sum();
        if !arity_sum.is_multiple_of(2) {
            return Err(InvError::NotClosed { arity_sum });
        }
        if !arity_sum.is_multiple_of(3) {
            return Err(InvError::NotTrivalent { arity_sum });
        }
        let edges = arity_sum / 2;
        let vertices = arity_sum / 3;
        let faces = self.faces.len() as u64;
        let pents = self.faces.iter().filter(|f| f.kind == Kind::Pent).count() as u64;

        let mut anchors: Vec<&str> = self
            .faces
            .iter()
            .filter_map(|f| f.anchor.as_deref())
            .collect();
        anchors.sort_unstable();
        anchors.dedup();

        Ok(Invariants {
            faces,
            pents,
            hexes: faces - pents,
            edges,
            vertices,
            chi: vertices as i64 - edges as i64 + faces as i64,
            max_level: self.faces.iter().map(|f| f.level).max().unwrap_or(0),
            anchor_count: anchors.len(),
        })
    }
}

#[cfg(test)]
mod mesh_tests {
    use super::*;

    fn seed() -> (State, Params, Rng) {
        (State::seed_c60(), Params::default(), Rng::new(0x5EED))
    }

    /// The seed is the certified C60, and its anchors are the twelve.
    #[test]
    fn the_seed_is_the_certified_c60() {
        let s = State::seed_c60();
        let inv = s.invariants().expect("the C60 seed must measure");
        assert_eq!(inv.faces, 32);
        assert_eq!(inv.pents, 12);
        assert_eq!(inv.hexes, 20);
        assert_eq!(inv.vertices, 60);
        assert_eq!(inv.edges, 90);
        assert_eq!(inv.chi, 2);
        assert_eq!(inv.anchor_count, 12, "twelve distinct anchors at the seed");
        assert_eq!(inv.max_level, 0);
        // every pentagon carries one, every hexagon carries none
        assert!(s
            .faces
            .iter()
            .all(|f| (f.kind == Kind::Pent) == f.anchor.is_some()));
    }

    /// **The headline test of step 2.** The integer lane predicts, the geometry
    /// lane produces, and they must agree -- on every op, from every state.
    ///
    /// These are two genuinely independent derivations. `grow` is a closed-form
    /// census recurrence that never allocates a point; `refine` builds actual
    /// polygons and the invariants are then counted back off the arity sum. If
    /// the operator ever emits the wrong number of children, or the wrong
    /// arity, the census will not match.
    #[test]
    fn the_integer_lane_and_the_geometry_lane_agree() {
        let (mut s, p, mut rng) = seed();
        for op in [Op::All, Op::Hex, Op::Pent, Op::Hex, Op::Pent, Op::All] {
            let predicted = s.predict(op).expect("the census must price the step");
            s = s.refine(op, &p, &mut rng);
            let measured = s.invariants().expect("a refined shell must measure");
            assert_eq!(
                measured.faces,
                predicted.f,
                "op {} : census predicted F={} but the operator built {}",
                op.label(),
                predicted.f,
                measured.faces
            );
            assert_eq!(measured.pents, predicted.p, "op {}: P moved", op.label());
            assert_eq!(measured.chi, 2, "op {}: chi left the sphere", op.label());
            assert_eq!(
                measured.anchor_count,
                12,
                "op {}: an anchor was lost or minted",
                op.label()
            );
        }
    }

    /// The browser's logged ladder, built rather than counted.
    /// `32 -> 212 -> 1412`, with the real operator making real polygons.
    #[test]
    fn builds_the_browser_ladder_for_two_rungs() {
        let (mut s, p, mut rng) = seed();
        assert_eq!(s.faces.len(), 32);
        s = s.refine(Op::All, &p, &mut rng);
        assert_eq!(s.faces.len(), 212);
        s = s.refine(Op::Hex, &p, &mut rng);
        assert_eq!(s.faces.len(), 1412);
        let inv = s.invariants().unwrap();
        // matches TOPOLOGY_GATE's k1 row exactly: V=420 E=630 F=212 at 212,
        // and the next rung follows the same arithmetic
        assert_eq!((inv.vertices, inv.edges, inv.faces), (2820, 4230, 1412));
        assert_eq!(inv.chi, 2);
        assert_eq!(inv.pents, 12);
    }

    /// The pentagon branch -- the one the Python got wrong and never tested.
    /// `+60 = 5P` per step, exactly as the browser log says.
    #[test]
    fn the_pentagon_branch_adds_sixty_and_keeps_twelve() {
        let (mut s, p, mut rng) = seed();
        let before = s.faces.len();
        s = s.refine(Op::Pent, &p, &mut rng);
        assert_eq!(s.faces.len(), before + 60, "5s must add 5P = 60 faces");
        let inv = s.invariants().unwrap();
        assert_eq!(inv.pents, 12, "a pentagon refines to exactly one pentagon");
        assert_eq!(inv.anchor_count, 12);
        assert_eq!(inv.chi, 2);
    }

    /// Arity is preserved and the cells are always hexagons -- the two
    /// sentences, checked on one face of each kind.
    #[test]
    fn arity_is_preserved_and_every_cell_is_a_hexagon() {
        let (s, p, mut rng) = seed();
        let mut counter = 0u64;
        for kind in [Kind::Pent, Kind::Hex] {
            let parent = s.faces.iter().find(|f| f.kind == kind).unwrap();
            let kids = refine_face(parent, &p, &mut counter, &mut rng);
            assert_eq!(kids.len(), kind.sides() + 1, "{:?}: n+1 children", kind);
            assert_eq!(kids[0].kind, kind, "{:?}: the inner face keeps arity", kind);
            assert_eq!(kids[0].pts.len(), kind.sides());
            for cell in &kids[1..] {
                assert_eq!(cell.kind, Kind::Hex, "every surrounding cell is a hex");
                assert_eq!(cell.pts.len(), 6, "and it has six points");
            }
        }
    }

    /// A pentagon hands its anchor to its inner child and to nothing else.
    #[test]
    fn the_anchor_threads_through_the_inner_pentagon_only() {
        let (s, p, mut rng) = seed();
        let mut counter = 0u64;
        let parent = s.faces.iter().find(|f| f.kind == Kind::Pent).unwrap();
        let want = parent.anchor.clone().unwrap();
        let kids = refine_face(parent, &p, &mut counter, &mut rng);
        assert_eq!(kids[0].anchor.as_deref(), Some(want.as_str()));
        assert!(kids[1..].iter().all(|c| c.anchor.is_none()));
    }

    /// Ids are minted once, never reused, and carry the parent in the name.
    #[test]
    fn ids_are_unique_and_carry_their_lineage() {
        let (mut s, p, mut rng) = seed();
        s = s.refine(Op::All, &p, &mut rng);
        s = s.refine(Op::Hex, &p, &mut rng);
        let mut ids: Vec<&str> = s.faces.iter().map(|f| f.id.as_str()).collect();
        let total = ids.len();
        ids.sort_unstable();
        ids.dedup();
        assert_eq!(ids.len(), total, "every face id must be distinct");
        // lineage depth tracks level, always
        assert!(s
            .faces
            .iter()
            .all(|f| f.lineage.len() == f.level as usize + 1));
    }

    /// Immutability, and the undo it buys.
    #[test]
    fn refinement_is_immutable_and_undo_returns_the_exact_faces() {
        let (s0, p, mut rng) = seed();
        let s1 = s0.refine(Op::All, &p, &mut rng);
        let s2 = s1.refine(Op::Pent, &p, &mut rng);

        // nothing upstream moved
        assert_eq!(s0.faces.len(), 32);
        assert_eq!(s1.faces.len(), 212);
        assert_eq!(s2.faces.len(), 272);

        // undo restores the previous faces exactly -- not approximately
        let back1 = s2.undo().expect("one step back");
        assert_eq!(back1.faces, s1.faces, "undo must restore the faces bitwise");
        let back0 = back1.undo().expect("two steps back");
        assert_eq!(back0.faces, s0.faces);
        assert!(back0.undo().is_none(), "the seed has nothing behind it");

        // and the counter does NOT roll back -- the browser's own choice
        assert_eq!(back1.counter, s2.counter);
        assert!(s2.counter > s1.counter);
    }

    /// `refine_one` touches one face and leaves its neighbours alone.
    #[test]
    fn refine_one_replaces_exactly_one_face_in_place() {
        let (s, p, mut rng) = seed();
        let idx = 7;
        let victim = s.faces[idx].clone();
        let t = s.refine_one(idx, &p, &mut rng).expect("index 7 exists");
        assert_eq!(t.faces.len(), s.faces.len() + victim.pts.len());
        // the faces before and after the splice are untouched
        assert_eq!(t.faces[..idx], s.faces[..idx]);
        let tail = t.faces.len() - (s.faces.len() - idx - 1);
        assert_eq!(t.faces[tail..], s.faces[idx + 1..]);
        assert!(s.refine_one(9_999, &p, &mut rng).is_none());
    }

    /// **The check must be able to fail.** Feed `invariants` a soup that is not
    /// a closed trivalent shell and it must refuse, not print 2.
    ///
    /// This is the whole point of R-INV. The browser's no-hex branch derives
    /// `V = E - F + 2` and then computes `chi = V - E + F`, which is 2 for any
    /// input at all. Ours derives V and E from independent divisors, so a torn
    /// soup has nowhere to hide.
    #[test]
    fn invariants_can_say_something_other_than_two() {
        let mut s = State::seed_c60();

        // tear one corner off one face: arity sum 180 -> 179, odd
        s.faces[0].pts.pop();
        match s.invariants() {
            Err(InvError::NotClosed { arity_sum }) => assert_eq!(arity_sum, 179),
            other => panic!("a torn soup must refuse, got {other:?}"),
        }

        // a soup that is closed but not trivalent: two quadrilaterals,
        // arity sum 8 -- even, so it passes the closure gate, and 8 % 3 != 0
        let quad = Face {
            pts: vec![[0.0, 0.0, 0.0]; 4],
            kind: Kind::Hex,
            level: 0,
            lineage: vec![0],
            id: "Q".into(),
            anchor: None,
        };
        let odd = State {
            faces: vec![quad.clone(), quad],
            history: Vec::new(),
            counter: 0,
        };
        match odd.invariants() {
            Err(InvError::NotTrivalent { arity_sum }) => assert_eq!(arity_sum, 8),
            other => panic!("a non-trivalent soup must refuse, got {other:?}"),
        }
    }

    /// A hexagon-free seed -- the browser's `SEED 12`, where its own `chi`
    /// becomes a tautology. Ours stays a measurement and still lands on 2.
    #[test]
    fn the_dodecahedron_earns_chi_two_instead_of_assuming_it() {
        let pent = |id: &str, a: &str| Face {
            pts: vec![[0.0, 0.0, 0.0]; 5],
            kind: Kind::Pent,
            level: 0,
            lineage: vec![0],
            id: id.into(),
            anchor: Some(a.into()),
        };
        let faces: Vec<Face> = (0..12)
            .map(|i| pent(&format!("F{i}"), &format!("A{i}")))
            .collect();
        let s = State {
            faces,
            history: Vec::new(),
            counter: 0,
        };
        let inv = s
            .invariants()
            .expect("12 pentagons is a closed trivalent shell");
        // arity sum 60 -> V=20, E=30, F=12. Both divisors independent.
        assert_eq!((inv.vertices, inv.edges, inv.faces), (20, 30, 12));
        assert_eq!(inv.chi, 2, "and it is COUNTED, not substituted");
        assert_eq!(inv.pents, 12);
        assert_eq!(inv.anchor_count, 12);
    }

    /// The default path never touches the RNG, which is what keeps it
    /// bit-identical to the browser. Two refinements from two different seeds
    /// must produce the same points.
    #[test]
    fn the_default_path_does_not_consult_the_rng() {
        let s = State::seed_c60();
        let p = Params::default();
        let a = s.refine(Op::All, &p, &mut Rng::new(1));
        let b = s.refine(Op::All, &p, &mut Rng::new(0xDEAD_BEEF));
        assert_eq!(a.faces, b.faces, "jitter=0 must ignore the seed entirely");
    }

    /// Jitter is reproducible here even though it is not the browser's stream,
    /// and it touches `inner` and `midRing` while leaving the shared corners
    /// exactly where they were. Jittering those would tear the mesh.
    #[test]
    fn jitter_is_reproducible_and_never_moves_a_shared_corner() {
        let s = State::seed_c60();
        let p = Params {
            jitter: 0.05,
            ..Params::default()
        };
        let a = s.refine(Op::All, &p, &mut Rng::new(0x5EED));
        let b = s.refine(Op::All, &p, &mut Rng::new(0x5EED));
        assert_eq!(a.faces, b.faces, "same seed, same mesh -- no Math.random");

        let c = s.refine(Op::All, &p, &mut Rng::new(0x5EEE));
        assert_ne!(a.faces, c.faces, "a different seed must move the points");

        // in every cell, pts[0] and pts[2] are the parent's own corners and
        // pts[1] is the edge midpoint. None of the three may be jittered.
        let mut counter = 0u64;
        let mut rng = Rng::new(0x5EED);
        let parent = &s.faces[0];
        let kids = refine_face(parent, &p, &mut counter, &mut rng);
        let n = parent.pts.len();
        for (i, cell) in kids[1..].iter().enumerate() {
            let j = (i + 1) % n;
            assert_eq!(cell.pts[0], parent.pts[i], "cell {i}: corner i moved");
            assert_eq!(cell.pts[2], parent.pts[j], "cell {i}: corner j moved");
            assert_eq!(
                cell.pts[1],
                vlerp(parent.pts[i], parent.pts[j], 0.5),
                "cell {i}: the shared edge midpoint moved"
            );
        }
    }

    /// The price is stated before it is paid (Curse 35) -- and the price is
    /// the WHOLE face, not the points.
    ///
    /// This test used to assert `snapshot_bytes() == 180 * 24`, pinning a
    /// points-only model that was wrong by 1.88x at the seed and 3.09x at
    /// depth 7. It failed the moment the model was fixed, which is precisely
    /// what a test pinning a wrong number is for.
    #[test]
    fn the_snapshot_cost_counts_the_whole_face() {
        let (mut s, p, mut rng) = seed();
        let b = s.heap_bytes();

        // 12 pentagons + 20 hexagons = 180 points, and that part IS structural
        assert_eq!(b.pts, 180 * 24, "six points a hexagon, five a pentagon");
        assert_eq!(b.faces, 32);

        // ...and it is not most of the cost, even at the shallowest depth
        assert!(b.pts < b.total(), "points {} vs total {}", b.pts, b.total());
        assert_eq!(b.inline, 32 * std::mem::size_of::<Face>() as u64);
        assert!(b.anchors > 0, "twelve pentagons carry twelve anchors");
        assert_eq!(b.allocs, 32 * 3 + 12, "three per face, plus one per anchor");
        assert_eq!(s.snapshot_bytes(), b.total());

        s = s.refine(Op::All, &p, &mut rng);
        let after = s.heap_bytes();
        assert_eq!(after.faces, 212);
        assert_eq!(after.pts, 1260 * 24);
        assert_eq!(s.invariants().unwrap().edges, 630);
        assert!(
            after.total() > b.total() * 6,
            "seven times the faces costs at least six times the bytes"
        );
    }

    /// The operator refuses a census Euler forbids rather than building it.
    #[test]
    fn a_census_without_twelve_pentagons_is_refused() {
        let bad = Census { f: 32, p: 11 };
        assert!(matches!(
            grow(bad, Op::All),
            Err(GrowthError::Impossible(_))
        ));
    }
}

#[cfg(test)]
mod cost_tests {
    use super::*;

    fn built(depth: u32) -> State {
        let p = Params::default();
        let mut rng = Rng::new(0x5EED);
        let mut s = State::seed_c60();
        for _ in 0..depth {
            s = s.refine(Op::All, &p, &mut rng);
            s.history.clear();
        }
        s
    }

    /// **The points do not dominate.** The old `snapshot_bytes` said they did
    /// and every memory number printed anywhere was built on that.
    #[test]
    fn the_points_are_less_than_half_the_cost() {
        let s = built(3);
        let b = s.heap_bytes();
        assert_eq!(b.faces, 10292);
        assert!(
            b.pts < b.total() / 2,
            "points are {} of {} -- if this ever becomes true again, a Face got smaller \
             and the doc needs rewriting, not the test",
            b.pts,
            b.total()
        );
        // measured by examples/kaboom at this exact depth
        assert!(
            (b.per_face() - 321.3).abs() < 1.0,
            "per-face cost moved: {:.1}, was 321.3",
            b.per_face()
        );
    }

    /// `pts` is flat forever and the rest is not, so the error in a
    /// points-only model GROWS with depth. That direction is the whole problem.
    #[test]
    fn the_points_only_model_gets_worse_with_depth() {
        let shallow = built(1).heap_bytes();
        let deeper = built(4).heap_bytes();

        let r1 = shallow.total() as f64 / shallow.pts as f64;
        let r4 = deeper.total() as f64 / deeper.pts as f64;

        // pts per face is SIX POINTS, always -- that is why it cannot track
        assert!((shallow.pts as f64 / shallow.faces as f64 - 144.0).abs() < 2.0);
        assert!((deeper.pts as f64 / deeper.faces as f64 - 144.0).abs() < 0.5);

        assert!(
            r4 > r1,
            "the ratio must worsen with depth: depth1 {r1:.2}x, depth4 {r4:.2}x"
        );
        assert!(
            r4 > 2.3,
            "at depth 4 the real cost was measured at 2.43x the points, got {r4:.2}x"
        );
    }

    /// The ids really are the thing that grows. At depth 7 they are 2 GB.
    #[test]
    fn ids_and_lineage_grow_while_points_do_not() {
        let a = built(2).heap_bytes();
        let b = built(4).heap_bytes();
        let per = |x: u64, f: u64| x as f64 / f as f64;
        assert!(
            per(b.ids, b.faces) > per(a.ids, a.faces),
            "id bytes per face must grow with depth"
        );
        assert!(
            per(b.lineage, b.faces) > per(a.lineage, a.faces),
            "lineage bytes per face must grow with depth"
        );
    }

    /// **What actually decides whether a step can run.** `refine` keeps the
    /// old generation alive while building the new one, so the peak is
    /// `old + new` -- about 8x the current mesh for `Op::All`. A budget that
    /// checks only the result would pass steps that cannot run.
    #[test]
    fn the_peak_is_both_generations_not_just_the_result() {
        let s = built(2);
        let now = s.snapshot_bytes();
        let peak = s.refine_peak_bytes(Op::All).expect("C60 can always grow");
        assert!(peak > now, "the peak must exceed what is already held");
        let ratio = peak as f64 / now as f64;
        assert!(
            (7.0..9.5).contains(&ratio),
            "Op::All is ~7x faces, so the peak should be ~8x the mesh, got {ratio:.2}x"
        );
    }

    /// Twelve anchors, however deep it goes -- so that field never grows.
    #[test]
    fn the_anchors_do_not_grow() {
        let a = built(1).heap_bytes();
        let b = built(4).heap_bytes();
        assert_eq!(a.anchors, b.anchors, "twelve anchors, forever");
    }
}
