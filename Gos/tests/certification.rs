//! Proof by kernel, not by claim.
//!
//! Every number here was produced by an independent derivation before the
//! Rust was written. If a test fails, the port changed the mathematics --
//! which is exactly what we want to hear about.

use goldberg_kernel::bits;
use goldberg_kernel::complex::{c_to_s2, C};
use goldberg_kernel::genesis::{Op, Params, State, Surface};
use goldberg_kernel::ladder;
use goldberg_kernel::ledger::{Lane, Ledger};
use goldberg_kernel::mobius;
use goldberg_kernel::netfile;
use goldberg_kernel::raster::Canvas;
use goldberg_kernel::rng::Rng;
use goldberg_kernel::*;

// ===========================================================================
// TOPOLOGY -- the C60 seed
// ===========================================================================

#[test]
fn c60_certifies() {
    let m = Mesh::c60();
    let c = certify(&m).expect("the C60 seed must certify");
    assert_eq!(c.v, 60, "V");
    assert_eq!(c.e, 90, "E");
    assert_eq!(c.f, 32, "F");
    assert_eq!(c.p, 12, "P -- Euler forces twelve pentagons");
    assert_eq!(c.h, 20, "H");
    assert_eq!(c.chi, 2, "chi -- the surface is a sphere");
}

#[test]
fn edge_ratio_is_three_halves() {
    let m = Mesh::c60();
    assert_eq!(m.edges.len() * 2, m.verts.len() * 3, "E/V must be 3/2");
}

#[test]
fn every_vertex_is_trivalent() {
    for (i, a) in Mesh::c60().adj.iter().enumerate() {
        assert_eq!(a.len(), 3, "vertex {i} has degree {}", a.len());
    }
}

#[test]
fn all_vertices_lie_on_the_unit_sphere() {
    for (i, v) in Mesh::c60().verts.iter().enumerate() {
        assert!(
            (vlen(*v) - 1.0).abs() < 1e-12,
            "vertex {i} is off the sphere by {}",
            (vlen(*v) - 1.0).abs()
        );
    }
}

#[test]
fn faces_are_only_pentagons_and_hexagons() {
    for f in &Mesh::c60().faces {
        assert!(
            f.len() == 5 || f.len() == 6,
            "found a {}-gon; a Goldberg polyhedron has only 5s and 6s",
            f.len()
        );
    }
}

#[test]
fn every_directed_edge_belongs_to_exactly_one_face() {
    let m = Mesh::c60();
    let mut count = std::collections::HashMap::new();
    for f in &m.faces {
        for i in 0..f.len() {
            *count.entry((f[i], f[(i + 1) % f.len()])).or_insert(0usize) += 1;
        }
    }
    assert_eq!(
        count.len(),
        180,
        "60 vertices x degree 3 = 180 directed edges"
    );
    for (k, v) in &count {
        assert_eq!(*v, 1, "directed edge {k:?} appears {v} times, expected 1");
    }
}

#[test]
fn centroid_of_a_symmetric_shell_is_the_origin() {
    let c = centroid(&Mesh::c60().verts);
    assert!(
        c.iter().all(|x| x.abs() < 1e-12),
        "C60 is centrally symmetric; its centroid is the origin, got {c:?}"
    );
}

#[test]
fn there_are_thirty_two_face_centers_all_on_the_sphere() {
    let fc = Mesh::c60().face_centers();
    assert_eq!(fc.len(), 32, "one dual vertex per face");
    for c in fc {
        assert!((vlen(c) - 1.0).abs() < 1e-12);
    }
}

/// The exact table printed by `builder/build_helena.py` into HELENA.md.
/// This is the port's contract with the browser build.
#[test]
fn goldberg_ladder_matches_the_helena_build_card() {
    let card = [
        (0u32, 12usize, 20usize, 32usize, 60usize, 90usize),
        (1, 12, 200, 212, 420, 630),
        (2, 12, 1460, 1472, 2940, 4410),
        (3, 12, 10280, 10292, 20580, 30870),
    ];
    for (level, p, h, f, v, e) in card {
        let c = goldberg_counts(level);
        assert_eq!(c.v, v, "V at level {level}");
        assert_eq!(c.e, e, "E at level {level}");
        assert_eq!(c.f, f, "F at level {level}");
        assert_eq!(c.p, p, "P at level {level}");
        assert_eq!(c.h, h, "H at level {level}");
        assert_eq!(c.chi, 2, "chi at level {level}");
        assert_eq!(c.e * 2, c.v * 3, "E/V at level {level}");
    }
}

#[test]
fn triangulation_number_multiplies_by_seven() {
    assert_eq!(triangulation_number(0), 3);
    assert_eq!(triangulation_number(1), 21);
    assert_eq!(triangulation_number(2), 147);
    assert_eq!(triangulation_number(3), 1029);
}

// ===========================================================================
// PRIMITIVES
// ===========================================================================

#[test]
fn vector_primitives() {
    let a: Vec3 = [1.0, 2.0, 3.0];
    let b: Vec3 = [4.0, 5.0, 6.0];
    assert_eq!(vadd(a, b), [5.0, 7.0, 9.0]);
    assert_eq!(vsub(b, a), [3.0, 3.0, 3.0]);
    assert_eq!(vscale(a, 2.0), [2.0, 4.0, 6.0]);
    assert_eq!(vdot(a, b), 32.0);
    assert_eq!(vcross(a, b), [-3.0, 6.0, -3.0]);
    assert_eq!(vlerp(a, b, 0.0), a);
    assert_eq!(vlerp(a, b, 1.0), b);
    assert_eq!(vlerp(a, b, 0.5), [2.5, 3.5, 4.5]);
}

#[test]
fn cross_is_perpendicular_to_both() {
    let a: Vec3 = [1.0, 2.0, 3.0];
    let b: Vec3 = [4.0, 5.0, 6.0];
    let c = vcross(a, b);
    assert!(vdot(c, a).abs() < 1e-12);
    assert!(vdot(c, b).abs() < 1e-12);
}

#[test]
fn vnorm_of_zero_does_not_produce_nan() {
    let z = vnorm([0.0, 0.0, 0.0]);
    assert!(
        z.iter().all(|x| x.is_finite()),
        "must not poison a mesh with NaN"
    );
}

#[test]
fn phi_satisfies_its_defining_equation() {
    assert_eq!(
        PHI * PHI - PHI - 1.0,
        0.0,
        "phi^2 - phi - 1 is EXACTLY zero at this double, not merely small"
    );
}

// ===========================================================================
// RULE 0 -- the certified path, MEASURED rather than argued
// ===========================================================================

/// The seed constant must be bit-identical across every tongue in the cave.
///
/// `Gos` writes a literal. `builder/genesis_wallpaper_v1_6.py` writes
/// `(1.0 + 5.0**0.5)/2.0`. `shell/byte_sphere.html` writes `(1+Math.sqrt(5))/2`.
/// `sqrt` is correctly rounded by IEEE-754 and `+`/`/` are too, so all three
/// are required to land on the same double -- and here that requirement is
/// checked instead of assumed.
///
/// Every C60 vertex is built from `PHI` using only `+ - * / sqrt`, so this one
/// assertion is what the whole "the port is a translation" claim rests on.
#[test]
fn phi_is_bit_identical_to_the_computed_form() {
    let computed = (1.0 + 5.0_f64.sqrt()) / 2.0;
    assert_eq!(
        PHI.to_bits(),
        computed.to_bits(),
        "literal {:#018x} vs computed {:#018x} -- the port diverges at the seed",
        PHI.to_bits(),
        computed.to_bits()
    );
    assert_eq!(
        PHI.to_bits(),
        0x3FF9_E377_9B97_F4A8,
        "the golden ratio's f64 bit pattern is frozen; a change here is a finding"
    );
}

/// The mantissa of `PHI` and `splitmix64`'s gamma are the same constant at two
/// widths: `(phi - 1) * 2^64 = 0x9E3779B97F4A7C15`, and the top 52 bits of that
/// fraction are `PHI`'s mantissa. The geometry and the PRNG are seeded by the
/// same number, which nobody planned.
#[test]
fn the_golden_ratio_appears_at_two_widths() {
    let mantissa = PHI.to_bits() & ((1u64 << 52) - 1);
    assert_eq!(mantissa, 0x9_E377_9B97_F4A8);
    const SPLITMIX_GAMMA: u64 = 0x9E37_79B9_7F4A_7C15;
    assert_eq!(
        mantissa >> 4,
        SPLITMIX_GAMMA >> 16,
        "both encode phi's fractional part; they must share their leading digits"
    );
}

