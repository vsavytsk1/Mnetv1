//! THE RASTER -- pixels without Chromium. Zero dependencies, including the PNG.
//!
//! The dashboard currently reaches your eye like this:
//!
//! ```text
//!   build_eng_v2.py -> HTML + JS -> (mysteriously) 1s and 0s
//!                   -> Chromium (another 1s and 0s package) -> pixels
//! ```
//!
//! This module removes the middle two boxes. A [`Canvas`] is a flat `Vec<u8>`
//! of sRGB triples; nothing between the mathematics and the pixel.
//!
//! # Lanes (RULE 0)
//!
//! * **CERTIFIED** -- every colour is `[u8; 3]`, every coordinate an `i32`, and
//!   [`Canvas::line`] is integer Bresenham. Two renders of the same geometry
//!   through the same palette are **bit-identical by construction**, so a
//!   render can be hashed and compared like any other receipt.
//! * **DISPLAY** -- [`project`] uses `sin`/`cos`, so screen positions are not
//!   bit-portable. That is fine: it decides *where* a pixel lands, never *what
//!   colour it is*.
//!
//! # The PNG
//!
//! Written by hand in about eighty lines: CRC-32, Adler-32, and a zlib stream
//! of **stored** (uncompressed) deflate blocks. Files are large and perfectly
//! valid. Adding a compression crate to shrink them would cost the empty
//! `[dependencies]` that RULE 0's fourth row rests on -- a bad trade for bytes
//! on disk.

use std::io;
use std::path::Path;

use crate::palette::Rgb;

/// An RGB framebuffer. Row-major, 3 bytes per pixel, no padding.
#[derive(Clone)]
pub struct Canvas {
    pub w: usize,
    pub h: usize,
    pub px: Vec<u8>,
}

impl Canvas {
    pub fn new(w: usize, h: usize, bg: Rgb) -> Canvas {
        let mut c = Canvas {
            w,
            h,
            px: vec![0u8; w * h * 3],
        };
        c.fill(bg);
        c
    }

    pub fn fill(&mut self, c: Rgb) {
        for p in self.px.chunks_exact_mut(3) {
            p.copy_from_slice(&c);
        }
    }

    /// CERTIFIED. Out-of-bounds writes are dropped, never wrapped.
    #[inline]
    pub fn set(&mut self, x: i32, y: i32, c: Rgb) {
        if x < 0 || y < 0 || x as usize >= self.w || y as usize >= self.h {
            return;
        }
        let i = (y as usize * self.w + x as usize) * 3;
        self.px[i..i + 3].copy_from_slice(&c);
    }

    #[inline]
    pub fn get(&self, x: usize, y: usize) -> Rgb {
        let i = (y * self.w + x) * 3;
        [self.px[i], self.px[i + 1], self.px[i + 2]]
    }

    /// CERTIFIED. `a` is 0..=255. Integer blend with rounding -- no float, so
    /// the result is reproducible on any machine.
    #[inline]
    /// Alpha-fills a polygon by scanline, even-odd rule.
    ///
    /// DISPLAY LANE. This is the browser's `cx.fill()` after `beginPath` /
    /// `lineTo` / `closePath`, and canvas fills with the **non-zero** winding
    /// rule by default. Even-odd and non-zero differ only for
    /// **self-intersecting** polygons; a Goldberg face is convex, so on this
    /// mesh the two rules agree exactly. Written down because the day someone
    /// fills a non-convex face here, this comment is the bug report.
    ///
    /// Half-open rows (`y0 <= y < y1`) so shared horizontal edges between
    /// neighbouring faces are painted once, not twice -- face soup means every
    /// interior edge is drawn by both of its owners, and double-blending a
    /// translucent fill would draw a visible seam along every shared edge.
    pub fn fill_poly(&mut self, pts: &[(i32, i32)], c: Rgb, a: u8) {
        if pts.len() < 3 || a == 0 {
            return;
        }
        let mut ymin = i32::MAX;
        let mut ymax = i32::MIN;
        for &(_, y) in pts {
            ymin = ymin.min(y);
            ymax = ymax.max(y);
        }
        // clip to the canvas before looping: a face can project far off-screen
        // at high zoom, and scanning its full height would cost the same as
        // drawing it
        ymin = ymin.max(0);
        ymax = ymax.min(self.h as i32 - 1);
        if ymin > ymax {
            return;
        }

        let n = pts.len();
        let mut xs: Vec<i32> = Vec::with_capacity(8);
        for y in ymin..=ymax {
            xs.clear();
            for i in 0..n {
                let (x0, y0) = pts[i];
                let (x1, y1) = pts[(i + 1) % n];
                if y0 == y1 {
                    continue; // horizontal edges contribute no crossing
                }
                let (lo, hi) = if y0 < y1 { (y0, y1) } else { (y1, y0) };
                // half-open: the top row counts, the bottom row does not
                if y < lo || y >= hi {
                    continue;
                }
                // integer-safe crossing: i64 because (dx * dy) overflows i32
                // at the zoom levels this viewer actually reaches
                let dx = (x1 - x0) as i64;
                let dy = (y1 - y0) as i64;
                let t = (y - y0) as i64;
                xs.push(x0 + (dx * t / dy) as i32);
            }
            if xs.len() < 2 {
                continue;
            }
            xs.sort_unstable();
            let mut i = 0;
            while i + 1 < xs.len() {
                let (mut xa, xb) = (xs[i], xs[i + 1]);
                // HALF-OPEN IN X TOO, for the same reason as the rows: a
                // span [xa, xb) means two faces sharing a vertical edge blend
                // it once between them. Inclusive here painted one column too
                // many -- an 8-wide square came out 9 -- and every vertical
                // interior edge would have carried a double-blended seam.
                if xb > 0 && xa < self.w as i32 {
                    xa = xa.max(0);
                    let xe = xb.min(self.w as i32);
                    for x in xa..xe {
                        self.blend(x, y, c, a);
                    }
                }
                i += 2;
            }
        }
    }

