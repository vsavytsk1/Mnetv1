//! Paint the C60 with every declared palette, and let the eye choose.
//!
//! The geometry is absolute -- the same certified mesh, the same projection,
//! the same integer Bresenham lines. Only the palette changes. That is the
//! whole point: when the mathematics is settled, taste is free to be explored
//! instead of argued about.
//!
//! Follows genesis' own draw path (`GENESIS_CANVAS`, v8.5.2):
//!
//! ```text
//!   alpha = 0.15 + clamp((depth + 2) / 4, 0, 1) * 0.5
//!   pentagon edges: pent_edge at alpha          (the 12, always visible)
//!   hexagon  edges: hex_edge  at alpha * 0.6
//! ```
//!
//! ```powershell
//! cargo +stable-x86_64-pc-windows-gnu run --example paint_c60
//! ```

use goldberg_kernel::palette::{Palette, ALL};
use goldberg_kernel::raster::{project, Canvas};
use goldberg_kernel::{certify, judge, Mesh};

const W: usize = 720;
const H: usize = 800;
const SPHERE_H: usize = 720;

fn main() -> std::io::Result<()> {
    let mesh = Mesh::c60();
    let cert = certify(&mesh).expect("C60 must certify before it is painted");
    let verdict = judge::check(&judge::rotation_system_c60()).expect("and the judge must agree");

    println!("== THE GEOMETRY (absolute -- identical for every palette) ==");
    println!("   float lane : {cert}");
    println!("   judge      : {verdict}");
    println!();

    // classify each undirected edge: does it touch a pentagon?
    let mut pent_edge = vec![false; mesh.edges.len()];
    for face in &mesh.faces {
        if face.len() != 5 {
            continue;
        }
        for i in 0..face.len() {
            let (a, b) = (face[i], face[(i + 1) % face.len()]);
            let key = (a.min(b), a.max(b));
            if let Some(idx) = mesh
                .edges
                .iter()
                .position(|&(u, v)| (u.min(v), u.max(v)) == key)
            {
                pent_edge[idx] = true;
            }
        }
    }
    println!(
        "== {} pentagon edges (12 x 5), {} hexagon-only edges ==",
        pent_edge.iter().filter(|&&p| p).count(),
        pent_edge.iter().filter(|&&p| !p).count()
    );
    println!();

    println!("{:<12} {:<10} {:>18}  {}", "palette", "bg", "digest", "file");
    println!("{}", "-".repeat(68));

    for pal in ALL {
        let mut cv = Canvas::new(W, H, pal.bg);
        paint_shell(&mut cv, &mesh, &pent_edge, &pal);
        paint_swatches(&mut cv, &pal);

        let file = format!("c60_{}.png", pal.name);
        cv.write_png(&file)?;
        println!(
            "{:<12} {:<10} {:>18x}  {}",
            pal.name,
            Palette::hex(pal.bg),
            cv.digest(),
            file
        );
    }

    println!();
    println!("Same math, three dresses. Open them and pick.");
    println!("The digest is a receipt: re-run and it must not move.");
    Ok(())
}

/// The shell, painter-sorted back to front with genesis' depth-cued alpha.
fn paint_shell(cv: &mut Canvas, mesh: &Mesh, pent_edge: &[bool], pal: &Palette) {
    let (rx, ry, zoom) = (0.30_f64, 0.55_f64, 300.0_f64);

    // project once (DISPLAY lane -- decides where, never what colour)
    let pts: Vec<(i32, i32, f64)> = mesh
        .verts
        .iter()
        .map(|&v| project(v, rx, ry, zoom, W, SPHERE_H))
        .collect();

    // far edges first, so near ones land on top
    let mut order: Vec<usize> = (0..mesh.edges.len()).collect();
    order.sort_by(|&i, &j| {
        let d = |k: usize| {
            let (a, b) = mesh.edges[k];
            (pts[a].2 + pts[b].2) / 2.0
        };
        d(i).partial_cmp(&d(j)).unwrap()
    });

    for k in order {
        let (a, b) = mesh.edges[k];
        let depth = (pts[a].2 + pts[b].2) / 2.0;
        // genesis: alpha = 0.15 + clamp((depth+2)/4, 0, 1) * 0.5
        let t = ((depth + 2.0) / 4.0).clamp(0.0, 1.0);
        let alpha = 0.15 + t * 0.5;

        let (colour, a8) = if pent_edge[k] {
            (pal.pink, (alpha * 255.0) as u8)
        } else {
            (pal.cyan, (alpha * 0.6 * 255.0) as u8)
        };
        cv.line_a(pts[a].0, pts[a].1, pts[b].0, pts[b].1, colour, a8);
    }

    // the atoms: pentagon vertices brighter, as genesis draws them
    for (i, p) in pts.iter().enumerate() {
        let on_pent = mesh
            .edges
            .iter()
            .enumerate()
            .any(|(k, &(u, v))| pent_edge[k] && (u == i || v == i));
        let t = ((p.2 + 2.0) / 4.0).clamp(0.0, 1.0);
        let a8 = ((0.15 + t * 0.5) * 255.0) as u8;
        if on_pent {
            cv.disc(p.0, p.1, 2, pal.pink, a8);
        } else {
            cv.disc(p.0, p.1, 1, pal.green, (a8 as u32 * 6 / 10) as u8);
        }
    }
}

/// A swatch strip, so the palettes can be compared as colours and not only as
/// renders. Every slot, in a stable order, with its border.
fn paint_swatches(cv: &mut Canvas, pal: &Palette) {
    let slots = pal.slots();
    let n = slots.len();
    let pad = 8i32;
    let top = SPHERE_H as i32 + 4;
    let hgt = (H as i32) - top - pad;
    let wid = ((W as i32) - pad * 2) / n as i32;

    cv.fill_rect(0, SPHERE_H as i32, W as i32, (H - SPHERE_H) as i32, pal.panel);
    for (i, (_name, c)) in slots.iter().enumerate() {
        let x = pad + i as i32 * wid;
        cv.fill_rect(x, top, wid - 2, hgt, *c);
        cv.rect(x, top, wid - 2, hgt, pal.border);
    }
}
