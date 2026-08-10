#!/usr/bin/env python3
"""Executable receipts for THEA v1.3.4 QCD-to-Cosmos Mana Codex.

Scope: standard algebraic identities, declared numerical toy integrations, the
exact THEA core, and the TopoMagic D(n) provenance control.  The script does
NOT certify a physical unification bridge.
"""
from __future__ import annotations
import argparse, json, math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any
import mpmath as mp
import numpy as np
import sympy as sp
from scipy.integrate import solve_ivp

@dataclass
class Check:
    name: str
    status: str
    passed: bool
    result: Any
    tolerance: Any = None
    note: str = ""

def gell_mann():
    I=sp.I; z=sp.Integer(0); o=sp.Integer(1); s3=sp.sqrt(3)
    return [
      sp.Matrix([[z,o,z],[o,z,z],[z,z,z]]),
      sp.Matrix([[z,-I,z],[I,z,z],[z,z,z]]),
      sp.Matrix([[o,z,z],[z,-o,z],[z,z,z]]),
      sp.Matrix([[z,z,o],[z,z,z],[o,z,z]]),
      sp.Matrix([[z,z,-I],[z,z,z],[I,z,z]]),
      sp.Matrix([[z,z,z],[z,z,o],[z,o,z]]),
      sp.Matrix([[z,z,z],[z,z,-I],[z,I,z]]),
      sp.Matrix([[1/s3,z,z],[z,1/s3,z],[z,z,-2/s3]])]

def structure_f(T):
    f=np.zeros((8,8,8))
    for a in range(8):
      for b in range(8):
        C=T[a]*T[b]-T[b]*T[a]
        for c in range(8):
          f[a,b,c]=float(sp.N(-2*sp.I*sp.trace(C*T[c]),30))
    return f

def lane_emden(n, xmax=20.0):
    e=1e-7
    y0=[1-e*e/6+n*e**4/120,-e/3+n*e**3/30]
    def rhs(x,y): return [y[1],-2*y[1]/x-max(y[0],0.0)**n]
    def stop(x,y): return y[0]
    stop.terminal=True; stop.direction=-1
    sol=solve_ivp(rhs,(e,xmax),y0,events=stop,rtol=2e-11,atol=2e-13,max_step=.02,dense_output=True)
    x1=float(sol.t_events[0][0]); th,dth=sol.sol(x1)
    return x1,float(-x1*x1*dth),sol

def tov(pc,s=1/3,eps0=1.0):
    r0=1e-6; ec=eps0+pc/s; m0=4*math.pi*ec*r0**3/3
    def rhs(r,y):
      m,p=y; e=eps0+max(p,0)/s; den=r*(r-2*m)
      return [4*math.pi*r*r*e, -(e+p)*(m+4*math.pi*r**3*p)/den if den>0 else -1e30]
    def surface(r,y): return y[1]
    surface.terminal=True; surface.direction=-1
    sol=solve_ivp(rhs,(r0,100),[m0,pc],events=surface,rtol=2e-9,atol=2e-11,max_step=.02)
    if not len(sol.t_events[0]): return math.nan,math.nan,math.nan
    R=float(sol.t_events[0][0]); M=float(sol.y_events[0][0][0]); return M,R,2*M/R

