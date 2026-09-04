//! `weld` -- turn the face soup back into a graph, keyed on the BITS.
//!
//! # WHAT THIS CLOSES
//!
//! [`crate::genesis`] builds **face soup**: every face owns its own copy of
//! every corner, and no index survives. [`crate::judge`] wants a **rotation
//! system** -- a permutation over *indexed* vertices. So the port has had an
//! honest builder and an honest judge since v0.1 and no way to introduce them,
//! which is the R13-R16 pattern at the scale of a project: two correct
//! instruments and no correspondence between them.
//!
//! This is the introduction. Step 6 of `GENESIS_PORT_SPEC.md`.
//!
//! # WHY THE KEY IS BITS AND NOT A DISTANCE
//!
//! [`crate::sphere`] welds by **sorted index pair**, exactly, because its
//! subdivision never loses the indices. Genesis cannot copy that -- it has no
//! indices to sort. The obvious substitute is a distance threshold, and RUSTIUM
//! **R7 measured that lane dying at C380**: the edge-length spread outgrew the
//! tolerance, so a weld that worked at C60 silently fused distinct vertices
//! deeper down.
//!
//! There is a better key. A shared corner is computed independently by each
//! face that owns it -- and IEEE-754 is deterministic: **the same expression on
//! the same inputs returns the same 64 bits, every time, on every conforming
//! machine.** So two faces that agree about a corner agree about it *exactly*,
//! and the key can be the bits themselves:
//!
//! ```text
//!   key = ( x.to_bits(), y.to_bits(), z.to_bits() )
//! ```
//!
//! No tolerance to outgrow, no quantisation to drift, nothing for depth to
//! erode. The weld is a hash on the 1s and 0s.
//!
//! # BOTH ANSWERS ARE WORTH HAVING
//!
//! ```text
//!   V_welded == arity_sum / 3    the soup is consistent -- hand it to judge
//!   V_welded >  arity_sum / 3    some shared corner is reached by two
//!                                different EXPRESSIONS, and the bits found it
//! ```
//!
//! The second is a real defect in `refine_face` that **no census could ever
//! see**, because a census counts faces and both copies are faces. That is the
//! reason to run this rather than a risk in running it.
//!
//! # LANE
//!
//! **CERTIFIED.** Nothing here computes a coordinate. It reads the bits that
//! are already there, compares them for equality, and counts. No arithmetic on
//! a float happens in this module at all -- which is what lets a bit key be
//! honest, and is also why the one normalisation below is worth its comment.

use crate::genesis::State;
use crate::judge::{self, Refusal, Verdict};
use crate::Vec3;
use std::collections::HashMap;

/// The 192-bit identity of a point: three `f64` patterns, verbatim.
pub type Key = [u64; 3];

/// The key of a point.
///
/// **The one normalisation, and it is not a tolerance.** `-0.0` and `+0.0` are
/// equal as numbers and *differ in every bit of the sign*, so a face that
/// arrived at a corner by subtraction and one that arrived by multiplication
/// could hold the same point under two keys. `x == 0.0` is true for both
/// zeroes, so this maps `-0.0` onto `+0.0` and touches nothing else.
///
/// A `NaN` coordinate is left exactly as it is. `NaN != NaN` in arithmetic, but
/// this is a hash on bits, so two identical NaN patterns weld and two different
/// ones do not -- which is the correct behaviour for a key and would be a
/// silent lie for a comparison. A shell containing one is broken either way,
/// and [`Weld::judge`] will say so rather than paper over it.
#[inline]
pub fn key(p: Vec3) -> Key {
    let z = |x: f64| if x == 0.0 { 0.0f64 } else { x };
    [z(p[0]).to_bits(), z(p[1]).to_bits(), z(p[2]).to_bits()]
}

/// A soup, welded: distinct points and the faces as index cycles.
#[derive(Clone, Debug)]
pub struct Weld {
    /// one entry per distinct bit pattern, in first-seen order
    pub verts: Vec<Vec3>,
    /// each face as a cycle of indices into [`Weld::verts`]
    pub faces: Vec<Vec<usize>>,
    /// total corners read -- the arity sum, and the soup's own size
    pub corners: usize,
}

impl Weld {
    /// Distinct points found.
    pub fn v(&self) -> usize {
        self.verts.len()
    }

    /// Faces, unchanged by welding -- a weld moves no face.
    pub fn f(&self) -> usize {
        self.faces.len()
    }

