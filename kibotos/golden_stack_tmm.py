#!/usr/bin/env python3
"""KIBOTOS-100 photon-management stack -- transfer-matrix kernel.
Race: periodic vs phi^2-chirped vs Fibonacci quarter-wave multilayers as the
sub-bandgap back reflector (the component that made 40% TPV possible).
Also: EXACT check of the Kohmoto-Kadanoff-Tang golden trace map + invariant.
Materials idealized dispersionless [DESIGN CHOICE]: A=Si n=3.42, B=SiO2 n=1.45.
Band [DESIGN CHOICE, golden]: [L, L*phi^2] with L=1.80 um  (span = phi^2)."""
import math, cmath
import numpy as np

PHI=(1+5**0.5)/2
nA,nB=3.42,1.45
n0,ns=1.0,1.45
Lmin=1.80; Lmax=Lmin*PHI*PHI          # 1.80 .. 4.712 um, span phi^2
lam0=Lmin*PHI                          # geometric center 2.913 um

def layer_M(n,d,lam):
    dlt=2*math.pi*n*d/lam
    return np.array([[math.cos(dlt), 1j*math.sin(dlt)/n],
                     [1j*n*math.sin(dlt), math.cos(dlt)]],complex)

def stack_R(layers,lam):
    M=np.eye(2,dtype=complex)
    for n,d in layers: M=M@layer_M(n,d,lam)
    B=M[0,0]+M[0,1]*ns; C=M[1,0]+M[1,1]*ns
    r=(n0*B-C)/(n0*B+C)
    return abs(r)**2

def qw(n,lam): return lam/(4*n)

# ---- the three contenders, equal layer count N=34 ----
def periodic():
    return [(nA,qw(nA,lam0)),(nB,qw(nB,lam0))]*17
def chirp_phi2():
    lays=[]
    for j in range(17):
        lj=Lmin*PHI**(2*j/16)          # centers sweep exactly [L, L*phi^2]
        lays+=[(nA,qw(nA,lj)),(nB,qw(nB,lj))]
    return lays
def fib_word(N):
    a,b="A","AB"
    while len(b)<N: a,b=b,b+a
    return b[:N]
def fibonacci():
    w=fib_word(34)
    return [ (nA,qw(nA,lam0)) if c=="A" else (nB,qw(nB,lam0)) for c in w ]

def planck_w(lam_um,T=1300.0):
    lam=lam_um*1e-6; h,c,kB=6.626e-34,2.998e8,1.381e-23
    return (1/lam**5)/(math.exp(h*c/(lam*kB*T))-1)

lams=np.linspace(Lmin,Lmax,1200)
res={}
for name,build in (("periodic",periodic),("phi2-chirp",chirp_phi2),("fibonacci",fibonacci)):
    lays=build()
    R=np.array([stack_R(lays,l) for l in lams])
    w=np.array([planck_w(l) for l in lams]); w/=w.sum()
    res[name]=(R, R.mean(), (R*w).sum(), R.min())
print("STACK RACE -- band [1.800, 4.712] um (span = phi^2), N=34 layers each")
print(f"{'stack':>11} {'mean R':>8} {'1300K-weighted R':>17} {'min R in band':>14}")
for k,(R,m,wm,mn) in res.items():
    print(f"{k:>11} {m:8.4f} {wm:17.4f} {mn:14.4f}")
best=max(res,key=lambda k:res[k][2])
print(f"VERDICT [COMPUTED, honest]: weighted-average winner = {best}")

# ---- Fibonacci fractal spectrum (for the scroll) ----
w9=fib_word(55)
fib55=[(nA,qw(nA,lam0)) if c=="A" else (nB,qw(nB,lam0)) for c in w9]
nus=np.linspace(0.02,1.98,1600)                # nu/nu0 in quarter-wave units
Tfib=np.array([1-stack_R(fib55,lam0/nu) for nu in nus])

