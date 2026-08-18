//! THE BIT MATRIX -- 1s and 0s as the payload, numbers only as commentary.
//!
//! "we write all in 1 and 0s ... we could use hex but no ... we will pay a bit
//! more price in compute and use the numbers as comments"
//!
//! So a `.bits` file is literally the characters `0` and `1`, laid out as a
//! matrix. Every decimal figure lives in the header, above a line that says
//! where commentary stops. The price is exactly 8 bytes on disk per byte of
//! payload, paid on purpose.
//!
//! # Why bother
//!
//! A hex dump is already a compression -- it asks your eye to decode a symbol
//! back into four bits. A 1/0 matrix asks nothing: the file *is* the state, and
//! when it is laid out in rows the eye reads structure directly. Broken
//! symmetry shows up as visible texture, which is the entire premise.
//!
//! # Lanes
//!
//! CERTIFIED throughout. `u8` in, ASCII out, integer digest. No float, no
//! clock inside the digest (Curse 38) -- two dumps of the same bytes are
//! byte-identical, so a `.bits` file is a receipt.

use std::fmt::Write as _;
use std::io;
use std::path::Path;

/// What a dump covers, and what it left out. Truncation is always reported --
/// a silently clipped dump reads as a complete one (Path IV).
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct DumpReport {
    /// bytes actually written as 1s and 0s
    pub bytes_written: usize,
    /// bytes in the source
    pub bytes_total: usize,
    /// characters of `0`/`1` emitted
    pub bits_written: usize,
    /// rows in the matrix
    pub rows: usize,
    pub cols: usize,
    /// FNV-1a over the SOURCE bytes covered -- the receipt
    pub digest: u64,
    pub truncated: bool,
}

impl DumpReport {
    pub fn coverage_pct(&self) -> f64 {
        if self.bytes_total == 0 {
            100.0
        } else {
            100.0 * self.bytes_written as f64 / self.bytes_total as f64
        }
    }
}

/// FNV-1a, 64-bit. A change detector, not a cryptographic hash.
pub fn digest(bytes: &[u8]) -> u64 {
    let mut h: u64 = 0xcbf2_9ce4_8422_2325;
    for &b in bytes {
        h ^= b as u64;
        h = h.wrapping_mul(0x0000_0100_0000_01b3);
    }
    h
}

/// Render `bytes` as a 1/0 matrix with `cols` bits per row, capped at
/// `max_bytes` of source.
///
/// MSB first within each byte, so reading left to right is reading the byte in
/// its written order.
pub fn to_matrix(bytes: &[u8], cols: usize, max_bytes: usize) -> (String, DumpReport) {
    let cols = cols.max(1);
    let take = bytes.len().min(max_bytes);
    let src = &bytes[..take];

    let mut out = String::with_capacity(take * 9);
    let mut in_row = 0usize;
    let mut rows = 0usize;
    for &b in src {
        for k in (0..8).rev() {
            out.push(if b & (1 << k) != 0 { '1' } else { '0' });
            in_row += 1;
            if in_row == cols {
                out.push('\n');
                in_row = 0;
                rows += 1;
            }
        }
    }
    if in_row != 0 {
        out.push('\n');
        rows += 1;
    }

    let rep = DumpReport {
        bytes_written: take,
        bytes_total: bytes.len(),
        bits_written: take * 8,
        rows,
        cols,
        digest: digest(src),
        truncated: take < bytes.len(),
    };
    (out, rep)
}

/// The header. Every number in the file lives here, as commentary, above the
/// line that marks where the payload starts.
pub fn header(label: &str, rep: &DumpReport) -> String {
    let mut h = String::new();
    let _ = writeln!(h, "# BIT MATRIX -- the payload below is 1s and 0s only.");
    let _ = writeln!(h, "# Every number on these header lines is a COMMENT.");
    let _ = writeln!(h, "#");
    let _ = writeln!(h, "# source        : {label}");
    let _ = writeln!(
        h,
        "# bytes total   : {}          (0x{:X})",
        rep.bytes_total, rep.bytes_total
    );
    let _ = writeln!(
        h,
        "# bytes written : {}          (0x{:X})",
        rep.bytes_written, rep.bytes_written
    );
    let _ = writeln!(h, "# bits written  : {}", rep.bits_written);
    let _ = writeln!(h, "# matrix        : {} rows x {} cols", rep.rows, rep.cols);
    let _ = writeln!(h, "# coverage      : {:.4}%", rep.coverage_pct());
    let _ = writeln!(
        h,
        "# truncated     : {}{}",
        rep.truncated,
        if rep.truncated {
            "   <-- INCOMPLETE, and saying so"
        } else {
            ""
        }
    );
    let _ = writeln!(h, "# fnv1a64       : {:016x}", rep.digest);
    let _ = writeln!(h, "# bit order     : MSB first within each byte");
    let _ = writeln!(h, "#");
    let _ = writeln!(
        h,
        "# ---- commentary ends. every character below is 0 or 1. ----"
    );
    h
}

/// Write a `.bits` file: header of commentary, then nothing but `0` and `1`.
pub fn write_bits(
    path: impl AsRef<Path>,
    label: &str,
    bytes: &[u8],
    cols: usize,
    max_bytes: usize,
) -> io::Result<DumpReport> {
    let (body, rep) = to_matrix(bytes, cols, max_bytes);
    let mut all = header(label, &rep);
    all.push_str(&body);
    std::fs::write(path, all)?;
    Ok(rep)
}

/// Write the raw bytes verbatim, for the packed twin of a `.bits` file.
/// The pair is the point: one for the eye, one for the machine, same digest.
pub fn write_packed(
    path: impl AsRef<Path>,
    bytes: &[u8],
    max_bytes: usize,
) -> io::Result<DumpReport> {
    let take = bytes.len().min(max_bytes);
    std::fs::write(path, &bytes[..take])?;
    Ok(DumpReport {
        bytes_written: take,
        bytes_total: bytes.len(),
        bits_written: take * 8,
        rows: 0,
        cols: 0,
        digest: digest(&bytes[..take]),
        truncated: take < bytes.len(),
    })
}

/// Count set bits. The population of a state -- the crudest symmetry measure
/// there is, and the one that moves first when symmetry breaks.
pub fn ones(bytes: &[u8]) -> usize {
    bytes.iter().map(|b| b.count_ones() as usize).sum()
}

/// Shannon entropy in bits per byte, measured over the byte histogram.
///
/// DISPLAY lane -- uses `log2`. Reported, never asserted bit-exactly.
pub fn entropy(bytes: &[u8]) -> f64 {
    if bytes.is_empty() {
        return 0.0;
    }
    let mut hist = [0usize; 256];
    for &b in bytes {
        hist[b as usize] += 1;
    }
    let n = bytes.len() as f64;
    -hist
        .iter()
        .filter(|&&c| c > 0)
        .map(|&c| {
            let p = c as f64 / n;
            p * p.log2()
        })
        .sum::<f64>()
}
