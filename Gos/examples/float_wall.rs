//! THE GOLDEN PRECISION WALL -- Sol's Figure 5, rebuilt in the kernel.
//!
//! Verifying a gift from the Sol mage,
//! `THEA_PRECISE_FLOAT_PARADIGM_v1.0.0_BOOKKEEPING.md` (63/63 checks, 11
//! corrections). Its **PF39** claims the first binary64 Fibonacci-ratio false
//! zero is at `n = 40`. Reproduced here independently.
//!
//! ```text
//!   exact:   F_{n+1}/F_n - phi = (-phi^-1)^n / F_n       never zero
//!   binary64: fl(F_{n+1}/F_n) - fl(phi)                  zero from n = 40
//! ```
//!
//! # Two walls, one inequality
//!
//! The deviation shrinks like `phi^-2n`, so it falls under phi's ulp when
//! `2n log2(phi) > 53`, i.e. `n > 38.17`. Both walls sit on that line:
//!
//! ```text
//!   n = 38   OUR integer ladder breaks   (3*T_37 leaves 2^53)   RUSTIUM R3
//!   n = 40   SOL's measured false zero   (the subtraction cancels)  PF39
//! ```
//!
//! Different failures -- representability versus resolution -- from one cause.
//!
//! ```powershell
//! cargo run --release --example float_wall
//! ```

use goldberg_kernel::font;
use goldberg_kernel::layout::Rect;
use goldberg_kernel::palette::{Palette, Rgb, DASHBOARD};
use goldberg_kernel::raster::Canvas;
use goldberg_kernel::PHI;

const W: usize = 1180;
const H: usize = 720;
const N_MAX: usize = 60;
/// decades shown below 1.0
const DECADES: f64 = 30.0;

fn main() -> std::io::Result<()> {
    // exact Fibonacci in i128 -- F_61 is about 2.5e12, comfortable
    let mut f: Vec<i128> = vec![0, 1];
    for i in 2..=N_MAX + 2 {
        let x = f[i - 1] + f[i - 2];
        f.push(x);
    }

    // the two series
    let mut exact = Vec::with_capacity(N_MAX);
    let mut measured = Vec::with_capacity(N_MAX);
    let mut first_false_zero = None;
    for n in 1..=N_MAX {
        // exact:  |r_n - phi| = phi^-n / F_n
        let ex = PHI.powi(-(n as i32)) / f[n] as f64;
        // binary64: the subtraction the naive route performs
        let r = f[n + 1] as f64 / f[n] as f64;
        let me = (r - PHI).abs();
        if me == 0.0 && first_false_zero.is_none() {
            first_false_zero = Some(n);
        }
        exact.push(ex);
        measured.push(me);
    }
    let ffz = first_false_zero.unwrap_or(0);

    println!("PF39 -- first binary64 Fibonacci-ratio false zero: n = {ffz}   (Sol says 40)");
    println!("R3   -- our integer ladder f64 wall:               n = 38");
    println!(
        "theory -- deviation drops under phi's ulp at n > {:.2}",
        53.0 / (2.0 * PHI.log2())
    );
    println!();
    println!("   n        exact |r-phi|        binary64 measured");
    for n in [36, 37, 38, 39, 40, 41] {
        println!(
            "  {:>3}  {:>18.6e}  {:>18.6e}{}",
            n,
            exact[n - 1],
            measured[n - 1],
            if measured[n - 1] == 0.0 {
                "   <- FALSE ZERO"
            } else {
                ""
            }
        );
    }

    // ---- paint ------------------------------------------------------------
    let pal = DASHBOARD;
    let mut cv = Canvas::new(W, H, pal.bg);
    let plot = Rect::new(90, 96, W as i32 - 150, H as i32 - 200);

    grid(&mut cv, &pal, plot);
    axes_labels(&mut cv, &pal, plot);

    // the two curves
    plot_series(&mut cv, plot, &exact, pal.cyan, 2);
    plot_series(&mut cv, plot, &measured, pal.gold, 2);

    // where binary64 reports exactly zero, mark the floor -- a zero has no
    // place on a log axis, and pretending otherwise is the whole error
    for (i, &m) in measured.iter().enumerate() {
        if m == 0.0 {
            let x = px(plot, i + 1);
            cv.disc(x, plot.bottom() - 4, 3, pal.orange, 255);
        }
    }

    // the two walls, labels staggered so they cannot collide
    vline(
        &mut cv,
        &pal,
        plot,
        38,
        pal.pink,
        "N=38 R3 INTEGER LADDER",
        8,
    );
    vline(
        &mut cv,
        &pal,
        plot,
        ffz,
        pal.orange,
        "N=40 PF39 FALSE ZERO",
        24,
    );

    // phi's ulp floor: 2^-53 relative to phi
    let ulp = PHI * 2f64.powi(-53);
    let y = py(plot, ulp);
    for x in (plot.x..plot.right()).step_by(6) {
        cv.set(x, y, pal.purple);
    }
    font::text(
        &mut cv,
        plot.right() - 150,
        y - 10,
        "PHI ULP 2^-53",
        pal.purple,
        1,
    );

    header(&mut cv, &pal, ffz);
    legend(&mut cv, &pal, plot);

    let (kw, kh, kn) = cv.write_png_4k("float_wall.png")?;
    println!(
        "\nwrote float_wall.png + _4k.png  {kw}x{kh}  ({kn}x exact)   seal {:016x}",
        cv.digest()
    );
    Ok(())
}

