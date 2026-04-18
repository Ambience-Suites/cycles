# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — Cycles Broadcast Production Platform
"""
Ambience Suites Python package.

Provides the host/client business-machine architecture, the 1970ai AI engine,
and all supporting utilities for broadcast-grade production rendering with
technical and fundamental analysis.

Quick start
-----------
    from ambience_suites import print_banner, __version__
    print_banner()
"""

from ambience_suites.banner import print_banner, print_arch, print_ai_badge, print_all

__version__ = "1.0.0"
__author__ = "Ambience Suites"
__license__ = "Apache-2.0"

__all__ = [
    "print_banner",
    "print_arch",
    "print_ai_badge",
    "print_all",
    "__version__",
]
