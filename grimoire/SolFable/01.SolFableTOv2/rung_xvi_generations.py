#!/usr/bin/env python3
"""RUNG XVI -- three generations. Does the bit survive?

Task 6 of the Rung XV sprint. Question: the one-generation kernel gives
dim_R D = 16 for the unit-completed action and 32 for the unital chi = lambda
action. Is that gap an artifact of the one-generation bimodule, or structural?

The three-generation bimodule is H_3 = H_F (x) C^3, index 3*i + g, with the
algebra acting diagonally on the generation index:

    pi_3(a) = pi(a) (x) I_3,   gamma_3 = gamma (x) I_3,
    J_3     = (P (x) I_3) . conj

THE DECOUPLING LEMMA  (EXACT)
-----------------------------
Write D = sum_{a,b} X_ab (x) E_ab. Because pi_3 and pi_3^op are both of the
form (.) (x) I_3, the double commutator is

    [[D, pi_3(a)], pi_3^op(b)] = sum_{a,b} [[X_ab, pi(a)], pi^op(b)] (x) E_ab

and the E_ab are linearly independent. So the order-one condition holds iff it
holds for every generation block separately. Generations do not mix.

The KO-6 structure conditions likewise decouple:
    {D, gamma_3} = 0     <=>  {X_ab, gamma} = 0     for all a,b
    D J_3 = J_3 D        <=>  X_ab P = P conj(X_ab) for all a,b
    D* = D               <=>  X_ab^dagger = X_ba          (couples a<->b only)

Hence, with
    V   = { X : {X,gamma}=0, XP=P conj(X), order-one }   (NO hermiticity)
    V_+ = hermitian part of V  = the one-generation answer

    dim_R D_3(A) = 3 * dim V_+  +  3 * dim V
                   ^^^^^^^^^^^     ^^^^^^^^^
                   a = b blocks    a < b blocks (a > b determined by dagger)

Arithmetic check with no order-one condition imposed:
    V_base = 512 (B in M_16(C) free), V_base_+ = 272
    => 3*272 + 3*512 = 2352 = 2 * (48*49/2)   the exact 96-state base. OK.

So the whole three-generation question reduces to computing dim V, which is a
512-column problem, not a 2352-column one. Exact rank sandwich as before.
"""
from __future__ import annotations

import json
from typing import Dict, List

import numpy as np
import sympy as sp

import rung_xv_irreducible as K

NGEN = 3


# ---------------------------------------------------------------------------
# I. The non-hermitian base V_base: {X, gamma} = 0 and X P = P conj(X)
# ---------------------------------------------------------------------------

def nonhermitian_base() -> np.ndarray:
    """X = [[0, B], [conj(B), 0]] with B in M_16(C) free.  dim_R = 512."""
    out: List[np.ndarray] = []
    for p in range(16):
        for q in range(16):
            for val in (1.0 + 0.0j, 1.0j):
                B = np.zeros((16, 16), complex)
                B[p, q] = val
                X = np.zeros((32, 32), complex)
                X[:16, 16:] = B
                X[16:, :16] = B.conjugate()
                out.append(X)
    return np.asarray(out)


VBASE = nonhermitian_base()


