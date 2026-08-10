#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENESIS WALLPAPER GENERATOR  v1.7
=================================================================================
v1.5 rendered the v8.1 refineFace operator, midRing and all. v1.6 keeps that
operator byte for byte and adds the three things v8.5.2 learned:

  1. THE GOLDEN CATALOGUE (Thea Lane B, certified closure).
     GK.buildGoldberg(k,l) ported exactly: icosahedron -> integer barycentric
     lattice -> weld -> convex hull -> dual. C20 C60 C140 C380 C980 C2580 C6740,
     plus C17660 and beyond, which the browser cannot reach.
     Every shell verified here at build time: V=20T, E=30T, F=10T+2, P=12, chi=2.

  2. THE FLIGHT LOCK. genesis' flCenterOn, ported -- and audited.
     genesis v8.5.2 computes  rx = -asin(dy).  The projection it feeds is
     y1 = y*cos(rx) - z1*sin(rx), which is zero only when rx = +asin(dy).
     The browser therefore centres a point only when dy = 0. On C60 that is
     4 of the 12 pentagons; on the other 8 the point lands 1.338 off-centre and
     half of those flip to the far side of the shell. Both signs ship here.
     FLIGHT_SIGN="fixed" centres every point; "genesis" reproduces the browser.
     The residual is printed per lock, so you never take it on faith.

  3. THE LOCK TABLE. python genesis_wallpaper_v1_6.py --locks
     Every lock on every shell, classified into distinct camera views by an
     icosahedral-axis signature, with the (rx, ry) each one needs. --locks-csv
     writes the full uncapped enumeration; the browser caps its dropdown at 240
     (Curse 35 for the DOM) and this does not have a DOM.

  ALSO IN 1.6
    - one colour table. GENESIS_CANVAS holds the browser's own rgba constants
      and BOTH renderers read it. No drift, no second palette to keep in sync.
    - genesis' ss>2 stroke gate, which v1.5 was missing: faces between 0.5 and
      2 px are filled and NOT stroked. It is why a dense shell reads as body
      rather than as wire.
    - vectorised cull + global painter sort. v1.5 sorted a python generator of
      millions of tuples and looped them one at a time; v1.6 does it in numpy.
    - the guillotine (Curse 35). Every refine predicts its face count from the
      recurrence and refuses out loud before it allocates.
    - the exact integer ladder, which is the whole point of doing this in
      python: Chromium's float64 stops being exact at n=39. Python does not.
    - ASCII source only (Curse 2). Verify: no byte above 0x7F in this file.

  pip install numpy pillow
  optional CUDA:      pip install cupy-cuda12x
  optional exact:     pip install matplotlib
  optional fast hull: pip install scipy      (falls back to a ported hull)

  python genesis_wallpaper_v1_6.py            render
  python genesis_wallpaper_v1_6.py --plan     capacity, before you allocate
  python genesis_wallpaper_v1_6.py --locks    the lock table, every shell
  python genesis_wallpaper_v1_6.py --ladder   the exact ladder vs the fence
  python genesis_wallpaper_v1_6.py --cert     reproducible math certificate

NEW IN 1.7 -- THE FRACTAL LANE
    python genesis_wallpaper_v1_7.py --fractal
  Box counting on the operator's own faces. The certified tower gives
  log V / log R = 2 exactly (V ~ T, R ~ sqrt T, no fit). The local refine
  hierarchy is then MEASURED the same way, from the SHIPPED refine() --
  never a replica (Curse 40). Reports b, s, the area ratio that has to
  hold for b to mean anything, and D = log b / log(1/s). It comes back 2,
  and that is the result: a surface operator tiling a surface is
  two-dimensional however deep the tree runs. In THEA fractal means
  HIERARCHY (K2); this is the number that says it is not more. The
  pentagons are the 0-dimensional part: twelve forever, density -> 0.
    --fractal-depth N   how many refines to walk (default 3)
    --fractal-op  all|hex|pent

P=12. chi=2. The price is always paid.
=================================================================================
"""
import sys, os, time, math, argparse

# =============================================================================
#  CONFIG  -- edit freely
# =============================================================================

# ---- the seed ---------------------------------------------------------------
#  GOLDEN (Thea Lane B, certified closure -- Goldberg-Coxeter (k,l), T=k^2+kl+l^2)
#     C20 C60 C140 C380 C980 C2580 C6740 C17660 C46260 C121020
#  LEGACY (v1.5 lineage, kept so old renders still reproduce)
#     dodec c60 c80 c180 c320
#  Both families carry exactly 12 pentagons. That is the family.
SEED          = "C60"

# ---- the operator (genesis v8.1 defaults) -----------------------------------
INNER_SCALE   = 0.1      # inner[i] = lerp(c, pts[i], INNER_SCALE)
MID_SCALE     = 0.1    # midRing[i] = lerp(c, edgeMid, MID_SCALE)
                          #   > INNER_SCALE -> crescent GAP     (the rosette)
                          #   < INNER_SCALE -> crescent OVERLAP (layered)
                          #   = INNER_SCALE -> flat, still open
JITTER        = 0.00      # 0.00 - 0.30
SPHERE_R      = 1.6       # genesis builds every shell at radius 1.6
SPHERICAL     = True      # False = 'planar' mode, no reprojection

# ---- order of operations, top to bottom -------------------------------------
#  "all" = REFINE ALL, "hex" = REFINE 6s, "pent" = REFINE 5s
#     REFINE ALL   P stays 12, H' = 5P + 7H  ->  F' = 7F - 12
#     REFINE 6s    pentagons untouched       ->  F' = 7F - 72
#  Your screenshot's lane, reproduced exactly:
#     C60 F=32 -> all -> 212 -> 6s x5 -> 1412, 9812, 68612, 480212, 3361412
OPS           = ["all"]*1 + ["hex"]*7


# ---- FLIGHT LOCK ------------------------------------------------------------
#  None, or a label from --locks. Sets CAM_RX / CAM_RY so that point faces you.
#     FLIGHT_LOCK = "pentagon 7"      the one in your screenshot
#     FLIGHT_LOCK = "vertex 379"
#     FLIGHT_LOCK = "hexagon 3"
#     FLIGHT_LOCK = "axis 5-fold"     canonical icosahedral axes
#  The lock is computed on the SEED, before refinement -- the refined mesh sits
#  on the same sphere, so a seed lock is a lock on every generation of it.
FLIGHT_LOCK   = "vertex 379"   # None | "pentagon 7" | "vertex 379" | "hexagon 3" | "axis 5-fold"
FLIGHT_SIGN   = "fixed"   # "fixed"   rx=+asin(dy)  -- centres every point
                          # "genesis" rx=-asin(dy)  -- reproduces v8.5.2 verbatim

# ---- MOBIUS -----------------------------------------------------------------
#  genesis' sphereToMobius, ported exactly:
#     theta=atan2(y,x)  phi=acos(z/r)   u=theta+PI   v=(phi/PI-0.5)*2*W
#     -> ((R + v*cos(u/2))*cos u, (R + v*cos(u/2))*sin u, v*sin(u/2))
#  MOBIUS_WHEN="first" twists the SEED and then refines over the twisted
#  surface with projectToSphere still on, so children snap back to SPHERE_R
#  while inherited corners stay out where the twist put them. That mismatch is
#  the spikes, and it is genesis' own order. "last" twists after refining.
MOBIUS_T      = 0.0       # 0 = off, 1 = full strip
MOBIUS_R      = 2.5
MOBIUS_W      = 0.8
MOBIUS_WHEN   = "first"   # "first" | "last"
MOBIUS_PROJECT = True     # True = keep projectToSphere -> spikes (genesis)

# ---- renderer ---------------------------------------------------------------
RENDERER      = "exact"   # "exact"    the canvas, ported: ortho, culled,
                          #            painter-sorted, source-over. needs matplotlib.
                          # "additive" the wallpaper instrument: additive lines,
                          #            scales past a hundred million faces, glows.

# ---- camera, EXACT mode -- these are genesis' own `cam` ---------------------
#  project() is ORTHOGRAPHIC out here. No perspective divide at all:
#     x1 = x*cos(ry) - z*sin(ry);   z1 = x*sin(ry) + z*cos(ry)
#     y1 = y*cos(rx) - z1*sin(rx);  z2 = y*sin(rx) + z1*cos(rx)
#     screen = (W/2 + x1*zoom, H/2 - y1*zoom),  depth = z2
#  A distance and an FOV cannot imitate that; they change the silhouette.
CAM_RX        = 0.30      # cam.rx -- OVERRIDDEN by FLIGHT_LOCK when set
CAM_RY        = 0.00      # cam.ry -- OVERRIDDEN by FLIGHT_LOCK when set
CAM_ZOOM      = 3000.0     # the ZOOM slider (your screenshot reads 783)
CAM_ATOM      = 0.010      # the ATOM slider. genesis gates atoms at >0.2
SUPERSAMPLE   = 2         # render NxN then box-filter down

# ---- camera, ADDITIVE mode --------------------------------------------------
ROT_X         = 0.42      # radians, pitch. FLIGHT_LOCK overrides with rx
ROT_Y         = 0.85      # radians, yaw.   FLIGHT_LOCK overrides with ry
ROT_Z         = 0.00      # radians, roll
CAM_DIST      = 2.05      # * SPHERE_R.  < 1.0 puts you inside the shell
FOV_DEG       = 62.0
ZOOM          = 1.00

# ---- output -----------------------------------------------------------------
WIDTH         = 7680      # 5120x2880 = 5K.  7680x4320 = 8K (needs ~1.5 GB more)
HEIGHT        = 4320
JPG_QUALITY   = 97
OUT           = None      # None = auto-named
OUT_DIR       = "."       # portable. Curse 38: never hardcode a sandbox path.

# ---- look -------------------------------------------------------------------
PALETTE       = "genesis_canvas"  # genesis_canvas | genesis_true | spectrum
                                  # | bone | ember
PENT_BOOST    = None      # None = take it from the palette
GAIN          = None
GAMMA         = None
TONE          = None
DRAW_HISTORY  = True      # additive only: keep every generation's edges

TONE_NORM     = "luma"    # "luma"        curve max(R,G,B) once, scale RGB by the
                          #               gain -> hue is EXACTLY the palette's
                          # "shared"      one shared max, curve per channel
                          # "per_channel" v1.5's behaviour. Shifts hue; kept so
                          #               v1.5 renders still reproduce.
# ATOMS, additive mode. NOTE what the browser actually does: cam.atom defaults
# to 0.1 and the draw gate is `cam.atom > 0.2` -- so at its own defaults genesis
# renders NO atoms at all, which is what the reference screenshots show (their
# ATOM slider reads 0.1). ATOM_SIZE is this instrument's own knob in pixels, not
# genesis' cam.atom, and a disc of radius 3 px carries ~40x the energy of an
# edge sample. Turning it up is a choice; it pulls the render toward the atom
# colour (0,255,213) and away from the edge colour (0,180,255). Default off, to
# match the browser. Measured G/B: 0.7064 off vs 0.9842 on (browser 0.7059).
ATOM_SIZE     = 0.0       # additive-mode vertex disc radius, px. 0 = browser default.
ATOM_MIN_PX   = 5.0       # genesis' own gate: ss = |proj(p0)-proj(p1)| > 5

# ---- compute ----------------------------------------------------------------
USE_GPU       = True          # GPU for rasterising only; the mesh lives in RAM
REFINE_CHUNK  = 2_000_000     # parent faces per refine batch; caps transient RAM
CHUNK_SAMPLES = 20_000_000    # raster samples per upload. 6 GB VRAM -> 20M
MEM_BUDGET_GB = "auto"        # "auto" = 82% of detected system RAM, or a number

# ---- the guillotine (Curse 35 -- predict before you allocate) ---------------
#  A correct kernel with no ceiling is a loaded gun pointed at the tab. This one
#  caps itself, out loud, with the number. The math is right past these walls;
#  the machine is what ends.
FACE_BUDGET       = 600_000_000   # hard refuse: no generation may exceed this
EXACT_FACE_BUDGET = 600_000_000     # matplotlib's honest ceiling for RENDERER="exact"
                                  # past it, use RENDERER="additive"
HULL_VERT_BUDGET  = 40_000        # geodesic points the seed hull may chew

# =============================================================================
#  end CONFIG
# =============================================================================

# -----------------------------------------------------------------------------
#  THE COLOUR TABLE -- one source of truth, lifted from the v8.5.2 draw path.
#
#    cx.fillStyle   = '#050508'
#    pent: fill rgba(193, 74, 59, alpha*0.4)   stroke rgba(255,105,180, alpha)
#    hex : fill rgba(  0, 40, 60, alpha*0.3)   stroke rgba(  0,180,255, alpha*0.6)
#    atom: pent rgba(255,105,180, alpha)       hex    rgba(  0,255,213, alpha*0.6)
#    alpha  = 0.15 + clamp((depth+2)/4, 0, 1)*0.5
#    stroke only if screenSize > 2      lineWidth = pent ? 1.5 : 0.5
#    atoms  only if cam.atom > 0.2 and screenSize > 5      r = atom*(pent?2:1.2)
#
#  BOTH renderers read this dict. v1.5 kept two tables and they drifted.
# -----------------------------------------------------------------------------
GENESIS_CANVAS = dict(
    bg         = (5, 5, 8),
    hex_fill   = (0, 40, 60),     hex_fill_a  = 0.3,
    pent_fill  = (193, 74, 59),   pent_fill_a = 0.4,
    hex_edge   = (0, 180, 255),   hex_edge_a  = 0.6,   hex_lw  = 0.5,
    pent_edge  = (255, 105, 180), pent_edge_a = 1.0,   pent_lw = 1.5,
    hex_atom   = (0, 255, 213),   hex_atom_a  = 0.6,
    pent_atom  = (255, 105, 180), pent_atom_a = 1.0,
    stroke_ss  = 2.0,             # genesis: if(ss>2) stroke
    atom_ss    = 5.0,             # genesis: if(cam.atom>0.2 && ss>5)
    atom_gate  = 0.2,
    cull_ss    = 0.5,             # genesis: sub-pixel cull
    alpha_base = 0.15, alpha_span = 0.5,
)
_G = GENESIS_CANVAS

PALETTES = {
 # the browser's own constants, for the additive instrument. Same rgb as _G,
 # so a change in one place moves both renderers together.
 "genesis_canvas": dict(
    mode="facetype", bg=_G["bg"],
    hex_edge=_G["hex_edge"],   hex_mul=_G["hex_edge_a"],
    pent_edge=_G["pent_edge"], pent_mul=_G["pent_edge_a"],
    hex_atom=_G["hex_atom"],   hex_atom_mul=_G["hex_atom_a"],
    pent_atom=_G["pent_atom"], pent_atom_mul=_G["pent_atom_a"],
    gain=0.34, tone="asinh", gamma=0.82, pent=1.0),
 "genesis_true": dict(          # v1.5's name, kept so old renders reproduce
    mode="facetype", bg=(5,5,8),
    hex_edge=(0,180,255),    hex_mul=0.6,
    pent_edge=(255,105,180), pent_mul=1.0,
    hex_atom=(0,255,213),    hex_atom_mul=0.6,
    pent_atom=(255,105,180), pent_atom_mul=1.0,
    gain=0.34, tone="asinh", gamma=0.82, pent=1.0),
 "genesis": dict(
    mode="generation",
    colors=[(0.02,0.20,0.36),(0.03,0.31,0.52),(0.04,0.44,0.68),(0.07,0.58,0.84),
            (0.14,0.72,0.94),(0.30,0.86,1.00),(0.60,0.96,1.00)],
    bg=(3,8,14), gain=0.42, tone="asinh", gamma=0.80, pent=1.7),
 "spectrum": dict(
    mode="generation",
    colors=[(0.06,0.34,0.55),(0.05,0.46,0.78),(0.04,0.62,0.95),(0.10,0.80,1.00),
            (0.35,0.94,1.00),(0.70,1.00,0.98),(1.00,0.99,0.80)],
    bg=(2,4,8), gain=0.90, tone="asinh", gamma=0.62, pent=2.6),
 "bone": dict(
    mode="generation",
    colors=[(0.28,0.24,0.16),(0.42,0.36,0.24),(0.58,0.50,0.34),(0.74,0.65,0.45),
            (0.88,0.79,0.58),(0.97,0.90,0.72),(1.00,0.97,0.86)],
    bg=(6,6,15), gain=0.55, tone="asinh", gamma=0.74, pent=2.0),
 "ember": dict(
    mode="generation",
    colors=[(0.30,0.05,0.03),(0.48,0.10,0.04),(0.68,0.20,0.05),(0.86,0.36,0.07),
            (0.97,0.55,0.14),(1.00,0.75,0.34),(1.00,0.93,0.72)],
    bg=(8,3,3), gain=0.60, tone="asinh", gamma=0.72, pent=2.2),
}

# =============================================================================
#  PART 0 -- THE LIGHT MATRIX, EXACT
#
#  THEA v3.0, Parts I-IV. This is the reason the generator is in python at all.
#  Chromium carries the ladder in BigInt for the integers and float64 for
#  everything else; python carries unbounded integers natively, so the exact
#  lane never ends here. Everything below is EXACT integer arithmetic -- no
#  float appears until a ratio is asked for.
#
#     Euler + trivalence + {5,6} faces           ->  P = 12       (forced)
#     T = k^2 + k*l + l^2                            hexagonal norm
#     V = 20T, E = 30T, F = 10T+2, H = 10(T-1)       closure counts
#     (k,l) -> (k+l, k)                              the golden selector
#     T_{n+3} = 2T_{n+2} + 2T_{n+1} - T_n            the ladder
#     M_light = [[1,2,1,0],[1,1,0,0],[1,0,0,0],[0,0,0,1]]
#     char poly = (x-1)(x+1)(x^2-3x+1),  spec = {phi^2, 1, -1, phi^-2}
# =============================================================================
PHI = (1.0 + 5.0 ** 0.5) / 2.0
LN_PHI2 = math.log(PHI * PHI)          # 0.962423650  -- one rung
EPS64 = sys.float_info.epsilon         # 2.220446049250313e-16
L_PLANCK, L_HORIZON = 1.616255e-35, 4.4e26


def hex_norm(k, l):
    """T = k^2 + k*l + l^2. EXACT, integers only."""
    return k * k + k * l + l * l


def topology_from_T(T):
    """The closure counts. EXACT. chi is computed, never assumed."""
    V, E = 20 * T, 30 * T
    P, H = 12, 10 * (T - 1)
    F = P + H
    return dict(T=T, V=V, E=E, F=F, P=P, H=H, chi=V - E + F)


def golden_next(k, l):
    """The Fibonacci selector. (k,l) -> (k+l, k). EXACT."""
    return k + l, k


def ladder_exact(n):
    """The golden ladder in exact integers. No BigInt fence -- python has none."""
    k, l, out = 1, 0, []
    for _ in range(n):
        out.append(hex_norm(k, l))
        k, l = golden_next(k, l)
    return out


def ladder_f64_recurrence(n):
    """The same recurrence advanced in float64. Chromium's lane."""
    T = [1.0, 3.0, 7.0]
    for i in range(max(0, n - 3)):
        T.append(2 * T[i + 2] + 2 * T[i + 1] - T[i])
    return T[:n]


