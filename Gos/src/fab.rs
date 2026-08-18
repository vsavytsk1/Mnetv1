//! # fab -- where the graph stops being ours
//!
//! Every module before this one is the cave talking to itself. This one is the
//! cave talking to a machine that has never heard of us: a photoplotter, a
//! drill, a printer, a mill. Those machines eat a very small number of very old
//! file formats, and they do not negotiate.
//!
//! ## The discovery that justifies the whole crate
//!
//! **A Gerber file has no floating-point numbers in it.**
//!
//! RS-274X declares a coordinate format up front -- we emit `%FSLAX46Y46*%`,
//! meaning *4 integer digits, 6 decimal digits* -- and every coordinate after
//! that is a **plain integer** in units of 10^-6 mm. `X1000000` is 1.000000 mm.
//! Not "approximately". The photoplotter is an integer lattice machine and
//! always was. Same for Excellon drill files. Same for the step count a mill
//! actually executes.
//!
//! So the entire tower -- 1s and 0s, logic gates, assembly, C, C++, Python,
//! float64, the whole scaffold built so a human could hold the complexity --
//! terminates here, at the fab wall, back in **integers on a lattice**. The
//! float was never in the machine. It was in us, the whole time, as a
//! convenience. Compare `RUSTIUM.md` RULE 0: this module is that boundary in
//! its final and most literal form.
//!
//! ```text
//!   idea  ->  graph (certified, integers)  ->  f64 projection (DISPLAY)
//!                                                    |
//!                                            quantise()  <-- THE WALL
//!                                                    v
//!                                    i64 lattice  ->  Gerber / Excellon
//!                                                     -> photoplotter -> copper
//! ```
//!
//! Quantisation is the last place a float can decide anything. It happens in
//! exactly one function, [`quantise`], and it is checked and loud. After it,
//! every byte we write is exact and two runs cannot disagree.
//!
//! ## What is here, and what is honestly not
//!
//! | writer | format | status |
//! |---|---|---|
//! | [`Gerber`] | RS-274X, format 4.6, MM, absolute | copper polylines + flashed pads |
//! | [`Excellon`] | M48 header, METRIC | plated/unplated hits, one tool per diameter |
//! | [`stl_binary`] | binary STL, 50 B/triangle | any [`Mesh`] or [`Ico`], fan-triangulated |
//! | [`dxf_lines`] | DXF R12 ENTITIES, LINE only | 2D outlines, the universal lowest common denominator |
//!
//! **Not built, and not pretended:** no dielectric stackup, so no controlled
//! impedance and no per-trace Z0. No netlist output (IPC-356). No solder mask
//! or paste layers -- a real board needs them and we emit copper and drill
//! only. No arcs (G02/G03): every curve we ever emit is already a polyline,
//! which is not a limitation here but the entire point.
//!
//! **DESIGN CHOICE -- we do not own the fab formats, so we do not judge them.**
//! `judge.rs` certifies the graph. Nothing certifies a Gerber file except the
//! fab's own CAM engineer, and pretending otherwise would be the exact kind of
//! claim this crate exists to refuse. What we *can* promise is that the file we
//! wrote is the graph we certified, quantised once, losslessly within the
//! declared resolution -- and [`Gerber::checksum`] lets a later run prove it.

use crate::{Mesh, Vec3};
use std::fmt::Write as _;
use std::io;
use std::path::Path;

// ---------------------------------------------------------------------------
// THE WALL
// ---------------------------------------------------------------------------

/// Coordinate scale for format 4.6: one integer unit is 10^-6 mm (1 nm).
///
/// 1_000_000 in binary is
/// `11110100001001000000` -- the decimal is the comment, as the cave writes it.
pub const SCALE: i64 = 1_000_000;

/// Format 4.6 allows four integer digits, so the plottable window is
/// +/- 9999.999999 mm. A board bigger than ten metres is a different problem.
pub const MAX_MM: f64 = 9_999.999_999;

/// Why a value could not cross the wall.
#[derive(Clone, Copy, PartialEq, Debug)]
pub enum FabError {
    /// Outside the +/- 9999.999999 mm window that format 4.6 can express.
    OutOfRange(f64),
    /// NaN or infinity reached the wall. Always a bug upstream, never data.
    NotFinite(f64),
    /// An aperture or tool diameter that is zero or negative.
    BadDiameter(f64),
    /// A polyline with fewer than two points draws nothing.
    DegeneratePath(usize),
}

