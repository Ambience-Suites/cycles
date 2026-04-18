# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — Client Business Machine Configuration
"""
Client machine configuration expressed in Python (no JSON required).

The client node consumes Content Data Serial Boxes produced by the host,
renders analysis overlays, and manages portfolio state.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# Display settings
# ---------------------------------------------------------------------------


@dataclass
class DisplaySettings:
    """Display and rendering settings for the client node."""

    monitor_resolution_x: int = 2560
    monitor_resolution_y: int = 1440
    color_profile: str = "sRGB"          # sRGB | DCI-P3 | Rec.709 | Rec.2020
    hdr_enabled: bool = False
    refresh_rate_hz: int = 60

    # Render playback
    playback_fps: int = 30
    loop_animation: bool = True


# ---------------------------------------------------------------------------
# Connection settings (connecting to the host broadcast stream)
# ---------------------------------------------------------------------------


@dataclass
class ConnectionSettings:
    """Settings for the client's connection to the host broadcast node."""

    host_address: str = "127.0.0.1"
    host_port: int = 9000
    protocol: str = "SRT"                # RTMP | SRT | WebRTC | local
    reconnect_attempts: int = 5
    reconnect_delay_sec: float = 2.0

    # Serial box inbox
    serial_box_inbox_dir: str = "./serial_boxes/inbox"
    auto_validate: bool = True


# ---------------------------------------------------------------------------
# Portfolio / analysis display settings
# ---------------------------------------------------------------------------


@dataclass
class PortfolioDisplaySettings:
    """Settings controlling how analysis overlays appear on the client."""

    show_technical_overlay: bool = True
    show_fundamental_overlay: bool = True
    overlay_opacity: float = 0.85

    # Indicators to show on-screen (subset of host's computed set)
    visible_indicators: List[str] = field(
        default_factory=lambda: ["RSI", "MACD", "BB", "VWAP"]
    )

    # Watchlist shown in the broadcast frame
    watchlist: List[str] = field(
        default_factory=lambda: ["SPY", "QQQ", "AAPL", "BTCUSD"]
    )

    # TV/EV grade display
    show_tvev_grade: bool = True


# ---------------------------------------------------------------------------
# Top-level client configuration
# ---------------------------------------------------------------------------


@dataclass
class ClientConfig:
    """
    Complete configuration for an Ambience Suites client business machine.

    Example
    -------
        from ambience_suites.client.config import ClientConfig

        cfg = ClientConfig(node_id="client-workstation-01")
        print(cfg.connection.host_address)
    """

    node_id: str = "client-01"
    environment: str = "production"
    node_role: str = "analyst-workstation"

    display: DisplaySettings = field(default_factory=DisplaySettings)
    connection: ConnectionSettings = field(default_factory=ConnectionSettings)
    portfolio: PortfolioDisplaySettings = field(default_factory=PortfolioDisplaySettings)

    def summary(self) -> str:
        """Return a human-readable summary of this client configuration."""
        lines = [
            f"Ambience Suites — Client Config [{self.node_id}]",
            f"  Environment  : {self.environment}",
            f"  Role         : {self.node_role}",
            f"  Host         : {self.connection.host_address}:{self.connection.host_port}",
            f"  Protocol     : {self.connection.protocol}",
            f"  Watchlist    : {', '.join(self.portfolio.watchlist)}",
            f"  Display Res  : {self.display.monitor_resolution_x}x{self.display.monitor_resolution_y}",
        ]
        return "\n".join(lines)
