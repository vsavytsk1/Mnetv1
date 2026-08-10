"""SOL TOWER, SEALED v2.1.

One deterministic entry and no command-line options. Import intentionally runs
SEAL(). The mathematical core is exact integer arithmetic; the binary64 oracle
is certified against every exact golden-ladder value representable as finite
binary64 (n=0,...,737).

This revision repairs the first seal in five ways:

1. The binary64 stride is derived at high precision, not through binary64 log2.
2. The "magic constant" is exposed as an admissible interval; the chosen value
   is the exact midpoint of that interval, not a unique mystical number.
3. Source discovery follows this code object's origin, never an inherited
   caller __file__, so exec() cannot accidentally hash its wrapper.
4. The bytecode digest is computed lazily after SEAL is defined and normalized
   to remove path dependence.
5. A self-hash is called an integrity fingerprint, not authenticated provenance.
   Authentication still requires the detached release manifest.

Entry paths:

    python sol_tower_sealed_v2.py
    python -m sol_tower_sealed_v2
    import sol_tower_sealed_v2
    runpy.run_path(path)
    exec(open(path).read())              -> OPEN: source origin unreachable
    exec(compile(src, real_path, 'exec'))

The source is bounded, deterministic, and reads no environment variables,
network resources, command-line options, or working-directory inventory.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_EVEN, localcontext
import hashlib
from pathlib import Path
import struct
import sys
import types

# Preserve idempotence across importlib.reload(), which reuses the module dict.
if "_SOL_SEAL_EMITTED" not in globals():
    _SOL_SEAL_EMITTED = False

# ---------------------------------------------------------------------------
# I. Seed and exact ladder
# ---------------------------------------------------------------------------

DODECAHEDRON = {
    "points": 20,
    "lines": 30,
    "faces": 12,
    "T": 1,
    "kl": (1, 0),
}


def fib_pair(n: int) -> tuple[int, int]:
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    a, b = 0, 1
    for bit in bin(n)[2:]:
        c = a * ((b << 1) - a)
        d = a * a + b * b
        a, b = (d, c + d) if bit == "1" else (c, d)
    return a, b


def golden(n: int) -> tuple[int, int]:
    fn, fn1 = fib_pair(n)
    return fn1, fn


def hex_norm(k: int, ell: int) -> int:
    return k * k + k * ell + ell * ell


def exact_T(n: int) -> int:
    return hex_norm(*golden(n))


def topology(T: int) -> dict[str, int]:
    V, E, F = 20 * T, 30 * T, 10 * T + 2
    return {
        "T": T,
        "V": V,
        "E": E,
        "F": F,
        "P": 12,
        "H": 10 * (T - 1),
        "chi": V - E + F,
    }


def cassini(k: int, ell: int) -> int:
    return k * k - k * ell - ell * ell


def su3_dim(p: int, q: int) -> int:
    return (p + 1) * (q + 1) * (p + q + 2) // 2


def su3_casimir_x3(p: int, q: int) -> int:
    return hex_norm(p, q) + 3 * (p + q)


# ---------------------------------------------------------------------------
# II. Binary64 oracle
# ---------------------------------------------------------------------------

MANTISSA_BITS = 52
SCALE = 1 << MANTISSA_BITS
EXPONENT_BIAS = 1023


def _derive_constants() -> tuple[int, int]:
    with localcontext() as ctx:
        ctx.prec = 120
        two = Decimal(2)
        five = Decimal(5)
        phi = (Decimal(1) + five.sqrt()) / two
        ln2 = two.ln()
        log2phi = phi.ln() / ln2
        stride = int(
            (Decimal(1 << 53) * log2phi).to_integral_value(
                rounding=ROUND_HALF_EVEN
            )
        )
        intercept = int(
            (
                Decimal(SCALE)
                * (
                    Decimal(EXPONENT_BIAS)
                    + (Decimal(2) / five).ln() / ln2
                    + two * log2phi
                )
            ).to_integral_value(rounding=ROUND_HALF_EVEN)
        )
        return stride, intercept


D_CANONICAL, C_ASYMPTOTIC = _derive_constants()
if D_CANONICAL != 0x0016373AD151CA68:
    raise AssertionError("canonical stride changed")
if C_ASYMPTOTIC != 0x3FF1109CBE5E8386:
    raise AssertionError("asymptotic intercept changed")

# Supplied Opus-5 values retained as lineage checks.
C_LEGACY = 0x3FF100E2F21F7C00
D_LEGACY = 0x0016373AD151CA69


def bits_of(x: float) -> int:
    return struct.unpack("<Q", struct.pack("<d", x))[0]


def float_of_bits(bits: int) -> float:
    return struct.unpack("<d", struct.pack("<Q", bits & 0xFFFFFFFFFFFFFFFF))[0]


def _binary64_ladder() -> tuple[tuple[int, int, float, int], ...]:
    out = []
    n = 0
    while True:
        T = exact_T(n)
        try:
            x = float(T)
        except OverflowError:
            break
        if not (x > 0.0 and x < float("inf")):
            break
        out.append((n, T, x, bits_of(x)))
        n += 1
    return tuple(out)


BINARY64_LADDER = _binary64_ladder()
MAX_BINARY64_RUNG = BINARY64_LADDER[-1][0]
if MAX_BINARY64_RUNG != 737:
    raise AssertionError(MAX_BINARY64_RUNG)


def admissible_interval(stride: int) -> tuple[int, int]:
    h = stride // 2
    lower = max(
        bits + h - (n + 1) * stride + 1
        for n, _T, _x, bits in BINARY64_LADDER
    )
    upper = min(
        bits + h - n * stride
        for n, _T, _x, bits in BINARY64_LADDER
    )
    if lower > upper:
        raise ArithmeticError("empty oracle interval")
    return lower, upper


C_MIN, C_MAX = admissible_interval(D_CANONICAL)
C_ROBUST = (C_MIN + C_MAX) // 2
if (C_MIN, C_MAX, C_ROBUST) != (
    0x3FE6AD27C6055065,
    0x3FFAAD27C6055064,
    0x3FF0AD27C6055064,
):
    raise AssertionError("oracle plateau changed")


def rung(T: float) -> int:
    """Nearest certified rung for finite binary64 T >= 1.

    This classifies; it does not prove membership in the exact ladder.
    """
    x = float(T)
    if not (x >= 1.0 and x < float("inf")):
        raise ValueError("T must be finite and >= 1")
    n = (bits_of(x) - C_ROBUST + D_CANONICAL // 2) // D_CANONICAL
    if not (0 <= n <= MAX_BINARY64_RUNG):
        raise ValueError("T is outside the certified binary64 ladder range")
    return int(n)


def shell_guess(n: int) -> float:
    """Approximate T_n by affine raw bits; exact_shell(n) is the exact integer."""
    if not isinstance(n, int) or not (0 <= n <= MAX_BINARY64_RUNG):
        raise ValueError(f"n must lie in [0,{MAX_BINARY64_RUNG}]")
    x = float_of_bits(C_ROBUST + D_CANONICAL * n)
    if not (x > 0.0 and x < float("inf")):
        raise ArithmeticError("constructed pattern is not positive finite binary64")
    return x


def exact_shell(n: int) -> int:
    return exact_T(n)


def is_rounded_shell(T: float) -> bool:
    try:
        n = rung(T)
    except (TypeError, ValueError):
        return False
    return float(exact_T(n)) == float(T)


def _oracle_failures(constant: int, stride: int) -> list[tuple[int, int]]:
    out = []
    for n, _T, x, _bits in BINARY64_LADDER:
        got = (bits_of(x) - constant + stride // 2) // stride
        if got != n:
            out.append((n, int(got)))
    return out


# ---------------------------------------------------------------------------
# III. Exact Light-Matrix invariants
# ---------------------------------------------------------------------------

M_LIGHT = (
    (1, 2, 1, 0),
    (1, 1, 0, 0),
    (1, 0, 0, 0),
    (0, 0, 0, 1),
)
GAMMA = (
    (1, -1, 0, 0),
    (-1, -1, 1, 0),
    (0, 1, 1, 0),
    (0, 0, 0, 1),
)
Q_F = ((1, 1), (1, 0))
J2 = ((2, -1), (-1, -2))


def transpose(A):
    return tuple(zip(*A))


def matmul(A, B):
    return tuple(
        tuple(
            sum(A[i][k] * B[k][j] for k in range(len(B)))
            for j in range(len(B[0]))
        )
        for i in range(len(A))
    )


def det_bareiss(A) -> int:
    n = len(A)
    M = [list(row) for row in A]
    sign, previous = 1, 1
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
                M[i][j] = (
                    M[i][j] * M[k][k] - M[i][k] * M[k][j]
                ) // previous
        previous = M[k][k]
    return sign * M[-1][-1]


def inertia_by_minors(A) -> tuple[int, int]:
    n = len(A)
    minors = [1] + [
        det_bareiss([list(row[:m]) for row in A[:m]])
        for m in range(1, n + 1)
    ]
    if any(value == 0 for value in minors):
        raise ArithmeticError("zero leading principal minor")
    negative = sum(
        1 for i in range(n) if minors[i] * minors[i + 1] < 0
    )
    return n - negative, negative


# ---------------------------------------------------------------------------
# IV. Integrity fingerprints
# ---------------------------------------------------------------------------


def _code_origin() -> str:
    """Origin embedded in this function's code object, never caller __file__."""
    return _code_origin.__code__.co_filename


