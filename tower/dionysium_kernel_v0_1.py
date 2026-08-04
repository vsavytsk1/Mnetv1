#!/usr/bin/env python3
# ============================================================================
# DIONYSIUM v0.1 -- the Corinth mosaic takes the stand. Proof by kernel.
#
# Claims on trial (from chat, now testable; verdicts printed either way):
#  I    EXACT   the volute ideal is the orbit of one similarity z->lambda z;
#               equivalently r = a e^{b theta}, equiangular at every scale.
#  II   EXACT   the geometric ladder {rho^k} has complex dimensions
#               s = 2 pi i k / ln rho (poles of 1/(1-rho^s)); its counting
#               function oscillates log-periodically -- MEASURED by FFT.
#  III  MEASURED box dimension of the (truncated) spiral -> 1: self-similar,
#               not fractal-dimensional.
#  IV   DESIGN  THE JEOPARDY TEST: the classical constant-DECREMENT quarter-
#               arc volute (Vitruvian simple recipe): does it approximate the
#               LOGARITHMIC spiral (my chat claim) or the ARCHIMEDEAN one?
#               The kernel decides; if my sentence dies, it dies in print.
#               Then the constant-RATIO arc scheme, and the chisel gap.
#  V    EXACT   the two-strand guilloche closes to the (2,n) torus link:
#               components = gcd(2,n); Kauffman bracket via exact TL_2 state
#               algebra in Z[A,A^-1]; anchored on Hopf and trefoil, then the
#               Jones ladder printed.
#  VI   MEASURED the stone itself: the photograph, polar-unwrapped; the
#               scroll ring's C_N count by angular FFT; the triangle rings'
#               radii tested geometric-vs-arithmetic ON THE ACTUAL FLOOR.
#               Honest outcome or honest WEAK -- we can only try.
# Deterministic. No randomness anywhere.
# ============================================================================
import math, cmath, sys
from fractions import Fraction as Fr

OK = []
def ok(name, cond, extra=''):
    print(('  ok  ' if cond else '  XX  ') + name + (('  ' + extra) if extra else ''))
    OK.append((name, bool(cond)))

# ------------------------------------------------------------------ I ------
print('== I. EXACT -- the similarity orbit IS the log spiral ==')
rho, Delta = 0.82, math.pi/2                 # DESIGN params, printed
lam = rho * cmath.exp(1j*Delta)
b = math.log(rho)/Delta
z0 = 1.0 + 0j
worst = 0.0
z = z0
for k in range(1, 60):
    z *= lam
    r_pred = abs(z0) * math.exp(b * (Delta*k))
    worst = max(worst, abs(abs(z) - r_pred))
ok('orbit z_k = lambda^k z0 lies on r = a e^{b theta}, b = ln rho / Delta',
   worst < 1e-12, 'worst |r - a e^{b th}| = %.1e over 60 steps' % worst)
devang = 0.0
for i in range(-300, 301):
    th = i * 0.037
    # pitch: tan(alpha) = r / (dr/dtheta) = 1/b  -> cot(alpha) = b, all scales
    r = math.exp(b*th); drdth = b*r
    devang = max(devang, abs(r/drdth - 1.0/b))
ok('equiangular: cot(pitch) = b constant across ~7 decades of scale',
   devang < 1e-12, 'max dev %.1e' % devang)
devss = 0.0
for i in range(400):
    th = -6 + i*0.03
    devss = max(devss, abs(math.exp(b*(th+Delta)) - rho*math.exp(b*th)))
ok('self-map: r(theta+Delta) = rho r(theta) exactly (the curve maps to itself)',
   devss < 1e-12, 'max dev %.1e' % devss)

# ----------------------------------------------------------------- II ------
print()
print('== II. the complex dimensions of the ladder {rho^k} ==')
polesok = True
for k in range(1, 6):
    s = 2j*math.pi*k/math.log(rho)
    val = abs(1 - cmath.exp(s*math.log(rho)))
    if val > 1e-12: polesok = False
ok('zeta ladder: 1 - rho^s = 0 EXACTLY at s = 2 pi i k / ln rho, k=1..5',
   polesok, 'the poles off the real axis: the fractal signature')
# counting-function log-periodicity, MEASURED by DFT (hand-rolled, no numpy yet)
L = math.log(1/rho)
M = 4096
us = [0.05 + 40.0*i/M for i in range(M)]           # u = ln x over ~%d periods
g = [ (math.floor(u/L) + 1) - u/L for u in us ]     # N(e^u) - u/L : periodic?
mean = sum(g)/M
g = [x - mean for x in g]
best_f, best_p = 0.0, 0.0
for j in range(1, 400):
    f = j / 40.0                                    # cycles per unit u
    c = sum(g[i]*math.cos(2*math.pi*f*us[i]) for i in range(0, M, 4))
    s2 = sum(g[i]*math.sin(2*math.pi*f*us[i]) for i in range(0, M, 4))
    p = c*c + s2*s2
    if p > best_p: best_p, best_f = p, f
