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
use goldberg_kernel::{certify, judge, Mesh};

use gos_win32::*;

const W: usize = 900;
const H: usize = 700;
const BAR_H: i32 = 34;

/// Cap on any single exported dump. The HELENA doctrine: heavy payload stays
/// local, git keeps the manifest. A cap that is stated is engineering; a dump
/// that silently stops is a lie (Path IV).
const DUMP_CAP: usize = 4 * 1024 * 1024;

/// WM_TIMER id for the GENESIS turn.
const GENESIS_TIMER: usize = 1;

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
    /// where each painted card leads, built in the SAME loop that builds the
    /// cards. Previously the click handler said `if i == 1` and the wiring
    /// lived in a magic index -- insert a card at the front and GENESIS would
    /// silently become something else. Same shape as R3 and R9: an index
    /// standing where an identity belongs.
    card_views: Vec<Option<View>>,
}

thread_local! {
    static APP: RefCell<Option<App>> = const { RefCell::new(None) };
}

fn main() {
    unsafe { run() }
}

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
    if RegisterClassW(&wc) == 0 {
        eprintln!("RegisterClassW failed");
        return;
    }

    APP.with(|a| *a.borrow_mut() = Some(App::new()));

    // client area must be W x H; ask for a bit more and let Windows fit it
    let hwnd = CreateWindowExW(
        0,
        class.as_ptr(),
        title.as_ptr(),
        WS_OVERLAPPEDWINDOW | WS_VISIBLE,
        CW_USEDEFAULT,
        CW_USEDEFAULT,
        W as i32 + 16,
        H as i32 + 39,
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
            if wp == 0x53 {
                // S -- hold the GENESIS turn still, or release it again.
                let mut go = false;
                APP.with(|a| {
                    if let Some(app) = a.borrow_mut().as_mut() {
                        if app.view() == View::Genesis {
                            app.genesis_spin = !app.genesis_spin;
                            app.status = if app.genesis_spin {
                                String::from("GENESIS SPINNING.")
                            } else {
                                String::from("GENESIS HELD STILL.")
                            };
                            go = true;
                        }
                    }
                });
                if go {
                    InvalidateRect(hwnd, std::ptr::null(), 0);
                }
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
        };
        app.layout();
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
    fn paint_genesis(&mut self) {
        let pal = self.pal();
        let (rx, zoom) = (0.30_f64, 250.0_f64);
        let ry = self.genesis_yaw;
        let sh = H as i32 - BAR_H - 60;
        let pts: Vec<(i32, i32, f64)> = self
            .mesh
            .verts
            .iter()
            .map(|&v| project(v, rx, ry, zoom, W, sh as usize))
            .collect();

        // painter's order: far edges first, so near ones land on top
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
            self.cv
                .line_a(pts[a].0, pts[a].1, pts[b].0, pts[b].1, c, a8);
        }
        for p in pts.iter() {
            let t = ((p.2 + 2.0) / 4.0).clamp(0.0, 1.0);
            let a8 = ((0.15 + t * 0.5) * 255.0) as u8;
            self.cv.disc(p.0, p.1, 2, pal.green, a8);
        }

        // the census, computed -- never typed into a string literal
        let g = genesis::Census::C60;
        let chi = genesis::certify(g).map_or("?".to_string(), |c| c.to_string());
        let (v, e) = genesis::implied(g).unwrap_or((0, 0));
        let lines = [
            format!("SEED   {g}"),
            format!("V={v}  E={e}  F={}", g.f),
            format!("chi={chi}   E/V={:.3}", e as f64 / v as f64),
            format!("yaw {:.2} rad", self.genesis_yaw % std::f64::consts::TAU),
            String::from("chi is COMPUTED from trivalence,"),
            String::from("never assumed from Euler (R-INV)."),
            String::new(),
            String::from("NOT YET: refine, sliders, mobius."),
            String::from("step 1 of 8 - GENESIS_PORT_SPEC.md"),
        ];
        for (i, l) in lines.iter().enumerate() {
            let c = if i >= 7 { pal.border } else { pal.text };
            font::text(&mut self.cv, 16, 60 + i as i32 * 14, l, c, 1);
        }
    }

    fn paint_shell(&mut self) {
        let pal = self.pal();
        let (rx, ry, zoom) = (0.30_f64, 0.55_f64, 250.0_f64);
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
            // the sealed content digest, NOT a fresh one -- R10
            let sub = format!(
                "V 60 E 90 F 32 CHI 2 P 12 - RENDER {} US - SEAL {:016X}",
                self.last_render_us, self.content_digest
            );
            font::text(&mut self.cv, 10, 30, &sub, pal.cyan, 1);

            let sy = H as i32 - BAR_H - 14;
            font::text(&mut self.cv, 10, sy, &self.status, pal.text, 1);
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