/// RULE 0's second row. `mul_add` is ONE rounding where the browser does two,
/// so it is faster, more accurate, and WRONG for the certified path -- accuracy
/// is not the contract, bit-identity is.
///
/// On the baseline `x86_64` target FMA is not even in the feature set, so this
/// is belt and braces. It becomes load-bearing the moment anyone builds with
/// `-C target-cpu=native`, which unlocks `fma` (measured: 5 features -> 30).
#[test]
fn fused_multiply_add_is_not_the_certified_path() {
    // (1 + eps)(1 - eps) = 1 - eps^2. The product's true value needs 104 bits,
    // so `*` rounds it to exactly 1.0 and the subtraction then yields zero.
    // A fused op keeps the full product and lands on -eps^2, which IS
    // representable. Same inputs, same arithmetic on paper, different bits.
    let a = 1.0_f64 + f64::EPSILON;
    let b = 1.0_f64 - f64::EPSILON;
    let separate = a * b + (-1.0);
    let fused = a.mul_add(b, -1.0);
    assert_eq!(separate, 0.0, "the rounded product cancels exactly");
    assert!(fused < 0.0, "the fused form keeps -eps^2, got {fused:e}");
    assert_ne!(
        separate.to_bits(),
        fused.to_bits(),
        "if these ever agree the example is too weak to guard the rule"
    );

    // vdot must use the separate form -- what the browser computes.
    let d = vdot([a, a, a], [b, b, b]);
    assert_eq!(d.to_bits(), (a * b + a * b + a * b).to_bits());
}

// ===========================================================================
// THE LADDER -- exact vs float64
// ===========================================================================

#[test]
fn ladder_first_terms() {
    assert_eq!(
        ladder::exact(11).unwrap(),
        vec![1, 3, 7, 19, 49, 129, 337, 883, 2311, 6051, 15841, 41473]
    );
}

/// The headline: float64 first lies at n = 38.
#[test]
fn float64_wall_is_at_thirty_eight() {
    assert_eq!(
        ladder::find_wall(60).unwrap(),
        Some(ladder::F64_WALL),
        "the f64 recurrence must first disagree at n = 38"
    );
}

/// And the value crossing is one step LATER -- the intermediate `3*T_(n-1)`
/// leaves the exact range before the term itself does.
#[test]
fn value_crosses_two_pow_53_one_step_after_the_wall() {
    let crossing = ladder::find_2p53_crossing(60).unwrap().unwrap();
    assert_eq!(crossing, 39, "T_n first exceeds 2^53 at n = 39");
    assert_eq!(
        crossing,
        ladder::F64_WALL + 1,
        "the wall precedes the crossing by exactly one step"
    );
}

#[test]
fn the_offending_intermediate_really_does_overflow() {
    let t = ladder::exact(38).unwrap();
    assert_eq!(t[37], 3_055_769_911_545_123, "T_37");
    assert!(
        3 * t[37] > ladder::TWO_POW_53,
        "3*T_37 must exceed 2^53 -- that is the mechanism"
    );
    assert!(
        t[38] < ladder::TWO_POW_53,
        "yet T_38 itself is still under 2^53"
    );
    assert_eq!(t[38], 8_000_109_490_224_391, "T_38 exact");
}

#[test]
fn everything_below_the_wall_agrees_exactly() {
    for r in ladder::compare(ladder::F64_LAST_GOOD).unwrap() {
        assert!(r.agrees, "n = {} must agree exactly", r.n);
        assert_eq!(r.rel_err, 0.0, "n = {} error must be zero", r.n);
    }
}

#[test]
fn the_error_grows_past_the_wall() {
    let rows = ladder::compare(50).unwrap();
    let a = rows[ladder::F64_WALL].rel_err;
    let b = rows[50].rel_err;
    assert!(a > 0.0, "there must be error at the wall");
    assert!(b > a, "the error must compound: {b} should exceed {a}");
}

#[test]
fn ladder_refuses_to_guess_past_i128() {
    assert!(
        ladder::exact(ladder::I128_MAX_N).is_ok(),
        "n = {} must fit",
        ladder::I128_MAX_N
    );
    assert!(
        ladder::exact(ladder::I128_MAX_N + 1).is_err(),
        "n = {} must report overflow, never wrap",
        ladder::I128_MAX_N + 1
    );
}

/// RUSTIUM R3. The bound must be MEASURED, not asserted.
///
/// `exact_measured` consults no constant -- `checked_*` arithmetic decides. If
/// `I128_MAX_N` ever disagrees with the arithmetic again, this fails and names
/// the real boundary. The previous value (92) counted TERMS while the code read
/// it as an INDEX, and the test that was supposed to guard it asserted the
/// wrong number, so it enforced the bug instead of catching it.
#[test]
fn the_stated_bound_is_the_measured_bound() {
    assert!(
        ladder::exact_measured(ladder::I128_MAX_N).is_ok(),
        "T_{} must be computable in i128",
        ladder::I128_MAX_N
    );
    let over = ladder::exact_measured(ladder::I128_MAX_N + 1);
    assert!(
        over.is_err(),
        "T_{} must overflow i128 -- if this passes, the bound is too LOW",
        ladder::I128_MAX_N + 1
    );
    assert_eq!(ladder::I128_MAX_N, 91, "measured: T_91 fits, T_92 does not");
}

/// The promise is "returns LadderError rather than wrapping". Rust only checks
/// overflow in debug, so a magic-number guard is false in a release build.
/// This asserts the failure is produced by the ARITHMETIC, and reports the step.
#[test]
fn overflow_is_reported_never_wrapped() {
    match ladder::exact_measured(120) {
        Ok(_) => panic!("n = 120 cannot fit i128 -- a wrap was silently accepted"),
        Err(e) => {
            assert!(
                e.at > ladder::I128_MAX_N,
                "must fail past the bound, not before it; failed at {}",
                e.at
            );
            let t = ladder::exact_measured(ladder::I128_MAX_N).unwrap();
            assert!(
                t[ladder::I128_MAX_N] > 0,
                "no wrap: every term stays positive"
            );
        }
    }
}

/// RUSTIUM R6. A comment that states a count now has an assertion behind it.
#[test]
fn the_raw_permutation_count_is_sixty() {
    assert_eq!(RAW_PERM_POINTS, 60, "12 + 24 + 24");
    assert_eq!(
        build_c60_vertices().len(),
        60,
        "the zero-skip leaves 60 raw points and dedupe is a no-op"
    );
}

// ===========================================================================
// COMPLEX
// ===========================================================================

#[test]
fn complex_arithmetic() {
    let a = C::new(3.0, 4.0);
    let b = C::new(1.0, -2.0);
    assert_eq!(a + b, C::new(4.0, 2.0));
    assert_eq!(a - b, C::new(2.0, 6.0));
    assert_eq!(a * b, C::new(11.0, -2.0));
    assert_eq!(a.conj(), C::new(3.0, -4.0));
    assert_eq!(a.norm_sqr(), 25.0);
    assert_eq!(a.abs(), 5.0, "the 3-4-5 triangle is exact");
}

#[test]
fn i_squared_is_minus_one() {
    assert_eq!(C::I * C::I, C::new(-1.0, 0.0));
}

#[test]
fn division_inverts_multiplication() {
    let a = C::new(3.0, 4.0);
    let b = C::new(1.0, -2.0);
    let q = (a * b) / b;
    assert!((q.re - a.re).abs() < 1e-12 && (q.im - a.im).abs() < 1e-12);
}

#[test]
fn powi_matches_repeated_multiplication() {
    let z = C::new(0.7, -0.3);
    let mut acc = C::ONE;
    for _ in 0..7 {
        acc = acc * z;
    }
    let p = z.powi(7);
    assert!((p.re - acc.re).abs() < 1e-12 && (p.im - acc.im).abs() < 1e-12);
    assert_eq!(z.powi(0), C::ONE, "z^0 = 1");
}

#[test]
fn stereographic_lands_on_the_unit_sphere() {
    let mut r = Rng::new(7);
    for _ in 0..500 {
        let p = c_to_s2(C::new(r.range(-6.0, 6.0), r.range(-6.0, 6.0)));
        let n = (p[0] * p[0] + p[1] * p[1] + p[2] * p[2]).sqrt();
        assert!(
            (n - 1.0).abs() < 1e-12,
            "off the sphere by {}",
            (n - 1.0).abs()
        );
    }
}

