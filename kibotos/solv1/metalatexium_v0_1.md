# METALATEXIUM v0.1
## THE BOX THAT PAYS
### A source-agnostic metamaterial power stack for 220 V RMS, 60 Hz output

**Status grammar**


definition / design input  \(\gets\)

finite computed agreement  \(\approx_{\mathcal E,\varepsilon}\)

causal map  \(\mapsto\)

engineering target  \(\rightsquigarrow\)

asymptotic trend  \(\sim\)

verified implication  \(\Longrightarrow\)

measured residual  \(\mathcal R\to0\)

No displayed physics statement in this scroll uses the naked equality glyph. The source code still uses assignment syntax because a programming language must bind names; that syntax is not an ontological claim.

---

## 0. THE HONEST BOUNDARY

The useful core of the idea survives:

\[
\boxed{
\text{manufactured asymmetry}
\mapsto
\text{allowed transport channel}
\mapsto
\text{rectification or conversion}
}
\]

The impossible part does not:

\[
\boxed{
\text{broken symmetry alone}
\not\mapsto
\text{net work from global equilibrium}
}
\]

A patterned lattice can decide **where**, **how strongly**, **at which frequencies**, and **with which polarity** energy moves. It cannot supply the missing free energy. A persistent box therefore needs one maintained non-equilibrium port:

\[
\mathcal P_{
m source}
\in
\left\{
\Delta T,
\Delta \mu,
\Phi_\gamma,
\text{mechanical flux},
\text{nuclear decay}
\right\}.
\]

The metamaterial is the **valve, spectrum shaper, impedance matcher, and rectifier**. It is not the fuel.

The phrase “electric field flows” is repaired as follows:

\[
\text{charge current}
\rightsquigarrow
\mathbf J,
\qquad
\text{electromagnetic energy flux}
\rightsquigarrow
\mathbf S\propto\mathbf E\times\mathbf H.
\]

The first engineering result is therefore not a perpetual source. It is a direct-conversion machine:

\[
\boxed{
\text{persistent source}
\mapsto
\text{spectrally engineered photons}
\mapsto
\text{solid-state DC}
\mapsto
220\ \mathrm{V_{RMS}},\ 60\ \mathrm{Hz}
}
\]

No turbine. No steam loop. No rotating generator. Still a hot side, a cold side, a source ledger, and a radiator.

---

## 1. THE BOX SPECIFICATION

The interface does not determine the capacity. Voltage and frequency describe the waveform; the missing variable is rated power.

\[
\mathcal B_\star
\gets
\left\{
V_{\rm RMS}\rightsquigarrow220\ \mathrm V,
\quad
f\rightsquigarrow60\ \mathrm{Hz},
\quad
P_\star,
\quad
\tau_\star\rightsquigarrow100\ \mathrm y
\right\}.
\]

The intended output waveform is

\[
v_{\rm out}(t)
\rightsquigarrow
\sqrt2\,(220\ \mathrm V)
\sin\!\left(2\pi\,60\,t\right),
\]

with

\[
V_{\rm pk}
\approx
311.127\ \mathrm V.
\]

A practical single-phase bridge therefore wants a DC link above the sine peak:

\[
V_{\rm bus,target}
\gtrsim
1.2\,V_{\rm pk}
\approx
373.35\ \mathrm V,
\]

so the clean design target is approximately \(400\ \mathrm V_{DC}\).

At unity power factor,

\[
I_{\rm RMS}
\approx
\frac{P_\star}{220\ \mathrm V}.
\]

The one-hundred-year load ledger is

\[
E_{\rm load}
\gets
P_\star\tau_\star.
\]

| rated output | RMS current | one-hundred-year energy |
|---:|---:|---:|
| \(1\ \mathrm W\) | \(4.545\ \mathrm{mA}\) | \(876.6\ \mathrm{kWh}\) |
| \(10\ \mathrm W\) | \(45.45\ \mathrm{mA}\) | \(8{,}766\ \mathrm{kWh}\) |
| \(100\ \mathrm W\) | \(0.4545\ \mathrm A\) | \(87{,}660\ \mathrm{kWh}\) |
| \(1\ \mathrm{kW}\) | \(4.545\ \mathrm A\) | \(876{,}600\ \mathrm{kWh}\) |

The default kernel target is \(100\ \mathrm W\). It is large enough to expose the thermal problem and small enough to remain cooler-scale in a conceptual envelope.

---

