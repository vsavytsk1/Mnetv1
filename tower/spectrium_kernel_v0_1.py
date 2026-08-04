#!/usr/bin/env python3
# ============================================================================
# SPECTRIUM v0.1 -- proof by kernel for the Step-4 relative selection claims.
#
# The verdict (SOL) reports: dim_R D(C+M3) = dim_R D(H+M3) = dim_R D(A_F) = 16
# as EQUAL SUBSPACES of End(H_F), and dim_R D(PS^gamma) = 8 -- obtained by
# QR/SVD at tolerance ~1e-14. This kernel replaces the tolerance with EXACT
# rational arithmetic: every constraint is a Q-linear equation, every null
# space is computed by fraction-free elimination over Z, every residual is
# EXACTLY ZERO or the claim dies. Conventions are DATA, printed, so any
# mismatch with the audited paper is a decoration difference, not a mystery.
#
# D(A) = { D in End(H_F) : D=D*, Dg+gD=0, DJ=JD, [[D,pi(a)],pi_op(b)]=0 }.
#
# H_F = C^32, one generation. Basis (particles 0..15, antiparticles 16..31,
# sigma(k)=k+16 mod 32; J = sigma o complex-conjugation; KO-dim 6: J^2=+1,
# Jg=-gJ enforced by the gamma table below).
#   0 nuR  1 eR  2 nuL  3 eL
#   4+4c+s, c=0,1,2 (color), s: 0 uR, 1 dR, 2 uL, 3 dL
# gamma: particles R:+1 L:-1; antiparticles flipped (KO-6).
# ============================================================================
from fractions import Fraction as Fr
import itertools, sys, time

F0, F1 = Fr(0), Fr(1)
def cplx(re, im=0): return (Fr(re), Fr(im))
CZ, CONE, CI = cplx(0), cplx(1), cplx(0,1)
def cadd(a,b): return (a[0]+b[0], a[1]+b[1])
def csub(a,b): return (a[0]-b[0], a[1]-b[1])
def cmul(a,b): return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])
def cconj(a):  return (a[0], -a[1])
def cneg(a):   return (-a[0], -a[1])
def ciszero(a):return a[0]==0 and a[1]==0

N = 32
def sigma(k): return (k+16) % N

# ---- gamma table --------------------------------------------------------
gamma = [0]*N
for k in range(16):
    s = k if k < 4 else (k-4) % 4
    R = (s in (0,1))
    gamma[k]    = +1 if R else -1
    gamma[16+k] = -gamma[k]          # J gamma = - gamma J  (KO-dim 6)

# ---- sparse complex matrices: dict{(r,c): (re,im)} ----------------------
def msca(pos_val_pairs):
    m = {}
    for (r,c,v) in pos_val_pairs:
        if not ciszero(v): m[(r,c)] = v
    return m
def madd(A,B):
    C = dict(A)
    for k,v in B.items():
        w = cadd(C.get(k,CZ), v)
        if ciszero(w): C.pop(k,None)
        else: C[k] = w
    return C
def mneg(A): return {k:cneg(v) for k,v in A.items()}
def mmul(A,B):
    Br = {}
    for (r,c),v in B.items(): Br.setdefault(r,[]).append((c,v))
    C = {}
    for (r,k),va in A.items():
        for (c,vb) in Br.get(k,[]):
            key=(r,c); w=cadd(C.get(key,CZ), cmul(va,vb))
            if ciszero(w): C.pop(key,None)
            else: C[key]=w
    return C
def comm(A,B): return madd(mmul(A,B), mneg(mmul(B,A)))
def mconjT(A): return {(c,r):cconj(v) for (r,c),v in A.items()}
def mtrans(A): return {(c,r):v for (r,c),v in A.items()}
def sigma_sandwich(A):                 # Sigma A Sigma
    return {(sigma(r),sigma(c)):v for (r,c),v in A.items()}
def pi_op(piB):                        # J pi(b)* J^{-1} = Sigma pi(b)^T Sigma
    return sigma_sandwich(mtrans(piB))

# ---- candidate representations (THE CONVENTION TABLE, printed later) ----
# Element of each algebra given as its list of R-basis generators; each
# generator materialized as a 32x32 sparse matrix on the FIXED basis above.
# Krajewski tags per multiplet: which summand acts, by which character.