#[test]
fn stereographic_fixes_the_poles() {
    assert_eq!(c_to_s2(C::ZERO), [0.0, 0.0, -1.0], "origin -> south pole");
    let far = c_to_s2(C::new(1e300, 0.0));
    assert!(
        far[2] > 0.999_999,
        "far away -> north pole, got z = {}",
        far[2]
    );
}

// ===========================================================================
// RNG -- reproducibility is the feature
// ===========================================================================

/// Known-good vectors, generated by an independent implementation.
/// If these fail the stream has changed and no Monte Carlo result is comparable.
#[test]
fn xoshiro_matches_the_reference_stream() {
    let mut r = Rng::new(0x5EED);
    assert_eq!(r.next_u64(), 0xEF33_F170_5524_4B74);
    assert_eq!(r.next_u64(), 0xE1F5_9111_2FB5_051B);
    assert_eq!(r.next_u64(), 0xD8AB_0564_0214_863A);
    assert_eq!(r.next_u64(), 0xF985_E1F2_FB89_7B03);
    assert_eq!(r.next_u64(), 0xAF87_A5F7_E6CE_1408);
    assert_eq!(r.next_u64(), 0x86F2_8E3A_0746_FF9E);
}

#[test]
fn same_seed_gives_the_same_stream() {
    let mut a = Rng::new(42);
    let mut b = Rng::new(42);
    for _ in 0..100 {
        assert_eq!(a.next_u64(), b.next_u64());
    }
}

#[test]
fn different_seeds_diverge() {
    let mut a = Rng::new(1);
    let mut b = Rng::new(2);
    assert_ne!(a.next_u64(), b.next_u64());
}

#[test]
fn seed_zero_does_not_stick() {
    let mut r = Rng::new(0);
    let v: Vec<u64> = (0..8).map(|_| r.next_u64()).collect();
    assert!(
        v.iter().any(|&x| x != 0),
        "splitmix64 seeding must avoid the all-zero state"
    );
}

#[test]
fn next_f64_stays_in_the_unit_interval() {
    let mut r = Rng::new(0xC0FFEE);
    for _ in 0..10_000 {
        let x = r.next_f64();
        assert!((0.0..1.0).contains(&x), "{x} outside [0,1)");
    }
}

#[test]
fn sphere_sampling_is_uniform_and_reproducible() {
    let mut r = Rng::new(1);
    let n = 20_000;
    let mut s = [0.0f64; 3];
    for _ in 0..n {
        let p = r.on_sphere();
        let len = (p[0] * p[0] + p[1] * p[1] + p[2] * p[2]).sqrt();
        assert!((len - 1.0).abs() < 1e-12, "point off the sphere");
        s = vadd(s, p);
    }
    let mean = vscale(s, 1.0 / n as f64);
    for c in mean {
        assert!(
            c.abs() < 0.02,
            "mean {mean:?} should be near zero if uniform"
        );
    }
}

// ===========================================================================
// THE JUDGE -- closure in pure graph space, integers only
// ===========================================================================

#[test]
fn the_judge_certifies_c60_without_a_single_float() {
    let sigma = judge::rotation_system_c60();
    assert_eq!(sigma.len(), 180, "60 vertices x degree 3 = 180 darts");
    let v = judge::check(&sigma).expect("C60 must be a closed orientable surface");
    assert_eq!(v.v, 60, "V -- orbits of sigma");
    assert_eq!(v.e, 90, "E -- darts/2");
    assert_eq!(v.f, 32, "F -- orbits of sigma o alpha");
    assert_eq!(v.chi, 2, "chi = V-E+F, COUNTED");
    assert_eq!(v.components, 1);
    assert_eq!(v.genus, Some(0), "a sphere");
}

/// Diverse Double-Compiling, in miniature.
///
/// Two derivations that share no machinery: the float lane measures distances,
/// sorts by `atan2` and walks faces; the integer lane counts orbits of a
/// permutation and never sees a coordinate. Wheeler's rule is that agreement
/// only counts when the second derivation is genuinely *diverse*. These are.
#[test]
fn float_lane_and_integer_lane_agree_on_c60() {
    let float_cert = certify(&Mesh::c60()).expect("the float lane certifies C60");
    let int_cert = judge::check(&judge::rotation_system_c60()).expect("the judge certifies C60");
    assert_eq!(float_cert.v, int_cert.v, "V");
    assert_eq!(float_cert.e, int_cert.e, "E");
    assert_eq!(float_cert.f, int_cert.f, "F");
    assert_eq!(float_cert.chi, int_cert.chi, "chi");
}

/// The judge must be able to FAIL. This is the whole difference between it and
/// `byte_sphere.html`'s `invCounts()`, which returns `chi: 2` as a typed
/// literal and therefore prints 2 for a mesh it never looked at.
///
/// The one-vertex torus: 4 darts, sigma a single 4-cycle. Two edges, one vertex,
/// one face -- chi = 0, genus 1. If the judge said 2 here it would be worthless.
#[test]
fn the_judge_can_say_something_other_than_two() {
    let torus = vec![2usize, 3, 1, 0];
    let v = judge::check(&torus).expect("a torus is a valid map, just not a sphere");
    assert_eq!((v.v, v.e, v.f), (1, 2, 1));
    assert_eq!(v.chi, 0, "a torus has chi = 0, and the judge must say so");
    assert_eq!(v.genus, Some(1), "genus 1 -- one handle");
}

#[test]
fn the_judge_certifies_the_smallest_sphere() {
    // one edge, two vertices, one face: chi = 2 - 1 + 1 = 2
    let v = judge::check(&[0usize, 1]).expect("the 1-edge sphere");
    assert_eq!((v.v, v.e, v.f, v.chi, v.genus), (2, 1, 1, 2, Some(0)));
}

#[test]
fn the_judge_refuses_an_odd_dart_count() {
    assert_eq!(judge::check(&[0usize]), Err(judge::Refusal::DartCount(1)));
    assert_eq!(judge::check(&[]), Err(judge::Refusal::DartCount(0)));
}

#[test]
fn the_judge_refuses_a_sigma_that_leaves_the_dart_set() {
    assert_eq!(
        judge::check(&[9usize, 1]),
        Err(judge::Refusal::OutOfRange { at: 0, to: 9 })
    );
}

#[test]
fn the_judge_refuses_a_non_bijection() {
    assert_eq!(
        judge::check(&[0usize, 0]),
        Err(judge::Refusal::NotBijection { hits: 0 })
    );
}

/// alpha is an XOR, so it is an involution by construction -- there is no way
/// to get the edge pairing subtly wrong, which is the point of the encoding.
#[test]
fn alpha_is_an_involution_by_construction() {
    for d in 0..180usize {
        assert_eq!(judge::alpha(judge::alpha(d)), d);
        assert_ne!(judge::alpha(d), d);
    }
}

/// R7's promise: the judge's depth is not bounded by any tolerance. Every face
/// of C60 must be a pentagon or hexagon, read off phi's orbit lengths rather
/// than from geometry.
#[test]
fn face_sizes_come_from_orbit_lengths_not_geometry() {
    let sigma = judge::rotation_system_c60();
    let mut seen = vec![false; sigma.len()];
    let (mut pent, mut hex) = (0, 0);
    for s in 0..sigma.len() {
        if seen[s] {
            continue;
        }
        let (mut c, mut len) = (s, 0);
        loop {
            seen[c] = true;
            c = sigma[judge::alpha(c)];
            len += 1;
            if c == s {
                break;
            }
        }
        match len {
            5 => pent += 1,
            6 => hex += 1,
            n => panic!("a {n}-gon on C60"),
        }
    }
    assert_eq!(pent, 12, "Euler forces exactly twelve pentagons");
    assert_eq!(hex, 20);
}

// ===========================================================================
// THE ICOSPHERE LANE -- exact index subdivision, chi COUNTED not recited
// ===========================================================================

use goldberg_kernel::sphere::{self, Ico};

#[test]
fn subdivision_counts_match_the_exact_formula() {
    for l in 0..=5u32 {
        let ico = Ico::level(l).expect("within budget");
        let (v, e, f) = sphere::counts(l).unwrap();
        assert_eq!(ico.faces.len(), f, "F = 20*4^{l}");
        assert_eq!(ico.verts.len(), v, "V = 10*4^{l} + 2");
        assert_eq!(f, 20 * 4usize.pow(l));
        assert_eq!(v, 10 * 4usize.pow(l) + 2);
        assert_eq!(e, 30 * 4usize.pow(l));
    }
}

