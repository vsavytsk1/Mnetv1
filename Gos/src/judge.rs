//! THE JUDGE -- closure certified in pure graph space. Integer only.
//!
//! Ported from `shell/latexium_symbols_v0_2.html`, kernel frozen at v0.1.0,
//! sha-256 `2d7337ea...d02ef63f`. The port changes no semantics: same refusals,
//! same counts, same order of checks. Path X -- a frozen rung is re-implemented,
//! never edited.
//!
//! # Why this exists
//!
//! [`crate::build_edges`] decides adjacency with a float distance threshold,
//! and RUSTIUM curse R7 measured where that dies: **C380**, the fourth rung,
//! where the edge-length spread (1.2156) exceeds the 1.15 tolerance and 330 of
//! 570 edges vanish. Precision is fractalization depth, so a float in the
//! adjacency test is a hard ceiling on precision.
//!
//! This module has no such ceiling because it has no float. A surface is a
//! **combinatorial map**: a set of darts and two permutations.
//!
//! ```text
//!   dart      a half-edge. Edge i owns darts 2i and 2i+1.
//!   alpha     the edge involution. alpha(d) = d ^ 1. Free, exact, an XOR.
//!   sigma     the rotation: the cyclic order of darts around their vertex.
//!   phi       sigma o alpha -- the face permutation.
//!
//!   V = orbits of sigma        E = darts / 2        F = orbits of phi
//!   chi = V - E + F            genus = (2 - chi) / 2   when connected
//! ```
//!
//! Every one of those is an integer counted by walking a cycle. Nothing is
//! measured, nothing is compared to a tolerance, nothing rounds. The judge
//! never sees a coordinate, so it cannot be fooled by one.
//!
//! # The trusted base
//!
//! This is the whole trust boundary, and it is deliberately small enough to
//! read in one sitting -- the LCF `thm` / seL4 / Guix-357-byte-seed lineage.
//! Everything else in this crate is untrusted surgery that must earn the
//! judge's acceptance. **Guard the line count like Wirth guarded Oberon's.**
//!
//! ```
//! use goldberg_kernel::judge::{check, rotation_system_c60};
//! let sigma = rotation_system_c60();
//! let v = check(&sigma).expect("C60 is a closed orientable surface");
//! assert_eq!((v.v, v.e, v.f, v.chi, v.genus), (60, 90, 32, 2, Some(0)));
//! ```

use std::collections::HashMap;
use std::fmt;

/// What the judge reports about a map. Integers, all of them.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct Verdict {
    /// orbits of `sigma` -- vertices
    pub v: usize,
    /// `darts / 2` -- edges
    pub e: usize,
    /// orbits of `sigma o alpha` -- faces
    pub f: usize,
    /// `V - E + F`. Computed, never assumed.
    pub chi: i64,
    pub components: usize,
    /// `(2 - chi) / 2`, only meaningful when connected.
    pub genus: Option<i64>,
}

impl fmt::Display for Verdict {
    fn fmt(&self, w: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            w,
            "V={} E={} F={} chi={} components={} genus={}",
            self.v,
            self.e,
            self.f,
            self.chi,
            self.components,
            match self.genus {
                Some(g) => g.to_string(),
                None => "n/a".into(),
            }
        )
    }
}

/// Why a map was refused. Every refusal is labelled and loud -- never a silent
/// wrong answer (Path IV; Erlang's "let it crash" applied to a certificate).
#[derive(Clone, PartialEq, Eq, Debug)]
pub enum Refusal {
    /// darts must be even and nonzero
    DartCount(usize),
    /// `sigma` leaves the dart set
    OutOfRange { at: usize, to: usize },
    /// `sigma` is not a bijection -- it hits the same dart twice
    NotBijection { hits: usize },
    /// a half-integer genus means the map is corrupt
    HalfGenus { chi: i64 },
}

impl fmt::Display for Refusal {
    fn fmt(&self, w: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Refusal::DartCount(d) => write!(w, "darts must be even and nonzero, got {d}"),
            Refusal::OutOfRange { at, to } => {
                write!(w, "sigma leaves the dart set at {at} (-> {to})")
            }
            Refusal::NotBijection { hits } => {
                write!(w, "sigma is not a bijection (hits {hits} twice)")
            }
            Refusal::HalfGenus { chi } => {
                write!(w, "half-integer genus from chi = {chi}: the map is corrupt")
            }
        }
    }
}

impl std::error::Error for Refusal {}

/// The edge involution. Darts `2i` and `2i+1` are the two halves of edge `i`,
/// so pairing them is a single XOR -- exact, free, and impossible to get wrong.
#[inline]
pub fn alpha(d: usize) -> usize {
    d ^ 1
}

/// Count the orbits of a permutation given as a successor function.
fn orbits(d_count: usize, next: impl Fn(usize) -> usize) -> usize {
    let mut seen = vec![false; d_count];
    let mut n = 0;
    for s in 0..d_count {
        if seen[s] {
            continue;
        }
        n += 1;
        let mut c = s;
        loop {
            seen[c] = true;
            c = next(c);
            if c == s {
                break;
            }
        }
    }
    n
}

