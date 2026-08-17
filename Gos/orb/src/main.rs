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

const W: usize = 1180;
const H: usize = 820;
const BAR_H: i32 = 34;
const HUD_W: i32 = 320;
const BLOCK: usize = 64;
const TICK: u32 = 33;
const TIMER_ID: usize = 1;
/// levels the buttons may reach. L7 is 327,680 faces -- affordable, and the
/// judge there is ~0.5 s, so it is the honest ceiling for an interactive panel.
const MAX_LEVEL: u32 = 7;

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
}

thread_local! { static APP: RefCell<Option<App>> = const { RefCell::new(None) }; }

fn main() {
    unsafe { run() }
}

unsafe fn run() {
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
    if RegisterClassW(&wc) == 0 {
        return;
    }
    APP.with(|a| *a.borrow_mut() = Some(App::new()));
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
        return;
    }
    ShowWindow(hwnd, SW_SHOW);
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
                        app.yaw += 0.012;
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
    fn new() -> App {
        let (label, bytes) = match std::env::args().nth(1) {
            Some(p) => {
                let b = fs::read(&p).unwrap_or_default();
                (p, b)
            }
            None => {
                let p = std::env::current_exe().unwrap_or_default();
                let b = fs::read(&p).unwrap_or_default();
                (
                    p.file_name().map(|s| s.to_string_lossy().to_string()).unwrap_or_default(),
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
        let shell = Shell::build(start, &bytes).or_else(|| Shell::build(3, &bytes)).expect("a shell must build");

        println!("AXIOM 01 GATE  chi {} genus {}  JUDGE {} us", shell.chi, shell.genus, shell.judged_us);
        println!("stream  {label} ({} bytes)  dup {rep}/{blocks} at {BLOCK}B", bytes.len());
        println!("start   L{}  {} faces  {} B/face", shell.level, shell.ico.faces.len(), shell.per_face);

        let session = open_session();
        println!("session {}", session.display());

        let pal = ALL[0];
        let mut app = App {
            cv: Canvas::new(W, H, pal.bg),
            dib: vec![0u8; W * H * 4],
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
        };
        app.layout();
        app
    }

    fn pal(&self) -> Palette {
        ALL[self.pal]
    }

    fn layout(&mut self) {
        let y = H as i32 - BAR_H + 6;
        let mut x = 10i32;
        self.buttons.clear();
        for (id, l) in [(0u8, "SHOT"), (1, "SPIN"), (2, "PALETTE"), (3, "LEVEL -"), (4, "LEVEL +")] {
            let w = font::width(l, 1) + 16;
            self.buttons.push((Rect::new(x, y, w, BAR_H - 12), l, id));
            x += w + 8;
        }
    }

    fn set_level(&mut self, d: i32) {
        let want = (self.shell.level as i32 + d).clamp(0, MAX_LEVEL as i32) as u32;
        if want == self.shell.level {
            self.status = format!("AT THE {} LEVEL ALREADY", if d > 0 { "TOP" } else { "BOTTOM" });
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
        let hit = self.buttons.iter().find(|(r, _, _)| r.contains(mx, my)).map(|(_, _, i)| *i);
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
        let area = Rect::new(0, 0, W as i32 - HUD_W, H as i32 - BAR_H);
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
            let col = if s.repeat[fi] { pal.orange } else { ramp(&pal, s.ink[fi]) };
            let span = (a.0 - b.0).abs().max((a.1 - b.1).abs()).max((a.0 - c.0).abs());
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
        let x = W as i32 - HUD_W + 12;
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
                format!("= {:.2} PCT OF FACES", 100.0 * s.repeats as f64 / s.ico.faces.len() as f64),
                pal.orange,
            ),
            (format!("WHOLE STREAM {:.2} PCT", self.dup_pct), pal.text),
            (format!("AT {} B BLOCKS", BLOCK), [0x4a, 0x5a, 0x6a]),
            (String::new(), pal.text),
            (format!("ENTROPY {:.4} B/B", self.entropy), pal.text),
            (format!("ONES    {:.2} PCT", self.ones_pct), pal.text),
            (String::new(), pal.text),
            (format!("RENDER {} US", self.render_us), pal.purple),
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
        self.cv.fill_rect(0, H as i32 - BAR_H, W as i32, BAR_H, pal.panel);
        self.cv.line(0, H as i32 - BAR_H, W as i32 - 1, H as i32 - BAR_H, pal.border);
        font::text(&mut self.cv, 10, H as i32 - BAR_H - 14, &self.status, pal.text, 1);
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
            self.status = format!("SHOT {:04} - L{} - SEAL {:016X}", self.shots, self.shell.level, self.seal);
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
                biHeight: -(H as i32),
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
            hdc, 0, 0, W as i32, H as i32, 0, 0, W as i32, H as i32,
            self.dib.as_ptr() as *const c_void, &bmi, DIB_RGB_COLORS, SRCCOPY,
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
        s.chars().rev().take(n).collect::<Vec<_>>().into_iter().rev().collect()
    }
}

fn append(p: &std::path::Path, s: &str) {
    use std::io::Write as _;
    if let Ok(mut f) = fs::OpenOptions::new().create(true).append(true).open(p) {
        let _ = f.write_all(s.as_bytes());
    }
}

fn open_session() -> PathBuf {
    let base = PathBuf::from(env!("CARGO_MANIFEST_DIR")).parent().map(|p| p.join("runs")).unwrap_or_default();
    let _ = fs::create_dir_all(&base);
    let pre = format!("orb_v{}_s", env!("CARGO_PKG_VERSION").replace('.', "_"));
    let n = fs::read_dir(&base)
        .map(|rd| {
            rd.filter_map(|e| e.ok())
                .filter_map(|e| e.file_name().to_string_lossy().strip_prefix(&pre).and_then(|s| s.parse::<usize>().ok()))
                .max()
                .unwrap_or(0)
        })
        .unwrap_or(0)
        + 1;
    let d = base.join(format!("{pre}{n:04}"));
    let _ = fs::create_dir_all(&d);
    d
}
