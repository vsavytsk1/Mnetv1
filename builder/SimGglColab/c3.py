# ============================================================
# CELL 3 -- HONEST RUN + REAL PLOTS
# Requires: c1.py ran (A, L, nF, NU, dt, inv all in scope)
#           c2.py ran (honest diagnostics patched onto class)
# ============================================================
import numpy as np
import matplotlib.pyplot as plt

HONEST_STEPS = 50000

print("  Building fresh engine with honest diagnostics...")
engine = KolmogorovEngine(A, L, nF, nu=NU, dt=dt, forcing_scale=0.1)
print(f"  Running {HONEST_STEPS:,} steps -- Re={1/NU:,.0f}")
print(f"  {'='*55}\n")

engine.run(
    HONEST_STEPS,
    log_interval=max(1, HONEST_STEPS//25),
    spectrum_interval=max(1, HONEST_STEPS//5)
)

tke, enst, diss = engine.compute_diagnostics()
print(f"\n  {'='*55}")
print(f"  HONEST FINAL: TKE={tke:.6f}  Enstrophy={enst:.6f}  Dissipation={diss:.8f}")
print(f"  diss/enst={diss/max(enst,1e-12):.8f}  expect 2*nu={2*NU:.8f}")
print(f"  P={inv['P']}  chi={inv['chi']}  ALWAYS.")

# ============================================================
#  PLOTS
# ============================================================
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.patch.set_facecolor('#050508')
for ax in axes:
    ax.set_facecolor('#0a0f18')
    ax.tick_params(colors='#aaa')
    ax.xaxis.label.set_color('#aaa'); ax.yaxis.label.set_color('#aaa')
    ax.title.set_color('#ffd700')
    for sp in ax.spines.values(): sp.set_edgecolor('#1a1f2e')

n_pts = len(engine.tke_history)
x = np.arange(n_pts) * (HONEST_STEPS // max(n_pts, 1))

# Plot 1 -- TKE + Enstrophy (decoupled now)
ax = axes[0]
ax.plot(x, engine.tke_history,       color='#00ffd5', lw=1.5, label='TKE (real: <psi,-L psi>/2)')
ax.plot(x, engine.enstrophy_history, color='#ff69b4', lw=1.5, label='Enstrophy')
ax.set_title('TKE & Enstrophy -- DECOUPLED')
ax.set_xlabel('step')
ax.legend(facecolor='#0a0f18', labelcolor='white', fontsize=7)

# Plot 2 -- Honest dissipation check (has teeth)
ax = axes[1]
diss_arr = np.array(engine.dissipation_history)
enst_arr = np.array(engine.enstrophy_history)
ratio    = diss_arr / np.maximum(enst_arr, 1e-12)
ax.plot(x, ratio,   color='#ffd700', lw=2,   label='diss/enst (independent)')
ax.axhline(2*NU,    color='#ff4444', lw=1.5, ls='--', label=f'2*nu={2*NU}')
ax.set_title('Dissipation check -- HAS TEETH')
ax.set_xlabel('step')
ax.legend(facecolor='#0a0f18', labelcolor='white', fontsize=8)

# Plot 3 -- REAL eigenmode spectrum
ax = axes[2]
colors = plt.cm.plasma(np.linspace(0.2, 0.9, max(len(engine.spectrum_snapshots), 1)))
for idx, (snap_step, k_arr, E_arr) in enumerate(engine.spectrum_snapshots):
    valid = (k_arr > 0) & (E_arr > 0)
    if valid.sum() > 2:
        lbl = f'step {snap_step:,}' if idx in [0, len(engine.spectrum_snapshots)-1] else ''
        ax.loglog(k_arr[valid], E_arr[valid],
                  color=colors[idx], lw=1.2, alpha=0.8, label=lbl)

# k^(-5/3) reference
if engine.spectrum_snapshots:
    _, k_ref, E_ref = engine.spectrum_snapshots[-1]
    valid = (k_ref > 0) & (E_ref > 0)
    if valid.sum() > 2:
        kv, Ev = k_ref[valid], E_ref[valid]
        mid = len(kv) // 4
        kl  = np.logspace(np.log10(kv.min()), np.log10(kv.max()), 50)
        El  = Ev[mid] * (kl / kv[mid])**(-5/3)
        ax.loglog(kl, El, color='#ffd700', lw=2.5, ls='--', label='k^(-5/3)')

ax.set_title('REAL Spectrum E(k) -- eigenmode basis')
ax.set_xlabel('wavenumber k'); ax.set_ylabel('E(k)')
ax.legend(facecolor='#0a0f18', labelcolor='white', fontsize=7)

plt.suptitle(
    f'HONEST Kolmogorov -- Goldberg L{LEVEL} -- {inv["F"]:,} faces -- '
    f'Re={1/NU:.0f} -- chi={inv["chi"]} -- P={inv["P"]} -- ALWAYS',
    color='#c8d8e8', fontsize=10
)
plt.tight_layout()
fname = f'kolmogorov_HONEST_L{LEVEL}_Re{int(1/NU)}.png'
plt.savefig(fname, dpi=150, bbox_inches='tight', facecolor='#050508')
plt.show()
print(f"\n  Saved: {fname}")
print(f"  Download from Colab Files panel")
print(f"\n  This is the real plot. No costume.")
print(f"  Buenos Aires. The dodecahedron asked. Google answered honestly.")