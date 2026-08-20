//! OKLab -- measuring a frame in a space where distance means something.
//!
//! # Why not RGB
//!
//! sRGB is a storage format, not a measuring stick. Two pairs of colours the
//! same Euclidean distance apart in RGB can look nothing alike, because the
//! channels are gamma-encoded and the axes are not perceptually orthogonal.
//! Averaging in RGB darkens; a histogram over R, G and B measures the *file*
//! rather than the *picture*.
//!
//! OKLab (Björn Ottosson, 2020) is a perceptual space built for exactly this:
//! a lightness axis `L` and two opponent axes `a`, `b`, tuned so that equal
//! distances look equally different. Chroma is `sqrt(a² + b²)` and hue is the
//! angle. It costs one matrix, three cube roots and one more matrix -- no
//! tables, no white-point negotiation, no dependencies.
//!
//! # Which lane this is
//!
//! **DISPLAY, and it must stay there.** The transfer function uses `powf` and
//! the conversion uses `cbrt`; neither is required to be correctly rounded by
//! IEEE-754, so nothing here may be asserted bit-identical across a language
//! seam (RULE 0). These numbers are measurements *of* a picture, never
//! certificates *about* one. The frame seal remains the integer witness; this
//! is the perceptual one beside it.
//!
//! # What it is for
//!
//! The orb measures the topology of the code's bytes. This measures the
//! topology of the pixels those bytes painted. A frame seal is exact and
//! brittle -- flip one pixel and it moves completely -- so it can say
//! *"different"* and never *"how different"*. [`FrameStats`] answers the
//! second question, and it is what makes a movie's frames comparable to each
//! other rather than merely distinguishable.

use std::collections::HashSet;

/// How far above the background a pixel must sit, in OKLab lightness, to count
/// as ink.
///
/// DESIGN CHOICE. 0.02 is roughly a just-noticeable step in this space -- big
/// enough to reject the faintest antialiasing fringe, small enough to keep the
/// dim tail of a depth-cued line. Stated here so it can be argued with.
pub const INK_STEP: f64 = 0.02;

/// A colour in OKLab: lightness, and two opponent axes.
pub type Lab = [f64; 3];

/// sRGB byte -> linear light. The standard piecewise transfer function.
///
/// DISPLAY: `powf` is not correctly rounded.
#[inline]
pub fn srgb_to_linear(c: u8) -> f64 {
    let x = c as f64 / 255.0;
    if x <= 0.040_45 {
        x / 12.92
    } else {
        ((x + 0.055) / 1.055).powf(2.4)
    }
}

/// sRGB bytes -> OKLab. Ottosson's matrices, verbatim.
pub fn srgb_to_oklab(rgb: [u8; 3]) -> Lab {
    let r = srgb_to_linear(rgb[0]);
    let g = srgb_to_linear(rgb[1]);
    let b = srgb_to_linear(rgb[2]);

    let l = 0.412_221_470_8 * r + 0.536_332_536_3 * g + 0.051_445_992_9 * b;
    let m = 0.211_903_498_2 * r + 0.680_699_545_1 * g + 0.107_396_956_6 * b;
    let s = 0.088_302_461_9 * r + 0.281_718_837_6 * g + 0.629_978_700_5 * b;

    let l_ = l.cbrt();
    let m_ = m.cbrt();
    let s_ = s.cbrt();

    [
        0.210_454_255_3 * l_ + 0.793_617_785_0 * m_ - 0.004_072_046_8 * s_,
        1.977_998_495_1 * l_ - 2.428_592_205_0 * m_ + 0.450_593_709_9 * s_,
        0.025_904_037_1 * l_ + 0.782_771_766_2 * m_ - 0.808_675_766_0 * s_,
    ]
}

/// Chroma: how far from grey, in a space where that distance is meaningful.
#[inline]
pub fn chroma(lab: Lab) -> f64 {
    (lab[1] * lab[1] + lab[2] * lab[2]).sqrt()
}

