"""
TRADEOFF RECEIPT v0.1 -- proof by kernel before render.

The brief: the sub-Planck render is not computable on this chip. So lock the
numeric fence at what Chromium honestly gives (float64), and pick bands where
the SAME generator has real anchors: a QCD band and a galactic band.

The claim under test: T = k^2 + k*l + l^2 is not just the Goldberg triangulation
number. It is the norm form of the A2 root lattice = the SU(3) weight lattice,
and it sits inside the SU(3) quadratic Casimir. Same integers, two readings.
"""
import numpy as np
from fractions import Fraction as Fr

PHI = (1 + 5 ** 0.5) / 2
LN_PHI2 = np.log(PHI ** 2)

print("=" * 76)
print("B1  EXACT -- T is the A2 (= SU(3) weight lattice) norm form")
print("=" * 76)
# A2 simple roots in the plane, |a|^2 = 2, angle 120 deg
a1 = np.array([1.0, 0.0]) * np.sqrt(2)
a2 = np.array([-0.5, np.sqrt(3) / 2]) * np.sqrt(2)
G = np.array([[a1 @ a1, a1 @ a2], [a2 @ a1, a2 @ a2]])
print(f"   A2 Cartan/Gram matrix =\n   {G.round(6).tolist()}   (2,-1;-1,2 up to scale)")
worst = 0.0
for p in range(-6, 7):
    for q in range(-6, 7):
        v = p * a1 - q * a2                     # sign chosen to give +pq
        worst = max(worst, abs(0.5 * (v @ v) - (p * p + p * q + q * q)))
print(f"   max | |p a1 - q a2|^2 / 2  -  (p^2+pq+q^2) |  over 169 points : {worst:.2e}")
print(f"   -> the Goldberg T and the A2 norm are THE SAME FORM : {worst < 1e-12}")

print()
print("=" * 76)
print("B2  EXACT -- SU(3) irrep dimension and Casimir contain T")
print("=" * 76)
def dim(p, q): return Fr((p + 1) * (q + 1) * (p + q + 2), 2)
def cas(p, q): return Fr(p * p + q * q + p * q + 3 * p + 3 * q, 3)
known = {(1, 0): 3, (0, 1): 3, (2, 0): 6, (1, 1): 8, (3, 0): 10, (2, 1): 15, (2, 2): 27, (4, 0): 15}
ok = all(dim(*k) == v for k, v in known.items())
print("   dim(p,q) = (p+1)(q+1)(p+q+2)/2 against the standard table :", ok)
print("  ", {f"({p},{q})": int(dim(p, q)) for p, q in known})
print(f"   C2(fundamental (1,0)) = {cas(1,0)}   expected 4/3 : {cas(1,0) == Fr(4,3)}")
print(f"   C2(adjoint     (1,1)) = {cas(1,1)}   expected 3   : {cas(1,1) == 3}")
idok = all(cas(p, q) == Fr(p*p + p*q + q*q, 3) + Fr(3*(p+q), 3) for p in range(8) for q in range(8))
print(f"   C2(p,q) == ( T(p,q) + 3(p+q) ) / 3  for all 64 pairs : {idok}")

print()
print("=" * 76)
print("B3  EXACT -- the light-matrix golden ladder read as SU(3) irreps")
print("=" * 76)
k, l = 1, 0
print(f"   {'n':>2} {'(k,l)':>8} {'T':>6} {'SU(3) dim':>10} {'C2':>10}   cage")
CAGE = {1: 'C20', 3: 'C60', 7: 'C140', 19: 'C380', 49: 'C980', 129: 'C2580', 337: 'C6740'}
lad = []
for n in range(7):
    T = k*k + k*l + l*l
    lad.append((n, k, l, T, int(dim(k, l)), cas(k, l)))
    print(f"   {n:>2} {f'({k},{l})':>8} {T:>6} {int(dim(k,l)):>10} {str(cas(k,l)):>10}   {CAGE.get(T,'-')}")
    k, l = k + l, k
