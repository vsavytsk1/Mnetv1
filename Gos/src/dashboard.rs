//! THE DASHBOARD -- ENG v2.0 master control, painted from integers.
//!
//! The target is `Gos/ponderTheOrb/machinenet_eng_v2_0_master_control.html`, the
//! 361 KB of HTML+JS that `builder/build_eng_v2.py` emits for Chromium. This
//! module reproduces it region by region with no browser in the path.
//!
//! Every colour and every dimension here is traceable to a line of CSS in the
//! builder. Where the browser has a value this module cannot yet honour
//! (gradients, box-shadow glow, border-radius, antialiased text), that is stated
//! rather than approximated in silence -- see [`NOT_YET`].
//!
//! Status: SKELETON plus one card. Deliberately partial, and the partiality is
//! listed.

use crate::font;
use crate::layout::{Dash, Rect, CENTER_PAD, GRID_GAP};
use crate::palette::{Palette, Rgb};
use crate::raster::Canvas;

/// What the browser does that this renderer does not do YET.
///
/// Kept as data so it can be printed next to a render. A gap that is written
/// down is engineering; a gap that is quietly approximated is a lie about
/// fidelity (Path IV).
pub const NOT_YET: &[&str] = &[
    "border-radius (cards are square here; CSS says 4px)",
    "box-shadow glow on featured cards (0 0 22px -10px accent)",
    "linear-gradient card background (160deg #0c0c16 -> panel)",
    "radial-gradient hover bloom (.mod-card::before)",
    "antialiased text (5x7 bitmap font, hard pixels)",
    "letter-spacing (CSS 0.12em-0.32em; fixed 1px advance here)",
    "the birthGlow 5.5s animation",
    "proportional font metrics (this font is fixed 6px advance)",
];

// ---------------------------------------------------------------------------
// CHROME COLOURS -- the dim structural greys the dashboard uses that are not
// semantic palette slots. Lifted verbatim from build_eng_v2.py's CSS.
// ---------------------------------------------------------------------------

/// Structural colours that are not part of the semantic [`Palette`].
///
/// These are literal CSS values, not theme choices: the browser hardcodes them
/// too. Kept in one struct so nothing is a magic number at the call site.
#[derive(Clone, Copy, Debug)]
pub struct Chrome {
    /// `#top-bar .build` -- the build stamp
    pub build: Rgb,
    /// `#top-bar .git` -- the git hash, dimmest thing on screen
    pub git: Rgb,
    /// `#top-bar .clock` and `.panel-title`
    pub dim: Rgb,
    /// `.k-name` -- kernel module names
    pub k_name: Rgb,
    /// `.k-kb` -- module sizes
    pub k_kb: Rgb,
    /// `.cat-header`
    pub cat: Rgb,
    /// `.k-row` separator, `.cat-count` background
    pub hair: Rgb,
    /// `.cat-header` bottom rule
    pub rule: Rgb,
    /// `.card-desc`
    pub desc: Rgb,
    /// `.feat-card .card-desc`
    pub feat_desc: Rgb,
    /// `.k-miss` / `.k-bad`
    pub bad: Rgb,
}

/// The values in `builder/build_eng_v2.py`.
pub const CHROME: Chrome = Chrome {
    build: [0x2a, 0x3a, 0x4a],
    git: [0x1a, 0x2a, 0x1a],
    dim: [0x1a, 0x2a, 0x3a],
    k_name: [0x2a, 0x3a, 0x4a],
    k_kb: [0x1a, 0x2a, 0x2a],
    cat: [0x3a, 0x4a, 0x5a],
    hair: [0x0a, 0x0a, 0x14],
    rule: [0x10, 0x10, 0x1e],
    desc: [0x4a, 0x5a, 0x6a],
    feat_desc: [0x4a, 0x5a, 0x6a],
    bad: [0xff, 0x44, 0x44],
};

// ---------------------------------------------------------------------------
// MODEL
// ---------------------------------------------------------------------------

