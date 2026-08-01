#!/usr/bin/env python3
"""KIBOTOS-METALATEXIUM v1.2 -- THE BOX THAT PAYS, WELDED

Lineage (Path X -- every rung frozen, none overwritten):
  v1.0  KIBOTOS-100 scroll + kernels          (Fable)   -- the wall, the symmetry
        law, the phi^2-chirped mirror (worst-case R 0.9977 over its band).
  v0.1  METALATEXIUM -- THE BOX THAT PAYS     (Sol)     -- BoxSpec/ledger/decay
        bound, 12 anchors, 12-layer stack, Fibonacci emitter search,
        free_energy: REJECTED, self-hashing certificate.  6/6 tests, byte-exact
        reproduction, and the two-kernel mass lock (1.3560 vs 1.3568 kg)
        verified before this weld was written.
  v1.2  THIS FILE (Vlad + Sol + Fable)        -- the weld:
        (1) installs the phi^2-chirp mirror (on a metal floor) into Sol's open
            L08 photon-recycling slot;
        (2) replaces the temperature-free hand-weighted optical objective with
            a Planck-weighted CAVITY model at a declared emitter temperature;
        (3) DERIVES the conversion efficiency Sol assumed (0.30 converter),
            with controls (no mirror; bare metal; full weld);
        (4) re-aims the Fibonacci emitter search at the cavity figure of merit.

HONEST BOUNDARY (unchanged from both parents):
  Broken symmetry rectifies; only a paid free-energy gradient supplies.
  free_energy: REJECTED.  The 100-year integrated device is a HYPOTHESIS.
  All optical constants are fixed surrogates; the cavity model is first-order
  (view factor 1, single-pass parasitic accounting, reflected sub-gap photons
  returned to the emitter).  This is an engineering bound, not a build permit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

VERSION = "1.2"
ARTIFACT = "KIBOTOS-METALATEXIUM -- THE BOX THAT PAYS, WELDED"

SECONDS_PER_YEAR = 365.25 * 24.0 * 3600.0
SIGMA_SB = 5.670374419e-8
HC_EV_UM = 1.239841984
PHI = (1.0 + math.sqrt(5.0)) / 2.0
C1_W_M2 = 3.741771852e-16      # 2*pi*h*c^2  [W m^2]
C2_M_K = 1.438776877e-2        # h*c/k       [m K]

EXPECTED_PARENTS = {
    "sol_kernel_v0_1_sha256": "4c5e665877a8391d8c1652877a5eaee2428abef3c6496a45b8f2a8de0d84ee0c",
    "sol_certificate_file_sha256": "e388d796aadc95d23e1f1904b8e269156cf2ec3c1aa9e9f58920e78ce84f0a13",
    "sol_certificate_embedded_sha256": "c5f79b74a65ee783afc711fd72642753eae57d158e36a9e183d5919ef14e6acb",
}
# Curse 38: portable -- find the frozen v1.0 scroll relatively (sibling, then the
# kibotos/ parent where it lives in the cave), first hit wins; else absent-at-build.
def _find_v1_0_scroll():
    here = Path(__file__).resolve().parent
    for c in (here / "kibotos_100_scroll_v1_0.html",
              here.parent / "kibotos_100_scroll_v1_0.html"):
        if c.exists():
            return c
    return here / "kibotos_100_scroll_v1_0.html"
FABLE_V1_0_SCROLL = _find_v1_0_scroll()


# ------------------------------------------------------------------ box (Sol)
@dataclass(frozen=True)
class BoxSpec:
    output_power_w: float = 100.0
    output_voltage_rms_v: float = 220.0
    output_frequency_hz: float = 60.0
    power_factor: float = 1.0
    service_years: float = 100.0
    converter_efficiency: float = 0.30
    inverter_efficiency: float = 0.95
    source_half_life_years: float = 87.7
    source_specific_thermal_power_w_per_g: float = 0.57
    radiator_surface_c: float = 80.0
    ambient_c: float = 25.0
    radiator_emissivity: float = 0.90
    natural_convection_w_m2k: float = 5.0
    dc_bus_headroom: float = 1.20


def lifetime_energy(spec: BoxSpec) -> dict[str, float]:
    seconds = spec.service_years * SECONDS_PER_YEAR
    energy_j = spec.output_power_w * seconds
    current_rms = spec.output_power_w / (spec.output_voltage_rms_v * spec.power_factor)
    voltage_peak = math.sqrt(2.0) * spec.output_voltage_rms_v
    return {
        "service_seconds": seconds,
        "load_energy_j": energy_j,
        "load_energy_kwh": spec.output_power_w * spec.service_years * 365.25 * 24.0 / 1000.0,
        "output_current_rms_a": current_rms,
        "output_voltage_peak_v": voltage_peak,
        "minimum_dc_bus_target_v": spec.dc_bus_headroom * voltage_peak,
    }


def decay_factor(years: float, half_life_years: float) -> float:
    return 2.0 ** (-years / half_life_years)


def heat_rejection_flux_w_m2(spec: BoxSpec) -> float:
    ts = spec.radiator_surface_c + 273.15
    ta = spec.ambient_c + 273.15
    return spec.radiator_emissivity * SIGMA_SB * (ts**4 - ta**4) + spec.natural_convection_w_m2k * (ts - ta)


def long_life_source_bound(spec: BoxSpec) -> dict[str, float]:
    eta_total = spec.converter_efficiency * spec.inverter_efficiency
    end_decay = decay_factor(spec.service_years, spec.source_half_life_years)
    eol_thermal = spec.output_power_w / eta_total
    bol_thermal = eol_thermal / end_decay
    mass_g = bol_thermal / spec.source_specific_thermal_power_w_per_g
    flux = heat_rejection_flux_w_m2(spec)
    return {
        "total_conversion_efficiency": eta_total,
        "end_of_life_decay_fraction": end_decay,
        "beginning_thermal_power_w": bol_thermal,
        "end_thermal_power_w": eol_thermal,
        "analytical_source_mass_g": mass_g,
        "analytical_source_mass_kg": mass_g / 1000.0,
        "beginning_rejected_heat_if_output_clamped_w": bol_thermal - spec.output_power_w,
        "end_rejected_heat_w": eol_thermal - spec.output_power_w,
        "radiator_flux_at_design_temperature_w_m2": flux,
        "radiator_area_bol_m2": (bol_thermal - spec.output_power_w) / flux,
        "radiator_area_eol_m2": (eol_thermal - spec.output_power_w) / flux,
    }


# ------------------------------------------------------ optics (shared TMM)
@dataclass(frozen=True)
class OpticalSpec:
    bandgap_ev: float = 0.74
    order_min: int = 3
    order_max: int = 11
    thickness_scale_min: float = 0.72
    thickness_scale_max: float = 1.28
    thickness_scale_steps: int = 15
    n_high: complex = 2.05 + 0.0j          # emitter-side H (HfO2-like)
    n_low: complex = 1.65 + 0.0j           # emitter-side L (Al2O3-like)
    n_substrate: complex = 3.50 + 2.70j    # tungsten-like emitter body
    n_incident: complex = 1.0 + 0.0j
    # mirror side (Fable v1.0, retuned to the 0.74 eV gap):
    mirror_n_high: complex = 3.42 + 0.0j   # Si-like
    mirror_n_low: complex = 1.45 + 0.0j    # SiO2-like
    mirror_n_metal: complex = 0.80 + 12.0j # gold-like floor
    mirror_lambda_min_um: float = 1.71     # band [L, L*phi^2] hugs the gap
    mirror_pairs: int = 17
    emitter_temperature_k: float = 1300.0


def fibonacci_word(order: int) -> str:
    word = "H"
    for _ in range(order):
        word = "".join("HL" if ch == "H" else "H" for ch in word)
    return word


def fibonacci_counts(order: int) -> tuple[int, int, int]:
    w = fibonacci_word(order)
    return w.count("H"), w.count("L"), len(w)


def _stack_matrix(layers: list[tuple[complex, float]], lam_um: np.ndarray) -> np.ndarray:
    m = np.broadcast_to(np.eye(2, dtype=np.complex128), (len(lam_um), 2, 2)).copy()
    for n, d in layers:
        delta = 2.0 * np.pi * n * d / lam_um
        c, s = np.cos(delta), np.sin(delta)
        layer = np.empty((len(lam_um), 2, 2), dtype=np.complex128)
        layer[:, 0, 0] = c
        layer[:, 0, 1] = 1j * s / n
        layer[:, 1, 0] = 1j * n * s
        layer[:, 1, 1] = c
        m = np.einsum("nij,njk->nik", m, layer)
    return m


def stack_reflectance(layers: list[tuple[complex, float]], lam_um: np.ndarray,
                      n_sub: complex, n_inc: complex = 1.0 + 0.0j) -> np.ndarray:
    m = _stack_matrix(layers, lam_um)
    a, b, c, d = m[:, 0, 0], m[:, 0, 1], m[:, 1, 0], m[:, 1, 1]
    y_in = (c + d * n_sub) / (a + b * n_sub)
    r = (n_inc - y_in) / (n_inc + y_in)
    return np.clip(np.abs(r) ** 2, 0.0, 1.0)


def emitter_layers(word: str, lambda_g_um: float, sh: float, sl: float, spec: OpticalSpec) -> list[tuple[complex, float]]:
    d_h = sh * lambda_g_um / (4.0 * spec.n_high.real)
    d_l = sl * lambda_g_um / (4.0 * spec.n_low.real)
    return [(spec.n_high, d_h) if ch == "H" else (spec.n_low, d_l) for ch in word]


def emitter_emissivity(word: str, lam_um: np.ndarray, lambda_g_um: float,
                       sh: float, sl: float, spec: OpticalSpec) -> np.ndarray:
    return 1.0 - stack_reflectance(emitter_layers(word, lambda_g_um, sh, sl, spec), lam_um, spec.n_substrate)


def mirror_layers(spec: OpticalSpec) -> list[tuple[complex, float]]:
    lays: list[tuple[complex, float]] = []
    for j in range(spec.mirror_pairs):
        lj = spec.mirror_lambda_min_um * PHI ** (2.0 * j / (spec.mirror_pairs - 1))
        lays.append((spec.mirror_n_high, lj / (4.0 * spec.mirror_n_high.real)))
        lays.append((spec.mirror_n_low, lj / (4.0 * spec.mirror_n_low.real)))
    return lays


def mirror_reflectance(lam_um: np.ndarray, spec: OpticalSpec) -> np.ndarray:
    return stack_reflectance(mirror_layers(spec), lam_um, spec.mirror_n_metal)


def bare_metal_reflectance(lam_um: np.ndarray, spec: OpticalSpec) -> np.ndarray:
    return stack_reflectance([], lam_um, spec.mirror_n_metal)


# ------------------------------------------------------------- cavity (v1.2)
def planck_spectral_w_m2_um(lam_um: np.ndarray, t_k: float) -> np.ndarray:
    lam_m = lam_um * 1e-6
    return (C1_W_M2 / lam_m**5 / np.expm1(C2_M_K / (lam_m * t_k))) * 1e-6


def cavity_grid() -> np.ndarray:
    return np.concatenate([np.linspace(0.5, 6.0, 500, endpoint=False), np.linspace(6.0, 25.0, 220)])


def cavity_metrics(eps_e: np.ndarray, r_mirror: np.ndarray, lam_um: np.ndarray,
                   lambda_g_um: float, t_k: float) -> dict[str, float]:
    """First-order spectral bookkeeping [COMPUTED under surrogate]:
    useful    ~ in-band emitted power (absorbed by the cell),
    parasitic ~ out-band emitted power NOT returned by the mirror,
    recycled  ~ out-band emitted power the mirror sends home.
    eta_spectral ~ useful / (useful + parasitic)."""
    b = planck_spectral_w_m2_um(lam_um, t_k)
    inband = lam_um < lambda_g_um
    useful = float(np.trapezoid((eps_e * b)[inband], lam_um[inband]))
    out = ~inband
    emitted_out = float(np.trapezoid((eps_e * b)[out], lam_um[out]))
    parasitic = float(np.trapezoid((eps_e * b * (1.0 - r_mirror))[out], lam_um[out]))
    eta = useful / (useful + parasitic) if useful + parasitic > 0 else 0.0
    return {
        "useful_w_m2": useful,
        "outband_emitted_w_m2": emitted_out,
        "parasitic_w_m2": parasitic,
        "recycled_w_m2": emitted_out - parasitic,
        "eta_spectral": eta,
        "fom_w_m2": useful * eta,
    }


def derived_chain(eta_spectral: float, eta_cell: float, eta_inverter: float = 0.95) -> float:
    return eta_spectral * eta_cell * eta_inverter


# --------------------------------------------------- re-aimed search (v1.2)
def search_fibonacci_emitter_cavity(spec: OpticalSpec) -> dict[str, Any]:
    lambda_g = HC_EV_UM / spec.bandgap_ev
    lam = cavity_grid()
    r_m = mirror_reflectance(lam, spec)
    scales = np.linspace(spec.thickness_scale_min, spec.thickness_scale_max, spec.thickness_scale_steps)
    best: dict[str, Any] | None = None
    count = 0
    sol_row: dict[str, Any] | None = None
    all_fom: list[float] = []
    for order in range(spec.order_min, spec.order_max + 1):
        word = fibonacci_word(order)
        for sh in scales:
            for sl in scales:
                eps = emitter_emissivity(word, lam, lambda_g, float(sh), float(sl), spec)
                met = cavity_metrics(eps, r_m, lam, lambda_g, spec.emitter_temperature_k)
                all_fom.append(met["fom_w_m2"])
                count += 1
                row = {"order": order, "word": word, "layers": len(word),
                       "scale_high": float(sh), "scale_low": float(sl), **met}
                if best is None or row["fom_w_m2"] > best["fom_w_m2"]:
                    best = row
                if order == 4 and abs(sh - 0.80) < 1e-9 and abs(sl - 1.28) < 1e-9:
                    sol_row = row
    assert best is not None and sol_row is not None
    beats_sol = int(sum(1 for f in all_fom if f > sol_row["fom_w_m2"]))
    return {"candidate_count": count, "best": best, "sol_v0_1_winner_under_cavity": sol_row,
            "candidates_beating_sol_winner": beats_sol, "lambda_g_um": lambda_g}


# ----------------------------------------------------------- anchors & stack
def twelve_anchor_constraints() -> list[dict[str, str]]:
    return [
        {"id": "A01", "name": "Energy ledger", "criterion": "source power must cover electrical output, rejected heat, storage change, and auxiliaries"},
        {"id": "A02", "name": "Non-equilibrium port", "criterion": "a maintained temperature, photon, chemical, mechanical, or nuclear free-energy gradient is mandatory"},
        {"id": "A03", "name": "Charge continuity", "criterion": "no persistent charge accumulation outside specified capacitive states"},
        {"id": "A04", "name": "Electrical stress", "criterion": "creepage, clearance, insulation, field crowding, and switching transients remain below certified limits"},
        {"id": "A05", "name": "Heat rejection", "criterion": "all non-converted input plus electronics loss reaches the environment under worst-case ambient conditions"},
        {"id": "A06", "name": "Hot-stack stability", "criterion": "oxidation, interdiffusion, agglomeration, phase drift, and thermal expansion remain bounded"},
        {"id": "A07", "name": "Cold-cell stability", "criterion": "TPV junction temperature, dark current, contacts, and photon-recycling surfaces remain within tested limits"},
        {"id": "A08", "name": "Radiation compatibility", "criterion": "displacement damage, ionization, contamination, and source containment are institutionally certified when applicable"},
        {"id": "A09", "name": "Current-density life", "criterion": "electromigration, contact heating, and cyclic fatigue remain below lifetime damage budgets"},
        {"id": "A10", "name": "Hermeticity", "criterion": "vacuum or inert atmosphere, getters, seals, feedthroughs, and corrosion barriers survive the declared life"},
        {"id": "A11", "name": "Power quality and protection", "criterion": "220 V RMS output remains within harmonic, isolation, overcurrent, ground-fault, and safe-shutdown limits"},
        {"id": "A12", "name": "Receipt and manufacturability", "criterion": "every layer, process window, measurement, uncertainty, and failure test is traceable and reproducible"},
    ]


def twelve_candidate_layers() -> list[dict[str, str]]:
    layers = [
        {"id": "L01", "layer": "Primary free-energy port", "candidate": "external heater for Phase A; regulated isotope heat only as an institutional Phase C option", "status": "SOURCE"},
        {"id": "L02", "layer": "Refractory heat spreader", "candidate": "SiC, graphite composite, molybdenum, or tungsten candidate after compatibility testing", "status": "DESIGN"},
        {"id": "L03", "layer": "Diffusion and oxidation barrier", "candidate": "ALD ceramic or refractory nitride candidate selected by hot-soak testing", "status": "DESIGN"},
        {"id": "L04", "layer": "Selective emitter", "candidate": "W/HfO2-inspired refractory multilayer or photonic-crystal emitter", "status": "RESEARCH"},
        {"id": "L05", "layer": "Fibonacci spectral filter", "candidate": "H/L quasiperiodic sequence, objective now CAVITY-COUPLED at declared T_e", "status": "COMPUTED (v1.2 re-aim)"},
        {"id": "L06", "layer": "Photon cavity", "candidate": "vacuum or controlled low-index gap with view-factor management", "status": "DESIGN"},
        {"id": "L07", "layer": "TPV junction", "candidate": "air-bridge InGaAs(P)-class junction matched to emitter spectrum", "status": "RESEARCH"},
        {"id": "L08", "layer": "Photon-recycling reflector", "candidate": "phi^2-chirped Si/SiO2 stack on gold-like floor (Fable v1.0, retuned)", "status": "COMPUTED (v1.2 weld)"},
        {"id": "L09", "layer": "Fractal current collector", "candidate": "interdigitated or space-filling electrode compared against a straight-busbar control", "status": "HYPOTHESIS"},
        {"id": "L10", "layer": "Cold-side heat spreader", "candidate": "AlN, SiC, graphite, or diamond-composite candidate", "status": "DESIGN"},
        {"id": "L11", "layer": "DC conditioning and inverter", "candidate": "ceramic/film DC link plus SiC or GaN switching bridge and LC output filter", "status": "ENGINEERING"},
        {"id": "L12", "layer": "Hermetic shell and radiator", "candidate": "welded enclosure, getters, redundant sensing, passive fins, and service-isolated output", "status": "ENGINEERING"},
    ]
    return layers


# ---------------------------------------------------------------- certificate
def lineage_report() -> dict[str, str]:
    rep = dict(EXPECTED_PARENTS)
    if FABLE_V1_0_SCROLL.exists():
        rep["fable_v1_0_scroll_sha256"] = hashlib.sha256(FABLE_V1_0_SCROLL.read_bytes()).hexdigest()
    else:
        rep["fable_v1_0_scroll_sha256"] = "absent-at-build"
    return rep


def make_certificate(box_center: BoxSpec, spec: OpticalSpec, weld: dict[str, Any]) -> dict[str, Any]:
    # Curse 38: the SEALED payload is the MATH only -- deterministic, so a stranger
    # on any machine reproduces the same sha256. The wall-clock and the build
    # environment are attached AFTER, as peers the hash does not cover.
    payload = {
        "artifact": ARTIFACT,
        "version": VERSION,
        "status": {
            "energy_ledger": "EXACT ARITHMETIC UNDER DECLARED INPUTS",
            "decay_source": "ANALYTICAL LOWER-BOUND MODEL",
            "mirror_and_cavity": "COMPUTED UNDER FIXED SURROGATE OPTICS, FIRST-ORDER CAVITY",
            "cell_chain": "ESTABLISHED LAB RANGE (0.30-0.40 on absorbed in-band), NOT CENTURY-QUALIFIED",
            "hundred_year_box": "HYPOTHESIS -- NOT DEMONSTRATED",
            "free_energy": "REJECTED",
        },
        "lineage": lineage_report(),
        "box_spec_center_chain": asdict(box_center),
        "energy": lifetime_energy(box_center),
        "source_bound_center_chain": long_life_source_bound(box_center),
        "weld": weld,
        "anchors": twelve_anchor_constraints(),
        "stack": twelve_candidate_layers(),
    }
    stable = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    payload["sha256"] = hashlib.sha256(stable).hexdigest()
    # non-reproducible metadata: recorded, never hashed.
    payload["generated_utc"] = datetime.now(timezone.utc).isoformat()
    payload["environment"] = {"python": sys.version, "platform": platform.platform(), "numpy": np.__version__}
    return payload


# ----------------------------------------------------------------------- main
_WELD_CACHE: dict[str, Any] | None = None


def run_weld(spec: OpticalSpec | None = None) -> dict[str, Any]:
    global _WELD_CACHE
    default = spec is None
    if default and _WELD_CACHE is not None:
        return _WELD_CACHE
    spec = spec or OpticalSpec()
    lam = cavity_grid()
    lambda_g = HC_EV_UM / spec.bandgap_ev
    t_e = spec.emitter_temperature_k
    r_weld = mirror_reflectance(lam, spec)
    r_metal = bare_metal_reflectance(lam, spec)
    r_none = np.zeros_like(lam)
    sub = lam >= lambda_g
    r_sub = r_weld[sub]
    lam_sub = lam[sub]
    b_sub = planck_spectral_w_m2_um(lam_sub, t_e)
    seg = 0.5 * (b_sub[1:] + b_sub[:-1]) * np.diff(lam_sub)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    cum = cum / cum[-1]
    lam90 = float(lam_sub[np.searchsorted(cum, 0.90)])
    band90 = lam_sub <= lam90
    i_notch = int(np.argmin(r_sub))
    mirror_stats = {
        "band_um": [spec.mirror_lambda_min_um, spec.mirror_lambda_min_um * PHI * PHI],
        "planck_weighted_subgap_R": float(np.trapezoid(r_sub * b_sub, lam_sub) / np.trapezoid(b_sub, lam_sub)),
        "power90_wavelength_um": lam90,
        "worst_R_in_power90_band": float(np.min(r_sub[band90])),
        "subgap_worst_R_absolute": float(np.min(r_sub)),
        "far_ir_ar_notch_um": float(lam_sub[i_notch]),
        "subgap_mean_R": float(np.mean(r_sub)),
        "metal_floor_R_at_10um": float(bare_metal_reflectance(np.array([10.0]), spec)[0]),
        "note": "far-IR AR notch: at long wavelengths the dielectric stack acts as a weak anti-reflection film on the metal; the cavity integral already includes it. The Planck-weighted R is the physical spec.",
    }
    eps_gray = np.full_like(lam, 0.90)
    eps_sol = emitter_emissivity("HLHHLHLH", lam, lambda_g, 0.80, 1.28, spec)
    eps_bare_w = emitter_emissivity("", lam, lambda_g, 1.0, 1.0, spec)
    cases = {}
    for ename, eps in (("gray_0.90", eps_gray), ("sol_v0_1_best_stack", eps_sol), ("bare_tungsten_surrogate", eps_bare_w)):
        for mname, r in (("no_mirror", r_none), ("bare_metal_only", r_metal), ("weld_phi2_chirp", r_weld)):
            cases[f"{ename}|{mname}"] = cavity_metrics(eps, r, lam, lambda_g, t_e)
    search = search_fibonacci_emitter_cavity(spec)
    eta_sp = cases["gray_0.90|weld_phi2_chirp"]["eta_spectral"]
    chain = {f"eta_cell_{ec:.2f}": derived_chain(eta_sp, ec) for ec in (0.30, 0.35, 0.40)}
    boxes = {}
    for ec in (0.30, 0.35, 0.40):
        b = BoxSpec(converter_efficiency=eta_sp * ec)
        boxes[f"eta_cell_{ec:.2f}"] = {"eta_total": derived_chain(eta_sp, ec),
                                       "source_mass_kg": long_life_source_bound(b)["analytical_source_mass_kg"]}
    result = {"emitter_temperature_k": t_e, "lambda_g_um": lambda_g, "mirror": mirror_stats,
              "cavity_cases": cases, "reaimed_search": search,
              "derived_chain_gray_weld": chain, "boxes_at_derived_eta": boxes,
              "sol_assumed_total_efficiency": 0.285}
    if default:
        _WELD_CACHE = result
    return result


def human_results(cert: dict[str, Any]) -> str:
    w = cert["weld"]
    m = w["mirror"]
    cc = w["cavity_cases"]
    ch = w["derived_chain_gray_weld"]
    bx = w["boxes_at_derived_eta"]
    s = w["reaimed_search"]
    lines = [
        f"{ARTIFACT} v{VERSION}",
        "",
        "HONEST BOUNDARY  (both parents, preserved)",
        "  Broken symmetry rectifies; only a paid gradient supplies. free_energy: REJECTED.",
        "  Century device: HYPOTHESIS. All optics are fixed surrogates; cavity is first-order.",
        "",
        f"THE MIRROR (L08 filled)   band [{m['band_um'][0]:.2f}, {m['band_um'][1]:.3f}] um (span phi^2) on gold-like floor",
        f"  Planck-weighted sub-gap R (the physical spec)   {m['planck_weighted_subgap_R']:.4f}",
        f"  worst R in the 90%-power band (<= {m['power90_wavelength_um']:.2f} um)     {m['worst_R_in_power90_band']:.4f}",
        f"  absolute worst R {m['subgap_worst_R_absolute']:.4f} at {m['far_ir_ar_notch_um']:.1f} um -- documented far-IR AR",
        "  notch (stack-on-metal); the cavity integral already includes it.",
        "",
        f"THE CAVITY at T_e = {w['emitter_temperature_k']:.0f} K, gap {w['lambda_g_um']:.4f} um  (gray 0.90 emitter)",
        f"  eta_spectral, NO mirror       {cc['gray_0.90|no_mirror']['eta_spectral']:.4f}   <- the damning control",
        f"  eta_spectral, bare metal only {cc['gray_0.90|bare_metal_only']['eta_spectral']:.4f}",
        f"  eta_spectral, THE WELD        {cc['gray_0.90|weld_phi2_chirp']['eta_spectral']:.4f}",
        "",
        "ASSUMED -> DERIVED  (eta_total = eta_spectral x eta_cell x 0.95 inverter)",
        f"  eta_cell 0.30 -> eta_total {ch['eta_cell_0.30']:.4f}   mass {bx['eta_cell_0.30']['source_mass_kg']:.3f} kg",
        f"  eta_cell 0.35 -> eta_total {ch['eta_cell_0.35']:.4f}   mass {bx['eta_cell_0.35']['source_mass_kg']:.3f} kg",
        f"  eta_cell 0.40 -> eta_total {ch['eta_cell_0.40']:.4f}   mass {bx['eta_cell_0.40']['source_mass_kg']:.3f} kg",
        f"  Sol v0.1 ASSUMED 0.285 total -- now sits inside the DERIVED band.",
        "",
        f"RE-AIMED FIBONACCI SEARCH  ({s['candidate_count']} candidates, cavity figure of merit)",
        f"  new best: order {s['best']['order']}, word {s['best']['word'][:21]}{'...' if len(s['best']['word'])>21 else ''},",
        f"            layers {s['best']['layers']}, scales H/L {s['best']['scale_high']:.2f}/{s['best']['scale_low']:.2f}",
        f"            eta_spectral {s['best']['eta_spectral']:.4f}, FOM {s['best']['fom_w_m2']:.1f} W/m^2",
        f"  Sol's v0.1 winner under the cavity objective: FOM {s['sol_v0_1_winner_under_cavity']['fom_w_m2']:.1f} W/m^2,",
        f"            beaten by {s['candidates_beating_sol_winner']} of {s['candidate_count']} candidates.",
        "",
        f"SHA256  {cert['sha256']}",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="KIBOTOS-METALATEXIUM v1.2 -- the box that pays, welded")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent,
                    help="output directory (default: beside this file). Curse 38: portable path.")
    args = ap.parse_args()
    weld = run_weld()
    eta_sp = weld["cavity_cases"]["gray_0.90|weld_phi2_chirp"]["eta_spectral"]
    box_center = BoxSpec(converter_efficiency=eta_sp * 0.35)
    cert = make_certificate(box_center, OpticalSpec(), weld)
    out = args.out; out.mkdir(parents=True, exist_ok=True)
    (out / "kibotos_metalatexium_v1_2_certificate.json").write_text(
        json.dumps(cert, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    (out / "kibotos_metalatexium_v1_2_results.txt").write_text(human_results(cert), encoding="utf-8")
    lam = cavity_grid()
    spec = OpticalSpec()
    r = mirror_reflectance(lam, spec)
    eps = emitter_emissivity("HLHHLHLH", lam, HC_EV_UM / spec.bandgap_ev, 0.80, 1.28, spec)
    b = planck_spectral_w_m2_um(lam, spec.emitter_temperature_k)
    with (out / "kibotos_metalatexium_v1_2_cavity_spectrum.csv").open("w", encoding="utf-8") as f:
        f.write("wavelength_um,mirror_reflectance,sol_best_emitter_emissivity,planck_1300K_w_m2_um\n")
        for i in range(len(lam)):
            f.write(f"{lam[i]:.6g},{r[i]:.8g},{eps[i]:.8g},{b[i]:.8g}\n")
    print(human_results(cert), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
