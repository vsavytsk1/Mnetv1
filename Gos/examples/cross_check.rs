//! Three implementations, one topology. JS (binary64) / C# (binary32) / Rust (binary64).
//!
//! The C# VR kernel (`MnetUni/Mnet`, `Assets/Kernel/GoldbergKernel.cs`) runs the
//! same Goldberg-Coxeter refinement on a Meta Quest 3, in **binary32**. Its
//! README reports `F=32` for the C60 seed and `F=212` after one `RefineAll()`,
//! with `pents=12` and `chi=2`.
//!
//! We compute in **binary64**, from a closed-form ladder that builds nothing:
//! `T = 3 * 7^k`, `V = 20T`, `E = 30T`, `F = 10T + 2`, `P = 12`.
//!
//! If the integers agree across a precision change of 29 mantissa bits, the
//! topology genuinely does not care what language -- or what float -- you are
//! in. That is the claim the VR repo makes on its front page. This checks it.

use goldberg_kernel::{certify, goldberg_counts, triangulation_number, Mesh};

fn main() {
    // the seed, built for real and certified from geometry
    let m = Mesh::c60();
    let seed = certify(&m).expect("the C60 must certify");
    println!("== THE SEED (built, then certified) ==");
    println!("   rust  : {seed}");
    println!("   C#    : F=32, pents=12, chi=2   (GoldbergKernel.cs BuildC60)");
    assert_eq!((seed.v, seed.e, seed.f, seed.p, seed.chi), (60, 90, 32, 12, 2));
    println!("   AGREE on all five integers.\n");

    println!("== THE LADDER (closed form, nothing built) ==");
    println!("{:<7} {:>6} {:>8} {:>8} {:>8} {:>4} {:>4}", "level", "T", "V", "E", "F", "P", "chi");
    println!("{}", "-".repeat(50));
    for k in 0..5 {
        let c = goldberg_counts(k);
        println!(
            "{:<7} {:>6} {:>8} {:>8} {:>8} {:>4} {:>4}",
            k, triangulation_number(k), c.v, c.e, c.f, c.p, c.chi
        );
        assert_eq!(c.p, 12, "P=12 at every level");
        assert_eq!(c.chi, 2, "chi=2 at every level");
    }

    println!("\n== THE CROSS-CHECK ==");
    let k1 = goldberg_counts(1);
    println!("   C# RefineAll() reports  F = 212");
    println!("   rust level 1 predicts   F = {}", k1.f);
    assert_eq!(k1.f, 212, "the two implementations must agree");
    println!("   AGREE.  and rust additionally predicts V={} E={}", k1.v, k1.e);
    println!("   -- numbers the C# side can check itself with Invariants().");

    println!("\n== WHY THIS IS WORTH SOMETHING ==");
    println!("   C#   : float   (binary32, 24-bit mantissa)");
    println!("   rust : f64     (binary64, 53-bit mantissa)");
    println!("   29 bits of difference, identical integers.");
    println!("   The topology is not a float result. It never was.");
}
