//! THE CASCADE -- 'A' to the logic gates, and where the phase shift really is.
//!
//! > "2 logic gates do nothing.....like a million they do...so lets see that..
//! >  the critical phase shift"
//!
//! The intuition is right and the location is off by a lot, in the interesting
//! direction. The discontinuity is not at a million gates. **It is at one.**
//!
//! ```text
//!   NAND is FUNCTIONALLY COMPLETE.   Peirce 1880, Sheffer 1913.
//!   Every Boolean function of every arity is buildable from NAND alone.
//! ```
//!
//! That is a theorem, and theorems do not fade in gradually -- you cannot be
//! *partly* universal. So there are **two thresholds**, and only one of them is
//! a phase transition:
//!
//! ```text
//!   THRESHOLD 1   one gate TYPE      universality      DISCONTINUOUS, a theorem
//!   THRESHOLD 2   ~10^2..10^10       usefulness        SMOOTH, an engineering slope
//! ```
//!
//! And a third wall that no amount of gates crosses: **combinational logic is
//! not Turing complete.** A DAG of gates computes one fixed function of its
//! inputs, forever. Turing completeness needs a cycle -- memory, state, a clock.
//! That is a change of TOPOLOGY (acyclic to cyclic), not of scale.
//!
//! # Logic gates are graph math
//!
//! Exactly, and precisely: a combinational circuit **is** a directed acyclic
//! graph. Gates are nodes, wires are edges, DEPTH is the critical path
//! (latency), WIDTH is parallelism, fan-in and fan-out are degree. The same
//! language the judge speaks.
//!
//! ```powershell
//! cargo run --release --example gate_cascade
//! ```

use goldberg_kernel::font;
use goldberg_kernel::layout::Rect;
use goldberg_kernel::palette::{Palette, Rgb, DASHBOARD};
use goldberg_kernel::raster::Canvas;

const W: usize = 1500;
const H: usize = 1040;

/// One rung of the cascade. Every count is DERIVED below, never typed twice.
struct Rung {
    layer: &'static str,
    what: &'static str,
    /// NAND gates required, when the rung is made of gates
    nands: Option<u64>,
    /// CMOS transistors: 4 per NAND
    trans: Option<u64>,
    detail: String,
    /// EXACT / DESIGN / PHYSICS / SOCIAL / THEOREM / HYPOTHESIS
    status: &'static str,
}

/// CMOS NAND: 2 PMOS in parallel + 2 NMOS in series.
const TRANSISTORS_PER_NAND: u64 = 4;
/// XOR from NAND alone.
const NAND_PER_XOR: u64 = 4;
/// half adder = XOR + AND; AND = NAND + NOT(NAND) = 2.
const NAND_PER_HALF_ADDER: u64 = NAND_PER_XOR + 2;
/// the classic 9-NAND full adder.
const NAND_PER_FULL_ADDER: u64 = 9;

