//! THE GROWTH -- one byte stream, every subdivision level, side by side.
//!
//! > "we need to see as it grows because in that the duplications and the path
//! > forward will be clear"
//!
//! The algebraic side and the monkey brain, doing the same job at once:
//!
//! * **algebraic** -- each shell is built by exact index subdivision (no float
//!   decides adjacency, R7 cannot happen), and its `chi` is COUNTED by the
//!   integer judge, not recited from `V-E+F` on closed-form counts.
//! * **monkey brain** -- the same bytes are painted on each shell, so structure
//!   that is invisible at 20 faces becomes texture at 20,480. Symmetry is the
//!   first test; growth is the second.
//!
//! Every panel carries the numbers that earned it. A panel whose `chi` was
//! counted says JUDGE; one that was only edge-censused says COUNTED. They are
//! never blurred into a single green 2.
//!
//! ```powershell
//! cargo run --release --example orb_growth            # its own machine code
//! cargo run --release --example orb_growth -- FILE
//! ```

use goldberg_kernel::bits;
use goldberg_kernel::font;
use goldberg_kernel::judge;
use goldberg_kernel::layout::Rect;
use goldberg_kernel::palette::{Palette, Rgb, DASHBOARD};
use goldberg_kernel::raster::{project, Canvas};
use goldberg_kernel::sphere::{self, Ico};

const W: usize = 3840;
const H: usize = 2160;
/// levels shown, left to right
const LEVELS: [u32; 6] = [1, 2, 3, 4, 5, 6];
/// duplication granularity over the whole stream
const BLOCK: usize = 64;

struct Panel {
    faces: usize,
    verts: usize,
    edges: usize,
    chi: i64,
    how: &'static str,
    bytes_per_face: usize,
    /// faces whose byte block repeats an earlier one
    repeats: usize,
}

fn main() -> std::io::Result<()> {
    // ---- the stream -------------------------------------------------------
    let arg = std::env::args().nth(1);
    let (label, bytes) = match arg {
        Some(p) => {
            let b = std::fs::read(&p).unwrap_or_default();
            (p, b)
        }
        None => {
            let p = std::env::current_exe().unwrap_or_default();
            let b = std::fs::read(&p).unwrap_or_default();
            (
                p.file_name().map(|s| s.to_string_lossy().to_string()).unwrap_or_default(),
                b,
            )
        }
    };
    if bytes.is_empty() {
        eprintln!("empty stream");
        return Ok(());
    }

    // ---- global duplication, exact over the whole stream ------------------
    let mut seen: Vec<u64> = Vec::new();
    let mut repeated = 0usize;
    for chunk in bytes.chunks(BLOCK) {
        let h = bits::digest(chunk);
        if seen.contains(&h) {
            repeated += 1;
        } else {
            seen.push(h);
        }
    }
    let blocks = bytes.len().div_ceil(BLOCK);
    let dup_pct = 100.0 * repeated as f64 / blocks.max(1) as f64;
    let entropy = bits::entropy(&bytes);
    let ones_pct = 100.0 * bits::ones(&bytes) as f64 / (bytes.len() * 8) as f64;

    println!("stream      {label}  ({} bytes)", bytes.len());
    println!("duplication {repeated}/{blocks} blocks at {BLOCK}B = {dup_pct:.2}%");
    println!("entropy     {entropy:.4} bits/byte   ones {ones_pct:.2}%");
    println!();

    let pal = DASHBOARD;
    let mut cv = Canvas::new(W, H, pal.bg);

    // ---- header -----------------------------------------------------------
    font::text(&mut cv, 24, 20, "THE GROWTH", pal.gold, 5);
    font::text(
        &mut cv,
        24 + font::width("THE GROWTH", 5) + 18,
        52,
        "ONE STREAM, EVERY SUBDIVISION. EXACT INDEX WELD, CHI COUNTED.",
        pal.pink,
        1,
    );
    font::text(
        &mut cv,
        24,
        96,
        &format!(
            "{}  {} BYTES  .  DUP {}/{} BLOCKS AT {}B = {:.2} PCT  .  ENTROPY {:.4} B/B  .  ONES {:.2} PCT",
            label.to_uppercase(),
            bytes.len(),
            repeated,
            blocks,
            BLOCK,
            dup_pct,
            entropy,
            ones_pct
        ),
        pal.text,
        1,
    );

    // ---- panels -----------------------------------------------------------
    let grid = Rect::new(40, 140, W as i32 - 80, H as i32 - 300);
    let cols = grid.columns(3, 32);
    let panel_h = (grid.h - 32) / 2;
    let mut panels = Vec::new();

    for (i, &l) in LEVELS.iter().enumerate() {
        let col = &cols[i % 3];
        let row = i / 3;
        let r = Rect::new(col.x, grid.y + row as i32 * (panel_h + 32), col.w, panel_h);

        let ico = match Ico::level(l) {
            Ok(x) => x,
            Err(e) => {
                font::text(&mut cv, r.x + 8, r.y + 8, &format!("{e}"), pal.orange, 1);
                continue;
            }
        };

        // JUDGE EVERY LEVEL. The earlier version stopped at L4 and labelled
        // L5/L6 "COUNTED" -- not because the permutation was too expensive, but
        // because I assumed it was without measuring. L6 is 245,760 darts and
        // the judge is O(darts). Assuming a cost is not the same as paying it.
        let t0 = std::time::Instant::now();
        let (chi, how, e_count) = match ico.rotation_system().and_then(|s| judge::check(&s).ok()) {
            Some(j) => (j.chi, "JUDGE", j.e),
            None => (-999, "JUDGE FAILED", 0),
        };
        let judged_us = t0.elapsed().as_micros();

        let p = paint_panel(&mut cv, r, &ico, &bytes, &pal, l, chi, how, e_count);
        println!(
            "  L{}  faces {:>6}  V {:>6}  E {:>6}  chi {}  {:<6}  {:>7} us  {:>5} B/face  repeats {:>6}",
            l, p.faces, p.verts, p.edges, p.chi, p.how, judged_us, p.bytes_per_face, p.repeats
        );
        panels.push(p);
    }

    // ---- footer -----------------------------------------------------------
    let fy = H as i32 - 120;
    font::text(
        &mut cv,
        24,
        fy,
        "ALGEBRAIC: EXACT INDEX WELD -- THE MIDPOINT KEY IS A SORTED INDEX PAIR, SO THE SHELL CANNOT DRIFT WITH DEPTH.",
        pal.cyan,
        1,
    );
    font::text(
        &mut cv,
        24,
        fy + 26,
        "MONKEY BRAIN: THE SAME BYTES ON EVERY SHELL. WHAT IS ONE FLAT COLOUR AT 80 FACES IS TEXTURE AT 81,920.",
        pal.pink,
        1,
    );
    font::text(
        &mut cv,
        24,
        fy + 52,
        "ORANGE = A FACE WHOSE BYTE BLOCK REPEATS AN EARLIER ONE. DUPLICATION IS THE FINDING, SO IT DOES NOT HIDE IN THE RAMP.",
        pal.orange,
        1,
    );
    font::text(
        &mut cv,
        24,
        fy + 78,
        "TWELVE PINK VERTICES AT EVERY DEPTH -- EULER FORCES THEM. THEY ARE THE TWELVE PENTAGONS OF THE DUAL.",
        [0x4a, 0x5a, 0x6a],
        1,
    );

    cv.write_png("orb_growth.png")?;
    println!("\nwrote orb_growth.png   seal {:016x}", cv.digest());
    Ok(())
}

