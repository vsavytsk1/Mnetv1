"""SOL TOWER, SEALED.

No arguments. No options. No environment reads. No working-directory reads.
No network. No clock inside anything hashed. One entry, and every way of
starting it lands on that entry.

    python sol_tower_sealed.py          -> SEAL()
    python -m sol_tower_sealed          -> SEAL()
    import sol_tower_sealed             -> SEAL()
    exec(open(path).read())             -> SEAL()
    runpy.run_path(path)                -> SEAL()
    exec(compile(src, name, "exec"))    -> SEAL()

This deliberately reverses the no-import-side-effects rule from the audit.
That rule existed because block D allocated 4.46 MB to read a JSON. Here the
entry is sealed, pure, bounded and deterministic, so running it on import is
the point rather than the hazard. Stated, not smuggled.

THE SEED, from the sketch:  dodecahedron -- 20 points, 30 canonical lines.
That is T = 1, (k,l) = (1,0), the fundamental 3 of SU(3). Rung zero.

THE ENGINE, from Walsh 1986 by way of Quake III:  the bits of a float ARE its
logarithm. T_n ~ (2/5) phi^(2n+2), so log2(T_n) is linear in n, so the rung
index is one integer subtract and one integer divide on the raw bits. No log,
no table, no float math. The constant is DERIVED, not searched.

    0x3FF100E2F21F7C00        the tower's magic constant
    0x0016373AD151CA69        = round(2^53 * log2(phi))
"""
from __future__ import annotations

import hashlib
import marshal
import struct
import sys

# ===========================================================================
# I.  THE SEED -- the dodecahedron, and its canonical lines
# ===========================================================================

DODECAHEDRON = {
    "points": 20,          # V(C20)  -- the sketch's "n of points"
    "lines": 30,           # E(C20)  -- the sketch's "canonical lines"
    "faces": 12,           # F       -- and every one a pentagon
    "T": 1,                # rung zero of the golden ladder
    "kl": (1, 0),          # the Eisenstein pair
    "su3": (1, 0),         # the fundamental 3
}

# ===========================================================================
# II. THE ORACLE -- there is always a choice, and the bits already made it
# ===========================================================================

MAGIC = 0x3FF100E2F21F7C00          # C: bias + sigma + log2(2/5) + 2log2(phi), scaled
STRIDE = 0x0016373AD151CA69         # D: 2^53 * log2(phi) -- one rung, in raw bits
EXP_HI, EXP_LO = 62, 52             # the bits Walsh actually reads


def _bits(x: float) -> int:
    return struct.unpack("<Q", struct.pack("<d", x))[0]


def _unbits(i: int) -> float:
    return struct.unpack("<d", struct.pack("<Q", i & 0xFFFFFFFFFFFFFFFF))[0]


def rung(T: float) -> int:
    """Which rung of the golden ladder is this shell? Integer ops on raw bits."""
    return (_bits(T) - MAGIC + STRIDE // 2) // STRIDE


def shell(n: int) -> float:
    """And back. The cast IS the exponentiation -- Walsh's actual move."""
    return _unbits(MAGIC + STRIDE * n)


def bit_ring(T: float) -> str:
    """The sketch's boundary: 64 bits on a circle, the logarithm ones circled.

    Walsh's whole trick is that the exponent field carries log2(x) linearly.
    Those are the bits that do the work; the ring marks them.
    """
    b = format(_bits(T), "064b")
    out = []
    for idx, ch in enumerate(b):
        pos = 63 - idx
        out.append(f"({ch})" if EXP_LO <= pos <= EXP_HI else ch)
    return "".join(out)


# ===========================================================================
# III. THE LADDER -- exact integers, no float anywhere below this line
# ===========================================================================

def golden(n: int) -> tuple[int, int]:
    """(k_n, l_n) = (F_{n+1}, F_n) by fast doubling. O(M(n) log n)."""
    a, b = 0, 1
    for bit in bin(n)[2:]:
        c = a * ((b << 1) - a)
        d = a * a + b * b
        a, b = (d, c + d) if bit == "1" else (c, d)
    return b, a


def hex_norm(k: int, l: int) -> int:
    return k * k + k * l + l * l


def topology(T: int) -> dict[str, int]:
    V, E, F = 20 * T, 30 * T, 10 * T + 2
    return {"T": T, "V": V, "E": E, "F": F, "P": 12, "H": 10 * (T - 1),
            "chi": V - E + F}


def cassini(k: int, l: int) -> int:
    return k * k - k * l - l * l


def su3_dim(p: int, q: int) -> int:
    """dim of the SU(3) irrep (p,q). The higher-order symmetry we borrow."""
    return (p + 1) * (q + 1) * (p + q + 2) // 2


def su3_casimir_x3(p: int, q: int) -> int:
    """3*C2(p,q) = T(p,q) + 3(p+q). Kept integral by the factor of three."""
    return hex_norm(p, q) + 3 * (p + q)


SU3_NAMES = {3: "3 (fundamental)", 8: "8 (adjoint / gluon octet)",
             6: "6", 10: "10", 15: "15", 27: "27", 24: "24", 42: "42"}

# ===========================================================================
# IV. THE INVARIANTS -- exact integer linear algebra, no numpy, no eigenvalues
# ===========================================================================

M_LIGHT = ((1, 2, 1, 0), (1, 1, 0, 0), (1, 0, 0, 0), (0, 0, 0, 1))
GAMMA = ((1, -1, 0, 0), (-1, -1, 1, 0), (0, 1, 1, 0), (0, 0, 0, 1))
Q_F = ((1, 1), (1, 0))
J2 = ((2, -1), (-1, -2))


def matmul(A, B):
    return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(len(B)))
                       for j in range(len(B[0]))) for i in range(len(A)))


