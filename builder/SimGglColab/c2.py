# ============================================================
#  CELL 2 — HONEST DIAGNOSTICS PATCH
#  Replaces: compute_spectrum (was argsort+FFT = fake),
#            compute_diagnostics (TKE was 0.5*mean(psi^2)),
#  Adds a real graph-eigenmode spectrum off L.
# ============================================================
import numpy as np, time
import scipy.sparse.linalg as sla_cpu

def _to_cpu(x):
    try:
        import cupy as _cp
        if isinstance(x, _cp.ndarray): return _cp.asnumpy(x)
    except Exception: pass
    return np.asarray(x)

# --- one-time: compute the lowest M Laplacian eigenmodes (the real "k" basis) ---
def _ensure_eigenbasis(self, M=256):
    if getattr(self, "_eig_ready", False): return
    print(f"  [patch] diagonalising L for {M} eigenmodes (one-time)...", flush=True)
    t0 = time.perf_counter()
    # -L is PSD on a graph; smallest eigenvalues of -L = largest spatial scales.
    # Work on CPU in float64 for a stable symmetric solve, then cache on device.
    L_cpu = self.L.get() if GPU else (self.L.toarray() if hasattr(self.L, 'toarray') else self.L)
    L_cpu = L_cpu.astype(np.float64)
    Lsym = -0.5 * (L_cpu + L_cpu.T)            # symmetrise; -L so eigenvalues >= 0
    M = min(M, self.nF - 2)
    vals, vecs = sla_cpu.eigsh(Lsym, k=M, which='SM')
    order = np.argsort(vals)
    self._eig_vals = np.maximum(vals[order], 0.0)        # graph "k^2" proxy
    self._eig_k    = np.sqrt(self._eig_vals)             # wavenumber proxy
    self._eig_vecs = vecs[:, order]                      # (nF, M), orthonormal
    self._eig_ready = True
    print(f"  [patch] eigenbasis ready: {M} modes, "
          f"k in [{self._eig_k[1]:.3g}, {self._eig_k[-1]:.3g}]  "
          f"({time.perf_counter()-t0:.1f}s)", flush=True)

def compute_spectrum_real(self):
    self._ensure_eigenbasis()
    w = _to_cpu(self.omega).astype(np.float64)
    # project vorticity onto eigenmodes: coefficients c_m = <phi_m, w>
    c = self._eig_vecs.T @ w                     # (M,)
    # energy spectrum: vorticity power per mode -> velocity energy = |c|^2 / k^2
    k = self._eig_k.copy()
    Ew = c**2                                    # enstrophy spectrum
    with np.errstate(divide='ignore', invalid='ignore'):
        Ev = np.where(k > 1e-9, Ew / self._eig_vals, 0.0)  # energy spectrum
    # log-bin in k
    good = k > 1e-9
    k, Ev = k[good], Ev[good]
    if len(k) < 4: return k, Ev
    nb = 24
    edges = np.logspace(np.log10(k.min()), np.log10(k.max()), nb+1)
    kb, Eb = [], []
    for i in range(nb):
        m = (k >= edges[i]) & (k < edges[i+1])
        if m.sum() > 0:
            kb.append(k[m].mean()); Eb.append(Ev[m].mean())
    return np.array(kb), np.array(Eb)

def compute_diagnostics_real(self):
    # gradient-based TKE: E = 0.5 * <psi, -L psi>  (energy in velocity, not psi itself)
    w = _to_cpu(self.omega).astype(np.float64)
    p = _to_cpu(self.psi).astype(np.float64)
    Lp = _to_cpu((self.L @ self.psi)) if GPU else (self.L @ p)
    Lp = np.asarray(Lp, dtype=np.float64)
    tke  = 0.5 * np.mean(p * (-Lp))      # real kinetic energy proxy
    enst = 0.5 * np.mean(w**2)           # enstrophy (unchanged — this one was fine)
    # honest dissipation: nu * <|grad omega|^2> via -L, NOT nu*enst*2
    Lw = _to_cpu((self.L @ self.omega)) if GPU else (self.L @ w)
    Lw = np.asarray(Lw, dtype=np.float64)
    diss = self.nu * np.mean(w * (-Lw))  # independent of enst -> the check has teeth
    return tke, enst, diss

# bind the fixes onto the class
KolmogorovEngine._ensure_eigenbasis   = _ensure_eigenbasis
KolmogorovEngine.compute_spectrum      = compute_spectrum_real
KolmogorovEngine.compute_diagnostics   = compute_diagnostics_real
print("  [patch] honest diagnostics installed. Re-run the BUILD+RUN cell.")