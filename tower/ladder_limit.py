#!/usr/bin/env python3
"""
ladder_limit.py -- what does T*lambda_2 ACTUALLY converge to?

THEA section X derives 2*pi/(5*sqrt3) = 0.7255197 from three gifts (the
honeycomb stencil, the area bookkeeping, the sphere's l(l+1) ladder). Two
measured rungs (T=1, T=3) approached it from above and looked like agreement.

Eleven rungs do not. The sequence CROSSES the derived value near T=7 and keeps
descending. This extrapolates the real limit and tests whether the derived
constant is even in the running.

LANE: DISPLAY. numpy eigh -> LAPACK, not the certified + - * / sqrt path.
Every number here is COMPUTED.
"""
import math
import sys

import numpy as np

sys.path.insert(0, ".")
import goldberg_modes as gm

DERIVED = 2.0 * math.pi / (5.0 * math.sqrt(3.0))

RUNGS = [(1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (2, 2), (3, 1), (4, 0),
         (3, 2), (4, 1), (5, 0), (4, 2), (5, 1), (4, 3), (6, 0), (5, 2),
         (6, 1), (4, 4), (5, 3), (7, 0)]


def main():
    data = []
    print("  %-8s %-6s %-6s %-13s %s" % ("(k,l)", "T", "V", "T*lambda_2", "minus derived"))
    for (k, l) in RUNGS:
        T = k * k + k * l + l * l
        try:
            w, V, T2, n = gm.tones(k, l)
        except Exception as e:
            print("  (%d,%d)   T=%-5d FAILED: %s" % (k, l, T, str(e)[:40]))
            continue
        prod = T * float(w[1])
        data.append((T, prod, n))
        print("  (%d,%d)    %-6d %-6d %-13.7f %+.7f" % (k, l, T, n, prod, prod - DERIVED))

    if len(data) < 4:
        return
    data.sort()

    # fit  T*lambda_2 = L + c/T  on the deepest rungs, then also L + c/T + d/T^2
    print()
    for tail in (4, 6, 8):
        sub = data[-tail:]
        A = np.array([[1.0, 1.0 / T] for T, _, _ in sub])
        y = np.array([p for _, p, _ in sub])
        (L, c), *_ = np.linalg.lstsq(A, y, rcond=None)
        A2 = np.array([[1.0, 1.0 / T, 1.0 / (T * T)] for T, _, _ in sub])
        (L2, c2, d2), *_ = np.linalg.lstsq(A2, y, rcond=None)
        print("  last %-2d rungs:  L + c/T  -> L = %.7f      L + c/T + d/T^2 -> L = %.7f"
              % (tail, L, L2))

    print()
    print("  derived 2*pi/(5*sqrt3) = %.7f" % DERIVED)
    sub = data[-8:]
    A2 = np.array([[1.0, 1.0 / T, 1.0 / (T * T)] for T, _, _ in sub])
    y = np.array([p for _, p, _ in sub])
    (L2, _, _), *_ = np.linalg.lstsq(A2, y, rcond=None)
    print("  extrapolated limit     = %.7f" % L2)
    print("  difference             = %+.7f   (%.3f%%)" % (L2 - DERIVED, 100 * (L2 - DERIVED) / DERIVED))

    # is the extrapolated limit a nicer constant?
    print("\n  candidates near the extrapolated limit:")
    cands = {
        "2*pi/(5*sqrt3)": DERIVED,
        "pi/(2*sqrt3)*4/5": math.pi / (2 * math.sqrt(3)) * 4 / 5,
        "sqrt(3)*5/12": math.sqrt(3) * 5 / 12,
        "9/(4*pi)": 9 / (4 * math.pi),
        "pi^2/(2*3^1.5)*0.8": math.pi ** 2 / (2 * 3 ** 1.5) * 0.8,
        "0.5*sqrt(2.1)": 0.5 * math.sqrt(2.1),
    }
    for name, v in sorted(cands.items(), key=lambda kv: abs(kv[1] - L2)):
        print("    %-22s %.7f   diff %+.7f" % (name, v, v - L2))


if __name__ == "__main__":
    main()
