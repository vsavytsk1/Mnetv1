//! # chi_witness -- seven machines, one integer, no compiler trusted
//!
//! The engineering trick: when you cannot verify a machine from the inside,
//! run the same job on **different machines** and see whether they hand back
//! the same colour. Any one of them may be wrong. All of them being wrong the
//! same way is a much smaller universe.
//!
//! ## The identity under test
//!
//! From the Goldberg ladder, at triangulation number `T`:
//!
//! ```text
//!   V = 20T          E = 30T          F = 10T + 2
//!   chi = V - E + F = 20T - 30T + 10T + 2
//!                   = (20 - 30 + 10)T + 2
//!                   = 0*T + 2
//!                   = 2                      for every T. always.
//! ```
//!
//! This is the right thing to take to the metal, for three reasons:
//!
//! 1. **It is pure integer.** No float can enter, so there is no rounding to
//!    argue about and no precision lane to declare. Every witness must agree
//!    *exactly* or one of them is broken.
//! 2. **The T terms cancel.** `20 - 30 + 10 = 0`. So the machine really does
//!    three multiplications whose entire contribution is zero, and the answer
//!    survives. If any witness gets the multiply, the sign, or the order
//!    wrong, the T term stops cancelling and the answer is not 2.
//! 3. **It is the cave's own law.** `chi = 2` is AXIOM 01. This is that axiom
//!    executed as raw machine code.
//!
//! ## The witnesses
//!
//! | # | witness | who chose the instructions |
//! |---|---|---|
//! | 1 | **raw machine code** | *we did* -- 23 bytes, hand-encoded, handed to the CPU |
//! | 2 | **inline assembly** | we wrote the mnemonics; LLVM only encoded them |
//! | 3 | **safe Rust** | rustc/LLVM chose everything |
//! | 4 | Python | CPython's bytecode interpreter |
//! | 5 | JavaScript | V8's JIT |
//! | 6 | C# | RyuJIT |
//! | 7 | browser JS | whatever the browser brought |
//!
//! Witness 1 is the floor. There is no compiler under it -- the bytes in the
//! array are the bytes the processor decodes. If witness 1 and witness 3
//! agree, then rustc did not mistranslate this identity; and if all seven
//! agree, the identity is not an artifact of any one toolchain.
//!
//! ## Safety, stated plainly
//!
//! This crate is **UNTRUSTED** and uses `unsafe`. It allocates a page with
//! `PAGE_EXECUTE_READWRITE`, copies 23 bytes into it, and calls them. That is
//! genuinely dangerous in general; it is defensible here because the byte
//! sequence is fixed at compile time, fully listed below, 23 bytes long, takes
//! one integer, touches no memory, and ends in `ret`.
//!
//! The trusted kernel remains `#![forbid(unsafe_code)]`. Nothing here is
//! linked into it. See `RUSTIUM.md`, THE TITANS SPLIT.

use goldberg_kernel::goldberg_counts;
use gos_win32::{
    VirtualAlloc, VirtualFree, MEM_COMMIT, MEM_RELEASE, MEM_RESERVE, PAGE_EXECUTE_READWRITE,
};

// ---------------------------------------------------------------------------
// WITNESS 1 -- the raw machine code
// ---------------------------------------------------------------------------

