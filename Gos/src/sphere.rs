//! THE ICOSPHERE LANE -- exact index subdivision, one face per byte.
//!
//! Ported from `shell/byte_sphere.html`, whose `subdivide()` does the one thing
//! `crate::build_edges` does not: it welds midpoints by an **index map**, never
//! by a distance.
//!
//! ```js
//! const m=(a,b)=>{const k=a<b?a+'_'+b:b+'_'+a;
//!                 if(mid[k]!==undefined)return mid[k]; ... }
//! ```
//!
//! That key is a pair of integers. Two triangles sharing an edge ask for the
//! same key and receive the same vertex, so the weld is **combinatorially
//! exact at every depth**. RUSTIUM curse R7 measured the float-threshold lane
//! dying at C380 because the edge-length spread outgrew the tolerance; there is
//! no tolerance here to outgrow. This lane subdivides as far as memory allows.
//!
//! # The counts are exact integers
//!
//! ```text
//!   F = 20 * 4^L      V = 10 * 4^L + 2      E = 30 * 4^L
//!   chi = V - E + F = 10*4^L + 2 - 30*4^L + 20*4^L = 2      identically
//! ```
//!
//! **And that identity is exactly why `byte_sphere`'s HUD cannot be trusted.**
//! It prints `chi:2` as a literal, and the formula above returns 2 for every L
//! whether or not a mesh was ever built -- so a duplicated vertex or an unwelded
//! seam would still read `chi = 2` in green (Curse 26). Here the counts are
//! predicted from the formula and then **the built mesh is handed to
//! [`crate::judge`]**, which counts orbits of a permutation and can say
//! something other than 2.
//!
//! # Triangles, and where the twelve pentagons went
//!
//! This lane is a **triangulation**: almost every vertex has degree 6, and
//! exactly twelve have degree 5 -- the 12 original icosahedron corners, forced
//! by Euler at every depth. Those twelve are the twelve pentagons **of the
//! dual**. `byte_sphere` calls them "the 12 pentagons" and marks them pink; that
//! is the dual statement of the same constraint, and it is honest as long as
//! nobody claims a triangle is a pentagon. The trivalent Goldberg lane
//! ([`crate::Mesh`]) carries pentagons as FACES.

use std::collections::HashMap;

use crate::{vnorm, Vec3, PHI};

/// Faces past which we refuse to allocate.
///
/// Curse 35: growth is **4x per level**, which crosses from instant to fatal in
/// two clicks. The recurrence is known exactly, so the bill is predictable and
/// [`Ico::level`] refuses out loud with the number rather than OOM-ing.
pub const FACE_BUDGET: usize = 6_000_000;

/// A triangulated sphere. Vertices on the unit sphere, faces as index triples.
#[derive(Clone, Debug)]
pub struct Ico {
    pub verts: Vec<Vec3>,
    pub faces: Vec<[usize; 3]>,
    /// how many subdivisions produced this mesh
    pub level: u32,
}

/// Why a refinement was refused. Loud, with the number (Curse 35 / K4).
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct TooBig {
    pub level: u32,
    pub predicted_faces: usize,
    pub budget: usize,
}

impl std::fmt::Display for TooBig {
    fn fmt(&self, w: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            w,
            "HALT: level {} = {} faces > budget {}. The math is fine past here; \
             the MACHINE is what ends.",
            self.level, self.predicted_faces, self.budget
        )
    }
}

impl std::error::Error for TooBig {}

/// `F = 20 * 4^L`, `V = 10 * 4^L + 2`, `E = 30 * 4^L`. EXACT, integers.
///
/// Returns `None` on overflow rather than wrapping -- R3's lesson: a bound
/// implemented as `checked_*` is true by construction.
pub fn counts(level: u32) -> Option<(usize, usize, usize)> {
    let q = 4usize.checked_pow(level)?;
    let f = 20usize.checked_mul(q)?;
    let v = 10usize.checked_mul(q)?.checked_add(2)?;
    let e = 30usize.checked_mul(q)?;
    Some((v, e, f))
}

/// `chi` from the formula alone. Always 2 -- which is the point of the warning
/// in this module's docs, not a certification.
pub fn formula_chi(level: u32) -> Option<i64> {
    let (v, e, f) = counts(level)?;
    Some(v as i64 - e as i64 + f as i64)
}

