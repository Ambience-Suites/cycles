# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — Cycles Render Configuration (Python)
#
# This file defines the broadcast-grade render configuration for the Cycles
# path-tracing renderer.  It replaces a JSON config file: all settings are
# expressed as Python structures so they can be imported, validated, and
# composed programmatically.
#
# The ``RENDER_CONFIG`` dict is read by the Serial Box generator:
#
#     python -m tools.serial_boxes.generator --render-config ./render_config.py
#
# It is also consumed by the host broadcast pipeline:
#
#     from ambience_suites.host.config import HostConfig
#     cfg = HostConfig(render_config_module="render_config")

# ---------------------------------------------------------------------------
# Color management
# ---------------------------------------------------------------------------

COLOR_MANAGEMENT = {
    "display_device": "sRGB",
    "view_transform": "Filmic",     # perceptual, broadcast-standard
    "look": "None",
    "exposure": 0.0,
    "gamma": 1.0,
    "use_curve_mapping": False,
}

# ---------------------------------------------------------------------------
# Path tracing
# ---------------------------------------------------------------------------

PATH_TRACING = {
    "samples": 512,
    "adaptive_sampling": True,
    "adaptive_min_samples": 0,
    "adaptive_threshold": 0.01,
    "time_limit": 0,                # seconds; 0 = unlimited
    "seed": 0,
    "use_animated_seed": True,
    "denoising_enabled": True,
    "denoiser": "OPENIMAGEDENOISE",
    "denoising_prefilter": "ACCURATE",
    "denoising_input_passes": "RGB_ALBEDO_NORMAL",
}

# ---------------------------------------------------------------------------
# Render output
# ---------------------------------------------------------------------------

OUTPUT = {
    "file_format": "OPEN_EXR",              # broadcast-grade lossless
    "color_mode": "RGBA",
    "color_depth": "32",                    # full float
    "exr_codec": "DWAB",                    # lossy EXR codec for delivery
    "output_path": "./install/renders/",
    "use_render_cache": False,
}

# ---------------------------------------------------------------------------
# Resolution & camera
# ---------------------------------------------------------------------------

RESOLUTION = {
    "resolution_x": 3840,                  # 4K UHD
    "resolution_y": 2160,
    "resolution_percentage": 100,
    "pixel_aspect_x": 1.0,
    "pixel_aspect_y": 1.0,
    "fps": 30,
    "fps_base": 1.0,
}

# ---------------------------------------------------------------------------
# GPU / device selection
# ---------------------------------------------------------------------------

DEVICE = {
    "type": "GPU",                          # GPU | CPU | OPTIX
    "use_optix": True,
    "use_cuda": True,
    "use_hip": False,
    "use_oneapi": False,
    "use_metal": False,                     # macOS only
    "tile_size": 0,                         # 0 = auto
    "num_threads": 0,                       # 0 = auto
}

# ---------------------------------------------------------------------------
# Animation / broadcast timeline
# ---------------------------------------------------------------------------

ANIMATION = {
    "frame_start": 1,
    "frame_end": 250,
    "frame_step": 1,
    "use_frame_range": True,
}

# ---------------------------------------------------------------------------
# 1970ai analysis overlay render settings
# ---------------------------------------------------------------------------

AI_OVERLAY = {
    "enabled": True,
    "opacity": 0.85,
    "indicator_font_size": 18,             # pixels
    "indicator_color": (1.0, 0.9, 0.1),   # RGB 0–1 (broadcast yellow)
    "grade_badge_enabled": True,           # show TV/EV grade on frame
    "grade_badge_position": "bottom-right",
}

# ---------------------------------------------------------------------------
# Top-level config dict (consumed by the Serial Box generator)
# ---------------------------------------------------------------------------

RENDER_CONFIG = {
    "color_management": COLOR_MANAGEMENT,
    "path_tracing": PATH_TRACING,
    "output": OUTPUT,
    "resolution": RESOLUTION,
    "device": DEVICE,
    "animation": ANIMATION,
    "ai_overlay": AI_OVERLAY,
    "schema_version": "1.0.0",
    "platform": "Ambience Suites / Cycles Broadcast",
}


if __name__ == "__main__":
    import pprint
    print("Ambience Suites — Cycles Render Config")
    print("=" * 45)
    pprint.pprint(RENDER_CONFIG)