impl std::fmt::Display for FabError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            FabError::OutOfRange(v) => {
                write!(f, "{v} mm is outside the format-4.6 window +/-{MAX_MM} mm")
            }
            FabError::NotFinite(v) => write!(f, "{v} is not finite -- a float bug upstream"),
            FabError::BadDiameter(d) => write!(f, "diameter {d} mm must be > 0"),
            FabError::DegeneratePath(n) => write!(f, "a path of {n} point(s) draws nothing"),
        }
    }
}

impl std::error::Error for FabError {}

/// **The wall itself.** Millimetres (f64, display lane) become lattice units
/// (i64, certified lane). This is the only float-to-integer decision in the
/// export path, and after it nothing can drift.
///
/// Rounds half away from zero, which is what `f64::round` does and what every
/// CAM tool assumes. The rounding is *declared*, not discovered.
///
/// ```
/// use goldberg_kernel::fab::{quantise, SCALE};
/// assert_eq!(quantise(1.0).unwrap(), SCALE);          // 1 mm  == 1_000_000
/// assert_eq!(quantise(0.0).unwrap(), 0);
/// assert_eq!(quantise(-2.5).unwrap(), -2_500_000);
/// assert_eq!(quantise(0.000_000_4).unwrap(), 0);      // below resolution
/// assert_eq!(quantise(0.000_000_6).unwrap(), 1);      // rounds up, declared
/// assert!(quantise(f64::NAN).is_err());
/// ```
pub fn quantise(mm: f64) -> Result<i64, FabError> {
    if !mm.is_finite() {
        return Err(FabError::NotFinite(mm));
    }
    if mm.abs() > MAX_MM {
        return Err(FabError::OutOfRange(mm));
    }
    Ok((mm * SCALE as f64).round() as i64)
}

/// A point that has already crossed the wall. Integers only, no further
/// arithmetic on floats is possible from here.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct Pt {
    pub x: i64,
    pub y: i64,
}

impl Pt {
    /// Cross the wall.
    pub fn at(x_mm: f64, y_mm: f64) -> Result<Self, FabError> {
        Ok(Pt {
            x: quantise(x_mm)?,
            y: quantise(y_mm)?,
        })
    }
}

// ---------------------------------------------------------------------------
// GERBER RS-274X
// ---------------------------------------------------------------------------

/// One copper layer, as the photoplotter reads it.
///
/// Apertures are deduplicated by diameter and numbered from D10 upward, which
/// is the convention every CAM tool expects (D0-D9 are reserved commands).
///
/// ```
/// use goldberg_kernel::fab::Gerber;
/// let mut g = Gerber::new("top copper");
/// g.polyline(&[(0.0, 0.0), (10.0, 0.0), (10.0, 5.0)], 0.2).unwrap();
/// g.flash(10.0, 5.0, 1.6).unwrap();
/// let s = g.finish();
/// assert!(s.starts_with("G04 top copper*"));
/// assert!(s.contains("%FSLAX46Y46*%"));
/// assert!(s.contains("X10000000Y0D01*"));   // integers, all the way down
/// assert!(s.ends_with("M02*\n"));
/// ```
#[derive(Clone, Debug)]
pub struct Gerber {
    title: String,
    /// aperture diameters in lattice units, index + 10 == D-code
    apertures: Vec<i64>,
    /// (aperture index, points) for a stroke; empty points == a flash
    ops: Vec<(usize, Vec<Pt>)>,
}

impl Gerber {
    pub fn new(title: impl Into<String>) -> Self {
        Gerber {
            title: title.into(),
            apertures: Vec::new(),
            ops: Vec::new(),
        }
    }

    /// Find or create the aperture for this diameter. Deduplicated so a board
    /// with one trace width declares one aperture, not one per trace.
    fn aperture(&mut self, dia_mm: f64) -> Result<usize, FabError> {
        if dia_mm.is_nan() || dia_mm <= 0.0 {
            return Err(FabError::BadDiameter(dia_mm));
        }
        let d = quantise(dia_mm)?;
        if let Some(i) = self.apertures.iter().position(|&a| a == d) {
            return Ok(i);
        }
        self.apertures.push(d);
        Ok(self.apertures.len() - 1)
    }