    pub fn blend(&mut self, x: i32, y: i32, c: Rgb, a: u8) {
        if x < 0 || y < 0 || x as usize >= self.w || y as usize >= self.h {
            return;
        }
        let i = (y as usize * self.w + x as usize) * 3;
        let a = a as u32;
        for (dst, &src) in self.px[i..i + 3].iter_mut().zip(c.iter()) {
            let d = *dst as u32;
            *dst = (((src as u32 * a) + (d * (255 - a)) + 127) / 255) as u8;
        }
    }

    /// CERTIFIED. Integer Bresenham -- no float touches the pixel positions.
    pub fn line(&mut self, x0: i32, y0: i32, x1: i32, y1: i32, c: Rgb) {
        let (dx, dy) = ((x1 - x0).abs(), -(y1 - y0).abs());
        let (sx, sy) = (if x0 < x1 { 1 } else { -1 }, if y0 < y1 { 1 } else { -1 });
        let (mut x, mut y, mut err) = (x0, y0, dx + dy);
        loop {
            self.set(x, y, c);
            if x == x1 && y == y1 {
                break;
            }
            let e2 = 2 * err;
            if e2 >= dy {
                err += dy;
                x += sx;
            }
            if e2 <= dx {
                err += dx;
                y += sy;
            }
        }
    }

    /// The same line, drawn at partial strength. Used for depth cueing.
    /// Cohen--Sutherland: trim a segment to the canvas, or reject it entirely.
    ///
    /// Returns `None` when nothing of the line is on screen -- which at high
    /// zoom is almost all of them, and is exactly the work worth not doing.
    ///
    /// **A fully visible line is returned unchanged**, so the common case is
    /// two comparisons and no arithmetic, and its rasterisation is bit-for-bit
    /// what it was before clipping existed.
    fn clip(
        &self,
        mut x0: i32,
        mut y0: i32,
        mut x1: i32,
        mut y1: i32,
    ) -> Option<(i32, i32, i32, i32)> {
        let (w, h) = (self.w as i32 - 1, self.h as i32 - 1);
        let code = |x: i32, y: i32| -> u8 {
            let mut c = 0u8;
            if x < 0 {
                c |= 1;
            } else if x > w {
                c |= 2;
            }
            if y < 0 {
                c |= 4;
            } else if y > h {
                c |= 8;
            }
            c
        };
        let (mut c0, mut c1) = (code(x0, y0), code(x1, y1));
        loop {
            if c0 | c1 == 0 {
                return Some((x0, y0, x1, y1)); // wholly inside
            }
            if c0 & c1 != 0 {
                return None; // wholly outside, on one side
            }
            let out = if c0 != 0 { c0 } else { c1 };
            // f64 for the intersection: this is the DISPLAY lane, a pixel
            // boundary, and integer division here would bias every clipped
            // endpoint toward zero
            let (dx, dy) = ((x1 - x0) as f64, (y1 - y0) as f64);
            let (nx, ny) = if out & 8 != 0 {
                (x0 as f64 + dx * (h - y0) as f64 / dy, h as f64)
            } else if out & 4 != 0 {
                (x0 as f64 + dx * (0 - y0) as f64 / dy, 0.0)
            } else if out & 2 != 0 {
                (w as f64, y0 as f64 + dy * (w - x0) as f64 / dx)
            } else {
                (0.0, y0 as f64 + dy * (0 - x0) as f64 / dx)
            };
            if !nx.is_finite() || !ny.is_finite() {
                return None;
            }
            let (nx, ny) = (nx.round() as i32, ny.round() as i32);
            if out == c0 {
                x0 = nx;
                y0 = ny;
                c0 = code(x0, y0);
            } else {
                x1 = nx;
                y1 = ny;
                c1 = code(x1, y1);
            }
        }
    }

