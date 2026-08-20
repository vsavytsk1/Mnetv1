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
use goldberg_kernel::palette::{Palette, ALL};
use goldberg_kernel::raster::{project, Canvas};
use goldberg_kernel::rng::Rng;
use goldberg_kernel::{certify, judge, Mesh};

use gos_win32::*;

/// The canvas, and therefore the client area -- `AdjustWindowRect` sizes the
/// window to yield exactly this, and the app refuses to claim pixel-exactness
/// if the OS disagrees. 1920x1080 on a 2560x1440 panel, so the whole frame is
/// on screen with the window frame to spare.
const W: usize = 1920;
const H: usize = 1080;
const BAR_H: i32 = 34;

/// One full frame, in source bytes: `W * H * 3`.
const FRAME_BYTES: usize = W * H * 3;

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
const DUMP_CAP: usize = FRAME_BYTES;

/// WM_TIMER id for the GENESIS turn.
const GENESIS_TIMER: usize = 1;

/// Height of the GENESIS control bar, which sits above the main button bar.
const GEN_BAR_H: i32 = 34;

/// The most faces the viewer will BUILD. The mathematics is fine far past
/// this -- `genesis::grow` counts to `u64` -- so the refusal names the number
/// and says whose limit it is (Curse 35: state the cost before allocating).
const GEN_FACE_BUDGET: u64 = 400_000;

/// The most faces the viewer will DRAW in one frame. Distinct from the build
/// budget on purpose: the mesh may legitimately be larger than the canvas can
/// show, and the HUD prints `DRAWN n OF m` so the shortfall is a number rather
/// than a silence.
const GEN_DRAW_CAP: usize = 60_000;

/// A continuous control. The browser's `<input type=range>`.
///
/// The value does NOT live here -- it lives in [`genesis::Params`], which is
/// what the operator actually reads. A slider that carried its own copy would
/// be a second source of truth, and the two would drift the moment either
/// moved (the `card_rects` lesson, one widget down).
struct Slider {
    x: i32,
    y: i32,
    w: i32,
    h: i32,
    label: &'static str,
    id: u8,
    lo: f64,
    hi: f64,
}

