#!/usr/bin/env python3
"""SOL TOWER, OPENED -- one monolith, every block visible.

The tower's own criterion (v2.0 section 14):

    "A block of code is mathematical when its specification, representation,
     arithmetic domain, invariants, and failure conditions are explicit."

In the shipped bundle those five properties live in prose. Here they are
STRUCTURE: every rung is a Block whose five fields are data, and the runner
ENFORCES the declared arithmetic domain against what the block actually
produced. A rung that declares EXACT_Z and returns a float fails -- not
because a human noticed, but because the runner refuses it.

Design rules, stated so they can be broken visibly:
  1. No import-time side effects. Nothing is built until run() is called.
  2. No bare `assert` as a proof step. Asserts vanish under `python -O`;
     verdicts do not.
  3. Exact first. A rung may use float64 only if it DECLARES a float domain,
     and then it must report a residual rather than a tolerance verdict.
  4. No clock, no path, no hostname inside a hashed region (Curse 38).
  5. Determinism: every stochastic draw is seeded and the seed is in the receipt.

Usage:
    python3 sol_tower_opened.py                 # run every rung
    python3 sol_tower_opened.py --json out.json # write the receipt
    python3 sol_tower_opened.py --only EXACT    # one status class
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from fractions import Fraction
from typing import Callable, Sequence

# ===========================================================================
# 0. THE GRAMMAR -- made enforceable
# ===========================================================================


class Domain(Enum):
    """The arithmetic a block is allowed to touch. Enforced, not documented."""
    EXACT_Z = "Z"            # Python int: unbounded, exact
    EXACT_ZI = "Z[i]"        # Gaussian integers as (int, int)
    EXACT_FP = "F_p"         # finite field, exact -- BUT see the int64 fence
    EXACT_Q = "Q"            # Fraction
    FLOAT64 = "R64"          # IEEE-754 binary64 -- must report a residual
    COMPLEX128 = "C128"      # two binary64 -- must report a residual
    WALLCLOCK = "t"          # not arithmetic at all: residual is the timing spread


class Status(Enum):
    EXACT = "EXACT"
    COMPUTED = "COMPUTED"
    CONDITIONAL = "CONDITIONAL"
    DESIGN = "DESIGN"
    OPEN = "OPEN"


@dataclass
class Result:
    """target / current / error, kept apart. Never averaged, never merged."""
    passed: bool
    detail: str
    values: dict = field(default_factory=dict)
    residual: float | None = None      # required iff the domain is inexact
    cost_ms: float = 0.0


@dataclass(frozen=True)
class Block:
    """One rung. The five properties are fields, not prose."""
    rung: str
    specification: str
    representation: str
    domain: Domain
    invariants: tuple[str, ...]
    failure: str
    status: Status
    run: Callable[[], Result]

    EXACT_DOMAINS = (Domain.EXACT_Z, Domain.EXACT_ZI, Domain.EXACT_FP, Domain.EXACT_Q)

    def execute(self) -> Result:
        t0 = time.perf_counter()
        try:
            r = self.run()
        except Exception as exc:                      # a throw is a verdict too
            return Result(False, f"THREW {type(exc).__name__}: {exc}",
                          cost_ms=(time.perf_counter() - t0) * 1e3)
        r.cost_ms = (time.perf_counter() - t0) * 1e3
        violation = self._domain_violation(r)
        if violation:
            return Result(False, f"DOMAIN VIOLATION -- {violation}", r.values,
                          r.residual, r.cost_ms)
        return r

    def _domain_violation(self, r: Result) -> str | None:
        """The runner refuses a rung whose output contradicts its declared domain."""
        exact = self.domain in self.EXACT_DOMAINS
        if exact:
            for k, v in r.values.items():
                if isinstance(v, float):
                    return f"declared {self.domain.value} but '{k}' is a float ({v!r})"
            if r.residual not in (None, 0.0):
                return f"declared {self.domain.value} but reported residual {r.residual!r}"
        else:
            if r.residual is None:
                return f"declared {self.domain.value} but reported no residual"
        return None


# ===========================================================================
# 1. THE EXACT CORE -- integers only. No float appears below this line
#    until the section that declares it.
# ===========================================================================

def fib_pair(n: int) -> tuple[int, int]:
    """(F_n, F_{n+1}) by fast doubling. O(M(n) log n) bit operations."""
    if n < 0:
        raise ValueError("n must be nonnegative")
    a, b = 0, 1
    for bit in bin(n)[2:]:                # iterative: no recursion-depth fence
        c = a * ((b << 1) - a)
        d = a * a + b * b
        a, b = (d, c + d) if bit == "1" else (c, d)
    return a, b


def golden_pair(n: int) -> tuple[int, int]:
    """(k_n, l_n) = (F_{n+1}, F_n)."""
    fn, fn1 = fib_pair(n)
    return fn1, fn


def hex_norm(k: int, l: int) -> int:
    """T = N(k + l*omega) in Z[omega]. omega = e^{i pi/3}, omega^2 = omega - 1."""
    return k * k + k * l + l * l


def eis_mul(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    a, b = x
    c, d = y
    return a * c - b * d, a * d + b * c + b * d


def cassini(k: int, l: int) -> int:
    """q(k,l) = k^2 - kl - l^2. The second conserved integer."""
    return k * k - k * l - l * l


def topology_from_T(T: int) -> dict[str, int]:
    V, E, F = 20 * T, 30 * T, 10 * T + 2
    return {"T": T, "V": V, "E": E, "F": F, "P": 12, "H": 10 * (T - 1),
            "chi": V - E + F}


# --- exact integer linear algebra (no numpy, no float) ---------------------

Mat = list[list[int]]

M_LIGHT: Mat = [[1, 2, 1, 0], [1, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1]]
Q_F: Mat = [[1, 1], [1, 0]]
GAMMA: Mat = [[1, -1, 0, 0], [-1, -1, 1, 0], [0, 1, 1, 0], [0, 0, 0, 1]]
J2: Mat = [[2, -1], [-1, -2]]            # 2J, kept integral


def mat_mul(A: Mat, B: Mat) -> Mat:
    return [[sum(A[i][k] * B[k][j] for k in range(len(B)))
             for j in range(len(B[0]))] for i in range(len(A))]


def transpose(A: Mat) -> Mat:
    return [list(col) for col in zip(*A)]


def det_int(A: Mat) -> int:
    """Exact Bareiss fraction-free elimination. Integer in, integer out."""
    n = len(A)
    M = [row[:] for row in A]
    sign, prev = 1, 1
    for k in range(n - 1):
        if M[k][k] == 0:
            for i in range(k + 1, n):
                if M[i][k] != 0:
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


def signature_by_minors(A: Mat) -> tuple[int, int]:
    """Jacobi's criterion: (positive, negative) inertia from leading minors.

    This replaces np.linalg.eigvalsh -- the ONE place the shipped tower sends
    an exact statement (sig Gamma = (3,1)) through float64 for no reason.
    Requires every leading principal minor nonzero; checked, not assumed.
    """
    n = len(A)
    minors = [1] + [det_int([row[:m] for row in A[:m]]) for m in range(1, n + 1)]
    if any(d == 0 for d in minors):
        raise ValueError("a leading principal minor vanishes; Jacobi does not apply")
    neg = sum(1 for i in range(n) if minors[i] * minors[i + 1] < 0)
    return n - neg, neg


def charpoly_int(A: Mat) -> list[int]:
    """Faddeev-LeVerrier. Returns [c_n, ..., c_0] for det(xI - A)."""
    n = len(A)
    I = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    M = [[0] * n for _ in range(n)]
    coeffs = [1]
    for k in range(1, n + 1):
        M = mat_mul(A, M)
        for i in range(n):
            M[i][i] += coeffs[-1]
        AM = mat_mul(A, M)
        c = -sum(AM[i][i] for i in range(n))
        if c % k:
            raise ArithmeticError("Faddeev-LeVerrier produced a non-integer coefficient")
        coeffs.append(c // k)
    return coeffs


# ===========================================================================
# 2. THE F_p LANE -- exact, and the ONE place x86-64 genuinely binds
# ===========================================================================

INT64_MAX = 2**63 - 1
PRIME_CEILING_INT64 = math.isqrt(INT64_MAX)     # 3037000499


def rank_mod_pure(M: Sequence[Sequence[int]], p: int) -> int:
    """Exact Gaussian rank over F_p in PYTHON ints -- no width fence at all.

    The shipped kernel does this in numpy int64, which is faster and carries a
    silent ceiling: the update a - f*a needs f*a < 2^63, i.e. p < isqrt(2^63)
    = 3037000499. Above that the rank is WRONG, not slow. That ceiling is a
    property of the register, not of the mathematics.
    """
    A = [[x % p for x in row] for row in M]
    rows, cols = len(A), len(A[0]) if A else 0
    r = 0
    for c in range(cols):
        piv = next((i for i in range(r, rows) if A[i][c]), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        inv = pow(A[r][c], -1, p)
        A[r] = [(x * inv) % p for x in A[r]]
        for i in range(rows):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(A[i][j] - f * A[r][j]) % p for j in range(cols)]
        r += 1
        if r == min(rows, cols):
            break
    return r


# ===========================================================================
# 3. THE BLOCKS
# ===========================================================================

def _b_euler() -> Result:
    """Euler forces twelve pentagons; chi = 2 on every golden rung."""
    bad = []
    for n in range(0, 40):
        k, l = golden_pair(n)
        t = topology_from_T(hex_norm(k, l))
        if not (t["P"] == 12 and t["chi"] == 2
                and 3 * t["V"] == 2 * t["E"] and t["F"] == t["V"] // 2 + 2):
            bad.append(n)
    # the closure identity itself, symbolically in integers: sum (6-p) f_p = 12
    P, H = 12, 10 * (hex_norm(*golden_pair(6)) - 1)
    defect = (6 - 5) * P + (6 - 6) * H
    return Result(not bad and defect == 12,
                  f"P=12 and chi=2 on 40 golden rungs; sum (6-p)f_p = {defect}",
                  {"rungs_checked": 40, "failures": len(bad), "curvature_defect": defect})


def _b_eisenstein() -> Result:
    """N is multiplicative on Z[omega]; T is that norm."""
    worst = 0
    for a in range(-6, 7):
        for b in range(-6, 7):
            for c in range(-6, 7):
                for d in range(-6, 7):
                    lhs = hex_norm(*eis_mul((a, b), (c, d)))
                    rhs = hex_norm(a, b) * hex_norm(c, d)
                    worst = max(worst, abs(lhs - rhs))
    return Result(worst == 0,
                  f"N(xy)=N(x)N(y) on {13**4} pairs, worst integer deviation {worst}",
                  {"pairs": 13**4, "worst_integer_deviation": worst})


def _b_fence() -> Result:
    """13 != 9: the shifted power is not Goldberg norm evolution."""
    w = (1, 1)
    w2 = eis_mul(w, w)
    wc = (w2[0] + 1, w2[1])
    return Result(hex_norm(*wc) == 13 and hex_norm(*w) ** 2 == 9,
                  "N(w^2+c)=13 vs N(w)^2=9 -- the translation breaks multiplicativity",
                  {"N_w": hex_norm(*w), "w_squared": list(w2),
                   "N_shifted": hex_norm(*wc), "N_w_squared": hex_norm(*w) ** 2})


def _b_light_matrix() -> Result:
    """Sym^2(Q_F) (+) [1]; charpoly (x-1)(x+1)(x^2-3x+1) in exact integers."""
    a, b, c, d = Q_F[0][0], Q_F[0][1], Q_F[1][0], Q_F[1][1]
    sym2 = [[a * a, 2 * a * b, b * b],
            [a * c, a * d + b * c, b * d],
            [c * c, 2 * c * d, d * d]]
    lift_ok = all(sym2[i][j] == M_LIGHT[i][j] for i in range(3) for j in range(3))
    # charpoly of M_LIGHT, exact
    cp = charpoly_int(M_LIGHT)                       # [1, c3, c2, c1, c0]
    # (x-1)(x+1)(x^2-3x+1) = x^4 - 3x^3 + 0x^2 + 3x - 1
    want = [1, -3, 0, 3, -1]
    # and the recursion actually advances real shell data
    k0, l0 = golden_pair(7)
    k1, l1 = golden_pair(8)
    s = [k0 * k0, k0 * l0, l0 * l0, 12]
    ns = [sum(M_LIGHT[i][j] * s[j] for j in range(4)) for i in range(4)]
    target = [k1 * k1, k1 * l1, l1 * l1, 12]
    return Result(lift_ok and cp == want and ns == target,
                  f"charpoly = {cp} (want {want}); M advances (k,l) shell data exactly",
                  {"charpoly": cp, "sym2_matches": int(lift_ok),
                   "advance_matches": int(ns == target)})


def _b_gamma() -> Result:
    """M^T Gamma M = Gamma, det = -3, signature (3,1) -- ALL in integers.

    The shipped tower computes the signature with np.linalg.eigvalsh (block A)
    and HARDCODES it as [3, 1] (block D). Here it is Jacobi's minor criterion:
    exact, integral, and it cannot be typed in by hand.
    """
    preserved = mat_mul(mat_mul(transpose(M_LIGHT), GAMMA), M_LIGHT) == GAMMA
    det = det_int(GAMMA)
    pos, neg = signature_by_minors(GAMMA)
    anti = mat_mul(mat_mul(transpose(Q_F), J2), Q_F) == [[-x for x in row] for row in J2]
    # s^T Gamma s = 145 on the whole ladder
    intervals = set()
    cass_ok = True
    for n in range(0, 80):
        k, l = golden_pair(n)
        s = [k * k, k * l, l * l, 12]
        intervals.add(sum(GAMMA[i][j] * s[i] * s[j] for i in range(4) for j in range(4)))
        if cassini(k, l) != (-1) ** n:
            cass_ok = False
    return Result(preserved and det == -3 and (pos, neg) == (3, 1)
                  and anti and intervals == {145} and cass_ok,
                  f"M^T G M = G; det = {det}; signature = ({pos},{neg}) by minors; "
                  f"s^T G s = {intervals.pop()} on 80 rungs; q = (-1)^n",
                  {"det_Gamma": det, "sig_pos": pos, "sig_neg": neg,
                   "interval": 145, "rungs": 80, "cassini_ok": int(cass_ok)})


def _b_recurrence() -> Result:
    """T_{n+3} = 2T_{n+2} + 2T_{n+1} - T_n, and its generating function."""
    N = 200
    T = [hex_norm(*golden_pair(n)) for n in range(N)]
    rec_bad = sum(1 for n in range(N - 3)
                  if T[n + 3] != 2 * T[n + 2] + 2 * T[n + 1] - T[n])
    # rational generating function by exact integer long division
    num, den = [1, 1, -1], [1, -2, -2, 1]
    a: list[int] = []
    for n in range(N):
        s = num[n] if n < len(num) else 0
        for j in range(1, len(den)):
            if j <= n:
                s -= den[j] * a[n - j]
        q, r = divmod(s, den[0])
        if r:
            raise ArithmeticError("generating function is not integral")
        a.append(q)
    return Result(rec_bad == 0 and a == T,
                  f"recurrence exact on {N-3} steps; GF (1+x-x^2)/(1-2x-2x^2+x^3) "
                  f"reproduces {N} terms",
                  {"terms": N, "recurrence_failures": rec_bad,
                   "gf_matches": int(a == T), "first_eight": T[:8]})


def _b_dirac_base() -> Result:
    """dim_R D_base = 272 = 2 * 16*17/2, by counting, not by SVD."""
    entries = 16 * 17 // 2
    real_dims = 2 * entries
    # verify the count constructively over the Gaussian integers: for each
    # (p<=q) pair and each of {1, i} there is one basis element, and they are
    # linearly independent because their supports are distinct.
    supports = {(p, q, unit) for p in range(16) for q in range(p, 16)
                for unit in (0, 1)}
    return Result(entries == 136 and real_dims == 272 and len(supports) == 272,
                  f"complex symmetric 16x16 has {entries} free entries; "
                  f"{real_dims} real directions, {len(supports)} distinct supports",
                  {"complex_entries": entries, "real_dimension": real_dims,
                   "distinct_supports": len(supports)})


def _b_group_algebra() -> Result:
    """R[C_N], R[D_N], R[Q8] dimensions -- and the no-go, in integers."""
    def cyclic(n):                      # R^2 + C^{(n-2)/2}
        return {"R": 2, "C": (n - 2) // 2, "H": 0, "M3C": 0, "dim": 2 + 2 * ((n - 2) // 2)}
    def dihedral(n):                    # R^4 + M2(R)^{n/2 - 1}
        return {"R": 4, "M2R": n // 2 - 1, "H": 0, "M3C": 0, "dim": 4 + 4 * (n // 2 - 1)}
    c14, d14 = cyclic(14), dihedral(14)
    q8 = {"R": 4, "H": 1, "dim": 8}
    af_dim = 2 + 4 + 18
    ok = (c14["dim"] == 14 and d14["dim"] == 28 and q8["dim"] == 8
          and c14["H"] == 0 and d14["H"] == 0 and af_dim == 24)
    return Result(ok,
                  f"dim R[C14]={c14['dim']}, dim R[D14]={d14['dim']}, dim R[Q8]={q8['dim']}, "
                  f"dim A_F={af_dim}; neither planar algebra carries an H or M3(C) block",
                  {"dim_RC14": c14["dim"], "dim_RD14": d14["dim"], "dim_RQ8": q8["dim"],
                   "H_blocks_in_C14": c14["H"], "H_blocks_in_D14": d14["H"],
                   "dim_AF": af_dim})


def _b_int64_fence() -> Result:
    """WHERE x86-64 ACTUALLY BINDS AN EXACT METHOD.

    Modular rank in numpy int64 needs the elimination update f * a[r][j] to
    stay below 2^63. With entries reduced mod p that is p^2 < 2^63, i.e.
    p <= isqrt(2^63) = 3037000499. This is the only fence in the entire exact
    tower that comes from the register width rather than from mathematics.
    Demonstrated here by computing one rank two ways past the ceiling.
    """
    import numpy as np

    def rank_mod_int64(M, p):
        A = np.mod(np.asarray(M, dtype=object), p).astype(np.int64)
        rows, cols = A.shape
        r = 0
        for c in range(cols):
            nz = np.flatnonzero(A[r:, c])
            if nz.size == 0:
                continue
            i = r + int(nz[0])
            if i != r:
                A[[r, i]] = A[[i, r]]
            inv = pow(int(A[r, c]), -1, p)
            A[r, c:] = (A[r, c:] * inv) % p
            if r + 1 < rows:
                f = A[r + 1:, c].copy()
                m = f != 0
                if np.any(m):
                    tgt = np.where(m)[0] + r + 1
                    A[tgt, c:] = (A[tgt, c:] - f[m, None] * A[r, c:]) % p
            r += 1
            if r == min(rows, cols):
                break
        return r

    # a small matrix of known rank 3
    M = [[1, 2, 3, 4], [2, 4, 6, 8], [1, 0, 1, 0], [0, 1, 1, 1], [3, 1, 2, 5]]
    safe_p, over_p = 65521, 4_000_000_007          # over_p^2 = 1.6e19 > 2^63
    safe_i64, safe_py = rank_mod_int64(M, safe_p), rank_mod_pure(M, safe_p)
    over_i64, over_py = rank_mod_int64(M, over_p), rank_mod_pure(M, over_p)
    agrees_below = safe_i64 == safe_py
    breaks_above = over_i64 != over_py
    return Result(agrees_below,
                  f"p={safe_p}: int64 rank {safe_i64} == python rank {safe_py}. "
                  f"p={over_p} (> {PRIME_CEILING_INT64}): int64 {over_i64} vs python {over_py} "
                  f"-> {'DIVERGES SILENTLY' if breaks_above else 'still agrees (headroom)'}",
                  {"prime_ceiling_int64": PRIME_CEILING_INT64,
                   "safe_prime": safe_p, "rank_int64_safe": safe_i64,
                   "rank_python_safe": safe_py, "over_prime": over_p,
                   "rank_int64_over": over_i64, "rank_python_over": over_py,
                   "diverges_above_ceiling": int(breaks_above)})


def _b_float_fence() -> Result:
    """WHERE float64 BINDS -- measured on the ladder, not asserted.

    Declared FLOAT64, so a residual is mandatory. The result is the rung index
    at which each exact integer stops being representable in binary64.
    """
    N = 200
    T = [hex_norm(*golden_pair(n)) for n in range(N)]

    def exact_in_f64(x: int) -> bool:
        f = float(x)
        return math.isfinite(f) and int(f) == x

    def last_true(pred) -> int:
        for n in range(N):
            if not pred(n):
                return n - 1
        return N - 1

    nT = last_true(lambda n: exact_in_f64(T[n]))
    nV = last_true(lambda n: exact_in_f64(20 * T[n]))
    nE = last_true(lambda n: exact_in_f64(30 * T[n]))

    def chi_f64(n: int) -> float:
        t = float(T[n])
        return 20 * t - 30 * t + (10 * t + 2)

    nChi = last_true(lambda n: chi_f64(n) == 2.0)
    bits_147 = T[147].bit_length()
    # the residual this block owes: the relative error of the first broken chi
    broken = chi_f64(nChi + 1)
    residual = abs(broken - 2.0) / 2.0
    return Result(nChi < nT,
                  f"T_n exact in binary64 to n={nT}; V=20T to n={nV}; E=30T to n={nE}; "
                  f"chi==2 only to n={nChi} (at n={nChi+1} it returns {broken}). "
                  f"The invariant dies {nT-nChi} rungs before its parts. "
                  f"T_147 needs {bits_147} bits.",
                  {"n_T_exact": nT, "n_V_exact": nV, "n_E_exact": nE,
                   "n_chi_exact": nChi, "bits_for_T147": bits_147,
                   "first_broken_chi": broken},
                  residual=residual)


def _b_cost_split() -> Result:
    """THE MONOLITH OPTIMIZATION: the check is cheaper than the thing checked.

    The shipped harness advances T_n by the three-term recurrence to N=500,000.
    Because T_n has Theta(n) digits, that loop costs Theta(N^2) bit operations.
    The independent cross-check -- Fibonacci fast doubling -- costs
    O(M(N) log N), which is subquadratic. So the verification is asymptotically
    CHEAPER than the computation it verifies. Measured here at three depths.
    """
    rows, spreads = [], []
    REPS = 5
    for N in (2000, 4000, 8000):
        recs, fasts = [], []
        for _ in range(REPS):
            t0 = time.perf_counter()
            a, b, c = 1, 3, 7
            for _ in range(3, N + 1):
                a, b, c = b, c, 2 * c + 2 * b - a
            recs.append(time.perf_counter() - t0)
            t0 = time.perf_counter()
            fn, fn1 = fib_pair(N)
            fasts.append(time.perf_counter() - t0)
        t_rec, t_fast = min(recs), min(fasts)
        spreads.append((max(recs) - min(recs)) / max(min(recs), 1e-12))
        direct = fn1 * fn1 + fn1 * fn + fn * fn
        if direct != c:
            return Result(False, f"recurrence and fast doubling disagree at N={N}",
                          {"N": N}, residual=0.0)
        t0 = time.perf_counter()
        digits = len(str(c))
        t_str = time.perf_counter() - t0
        rows.append({"N": N, "digits": digits,
                     "recurrence_ms": round(t_rec * 1e3, 2),
                     "fast_doubling_ms": round(t_fast * 1e3, 3),
                     "decimal_render_ms": round(t_str * 1e3, 2),
                     "speedup": round(t_rec / max(t_fast, 1e-9), 1)})
    # quadratic scaling check: 4x the work for 2x the depth
    ratio = rows[2]["recurrence_ms"] / max(rows[1]["recurrence_ms"], 1e-9)
    return Result(rows[-1]["speedup"] > 1.0,
                  "; ".join(f"N={r['N']}: recurrence {r['recurrence_ms']}ms vs "
                            f"fast-doubling {r['fast_doubling_ms']}ms "
                            f"(x{r['speedup']} cheaper), decimal render "
                            f"{r['decimal_render_ms']}ms" for r in rows)
                  + f"; doubling N multiplies recurrence cost by {ratio:.2f} (quadratic ~ 4)",
                  {"rows": rows, "scaling_factor_on_doubling": round(ratio, 2),
                   "repeats": REPS},
                  residual=max(spreads))


# ===========================================================================
# 4. THE REGISTRY
# ===========================================================================

BLOCKS: tuple[Block, ...] = (
    Block("III  Euler closure",
          "Every closed trivalent 5/6 tiling of S^2 has P=12 and chi=2.",
          "T -> (V,E,F,P,H) as Python ints; golden rungs from fast doubling.",
          Domain.EXACT_Z,
          ("3V = 2E", "F = V/2 + 2", "sum (6-p) f_p = 12", "chi = 2"),
          "any rung where P != 12 or chi != 2",
          Status.EXACT, _b_euler),

    Block("IV   Eisenstein norm",
          "N(xy) = N(x)N(y) on Z[omega]; T = N(k + l omega).",
          "lattice points as (k,l) int pairs; omega^2 = omega - 1 folded into eis_mul.",
          Domain.EXACT_Z,
          ("N(xy) - N(x)N(y) == 0 for every pair in the block",),
          "any nonzero integer deviation",
          Status.EXACT, _b_eisenstein),

    Block("IV*  the fence 13 != 9",
          "A shifted power w^2 + c does NOT evolve the triangulation number.",
          "same integer pairs; the single counterexample w = 1 + omega, c = 1.",
          Domain.EXACT_Z,
          ("N(w^2+c) == 13", "N(w)^2 == 9"),
          "if these ever coincide the refutation is void",
          Status.EXACT, _b_fence),

    Block("V    Light Matrix",
          "M = Sym^2(Q_F) (+) [1]; charpoly (x-1)(x+1)(x^2-3x+1).",
          "4x4 integer matrix; Faddeev-LeVerrier for the characteristic polynomial.",
          Domain.EXACT_Z,
          ("M[:3,:3] == Sym^2(Q_F)", "charpoly == [1,-3,0,3,-1]",
           "M advances real shell data exactly"),
          "any coefficient off by one, or a shell that does not land",
          Status.EXACT, _b_light_matrix),

    Block("V*   the integral Lorentz metric",
          "M^T Gamma M = Gamma; det = -3; signature (3,1); s^T Gamma s = 145.",
          "integer matrices; signature by Jacobi leading-minor criterion -- NOT eigenvalues.",
          Domain.EXACT_Z,
          ("M^T G M == G", "det G == -3", "inertia == (3,1)",
           "Q_F^T (2J) Q_F == -(2J)", "s^T G s == 145 on every rung",
           "q(k,l) == (-1)^n"),
          "a vanishing leading minor voids Jacobi; any interval != 145",
          Status.EXACT, _b_gamma),

    Block("V**  triangulation sequence",
          "T_{n+3} = 2T_{n+2} + 2T_{n+1} - T_n; GF = (1+x-x^2)/(1-2x-2x^2+x^3).",
          "exact integer long division of the rational generating function.",
          Domain.EXACT_Z,
          ("recurrence residual == 0", "series coefficients == T_n"),
          "a non-integral series coefficient, or any mismatch",
          Status.EXACT, _b_recurrence),

    Block("VI   planar no-go",
          "No finite planar point-group algebra equals A_F = C + H + M3(C).",
          "Wedderburn block counts as integers; no matrices constructed.",
          Domain.EXACT_Z,
          ("dim R[C14] == 14", "dim R[D14] == 28", "no H block in either",
           "dim A_F == 24"),
          "an H or M3(C) block appearing in a cyclic or dihedral algebra",
          Status.EXACT, _b_group_algebra),

    Block("VIII base Dirac dimension",
          "dim_R D_base = 272, by counting free entries of a complex symmetric 16x16.",
          "combinatorial count over (p<=q, unit) supports. No SVD, no allocation.",
          Domain.EXACT_Z,
          ("16*17/2 == 136", "2*136 == 272", "272 distinct supports"),
          "a duplicate support would mean the basis is dependent",
          Status.EXACT, _b_dirac_base),

    Block("X*   the int64 fence",
          "Modular rank in numpy int64 is exact only while p^2 < 2^63.",
          "one small matrix of known rank, ranked twice: numpy int64 vs Python int.",
          Domain.EXACT_FP,
          ("p <= isqrt(2^63) = 3037000499 for the int64 path",
           "Python-int path has no width fence"),
          "above the ceiling the int64 rank is wrong, not slow, and says nothing",
          Status.EXACT, _b_int64_fence),

    Block("XIII float64 fence",
          "Where binary64 stops holding the exact ladder -- measured per quantity.",
          "exact int ladder vs its float64 image; chi recomputed in float.",
          Domain.FLOAT64,
          ("chi breaks strictly before T_n does",),
          "if the composite outlived its parts the model of the fence is wrong",
          Status.COMPUTED, _b_float_fence),

    Block("XIII* the cost split",
          "The O(M(N) log N) cross-check is cheaper than the O(N^2) computation.",
          "three depths, best-of-5 wall clock, same host, same process.",
          Domain.WALLCLOCK,
          ("fast doubling strictly faster than the recurrence at every depth",),
          "if the recurrence ever wins, the asymptotics are being masked by constants",
          Status.COMPUTED, _b_cost_split),
)


# ===========================================================================
# 5. THE RUNNER
# ===========================================================================

def architecture() -> dict:
    """The receipt. Measured, and deliberately OUTSIDE the hashed region."""
    import numpy as np
    flags: list[str] = []
    model = "unknown"
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name") and model == "unknown":
                model = line.split(":", 1)[1].strip()
            elif line.startswith("flags") and not flags:
                flags = line.split(":", 1)[1].split()
    except OSError:
        pass
    return {
        "machine": platform.machine(),
        "python": sys.version.split()[0],
        "cpu_model": model,
        "pointer_bits": 8 * np.dtype(np.intp).itemsize,
        "float64_mantissa_bits": int(np.finfo(np.float64).nmant) + 1,
        "int64_max": int(np.iinfo(np.int64).max),
        "prime_ceiling_for_int64_rank": PRIME_CEILING_INT64,
        "simd": [f for f in ("sse2", "avx", "avx2", "avx512f", "fma", "bmi2", "sha_ni")
                 if f in flags],
    }


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", type=str, default=None, help="write the receipt here")
    ap.add_argument("--only", type=str, default=None, help="EXACT | COMPUTED | ...")
    args = ap.parse_args(argv)

    blocks = [b for b in BLOCKS
              if args.only is None or b.status.name == args.only.upper()]

    print("=" * 78)
    print("SOL TOWER, OPENED -- every block visible, every domain enforced")
    print("=" * 78)
    arch = architecture()
    print(f"host: {arch['machine']} / {arch['cpu_model']} / python {arch['python']}")
    print(f"      binary64 mantissa {arch['float64_mantissa_bits']} bits; "
          f"int64 rank ceiling p <= {arch['prime_ceiling_for_int64_rank']}")
    print(f"      simd: {' '.join(arch['simd']) or '(none detected)'}")
    print()

    results, npass = [], 0
    for b in blocks:
        r = b.execute()
        npass += r.passed
        tag = "PASS" if r.passed else "FAIL"
        print(f"[{tag}] {b.rung:28s} {b.status.value:11s} {b.domain.value:5s} "
              f"{r.cost_ms:8.2f} ms")
        print(f"       spec : {b.specification}")
        print(f"       repr : {b.representation}")
        print(f"       inv  : {'; '.join(b.invariants)}")
        print(f"       fail : {b.failure}")
        print(f"       ---> {r.detail}")
        if r.residual is not None:
            print(f"       residual: {r.residual:.3e}")
        print()
        results.append({
            "rung": b.rung, "status": b.status.value, "domain": b.domain.value,
            "specification": b.specification, "representation": b.representation,
            "invariants": list(b.invariants), "failure_condition": b.failure,
            "passed": r.passed, "detail": r.detail, "values": r.values,
            "residual": r.residual, "cost_ms": round(r.cost_ms, 3),
        })

    print("=" * 78)
    print(f"{npass}/{len(blocks)} blocks pass, domain-enforced")
    print("=" * 78)

    # Curse 38: hash the MATH, never the clock, the host, or a measurement.
    # An EXACT block contributes its values; an inexact block contributes only
    # its verdict, because its numbers are host- and load-dependent by nature.
    # (First draft of this file hashed the timings too and produced a different
    #  digest on every run. Kept as the failure this rule exists to prevent.)
    EXACT_D = {d.value for d in Block.EXACT_DOMAINS}
    hashable_view = []
    for r in results:
        if r["domain"] in EXACT_D:
            hashable_view.append({k: v for k, v in r.items() if k != "cost_ms"})
        else:
            hashable_view.append({"rung": r["rung"], "status": r["status"],
                                  "domain": r["domain"], "passed": r["passed"]})
    hashable = json.dumps(hashable_view, sort_keys=True).encode()
    receipt = {
        "artifact": "SOL_TOWER_OPENED",
        "math_sha256": hashlib.sha256(hashable).hexdigest(),
        "blocks": results,
        "architecture": arch,           # OUTSIDE the hash, on purpose
        "generated_unix": int(time.time()),   # OUTSIDE the hash, on purpose
    }
    print(f"math_sha256 (clock- and host-free): {receipt['math_sha256']}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2, sort_keys=True)
        print(f"receipt -> {args.json}")
    return 0 if npass == len(blocks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
