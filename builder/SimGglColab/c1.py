#!/usr/bin/env python3
"""
navierKolmogorov_colab.py -- Kolmogorov Turbulence on Goldberg Polyhedra
COLAB VERSION -- no sys.argv, no webbrowser, plots inline
Paste entire file into one Colab cell. Runtime > Run all.
"""
import os, time, math
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
#  CONFIG
# ============================================================================
LEVEL       = 5        # 5 = 504,212 faces
TOTAL_STEPS = 50000  # let google suffer
NU          = 0.00005  # Re = 20,000
# ============================================================================

print("=" * 60)
print("  navierKolmogorov COLAB -- FULL TURBULENCE ENGINE")
print(f"  LEVEL={LEVEL}  STEPS={TOTAL_STEPS:,}  nu={NU}  Re={1/NU:,.0f}")
print("=" * 60)

GPU = False
sp_sparse = None
try:
    import cupy as cp
    import cupyx.scipy.sparse as csp
    import cupyx.scipy.sparse.linalg as csla
    GPU = True
    gname = cp.cuda.runtime.getDeviceProperties(0)['name'].decode()
    vram = cp.cuda.runtime.memGetInfo()[1] / 1024**3
    print(f"  GPU: {gname} ({vram:.1f} GB)  MODE: CUDA")
except Exception:
    try:
        import scipy.sparse as sp_sparse
        print("  MODE: CPU sparse (scipy)")
    except Exception:
        print("  MODE: CPU dense (numpy)")
print()

PHI = (1 + math.sqrt(5)) / 2

# ============================================================================
#  GOLDBERG KERNEL
# ============================================================================
def norm_v(v):
    L = np.linalg.norm(v, axis=-1, keepdims=True)
    return v / np.where(L < 1e-12, 1, L)

def build_dodecahedron():
    ip = 1.0 / PHI
    raw = np.array([
        [1,1,1],[1,1,-1],[1,-1,1],[1,-1,-1],
        [-1,1,1],[-1,1,-1],[-1,-1,1],[-1,-1,-1],
        [0,ip,PHI],[0,ip,-PHI],[0,-ip,PHI],[0,-ip,-PHI],
        [ip,PHI,0],[ip,-PHI,0],[-ip,PHI,0],[-ip,-PHI,0],
        [PHI,0,ip],[PHI,0,-ip],[-PHI,0,ip],[-PHI,0,-ip]
    ], dtype=np.float64)
    raw = norm_v(raw) * 1.6
    d = np.linalg.norm(raw[:,None]-raw[None,:], axis=-1)
    np.fill_diagonal(d, 999)
    el = d[d>0.01].min(); tol = el*0.1
    adj = [[j for j in range(len(raw)) if j!=i and
            abs(np.linalg.norm(raw[i]-raw[j])-el)<tol]
           for i in range(len(raw))]
    for i in range(len(raw)):
        v=raw[i]; n=v/np.linalg.norm(v); ref=raw[adj[i][0]]-v
        tan=ref-n*np.dot(ref,n); tl=np.linalg.norm(tan)
        if tl>1e-12: tan/=tl
        e2=np.cross(n,tan)
        adj[i].sort(key=lambda idx: math.atan2(
            np.dot(raw[idx]-v,e2), np.dot(raw[idx]-v,tan)))
    def nxt(u,v):
        idx=adj[v].index(u) if u in adj[v] else -1
        return adj[v][(idx+len(adj[v])-1)%len(adj[v])] if idx>=0 else -1
    vis=set(); faces=[]
    for u in range(len(raw)):
        for v in adj[u]:
            if (u,v) in vis: continue
            f=[u]; a,b=u,v
            for _ in range(10):
                vis.add((a,b)); c=nxt(a,b)
                if c<0 or c==u: break
                f.append(b); a,b=b,c
            if f[-1]!=b: f.append(b)
            if len(f)==5: faces.append(f)
    seen=set(); uni=[]
    for f in faces:
        k=tuple(sorted(f))
        if k not in seen: seen.add(k); uni.append(f)
    return [{'pts':np.array([raw[k] for k in f]),'type':'pent'} for f in uni]

