//! KABOOM -- push the fractalization until the program gives up, and watch.
//!
//! # Why this is a program and not an argument
//!
//! We know the *counts* exactly: `genesis::grow` is integer arithmetic with
//! `checked_*`, so it will name the rung where `u64` runs out and never guess.
//! What we do NOT know is where the **machine** stops, and no amount of
//! reasoning produces that number -- it depends on how many bytes a `Face`
//! really costs, which depends on things nobody has measured.
//!
//! So this does not reason. It builds, measures, and when it eventually dies
//! the parent process reports how.
//!
//! ```powershell
//! cargo run --release --example kaboom            # the sweep, until it breaks
//! cargo run --release --example kaboom -- 5       # one attempt, depth 5
//! ```
//!
//! # The prediction it is testing
//!
//! Everything so far has priced meshes as `faces * 6 * 24` -- the points, and
//! nothing else. That is what `State::snapshot_bytes` reports and it is what
//! the viewer's budget is built on. This asks whether that is true, and the
//! answer decides whether every memory number we have printed is honest.
//!
//! # How a child dies, and what each death means
//!
//! A Rust allocation failure ABORTS; it does not unwind, so nothing can be
//! caught in-process. The only honest way to observe it is from outside, which
//! is why the sweep spawns itself:
//!
//! ```text
//!   exit 0           built it, and the numbers below are real
//!   exit 101         a Rust panic -- a checked_* refusal reached, by design
//!   exit 0xC0000409  abort -- the allocator gave up. THE WALL.
//!   killed / other   the OS took it. Also the wall, wearing a different hat.
//! ```

use goldberg_kernel::genesis::{self, Face, Op, Params, State};
use goldberg_kernel::rng::Rng;
use std::time::Instant;

/// What a face really costs, in bytes, counted rather than assumed.
///
/// Walks the built structure and sums the ACTUAL heap each field holds. This
/// is exact up to allocator bookkeeping -- typically 8 to 16 bytes per
/// allocation, which is itself worth knowing because a `Face` makes FOUR
/// allocations (pts, lineage, id, anchor) and that overhead is per-allocation,
/// not per-byte.
#[derive(Default, Clone, Copy)]
struct Cost {
    faces: usize,
    /// `size_of::<Face>()` times the count -- the inline part
    inline: usize,
    /// the corner points
    pts: usize,
    /// the lineage path, which GROWS one entry per level
    lineage: usize,
    /// the id string, which GROWS with depth: `F7.c33.e34.e35...`
    ids: usize,
    /// pentagons only
    anchors: usize,
    /// allocations made, so per-allocation overhead can be reasoned about
    allocs: usize,
}

impl Cost {
    fn of(s: &State) -> Cost {
        let mut c = Cost {
            faces: s.faces.len(),
            inline: s.faces.len() * std::mem::size_of::<Face>(),
            ..Default::default()
        };
        for f in &s.faces {
            c.pts += f.pts.capacity() * std::mem::size_of::<[f64; 3]>();
            c.lineage += f.lineage.capacity() * std::mem::size_of::<usize>();
            c.ids += f.id.capacity();
            c.allocs += 3;
            if let Some(a) = &f.anchor {
                c.anchors += a.capacity();
                c.allocs += 1;
            }
        }
        c
    }
    fn total(&self) -> usize {
        self.inline + self.pts + self.lineage + self.ids + self.anchors
    }
    /// What the rest of the codebase has been assuming: points only.
    fn naive(&self) -> usize {
        self.pts
    }
}

fn mb(b: usize) -> f64 {
    b as f64 / 1_048_576.0
}