    /// Stroke a polyline in millimetres at the given trace width.
    ///
    /// **There is no arc command here and there never will be.** A curve, in
    /// this crate, is a sufficiently fine polyline -- which is exactly what the
    /// plotter converts an arc into anyway, one step at a time. We simply
    /// decline to launder the discretisation through a fiction.
    pub fn polyline(&mut self, pts_mm: &[(f64, f64)], width_mm: f64) -> Result<(), FabError> {
        if pts_mm.len() < 2 {
            return Err(FabError::DegeneratePath(pts_mm.len()));
        }
        let ap = self.aperture(width_mm)?;
        let mut pts = Vec::with_capacity(pts_mm.len());
        for &(x, y) in pts_mm {
            pts.push(Pt::at(x, y)?);
        }
        self.ops.push((ap, pts));
        Ok(())
    }

    /// Flash a round pad -- one aperture, one exposure, no motion.
    pub fn flash(&mut self, x_mm: f64, y_mm: f64, dia_mm: f64) -> Result<(), FabError> {
        let ap = self.aperture(dia_mm)?;
        self.ops.push((ap, vec![Pt::at(x_mm, y_mm)?]));
        Ok(())
    }

    /// Render the file. Deterministic: same input, same bytes, every run.
    pub fn finish(&self) -> String {
        let mut s = String::with_capacity(256 + self.ops.len() * 48);
        // header
        let _ = writeln!(s, "G04 {}*", self.title);
        let _ = writeln!(s, "G04 generated by goldberg_kernel::fab -- zero deps*");
        s.push_str("%FSLAX46Y46*%\n"); // leading zeros omitted, absolute, 4.6
        s.push_str("%MOMM*%\n"); // millimetres
        s.push_str("%LPD*%\n"); // dark polarity
        for (i, d) in self.apertures.iter().enumerate() {
            // aperture diameters print as decimal mm -- the ONE place the
            // format wants a decimal point, and it is a declaration, not a
            // coordinate. Reconstructed from the integer so it cannot drift.
            let _ = writeln!(s, "%ADD{}C,{}*%", i + 10, fmt_mm(*d));
        }
        // body
        let mut cur_ap = usize::MAX;
        for (ap, pts) in &self.ops {
            if *ap != cur_ap {
                let _ = writeln!(s, "D{}*", ap + 10);
                cur_ap = *ap;
            }
            match pts.len() {
                1 => {
                    // flash: D03
                    let _ = writeln!(s, "X{}Y{}D03*", pts[0].x, pts[0].y);
                }
                _ => {
                    let _ = writeln!(s, "X{}Y{}D02*", pts[0].x, pts[0].y); // move
                    for p in &pts[1..] {
                        let _ = writeln!(s, "X{}Y{}D01*", p.x, p.y); // draw
                    }
                }
            }
        }
        s.push_str("M02*\n");
        s
    }

    /// FNV-1a over the rendered bytes -- the same receipt discipline as
    /// `raster.rs::digest`. Two runs that claim to be the same board must
    /// produce the same number, and a fab that re-plots can prove it got what
    /// we sent.
    pub fn checksum(&self) -> u64 {
        fnv1a(self.finish().as_bytes())
    }

    /// How many distinct trace widths / pad sizes this layer needs.
    pub fn aperture_count(&self) -> usize {
        self.apertures.len()
    }

    pub fn write(&self, path: impl AsRef<Path>) -> io::Result<usize> {
        let s = self.finish();
        std::fs::write(path, s.as_bytes())?;
        Ok(s.len())
    }
}

/// Print a lattice length back as decimal millimetres, trimmed, exactly.
///
/// Integer arithmetic only -- no float ever re-enters the file.
fn fmt_mm(units: i64) -> String {
    let neg = units < 0;
    let u = units.unsigned_abs();
    let whole = u / SCALE as u64;
    let frac = u % SCALE as u64;
    let mut s = if frac == 0 {
        format!("{whole}")
    } else {
        let f = format!("{frac:06}");
        format!("{whole}.{}", f.trim_end_matches('0'))
    };
    if neg {
        s.insert(0, '-');
    }
    s
}

// ---------------------------------------------------------------------------
// EXCELLON DRILL
// ---------------------------------------------------------------------------

