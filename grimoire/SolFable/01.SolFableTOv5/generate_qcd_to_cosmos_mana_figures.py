#!/usr/bin/env python3
"""Generate the seven figures for the QCD-to-Cosmos Mana Codex.

The plots are pedagogical receipts.  They use the same toy assumptions declared
in the LaTeX source and do not claim a precision QCD or neutron-star fit.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from verify_qcd_to_cosmos_mana_v100 import lane_emden, run


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="qcd_to_cosmos_mana_figures")
    args = parser.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    receipt = run()

    # 1. Illustrative one-loop QCD running.
    alpha_mz = 0.118
    mz = 91.1876
    nf = 5
    beta0 = 11 - 2 * nf / 3
    Lambda = receipt["computed_tables"]["Lambda_QCD_1loop_GeV"]
    Q = np.logspace(math.log10(max(Lambda * 1.15, 0.11)), 4, 700)
    alpha = 4 * math.pi / (beta0 * np.log(Q**2 / Lambda**2))
    plt.figure(figsize=(8.6, 5.0))
    plt.plot(Q, alpha)
    plt.axvline(mz, linestyle="--", label=r"$M_Z$ anchor")
    plt.axvline(Lambda, linestyle=":", label=r"$\Lambda_{\rm 1\,loop}$")
    plt.xscale("log")
    plt.ylim(0, min(1.6, np.nanmax(alpha[np.isfinite(alpha)])))
    plt.xlabel(r"Renormalization scale $Q$ (GeV)")
    plt.ylabel(r"$\alpha_s(Q)$")
    plt.title("One-loop asymptotic freedom (illustrative, not a precision fit)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "qcd_running_coupling.png", dpi=200)
    plt.close()

    # 2. Relativistic degenerate Fermi-gas EOS.
    x = np.logspace(-3, 3, 800)
    p = (x*np.sqrt(1+x*x)*(2*x*x-3) + 3*np.arcsinh(x))/(24*math.pi**2)
    n = x**3/(3*math.pi**2)
    p = np.maximum(p, np.finfo(float).tiny)
    plt.figure(figsize=(8.6, 5.0))
    plt.loglog(n, p, label="exact zero-temperature Fermi gas")
    i_nr = np.argmin(np.abs(x - 0.02))
    i_ur = np.argmin(np.abs(x - 50))
    plt.loglog(n, p[i_nr]*(n/n[i_nr])**(5/3), linestyle="--", label=r"$P\propto n^{5/3}$")
    plt.loglog(n, p[i_ur]*(n/n[i_ur])**(4/3), linestyle=":", label=r"$P\propto n^{4/3}$")
    plt.xlabel(r"Number density $n/m^3$ in natural units")
    plt.ylabel(r"Pressure $P/m^4$")
    plt.title("Degenerate matter crosses from nonrelativistic to ultrarelativistic")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "fermi_eos_transition.png", dpi=200)
    plt.close()

    # 3. Lane-Emden profiles.
    plt.figure(figsize=(8.6, 5.0))
    for n_index in (1.0, 1.5, 3.0):
        xi1, _, sol = lane_emden(n_index, 9.0)
        grid = np.linspace(0.0001, xi1, 500)
        theta = sol.sol(grid)[0]
        plt.plot(grid, theta, label=fr"$n={n_index:g}$, $\xi_1={xi1:.4f}$")
    plt.axhline(0, linewidth=0.8)
    plt.xlabel(r"Dimensionless radius $\xi$")
    plt.ylabel(r"Lane--Emden function $\theta(\xi)$")
    plt.title("Polytropic stellar profiles")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "lane_emden_profiles.png", dpi=200)
    plt.close()

    # 4 and 5. TOV mass-radius and compactness sequence.
    rows = np.asarray(receipt["computed_tables"]["tov_linear_eos"], dtype=float)
    pc, mass, radius, compactness = rows.T
    imax = int(np.argmax(mass))
    plt.figure(figsize=(8.6, 5.0))
    plt.plot(radius, mass)
    plt.scatter([radius[imax]], [mass[imax]], label="maximum-mass turning point")
    plt.xlabel(r"Scaled radius $R\sqrt{\epsilon_0}$")
    plt.ylabel(r"Scaled mass $M\sqrt{\epsilon_0}$")
    plt.title(r"TOV sequence for $P=(\epsilon-\epsilon_0)/3$ (toy quark-star EOS)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "tov_linear_eos_mass_radius.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8.6, 5.0))
    plt.plot(pc, compactness)
    plt.xscale("log")
    plt.axhline(8/9, linestyle="--", label="Buchdahl bound")
    plt.xlabel(r"Central pressure $P_c/\epsilon_0$")
    plt.ylabel(r"Compactness $2M/R$")
    plt.title("Toy TOV compactness remains below the black-hole limit")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "tov_compactness.png", dpi=200)
    plt.close()

    # 6. FLRW density scaling.
    a = np.logspace(-6, 1, 700)
    plt.figure(figsize=(8.6, 5.0))
    plt.loglog(a, a**-4, label=r"radiation $w=1/3$")
    plt.loglog(a, a**-3, label=r"matter $w=0$")
    plt.loglog(a, a**-2, label=r"curvature-like $a^{-2}$")
    plt.loglog(a, np.ones_like(a), label=r"vacuum $w=-1$")
    plt.xlabel("Scale factor a (arbitrary normalization)")
    plt.ylabel(r"Relative density $\rho(a)/\rho(1)$")
    plt.title("Friedmann continuity equation: four scaling laws")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / "friedmann_density_scaling.png", dpi=200)
    plt.close()

    # 7. Schematic QCD-to-cosmos length ladder.
    labels = [
        "hard QCD", "hadron", "nucleus", "atom", "neutron star",
        "white dwarf", "star", "galaxy", "Hubble radius",
    ]
    lengths = np.asarray([1e-18, 1e-15, 1e-14, 1e-10, 1e4, 1e7, 7e8, 1e21, 1e26])
    y = np.arange(len(labels))
    plt.figure(figsize=(9.2, 5.5))
    plt.scatter(lengths, y)
    for xi, yi, label in zip(lengths, y, labels):
        plt.text(xi * 1.2, yi, label, va="center")
    plt.xscale("log")
    plt.yticks([])
    plt.xlabel("Characteristic length scale (m, schematic)")
    plt.title("The renormalization ladder becomes the astrophysical ladder")
    plt.tight_layout()
    plt.savefig(out / "qcd_to_cosmos_scale_ladder.png", dpi=200)
    plt.close()

    print(f"Created 7 figures in {out}")


if __name__ == "__main__":
    main()
