# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — 1970ai Technical & Fundamental Analysis
"""
Technical and fundamental analysis for broadcast-grade production.

Both ``TechnicalAnalysis`` and ``FundamentalAnalysis`` are plugged into the
``AI1970Engine`` and emit ``AnalysisSignal`` objects that drive rendering
overlays in the Cycles broadcast pipeline.

Technical indicators implemented
---------------------------------
RSI, MACD (line + signal + histogram), Bollinger Bands, VWAP, EMA.

Fundamental factors implemented
--------------------------------
P/E ratio grading, EPS growth, revenue growth, debt-to-equity grading.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional

from ambience_suites.ai.engine import AI1970Engine, AnalysisSignal


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ema(values: List[float], period: int) -> List[float]:
    """Compute Exponential Moving Average over *values* with *period*."""
    if not values:
        return []
    k = 2.0 / (period + 1)
    result = [values[0]]
    for v in values[1:]:
        result.append(v * k + result[-1] * (1 - k))
    return result


def _sma(values: List[float], period: int) -> List[float]:
    """Compute Simple Moving Average."""
    return [
        sum(values[max(0, i - period + 1): i + 1]) / min(i + 1, period)
        for i in range(len(values))
    ]


def _stddev(values: List[float]) -> float:
    """Population standard deviation of *values*."""
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    return math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))


# ---------------------------------------------------------------------------
# Technical Analysis
# ---------------------------------------------------------------------------


class TechnicalAnalysis:
    """
    Broadcast-grade technical analysis using OHLCV price data.

    Feed prices via ``push_price`` and call ``compute`` to generate signals.
    Signals are emitted to the attached ``AI1970Engine``.

    Indicators
    ----------
    * **RSI** (14-period relative strength index)
    * **MACD** (12/26/9 exponential moving averages)
    * **Bollinger Bands** (20-period, 2σ)
    * **VWAP** (volume-weighted average price, intraday reset)
    * **EMA 20 / EMA 50** crossover

    Example
    -------
        from ambience_suites.ai.engine import AI1970Engine
        from ambience_suites.ai.analysis import TechnicalAnalysis

        engine = AI1970Engine()
        ta = TechnicalAnalysis(engine)

        for price in [440, 442, 441, 445, 448, 446]:
            ta.push_price("SPY", price, volume=1_000_000)

        signals = ta.compute("SPY")
    """

    RSI_PERIOD = 14
    MACD_FAST = 12
    MACD_SLOW = 26
    MACD_SIGNAL = 9
    BB_PERIOD = 20
    BB_STDDEV = 2.0
    EMA_SHORT = 20
    EMA_LONG = 50

    def __init__(self, engine: AI1970Engine) -> None:
        self.engine = engine
        # symbol -> (prices, volumes)
        self._prices: Dict[str, List[float]] = {}
        self._volumes: Dict[str, List[float]] = {}

    def push_price(self, symbol: str, price: float, volume: float = 0.0) -> None:
        """Append a new price (and optional volume) for *symbol*."""
        self._prices.setdefault(symbol, []).append(float(price))
        self._volumes.setdefault(symbol, []).append(float(volume))

    # ------------------------------------------------------------------
    # Individual indicator calculations
    # ------------------------------------------------------------------

    def rsi(self, symbol: str) -> Optional[float]:
        """Return the current RSI value (0–100) or None if insufficient data."""
        prices = self._prices.get(symbol, [])
        if len(prices) < self.RSI_PERIOD + 1:
            return None

        gains, losses = [], []
        for i in range(1, len(prices)):
            delta = prices[i] - prices[i - 1]
            gains.append(max(delta, 0.0))
            losses.append(max(-delta, 0.0))

        avg_gain = sum(gains[-self.RSI_PERIOD:]) / self.RSI_PERIOD
        avg_loss = sum(losses[-self.RSI_PERIOD:]) / self.RSI_PERIOD

        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100.0 - (100.0 / (1 + rs))

    def macd(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        Return ``{"macd": ..., "signal": ..., "histogram": ...}``
        or None if insufficient data.
        """
        prices = self._prices.get(symbol, [])
        if len(prices) < self.MACD_SLOW + self.MACD_SIGNAL:
            return None

        ema_fast = _ema(prices, self.MACD_FAST)
        ema_slow = _ema(prices, self.MACD_SLOW)
        macd_line = [f - s for f, s in zip(ema_fast, ema_slow)]
        signal_line = _ema(macd_line, self.MACD_SIGNAL)

        macd_val = macd_line[-1]
        sig_val = signal_line[-1]
        return {
            "macd": macd_val,
            "signal": sig_val,
            "histogram": macd_val - sig_val,
        }

    def bollinger_bands(self, symbol: str) -> Optional[Dict[str, float]]:
        """
        Return ``{"upper": ..., "middle": ..., "lower": ..., "pct_b": ...}``
        or None if insufficient data.
        """
        prices = self._prices.get(symbol, [])
        if len(prices) < self.BB_PERIOD:
            return None

        window = prices[-self.BB_PERIOD:]
        middle = sum(window) / self.BB_PERIOD
        sd = _stddev(window)
        upper = middle + self.BB_STDDEV * sd
        lower = middle - self.BB_STDDEV * sd
        pct_b = (prices[-1] - lower) / (upper - lower) if upper != lower else 0.5
        return {"upper": upper, "middle": middle, "lower": lower, "pct_b": pct_b}

    def vwap(self, symbol: str) -> Optional[float]:
        """Return VWAP for the current session or None if no volume data."""
        prices = self._prices.get(symbol, [])
        volumes = self._volumes.get(symbol, [])
        total_vol = sum(volumes)
        if total_vol == 0:
            return None
        return sum(p * v for p, v in zip(prices, volumes)) / total_vol

    def ema_crossover(self, symbol: str) -> Optional[str]:
        """
        Return ``"bullish"`` (short EMA > long EMA),
        ``"bearish"`` (short EMA < long EMA), or None if insufficient data.
        """
        prices = self._prices.get(symbol, [])
        if len(prices) < self.EMA_LONG:
            return None
        short_val = _ema(prices, self.EMA_SHORT)[-1]
        long_val = _ema(prices, self.EMA_LONG)[-1]
        return "bullish" if short_val > long_val else "bearish"

    # ------------------------------------------------------------------
    # Compute all signals
    # ------------------------------------------------------------------

    def compute(self, symbol: str) -> List[AnalysisSignal]:
        """
        Run all enabled indicators for *symbol* and emit signals to the engine.

        Returns the list of signals generated.
        """
        signals: List[AnalysisSignal] = []

        # RSI
        rsi_val = self.rsi(symbol)
        if rsi_val is not None:
            direction = "bearish" if rsi_val > 70 else ("bullish" if rsi_val < 30 else "neutral")
            strength = abs(rsi_val - 50) / 50.0
            sig = AnalysisSignal(
                symbol=symbol,
                signal_type="technical",
                direction=direction,
                strength=round(strength, 4),
                source="RSI",
                metadata={"rsi": round(rsi_val, 2)},
            )
            self.engine.emit(sig)
            signals.append(sig)

        # MACD
        macd_val = self.macd(symbol)
        if macd_val is not None:
            direction = "bullish" if macd_val["histogram"] > 0 else "bearish"
            strength = min(abs(macd_val["histogram"]) / (abs(macd_val["macd"]) + 1e-9), 1.0)
            sig = AnalysisSignal(
                symbol=symbol,
                signal_type="technical",
                direction=direction,
                strength=round(strength, 4),
                source="MACD",
                metadata={k: round(v, 4) for k, v in macd_val.items()},
            )
            self.engine.emit(sig)
            signals.append(sig)

        # Bollinger Bands
        bb = self.bollinger_bands(symbol)
        if bb is not None:
            pct_b = bb["pct_b"]
            if pct_b > 1.0:
                direction, strength = "bearish", min((pct_b - 1.0) * 2, 1.0)
            elif pct_b < 0.0:
                direction, strength = "bullish", min(-pct_b * 2, 1.0)
            else:
                direction, strength = "neutral", 0.0
            sig = AnalysisSignal(
                symbol=symbol,
                signal_type="technical",
                direction=direction,
                strength=round(strength, 4),
                source="BB",
                metadata={k: round(v, 4) for k, v in bb.items()},
            )
            self.engine.emit(sig)
            signals.append(sig)

        # EMA crossover
        cross = self.ema_crossover(symbol)
        if cross is not None:
            sig = AnalysisSignal(
                symbol=symbol,
                signal_type="technical",
                direction=cross,
                strength=0.6,
                source="EMA_CROSS",
                metadata={"short_period": self.EMA_SHORT, "long_period": self.EMA_LONG},
            )
            self.engine.emit(sig)
            signals.append(sig)

        return signals


