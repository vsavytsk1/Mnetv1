//! # goldberg_kernel
//!
//! The closed set, in Rust. Zero dependencies.
//!
//! A census of 2,333 sims found 70,224 function bodies reducing to 5,598
//! distinct rules. Thirteen of them carry the whole structure, appearing in
//! 249-443 sims each: `vdot` `vsub` `vcross` `vscale` `vlerp` `vadd` `vlen`
//! `vnorm` `centroid` `project_to_sphere` `next_in_face` `build_c60_vertices`
//! `build_c60_faces`. This crate is those rules, once.
//!
//! ## The certified path and the display path
//!
//! JavaScript `Number` and Rust `f64` are both IEEE-754 binary64. For
//! `+ - * /` and `sqrt`, both are *correctly rounded*, so results are
//! bit-identical and a port is a translation rather than a reimplementation.
//!
//! `sin` `cos` `exp` `ln` `powf` are **not** bit-guaranteed -- not across
//! platforms and not between JS and Rust. They agree to within an ULP or so,
//! never exactly.
//!
//! So the crate is split:
//!
//! * **certified** -- integers, and f64 restricted to `+ - * / sqrt`.
//!   Asserted with `assert_eq!`. [`topology`], [`ladder`], most of [`complex`].
//! * **display** -- anything transcendental. Asserted with tolerances.
//!
//! Never assert bit-equality across the boundary. Tracking the boundary
//! explicitly is the whole discipline.
//!
//! ## Modules
//!
//! | module | what |
//! |---|---|
//! | [`ladder`] | the exact integer ladder, and where float64 breaks (n=38) |
//! | [`complex`] | complex arithmetic, the certified core of the light matrix |
//! | [`rng`] | deterministic PRNG -- replaces `Math.random`, makes runs reproducible |
//!
//! ```
//! use goldberg_kernel::{Mesh, certify};
//! let m = Mesh::c60();
//! let c = certify(&m).expect("the seed must certify");
//! assert_eq!((c.v, c.e, c.f, c.p, c.chi), (60, 90, 32, 12, 2));
//! ```
//!
//! *P=12 . chi=2 . the center holds and is not shown . always*

#![forbid(unsafe_code)]

pub mod bits;
pub mod complex;
pub mod font;
pub mod judge;
pub mod ladder;
pub mod ledger;
pub mod palette;
pub mod raster;
pub mod rng;

use std::collections::HashSet;
use std::fmt;

/// The golden ratio. The seed of the whole construction.
pub const PHI: f64 = 1.618_033_988_749_894_8;

/// A point or direction in R^3. Plain data, `Copy`, no allocation.
pub type Vec3 = [f64; 3];

/// Raw points emitted by the three phi-permutation triples before dedupe.
///
/// Exactly 60, so the dedupe pass is a no-op on a correct build -- which is
/// precisely why a wrong count here could never be caught at runtime (R6).
pub const RAW_PERM_POINTS: usize = 60;

// ===========================================================================
// STAGE 0 -- PRIMITIVE  (certified: + - * / sqrt only)
// ===========================================================================

