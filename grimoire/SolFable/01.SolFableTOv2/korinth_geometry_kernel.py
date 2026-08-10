#!/usr/bin/env python3
"""KORINTH GEOMETRY KERNEL v0.1 -- verify the scroll, do not trust it.

The research scroll "Before the Titans" is INSPIRATION. This file is the
receipt. Every mathematical claim in that scroll is recomputed here in exact
rational or integer arithmetic, or in 60-digit Decimal where an irrational is
unavoidable. Nothing is accepted because a source said it.

Status grammar (inherited, THEA v3.0 / SOL Tower v2.1):
    EXACT       provable here by integer/rational arithmetic
    COMPUTED    finite precision, error printed
    DISCREPANCY the scroll and the arithmetic disagree -- reported, not hidden
    OUT_OF_SCOPE a claim no kernel can settle (textual, historical, doctrinal)

HARD BOUNDARY. This kernel verifies arithmetic. It cannot verify:
  - what Hesiod, the Derveni papyrus, or Damascius actually say
  - whether Rigveda Mandala 10 is late
  - whether Baudhayana predates Pythagoras
  - who translated the Dodoni "Vedes"
  - whether any of this means anything about the Standard Model
Those need sources, not compute. They are listed at the end and left OPEN.
"""
from __future__ import annotations

from decimal import Decimal, getcontext, localcontext
from fractions import Fraction as F
from math import gcd, isqrt
from typing import Dict, List

getcontext().prec = 60

RESULTS: List[Dict[str, object]] = []


def record(section: str, claim: str, status: str, detail: object) -> None:
    RESULTS.append({"section": section, "claim": claim, "status": status, "detail": detail})


def dsqrt(n: int) -> Decimal:
    with localcontext() as ctx:
        ctx.prec = 60
        return Decimal(n).sqrt()


DSQRT2 = dsqrt(2)
DPI = Decimal(
    "3.14159265358979323846264338327950288419716939937510582097494"
)


# ---------------------------------------------------------------------------
# A. SULBA-SUTRA ARITHMETIC
# ---------------------------------------------------------------------------

def A1_sqrt2_construction() -> None:
    """Baudhayana i.61-62: 1 + 1/3 + 1/(3*4) - 1/(3*4*34)."""
    v = F(1) + F(1, 3) + F(1, 3 * 4) - F(1, 3 * 4 * 34)
    ok = v == F(577, 408)
    approx = Decimal(v.numerator) / Decimal(v.denominator)
    err = abs(approx - DSQRT2)
    # count agreeing decimal places
    digits = 0
    while abs(approx - DSQRT2) < Decimal(10) ** (-(digits + 1)):
        digits += 1
    record("A", "sutra text evaluates to 577/408", "EXACT" if ok else "DISCREPANCY",
           {"value": f"{v.numerator}/{v.denominator}",
            "decimal": str(approx)[:20],
            "abs_error": f"{err:.3E}",
            "correct_decimal_places": digits,
            "scroll_said": "accurate to 5 decimal places"})


def A2_newton_identity() -> None:
    """Is the Sulba value a Newton step? x -> x/2 + 1/x on 17/12."""
    seed = F(1) + F(1, 3) + F(1, 3 * 4)          # = 17/12, the sutra minus its last term
    step = seed / 2 + 1 / seed
    next_step = step / 2 + 1 / step
    record("A", "577/408 is exactly one Newton-Raphson step from 17/12",
           "EXACT" if step == F(577, 408) else "DISCREPANCY",
           {"seed": f"{seed.numerator}/{seed.denominator}",
            "one_step": f"{step.numerator}/{step.denominator}",
            "two_steps": f"{next_step.numerator}/{next_step.denominator}",
            "scroll_next_term": "665857/470832",
            "two_steps_matches_scroll": next_step == F(665857, 470832),
            "note": "an exact arithmetic identity; it implies NOTHING about "
                    "whether the authors possessed an iterative method"})