/// What a rendered frame is made of.
///
/// Every field is COUNTED from the pixels, never inferred from the parameters
/// that produced them.
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct FrameStats {
    /// pixels examined
    pub pixels: usize,
    /// how many distinct 24-bit colours appear -- the frame's real palette,
    /// which for a line renderer is a count of how many blend levels the
    /// alpha compositing actually produced
    pub distinct: usize,
    /// Fraction of pixels perceptibly brighter than the background.
    ///
    /// **The first definition of this was wrong and said so loudly.** It
    /// counted pixels that were not *exactly* the darkest colour, and with
    /// alpha-blended lines almost none are -- it reported 99.7% on every frame
    /// of a sweep and carried no information at all. A number that is the same
    /// for everything is not a measurement (the tautology lesson, in a
    /// histogram).
    ///
    /// It now takes the MODAL lightness as the background -- for these renders
    /// that is the black the canvas is cleared to -- and counts pixels more
    /// than [`INK_STEP`] above it in OKLab L. Perceptual, so the threshold
    /// means the same thing at any brightness.
    pub ink: f64,
    /// mean OKLab lightness, 0..1
    pub mean_l: f64,
    /// mean OKLab chroma
    pub mean_c: f64,
    /// Shannon entropy of the lightness histogram, in bits (0..8).
    ///
    /// A flat black frame is 0. A frame using every lightness evenly is 8.
    /// This is the number that says how much *structure* a picture carries,
    /// as opposed to how many bytes it happens to occupy.
    pub l_entropy: f64,
}

impl FrameStats {
    /// Measure an RGB8 buffer, `w * h * 3` bytes.
    ///
    /// `stride` samples every nth pixel -- at 1920x1080 a full pass is 2.07M
    /// cube roots and that is a real cost, so the caller states what it paid.
    /// `stride = 1` examines everything.
    pub fn measure(px: &[u8], stride: usize) -> FrameStats {
        let stride = stride.max(1);
        let mut seen: HashSet<u32> = HashSet::new();
        let mut hist = [0usize; 256];
        let mut sum_l = 0.0f64;
        let mut sum_c = 0.0f64;
        let mut n = 0usize;

        for p in px.chunks_exact(3).step_by(stride) {
            let key = (p[0] as u32) << 16 | (p[1] as u32) << 8 | p[2] as u32;
            seen.insert(key);
            let lab = srgb_to_oklab([p[0], p[1], p[2]]);
            sum_l += lab[0];
            sum_c += chroma(lab);
            let bin = (lab[0].clamp(0.0, 1.0) * 255.0).round() as usize;
            hist[bin.min(255)] += 1;
            n += 1;
        }

        if n == 0 {
            return FrameStats {
                pixels: 0,
                distinct: 0,
                ink: 0.0,
                mean_l: 0.0,
                mean_c: 0.0,
                l_entropy: 0.0,
            };
        }

        // the background is the MODE, not the minimum: on a cleared canvas the
        // most common lightness IS the clear colour, and a single stray dark
        // pixel cannot move it the way a minimum can
        // Strict `>`, so a TIE keeps the DARKER bin. `max_by_key` returns the
        // last maximum, which on a half-black half-white frame picks WHITE as
        // the background and reports zero ink -- caught by
        // `two_colours_in_equal_measure_is_one_bit`, which is exactly the
        // degenerate case a real frame never shows and a test must.
        let mut bg_bin = 0usize;
        let mut best = 0usize;
        for (i, &c) in hist.iter().enumerate() {
            if c > best {
                best = c;
                bg_bin = i;
            }
        }
        let bg_l = bg_bin as f64 / 255.0;
        let inked: usize = hist
            .iter()
            .enumerate()
            .filter(|(i, _)| (*i as f64 / 255.0) > bg_l + INK_STEP)
            .map(|(_, c)| *c)
            .sum();

        // Shannon entropy of the lightness histogram
        let mut h = 0.0f64;
        for &c in hist.iter() {
            if c > 0 {
                let p = c as f64 / n as f64;
                h -= p * p.log2();
            }
        }

        FrameStats {
            pixels: n,
            distinct: seen.len(),
            ink: inked as f64 / n as f64,
            mean_l: sum_l / n as f64,
            mean_c: sum_c / n as f64,
            l_entropy: h,
        }
    }
}