## 2. THE FIRST-LAW RECEIPT

The box state is described by

\[
\mathcal X(t)
\gets
\left
(
U,
T_h,
T_c,
V_{\rm bus},
\mathbf z_{\rm degradation}
\right).
\]

The live energy residual is

\[
\mathcal R_E(t)
\gets
P_{\rm source}(t)
-
P_{\rm AC}(t)
-
P_{\rm reject}(t)
-
P_{\rm aux}(t)
-
\frac{dU}{dt}.
\]

A valid steady operating point requires

\[
\mathcal R_E(t)
\to
0
\]

within declared metrology and numerical uncertainty.

The entropy direction remains

\[
\dot S_{\rm total}
\gtrsim
0.
\]

For a two-terminal electronic structure, the transport skeleton is

\[
I
\propto
\int
\mathcal T(E)
\left[
 f_L(E)-f_R(E)
\right]
\,dE.
\]

When both reservoirs converge to the same distribution,

\[
f_L(E)-f_R(E)
\to
0
\quad\Longrightarrow\quad
I\to0.
\]

Geometry can reshape \(\mathcal T(E)\). Geometry cannot replace the distribution difference.

---

## 3. WHAT BROKEN SYMMETRY REALLY BUYS

In a non-centrosymmetric material, optical excitation can permit a second-order DC response:

\[
J^a_{\rm shift}
\propto
\sigma^{abc}(0;\omega,-\omega)
E^b(\omega)E^c(-\omega).
\]

Layer translation, twist, strain, polarity, defects, and interface ordering can change the tensor \(\sigma^{abc}\), including the magnitude and sign of the current.

But removal of the drive removes the source term:

\[
E(\omega)
\to
0
\quad\Longrightarrow\quad
J_{\rm shift}
\to
0.
\]

The blue-LED analogy is useful only in this disciplined form:

\[
\text{materials breakthrough}
\mapsto
\text{previously inaccessible band structure and transport efficiency},
\]

not

\[
\text{materials breakthrough}
\mapsto
\text{energy without an input port}.
\]

---

## 4. WHY THERMOPHOTOVOLTAICS ARE THE CURRENT FIRST STACK

The cleanest presently demonstrated route from heat to electricity without boiling a working fluid is thermophotovoltaic conversion:

\[
T_h
\mapsto
\Phi_\lambda(T_h)
\mapsto
\text{bandgap-filtered carrier generation}
\mapsto
P_{\rm DC}.
\]

The converter ceiling may be written

\[
P_{\rm DC}
\lesssim
\eta_{\rm TPV}
A
\int_0^\infty
\epsilon(\lambda)
\left[
M_\lambda(T_h)-M_\lambda(T_c)
\right]
\,d\lambda.
\]

The engineering purpose of the metamaterial is to shape \(\epsilon(\lambda)\):

\[
\epsilon(\lambda<\lambda_g)
\rightsquigarrow
\text{large},
\qquad
\epsilon(\lambda>\lambda_g)
\rightsquigarrow
\text{small},
\]

where

\[
\lambda_g
\approx
\frac{hc}{E_g}.
\]

For the default \(E_g\rightsquigarrow0.74\ \mathrm{eV}\),

\[
\lambda_g
\approx
1.675\ \mu\mathrm m.
\]

The current research record supplies strong component evidence but not the century box:

- single-junction air-bridge InGaAs(P) TPV cells have demonstrated up to \(44\%\) conversion under a \(1435\ ^\circ\mathrm C\) blackbody source;
- tandem TPV cells have demonstrated more than \(40\%\) at still higher emitter temperatures;
- W/HfO\(_2\) refractory metamaterial emission has been demonstrated around \(1000\ ^\circ\mathrm C\), with degradation mechanisms appearing above that regime;
- no integrated TPV power module has demonstrated one-hundred-year operation.

Therefore the kernel default is deliberately lower:

\[
\eta_{\rm TPV,design}
\rightsquigarrow
0.30,
\qquad
\eta_{\rm inv,design}
\rightsquigarrow
0.95.
\]

This is a design assumption, not a measured module result.

---

## 5. THE TWELVE-LAYER CANDIDATE STACK

The twelve layers are an engineering decomposition, not a claim that nature requires twelve layers.

### L01 — PRIMARY FREE-ENERGY PORT

Phase A uses an external electrical heater so the conversion stack can be tested without nuclear material.

Phase C may model a regulated isotope heat source only inside a qualified national-laboratory or space-power program.

