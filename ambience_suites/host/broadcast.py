# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — Host Broadcast Pipeline
"""
Host broadcast pipeline.

Drives the Cycles renderer, packages frames and analysis results into Content
Data Serial Boxes, and delivers them to connected client nodes.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ambience_suites.host.config import HostConfig


# ---------------------------------------------------------------------------
# Frame descriptor
# ---------------------------------------------------------------------------


class FrameDescriptor:
    """Represents a single rendered broadcast frame."""

    def __init__(self, frame_number: int, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        self.frame_number = frame_number
        self.file_path = file_path
        self.metadata: Dict[str, Any] = metadata or {}
        self.timestamp: str = datetime.now(timezone.utc).isoformat()

    def as_dict(self) -> Dict[str, Any]:
        return {
            "frame_number": self.frame_number,
            "file_path": self.file_path,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# Broadcast pipeline
# ---------------------------------------------------------------------------


class BroadcastPipeline:
    """
    Orchestrates the host broadcast pipeline.

    Responsibilities
    ----------------
    * Invoke the Cycles standalone binary for each frame / scene.
    * Package rendered frames and 1970ai analysis results into Serial Boxes.
    * Deliver boxes to the configured output directory.

    Example
    -------
        from ambience_suites.host.config import HostConfig
        from ambience_suites.host.broadcast import BroadcastPipeline

        cfg = HostConfig(node_id="host-01")
        pipeline = BroadcastPipeline(cfg)
        pipeline.render_scene("examples/scene_monkey.xml")
    """

    def __init__(self, config: HostConfig) -> None:
        self.config = config
        self._frame_log: List[FrameDescriptor] = []

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render_scene(self, scene_xml: str, extra_args: Optional[List[str]] = None) -> int:
        """
        Invoke the Cycles binary to render a scene.

        Parameters
        ----------
        scene_xml:
            Path to the XML scene file.
        extra_args:
            Additional command-line arguments forwarded to Cycles.

        Returns
        -------
        int
            Process return code (0 = success).
        """
        cmd: List[str] = [
            self.config.cycles_binary,
            "--samples", str(self.config.render.samples),
            "--output", self.config.render.output_dir,
        ]
        if extra_args:
            cmd.extend(extra_args)
        cmd.append(scene_xml)

        result = subprocess.run(cmd)
        return result.returncode

    # ------------------------------------------------------------------
    # Frame packaging
    # ------------------------------------------------------------------

    def package_frame(
        self,
        frame: FrameDescriptor,
        analysis_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Wrap a rendered frame (and optional analysis overlay) in a Serial Box.

        Returns a Python dict conforming to the Content Data Serial Box schema.
        """
        payload: Dict[str, Any] = {
            "content_type": "ui_component",
            "data": {
                "frame": frame.as_dict(),
                "analysis": analysis_data or {},
            },
            "dependencies": [],
        }

        checksum = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()

        box: Dict[str, Any] = {
            "box_id": str(uuid.uuid4()),
            "version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "box_type": "state",
            "metadata": {
                "source_repository": "Ambience-Suites/cycles",
                "generator": f"ambience_suites.host.broadcast/{self.config.node_id}",
                "checksum": checksum,
                "tags": ["broadcast", "frame", "cycles"],
                "compression": "none",
            },
            "payload": payload,
        }

        if self.config.broadcast.enable_compression:
            box["metadata"]["compression"] = self.config.broadcast.compression_algorithm

        self._frame_log.append(frame)
        return box

    # ------------------------------------------------------------------
    # Delivery
    # ------------------------------------------------------------------

    def deliver_box(self, box: Dict[str, Any]) -> str:
        """
        Write a Serial Box to the configured output directory.

        Returns
        -------
        str
            Full path of the written file.
        """
        out_dir = self.config.broadcast.serial_box_output_dir
        os.makedirs(out_dir, exist_ok=True)
        file_path = os.path.join(out_dir, f"{box['box_id']}.py")

        # Write as a Python literal (not JSON) for consistency with the
        # project-wide "Python formatting" convention.
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write("# Ambience Suites — Content Data Serial Box\n")
            fh.write("# Auto-generated by BroadcastPipeline\n\n")
            fh.write("BOX = ")
            fh.write(repr(box))
            fh.write("\n")

        return file_path

    # ------------------------------------------------------------------
    # Status helpers
    # ------------------------------------------------------------------

    def frame_count(self) -> int:
        """Return the number of frames processed in this pipeline session."""
        return len(self._frame_log)

    def __repr__(self) -> str:
        return (
            f"BroadcastPipeline(node={self.config.node_id!r}, "
            f"frames_processed={self.frame_count()})"
        )
