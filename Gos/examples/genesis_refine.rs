//! GENESIS step 2 -- the operator, walked up the browser's own ladder.
//!
//! Proof by kernel, not by claim. This builds real polygons at every rung and
//! grades them against the integer census, which never allocates a point. Two
//! independent derivations of the same number; if the operator is wrong, they
//! part company and this prints the disagreement instead of a tidy table.
//!
//! ```powershell
//! cargo +stable-x86_64-pc-windows-gnu run --example genesis_refine
//! ```

use goldberg_kernel::genesis::{Op, Params, State};
use goldberg_kernel::rng::Rng;

fn main() {
    let p = Params::default();
    let mut rng = Rng::new(0x5EED);

    println!("GENESIS STEP 2 -- THE OPERATOR");
    println!("source: shell/genesis_v8.5.2.html  GK.refineFace / refineAll / undo");
    println!(
        "params: inner {} mid {} jitter {} ({:?})",
        p.inner_scale, p.mid_scale, p.jitter, p.surface
    );
    println!();
    println!(
        "{:<5} {:>9} {:>9} {:>4} {:>9} {:>9} {:>4} {:>8} {:>6} {:>9}",
        "op", "F pred", "F built", "P", "V", "E", "chi", "anchors", "depth", "undo KB"
    );
    println!("{}", "-".repeat(84));

    let mut s = State::seed_c60();
    let i = s.invariants().expect("the seed must measure");
    println!(
        "{:<5} {:>9} {:>9} {:>4} {:>9} {:>9} {:>4} {:>8} {:>6} {:>9}",
        "seed",
        "-",
        i.faces,
        i.pents,
        i.vertices,
        i.edges,
        i.chi,
        i.anchor_count,
        i.max_level,
        s.snapshot_bytes() / 1024
    );

    // the browser's logged run: ALL, then 6s four times. Every rung is a real
    // mesh, not a formula.
    let mut disagreements = 0usize;
    for op in [Op::All, Op::Hex, Op::Hex, Op::Hex, Op::Pent] {
        let predicted = match s.predict(op) {
            Ok(c) => c,
            Err(e) => {
                println!("REFUSED at {}: {e}", op.label());
                break;
            }
        };
        s = s.refine(op, &p, &mut rng);
        let i = s.invariants().expect("a refined shell must measure");
        let flag = if i.faces == predicted.f && i.pents == predicted.p {
            ""
        } else {
            disagreements += 1;
            "   <-- LANES DISAGREE"
        };
        println!(
            "{:<5} {:>9} {:>9} {:>4} {:>9} {:>9} {:>4} {:>8} {:>6} {:>9}{}",
            op.label(),
            predicted.f,
            i.faces,
            i.pents,
            i.vertices,
            i.edges,
            i.chi,
            i.anchor_count,
            i.max_level,
            s.snapshot_bytes() / 1024,
            flag
        );
    }

    println!();
    // UNDO, all the way back to the seed. The faces must come back EXACTLY.
    let depth = s.history.len();
    let mut back = s.clone();
    while let Some(prev) = back.undo() {
        back = prev;
    }
    println!(
        "UNDO x{depth} -> {} faces, counter {} (NOT rolled back -- ids are never reused)",
        back.faces.len(),
        back.counter
    );
    assert_eq!(back.faces, State::seed_c60().faces, "undo must be exact");
    println!("undo restored the seed's faces bit for bit.");

    println!();
    println!("disagreements between the integer lane and the built mesh: {disagreements}");
    println!("chi is COUNTED from trivalence at every rung, never assumed from Euler.");
    println!("P=12 . chi=2 . counting is not closing.");

    if disagreements > 0 {
        std::process::exit(1);
    }
}