def base_audit() -> Dict[str, object]:
    return {
        "dim_V_base": int(len(VBASE)),
        "max_gamma_anticommutator": max(float(np.max(np.abs(X @ K.GAMMA + K.GAMMA @ X))) for X in VBASE),
        "max_reality_residual": max(float(np.max(np.abs(X @ K.JPERM - K.JPERM @ X.conjugate()))) for X in VBASE),
        "hermitian_subspace_dim": 272,
        "three_generation_base_check": 3 * 272 + 3 * len(VBASE),
        "expected_2x48x49over2": 2 * (48 * 49 // 2),
        "lemma_arithmetic_ok": bool(3 * 272 + 3 * len(VBASE) == 2 * (48 * 49 // 2)),
    }


# ---------------------------------------------------------------------------
# II. Exact rank sandwich on V
# ---------------------------------------------------------------------------

def constraint_matrix_V(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    C = VBASE @ A - A @ VBASE
    Y = C @ B - B @ C
    F = Y.reshape(len(VBASE), -1)
    X = np.concatenate([F.real.T, F.imag.T], axis=0)
    r = np.rint(X)
    if float(np.max(np.abs(X - r))) > 1e-9:
        raise RuntimeError("non-integer constraint matrix")
    return r.astype(np.int64)


def dim_V(rule: str, primes=(10007, 65521, 2147483647)) -> Dict[str, object]:
    basis = K.algebra_basis(rule)
    ops = [K.opposite(A) for A in basis]

    rng = np.random.default_rng(31415926)
    blocks = []
    for _ in range(4):
        A = K.pi(K.rand_elem(rng, rule), rule)
        B = K.opposite(K.pi(K.rand_elem(rng, rule), rule))
        blocks.append(constraint_matrix_V(A, B))
    X = np.concatenate(blocks, axis=0)

    ranks, pivots = {}, None
    for p in primes:
        r, pr = K.rref_mod(X, p)
        ranks[str(p)] = r
        if pivots is None or r > len(pivots):
            pivots = pr
    rank_lb = max(ranks.values())

    P = sp.Matrix(X[pivots, :].tolist())
    null = P.nullspace()
    vecs = []
    for v in null:
        den = sp.ilcm(*[sp.Rational(x).q for x in v])
        w = [int(sp.Rational(x) * den) for x in v]
        g = 0
        for x in w:
            g = sp.igcd(g, abs(x))
        vecs.append([x // g for x in w] if g else w)

    # exact verification against every algebra-basis pair
    worst = 0.0
    mats = []
    for w in vecs:
        Xm = np.tensordot(np.array(w, dtype=float), VBASE, axes=(0, 0))
        mats.append(Xm)
        for A in basis:
            C = Xm @ A - A @ Xm
            for B in ops:
                worst = max(worst, float(np.max(np.abs(C @ B - B @ C))))

    # split V into hermitian / anti-hermitian parts under X -> X^dagger
    dim = len(vecs)
    if dim:
        flat = np.array([np.concatenate([m.real.ravel(), m.imag.ravel()]) for m in mats])
        flat_d = np.array([np.concatenate([m.conj().T.real.ravel(), m.conj().T.imag.ravel()]) for m in mats])
        # X + X^dagger spans the hermitian part
        herm = np.linalg.matrix_rank(flat + flat_d, tol=1e-8)
        anti = np.linalg.matrix_rank(flat - flat_d, tol=1e-8)
    else:
        herm = anti = 0

    return {
        "rule": rule,
        "modular_ranks": ranks,
        "rank_lower_bound": rank_lb,
        "nullity_upper_bound": len(VBASE) - rank_lb,
        "dim_V": dim,
        "max_exact_residual": worst,
        "sandwich_closed": bool(worst == 0.0 and dim == len(VBASE) - rank_lb),
        "dim_V_hermitian": int(herm),
        "dim_V_antihermitian": int(anti),
        "status": "EXACT" if (worst == 0.0 and dim == len(VBASE) - rank_lb) else "COMPUTED",
    }


# ---------------------------------------------------------------------------
# III. Direct 96-state spot check that the lemma is not a coding fiction
# ---------------------------------------------------------------------------

def lift(X_blocks: Dict[tuple, np.ndarray]) -> np.ndarray:
    D = np.zeros((32 * NGEN, 32 * NGEN), complex)
    for (a, b), Xm in X_blocks.items():
        E = np.zeros((NGEN, NGEN), complex)
        E[a, b] = 1.0
        D += np.kron(Xm, E)
    return D


def spot_check(rule: str, trials: int = 6) -> Dict[str, object]:
    """Build random 3-generation D from the lemma and test at full 96 states."""
    v = dim_V(rule)
    basis = K.algebra_basis(rule)
    ops = [K.opposite(A) for A in basis]

    rng = np.random.default_rng(5551212)
    blocks = []
    for _ in range(4):
        A = K.pi(K.rand_elem(rng, rule), rule)
        B = K.opposite(K.pi(K.rand_elem(rng, rule), rule))
        blocks.append(constraint_matrix_V(A, B))
    Xc = np.concatenate(blocks, axis=0)
    _, piv = K.rref_mod(Xc, 2147483647)
    P = sp.Matrix(Xc[piv, :].tolist())
    Vmats = []
    for vec in P.nullspace():
        den = sp.ilcm(*[sp.Rational(x).q for x in vec])
        w = np.array([int(sp.Rational(x) * den) for x in vec], dtype=float)
        Vmats.append(np.tensordot(w, VBASE, axes=(0, 0)))

    I3 = np.eye(NGEN)
    G3 = np.kron(K.GAMMA, I3)
    P3 = np.kron(K.JPERM, I3)
    A3 = [np.kron(A, I3) for A in basis]
    O3 = [np.kron(B, I3) for B in ops]

    worst_o1 = worst_struct = 0.0
    for _ in range(trials):
        Xb: Dict[tuple, np.ndarray] = {}
        for a in range(NGEN):
            for b in range(a, NGEN):
                M = sum(float(rng.normal()) * m for m in Vmats)
                if a == b:
                    M = M + M.conj().T           # force hermitian on the diagonal
                    Xb[(a, a)] = M
                else:
                    Xb[(a, b)] = M
                    Xb[(b, a)] = M.conj().T
        D = lift(Xb)
        worst_struct = max(
            worst_struct,
            float(np.max(np.abs(D - D.conj().T))),
            float(np.max(np.abs(D @ G3 + G3 @ D))),
            float(np.max(np.abs(D @ P3 - P3 @ D.conjugate()))),
        )
        for A in A3:
            C = D @ A - A @ D
            for B in O3:
                worst_o1 = max(worst_o1, float(np.max(np.abs(C @ B - B @ C))))

    return {
        "trials": trials,
        "max_structure_residual_96": worst_struct,
        "max_order_one_residual_96": worst_o1,
        "lemma_confirmed_at_96_states": bool(worst_o1 < 1e-9 and worst_struct < 1e-9),
        "dim_V_used": v["dim_V"],
    }


# ---------------------------------------------------------------------------
# IV. Moduli at three generations
# ---------------------------------------------------------------------------

def moduli_3gen(rule: str) -> Dict[str, object]:
    from rung_xv_moduli import lie_algebra_basis

    rng = np.random.default_rng(8675309)
    blocks = []
    for _ in range(4):
        A = K.pi(K.rand_elem(rng, rule), rule)
        B = K.opposite(K.pi(K.rand_elem(rng, rule), rule))
        blocks.append(constraint_matrix_V(A, B))
    Xc = np.concatenate(blocks, axis=0)
    _, piv = K.rref_mod(Xc, 2147483647)
    P = sp.Matrix(Xc[piv, :].tolist())
    Vmats = []
    for vec in P.nullspace():
        den = sp.ilcm(*[sp.Rational(x).q for x in vec])
        w = np.array([int(sp.Rational(x) * den) for x in vec], dtype=float)
        Vmats.append(np.tensordot(w, VBASE, axes=(0, 0)))

    Xb: Dict[tuple, np.ndarray] = {}
    for a in range(NGEN):
        for b in range(a, NGEN):
            M = sum(float(rng.normal()) * m for m in Vmats)
            if a == b:
                Xb[(a, a)] = M + M.conj().T
            else:
                Xb[(a, b)] = M
                Xb[(b, a)] = M.conj().T
    D = lift(Xb)

    I3 = np.eye(NGEN)
    P3 = np.kron(K.JPERM, I3)
    tangents = []
    for A in lie_algebra_basis(rule):
        A3 = np.kron(A, I3)
        X = A3 + P3 @ A3.conjugate() @ P3
        T = X @ D - D @ X
        tangents.append(np.concatenate([T.real.ravel(), T.imag.ravel()]))
    orbit = int(np.linalg.matrix_rank(np.array(tangents), tol=1e-8))
    return {"gauge_generators": len(tangents), "orbit_dimension": orbit}


def main() -> None:
    receipt: Dict[str, object] = {
        "artifact": "RUNG XVI -- three generations (sprint task 6)",
        "decoupling_lemma": {
            "statement": "pi_3 = pi (x) I_3 and pi_3^op = pi^op (x) I_3, so the "
                         "order-one condition holds block-by-block in the "
                         "generation index. Generations do not mix.",
            "status": "EXACT",
            "consequence": "dim D_3 = 3*dim V_+ + 3*dim V",
        },
        "base_audit": base_audit(),
        "per_rule": {},
    }
    for rule in ("free_real", "zero", "lambda", "lambda_bar"):
        v = dim_V(rule)
        one_gen = v["dim_V_hermitian"]
        d3 = 3 * one_gen + 3 * v["dim_V"]
        mod = moduli_3gen(rule)
        receipt["per_rule"][rule] = {
            "dim_V": v["dim_V"],
            "dim_V_hermitian_equals_one_generation_answer": one_gen,
            "dim_V_antihermitian": v["dim_V_antihermitian"],
            "dim_D_three_generations": d3,
            "moduli_three_generations": d3 - mod["orbit_dimension"],
            "gauge_orbit_dimension": mod["orbit_dimension"],
            "sandwich": v["status"],
            "modular_ranks": v["modular_ranks"],
            "max_exact_residual": v["max_exact_residual"],
        }
    receipt["spot_check_lambda"] = spot_check("lambda")
    receipt["spot_check_zero"] = spot_check("zero")

    d16 = receipt["per_rule"]["zero"]["dim_D_three_generations"]
    d32 = receipt["per_rule"]["lambda"]["dim_D_three_generations"]
    receipt["verdict"] = {
        "unit_completed_branch": d16,
        "unital_lambda_branch": d32,
        "gap_survives_three_generations": bool(d16 != d32),
        "ratio": d32 / d16 if d16 else None,
        "reading": "generation count multiplies both branches by the same "
                   "structure; it cannot decide the unitality bit",
    }
    print(json.dumps(receipt, indent=2, default=str))
    with open("/home/claude/rung_xvi_generations.json", "w") as f:
        json.dump(receipt, f, indent=2, default=str)


if __name__ == "__main__":
    main()