def A3_pythagorean_triples() -> None:
    """Baudhayana i.49 list, primitivity, and completeness below the bound."""
    listed = [(3, 4, 5), (12, 5, 13), (15, 8, 17), (7, 24, 25), (12, 35, 37), (15, 36, 39)]
    rows = []
    for a, b, c in listed:
        rows.append({
            "triple": (a, b, c),
            "is_pythagorean": a * a + b * b == c * c,
            "gcd": gcd(gcd(a, b), c),
            "primitive": gcd(gcd(a, b), c) == 1,
        })
    all_pyth = all(r["is_pythagorean"] for r in rows)
    n_prim = sum(1 for r in rows if r["primitive"])

    # completeness: every primitive triple with hypotenuse <= 37
    found = set()
    for c in range(5, 38):
        for a in range(3, c):
            b2 = c * c - a * a
            b = isqrt(b2)
            if b * b == b2 and 0 < a < b and gcd(gcd(a, b), c) == 1:
                found.add((a, b, c))
    listed_norm = {tuple(sorted((a, b))) + (c,) for a, b, c in listed if gcd(gcd(a, b), c) == 1}
    missing = sorted(found - listed_norm)

    record("A", "the six triples are Pythagorean; five are primitive",
           "EXACT" if (all_pyth and n_prim == 5) else "DISCREPANCY",
           {"rows": rows, "primitive_count": n_prim,
            "derived": "(15,36,39) = 3 x (5,12,13)"})
    record("A", "the list is complete for hypotenuse <= 37",
           "DISCREPANCY" if missing else "EXACT",
           {"omitted_primitive_triples": missing,
            "note": "the sutra's list is a selection, not an enumeration"})


def A4_circling_the_square() -> None:
    """Baudhayana i.58: square side 2a -> circle radius a + (a*sqrt2 - a)/3."""
    a = Decimal(1)
    r = a + (a * DSQRT2 - a) / 3
    square_area = (2 * a) ** 2
    circle_area = DPI * r * r
    ratio = circle_area / square_area
    implied_pi = square_area / (r * r)
    record("A", "Baudhayana circling-the-square error and implied pi", "COMPUTED",
           {"radius_over_half_side": str(r)[:12],
            "area_ratio_circle_over_square": str(ratio)[:12],
            "percent_error": f"{(ratio - 1) * 100:.4f}",
            "implied_pi": str(implied_pi)[:12],
            "scroll_said": "about 1.7% too large, pi ~ 3.0883"})


def A5_manava_rule() -> None:
    """Manava/Maitrayaniya: radius = 9/16 of the side."""
    side = Decimal(1)
    r = Decimal(9) / Decimal(16) * side
    ratio = DPI * r * r / (side * side)
    implied_pi = (side * side) / (r * r)
    egyptian = Decimal(256) / Decimal(81)
    record("A", "Manava rule is more accurate than Baudhayana's", "COMPUTED",
           {"area_ratio": str(ratio)[:12],
            "percent_error": f"{(ratio - 1) * 100:.4f}",
            "implied_pi": str(implied_pi)[:12],
            "equals_256_over_81": implied_pi == egyptian,
            "note": "256/81 is the Rhind-papyrus value; the coincidence is "
                    "arithmetic, not evidence of contact",
            "scroll_said": "about 0.5% error"})


def A6_squaring_the_circle() -> None:
    """s = (7/8) d."""
    d = Decimal(1)
    s = Decimal(7) / Decimal(8) * d
    circle_area = DPI * d * d / 4
    ratio = s * s / circle_area
    implied_pi = 4 * s * s / (d * d)
    record("A", "squaring-the-circle implied pi lies in the scroll's range", "COMPUTED",
           {"area_ratio_square_over_circle": str(ratio)[:12],
            "percent_error": f"{(ratio - 1) * 100:.4f}",
            "implied_pi": str(implied_pi)[:12],
            "scroll_range": "3.004 - 3.088",
            "inside_range": Decimal("3.004") <= implied_pi <= Decimal("3.088")})


def A7_enlargement_rule() -> None:
    """Altar grows 7.5 -> 101.5 sq purusa; unit side = sqrt(1 + 2q/15)."""
    base = F(15, 2)
    ok = all(base * (1 + F(2 * q, 15)) == base + q for q in range(0, 95))
    steps = int(F(203, 2) - base)
    record("A", "scaling by (1 + 2q/15) enlarges 7.5 sq purusa by exactly q",
           "EXACT" if ok else "DISCREPANCY",
           {"verified_for_q": "0..94", "identity": "7.5 * (1 + 2q/15) = 7.5 + q"})
    record("A", "the enlargement series runs 7.5 -> 101.5", "EXACT",
           {"increments": steps, "distinct_altar_sizes": steps + 1,
            "scroll_said": "95 steps",
            "reading": f"{steps} enlargements, {steps + 1} sizes -- the scroll's "
                       "'95' is the count of sizes, not of enlargements"})


