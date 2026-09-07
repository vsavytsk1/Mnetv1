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

/// A Goldberg polyhedron: trivalent, twelve pentagons, closed.
///
/// Produced by [`Ico::dual`], never by refinement of a face soup.
#[derive(Clone, Debug)]
pub struct Gold {
    /// one per triangle of the icosphere it came from
    pub verts: Vec<Vec3>,
    /// one per VERTEX of that icosphere -- a cycle of triangle indices
    pub faces: Vec<Vec<usize>>,
}

impl Gold {
    /// Pentagons, counted by arity rather than by a label.
    pub fn pents(&self) -> usize {
        self.faces.iter().filter(|f| f.len() == 5).count()
    }

    /// The rotation system, if these faces form a closed orientable surface.
    pub fn rotation(&self) -> Option<Vec<usize>> {
        crate::judge::rotation_from_faces(&self.faces)
    }

    /// Hand it to the judge. `chi` comes from ORBITS, never from a formula.
    pub fn judge(&self) -> Option<crate::judge::Verdict> {
        crate::judge::check(&self.rotation()?).ok()
    }
}

impl Ico {
    /// **The dual: a closed Goldberg polyhedron, `GP(2^L, 0)`.**
    ///
    /// This is the answer to a question `genesis` cannot answer. Its
    /// `refine_face` builds FACE SOUP -- every face owning its own corners --
    /// and `examples/whats_open` measures the consequence exactly: at level 1
    /// there are 540 unpaired directed edges in three groups of 180,
    /// `inner -> mid-ring`, `inner -> inner` and `mid-ring -> inner`. That is
    /// 180 triangular holes, one per face-edge of the seed, and **not one of
    /// them touches a corner or an edge midpoint**. The hole lies INSIDE a
    /// face, so no amount of sharing points BETWEEN faces can fill it, and
    /// filling it with a triangle would change `7F - 12` and break the growth
    /// law. The crescent is the picture (README) and it stays.
    ///
    /// So the closed lane is built somewhere else, and it is nearly free:
    ///
    /// ```text
    ///   icosphere         F = 20*4^L   V = 10*4^L + 2   E = 30*4^L
    ///   its dual          V = 20*4^L   F = 10*4^L + 2   E = 30*4^L
    ///                       = 20T          = 10T + 2        = 30T,  T = 4^L
    /// ```
    ///
    /// which is exactly THEA's Goldberg counting. Every dual vertex is a
    /// triangle centre with three neighbours, so the mesh is **trivalent by
    /// construction**; every dual face is one icosphere vertex, so the twelve
    /// defects become the twelve pentagons and `P = 12` is inherited rather
    /// than asserted.
    ///
    /// The subdivision underneath welds by SORTED INDEX PAIR with no tolerance
    /// (see the module header), so this closes at every depth memory allows --
    /// R7's float-threshold lane died at C380 and there is nothing here to
    /// outgrow.
    ///
    /// LANE: the connectivity is EXACT integer work. `face_center` normalises,
    /// which is DISPLAY -- so the positions are display and the topology is not.
    pub fn dual(&self) -> Gold {
        // triangle centres become the dual's vertices
        let verts: Vec<Vec3> = self.faces.iter().map(|f| self.face_center(f)).collect();

        // directed edge -> the triangle that carries it. On a closed oriented
        // surface each directed edge belongs to exactly one triangle, which is
        // what makes the walk below deterministic.
        let mut tri_of: HashMap<(usize, usize), usize> =
            HashMap::with_capacity(self.faces.len() * 3);
        for (t, f) in self.faces.iter().enumerate() {
            for i in 0..3 {
                tri_of.insert((f[i], f[(i + 1) % 3]), t);
            }
        }

        let mut faces: Vec<Vec<usize>> = Vec::with_capacity(self.verts.len());
        for v in 0..self.verts.len() {
            // any triangle that has v, to start the fan
            let Some(start) = self.faces.iter().position(|f| f.contains(&v)) else {
                continue;
            };
            let mut cycle = Vec::with_capacity(6);
            let mut t = start;
            loop {
                cycle.push(t);
                // the neighbour v points at inside this triangle
                let f = &self.faces[t];
                let i = f
                    .iter()
                    .position(|&x| x == v)
                    .expect("v is in this triangle");
                let n = f[(i + 1) % 3];
                // cross edge (v,n): the triangle carrying (n,v)
                let Some(&next) = tri_of.get(&(n, v)) else {
                    break; // a border -- cannot happen on a closed icosphere
                };
                t = next;
                if t == start {
                    break;
                }
                if cycle.len() > 32 {
                    break; // a fan that never closes is a corrupt mesh, not a loop to ride
                }
            }
            faces.push(cycle);
        }

        Gold { verts, faces }
    }
}

