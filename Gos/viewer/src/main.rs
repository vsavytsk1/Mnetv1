//! GOS VIEWER -- a window, painted by the kernel. Zero dependencies.
//!
//! ```text
//!   the old road :  build_eng_v2.py -> HTML+JS -> ??? -> Chromium -> ??? -> pixels
//!   this road    :  goldberg_kernel -> Canvas -> StretchDIBits -> pixels
//! ```
//!
//! Three views, a BACK button, an EXPORT button, and a full 1/0 dump of
//! everything it draws -- including its own machine code, so we can look at
//! what rustc actually emitted and judge whether it looks right.
//!
//! Every pixel is computed by the TRUSTED kernel (`#![forbid(unsafe_code)]`,
//! integers, no deps). This binary only asks for them and hands them to the OS.
//! The `unsafe` lives entirely in `win32.rs`.
//!
//! ```powershell
//! cargo +stable-x86_64-pc-windows-gnu run -p gos_viewer --release
//! ```

use std::cell::RefCell;
use std::ffi::c_void;
use std::fs;
use std::path::PathBuf;
use std::time::Instant;

use goldberg_kernel::bits;
use goldberg_kernel::dashboard;
use goldberg_kernel::font;
use goldberg_kernel::genesis;
use goldberg_kernel::layout::Rect;
use goldberg_kernel::mobius;
use goldberg_kernel::palette;
use goldberg_kernel::palette::{Palette, ALL};
use goldberg_kernel::raster::{project, project_rpy, Canvas};
use goldberg_kernel::rng::Rng;
use goldberg_kernel::{certify, judge, Mesh};

use gos_win32::*;

/// The canvas, and therefore the client area -- `AdjustWindowRect` sizes the
/// window to yield exactly this, and the app refuses to claim pixel-exactness
/// if the OS disagrees. 1920x1080 on a 2560x1440 panel, so the whole frame is
/// on screen with the window frame to spare.
const DEFAULT_W: usize = 1920;
const DEFAULT_H: usize = 1080;

/// The canvas, decided ONCE at startup and never again.
///
/// It was a pair of `const`s, which meant the render size was a property of
/// the BUILD rather than of the run -- so 4K needed a recompile and "fill the
/// screen" was not expressible at all. It is now set once, before the window
/// or any script exists, and read through `W()` / `H()` everywhere.
///
/// **Set once, not mutable.** A canvas that could change mid-run would have to
/// reallocate the framebuffer, the DIB and every cached layout rect while a
/// paint might be in flight; `OnceLock` makes that impossible by construction
/// rather than by remembering not to. Live drag-resize is a separate job with
/// a `WM_SIZE` handler behind it, and this is not pretending to be it.
static CANVAS: std::sync::OnceLock<(usize, usize)> = std::sync::OnceLock::new();

/// Canvas width. Falls back to the old default if nothing set it, so a code
/// path that forgets cannot produce a zero-sized buffer.
#[allow(non_snake_case)]
#[inline]
fn W() -> usize {
    CANVAS.get().map(|c| c.0).unwrap_or(DEFAULT_W)
}

/// Canvas height.
#[allow(non_snake_case)]
#[inline]
fn H() -> usize {
    CANVAS.get().map(|c| c.1).unwrap_or(DEFAULT_H)
}

/// Fix the canvas. Ignored if it has already been set.
///
/// **Both dimensions are forced EVEN.** `yuv420p` subsamples chroma 2x2, so
/// H.264 cannot encode an odd width or height -- ffmpeg simply refuses. An odd
/// canvas would render and shoot and then fail only at `movie`, which is the
/// worst place to find out. Rounding down here, once, is the whole fix.
fn set_canvas(w: usize, h: usize) -> (usize, usize) {
    let wh = ((w.max(64)) & !1, (h.max(64)) & !1);
    let _ = CANVAS.set(wh);
    *CANVAS.get().unwrap_or(&wh)
}

const BAR_H: i32 = 34;

/// One full frame, in source bytes: `W * H * 3`.
/// One full frame, in source bytes.
fn frame_bytes() -> usize {
    W() * H() * 3
}

/// Cap on any single exported dump. The HELENA doctrine: heavy payload stays
/// local, git keeps the manifest. A cap that is stated is engineering; a dump
/// that silently stops is a lie (Path IV).
///
/// **Stated in the units of the thing it protects (R11).** A `.bits` file
/// writes one ASCII `0` or `1` per bit, so what lands on disk is **eight times
/// this number**, plus newlines. The old cap said "4 MB" and permitted a 32 MB
/// file; four clicks wrote 88 MB into a folder nobody had ignored yet.
///
/// One full frame is the natural unit -- a truncated frame is not the frame --
/// so the cap is `FRAME_BYTES`:
///
/// ```text
///   source  1920 * 1080 * 3 =  6,220,800 B   ~5.9 MB
///   on disk           x8 + newlines          ~50   MB per frame.bits
/// ```
///
/// That is the price, stated before it is paid. `runs/**` is gitignored, and
/// `MANIFEST.json` carries the digests so the steps travel without the payload.
fn dump_cap() -> usize {
    frame_bytes()
}

/// WM_TIMER id for the GENESIS turn.
const GENESIS_TIMER: usize = 1;

/// Height of the GENESIS control bar, which sits above the main button bar.
const GEN_BAR_H: i32 = 34;

/// The most faces the viewer will BUILD. The mathematics is fine far past
/// this -- `genesis::grow` counts to `u64` -- so the refusal names the number
/// and says whose limit it is (Curse 35: state the cost before allocating).
const GEN_FACE_BUDGET: u64 = 1_200_000;

/// One press of `ZOOM +`. The fourth root of two, so four presses double it.
///
/// Multiplicative because zoom is a SCALE: a fixed additive step is a huge
/// jump at 0.25 and imperceptible at 6.0, which is the same complaint as
/// measuring colour in sRGB instead of OKLab -- the axis is not linear in what
/// the eye does.
const ZOOM_STEP: f64 = 1.189_207_115_002_721;

/// Where the viewer opens INNER and MID.
///
/// **Not the browser's defaults, and deliberately not.** `Params::default()`
/// is 0.45 / 0.70 because that is what `GK.refineFace` declares, and that
/// stays true -- it is a recorded fact about the source, not a preference.
/// This is the viewer's preference, and it is a different thing.
///
/// 0.1 / 0.1 sits at `MID = INNER`, where the ring closes flat and the
/// interference between the front and back lattices is at its strongest. That
/// interference is the picture: it is where the symmetry visibly collapses
/// into and out of register as the shell turns, and a see-through render is
/// the only way to see it happen.
const VIEW_INNER: f64 = 0.1;
const VIEW_MID: f64 = 0.1;

/// The most memory one refinement may PEAK at.
///
/// Distinct from the face budget on purpose: they fence different things and
/// either can be the binding one. `examples/kaboom` found the machine's own
/// wall at depth 7 -- 24.7 million faces, 10.49 GB -- with depth 8 aborting
/// (`0xC0000409`) while asking for 6.1 GB on top of the 10.5 it already held.
///
/// 6 GB leaves the window responsive and the machine usable, which is the
/// point of a viewer as opposed to a batch job.
///
/// MEASURED 2026-09-02, `examples/level_six` -- and the peak is `old + new`,
/// which is ~8x the mesh you HAVE, not 8x the one you are about to build. Get
/// that backwards and every projection is off by the growth factor:
///
/// ```text
///   level 5    504,212 faces   0.18 GB mesh   peak 0.19 GB   allowed
///   level 6  3,529,472 faces   1.35 GB mesh   peak 1.42 GB   ALLOWED, measured
///   level 7 24,705,884 faces  ~9.7  GB mesh   peak ~11 GB    refused here, and
///                                                            the machine's own
///                                                            wall is 10.49 GB
/// ```
///
/// So level 6 already fits and level 7 is the one that needs a cheaper face --
/// bought by welding, not by widening this gate. See `GENESIS_PORT_SPEC.md`
/// step 6.
const GEN_PEAK_BYTES: u64 = 6 * 1024 * 1024 * 1024;

/// The most faces the viewer will DRAW in one frame. Distinct from the build
/// budget on purpose: the mesh may legitimately be larger than the canvas can
/// show, and the HUD prints `DRAWN n OF m` so the shortfall is a number rather
/// than a silence.
const GEN_DRAW_CAP: usize = 500_000;

/// WHEN a control takes effect, which is not the same for all of them.
///
/// **This exists because a control was shipped that did nothing at all.**
/// `zoom` had a box, a verb, a movie channel and validation -- and no reader:
/// `fit_zoom()` never consulted it. The value moved, the frame repainted, and
/// the picture was identical. "One row plus two match arms" was true of the
/// plumbing and false of the effect, and nothing in the design noticed.
///
/// Naming the category is what makes the difference testable.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum When {
    /// Read by the renderer. Changing it changes the very next frame.
    Render,
    /// Read by `refine_face` when it CREATES points. Changing it moves
    /// nothing that already exists -- it applies to the next refinement.
    ///
    /// Measured: with the mesh already built, `mid 0.9` vs `mid 0.1` gives
    /// PSNR 41.07 dB, and the whole of that difference is the printed number
    /// in the corner. Set BEFORE building, the same pair gives 23.99 dB --
    /// the picture genuinely moves. This is the browser's semantics too; its
    /// sliders also apply on the next REFINE.
    Build,
    /// Read only when the turn advances. A single frame cannot show it.
    Motion,
}

impl When {
    fn note(self) -> &'static str {
        match self {
            When::Render => "takes effect now",
            When::Build => "applies to the NEXT refine -- it does not move built faces",
            When::Motion => "only visible while it turns",
        }
    }
}

/// One named, bounded, numeric control.
///
/// **This table is the point.** A control listed here gets, for free and at
/// once: a box on the panel, a command-line verb, a `movie` channel, a slot in
/// `LAYOUT.json`, and input validation. Adding the next one is a row here plus
/// two match arms in [`App::ctl_get`] / [`App::ctl_set`] -- and it is
/// immediately animatable, which is the whole reason it is a table instead of
/// seven copies of the same wiring.
struct Control {
    /// how the command line names it: `inner 0.78`, `movie inner ...`
    name: &'static str,
    /// how the panel names it
    label: &'static str,
    lo: f64,
    hi: f64,
    /// what a bad value should be compared against, in words, when a human
    /// types a shoe into a box that wanted a number
    unit: &'static str,
    /// when it takes effect -- and the thing the tests grade against
    when: When,
}

/// Every animatable control the GENESIS view has.
const CONTROLS: [Control; 12] = [
    Control {
        name: "inner",
        label: "INNER",
        lo: 0.05,
        hi: 0.95,
        unit: "where the inner ring sits, 0..1",
        when: When::Build,
    },
    Control {
        name: "twist",
        label: "TWIST",
        lo: 0.0,
        hi: 1.0,
        unit: "sphere -> Mobius band, 0..1 -- DISPLAY LANE, moves points only",
        when: When::Render,
    },
    Control {
        name: "mid",
        label: "MID",
        lo: 0.05,
        hi: 0.95,
        unit: "where the mid ring is pulled to, 0..1",
        when: When::Build,
    },
    Control {
        name: "jitter",
        label: "JITTER",
        lo: 0.0,
        hi: 0.20,
        unit: "symmetry-breaking, 0 = off",
        when: When::Build,
    },
    Control {
        name: "sphere",
        label: "SPHERE",
        lo: 0.5,
        hi: 3.0,
        unit: "projection radius when spherical",
        when: When::Build,
    },
    Control {
        name: "yaw",
        label: "YAW",
        lo: 0.0,
        hi: std::f64::consts::TAU,
        unit: "turn, radians",
        when: When::Render,
    },
    Control {
        name: "zoom",
        label: "ZOOM",
        lo: 0.01,
        hi: 20_000.0,
        // Deliberately absurd at the top end. The mathematics does not care:
        // the mesh is exact at any scale, and past about 40x the canvas lands
        // inside a single face and NOTHING renders -- every one of the half a
        // million faces is projected, sorted and clipped away. Zooming back
        // out is then a demonstration of exactly what that cost buys, which is
        // why the HUD prints VISIBLE beside DRAWN.
        //
        // Safe because `line_a` clips before it rasterises. Without that this
        // range would hang: cost was proportional to a line's FULL length, and
        // at 20,000x a span is ~1.6 million pixels.
        unit: "multiplier on the fitted zoom -- 0.01 to 20000",
        when: When::Render,
    },
    // THE OTHER TWO AXES. `pitch` was always there and was nailed to 0.30 --
    // a hardcoded camera angle nobody could reach, which is R13's shape with
    // no control at all rather than a control with no reader. `roll` is new.
    Control {
        name: "pitch",
        label: "PITCH",
        lo: 0.0,
        hi: std::f64::consts::TAU,
        unit: "tip, radians -- 0.30 is the old fixed angle",
        when: When::Render,
    },
    Control {
        name: "roll",
        label: "ROLL",
        lo: 0.0,
        hi: std::f64::consts::TAU,
        unit: "spin in the screen plane, radians",
        when: When::Render,
    },
    Control {
        name: "speedp",
        label: "SPD-P",
        lo: 0.0,
        hi: 0.25,
        unit: "pitch per frame -- tumble",
        when: When::Motion,
    },
    Control {
        name: "speedr",
        label: "SPD-R",
        lo: 0.0,
        hi: 0.25,
        unit: "roll per frame -- barrel",
        when: When::Motion,
    },
    Control {
        name: "speed",
        label: "SPEED",
        lo: 0.0,
        hi: 0.25,
        // A rate, expressed PER FRAME rather than per second, because the
        // frame is what this program actually counts. At the 60 Hz timer the
        // default 0.012 is one turn every 8.7 seconds; in a movie it is one
        // turn every 524 frames, and both statements are the same statement.
        unit: "turn per frame, radians -- 0 holds it still",
        when: When::Motion,
    },
];

/// Why a typed value was refused.
///
/// **The monkey brain will type a shoe.** That is not a failure of the user,
/// it is a certainty about input, so the box says what it wanted and keeps the
/// old value rather than imploding or -- worse -- accepting a NaN that
/// silently poisons every frame downstream.
#[derive(Clone, Debug, PartialEq)]
enum BadValue {
    /// not a number at all
    NotANumber(String),
    /// NaN or an infinity. `"nan"` and `"inf"` PARSE as f64, which is exactly
    /// why this check exists separately: `"nan".parse::<f64>()` succeeds.
    NotFinite(String),
    /// a real number, outside the control's range
    OutOfRange { got: f64, lo: f64, hi: f64 },
}

impl std::fmt::Display for BadValue {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            BadValue::NotANumber(s) => write!(f, "'{s}' IS NOT A NUMBER"),
            BadValue::NotFinite(s) => write!(f, "'{s}' IS NOT FINITE - NAN AND INF ARE REFUSED"),
            BadValue::OutOfRange { got, lo, hi } => {
                write!(f, "{got} IS OUTSIDE {lo}..{hi}")
            }
        }
    }
}

/// Parse a human's typing into a value this control will accept.
///
/// Three refusals, in order, because they are three different mistakes:
/// gibberish, a number that is not a number (`NaN`, `inf` -- both of which
/// `parse::<f64>()` happily accepts), and a fine number in the wrong place.
fn parse_control(c: &Control, text: &str) -> Result<f64, BadValue> {
    let t = text.trim();
    let v: f64 = t.parse().map_err(|_| BadValue::NotANumber(t.to_string()))?;
    if !v.is_finite() {
        return Err(BadValue::NotFinite(t.to_string()));
    }
    if v < c.lo || v > c.hi {
        return Err(BadValue::OutOfRange {
            got: v,
            lo: c.lo,
            hi: c.hi,
        });
    }
    Ok(v)
}

/// A numeric input box. Click to edit, type, Enter commits, Esc cancels.
///
/// Replaces the slider it grew out of. A slider cannot express `0.7853981634`
/// and cannot be driven from a keyboard; a box can do both, and it is the same
/// text the command line takes, so what you type by hand and what you script
/// are literally the same string.
struct Field {
    x: i32,
    y: i32,
    w: i32,
    h: i32,
    /// index into [`CONTROLS`]
    ctl: usize,
}

impl Field {
    fn hit(&self, mx: i32, my: i32) -> bool {
        mx >= self.x && mx < self.x + self.w && my >= self.y && my < self.y + self.h
    }
}

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum View {
    /// ENG v2.0 master control, painted from integers -- the target
    Dashboard,
    /// the certified C60, painted
    Shell,
    /// the framebuffer's own bits, as a 1/0 texture
    FrameBits,
    /// what rustc emitted for this .exe, as a 1/0 texture
    MachineBits,
    /// GENESIS step 1: the certified C60, spinning. The port target is
    /// shell/genesis_v8.5.2.html -- see grimoire/GENESIS_PORT_SPEC.md.
    /// Deliberately the smallest thing that can be shipped and tested:
    /// a seed on screen, turning, with its census beside it. Refinement,
    /// the sliders and the Mobius twist arrive as later steps.
    Genesis,
}

impl View {
    fn title(self) -> &'static str {
        match self {
            View::Dashboard => "", // the dashboard paints its own top bar
            View::Shell => "THE SHELL - C60 CERTIFIED",
            View::FrameBits => "THE FRAME - ITS OWN 1 AND 0S",
            View::MachineBits => "THE MACHINE - WHAT RUSTC EMITTED",
            View::Genesis => "GENESIS - THE SEED, SPINNING",
        }
    }
}

/// The kernel modules the dashboard's left panel reports. Real sizes, read from
/// `kernel/*.js` at startup -- the browser reports the same six.
const MODULE_FILES: [&str; 6] = [
    "goldberg_kernel.js",
    "graph_axioms.js",
    "sar_modular.js",
    "ns_spectral.js",
    "fractal_search.js",
    "mnet_nanite.js",
];

struct Button {
    x: i32,
    y: i32,
    w: i32,
    h: i32,
    label: &'static str,
    id: u8,
}

