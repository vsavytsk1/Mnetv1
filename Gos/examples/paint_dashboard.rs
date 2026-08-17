//! Paint the ENG v2.0 dashboard skeleton + the first card, straight to a PNG.
//!
//! No window, no browser. Renders the same code path the viewer uses, so the
//! image is exactly what the .exe shows -- which makes it diffable against a
//! screenshot of the real .io page.
//!
//! ```powershell
//! cargo +stable-x86_64-pc-windows-gnu run --example paint_dashboard
//! ```

use goldberg_kernel::dashboard::{self, Card, KRow, Model, NOT_YET};
use goldberg_kernel::layout::{Dash, Rect};
use goldberg_kernel::palette::DASHBOARD;
use goldberg_kernel::raster::Canvas;
use goldberg_kernel::{certify, judge, Mesh};

const W: usize = 1280;
const H: usize = 720;

fn main() -> std::io::Result<()> {
    // AXIOM 01 -- the gate, before a single pixel exists.
    let cert = certify(&Mesh::c60()).expect("P=12 and chi=2 or do not ship");
    let verdict = judge::check(&judge::rotation_system_c60()).expect("the judge must agree");
    println!("AXIOM 01 GATE");
    println!("  float lane : {cert}");
    println!("  judge      : {verdict}");
    println!("  lanes agree: {}", cert.chi == verdict.chi && cert.v == verdict.v);
    println!();

    // the layout must tile the canvas exactly -- asserted, not hoped
    let canvas = Rect::of(W, H);
    let d = Dash::split(canvas);
    assert!(d.covers(canvas), "the five regions must tile the canvas");
    println!("LAYOUT  {}x{}", W, H);
    for (name, r) in [
        ("top", d.top),
        ("left", d.left),
        ("center", d.center),
        ("right", d.right),
        ("bottom", d.bottom),
    ] {
        println!("  {name:<7} x{:<5} y{:<5} {}x{}", r.x, r.y, r.w, r.h);
    }
    println!("  tiles exactly: {}", d.covers(canvas));
    println!();

    let pal = DASHBOARD;
    let modules = [
        KRow { name: "M1 GOLDBERG", ok: true, kb: 47 },
        KRow { name: "M2 AXIOMS", ok: true, kb: 12 },
        KRow { name: "M3 SAR", ok: true, kb: 9 },
        KRow { name: "M4 NS SPECTRAL", ok: true, kb: 21 },
        KRow { name: "M5 FRACTAL", ok: true, kb: 14 },
        KRow { name: "M6 NANITE", ok: true, kb: 18 },
    ];

    // THE BIRTH -- the real front door centerpiece, and a `.feat-card`, so this
    // one card exercises the featured path, the accent colour, the wrap and the
    // caps row all at once. Gold is the slot every palette in the cave agrees
    // on, so nothing here is confounded by the palette drift.
    let test_name = format!("C60KTEST v{}", goldberg_kernel::VERSION);
    let test_desc = format!(
        "the integration card. painted by the kernel, no browser. this shell was certified \
         by BOTH lanes before a pixel existed: V {} E {} F {} CHI {} and the integer judge \
         agrees. seal is content-only, so it reproduces.",
        cert.v, cert.e, cert.f, cert.chi
    );
    let cards = [
        Card {
            tag: "* THE BIRTH",
            name: "THE LIGHT MATRIX",
            desc: "the source code of it all, computed LIVE. Euler forces P=12; one 4x4 \
                   integer matrix governs the whole family; the C60 adjacency graph is built \
                   and diagonalized on the fly to land lambda min at minus phi squared.",
            accent: pal.gold,
            caps: &["frm", "kbd"],
            featured: true,
        },
        Card {
            tag: "KERNEL",
            name: &test_name,
            desc: &test_desc,
            accent: pal.cyan,
            caps: &["frm", "pc", "kbd"],
            featured: false,
        },
    ];

    let m = Model {
        version: "v2.0",
        git: "4d9bd67",
        ledger: "L189",
        cert: "V 60 E 90 F 32 CHI 2",
        modules: &modules,
        cards: &cards,
        category: "THEA HELENI SOURCE CODE",
    };

    let mut cv = Canvas::new(W, H, pal.bg);
    let rects = dashboard::draw(&mut cv, &pal, &m);

    println!("CARDS PAINTED: {}", rects.len());
    for r in &rects {
        println!("  x{:<5} y{:<5} {}x{}", r.x, r.y, r.w, r.h);
    }
    println!();
    println!("SEAL (content only, no clock painted): {:016x}", cv.digest());
    println!();
    println!("KNOWN GAPS vs the browser -- {} of them, stated not hidden:", NOT_YET.len());
    for g in NOT_YET {
        println!("  - {g}");
    }

    cv.write_png("dashboard_skeleton.png")?;
    println!("\nwrote dashboard_skeleton.png");
    Ok(())
}