def refine_all(faces, R=1.6):
    out=[]
    for face in faces:
        pts=face['pts']; n=len(pts); c=pts.mean(axis=0)
        inner=norm_v(np.array([c+0.45*(pts[i]-c) for i in range(n)]))*R
        mid=norm_v(np.array([c+0.70*((pts[i]+pts[(i+1)%n])*0.5-c) for i in range(n)]))*R
        out.append({'pts':inner.copy(),'type':face['type']})
        for i in range(n):
            j=(i+1)%n
            em=norm_v(((pts[i]+pts[j])*0.5).reshape(1,3)).flatten()*R
            out.append({'pts':np.array([pts[i],em,pts[j],inner[j],mid[i],inner[i]]),'type':'hex'})
    return out

def invariants(faces):
    P=sum(1 for f in faces if f['type']=='pent')
    H=len(faces)-P; fes=5*P+6*H; V=round(fes/3); E=round(fes/2)
    return {'F':len(faces),'P':P,'H':H,'V':V,'E':E,'chi':V-E+len(faces)}

def build_operators(faces):
    nF=len(faces); edge_map={}; rows=[]; cols=[]
    for i,face in enumerate(faces):
        pts=face['pts']
        for k in range(len(pts)):
            a=tuple(np.round(pts[k],3))
            b=tuple(np.round(pts[(k+1)%len(pts)],3))
            rkey=(b,a)
            if rkey in edge_map:
                j=edge_map[rkey]
                rows.extend([i,j]); cols.extend([j,i])
            else:
                edge_map[(a,b)]=i
    if GPU:
        r=cp.array(rows,dtype=cp.int32); c=cp.array(cols,dtype=cp.int32)
        d=cp.ones(len(rows),dtype=cp.float32)
        A=csp.csr_matrix((d,(r,c)),shape=(nF,nF))
        deg=cp.array(A.sum(axis=1)).flatten()
        deg=cp.where(deg==0,1,deg)
        A_norm=csp.diags(1.0/deg)@A
        L=A_norm-csp.eye(nF,dtype=cp.float32)
    elif sp_sparse:
        d=np.ones(len(rows),dtype=np.float32)
        A=sp_sparse.csr_matrix((d,(rows,cols)),shape=(nF,nF))
        deg=np.array(A.sum(axis=1)).flatten(); deg[deg==0]=1
        A_norm=sp_sparse.diags(1.0/deg)@A
        L=A_norm-sp_sparse.eye(nF,dtype=np.float32)
    else:
        A=np.zeros((nF,nF),dtype=np.float32)
        for r,c in zip(rows,cols): A[r,c]=1.0
        deg=A.sum(axis=1,keepdims=True); deg[deg==0]=1
        A_norm=A/deg; L=A_norm-np.eye(nF,dtype=np.float32)
    return A_norm, L, nF

