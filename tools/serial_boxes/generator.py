# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — Content Data Serial Boxes — Generator CLI
"""
Generator CLI for Content Data Serial Boxes.

Reads animation YAML files and the Python render config, and writes
``.py`` box files to an output directory.

Usage
-----
    python -m tools.serial_boxes.generator --help

    # Generate boxes from all animations and the render config
    python -m tools.serial_boxes.generator \\
        --animations-dir ./animations \\
        --render-config ./render_config.py \\
        --output-dir ./serial_boxes

    # Generate only animation boxes
    python -m tools.serial_boxes.generator --animations-dir ./animations
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from typing import Any, Dict, List, Optional

try:
    import yaml  # PyYAML
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

from tools.serial_boxes.schema import (
    make_content_box,
    make_config_box,
    SerialBox,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_box(box: SerialBox, output_dir: str) -> str:
    """Write *box* as a Python literal to *output_dir*/<box_id>.py."""
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{box.box_id}.py")
    with open(file_path, "w", encoding="utf-8") as fh:
        fh.write("# Ambience Suites — Content Data Serial Box\n")
        fh.write(f"# box_type : {box.box_type}\n")
        fh.write(f"# version  : {box.version}\n")
        fh.write(f"# timestamp: {box.timestamp}\n\n")
        fh.write("BOX = ")
        fh.write(repr(box.as_dict()))
        fh.write("\n")
    return file_path


def _load_yaml(file_path: str) -> Dict[str, Any]:
    if not _YAML_AVAILABLE:
        raise RuntimeError(
            "PyYAML is required for animation generation. "
            "Install it with:  pip install pyyaml"
        )
    with open(file_path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _load_render_config(module_path: str) -> Dict[str, Any]:
    """
    Import a Python render config module and extract ``RENDER_CONFIG`` dict.
    Falls back to reading ``render_config.py`` in the repository root.
    """
    spec = importlib.util.spec_from_file_location("render_config", module_path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"Cannot load render config from {module_path!r}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    cfg = getattr(mod, "RENDER_CONFIG", None)
    if cfg is None:
        raise AttributeError(f"{module_path!r} does not define RENDER_CONFIG")
    return cfg


# ---------------------------------------------------------------------------
# Generator
# ---------------------------------------------------------------------------


def generate_animation_boxes(
    animations_dir: str, output_dir: str
) -> List[str]:
    """
    Read all ``.yaml`` files in *animations_dir* and produce content boxes.

    Returns a list of written file paths.
    """
    written: List[str] = []
    if not os.path.isdir(animations_dir):
        print(f"[generator] animations directory not found: {animations_dir!r}", file=sys.stderr)
        return written

    for fname in sorted(os.listdir(animations_dir)):
        if not fname.endswith(".yaml") and not fname.endswith(".yml"):
            continue
        fpath = os.path.join(animations_dir, fname)
        data = _load_yaml(fpath)
        box = make_content_box(
            data=data,
            content_type="animation",
            tags=["animation", os.path.splitext(fname)[0]],
        )
        out = _write_box(box, output_dir)
        written.append(out)
        print(f"[generator] animation box: {fname!r} -> {out!r}")

    return written


def generate_config_box(render_config_path: str, output_dir: str) -> Optional[str]:
    """
    Read the Python render config and produce a config box.

    Returns the written file path or None on error.
    """
    try:
        data = _load_render_config(render_config_path)
    except (FileNotFoundError, AttributeError) as exc:
        print(f"[generator] skipping render config: {exc}", file=sys.stderr)
        return None

    box = make_config_box(
        data=data,
        content_type="style",
        tags=["render", "config"],
    )
    out = _write_box(box, output_dir)
    print(f"[generator] config box: {render_config_path!r} -> {out!r}")
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Content Data Serial Boxes from Cycles sources.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--animations-dir",
        default="./animations",
        metavar="DIR",
        help="directory containing animation *.yaml files (default: ./animations)",
    )
    parser.add_argument(
        "--render-config",
        default="./render_config.py",
        metavar="FILE",
        help="Python render config file (default: ./render_config.py)",
    )
    parser.add_argument(
        "--output-dir",
        default="./serial_boxes",
        metavar="DIR",
        help="output directory for generated .py box files (default: ./serial_boxes)",
    )
    parser.add_argument(
        "--skip-animations",
        action="store_true",
        help="skip animation box generation",
    )
    parser.add_argument(
        "--skip-config",
        action="store_true",
        help="skip render config box generation",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    written: List[str] = []

    if not args.skip_animations:
        written.extend(generate_animation_boxes(args.animations_dir, args.output_dir))

    if not args.skip_config:
        out = generate_config_box(args.render_config, args.output_dir)
        if out:
            written.append(out)

    print(f"[generator] done — {len(written)} box(es) written to {args.output_dir!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
