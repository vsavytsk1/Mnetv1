#!/usr/bin/env python3
"""
goldberg_gc.py -- the Goldberg-Coxeter (k,l) fullerene mesh generator + verifier.
KERNELIC_MAGIC compliant: ASCII-only source, stdlib only (math), one job.

Thea Lane B (certified closure), made geometric. For each (k,l) we:
  1. take the icosahedron (12 verts, 20 outward triangles),
  2. Goldberg-Coxeter subdivide every triangle on the triangular lattice
     (master triangle L0=(0,0), L1=(k,l), L2=(-l,k+l) -- rotate 60 deg),
     mapping each interior lattice point back by barycentric coords -> sphere,
  3. weld shared edges/corners by rounding 3D coords (both faces parametrize a
     shared edge identically, so the weld is exact),
  4. take the DUAL: fullerene vertex = triangle centroid on the sphere; fullerene
     face = the ordered ring of triangles around each geodesic vertex
     (5 around the 12 icosa corners -> pentagons, 6 elsewhere -> hexagons).

Proof by kernel (Path III): every shell must show V=20T, E=30T, F=10T+2, P=12,
chi=2, and degree(v)=3 for all v, or the builder REFUSES to bless it.

Run:
    py -3 goldberg_gc.py            # verify the golden 7 shells
    py -3 goldberg_gc.py --json 2 1 # emit one mesh (k=2,l=1) as JSON

spini. P=12. chi=2. The pentagons hold; the hexes pay.
"""
import math
import sys
import json

PHI = (1.0 + math.sqrt(5.0)) / 2.0

# The golden selector (Thea Part III): Fibonacci pairs (F_{n+1}, F_n).
GOLDEN = [(1, 0), (1, 1), (2, 1), (3, 2), (5, 3), (8, 5), (13, 8)]

# lattice basis: |i*eu + j*ev|^2 = i^2 + i*j + j^2  (the hexagonal norm T)
EU = (1.0, 0.0)
EV = (0.5, math.sqrt(3.0) / 2.0)


def _v(i, j):
    return (i * EU[0] + j * EV[0], i * EU[1] + j * EV[1])


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def bary2d(p, a, b, c):
    """Barycentric coords of 2D point p in triangle (a,b,c)."""
    v0, v1, v2 = _sub(b, a), _sub(c, a), _sub(p, a)
    d00, d01, d11 = _dot(v0, v0), _dot(v0, v1), _dot(v1, v1)
    d20, d21 = _dot(v2, v0), _dot(v2, v1)
    den = d00 * d11 - d01 * d01
    w1 = (d11 * d20 - d01 * d21) / den
    w2 = (d00 * d21 - d01 * d20) / den
    return (1.0 - w1 - w2, w1, w2)