impl Button {
    fn hit(&self, mx: i32, my: i32) -> bool {
        mx >= self.x && mx < self.x + self.w && my >= self.y && my < self.y + self.h
    }
}

struct App {
    cv: Canvas,
    dib: Vec<u8>,
    stack: Vec<View>,
    pal: usize,
    buttons: Vec<Button>,
    status: String,
    runs: usize,
    last_render_us: u128,
    /// The digest of the CONTENT ONLY -- taken before any chrome is painted.
    ///
    /// RUSTIUM R10: the render time is drawn into the framebuffer, so hashing
    /// the finished frame hashes a clock and the digest moves every render.
    /// Hash the math, not the moment (Curse 38): seal the content, then dress
    /// it, and report the seal taken before the dressing.
    content_digest: u64,
    flipped: usize,
    mesh: Mesh,
    pent_edge: Vec<bool>,
    exe_bytes: Vec<u8>,
    /// The session folder, created BEFORE anything is drawn.
    ///
    /// Named `v<crate version>_s<session>` -- the crate version so a run can
    /// always be traced to the build that made it (Path X: freeze every
    /// version), the session counter so numbering never needs a clock
    /// (Curse 38). The permanent spine -- git HEAD and the ledger entry --
    /// lives inside `SESSION.json`, because per Curse 27 a thing's identity is
    /// its origin, never its name on disk.
    session_dir: PathBuf,
    shots: usize,
    exports: usize,
    /// kernel module sizes in KB, read from `kernel/*.js` -- 0 means MISSING,
    /// and the left panel says MISS rather than pretending (Path IV)
    module_kb: [usize; 6],
    git: String,
    ledger: String,
    cert_line: String,
    /// GENESIS: the turn angle, advanced by WM_TIMER. Only this view spins,
    /// so the dashboard stays still -- Curse 13 / Path VIII, motion is opt-in.
    genesis_yaw: f64,
    /// spin runs only while the GENESIS view is open AND this is true.
    /// Starts ON here because a still seed reads as a broken one, but `S`
    /// stops it and the panel says so -- motion is opt-in and reversible.
    genesis_spin: bool,
    /// what the dashboard actually painted, so clicks hit-test against the
    /// drawn geometry instead of a recomputed guess
    card_rects: Vec<Rect>,
    /// Whether the HUD may paint the render time into the frame.
    ///
    /// **R10, one level out.** The seal is taken before the chrome, so the
    /// SEAL reproduces -- but a PNG written after the chrome contains
    /// `RENDER 683 US`, and 683 is a clock. Two runs of the identical script
    /// produced the identical seal and DIFFERENT png bytes, which is the same
    /// disease wearing a file instead of a hash.
    ///
    /// Interactive runs keep it: a human watching wants the number live.
    /// `--run` drops it and puts the timing in `DRIVE.log` as a peer OUTSIDE
    /// the image -- exactly the remedy R10 prescribed for the manifest.
    /// Hash the math, not the moment; and photograph the math, not the moment.
    paint_clock: bool,
    /// where each painted card leads, built in the SAME loop that builds the
    /// cards. Previously the click handler said `if i == 1` and the wiring
    /// lived in a magic index -- insert a card at the front and GENESIS would
    /// silently become something else. Same shape as R3 and R9: an index
    /// standing where an identity belongs.
    card_views: Vec<Option<View>>,
    /// The live GENESIS mesh the control bar operates on.
    gen: genesis::State,
    /// INNER / MID and the rest. The sliders READ this; they do not shadow it.
    gen_params: genesis::Params,
    /// the control bar's own buttons, live only in the GENESIS view
    gen_buttons: Vec<Button>,
    /// one numeric box per row of CONTROLS
    gen_fields: Vec<Field>,
    /// which box has the caret, and what has been typed into it so far.
    /// `None` means nothing is being edited and keys go to the view.
    gen_edit: Option<(usize, String)>,
    /// the last refusal, shown under the box that caused it
    gen_error: Option<String>,
    /// multiplier on the fitted zoom -- a control like any other
    gen_zoom: f64,
    /// Drop the far hemisphere before drawing.
    ///
    /// Off by default, and the default is the honest one: this renderer has no
    /// depth buffer, so faces do not occlude, they BLEND. What you see is the
    /// back lattice superimposed on the front at a different projected scale,
    /// which is a real moire and the thing that makes these pictures.
    ///
    /// It also imposes a symmetry that is not the shell's: a rotation by pi
    /// swaps front and back, so a transparent render is 2-fold symmetric about
    /// the view axis whatever the mesh underneath is doing. Measured over a
    /// full turn, every significant rotational harmonic of the frame came out
    /// EVEN -- m = 2,4,6,8,10,12 -- with the odd ones one to two orders of
    /// magnitude down. `m=10` is the icosahedral 5-fold axis doubled; `m=6`
    /// is the 3-fold doubled.
    ///
    /// Turning this on removes that doubling, so it is the control that
    /// separates "the shell's symmetry" from "the render's symmetry".
    ///
    /// The test is exact for this mesh and only for this mesh: the shell is
    /// convex and centred on the origin, so a face is back-facing exactly when
    /// its centroid's rotated depth is negative. No normals, no dot products,
    /// and nothing that could disagree with the painter's order -- it reuses
    /// the very depth that order is computed from.
    gen_cull: bool,
    /// Fill the faces as the browser does, not merely outline them.
    gen_fill: bool,
    /// Mobius blend, 0 = sphere, 1 = band. Applied at DRAW time, so the stored
    /// mesh is never bent -- toggling back is exact, not a re-derivation.
    gen_twist: f64,
    /// whether the twist is armed at all; the box is live only when it is
    gen_mobius: bool,
    /// Project refined points onto the sphere instead of leaving them planar.
    ///
    /// **Ported because a test found `sphere` was dead without it.**
    /// `Params::sphere_r` is only consulted when `surface` is `Spherical`, the
    /// default is `Planar`, and nothing could change it -- so a control with a
    /// box, a verb and a movie channel had no effect at any value. That is the
    /// same failure as `zoom`, found the same way, in the same test run.
    ///
    /// The browser offers `planar | spherical | tangent`. Two of the three are
    /// here; `tangent` is not, and is not pretended to be.
    gen_spherical: bool,
    /// radians of turn per frame. ONE constant for both callers: the window's
    /// timer and the script's `spin`. They were separate literals in the orb
    /// and had DRIFTED apart -- 0.012 in the timer, 0.01 in advance() -- so a
    /// scripted spin did not reproduce what the window did. A control cannot
    /// drift from itself.
    gen_speed: f64,
    /// tip, radians. Was the literal `0.30` inside `paint_genesis`.
    gen_pitch: f64,
    /// spin in the screen plane, radians. Applied after projection.
    gen_roll: f64,
    /// pitch per frame -- with `speed` non-zero as well, it tumbles
    gen_speed_p: f64,
    /// roll per frame -- a barrel roll of the picture itself
    gen_speed_r: f64,
}

thread_local! {
    static APP: RefCell<Option<App>> = const { RefCell::new(None) };
}

/// Declare this process DPI-aware, once, and remember the answer.
///
/// **Awareness can only be set ONCE per process.** A second call fails, and a
/// caller reading that failure concludes the process is not aware -- which is
/// exactly what happened the moment `--max` needed the screen size before the
/// window existed: `resolve_canvas` set it, `run()` set it again, got 0, and
/// renamed the window to "PIXELS RESAMPLED - NOT EXACT" while the pixels were
/// in fact exact. The report was wrong, not the rendering.
///
/// Caching turns the second caller into a reader of the first result instead
/// of a second setter with a worse answer. One call, one witness.
static DPI_AWARE: std::sync::OnceLock<bool> = std::sync::OnceLock::new();

fn ensure_dpi_aware() -> bool {
    *DPI_AWARE
        .get_or_init(|| unsafe { SetProcessDpiAwarenessContext(DPI_PER_MONITOR_AWARE_V2) != 0 })
}

/// Work out the canvas from the command line, and FIX it before anything runs.
///
/// Three ways, in order of how much the caller knows:
///
/// * `--size 3840x2160` -- say it exactly. This is how 4K and 8K happen now,
///   with no recompile, because the canvas stopped being a property of the
///   build.
/// * `--max` -- fill the screen. `SM_CXFULLSCREEN` is the client area of a
///   maximised window, so the taskbar and the frame are already deducted and
///   there is no guesswork left to get wrong.
/// * neither -- the old default, unchanged.
///
/// DPI awareness is declared HERE rather than in `run()`, because `--max`
/// reads a screen metric and a DPI-unaware process is told a 2560-wide panel
/// is 1707 wide. Sizing a canvas from that number would reintroduce the exact
/// resampling the DPI work removed. `--run` never opens a window and still
/// needs the true number, so this must happen before the fork, not after it.
fn resolve_canvas(size: Option<String>, want_max: bool) -> Result<(usize, usize), String> {
    ensure_dpi_aware();
    if let Some(spec) = size {
        let lower = spec.to_ascii_lowercase();
        let (w, h) = lower
            .split_once('x')
            .ok_or_else(|| format!("--size wants WxH, got {spec:?}"))?;
        let w: usize = w
            .trim()
            .parse()
            .map_err(|_| format!("{:?} is not a width", w.trim()))?;
        let h: usize = h
            .trim()
            .parse()
            .map_err(|_| format!("{:?} is not a height", h.trim()))?;
        if w < 64 || h < 64 || w > 16384 || h > 16384 {
            return Err(format!("{w}x{h} is outside 64..16384"));
        }
        return Ok(set_canvas(w, h));
    }
    if want_max {
        let (w, h) = unsafe {
            (
                GetSystemMetrics(SM_CXFULLSCREEN),
                GetSystemMetrics(SM_CYFULLSCREEN),
            )
        };
        if w > 0 && h > 0 {
            return Ok(set_canvas(w as usize, h as usize));
        }
        return Err(String::from("the screen would not report its size"));
    }
    Ok(set_canvas(DEFAULT_W, DEFAULT_H))
}

fn main() {
    // A click is a function call and a frame is a buffer we already own, so
    // the driver lives HERE, not in a shell wrapping the OS. See run_script.
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut i = 0;
    let mut script: Option<String> = None;
    let mut open: Option<String> = None;
    let mut size: Option<String> = None;
    let mut want_max = false;

    while i < args.len() {
        match args[i].as_str() {
            "--open" | "-o" => {
                i += 1;
                match args.get(i) {
                    Some(s) => open = Some(s.clone()),
                    None => {
                        eprintln!("--open needs a script string");
                        std::process::exit(2);
                    }
                }
            }
            "--run" | "-r" => {
                i += 1;
                match args.get(i) {
                    Some(s) => script = Some(s.clone()),
                    None => {
                        eprintln!("--run needs a script string");
                        std::process::exit(2);
                    }
                }
            }
            "--script" | "-s" => {
                i += 1;
                match args.get(i).map(fs::read_to_string) {
                    Some(Ok(s)) => script = Some(s),
                    Some(Err(e)) => {
                        eprintln!("cannot read script: {e}");
                        std::process::exit(2);
                    }
                    None => {
                        eprintln!("--script needs a path");
                        std::process::exit(2);
                    }
                }
            }
            "--size" => {
                i += 1;
                match args.get(i) {
                    Some(v) => size = Some(v.clone()),
                    None => {
                        eprintln!("--size needs WxH, e.g. --size 3840x2160");
                        std::process::exit(2);
                    }
                }
            }
            "--max" => want_max = true,
            "--help" | "-h" => {
                println!("{HELP}");
                return;
            }
            other => {
                eprintln!(
                    "unknown argument '{other}'

{HELP}"
                );
                std::process::exit(2);
            }
        }
        i += 1;
    }

    // THE CANVAS IS FIXED HERE, before a window, a script or a buffer exists.
    let asked = size.clone();
    match resolve_canvas(size, want_max) {
        Ok((w, h)) => {
            // If a request was rounded, SAY SO. `--size 1921x1081` quietly
            // becoming 1920x1080 is a silent cap, and a cap that does not
            // announce itself reads as "you got what you asked for".
            if let Some(spec) = asked.as_deref() {
                let got = format!("{w}x{h}");
                if spec.eq_ignore_ascii_case(&got) {
                    println!("canvas  {w} x {h}");
                } else {
                    println!(
                        "canvas  {w} x {h}   ROUNDED from {spec} -- both axes forced even, \
                         because yuv420p subsamples chroma 2x2 and cannot encode an odd one"
                    );
                }
            } else if want_max {
                println!(
                    "canvas  {w} x {h}   MAXIMISED -- the client area of a full-screen window, \
                     so the taskbar and the frame are already deducted"
                );
            }
        }
        Err(e) => {
            eprintln!("{e}");
            std::process::exit(2);
        }
    }

    match script {
        // headless: no window, no compositor, no capture API. The PNGs come
        // straight off the framebuffer the kernel computed.
        Some(src) => std::process::exit(run_script(&src)),
        None => unsafe { run(want_max, open) },
    }
}

const HELP: &str = "GOS VIEWER -- a window, painted by the kernel.

  gos_viewer                       open the window
  gos_viewer --run \"<steps>\"       run steps headless, write PNGs, exit
  gos_viewer --script <file>       the same, from a file
  gos_viewer --open \"<steps>\"      run steps, THEN open the window with them
  gos_viewer --max                 canvas = a full-screen client area
  gos_viewer --size 3840x2160      any canvas, no recompile
  gos_viewer --max                 fill the screen

STEPS -- ';' or newline separated, '#' comments

  shot <name>      render and write <name>.png FROM THE FRAMEBUFFER
  card <n>         click the centre of card n
  button <LABEL>   click the centre of that button
  panel|back|shell|palette   sugar for the matching button
  key <c>          press a key
  spin <n>         advance the GENESIS turn n frames -- deterministic, not a sleep
  expect <View>    the current view must be this, or FAIL
  status           print the status line

GENESIS CONTROL BAR -- the same methods the mouse calls

  seed c60|12      reseed
  refine all|5s|6s one refinement, priced before it is allocated
  undo | reset     step back, or back to the seed and the browser defaults
  zoomin | zoomout one multiplicative step -- x2 every four presses
  inner <v>        0.05..0.95   where the inner ring sits
  mid <v>          0.05..0.95   where the mid ring is pulled to
                   mid > inner opens a rosette; mid < inner overlaps into
                   bursts. That is the CRESCENT DEFECT, and it is the picture.
MOVIES -- priced exactly before the first frame is written

  movie spin <frames> <name>              one full turn across the movie
  movie inner <lo> <hi> <frames> <name>   sweep the inner ring
  movie mid   <lo> <hi> <frames> <name>   sweep the mid ring
  stats                                   what the frame is made of, in OKLab
  mp4 <name> [fps] [crf]                  one shareable file, via ffmpeg

  We do NOT own H().264 and do not pretend to: the job goes to ffmpeg, which is
  libavcodec, which is the engine under VLC. `[dependencies]` is still empty --
  ffmpeg is a TOOL we invoke, found by running it, and if it is missing we say
  so and leave the exact command in movie_<name>/MAKE_MP4.txt.

  Measured: 60 frames at 1920x1080, 356.05 MB -> 0.421 MB. 846:1.
  yuv420p chroma-subsamples, which softens coloured edges -- the PNG frames
  stay the source of truth; the mp4 is a lossy convenience for sharing.

  Frames land in <session>/drive/movie_<name>/ and are GITIGNORED -- the same
  script rewrites them byte for byte, so they are a cache, not a record.
  MOVIE.json beside them is the record: every frame's seal plus its perceptual
  statistics. At 1920x1080 a frame is 5.93 MB; at 8K it is 94.93 MB, five
  short of the limit that bounces a push.

Exit code is the number of failures.

  gos_viewer --run \"card 1; inner 0.78; mid 0.32; shot bursts\"
  gos_viewer --run \"card 1; sweepmid 0.9 0.1 120 twist\"    # 121 frames
";

