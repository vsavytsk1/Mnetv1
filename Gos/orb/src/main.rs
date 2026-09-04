//! GOS ORB v0.2 -- the spini spini byte topology, now on the ICOSPHERE lane.
//!
//! v0.1 rendered C60's 32 faces at ~17 KB per face. This one uses
//! `sphere::Ico` -- exact index subdivision, no float decides adjacency -- so
//! LEVEL- / LEVEL+ walks the same byte stream from 20 faces to 81,920 and the
//! duplication becomes visible exactly as `orb_growth` proved it does.
//!
//! chi is COUNTED by the integer judge at every level, never recited.
//!
//! ```powershell
//! cargo run -p gos_orb --release            # its own machine code
//! cargo run -p gos_orb --release -- FILE
//! ```

use std::cell::RefCell;
use std::collections::HashSet;
use std::ffi::c_void;
use std::fs;
use std::path::PathBuf;
use std::time::Instant;

use goldberg_kernel::palette::{Palette, Rgb, ALL};
use goldberg_kernel::raster::{project, Canvas};
use goldberg_kernel::sphere::{self, Ico};
use goldberg_kernel::{bits, font, judge, layout::Rect};

use gos_win32::*;

const DEFAULT_W: usize = 1180;
const DEFAULT_H: usize = 820;

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
const HUD_W: i32 = 320;
const BLOCK: usize = 64;
const TICK: u32 = 33;
const TIMER_ID: usize = 1;
/// levels the buttons may reach. L7 is 327,680 faces -- affordable, and the
/// judge there is ~0.5 s, so it is the honest ceiling for an interactive panel.
/// The deepest subdivision the orb will build.
///
/// `sphere::FACE_BUDGET` is 6,000,000 and the kernel would allow L9
/// (5,242,880 faces); this is the ORB's own, tighter fence, so the two are
/// distinct on purpose and either can be the binding one.
///
/// L8 is 20 * 4^8 = 1,310,720 faces. Raised from 7 because L7 built and judged
/// comfortably, and a fence should sit where the machine actually complains
/// rather than where it was first guessed.
const MAX_LEVEL: u32 = 8;

struct Shell {
    ico: Ico,
    level: u32,
    chi: i64,
    genus: i64,
    judged_us: u128,
    /// per face: ink 0..255, and whether its byte block repeats
    ink: Vec<u8>,
    repeat: Vec<bool>,
    repeats: usize,
    per_face: usize,
}

impl Shell {
    fn build(level: u32, bytes: &[u8]) -> Option<Shell> {
        let ico = Ico::level(level).ok()?;
        let t0 = Instant::now();
        let v = ico.rotation_system().and_then(|s| judge::check(&s).ok())?;
        let judged_us = t0.elapsed().as_micros();

        let n = ico.faces.len();
        let order = ico.curve_order();
        let per = bytes.len().div_ceil(n).max(1);
        let mut ink = vec![0u8; n];
        let mut repeat = vec![false; n];
        let mut seen: HashSet<u64> = HashSet::with_capacity(n);
        for (slot, &fi) in order.iter().enumerate() {
            let s = (slot * per).min(bytes.len());
            let e = ((slot + 1) * per).min(bytes.len());
            let sl = &bytes[s..e];
            if sl.is_empty() {
                continue;
            }
            ink[fi] = ((bits::ones(sl) * 255) / (sl.len() * 8)) as u8;
            if !seen.insert(bits::digest(sl)) {
                repeat[fi] = true;
            }
        }
        let repeats = repeat.iter().filter(|&&b| b).count();
        Some(Shell {
            level,
            chi: v.chi,
            genus: v.genus.unwrap_or(-1),
            judged_us,
            ink,
            repeat,
            repeats,
            per_face: per,
            ico,
        })
    }
}

struct App {
    cv: Canvas,
    dib: Vec<u8>,
    label: String,
    bytes: Vec<u8>,
    shell: Shell,
    dup_pct: f64,
    entropy: f64,
    ones_pct: f64,
    pal: usize,
    yaw: f64,
    spin: bool,
    render_us: u128,
    seal: u64,
    status: String,
    buttons: Vec<(Rect, &'static str, u8)>,
    session: PathBuf,
    shots: usize,
    /// Radians of turn per frame.
    ///
    /// **This closes a real drift.** The window's timer added 0.012 and
    /// `advance()` added 0.01, so a scripted `spin n` did NOT reproduce what
    /// the window did -- the same motion with two different constants, which
    /// is the R3/R9 shape wearing a rate. One field, both callers, and it
    /// cannot drift from itself.
    speed: f64,
    /// Whether the HUD may paint the render time into the frame.
    ///
    /// R10: the seal is taken before the chrome so the SEAL reproduces, but a
    /// PNG written after the chrome contains `RENDER 683 US`, and 683 is a
    /// clock. Interactive keeps it -- a human watching wants the number live.
    /// `--run` drops it and reports the timing in DRIVE.log as a peer outside
    /// the image.
    paint_clock: bool,
}

thread_local! { static APP: RefCell<Option<App>> = const { RefCell::new(None) }; }

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
    // the driver lives HERE rather than in a shell wrapping the OS.
    //
    // The first non-flag argument stays what it always was: the file to
    // stream. Default is this executable, so by default the orb draws a
    // portrait of the build that produced it.
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mut i = 0;
    let mut script: Option<String> = None;
    let mut size: Option<String> = None;
    // FULL SCREEN IS THE DEFAULT -- but only for a WINDOW.
    //
    // `--max` still works and still means the same thing; it is now the
    // default rather than a request. `--windowed` is its opposite and exists
    // because removing the ability to get a small window would be a feature
    // deleted rather than a default changed.
    //
    // **A HEADLESS RUN KEEPS THE FIXED CANVAS.** `resolve_canvas` is called
    // before the script/window dispatch, so defaulting this to `true`
    // unconditionally would make every `--run` and `--script` render at
    // whatever monitor happens to be attached -- and those runs exist to
    // produce byte-identical PNGs on any machine. A receipt that changes with
    // the hardware is a screenshot again (R10).
    let mut explicit_max = false;
    let mut explicit_windowed = false;
    let mut target: Option<String> = None;

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
            "--max" => explicit_max = true,
            "--windowed" | "-w" => explicit_windowed = true,
            "--help" | "-h" => {
                println!("{HELP}");
                return;
            }
            other if other.starts_with('-') => {
                eprintln!(
                    "unknown flag '{other}'

{HELP}"
                );
                std::process::exit(2);
            }
            other => target = Some(other.to_string()),
        }
        i += 1;
    }

    // THE CANVAS IS FIXED HERE, before a window, a script or a buffer exists.
    let asked = size.clone();
    // an explicit flag always wins over the default, in both directions
    let want_max = if explicit_max {
        true
    } else if explicit_windowed {
        false
    } else {
        script.is_none()
    };

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
        Some(src) => std::process::exit(run_script(&src, target)),
        None => unsafe { run(target) },
    }
}

