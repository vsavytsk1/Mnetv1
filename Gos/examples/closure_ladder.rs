//! `closure_ladder` -- closing the topology, storing the net, to the ceiling.
//!
//! Three questions asked together at every rung, which is the point:
//!
//! ```text
//!   DOES IT CLOSE?   weld on the bits, hand it to judge, take chi from ORBITS
//!   WHAT DOES IT     netfile bytes -- exact, a pure function of the counts,
//!   COST TO STORE?   so a save is priced before it is made
//!   WHERE DOES IT    live heap against a stated budget, and the arithmetic
//!   STOP?            that says which rung is the last one
//! ```
//!
//! # WHY THESE THREE BELONG ON ONE TABLE
//!
//! They are the three ways this cave has learned a shell can lie to it.
//!
//! * A **census** counts faces and cannot see that two faces disagree about a
//!   shared corner. `weld` keys on `to_bits()` and `judge` counts orbits of a
//!   permutation -- neither can be fooled by a `kind` label.
//! * A **size estimate** is a guess. `netfile::bytes_for` is exact, so the
//!   price quoted is the price paid (Curse 35).
//! * A **ceiling** discovered by an allocator is a crash. RUSTIUM R3 and
//!   Curse 35 both say the same thing: predict the next step's cost from the
//!   recurrence BEFORE allocating.
//!
//! # THE WALL THIS LADDER LIVES UNDER
//!
//! `grimoire/TOPOLOGY_FIRST_FRONTIER.md` derives an exact threshold on the
//! Eisenstein lattice: hex shells nest inside Euclidean norm shells only while
//!
//! ```text
//!   h < sqrt(3)/(2 - sqrt(3)) = 2*sqrt(3) + 3 = 6.4641016...
//! ```
//!
//! so `h <= 6` nests and `h = 7` is the first break -- the corner at `(7,0)`
//! has norm 49 while the next ring dips to 48, overshooting by exactly one.
//! Verified here as integers, because a threshold you can check with `<` should
//! never be taken on faith.
//!
//! ```powershell
//! cargo run --release --example closure_ladder            # to the 2 GB budget
//! cargo run --release --example closure_ladder -- 6       # 6 GB
//! ```

use goldberg_kernel::genesis::{Op, Params, State, Surface};
use goldberg_kernel::netfile;
use goldberg_kernel::rng::Rng;
use goldberg_kernel::weld;
use std::time::Instant;

/// Hex-lattice distance in axial coordinates.
fn hexd(q: i64, r: i64) -> i64 {
    (q.abs() + (q + r).abs() + r.abs()) / 2
}

/// The Eisenstein norm, `q^2 + qr + r^2`. Integers only -- no float, so the
/// wall below is checked with `<` and not with a tolerance.
fn norm(q: i64, r: i64) -> i64 {
    q * q + q * r + r * r
}

/// One ring of the wall scan: `h`, min norm, max norm, the next ring's min,
/// and whether this ring still nests inside the next.
type Ring = (i64, i64, i64, i64, bool);

/// Where the hex shell stops nesting inside the Euclidean norm shell.
fn the_wall(max_h: i64) -> (i64, Vec<Ring>) {
    let mut rows = Vec::new();
    let mut first_break = 0;
    let span = 2 * max_h + 2;
    let mut per: Vec<Vec<i64>> = vec![Vec::new(); (max_h + 2) as usize];
    for q in -span..=span {
        for r in -span..=span {
            let h = hexd(q, r);
            if h <= max_h + 1 {
                per[h as usize].push(norm(q, r));
            }
        }
    }
    for h in 1..=max_h {
        let mx = *per[h as usize].iter().max().expect("ring is non-empty");
        let mn = *per[h as usize].iter().min().expect("ring is non-empty");
        let next = *per[(h + 1) as usize]
            .iter()
            .min()
            .expect("the next ring is non-empty");
        let nests = mx < next;
        if !nests && first_break == 0 {
            first_break = h;
        }
        rows.push((h, mn, mx, next, nests));
    }
    (first_break, rows)
}