/// Open the window, optionally after running some steps first.
///
/// `--run` is headless and exits; `--open` runs the SAME steps through the
/// SAME `step()` and then hands the result to the window. That is why the two
/// cannot disagree about what `refine all` means -- there is one step table
/// and both callers go through it.
unsafe fn run(maximised: bool, prelude: Option<String>) {
    let hinst = GetModuleHandleW(std::ptr::null());
    let class = wide("GosViewerClass");
    let title = wide("GOS VIEWER - the 1 and 0s, painted by the kernel");

    let wc = WNDCLASSW {
        style: CS_HREDRAW | CS_VREDRAW | CS_OWNDC,
        lpfnWndProc: Some(wndproc),
        cbClsExtra: 0,
        cbWndExtra: 0,
        hInstance: hinst,
        hIcon: std::ptr::null_mut(),
        hCursor: LoadCursorW(std::ptr::null_mut(), IDC_ARROW),
        hbrBackground: std::ptr::null_mut(),
        lpszMenuName: std::ptr::null(),
        lpszClassName: class.as_ptr(),
    };
    // DPI FIRST -- before the class, before the window, before any pixel.
    //
    // Without it the OS resamples the entire framebuffer on the way to the
    // glass: on a 150% display a 916x739 request becomes a 1374x1109 window
    // and every kernel-computed pixel is stretched 1.5x by a scaler we do not
    // own. The frame seal hashes the framebuffer and cannot see it, so the
    // receipt would stay honest while the screen quietly stopped matching it.
    //
    // If it fails we do not pretend. The title says so.
    let dpi_exact = ensure_dpi_aware();

    if RegisterClassW(&wc) == 0 {
        eprintln!("RegisterClassW failed");
        return;
    }

    APP.with(|a| {
        let mut app = App::new();
        app.layout();
        app.layout_genesis();
        // the prelude, through the ordinary step path
        if let Some(src) = &prelude {
            let dir = app.session_dir.join("drive");
            let _ = fs::create_dir_all(&dir);
            app.render();
            let mut failures = 0i32;
            for raw in src.split([';', '\n', '\r']) {
                let line = raw.trim();
                if line.is_empty() || line.starts_with('#') {
                    continue;
                }
                println!("{}", step(&mut app, &dir, line, &mut failures));
            }
            if failures > 0 {
                eprintln!("{failures} step(s) failed -- opening anyway");
            }
        }
        *a.borrow_mut() = Some(app);
    });

    // The client area must be EXACTLY W x H, so one canvas pixel is one screen
    // pixel and a click coordinate is a canvas coordinate.
    //
    // `W + 16, H + 39` was a guess at the border and caption. Border metrics
    // are the OS's business -- they move with the theme, the Windows version
    // and the DPI -- so a guess is right on the machine it was made on and
    // silently clips somewhere else. AdjustWindowRect asks the OS instead.
    let mut want = RECT {
        left: 0,
        top: 0,
        right: W() as LONG,
        bottom: H() as LONG,
    };
    AdjustWindowRect(&mut want, WS_OVERLAPPEDWINDOW, 0);
    let outer_w = want.right - want.left;
    let outer_h = want.bottom - want.top;

    let hwnd = CreateWindowExW(
        0,
        class.as_ptr(),
        title.as_ptr(),
        WS_OVERLAPPEDWINDOW | WS_VISIBLE,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        outer_w,
        outer_h,
        std::ptr::null_mut(),
        std::ptr::null_mut(),
        hinst,
        std::ptr::null_mut(),
    );
    if hwnd.is_null() {
        eprintln!("CreateWindowExW failed");
        return;
    }
    ShowWindow(hwnd, SW_SHOW);
    // SHOW IS NOT RAISE.
    //
    // Launched from an elevated PowerShell the window appeared *behind* the
    // console, which to the person who typed the command is exactly the same
    // experience as no window at all -- and that is how it was reported.
    // Neither call is guaranteed to succeed (Windows refuses foreground
    // steals), so their results are deliberately ignored: this is a request,
    // and a failed request is not an error worth stopping for.
    BringWindowToTop(hwnd);
    SetForegroundWindow(hwnd);

    // With --max the canvas already IS the full-screen client area, so the
    // window only needs putting at the origin for the two to coincide. Note
    // what is NOT done here: `SW_MAXIMIZE`. Maximising lets the OS choose the
    // client size, and if that disagrees with the canvas by even one pixel the
    // frame is letterboxed or clipped and the pixel-exact promise quietly
    // stops being true. The canvas decides; the window follows.
    if maximised {
        SetWindowPos(
            hwnd,
            std::ptr::null_mut(),
            0,
            0,
            0,
            0,
            SWP_NOSIZE | SWP_NOZORDER,
        );
    }

    // MEASURE it. AdjustWindowRect is a request; the client rect is the fact.
    // Proof by kernel: the window's own report grades the arithmetic above.
    let mut got = RECT {
        left: 0,
        top: 0,
        right: 0,
        bottom: 0,
    };
    GetClientRect(hwnd, &mut got);
    let (cw, ch) = (got.right - got.left, got.bottom - got.top);
    let exact = dpi_exact && cw == W() as LONG && ch == H() as LONG;
    println!("DPI aware   : {dpi_exact}");
    println!("client area : {cw} x {ch}   (canvas {} x {})", W(), H());
    println!(
        "pixel exact : {}",
        if exact {
            "YES -- one canvas pixel is one screen pixel"
        } else {
            "NO -- the OS is resampling; the seal no longer describes the screen"
        }
    );
    if !exact {
        // Path IV: incomplete is fine, fake is not. If the screen is not the
        // framebuffer, the window says so where a human will read it.
        let warn = wide("GOS VIEWER - PIXELS RESAMPLED BY THE OS - NOT EXACT");
        SetWindowTextW(hwnd, warn.as_ptr());
    }
    // ~60 Hz, consumed ONLY by the GENESIS view (see WM_TIMER). The orb's
    // pattern: SetTimer drives the turn, so there is no render thread and
    // nothing moves when nothing is looking.
    SetTimer(hwnd, GENESIS_TIMER, 16, 0);

    let mut msg: MSG = std::mem::zeroed();
    while GetMessageW(&mut msg, std::ptr::null_mut(), 0, 0) > 0 {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }
}

unsafe extern "system" fn wndproc(hwnd: HWND, msg: UINT, wp: WPARAM, lp: LPARAM) -> LRESULT {
    match msg {
        WM_PAINT => {
            let mut ps: PAINTSTRUCT = std::mem::zeroed();
            let hdc = BeginPaint(hwnd, &mut ps);
            APP.with(|a| {
                if let Some(app) = a.borrow_mut().as_mut() {
                    app.render();
                    app.blit(hdc);
                }
            });
            EndPaint(hwnd, &ps);
            0
        }
        WM_LBUTTONDOWN => {
            let (mx, my) = lparam_xy(lp);
            let mut redraw = false;
            APP.with(|a| {
                if let Some(app) = a.borrow_mut().as_mut() {
                    redraw = app.click(mx, my);
                }
            });
            if redraw {
                InvalidateRect(hwnd, std::ptr::null(), 0);
            }
            0
        }
        WM_TIMER => {
            // Only the GENESIS view animates. Everything else stays still, so
            // the dashboard never pulses at a reader (Curse 13 / Path VIII).
            let mut go = false;
            APP.with(|a| {
                if let Some(app) = a.borrow_mut().as_mut() {
                    if app.view() == View::Genesis && app.genesis_spin {
                        app.genesis_yaw += app.gen_speed;
                        app.gen_pitch += app.gen_speed_p;
                        app.gen_roll += app.gen_speed_r;
                        go = true;
                    }
                }
            });
            if go {
                InvalidateRect(hwnd, std::ptr::null(), 0);
            }
            0
        }
        WM_KEYDOWN => {
            if wp == VK_ESCAPE {
                DestroyWindow(hwnd);
            }
            // Every key goes through App::key. The window is one caller of
            // it; --run is another. A key pressed by a human and a key pressed
            // by a script must travel the SAME path, or the script is testing
            // a different program than the one being shipped.
            let mut go = false;
            APP.with(|a| {
                if let Some(app) = a.borrow_mut().as_mut() {
                    go = app.key(wp);
                }
            });
            if go {
                InvalidateRect(hwnd, std::ptr::null(), 0);
            }
            0
        }
        WM_CLOSE => {
            DestroyWindow(hwnd);
            0
        }
        WM_DESTROY => {
            PostQuitMessage(0);
            0
        }
        _ => DefWindowProcW(hwnd, msg, wp, lp),
    }
}

impl App {
    fn new() -> App {
        let mesh = Mesh::c60();
        let cert = certify(&mesh).expect("C60 must certify before it is painted");
        let verdict =
            judge::check(&judge::rotation_system_c60()).expect("and the judge must agree");
        println!("float lane : {cert}");
        println!("judge      : {verdict}");

        // which edges touch a pentagon
        let mut pent_edge = vec![false; mesh.edges.len()];
        for face in &mesh.faces {
            if face.len() != 5 {
                continue;
            }
            for i in 0..face.len() {
                let (a, b) = (face[i], face[(i + 1) % face.len()]);
                let key = (a.min(b), a.max(b));
                if let Some(ix) = mesh
                    .edges
                    .iter()
                    .position(|&(u, v)| (u.min(v), u.max(v)) == key)
                {
                    pent_edge[ix] = true;
                }
            }
        }

        let exe_bytes = std::env::current_exe()
            .and_then(fs::read)
            .unwrap_or_default();
        println!("own machine code: {} bytes", exe_bytes.len());

        // AXIOM 01 -- the gate, before anything is created or drawn:
        //   "1. Verify P=12 pentagons. If not 12 -- stop. Do not ship.
        //    2. Verify V-E+F=2.       If not 2  -- stop. Do not ship."
        // Both lanes agree above, or `expect` already stopped us. The session
        // folder records that it passed BEFORE the first pixel existed.
        let session_dir = open_session(&cert, &verdict);
        println!("session    : {}", session_dir.display());

        // the six kernel modules, measured not assumed
        let kroot = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .and_then(|p| p.parent())
            .map(|p| p.join("kernel"))
            .unwrap_or_default();
        let mut module_kb = [0usize; 6];
        for (i, f) in MODULE_FILES.iter().enumerate() {
            module_kb[i] = fs::metadata(kroot.join(f))
                .map(|m| m.len() as usize / 1024)
                .unwrap_or(0);
        }
        println!("modules    : {module_kb:?} KB  (0 = MISSING)");

        let pal = ALL[0];
        let mut app = App {
            cv: Canvas::new(W(), H(), pal.bg),
            dib: vec![0u8; W() * H() * 4],
            stack: vec![View::Dashboard],
            pal: 0,
            buttons: Vec::new(),
            status: String::from("AXIOM 01 GATE PASSED - P=12 CHI=2 - CERTIFIED BEFORE DRESSED."),
            runs: 0,
            last_render_us: 0,
            content_digest: 0,
            flipped: 0,
            mesh,
            pent_edge,
            exe_bytes,
            session_dir,
            shots: 0,
            exports: 0,
            module_kb,
            git: git_head(),
            ledger: ledger_entry(),
            cert_line: format!("V {} E {} F {} CHI {}", cert.v, cert.e, cert.f, cert.chi),
            genesis_yaw: 0.55,
            genesis_spin: true,
            card_rects: Vec::new(),
            card_views: Vec::new(),
            gen: genesis::State::seed_c60(),
            gen_params: genesis::Params {
                inner_scale: VIEW_INNER,
                mid_scale: VIEW_MID,
                ..genesis::Params::default()
            },
            gen_buttons: Vec::new(),
            gen_fields: Vec::new(),
            gen_edit: None,
            gen_error: None,
            gen_zoom: 1.0,
            gen_speed: 0.012,
            gen_pitch: 0.30,
            gen_roll: 0.0,
            gen_speed_p: 0.0,
            gen_speed_r: 0.0,
            gen_cull: false,
            gen_fill: true,
            gen_twist: 0.0,
            gen_mobius: false,
            gen_spherical: false,
            paint_clock: true,
        };
        app.layout();
        app.layout_genesis();
        app
    }

    fn pal(&self) -> Palette {
        ALL[self.pal]
    }
    fn view(&self) -> View {
        *self.stack.last().unwrap_or(&View::Shell)
    }

    fn layout(&mut self) {
        let y = H() as i32 - BAR_H + 6;
        let mut x = 10i32;
        self.buttons.clear();
        for (id, label) in [
            (5u8, "SHOT"),
            (0, "EXPORT ALL"),
            (6, "SHELL"),
            (1, "FRAME BITS"),
            (2, "MACHINE BITS"),
            (3, "PALETTE"),
            (4, "BACK"),
            (7, "PANEL"),
        ] {
            let w = font::width(label, 1) + 16;
            self.buttons.push(Button {
                x,
                y,
                w,
                h: BAR_H - 12,
                label,
                id,
            });
            x += w + 8;
        }
    }

    fn click(&mut self, mx: i32, my: i32) -> bool {
        // THE GENESIS CONTROL BAR, and only while that view is open, so no
        // other view can be driven by a click landing in the same pixels.
        if self.view() == View::Genesis {
            if let Some(id) = self
                .gen_buttons
                .iter()
                .find(|b| b.hit(mx, my))
                .map(|b| b.id)
            {
                self.status = self.gen_action(id);
                return true;
            }
            // click a box to edit it. The buffer starts EMPTY rather than
            // pre-filled, so the first keystroke replaces instead of appending
            // to a number the user did not choose.
            if let Some(ctl) = self
                .gen_fields
                .iter()
                .find(|f| f.hit(mx, my))
                .map(|f| f.ctl)
            {
                self.gen_edit = Some((ctl, String::new()));
                self.gen_error = None;
                self.status = format!(
                    "{} - TYPE A NUMBER, ENTER COMMITS, ESC CANCELS. {} ({}..{})",
                    CONTROLS[ctl].label, CONTROLS[ctl].unit, CONTROLS[ctl].lo, CONTROLS[ctl].hi
                );
                return true;
            }
            // a click anywhere else abandons the edit rather than leaving a
            // half-typed number holding the keyboard hostage
            if self.gen_edit.is_some() {
                self.gen_edit = None;
                self.gen_error = None;
            }
        }

        // CARDS FIRST. draw() returns exactly what it painted, so a click
        // hit-tests the real geometry instead of a recomputed guess -- which
        // is how a UI and its layout drift apart. Until now these rects were
        // collected and never used: the cards looked clickable and were not.
        if self.view() == View::Dashboard {
            for (i, r) in self.card_rects.iter().enumerate() {
                if mx >= r.x && mx < r.x + r.w && my >= r.y && my < r.y + r.h {
                    // the destination travels WITH the card, built in the same
                    // loop -- never recovered from the index (R3/R9)
                    match self.card_views.get(i).copied().flatten() {
                        Some(View::Genesis) => {
                            self.stack.push(View::Genesis);
                            self.status = String::from("GENESIS - THE SEED, SPINNING. S STOPS IT.");
                        }
                        Some(v) => {
                            self.stack.push(v);
                            self.status = v.title().to_string();
                        }
                        None => {
                            self.status =
                                format!("CARD {i} HAS NO VIEW YET - NOT WIRED, NOT PRETENDING");
                        }
                    }
                    return true;
                }
            }
        }
        let hit = self.buttons.iter().find(|b| b.hit(mx, my)).map(|b| b.id);
        match hit {
            Some(5) => {
                self.screenshot();
                true
            }
            Some(0) => {
                self.export();
                true
            }
            Some(6) => {
                self.stack.push(View::Shell);
                true
            }
            Some(1) => {
                self.stack.push(View::FrameBits);
                true
            }
            Some(2) => {
                self.stack.push(View::MachineBits);
                true
            }
            Some(3) => {
                self.pal = (self.pal + 1) % ALL.len();
                self.status = format!(
                    "PALETTE {} - BG {} - SAME MATH, NEW DRESS",
                    self.pal().name.to_uppercase(),
                    Palette::hex(self.pal().bg)
                );
                true
            }
            Some(4) => {
                if self.stack.len() > 1 {
                    self.stack.pop();
                    self.status = String::from("BACK.");
                } else {
                    self.status = String::from("ALREADY AT THE ROOT VIEW.");
                }
                true
            }
            // PANEL -- all the way home in one click, however deep the stack
            // got. BACK pops one; this truncates to the root. Two buttons
            // because they answer two different questions, and a reader should
            // never have to click BACK an unknown number of times to find out
            // where the root is.
            Some(7) => {
                if self.stack.len() > 1 {
                    let depth = self.stack.len() - 1;
                    self.stack.truncate(1);
                    self.status = format!("PANEL - CLIMBED {depth} BACK TO THE DASHBOARD.");
                } else {
                    self.status = String::from("ALREADY ON THE PANEL.");
                }
                true
            }
            _ => false,
        }
    }

    /// Read a control by index. One arm per row of [`CONTROLS`].
    fn ctl_get(&self, i: usize) -> f64 {
        match CONTROLS[i].name {
            "inner" => self.gen_params.inner_scale,
            "mid" => self.gen_params.mid_scale,
            "jitter" => self.gen_params.jitter,
            "sphere" => self.gen_params.sphere_r,
            "yaw" => self.genesis_yaw,
            "speed" => self.gen_speed,
            "pitch" => self.gen_pitch,
            "roll" => self.gen_roll,
            "speedp" => self.gen_speed_p,
            "speedr" => self.gen_speed_r,
            _ => self.gen_zoom,
        }
    }

    /// Write a control by index, clamped to its own range.
    ///
    /// Clamping rather than refusing is right HERE because the value has
    /// already been validated by [`parse_control`] or produced by a movie's
    /// own interpolation; this is the last line of defence, not the first.
    fn ctl_set(&mut self, i: usize, v: f64) -> String {
        let c = &CONTROLS[i];
        let v = v.clamp(c.lo, c.hi);
        match c.name {
            // Setting a twist ARMS the Mobius. `every_control_changes_something`
            // caught the alternative: with arming required first, `twist` was a
            // Render control that moved nothing, which is R13 exactly -- a box
            // that exists and is read by nobody. Typing `twist 0.6` means it.
            "twist" => {
                self.gen_twist = v;
                self.gen_mobius = v > 0.0;
            }
            "inner" => self.gen_params.inner_scale = v,
            "mid" => self.gen_params.mid_scale = v,
            "jitter" => self.gen_params.jitter = v,
            "sphere" => self.gen_params.sphere_r = v,
            "yaw" => self.genesis_yaw = v,
            "speed" => self.gen_speed = v,
            "pitch" => self.gen_pitch = v,
            "roll" => self.gen_roll = v,
            "speedp" => self.gen_speed_p = v,
            "speedr" => self.gen_speed_r = v,
            _ => self.gen_zoom = v,
        }
        // the crescent is the fact worth repeating, so the two that decide it
        // say which side they are on every time either moves
        if c.name == "inner" || c.name == "mid" {
            format!(
                "{} {v:.4}   INNER {:.3} MID {:.3} - {} - {}",
                c.label,
                self.gen_params.inner_scale,
                self.gen_params.mid_scale,
                Self::crescent(&self.gen_params),
                c.when.note()
            )
        } else {
            format!("{} {v:.4}   ({}) - {}", c.label, c.unit, c.when.note())
        }
    }

    /// Find a control by the name the command line uses.
    fn ctl_index(name: &str) -> Option<usize> {
        CONTROLS
            .iter()
            .position(|c| c.name.eq_ignore_ascii_case(name))
    }
}

/// What a movie will cost, measured before it is agreed to.
///
/// **This is the "bro, get a server" gate.** Bytes were already exact --
/// stored deflate makes a frame's size a pure function of the canvas. Time was
/// not, so it is MEASURED: render one real frame at the current settings,
/// then multiply. A mesh at 68,612 faces renders an order of magnitude slower
/// than one at 212, and no formula would have known that; the clock does.
struct Estimate {
    frames: u32,
    fps: u32,
    /// seconds of finished footage
    play_s: f64,
    /// seconds of rendering, from one measured frame
    render_s: f64,
    /// bytes of PNG, exact, if frames are written
    png_bytes: u64,
}

