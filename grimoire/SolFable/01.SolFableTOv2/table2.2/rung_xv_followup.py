#!/usr/bin/env python3
"""Follow-up: are the two 16-dimensional spaces the same subspace, and what
are the extra 16 directions that survive the unital chi = lambda action?"""
from __future__ import annotations

import json
from typing import Dict, List

import numpy as np
import sympy as sp

import rung_xv_irreducible as K


def null_space(rule: str) -> np.ndarray:
    """Return the exact order-one space as an array of 32x32 matrices."""
    basis = K.algebra_basis(rule)
    rng = np.random.default_rng(31415926)
    blocks = []
    for _ in range(4):
        A = K.pi(K.rand_elem(rng, rule), rule)
        B = K.opposite(K.pi(K.rand_elem(rng, rule), rule))
        blocks.append(K.constraint_matrix(A, B))
    X = np.concatenate(blocks, axis=0)
    _, pivot_rows = K.rref_mod(X, 2147483647)
    P = sp.Matrix(X[pivot_rows, :].tolist())
    vecs = []
    for v in P.nullspace():
        den = sp.ilcm(*[sp.Rational(x).q for x in v])
        w = np.array([int(sp.Rational(x) * den) for x in v], dtype=float)
        vecs.append(w)
    return np.array(vecs)


def as_real_vectors(coeffs: np.ndarray) -> np.ndarray:
    """Flatten each D = sum c_j D_j into a real vector for span comparison."""
    out = []
    for c in coeffs:
        D = np.tensordot(c, K.DBASE, axes=(0, 0))
        out.append(np.concatenate([D.real.ravel(), D.imag.ravel()]))
    return np.array(out)


def span_equal(a: np.ndarray, b: np.ndarray) -> Dict[str, object]:
    A, B = as_real_vectors(a), as_real_vectors(b)
    ra = np.linalg.matrix_rank(A, tol=1e-9)
    rb = np.linalg.matrix_rank(B, tol=1e-9)
    rab = np.linalg.matrix_rank(np.vstack([A, B]), tol=1e-9)
    return {"rank_A": int(ra), "rank_B": int(rb), "rank_union": int(rab),
            "identical_subspace": bool(ra == rb == rab)}


def support_report(coeffs: np.ndarray, label: str) -> Dict[str, object]:
    """Which (particle-left, particle-right) state pairs does the space touch?"""
    kinds = {"quark_diagonal": 0, "lepton_diagonal": 0, "quark_lepton_mixing": 0, "other": 0}
    for c in coeffs:
        D = np.tensordot(c, K.DBASE, axes=(0, 0))
        for i, j in np.argwhere(np.abs(D[:16, 16:]) > 1e-9):
            ci = K.STATES[i][3]
            cj = K.STATES[16 + j][3]
            if ci < 3 and cj < 3:
                kinds["quark_diagonal" if ci == cj else "other"] += 1
            elif ci == 3 and cj == 3:
                kinds["lepton_diagonal"] += 1
            else:
                kinds["quark_lepton_mixing"] += 1
    return {"label": label, "dimension": int(len(coeffs)), "block_support_counts": kinds}


def yukawa_check(coeffs: np.ndarray) -> Dict[str, object]:
    """Does the tower's physical_yukawa_basis span this space?"""
    out: List[np.ndarray] = []
    for typ in ("q", "l"):
        colors = range(3) if typ == "q" else [3]
        for wl in range(2):
            for wr in range(2):
                for imag in (False, True):
                    B = np.zeros((16, 16), complex)
                    val = 1j if imag else 1.0
                    for c in colors:
                        pl, pr = wl * 4 + c, 8 + wr * 4 + c
                        B[pl, pr] = val
                        B[pr, pl] = val
                    D = np.zeros((32, 32), complex)
                    D[:16, 16:] = B
                    D[16:, :16] = B.conj().T
                    out.append(np.concatenate([D.real.ravel(), D.imag.ravel()]))
    Y = np.array(out)
    S = as_real_vectors(coeffs)
    return {
        "yukawa_directions": int(len(Y)),
        "yukawa_rank": int(np.linalg.matrix_rank(Y, tol=1e-9)),
        "space_rank": int(np.linalg.matrix_rank(S, tol=1e-9)),
        "union_rank": int(np.linalg.matrix_rank(np.vstack([Y, S]), tol=1e-9)),
        "yukawas_span_the_space": bool(
            np.linalg.matrix_rank(np.vstack([Y, S]), tol=1e-9)
            == np.linalg.matrix_rank(S, tol=1e-9) == np.linalg.matrix_rank(Y, tol=1e-9)
        ),
    }


def main() -> None:
    n_free = null_space("free_real")
    n_zero = null_space("zero")
    n_lam = null_space("lambda")
    n_bar = null_space("lambda_bar")

    receipt = {
        "span_free_real_vs_zero": span_equal(n_free, n_zero),
        "span_lambda_vs_lambda_bar": span_equal(n_lam, n_bar),
        "support": [
            support_report(n_free, "R + A_F  (chi = free real, unital, dim 25)"),
            support_report(n_zero, "A_F      (chi = 0, NON-unital, dim 24)"),
            support_report(n_lam, "A_F      (chi = lambda, unital, dim 24)"),
        ],
        "yukawa_span_of_16": yukawa_check(n_free),
        "yukawa_inside_32": yukawa_check(n_lam),
    }
    print(json.dumps(receipt, indent=2))
    with open("/home/claude/rung_xv_followup.json", "w") as f:
        json.dump(receipt, f, indent=2)


if __name__ == "__main__":
    main()
