#!/usr/bin/env python3
"""KIBOTOS-100 energy ledger -- the bookkeeping wall.
Spec: sealed box, ~cooler size (~100 L), electrical output for T = 100 years,
no refuel, no moving parts. What sources are ARITHMETICALLY allowed?"""
import math

YR = 365.25*24*3600.0
T = 100*YR

print("="*78)
print("PART A -- THE WALL: total energy for 100 years of continuous output")
print("="*78)
for Pe in (1.0, 100.0, 1000.0):
    E = Pe*T
    print(f"  P_e = {Pe:7.0f} W  ->  E_total = {E:.3e} J  = {E/3.6e6:.3e} kWh")

print()
print("PART B -- CHEMISTRY EXCLUDED [EXACT arithmetic]")
e_chem = 50e6   # J/kg, generous (diesel ~45.6, H2 ~120 but needs O2 + tanks)
for Pe in (100.0, 1000.0):
    m = Pe*T/e_chem
    print(f"  P_e={Pe:6.0f} W for 100 yr at 50 MJ/kg  ->  m >= {m:,.0f} kg  ({m/1000:,.1f} t)")
print("  A ~100 L / ~200 kg cooler at chemical density: 200kg*50MJ/kg = 1e10 J")
print(f"  -> {1e10/T:.2f} W continuous for a century. Chemistry is out by ~10^3.")
print("  Nuclear binding (~10^6 x chemical) is the ONLY admitted source. [EXACT]")

print()
print("PART C -- THE DECAY SOURCE LEDGER [COMPUTED from t_half + mean decay energy]")
print("  P(t) ~ P0 * 2^(-t/th);  BOL mass sized so EOL(100yr) electrical >= target")
# isotope: (specific power W/g fresh, half-life yr, note)
iso = {
 "Pu-238":(0.567, 87.7,  "RTG flight heritage (Voyager, MMRTG)"),
 "Am-241":(0.1146, 432.6,"ESA century-flat candidate"),
 "Sr-90 ":(0.916, 28.8,  "cheap, hot, short-lived (Soviet RTGs)"),
 "Ni-63 ":(0.0058, 101.2,"betavoltaic; t_half ~ THE SPEC"),
 "H-3   ":(0.326, 12.32, "tritium betavoltaic (City Labs)"),
 "C-14  ":(0.0013, 5730., "diamond battery; millennium tier"),
}
print(f"  {'isotope':8} {'W/g':>7} {'t_half yr':>10} {'2^(T/th)':>9}  note")
for k,(p0,th,note) in iso.items():
    print(f"  {k:8} {p0:7.4f} {th:10.1f} {2**(100/th):9.3f}  {note}")

print()
print("PART D -- DESIGN POINTS: EOL 100 W_e after 100 yr, two converter chains")
print("  chain 1: thermoelectric eta ~ 0.06  [ESTABLISHED, 48 yr flight proof]")
print("  chain 2: TPV-at-RTG-temp eta ~ 0.15 [frontier lab, HYPOTHESIS at century]")
for eta,tag in ((0.06,"TE 6%"),(0.15,"TPV 15%")):
    print(f"  -- eta ~ {eta:.2f} ({tag}): need P_th(EOL) ~ {100/eta:7.1f} W")
    for k in ("Pu-238","Am-241","Sr-90 "):
        p0,th,_ = iso[k]
        Pth_bol = (100/eta)*2**(100/th)
        m = Pth_bol/p0/1000.0
        print(f"       {k}: BOL thermal ~ {Pth_bol:8.1f} W  ->  mass ~ {m:6.2f} kg")
print("  supply wall [ESTABLISHED]: Pu-238 world production ~1.5 kg/yr (NASA);")
print("  Am-241 separable stocks kg-scale. The isotope ledger, not physics,")
print("  is why Earth still boils water at the GW scale.")

print()
print("PART E -- THE SMALL TIERS [COMPUTED raw / ESTABLISHED delivered]")
p0,th,_ = iso["Ni-63 "]
print(f"  Ni-63 raw decay power {p0*1e3:.1f} mW/g; betavoltaic eta ~ 2-8 % =>")
print(f"  ~0.1-0.5 mW_e/g. One WATT_e needs ~2-10 kg Ni-63: supply-absurd.")
print("  Honest tier: uW..mW for 20-100 yr (sensors, pacemakers, dust). [ESTABLISHED]")
print(f"  C-14 raw {iso['C-14  '][0]*1e3:.1f} mW/g, delivered nW-uW: the 5,000-year clock.")

print()
print("PART F -- EXISTENCE PROOFS [ESTABLISHED]")
print("  Voyager 1/2: Pu-238 + SiGe thermocouples, zero moving parts, launched")
print("  1977, still transmitting 2026: 48+ years. The box half-exists.")
print("  KRUSTY/Kilopower 2018: 1-10 kW_e fission demo (Stirling: moving parts).")
print("  Record TPV 40% (Nature 604, 2022) at ~2000-2400 C emitter;")
print("  the enabling trick: a >93%-reflective back mirror recycling sub-gap")
print("  photons -- i.e. THE PHOTON-MANAGEMENT STACK IS THE WHOLE GAME.")