unsafe fn run(target: Option<String>) {
    let hinst = GetModuleHandleW(std::ptr::null());
    let class = wide("GosOrbClass");
    let title = wide("GOS ORB v0.2 - the byte topology, icosphere lane");
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
        return;
    }
    APP.with(|a| *a.borrow_mut() = Some(App::new(target)));
    // Ask the OS for the border metrics instead of guessing them, so the
    // client area is EXACTLY W x H and the byte topology is not resampled on
    // its way to the eye. See the viewer for the full note.
    let mut want = RECT {
        left: 0,
        top: 0,
        right: W() as LONG,
        bottom: H() as LONG,
    };
    AdjustWindowRect(&mut want, WS_OVERLAPPEDWINDOW, 0);

    let hwnd = CreateWindowExW(
        0,
        class.as_ptr(),
        title.as_ptr(),
        WS_OVERLAPPEDWINDOW | WS_VISIBLE,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        want.right - want.left,
        want.bottom - want.top,
        std::ptr::null_mut(),
        std::ptr::null_mut(),
        hinst,
        std::ptr::null_mut(),
    );
    if hwnd.is_null() {
        return;
    }
    let mut got = RECT {
        left: 0,
        top: 0,
        right: 0,
        bottom: 0,
    };
    GetClientRect(hwnd, &mut got);
    let (cw, ch) = (got.right - got.left, got.bottom - got.top);
    println!(
        "dpi     {}  client {cw} x {ch}  canvas {} x {}  exact {}",
        dpi_exact,
        W(),
        H(),
        dpi_exact && cw == W() as LONG && ch == H() as LONG
    );
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
    SetTimer(hwnd, TIMER_ID, TICK, 0);
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
        WM_TIMER => {
            let mut go = false;
            APP.with(|a| {
                if let Some(app) = a.borrow_mut().as_mut() {
                    if app.spin {
                        app.yaw = wrap_turn(app.yaw + app.speed);
                        go = true;
                    }
                }
            });
            if go {
                InvalidateRect(hwnd, std::ptr::null(), 0);
            }
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
        WM_KEYDOWN => {
            if wp == VK_ESCAPE {
                DestroyWindow(hwnd);
            }
            0
        }
        WM_CLOSE => {
            DestroyWindow(hwnd);
            0
        }
        WM_DESTROY => {
            KillTimer(hwnd, TIMER_ID);
            PostQuitMessage(0);
            0
        }
        _ => DefWindowProcW(hwnd, msg, wp, lp),
    }
}

impl App {
    fn new(target: Option<String>) -> App {
        let (label, bytes) = match target {
            Some(p) => {
                let b = fs::read(&p).unwrap_or_default();
                (p, b)
            }
            None => {
                let p = std::env::current_exe().unwrap_or_default();
                let b = fs::read(&p).unwrap_or_default();
                (
                    p.file_name()
                        .map(|s| s.to_string_lossy().to_string())
                        .unwrap_or_default(),
                    b,
                )
            }
        };

        // duplication over the WHOLE stream, exact, at BLOCK granularity
        let mut seen: HashSet<u64> = HashSet::new();
        let mut rep = 0usize;
        for c in bytes.chunks(BLOCK) {
            if !seen.insert(bits::digest(c)) {
                rep += 1;
            }
        }
        let blocks = bytes.len().div_ceil(BLOCK).max(1);

        // start where one face is close to one byte, capped
        let start = sphere::level_for_bytes(bytes.len()).min(MAX_LEVEL);
        let shell = Shell::build(start, &bytes)
            .or_else(|| Shell::build(3, &bytes))
            .expect("a shell must build");

        println!(
            "AXIOM 01 GATE  chi {} genus {}  JUDGE {} us",
            shell.chi, shell.genus, shell.judged_us
        );
        println!(
            "stream  {label} ({} bytes)  dup {rep}/{blocks} at {BLOCK}B",
            bytes.len()
        );
        println!(
            "start   L{}  {} faces  {} B/face",
            shell.level,
            shell.ico.faces.len(),
            shell.per_face
        );

        let session = open_session();
        println!("session {}", session.display());

        let pal = ALL[0];
        let mut app = App {
            cv: Canvas::new(W(), H(), pal.bg),
            dib: vec![0u8; W() * H() * 4],
            dup_pct: 100.0 * rep as f64 / blocks as f64,
            entropy: bits::entropy(&bytes),
            ones_pct: 100.0 * bits::ones(&bytes) as f64 / (bytes.len() * 8).max(1) as f64,
            label,
            bytes,
            shell,
            pal: 0,
            yaw: 0.6,
            spin: true,
            render_us: 0,
            seal: 0,
            status: String::from("LEVEL- / LEVEL+ WALKS THE SAME BYTES."),
            buttons: Vec::new(),
            session,
            shots: 0,
            speed: 0.012,
            paint_clock: true,
        };
        app.layout();
        app
    }

    fn pal(&self) -> Palette {
        ALL[self.pal]
    }

    fn layout(&mut self) {
        let y = H() as i32 - BAR_H + 6;
        let mut x = 10i32;
        self.buttons.clear();
        for (id, l) in [
            (0u8, "SHOT"),
            (1, "SPIN"),
            (2, "PALETTE"),
            (3, "LEVEL -"),
            (4, "LEVEL +"),
        ] {
            let w = font::width(l, 1) + 16;
            self.buttons.push((Rect::new(x, y, w, BAR_H - 12), l, id));
            x += w + 8;
        }
    }

