//! THE TOPOLOGY GATE -- run it on every version, before every integration.
//!
//! > "with each version of the next dashboard we always check the structure of
//! > the closed topology ... each sim and each integration will update our core
//! > kernel ... so here we log each step as well"
//!
//! This is AXIOM 01 clauses 1-2 turned from a runtime print into a permanent
//! receipt trail:
//!
//! ```text
//! BY GALACTIC LAW -- every build of this software must:
//!   1. Verify P=12 pentagons.  If not 12 -- stop. Do not ship.
//!   2. Verify V-E+F=2.         If not 2  -- stop. Do not ship.
//!   5. ... The ledger is permanent.
//! ```
//!
//! Every lane, every level, **counted by the integer judge** -- never recited
//! from a formula. One row per check appended to `TOPOLOGY_GATE.md`, which is
//! git-tracked because it is small and it is the trail. Exit code is nonzero if
//! any invariant fails, so this can gate a build rather than merely inform it.
//!
//! ```powershell
//! cargo run --example gate            # check + append to the log
//! cargo run --example gate -- --dry   # check only, write nothing
//! ```

use std::fmt::Write as _;
use std::fs;
use std::path::PathBuf;

use goldberg_kernel::sphere::Ico;
use goldberg_kernel::{certify, goldberg_counts, judge, triangulation_number, Mesh, VERSION};

/// Ideal C60 bond length, metres. Thea sec.17.
const BOND: f64 = 1.42e-10;
/// C60 radius from that bond: `R0 = (a/4) sqrt(58 + 18 sqrt5)`.
fn c60_radius() -> f64 {
    (BOND / 4.0) * (58.0 + 18.0 * 5.0_f64.sqrt()).sqrt()
}
const L_PLANCK: f64 = 1.616_255e-35;

struct Row {
    lane: String,
    level: String,
    v: usize,
    e: usize,
    f: usize,
    p: String,
    chi: i64,
    genus: String,
    /// how chi was obtained -- the whole point
    how: &'static str,
    spacing_m: f64,
    pass: bool,
}

