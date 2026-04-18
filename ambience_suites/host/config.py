# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — Host Business Machine Configuration
"""
Host machine configuration expressed in Python (no JSON required).

All render, broadcast, and AI settings are typed Python dataclasses so they
can be imported, validated, and composed programmatically.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List


# ---------------------------------------------------------------------------
# Render settings
# ---------------------------------------------------------------------------


@dataclass
class RenderSettings:
    """Cycles render settings for the host broadcast node."""

    # Path-tracing quality
    samples: int = 512
    adaptive_sampling: bool = True
    adaptive_threshold: float = 0.01

    # Output
    output_dir: str = "./install/renders"
    output_format: str = "EXR"          # EXR for broadcast-grade production
    resolution_x: int = 3840            # 4K UHD default
    resolution_y: int = 2160
    fps: int = 30

    # GPU / device
    device: str = "GPU"                 # GPU, CPU, or OPTIX
    tile_size: int = 256

    # Denoising (OIDN) — essential for broadcast-grade stills
    use_denoising: bool = True
    denoising_prefilter: str = "ACCURATE"


# ---------------------------------------------------------------------------
# Broadcast pipeline settings
# ---------------------------------------------------------------------------


@dataclass
class BroadcastSettings:
    """Settings for the host broadcast pipeline."""

    # Serial box output
    serial_box_output_dir: str = "./serial_boxes"
    enable_compression: bool = True
    compression_algorithm: str = "gzip"  # gzip | brotli | none

    # Live streaming
    enable_live_stream: bool = False
    stream_endpoint: str = ""
    stream_protocol: str = "RTMP"        # RTMP | SRT | WebRTC

    # Frame packaging
    package_interval_frames: int = 1     # emit a box every N frames
    include_analysis_overlay: bool = True


# ---------------------------------------------------------------------------
# Analysis feed settings
# ---------------------------------------------------------------------------


@dataclass
class AnalysisFeedSettings:
    """Settings for the 1970ai data feed on the host node."""

    # Market data source
    data_source: str = "1970ai"
    symbols: List[str] = field(default_factory=lambda: ["SPY", "QQQ", "BTCUSD"])

    # Technical analysis indicators to compute and overlay
    enabled_indicators: List[str] = field(
        default_factory=lambda: ["RSI", "MACD", "BB", "VWAP", "EMA_20", "EMA_50"]
    )

    # Fundamental analysis refresh (seconds)
    fundamental_refresh_sec: int = 3600

    # TV/EV grading targets
    tv_target_trades_per_sec: float = 10_000.0
    ev_target_latency_ms: float = 5.0


# ---------------------------------------------------------------------------
# Top-level host configuration
# ---------------------------------------------------------------------------


@dataclass
class HostConfig:
    """
    Complete configuration for an Ambience Suites host business machine.

    Example
    -------
        from ambience_suites.host.config import HostConfig

        cfg = HostConfig(node_id="host-01", environment="production")
        print(cfg.render.resolution_x, cfg.render.device)
    """

    node_id: str = "host-01"
    environment: str = "production"       # production | staging | development
    node_role: str = "broadcast-master"

    render: RenderSettings = field(default_factory=RenderSettings)
    broadcast: BroadcastSettings = field(default_factory=BroadcastSettings)
    analysis: AnalysisFeedSettings = field(default_factory=AnalysisFeedSettings)

    # Paths
    cycles_binary: str = os.path.join(".", "install", "cycles")
    animations_dir: str = "./animations"
    render_config_module: str = "render_config"

    def summary(self) -> str:
        """Return a human-readable summary of this host configuration."""
        lines = [
            f"Ambience Suites — Host Config [{self.node_id}]",
            f"  Environment  : {self.environment}",
            f"  Role         : {self.node_role}",
            f"  Resolution   : {self.render.resolution_x}x{self.render.resolution_y}",
            f"  Device       : {self.render.device}",
            f"  Samples      : {self.render.samples}",
            f"  Symbols      : {', '.join(self.analysis.symbols)}",
            f"  Indicators   : {', '.join(self.analysis.enabled_indicators)}",
        ]
        return "\n".join(lines)
