# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — TV/EV Scorer Unit Tests
"""
Unit tests for ``tools.tvev.scorer``.

Run with:
    python -m pytest tools/tvev/test_scorer.py -v

or via the Makefile:
    make test
"""

from __future__ import annotations

import unittest

from tools.tvev.scorer import (
    LatencyObservation,
    ScorerConfig,
    TVEVScorer,
    TVEVResult,
    _to_grade,
    _reliability_multiplier,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def make_scorer(**kwargs) -> TVEVScorer:
    return TVEVScorer(ScorerConfig(**kwargs))


def make_lat(p50: float = 2.5, p95: float = 4.8, p99: float = 6.2) -> LatencyObservation:
    return LatencyObservation(p50=p50, p95=p95, p99=p99)


# ---------------------------------------------------------------------------
# LatencyObservation
# ---------------------------------------------------------------------------


class TestLatencyObservation(unittest.TestCase):
    def test_weighted_ev_spec_example(self):
        """Spec example: P50=2.5, P95=4.8, P99=6.2 → EV=5.04."""
        lat = LatencyObservation(p50=2.5, p95=4.8, p99=6.2)
        self.assertAlmostEqual(lat.weighted_ev(), 5.04, places=6)

    def test_weighted_ev_zero(self):
        lat = LatencyObservation(p50=0.0, p95=0.0, p99=0.0)
        self.assertEqual(lat.weighted_ev(), 0.0)

    def test_weights_sum(self):
        """0.2 + 0.3 + 0.5 == 1.0."""
        lat = LatencyObservation(p50=10.0, p95=10.0, p99=10.0)
        self.assertAlmostEqual(lat.weighted_ev(), 10.0)


# ---------------------------------------------------------------------------
# ScorerConfig validation
# ---------------------------------------------------------------------------


class TestScorerConfig(unittest.TestCase):
    def test_weights_must_sum_to_one(self):
        with self.assertRaises(ValueError):
            ScorerConfig(weight_tv=0.6, weight_ev=0.6)

    def test_invalid_composite_method(self):
        with self.assertRaises(ValueError):
            ScorerConfig(composite_method="bad")

    def test_valid_defaults(self):
        cfg = ScorerConfig()
        self.assertAlmostEqual(cfg.weight_tv + cfg.weight_ev, 1.0)


# ---------------------------------------------------------------------------
# Grade bands
# ---------------------------------------------------------------------------


class TestGradeBands(unittest.TestCase):
    def test_grade_boundaries(self):
        expected = [
            (100.0, "A+"),
            (97.0,  "A+"),
            (96.99, "A"),
            (93.0,  "A"),
            (92.99, "A-"),
            (90.0,  "A-"),
            (89.99, "B+"),
            (83.0,  "B"),
            (80.0,  "B-"),
            (77.0,  "C+"),
            (73.0,  "C"),
            (70.0,  "C-"),
            (60.0,  "D"),
            (59.99, "F"),
            (0.0,   "F"),
        ]
        for score, grade in expected:
            with self.subTest(score=score):
                self.assertEqual(_to_grade(score), grade)


# ---------------------------------------------------------------------------
# Reliability multiplier
# ---------------------------------------------------------------------------


class TestReliabilityMultiplier(unittest.TestCase):
    def test_no_errors(self):
        self.assertEqual(_reliability_multiplier(0.0), 1.0)

    def test_minor_errors(self):
        r = _reliability_multiplier(0.00005)   # < 0.01%
        self.assertAlmostEqual(r, 0.99)

    def test_critical_error(self):
        self.assertEqual(_reliability_multiplier(0.0, critical_error=True), 0.0)

    def test_high_error_rate(self):
        r = _reliability_multiplier(0.005)     # > 0.10%
        self.assertAlmostEqual(r, 0.93)


# ---------------------------------------------------------------------------
# Scorer — spec worked example (Section 13 of TV-EV Specification.md)
# ---------------------------------------------------------------------------


class TestScorerSpecExample(unittest.TestCase):
    """Reproduce the example in Section 13 of the TV/EV Specification."""

    def setUp(self):
        self.scorer = make_scorer(
            tv_target=10_000.0,
            ev_target_ms=5.0,
            weight_tv=0.5,
            weight_ev=0.5,
        )
        self.lat = LatencyObservation(p50=2.5, p95=4.8, p99=6.2)

    def test_tv_score(self):
        self.assertAlmostEqual(self.scorer.tv_score(9_200.0), 92.0)

    def test_ev_observed(self):
        self.assertAlmostEqual(self.lat.weighted_ev(), 5.04, places=4)

    def test_ev_score(self):
        ev_obs = self.lat.weighted_ev()   # 5.04
        self.assertAlmostEqual(self.scorer.ev_score(ev_obs), 5.0 / 5.04 * 100, places=2)

    def test_composite(self):
        # Spec: 0.5*92 + 0.5*99.2 = 95.6 (approx)
        tv_s = self.scorer.tv_score(9_200.0)
        ev_s = self.scorer.ev_score(self.lat.weighted_ev())
        comp = self.scorer.composite_score(tv_s, ev_s)
        self.assertAlmostEqual(comp, 95.6, delta=0.3)

    def test_final_grade_with_reliability(self):
        result = self.scorer.score(
            tv_observed=9_200.0,
            latency=self.lat,
            error_rate=0.00005,  # minor errors → penalty 0.01
        )
        # Spec predicts adjusted ≈ 94.64 → grade A
        self.assertAlmostEqual(result.adjusted_score, 94.64, delta=0.5)
        self.assertIn(result.grade, ("A", "A-", "A+"))


# ---------------------------------------------------------------------------
# Scorer — gate conditions
# ---------------------------------------------------------------------------


class TestGateConditions(unittest.TestCase):
    def test_fails_gate_low_tv(self):
        scorer = make_scorer(tv_target=10_000.0, ev_target_ms=5.0)
        # Very low TV → TV_score < 70
        result = scorer.score(
            tv_observed=1_000.0,
            latency=LatencyObservation(p50=1.0, p95=2.0, p99=3.0),
        )
        self.assertFalse(result.passed_gate)
        self.assertEqual(result.grade, "F")

    def test_fails_gate_low_ev(self):
        scorer = make_scorer(tv_target=10_000.0, ev_target_ms=5.0)
        # Very high latency → EV_score < 70
        result = scorer.score(
            tv_observed=10_000.0,
            latency=LatencyObservation(p50=50.0, p95=80.0, p99=100.0),
        )
        self.assertFalse(result.passed_gate)
        self.assertEqual(result.grade, "F")

    def test_passes_gate_balanced(self):
        scorer = make_scorer(tv_target=10_000.0, ev_target_ms=5.0)
        result = scorer.score(
            tv_observed=9_000.0,
            latency=LatencyObservation(p50=2.0, p95=4.0, p99=5.0),
        )
        self.assertTrue(result.passed_gate)

    def test_critical_error_forces_zero_score(self):
        scorer = make_scorer()
        result = scorer.score(
            tv_observed=10_000.0,
            latency=LatencyObservation(p50=1.0, p95=2.0, p99=3.0),
            critical_error=True,
        )
        self.assertEqual(result.adjusted_score, 0.0)
        self.assertEqual(result.grade, "F")


# ---------------------------------------------------------------------------
# Scorer — geometric composite
# ---------------------------------------------------------------------------


class TestGeometricComposite(unittest.TestCase):
    def test_geometric_penalises_weakness(self):
        cfg_geo = ScorerConfig(composite_method="geometric", weight_tv=0.5, weight_ev=0.5)
        cfg_sum = ScorerConfig(composite_method="weighted_sum", weight_tv=0.5, weight_ev=0.5)

        scorer_geo = TVEVScorer(cfg_geo)
        scorer_sum = TVEVScorer(cfg_sum)

        # One dimension very weak (TV_score ≈ 50, EV_score ≈ 100)
        tv_s, ev_s = 50.0, 100.0

        geo = scorer_geo.composite_score(tv_s, ev_s)
        lin = scorer_sum.composite_score(tv_s, ev_s)

        # Geometric should be lower than linear for asymmetric inputs
        self.assertLess(geo, lin)


# ---------------------------------------------------------------------------
# TVEVResult helpers
# ---------------------------------------------------------------------------


class TestTVEVResultHelpers(unittest.TestCase):
    def _make_result(self) -> TVEVResult:
        scorer = make_scorer()
        return scorer.score(
            tv_observed=9_200.0,
            latency=make_lat(),
        )

    def test_summary_contains_grade(self):
        r = self._make_result()
        self.assertIn(r.grade, r.summary())

    def test_report_contains_all_fields(self):
        r = self._make_result()
        report = r.report()
        for keyword in ("TV observed", "EV observed", "Final grade", "Reliability mult."):
            self.assertIn(keyword, report)


if __name__ == "__main__":
    unittest.main()
