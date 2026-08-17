//! GOS ORB -- the spini spini byte topology.
//!
//! The second program. `gos_viewer` shows the dashboard; this shows the
//! TOPOLOGY OF THE CURRENT CODE -- a file's 1s and 0s laid on the certified
//! closed shell, spinning, so duplication becomes something the eye can see.
//!
//! ```text
//!   byte_oracle.html  : bytes on an OPEN plane. edges, corners, a beginning.
//!   byte_sphere.html  : bytes on a sphere, but chi=2 printed as a LITERAL.
//!   gos_orb           : bytes on C60, chi COUNTED by the integer judge, and
//!                       the twelve pentagons drawn because Euler forces them.
//! ```
//!
//! # What it measures
//!
//! Duplication, because that is the finding the census already made and never
//! showed: `MATH_LEDGER.md` counted **89.9% redundant characters** across 2,333
//! sims, `buildC60Faces()` copied into 249 of them. This program takes any byte
//! stream, blocks it, hashes the blocks, and paints the repeats. Structure that
//! repeats is structure that could be a kernel instead.
//!
//! # Honest boundary
//!
//! C60 has **32 faces**. That is a coarse canvas for a 500 KB binary -- about
//! 17 KB per face -- so the shell shows the SHAPE of the distribution, not the
//! detail. The block-level duplication numbers in the HUD are computed over the
//! whole stream at 64-byte granularity and are exact; only the *painting* is
//! coarse. When `Mesh::refine()` exists this gets its resolution and the numbers
//! do not change. Stated rather than blurred (Path IV).
//!
//! ```powershell
//! cargo run -p gos_orb --release            # its own machine code
//! cargo run -p gos_orb --release -- FILE    # any file
//! ```

use std::cell::RefCell;
use std::ffi::c_void;
use std::fs;
use std::path::PathBuf;
use std::time::Instant;

use goldberg_kernel::bits;
use goldberg_kernel::font;
use goldberg_kernel::layout::Rect;
use goldberg_kernel::palette::{Palette, Rgb, ALL};
use goldberg_kernel::raster::{project, Canvas};
use goldberg_kernel::{centroid, certify, judge, project_to_sphere, Cert, Mesh};

use gos_win32::*;

const W: usize = 1000;
const H: usize = 760;
const BAR_H: i32 = 34;
const HUD_W: i32 = 300;
/// duplication is measured at this granularity, over the WHOLE stream
const BLOCK: usize = 64;
/// spin tick, milliseconds -- ~30 Hz, far below what the renderer can do
const TICK: u32 = 33;
const TIMER_ID: usize = 1;

/// What the byte stream turned out to be. All measured, none assumed.
struct Census {
    label: String,
    bytes: Vec<u8>,
    /// blocks of `BLOCK` bytes
    blocks: usize,
    /// blocks whose content was seen earlier in the stream
    repeated: usize,
    /// distinct block contents
    unique: usize,
    ones: usize,
    entropy: f64,
    /// per-face: (ones density 0..255, is this face's block a repeat)
    face_ink: Vec<(u8, bool)>,
}

impl Census {
    fn of(label: String, bytes: Vec<u8>, faces: usize) -> Census {
        // ---- duplication over the whole stream, at BLOCK granularity ----
        let mut seen: Vec<u64> = Vec::new();
        let mut repeated = 0usize;
        let mut blocks = 0usize;
        for chunk in bytes.chunks(BLOCK) {
            let h = bits::digest(chunk);
            blocks += 1;
            if seen.contains(&h) {
                repeated += 1;
            } else {
                seen.push(h);
            }
        }
        let unique = seen.len();

        // ---- per-face ink: the shell is coarse, and that is stated ----
        let mut face_ink = Vec::with_capacity(faces);
        let per = (bytes.len() / faces.max(1)).max(1);
        let mut fseen: Vec<u64> = Vec::new();
        for i in 0..faces {
            let s = (i * per).min(bytes.len());
            let e = ((i + 1) * per).min(bytes.len());
            let slice = &bytes[s..e];
            let ink = if slice.is_empty() {
                0u8
            } else {
                let ones = bits::ones(slice);
                ((ones * 255) / (slice.len() * 8)) as u8
            };
            let h = bits::digest(slice);
            let rep = fseen.contains(&h);
            if !rep {
                fseen.push(h);
            }
            face_ink.push((ink, rep));
        }

        Census {
            blocks,
            repeated,
            unique,
            ones: bits::ones(&bytes),
            entropy: bits::entropy(&bytes),
            face_ink,
            label,
            bytes,
        }
    }