impl Slider {
    fn hit(&self, mx: i32, my: i32) -> bool {
        mx >= self.x && mx < self.x + self.w && my >= self.y - 6 && my < self.y + self.h + 6
    }
    /// Where a click lands, in the slider's own units.
    fn value_at(&self, mx: i32) -> f64 {
        let t = ((mx - self.x) as f64 / self.w.max(1) as f64).clamp(0.0, 1.0);
        self.lo + t * (self.hi - self.lo)
    }
    /// Where a value sits, in pixels.
    fn knob_x(&self, v: f64) -> i32 {
        let t = ((v - self.lo) / (self.hi - self.lo)).clamp(0.0, 1.0);
        self.x + (t * self.w as f64) as i32
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
    /// INNER and MID
    gen_sliders: Vec<Slider>,
}

thread_local! {
    static APP: RefCell<Option<App>> = const { RefCell::new(None) };
}

fn main() {
    // A click is a function call and a frame is a buffer we already own, so
    // the driver lives HERE, not in a shell wrapping the OS. See run_script.
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut i = 0;
    let mut script: Option<String> = None;

    while i < args.len() {
        match args[i].as_str() {
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

    match script {
        // headless: no window, no compositor, no capture API. The PNGs come
        // straight off the framebuffer the kernel computed.
        Some(src) => std::process::exit(run_script(&src)),
        None => unsafe { run() },
    }
}

const HELP: &str = "GOS VIEWER -- a window, painted by the kernel.

  gos_viewer                       open the window
  gos_viewer --run \"<steps>\"       run steps headless, write PNGs, exit
  gos_viewer --script <file>       the same, from a file

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

  We do NOT own H.264 and do not pretend to: the job goes to ffmpeg, which is
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

unsafe fn run() {
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
    let dpi_exact = SetProcessDpiAwarenessContext(DPI_PER_MONITOR_AWARE_V2) != 0;

    if RegisterClassW(&wc) == 0 {
        eprintln!("RegisterClassW failed");
        return;
    }

    APP.with(|a| *a.borrow_mut() = Some(App::new()));

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
        right: W as LONG,
        bottom: H as LONG,
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
    let exact = dpi_exact && cw == W as LONG && ch == H as LONG;
    println!("DPI aware   : {dpi_exact}");
    println!("client area : {cw} x {ch}   (canvas {W} x {H})");
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
                        app.genesis_yaw += 0.012;
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
            cv: Canvas::new(W, H, pal.bg),
            dib: vec![0u8; W * H * 4],
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
            gen_params: genesis::Params::default(),
            gen_buttons: Vec::new(),
            gen_sliders: Vec::new(),
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
        let y = H as i32 - BAR_H + 6;
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
            if let Some((id, v)) = self
                .gen_sliders
                .iter()
                .find(|s| s.hit(mx, my))
                .map(|s| (s.id, s.value_at(mx)))
            {
                self.status = self.gen_set(id, v);
                return true;
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
        let y = H as i32 - BAR_H - GEN_BAR_H + 6;
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

        // the sliders take the rest of the bar, split evenly
        self.gen_sliders.clear();
        x += 12;
        let room = (W as i32 - 20 - x).max(120);
        let each = room / 2;
        for (i, (id, label, lo, hi)) in
            [(20u8, "INNER", 0.05_f64, 0.95_f64), (21, "MID", 0.05, 0.95)]
                .into_iter()
                .enumerate()
        {
            let lw = font::width(label, 1) + 8;
            let sx = x + i as i32 * each + lw;
            self.gen_sliders.push(Slider {
                x: sx,
                y: y + h / 2 - 2,
                w: each - lw - 90,
                h: 4,
                label,
                id,
                lo,
                hi,
            });
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
                self.gen_params = genesis::Params::default();
                format!(
                    "RESET - THE SEED, AND INNER {:.2} MID {:.2} BACK TO THE BROWSER DEFAULTS.",
                    p.inner_scale, p.mid_scale
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

    /// Set a slider's value, by id. Shared by the mouse and by `--run`.
    fn gen_set(&mut self, id: u8, v: f64) -> String {
        match id {
            20 => {
                self.gen_params.inner_scale = v.clamp(0.05, 0.95);
                format!(
                    "INNER {:.3}  (MID {:.3}) - {}",
                    self.gen_params.inner_scale,
                    self.gen_params.mid_scale,
                    Self::crescent(&self.gen_params)
                )
            }
            21 => {
                self.gen_params.mid_scale = v.clamp(0.05, 0.95);
                format!(
                    "MID {:.3}  (INNER {:.3}) - {}",
                    self.gen_params.mid_scale,
                    self.gen_params.inner_scale,
                    Self::crescent(&self.gen_params)
                )
            }
            other => format!("SLIDER {other} IS NOT WIRED"),
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
        let top = H as i32 - BAR_H - GEN_BAR_H;
        self.cv.fill_rect(0, top, W as i32, GEN_BAR_H, pal.panel);
        self.cv.line(0, top, W as i32 - 1, top, pal.border);

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

        let sliders: Vec<(i32, i32, i32, i32, &str, u8, f64)> = self
            .gen_sliders
            .iter()
            .map(|s| {
                let v = match s.id {
                    20 => self.gen_params.inner_scale,
                    _ => self.gen_params.mid_scale,
                };
                (s.x, s.y, s.w, s.h, s.label, s.id, v)
            })
            .collect();
        for (x, y, w, h, label, id, v) in sliders {
            let lw = font::width(label, 1) + 8;
            font::text(&mut self.cv, x - lw, y - 3, label, pal.text, 1);
            self.cv.fill_rect(x, y, w, h, pal.border);
            let kx = self.gen_sliders[if id == 20 { 0 } else { 1 }].knob_x(v);
            // filled to the knob, so the eye reads the value without the number
            self.cv.fill_rect(x, y, (kx - x).max(0), h, pal.cyan);
            self.cv.disc(kx, y + h / 2, 5, pal.cyan, 255);
            font::text(
                &mut self.cv,
                x + w + 10,
                y - 3,
                &format!("{v:.2}"),
                pal.text,
                1,
            );
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
        let sh = (H as i32 - BAR_H - 60) as f64;
        0.41 * (W as f64).min(sh)
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
        lines.push(format!("  \"canvas\": [{}, {}],", W, H));
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

        lines.push(String::from("  \"gen_sliders\": ["));
        for (i, sl) in self.gen_sliders.iter().enumerate() {
            let comma = if i + 1 == self.gen_sliders.len() {
                ""
            } else {
                ","
            };
            let v = if sl.id == 20 {
                self.gen_params.inner_scale
            } else {
                self.gen_params.mid_scale
            };
            lines.push(format!(
                "    {{ \"label\": \"{}\", \"id\": {}, \"x\": {}, \"y\": {}, \"w\": {}, \"lo\": {}, \"hi\": {}, \"value\": {:.4} }}{}",
                sl.label, sl.id, sl.x, sl.y, sl.w, sl.lo, sl.hi, v, comma
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
        let (rx, ry, zoom) = (0.30_f64, self.genesis_yaw, self.fit_zoom());
        let sh = H as i32 - BAR_H - GEN_BAR_H - 60;

        let depths: Vec<f64> = self
            .gen
            .faces
            .iter()
            .map(|f| {
                let n = f.pts.len() as f64;
                f.pts
                    .iter()
                    .map(|&v| project(v, rx, ry, zoom, W, sh as usize).2)
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
        for &k in order.iter().take(drawn) {
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
                .map(|&v| project(v, rx, ry, zoom, W, sh as usize))
                .collect();
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
                    "depth {}  history {}  undo cost {} KB",
                    i.max_level,
                    self.gen.history.len(),
                    self.gen.snapshot_bytes() / 1024
                ));
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
        lines.push(String::new());
        if drawn < order.len() {
            lines.push(format!(
                "DRAWN {drawn} OF {} - capped, not complete",
                order.len()
            ));
        } else {
            lines.push(format!("DRAWN {drawn} OF {} - all of them", order.len()));
        }
        lines.push(format!("YAW {:.2} RAD", self.genesis_yaw));
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
        let (rx, ry, zoom) = (0.30_f64, 0.55_f64, self.fit_zoom());
        let sh = H as i32 - BAR_H - 60;
        let pts: Vec<(i32, i32, f64)> = self
            .mesh
            .verts
            .iter()
            .map(|&v| project(v, rx, ry, zoom, W, sh as usize))
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
        let bot = H as i32 - BAR_H - 8;
        let rows = (bot - top) as usize;
        let cols = W - 20;

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
            let sy = H as i32 - BAR_H - extra - 14;
            font::text(&mut self.cv, 10, sy, &self.status, pal.text, 1);
        }

        if v == View::Genesis {
            self.paint_gen_bar();
        }

        // button bar
        self.cv
            .fill_rect(0, H as i32 - BAR_H, W as i32, BAR_H, pal.panel);
        self.cv.line(
            0,
            H as i32 - BAR_H,
            W as i32 - 1,
            H as i32 - BAR_H,
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
            &format!("framebuffer {}x{} RGB, view {:?}", W, H, self.view()),
            &self.cv.px,
            self.cv.w * 3,
            DUMP_CAP,
        );
        let r2 = bits::write_bits(
            &machinebits,
            "this .exe, as emitted by rustc",
            &self.exe_bytes,
            64,
            DUMP_CAP,
        );
        let _ = bits::write_packed(&packed, &self.cv.px, DUMP_CAP);

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
            format!("  \"canvas\": [{}, {}],", W, H),
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
            format!("  \"dump_cap_bytes\": {},", DUMP_CAP),
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
                biWidth: W as i32,
                biHeight: -(H as i32), // negative = top-down
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
            W as i32,
            H as i32,
            0,
            0,
            W as i32,
            H as i32,
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
                self.genesis_yaw += 0.012;
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

/// One movie: N frames, priced exactly before the first one is written.
///
/// **The price is knowable, so it is stated.** `png_bytes` is exact rather than
/// approximate -- stored deflate makes a frame's size a pure function of the
/// canvas -- so a 60-frame 8K movie can be refused *before* it writes 5.5 GB,
/// with the real number in the refusal. That is Curse 35 with the arithmetic
/// actually available.
///
/// Every frame carries two witnesses:
///
/// * the **seal**, an exact integer digest of the framebuffer. Brittle by
///   design: flip one pixel and it moves completely, so it answers *different
///   or not* and never *how different*.
/// * the **OKLab statistics**, which answer the second question. Perceptual,
///   so `mean_l` and `l_entropy` move smoothly across a sweep where the seal
///   just scatters. This is the topology of the pixels, beside the topology of
///   the bytes that painted them.
fn run_movie(
    app: &mut App,
    dir: &std::path::Path,
    channel: &str,
    lo: f64,
    hi: f64,
    frames: u32,
    name: &str,
) -> Result<String, String> {
    if frames == 0 {
        return Err(String::from("a movie needs at least one frame"));
    }
    let per = goldberg_kernel::raster::png_bytes(W, H) as u64;
    let total = per * frames as u64;
    if total > MOVIE_BUDGET {
        return Err(format!(
            "REFUSED - {frames} frames at {W}x{H} is {} B per frame = {:.2} GB, over the {:.0} GB \
             movie budget. The renderer is fine; the disk is the fence. Fewer frames, or a \
             smaller canvas.",
            per,
            total as f64 / 1_073_741_824.0,
            MOVIE_BUDGET as f64 / 1_073_741_824.0
        ));
    }

    let out = dir.join(format!("movie_{name}"));
    fs::create_dir_all(&out).map_err(|e| format!("cannot create {}: {e}", out.display()))?;

    println!(
        "movie  {name}: {frames} frames x {} B = {:.2} GB, priced before the first write",
        per,
        total as f64 / 1_073_741_824.0
    );

    let mut rows: Vec<String> = Vec::new();
    let mut written = 0u64;
    let t0 = Instant::now();

    for f in 0..frames {
        // f/(frames-1) so a single frame is the START and the last frame is
        // exactly `hi` -- an off-by-one here would silently never reach the end
        let t = if frames == 1 {
            0.0
        } else {
            f as f64 / (frames - 1) as f64
        };
        match channel {
            "spin" => {
                // one full turn across the whole movie, deterministic: the yaw
                // is SET from the frame index, never accumulated from a clock
                app.genesis_yaw = t * std::f64::consts::TAU;
            }
            "inner" => {
                app.gen_set(20, lo + t * (hi - lo));
            }
            "mid" => {
                app.gen_set(21, lo + t * (hi - lo));
            }
            other => return Err(format!("unknown movie channel '{other}'")),
        }
        app.render();
        let file = out.join(format!("frame_{f:05}.png"));
        app.cv
            .write_png(&file)
            .map_err(|e| format!("frame {f}: {e}"))?;
        written += per;

        // stride 37: prime, so it never aligns with a row width and samples
        // the whole frame evenly. ~56k of 2.07M pixels, and it SAYS so.
        let st = goldberg_kernel::oklab::FrameStats::measure(&app.cv.px, 37);
        rows.push(format!(
            "  {{ \"frame\": {f}, \"t\": {t:.6}, \"{channel}\": {:.6}, \"seal\": \"{:016x}\", \
             \"colours\": {}, \"ink\": {:.6}, \"mean_l\": {:.6}, \"mean_c\": {:.6}, \"l_entropy\": {:.6} }}",
            match channel {
                "spin" => app.genesis_yaw,
                "inner" => app.gen_params.inner_scale,
                _ => app.gen_params.mid_scale,
            },
            app.content_digest,
            st.distinct,
            st.ink,
            st.mean_l,
            st.mean_c,
            st.l_entropy
        ));
    }
    let secs = t0.elapsed().as_secs_f64();

    // MOVIE.json is the STEPS -- it travels. The frames are payload and are
    // gitignored, because `--run` regenerates them byte for byte.
    let mut m: Vec<String> = Vec::new();
    m.push(String::from("{"));
    m.push(format!("  \"name\": \"{name}\","));
    m.push(format!("  \"channel\": \"{channel}\","));
    m.push(format!("  \"from\": {lo:.6}, \"to\": {hi:.6},"));
    m.push(format!("  \"frames\": {frames},"));
    m.push(format!("  \"canvas\": [{W}, {H}],"));
    m.push(format!(
        "  \"bytes_per_frame\": {per}, \"bytes_total\": {written},"
    ));
    m.push(format!(
        "  \"faces\": {}, \"inner\": {:.6}, \"mid\": {:.6},",
        app.gen.faces.len(),
        app.gen_params.inner_scale,
        app.gen_params.mid_scale
    ));
    m.push(String::from(
        "  \"note\": \"frames are payload and gitignored; --run regenerates them byte for byte. \
         seal is the exact integer witness, the oklab fields are the perceptual one (DISPLAY \
         lane: cbrt and powf are not correctly rounded).\",",
    ));
    m.push(String::from("  \"oklab_sample_stride\": 37,"));
    m.push(String::from("  \"frames_detail\": ["));
    m.push(rows.join(",\n"));
    m.push(String::from("  ]"));
    m.push(String::from("}"));
    let _ = fs::write(out.join("MOVIE.json"), m.join("\n") + "\n");

    Ok(format!(
        "movie  {name:<22} {frames} frames  {:.2} GB  {:.1} s  {:.1} fps  -> movie_{name}/",
        written as f64 / 1_073_741_824.0,
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

    println!("canvas   {W} x {H}   headless, no window, no compositor");
    println!("session  {}", app.session_dir.display());
    report_disk();
    println!();

    for raw in src.split([';', '\n', '\r']) {
        let line = raw.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }
        let (verb, arg) = match line.split_once(char::is_whitespace) {
            Some((v, a)) => (v, a.trim()),
            None => (line, ""),
        };

        let entry = match verb.to_ascii_lowercase().as_str() {
            "shot" => {
                let name = if arg.is_empty() { "shot" } else { arg };
                app.shot_named(&dir, name)
            }
            "card" => match arg.parse::<usize>() {
                Ok(i) => match app.click_card(i) {
                    Ok(s) => s,
                    Err(e) => {
                        failures += 1;
                        format!("FAIL   {e}")
                    }
                },
                Err(_) => {
                    failures += 1;
                    format!("FAIL   card needs a number, got '{arg}'")
                }
            },
            "button" => match app.click_button(arg) {
                Ok(s) => s,
                Err(e) => {
                    failures += 1;
                    format!("FAIL   {e}")
                }
            },
            "panel" | "back" | "shell" | "palette" => match app.click_button(verb) {
                Ok(s) => s,
                Err(e) => {
                    failures += 1;
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
                    failures += 1;
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
                        failures += 1;
                        log.push(format!("FAIL   refine wants all|5s|6s, got '{other}'"));
                        continue;
                    }
                };
                app.gen_action(id)
            }
            "undo" => app.gen_action(15),
            "reset" => app.gen_action(16),
            "inner" | "mid" => {
                let id = if verb == "inner" { 20 } else { 21 };
                match arg.parse::<f64>() {
                    Ok(v) => app.gen_set(id, v),
                    Err(_) => {
                        failures += 1;
                        format!("FAIL   {verb} wants a number, got '{arg}'")
                    }
                }
            }
            // MOVIES. Frames at 60/s, priced exactly before the first write.
            //
            //   movie spin  <frames> <name>
            //   movie inner <lo> <hi> <frames> <name>
            //   movie mid   <lo> <hi> <frames> <name>
            "movie" => {
                let a: Vec<&str> = arg.split_whitespace().collect();
                let parsed: Result<(&str, f64, f64, u32, &str), String> = match a.as_slice() {
                    ["spin", n, name] => n
                        .parse::<u32>()
                        .map(|k| ("spin", 0.0, 1.0, k, *name))
                        .map_err(|_| format!("frames must be a number, got '{n}'")),
                    [ch @ ("inner" | "mid"), lo, hi, n, name] => {
                        match (lo.parse::<f64>(), hi.parse::<f64>(), n.parse::<u32>()) {
                            (Ok(l), Ok(h), Ok(k)) => Ok((*ch, l, h, k, *name)),
                            _ => Err(format!("bad numbers in 'movie {arg}'")),
                        }
                    }
                    _ => Err(String::from(
                        "usage: movie spin <frames> <name> | movie inner|mid <lo> <hi> <frames> <name>",
                    )),
                };
                match parsed {
                    Ok((ch, lo, hi, n, name)) => {
                        match run_movie(&mut app, &dir, ch, lo, hi, n, name) {
                            Ok(msg) => msg,
                            Err(e) => {
                                failures += 1;
                                format!("FAIL   {e}")
                            }
                        }
                    }
                    Err(e) => {
                        failures += 1;
                        format!("FAIL   {e}")
                    }
                }
            }
            // ONE SHAREABLE FILE. 846:1 measured, so this is the price paid
            // in compute that makes 356 MB of frames a 0.4 MB link.
            "mp4" => {
                let a: Vec<&str> = arg.split_whitespace().collect();
                if a.is_empty() {
                    failures += 1;
                    String::from("FAIL   usage: mp4 <name> [fps] [crf]")
                } else {
                    let name = a[0];
                    let fps = a.get(1).and_then(|v| v.parse().ok()).unwrap_or(60);
                    let crf = a.get(2).and_then(|v| v.parse().ok()).unwrap_or(16);
                    match run_mp4(&dir, name, fps, crf) {
                        Ok(m) => m,
                        Err(e) => {
                            failures += 1;
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
                failures += 1;
                format!("FAIL   unknown command '{other}'")
            }
        };

        println!("{entry}");
        log.push(entry);
    }

    // the receipt
    log.push(String::new());
    log.push(format!("canvas          {W}x{H}"));
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