#[cfg(test)]
mod dual_tests {
    use super::*;

    /// **The dual closes, and the judge says so from orbits.**
    ///
    /// The sentence `genesis` cannot make. Not "the formula gives 2" -- the
    /// module header warns that `V - E + F` returns 2 for every L whether or
    /// not a mesh was ever built -- but "a permutation was walked and its
    /// orbits were counted".
    #[test]
    fn the_dual_closes_at_every_rung() {
        for l in 0..=4 {
            let g = Ico::level(l).expect("level fits").dual();
            let v = g
                .judge()
                .unwrap_or_else(|| panic!("level {l}: the dual is not a closed surface"));
            let t = 4u64.pow(l);
            assert_eq!(v.v as u64, 20 * t, "L{l}: V must be 20T");
            assert_eq!(v.e as u64, 30 * t, "L{l}: E must be 30T");
            assert_eq!(v.f as u64, 10 * t + 2, "L{l}: F must be 10T+2");
            assert_eq!(v.chi, 2, "L{l}: chi from ORBITS must be 2");
            assert_eq!(v.components, 1, "L{l}: one piece");
            assert_eq!(v.genus, Some(0), "L{l}: a sphere");
        }
    }

    /// Twelve pentagons, counted by arity, inherited from the icosphere's
    /// twelve defects rather than asserted.
    #[test]
    fn the_dual_has_exactly_twelve_pentagons() {
        for l in 0..=4 {
            let ico = Ico::level(l).expect("level fits");
            let defects = ico.defects().len();
            let g = ico.dual();
            assert_eq!(
                defects, 12,
                "L{l}: the icosphere has twelve degree-5 vertices"
            );
            assert_eq!(g.pents(), 12, "L{l}: and so the dual has twelve pentagons");
            // every other face is a hexagon -- nothing else may appear
            for f in &g.faces {
                assert!(
                    f.len() == 5 || f.len() == 6,
                    "L{l}: a face of arity {} appeared; a Goldberg polyhedron has only 5s and 6s",
                    f.len()
                );
            }
        }
    }

    /// **Trivalent by construction** -- every dual vertex is a triangle centre
    /// with exactly three neighbours.
    ///
    /// This is the property `genesis`'s soup does not have: its welded degrees
    /// are 1, 2, 3 and 6 (see `src/weld.rs`), so `arity_sum / 3` is a
    /// prediction the geometry does not satisfy. Here it is satisfied, so the
    /// same division is a measurement.
    #[test]
    fn the_dual_is_trivalent() {
        for l in 0..=4 {
            let g = Ico::level(l).expect("level fits").dual();
            let mut deg = vec![0usize; g.verts.len()];
            for f in &g.faces {
                for &i in f {
                    deg[i] += 1;
                }
            }
            assert!(
                deg.iter().all(|&d| d == 3),
                "L{l}: a dual vertex has degree {:?}, not 3",
                deg.iter().find(|&&d| d != 3)
            );
            let arity: usize = g.faces.iter().map(|f| f.len()).sum();
            assert_eq!(
                arity / 3,
                g.verts.len(),
                "L{l}: arity_sum/3 must equal V when the mesh really is trivalent"
            );
        }
    }

    /// **`Ico::level(0).dual()` is the DODECAHEDRON.**
    ///
    /// Worth its own test because the viewer's `SEED 12` button has said
    /// *NOT WIRED, NOT PRETENDING* since v0.1, and `GENESIS_PORT_SPEC` lists
    /// `buildDodecahedron` as unported. It was reachable the whole time from
    /// the lane next door: the dual of the base icosahedron.
    #[test]
    fn level_zero_dual_is_the_dodecahedron() {
        let g = Ico::level(0).expect("the base fits").dual();
        assert_eq!(g.verts.len(), 20, "a dodecahedron has 20 vertices");
        assert_eq!(g.faces.len(), 12, "and 12 faces");
        assert_eq!(g.pents(), 12, "all of them pentagons");
        let v = g.judge().expect("it closes");
        assert_eq!((v.v, v.e, v.f, v.chi), (20, 30, 12, 2));
    }

