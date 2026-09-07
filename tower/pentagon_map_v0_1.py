# PENTAGON_MAP v0.1 -- Door 1. The Fable mage's hypothesis, put to the kernel.
#
# HYPOTHESIS (the mage's own grammar, owes the receipt):
#   Adjacent pentagon centers on GP(k,l) sit at hop distance
#       d = max(|k|,|l|,|k+l|)
#   in the flat chart, so the exact-lookup zone (the 2*sqrt3+3 wall, nesting
#   radius 6) and the defect charge first collide precisely when that max
#   crosses 7. And (4,3) on the golden lane (T=37) would be the first chiral
#   cage to break it.
#
# This script builds each Goldberg (k,l) fullerene with the certified kernel
# (goldberg_gc.py), finds the 12 pentagons, builds the DUAL adjacency (faces
# sharing an edge), and measures the TRUE hop distance between every pair of
# adjacent pentagon centers by BFS on the dual graph. Then it compares the
# measured distance to the mage's closed form max(|k|,|l|,|k+l|).
#
# One script, one run, one receipt. Exact combinatorics, float only for coords.

import json
from collections import deque
import goldberg_gc as gc


def dual_adjacency(faces):
    """Dual graph: node = fullerene face; edge between faces sharing a primal
    edge (i.e. sharing two consecutive primal vertices). Two faces are adjacent
    iff their rings share an edge = two vertices that are consecutive in both."""
    # map each primal edge (pair of fvert indices) to the faces containing it
    edge_to_faces = {}
    for fi, ring in enumerate(faces):
        m = len(ring)
        for i in range(m):
            a, b = ring[i], ring[(i + 1) % m]
            e = (min(a, b), max(a, b))
            edge_to_faces.setdefault(e, []).append(fi)
    adj = {fi: set() for fi in range(len(faces))}
    for e, fl in edge_to_faces.items():
        for i in range(len(fl)):
            for j in range(i + 1, len(fl)):
                adj[fl[i]].add(fl[j])
                adj[fl[j]].add(fl[i])
    return adj


def bfs_dist(adj, s, t):
    if s == t:
        return 0
    seen = {s: 0}
    dq = deque([s])
    while dq:
        u = dq.popleft()
        for w in adj[u]:
            if w == t:
                return seen[u] + 1
            if w not in seen:
                seen[w] = seen[u] + 1
                dq.append(w)
    return -1


def pentagon_map(k, l):
    """Build GP(k,l), find the 12 pentagons, measure all pairwise hop distances
    between pentagon centers on the dual graph. Return stats."""
    fverts, faces, T = gc.build_fullerene(k, l)
    inv = gc.invariants(fverts, faces)
    assert inv["P"] == 12 and inv["chi"] == 2, "kernel refused: not a certified shell"
    pent = [fi for fi, ring in enumerate(faces) if len(ring) == 5]
    adj = dual_adjacency(faces)

    # pairwise distances among the 12 pentagons
    dists = []
    for i in range(len(pent)):
        for j in range(i + 1, len(pent)):
            dists.append(bfs_dist(adj, pent[i], pent[j]))
    dmin = min(dists)
    dmax = max(dists)
    # the ADJACENT pentagon distance = the minimum pairwise distance (nearest
    # pentagon neighbours on the icosa vertex graph)
    mage_closed = max(abs(k), abs(l), abs(k + l))
    return {
        "k": k, "l": l, "T": T,
        "V": inv["V"], "P": inv["P"],
        "pentagon_pair_dist_min": dmin,
        "pentagon_pair_dist_max": dmax,
        "distinct_pair_dists": sorted(set(dists)),
        "mage_closed_form_max": mage_closed,
        "matches_min": (dmin == mage_closed),
        "inside_wall": (dmin <= 6),   # 2*sqrt3+3 ~ 6.464 -> nesting radius 6
    }


def main():
    # the golden lane (Fibonacci pairs) + the achiral anchors + the mage's (4,3)
    lanes = [
        ("anchor C20", (1, 0)),
        ("anchor C60", (1, 1)),
        ("golden n=2", (2, 1)),
        ("golden n=3", (3, 2)),
        ("golden n=4", (5, 3)),
        ("golden n=5", (8, 5)),
        ("mage (4,3)", (4, 3)),
        ("off-lane (3,1)", (3, 1)),
        ("off-lane (4,1)", (4, 1)),
        ("off-lane (5,2)", (5, 2)),
    ]
    rows = []
    for name, (k, l) in lanes:
        r = pentagon_map(k, l)
        r["lane"] = name
        rows.append(r)

    receipt = {
        "experiment": "PENTAGON_MAP v0.1 -- Door 1, the mage's hypothesis",
        "hypothesis": "adjacent pentagon hop distance = max(|k|,|l|,|k+l|); "
                      "defect charge first collides with the nesting radius (6) "
                      "when that max crosses 7; (4,3) T=37 first chiral breaker",
        "wall_nesting_radius": 6,
        "wall_exact": "2*sqrt(3)+3 = 6.464...",
        "results": rows,
    }

    # verdict on the mage's closed form
    matches = sum(1 for r in rows if r["matches_min"])
    receipt["closed_form_verdict"] = {
        "shells_tested": len(rows),
        "shells_where_max_equals_measured_min": matches,
        "note": "if matches < tested, the closed form is NOT the adjacent "
                "pentagon distance -- read the measured min instead",
    }

    txt = json.dumps(receipt, indent=2)
    with open("pentagon_map_v0_1_receipt.json", "w", encoding="utf-8") as f:
        f.write(txt)
    # human summary
    print("PENTAGON MAP -- Door 1 receipt")
    print("lane           (k,l)    T     V    P  dmin dmax  mage_max  match  inside_wall")
    for r in rows:
        print("%-14s (%2d,%2d) %4d %5d %3d  %4d %4d  %8d  %-5s  %s" % (
            r["lane"], r["k"], r["l"], r["T"], r["V"], r["P"],
            r["pentagon_pair_dist_min"], r["pentagon_pair_dist_max"],
            r["mage_closed_form_max"], r["matches_min"], r["inside_wall"]))
    print("\nclosed form matches on %d/%d shells" % (matches, len(rows)))
    print("distinct pair distances per shell:")
    for r in rows:
        print("  %-14s (%d,%d): %s" % (r["lane"], r["k"], r["l"], r["distinct_pair_dists"]))


if __name__ == "__main__":
    main()
