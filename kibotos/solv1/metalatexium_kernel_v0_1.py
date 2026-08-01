#!/usr/bin/env python3
"""METALATEXIUM v0.1 -- THE BOX THAT PAYS

A source-agnostic, first-principles engineering kernel for a long-lived
solid-state heat-to-electric power box.  The kernel does NOT claim free energy.
It keeps four objects separate:

  source -> converter -> power conditioner -> rejected heat

The default long-life source model uses published Pu-238 decay parameters only
as an analytical bound.  It is not a fabrication guide and not a recommendation.
Radioisotope systems are regulated and require qualified institutions.

The optical search is an illustrative transfer-matrix model using fixed surrogate
optical constants.  It ranks Fibonacci multilayers; it is not a materials
certificate and cannot establish 100-year stability.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np

VERSION = "0.1"
ARTIFACT = "METALATEXIUM -- THE BOX THAT PAYS"

SECONDS_PER_YEAR = 365.25 * 24.0 * 3600.0
HOURS_PER_YEAR = 365.25 * 24.0
SIGMA_SB = 5.670374419e-8  # W m^-2 K^-4
HC_EV_UM = 1.239841984  # eV um


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


@dataclass(frozen=True)
class OpticalSpec:
    bandgap_ev: float = 0.74
    order_min: int = 3
    order_max: int = 11
    thickness_scale_min: float = 0.72
    thickness_scale_max: float = 1.28
    thickness_scale_steps: int = 15
    layer_penalty: float = 0.0020
    n_high: complex = 2.05 + 0.0j  # HfO2-like surrogate
    n_low: complex = 1.65 + 0.0j  # Al2O3-like surrogate
    n_substrate: complex = 3.50 + 2.70j  # tungsten-like surrogate
    n_incident: complex = 1.0 + 0.0j


def _require_positive(name: str, value: float) -> None:
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive; received {value!r}")


def _require_fraction(name: str, value: float) -> None:
    if not math.isfinite(value) or not (0.0 < value <= 1.0):
        raise ValueError(f"{name} must lie in (0, 1]; received {value!r}")


def validate_box_spec(spec: BoxSpec) -> None:
    for name in (
        "output_power_w",
        "output_voltage_rms_v",
        "output_frequency_hz",
        "service_years",
        "source_half_life_years",
        "source_specific_thermal_power_w_per_g",
    ):
        _require_positive(name, float(getattr(spec, name)))
    for name in ("power_factor", "converter_efficiency", "inverter_efficiency", "radiator_emissivity"):
        _require_fraction(name, float(getattr(spec, name)))
    if spec.radiator_surface_c <= spec.ambient_c:
        raise ValueError("radiator_surface_c must exceed ambient_c")
    if spec.natural_convection_w_m2k < 0:
        raise ValueError("natural_convection_w_m2k cannot be negative")
    if spec.dc_bus_headroom < 1.0:
        raise ValueError("dc_bus_headroom must be at least one")


def lifetime_energy(spec: BoxSpec) -> dict[str, float]:
    validate_box_spec(spec)
    seconds = spec.service_years * SECONDS_PER_YEAR
    hours = spec.service_years * HOURS_PER_YEAR
    energy_j = spec.output_power_w * seconds
    energy_kwh = spec.output_power_w * hours / 1000.0
    current_rms = spec.output_power_w / (spec.output_voltage_rms_v * spec.power_factor)
    voltage_peak = math.sqrt(2.0) * spec.output_voltage_rms_v
    dc_bus_target = spec.dc_bus_headroom * voltage_peak
    return {
        "service_seconds": seconds,
        "service_hours": hours,
        "load_energy_j": energy_j,
        "load_energy_gj": energy_j / 1e9,
        "load_energy_kwh": energy_kwh,
        "output_current_rms_a": current_rms,
        "output_voltage_peak_v": voltage_peak,
        "minimum_dc_bus_target_v": dc_bus_target,
    }


def decay_factor(years: float, half_life_years: float) -> float:
    _require_positive("half_life_years", half_life_years)
    if years < 0 or not math.isfinite(years):
        raise ValueError("years must be finite and nonnegative")
    return 2.0 ** (-years / half_life_years)


def heat_rejection_flux_w_m2(spec: BoxSpec) -> float:
    validate_box_spec(spec)
    ts = spec.radiator_surface_c + 273.15
    ta = spec.ambient_c + 273.15
    radiative = spec.radiator_emissivity * SIGMA_SB * (ts**4 - ta**4)
    convective = spec.natural_convection_w_m2k * (ts - ta)
    return radiative + convective


def long_life_source_bound(spec: BoxSpec) -> dict[str, float]:
    """Return a decay-source lower-bound model sized to meet rated output at EOL.

    The model intentionally ignores shielding, encapsulation, conversion-area,
    electronics degradation, redundancy, and regulatory constraints.  It is a
    thermodynamic/material inventory bound, not a complete-system mass estimate.
    """

    validate_box_spec(spec)
    eta_total = spec.converter_efficiency * spec.inverter_efficiency
    end_decay = decay_factor(spec.service_years, spec.source_half_life_years)
    eol_thermal_needed = spec.output_power_w / eta_total
    bol_thermal_needed = eol_thermal_needed / end_decay
    source_mass_g = bol_thermal_needed / spec.source_specific_thermal_power_w_per_g
    bol_electrical_capacity = bol_thermal_needed * eta_total
    # Constant rated output implies curtailing/dumping surplus at beginning of life.
    bol_rejected_if_clamped = bol_thermal_needed - spec.output_power_w
    eol_rejected = eol_thermal_needed - spec.output_power_w
    flux = heat_rejection_flux_w_m2(spec)
    return {
        "total_conversion_efficiency": eta_total,
        "end_of_life_decay_fraction": end_decay,
        "beginning_thermal_power_w": bol_thermal_needed,
        "end_thermal_power_w": eol_thermal_needed,
        "analytical_source_mass_g": source_mass_g,
        "analytical_source_mass_kg": source_mass_g / 1000.0,
        "beginning_electrical_capacity_w": bol_electrical_capacity,
        "beginning_rejected_heat_if_output_clamped_w": bol_rejected_if_clamped,
        "end_rejected_heat_w": eol_rejected,
        "radiator_flux_at_design_temperature_w_m2": flux,
        "radiator_area_bol_m2": bol_rejected_if_clamped / flux,
        "radiator_area_eol_m2": eol_rejected / flux,
    }


def poynting_and_transport_notes() -> dict[str, str]:
    return {
        "charge_transport": "Charge carriers move; the electric field biases their transport.",
        "energy_transport": "Electromagnetic energy transport is represented by the Poynting vector.",
        "symmetry": "Broken inversion symmetry can permit second-order rectification or shift current.",
        "no_go": "At global equilibrium, detailed balance removes sustained directed work.",
    }


def fibonacci_word(order: int) -> str:
    if order < 0:
        raise ValueError("order must be nonnegative")
    word = "H"
    for _ in range(order):
        word = "".join("HL" if ch == "H" else "H" for ch in word)
    return word


def fibonacci_counts(order: int) -> tuple[int, int, int]:
    word = fibonacci_word(order)
    return word.count("H"), word.count("L"), len(word)


def characteristic_matrix(n: complex, d_um: float, wavelength_um: np.ndarray) -> np.ndarray:
    delta = 2.0 * np.pi * n * d_um / wavelength_um
    c = np.cos(delta)
    s = np.sin(delta)
    out = np.empty((len(wavelength_um), 2, 2), dtype=np.complex128)
    out[:, 0, 0] = c
    out[:, 0, 1] = 1j * s / n
    out[:, 1, 0] = 1j * n * s
    out[:, 1, 1] = c
    return out


def transfer_matrix_spectrum(
    word: str,
    wavelength_um: np.ndarray,
    wavelength_design_um: float,
    scale_high: float,
    scale_low: float,
    spec: OpticalSpec,
) -> dict[str, np.ndarray]:
    if wavelength_design_um <= 0:
        raise ValueError("wavelength_design_um must be positive")
    if not len(word):
        raise ValueError("word cannot be empty")
    matrix = np.broadcast_to(np.eye(2, dtype=np.complex128), (len(wavelength_um), 2, 2)).copy()
    d_high = scale_high * wavelength_design_um / (4.0 * spec.n_high.real)
    d_low = scale_low * wavelength_design_um / (4.0 * spec.n_low.real)
    for ch in word:
        if ch == "H":
            layer = characteristic_matrix(spec.n_high, d_high, wavelength_um)
        elif ch == "L":
            layer = characteristic_matrix(spec.n_low, d_low, wavelength_um)
        else:
            raise ValueError(f"invalid layer token {ch!r}")
        matrix = np.einsum("nij,njk->nik", matrix, layer)
    a = matrix[:, 0, 0]
    b = matrix[:, 0, 1]
    c = matrix[:, 1, 0]
    d = matrix[:, 1, 1]
    y_in = (c + d * spec.n_substrate) / (a + b * spec.n_substrate)
    r = (spec.n_incident - y_in) / (spec.n_incident + y_in)
    reflectance = np.abs(r) ** 2
    # Numerical and surrogate-dispersion imperfections can produce tiny excursions.
    reflectance = np.clip(reflectance.real, 0.0, 1.0)
    emissivity = 1.0 - reflectance  # opaque-substrate approximation
    return {
        "reflectance": reflectance,
        "emissivity": emissivity,
        "d_high_um": np.full_like(wavelength_um, d_high, dtype=float),
        "d_low_um": np.full_like(wavelength_um, d_low, dtype=float),
    }


def optical_score(wavelength_um: np.ndarray, emissivity: np.ndarray, lambda_g_um: float, layer_count: int, penalty: float) -> dict[str, float]:
    desired = (wavelength_um >= 0.78 * lambda_g_um) & (wavelength_um <= 1.12 * lambda_g_um)
    longwave = (wavelength_um >= 1.45 * lambda_g_um) & (wavelength_um <= 3.00 * lambda_g_um)
    shortwave = (wavelength_um >= 0.45 * lambda_g_um) & (wavelength_um < 0.78 * lambda_g_um)
    inband = float(np.mean(emissivity[desired]))
    out_long = float(np.mean(emissivity[longwave]))
    out_short = float(np.mean(emissivity[shortwave]))
    selectivity = inband - 0.70 * out_long - 0.15 * out_short
    penalized = selectivity - penalty * layer_count
    return {
        "inband_mean_emissivity": inband,
        "longwave_mean_emissivity": out_long,
        "shortwave_mean_emissivity": out_short,
        "raw_selectivity": selectivity,
        "penalized_score": penalized,
    }


def search_fibonacci_stack(spec: OpticalSpec) -> dict[str, Any]:
    lambda_g_um = HC_EV_UM / spec.bandgap_ev
    wavelength_um = np.linspace(0.45 * lambda_g_um, 3.0 * lambda_g_um, 1200)
    scales = np.linspace(spec.thickness_scale_min, spec.thickness_scale_max, spec.thickness_scale_steps)
    rows: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None
    for order in range(spec.order_min, spec.order_max + 1):
        word = fibonacci_word(order)
        for sh in scales:
            for sl in scales:
                spectrum = transfer_matrix_spectrum(word, wavelength_um, lambda_g_um, float(sh), float(sl), spec)
                score = optical_score(wavelength_um, spectrum["emissivity"], lambda_g_um, len(word), spec.layer_penalty)
                row = {
                    "order": order,
                    "word": word,
                    "layers": len(word),
                    "high_layers": word.count("H"),
                    "low_layers": word.count("L"),
                    "scale_high": float(sh),
                    "scale_low": float(sl),
                    "d_high_nm": float(spectrum["d_high_um"][0] * 1000.0),
                    "d_low_nm": float(spectrum["d_low_um"][0] * 1000.0),
                    **score,
                }
                rows.append(row)
                if best is None or row["penalized_score"] > best["penalized_score"]:
                    best = row
    assert best is not None
    best_word = str(best["word"])
    best_spectrum = transfer_matrix_spectrum(
        best_word,
        wavelength_um,
        lambda_g_um,
        float(best["scale_high"]),
        float(best["scale_low"]),
        spec,
    )
    return {
        "optical_spec": optical_spec_to_json(spec),
        "bandgap_cutoff_um": lambda_g_um,
        "best": best,
        "wavelength_um": wavelength_um.tolist(),
        "best_reflectance": best_spectrum["reflectance"].tolist(),
        "best_emissivity": best_spectrum["emissivity"].tolist(),
        "candidate_count": len(rows),
        "top_candidates": sorted(rows, key=lambda r: r["penalized_score"], reverse=True)[:20],
    }


def optical_spec_to_json(spec: OpticalSpec) -> dict[str, Any]:
    d = asdict(spec)
    for k in ("n_high", "n_low", "n_substrate", "n_incident"):
        z = complex(d[k])
        d[k] = {"real": z.real, "imag": z.imag}
    return d


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
        {"id": "A11", "name": "Power quality and protection", "criterion": "220 V RMS, 60 Hz output remains within harmonic, isolation, overcurrent, ground-fault, and safe-shutdown limits"},
        {"id": "A12", "name": "Receipt and manufacturability", "criterion": "every layer, process window, measurement, uncertainty, and failure test is traceable and reproducible"},
    ]


def twelve_candidate_layers() -> list[dict[str, str]]:
    return [
        {"id": "L01", "layer": "Primary free-energy port", "candidate": "external heater for Phase A; regulated isotope heat only as an institutional Phase C option", "status": "SOURCE"},
        {"id": "L02", "layer": "Refractory heat spreader", "candidate": "SiC, graphite composite, molybdenum, or tungsten candidate after compatibility testing", "status": "DESIGN"},
        {"id": "L03", "layer": "Diffusion and oxidation barrier", "candidate": "ALD ceramic or refractory nitride candidate selected by hot-soak testing", "status": "DESIGN"},
        {"id": "L04", "layer": "Selective emitter", "candidate": "W/HfO2-inspired refractory multilayer or photonic-crystal emitter", "status": "RESEARCH"},
        {"id": "L05", "layer": "Fibonacci spectral filter", "candidate": "H/L quasiperiodic dielectric sequence generated by H->HL and L->H", "status": "ILLUSTRATIVE COMPUTE"},
        {"id": "L06", "layer": "Photon cavity", "candidate": "vacuum or controlled low-index gap with view-factor management", "status": "DESIGN"},
        {"id": "L07", "layer": "TPV junction", "candidate": "air-bridge InGaAs(P)-class junction matched to emitter spectrum", "status": "RESEARCH"},
        {"id": "L08", "layer": "Photon-recycling reflector", "candidate": "high-reflectance back surface for below-band-gap photons", "status": "RESEARCH"},
        {"id": "L09", "layer": "Fractal current collector", "candidate": "interdigitated or space-filling electrode compared against a straight-busbar control", "status": "HYPOTHESIS"},
        {"id": "L10", "layer": "Cold-side heat spreader", "candidate": "AlN, SiC, graphite, or diamond-composite candidate", "status": "DESIGN"},
        {"id": "L11", "layer": "DC conditioning and inverter", "candidate": "ceramic/film DC link plus SiC or GaN switching bridge and LC output filter", "status": "ENGINEERING"},
        {"id": "L12", "layer": "Hermetic shell and radiator", "candidate": "welded enclosure, getters, redundant sensing, passive fins, and service-isolated output", "status": "ENGINEERING"},
    ]


def make_certificate(box: BoxSpec, optical: OpticalSpec, optical_result: dict[str, Any]) -> dict[str, Any]:
    energy = lifetime_energy(box)
    source = long_life_source_bound(box)
    payload = {
        "artifact": ARTIFACT,
        "version": VERSION,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": {
            "energy_ledger": "EXACT ARITHMETIC UNDER DECLARED INPUTS",
            "decay_source": "ANALYTICAL LOWER-BOUND MODEL",
            "optical_stack": "ILLUSTRATIVE TRANSFER-MATRIX SEARCH",
            "hundred_year_box": "HYPOTHESIS -- NOT DEMONSTRATED",
            "free_energy": "REJECTED",
        },
        "box_spec": asdict(box),
        "energy": energy,
        "source_bound": source,
        "transport_notes": poynting_and_transport_notes(),
        "anchors": twelve_anchor_constraints(),
        "stack": twelve_candidate_layers(),
        "optical_search": optical_result,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
    }
    stable = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    payload["sha256"] = hashlib.sha256(stable).hexdigest()
    return payload


def human_results(cert: dict[str, Any]) -> str:
    b = cert["box_spec"]
    e = cert["energy"]
    s = cert["source_bound"]
    o = cert["optical_search"]["best"]
    lines = [
        f"{ARTIFACT} v{VERSION}",
        "",
        "HONEST BOUNDARY",
        "  Broken symmetry can select/rectify a response; it cannot supply the missing free energy.",
        "  The 100-year integrated product is a hypothesis, not a demonstrated device.",
        "",
        "DEFAULT BOX",
        f"  output target           {b['output_power_w']:.3f} W",
        f"  interface               {b['output_voltage_rms_v']:.1f} V RMS at {b['output_frequency_hz']:.1f} Hz",
        f"  output current          {e['output_current_rms_a']:.6f} A RMS at PF {b['power_factor']:.3f}",
        f"  sine peak               {e['output_voltage_peak_v']:.3f} V",
        f"  design DC-bus floor     {e['minimum_dc_bus_target_v']:.3f} V",
        f"  service target          {b['service_years']:.3f} y",
        f"  load energy             {e['load_energy_gj']:.6f} GJ  |  {e['load_energy_kwh']:.3f} kWh",
        "",
        "DECAY-SOURCE LOWER BOUND",
        f"  total efficiency        {100.0*s['total_conversion_efficiency']:.3f} %",
        f"  EOL decay fraction      {s['end_of_life_decay_fraction']:.9f}",
        f"  source mass             {s['analytical_source_mass_kg']:.6f} kg (active material only)",
        f"  BOL thermal power       {s['beginning_thermal_power_w']:.3f} Wth",
        f"  EOL thermal power       {s['end_thermal_power_w']:.3f} Wth",
        f"  BOL surplus heat        {s['beginning_rejected_heat_if_output_clamped_w']:.3f} W",
        f"  EOL rejected heat       {s['end_rejected_heat_w']:.3f} W",
        f"  radiator area BOL       {s['radiator_area_bol_m2']:.4f} m^2 at declared surface/ambient",
        f"  radiator area EOL       {s['radiator_area_eol_m2']:.4f} m^2 at declared surface/ambient",
        "",
        "ILLUSTRATIVE FIBONACCI OPTICAL SEARCH",
        f"  candidates evaluated    {cert['optical_search']['candidate_count']}",
        f"  bandgap cutoff          {cert['optical_search']['bandgap_cutoff_um']:.6f} um",
        f"  best order              {o['order']}",
        f"  layer word              {o['word']}",
        f"  layer count             {o['layers']}",
        f"  H/L thickness           {o['d_high_nm']:.3f} / {o['d_low_nm']:.3f} nm",
        f"  scale H/L               {o['scale_high']:.6f} / {o['scale_low']:.6f}",
        f"  in-band emissivity      {o['inband_mean_emissivity']:.6f}",
        f"  long-wave emissivity    {o['longwave_mean_emissivity']:.6f}",
        f"  penalized score         {o['penalized_score']:.6f}",
        "",
        f"SHA256  {cert['sha256']}",
    ]
    return "\n".join(lines) + "\n"


def write_csv(path: Path, cert: dict[str, Any]) -> None:
    o = cert["optical_search"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["wavelength_um", "reflectance", "emissivity"])
        for lam, r, em in zip(o["wavelength_um"], o["best_reflectance"], o["best_emissivity"], strict=True):
            w.writerow([f"{lam:.10g}", f"{r:.10g}", f"{em:.10g}"])


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--power-w", type=float, default=100.0)
    p.add_argument("--years", type=float, default=100.0)
    p.add_argument("--converter-efficiency", type=float, default=0.30)
    p.add_argument("--inverter-efficiency", type=float, default=0.95)
    p.add_argument("--bandgap-ev", type=float, default=0.74)
    p.add_argument("--output-dir", type=Path, default=Path("."))
    return p.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    box = BoxSpec(
        output_power_w=args.power_w,
        service_years=args.years,
        converter_efficiency=args.converter_efficiency,
        inverter_efficiency=args.inverter_efficiency,
    )
    optical = OpticalSpec(bandgap_ev=args.bandgap_ev)
    optical_result = search_fibonacci_stack(optical)
    cert = make_certificate(box, optical, optical_result)
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "metalatexium_v0_1_certificate.json"
    txt_path = out / "metalatexium_v0_1_results.txt"
    csv_path = out / "metalatexium_v0_1_optical_spectrum.csv"
    json_path.write_text(json.dumps(cert, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    txt_path.write_text(human_results(cert), encoding="utf-8")
    write_csv(csv_path, cert)
    print(human_results(cert), end="")
    print(f"wrote {json_path}")
    print(f"wrote {txt_path}")
    print(f"wrote {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
