# SHELL7 v0.1 -- WHERE and WHY does the norm stop nesting inside the hop shells?
#
# The first experiment found: shells 0..6 nest cleanly, shell 7 interleaves.
# Suspect: the hop-shell is a HEXAGON (hex-Manhattan sphere), the norm-ball is
# an ELLIPSE (Euclidean sphere in (k,l) coords). They diverge when the hexagon
# corner overtakes the circle. Is the break radius EXACT? Let us look.
#
# Exact integer arithmetic. ASCII-only. One run, one receipt.

import json

ZETA_STEPS = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]


def norm(dk, dl):
    return dk * dk + dk * dl + dl * dl


def hop(dk, dl):
    return max(abs(dk), abs(dl), abs(dk + dl))


def shell_points(h):
    """All (k,l) at exact hop-distance h: the hexagon ring of radius h."""
    out = []
    R = h + 1
    for k in range(-R, R + 1):
        for l in range(-R, R + 1):
            if hop(k, l) == h:
                out.append((k, l))
    return out


def analyze(max_h):
    """For each shell: the norm range on the hexagon ring, and whether the
    whole ring sits strictly below the next ring's min norm (clean nesting)."""
    rows = []
    prev_max = -1
    for h in range(0, max_h + 1):
        pts = shell_points(h)
        norms = [norm(k, l) for k, l in pts]
        lo, hi = min(norms), max(norms)
        # the corners of the hex ring are at (h,0),(0,h),(-h,h) and mirrors:
        # norm(h,0)=h^2. The EDGE MIDPOINTS are at (h,-h//2)-ish: smaller norm.
        corner = norm(h, 0)          # a hexagon corner: (h,0) -> h^2
        rows.append({
            "shell": h,
            "ring_size": len(pts),       # should be 6h for h>=1
            "norm_min": lo,
            "norm_max": hi,
            "corner_norm_h2": corner,    # the corner sits at norm h^2
            "nests_below_next": None,    # filled after
        })
    for i in range(len(rows) - 1):
        rows[i]["nests_below_next"] = rows[i]["norm_max"] < rows[i + 1]["norm_min"]
    return rows


def corner_vs_edge(h):
    """The geometry of the break. On ring h:
      corner  = (h,0)         norm = h^2
      edge    = the flattest point, near (h, -h/2) i.e. (ceil(h/2), -h+... )
    The hex ring has 6 corners at norm h^2 and 6 edge-midpoints at the min norm.
    The NEXT ring's corners are at norm (h+1)^2. Nesting breaks when this
    ring's corner norm >= next ring's edge-midpoint min norm."""
    pts = shell_points(h)
    by_norm = sorted(pts, key=lambda p: norm(*p))
    lo_pt, hi_pt = by_norm[0], by_norm[-1]
    return {
        "shell": h,
        "min_norm_point": lo_pt, "min_norm": norm(*lo_pt),
        "max_norm_point": hi_pt, "max_norm": norm(*hi_pt),
        "h2": h * h, "hp1_2": (h + 1) * (h + 1),
    }


def first_breaks(limit):
    """Find every shell where nesting fails, up to limit. Is it only 7?"""
    rows = analyze(limit)
    return [r["shell"] for r in rows if r["nests_below_next"] is False]


def main():
    receipt = {"experiment": "SHELL7 v0.1 -- where the hexagon overtakes the circle"}

    # ring sizes are 6h (hex number) -- verify
    receipt["ring_sizes"] = [
        {"h": h, "size": len(shell_points(h)), "6h": 6 * h}
        for h in range(1, 8)
    ]

    # the nesting table
    receipt["nesting"] = analyze(14)

    # the geometry of the break at shell 7 and around it
    receipt["break_geometry"] = [corner_vs_edge(h) for h in (5, 6, 7, 8, 9)]

    # is shell 7 the ONLY early break, or the first of many?
    receipt["all_breaks_up_to_30"] = first_breaks(30)

    # THE EXACT QUESTION: nesting holds iff max norm on ring h < min norm on ring h+1.
    # corner norm on ring h is h^2 (at (h,0)). min norm on ring h+1 is at the
    # edge midpoint. For the triangular lattice the edge midpoint of ring r is
    # near (r, -r/2): norm ~ (3/4) r^2. So nesting needs h^2 < (3/4)(h+1)^2,
    # i.e. 2h < sqrt(3)(h+1), i.e. h(2-sqrt3) < sqrt3, i.e. h < sqrt3/(2-sqrt3).
    # sqrt3/(2-sqrt3) = sqrt3(2+sqrt3)/(4-3) = 2sqrt3+3 ~ 6.464. So h<=6 nests,
    # h=7 breaks. EXACT: the break is at h=7 because 2sqrt3+3 ~ 6.464 < 7.
    receipt["exact_threshold"] = {
        "claim": "nesting holds iff h^2 < min_norm(ring h+1)",
        "corner_norm_ring_h": "h^2",
        "min_norm_ring_r_approx": "(3/4) r^2  (edge midpoint of the hexagon)",
        "inequality": "h^2 < (3/4)(h+1)^2  =>  h < 2*sqrt3+3 ~ 6.464",
        "threshold_exact": "2*sqrt(3)+3",
        "threshold_decimal": 2 * 1.7320508075688772 + 3,
        "prediction": "shells h<=6 nest, shell h=7 is the first break",
        "status": "EXACT (algebra) -- to be checked against the integer scan",
    }

    txt = json.dumps(receipt, indent=2)
    with open("shell7_v0_1_receipt.json", "w", encoding="utf-8") as f:
        f.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