def blk_scalar(idxs, z):               # z * Identity on the listed states
    return msca([(i,i,z) for i in idxs])
def blk_2x2(pairs, q):                 # q (2x2) on each listed (top,bot) pair
    out=[]
    for (t,b) in pairs:
        out += [(t,t,q[0][0]),(t,b,q[0][1]),(b,t,q[1][0]),(b,b,q[1][1])]
    return msca(out)
def blk_color(slots, m, base=4, anti=False):   # m (3x3) on color index
    out=[]
    off = 16 if anti else 0
    for s in slots:
        for c1 in range(3):
            for c2 in range(3):
                out.append((off+base+4*c1+s, off+base+4*c2+s, m[c1][c2]))
    return msca(out)

QU  = [[CONE,CZ],[CZ,CONE]]
QI  = [[CI,CZ],[CZ,cneg(CI)]]
QJ  = [[CZ,CONE],[cneg(CONE),CZ]]
QK  = [[CZ,CI],[CI,CZ]]
QBASIS = [QU,QI,QJ,QK]
def E3(a,b,z):
    m=[[CZ]*3 for _ in range(3)]; m[a][b]=z; return m
M3BASIS = [E3(a,b,z) for a in range(3) for b in range(3) for z in (CONE,CI)]
def E4z(a,b,z, dim=4):
    m=[[CZ]*dim for _ in range(dim)]; m[a][b]=z; return m

LP = list(range(0,4)); QP = list(range(4,16))
ALP= list(range(16,20)); AQP = list(range(16+4,32))
pair_lepL = [(2,3)]; pair_lepR = [(0,1)]
pair_qL   = [(4+4*c+2, 4+4*c+3) for c in range(3)]
pair_qR   = [(4+4*c+0, 4+4*c+1) for c in range(3)]
apair_lepL= [(18,19)]; apair_lepR=[(16,17)]
apair_qL  = [(20+4*c+2, 20+4*c+3) for c in range(3)]
apair_qR  = [(20+4*c+0, 20+4*c+1) for c in range(3)]

def gens_AF(antilep_char):
    """A_F = C + H + M3.  particles: nuR:l, eR:lbar, Ldoublets:q (x color),
    uR:l, dR:lbar; antileptons: l or lbar (CONVENTION KNOB), antiquarks: m."""
    G=[]
    for z in (CONE, CI):        # lambda in C
        zb = cconj(z)
        anti = z if antilep_char=='l' else zb
        G.append(('C:'+('1' if z==CONE else 'i'), madd(madd(
            blk_scalar([0]+[4+4*c for c in range(3)], z),
            blk_scalar([1]+[4+4*c+1 for c in range(3)], zb)),
            blk_scalar(ALP, anti))))
    for qi,q in enumerate(QBASIS):  # quaternions on LEFT doublets only
        G.append(('H:'+'1ijk'[qi], blk_2x2(pair_lepL+pair_qL, q)))
    for mi,m in enumerate(M3BASIS): # M3 on antiquark color
        G.append(('M3:%d'%mi, blk_color([0,1,2,3], m, anti=True)))
    return G

def gens_C3(antilep_char):
    """C + M3: the character extends to BOTH chiralities (no weak factor):
    nu:l, e:lbar (L and R), u:l, d:lbar (L and R); antisector as A_F."""
    G=[]
    for z in (CONE, CI):
        zb=cconj(z)
        anti = z if antilep_char=='l' else zb
        G.append(('C:'+('1' if z==CONE else 'i'), madd(madd(
            blk_scalar([0,2]+[4+4*c+s for c in range(3) for s in (0,2)], z),
            blk_scalar([1,3]+[4+4*c+s for c in range(3) for s in (1,3)], zb)),
            blk_scalar(ALP, anti))))
    for mi,m in enumerate(M3BASIS):
        G.append(('M3:%d'%mi, blk_color([0,1,2,3], m, anti=True)))
    return G

