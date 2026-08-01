#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import numpy as np

import metalatexium_kernel_v0_1 as m


def test_lifetime_energy() -> None:
    s = m.BoxSpec(output_power_w=100.0, service_years=100.0)
    r = m.lifetime_energy(s)
    assert math.isclose(r["load_energy_kwh"], 87660.0, rel_tol=0, abs_tol=1e-9)
    assert math.isclose(r["output_current_rms_a"], 100.0 / 220.0, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(r["output_voltage_peak_v"], math.sqrt(2.0) * 220.0, rel_tol=0, abs_tol=1e-12)


def test_decay_bound() -> None:
    s = m.BoxSpec(output_power_w=100.0, service_years=100.0, converter_efficiency=0.30, inverter_efficiency=0.95)
    r = m.long_life_source_bound(s)
    assert 0.45 < r["end_of_life_decay_fraction"] < 0.46
    assert 1.35 < r["analytical_source_mass_kg"] < 1.37
    assert r["beginning_thermal_power_w"] > r["end_thermal_power_w"] > s.output_power_w
    assert r["radiator_area_bol_m2"] > r["radiator_area_eol_m2"] > 0.0


def test_fibonacci_counts_and_ratio() -> None:
    h, l, total = m.fibonacci_counts(10)
    assert total == h + l
    assert abs(h / l - (1.0 + math.sqrt(5.0)) / 2.0) < 0.02


def test_optical_spectrum_is_physical_under_surrogate() -> None:
    spec = m.OpticalSpec(order_min=3, order_max=3, thickness_scale_steps=3)
    lam_g = m.HC_EV_UM / spec.bandgap_ev
    wave = np.linspace(0.45 * lam_g, 3.0 * lam_g, 200)
    out = m.transfer_matrix_spectrum(m.fibonacci_word(3), wave, lam_g, 1.0, 1.0, spec)
    assert np.all(np.isfinite(out["reflectance"]))
    assert np.all(np.isfinite(out["emissivity"]))
    assert np.min(out["reflectance"]) >= 0.0
    assert np.max(out["reflectance"]) <= 1.0
    assert np.allclose(out["reflectance"] + out["emissivity"], 1.0, atol=1e-12)


def test_anchor_and_stack_count() -> None:
    assert len(m.twelve_anchor_constraints()) == 12
    assert len(m.twelve_candidate_layers()) == 12


def test_certificate_round_trip() -> None:
    box = m.BoxSpec(output_power_w=10.0, service_years=20.0)
    optical = m.OpticalSpec(order_min=3, order_max=3, thickness_scale_steps=3)
    result = m.search_fibonacci_stack(optical)
    cert = m.make_certificate(box, optical, result)
    assert len(cert["sha256"]) == 64
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "cert.json"
        p.write_text(json.dumps(cert, default=str), encoding="utf-8")
        read = json.loads(p.read_text(encoding="utf-8"))
        assert read["status"]["free_energy"] == "REJECTED"


def main() -> int:
    tests = [
        test_lifetime_energy,
        test_decay_bound,
        test_fibonacci_counts_and_ratio,
        test_optical_spectrum_is_physical_under_surrogate,
        test_anchor_and_stack_count,
        test_certificate_round_trip,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"PASS {len(tests)}/{len(tests)} tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
