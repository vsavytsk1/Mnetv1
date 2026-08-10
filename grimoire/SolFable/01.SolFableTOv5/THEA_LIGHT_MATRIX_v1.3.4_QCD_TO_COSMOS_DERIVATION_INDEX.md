# QCD-to-Cosmos Mana Codex - derivation index

The codex contains 48 principal derivation lanes. `STANDARD` means accepted theory re-derived or stated with its assumptions; `THEA-EXACT` means exact Light Matrix mathematics; `COMPUTED` means independently replayed; `BRIDGE` and `OPEN` are not promoted to theorem status.

| ID | Lane | Main output | Status |
|---:|---|---|---|
| D01 | Local color covariance | transformation law for `A_mu` | STANDARD |
| D02 | Covariant-derivative commutator | nonabelian `F_mu nu` | STANDARD |
| D03 | QCD action variation | Dirac and Yang-Mills equations | STANDARD |
| D04 | Gell-Mann algebra | `C_F=4/3`, `C_A=3`, `T_F=1/2` | STANDARD / COMPUTED |
| D05 | `A_2` root geometry | exact Casimir quadratic form | STANDARD |
| D06 | Gauge fixing | Faddeev-Popov determinant and ghosts | STANDARD |
| D07 | One-loop color beta function | asymptotic freedom | STANDARD |
| D08 | RG integration | dimensional transmutation and `Lambda_QCD` | STANDARD / COMPUTED |
| D09 | Wilson-loop limit | static potential and area-law criterion | STANDARD |
| D10 | Chiral Ward identity | GMOR relation | STANDARD |
| D11 | Trace anomaly | quantum origin of hadron mass scale | STANDARD |
| D12 | Grand canonical ensemble | `p`, `s`, `n_i`, `epsilon`, `c_s^2` | STANDARD |
| D13 | Ideal quark-gluon plasma | `g_*=47.5`, `epsilon=3p` for three massless flavors | STANDARD / COMPUTED |
| D14 | Bag-model interface | toy QCD phase scale and linear EOS | STANDARD TOY |
| D15 | Relativistic fluid projection | energy and Euler equations | STANDARD |
| D16 | Cold Fermi integrals | exact `epsilon(x)`, `p(x)`, `p=n mu-epsilon` | STANDARD / COMPUTED |
| D17 | Degenerate limits | polytropic indices `5/3` and `4/3` | STANDARD / COMPUTED |
| D18 | Nuclear saturation expansion | `K_0`, `J`, `L`, composition | STANDARD EFT |
| D19 | Beta equilibrium | neutron-star and quark-matter chemical constraints | STANDARD |
| D20 | Phase equilibrium | Maxwell/Gibbs constructions | STANDARD |
| D21 | Coulomb tunneling | Gamow peak and stellar reaction scale | STANDARD / COMPUTED |
| D22 | Neutrino diffusion | mean free path, flux, and cooling scalings | STANDARD |
| D23 | Newtonian stellar structure | mass, hydrostatic, luminosity, temperature equations | STANDARD |
| D24 | Virial theorem | negative heat capacity and Kelvin-Helmholtz scale | STANDARD |
| D25 | Lane-Emden reduction | dimensionless polytropic ODE | STANDARD / COMPUTED |
| D26 | Polytropic scaling | mass-radius-central-density exponents | STANDARD |
| D27 | White-dwarf limit | `M_Ch=5.83 M_sun/mu_e^2` | STANDARD / COMPUTED |
| D28 | Static spherical GR | mass equation and metric potential | STANDARD |
| D29 | Stress-energy conservation | TOV equation with restored `c` factors | STANDARD / COMPUTED |
| D30 | Linear self-bound EOS | scale-free TOV sequence | STANDARD TOY / COMPUTED |
| D31 | Tidal response | `Lambda=(2/3)k_2 C^-5` | STANDARD |
| D32 | Hadron-quark transition | hybrid- and quark-star stability parameters | STANDARD MODEL |
| D33 | Core-collapse ledger | binding energy, electron capture, neutrino release | STANDARD |
| D34 | Schwarzschild geometry | horizon, ISCO, thin-disk efficiency | STANDARD |
| D35 | Black-hole thermodynamics | Hawking temperature and area entropy | STANDARD |
| D36 | Eddington and Bondi flow | radiative and spherical accretion rates | STANDARD |
| D37 | Thin-disk conservation | radial flux and temperature profile | STANDARD |
| D38 | Binary energy balance | chirp mass and frequency evolution | STANDARD / COMPUTED |
| D39 | Jeans analysis | instability threshold | STANDARD / COMPUTED |
| D40 | Flat-curve inversion | `rho proportional to r^-2` | STANDARD |
| D41 | FLRW dynamics | Friedmann and continuity equations | STANDARD / COMPUTED |
| D42 | Thermal expansion | `T proportional to g_*s^-1/3 a^-1` | STANDARD |
| D43 | Linear cosmological growth | `delta proportional to a` in matter domination | STANDARD |
| D44 | Vacuum stress tensor | `w=-1` criterion | STANDARD |
| D45 | Euler fullerene closure | `P=12`, total defect `4 pi` | THEA-EXACT / COMPUTED |
| D46 | Hexagonal closure algebra | `M^T Q_2 M=TQ_2` | THEA-EXACT / COMPUTED |
| D47 | Four-mode Light Matrix | spectrum `{phi^2,1,-1,phi^-2}` | THEA-EXACT / COMPUTED |
| D48 | QCD-to-THEA control gates | strong-CP correction, `D(n)` mismatch, EFT obligations | CORRECTION / OPEN |

## The one-line pipeline

```text
local SU(3)
-> quantum RG and confinement
-> hadronic/nuclear partition function
-> equation of state and transport
-> stellar structure / TOV / tidal response
-> photons, neutrinos, gravitational waves, and cosmological growth
```

Every arrow is a calculation. Algebraic resemblance alone is not an arrow.