/// `a + b`
#[inline]
pub fn vadd(a: Vec3, b: Vec3) -> Vec3 {
    [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
}

/// `a - b`
#[inline]
pub fn vsub(a: Vec3, b: Vec3) -> Vec3 {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}

/// `a * s`
#[inline]
pub fn vscale(a: Vec3, s: f64) -> Vec3 {
    [a[0] * s, a[1] * s, a[2] * s]
}

/// The cheapest "equals": `a . b = |a||b| cos t`. On unit vectors it *is*
/// `cos t`. This one line is the transformer in HELENA and the
/// nearest-neighbour test in every mesh here. It appears in 443 sims.
#[inline]
pub fn vdot(a: Vec3, b: Vec3) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

/// `a x b` -- the oriented normal. Orientation is what makes chi meaningful.
#[inline]
pub fn vcross(a: Vec3, b: Vec3) -> Vec3 {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}

/// `|a|`. `sqrt` is correctly rounded, so this stays on the certified path.
#[inline]
pub fn vlen(a: Vec3) -> f64 {
    vdot(a, a).sqrt()
}

/// `a / |a|`. A zero vector passes through unchanged rather than producing
/// NaN -- the JS did the same (`|| 1.0`). A NaN silently poisons a whole mesh
/// and resurfaces three stages later as an unexplainable render bug; a zero
/// is caught by [`certify`] where it happened.
#[inline]
pub fn vnorm(a: Vec3) -> Vec3 {
    let l = vlen(a);
    if l == 0.0 {
        a
    } else {
        vscale(a, 1.0 / l)
    }
}

/// Linear interpolation `a + (b - a) t`.
#[inline]
pub fn vlerp(a: Vec3, b: Vec3, t: f64) -> Vec3 {
    [
        a[0] * (1.0 - t) + b[0] * t,
        a[1] * (1.0 - t) + b[1] * t,
        a[2] * (1.0 - t) + b[2] * t,
    ]
}

/// Push a point onto the sphere of radius `r`.
#[inline]
pub fn project_to_sphere(a: Vec3, r: f64) -> Vec3 {
    vscale(vnorm(a), r)
}

/// The mean of a set of points. Empty input gives the origin.
pub fn centroid(pts: &[Vec3]) -> Vec3 {
    if pts.is_empty() {
        return [0.0, 0.0, 0.0];
    }
    let mut s = [0.0, 0.0, 0.0];
    for p in pts {
        s = vadd(s, *p);
    }
    vscale(s, 1.0 / pts.len() as f64)
}

// ===========================================================================
// STAGE 1 -- TOPOLOGY
// ===========================================================================

/// A closed polyhedral surface: vertices on the unit sphere, undirected
/// edges, faces as vertex-index cycles, and per-vertex adjacency.
#[derive(Clone, Debug)]
pub struct Mesh {
    pub verts: Vec<Vec3>,
    pub edges: Vec<(usize, usize)>,
    pub faces: Vec<Vec<usize>>,
    pub adj: Vec<Vec<usize>>,
}

/// What a certified shell reports. These are the integers the browser build
/// card prints; the port must reproduce them exactly.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct Cert {
    pub v: usize,
    pub e: usize,
    pub f: usize,
    /// pentagons -- Euler forces exactly 12
    pub p: usize,
    /// hexagons
    pub h: usize,
    pub chi: i64,
}

impl fmt::Display for Cert {
    fn fmt(&self, w: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            w,
            "V={} E={} F={} P={} H={} chi={} E/V={:.1} CLOSED",
            self.v,
            self.e,
            self.f,
            self.p,
            self.h,
            self.chi,
            self.e as f64 / self.v as f64
        )
    }
}

/// Why a shell failed to certify. A failure is never silent and always says
/// which invariant broke and by how much.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum CertError {
    /// `V - E + F != 2` -- the surface is not a sphere.
    NotSphere(i64),
    /// Euler forces twelve pentagons on a trivalent pentagon/hexagon surface.
    PentagonCount(usize),
    /// Every vertex of a Goldberg polyhedron has degree 3.
    NotTrivalent(usize),
    /// `E/V != 3/2`.
    EdgeRatio(usize, usize),
    Empty,
}

impl fmt::Display for CertError {
    fn fmt(&self, w: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            CertError::NotSphere(c) => write!(w, "chi = {c}, expected 2 (not a sphere)"),
            CertError::PentagonCount(p) => write!(w, "P = {p}, expected 12 (Euler forces 12)"),
            CertError::NotTrivalent(d) => write!(w, "found a vertex of degree {d}, expected 3"),
            CertError::EdgeRatio(e, v) => write!(w, "E/V = {e}/{v}, expected 3/2"),
            CertError::Empty => write!(w, "empty mesh"),
        }
    }
}

impl std::error::Error for CertError {}

/// Emit every cyclic permutation and sign combination of `(a, b, c)`.
///
/// A zero coordinate has no distinct negative, so it is skipped -- that is what
/// keeps the raw count at **60 rather than 72**. Measured: `3*1*2*2 = 12` from
/// `(0, +-1, +-3phi)`, plus `3*8 = 24` and `3*8 = 24` from the two triples with
/// no zero. Twelve, twenty-four, twenty-four.
///
/// (The earlier comment here said "72 rather than 96". Both numbers were wrong,
/// the code was right, and every test passed -- RUSTIUM curse R6. A comment
/// that states a count now has an assertion behind it.)
fn push_perms(a: f64, b: f64, c: f64, raw: &mut Vec<Vec3>) {
    const PERMS: [[usize; 3]; 3] = [[0, 1, 2], [1, 2, 0], [2, 0, 1]];
    for p in PERMS.iter() {
        for sa in [-1.0f64, 1.0] {
            for sb in [-1.0f64, 1.0] {
                for sc in [-1.0f64, 1.0] {
                    if a == 0.0 && sa < 0.0 {
                        continue;
                    }
                    if b == 0.0 && sb < 0.0 {
                        continue;
                    }
                    if c == 0.0 && sc < 0.0 {
                        continue;
                    }
                    let mut v = [0.0f64; 3];
                    v[p[0]] = sa * a;
                    v[p[1]] = sb * b;
                    v[p[2]] = sc * c;
                    raw.push(v);
                }
            }
        }
    }
}

