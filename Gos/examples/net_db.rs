//! `net_db` -- every net as a row of numbers, and the question of which one is
//! closest to being made of ones and zeros.
//!
//! # What a row holds
//!
//! One record per permutation of `(inner, mid, zoom, rx, ry, rz)`. Each carries
//! three kinds of number, and they are kept apart on purpose:
//!
//! * **the mesh** -- `F, P, V, E, chi`. EXACT, integer, and asserted before the
//!   row is written. A row describing a broken net would poison every query
//!   made against the table afterwards.
//! * **the bits** -- `mantissa_ones`, `density`, `powers_of_two`. EXACT. This
//!   is the "closest to 1 and 0" measure and it is not a metaphor: an f64 whose
//!   mantissa is empty is a number the machine holds for free, and one whose
//!   mantissa is full is a number that had to be rounded to fit. Counting those
//!   bits counts what the geometry actually costs to be.
//! * **the picture** -- `ink`, `l_entropy`, `distinct`. DISPLAY. Derived from
//!   the render through OKLab, and carrying no claim about the mesh.
//!
//! Points and lines, and every point has a value -- the value being what it
//! costs to write down.
//!
//! # Why the vector form
//!
//! Each row is a fixed-width numeric vector, so nets become comparable without
//! looking at them: nearest neighbours, clustering, "show me every net whose
//! density is under 0.1". The image and the `.gosnet` are referenced by name so
//! a hit can always be opened, and the netfile round trip is bit-identical, so
//! a stored net is the net.
//!
//! ```powershell
//! cargo run --release --example net_db            # 3x3 params x 4 views
//! cargo run --release --example net_db -- 4 3     # 4x4 params, level 3
//! ```

use goldberg_kernel::bits;
use goldberg_kernel::genesis::{Kind, Op, Params, State, Surface};
use goldberg_kernel::netfile;
use goldberg_kernel::oklab::FrameStats;
use goldberg_kernel::palette;
use goldberg_kernel::raster::{project_rpy, Canvas};
use goldberg_kernel::rng::Rng;
use std::fs;
use std::path::PathBuf;

const W: usize = 640;
const H: usize = 640;

/// The views swept per parameter pair: zoom, then pitch/yaw/roll in radians.
const VIEWS: [(f64, f64, f64, f64); 4] = [
    (180.0, 0.0, 0.0, 0.0),
    (260.0, 0.35, 0.60, 0.0),
    (420.0, 0.90, 1.20, 0.30),
    (760.0, 0.35, 2.40, 0.0),
];

