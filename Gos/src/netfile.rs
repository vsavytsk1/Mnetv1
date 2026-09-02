//! `netfile` -- a generated net, carved into bytes and read back.
//!
//! THE TRADE THIS FILE EXISTS TO MEASURE. A level of refinement costs time to
//! compute and bytes to keep. Once a net is on disk, the next run can *load*
//! instead of *build* -- and the question is not which is smaller but which is
//! FASTER, and from which level onward.
//!
//! # What is stored, and what is deliberately thrown away
//!
//! `examples/memory_ladder` measured a level-5 mesh at 182.58 MB, of which
//! **34.7% is `id: String` and `lineage: Vec<usize>`** -- bookkeeping about
//! identity, growing one rung per level, while the geometry stays flat at
//! 144 B/face forever.
//!
//! This format keeps the geometry and drops the bookkeeping:
//!
//! ```text
//!   header   8  magic "GOSNET01"
//!            8  face count, u64 LE
//!            1  surface (0 planar, 1 spherical)
//!            7  reserved, zero
//!   per face 1  kind        0 = hex, 1 = pent
//!            4  level       u32 LE
//!            1  point count
//!            1  anchor      0 = none, else 1..=12 -- the SECOND WITNESS,
//!                           one byte instead of a String
//!            n  points      3 * f64 each, stored as to_bits() LE
//! ```
//!
//! **The f64s are stored as raw bits, never as decimal.** A decimal round trip
//! is the one thing that could silently alter the value being preserved, and
//! this file is supposed to be the receipt that the value did not move.
//!
//! A loaded net therefore has **no `id` and no `lineage`** -- and `from_bytes`
//! says so rather than inventing them. What you get back is the *shape*, which
//! is what `invariants()`, `judge` and the renderer all consume. What you lose
//! is the *provenance*, which only `undo` and the id display ever used.
//!
//! LANE: EXACT. Every byte is integer or an f64 bit pattern; nothing here is
//! computed, rounded, or approximated.

use crate::genesis::{Face, Kind, State, Surface};

/// The eight bytes that say this is one of ours.
pub const MAGIC: &[u8; 8] = b"GOSNET01";
/// Header size: magic + count + surface + reserved.
pub const HEADER: usize = 24;

/// Why a net file could not be read.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum NetError {
    /// the first eight bytes were not `GOSNET01`
    BadMagic,
    /// the file ended in the middle of something
    Truncated { at: usize, need: usize },
    /// a face claimed a point count no Goldberg face has
    BadArity { face: usize, pts: u8 },
    /// the header promised more faces than the bytes hold
    ShortCount { promised: u64, got: u64 },
}

/// Bytes a net of this many faces will occupy, exactly.
///
/// A pure function of the counts, so a caller can price a save before making
/// one -- the same discipline the movie writer uses.
pub fn bytes_for(pents: u64, hexes: u64) -> u64 {
    // per face: kind + level + npts + anchor = 7, then 24 B per point
    HEADER as u64 + pents * (7 + 5 * 24) + hexes * (7 + 6 * 24)
}

/// Writes the net. The inverse of [`from_bytes`].
pub fn to_bytes(st: &State, surface: Surface) -> Vec<u8> {
    let (mut p, mut h) = (0u64, 0u64);
    for f in &st.faces {
        if f.kind == Kind::Pent {
            p += 1
        } else {
            h += 1
        }
    }
    let mut out = Vec::with_capacity(bytes_for(p, h) as usize);
    out.extend_from_slice(MAGIC);
    out.extend_from_slice(&(st.faces.len() as u64).to_le_bytes());
    out.push(match surface {
        Surface::Planar => 0,
        Surface::Spherical => 1,
    });
    out.extend_from_slice(&[0u8; 7]);

    for f in &st.faces {
        out.push(if f.kind == Kind::Pent { 1 } else { 0 });
        out.extend_from_slice(&f.level.to_le_bytes());
        out.push(f.pts.len() as u8);
        // The anchor as ONE BYTE. It is a String on the face because the
        // browser mints it as text, but it only ever takes twelve values and
        // its whole job is to be counted. A byte counts identically.
        out.push(match &f.anchor {
            None => 0,
            Some(a) => anchor_byte(a),
        });
        for v in &f.pts {
            for c in v {
                out.extend_from_slice(&c.to_bits().to_le_bytes());
            }
        }
    }
    out
}

/// Maps an anchor string to 1..=255, stably, by its trailing digits.
///
/// The twelve anchors are minted as `F0`..`F11` on the seed and inherited
/// verbatim, so the digits ARE the identity. Anything unparseable becomes 255
/// -- distinct from 0 (no anchor) so a malformed anchor cannot masquerade as
/// an absent one.
fn anchor_byte(a: &str) -> u8 {
    let digits: String = a.chars().filter(|c| c.is_ascii_digit()).collect();
    match digits.parse::<u16>() {
        Ok(n) if n < 255 => (n + 1) as u8,
        _ => 255,
    }
}

/// Reads a net back. The inverse of [`to_bytes`], for geometry.
///
/// The returned faces carry **empty `id` and `lineage`**: this format does not
/// store them, and inventing plausible ones would be worse than admitting the
/// gap. `history` is empty for the same reason -- a loaded net has no past to
/// undo into.
pub fn from_bytes(b: &[u8]) -> Result<(State, Surface), NetError> {
    if b.len() < HEADER {
        return Err(NetError::Truncated {
            at: b.len(),
            need: HEADER,
        });
    }
    if &b[..8] != MAGIC {
        return Err(NetError::BadMagic);
    }
    let n = u64::from_le_bytes(b[8..16].try_into().unwrap());
    let surface = if b[16] == 1 {
        Surface::Spherical
    } else {
        Surface::Planar
    };

    let mut faces = Vec::with_capacity(n as usize);
    let mut o = HEADER;
    for i in 0..n as usize {
        if o + 7 > b.len() {
            return Err(NetError::Truncated { at: o, need: o + 7 });
        }
        let kind = if b[o] == 1 { Kind::Pent } else { Kind::Hex };
        let level = u32::from_le_bytes(b[o + 1..o + 5].try_into().unwrap());
        let npts = b[o + 5];
        let anchor = b[o + 6];
        o += 7;
        if npts != 5 && npts != 6 {
            return Err(NetError::BadArity { face: i, pts: npts });
        }
        let need = o + npts as usize * 24;
        if need > b.len() {
            return Err(NetError::Truncated { at: o, need });
        }
        let mut pts = Vec::with_capacity(npts as usize);
        for _ in 0..npts {
            let mut v = [0f64; 3];
            for c in v.iter_mut() {
                *c = f64::from_bits(u64::from_le_bytes(b[o..o + 8].try_into().unwrap()));
                o += 8;
            }
            pts.push(v);
        }
        faces.push(Face {
            pts,
            kind,
            level,
            lineage: Vec::new(),
            id: String::new(),
            anchor: if anchor == 0 {
                None
            } else {
                Some(format!("F{}", anchor - 1))
            },
        });
    }
    if faces.len() as u64 != n {
        return Err(NetError::ShortCount {
            promised: n,
            got: faces.len() as u64,
        });
    }
    Ok((
        State {
            faces,
            history: Vec::new(),
            counter: 0,
        },
        surface,
    ))
}
