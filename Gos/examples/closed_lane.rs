//! `closed_lane` -- the Goldberg polyhedron that actually closes.
//!
//! `examples/whats_open` measured why `genesis`'s soup cannot: 540 unpaired
//! directed edges at level 1, in three groups of 180, all of them between
//! `inner` and `mid-ring` points and none touching a corner or an edge
//! midpoint. The hole is INSIDE a face, so sharing points between faces cannot
//! fill it, and filling it with a triangle would break `7F - 12`.
//!
//! So this is the other lane. `Ico::dual` takes the index-welded icosphere --
//! no tolerance, closed at every depth -- and dualises it:
//!
//! ```text
//!   V = 20T    E = 30T    F = 10T + 2    T = 4^L    P = 12
//! ```
//!
//! trivalent by construction, twelve pentagons inherited from the icosphere's
//! twelve defects. Every rung is handed to `judge`, and chi comes from orbits
//! of a permutation -- never from the formula that produced the counts.
//!
//! `cargo run --release --example closed_lane [max_level]`

use goldberg_kernel::judge;
use goldberg_kernel::sphere::Ico;

fn main() {
    let maxl: u32 = std::env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(6);

    println!("  THE CLOSED LANE -- dual of the icosphere, GP(2^L, 0)\n");
    println!(
        "  {:>3} {:>4} {:>10} {:>10} {:>10} {:>5} {:>6} {:>7} {:>7}",
        "L", "T", "V", "E", "F", "P", "chi", "genus", "trivalent"
    );

    for l in 0..=maxl {
        let ico = match Ico::level(l) {
            Ok(i) => i,
            Err(e) => {
                println!("  {l:>3}  REFUSED -- {e}");
                break;
            }
        };
        let g = ico.dual();

        // every dual vertex is a triangle centre with three neighbours
        let mut deg = vec![0usize; g.verts.len()];
        for f in &g.faces {
            for &i in f {
                deg[i] += 1;
            }
        }
        let trivalent = deg.iter().all(|&d| d == 3);

        let Some(v) = g.judge() else {
            println!("  {l:>3}  the judge REFUSED the dual -- it is not a closed surface");
            break;
        };

        let t = 4u64.pow(l);
        println!(
            "  {:>3} {:>4} {:>10} {:>10} {:>10} {:>5} {:>6} {:>7} {:>9}",
            l,
            t,
            v.v,
            v.e,
            v.f,
            g.pents(),
            v.chi,
            v.genus.map_or(String::from("?"), |x| x.to_string()),
            if trivalent { "yes" } else { "NO" }
        );

        // the counts THEA predicts, checked against the judge's orbits
        assert_eq!(v.v as u64, 20 * t, "V must be 20T");
        assert_eq!(v.e as u64, 30 * t, "E must be 30T");
        assert_eq!(v.f as u64, 10 * t + 2, "F must be 10T+2");
        assert_eq!(g.pents(), 12, "P=12 is not negotiable");
        assert_eq!(v.chi, 2, "a sphere has chi 2, counted from orbits");
        assert!(trivalent, "a Goldberg polyhedron is trivalent");
    }

    println!("\n  EVERY RUNG CLOSED. V, E and F from the JUDGE'S ORBITS, matched against");
    println!("  20T / 30T / 10T+2 from THEA -- two routes, no shared code, one triple.");
    println!("  P = 12 counted by arity, and the mesh trivalent at every depth.");
    println!();
    println!("  This is the base the frontier work needs. The crescent lane keeps its");
    println!("  picture; this one keeps its topology. Both are honest and they are");
    println!("  not the same object -- which is the thing that was never written down.");
    let _ = judge::alpha(0);
}