/// The smallest level whose face count can hold `n` bytes at one byte per face.
///
/// `byte_sphere` reaches one-byte-per-face at L5 for a 24 KB sample; a 541 KB
/// binary needs L8.
pub fn level_for_bytes(n: usize) -> u32 {
    let mut l = 0u32;
    while let Some((_, _, f)) = counts(l) {
        if f >= n || f >= FACE_BUDGET {
            return l;
        }
        l += 1;
    }
    l
}

impl Ico {
    /// The icosahedron: 12 vertices, 20 faces, in `byte_sphere`'s own order so
    /// "the twelve" mean the same twelve in both programs.
    pub fn base() -> Ico {
        let p = PHI;
        let raw: [[f64; 3]; 12] = [
            [-1.0, p, 0.0],
            [1.0, p, 0.0],
            [-1.0, -p, 0.0],
            [1.0, -p, 0.0],
            [0.0, -1.0, p],
            [0.0, 1.0, p],
            [0.0, -1.0, -p],
            [0.0, 1.0, -p],
            [p, 0.0, -1.0],
            [p, 0.0, 1.0],
            [-p, 0.0, -1.0],
            [-p, 0.0, 1.0],
        ];
        #[rustfmt::skip]
        let faces: [[usize; 3]; 20] = [
            [0,11,5],[0,5,1],[0,1,7],[0,7,10],[0,10,11],
            [1,5,9],[5,11,4],[11,10,2],[10,7,6],[7,1,8],
            [3,9,4],[3,4,2],[3,2,6],[3,6,8],[3,8,9],
            [4,9,5],[2,4,11],[6,2,10],[8,6,7],[9,8,1],
        ];
        let verts: Vec<Vec3> = raw.iter().map(|v| vnorm(*v)).collect();

        // Orient every face OUTWARD before anything else.
        //
        // byte_sphere's raw list is not consistently wound -- it fixes the
        // winding later, per frame, inside `faceData()` for backface culling.
        // That is fine for drawing and fatal for the judge: a rotation system
        // needs each DIRECTED edge to appear exactly once, which only holds on a
        // consistently oriented surface. Orientability is precisely what makes
        // chi=2 mean anything, so it is fixed here, once, at the source.
        let faces = faces
            .iter()
            .map(|f| {
                let (a, b, c) = (verts[f[0]], verts[f[1]], verts[f[2]]);
                let n = crate::vcross(crate::vsub(b, a), crate::vsub(c, a));
                let out = [a[0] + b[0] + c[0], a[1] + b[1] + c[1], a[2] + b[2] + c[2]];
                if crate::vdot(n, out) > 0.0 {
                    *f
                } else {
                    [f[0], f[2], f[1]]
                }
            })
            .collect();

        Ico {
            verts,
            faces,
            level: 0,
        }
    }

    /// One subdivision: every triangle becomes four.
    ///
    /// The midpoint of edge `(a,b)` is keyed by the **sorted index pair**, so
    /// both triangles sharing that edge get the identical vertex. No distance,
    /// no tolerance, no quantisation key -- the weld cannot drift with depth.
    pub fn subdivide(&mut self) {
        let mut mid: HashMap<(usize, usize), usize> = HashMap::with_capacity(self.faces.len() * 3);
        let mut out: Vec<[usize; 3]> = Vec::with_capacity(self.faces.len() * 4);

        // borrow dance: collect the new vertices, then extend
        let mut verts = std::mem::take(&mut self.verts);
        let mut m = |a: usize, b: usize, verts: &mut Vec<Vec3>| -> usize {
            let k = if a < b { (a, b) } else { (b, a) };
            if let Some(&i) = mid.get(&k) {
                return i;
            }
            let (va, vb) = (verts[a], verts[b]);
            verts.push(vnorm([
                (va[0] + vb[0]) / 2.0,
                (va[1] + vb[1]) / 2.0,
                (va[2] + vb[2]) / 2.0,
            ]));
            let i = verts.len() - 1;
            mid.insert(k, i);
            i
        };

        for &[a, b, c] in &self.faces {
            let ab = m(a, b, &mut verts);
            let bc = m(b, c, &mut verts);
            let ca = m(c, a, &mut verts);
            out.push([a, ab, ca]);
            out.push([ab, b, bc]);
            out.push([ca, bc, c]);
            out.push([ab, bc, ca]);
        }
        self.verts = verts;
        self.faces = out;
        self.level += 1;
    }

    /// Build to `level`, predicting the bill before every allocation.
    pub fn level(level: u32) -> Result<Ico, TooBig> {
        let mut ico = Ico::base();
        for l in 1..=level {
            let predicted = counts(l).map(|(_, _, f)| f).unwrap_or(usize::MAX);
            if predicted > FACE_BUDGET {
                return Err(TooBig {
                    level: l,
                    predicted_faces: predicted,
                    budget: FACE_BUDGET,
                });
            }
            ico.subdivide();
        }
        Ok(ico)
    }

