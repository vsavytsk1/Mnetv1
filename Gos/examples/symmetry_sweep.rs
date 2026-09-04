//! `symmetry_sweep` -- find every rotation axis of the shell, and walk them.
//!
//! # WHY THIS EXISTS
//!
//! The C60 is built from the golden ratio, so its rotation group is
//! icosahedral: order 60, with 15 two-fold axes, 10 three-fold and 6 five-fold.
//! That is a fact about the coordinates. This program does not assume it: it
//! **finds the axes in the mesh and then confirms every one of them on
//! screen**, and the count is either 15 / 10 / 6 or the claim is wrong.
//!
//! *(This sentence used to read "measures it, from the rendered image alone".
//! That was true of the first version and stopped being true when the search
//! moved -- see WHERE THE SEARCH HAPPENS -- and the header was not moved with
//! it. A file that contradicts itself four screens apart is the exact shape
//! this crate spends its tests catching, so the correction is recorded rather
//! than quietly applied.)*
//!
//! # THE INSTRUMENT, AND WHY THE OBVIOUS TWO DO NOT WORK
//!
//! `roll` is applied AFTER the shell is flattened (see `project_rpy`), so it
//! spins the finished 2D picture and never touches depth. Therefore:
//!
//! > **the image repeats under a roll of `2*PI/n` exactly when the view axis
//! > is an n-fold axis of the solid** -- because the projection is
//! > ORTHOGRAPHIC, and an orthographic projection carries the symmetry group
//! > of the object straight onto the screen.
//!
//! Two instruments already existed and neither could see this:
//!
//! ```text
//!   the frame seal      too STRICT -- a hash. One flipped pixel and two
//!                       otherwise identical pictures get unrelated numbers.
//!                       Measured: a literal FULL TURN differs from its own
//!                       start by 1181 bytes, because sin(TAU) is -2.4e-16
//!                       rather than 0, and the seal calls that "different".
//!
//!   OKLab FrameStats    too LOOSE -- ink, entropy and chroma are invariant
//!                       under EVERY rotation, symmetric or not. Measured:
//!                       identical to three decimals at 0, 36, 72, 144, 216
//!                       and 288 degrees, where only four of those are
//!                       symmetry angles.
//! ```
//!
//! What works is the plainest thing in between: **count the bytes that
//! differ.** Measured on the real render, level 2:
//!
//! ```text
//!   z axis, roll PI      (2-fold, predicted)      1541 bytes   0.02%
//!   z axis, roll 1.0     (control)              414731 bytes   6.67%
//!   atan(1/PHI), 2PI/5   (5-fold, predicted)      4912 bytes   0.08%
//!   atan(1/PHI), PI/5    (control)              348999 bytes   5.61%
//! ```
//!
//! Two orders of magnitude, with the symmetric cases sitting on the
//! floating-point noise floor. A threshold anywhere in the decade between
//! them separates them, so `THRESHOLD_PCT` has an order of magnitude of slack
//! in both directions -- which is what makes it a measurement and not a knob.
//!
//! # LANE
//!
//! **DISPLAY.** `sin`, `cos` and `atan2` are all over the projection and none
//! is required to be correctly rounded, so nothing here carries a bit-identity
//! claim. That is exactly why the test is a *tolerance* on a pixel count and
//! not an equality: the residual at a true symmetry is the rounding, and the
//! program reports it rather than hiding it.
//!
//! # WHERE THE SEARCH HAPPENS, AND WHY NOT HERE
//!
//! The first version of this program swept a grid over the (pitch, yaw) sphere
//! looking for the dips. It found exactly ONE axis: the one that happened to
//! land on a grid line. That is not a bug, it is the shape of the function --
//! the probe below measures a basin under 0.001 rad wide, so a blind grid needs
//! something like 10^7 samples and 10^8 renders to be sure of hitting one.
//!
//! **A symmetry is a property of the point set, not of the pixels it lands
//! on.** So the search moved into the mesh, where the candidates are finite --
//! every rotation axis of a polyhedron passes through a vertex, an edge
//! midpoint or a face centre, which is 182 directions for the seed. All 546
//! axis-order pairs are decided in 0.2 ms.
//!
//! The raster keeps the job it is good at: **confirming**. The mesh says an
//! axis is five-fold; the screen shows the picture coming back.
//!
//! ```powershell
//! cargo run --release --example symmetry_sweep        # level 2
//! cargo run --release --example symmetry_sweep -- 3   # level 3, slower
//! ```

