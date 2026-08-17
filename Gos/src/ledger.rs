//! THE LEDGER -- the cave's logger. Zero dependencies, like everything else.
//!
//! A logger that only prints strings is a diary. This one enforces the laws it
//! reports, because the laws are all about what gets *shown*:
//!
//! * **Curse 26 / Path III** -- target, current and error are printed side by
//!   side, always. A checker that can only say PASS is a checker that can print
//!   the target and call it the result. [`Ledger::check_eq`] and
//!   [`Ledger::check_near`] cannot do that: they take both numbers.
//! * **RULE 0** -- every line is tagged [`Lane::Certified`] or
//!   [`Lane::Display`]. An exact assertion on the display lane is a category
//!   error, and it is visible in the output.
//! * **Curse 35** -- [`Ledger::predict`] compares the next step's cost to a
//!   budget *before* allocating, and refuses out loud with the number.
//! * **Curse 38** -- no wall clock. Elapsed time comes from a monotonic
//!   [`Instant`] and is display-only; nothing here ever enters a hash.
//! * **Curse 2** -- ASCII output only. No glyphs to rot.
//!
//! Level comes from the `GOS_LOG` environment variable
//! (`silent` | `halt` | `warn` | `note` | `trace`), defaulting to `note`.
//!
//! ```
//! use goldberg_kernel::ledger::{Ledger, Lane};
//! let mut led = Ledger::silent();          // quiet, for doctests
//! led.check_eq(Lane::Certified, "P", 12usize, 12usize);
//! led.check_near(Lane::Display, "radius", 1.0, 1.0 + 1e-15, 1e-12);
//! assert!(led.sealed_ok());
//! assert_eq!(led.passed(), 2);
//! ```

use std::fmt;
use std::time::Instant;

/// Which side of RULE 0 a value lives on.
#[derive(Clone, Copy, PartialEq, Eq, Debug)]
pub enum Lane {
    /// Integers, and f64 restricted to `+ - * / sqrt`. Bit-identical to the
    /// browser. Compared with exact equality.
    Certified,
    /// Anything transcendental. Compared with a tolerance, never a bit.
    Display,
}

impl Lane {
    fn tag(self) -> &'static str {
        match self {
            Lane::Certified => "CERT",
            Lane::Display => "DISP",
        }
    }
}

/// Verbosity. `Silent` prints nothing but still counts.
#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Debug)]
pub enum Level {
    Silent = 0,
    Halt = 1,
    Warn = 2,
    Note = 3,
    Trace = 4,
}

impl Level {
    fn from_env() -> Level {
        match std::env::var("GOS_LOG").unwrap_or_default().to_lowercase().as_str() {
            "silent" | "off" | "0" => Level::Silent,
            "halt" | "error" => Level::Halt,
            "warn" => Level::Warn,
            "trace" | "debug" => Level::Trace,
            _ => Level::Note,
        }
    }
}

/// A running record of checks, with a verdict at the end.
pub struct Ledger {
    level: Level,
    t0: Instant,
    passed: usize,
    failed: usize,
    refused: usize,
}

impl Default for Ledger {
    fn default() -> Ledger {
        Ledger::new()
    }
}

impl Ledger {
    /// Level from `GOS_LOG`, defaulting to `note`.
    pub fn new() -> Ledger {
        Ledger::with_level(Level::from_env())
    }

    /// Counts everything, prints nothing. What tests use.
    pub fn silent() -> Ledger {
        Ledger::with_level(Level::Silent)
    }

    pub fn with_level(level: Level) -> Ledger {
        Ledger {
            level,
            t0: Instant::now(),
            passed: 0,
            failed: 0,
            refused: 0,
        }
    }

    pub fn passed(&self) -> usize {
        self.passed
    }
    pub fn failed(&self) -> usize {
        self.failed
    }
    pub fn refused(&self) -> usize {
        self.refused
    }

    /// True when nothing failed and nothing was refused.
    pub fn sealed_ok(&self) -> bool {
        self.failed == 0 && self.refused == 0
    }

    fn say(&self, at: Level, line: &str) {
        if self.level >= at {
            println!("{line}");
        }
    }

    /// A plain note. No verdict, no counter.
    pub fn note(&self, msg: &str) {
        self.say(Level::Note, &format!("       {msg}"));
    }

    /// A section header.
    pub fn section(&self, title: &str) {
        self.say(Level::Note, &format!("\n-- {title} {}", "-".repeat(62usize.saturating_sub(title.len()))));
    }

    /// An exact check. Target and current are both shown, always.
    ///
    /// On [`Lane::Display`] this is deliberately still available -- and the
    /// `DISP` tag in the output is the tell that someone is asserting a bit on
    /// a value that carries no bit guarantee.
    pub fn check_eq<T>(&mut self, lane: Lane, name: &str, target: T, current: T) -> bool
    where
        T: PartialEq + fmt::Debug,
    {
        let ok = target == current;
        if ok {
            self.passed += 1;
        } else {
            self.failed += 1;
        }
        self.say(
            if ok { Level::Note } else { Level::Halt },
            &format!(
                "  [{}] {:<34} target {:>16}  current {:>16}  {}",
                lane.tag(),
                name,
                format!("{target:?}"),
                format!("{current:?}"),
                if ok { "PASS" } else { "FAIL" }
            ),
        );
        ok
    }

    /// A tolerance check for the display lane. Prints the error, never hides it.
    pub fn check_near(&mut self, lane: Lane, name: &str, target: f64, current: f64, tol: f64) -> bool {
        let err = (current - target).abs();
        let ok = err <= tol;
        if ok {
            self.passed += 1;
        } else {
            self.failed += 1;
        }
        self.say(
            if ok { Level::Note } else { Level::Halt },
            &format!(
                "  [{}] {:<34} target {:>16.10}  current {:>16.10}  err {:>10.3e}  tol {:>8.1e}  {}",
                lane.tag(),
                name,
                target,
                current,
                err,
                tol,
                if ok { "PASS" } else { "FAIL" }
            ),
        );
        ok
    }

    /// Curse 35: predict the next step's cost from the recurrence and refuse
    /// LOUDLY, with the number, before allocating anything.
    ///
    /// Returns `false` when the step must not be taken.
    pub fn predict(&mut self, name: &str, predicted: u128, budget: u128) -> bool {
        let ok = predicted <= budget;
        if ok {
            self.passed += 1;
            self.say(
                Level::Trace,
                &format!("  [CERT] {name:<34} predicted {predicted:>16}  budget {budget:>16}  OK"),
            );
        } else {
            self.refused += 1;
            self.say(
                Level::Halt,
                &format!(
                    "  [HALT] {name:<34} predicted {predicted:>16}  budget {budget:>16}  REFUSED\n\
                              the math is fine past here; the MACHINE is what ends."
                ),
            );
        }
        ok
    }

    /// The verdict. Returns true if the ledger is clean.
    pub fn seal(&self) -> bool {
        let ok = self.sealed_ok();
        let total = self.passed + self.failed;
        self.say(
            Level::Halt,
            &format!(
                "\n{}\n  LEDGER  {}/{} checks passed{}  in {:.3}s  --  {}\n{}",
                "=".repeat(78),
                self.passed,
                total,
                if self.refused > 0 {
                    format!(", {} REFUSED", self.refused)
                } else {
                    String::new()
                },
                self.t0.elapsed().as_secs_f64(),
                if ok { "SEALED" } else { "BROKEN" },
                "=".repeat(78)
            ),
        );
        ok
    }
}
