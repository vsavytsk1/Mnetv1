#!/usr/bin/env python3
"""THE STOPS AND CONTRADICTIONS -- demonstrated, not asserted.

Each section below reproduces a shipped code block faithfully and then shows
what it does NOT catch. Nothing here is a style opinion; every claim is run.
"""
from __future__ import annotations
import json, math, os, subprocess, sys, tempfile, time, tracemalloc
from pathlib import Path
import numpy as np

W = 78
def hdr(n, t): print("\n" + "=" * W + f"\n{n}. {t}\n" + "=" * W)

# ===========================================================================
hdr(1, "Block C's 8/8 PASS: how much of it is mathematics?")
# ===========================================================================
# Block C, verbatim in structure: R = json.loads(receipts/....json) at module
# scope, then eight tests. Classify each by whether it computes anything.
BLOCK_C_TESTS = {
    "test_light_matrix_exact":        ("computes Sym^2(Q); then reads 2 receipt fields", "MIXED"),
    "test_architecture_receipt":      ("reads receipt only", "FILE"),
    "test_big_integer_depth":         ("reads receipt only", "FILE"),
    "test_node_bigint":               ("reads receipt only", "FILE"),
    "test_modular_rank_stress":       ("reads receipt only", "FILE"),
    "test_commutant":                 ("reads receipt only", "FILE"),
    "test_genesis_counterexample":    ("computes 13 vs 9 from scratch", "MATH"),
    "test_open_rung_is_joke_not_result": ("reads receipt only", "FILE"),
}
for k, (what, kind) in BLOCK_C_TESTS.items():
    print(f"  {kind:5s}  {k:36s} {what}")
n_file = sum(1 for _, k in BLOCK_C_TESTS.values() if k == "FILE")
n_math = sum(1 for _, k in BLOCK_C_TESTS.values() if k == "MATH")
n_mix  = sum(1 for _, k in BLOCK_C_TESTS.values() if k == "MIXED")
print(f"\n  -> {n_file}/8 assert only that a JSON file contains certain strings.")
print(f"     {n_math}/8 recomputes mathematics. {n_mix}/8 does both.")

# Now DEMONSTRATE the failure mode: keep the receipt, break the mathematics.
print("\n  DEMONSTRATION -- freeze a receipt, then sabotage the maths behind it:")
receipt = {
    "symbolic": {"charpoly_M": "(lambda - 1)*(lambda + 1)*(lambda**2 - 3*lambda + 1)",
                 "M_T_Gamma_M_equals_Gamma": True},
    "architecture": {"machine": "x86_64", "pointer_bits": 64, "float64_mantissa_bits": 53},
    "exact_ladder_stress": {"depth": 500000, "terminal_decimal_digits": 208988,
                            "exact_match": True, "terminal_sha256_big_endian": "0" * 64},
    "node_bigint": {"depth": 200000, "terminal_decimal_digits": 83596,
                    "exact_match": True, "euler_characteristic": "2"},
    "modular_rank_stress": {"exact_extended_nullity": 16, "exact_pati_salam_nullity": 8,
                            "extended_runs": [{"ranks": {"1009": 256}}],
                            "pati_salam_runs": [{"ranks": {"1009": 264}}],
                            "explicit_yukawa16_rank": 16, "explicit_yukawa16_full_basis_residual": 0.0,
                            "explicit_paired8_rank": 8, "explicit_paired8_full_basis_residual": 0.0},
    "commutant": {"base_AF_witness": {"computed_commutant_dimension": 24, "verdict": "PASS"},
                  "computed_commutant_dimension": 25, "verdict": "PASS"},
    "status_boundary": {"trivial": "mathematical joke label for the still-open global Step 4"},
}
# the sabotage: the SAME symbolic function, but wrong. A real math test dies here.
def symmetric_square_2x2_SABOTAGED(Q):
    a, b, c, d = Q[0][0], Q[0][1], Q[1][0], Q[1][1]
    return [[a*a, 2*a*b, b*b], [a*c, a*d + b*c, b*d], [c*c, 2*c*d, d*d + 1]]  # <-- +1

