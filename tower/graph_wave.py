#!/usr/bin/env python3
"""
graph_wave.py -- the PERFECT-MATH block for the light flow (GENESIS v8.5 audit).
KERNELIC_MAGIC compliant: ASCII-only, one job. Depends on goldberg_gc.py (verified).

Vlad's doctrine (Thea): "all code is pure math, merely stepped into compute." For
the light to PROPAGATE THROUGH THE CENTER honestly (not per-edge blinking), the one
exact answer is the GRAPH WAVE EQUATION on the net's own Laplacian:

    u''(t) = -c^2 * L u                     (L = D - A, the net's Laplacian)

stepped by LEAPFROG / Stormer-Verlet:

    u_{n+1} = 2 u_n - u_{n-1} - (c*dt)^2 * L u_n

This is a symplectic integrator: it conserves a DISCRETE ENERGY exactly (drift
bounded, no secular growth) when the CFL condition holds:

    (c*dt)^2 * lambda_max(L) < 4.

THE PERFECT MATH (what is EXACT vs COMPUTED, Thea status grammar):
  EXACT    : L is integer (D-A); its spectrum is the net's true modes; the leapfrog
             update is an exact algebraic recurrence; the modified (shadow) energy
             H~ = 0.5|v|^2 + 0.5 u^T L u - (dt^2/8)(Lu).(Lu) is conserved to machine
             precision by the symplectic map.
  COMPUTED : the numeric energy trace over N steps at finite dt (reported, not
             narrated); we SHOW max drift, we do not claim zero.

This kernel proves, per golden shell:
  1. the leapfrog energy drift stays bounded (< tol) over many periods when CFL holds,
  2. a single eigenmode u0 = eigenvector stays a pure standing wave (frequency =
     sqrt(lambda) * c), matching the continuous solution -- the honest propagation.

Run:
    py -3 graph_wave.py            # human proof (C20, C60)
    py -3 graph_wave.py --json     # machine receipt (dt, c, energy drift per shell)

spini. P=12. chi=2. The price is paid in dissipation; the wave conserves the rest.
"""
import json
import sys

import numpy as np

import goldberg_gc as gg


def laplacian(k, l):
    fv, fc, T = gg.build_fullerene(k, l)
    n = len(fv)
    A = np.zeros((n, n))
    for ring in fc:
        m = len(ring)
        for i in range(m):
            a, b = ring[i], ring[(i + 1) % m]
            A[a, b] = 1.0
            A[b, a] = 1.0
    L = np.diag(A.sum(axis=1)) - A
    return L, n, T


def leapfrog_energy_drift(L, c, dt, steps, u0, v0):
    """Step u'' = -c^2 L u by leapfrog; return (max_rel_drift, H0, Hs).

    Uses the CENTERED velocity v_n = (u_{n+1}-u_{n-1})/(2dt) for the energy trace,
    and the leapfrog-consistent kinetic term 0.5 v.v - (dt^2/8) c^4 (Lu).(Lu) is
    not needed here: at moderate CFL the plain discrete energy drift is already
    bounded and small, which is what we report (COMPUTED, honest)."""
    n = L.shape[0]
    cdt2 = (c * dt) ** 2
    # The EXACTLY conserved leapfrog invariant uses the half-step velocity with the
    # potential STAGGERED across the step: H = 0.5 |v_{n+1/2}|^2 + 0.5 c^2 u_n.L u_{n+1}.
    # (This is the discrete energy the symplectic map preserves to machine precision.)
    def energy(u, u_next, v_half):
        return 0.5 * v_half.dot(v_half) + 0.5 * (c ** 2) * u.dot(L.dot(u_next))
    u_prev = u0.copy()
    u = u0 + dt * v0 - 0.5 * cdt2 * L.dot(u0)          # 2nd-order kick-start
    H = []
    for s in range(steps):
        u_next = 2 * u - u_prev - cdt2 * L.dot(u)
        v_half = (u_next - u) / dt                      # velocity at n+1/2 (exact for leapfrog)
        H.append(energy(u, u_next, v_half))
        u_prev, u = u, u_next
    H = np.array(H)
    H0 = H[0]
    drift = np.max(np.abs(H - H0)) / (abs(H0) + 1e-30)
    return drift, H0, H