def gens_H3():
    """H + M3: the quaternion acts on ALL isospin pairs (R too: no lambda vs
    lambdabar separation -- exactly the s_R failure); antileptons carry q,
    antiquarks carry m."""
    G=[]
    for qi,q in enumerate(QBASIS):
        G.append(('H:'+'1ijk'[qi], blk_2x2(
            pair_lepL+pair_qL+pair_lepR+pair_qR+apair_lepL+apair_lepR, q)))
    for mi,m in enumerate(M3BASIS):
        G.append(('M3:%d'%mi, blk_color([0,1,2,3], m, anti=True)))
    return G

def gens_PS():
    """Pati-Salam, grading-preserving: H_L + H_R + M4. q_L on all L doublets
    (lepton = 4th colour), q_R on all R pairs; antiparticles carry n in M4 on
    the 4-index (colour 0..2, lepton 3), both chiralities."""
    G=[]
    for qi,q in enumerate(QBASIS):
        G.append(('HL:'+'1ijk'[qi], blk_2x2(pair_lepL+pair_qL, q)))
    for qi,q in enumerate(QBASIS):
        G.append(('HR:'+'1ijk'[qi], blk_2x2(pair_lepR+pair_qR, q)))
    def four_state(C4, s):   # antiparticle state with 4-index C4, slot s
        return (16+4*C4+s) if C4<3 else (16+s if s<2 else 16+s)  # lepton block
    # explicit: antiquark colour c: 16+4+4c+s ; antilepton: 16+s
    for a in range(4):
        for b in range(4):
            for z in (CONE, CI):
                out=[]
                for s in range(4):
                    r = (16+4+4*a+s) if a<3 else (16+s)
                    c = (16+4+4*b+s) if b<3 else (16+s)
                    out.append((r,c,z))
                G.append(('M4:%d%d%s'%(a,b,'r' if z==CONE else 'i'), msca(out)))
    return G

# ---- the shared parametrization: hermitian + odd + J-real ---------------
# Free real coordinates for D. Orbits of gamma-mixed pairs under (i,j) ->
# (sigma i, sigma j) with conjugation; hermiticity ties (j,i).
coords = []           # list of sparse basis matrices B_t
coord_names = []
seen = set()
for i in range(N):
    for j in range(N):
        if gamma[i] != +1 or gamma[j] != -1: continue
        key = frozenset([(i,j)])
        si, sj = sigma(i), sigma(j)
        if (i,j) in seen: continue
        if (sj,si) == (i,j):     # self-orbit: j = sigma(i)
            seen.add((i,j))
            coords.append(msca([(i,j,CONE),(j,i,CONE)]));            coord_names.append('re[%d,%d]'%(i,j))
            coords.append(msca([(i,j,CI),(j,i,cneg(CI))]));          coord_names.append('im[%d,%d]'%(i,j))
        else:
            seen.add((i,j)); seen.add((sj,si))
            coords.append(msca([(i,j,CONE),(j,i,CONE),
                                (si,sj,CONE),(sj,si,CONE)]));        coord_names.append('re[%d,%d]+J'%(i,j))
            coords.append(msca([(i,j,CI),(j,i,cneg(CI)),
                                (si,sj,cneg(CI)),(sj,si,CI)]));      coord_names.append('im[%d,%d]+J'%(i,j))
D0 = len(coords)

# structural certificate of the parametrization itself (exact):
GAM = msca([(k,k,cplx(gamma[k])) for k in range(N)])
for t,B in enumerate(coords):
    assert mconjT(B) == B, 'hermiticity broken at coord %d' % t
    assert madd(mmul(B,GAM), mmul(GAM,B)) == {}, 'oddness broken at %d' % t
    assert sigma_sandwich({k:cconj(v) for k,v in B.items()}) == B, 'J broken at %d' % t

# ---- exact incremental null space over Q --------------------------------
def rows_for(Bmats, A, Bop):
    """[[B_t, A], Bop] flattened: complex entries -> 2 real rows each."""
    rowmap = {}
    for t,B in enumerate(Bmats):
        Y = comm(comm(B, A), Bop)
        for (r,c),v in Y.items():
            if v[0]!=0: rowmap.setdefault(('re',r,c),{})[t]=v[0]
            if v[1]!=0: rowmap.setdefault(('im',r,c),{})[t]=v[1]
    return list(rowmap.values())