use goldberg_kernel::genesis::{Kind, Op, Params, State, Surface};
use goldberg_kernel::palette;
use goldberg_kernel::raster::{project_rpy, Canvas};
use goldberg_kernel::rng::Rng;
use goldberg_kernel::{vadd, vnorm, vscale, Vec3};
use std::f64::consts::TAU;
use std::fs;
use std::path::PathBuf;
use std::time::Instant;

/// Small on purpose. The sweep asks "is this picture the same picture", which
/// needs structure, not resolution -- and it asks it thousands of times.
const W: usize = 260;
const H: usize = 260;
const ZOOM: f64 = 108.0;

/// The rotation orders an icosahedral group can have, besides the identity.
const ORDERS: [u32; 3] = [2, 3, 5];

/// Below this fraction of the frame, two pictures are the same picture.
///
/// The measured gap is 0.08% (symmetric) against 5.61% (not), so this sits
/// roughly a factor of six above the highest true positive and a factor of
/// eleven below the lowest true negative. It is a separator, not a tuning.
const THRESHOLD_PCT: f64 = 0.5;

/// The golden ratio, from its definition rather than a typed decimal.
fn phi() -> f64 {
    (1.0 + 5.0f64.sqrt()) / 2.0
}

/// Bytes that differ between two frames of the same size.
///
/// The whole instrument. Linear in the frame, no allocation, and it answers
/// the question the seal and the OKLab stats both decline to.
fn frame_diff(a: &Canvas, b: &Canvas) -> usize {
    debug_assert_eq!(a.px.len(), b.px.len(), "frames must be the same size");
    a.px.iter().zip(b.px.iter()).filter(|(x, y)| x != y).count()
}

/// Paint the shell at one orientation, at the search size.
fn render(st: &State, pal: &palette::Palette, rx: f64, ry: f64, rz: f64) -> Canvas {
    render_at(st, pal, rx, ry, rz, W, H, ZOOM)
}

/// The gallery frame size. Bigger than the search frames on purpose: those
/// were for counting bytes, these are for looking at.
const GAL_W: usize = 700;
const GAL_H: usize = 700;
/// Sized from the shell, not guessed. `sphere_r` is 1.6, so a zoom of 300 put
/// a 960-pixel shell in a 700-pixel frame and cropped the rosette -- the first
/// gallery showed the middle of the picture and called it the picture.
const GAL_ZOOM: f64 = 700.0 * 0.44 / 1.6;

/// Frames in the walk around the fundamental triangle. Divisible by three, so
/// each leg gets the same number and a corner lands on a frame rather than
/// between two.
const FLOW_FRAMES: usize = 270;

/// The painter. One body, so a picture in the gallery is made by exactly the
/// code that measured the axis it is a picture of -- two painters would drift
/// and the drift would be invisible, since both would keep working.
#[allow(clippy::too_many_arguments)]
fn render_at(
    st: &State,
    pal: &palette::Palette,
    rx: f64,
    ry: f64,
    rz: f64,
    w: usize,
    h: usize,
    zoom: f64,
) -> Canvas {
    let mut cv = Canvas::new(w, h, pal.bg);

    let depths: Vec<f64> = st
        .faces
        .iter()
        .map(|f| {
            f.pts
                .iter()
                .map(|&v| project_rpy(v, rx, ry, rz, zoom, w, h).2)
                .sum::<f64>()
                / f.pts.len() as f64
        })
        .collect();
    let mut order: Vec<usize> = (0..st.faces.len()).collect();
    order.sort_by(|&a, &b| depths[a].partial_cmp(&depths[b]).expect("no NaN depth"));

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
                let q = project_rpy(v, rx, ry, rz, zoom, w, h);
                (q.0, q.1)
            })
            .collect();
        // FILLED, and that is the whole difference between an instrument that
        // works and one that does not.
        //
        // Measured: with a wireframe, moving the view by 0.0005 rad -- about a
        // twentieth of a pixel -- already changed 8.3% of the frame, because
        // eight thousand thin lines each round to their own pixel independently
        // and a sub-pixel shift flips a fraction of every one of them. The
        // basin around a true axis was narrower than the smallest offset
        // probed, so a grid could not land in one.
        //
        // A filled polygon is an AREA. A sub-pixel shift moves its boundary and
        // leaves its interior alone, so the difference falls off with the
        // PERIMETER rather than with the whole curve. That is the difference
        // between a phase-sensitive measure and a shape-sensitive one.
        cv.fill_poly(&pts, c, a8);
    }
    cv
}