    fn set_level(&mut self, d: i32) {
        let want = (self.shell.level as i32 + d).clamp(0, MAX_LEVEL as i32) as u32;
        if want == self.shell.level {
            self.status = format!(
                "AT THE {} LEVEL ALREADY",
                if d > 0 { "TOP" } else { "BOTTOM" }
            );
            return;
        }
        let t0 = Instant::now();
        match Shell::build(want, &self.bytes) {
            Some(s) => {
                self.status = format!(
                    "L{} - {} FACES - {} B/FACE - JUDGE {} US - BUILT IN {} MS",
                    s.level,
                    s.ico.faces.len(),
                    s.per_face,
                    s.judged_us,
                    t0.elapsed().as_millis()
                );
                self.shell = s;
                println!("{}", self.status);
            }
            None => self.status = format!("L{want} REFUSED - PAST THE BUDGET"),
        }
    }

    fn click(&mut self, mx: i32, my: i32) -> bool {
        let hit = self
            .buttons
            .iter()
            .find(|(r, _, _)| r.contains(mx, my))
            .map(|(_, _, i)| *i);
        match hit {
            Some(0) => {
                self.shot();
                true
            }
            Some(1) => {
                self.spin = !self.spin;
                true
            }
            Some(2) => {
                self.pal = (self.pal + 1) % ALL.len();
                true
            }
            Some(3) => {
                self.set_level(-1);
                true
            }
            Some(4) => {
                self.set_level(1);
                true
            }
            _ => false,
        }
    }

    fn render(&mut self) {
        let t0 = Instant::now();
        let pal = self.pal();
        self.cv.fill(pal.bg);
        self.paint_orb();
        self.render_us = t0.elapsed().as_micros();
        self.seal = self.cv.digest(); // R10: seal BEFORE the chrome
        self.paint_hud();
        self.paint_bar();
    }

    fn paint_orb(&mut self) {
        let pal = self.pal();
        let area = Rect::new(0, 0, W() as i32 - HUD_W, H() as i32 - BAR_H);
        let zoom = (area.w.min(area.h) as f64) * 0.42;
        let s = &self.shell;
        let pts: Vec<(i32, i32, f64)> = s
            .ico
            .verts
            .iter()
            .map(|&v| project(v, 0.32, self.yaw, zoom, area.w as usize, area.h as usize))
            .collect();

        let mut ord: Vec<(usize, f64)> = (0..s.ico.faces.len())
            .map(|i| {
                let f = &s.ico.faces[i];
                (i, (pts[f[0]].2 + pts[f[1]].2 + pts[f[2]].2) / 3.0)
            })
            .collect();
        ord.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());

        for (fi, d) in ord {
            if d < 0.0 {
                continue;
            }
            let f = &s.ico.faces[fi];
            let (a, b, c) = (pts[f[0]], pts[f[1]], pts[f[2]]);
            let t = ((d + 1.0) / 2.0).clamp(0.0, 1.0);
            let al = ((0.25 + t * 0.70) * 255.0) as u8;
            let col = if s.repeat[fi] {
                pal.orange
            } else {
                ramp(&pal, s.ink[fi])
            };
            let span = (a.0 - b.0)
                .abs()
                .max((a.1 - b.1).abs())
                .max((a.0 - c.0).abs());
            if span <= 2 {
                self.cv.blend(a.0, a.1, col, al);
            } else {
                fill_tri(&mut self.cv, (a.0, a.1), (b.0, b.1), (c.0, c.1), col, al);
            }
        }
        for &dv in &s.ico.defects() {
            let p = pts[dv];
            if p.2 > 0.0 {
                self.cv.disc(p.0, p.1, 3, pal.pink, 255);
            }
        }
    }

    fn paint_hud(&mut self) {
        let pal = self.pal();
        let x = W() as i32 - HUD_W + 12;
        let mut y = 14;
        let s = &self.shell;
        font::text(&mut self.cv, x, y, "GOS ORB", pal.gold, 2);
        y += 24;
        let rows: Vec<(String, Rgb)> = vec![
            (format!("STREAM {}", trunc(&self.label, 22)), pal.cyan),
            (format!("BYTES  {}", self.bytes.len()), pal.text),
            (String::new(), pal.text),
            (format!("-- LEVEL {} --", s.level), pal.gold),
            (format!("FACES  {}", s.ico.faces.len()), pal.cyan),
            (format!("V      {}", s.ico.verts.len()), pal.text),
            (format!("B/FACE {}", s.per_face), pal.cyan),
            (String::new(), pal.text),
            (format!("CHI    {}  JUDGE", s.chi), pal.green),
            (format!("GENUS  {}", s.genus), pal.green),
            (format!("JUDGED {} US", s.judged_us), pal.purple),
            (String::from("DEFECTS 12  EULER"), pal.pink),
            (String::new(), pal.text),
            (String::from("-- DUPLICATION --"), pal.gold),
            (format!("THIS LEVEL {}", s.repeats), pal.orange),
            (
                format!(
                    "= {:.2} PCT OF FACES",
                    100.0 * s.repeats as f64 / s.ico.faces.len() as f64
                ),
                pal.orange,
            ),
            (format!("WHOLE STREAM {:.2} PCT", self.dup_pct), pal.text),
            (format!("AT {} B BLOCKS", BLOCK), [0x4a, 0x5a, 0x6a]),
            (String::new(), pal.text),
            (format!("ENTROPY {:.4} B/B", self.entropy), pal.text),
            (format!("ONES    {:.2} PCT", self.ones_pct), pal.text),
            (String::new(), pal.text),
            // the clock only when a human is watching (R10)
            (
                if self.paint_clock {
                    format!("RENDER {} US", self.render_us)
                } else {
                    String::new()
                },
                pal.purple,
            ),
            (format!("SEAL {:016X}", self.seal), pal.purple),
        ];
        for (t, c) in rows {
            if !t.is_empty() {
                font::text(&mut self.cv, x, y, &t, c, 1);
            }
            y += 11;
        }
        y += 8;
        for l in [
            "DUP DEPENDS ON BLOCK SIZE.",
            "THE TWO NUMBERS ABOVE MEASURE",
            "DIFFERENT THINGS AND BOTH ARE",
            "HONEST.",
        ] {
            font::text(&mut self.cv, x, y, l, pal.border, 1);
            y += 10;
        }
    }

    fn paint_bar(&mut self) {
        let pal = self.pal();
        self.cv
            .fill_rect(0, H() as i32 - BAR_H, W() as i32, BAR_H, pal.panel);
        self.cv.line(
            0,
            H() as i32 - BAR_H,
            W() as i32 - 1,
            H() as i32 - BAR_H,
            pal.border,
        );
        font::text(
            &mut self.cv,
            10,
            H() as i32 - BAR_H - 14,
            &self.status,
            pal.text,
            1,
        );
        for (r, l, id) in self.buttons.clone() {
            let a = match id {
                0 => pal.gold,
                1 => pal.pink,
                3 | 4 => pal.green,
                _ => pal.cyan,
            };
            self.cv.rect(r.x, r.y, r.w, r.h, a);
            font::text(&mut self.cv, r.x + 8, r.y + (r.h - font::GH) / 2, l, a, 1);
        }
    }

    fn shot(&mut self) {
        self.shots += 1;
        let f = self.session.join(format!("orb_{:04}.png", self.shots));
        if self.cv.write_png(&f).is_ok() {
            self.status = format!(
                "SHOT {:04} - L{} - SEAL {:016X}",
                self.shots, self.shell.level, self.seal
            );
            let line = format!(
                "orb_{:04}.png  level={}  faces={}  yaw={:.4}  palette={}  seal={:016x}\n",
                self.shots,
                self.shell.level,
                self.shell.ico.faces.len(),
                self.yaw,
                self.pal().name,
                self.seal
            );
            append(&self.session.join("SHOTS.log"), &line);
            println!("{}", self.status);
        }
    }

    /// Advance the turn by exactly `frames` ticks.
    ///
    /// Replaces `sleep`. A driver that waits on the wall clock renders a
    /// different picture every run, and a picture that will not reproduce is a
    /// screenshot rather than a receipt (R10 / Curse 38).
    fn advance(&mut self, frames: u32) {
        for _ in 0..frames {
            if self.spin {
                self.yaw = wrap_turn(self.yaw + self.speed);
            }
        }
    }

    /// Set the level absolutely, rather than by delta.
    fn goto_level(&mut self, want: u32) {
        let d = want as i32 - self.shell.level as i32;
        if d != 0 {
            self.set_level(d);
        }
    }

    /// Write the current canvas to a named PNG, from the FRAMEBUFFER.
    fn shot_named(&mut self, dir: &std::path::Path, name: &str) -> String {
        self.render();
        let f = dir.join(format!("{name}.png"));
        match self.cv.write_png(&f) {
            Ok(()) => format!(
                "shot   {name:<22} L{} {:>9} faces  {:>4} B/face  chi {}  seal {:016x}",
                self.shell.level,
                self.shell.ico.faces.len(),
                self.shell.per_face,
                self.shell.chi,
                self.seal
            ),
            Err(e) => format!("shot   {name:<22} FAILED: {e}"),
        }
    }

    /// Click the centre of a named button, through the real hit-test path.
    fn click_button(&mut self, label: &str) -> Result<String, String> {
        let b = self
            .buttons
            .iter()
            .find(|(_, l, _)| l.eq_ignore_ascii_case(label))
            .map(|(r, l, _)| (*r, *l))
            .ok_or_else(|| {
                let have: Vec<&str> = self.buttons.iter().map(|(_, l, _)| *l).collect();
                format!("no button '{label}'. have: {}", have.join(", "))
            })?;
        let (r, l) = b;
        self.click(r.x + r.w / 2, r.y + r.h / 2);
        Ok(format!("button {l:<22} at {},{}", r.x, r.y))
    }
}

