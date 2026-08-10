#!/usr/bin/env python3
"""Moduli dimension of the order-one space.

dim_R D(A) counts DIRECTIONS. Physics counts ORBITS. The gauge group of a
finite real spectral triple acts on D by

    D  |->  U D U*,   U = pi(u) J pi(u) J*,   u unitary in A,

so the physically distinguishable content is

    dim moduli = dim D(A) - dim (gauge orbit through a generic D).

Infinitesimally, with a in the anti-hermitian part of A (the Lie algebra
u(A)), the tangent to the orbit at D is [X, D] with X = pi(a) + J pi(a) J^-1.

This is the finite-dimensional shadow of Cacic's moduli space of Dirac
operators for finite spectral triples (arXiv:0902.2068). Reporting only
dim D(A) = 16 overcounts the physics.
"""
from __future__ import annotations

import json
from typing import Dict, List

import numpy as np

import rung_xv_irreducible as K
from rung_xv_followup import null_space, as_real_vectors


def lie_algebra_basis(rule: str) -> List[np.ndarray]:
    """Anti-hermitian generators of u(A), pushed through pi."""
    Z3 = np.zeros((3, 3), complex)
    elems = []
    if rule == "free_real":
        # u(R) = {0}: the real line has no anti-hermitian part beyond 0.
        pass
    # u(1) from C
    elems.append((0.0, 1.0j, (0, 0, 0, 0), Z3))
    # su(2) from H: imaginary quaternions
    for j in (1, 2, 3):
        q = [0, 0, 0, 0]
        q[j] = 1
        elems.append((0.0, 0j, tuple(q), Z3))
    # u(3) from M3(C): anti-hermitian 3x3
    for a in range(3):
        elems.append((0.0, 0j, (0, 0, 0, 0), _e(a, a, 1j)))
    for a in range(3):
        for b in range(a + 1, 3):
            elems.append((0.0, 0j, (0, 0, 0, 0), _e(a, b, 1.0) - _e(b, a, 1.0)))
            elems.append((0.0, 0j, (0, 0, 0, 0), _e(a, b, 1j) + _e(b, a, 1j)))
    return [K.pi(e, rule) for e in elems]


def _e(a: int, b: int, z: complex) -> np.ndarray:
    m = np.zeros((3, 3), complex)
    m[a, b] = z
    return m


def moduli_report(rule: str) -> Dict[str, object]:
    coeffs = null_space(rule)
    S = as_real_vectors(coeffs)
    dim_D = int(np.linalg.matrix_rank(S, tol=1e-9))

    # generic point of the space
    rng = np.random.default_rng(11235)
    c = rng.normal(size=len(coeffs))
    D = np.tensordot(c @ coeffs, K.DBASE, axes=(0, 0))

    Jinv = K.JPERM  # J = JPERM . conj, and JPERM is a real involution
    tangents = []
    for A in lie_algebra_basis(rule):
        X = A + Jinv @ A.conjugate() @ Jinv
        T = X @ D - D @ X
        tangents.append(np.concatenate([T.real.ravel(), T.imag.ravel()]))
    Tm = np.array(tangents)

    orbit_dim = int(np.linalg.matrix_rank(Tm, tol=1e-8))
    inside = int(np.linalg.matrix_rank(np.vstack([S, Tm]), tol=1e-8))
    return {
        "rule": rule,
        "dim_D": dim_D,
        "gauge_generators": len(tangents),
        "orbit_dimension_at_generic_D": orbit_dim,
        "orbit_tangent_lies_inside_D_space": bool(inside == dim_D),
        "moduli_dimension": dim_D - orbit_dim,
        "status": "COMPUTED (numerical rank, tol 1e-8)",
    }


def main() -> None:
    out = {r: moduli_report(r) for r in ("free_real", "zero", "lambda")}
    print(json.dumps(out, indent=2))
    with open("/home/claude/rung_xv_moduli.json", "w") as f:
        json.dump(out, f, indent=2)


if __name__ == "__main__":
    main()
