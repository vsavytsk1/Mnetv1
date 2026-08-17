//! Proof by kernel, not by claim.
//!
//! Every number here was produced by an independent derivation before the
//! Rust was written. If a test fails, the port changed the mathematics --
//! which is exactly what we want to hear about.

use goldberg_kernel::complex::{c_to_s2, C};
use goldberg_kernel::ladder;
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
    assert_eq!(count.len(), 180, "60 vertices x degree 3 = 180 directed edges");
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
    assert!((PHI * PHI - (PHI + 1.0)).abs() < 1e-15, "phi^2 = phi + 1");
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
    assert!(ladder::exact(ladder::I128_MAX_N).is_ok(), "n = 92 must fit");
    let e = ladder::exact(ladder::I128_MAX_N + 1);
    assert!(e.is_err(), "n = 93 must report overflow, never wrap");
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
        assert!((n - 1.0).abs() < 1e-12, "off the sphere by {}", (n - 1.0).abs());
    }
}

#[test]
fn stereographic_fixes_the_poles() {
    assert_eq!(c_to_s2(C::ZERO), [0.0, 0.0, -1.0], "origin -> south pole");
    let far = c_to_s2(C::new(1e300, 0.0));
    assert!(far[2] > 0.999_999, "far away -> north pole, got z = {}", far[2]);
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
        assert!(c.abs() < 0.02, "mean {mean:?} should be near zero if uniform");
    }
}
