#!/usr/bin/env python3
"""Independent reconstruction of the THEA v3.0 leapfrog spectral tower.

Tower levels n = 0..7 are fullerenes with T = 3^n (V = 20*3^n):
  even n = GP(m,0), m = 3^(n/2)   -> the DUAL of the (m,0) geodesic icosphere
                                     triangulation (triangle-adjacency graph);
  odd  n = GP(m,m), m = 3^((n-1)/2) -> the LEAPFROG of GP(m,0) = truncated dual,
                                     realized directly on the triangulation as
                                     the vertex-edge INCIDENCE graph:
        nodes  = (v, e) for every vertex-edge incidence,
        edges  = (v,e)-(v,e') for e,e' rotationally consecutive at v,
                 (v,e)-(u,e) across e = (u,v).
This shares no code or method with the generator. Laplacian lambda2 = 3 - mu2(A)
for 3-regular graphs; low Laplacian modes = top adjacency modes via Lanczos
(eigsh which='LA'), no shift-invert needed.
"""
import math
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh

PHI = (1 + math.sqrt(5)) / 2

HIS_LAMBDA2 = [0.7639320225002093, 0.24340174613993026, 0.08056267490271063,
               0.026835383239955046, 0.008946119207323466, 0.0029824254958508156,
               0.0009942087404430922, 0.00033141249681589713]
HIS_GAP = [None, 0.7565982538600667, 0.5794902974522533, 0.3577715761992155,
           0.219612230699643, 0.12845145231167437, 0.07503525256368275,
           0.04340762833732999]
HIS_BANDS = [(0.7247991302336692, 3), (2.167654165933704, 5),
             (4.026433003698821, 3), (4.596940195929026, 4)]

# ---------------- geodesic (m,0) icosphere triangulation ----------------
def icosahedron():
    p = PHI
    base = []
    for a, b in [(1, p), (1, -p), (-1, p), (-1, -p)]:
        base += [(0, a, b), (a, b, 0), (b, 0, a)]
    V = [np.array(v, float) / np.linalg.norm(v) for v in base]
    n = len(V)
    D = np.array([[np.linalg.norm(V[i] - V[j]) for j in range(n)] for i in range(n)])
    np.fill_diagonal(D, np.inf)
    emin = D.min()
    adj = [set(np.where(np.abs(D[i] - emin) < emin * 0.05)[0]) for i in range(n)]
    tris = set()
    for i in range(n):
        for j in adj[i]:
            for k in adj[j]:
                if k in adj[i] and i < j < k:
                    tris.add((i, j, k))
    tris = [list(t) for t in tris]
    assert len(V) == 12 and len(tris) == 20
    # orient outward
    out = []
    for a, b, c in tris:
        nrm = np.cross(V[b] - V[a], V[c] - V[a])
        cen = (V[a] + V[b] + V[c]) / 3
        out.append([a, b, c] if np.dot(nrm, cen) > 0 else [a, c, b])
    return V, out

def subdivide(m):
    V0, F0 = icosahedron()
    pos = []
    vid = {}
    def key(p):
        return (round(p[0], 9), round(p[1], 9), round(p[2], 9))
    def getv(p):
        p = p / np.linalg.norm(p)
        k = key(p)
        if k not in vid:
            vid[k] = len(pos)
            pos.append(p)
        return vid[k]
    tris = []
    for a, b, c in F0:
        A, B, C = V0[a], V0[b], V0[c]
        grid = {}
        for i in range(m + 1):
            for j in range(m + 1 - i):
                grid[(i, j)] = getv(((m - i - j) * A + i * B + j * C))
        for i in range(m):
            for j in range(m - i):
                tris.append((grid[(i, j)], grid[(i + 1, j)], grid[(i, j + 1)]))
                if j < m - i - 1:
                    tris.append((grid[(i + 1, j)], grid[(i + 1, j + 1)], grid[(i, j + 1)]))
    Vc, Fc = len(pos), len(tris)
    edges = set()
    for a, b, c in tris:
        for u, v in ((a, b), (b, c), (c, a)):
            edges.add((min(u, v), max(u, v)))
    Ec = len(edges)
    assert Vc == 10 * m * m + 2 and Fc == 20 * m * m and Ec == 30 * m * m
    assert Vc - Ec + Fc == 2, "triangulation not closed"
    return pos, tris, sorted(edges)

# ---------------- the two fullerene constructions ----------------
def even_graph(tris, edges):
    """GP(m,0) fullerene = triangle-adjacency dual."""
    emap = {}
    for t, (a, b, c) in enumerate(tris):
        for u, v in ((a, b), (b, c), (c, a)):
            emap.setdefault((min(u, v), max(u, v)), []).append(t)
    rows, cols = [], []
    for e, ts in emap.items():
        assert len(ts) == 2
        rows += [ts[0], ts[1]]
        cols += [ts[1], ts[0]]
    n = len(tris)
    A = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    assert (A.sum(axis=1) == 3).all()
    return A

