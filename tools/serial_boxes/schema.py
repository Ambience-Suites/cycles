# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — Content Data Serial Boxes — Python Schema
"""
Python-native schema for Content Data Serial Boxes.

All types are expressed as Python dataclasses — no JSON Schema required.
The dataclasses serve as both documentation and runtime validation targets.

Box Types
---------
* ``ContentBox``  — animation cycle definitions, UI components
* ``ConfigBox``   — render configs, style / theme settings
* ``StateBox``    — frame state snapshots, portfolio state
"""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_BOX_TYPES = ("content", "state", "config")
VALID_CONTENT_TYPES = ("ui_component", "narrative", "style", "layout", "animation")
VALID_PERMISSION_RULESETS = {
    "default": VALID_CONTENT_TYPES,
    "billfold_primary_uiux_llm_slm": VALID_CONTENT_TYPES,
    "datos_novelas_prompt_extension": ("ui_component", "layout", "narrative"),
}
VALID_COMPRESSION = ("none", "gzip", "brotli")
BOX_FORMAT_VERSION = "1.0.0"

_UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
)
_SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


# ---------------------------------------------------------------------------
# Dependency descriptor
# ---------------------------------------------------------------------------


@dataclass
class BoxDependency:
    """A reference to another Serial Box required by this one."""

    box_id: str
    box_type: str
    version: str
    required: bool = True

    def validate(self) -> List[str]:
        errors: List[str] = []
        if not _UUID4_RE.match(self.box_id):
            errors.append(f"dependency box_id {self.box_id!r} is not a valid UUID v4")
        if self.box_type not in VALID_BOX_TYPES:
            errors.append(f"dependency box_type {self.box_type!r} is invalid")
        if not _SEMVER_RE.match(self.version):
            errors.append(f"dependency version {self.version!r} is not semantic versioning")
        return errors


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------


@dataclass
class BoxMetadata:
    """Metadata block attached to every Serial Box."""

    source_repository: str
    generator: str
    checksum: str                                  # SHA-256 hex of payload JSON
    tags: List[str] = field(default_factory=list)
    compression: str = "none"

    def validate(self) -> List[str]:
        errors: List[str] = []
        if not self.source_repository:
            errors.append("metadata.source_repository must not be empty")
        if not self.generator:
            errors.append("metadata.generator must not be empty")
        if not _SHA256_RE.match(self.checksum):
            errors.append(f"metadata.checksum {self.checksum!r} is not a valid SHA-256 hex")
        if self.compression not in VALID_COMPRESSION:
            errors.append(
                f"metadata.compression {self.compression!r} must be one of {VALID_COMPRESSION}"
            )
        return errors


# ---------------------------------------------------------------------------
# Payload
# ---------------------------------------------------------------------------


@dataclass
class BoxPayload:
    """Payload block of a Serial Box."""

    content_type: str
    data: Dict[str, Any]
    dependencies: List[BoxDependency] = field(default_factory=list)
    permission_ruleset: str = "default"

    def validate(self) -> List[str]:
        errors: List[str] = []
        if self.content_type not in VALID_CONTENT_TYPES:
            errors.append(
                f"payload.content_type {self.content_type!r} must be one of {VALID_CONTENT_TYPES}"
            )
        if self.permission_ruleset not in VALID_PERMISSION_RULESETS:
            errors.append(
                f"payload.permission_ruleset {self.permission_ruleset!r} "
                f"must be one of {tuple(VALID_PERMISSION_RULESETS)}"
            )
        elif self.content_type not in VALID_PERMISSION_RULESETS[self.permission_ruleset]:
            errors.append(
                f"payload.content_type {self.content_type!r} is blocked by "
                f"permission ruleset {self.permission_ruleset!r}"
            )
        if not isinstance(self.data, dict):
            errors.append("payload.data must be a dict")
        for dep in self.dependencies:
            errors.extend(dep.validate())
        return errors

    def checksum(self) -> str:
        """
        Compute the SHA-256 checksum of this payload.

        Note: ``permission_ruleset`` is serialized only when not ``"default"``,
        so legacy payloads and default-ruleset payloads keep stable checksums.
        """
        serialised = json.dumps(self.as_dict(), sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(serialised.encode()).hexdigest()

    def as_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "content_type": self.content_type,
            "data": self.data,
            "dependencies": [
                {
                    "box_id": d.box_id,
                    "type": d.box_type,
                    "version": d.version,
                    "required": d.required,
                }
                for d in self.dependencies
            ],
        }
        if self.permission_ruleset != "default":
            payload["permission_ruleset"] = self.permission_ruleset
        return payload


# ---------------------------------------------------------------------------
# Serial Box (base)
# ---------------------------------------------------------------------------