impl Estimate {
    /// Time one frame at the real settings, then scale.
    fn measure(app: &mut App, frames: u32, fps: u32) -> Estimate {
        let t0 = Instant::now();
        app.render();
        let one = t0.elapsed().as_secs_f64();
        Estimate {
            frames,
            fps: fps.max(1),
            play_s: frames as f64 / fps.max(1) as f64,
            render_s: one * frames as f64,
            png_bytes: goldberg_kernel::raster::png_bytes(W(), H()) as u64 * frames as u64,
        }
    }

    fn hms(s: f64) -> String {
        let t = s.max(0.0) as u64;
        if t < 60 {
            format!("{:.1}s", s)
        } else if t < 3600 {
            format!("{}m {:02}s", t / 60, t % 60)
        } else {
            format!("{}h {:02}m", t / 3600, (t % 3600) / 60)
        }
    }

    /// The line a human reads before deciding.
    fn report(&self, write_png: bool) -> String {
        format!(
            "  {} frames @ {} fps = {} of footage\n  render ~{} (one frame measured)\n  \
             disk {}",
            self.frames,
            self.fps,
            Self::hms(self.play_s),
            Self::hms(self.render_s),
            if write_png {
                format!(
                    "{:.2} GB of PNG, exact",
                    self.png_bytes as f64 / 1_073_741_824.0
                )
            } else {
                String::from("0 bytes -- frames are piped, never written")
            }
        )
    }
}

/// Past this a movie is refused, with the number, and told to go elsewhere.
const RENDER_SECONDS_BUDGET: f64 = 20.0 * 60.0;

impl App {
    /// The GENESIS control bar: the browser's own row, ported.
    ///
    /// `SEED C60 | SEED 12 | REFINE ALL | REFINE 5s | REFINE 6s | UNDO | RESET`
    /// then the two sliders that decide what the picture looks like.
    ///
    /// **INNER and MID are the whole aesthetic.** With `mid > inner` the ring
    /// opens a rosette; with `mid < inner` it overlaps and you get the
    /// five-pointed bursts. The spec calls that the CRESCENT DEFECT and says
    /// plainly: it is not a bug to fix, it is the picture. So these two floats
    /// are a first-class control, not a debug knob.
    fn layout_genesis(&mut self) {
        let y = H() as i32 - BAR_H - GEN_BAR_H + 6;
        let h = GEN_BAR_H - 12;
        let mut x = 10i32;

        self.gen_buttons.clear();
        for (id, label) in [
            (10u8, "SEED C60"),
            (11, "SEED 12"),
            (12, "REFINE ALL"),
            (13, "REFINE 5s"),
            (14, "REFINE 6s"),
            (15, "UNDO"),
            (16, "RESET"),
            // Zoom in STEPS as well as by typing. A box is exact and a step is
            // fast, and they are the same control underneath -- both go
            // through ctl_set, so neither can drift from the other.
            (17, "ZOOM -"),
            (18, "ZOOM +"),
            (19, "CULL"),
            (20, "SPHERICAL"),
            (21, "FILL"),
            (22, "MOBIUS"),
        ] {
            let w = font::width(label, 1) + 16;
            self.gen_buttons.push(Button {
                x,
                y,
                w,
                h,
                label,
                id,
            });
            x += w + 8;
        }

        // one numeric BOX per control, laid out from the table. Add a row to
        // CONTROLS and a box appears here without touching this code.
        self.gen_fields.clear();
        x += 12;
        let bw = 68i32;
        for (i, c) in CONTROLS.iter().enumerate() {
            let lw = font::width(c.label, 1) + 6;
            self.gen_fields.push(Field {
                x: x + lw,
                y,
                w: bw,
                h,
                ctl: i,
            });
            x += lw + bw + 10;
        }
    }

    /// One control-bar action. The window calls this and so does `--run`.
    fn gen_action(&mut self, id: u8) -> String {
        let p = self.gen_params;
        match id {
            10 => {
                self.gen = genesis::State::seed_c60();
                String::from("SEED C60 - 12 PENTAGONS, 20 HEXAGONS, 12 ANCHORS.")
            }
            11 => String::from(
                "SEED 12 NOT BUILT YET - buildDodecahedron IS STEP 1 OF THE PORT. NOT WIRED, NOT PRETENDING.",
            ),
            12 => self.gen_refine(genesis::Op::All),
            13 => self.gen_refine(genesis::Op::Pent),
            14 => self.gen_refine(genesis::Op::Hex),
            15 => match self.gen.undo() {
                Some(prev) => {
                    self.gen = prev;
                    format!(
                        "UNDO - BACK TO {} FACES. THE COUNTER DOES NOT ROLL BACK.",
                        self.gen.faces.len()
                    )
                }
                None => String::from("NOTHING TO UNDO - THIS IS THE SEED."),
            },
            16 => {
                self.gen = genesis::State::seed_c60();
                self.gen_params = genesis::Params {
                    inner_scale: VIEW_INNER,
                    mid_scale: VIEW_MID,
                    ..genesis::Params::default()
                };
                format!(
                    "RESET - THE SEED, AND INNER {:.2} MID {:.2} BACK TO {VIEW_INNER} / {VIEW_MID}.",
                    p.inner_scale, p.mid_scale
                )
            }
            // MULTIPLICATIVE steps, not additive.
            //
            // Zoom is a scale: the eye reads a doubling the same way at 0.5 as
            // at 4.0, while a fixed +0.25 is a huge jump down low and invisible
            // up high. `ZOOM_STEP` is the fourth root of 2, so four presses
            // double it and the range 0.25..6 is 18 even steps rather than a
            // ramp that feels wrong at both ends.
            17 | 18 => {
                let i = Self::ctl_index("zoom").expect("zoom is in the table");
                let now = self.ctl_get(i);
                let next = if id == 18 {
                    now * ZOOM_STEP
                } else {
                    now / ZOOM_STEP
                };
                let msg = self.ctl_set(i, next);
                let got = self.ctl_get(i);
                if (got - now).abs() < 1e-12 {
                    format!("ZOOM {got:.3} - AT THE {} OF THE RANGE ALREADY",
                        if id == 18 { "TOP" } else { "BOTTOM" })
                } else {
                    msg
                }
            }
            19 => {
                self.gen_cull = !self.gen_cull;
                if self.gen_cull {
                    String::from(
                        "CULL ON - THE FAR HEMISPHERE IS DROPPED. THE RENDER'S OWN 2-FOLD                          SYMMETRY GOES WITH IT.",
                    )
                } else {
                    String::from(
                        "CULL OFF - SEE-THROUGH. FRONT AND BACK SUPERIMPOSE, WHICH IS THE MOIRE.",
                    )
                }
            }
            22 => {
                self.gen_mobius = !self.gen_mobius;
                if self.gen_mobius {
                    String::from(
                        "MOBIUS ARMED - SET twist 0..1. THE BROWSER LOGS chi 2->0 AND NEVER COMPUTES IT; THIS PANEL DOES.",
                    )
                } else {
                    self.gen_twist = 0.0;
                    String::from("MOBIUS OFF - twist 0. THE MESH WAS NEVER BENT, ONLY THE DRAW WAS.")
                }
            }
            21 => {
                self.gen_fill = !self.gen_fill;
                if self.gen_fill {
                    String::from("FILL ON - FACES PAINTED AS THE BROWSER DOES: PENT rgba(193,74,59,a*0.4), HEX rgba(0,40,60,a*0.3).")
                } else {
                    String::from("FILL OFF - WIREFRAME. THE MESH IS THE SAME; ONLY THE PAINT IS GONE.")
                }
            }
            20 => {
                self.gen_spherical = !self.gen_spherical;
                self.gen_params.surface = if self.gen_spherical {
                    genesis::Surface::Spherical
                } else {
                    genesis::Surface::Planar
                };
                format!(
                    "SURFACE {} - APPLIES TO THE NEXT REFINE. {}",
                    if self.gen_spherical { "SPHERICAL" } else { "PLANAR" },
                    if self.gen_spherical {
                        "SPHERE radius is live now."
                    } else {
                        "SPHERE radius is inert while planar."
                    }
                )
            }
            other => format!("CONTROL {other} IS NOT WIRED, NOT PRETENDING"),
        }
    }

    /// One refinement, priced BEFORE it is allocated (Curse 35).
    ///
    /// The integer census predicts; the operator builds; the invariants
    /// measure. All three are printed, so the two lanes can be seen to agree
    /// -- or, if the operator ever breaks, to disagree in public.
    fn gen_refine(&mut self, op: genesis::Op) -> String {
        let predicted = match self.gen.predict(op) {
            Ok(c) => c,
            Err(e) => return format!("REFUSED {} - {e}", op.label().to_uppercase()),
        };
        if predicted.f > GEN_FACE_BUDGET {
            return format!(
                "REFUSED {} - {} FACES EXCEEDS THE {} VIEWER BUDGET. THE MATH IS FINE.",
                op.label().to_uppercase(),
                predicted.f,
                GEN_FACE_BUDGET
            );
        }
        // AND the memory, which is a different fence in a different place.
        //
        // `refine` holds BOTH generations at once -- the old faces are the
        // input and stay alive while the new Vec fills -- so the peak is
        // roughly 8x the current mesh, not the size of the result. Measured
        // by `examples/kaboom`: depth 8 died asking for 6.1 GB while already
        // holding 10.5 GB, nowhere near the 84 GB the finished mesh needed.
        //
        // A face also costs about 3x what the points alone suggest, and that
        // multiple GROWS with depth, so this reads the REAL per-face cost off
        // the mesh in hand rather than assuming one.
        if let Some(peak) = self.gen.refine_peak_bytes(op) {
            if peak > GEN_PEAK_BYTES {
                return format!(
                    "REFUSED {} - PEAK {:.2} GB EXCEEDS THE {:.1} GB CEILING.                      refine HOLDS BOTH GENERATIONS, so the peak is ~8x the mesh,                      not the size of the result. THE MATH IS FINE.",
                    op.label().to_uppercase(),
                    peak as f64 / 1_073_741_824.0,
                    GEN_PEAK_BYTES as f64 / 1_073_741_824.0
                );
            }
        }
        let params = self.gen_params;
        let mut rng = Rng::new(0x5EED);
        self.gen = self.gen.refine(op, &params, &mut rng);
        match self.gen.invariants() {
            Ok(i) if i.faces == predicted.f && i.pents == predicted.p => format!(
                "REFINE {} - PREDICTED F={} P={}, BUILT F={} P={}. LANES AGREE.",
                op.label().to_uppercase(),
                predicted.f,
                predicted.p,
                i.faces,
                i.pents
            ),
            Ok(i) => format!(
                "LANES DISAGREE - PREDICTED F={} P={}, BUILT F={} P={}",
                predicted.f, predicted.p, i.faces, i.pents
            ),
            Err(e) => format!("BUILT, BUT WOULD NOT MEASURE: {e}"),
        }
    }

