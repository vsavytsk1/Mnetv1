//! `pentagon_map` -- the mage's hypothesis, re-certified in Rust.
//!
//! `tower/pentagon_map_v0_1.py` states it:
//!
//! > adjacent pentagon hop distance = `max(|k|, |l|, |k+l|)`
//!
//! and its receipt reports 10 shells tested, 10 matching -- on the golden lane
//! `(1,1) (2,1) (3,2) (5,3) (8,5)` and four off-lane pairs.
//!
//! # WHAT THIS ADDS RATHER THAN REPEATS
//!
//! The Python covered the golden lane. `Ico::dual` produces `GP(2^L, 0)` -- the
//! DOUBLING lane, `T = 4^L` -- which its table touches only at `(1,0)`. So
//! these are new points on the same claim:
//!
//! ```text
//!   (1,0) (2,0) (4,0) (8,0) (16,0) (32,0) (64,0)
//!   closed form max(k, 0, k) = k = 2^L
//! ```
//!
//! and the shared row `(1,0)` is the check that the two labs agree at all: the
//! Python measured min 1, max 3 there, and so must this.
//!
//! # THE LANE
//!
//! Run on the **closed** shell, never on the crescent soup. Hop distance needs
//! a surface where every edge has two faces; `examples/whats_open` measured 540
//! unpaired edges at genesis level 1, so BFS there would be walking a mesh with
//! 180 holes in it and calling the result a distance.
//!
//! `cargo run --release --example pentagon_map [max_level]`

use goldberg_kernel::sphere::Ico;

/// The hypothesis, as a function of `(k, l)` rather than of this one lane.
///
/// `max(|k|, |l|, |k+l|)`. Written general so step 3's `(k,l)` selector can
/// call the same line -- and because `max(k, 0, k)` with `l` pinned to zero is
/// two dead comparisons wearing the shape of a formula, which clippy said
/// plainly and was right about.
fn closed_form(k: i64, l: i64) -> i64 {
    k.abs().max(l.abs()).max((k + l).abs())
}

fn main() {
    let maxl: u32 = std::env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(6);

    println!("  PENTAGON MAP -- the doubling lane GP(2^L, 0)\n");
    println!("  hypothesis: adjacent pentagon hop distance = max(|k|, |l|, |k+l|)\n");
    println!(
        "  {:>3} {:>6} {:>6} {:>9} {:>6} {:>6} {:>11} {:>9}",
        "L", "k", "T", "V", "min", "max", "closed form", "matches"
    );

    let mut tested = 0usize;
    let mut matched = 0usize;

    for l in 0..=maxl {
        let ico = match Ico::level(l) {
            Ok(i) => i,
            Err(e) => {
                println!("  {l:>3}  REFUSED -- {e}");
                break;
            }
        };
        let g = ico.dual();
        let Some((lo, hi)) = g.pentagon_span() else {
            println!("  {l:>3}  no pentagon pair -- impossible on a fullerene");
            break;
        };

        // GP(2^L, 0): k = 2^L, l = 0
        let k = 1i64 << l;
        let closed = closed_form(k, 0) as usize;
        let ok = closed == lo;
        tested += 1;
        matched += usize::from(ok);

        println!(
            "  {:>3} {:>6} {:>6} {:>9} {:>6} {:>6} {:>11} {:>9}",
            l,
            k,
            4u64.pow(l),
            g.verts.len(),
            lo,
            hi,
            closed,
            if ok { "yes" } else { "NO" }
        );
    }

    println!("\n  {matched} of {tested} shells match the closed form on the MINIMUM.");
    if matched == tested {
        println!("  The hypothesis survives the doubling lane as well as the golden one.");
    } else {
        println!("  THE CLOSED FORM IS NOT THE ADJACENT PENTAGON DISTANCE HERE.");
        println!("  Read the measured min; the receipt's own note says exactly this.");
    }

    println!("\n  THE SHARED ROW, against tower/pentagon_map_v0_1_receipt.json:");
    println!("    (1,0)  python: min 1, max 3, closed form 1");
    let g0 = Ico::level(0).expect("the base fits").dual();
    match g0.pentagon_span() {
        Some((lo, hi)) => println!("    (1,0)  rust:   min {lo}, max {hi}, closed form 1"),
        None => println!("    (1,0)  rust:   no pair"),
    }
    println!("\n  Two labs, two languages, one dodecahedron. The max is reported beside");
    println!("  the min on purpose -- a closed form that matched the MAX instead would");
    println!("  be a different claim, and printing only the number you predicted is how");
    println!("  a hypothesis gets confirmed by its own reader.");
}