fn main() -> std::io::Result<()> {
    let mut a = std::env::args().skip(1);
    let n: usize = a.next().and_then(|s| s.parse().ok()).unwrap_or(3);
    let levels: u32 = a.next().and_then(|s| s.parse().ok()).unwrap_or(3);

    let out = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("nets/db");
    fs::create_dir_all(&out)?;

    let vals: Vec<f64> = (0..n)
        .map(|i| 0.05 + (0.90 * i as f64) / (n as f64 - 1.0).max(1.0))
        .collect();
    let pal = palette::GENESIS;

    let mut csv = String::from(
        "inner,mid,zoom,rx,ry,rz,level,faces,pents,chi,coords,\
         mantissa_ones,density,powers_of_two,short_tail,worst,\
         ink,l_entropy,distinct,net_digest,image,netfile\n",
    );
    let mut rows = 0usize;
    let mut best: Option<(f64, String)> = None;

    println!(
        "  NET DB -- {} params x {} views = {} rows, level {levels}\n",
        n * n,
        VIEWS.len(),
        n * n * VIEWS.len()
    );
    println!(
        "  {:>5} {:>5} {:>8} {:>7} {:>7} {:>8} {:>7}",
        "inner", "mid", "coords", "density", "pow2", "l_entrop", "ink"
    );

    for &inner in &vals {
        for &mid in &vals {
            let p = Params {
                inner_scale: inner,
                mid_scale: mid,
                surface: Surface::Spherical,
                ..Params::default()
            };
            let mut rng = Rng::new(0xC60);
            let mut st = State::seed_c60();
            for _ in 0..levels {
                st = st.refine(Op::All, &p, &mut rng);
            }

            // A row about a broken net would poison every later query.
            let inv = st.invariants().expect("must measure");
            let census = st.census();
            assert_eq!(inv.faces, census.f, "lanes disagree at {inner}/{mid}");
            assert_eq!(inv.pents, 12, "P=12 is not negotiable");

            // ---- the bits: what this geometry costs to be ------------------
            let prof = bits::float_profile(
                st.faces
                    .iter()
                    .flat_map(|f| f.pts.iter().flat_map(|v| v.iter().copied())),
            );

            // ---- the net itself, stored once per parameter pair ------------
            let net_bytes = netfile::to_bytes(&st, Surface::Spherical);
            let netname = format!("net_i{inner:.2}_m{mid:.2}_lv{levels}.gosnet");
            fs::write(out.join(&netname), &net_bytes)?;
            let digest = bits::digest(&net_bytes);

            for (vi, &(zoom, rx, ry, rz)) in VIEWS.iter().enumerate() {
                let mut cv = Canvas::new(W, H, pal.bg);
                draw(&mut cv, &st, &pal, zoom, rx, ry, rz);
                // stride 1: examine every pixel. 640x640 is 409,600 cube roots per
                // image and the doc asks the caller to state what it paid -- this pays
                // in full, because a sampled entropy is a different number and this one
                // goes into a table other things will be compared against.
                let stats = FrameStats::measure(&cv.px, 1);
                let img = format!("img_i{inner:.2}_m{mid:.2}_v{vi}.png");
                cv.write_png(out.join(&img))?;

                csv.push_str(&format!(
                    "{inner:.2},{mid:.2},{zoom},{rx},{ry},{rz},{levels},\
                     {},{},{},{},{},{:.6},{},{},{},\
                     {:.6},{:.6},{},{digest:016x},{img},{netname}\n",
                    census.f,
                    census.p,
                    inv.chi,
                    prof.n,
                    prof.mantissa_ones,
                    prof.density(),
                    prof.powers_of_two,
                    prof.short_tail,
                    prof.worst,
                    stats.ink,
                    stats.l_entropy,
                    stats.distinct,
                ));
                rows += 1;

                if vi == 1 {
                    println!(
                        "  {inner:>5.2} {mid:>5.2} {:>8} {:>7.4} {:>7} {:>8.3} {:>7.4}",
                        prof.n,
                        prof.density(),
                        prof.powers_of_two,
                        stats.l_entropy,
                        stats.ink
                    );
                }
            }

            let d = prof.density();
            if best.as_ref().is_none_or(|(b, _)| d < *b) {
                best = Some((d, format!("inner={inner:.2} mid={mid:.2}")));
            }
        }
    }

    fs::write(out.join("NETS.csv"), &csv)?;
    println!("\n  {rows} rows -> {}", out.join("NETS.csv").display());
    if let Some((d, who)) = best {
        println!(
            "\n  CLOSEST TO ONES AND ZEROS: {who}\n  \
             mantissa density {d:.4} -- {:.1}% of the 52 available bits are set.\n  \
             A perfectly binary geometry would read 0.0000; a random one ~0.5.",
            d * 100.0
        );
    }
    Ok(())
}

fn draw(cv: &mut Canvas, st: &State, pal: &palette::Palette, zoom: f64, rx: f64, ry: f64, rz: f64) {
    let depths: Vec<f64> = st
        .faces
        .iter()
        .map(|f| {
            f.pts
                .iter()
                .map(|&v| project_rpy(v, rx, ry, rz, zoom, W, H).2)
                .sum::<f64>()
                / f.pts.len() as f64
        })
        .collect();
    let mut order: Vec<usize> = (0..st.faces.len()).collect();
    order.sort_by(|&a, &b| depths[a].partial_cmp(&depths[b]).unwrap());
    for &k in &order {
        let f = &st.faces[k];
        let t = ((depths[k] + 2.0) / 4.0).clamp(0.0, 1.0);
        let alpha = 0.15 + t * 0.5;
        let (c, a8) = if f.kind == Kind::Pent {
            (pal.pink, (alpha * 255.0) as u8)
        } else {
            (pal.cyan, (alpha * 0.6 * 255.0) as u8)
        };
        let pts: Vec<(i32, i32)> = f
            .pts
            .iter()
            .map(|&v| {
                let q = project_rpy(v, rx, ry, rz, zoom, W, H);
                (q.0, q.1)
            })
            .collect();
        for i in 0..pts.len() {
            let j = (i + 1) % pts.len();
            cv.line_a(pts[i].0, pts[i].1, pts[j].0, pts[j].1, c, a8);
        }
    }
}
