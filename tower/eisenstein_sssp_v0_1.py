# EISENSTEIN_SSSP v0.1 -- the topology-first shortest-path experiment.
#
# The claim under test (HYPOTHESIS, owes the price):
#   On the flat Eisenstein lattice Z[zeta], zeta = e^{i pi/3}, the bounded
#   frontier of SSSP is a NORM-SHELL { z : b <= N(z) < B } with N(k,l)=k^2+kl+l^2,
#   so the shortest-path search is replaced by a lookup on a STORED structure.
#   The tradeoff: pay storage once, buy time on every later calculation.
#   (calculus: invented once, used forever -- not rediscovered per integral.)
#
# Three distances are measured side by side and kept apart:
#   (a) HOP   -- true graph shortest path on the triangular lattice (BFS/Dijkstra)
#   (b) NORM  -- the Eisenstein norm N(dk,dl) = dk^2+dk*dl+dl^2 (Euclidean^2)
#   (c) SHELL -- the norm-shell lookup on the stored net (the symbiosis lane)
#
# Exact integer arithmetic only in the core. No floats in the math.
# ASCII-only source (Curse 2). One script, one run, one receipt (Curse 19).

import json
import time
from collections import deque

# ----------------------------------------------------------------------------
# The lattice: axial coords (k, l) for z = k + l*zeta, zeta^2 = zeta - 1.
# Six unit steps on the triangular lattice (the hex grid of the hexagons).
# ----------------------------------------------------------------------------
ZETA_STEPS = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]


def norm(dk, dl):
    """Eisenstein norm N(dk,dl) = dk^2 + dk*dl + dl^2. Exact integer. EXACT."""
    return dk * dk + dk * dl + dl * dl


def hop_distance(dk, dl):
    """True graph distance (number of edges) on the triangular lattice from
    (0,0) to (dk,dl). Closed form: max(|dk|,|dl|,|dk+dl|). EXACT (integer)."""
    return max(abs(dk), abs(dl), abs(dk + dl))


def bfs_hop(target_dk, target_dl):
    """Independent check of hop_distance by real BFS over the lattice graph.
    This is the 'from scratch' Dijkstra (unit weights => BFS). COMPUTED."""
    target = (target_dk, target_dl)
    if target == (0, 0):
        return 0
    seen = {(0, 0): 0}
    dq = deque([(0, 0)])
    while dq:
        k, l = dq.popleft()
        d = seen[(k, l)]
        for sk, sl in ZETA_STEPS:
            nk, nl = k + sk, l + sl
            if (nk, nl) == target:
                return d + 1
            if (nk, nl) not in seen:
                seen[(nk, nl)] = d + 1
                dq.append((nk, nl))
    return -1  # unreachable (never happens on a connected lattice)


# ----------------------------------------------------------------------------
# PART 1 -- the divergence map: NORM vs HOP on a disk of lattice points.
# Where does the algebraic norm agree with the graph distance, where not?
# ----------------------------------------------------------------------------
def divergence_map(radius):
    """Scan all (k,l) with hop <= radius. Compare norm(k,l) to hop(k,l).
    Returns agreement stats. The norm is Euclidean^2; hop is Manhattan-on-hex.
    They CANNOT be equal pointwise (different geometries) -- the question is
    whether the norm ORDERS the points the same way hop does (the frontier)."""
    rows = []
    for k in range(-radius, radius + 1):
        for l in range(-radius, radius + 1):
            h = hop_distance(k, l)
            if h > radius:
                continue
            rows.append((k, l, h, norm(k, l)))
    return rows


def frontier_order_check(rows):
    """The SSSP frontier is an ORDER: process nearer vertices before farther.
    Test: does sorting by NORM give the same 'expand outward' containment as
    sorting by HOP? i.e. is every norm-ball a union of whole hop-shells?
    Report the largest radius where the norm-ball is hop-shell-aligned."""
    # group by hop shell and by norm value
    max_hop = max(r[2] for r in rows)
    # for each hop shell, the set of norms present
    shell_norms = {}
    for k, l, h, n in rows:
        shell_norms.setdefault(h, set()).add(n)
    # A norm threshold B selects a hop-shell-aligned region iff there is no
    # overlap interleaving: max norm in shell h <= min norm in shell h+1 would
    # be ideal (perfect nesting). Measure the nesting defect.
    nesting = []
    for h in range(max_hop):
        lo = shell_norms.get(h, set())
        hi = shell_norms.get(h + 1, set())
        if lo and hi:
            nesting.append((h, max(lo), min(hi), max(lo) <= min(hi)))
    return nesting


# ----------------------------------------------------------------------------
# PART 2 -- the symbiosis: store the net once, then ride it.
# We precompute a norm-indexed shell table (the STORED CALCULUS), then time a
# random BIG calculation (many SSSP-like frontier queries) two ways:
#   FROM SCRATCH : BFS each query (rediscover the wheel)
#   ON THE NET   : norm-shell lookup on the stored table (use calculus)
# ----------------------------------------------------------------------------
def build_stored_net(radius):
    """Pay the one-time storage cost: index every lattice point by its norm.
    Returns dict norm -> list of (k,l). This is the 'invent calculus' step."""
    t0 = time.perf_counter()
    table = {}
    for k in range(-radius, radius + 1):
        for l in range(-radius, radius + 1):
            if hop_distance(k, l) <= radius:
                table.setdefault(norm(k, l), []).append((k, l))
    build_s = time.perf_counter() - t0
    return table, build_s