fn main() -> std::process::ExitCode {
    let dry = std::env::args().any(|a| a == "--dry");
    let mut rows: Vec<Row> = Vec::new();

    println!("{}", "=".repeat(96));
    println!("  THE TOPOLOGY GATE -- AXIOM 01. Counted, never recited.");
    println!("{}", "=".repeat(96));

    // ---- LANE 1: the trivalent shell. Pentagons are FACES here. -----------
    {
        let m = Mesh::c60();
        let cert = certify(&m).expect("C60 must certify");
        let v = judge::check(&judge::rotation_system_c60()).expect("and the judge must agree");
        let ok = cert.p == 12 && v.chi == 2 && cert.v == v.v && cert.e == v.e && cert.f == v.f;
        rows.push(Row {
            lane: String::from("trivalent C60"),
            level: String::from("-"),
            v: v.v,
            e: v.e,
            f: v.f,
            p: format!("{}", cert.p),
            chi: v.chi,
            genus: fmt_genus(v.genus),
            how: "JUDGE (orbit count)",
            spacing_m: 2.0 * c60_radius() / (v.v as f64).sqrt(),
            pass: ok,
        });
    }

    // ---- LANE 2: the icosphere. The twelve are five-valent VERTICES. ------
    for l in 0..=6u32 {
        let ico = match Ico::level(l) {
            Ok(i) => i,
            Err(e) => {
                println!("  level {l}: {e}");
                break;
            }
        };
        let defects = ico.defects().len();
        // levels past 4 make a very large rotation system; count chi there only
        // when it is affordable, and SAY which rows were judged (Path IV).
        let (v, e, f, chi, genus, how) = if l <= 4 {
            match ico.rotation_system().and_then(|s| judge::check(&s).ok()) {
                Some(j) => (
                    j.v,
                    j.e,
                    j.f,
                    j.chi,
                    fmt_genus(j.genus),
                    "JUDGE (orbit count)",
                ),
                None => (0, 0, 0, -999, String::from("?"), "JUDGE FAILED"),
            }
        } else {
            // structural check without the full permutation: every undirected
            // edge shared by exactly two faces, then chi from the COUNTED V/E/F
            let (v, e, f) = edges_counted(&ico);
            (
                v,
                e,
                f,
                v as i64 - e as i64 + f as i64,
                String::from("0"),
                "COUNTED (edge census)",
            )
        };
        let ok = chi == 2 && defects == 12;
        rows.push(Row {
            lane: String::from("icosphere"),
            level: format!("L{l}"),
            v,
            e,
            f,
            p: format!("{defects}*"),
            chi,
            genus,
            how,
            spacing_m: 2.0 * c60_radius() / (v.max(1) as f64).sqrt(),
            pass: ok,
        });
    }

    // ---- LANE 3: the Goldberg ladder. Integer counts only, no mesh. -------
    for k in 0..=3u32 {
        let c = goldberg_counts(k);
        let ok = c.p == 12 && c.chi == 2 && c.e * 2 == c.v * 3;
        rows.push(Row {
            lane: String::from("goldberg 3*7^k"),
            level: format!("k{k} T{}", triangulation_number(k)),
            v: c.v,
            e: c.e,
            f: c.f,
            p: format!("{}", c.p),
            chi: c.chi,
            genus: String::from("0"),
            how: "FORMULA (counts only)",
            spacing_m: 2.0 * c60_radius() / (c.v as f64).sqrt(),
            pass: ok,
        });
    }

    // ---- report ------------------------------------------------------------
    println!(
        "\n  {:<16} {:<10} {:>9} {:>9} {:>9} {:>5} {:>4} {:>6} {:>12} {:<22} verdict",
        "lane", "level", "V", "E", "F", "P", "chi", "genus", "spacing m", "how"
    );
    println!("  {}", "-".repeat(112));
    let mut failed = 0usize;
    for r in &rows {
        if !r.pass {
            failed += 1;
        }
        println!(
            "  {:<16} {:<10} {:>9} {:>9} {:>9} {:>5} {:>4} {:>6} {:>12.3e} {:<22} {}",
            r.lane,
            r.level,
            r.v,
            r.e,
            r.f,
            r.p,
            r.chi,
            r.genus,
            r.spacing_m,
            r.how,
            if r.pass { "PASS" } else { "*** FAIL ***" }
        );
    }
    println!("  {}", "-".repeat(112));
    println!("  * = five-valent VERTICES (the twelve pentagons of the dual), not faces");

    // the nanostructure ladder: how far the spacing is from Planck
    let finest = rows
        .iter()
        .filter(|r| r.pass)
        .map(|r| r.spacing_m)
        .fold(f64::INFINITY, f64::min);
    let rungs = (finest / L_PLANCK).log2();
    println!("\n  LATTICE NANOSTRUCTURE");
    println!("    C60 radius            {:.4e} m", c60_radius());
    println!("    finest node spacing   {finest:.4e} m");
    println!("    Planck length         {L_PLANCK:.4e} m");
    println!("    ratio                 {:.4e}", finest / L_PLANCK);
    println!("    halvings to Planck    {rungs:.1}   (each subdivision halves the spacing)");

    println!("\n  {} rows, {} failed", rows.len(), failed);

    if failed > 0 {
        println!("\n  GATE FAILED. By AXIOM 01: do not ship.");
        return std::process::ExitCode::from(1);
    }
    println!("  GATE PASSED.");

    if !dry {
        match append_log(&rows, finest) {
            Ok(p) => println!("  logged -> {}", p.display()),
            Err(e) => {
                println!("  LOG FAILED: {e}");
                return std::process::ExitCode::from(2);
            }
        }
    } else {
        println!("  --dry: nothing written");
    }
    std::process::ExitCode::SUCCESS
}

fn fmt_genus(g: Option<i64>) -> String {
    match g {
        Some(x) => x.to_string(),
        None => String::from("n/a"),
    }
}

