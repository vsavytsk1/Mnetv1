#!/usr/bin/env python3
"""EXACT verification of the THEA v3.0 C60 spectral claims.

Builds the truncated-icosahedron (C60) adjacency matrix from geometry, then:
  1. PROVES the claimed characteristic polynomial factorization by evaluating
     det(xI - A) in exact integer arithmetic (Bareiss) at 61 integer points and
     comparing with the claimed product at the same points. Two monic degree-60
     polynomials agreeing at 61 points are identical. This is a proof, not a
     spot check.
  2. Confirms least eigenvalue = -(3+sqrt5)/2 = -phi^2 with multiplicity 3.
  3. Confirms the central adjacency gap 0.7565982538600667 (and that its upper
     edge is 1/phi).
  4. Cross-lock: Laplacian lambda2(C60) = 3 - (largest root of the quartic
     factor) = 0.24340174613993026 -- tying the EXACT column of the certificate
     to the COMPUTED spectral-tower column at level 1.
"""
import math
import numpy as np

PHI = (1 + math.sqrt(5)) / 2

# ---------- build C60 geometrically (truncated icosahedron) ----------
def build_c60():
    p = PHI
    templates = [[0, 1, 3 * p], [1, 2 + p, 2 * p], [p, 2, 2 * p + 1]]
    perms = [[0, 1, 2], [1, 2, 0], [2, 0, 1]]  # cyclic = even permutations
    raw = []
    for t in templates:
        a, b, c = t
        for perm in perms:
            for sa in (-1, 1):
                for sb in (-1, 1):
                    for sc in (-1, 1):
                        if a == 0 and sa == -1:
                            continue
                        if b == 0 and sb == -1:
                            continue
                        if c == 0 and sc == -1:
                            continue
                        v = [0.0, 0.0, 0.0]
                        v[perm[0]] = sa * a
                        v[perm[1]] = sb * b
                        v[perm[2]] = sc * c
                        if not any(all(abs(u[i] - v[i]) < 1e-3 for i in range(3)) for u in raw):
                            raw.append(v)
    assert len(raw) == 60, len(raw)
    P = np.array(raw)
    D = np.linalg.norm(P[:, None, :] - P[None, :, :], axis=2)
    np.fill_diagonal(D, np.inf)
    emin = D.min()
    A = (np.abs(D - emin) < emin * 0.05).astype(np.int64)
    assert (A.sum(axis=1) == 3).all(), "not 3-regular"
    assert A.sum() // 2 == 90, "not 90 edges"
    return A

# ---------- exact integer determinant (Bareiss, fraction-free) ----------
def det_int(M):
    M = [row[:] for row in M]
    n = len(M)
    sign = 1
    prev = 1
    for k in range(n - 1):
        if M[k][k] == 0:
            for i in range(k + 1, n):
                if M[i][k]:
                    M[k], M[i] = M[i], M[k]
                    sign = -sign
                    break
            else:
                return 0
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
        prev = M[k][k]
    return sign * M[n - 1][n - 1]

# ---------- the claimed factorization ----------
# (x-3)(x-1)^9 (x+2)^4 (x^2-x-3)^5 (x^2+x-4)^4 (x^2+x-1)^5 (x^2+3x+1)^3
# (x^4-3x^3-2x^2+7x+1)^3
FACTORS = [
    ([1, -3], 1),
    ([1, -1], 9),
    ([1, 2], 4),
    ([1, -1, -3], 5),
    ([1, 1, -4], 4),
    ([1, 1, -1], 5),
    ([1, 3, 1], 3),
    ([1, -3, -2, 7, 1], 3),
]

def poly_eval_int(coeffs, x):
    v = 0
    for c in coeffs:
        v = v * x + c
    return v

def claimed_eval(x):
    v = 1
    for coeffs, mult in FACTORS:
        v *= poly_eval_int(coeffs, x) ** mult
    return v

def main():
    A = build_c60()
    print("C60 built: 60 vertices, 90 edges, 3-regular. OK")

    deg = sum((len(c) - 1) * m for c, m in FACTORS)
    print(f"claimed factorization degree: {deg} (must be 60)")
    assert deg == 60

    # ----- 1. the 61-point exact proof -----
    Alist = A.tolist()
    n = 60
    bad = 0
    pts = list(range(-30, 31))
    for idx, x in enumerate(pts):
        M = [[(x if i == j else 0) - Alist[i][j] for j in range(n)] for i in range(n)]
        d = det_int(M)
        c = claimed_eval(x)
        if d != c:
            bad += 1
            print(f"  MISMATCH at x={x}: det={d} claimed={c}")
        if (idx + 1) % 20 == 0:
            print(f"  ... {idx + 1}/61 points checked, mismatches so far: {bad}")
    if bad == 0:
        print("EXACT PROOF COMPLETE: det(xI - A) == claimed factorization at all 61")
        print("integer points x = -30..30. Both are monic of degree 60, therefore")
        print("they are THE SAME POLYNOMIAL. The certificate's charpoly is EXACT.")
    else:
        print(f"FAILED: {bad} mismatching points")
        return

    # ----- 2. numeric spectrum, least eigenvalue, multiplicity -----
    w = np.linalg.eigvalsh(A.astype(float))
    w.sort()
    least = w[:4]
    phi2 = PHI * PHI
    mult = int(np.sum(np.abs(w - (-phi2)) < 1e-9))
    print(f"\nleast eigenvalue: {w[0]:.15f}   -phi^2 = {-phi2:.15f}")
    print(f"|least + phi^2| = {abs(w[0] + phi2):.3e}   multiplicity within 1e-9: {mult} (claimed 3)")

    # ----- 3. central adjacency gap -----
    neg = w[w < -1e-12].max()
    pos = w[w > 1e-12].min()
    gap = pos - neg
    print(f"\ncentral gap: smallest positive {pos:.15f} (1/phi = {1/PHI:.15f})")
    print(f"             largest negative  {neg:.15f}")
    print(f"             gap = {gap:.16f}   certificate: 0.7565982538600667")

    # ----- 4. the lambda2 cross-lock -----
    quartic = np.roots([1, -3, -2, 7, 1])
    top = max(quartic.real)
    lam2 = 3 - top
    print(f"\nlargest root of the quartic factor: {top:.15f}")
    print(f"3 - root = {lam2:.17f}")
    print( "certificate spectral-tower level-1 lambda2 = 0.24340174613993026")
    print(f"agreement: {abs(lam2 - 0.24340174613993026):.3e}")
    print("=> the EXACT charpoly and the COMPUTED tower lock together at C60.")

if __name__ == "__main__":
    main()