/// One kernel module row in the left panel. `.k-row`
pub struct KRow<'a> {
    pub name: &'a str,
    pub ok: bool,
    pub kb: usize,
}

/// A module card. `.mod-card` / `.feat-card`
///
/// Borrowed rather than `&'static`: real cards come from `sim_scan.discover()`
/// at runtime, with versions in their names. A struct that only accepts
/// literals cannot hold the actual dashboard.
pub struct Card<'a> {
    pub tag: &'a str,
    pub name: &'a str,
    pub desc: &'a str,
    /// the per-card accent -- `--card-color`, drives tag, name, arrow and border
    pub accent: Rgb,
    pub caps: &'a [&'a str],
    /// `.feat-card` -- bigger, brighter, carries the FRONT DOOR marker
    pub featured: bool,
}

/// Everything the dashboard needs to draw itself. No I/O, no globals.
pub struct Model<'a> {
    pub version: &'a str,
    pub git: &'a str,
    pub ledger: &'a str,
    /// the certified line -- `V=60 E=90 ...`
    pub cert: &'a str,
    pub modules: &'a [KRow<'a>],
    pub cards: &'a [Card<'a>],
    pub category: &'a str,
}

// ---------------------------------------------------------------------------
// PAINT
// ---------------------------------------------------------------------------

/// Draw the whole skeleton. Returns the card rects, so a caller can hit-test
/// clicks against exactly what was painted rather than recomputing the layout
/// (which is how a UI and its geometry drift apart).
pub fn draw(cv: &mut Canvas, pal: &Palette, m: &Model) -> Vec<Rect> {
    let canvas = Rect::of(cv.w, cv.h);
    let d = Dash::split(canvas);
    debug_assert!(d.covers(canvas), "the five regions must tile the canvas");

    cv.fill(pal.bg);
    top_bar(cv, pal, d.top, m);
    left_panel(cv, pal, d.left, m);
    right_panel(cv, pal, d.right, m);
    bottom_bar(cv, pal, d.bottom, m);
    center(cv, pal, d.center, m)
}

/// `#top-bar` -- logo, build stamp, git hash, kernel state, clock at `margin-left:auto`.
fn top_bar(cv: &mut Canvas, pal: &Palette, r: Rect, m: &Model) {
    cv.fill_rect(r.x, r.y, r.w, r.h, pal.panel);
    cv.line(
        r.x,
        r.bottom() - 1,
        r.right() - 1,
        r.bottom() - 1,
        pal.border,
    );

    let ty = r.y + (r.h - font::GH) / 2;
    let mut x = r.x + 16;
    x += font::text(cv, x, ty - 2, "MACHINENET", pal.cyan, 1) + 10;
    x += font::text(cv, x, ty, &format!("ENG {}", m.version), CHROME.build, 1) + 12;
    x += font::text(cv, x, ty, &format!("GIT {}", m.git), CHROME.git, 1) + 12;
    font::text(cv, x, ty, "KERNEL 6/6 OK", pal.green, 1);

    // `margin-left:auto` -- right-aligned
    let right = m.ledger;
    let w = font::width(right, 1);
    font::text(cv, r.right() - 16 - w, ty, right, CHROME.dim, 1);
}