/// x pixel for ladder index n.
fn px(p: Rect, n: usize) -> i32 {
    p.x + ((n as f64 / N_MAX as f64) * p.w as f64) as i32
}

/// y pixel for a magnitude, log10 scale from 1.0 down `DECADES`.
fn py(p: Rect, v: f64) -> i32 {
    if v <= 0.0 || !v.is_finite() {
        return p.bottom();
    }
    let d = -v.log10();
    let t = (d / DECADES).clamp(0.0, 1.0);
    p.y + (t * p.h as f64) as i32
}

fn grid(cv: &mut Canvas, pal: &Palette, p: Rect) {
    cv.fill_rect(p.x, p.y, p.w, p.h, [0x05, 0x05, 0x0c]);
    for d in 0..=DECADES as i32 {
        if d % 5 != 0 {
            continue;
        }
        let y = p.y + ((d as f64 / DECADES) * p.h as f64) as i32;
        for x in (p.x..p.right()).step_by(4) {
            cv.set(x, y, [0x14, 0x14, 0x24]);
        }
        let lab = if d == 0 {
            String::from("1")
        } else {
            format!("1E-{d}")
        };
        font::text(cv, p.x - 52, y - 3, &lab, [0x3a, 0x4a, 0x5a], 1);
    }
    for n in (0..=N_MAX).step_by(10) {
        let x = px(p, n);
        for y in (p.y..p.bottom()).step_by(4) {
            cv.set(x, y, [0x14, 0x14, 0x24]);
        }
        font::text(
            cv,
            x - 6,
            p.bottom() + 8,
            &format!("{n}"),
            [0x3a, 0x4a, 0x5a],
            1,
        );
    }
    cv.rect(p.x, p.y, p.w, p.h, pal.border);
}

fn axes_labels(cv: &mut Canvas, pal: &Palette, p: Rect) {
    font::text(
        cv,
        p.x + p.w / 2 - 60,
        p.bottom() + 26,
        "LADDER INDEX N",
        pal.text,
        1,
    );
    // clear of the header block, which ends at y=74
    font::text(cv, 8, p.y - 8, "ABS DEVIATION", pal.text, 1);
}

fn plot_series(cv: &mut Canvas, p: Rect, s: &[f64], c: Rgb, thick: i32) {
    let mut prev: Option<(i32, i32)> = None;
    for (i, &v) in s.iter().enumerate() {
        if v <= 0.0 {
            prev = None; // a zero cannot be drawn on a log axis. Break the line.
            continue;
        }
        let (x, y) = (px(p, i + 1), py(p, v));
        if let Some((qx, qy)) = prev {
            for t in 0..thick {
                cv.line(qx, qy + t, x, y + t, c);
            }
        }
        prev = Some((x, y));
    }
}

fn vline(cv: &mut Canvas, _pal: &Palette, p: Rect, n: usize, c: Rgb, label: &str, dy: i32) {
    let x = px(p, n);
    for y in (p.y..p.bottom()).step_by(3) {
        cv.set(x, y, c);
        cv.set(x + 1, y, c);
    }
    font::text(cv, x + 6, p.y + dy, label, c, 1);
}

fn header(cv: &mut Canvas, pal: &Palette, ffz: usize) {
    font::text(cv, 24, 22, "THE GOLDEN PRECISION WALL", pal.gold, 2);
    font::text(
        cv,
        24,
        46,
        "SOL MAGE PF39, REPRODUCED. THE EXACT DEVIATION NEVER REACHES ZERO.",
        pal.pink,
        1,
    );
    font::text(
        cv,
        24,
        60,
        &format!(
            "BINARY64 REPORTS ZERO FROM N={ffz}. TWO WALLS, ONE INEQUALITY: 2N LOG2 PHI > 53 AT N > 38.17"
        ),
        pal.text,
        1,
    );
    font::text(
        cv,
        24,
        74,
        "R3 N=38 REPRESENTABILITY  .  PF39 N=40 RESOLUTION  .  AT N=39 THE FLOAT DIFF EXCEEDS THE TRUTH",
        [0x4a, 0x5a, 0x6a],
        1,
    );
}

fn legend(cv: &mut Canvas, pal: &Palette, p: Rect) {
    let y = p.bottom() + 48;
    let mut x = 24;
    for (c, s) in [
        (pal.cyan, "EXACT  PHI^-N / F_N   (NEVER ZERO)"),
        (pal.gold, "BINARY64  FL(R_N) - FL(PHI)"),
        (pal.orange, "REPORTED EXACTLY ZERO"),
    ] {
        cv.fill_rect(x, y, 14, 4, c);
        x += 20;
        x += font::text(cv, x, y - 2, s, pal.text, 1) + 26;
    }
}