impl std::fmt::Display for FrameStats {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(
            f,
            "colours {:>6}  ink {:>6.2}%  L {:.4}  C {:.4}  Lent {:.3} bits",
            self.distinct,
            100.0 * self.ink,
            self.mean_l,
            self.mean_c,
            self.l_entropy
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Ottosson's own reference values, to three places. If the matrices were
    /// mistyped this is what says so.
    #[test]
    fn matches_the_reference_conversions() {
        let white = srgb_to_oklab([255, 255, 255]);
        assert!(
            (white[0] - 1.0).abs() < 1e-3,
            "white L must be 1, got {white:?}"
        );
        assert!(chroma(white) < 1e-3, "white must have no chroma");

        let black = srgb_to_oklab([0, 0, 0]);
        assert!(black[0].abs() < 1e-6, "black L must be 0");

        // mid grey sits near L = 0.5 by construction -- that is the whole point
        // of a perceptual space, and it is NOT true of RGB's own midpoint
        let grey = srgb_to_oklab([128, 128, 128]);
        assert!(
            (grey[0] - 0.6).abs() < 0.05,
            "sRGB 128 should land near L=0.6, got {}",
            grey[0]
        );
        assert!(chroma(grey) < 1e-3, "grey must have no chroma");
    }

    /// Red, green and blue must be far apart in hue and all carry chroma.
    #[test]
    fn the_primaries_separate() {
        let r = srgb_to_oklab([255, 0, 0]);
        let g = srgb_to_oklab([0, 255, 0]);
        let b = srgb_to_oklab([0, 0, 255]);
        for (name, c) in [("red", r), ("green", g), ("blue", b)] {
            assert!(chroma(c) > 0.1, "{name} must be chromatic");
        }
        // green is much lighter than blue, which RGB's raw values hide
        assert!(g[0] > b[0] + 0.3, "green must read far lighter than blue");
    }

    /// A flat frame has no structure, and the entropy must say so.
    #[test]
    fn a_flat_frame_has_zero_entropy() {
        let px = vec![17u8; 300];
        let s = FrameStats::measure(&px, 1);
        assert_eq!(s.distinct, 1);
        assert_eq!(s.pixels, 100);
        assert!(s.l_entropy.abs() < 1e-12, "one colour is zero bits");
        assert!(s.ink.abs() < 1e-12, "all background means no ink");
    }

    /// Two colours in equal measure is exactly one bit, and half the frame
    /// is ink. Small enough to check by hand, which is the point.
    #[test]
    fn two_colours_in_equal_measure_is_one_bit() {
        let mut px = Vec::new();
        for i in 0..100 {
            if i % 2 == 0 {
                px.extend_from_slice(&[0, 0, 0]);
            } else {
                px.extend_from_slice(&[255, 255, 255]);
            }
        }
        let s = FrameStats::measure(&px, 1);
        assert_eq!(s.distinct, 2);
        assert!((s.l_entropy - 1.0).abs() < 1e-9, "got {}", s.l_entropy);
        assert!((s.ink - 0.5).abs() < 1e-9, "half of it is not background");
    }

    /// On a tie the DARKER bin is the background. Half black, half white has
    /// no majority, and picking white would report an inkless frame.
    #[test]
    fn a_tied_background_resolves_to_the_darker_bin() {
        let mut px = Vec::new();
        for i in 0..40 {
            if i < 20 {
                px.extend_from_slice(&[0, 0, 0]);
            } else {
                px.extend_from_slice(&[200, 200, 200]);
            }
        }
        let s = FrameStats::measure(&px, 1);
        assert!(
            (s.ink - 0.5).abs() < 1e-9,
            "the bright half must be the ink, got {}",
            s.ink
        );
    }

    /// Sampling must not change what the numbers MEAN, only what they cost.
    #[test]
    fn a_stride_samples_rather_than_lies() {
        let mut px = Vec::new();
        for i in 0..1000u32 {
            let v = (i % 256) as u8;
            px.extend_from_slice(&[v, v, v]);
        }
        let full = FrameStats::measure(&px, 1);
        let sampled = FrameStats::measure(&px, 10);
        assert_eq!(full.pixels, 1000);
        assert_eq!(sampled.pixels, 100);
        // the sample states its own size, so nothing here pretends to be
        // a full measurement
        assert!(
            (full.mean_l - sampled.mean_l).abs() < 0.05,
            "a 1-in-10 sample should track the mean: {} vs {}",
            full.mean_l,
            sampled.mean_l
        );
    }
}