fn main() -> std::io::Result<()> {
    let byte_add = 8 * NAND_PER_FULL_ADDER;
    let word_add = 64 * NAND_PER_FULL_ADDER;

    let rungs = vec![
        Rung {
            layer: "0  THE GLYPH",
            what: "'A'",
            nands: None,
            trans: None,
            detail: String::from("a shape people agreed on. no mathematics yet."),
            status: "SOCIAL",
        },
        Rung {
            layer: "1  THE CODEPOINT",
            what: "65",
            nands: None,
            trans: None,
            detail: String::from("ASCII. a LOOKUP TABLE someone chose in 1963. 'A'=65 is not derived."),
            status: "DESIGN",
        },
        Rung {
            layer: "2  THE BITS",
            what: "0100 0001",
            nands: None,
            trans: None,
            detail: String::from("base 2 of 65. EXACT -- the only step so far that is forced."),
            status: "EXACT",
        },
        Rung {
            layer: "3  THE VOLTAGE",
            what: "8 x (HIGH | LOW)",
            nands: None,
            trans: None,
            detail: String::from("a bit becomes a voltage across a threshold. PHYSICS, not math."),
            status: "PHYSICS",
        },
        Rung {
            layer: "4  THE SWITCH",
            what: "1 transistor",
            nands: None,
            trans: Some(1),
            detail: String::from("a gate voltage opens a channel. alone it computes NOTHING."),
            status: "PHYSICS",
        },
        Rung {
            layer: "5  THE GATE",
            what: "NAND",
            nands: Some(1),
            trans: Some(TRANSISTORS_PER_NAND),
            detail: format!(
                "{} transistors. *** FUNCTIONALLY COMPLETE *** every boolean function, from this alone.",
                TRANSISTORS_PER_NAND
            ),
            status: "THEOREM",
        },
        Rung {
            layer: "6  XOR",
            what: "difference",
            nands: Some(NAND_PER_XOR),
            trans: Some(NAND_PER_XOR * TRANSISTORS_PER_NAND),
            detail: String::from("the first gate that ANSWERS something: are these two bits unequal?"),
            status: "EXACT",
        },
        Rung {
            layer: "7  HALF ADDER",
            what: "1 bit + 1 bit",
            nands: Some(NAND_PER_HALF_ADDER),
            trans: Some(NAND_PER_HALF_ADDER * TRANSISTORS_PER_NAND),
            detail: String::from("XOR gives the sum, AND gives the carry. arithmetic, from switches."),
            status: "EXACT",
        },
        Rung {
            layer: "8  FULL ADDER",
            what: "+ carry in",
            nands: Some(NAND_PER_FULL_ADDER),
            trans: Some(NAND_PER_FULL_ADDER * TRANSISTORS_PER_NAND),
            detail: String::from("now they CHAIN. the carry is what makes width possible."),
            status: "EXACT",
        },
        Rung {
            layer: "9  BYTE ADDER",
            what: "'A' + 'B'",
            nands: Some(byte_add),
            trans: Some(byte_add * TRANSISTORS_PER_NAND),
            detail: format!(
                "8 full adders = {} NAND = {} transistors. THE FIRST CALCULATOR.",
                byte_add,
                byte_add * TRANSISTORS_PER_NAND
            ),
            status: "EXACT",
        },
        Rung {
            layer: "10 WORD ADDER",
            what: "64-bit",
            nands: Some(word_add),
            trans: Some(word_add * TRANSISTORS_PER_NAND),
            detail: format!("{} NAND. still ONE FIXED FUNCTION. still not a computer.", word_add),
            status: "EXACT",
        },
        Rung {
            layer: "11 THE CYCLE",
            what: "+ memory, + clock",
            nands: None,
            trans: None,
            detail: String::from("a WIRE GOES BACKWARD. acyclic -> cyclic. THIS is the second threshold."),
            status: "THEOREM",
        },
        Rung {
            layer: "12 THE CHIP",
            what: "Ryzen 5 5600H",
            nands: None,
            trans: Some(10_700_000_000),
            detail: String::from("~10.7e9 transistors (vendor figure, NOT measured here). the slope, not a jump."),
            status: "CITED",
        },
    ];

    // ---- console ----------------------------------------------------------
    println!("{}", "=".repeat(94));
    println!("  THE CASCADE -- 'A' to the gates");
    println!("{}", "=".repeat(94));
    println!(
        "  {:<18} {:<18} {:>10} {:>14}  {}",
        "layer", "what", "NAND", "transistors", "status"
    );
    println!("  {}", "-".repeat(90));
    for r in &rungs {
        println!(
            "  {:<18} {:<18} {:>10} {:>14}  {}",
            r.layer,
            r.what,
            r.nands.map(|n| n.to_string()).unwrap_or_else(|| String::from("-")),
            r.trans.map(|n| n.to_string()).unwrap_or_else(|| String::from("-")),
            r.status
        );
    }
    println!();
    println!("  THRESHOLD 1  one gate TYPE     -> UNIVERSALITY   discontinuous, a theorem");
    println!("  THRESHOLD 2  ~10^2 .. 10^10    -> USEFULNESS     smooth, an engineering slope");
    println!("  THRESHOLD 3  a backward wire   -> COMPUTATION    a change of TOPOLOGY, not scale");
    println!();
    println!(
        "  'A'+'B' costs {} NAND = {} transistors.",
        byte_add,
        byte_add * TRANSISTORS_PER_NAND
    );
    println!(
        "  a 5600H holds ~{:.0} MILLION byte-adders' worth of transistors.",
        10_700_000_000f64 / (byte_add * TRANSISTORS_PER_NAND) as f64 / 1e6
    );

    // ---- paint ------------------------------------------------------------
    let pal = DASHBOARD;
    let mut cv = Canvas::new(W, H, pal.bg);
    header(&mut cv, &pal);

    let col = Rect::new(30, 96, 900, H as i32 - 190);
    let rh = col.h / rungs.len() as i32;

    for (i, r) in rungs.iter().enumerate() {
        let y = col.y + i as i32 * rh;
        let box_r = Rect::new(col.x, y, col.w, rh - 6);
        draw_rung(&mut cv, &pal, box_r, r, i);
        if i + 1 < rungs.len() {
            arrow(&mut cv, &pal, col.x + 70, box_r.bottom(), rh - box_r.h + 6);
        }
    }

    thresholds(&mut cv, &pal, Rect::new(960, 96, W as i32 - 990, H as i32 - 190), byte_add);
    footer(&mut cv, &pal);

    cv.write_png("gate_cascade.png")?;
    println!("\nwrote gate_cascade.png   seal {:016x}", cv.digest());
    Ok(())
}