    fn dup_pct(&self) -> f64 {
        if self.blocks == 0 {
            0.0
        } else {
            100.0 * self.repeated as f64 / self.blocks as f64
        }
    }
    fn ones_pct(&self) -> f64 {
        let n = self.bytes.len() * 8;
        if n == 0 {
            0.0
        } else {
            100.0 * self.ones as f64 / n as f64
        }
    }
}

/// The Class I rung that would hold this many bits, one bit per node.
///
/// `T = k^2`, `V = 20T`, and `k` is FREE -- which is why this lane fits a
/// payload to 99.99% where `7^k` can waste 85%. Exact integers.
fn rung_for(bits_needed: usize) -> (usize, usize, usize) {
    let need_t = bits_needed.div_ceil(20);
    let mut k = (need_t as f64).sqrt() as usize;
    while k * k < need_t {
        k += 1;
    }
    (k, k * k, 20 * k * k)
}

struct App {
    cv: Canvas,
    dib: Vec<u8>,
    mesh: Mesh,
    cert: Cert,
    verdict: judge::Verdict,
    pent_face: Vec<bool>,
    census: Census,
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

thread_local! {
    static APP: RefCell<Option<App>> = const { RefCell::new(None) };
}

fn main() {
    unsafe { run() }
}

unsafe fn run() {
    let hinst = GetModuleHandleW(std::ptr::null());
    let class = wide("GosOrbClass");
    let title = wide("GOS ORB - the spini spini byte topology");

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
            let mut spin = false;
            APP.with(|a| {
                if let Some(app) = a.borrow_mut().as_mut() {
                    if app.spin {
                        app.yaw += 0.012;
                        spin = true;
                    }
                }
            });
            if spin {
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
        // AXIOM 01 -- the gate, before a pixel exists.
        let mesh = Mesh::c60();
        let cert = certify(&mesh).expect("P=12 and chi=2, or do not ship");
        let verdict = judge::check(&judge::rotation_system_c60()).expect("the judge must agree");
        println!("AXIOM 01 GATE");
        println!("  float lane : {cert}");
        println!("  judge      : {verdict}");

        // which faces are pentagons -- Euler forces exactly twelve
        let pent_face: Vec<bool> = mesh.faces.iter().map(|f| f.len() == 5).collect();
        assert_eq!(
            pent_face.iter().filter(|&&p| p).count(),
            12,
            "Euler forces twelve pentagons"
        );

        // the byte stream: a file if given, otherwise our own machine code
        let arg = std::env::args().nth(1);
        let (label, bytes) = match arg {
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
                        .unwrap_or_else(|| String::from("self")),
                    b,
                )
            }
        };
        println!("stream     : {} ({} bytes)", label, bytes.len());

        let census = Census::of(label, bytes, mesh.faces.len());
        println!(
            "duplication: {}/{} blocks repeat at {}B granularity = {:.2}%",
            census.repeated,
            census.blocks,
            BLOCK,
            census.dup_pct()
        );
        println!(
            "entropy    : {:.4} bits/byte   ones {:.2}%",
            census.entropy,
            census.ones_pct()
        );
        let (k, t, v) = rung_for(census.bytes.len() * 8);
        println!("rung needed: Class I k={k}  T={t}  V=20T={v} nodes (one bit per node)");

        let session = open_session(&cert, &verdict, &census);
        println!("session    : {}", session.display());