/// The 60 vertices of the truncated icosahedron, on the unit sphere.
///
/// All cyclic permutations of `(0, +-1, +-3phi)`, `(+-1, +-(2+phi), +-2phi)`,
/// `(+-phi, +-2, +-(2phi+1))`. No trigonometry anywhere: the seed is `PHI`
/// and exact arithmetic, so the result is reproducible bit-for-bit on any
/// IEEE-754 platform. This is why the certified path can avoid `sin`/`cos`.
pub fn build_c60_vertices() -> Vec<Vec3> {
    let mut raw: Vec<Vec3> = Vec::with_capacity(RAW_PERM_POINTS);
    push_perms(0.0, 1.0, 3.0 * PHI, &mut raw);
    push_perms(1.0, 2.0 + PHI, 2.0 * PHI, &mut raw);
    push_perms(PHI, 2.0, 2.0 * PHI + 1.0, &mut raw);
    debug_assert_eq!(
        raw.len(),
        RAW_PERM_POINTS,
        "the zero-skip must leave exactly {RAW_PERM_POINTS} raw points (R6)"
    );

    let mut out: Vec<Vec3> = Vec::with_capacity(60);
    for v in raw {
        let dup = out.iter().any(|u| {
            (v[0] - u[0]).abs() < 1e-9 && (v[1] - u[1]).abs() < 1e-9 && (v[2] - u[2]).abs() < 1e-9
        });
        if !dup {
            out.push(v);
        }
    }
    out.iter().map(|v| vnorm(*v)).collect()
}

/// Undirected edges and adjacency, by shortest-distance threshold.
///
/// On a Goldberg polyhedron every vertex has exactly three neighbours, so a
/// 15% tolerance above the minimum separation is generous but unambiguous --
/// the next distance class is far beyond it. [`certify`] re-checks the degree,
/// so a bad threshold cannot pass silently.
pub fn build_edges(verts: &[Vec3]) -> (Vec<(usize, usize)>, Vec<Vec<usize>>) {
    let n = verts.len();
    let mut min_d = f64::INFINITY;
    for i in 0..n {
        for j in (i + 1)..n {
            let d = vlen(vsub(verts[i], verts[j]));
            if d < min_d {
                min_d = d;
            }
        }
    }
    let tol = min_d * 1.15;
    let mut edges = Vec::new();
    let mut adj: Vec<Vec<usize>> = vec![Vec::new(); n];
    for i in 0..n {
        for j in (i + 1)..n {
            if vlen(vsub(verts[i], verts[j])) <= tol {
                edges.push((i, j));
                adj[i].push(j);
                adj[j].push(i);
            }
        }
    }
    (edges, adj)
}

/// Walking the directed edge `a -> b`, which vertex comes next around the face?
///
/// At `b` the outward normal is `b` itself (we are on the sphere). Project the
/// incoming direction and each candidate into the tangent plane at `b`, then
/// take the candidate at the smallest positive turn. Choosing consistently is
/// what makes the traversal orientable -- and orientability is what makes
/// `chi = 2` mean anything.
///
/// Uses `atan2`, so this sits on the **display** side of the boundary: the
/// angles are not bit-portable, but the *ordering* they induce is stable
/// because the candidates are far apart on a valid mesh.
pub fn next_in_face(verts: &[Vec3], adj: &[Vec<usize>], a: usize, b: usize) -> Option<usize> {
    let n = vnorm(verts[b]);
    let r = vsub(verts[a], verts[b]);
    let r = vnorm(vsub(r, vscale(n, vdot(r, n))));
    let perp = vcross(n, r);

    let mut best: Option<usize> = None;
    let mut best_ang = f64::INFINITY;
    for &c in &adj[b] {
        if c == a {
            continue;
        }
        let t = vsub(verts[c], verts[b]);
        let t = vsub(t, vscale(n, vdot(t, n)));
        let mut ang = vdot(t, perp).atan2(vdot(t, r));
        if ang < 0.0 {
            ang += std::f64::consts::TAU;
        }
        if ang < best_ang {
            best_ang = ang;
            best = Some(c);
        }
    }
    best
}