/// The drill file. One tool per distinct diameter, hits grouped by tool,
/// because a real drill changes tools slowly and we are not going to make it
/// do that once per hole.
///
/// ```
/// use goldberg_kernel::fab::Excellon;
/// let mut d = Excellon::new();
/// d.hit(1.0, 2.0, 0.8).unwrap();
/// d.hit(5.0, 2.0, 0.8).unwrap();   // same tool, no tool change
/// d.hit(9.0, 2.0, 3.2).unwrap();   // second tool
/// assert_eq!(d.tool_count(), 2);
/// let s = d.finish();
/// assert!(s.starts_with("M48\n"));
/// assert!(s.contains("T1C0.8"));
/// assert!(s.ends_with("M30\n"));
/// ```
#[derive(Clone, Debug, Default)]
pub struct Excellon {
    tools: Vec<i64>,
    hits: Vec<(usize, Pt)>,
}

impl Excellon {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn hit(&mut self, x_mm: f64, y_mm: f64, dia_mm: f64) -> Result<(), FabError> {
        if dia_mm.is_nan() || dia_mm <= 0.0 {
            return Err(FabError::BadDiameter(dia_mm));
        }
        let d = quantise(dia_mm)?;
        let t = match self.tools.iter().position(|&a| a == d) {
            Some(i) => i,
            None => {
                self.tools.push(d);
                self.tools.len() - 1
            }
        };
        self.hits.push((t, Pt::at(x_mm, y_mm)?));
        Ok(())
    }

    pub fn tool_count(&self) -> usize {
        self.tools.len()
    }

    pub fn hit_count(&self) -> usize {
        self.hits.len()
    }

    pub fn finish(&self) -> String {
        let mut s = String::new();
        s.push_str("M48\n");
        s.push_str("; goldberg_kernel::fab -- zero deps\n");
        s.push_str("METRIC,TZ\n");
        for (i, d) in self.tools.iter().enumerate() {
            let _ = writeln!(s, "T{}C{}", i + 1, fmt_mm(*d));
        }
        s.push_str("%\n");
        s.push_str("G90\n"); // absolute
        for (t, _) in self.tools.iter().enumerate() {
            let group: Vec<&Pt> = self
                .hits
                .iter()
                .filter(|(ti, _)| *ti == t)
                .map(|(_, p)| p)
                .collect();
            if group.is_empty() {
                continue;
            }
            let _ = writeln!(s, "T{}", t + 1);
            for p in group {
                let _ = writeln!(s, "X{}Y{}", fmt_mm(p.x), fmt_mm(p.y));
            }
        }
        s.push_str("M30\n");
        s
    }

    pub fn write(&self, path: impl AsRef<Path>) -> io::Result<usize> {
        let s = self.finish();
        std::fs::write(path, s.as_bytes())?;
        Ok(s.len())
    }
}

// ---------------------------------------------------------------------------
// STL -- the shape, for CAD and for the printer
// ---------------------------------------------------------------------------

/// Binary STL from any triangle soup. 84-byte header, then exactly 50 bytes per
/// triangle, so the file length is a checkable invariant -- see the test.
///
/// STL is a *terrible* format: no units, no topology, every vertex repeated
/// three times, and it cannot express that our surface is closed. We emit it
/// anyway because every slicer and every CAD package on earth reads it. **Our
/// closedness lives in `judge.rs`, not in the file** -- the STL is a shadow of
/// a certified object, and the certificate stays home.
pub fn stl_binary(tris: &[[Vec3; 3]], scale_mm: f64) -> Vec<u8> {
    let mut out = Vec::with_capacity(84 + tris.len() * 50);
    out.extend_from_slice(&[0u8; 80]); // header, conventionally ignored
    out.extend_from_slice(&(tris.len() as u32).to_le_bytes());
    for t in tris {
        // facet normal by cross product; a zero normal is legal and means
        // "you work it out", which slicers do anyway
        let u = sub(t[1], t[0]);
        let v = sub(t[2], t[0]);
        let n = norm(cross(u, v));
        for c in n {
            out.extend_from_slice(&(c as f32).to_le_bytes());
        }
        for p in t {
            for c in p {
                out.extend_from_slice(&((c * scale_mm) as f32).to_le_bytes());
            }
        }
        out.extend_from_slice(&0u16.to_le_bytes()); // attribute byte count
    }
    out
}

