#!/usr/bin/env python3
"""RUNG XV -- the irreducible choice.

Thesis under test
-----------------
Rung X of SOL FABLE LaTeX Tower v2.1 reports a "source specification fork":
the source-aligned model (R_lbar + C + H + M3(C), dim 25) yields
dim_R D(A) = 16, while a natural standard-A_F completion yields 32.
The tower marks this OPEN and calls it a representation fork.

This kernel shows the fork is NOT a continuum of conventions. Every
representation in Code block I -- pi_extended, pi_canonical,
pi_affine_fixed_identity -- is the SAME 32x32 matrix except for four
diagonal entries: the states (a=-1, s=+-1, w=+-1, c=3), i.e. the
anti-lepton colour slot. The entire fork is one scalar chi.

And chi is not free. chi must be an algebra character of A_F. By
Wedderburn, H and M3(C) are simple noncommutative algebras, so they admit
no nonzero homomorphism to the commutative algebra C. Hence every
character of A_F kills them, and restricts on the C summand to a
*-endomorphism of C: identity or conjugation. Therefore

    chi in {0, lambda, conj(lambda)}   -- exactly three options
    unital => chi in {lambda, conj(lambda)} -- exactly two

The "identity action" of the source prose is a fourth thing that is not a
character at all: pi(0) = I != 0.

So the irreducible choice is a 2-element set, not an open convention.
This script computes dim_R D(A) for every member of that set, exactly.

Status grammar (THEA v3.0 / tower v2.1):
    EXACT      integer / finite-field certificate inside the declared model
    COMPUTED   finite arithmetic with printed residual
    OPEN       not decided here

Method for every dimension reported below
-----------------------------------------
1. rank_Fp(X) = r for several primes p on an integer constraint matrix X
   built from generic algebra elements  =>  rank_Q(X) >= r  =>  nullity <= 272-r.
2. Exact rational nullspace of the r pivot rows  =>  a space of dim 272-r.
3. Every basis vector of that space is verified with EXACT Gaussian-integer
   arithmetic against ALL algebra-basis order-one constraints => nullity >= 272-r.
Bounds meet. The reported dimension is EXACT inside the declared bimodule.
"""
from __future__ import annotations

import json
import itertools
from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

import numpy as np
import sympy as sp

# ---------------------------------------------------------------------------
# I. The finite bimodule -- DECLARED, not derived. This is the real input.
# ---------------------------------------------------------------------------
# 32 = 2 (particle/antiparticle a) x 2 (chirality s) x 2 (weak w) x 4 (colour c)
# c in {0,1,2} are the three quark colours; c = 3 is the lepton slot.
# Lepton-as-fourth-colour is put in HERE, at the first line, by hand.

STATES: List[Tuple[int, int, int, int]] = []
for _a, _s in [(1, 1), (-1, -1), (-1, 1), (1, -1)]:
    for _w in (1, -1):
        for _c in range(4):
            STATES.append((_a, _s, _w, _c))
INDEX = {st: i for i, st in enumerate(STATES)}

GAMMA = np.diag([a * s for a, s, w, c in STATES]).astype(complex)
JPERM = np.zeros((32, 32), complex)
for _i, (_a, _s, _w, _c) in enumerate(STATES):
    JPERM[INDEX[(-_a, _s, _w, _c)], _i] = 1.0

ANTILEPTON_SLOTS = [INDEX[(-1, s, w, 3)] for s in (1, -1) for w in (1, -1)]


def base_dirac_basis() -> np.ndarray:
    """272 real directions: D=D*, {D,gamma}=0, DJ=JD. EXACT count 2*16*17/2."""
    out: List[np.ndarray] = []
    for p in range(16):
        for q in range(p, 16):
            for val in (1.0 + 0.0j, 1.0j):
                B = np.zeros((16, 16), complex)
                B[p, q] = val
                B[q, p] = val
                D = np.zeros((32, 32), complex)
                D[:16, 16:] = B
                D[16:, :16] = B.conj().T
                out.append(D)
    return np.asarray(out)


DBASE = base_dirac_basis()


def opposite(A: np.ndarray) -> np.ndarray:
    return JPERM @ A.T @ JPERM


# ---------------------------------------------------------------------------
# II. The representation, with the anti-lepton character as the ONLY knob
# ---------------------------------------------------------------------------