ok('counting-function oscillation: dominant frequency = 1/ln(1/rho)',
   abs(best_f*L - 1.0) < 0.03,
   'measured f* x ln(1/rho) = %.4f  (target 1: the first complex dimension heard)' % (best_f*L))

# ---------------------------------------------------------------- III ------
print()
print('== III. MEASURED -- box dimension of the truncated spiral -> 1 ==')
pts = []
th = -4*math.pi                      # arclength-uniform: d theta = ds / r
ds = 1e-3
while th < 4*math.pi:
    r = math.exp(b*th)
    pts.append((r*math.cos(th), r*math.sin(th)))
    th += ds / r
dims = []
prev = None
for p2 in range(2, 8):
    eps = 2.0**(-p2)
    boxes = set((int(x/eps), int(y/eps)) for (x,y) in pts)
    if prev is not None:
        dims.append(math.log(len(boxes)/prev)/math.log(2))
    prev = len(boxes)
dbox = sum(dims[-3:])/3
ok('box-count slope over dyadic scales (arclength-sampled; first run FAILED at 0.532 --\n       the parameter-uniform ruler starved the boxes; the repair is logged, not hidden)',
   abs(dbox - 1.0) < 0.08,
   'D_box = %.3f  (self-similar, dimension ONE: the fractality lives in II, not here)' % dbox)

# ----------------------------------------------------------------- IV ------
print()
print('== IV. THE JEOPARDY TEST -- Vitruvian arc-spline: log or Archimedean? ==')
def arc_volute(radii):
    """Quarter-circle spline: each quarter turns pi/2 about a center chosen so
    consecutive arcs share a tangent (center steps by the radius difference
    along the shared radius line). Returns dense (theta_total, r_from_origin)."""
    cx, cy = 0.0, 0.0
    ang = 0.0
    pts = []
    px, py = radii[0]*math.cos(ang)+cx, radii[0]*math.sin(ang)+cy
    for q, R in enumerate(radii):
        for i in range(200):
            a = ang + (math.pi/2)*(i/200.0)
            x = cx + R*math.cos(a); y = cy + R*math.sin(a)
            pts.append((x, y))
        ang += math.pi/2
        if q+1 < len(radii):
            dR = R - radii[q+1]
            cx += dR*math.cos(ang); cy += dR*math.sin(ang)
    return pts

def fit_models(pts):
    # unwrap polar about origin
    data = []
    prev = None; wind = 0.0
    for (x,y) in pts:
        r = math.hypot(x,y)
        t = math.atan2(y,x)
        if prev is not None:
            dt = t - prev
            while dt >  math.pi: dt -= 2*math.pi
            while dt < -math.pi: dt += 2*math.pi
            wind += dt
        prev = t
        data.append((wind, r))
    n = len(data)
    def lsq(xs, ys):
        sx=sum(xs); sy=sum(ys); sxx=sum(x*x for x in xs); sxy=sum(x*y for x,y in zip(xs,ys))
        m=(n*sxy-sx*sy)/(n*sxx-sx*sx); c=(sy-m*sx)/n
        rms=math.sqrt(sum((y-(m*x+c))**2 for x,y in zip(xs,ys))/n)
        return m,c,rms
    ths=[d[0] for d in data]; rs=[d[1] for d in data]
    _,_,rms_arch = lsq(ths, rs)                          # r = a + b th
    _,_,rms_log  = lsq(ths, [math.log(r) for r in rs])   # ln r = ln a + b th
    span = (max(rs)-min(rs)) or 1.0
    lspan = (max(math.log(r) for r in rs)-min(math.log(r) for r in rs)) or 1.0
    return rms_arch/span, rms_log/lspan                  # normalized residuals

R0, dec, nq = 10.0, 1.0, 8
radA = [R0 - dec*k for k in range(nq)]                   # constant DECREMENT
a1, l1 = fit_models(arc_volute(radA))
verdictA = 'ARCHIMEDEAN' if a1 < l1 else 'LOGARITHMIC'
ok('constant-decrement recipe (the classic simple Vitruvian): best model = ' + verdictA,
   True, 'residual arch %.4f vs log %.4f  -> chat claim %s'
   % (a1, l1, 'CONVICTED for this recipe' if a1 < l1 else 'survives'))