    pub fn line_a(&mut self, x0: i32, y0: i32, x1: i32, y1: i32, c: Rgb, a: u8) {
        // CLIP FIRST, or the cost is the line's FULL length rather than its
        // visible one.
        //
        // Bresenham below walks one pixel per step and `blend` discards the
        // out-of-bounds ones, so an entirely off-screen line still costs every
        // pixel it would have covered. That is fine at zoom 1 and unbounded as
        // zoom grows: at 480,212 faces and a 400,000-pixel span it is over a
        // trillion iterations, which is a hang and not a slowdown.
        //
        // A line already fully inside is trivially accepted and takes the
        // IDENTICAL path it took before, so nothing that was visible changes.
        let (x0, y0, x1, y1) = match self.clip(x0, y0, x1, y1) {
            Some(v) => v,
            None => return,
        };
        let (dx, dy) = ((x1 - x0).abs(), -(y1 - y0).abs());
        let (sx, sy) = (if x0 < x1 { 1 } else { -1 }, if y0 < y1 { 1 } else { -1 });
        let (mut x, mut y, mut err) = (x0, y0, dx + dy);
        loop {
            self.blend(x, y, c, a);
            if x == x1 && y == y1 {
                break;
            }
            let e2 = 2 * err;
            if e2 >= dy {
                err += dy;
                x += sx;
            }
            if e2 <= dx {
                err += dx;
                y += sy;
            }
        }
    }

    /// A filled disc, for the atoms.
    pub fn disc(&mut self, cx: i32, cy: i32, r: i32, c: Rgb, a: u8) {
        for dy in -r..=r {
            for dx in -r..=r {
                if dx * dx + dy * dy <= r * r {
                    self.blend(cx + dx, cy + dy, c, a);
                }
            }
        }
    }

    /// An axis-aligned rectangle outline, one pixel wide.
    pub fn rect(&mut self, x: i32, y: i32, w: i32, h: i32, c: Rgb) {
        self.line(x, y, x + w - 1, y, c);
        self.line(x, y + h - 1, x + w - 1, y + h - 1, c);
        self.line(x, y, x, y + h - 1, c);
        self.line(x + w - 1, y, x + w - 1, y + h - 1, c);
    }

    pub fn fill_rect(&mut self, x: i32, y: i32, w: i32, h: i32, c: Rgb) {
        for yy in y..y + h {
            for xx in x..x + w {
                self.set(xx, yy, c);
            }
        }
    }

    /// A content hash of the pixels. Two renders of the same frame through the
    /// same palette must produce the same digest -- that is what makes a render
    /// a receipt rather than a screenshot (Curse 38: hash the math).
    pub fn digest(&self) -> u64 {
        // FNV-1a, 64-bit. Not cryptographic; a change detector.
        let mut h: u64 = 0xcbf2_9ce4_8422_2325;
        for &b in &self.px {
            h ^= b as u64;
            h = h.wrapping_mul(0x0000_0100_0000_01b3);
        }
        h
    }

