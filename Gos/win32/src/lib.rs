//! Raw Win32, declared by hand. No `windows` crate, no `winapi`, no bindgen.
//!
//! Everything below is an `extern "system"` declaration against `user32.dll`,
//! `gdi32.dll` and `kernel32.dll` -- the DLLs the OS already loads. That keeps
//! `[dependencies]` empty even here, in the untrusted layer, so RULE 0's fourth
//! row survives the whole program.
//!
//! This is the ONLY `unsafe` in the project, and it is confined to one crate
//! that does one thing: put a rectangle of our pixels on the screen and report
//! input. **Nothing here computes anything.**
//!
//! It became its own crate the moment a SECOND binary needed a window
//! (`gos_viewer` and `gos_orb`). Copying the file would have been faster and
//! would have quietly doubled the project's unsafe surface -- and RUSTIUM
//! states in print that there is exactly one such file. A claim in a scroll is
//! a constraint on the code, not a description of it.

#![allow(non_snake_case, non_camel_case_types, dead_code)]
// Every type below carries Win32's OWN name -- `HWND`, `LPARAM`, `BITMAPINFOHEADER`.
// clippy would rather they were `Hwnd`, `Lparam`, `BitmapInfoHeader`. Declined on
// purpose: the whole value of a hand-written FFI layer is that a reader can diff
// it line-by-line against the Microsoft documentation. Renaming the types to suit
// a style lint would make the one `unsafe` file in this project HARDER to audit,
// which is the opposite of why it is written out by hand.
#![allow(clippy::upper_case_acronyms)]

use std::ffi::c_void;

pub type HANDLE = *mut c_void;
pub type HWND = HANDLE;
pub type HDC = HANDLE;
pub type HINSTANCE = HANDLE;
pub type HICON = HANDLE;
pub type HCURSOR = HANDLE;
pub type HBRUSH = HANDLE;
pub type HMENU = HANDLE;
pub type LPARAM = isize;
pub type WPARAM = usize;
pub type LRESULT = isize;
pub type DWORD = u32;
pub type UINT = u32;
pub type BOOL = i32;
pub type LONG = i32;
pub type WORD = u16;

pub type WNDPROC = unsafe extern "system" fn(HWND, UINT, WPARAM, LPARAM) -> LRESULT;

// ---- messages -------------------------------------------------------------
pub const WM_DESTROY: UINT = 0x0002;
pub const WM_PAINT: UINT = 0x000F;
pub const WM_CLOSE: UINT = 0x0010;
pub const WM_KEYDOWN: UINT = 0x0100;
pub const WM_LBUTTONDOWN: UINT = 0x0201;
pub const WM_MOUSEMOVE: UINT = 0x0200;
/// the spin tick -- `SetTimer` drives "spini spini" without a render thread
pub const WM_TIMER: UINT = 0x0113;

// ---- window styles --------------------------------------------------------
pub const WS_OVERLAPPED: DWORD = 0x0000_0000;
pub const WS_CAPTION: DWORD = 0x00C0_0000;
pub const WS_SYSMENU: DWORD = 0x0008_0000;
pub const WS_MINIMIZEBOX: DWORD = 0x0002_0000;
pub const WS_VISIBLE: DWORD = 0x1000_0000;
pub const WS_OVERLAPPEDWINDOW: DWORD = WS_OVERLAPPED | WS_CAPTION | WS_SYSMENU | WS_MINIMIZEBOX;

pub const CW_USEDEFAULT: i32 = 0x8000_0000u32 as i32;
pub const CS_HREDRAW: UINT = 0x0002;
pub const CS_VREDRAW: UINT = 0x0001;
pub const CS_OWNDC: UINT = 0x0020;
pub const IDC_ARROW: usize = 32512;
pub const SW_SHOW: i32 = 5;

/// `SetWindowPos`: keep the current size.
pub const SWP_NOSIZE: u32 = 0x0001;

/// `SetWindowPos`: keep the current Z order.
pub const SWP_NOZORDER: u32 = 0x0004;

/// Show the window maximised.
pub const SW_MAXIMIZE: i32 = 3;

// ---- DIB ------------------------------------------------------------------
pub const BI_RGB: DWORD = 0;
pub const DIB_RGB_COLORS: UINT = 0;
pub const SRCCOPY: DWORD = 0x00CC_0020;

pub const VK_ESCAPE: WPARAM = 0x1B;

#[repr(C)]
#[derive(Clone, Copy)]
pub struct POINT {
    pub x: LONG,
    pub y: LONG,
}

#[repr(C)]
#[derive(Clone, Copy)]
pub struct RECT {
    pub left: LONG,
    pub top: LONG,
    pub right: LONG,
    pub bottom: LONG,
}

