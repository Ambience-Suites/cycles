# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — Client Broadcast Consumer
"""
Client broadcast consumer.

Watches the serial-box inbox, validates incoming boxes, and surfaces rendered
frames and 1970ai analysis results to the analyst workstation.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
from typing import Any, Callable, Dict, List

from ambience_suites.client.config import ClientConfig


# ---------------------------------------------------------------------------
# Box loader
# ---------------------------------------------------------------------------


def _load_box_file(file_path: str) -> Dict[str, Any]:
    """
    Load a Serial Box written as a Python literal.

    The file is expected to define a module-level ``BOX`` variable.
    """
    namespace: Dict[str, Any] = {}
    with open(file_path, encoding="utf-8") as fh:
        source = fh.read()

    # exec in a restricted namespace; only BOX is extracted
    exec(compile(source, file_path, "exec"), namespace)  # noqa: S102
    box = namespace.get("BOX")
    if not isinstance(box, dict):
        raise ValueError(f"File {file_path!r} does not define a valid BOX dict.")
    return box


# ---------------------------------------------------------------------------
# Broadcast consumer
# ---------------------------------------------------------------------------


class BroadcastConsumer:
    """
    Consumes Content Data Serial Boxes on the client business machine.

    Responsibilities
    ----------------
    * Poll the serial-box inbox directory for new ``.py`` box files.
    * Optionally validate checksum integrity.
    * Dispatch decoded frames and analysis payloads to registered callbacks.

    Example
    -------
        from ambience_suites.client.config import ClientConfig
        from ambience_suites.client.broadcast import BroadcastConsumer

        def on_frame(box):
            print("Received frame:", box["payload"]["data"]["frame"]["frame_number"])

        cfg = ClientConfig(node_id="client-01")
        consumer = BroadcastConsumer(cfg)
        consumer.on_frame_received(on_frame)
        consumer.poll_once()
    """

    def __init__(self, config: ClientConfig) -> None:
        self.config = config
        self._seen_ids: set = set()
        self._frame_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._analysis_callbacks: List[Callable[[Dict[str, Any]], None]] = []

    # ------------------------------------------------------------------
    # Callback registration
    # ------------------------------------------------------------------

    def on_frame_received(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback invoked with each received frame box."""
        self._frame_callbacks.append(callback)

    def on_analysis_received(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Register a callback invoked with each received analysis payload."""
        self._analysis_callbacks.append(callback)

    # ------------------------------------------------------------------
    # Polling
    # ------------------------------------------------------------------

    def poll_once(self) -> int:
        """
        Process all new ``.py`` box files in the inbox directory.

        Returns
        -------
        int
            Number of boxes processed in this poll cycle.
        """
        inbox = self.config.connection.serial_box_inbox_dir
        if not os.path.isdir(inbox):
            return 0

        processed = 0
        for file_path in sorted(glob.glob(os.path.join(inbox, "*.py"))):
            try:
                box = _load_box_file(file_path)
            except Exception:
                continue

            box_id = box.get("box_id", "")
            if box_id in self._seen_ids:
                continue

            if self.config.connection.auto_validate and not self._validate(box):
                continue

            self._seen_ids.add(box_id)
            self._dispatch(box)
            processed += 1

        return processed

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate(self, box: Dict[str, Any]) -> bool:
        """Return True if the box checksum matches the payload."""
        try:
            payload = box["payload"]
            expected = box["metadata"]["checksum"]
            actual = hashlib.sha256(
                json.dumps(payload, sort_keys=True).encode()
            ).hexdigest()
            return actual == expected
        except (KeyError, TypeError):
            return False

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def _dispatch(self, box: Dict[str, Any]) -> None:
        """Route a validated box to registered callbacks."""
        box_type = box.get("box_type", "")
        payload_data = box.get("payload", {}).get("data", {})

        if box_type == "state" and "frame" in payload_data:
            for cb in self._frame_callbacks:
                cb(box)

        if "analysis" in payload_data and payload_data["analysis"]:
            for cb in self._analysis_callbacks:
                cb(box)

    def __repr__(self) -> str:
        return (
            f"BroadcastConsumer(node={self.config.node_id!r}, "
            f"seen_boxes={len(self._seen_ids)})"
        )