/// The whole point of this lane over `byte_sphere.html`.
///
/// Its HUD prints `chi:2` as a typed literal from `{F:20*4**L, E:30*4**L,
/// V:10*4**L+2}` -- an exact algebraic identity that returns 2 for every L
/// whether or not a mesh exists. Here the built mesh is handed to the judge,
/// which counts orbits of a permutation and CAN say something else.
#[test]
fn the_judge_counts_chi_on_every_refined_level() {
    for l in 0..=4u32 {
        let ico = Ico::level(l).expect("within budget");
        let sigma = ico
            .rotation_system()
            .unwrap_or_else(|| panic!("level {l} must present each directed edge exactly once"));
        let v = judge::check(&sigma).unwrap_or_else(|e| panic!("level {l}: {e}"));

        let (cv, ce, cf) = sphere::counts(l).unwrap();
        assert_eq!(v.v, cv, "level {l}: V counted vs formula");
        assert_eq!(v.e, ce, "level {l}: E counted vs formula");
        assert_eq!(v.f, cf, "level {l}: F counted vs formula");
        assert_eq!(v.chi, 2, "level {l}: chi COUNTED, not recited");
        assert_eq!(v.genus, Some(0), "level {l}: a sphere");
    }
}

/// Euler forces exactly twelve five-valent vertices at EVERY depth. Those are
/// the twelve pentagons of the dual -- the constraint, in the triangulated lane.
#[test]
fn twelve_defects_at_every_depth() {
    for l in 0..=5u32 {
        let ico = Ico::level(l).expect("within budget");
        assert_eq!(
            ico.defects().len(),
            12,
            "level {l}: Euler forces twelve five-valent vertices"
        );
    }
}

/// R7 cannot happen here: the weld is an index map, so a subdivided edge is
/// shared exactly, and every vertex stays exactly on the unit sphere.
#[test]
fn subdivision_welds_exactly_and_stays_on_the_sphere() {
    let ico = Ico::level(4).expect("within budget");
    let worst = ico
        .verts
        .iter()
        .map(|v| (vlen(*v) - 1.0).abs())
        .fold(0.0f64, f64::max);
    assert!(worst < 1e-12, "worst radius error {worst:e}");

    // every undirected edge shared by exactly two faces == no seam, no dup
    let mut count: std::collections::HashMap<(usize, usize), usize> = Default::default();
    for f in &ico.faces {
        for i in 0..3 {
            let (a, b) = (f[i], f[(i + 1) % 3]);
            *count.entry((a.min(b), a.max(b))).or_insert(0) += 1;
        }
    }
    assert_eq!(count.len(), sphere::counts(4).unwrap().1, "E");
    assert!(
        count.values().all(|&c| c == 2),
        "every edge must be shared by exactly two faces"
    );
}

/// One face per byte is the resolution `byte_sphere` reaches at L5 for 24 KB.
#[test]
fn level_for_bytes_reaches_one_byte_per_face() {
    assert_eq!(sphere::level_for_bytes(20), 0, "20 faces hold 20 bytes");
    let l = sphere::level_for_bytes(24_000);
    let ico = Ico::level(l).expect("within budget");
    assert!(
        ico.faces.len() >= 24_000,
        "level {l} gives {} faces for 24,000 bytes",
        ico.faces.len()
    );
    assert_eq!(ico.bytes_per_face(24_000), 1, "one byte per face");
    // and the level below must NOT be enough -- the choice is tight
    if l > 0 {
        assert!(sphere::counts(l - 1).unwrap().2 < 24_000);
    }
}

/// Curse 35: growth is 4x per level, so the guillotine must refuse with a number.
#[test]
fn refinement_refuses_loudly_past_the_budget() {
    let e = Ico::level(12).expect_err("level 12 must be refused");
    assert!(e.predicted_faces > sphere::FACE_BUDGET);
    assert!(format!("{e}").contains("HALT"), "must refuse out loud");
}

/// The formula ALWAYS says 2 -- which is why it is not a certification.
#[test]
fn the_formula_is_an_identity_and_therefore_proves_nothing() {
    for l in 0..=20u32 {
        assert_eq!(
            sphere::formula_chi(l),
            Some(2),
            "the formula returns 2 for every L, mesh or no mesh"
        );
    }
}

#[test]
fn hilbert_key_is_a_bijection_on_its_grid() {
    let mut seen = std::collections::HashSet::new();
    for y in 0..128u32 {
        for x in 0..128u32 {
            assert!(
                seen.insert(sphere::hilbert_xy(7, x, y)),
                "collision at {x},{y}"
            );
        }
    }
    assert_eq!(seen.len(), 128 * 128);
}

// ===========================================================================
// THE LEDGER -- the logger must enforce, not merely print
// ===========================================================================

#[test]
fn ledger_counts_both_outcomes() {
    let mut l = Ledger::silent();
    assert!(l.check_eq(Lane::Certified, "good", 12usize, 12usize));
    assert!(!l.check_eq(Lane::Certified, "bad", 12usize, 11usize));
    assert_eq!((l.passed(), l.failed()), (1, 1));
    assert!(!l.sealed_ok(), "a ledger with a failure must not seal");
}

/// Curse 35: the guillotine refuses BEFORE the allocation, and says the number.
#[test]
fn ledger_refuses_over_budget() {
    let mut l = Ledger::silent();
    assert!(l.predict("level 5", 9_812, 1_200_000));
    assert!(!l.predict("level 8", 68_612_000, 1_200_000));
    assert_eq!(l.refused(), 1);
    assert!(!l.sealed_ok(), "a refusal must break the seal");
}

/// The display lane reports its error rather than hiding it behind a bool.
#[test]
fn ledger_display_lane_carries_a_tolerance() {
    let mut l = Ledger::silent();
    assert!(l.check_near(Lane::Display, "phi^2-phi-1", 0.0, 1e-16, 1e-12));
    assert!(!l.check_near(Lane::Display, "too far", 0.0, 1e-3, 1e-12));
    assert_eq!((l.passed(), l.failed()), (1, 1));
}

/// The whole C60 certificate, driven through the ledger. This is the shape the
/// pre-build closure gate will take: every invariant MEASURED from the built
/// mesh, target and current side by side, nothing inferred from a formula.
#[test]
fn ledger_certifies_c60_end_to_end() {
    let m = Mesh::c60();
    let c = certify(&m).expect("C60 must certify");
    let mut l = Ledger::silent();

    l.check_eq(Lane::Certified, "V", 60usize, c.v);
    l.check_eq(Lane::Certified, "E", 90usize, c.e);
    l.check_eq(Lane::Certified, "F", 32usize, c.f);
    l.check_eq(Lane::Certified, "P (Euler forces 12)", 12usize, c.p);
    l.check_eq(Lane::Certified, "H", 20usize, c.h);
    l.check_eq(Lane::Certified, "chi = V-E+F", 2i64, c.chi);
    l.check_eq(Lane::Certified, "2E == 3V", c.e * 2, c.v * 3);

    let worst = m
        .verts
        .iter()
        .map(|v| (vlen(*v) - 1.0).abs())
        .fold(0.0f64, f64::max);
    l.check_near(Lane::Display, "worst radius error", 0.0, worst, 1e-12);

    assert!(l.sealed_ok(), "the C60 ledger must seal clean");
    assert_eq!(l.passed(), 8);
    assert_eq!(l.failed(), 0);
}

// ===========================================================================
// R12 -- THE EQUAL FORMULA
//
// RULE 0 promises bit-identity with the browser on the certified path. That
// promise is about the EXPRESSION, not the value: IEEE-754 gives correct
// rounding per OPERATION, so two algebraically identical formulas that round a
// different number of times give different doubles.
//
// These three tests freeze the browser's spelling. They are the only thing
// standing between the port and a well-meaning "simplification" -- the whole
// 90-test suite passed on both spellings, so nothing else here can see it.
// ===========================================================================