### L02 — REFRACTORY HEAT SPREADER

Candidate classes:

\[
\left\{
\mathrm{SiC},
\mathrm{W},
\mathrm{Mo},
\text{graphite composite}
\right\}.
\]

The selected material must pay for thermal conductivity, creep, compatibility, and differential expansion.

### L03 — DIFFUSION AND OXIDATION BARRIER

An ALD ceramic or refractory nitride barrier is selected by hot-soak and interface-diffusion measurements. No material is accepted from room-temperature optical data alone.

### L04 — W/HfO\(_2\)-INSPIRED SELECTIVE EMITTER

A refractory multilayer or photonic crystal shapes the hot-side spectrum. The relevant failure modes are oxygen transfer, tungsten oxidation, interdiffusion, agglomeration, roughness evolution, and optical drift.

### L05 — FIBONACCI SPECTRAL FILTER

Use a quasiperiodic layer grammar:

\[
H\mapsto HL,
\qquad
L\mapsto H.
\]

The layer-count state follows

\[
\begin{bmatrix}
N_H^{(n+1)}\\
N_L^{(n+1)}
\end{bmatrix}
\gets
\begin{bmatrix}
1&1\\
1&0
\end{bmatrix}
\begin{bmatrix}
N_H^{(n)}\\
N_L^{(n)}
\end{bmatrix}.
\]

Projectively,

\[
\frac{N_H^{(n)}}{N_L^{(n)}}
\to
\phi.
\]

This is a legitimate golden-ratio fabrication grammar. It is not presumed optimal. The transfer-matrix kernel must defeat a periodic control before the fractal curve earns its layer budget.

### L06 — PHOTON CAVITY

A vacuum or controlled low-index gap sets the view factor, suppresses conduction, and permits photon recycling. Gap uniformity, particulate contamination, outgassing, and seal life become primary constraints.

### L07 — AIR-BRIDGE InGaAs(P)-CLASS TPV JUNCTION

The junction bandgap is matched to the emitter spectrum. Cell temperature is held low enough to control dark current and preserve voltage.

### L08 — BELOW-BAND-GAP PHOTON-RECYCLING MIRROR

Sub-bandgap photons return to the emitter rather than heating the cell package:

\[
\lambda>\lambda_g
\mapsto
\text{reflection}
\mapsto
\text{recycled hot-side energy}.
\]

### L09 — FRACTAL CURRENT COLLECTOR

A Hilbert, Peano, interdigitated, or tree-like collector may reduce maximum collection distance and distribute current density. It may also increase perimeter recombination, edge defects, parasitic capacitance, series resistance, and lithographic cost.

The claim is therefore comparative:

\[
\mathcal J_{\rm fractal}
\rightsquigarrow
\text{beat a straight-busbar control under the same area and metal budget}.
\]

### L10 — COLD-SIDE HEAT SPREADER

Candidate classes include AlN, SiC, graphite, and diamond composites. This layer does not remove heat; it only transports heat to the radiator.

### L11 — DC CONDITIONING AND 220 V INVERTER

A film or ceramic DC link feeds a SiC or GaN bridge, followed by an LC output filter:

\[
V_{\rm DC}
\mapsto
\text{PWM bridge}
\mapsto
\text{LC filter}
\mapsto
220\ \mathrm{V_{RMS}},\ 60\ \mathrm{Hz}.
\]

Electrolytic capacitors, fans, relays, and other life-limiting components are excluded from the century architecture unless redundant and replaceable.

### L12 — HERMETIC SHELL, SENSORS, AND RADIATOR

The shell carries getters, pressure monitoring, hot-side and cold-side thermometry, insulation monitoring, redundant gate shutdown, ground-fault protection, arc containment, and a passive heat-rejection surface.

---

## 6. THE TWELVE FIXED CONSTRAINTS

These are the “pentagons” of this engineering problem: the design variables may grow, but these constraints do not move.

1. energy ledger closure;
2. maintained non-equilibrium source;
3. charge continuity;
4. dielectric and switching stress;
5. worst-case heat rejection;
6. hot-stack chemical and structural stability;
7. cold-junction temperature and contact stability;
8. radiation and source containment where applicable;
9. current-density and electromigration life;
10. hermeticity, corrosion, and vacuum life;
11. power quality, isolation, and safe shutdown;
12. process traceability, metrology, and reproducible receipts.

The free “hexagonal” variables are