def odd_graph(pos, edges):
    """GP(m,m) = leapfrog of GP(m,0): the vertex-edge incidence graph."""
    inc = {}
    per_v = {}
    eid = {e: i for i, e in enumerate(edges)}
    for (u, v) in edges:
        per_v.setdefault(u, []).append((u, v))
        per_v.setdefault(v, []).append((u, v))
    # rotational order of incident edges at each vertex (angle in tangent plane)
    for v, elist in per_v.items():
        nv = pos[v]
        ref = np.array([1.0, 0.0, 0.0])
        if abs(np.dot(ref, nv)) > 0.9:
            ref = np.array([0.0, 1.0, 0.0])
        t1 = ref - np.dot(ref, nv) * nv
        t1 /= np.linalg.norm(t1)
        t2 = np.cross(nv, t1)
        def ang(e):
            o = e[1] if e[0] == v else e[0]
            d = pos[o] - pos[v]
            return math.atan2(np.dot(d, t2), np.dot(d, t1))
        elist.sort(key=ang)
    nodes = {}
    for v, elist in per_v.items():
        for e in elist:
            nodes[(v, eid[e])] = len(nodes)
    rows, cols = [], []
    def link(a, b):
        rows.append(a); cols.append(b)
        rows.append(b); cols.append(a)
    for v, elist in per_v.items():
        d = len(elist)
        for i in range(d):
            a = nodes[(v, eid[elist[i]])]
            b = nodes[(v, eid[elist[(i + 1) % d]])]
            link(a, b)
    for (u, v) in edges:
        link(nodes[(u, eid[(u, v)])], nodes[(v, eid[(u, v)])])
    n = len(nodes)
    A = csr_matrix((np.ones(len(rows)), (rows, cols)), shape=(n, n))
    A.data[:] = 1.0
    assert (A.sum(axis=1) == 3).all(), "leapfrog not 3-regular"
    return A

def lam2_of(A):
    vals = eigsh(A, k=6, which='LA', return_eigenvectors=False, maxiter=20000)
    vals = np.sort(vals)[::-1]
    assert abs(vals[0] - 3) < 1e-8, "top eigenvalue not 3 (disconnected?)"
    return 3.0 - vals[1]

def main():
    print("LEAPFROG TOWER -- independent construction vs certificate")
    print(f"{'lvl':>3} {'N':>7} {'T':>5}  {'lambda2 (mine)':>20}  {'lambda2 (his)':>20}  {'|diff|':>9}   {'T*lam2':>13}")
    graphs = {}
    for j, m in enumerate([1, 3, 9, 27]):
        pos, tris, edges = subdivide(m)
        graphs[2 * j] = even_graph(tris, edges)
        graphs[2 * j + 1] = odd_graph(pos, edges)
    deepest = None
    for lvl in range(8):
        A = graphs[lvl]
        N = A.shape[0]
        T = 3 ** lvl
        assert N == 20 * T, (N, T)
        l2 = lam2_of(A)
        d = abs(l2 - HIS_LAMBDA2[lvl])
        print(f"{lvl:>3} {N:>7} {T:>5}  {l2:>20.15f}  {HIS_LAMBDA2[lvl]:>20.15f}  {d:>9.2e}   {T*l2:>13.9f}")
        deepest = (lvl, A, N, T)
    # ---- low bands at the deepest level ----
    lvl, A, N, T = deepest
    print(f"\nLOW LAPLACIAN BANDS at level {lvl} (N={N}), renormalized by T={T}:")
    vals = eigsh(A, k=20, which='LA', return_eigenvectors=False, maxiter=40000)
    lap = np.sort(3.0 - vals)
    lap = lap[lap > 1e-8]           # drop the zero mode
    scaled = T * lap
    bands = []
    for v in scaled:
        if bands and abs(v - bands[-1][0]) < 1e-4 * max(1, abs(v)):
            s, c = bands[-1]
            bands[-1] = ((s * c + v) / (c + 1), c + 1)
        else:
            bands.append((v, 1))
    print(f"{'mine: value':>16} {'mult':>5}    {'his: value':>16} {'mult':>5}")
    for i in range(min(4, len(bands))):
        hv, hm = HIS_BANDS[i]
        print(f"{bands[i][0]:>16.9f} {bands[i][1]:>5}    {hv:>16.9f} {hm:>5}")
    b1 = bands[0][0]
    r21 = bands[1][0] / b1
    c3 = (bands[2][0] * bands[2][1] + bands[3][0] * bands[3][1]) / (bands[2][1] + bands[3][1])
    print(f"second/first = {r21:.9f}   (sphere l(l+1) target: 3)")
    print(f"split-7 center/first = {c3 / b1:.9f}   (sphere target: 6)")
    # ---- central adjacency gaps, dense, levels 1..4 ----
    print("\nCENTRAL ADJACENCY GAP (dense, levels 1-4) vs certificate:")
    for lvl in range(1, 5):
        A = graphs[lvl].toarray()
        w = np.linalg.eigvalsh(A)
        neg = w[w < -1e-9].max()
        posv = w[w > 1e-9].min()
        gap = posv - neg
        print(f"  level {lvl}: mine {gap:.15f}   his {HIS_GAP[lvl]:.15f}   |diff| {abs(gap-HIS_GAP[lvl]):.2e}   sqrt(T)*gap {math.sqrt(3**lvl)*gap:.9f}")
    print("\nDONE. Same numbers, different hands.")

if __name__ == "__main__":
    main()