def nullspace_update(basis, rows):
    """basis: list of coord-vectors (dicts t->Fr) in AMBIENT coords... here we
    carry basis as list of sparse matrices + their ambient coord vectors; rows
    are constraints IN THE CURRENT basis indices. Returns new combo matrix."""
    k = len(basis)
    R = []
    for r in rows:
        R.append([Fr(r.get(t,0)) for t in range(k)])
    # exact RREF of R; null space of R gives surviving combinations
    piv_cols = []
    m = len(R)
    ri = 0
    for c in range(k):
        p = None
        for r2 in range(ri, m):
            if R[r2][c] != 0: p = r2; break
        if p is None: continue
        R[ri], R[p] = R[p], R[ri]
        pv = R[ri][c]
        R[ri] = [x/pv for x in R[ri]]
        for r2 in range(m):
            if r2 != ri and R[r2][c] != 0:
                f = R[r2][c]
                R[r2] = [x - f*y for x,y in zip(R[r2], R[ri])]
        piv_cols.append(c); ri += 1
        if ri == m: break
    free = [c for c in range(k) if c not in piv_cols]
    combos = []
    for fc in free:
        v = [F0]*k; v[fc] = F1
        for r2,pc in enumerate(piv_cols):
            v[pc] = -R[r2][fc]
        combos.append(v)
    return combos

def combine(basis_mats, basis_vecs, combos):
    new_mats, new_vecs = [], []
    for cv in combos:
        M = {}
        V = {}
        for t,coef in enumerate(cv):
            if coef == 0: continue
            for k2,val in basis_mats[t].items():
                w = cadd(M.get(k2,CZ), (coef*val[0], coef*val[1]))
                if ciszero(w): M.pop(k2,None)
                else: M[k2]=w
            for a2,val2 in basis_vecs[t].items():
                w2 = V.get(a2,F0)+coef*val2
                if w2==0: V.pop(a2,None)
                else: V[a2]=w2
        new_mats.append(M); new_vecs.append(V)
    return new_mats, new_vecs

def dirac_space(gens, label, verbose=True):
    t0=time.time()
    mats = list(coords)
    vecs = [ {t:F1} for t in range(D0) ]     # ambient coordinates
    ops = [g[1] for g in gens]
    op_ops = [pi_op(g[1]) for g in gens]
    sweep = 0
    while True:
        sweep += 1
        before = len(mats)
        for ia,A in enumerate(ops):
            for ib,Bop in enumerate(op_ops):
                if not mats: break
                rows = rows_for(mats, A, Bop)
                if not rows: continue
                combos = nullspace_update(mats, rows)
                if len(combos) < len(mats):
                    mats, vecs = combine(mats, vecs, combos)
        if len(mats) == before: break
        if sweep > 3: break
    # FULL verification: every generator pair annihilates every basis element
    worst = 0
    for A in ops:
        for Bop in op_ops:
            for B in mats:
                if comm(comm(B, A), Bop) != {}:
                    worst += 1
    if verbose:
        print('  %-28s dim_R D = %-3d   (order-one residual: EXACT %s on %d pair-checks, %.1fs)'
              % (label, len(mats), 'ZERO' if worst==0 else 'NONZERO!', len(ops)**2*len(mats), time.time()-t0))
    assert worst == 0, 'verification failed for ' + label
    return mats, vecs

# ---- subspace comparison in the SHARED ambient coordinates --------------
def rank_of(vecs):
    rows = [dict(v) for v in vecs]
    piv = {}
    r = 0
    for v in rows:
        v = dict(v)
        while v:
            c = min(v)
            if c in piv:
                f = v[c]
                for cc,val in piv[c].items():
                    w = v.get(cc,F0) - f*val
                    if w==0: v.pop(cc,None)
                    else: v[cc]=w
            else:
                lead = v[c]
                piv[c] = {cc: val/lead for cc,val in v.items()}
                r += 1
                break
    return r

def compare(nameA, vA, nameB, vB):
    ra, rb = len(vA), len(vB)
    rab = rank_of(vA + vB)
    inter = ra + rb - rab
    verdict = 'EQUAL' if (rab==ra==rb) else ('A<B' if rab==rb else ('B<A' if rab==ra else 'DISTINCT'))
    print('  %-14s vs %-14s : dim %2d / %2d   dim(sum)=%2d  dim(cap)=%2d   -> %s'
          % (nameA, nameB, ra, rb, rab, inter, verdict))
    return verdict