    /// The dual is deterministic: two calls give the identical mesh.
    #[test]
    fn the_dual_is_deterministic() {
        let ico = Ico::level(2).expect("level fits");
        let (a, b) = (ico.dual(), ico.dual());
        assert_eq!(a.faces, b.faces);
        assert_eq!(a.verts.len(), b.verts.len());
        for (u, v) in a.verts.iter().zip(b.verts.iter()) {
            for k in 0..3 {
                assert_eq!(
                    u[k].to_bits(),
                    v[k].to_bits(),
                    "a centre moved between calls"
                );
            }
        }
    }
}

impl Gold {
    /// Face adjacency: two faces are neighbours when they share an edge.
    ///
    /// On a closed orientable surface every undirected edge belongs to exactly
    /// two faces, so this is a total function and a face with a different
    /// count is a corrupt mesh rather than a special case. That is asserted,
    /// not assumed -- the whole point of building on a lane that closes.
    pub fn adjacency(&self) -> Vec<Vec<usize>> {
        let mut by_edge: HashMap<(usize, usize), Vec<usize>> = HashMap::new();
        for (fi, f) in self.faces.iter().enumerate() {
            for i in 0..f.len() {
                let (a, b) = (f[i], f[(i + 1) % f.len()]);
                let key = if a < b { (a, b) } else { (b, a) };
                by_edge.entry(key).or_default().push(fi);
            }
        }
        let mut adj = vec![Vec::new(); self.faces.len()];
        for (_, fs) in by_edge {
            debug_assert_eq!(fs.len(), 2, "an edge of a closed surface has two faces");
            if fs.len() == 2 {
                adj[fs[0]].push(fs[1]);
                adj[fs[1]].push(fs[0]);
            }
        }
        adj
    }

    /// Hop distance from `src` to every face, on the DUAL adjacency.
    ///
    /// Plain BFS: every edge costs one, so the queue is a queue and there is
    /// no priority to maintain. That is the whole point of a topology-first
    /// frontier -- the sorting barrier is a cost of ORDERING, and unit weights
    /// have nothing to order.
    ///
    /// `usize::MAX` marks unreachable, which on a connected shell never occurs
    /// and is therefore worth leaving visible rather than collapsing to 0.
    pub fn hops(&self, src: usize, adj: &[Vec<usize>]) -> Vec<usize> {
        let mut d = vec![usize::MAX; self.faces.len()];
        if src >= d.len() {
            return d;
        }
        d[src] = 0;
        let mut q = std::collections::VecDeque::new();
        q.push_back(src);
        while let Some(u) = q.pop_front() {
            for &v in &adj[u] {
                if d[v] == usize::MAX {
                    d[v] = d[u] + 1;
                    q.push_back(v);
                }
            }
        }
        d
    }

    /// Which faces are pentagons -- by ARITY, never by a label.
    pub fn pentagons(&self) -> Vec<usize> {
        self.faces
            .iter()
            .enumerate()
            .filter(|(_, f)| f.len() == 5)
            .map(|(i, _)| i)
            .collect()
    }

    /// The smallest and largest hop distance between two distinct pentagons.
    ///
    /// The MINIMUM is the interesting one: it is the "adjacent pentagon
    /// distance" the pentagon-map hypothesis predicts as
    /// `max(|k|, |l|, |k+l|)`. The maximum is reported beside it because a
    /// closed form that happened to match the max instead would be a different
    /// claim, and printing only the number you predicted is how a hypothesis
    /// gets confirmed by its own reader.
    ///
    /// Returns `None` for a shell with fewer than two pentagons, which cannot
    /// happen on a fullerene and is therefore reported rather than defaulted.
    pub fn pentagon_span(&self) -> Option<(usize, usize)> {
        let pents = self.pentagons();
        if pents.len() < 2 {
            return None;
        }
        let adj = self.adjacency();
        let (mut lo, mut hi) = (usize::MAX, 0usize);
        for (i, &p) in pents.iter().enumerate() {
            let d = self.hops(p, &adj);
            for &q in &pents[i + 1..] {
                let x = d[q];
                if x == usize::MAX {
                    continue;
                }
                lo = lo.min(x);
                hi = hi.max(x);
            }
        }
        if lo == usize::MAX {
            None
        } else {
            Some((lo, hi))
        }
    }
}

