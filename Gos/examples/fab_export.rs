//! Take the certified C60 all the way out of the cave and into fab formats.
//!
//! This is the whole argument in one run: a graph we *judged* becomes four
//! files that four different machines eat, and the last float dies at
//! `quantise()`.
//!
//! ```powershell
//! cargo +stable-x86_64-pc-windows-gnu run --example fab_export
//! ```

use goldberg_kernel::fab::{dxf_lines, mesh_tris, stl_binary, unwrap_equirect, Excellon, Gerber};
use goldberg_kernel::{certify, judge, Mesh};

/// Board diameter in mm -- the same 40 mm pcbium uses, so the numbers compare.
const BOARD_DIA: f64 = 40.0;
/// Panel is the unwrapped unit square scaled to this many mm across.
const PANEL_W: f64 = 120.0;
const TRACE_W: f64 = 0.25;
const PAD_DIA: f64 = 1.20;
const DRILL_DIA: f64 = 0.60;

fn main() -> std::io::Result<()> {
    // ---- 1. the gate. nothing is exported that was not judged. -------------
    let mesh = Mesh::c60();
    let cert = certify(&mesh).expect("the shell must certify before it is fabricated");
    let verdict = judge::check(&judge::rotation_system_c60()).expect("and the judge must agree");
    println!("== THE GATE ==");
    println!("   float lane : {cert}");
    println!("   judge      : {verdict}");
    assert_eq!(cert.p, 12, "AXIOM 01: P=12 or do not ship");
    assert_eq!(cert.chi, 2, "AXIOM 01: chi=2 or do not ship");
    println!("   AXIOM 01   : P=12, chi=2 -- PASS, export permitted");
    println!();

    // ---- 2. the 3D shape: STL, for CAD and the printer ---------------------
    let tris = mesh_tris(&mesh);
    let stl = stl_binary(&tris, BOARD_DIA / 2.0);
    std::fs::write("c60_shell.stl", &stl)?;
    println!("== STL (the shape) ==");
    println!("   {} faces -> {} triangles (fan)", mesh.faces.len(), tris.len());
    println!(
        "   c60_shell.stl  {} B  = 84 + {}*50",
        stl.len(),
        tris.len()
    );
    println!();

    // ---- 3. sphere -> panel. DISPLAY lane, and the seam is real. ----------
    // Equirectangular puts a seam on the antimeridian: an edge whose ends sit
    // either side of u = +/-0.5 would be drawn as a false line straight across
    // the panel. We DROP those and we SAY SO. Silence here would be a lie
    // shaped exactly like a working board.
    let uv: Vec<(f64, f64)> = mesh.verts.iter().map(|&v| unwrap_equirect(v)).collect();
    let to_mm = |(u, w): (f64, f64)| (u * PANEL_W, w * PANEL_W / 2.0);

    let mut gerber = Gerber::new("C60 unwrapped -- top copper");
    let mut drill = Excellon::new();
    let mut segs: Vec<goldberg_kernel::fab::Seg> = Vec::new();
    let mut seam_skipped = 0usize;

    for &(a, b) in &mesh.edges {
        let (ua, ub) = (uv[a], uv[b]);
        if (ua.0 - ub.0).abs() > 0.5 {
            seam_skipped += 1; // crosses the antimeridian
            continue;
        }
        let (pa, pb) = (to_mm(ua), to_mm(ub));
        gerber
            .polyline(&[pa, pb], TRACE_W)
            .expect("edge must quantise");
        segs.push((pa, pb));
    }
    for &p in &uv {
        let (x, y) = to_mm(p);
        gerber.flash(x, y, PAD_DIA).expect("pad must quantise");
        drill.hit(x, y, DRILL_DIA).expect("hit must quantise");
    }

    let gb = gerber.write("c60_top.gbr")?;
    let dr = drill.write("c60.drl")?;
    let dxf = dxf_lines(&segs, "COPPER");
    std::fs::write("c60_outline.dxf", dxf.as_bytes())?;

    println!("== THE PANEL (equirectangular, DISPLAY lane) ==");
    println!(
        "   {} edges -> {} drawn, {} dropped at the seam",
        mesh.edges.len(),
        segs.len(),
        seam_skipped
    );
    println!(
        "   c60_top.gbr      {gb} B   {} aperture(s), {} pads flashed",
        gerber.aperture_count(),
        uv.len()
    );
    println!(
        "   c60.drl          {dr} B   {} tool(s), {} hits",
        drill.tool_count(),
        drill.hit_count()
    );
    println!("   c60_outline.dxf  {} B   {} LINE entities", dxf.len(), segs.len());
    println!();

    // ---- 4. the receipt ----------------------------------------------------
    println!("== THE RECEIPT ==");
    println!("   gerber checksum : {:016x}", gerber.checksum());
    println!("   re-run and this number must not move.");
    println!();
    println!("== WHAT THIS RUN DOES NOT CLAIM ==");
    println!("   - the seam drop makes this panel NOT a faithful copy of the shell");
    println!("   - equirectangular stretches at the poles (Theorema Egregium)");
    println!("   - no stackup, so no impedance; no mask, no paste, no netlist");
    println!("   - judge.rs certified the GRAPH. nothing certifies a Gerber but a fab.");
    Ok(())
}
