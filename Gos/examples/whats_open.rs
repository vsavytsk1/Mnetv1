//! `whats_open` -- exactly which edges have no twin, and what would close them.
//!
//! Before rebuilding `refine_face` to "share the mid ring", measure whether
//! that would close anything. The card reports level 1 as OPEN with 510 points
//! against the 420 trivalence predicts; this asks the finer question:
//!
//! ```text
//!   WHICH directed edges have no twin, and between WHICH KINDS of point?
//! ```
//!
//! Because a surface is closed exactly when every directed edge `(a,b)` has a
//! partner `(b,a)`. Counting unpaired edges by the kind of their endpoints says
//! what the hole is SHAPED like, and therefore what would actually fill it.
//!
//! `cargo run --release --example whats_open`

use goldberg_kernel::genesis::{Op, Params, State, Surface};
use goldberg_kernel::rng::Rng;
use goldberg_kernel::weld;
use std::collections::{HashMap, HashSet};

/// What a welded point was, recovered from how many faces meet at it.
///
/// Measured at level 1 and stated in `src/weld.rs`: 180 points of degree 1
/// (the mid ring), 90 of degree 2 (the raw edge midpoints), 180 of degree 3
/// (the inner rings) and 60 of degree 6 (the original C60 corners).
fn kind_of(deg: usize) -> &'static str {
    match deg {
        1 => "mid-ring",
        2 => "edge-mid",
        3 => "inner",
        6 => "corner",
        _ => "other",
    }
}

fn main() {
    let p = Params {
        surface: Surface::Spherical,
        ..Params::default()
    };
    let mut rng = Rng::new(0xC60);
    let st = State::seed_c60().refine(Op::All, &p, &mut rng);
    let w = weld::weld(&st);

    let mut deg = vec![0usize; w.v()];
    for f in &w.faces {
        for &i in f {
            deg[i] += 1;
        }
    }

    // every directed edge, and whether its reverse exists
    let mut dir: HashSet<(usize, usize)> = HashSet::new();
    for f in &w.faces {
        for i in 0..f.len() {
            dir.insert((f[i], f[(i + 1) % f.len()]));
        }
    }
    let unpaired: Vec<(usize, usize)> = dir
        .iter()
        .copied()
        .filter(|&(a, b)| !dir.contains(&(b, a)))
        .collect();

    println!("  WHAT IS OPEN AT LEVEL 1\n");
    println!("  points      {}", w.v());
    println!("  faces       {}", w.faces.len());
    println!("  directed edges  {}", dir.len());
    println!("  UNPAIRED        {}\n", unpaired.len());

    let mut by_kind: HashMap<(&str, &str), usize> = HashMap::new();
    for &(a, b) in &unpaired {
        by_kind
            .entry((kind_of(deg[a]), kind_of(deg[b])))
            .and_modify(|c| *c += 1)
            .or_insert(1);
    }
    let mut rows: Vec<_> = by_kind.into_iter().collect();
    rows.sort_by_key(|r| std::cmp::Reverse(r.1));
    println!("  {:>10} -> {:<10} {:>7}", "from", "to", "count");
    for ((a, b), n) in &rows {
        println!("  {a:>10} -> {b:<10} {n:>7}");
    }

    println!("\n  READ IT AS A SHAPE:");
    println!("    an inner ring runs inner[i] -> inner[j] around the inner face.");
    println!("    the cell beside it runs inner[j] -> mid -> inner[i], the LONG way.");
    println!("    so the triangle (inner[i], mid, inner[j]) is a HOLE -- three edges,");
    println!("    none of them paired. That hole IS the crescent.");
    println!();
    println!("  WHAT 'SHARING THE MID RING' WOULD ACTUALLY DO:");
    println!("    it would merge 180 mid-ring points into 90, so V would fall from");
    println!("    510 to 420 -- which is arity_sum/3 exactly, and would LOOK closed.");
    println!("    But the hole is not between the two copies of the mid point. It is");
    println!("    between the inner ring and the cell, INSIDE one face, and merging a");
    println!("    point across two faces does not fill a hole that lies within each.");
    println!();
    println!("    Filling it needs a FACE -- one triangle per face-edge -- and that");
    println!("    changes the face count from 7F-12 to something else, which breaks");
    println!("    the growth law the browser and the tests both hold to.");
    println!();
    println!("  SO: the crescent cannot be closed by welding harder. It is closed by");
    println!("  a DIFFERENT OPERATOR, and Op::All must keep producing exactly what it");
    println!("  produces today (README: the crescent is the picture, not a bug).");
}
