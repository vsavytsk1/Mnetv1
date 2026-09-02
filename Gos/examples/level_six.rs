//! `level_six` -- go one level deeper than the viewer allows, and measure it.
//!
//! The viewer refuses level 6: `refine_peak_bytes` projects ~10.78 GB against a
//! 6 GB ceiling. That refusal is correct policy for a window you want to keep
//! responsive. It is not a statement about whether the level EXISTS.
//!
//! This runs the step in a **child process** -- the same trick `kaboom` uses --
//! because an allocation failure aborts, and abort takes the whole process with
//! it. A parent that only watches can report the death instead of sharing it.
//!
//! Run:
//!     cargo run --release --example level_six              # the parent
//!     cargo run --release --example level_six -- 6         # the child, direct
//!
//! LANE: face counts are integers (EXACT). Byte figures are measured off real
//! allocations (COMPUTED). The projection it is checked against is arithmetic.

use goldberg_kernel::genesis::{Op, Params, State};
use goldberg_kernel::rng::Rng;
use std::env;
use std::process::Command;

fn gb(b: u64) -> f64 {
    b as f64 / 1_073_741_824.0
}

fn child(target: u32) {
    let p = Params::default();
    let mut rng = Rng::new(0xC60);
    let mut st = State::seed_c60();
    for lvl in 1..=target {
        // Report the PROJECTION before the step, so a death is preceded by the
        // number that predicted it rather than by silence.
        let peak = st.refine_peak_bytes(Op::All).unwrap_or(0);
        println!("  -> level {lvl}: projected peak {:.2} GB", gb(peak));
        st = st.refine(Op::All, &p, &mut rng);
        let b = st.heap_bytes();
        let inv = st.invariants();
        let census = st.census();
        println!(
            "     built  F={:<9} {:.2} GB  {:.1} B/face   census F={} P={}  {}",
            b.faces,
            gb(b.total()),
            b.total() as f64 / b.faces as f64,
            census.f,
            census.p,
            match &inv {
                Ok(i) if i.faces == census.f && i.pents == census.p =>
                    format!("LANES AGREE, chi={}", i.chi),
                Ok(i) => format!("LANES DISAGREE built F={} P={}", i.faces, i.pents),
                Err(e) => format!("INVARIANTS FAILED: {e:?}"),
            }
        );
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if let Some(n) = args.get(1).and_then(|s| s.parse::<u32>().ok()) {
        child(n);
        return;
    }

    println!("  LEVEL SIX -- past the viewer's ceiling, in a child that may die\n");
    let exe = env::current_exe().expect("own path");
    let out = Command::new(&exe).arg("6").output().expect("spawn");
    print!("{}", String::from_utf8_lossy(&out.stdout));
    let err = String::from_utf8_lossy(&out.stderr);
    if !err.trim().is_empty() {
        println!("  stderr: {}", err.trim());
    }
    println!(
        "\n  child exit: {}  {}",
        out.status,
        if out.status.success() {
            "-- the level exists and was measured"
        } else {
            "-- the machine said no. That IS the result."
        }
    );
}