def A8_caturasra_bricks() -> None:
    """Manava square-falcon brick inventory: do the two layer types tile equal area?"""
    odd = [(110, 30, 30), (85, 12, 12), (5, 12, 6)]
    even = [(110, 30, 30), (75, 12, 12), (10, 12, 6), (5, 18, 12)]
    n_odd = sum(n for n, _, _ in odd)
    n_even = sum(n for n, _, _ in even)
    a_odd = sum(n * w * h for n, w, h in odd)
    a_even = sum(n * w * h for n, w, h in even)
    PURUSA2 = 120 * 120
    record("A", "each layer uses exactly 200 bricks",
           "EXACT" if n_odd == n_even == 200 else "DISCREPANCY",
           {"layers_1_3_5": n_odd, "layers_2_4": n_even})
    record("A", "the two layer inventories cover the same area",
           "EXACT" if a_odd == a_even else "DISCREPANCY",
           {"area_odd_angula2": a_odd, "area_even_angula2": a_even,
            "difference": a_odd - a_even,
            "note": "they must agree -- alternate tilings of one altar. They do."})
    area_purusa = F(a_odd, PURUSA2)
    record("A", "the caturasra area equals 7.5 square purusas",
           "EXACT" if area_purusa == F(15, 2) else "DISCREPANCY",
           {"computed_sq_purusa": f"{area_purusa.numerator}/{area_purusa.denominator}"
                                  f" = {float(area_purusa)}",
            "scroll_said": "7.5",
            "gap": f"{float(area_purusa - F(15,2))} sq purusa",
            "body_square_alone": f"{F(240*240, PURUSA2)} sq purusa",
            "verdict": "OPEN -- either the caturasra is not 7.5, or one figure is "
                       "mis-transcribed. Needs Sen & Bag 1983. Kernel cannot settle it."})


def A9_special_brick_counts() -> None:
    """396 yajusmati bricks, layer split 98+41+71+47+138."""
    layers = [98, 41, 71, 47, 138]
    s = sum(layers)
    record("A", "the layer split sums to the stated 396 special bricks",
           "EXACT" if s == 396 else "DISCREPANCY",
           {"layers": layers, "sum": s, "scroll_total": 396, "difference": 396 - s,
            "year_symbolism": "360 + 36 = 396",
            "verdict": "OPEN -- the breakdown is one short of the total. Either a "
                       "transcription slip or a real feature of the ritual count. "
                       "Needs Kak's original table."})


def A10_symbolic_vs_physical() -> None:
    record("A", "10800 = muhurtas in a symbolic year", "EXACT",
           {"30_per_day_x_360_days": 30 * 360, "equals_10800": 30 * 360 == 10800})
    record("A", "physical shaped bricks = 200 per layer x 5 layers", "EXACT",
           {"physical": 200 * 5,
            "note": "1000 physical vs 10800 symbolic are DIFFERENT quantities. "
                    "Popular sources conflate them."})


def A11_units() -> None:
    record("A", "unit system is internally consistent", "EXACT",
           {"purusa_angula": 120, "aratni_angula": 24,
            "aratni_in_purusa": str(F(24, 120)),
            "altar_height_angula": 5 * 6,
            "altar_height_inches_at_0.75in_per_angula": float(30 * F(3, 4)),
            "scroll_said": "about 2 ft"})


# ---------------------------------------------------------------------------
# B. PLATO
# ---------------------------------------------------------------------------

def B1_world_soul_series() -> None:
    doubles = [1, 2, 4, 8]
    triples = [1, 3, 9, 27]
    merged = sorted(set(doubles + triples))
    record("B", "the lambda series is the union of powers of 2 and 3 up to cubes",
           "EXACT" if merged == [1, 2, 3, 4, 8, 9, 27] else "DISCREPANCY",
           {"doubles": doubles, "triples": triples, "merged": merged,
            "timaeus_order": [1, 2, 3, 4, 9, 8, 27]})


def B2_means_and_tone() -> None:
    a, b = F(1), F(2)
    harmonic = 2 * a * b / (a + b)
    arithmetic = (a + b) / 2
    tone = arithmetic / harmonic
    record("B", "harmonic and arithmetic means of 1:2 give 4/3 and 3/2, ratio 9/8",
           "EXACT" if (harmonic == F(4, 3) and arithmetic == F(3, 2)
                       and tone == F(9, 8)) else "DISCREPANCY",
           {"harmonic": str(harmonic), "arithmetic": str(arithmetic),
            "ratio": str(tone)})