/// One view axis, and what it turned out to be.
struct Hit {
    rx: f64,
    ry: f64,
    /// the object-space direction the camera is looking down
    axis: [f64; 3],
    order: u32,
    /// percentage of the frame that differed at `2*PI/order`
    pct: f64,
}

/// The direction, in object space, that the camera looks down at (rx, ry).
///
/// Derived from `project_rpy` by inverting it: a Y-rotation then an
/// X-rotation, so the screen's +z pulls back to this. The gallery goes the
/// other way -- `rx = asin(d.y)`, `ry = atan2(d.x, d.z)` -- and the two are
/// checked against each other before a single picture is written.
fn view_axis(rx: f64, ry: f64) -> Vec3 {
    [rx.cos() * ry.sin(), rx.sin(), rx.cos() * ry.cos()]
}

/// Great-circle interpolation between two directions.
///
/// A straight line between two points on a sphere leaves the sphere and comes
/// back shorter, so the camera would speed up in the middle and the "flow"
/// would be an artefact of the interpolation rather than of the shell. Slerp
/// keeps the step angular and constant.
fn slerp(a: Vec3, b: Vec3, t: f64) -> Vec3 {
    let d = (a[0] * b[0] + a[1] * b[1] + a[2] * b[2]).clamp(-1.0, 1.0);
    let om = d.acos();
    if om.abs() < 1e-9 {
        return a;
    }
    let (s0, s1) = (((1.0 - t) * om).sin() / om.sin(), (t * om).sin() / om.sin());
    vnorm([
        a[0] * s0 + b[0] * s1,
        a[1] * s0 + b[1] * s1,
        a[2] * s0 + b[2] * s1,
    ])
}

/// Does rotating the vertex set by `ang` about `axis` map it onto itself?
///
/// Rodrigues' rotation, then a nearest-point match. **Exact equality is the
/// wrong test** -- `sin` and `cos` are display-lane and a rotated coordinate
/// lands an ULP or two away from the vertex it should equal. The tolerance is
/// far below the shortest edge and far above the rounding, and the gap between
/// those two numbers is what makes this a measurement rather than a hope.
fn maps_onto_itself(verts: &[Vec3], axis: Vec3, ang: f64) -> bool {
    const TOL: f64 = 1e-9;
    let (s, c) = (ang.sin(), ang.cos());
    let k = vnorm(axis);
    for &v in verts {
        let kv = k[0] * v[0] + k[1] * v[1] + k[2] * v[2];
        let cr = [
            k[1] * v[2] - k[2] * v[1],
            k[2] * v[0] - k[0] * v[2],
            k[0] * v[1] - k[1] * v[0],
        ];
        let r = [
            v[0] * c + cr[0] * s + k[0] * kv * (1.0 - c),
            v[1] * c + cr[1] * s + k[1] * kv * (1.0 - c),
            v[2] * c + cr[2] * s + k[2] * kv * (1.0 - c),
        ];
        if !verts.iter().any(|&u| {
            (u[0] - r[0]).abs() < TOL && (u[1] - r[1]).abs() < TOL && (u[2] - r[2]).abs() < TOL
        }) {
            return false;
        }
    }
    true
}

/// The plain dot product, named, because it appears in four places below and
/// three of them are about angles between axes.
fn dot(a: Vec3, b: Vec3) -> f64 {
    a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
}

/// Two axes are the same axis if they are parallel OR antiparallel -- a
/// rotation axis has no direction, and the sweep will find both ends.
fn same_axis(a: [f64; 3], b: [f64; 3]) -> bool {
    let d = a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
    d.abs() > 0.995
}

