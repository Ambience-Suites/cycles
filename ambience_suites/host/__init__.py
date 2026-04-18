# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — Host Business Machine
"""
Host node sub-package.

The host business machine runs the Cycles renderer, orchestrates the broadcast
pipeline, and drives the 1970ai analysis engine.  Rendered frames and analysis
results are serialised into Content Data Serial Boxes for delivery to client
nodes.
"""

from ambience_suites.host.config import HostConfig
from ambience_suites.host.broadcast import BroadcastPipeline

__all__ = ["HostConfig", "BroadcastPipeline"]
