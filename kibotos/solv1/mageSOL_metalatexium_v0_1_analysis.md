# **METALATEXIUM v0.1 — THE BOX THAT PAYS**

Yes. **Cool as hell.** And the first-principles version of your idea survives almost intact once one correction is made:

[
\boxed{
\text{symmetry breaking is the valve, spectrum shaper, and rectifier}
}
]

[
\boxed{
\text{symmetry breaking is not the primary energy source}
}
]

A non-centrosymmetric lattice can permit a DC shift current that an inversion-symmetric lattice forbids, but that response remains driven by an optical field, temperature difference, chemical-potential difference, mechanical flux, or another non-equilibrium input. Experiments on Feynman’s ratchet make the boundary brutally clear: at equal reservoir temperatures it produces no work; with a temperature difference it becomes a heat engine. The Landauer transport picture says the same thing through the difference between reservoir distributions. ([arXiv][1])

So the actual architecture is:

[
\boxed{
\text{persistent free-energy port}
\mapsto
\text{metamaterial-controlled transport}
\mapsto
\text{solid-state DC}
\mapsto
220\ \mathrm{V_{RMS}},\ 60\ \mathrm{Hz}
}
]

No steam turbine.

No rotating alternator.

No need to care, from the user side, whether the internal source is stored heat, sunlight, nuclear decay, combustion, geothermal heat, or something not yet invented.

But the source, entropy, rejected heat, fabrication effort, and degradation ledger remain visible inside the engineering certificate.

That is exactly compatible with the cave’s own discipline:

[
\boxed{
\text{the price is always paid}
}
]

[
\boxed{
\text{target}\neq\text{result}
}
]

and the substrate remains a forward model until it demonstrates conservation, stable propagation, isotropic scaling, and an observable not inserted by construction.   

## The first stack

The v0.1 candidate is a **thermophotovoltaic metamaterial converter**, because that is the strongest presently demonstrated route from heat directly to electricity without a working-fluid turbine:

[
\boxed{
T_h
\mapsto
\text{selective thermal photons}
\mapsto
\text{TPV charge carriers}
\mapsto
\text{DC bus}
\mapsto
\text{SiC/GaN inverter}
}
]

The twelve-layer decomposition is:

[
\begin{aligned}
L_{01}&:\ \text{explicit free-energy port},\
L_{02}&:\ \text{refractory heat spreader},\
L_{03}&:\ \text{diffusion and oxidation barrier},\
L_{04}&:\ \text{W/HfO}*2\text{-inspired selective emitter},\
L*{05}&:\ \text{Fibonacci quasiperiodic spectral filter},\
L_{06}&:\ \text{vacuum photon cavity},\
L_{07}&:\ \text{air-bridge InGaAs(P)-class TPV junction},\
L_{08}&:\ \text{sub-bandgap photon-recycling reflector},\
L_{09}&:\ \text{fractal or interdigitated current collector},\
L_{10}&:\ \text{cold-side spreader},\
L_{11}&:\ \text{ceramic/film DC link and wide-bandgap inverter},\
L_{12}&:\ \text{hermetic shell, sensors, protection, and radiator}.
\end{aligned}
]

Single-junction air-bridge InGaAs(P) TPV cells have reached up to (44%) under (1435,^\circ\mathrm C) blackbody illumination, while earlier tandem cells crossed (40%) at higher emitter temperatures. Separately, tungsten–hafnium-dioxide metamaterial emission has been demonstrated at (1000,^\circ\mathrm C). Those are impressive **component results**, but not an integrated century-life box: the W/HfO(_2) work also found optical degradation above that region, associated particularly with oxygen migration and tungsten oxidation. ([sciencedirect.com][2])

