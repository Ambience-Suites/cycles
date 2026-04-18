# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — Content Data Serial Boxes — Validator CLI
"""
Validator CLI for Content Data Serial Boxes.

Reads ``.py`` box files produced by the generator and validates them against
the Python-native schema (checksum, structure, dependency integrity).

Usage
-----
    python -m tools.serial_boxes.validator --help

    # Validate all boxes in the default directory
    python -m tools.serial_boxes.validator --boxes-dir ./serial_boxes

    # Validate specific files
    python -m tools.serial_boxes.validator path/to/box1.py path/to/box2.py

    # Strict mode: exit 1 on any validation error
    python -m tools.serial_boxes.validator --strict --boxes-dir ./serial_boxes
"""

from __future__ import annotations

import argparse
import ast
import glob
import hashlib
import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

from tools.serial_boxes.schema import (
    VALID_BOX_TYPES,
    VALID_CONTENT_TYPES,
    VALID_PERMISSION_RULESETS,
    VALID_COMPRESSION,
    _UUID4_RE,
    _SHA256_RE,
    _SEMVER_RE,
)


# ---------------------------------------------------------------------------
# Box loader
# ---------------------------------------------------------------------------


def load_box_file(file_path: str) -> Dict[str, Any]:
    """
    Load a ``.py`` box file and return the ``BOX`` dict.

    Box files contain a single ``BOX = { ... }`` assignment whose value is a
    Python literal (dict / list / str / int / float / bool / None).
    The value is parsed with ``ast.literal_eval`` to prevent arbitrary code
    execution when loading boxes from untrusted sources.

    Raises
    ------
    ValueError
        If the file does not define a valid ``BOX`` dict.
    """
    with open(file_path, encoding="utf-8") as fh:
        source = fh.read()

    # Extract the literal value assigned to BOX = ...
    # Accept lines like: BOX = {...}  (potentially multi-line)
    prefix = "BOX = "
    # Find the position of the assignment in the source
    idx = source.find(prefix)
    if idx == -1:
        raise ValueError(f"{file_path!r} does not contain a BOX assignment")
    literal_src = source[idx + len(prefix):]
    try:
        box = ast.literal_eval(literal_src)
    except (ValueError, SyntaxError) as exc:
        raise ValueError(f"{file_path!r}: cannot parse BOX value: {exc}") from exc
    if not isinstance(box, dict):
        raise ValueError(f"{file_path!r} does not define a valid BOX dict")
    return box


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _payload_checksum(payload: Dict[str, Any], include_permission_ruleset: bool = True) -> str:
    payload_copy: Dict[str, Any] = {
        "content_type": payload.get("content_type"),
        "data": payload.get("data"),
        "dependencies": payload.get("dependencies", []),
    }
    if include_permission_ruleset and "permission_ruleset" in payload:
        payload_copy["permission_ruleset"] = payload.get("permission_ruleset")
    return hashlib.sha256(
        json.dumps(payload_copy, sort_keys=True, ensure_ascii=True).encode()
    ).hexdigest()