/// **The judge.** Accept a rotation system, or say exactly why not.
///
/// `sigma[d]` is the next dart counter-clockwise around the vertex that `d`
/// leaves. Nothing else is required and nothing else is consulted.
pub fn check(sigma: &[usize]) -> Result<Verdict, Refusal> {
    let d_count = sigma.len();
    if d_count == 0 || d_count % 2 == 1 {
        return Err(Refusal::DartCount(d_count));
    }

    // sigma must be a permutation of the dart set. Both halves are checked
    // because "in range" and "bijective" are different failures.
    let mut seen = vec![false; d_count];
    for (d, &t) in sigma.iter().enumerate() {
        if t >= d_count {
            return Err(Refusal::OutOfRange { at: d, to: t });
        }
        if seen[t] {
            return Err(Refusal::NotBijection { hits: t });
        }
        seen[t] = true;
    }

    let v = orbits(d_count, |d| sigma[d]);
    let f = orbits(d_count, |d| sigma[alpha(d)]);
    let e = d_count / 2;

    // connected components under "same vertex" or "same edge"
    let mut comp = vec![usize::MAX; d_count];
    let mut nc = 0;
    for s in 0..d_count {
        if comp[s] != usize::MAX {
            continue;
        }
        let mut stack = vec![s];
        comp[s] = nc;
        while let Some(d) = stack.pop() {
            for n in [sigma[d], alpha(d)] {
                if comp[n] == usize::MAX {
                    comp[n] = nc;
                    stack.push(n);
                }
            }
        }
        nc += 1;
    }

    let chi = v as i64 - e as i64 + f as i64;
    let genus = if nc == 1 {
        if (2 - chi) % 2 != 0 {
            return Err(Refusal::HalfGenus { chi });
        }
        Some((2 - chi) / 2)
    } else {
        None
    };

    Ok(Verdict {
        v,
        e,
        f,
        chi,
        components: nc,
        genus,
    })
}

// ===========================================================================
// BUILDING A ROTATION SYSTEM -- the float touches this ONCE, then never again
// ===========================================================================

/// Turn oriented face cycles into a rotation system.
///
/// Faces arrive as vertex-index cycles wound consistently. From them the face
/// permutation `phi` is read off directly (the next dart in the same face), and
/// `sigma(x) = phi(alpha(x))` recovers the rotation.
///
/// **This is the seam.** Whatever produced those faces -- a float threshold, an
/// exact integer lattice, a file on disk -- stops mattering the moment sigma
/// exists. From here down everything is integer, so the judge's verdict is
/// exact even when the construction that suggested it was not.
///
/// Returns `None` if the faces do not present each directed edge exactly once,
/// which is itself a closure failure worth catching early.
pub fn rotation_from_faces(faces: &[Vec<usize>]) -> Option<Vec<usize>> {
    // index every directed edge; pair (a,b) with (b,a) as darts 2i / 2i+1
    let mut dart_of: HashMap<(usize, usize), usize> = HashMap::new();
    let mut directed: Vec<(usize, usize)> = Vec::new();
    for face in faces {
        for i in 0..face.len() {
            let a = face[i];
            let b = face[(i + 1) % face.len()];
            if dart_of.contains_key(&(a, b)) {
                return None; // a directed edge used twice -- not a surface
            }
            dart_of.insert((a, b), usize::MAX);
            directed.push((a, b));
        }
    }
    // assign dart ids so that alpha is XOR-1
    let mut next_id = 0usize;
    for &(a, b) in &directed {
        if dart_of[&(a, b)] != usize::MAX {
            continue;
        }
        let twin = dart_of.get(&(b, a)).copied()?;
        if twin != usize::MAX {
            return None; // twin already numbered out of band
        }
        dart_of.insert((a, b), next_id);
        dart_of.insert((b, a), next_id + 1);
        next_id += 2;
    }
    if next_id != directed.len() {
        return None; // some directed edge had no twin: the surface has a border
    }

    // phi: the next dart around the same face
    let mut phi = vec![usize::MAX; next_id];
    for face in faces {
        for i in 0..face.len() {
            let a = face[i];
            let b = face[(i + 1) % face.len()];
            let c = face[(i + 2) % face.len()];
            phi[dart_of[&(a, b)]] = dart_of[&(b, c)];
        }
    }
    if phi.contains(&usize::MAX) {
        return None;
    }

    // sigma(x) = phi(alpha(x))
    Some((0..next_id).map(|x| phi[alpha(x)]).collect())
}

/// The C60 rotation system, as integers.
///
/// Built once from [`crate::Mesh::c60`] -- whose float construction R7 measured
/// as *correct at C60* (edge spread 1.0982, comfortably under the 1.15
/// threshold) and *broken from C380*. So this is the last honest rung of the
/// float lane, frozen into the integer lane where depth no longer costs
/// anything.
pub fn rotation_system_c60() -> Vec<usize> {
    let m = crate::Mesh::c60();
    rotation_from_faces(&m.faces).expect("C60's faces must form a closed orientable surface")
}