def qmat(q: Sequence[complex]) -> np.ndarray:
    q0, q1, q2, q3 = q
    return np.array(
        [[q0 + 1j * q1, q2 + 1j * q3], [-q2 + 1j * q3, q0 - 1j * q1]], complex
    )


def quat_mul(x, y):
    a0, a1, a2, a3 = x
    b0, b1, b2, b3 = y
    return (
        a0 * b0 - a1 * b1 - a2 * b2 - a3 * b3,
        a0 * b1 + a1 * b0 + a2 * b3 - a3 * b2,
        a0 * b2 - a1 * b3 + a2 * b0 + a3 * b1,
        a0 * b3 + a1 * b2 - a2 * b1 + a3 * b0,
    )


# chi rules: how the algebra acts on the single anti-lepton colour slot.
CHI_RULES = {
    "lambda":      lambda r, lam, q, m: lam,
    "lambda_bar":  lambda r, lam, q, m: np.conjugate(lam),
    "zero":        lambda r, lam, q, m: 0.0 + 0j,
    "free_real":   lambda r, lam, q, m: complex(r),      # needs R summand
    "identity":    lambda r, lam, q, m: 1.0 + 0j,        # the literal prose: affine
}


def pi(elem, rule: str) -> np.ndarray:
    """elem = (r, lambda, q, m). r is ignored unless rule == 'free_real'."""
    r, lam, q, m = elem
    Q = qmat(q)
    A = np.zeros((32, 32), complex)
    for c in range(4):
        # left-handed particles: SU(2) doublet in w  -> this fixes c_2
        il = [INDEX[(1, 1, 1, c)], INDEX[(1, 1, -1, c)]]
        A[np.ix_(il, il)] = Q
        # right-handed particles: lambda on w=+, conj(lambda) on w=-  -> fixes s_R
        A[INDEX[(1, -1, 1, c)], INDEX[(1, -1, 1, c)]] = lam
        A[INDEX[(1, -1, -1, c)], INDEX[(1, -1, -1, c)]] = np.conjugate(lam)
    chi = CHI_RULES[rule](r, lam, q, m)
    for s in (1, -1):
        for w in (1, -1):
            ic = [INDEX[(-1, s, w, c)] for c in range(3)]   # colour triplet -> fixes c_3
            A[np.ix_(ic, ic)] = m
            A[INDEX[(-1, s, w, 3)], INDEX[(-1, s, w, 3)]] = chi
    return A


def algebra_basis(rule: str) -> List[np.ndarray]:
    Z3 = np.zeros((3, 3), complex)
    elems = []
    if rule == "free_real":
        elems.append((1.0, 0j, (0, 0, 0, 0), Z3))
    for lam in (1.0 + 0j, 1.0j):
        elems.append((0.0, lam, (0, 0, 0, 0), Z3))
    for j in range(4):
        q = [0, 0, 0, 0]
        q[j] = 1
        elems.append((0.0, 0j, tuple(q), Z3))
    for a in range(3):
        for b in range(3):
            for z in (1.0 + 0j, 1.0j):
                m = np.zeros((3, 3), complex)
                m[a, b] = z
                elems.append((0.0, 0j, (0, 0, 0, 0), m))
    return [pi(e, rule) for e in elems]


def rand_elem(rng, rule: str):
    r = float(rng.integers(-2, 3))
    lam = complex(int(rng.integers(-2, 3)), int(rng.integers(-2, 3)))
    q = tuple(complex(int(v)) for v in rng.integers(-2, 3, size=4))
    m = rng.integers(-2, 3, size=(3, 3)) + 1j * rng.integers(-2, 3, size=(3, 3))
    return (r, lam, q, m.astype(complex))


def mul_elem(x, y):
    rx, lx, qx, mx = x
    ry, ly, qy, my = y
    return (rx * ry, lx * ly, quat_mul(qx, qy), mx @ my)


def star_elem(x):
    r, lam, q, m = x
    return (r, np.conjugate(lam), (q[0], -q[1], -q[2], -q[3]), m.conj().T)