#[repr(C)]
pub struct MSG {
    pub hwnd: HWND,
    pub message: UINT,
    pub wParam: WPARAM,
    pub lParam: LPARAM,
    pub time: DWORD,
    pub pt: POINT,
}

#[repr(C)]
pub struct WNDCLASSW {
    pub style: UINT,
    pub lpfnWndProc: Option<WNDPROC>,
    pub cbClsExtra: i32,
    pub cbWndExtra: i32,
    pub hInstance: HINSTANCE,
    pub hIcon: HICON,
    pub hCursor: HCURSOR,
    pub hbrBackground: HBRUSH,
    pub lpszMenuName: *const u16,
    pub lpszClassName: *const u16,
}

#[repr(C)]
pub struct PAINTSTRUCT {
    pub hdc: HDC,
    pub fErase: BOOL,
    pub rcPaint: RECT,
    pub fRestore: BOOL,
    pub fIncUpdate: BOOL,
    pub rgbReserved: [u8; 32],
}

#[repr(C)]
#[derive(Clone, Copy)]
pub struct BITMAPINFOHEADER {
    pub biSize: DWORD,
    pub biWidth: LONG,
    pub biHeight: LONG,
    pub biPlanes: WORD,
    pub biBitCount: WORD,
    pub biCompression: DWORD,
    pub biSizeImage: DWORD,
    pub biXPelsPerMeter: LONG,
    pub biYPelsPerMeter: LONG,
    pub biClrUsed: DWORD,
    pub biClrImportant: DWORD,
}

#[repr(C)]
pub struct BITMAPINFO {
    pub bmiHeader: BITMAPINFOHEADER,
    pub bmiColors: [DWORD; 3],
}

// --- executable memory, for the assembly witness ----------------------------
// `experiments/` hand-assembles 23 bytes of x86-64 machine code and asks the
// CPU to run them. Data pages are non-executable (DEP/NX), so the bytes must
// live in a page allocated with PAGE_EXECUTE_READWRITE. These are the
// declarations for that, and nothing here computes anything -- same rule as
// the rest of this crate.
pub const MEM_COMMIT: u32 = 0x0000_1000;
pub const MEM_RESERVE: u32 = 0x0000_2000;
pub const MEM_RELEASE: u32 = 0x0000_8000;
pub const PAGE_EXECUTE_READWRITE: u32 = 0x40;

#[link(name = "kernel32")]
extern "system" {
    pub fn GetModuleHandleW(lpModuleName: *const u16) -> HINSTANCE;

    pub fn VirtualAlloc(
        lpAddress: *mut core::ffi::c_void,
        dwSize: usize,
        flAllocationType: u32,
        flProtect: u32,
    ) -> *mut core::ffi::c_void;

    pub fn VirtualFree(lpAddress: *mut core::ffi::c_void, dwSize: usize, dwFreeType: u32) -> BOOL;
}

