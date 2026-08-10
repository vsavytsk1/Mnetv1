#!/usr/bin/env python3
"""RUNG XVI-b -- is the tower's finite triple under-constrained?

Rung XVI shows the 16 / 32 gap survives to three generations (144 / 282), so
generation count cannot decide the unitality bit. That leaves a sharper
suspicion: the tower imposes only

    D* = D,   {D, gamma} = 0,   DJ = JD,   order-one

whereas Chamseddine-Connes impose one more condition on the finite Dirac
operator -- the MASSLESS PHOTON condition: D commutes with a distinguished
complex subalgebra C_F of A_F. Physically it is what keeps the photon
massless; structurally it removes directions the order-one condition leaves
standing.

Here C_F(lambda) is the diagonal complex line

    lambda  |->  ( lambda,  diag(lambda, conj lambda) in H,  lambda * I_3 )

and the extra condition is [D, pi(c)] = 0 for every c in C_F.

The generation decoupling lemma of Rung XVI still applies verbatim, because
pi_3(c) = pi(c) (x) I_3, so the photon condition is also block-by-block.

If the gap closes here, the tower was simply missing an axiom and the whole
Rung X fork was never a fork. If it does not, the bit is real and must be
settled by physics (sprint task 5).
"""
from __future__ import annotations

import json
from typing import Dict, List

import numpy as np
import sympy as sp

import rung_xv_irreducible as K
import rung_xvi_generations as G


def photon_elements() -> List[tuple]:
    """Real basis of the diagonal complex line C_F inside A_F."""
    out = []
    for lam in (1.0 + 0j, 1.0j):
        q = (lam.real, lam.imag, 0.0, 0.0)   # diag(lam, conj lam) in H
        m = lam * np.eye(3, dtype=complex)
        out.append((lam.real, lam, q, m))
    return out


def photon_constraint(basis_space: np.ndarray, A: np.ndarray) -> np.ndarray:
    Y = basis_space @ A - A @ basis_space
    F = Y.reshape(len(basis_space), -1)
    X = np.concatenate([F.real.T, F.imag.T], axis=0)
    r = np.rint(X)
    if float(np.max(np.abs(X - r))) > 1e-9:
        raise RuntimeError("non-integer photon constraint")
    return r.astype(np.int64)


def dim_with_photon(rule: str, primes=(10007, 65521, 2147483647)) -> Dict[str, object]:
    basis = K.algebra_basis(rule)
    ops = [K.opposite(A) for A in basis]
    photons = [K.pi(e, rule) for e in photon_elements()]

    rng = np.random.default_rng(31415926)
    blocks = []
    for _ in range(4):
        A = K.pi(K.rand_elem(rng, rule), rule)
        B = K.opposite(K.pi(K.rand_elem(rng, rule), rule))
        blocks.append(G.constraint_matrix_V(A, B))
    for Pph in photons:
        blocks.append(photon_constraint(G.VBASE, Pph))
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
    mats, worst = [], 0.0
    for v in null:
        den = sp.ilcm(*[sp.Rational(x).q for x in v])
        w = np.array([int(sp.Rational(x) * den) for x in v], dtype=float)
        Xm = np.tensordot(w, G.VBASE, axes=(0, 0))
        mats.append(Xm)
        for Pph in photons:
            worst = max(worst, float(np.max(np.abs(Xm @ Pph - Pph @ Xm))))
        for A in basis:
            C = Xm @ A - A @ Xm
            for B in ops:
                worst = max(worst, float(np.max(np.abs(C @ B - B @ C))))

    dim = len(mats)
    if dim:
        flat = np.array([np.concatenate([m.real.ravel(), m.imag.ravel()]) for m in mats])
        flat_d = np.array([np.concatenate([m.conj().T.real.ravel(), m.conj().T.imag.ravel()]) for m in mats])
        herm = int(np.linalg.matrix_rank(flat + flat_d, tol=1e-8))
    else:
        herm = 0

    return {
        "rule": rule,
        "modular_ranks": ranks,
        "dim_V_with_photon": dim,
        "dim_V_hermitian_with_photon": herm,
        "one_generation_dim_D": herm,
        "three_generation_dim_D": 3 * herm + 3 * dim,
        "max_exact_residual": worst,
        "sandwich_closed": bool(worst == 0.0 and dim == len(G.VBASE) - rank_lb),
        "status": "EXACT" if (worst == 0.0 and dim == len(G.VBASE) - rank_lb) else "COMPUTED",
    }


def main() -> None:
    out = {r: dim_with_photon(r) for r in ("zero", "lambda", "lambda_bar", "free_real")}
    z, l = out["zero"], out["lambda"]
    receipt = {
        "artifact": "RUNG XVI-b -- massless-photon condition",
        "per_rule": out,
        "comparison_without_photon": {
            "zero": {"one_gen": 16, "three_gen": 144},
            "lambda": {"one_gen": 32, "three_gen": 282},
        },
        "verdict": {
            "gap_closes_under_photon_condition": bool(
                z["one_generation_dim_D"] == l["one_generation_dim_D"]
            ),
            "zero_one_gen": z["one_generation_dim_D"],
            "lambda_one_gen": l["one_generation_dim_D"],
            "zero_three_gen": z["three_generation_dim_D"],
            "lambda_three_gen": l["three_generation_dim_D"],
        },
    }
    print(json.dumps(receipt, indent=2, default=str))
    with open("/home/claude/rung_xvi_photon.json", "w") as f:
        json.dump(receipt, f, indent=2, default=str)


if __name__ == "__main__":
    main()