        let pal = ALL[0];
        let mut app = App {
            cv: Canvas::new(W, H, pal.bg),
            dib: vec![0u8; W * H * 4],
            mesh,
            cert,
            verdict,
            pent_face,
            census,
            pal: 0,
            yaw: 0.6,
            spin: true,
            render_us: 0,
            seal: 0,
            status: String::from("SPINNING. THROUGH MOVEMENT MORE DATA IS EXTRACTED."),
            buttons: Vec::new(),
            session,
            shots: 0,
        };
        app.layout();
        // the PNG at startup, as asked -- the topology as it was on open
        app.render();
        app.save_shot();
        app
    }

    fn pal(&self) -> Palette {
        ALL[self.pal]
    }

    fn layout(&mut self) {
        let y = H as i32 - BAR_H + 6;
        let mut x = 10i32;
        self.buttons.clear();
        for (id, label) in [
            (0u8, "SHOT"),
            (1, "SPIN"),
            (2, "PALETTE"),
            (3, "DUMP BITS"),
        ] {
            let w = font::width(label, 1) + 16;
            self.buttons
                .push((Rect::new(x, y, w, BAR_H - 12), label, id));
            x += w + 8;
        }
    }

    fn click(&mut self, mx: i32, my: i32) -> bool {
        let hit = self
            .buttons
            .iter()
            .find(|(r, _, _)| r.contains(mx, my))
            .map(|(_, _, id)| *id);
        match hit {
            Some(0) => {
                self.save_shot();
                true
            }
            Some(1) => {
                self.spin = !self.spin;
                self.status = if self.spin {
                    String::from("SPINNING. MOVEMENT IS THE SECOND TEST.")
                } else {
                    String::from("HELD. SYMMETRY IS THE FIRST TEST.")
                };
                true
            }
            Some(2) => {
                self.pal = (self.pal + 1) % ALL.len();
                self.status = format!("PALETTE {}", self.pal().name.to_uppercase());
                true
            }
            Some(3) => {
                self.dump_bits();
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
        // R10: seal the content BEFORE the chrome, which carries a clock
        self.seal = self.cv.digest();
        self.paint_hud();
        self.paint_bar();
    }

    /// The shell, painter-sorted, each face inked by the bytes that landed on it.
    /// Pentagons always outlined -- the twelve constraints, visible at all times.
    fn paint_orb(&mut self) {
        let pal = self.pal();
        let area = Rect::new(0, 0, W as i32 - HUD_W, H as i32 - BAR_H);
        let (rx, zoom) = (0.32_f64, 300.0_f64);

        // face centres and their depth
        let mut order: Vec<(usize, f64)> = Vec::with_capacity(self.mesh.faces.len());
        let mut poly: Vec<Vec<(i32, i32)>> = Vec::with_capacity(self.mesh.faces.len());
        for (fi, face) in self.mesh.faces.iter().enumerate() {
            let mut pts = Vec::with_capacity(face.len());
            let mut depth = 0.0;
            for &vi in face {
                let (sx, sy, z) =
                    project(self.mesh.verts[vi], rx, self.yaw, zoom, area.w as usize, area.h as usize);
                pts.push((sx, sy));
                depth += z;
            }
            order.push((fi, depth / face.len() as f64));
            poly.push(pts);
        }
        order.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());

        // outward-facing test: the face centroid must point toward the camera
        let centers: Vec<[f64; 3]> = self
            .mesh
            .faces
            .iter()
            .map(|f| {
                let p: Vec<[f64; 3]> = f.iter().map(|&i| self.mesh.verts[i]).collect();
                project_to_sphere(centroid(&p), 1.0)
            })
            .collect();

        for (fi, depth) in order {
            let (_, _, cz) = project(centers[fi], rx, self.yaw, zoom, area.w as usize, area.h as usize);
            if cz < 0.0 {
                continue; // back face
            }
            let (ink, repeat) = self.census.face_ink[fi];
            let t = ((depth + 2.0) / 4.0).clamp(0.0, 1.0);
            let alpha = (0.20 + t * 0.55) * 255.0;

            // a REPEATED block is painted in the alarm colour, not the ink ramp:
            // duplication is the finding, so it must not be a shade of the
            // normal case (Curse 26 -- do not let a signal hide inside a ramp).
            let base = if repeat { pal.orange } else { ink_ramp(&pal, ink) };
            fill_poly(&mut self.cv, &poly[fi], base, alpha as u8);

            let edge = if self.pent_face[fi] { pal.pink } else { pal.cyan };
            let ea = if self.pent_face[fi] { 255 } else { (alpha * 0.7) as u8 };
            let p = &poly[fi];
            for i in 0..p.len() {
                let (x0, y0) = p[i];
                let (x1, y1) = p[(i + 1) % p.len()];
                self.cv.line_a(x0, y0, x1, y1, edge, ea);
            }
        }
    }

    fn paint_hud(&mut self) {
        let pal = self.pal();
        let x = W as i32 - HUD_W + 12;
        let mut y = 14;
        let c = &self.census;

        font::text(&mut self.cv, x, y, "GOS ORB", pal.gold, 2);
        y += 22;
        font::text(&mut self.cv, x, y, "THE SPINI SPINI TOPOLOGY", pal.pink, 1);
        y += 18;

        let (k, t, v) = rung_for(c.bytes.len() * 8);
        let rows: Vec<(String, Rgb)> = vec![
            (format!("STREAM  {}", trunc(&c.label, 22)), pal.cyan),
            (format!("BYTES   {}", c.bytes.len()), pal.text),
            (String::new(), pal.text),
            (String::from("-- AXIOM 01 GATE --"), pal.gold),
            (
                format!("V {} E {} F {}", self.cert.v, self.cert.e, self.cert.f),
                pal.green,
            ),
            (
                format!("P {} CHI {} GENUS {}", self.cert.p, self.verdict.chi,
                        self.verdict.genus.unwrap_or(-1)),
                pal.green,
            ),
            (String::from("LANES AGREE  COUNTED"), pal.green),
            (String::new(), pal.text),
            (String::from("-- DUPLICATION --"), pal.gold),
            (format!("BLOCK   {} BYTES", BLOCK), pal.text),
            (format!("BLOCKS  {}", c.blocks), pal.text),
            (format!("UNIQUE  {}", c.unique), pal.text),
            (format!("REPEAT  {}", c.repeated), pal.orange),
            (format!("DUP     {:.2} PCT", c.dup_pct()), pal.orange),
            (String::new(), pal.text),
            (String::from("-- THE STREAM --"), pal.gold),
            (format!("ONES    {:.2} PCT", c.ones_pct()), pal.text),
            (format!("ENTROPY {:.4} B/B", c.entropy), pal.text),
            (String::new(), pal.text),
            (String::from("-- RUNG NEEDED --"), pal.gold),
            (format!("CLASS I K {}", k), pal.cyan),
            (format!("T {}", t), pal.cyan),
            (format!("V 20T {}", v), pal.cyan),
            (String::new(), pal.text),
            (format!("RENDER  {} US", self.render_us), pal.purple),
            (format!("SEAL {:016X}", self.seal), pal.purple),
        ];
        for (s, col) in rows {
            if !s.is_empty() {
                font::text(&mut self.cv, x, y, &s, col, 1);
            }
            y += 11;
        }

        // the honest note about resolution
        y += 6;
        for line in [
            "C60 HAS 32 FACES. THE SHELL",
            "SHOWS SHAPE, NOT DETAIL. THE",
            "DUP NUMBERS ARE EXACT OVER THE",
            "WHOLE STREAM AT 64B BLOCKS.",
        ] {
            font::text(&mut self.cv, x, y, line, pal.border, 1);
            y += 10;
        }
    }

    fn paint_bar(&mut self) {
        let pal = self.pal();
        self.cv
            .fill_rect(0, H as i32 - BAR_H, W as i32, BAR_H, pal.panel);
        self.cv
            .line(0, H as i32 - BAR_H, W as i32 - 1, H as i32 - BAR_H, pal.border);
        font::text(
            &mut self.cv,
            10,
            H as i32 - BAR_H - 14,
            &self.status,
            pal.text,
            1,
        );
        let btns = self.buttons.clone();
        for (r, label, id) in btns {
            let accent = match id {
                0 => pal.gold,
                1 => pal.pink,
                3 => pal.orange,
                _ => pal.cyan,
            };
            self.cv.rect(r.x, r.y, r.w, r.h, accent);
            font::text(
                &mut self.cv,
                r.x + 8,
                r.y + (r.h - font::GH) / 2,
                label,
                accent,
                1,
            );
        }
    }

    fn save_shot(&mut self) {
        self.shots += 1;
        let f = self.session.join(format!("orb_{:04}.png", self.shots));
        match self.cv.write_png(&f) {
            Ok(()) => {
                self.status = format!("SHOT {:04} - SEAL {:016X}", self.shots, self.seal);
                let line = format!(
                    "orb_{:04}.png  yaw={:.4}  palette={}  render_us={}  seal={:016x}\n",
                    self.shots,
                    self.yaw,
                    self.pal().name,
                    self.render_us,
                    self.seal
                );
                append(&self.session.join("SHOTS.log"), &line);
                println!("{}", self.status);
            }
            Err(e) => self.status = format!("SHOT FAILED: {e}"),
        }
    }

    /// The stream as a 1/0 matrix. Capped, and the cap is in OUTPUT bytes this
    /// time -- R11: a cap stated in source bytes bounded a file eight times
    /// larger. 8 source bytes become 8 output bytes per bit, so divide by 8.
    fn dump_bits(&mut self) {
        const OUT_CAP: usize = 8 * 1024 * 1024;
        let src_cap = OUT_CAP / 9; // 8 chars per byte plus newlines
        let f = self.session.join("stream.bits");
        match bits::write_bits(&f, &self.census.label, &self.census.bytes, 64, src_cap) {
            Ok(r) => {
                self.status = format!(
                    "BITS {} OF {} BYTES{} - FNV {:016X}",
                    r.bytes_written,
                    r.bytes_total,
                    if r.truncated { " (CAPPED, SAYING SO)" } else { "" },
                    r.digest
                );
                println!("{}", self.status);
            }
            Err(e) => self.status = format!("DUMP FAILED: {e}"),
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

/// Ink ramp for a face: dim panel -> cyan -> bright. Integer interpolation.
fn ink_ramp(pal: &Palette, t: u8) -> Rgb {
    let t = t as u32;
    let (a, b) = (pal.panel, pal.cyan);
    [
        ((a[0] as u32 * (255 - t) + b[0] as u32 * t) / 255) as u8,
        ((a[1] as u32 * (255 - t) + b[1] as u32 * t) / 255) as u8,
        ((a[2] as u32 * (255 - t) + b[2] as u32 * t) / 255) as u8,
    ]
}

/// Fill a convex polygon by scanline. Integer edges, integer spans.
fn fill_poly(cv: &mut Canvas, pts: &[(i32, i32)], c: Rgb, a: u8) {
    if pts.len() < 3 {
        return;
    }
    let (mut lo, mut hi) = (i32::MAX, i32::MIN);
    for &(_, y) in pts {
        lo = lo.min(y);
        hi = hi.max(y);
    }
    for y in lo..=hi {
        let mut xs: Vec<i32> = Vec::with_capacity(8);
        for i in 0..pts.len() {
            let (x0, y0) = pts[i];
            let (x1, y1) = pts[(i + 1) % pts.len()];
            if (y0 <= y && y1 > y) || (y1 <= y && y0 > y) {
                let dy = y1 - y0;
                if dy != 0 {
                    xs.push(x0 + (y - y0) * (x1 - x0) / dy);
                }
            }
        }
        xs.sort_unstable();
        for pair in xs.chunks(2) {
            if let [xa, xb] = pair {
                for x in *xa..=*xb {
                    cv.blend(x, y, c, a);
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

fn append(path: &std::path::Path, s: &str) {
    use std::io::Write as _;
    if let Ok(mut f) = fs::OpenOptions::new().create(true).append(true).open(path) {
        let _ = f.write_all(s.as_bytes());
    }
}

fn runs_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .map(|p| p.join("runs"))
        .unwrap_or_else(|| PathBuf::from("runs"))
}

fn open_session(cert: &Cert, verdict: &judge::Verdict, c: &Census) -> PathBuf {
    let ver = env!("CARGO_PKG_VERSION").replace('.', "_");
    let base = runs_dir();
    let _ = fs::create_dir_all(&base);
    let prefix = format!("orb_v{ver}_s");
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

    let (k, t, v) = rung_for(c.bytes.len() * 8);
    let lines = vec![
        String::from("{"),
        format!("  \"program\": \"gos_orb\","),
        format!("  \"session\": {n},"),
        format!("  \"version\": \"{}\",", env!("CARGO_PKG_VERSION")),
        format!("  \"stream\": \"{}\",", c.label.replace('\\', "/")),
        format!("  \"bytes\": {},", c.bytes.len()),
        String::from("  \"axiom_01_gate\": {"),
        format!(
            "    \"float_lane\": {{ \"v\": {}, \"e\": {}, \"f\": {}, \"p\": {}, \"chi\": {} }},",
            cert.v, cert.e, cert.f, cert.p, cert.chi
        ),
        format!(
            "    \"integer_judge\": {{ \"v\": {}, \"e\": {}, \"f\": {}, \"chi\": {}, \"genus\": {} }},",
            verdict.v, verdict.e, verdict.f, verdict.chi, verdict.genus.unwrap_or(-1)
        ),
        String::from("    \"passed\": true"),
        String::from("  },"),
        String::from("  \"duplication\": {"),
        format!("    \"block_bytes\": {BLOCK},"),
        format!("    \"blocks\": {},", c.blocks),
        format!("    \"unique\": {},", c.unique),
        format!("    \"repeated\": {},", c.repeated),
        format!("    \"pct\": {:.4}", c.dup_pct()),
        String::from("  },"),
        format!("  \"ones_pct\": {:.4},", c.ones_pct()),
        format!("  \"entropy_bits_per_byte\": {:.6},", c.entropy),
        format!(
            "  \"rung_needed\": {{ \"lane\": \"class_I\", \"k\": {k}, \"t\": {t}, \"v\": {v} }},"
        ),
        String::from("  \"note\": \"C60 has 32 faces; the shell shows shape, the numbers are exact\""),
        String::from("}"),
    ];
    let _ = fs::write(dir.join("SESSION.json"), lines.join("\n") + "\n");
    dir
}