def homomorphism_audit(rule: str, trials: int = 40) -> Dict[str, object]:
    rng = np.random.default_rng(20260805)
    unit = (1.0, 1.0 + 0j, (1, 0, 0, 0), np.eye(3, dtype=complex))
    mult, add, star, zero = 0.0, 0.0, 0.0, 0.0
    for _ in range(trials):
        x, y = rand_elem(rng, rule), rand_elem(rng, rule)
        mult = max(mult, float(np.max(np.abs(pi(mul_elem(x, y), rule) - pi(x, rule) @ pi(y, rule)))))
        xy = (x[0] + y[0], x[1] + y[1], tuple(np.add(x[2], y[2])), x[3] + y[3])
        add = max(add, float(np.max(np.abs(pi(xy, rule) - pi(x, rule) - pi(y, rule)))))
        star = max(star, float(np.max(np.abs(pi(star_elem(x), rule) - pi(x, rule).conj().T))))
    zero_el = (0.0, 0j, (0, 0, 0, 0), np.zeros((3, 3), complex))
    zero = float(np.max(np.abs(pi(zero_el, rule))))
    unital = float(np.max(np.abs(pi(unit, rule) - np.eye(32))))
    return {
        "multiplicative_residual": mult,
        "additive_residual": add,
        "star_residual": star,
        "pi_of_zero_max_abs": zero,
        "unitality_residual": unital,
        "is_star_homomorphism": bool(mult < 1e-12 and add < 1e-12 and star < 1e-12 and zero < 1e-12),
        "is_unital": bool(unital < 1e-12),
    }


# ---------------------------------------------------------------------------
# III. Exact order-one dimension by rank sandwich
# ---------------------------------------------------------------------------

