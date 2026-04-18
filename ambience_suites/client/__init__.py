# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — Client Business Machine
"""
Client node sub-package.

The client business machine consumes Content Data Serial Boxes produced by the
host, displays broadcast-grade renders, and surfaces technical / fundamental
analysis results for portfolio and trading workflows.
"""

from ambience_suites.client.config import ClientConfig
from ambience_suites.client.broadcast import BroadcastConsumer

__all__ = ["ClientConfig", "BroadcastConsumer"]
