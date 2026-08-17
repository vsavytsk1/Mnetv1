//! THE EML GENERATOR -- enumerate every descent, log every attempt.
//!
//! ```text
//!   eml(x, y) = exp(x) - ln(y)
//!   S -> 1 | eml(S, S)
//! ```
//!
//! Closed terms of size `n` are counted by Catalan `C_n`, so the space is
//! exhaustible for a while. This walks it in order of increasing price and
//! reports what each term lands on.
//!
//! ```powershell
//! cargo run --release --example eml_search           # K <= 8
//! cargo run --release --example eml_search -- 10     # deeper
//! ```

use goldberg_kernel::eml::{self, catalan, Term, TARGETS};

fn main() {
    let max_k: usize = std::env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(8);
    let tol = 1e-9;

    println!("{}", "=".repeat(84));
    println!("  THE EML GENERATOR -- one operator, one constant, every descent");
    println!("{}", "=".repeat(84));
    println!("    eml(x, y) = exp(x) - ln(y)");
    println!("    S -> 1 | eml(S, S)");
    println!();

    // the price of the sweep, BEFORE paying it (Curse 35)
    let mut total = 0u64;
    println!("  {:>3}  {:>14}  {:>18}", "K", "terms (Catalan)", "cumulative");
    for k in 0..=max_k {
        total += catalan(k);
        println!("  {k:>3}  {:>14}  {total:>18}", catalan(k));
    }
    println!("\n  sweeping {total} terms at tol {tol:e}\n");

    let sw = eml::sweep(max_k, tol);

    println!("{}", "-".repeat(84));
    println!("  KNOWN ONES -- did the generator rediscover them?");
    println!("{}", "-".repeat(84));
    println!(
        "  {:<6} {:<18} {:>5} {:>5}  chain",
        "sym", "name", "K", "known"
    );
    for tg in TARGETS {
        let hit = sw.hits.iter().find(|h| h.target == Some(tg.sym));
        match hit {
            Some(h) => {
                let known = tg
                    .known_k
                    .map(|k| k.to_string())
                    .unwrap_or_else(|| String::from("-"));
                let mark = if h.shorter { "  <== SHORTER THAN KNOWN" } else { "" };
                println!(
                    "  {:<6} {:<18} {:>5} {:>5}  {}{}",
                    tg.sym,
                    tg.name,
                    h.k,
                    known,
                    trunc(&h.chain, 34),
                    mark
                );
            }
            None => println!(
                "  {:<6} {:<18} {:>5} {:>5}  not reached at K <= {}",
                tg.sym,
                tg.name,
                "-",
                tg.known_k.map(|k| k.to_string()).unwrap_or_else(|| String::from("-")),
                max_k
            ),
        }
    }

    println!("\n{}", "-".repeat(84));
    println!("  THE SWEEP");
    println!("{}", "-".repeat(84));
    println!("  terms visited     {}", sw.terms_visited);
    println!("  finite values     {}", sw.finite);
    println!(
        "  non-finite        {}   (the ln 0 = -inf lane, kept not crashed)",
        sw.terms_visited - sw.finite
    );
    println!("  distinct reals    {}", sw.distinct_values);
    println!("  targets hit       {}/{}", sw.hits.len(), TARGETS.len());
    println!(
        "  shorter than known {}",
        sw.hits.iter().filter(|h| h.shorter).count()
    );

    // the seed chains from the spiral, verified directly
    println!("\n{}", "-".repeat(84));
    println!("  THE SPIRAL'S OWN CHAINS, EVALUATED HERE");
    println!("{}", "-".repeat(84));
    let one = || Term::One;
    let eml = |a: Term, b: Term| Term::Eml(Box::new(a), Box::new(b));

    // e = eml(1,1)
    let e_term = eml(one(), one());
    show("e = eml(1,1)", &e_term, std::f64::consts::E);

    // e^e = eml(eml(1,1), 1)
    let ee = eml(eml(one(), one()), one());
    show("eml(eml(1,1),1)", &ee, std::f64::consts::E.exp());

    println!("\n  NOTE: evaluation is the DISPLAY lane -- exp and ln are not");
    println!("  correctly rounded and the branch cut is a choice, so a match is");
    println!("  EVIDENCE of a descent, not a proof of one. The spiral verifies");
    println!("  its chains at many samples for exactly this reason.");
}

fn show(label: &str, t: &Term, expect: f64) {
    let v = t.eval();
    let err = (v.re - expect).abs();
    println!(
        "  {:<22} K={:<3} -> {:>18.12}  expect {:>18.12}  err {:.2e}",
        label,
        t.k(),
        v.re,
        expect,
        err
    );
}

fn trunc(s: &str, n: usize) -> String {
    if s.chars().count() <= n {
        s.to_string()
    } else {
        s.chars().take(n - 1).chain("~".chars()).collect()
    }
}