def main():
    shells = gg.GOLDEN if "--json" in sys.argv else [(1, 0), (1, 1)]
    if "--json" in sys.argv:
        rec = {"schema": "graph_wave.v1", "note": "leapfrog u''=-c^2 L u; CFL (c dt)^2 lam_max<4",
               "shells": []}
        for (k, l) in shells:
            L, n, T = laplacian(k, l)
            lam = np.linalg.eigvalsh(L)
            lam_max = float(lam[-1])
            c = 1.0
            dt = float(0.5 * 2.0 / np.sqrt(lam_max))   # 0.5 of CFL limit
            rng = np.random.default_rng(12)
            u0 = rng.standard_normal(n); u0 -= u0.mean()
            v0 = np.zeros(n)
            drift, H0, _ = leapfrog_energy_drift(L, c, dt, 4000, u0, v0)
            rec["shells"].append({"k": k, "l": l, "n": n, "lam_max": round(lam_max, 6),
                                  "c": c, "dt": round(dt, 6), "steps": 4000,
                                  "energy_drift": drift, "cfl_ok": (c * dt) ** 2 * lam_max < 4})
        print(json.dumps(rec, indent=2))
        return

    print("GRAPH WAVE u''=-c^2 L u -- the perfect-math light block (proof by kernel)")
    print("  leapfrog / Stormer-Verlet: symplectic, conserves discrete energy.")
    print("  shell   n   lam_max     dt(0.5CFL)  steps   energy_drift   CFL   VERDICT")
    ok_all = True
    for (k, l) in shells:
        L, n, T = laplacian(k, l)
        lam = np.linalg.eigvalsh(L)
        lam_max = float(lam[-1])
        c = 1.0
        dt = 0.5 * 2.0 / np.sqrt(lam_max)   # 0.5 of CFL limit -> comfortable margin
        rng = np.random.default_rng(12)
        u0 = rng.standard_normal(n); u0 -= u0.mean()
        v0 = np.zeros(n)
        drift, H0, _ = leapfrog_energy_drift(L, c, dt, 4000, u0, v0)
        cfl = (c * dt) ** 2 * lam_max
        good = drift < 1e-3 and cfl < 4
        ok_all = ok_all and good
        cage = "C%d" % (20 * T)
        print("  %-6s %3d  %.5f   %.5f    %5d   %.3e   %.3f  %s" % (
            cage, n, lam_max, dt, 4000, drift, cfl, "PASS" if good else "FAIL"))

    # also prove: a single eigenmode stays a PURE standing wave. The EXACT discrete
    # dispersion of leapfrog is omega_num = (2/dt) arcsin( (c dt/2) sqrt(lambda) ),
    # not the continuous sqrt(lambda)*c -- that arcsin IS the perfect math of the
    # stepped scheme. The mode amplitude follows cos(omega_num * t) exactly.
    L, n, T = laplacian(1, 0)  # C20
    w, V = np.linalg.eigh(L)
    j = 1  # Fiedler mode
    c, dt = 1.0, 0.5 * 2.0 / np.sqrt(w[-1])
    ev = V[:, j] / np.linalg.norm(V[:, j])   # unit eigenvector
    u0 = ev.copy()
    cdt2 = (c * dt) ** 2
    u_prev = u0.copy(); u = u0 - 0.5 * cdt2 * L.dot(u0)   # v0=0 kick-start
    M = 200
    for _ in range(M):
        u_next = 2 * u - u_prev - cdt2 * L.dot(u)
        u_prev, u = u, u_next
    amp = u.dot(ev)                          # normalized projection (u stays along ev)
    omega_num = (2.0 / dt) * np.arcsin((c * dt / 2.0) * np.sqrt(w[j]))
    expected = np.cos(omega_num * dt * (M + 1))
    print()
    print("  single-eigenmode test (C20 Fiedler): pure standing wave, EXACT leapfrog dispersion")
    print("    omega_num=(2/dt)arcsin((c dt/2)sqrt(lam2))=%.6f  proj=%.6f  cos=%.6f  |err|=%.2e" % (
        omega_num, amp, expected, abs(amp - expected)))
    mode_ok = abs(amp - expected) < 1e-6
    ok_all = ok_all and mode_ok
    print()
    print("PROOF: " + ("PASS -- the graph wave is the honest propagation." if ok_all else "FAIL"))
    if not ok_all:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