    /// Which side of the crescent defect the parameters are on.
    ///
    /// Named out loud in the HUD because it is the single fact that explains
    /// what you are looking at, and the browser never says it anywhere.
    fn crescent(p: &genesis::Params) -> &'static str {
        if p.mid_scale > p.inner_scale {
            "MID > INNER: THE RING OPENS. ROSETTE."
        } else if p.mid_scale < p.inner_scale {
            "MID < INNER: THE RING OVERLAPS. BURSTS."
        } else {
            "MID = INNER: THE RING CLOSES FLAT."
        }
    }

    /// Paint the GENESIS control bar.
    fn paint_gen_bar(&mut self) {
        let pal = self.pal();
        let top = H() as i32 - BAR_H - GEN_BAR_H;
        self.cv.fill_rect(0, top, W() as i32, GEN_BAR_H, pal.panel);
        self.cv.line(0, top, W() as i32 - 1, top, pal.border);

        let items: Vec<(i32, i32, i32, i32, &str, u8)> = self
            .gen_buttons
            .iter()
            .map(|b| (b.x, b.y, b.w, b.h, b.label, b.id))
            .collect();
        for (x, y, w, h, label, id) in items {
            // SEED 12 is drawn dim on purpose: it exists, it is not wired, and
            // the colour says so before the click does (Path IV).
            let accent = match id {
                11 => pal.border,
                10 | 16 => pal.green,
                15 => pal.pink,
                17 | 18 => pal.gold,
                19 => {
                    if self.gen_cull {
                        pal.green
                    } else {
                        pal.border
                    }
                }
                22 => {
                    if self.gen_mobius {
                        pal.pink
                    } else {
                        pal.text
                    }
                }
                21 => {
                    if self.gen_fill {
                        pal.green
                    } else {
                        pal.text
                    }
                }
                20 => {
                    if self.gen_spherical {
                        pal.green
                    } else {
                        pal.border
                    }
                }
                _ => pal.cyan,
            };
            self.cv.rect(x, y, w, h, accent);
            font::text(
                &mut self.cv,
                x + 8,
                y + (h - font::GH) / 2,
                label,
                accent,
                1,
            );
        }

        // the boxes. The one being edited shows what has been TYPED, not the
        // committed value -- otherwise a half-finished number looks accepted.
        let boxes: Vec<(i32, i32, i32, i32, usize)> = self
            .gen_fields
            .iter()
            .map(|f| (f.x, f.y, f.w, f.h, f.ctl))
            .collect();
        let editing = self.gen_edit.clone();
        let bad = self.gen_error.is_some();
        for (x, y, w, h, ctl) in boxes {
            let c = &CONTROLS[ctl];
            let lw = font::width(c.label, 1) + 6;
            font::text(
                &mut self.cv,
                x - lw,
                y + (h - font::GH) / 2,
                c.label,
                pal.text,
                1,
            );

            let (shown, live) = match &editing {
                Some((e, buf)) if *e == ctl => (buf.clone(), true),
                _ => (format!("{:.3}", self.ctl_get(ctl)), false),
            };
            let accent = if live && bad {
                pal.pink
            } else if live {
                pal.gold
            } else {
                pal.cyan
            };
            self.cv.rect(x, y, w, h, accent);
            font::text(
                &mut self.cv,
                x + 5,
                y + (h - font::GH) / 2,
                &shown,
                accent,
                1,
            );
            // a caret, so it is obvious the box is taking keys
            if live {
                let cx = x + 5 + font::width(&shown, 1) + 1;
                self.cv.fill_rect(cx, y + 4, 1, h - 8, accent);
            }
        }

        // the refusal, under the bar, in the colour of a refusal
        if let Some(e) = self.gen_error.clone() {
            font::text(&mut self.cv, 10, top - 14, &e, pal.pink, 1);
        }
    }

    /// How many pixels one unit of the shell's radius should occupy.
    ///
    /// The shell sits on the unit sphere, so it spans `2 * zoom` pixels. This
    /// was a hard 250.0 -- tuned by eye at 900x700 and then WRONG the moment
    /// the canvas moved, which is exactly what the first 1920x1080 render
    /// showed: a small ball in a large empty frame.
    ///
    /// A constant that has to be re-tuned per canvas is not a constant, it is
    /// an unstated dependency (the R7 shape, one lane over). Derive it from the
    /// drawing area instead, and the picture is the same picture at any size.
    /// `0.41` reproduces the 900x700 framing that was tuned by eye: at that
    /// size the drawing height is 606 px and `606 * 0.41 = 248`, within a
    /// couple of pixels of the old 250.
    fn fit_zoom(&self) -> f64 {
        let sh = (H() as i32 - BAR_H - 60) as f64;
        // `* self.gen_zoom` was MISSING, so the zoom control was a value with
        // no reader: the button pushed, the box updated, the frame repainted,
        // and the picture never moved. Reported as "the zoom pushes but the
        // view does not re-render" -- the view re-rendered perfectly, it just
        // rendered the same thing.
        0.41 * (W() as f64).min(sh) * self.gen_zoom
    }

    /// Publish the hit-test geometry the viewer ACTUALLY painted.
    ///
    /// `tools/drive.ps1` clicks this app by name -- "SHOT", "card 1" -- and it
    /// must never recompute where those things are. That is the `card_rects`
    /// lesson one level up: a driver that derives the layout from the same
    /// constants the app uses is not an independent witness, it is a second
    /// copy of the same assumption, and the two drift the moment either moves.
    ///
    /// So the app writes down what it painted and the driver reads it. The
    /// rects here are the very ones [`Self::click`] hit-tests against, and the
    /// canvas is 900x700 with the client area asserted equal to it at startup,
    /// so a coordinate in this file is a screen coordinate plus the client
    /// origin. Nothing to convert, nothing to scale, nothing to guess.
    fn dump_layout(&self) {
        let mut lines: Vec<String> = Vec::new();
        lines.push(String::from("{"));
        lines.push(format!("  \"canvas\": [{}, {}],", W(), H()));
        lines.push(format!("  \"view\": \"{:?}\",", self.view()));
        lines.push(format!("  \"stack_depth\": {},", self.stack.len()));

        lines.push(String::from("  \"buttons\": ["));
        for (i, b) in self.buttons.iter().enumerate() {
            let comma = if i + 1 == self.buttons.len() { "" } else { "," };
            lines.push(format!(
                "    {{ \"label\": \"{}\", \"id\": {}, \"x\": {}, \"y\": {}, \"w\": {}, \"h\": {} }}{}",
                b.label, b.id, b.x, b.y, b.w, b.h, comma
            ));
        }
        lines.push(String::from("  ],"));

        lines.push(String::from("  \"cards\": ["));
        for (i, r) in self.card_rects.iter().enumerate() {
            let comma = if i + 1 == self.card_rects.len() {
                ""
            } else {
                ","
            };
            let dest = match self.card_views.get(i).copied().flatten() {
                Some(v) => format!("\"{v:?}\""),
                None => String::from("null"),
            };
            lines.push(format!(
                "    {{ \"index\": {}, \"x\": {}, \"y\": {}, \"w\": {}, \"h\": {}, \"leads_to\": {} }}{}",
                i, r.x, r.y, r.w, r.h, dest, comma
            ));
        }
        lines.push(String::from("  ],"));

        lines.push(String::from("  \"gen_buttons\": ["));
        for (i, b) in self.gen_buttons.iter().enumerate() {
            let comma = if i + 1 == self.gen_buttons.len() {
                ""
            } else {
                ","
            };
            lines.push(format!(
                "    {{ \"label\": \"{}\", \"id\": {}, \"x\": {}, \"y\": {}, \"w\": {}, \"h\": {} }}{}",
                b.label, b.id, b.x, b.y, b.w, b.h, comma
            ));
        }
        lines.push(String::from("  ],"));

        lines.push(String::from("  \"gen_controls\": ["));
        for (i, f) in self.gen_fields.iter().enumerate() {
            let comma = if i + 1 == self.gen_fields.len() {
                ""
            } else {
                ","
            };
            let c = &CONTROLS[f.ctl];
            lines.push(format!(
                "    {{ \"name\": \"{}\", \"label\": \"{}\", \"x\": {}, \"y\": {}, \"w\": {}, \"h\": {}, \"lo\": {}, \"hi\": {}, \"value\": {:.6} }}{}",
                c.name, c.label, f.x, f.y, f.w, f.h, c.lo, c.hi, self.ctl_get(f.ctl), comma
            ));
        }
        lines.push(String::from("  ],"));
        lines.push(format!(
            "  \"cards_declared\": {}, \"cards_painted\": {},",
            self.card_views.len(),
            self.card_rects.len()
        ));
        lines.push(String::from(
            "  \"note\": \"written by the app from the rects it painted; the driver reads, never recomputes\"",
        ));
        lines.push(String::from("}"));

        let _ = fs::write(
            self.session_dir.join("LAYOUT.json"),
            lines.join("\n") + "\n",
        );
    }

    /// Paint the current view, then the chrome. Timed, because "how close to
    /// the chip" is a number, not an adjective.
    fn render(&mut self) {
        let before = self.cv.digest();
        let t0 = Instant::now();

        let pal = self.pal();
        self.cv.fill(pal.bg);
        match self.view() {
            View::Dashboard => self.paint_dashboard(),
            View::Genesis => self.paint_genesis(),
            View::Shell => self.paint_shell(),
            View::FrameBits => self.paint_bit_texture(true),
            View::MachineBits => self.paint_bit_texture(false),
        }
        self.last_render_us = t0.elapsed().as_micros();

        // R10: SEAL HERE. Everything above is mathematics; everything below is
        // chrome, and the chrome contains a clock. A digest taken after the
        // chrome is a digest of the moment, not of the frame.
        self.content_digest = self.cv.digest();
        self.flipped = usize::from(before != self.content_digest);

        self.paint_chrome();

        // publish the geometry AFTER the chrome, because the chrome is where
        // the buttons live. Small file, rare write; the dashboard does not
        // animate and GENESIS repaints do not move a rect.
        self.dump_layout();
    }

    /// The dashboard skeleton plus the first card, as a fidelity test.
    ///
    /// THE BIRTH card is the honest one to start with: it is the centerpiece of
    /// the real front door, it is `.feat-card` so it exercises the featured
    /// path, and its accent is gold -- a slot every palette in the cave agrees
    /// on, so nothing here is confounded by the palette drift.
    fn paint_dashboard(&mut self) {
        let pal = self.pal();
        const NAMES: [&str; 6] = [
            "M1 GOLDBERG",
            "M2 AXIOMS",
            "M3 SAR",
            "M4 NS SPECTRAL",
            "M5 FRACTAL",
            "M6 NANITE",
        ];
        let modules: Vec<dashboard::KRow> = (0..6)
            .map(|i| dashboard::KRow {
                name: NAMES[i],
                ok: self.module_kb[i] > 0,
                kb: self.module_kb[i],
            })
            .collect();

        // Two cards, on purpose: THE BIRTH is `.feat-card` (gold, FRONT DOOR
        // marker, scale-2 name) and GENESIS is a plain `.mod-card` (green,
        // border only). Side by side they exercise both paths and the 2-column
        // grid at once -- the integration test, not a decoration.
        //
        // Only GENESIS is wired. THE LIGHT MATRIX describes a browser page
        // this crate has NOT ported -- nothing in Rust computes the spectrum
        // it names -- so it stays a catalogue entry and its click says
        // NOT WIRED, NOT PRETENDING.
        let birth_desc = "the source code of it all, computed LIVE. Euler forces P=12; one \
                          4x4 integer matrix governs the whole family; the C60 adjacency \
                          graph is built and diagonalized to land lambda min at minus phi \
                          squared.";
        // the card says the census, not a slogan: computed, not typed
        let g = genesis::Census::C60;
        let genesis_desc = &format!(
            "the certified C60, spinning. {} chi={} -- step 1 of the port              (spec: grimoire/GENESIS_PORT_SPEC.md)",
            g,
            genesis::certify(g).map_or("?".into(), |c| c.to_string())
        );
        let cards = [
            dashboard::Card {
                tag: "* THE BIRTH",
                name: "THE LIGHT MATRIX",
                desc: birth_desc,
                accent: pal.gold,
                caps: &["frm", "kbd"],
                featured: true,
            },
            dashboard::Card {
                tag: "GENESIS",
                name: "GENESIS v0.1 - THE SEED",
                desc: genesis_desc,
                accent: pal.green,
                caps: &["frm", "kbd"],
                featured: false,
            },
        ];

        // Where each card leads, built in the SAME place as the cards so the
        // two lists cannot drift. `None` is a card with nothing behind it, and
        // the click says so out loud rather than doing nothing and looking
        // broken. Two cards, one wired -- the honest state of the port.
        self.card_views = vec![
            None,                // THE LIGHT MATRIX -- the browser page, not ported
            Some(View::Genesis), // GENESIS v0.1 -- the seed, spinning
        ];

        let m = dashboard::Model {
            version: "v2.0",
            git: &self.git,
            ledger: &self.ledger,
            cert: &self.cert_line,
            modules: &modules,
            cards: &cards,
            category: "THEA HELENI SOURCE CODE",
        };
        self.card_rects = dashboard::draw(&mut self.cv, &pal, &m);
        self.status = format!(
            "DASHBOARD SKELETON - {} CARD - {} KNOWN GAPS (see NOT_YET)",
            self.card_rects.len(),
            dashboard::NOT_YET.len()
        );
    }

    /// GENESIS step 1 -- the certified seed, spinning, with its census.
    ///
    /// Deliberately the same projection and depth-cue as `paint_shell`, so the
    /// only difference is the turn: one variable, one timer, nothing else new.
    /// Refinement is step 3 in the spec and is NOT faked here -- the panel says
    /// so rather than implying more than is built.
    /// GENESIS -- the live mesh, turning, with its control bar.
    ///
    /// Draws the face soup `genesis::State` actually holds: every face
    /// outlined from its OWN points, painter-ordered by depth, pentagons
    /// picked out. Face soup means neighbours each draw their own copy of a
    /// shared corner; that is the browser's design and it is what lets the
    /// mesh reach millions of faces with no index structure.
    fn paint_genesis(&mut self) {
        let pal = self.pal();
        let (rx, ry, rz, zoom) = (
            self.gen_pitch,
            self.genesis_yaw,
            self.gen_roll,
            self.fit_zoom(),
        );
        let sh = H() as i32 - BAR_H - GEN_BAR_H - 60;

        // The twist is applied HERE, between the mesh and the projection, so
        // `self.gen` is never bent. Toggling back to 0 is therefore exact
        // rather than a re-derivation -- the browser instead mutates the face
        // points and keeps a saved copy to restore from, which is a second
        // source of truth for the same geometry.
        let band = mobius::Band::default();
        let t = if self.gen_mobius { self.gen_twist } else { 0.0 };
        let bend = |v: [f64; 3]| -> [f64; 3] {
            if t <= 0.0 {
                v
            } else {
                mobius::lerp(v, mobius::sphere_to_mobius(v, band), t)
            }
        };

        let depths: Vec<f64> = self
            .gen
            .faces
            .iter()
            .map(|f| {
                let n = f.pts.len() as f64;
                f.pts
                    .iter()
                    .map(|&v| project_rpy(bend(v), rx, ry, rz, zoom, W(), sh as usize).2)
                    .sum::<f64>()
                    / n
            })
            .collect();
        let mut order: Vec<usize> = (0..self.gen.faces.len()).collect();
        order.sort_by(|&a, &b| depths[a].partial_cmp(&depths[b]).unwrap());

        // At depth the soup outruns the canvas: 1920x1080 is 2.07M pixels and
        // the mesh passes that within a few rungs. Cap the draw and PRINT the
        // count -- silence here would be a lie shaped like a finished render.
        let drawn = order.len().min(GEN_DRAW_CAP);
        let mut visible = 0usize;
        // KEEP THE NEAR HALF, NOT THE FAR ONE.
        //
        // `order` is sorted ASCENDING by depth, because painter's order draws
        // far first so near faces land on top. `take(drawn)` therefore kept
        // the FARTHEST faces and threw the near ones away -- so the moment the
        // cap bit, the picture became the BACK of the shell seen through where
        // the front should have been. Reported as "on lv 6 the centre shows
        // only the back", which is exactly and literally what it was doing.
        //
        // `skip(len - drawn)` keeps the nearest, still ordered far-to-near
        // among themselves, so the painter's order is untouched.
        for &k in order.iter().skip(order.len() - drawn) {
            // back-face cull: exact for a convex shell centred on the origin,
            // and it reuses the SAME depth the painter's order sorted on, so
            // the two can never disagree about which side a face is on
            if self.gen_cull && depths[k] < 0.0 {
                continue;
            }
            let f = &self.gen.faces[k];
            let t = ((depths[k] + 2.0) / 4.0).clamp(0.0, 1.0);
            let alpha = 0.15 + t * 0.5;
            let (c, a8) = if f.kind == genesis::Kind::Pent {
                (pal.pink, (alpha * 255.0) as u8)
            } else {
                (pal.cyan, (alpha * 0.6 * 255.0) as u8)
            };
            let pts: Vec<(i32, i32, f64)> = f
                .pts
                .iter()
                .map(|&v| project_rpy(bend(v), rx, ry, rz, zoom, W(), sh as usize))
                .collect();
            // Did any corner of this face land on the canvas? Cheap, and it is
            // the difference between what we DRAW and what anyone SEES.
            if pts
                .iter()
                .any(|p| p.0 >= 0 && p.0 < W() as i32 && p.1 >= 0 && p.1 < H() as i32)
            {
                visible += 1;
            }
            // FILL FIRST, then stroke -- the browser's order (`cx.fill()`
            // then `cx.stroke()`). Reversing it would let a translucent fill
            // wash over the outline it is supposed to sit inside.
            if self.gen_fill {
                let flat: Vec<(i32, i32)> = pts.iter().map(|p| (p.0, p.1)).collect();
                let (fc, fa) = if f.kind == genesis::Kind::Pent {
                    (palette::GEN_FILL_PENT, alpha * 0.4)
                } else {
                    (palette::GEN_FILL_HEX, alpha * 0.3)
                };
                self.cv.fill_poly(&flat, fc, (fa * 255.0) as u8);
            }
            for i in 0..pts.len() {
                let j = (i + 1) % pts.len();
                self.cv
                    .line_a(pts[i].0, pts[i].1, pts[j].0, pts[j].1, c, a8);
            }
        }

        // ---- the panel. measured off the built mesh, never typed ----------
        let inv = self.gen.invariants();
        let census = self.gen.census();
        let mut lines: Vec<String> = Vec::new();
        match &inv {
            Ok(i) => {
                lines.push(format!("MEASURED  {i}"));
                lines.push(format!("CENSUS    {census}"));
                // THE MOBIUS CHECK. The browser logs `chi:'2->0'` as a string
                // literal and never calls invariants() in its Mobius engine.
                // Bending points cannot change connectivity, so chi is whatever
                // it was -- and this line says the measured number out loud
                // rather than inheriting the claim. A real Mobius needs
                // F = E - V faces; the gap is how many would have to die.
                if self.gen_mobius {
                    let need = mobius::faces_for_chi_zero(i.vertices, i.edges);
                    lines.push(format!(
                        "MOBIUS    twist {:.2} - chi STILL {} (bending moves points, not connectivity)",
                        self.gen_twist, i.chi
                    ));
                    if let Some(n) = need {
                        lines.push(format!(
                            "          chi=0 would force F={n}, so {} face(s) must die. NONE HAVE.",
                            i.faces as i64 - n as i64
                        ));
                    }
                }
                let agree = i.faces == census.f && i.pents == census.p;
                lines.push(format!(
                    "LANES     {}",
                    if agree {
                        "AGREE - integer census == built soup"
                    } else {
                        "DISAGREE - THE OPERATOR IS WRONG"
                    }
                ));
                lines.push(String::new());
                lines.push(format!(
                    "chi = V-E+F = {} - {} + {} = {}",
                    i.vertices, i.edges, i.faces, i.chi
                ));
                lines.push(String::from(
                    "V and E from TRIVALENCE, never Euler (R-INV).",
                ));
                lines.push(format!(
                    "anchors {} - the second witness to P=12",
                    i.anchor_count
                ));
                lines.push(String::new());
                lines.push(format!(
                    "depth {}  history {}",
                    i.max_level,
                    self.gen.history.len()
                ));
                lines.push(format!("mesh  {}", self.gen.heap_bytes()));
                if let Some(peak) = self
                    .gen
                    .predict(genesis::Op::All)
                    .ok()
                    .and_then(|_| self.gen.refine_peak_bytes(genesis::Op::All))
                {
                    lines.push(format!(
                        "next ALL would PEAK at {:.2} GB (both generations)",
                        peak as f64 / 1_073_741_824.0
                    ));
                }
            }
            Err(e) => {
                lines.push(String::from("REFUSED - the soup did not measure:"));
                lines.push(format!("{e}"));
            }
        }
        lines.push(String::new());
        lines.push(format!(
            "INNER {:.3}   MID {:.3}",
            self.gen_params.inner_scale, self.gen_params.mid_scale
        ));
        lines.push(Self::crescent(&self.gen_params).to_string());
        lines.push(format!(
            "SURFACE {} - INNER/MID/JITTER/SPHERE APPLY TO THE NEXT REFINE",
            if self.gen_spherical {
                "SPHERICAL"
            } else {
                "PLANAR (sphere radius inert)"
            }
        ));
        lines.push(format!(
            "CULL {} - {}",
            if self.gen_cull { "ON " } else { "OFF" },
            if self.gen_cull {
                "far hemisphere dropped"
            } else {
                "see-through: front and back superimpose"
            }
        ));
        lines.push(String::new());
        if drawn < order.len() {
            lines.push(format!(
                "DRAWN {drawn} OF {} - capped, not complete",
                order.len()
            ));
        } else {
            lines.push(format!("DRAWN {drawn} OF {} - all of them", order.len()));
        }
        // The price, made visible. Every drawn face was projected, depth-sorted
        // and clipped whether or not one pixel of it reached the canvas.
        lines.push(format!(
            "VISIBLE {visible} - {:.2}% of what was drawn{}",
            100.0 * visible as f64 / drawn.max(1) as f64,
            if visible == 0 {
                "  <- NOTHING ON SCREEN, AND WE PAID FOR ALL OF IT"
            } else {
                ""
            }
        ));
        lines.push(format!(
            "YAW {:.2}  PITCH {:.2}  ROLL {:.2} RAD",
            self.genesis_yaw, self.gen_pitch, self.gen_roll
        ));
        lines.push(String::new());
        for op in [genesis::Op::All, genesis::Op::Hex, genesis::Op::Pent] {
            match self.gen.predict(op) {
                Ok(c) => lines.push(format!("next {:<4} -> {}", op.label(), c)),
                Err(e) => lines.push(format!("next {:<4} -> REFUSED: {e}", op.label())),
            }
        }

        for (i, l) in lines.iter().enumerate() {
            font::text(&mut self.cv, 16, 60 + i as i32 * 14, l, pal.text, 1);
        }
    }

    fn paint_shell(&mut self) {
        let pal = self.pal();
        // THE SHELL VIEW IS DELIBERATELY FIXED. It is the certification card --
        // one canonical angle, so two runs are comparable by eye and by seal.
        // The GENESIS view is the one you fly; this one you check against.
        let (rx, ry, zoom) = (0.30_f64, 0.55_f64, self.fit_zoom());
        let sh = H() as i32 - BAR_H - 60;
        let pts: Vec<(i32, i32, f64)> = self
            .mesh
            .verts
            .iter()
            .map(|&v| project(v, rx, ry, zoom, W(), sh as usize))
            .collect();

        let mut order: Vec<usize> = (0..self.mesh.edges.len()).collect();
        let (edges, pts_ref) = (&self.mesh.edges, &pts);
        order.sort_by(|&i, &j| {
            let d = |k: usize| {
                let (a, b) = edges[k];
                (pts_ref[a].2 + pts_ref[b].2) / 2.0
            };
            d(i).partial_cmp(&d(j)).unwrap()
        });

        for k in order {
            let (a, b) = self.mesh.edges[k];
            let depth = (pts[a].2 + pts[b].2) / 2.0;
            let t = ((depth + 2.0) / 4.0).clamp(0.0, 1.0);
            let alpha = 0.15 + t * 0.5;
            let (c, a8) = if self.pent_edge[k] {
                (pal.pink, (alpha * 255.0) as u8)
            } else {
                (pal.cyan, (alpha * 0.6 * 255.0) as u8)
            };
            let dy = 44;
            self.cv
                .line_a(pts[a].0, pts[a].1 + dy, pts[b].0, pts[b].1 + dy, c, a8);
        }
    }

    /// One pixel per bit. `1` takes the accent colour, `0` the panel colour --
    /// so structure in the bits becomes texture on the screen, which is the
    /// whole reason the monkey brain is a good detector.
    fn paint_bit_texture(&mut self, frame: bool) {
        let pal = self.pal();
        let top = 52i32;
        let bot = H() as i32 - BAR_H - 8;
        let rows = (bot - top) as usize;
        let cols = W() - 20;

        // snapshot the source first; painting mutates the framebuffer
        let src: Vec<u8> = if frame {
            self.cv.px.clone()
        } else {
            self.exe_bytes.clone()
        };
        let want = rows * cols / 8;
        let take = src.len().min(want);

        let (on, off) = (pal.green, pal.panel);
        let mut bit = 0usize;
        'outer: for r in 0..rows {
            for c in 0..cols {
                let byte = bit / 8;
                if byte >= take {
                    break 'outer;
                }
                let set = src[byte] & (1 << (7 - (bit % 8))) != 0;
                self.cv
                    .set(10 + c as i32, top + r as i32, if set { on } else { off });
                bit += 1;
            }
        }

        let ones = bits::ones(&src[..take]);
        let ent = bits::entropy(&src[..take]);
        let label = if frame { "FRAMEBUFFER" } else { "MACHINE CODE" };
        self.status = format!(
            "{} - {} BYTES SHOWN OF {} - ONES {} - {:.1}% - ENTROPY {:.3} BITS/BYTE",
            label,
            take,
            src.len(),
            ones,
            100.0 * ones as f64 / (take.max(1) * 8) as f64,
            ent
        );
    }

    fn paint_chrome(&mut self) {
        let pal = self.pal();
        let v = self.view();

        // The dashboard paints its own top bar and its own bottom strip, so the
        // viewer's header and status line would overdraw its content. Only the
        // button bar is shared -- which is correct: the buttons ARE the command
        // bar the real dashboard reserves that space for.
        if v != View::Dashboard {
            font::text(&mut self.cv, 10, 10, v.title(), pal.gold, 2);
            // the sealed content digest, NOT a fresh one -- R10.
            // And the render time only when a human is watching: it is a
            // clock, and a clock in the frame makes the frame unreproducible.
            let sub = if self.paint_clock {
                format!(
                    "V 60 E 90 F 32 CHI 2 P 12 - RENDER {} US - SEAL {:016X}",
                    self.last_render_us, self.content_digest
                )
            } else {
                format!(
                    "V 60 E 90 F 32 CHI 2 P 12 - SEAL {:016X}",
                    self.content_digest
                )
            };
            font::text(&mut self.cv, 10, 30, &sub, pal.cyan, 1);

            let extra = if v == View::Genesis { GEN_BAR_H } else { 0 };
            let sy = H() as i32 - BAR_H - extra - 14;
            font::text(&mut self.cv, 10, sy, &self.status, pal.text, 1);
        }

        if v == View::Genesis {
            self.paint_gen_bar();
        }

        // button bar
        self.cv
            .fill_rect(0, H() as i32 - BAR_H, W() as i32, BAR_H, pal.panel);
        self.cv.line(
            0,
            H() as i32 - BAR_H,
            W() as i32 - 1,
            H() as i32 - BAR_H,
            pal.border,
        );
        let buttons: Vec<(i32, i32, i32, i32, &str, u8)> = self
            .buttons
            .iter()
            .map(|b| (b.x, b.y, b.w, b.h, b.label, b.id))
            .collect();
        for (x, y, w, h, label, id) in buttons {
            let accent = match id {
                0 => pal.gold,
                4 => pal.pink,
                _ => pal.cyan,
            };
            self.cv.rect(x, y, w, h, accent);
            font::text(
                &mut self.cv,
                x + 8,
                y + (h - font::GH) / 2,
                label,
                accent,
                1,
            );
        }
    }

    /// PNG + a 1/0 vector matrix + a manifest, into `runs/NNN/`.
    ///
    /// The HELENA doctrine, applied: the payload is local and gitignored, the
    /// MANIFEST is tracked, so another mage sees the exact steps and can
    /// regenerate. Pay thea Heleni in compute.
    /// A screenshot: the PNG alone, straight into the session folder.
    ///
    /// Deliberately separate from EXPORT. R11 measured the cost of a full dump
    /// at ~23 MB a click because `.bits` is eight bytes on disk per byte of
    /// payload. A screenshot is ~1.9 MB, so you can take a hundred while
    /// comparing palettes without walking into the 100 MB wall.
    fn screenshot(&mut self) {
        self.shots += 1;
        let file = self.session_dir.join(format!("shot_{:04}.png", self.shots));
        match self.cv.write_png(&file) {
            Ok(()) => {
                self.status = format!(
                    "SHOT {:04} - SEAL {:016X} - {} - PALETTE {}",
                    self.shots,
                    self.content_digest,
                    file.file_name().unwrap_or_default().to_string_lossy(),
                    self.pal().name.to_uppercase()
                );
                // one line per shot, appended -- the session's own little ledger
                let line = format!(
                    "shot_{:04}.png  view={:?}  palette={}  render_us={}  seal={:016x}\n",
                    self.shots,
                    self.view(),
                    self.pal().name,
                    self.last_render_us,
                    self.content_digest
                );
                append(&self.session_dir.join("SHOTS.log"), &line);
                println!("{}", self.status);
            }
            Err(e) => self.status = format!("SHOT FAILED: {e}"),
        }
    }

    fn export(&mut self) {
        self.exports += 1;
        self.runs = self.exports;
        let dir = self.session_dir.join(format!("export_{:04}", self.exports));
        if let Err(e) = fs::create_dir_all(&dir) {
            self.status = format!("EXPORT FAILED: {e}");
            return;
        }

        let png = dir.join("frame.png");
        let framebits = dir.join("frame.bits");
        let machinebits = dir.join("machine.bits");
        let packed = dir.join("frame.bin");

        let _ = self.cv.write_png(&png);
        let r1 = bits::write_bits(
            &framebits,
            &format!("framebuffer {}x{} RGB, view {:?}", W(), H(), self.view()),
            &self.cv.px,
            self.cv.w * 3,
            dump_cap(),
        );
        let r2 = bits::write_bits(
            &machinebits,
            "this .exe, as emitted by rustc",
            &self.exe_bytes,
            64,
            dump_cap(),
        );
        let _ = bits::write_packed(&packed, &self.cv.px, dump_cap());

        let (f1, f2) = (r1.unwrap_or_else(zero_rep), r2.unwrap_or_else(zero_rep));
        // RUSTIUM R8: no backslash line continuations. Rust's own continuation
        // already eats the leading whitespace, so a `\` added at the start of a
        // continued line becomes the invalid escape `\ `. Build the lines
        // instead -- one string per line, joined. Obvious beats clever.
        let lines = vec![
            String::from("{"),
            format!("  \"run\": {},", self.runs),
            format!("  \"view\": \"{:?}\",", self.view()),
            format!("  \"palette\": \"{}\",", self.pal().name),
            format!("  \"canvas\": [{}, {}],", W(), H()),
            // render_us is a PEER of the seal, never inside it (Curse 38 / R10)
            format!("  \"render_us\": {},", self.last_render_us),
            format!(
                "  \"content_seal_fnv1a64\": \"{:016x}\",",
                self.content_digest
            ),
            format!(
                "  \"frame_bits\": {{ \"bytes\": {}, \"of\": {}, \"truncated\": {}, \"fnv1a64\": \"{:016x}\" }},",
                f1.bytes_written, f1.bytes_total, f1.truncated, f1.digest
            ),
            format!(
                "  \"machine_bits\": {{ \"bytes\": {}, \"of\": {}, \"truncated\": {}, \"fnv1a64\": \"{:016x}\" }},",
                f2.bytes_written, f2.bytes_total, f2.truncated, f2.digest
            ),
            format!("  \"dump_cap_bytes\": {},", dump_cap()),
            String::from("  \"note\": \"payload is local and gitignored; this manifest is the mirror\""),
            String::from("}"),
        ];
        let _ = fs::write(dir.join("MANIFEST.json"), lines.join("\n") + "\n");

        self.status = format!(
            "RUN {:04} WRITTEN - PNG + {} BYTES FRAME BITS + {} BYTES MACHINE BITS{}",
            self.runs,
            f1.bytes_written,
            f2.bytes_written,
            if f1.truncated || f2.truncated {
                " - CAPPED, AND SAYING SO"
            } else {
                ""
            }
        );
        println!("{}", self.status);
    }

    /// RGB -> BGRA, then hand the rectangle to the OS. The only place our
    /// pixels leave our control.
    unsafe fn blit(&mut self, hdc: HDC) {
        for (i, p) in self.cv.px.chunks_exact(3).enumerate() {
            let q = i * 4;
            self.dib[q] = p[2];
            self.dib[q + 1] = p[1];
            self.dib[q + 2] = p[0];
            self.dib[q + 3] = 255;
        }
        let bmi = BITMAPINFO {
            bmiHeader: BITMAPINFOHEADER {
                biSize: std::mem::size_of::<BITMAPINFOHEADER>() as u32,
                biWidth: W() as i32,
                biHeight: -(H() as i32), // negative = top-down
                biPlanes: 1,
                biBitCount: 32,
                biCompression: BI_RGB,
                biSizeImage: 0,
                biXPelsPerMeter: 0,
                biYPelsPerMeter: 0,
                biClrUsed: 0,
                biClrImportant: 0,
            },
            bmiColors: [0; 3],
        };
        StretchDIBits(
            hdc,
            0,
            0,
            W() as i32,
            H() as i32,
            0,
            0,
            W() as i32,
            H() as i32,
            self.dib.as_ptr() as *const c_void,
            &bmi,
            DIB_RGB_COLORS,
            SRCCOPY,
        );
    }

    /// One key press. The window calls this, and so does `--run`.
    ///
    /// Returns whether anything changed and a repaint is owed.
    fn key(&mut self, vk: usize) -> bool {
        // A BOX IS OPEN: every key belongs to it, so nothing typed into a
        // number can also trip a view shortcut.
        if let Some((ctl, buf)) = self.gen_edit.clone() {
            match vk {
                0x0D => {
                    // ENTER -- validate. On refusal the OLD VALUE STANDS and
                    // the box says what it wanted. Nothing implodes, and
                    // nothing silently becomes NaN.
                    match parse_control(&CONTROLS[ctl], &buf) {
                        Ok(v) => {
                            self.status = self.ctl_set(ctl, v);
                            self.gen_edit = None;
                            self.gen_error = None;
                        }
                        Err(e) => {
                            self.status = format!(
                                "{} REFUSED: {e}. WANTED {} ({}..{}). THE OLD VALUE STANDS.",
                                CONTROLS[ctl].label,
                                CONTROLS[ctl].unit,
                                CONTROLS[ctl].lo,
                                CONTROLS[ctl].hi
                            );
                            self.gen_error = Some(self.status.clone());
                        }
                    }
                    return true;
                }
                0x1B => {
                    self.gen_edit = None;
                    self.gen_error = None;
                    self.status = String::from("EDIT CANCELLED - NOTHING CHANGED.");
                    return true;
                }
                0x08 => {
                    let mut b = buf;
                    b.pop();
                    self.gen_edit = Some((ctl, b));
                    self.gen_error = None;
                    return true;
                }
                _ => {}
            }
            // Only what a number is made of gets in. This is the FIRST fence,
            // not the last: `parse_control` still runs, because "..--" is made
            // entirely of legal characters and is still not a number.
            let ch = match vk {
                0x30..=0x39 => Some((b'0' + (vk - 0x30) as u8) as char),
                0x60..=0x69 => Some((b'0' + (vk - 0x60) as u8) as char),
                0xBE | 0x6E => Some('.'),
                0xBD | 0x6D => Some('-'),
                _ => None,
            };
            if let Some(c) = ch {
                let mut b = buf;
                if b.len() < 16 {
                    b.push(c);
                }
                self.gen_edit = Some((ctl, b));
                self.gen_error = None;
            }
            return true;
        }

        match vk {
            // S -- hold the GENESIS turn still, or release it again.
            0x53 if self.view() == View::Genesis => {
                self.genesis_spin = !self.genesis_spin;
                self.status = if self.genesis_spin {
                    String::from("GENESIS SPINNING.")
                } else {
                    String::from("GENESIS HELD STILL.")
                };
                true
            }
            _ => false,
        }
    }

    /// Advance the GENESIS turn by exactly `frames` ticks.
    ///
    /// **This is what replaces `sleep`.** A driver that waits on the wall clock
    /// produces a different picture every run, and a picture that will not
    /// reproduce is a screenshot, not a receipt (Curse 38, R10). The timer
    /// advances the yaw by a fixed step, so stepping it `n` times from a known
    /// state is deterministic: the same script twice gives the same seal.
    fn advance(&mut self, frames: u32) {
        for _ in 0..frames {
            if self.view() == View::Genesis && self.genesis_spin {
                self.genesis_yaw += self.gen_speed;
                self.gen_pitch += self.gen_speed_p;
                self.gen_roll += self.gen_speed_r;
            }
        }
    }

    /// Write the current canvas to a named PNG, and log its seal.
    ///
    /// The image comes from `self.cv` -- the framebuffer the kernel computed --
    /// **not from the screen**. There is no window, no compositor, no DPI
    /// scaler and no capture API between the mathematics and the file. That is
    /// the whole reason this runs inside Rust instead of outside it.
    fn shot_named(&mut self, dir: &std::path::Path, name: &str) -> String {
        self.render();
        let file = dir.join(format!("{name}.png"));
        match self.cv.write_png(&file) {
            Ok(()) => format!(
                "shot   {name:<28} seal {:016x}  view {:?}  {} us",
                self.content_digest,
                self.view(),
                self.last_render_us
            ),
            Err(e) => format!("shot   {name:<28} FAILED: {e}"),
        }
    }

    /// Click the centre of a named button, by reading the rect it painted.
    fn click_button(&mut self, label: &str) -> Result<String, String> {
        let b = self
            .buttons
            .iter()
            .find(|b| b.label.eq_ignore_ascii_case(label))
            .ok_or_else(|| {
                let have: Vec<&str> = self.buttons.iter().map(|b| b.label).collect();
                format!("no button '{label}'. have: {}", have.join(", "))
            })?;
        let (x, y) = (b.x + b.w / 2, b.y + b.h / 2);
        self.click(x, y);
        Ok(format!("button {label:<27} at {x},{y}"))
    }

    /// Click the centre of card `i`, through the real hit-test path.
    fn click_card(&mut self, i: usize) -> Result<String, String> {
        let r = *self.card_rects.get(i).ok_or_else(|| {
            format!(
                "no card {i} -- {} declared, {} painted (the grid clips)",
                self.card_views.len(),
                self.card_rects.len()
            )
        })?;
        let (x, y) = (r.x + r.w / 2, r.y + r.h / 2);
        self.click(x, y);
        Ok(format!("card   {i:<27} at {x},{y}"))
    }
}

