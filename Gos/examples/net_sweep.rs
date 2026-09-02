//! `net_sweep` -- every (inner, mid) is a different net. Build them all, keep
//! a picture of each, and let the eye do the sorting.
//!
//! `inner` is where the child ring sits inside its parent; `mid` is how far the
//! edge midpoints are pulled in. The viewer's own help states the rule this
//! sweep is built to display:
//!
//! > `mid > inner` opens a rosette; `mid < inner` overlaps into bursts.
//! > That is the CRESCENT DEFECT, and it is the picture.
//!
//! So the grid is not decoration -- the diagonal `mid == inner` is the seam
//! between two different families, and the sweep exists to see where it runs.
//!
//! Each cell builds levels 1..=4 and renders the LAST one. Wireframe, no fill:
//! the fill is 3.5 million blended spans at depth and adds nothing to a
//! parameter comparison, where only the shape of the interference matters.
//!
//! ```powershell
//! cargo run --release --example net_sweep              # 5x5, level 4
//! cargo run --release --example net_sweep -- 4 3       # 4x4 grid, level 3
//! ```
//!
//! Writes to `Gos/nets/`, named so a file listing sorts into the grid:
//! `net_i0.20_m0.35_lv4.png`. Scroll them in order and `mid` sweeps within
//! each `inner`.
//!
//! LANE: the mesh is EXACT (integer census, verified per cell). The picture is
//! DISPLAY -- projection and alpha, neither of which carries a claim.

use goldberg_kernel::genesis::{Op, Params, State, Surface};
use goldberg_kernel::palette;
use goldberg_kernel::raster::{project_rpy, Canvas};
use goldberg_kernel::rng::Rng;
use std::fs;
use std::path::PathBuf;
use std::time::Instant;

const W: usize = 900;
const H: usize = 900;

fn main() -> std::io::Result<()> {
    let mut a = std::env::args().skip(1);
    let n: usize = a.next().and_then(|s| s.parse().ok()).unwrap_or(5);
    let levels: u32 = a.next().and_then(|s| s.parse().ok()).unwrap_or(4);

    let out = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("nets");
    fs::create_dir_all(&out)?;

    // n values evenly spaced across the viewer's own 0.05..0.95 range
    let vals: Vec<f64> = (0..n)
        .map(|i| 0.05 + (0.90 * i as f64) / (n as f64 - 1.0).max(1.0))
        .collect();

    println!(
        "  NET SWEEP -- {n}x{n} = {} nets, each built to level {levels}\n  writing to {}\n",
        n * n,
        out.display()
    );
    println!(
        "  {:>6} {:>6} {:>9} {:>4} {:>8} {:>9}  family",
        "inner", "mid", "faces", "P", "build ms", "draw ms"
    );

    let pal = palette::GENESIS;
    let mut manifest = String::from(
        "# net_sweep manifest -- inner, mid, level, faces, pents, chi, file\n\
         # mid > inner = rosette; mid < inner = bursts (the crescent defect)\n",
    );
    let t_all = Instant::now();

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

            let t = Instant::now();
            for _ in 0..levels {
                st = st.refine(Op::All, &p, &mut rng);
            }
            let build_ms = t.elapsed().as_secs_f64() * 1000.0;

            // The mesh must certify before it is painted. A pretty picture of a
            // broken net is the one thing worse than no picture.
            let inv = st.invariants().expect("the swept net must measure");
            let census = st.census();
            assert_eq!(
                inv.faces, census.f,
                "lanes disagree at inner={inner} mid={mid}"
            );
            assert_eq!(inv.pents, 12, "P=12 is not negotiable");

            let t = Instant::now();
            let mut cv = Canvas::new(W, H, pal.bg);
            draw(&mut cv, &st, &pal);
            let draw_ms = t.elapsed().as_secs_f64() * 1000.0;

            let name = format!("net_i{inner:.2}_m{mid:.2}_lv{levels}.png");
            cv.write_png(out.join(&name))?;

            let family = if (mid - inner).abs() < 1e-9 {
                "seam"
            } else if mid > inner {
                "rosette"
            } else {
                "bursts"
            };
            println!(
                "  {inner:>6.2} {mid:>6.2} {:>9} {:>4} {build_ms:>8.1} {draw_ms:>9.1}  {family}",
                census.f, census.p
            );
            manifest.push_str(&format!(
                "{inner:.2},{mid:.2},{levels},{},{},{},{name}\n",
                census.f, census.p, inv.chi
            ));
        }
    }

    fs::write(out.join("MANIFEST.csv"), &manifest)?;
    println!(
        "\n  {} nets in {:.1} s. MANIFEST.csv beside them.",
        n * n,
        t_all.elapsed().as_secs_f64()
    );
    println!("  scroll the folder in name order: mid sweeps within each inner.");
    Ok(())
}

/// The viewer's `paint_genesis`, minus the fill and the panel: painter-ordered
/// by depth, pentagons picked out, alpha rising toward the camera.
fn draw(cv: &mut Canvas, st: &State, pal: &palette::Palette) {
    let (rx, ry, rz, zoom) = (0.35, 0.6, 0.0, 260.0);
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
        let (c, a8) = if f.kind == goldberg_kernel::genesis::Kind::Pent {
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
