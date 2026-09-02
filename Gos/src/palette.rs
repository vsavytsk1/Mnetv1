//! THE PALETTES -- exact integers, swappable, nothing hardcoded into a renderer.
//!
//! A palette census across the cave found the same semantic name carrying
//! different bits in different sims:
//!
//! ```text
//!   BG      #030308  dashboard          |  #050508  genesis, byte_sphere, byte_oracle
//!   CYAN    #00d4ff  dashboard, byte_*  |  #00b4ff  genesis
//!   GREEN   #00ffd5  dashboard, genesis |  #7fff7f  byte_sphere, byte_oracle
//!   GOLD    #ffd700  everywhere -- agrees
//!   PINK    #ff69b4  everywhere -- agrees
//! ```
//!
//! That is not filed as a defect. **The mathematics underneath is absolute, so
//! the palette is free** -- these are DESIGN CHOICES, and the point of holding
//! them as data is that we can render the same certified geometry through each
//! one and simply look at which is better.
//!
//! What the census *does* buy us is that a NEW, undeclared value can never
//! sneak in unnoticed: every variant below is named, sourced, and testable.
//!
//! Colours are sRGB `[u8; 3]`. Exact integers -- the CERTIFIED lane. No float
//! enters a colour, so two renders of the same frame through the same palette
//! are bit-identical by construction.

/// One named colour slot.
pub type Rgb = [u8; 3];

/// A named, sourced palette. Every field is an exact integer triple.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub struct Palette {
    pub name: &'static str,
    /// where these bits actually live, so a claim can be checked
    pub source: &'static str,
    pub bg: Rgb,
    pub panel: Rgb,
    pub border: Rgb,
    pub text: Rgb,
    pub bright: Rgb,
    pub cyan: Rgb,
    pub gold: Rgb,
    pub pink: Rgb,
    pub green: Rgb,
    pub purple: Rgb,
    pub orange: Rgb,
}

/// `builder/build_eng_v2.py` `:root{}` -- the ENG v2.0 master control dashboard.
/// This is the artifact the renderer is trying to reproduce, so it is the
/// default ground truth.
/// The browser's GENESIS face fills, lifted verbatim from
/// `shell/genesis_v8.5.2.html` around line 3808:
///
/// ```text
///   pent  fill rgba(193, 74, 59, alpha*0.4)   stroke rgba(255,105,180, alpha)
///   hex   fill rgba(  0, 40, 60, alpha*0.3)   stroke rgba(  0,180,255, alpha*0.6)
/// ```
///
/// These are NOT palette fields, on purpose. A `Palette` varies by theme; the
/// browser has exactly one fill colour per face type, and the port's job is to
/// reproduce THAT picture. Themed fills would be a different render that
/// happened to look similar.
///
/// The strokes already matched before the fills existed: `pink` is
/// `(255,105,180)` and the GENESIS palette's `cyan` is `(0,180,255)` -- the
/// same two numbers the browser strokes with.
pub const GEN_FILL_PENT: Rgb = [193, 74, 59];
/// See [`GEN_FILL_PENT`]. The hexagon fill, `rgba(0,40,60,...)`.
pub const GEN_FILL_HEX: Rgb = [0, 40, 60];

pub const DASHBOARD: Palette = Palette {
    name: "dashboard",
    source: "builder/build_eng_v2.py :root",
    bg: [0x03, 0x03, 0x08],
    panel: [0x07, 0x07, 0x0f],
    border: [0x0e, 0x0e, 0x1e],
    text: [0x90, 0x90, 0xa0],
    bright: [0xd0, 0xd8, 0xe8],
    cyan: [0x00, 0xd4, 0xff],
    gold: [0xff, 0xd7, 0x00],
    pink: [0xff, 0x69, 0xb4],
    green: [0x00, 0xff, 0xd5],
    purple: [0xa7, 0x8b, 0xfa],
    orange: [0xff, 0x90, 0x40],
};

/// `builder/genesis_wallpaper_v1_6.py` `GENESIS_CANVAS` -- the browser's own
/// draw-path constants. Lifts the background two units and cools the cyan.
pub const GENESIS: Palette = Palette {
    name: "genesis",
    source: "builder/genesis_wallpaper_v1_6.py GENESIS_CANVAS",
    bg: [0x05, 0x05, 0x08],
    panel: [0x00, 0x28, 0x3c], // hex_fill
    border: [0x0e, 0x0e, 0x1e],
    text: [0x90, 0x90, 0xa0],
    bright: [0xd0, 0xd8, 0xe8],
    cyan: [0x00, 0xb4, 0xff], // hex_edge
    gold: [0xff, 0xd7, 0x00],
    pink: [0xff, 0x69, 0xb4],  // pent_edge
    green: [0x00, 0xff, 0xd5], // hex_atom
    purple: [0xa7, 0x8b, 0xfa],
    orange: [0xc1, 0x4a, 0x3b], // pent_fill
};

/// `shell/byte_sphere.html` + `shell/byte_oracle.html` -- the byte sims.
/// Same background as genesis, same cyan as the dashboard, and a green of its
/// own that neither of the others uses.
pub const BYTE: Palette = Palette {
    name: "byte",
    source: "shell/byte_sphere.html, shell/byte_oracle.html",
    bg: [0x05, 0x05, 0x08],
    panel: [0x0a, 0x0e, 0x1a],
    border: [0x1a, 0x1f, 0x2e],
    text: [0xdc, 0xe4, 0xf0],
    bright: [0xe6, 0xdd, 0xc7],
    cyan: [0x00, 0xd4, 0xff],
    gold: [0xff, 0xd7, 0x00],
    pink: [0xff, 0x69, 0xb4],
    green: [0x7f, 0xff, 0x7f],
    purple: [0xa7, 0x8b, 0xfa],
    orange: [0xd9, 0xa4, 0x41],
};

/// Every palette the cave declares. A variant not in this list is drift.
pub const ALL: [Palette; 3] = [DASHBOARD, GENESIS, BYTE];

impl Palette {
    /// The slots, in a stable order, for census and diffing.
    pub fn slots(&self) -> [(&'static str, Rgb); 11] {
        [
            ("bg", self.bg),
            ("panel", self.panel),
            ("border", self.border),
            ("text", self.text),
            ("bright", self.bright),
            ("cyan", self.cyan),
            ("gold", self.gold),
            ("pink", self.pink),
            ("green", self.green),
            ("purple", self.purple),
            ("orange", self.orange),
        ]
    }

    /// `#rrggbb`, lowercase.
    pub fn hex(c: Rgb) -> String {
        format!("#{:02x}{:02x}{:02x}", c[0], c[1], c[2])
    }
}