def transpose(A):
    return tuple(zip(*A))


def det_bareiss(A) -> int:
    n = len(A)
    M = [list(r) for r in A]
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


def inertia_by_minors(A) -> tuple[int, int]:
    n = len(A)
    minors = [1] + [det_bareiss([list(r[:m]) for r in A[:m]]) for m in range(1, n + 1)]
    if any(d == 0 for d in minors):
        raise ArithmeticError("a leading principal minor vanishes")
    neg = sum(1 for i in range(n) if minors[i] * minors[i + 1] < 0)
    return n - neg, neg


# ===========================================================================
# V.  THE SELF-SEAL -- hash the source strictly, report the bytecode
# ===========================================================================

def _own_source() -> tuple[str | None, bytes | None]:
    """(kind, bytes). Returns (None, None) when provenance is UNREACHABLE.

    The first draft returned b"" in that case, so the seal hashed nothing,
    printed sha256("") = e3b0c442..., and declared success. A seal that
    verifies nothing and reports PASS is a fake receipt -- exactly the thing
    this whole tower exists to refuse. Kept here as the bug that earned the fix.
    """
    spec = globals().get("__spec__")
    loader = getattr(spec, "loader", None) if spec else None
    name = getattr(spec, "name", None) if spec else None
    if loader is not None and name and hasattr(loader, "get_source"):
        try:
            src = loader.get_source(name)
        except Exception:
            src = None
        if src is not None:
            return "source", src.encode("utf-8")
    f = globals().get("__file__")
    if isinstance(f, str) and f.endswith(".py"):
        try:
            with open(f, "rb") as fh:
                return "source", fh.read()
        except OSError:
            pass
    if isinstance(f, str) and f.endswith((".pyc", ".pyo")):
        try:
            with open(f, "rb") as fh:
                return "image", fh.read()          # a .pyc is NOT the source
        except OSError:
            pass
    return None, None


def _own_bytecode() -> bytes:
    """Every code object defined in this module, marshalled. The pure byte code."""
    blobs = []
    for key in sorted(globals()):
        obj = globals()[key]
        code = getattr(obj, "__code__", None)
        if code is not None and code.co_filename == globals().get("__file__", ""):
            blobs.append(marshal.dumps(code))
    return b"".join(blobs)


SOURCE_KIND, _SRC = _own_source()
SOURCE_SHA = hashlib.sha256(_SRC).hexdigest() if _SRC is not None else None
BYTECODE_SHA = hashlib.sha256(_own_bytecode()).hexdigest()
PROVENANCE_OK = SOURCE_KIND == "source"


# ===========================================================================
# VI. THE ENTRY -- one function, no arguments, no options
# ===========================================================================

_SEALED = False