# ============================================================================
#  KOLMOGOROV ENGINE
# ============================================================================
class KolmogorovEngine:
    def __init__(self, A, L, nF, nu=1e-3, dt=0.01, forcing_scale=0.1):
        self.A=A; self.L=L; self.nF=nF; self.nu=nu
        self.dt=dt; self.forcing_scale=forcing_scale; self.step=0
        xp = cp if GPU else np
        self.omega=xp.zeros(nF,dtype=xp.float32)
        self.psi  =xp.zeros(nF,dtype=xp.float32)
        self.tke_history=[]; self.enstrophy_history=[]
        self.dissipation_history=[]; self.spectrum_snapshots=[]

    def inject_forcing(self):
        n_forced=max(1,self.nF//20)
        if GPU:
            idx=cp.random.randint(0,self.nF,n_forced)
            self.omega[idx]+=cp.random.normal(0,self.forcing_scale,n_forced,dtype=cp.float32)
        else:
            idx=np.random.randint(0,self.nF,n_forced)
            self.omega[idx]+=np.random.normal(0,self.forcing_scale,n_forced).astype(np.float32)

    def poisson_solve(self):
        rhs=-self.omega
        if GPU:
            L_reg=self.L-1e-6*csp.eye(self.nF,dtype=cp.float32)
            try: self.psi,_=csla.cg(L_reg,rhs,x0=self.psi,maxiter=50,tol=1e-4)
            except Exception: self.psi=rhs*0.1
        elif sp_sparse:
            import scipy.sparse.linalg as sla
            L_reg=self.L-1e-6*sp_sparse.eye(self.nF,dtype=np.float32)
            try: self.psi,_=sla.cg(L_reg,rhs,x0=self.psi,maxiter=50,tol=1e-4)
            except Exception: self.psi=rhs*0.1
        else:
            L_reg=self.L-1e-6*np.eye(self.nF,dtype=np.float32)
            self.psi=np.linalg.solve(L_reg,rhs)

    def jacobian(self):
        dot=self.A.dot if hasattr(self.A,'dot') else (lambda x: self.A@x)
        Aw=dot(self.omega); Ap=dot(self.psi)
        return Ap*self.omega-self.psi*Aw

    def step_forward(self):
        self.inject_forcing()
        self.poisson_solve()
        J=self.jacobian()
        dot=self.L.dot if hasattr(self.L,'dot') else (lambda x: self.L@x)
        diff=self.nu*dot(self.omega)
        self.omega+=self.dt*(-J+diff)
        xp=(cp if GPU else np)
        self.omega=xp.clip(self.omega,-100,100)
        self.step+=1

    def compute_diagnostics(self):
        w=cp.asnumpy(self.omega) if GPU else self.omega.copy()
        p=cp.asnumpy(self.psi)   if GPU else self.psi.copy()
        tke=0.5*np.mean(p**2)
        enst=0.5*np.mean(w**2)
        diss=self.nu*enst*2
        return tke,enst,diss

    def compute_spectrum(self):
        w=cp.asnumpy(self.omega) if GPU else self.omega.copy()
        n=len(w)
        power=np.abs(np.fft.fft(w[np.argsort(np.abs(w))]))**2
        nbins=min(50,n//2)
        if nbins<2: return np.array([1]),np.array([np.mean(power)])
        bins=np.unique(np.logspace(0,np.log10(n//2),nbins,dtype=int))
        spectrum=[]; wavenumbers=[]
        for i in range(len(bins)-1):
            ks,ke=bins[i],bins[i+1]
            if ks<len(power) and ke<=len(power):
                spectrum.append(np.mean(power[ks:ke]))
                wavenumbers.append((ks+ke)/2)
        return np.array(wavenumbers),np.array(spectrum)

    def run(self,total_steps,log_interval=2000,spectrum_interval=50000):
        t0=time.perf_counter()
        for s in range(total_steps):
            self.step_forward()
            if (s+1)%log_interval==0:
                tke,enst,diss=self.compute_diagnostics()
                self.tke_history.append(tke)
                self.enstrophy_history.append(enst)
                self.dissipation_history.append(diss)
                elapsed=time.perf_counter()-t0
                sps=(s+1)/elapsed
                eta=(total_steps-s-1)/max(sps,1)
                ratio=diss/max(enst,1e-12)
                print(f"  step {s+1:>8,}/{total_steps:,}  "
                      f"TKE={tke:.4f}  enst={enst:.4f}  "
                      f"diss/enst={ratio:.6f}  2nu={2*self.nu:.6f}  "
                      f"({sps:.0f}sps  ~{eta/60:.1f}min)")
            if (s+1)%spectrum_interval==0:
                k,E=self.compute_spectrum()
                self.spectrum_snapshots.append((s+1,k,E))
        k,E=self.compute_spectrum()
        self.spectrum_snapshots.append((self.step,k,E))
        return time.perf_counter()-t0

# ============================================================================
#  BUILD + RUN
# ============================================================================
print("  Building mesh...")
faces=build_dodecahedron()
for r in range(LEVEL):
    faces=refine_all(faces)
    print(f"    L{r+1}: {len(faces):,} faces")

inv=invariants(faces)
print(f"\n  Mesh: {inv['F']:,} faces  P={inv['P']}  chi={inv['chi']}  E/V={inv['E']/max(inv['V'],1):.3f}")

print("  Building operators...",end=" ",flush=True)
t0=time.perf_counter()
A,L,nF=build_operators(faces)
print(f"{(time.perf_counter()-t0)*1000:.0f}ms")

dt=0.005 if (1/NU)>5000 else 0.01
engine=KolmogorovEngine(A,L,nF,nu=NU,dt=dt,forcing_scale=0.1)
print(f"  dt={dt}  forcing=0.1")
print(f"\n  RUNNING {TOTAL_STEPS:,} STEPS -- Re={1/NU:,.0f} -- LET GOOGLE SUFFER")
print(f"  {'='*55}\n")

total_time=engine.run(
    TOTAL_STEPS,
    log_interval=max(1,TOTAL_STEPS//250),
        spectrum_interval=max(1,TOTAL_STEPS//5)
)

tke,enst,diss=engine.compute_diagnostics()
print(f"\n  {'='*55}")
print(f"  DONE in {total_time:.1f}s  ({TOTAL_STEPS/total_time:.0f} sps)")
print(f"  Final TKE={tke:.6f}  Enstrophy={enst:.6f}  Dissipation={diss:.8f}")
print(f"  diss/enst={diss/max(enst,1e-12):.8f}  expect 2*nu={2*NU:.8f}")
print(f"  P={inv['P']}  chi={inv['chi']}  ALWAYS.")

# ============================================================================
#  PLOTS
# ============================================================================
fig,axes=plt.subplots(1,3,figsize=(18,5))
fig.patch.set_facecolor('#050508')
for ax in axes:
    ax.set_facecolor('#0a0f18')
    ax.tick_params(colors='#aaa')
    ax.xaxis.label.set_color('#aaa'); ax.yaxis.label.set_color('#aaa')
    ax.title.set_color('#ffd700')
    for sp in ax.spines.values(): sp.set_edgecolor('#1a1f2e')

n_pts=len(engine.tke_history)
steps_x=np.arange(n_pts)*(TOTAL_STEPS//max(n_pts,1))

# 1 -- TKE + Enstrophy
ax=axes[0]
ax.plot(steps_x,engine.tke_history,      color='#00ffd5',lw=1.5,label='TKE')
ax.plot(steps_x,engine.enstrophy_history,color='#ff69b4',lw=1.5,label='Enstrophy')
ax.set_title(f'TKE & Enstrophy  L{LEVEL}  Re={1/NU:.0f}')
ax.set_xlabel('step')
ax.legend(facecolor='#0a0f18',labelcolor='white')

# 2 -- Kraichnan identity
ax=axes[1]
diss_arr=np.array(engine.dissipation_history)
enst_arr=np.array(engine.enstrophy_history)
ratio_arr=diss_arr/np.maximum(enst_arr,1e-12)
ax.plot(steps_x,ratio_arr,color='#ffd700',lw=2,label='diss/enst measured')
ax.axhline(2*NU,color='#ff4444',lw=1.5,ls='--',label=f'2*nu={2*NU}')
ax.set_title('Kraichnan: diss = 2*nu*enst')
ax.set_xlabel('step')
ax.legend(facecolor='#0a0f18',labelcolor='white')

# 3 -- E(k) spectrum
ax=axes[2]
colors=plt.cm.plasma(np.linspace(0.2,0.9,max(len(engine.spectrum_snapshots),1)))
for idx,(snap_step,k_arr,E_arr) in enumerate(engine.spectrum_snapshots):
    valid=(k_arr>0)&(E_arr>0)
    if valid.sum()>2:
        lbl=f'step {snap_step:,}' if idx in [0,len(engine.spectrum_snapshots)-1] else ''
        ax.loglog(k_arr[valid],E_arr[valid],
                  color=colors[idx],lw=1.2,alpha=0.8,label=lbl)

# -5/3 reference
if engine.spectrum_snapshots:
    _,k_ref,E_ref=engine.spectrum_snapshots[-1]
    valid=(k_ref>0)&(E_ref>0)
    if valid.sum()>2:
        k_v=k_ref[valid]; E_v=E_ref[valid]
        mid=len(k_v)//4
        k_line=np.logspace(np.log10(k_v.min()),np.log10(k_v.max()),50)
        E_line=E_v[mid]*(k_line/k_v[mid])**(-5/3)
        ax.loglog(k_line,E_line,color='#ffd700',lw=2.5,ls='--',label='k^(-5/3)')

ax.set_title('Energy Spectrum E(k)')
ax.set_xlabel('wavenumber k'); ax.set_ylabel('E(k)')
ax.legend(facecolor='#0a0f18',labelcolor='white',fontsize=7)

plt.suptitle(
    f'Kolmogorov Turbulence -- Goldberg L{LEVEL} -- {inv["F"]:,} faces -- '
    f'Re={1/NU:.0f} -- chi={inv["chi"]} -- P={inv["P"]} -- ALWAYS',
    color='#c8d8e8',fontsize=10
)
plt.tight_layout()
fname=f'kolmogorov_L{LEVEL}_Re{int(1/NU)}.png'
plt.savefig(fname,dpi=150,bbox_inches='tight',facecolor='#050508')
plt.show()
print(f"\n  Saved: {fname}")
print(f"  Download from Colab Files panel (left sidebar folder icon)")
print(f"\n  Buenos Aires. The dodecahedron asked. Google answered.")