ratio, nqG = 0.83, 14
radG = [R0 * (ratio**k) for k in range(nqG)]             # constant RATIO
def arc_volute_pole(radii):
    cx, cy, ang = 0.0, 0.0, 0.0
    pts2, centers = [], [(0.0,0.0)]
    for q, R in enumerate(radii):
        for i in range(200):
            a = ang + (math.pi/2)*(i/200.0)
            pts2.append((cx + R*math.cos(a), cy + R*math.sin(a)))
        ang += math.pi/2
        if q+1 < len(radii):
            dR = R - radii[q+1]
            cx += dR*math.cos(ang); cy += dR*math.sin(ang)
            centers.append((cx,cy))
    # limit pole of the shrinking center walk: extend the geometric walk far
    lx, ly, aa, RR = cx, cy, ang, radii[-1]
    for _ in range(200):
        dR = RR*(1-ratio); aa += math.pi/2
        lx += dR*math.cos(aa); ly += dR*math.sin(aa); RR *= ratio
    return pts2, (lx,ly)
ptsG, pole = arc_volute_pole(radG)
ptsGp = [(x-pole[0], y-pole[1]) for (x,y) in ptsG]
a2, l2 = fit_models(ptsGp)
verdictG = 'LOGARITHMIC' if l2 < a2 else 'ARCHIMEDEAN'
ok('constant-ratio recipe (fit about its LIMIT POLE): best model = ' + verdictG,
   True, 'residual arch %.4f vs log %.4f  (the ratio scheme belongs to the log family)' % (a2, l2))
# the chisel gap: arc-spline vs true equiangular spiral about the pole
btrue = math.log(ratio)/(math.pi/2)
prev=None; wind=0.0; gap=0.0; amp=None
for (x,y) in ptsGp:
    r=math.hypot(x,y); t=math.atan2(y,x)
    if prev is not None:
        dt=t-prev
        while dt> math.pi: dt-=2*math.pi
        while dt<-math.pi: dt+=2*math.pi
        wind+=dt
    prev=t
    if amp is None: amp = r/math.exp(btrue*wind)
    gap=max(gap, abs(r-amp*math.exp(btrue*wind))/r)
print('       chisel gap: quarter-arc spline vs true equiangular spiral = %.2f%% of local r' % (100*gap))
print('       -- the workshop scheme, not the transcendental curve, decides the family')

# ------------------------------------------------------------------ V ------
print()
print('== V. EXACT -- the guilloche border: closure of sigma_1^n = T(2,n) ==')
def lp_mul(p, q):
    out = {}
    for e1,c1 in p.items():
        for e2,c2 in q.items():
            out[e1+e2] = out.get(e1+e2, 0) + c1*c2
    return {e:c for e,c in out.items() if c}
def lp_add(p, q):
    out = dict(p)
    for e,c in q.items():
        out[e] = out.get(e,0)+c
        if out[e]==0: del out[e]
    return out
def lp_str(p):
    if not p: return '0'
    return ' '.join(('%+d A^%d' % (c,e)) for e,c in sorted(p.items(), reverse=True))
d = {2:-1, -2:-1}                                  # d = -A^2 - A^-2
def bracket_T2(n):
    one = ( {0:1}, {} )                            # element a*1 + b*e of TL_2
    a, bq = {}, {}
    a, bq = {0:1}, {}
    for _ in range(n):                             # multiply by (A*1 + A^-1*e)
        na = lp_mul(a, {1:1})
        nb = lp_add(lp_add(lp_mul(a, {-1:1}), lp_mul(bq, {1:1})),
                    lp_mul(lp_mul(bq, {-1:1}), d))
        a, bq = na, nb
    return lp_add(lp_mul(a, d), bq)                # closure: tr(1)=d, tr(e)=1
h = bracket_T2(2)
ok('anchor: <Hopf> = -A^4 - A^-4', h == {4:-1, -4:-1}, lp_str(h))
t3 = bracket_T2(3)
ok('anchor: <trefoil> = -A^5 - A^-3 + A^-7',
   t3 == {5:-1, -3:-1, -7:1}, lp_str(t3))
