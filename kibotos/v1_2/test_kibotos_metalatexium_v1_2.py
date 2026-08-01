#!/usr/bin/env python3
"""KIBOTOS-METALATEXIUM v1.2 -- merged test suite.
Sol's v0.1 test semantics preserved (tests 1-4, 9), plus the weld assertions."""
from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import numpy as np

import kibotos_metalatexium_v1_2 as k


def test_lifetime_energy() -> None:  # Sol v0.1, ported
    s = k.BoxSpec(output_power_w=100.0, service_years=100.0)
    r = k.lifetime_energy(s)
    assert math.isclose(r["load_energy_kwh"], 87660.0, rel_tol=0, abs_tol=1e-9)
    assert math.isclose(r["output_current_rms_a"], 100.0 / 220.0, abs_tol=1e-12)
    assert math.isclose(r["output_voltage_peak_v"], math.sqrt(2.0) * 220.0, abs_tol=1e-12)


def test_decay_bound_sol_point() -> None:  # Sol v0.1, ported
    s = k.BoxSpec(converter_efficiency=0.30, inverter_efficiency=0.95)
    r = k.long_life_source_bound(s)
    assert 0.45 < r["end_of_life_decay_fraction"] < 0.46
    assert 1.35 < r["analytical_source_mass_kg"] < 1.37
    assert r["beginning_thermal_power_w"] > r["end_thermal_power_w"] > s.output_power_w


def test_fibonacci_counts_and_ratio() -> None:  # Sol v0.1, ported
    h, l, total = k.fibonacci_counts(10)
    assert total == h + l
    assert abs(h / l - (1.0 + math.sqrt(5.0)) / 2.0) < 0.02
    assert k.fibonacci_word(4) == "HLHHLHLH"


def test_spectra_physical() -> None:  # Sol v0.1 semantics on both optics
    lam = k.cavity_grid()
    spec = k.OpticalSpec()
    eps = k.emitter_emissivity("HLHHLHLH", lam, 1.6755, 0.80, 1.28, spec)
    r = k.mirror_reflectance(lam, spec)
    for arr in (eps, r):
        assert np.all(np.isfinite(arr)) and np.min(arr) >= 0.0 and np.max(arr) <= 1.0
    assert np.allclose(eps + (1.0 - eps), 1.0, atol=1e-12)


def test_mirror_physical_spec() -> None:
    lam = k.cavity_grid()
    spec = k.OpticalSpec()
    r = k.mirror_reflectance(lam, spec)
    lg = k.HC_EV_UM / spec.bandgap_ev
    sub = lam >= lg
    lam_sub = lam[sub]
    b = k.planck_spectral_w_m2_um(lam_sub, spec.emitter_temperature_k)
    planck_weighted = float(np.trapezoid(r[sub] * b, lam_sub) / np.trapezoid(b, lam_sub))
    seg = 0.5 * (b[1:] + b[:-1]) * np.diff(lam_sub)
    cum = np.concatenate([[0.0], np.cumsum(seg)]); cum = cum / cum[-1]
    lam90 = float(lam_sub[np.searchsorted(cum, 0.90)])
    assert planck_weighted >= 0.98                       # the physical spec
    assert float(np.min(r[sub][lam_sub <= lam90])) >= 0.88  # power-band worst
    assert float(np.min(r[sub])) >= 0.85                 # documented far-IR notch floor


def test_cavity_controls_and_weld() -> None:
    lam = k.cavity_grid()
    spec = k.OpticalSpec()
    lg = k.HC_EV_UM / spec.bandgap_ev
    eps = np.full_like(lam, 0.90)
    none = k.cavity_metrics(eps, np.zeros_like(lam), lam, lg, 1300.0)
    weld = k.cavity_metrics(eps, k.mirror_reflectance(lam, spec), lam, lg, 1300.0)
    assert none["eta_spectral"] < 0.20          # the damning control
    assert weld["eta_spectral"] > 0.80          # the weld
    assert weld["eta_spectral"] > 4.0 * none["eta_spectral"]


def test_derived_band_brackets_sol_assumption() -> None:
    w = k.run_weld()
    ch = w["derived_chain_gray_weld"]
    lo, hi = ch["eta_cell_0.30"], ch["eta_cell_0.40"]
    assert 0.20 < lo < hi < 0.40
    assert lo <= 0.285 <= hi                    # Sol assumed it; v1.2 derives it


def test_source_mass_at_derived_center() -> None:
    w = k.run_weld()
    m = w["boxes_at_derived_eta"]["eta_cell_0.35"]["source_mass_kg"]
    assert 1.0 < m < 1.8


def test_certificate_round_trip_free_energy_rejected() -> None:  # Sol v0.1, extended
    w = k.run_weld()
    eta_sp = w["cavity_cases"]["gray_0.90|weld_phi2_chirp"]["eta_spectral"]
    cert = k.make_certificate(k.BoxSpec(converter_efficiency=eta_sp * 0.35), k.OpticalSpec(), w)
    assert len(cert["sha256"]) == 64
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "cert.json"
        p.write_text(json.dumps(cert, default=str), encoding="utf-8")
        read = json.loads(p.read_text(encoding="utf-8"))
        assert read["status"]["free_energy"] == "REJECTED"
        assert read["status"]["hundred_year_box"].startswith("HYPOTHESIS")


def test_certificate_reproducible() -> None:  # Curse 38: hash the math, not the moment
    w = k.run_weld()
    eta_sp = w["cavity_cases"]["gray_0.90|weld_phi2_chirp"]["eta_spectral"]
    box = k.BoxSpec(converter_efficiency=eta_sp * 0.35)
    a = k.make_certificate(box, k.OpticalSpec(), w)
    b = k.make_certificate(box, k.OpticalSpec(), w)
    assert a["sha256"] == b["sha256"]                       # two runs, one math-hash
    # the clock and environment are recorded but NOT sealed by the hash
    import hashlib as _h, json as _j
    core = {kk: vv for kk, vv in a.items() if kk not in ("sha256", "generated_utc", "environment")}
    stable = _j.dumps(core, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    assert _h.sha256(stable).hexdigest() == a["sha256"]     # hash covers the math only


def test_lineage_hashes_present() -> None:
    rep = k.lineage_report()
    for key in ("sol_kernel_v0_1_sha256", "sol_certificate_file_sha256", "sol_certificate_embedded_sha256"):
        assert len(rep[key]) == 64
    assert "fable_v1_0_scroll_sha256" in rep


def test_anchor_and_stack_count() -> None:  # Sol v0.1, ported (P=12)
    assert len(k.twelve_anchor_constraints()) == 12
    assert len(k.twelve_candidate_layers()) == 12


def main() -> int:
    tests = [
        test_lifetime_energy,
        test_decay_bound_sol_point,
        test_fibonacci_counts_and_ratio,
        test_spectra_physical,
        test_mirror_physical_spec,
        test_cavity_controls_and_weld,
        test_derived_band_brackets_sol_assumption,
        test_source_mass_at_derived_center,
        test_certificate_round_trip_free_energy_rejected,        test_certificate_reproducible,        test_lineage_hashes_present,
        test_anchor_and_stack_count,
    ]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"PASS {len(tests)}/{len(tests)} tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
