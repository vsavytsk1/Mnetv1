//! `net_curve` -- build it, weld it, store it, load it back, to the ceiling.
//!
//! The curve this draws is the one that decides how the cave should work:
//!
//! ```text
//!   BUILD   refine from the level below            grows with the faces
//!   WELD    close the topology on the bits         grows with the corners
//!   SAVE    netfile bytes, exact and predictable   grows with the faces
//!   LOAD    read the bits back                     grows with the FILE
//! ```
//!
//! and the question is where LOAD overtakes BUILD, because past that rung a
//! stored net is not a convenience, it is the cheaper object.
//!
//! # WHY THE ROUND TRIP IS AN EQUALITY, NOT AN APPROXIMATION
//!
//! `netfile` stores every coordinate as `to_bits()` and never as decimal, so a
//! loaded level is not a copy of a computed one -- **it is it**. This program
//! asserts that rather than trusting it: every rung is compared face by face,
//! bit pattern by bit pattern, and a single differing bit stops the run.
//!
//! Anything less would make the curve meaningless. A "load" that returns
//! something merely close is not competing with the build; it is a different
//! object that happens to be faster.
//!
//! # THE CEILING IS ARITHMETIC
//!
//! `Op::All` is multiplication by the Eisenstein integer `(1,2)`: `T -> 7T`, so
//! faces go `7F - 12`. The next rung is priced from that recurrence and refused
//! with the number before anything is allocated (Curse 35, RUSTIUM R3).
//!
//! ```powershell
//! cargo run --release --example net_curve          # to the 2 GB budget
//! cargo run --release --example net_curve -- 4     # 4 GB, one rung further
//! ```

use goldberg_kernel::genesis::{Op, Params, State, Surface};
use goldberg_kernel::netfile;
use goldberg_kernel::rng::Rng;
use goldberg_kernel::weld;
use std::fs;
use std::path::PathBuf;
use std::time::Instant;

fn main() -> std::io::Result<()> {
    let budget_gb: f64 = std::env::args()
        .nth(1)
        .and_then(|s| s.parse().ok())
        .unwrap_or(2.0);
    let budget = (budget_gb * 1024.0 * 1024.0 * 1024.0) as u64;

    let out = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("nets/curve");
    fs::create_dir_all(&out)?;

    println!("  NET CURVE -- build, weld, save, load. budget {budget_gb} GB");
    println!("  storing to {}\n", out.display());
    println!(
        "  {:>3} {:>10} {:>10} {:>9} {:>9} {:>9} {:>9} {:>8} {:>7}",
        "lvl", "faces", "V welded", "build ms", "weld ms", "save ms", "load ms", "file MB", "L/B"
    );

    let p = Params {
        surface: Surface::Spherical,
        ..Params::default()
    };
    let mut rng = Rng::new(0xC60);
    let mut st = State::seed_c60();
    let mut level = 0u32;
    let mut csv = String::from(
        "# net_curve -- one row per level. milliseconds are COMPUTED on this\n\
         # machine this run; faces, points and bytes are EXACT.\n\
         level,faces,v_welded,build_ms,weld_ms,save_ms,load_ms,file_bytes,heap_bytes,speedup\n",
    );
    let mut build_ms = 0.0f64;

    loop {
        let inv = st.invariants().expect("the shell must measure");

        let t = Instant::now();
        let w = weld::weld(&st);
        let weld_ms = t.elapsed().as_secs_f64() * 1000.0;

        // SAVE
        let t = Instant::now();
        let bytes = netfile::to_bytes(&st, Surface::Spherical);
        let save_ms = t.elapsed().as_secs_f64() * 1000.0;
        let path = out.join(format!("level_{level}.gosnet"));
        fs::write(&path, &bytes)?;

        // the price was quoted before the file existed -- check it was paid
        let c = st.census();
        assert_eq!(
            netfile::bytes_for(c.p, c.f - c.p) as usize,
            bytes.len(),
            "bytes_for quoted a price the writer did not pay at level {level}"
        );

        // LOAD
        let raw = fs::read(&path)?;
        let t = Instant::now();
        let (back, surf) = netfile::from_bytes(&raw).expect("a net we just wrote must read back");
        let load_ms = t.elapsed().as_secs_f64() * 1000.0;
        assert_eq!(
            surf,
            Surface::Spherical,
            "the surface must survive the trip"
        );

        // THE ROUND TRIP IS AN EQUALITY. Bit patterns, not distances -- a
        // tolerance here would turn the curve into a comparison of two
        // different objects.
        assert_eq!(back.faces.len(), st.faces.len(), "face count changed");
        for (a, b) in back.faces.iter().zip(st.faces.iter()) {
            assert_eq!(a.kind, b.kind);
            assert_eq!(a.pts.len(), b.pts.len());
            for (u, v) in a.pts.iter().zip(b.pts.iter()) {
                for k in 0..3 {
                    assert_eq!(
                        u[k].to_bits(),
                        v[k].to_bits(),
                        "level {level}: a coordinate came back with different bits"
                    );
                }
            }
        }

        let heap = st.heap_bytes().total();
        let speedup = if load_ms > 0.0 {
            build_ms / load_ms
        } else {
            0.0
        };
        println!(
            "  {:>3} {:>10} {:>10} {:>9.1} {:>9.1} {:>9.1} {:>9.1} {:>8.2} {:>7}",
            level,
            inv.faces,
            w.v(),
            build_ms,
            weld_ms,
            save_ms,
            load_ms,
            bytes.len() as f64 / 1_048_576.0,
            if level == 0 {
                String::from("--")
            } else {
                format!("{speedup:.1}x")
            }
        );
        csv.push_str(&format!(
            "{level},{},{},{build_ms:.3},{weld_ms:.3},{save_ms:.3},{load_ms:.3},{},{heap},{speedup:.3}\n",
            inv.faces,
            w.v(),
            bytes.len()
        ));

        // price the next rung, refuse with the number
        let next_faces = 7 * inv.faces - 12;
        let next_heap = heap.saturating_mul(next_faces) / inv.faces.max(1);
        if next_heap > budget {
            println!(
                "\n  NEXT RUNG REFUSED: level {} would hold {} faces and about {:.2} GB,\n  \
                 past the {budget_gb} GB budget -- priced from the recurrence, never allocated.",
                level + 1,
                next_faces,
                next_heap as f64 / 1_073_741_824.0
            );
            break;
        }

        let t = Instant::now();
        st = st.refine(Op::All, &p, &mut rng);
        build_ms = t.elapsed().as_secs_f64() * 1000.0;
        level += 1;
    }

    fs::write(out.join("CURVE.csv"), &csv)?;
    println!("\n  curve -> {}", out.join("CURVE.csv").display());
    println!("  nets  -> {} files", level + 1);
    println!("\n  EVERY RUNG ROUND-TRIPPED BIT FOR BIT. A loaded net is not a copy of a");
    println!("  computed one, it is the same object -- which is the only reason the");
    println!("  load column may be compared against the build column at all.");
    Ok(())
}