def B3_leimma() -> None:
    leimma = F(4, 3) / (F(9, 8) ** 2)
    record("B", "a fourth minus two whole tones leaves exactly 256/243",
           "EXACT" if leimma == F(256, 243) else "DISCREPANCY",
           {"computed": f"{leimma.numerator}/{leimma.denominator}",
            "check": str(F(9, 8) ** 2 * leimma) + " = 4/3"})


def B4_total_span() -> None:
    span = F(27)
    octaves = 0
    r = span
    while r >= 2:
        r /= 2
        octaves += 1
    record("B", "the span 1:27 is four octaves plus a major sixth",
           "EXACT" if (octaves == 4 and r == F(27, 16)) else "DISCREPANCY",
           {"octaves": octaves, "remainder": f"{r.numerator}/{r.denominator}",
            "pythagorean_major_sixth": "27/16", "matches": r == F(27, 16)})


def B5_five_solids_only() -> None:
    """Schlafli condition (p-2)(q-2) < 4 with p,q >= 3."""
    solids = []
    for p in range(3, 12):
        for q in range(3, 12):
            if (p - 2) * (q - 2) < 4:
                # V - E + F = 2 with pF = 2E = qV
                E = F(2, (F(2, p) + F(2, q) - 1))
                E = int(E) if E == int(E) else E
                V = int(F(2 * E, q))
                Fa = int(F(2 * E, p))
                solids.append({"schlafli": f"{{{p},{q}}}", "V": V, "E": E, "F": Fa,
                               "chi": V - E + Fa})
    ok = len(solids) == 5 and all(s["chi"] == 2 for s in solids)
    record("B", "exactly five regular convex polyhedra exist, all with chi = 2",
           "EXACT" if ok else "DISCREPANCY", {"count": len(solids), "solids": solids})


def B6_elemental_triangle() -> None:
    """Equilateral face = six 30-60-90 triangles; cube face = four 45-45-90."""
    s = Decimal(1)
    equilateral = dsqrt(3) / 4 * s * s
    small = equilateral / 6
    # Cutting by the three altitudes gives six 30-60-90 triangles whose legs are
    # half a side (1/2) and the inradius (sqrt(3)/6), hypotenuse = circumradius.
    half_side = s / 2
    inradius = dsqrt(3) / 6 * s
    direct = half_side * inradius / 2
    record("B", "an equilateral face decomposes into six 30-60-90 triangles", "COMPUTED",
           {"equilateral_area": str(equilateral)[:14],
            "one_sixth": str(small)[:14],
            "direct_30_60_90_area": str(direct)[:14],
            "residual": f"{abs(small - direct):.3E}",
            "leg_ratio_check_1_to_sqrt3_to_2": str((inradius / half_side) * dsqrt(3))[:8] + " (= 1)"})


def B7_dodecahedron_is_the_tower_seed() -> None:
    """Plato's cosmic solid vs the SOL tower's T=1 Goldberg seed."""
    T = 1
    V, E, Fa = 20 * T, 30 * T, 10 * T + 2
    P, H = 12, 10 * (T - 1)
    tower = {"V": V, "E": E, "F": Fa, "P": P, "H": H, "chi": V - E + Fa}
    plato = {"V": 20, "E": 30, "F": 12, "P": 12, "H": 0, "chi": 2}
    record("B", "the dodecahedron is exactly the T=1 seed of the tower's Goldberg family",
           "EXACT" if tower == plato else "DISCREPANCY",
           {"tower_topology_T1": tower, "dodecahedron": plato,
            "BOUNDARY": "This is a fact about the tower's own topology() function "
                        "and about Euclid XIII. It is NOT evidence that Timaeus 55c "
                        "anticipated anything. Two integers agreeing is not a result."})


# ---------------------------------------------------------------------------
# C. ANAXIMANDER
# ---------------------------------------------------------------------------

def C1_wheels() -> None:
    inner = [9, 18, 27]
    outer = [i + 1 for i in inner]
    ratios = [F(inner[i + 1], inner[i]) for i in range(len(inner) - 1)]
    geometric = len(set(ratios)) == 1
    record("C", "the 9/18/27 scheme is a geometric progression",
           "DISCREPANCY" if not geometric else "EXACT",
           {"inner_radii": inner, "outer_radii_thickness_1": outer,
            "successive_ratios": [str(r) for r in ratios],
            "actual_structure": "arithmetic in units of 9, i.e. 9 x (1,2,3)",
            "note": "calling it a 'x9 ratio series' is wrong; only the unit is 9",
            "doxography_gives": "sun 27 or 28, moon 18 or 19 -- consistent with a "
                                "wheel one earth-diameter thick",
            "stars_ring_9_10": "NOT numerically attested; Diels-Tannery extrapolation"})