#[allow(clippy::too_many_arguments)]
fn paint_panel(
    cv: &mut Canvas,
    r: Rect,
    ico: &Ico,
    bytes: &[u8],
    pal: &Palette,
    level: u32,
    chi: i64,
    how: &'static str,
    edges: usize,
) -> Panel {
    cv.fill_rect(r.x, r.y, r.w, r.h, [0x05, 0x05, 0x0c]);
    cv.rect(r.x, r.y, r.w, r.h, pal.border);

    let cap_h = 110;
    let view = Rect::new(r.x, r.y, r.w, r.h - cap_h);
    let (rx, ry) = (0.34_f64, 0.62_f64);
    let zoom = (view.w.min(view.h) as f64) * 0.40;

    // bytes follow the spherical Hilbert order, so consecutive bytes land on
    // neighbouring faces -- byte_sphere's curveKey, ported
    let order = ico.curve_order();
    let n = ico.faces.len();
    let per = bytes.len().div_ceil(n).max(1);

    // Which face-blocks repeat.
    //
    // A HashSet with NO CAP. The first version used a Vec capped at 200,000
    // entries, which made the answer depend on where the cap fell: two runs
    // reported 22,080 and 22,094 repeats and two different seals. A capped
    // dedup that prints an exact-looking integer is RUSTIUM R11 in new clothes
    // -- the number was not wrong by a little, it was not a number.
    let mut fseen: std::collections::HashSet<u64> = std::collections::HashSet::with_capacity(n);
    let mut repeat_flag = vec![false; n];
    let mut ink = vec![0u8; n];
    for (slot, &fi) in order.iter().enumerate() {
        let s = (slot * per).min(bytes.len());
        let e = ((slot + 1) * per).min(bytes.len());
        let slice = &bytes[s..e];
        if slice.is_empty() {
            continue;
        }
        ink[fi] = ((bits::ones(slice) * 255) / (slice.len() * 8)) as u8;
        if !fseen.insert(bits::digest(slice)) {
            repeat_flag[fi] = true;
        }
    }
    let repeats = repeat_flag.iter().filter(|&&b| b).count();

    // project once
    let pts: Vec<(i32, i32, f64)> = ico
        .verts
        .iter()
        .map(|&v| {
            let (x, y, z) = project(v, rx, ry, zoom, view.w as usize, view.h as usize);
            (x + view.x, y + view.y, z)
        })
        .collect();

    // painter order, far first
    let mut order_f: Vec<(usize, f64)> = (0..n)
        .map(|i| {
            let f = &ico.faces[i];
            (i, (pts[f[0]].2 + pts[f[1]].2 + pts[f[2]].2) / 3.0)
        })
        .collect();
    order_f.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());

    for (fi, depth) in order_f {
        if depth < 0.0 {
            continue; // back face
        }
        let f = &ico.faces[fi];
        let (a, b, c) = (pts[f[0]], pts[f[1]], pts[f[2]]);
        let t = ((depth + 1.0) / 2.0).clamp(0.0, 1.0);
        let alpha = (0.25 + t * 0.70) * 255.0;
        let col = if repeat_flag[fi] {
            pal.orange
        } else {
            ramp(pal, ink[fi])
        };

        // LOD: a sub-pixel triangle is a dot. Honest, and it is what keeps
        // 81,920 faces affordable at panel size.
        let span = (a.0 - b.0).abs().max((a.1 - b.1).abs()).max((a.0 - c.0).abs());
        if span <= 2 {
            cv.blend(a.0, a.1, col, alpha as u8);
        } else {
            fill_tri(cv, a, b, c, col, alpha as u8);
        }
    }

    // the twelve, always
    for &d in &ico.defects() {
        let (x, y, z) = pts[d];
        if z > 0.0 {
            cv.disc(x, y, 7, pal.pink, 255);
        }
    }

    // caption
    let (vv, _, ff) = sphere::counts(level).unwrap();
    let cy = r.bottom() - cap_h + 6;
    font::text(cv, r.x + 8, cy, &format!("L{level}"), pal.gold, 2);
    font::text(
        cv,
        r.x + 8 + font::width("L0", 2) + 10,
        cy + 4,
        &format!("{ff} FACES  {} B/FACE", bytes.len().div_ceil(ff).max(1)),
        pal.cyan,
        1,
    );
    let how_col = if how == "JUDGE" { pal.green } else { pal.text };
    font::text(
        cv,
        r.x + 8,
        cy + 20,
        &format!("V {vv}  E {edges}  CHI {chi}  {how}"),
        how_col,
        1,
    );
    font::text(
        cv,
        r.x + 8,
        cy + 32,
        &format!("P 12 DEFECTS  .  {repeats} REPEAT FACES"),
        if repeats > 0 { pal.orange } else { [0x3a, 0x4a, 0x5a] },
        1,
    );

    Panel {
        faces: ff,
        verts: vv,
        edges,
        chi,
        how,
        bytes_per_face: bytes.len().div_ceil(ff).max(1),
        repeats,
    }
}