    /// Exact integer upscale: every pixel becomes an `n` x `n` block.
    ///
    /// Nearest-neighbour, no interpolation, **no new colours introduced** -- the
    /// output histogram is the input histogram with every count multiplied by
    /// `n^2`. For this renderer that is not a compromise but the correct
    /// operation: a 5x7 bitmap font and integer Bresenham lines carry no
    /// sub-pixel information, so any smooth filter would be **inventing
    /// detail that was never computed** (Path IV -- incomplete is fine, fake
    /// is not).
    ///
    /// Where genuine detail exists -- a shell with 81,920 faces -- render at the
    /// larger size natively instead. This is for the hard-pixel figures.
    pub fn upscale(&self, n: usize) -> Canvas {
        let n = n.max(1);
        let (w, h) = (self.w * n, self.h * n);
        let mut out = Canvas {
            w,
            h,
            px: vec![0u8; w * h * 3],
        };
        for y in 0..self.h {
            for x in 0..self.w {
                let c = self.get(x, y);
                for dy in 0..n {
                    let row = (y * n + dy) * w;
                    for dx in 0..n {
                        let i = (row + x * n + dx) * 3;
                        out.px[i..i + 3].copy_from_slice(&c);
                    }
                }
            }
        }
        out
    }

    /// The largest integer `n` with `w*n <= tw` and `h*n <= th`. At least 1.
    pub fn fit_scale(&self, tw: usize, th: usize) -> usize {
        ((tw / self.w.max(1)).min(th / self.h.max(1))).max(1)
    }

    /// Write the native PNG and an exact 4K-class upscale beside it.
    ///
    /// Returns `(native_path, k4_path, scale)`. The seal of the upscale is a
    /// pure function of the native seal and `n`, so the receipt still holds.
    pub fn write_png_4k(&self, path: impl AsRef<Path>) -> io::Result<(usize, usize, usize)> {
        let p = path.as_ref();
        self.write_png(p)?;
        let n = self.fit_scale(3840, 2160);
        let big = self.upscale(n);
        let k4 = p.with_file_name(format!(
            "{}_4k.png",
            p.file_stem().unwrap_or_default().to_string_lossy()
        ));
        big.write_png(k4)?;
        Ok((big.w, big.h, n))
    }

    pub fn write_png(&self, path: impl AsRef<Path>) -> io::Result<()> {
        std::fs::write(path, self.to_png())
    }

    /// Encode as PNG: 8-bit truecolour, stored deflate. No dependencies.
    pub fn to_png(&self) -> Vec<u8> {
        // raw scanlines, each prefixed with filter byte 0
        let mut raw = Vec::with_capacity(self.h * (1 + self.w * 3));
        for y in 0..self.h {
            raw.push(0u8);
            let s = y * self.w * 3;
            raw.extend_from_slice(&self.px[s..s + self.w * 3]);
        }

        let mut out = vec![137, 80, 78, 71, 13, 10, 26, 10];

        let mut ihdr = Vec::with_capacity(13);
        ihdr.extend_from_slice(&(self.w as u32).to_be_bytes());
        ihdr.extend_from_slice(&(self.h as u32).to_be_bytes());
        ihdr.extend_from_slice(&[8, 2, 0, 0, 0]); // depth 8, truecolour
        push_chunk(&mut out, b"IHDR", &ihdr);
        push_chunk(&mut out, b"IDAT", &zlib_stored(&raw));
        push_chunk(&mut out, b"IEND", &[]);
        out
    }
}

/// Exactly how many bytes [`Canvas::to_png`] will produce for a `w x h` canvas.
///
/// **This is a real prediction, not an estimate.** Our encoder uses *stored*
/// (uncompressed) deflate, so the output size depends on nothing but the
/// dimensions -- not on the image, not on the palette, not on how much of the
/// frame is black. That property was found by noticing two renders weighed the
/// same to the byte, and it is what lets a movie be PRICED BEFORE THE FIRST
/// FRAME IS WRITTEN rather than discovered at frame 400 (Curse 35).
///
/// ```text
///   raw     = (w*3 + 1) * h        scanlines, each with its filter byte
///   blocks  = ceil(raw / 65535)    stored deflate blocks
///   bytes   = raw + blocks*5 + 6 + 57
///                        |     |    |
///                        |     |    +-- 8 signature + 25 IHDR + 12 IEND + 12 IDAT
///                        |     +------- zlib header (2) + adler32 (4)
///                        +------------- 1 flag + 2 len + 2 ~len per block
/// ```
///
/// The scale this exists to make visible:
///
/// ```text
///   1920x1080    5.93 MB/frame     60 frames    0.35 GB
///   3840x2160   23.73 MB/frame     60 frames    1.39 GB
///   7680x4320   94.93 MB/frame     60 frames    5.56 GB
/// ```
///
/// **One 8K frame is 94.93 MB** -- five megabytes short of the 100 MB limit
/// that bounces an entire push (Curse 31). Nothing at that size may ever be
/// tracked, and the caller must be told the number before it allocates.
pub const fn png_bytes(w: usize, h: usize) -> usize {
    let raw = (w * 3 + 1) * h;
    let blocks = raw.div_ceil(65535);
    raw + blocks * 5 + 6 + 57
}

