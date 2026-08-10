#!/usr/bin/env python3
"""SOL FABLE LaTeX Tower v2.0 - architecture-bounded verification.

This is a deterministic stress harness, not an attempt to crash the host.
It records the available CPU/memory/SIMD envelope, executes exact arbitrary-
precision recurrence checks to a declared depth, repeats the finite-field rank
certificates across independent deterministic witnesses, validates the Schur
commutant, and executes a browser-style BigInt kernel under Node.

Status grammar:
  EXACT       symbolic/integer/finite-field proof within the declared model.
  COMPUTED    finite-precision result with residual and environment receipt.
  CONDITIONAL exact after explicit representation assumptions.
  TRIVIAL     the traditional mathematician's joke for the still-open rung.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RECEIPTS = ROOT / "receipts"
RECEIPTS.mkdir(parents=True, exist_ok=True)

# Import the complete v1 reconstruction kernel copied into this bundle.
import sol_fable_tower_audit_v1 as A

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fib_pair(n: int) -> Tuple[int, int]:
    """Return (F_n, F_{n+1}) by exact fast doubling."""
    if n < 0:
        raise ValueError("n must be nonnegative")
    if n == 0:
        return 0, 1
    a, b = fib_pair(n >> 1)
    c = a * ((b << 1) - a)
    d = a * a + b * b
    return (d, c + d) if (n & 1) else (c, d)


def exact_triangulation(n: int) -> int:
    """T_n = F_{n+1}^2 + F_{n+1}F_n + F_n^2."""
    fn, fn1 = fib_pair(n)
    return fn1 * fn1 + fn1 * fn + fn * fn


def architecture_info() -> Dict[str, object]:
    cpu_flags = []
    model_name = "unknown"
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name") and model_name == "unknown":
                model_name = line.split(":", 1)[1].strip()
            elif line.startswith("flags") and not cpu_flags:
                cpu_flags = line.split(":", 1)[1].split()
    except OSError:
        pass

    mem_total = None
    mem_available = None
    try:
        mem = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, value = line.split(":", 1)
            mem[key] = int(value.strip().split()[0]) * 1024
        mem_total = mem.get("MemTotal")
        mem_available = mem.get("MemAvailable")
    except OSError:
        pass

    return {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "python": sys.version,
        "cpu_count": os.cpu_count(),
        "cpu_model": model_name,
        "byteorder": sys.byteorder,
        "pointer_bits": 8 * np.dtype(np.intp).itemsize,
        "float64_mantissa_bits": np.finfo(np.float64).nmant + 1,
        "float64_epsilon": float(np.finfo(np.float64).eps),
        "memory_total_bytes": mem_total,
        "memory_available_bytes_at_start": mem_available,
        "simd_flags_of_interest": [
            f for f in ("sse2", "avx", "avx2", "avx512f", "fma", "bmi2", "sha_ni")
            if f in cpu_flags
        ],
    }


def stress_exact_ladder(depth: int = 500_000) -> Dict[str, object]:
    """Advance the exact T recurrence to a large but non-destructive depth.

    The recurrence is not accepted merely because it generated its own output:
    the terminal value is independently recomputed from Fibonacci fast doubling.
    """
    if depth < 3:
        raise ValueError("depth must be at least 3")
    t0 = time.perf_counter()
    t_nm2, t_nm1, t_n = 1, 3, 7
    for _ in range(3, depth + 1):
        t_np1 = 2 * t_n + 2 * t_nm1 - t_nm2
        t_nm2, t_nm1, t_n = t_nm1, t_n, t_np1
    recurrence_seconds = time.perf_counter() - t0

    t1 = time.perf_counter()
    independent = exact_triangulation(depth)
    fast_doubling_seconds = time.perf_counter() - t1
    if independent != t_n:
        raise AssertionError("recurrence and fast-doubling values disagree")

    # Exact modular digests avoid storing the huge decimal string in the receipt.
    primes = (1_000_000_007, 1_000_000_009, 2_147_483_647)
    residues = {str(p): int(t_n % p) for p in primes}
    digits = len(str(t_n))
    byte_len = (t_n.bit_length() + 7) // 8
    digest = sha256_bytes(t_n.to_bytes(byte_len, "big"))

    return {
        "depth": depth,
        "terminal_decimal_digits": digits,
        "terminal_bit_length": t_n.bit_length(),
        "terminal_sha256_big_endian": digest,
        "terminal_prime_residues": residues,
        "recurrence_seconds": recurrence_seconds,
        "fast_doubling_crosscheck_seconds": fast_doubling_seconds,
        "exact_match": True,
    }


def fixed_extended_element(seed: int, slot: int):
    rng = np.random.default_rng(seed + 104729 * slot)
    return A.random_extended_elem(rng)


def fixed_ps_element(seed: int, slot: int):
    rng = np.random.default_rng(seed + 130363 * slot)
    return A.random_ps_elem(rng)


def repeated_modular_rank_receipt() -> Dict[str, object]:
    """Repeat exact rank lower bounds with independent deterministic witnesses.

    Each rank is computed modulo a prime on an integer constraint matrix.  A
    rank-r minor nonzero mod p is a nonzero integer minor, hence rank_Q >= r.
    The explicit null vectors checked against the full algebra basis supply the
    opposite nullity inequality.
    """
    primes = (1009, 1013, 10007, 10009, 65519, 65521)
    seeds = (20260803, 31415926, 27182818)
    ext_runs = []
    ps_runs = []

    t0 = time.perf_counter()
    for seed in seeds:
        ext_parts = []
        for slot in range(3):
            left = A.pi_extended(fixed_extended_element(seed, 2 * slot))
            right = A.opposite(A.pi_extended(fixed_extended_element(seed, 2 * slot + 1)))
            ext_parts.append(A.constraint_matrix(A.DBASE, left, right))
        x_ext = np.concatenate(ext_parts, axis=0)
        ranks_ext = {str(p): A.rank_mod(x_ext, p) for p in primes}
        ext_runs.append({"seed": seed, "shape": list(x_ext.shape), "ranks": ranks_ext})

        left_ps = A.pi_ps(fixed_ps_element(seed, 0))
        right_ps = A.opposite(A.pi_ps(fixed_ps_element(seed, 1)))
        x_ps = A.constraint_matrix(A.DBASE, left_ps, right_ps)
        ranks_ps = {str(p): A.rank_mod(x_ps, p) for p in primes}
        ps_runs.append({"seed": seed, "shape": list(x_ps.shape), "ranks": ranks_ps})

    y16 = A.physical_yukawa_basis()
    y8 = A.paired_ps_yukawa_basis()
    y16_rank = A.real_span_rank(y16)
    y8_rank = A.real_span_rank(y8)
    y16_residual = A.max_order_one_residual(y16, A.extended_basis("CHM"))
    y8_residual = A.max_order_one_residual(y8, A.ps_basis())

    ext_all = [r for run in ext_runs for r in run["ranks"].values()]
    ps_all = [r for run in ps_runs for r in run["ranks"].values()]
    exact16 = set(ext_all) == {256} and y16_rank == 16 and y16_residual == 0.0
    exact8 = set(ps_all) == {264} and y8_rank == 8 and y8_residual == 0.0
    if not (exact16 and exact8):
        raise AssertionError("rank sandwich stress failed")

    return {
        "primes": list(primes),
        "seeds": list(seeds),
        "extended_runs": ext_runs,
        "pati_salam_runs": ps_runs,
        "explicit_yukawa16_rank": y16_rank,
        "explicit_yukawa16_full_basis_residual": y16_residual,
        "explicit_paired8_rank": y8_rank,
        "explicit_paired8_full_basis_residual": y8_residual,
        "exact_extended_nullity": 16,
        "exact_pati_salam_nullity": 8,
        "seconds": time.perf_counter() - t0,
    }


def exact_symbolic_receipt() -> Dict[str, object]:
    q = sp.Matrix([[1, 1], [1, 0]])
    b = A.symmetric_square_2x2(q)
    m = sp.diag(1, 1, 1, 1)
    m[:3, :3] = b
    lam = sp.symbols("lambda")
    gamma = sp.Matrix([
        [1, -1, 0, 0],
        [-1, -1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 1],
    ])
    j = sp.Matrix([[1, sp.Rational(-1, 2)], [sp.Rational(-1, 2), -1]])
    checks = {
        "sym2": [[int(b[i, j_]) for j_ in range(3)] for i in range(3)],
        "charpoly_Q": str(sp.factor(q.charpoly(lam).as_expr())),
        "charpoly_M": str(sp.factor(m.charpoly(lam).as_expr())),
        "Q_T_J_Q_equals_minus_J": bool(q.T * j * q == -j),
        "M_T_Gamma_M_equals_Gamma": bool(m.T * gamma * m == gamma),
        "Gamma_det": int(gamma.det()),
        "Gamma_eigenvalue_signs_numeric": [
            int(np.sign(x)) for x in np.linalg.eigvalsh(np.array(gamma, dtype=float))
        ],
    }
    if checks["charpoly_M"] != "(lambda - 1)*(lambda + 1)*(lambda**2 - 3*lambda + 1)":
        raise AssertionError("unexpected Light Matrix characteristic polynomial")
    return checks


def node_bigint_receipt(depth: int = 200_000) -> Dict[str, object]:
    js = ROOT / "code" / "sol_tower_browser_v2.js"
    proc = subprocess.run(
        ["node", str(js), str(depth)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(proc.stdout)
    if not result.get("exact_match"):
        raise AssertionError("Node BigInt cross-check failed")
    return result


def memory_peak_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    # Linux reports KiB; macOS reports bytes.
    return int(value * 1024 if sys.platform.startswith("linux") else value)


def main() -> None:
    start = time.perf_counter()
    receipt: Dict[str, object] = {
        "version": "SOL_FABLE_LATEX_TOWER_v2.0",
        "status_boundary": {
            "exact": "symbolic, integer, or finite-field certificate within declared model",
            "computed": "finite arithmetic with residual and environment",
            "conditional": "exact only after explicit representation assumptions",
            "trivial": "mathematical joke label for the still-open global Step 4",
        },
        "architecture": architecture_info(),
        "symbolic": exact_symbolic_receipt(),
        "exact_ladder_stress": stress_exact_ladder(),
        "modular_rank_stress": repeated_modular_rank_receipt(),
        "commutant": A.extended_commutant_receipt(),
        "node_bigint": node_bigint_receipt(),
    }
    receipt["elapsed_seconds"] = time.perf_counter() - start
    receipt["peak_rss_bytes"] = memory_peak_bytes()
    out = RECEIPTS / "sol_architecture_stress_v2.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "receipt": str(out),
        "elapsed_seconds": receipt["elapsed_seconds"],
        "peak_rss_bytes": receipt["peak_rss_bytes"],
        "ladder_depth": receipt["exact_ladder_stress"]["depth"],
        "ladder_digits": receipt["exact_ladder_stress"]["terminal_decimal_digits"],
        "extended_nullity": receipt["modular_rank_stress"]["exact_extended_nullity"],
        "pati_salam_nullity": receipt["modular_rank_stress"]["exact_pati_salam_nullity"],
        "node_depth": receipt["node_bigint"]["depth"],
    }, indent=2))


if __name__ == "__main__":
    main()
