//! `mobius_extent` -- the number behind "the mobius is linked to the zoom".
//!
//! The browser hardcodes the band at `R = 2.5`, `W = 0.8`, because its sphere
//! is one fixed size. Ours has `sphere_r` as a live control. Measure both and
//! the coupling is obvious: the twist doubles the picture, so the shell walks
//! off the view and the operator reaches for the zoom.
//!
//! `Band::fit` scales the band to the sphere it came from, keeping the
//! browser's 2.5 : 0.8 proportions, so the twist changes the SHAPE without
//! changing the SIZE -- which is the only way to see what the twist did.
//!
//! LANE: DISPLAY. The map is transcendental; these are measurements of a
//! picture, not claims about a mesh.

use goldberg_kernel::genesis::{Op, Params, State, Surface};
use goldberg_kernel::mobius;
use goldberg_kernel::rng::Rng;

fn extent(pts: impl Iterator<Item = [f64; 3]>) -> (f64, [f64; 3]) {
    let (mut r, mut m) = (0.0f64, [0.0f64; 3]);
    for p in pts {
        r = r.max((p[0] * p[0] + p[1] * p[1] + p[2] * p[2]).sqrt());
        for k in 0..3 {
            m[k] = m[k].max(p[k].abs());
        }
    }
    (r, m)
}

fn main() {
    let p = Params {
        surface: Surface::Spherical,
        ..Params::default()
    };
    let mut rng = Rng::new(0xC60);
    let st = State::seed_c60().refine(Op::All, &p, &mut rng);

    let (rs, ms) = extent(st.faces.iter().flat_map(|f| f.pts.iter().copied()));
    println!("  sphere_r param      {:.3}", p.sphere_r);
    println!("  sphere  max |p|     {rs:.3}   per-axis {ms:.3?}");

    let raw = mobius::Band::default();
    let (rr, mr) = extent(
        st.faces
            .iter()
            .flat_map(|f| f.pts.iter().map(|&v| mobius::sphere_to_mobius(v, raw))),
    );
    println!(
        "\n  BROWSER CONSTANTS  R={} W={}  reach {}",
        raw.r,
        raw.w,
        raw.reach()
    );
    println!("  mobius  max |p|     {rr:.3}   per-axis {mr:.3?}");
    println!(
        "  ratio               {:.2}x  <- the picture GROWS, hence the zoom",
        rr / rs
    );

    let fit = mobius::Band::fit(p.sphere_r);
    let (rf, mf) = extent(
        st.faces
            .iter()
            .flat_map(|f| f.pts.iter().map(|&v| mobius::sphere_to_mobius(v, fit))),
    );
    println!(
        "\n  FITTED             R={:.3} W={:.3}  reach {:.3}",
        fit.r,
        fit.w,
        fit.reach()
    );
    println!("  mobius  max |p|     {rf:.3}   per-axis {mf:.3?}");
    println!(
        "  ratio               {:.2}x  <- the picture HOLDS its size",
        rf / rs
    );

    let xy = mf[0].max(mf[1]);
    println!(
        "\n  flatness  xy {:.3} vs z {:.3} = {:.1} : 1",
        xy,
        mf[2],
        xy / mf[2]
    );
    println!(
        "  A sphere looks the same from every angle and a flat ring does not,\n  \
         so PITCH shows during a twist what it could not show before. That is\n  \
         the geometry, not a bug."
    );
}
