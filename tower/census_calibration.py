"""
CENSUS CALIBRATION v0.1
Put the angular-FFT census operator on a standard whose integer is a theorem.

Ground truth:  M_d = {c : orbit of 0 under z -> z^d + c is bounded}
               has EXACTLY (d-1)-fold rotational symmetry.
               d=14 -> certified N=13.   d=15 -> certified N=14.
"""
import numpy as np
from scipy.ndimage import map_coordinates

# ---------- 1. field generator -------------------------------------------
def multibrot_field(d, half=1.35, n=1400, maxit=300, R=3.0):
    """smooth escape time on a square grid centred at the origin"""
    ax = np.linspace(-half, half, n)
    C = ax[None, :] + 1j * ax[:, None]
    Z = np.zeros_like(C)
    nu = np.zeros(C.shape)
    alive = np.ones(C.shape, bool)
    for k in range(maxit):
        Z[alive] = Z[alive] ** d + C[alive]
        esc = alive & (np.abs(Z) > R)
        if esc.any():
            az = np.abs(Z[esc])
            nu[esc] = k + 1 - np.log(np.log(az) / np.log(R)) / np.log(d)
            alive[esc] = False
        if not alive.any():
            break
    nu[alive] = maxit
    return nu, half, ax


def edge(field):
    """gradient magnitude -- the analogue of the mosaic 'edge' channel"""
    gy, gx = np.gradient(field)
    return np.hypot(gx, gy)


# ---------- 2. the census operator ---------------------------------------
def angular_power(field, half, centre, r1, r2, mmax=34, nr=200, nth=2048):
    """band-integrated angular Fourier power P_m about `centre`"""
    n = field.shape[0]
    pix = (n - 1) / (2 * half)                       # pixels per unit
    r = np.linspace(r1, r2, nr)
    th = np.linspace(0, 2 * np.pi, nth, endpoint=False)
    RR, TT = np.meshgrid(r, th, indexing="ij")
    X = centre[0] + RR * np.cos(TT)
    Y = centre[1] + RR * np.sin(TT)
    col = (X + half) * pix
    row = (Y + half) * pix
    F = map_coordinates(field, [row.ravel(), col.ravel()], order=1,
                        mode="constant", cval=0.0).reshape(RR.shape)
    F = F - F.mean(axis=1, keepdims=True)            # kill m=0 per ring
    H = np.fft.rfft(F, axis=1) / nth
    P = (np.abs(H) ** 2).sum(axis=0) * (r[1] - r[0])
    return P[:mmax + 1]


def verdict(P, lo=3, hi=30):
    m = lo + int(np.argmax(P[lo:hi + 1]))
    return m, P


def suppression(P, N):
    """sideband suppression ratio -- the proposed centring criterion"""
    return P[N] / (P[N - 1] + P[N + 1])


# ---------- 3. run -------------------------------------------------------
np.random.seed(0)
print("=" * 78)
print("TEST A  -- operator on the certified standard, true centre")
print("=" * 78)
std = {}
for d, truth in [(14, 13), (15, 14)]:
    nu, half, ax = multibrot_field(d)
    E = edge(nu)
    # decoration band sits just outside the main component
    z0 = (1.0 / d) ** (1.0 / (d - 1))
    r1, r2 = 0.97 * z0, 1.22 * z0
    m, P = verdict(angular_power(E, half, (0.0, 0.0), r1, r2))
    std[d] = (E, half, r1, r2, truth)
    frac = P[truth] / P[3:31].sum()
    print(f"  M_{d}: theorem says N={truth:2d} | census reads m={m:2d} "
          f"| band r=[{r1:.3f},{r2:.3f}] | dominance {frac:5.1%} "
          f"| {'PASS' if m == truth else 'FAIL'}")

print()
print("=" * 78)
print("TEST B  -- can a centre error turn the 13 into a 14?")
print("        eps = |offset| / mean band radius")
print("=" * 78)
E, half, r1, r2, truth = std[14]
rbar = 0.5 * (r1 + r2)
print(f"  {'eps':>6} {'offset':>16} {'argmax':>7} {'P12':>9} {'P13':>9} "
      f"{'P14':>9} {'P13/(P12+P14)':>14}")
flip = None
for eps in [0.0, 0.02, 0.05, 0.08, 0.126, 0.16, 0.20, 0.25, 0.30, 0.40, 0.50]:
    ang = 0.37                                   # arbitrary offset direction
    off = (eps * rbar * np.cos(ang), eps * rbar * np.sin(ang))
    m, P = verdict(angular_power(E, half, off, r1, r2))
    if m != truth and flip is None:
        flip = eps
    print(f"  {eps:6.3f} ({off[0]:+.4f},{off[1]:+.4f}) {m:7d} "
          f"{P[12]:9.2e} {P[13]:9.2e} {P[14]:9.2e} {suppression(P,13):14.2f}")
print(f"\n  first misread at eps = {flip}")

print()
print("=" * 78)
print("TEST C  -- worst case over offset DIRECTION at the mosaic's own eps")
print("        (mosaic centres differ by (+7,-14)px on rbar~124px -> eps=0.126)")
print("=" * 78)
reads = {}
for ang in np.linspace(0, 2 * np.pi, 48, endpoint=False):
    off = (0.126 * rbar * np.cos(ang), 0.126 * rbar * np.sin(ang))
    m, _ = verdict(angular_power(E, half, off, r1, r2))
    reads[m] = reads.get(m, 0) + 1
print(f"  48 offset directions at eps=0.126 -> readings {dict(sorted(reads.items()))}")

print()
print("=" * 78)
print("TEST D  -- does sideband suppression recover the true centre?")
print("=" * 78)
best = max(
    ((suppression(angular_power(E, half, (dx, dy), r1, r2), 13), dx, dy)
     for dx in np.linspace(-0.10, 0.10, 21)
     for dy in np.linspace(-0.10, 0.10, 21)),
)
print(f"  argmax P13/(P12+P14) at offset ({best[1]:+.4f},{best[2]:+.4f}), "
      f"ratio {best[0]:.2f}   [truth is (0,0)]")
print(f"  recovery error = {np.hypot(best[1],best[2])/rbar:.4f} in units of eps")

print()
print("=" * 78)
print("TEST E  -- the OTHER way to manufacture a 14: harmonic doubling")
print("=" * 78)
th = np.linspace(0, 2 * np.pi, 2048, endpoint=False)
for a2 in [0.0, 0.4, 0.8, 1.2, 2.0]:
    sig = np.cos(7 * th) + a2 * np.cos(14 * th)
    Pm = np.abs(np.fft.rfft(sig)) ** 2
    print(f"  7-fold pattern with 2nd-harmonic weight {a2:3.1f} -> census reads "
          f"m={int(np.argmax(Pm[3:31]))+3}")

print()
print("=" * 78)
print("TEST F  -- is N even well defined? scale sweep on a TRUE fractal (d=2)")
print("=" * 78)
nu2, half2, _ = multibrot_field(2, half=1.35, n=1400, maxit=400)
E2 = edge(nu2)
for (a, b) in [(0.30, 0.45), (0.45, 0.60), (0.60, 0.75), (0.75, 0.90),
               (0.90, 1.05), (1.05, 1.20)]:
    m, P = verdict(angular_power(E2, half2, (-0.0, 0.0), a, b))
    frac = P[m] / P[3:31].sum()
    print(f"  Mandelbrot, band r=[{a:.2f},{b:.2f}] -> dominant m={m:2d} "
          f"(dominance {frac:5.1%})")