/// Fan-triangulate a [`Mesh`]'s polygonal faces into a triangle soup.
///
/// A pentagon becomes 3 triangles, a hexagon 4. **COMPUTED:** the C60's
/// 12 pentagons + 20 hexagons give 12*3 + 20*4 = 116 triangles.
pub fn mesh_tris(m: &Mesh) -> Vec<[Vec3; 3]> {
    let mut out = Vec::new();
    for f in &m.faces {
        for i in 1..f.len().saturating_sub(1) {
            out.push([m.verts[f[0]], m.verts[f[i]], m.verts[f[i + 1]]]);
        }
    }
    out
}

// ---------------------------------------------------------------------------
// DXF R12 -- the lowest common denominator
// ---------------------------------------------------------------------------

/// A 2D segment in millimetres: `((x1, y1), (x2, y2))`.
pub type Seg = ((f64, f64), (f64, f64));

/// A minimal DXF R12 with a LINE entity per segment. Every CAD, CAM and laser
/// package reads R12; almost none of them agree on anything newer.
///
/// Group codes are written one per line, value beneath -- the format is a
/// flat key/value stream and is not, despite appearances, indented.
pub fn dxf_lines(segs: &[Seg], layer: &str) -> String {
    let mut s = String::from("0\nSECTION\n2\nENTITIES\n");
    for ((x1, y1), (x2, y2)) in segs {
        let _ = write!(
            s,
            "0\nLINE\n8\n{layer}\n10\n{x1}\n20\n{y1}\n30\n0\n11\n{x2}\n21\n{y2}\n31\n0\n"
        );
    }
    s.push_str("0\nENDSEC\n0\nEOF\n");
    s
}

// ---------------------------------------------------------------------------
// SPHERE -> PLANE, the honest way
// ---------------------------------------------------------------------------

/// Equirectangular unwrap, the same transformer `pcbium` uses:
/// `u = atan2(y,x) / 2pi`, `w = asin(z) / pi`, both in `[-0.5, 0.5]`.
///
/// **DISPLAY LANE -- transcendental, never bit-certified.** `atan2` and `asin`
/// are not correctly rounded, so this must not sit inside an `assert_eq!`.
///
/// **The honest caveat, stated where it can be read:** this projection
/// *stretches near the poles*. A sphere cannot be flattened without
/// concentrating distortion somewhere -- Gauss's *Theorema Egregium*, and the
/// reason the 12 pentagons are unavoidable in the first place. A
/// dimensionally faithful panel needs a conformal or local-patch projection.
/// **Do not send a pole-crossing board to a fab on the strength of this.**
pub fn unwrap_equirect(v: Vec3) -> (f64, f64) {
    let u = v[1].atan2(v[0]) / std::f64::consts::TAU;
    let w = v[2].clamp(-1.0, 1.0).asin() / std::f64::consts::PI;
    (u, w)
}

// ---------------------------------------------------------------------------
// small vector helpers (local, so this module stands alone)
// ---------------------------------------------------------------------------

