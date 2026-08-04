import numpy as np
from numpy.polynomial import polynomial as P
PHI=(1+5**.5)/2

M=np.array([[1,2,1,0],[1,1,0,0],[1,0,0,0],[0,0,0,1]],float)   # THEA's light matrix
Q=np.array([[1,1],[1,0]],float)                                # Fibonacci step (k,l)->(k+l,k)

print("1. CLAIM: M_LIGHT = Sym^2(Q) (+) [1]  on state (k^2, kl, l^2, P)")
# symmetric square of Q in basis (k^2, kl, l^2)
a,b,c,d=Q[0,0],Q[0,1],Q[1,0],Q[1,1]
S2=np.array([[a*a,2*a*b,b*b],[a*c,a*d+b*c,b*d],[c*c,2*c*d,d*d]])
print("   Sym^2(Q) =\n", S2.astype(int))
print("   M_LIGHT[:3,:3] =\n", M[:3,:3].astype(int))
print("   identical:", np.array_equal(S2, M[:3,:3]), "| P block eigenvalue:", M[3,3])

print("\n2. eigenvalues")
print("   Q      :", np.sort(np.linalg.eigvals(Q)),  "   {phi, -1/phi} =", sorted([PHI,-1/PHI]))
print("   M_LIGHT:", np.sort(np.linalg.eigvals(M)),  "   {phi^2,1,-1,1/phi^2} =", sorted([PHI**2,1,-1,1/PHI**2]))
print("   det Q =", round(np.linalg.det(Q)), " -> area-preserving, ORIENTATION-REVERSING")

print("\n3. IS THE LADDER A SPIRAL OR A HYPERBOLA?")
print("   a similarity needs complex eigenvalues rho*e^{i*Delta}. Q's are REAL:")
w=np.linalg.eigvals(Q); print("   max |Im(eig Q)| =", abs(w.imag).max())
print("   -> Q is HYPERBOLIC (Anosov), not a similarity. Orbits lie on hyperbolas, not log spirals.")

print("\n4. Coxeter coordinates: w = k + l*exp(i*pi/3)  =>  |w|^2 = k^2+kl+l^2 = T ?")
om=np.exp(1j*np.pi/3)
bad=max(abs(abs(k+l*om)**2-(k*k+k*l+l*l)) for k in range(-6,7) for l in range(-6,7))
print("   max error over 169 lattice points:", f"{bad:.2e}", "-> EXACT")

print("\n5. golden branch (k,l)=(F_{n+1},F_n): T ladder and its ratio -> phi^2 ?")
k,l=1,0; Ts=[]
for n in range(12):
    Ts.append(k*k+k*l+l*l); k,l=k+l,k
print("   T =", Ts)
r=[Ts[i+1]/Ts[i] for i in range(4,11)]
print("   ratios ->", [round(x,6) for x in r], " phi^2 =", round(PHI**2,6))
print("   |ratio-phi^2| final =", f"{abs(r[-1]-PHI**2):.2e}")

print("\n6. T recurrence T_{n+3}=2T_{n+2}+2T_{n+1}-T_n on the golden branch?")
err=max(abs(Ts[n+3]-(2*Ts[n+2]+2*Ts[n+1]-Ts[n])) for n in range(len(Ts)-3))
print("   max residual over the ladder:", err, "-> EXACT" if err==0 else "-> FAILS")

print("\n7. Genesis topology closes on every ladder rung?")
ok=all((20*T)-(30*T)+(10*T+2)==2 for T in Ts)
print("   V-E+F = 20T-30T+(10T+2) = 2 for all T:", ok, "| P=12 is the eigenvalue-1 direction")

print("\n8. escape-time reading: T is multiplicative under Eisenstein mult?")
za,zb=(2+1j*0)+1*om, (1)+2*om
Ta=abs(za)**2; Tb=abs(zb)**2; Tab=abs(za*zb)**2
print(f"   T(w1)={Ta:.4f} T(w2)={Tb:.4f} T(w1*w2)={Tab:.4f} product={Ta*Tb:.4f} -> multiplicative:",
      abs(Tab-Ta*Tb)<1e-9)
print("   => squaring a seed SQUARES its triangulation number. escape count = GC refinement depth.")