/// `centroid` must divide by `n`, never multiply by `1/n`.
///
/// `1/5` is not representable in binary64, so `sum * (1.0/5.0)` rounds twice
/// where `sum / 5.0` rounds once. Measured over 400k random inputs, 34.2%
/// disagree by an ulp. `refineFace` calls this on every face at every level.
#[test]
fn centroid_divides_by_n_and_does_not_multiply_by_its_reciprocal() {
    // A pentagon whose coordinate sum exercises the n=5 rounding, built from
    // PHI so it sits on the scale the operator actually works at.
    let pts: Vec<Vec3> = vec![
        [1.0, 2.0, PHI],
        [2.0 * PHI, 1.0, 2.0],
        [3.0 * PHI, PHI, 1.0],
        [2.0, 3.0 * PHI, 2.0 * PHI],
        [PHI, 2.0 * PHI, 3.0 * PHI],
    ];
    let n = pts.len() as f64;
    let sum = pts.iter().fold([0.0f64; 3], |a, p| vadd(a, *p));

    let good = centroid(&pts);
    let bad = vscale(sum, 1.0 / n);

    // the browser's spelling, reproduced here so the test does not consult the
    // function it is grading
    for k in 0..3 {
        assert_eq!(
            good[k].to_bits(),
            (sum[k] / n).to_bits(),
            "centroid component {k} must be sum/n, bit for bit"
        );
    }

    // and the two spellings really do differ -- a weak example is a failed
    // test, not a passed one (the fused_multiply_add lesson)
    assert!(
        (0..3).any(|k| good[k].to_bits() != bad[k].to_bits()),
        "this fixture no longer distinguishes sum/n from sum*(1/n); \
         pick coordinates that do, or the test is decorative"
    );
}

/// `project_to_sphere` must be `p * (R/L)`, never `(p * (1/L)) * R`.
///
/// Measured over 400k random inputs, 41.6% disagree by an ulp.
#[test]
fn project_to_sphere_scales_by_r_over_l_in_one_step() {
    let p: Vec3 = [0.7136441795461798, 1.0 / 3.0, PHI];
    let r = 1.6;
    let l = vlen(p);

    let good = project_to_sphere(p, r);
    let bad = vscale(vnorm(p), r);

    for k in 0..3 {
        assert_eq!(
            good[k].to_bits(),
            (p[k] * (r / l)).to_bits(),
            "component {k} must be p*(R/L), bit for bit"
        );
    }
    assert!(
        (0..3).any(|k| good[k].to_bits() != bad[k].to_bits()),
        "this fixture no longer distinguishes p*(R/L) from (p*(1/L))*R"
    );
}

/// A point at the origin has no direction. The browser returns it unchanged;
/// normalising it would produce NaN and poison every face downstream.
#[test]
fn project_to_sphere_refuses_the_origin_instead_of_returning_nan() {
    let o = project_to_sphere([0.0, 0.0, 0.0], 1.6);
    assert_eq!(o, [0.0, 0.0, 0.0]);
    assert!(o.iter().all(|c| c.is_finite()), "must not be NaN");
}

/// `vlerp` must be `a(1-t) + bt`, never `a + (b-a)t`.
#[test]
fn vlerp_is_the_browsers_spelling() {
    let a: Vec3 = [1.0, PHI, 3.0 * PHI];
    let b: Vec3 = [2.0 * PHI, 0.1, 1.0 / 7.0];
    let t = 0.45; // the operator's INNER_SCALE
    let got = vlerp(a, b, t);
    for k in 0..3 {
        assert_eq!(
            got[k].to_bits(),
            (a[k] * (1.0 - t) + b[k] * t).to_bits(),
            "component {k} must be a(1-t)+bt, bit for bit"
        );
    }
}

// ===========================================================================
// THE GRID MUST NOT SILENTLY DROP A CARD
//
// `dashboard::center` clips: a card whose bottom leaves the grid is skipped
// with a bare `break`, so it is never drawn AND never gets a rect. The viewer
// hit-tests against those rects, so a clipped card is invisible and unclickable
// and nothing anywhere says so.
//
// That is the drift these tests exist to catch: the viewer's `card_views` list
// is built beside the cards, so if `draw()` returns fewer rects than there are
// cards, the two lists disagree and a click lands on the wrong view -- or on
// nothing. Pin the viewer's ACTUAL geometry so adding a card that does not fit
// fails here instead of in someone's hand.
// ===========================================================================

/// The viewer paints the dashboard at exactly 900x700. Every card it declares
/// must come back with a rect.
#[test]
fn every_card_the_viewer_declares_gets_a_clickable_rect() {
    use goldberg_kernel::dashboard::{self, Card, KRow, Model};
    use goldberg_kernel::palette::DASHBOARD;
    use goldberg_kernel::raster::Canvas;

    // the viewer's canvas, not a convenient one
    const VIEWER_W: usize = 900;
    const VIEWER_H: usize = 700;

    let modules: Vec<KRow> = (0..6)
        .map(|i| KRow {
            name: "M",
            ok: true,
            kb: i,
        })
        .collect();

    let card = |tag, name, featured| Card {
        tag,
        name,
        desc: "a description long enough to wrap the way the real ones do, so the \
               measured height is the height the viewer actually paints",
        accent: DASHBOARD.gold,
        caps: &["frm", "kbd"],
        featured,
    };

    // the two the viewer declares today, in its order
    let cards = [
        card("* THE BIRTH", "THE LIGHT MATRIX", true),
        card("GENESIS", "GENESIS v0.1 - THE SEED", false),
    ];

    let m = Model {
        version: "v2.0",
        git: "0000000",
        ledger: "L000",
        cert: "V 60 E 90 F 32 CHI 2",
        modules: &modules,
        cards: &cards,
        category: "THEA HELENI SOURCE CODE",
    };

    let mut cv = Canvas::new(VIEWER_W, VIEWER_H, DASHBOARD.bg);
    let rects = dashboard::draw(&mut cv, &DASHBOARD, &m);

    assert_eq!(
        rects.len(),
        cards.len(),
        "the grid dropped {} of {} cards at {VIEWER_W}x{VIEWER_H}. A clipped card is \
         never drawn and never clickable, and the viewer's card_views list would then \
         be indexed against a shorter rect list. Either shrink the card or scroll the \
         grid -- do not ship a card nobody can reach.",
        cards.len() - rects.len(),
        cards.len()
    );

    // and the rects must be real, disjoint, and inside the canvas
    for (i, r) in rects.iter().enumerate() {
        assert!(r.w > 0 && r.h > 0, "card {i} has an empty rect");
        assert!(
            r.x >= 0 && r.y >= 0 && r.right() <= VIEWER_W as i32 && r.bottom() <= VIEWER_H as i32,
            "card {i} rect {r:?} leaves the canvas"
        );
        for (j, o) in rects.iter().enumerate().skip(i + 1) {
            let overlap =
                r.x < o.right() && o.x < r.right() && r.y < o.bottom() && o.y < r.bottom();
            assert!(
                !overlap,
                "cards {i} and {j} overlap -- one click would hit both"
            );
        }
    }
}

/// How much headroom the grid actually has, so the next mage knows the budget
/// before adding a card rather than after.
#[test]
fn the_grid_reports_its_real_card_budget() {
    use goldberg_kernel::dashboard::{self, Card, KRow, Model};
    use goldberg_kernel::palette::DASHBOARD;
    use goldberg_kernel::raster::Canvas;

    let modules: Vec<KRow> = (0..6)
        .map(|_| KRow {
            name: "M",
            ok: true,
            kb: 1,
        })
        .collect();
    // Card borrows, so build 40 fresh ones rather than cloning
    let many: Vec<Card> = (0..40)
        .map(|_| Card {
            tag: "T",
            name: "N",
            desc: "d",
            accent: DASHBOARD.gold,
            caps: &["frm"],
            featured: false,
        })
        .collect();
    let m = Model {
        version: "v2.0",
        git: "0000000",
        ledger: "L000",
        cert: "c",
        modules: &modules,
        cards: &many,
        category: "CAT",
    };
    let mut cv = Canvas::new(900, 700, DASHBOARD.bg);
    let fits = dashboard::draw(&mut cv, &DASHBOARD, &m).len();

    // MEASURED, not assumed. If the layout changes this number moves and the
    // assertion says so, instead of a card quietly vanishing.
    assert_eq!(
        fits, 10,
        "the 900x700 grid holds a different number of cards than recorded"
    );
    assert!(
        fits >= 2,
        "the viewer declares 2 cards and the grid must hold them"
    );
}

// ===========================================================================
// THE MOVIE BUDGET -- a prediction that must be exact, not close
//
// `png_bytes` prices a render before it is written. If it were an estimate,
// a 60-frame 8K movie would be "about 5 GB" and the disk would find out the
// truth. It is not an estimate: stored deflate makes the size a pure function
// of the dimensions, so this can be graded against a real encode.
// ===========================================================================

