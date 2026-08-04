"""
KLEIN RECEIPT v0.3 -- v0.2 frozen; this is a copy + extension.

v0.2 result that forced this: the degree-11 map's attractor is NOT the 12
vertices. R7's multiplier chart was buggy (it reported a fixed point 38 away
from itself, which Euler's relation z f_z + w f_w = 12 f forbids), so R7 is
dropped entirely rather than patched -- R8-style iteration measures the same
thing without a chart. Here we measure the attractor of all three gradient
equivariants and let the kernel choose which map the shell should render.
"""
import numpy as np, sympy as sp

z, w = sp.symbols('z w')
f = z*w*(z**10 + 11*z**5*w**5 - w**10)
H = sp.expand(sp.diff(f, z, 2)*sp.diff(f, w, 2) - sp.diff(f, z, w)**2)
T = sp.expand(sp.diff(f, z)*sp.diff(H, w) - sp.diff(f, w)*sp.diff(H, z))

# --- the three orbits on S^2, from Klein's own normalization ------------------
r10 = np.roots([1, 0, 0, 0, 0, 11, 0, 0, 0, 0, -1])
VERT = [(0j, 1+0j), (1+0j, 0j)] + [(c, 1+0j) for c in r10]


def to_s2(p):
    zz, ww = p
    if abs(ww) < 1e-14: return np.array([0., 0., 1.])
    c = zz/ww; x, y = c.real, c.imag; d = 1 + x*x + y*y
    return np.array([2*x/d, 2*y/d, (d-2)/d])


S2 = np.array([to_s2(p) for p in VERT])
D = np.linalg.norm(S2[:, None] - S2[None, :], axis=2)
FACE = np.array([S2[[i, j, k]].sum(0)/np.linalg.norm(S2[[i, j, k]].sum(0))
                 for i in range(12) for j in range(i+1, 12) for k in range(j+1, 12)
                 if D[i, j] < 1.2 and D[i, k] < 1.2 and D[j, k] < 1.2])
EDGE = np.array([(S2[i]+S2[j])/np.linalg.norm(S2[i]+S2[j])
                 for i in range(12) for j in range(i+1, 12) if D[i, j] < 1.2])
ORB = {'vertices (P)': S2, 'faces (V of C20)': FACE, 'edges (E of C20)': EDGE}
print("orbits on S^2 :", {k: len(v) for k, v in ORB.items()})

# --- the three gradient equivariants -----------------------------------------
MAPS = {}
for name, F, d in (('g11 = [f_w : -f_z]', f, 11), ('g19 = [H_w : -H_z]', H, 19),
                   ('g29 = [T_w : -T_z]', T, 29)):
    n = sp.lambdify((z, w), sp.expand(sp.diff(F, w)), 'numpy')
    dd = sp.lambdify((z, w), sp.expand(-sp.diff(F, z)), 'numpy')
    MAPS[name] = (n, dd, d)

rng = np.random.default_rng(3)


def run(nf, df, iters=400, seeds=600):
    P = rng.normal(size=(seeds, 2)) @ [1, 1j]
    Z = P.astype(complex); Wc = np.ones(seeds, complex)
    for _ in range(iters):
        m = np.sqrt(abs(Z)**2 + abs(Wc)**2); m[m < 1e-300] = 1
        Z, Wc = Z/m, Wc/m
        Z, Wc = nf(Z, Wc), df(Z, Wc)
        bad = ~np.isfinite(Z) | ~np.isfinite(Wc)
        Z[bad], Wc[bad] = 0, 1
    pts = np.array([to_s2((a, b)) for a, b in zip(Z, Wc)])
    cl = []
    for v in pts:
        for c in cl:
            if np.linalg.norm(v-c[0]) < 2e-3: c[1] += 1; break
        else: cl.append([v, 1])
    return np.array([c[0] for c in cl])


print()
print("=" * 78)
print(f"{'map':22s} {'deg':>4s} {'attractors':>11s}   nearest orbit (max distance)")
print("=" * 78)
CHOSEN = None
for name, (nf, df, d) in MAPS.items():
    C = run(nf, df)
    best, bd = None, 9
    for on, ov in ORB.items():
        dist = max(np.min(np.linalg.norm(ov - c, axis=1)) for c in C)
        if dist < bd: bd, best = dist, on
    tag = f"{best}  ({bd:.1e})" if bd < 1e-2 else f"none within 1e-2 (best {best} {bd:.1e})"
    print(f"{name:22s} {d:4d} {len(C):11d}   {tag}")
    if len(C) == 12 and bd < 1e-2 and 'vertices' in best:
        CHOSEN = name

print()
print("=" * 78)
print("VERDICT")
print("=" * 78)
if CHOSEN:
    print(f"   a 12-basin icosahedral map exists: {CHOSEN}  -> P = 12 is the basin count")
else:
    print("   NO gradient equivariant among degrees 11/19/29 has 12 basins.")
    print("   The shell must therefore label its basin count as MEASURED, not as P.")
    print("   Genesis's P=12 is a TOPOLOGY invariant (Euler), not a dynamical one.")
    print("   Claiming otherwise would be Curse 26 with extra steps.")
