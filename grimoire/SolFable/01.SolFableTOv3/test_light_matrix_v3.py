#!/usr/bin/env python3
"""Fast exact tests for the THEA v3.0 light-matrix kernel."""

from __future__ import annotations

import math
import unittest

import light_matrix_v3 as lm


class LightMatrixExactTests(unittest.TestCase):
    def test_euler_counts(self) -> None:
        for t in (1, 3, 7, 19, 49, 129):
            topo = lm.topology_from_t(t)
            self.assertEqual(topo["P"], 12)
            self.assertEqual(topo["chi"], 2)
            self.assertEqual(topo["V"], 20 * t)
            self.assertEqual(topo["E"], 30 * t)
            self.assertEqual(topo["H"], 10 * (t - 1))

    def test_golden_shell_sequence(self) -> None:
        shells = lm.golden_shells(7)
        self.assertEqual([s.triangulation_number for s in shells], [1, 3, 7, 19, 49, 129, 337])
        self.assertEqual([s.vertices for s in shells], [20, 60, 140, 380, 980, 2580, 6740])

    def test_projective_attractor(self) -> None:
        shells = lm.golden_shells(15)
        errors = [s.projective_error for s in shells if s.projective_error is not None]
        self.assertLess(errors[-1], errors[-3])
        self.assertLess(errors[-1], 1.0e-5)

    def test_norm_multiplicative(self) -> None:
        a = lm.Pair(7, 3)
        b = lm.Pair(4, 1)
        product = lm.multiply_pairs(a, b)
        self.assertEqual(lm.hex_norm(product.k, product.ell), lm.hex_norm(a.k, a.ell) * lm.hex_norm(b.k, b.ell))

    def test_canonical_rotation(self) -> None:
        self.assertEqual(lm.canonical_pair(lm.Pair(0, 3)), lm.Pair(3, 0))
        self.assertEqual(lm.canonical_pair(lm.Pair(-3, 6)), lm.Pair(3, 3))

    def test_lifted_matrix(self) -> None:
        p = lm.Pair(8, 5)
        next_p = lm.golden_next(p)
        state = (p.k * p.k, p.k * p.ell, p.ell * p.ell)
        lifted = lm.lifted_step(state)
        self.assertEqual(lifted, (next_p.k**2, next_p.k * next_p.ell, next_p.ell**2))

    def test_closed_form(self) -> None:
        for shell in lm.golden_shells(12):
            self.assertAlmostEqual(lm.golden_closed_form_t(shell.level), shell.triangulation_number, places=7)

    def test_planck_count_is_choice_dependent(self) -> None:
        report = lm.planck_report()
        self.assertNotAlmostEqual(report["levels_from_edge"], report["levels_from_radius"], places=3)
        self.assertAlmostEqual(report["levels_from_radius"], 60.62053001048617, places=8)


if __name__ == "__main__":
    unittest.main()