def icosahedron():
    """12 unit vertices + 20 outward-oriented (CCW-from-outside) triangles."""
    p = PHI
    raw = [
        (-1, p, 0), (1, p, 0), (-1, -p, 0), (1, -p, 0),
        (0, -1, p), (0, 1, p), (0, -1, -p), (0, 1, -p),
        (p, 0, -1), (p, 0, 1), (-p, 0, -1), (-p, 0, 1),
    ]
    s = math.sqrt(1.0 + p * p)
    verts = [(x / s, y / s, z / s) for (x, y, z) in raw]
    faces = [
        (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
        (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
        (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
        (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
    ]
    # force every triangle outward (normal . centroid > 0)
    out = []
    for (a, b, c) in faces:
        va, vb, vc = verts[a], verts[b], verts[c]
        ux = (vb[0] - va[0], vb[1] - va[1], vb[2] - va[2])
        wx = (vc[0] - va[0], vc[1] - va[1], vc[2] - va[2])
        nx = (ux[1] * wx[2] - ux[2] * wx[1],
              ux[2] * wx[0] - ux[0] * wx[2],
              ux[0] * wx[1] - ux[1] * wx[0])
        cen = (va[0] + vb[0] + vc[0], va[1] + vb[1] + vc[1], va[2] + vb[2] + vc[2])
        out.append((a, b, c) if (nx[0] * cen[0] + nx[1] * cen[1] + nx[2] * cen[2]) > 0
                   else (a, c, b))
    return verts, out


def normalize(p, r=1.0):
    L = math.sqrt(p[0] * p[0] + p[1] * p[1] + p[2] * p[2])
    if L < 1e-15:
        return p
    return (p[0] * r / L, p[1] * r / L, p[2] * r / L)


def key3(p, q=1e6):
    return (round(p[0] * q), round(p[1] * q), round(p[2] * q))


def bary_int(i, j, k, l):
    """EXACT barycentric numerators (over T) of lattice point (i,j) in the master
    triangle M0=(0,0), M1=(k,l), M2=(-l,k+l). Affine-invariant, so we compute in
    integer (i,j) coords: all-integer, zero float error. Inside-or-on iff all >=0."""
    b1 = i * (k + l) + j * l        # area(M0, P, M2)
    b2 = k * j - l * i              # area(M0, M1, P)
    T = k * k + k * l + l * l
    b0 = T - b1 - b2
    return b0, b1, b2, T


def convex_hull(points):
    """Incremental 3D convex hull -> list of outward CCW triangles (index triples).
    Robust for points on a sphere (strictly convex, cospherical but not coplanar).
    O(n^2); fine up to a few thousand points for the offline verify/emit."""
    n = len(points)

    def sub(a, b):
        return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

    def cross(a, b):
        return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

    def dot(a, b):
        return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]

    # seed tetra: 4 non-coplanar points
    i0 = 0
    i1 = next((i for i in range(1, n)
               if dot(sub(points[i], points[i0]), sub(points[i], points[i0])) > 1e-12), None)
    i2 = None
    for i in range(1, n):
        if i == i1:
            continue
        cr = cross(sub(points[i1], points[i0]), sub(points[i], points[i0]))
        if dot(cr, cr) > 1e-16:
            i2 = i
            break
    nrm = cross(sub(points[i1], points[i0]), sub(points[i2], points[i0]))
    i3 = None
    for i in range(n):
        if i in (i0, i1, i2):
            continue
        if abs(dot(nrm, sub(points[i], points[i0]))) > 1e-9:
            i3 = i
            break

    def outward(tri):
        a, b, c = points[tri[0]], points[tri[1]], points[tri[2]]
        nx = cross(sub(b, a), sub(c, a))
        # centroid of the 4 seed points as interior reference
        return dot(nx, sub(cen4, a)) < 0

    cen4 = tuple(sum(points[t][d] for t in (i0, i1, i2, i3)) / 4.0 for d in range(3))
    faces = []
    for tri in ((i0, i1, i2), (i0, i1, i3), (i0, i2, i3), (i1, i2, i3)):
        a, b, c = points[tri[0]], points[tri[1]], points[tri[2]]
        nx = cross(sub(b, a), sub(c, a))
        faces.append(tri if dot(nx, sub(a, cen4)) > 0 else (tri[0], tri[2], tri[1]))

    def fnorm(f):
        a, b, c = points[f[0]], points[f[1]], points[f[2]]
        return cross(sub(b, a), sub(c, a)), a

    used = {i0, i1, i2, i3}
    for p in range(n):
        if p in used:
            continue
        vp = points[p]
        visible = []
        for fi, f in enumerate(faces):
            nx, a = fnorm(f)
            if dot(nx, sub(vp, a)) > 1e-12:
                visible.append(fi)
        if not visible:
            continue
        # horizon edges: edges on exactly one visible face
        edge_count = {}
        for fi in visible:
            f = faces[fi]
            for e in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
                edge_count[e] = edge_count.get(e, 0) + 1
        horizon = [e for e in edge_count if (e[1], e[0]) not in edge_count]
        vis = set(visible)
        faces = [f for fi, f in enumerate(faces) if fi not in vis]
        for (a, b) in horizon:
            faces.append((a, b, p))
        used.add(p)
    return faces


def build_geodesic(k, l, radius=1.6):
    """Return (gverts, gtris, T): geodesic sphere = GC-subdivided icosahedron.

    Robust for ALL (k,l), chiral (Class III) included. Per icosa face we map the
    lattice points inside-or-on the master triangle M0=(0,0),M1=(k,l),M2=(-l,k+l)
    to the sphere (exact integer barycentric -> boundary points weld byte-exact by
    rounded 3D key). The correct geodesic TRIANGULATION is then the convex hull of
    those cospherical points -- no per-face unit-triangle tiling, so the chiral
    boundary cut is a non-issue. Vertices number 10T+2 exactly."""
    ico_v, ico_f = icosahedron()
    T = k * k + k * l + l * l

    lo = -l - 2
    hi = k + l + 2

    def inside(i, j):
        b0, b1, b2, _ = bary_int(i, j, k, l)
        return b0 >= 0 and b1 >= 0 and b2 >= 0

    latpts = [(i, j) for i in range(lo, hi + 1) for j in range(lo, hi + 1) if inside(i, j)]

    gmap = {}
    gverts = []

    def gv(ij, face):
        b0, b1, b2, TT = bary_int(ij[0], ij[1], k, l)
        w0, w1, w2 = b0 / TT, b1 / TT, b2 / TT
        pa, pb, pc = ico_v[face[0]], ico_v[face[1]], ico_v[face[2]]
        p = (w0 * pa[0] + w1 * pb[0] + w2 * pc[0],
             w0 * pa[1] + w1 * pb[1] + w2 * pc[1],
             w0 * pa[2] + w1 * pb[2] + w2 * pc[2])
        p = normalize(p, radius)
        ky = key3(p)
        gi = gmap.get(ky)
        if gi is None:
            gi = len(gverts)
            gmap[ky] = gi
            gverts.append(p)
        return gi

    for face in ico_f:
        for ij in latpts:
            gv(ij, face)

    gtris = convex_hull(gverts)
    return gverts, gtris, T


def build_fullerene(k, l, radius=1.6):
    """Dual of the geodesic sphere -> the Goldberg (k,l) fullerene."""
    gverts, gtris, T = build_geodesic(k, l, radius)

    # fullerene vertex = centroid of each geodesic triangle, on the sphere
    fverts = []
    for (a, b, c) in gtris:
        pa, pb, pc = gverts[a], gverts[b], gverts[c]
        cen = ((pa[0] + pb[0] + pc[0]) / 3.0,
               (pa[1] + pb[1] + pc[1]) / 3.0,
               (pa[2] + pb[2] + pc[2]) / 3.0)
        fverts.append(normalize(cen, radius))

    # tris around each geodesic vertex -> one fullerene face
    around = [[] for _ in range(len(gverts))]
    for ti, (a, b, c) in enumerate(gtris):
        around[a].append(ti)
        around[b].append(ti)
        around[c].append(ti)

    faces = []
    for gvi, tlist in enumerate(around):
        if not tlist:
            continue
        n = gverts[gvi]
        # tangent frame at n
        ref = (1.0, 0.0, 0.0) if abs(n[0]) < 0.9 else (0.0, 1.0, 0.0)
        t = (n[1] * ref[2] - n[2] * ref[1],
             n[2] * ref[0] - n[0] * ref[2],
             n[0] * ref[1] - n[1] * ref[0])
        tl = math.sqrt(t[0]**2 + t[1]**2 + t[2]**2)
        t = (t[0] / tl, t[1] / tl, t[2] / tl)
        bt = (n[1] * t[2] - n[2] * t[1],
              n[2] * t[0] - n[0] * t[2],
              n[0] * t[1] - n[1] * t[0])

        def ang(ti):
            c = fverts[ti]
            d = (c[0] - n[0], c[1] - n[1], c[2] - n[2])
            return math.atan2(d[0] * bt[0] + d[1] * bt[1] + d[2] * bt[2],
                              d[0] * t[0] + d[1] * t[1] + d[2] * t[2])

        ring = sorted(tlist, key=ang)
        faces.append(ring)
    return fverts, faces, T


def invariants(fverts, faces):
    V = len(fverts)
    F = len(faces)
    edges = set()
    deg = [0] * V
    for ring in faces:
        m = len(ring)
        for i in range(m):
            a, b = ring[i], ring[(i + 1) % m]
            edges.add((min(a, b), max(a, b)))
    for (a, b) in edges:
        deg[a] += 1
        deg[b] += 1
    E = len(edges)
    P = sum(1 for r in faces if len(r) == 5)
    Hx = sum(1 for r in faces if len(r) == 6)
    other = sum(1 for r in faces if len(r) not in (5, 6))
    degset = sorted(set(deg))
    return dict(V=V, E=E, F=F, chi=V - E + F, P=P, H=Hx, other=other,
                degset=degset, alltriv=(degset == [3]))


def verify_all():
    print("GOLDBERG-COXETER golden catalogue -- proof by kernel")
    print("  n  (k,l)     T     V      E      F     P   H     chi  deg  VERDICT")
    ok_all = True
    for n, (k, l) in enumerate(GOLDEN):
        fv, fc, T = build_fullerene(k, l)
        inv = invariants(fv, fc)
        want = dict(V=20 * T, E=30 * T, F=10 * T + 2, P=12, chi=2)
        good = (inv["V"] == want["V"] and inv["E"] == want["E"] and
                inv["F"] == want["F"] and inv["P"] == 12 and inv["chi"] == 2 and
                inv["other"] == 0 and inv["alltriv"])
        ok_all = ok_all and good
        print("  %d  (%2d,%2d) %5d %6d %6d %6d %4d %5d %4d  %-4s %s" % (
            n, k, l, T, inv["V"], inv["E"], inv["F"], inv["P"], inv["H"],
            inv["chi"], str(inv["degset"]), "PASS" if good else "FAIL"))
    print("\nALL SHELLS: " + ("PASS -- Lane B certified." if ok_all else "FAIL"))
    return ok_all


def emit_json(k, l):
    fv, fc, T = build_fullerene(k, l)
    inv = invariants(fv, fc)
    print(json.dumps({"k": k, "l": l, "T": T, "invariants": inv,
                      "vertices": fv, "faces": fc}))


def main():
    if "--json" in sys.argv:
        i = sys.argv.index("--json")
        k = int(sys.argv[i + 1])
        l = int(sys.argv[i + 2])
        emit_json(k, l)
        return
    ok = verify_all()
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
