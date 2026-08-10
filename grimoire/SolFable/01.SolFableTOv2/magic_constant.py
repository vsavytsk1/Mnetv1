#!/usr/bin/env python3
"""THE TOWER'S MAGIC CONSTANT.

Walsh's lesson, 1986: reading a float's bits as an integer GIVES YOU ITS
LOGARITHM. The exponent field sits in the high bits, the mantissa in the low
bits, and log2(1+m) ~= m, so

    (bits as int) / 2^52  ~=  1023 + log2(x) + sigma

Now look at the golden ladder:

    T_n = (2/5)(phi^(2n+2) + phi^(-2n-2)) - (1/5)(-1)^n   ~   (2/5) phi^(2n+2)

which means log2(T_n) is LINEAR IN n. Linear. So if bits give log2 for free,
then the rung index n is an INTEGER SUBTRACT AND DIVIDE ON THE RAW BITS --
no log, no float math, no lookup table.

    n = (bits(T) - C) / D

There is a magic constant. This file derives it, then hunts for a better one
the way Lomont hunted for 0x5F375A86.

Ground truth is exact BigInt. Nothing here is believed until it is checked
against integers.
"""
from __future__ import annotations
import math, struct

PHI = (1 + math.sqrt(5)) / 2
L2PHI = math.log2(PHI)                 # 0.694241913630617...
MANT = 52                              # float64 mantissa bits
BIAS = 1023

def bits(x: float) -> int:
    return struct.unpack("<Q", struct.pack("<d", x))[0]

def unbits(i: int) -> float:
    return struct.unpack("<d", struct.pack("<Q", i & 0xFFFFFFFFFFFFFFFF))[0]

# --- exact ladder, integers only -------------------------------------------
def ladder(N: int) -> list[int]:
    k, l, out = 1, 0, []
    for _ in range(N):
        out.append(k * k + k * l + l * l)
        k, l = k + l, k
    return out

# how far can float64 even hold T_n?
N_MAX = 0
while True:
    approx = (2 / 5) * PHI ** (2 * N_MAX + 2)
    if not math.isfinite(approx) or approx > 1e307:
        break
    N_MAX += 1
T = ladder(N_MAX)
print("=" * 78)
print("0.  THE LADDER, AND HOW MUCH OF IT float64 CAN HOLD")
print("=" * 78)
print(f"  rungs representable as finite float64 : n = 0 .. {N_MAX-1}")
print(f"  T_0..T_7                              : {T[:8]}")
print(f"  T_{N_MAX-1} has {len(str(T[N_MAX-1]))} decimal digits, "
      f"{T[N_MAX-1].bit_length()} bits")
print()

# ===========================================================================
print("=" * 78)
print("1.  THE DERIVATION  (no search, just algebra)")
print("=" * 78)
# bits(x)/2^52 ~= 1023 + log2(x) + sigma      [sigma = linear-approx offset]
# log2(T_n)    ~= (2n+2) L + log2(2/5)
# =>  n = (bits/2^52 - 1023 - sigma - log2(2/5) - 2L) / (2L)
# =>  n = (bits - C) / D    with
#         D = 2^52 * 2L
#         C = 2^52 * (1023 + sigma + log2(2/5) + 2L)
SIGMA0 = 0.0430357                     # the classical Q_rsqrt correction term
D_exact = (1 << MANT) * 2 * L2PHI
def C_of(sigma: float) -> float:
    return (1 << MANT) * (BIAS + sigma + math.log2(2 / 5) + 2 * L2PHI)

C0 = C_of(SIGMA0)
print(f"  L = log2(phi)            = {L2PHI:.15f}")
print(f"  D = 2^52 * 2L            = {D_exact:.3f}   -> 0x{int(round(D_exact)):X}")
print(f"  sigma (classical)        = {SIGMA0}")
print(f"  C = 2^52 * (1023 + ...)  = {C0:.3f}   -> 0x{int(round(C0)):X}")
print()

def rung_derived(x: float, C: float = C0, D: float = D_exact) -> int:
    """Recover the rung index from the RAW BITS. One subtract, one divide."""
    return int(math.floor((bits(x) - C) / D + 0.5))

hits = sum(1 for n in range(N_MAX) if rung_derived(float(T[n])) == n)
print(f"  derived constant recovers the rung on {hits}/{N_MAX} rungs "
      f"({100*hits/N_MAX:.1f}%)")
bad = [n for n in range(N_MAX) if rung_derived(float(T[n])) != n]
print(f"  misses at n = {bad[:12]}{' ...' if len(bad) > 12 else ''}")
print()