/// One named, bounded, numeric control of the orb.
///
/// Same table, same reasons as the viewer's: a row here is a command-line
/// verb and a `movie` channel at once, so the next control is animatable the
/// day it lands. The orb's fractal space has fewer knobs than the mesh, and
/// that is exactly why a table beats three copies of the same wiring -- the
/// cost of the table is paid once and the third control is free.
struct Control {
    name: &'static str,
    lo: f64,
    hi: f64,
    unit: &'static str,
}

const CONTROLS: [Control; 3] = [
    Control {
        name: "yaw",
        lo: 0.0,
        hi: std::f64::consts::TAU,
        unit: "turn, radians",
    },
    Control {
        name: "level",
        lo: 0.0,
        hi: MAX_LEVEL as f64,
        unit: "subdivision depth -- 4^n faces, and a REBUILD each step",
    },
    Control {
        name: "speed",
        lo: 0.0,
        hi: 0.25,
        unit: "turn per frame, radians -- 0 holds it still",
    },
];

/// Why a typed value was refused. The monkey brain will type a shoe.
#[derive(Clone, Debug, PartialEq)]
enum BadValue {
    NotANumber(String),
    NotFinite(String),
    OutOfRange { got: f64, lo: f64, hi: f64 },
}

impl std::fmt::Display for BadValue {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            BadValue::NotANumber(s) => write!(f, "'{s}' IS NOT A NUMBER"),
            BadValue::NotFinite(s) => write!(f, "'{s}' IS NOT FINITE - NAN AND INF ARE REFUSED"),
            BadValue::OutOfRange { got, lo, hi } => write!(f, "{got} IS OUTSIDE {lo}..{hi}"),
        }
    }
}

/// Parse a human's typing. `"nan".parse::<f64>()` SUCCEEDS, which is why the
/// finite test is a separate fence and not folded into the parse.
/// Wrap an angle into `[0, TAU)`.
///
/// **RUSTIUM R20 -- The Unwrapped Turn.** `yaw` declares `lo: 0.0, hi: TAU` in
/// [`CONTROLS`] and `ctl_set` clamps to it -- but the SPIN advanced it with a
/// bare `+=` in two places, the window timer and `advance()`, so the value
/// walked out of the range its own table advertises and never came back.
///
/// Found in the viewer first, reported as *"yaw, pitch and roll are acting as
/// a counter, they don't go back"*. The orb had the identical curse and was
/// missed, because the fix was applied to the FILE the bug was seen in rather
/// than swept across the workspace. One binary fixed, one still counting, and
/// both launched by the same command.
///
/// `rem_euclid`, never `%`: the remainder operator keeps the sign of the
/// DIVIDEND, so a negative speed would drive the angle below `lo` instead of
/// above `hi` -- the same curse at the other end, and a `%` fix would look
/// correct while leaving half the bug in place.
///
/// The second cost is the one that waits: `sin` and `cos` reduce their
/// argument modulo TAU using whatever precision is left after the integer
/// part, so a long enough spin does not merely READ wrong, it stops turning
/// smoothly. Nothing warns; the motion just coarsens.
fn wrap_turn(a: f64) -> f64 {
    if a.is_finite() {
        a.rem_euclid(std::f64::consts::TAU)
    } else {
        0.0
    }
}

