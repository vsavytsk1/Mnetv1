//! EML -- the one-operator language, and a generator that searches its terms.
//!
//! From `shell__eml_luca_spiral_v0_2.html` (EML annex, arXiv:2603.21852):
//!
//! ```text
//!   eml(x, y) = exp(x) - ln(y)          the single operator
//!   S -> 1 | eml(S, S)                  the entire grammar
//! ```
//!
//! One binary operator and one constant. Every mathematical symbol is a
//! **descent**: a closed term in that grammar. The LUCA spiral shows 33 of them:
//!
//! ```text
//!   e      = eml(1,1)                        K = 2
//!   exp z  = eml(z,1)                        K = 2
//!   ln z   = eml(1, eml(eml(1,z), 1))        K = 4      paper says 7
//!   x - y  = eml(ln x, exp y)                K = 6
//!   -1     = minus(1)                        K = 11     paper: 15 / 17
//! ```
//!
//! **K is the price**: the number of `eml` applications a symbol costs. Two of
//! the sim's chains already beat the paper's, which is the whole invitation --
//! the descents are not unique, and a shorter one is a real finding.
//!
//! # Why this is a generator
//!
//! > "each latexium symbol is a process or a combination ... so each permutation
//! > we try we also log it and treat it as a generator ... we will test the
//! > known ones and find new ones"
//!
//! Closed terms of size `n` are counted by the **Catalan numbers**
//! `1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796, ...` -- so the whole space
//! through `K = 12` is a few hundred thousand terms. Exhaustible. This module
//! enumerates them in order of increasing price, evaluates each over `C`, and
//! reports every value it lands on.
//!
//! # The honest boundary
//!
//! Evaluation is the **DISPLAY** lane: `exp` and `ln` are not correctly rounded
//! and the branch cut is a choice, so two terms are called equal within a stated
//! tolerance, never bit-for-bit. A hit is therefore *evidence of* a descent, not
//! a proof of one -- the sim verifies its chains numerically at many samples for
//! exactly this reason. A match here says "look at this term", not "theorem".

use crate::complex::C;

/// A closed term in `S -> 1 | eml(S, S)`.
#[derive(Clone, PartialEq, Debug)]
pub enum Term {
    /// the terminal `1`
    One,
    /// `eml(a, b) = exp(a) - ln(b)`
    Eml(Box<Term>, Box<Term>),
}

impl Term {
    /// Raw count of `eml` applications in this term.
    ///
    /// **Not** the spiral's `K` -- see [`Term::k`]. Kept separate because
    /// comparing a count against another convention without establishing that
    /// convention first is how R3 and R11 happened, and it happened again here:
    /// the first run of this generator reported `e` at "K=1, SHORTER THAN
    /// KNOWN" against the spiral's 2. It was not shorter. It was the same term
    /// measured with a different ruler.
    pub fn applications(&self) -> usize {
        match self {
            Term::One => 0,
            Term::Eml(a, b) => 1 + a.applications() + b.applications(),
        }
    }

    /// `K` in the LUCA spiral's convention: **applications + 1**.
    ///
    /// Derived from its own table, not assumed:
    ///
    /// ```text
    ///   e   = eml(1,1)                  1 application   spiral K = 2
    ///   ln  = eml(1,eml(eml(1,z),1))    3 applications  spiral K = 4
    ///   sub = eml(ln x, exp y)          5 expanded      spiral K = 6
    ///   minus = sub(sub(1,z),1)        10 expanded      spiral K = 11
    /// ```
    ///
    /// Four independent rows, one rule. Any comparison against the spiral's
    /// numbers must use THIS, or it is comparing rulers rather than terms.
    pub fn k(&self) -> usize {
        self.applications() + 1
    }

    /// DISPLAY lane. `exp` and `ln` are not bit-portable; `ln 0 = -inf` is
    /// deliberate (the extended-reals lane the descents ride).
    pub fn eval(&self) -> C {
        match self {
            Term::One => C::ONE,
            Term::Eml(a, b) => {
                let x = a.eval();
                let y = b.eval();
                x.exp() - y.ln()
            }
        }
    }

    /// `eml(eml(1,1), 1)` -- the shape the spiral prints.
    pub fn to_chain(&self) -> String {
        match self {
            Term::One => String::from("1"),
            Term::Eml(a, b) => format!("eml({},{})", a.to_chain(), b.to_chain()),
        }
    }
}

/// Catalan number `C_n` -- how many closed terms have exactly `n` `eml` nodes.
pub fn catalan(n: usize) -> u64 {
    let mut c: u64 = 1;
    for i in 0..n as u64 {
        c = c * 2 * (2 * i + 1) / (i + 2);
    }
    c
}