/// x86-64, Microsoft x64 calling convention: argument `T` arrives in `RCX`,
/// the result leaves in `RAX`.
///
/// Every byte is derived below from the Intel encoding rules. Nothing here was
/// produced by an assembler -- this is the assembler's *output*, written by
/// hand, so that no tool sits between the intent and the silicon.
///
/// ```text
///  bytes         instruction            encoding rule
///  ----------------------------------------------------------------------
///  48 6B C1 14   imul rax, rcx, 20      REX.W(48) + 6B /r ib
///                                       ModRM C1 = 11 000 001 (reg=RAX, rm=RCX)
///                                       imm8 14 = 20            -> V = 20T
///  48 6B D1 1E   imul rdx, rcx, 30      ModRM D1 = 11 010 001 (reg=RDX, rm=RCX)
///                                       imm8 1E = 30            -> E = 30T
///  48 2B C2      sub  rax, rdx          REX.W + 2B /r
///                                       ModRM C2 = 11 000 010   -> V - E
///  48 6B D1 0A   imul rdx, rcx, 10      imm8 0A = 10            -> 10T
///  48 83 C2 02   add  rdx, 2            REX.W + 83 /0 ib
///                                       ModRM C2 = 11 000 010   -> F = 10T + 2
///  48 03 C2      add  rax, rdx          REX.W + 03 /r           -> chi
///  C3            ret
/// ```
///
/// 23 bytes. Three multiplications that cancel, one constant that does not.
#[rustfmt::skip]
const CHI_MACHINE_CODE: [u8; 23] = [
    0x48, 0x6B, 0xC1, 0x14, // imul rax, rcx, 20     V = 20T
    0x48, 0x6B, 0xD1, 0x1E, // imul rdx, rcx, 30     E = 30T
    0x48, 0x2B, 0xC2,       // sub  rax, rdx         V - E
    0x48, 0x6B, 0xD1, 0x0A, // imul rdx, rcx, 10     10T
    0x48, 0x83, 0xC2, 0x02, // add  rdx, 2           F = 10T + 2
    0x48, 0x03, 0xC2,       // add  rax, rdx         chi = V - E + F
    0xC3,                   // ret
];

/// A page of executable memory holding our bytes, freed on drop.
struct CodePage {
    ptr: *mut core::ffi::c_void,
}

impl CodePage {
    fn new(code: &[u8]) -> Option<Self> {
        // SAFETY: a fresh RWX page of one page size; we own it exclusively.
        let ptr = unsafe {
            VirtualAlloc(
                core::ptr::null_mut(),
                4096,
                MEM_COMMIT | MEM_RESERVE,
                PAGE_EXECUTE_READWRITE,
            )
        };
        if ptr.is_null() {
            return None;
        }
        // SAFETY: `ptr` is a valid 4096-byte writable region and `code` is 23
        // bytes, so the copy is in bounds and the regions cannot overlap.
        unsafe {
            core::ptr::copy_nonoverlapping(code.as_ptr(), ptr as *mut u8, code.len());
        }
        Some(CodePage { ptr })
    }

    /// Call the bytes.
    ///
    /// # Safety
    /// The page must contain a valid function with this exact signature that
    /// returns via `ret`. Ours does; it is listed byte by byte above.
    unsafe fn call(&self, t: i64) -> i64 {
        let f: extern "win64" fn(i64) -> i64 = core::mem::transmute(self.ptr);
        f(t)
    }
}

impl Drop for CodePage {
    fn drop(&mut self) {
        // SAFETY: `ptr` came from VirtualAlloc with MEM_RESERVE and is freed once.
        unsafe {
            VirtualFree(self.ptr, 0, MEM_RELEASE);
        }
    }
}

// ---------------------------------------------------------------------------
// WITNESS 2 -- inline assembly (we choose the instructions, LLVM encodes them)
// ---------------------------------------------------------------------------

fn chi_inline_asm(t: i64) -> i64 {
    let chi: i64;
    // SAFETY: pure register arithmetic. No memory is read or written, the
    // stack is untouched, and the output depends only on the input -- which
    // is exactly what `pure, nomem, nostack` assert.
    unsafe {
        core::arch::asm!(
            "imul {v}, {t}, 20",   // V = 20T
            "imul {e}, {t}, 30",   // E = 30T
            "imul {f}, {t}, 10",   // 10T
            "add  {f}, 2",         // F = 10T + 2
            "sub  {v}, {e}",       // V - E
            "add  {v}, {f}",       // chi = V - E + F
            t = in(reg) t,
            v = out(reg) chi,
            e = out(reg) _,
            f = out(reg) _,
            options(pure, nomem, nostack),
        );
    }
    chi
}

// ---------------------------------------------------------------------------
// WITNESS 3 -- ordinary safe Rust. rustc chooses everything.
// ---------------------------------------------------------------------------

fn chi_rust(t: i64) -> i64 {
    let v = 20 * t;
    let e = 30 * t;
    let f = 10 * t + 2;
    v - e + f
}

// ---------------------------------------------------------------------------

/// The T values every witness is asked about: the real ladder T = 3*7^k, plus
/// edge cases the ladder never produces but the identity still covers.
const PROBES: [i64; 10] = [0, 1, 2, 3, 21, 147, 1029, 7203, 50421, 1_000_000];

