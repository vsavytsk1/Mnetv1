#!/usr/bin/env python3
"""WITNESS 4 -- Python. CPython's bytecode interpreter chooses everything.

chi(T) = 20T - 30T + (10T + 2) = 2, for every T.

Python's ints are ARBITRARY PRECISION, so this witness cannot overflow at all.
It is the only one of the seven with that property, which makes it the
reference when the others start to disagree at scale.
"""
PROBES = [0, 1, 2, 3, 21, 147, 1029, 7203, 50421, 1_000_000]

def chi(t):
    v = 20 * t
    e = 30 * t
    f = 10 * t + 2
    return v - e + f

print("python|" + "|".join(f"{t}:{chi(t)}" for t in PROBES))
