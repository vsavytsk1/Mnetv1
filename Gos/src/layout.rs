//! LAYOUT -- just enough box model to hold the dashboard. Integers only.
//!
//! The browser reaches the ENG v2.0 layout through flexbox: a column of
//! `#top-bar / #main / #bar`, with `#main` a row of `#left / #center / #right`
//! and `#center` a two-column grid. Flexbox is a constraint solver, and solving
//! constraints in general is a large problem.
//!
//! The dashboard does not need the general problem. Every division in it is
//! "take a fixed strip off one edge, the rest is the remainder" -- which is four
//! functions and no solver. When a panel eventually needs real flex, that will
//! be a new module and this one will stay honest about what it does.
//!
//! CERTIFIED lane: `i32` throughout. No float, so a layout is reproducible to
//! the pixel and a rect can be asserted in a test.

/// An axis-aligned rectangle in pixels. `Copy`, so splitting never allocates.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct Rect {
    pub x: i32,
    pub y: i32,
    pub w: i32,
    pub h: i32,
}

impl Rect {
    pub const fn new(x: i32, y: i32, w: i32, h: i32) -> Rect {
        Rect { x, y, w, h }
    }

    /// The whole canvas.
    pub const fn of(w: usize, h: usize) -> Rect {
        Rect::new(0, 0, w as i32, h as i32)
    }

    pub const fn right(&self) -> i32 {
        self.x + self.w
    }
    pub const fn bottom(&self) -> i32 {
        self.y + self.h
    }
    pub const fn is_empty(&self) -> bool {
        self.w <= 0 || self.h <= 0
    }

    pub fn contains(&self, px: i32, py: i32) -> bool {
        px >= self.x && px < self.right() && py >= self.y && py < self.bottom()
    }

    /// Take `n` pixels off the top. Returns `(strip, remainder)`.
    ///
    /// Clamped, so an over-large request yields the whole rect and an empty
    /// remainder rather than a negative height (Path IV -- degrade visibly, do
    /// not produce nonsense).
    pub fn split_top(&self, n: i32) -> (Rect, Rect) {
        let n = n.clamp(0, self.h);
        (
            Rect::new(self.x, self.y, self.w, n),
            Rect::new(self.x, self.y + n, self.w, self.h - n),
        )
    }

    pub fn split_bottom(&self, n: i32) -> (Rect, Rect) {
        let n = n.clamp(0, self.h);
        (
            Rect::new(self.x, self.bottom() - n, self.w, n),
            Rect::new(self.x, self.y, self.w, self.h - n),
        )
    }

    pub fn split_left(&self, n: i32) -> (Rect, Rect) {
        let n = n.clamp(0, self.w);
        (
            Rect::new(self.x, self.y, n, self.h),
            Rect::new(self.x + n, self.y, self.w - n, self.h),
        )
    }

    pub fn split_right(&self, n: i32) -> (Rect, Rect) {
        let n = n.clamp(0, self.w);
        (
            Rect::new(self.right() - n, self.y, n, self.h),
            Rect::new(self.x, self.y, self.w - n, self.h),
        )
    }

    /// Shrink by `p` on every side. CSS `padding`.
    pub fn inset(&self, p: i32) -> Rect {
        Rect::new(
            self.x + p,
            self.y + p,
            (self.w - 2 * p).max(0),
            (self.h - 2 * p).max(0),
        )
    }

    /// Shrink per side: CSS order, `padding: t r b l`.
    pub fn pad(&self, t: i32, r: i32, b: i32, l: i32) -> Rect {
        Rect::new(
            self.x + l,
            self.y + t,
            (self.w - l - r).max(0),
            (self.h - t - b).max(0),
        )
    }

    /// Slice into `n` columns with `gap` between them. CSS
    /// `grid-template-columns: repeat(n, 1fr)`.
    ///
    /// Leftover pixels from integer division go to the LAST column, so the row
    /// always fills its parent exactly -- no one-pixel seam at the right edge.
    pub fn columns(&self, n: usize, gap: i32) -> Vec<Rect> {
        if n == 0 {
            return Vec::new();
        }
        let n_i = n as i32;
        let total_gap = gap * (n_i - 1);
        let each = (self.w - total_gap) / n_i;
        (0..n)
            .map(|i| {
                let i_i = i as i32;
                let last = i + 1 == n;
                let x = self.x + i_i * (each + gap);
                let w = if last { self.right() - x } else { each };
                Rect::new(x, self.y, w.max(0), self.h)
            })
            .collect()
    }

    /// Stack `n` rows of height `each` with `gap` between, from the top.
    pub fn rows_of(&self, each: i32, gap: i32, n: usize) -> Vec<Rect> {
        (0..n)
            .map(|i| Rect::new(self.x, self.y + i as i32 * (each + gap), self.w, each))
            .collect()
    }
}

/// The five regions of the ENG v2.0 master control dashboard.
///
/// Sizes lifted from `builder/build_eng_v2.py`: `#top-bar` is 36px, `#left` is
/// 180px, the bottom command bar is a strip, and `#center` / `#right` share the
/// remainder. Each is a stated DESIGN CHOICE traceable to a CSS line.
#[derive(Clone, Copy, Debug)]
pub struct Dash {
    pub top: Rect,
    pub left: Rect,
    pub center: Rect,
    pub right: Rect,
    pub bottom: Rect,
}

/// `#top-bar{height:36px}`
pub const TOP_H: i32 = 36;
/// `#left{width:180px}`
pub const LEFT_W: i32 = 180;
/// the command bar at the foot
pub const BOTTOM_H: i32 = 34;
/// the log / ledger column; the browser lets it flex, we fix it
pub const RIGHT_W: i32 = 260;
/// `#center{padding:16px}`
pub const CENTER_PAD: i32 = 16;
/// `.mod-grid{gap:10px}`
pub const GRID_GAP: i32 = 10;

impl Dash {
    /// Divide a canvas into the five regions. Pure arithmetic, no float.
    pub fn split(canvas: Rect) -> Dash {
        let (top, rest) = canvas.split_top(TOP_H);
        let (bottom, mid) = rest.split_bottom(BOTTOM_H);
        let (left, rest2) = mid.split_left(LEFT_W);
        let (right, center) = rest2.split_right(RIGHT_W);
        Dash {
            top,
            left,
            center,
            right,
            bottom,
        }
    }

    /// Every region, for iteration and for tests.
    pub fn all(&self) -> [Rect; 5] {
        [self.top, self.left, self.center, self.right, self.bottom]
    }

    /// The regions must tile the canvas: no gaps, no overlaps, total area equal.
    /// Cheap enough to assert on every layout.
    pub fn covers(&self, canvas: Rect) -> bool {
        let sum: i32 = self.all().iter().map(|r| r.w * r.h).sum();
        sum == canvas.w * canvas.h
    }
}