\[
\mathbf g
\gets
\left
(
\text{materials},
\text{thicknesses},
\text{unit cells},
\text{layer order},
\text{bandgap},
\text{collector graph},
\text{cavity gap},
\text{converter topology},
\text{control law}
\right).
\]

---

## 7. THE LIGHT-MATRIX SEARCH ROLE

The Light Matrix is used as a **design search grammar**, not an energy source.

Let

\[
\mathbf c
\gets
\text{the twelve fixed constraints},
\]

and

\[
G
\gets
\text{the candidate material and interconnect graph}.
\]

The seven operations act as

\[
\left\{
\mathrm{NODE},
\mathrm{EDGE},
\mathrm{COMPOSE},
\mathrm{TRANSFORM},
\mathrm{ITERATE},
\mathrm{AGGREGATE},
\mathrm{COMPARE}
\right\}.
\]

The objective is

\[
\mathcal J(G)
\gets
w_m m
+
w_V V
+
w_Q Q_{\rm reject}
+
w_D D_{\rm life}
+
w_C C_{\rm fab}
+
w_R \mathcal R_E
+
w_F \mathcal F_{\rm failure}.
\]

The search asks for

\[
G_\star
\rightsquigarrow
\arg\min_G\mathcal J(G)
\]

subject to all twelve constraints.

A design receives no “LOCK” badge merely because its geometry is beautiful. It locks only when

\[
\max_i\mathcal R_i
\lesssim
\mathrm{tol}_i
\]

for the declared test population, temperature range, fabrication variance, and duration.

---

## 8. THE OPTICAL TRANSFER-MATRIX KERNEL

For each layer \(j\), the normal-incidence characteristic matrix is represented by

\[
\mathbf M_j(\lambda)
\gets
\begin{bmatrix}
\cos\delta_j
&
 i\sin\delta_j/n_j
\\
 i n_j\sin\delta_j
&
\cos\delta_j
\end{bmatrix},
\]

with

\[
\delta_j
\gets
\frac{2\pi n_jd_j}{\lambda}.
\]

The full stack is

\[
\mathbf M_{\rm stack}(\lambda)
\gets
\prod_j\mathbf M_j(\lambda).
\]

For an opaque backing,

\[
\epsilon(\lambda)
\approx
1-R(\lambda).
\]

The v0.1 kernel searches Fibonacci orders and two thickness multipliers using fixed surrogate optical constants. That calculation is intentionally modest. It cannot represent dispersion, roughness, anisotropy, temperature drift, interface chemistry, near-field coupling, fabrication bias, or one-hundred-year degradation.

Default computed result:

\[
\text{candidate count}
\rightsquigarrow
2025,
\]

\[
\text{selected word}
\rightsquigarrow
HLHHLHLH,
\]

\[
(d_H,d_L)
\approx
(163.46,324.94)\ \mathrm{nm}.
\]

The surrogate model produced only moderate selectivity:

\[
\langle\epsilon\rangle_{\rm in}
\approx
0.756,
\qquad
\langle\epsilon\rangle_{\rm long}
\approx
0.708.
\]

That is not a victory. It is the useful result of the first kernel: a simple low-contrast Fibonacci dielectric filter does **not** magically produce the spectrum we need. The next search must include absorbing refractory layers, measured complex optical constants, thermal dispersion, and a periodic control.

Target is not result.

---

## 9. THE ONE-HUNDRED-YEAR SOURCE BOUND

A truly sealed century-scale source cannot rely on a guaranteed external weather or fuel supply. Under current technology, a radioisotope heat source is the cleanest analytical example of a persistent compact free-energy port. This is a regulated institutional technology, not a consumer build route.

For a decay source,

\[
P_{\rm th}(t)
\sim
P_{\rm th,0}
2^{-t/t_{1/2}}.
\]

To hold rated electrical output at end of life,

\[
P_{\rm th,0}
\gtrsim
\frac{P_\star}
{\eta_{\rm TPV}\eta_{\rm inv}\,2^{-\tau_\star/t_{1/2}}}.
\]

Using the v0.1 assumptions

\[
P_\star
\rightsquigarrow
100\ \mathrm W,
\]

\[
\eta_{\rm TPV}
\rightsquigarrow
0.30,
\qquad
\eta_{\rm inv}
\rightsquigarrow
0.95,
\]