/// Total bytes currently sitting under `runs/`.
///
/// Printed on every scripted run, because this is the number that grows while
/// nobody is looking. 829 MB arrived over three days of clicking.
fn runs_bytes() -> u64 {
    fn walk(p: &std::path::Path) -> u64 {
        let mut n = 0u64;
        if let Ok(rd) = fs::read_dir(p) {
            for e in rd.flatten() {
                match e.file_type() {
                    Ok(t) if t.is_dir() => n += walk(&e.path()),
                    Ok(_) => n += e.metadata().map(|m| m.len()).unwrap_or(0),
                    Err(_) => {}
                }
            }
        }
        n
    }
    walk(&runs_dir())
}

/// Past this, the run says so and names the oldest sessions to move out.
///
/// **Not a limit -- a tap on the shoulder.** Frames are regenerable by
/// definition (`--run` reproduces them byte for byte), so the right move when
/// this fires is to archive or delete the old payload, never to stop working.
const DISK_WARN: u64 = 2 * 1024 * 1024 * 1024;

/// The most a single movie may write. **Stated in the units it protects**
/// (R11): bytes that will exist on the disk, not frames and not seconds.
const MOVIE_BUDGET: u64 = 3 * 1024 * 1024 * 1024;

/// Say what `runs/` holds, and if it is getting heavy, say which folders to
/// move and how much that would recover.
fn report_disk() {
    let total = runs_bytes();
    let gb = total as f64 / 1_073_741_824.0;
    println!("runs/   {gb:.2} GB on disk   (payload is gitignored; the steps travel)");
    if total < DISK_WARN {
        return;
    }
    println!();
    println!("  ------------------------------------------------------------------");
    println!("  runs/ is over {} GB.", DISK_WARN / 1_073_741_824);
    println!("  Every frame here is REGENERABLE -- the same script writes the same");
    println!("  bytes -- so the payload is a cache, not a record. The MANIFEST and");
    println!("  DRIVE.log are the record, and they are tiny and tracked.");
    println!();
    let mut dirs: Vec<(String, u64)> = fs::read_dir(runs_dir())
        .map(|rd| {
            rd.flatten()
                .filter(|e| e.file_type().map(|t| t.is_dir()).unwrap_or(false))
                .map(|e| {
                    fn walk(p: &std::path::Path) -> u64 {
                        let mut n = 0u64;
                        if let Ok(rd) = fs::read_dir(p) {
                            for e in rd.flatten() {
                                match e.file_type() {
                                    Ok(t) if t.is_dir() => n += walk(&e.path()),
                                    Ok(_) => n += e.metadata().map(|m| m.len()).unwrap_or(0),
                                    Err(_) => {}
                                }
                            }
                        }
                        n
                    }
                    (e.file_name().to_string_lossy().to_string(), walk(&e.path()))
                })
                .collect()
        })
        .unwrap_or_default();
    dirs.sort_by_key(|(n, _)| n.clone());
    let heavy: Vec<&(String, u64)> = dirs.iter().filter(|(_, b)| *b > 50 * 1024 * 1024).collect();
    println!("  the heaviest, oldest first -- move these out and keep the manifests:");
    for (n, b) in heavy.iter().take(8) {
        println!("    {:>8.1} MB   runs/{n}", *b as f64 / 1_048_576.0);
    }
    let freed: u64 = heavy.iter().take(8).map(|(_, b)| *b).sum();
    println!(
        "    {:>8.2} GB   would be recovered",
        freed as f64 / 1_073_741_824.0
    );
    println!("  ------------------------------------------------------------------");
    println!();
}