passed = []
R = receipt
def t_arch():   return R["architecture"]["machine"] == "x86_64" and R["architecture"]["pointer_bits"] == 64
def t_bigint(): return R["exact_ladder_stress"]["depth"] == 500_000 and R["exact_ladder_stress"]["exact_match"]
def t_node():   return R["node_bigint"]["euler_characteristic"] == "2"
def t_rank():   return R["modular_rank_stress"]["exact_extended_nullity"] == 16
def t_comm():   return R["commutant"]["verdict"] == "PASS"
def t_joke():   return R["status_boundary"]["trivial"].startswith("mathematical joke")
def t_genesis():
    def eis_mul(x, y): a,b=x; c,d=y; return (a*c-b*d, a*d+b*c+b*d)
    def N(w): k,l=w; return k*k+k*l+l*l
    s=(1,1); sq=eis_mul(s,s); sh=(sq[0]+1, sq[1])
    return N(s)==3 and N(sh)==13 and N(s)**2==9
def t_lm():
    # block C's actual body: compute Sym^2, compare to a literal, then read the receipt
    got = symmetric_square_2x2_SABOTAGED([[1,1],[1,0]])
    struct_ok = (got == [[1,2,1],[1,1,0],[1,0,0]])
    recpt_ok  = (R["symbolic"]["charpoly_M"] == "(lambda - 1)*(lambda + 1)*(lambda**2 - 3*lambda + 1)"
                 and R["symbolic"]["M_T_Gamma_M_equals_Gamma"])
    return struct_ok and recpt_ok

for name, fn in [("test_architecture_receipt", t_arch), ("test_big_integer_depth", t_bigint),
                 ("test_node_bigint", t_node), ("test_modular_rank_stress", t_rank),
                 ("test_commutant", t_comm), ("test_open_rung_is_joke_not_result", t_joke),
                 ("test_genesis_counterexample", t_genesis), ("test_light_matrix_exact", t_lm)]:
    ok = fn(); passed.append(ok)
    print(f"    {'PASS' if ok else 'FAIL'}  {name}")
print(f"    -> {sum(passed)}/8 with Sym^2 sabotaged. The one test that touches the")
print("       broken function catches it; the six receipt-readers cannot, because")
print("       the receipt is a file and the file is still correct.")

# ===========================================================================
hdr(2, "python -O erases the proof steps that are written as `assert`")
# ===========================================================================
src = '''
def step4_no_go():
    plateau = [16, 16, 16]
    dsi_only_unique = len(set(plateau)) == len(plateau)
    assert not dsi_only_unique          # block E line 438: a PROOF STEP
    return "no-go established"
def wedderburn(n):
    r_blocks, c_blocks = 2, (n - 2) // 2
    real_dimension = r_blocks + 2 * c_blocks
    assert real_dimension == n          # block E line 317: a CHECK
    return real_dimension
print("step4_no_go ->", step4_no_go())
print("wedderburn(14) ->", wedderburn(14))
import sys
print("asserts active:", __debug__)
'''
with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
    f.write(src); tmp = f.name
for flags in ([], ["-O"]):
    out = subprocess.run([sys.executable, *flags, tmp], capture_output=True, text=True)
    label = "python" if not flags else "python -O"
    print(f"  {label:10s} -> {out.stdout.strip().splitlines()[-1]}")
os.unlink(tmp)
print("  -> under -O every `assert` in blocks D and E disappears. The functions still")
print("     return, the suite still prints PASS, and two proof steps have silently gone.")

# ===========================================================================
hdr(3, "Block D hardcodes what block A computes: the Gamma signature")
# ===========================================================================
print("  block A  (line ~238):  \"Gamma_eigenvalue_signs_numeric\":")
print("                          [int(np.sign(x)) for x in np.linalg.eigvalsh(Gamma)]   <- computed, in float64")
print("  block D  (line ~197):  \"Gamma4_signature_numeric\": [3, 1]                      <- TYPED IN")
G = [[1,-1,0,0],[-1,-1,1,0],[0,1,1,0],[0,0,0,1]]
ev = np.linalg.eigvalsh(np.array(G, dtype=float))
print(f"\n  float64 route (block A): eigenvalues {np.round(ev,12).tolist()}  -> ({int((ev>0).sum())},{int((ev<0).sum())})")
def det_int(A):
    n=len(A); M=[r[:] for r in A]; sign=1; prev=1
    for k in range(n-1):
        if M[k][k]==0:
            for i in range(k+1,n):
                if M[i][k]!=0: M[k],M[i]=M[i],M[k]; sign=-sign; break
            else: return 0
        for i in range(k+1,n):
            for j in range(k+1,n):
                M[i][j]=(M[i][j]*M[k][k]-M[i][k]*M[k][j])//prev
        prev=M[k][k]
    return sign*M[n-1][n-1]