# ---------------------------------------------------------------------------
# Fundamental Analysis
# ---------------------------------------------------------------------------


class FundamentalAnalysis:
    """
    Broadcast-grade fundamental analysis for equity instruments.

    Accepts key financial metrics and emits scored signals via the engine.

    Metrics evaluated
    -----------------
    * **P/E Ratio** — price-to-earnings grading
    * **EPS Growth** — year-over-year earnings growth
    * **Revenue Growth** — year-over-year revenue growth
    * **Debt-to-Equity** — leverage grading

    Example
    -------
        from ambience_suites.ai.engine import AI1970Engine
        from ambience_suites.ai.analysis import FundamentalAnalysis

        engine = AI1970Engine()
        fa = FundamentalAnalysis(engine)

        fa.evaluate("AAPL", pe_ratio=28.5, eps_growth=0.12,
                    revenue_growth=0.08, debt_to_equity=1.4)
    """

    def __init__(self, engine: AI1970Engine) -> None:
        self.engine = engine

    # ------------------------------------------------------------------
    # Grading helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _grade_pe(pe: float) -> tuple:
        """Return (direction, strength) for a P/E ratio."""
        if pe <= 0:
            return "bearish", 0.8          # negative earnings
        if pe < 15:
            return "bullish", 0.8          # value territory
        if pe < 25:
            return "bullish", 0.5          # fair value
        if pe < 35:
            return "neutral", 0.3
        return "bearish", 0.6              # expensive

    @staticmethod
    def _grade_growth(growth: float) -> tuple:
        """Return (direction, strength) for a growth rate (0–1 fraction)."""
        if growth > 0.20:
            return "bullish", 0.9
        if growth > 0.10:
            return "bullish", 0.7
        if growth > 0.00:
            return "bullish", 0.4
        if growth > -0.10:
            return "bearish", 0.4
        return "bearish", 0.8

    @staticmethod
    def _grade_dte(dte: float) -> tuple:
        """Return (direction, strength) for a debt-to-equity ratio."""
        if dte < 0.5:
            return "bullish", 0.7
        if dte < 1.5:
            return "neutral", 0.3
        if dte < 3.0:
            return "bearish", 0.5
        return "bearish", 0.85

    # ------------------------------------------------------------------
    # Evaluation entry point
    # ------------------------------------------------------------------

    def evaluate(
        self,
        symbol: str,
        pe_ratio: Optional[float] = None,
        eps_growth: Optional[float] = None,
        revenue_growth: Optional[float] = None,
        debt_to_equity: Optional[float] = None,
    ) -> List[AnalysisSignal]:
        """
        Evaluate available fundamental metrics for *symbol* and emit signals.

        All metric parameters are optional; only provided ones generate signals.

        Returns
        -------
        List[AnalysisSignal]
            Signals emitted during this evaluation.
        """
        signals: List[AnalysisSignal] = []

        if pe_ratio is not None:
            direction, strength = self._grade_pe(pe_ratio)
            sig = AnalysisSignal(
                symbol=symbol,
                signal_type="fundamental",
                direction=direction,
                strength=strength,
                source="PE_RATIO",
                metadata={"pe_ratio": pe_ratio},
            )
            self.engine.emit(sig)
            signals.append(sig)

        if eps_growth is not None:
            direction, strength = self._grade_growth(eps_growth)
            sig = AnalysisSignal(
                symbol=symbol,
                signal_type="fundamental",
                direction=direction,
                strength=strength,
                source="EPS_GROWTH",
                metadata={"eps_growth": eps_growth},
            )
            self.engine.emit(sig)
            signals.append(sig)

        if revenue_growth is not None:
            direction, strength = self._grade_growth(revenue_growth)
            sig = AnalysisSignal(
                symbol=symbol,
                signal_type="fundamental",
                direction=direction,
                strength=strength,
                source="REVENUE_GROWTH",
                metadata={"revenue_growth": revenue_growth},
            )
            self.engine.emit(sig)
            signals.append(sig)

        if debt_to_equity is not None:
            direction, strength = self._grade_dte(debt_to_equity)
            sig = AnalysisSignal(
                symbol=symbol,
                signal_type="fundamental",
                direction=direction,
                strength=strength,
                source="DEBT_TO_EQUITY",
                metadata={"debt_to_equity": debt_to_equity},
            )
            self.engine.emit(sig)
            signals.append(sig)

        return signals