def ladder_f64_closed(n):
    """T_n = (2/5)(phi^(2n+2) + phi^(-2n-2)) - (1/5)(-1)^n, in float64."""
    return [(2.0 / 5.0) * (PHI ** (2 * i + 2) + PHI ** (-2 * i - 2))
            - (1.0 / 5.0) * ((-1.0) ** i) for i in range(n)]


def light_matrix_charpoly():
    """char poly of M_light by exact integer Leverrier-Faddeev.
    Returns coefficients [c0..c4] of c0*x^4 + c1*x^3 + ... , c0 = 1."""
    M = [[1, 2, 1, 0], [1, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]]

    def matmul(A, B):
        return [[sum(A[i][t] * B[t][j] for t in range(4)) for j in range(4)]
                for i in range(4)]

    def trace(A):
        return sum(A[i][i] for i in range(4))

    Ak, coeffs = [row[:] for row in M], [1]
    c = -trace(Ak)
    coeffs.append(c)
    for k in range(2, 5):
        for i in range(4):
            Ak[i][i] += c
        Ak = matmul(M, Ak)
        c = -trace(Ak) // k          # exact: the division is always exact here
        coeffs.append(c)
    return coeffs


def rungs_of(u):
    """resolving power of a relative uncertainty u, in rungs of phi^2."""
    return math.log(1.0 / u) / LN_PHI2


# -----------------------------------------------------------------------------
#  THE GOLDEN CATALOGUE -- Thea Lane B, certified closure.
#  Indices 0..6 are exactly v8.5.2's GOLDEN_CATALOG buttons. 7+ are what the
#  browser will not attempt and this will.
# -----------------------------------------------------------------------------
def golden_catalog(n=10):
    out, k, l = [], 1, 0
    for i in range(n):
        T = hex_norm(k, l)
        t = topology_from_T(T)
        rec = dict(t)
        rec.update(idx=i, k=k, l=l, name="C%d" % t["V"])
        out.append(rec)
        k, l = golden_next(k, l)
    return out


GOLDEN = golden_catalog(10)
GOLDEN_BY_NAME = {g["name"]: g for g in GOLDEN}


def print_ladder(n=170):
    """--ladder : the exact lane, and where the browser's lane stops being exact."""
    ex = ladder_exact(n)
    rec = ladder_f64_recurrence(n)
    cls = ladder_f64_closed(n)
    print("=" * 79)
    print("  THE LIGHT MATRIX -- the exact ladder, and the fence")
    print("=" * 79)

    cp = light_matrix_charpoly()
    print("  M_light char poly (EXACT, integer Leverrier-Faddeev)")
    print("      x^4 %+d x^3 %+d x^2 %+d x %+d" % (cp[1], cp[2], cp[3], cp[4]))
    print("      factors as (x-1)(x+1)(x^2-3x+1)   ->  spec = {phi^2, 1, -1, phi^-2}")
    # verify by EXPANDING the claimed factorisation, not by trusting a constant
    # someone typed once. (x-1)(x+1) = [1,0,-1];  (x^2-3x+1) = [1,-3,1].
    def _conv(a, b):
        out = [0] * (len(a) + len(b) - 1)
        for i, u in enumerate(a):
            for j, v in enumerate(b):
                out[i + j] += u * v
        return out
    expect = _conv(_conv([1, -1], [1, 1]), [1, -3, 1])
    ok = (cp == expect)
    print("      expanding (x-1)(x+1)(x^2-3x+1) gives  x^4 %+d x^3 %+d x^2 %+d x %+d"
          % (expect[1], expect[2], expect[3], expect[4]))
    print("      match : %s        (phi^2 + phi^-2 = 3, phi^2 * phi^-2 = 1)"
          % ("PASS" if ok else "FAIL"))
    print()

    print("  the golden shells (V=20T, E=30T, F=10T+2, P=12, chi=2 -- all EXACT)")
    print("  %-3s %-9s %-8s %14s %14s %14s %6s" % ("n", "(k,l)", "name", "T", "V", "F", "chi"))
    print("  " + "-" * 73)
    for g in GOLDEN[:8]:
        print("  %-3d (%2d,%2d)   %-8s %14s %14s %14s %6d"
              % (g["idx"], g["k"], g["l"], g["name"],
                 "{:,}".format(g["T"]), "{:,}".format(g["V"]),
                 "{:,}".format(g["F"]), g["chi"]))
    print()

    # where float64 stops being EXACT -- not accurate, exact.
    n53 = next((i for i, t in enumerate(ex) if t > 2 ** 53), None)
    n_ladder = math.log(L_HORIZON / L_PLANCK) / LN_PHI2
    n_chart = rungs_of(EPS64)
    bits147 = ex[147].bit_length() if len(ex) > 147 else None

    print("  THE CHROMIUM FENCE -- computed here, not quoted")
    print("  %-52s %s" % ("one rung  phi^2", "%.9f   ln = %.9f" % (PHI * PHI, LN_PHI2)))
    print("  %-52s %.1f rungs" % ("Planck -> observable horizon", n_ladder))
    print("  %-52s %.1f rungs" % ("one float64 chart  ln(1/eps)/ln(phi^2)", n_chart))
    print("  %-52s %d" % ("charts required to span it", math.ceil(n_ladder / n_chart)))
    print("  %-52s n = %s" % ("exact integer T_n first exceeds 2^53 at", n53))
    print("  %-52s delta = %.1f rung" % ("two independent derivations of the same wall",
                                         abs(n53 - n_chart)))
    if bits147:
        print("  %-52s %d bits   (float64 gives 53)"
              % ("mantissa bits to carry T_147 exactly", bits147))
    print()

    # the compounding-delta prediction, and its refutation
    d_rec = [abs(rec[i] - ex[i]) / ex[i] for i in range(n)]
    d_cls = [abs(cls[i] - ex[i]) / ex[i] for i in range(n)]
    tail = min(n, 148)
    max_r = max(d_rec[40:tail]) if tail > 40 else 0.0
    max_c = max(d_cls[40:tail]) if tail > 40 else 0.0
    print("  THE COMPOUNDING DELTA -- predicted to blow up, measured, refuted")
    print("  %-52s %.2e" % ("float64 recurrence, worst rel err past the wall", max_r))
    print("  %-52s %.2e  (x%.1f WORSE)"
          % ("float64 closed form, worst rel err past the wall", max_c,
             max_c / max(max_r, 1e-300)))
    print("  %-52s %s" % ("delta compounds?", "NO -- forward-stable toward phi^2"))
    print("  %-52s %s" % ("what actually dies at the wall",
                          "EXACTNESS. V=20T stops landing on an integer."))
    print()
    print("  PYTHON'S LANE: unbounded integers. T_%d has %d digits and is exact."
          % (n - 1, len(str(ex[-1]))))
    print("  There is no fence here. That is the whole reason this is not a browser.")
    print("=" * 79)


# =============================================================================
#  backend, and the progress bar
# =============================================================================
xp = None
GPU = False
HOST_RAM_GB = 0.0
HAVE_SCIPY = None