def validate_box_dict(box: Dict[str, Any]) -> List[str]:
    """
    Validate a raw box dict and return a list of error strings.

    An empty list means the box is valid.
    """
    errors: List[str] = []

    # Required top-level keys
    for key in ("box_id", "version", "timestamp", "box_type", "metadata", "payload"):
        if key not in box:
            errors.append(f"missing required field: {key!r}")

    if errors:
        return errors  # structural errors prevent further checks

    # box_id
    if not _UUID4_RE.match(str(box.get("box_id", ""))):
        errors.append(f"box_id {box['box_id']!r} is not a valid UUID v4")

    # version
    if not _SEMVER_RE.match(str(box.get("version", ""))):
        errors.append(f"version {box['version']!r} is not semantic versioning (X.Y.Z)")

    # box_type
    if box.get("box_type") not in VALID_BOX_TYPES:
        errors.append(f"box_type {box.get('box_type')!r} must be one of {VALID_BOX_TYPES}")

    # metadata
    meta = box.get("metadata", {})
    if not isinstance(meta, dict):
        errors.append("metadata must be a dict")
    else:
        for mkey in ("source_repository", "generator", "checksum"):
            if not meta.get(mkey):
                errors.append(f"metadata.{mkey} must not be empty")
        if not _SHA256_RE.match(str(meta.get("checksum", ""))):
            errors.append("metadata.checksum is not a valid 64-char hex string")
        if meta.get("compression", "none") not in VALID_COMPRESSION:
            errors.append(
                f"metadata.compression {meta.get('compression')!r} "
                f"must be one of {VALID_COMPRESSION}"
            )

    # payload
    payload = box.get("payload", {})
    if not isinstance(payload, dict):
        errors.append("payload must be a dict")
    else:
        if payload.get("content_type") not in VALID_CONTENT_TYPES:
            errors.append(
                f"payload.content_type {payload.get('content_type')!r} "
                f"must be one of {VALID_CONTENT_TYPES}"
            )
        ruleset = payload.get("permission_ruleset", "default")
        if ruleset not in VALID_PERMISSION_RULESETS:
            errors.append(
                f"payload.permission_ruleset {ruleset!r} "
                f"must be one of {tuple(VALID_PERMISSION_RULESETS)}"
            )
        elif payload.get("content_type") not in VALID_PERMISSION_RULESETS[ruleset]:
            errors.append(
                f"payload.content_type {payload.get('content_type')!r} "
                f"is blocked by permission ruleset {ruleset!r}"
            )
        if not isinstance(payload.get("data"), dict):
            errors.append("payload.data must be a dict")

        # Checksum cross-check
        actual_checksum_with_ruleset = _payload_checksum(payload, include_permission_ruleset=True)
        actual_checksum_without_ruleset = _payload_checksum(payload, include_permission_ruleset=False)
        declared_checksum = meta.get("checksum", "") if isinstance(meta, dict) else ""
        if ruleset == "default":
            # Backwards compatibility:
            # Older boxes did not include permission_ruleset in payload checksums.
            checksum_matches = declared_checksum in {
                actual_checksum_with_ruleset,
                actual_checksum_without_ruleset,
            }
            checksum_report = (
                f"{actual_checksum_with_ruleset} (with permission_ruleset), "
                f"{actual_checksum_without_ruleset} (without permission_ruleset)"
            )
        else:
            checksum_matches = actual_checksum_with_ruleset == declared_checksum
            checksum_report = actual_checksum_with_ruleset
        if not checksum_matches:
            errors.append(
                f"checksum mismatch: declared={declared_checksum!r}, "
                f"computed={checksum_report!r}"
            )

    return errors


def validate_file(file_path: str) -> Tuple[bool, List[str]]:
    """
    Load and validate a single ``.py`` box file.

    Returns ``(is_valid, errors)``.
    """
    try:
        box = load_box_file(file_path)
    except Exception as exc:
        return False, [f"failed to load file: {exc}"]

    errors = validate_box_dict(box)
    return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate Content Data Serial Box .py files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="specific .py box files to validate (overrides --boxes-dir)",
    )
    parser.add_argument(
        "--boxes-dir",
        default="./serial_boxes",
        metavar="DIR",
        help="directory containing .py box files (default: ./serial_boxes)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit with code 1 if any box fails validation",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress per-box output; only print summary",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.files:
        targets = args.files
    else:
        targets = sorted(glob.glob(os.path.join(args.boxes_dir, "*.py")))

    if not targets:
        print("[validator] no box files found — nothing to validate.")
        return 0

    passed = 0
    failed = 0

    for file_path in targets:
        is_valid, errors = validate_file(file_path)
        if is_valid:
            passed += 1
            if not args.quiet:
                print(f"[validator] PASS  {file_path}")
        else:
            failed += 1
            print(f"[validator] FAIL  {file_path}")
            for err in errors:
                print(f"           - {err}")

    total = passed + failed
    print(f"\n[validator] {passed}/{total} box(es) passed validation.")

    if args.strict and failed > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
