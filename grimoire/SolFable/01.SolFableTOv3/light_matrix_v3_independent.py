#!/usr/bin/env python3
"""THEA v3.0 light-matrix kernel -- INDEPENDENT REIMPLEMENTATION (Fable, 2026-07-31).

The original `light_matrix_v3.py` (sha256 bec6299f...) was pinned in the bundle
manifest but absent from the upload. This file was rebuilt from three artifacts
ONLY: light_matrix_v3_certificate.json, light_matrix_v3_results.txt, and
test_light_matrix_v3.py. It shares no code with the generator. If the author's
own test suite passes against this file, what is verified is the SPEC.

Math content:
  - Goldberg fullerene topology from triangulation number T:
      V=20T, E=30T, F=10T+2, P=12 always, chi=2 always (Euler-forced).
  - Eisenstein/Loeschian pair arithmetic on the hexagonal lattice,
      norm N(k,l)=k^2+kl+l^2, multiplicative; metric [[2,1],[1,2]].
  - The golden selector: Fibonacci pairs (F_{n+1},F_n), k/l -> phi,
      T_n = F_{n+1}^2 + F_{n+1}F_n + F_n^2, radius scale sqrt(T).
  - The lifted 3-mode recursion u=(k^2,kl,l^2), B=[[1,2,1],[1,1,0],[1,0,0]],
      spec(M_light) = {phi^2, 1, -1, phi^-2} with the appended P=12 mode.
  - The Planck pentagram test: q=phi^-2 contraction, level counts from
      edge / radius / diameter -- CHOICE-DEPENDENT BY CONSTRUCTION (hypothesis,
      not derivation; the test suite enforces the caveat).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import NamedTuple

PHI = (1.0 + math.sqrt(5.0)) / 2.0
PSI = (1.0 - math.sqrt(5.0)) / 2.0

PLANCK_LENGTH_M = 1.616255e-35      # CODATA 2018
C60_EDGE_M = 1.42e-10               # graphene-like C-C bond


# ---------------------------------------------------------------- pairs
class Pair(NamedTuple):
    k: int
    ell: int


def hex_norm(k: int, ell: int) -> int:
    """Loeschian norm on the hexagonal lattice: N = k^2 + kl + l^2.
    Equals the Goldberg triangulation number T of shell (k,l)."""
    return k * k + k * ell + ell * ell


def multiply_pairs(a: Pair, b: Pair) -> Pair:
    """Eisenstein multiplication in Z[w] with w^2 = w - 1 (sixth root of unity).
    (a.k + a.l w)(b.k + b.l w) = (ak*bk - al*bl) + (ak*bl + al*bk + al*bl) w.
    The norm is multiplicative: N(ab) = N(a) N(b)."""
    return Pair(a.k * b.k - a.ell * b.ell,
                a.k * b.ell + a.ell * b.k + a.ell * b.ell)


def _rot(p: Pair) -> Pair:
    """Multiply by the unit w: (k,l) -> (-l, k+l). Six applications = identity."""
    return Pair(-p.ell, p.k + p.ell)


def _conj(p: Pair) -> Pair:
    """Complex conjugation: k + l w -> (k+l) - l w."""
    return Pair(p.k + p.ell, -p.ell)


def canonical_pair(p: Pair) -> Pair:
    """Rotate (and if needed conjugate) into the canonical sector k >= l >= 0."""
    for start in (p, _conj(p)):
        q = start
        for _ in range(6):
            if q.k >= q.ell >= 0 and (q.k, q.ell) != (0, 0):
                return Pair(q.k, q.ell)
            q = _rot(q)
    return Pair(0, 0)


def golden_next(p: Pair) -> Pair:
    """The Fibonacci step on shells: (k, l) -> (k + l, k)."""
    return Pair(p.k + p.ell, p.k)


def lifted_step(state: tuple[int, int, int]) -> tuple[int, int, int]:
    """The lifted light-matrix step B on u=(k^2, kl, l^2):
    B = [[1,2,1],[1,1,0],[1,0,0]]; exactly the symmetric square of the
    Fibonacci matrix, spectrum {phi^2, -1, phi^-2}."""
    a, b, c = state
    return (a + 2 * b + c, a + b, a)


# ---------------------------------------------------------------- topology
def topology_from_t(t: int) -> dict:
    """Exact Goldberg fullerene counts for triangulation number T.
    Euler: V - E + F = 20T - 30T + (10T + 2) = 2. Pentagons = 12 always."""
    return {"T": t, "P": 12, "chi": 2,
            "V": 20 * t, "E": 30 * t, "F": 10 * t + 2, "H": 10 * (t - 1)}


@dataclass
class Shell:
    level: int
    k: int
    ell: int
    triangulation_number: int
    vertices: int
    edges: int
    faces: int
    pentagons: int
    hexagons: int
    chi: int
    radius_scale: float
    projective_ratio: float | None
    projective_error: float | None


def golden_shells(n: int) -> list[Shell]:
    """The golden-selected tower: shells GP(F_{i+1}, F_i), i = 0..n-1."""
    out: list[Shell] = []
    p = Pair(1, 0)
    for level in range(n):
        t = hex_norm(p.k, p.ell)
        topo = topology_from_t(t)
        ratio = (p.k / p.ell) if p.ell else None
        err = abs(ratio - PHI) if ratio is not None else None
        out.append(Shell(level, p.k, p.ell, t,
                         topo["V"], topo["E"], topo["F"],
                         12, topo["H"], 2,
                         math.sqrt(t), ratio, err))
        p = golden_next(p)
    return out


def _fib(n: int) -> float:
    """Binet closed form."""
    return (PHI ** n - PSI ** n) / math.sqrt(5.0)


def golden_closed_form_t(level: int) -> float:
    """Closed form for the golden shell triangulation number:
    T_n = F_{n+1}^2 + F_{n+1} F_n + F_n^2 via Binet."""
    a = _fib(level + 1)
    b = _fib(level)
    return a * a + a * b + b * b


# ---------------------------------------------------------------- planck test
def ideal_c60_radius(edge: float = C60_EDGE_M) -> float:
    """Circumradius of the ideal truncated icosahedron with edge a:
    R = (a/4) sqrt(58 + 18 sqrt 5)."""
    return edge * math.sqrt(58.0 + 18.0 * math.sqrt(5.0)) / 4.0


def planck_report() -> dict:
    """The inward-pentagram level count: R_j = R_0 * phi^(-2j); solve R_N = l_P.
    N = log(R_0 / l_P) / (2 log phi).  DELIBERATELY reported for THREE different
    starting lengths, because the count moves with the choice -- that movement is
    the point: HYPOTHESIS TEST, NOT DERIVATION. h is not a length."""
    q = 1.0 / (PHI * PHI)

    def levels(start: float) -> float:
        return math.log(start / PLANCK_LENGTH_M) / math.log(1.0 / q)

    r0 = ideal_c60_radius()
    return {
        "q_phi_minus_2": q,
        "edge_m": C60_EDGE_M,
        "planck_length_m": PLANCK_LENGTH_M,
        "ideal_c60_radius_m": r0,
        "levels_from_edge": levels(C60_EDGE_M),
        "levels_from_radius": levels(r0),
        "levels_from_diameter": levels(2.0 * r0),
        "status": "HYPOTHESIS_TEST_NOT_DERIVATION",
        "warning": "The count depends on the chosen start length and contraction; h is not a length.",
    }