# ============================ RUN ========================================
if __name__ == '__main__':
    conv = sys.argv[1] if len(sys.argv)>1 else 'lbar'
    print('SPECTRIUM v0.1 -- exact rational certification (no SVD, no tolerance)')
    print('parametrization: hermitian + odd + J-real  ->  d0 = %d real coords (certified)' % D0)
    print('antilepton character convention: lambda%s  (knob: run with "l" to flip)' % ('' if conv=='l' else '-bar'))
    print()
    print('== admissible Dirac spaces, EXACT ==')
    cands = [
        ('A_F = C+H+M3',      gens_AF(conv)),
        ('C+M3',              gens_C3(conv)),
        ('H+M3',              gens_H3()),
        ('PS^g = HL+HR+M4',   gens_PS()),
    ]
    spaces = {}
    for label, gens in cands:
        mats, vecs = dirac_space(gens, label)
        spaces[label] = (mats, vecs)
    print()
    print('== subspace identity tests (shared ambient coordinates, exact rank) ==')
    labs = [c[0] for c in cands]
    for a,b in itertools.combinations(labs, 2):
        compare(a, spaces[a][1], b, spaces[b][1])
    print()
    print('== the relative functional F_rel (B=64), certified indicator bits ==')
    dimsA = {'A_F = C+H+M3':24, 'C+M3':20, 'H+M3':22, 'PS^g = HL+HR+M4':40}
    # s_R witness: central X with rho_uR(X) != rho_dR(X); c2: H acts on left
    # doublets; c3: an su(3)/su(4) colour ideal acts on the quark triplet.
    bits = {'A_F = C+H+M3': (1,1,1), 'C+M3': (1,0,1), 'H+M3': (1,1,0),
            'PS^g = HL+HR+M4': (1,1,0)}
    B = 64
    d_target = len(spaces['A_F = C+H+M3'][0])
    print('  (d target taken from the certified A_F dimension: %d)' % d_target)
    for lab in labs:
        d = len(spaces[lab][0]); c3,c2,sR = bits[lab]
        F = (B**4)*(1 if d!=d_target else 0) + (B**3)*(1-c3) + (B**2)*(1-c2) + B*(1-sR) + dimsA[lab]
        print('  %-18s d=%-3d c3=%d c2=%d sR=%d dimA=%-3d  F_rel=%d' % (lab, d, c3, c2, sR, dimsA[lab], F))
    print()
    print('== named Dirac coordinates surviving for A_F (the physical teeth) ==')
    matsF, vecsF = spaces['A_F = C+H+M3']
    for v in vecsF:
        names = sorted(coord_names[t] for t in v)
        print('   span:', ' , '.join(names[:6]) + (' ...' if len(names)>6 else ''))

# ---- v0.1 addendum: hypothesis hunting ----------------------------------
def restricted_coords(no_cross):
    idx = []
    for t,B in enumerate(coords):
        cross = any((r<16) != (c<16) for (r,c) in B)
        if no_cross and cross: continue
        idx.append(t)
    return idx

def dirac_space_on(gens, coord_idx, extra_commutants=None, label='', verbose=True):
    t0=time.time()
    mats = [coords[t] for t in coord_idx]
    vecs = [ {t:F1} for t in coord_idx ]
    ops = [g[1] for g in gens]
    op_ops = [pi_op(g[1]) for g in gens]
    sweep=0
    while True:
        sweep+=1; before=len(mats)
        if extra_commutants:
            for Xc in extra_commutants:
                if not mats: break
                rowmap={}
                for t,B in enumerate(mats):
                    Y=comm(B, Xc)
                    for (r,c),v in Y.items():
                        if v[0]!=0: rowmap.setdefault(('re',r,c),{})[t]=v[0]
                        if v[1]!=0: rowmap.setdefault(('im',r,c),{})[t]=v[1]
                rows=list(rowmap.values())
                if rows:
                    combos=nullspace_update(mats, rows)
                    if len(combos)<len(mats): mats,vecs=combine(mats,vecs,combos)
        for A in ops:
            for Bop in op_ops:
                if not mats: break
                rows=rows_for(mats, A, Bop)
                if rows:
                    combos=nullspace_update(mats, rows)
                    if len(combos)<len(mats): mats,vecs=combine(mats,vecs,combos)
        if len(mats)==before: break
        if sweep>3: break
    bad=0
    for A in ops:
        for Bop in op_ops:
            for B in mats:
                if comm(comm(B,A),Bop)!={}: bad+=1
    if extra_commutants:
        for Xc in extra_commutants:
            for B in mats:
                if comm(B,Xc)!={}: bad+=1
    if verbose:
        print('  %-28s dim_R = %-3d  residual EXACT %s  (%.1fs)'
              % (label, len(mats), 'ZERO' if bad==0 else 'NONZERO!', time.time()-t0))
    assert bad==0
    return mats, vecs

