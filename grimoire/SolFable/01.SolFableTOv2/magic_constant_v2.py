#!/usr/bin/env python3
"""Derive and certify the binary64 rung oracle for the golden shell ladder.

The exact ladder is

    (k_n, l_n) = (F_{n+1}, F_n),
    T_n = k_n^2 + k_n l_n + l_n^2.

For a positive normal IEEE-754 binary64 number x = 2^e (1 + u), with
u = m / 2^52, the unsigned 64-bit encoding B(x) obeys the exact identity

    B(x)/2^52 = 1023 + log2(x) + psi(u),
    psi(u) = u - log2(1+u).

The ladder has asymptotically affine logarithm, so a nearest-rung classifier
can be implemented by one integer subtraction and one integer division on the
raw binary64 encoding. This file distinguishes three constants:

    C_ASYMPTOTIC  -- derived from the exact asymptotic intercept;
    C_ROBUST      -- midpoint of the exact admissible interval for every
                     representable T_n (n = 0,...,737), maximizing the worst
                     decision margin for the chosen stride;
    C_LEGACY      -- the supplied Opus-5 plateau member, retained for lineage.

No stochastic search is used here. All ladder ground truth is exact Python int.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
import json
import math
from pathlib import Path
import struct
from typing import Iterable

MANTISSA_BITS = 52
EXPONENT_BIAS = 1023
SCALE = 1 << MANTISSA_BITS

# Supplied artifacts used these values. They remain valid plateau members but
# are not the unique outcome of the asymptotic derivation.
C_LEGACY = 0x3FF100E2F21F7C00
D_LEGACY = 0x0016373AD151CA69


def decimal_constants(precision: int = 120) -> tuple[Decimal, Decimal, int, Decimal, int]:
    """Return phi, log2(phi), rounded D, asymptotic intercept, rounded C.

    Decimal arithmetic is used because binary64 math.log2(phi) rounds the stride
    one integer unit too high after multiplication by 2^53.
    """
    with localcontext() as ctx:
        ctx.prec = precision
        two = Decimal(2)
        five = Decimal(5)
        phi = (Decimal(1) + five.sqrt()) / two
        ln2 = two.ln()
        log2_phi = phi.ln() / ln2
        d_real = Decimal(1 << 53) * log2_phi
        d_int = int(d_real.to_integral_value(rounding=ROUND_HALF_EVEN))
        c_real = Decimal(SCALE) * (
            Decimal(EXPONENT_BIAS)
            + (Decimal(2) / five).ln() / ln2
            + two * log2_phi
        )
        c_int = int(c_real.to_integral_value(rounding=ROUND_HALF_EVEN))
        return phi, log2_phi, d_int, c_real, c_int


PHI_DEC, LOG2_PHI_DEC, D_CANONICAL, C_ASYMPTOTIC_REAL, C_ASYMPTOTIC = decimal_constants()

# Exact high-precision results, frozen as regression guards.
EXPECTED_D_CANONICAL = 0x0016373AD151CA68
EXPECTED_C_ASYMPTOTIC = 0x3FF1109CBE5E8386
if D_CANONICAL != EXPECTED_D_CANONICAL:
    raise AssertionError((D_CANONICAL, EXPECTED_D_CANONICAL))
if C_ASYMPTOTIC != EXPECTED_C_ASYMPTOTIC:
    raise AssertionError((C_ASYMPTOTIC, EXPECTED_C_ASYMPTOTIC))


def bits_of(x: float) -> int:
    return struct.unpack("<Q", struct.pack("<d", x))[0]


def float_of_bits(bits: int) -> float:
    return struct.unpack("<d", struct.pack("<Q", bits & 0xFFFFFFFFFFFFFFFF))[0]


def fib_pair(n: int) -> tuple[int, int]:
    """Return (F_n, F_{n+1}) exactly by iterative fast doubling."""
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    a, b = 0, 1
    for bit in bin(n)[2:]:
        c = a * ((b << 1) - a)
        d = a * a + b * b
        a, b = (d, c + d) if bit == "1" else (c, d)
    return a, b


def golden_pair(n: int) -> tuple[int, int]:
    fn, fn1 = fib_pair(n)
    return fn1, fn


def exact_T(n: int) -> int:
    k, ell = golden_pair(n)
    return k * k + k * ell + ell * ell


def representable_rungs() -> list[tuple[int, int, float, int]]:
    """Return every exact T_n that rounds to a finite binary64 value."""
    out: list[tuple[int, int, float, int]] = []
    n = 0
    while True:
        t = exact_T(n)
        try:
            x = float(t)
        except OverflowError:
            break
        if not math.isfinite(x):
            break
        out.append((n, t, x, bits_of(x)))
        n += 1
    return out


BINARY64_LADDER = representable_rungs()
MAX_BINARY64_RUNG = BINARY64_LADDER[-1][0]
if MAX_BINARY64_RUNG != 737:
    raise AssertionError(MAX_BINARY64_RUNG)


def admissible_constant_interval(
    stride: int,
    ladder: Iterable[tuple[int, int, float, int]] = BINARY64_LADDER,
) -> tuple[int, int]:
    """Exact C interval for nearest-integer classification of all ladder points.

    The classifier is

        floor((B(T_n) - C + floor(D/2))/D).

    For each n this equals n exactly iff

        B_n + h - (n+1)D < C <= B_n + h - nD,

    with h=floor(D/2). Integer endpoints are intersected without floats.
    """
    if stride <= 0:
        raise ValueError("stride must be positive")
    h = stride // 2
    lower: int | None = None
    upper: int | None = None
    for n, _t, _x, b in ladder:
        lo_n = b + h - (n + 1) * stride + 1
        hi_n = b + h - n * stride
        lower = lo_n if lower is None else max(lower, lo_n)
        upper = hi_n if upper is None else min(upper, hi_n)
    if lower is None or upper is None or lower > upper:
        raise ArithmeticError("empty admissible interval")
    return lower, upper


C_MIN, C_MAX = admissible_constant_interval(D_CANONICAL)
C_ROBUST = (C_MIN + C_MAX) // 2
EXPECTED_C_MIN = 0x3FE6AD27C6055065
EXPECTED_C_MAX = 0x3FFAAD27C6055064
EXPECTED_C_ROBUST = 0x3FF0AD27C6055064
if (C_MIN, C_MAX, C_ROBUST) != (
    EXPECTED_C_MIN,
    EXPECTED_C_MAX,
    EXPECTED_C_ROBUST,
):
    raise AssertionError((C_MIN, C_MAX, C_ROBUST))


def rung_from_bits(x: float, *, constant: int = C_ROBUST, stride: int = D_CANONICAL) -> int:
    """Return the nearest golden-ladder rung for finite binary64 x >= 1.

    This is a classifier, not a membership proof. To certify that x is exactly a
    rounded ladder value, compare x with float(exact_T(returned_n)).
    """
    if not isinstance(x, (float, int)):
        raise TypeError("x must be real")
    xf = float(x)
    if not math.isfinite(xf) or xf < 1.0:
        raise ValueError("oracle domain is finite x >= 1")
    candidate = (bits_of(xf) - constant + stride // 2) // stride
    if candidate < 0 or candidate > MAX_BINARY64_RUNG:
        raise ValueError("x lies outside the certified binary64 ladder range")
    return int(candidate)


def is_rounded_ladder_value(x: float, *, constant: int = C_ROBUST, stride: int = D_CANONICAL) -> bool:
    try:
        n = rung_from_bits(x, constant=constant, stride=stride)
    except (TypeError, ValueError):
        return False
    return float(exact_T(n)) == float(x)


def shell_guess(n: int, *, constant: int = C_ROBUST, stride: int = D_CANONICAL) -> float:
    """Piecewise-linear exp2 guess obtained by reinterpreting affine raw bits."""
    if not isinstance(n, int) or not (0 <= n <= MAX_BINARY64_RUNG):
        raise ValueError(f"n must lie in [0,{MAX_BINARY64_RUNG}]")
    x = float_of_bits(constant + stride * n)
    if not math.isfinite(x) or x <= 0.0:
        raise ArithmeticError("constructed bit pattern is not a positive finite number")
    return x


def exact_shell(n: int) -> int:
    """Exact integer refinement after the bit oracle has supplied n."""
    return exact_T(n)


def classification_failures(constant: int, stride: int) -> list[tuple[int, int]]:
    failures: list[tuple[int, int]] = []
    for n, _t, x, _b in BINARY64_LADDER:
        got = (bits_of(x) - constant + stride // 2) // stride
        if got != n:
            failures.append((n, int(got)))
    return failures


def decision_margin(constant: int, stride: int) -> tuple[int, int]:
    """Return (minimum raw-bit margin, binding rung)."""
    best: tuple[int, int] | None = None
    for n, _t, _x, b in BINARY64_LADDER:
        error = b - constant - n * stride
        # Twice the margin avoids half-integer bookkeeping for odd D.
        margin2 = stride - 2 * abs(error)
        candidate = (margin2, n)
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    return best


def inverse_error(constant: int, stride: int) -> tuple[float, int, float]:
    worst = -1.0
    worst_n = -1
    total = 0.0
    for n, t, _x, _b in BINARY64_LADDER:
        guess = shell_guess(n, constant=constant, stride=stride)
        rel = abs(guess - t) / t
        total += rel
        if rel > worst:
            worst, worst_n = rel, n
    return worst, worst_n, total / len(BINARY64_LADDER)


def analytic_error_bounds() -> dict[str, str]:
    """High-precision bounds proving that the affine log index has wide slack."""
    with localcontext() as ctx:
        ctx.prec = 100
        one = Decimal(1)
        two = Decimal(2)
        ln2 = two.ln()
        phi = PHI_DEC
        log2_phi = LOG2_PHI_DEC

        # psi(u)=u-log2(1+u), u in [0,1). Its minimum occurs at 1/ln2-1.
        u_star = one / ln2 - one
        psi_min = u_star - (one + u_star).ln() / ln2
        psi_max = Decimal(0)

        # Exact correction after factoring (2/5) phi^(2n+2) out of T_n.
        delta_even_max_magnitude = phi ** Decimal(-4) - one / (two * phi ** Decimal(2))
        delta_odd_max = phi ** Decimal(-8) + one / (two * phi ** Decimal(4))
        log_corr_min = (one + delta_even_max_magnitude).ln() / ln2
        log_corr_max = (one + delta_odd_max).ln() / ln2

        total_min = psi_min + log_corr_min
        total_max = psi_max + log_corr_max
        if not (-log2_phi < total_min < total_max < log2_phi):
            raise AssertionError((total_min, total_max, log2_phi))
        return {
            "psi_min": str(+psi_min),
            "psi_max": str(+psi_max),
            "log_correction_min": str(+log_corr_min),
            "log_correction_max": str(+log_corr_max),
            "total_min": str(+total_min),
            "total_max": str(+total_max),
            "half_rung_log2_phi": str(+log2_phi),
        }


@dataclass(frozen=True)
class OracleReceipt:
    max_binary64_rung: int
    representable_count: int
    d_canonical_hex: str
    c_asymptotic_hex: str
    c_min_hex: str
    c_max_hex: str
    c_robust_hex: str
    c_legacy_hex: str
    legacy_stride_hex: str
    interval_width: int
    robust_min_margin_twice: int
    robust_binding_rung: int
    robust_max_inverse_relative_error: float
    robust_max_inverse_error_rung: int
    robust_mean_inverse_relative_error: float
    asymptotic_failures: int
    robust_failures: int
    legacy_failures: int
    analytic_bounds: dict[str, str]


def build_receipt() -> OracleReceipt:
    margin2, binding = decision_margin(C_ROBUST, D_CANONICAL)
    worst, worst_n, mean = inverse_error(C_ROBUST, D_CANONICAL)
    return OracleReceipt(
        max_binary64_rung=MAX_BINARY64_RUNG,
        representable_count=len(BINARY64_LADDER),
        d_canonical_hex=f"0x{D_CANONICAL:016X}",
        c_asymptotic_hex=f"0x{C_ASYMPTOTIC:016X}",
        c_min_hex=f"0x{C_MIN:016X}",
        c_max_hex=f"0x{C_MAX:016X}",
        c_robust_hex=f"0x{C_ROBUST:016X}",
        c_legacy_hex=f"0x{C_LEGACY:016X}",
        legacy_stride_hex=f"0x{D_LEGACY:016X}",
        interval_width=C_MAX - C_MIN + 1,
        robust_min_margin_twice=margin2,
        robust_binding_rung=binding,
        robust_max_inverse_relative_error=worst,
        robust_max_inverse_error_rung=worst_n,
        robust_mean_inverse_relative_error=mean,
        asymptotic_failures=len(classification_failures(C_ASYMPTOTIC, D_CANONICAL)),
        robust_failures=len(classification_failures(C_ROBUST, D_CANONICAL)),
        legacy_failures=len(classification_failures(C_LEGACY, D_LEGACY)),
        analytic_bounds=analytic_error_bounds(),
    )


def report() -> str:
    receipt = build_receipt()
    margin_fraction = Decimal(receipt.robust_min_margin_twice) / Decimal(2 * D_CANONICAL)
    lines = [
        "=" * 78,
        "THE GOLDEN BINARY64 ORACLE -- DERIVATION, PLATEAU, AND RECEIPT",
        "=" * 78,
        f"representable exact ladder values : n = 0 .. {MAX_BINARY64_RUNG}",
        f"count                              : {len(BINARY64_LADDER)}",
        f"T_{MAX_BINARY64_RUNG} decimal digits             : {len(str(exact_T(MAX_BINARY64_RUNG)))}",
        "",
        "canonical asymptotic constants (120-digit Decimal derivation)",
        f"  D = round(2^53 log2(phi))        : 0x{D_CANONICAL:016X}",
        f"  C_asym                           : 0x{C_ASYMPTOTIC:016X}",
        "",
        "exact finite-set admissible interval for C at canonical D",
        f"  C_min                            : 0x{C_MIN:016X}",
        f"  C_max                            : 0x{C_MAX:016X}",
        f"  width                            : {C_MAX-C_MIN+1} = 5*2^50",
        f"  robust midpoint                  : 0x{C_ROBUST:016X}",
        f"  minimum decision margin / D      : {margin_fraction}",
        "",
        "lineage constant",
        f"  supplied C_legacy                : 0x{C_LEGACY:016X}",
        f"  supplied D_legacy                : 0x{D_LEGACY:016X}",
        "",
        "classification over every representable exact T_n",
        f"  asymptotic constant failures     : {receipt.asymptotic_failures}",
        f"  robust midpoint failures         : {receipt.robust_failures}",
        f"  supplied legacy failures         : {receipt.legacy_failures}",
        "",
        "inverse bit-cast guess using robust midpoint",
        f"  worst relative error             : {receipt.robust_max_inverse_relative_error:.12e}",
        f"  worst rung                       : {receipt.robust_max_inverse_error_rung}",
        f"  mean relative error              : {receipt.robust_mean_inverse_relative_error:.12e}",
        "",
        "verdict",
        "  the classifier is exact on the certified finite binary64 ladder;",
        "  the reconstructed shell value remains an approximation until snapped",
        "  to exact_T(n). The magic is an admissible interval, not a unique point.",
    ]
    return "\n".join(lines)


def write_receipt(path: Path) -> None:
    path.write_text(json.dumps(asdict(build_receipt()), indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    print(report())