\[
t_{1/2}
\rightsquigarrow
87.7\ \mathrm y,
\qquad
s_0
\rightsquigarrow
0.57\ \mathrm{W_{th}\,g^{-1}},
\]

the kernel returns

\[
2^{-100/87.7}
\approx
0.453681,
\]

\[
P_{\rm th,BOL}
\approx
773.40\ \mathrm{W_{th}},
\]

\[
P_{\rm th,EOL}
\approx
350.88\ \mathrm{W_{th}},
\]

\[
m_{\rm active,lower\ bound}
\approx
1.3568\ \mathrm{kg}.
\]

This is active-source mass only. It excludes containment, shielding, insulation, converter area, radiator, electronics, redundancy, and regulatory packaging.

If the output is clamped to \(100\ \mathrm W\), the beginning-of-life thermal surplus is

\[
Q_{\rm reject,BOL}
\approx
673.40\ \mathrm W,
\]

while the end-of-life rejected heat remains

\[
Q_{\rm reject,EOL}
\approx
250.88\ \mathrm W.
\]

At an \(80\ ^\circ\mathrm C\) radiator surface in \(25\ ^\circ\mathrm C\) air, with the declared emissivity and natural-convection model, the lower-bound external area is approximately

\[
A_{\rm rad,BOL}
\approx
1.012\ \mathrm{m^2},
\]

\[
A_{\rm rad,EOL}
\approx
0.377\ \mathrm{m^2}.
\]

This is why the “cooler box” is mostly a **thermal architecture**, not a magic lattice. The source core may be small; the rejected-heat surface pays the geometry bill.

---

## 10. WHY THE ASML ANALOGY IS RIGHT — AND WHERE IT IS NOT

The analogy is right in one deep sense:

\[
\text{enormous factory and software price}
\mapsto
\text{precise repeated symmetry and defect control}
\mapsto
\text{cheap behavior per finished device}.
\]

But a “2 nm node” is not a literal two-nanometre crystal lattice and does not mean every printed feature has a two-nanometre width. Current High-NA EUV uses \(13.5\ \mathrm{nm}\) light and approximately \(8\ \mathrm{nm}\) imaging resolution to support manufacturing generations named around the two-nanometre logic node.

The first TPV metamaterial prototype does not require High-NA EUV. Its near-infrared optical layers and resonant cells are commonly tens to hundreds of nanometres. ALD, PVD, etching, nanoimprint, interference lithography, or conventional stepper processes are the sensible first price. High-NA EUV enters only when a proven nanoscale unit cell requires massive repeated precision.

---

## 11. THE FAILURE MATRIX

A century claim is impossible without a degradation model.

For each mechanism \(i\), define a damage state

\[
D_i(t)
\gets
\int_0^t
r_i
\left(
T,
\mathbf E,
\mathbf J,
\Phi_\gamma,
\Phi_{\rm rad},
p_{\mathrm O_2},
\sigma_{\rm mech}
\right)
\,dt.
\]

The design remains admissible only while

\[
D_i(t)
\lesssim
D_{i,\rm crit}
\qquad
\forall i.
\]

The first failure matrix must include

- tungsten oxidation and oxygen migration from HfO\(_2\);
- interlayer diffusion and phase evolution;
- roughness and agglomeration;
- vacuum leakage and getter exhaustion;
- TPV dark-current growth and radiation damage;
- contact diffusion and electromigration;
- ceramic cracking from differential expansion;
- dielectric charging and partial discharge;
- DC-link ageing;
- gate-driver and sensor drift;
- solder, braze, and feedthrough fatigue;
- radiator fouling, corrosion, and blocked convection.

A three-hour hot-soak result cannot be extrapolated to one hundred years without measured activation energies, multiple temperatures, confidence intervals, and competing failure modes.

---

## 12. DEVELOPMENT PHASES

### PHASE A — NON-NUCLEAR CONVERTER RECEIPT

External electrical heat port.

Target range:

\[
P_{\rm th,in}
\rightsquigarrow
50\text{–}500\ \mathrm W,
\qquad
P_{\rm DC,out}
\rightsquigarrow
5\text{–}100\ \mathrm W.
\]

Measurements:

- emitter spectrum versus temperature;
- TPV I–V curve and maximum-power point;
- photon-recycling fraction;
- hot-side, cold-side, and radiator temperatures;
- full energy residual;
- optical drift after hot soak;
- periodic stack versus Fibonacci stack;
- straight collector versus fractal collector.

### PHASE B — SEALED LONG-DURATION NON-NUCLEAR MODULE