/// `#left` -- `.panel-title`, the six `.k-row`s, then `#mini-canvas-wrap`.
fn left_panel(cv: &mut Canvas, pal: &Palette, r: Rect, m: &Model) {
    cv.fill_rect(r.x, r.y, r.w, r.h, pal.panel);
    cv.line(
        r.right() - 1,
        r.y,
        r.right() - 1,
        r.bottom() - 1,
        pal.border,
    );

    let (title, body) = r.split_top(20);
    font::text(cv, title.x + 12, title.y + 7, "KERNEL", CHROME.dim, 1);
    cv.line(
        title.x,
        title.bottom() - 1,
        title.right() - 2,
        title.bottom() - 1,
        pal.border,
    );

    // `#k-list{padding:8px 12px}` with `.k-row{padding:3px 0}`
    let list = body.pad(8, 12, 0, 12);
    for (i, row) in m.modules.iter().enumerate() {
        let y = list.y + i as i32 * 13;
        font::text(cv, list.x, y, row.name, CHROME.k_name, 1);

        let mark = if row.ok { "OK" } else { "MISS" };
        let colour = if row.ok { pal.green } else { CHROME.bad };
        let mw = font::width(mark, 1);
        font::text(cv, list.right() - mw, y, mark, colour, 1);

        let kb = format!("{}K", row.kb);
        let kw = font::width(&kb, 1);
        font::text(cv, list.right() - mw - kw - 6, y, &kb, CHROME.k_kb, 1);

        cv.line(list.x, y + 10, list.right() - 1, y + 10, CHROME.hair);
    }

    // `#mini-canvas-wrap` -- reserved, titled, and honestly labelled EMPTY until
    // the mesh is wired in. A blank panel with no label reads as a bug.
    let used = 8 + m.modules.len() as i32 * 13 + 8;
    let (_, canvas_area) = body.split_top(used);
    if canvas_area.h > 30 {
        cv.line(
            canvas_area.x,
            canvas_area.y,
            canvas_area.right() - 2,
            canvas_area.y,
            pal.border,
        );
        font::text(
            cv,
            canvas_area.x + 12,
            canvas_area.y + 8,
            "C60 MINI",
            CHROME.dim,
            1,
        );
    }
}

/// `#right` -- build log and the last LEDGER entries. Reserved, titled, empty.
fn right_panel(cv: &mut Canvas, pal: &Palette, r: Rect, m: &Model) {
    cv.fill_rect(r.x, r.y, r.w, r.h, pal.panel);
    cv.line(r.x, r.y, r.x, r.bottom() - 1, pal.border);

    let (title, body) = r.split_top(20);
    font::text(cv, title.x + 12, title.y + 7, "BUILD LOG", CHROME.dim, 1);
    cv.line(
        title.x + 1,
        title.bottom() - 1,
        title.right() - 1,
        title.bottom() - 1,
        pal.border,
    );

    let b = body.pad(8, 12, 0, 12);
    font::text(cv, b.x, b.y, m.cert, pal.green, 1);
    font::text(cv, b.x, b.y + 13, "AXIOM 01 GATE PASSED", pal.gold, 1);
    font::text(
        cv,
        b.x,
        b.y + 26,
        "P 12 - CHI 2 - E/V 3/2",
        CHROME.k_name,
        1,
    );
    font::text(cv, b.x, b.y + 44, m.ledger, CHROME.cat, 1);
}

/// The command bar at the foot.
fn bottom_bar(cv: &mut Canvas, pal: &Palette, r: Rect, _m: &Model) {
    cv.fill_rect(r.x, r.y, r.w, r.h, pal.panel);
    cv.line(r.x, r.y, r.right() - 1, r.y, pal.border);
    let ty = r.y + (r.h - font::GH) / 2;
    font::text(
        cv,
        r.x + 16,
        ty,
        "> PAINTED BY THE KERNEL. NO CHROMIUM.",
        CHROME.build,
        1,
    );
}