/// THE CONTROL CONTRACT, given to the orb.
impl App {
    /// Find a control by name, case-insensitively.
    fn ctl_index(name: &str) -> Option<usize> {
        CONTROLS
            .iter()
            .position(|c| c.name.eq_ignore_ascii_case(name))
    }

    /// Read a control by index. One arm per row of [`CONTROLS`].
    ///
    /// NOT a plausible catch-all. R18: a `_ =>` in a getter does not fail, it
    /// answers with a believable number from the wrong field, which is
    /// strictly worse than a panic because nothing about it looks broken.
    /// `NaN` cannot round-trip, so the contract test fails instantly.
    fn ctl_get(&self, i: usize) -> f64 {
        match CONTROLS[i].name {
            "yaw" => self.yaw,
            "speed" => self.speed,
            "level" => self.shell.level as f64,
            _ => f64::NAN,
        }
    }

    /// Write a control by index, clamped to its own declared range.
    ///
    /// Clamping is right HERE because the value has already been validated by
    /// [`parse_control`] or produced by a movie's interpolation; this is the
    /// last line of defence, not the first.
    fn ctl_set(&mut self, i: usize, v: f64) {
        let c = &CONTROLS[i];
        let v = v.clamp(c.lo, c.hi);
        match c.name {
            "yaw" => self.yaw = v,
            "speed" => self.speed = v,
            "level" => self.goto_level(v.round().clamp(0.0, MAX_LEVEL as f64) as u32),
            // named explicitly for the same reason the getter is -- a silent
            // catch-all writes the wrong field just as happily as it reads one
            _ => debug_assert!(false, "no ctl_set arm for '{}'", c.name),
        }
    }
}

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

/// Where a movie's frames end up.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum Emit {
    Png,
    Mp4,
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

/// Past this a movie is refused, with the number.
const RENDER_SECONDS_BUDGET: f64 = 20.0 * 60.0;

/// Where `ffmpeg` might be. Probed by RUNNING it -- an installer's exit code
/// certifies the download, never the capability (R2).
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

fn hms(s: f64) -> String {
    let t = s.max(0.0) as u64;
    if t < 60 {
        format!("{s:.1}s")
    } else if t < 3600 {
        format!("{}m {:02}s", t / 60, t % 60)
    } else {
        format!("{}h {:02}m", t / 3600, (t % 3600) / 60)
    }
}

/// One movie over any registered orb control.
///
/// **`level` is the interesting one.** Sweeping it does not merely move a
/// camera: each step REBUILDS the shell and re-judges it, so the film is the
/// fractal space growing, with chi counted at every frame rather than assumed.
/// That is the orb's whole subject, and it was previously only reachable by
/// clicking LEVEL+ seven times and watching.
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

    // price it in both currencies, from ONE measured frame
    let t0 = Instant::now();
    app.render();
    let one = t0.elapsed().as_secs_f64();
    let render_s = one * frames as f64;
    let png_total = goldberg_kernel::raster::png_bytes(W(), H()) as u64 * frames as u64;

    println!("movie  {name}  [{}]", CONTROLS[ctl].name);
    println!(
        "  {frames} frames @ {fps} fps = {} of footage",
        hms(frames as f64 / fps.max(1) as f64)
    );
    println!("  render ~{} (one frame measured)", hms(render_s));
    println!(
        "  disk {}",
        if emit.writes_png() {
            format!("{:.2} GB of PNG, exact", png_total as f64 / 1_073_741_824.0)
        } else {
            String::from("0 bytes -- frames are piped, never written")
        }
    );
    if render_s > RENDER_SECONDS_BUDGET {
        return Err(format!(
            "REFUSED - this would render for {}, past the {} ceiling. One frame at L{} \
             ({} faces) took {:.0} ms, and that is measured, not guessed.",
            hms(render_s),
            hms(RENDER_SECONDS_BUDGET),
            app.shell.level,
            app.shell.ico.faces.len(),
            1000.0 * one
        ));
    }

    let out = dir.join(format!("movie_{name}"));
    fs::create_dir_all(&out).map_err(|e| format!("cannot create {}: {e}", out.display()))?;
    let mp4 = out.join(format!("{name}.mp4"));

    let mut child = if emit.writes_mp4() {
        let ff = find_ffmpeg().ok_or_else(|| {
            String::from("ffmpeg NOT FOUND. `winget install Gyan.FFmpeg`, or render with `png`.")
        })?;
        Some(
            std::process::Command::new(&ff)
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
                .map_err(|e| format!("could not start {}: {e}", ff.display()))?,
        )
    } else {
        None
    };

    let mut rows: Vec<String> = Vec::new();
    let mut png_written = 0u64;
    let t1 = Instant::now();

    for f in 0..frames {
        let t = if frames == 1 {
            0.0
        } else {
            f as f64 / (frames - 1) as f64
        };
        let v = lo + t * (hi - lo);
        app.ctl_set(ctl, v);
        app.render();

        if let Some(c) = child.as_mut() {
            use std::io::Write as _;
            let pipe = c.stdin.as_mut().ok_or("the encoder closed its stdin")?;
            pipe.write_all(&app.cv.px)
                .map_err(|e| format!("frame {f}: the encoder stopped reading: {e}"))?;
        }
        if emit.writes_png() {
            app.cv
                .write_png(out.join(format!("frame_{f:05}.png")))
                .map_err(|e| format!("frame {f}: {e}"))?;
            png_written += goldberg_kernel::raster::png_bytes(W(), H()) as u64;
        }

        let st = goldberg_kernel::oklab::FrameStats::measure(&app.cv.px, 37);
        rows.push(format!(
            "  {{ \"frame\": {f}, \"t\": {t:.6}, \"{}\": {v:.6}, \"level\": {}, \"faces\": {}, \
             \"chi\": {}, \"genus\": {}, \"seal\": \"{:016x}\", \"colours\": {}, \"ink\": {:.6}, \
             \"mean_l\": {:.6}, \"l_entropy\": {:.6} }}",
            CONTROLS[ctl].name,
            app.shell.level,
            app.shell.ico.faces.len(),
            app.shell.chi,
            app.shell.genus,
            app.seal,
            st.distinct,
            st.ink,
            st.mean_l,
            st.l_entropy
        ));
    }

    let mut mp4_bytes = 0u64;
    if let Some(mut c) = child {
        drop(c.stdin.take());
        let status = c.wait().map_err(|e| format!("waiting on ffmpeg: {e}"))?;
        if !status.success() {
            return Err(format!("ffmpeg refused (exit {:?})", status.code()));
        }
        mp4_bytes = fs::metadata(&mp4).map(|m| m.len()).unwrap_or(0);
    }
    let secs = t1.elapsed().as_secs_f64();

    let _ = fs::write(
        out.join("MAKE_MP4.txt"),
        format!(
            "ffmpeg -y -framerate {fps} -i \"{}\" -c:v libx264 -preset slow -crf {crf} \
             -pix_fmt yuv420p -movflags +faststart \"{}\"\n",
            out.join("frame_%05d.png").display(),
            mp4.display()
        ),
    );

    let mut m: Vec<String> = Vec::new();
    m.push(String::from("{"));
    m.push(format!(
        "  \"name\": \"{name}\", \"control\": \"{}\",",
        CONTROLS[ctl].name
    ));
    m.push(format!("  \"from\": {lo:.6}, \"to\": {hi:.6},"));
    m.push(format!(
        "  \"frames\": {frames}, \"fps\": {fps}, \"crf\": {crf},"
    ));
    m.push(format!(
        "  \"emit\": \"{emit:?}\", \"canvas\": [{}, {}],",
        W(),
        H()
    ));
    m.push(format!(
        "  \"stream\": \"{}\", \"stream_bytes\": {},",
        app.label,
        app.bytes.len()
    ));
    m.push(format!(
        "  \"png_bytes\": {png_written}, \"mp4_bytes\": {mp4_bytes},"
    ));
    m.push(format!("  \"render_seconds\": {secs:.3},"));
    m.push(String::from("  \"oklab_sample_stride\": 37,"));
    m.push(String::from("  \"frames_detail\": ["));
    m.push(rows.join(",\n"));
    m.push(String::from("  ]"));
    m.push(String::from("}"));
    let _ = fs::write(out.join("MOVIE.json"), m.join("\n") + "\n");

    Ok(format!(
        "movie  {name:<18} {frames}f @ {fps} = {} footage  |  {}  |  {secs:.1}s at {:.1} fps",
        hms(frames as f64 / fps.max(1) as f64),
        if mp4_bytes > 0 {
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
        },
        frames as f64 / secs.max(1e-9)
    ))
}