def _detect_ram():
    """total system RAM in GB, without needing psutil"""
    try:
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 2 ** 30
    except (ValueError, OSError, AttributeError):
        pass
    try:                                    # windows
        import ctypes

        class MS(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = MS()
        m.dwLength = ctypes.sizeof(MS)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
        return m.ullTotalPhys / 2 ** 30
    except Exception:
        return 16.0


def _pick_backend(quiet=False):
    global xp, GPU, HOST_RAM_GB, MEM_BUDGET_GB
    HOST_RAM_GB = _detect_ram()
    if MEM_BUDGET_GB == "auto":
        MEM_BUDGET_GB = round(HOST_RAM_GB * 0.82, 1)
    if not quiet:
        where = "  [Colab]" if ("COLAB_GPU" in os.environ or os.path.isdir("/content")) else ""
        print("  host    : %.1f GB RAM%s   mesh budget %.1f GB"
              % (HOST_RAM_GB, where, MEM_BUDGET_GB))
    if USE_GPU:
        try:
            import cupy
            cupy.zeros(1)
            xp, GPU = cupy, True
            dev = cupy.cuda.runtime.getDeviceProperties(0)
            free, total = cupy.cuda.runtime.memGetInfo()
            if not quiet:
                print("  backend : CUDA  %s  %.1f GB (%.1f free)"
                      % (dev["name"].decode(), total / 2 ** 30, free / 2 ** 30))
            return
        except Exception as e:
            if not quiet:
                print("  backend : no CUDA device (%s) -> NumPy raster" % type(e).__name__)
    import numpy
    xp, GPU = numpy, False
    if not quiet:
        print("  backend : NumPy (CPU)")


import numpy as np


def _have_scipy():
    global HAVE_SCIPY
    if HAVE_SCIPY is None:
        try:
            from scipy.spatial import ConvexHull  # noqa: F401
            HAVE_SCIPY = True
        except ImportError:
            HAVE_SCIPY = False
    return HAVE_SCIPY


class Bar:
    def __init__(self, total, label, width=34):
        self.total, self.label, self.width = max(1, total), label, width
        self.n, self.t0, self.last = 0, time.time(), 0.0

    def step(self, k=1):
        self.n += k
        now = time.time()
        if now - self.last < 0.08 and self.n < self.total:
            return
        self.last = now
        frac = min(1.0, self.n / self.total)
        el = now - self.t0
        eta = (el / frac - el) if frac > 1e-9 else 0.0
        fill = int(self.width * frac)
        bar = "#" * fill + "-" * (self.width - fill)
        sys.stdout.write("\r  %-22s [%s] %5.1f%%  %6.1fs  eta %5.1fs   "
                         % (self.label, bar, 100 * frac, el, eta))
        sys.stdout.flush()

    def done(self, msg=""):
        el = time.time() - self.t0
        sys.stdout.write("\r  %-22s [%s] 100.0%%  %6.1fs  %s\n"
                         % (self.label, "#" * self.width, el, msg))
        sys.stdout.flush()


def human(n):
    for u in ("", "K", "M", "G"):
        if abs(n) < 1000:
            return ("{:,.0f}".format(n) if u == "" else "%.1f%s" % (n, u))
        n /= 1000.0
    return "%.1fT" % n


# =============================================================================
#  PART 1 -- SEEDS
#
#  LANE B, the golden catalogue: GK.buildGoldberg(k,l,radius) from v8.5.2,
#  ported step for step. The browser's comment is worth repeating, because it
#  is the reason this is a hull and not a tiling:
#
#      "Robust for chiral (Class III) shells via convex hull of the cospherical
#       lattice points (per-face unit-tri tiling FAILS there)."
#
#  C140 (2,1), C380 (3,2), C980 (5,3), C2580 (8,5), C6740 (13,8) are all
#  chiral. The hull is what makes them close.
#
#  LANE A, the legacy seeds: v1.5's geodesic+dual path, kept byte for byte so
#  that every render made with v1.5 still reproduces here.
# =============================================================================

def _norm(a):
    L = np.linalg.norm(a, axis=-1, keepdims=True)
    return a / np.where(L < 1e-12, 1.0, L)


def _icosahedron_gk():
    """v8.5.2 _icosahedron(): the same 12 vertices, the same 20 faces, in the
    same order, with the same outward orientation fix. Order matters -- it is
    what makes 'pentagon 7' mean the same pentagon here as in the browser."""
    p = PHI
    raw = [[-1, p, 0], [1, p, 0], [-1, -p, 0], [1, -p, 0],
           [0, -1, p], [0, 1, p], [0, -1, -p], [0, 1, -p],
           [p, 0, -1], [p, 0, 1], [-p, 0, -1], [-p, 0, 1]]
    s = math.sqrt(1.0 + p * p)
    verts = np.array(raw, np.float64) / s
    faces = [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
             [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
             [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
             [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]]
    out = []
    for f in faces:
        a, b, c = verts[f[0]], verts[f[1]], verts[f[2]]
        nx = np.cross(b - a, c - a)
        if nx @ (a + b + c) > 0:
            out.append(tuple(f))
        else:
            out.append((f[0], f[2], f[1]))
    return verts, out


def _bary_int(i, j, k, l):
    """exact integer barycentric numerators (over T) of lattice point (i,j).
    v8.5.2 _baryInt, verbatim. Integers throughout -- no float test decides
    whether a lattice point is inside the master triangle."""
    b1 = i * (k + l) + j * l
    b2 = k * j - l * i
    T = k * k + k * l + l * l
    return (T - b1 - b2, b1, b2, T)


def _hull_scipy(P):
    from scipy.spatial import ConvexHull
    h = ConvexHull(P)
    tris = []
    for s in h.simplices:
        a, b, c = P[s[0]], P[s[1]], P[s[2]]
        # cospherical about the origin -> outward iff normal agrees with a
        tris.append((int(s[0]), int(s[1]), int(s[2])) if np.cross(b - a, c - a) @ a > 0
                    else (int(s[0]), int(s[2]), int(s[1])))
    return tris


def _hull_ported(P, bar=None):
    """v8.5.2 _convexHull(), ported. Incremental, with the visibility test
    vectorised over faces so that a shell the browser needs seconds for lands
    in well under one. Same algorithm, same output, different arithmetic
    schedule -- Path X: the slow one stays available to check the fast one."""
    n = len(P)
    i0 = 0
    i1 = next(i for i in range(1, n) if np.dot(P[i] - P[i0], P[i] - P[i0]) > 1e-12)
    i2 = next(i for i in range(1, n)
              if i != i1 and np.dot(np.cross(P[i1] - P[i0], P[i] - P[i0]),
                                    np.cross(P[i1] - P[i0], P[i] - P[i0])) > 1e-16)
    nrm = np.cross(P[i1] - P[i0], P[i2] - P[i0])
    i3 = next(i for i in range(n)
              if i not in (i0, i1, i2) and abs(nrm @ (P[i] - P[i0])) > 1e-9)
    cen4 = (P[i0] + P[i1] + P[i2] + P[i3]) / 4.0
    faces = []
    for t in ((i0, i1, i2), (i0, i1, i3), (i0, i2, i3), (i1, i2, i3)):
        nx = np.cross(P[t[1]] - P[t[0]], P[t[2]] - P[t[0]])
        faces.append(t if nx @ (P[t[0]] - cen4) > 0 else (t[0], t[2], t[1]))
    used = {i0, i1, i2, i3}
    for p in range(n):
        if p in used:
            if bar:
                bar.step()
            continue
        Fa = np.asarray(faces, np.int64)
        A, B, C = P[Fa[:, 0]], P[Fa[:, 1]], P[Fa[:, 2]]
        NX = np.cross(B - A, C - A)
        vis = np.einsum("ij,ij->i", NX, P[p] - A) > 1e-12
        if not vis.any():
            if bar:
                bar.step()
            continue
        ec = set()
        for f in Fa[vis]:
            ec.add((f[0], f[1]))
            ec.add((f[1], f[2]))
            ec.add((f[2], f[0]))
        horizon = [e for e in ec if (e[1], e[0]) not in ec]
        faces = [tuple(f) for f in Fa[~vis]]
        for a, b in horizon:
            faces.append((int(a), int(b), p))
        used.add(p)
        if bar:
            bar.step()
    return faces


def build_goldberg(k, l, R=None, verbose=True):
    """GK.buildGoldberg(k, l, radius). Returns (P, H, info).

    P = (np,5,3) pentagons, H = (nh,6,3) hexagons -- the same split v1.5's
    operator consumes, so the golden shells drop straight into the old lane.
    """
    R = SPHERE_R if R is None else R
    T = hex_norm(k, l)
    topo = topology_from_T(T)

    # Curse 35: predict the hull's bill BEFORE building it. 10T+2 cospherical
    # points, and the ported hull is O(n^2) in the worst case.
    n_geo = 10 * T + 2
    if n_geo > HULL_VERT_BUDGET:
        raise SystemExit(
            "  HALT: Goldberg(%d,%d) needs a hull over %s points > HULL_VERT_BUDGET %s.\n"
            "        The math is fine -- V=20T=%s, P=12, chi=2 all hold. The HULL is\n"
            "        what ends. Raise HULL_VERT_BUDGET if you have the patience."
            % (k, l, "{:,}".format(n_geo), "{:,}".format(HULL_VERT_BUDGET),
               "{:,}".format(topo["V"])))

    ico_v, ico_f = _icosahedron_gk()
    lo, hi = -l - 2, k + l + 2

    # lattice points inside-or-on the master triangle (exact integer test)
    lat = [(i, j) for i in range(lo, hi + 1) for j in range(lo, hi + 1)
           if all(v >= 0 for v in _bary_int(i, j, k, l)[:3])]

    # map each (face, lattice pt) -> sphere, dedup by rounded 3D key (weld)
    Q = 1e6
    gmap, gverts = {}, []
    for f in ico_f:
        pa, pb, pc = ico_v[f[0]], ico_v[f[1]], ico_v[f[2]]
        for (i, j) in lat:
            b0, b1, b2, TT = _bary_int(i, j, k, l)
            p = (b0 / TT) * pa + (b1 / TT) * pb + (b2 / TT) * pc
            L = np.linalg.norm(p)
            p = p * (R / (L if L > 1e-12 else 1.0))
            key = (round(p[0] * Q), round(p[1] * Q), round(p[2] * Q))
            if key not in gmap:
                gmap[key] = len(gverts)
                gverts.append(p)
    gverts = np.array(gverts, np.float64)

    if len(gverts) != n_geo:
        raise SystemExit("  WELD MISMATCH: got %d geodesic vertices, exact says %d.\n"
                         "  Refusing to build a shell whose closure is not certified."
                         % (len(gverts), n_geo))

    # geodesic triangulation = convex hull of the cospherical geodesic vertices
    t0 = time.time()
    if _have_scipy():
        gtris = _hull_scipy(gverts)
        how = "scipy/qhull"
    else:
        bar = Bar(len(gverts), "seed hull (ported)") if verbose and len(gverts) > 800 else None
        gtris = _hull_ported(gverts, bar)
        if bar:
            bar.done("%d triangles" % len(gtris))
        how = "ported v8.5.2 hull"
    hull_ms = (time.time() - t0) * 1000.0

    # DUAL -> fullerene: vertex = geodesic-triangle centroid on the sphere
    G = np.asarray(gtris, np.int64)
    fv = (gverts[G[:, 0]] + gverts[G[:, 1]] + gverts[G[:, 2]]) / 3.0
    fv = _norm(fv) * R

    around = [[] for _ in range(len(gverts))]
    for ti, t in enumerate(gtris):
        around[t[0]].append(ti)
        around[t[1]].append(ti)
        around[t[2]].append(ti)

    pent, hexa, ordered = [], [], []
    for g in range(len(gverts)):
        tl = around[g]
        if not tl:
            continue
        nrm = gverts[g] / np.linalg.norm(gverts[g])
        ref = np.array([1.0, 0, 0]) if abs(nrm[0]) < 0.9 else np.array([0.0, 1, 0])
        tan = np.cross(nrm, ref)
        tan = tan / np.linalg.norm(tan)
        bit = np.cross(nrm, tan)
        d = fv[tl] - nrm
        ang = np.arctan2(d @ bit, d @ tan)
        ring = [tl[i] for i in np.argsort(ang, kind="stable")]
        pts = fv[ring]
        kind = "pent" if len(ring) == 5 else "hex"
        (pent if kind == "pent" else hexa).append(pts)
        # keep the ORIGINAL geodesic-vertex order. genesis numbers its locks by
        # scanning gkState.faces in exactly this order, so preserving it is what
        # makes 'pentagon 7' the same pentagon in both programs.
        ordered.append((kind, pts))

    P = np.array(pent, np.float32) if pent else np.zeros((0, 5, 3), np.float32)
    Hf = np.array(hexa, np.float32) if hexa else np.zeros((0, 6, 3), np.float32)

    # THE CERTIFICATE -- Path III. Verified, not assumed, every single build.
    nV, nF = len(gtris), len(P) + len(Hf)
    nE = (len(P) * 5 + len(Hf) * 6) // 2
    cert = dict(V=nV, E=nE, F=nF, P=len(P), H=len(Hf), chi=nV - nE + nF,
                EV=(nE / nV if nV else 0.0), hull=how, hull_ms=hull_ms)
    bad = [w for w, got, want in
           (("V", nV, topo["V"]), ("E", nE, topo["E"]), ("F", nF, topo["F"]),
            ("P", len(P), 12), ("chi", nV - nE + nF, 2))
           if got != want]
    cert["pass"] = not bad
    if bad:
        raise SystemExit("  CLOSURE FAILED on Goldberg(%d,%d): %s disagree with the\n"
                         "  exact counts. OPEN CANDIDATE, not a closed shell. Refusing."
                         % (k, l, ", ".join(bad)))
    if verbose:
        print("  GOLDEN  : C%d  Goldberg(%d,%d)  T=%d  via %s in %.0f ms"
              % (topo["V"], k, l, T, how, hull_ms))
        print("            V=%s E=%s F=%s P=%d chi=%d  E/V=%.3f   CLOSURE PASS"
              % ("{:,}".format(nV), "{:,}".format(nE), "{:,}".format(nF),
                 len(P), cert["chi"], cert["EV"]))
    out = dict(topo)
    out.update(k=k, l=l, name="C%d" % topo["V"], cert=cert, faces_ordered=ordered)
    return P, Hf, out


# -----------------------------------------------------------------------------
#  LANE A -- v1.5's legacy seeds, unchanged.
# -----------------------------------------------------------------------------
def _icosahedron():
    raw = []
    for s1 in (1, -1):
        for s2 in (1, -1):
            raw += [[0, s1, s2 * PHI], [s1, s2 * PHI, 0], [s2 * PHI, 0, s1]]
    V = _norm(np.array(raw, np.float64))
    D = np.linalg.norm(V[:, None] - V[None, :], axis=-1)
    e = D[D > 1e-9].min()
    F = []
    for i in range(12):
        for j in range(i + 1, 12):
            if abs(D[i, j] - e) > 1e-6:
                continue
            for k in range(j + 1, 12):
                if abs(D[i, k] - e) < 1e-6 and abs(D[j, k] - e) < 1e-6:
                    F.append((i, j, k))
    return V, F


def _dual(gv, gt, R):
    """geodesic vertex -> face. degree 5 gives a pentagon, degree 6 a hexagon."""
    dual = _norm(np.array([gv[list(t)].mean(0) for t in gt])) * R
    inc = [[] for _ in range(len(gv))]
    spoke = {}
    for ti, t in enumerate(gt):
        for k in range(3):
            inc[t[k]].append(ti)
            a, b = t[k], t[(k + 1) % 3]
            spoke.setdefault((a, b), []).append(ti)
            spoke.setdefault((b, a), []).append(ti)
    out = []
    for v in range(len(gv)):
        ring = inc[v]
        cyc, seen = [ring[0]], {ring[0]}
        for _ in range(len(ring)):
            cur, nxt = cyc[-1], None
            for o in gt[cur]:
                if o == v:
                    continue
                for cand in spoke.get((v, o), ()):
                    if cand != cur and cand not in seen:
                        nxt = cand
                        break
                if nxt is not None:
                    break
            if nxt is None:
                break
            cyc.append(nxt)
            seen.add(nxt)
        pts = dual[cyc]
        c = pts.mean(0)
        N = np.zeros(3)
        for k in range(len(pts)):
            A, B = pts[k], pts[(k + 1) % len(pts)]
            N += [(A[1] - B[1]) * (A[2] + B[2]), (A[2] - B[2]) * (A[0] + B[0]),
                  (A[0] - B[0]) * (A[1] + B[1])]
        if N @ c < 0:
            pts = pts[::-1]
        out.append(pts)
    return out


def _geodesic(nu):
    bv, bf = _icosahedron()
    idx, verts = {}, []

    def get(tri, i, j):
        w = [(tri[0], nu - i - j), (tri[1], i), (tri[2], j)]
        key = tuple(sorted((a, b) for a, b in w if b > 0))
        if key not in idx:
            p = sum(bv[a] * b for a, b in w)
            idx[key] = len(verts)
            verts.append(p / np.linalg.norm(p))
        return idx[key]

    tris = []
    for tri in bf:
        for i in range(nu):
            for j in range(nu - i):
                tris.append((get(tri, i, j), get(tri, i + 1, j), get(tri, i, j + 1)))
                if i + j < nu - 1:
                    tris.append((get(tri, i + 1, j), get(tri, i + 1, j + 1), get(tri, i, j + 1)))
    return np.array(verts), tris


def _kis(polys, R):
    """fan every face from its centroid -> triangles (for the C60 dual)"""
    verts, tris, vidx = [], [], {}

    def vid(p):
        k = tuple(np.round(p, 9))
        if k not in vidx:
            vidx[k] = len(verts)
            verts.append(np.array(p))
        return vidx[k]

    for f in polys:
        ids = [vid(p) for p in f]
        ci = vid(_norm(np.array(f).mean(0)) * R)
        for k in range(len(ids)):
            tris.append((ids[k], ids[(k + 1) % len(ids)], ci))
    return np.array(verts), tris


_LEGACY_SEEDS = {         # name: (how, nu)   every one has exactly 12 pentagons
    "dodec": ("gp", 1),   # C20   GP(1,0)   F=12
    "c60":   ("kis", 0),  # C60   GP(1,1)   F=32   dual of the pentakis dodecahedron
    "c80":   ("gp", 2),   # C80   GP(2,0)   F=42
    "c180":  ("gp", 3),   # C180  GP(3,0)   F=92
    "c320":  ("gp", 4),   # C320  GP(4,0)   F=162
}


def build_seed(kind, R=None, verbose=True):
    """Golden name -> Lane B. Legacy name -> Lane A. Returns (P, H, info)."""
    R = SPHERE_R if R is None else R
    if kind in GOLDEN_BY_NAME:
        g = GOLDEN_BY_NAME[kind]
        return build_goldberg(g["k"], g["l"], R, verbose)
    if kind in _LEGACY_SEEDS:
        how, nu = _LEGACY_SEEDS[kind]
        if how == "gp":
            gv, gt = _geodesic(nu)
            polys = _dual(gv, gt, R)
        else:                       # C60 = dual of the pentakis dodecahedron
            gv, gt = _geodesic(1)
            kv, kt = _kis(_dual(gv, gt, R), R)
            polys = _dual(kv, kt, R)
        P = np.array([p for p in polys if len(p) == 5], np.float32)
        Hf = np.array([p for p in polys if len(p) == 6], np.float32)
        if Hf.size == 0:
            Hf = np.zeros((0, 6, 3), np.float32)
        if P.size == 0:
            P = np.zeros((0, 5, 3), np.float32)
        nF = len(P) + len(Hf)
        nE = (len(P) * 5 + len(Hf) * 6) // 2
        nV = nE * 2 // 3
        if verbose:
            print("  LEGACY  : %s   V=%s E=%s F=%s P=%d chi=%d"
                  % (kind, "{:,}".format(nV), "{:,}".format(nE), "{:,}".format(nF),
                     len(P), nV - nE + nF))
        # legacy seeds have no browser lock numbering to match; document the
        # order used rather than imply it is the browser's.
        ordered = ([("pent", p) for p in P] + [("hex", h) for h in Hf])
        return P, Hf, dict(name=kind, V=nV, E=nE, F=nF, P=len(P), H=len(Hf),
                           chi=nV - nE + nF, T=None, k=None, l=None,
                           faces_ordered=ordered, cert=dict(pass_legacy=True))
    raise SystemExit("  unknown SEED %r\n  golden: %s\n  legacy: %s"
                     % (kind, ", ".join(GOLDEN_BY_NAME), ", ".join(_LEGACY_SEEDS)))


# =============================================================================
#  PART 2 -- THE FLIGHT LOCK
#
#  v8.5.2's flCenterOn, ported -- and audited, because it does not do what its
#  own comment says it does.
#
#  THE BROWSER'S CODE
#      ry = Math.atan2(dx, dz);
#      rx = -Math.asin(clamp(dy));
#
#  THE PROJECTION IT FEEDS
#      x1 = x*cos(ry) - z*sin(ry)          z1 = x*sin(ry) + z*cos(ry)
#      y1 = y*cos(rx) - z1*sin(rx)         z2 = y*sin(rx) + z1*cos(rx)
#
#  With ry = atan2(dx,dz) and h = sqrt(dx^2+dz^2):  cos ry = dz/h, sin ry = dx/h
#      x1 = dx*dz/h - dz*dx/h = 0                          centred in x, always
#      z1 = (dx^2 + dz^2)/h  = h
#      y1 = dy*cos(rx) - h*sin(rx)
#  y1 = 0 requires tan(rx) = dy/h, i.e. rx = +asin(dy), since h = cos(asin dy).
#  The browser passes -asin(dy), which gives
#      y1 = dy*h + h*dy = 2*dy*h
#  -- zero only when dy = 0. Measured on C60's twelve pentagon centres:
#
#      dy = 0        pentagons  3, 6, 7, 11   ->  y1 = 0.0000   z = +1.496  OK
#      dy = +-0.5257 pentagons  1, 5, 8, 10   ->  y1 = 1.3380   z = +0.669  off
#      dy = +-0.8507 pentagons  2, 4, 9, 12   ->  y1 = 1.3380   z = -0.669  off AND behind
#
#  Four of twelve land. The screenshot that started this says
#  "FLIGHT: center pentagon 7" -- one of the four that happens to work.
#
#  Both signs ship. "fixed" centres every point; "genesis" reproduces v8.5.2
#  exactly, because a frozen version is not corrected in place (Path X). The
#  residual is measured and printed for whichever you pick -- target is not
#  result (Path III).
# =============================================================================

def fl_center_on(pos, sign=None):
    """genesis flCenterOn -> (rx, ry). sign: 'fixed' | 'genesis'."""
    sign = FLIGHT_SIGN if sign is None else sign
    L = math.sqrt(pos[0] * pos[0] + pos[1] * pos[1] + pos[2] * pos[2]) or 1.0
    dx, dy, dz = pos[0] / L, pos[1] / L, pos[2] / L
    ry = math.atan2(dx, dz)
    a = math.asin(max(-1.0, min(1.0, dy)))
    return (a if sign == "fixed" else -a), ry


def project_one(p, rx, ry, zoom=1.0):
    """genesis project(), outside mode, for a single point. Scalar, for audit."""
    x, y, z = float(p[0]), float(p[1]), float(p[2])
    cy, sy = math.cos(ry), math.sin(ry)
    x1 = x * cy - z * sy
    z1 = x * sy + z * cy
    crx, srx = math.cos(rx), math.sin(rx)
    y1 = y * crx - z1 * srx
    z2 = y * srx + z1 * crx
    return x1 * zoom, y1 * zoom, z2


def lock_residual(pos, rx, ry):
    """How far off centre this lock actually lands, in world units, and whether
    the point ends up in front of the shell or behind it. Measured, not claimed."""
    x1, y1, z2 = project_one(pos, rx, ry)
    return math.hypot(x1, y1), z2


# -- the icosahedral axis frame: 6 five-fold + 10 three-fold + 15 two-fold ----
def _ico_axes():
    v, f = _icosahedron_gk()
    five = [v[i] for i in range(12)]
    three = [(v[a] + v[b] + v[c]) / 3.0 for (a, b, c) in f]
    eset = set()
    for (a, b, c) in f:
        for (i, j) in ((a, b), (b, c), (c, a)):
            eset.add((min(i, j), max(i, j)))
    two = [(v[i] + v[j]) / 2.0 for (i, j) in sorted(eset)]
    ax = np.array(five + three + two, np.float64)
    return _norm(ax)


_ICO_AXES = None


def view_signature(d, nd=6):
    """A COMPUTED signature of a direction under the icosahedral group: the
    sorted absolute dot products with all 31 symmetry axis lines.

    Two directions in the same orbit necessarily share this signature. The
    converse is not proved here, so this is a CLASSIFICATION, not a theorem --
    it groups directions that give the same camera view up to a roll, and it is
    labelled as a signature everywhere it is printed. (Path IV: incomplete is
    fine, fake is not.)"""
    global _ICO_AXES
    if _ICO_AXES is None:
        _ICO_AXES = _ico_axes()
    d = np.asarray(d, np.float64)
    L = np.linalg.norm(d)
    d = d / (L if L > 1e-12 else 1.0)
    return tuple(np.sort(np.round(np.abs(_ICO_AXES @ d), nd)))


def canonical_axes():
    """The three icosahedral axis families, as ready-made locks. These are the
    views the solid actually has: 5-fold through a pentagon, 3-fold through a
    vertex of the dual, 2-fold through an edge."""
    v, f = _icosahedron_gk()
    e = set()
    for (a, b, c) in f:
        for (i, j) in ((a, b), (b, c), (c, a)):
            e.add((min(i, j), max(i, j)))
    i0, j0 = sorted(e)[0]
    return [
        ("axis 5-fold", np.asarray(v[0], np.float64) * SPHERE_R, 6, 12),
        ("axis 3-fold", _norm(np.asarray((v[f[0][0]] + v[f[0][1]] + v[f[0][2]]) / 3.0,
                                         np.float64)) * SPHERE_R, 10, 20),
        ("axis 2-fold", _norm(np.asarray((v[i0] + v[j0]) / 2.0,
                                         np.float64)) * SPHERE_R, 15, 30),
    ]


def centroid3(pts):
    return np.asarray(pts, np.float64).mean(axis=0)


def key3s(p):
    """v8.5.2 key3s -- the same 1e6 rounding, so a vertex is the same vertex."""
    return (round(float(p[0]) * 1e6), round(float(p[1]) * 1e6), round(float(p[2]) * 1e6))


def lock_points(info, P, Hf, want_vertices=True, want_hexes=True, cap=None):
    """v8.5.2 flLockPoints, ported -- and uncapped by default.

    The browser caps its dropdown at VERTEX_CAP=240 and strides through the
    vertex list to fill it (Curse 35, but for the DOM). There is no DOM here,
    so the default is every point. Ordering follows the browser exactly:
    the twelve pentagon centres first, in face order, then unique vertices in
    first-seen order -- which is why 'pentagon 7' and 'vertex 379' mean the
    same points in both programs.
    """
    pts_out = []
    ordered = info.get("faces_ordered")
    if ordered is None:
        ordered = ([("pent", p) for p in P] + [("hex", h) for h in Hf])

    n = 0
    for kind, pts in ordered:
        if kind == "pent":
            n += 1
            pts_out.append(dict(label="pentagon %d" % n, pos=centroid3(pts), kind="pent"))
    if want_hexes:
        n = 0
        for kind, pts in ordered:
            if kind == "hex":
                n += 1
                pts_out.append(dict(label="hexagon %d" % n, pos=centroid3(pts), kind="hex"))

    if want_vertices:
        seen, vlist = set(), []
        for _, pts in ordered:
            for p in pts:
                ky = key3s(p)
                if ky not in seen:
                    seen.add(ky)
                    vlist.append(np.asarray(p, np.float64))
        step = math.ceil(len(vlist) / cap) if (cap and len(vlist) > cap) else 1
        for i in range(0, len(vlist), step):
            pts_out.append(dict(label="vertex %d" % (i + 1), pos=vlist[i], kind="vert"))

    for name, pos, nax, npt in canonical_axes():
        pts_out.append(dict(label=name, pos=pos, kind="axis", axes=nax, thru=npt))
    return pts_out


def find_lock(locks, label):
    lab = str(label).strip().lower()
    for L in locks:
        if L["label"].lower() == lab:
            return L
    hits = [L for L in locks if L["label"].lower().startswith(lab)]
    if len(hits) == 1:
        return hits[0]
    raise SystemExit(
        "  FLIGHT_LOCK %r not found on this seed.\n"
        "  Run  --locks  to see every lock this shell has.%s"
        % (label, ("\n  did you mean: " + ", ".join(h["label"] for h in hits[:6]))
           if hits else ""))


def apply_flight_lock(info, P, Hf, verbose=True):
    """Resolve FLIGHT_LOCK into (rx, ry) and report what it actually bought."""
    if not FLIGHT_LOCK:
        return None
    locks = lock_points(info, P, Hf)
    L = find_lock(locks, FLIGHT_LOCK)
    rx, ry = fl_center_on(L["pos"])
    off, z = lock_residual(L["pos"], rx, ry)
    rx_g, ry_g = fl_center_on(L["pos"], "genesis")
    off_g, z_g = lock_residual(L["pos"], rx_g, ry_g)
    if verbose:
        print("  FLIGHT  : lock '%s'  (%s)   sign=%s" % (L["label"], L["kind"], FLIGHT_SIGN))
        print("            pos  (%+.4f, %+.4f, %+.4f)   rx=%+.6f  ry=%+.6f"
              % (L["pos"][0], L["pos"][1], L["pos"][2], rx, ry))
        print("            residual |screen offset| = %.6f   depth z = %+.4f  (%s)"
              % (off, z, "front" if z > 0 else "BEHIND the shell"))
        if FLIGHT_SIGN == "fixed" and off_g > 1e-9:
            print("            v8.5.2 would put this lock %.4f off centre at z=%+.4f"
                  % (off_g, z_g))
        elif FLIGHT_SIGN == "genesis" and off > 1e-9:
            print("            NOT CENTRED -- this is v8.5.2's own result, reproduced")
            print("            on purpose. FLIGHT_SIGN='fixed' gives offset 0.000000.")
    return dict(label=L["label"], kind=L["kind"], pos=L["pos"], rx=rx, ry=ry,
                offset=off, z=z, offset_genesis=off_g, z_genesis=z_g)


# -----------------------------------------------------------------------------
#  THE LOCK TABLE -- every lock on every buckyball, in one python.
# -----------------------------------------------------------------------------
def _fmt_lock_row(L, sig_id, count):
    rx, ry = fl_center_on(L["pos"])
    off, z = lock_residual(L["pos"], rx, ry)
    rxg, ryg = fl_center_on(L["pos"], "genesis")
    offg, zg = lock_residual(L["pos"], rxg, ryg)
    return ("  %-14s %-5s %8.4f %8.4f %8.4f  %+8.5f %+8.5f  %6.4f %6.4f  V%-3d x%d"
            % (L["label"], L["kind"], L["pos"][0], L["pos"][1], L["pos"][2],
               rx, ry, off, offg, sig_id, count))


def print_locks(shells=None, max_rows=14, verbose_build=False):
    """--locks : the distinct camera views of every golden shell, with the
    (rx, ry) each one needs, and both signs measured side by side."""
    shells = shells or [g["name"] for g in GOLDEN[:7]]
    print("=" * 79)
    print("  THE LOCK TABLE -- every buckyball, every lock, both signs measured")
    print("=" * 79)
    print("  Rows are DISTINCT VIEWS: locks are grouped by an icosahedral-axis")
    print("  signature (sorted |d.a| over the 6 five-fold, 10 three-fold and 15")
    print("  two-fold axis lines). Same signature -> same view up to a roll.")
    print("  A signature match is COMPUTED classification, not a proved orbit.")
    print()
    print("  off  = |screen offset| with FLIGHT_SIGN='fixed'    (want 0.000000)")
    print("  offG = |screen offset| with FLIGHT_SIGN='genesis'  (v8.5.2 verbatim)")
    print()
    grand = 0
    for name in shells:
        g = GOLDEN_BY_NAME.get(name)
        if not g:
            print("  -- unknown shell %s, skipped" % name)
            continue
        try:
            P, Hf, info = build_seed(name, verbose=verbose_build)
        except SystemExit as e:
            print("  %-8s  %s" % (name, str(e).strip().splitlines()[0]))
            continue
        locks = lock_points(info, P, Hf)
        groups = {}
        for L in locks:
            if L["kind"] == "axis":
                continue
            groups.setdefault((L["kind"], view_signature(L["pos"])), []).append(L)
        grand += len(locks)

        print("  " + "-" * 75)
        print("  %s   Goldberg(%d,%d)  T=%d   V=%s E=%s F=%s P=12 chi=%d  E/V=%.3f"
              % (name, g["k"], g["l"], g["T"], "{:,}".format(g["V"]),
                 "{:,}".format(g["E"]), "{:,}".format(g["F"]), g["chi"],
                 g["E"] / g["V"]))
        n_pent = sum(1 for L in locks if L["kind"] == "pent")
        n_hex = sum(1 for L in locks if L["kind"] == "hex")
        n_vert = sum(1 for L in locks if L["kind"] == "vert")
        print("  locks: %d pentagon + %d hexagon + %d vertex + 3 axis = %s total"
              % (n_pent, n_hex, n_vert, "{:,}".format(len(locks))))
        # genesis' dropdown = 12 pentagon centres + up to VERTEX_CAP=240 strided
        # vertices. No hexagons at all. This has no DOM, so it lists everything.
        print("  distinct views: %d   (browser dropdown would show %d: 12 pent + "
              "%d strided vertices, no hexagons)"
              % (len(groups), 12 + min(n_vert, 240), min(n_vert, 240)))
        print("  %-14s %-5s %8s %8s %8s  %8s %8s  %6s %6s  %-4s %s"
              % ("lock", "kind", "x", "y", "z", "rx", "ry", "off", "offG", "sig", "n"))
        rows = sorted(groups.items(), key=lambda kv: (kv[0][0], -len(kv[1])))
        for i, (key, members) in enumerate(rows[:max_rows]):
            print(_fmt_lock_row(members[0], i, len(members)))
        if len(rows) > max_rows:
            more = sum(len(m) for _, m in rows[max_rows:])
            print("  ... %d more distinct views covering %s locks   (--locks-csv for all)"
                  % (len(rows) - max_rows, "{:,}".format(more)))
        for name_ax, pos, nax, npt in canonical_axes():
            rx, ry = fl_center_on(pos)
            off, z = lock_residual(pos, rx, ry)
            rxg, ryg = fl_center_on(pos, "genesis")
            offg, _ = lock_residual(pos, rxg, ryg)
            print("  %-14s %-5s %8.4f %8.4f %8.4f  %+8.5f %+8.5f  %6.4f %6.4f  --   x%d"
                  % (name_ax, "axis", pos[0], pos[1], pos[2], rx, ry, off, offg, nax))
    print("  " + "-" * 75)
    print("  %s locks enumerated. FLIGHT_LOCK takes any label above."
          % "{:,}".format(grand))
    print("=" * 79)


def write_locks_csv(path, shells=None):
    """--locks-csv : the full uncapped enumeration. Every lock, every shell."""
    import csv
    shells = shells or [g["name"] for g in GOLDEN[:7]]
    n = 0
    # newline="" is csv's requirement; lineterminator="\n" keeps the CR out
    # (Curse 14 -- a CSV that rots under git is still a rotted artifact).
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["shell", "k", "l", "T", "V", "E", "F", "label", "kind",
                    "x", "y", "z", "rx_fixed", "ry", "offset_fixed",
                    "rx_genesis", "offset_genesis", "depth_z", "view_sig"])
        for name in shells:
            g = GOLDEN_BY_NAME[name]
            P, Hf, info = build_seed(name, verbose=False)
            locks = lock_points(info, P, Hf)
            sigs, sid = {}, 0
            for L in locks:
                rx, ry = fl_center_on(L["pos"], "fixed")
                off, z = lock_residual(L["pos"], rx, ry)
                rxg, _ = fl_center_on(L["pos"], "genesis")
                offg, _zg = lock_residual(L["pos"], rxg, ry)
                s = view_signature(L["pos"])
                if s not in sigs:
                    sigs[s] = sid
                    sid += 1
                w.writerow([name, g["k"], g["l"], g["T"], g["V"], g["E"], g["F"],
                            L["label"], L["kind"],
                            "%.9f" % L["pos"][0], "%.9f" % L["pos"][1], "%.9f" % L["pos"][2],
                            "%.9f" % rx, "%.9f" % ry, "%.3e" % off,
                            "%.9f" % rxg, "%.3e" % offg, "%.6f" % z, sigs[s]])
                n += 1
            print("  %-8s %s locks" % (name, "{:,}".format(len(locks))))
    print("  written : %s   (%s rows)" % (path, "{:,}".format(n)))
    return path


# =============================================================================
#  PART 3 -- THE OPERATOR
#
#  Vectorised transcription of genesis GK.refineFace. Same expressions, same
#  order, midRing included. Unchanged from v1.5 -- the crescent defect is kept
#  on purpose. It is the picture.
#
#     inner[i]   = projectToSphere(lerp(c, pts[i], innerScale))
#     midRing[i] = projectToSphere(lerp(c, mid(pts[i],pts[j]), midScale))
#     em         = projectToSphere(mid(pts[i],pts[j]))
#     inner cell = [inner[0..n-1]]                       arity preserved
#     cell i     = [pts[i], em, pts[j], inner[j], midRing[i], inner[i]]
#
#  midRing sits on the hex side of the cell edge inner[i]->inner[j] and nowhere
#  on the cell side. That is the whole phenomenon.
#
#  GROWTH, exactly:
#     REFINE ALL  P'=P=12, H'=5P+7H  ->  F' = 7F - 12
#     REFINE 6s   pentagons untouched ->  F' = 7F - 72
#     REFINE 5s   H'=H+7P            ->  F' = F + 6P
#  Verified against the browser's own log: C60 F=32 -> all -> 212 -> 6s x5 ->
#  1412, 9812, 68612, 480212, 3361412. Every number matches the screenshot.
# =============================================================================
_SPHERICAL_NOW = [None]   # set at runtime; MOBIUS_WHEN="first" may force planar


def face_growth(F, P, op):
    """Predict the NEXT generation before allocating a byte of it (Curse 35)."""
    H = F - P
    if op == "all":
        return P + 5 * P + 7 * H, P
    if op == "hex":
        return P + 7 * H, P
    if op == "pent":
        return H + 7 * P, 0
    raise SystemExit("  unknown op %r -- use all | hex | pent" % op)


def predict_ops(F0, P0, ops):
    """The whole plan, priced before the first allocation."""
    out, F, P = [], F0, P0
    for op in ops:
        F, P = face_growth(F, P, op)
        out.append((op, F, P))
    return out


def _projn(a, R):
    if not _SPHERICAL_NOW[0]:
        return a
    L = np.linalg.norm(a, axis=-1, keepdims=True)
    return a * (R / np.where(L < 1e-12, np.float32(1.0), L))


def refine(faces, R, rng, bar=None):
    """genesis GK.refineFace, vectorised, in CHUNKS.

    Output is preallocated, so peak transient memory is set by REFINE_CHUNK
    rather than by the size of the generation. The arithmetic per chunk is
    identical to the scalar original -- verified vertex for vertex against it.
    """
    m, nn, _ = faces.shape
    inner_out = np.empty((m, nn, 3), np.float32)
    cells_out = np.empty((m * nn, 6, 3), np.float32)
    step = max(1, int(REFINE_CHUNK))
    for s0 in range(0, m, step):
        s1 = min(m, s0 + step)
        f = faces[s0:s1]
        c = f.mean(axis=1, keepdims=True)
        inner = _projn(c + (f - c) * np.float32(INNER_SCALE), R)
        nxt = np.roll(f, -1, axis=1)
        mid = (f + nxt) * np.float32(0.5)
        midRing = _projn(c + (mid - c) * np.float32(MID_SCALE), R)
        em = _projn(mid, R)
        if JITTER > 0.0:
            inner += (rng.random(inner.shape, dtype=np.float32) - np.float32(0.5)) * np.float32(JITTER)
            midRing += (rng.random(midRing.shape, dtype=np.float32) - np.float32(0.5)) * np.float32(JITTER)
        innerN = np.roll(inner, -1, axis=1)
        inner_out[s0:s1] = inner
        np.stack([f, em, nxt, innerN, midRing, inner], axis=2,
                 out=cells_out[s0 * nn:s1 * nn].reshape(s1 - s0, nn, 6, 3))
        del c, inner, nxt, mid, midRing, em, innerN
        if bar:
            bar.step(s1 - s0)
    return inner_out, cells_out


def sphere_to_mobius(pts, R, W, t):
    """genesis sphereToMobius, vectorised, with the slider's lerp.
    pts (...,3) -> (...,3).  t=0 returns pts untouched."""
    if t <= 0.0:
        return pts
    x, y, z = pts[..., 0], pts[..., 1], pts[..., 2]
    r = np.sqrt(x * x + y * y + z * z)
    safe = r > 1e-10
    rr = np.where(safe, r, np.float32(1.0))
    theta = np.arctan2(y, x)
    phi = np.arccos(np.clip(z / rr, -1.0, 1.0))
    u = theta + np.float32(np.pi)
    v = (phi / np.float32(np.pi) - np.float32(0.5)) * np.float32(2.0 * W)
    rad = np.float32(R) + v * np.cos(u * np.float32(0.5))
    mob = np.stack([rad * np.cos(u), rad * np.sin(u),
                    v * np.sin(u * np.float32(0.5))], axis=-1).astype(np.float32)
    mob = np.where(safe[..., None], mob, np.array([R, 0, 0], np.float32))
    tt = np.float32(t)
    return (pts * (np.float32(1.0) - tt) + mob * tt).astype(np.float32)


# =============================================================================
#  PART 4 -- THE EXACT RENDERER, the canvas ported
#
#  Four things genesis does that an additive path cannot imitate:
#    1. orthographic projection scaled by cam.zoom -- no perspective divide
#    2. sub-pixel cull: |proj(pts[0]) - proj(pts[1])| < 0.5  ->  drop
#    3. backface cull by screen winding, threshold -max(0.5, screenSize*0.02)
#    4. fills UNDER strokes, painter-sorted, composited source-over
#  and a fifth that v1.5 missed:
#    5. STROKE ONLY IF screenSize > 2.  Faces between 0.5 and 2 px are filled
#       and left unstroked. At depth that is most of the shell, and it is why
#       a dense genesis render reads as a body with a bright rim rather than as
#       a uniform wire ball. v1.5 stroked everything it kept, which is the
#       single biggest reason its output looked flatter than the browser's.
#
#  v1.6 does the cull, the sort and the colour assignment in numpy. v1.5 sorted
#  a python generator of millions of tuples and then looped it one face at a
#  time, appending to five python lists. Same pixels, different schedule.
# =============================================================================

def project_exact(pts, rx, ry, zoom, w, h):
    """genesis project(), outside mode, verbatim, vectorised."""
    x, y, z = pts[..., 0], pts[..., 1], pts[..., 2]
    cy, sy = math.cos(ry), math.sin(ry)
    crx, srx = math.cos(rx), math.sin(rx)
    x1 = x * cy - z * sy
    z1 = x * sy + z * cy
    y1 = y * crx - z1 * srx
    z2 = y * srx + z1 * crx
    return (w / 2 + x1 * zoom), (h / 2 - y1 * zoom), z2


def cull_exact(faces, rx, ry, zoom, w, h):
    """genesis' four culls in its own order. Returns (keep, ss, cZ, X, Y)."""
    X, Y, Z = project_exact(faces, rx, ry, zoom, w, h)
    cX, cY, cZ = X.mean(1), Y.mean(1), Z.mean(1)
    ss = np.hypot(X[:, 0] - X[:, 1], Y[:, 0] - Y[:, 1])
    keep = ss >= _G["cull_ss"]
    keep &= (cX >= -200) & (cX <= w + 200) & (cY >= -200) & (cY <= h + 200)
    cross = ((X[:, 1] - X[:, 0]) * (Y[:, 2] - Y[:, 0]) -
             (Y[:, 1] - Y[:, 0]) * (X[:, 2] - X[:, 0]))
    keep &= cross >= -np.maximum(0.5, ss * 0.02)
    return keep, ss, cZ, X, Y


def _rgba(rgb, a):
    return (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0, a)


def render_exact(P, Hf, rx, ry):
    try:
        from matplotlib.backends.backend_agg import FigureCanvasAgg
        from matplotlib.figure import Figure
        from matplotlib.collections import PolyCollection
    except ImportError:
        raise SystemExit("  RENDERER='exact' needs matplotlib: pip install matplotlib")

    ssf = max(1, int(SUPERSAMPLE))
    w, h, zoom = WIDTH * ssf, HEIGHT * ssf, CAM_ZOOM * ssf
    totalF = P.shape[0] + Hf.shape[0]

    # -- THE GUILLOTINE (Curse 35). matplotlib draws one path per face; the cost
    #    is linear and the wall is real. Refuse with the number, and name the
    #    tool that does hold it.
    if totalF > EXACT_FACE_BUDGET:
        raise SystemExit(
            "\n  HALT: RENDERER='exact' asked to composite %s faces >"
            " EXACT_FACE_BUDGET %s.\n"
            "        Every face is a separate Agg path with its own fill, stroke and\n"
            "        alpha -- that is what makes it exact, and what makes it linear.\n"
            "        The kernel is fine at this size. The compositor is what ends.\n"
            "        -> RENDERER='additive' holds hundreds of millions, or drop one op,\n"
            "           or raise EXACT_FACE_BUDGET if you have the minutes."
            % ("{:,}".format(totalF), "{:,}".format(EXACT_FACE_BUDGET)))

    # ---- cull, vectorised, both face types --------------------------------
    packs = []
    for tag, F in (("pent", P), ("hex", Hf)):
        if F.shape[0]:
            keep, ss, cZ, X, Y = cull_exact(F, rx, ry, zoom, w, h)
            idx = np.nonzero(keep)[0]
            if idx.size:
                packs.append((tag, idx, ss[idx], cZ[idx], X[idx], Y[idx]))
    drawn = sum(p[1].size for p in packs)
    if drawn == 0:
        raise SystemExit("  every face was culled -- nothing to draw. Check CAM_ZOOM "
                         "and FLIGHT_LOCK (a 'genesis' sign lock can point at the "
                         "far side of the shell).")
    print("  drawn   : %s/%s  (%.0f%% -- the rest is genesis' own culling)"
          % ("{:,}".format(drawn), "{:,}".format(totalF), 100.0 * drawn / max(1, totalF)))

    # ---- one padded vertex array, one global painter sort ------------------
    #  pentagons are padded to 6 by repeating their last vertex. A zero-length
    #  edge draws nothing under a butt cap, so the fill and the stroke are
    #  unchanged -- it only lets every face live in one (N,6,2) array and one
    #  PolyCollection, which is what keeps the painter order exact.
    NV = np.zeros((drawn, 6, 2), np.float64)
    DZ = np.empty(drawn, np.float64)
    SS = np.empty(drawn, np.float64)
    IP = np.zeros(drawn, bool)
    o = 0
    for tag, idx, ss, cZ, X, Y in packs:
        n, k = idx.size, X.shape[1]
        NV[o:o + n, :k, 0] = X
        NV[o:o + n, :k, 1] = Y
        if k < 6:
            NV[o:o + n, k:, 0] = X[:, -1:]
            NV[o:o + n, k:, 1] = Y[:, -1:]
        DZ[o:o + n] = cZ
        SS[o:o + n] = ss
        IP[o:o + n] = (tag == "pent")
        o += n

    order = np.argsort(DZ, kind="stable")
    NV, DZ, SS, IP = NV[order], DZ[order], SS[order], IP[order]

    # ---- genesis' alpha law, exactly --------------------------------------
    #      alpha = 0.15 + clamp((depth+2)/4, 0, 1) * 0.5
    A = _G["alpha_base"] + np.clip((DZ + 2.0) / 4.0, 0.0, 1.0) * _G["alpha_span"]

    def pick(rgb_p, rgb_h, mul_p, mul_h):
        c = np.empty((drawn, 4), np.float64)
        for j in range(3):
            c[:, j] = np.where(IP, rgb_p[j] / 255.0, rgb_h[j] / 255.0)
        c[:, 3] = A * np.where(IP, mul_p, mul_h)
        return c

    fcol = pick(_G["pent_fill"], _G["hex_fill"], _G["pent_fill_a"], _G["hex_fill_a"])
    ecol = pick(_G["pent_edge"], _G["hex_edge"], _G["pent_edge_a"], _G["hex_edge_a"])
    # THE ss>2 GATE: below it genesis never calls stroke(). Alpha 0 is the same
    # pixel and keeps every face in one collection, so the sort stays exact.
    stroked = SS > (_G["stroke_ss"] * ssf)
    ecol[~stroked, 3] = 0.0
    lws = np.where(IP, _G["pent_lw"], _G["hex_lw"]) * ssf
    print("  stroked : %s/%s faces clear genesis' ss>%.0f gate (%.0f%%)"
          % ("{:,}".format(int(stroked.sum())), "{:,}".format(drawn),
             _G["stroke_ss"], 100.0 * stroked.sum() / drawn))

    fig = Figure(figsize=(w / 100.0, h / 100.0), dpi=100)
    fig.subplots_adjust(0, 0, 1, 1)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, w)
    ax.set_ylim(h, 0)
    ax.axis("off")
    bg = tuple(c / 255.0 for c in _G["bg"])
    ax.set_facecolor(bg)
    fig.patch.set_facecolor(bg)

    t0 = time.time()
    ax.add_collection(PolyCollection(NV, facecolors=fcol, edgecolors=ecol,
                                     linewidths=lws, antialiased=True))

    # ---- atoms: genesis' own gate, cam.atom > 0.2 and ss > 5 ---------------
    if CAM_ATOM > _G["atom_gate"]:
        sel = np.nonzero(SS > _G["atom_ss"] * ssf)[0]
        if sel.size:
            nk = np.where(IP[sel], 5, 6)          # padded slots are duplicates
            keepmask = np.zeros((sel.size, 6), bool)
            for kk in (5, 6):
                keepmask[nk == kk, :kk] = True
            ax_ = NV[sel][:, :, 0][keepmask]
            ay_ = NV[sel][:, :, 1][keepmask]
            aa = np.repeat(A[sel], nk)
            ip = np.repeat(IP[sel], nk)
            r = CAM_ATOM * np.where(ip, 2.0, 1.2) * ssf
            ac = np.empty((ax_.size, 4), np.float64)
            for j in range(3):
                ac[:, j] = np.where(ip, _G["pent_atom"][j] / 255.0,
                                    _G["hex_atom"][j] / 255.0)
            ac[:, 3] = aa * np.where(ip, _G["pent_atom_a"], _G["hex_atom_a"])
            ax.scatter(ax_, ay_, s=math.pi * r * r if np.isscalar(r) else np.pi * r * r,
                       c=ac, linewidths=0, marker="o")
            print("  atoms   : %s discs (ss>%.0f only)"
                  % ("{:,}".format(ax_.size), _G["atom_ss"]))

    canvas = FigureCanvasAgg(fig)
    canvas.draw()
    print("  composite: %.1fs for %s faces at %dx%d"
          % (time.time() - t0, "{:,}".format(drawn), w, h))
    img = np.asarray(canvas.buffer_rgba())[..., :3].astype(np.float32)
    if ssf > 1:
        img = img.reshape(HEIGHT, ssf, WIDTH, ssf, 3).mean(axis=(1, 3))
    return np.clip(img, 0, 255).astype(np.uint8)


# =============================================================================
#  PART 5 -- THE ADDITIVE RENDERER, the wallpaper instrument
#
#  A different instrument, and it says so. It does not composite source-over;
#  it accumulates energy per pixel and tone-maps at the end. That is what lets
#  it hold hundreds of millions of faces and what makes the hubs burn out to
#  white. It reads the SAME colour table as the exact path, so the hue is the
#  browser's even though the compositing is not.
#
#  v1.6 adds a screen-space bounding-box pre-cull: a face entirely off canvas
#  is dropped before its edges are expanded into samples. On a locked, zoomed
#  camera that is most of the mesh, and the expansion is the expensive half.
# =============================================================================

def make_camera(rot_x, rot_y, rot_z):
    cx, sx = math.cos(rot_x), math.sin(rot_x)
    cy, sy = math.cos(rot_y), math.sin(rot_y)
    cz, sz = math.cos(rot_z), math.sin(rot_z)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return (Rz @ Rx @ Ry).astype(np.float32)


def _disc(r):
    """integer offsets of a filled disc of radius r, plus per-offset coverage"""
    R = max(1, int(math.ceil(r)))
    yy, xx = np.mgrid[-R:R + 1, -R:R + 1]
    d = np.sqrt(xx * xx + yy * yy)
    cov = np.clip(r + 0.5 - d, 0.0, 1.0)      # soft edge
    m = cov > 0.01
    return xx[m].astype(np.int32), yy[m].astype(np.int32), cov[m].astype(np.float32)


def _splat(px, py, pa, r, acc):
    """additive discs at every point. duplicates stack, as genesis' do."""
    W, H = WIDTH, HEIGHT
    ox, oy, cov = _disc(r)
    k = ox.size
    per = max(1, int(CHUNK_SAMPLES) // max(1, k))
    gox, goy = xp.asarray(ox)[None, :], xp.asarray(oy)[None, :]
    gcv = xp.asarray(cov)[None, :]
    for s0 in range(0, px.size, per):
        gx = xp.asarray(px[s0:s0 + per]).astype(xp.int32)[:, None] + gox
        gy = xp.asarray(py[s0:s0 + per]).astype(xp.int32)[:, None] + goy
        gw = xp.asarray(pa[s0:s0 + per])[:, None] * gcv
        inb = (gx >= 0) & (gx < W) & (gy >= 0) & (gy < H)
        idx = (gy[inb].astype(xp.int64) * W + gx[inb].astype(xp.int64))
        wts = gw[inb].astype(xp.float64)
        del gx, gy, gw, inb
        if idx.size:
            acc += xp.bincount(idx, weights=wts, minlength=W * H).astype(xp.float32)
        del idx, wts


def _scatter(x0, y0, x1, y1, aw, acc):
    """additive line accumulation. edges are bucketed by pixel length into
    powers of two so each bucket is one vectorised linspace."""
    W, H = WIDTH, HEIGHT
    dx, dy = x1 - x0, y1 - y0
    ln = np.maximum(np.abs(dx), np.abs(dy))
    steps = np.clip(np.ceil(ln), 1, 4096).astype(np.int32)
    b = np.clip(1 << np.ceil(np.log2(np.maximum(steps, 1))).astype(np.int32), 1, 4096)
    for bv in np.unique(b):
        bv = int(bv)
        sel = np.nonzero(b == bv)[0]
        per = max(1, int(CHUNK_SAMPLES) // bv)
        t = xp.linspace(xp.float32(0), xp.float32(1), bv, dtype=xp.float32)[None, :]
        for s0 in range(0, sel.size, per):
            ii = sel[s0:s0 + per]
            gx0, gy0 = xp.asarray(x0[ii]), xp.asarray(y0[ii])
            gdx, gdy = xp.asarray(dx[ii]), xp.asarray(dy[ii])
            gw = xp.broadcast_to(xp.asarray(aw[ii])[:, None], (ii.size, bv))
            X = (gx0[:, None] + gdx[:, None] * t).astype(xp.int32).ravel()
            Y = (gy0[:, None] + gdy[:, None] * t).astype(xp.int32).ravel()
            del gx0, gy0, gdx, gdy
            inb = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
            idx = Y[inb].astype(xp.int64) * W + X[inb].astype(xp.int64)
            wts = gw.ravel()[inb].astype(xp.float64)
            del X, Y, inb, gw
            if idx.size:
                acc += xp.bincount(idx, weights=wts, minlength=W * H).astype(xp.float32)
            del idx, wts


def draw_faces(faces, acc, M, D, focal, bar, face_chunk, atoms=False, atom_r=0.0):
    """Faces live in system RAM; only screen-space coords cross to the GPU.

    Depth alpha follows genesis exactly: alpha = 0.15 + depth01*0.5, so faces
    nearer the camera contribute more, which is what gives the shell its
    interior falloff rather than a flat wash of lines.
    """
    W, H = WIDTH, HEIGHT
    m, nn, _ = faces.shape
    Rs = np.float32(SPHERE_R)
    for s0 in range(0, m, face_chunk):
        s1 = min(m, s0 + face_chunk)
        f = faces[s0:s1]
        V = (f.reshape(-1, 3) @ M.T).reshape(s1 - s0, nn, 3)
        w = D - V[:, :, 2]
        ok = w > 0.02
        wsafe = np.where(ok, w, np.float32(1.0))
        X = np.float32(W * 0.5) + V[:, :, 0] * focal / wsafe
        Y = np.float32(H * 0.5) - V[:, :, 1] * focal / wsafe
        d01 = np.clip((V[:, :, 2] + Rs) / (np.float32(2.0) * Rs), 0.0, 1.0)
        alpha = (np.float32(_G["alpha_base"]) + d01 * np.float32(_G["alpha_span"])).astype(np.float32)
        allok = ok.all(axis=1)
        del V, w, wsafe, d01

        # v1.6 PRE-CULL: drop faces whose screen bbox misses the canvas before
        # any edge is expanded into samples. The expansion is the expensive half.
        onscreen = ((X.max(1) >= 0) & (X.min(1) < W) &
                    (Y.max(1) >= 0) & (Y.min(1) < H))

        if atoms:
            # genesis gates atoms on ss = |proj(pts[0]) - proj(pts[1])| > 5 --
            # the length of ONE edge, not the whole face's bounding box. v1.5
            # used the bbox, which is up to ~2x larger, so it let far more faces
            # splat atoms than the browser ever does. At depth the atom colour
            # (0,255,213) then swamps the edge colour (0,180,255) and the whole
            # render goes teal. Same test as the browser now.
            ss = np.hypot(X[:, 0] - X[:, 1], Y[:, 0] - Y[:, 1])
            sel = allok & onscreen & (ss > np.float32(ATOM_MIN_PX))
            if sel.any():
                px, py = X[sel].ravel(), Y[sel].ravel()
                pa = alpha[sel].ravel()
                _splat(px, py, pa, atom_r, acc)
                del px, py, pa
            del ss, sel
        else:
            keep2 = (ok & np.roll(ok, -1, axis=1)) & onscreen[:, None]
            keep2 = keep2.ravel()
            gx, gy = np.roll(X, -1, axis=1), np.roll(Y, -1, axis=1)
            ga = np.roll(alpha, -1, axis=1)
            x0, y0 = X.ravel()[keep2], Y.ravel()[keep2]
            x1, y1 = gx.ravel()[keep2], gy.ravel()[keep2]
            aw = ((alpha.ravel()[keep2] + ga.ravel()[keep2]) * np.float32(0.5))
            del gx, gy, ga, keep2
            if x0.size:
                _scatter(x0, y0, x1, y1, aw, acc)
            del x0, y0, x1, y1, aw
        del f, X, Y, alpha, ok, allok, onscreen
        bar.step(s1 - s0)


def tonemap(R, G, B, PAL):
    """Compress the accumulator to 8 bits.

    THE HUE BUG v1.5 SHIPPED, and the fix.
    v1.5 normalised each channel by its OWN maximum before the gamma curve.
    A channel carrying less energy was then stretched to the same full range as
    the brightest one, which destroys the ratio the colour table set. Measured
    on the same mesh: the browser's hex stroke is rgba(0,180,255), G/B = 0.706;
    the exact renderer reproduces 0.694; v1.5's additive path returned 0.879 --
    visibly greener, from the tone map alone, before atoms were even counted.

    TONE_NORM="luma"        curve max(R,G,B) once, scale all three by the gain
                            it received. Hue is preserved exactly. Default.
    TONE_NORM="shared"      one shared maximum, curve per channel. Better than
                            v1.5, still shifts hue a little (nonlinear curve).
    TONE_NORM="per_channel" v1.5's behaviour, kept so its renders reproduce
                            (Path X -- a frozen version is not corrected in place).
    """
    GAIN_ = PAL["gain"] if GAIN is None else GAIN
    TONE_ = PAL["tone"] if TONE is None else TONE
    GAMMA_ = PAL["gamma"] if GAMMA is None else GAMMA

    def curve(a):
        a = a * np.float32(GAIN_)
        if TONE_ == "log":
            return np.log1p(a)
        if TONE_ == "asinh":
            return np.arcsinh(a)
        return a

    g = np.float32(GAMMA_)
    if TONE_NORM == "luma":
        # Drive the curve with ONE channel-independent quantity and rescale RGB
        # by the gain it received. asinh and a gamma are both nonlinear, so
        # applying them to R and B separately compresses the larger one harder
        # and drags the ratio toward 1 -- that is a hue shift produced by the
        # tone map, not by the palette. Curving max(R,G,B) once and scaling all
        # three by the same factor leaves the ratio exactly where the colour
        # table put it, and cannot clip, since the driver is the largest channel.
        Lm = np.maximum(np.maximum(R, G), B)
        Lc = curve(Lm)
        mm = float(Lc.max())
        if mm > 0:
            Lc /= mm
        Lc = np.power(Lc, g)
        k = Lc / np.where(Lm > 1e-12, Lm, np.float32(1.0))
        R, G, B = R * k, G * k, B * k
    else:
        R, G, B = curve(R), curve(G), curve(B)
        if TONE_NORM == "shared":
            m = max(float(R.max()), float(G.max()), float(B.max()))
            if m > 0:
                R, G, B = R / m, G / m, B / m
        else:                                   # "per_channel" -- v1.5, hue-shifting
            for a in (R, G, B):
                mm = float(a.max())
                if mm > 0:
                    a /= mm
        R, G, B = np.power(R, g), np.power(G, g), np.power(B, g)
    R, G, B = np.clip(R, 0, 1), np.clip(G, 0, 1), np.clip(B, 0, 1)
    bg = np.array(PAL["bg"], np.float32) / 255.0
    img = np.stack([bg[0] + (1.0 - bg[0]) * R,
                    bg[1] + (1.0 - bg[1]) * G,
                    bg[2] + (1.0 - bg[2]) * B], axis=-1)
    return (np.clip(img, 0, 1) * 255.0 + 0.5).astype(np.uint8)


# =============================================================================
#  PART 6 -- THE PLANNER, and the certificate
# =============================================================================

def plan():
    """--plan : price every lane before allocating a byte of any of them."""
    ram = _detect_ram()
    budget = round(ram * 0.82, 1) if MEM_BUDGET_GB == "auto" else float(MEM_BUDGET_GB)
    print("=" * 79)
    print("  CAPACITY  .  %.1f GB RAM detected  .  budget %.1f GB" % (ram, budget))
    print("=" * 79)
    print("  The mesh is built in RAM and streamed to the GPU for rasterising, so")
    print("  VRAM does not cap how deep you can go -- RAM does. A hexagon is")
    print("  6 verts x 3 floats x 4 B = 72 B.  DRAW_HISTORY keeps ~1.17x the final.")
    print("  Refining adds only REFINE_CHUNK-sized transients on top.")
    print()
    print("  REFINE ALL   F' = 7F - 12        REFINE 6s   F' = 7F - 72")
    print("  P stays 12 through both. Always. That is the family.")
    print()
    hdr = "  %-22s %16s %10s %11s %8s %s"
    print(hdr % ("seed + order", "faces", "final", "w/ history", "exact?", "verdict"))
    print("  " + "-" * 77)
    seeds = [(g["name"], g["F"], 12) for g in GOLDEN[:7]]
    for name, F0, P0 in seeds:
        for ops in ([["all"] * k for k in (1, 2, 3)] +
                    [["all"] + ["hex"] * k for k in (3, 4, 5, 6)]):
            steps = predict_ops(F0, P0, ops)
            F = steps[-1][1]
            final = ((F - 12) * 6 + 12 * 5) * 12 / 2 ** 30
            hist = final * 7 / 6
            need = hist + 0.3
            v = "OK" if need < budget else ("tight" if need < ram * 0.85 else "NO")
            if F > FACE_BUDGET:
                v = "GUILLOTINE"
            lbl = "%s: %s" % (name, "all x%d" % len(ops) if all(o == "all" for o in ops)
                             else "all + 6s x%d" % (len(ops) - 1))
            print(hdr % (lbl, "{:,}".format(F), "%.2f GB" % final, "%.2f GB" % hist,
                         "yes" if F <= EXACT_FACE_BUDGET else "additive", v))
    print("  " + "-" * 77)
    print("  'exact?' is the RENDERER, not the math: matplotlib draws one Agg path")
    print("  per face. Past EXACT_FACE_BUDGET=%s use RENDERER='additive'."
          % "{:,}".format(EXACT_FACE_BUDGET))
    print("  The mesh never touches VRAM, so a GPU changes speed, not depth.")
    print("  DRAW_HISTORY=False buys back ~15%% if you need one more step.")
    print("=" * 79)


def certificate(path=None):
    """--cert : a receipt a stranger can reproduce.

    Curse 38: the clock lives OUTSIDE the hashed region and the output path is
    relative. Only reproducible mathematics is sealed -- the golden counts, the
    ladder, the char poly, the lock geometry. Re-run this on your own machine
    and the sha256 must match byte for byte. If it does not, the seal is the
    thing that is wrong, not your machine.
    """
    import json, hashlib
    payload = {"kernel": "genesis_wallpaper_v1_6",
               "P": 12, "chi": 2,
               "charpoly_M_light": light_matrix_charpoly(),
               "spectrum": ["phi^2", "1", "-1", "phi^-2"],
               "ladder_T_0_to_19": ladder_exact(20),
               "T_147_bits": ladder_exact(148)[147].bit_length(),
               "f64_exactness_dies_at_n": next(
                   (i for i, t in enumerate(ladder_exact(60)) if t > 2 ** 53), None),
               "shells": []}
    for g in GOLDEN[:7]:
        P, Hf, info = build_seed(g["name"], verbose=False)
        c = info["cert"]
        locks = lock_points(info, P, Hf)
        sigs = sorted({view_signature(L["pos"]) for L in locks if L["kind"] != "axis"})
        res = max(lock_residual(L["pos"], *fl_center_on(L["pos"], "fixed"))[0]
                  for L in locks)
        res_g = max(lock_residual(L["pos"], *fl_center_on(L["pos"], "genesis"))[0]
                    for L in locks)
        payload["shells"].append({
            "name": g["name"], "k": g["k"], "l": g["l"], "T": g["T"],
            "V": c["V"], "E": c["E"], "F": c["F"], "P": c["P"], "chi": c["chi"],
            "closure_pass": bool(c["pass"]), "locks": len(locks),
            "distinct_view_signatures": len(sigs),
            "max_lock_residual_fixed": "%.3e" % res,
            "max_lock_residual_genesis": "%.6f" % res_g})
    stable = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(stable.encode("utf-8")).hexdigest()
    out = {"payload": payload, "sha256": digest,
           # peers of the hash, never inside it
           "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "note": "sha256 covers 'payload' only. The timestamp is outside the "
                   "seal on purpose (Curse 38): hash the math, not the moment."}
    print("=" * 79)
    print("  MATH CERTIFICATE  .  sha256 = %s" % digest)
    print("=" * 79)
    for s in payload["shells"]:
        print("  %-8s Goldberg(%2d,%2d) T=%-4d V=%-7s F=%-7s P=%d chi=%d  %s"
              % (s["name"], s["k"], s["l"], s["T"], "{:,}".format(s["V"]),
                 "{:,}".format(s["F"]), s["P"], s["chi"],
                 "CLOSED" if s["closure_pass"] else "OPEN"))
        print("           locks %-7s distinct views %-4s  worst lock residual: "
              "fixed %s / genesis %s"
              % ("{:,}".format(s["locks"]), s["distinct_view_signatures"],
                 s["max_lock_residual_fixed"], s["max_lock_residual_genesis"]))
    print()
    print("  float64 exactness dies at n = %d.  T_147 needs %d mantissa bits."
          % (payload["f64_exactness_dies_at_n"], payload["T_147_bits"]))
    print("  Re-run --cert on your own machine. The sha256 must match. If it does")
    print("  not, do not trust the seal -- reproduce it or discard it.")
    print("=" * 79)
    if path:
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(out, fh, indent=2, sort_keys=True)
        print("  written : %s" % path)
    return out


# =============================================================================
#  PART 7 -- MAIN
# =============================================================================

def main():
    print("=" * 79)
    print("  GENESIS WALLPAPER GENERATOR v1.6  .  golden shells + flight lock")
    print("=" * 79)
    _pick_backend()
    print("  canvas  : %d x %d  (%.1f Mpx)" % (WIDTH, HEIGHT, WIDTH * HEIGHT / 1e6))
    print("  operator: inner=%s  mid=%s  jitter=%s  %s"
          % (INNER_SCALE, MID_SCALE, JITTER, "spherical" if SPHERICAL else "planar"))
    d = MID_SCALE - INNER_SCALE
    print("  crescent: mid-inner = %+.2f  ->  %s"
          % (d, "GAP (rosette)" if d > 0 else "OVERLAP (layered)" if d < 0
             else "flat, still open"))
    print("  order   : %s" % " -> ".join(OPS))
    print("  renderer: %s%s" % (RENDERER, "   (orthographic, culled, source-over)"
                                if RENDERER == "exact" else "   (additive lines)"))
    if MOBIUS_T > 0.0:
        print("  mobius  : t=%.2f  R=%s  W=%s  when=%s  project=%s"
              % (MOBIUS_T, MOBIUS_R, MOBIUS_W, MOBIUS_WHEN, MOBIUS_PROJECT))
    PAL = PALETTES[PALETTE]
    PENT = PAL["pent"] if PENT_BOOST is None else PENT_BOOST
    print("  palette : %s  (%s)   the browser's own rgba constants" % (PALETTE, PAL.get("mode")))
    print()

    rng = np.random.default_rng(12345)

    # ---- seed -----------------------------------------------------------
    P, H, info = build_seed(SEED, SPHERE_R)
    F0 = P.shape[0] + H.shape[0]

    # ---- THE GUILLOTINE, before a single byte is allocated (Curse 35) ----
    steps = predict_ops(F0, P.shape[0], OPS)
    print()
    print("  PRICE FIRST -- the whole plan, before anything is allocated:")
    print("  %-6s %-6s %16s %8s %12s" % ("step", "op", "faces", "pents", "mesh"))
    Fp = F0
    print("  %-6s %-6s %16s %8d %12s" % ("seed", SEED, "{:,}".format(F0), P.shape[0],
                                         "%.2f GB" % (F0 * 6 * 3 * 4 / 2 ** 30)))
    for i, (op, F, Pn) in enumerate(steps, 1):
        gb = ((F - Pn) * 6 + Pn * 5) * 12 / 2 ** 30
        print("  %-6d %-6s %16s %8d %12s" % (i, op, "{:,}".format(F), Pn, "%.2f GB" % gb))
        if F > FACE_BUDGET:
            raise SystemExit(
                "\n  HALT: step %d (%s) would reach %s faces > FACE_BUDGET %s.\n"
                "        The recurrence is exact and the kernel is correct at this\n"
                "        size -- 7x per level is what ends, not the math. Drop an op,\n"
                "        pick a smaller seed, or raise FACE_BUDGET on purpose."
                % (i, op, "{:,}".format(F), "{:,}".format(FACE_BUDGET)))
        Fp = F
    if RENDERER == "exact" and Fp > EXACT_FACE_BUDGET:
        print("\n  NOTE: %s faces is past EXACT_FACE_BUDGET %s. RENDERER='exact'"
              % ("{:,}".format(Fp), "{:,}".format(EXACT_FACE_BUDGET)))
        print("        will refuse. Switch to 'additive' or shorten OPS.")
    print()

    # ---- flight lock, computed on the SEED -------------------------------
    lock = apply_flight_lock(info, P, H)
    rx = lock["rx"] if lock else CAM_RX
    ry = lock["ry"] if lock else CAM_RY
    ax_, ay_ = (lock["rx"], lock["ry"]) if lock else (ROT_X, ROT_Y)
    if lock:
        print()

    _SPHERICAL_NOW[0] = SPHERICAL
    if MOBIUS_T > 0.0 and MOBIUS_WHEN == "first":
        P = sphere_to_mobius(P, MOBIUS_R, MOBIUS_W, MOBIUS_T)
        H = sphere_to_mobius(H, MOBIUS_R, MOBIUS_W, MOBIUS_T)
        if MOBIUS_PROJECT:
            print("  mobius  : twisted the SEED, refining with projectToSphere ON.")
            print("            children snap to r=SPHERE_R, inherited corners do not.")
            print("            that mismatch is the spikes. this is genesis' order.")
        else:
            _SPHERICAL_NOW[0] = False
            print("  mobius  : twisted the SEED, refining planar -> smooth strip.")

    generations = [(P.copy(), H.copy())] if DRAW_HISTORY else []
    kept = P.nbytes + H.nbytes
    print("  gen 0  %-8s P=%13s  H=%13s  F=%14s"
          % (SEED, "{:,}".format(P.shape[0]), "{:,}".format(H.shape[0]),
             "{:,}".format(F0)))

    for gi, op in enumerate(OPS, 1):
        nP, nH = P.shape[0], H.shape[0]
        if op == "all":
            fP, fH = nP, 5 * nP + 7 * nH
        elif op == "hex":
            fP, fH = nP, 7 * nH
        else:
            fP, fH = 0, nH + 7 * nP
        out_b = (fP * 5 + fH * 6) * 12
        need = (kept + out_b + min(REFINE_CHUNK, max(nP, nH)) * 6 * 6 * 12 * 3) / 2 ** 30
        if need > MEM_BUDGET_GB:
            print("\n  gen %d  %s: needs ~%.1f GB for F=%s -- over MEM_BUDGET_GB=%s."
                  % (gi, op, need, "{:,}".format(fP + fH), MEM_BUDGET_GB))
            print("  Stopping here. Raise MEM_BUDGET_GB, set DRAW_HISTORY=False, or")
            print("  drop one op. The refusal is the feature.")
            break

        bar = Bar(nP + nH, "gen %d %s refine" % (gi, op))
        newP = [P] if op == "hex" else []
        newH = [H] if op == "pent" else []
        if op in ("all", "pent") and nP:
            ip, cp = refine(P, SPHERE_R, rng, bar)
            newP.append(ip)
            newH.append(cp)
        if op in ("all", "hex") and nH:
            ih, ch = refine(H, SPHERE_R, rng, bar)
            newH.append(ih)
            newH.append(ch)
        P = np.concatenate(newP, 0) if newP else np.zeros((0, 5, 3), np.float32)
        H = np.concatenate(newH, 0) if newH else np.zeros((0, 6, 3), np.float32)
        del newP, newH
        if DRAW_HISTORY:
            generations.append((P, H))
        else:
            generations = [(P, H)]
        kept = sum(a.nbytes + b.nbytes for a, b in generations)
        bar.done("F=%s   mesh %.2f GB" % ("{:,}".format(P.shape[0] + H.shape[0]),
                                          kept / 2 ** 30))

    if MOBIUS_T > 0.0 and MOBIUS_WHEN == "last":
        print("  mobius  : applied after refinement (genesis' own order)")
        generations = [(sphere_to_mobius(a, MOBIUS_R, MOBIUS_W, MOBIUS_T),
                        sphere_to_mobius(b, MOBIUS_R, MOBIUS_W, MOBIUS_T))
                       for a, b in generations]

    total_edges = sum(p.shape[0] * 5 + h.shape[0] * 6 for p, h in generations)
    print("\n  generations: %d   mesh in RAM: %.2f GB   edges: %s\n"
          % (len(generations), kept / 2 ** 30, human(total_edges)))

    if RENDERER == "exact":
        # genesis has no history -- it draws the mesh it currently holds
        img = render_exact(P, H, rx, ry)
        del generations, P, H
    else:
        M = make_camera(ax_, ay_, ROT_Z)
        _scale = (MOBIUS_R + MOBIUS_W) if MOBIUS_T > 0.0 else SPHERE_R
        D = np.float32(CAM_DIST * (SPHERE_R * (1 - MOBIUS_T) + _scale * MOBIUS_T))
        focal = np.float32((HEIGHT * 0.5) / math.tan(math.radians(FOV_DEG) * 0.5) * ZOOM)
        face_chunk = max(50_000, int(CHUNK_SAMPLES) // 24)

        Rb = xp.zeros(WIDTH * HEIGHT, xp.float32)
        Gb = xp.zeros(WIDTH * HEIGHT, xp.float32)
        Bb = xp.zeros(WIDTH * HEIGHT, xp.float32)

        def blend(acc, rgb, mul):
            Rb[...] += acc * xp.float32(rgb[0] / 255.0 * mul)
            Gb[...] += acc * xp.float32(rgb[1] / 255.0 * mul)
            Bb[...] += acc * xp.float32(rgb[2] / 255.0 * mul)

        facetype = PAL.get("mode", "generation") == "facetype"
        ncol = len(PAL.get("colors", [(1, 1, 1)]))
        span = max(1, len(generations) - 1)

        for gi, (Pg, Hg) in enumerate(generations):
            for tag, faces in (("pent", Pg), ("hex", Hg)):
                if faces.shape[0] == 0:
                    continue
                isP = (tag == "pent")
                acc = xp.zeros(WIDTH * HEIGHT, xp.float32)
                bar = Bar(faces.shape[0], "gen %d %s edges" % (gi, tag))
                draw_faces(faces, acc, M, D, focal, bar, face_chunk)
                bar.done("%s edges" % human(faces.shape[0] * faces.shape[1]))
                if facetype:
                    blend(acc, PAL["pent_edge"] if isP else PAL["hex_edge"],
                          (PAL["pent_mul"] if isP else PAL["hex_mul"]) * (PENT if isP else 1.0))
                else:
                    c = PAL["colors"][min(ncol - 1, int(round(gi * (ncol - 1) / span)))]
                    blend(acc, tuple(v * 255 for v in c), PENT if isP else 1.0)
                del acc
                if ATOM_SIZE > 0.0:
                    r = ATOM_SIZE * (2.0 if isP else 1.2)
                    acc = xp.zeros(WIDTH * HEIGHT, xp.float32)
                    bar = Bar(faces.shape[0], "gen %d %s atoms r=%.1f" % (gi, tag, r))
                    draw_faces(faces, acc, M, D, focal, bar, face_chunk,
                               atoms=True, atom_r=r)
                    bar.done("vertex discs")
                    if facetype:
                        blend(acc, PAL["pent_atom"] if isP else PAL["hex_atom"],
                              PAL["pent_atom_mul"] if isP else PAL["hex_atom_mul"])
                    else:
                        c = PAL["colors"][min(ncol - 1, int(round(gi * (ncol - 1) / span)))]
                        blend(acc, tuple(v * 255 for v in c), 1.3)
                    del acc

        print("\n  tone mapping and encoding ...")
        if GPU:
            Rn, Gn, Bn = xp.asnumpy(Rb), xp.asnumpy(Gb), xp.asnumpy(Bb)
            del Rb, Gb, Bb
            xp.get_default_memory_pool().free_all_blocks()
        else:
            Rn, Gn, Bn = Rb, Gb, Bb
        img = tonemap(Rn.reshape(HEIGHT, WIDTH), Gn.reshape(HEIGHT, WIDTH),
                      Bn.reshape(HEIGHT, WIDTH), PAL)
        del generations, P, H

    out = OUT
    if out is None:
        ops_tag = "".join("%d%s" % (sum(1 for o in OPS if o == k), k[0])
                          for k in ("all", "hex", "pent") if any(o == k for o in OPS))
        lk = ("_lk" + "".join(ch for ch in FLIGHT_LOCK if ch.isalnum())[:12]
              + FLIGHT_SIGN[0]) if FLIGHT_LOCK else ""
        out = os.path.join(
            OUT_DIR,
            "%d" % int(time.time())
            + ("_gens_" if RENDERER == "additive" else "_exact_")
            + "in%.2f_mid%.2f_%s_%s" % (INNER_SCALE, MID_SCALE, SEED, ops_tag)
            + lk
            + (("_atm%.2f" % ATOM_SIZE) if RENDERER == "additive"
               else ("_zm%.0f_atm%.2f" % (CAM_ZOOM, CAM_ATOM)))
            + (("_mob%.2f%s%s" % (MOBIUS_T, MOBIUS_WHEN[0],
                                  "p" if MOBIUS_PROJECT else "s")) if MOBIUS_T > 0 else "")
            + ".jpg")
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    Image.fromarray(img, "RGB").save(out, "JPEG", quality=JPG_QUALITY,
                                     optimize=True, progressive=True)
    print("  written : %s\n            %.1f MB   %dx%d"
          % (out, os.path.getsize(out) / 2 ** 20, WIDTH, HEIGHT))
    print("=" * 79)
    return out



# =============================================================================
# v1.7  THE FRACTAL LANE
# -----------------------------------------------------------------------------
# The browser holds two or three levels before the DOM gives out. Python walks
# eight. This lane measures the scaling dimension of the refine hierarchy by box
# counting, using the operator's own faces as the boxes:
#
#       N(L) faces of mean diameter d(L)   ->   N ~ d^-D
#       D = log( N(L+1)/N(L) ) / log( d(L)/d(L+1) )
#
# Nothing about refineFace's branching is assumed. It is COUNTED, from the
# shipped refine() and the shipped build_seed() -- never a re-implementation.
# (Curse 40: a harness that retypes the function it tests has tested itself.)
#
# THEA K2: "fractal means HIERARCHY, not infinity, unless a non-integer
# dimension is separately demonstrated." This is that demonstration, and it is
# expected to return 2. That IS the result: branching and shrinking are locked
# together by area, so a surface operator tiling a surface stays
# two-dimensional however deep the tree runs.
# =============================================================================


def _fc_stats(arr):
    """(m, k, 3) vertex array -> (count, mean diameter, total area)."""
    if arr is None or len(arr) == 0:
        return 0, 0.0, 0.0
    a = np.asarray(arr, dtype=np.float64)
    a = a.reshape(-1, a.shape[-2], a.shape[-1])
    c = a.mean(axis=1, keepdims=True)
    diam = 2.0 * np.linalg.norm(a - c, axis=2).mean(axis=1)
    nxt = np.roll(a, -1, axis=1)
    cr = np.cross(a - c, nxt - c)
    area = 0.5 * np.linalg.norm(cr, axis=2).sum(axis=1)
    return int(a.shape[0]), float(diam.mean()), float(area.sum())


def _fc_gen(P, Hf):
    np_, dp, ap = _fc_stats(P)
    nh, dh, ah = _fc_stats(Hf)
    n = np_ + nh
    d = ((dp * np_) + (dh * nh)) / n if n else 0.0
    return {"n": n, "pent": np_, "hex": nh, "d": d, "area": ap + ah}


def _fc_flat(x):
    a = np.asarray(x)
    return a.reshape(-1, a.shape[-2], a.shape[-1])


def print_fractal(seed=None, depth=3, op="all"):
    seed = seed or SEED
    print("")
    print("=" * 79)
    print("  THE FRACTAL LANE -- box counting on the operator's own faces")
    print("=" * 79)
    print("  seed %s   depth %d   op %s" % (seed, depth, op))
    print("")

    print("  A. THE CERTIFIED TOWER (Lane B) -- exact integer counts")
    print("     %-4s %-9s %-13s %-13s %-12s %s"
          % ("n", "T", "V = 20T", "R ~ sqrt(T)", "logV/logR", "P"))
    for g in golden_catalog(8):
        T, V = int(g["T"]), int(g["V"])
        R = math.sqrt(T)
        Dt = (math.log(V) / math.log(R)) if R > 1.0 else float("nan")
        print("     %-4d %-9d %-13d %-13.6f %-12s %d"
              % (g["idx"], T, V, R, ("%.6f" % Dt) if Dt == Dt else "--", int(g["P"])))
    print("")
    print("     V grows like T and R like sqrt(T), so log V / log R -> 2 EXACTLY.")
    print("     Two counts and one square root. Nothing is fitted.")
    print("")

    print("  B. THE REFINE HIERARCHY (Lane A) -- MEASURED from the shipped refine()")
    try:
        P, Hf, info = build_seed(seed, verbose=False)
    except Exception as exc:
        print("     REFUSED: the shipped builder did not run (%s)." % exc)
        print("     This lane will not substitute a replica -- see Curse 40.")
        return
    try:
        rng = np.random.default_rng(20260809)
    except Exception:
        rng = np.random

    print("     %-5s %-13s %-11s %-11s %-16s %s"
          % ("gen", "faces", "pentagons", "hexagons", "mean diam", "total area"))
    cen = [_fc_gen(P, Hf)]
    r0 = cen[0]
    print("     %-5d %-13s %-11d %-11d %-16.9f %.9f"
          % (0, human(r0["n"]), r0["pent"], r0["hex"], r0["d"], r0["area"]))

    for step in range(depth):
        prev = cen[-1]
        pred = face_growth(prev["n"], prev["pent"], op)
        print("     -> next generation priced at %s faces before allocating (Curse 35)"
              % human(pred[0]))
        try:
            newP, newH = None, []
            if op in ("all", "pent") and len(P):
                ip, cp = refine(P, SPHERE_R, rng)
                newP = _fc_flat(ip)
                newH.append(_fc_flat(cp))
            else:
                newP = P
            if op in ("all", "hex") and len(Hf):
                ih, ch = refine(Hf, SPHERE_R, rng)
                newH.append(_fc_flat(ih))
                newH.append(_fc_flat(ch))
            elif len(Hf):
                newH.append(_fc_flat(Hf))
        except Exception as exc:
            print("     REFUSED at generation %d: %s" % (step + 1, exc))
            break
        P = newP
        Hf = np.concatenate(newH, axis=0) if newH else None
        row = _fc_gen(P, Hf)
        cen.append(row)
        print("     %-5d %-13s %-11d %-11d %-16.9f %.9f"
              % (step + 1, human(row["n"]), row["pent"], row["hex"], row["d"], row["area"]))

    print("")
    print("  C. THE SCALING DIMENSION -- D = log(b) / log(1/s), measured")
    print("     %-9s %-12s %-12s %-16s %-14s %s"
          % ("gens", "b (count)", "s (diam)", "area ratio", "D (diam)", "D (area)"))
    good, areas = [], []
    for i in range(1, len(cen)):
        lo, hi = cen[i - 1], cen[i]
        if lo["n"] == 0 or lo["d"] <= 0 or hi["d"] <= 0:
            continue
        b = hi["n"] / float(lo["n"])
        s = hi["d"] / lo["d"]
        aR = hi["area"] / (lo["area"] or 1.0)
        D = (math.log(b) / math.log(1.0 / s)) if (0.0 < s < 1.0 and b > 1.0) else float("nan")
        # The DIAMETER estimator is only a similarity ratio when the children are
        # similar copies of the parent. Here they are not: pentagons beget hexagons,
        # and the area ratio says the children are not a partition. The AREA
        # estimator needs neither -- each child holds aR/b of the parent's area, so
        # the linear ratio is sqrt(aR/b) whatever the shape.
        Da = (2.0 * math.log(b) / (math.log(b) - math.log(aR))) if (b > 1.0 and aR > 0.0) else float("nan")
        print("     %-9s %-12.6f %-12.6f %-16.9f %-14s %s"
              % ("%d->%d" % (i - 1, i), b, s, aR,
                 ("%.6f" % D) if D == D else "unresolved",
                 ("%.6f" % Da) if Da == Da else "unresolved"))
        if Da == Da:
            good.append(Da)
            areas.append(aR)

    print("")
    if not good:
        print("     No resolvable pair. Raise --fractal-depth.")
    else:
        m = sum(good) / len(good)
        sd = (sum((x - m) ** 2 for x in good) / len(good)) ** 0.5
        print("     mean D = %.6f   spread %.6f   over %d generation pairs"
              % (m, sd, len(good)))
        print("")
        aM = sum(areas) / len(areas)
        conserved = abs(aM - 1.0) < 0.01
        print("     mean area ratio = %.9f   %s"
              % (aM, "conserved" if conserved else "NOT conserved -- area is lost every generation"))
        print("")
        if conserved:
            print("     VERDICT: the children tile the parent, so D = %.4f is a surface." % m)
            print("     Branching and shrinking are locked together by area conservation.")
            print("     In THEA fractal means HIERARCHY (K2), and this is the number that")
            print("     says it is not more.")
        else:
            print("     VERDICT: D = %.6f, and it is NOT 2." % m)
            print("     This operator loses a fixed %.4f of the area every generation, so the" % aM)
            print("     children are not a partition of their parent -- there are gaps, and")
            print("     the gaps are self-similar. The limit set has zero area and a genuine")
            print("     non-integer dimension. GENESIS calls itself a Fractal Graph Explorer")
            print("     and on this lane it has earned the word.")
            print("")
            print("     Lane B, the certified Goldberg tower, is exactly 2. Lane A is %.4f." % m)
            print("     Two operators, two dimensions, one shell. That is the whole finding,")
            print("     and neither number was assumed.")
            print("")
            print("     D depends on INNER_SCALE and MID_SCALE: set them so the children")
            print("     tile and the area ratio returns to 1 and D returns to 2. The")
            print("     dimension is a dial on this operator, not a property of the sphere.")
        print("")
        print("     Trust the area column, not the diameter column: the diameter estimator")
        print("     assumes the children are similar copies of the parent, and here a")
        print("     pentagon begets hexagons. Its numbers drift and straddle 2 for that")
        print("     reason alone.")

    last = cen[-1]
    print("")
    print("  D. THE ZERO-DIMENSIONAL PART")
    print("     faces at the deepest generation     : %s" % human(last["n"]))
    print("     pentagons at the deepest generation : %d" % last["pent"])
    if last["n"]:
        print("     pentagon fraction                   : %.9f %%"
              % (100.0 * last["pent"] / last["n"]))
    print("     Euler fixes the pentagon count while the face count grows without")
    print("     bound, so the defect set has density zero. The object is a")
    print("     2-dimensional sheet carrying a 0-dimensional set of twelve.")
    print("")
    print("  P=12. chi=2. The price is always paid.")
    print("=" * 79)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        prog="genesis_wallpaper_v1_6.py",
        description="genesis v8.1 operator + v8.5.2 golden shells + the flight lock")
    ap.add_argument("--plan", action="store_true", help="capacity, before you allocate")
    ap.add_argument("--locks", action="store_true", help="the lock table, every shell")
    ap.add_argument("--locks-csv", metavar="PATH", nargs="?", const="genesis_locks_v1_6.csv",
                    help="write every lock of every shell to CSV")
    ap.add_argument("--ladder", action="store_true", help="the exact ladder vs the fence")
    ap.add_argument("--cert", metavar="PATH", nargs="?", const="",
                    help="reproducible math certificate (optionally to a file)")
    ap.add_argument("--seed", metavar="NAME", help="override SEED for this run")
    ap.add_argument("--lock", metavar="LABEL", help="override FLIGHT_LOCK for this run")
    ap.add_argument("--sign", choices=("fixed", "genesis"), help="override FLIGHT_SIGN")
    ap.add_argument("--out", metavar="PATH", help="output image path")
    ap.add_argument("--rows", type=int, default=14, help="lock-table rows per shell")
    ap.add_argument("--fractal", action="store_true",
                    help="box-count the hierarchy: N ~ d^-D, measured from the shipped refine")
    ap.add_argument("--fractal-depth", type=int, default=3, dest="fractal_depth",
                    help="how many refines the fractal lane walks (default 3)")
    ap.add_argument("--fractal-op", choices=("all", "hex", "pent"), default="all",
                    dest="fractal_op", help="which faces the fractal lane refines")
    ap.add_argument("--ops", metavar="SPEC",
                    help="override OPS, e.g. 'all,hex,hex,hex' or 'all+4hex'")
    ap.add_argument("--renderer", choices=("exact", "additive"), help="override RENDERER")
    ap.add_argument("--size", metavar="WxH", help="override WIDTH x HEIGHT, e.g. 3840x2160")
    ap.add_argument("--zoom", type=float, help="override CAM_ZOOM (exact mode)")
    a = ap.parse_args()

    if a.seed:
        SEED = a.seed
    if a.lock:
        FLIGHT_LOCK = a.lock
    if a.sign:
        FLIGHT_SIGN = a.sign
    if a.out:
        OUT = a.out
    if a.renderer:
        RENDERER = a.renderer
    if a.zoom:
        CAM_ZOOM = a.zoom
    if a.size:
        _w, _h = a.size.lower().split("x")
        WIDTH, HEIGHT = int(_w), int(_h)
    if a.ops:
        _spec, _out = a.ops.replace(" ", ""), []
        for _tok in _spec.replace("+", ",").split(","):
            if not _tok:
                continue
            _n = "".join(c for c in _tok if c.isdigit())
            _k = "".join(c for c in _tok if c.isalpha())
            if _k not in ("all", "hex", "pent"):
                raise SystemExit("  --ops: unknown op %r -- use all | hex | pent" % _k)
            _out += [_k] * (int(_n) if _n else 1)
        OPS = _out

    did = False
    if getattr(a, "fractal", False):
        print_fractal(seed=(SEED if a.seed else None),
                      depth=getattr(a, "fractal_depth", 3),
                      op=getattr(a, "fractal_op", "all"))
        did = True
    if a.ladder:
        print_ladder()
        did = True
    if a.plan:
        plan()
        did = True
    if a.locks:
        print_locks(shells=[SEED] if a.seed else None, max_rows=a.rows)
        did = True
    if a.locks_csv:
        write_locks_csv(a.locks_csv, shells=[SEED] if a.seed else None)
        did = True
    if a.cert is not None:
        certificate(a.cert or None)
        did = True
    if not did:
        main()
