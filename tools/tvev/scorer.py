# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — TV/EV Trade Engine Scorer
"""
TV/EV Performance Grading for trade engines.

Implements the full TV/EV Specification (see TV-EV Specification.md):

* TV score  — normalised trading volume against a target
* EV score  — normalised execution velocity (weighted latency percentiles)
* Composite — weighted sum or geometric composite
* Gate conditions — prevent a single strong dimension from hiding a weak one
* Reliability multiplier — penalise correctness failures

All configuration and results are expressed as Python dataclasses.

Example
-------
    from tools.tvev.scorer import TVEVScorer, ScorerConfig, LatencyObservation

    scorer = TVEVScorer(ScorerConfig(
        tv_target=10_000.0,
        ev_target_ms=5.0,
        weight_tv=0.5,
        weight_ev=0.5,
    ))

    result = scorer.score(
        tv_observed=9_200.0,
        latency=LatencyObservation(p50=2.5, p95=4.8, p99=6.2),
        error_rate=0.0001,
    )

    print(result.grade, result.adjusted_score)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Input types
# ---------------------------------------------------------------------------


@dataclass
class LatencyObservation:
    """
    Observed latency percentiles in milliseconds.

    Attributes
    ----------
    p50, p95, p99:
        50th, 95th, and 99th percentile round-trip latencies in ms.
    """

    p50: float
    p95: float
    p99: float

    def weighted_ev(self) -> float:
        """
        Compute the weighted EV latency per the specification:

            EV = 0.2 * P50 + 0.3 * P95 + 0.5 * P99
        """
        return 0.2 * self.p50 + 0.3 * self.p95 + 0.5 * self.p99


# ---------------------------------------------------------------------------
# Scorer configuration
# ---------------------------------------------------------------------------


@dataclass
class ScorerConfig:
    """
    Configuration for a TV/EV scoring run.

    Attributes
    ----------
    tv_target:
        Target sustained throughput (trades/sec or orders/sec).
    ev_target_ms:
        Target maximum weighted latency in milliseconds.
    weight_tv, weight_ev:
        Composite score weights.  Must sum to 1.0.
    composite_method:
        ``"weighted_sum"`` (default, simple reporting) or
        ``"geometric"`` (recommended for certification — penalises weakness
        in either dimension more sharply).
    alpha:
        Exponent used in the hard-penalty EV scoring branch (1.25–2.0).
        Values above 1.0 make latency overruns degrade more sharply.
    use_ev_hard_penalty:
        When True, applies the exponential hard-penalty EV formula.
    """

    tv_target: float = 10_000.0       # trades/sec
    ev_target_ms: float = 5.0         # ms
    weight_tv: float = 0.50
    weight_ev: float = 0.50
    composite_method: str = "weighted_sum"   # "weighted_sum" | "geometric"
    alpha: float = 1.5
    use_ev_hard_penalty: bool = False

    def __post_init__(self) -> None:
        if not math.isclose(self.weight_tv + self.weight_ev, 1.0, rel_tol=1e-6):
            raise ValueError(
                f"weight_tv + weight_ev must equal 1.0, "
                f"got {self.weight_tv} + {self.weight_ev} = {self.weight_tv + self.weight_ev}"
            )
        if self.composite_method not in ("weighted_sum", "geometric"):
            raise ValueError(
                f"composite_method must be 'weighted_sum' or 'geometric', "
                f"got {self.composite_method!r}"
            )


# ---------------------------------------------------------------------------
# Scoring result
# ---------------------------------------------------------------------------


@dataclass
class TVEVResult:
    """
    Complete TV/EV scoring result.

    Attributes
    ----------
    tv_observed:
        Measured sustained throughput.
    ev_observed_ms:
        Weighted latency measure (EV_observed).
    tv_score, ev_score:
        Normalised 0–100 scores.
    raw_composite:
        Composite before reliability adjustment.
    reliability_multiplier:
        R = 1 - P (penalty factor).
    adjusted_score:
        Final score after reliability adjustment.
    grade:
        Letter grade (A+, A, A-, B+, … F).
    error_rate:
        Observed error rate used for the reliability multiplier.
    passed_gate:
        Whether the engine satisfies the minimum gate conditions.
    gate_message:
        Human-readable gate failure reason, or empty string if passed.
    """

    tv_observed: float
    ev_observed_ms: float
    tv_score: float
    ev_score: float
    raw_composite: float
    reliability_multiplier: float
    adjusted_score: float
    grade: str
    error_rate: float
    passed_gate: bool
    gate_message: str = ""

    def summary(self) -> str:
        """Return a compact one-line summary."""
        return (
            f"Grade={self.grade}  adjusted={self.adjusted_score:.2f}  "
            f"TV={self.tv_score:.1f}  EV={self.ev_score:.1f}  "
            f"R={self.reliability_multiplier:.3f}"
        )

    def report(self) -> str:
        """Return a multi-line certification-style report."""
        lines = [
            "TV/EV Scoring Report",
            "====================",
            f"  TV observed          : {self.tv_observed:.1f} trades/sec",
            f"  EV observed (wt.)    : {self.ev_observed_ms:.3f} ms",
            f"  TV score             : {self.tv_score:.2f}",
            f"  EV score             : {self.ev_score:.2f}",
            f"  Raw composite        : {self.raw_composite:.2f}",
            f"  Reliability mult.    : {self.reliability_multiplier:.4f}",
            f"  Adjusted score       : {self.adjusted_score:.2f}",
            f"  Final grade          : {self.grade}",
            f"  Error rate           : {self.error_rate:.4%}",
            f"  Gate passed          : {'YES' if self.passed_gate else 'NO'}",
        ]
        if self.gate_message:
            lines.append(f"  Gate message         : {self.gate_message}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Grade bands
# ---------------------------------------------------------------------------

_GRADE_BANDS = [
    (97.0, "A+"),
    (93.0, "A"),
    (90.0, "A-"),
    (87.0, "B+"),
    (83.0, "B"),
    (80.0, "B-"),
    (77.0, "C+"),
    (73.0, "C"),
    (70.0, "C-"),
    (60.0, "D"),
    (0.0,  "F"),
]


def _to_grade(score: float) -> str:
    """Map a numeric score to a letter grade."""
    for threshold, grade in _GRADE_BANDS:
        if score >= threshold:
            return grade
    return "F"


# ---------------------------------------------------------------------------
# Reliability penalty
# ---------------------------------------------------------------------------

_PENALTY_TABLE = [
    (0.0,    0.00),   # no errors
    (0.0001, 0.01),   # <0.01 %
    (0.0005, 0.03),   # 0.01–0.05 %
    (0.001,  0.07),   # 0.05–0.10 %
]
_CRITICAL_PENALTY = 0.20   # any critical state corruption


def _reliability_multiplier(error_rate: float, critical_error: bool = False) -> float:
    """
    Compute the reliability multiplier R = 1 - P.

    Automatic failure (returns 0.0) when ``critical_error`` is True.
    """
    if critical_error:
        return 0.0
    penalty = 0.07  # default for >0.10 %
    for threshold, p in _PENALTY_TABLE:      # iterate forward: smallest threshold first
        if error_rate <= threshold:
            penalty = p
            break
    return max(0.0, 1.0 - penalty)


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------


class TVEVScorer:
    """
    Compute TV/EV performance grades for trade engines.

    Implements the TV-EV Specification from ``TV-EV Specification.md``.

    Example
    -------
        scorer = TVEVScorer()
        result = scorer.score(
            tv_observed=9_200,
            latency=LatencyObservation(p50=2.5, p95=4.8, p99=6.2),
        )
        print(result.grade)
    """

    def __init__(self, config: Optional[ScorerConfig] = None) -> None:
        self.config: ScorerConfig = config or ScorerConfig()

    # ------------------------------------------------------------------
    # Individual component scores
    # ------------------------------------------------------------------

    def tv_score(self, tv_observed: float) -> float:
        """Compute normalised TV score (0–100)."""
        return min(100.0, 100.0 * tv_observed / self.config.tv_target)

    def ev_score(self, ev_observed_ms: float) -> float:
        """Compute normalised EV score (0–100) with optional hard penalty."""
        cfg = self.config
        if not cfg.use_ev_hard_penalty or ev_observed_ms <= cfg.ev_target_ms:
            return min(100.0, 100.0 * cfg.ev_target_ms / ev_observed_ms)
        # Hard-penalty branch
        return 100.0 * (cfg.ev_target_ms / ev_observed_ms) ** cfg.alpha

    # ------------------------------------------------------------------
    # Composite score
    # ------------------------------------------------------------------

    def composite_score(self, tv_s: float, ev_s: float) -> float:
        """Combine TV and EV scores according to the configured method."""
        cfg = self.config
        if cfg.composite_method == "geometric":
            return 100.0 * ((tv_s / 100.0) ** cfg.weight_tv) * ((ev_s / 100.0) ** cfg.weight_ev)
        return cfg.weight_tv * tv_s + cfg.weight_ev * ev_s

    # ------------------------------------------------------------------
    # Gate check
    # ------------------------------------------------------------------

    def _check_gates(self, tv_s: float, ev_s: float, raw: float) -> tuple:
        """
        Apply minimum gate thresholds.

        Returns ``(passed, message, clamped_grade_floor)``.
        """
        if tv_s < 70 or ev_s < 70:
            return False, f"TV_score={tv_s:.1f} or EV_score={ev_s:.1f} below minimum gate 70", "F"
        if raw >= 90 and (tv_s < 90 or ev_s < 90):
            msg = "A-range composite requires TV_score>=90 and EV_score>=90; downgraded to B+"
            return False, msg, "B+"
        if raw >= 80 and (tv_s < 80 or ev_s < 80):
            msg = "B-range composite requires TV_score>=80 and EV_score>=80; downgraded to C+"
            return False, msg, "C+"
        return True, "", ""

    # ------------------------------------------------------------------
    # Full scoring
    # ------------------------------------------------------------------

    def score(
        self,
        tv_observed: float,
        latency: LatencyObservation,
        error_rate: float = 0.0,
        critical_error: bool = False,
    ) -> TVEVResult:
        """
        Compute the full TV/EV score and grade.

        Parameters
        ----------
        tv_observed:
            Sustained measured throughput (same units as ``config.tv_target``).
        latency:
            Observed latency percentiles.
        error_rate:
            Fraction of transactions that resulted in an error (0.0–1.0).
        critical_error:
            Set True for any critical state corruption — forces automatic fail.

        Returns
        -------
        TVEVResult
        """
        ev_obs = latency.weighted_ev()
        tv_s = self.tv_score(tv_observed)
        ev_s = self.ev_score(ev_obs)
        composite = self.composite_score(tv_s, ev_s)
        r = _reliability_multiplier(error_rate, critical_error)
        adjusted = composite * r

        passed_gate, gate_msg, floor_grade = self._check_gates(tv_s, ev_s, composite)

        # Determine grade from adjusted score, then apply floor if gated
        grade = _to_grade(adjusted)
        if not passed_gate and floor_grade:
            grade = floor_grade

        return TVEVResult(
            tv_observed=tv_observed,
            ev_observed_ms=ev_obs,
            tv_score=round(tv_s, 4),
            ev_score=round(ev_s, 4),
            raw_composite=round(composite, 4),
            reliability_multiplier=round(r, 4),
            adjusted_score=round(adjusted, 4),
            grade=grade,
            error_rate=error_rate,
            passed_gate=passed_gate,
            gate_message=gate_msg,
        )
