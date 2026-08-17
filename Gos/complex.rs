//! Complex arithmetic -- the certified core of the light matrix.
//!
//! THEA's `cadd` `csub` `cmul` `cdiv` `cscl` `cabs` `cpow`, as one `Copy`
//! type. Everything except [`C::powf`] and [`C::exp`] stays on the certified
//! path: `+ - * /` and `sqrt` only, so results are bit-identical to the
//! browser.
//!
//! [`C::abs`] uses `hypot`, which is *not* bit-portable. [`C::norm_sqr`] is
//! the certified alternative -- prefer it for comparisons, where the square
//! root is pure ceremony anyway.

/// A complex number `re + i*im`.
#[derive(Clone, Copy, PartialEq, Debug, Default)]
pub struct C {
    pub re: f64,
    pub im: f64,
}

impl C {
    pub const ZERO: C = C { re: 0.0, im: 0.0 };
    pub const ONE: C = C { re: 1.0, im: 0.0 };
    pub const I: C = C { re: 0.0, im: 1.0 };

    #[inline]
    pub const fn new(re: f64, im: f64) -> C {
        C { re, im }
    }

    /// CERTIFIED. `(a+bi) + (c+di)`
    #[inline]
    pub fn add(self, o: C) -> C {
        C::new(self.re + o.re, self.im + o.im)
    }

    /// CERTIFIED. `(a+bi) - (c+di)`
    #[inline]
    pub fn sub(self, o: C) -> C {
        C::new(self.re - o.re, self.im - o.im)
    }

    /// CERTIFIED. `(ac - bd) + (ad + bc)i`
    #[inline]
    pub fn mul(self, o: C) -> C {
        C::new(
            self.re * o.re - self.im * o.im,
            self.re * o.im + self.im * o.re,
        )
    }

    /// CERTIFIED. Scale by a real.
    #[inline]
    pub fn scale(self, s: f64) -> C {
        C::new(self.re * s, self.im * s)
    }

    /// CERTIFIED. Division by the conjugate. Division by zero yields infinities
    /// rather than panicking -- IEEE-754 behaviour, same as the JS.
    #[inline]
    pub fn div(self, o: C) -> C {
        let d = o.re * o.re + o.im * o.im;
        C::new(
            (self.re * o.re + self.im * o.im) / d,
            (self.im * o.re - self.re * o.im) / d,
        )
    }

    /// CERTIFIED. `a - bi`
    #[inline]
    pub fn conj(self) -> C {
        C::new(self.re, -self.im)
    }

    /// CERTIFIED. `|z|^2`. Prefer this to [`C::abs`] whenever you are only
    /// comparing magnitudes -- it is exact and it is faster.
    #[inline]
    pub fn norm_sqr(self) -> f64 {
        self.re * self.re + self.im * self.im
    }

    /// DISPLAY. `|z|` via `hypot`, which is not bit-portable across platforms.
    #[inline]
    pub fn abs(self) -> f64 {
        self.re.hypot(self.im)
    }

    /// DISPLAY. `arg z` in `(-pi, pi]`.
    #[inline]
    pub fn arg(self) -> f64 {
        self.im.atan2(self.re)
    }

    /// CERTIFIED for non-negative integer exponents: repeated multiplication,
    /// no transcendentals. `z^0 = 1` including for `z = 0`.
    pub fn powi(self, mut n: u32) -> C {
        let mut result = C::ONE;
        let mut base = self;
        while n > 0 {
            if n & 1 == 1 {
                result = result.mul(base);
            }
            base = base.mul(base);
            n >>= 1;
        }
        result
    }

    /// DISPLAY. `e^z`.
    pub fn exp(self) -> C {
        let e = self.re.exp();
        C::new(e * self.im.cos(), e * self.im.sin())
    }

    /// DISPLAY. `z^w` for real `w`, via polar form.
    pub fn powf(self, w: f64) -> C {
        let r = self.abs();
        if r == 0.0 {
            return C::ZERO;
        }
        let t = self.arg() * w;
        let m = r.powf(w);
        C::new(m * t.cos(), m * t.sin())
    }

    /// CERTIFIED. Is every component finite?
    #[inline]
    pub fn is_finite(self) -> bool {
        self.re.is_finite() && self.im.is_finite()
    }
}

impl core::fmt::Display for C {
    fn fmt(&self, w: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        if self.im < 0.0 {
            write!(w, "{}-{}i", self.re, -self.im)
        } else {
            write!(w, "{}+{}i", self.re, self.im)
        }
    }
}

/// CERTIFIED. Stereographic projection of the plane onto the unit sphere.
///
/// `(x, y) -> ( 2x/(1+r^2), 2y/(1+r^2), (r^2-1)/(1+r^2) )`, the map THEA uses
/// at line 1916 to turn each pixel into a point on `S^2`. Only `+ - * /`, so
/// this is bit-identical to the browser -- the whole reason the rasterizer
/// ports cleanly.
///
/// The point at infinity maps to the north pole `(0, 0, 1)`.
pub fn c_to_s2(z: C) -> [f64; 3] {
    let r2 = z.norm_sqr();
    if !r2.is_finite() {
        return [0.0, 0.0, 1.0];
    }
    let d = 1.0 + r2;
    [2.0 * z.re / d, 2.0 * z.im / d, (r2 - 1.0) / d]
}