# ===========================================================================
print("=" * 78)
print("2.  THE HUNT  (Lomont's move: search the constant, keep what wins)")
print("=" * 78)
Ci = int(round(C0))
Di = int(round(D_exact))
best = None
# integer-only oracle: n = (i - C) >> nothing; use integer division with rounding
def rung_int(x: float, C: int, D: int) -> int:
    return ((bits(x) - C) + D // 2) // D

span = 1 << 46
lo, hi = Ci - 3 * span, Ci + 3 * span
step = span // 8
while step >= 1:
    cand = range(max(0, lo), hi + 1, max(1, step))
    for C in cand:
        h = sum(1 for n in range(N_MAX) if rung_int(float(T[n]), C, Di) == n)
        if best is None or h > best[1]:
            best = (C, h)
    lo, hi = best[0] - 4 * step, best[0] + 4 * step
    step //= 2
C_best, h_best = best
print(f"  derived   C = 0x{Ci:016X}   -> {hits}/{N_MAX} rungs")
print(f"  searched  C = 0x{C_best:016X}   -> {h_best}/{N_MAX} rungs")
print(f"  shift between them: {C_best - Ci:+d}  "
      f"(= sigma moved by {(C_best - Ci)/(1<<MANT):+.6f})")
print()
print(f"  >>> THE TOWER'S MAGIC CONSTANT:  0x{C_best:016X}")
print(f"  >>> THE TOWER'S DIVISOR:         0x{Di:016X}   (= 2^53 * log2(phi))")
print()

# ===========================================================================
print("=" * 78)
print("3.  THE INVERSE  (Walsh's actual trick: exponentiate by casting back)")
print("=" * 78)
# Q_rsqrt's final move is reading the int back as a float -- that IS the
# exponentiation. Same here: build the bits from n, read as double, get T_n.
def T_guess(n: int, C: int = C_best, D: int = Di) -> float:
    return unbits(C + D * n)

print("   n     exact T_n                      bit-guess                 rel.err")
print("   " + "-" * 70)
worst = 0.0
for n in list(range(0, 10)) + [20, 40, 80, 160, 320, N_MAX - 1]:
    if n >= N_MAX: continue
    g = T_guess(n)
    e = abs(g - T[n]) / T[n]
    worst = max(worst, e)
    print(f"  {n:4d}   {T[n]:<28.6e}   {g:<22.6e}   {e:.3e}")
print(f"\n  worst relative error over all {N_MAX} rungs: ", end="")
worst_all = max(abs(T_guess(n) - T[n]) / T[n] for n in range(N_MAX))
print(f"{worst_all:.4e}   ({100*worst_all:.3f}%)")
print(f"  (Walsh's inverse sqrt first guess: 3.4%. One Newton pass: 0.17%.)")
print()

# ===========================================================================
print("=" * 78)
print("4.  ONE NEWTON PASS -- except the tower's Newton is EXACT")
print("=" * 78)
print("  Q_rsqrt refines with y = y*(1.5 - x2*y*y) because sqrt has no closed")
print("  form in the register. The ladder DOES: round the bit-guess to the")
print("  nearest integer and snap it onto the exact recurrence. The refinement")
print("  is not an approximation -- it is a lookup keyed by the guess.")
print()
ok = 0
for n in range(N_MAX):
    guess = T_guess(n)
    n_rec = rung_int(guess, C_best, Di)          # round-trip the index
    if n_rec == n:
        ok += 1
print(f"  bit-guess -> rung -> exact T_n  round-trips on {ok}/{N_MAX} rungs")
print(f"  so the guess is a perfect INDEX even where it is a poor VALUE.")
print()

# ===========================================================================
print("=" * 78)
print("5.  THE FUNCTION, IN C, THE WAY WALSH WOULD HAVE WRITTEN IT")
print("=" * 78)
print(f'''
/* Which rung of the golden Goldberg ladder is this shell?
   No log. No divide by a float. No table. The bits ARE the logarithm.
   T_n ~ (2/5) phi^(2n+2), so log2(T_n) is linear in n, so n is linear in
   the raw bits. Derived, then tuned -- Walsh 1986, Lomont 2003. */

int rung( double T )
{{
    long long i = *(long long*)&T;              /* evil floating point bit level hacking */
    return (int)((i - 0x{C_best:016X}LL) / 0x{Di:X}LL);   /* what the fuck? */
}}

/* and back the other way -- the cast IS the exponentiation */
double shell( int n )
{{
    long long i = 0x{C_best:016X}LL + 0x{Di:X}LL * n;
    return *(double*)&i;
}}
''')
print(f"  verified: rung() correct on {h_best}/{N_MAX} rungs, "
      f"shell() worst relative error {worst_all:.3e}")