/// Trace every face by walking each directed edge exactly once.
///
/// A closed orientable surface puts each directed edge in exactly one face,
/// so the traversal terminates and the faces partition the directed edges.
/// The guard at 16 is a tripwire, not a limit: on a valid mesh it never fires.
pub fn build_c60_faces(verts: &[Vec3], adj: &[Vec<usize>]) -> Vec<Vec<usize>> {
    let mut seen: HashSet<(usize, usize)> = HashSet::new();
    let mut faces: Vec<Vec<usize>> = Vec::new();

    for a in 0..verts.len() {
        for &b in &adj[a] {
            if seen.contains(&(a, b)) {
                continue;
            }
            let mut face = vec![a];
            let (mut x, mut y) = (a, b);
            loop {
                seen.insert((x, y));
                face.push(y);
                let z = match next_in_face(verts, adj, x, y) {
                    Some(z) => z,
                    None => break,
                };
                x = y;
                y = z;
                if (x, y) == (a, b) {
                    break;
                }
                if face.len() > 16 {
                    break;
                }
            }
            if face.last() == Some(&a) {
                face.pop();
            }
            faces.push(face);
        }
    }
    faces
}

impl Mesh {
    /// The seed: C60, the buckyball. The only closed structure you can build
    /// from pentagons and hexagons at this size.
    pub fn c60() -> Mesh {
        let verts = build_c60_vertices();
        let (edges, adj) = build_edges(&verts);
        let faces = build_c60_faces(&verts, &adj);
        Mesh {
            verts,
            edges,
            faces,
            adj,
        }
    }

    pub fn pentagons(&self) -> usize {
        self.faces.iter().filter(|f| f.len() == 5).count()
    }

    pub fn hexagons(&self) -> usize {
        self.faces.iter().filter(|f| f.len() == 6).count()
    }

    /// `V - E + F`. Two for a sphere. Zero for a Mobius band (HELENA's heart).
    pub fn chi(&self) -> i64 {
        self.verts.len() as i64 - self.edges.len() as i64 + self.faces.len() as i64
    }

    /// The centre of each face, pushed back onto the unit sphere. These are
    /// the vertices of the dual and the seed of the next refinement level.
    pub fn face_centers(&self) -> Vec<Vec3> {
        self.faces
            .iter()
            .map(|f| {
                let pts: Vec<Vec3> = f.iter().map(|&i| self.verts[i]).collect();
                project_to_sphere(centroid(&pts), 1.0)
            })
            .collect()
    }
}

/// Certify a shell, or say exactly why it fails. Nothing here is assumed.
pub fn certify(m: &Mesh) -> Result<Cert, CertError> {
    if m.verts.is_empty() {
        return Err(CertError::Empty);
    }
    for a in &m.adj {
        if a.len() != 3 {
            return Err(CertError::NotTrivalent(a.len()));
        }
    }
    let (v, e, f) = (m.verts.len(), m.edges.len(), m.faces.len());
    let chi = m.chi();
    if chi != 2 {
        return Err(CertError::NotSphere(chi));
    }
    let p = m.pentagons();
    if p != 12 {
        return Err(CertError::PentagonCount(p));
    }
    if e * 2 != v * 3 {
        return Err(CertError::EdgeRatio(e, v));
    }
    Ok(Cert {
        v,
        e,
        f,
        p,
        h: m.hexagons(),
        chi,
    })
}

// ===========================================================================
// THE GOLDBERG LADDER  (counts only -- pure integer, certified)
// ===========================================================================

/// The triangulation number at refinement level `k`: `T = 3 * 7^k`.
pub fn triangulation_number(level: u32) -> usize {
    3 * 7usize.pow(level)
}

/// Counts for refinement level `k`, without building the mesh.
///
/// `V = 20T`, `E = 30T`, `F = 10T + 2`, and `P = 12` forever. Reproduces the
/// HELENA build card exactly for k = 0..3.
pub fn goldberg_counts(level: u32) -> Cert {
    let t = triangulation_number(level);
    let v = 20 * t;
    let e = 30 * t;
    let f = 10 * t + 2;
    Cert {
        v,
        e,
        f,
        p: 12,
        h: f - 12,
        chi: v as i64 - e as i64 + f as i64,
    }
}