    /// What trivalence *predicts* the vertex count to be.
    ///
    /// Three faces meet at every vertex of a Goldberg polyhedron, so the sum of
    /// face arities counts each vertex exactly three times. This is the number
    /// [`crate::genesis::State::invariants`] reports, computed without ever
    /// looking at a coordinate -- so comparing it against [`Weld::v`] compares
    /// two genuinely independent routes to the same integer.
    pub fn predicted_v(&self) -> usize {
        self.corners / 3
    }

    /// Did the bits agree with the arithmetic?
    pub fn consistent(&self) -> bool {
        self.corners.is_multiple_of(3) && self.v() == self.predicted_v()
    }

    /// How many more distinct points than trivalence allows.
    ///
    /// Zero when the soup is consistent. Positive means some corner was reached
    /// by two different expressions; it cannot go negative, because welding can
    /// only ever merge.
    pub fn surplus(&self) -> i64 {
        self.v() as i64 - self.predicted_v() as i64
    }

    /// The rotation system, if these faces form a closed orientable surface.
    pub fn rotation(&self) -> Option<Vec<usize>> {
        judge::rotation_from_faces(&self.faces)
    }

    /// **The introduction.** Hand the welded soup to the judge.
    ///
    /// This is the sentence the port could not say before: not *"the census
    /// counted 32 faces"* and not *"the judge accepts some rotation system"*,
    /// but *"the mesh genesis actually built closes, and here is its chi,
    /// counted from orbits of a permutation"*.
    pub fn judge(&self) -> Result<Verdict, WeldError> {
        let sigma = self.rotation().ok_or(WeldError::NotASurface)?;
        judge::check(&sigma).map_err(WeldError::Refused)
    }
}

/// Why a welded soup could not be judged.
#[derive(Clone, Debug, PartialEq)]
pub enum WeldError {
    /// a directed edge was used twice, or some edge had no twin -- the faces
    /// do not form a closed orientable surface, so there is no rotation system
    /// to check
    NotASurface,
    /// there was a rotation system and the judge refused it
    Refused(Refusal),
}

impl std::fmt::Display for WeldError {
    fn fmt(&self, w: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            WeldError::NotASurface => write!(
                w,
                "the welded faces are not a closed orientable surface: some directed edge \
                 is used twice or has no twin. A duplicated vertex does this -- the two \
                 copies each take half the edges"
            ),
            WeldError::Refused(r) => write!(w, "the judge refused: {r}"),
        }
    }
}

impl std::error::Error for WeldError {}