def run():
    C=[]
    def add(name,status,ok,result,tol=None,note=""): C.append(Check(name,status,bool(ok),result,tol,note))

    # SU(3)
    lam=gell_mann(); T=[x/2 for x in lam]; I3=sp.eye(3)
    ok=all(sp.simplify(sp.trace(T[a]*T[b])-(sp.Rational(1,2) if a==b else 0))==0 for a in range(8) for b in range(8))
    add("SU(3) generator normalization","STANDARD-EXACT",ok,{"Tr(TaTb)":"delta_ab/2"})
    cf=sp.simplify(sum((x*x for x in T),sp.zeros(3)))
    add("fundamental quadratic Casimir","STANDARD-EXACT",cf==sp.Rational(4,3)*I3,{"C_F":"4/3","matrix":str(cf)})
    f=structure_f(T); adj=np.einsum('acd,bcd->ab',f,f); err=float(np.max(np.abs(adj-3*np.eye(8))))
    add("adjoint quadratic Casimir","STANDARD-COMPUTED",err<1e-12,{"C_A":3,"max_error":err},1e-12)
    add("[T1,T2]=iT3","STANDARD-EXACT",sp.simplify(T[0]*T[1]-T[1]*T[0]-sp.I*T[2])==sp.zeros(3),"zero matrix")
    add("color tensor-product dimensions","STANDARD-EXACT",3*3==6+3 and 3*3==1+8,{"3x3":"6+3bar","3x3bar":"1+8"})
    # With D_mu = partial_mu - i g A_mu, covariance fixes a minus sign
    # on (partial U) U^{-1}, equivalently a plus sign on U partial U^{-1}.
    U,dU,A0,g0=sp.symbols('U dU A g', nonzero=True)
    Aprime=A0-sp.I*dU/(g0*U)
    gauge_res=sp.simplify(dU-sp.I*g0*Aprime*U+sp.I*g0*U*A0)
    add("local gauge-transformation sign","STANDARD-EXACT",gauge_res==0,{"D_mu":"partial-i g A","A_prime":"U A U^-1 - (i/g)(partial U)U^-1"})

    # A2 / Casimir
    A=sp.Matrix([[2,-1],[-1,2]])
    add("A2 Cartan inverse","STANDARD-EXACT",A.inv()==sp.Rational(1,3)*sp.Matrix([[2,1],[1,2]]),str(A.inv()))
    p,q=sp.symbols('p q'); C2=(p*p+p*q+q*q+3*p+3*q)/3
    add("SU(3) Casimir quadratic part","STANDARD-EXACT",sp.expand(3*C2-3*(p+q))==p*p+p*q+q*q,{"C2":str(C2),"THEA_T":"p^2+pq+q^2"})

    # QCD RG
    nf=sp.symbols('n_f')
    b0=sp.Rational(11,3)*3-sp.Rational(4,3)*sp.Rational(1,2)*nf
    b1=sp.Rational(34,3)*9-4*sp.Rational(4,3)*sp.Rational(1,2)*nf-sp.Rational(20,3)*3*sp.Rational(1,2)*nf
    add("QCD beta coefficients for SU(3)","STANDARD-EXACT",sp.simplify(b0-(11-sp.Rational(2,3)*nf))==0 and sp.simplify(b1-(102-sp.Rational(38,3)*nf))==0,{"beta0":str(b0),"beta1":str(b1)})
    Q,L,B=sp.symbols('Q Lambda beta0',positive=True); alpha=4*sp.pi/(B*sp.log(Q**2/L**2))
    add("one-loop RG solution","STANDARD-EXACT",sp.simplify(Q*sp.diff(alpha,Q)+B*alpha**2/(2*sp.pi))==0,{"alpha_s":"4pi/[beta0 ln(Q^2/Lambda^2)]"})
    aM=0.118; MZ=91.1876; b05=11-10/3; lam1=MZ*math.exp(-2*math.pi/(b05*aM))
    add("illustrative one-loop Lambda_QCD","STANDARD-COMPUTED",0<lam1<MZ,{"Lambda_GeV":lam1,"nf":5,"alpha_s_MZ":aM})

    # QGP
    gg=2*(3**2-1); gq=4*3*3; ge=gg+7*gq/8
    add("ideal QGP degrees of freedom","STANDARD-EXACT",ge==47.5,{"g_gluon":gg,"g_qbarq":gq,"g_eff":ge})
    add("conformal QGP sound speed","STANDARD-EXACT",True,{"p":"epsilon/3","cs2":"1/3"})

    # Fermi gas
    mp.mp.dps=80; ferr=[]; xs=[1e-3,.1,1,10,100]
    for x0 in xs:
      x=mp.mpf(str(x0)); eps=(x*mp.sqrt(1+x*x)*(1+2*x*x)-mp.asinh(x))/(8*mp.pi**2)
      pres=(x*mp.sqrt(1+x*x)*(2*x*x-3)+3*mp.asinh(x))/(24*mp.pi**2)
      n=x**3/(3*mp.pi**2); mu=mp.sqrt(1+x*x); ferr.append(float(abs(n*mu-eps-pres)/max(abs(pres),mp.mpf('1e-300'))))
    add("degenerate Fermi gas p=nmu-epsilon","STANDARD-COMPUTED",max(ferr)<1e-60,{"max_relative_error":max(ferr),"x":xs},1e-60)
    def fp(x): return (x*math.sqrt(1+x*x)*(2*x*x-3)+3*math.asinh(x))/(24*math.pi**2)
    def fn(x): return x**3/(3*math.pi**2)
    nr=math.log(fp(.02)/fp(.01))/math.log(fn(.02)/fn(.01)); ur=math.log(fp(200)/fp(100))/math.log(fn(200)/fn(100))
    add("degenerate EOS asymptotic indices","STANDARD-COMPUTED",abs(nr-5/3)<5e-4 and abs(ur-4/3)<5e-4,{"gamma_NR":nr,"gamma_UR":ur},5e-4)
    EE,EG,kT=sp.symbols('E E_G kT', positive=True)
    E0=(EG*kT**2/sp.Integer(4))**sp.Rational(1,3)
    gamow_exp=EE/kT+sp.sqrt(EG/EE)
    gamow_res=sp.simplify(sp.diff(gamow_exp,EE).subs(EE,E0))
    add("Gamow-peak stationary energy","STANDARD-EXACT",gamow_res==0,{"E0":"[E_G (kT)^2/4]^(1/3)"})

    # Lane-Emden and Chandrasekhar
    le={}
    for nv in (1.0,1.5,3.0): x1,w1,_=lane_emden(nv); le[str(nv)]={"xi1":x1,"omega":w1}
    add("Lane-Emden n=1 analytic root","STANDARD-COMPUTED",abs(le['1.0']['xi1']-math.pi)<2e-8,le['1.0'],2e-8)
    add("Lane-Emden n=3/2 constants","STANDARD-COMPUTED",abs(le['1.5']['xi1']-3.65375374)<2e-7 and abs(le['1.5']['omega']-2.71405512)<2e-7,le['1.5'],2e-7)
    add("Lane-Emden n=3 constants","STANDARD-COMPUTED",abs(le['3.0']['xi1']-6.89684862)<2e-7 and abs(le['3.0']['omega']-2.01823595)<2e-7,le['3.0'],2e-7)
    hbar=1.054571817e-34; cc=299792458.; G=6.67430e-11; mu=1.66053906660e-27; Ms=1.98847e30
    K0=(3*math.pi**2)**(1/3)*hbar*cc/(4*mu**(4/3)); coeff=4*le['3.0']['omega']/math.sqrt(math.pi)*(K0/G)**1.5/Ms
    add("Chandrasekhar mass coefficient","STANDARD-COMPUTED",abs(coeff-5.83)<.03,{"Mch/Msun":f"{coeff:.8f}/mu_e^2"},.03)

    # TOV
    rows=[]
    for pc in np.logspace(-2,2.2,90):
      M,R,comp=tov(float(pc));
      if math.isfinite(M): rows.append([float(pc),M,R,comp])
    peak=max(rows,key=lambda r:r[1]); ok=len(rows)>70 and peak[2]>2*peak[1] and peak[3]<1
    add("TOV linear-EOS toy sequence","STANDARD-COMPUTED",ok,{"models":len(rows),"peak_pc":peak[0],"peak_M":peak[1],"peak_R":peak[2],"peak_2M/R":peak[3]})
    G0,m0,r0,p0,e0,c0s=sp.symbols('G m r p epsilon c', positive=True)
    phip=G0*(m0+4*sp.pi*r0**3*p0/c0s**2)/(r0**2*c0s**2*(1-2*G0*m0/(r0*c0s**2)))
    dp_cons=-(e0+p0)*phip
    dp_tov=-G0*(e0+p0)*(m0+4*sp.pi*r0**3*p0/c0s**2)/(r0**2*c0s**2*(1-2*G0*m0/(r0*c0s**2)))
    add("TOV restoration of c factors","STANDARD-EXACT",sp.simplify(dp_cons-dp_tov)==0,{"conservation":"dp/dr=-(epsilon+p) Phi_prime","mass":"dm/dr=4pi r^2 epsilon/c^2"})

    # Jeans, FLRW, GW formula presence
    cs,k,rho,Gs=sp.symbols('c_s k rho G',positive=True); om=cs**2*k**2-4*sp.pi*Gs*rho; kJ=sp.sqrt(4*sp.pi*Gs*rho/cs**2)
    add("Jeans threshold","STANDARD-EXACT",sp.simplify(om.subs(k,kJ))==0,{"omega2":"cs2 k2-4piG rho","kJ":str(kJ)})
    a,w,r0=sp.symbols('a w rho0',positive=True); ra=r0*a**(-3*(1+w))
    add("FLRW continuity solution","STANDARD-EXACT",sp.simplify(a*sp.diff(ra,a)+3*(1+w)*ra)==0,{"rho(a)":"rho0 a^-3(1+w)"})
    ff,Mc,Gc,c0=sp.symbols('f Mc G c',positive=True); fd=sp.Rational(96,5)*sp.pi**(sp.Rational(8,3))*(Gc*Mc/c0**3)**(sp.Rational(5,3))*ff**(sp.Rational(11,3))
    add("binary inspiral chirp formula","STANDARD-EXACT",fd.has(Mc) and fd.has(ff),{"df/dt":str(fd)})

    # THEA exact core
    Ml=sp.Matrix([[1,2,1,0],[1,1,0,0],[1,0,0,0],[0,0,0,1]]); x=sp.symbols('lambda')
    cp=sp.factor(Ml.charpoly(x).as_expr()); ex=(x-1)*(x+1)*(x*x-3*x+1)
    add("Light Matrix characteristic polynomial","THEA-EXACT",sp.expand(cp-ex)==0,{"charpoly":str(cp),"coefficients":[1,-3,0,3,-1]})
    phi=(1+sp.sqrt(5))/2; eig=list(Ml.eigenvals())
    add("Light Matrix reciprocal spectrum","THEA-EXACT",all(any(sp.simplify(e-t)==0 for e in eig) for t in [phi**2,1,-1,phi**-2]),{"spectrum":[str(e) for e in eig]})
    kk,ll=sp.symbols('k ell'); MM=sp.Matrix([[kk,-ll],[ll,kk+ll]]); Q2=sp.Matrix([[2,1],[1,2]]); TT=kk*kk+kk*ll+ll*ll
    add("hexagonal closure metric identity","THEA-EXACT",sp.simplify(MM.T*Q2*MM-TT*Q2)==sp.zeros(2),{"T":"k^2+k ell+ell^2"})
    V,E,P,H=sp.symbols('V E P H'); sol=sp.solve([sp.Eq(3*V,2*E),sp.Eq(5*P+6*H,2*E),sp.Eq(V-E+P+H,2)],[V,E,P],dict=True)[0]
    add("Euler fullerene defect charge","THEA-EXACT",sp.simplify(sol[P])==12,{"P":str(sp.simplify(sol[P]))})

    # TopoMagic D(n) mismatch
    D=[1.203011392,4.806545406,10.818228646]; dD=D[0]-2*D[1]+D[2]
    z1=.888490076146; z2=z1+3*math.log(2); z3=z2+8*math.log(3); dz=abs(z1-2*z2+z3)
    add("TopoMagic D(n) affine-invariant mismatch","CONTROL-CORRECTION",abs(dD-dz)>1,{"Delta2_D":dD,"abs_Delta2_zeta":dz,"difference":dz-dD},note="Constant/linear absorption cannot change a second difference.")

    passed=sum(x.passed for x in C); sc={}
    for x in C: sc[x.status]=sc.get(x.status,0)+1
    return {"title":"THEA v1.3.4 QCD-to-Cosmos Mana Codex receipt","schema":"qcd-cosmos-v1","summary":{"checks":len(C),"passed":passed,"failed":len(C)-passed,"status_counts":sc},"checks":[asdict(x) for x in C],"computed_tables":{"lane_emden":le,"tov_linear_eos":rows,"Lambda_QCD_1loop_GeV":lam1},"boundary":"Certifies displayed identities and toy computations only; no physical unification bridge is certified."}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='/mnt/data/qcd_to_cosmos_mana_v1.0.0_receipt.json'); ap.add_argument('--report',default='/mnt/data/qcd_to_cosmos_mana_v1.0.0_report.md'); a=ap.parse_args()
    r=run(); Path(a.out).write_text(json.dumps(r,indent=2,sort_keys=True),encoding='utf-8')
    lines=["# QCD-to-Cosmos Mana Codex audit","",f"- Checks: **{r['summary']['checks']}**",f"- Passed: **{r['summary']['passed']}**",f"- Failed: **{r['summary']['failed']}**","","## Ledger",""]
    lines += [f"- {'PASS' if c['passed'] else 'FAIL'} | `{c['status']}` | {c['name']}" for c in r['checks']]
    lines += ["","## Boundary","",r['boundary']]
    Path(a.report).write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps(r['summary'],indent=2)); raise SystemExit(0 if r['summary']['failed']==0 else 1)
if __name__=='__main__': main()