#[test]
fn png_bytes_predicts_the_encoder_exactly() {
    use goldberg_kernel::palette::DASHBOARD;
    use goldberg_kernel::raster::{png_bytes, Canvas};

    // sizes that straddle the 65535-byte deflate block boundary in both
    // directions, plus the two the viewer actually uses
    for (w, h) in [
        (1, 1),
        (7, 3),
        (64, 64),
        (321, 197),
        (900, 700),
        (1920, 1080),
    ] {
        let mut cv = Canvas::new(w, h, DASHBOARD.bg);
        // paint something, to prove the size does NOT depend on the content
        cv.fill_rect(0, 0, (w / 2) as i32, (h / 2) as i32, DASHBOARD.gold);
        let encoded = cv.to_png().len();
        assert_eq!(
            encoded,
            png_bytes(w, h),
            "png_bytes({w},{h}) predicted {} but the encoder produced {encoded}",
            png_bytes(w, h)
        );
    }
}

/// The size must not move when the picture does. That is the whole property
/// the movie budget rests on.
#[test]
fn png_size_is_blind_to_the_image() {
    use goldberg_kernel::palette::DASHBOARD;
    use goldberg_kernel::raster::Canvas;

    let blank = Canvas::new(200, 150, DASHBOARD.bg).to_png().len();
    let mut busy = Canvas::new(200, 150, DASHBOARD.bg);
    for i in 0..150 {
        busy.line(0, i, 199, 149 - i, DASHBOARD.cyan);
    }
    assert_eq!(
        blank,
        busy.to_png().len(),
        "stored deflate must make size independent of content"
    );
}

/// The number that governs how careful we have to be.
#[test]
fn an_8k_frame_is_five_megabytes_from_the_hundred_meg_wall() {
    use goldberg_kernel::raster::png_bytes;
    let eight_k = png_bytes(7680, 4320);
    assert_eq!(eight_k, 99_544_778);
    assert!(
        eight_k < 100 * 1024 * 1024,
        "an 8K frame must still be under the git limit, barely"
    );
    assert!(
        100 * 1024 * 1024 - eight_k < 6 * 1024 * 1024,
        "and the margin is thin enough that nothing at this size may be tracked"
    );
}

// ===========================================================================
// CENTROSYMMETRY -- why a full turn shows only EVEN harmonics
//
// Sweeping the view through a full turn and measuring each frame, every
// significant rotational harmonic came out even: m = 2,4,6,8,10,12, with the
// odd ones one to two orders of magnitude down.
//
// The first explanation offered was that the see-through render superimposes
// front and back, so a rotation by pi maps one onto the other and imposes a
// 2-fold symmetry the mesh does not have. A prediction followed: turn on
// back-face culling and the odd harmonics should rise.
//
// THEY FELL. m=3 dropped 10x and m=5 dropped 2x. The hypothesis was wrong.
//
// The real cause is this test: the shell is CENTROSYMMETRIC. `-v` is a vertex
// for every vertex `v`, so the orthographic projection from `d` and from `-d`
// differ only by an inversion; any global scalar of them is therefore equal,
// and `f(yaw) == f(yaw + pi)` for any such measure -- with or without culling,
// and for any renderer at all. Only even harmonics can survive.
// ===========================================================================

#[test]
fn the_c60_is_centrosymmetric() {
    let m = Mesh::c60();
    let key = |v: Vec3| {
        (
            (v[0] * 1e9).round() as i64,
            (v[1] * 1e9).round() as i64,
            (v[2] * 1e9).round() as i64,
        )
    };
    let set: std::collections::HashSet<(i64, i64, i64)> = m.verts.iter().map(|v| key(*v)).collect();
    assert_eq!(set.len(), 60, "sixty distinct vertices");

    let orphans: Vec<Vec3> = m
        .verts
        .iter()
        .copied()
        .filter(|v| !set.contains(&key([-v[0], -v[1], -v[2]])))
        .collect();
    assert!(
        orphans.is_empty(),
        "{} vertices have no antipode -- the shell is NOT centrosymmetric, and the \
         even-only harmonic spectrum measured over a full turn has no explanation",
        orphans.len()
    );
}

/// The consequence, stated as geometry rather than as a rendering effect:
/// the centroid of the whole shell sits exactly at the origin, because the
/// vertices cancel in antipodal pairs.
#[test]
fn centrosymmetry_puts_the_centroid_exactly_at_the_origin() {
    let m = Mesh::c60();
    let c = centroid(&m.verts);
    for (i, x) in c.iter().enumerate() {
        assert!(
            x.abs() < 1e-15,
            "centroid component {i} is {x:e}, not zero -- antipodal pairs must cancel"
        );
    }
}

/// And it survives refinement: `refineFace` treats every face the same way, so
/// a centrosymmetric face set stays centrosymmetric. This is what makes the
/// even-only spectrum hold at depth, not just at the seed.
#[test]
fn refinement_preserves_the_centre() {
    use goldberg_kernel::genesis::{Op, Params, State};
    use goldberg_kernel::rng::Rng;

    let mut rng = Rng::new(0x5EED);
    let mut s = State::seed_c60();
    for _ in 0..2 {
        s = s.refine(Op::All, &Params::default(), &mut rng);
    }
    let all: Vec<Vec3> = s.faces.iter().flat_map(|f| f.pts.iter().copied()).collect();
    let c = centroid(&all);
    for (i, x) in c.iter().enumerate() {
        assert!(
            x.abs() < 1e-12,
            "after two refinements the centroid component {i} is {x:e}"
        );
    }
}

// ===========================================================================
// CLIPPING -- cost proportional to what is SEEN, not to what is asked for
//
// `line_a` walks one pixel per step, so an entirely off-screen line used to
// cost every pixel it would have covered. Fine at zoom 1; unbounded as zoom
// grows. At 480,212 faces and a 400,000-pixel span that is over a trillion
// iterations -- a hang, not a slowdown, and the reason the zoom range could
// not be widened until this existed.
// ===========================================================================

/// A line wholly inside must be untouched by the clipper, so everything that
/// was visible before rasterises **identically**. This is the property that
/// makes clipping safe to add to a program whose frames are sealed.
#[test]
fn a_fully_visible_line_is_unchanged_by_clipping() {
    use goldberg_kernel::palette::DASHBOARD;
    use goldberg_kernel::raster::Canvas;

    let mut a = Canvas::new(64, 64, DASHBOARD.bg);
    a.line_a(5, 5, 58, 40, DASHBOARD.cyan, 255);

    // the same line drawn on a canvas large enough that it could never have
    // been clipped either way
    let mut b = Canvas::new(200, 200, DASHBOARD.bg);
    b.line_a(5, 5, 58, 40, DASHBOARD.cyan, 255);

    for y in 0..64 {
        for x in 0..64 {
            let ia = (y * 64 + x) * 3;
            let ib = (y * 200 + x) * 3;
            assert_eq!(
                a.px[ia..ia + 3],
                b.px[ib..ib + 3],
                "pixel ({x},{y}) differs -- clipping changed a line it should not touch"
            );
        }
    }
}

/// A line with nothing on screen must draw nothing, and must not iterate its
/// length to find that out.
#[test]
fn a_line_entirely_off_screen_draws_nothing() {
    use goldberg_kernel::palette::DASHBOARD;
    use goldberg_kernel::raster::Canvas;

    for (x0, y0, x1, y1, where_) in [
        (-500, -500, -400, -400, "up-left"),
        (900, 10, 2000, 40, "right"),
        (10, -900, 40, -500, "above"),
        (
            -2_000_000,
            30,
            -1_000_000,
            35,
            "far left, a million pixels long",
        ),
    ] {
        let mut cv = Canvas::new(200, 150, DASHBOARD.bg);
        let before = cv.digest();
        cv.line_a(x0, y0, x1, y1, DASHBOARD.cyan, 255);
        assert_eq!(
            before,
            cv.digest(),
            "a line {where_} of the canvas changed pixels"
        );
    }
}

/// A line that crosses the boundary keeps its visible part.
#[test]
fn a_crossing_line_keeps_the_part_that_is_on_screen() {
    use goldberg_kernel::palette::DASHBOARD;
    use goldberg_kernel::raster::Canvas;

    let mut cv = Canvas::new(200, 150, DASHBOARD.bg);
    let before = cv.digest();
    // starts far off the left, ends in the middle
    cv.line_a(-10_000, 75, 100, 75, DASHBOARD.cyan, 255);
    assert_ne!(before, cv.digest(), "the visible half must still be drawn");

    // and it reaches the edge it entered through
    let left = (75 * 200) * 3;
    assert_ne!(
        cv.px[left..left + 3],
        [DASHBOARD.bg[0], DASHBOARD.bg[1], DASHBOARD.bg[2]][..],
        "the clipped line must start at the canvas edge, not inside it"
    );
}

