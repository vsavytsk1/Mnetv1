//! `net_timing` -- compute it, or load it? The exchange rate, in milliseconds.
//!
//! THE QUESTION: once a net is carved into bytes, the next run can *load* it
//! instead of *building* it. Which is faster, and from which level onward?
//!
//! Memory answers "how much"; this answers "how long", and they do not point
//! the same way. A level that is cheap to hold can be expensive to make.
//!
//! Prints, per level: build time, save time, load time, file size, and the
//! **speedup** load gives over build. LANE: face counts are EXACT; the
//! milliseconds are COMPUTED, on this machine, this run -- a wall clock is a
//! measurement of a moment, never a constant. Run it twice and the numbers
//! move; run it on another machine and they move further.

use goldberg_kernel::genesis::{Op, Params, State, Surface};
use goldberg_kernel::netfile;
use goldberg_kernel::rng::Rng;
use std::time::Instant;

fn mb(b: usize) -> f64 {
    b as f64 / 1_048_576.0
}

fn main() {
    let target: u32 = std::env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(5);

    let p = Params::default();
    let mut rng = Rng::new(0xC60);
    let mut st = State::seed_c60();

    println!("  NET TIMING -- build vs load, to level {target}\n");
    println!(
        "  {:<4} {:>9} {:>10} {:>9} {:>9} {:>9} {:>9}",
        "lvl", "faces", "build ms", "save ms", "load ms", "file MB", "speedup"
    );

    // level 0 has nothing to build, so the ladder starts at 1
    for lvl in 1..=target {
        let t = Instant::now();
        st = st.refine(Op::All, &p, &mut rng);
        let build_ms = t.elapsed().as_secs_f64() * 1000.0;

        let t = Instant::now();
        let bytes = netfile::to_bytes(&st, Surface::Spherical);
        let save_ms = t.elapsed().as_secs_f64() * 1000.0;

        let t = Instant::now();
        let (back, _) = netfile::from_bytes(&bytes).expect("reads back");
        let load_ms = t.elapsed().as_secs_f64() * 1000.0;

        // The load is only worth timing if it produced the same mesh. Check
        // the cheap invariant every single time rather than trusting the
        // round-trip test to still be true here.
        assert_eq!(back.faces.len(), st.faces.len(), "load lost faces");
        assert_eq!(back.census(), st.census(), "load changed the census");

        println!(
            "  {:<4} {:>9} {:>10.1} {:>9.1} {:>9.1} {:>9.2} {:>8.2}x",
            lvl,
            st.faces.len(),
            build_ms,
            save_ms,
            load_ms,
            mb(bytes.len()),
            build_ms / load_ms
        );
    }

    // ---- the same trip, through an ACTUAL FILE ----------------------------
    //
    // Everything above serialises to a Vec in RAM, which measures the CODEC
    // and nothing else. "How fast can we pass the chunks" is a question about
    // a disk, so ask a disk. First write is also first allocation of the
    // file, so it is timed separately from the read.
    {
        use std::fs;
        use std::io::Write;
        let dir = std::env::temp_dir().join("gos_nets");
        let _ = fs::create_dir_all(&dir);
        let path = dir.join(format!("c60_lvl{target}.gosnet"));

        let bytes = netfile::to_bytes(&st, Surface::Spherical);

        let t = Instant::now();
        {
            let mut f = fs::File::create(&path).expect("create");
            f.write_all(&bytes).expect("write");
            f.sync_all().expect("fsync"); // or we time the OS cache, not the disk
        }
        let write_ms = t.elapsed().as_secs_f64() * 1000.0;

        let t = Instant::now();
        let raw = fs::read(&path).expect("read");
        let read_ms = t.elapsed().as_secs_f64() * 1000.0;

        let t = Instant::now();
        let (back, _) = netfile::from_bytes(&raw).expect("parse");
        let parse_ms = t.elapsed().as_secs_f64() * 1000.0;
        assert_eq!(back.census(), st.census(), "the file changed the mesh");

        println!();
        println!("  THROUGH A REAL FILE at level {target}");
        println!("    {}", path.display());
        println!(
            "    write + fsync {:>9.1} ms   {:>7.1} MB/s",
            write_ms,
            mb(bytes.len()) / (write_ms / 1000.0)
        );
        println!(
            "    read          {:>9.1} ms   {:>7.1} MB/s",
            read_ms,
            mb(raw.len()) / (read_ms / 1000.0)
        );
        println!("    parse         {:>9.1} ms", parse_ms);
        println!(
            "    ---- load total {:>7.1} ms  vs a rebuild of every level",
            read_ms + parse_ms
        );
        let _ = fs::remove_file(&path);
    }

    // ---- the standing cost, once the net exists ---------------------------
    let bytes = netfile::to_bytes(&st, Surface::Spherical);
    let heap = st.heap_bytes().total();
    println!("\n  AT LEVEL {target}");
    println!(
        "    in memory  {:>10.2} MB   the soup, with id and lineage",
        heap as f64 / 1_048_576.0
    );
    println!(
        "    on disk    {:>10.2} MB   geometry only -- {:.2}x smaller",
        mb(bytes.len()),
        heap as f64 / bytes.len() as f64
    );
    println!(
        "\n  The disk copy is smaller because it drops what a rebuild can mint\n  \
         again: the id strings and the lineage paths. What it keeps is the\n  \
         geometry, which is the part no amount of recomputation can recover\n  \
         once the jitter seed is gone."
    );
}