def shell_lookup(table, b, B):
    """The bounded frontier as a norm-shell: all points with b <= N < B.
    This is the BMSSP frontier as a LOOKUP. O(shell size), no search."""
    out = []
    for n, pts in table.items():
        if b <= n < B:
            out.extend(pts)
    return out


def symbiosis_race(radius, n_queries, seed=12345):
    """Time a random big calculation both ways. The 'big calculation' is a batch
    of frontier queries: for random shells [b,B), gather the frontier points.
    FROM SCRATCH recomputes the lattice walk each time; ON THE NET uses the
    stored norm table. The point: storage paid once, time bought forever."""
    import random
    rnd = random.Random(seed)
    maxn = norm(radius, 0)

    # one-time storage cost (the calculus invention)
    table, build_s = build_stored_net(radius)

    queries = []
    for _ in range(n_queries):
        a = rnd.randint(0, maxn)
        b = rnd.randint(0, maxn)
        lo, hi = min(a, b), max(a, b)
        if hi == lo:
            hi = lo + 1
        queries.append((lo, hi))

    # ON THE NET: ride the stored structure
    t0 = time.perf_counter()
    net_total = 0
    for lo, hi in queries:
        net_total += len(shell_lookup(table, lo, hi))
    net_s = time.perf_counter() - t0

    # FROM SCRATCH: rebuild the lattice region each query (rediscover)
    t0 = time.perf_counter()
    scratch_total = 0
    for lo, hi in queries:
        cnt = 0
        for k in range(-radius, radius + 1):
            for l in range(-radius, radius + 1):
                if hop_distance(k, l) <= radius and lo <= norm(k, l) < hi:
                    cnt += 1
        scratch_total += cnt
    scratch_s = time.perf_counter() - t0

    return {
        "radius": radius,
        "stored_points": sum(len(v) for v in table.values()),
        "distinct_norms": len(table),
        "build_once_s": round(build_s, 6),
        "n_queries": n_queries,
        "on_the_net_s": round(net_s, 6),
        "from_scratch_s": round(scratch_s, 6),
        "speedup_x": round(scratch_s / net_s, 2) if net_s > 0 else None,
        "answers_match": net_total == scratch_total,
        "frontier_points_total": net_total,
    }


# ----------------------------------------------------------------------------
# PART 3 -- verify the hop closed form against real BFS (independent lane).
# ----------------------------------------------------------------------------
def verify_hop_vs_bfs(radius):
    bad = []
    checked = 0
    for k in range(-radius, radius + 1):
        for l in range(-radius, radius + 1):
            if hop_distance(k, l) > radius:
                continue
            h_closed = hop_distance(k, l)
            h_bfs = bfs_hop(k, l)
            checked += 1
            if h_closed != h_bfs:
                bad.append((k, l, h_closed, h_bfs))
    return checked, bad


def main():
    receipt = {"experiment": "EISENSTEIN_SSSP v0.1", "labels": {}}

    # PART 3 first (cheap): is the hop closed form even right?
    checked, bad = verify_hop_vs_bfs(6)
    receipt["hop_closed_form"] = {
        "points_checked": checked,
        "mismatches": len(bad),
        "verdict": "EXACT (closed form == BFS)" if not bad else "FAILS",
        "examples": bad[:5],
    }

    # PART 1: divergence / nesting map
    rows = divergence_map(12)
    nesting = frontier_order_check(rows)
    aligned = sum(1 for r in nesting if r[3])
    receipt["norm_vs_hop_frontier"] = {
        "radius": 12,
        "lattice_points": len(rows),
        "hop_shells": len(nesting) + 1,
        "shells_where_norm_nests_cleanly": aligned,
        "shells_where_norm_interleaves": len(nesting) - aligned,
        "reading": (
            "norm is Euclidean^2, hop is hex-Manhattan; they do NOT coincide "
            "pointwise. The question is whether norm-ball == union of hop-shells."
        ),
        "nesting_table_head": nesting[:8],
    }

    # PART 2: the symbiosis race -- store once, ride forever
    receipt["symbiosis"] = symbiosis_race(radius=40, n_queries=400)
    receipt["symbiosis_small"] = symbiosis_race(radius=20, n_queries=200)

    receipt["labels"] = {
        "hop_closed_form": "EXACT if it matches BFS",
        "norm_vs_hop": "EXACT arithmetic; the INTERPRETATION is DESIGN/HYPOTHESIS",
        "symbiosis": "COMPUTED (wall-clock on this machine, this run)",
        "the_claim": "HYPOTHESIS -- storage-for-time symbiosis, owes the price",
    }

    txt = json.dumps(receipt, indent=2)
    with open("eisenstein_sssp_v0_1_receipt.json", "w", encoding="utf-8") as f:
        f.write(txt)
    print(txt)


if __name__ == "__main__":
    main()