/// The canonical one-line receipt every witness prints, so seven programs in
/// five languages can be compared with string equality instead of judgement.
fn canon(name: &str, f: impl Fn(i64) -> i64) -> String {
    let mut s = String::from(name);
    for t in PROBES {
        s.push_str(&format!("|{}:{}", t, f(t)));
    }
    s
}

fn main() {
    // `--canon` prints only the receipts, for run_all.ps1 to diff.
    if std::env::args().any(|a| a == "--canon") {
        let page = CodePage::new(&CHI_MACHINE_CODE).expect("VirtualAlloc");
        // SAFETY: the 23 bytes listed above.
        println!(
            "{}",
            canon("rust-machine-code", |t| unsafe { page.call(t) })
        );
        println!("{}", canon("rust-inline-asm", chi_inline_asm));
        println!("{}", canon("rust-safe", chi_rust));
        return;
    }

    println!("== THE 23 BYTES ==");
    println!("   what the processor actually decodes, in 1s and 0s:\n");
    let mnemonics = [
        (0, 4, "imul rax, rcx, 20    V = 20T"),
        (4, 4, "imul rdx, rcx, 30    E = 30T"),
        (8, 3, "sub  rax, rdx        V - E"),
        (11, 4, "imul rdx, rcx, 10    10T"),
        (15, 4, "add  rdx, 2          F = 10T + 2"),
        (19, 3, "add  rax, rdx        chi"),
        (22, 1, "ret"),
    ];
    for (off, len, text) in mnemonics {
        let bits: Vec<String> = CHI_MACHINE_CODE[off..off + len]
            .iter()
            .map(|b| format!("{b:08b}"))
            .collect();
        let hex: Vec<String> = CHI_MACHINE_CODE[off..off + len]
            .iter()
            .map(|b| format!("{b:02X}"))
            .collect();
        println!("   {:<36}  {:<12}  {}", bits.join(" "), hex.join(" "), text);
    }
    println!("\n   184 bits. no compiler under this.\n");

    // ---- the seven-way comparison -----------------------------------------
    let page = CodePage::new(&CHI_MACHINE_CODE).expect("VirtualAlloc must give us a page");

    println!("== THE WITNESSES (this binary's three) ==");
    println!(
        "{:>9}  {:>12} {:>12} {:>12}  verdict",
        "T", "raw bytes", "inline asm", "safe rust"
    );
    println!("{}", "-".repeat(80));

    let mut all_agree = true;
    for t in PROBES {
        // SAFETY: the page holds the 23 bytes listed above, an extern "win64"
        // fn(i64) -> i64 that touches no memory.
        let a = unsafe { page.call(t) };
        let b = chi_inline_asm(t);
        let c = chi_rust(t);
        let agree = a == 2 && b == 2 && c == 2;
        all_agree &= agree;
        println!(
            "{t:>9}  {a:>12} {b:>12} {c:>12}  {}",
            if agree { "chi = 2" } else { "*** SPLIT ***" }
        );
    }

    // ---- and against the kernel's own closed form -------------------------
    println!("\n== AGAINST THE TRUSTED KERNEL (goldberg_counts, safe, no unsafe) ==");
    println!(
        "{:>6} {:>8} {:>10} {:>10} {:>10} {:>5}",
        "k", "T", "V", "E", "F", "chi"
    );
    println!("{}", "-".repeat(56));
    for k in 0..6u32 {
        let c = goldberg_counts(k);
        let t = (c.f as i64 - 2) / 10;
        // SAFETY: as above.
        let raw = unsafe { page.call(t) };
        assert_eq!(raw as i64, c.chi, "the metal and the kernel must agree");
        assert_eq!(c.p, 12);
        println!(
            "{k:>6} {t:>8} {:>10} {:>10} {:>10} {:>5}",
            c.v, c.e, c.f, c.chi
        );
    }

    println!("\n== VERDICT ==");
    if all_agree {
        println!("   3 of 3 in-process witnesses agree: chi = 2 for every probe.");
        println!("   the raw bytes and the trusted kernel agree at k = 0..5.");
    } else {
        println!("   *** WITNESSES DISAGREE -- this is the interesting case ***");
        std::process::exit(1);
    }
    println!("\n   run witnesses/run_all.ps1 for Python, JavaScript, C# and the browser.");
    println!("\n   20 - 30 + 10 = 0.  the T terms cancel.  what is left is 2.");
}