fn ramp(pal: &Palette, t: u8) -> Rgb {
    let t = t as u32;
    let (a, b) = (pal.panel, pal.cyan);
    [
        ((a[0] as u32 * (255 - t) + b[0] as u32 * t) / 255) as u8,
        ((a[1] as u32 * (255 - t) + b[1] as u32 * t) / 255) as u8,
        ((a[2] as u32 * (255 - t) + b[2] as u32 * t) / 255) as u8,
    ]
}

fn fill_tri(cv: &mut Canvas, a: (i32, i32, f64), b: (i32, i32, f64), c: (i32, i32, f64), col: Rgb, al: u8) {
    let pts = [(a.0, a.1), (b.0, b.1), (c.0, c.1)];
    let lo = pts.iter().map(|p| p.1).min().unwrap();
    let hi = pts.iter().map(|p| p.1).max().unwrap();
    for y in lo..=hi {
        let mut xs: Vec<i32> = Vec::with_capacity(4);
        for i in 0..3 {
            let (x0, y0) = pts[i];
            let (x1, y1) = pts[(i + 1) % 3];
            if (y0 <= y && y1 > y) || (y1 <= y && y0 > y) {
                let dy = y1 - y0;
                if dy != 0 {
                    xs.push(x0 + (y - y0) * (x1 - x0) / dy);
                }
            }
        }
        xs.sort_unstable();
        for pair in xs.chunks(2) {
            if let [xa, xb] = pair {
                for x in *xa..=*xb {
                    cv.blend(x, y, col, al);
                }
            }
        }
    }
}