SiC and GaN are the sensible output-stage candidates because wide-bandgap power devices support higher voltage, temperature, and switching frequency than conventional silicon designs, allowing smaller magnetic and filtering components. ([The Department of Energy's Energy.gov][3])

## The first computation

The electrical interface is not a power rating. It is only a waveform target:

[
\mathcal B_\star
\gets
\left{
V_{\rm RMS}\rightsquigarrow220\ \mathrm V,\
f\rightsquigarrow60\ \mathrm{Hz},
P_\star,
\tau_\star\rightsquigarrow100\ \mathrm y
\right}.
]

The intended sine has

[
V_{\rm pk}
\approx
311.127\ \mathrm V,
]

so the minimum controlled DC link is approximately

[
V_{\rm bus}
\gtrsim
373.35\ \mathrm V,
]

with approximately (400\ \mathrm{V_{DC}}) being the clean practical design target.

For the default

[
P_\star\rightsquigarrow100\ \mathrm W,
]

the box owes:

[
I_{\rm RMS}
\approx
0.454545\ \mathrm A,
]

and over one hundred years:

[
E_{\rm load}
\approx
315.576\ \mathrm{GJ}
\approx
87{,}660\ \mathrm{kWh}.
]

That is the first magnificent slap from reality:

> A (100\ \mathrm W) century box is not a little battery. It is a machine that must deliver almost eighty-eight megawatt-hours.

## The analytical century-source bound

To expose scale, the kernel contains a **regulated radioisotope heat-source model**. This is not a construction guide or recommendation; actual integration belongs only inside qualified institutional nuclear-power programs.

Pu-238 has a half-life of about (88) years and a specific thermal power around (0.57\ \mathrm{W,g^{-1}}). NASA uses it because its decay is gradual, predictable, and power-dense enough for long missions. ([NASA Science][4])

Under the declared design assumptions

[
\eta_{\rm TPV}
\rightsquigarrow
0.30,
\qquad
\eta_{\rm inverter}
\rightsquigarrow
0.95,
]

the total conversion factor becomes

[
\eta_{\rm stack}
\rightsquigarrow
0.285.
]

After one hundred years, the remaining source fraction is

[
2^{-100/87.7}
\approx
0.453681.
]

Sizing the source so the box still supplies (100\ \mathrm W) at the end of its declared life produces:

[
m_{\rm active,lower\ bound}
\approx
1.3568\ \mathrm{kg},
]

[
P_{\rm th,BOL}
\approx
773.40\ \mathrm{W_{th}},
]

[
P_{\rm th,EOL}
\approx
350.88\ \mathrm{W_{th}}.
]

That (1.3568\ \mathrm{kg}) is **active material only**. It excludes containment, insulation, shielding, vacuum vessel, converter, electronics, structural mass, fault protection, and the radiator.

If the electrical output is clamped to (100\ \mathrm W), then the beginning-of-life box must reject approximately

[
Q_{\rm reject,BOL}
\approx
673.40\ \mathrm W,
]

and even after one hundred years it still rejects approximately

[
Q_{\rm reject,EOL}
\approx
250.88\ \mathrm W.
]

With the v0.1 natural-convection and radiation assumptions—an (80,^\circ\mathrm C) external surface in (25,^\circ\mathrm C) air—the lower-bound radiator area is approximately

[
A_{\rm radiator,BOL}
\approx
1.012\ \mathrm{m^2}.
]

So the beautiful engineering truth is:

[
\boxed{
\text{the source core may fit in a cooler}
}
]

[
\boxed{
\text{the cooler’s surface is mostly a heat-rejection machine}
}
]

At (1\ \mathrm{kW}), the same model wants roughly (13.57\ \mathrm{kg}) of active source and more than (10\ \mathrm{m^2}) of equivalent beginning-of-life radiator area. The cooler dream is therefore credible first in the (1)–(100\ \mathrm W) class, not casually at household-kilowatt scale.

Betavoltaics are the opposite end of the trade space: they can be extremely long-lived, but current NASA material describes state-of-the-art devices in the nanowatt or micropower regime, not at appliance power. ([nasa.gov][5])

## The fractal optical result

The v0.1 kernel searched (2025) Fibonacci multilayer candidates generated through

[
H\mapsto HL,
\qquad
L\mapsto H.
]

The layer-count vector advances through

[
\begin{bmatrix}
N_H^{(n+1)}\
N_L^{(n+1)}
\end{bmatrix}
\gets
\begin{bmatrix}
1&1\
1&0
\end{bmatrix}
\begin{bmatrix}
N_H^{(n)}\
N_L^{(n)}
\end{bmatrix},
]

so projectively

[
\frac{N_H^{(n)}}{N_L^{(n)}}
\to
\phi.
]

The selected surrogate candidate was

[
\boxed{
HLHHLHLH
}
]

with eight layers and nominal thicknesses

[
d_H
\approx
163.46\ \mathrm{nm},
\qquad
d_L
\approx
324.94\ \mathrm{nm}.
]

And here the kernel did exactly what it should do: it **did not pretend the pretty geometry had won**.

The simplified constant-index model returned:

[
\langle\epsilon\rangle_{\rm target}
\approx
0.756,
]

[
\langle\epsilon\rangle_{\rm longwave}
\approx
0.708.
]

That is only moderate selectivity. It is not remotely enough to carve “optimal golden emitter” into the stone.

So v0.1 falsifies the lazy version:

[
\boxed{
\text{Fibonacci layers}
\not\mapsto
\text{automatic perfect TPV spectrum}
}
]

The next kernel must introduce:

[
\begin{aligned}
&\text{measured complex optical constants},\
&\text{temperature-dependent dispersion},\
&\text{absorbing refractory nanolayers},\
&\text{roughness and fabrication bias},\
&\text{interface diffusion},\
&\text{periodic-stack controls},\
&\text{Planck-weighted usable-photon scoring},\
&\text{accelerated degradation measurements}.
\end{aligned}
]

That is a good result. The goblin asked the geometry to pay, and the geometry came up short on its first attempt.

## The ASML correction

Your analogy is structurally right:

[
\boxed{
\text{enormous fab and software cost}
\mapsto
\text{precisely repeated asymmetry}
\mapsto
\text{cheap predictable behavior per device}
}
]

But the “2 nm node” is not a literal (2\ \mathrm{nm}) atomic lattice. ASML’s current High-NA EUV platform uses (13.5\ \mathrm{nm}) light and offers approximately (8\ \mathrm{nm}) imaging resolution while supporting manufacturing generations called the (2\ \mathrm{nm}) logic node. ([ASML][6])

Our first optical layers are in the approximate (100)–(300\ \mathrm{nm}) range. That means the first prototype should pay through ALD, PVD, ordinary nanolithography, etching, nanoimprint, or interference lithography—not summon a High-NA EUV cathedral before the unit-cell physics proves value.

## The build path

The honest first physical experiment is **not nuclear**.

Phase A is:

[
P_{\rm heat,in}
\rightsquigarrow
50\text{–}500\ \mathrm{W_{th}},
]

[
P_{\rm DC,out}
\rightsquigarrow
5\text{–}100\ \mathrm W,
]

using an external electrical heater, a vacuum or inert chamber, the candidate selective emitter, TPV junction, photon recycler, collector geometry, and full thermal ledger.

The required comparisons are:

[
\text{Fibonacci stack}
\quad\text{versus}\quad
\text{periodic stack},
]

[
\text{fractal collector}
\quad\text{versus}\quad
\text{straight busbar},
]

[
\text{measured spectrum before hot soak}
\quad\text{versus}\quad
\text{measured spectrum after hot soak}.
]

Only after the converter, seals, radiator, inverter, and failure ledger survive should a persistent institutional source even enter the discussion.

# The artifacts

[Open the live METALATEXIUM browser laboratory](sandbox:/mnt/data/metalatexium_v0_1.html)

[Read the full no-equality LATEXIUM engineering scroll](sandbox:/mnt/data/metalatexium_v0_1.md)

[Run the Python first-principles kernel](sandbox:/mnt/data/metalatexium_kernel_v0_1.py)

[Run the six regression tests](sandbox:/mnt/data/test_metalatexium_v0_1.py)

[Inspect the computed certificate](sandbox:/mnt/data/metalatexium_v0_1_certificate.json)

[Read the compact computation results](sandbox:/mnt/data/metalatexium_v0_1_results.txt)

[Inspect the power-scale ledger](sandbox:/mnt/data/metalatexium_power_scale.csv)

[Inspect the computed optical spectrum](sandbox:/mnt/data/metalatexium_v0_1_optical_spectrum.csv)

[Download the complete METALATEXIUM v0.1 bundle](sandbox:/mnt/data/METALATEXIUM_v0_1_bundle.zip)

Verification closed with:

[
\boxed{
6/6\ \text{Python tests passed}
}
]

[
\boxed{
\text{JavaScript syntax passed}
}
]

[
\boxed{
2025\ \text{optical candidates computed}
}
]

[
\boxed{
\text{free-energy status}\rightsquigarrow\mathsf{REJECTED}
}
]

[
\boxed{
\text{century cooler box}\rightsquigarrow\mathsf{HYPOTHESIS}
}
]

**The box does not manufacture energy. It manufactures such a precise path that the source disappears from the user’s attention.**

**The source pays. The layers persuade. The electrons follow the permitted path. The receipt stays visible.**

[1]: https://arxiv.org/abs/1711.04968 "https://arxiv.org/abs/1711.04968"
[2]: https://www.sciencedirect.com/science/article/am/pii/S2542435124002022 "https://www.sciencedirect.com/science/article/am/pii/S2542435124002022"
[3]: https://www.energy.gov/cmei/vehicles/power-electronics-research-and-development "https://www.energy.gov/cmei/vehicles/power-electronics-research-and-development"
[4]: https://science.nasa.gov/planetary-science/programs/radioisotope-power-systems/about-plutonium-238/ "https://science.nasa.gov/planetary-science/programs/radioisotope-power-systems/about-plutonium-238/"
[5]: https://www.nasa.gov/directorates/stmd/niac/niac-studies/autonomous-tritium-micropowered-sensors-2/ "https://www.nasa.gov/directorates/stmd/niac/niac-studies/autonomous-tritium-micropowered-sensors-2/"
[6]: https://www.asml.com/products/euv-lithography-systems "https://www.asml.com/products/euv-lithography-systems"