/// **The property the whole thing exists for.** A line a million pixels long
/// with nothing on screen must return in the time a short one takes -- if it
/// still walked its length, this would be the slowest test in the suite by
/// several orders of magnitude.
#[test]
fn an_enormous_off_screen_line_costs_nothing() {
    use goldberg_kernel::palette::DASHBOARD;
    use goldberg_kernel::raster::Canvas;
    use std::time::Instant;

    let mut cv = Canvas::new(200, 150, DASHBOARD.bg);
    let t0 = Instant::now();
    for _ in 0..1000 {
        cv.line_a(
            -3_000_000,
            -3_000_000,
            -2_000_000,
            -2_000_000,
            DASHBOARD.cyan,
            255,
        );
    }
    let us = t0.elapsed().as_micros();
    assert!(
        us < 50_000,
        "1000 rejected lines took {us} us. Unclipped they would each have walked \
         a million pixels -- this test is the difference between a fence and a hang."
    );
}

// ---------------------------------------------------------------------------
//  fill_poly -- the face fill, added 2026-09-02 to match the browser's cx.fill()
// ---------------------------------------------------------------------------

/// A filled square must cover exactly its own area -- no more, no less.
/// Counts pixels rather than eyeballing a picture, because "looks filled" is
/// the claim this whole crate exists to avoid making.
#[test]
fn fill_poly_covers_exactly_the_polygon_area() {
    let mut cv = Canvas::new(32, 32, [0, 0, 0]);
    // half-open rows: y in [4, 12) -> 8 rows; x likewise -> 8 columns
    cv.fill_poly(&[(4, 4), (12, 4), (12, 12), (4, 12)], [255, 255, 255], 255);
    let mut lit = 0usize;
    for y in 0..32 {
        for x in 0..32 {
            if cv.get(x, y) != [0, 0, 0] {
                lit += 1;
            }
        }
    }
    assert_eq!(lit, 64, "an 8x8 half-open square is 64 pixels, got {lit}");
}

/// The seam test, and the reason the rows are half-open. Face soup means two
/// neighbours each draw their own copy of a shared edge. If the fill covered
/// both its top and bottom row, a translucent fill would blend TWICE along
/// every interior edge and the mesh would grow a bright seam on every join.
#[test]
fn abutting_polygons_do_not_double_blend_the_shared_edge() {
    let mut cv = Canvas::new(16, 16, [0, 0, 0]);
    // two rectangles meeting exactly at y = 8
    cv.fill_poly(&[(2, 2), (10, 2), (10, 8), (2, 8)], [100, 100, 100], 128);
    let once = cv.get(4, 5);
    cv.fill_poly(&[(2, 8), (10, 8), (10, 14), (2, 14)], [100, 100, 100], 128);
    assert_eq!(
        cv.get(4, 5),
        once,
        "the first rectangle's interior must not be touched by the second"
    );
    // the shared row belongs to the SECOND rectangle only -- blended once
    assert_eq!(
        cv.get(4, 8),
        once,
        "row 8 must be blended exactly once, not twice"
    );
}

/// Alpha must actually blend, and blending twice must differ from once --
/// otherwise the seam test above would pass for the wrong reason.
#[test]
fn fill_poly_alpha_blends_and_is_not_idempotent() {
    let mut cv = Canvas::new(8, 8, [0, 0, 0]);
    let sq = [(1, 1), (7, 1), (7, 7), (1, 7)];
    cv.fill_poly(&sq, [200, 200, 200], 128);
    let after_one = cv.get(3, 3);
    assert_ne!(after_one, [0, 0, 0], "half alpha must change the pixel");
    assert_ne!(after_one, [200, 200, 200], "half alpha must not be opaque");
    cv.fill_poly(&sq, [200, 200, 200], 128);
    assert_ne!(
        cv.get(3, 3),
        after_one,
        "a second blend must move the pixel; if not, the seam test is vacuous"
    );
}

/// A face at high zoom projects far off-canvas. The fill must clip, not panic,
/// and must not spend time scanning rows that cannot be seen.
#[test]
fn fill_poly_clips_instead_of_panicking() {
    let mut cv = Canvas::new(16, 16, [0, 0, 0]);
    cv.fill_poly(
        &[(-9000, -9000), (9000, -9000), (9000, 9000), (-9000, 9000)],
        [255, 0, 0],
        255,
    );
    assert_eq!(cv.get(8, 8), [255, 0, 0], "the canvas interior is covered");
    // degenerate inputs are no-ops, never panics
    cv.fill_poly(&[(0, 0), (5, 5)], [0, 255, 0], 255);
    cv.fill_poly(&[(0, 0), (5, 0), (5, 5)], [0, 255, 0], 0);
}

// ---------------------------------------------------------------------------
//  netfile -- storing a net and reading it back, added 2026-09-02
// ---------------------------------------------------------------------------

/// The round trip must return the geometry BIT FOR BIT, not merely close.
/// f64s go to disk as `to_bits()` precisely so this assertion can be about
/// bits; a decimal round trip is the one thing that could quietly alter the
/// value this file exists to preserve.
#[test]
fn netfile_round_trip_is_bit_identical() {
    let p = Params::default();
    let mut rng = Rng::new(0xC60);
    let st = State::seed_c60()
        .refine(Op::All, &p, &mut rng)
        .refine(Op::All, &p, &mut rng);

    let bytes = netfile::to_bytes(&st, Surface::Spherical);
    let (back, surf) = netfile::from_bytes(&bytes).expect("reads back");

    assert_eq!(surf, Surface::Spherical, "the surface mode survives");
    assert_eq!(back.faces.len(), st.faces.len(), "face count survives");
    for (a, b) in st.faces.iter().zip(back.faces.iter()) {
        assert_eq!(a.kind, b.kind);
        assert_eq!(a.level, b.level);
        assert_eq!(a.pts.len(), b.pts.len());
        for (va, vb) in a.pts.iter().zip(b.pts.iter()) {
            for k in 0..3 {
                assert_eq!(
                    va[k].to_bits(),
                    vb[k].to_bits(),
                    "coordinate {k} moved: {} -> {}",
                    va[k],
                    vb[k]
                );
            }
        }
    }
}

/// The invariants must hold on a LOADED net exactly as on a built one --
/// otherwise the file format has quietly changed the mesh while preserving
/// the numbers that describe it.
#[test]
fn a_loaded_net_measures_the_same_as_the_built_one() {
    let p = Params::default();
    let mut rng = Rng::new(7);
    let st = State::seed_c60()
        .refine(Op::All, &p, &mut rng)
        .refine(Op::All, &p, &mut rng);

    let (back, _) = netfile::from_bytes(&netfile::to_bytes(&st, Surface::Planar)).unwrap();
    let a = st.invariants().expect("built measures");
    let b = back.invariants().expect("loaded measures");
    assert_eq!(a.faces, b.faces);
    assert_eq!(a.pents, b.pents, "P=12 must survive the disk");
    assert_eq!(a.chi, b.chi, "chi must survive the disk");
    assert_eq!(st.census(), back.census(), "the census must agree");
}

/// The anchor is the SECOND WITNESS to P=12 -- independent of the `kind`
/// label -- so it has to survive the trip, and it is stored as one byte
/// rather than a String.
#[test]
fn the_anchor_witness_survives_as_one_byte() {
    let p = Params::default();
    let mut rng = Rng::new(1);
    let st = State::seed_c60().refine(Op::All, &p, &mut rng);
    let (back, _) = netfile::from_bytes(&netfile::to_bytes(&st, Surface::Planar)).unwrap();

    let count = |s: &State| {
        let mut v: Vec<&str> = s.faces.iter().filter_map(|f| f.anchor.as_deref()).collect();
        v.sort_unstable();
        v.dedup();
        v.len()
    };
    assert_eq!(count(&st), 12, "the built net has twelve anchors");
    assert_eq!(count(&back), 12, "and so does the loaded one");
}

/// `bytes_for` must predict the file size EXACTLY, so a save can be priced
/// before it is made -- the same rule the movie writer follows.
#[test]
fn bytes_for_predicts_the_file_size_exactly() {
    let p = Params::default();
    let mut rng = Rng::new(3);
    let st = State::seed_c60().refine(Op::All, &p, &mut rng);
    let c = st.census();
    let predicted = netfile::bytes_for(c.p, c.f - c.p);
    let actual = netfile::to_bytes(&st, Surface::Planar).len() as u64;
    assert_eq!(predicted, actual, "the price quoted must be the price paid");
}