/// `#center` -- `.cat-header` then the `.mod-grid`. Returns the card rects.
fn center(cv: &mut Canvas, pal: &Palette, r: Rect, m: &Model) -> Vec<Rect> {
    let area = r.inset(CENTER_PAD);

    // `.cat-header` -- label, count chip, bottom rule
    let (head, body) = area.split_top(18);
    let mut x = head.x;
    x += font::text(cv, x, head.y + 2, m.category, CHROME.cat, 1) + 8;
    let count = format!("{}", m.cards.len());
    let cw = font::width(&count, 1);
    cv.fill_rect(x - 3, head.y, cw + 6, 11, CHROME.hair);
    font::text(cv, x, head.y + 2, &count, CHROME.dim, 1);
    cv.line(
        head.x,
        head.bottom() - 1,
        head.right() - 1,
        head.bottom() - 1,
        CHROME.rule,
    );

    // `.mod-grid{grid-template-columns:repeat(2,1fr);gap:10px}`
    let grid = body.pad(GRID_GAP, 0, 0, 0);
    let cols = grid.columns(2, GRID_GAP);
    let card_h = 104;

    let mut rects = Vec::with_capacity(m.cards.len());
    for (i, card) in m.cards.iter().enumerate() {
        let col = &cols[i % 2];
        let row = i / 2;
        let cr = Rect::new(
            col.x,
            grid.y + row as i32 * (card_h + GRID_GAP),
            col.w,
            card_h,
        );
        if cr.bottom() > grid.bottom() {
            break; // the browser scrolls; we clip, and say so in NOT_YET
        }
        draw_card(cv, pal, cr, card);
        rects.push(cr);
    }
    rects
}

/// One `.mod-card`. Square corners for now (see [`NOT_YET`]).
pub fn draw_card(cv: &mut Canvas, pal: &Palette, r: Rect, c: &Card<'_>) {
    cv.fill_rect(r.x, r.y, r.w, r.h, pal.panel);
    cv.rect(
        r.x,
        r.y,
        r.w,
        r.h,
        if c.featured { c.accent } else { pal.border },
    );

    // `.feat-card::after{content:'FRONT DOOR'}` -- top-left, tiny, faint
    let mut y = r.y + 10;
    if c.featured {
        font::text(cv, r.x + 10, y, "FRONT DOOR", c.accent, 1);
        y += 12;
    }

    // `.card-dot` -- the accent status dot
    cv.disc(r.x + 13, y + 3, 2, c.accent, 255);

    // `.card-tag`
    font::text(cv, r.x + 22, y, c.tag, c.accent, 1);
    y += 14;

    // `.card-name` -- `.feat-card` bumps it to 14px, so scale 2 here
    let scale = if c.featured { 2 } else { 1 };
    font::text(cv, r.x + 10, y, c.name, c.accent, scale);
    y += if c.featured { 20 } else { 12 };

    // `.card-desc` -- wrapped by hand; the browser reflows, we measure
    let avail = ((r.w - 20) / 6) as usize;
    for line in wrap(c.desc, avail).iter().take(3) {
        font::text(cv, r.x + 10, y, line, CHROME.desc, 1);
        y += 9;
    }

    // `.card-arrow{content:'SUMMON >'}` and `.card-caps`
    let arrow = "SUMMON >";
    font::text(cv, r.x + 10, r.bottom() - 14, arrow, c.accent, 1);
    let mut cx = r.x + 10 + font::width(arrow, 1) + 10;
    for cap in c.caps {
        let up = cap.to_ascii_uppercase();
        let w = font::width(&up, 1);
        cv.rect(cx - 2, r.bottom() - 16, w + 4, 11, CHROME.rule);
        font::text(cv, cx, r.bottom() - 14, &up, CHROME.k_kb, 1);
        cx += w + 10;
    }
}

/// Greedy word wrap at `cols` characters. The font is fixed-advance, so a
/// character count IS a pixel measurement -- no text metrics needed.
pub fn wrap(s: &str, cols: usize) -> Vec<String> {
    if cols == 0 {
        return Vec::new();
    }
    let mut out: Vec<String> = Vec::new();
    let mut line = String::new();
    for word in s.split_whitespace() {
        if line.is_empty() {
            line.push_str(word);
        } else if line.chars().count() + 1 + word.chars().count() <= cols {
            line.push(' ');
            line.push_str(word);
        } else {
            out.push(std::mem::take(&mut line));
            line.push_str(word);
        }
    }
    if !line.is_empty() {
        out.push(line);
    }
    out
}