fn sub(a: Vec3, b: Vec3) -> Vec3 {
    [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
}
fn cross(a: Vec3, b: Vec3) -> Vec3 {
    [
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    ]
}
fn norm(a: Vec3) -> Vec3 {
    let l = (a[0] * a[0] + a[1] * a[1] + a[2] * a[2]).sqrt();
    if l == 0.0 {
        [0.0, 0.0, 0.0]
    } else {
        [a[0] / l, a[1] / l, a[2] / l]
    }
}

fn fnv1a(bytes: &[u8]) -> u64 {
    let mut h: u64 = 0xcbf2_9ce4_8422_2325;
    for &b in bytes {
        h ^= b as u64;
        h = h.wrapping_mul(0x100_0000_01b3);
    }
    h
}

// ---------------------------------------------------------------------------

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn the_wall_is_exact_and_loud() {
        assert_eq!(quantise(1.0).unwrap(), 1_000_000);
        assert_eq!(quantise(-1.0).unwrap(), -1_000_000);
        assert_eq!(quantise(0.1).unwrap(), 100_000);
        // 0.1 is not representable in binary64, but ONE rounding at the wall
        // makes it exact forever after. That is the whole trick.
        assert_eq!(quantise(0.1).unwrap() * 3, 300_000);
        assert!(matches!(
            quantise(f64::INFINITY),
            Err(FabError::NotFinite(_))
        ));
        assert!(matches!(quantise(1e9), Err(FabError::OutOfRange(_))));
    }

    #[test]
    fn fmt_mm_round_trips_without_floats() {
        assert_eq!(fmt_mm(1_000_000), "1");
        assert_eq!(fmt_mm(1_500_000), "1.5");
        assert_eq!(fmt_mm(200_000), "0.2");
        assert_eq!(fmt_mm(1), "0.000001");
        assert_eq!(fmt_mm(-2_500_000), "-2.5");
        assert_eq!(fmt_mm(0), "0");
    }

    #[test]
    fn gerber_has_no_decimal_point_in_any_coordinate() {
        let mut g = Gerber::new("t");
        g.polyline(&[(0.0, 0.0), (1.5, -2.25)], 0.2).unwrap();
        let s = g.finish();
        for line in s.lines() {
            // coordinate lines start with X; only aperture declarations (%AD)
            // are allowed a decimal point anywhere in this file
            if line.starts_with('X') {
                assert!(!line.contains('.'), "float leaked into a coordinate: {line}");
            }
        }
        assert!(s.contains("X1500000Y-2250000D01*"));
    }

    #[test]
    fn apertures_deduplicate() {
        let mut g = Gerber::new("t");
        g.polyline(&[(0.0, 0.0), (1.0, 0.0)], 0.2).unwrap();
        g.polyline(&[(0.0, 1.0), (1.0, 1.0)], 0.2).unwrap();
        g.polyline(&[(0.0, 2.0), (1.0, 2.0)], 0.5).unwrap();
        assert_eq!(g.aperture_count(), 2);
        // and the D-code is emitted only when it changes
        assert_eq!(g.finish().matches("D10*\n").count(), 1);
    }

    #[test]
    fn gerber_is_deterministic() {
        let build = || {
            let mut g = Gerber::new("receipt");
            g.polyline(&[(0.0, 0.0), (3.0, 4.0)], 0.25).unwrap();
            g.flash(3.0, 4.0, 1.0).unwrap();
            g
        };
        assert_eq!(build().checksum(), build().checksum());
        assert_eq!(build().finish(), build().finish());
    }

    #[test]
    fn degenerate_paths_are_refused_not_silently_dropped() {
        let mut g = Gerber::new("t");
        assert!(matches!(
            g.polyline(&[(0.0, 0.0)], 0.2),
            Err(FabError::DegeneratePath(1))
        ));
        assert!(matches!(
            g.polyline(&[(0.0, 0.0), (1.0, 1.0)], 0.0),
            Err(FabError::BadDiameter(_))
        ));
    }

    #[test]
    fn excellon_groups_by_tool() {
        let mut d = Excellon::new();
        d.hit(0.0, 0.0, 0.8).unwrap();
        d.hit(1.0, 0.0, 3.2).unwrap();
        d.hit(2.0, 0.0, 0.8).unwrap();
        assert_eq!(d.tool_count(), 2);
        assert_eq!(d.hit_count(), 3);
        let s = d.finish();
        // exactly one tool change per tool, not one per hit
        assert_eq!(s.matches("\nT1\n").count(), 1);
        assert_eq!(s.matches("\nT2\n").count(), 1);
    }

    #[test]
    fn stl_length_is_exactly_84_plus_50_per_triangle() {
        let m = Mesh::c60();
        let tris = mesh_tris(&m);
        // COMPUTED: 12 pentagons * 3 + 20 hexagons * 4 = 36 + 80 = 116
        assert_eq!(tris.len(), 116);
        let bytes = stl_binary(&tris, 20.0);
        assert_eq!(bytes.len(), 84 + 116 * 50);
        // and the declared count in the header must match reality
        let n = u32::from_le_bytes([bytes[80], bytes[81], bytes[82], bytes[83]]);
        assert_eq!(n as usize, tris.len());
    }

    #[test]
    fn equirect_stays_in_the_unit_square() {
        for v in Mesh::c60().verts {
            let (u, w) = unwrap_equirect(v);
            assert!((-0.5..=0.5).contains(&u), "u out of range: {u}");
            assert!((-0.5..=0.5).contains(&w), "w out of range: {w}");
        }
    }

    #[test]
    fn dxf_is_a_flat_key_value_stream() {
        let s = dxf_lines(&[((0.0, 0.0), (1.0, 1.0))], "COPPER");
        assert!(s.starts_with("0\nSECTION\n"));
        assert!(s.ends_with("0\nEOF\n"));
        assert_eq!(s.matches("\nLINE\n").count(), 1);
    }
}
