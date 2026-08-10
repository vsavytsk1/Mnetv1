#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
THE WALK v0.1 -- executing the pre-registered experiment of THE_CROWD.md S8
============================================================================
Object:   Lane A contact graphs from the SHIPPED refine() of
          genesis_wallpaper_v1_7.py (Curse 40: never a replica), seed C60,
          shipped defaults INNER=0.45 MID=0.70 (aR = 0.8875).
Question: does a random walker see the fractal (d_s < 2) or the sphere
          (d_s -> 2)? Sealed before running. Either answer publishes.
Registered protocol: gen 5, 1e5 walkers, 1e5 steps, seed 20260809,
          P0(t) ~ t^(-d_s/2), plus a second instrument.
Deviations, stated up front (Curse 12: the boundary is part of the result):
          steps T = 3e4 not 1e5 (wall-clock budget; window still ~2 decades);
          second instrument = (a) the same walk run on two graphs of KNOWN
          d_s (torus = 2 exactly, Sierpinski gasket = 2 ln3/ln5 = 1.3652)
          to calibrate the estimator, and (b) Laplacian eigenvalue counting
          on gen 3. Registration named (b); (a) is added, not substituted.
P=12. chi=2. The price is always paid.
"""
import importlib.util, math, time, sys
import numpy as np
from collections import defaultdict

T0 = time.time()
def tick(msg):
    print("[%6.1fs] %s" % (time.time()-T0, msg)); sys.stdout.flush()

spec = importlib.util.spec_from_file_location(
    "gen17", "/mnt/user-data/outputs/genesis_wallpaper_v1_7.py")
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
tick("shipped module loaded: INNER=%.2f MID=%.2f JITTER=%.2f R=%.1f"
     % (g.INNER_SCALE, g.MID_SCALE, g.JITTER, g.SPHERE_R))

RNG = np.random.default_rng(20260809)

# ---------------- generations with top-parent labels -------------------------
P, Hf, info = g.build_seed("C60", verbose=False)
labP = np.arange(len(P), dtype=np.int32)                 # 12 pentagons: 0..11
labH = np.arange(len(Hf), dtype=np.int32) + len(P)       # 20 hexes: 12..31

def one_gen(P, Hf, labP, labH):
    ip, cp = g.refine(P, g.SPHERE_R, RNG)                # (12,5,3), (60,6,3)
    ih, ch = g.refine(Hf, g.SPHERE_R, RNG)               # (m,6,3), (6m,6,3)
    newP, nlabP = ip, labP.copy()
    newH = np.concatenate([cp.reshape(-1, 6, 3), ih, ch.reshape(-1, 6, 3)], axis=0)
    nlabH = np.concatenate([np.repeat(labP, 5), labH, np.repeat(labH, 6)])
    return newP, newH, nlabP, nlabH.astype(np.int32)

GENS = {0: (P, Hf, labP, labH)}
for k in range(1, 6):
    P, Hf, labP, labH = one_gen(P, Hf, labP, labH)
    GENS[k] = (P, Hf, labP, labH)
    tick("gen %d built: faces=%d (12 pent + %d hex)" % (k, len(P)+len(Hf), len(Hf)))

# ---------------- contact graph --------------------------------------------
def contact_graph(P, Hf, labP, labH):
    arrs, fids, f0 = [], [], 0
    for A in (P, Hf):
        m, kk, _ = A.shape
        arrs.append(np.round(np.asarray(A, np.float64).reshape(-1, 3), 7))
        fids.append(np.repeat(np.arange(f0, f0+m, dtype=np.int64), kk))
        f0 += m
    Vs = np.concatenate(arrs); F = np.concatenate(fids)
    uq, inv = np.unique(Vs, axis=0, return_inverse=True)
    order = np.argsort(inv, kind="stable")
    invs, Fs = inv[order], F[order]
    starts = np.flatnonzero(np.r_[True, invs[1:] != invs[:-1]])
    ends = np.r_[starts[1:], len(invs)]
    pair = defaultdict(int)
    for s, e in zip(starts, ends):
        n = e - s
        if n < 2: continue
        fs = Fs[s:e]
        if n == 2:
            a, b = int(fs[0]), int(fs[1])
            if a != b:
                if a > b: a, b = b, a
                pair[(a, b)] += 1
        else:
            u = sorted(set(int(x) for x in fs))
            for i in range(len(u)):
                for j in range(i+1, len(u)):
                    pair[(u[i], u[j])] += 1
    lab = np.concatenate([labP, labH])
    a = np.fromiter((k[0] for k in pair), np.int64, len(pair))
    b = np.fromiter((k[1] for k in pair), np.int64, len(pair))
    w = np.fromiter(pair.values(), np.int64, len(pair))
    N = f0
    deg = np.bincount(a, minlength=N) + np.bincount(b, minlength=N)
    indptr = np.zeros(N+1, np.int64); indptr[1:] = np.cumsum(deg)
    indices = np.empty(indptr[-1], np.int64)
    cur = indptr[:-1].copy()
    for x, y in ((a, b), (b, a)):
        for i in range(len(x)):
            indices[cur[x[i]]] = y[i]; cur[x[i]] += 1
    corner = float(np.mean(w == 1))
    cross = float(np.mean(lab[a] != lab[b]))
    cross_corner = float(np.mean((w == 1) & (lab[a] != lab[b])))
    return N, indptr, indices, deg.astype(np.int64), lab, dict(
        edges=len(pair), corner_frac=corner, cross_frac=cross,
        cross_corner_frac=cross_corner)

# fill indices loop above is python over edges: vectorize instead
def contact_graph_fast(P, Hf, labP, labH):
    N, indptr, indices, deg, lab, st = None, None, None, None, None, None
    arrs, fids, f0 = [], [], 0
    for A in (P, Hf):
        m, kk, _ = A.shape
        arrs.append(np.round(np.asarray(A, np.float64).reshape(-1, 3), 7))
        fids.append(np.repeat(np.arange(f0, f0+m, dtype=np.int64), kk))
        f0 += m
    Vs = np.concatenate(arrs); F = np.concatenate(fids)
    uq, inv = np.unique(Vs, axis=0, return_inverse=True)
    order = np.argsort(inv, kind="stable")
    invs, Fs = inv[order], F[order]
    starts = np.flatnonzero(np.r_[True, invs[1:] != invs[:-1]])
    ends = np.r_[starts[1:], len(invs)]
    pair = defaultdict(int)
    for s, e in zip(starts, ends):
        n = e - s
        if n < 2: continue
        fs = Fs[s:e]
        if n == 2:
            x, y = int(fs[0]), int(fs[1])
            if x != y:
                if x > y: x, y = y, x
                pair[(x, y)] += 1
        else:
            u = sorted(set(int(v) for v in fs))
            for i in range(len(u)):
                for j in range(i+1, len(u)):
                    pair[(u[i], u[j])] += 1
    a = np.fromiter((k[0] for k in pair), np.int64, len(pair))
    b = np.fromiter((k[1] for k in pair), np.int64, len(pair))
    w = np.fromiter(pair.values(), np.int64, len(pair))
    N = f0
    src = np.concatenate([a, b]); dst = np.concatenate([b, a])
    o = np.argsort(src, kind="stable")
    src, dst = src[o], dst[o]
    deg = np.bincount(src, minlength=N).astype(np.int64)
    indptr = np.zeros(N+1, np.int64); indptr[1:] = np.cumsum(deg)
    indices = dst
    lab = np.concatenate([labP, labH])
    st = dict(edges=len(pair), corner_frac=float(np.mean(w == 1)),
              cross_frac=float(np.mean(lab[a] != lab[b])),
              cross_corner=float(np.mean((w == 1) & (lab[a] != lab[b]))))
    return N, indptr, indices, deg, lab, st

# ---------------- walk + fit -------------------------------------------------
def walk(indptr, indices, deg, W, T, seed, origin_lab=None):
    rng = np.random.default_rng(seed)
    N = len(deg)
    origin = rng.integers(0, N, W)
    pos = origin.copy()
    cps = np.unique(np.round(np.logspace(0, math.log10(T), 60)).astype(np.int64))
    cset = set(int(c) for c in cps)
    P0 = {}
    bows = 0; moves = 0
    for t in range(1, T+1):
        r = rng.random(W)
        idx = indptr[pos] + (r * deg[pos]).astype(np.int64)
        new = indices[idx]
        if origin_lab is not None:
            bows += int(np.sum(origin_lab[new] != origin_lab[pos])); moves += W
        pos = new
        if t in cset:
            P0[t] = float(np.mean(pos == origin))
    spb = (moves / bows) if (origin_lab is not None and bows) else float("nan")
    return P0, spb

def fit_ds(P0, lo, hi, N):
    ts = sorted(t for t in P0 if lo <= t <= hi and P0[t] > 3.0/N)
    if len(ts) < 6: return float("nan"), float("nan"), len(ts)
    x = np.log10(np.array(ts, float)); y = np.log10(np.array([P0[t] for t in ts]))
    n = len(x)
    mx, my = x.mean(), y.mean()
    Sxx = np.sum((x-mx)**2); Sxy = np.sum((x-mx)*(y-my))
    m = Sxy/Sxx; c = my - m*mx
    resid = y - (m*x + c)
    se = math.sqrt(np.sum(resid**2)/(n-2)/Sxx)
    return -2.0*m, 2.0*se, n

# ---------------- calibration graphs ----------------------------------------
def torus(nx, ny):
    N = nx*ny
    i = np.arange(N)
    x, y = i % nx, i // nx
    nb = np.stack([ (x+1) % nx + y*nx, (x-1) % nx + y*nx,
                    x + ((y+1) % ny)*nx, x + ((y-1) % ny)*nx ], 1)
    indices = nb.reshape(-1).astype(np.int64)
    deg = np.full(N, 4, np.int64)
    indptr = np.arange(0, 4*N+1, 4, dtype=np.int64)
    return N, indptr, indices, deg

def gasket(level):
    V = {}; 
    def vid(p):
        if p not in V: V[p] = len(V)
        return V[p]
    tris = [ (vid((0.0,0.0)), vid((1.0,0.0)), vid((0.5,math.sqrt(3)/2))) ]
    pts = {v:k for k,v in V.items()}
    def midpt(a,b):
        pa,pb = pts[a], pts[b]
        mp = (round((pa[0]+pb[0])/2,9), round((pa[1]+pb[1])/2,9))
        w = vid(mp); pts[w]=mp; return w
    for _ in range(level):
        nt=[]
        for (a,b,c) in tris:
            ab,bc,ca = midpt(a,b), midpt(b,c), midpt(c,a)
            nt += [(a,ab,ca),(ab,b,bc),(ca,bc,c)]
        tris=nt
    E=set()
    for (a,b,c) in tris:
        for u,v in ((a,b),(b,c),(c,a)):
            E.add((min(u,v),max(u,v)))
    N=len(V)
    a=np.fromiter((e[0] for e in E),np.int64,len(E))
    b=np.fromiter((e[1] for e in E),np.int64,len(E))
    src=np.concatenate([a,b]); dst=np.concatenate([b,a])
    o=np.argsort(src,kind="stable"); src,dst=src[o],dst[o]
    deg=np.bincount(src,minlength=N).astype(np.int64)
    indptr=np.zeros(N+1,np.int64); indptr[1:]=np.cumsum(deg)
    return N, indptr, dst, deg

# ---------------- run --------------------------------------------------------
print("="*79)
print("  THE WALK v0.1 -- the sealed experiment, executed")
print("="*79)

# calibration first: the instrument must read known dials correctly
for name, builder, args, truth in (
        ("TORUS 300x300 (d_s = 2 exactly)", torus, (300,300), 2.0),
        ("GASKET level 8 (d_s = 1.3652)", gasket, (8,), 2*math.log(3)/math.log(5))):
    N, ip, ix, dg = builder(*args)
    P0, _ = walk(ip, ix, dg, 100000, 30000, 20260809)
    ds, se, npt = fit_ds(P0, 30, 3000, N)
    tick("[CALIB] %-34s N=%-7d d_s = %.4f +- %.4f (%d pts)  truth %.4f  pull %+.1f"
         % (name, N, ds, se, npt, truth, (ds-truth)/se if se>0 else float("nan")))

results = {}
for gen in (3, 4, 5):
    Pg, Hg, lP, lH = GENS[gen]
    N, ip, ix, dg, lab, st = contact_graph_fast(Pg, Hg, lP, lH)
    # connectivity
    import scipy.sparse as sp
    import scipy.sparse.csgraph as cg
    A = sp.csr_matrix((np.ones(len(ix), np.int8), ix, ip), shape=(N, N))
    ncomp, _ = cg.connected_components(A, directed=False)
    tick("[GEN%d] N=%d edges=%d components=%d corner=%.3f cross-parent=%.4f deg(min/med/max)=%d/%d/%d"
         % (gen, N, st["edges"], ncomp, st["corner_frac"], st["cross_frac"],
            dg.min(), int(np.median(dg)), dg.max()))
    T = 30000
    P0, spb = walk(ip, ix, dg, 100000, T, 20260809, origin_lab=lab)
    ds1, se1, n1 = fit_ds(P0, 30, 3000, N)
    ds2, se2, n2 = fit_ds(P0, 10, 1000, N)
    ds3, se3, n3 = fit_ds(P0, 100, 10000, N)
    tick("[GEN%d] d_s [30,3000]=%.4f+-%.4f  [10,1000]=%.4f+-%.4f  [100,1e4]=%.4f+-%.4f  steps/bow=%.2f"
         % (gen, ds1, se1, ds2, se2, ds3, se3, spb))
    results[gen] = (ds1, se1, N, spb, st, ncomp)

# spectral second instrument on gen 3
Pg, Hg, lP, lH = GENS[3]
N3, ip3, ix3, dg3, lab3, st3 = contact_graph_fast(Pg, Hg, lP, lH)
import scipy.sparse as sp
from scipy.sparse.linalg import eigsh
L = sp.csr_matrix((np.concatenate([dg3.astype(float),
                                   -np.ones(len(ix3))]),
                   np.concatenate([np.arange(N3), ix3]),
                   np.concatenate([ip3[:-1]*0 + np.arange(N3), []])) ) if False else None
# build L properly
rows = np.repeat(np.arange(N3), np.diff(ip3))
A3 = sp.csr_matrix((np.ones(len(ix3)), (rows, ix3)), shape=(N3, N3))
L3 = sp.diags(dg3.astype(float)) - A3
vals = eigsh(L3, k=160, sigma=1e-9, which="LM", return_eigenvectors=False)
vals = np.sort(vals); vals = vals[vals > 1e-8]
lam = vals[4:150]
rank = np.arange(1, len(vals)+1)[4:150]
x = np.log10(lam); y = np.log10(rank)
mx, my = x.mean(), y.mean()
m = np.sum((x-mx)*(y-my))/np.sum((x-mx)**2)
c = my - m*mx
resid = y - (m*x+c)
se_m = math.sqrt(np.sum(resid**2)/(len(x)-2)/np.sum((x-mx)**2))
tick("[SPECTRAL gen3] N(lambda) ~ lambda^(d_s/2): d_s = %.4f +- %.4f over %d modes"
     % (2*m, 2*se_m, len(x)))

# ---------------- verdict ----------------------------------------------------
ds5, se5, N5, spb5, st5, nc5 = results[5]
pull = (2.0 - ds5)/se5
print("")
print("="*79)
print("  VERDICT (sealed hypotheses of THE_CROWD.md S8)")
print("  gen-5 contact graph: N = %d, connected components = %d" % (N5, nc5))
print("  d_s = %.4f +- %.4f   (window [30,3000], 1e5 walkers, seed 20260809)" % (ds5, se5))
print("  distance below 2: %.1f standard errors" % pull)
if pull > 3.0:
    print("  H_FRACTAL CONFIRMED: the walker sees the fractal. Hausdorff and")
    print("  spectral dimensions SPLIT on this object: D_H = 1.8835, d_s = %.3f." % ds5)
elif pull < -3.0:
    print("  d_s ABOVE 2 by >3 s.e. -- outside both sealed hypotheses; investigate.")
else:
    print("  H_BRIDGE holds at this size: d_s consistent with 2 within 3 s.e.")
    print("  The contacts act as bridges; fractality visible to area, not diffusion.")
print("  steps per bow (gen 5): %.2f" % spb5)
print("  P=12. chi=2. Either answer publishes. This is the answer.")
print("="*79)
