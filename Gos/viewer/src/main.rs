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

mod win32;

use std::cell::RefCell;
use std::ffi::c_void;
use std::fs;
use std::path::PathBuf;
use std::time::Instant;

use goldberg_kernel::bits;
use goldberg_kernel::font;
use goldberg_kernel::palette::{Palette, ALL};
use goldberg_kernel::raster::{project, Canvas};
use goldberg_kernel::{certify, judge, Mesh};

use win32::*;

const W: usize = 900;
const H: usize = 700;
const BAR_H: i32 = 34;

/// Cap on any single exported dump. The HELENA doctrine: heavy payload stays
/// local, git keeps the manifest. A cap that is stated is engineering; a dump
/// that silently stops is a lie (Path IV).
const DUMP_CAP: usize = 4 * 1024 * 1024;

#[derive(Clone, Copy, PartialEq, Eq, Debug)]
enum View {
    /// the certified C60, painted
    Shell,
    /// the framebuffer's own bits, as a 1/0 texture
    FrameBits,
    /// what rustc emitted for this .exe, as a 1/0 texture
    MachineBits,
}

impl View {
    fn title(self) -> &'static str {
        match self {
            View::Shell => "THE SHELL - C60 CERTIFIED",
            View::FrameBits => "THE FRAME - ITS OWN 1 AND 0S",
            View::MachineBits => "THE MACHINE - WHAT RUSTC EMITTED",
        }
    }
}

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

        let pal = ALL[0];
        let mut app = App {
            cv: Canvas::new(W, H, pal.bg),
            dib: vec![0u8; W * H * 4],
            stack: vec![View::Shell],
            pal: 0,
            buttons: Vec::new(),
            status: String::from("READY. THE SHELL IS CERTIFIED BEFORE IT IS DRESSED."),
            runs: next_run_index(),
            last_render_us: 0,
            content_digest: 0,
            flipped: 0,
            mesh,
            pent_edge,
            exe_bytes,
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
            (0u8, "EXPORT PNG + BITS"),
            (1, "FRAME BITS"),
            (2, "MACHINE BITS"),
            (3, "PALETTE"),
            (4, "BACK"),
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
        let hit = self.buttons.iter().find(|b| b.hit(mx, my)).map(|b| b.id);
        match hit {
            Some(0) => {
                self.export();
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

        // header
        font::text(&mut self.cv, 10, 10, v.title(), pal.gold, 2);
        // the sealed content digest, NOT a fresh one -- R10
        let sub = format!(
            "V 60 E 90 F 32 CHI 2 P 12 - RENDER {} US - SEAL {:016X}",
            self.last_render_us, self.content_digest
        );
        font::text(&mut self.cv, 10, 30, &sub, pal.cyan, 1);

        // status line
        let sy = H as i32 - BAR_H - 14;
        font::text(&mut self.cv, 10, sy, &self.status, pal.text, 1);

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
            font::text(&mut self.cv, x + 8, y + (h - font::GH) / 2, label, accent, 1);
        }
    }

    /// PNG + a 1/0 vector matrix + a manifest, into `runs/NNN/`.
    ///
    /// The HELENA doctrine, applied: the payload is local and gitignored, the
    /// MANIFEST is tracked, so another mage sees the exact steps and can
    /// regenerate. Pay thea Heleni in compute.
    fn export(&mut self) {
        self.runs += 1;
        let dir = runs_dir().join(format!("{:04}", self.runs));
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

/// Highest existing run index, so numbering never collides and never needs a
/// clock (Curse 38 -- deterministic, not timestamped).
fn next_run_index() -> usize {
    fs::read_dir(runs_dir())
        .map(|rd| {
            rd.filter_map(|e| e.ok())
                .filter_map(|e| e.file_name().to_string_lossy().parse::<usize>().ok())
                .max()
                .unwrap_or(0)
        })
        .unwrap_or(0)
}