print("   -> 3, 8, 15, 42, 120, ... is a golden ladder of SU(3) irreps")
print("   -> STATUS: the lattice identity is EXACT. Reading it as physics is a")
print("      DESIGN MAPPING -- one quadratic form used twice, not a theorem of QCD.")

print()
print("=" * 76)
print("B4  COMPUTED -- the phi^2 scale ladder, Planck to quasar")
print("=" * 76)
ANCH = [("Planck length", 1.616255e-35), ("proton radius", 0.8414e-15),
        ("QCD scale hbar c / 200MeV", 0.9862e-15), ("Bohr radius", 5.29177e-11),
        ("human", 1.7), ("Earth radius", 6.371e6), ("Sun radius", 6.957e8),
        ("r_s of the Sun", 2.953e3), ("r_s of a 1e10 Msun quasar", 2.953e13),
        ("quasar ISCO (3 r_s)", 8.859e13), ("observable universe", 4.4e26)]
base = ANCH[0][1]
print(f"   rung n counted from the Planck length, spacing phi^2 = {PHI**2:.6f}")
print(f"   {'anchor':>28} {'metres':>12} {'rung n':>9}")
for nm, L in ANCH:
    print(f"   {nm:>28} {L:>12.3e} {np.log(L/base)/LN_PHI2:>9.1f}")
span = np.log(ANCH[-1][1] / base) / LN_PHI2
qcd = np.log(ANCH[1][1] / base) / LN_PHI2
qso = np.log(ANCH[8][1] / base) / LN_PHI2
print(f"\n   Planck -> proton          : {qcd:6.1f} rungs")
print(f"   proton -> quasar r_s      : {qso-qcd:6.1f} rungs")
print(f"   Planck -> observable univ : {span:6.1f} rungs   <- the whole ladder")

print()
print("=" * 76)
print("B5  COMPUTED -- the Chromium fence: how much of that ladder fits in float64")
print("=" * 76)
eps = np.finfo(float).eps
win = np.log(1 / eps) / LN_PHI2
print(f"   float64 eps                    = {eps:.6e}")
print(f"   one mantissa window            = {win:.1f} phi^2 rungs")
print(f"   ladder needed                  = {span:.1f} rungs")
print(f"   windows required               = {span/win:.2f}  -> {int(np.ceil(span/win))} float64 charts")
print(f"   -> a single float64 chart CANNOT hold Planck..quasar. It holds {int(win)} rungs.")
print(f"   -> the honest move is to carry log(T) and re-anchor per band, not to")
print(f"      pretend one linear chart reaches the bottom. (K5: fence where nature put it.)")

print()
print("=" * 76)
print("B6  EXACT -- the complex-dimension ladder of this scale string")
print("=" * 76)
print(f"   rho = phi^-2 = {PHI**-2:.9f},  ln(1/rho) = {LN_PHI2:.9f}")
print(f"   poles at s = D + 2*pi*i*k / ln(1/rho);  imaginary spacing = {2*np.pi/LN_PHI2:.6f}")
print(f"   -> log-periodic oscillation period in ln(scale) = {LN_PHI2:.6f}")
print(f"   -> that is the ONE number the render must resolve, and it is O(1).")
print(f"      Resolving it does NOT require sub-Planck compute. That is the trade.")

print()
print("=" * 76)
print("B7  COMPUTED -- the galactic anchor, from first principles")
print("=" * 76)
G_, c_, mp, sT, Msun = 6.67430e-11, 2.99792458e8, 1.67262192e-27, 6.6524587e-29, 1.98892e30
for M in (1e8, 1e9, 1e10):
    Mk = M * Msun
    rs = 2 * G_ * Mk / c_**2
    Led = 4 * np.pi * G_ * Mk * mp * c_ / sT
    print(f"   M = {M:.0e} Msun :  r_s = {rs:.3e} m   L_Edd = {Led:.3e} W = {Led*1e7:.3e} erg/s"
          f"   rung {np.log(rs/base)/LN_PHI2:.1f}")
print(f"   check: L_Edd / (M/Msun) = {Led/M*1e7:.3e} erg/s   (textbook 1.26e38) ")