def constraint_matrix(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    C = DBASE @ A - A @ DBASE
    Y = C @ B - B @ C
    F = Y.reshape(len(DBASE), -1)
    X = np.concatenate([F.real.T, F.imag.T], axis=0)
    rounded = np.rint(X)
    if float(np.max(np.abs(X - rounded))) > 1e-9:
        raise RuntimeError("non-integer constraint matrix")
    return rounded.astype(np.int64)


def rref_mod(M: np.ndarray, p: int) -> Tuple[int, List[int]]:
    """Return (rank, indices of original rows that became pivots) modulo p."""
    A = np.mod(M, p).astype(np.int64, copy=True)
    rows = list(range(A.shape[0]))
    m, n = A.shape
    r = 0
    pivot_rows: List[int] = []
    for c in range(n):
        nz = np.flatnonzero(A[r:, c])
        if nz.size == 0:
            continue
        i = r + int(nz[0])
        if i != r:
            A[[r, i]] = A[[i, r]]
            rows[r], rows[i] = rows[i], rows[r]
        inv = pow(int(A[r, c]), -1, p)
        A[r, c:] = (A[r, c:] * inv) % p
        if r + 1 < m:
            fac = A[r + 1:, c].copy()
            mask = fac != 0
            if np.any(mask):
                idx = np.where(mask)[0] + r + 1
                A[idx, c:] = (A[idx, c:] - fac[mask, None] * A[r, c:]) % p
        pivot_rows.append(rows[r])
        r += 1
        if r == m:
            break
    return r, pivot_rows


def order_one_dimension(rule: str, primes=(10007, 65521, 2147483647)) -> Dict[str, object]:
    basis = algebra_basis(rule)
    ops = [opposite(A) for A in basis]

    # generic stacked constraints
    rng = np.random.default_rng(31415926)
    blocks = []
    for _ in range(4):
        A = pi(rand_elem(rng, rule), rule)
        B = opposite(pi(rand_elem(rng, rule), rule))
        blocks.append(constraint_matrix(A, B))
    X = np.concatenate(blocks, axis=0)

    ranks = {}
    pivot_rows = None
    for p in primes:
        r, pr = rref_mod(X, p)
        ranks[str(p)] = r
        if pivot_rows is None or r > len(pivot_rows):
            pivot_rows = pr
    rank_lb = max(ranks.values())

    # exact rational nullspace of the pivot rows
    P = sp.Matrix(X[pivot_rows, :].tolist())
    null = P.nullspace()
    dim = len(null)

    # clear denominators -> primitive integer coefficient vectors
    int_vecs = []
    for v in null:
        den = sp.ilcm(*[sp.Rational(x).q for x in v]) if dim else 1
        w = [int(sp.Rational(x) * den) for x in v]
        g = 0
        for x in w:
            g = sp.igcd(g, abs(x))
        w = [x // g for x in w] if g else w
        int_vecs.append(w)

    # EXACT verification of every candidate against ALL basis-pair constraints
    worst = 0.0
    for w in int_vecs:
        D = np.tensordot(np.array(w, dtype=float), DBASE, axes=(0, 0))
        for A in basis:
            C = D @ A - A @ D
            for B in ops:
                worst = max(worst, float(np.max(np.abs(C @ B - B @ C))))
    verified = worst == 0.0

    return {
        "rule": rule,
        "algebra": ("R + C + H + M3(C)" if rule == "free_real" else "C + H + M3(C)"),
        "algebra_real_dimension": len(basis),
        "modular_ranks": ranks,
        "rank_lower_bound_over_Q": rank_lb,
        "nullity_upper_bound": 272 - rank_lb,
        "exact_nullspace_dimension": dim,
        "max_exact_residual_over_full_basis": worst,
        "sandwich_closed": bool(verified and dim == 272 - rank_lb),
        "dim_R_D": dim if (verified and dim == 272 - rank_lb) else None,
        "status": "EXACT" if (verified and dim == 272 - rank_lb) else "COMPUTED",
    }


def base_space_audit() -> Dict[str, object]:
    return {
        "dimension": int(len(DBASE)),
        "analytic_dimension_2x16x17_over_2": 2 * (16 * 17 // 2),
        "max_hermiticity_residual": max(float(np.max(np.abs(D - D.conj().T))) for D in DBASE),
        "max_gamma_anticommutator": max(float(np.max(np.abs(D @ GAMMA + GAMMA @ D))) for D in DBASE),
        "max_reality_residual": max(float(np.max(np.abs(D @ JPERM - JPERM @ D.conjugate()))) for D in DBASE),
        "J_squared_residual": float(np.max(np.abs(JPERM @ JPERM - np.eye(32)))),
        "J_gamma_anticommutator": float(np.max(np.abs(JPERM @ GAMMA + GAMMA @ JPERM))),
    }


def fork_localisation() -> Dict[str, object]:
    """Show the three source representations differ ONLY on 4 diagonal entries."""
    rng = np.random.default_rng(7)
    diffs = {}
    for a, b in itertools.combinations(["lambda", "lambda_bar", "free_real", "identity", "zero"], 2):
        support = set()
        for _ in range(30):
            e = rand_elem(rng, "free_real")
            d = pi(e, a) - pi(e, b)
            support |= set(map(tuple, np.argwhere(np.abs(d) > 1e-12)))
        diffs[f"{a}_vs_{b}"] = {
            "differing_entries": sorted(support),
            "all_on_antilepton_diagonal": all(i == j and i in ANTILEPTON_SLOTS for i, j in support),
        }
    return {
        "antilepton_slot_indices": ANTILEPTON_SLOTS,
        "pairwise": diffs,
        "claim": "every reported representation of Rung X is one 32x32 matrix "
                 "plus one scalar on four identical diagonal entries",
    }


def main() -> None:
    receipt: Dict[str, object] = {
        "artifact": "RUNG XV -- the irreducible choice",
        "base_space": base_space_audit(),
        "fork_localisation": fork_localisation(),
        "character_theorem": {
            "statement": "chi: C+H+M3(C) -> C an algebra hom => chi(H)=chi(M3(C))=0 "
                         "and chi|_C in {id, conj}. Hence chi in {0, lambda, conj(lambda)}.",
            "proof": "H and M3(C) are simple, so ker chi is 0 or the whole summand. "
                     "An injective hom into the commutative algebra C is impossible for "
                     "a noncommutative algebra. So both summands die. A unital "
                     "*-endomorphism of C is the identity or conjugation.",
            "status": "EXACT",
            "admissible_unital_characters": 2,
        },
        "homomorphism_audit": {r: homomorphism_audit(r) for r in CHI_RULES},
        "order_one_dimensions": {},
    }
    for rule in ("free_real", "lambda", "lambda_bar", "zero"):
        receipt["order_one_dimensions"][rule] = order_one_dimension(rule)
    print(json.dumps(receipt, indent=2, default=str))
    with open("/home/claude/rung_xv_receipt.json", "w") as f:
        json.dump(receipt, f, indent=2, default=str)


if __name__ == "__main__":
    main()