#[cfg(test)]
mod hop_tests {
    use super::*;

    /// Every face has as many neighbours as it has sides.
    ///
    /// True only on a closed surface, which is why this lane can carry a hop
    /// distance and the crescent soup cannot: `examples/whats_open` measures
    /// 540 unpaired directed edges at genesis level 1, so a BFS there would be
    /// walking a mesh with 180 holes and calling the result a distance.
    #[test]
    fn adjacency_matches_arity_on_a_closed_shell() {
        for l in 0..=3 {
            let g = Ico::level(l).expect("level fits").dual();
            let adj = g.adjacency();
            for (i, f) in g.faces.iter().enumerate() {
                assert_eq!(
                    adj[i].len(),
                    f.len(),
                    "L{l} face {i}: {} sides but {} neighbours",
                    f.len(),
                    adj[i].len()
                );
            }
        }
    }

    /// BFS reaches every face, and the shell has a finite diameter.
    #[test]
    fn every_face_is_reachable() {
        for l in 0..=3 {
            let g = Ico::level(l).expect("level fits").dual();
            let adj = g.adjacency();
            let d = g.hops(0, &adj);
            assert!(
                d.iter().all(|&x| x != usize::MAX),
                "L{l}: a face is unreachable, so the shell is not connected"
            );
            assert_eq!(d[0], 0, "the source is at distance zero from itself");
        }
    }

    /// **The mage's hypothesis, on the doubling lane.**
    ///
    /// `tower/pentagon_map_v0_1.py` claims the adjacent pentagon hop distance
    /// is `max(|k|, |l|, |k+l|)` and its receipt reports 10 of 10 on the golden
    /// lane. `Ico::dual` gives `GP(2^L, 0)`, where that reduces to `k = 2^L`,
    /// and the Python's table touches this lane only at `(1,0)`.
    #[test]
    fn the_closed_form_predicts_the_adjacent_pentagon_distance() {
        for l in 0..=4 {
            let g = Ico::level(l).expect("level fits").dual();
            let (lo, _hi) = g.pentagon_span().expect("a fullerene has twelve pentagons");
            let k = 1usize << l;
            assert_eq!(
                lo, k,
                "L{l}: closed form max(|k|,|l|,|k+l|) = {k} but the measured minimum \
                 pentagon distance is {lo}"
            );
        }
    }

    /// The shared row with the Python lab: `(1,0)` must read min 1, max 3.
    ///
    /// One row measured twice, in two languages, on two implementations that
    /// share no code. If they ever disagree, one of the labs is wrong and this
    /// says so before either is quoted.
    #[test]
    fn the_dodecahedron_row_agrees_with_the_python_receipt() {
        let g = Ico::level(0).expect("the base fits").dual();
        assert_eq!(
            g.pentagon_span(),
            Some((1, 3)),
            "tower/pentagon_map_v0_1_receipt.json records min 1 and max 3 for (1,0)"
        );
    }

    /// **On the achiral doubling lane the span is exactly three times the
    /// minimum** -- and that is not true of the chiral lanes.
    ///
    /// Measured here: min 1,2,4,8,16 against max 3,6,12,24,48. The Python's
    /// golden-lane rows give ratios near 2.4 instead -- 5/2, 7/3, 12/5, 19/8,
    /// 31/13 -- so this clean integer 3 is a property of `l = 0`, not of
    /// Goldberg shells in general. Recorded because a ratio that holds on one
    /// lane and not another is a fact about the lanes.
    #[test]
    fn the_doubling_lane_span_is_exactly_three_times_the_minimum() {
        for l in 0..=4 {
            let g = Ico::level(l).expect("level fits").dual();
            let (lo, hi) = g.pentagon_span().expect("twelve pentagons");
            assert_eq!(
                hi,
                3 * lo,
                "L{l}: max {hi} is not three times min {lo} -- the integer relation broke"
            );
        }
    }
}