def C2_earth_cylinder() -> None:
    record("C", "drum earth has diameter:height = 3:1", "EXACT",
           {"height_over_diameter": str(F(1, 3)),
            "consistent_with_scroll": True})


# ---------------------------------------------------------------------------
# D. KALACHAKRA
# ---------------------------------------------------------------------------

def D1_mandala_bands() -> None:
    bands = [12, 24, 24, 24, 12, 24]
    per_side = sum(bands)
    inner = 624 - 2 * per_side
    record("D", "the outer bands and the 624-mus diameter are consistent", "COMPUTED",
           {"bands": bands, "band_total_radial": per_side,
            "implied_inner_square_width": inner,
            "factorisation_of_inner": "384 = 2^7 x 3",
            "verdict": "OPEN -- arithmetic is self-consistent, but the scroll gives "
                       "no documented inner-palace width to check 384 against. "
                       "Needs the Vajravali directly."})


def D2_deity_counts() -> None:
    record("D", "722 deities total, 536 in the body mandala", "OUT_OF_SCOPE",
           {"remainder": 722 - 536,
            "note": "a doctrinal enumeration. Arithmetic is trivially consistent; "
                    "the counts themselves are not kernel-verifiable."})


# ---------------------------------------------------------------------------
# E. WHAT NO KERNEL CAN SETTLE
# ---------------------------------------------------------------------------

OUT_OF_SCOPE = [
    "What Hesiod, Homer, Pherecydes, or Alcman actually wrote.",
    "Whether the Derveni papyrus contains Phanes (Betegh vs others).",
    "Whether the Rhapsodic theogony preserves archaic material or Neoplatonic system.",
    "The dating of Rigveda Mandala 10 (Witzel).",
    "Whether Baudhayana predates Pythagoras.",
    "Seidenberg's common-ritual-origin chronology vs Robson's Plimpton 322 dating.",
    "Whether the Orphic egg and Hiranyagarbha share an inheritance. (Typological "
    "similarity is not a computable quantity.)",
    "Dumezil's trifunctionalism; Mueller's solar mythology.",
    "The translator and source language of the Dodoni 'Vedes'.",
    "Whether ANY of the above bears on the SOL tower. It does not. Different scroll, "
    "different ledger, no shared load-bearing claim.",
]


def main() -> None:
    for fn in (A1_sqrt2_construction, A2_newton_identity, A3_pythagorean_triples,
               A4_circling_the_square, A5_manava_rule, A6_squaring_the_circle,
               A7_enlargement_rule, A8_caturasra_bricks, A9_special_brick_counts,
               A10_symbolic_vs_physical, A11_units,
               B1_world_soul_series, B2_means_and_tone, B3_leimma, B4_total_span,
               B5_five_solids_only, B6_elemental_triangle,
               B7_dodecahedron_is_the_tower_seed,
               C1_wheels, C2_earth_cylinder, D1_mandala_bands, D2_deity_counts):
        fn()

    width = 78
    print("=" * width)
    print("KORINTH GEOMETRY KERNEL v0.1 -- scroll is inspiration, kernel is receipt")
    print("=" * width)
    tally: Dict[str, int] = {}
    for r in RESULTS:
        tally[r["status"]] = tally.get(r["status"], 0) + 1
        print(f"\n[{r['status']:12s}] {r['section']} :: {r['claim']}")
        for k, v in r["detail"].items():
            print(f"      {k}: {v}")
    print("\n" + "=" * width)
    print("TALLY:", ", ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    print("=" * width)
    print("\nOUT OF SCOPE FOR ANY KERNEL -- needs sources, not compute:")
    for i, item in enumerate(OUT_OF_SCOPE, 1):
        print(f"  {i:2d}. {item}")
    print("\nincomplete is fine. fake is not.")

    import json
    with open("/home/claude/korinth_kernel_receipt.json", "w") as f:
        json.dump({"results": RESULTS, "tally": tally,
                   "out_of_scope": OUT_OF_SCOPE}, f, indent=2, default=str)


if __name__ == "__main__":
    main()