@dataclass
class SerialBox:
    """
    Content Data Serial Box — base dataclass.

    Do not instantiate directly; use ``ContentBox``, ``ConfigBox``, or
    ``StateBox`` (or the ``make_*`` factory functions below).

    Fields
    ------
    box_id:
        UUID v4 unique identifier.
    version:
        Semantic version string of the box format.
    timestamp:
        UTC ISO-8601 creation time.
    box_type:
        One of ``"content"``, ``"state"``, ``"config"``.
    metadata:
        ``BoxMetadata`` instance.
    payload:
        ``BoxPayload`` instance.
    signature:
        Optional cryptographic signature for authenticity.
    """

    box_id: str
    version: str
    timestamp: str
    box_type: str
    metadata: BoxMetadata
    payload: BoxPayload
    signature: Optional[str] = None

    def validate(self) -> List[str]:
        """
        Validate the box structure.

        Returns a list of error strings; an empty list means the box is valid.
        """
        errors: List[str] = []

        if not _UUID4_RE.match(self.box_id):
            errors.append(f"box_id {self.box_id!r} is not a valid UUID v4")
        if not _SEMVER_RE.match(self.version):
            errors.append(f"version {self.version!r} is not semantic versioning")
        if self.box_type not in VALID_BOX_TYPES:
            errors.append(f"box_type {self.box_type!r} must be one of {VALID_BOX_TYPES}")

        errors.extend(self.metadata.validate())
        errors.extend(self.payload.validate())

        # Checksum cross-check
        expected = self.payload.checksum()
        if self.metadata.checksum != expected:
            errors.append(
                f"checksum mismatch: metadata has {self.metadata.checksum!r} "
                f"but payload hashes to {expected!r}"
            )

        return errors

    def is_valid(self) -> bool:
        return len(self.validate()) == 0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "box_id": self.box_id,
            "version": self.version,
            "timestamp": self.timestamp,
            "box_type": self.box_type,
            "metadata": {
                "source_repository": self.metadata.source_repository,
                "generator": self.metadata.generator,
                "checksum": self.metadata.checksum,
                "tags": self.metadata.tags,
                "compression": self.metadata.compression,
            },
            "payload": self.payload.as_dict(),
            "signature": self.signature,
        }


# ---------------------------------------------------------------------------
# Typed sub-classes
# ---------------------------------------------------------------------------


@dataclass
class ContentBox(SerialBox):
    """
    Content box — animation cycle definitions, UI components, narratives.

    Produced from ``animations/*.yaml`` and rendered output.
    """


@dataclass
class ConfigBox(SerialBox):
    """
    Config box — render pipeline settings, style / theme data.

    Produced from ``render_config.py``.
    """


@dataclass
class StateBox(SerialBox):
    """
    State box — frame state snapshots, portfolio state.

    Produced by the broadcast pipeline on each rendered frame.
    """


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------


def _make_box(
    box_type: str,
    content_type: str,
    data: Dict[str, Any],
    source_repository: str = "Ambience-Suites/cycles",
    generator: str = "ambience_suites.tools.serial_boxes",
    tags: Optional[List[str]] = None,
    compression: str = "none",
    dependencies: Optional[List[BoxDependency]] = None,
    permission_ruleset: str = "default",
) -> SerialBox:
    payload = BoxPayload(
        content_type=content_type,
        data=data,
        dependencies=dependencies or [],
        permission_ruleset=permission_ruleset,
    )
    checksum = payload.checksum()
    metadata = BoxMetadata(
        source_repository=source_repository,
        generator=generator,
        checksum=checksum,
        tags=tags or [],
        compression=compression,
    )
    cls = {"content": ContentBox, "config": ConfigBox, "state": StateBox}.get(
        box_type, SerialBox
    )
    return cls(
        box_id=str(uuid.uuid4()),
        version=BOX_FORMAT_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        box_type=box_type,
        metadata=metadata,
        payload=payload,
    )


def make_content_box(
    data: Dict[str, Any],
    content_type: str = "animation",
    **kwargs: Any,
) -> ContentBox:
    """Create a ``ContentBox`` for animation / UI component data."""
    return _make_box("content", content_type, data, **kwargs)  # type: ignore[return-value]


def make_config_box(
    data: Dict[str, Any],
    content_type: str = "style",
    **kwargs: Any,
) -> ConfigBox:
    """Create a ``ConfigBox`` for render config / style data."""
    return _make_box("config", content_type, data, **kwargs)  # type: ignore[return-value]


def make_state_box(
    data: Dict[str, Any],
    content_type: str = "ui_component",
    **kwargs: Any,
) -> StateBox:
    """Create a ``StateBox`` for frame state / portfolio state data."""
    return _make_box("state", content_type, data, **kwargs)  # type: ignore[return-value]