    /// The twelve degree-5 vertices -- the original icosahedron corners, and the
    /// twelve pentagons of the dual. Euler forces exactly twelve at every depth.
    pub fn defects(&self) -> Vec<usize> {
        let mut deg = vec![0usize; self.verts.len()];
        for f in &self.faces {
            for &v in f {
                deg[v] += 1;
            }
        }
        (0..self.verts.len()).filter(|&i| deg[i] == 5).collect()
    }

    /// A rotation system for [`crate::judge::check`], built from the oriented
    /// faces. Lets the integer judge COUNT chi on the refined mesh instead of
    /// reciting the formula.
    pub fn rotation_system(&self) -> Option<Vec<usize>> {
        let cycles: Vec<Vec<usize>> = self.faces.iter().map(|f| f.to_vec()).collect();
        crate::judge::rotation_from_faces(&cycles)
    }

    /// Faces in spherical-Hilbert order, so consecutive bytes land on
    /// neighbouring faces. `byte_sphere`'s `curveKey`, ported.
    ///
    /// DISPLAY lane: the key uses division and `floor`, and its purpose is an
    /// ORDERING, not a value. The order is stable because the candidates are far
    /// apart on a valid mesh.
    pub fn curve_order(&self) -> Vec<usize> {
        let mut keyed: Vec<(u64, usize)> = self
            .faces
            .iter()
            .enumerate()
            .map(|(i, f)| {
                let c = self.face_center(f);
                (curve_key(c), i)
            })
            .collect();
        keyed.sort_unstable();
        keyed.into_iter().map(|(_, i)| i).collect()
    }

    pub fn face_center(&self, f: &[usize; 3]) -> Vec3 {
        let (a, b, c) = (self.verts[f[0]], self.verts[f[1]], self.verts[f[2]]);
        vnorm([
            (a[0] + b[0] + c[0]) / 3.0,
            (a[1] + b[1] + c[1]) / 3.0,
            (a[2] + b[2] + c[2]) / 3.0,
        ])
    }

    /// Bytes per face at this level, rounded up. `1` means one face per byte --
    /// the resolution `byte_sphere` reaches at L5 for a 24 KB sample.
    pub fn bytes_per_face(&self, n: usize) -> usize {
        (n.div_ceil(self.faces.len().max(1))).max(1)
    }
}

// ---------------------------------------------------------------------------
// THE SPHERICAL HILBERT KEY -- byte_sphere's curveKey, ported
// ---------------------------------------------------------------------------

/// Hilbert order for the 2D grid, `byte_sphere`'s `hilbXY2D`. Pure integer.
pub fn hilbert_xy(order: u32, mut x: u32, mut y: u32) -> u64 {
    let n = 1u32 << order;
    let mut d = 0u64;
    let mut s = n >> 1;
    while s > 0 {
        let rx = u32::from((x & s) > 0);
        let ry = u32::from((y & s) > 0);
        d += (s as u64) * (s as u64) * ((3 * rx) ^ ry) as u64;
        // rot
        if ry == 0 {
            if rx == 1 {
                x = n - 1 - x;
                y = n - 1 - y;
            }
            std::mem::swap(&mut x, &mut y);
        }
        s >>= 1;
    }
    d
}

/// Which cube face a direction points at, and where on it -- then the Hilbert
/// index within that face. `byte_sphere`'s `curveKey`, order 7 (128x128).
pub fn curve_key(c: Vec3) -> u64 {
    const O: u32 = 7;
    let n = 1u32 << O;
    let (ax, ay, az) = (c[0].abs(), c[1].abs(), c[2].abs());
    let (face, u, w) = if ax >= ay && ax >= az {
        (if c[0] > 0.0 { 0 } else { 1 }, -c[2] / ax, c[1] / ax)
    } else if ay >= az {
        (if c[1] > 0.0 { 2 } else { 3 }, c[0] / ay, -c[2] / ay)
    } else {
        (if c[2] > 0.0 { 4 } else { 5 }, c[0] / az, c[1] / az)
    };
    let g = |t: f64| -> u32 {
        let v = ((t * 0.5 + 0.5) * n as f64).floor();
        v.clamp(0.0, (n - 1) as f64) as u32
    };
    face as u64 * (n as u64 * n as u64) + hilbert_xy(O, g(u), g(w))
}