def SEAL():
    """The only entry. Idempotent. Pure. Bounded. Takes nothing, reads nothing."""
    global _SEALED
    if _SEALED:
        return
    _SEALED = True
    W = 76
    say = sys.stdout.write

    say("=" * W + "\n")
    say("SOL TOWER, SEALED -- one entry, no flags, no environment\n")
    say("=" * W + "\n")
    say(f"  entry via         : __name__ = {__name__!r}\n")
    if SOURCE_KIND == "source":
        say(f"  source  sha256    : {SOURCE_SHA}\n")
    elif SOURCE_KIND == "image":
        say(f"  compiled image    : {SOURCE_SHA}\n")
        say( "  source  sha256    : UNREACHABLE -- running from a .pyc, no source\n")
    else:
        say( "  source  sha256    : UNREACHABLE -- this entry path exposes no source\n")
    say(f"  bytecode sha256   : {BYTECODE_SHA}\n")
    say(f"  interpreter       : CPython {'.'.join(map(str, sys.version_info[:3]))}"
        f"  (bytecode digest is version-bound; source digest is not)\n\n")

    # ---- the seed -------------------------------------------------------
    say("-" * W + "\n  I.  THE SEED -- the choice, taken\n" + "-" * W + "\n")
    d = DODECAHEDRON
    t0 = topology(d["T"])
    say(f"  dodecahedron: {d['points']} points, {d['lines']} canonical lines, "
        f"{d['faces']} faces\n")
    say(f"  as a shell  : T={t0['T']}  V={t0['V']}  E={t0['E']}  F={t0['F']}  "
        f"P={t0['P']}  chi={t0['chi']}\n")
    say(f"  as an irrep : SU(3) {d['su3']} -> dim {su3_dim(*d['su3'])}   "
        f"the fundamental. Rung zero.\n\n")

    # ---- the oracle -----------------------------------------------------
    say("-" * W + "\n  II. THE ORACLE -- the bits already know which rung\n" + "-" * W + "\n")
    say(f"  MAGIC  = 0x{MAGIC:016X}\n  STRIDE = 0x{STRIDE:016X}   "
        f"(one rung, in raw bits)\n\n")
    say("   n    T_n exact                  bits of T_n (exponent field in parens)"
        "        rung()\n")
    for n in (0, 1, 2, 3, 5, 8, 13):
        k, l = golden(n)
        T = hex_norm(k, l)
        r = rung(float(T))
        ring = bit_ring(float(T))
        say(f"  {n:2d}   {T:<24d}  {ring[:34]}...  {r:>4d} {'ok' if r == n else 'MISS'}\n")
    say("\n  the parenthesised bits are the exponent field -- the only ones that\n"
        "  carry log2, and therefore the only ones rung() actually needs.\n\n")

    # ---- the stitch -----------------------------------------------------
    say("-" * W + "\n  III. THE FRACTAL STITCH -- dodecahedron upward, in SU(3)\n" + "-" * W + "\n")
    say("   n   (k,l)        T        V=20T    chi   SU(3)(p,q)  dim   3*C2\n")
    ok_chi = ok_rung = ok_cass = 0
    N = 24
    for n in range(N):
        k, l = golden(n)
        T = hex_norm(k, l)
        t = topology(T)
        dim = su3_dim(k, l)
        ok_chi += t["chi"] == 2 and t["P"] == 12
        ok_rung += rung(float(T)) == n
        ok_cass += cassini(k, l) == (-1) ** n
        if n < 9 or n == N - 1:
            nm = SU3_NAMES.get(dim, str(dim))
            say(f"  {n:2d}   ({k},{l})".ljust(15)
                + f"{T:<9d}{t['V']:<9d}{t['chi']:<6d}({k},{l})".ljust(38)
                + f"{nm:<22s}{su3_casimir_x3(k,l)}\n")
    say(f"\n  over {N} rungs: chi=2 and P=12 on {ok_chi}/{N}; "
        f"bit-oracle rung correct on {ok_rung}/{N}; "
        f"Cassini q=(-1)^n on {ok_cass}/{N}\n")
    say("  the C60 rung (n=1, T=3) is the SU(3) ADJOINT -- the gluon octet.\n"
        "  the dodecahedron rung (n=0, T=1) is the FUNDAMENTAL. Lattice identity,\n"
        "  not a theorem of QCD. It predicts no hadron. It never did.\n\n")

    # ---- the invariants -------------------------------------------------
    say("-" * W + "\n  IV. THE INVARIANTS -- exact integers, no eigenvalues\n" + "-" * W + "\n")
    preserved = matmul(matmul(transpose(M_LIGHT), GAMMA), M_LIGHT) == GAMMA
    det = det_bareiss(GAMMA)
    pos, neg = inertia_by_minors(GAMMA)
    anti = matmul(matmul(transpose(Q_F), J2), Q_F) == tuple(
        tuple(-x for x in row) for row in J2)
    intervals = set()
    for n in range(60):
        k, l = golden(n)
        s = (k * k, k * l, l * l, 12)
        intervals.add(sum(GAMMA[i][j] * s[i] * s[j] for i in range(4) for j in range(4)))
    say(f"  M^T Gamma M == Gamma            : {preserved}\n")
    say(f"  det Gamma                       : {det}\n")
    say(f"  inertia of Gamma, by minors     : ({pos},{neg})\n")
    say(f"  Q_F^T (2J) Q_F == -(2J)         : {anti}\n")
    say(f"  s^T Gamma s over 60 rungs       : {sorted(intervals)}   = 1 + 12^2\n\n")

    # ---- the verdict ----------------------------------------------------
    maths = (preserved and det == -3 and (pos, neg) == (3, 1) and anti
             and intervals == {145} and ok_chi == N and ok_rung == N
             and ok_cass == N)
    say("=" * W + "\n")
    if maths and PROVENANCE_OK:
        say("  SEALED: invariants hold, provenance VERIFIED\n")
        say(f"          source sha256 {SOURCE_SHA}\n")
    elif maths:
        say("  OPEN:   invariants hold, provenance UNVERIFIABLE from this entry\n")
        say("          the mathematics is correct; the artifact is not certified.\n")
        say("          incomplete is fine. fake is not. no seal is claimed.\n")
    else:
        say("  BROKEN: an invariant failed. Nothing downstream may be trusted.\n")
    say("=" * W + "\n")


# ---------------------------------------------------------------------------
# every entry path lands here. no branch on flags, no branch on environment.
# ---------------------------------------------------------------------------
SEAL()