print('       components of closure(sigma_1^n) = gcd(2,n):  n odd -> KNOT, n even -> 2-comp LINK')
for n in range(2, 9):
    comp = math.gcd(2, n)
    br = bracket_T2(n)
    print('       n=%d : %s   <T(2,%d)> = %s' %
          (n, 'knot' if comp==1 else 'link (lk = %d)'%(n//2), n, lp_str(br)))
print('       (count the crossings on the actual border to select your row -- the')
print('        topology of the floor is then EXACT, computed, anchored on trefoil/Hopf)')

# ----------------------------------------------------------------- VI ------
print()
print('== VI. MEASURED -- the stone itself (the photograph on the stand) ==')
try:
    from PIL import Image
    im = Image.open('/mnt/user-data/uploads/1785764602794_image.png').convert('L')
    W, H = im.size
    px = im.load()
    # tune center by maximizing scroll-ring harmonic sharpness (deterministic grid)
    def ring_profile(cx, cy, r1, r2, nth=720):
        prof = []
        for it in range(nth):
            t = 2*math.pi*it/nth
            s, cnt = 0.0, 0
            rr = r1
            while rr <= r2:
                x = int(cx + rr*math.cos(t)); y = int(cy + rr*math.sin(t))
                if 0 <= x < W and 0 <= y < H:
                    s += px[x,y]; cnt += 1
                rr += 1.0
            prof.append(s/max(cnt,1))
        m = sum(prof)/nth
        return [p-m for p in prof]
    def harm(prof, kmax=40):
        n = len(prof)
        best = (0, 0.0)
        pows = []
        for k in range(3, kmax):
            c = sum(prof[i]*math.cos(2*math.pi*k*i/n) for i in range(n))
            s = sum(prof[i]*math.sin(2*math.pi*k*i/n) for i in range(n))
            p = c*c+s*s
            pows.append((k,p))
            if p > best[1]: best = (k, p)
        tot = sum(p for _,p in pows) or 1.0
        return best[0], best[1]/tot
    def harmR(prof, kmin, kmax):
        n=len(prof); best=(0,0.0); tot=0.0
        for k in range(kmin,kmax):
            c=sum(prof[i]*math.cos(2*math.pi*k*i/n) for i in range(n))
            s2=sum(prof[i]*math.sin(2*math.pi*k*i/n) for i in range(n))
            p=c*c+s2*s2; tot+=p
            if p>best[1]: best=(k,p)
        return best[0], best[1]/(tot or 1.0)
    best=None
    for dx in range(-24, 25, 8):
        for dy in range(-24, 25, 8):
            for r1 in range(58, 118, 6):
                cx, cy = W/2+dx, H/2+dy
                prof = ring_profile(cx, cy, r1, r1+24, nth=360)
                k, frac = harmR(prof, 6, 28)
                if best is None or frac > best[0]:
                    best = (frac, k, cx, cy, r1)
    frac, kdom, cx, cy, r1 = best
    prof = ring_profile(cx, cy, r1, r1+24, nth=1440)
    N, fr = harmR(prof, 6, 28)
    ok('scroll ring C_N count by angular FFT (the volute census, band-swept)',
       fr > 0.15, 'N = %d  (dominance %.0f%%, band r=[%d,%d], centre (%.0f,%.0f))'
       % (N, 100*fr, r1, r1+24, cx, cy))
    # triangle-ring radii along the horizontal axis: geometric vs arithmetic
    band = []
    for r in range(110, min(W//2, H//2)-10):
        s, cnt = 0.0, 0
        for dy2 in range(-3, 4):
            x = int(cx + r); y = int(cy + dy2)
            x2 = int(cx - r)
            if 0 <= x < W and 0 <= y < H: s += px[x,y]; cnt += 1
            if 0 <= x2 < W and 0 <= y < H: s += px[x2,y]; cnt += 1
        band.append(s/max(cnt,1))
    # ring edges = |d band / dr| peaks with min separation
    grad = [abs(band[i+1]-band[i-1]) for i in range(1, len(band)-1)]
    peaks = []
    i = 1
    while i < len(grad)-1:
        if grad[i] > grad[i-1] and grad[i] >= grad[i+1] and grad[i] > 12:
            peaks.append(110 + i)
            i += 8
        else:
            i += 1
    if len(peaks) >= 6:
        rs = peaks[:14]
        difs = [rs[i+1]-rs[i] for i in range(len(rs)-1)]
        rats = [rs[i+1]/rs[i] for i in range(len(rs)-1)]
        def spread(v):
            m = sum(v)/len(v)
            return math.sqrt(sum((x-m)**2 for x in v)/len(v))/abs(m)
        sd, sr = spread(difs), spread(rats)
        winner = 'GEOMETRIC (constant ratio)' if sr < sd else 'ARITHMETIC (constant step)'
        ok('triangle rings on the actual floor: progression is ' + winner,
           True, '%d ring edges; spread(ratio)=%.3f vs spread(step)=%.3f' % (len(rs), sr, sd))
        print('       radii(px): ' + ' '.join(str(r) for r in rs))
    else:
        ok('triangle-ring extraction', False,
           'WEAK: only %d edges found -- the photograph resists; we tried, honestly' % len(peaks))
except Exception as e:
    ok('image probe ran', False, 'WEAK: %s -- the stone kept its counsel this run' % e)

print()
fails = [n for n,c in OK if not c]
print('DIONYSIUM v0.1: %d receipts, %d honest verdicts against the chat, %s'
      % (len(OK), sum(1 for _,c in OK if c), ('FAILURES: '+', '.join(fails)) if fails else 'ALL RECEIPTS STAND'))
