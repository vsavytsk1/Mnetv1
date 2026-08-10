#!/usr/bin/env python3
# -*- coding: ascii -*-
"""
THE CROWD v0.1 -- a coincidence engine, run with its own guillotine
=================================================================================
The temptation: scan the tower's dimensionless numbers against the constants of
physics, find the matches, announce them. This script DOES that -- and then runs
the null model that decides whether the matches mean anything: 2000 fake towers,
drawn log-uniform over the real tower's range, pushed through the SAME transforms
against the SAME constants. If the real tower's hit count sits inside the fake
distribution, the crowd has identified nobody.

Rules of the house:
  - DIMENSIONLESS ONLY. A pure number cannot equal a kilogram (Thea Part VII).
  - Constants pinned from CODATA/PDG/Planck values as known at write time and
    tagged; SOL should re-pin before quoting any individual value. The NULL does
    not care about the third decimal of any constant.
  - Deterministic seed (Curse 38). Price printed before the loop (Curse 35).
  - ASCII source only (Curse 2).
P=12. chi=2. The price is always paid.
"""
import math, random

PHI = (1.0 + 5.0**0.5) / 2.0

# ---------------- THE TOWER'S DIMENSIONLESS NUMBERS --------------------------
AR = 0.8875                                   # measured area ratio, 9 digits stable
D_INF = 2.0*math.log(7.0)/(math.log(7.0)-math.log(AR))   # closed form, computed here
TOWER = [
  ("lambda2(C60)",            0.2434017461399),
  ("phi^-2",                  1.0/PHI**2),
  ("theta_phi (rad)",         math.atan(math.sqrt(15.0)-2.0*math.sqrt(3.0))),
  ("HELENA gate (DESIGN)",    0.700),
  ("golden steps per bit",    1.0/(2.0*math.log2(PHI))),
  ("T*lambda2 leapfrog",      0.724799130),
  ("2pi/(5 sqrt3)",           2.0*math.pi/(5.0*math.sqrt(3.0))),
  ("area ratio aR",           AR),
  ("2 log2 phi",              2.0*math.log2(PHI)),
  ("phi",                     PHI),
  ("D measured",              1.8835),
  ("D_inf closed form",       D_INF),
  ("phi^2",                   PHI**2),
]