/// Weld a genesis soup on its bits.
///
/// One pass, one hash lookup per corner. First-seen order, so the result is
/// deterministic for a deterministic soup and two runs produce identical
/// indices.
pub fn weld(st: &State) -> Weld {
    let corners: usize = st.faces.iter().map(|f| f.pts.len()).sum();
    let mut index: HashMap<Key, usize> = HashMap::with_capacity(corners / 2);
    let mut verts: Vec<Vec3> = Vec::with_capacity(corners / 3);
    let mut faces: Vec<Vec<usize>> = Vec::with_capacity(st.faces.len());

    for f in &st.faces {
        let mut cycle = Vec::with_capacity(f.pts.len());
        for &p in &f.pts {
            let k = key(p);
            let i = *index.entry(k).or_insert_with(|| {
                verts.push(p);
                verts.len() - 1
            });
            cycle.push(i);
        }
        faces.push(cycle);
    }

    Weld {
        verts,
        faces,
        corners,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::genesis::{Op, Params, Surface};
    use crate::rng::Rng;

    fn refined(levels: u32) -> State {
        let p = Params {
            surface: Surface::Spherical,
            ..Params::default()
        };
        let mut rng = Rng::new(0xC60);
        let mut st = State::seed_c60();
        for _ in 0..levels {
            st = st.refine(Op::All, &p, &mut rng);
        }
        st
    }

    /// **The sentence step 6 existed to make.**
    ///
    /// Not "the census counted 32 faces" and not "the judge accepts some
    /// rotation system", but: the mesh genesis actually built closes, and its
    /// chi is 2 counted from ORBITS OF A PERMUTATION -- a route that shares no
    /// code with the arity sum.
    #[test]
    fn the_seed_welds_and_the_judge_agrees() {
        let st = State::seed_c60();
        let w = weld(&st);
        let inv = st.invariants().expect("the seed measures");

        assert_eq!(w.v(), 60, "the C60 has 60 distinct corners");
        assert_eq!(w.surplus(), 0, "no corner is reached by two expressions");
        assert_eq!(
            w.v() as u64,
            inv.vertices,
            "the bits and the arity sum agree"
        );

        let v = w.judge().expect("the seed is a closed orientable surface");
        assert_eq!((v.v, v.e, v.f, v.chi), (60, 90, 32, 2));
        assert_eq!(v.components, 1);
        assert_eq!(v.genus, Some(0));
    }

    /// **What step 6 actually found, locked so it cannot change in silence.**
    ///
    /// One refinement and the soup stops being a surface -- not by a rounding,
    /// but structurally. Measured at level 1, and every number here was read
    /// off the mesh rather than derived:
    ///
    /// ```text
    ///   degree 1   180 points   mid_ring[i], pulled toward its OWN centroid
    ///   degree 2    90 points   the raw edge midpoint, genuinely shared
    ///   degree 3   180 points   inner[i], in the inner face and two cells
    ///   degree 6    60 points   the original C60 corners
    /// ```
    ///
    /// `invariants()` divides the arity sum by three because a Goldberg
    /// polyhedron is trivalent. **This mesh is not**, so that division is a
    /// prediction the geometry does not satisfy -- and nothing had ever
    /// checked, because a census counts faces and every one of these points
    /// sits on a face.
    ///
    /// The 180 degree-one points are the crescent: `README.md` says the gap
    /// between the inner ring and the mid ring *"is not a bug to fix, it is
    /// the picture"*. This test does not argue with that. It records that the
    /// picture and a closed surface are different objects, so that no later
    /// claim can quietly assume otherwise.
    #[test]
    fn one_refinement_leaves_the_surface_category() {
        let st = refined(1);
        let w = weld(&st);

        assert_eq!(w.v(), 510, "510 genuinely distinct points");
        assert_eq!(w.predicted_v(), 420, "trivalence predicts 420");
        assert_eq!(w.surplus(), 90);

        let mut deg = vec![0usize; w.v()];
        for f in &w.faces {
            for &i in f {
                deg[i] += 1;
            }
        }
        let count = |d: usize| deg.iter().filter(|&&x| x == d).count();
        assert_eq!((count(1), count(2), count(3), count(6)), (180, 90, 180, 60));
        assert_eq!(
            deg.iter().sum::<usize>(),
            w.corners,
            "incidences are the arity sum"
        );

        // and therefore the judge must refuse -- a degree-one point leaves a
        // directed edge with no twin
        assert_eq!(w.judge().unwrap_err(), WeldError::NotASurface);
    }

    /// The surplus is STRUCTURE, not rounding, and the distance says so.
    ///
    /// This is the test that decides which bug we have. If the extra points
    /// were the same point reached by two expressions they would sit an ULP
    /// apart; the closest pair in the whole level-1 mesh is 0.1334 away, which
    /// is most of an edge. There is no float defect here to fix.
    #[test]
    fn the_surplus_is_not_a_rounding_error() {
        let w = weld(&refined(1));
        let mut closest = f64::INFINITY;
        for i in 0..w.v() {
            for j in (i + 1)..w.v() {
                let (a, b) = (w.verts[i], w.verts[j]);
                let d =
                    ((a[0] - b[0]).powi(2) + (a[1] - b[1]).powi(2) + (a[2] - b[2]).powi(2)).sqrt();
                if d < closest {
                    closest = d;
                }
            }
        }
        assert!(
            closest > 0.1,
            "closest pair is {closest}, which is ULP-scale -- that would be two \
             expressions for one point, a different bug with a different fix"
        );
    }

    /// `-0.0` and `+0.0` are equal and share no sign bit.
    #[test]
    fn negative_zero_welds_onto_positive_zero() {
        assert_eq!(key([-0.0, 1.0, -0.0]), key([0.0, 1.0, 0.0]));
        assert_ne!(key([0.0, 1.0, 0.0]), key([0.0, 1.0, f64::MIN_POSITIVE]));
    }

    /// A weld moves no face and invents no face.
    #[test]
    fn welding_preserves_every_face_and_its_arity() {
        let st = refined(2);
        let w = weld(&st);
        assert_eq!(w.f(), st.faces.len());
        for (a, b) in w.faces.iter().zip(st.faces.iter()) {
            assert_eq!(a.len(), b.pts.len());
        }
    }

    /// First-seen order, so two welds of one soup are the same weld.
    #[test]
    fn welding_is_deterministic() {
        let st = refined(1);
        let (a, b) = (weld(&st), weld(&st));
        assert_eq!(a.faces, b.faces);
        assert_eq!(a.verts.len(), b.verts.len());
    }
}