# ---- KKT trace map + invariant [EXACT recursion, checked numerically] ----
def TA(lam): return layer_M(nA,qw(nA,lam0),lam)
def TB(lam): return layer_M(nB,qw(nB,lam0),lam)
def kkt(lam,steps=13):
    M=[TB(lam),TA(lam)]
    x=[0.5*np.trace(M[0]).real,0.5*np.trace(M[1]).real]
    for n in range(1,steps):
        M.append(M[n-1]@M[n]); x.append(0.5*np.trace(M[-1]).real)
    rec=[abs(x[n+1]-(2*x[n]*x[n-1]-x[n-2])) for n in range(2,len(x)-1)]
    inv=[x[n+1]**2+x[n]**2+x[n-1]**2-2*x[n+1]*x[n]*x[n-1]-1 for n in range(1,len(x)-1)]
    return max(rec), max(inv)-min(inv), inv[0]
lam_pass=lam0/0.62
r_res,i_drift,i_val=kkt(lam_pass)
print(f"\nKKT TRACE MAP at a passband frequency (nu/nu0=0.62):")
print(f"  recursion residual max  = {r_res:.3e}   [EXACT identity, machine-checked]")
print(f"  invariant I value       = {i_val:.12f}")
print(f"  invariant drift over 12 generations = {i_drift:.3e}")
r2,d2,v2=kkt(lam0/1.00,steps=9)
print(f"at band center (nu/nu0=1.00): residual {r2:.3e}, I={v2:.9f}, drift {d2:.3e}")

# ---- SVGs for the scroll ----
def polyline(xs,ys,X0,X1,Y0,Y1,W,H,pad=42):
    pts=[]
    for x,y in zip(xs,ys):
        px=pad+(x-X0)/(X1-X0)*(W-2*pad); py=H-pad-(y-Y0)/(Y1-Y0)*(H-2*pad)
        pts.append(f"{px:.1f},{py:.1f}")
    return " ".join(pts)
W,H=740,300
cols={"periodic":"#ffd700","phi2-chirp":"#00d4ff","fibonacci":"#ff69b4"}
svg=[f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="background:#050510">']
svg.append(f'<rect x="42" y="18" width="{W-84}" height="{H-60}" fill="none" stroke="#241a30"/>')
for gl in (0.25,0.5,0.75):
    y=H-42-gl*(H-60+18-42+24)
for name in ("periodic","phi2-chirp","fibonacci"):
    R=res[name][0]
    svg.append(f'<polyline fill="none" stroke="{cols[name]}" stroke-width="1.6" opacity="0.9" points="{polyline(lams,R,Lmin,Lmax,0,1,W,H)}"/>')
for lx,lab in ((Lmin,"L"),(lam0,"L*phi"),(Lmax,"L*phi^2")):
    px=42+(lx-Lmin)/(Lmax-Lmin)*(W-84)
    svg.append(f'<line x1="{px:.0f}" y1="18" x2="{px:.0f}" y2="{H-42}" stroke="#cc44ff" stroke-dasharray="3 5" opacity="0.5"/>')
    svg.append(f'<text x="{px:.0f}" y="{H-26}" fill="#cc44ff" font-size="11" text-anchor="middle" font-family="monospace">{lab}</text>')
svg.append(f'<text x="42" y="14" fill="#e0e0e0" font-size="12" font-family="monospace">Reflectance R(lambda), band span phi^2 -- gold=periodic  cyan=phi2-chirp  pink=fibonacci</text>')
svg.append(f'<text x="14" y="{H-40}" fill="#6a6a82" font-size="10" font-family="monospace">0</text><text x="14" y="26" fill="#6a6a82" font-size="10" font-family="monospace">1</text>')
svg.append('</svg>')
open('spec_reflect.svg','w').write("".join(svg))

svg2=[f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="background:#050510">']
svg2.append(f'<rect x="42" y="18" width="{W-84}" height="{H-60}" fill="none" stroke="#241a30"/>')
svg2.append(f'<polyline fill="none" stroke="#cc44ff" stroke-width="1.2" points="{polyline(nus,Tfib,0,2,0,1,W,H)}"/>')
svg2.append(f'<text x="42" y="14" fill="#e0e0e0" font-size="12" font-family="monospace">Fibonacci 55-layer transmission T(nu/nu0): the self-similar golden gap forest</text>')
svg2.append(f'<text x="{W/2:.0f}" y="{H-26}" fill="#6a6a82" font-size="11" text-anchor="middle" font-family="monospace">nu/nu0 (quarter-wave units), 0..2</text>')
svg2.append('</svg>')
open('fib_trans.svg','w').write("".join(svg2))
print("\nSVGs written: spec_reflect.svg, fib_trans.svg")