# ---------------- ~90 DIMENSIONLESS CONSTANTS (tagged) -----------------------
# tags: qed, ew, qcd, mass, ckm, pmns, cosmo, grav, mag, hadron, math
C = [
 ("alpha^-1",137.035999177,"qed"), ("alpha",1.0/137.035999177,"qed"),
 ("a_e (g-2)/2",1.15965218059e-3,"qed"), ("g_e/2",1.00115965218059,"qed"),
 ("a_mu",1.16592059e-3,"qed"),
 ("sin2thW MSbar",0.23122,"ew"), ("alpha_s(MZ)",0.1179,"qcd"),
 ("mW/mZ",80.3692/91.1880,"ew"), ("sin2thW on-shell",1.0-(80.3692/91.1880)**2,"ew"),
 ("mZ/mH",91.1880/125.25,"ew"), ("mH/mt",125.25/172.57,"ew"),
 ("mt/mZ",172.57/91.1880,"ew"), ("mt/mH",172.57/125.25,"ew"),
 ("mW/mH",80.3692/125.25,"ew"), ("mH/mW",125.25/80.3692,"ew"),
 ("mp/me",1836.15267343,"mass"), ("mn/mp",1.00137841931,"mass"),
 ("mmu/me",206.7682830,"mass"), ("mtau/mmu",1776.86/105.6584,"mass"),
 ("mtau/me",3477.23,"mass"), ("mp/mmu",1836.15267343/206.7682830,"mass"),
 ("g_p",5.5856946893,"mag"), ("|g_n|",3.82608545,"mag"),
 ("|mu_p/mu_n|",1.45989805,"mag"), ("mu_p/mu_B",1.52103220e-3,"mag"),
 ("mpi+/me",139.5704/0.5109989,"hadron"), ("mpi0/mpi+",134.9768/139.5704,"hadron"),
 ("mK/mpi",493.677/139.5704,"hadron"), ("mp/mpi+",938.2721/139.5704,"hadron"),
 ("|Vus|",0.22501,"ckm"), ("|Vcb|",0.04183,"ckm"), ("|Vub|",0.00382,"ckm"),
 ("Wolfenstein A",0.826,"ckm"), ("Jarlskog J",3.08e-5,"ckm"),
 ("sin 2beta",0.699,"ckm"), ("delta_CP (rad)",1.147,"ckm"),
 ("sin2 th12 nu",0.307,"pmns"), ("sin2 th23 nu",0.546,"pmns"),
 ("sin2 th13 nu",0.02203,"pmns"), ("dm21^2/dm31^2",7.41e-5/2.511e-3,"pmns"),
 ("Omega_Lambda",0.6847,"cosmo"), ("Omega_m",0.3153,"cosmo"),
 ("Omega_b h^2",0.02237,"cosmo"), ("Omega_c h^2",0.1200,"cosmo"),
 ("h (Hubble)",0.6736,"cosmo"), ("n_s",0.9649,"cosmo"),
 ("sigma_8",0.8111,"cosmo"), ("S_8",0.832,"cosmo"),
 ("tau_reio",0.0544,"cosmo"), ("eta_baryon x1e10",6.12,"cosmo"),
 ("z_eq/1000",3.402,"cosmo"), ("z_rec/1000",1.0899,"cosmo"),
 ("N_eff",2.99,"cosmo"), ("Y_p helium",0.2454,"cosmo"),
 ("|w_DE|",1.03,"cosmo"), ("|q_0|",0.53,"cosmo"),
 ("alpha_G x1e39",5.906,"grav"), ("mPl/mp x1e-19",1.3011,"grav"),
 ("mPl/mH x1e-16",9.75,"grav"),
 ("pi",math.pi,"math"), ("e",math.e,"math"), ("sqrt2",2.0**0.5,"math"),
 ("sqrt3",3.0**0.5,"math"), ("sqrt5",5.0**0.5,"math"), ("ln2",math.log(2.0),"math"),
 ("gamma_EM",0.5772156649,"math"), ("zeta(3)",1.2020569032,"math"),
 ("pi^2/6",math.pi**2/6.0,"math"), ("e^gamma",1.7810724180,"math"),
 ("Feigenbaum delta",4.6692016091,"math"), ("Feigenbaum alpha",2.5029078751,"math"),
 ("Catalan",0.9159655942,"math"), ("Khinchin",2.6854520010,"math"),
 ("Glaisher",1.2824271291,"math"), ("ln10",math.log(10.0),"math"),
 ("pi/e",math.pi/math.e,"math"), ("e/pi",math.e/math.pi,"math"),
 ("Gauss constant",0.8346268417,"math"), ("plastic number",1.3247179572,"math"),
 ("silver ratio",1.0+2.0**0.5,"math"), ("Conway lambda",1.3035772690,"math"),
 ("Levy constant",3.2758229187,"math"), ("Mills constant",1.3063778838,"math"),
 ("Omega (Lambert)",0.5671432904,"math"), ("Cahen constant",0.6434105463,"math"),
 ("Golomb-Dickman",0.6243299885,"math"), ("Embree-Trefethen",0.70258,"math"),
 ("Laplace limit",0.6627434193,"math"), ("Ramanujan-Soldner",1.4513692349,"math"),
]

# The tower already contains phi; keep the constants list phi-free so no trial
# matches itself. (Checked below by the self-match guard anyway.)

# ---------------- THE TRANSFORMS (the numerologist's toolkit) ----------------
LN2 = math.log(2.0)
XF = [
 ("t",       lambda t: t),        ("1/t",     lambda t: 1.0/t),
 ("t^2",     lambda t: t*t),      ("sqrt t",  lambda t: math.sqrt(t)),
 ("2t",      lambda t: 2.0*t),    ("t/2",     lambda t: t/2.0),
 ("pi t",    lambda t: math.pi*t),("t/pi",    lambda t: t/math.pi),
 ("phi t",   lambda t: PHI*t),    ("t/phi",   lambda t: t/PHI),
 ("t ln2",   lambda t: t*LN2),    ("t/ln2",   lambda t: t/LN2),
]

TIERS = [1e-2, 3e-3, 1e-3, 3e-4, 1e-4]

def scan(vals):
    """vals: list of (name, value). Returns list of hits and per-tier counts."""
    hits = []
    for nm, tv in vals:
        for xn, fx in XF:
            try: q = fx(tv)
            except Exception: continue
            if not (q > 0.0 and math.isfinite(q)): continue
            for cn, cv, tag in C:
                d = abs(q - cv)/abs(cv)
                if d < 1e-12:  continue          # self-match guard
                if d < TIERS[0]:
                    hits.append((d, nm, xn, q, cn, cv, tag))
    counts = [sum(1 for h in hits if h[0] < th) for th in TIERS]
    return hits, counts