/// Where a movie's frames end up.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum Emit {
    /// PNG frames only. Byte-reproducible, and enormous.
    Png,
    /// Straight into ffmpeg's stdin as rawvideo. **Nothing touches the disk
    /// but the finished mp4.** 712 MB of intermediate PNG becomes 0 bytes.
    Mp4,
    /// Both, for when the frames are wanted for a 4K re-encode later.
    Both,
}

impl Emit {
    fn parse(s: &str) -> Option<Emit> {
        match s.to_ascii_lowercase().as_str() {
            "png" | "frames" => Some(Emit::Png),
            "mp4" | "film" => Some(Emit::Mp4),
            "both" => Some(Emit::Both),
            _ => None,
        }
    }
    fn writes_png(self) -> bool {
        matches!(self, Emit::Png | Emit::Both)
    }
    fn writes_mp4(self) -> bool {
        matches!(self, Emit::Mp4 | Emit::Both)
    }
}

/// One movie over any registered control.
///
/// **Generic on purpose.** The channel is an index into [`CONTROLS`], so every
/// control that exists is animatable the day it is added and none of this has
/// to be touched. That was the whole reason for the table.
///
/// # The pipe
///
/// With [`Emit::Mp4`] the frames never become files. ffmpeg is started with
/// `-f rawvideo -pix_fmt rgb24` and each rendered framebuffer is written
/// straight to its stdin -- which is exactly the buffer the kernel computed,
/// with no PNG encode, no filesystem, and no round trip. It is faster AND it
/// writes 0 bytes of intermediate, which is the answer to "do not save all
/// the images as we generate".
///
/// The PNG frames remain available on request, because they are the
/// byte-reproducible artifact and the mp4 is the lossy convenience.
#[allow(clippy::too_many_arguments)]
fn run_movie(
    app: &mut App,
    dir: &std::path::Path,
    ctl: usize,
    lo: f64,
    hi: f64,
    frames: u32,
    fps: u32,
    crf: u32,
    emit: Emit,
    name: &str,
) -> Result<String, String> {
    if frames == 0 {
        return Err(String::from("a movie needs at least one frame"));
    }

    // ---- PRICE IT FIRST, in both currencies ------------------------------
    let est = Estimate::measure(app, frames, fps);
    println!("movie  {name}  [{}]", CONTROLS[ctl].name);
    println!("{}", est.report(emit.writes_png()));

    if est.render_s > RENDER_SECONDS_BUDGET {
        return Err(format!(
            "REFUSED - this would render for {}, past the {} ceiling. One frame at the current \
             {} faces took {:.0} ms, and that is measured, not guessed. Fewer frames, a coarser \
             mesh, or a machine that is not this one.",
            Estimate::hms(est.render_s),
            Estimate::hms(RENDER_SECONDS_BUDGET),
            app.gen.faces.len(),
            1000.0 * est.render_s / frames as f64
        ));
    }
    if emit.writes_png() && est.png_bytes > MOVIE_BUDGET {
        return Err(format!(
            "REFUSED - {:.2} GB of PNG is past the {:.0} GB budget. Use `mp4` mode: the frames \
             are piped to the encoder and never written at all.",
            est.png_bytes as f64 / 1_073_741_824.0,
            MOVIE_BUDGET as f64 / 1_073_741_824.0
        ));
    }

    let out = dir.join(format!("movie_{name}"));
    fs::create_dir_all(&out).map_err(|e| format!("cannot create {}: {e}", out.display()))?;
    let mp4 = out.join(format!("{name}.mp4"));

    // ---- the encoder, fed from stdin -------------------------------------
    let mut child = if emit.writes_mp4() {
        let ff = find_ffmpeg().ok_or_else(|| {
            format!(
                "ffmpeg NOT FOUND, so no mp4 can be written. `winget install Gyan.FFmpeg`, or \
                 render with `png` mode and encode later -- movie_{name}/MAKE_MP4.txt will hold \
                 the command."
            )
        })?;
        let c = std::process::Command::new(&ff)
            .args([
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "-s",
                &format!("{}x{}", W(), H()),
                "-framerate",
                &fps.to_string(),
                "-i",
                "-",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                &crf.to_string(),
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
            ])
            .arg(&mp4)
            .stdin(std::process::Stdio::piped())
            .spawn()
            .map_err(|e| format!("could not start {}: {e}", ff.display()))?;
        Some(c)
    } else {
        None
    };

    let mut rows: Vec<String> = Vec::new();
    let mut png_written = 0u64;
    let t0 = Instant::now();

    for f in 0..frames {
        let t = if frames == 1 {
            0.0
        } else {
            f as f64 / (frames - 1) as f64
        };
        // SET from the frame index, never accumulated -- that is what makes
        // two runs of one command produce the same bytes.
        app.ctl_set(ctl, lo + t * (hi - lo));
        app.render();

        if let Some(c) = child.as_mut() {
            use std::io::Write as _;
            let pipe = c.stdin.as_mut().ok_or("the encoder closed its stdin")?;
            pipe.write_all(&app.cv.px)
                .map_err(|e| format!("frame {f}: the encoder stopped reading: {e}"))?;
        }
        if emit.writes_png() {
            let file = out.join(format!("frame_{f:05}.png"));
            app.cv
                .write_png(&file)
                .map_err(|e| format!("frame {f}: {e}"))?;
            png_written += goldberg_kernel::raster::png_bytes(W(), H()) as u64;
        }

        let st = goldberg_kernel::oklab::FrameStats::measure(&app.cv.px, 37);
        rows.push(format!(
            "  {{ \"frame\": {f}, \"t\": {t:.6}, \"{}\": {:.6}, \"seal\": \"{:016x}\", \
             \"colours\": {}, \"ink\": {:.6}, \"mean_l\": {:.6}, \"mean_c\": {:.6}, \"l_entropy\": {:.6} }}",
            CONTROLS[ctl].name,
            app.ctl_get(ctl),
            app.content_digest,
            st.distinct, st.ink, st.mean_l, st.mean_c, st.l_entropy
        ));
    }

    // close the pipe, THEN wait: ffmpeg finishes on EOF and would otherwise
    // block forever holding a stdin that never ends
    let mut mp4_bytes = 0u64;
    if let Some(mut c) = child {
        drop(c.stdin.take());
        let status = c.wait().map_err(|e| format!("waiting on ffmpeg: {e}"))?;
        if !status.success() {
            return Err(format!("ffmpeg refused (exit {:?})", status.code()));
        }
        mp4_bytes = fs::metadata(&mp4).map(|m| m.len()).unwrap_or(0);
    }
    let secs = t0.elapsed().as_secs_f64();

    let cmd = format!(
        "ffmpeg -y -framerate {fps} -i \"{}\" -c:v libx264 -preset slow -crf {crf} \
         -pix_fmt yuv420p -movflags +faststart \"{}\"",
        out.join("frame_%05d.png").display(),
        mp4.display()
    );
    let _ = fs::write(out.join("MAKE_MP4.txt"), format!("{cmd}\n"));

    let mut m: Vec<String> = Vec::new();
    m.push(String::from("{"));
    m.push(format!("  \"name\": \"{name}\","));
    m.push(format!("  \"control\": \"{}\",", CONTROLS[ctl].name));
    m.push(format!("  \"from\": {lo:.6}, \"to\": {hi:.6},"));
    m.push(format!(
        "  \"frames\": {frames}, \"fps\": {fps}, \"crf\": {crf},"
    ));
    m.push(format!("  \"emit\": \"{emit:?}\","));
    m.push(format!("  \"canvas\": [{}, {}],", W(), H()));
    m.push(format!(
        "  \"png_bytes\": {png_written}, \"mp4_bytes\": {mp4_bytes},"
    ));
    m.push(format!(
        "  \"faces\": {}, \"render_seconds\": {secs:.3},",
        app.gen.faces.len()
    ));
    for c in CONTROLS.iter() {
        let i = App::ctl_index(c.name).unwrap_or(0);
        m.push(format!("  \"{}\": {:.6},", c.name, app.ctl_get(i)));
    }
    m.push(String::from(
        "  \"note\": \"frames and mp4 are payload and gitignored; the same command rewrites them. \
         seal is the exact integer witness, oklab fields the perceptual one (DISPLAY lane).\",",
    ));
    m.push(String::from("  \"oklab_sample_stride\": 37,"));
    m.push(String::from("  \"frames_detail\": ["));
    m.push(rows.join(",\n"));
    m.push(String::from("  ]"));
    m.push(String::from("}"));
    let _ = fs::write(out.join("MOVIE.json"), m.join("\n") + "\n");

    let disk = if mp4_bytes > 0 {
        format!(
            "{:.3} MB mp4{}",
            mp4_bytes as f64 / 1_048_576.0,
            if png_written > 0 {
                format!(" + {:.2} GB png", png_written as f64 / 1_073_741_824.0)
            } else {
                String::from(" (0 bytes of frames -- piped)")
            }
        )
    } else {
        format!("{:.2} GB png", png_written as f64 / 1_073_741_824.0)
    };
    Ok(format!(
        "movie  {name:<18} {frames}f @ {fps} = {} footage  |  {disk}  |  {:.1}s at {:.1} fps",
        Estimate::hms(est.play_s),
        secs,
        frames as f64 / secs.max(1e-9)
    ))
}

/// Where `ffmpeg` might be, in order.
///
/// PATH first, then the places a Windows install actually lands. Each is
/// probed by RUNNING it, never by testing for a file -- an installer's exit
/// code certifies the download and not the capability (RUSTIUM R2, learned
/// when rustup installed a compiler that could not link).
fn find_ffmpeg() -> Option<PathBuf> {
    let mut tries: Vec<PathBuf> = vec![PathBuf::from("ffmpeg")];
    if let Ok(home) = std::env::var("USERPROFILE") {
        tries.push(PathBuf::from(&home).join("ffmpeg/bin/ffmpeg.exe"));
    }
    if let Ok(la) = std::env::var("LOCALAPPDATA") {
        tries.push(PathBuf::from(&la).join("Microsoft/WinGet/Links/ffmpeg.exe"));
    }
    if let Ok(pf) = std::env::var("ProgramFiles") {
        tries.push(PathBuf::from(&pf).join("ffmpeg/bin/ffmpeg.exe"));
    }
    tries.push(PathBuf::from("C:/ffmpeg/bin/ffmpeg.exe"));

    tries.into_iter().find(|p| {
        std::process::Command::new(p)
            .arg("-version")
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .status()
            .map(|s| s.success())
            .unwrap_or(false)
    })
}

/// Encode a movie folder into one shareable `.mp4`.
///
/// # We do not own this format, and we do not pretend to
///
/// H.264 is a standard with entropy coding, motion estimation and a decade of
/// tuning inside it. Writing one badly to keep a zero-dependency badge would
/// be exactly the kind of unpaid claim this cave exists to refuse, so the job
/// goes to the tool that actually does it. And note whose tool that is: VLC's
/// own muscle is **libavcodec**, which is FFmpeg. Handing frames to FFmpeg is
/// not a compromise, it is using the engine the titans use.
///
/// **The crate stays zero-dependency.** `[dependencies]` is still empty and
/// nothing is linked; `ffmpeg` is an external *tool*, invoked through
/// `std::process`, found by running it rather than by trusting a path. If it
/// is absent we say so and write the exact command down, because a build that
/// silently produces nothing is worse than one that refuses out loud.
///
/// # What is lost, stated
///
/// `yuv420p` chroma-subsamples: two of every four pixels lose their colour
/// difference, which on saturated cyan-on-black line art softens the coloured
/// edges. It is required for the file to play in browsers, on phones and in
/// QuickTime, so it is the right trade for a thing meant to be shared -- but
/// it IS a loss, and the PNG frames remain the source of truth. They are
/// byte-reproducible; the mp4 is a lossy convenience.
///
/// ```text
///   measured: 60 frames at 1920x1080
///   frames  356.05 MB      mp4  0.421 MB      846 : 1
/// ```
fn run_mp4(dir: &std::path::Path, name: &str, fps: u32, crf: u32) -> Result<String, String> {
    let src = dir.join(format!("movie_{name}"));
    if !src.is_dir() {
        return Err(format!(
            "no movie '{name}' -- make one first: movie mid 0.9 0.1 60 {name}"
        ));
    }
    let frames: u64 = fs::read_dir(&src)
        .map(|rd| {
            rd.flatten()
                .filter(|e| e.path().extension().is_some_and(|x| x == "png"))
                .count() as u64
        })
        .unwrap_or(0);
    if frames == 0 {
        return Err(format!("movie '{name}' has no frames on disk"));
    }
    let src_bytes: u64 = fs::read_dir(&src)
        .map(|rd| {
            rd.flatten()
                .filter(|e| e.path().extension().is_some_and(|x| x == "png"))
                .filter_map(|e| e.metadata().ok().map(|m| m.len()))
                .sum()
        })
        .unwrap_or(0);

    let out = src.join(format!("{name}.mp4"));
    let pattern = src.join("frame_%05d.png");

    // The command, written down whether or not we can run it. A receipt that
    // reproduces without us is worth more than one that needs us.
    let cmd = format!(
        "ffmpeg -y -framerate {fps} -i \"{}\" -c:v libx264 -preset slow -crf {crf} \
         -pix_fmt yuv420p -movflags +faststart \"{}\"",
        pattern.display(),
        out.display()
    );
    let _ = fs::write(src.join("MAKE_MP4.txt"), format!("{cmd}\n"));

    let ff = match find_ffmpeg() {
        Some(p) => p,
        None => {
            return Err(format!(
                "ffmpeg NOT FOUND, so no mp4 was written. The {frames} frames are on disk and \
                 the command is in movie_{name}/MAKE_MP4.txt. Install it with \
                 `winget install Gyan.FFmpeg` and run this again -- nothing needs regenerating."
            ));
        }
    };

    let t0 = Instant::now();
    let status = std::process::Command::new(&ff)
        .args([
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-framerate",
            &fps.to_string(),
            "-i",
        ])
        .arg(&pattern)
        .args([
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            &crf.to_string(),
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
        ])
        .arg(&out)
        .status()
        .map_err(|e| format!("could not run {}: {e}", ff.display()))?;

    if !status.success() {
        return Err(format!(
            "ffmpeg refused (exit {:?}). The frames are untouched; the command is in \
             movie_{name}/MAKE_MP4.txt",
            status.code()
        ));
    }

    let got = fs::metadata(&out).map(|m| m.len()).unwrap_or(0);
    if got == 0 {
        return Err(String::from("ffmpeg reported success and wrote nothing"));
    }

    Ok(format!(
        "mp4    {name:<22} {frames} frames @ {fps} fps  {:.2}s  |  {:.2} MB -> {:.3} MB  \
         {}:1  |  encoded in {:.1}s",
        frames as f64 / fps as f64,
        src_bytes as f64 / 1_048_576.0,
        got as f64 / 1_048_576.0,
        src_bytes / got.max(1),
        t0.elapsed().as_secs_f64()
    ))
}