def _source_material() -> tuple[str | None, bytes | None]:
    spec = globals().get("__spec__")
    loader = getattr(spec, "loader", None) if spec is not None else None
    name = getattr(spec, "name", None) if spec is not None else None
    if loader is not None and name and hasattr(loader, "get_source"):
        try:
            source = loader.get_source(name)
        except Exception:
            source = None
        if source is not None:
            return "source", source.encode("utf-8")

    origin = _code_origin()
    if origin and not origin.startswith("<"):
        path = Path(origin)
        if path.suffix == ".py":
            try:
                return "source", path.read_bytes()
            except OSError:
                pass

    # A compiled image can be fingerprinted, but it is not source provenance.
    runtime_file = globals().get("__file__")
    if isinstance(runtime_file, str) and runtime_file.endswith((".pyc", ".pyo")):
        try:
            return "image", Path(runtime_file).read_bytes()
        except OSError:
            pass
    return None, None


def _constant_record(value):
    """Canonical, identity-free serialization input for code constants."""
    if isinstance(value, types.CodeType):
        return ("code", _code_record(value))
    if isinstance(value, tuple):
        return ("tuple", tuple(_constant_record(item) for item in value))
    if isinstance(value, frozenset):
        return ("frozenset", tuple(sorted(repr(item) for item in value)))
    if isinstance(value, bytes):
        return ("bytes", value.hex())
    if isinstance(value, (str, int, float, complex, type(None), bool)):
        return (type(value).__name__, repr(value))
    return (type(value).__name__, repr(value))