#[link(name = "user32")]
extern "system" {
    pub fn RegisterClassW(lpWndClass: *const WNDCLASSW) -> u16;
    pub fn CreateWindowExW(
        dwExStyle: DWORD,
        lpClassName: *const u16,
        lpWindowName: *const u16,
        dwStyle: DWORD,
        x: i32,
        y: i32,
        nWidth: i32,
        nHeight: i32,
        hWndParent: HWND,
        hMenu: HMENU,
        hInstance: HINSTANCE,
        lpParam: *mut c_void,
    ) -> HWND;
    pub fn DefWindowProcW(hWnd: HWND, msg: UINT, wParam: WPARAM, lParam: LPARAM) -> LRESULT;
    pub fn GetMessageW(
        lpMsg: *mut MSG,
        hWnd: HWND,
        wMsgFilterMin: UINT,
        wMsgFilterMax: UINT,
    ) -> BOOL;
    pub fn TranslateMessage(lpMsg: *const MSG) -> BOOL;
    pub fn DispatchMessageW(lpMsg: *const MSG) -> LRESULT;
    pub fn BeginPaint(hWnd: HWND, lpPaint: *mut PAINTSTRUCT) -> HDC;
    pub fn EndPaint(hWnd: HWND, lpPaint: *const PAINTSTRUCT) -> BOOL;
    pub fn InvalidateRect(hWnd: HWND, lpRect: *const RECT, bErase: BOOL) -> BOOL;
    pub fn PostQuitMessage(nExitCode: i32);
    pub fn DestroyWindow(hWnd: HWND) -> BOOL;
    pub fn LoadCursorW(hInstance: HINSTANCE, lpCursorName: usize) -> HCURSOR;
    pub fn ShowWindow(hWnd: HWND, nCmdShow: i32) -> BOOL;
    pub fn SetWindowTextW(hWnd: HWND, lpString: *const u16) -> BOOL;
    pub fn GetClientRect(hWnd: HWND, lpRect: *mut RECT) -> BOOL;
    pub fn SetTimer(hWnd: HWND, nIDEvent: usize, uElapse: UINT, lpTimerFunc: usize) -> usize;
    pub fn KillTimer(hWnd: HWND, nIDEvent: usize) -> BOOL;

    /// Grow a desired CLIENT rect into the WINDOW rect that yields it.
    ///
    /// The border and caption are the OS's business and their size is not
    /// knowable at compile time -- it varies with the theme, the Windows
    /// version and the DPI. Guessing them (`W + 16`, `H + 39`) is how a canvas
    /// ends up clipped at the bottom while looking fine on the machine the
    /// guess was made on.
    pub fn AdjustWindowRect(lpRect: *mut RECT, dwStyle: u32, bMenu: BOOL) -> BOOL;

    /// Move or resize a window. Used only to PLACE it -- the canvas decides
    /// the size, so `SWP_NOSIZE` is always set here.
    pub fn SetWindowPos(
        hWnd: HWND,
        hWndInsertAfter: HWND,
        X: i32,
        Y: i32,
        cx: i32,
        cy: i32,
        uFlags: u32,
    ) -> BOOL;

    /// Bring a window to the top of the Z order.
    ///
    /// **`ShowWindow` shows; it does not RAISE.** A window created by a
    /// process launched from an elevated console appears *behind* the console
    /// that launched it, and to the person who typed the command that is
    /// indistinguishable from "no window opened". Both calls are needed, and
    /// neither is guaranteed -- Windows refuses foreground steals from
    /// background processes -- so the caller must treat failure as normal and
    /// not as an error.
    pub fn BringWindowToTop(hWnd: HWND) -> BOOL;

    /// Ask for the foreground. May legitimately fail; see [`BringWindowToTop`].
    pub fn SetForegroundWindow(hWnd: HWND) -> BOOL;

    /// A system metric, by index. See [`SM_CXFULLSCREEN`].
    ///
    /// **Call `SetProcessDpiAwarenessContext` FIRST.** Without it these come
    /// back in virtual, scaled coordinates -- on a 150% display a 2560-wide
    /// panel reports 1707, and a canvas sized from that would be resampled by
    /// exactly the factor the DPI work went in to remove.
    pub fn GetSystemMetrics(nIndex: i32) -> i32;

    /// Declare this process DPI-aware, per monitor, v2.
    ///
    /// **Without this the OS RESAMPLES the whole framebuffer before it reaches
    /// the glass.** On a 150% display the window we ask for at 916x739 is
    /// created at 1374x1109 and every pixel the kernel computed is stretched
    /// by 1.5 and interpolated by a bitmap scaler we do not own.
    ///
    /// The frame seal hashes the framebuffer, so it cannot see this: the
    /// receipt stays honest while the thing on screen stops being the thing
    /// that was sealed. Curse 26 wearing a display driver.
    ///
    /// Available since Windows 10 1703. Returns 0 on failure, and the caller
    /// must SAY SO rather than carry on pretending the pixels are exact.
    pub fn SetProcessDpiAwarenessContext(value: isize) -> BOOL;
}

/// Width of the CLIENT area of a maximised window -- the screen less the
/// taskbar and the window frame. Exactly the number "fill the screen" wants,
/// which is why it is used instead of `SM_CXSCREEN` and some guesswork.
pub const SM_CXFULLSCREEN: i32 = 16;

/// Height of the client area of a maximised window.
pub const SM_CYFULLSCREEN: i32 = 17;

/// `DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2` -- the handle value, as
/// documented. Not a pointer we dereference; a sentinel the OS compares.
pub const DPI_PER_MONITOR_AWARE_V2: isize = -4;

#[link(name = "gdi32")]
extern "system" {
    pub fn StretchDIBits(
        hdc: HDC,
        xDest: i32,
        yDest: i32,
        DestWidth: i32,
        DestHeight: i32,
        xSrc: i32,
        ySrc: i32,
        SrcWidth: i32,
        SrcHeight: i32,
        lpBits: *const c_void,
        lpbmi: *const BITMAPINFO,
        iUsage: UINT,
        rop: DWORD,
    ) -> i32;
}

/// A NUL-terminated UTF-16 string, for the W-suffixed APIs.
pub fn wide(s: &str) -> Vec<u16> {
    s.encode_utf16().chain(std::iter::once(0)).collect()
}

/// Low and high 16-bit halves of an `LPARAM`, as signed screen coordinates.
pub fn lparam_xy(l: LPARAM) -> (i32, i32) {
    let lo = (l & 0xFFFF) as u16 as i16 as i32;
    let hi = ((l >> 16) & 0xFFFF) as u16 as i16 as i32;
    (lo, hi)
}