minors=[1]+[det_int([r[:m] for r in G[:m]]) for m in range(1,5)]
neg=sum(1 for i in range(4) if minors[i]*minors[i+1]<0)
print(f"  integer route (Jacobi) : leading minors {minors[1:]}  -> ({4-neg},{neg})   det = {det_int(G)}")
print("  -> the SAME exact fact reached three ways: typed, floated, and derived.")
print("     Only the third can fail if the mathematics changes. It is also the cheapest.")

# ===========================================================================
hdr(4, "Block F, shipped unmarked in the appendix, prints a refuted conclusion")
# ===========================================================================
PHI=(1+5**.5)/2; om=np.exp(1j*np.pi/3)
bad=max(abs(abs(k+l*om)**2-(k*k+k*l+l*l)) for k in range(-6,7) for l in range(-6,7))
print(f"  block F item 4: 'max error over 169 lattice points: {bad:.2e} -> EXACT'")
worst_int=max(abs((k*k+k*l+l*l)-(k*k+k*l+l*l)) for k in range(-6,7) for l in range(-6,7))
print(f"                  the same statement in integers has deviation {worst_int} -- exactly zero.")
print(f"                  block F calls {bad:.0e} 'EXACT'. It is float64 noise standing in for 0.")
za,zb=(2+0j)+1*om,(1+0j)+2*om
Ta,Tb,Tab=abs(za)**2,abs(zb)**2,abs(za*zb)**2
print(f"\n  block F item 8: T(w1)={Ta:.4f} T(w2)={Tb:.4f} T(w1w2)={Tab:.4f}, "
      f"multiplicative within 1e-9: {abs(Tab-Ta*Tb)<1e-9}")
def eis_mul(x,y): a,b=x;c,d=y; return (a*c-b*d,a*d+b*c+b*d)
def N(w): k,l=w; return k*k+k*l+l*l
print(f"                  in integers: N(2,1)={N((2,1))}, N(1,2)={N((1,2))}, "
      f"N(product)={N(eis_mul((2,1),(1,2)))}, product of norms={N((2,1))*N((1,2))}  -- equal, exactly.")
print("\n  block F line 52-53 then PRINTS:")
print('     "=> squaring a seed SQUARES its triangulation number. escape count = GC refinement depth."')
print("  The tower's own section 5 refutes the second half with 13 != 9, and the final")
print("  ledger records 'Shifted Multibrot equals GC refinement -- false'. Block F ships")
print("  in the appendix with no STALE marker and no cross-reference to its own refutation.")

# ===========================================================================
hdr(5, "Import-time side effects: what `import` costs before you call anything")
# ===========================================================================
tracemalloc.start(); t0=time.perf_counter()
def base_dirac_basis():
    out=[]
    for p in range(16):
        for q in range(p,16):
            for val in (1.0+0j, 1.0j):
                B=np.zeros((16,16),complex); B[p,q]=val; B[q,p]=val
                D=np.zeros((32,32),complex); D[:16,16:]=B; D[16:,:16]=B.conj().T
                out.append(D)
    return np.asarray(out)
DBASE=base_dirac_basis(); ms=(time.perf_counter()-t0)*1e3
cur,peak=tracemalloc.get_traced_memory(); tracemalloc.stop()
print(f"  block D line 340:  DBASE = base_dirac_basis()   <- at MODULE SCOPE")
print(f"  cost paid on import, before any test runs: {ms:.0f} ms, "
      f"{DBASE.nbytes/1e6:.2f} MB array, {peak/1e6:.1f} MB peak")
