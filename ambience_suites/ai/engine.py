# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — 1970ai Engine
"""
1970ai — the official AI component of Ambience Suites.

The engine coordinates real-time and batch analysis pipelines (technical and
fundamental), manages data feeds, and emits signals that drive broadcast
rendering decisions in the Cycles pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional


# ---------------------------------------------------------------------------
# Signal types
# ---------------------------------------------------------------------------


@dataclass
class AnalysisSignal:
    """
    A signal emitted by the 1970ai engine.

    Attributes
    ----------
    symbol:
        Ticker symbol the signal refers to (e.g. ``"SPY"``).
    signal_type:
        One of ``"technical"``, ``"fundamental"``, or ``"composite"``.
    direction:
        ``"bullish"``, ``"bearish"``, or ``"neutral"``.
    strength:
        Normalised confidence 0.0–1.0.
    source:
        Name of the indicator / factor that generated the signal.
    timestamp:
        UTC ISO-8601 generation time.
    metadata:
        Arbitrary extra data (indicator values, ratios, etc.).
    """

    symbol: str
    signal_type: str
    direction: str
    strength: float
    source: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "signal_type": self.signal_type,
            "direction": self.direction,
            "strength": self.strength,
            "source": self.source,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# Engine configuration
# ---------------------------------------------------------------------------


@dataclass
class EngineConfig:
    """Configuration for the 1970ai engine."""

    name: str = "1970ai"
    version: str = "1.0.0"
    symbols: List[str] = field(default_factory=lambda: ["SPY", "QQQ", "BTCUSD"])
    technical_enabled: bool = True
    fundamental_enabled: bool = True
    composite_enabled: bool = True
    signal_history_size: int = 1000


# ---------------------------------------------------------------------------
# 1970ai Engine
# ---------------------------------------------------------------------------


class AI1970Engine:
    """
    1970ai broadcast-grade AI analysis engine.

    The engine accepts market data ticks, runs technical and fundamental
    analysis pipelines, and emits ``AnalysisSignal`` objects.  Registered
    callbacks receive signals synchronously so that they can drive broadcast
    rendering overlays in real time.

    Example
    -------
        from ambience_suites.ai.engine import AI1970Engine, EngineConfig
        from ambience_suites.ai.analysis import TechnicalAnalysis

        engine = AI1970Engine()
        engine.on_signal(lambda s: print(s.symbol, s.direction, s.strength))

        ta = TechnicalAnalysis(engine)
        ta.push_price("SPY", 450.25)
    """

    ENGINE_NAME = "1970ai"
    ENGINE_VERSION = "1.0.0"

    def __init__(self, config: Optional[EngineConfig] = None) -> None:
        self.config: EngineConfig = config or EngineConfig()
        self._signal_history: List[AnalysisSignal] = []
        self._callbacks: List[Callable[[AnalysisSignal], None]] = []

    # ------------------------------------------------------------------
    # Callback registration
    # ------------------------------------------------------------------

    def on_signal(self, callback: Callable[[AnalysisSignal], None]) -> None:
        """Register a callback that receives every emitted signal."""
        self._callbacks.append(callback)

    # ------------------------------------------------------------------
    # Signal emission
    # ------------------------------------------------------------------

    def emit(self, signal: AnalysisSignal) -> None:
        """
        Record a signal in the history buffer and notify all callbacks.

        The history buffer is capped at ``config.signal_history_size`` entries
        (oldest entries are discarded first).
        """
        self._signal_history.append(signal)
        if len(self._signal_history) > self.config.signal_history_size:
            self._signal_history.pop(0)

        for cb in self._callbacks:
            cb(signal)

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def latest_signal(self, symbol: str) -> Optional[AnalysisSignal]:
        """Return the most recent signal for the given symbol, or None."""
        for sig in reversed(self._signal_history):
            if sig.symbol == symbol:
                return sig
        return None

    def signals_for(self, symbol: str) -> List[AnalysisSignal]:
        """Return all recorded signals for the given symbol."""
        return [s for s in self._signal_history if s.symbol == symbol]

    def composite_direction(self, symbol: str) -> str:
        """
        Return a composite direction string for ``symbol`` based on the
        weighted average of all recent signal strengths.

        Returns ``"bullish"``, ``"bearish"``, or ``"neutral"``.
        """
        signals = self.signals_for(symbol)
        if not signals:
            return "neutral"

        score = 0.0
        for sig in signals:
            weight = sig.strength
            if sig.direction == "bullish":
                score += weight
            elif sig.direction == "bearish":
                score -= weight

        if score > 0.1:
            return "bullish"
        if score < -0.1:
            return "bearish"
        return "neutral"

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """Return a status dict for monitoring / Serial Box embedding."""
        return {
            "engine": self.ENGINE_NAME,
            "version": self.ENGINE_VERSION,
            "symbols": self.config.symbols,
            "signal_count": len(self._signal_history),
            "technical_enabled": self.config.technical_enabled,
            "fundamental_enabled": self.config.fundamental_enabled,
        }

    def __repr__(self) -> str:
        return (
            f"AI1970Engine(symbols={self.config.symbols}, "
            f"signals={len(self._signal_history)})"
        )