/// Run a script against a headless orb. Returns the number of failures.
///
/// **Why the orb needs this most.** The orb streams a file's bytes onto a
/// certified shell -- and by default that file is *its own executable*. So
/// every build changes the picture, and the picture is a portrait of the code
/// we just wrote. Driving it from a script means each build can end with a
/// render of what the build actually produced, beside the numbers.
///
/// ```text
///   shot <name>       render and write <name>.png FROM THE FRAMEBUFFER
///   level <n|+|->     absolute level, or one step
///   sweep <a>-<b>     shot every level from a to b -- the growth, in order
///   spin <n>          advance the turn n frames -- deterministic, not a sleep
///   palette           cycle the palette
///   button <LABEL>    click a button by name
///   expect <k>=<v>    level | faces | chi | genus, or FAIL
///   status            print the status line
/// ```
fn run_script(src: &str, target: Option<String>) -> i32 {
    let mut app = App::new(target);

    // No clock in the frame: the timing is reported in DRIVE.log as a peer
    // outside the image, so two runs of one script give identical PNGs (R10).
    app.paint_clock = false;

    let dir = app.session.join("drive");
    if let Err(e) = fs::create_dir_all(&dir) {
        eprintln!("cannot create {}: {e}", dir.display());
        return 1;
    }
    app.render();

    let mut log: Vec<String> = Vec::new();
    let mut failures = 0i32;

    // THE TOPOLOGY LEDGER ROW. What this build's bytes look like as a shell,
    // recorded before any picture, so a diff across commits is a diff of the
    // code's own shape rather than of a render.
    let head = format!(
        "stream  {}  {} bytes  dup {:.2}%  entropy {:.4} B/B  ones {:.2}%",
        app.label,
        app.bytes.len(),
        app.dup_pct,
        app.entropy,
        app.ones_pct
    );
    println!(
        "canvas  {} x {}   headless, no window, no compositor",
        W(),
        H()
    );
    println!("{head}");
    println!("session {}", app.session.display());
    println!();
    log.push(head);
    log.push(String::new());

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
                let name = if arg.is_empty() { "orb" } else { arg };
                app.shot_named(&dir, name)
            }
            "level" => match arg {
                "+" => {
                    app.set_level(1);
                    format!("level  +{:<21} -> L{}", "", app.shell.level)
                }
                "-" => {
                    app.set_level(-1);
                    format!("level  -{:<21} -> L{}", "", app.shell.level)
                }
                n => match n.trim_start_matches('L').parse::<u32>() {
                    Ok(v) => {
                        app.goto_level(v);
                        format!(
                            "level  {n:<22} -> L{} {} faces {} B/face",
                            app.shell.level,
                            app.shell.ico.faces.len(),
                            app.shell.per_face
                        )
                    }
                    Err(_) => {
                        failures += 1;
                        format!("FAIL   level wants a number, '+' or '-', got '{n}'")
                    }
                },
            },
            // the growth of the shell, one shot per rung, in order
            "sweep" => match arg.split_once('-') {
                Some((a, b)) => match (a.trim().parse::<u32>(), b.trim().parse::<u32>()) {
                    (Ok(lo), Ok(hi)) if lo <= hi => {
                        let mut rows = Vec::new();
                        for l in lo..=hi {
                            app.goto_level(l);
                            if app.shell.level != l {
                                rows.push(format!("sweep  L{l} REFUSED - past the budget"));
                                break;
                            }
                            rows.push(app.shot_named(&dir, &format!("L{l}")));
                        }
                        rows.join("\n")
                    }
                    _ => {
                        failures += 1;
                        format!("FAIL   sweep wants lo-hi, got '{arg}'")
                    }
                },
                None => {
                    failures += 1;
                    format!("FAIL   sweep wants lo-hi, got '{arg}'")
                }
            },
            "spin" => {
                let n: u32 = arg.parse().unwrap_or(1);
                app.advance(n);
                format!("spin   {n:<22} yaw {:.4} rad", app.yaw)
            }
            "palette" => {
                app.pal = (app.pal + 1) % ALL.len();
                format!("palette{:<23} {}", "", app.pal().name)
            }
            "button" => match app.click_button(arg) {
                Ok(s) => s,
                Err(e) => {
                    failures += 1;
                    format!("FAIL   {e}")
                }
            },
            "expect" => {
                let (k, want) = arg.split_once('=').unwrap_or((arg, ""));
                let got = match k.trim() {
                    "level" => app.shell.level.to_string(),
                    "faces" => app.shell.ico.faces.len().to_string(),
                    "chi" => app.shell.chi.to_string(),
                    "genus" => app.shell.genus.to_string(),
                    other => {
                        failures += 1;
                        log.push(format!("FAIL   unknown field '{other}'"));
                        continue;
                    }
                };
                if got == want.trim() {
                    format!("expect {arg:<22} OK")
                } else {
                    failures += 1;
                    format!("FAIL   {k} is {got}, expected {}", want.trim())
                }
            }
            "controls" => {
                let mut out = vec![String::from("controls")];
                for (i, c) in CONTROLS.iter().enumerate() {
                    let v = app.ctl_get(i);
                    out.push(format!(
                        "  {:<7} {:>10.4}   {}..{}   {}",
                        c.name, v, c.lo, c.hi, c.unit
                    ));
                }
                out.join("\n")
            }
            // ANY registered control, by its own name.
            //
            // This was a hardcoded `"yaw"` arm, and adding `speed` to the
            // table did NOT give it a verb -- the control showed up in
            // `controls` and could not be set. That is a card that looks
            // clickable and is not, one layer down. A table only pays for
            // itself if the lookup goes THROUGH it, so it now does.
            v if App::ctl_index(v).is_some() => {
                let i = App::ctl_index(v).expect("the guard on this arm just found it");
                let c = &CONTROLS[i];
                match parse_control(c, arg) {
                    Ok(x) => {
                        app.ctl_set(i, x);
                        format!("{:<7}{x:.4}   ({})", c.name, c.unit)
                    }
                    Err(e) => {
                        failures += 1;
                        format!(
                            "FAIL   {} REFUSED: {e}. WANTED {} ({}..{})",
                            c.name.to_uppercase(),
                            c.unit,
                            c.lo,
                            c.hi
                        )
                    }
                }
            }
            "movie" => {
                let a: Vec<&str> = arg.split_whitespace().collect();
                let parsed = (|| -> Result<_, String> {
                    if a.len() < 5 {
                        return Err(String::from(
                            "usage: movie <control> <lo> <hi> <frames> <name> [png|mp4|both] [fps] [crf]",
                        ));
                    }
                    let ctl = CONTROLS
                        .iter()
                        .position(|c| c.name.eq_ignore_ascii_case(a[0]))
                        .ok_or_else(|| {
                            let n: Vec<&str> = CONTROLS.iter().map(|c| c.name).collect();
                            format!("no control {:?}. have: {}", a[0], n.join(", "))
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
                    let emit = match a.get(5) {
                        Some(m) => {
                            Emit::parse(m).ok_or_else(|| format!("{m:?} is not png|mp4|both"))?
                        }
                        None => Emit::Mp4,
                    };
                    let fps: u32 = a.get(6).and_then(|v| v.parse().ok()).unwrap_or(60);
                    let crf: u32 = a.get(7).and_then(|v| v.parse().ok()).unwrap_or(18);
                    Ok((ctl, lo, hi, n, a[4], emit, fps, crf))
                })();
                match parsed {
                    Ok((ctl, lo, hi, n, name, emit, fps, crf)) => {
                        match run_movie(&mut app, &dir, ctl, lo, hi, n, fps, crf, emit, name) {
                            Ok(m) => m,
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

    log.push(String::new());
    log.push(format!("canvas          {}x{}", W(), H()));
    log.push(format!(
        "final           L{} {} faces chi {} genus {}",
        app.shell.level,
        app.shell.ico.faces.len(),
        app.shell.chi,
        app.shell.genus
    ));
    log.push(format!("failures        {failures}"));
    let _ = fs::write(dir.join("DRIVE.log"), log.join("\n") + "\n");

    println!();
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

const HELP: &str = "\
GOS ORB v0.2 -- the byte topology, icosphere lane.

  gos_orb                      open the window FULL SCREEN, streaming its own
                               machine code
  gos_orb --windowed           open it at 1920x1080 instead
  gos_orb <file>               stream that file instead
  gos_orb --run \"<steps>\"      run steps headless, write PNGs, exit
  gos_orb --script <file>      the same, from a file
  gos_orb --size 3840x2160     any canvas, no recompile
  gos_orb --max                fill the screen -- the default for a WINDOW, and
                               the way to ask for it in a HEADLESS run, which
                               otherwise stays at 1920x1080 so its PNGs do not
                               depend on the monitor

STEPS -- ';' or newline separated, '#' comments

  shot <name>      render and write <name>.png FROM THE FRAMEBUFFER
  level <n|+|->    absolute level, or one step
  sweep <a>-<b>    shot every level a..b -- the growth of the shell, in order
  spin <n>         advance the turn n frames -- deterministic, not a sleep
  palette          cycle the palette
  button <LABEL>   click a button by name
  expect <k>=<v>   level | faces | chi | genus, or FAIL
  controls         what exists, its value, its range, its units
  yaw <v>          set the turn, validated
  stats            what the frame is made of, in OKLab
  status           print the status line

MOVIES -- priced in BOTH currencies before the first frame

  movie <control> <lo> <hi> <frames> <name> [png|mp4|both] [fps] [crf]

  `movie level 0 6 240 grow mp4` films the fractal space GROWING: each step
  rebuilds the shell and re-judges it, so chi is counted at every frame rather
  than assumed. With mp4 the frames are piped to the encoder and NOTHING but
  the finished file touches the disk.

Exit code is the number of failures.

  gos_orb --run \"sweep 0-6; expect chi=2\"
";

impl App {
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
                biHeight: -(H() as i32),
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
}

fn ramp(pal: &Palette, t: u8) -> Rgb {
    let t = t as u32;
    let (a, b) = (pal.panel, pal.cyan);
    [
        ((a[0] as u32 * (255 - t) + b[0] as u32 * t) / 255) as u8,
        ((a[1] as u32 * (255 - t) + b[1] as u32 * t) / 255) as u8,
        ((a[2] as u32 * (255 - t) + b[2] as u32 * t) / 255) as u8,
    ]
}

fn fill_tri(cv: &mut Canvas, a: (i32, i32), b: (i32, i32), c: (i32, i32), col: Rgb, al: u8) {
    let p = [a, b, c];
    let lo = p.iter().map(|q| q.1).min().unwrap();
    let hi = p.iter().map(|q| q.1).max().unwrap();
    for y in lo..=hi {
        let mut xs: Vec<i32> = Vec::with_capacity(4);
        for i in 0..3 {
            let (x0, y0) = p[i];
            let (x1, y1) = p[(i + 1) % 3];
            if (y0 <= y && y1 > y) || (y1 <= y && y0 > y) {
                let dy = y1 - y0;
                if dy != 0 {
                    xs.push(x0 + (y - y0) * (x1 - x0) / dy);
                }
            }
        }
        xs.sort_unstable();
        for pr in xs.chunks(2) {
            if let [xa, xb] = pr {
                for x in *xa..=*xb {
                    cv.blend(x, y, col, al);
                }
            }
        }
    }
}

fn trunc(s: &str, n: usize) -> String {
    if s.chars().count() <= n {
        s.to_string()
    } else {
        s.chars()
            .rev()
            .take(n)
            .collect::<Vec<_>>()
            .into_iter()
            .rev()
            .collect()
    }
}

fn append(p: &std::path::Path, s: &str) {
    use std::io::Write as _;
    if let Ok(mut f) = fs::OpenOptions::new().create(true).append(true).open(p) {
        let _ = f.write_all(s.as_bytes());
    }
}

fn open_session() -> PathBuf {
    // RUSTIUM R19 -- The Per-Run Ledger. A run folder per `App` is correct
    // for a run and automatic under `cargo test`, where one test binary
    // builds several. The viewer's `runs/` reached 579 directories that way
    // before the guard went in; the orb mints from the same shape and would
    // do it again the moment this file grew its first test -- which is the
    // commit that added this line.
    if cfg!(test) {
        let d = std::env::temp_dir().join("gos_orb_test_runs");
        let _ = fs::create_dir_all(&d);
        return d;
    }
    let base = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .map(|p| p.join("runs"))
        .unwrap_or_default();
    let _ = fs::create_dir_all(&base);
    let pre = format!("orb_v{}_s", env!("CARGO_PKG_VERSION").replace('.', "_"));
    let n = fs::read_dir(&base)
        .map(|rd| {
            rd.filter_map(|e| e.ok())
                .filter_map(|e| {
                    e.file_name()
                        .to_string_lossy()
                        .strip_prefix(&pre)
                        .and_then(|s| s.parse::<usize>().ok())
                })
                .max()
                .unwrap_or(0)
        })
        .unwrap_or(0)
        + 1;
    let d = base.join(format!("{pre}{n:04}"));
    let _ = fs::create_dir_all(&d);
    d
}

/// THE CONTROL CONTRACT -- one test per column.
///
/// A `Control` row makes four promises. Before this module the orb enforced
/// none of them, and it shipped the R20 counter in plain sight for weeks.
///
/// ```text
///   the row says    the promise                    the test
///   name            it can be found                every_control_is_reachable_by_name
///   the field       write then read agree          controls_round_trip
///   lo, hi          the value stays inside them    no_control_escapes_its_declared_range
/// ```
///
/// A declaration is a claim, and a claim without a test is a comment.
#[cfg(test)]
mod tests {
    use super::*;

    /// `None` reads the test binary as its own payload, which is a real file
    /// of real bytes and exactly what the orb is for.
    fn app() -> App {
        App::new(None)
    }

    #[test]
    fn every_control_is_reachable_by_name() {
        for c in CONTROLS.iter() {
            assert!(
                App::ctl_index(c.name).is_some(),
                "control '{}' is in the table but cannot be looked up by name",
                c.name
            );
        }
    }

    #[test]
    fn controls_round_trip() {
        let mut a = app();
        for (i, c) in CONTROLS.iter().enumerate() {
            // 0.37 of the way up, so a control that ignores its argument and
            // parks on a default or an endpoint is caught rather than matched
            let mut want = c.lo + (c.hi - c.lo) * 0.37;
            if c.name == "level" {
                want = want.round();
            }
            a.ctl_set(i, want);
            let got = a.ctl_get(i);
            assert!(
                (got - want).abs() < 1e-9,
                "control '{}' wrote {want} and read back {got} \
                 -- the setter and the getter are not talking about the same field",
                c.name
            );
        }
    }

    /// R20. This is the test the counter earned.
    #[test]
    fn no_control_escapes_its_declared_range() {
        let mut a = app();
        a.spin = true;

        // Drive the speed THROUGH the API at the top of its declared range.
        // The viewer's first version of this test wrote a raw value straight
        // into the speed field and broke the very contract it exists to check;
        // a test that reaches around the API is testing something else.
        let sp = App::ctl_index("speed").expect("speed is in the table");
        a.ctl_set(sp, CONTROLS[sp].hi);

        a.advance(200);

        for (i, c) in CONTROLS.iter().enumerate() {
            let v = a.ctl_get(i);
            assert!(
                v >= c.lo && v <= c.hi,
                "control '{}' left its range after spinning: {v} is not in [{}, {}]",
                c.name,
                c.lo,
                c.hi
            );
        }
    }

    /// The wrap itself, at the two ends that differ.
    #[test]
    fn wrap_turn_is_euclidean() {
        let tau = std::f64::consts::TAU;
        assert!((wrap_turn(0.5) - 0.5).abs() < 1e-12);
        assert!(wrap_turn(tau) < 1e-12);
        assert!((wrap_turn(tau + 0.25) - 0.25).abs() < 1e-12);
        // the half a `%` fix would have left behind: a NEGATIVE angle must
        // come back at the TOP of the range, not below the bottom of it
        let below = wrap_turn(-0.25);
        assert!(
            below > 0.0 && below < tau,
            "a negative turn wrapped to {below}, which is outside [0, TAU)"
        );
        assert!((below - (tau - 0.25)).abs() < 1e-12);
        // and nothing infinite may escape into sin/cos
        assert_eq!(wrap_turn(f64::NAN), 0.0);
        assert_eq!(wrap_turn(f64::INFINITY), 0.0);
    }
}
