//! `net_cache` -- every net is built from the one before it, so keep them.
//!
//! THE IDEA: level N is `refine(level N-1)`. If N-1 is already carved into
//! bytes, there is no reason to rebuild it from the seed -- the round trip is
//! **bit-identical** (`netfile_round_trip_is_bit_identical`), so a loaded
//! level is not an approximation of a computed one, it IS it. The f64 bits
//! that come back are the same f64 bits that went out, which is the whole gift
//! IEEE-754 hands you for free.
//!
//! So: cache each level as it is built, and start the next run from the
//! deepest one on disk.
//!
//! ```text
//!   cargo run --release --example net_cache -- 6         # build to 6, caching
//!   cargo run --release --example net_cache -- 6         # again -- resumes
//!   cargo run --release --example net_cache -- 6 clear   # forget everything
//! ```
//!
//! LANE: face counts EXACT, milliseconds COMPUTED on this machine this run.

use goldberg_kernel::genesis::{Op, Params, State, Surface};
use goldberg_kernel::netfile;
use goldberg_kernel::rng::Rng;
use std::fs;
use std::path::PathBuf;
use std::time::Instant;

fn dir() -> PathBuf {
    let d = std::env::temp_dir().join("gos_netcache");
    let _ = fs::create_dir_all(&d);
    d
}

fn path(lvl: u32) -> PathBuf {
    dir().join(format!("c60_lvl{lvl}.gosnet"))
}

fn ms(t: Instant) -> f64 {
    t.elapsed().as_secs_f64() * 1000.0
}

fn main() {
    let target: u32 = std::env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(5);
    if std::env::args().any(|a| a == "clear") {
        let _ = fs::remove_dir_all(dir());
        println!("  cache cleared\n");
    }

    // ---- what is already on disk -----------------------------------------
    let mut deepest = 0u32;
    for l in (1..=target).rev() {
        if path(l).exists() {
            deepest = l;
            break;
        }
    }

    let p = Params::default();
    let mut rng = Rng::new(0xC60);
    let mut total = 0.0;

    let mut st = if deepest == 0 {
        println!("  COLD -- nothing cached, starting from the seed\n");
        State::seed_c60()
    } else {
        let t = Instant::now();
        let raw = fs::read(path(deepest)).expect("read cache");
        let (s, _) = netfile::from_bytes(&raw).expect("parse cache");
        let took = ms(t);
        total += took;
        println!(
            "  WARM -- resuming from cached level {deepest}\n\
             \x20   loaded {} faces in {:.1} ms ({:.2} MB)\n",
            s.faces.len(),
            took,
            raw.len() as f64 / 1_048_576.0
        );
        s
    };

    println!(
        "  {:<5} {:>10} {:>11} {:>10} {:>10}",
        "lvl", "faces", "action", "ms", "cum ms"
    );
    if deepest > 0 {
        println!(
            "  {:<5} {:>10} {:>11} {:>10.1} {:>10.1}",
            deepest,
            st.faces.len(),
            "LOADED",
            total,
            total
        );
    }

    for lvl in (deepest + 1)..=target {
        let t = Instant::now();
        st = st.refine(Op::All, &p, &mut rng);
        let build = ms(t);
        total += build;

        // cache it immediately: a level built and not kept is a level that
        // will be built again
        let t = Instant::now();
        let bytes = netfile::to_bytes(&st, Surface::Spherical);
        fs::write(path(lvl), &bytes).expect("write cache");
        let saved = ms(t);
        total += saved;

        println!(
            "  {:<5} {:>10} {:>11} {:>10.1} {:>10.1}   (+{:.1} ms cached)",
            lvl,
            st.faces.len(),
            "BUILT",
            build,
            total,
            saved
        );
    }

    // the mesh must be the same mesh however it got here
    let c = st.census();
    let inv = st.invariants().expect("measures");
    println!(
        "\n  RESULT  F={} P={} chi={}  {}",
        c.f,
        c.p,
        inv.chi,
        if inv.faces == c.f && inv.pents == c.p {
            "LANES AGREE"
        } else {
            "LANES DISAGREE"
        }
    );
    println!("  TOTAL   {total:.1} ms");

    let held: u64 = (1..=target)
        .filter_map(|l| fs::metadata(path(l)).ok().map(|m| m.len()))
        .sum();
    println!(
        "  CACHE   {} levels on disk, {:.2} MB in {}",
        (1..=target).filter(|l| path(*l).exists()).count(),
        held as f64 / 1_048_576.0,
        dir().display()
    );
    println!("\n  run it again -- it will resume from level {target}");
}
