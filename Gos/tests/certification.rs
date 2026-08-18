//! Proof by kernel, not by claim.
//!
//! Every number here was produced by an independent derivation before the
//! Rust was written. If a test fails, the port changed the mathematics --
//! which is exactly what we want to hear about.

use goldberg_kernel::complex::{c_to_s2, C};
use goldberg_kernel::ladder;
use goldberg_kernel::ledger::{Lane, Ledger};
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
    assert_eq!(a.add(b), C::new(4.0, 2.0));
    assert_eq!(a.sub(b), C::new(2.0, 6.0));
    assert_eq!(a.mul(b), C::new(11.0, -2.0));
    assert_eq!(a.conj(), C::new(3.0, -4.0));
    assert_eq!(a.norm_sqr(), 25.0);
    assert_eq!(a.abs(), 5.0, "the 3-4-5 triangle is exact");
}

#[test]
fn i_squared_is_minus_one() {
    assert_eq!(C::I.mul(C::I), C::new(-1.0, 0.0));
}

#[test]
fn division_inverts_multiplication() {
    let a = C::new(3.0, 4.0);
    let b = C::new(1.0, -2.0);
    let q = a.mul(b).div(b);
    assert!((q.re - a.re).abs() < 1e-12 && (q.im - a.im).abs() < 1e-12);
}

#[test]
fn powi_matches_repeated_multiplication() {
    let z = C::new(0.7, -0.3);
    let mut acc = C::ONE;
    for _ in 0..7 {
        acc = acc.mul(z);
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