/// Every closed term with exactly `n` `eml` applications.
///
/// `eml` is **non-commutative** (`exp(x) - ln(y)`), so `eml(a,b)` and
/// `eml(b,a)` are different terms and both are enumerated. That is why the
/// count is Catalan and not something smaller.
pub fn terms_of_size(n: usize, cache: &mut Vec<Vec<Term>>) -> Vec<Term> {
    if let Some(v) = cache.get(n) {
        if !v.is_empty() || n == 0 {
            return v.clone();
        }
    }
    while cache.len() <= n {
        cache.push(Vec::new());
    }
    if n == 0 {
        cache[0] = vec![Term::One];
        return cache[0].clone();
    }
    let mut out = Vec::new();
    for i in 0..n {
        let left = terms_of_size(i, cache);
        let right = terms_of_size(n - 1 - i, cache);
        for a in &left {
            for b in &right {
                out.push(Term::Eml(Box::new(a.clone()), Box::new(b.clone())));
            }
        }
    }
    cache[n] = out.clone();
    out
}

/// A value worth recognising when a term lands on it.
pub struct Target {
    pub sym: &'static str,
    pub name: &'static str,
    pub value: f64,
    /// the shortest K currently known, from the LUCA spiral's own table
    pub known_k: Option<usize>,
}

/// The constants the spiral names, plus a few the cave cares about.
///
/// `known_k` is what `shell__eml_luca_spiral_v0_2.html` reports for its chain.
/// Anything found BELOW that number is a shorter descent -- a finding.
pub const TARGETS: &[Target] = &[
    Target {
        sym: "e",
        name: "Euler's number",
        value: std::f64::consts::E,
        known_k: Some(2),
    },
    Target {
        sym: "1",
        name: "the terminal",
        value: 1.0,
        known_k: Some(0),
    },
    Target {
        sym: "0",
        name: "zero",
        value: 0.0,
        known_k: None,
    },
    Target {
        sym: "-1",
        name: "negative one",
        value: -1.0,
        known_k: Some(11),
    },
    Target {
        sym: "2",
        name: "two",
        value: 2.0,
        known_k: Some(16),
    },
    Target {
        sym: "3",
        name: "three",
        value: 3.0,
        known_k: None,
    },
    Target {
        sym: "1/e",
        name: "reciprocal of e",
        value: 1.0 / std::f64::consts::E,
        known_k: None,
    },
    Target {
        sym: "pi",
        name: "pi",
        value: std::f64::consts::PI,
        known_k: None,
    },
    Target {
        sym: "phi",
        name: "the golden ratio",
        value: crate::PHI,
        known_k: None,
    },
    Target {
        sym: "e^e",
        name: "e to the e",
        value: 15.154_262_241_479_262,
        known_k: None,
    },
    Target {
        sym: "ln2",
        name: "ln 2",
        value: std::f64::consts::LN_2,
        known_k: None,
    },
    Target {
        sym: "sqrt2",
        name: "root two",
        value: std::f64::consts::SQRT_2,
        known_k: None,
    },
];

/// One enumerated term and what it turned out to be.
pub struct Hit {
    pub k: usize,
    pub chain: String,
    pub value: C,
    /// which target it matched, if any
    pub target: Option<&'static str>,
    /// true when this beats the known K for that target
    pub shorter: bool,
}

/// Report of a full sweep. Every term is counted; only hits are kept.
pub struct Sweep {
    pub max_k: usize,
    pub terms_visited: u64,
    pub finite: u64,
    pub hits: Vec<Hit>,
    /// distinct finite real values seen, rounded to `tol` -- the "new ones"
    pub distinct_values: usize,
}

/// Search every closed term up to `max_k` applications.
///
/// Logs a hit whenever a term lands within `tol` of a [`TARGETS`] entry, and
/// flags it when the price is lower than the known chain.
pub fn sweep(max_k: usize, tol: f64) -> Sweep {
    let mut cache: Vec<Vec<Term>> = Vec::new();
    let mut hits: Vec<Hit> = Vec::new();
    let mut visited = 0u64;
    let mut finite = 0u64;
    let mut seen_values: Vec<f64> = Vec::new();
    // the cheapest K found so far for each target, so only IMPROVEMENTS log
    let mut best: Vec<Option<usize>> = vec![None; TARGETS.len()];

    // `n` counts APPLICATIONS; the spiral's K is n+1. Everything reported and
    // compared below is in the spiral's convention.
    for n in 0..=max_k.saturating_sub(1) {
        for t in terms_of_size(n, &mut cache) {
            visited += 1;
            let v = t.eval();
            if !v.is_finite() {
                continue;
            }
            finite += 1;
            let k = t.k();

            // real-valued? the constants we chase are real
            if v.im.abs() < tol {
                if !seen_values.iter().any(|&s| (s - v.re).abs() < tol) {
                    seen_values.push(v.re);
                }
                for (i, tg) in TARGETS.iter().enumerate() {
                    if (v.re - tg.value).abs() < tol && best[i].is_none() {
                        best[i] = Some(k);
                        let shorter = tg.known_k.map(|kk| k < kk).unwrap_or(false);
                        hits.push(Hit {
                            k,
                            chain: t.to_chain(),
                            value: v,
                            target: Some(tg.sym),
                            shorter,
                        });
                    }
                }
            }
        }
    }

    Sweep {
        max_k,
        terms_visited: visited,
        finite,
        hits,
        distinct_values: seen_values.len(),
    }
}
