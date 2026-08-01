#!/usr/bin/env python3
"""
goldberg_modes.py -- the graph-Laplacian TONES of the golden buckyballs.
KERNELIMAGIC compliant: ASCII-only, one job. Depends on goldberg_gc.py (verified).

GENESIS v8.3: to hear how the NET sounds, we listen to its graph Laplacian
L = D - A (the honest discrete Fourier basis on the graph). Eigenvectors are the
standing-wave modes; eigenvalues are the squared tones. This kernel builds each
certified golden shell (from goldberg_gc.py), forms L, and reports:
  - lambda_2 (Fiedler value = fundamental tone^2) and its degeneracy,
  - the first several distinct tones,
so the in-browser solver (deflated power iteration on cI - L) has an exact target
to match (proof by kernel across the language seam).

Note: every golden shell is a cubic (3-regular) fullerene, so L = 3I - A and the
tones live in [0, 6]. For C60 the Fiedler value is a known icosahedral quantity.

Run:
    py -3 goldberg_modes.py            # human table
    py -3 goldberg_modes.py --json     # machine receipt (targets for the sim)

spini. P=12. chi=2. The pentagons hold; the net sings its Laplacian.
"""
import json
import sys

import numpy as np

import goldberg_gc as gg


def laplacian(fverts, faces):
    """L = D - A from the fullerene faces (each face ring gives its edges)."""
    n = len(fverts)
    # map vertex position -> index via rounded key (faces store position copies)
    key = lambda p: (round(p[0] * 1e6), round(p[1] * 1e6), round(p[2] * 1e6))
    idx = {key(v): i for i, v in enumerate(fverts)}
    A = np.zeros((n, n))
    for ring in faces:
        m = len(ring)
        for i in range(m):
            a, b = ring[i], ring[(i + 1) % m]
            A[a, b] = 1.0
            A[b, a] = 1.0
    D = np.diag(A.sum(axis=1))
    return D - A, A


def tones(k, l):
    fv, fc, T = gg.build_fullerene(k, l)
    # faces store index rings already (gg returns rings of vertex indices)
    n = len(fv)
    A = np.zeros((n, n))
    for ring in fc:
        m = len(ring)
        for i in range(m):
            a, b = ring[i], ring[(i + 1) % m]
            A[a, b] = 1.0
            A[b, a] = 1.0
    L = np.diag(A.sum(axis=1)) - A
    w, V = np.linalg.eigh(L)  # ascending, symmetric
    return w, V, T, n


def distinct(vals, tol=1e-6):
    out = []
    for x in vals:
        if not out or abs(x - out[-1][0]) > tol:
            out.append([float(x), 1])
        else:
            out[-1][1] += 1
    return out


def main():
    shells = gg.GOLDEN
    if "--json" in sys.argv:
        receipt = {"schema": "goldberg_modes.v1", "shells": []}
        for (k, l) in shells:
            w, V, T, n = tones(k, l)
            fiedler = V[:, 1].tolist()
            receipt["shells"].append({
                "k": k, "l": l, "T": T, "n": n,
                "lambda2": float(w[1]),
                "lambda2_deg": distinct(w)[1][1] if len(distinct(w)) > 1 else 1,
                "lambda_max": float(w[-1]),
                "first_tones": [round(v[0], 8) for v in distinct(w)[:6]],
                "fiedler": fiedler,
            })
        print(json.dumps(receipt))
        return

    print("GOLDBERG GOLDEN SHELLS -- the graph-Laplacian TONES (proof by kernel)")
    print("  n  (k,l)     T     N     lambda2(fund)   deg   lambda_max   first distinct tones")
    for n_i, (k, l) in enumerate(shells):
        w, V, T, N = tones(k, l)
        dd = distinct(w)
        deg2 = dd[1][1] if len(dd) > 1 else 1
        tons = ", ".join("%.5f" % v[0] for v in dd[:5])
        print("  %d  (%2d,%2d) %5d %5d   %.8f   x%-2d   %.6f   [%s]" % (
            n_i, k, l, T, N, w[1], deg2, w[-1], tons))
    print("\nThe fundamental tone^2 = lambda_2. C20 (dodecahedron) = 3 - sqrt(5) = 0.76393.")
    print("Every shell is cubic (3-regular): L = 3I - A, tones in [0, 6].")


if __name__ == "__main__":
    main()