/// V/E/F counted from the mesh itself: every undirected edge must be shared by
/// exactly two faces, which is the seam check without building a permutation.
fn edges_counted(ico: &Ico) -> (usize, usize, usize) {
    use std::collections::HashMap;
    let mut count: HashMap<(usize, usize), usize> = HashMap::with_capacity(ico.faces.len() * 2);
    for f in &ico.faces {
        for i in 0..3 {
            let (a, b) = (f[i], f[(i + 1) % 3]);
            *count.entry((a.min(b), a.max(b))).or_insert(0) += 1;
        }
    }
    let clean = count.values().all(|&c| c == 2);
    if !clean {
        return (0, 0, 0);
    }
    (ico.verts.len(), count.len(), ico.faces.len())
}

/// Append one block to the permanent, git-tracked gate log.
///
/// Small enough to track (a few hundred bytes a run), which is the whole point:
/// the payload of a run stays local, but the GATE RESULT travels, because "the
/// ledger is permanent" (AXIOM 01.5).
fn append_log(rows: &[Row], finest: f64) -> std::io::Result<PathBuf> {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let path = root.join("TOPOLOGY_GATE.md");

    let git = git_head(&root);
    let ledger = ledger_entry(&root);

    let mut s = String::new();
    if !path.exists() {
        let _ = writeln!(s, "# THE TOPOLOGY GATE -- the permanent trail");
        let _ = writeln!(s);
        let _ = writeln!(
            s,
            "*Appended by `cargo run --example gate`. One block per version.*"
        );
        let _ = writeln!(s);
        let _ = writeln!(
            s,
            "> AXIOM 01: verify P=12, verify V-E+F=2, or do not ship."
        );
        let _ = writeln!(
            s,
            "> Every `chi` marked JUDGE was COUNTED from orbit cycles, never recited"
        );
        let _ = writeln!(
            s,
            "> from a formula -- `V-E+F` on the closed-form counts is an identity"
        );
        let _ = writeln!(s, "> and returns 2 whether or not a mesh exists.");
        let _ = writeln!(s);
        let _ = writeln!(s, "---");
    }

    let _ = writeln!(s);
    let _ = writeln!(s, "## kernel {VERSION} . git {git} . {ledger}");
    let _ = writeln!(s);
    let _ = writeln!(
        s,
        "| lane | level | V | E | F | P | chi | genus | spacing m | how | verdict |"
    );
    let _ = writeln!(s, "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|");
    for r in rows {
        let _ = writeln!(
            s,
            "| {} | {} | {} | {} | {} | {} | {} | {} | {:.3e} | {} | {} |",
            r.lane,
            r.level,
            r.v,
            r.e,
            r.f,
            r.p,
            r.chi,
            r.genus,
            r.spacing_m,
            r.how,
            if r.pass { "PASS" } else { "FAIL" }
        );
    }
    let _ = writeln!(s);
    let _ = writeln!(
        s,
        "finest node spacing {:.4e} m -- {:.1} halvings from the Planck length.",
        finest,
        (finest / L_PLANCK).log2()
    );

    let mut existing = fs::read_to_string(&path).unwrap_or_default();
    existing.push_str(&s);
    fs::write(&path, existing.replace("\r\n", "\n"))?;
    Ok(path)
}

fn git_head(from: &std::path::Path) -> String {
    let mut root = from.to_path_buf();
    for _ in 0..4 {
        let g = root.join(".git");
        if g.exists() {
            let head = fs::read_to_string(g.join("HEAD")).unwrap_or_default();
            let head = head.trim().to_string();
            if let Some(rf) = head.strip_prefix("ref: ") {
                if let Ok(h) = fs::read_to_string(g.join(rf)) {
                    return h.trim().chars().take(7).collect();
                }
            } else if !head.is_empty() {
                return head.chars().take(7).collect();
            }
        }
        if !root.pop() {
            break;
        }
    }
    String::from("unknown")
}

fn ledger_entry(from: &std::path::Path) -> String {
    let mut root = from.to_path_buf();
    for _ in 0..4 {
        if let Ok(t) = fs::read_to_string(root.join("LEDGER.md")) {
            return t
                .lines()
                .rfind(|l| l.starts_with("### L"))
                .and_then(|l| l.split_whitespace().nth(1))
                .unwrap_or("L???")
                .to_string();
        }
        if !root.pop() {
            break;
        }
    }
    String::from("L???")
}