def main():
    global C
    random.seed(20260809)                        # Curse 38: reproducible
    trials = len(TOWER)*len(XF)
    mc_n = 2000
    price = trials*len(C) + mc_n*trials*len(C)
    print("="*79)
    print("  THE CROWD v0.1 -- coincidence engine + null, one run")
    print("="*79)
    print("  tower numbers %d   transforms %d   constants %d" % (len(TOWER), len(XF), len(C)))
    print("  price: %d comparisons (real) + %d (null MC x%d) = %s total"
          % (trials*len(C), mc_n*trials*len(C), mc_n,
             "{:,}".format(price).replace(",", " ")))
    print("")
    print("  D_inf closed form check: 2 ln7 / (ln7 - ln %.4f) = %.9f" % (AR, D_INF))
    print("")

    hits, counts = scan(TOWER)
    hits.sort(key=lambda h: h[0])

    print("  A. THE TRAP -- the twenty juiciest matches, exactly as a believer")
    print("     would print them")
    print("     %-10s %-24s %-8s %-12s %-22s %s"
          % ("delta", "tower number", "via", "value", "constant", "sector"))
    for d, nm, xn, q, cn, cv, tag in hits[:20]:
        print("     %-10s %-24s %-8s %-12.7g %-22s %s"
              % ("%.2e" % d, nm, xn, q, cn, tag))
    print("")
    print("  B. HIT COUNTS BY TIER (real tower)")
    for th, c0 in zip(TIERS, counts):
        print("     within %-7s : %d" % ("%.0e" % th, c0))
    print("")

    # ---------------- the null: fake towers, same machinery ------------------
    lo, hi = math.log(0.2), math.log(3.0)        # the real tower's span
    null_counts = [[] for _ in TIERS]
    for _ in range(mc_n):
        fake = [("f%d" % i, math.exp(random.uniform(lo, hi)))
                for i in range(len(TOWER))]
        _, cc = scan(fake)
        for j in range(len(TIERS)):
            null_counts[j].append(cc[j])

    print("  C. THE NULL -- %d fake towers, log-uniform over [0.2, 3.0]," % mc_n)
    print("     same transforms, same constants, same tiers")
    print("     %-10s %-12s %-16s %-12s %s"
          % ("tier", "real hits", "null mean+-sd", "percentile", "verdict"))
    for j, th in enumerate(TIERS):
        arr = null_counts[j]
        m = sum(arr)/float(mc_n)
        sd = (sum((x-m)**2 for x in arr)/float(mc_n))**0.5
        pct = 100.0*sum(1 for x in arr if x < counts[j])/float(mc_n)
        excess = (counts[j]-m)/sd if sd > 0 else float("nan")
        verdict = ("INSIDE the noise" if abs(excess) < 2.0 else
                   ("%.1f sigma ABOVE noise -- investigate" % excess if excess > 0
                    else "%.1f sigma BELOW noise" % excess))
        print("     %-10s %-12d %-16s %-12s %s"
              % ("%.0e" % th, counts[j], "%.1f +- %.1f" % (m, sd),
                 "%.0f%%" % pct, verdict))
    print("")

    # ---------------- the autopsy: physics-only pass -------------------------
    # The 3e-3 excess rows are dominated by the "math" tag. Hypothesis: the tower
    # is BUILT from {phi, pi, sqrt3, ln2, small integers} and the transform kit is
    # BUILT from {phi, pi, ln2, 2} -- so tower x transform preferentially lands on
    # math constants assembled from the same alphabet. Self-correlation through a
    # shared alphabet, not physics. The kill test: drop the math tag entirely and
    # rerun BOTH the scan and the null. If the excess was alphabet, it dies.
    C_ALL = C
    C = [c for c in C_ALL if c[2] != "math"]
    hits2, counts2 = scan(TOWER)
    null2 = [[] for _ in TIERS]
    for _ in range(mc_n):
        fake = [("f%d" % i, math.exp(random.uniform(lo, hi)))
                for i in range(len(TOWER))]
        _, cc = scan(fake)
        for j in range(len(TIERS)):
            null2[j].append(cc[j])
    print("  C2. THE AUTOPSY -- same engine, PHYSICS-ONLY constants (%d of %d)"
          % (len(C), len(C_ALL)))
    print("     %-10s %-12s %-16s %-12s %s"
          % ("tier", "real hits", "null mean+-sd", "percentile", "verdict"))
    for j, th in enumerate(TIERS):
        arr = null2[j]
        m = sum(arr)/float(mc_n)
        sd = (sum((x-m)**2 for x in arr)/float(mc_n))**0.5
        pct = 100.0*sum(1 for x in arr if x < counts2[j])/float(mc_n)
        excess = (counts2[j]-m)/sd if sd > 0 else float("nan")
        verdict = ("INSIDE the noise" if abs(excess) < 2.0 else
                   ("%.1f sigma ABOVE noise" % excess if excess > 0
                    else "%.1f sigma BELOW noise" % excess))
        print("     %-10s %-12d %-16s %-12s %s"
              % ("%.0e" % th, counts2[j], "%.1f +- %.1f" % (m, sd),
                 "%.0f%%" % pct, verdict))
    print("")

    # ---------------- the second autopsy: dedup the tower --------------------
    # The tower list is internally CLUSTERED: {0.700, 0.7202, 0.7248, 0.7255}
    # is one neighbourhood wearing four badges (and 0.7202 is literally
    # 1/1.3885, which is also in the list); {1.8835, 1.8844} is one number
    # measured twice; {phi^-2, phi, phi^2} is a single orbit of the transform
    # group. The log-uniform null has no such redundancy, so at coarse tiers
    # the real tower outscores it for FREE. Kill test: collapse each cluster
    # to one representative and rerun, physics-only, with a matched null.
    DEDUP = [
      ("lambda2(C60)",       0.2434017461399),
      ("theta_phi (rad)",    math.atan(math.sqrt(15.0)-2.0*math.sqrt(3.0))),
      ("2pi/(5 sqrt3)",      2.0*math.pi/(5.0*math.sqrt(3.0))),
      ("area ratio aR",      AR),
      ("2 log2 phi",         2.0*math.log2(PHI)),
      ("phi",                PHI),
      ("D_inf closed form",  D_INF),
    ]
    hits3, counts3 = scan(DEDUP)
    null3 = [[] for _ in TIERS]
    for _ in range(mc_n):
        fake = [("f%d" % i, math.exp(random.uniform(lo, hi)))
                for i in range(len(DEDUP))]
        _, cc = scan(fake)
        for j in range(len(TIERS)):
            null3[j].append(cc[j])
    print("  C3. THE SECOND AUTOPSY -- deduped tower (%d honestly-independent" % len(DEDUP))
    print("      numbers), physics-only constants, matched null")
    print("     %-10s %-12s %-16s %-12s %s"
          % ("tier", "real hits", "null mean+-sd", "percentile", "verdict"))
    for j, th in enumerate(TIERS):
        arr = null3[j]
        m = sum(arr)/float(mc_n)
        sd = (sum((x-m)**2 for x in arr)/float(mc_n))**0.5
        pct = 100.0*sum(1 for x in arr if x < counts3[j])/float(mc_n)
        excess = (counts3[j]-m)/sd if sd > 0 else float("nan")
        verdict = ("INSIDE the noise" if abs(excess) < 2.0 else
                   ("%.1f sigma ABOVE noise" % excess if excess > 0
                    else "%.1f sigma BELOW noise" % excess))
        print("     %-10s %-12d %-16s %-12s %s"
              % ("%.0e" % th, counts3[j], "%.1f +- %.1f" % (m, sd),
                 "%.0f%%" % pct, verdict))
    C = C_ALL
    print("")

    # ---------------- the contrast: what a real derivation looks like --------
    a_e = 1.15965218059e-3
    schwinger = 1.0/(2.0*math.pi*137.035999177)
    print("  D. THE CONTRAST -- one line of QED, zero free choices")
    print("     Schwinger 1948:  a_e = alpha/2pi = %.9e" % schwinger)
    print("     measured      :  a_e            = %.9e" % a_e)
    print("     first-order agreement: %.2e relative -- and with the full series" %
          (abs(schwinger-a_e)/a_e))
    print("     QED lands at ~1e-12. No transform menu. No nearest neighbour.")
    print("     The formula existed BEFORE the measurement it explains.")
    print("")
    print("  P=12. chi=2. A crowd identifies nobody. The price is always paid.")
    print("="*79)

if __name__ == "__main__":
    main()