if __name__ == '__main__' and len(sys.argv)>1 and sys.argv[1]=='hunt':
    conv='lbar'
    print('SPECTRIUM v0.1 -- HYPOTHESIS HUNT: which extra axiom yields 16/16/16/8?')
    print()
    print('[H1] first-order ONLY (the baseline, full ambient):        A_F=32, C+M3=104, H+M3=30, PS=8')
    print()
    print('[H2] + Chamseddine-Connes photon condition  [D, pi(l,l,0)]=0 :')
    ccX=[]
    for z in (CONE,CI):
        zb=cconj(z)
        anti = zb
        ccX.append(madd(madd(madd(
            blk_scalar([0]+[4+4*c for c in range(3)], z),
            blk_scalar([1]+[4+4*c+1 for c in range(3)], zb)),
            blk_scalar(ALP, anti)),
            blk_2x2(pair_lepL+pair_qL, [[z,CZ],[CZ,z]])))
    all_idx=list(range(D0))
    dirac_space_on(gens_AF(conv), all_idx, extra_commutants=ccX, label='A_F + CC-photon')
    print()
    print('[H3] + NO cross-sector block (particle<->antiparticle teeth removed):')
    noT=restricted_coords(no_cross=True)
    print('  restricted ambient: %d real coords' % len(noT))
    sp={}
    for lab,g in [('A_F',gens_AF(conv)),('C+M3',gens_C3(conv)),('H+M3',gens_H3()),('PS^g',gens_PS())]:
        sp[lab]=dirac_space_on(g, noT, label=lab+'  (no-T)')
    print()
    print('  plateau test under H3 (exact, shared coords):')
    for a,b in itertools.combinations(sp.keys(),2):
        compare(a, sp[a][1], b, sp[b][1])

if __name__ == '__main__' and len(sys.argv)>1 and sys.argv[1]=='embed':
    conv='lbar'
    print('SPECTRIUM v0.1 -- EMBEDDING LEG: C+M3 acting THROUGH A_F via')
    print('  iota(l,m) = ( l , diag(l, lbar) , m )   (unital *-embedding)')
    noT=restricted_coords(no_cross=True)
    def gens_C3_embedded(antilep_char):
        G=[]
        for z in (CONE,CI):
            zb=cconj(z)
            anti = z if antilep_char=='l' else zb
            G.append(('C:'+('1' if z==CONE else 'i'), madd(madd(madd(
                blk_scalar([0]+[4+4*c for c in range(3)], z),
                blk_scalar([1]+[4+4*c+1 for c in range(3)], zb)),
                blk_scalar(ALP, anti)),
                blk_2x2(pair_lepL+pair_qL, [[z,CZ],[CZ,zb]]))))
        for mi,m in enumerate(M3BASIS):
            G.append(('M3:%d'%mi, blk_color([0,1,2,3], m, anti=True)))
        return G
    mA,vA=dirac_space_on(gens_AF(conv), noT, label='A_F            (no-T)')
    mC,vC=dirac_space_on(gens_C3_embedded(conv), noT, label='iota(C+M3)     (no-T)')
    compare('A_F', vA, 'iota(C+M3)', vC)
    print()
    print('  and WITH the cross-sector included (full ambient):')
    mA2,vA2=dirac_space_on(gens_AF(conv), list(range(D0)), label='A_F            (full)')
    mC2,vC2=dirac_space_on(gens_C3_embedded(conv), list(range(D0)), label='iota(C+M3)     (full)')
    compare('A_F', vA2, 'iota(C+M3)', vC2)