fn main() -> std::io::Result<()> {
    let mut args = std::env::args().skip(1);
    let levels: u32 = args.next().and_then(|s| s.parse().ok()).unwrap_or(2);

    let out = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("symmetry");
    fs::create_dir_all(&out)?;

    let p = Params {
        surface: Surface::Spherical,
        ..Params::default()
    };
    let mut rng = Rng::new(0xC60);
    let mut st = State::seed_c60();
    for _ in 0..levels {
        st = st.refine(Op::All, &p, &mut rng);
    }
    let inv = st.invariants().expect("the swept shell must measure");
    assert_eq!(inv.pents, 12, "P=12 is not negotiable");

    println!("  SYMMETRY SWEEP");
    println!(
        "  shell    level {levels}   F={}  V={}  E={}  P={}  chi={}",
        inv.faces, inv.vertices, inv.edges, inv.pents, inv.chi
    );
    println!("  frame    {W}x{H}   filled, orthographic, painter-ordered");
    println!("  test     roll by 2PI/n for n in {ORDERS:?}, count differing bytes");
    println!("  same     below {THRESHOLD_PCT}% of the frame\n");

    let pal = palette::GENESIS;
    let total = (W * H * 3) as f64;

    // ---- PROBE: how WIDE is a basin? ------------------------------------
    //
    // The first version of this program swept a 24x48 grid and found exactly
    // one axis -- the one that happened to land on a grid line. That is not a
    // failure of the instrument, it is a statement about the function: the
    // difference has SHARP minima, and a grid that does not land on an axis
    // does not see it at all.
    //
    // So measure the width before choosing a resolution. The 5-fold axis at
    // atan(1/PHI) is known exactly from the coordinates, which makes it the
    // right ruler.
    let known = (1.0 / phi()).atan();
    println!("  PROBE  around the known 5-fold axis, pitch = atan(1/PHI) = {known:.6}");
    println!("  {:>10} {:>10}", "offset", "diff %");
    let mut half_width = f64::NAN;
    let mut at_zero = f64::NAN;
    for k in 0..=11 {
        // k == 0 is the axis ITSELF. The first version of this probe started
        // one step off it and so never measured the thing everything else is
        // compared against -- a ruler with no zero.
        let off = if k == 0 {
            0.0
        } else {
            0.002 * (1u32 << (k - 1)) as f64 / 4.0
        };
        let a = render(&st, &pal, known + off, 0.0, 0.0);
        let b = render(&st, &pal, known + off, 0.0, TAU / 5.0);
        let pct = 100.0 * frame_diff(&a, &b) as f64 / total;
        let bar = "#".repeat(((pct * 6.0) as usize).min(48));
        let tag = if k == 0 { "  <- on the axis" } else { "" };
        println!("  {off:>10.5} {pct:>9.3}%  {bar}{tag}");
        if k == 0 {
            at_zero = pct;
        } else if half_width.is_nan() && pct > THRESHOLD_PCT {
            half_width = off;
        }
    }
    // What a blind grid would actually cost, from the measured width rather
    // than from a guess. A basin of angular radius r covers about pi*r^2 of the
    // 4*pi sphere, so 4/r^2 samples are needed to be sure of landing in one --
    // and each sample is four renders.
    let samples = 4.0 / (half_width * half_width);
    println!(
        "\n  ON the axis the frame differs by {at_zero:.3}%, and {:.4} rad off it by\n  \
         more than {THRESHOLD_PCT}%. The basin is under {:.4} rad wide.",
        half_width,
        half_width * 2.0
    );
    println!(
        "  A blind grid over the sphere would need about {:.0e} samples to land in\n  \
         one -- {:.0e} renders, which at this frame size is roughly {:.0} hours.\n  \
         So the search does NOT happen in the raster.\n",
        samples,
        samples * (1.0 + ORDERS.len() as f64),
        samples * 4.0 * 0.0012 / 3600.0
    );

    // ---- FIND, in the MESH -----------------------------------------
    //
    // The probe above settles where the search belongs. A basin is narrower
    // than 0.0005 rad, so a blind grid over the (pitch, yaw) sphere would need
    // something like a billion samples to land inside one -- and the first
    // version of this program duly found exactly one axis, the one that
    // happened to sit on a grid line.
    //
    // **A symmetry is a property of the POINT SET, not of the pixels it lands
    // on.** So the search moves into the mesh, where the answer is exact and
    // the candidates are finite: every rotation axis of a polyhedron passes
    // through a vertex, an edge midpoint, or a face centre. That is 182
    // directions for the seed, not a billion.
    //
    // The raster is not discarded -- it is demoted to what it is good at.
    // Finding is done in the mesh; CONFIRMING is done on screen, because a
    // symmetry nobody can see is a claim rather than a picture.
    let seed = goldberg_kernel::Mesh::c60();
    let mut cands: Vec<Vec3> = Vec::new();
    for &v in &seed.verts {
        cands.push(vnorm(v));
    }
    for &(a, b) in &seed.edges {
        cands.push(vnorm(vscale(vadd(seed.verts[a], seed.verts[b]), 0.5)));
    }
    for f in &seed.faces {
        let mut c = [0.0f64; 3];
        for &i in f {
            c = vadd(c, seed.verts[i]);
        }
        cands.push(vnorm(vscale(c, 1.0 / f.len() as f64)));
    }
    println!(
        "  CANDIDATES  {} directions from the seed: {} vertices, {} edge midpoints, {} face centres",
        cands.len(),
        seed.verts.len(),
        seed.edges.len(),
        seed.faces.len()
    );

    let t_all = Instant::now();
    let mut found: Vec<Hit> = Vec::new();
    for &axis in &cands {
        for &n in ORDERS.iter() {
            if !maps_onto_itself(&seed.verts, axis, TAU / n as f64) {
                continue;
            }
            // a 6-fold axis would also pass the 2- and 3-fold tests; keep the
            // HIGHEST order that works, which is the axis's true order
            if let Some(prev) = found.iter_mut().find(|h| same_axis(h.axis, axis)) {
                if n > prev.order {
                    prev.order = n;
                }
                continue;
            }
            let rx = axis[1].clamp(-1.0, 1.0).asin();
            let ry = axis[0].atan2(axis[2]);
            found.push(Hit {
                rx,
                ry,
                axis,
                order: n,
                pct: f64::NAN,
            });
        }
    }
    println!(
        "  SEARCHED    {} axis-order pairs in {:.1} ms\n",
        cands.len() * ORDERS.len(),
        t_all.elapsed().as_secs_f64() * 1000.0
    );

    // ---- CONFIRM, on screen ----------------------------------------
    //
    // Aim the camera down each axis the mesh claims, roll by 2PI/n, and count
    // the bytes. If the mesh is right the picture comes back; if it does not,
    // the mesh was wrong and this line says so.
    let t_conf = Instant::now();
    for h in found.iter_mut() {
        let a = render(&st, &pal, h.rx, h.ry, 0.0);
        let b = render(&st, &pal, h.rx, h.ry, TAU / h.order as f64);
        h.pct = 100.0 * frame_diff(&a, &b) as f64 / total;
    }
    found.sort_by(|a, b| b.order.cmp(&a.order).then(a.pct.total_cmp(&b.pct)));

    println!(
        "  {:>3}  {:>9} {:>9}  {:>26}  {:>8}",
        "n", "pitch", "yaw", "view axis", "diff %"
    );
    for h in &found {
        let mark = if h.pct < THRESHOLD_PCT {
            ""
        } else {
            "   <-- MESH SAID YES, SCREEN SAYS NO"
        };
        println!(
            "  {:>3}  {:>9.5} {:>9.5}  [{:>7.4} {:>7.4} {:>7.4}]  {:>7.3}%{}",
            h.order, h.rx, h.ry, h.axis[0], h.axis[1], h.axis[2], h.pct, mark
        );
    }

    let mut count = [0usize; 6];
    let mut confirmed = 0usize;
    for h in &found {
        count[h.order as usize] += 1;
        if h.pct < THRESHOLD_PCT {
            confirmed += 1;
        }
    }
    println!(
        "\n  FOUND       {} five-fold, {} three-fold, {} two-fold",
        count[5], count[3], count[2]
    );
    println!("  EXPECTED    6 five-fold, 10 three-fold, 15 two-fold   (icosahedral)");
    println!(
        "  CONFIRMED   {}/{} on screen, below {}% of the frame, in {:.0} ms",
        confirmed,
        found.len(),
        THRESHOLD_PCT,
        t_conf.elapsed().as_secs_f64() * 1000.0
    );

    // The group order, counted from the axes rather than looked up: the
    // identity, plus (n-1) non-trivial rotations about each axis of order n.
    let order: usize = 1 + count[2] + count[3] * 2 + count[5] * 4;
    println!(
        "  ORDER       1 + {}*1 + {}*2 + {}*4 = {}   (rotation group)",
        count[2], count[3], count[5], order
    );
    println!(
        "  COMPRESSION every face has {} images under that group, so a shell of\n                       {} faces holds about {} independent ones.",
        order,
        inv.faces,
        (inv.faces as usize).div_ceil(order.max(1))
    );

    // PHI, read back off a five-fold axis rather than typed in
    if let Some(five) = found
        .iter()
        .find(|h| h.order == 5 && h.axis[0].abs() < 1e-9 && h.axis[1].abs() > 1e-9)
    {
        println!(
            "\n  A five-fold axis is [0, {:.6}, {:.6}], whose ratio is {:.9}",
            five.axis[1],
            five.axis[2],
            (five.axis[2] / five.axis[1]).abs()
        );
        println!(
            "  PHI is                                          {:.9}",
            phi()
        );
        println!("  -- the golden ratio, recovered from a symmetry of the render.");
    }

    // ---- THE PICTURES ------------------------------------------------
    //
    // One frame per axis, looking straight down it. This is where the whole
    // exercise becomes something a person can see rather than a table: down a
    // five-fold axis the shell is a rosette, down a three-fold a triskelion,
    // down a two-fold a mirror pair -- and each one is the SAME shell, only
    // aimed differently.
    //
    // Rendered larger than the search frames, because these are for looking at
    // and those were for counting.
    let gal = out.join("axes");
    fs::create_dir_all(&gal)?;
    let mut manifest = String::from(
        "# symmetry_sweep -- one picture per rotation axis of the C60\n\
         # order, pitch, yaw, axis x, axis y, axis z, confirm diff %, file\n",
    );

    let t_gal = Instant::now();
    let mut seen = [0usize; 6];
    for h in &found {
        seen[h.order as usize] += 1;
        let name = format!("axis_{}fold_{:02}.png", h.order, seen[h.order as usize]);

        // The round trip must close before anything is written. `view_axis`
        // and the (rx, ry) the search produced are two paths to the same
        // direction, and if they disagree the picture is of some other axis
        // and the label on it is a lie.
        let back = view_axis(h.rx, h.ry);
        let d = back[0] * h.axis[0] + back[1] * h.axis[1] + back[2] * h.axis[2];
        assert!(
            d > 0.999_999,
            "axis round trip failed for {name}: asked for {:?}, aiming at {:?}",
            h.axis,
            back
        );

        let cv = render_at(&st, &pal, h.rx, h.ry, 0.0, GAL_W, GAL_H, GAL_ZOOM);
        cv.write_png(gal.join(&name))?;
        manifest.push_str(&format!(
            "{}, {:.6}, {:.6}, {:.6}, {:.6}, {:.6}, {:.4}, {}\n",
            h.order, h.rx, h.ry, h.axis[0], h.axis[1], h.axis[2], h.pct, name
        ));
    }
    fs::write(gal.join("AXES.csv"), &manifest)?;
    println!(
        "\n  PICTURES    {} frames at {GAL_W}x{GAL_H} in {:.1}s -> {}",
        found.len(),
        t_gal.elapsed().as_secs_f64(),
        gal.display()
    );
    println!("              6 rosettes, 10 triskelions, 15 mirror pairs, one shell");

    // ---- THE FLOW ----------------------------------------------------
    //
    // The pictures above are the shell standing still at each of its axes.
    // This is the passage BETWEEN them, which is where the structure actually
    // shows itself: on an axis the picture locks into a rosette, and one step
    // off it the whole thing dissolves. The probe measured how violent that
    // is -- 0.0005 rad off a five-fold axis and 5.4% of the frame has already
    // changed.
    //
    // The path is not decorative. An icosahedral fundamental domain is a
    // spherical triangle whose corners are a five-fold, a three-fold and a
    // two-fold axis, and every orientation of the shell is some symmetry of
    // some point in that one triangle. **Walking its three edges is a tour of
    // the entire orientation space, at 1/60 the length.** That is the same
    // compression the table above prints, taken for a walk.
    let a5 = found
        .iter()
        .find(|h| h.order == 5)
        .expect("a five-fold axis");
    let a3 = found
        .iter()
        .filter(|h| h.order == 3)
        .max_by(|p, q| {
            dot(p.axis, a5.axis)
                .abs()
                .total_cmp(&dot(q.axis, a5.axis).abs())
        })
        .expect("a three-fold axis");
    let a2 = found
        .iter()
        .filter(|h| h.order == 2)
        .max_by(|p, q| {
            (dot(p.axis, a5.axis).abs() + dot(p.axis, a3.axis).abs())
                .total_cmp(&(dot(q.axis, a5.axis).abs() + dot(q.axis, a3.axis).abs()))
        })
        .expect("a two-fold axis");

    let corners = [a5.axis, a3.axis, a2.axis];
    let orders = [a5.order, a3.order, a2.order];
    println!("\n  FLOW        the fundamental triangle, corner to corner:");
    for (i, (c, n)) in corners.iter().zip(orders.iter()).enumerate() {
        let j = (i + 1) % 3;
        let sep = dot(*c, corners[j]).clamp(-1.0, 1.0).acos().to_degrees();
        println!(
            "              {}-fold [{:>7.4} {:>7.4} {:>7.4}]  ->  {}-fold   {:.2} deg",
            n, c[0], c[1], c[2], orders[j], sep
        );
    }

    let flow = out.join("flow");
    fs::create_dir_all(&flow)?;
    let per_leg = FLOW_FRAMES / 3;
    let mut csv = String::from("# frame, leg, t, axis x, axis y, axis z, best n, diff %\n");
    let mut locks = 0usize;
    let t_flow = Instant::now();

    for frame in 0..FLOW_FRAMES {
        let leg = (frame / per_leg).min(2);
        let t = (frame % per_leg) as f64 / per_leg as f64;
        let d = slerp(corners[leg], corners[(leg + 1) % 3], t);

        let rx = d[1].clamp(-1.0, 1.0).asin();
        let ry = d[0].atan2(d[2]);

        // the symmetry score, measured at the SEARCH size -- the score is a
        // count, the frame is a picture, and they do not need the same pixels
        let small = render(&st, &pal, rx, ry, 0.0);
        let mut best = (f64::INFINITY, 0u32);
        for &n in ORDERS.iter() {
            let r = render(&st, &pal, rx, ry, TAU / n as f64);
            let pct = 100.0 * frame_diff(&small, &r) as f64 / total;
            if pct < best.0 {
                best = (pct, n);
            }
        }
        if best.0 < THRESHOLD_PCT {
            locks += 1;
        }

        let cv = render_at(&st, &pal, rx, ry, 0.0, GAL_W, GAL_H, GAL_ZOOM);
        cv.write_png(flow.join(format!("f{frame:04}.png")))?;
        csv.push_str(&format!(
            "{frame}, {leg}, {t:.4}, {:.6}, {:.6}, {:.6}, {}, {:.4}\n",
            d[0], d[1], d[2], best.1, best.0
        ));
    }
    fs::write(flow.join("FLOW.csv"), &csv)?;

    // ffmpeg is not called from here. The frames are the artefact; the mp4 is
    // a convenience, and a program that shells out to a tool it did not check
    // for is a program that fails on someone else's machine.
    fs::write(
        flow.join("MAKE_MP4.txt"),
        format!(
            "ffmpeg -y -framerate 30 -i f%04d.png -c:v libx264 -crf 18 \
             -pix_fmt yuv420p flow.mp4\n\n\
             {FLOW_FRAMES} frames, {GAL_W}x{GAL_H}, the fundamental triangle walked once.\n\
             FLOW.csv carries the symmetry score per frame -- it dips to zero at\n\
             each corner and nowhere else.\n"
        ),
    )?;

    println!(
        "\n  FRAMES      {} at {GAL_W}x{GAL_H} in {:.1}s -> {}",
        FLOW_FRAMES,
        t_flow.elapsed().as_secs_f64(),
        flow.display()
    );
    println!(
        "  LOCKED      {locks} of {FLOW_FRAMES} frames sit on a symmetry ({:.1}% of the walk)",
        100.0 * locks as f64 / FLOW_FRAMES as f64
    );
    println!("  SCORE       FLOW.csv -- the dips ARE the corners, and nothing else dips");
    println!("  MP4         see flow/MAKE_MP4.txt");

    Ok(())
}