fn push_chunk(out: &mut Vec<u8>, tag: &[u8; 4], data: &[u8]) {
    out.extend_from_slice(&(data.len() as u32).to_be_bytes());
    let start = out.len();
    out.extend_from_slice(tag);
    out.extend_from_slice(data);
    let crc = crc32(&out[start..]);
    out.extend_from_slice(&crc.to_be_bytes());
}

/// A zlib stream whose deflate blocks are all "stored" -- valid, and trivial.
fn zlib_stored(data: &[u8]) -> Vec<u8> {
    let mut z = vec![0x78, 0x01];
    let mut i = 0usize;
    if data.is_empty() {
        z.extend_from_slice(&[0x01, 0, 0, 0xff, 0xff]);
    }
    while i < data.len() {
        let n = usize::min(65535, data.len() - i);
        let last = i + n == data.len();
        z.push(if last { 1 } else { 0 });
        z.extend_from_slice(&(n as u16).to_le_bytes());
        z.extend_from_slice(&(!(n as u16)).to_le_bytes());
        z.extend_from_slice(&data[i..i + n]);
        i += n;
    }
    z.extend_from_slice(&adler32(data).to_be_bytes());
    z
}

fn crc32(buf: &[u8]) -> u32 {
    let mut c: u32 = 0xffff_ffff;
    for &b in buf {
        c ^= b as u32;
        for _ in 0..8 {
            c = if c & 1 != 0 {
                0xedb8_8320 ^ (c >> 1)
            } else {
                c >> 1
            };
        }
    }
    c ^ 0xffff_ffff
}

fn adler32(buf: &[u8]) -> u32 {
    let (mut a, mut b) = (1u32, 0u32);
    for &x in buf {
        a = (a + x as u32) % 65521;
        b = (b + a) % 65521;
    }
    (b << 16) | a
}

// ===========================================================================
// PROJECTION -- the DISPLAY lane. Decides WHERE, never WHAT COLOUR.
// ===========================================================================

/// genesis' own orthographic `project()`, ported. No perspective divide: a
/// distance and an FOV cannot imitate it, they change the silhouette.
///
/// Returns `(screen_x, screen_y, depth)`.
/// The same projection with all three axes, in yaw-pitch-roll order.
///
/// `project` is this with `rz = 0`, and delegates to it -- one implementation,
/// so the two can never disagree about what a rotation means.
///
/// ```text
///   yaw    ry   about Y, the vertical -- the turn
///   pitch  rx   about X, after the yaw -- tips the pole toward you
///   roll   rz   in the SCREEN PLANE, after projection -- spins the picture
/// ```
///
/// Roll is applied last and in 2D on purpose. Once the shell is flattened, a
/// rotation of the image and a rotation of the camera about the view axis are
/// the same thing, and doing it in 2D is two multiplies instead of nine.
///
/// **DISPLAY lane.** `sin` and `cos` are not correctly rounded by IEEE-754, so
/// nothing here may be asserted bit-identical across a language seam (RULE 0).
pub fn project_rpy(
    p: [f64; 3],
    rx: f64,
    ry: f64,
    rz: f64,
    zoom: f64,
    w: usize,
    h: usize,
) -> (i32, i32, f64) {
    let (x, y, z) = (p[0], p[1], p[2]);
    let (cy, sy) = (ry.cos(), ry.sin());
    let x1 = x * cy - z * sy;
    let z1 = x * sy + z * cy;
    let (crx, srx) = (rx.cos(), rx.sin());
    let y1 = y * crx - z1 * srx;
    let z2 = y * srx + z1 * crx;
    // roll, in the plane, after the shell is already flat
    let (cz, sz) = (rz.cos(), rz.sin());
    let (x2, y2) = (x1 * cz - y1 * sz, x1 * sz + y1 * cz);
    (
        (w as f64 / 2.0 + x2 * zoom).round() as i32,
        (h as f64 / 2.0 - y2 * zoom).round() as i32,
        z2,
    )
}

pub fn project(p: [f64; 3], rx: f64, ry: f64, zoom: f64, w: usize, h: usize) -> (i32, i32, f64) {
    project_rpy(p, rx, ry, 0.0, zoom, w, h)
}
