#!/usr/bin/env python3
"""
ladder_probe.py -- the third rung, and the disconfirming check.

TWO QUESTIONS, both owed by grimoire/SHADE_MAGIC.md:

  #2  T*lambda_2 -> 2*pi/(5*sqrt3) had TWO measured rungs. Two points are a
      trend, not a convergence. This climbs further.

  #4  Does the Goldberg mesh give a number a GENERIC sphere discretisation
      does not? If every local-parallel scheme lands on the same limit, the
      12 pentagons are decoration on the physics.

LANE: this is the DISPLAY lane. numpy's eigh uses LAPACK, not the certified
+ - * / sqrt path. Numbers here are COMPUTED, never EXACT. That matters most
at the top of the ladder, which is the whole point of looking.
"""
import math
import sys

import numpy as np

sys.path.insert(0, ".")
import goldberg_modes as gm

LIMIT = 2.0 * math.pi / (5.0 * math.sqrt(3.0))

# (k,l) -> T = k^2 + kl + l^2
RUNGS = [(1, 0), (1, 1), (2, 0), (2, 1), (3, 0), (2, 2),
         (3, 1), (4, 0), (3, 2), (4, 1), (5, 0)]


def rung(k, l):
    w, V, T, n = gm.tones(k, l)
    lam0, lam2 = float(w[0]), float(w[1])
    return T, n, lam0, lam2


def main():
    print("  derived limit  2*pi/(5*sqrt3) = %.7f\n" % LIMIT)
    print("  %-8s %-5s %-7s %-12s %-12s %-12s %s" %
          ("(k,l)", "T", "V", "lambda_0", "lambda_2", "T*lambda_2", "gap"))
    prev = None
    for (k, l) in RUNGS:
        try:
            T, n, lam0, lam2 = rung(k, l)
        except Exception as e:
            print("  (%d,%d)    FAILED: %s" % (k, l, e))
            continue
        prod = T * lam2
        gap = prod - LIMIT
        ratio = ""
        if prev is not None and gap != 0:
            ratio = "  x%.2f" % (prev / gap) if gap != 0 else ""
        print("  (%d,%d)    %-5d %-7d %-12.3e %-12.6f %-12.6f %+.6f%s" %
              (k, l, T, n, lam0, lam2, prod, gap, ratio))
        prev = gap


if __name__ == "__main__":
    main()