fn status_colour(pal: &Palette, s: &str) -> Rgb {
    match s {
        "EXACT" => pal.green,
        "THEOREM" => pal.gold,
        "PHYSICS" => pal.purple,
        "DESIGN" => pal.orange,
        "SOCIAL" => pal.pink,
        _ => pal.text,
    }
}

fn draw_rung(cv: &mut Canvas, pal: &Palette, r: Rect, rung: &Rung, i: usize) {
    let accent = status_colour(pal, rung.status);
    // the two theorem rungs are the ones that matter -- give them the border
    let is_key = rung.status == "THEOREM";
    cv.fill_rect(r.x, r.y, r.w, r.h, if is_key { [0x10, 0x0e, 0x06] } else { pal.panel });
    cv.rect(r.x, r.y, r.w, r.h, if is_key { accent } else { pal.border });

    font::text(cv, r.x + 10, r.y + 6, rung.layer, accent, 1);
    font::text(cv, r.x + 168, r.y + 4, rung.what, pal.bright, if is_key { 2 } else { 1 });

    // counts, right-aligned
    if let Some(n) = rung.nands {
        let s = format!("{n} NAND");
        font::text(cv, r.right() - 210 - font::width(&s, 1), r.y + 6, &s, pal.cyan, 1);
    }
    if let Some(t) = rung.trans {
        let s = if t >= 1_000_000 {
            format!("{:.1}e9 TR", t as f64 / 1e9)
        } else {
            format!("{t} TR")
        };
        font::text(cv, r.right() - 90 - font::width(&s, 1), r.y + 6, &s, pal.gold, 1);
    }
    let st = rung.status;
    font::text(cv, r.right() - 8 - font::width(st, 1), r.y + 6, st, accent, 1);

    font::text(cv, r.x + 10, r.y + 20, &rung.detail.to_uppercase(), [0x4a, 0x5a, 0x6a], 1);
    let _ = i;
}

fn arrow(cv: &mut Canvas, pal: &Palette, x: i32, y: i32, h: i32) {
    for t in 0..h {
        cv.set(x, y + t, pal.border);
    }
    cv.set(x - 1, y + h - 3, pal.border);
    cv.set(x + 1, y + h - 3, pal.border);
}