def _code_record(code: types.CodeType):
    """Path-independent semantic bytecode record for one code object."""
    return (
        code.co_name,
        code.co_qualname,
        code.co_argcount,
        code.co_posonlyargcount,
        code.co_kwonlyargcount,
        code.co_nlocals,
        code.co_stacksize,
        code.co_flags,
        code.co_code.hex(),
        tuple(_constant_record(value) for value in code.co_consts),
        code.co_names,
        code.co_varnames,
        code.co_freevars,
        code.co_cellvars,
        code.co_exceptiontable.hex(),
    )


def _bytecode_fingerprint() -> str:
    records = []
    for name in sorted(globals()):
        obj = globals()[name]
        if isinstance(obj, types.FunctionType):
            records.append((name, _code_record(obj.__code__)))
    if not records:
        raise AssertionError("no function bytecode found")
    payload = repr(tuple(records)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------------------
# V. Single entry
# ---------------------------------------------------------------------------


def SEAL() -> None:
    global _SOL_SEAL_EMITTED
    if _SOL_SEAL_EMITTED:
        return
    _SOL_SEAL_EMITTED = True

    say = sys.stdout.write
    width = 78
    source_kind, source_bytes = _source_material()
    source_sha = (
        hashlib.sha256(source_bytes).hexdigest()
        if source_bytes is not None
        else None
    )
    bytecode_sha = _bytecode_fingerprint()

    say("=" * width + "\n")
    say("SOL TOWER, SEALED v2.1 -- exact ladder, honest oracle, honest seal\n")
    say("=" * width + "\n")
    say(f"  entry name             : {__name__!r}\n")
    say(f"  code origin            : {_code_origin()!r}\n")
    if source_kind == "source":
        say(f"  source fingerprint     : {source_sha}\n")
        say("  source status          : REACHABLE (fingerprint, not authentication)\n")
    elif source_kind == "image":
        say(f"  compiled-image hash    : {source_sha}\n")
        say("  source status          : UNREACHABLE\n")
    else:
        say("  source fingerprint     : UNREACHABLE\n")
        say("  source status          : OPEN\n")
    say(f"  normalized bytecode    : {bytecode_sha}\n")
    say(
        f"  interpreter            : CPython "
        f"{'.'.join(map(str, sys.version_info[:3]))}; optimize={sys.flags.optimize}\n"
    )
    say("  trust boundary         : detached manifest required for authenticity\n\n")

    say("-" * width + "\n")
    say("  I. SEED AND EXACT TOPOLOGY\n")
    say("-" * width + "\n")
    seed = topology(1)
    say(
        "  dodecahedron           : "
        f"V={seed['V']} E={seed['E']} F={seed['F']} "
        f"P={seed['P']} H={seed['H']} chi={seed['chi']}\n"
    )
    say(
        "  shared A2 labels       : "
        f"(1,0), SU(3) dim={su3_dim(1,0)}, 3*C2={su3_casimir_x3(1,0)}\n\n"
    )

    say("-" * width + "\n")
    say("  II. BINARY64 ORACLE\n")
    say("-" * width + "\n")
    say(f"  canonical stride D     : 0x{D_CANONICAL:016X}\n")
    say(f"  asymptotic C           : 0x{C_ASYMPTOTIC:016X}\n")
    say(f"  admissible C interval  : [0x{C_MIN:016X}, 0x{C_MAX:016X}]\n")
    say(f"  robust midpoint C      : 0x{C_ROBUST:016X}\n")
    say(f"  legacy plateau member  : 0x{C_LEGACY:016X}\n")
    say(f"  finite binary64 ladder : n=0..{MAX_BINARY64_RUNG} ({len(BINARY64_LADDER)} values)\n")

    failures_robust = _oracle_failures(C_ROBUST, D_CANONICAL)
    failures_asym = _oracle_failures(C_ASYMPTOTIC, D_CANONICAL)
    failures_legacy = _oracle_failures(C_LEGACY, D_LEGACY)
    say(
        "  classification misses  : "
        f"robust={len(failures_robust)}, "
        f"asymptotic={len(failures_asym)}, "
        f"legacy={len(failures_legacy)}\n"
    )
    worst_rel = 0.0
    worst_n = -1
    for n, T, _x, _bits in BINARY64_LADDER:
        rel = abs(shell_guess(n) - T) / T
        if rel > worst_rel:
            worst_rel, worst_n = rel, n
    say(
        f"  shell_guess max error  : {worst_rel:.12e} at n={worst_n}; "
        "exact_shell(n) removes it\n"
    )
    for n in (0, 1, 2, 3, 5, 8, 13, 45, 737):
        T = exact_T(n)
        say(
            f"    n={n:<3d} T digits={len(str(T)):<3d} "
            f"rung(float(T))={rung(float(T)):<3d} "
            f"member={is_rounded_shell(float(T))}\n"
        )
    say("\n")

    say("-" * width + "\n")
    say("  III. GOLDEN / SU(3)-LATTICE LEDGER\n")
    say("-" * width + "\n")
    exact_ok = True
    for n in range(24):
        k, ell = golden(n)
        T = hex_norm(k, ell)
        topo = topology(T)
        row_ok = (
            topo["chi"] == 2
            and topo["P"] == 12
            and cassini(k, ell) == (-1) ** n
            and rung(float(T)) == n
        )
        exact_ok = exact_ok and row_ok
        if n < 9 or n == 23:
            say(
                f"  {n:2d}: (k,l)=({k},{ell}) "
                f"T={T} V={topo['V']} chi={topo['chi']} "
                f"dim_SU3={su3_dim(k,ell)} 3C2={su3_casimir_x3(k,ell)}\n"
            )
    say(
        "  status                 : exact lattice identities; "
        "no QCD dynamics inferred\n\n"
    )

    say("-" * width + "\n")
    say("  IV. LIGHT-MATRIX INVARIANTS\n")
    say("-" * width + "\n")
    preserved = matmul(matmul(transpose(M_LIGHT), GAMMA), M_LIGHT) == GAMMA
    det_gamma = det_bareiss(GAMMA)
    inertia = inertia_by_minors(GAMMA)
    anti = matmul(matmul(transpose(Q_F), J2), Q_F) == tuple(
        tuple(-entry for entry in row) for row in J2
    )
    intervals = set()
    for n in range(120):
        k, ell = golden(n)
        s = (k * k, k * ell, ell * ell, 12)
        intervals.add(
            sum(
                GAMMA[i][j] * s[i] * s[j]
                for i in range(4)
                for j in range(4)
            )
        )
    say(f"  M^T Gamma M = Gamma   : {preserved}\n")
    say(f"  det Gamma             : {det_gamma}\n")
    say(f"  inertia Gamma         : {inertia}\n")
    say(f"  Q^T (2J) Q = -(2J)    : {anti}\n")
    say(f"  s^T Gamma s           : {sorted(intervals)}\n\n")

    math_ok = (
        exact_ok
        and not failures_robust
        and not failures_asym
        and not failures_legacy
        and preserved
        and det_gamma == -3
        and inertia == (3, 1)
        and anti
        and intervals == {145}
    )

    say("=" * width + "\n")
    if not math_ok:
        say("  BROKEN: at least one invariant failed; no seal is claimed.\n")
    elif source_kind == "source":
        say("  SEALED: mathematics closed; source bytes reachable and fingerprinted.\n")
        say("          authenticity remains external to a self-hash; check manifest.\n")
    else:
        say("  OPEN: mathematics closed; source bytes unavailable from this entry.\n")
        say("        incomplete is fine. fake provenance is not.\n")
    say("=" * width + "\n")


SEAL()