print(f"  shape {DBASE.shape}, dtype {DBASE.dtype}")
print("  block C imports block A, which imports block D -> the suite pays this to read a JSON.")

# ===========================================================================
hdr(6, "The 272-space and the rank sandwich, recomputed here")
# ===========================================================================
STATES=[]
for _a,_s in [(1,1),(-1,-1),(-1,1),(1,-1)]:
    for _w in (1,-1):
        for _c in range(4): STATES.append((_a,_s,_w,_c))
IDX={st:i for i,st in enumerate(STATES)}
JPERM=np.zeros((32,32),complex)
for i,(a,s,w,c) in enumerate(STATES): JPERM[IDX[(-a,s,w,c)],i]=1.0
def qmat(q):
    q0,q1,q2,q3=q
    return np.array([[q0+1j*q1,q2+1j*q3],[-q2+1j*q3,q0-1j*q1]],complex)
def opposite(A): return JPERM@A.T@JPERM
def pi_extended(e):
    r,lam,q,m=e; Q=qmat(q); A=np.zeros((32,32),complex)
    for c in range(4):
        ii=[IDX[(1,1,1,c)],IDX[(1,1,-1,c)]]; A[np.ix_(ii,ii)]=Q
        A[IDX[(1,-1,1,c)],IDX[(1,-1,1,c)]]=lam
        A[IDX[(1,-1,-1,c)],IDX[(1,-1,-1,c)]]=np.conj(lam)
    for s in (1,-1):
        for w in (1,-1):
            ii=[IDX[(-1,s,w,c)] for c in range(3)]; A[np.ix_(ii,ii)]=m
            A[IDX[(-1,s,w,3)],IDX[(-1,s,w,3)]]=r
    return A
def constraint_matrix(Db,A,B):
    C=Db@A-A@Db; Y=C@B-B@C; F=Y.reshape(len(Db),-1)
    X=np.concatenate([F.real.T,F.imag.T],axis=0); Rr=np.rint(X)
    return Rr.astype(np.int64), float(np.max(np.abs(X-Rr)))
def rank_mod(M,p):
    A=np.mod(M,p).astype(np.int64,copy=True); rows,cols=A.shape; r=0
    for c in range(cols):
        nz=np.flatnonzero(A[r:,c])
        if nz.size==0: continue
        i=r+int(nz[0])
        if i!=r: A[[r,i]]=A[[i,r]]
        inv=pow(int(A[r,c]),-1,p); A[r,c:]=(A[r,c:]*inv)%p
        if r+1<rows:
            f=A[r+1:,c].copy(); m=f!=0
            if np.any(m):
                t=np.where(m)[0]+r+1; A[t,c:]=(A[t,c:]-f[m,None]*A[r,c:])%p
        r+=1
        if r==min(rows,cols): break
    return r
rng=np.random.default_rng(20260803)
def draw():
    return (int(rng.integers(-2,3)), complex(int(rng.integers(-2,3)),int(rng.integers(-2,3))),
            rng.integers(-2,3,size=4).astype(float),
            rng.integers(-2,3,size=(3,3))+1j*rng.integers(-2,3,size=(3,3)))
parts, residuals = [], []
for _ in range(2):
    A=pi_extended(draw()); B=opposite(pi_extended(draw()))
    X,res=constraint_matrix(DBASE,A,B); parts.append(X); residuals.append(res)
X=np.concatenate(parts,axis=0)
print(f"  base Dirac space dim_R : {len(DBASE)}  (= 2 * 16*17/2 = 272)")
print(f"  constraint matrix shape: {X.shape}")
print(f"  integrality residual   : {max(residuals)!r}  <- block D accepts anything < 1e-10;")
print(f"                            the true value is exactly 0.0, so the entries ARE integers")
print(f"                            and the whole rank step is exact, not 'within tolerance'.")
for p in (1009,10007,65521):
    print(f"  rank over F_{p:<6}      : {rank_mod(X,p)}   -> nullity <= {272-rank_mod(X,p)}")
print("  -> the headline 272 -> 16 sandwich reproduces here, and its float step has")
print("     residual 0.0. Reporting it as '< 1e-10' understates a result that is exact.")