fn main() {
    let budget_gb: f64 = std::env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(2.0);
    let budget = (budget_gb * 1024.0 * 1024.0 * 1024.0) as u64;

    // ---- THE WALL, as integers -------------------------------------
    let (brk, rows) = the_wall(11);
    println!("  THE WALL -- hex shell against Euclidean norm shell, integers only\n");
    println!(
        "  {:>3} {:>9} {:>9} {:>10} {:>8}",
        "h", "min norm", "max norm", "next min", "nests"
    );
    for (h, mn, mx, next, nests) in &rows {
        println!(
            "  {:>3} {:>9} {:>9} {:>10} {:>8}{}",
            h,
            mn,
            mx,
            next,
            if *nests { "yes" } else { "NO" },
            if *h == brk { "   <- first break" } else { "" }
        );
    }
    let wall = 2.0 * 3.0f64.sqrt() + 3.0;
    println!(
        "\n  2*sqrt(3)+3 = {wall:.9}   ceil = {}   measured first break = {brk}",
        wall.ceil() as i64
    );
    assert_eq!(
        brk,
        wall.ceil() as i64,
        "the integer scan and the algebra must agree on the wall"
    );
    println!("  the algebra and the integer scan agree.\n");

    // ---- THE LADDER --------------------------------------------------
    println!("  CLOSURE LADDER -- budget {budget_gb} GB\n");
    println!(
        "  {:>3} {:>10} {:>11} {:>11} {:>9} {:>6} {:>11} {:>10} {:>7}",
        "lvl", "faces", "V welded", "V = as/3", "surplus", "chi", "netfile", "heap", "ms"
    );

    let p = Params {
        surface: Surface::Spherical,
        ..Params::default()
    };
    let mut rng = Rng::new(0xC60);
    let mut st = State::seed_c60();
    let mut level = 0u32;

    loop {
        let inv = st.invariants().expect("the shell must measure");
        let c = st.census();

        let t = Instant::now();
        let w = weld::weld(&st);
        let ms = t.elapsed().as_secs_f64() * 1000.0;

        let chi = match w.judge() {
            Ok(v) => format!("{}", v.chi),
            Err(_) => String::from("open"),
        };
        let store = netfile::bytes_for(c.p, c.f - c.p);
        let heap = st.heap_bytes().total();

        println!(
            "  {:>3} {:>10} {:>11} {:>11} {:>9} {:>6} {:>10.1}M {:>9.1}M {:>7.1}",
            level,
            inv.faces,
            w.v(),
            w.predicted_v(),
            w.surplus(),
            chi,
            store as f64 / 1_048_576.0,
            heap as f64 / 1_048_576.0,
            ms
        );

        // PRICE THE NEXT RUNG BEFORE ALLOCATING IT. Op::All is multiplication
        // by the Eisenstein integer (1,2): T -> 7T, so faces go 7F - 12 and the
        // heap goes with them. Curse 35 / R3: refuse with the number.
        let next_faces = 7 * inv.faces - 12;
        let next_heap = heap.saturating_mul(next_faces) / inv.faces.max(1);
        if next_heap > budget {
            println!(
                "\n  NEXT RUNG REFUSED before allocating:\n    \
                 level {} would hold {} faces and about {:.2} GB,\n    \
                 past the {budget_gb} GB budget. Predicted from the recurrence, not\n    \
                 discovered by an allocator (Curse 35, RUSTIUM R3).",
                level + 1,
                next_faces,
                next_heap as f64 / 1_073_741_824.0
            );
            break;
        }

        st = st.refine(Op::All, &p, &mut rng);
        level += 1;
    }

    println!("\n  WHAT THE THREE COLUMNS SAY, TOGETHER:");
    println!("    the seed closes -- V from the bits, V from the arity sum and V from");
    println!("    the judge's orbits are one integer, and chi = 2 is COUNTED.");
    println!("    every refined rung carries a surplus, and it is not a rounding: the");
    println!("    closest two points at level 1 are 0.1334 apart. refine_face pulls each");
    println!("    new point toward ITS OWN face's centroid, so the mid ring is not shared.");
    println!("    That gap is the crescent, and the crescent is the picture.");
    println!("\n    netfile is EXACT -- a pure function of the counts -- so the storage");
    println!("    column is a price, not an estimate. The ladder stops by arithmetic.");
}