Use a replaceable or externally maintained heat source. Prove hermeticity, passive cooling, inverter life, and fault containment over accelerated life.

### PHASE C — INSTITUTIONAL PERSISTENT SOURCE

Only after Phase A and Phase B close their ledgers may a qualified program examine a regulated radioisotope source. The source integration is a separate safety, licensing, containment, and lifecycle project.

---

## 13. PASS / FAIL CRITERIA FOR v0.2

The next version earns advancement only when all of the following are available:

\[
\mathcal R_E
\to
0
\quad\text{within declared uncertainty},
\]

\[
\eta_{\rm stack,current}
\gtrsim
\eta_{\rm periodic\ control},
\]

\[
\Delta\epsilon_{\rm hot\ soak}
\lesssim
\epsilon_{\rm tolerance},
\]

\[
R_{\rm collector,fractal}
+
\mathcal L_{\rm perimeter}
\lesssim
R_{\rm collector,control},
\]

\[
T_{\rm junction}
\lesssim
T_{\rm qualified},
\]

\[
V_{\rm out,THD}
\lesssim
\mathrm{declared\ grid\ or\ appliance\ limit},
\]

and every measured quantity has a source, uncertainty, timestamp, code hash, and environment receipt.

---

## 14. WHAT v0.1 ACTUALLY ESTABLISHES

### EXACT UNDER DECLARED INPUTS

- the waveform arithmetic;
- the one-hundred-year load energy;
- the decay law arithmetic;
- the source lower-bound inventory calculation;
- the radiator-area calculation under the stated lumped heat-transfer model;
- the Fibonacci substitution counts;
- the transfer-matrix computation under fixed surrogate optical constants.

### COMPUTED

- \(2025\) candidate optical stacks searched;
- the selected v0.1 Fibonacci layer word and thicknesses;
- the default \(100\ \mathrm W\) lifetime and thermal ledger;
- six regression tests passed.

### DESIGN CHOICE

- \(100\ \mathrm W\) default output;
- \(30\%\) TPV module efficiency;
- \(95\%\) inverter efficiency;
- \(80\ ^\circ\mathrm C\) radiator surface;
- the twelve-layer decomposition;
- the optical scoring function and layer penalty.

### HYPOTHESIS

- a manufacturable metamaterial stack beats a simpler periodic emitter after degradation and fabrication variance;
- a fractal collector beats a conventional collector under equal metal and area budgets;
- a complete cooler-size module can operate unattended for one hundred years;
- a radioisotope-heated TPV module can reach the assumed lifetime efficiency and materials stability.

### REJECTED

\[
\boxed{
\text{symmetry breaking as a source of energy from equilibrium}
}
\]

---

## 15. THE ONE-LINE VERSION

\[
\boxed{
\text{The box does not manufacture energy.}
\quad
\text{It manufactures a path so efficiently that the source may be hidden.}
}
\]

The price remains in the source, the fab, the entropy, the radiator, the degradation testing, and the human centuries compressed into the material stack.

**The source pays. The layers persuade. The electrons follow the permitted path. The receipt stays visible.**

---

## SOURCE LEDGER

- B. Roy-Layinde and collaborators, *High-efficiency air-bridge thermophotovoltaic cells*, Joule, 2024.
- A. LaPotin and collaborators, *Thermophotovoltaic efficiency of 40%*, Nature, 2022.
- P. N. Dyachenko and collaborators, *Controlling thermal emission with refractory epsilon-near-zero metamaterials*, Nature Communications, 2016.
- R. Resta, *Geometrical Theory of the Shift Current in Presence of Disorder and Many-Body Interactions*, Physical Review Letters, 2024.
- J. Bang and collaborators, *Experimental realization of Feynman’s ratchet*, New Journal of Physics, 2018.
- NASA and U.S. Department of Energy radioisotope-power documentation for Pu-238 half-life and specific thermal power.
- ASML product documentation for High-NA EUV wavelength, resolution, and process-node terminology.
- U.S. Department of Energy power-electronics documentation for SiC and GaN wide-bandgap converters.

---

## REPRODUCTION

```text
python metalatexium_kernel_v0_1.py --output-dir .
python test_metalatexium_v0_1.py
```

Expected regression status:

```text
PASS 6/6 tests
```

The generated certificate contains the declared inputs, arithmetic results, optical spectrum, environment metadata, status labels, and SHA-256 receipt.