/// One attempt: refine ALL, `depth` times, from the certified seed.
fn one(depth: u32) -> i32 {
    let p = Params::default();
    let mut rng = Rng::new(0x5EED);
    let mut s = State::seed_c60();

    // PREDICT FIRST, and print it before allocating, so that if this process
    // dies we still know what it was reaching for (Curse 35).
    let mut c = genesis::Census::C60;
    for _ in 0..depth {
        c = match genesis::grow(c, Op::All) {
            Ok(n) => n,
            Err(e) => {
                println!("REFUSED at depth {depth}: {e}");
                return 3;
            }
        };
    }
    println!("depth {depth}  target F={} P={}", c.f, c.p);
    println!("  reaching for it now -- if this line is the last one, the allocator won.");

    let t0 = Instant::now();
    for i in 0..depth {
        s = s.refine(Op::All, &p, &mut rng);
        // history holds a full snapshot per step and would double the cost;
        // the question here is the MESH's ceiling, not the undo stack's
        s.history.clear();
        if i + 1 == depth {
            break;
        }
    }
    let secs = t0.elapsed().as_secs_f64();

    let cost = Cost::of(&s);
    let inv = s.invariants().expect("a built shell must measure");
    println!(
        "  BUILT  F={} V={} E={} P={} chi={} in {secs:.2}s",
        inv.faces, inv.vertices, inv.edges, inv.pents, inv.chi
    );
    println!(
        "  bytes  inline {:.1} MB | pts {:.1} MB | lineage {:.1} MB | ids {:.1} MB | anchors {:.3} MB",
        mb(cost.inline),
        mb(cost.pts),
        mb(cost.lineage),
        mb(cost.ids),
        mb(cost.anchors)
    );
    println!(
        "  TOTAL  {:.1} MB   ({:.1} B/face)   allocations {}",
        mb(cost.total()),
        cost.total() as f64 / cost.faces as f64,
        cost.allocs
    );
    println!(
        "  NAIVE  {:.1} MB   ({:.1} B/face)   <- what snapshot_bytes reports",
        mb(cost.naive()),
        cost.naive() as f64 / cost.faces as f64
    );
    println!(
        "  RATIO  the real cost is {:.2}x the points alone",
        cost.total() as f64 / cost.naive().max(1) as f64
    );
    0
}

/// Spawn ourselves at increasing depth until a child fails to come back.
fn sweep() -> i32 {
    let exe = match std::env::current_exe() {
        Ok(e) => e,
        Err(e) => {
            eprintln!("cannot find myself: {e}");
            return 2;
        }
    };
    println!("KABOOM -- pushing until it gives up");
    println!("each depth runs in its OWN process, because an allocation failure");
    println!("aborts and cannot be caught from inside the process that caused it.");
    println!();

    let mut last_good = 0u32;
    for depth in 1..=9u32 {
        print!("depth {depth} ... ");
        use std::io::Write as _;
        let _ = std::io::stdout().flush();

        let out = std::process::Command::new(&exe)
            .arg(depth.to_string())
            .output();
        match out {
            Ok(o) if o.status.success() => {
                last_good = depth;
                println!("ok");
                for line in String::from_utf8_lossy(&o.stdout).lines() {
                    if line.starts_with("  ") {
                        println!("  {line}");
                    }
                }
            }
            Ok(o) => {
                let code = o.status.code();
                println!("DIED");
                for line in String::from_utf8_lossy(&o.stdout).lines() {
                    println!("      | {line}");
                }
                let err = String::from_utf8_lossy(&o.stderr);
                for line in err.lines().take(6) {
                    println!("      ! {line}");
                }
                println!();
                println!(
                    "  exit code {}",
                    match code {
                        Some(c) => format!("{c} (0x{:08X})", c as u32),
                        None => String::from("none -- the OS took it"),
                    }
                );
                println!(
                    "  verdict   {}",
                    match code {
                        Some(101) => "a Rust panic -- a guard fired, BY DESIGN",
                        Some(3) => "the integer census refused before allocating -- the good wall",
                        Some(c) if c as u32 == 0xC000_0409 => {
                            "abort -- the allocator gave up. THE MACHINE'S WALL."
                        }
                        Some(c) if c as u32 == 0xC000_0005 => "access violation",
                        _ => "unclassified -- write down what it was",
                    }
                );
                println!();
                println!("  deepest that survived: depth {last_good}");
                return 0;
            }
            Err(e) => {
                println!("could not spawn: {e}");
                return 2;
            }
        }
        println!();
    }
    println!("reached depth 9 without dying, which was not the plan");
    0
}

fn main() {
    let code = match std::env::args().nth(1) {
        Some(a) => match a.parse::<u32>() {
            Ok(d) => one(d),
            Err(_) => {
                eprintln!("usage: kaboom [depth]");
                2
            }
        },
        None => sweep(),
    };
    std::process::exit(code);
}
