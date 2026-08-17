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
    pub fn line_a(&mut self, x0: i32, y0: i32, x1: i32, y1: i32, c: Rgb, a: u8) {
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
            c = if c & 1 != 0 { 0xedb8_8320 ^ (c >> 1) } else { c >> 1 };
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
pub fn project(p: [f64; 3], rx: f64, ry: f64, zoom: f64, w: usize, h: usize) -> (i32, i32, f64) {
    let (x, y, z) = (p[0], p[1], p[2]);
    let (cy, sy) = (ry.cos(), ry.sin());
    let x1 = x * cy - z * sy;
    let z1 = x * sy + z * cy;
    let (crx, srx) = (rx.cos(), rx.sin());
    let y1 = y * crx - z1 * srx;
    let z2 = y * srx + z1 * crx;
    (
        (w as f64 / 2.0 + x1 * zoom).round() as i32,
        (h as f64 / 2.0 - y1 * zoom).round() as i32,
        z2,
    )
}