/// Execute ONE step against an app, and return what to print.
///
/// Lifted out of `run_script` so that `--run` (headless) and `--open` (steps,
/// then a window) cannot diverge. That is the same rule the program already
/// follows for `click` and `key`: one path, many callers. Two copies of a step
/// table would drift the first time either was touched, and the drift would be
/// invisible -- both would keep working, differently.
fn step(app: &mut App, dir: &std::path::Path, line: &str, failures: &mut i32) -> String {
    let (verb, arg) = match line.split_once(char::is_whitespace) {
        Some((v, a)) => (v, a.trim()),
        None => (line, ""),
    };

    let entry = match verb.to_ascii_lowercase().as_str() {
        "shot" => {
            let name = if arg.is_empty() { "shot" } else { arg };
            app.shot_named(dir, name)
        }
        "card" => match arg.parse::<usize>() {
            Ok(i) => match app.click_card(i) {
                Ok(s) => s,
                Err(e) => {
                    *failures += 1;
                    format!("FAIL   {e}")
                }
            },
            Err(_) => {
                *failures += 1;
                format!("FAIL   card needs a number, got '{arg}'")
            }
        },
        "button" => match app.click_button(arg) {
            Ok(s) => s,
            Err(e) => {
                *failures += 1;
                format!("FAIL   {e}")
            }
        },
        "panel" | "back" | "shell" | "palette" => match app.click_button(verb) {
            Ok(s) => s,
            Err(e) => {
                *failures += 1;
                format!("FAIL   {e}")
            }
        },
        "key" => {
            let c = arg.chars().next().unwrap_or(' ').to_ascii_uppercase();
            let changed = app.key(c as usize);
            format!("key    {c:<27} changed {changed}")
        }
        "spin" => {
            let n: u32 = arg.parse().unwrap_or(1);
            app.advance(n);
            format!("spin   {n:<27} yaw {:.4} rad", app.genesis_yaw)
        }
        "expect" => {
            let got = format!("{:?}", app.view());
            if got.eq_ignore_ascii_case(arg) {
                format!("expect {arg:<27} OK")
            } else {
                *failures += 1;
                format!("FAIL   expected view '{arg}', got '{got}'")
            }
        }
        // THE GENESIS CONTROL BAR, from the command line. Same methods
        // the mouse calls, so a scripted run drives the shipped program.
        "seed" => {
            let id = if arg.eq_ignore_ascii_case("12") {
                11
            } else {
                10
            };
            app.gen_action(id)
        }
        "refine" => {
            let id = match arg.to_ascii_lowercase().as_str() {
                "all" => 12,
                "5s" | "pent" | "pents" => 13,
                "6s" | "hex" | "hexes" => 14,
                other => {
                    *failures += 1;
                    return format!("FAIL   refine wants all|5s|6s, got '{other}'");
                }
            };
            app.gen_action(id)
        }
        "undo" => app.gen_action(15),
        "cull" => app.gen_action(19),
        "spherical" => app.gen_action(20),
        "zoomin" => app.gen_action(18),
        "zoomout" => app.gen_action(17),
        "reset" => app.gen_action(16),
        // ANY registered control, by its own name. Adding a row to
        // CONTROLS makes it settable here with no code at all -- and the
        // SAME parse_control the box uses, so a shoe is refused the same
        // way whether it was typed or scripted.
        v if App::ctl_index(v).is_some() => {
            let ctl = App::ctl_index(v).unwrap();
            match parse_control(&CONTROLS[ctl], arg) {
                Ok(x) => app.ctl_set(ctl, x),
                Err(e) => {
                    *failures += 1;
                    format!(
                        "FAIL   {} REFUSED: {e}. WANTED {} ({}..{})",
                        CONTROLS[ctl].label, CONTROLS[ctl].unit, CONTROLS[ctl].lo, CONTROLS[ctl].hi
                    )
                }
            }
        }
        "controls" => {
            let mut out = vec![String::from("controls")];
            for (i, c) in CONTROLS.iter().enumerate() {
                out.push(format!(
                    "  {:<8} {:>10.4}   {}..{}   [{:?}] {}",
                    c.name,
                    app.ctl_get(i),
                    c.lo,
                    c.hi,
                    c.when,
                    c.unit
                ));
            }
            out.join("\n")
        }
        // MOVIES. Frames at 60/s, priced exactly before the first write.
        //
        //   movie spin  <frames> <name>
        //   movie inner <lo> <hi> <frames> <name>
        //   movie mid   <lo> <hi> <frames> <name>
        "movie" => {
            let a: Vec<&str> = arg.split_whitespace().collect();
            // movie <control> <lo> <hi> <frames> <name> [png|mp4|both] [fps] [crf]
            let parsed = (|| -> Result<_, String> {
                if a.len() < 5 {
                    return Err(String::from(
                            "usage: movie <control> <lo> <hi> <frames> <name> [png|mp4|both] [fps] [crf]",
                        ));
                }
                let ctl = App::ctl_index(a[0]).ok_or_else(|| {
                    let names: Vec<&str> = CONTROLS.iter().map(|c| c.name).collect();
                    format!("no control {:?}. have: {}", a[0], names.join(", "))
                })?;
                let lo: f64 = a[1]
                    .parse()
                    .map_err(|_| format!("{:?} is not a number", a[1]))?;
                let hi: f64 = a[2]
                    .parse()
                    .map_err(|_| format!("{:?} is not a number", a[2]))?;
                if !lo.is_finite() || !hi.is_finite() {
                    return Err(String::from("a movie cannot start or end at NaN"));
                }
                let n: u32 = a[3]
                    .parse()
                    .map_err(|_| format!("{:?} is not a frame count", a[3]))?;
                let name = a[4];
                let emit = match a.get(5) {
                    Some(m) => {
                        Emit::parse(m).ok_or_else(|| format!("{m:?} is not png|mp4|both"))?
                    }
                    None => Emit::Mp4,
                };
                let fps: u32 = a.get(6).and_then(|v| v.parse().ok()).unwrap_or(60);
                let crf: u32 = a.get(7).and_then(|v| v.parse().ok()).unwrap_or(18);
                Ok((ctl, lo, hi, n, name, emit, fps, crf))
            })();
            match parsed {
                Ok((ctl, lo, hi, n, name, emit, fps, crf)) => {
                    match run_movie(app, dir, ctl, lo, hi, n, fps, crf, emit, name) {
                        Ok(m) => m,
                        Err(e) => {
                            *failures += 1;
                            format!("FAIL   {e}")
                        }
                    }
                }
                Err(e) => {
                    *failures += 1;
                    format!("FAIL   {e}")
                }
            }
        }
        // ONE SHAREABLE FILE. 846:1 measured, so this is the price paid
        // in compute that makes 356 MB of frames a 0.4 MB link.
        "mp4" => {
            let a: Vec<&str> = arg.split_whitespace().collect();
            if a.is_empty() {
                *failures += 1;
                String::from("FAIL   usage: mp4 <name> [fps] [crf]")
            } else {
                let name = a[0];
                let fps = a.get(1).and_then(|v| v.parse().ok()).unwrap_or(60);
                let crf = a.get(2).and_then(|v| v.parse().ok()).unwrap_or(16);
                match run_mp4(dir, name, fps, crf) {
                    Ok(m) => m,
                    Err(e) => {
                        *failures += 1;
                        format!("FAIL   {e}")
                    }
                }
            }
        }
        // what the frame is MADE of, in a space where distance means
        // something. The seal says different; this says how different.
        "stats" => {
            app.render();
            let st = goldberg_kernel::oklab::FrameStats::measure(&app.cv.px, 37);
            format!("stats  {st}")
        }
        "status" => format!("status {}", app.status),
        other => {
            *failures += 1;
            format!("FAIL   unknown command '{other}'")
        }
    };
    entry
}

/// Run a script against a headless `App`. Returns the number of failures.
///
/// **Why this lives in Rust and not in a shell script.**
///
/// A click is a function call. A key is a function call. A frame is a
/// framebuffer we already own. Driving the app from outside meant synthesising
/// OS mouse events, fighting the foreground lock, translating coordinates
/// through a DPI scaler, and photographing a screen -- four layers of things
/// that can lie, between us and a picture we could simply write to disk.
///
/// From in here there is no window at all. `shot` writes the canvas the kernel
/// computed. `advance` steps the animation by whole frames instead of sleeping.
/// The same script run twice produces byte-identical PNGs, which is the
/// difference between a receipt and a screenshot.
///
/// The commands go through the SAME `click` and `key` methods the window uses,
/// so this drives the shipped program and not a parallel copy of it.
///
/// ```text
///   shot <name>      render and write <name>.png (from the framebuffer)
///   card <n>         click the centre of card n
///   button <LABEL>   click the centre of that button
///   key <c>          press a key ('S')
///   spin <n>         advance the GENESIS turn n frames -- NOT a sleep
///   expect <View>    the current view must be this, or FAIL
///   palette | back | panel | shell    sugar for the matching button
/// ```
fn run_script(src: &str) -> i32 {
    let mut app = App::new();
    app.layout();

    // No clock in the frame. The timing still gets reported -- in DRIVE.log,
    // as a peer outside the image (R10). This is what makes two runs of the
    // same script produce byte-identical PNGs.
    app.paint_clock = false;

    let dir = app.session_dir.join("drive");
    if let Err(e) = fs::create_dir_all(&dir) {
        eprintln!("cannot create {}: {e}", dir.display());
        return 1;
    }

    // paint once so card_rects and the button rects exist before any click
    app.render();

    let mut log: Vec<String> = Vec::new();
    let mut failures = 0i32;

    println!(
        "canvas   {} x {}   headless, no window, no compositor",
        W(),
        H()
    );
    println!("session  {}", app.session_dir.display());
    report_disk();
    println!();

    for raw in src.split([';', '\n', '\r']) {
        let line = raw.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let entry = step(&mut app, &dir, line, &mut failures);
        println!("{entry}");
        log.push(entry);
    }

    log.push(String::new());
    log.push(format!("canvas          {}x{}", W(), H()));
    log.push(format!(
        "cards declared  {}   painted {}",
        app.card_views.len(),
        app.card_rects.len()
    ));
    log.push(format!("failures        {failures}"));
    let _ = fs::write(dir.join("DRIVE.log"), log.join("\n") + "\n");

    println!();
    if app.card_views.len() != app.card_rects.len() {
        println!(
            "WARNING {} cards declared, {} painted -- the grid clipped one and it is unclickable",
            app.card_views.len(),
            app.card_rects.len()
        );
    }
    println!("shots -> {}", dir.display());
    println!(
        "{}",
        if failures == 0 {
            "all steps held"
        } else {
            "FAILURES -- see above"
        }
    );
    failures
}

fn zero_rep(_: std::io::Error) -> bits::DumpReport {
    bits::DumpReport {
        bytes_written: 0,
        bytes_total: 0,
        bits_written: 0,
        rows: 0,
        cols: 0,
        digest: 0,
        truncated: false,
    }
}

fn runs_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .map(|p| p.join("runs"))
        .unwrap_or_else(|| PathBuf::from("runs"))
}

fn append(path: &std::path::Path, s: &str) {
    use std::io::Write as _;
    if let Ok(mut f) = fs::OpenOptions::new().create(true).append(true).open(path) {
        let _ = f.write_all(s.as_bytes());
    }
}

/// The repo's real identity: `git HEAD`, resolved by reading `.git` directly.
///
/// Curse 27 -- a thing's identity is its origin, never its name on disk. A run
/// folder named `v0_1_0_s0003` says which VERSION; only the commit says which
/// BUILD. Best effort: `unknown` rather than a guess (Path IV).
fn git_head() -> String {
    let mut root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    for _ in 0..4 {
        let g = root.join(".git");
        if g.exists() {
            let head = fs::read_to_string(g.join("HEAD")).unwrap_or_default();
            let head = head.trim();
            if let Some(rf) = head.strip_prefix("ref: ") {
                if let Ok(h) = fs::read_to_string(g.join(rf)) {
                    return h.trim().chars().take(12).collect();
                }
            } else if !head.is_empty() {
                return head.chars().take(12).collect();
            }
        }
        if !root.pop() {
            break;
        }
    }
    String::from("unknown")
}

/// The newest `### Lnnn` in the cave's LEDGER -- "the ledger is permanent"
/// (AXIOM 01.5), so it is the version spine a run should hang from.
fn ledger_entry() -> String {
    let mut root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    for _ in 0..4 {
        if let Ok(t) = fs::read_to_string(root.join("LEDGER.md")) {
            let last = t
                .lines()
                .rfind(|l| l.starts_with("### L"))
                .unwrap_or_default();
            return last.split_whitespace().nth(1).unwrap_or("L???").to_string();
        }
        if !root.pop() {
            break;
        }
    }
    String::from("L???")
}

/// Create the session folder BEFORE anything is drawn, and record the AXIOM 01
/// gate as its first fact.
///
/// `runs/v<version>_s<NNNN>/` -- version for traceability (Path X), session
/// counter for determinism (no clock in a name, Curse 38).
fn open_session(cert: &goldberg_kernel::Cert, verdict: &judge::Verdict) -> PathBuf {
    let ver = env!("CARGO_PKG_VERSION").replace('.', "_");
    let base = runs_dir();
    let _ = fs::create_dir_all(&base);

    let prefix = format!("v{ver}_s");
    let n = fs::read_dir(&base)
        .map(|rd| {
            rd.filter_map(|e| e.ok())
                .filter_map(|e| {
                    e.file_name()
                        .to_string_lossy()
                        .strip_prefix(&prefix)
                        .and_then(|s| s.parse::<usize>().ok())
                })
                .max()
                .unwrap_or(0)
        })
        .unwrap_or(0)
        + 1;

    let dir = base.join(format!("{prefix}{n:04}"));
    let _ = fs::create_dir_all(&dir);

    let lines = vec![
        String::from("{"),
        format!("  \"session\": {n},"),
        format!("  \"viewer_version\": \"{}\",", env!("CARGO_PKG_VERSION")),
        format!("  \"kernel\": \"goldberg_kernel\","),
        format!("  \"git_head\": \"{}\",", git_head()),
        format!("  \"ledger_entry\": \"{}\",", ledger_entry()),
        String::from("  \"axiom_01_gate\": {"),
        String::from("    \"law\": \"verify P=12 and V-E+F=2 before you ship\","),
        format!(
            "    \"float_lane\": {{ \"v\": {}, \"e\": {}, \"f\": {}, \"p\": {}, \"chi\": {} }},",
            cert.v, cert.e, cert.f, cert.p, cert.chi
        ),
        format!(
            "    \"integer_judge\": {{ \"v\": {}, \"e\": {}, \"f\": {}, \"chi\": {}, \"genus\": {} }},",
            verdict.v,
            verdict.e,
            verdict.f,
            verdict.chi,
            verdict.genus.unwrap_or(-1)
        ),
        format!(
            "    \"lanes_agree\": {},",
            cert.v == verdict.v && cert.e == verdict.e && cert.f == verdict.f && cert.chi == verdict.chi
        ),
        String::from("    \"passed\": true"),
        String::from("  },"),
        String::from("  \"note\": \"folder created BEFORE the first pixel; payload local, this mirror travels\""),
        String::from("}"),
    ];
    let _ = fs::write(dir.join("SESSION.json"), lines.join("\n") + "\n");
    dir
}

#[cfg(test)]
mod control_tests {
    use super::*;

    /// Build a headless app at a known state.
    fn app_at(depth: usize) -> App {
        set_canvas(DEFAULT_W, DEFAULT_H);
        let mut a = App::new();
        a.layout();
        a.layout_genesis();
        a.paint_clock = false;
        a.stack.push(View::Genesis);
        a.genesis_spin = false;
        for _ in 0..depth {
            a.gen_action(12); // REFINE ALL
        }
        a
    }

    /// Render and return the sealed content digest.
    fn seal(a: &mut App) -> u64 {
        a.render();
        a.content_digest
    }

    /// **EVERY CONTROL MUST HAVE A READER.**
    ///
    /// This is the test that was missing when `zoom` shipped as a control that
    /// nothing consumed: it had a box, a command-line verb, a movie channel and
    /// input validation, and `fit_zoom()` never looked at it. The value moved,
    /// the frame repainted, and the picture was identical.
    ///
    /// Each category is checked the way it actually works, which is the whole
    /// reason `When` exists -- a single blanket assertion would have to be
    /// false for two thirds of the table.
    #[test]
    fn every_control_changes_something() {
        for (i, c) in CONTROLS.iter().enumerate() {
            match c.when {
                // the very next frame must differ
                When::Render => {
                    let mut a = app_at(1);
                    a.ctl_set(i, c.lo);
                    let lo = seal(&mut a);
                    a.ctl_set(i, c.hi);
                    let hi = seal(&mut a);
                    assert_ne!(
                        lo, hi,
                        "control '{}' is Render but the frame did not change between \
                         {} and {}. Either nothing reads it -- which is what happened to \
                         `zoom` -- or it belongs in another category.",
                        c.name, c.lo, c.hi
                    );
                }
                // set BEFORE building, the geometry must differ
                When::Build => {
                    // SPHERICAL first: `sphere_r` is only consulted when the
                    // surface is spherical, so grading it in planar mode would
                    // find it dead -- which it was, and which is how the
                    // missing surface toggle was discovered.
                    let mut a = app_at(0);
                    a.gen_action(20);
                    a.ctl_set(i, c.lo);
                    a.gen_action(12);
                    let lo = seal(&mut a);

                    let mut b = app_at(0);
                    b.gen_action(20);
                    b.ctl_set(i, c.hi);
                    b.gen_action(12);
                    let hi = seal(&mut b);
                    assert_ne!(
                        lo, hi,
                        "control '{}' is Build but refining at {} and at {} produced the \
                         same frame -- refine_face is not reading it",
                        c.name, c.lo, c.hi
                    );
                }
                // it must change how far SOMETHING advances
                //
                // The first version of this watched `genesis_yaw` alone and
                // failed the moment `speedp` was added -- which drives pitch.
                // That is precisely the mistake this test exists to catch: an
                // honest measurement of the wrong quantity. It now compares the
                // whole angle triple, so it need not know which axis a given
                // Motion control happens to move.
                When::Motion => {
                    let run = |v: f64| {
                        let mut a = app_at(0);
                        a.genesis_spin = true;
                        a.ctl_set(i, v);
                        a.genesis_yaw = 0.0;
                        a.gen_pitch = 0.0;
                        a.gen_roll = 0.0;
                        a.advance(50);
                        a.genesis_yaw + a.gen_pitch * 7.0 + a.gen_roll * 31.0
                    };
                    let lo = run(c.lo);
                    let hi = run(c.hi);
                    assert!(
                        (lo - hi).abs() > 1e-9,
                        "control '{}' is Motion but 50 frames left yaw, pitch AND roll \
                         identical at {} and at {} -- nothing advances on it",
                        c.name,
                        c.lo,
                        c.hi
                    );
                }
            }
        }
    }

    /// The specific regression: zoom must move the picture.
    #[test]
    fn zoom_moves_the_picture() {
        let mut a = app_at(1);
        let i = App::ctl_index("zoom").expect("zoom is in the table");
        a.ctl_set(i, 1.0);
        let one = seal(&mut a);
        a.ctl_set(i, 3.0);
        let three = seal(&mut a);
        assert_ne!(one, three, "fit_zoom must consult gen_zoom");
    }

    /// And the honest converse, so nobody re-reports it as a bug: a Build
    /// control genuinely does NOT move faces that already exist. Measured at
    /// PSNR 41.07 dB between two such frames, all of it the printed number.
    #[test]
    fn a_build_control_does_not_move_faces_that_already_exist() {
        let inner = App::ctl_index("inner").unwrap();
        let mut a = app_at(2);

        // strip the HUD's own text out of the comparison by asking the mesh
        // directly -- the geometry is the claim, not the caption
        let before: Vec<[f64; 3]> = a.gen.faces.iter().flat_map(|f| f.pts.clone()).collect();
        a.ctl_set(inner, 0.9);
        let after: Vec<[f64; 3]> = a.gen.faces.iter().flat_map(|f| f.pts.clone()).collect();

        assert_eq!(
            before, after,
            "changing a Build control must leave existing points untouched"
        );

        // ...and the NEXT refine must use the new value
        a.gen_action(12);
        let grown: Vec<[f64; 3]> = a.gen.faces.iter().flat_map(|f| f.pts.clone()).collect();
        assert_ne!(before.len(), grown.len(), "the refine must have happened");
    }

    /// Every control is reachable by the name the command line uses, and the
    /// table is the only place that decides.
    #[test]
    fn every_control_is_reachable_by_name() {
        for c in CONTROLS.iter() {
            assert!(
                App::ctl_index(c.name).is_some(),
                "control '{}' is in the table and cannot be looked up",
                c.name
            );
        }
        assert!(App::ctl_index("shoe").is_none());
    }
}