fn thresholds(cv: &mut Canvas, pal: &Palette, r: Rect, byte_add: u64) {
    cv.fill_rect(r.x, r.y, r.w, r.h, pal.panel);
    cv.rect(r.x, r.y, r.w, r.h, pal.border);
    let mut y = r.y + 12;

    font::text(cv, r.x + 12, y, "THE THREE THRESHOLDS", pal.gold, 2);
    y += 30;

    let blocks: [(&str, Rgb, &[&str]); 3] = [
        (
            "1  UNIVERSALITY",
            pal.gold,
            &[
                "ONE GATE TYPE. NAND ALONE BUILDS",
                "EVERY BOOLEAN FUNCTION.",
                "PEIRCE 1880 / SHEFFER 1913.",
                "",
                "DISCONTINUOUS. A THEOREM.",
                "YOU CANNOT BE PARTLY UNIVERSAL.",
                "THE JUMP IS AT 1, NOT A MILLION.",
            ],
        ),
        (
            "2  USEFULNESS",
            pal.cyan,
            &[
                "SCALE BUYS NOTHING NEW IN KIND,",
                "ONLY IN REACH.",
                "",
                "72 NAND ADD TWO LETTERS.",
                "576 NAND ADD TWO WORDS.",
                "1E10 RUNS A LAPTOP.",
                "",
                "SMOOTH. AN ENGINEERING SLOPE.",
            ],
        ),
        (
            "3  COMPUTATION",
            pal.pink,
            &[
                "A DAG OF GATES COMPUTES ONE",
                "FIXED FUNCTION, FOREVER, NO",
                "MATTER HOW MANY GATES.",
                "",
                "TURING NEEDS A CYCLE:",
                "A WIRE THAT GOES BACKWARD.",
                "",
                "ACYCLIC -> CYCLIC.",
                "A CHANGE OF TOPOLOGY,",
                "NOT OF SCALE.",
            ],
        ),
    ];

    for (title, c, lines) in blocks {
        font::text(cv, r.x + 12, y, title, c, 1);
        y += 14;
        for l in lines {
            font::text(cv, r.x + 12, y, l, if l.is_empty() { pal.text } else { [0x6a, 0x7a, 0x8a] }, 1);
            y += 10;
        }
        y += 10;
    }

    y += 4;
    cv.line(r.x + 8, y, r.right() - 8, y, pal.border);
    y += 12;
    font::text(cv, r.x + 12, y, "GATES ARE GRAPH MATH", pal.green, 1);
    y += 14;
    for l in [
        "A CIRCUIT IS A DAG.",
        "GATES = NODES. WIRES = EDGES.",
        "DEPTH = LATENCY.",
        "WIDTH = PARALLELISM.",
        "FAN-IN / FAN-OUT = DEGREE.",
        "",
        &format!("'A'+'B' = {byte_add} NODES."),
    ] {
        font::text(cv, r.x + 12, y, l, [0x6a, 0x7a, 0x8a], 1);
        y += 10;
    }
}

fn header(cv: &mut Canvas, pal: &Palette) {
    font::text(cv, 30, 22, "THE CASCADE", pal.gold, 2);
    font::text(
        cv,
        30 + font::width("THE CASCADE", 2) + 18,
        28,
        "ONE GLYPH, ALL THE WAY DOWN TO THE SWITCHES",
        pal.pink,
        1,
    );
    font::text(
        cv,
        30,
        48,
        "EVERY COUNT BELOW IS DERIVED FROM 4 TRANSISTORS PER NAND, 4 NAND PER XOR, 9 NAND PER FULL ADDER.",
        pal.text,
        1,
    );
    font::text(
        cv,
        30,
        62,
        "STATUS IS PART OF THE DIAGRAM: SOCIAL = AGREED. DESIGN = CHOSEN. EXACT = FORCED. PHYSICS = MEASURED. THEOREM = PROVED.",
        [0x4a, 0x5a, 0x6a],
        1,
    );
}

fn footer(cv: &mut Canvas, pal: &Palette) {
    let y = H as i32 - 78;
    font::text(
        cv,
        30,
        y,
        "THE HONEST BOUNDARY: 'CRITICAL MASS OF INFORMATION LOCKS INTO A HIGHER SYMMETRY' IS A HYPOTHESIS, NOT A RESULT ON THIS PAGE.",
        pal.orange,
        1,
    );
    font::text(
        cv,
        30,
        y + 12,
        "WHAT IS PROVED HERE: FUNCTIONAL COMPLETENESS AT ONE GATE TYPE, AND THAT NO AMOUNT OF ACYCLIC GATES REACHES TURING.",
        [0x4a, 0x5a, 0x6a],
        1,
    );
    font::text(
        cv,
        30,
        y + 24,
        "THE STANDARD MODEL PARALLEL IS AN ANALOGY. GAUGE SYMMETRY BREAKING IS A SPECIFIC MECHANISM, NOT A GENERAL LAW OF SCALE.",
        [0x4a, 0x5a, 0x6a],
        1,
    );
    font::text(
        cv,
        30,
        y + 40,
        "P=12 . CHI=2 . THE PRICE IS ALWAYS PAID . ALWAYS",
        pal.gold,
        1,
    );
}