/// Corruption must be REPORTED, never silently tolerated. A reader that
/// shrugs at a bad file is how a wrong mesh gets believed.
#[test]
fn a_damaged_net_is_refused_not_guessed() {
    let p = Params::default();
    let mut rng = Rng::new(5);
    let st = State::seed_c60().refine(Op::All, &p, &mut rng);
    let good = netfile::to_bytes(&st, Surface::Planar);

    let mut bad = good.clone();
    bad[0] = b'X';
    assert!(matches!(
        netfile::from_bytes(&bad),
        Err(netfile::NetError::BadMagic)
    ));

    let cut = &good[..good.len() - 40];
    assert!(
        matches!(
            netfile::from_bytes(cut),
            Err(netfile::NetError::Truncated { .. })
        ),
        "a truncated file must say so"
    );

    let mut arity = good.clone();
    arity[netfile::HEADER + 5] = 9; // no Goldberg face has nine sides
    assert!(matches!(
        netfile::from_bytes(&arity),
        Err(netfile::NetError::BadArity { .. })
    ));

    assert!(matches!(
        netfile::from_bytes(&[]),
        Err(netfile::NetError::Truncated { .. })
    ));
}

// ---------------------------------------------------------------------------
//  float_profile -- how close a number is to being made of ones and zeros
// ---------------------------------------------------------------------------

/// The numbers a binary machine holds for free must profile as free.
#[test]
fn powers_of_two_carry_no_mantissa_bits() {
    let p = bits::float_profile([1.0, 0.5, 0.25, 2.0, 4.0, -8.0]);
    assert_eq!(p.n, 6);
    assert_eq!(p.mantissa_ones, 0, "a power of two has an empty mantissa");
    assert_eq!(p.powers_of_two, 6);
    assert_eq!(p.worst, 0);
    assert_eq!(p.density(), 0.0, "the cheapest possible geometry");
}

/// And the ones it cannot hold exactly must cost, measurably.
#[test]
fn a_rounded_third_is_expensive_and_a_half_is_not() {
    let cheap = bits::float_profile([0.5]);
    let dear = bits::float_profile([1.0 / 3.0]);
    assert_eq!(cheap.mantissa_ones, 0);
    assert!(
        dear.mantissa_ones > 20,
        "1/3 needed a long tail, got {} bits",
        dear.mantissa_ones
    );
    assert!(dear.density() > cheap.density());
}

/// Zero is the one value that costs nothing anywhere, and it must not be
/// confused with a power of two even though its mantissa is also empty.
#[test]
fn zero_is_counted_as_zero_and_also_as_empty_mantissa() {
    let p = bits::float_profile([0.0, -0.0, 1.0]);
    assert_eq!(p.zeros, 2, "both signed zeros count");
    assert_eq!(p.powers_of_two, 3, "all three have an empty mantissa");
    assert_eq!(p.mantissa_ones, 0);
}

/// `density` must be a fraction of 52 bits, not of 64: the sign and exponent
/// are not part of what a value pays to be stored precisely.
#[test]
fn density_is_measured_against_the_mantissa_only() {
    // 1.5 = 0x3FF8000000000000 -- exactly one set mantissa bit
    let p = bits::float_profile([1.5]);
    assert_eq!(p.mantissa_ones, 1);
    assert!(
        (p.density() - 1.0 / 52.0).abs() < 1e-12,
        "density {} should be 1/52",
        p.density()
    );
    assert_eq!(bits::float_profile([] as [f64; 0]).density(), 0.0);
}

// ---------------------------------------------------------------------------
//  mobius -- the twist, and the claim it does NOT support
// ---------------------------------------------------------------------------

/// THE ONE THAT MATTERS. The browser logs `chi:'2->0'` and never computes it.
/// Bending points cannot change connectivity, so chi is untouched -- and this
/// port must say so out loud rather than inherit the claim.
#[test]
fn the_twist_moves_points_and_does_not_change_chi() {
    let p = Params::default();
    let mut rng = Rng::new(0xC60);
    let mut st = State::seed_c60().refine(Op::All, &p, &mut rng);

    let before = st.invariants().expect("measures before");
    let band = mobius::Band::default();
    let mut moved = 0usize;
    for f in st.faces.iter_mut() {
        for v in f.pts.iter_mut() {
            let m = mobius::sphere_to_mobius(*v, band);
            if m != *v {
                moved += 1;
            }
            *v = m;
        }
    }
    let after = st.invariants().expect("measures after");

    assert!(moved > 0, "the twist must actually move something");
    assert_eq!(
        before.chi, after.chi,
        "chi changed by bending points -- that is impossible, so something          else is wrong"
    );
    assert_eq!(after.chi, 2, "a bent sphere is still a sphere");
    assert_eq!(before.faces, after.faces, "no face may vanish by bending");
    assert_eq!(after.pents, 12, "and P=12 survives the twist");
}

/// What a genuine Mobius WOULD cost, in faces. chi=0 forces F = E - V, and the
/// gap against the faces you have is how many must die.
#[test]
fn a_real_mobius_would_cost_exactly_two_faces_on_the_c60() {
    // C60: V=60, E=90, F=32, chi=2
    let need = mobius::faces_for_chi_zero(60, 90).expect("E > V");
    assert_eq!(need, 30, "chi=0 forces F = 90 - 60 = 30");
    assert_eq!(32 - need, 2, "two faces must die -- the cost of the twist");
    assert_eq!(
        mobius::faces_for_chi_zero(90, 60),
        None,
        "V > E cannot close"
    );
}

/// The map must be well behaved where it is easy to be wrong: the origin has
/// no direction, and the poles sit at the clamp.
#[test]
fn the_map_survives_the_origin_and_the_poles() {
    let b = mobius::Band::default();
    assert_eq!(
        mobius::sphere_to_mobius([0.0, 0.0, 0.0], b),
        [b.r, 0.0, 0.0],
        "the origin goes to the reference point, never to NaN"
    );
    for p in [[0.0, 0.0, 1.0], [0.0, 0.0, -1.0], [0.0, 0.0, 1e-11]] {
        let q = mobius::sphere_to_mobius(p, b);
        assert!(q.iter().all(|c| c.is_finite()), "pole {p:?} produced {q:?}");
    }
}

/// The lerp must hit both ends exactly, or "t=0 is the sphere" is a lie.
#[test]
fn the_lerp_reaches_both_ends_exactly() {
    let a = [1.0, 2.0, 3.0];
    let b = [-4.0, 5.0, 0.5];
    assert_eq!(mobius::lerp(a, b, 0.0), a, "t=0 must BE the sphere");
    assert_eq!(mobius::lerp(a, b, 1.0), b, "t=1 must BE the band");
    let m = mobius::lerp(a, b, 0.5);
    for k in 0..3 {
        assert!((m[k] - (a[k] + b[k]) / 2.0).abs() < 1e-12);
    }
}

/// The twist must change the SHAPE without changing the SIZE. With the
/// browser's raw constants a 1.6-radius sphere becomes a 3.247 band -- the
/// picture doubles, walks off the view, and reads as "the mobius is linked to
/// the zoom", which is what it was.
#[test]
fn a_fitted_band_holds_the_spheres_size() {
    let p = Params {
        surface: Surface::Spherical,
        ..Params::default()
    };
    let mut rng = Rng::new(0xC60);
    let st = State::seed_c60().refine(Op::All, &p, &mut rng);
    let far = |b: mobius::Band| {
        st.faces
            .iter()
            .flat_map(|f| f.pts.iter())
            .map(|&v| {
                let q = mobius::sphere_to_mobius(v, b);
                (q[0] * q[0] + q[1] * q[1] + q[2] * q[2]).sqrt()
            })
            .fold(0.0f64, f64::max)
    };

    let raw = far(mobius::Band::default());
    assert!(
        raw > 1.9 * p.sphere_r,
        "the browser constants must still double it: {raw} vs r={}",
        p.sphere_r
    );

    let fitted = far(mobius::Band::fit(p.sphere_r));
    assert!(
        (fitted / p.sphere_r - 1.0).abs() < 0.05,
        "a fitted band must hold the size: {fitted} vs r={}",
        p.sphere_r
    );
    assert!(
        fitted <= mobius::Band::fit(p.sphere_r).reach(),
        "and never exceed its own stated reach"
    );

    // degenerate inputs fall back rather than producing a zero-size band
    assert_eq!(mobius::Band::fit(0.0), mobius::Band::default());
    assert_eq!(mobius::Band::fit(-1.0), mobius::Band::default());
}
