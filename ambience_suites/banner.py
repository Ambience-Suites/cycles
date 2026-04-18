# SPDX-License-Identifier: Apache-2.0
# Ambience Suites — Cycles Broadcast Production Platform
"""
Graphic banners, ASCII illustrations, and architecture diagrams for the
Ambience Suites / Cycles project.
"""

# ---------------------------------------------------------------------------
# Project banner
# ---------------------------------------------------------------------------

PROJECT_BANNER = r"""
+============================================================================+
|                                                                            |
|    ___  __  __ ___ ___ ___ _  _  ___ ___   ___ _   _ ___ _____ ___ ___   |
|   / _ \|  \/  | _ )_ _| __| \| |/ __| __| / __| | | |_ _|_   _| __/ __|  |
|  | (_) | |\/| | _ \| || _|| .` | (__| _|  \__ \ |_| || |  | | | _|\__ \  |
|   \__,_|_|  |_|___/___|___|_|\_|\___|___| |___/\___/|___| |_| |___|___/  |
|                                                                            |
|          B R O A D C A S T   P R O D U C T I O N   P L A T F O R M       |
|                       P o w e r e d   b y   1 9 7 0 a i                   |
|                                                                            |
|   * Broadcast-Grade Path Tracing        * Technical Analysis               |
|   * Fundamental Analysis                * Host / Client Architecture       |
|   * Content Data Serial Boxes           * TV/EV Performance Grading        |
|                                                                            |
+============================================================================+
"""

# ---------------------------------------------------------------------------
# Cycles renderer logo
# ---------------------------------------------------------------------------

CYCLES_LOGO = r"""
    _____           _
   / ____|         | |
  | |    _   _  ___| | ___  ___
  | |   | | | |/ __| |/ _ \/ __|
  | |___| |_| | (__| |  __/\__ \
   \_____\__, |\___|_|\___||___/
          __/ |
         |___/    Broadcast Renderer
"""

# ---------------------------------------------------------------------------
# 1970ai badge
# ---------------------------------------------------------------------------

AI_BADGE = r"""
  +-------------------------------+
  |  1 9 7 0 a i   +  AI Engine  |
  |  * Technical Analysis         |
  |  * Fundamental Analysis       |
  |  * Broadcast Signal Engine    |
  +-------------------------------+
"""

# ---------------------------------------------------------------------------
# Host / Client architecture diagram
# ---------------------------------------------------------------------------

AMBIENCE_SUITES_ARCH = r"""
  Ambience Suites -- Host / Client Architecture
  -----------------------------------------------

  +-------------------------+     +-------------------------+
  |      HOST  NODE         |     |     CLIENT  NODE        |
  |                         |     |                         |
  |  +-----------------+    |     |  +-----------------+    |
  |  | Cycles Renderer |    |     |  |  Display Layer  |    |
  |  | (path tracing)  |<------->|  | (consume boxes) |    |
  |  +--------+--------+    |     |  +--------+--------+    |
  |           |             |     |           |             |
  |  +--------v--------+    |     |  +--------v--------+    |
  |  | Broadcast Engine|    |     |  | Analysis Client |    |
  |  | (frame pipeline)|    |     |  | (tech + fund.)  |    |
  |  +--------+--------+    |     |  +--------+--------+    |
  |           |             |     |           |             |
  |  +--------v--------+    |     |  +--------v--------+    |
  |  |   1 9 7 0 a i   |    |     |  | Portfolio Layer |    |
  |  | (AI / signals)  |    |     |  | (state tracking)|    |
  |  +-----------------+    |     |  +-----------------+    |
  +----------+--------------+     +------------+------------+
             |                                 |
             +-----------------+---------------+
                               |
             +-----------------v-----------------+
             |   Content Data Serial Boxes        |
             |                                   |
             |  +--------+ +--------+            |
             |  | content| | config |            |
             |  +--------+ +--------+            |
             |  +--------+                       |
             |  |  state |                       |
             |  +--------+                       |
             +-----------------------------------+
"""

# ---------------------------------------------------------------------------
# TV/EV grade table illustration
# ---------------------------------------------------------------------------

TVEV_GRADE_TABLE = r"""
  TV/EV Performance Grade Table
  -------------------------------------------------------
  Grade | Score   | Classification  | Interpretation
  ------+---------+-----------------+------------------
  A+    | 97-100  | Elite           | Exceeds TV and EV
  A     | 93-97   | Excellent       | Very strong overall
  A-    | 90-93   | High            | Institutional-grade
  B+    | 87-90   | Strong          | Solid production
  B     | 83-87   | Good            | Meets standard
  B-    | 80-83   | Acceptable      | Limited headroom
  C+    | 77-80   | Marginal+       | Below benchmark
  C     | 73-77   | Marginal        | Non-demanding only
  C-    | 70-73   | Weak            | Significant limits
  D     | 60-70   | Poor            | Fails commercial
  F     | <60     | Unacceptable    | Fails specification
  -------------------------------------------------------
"""

# ---------------------------------------------------------------------------
# Serial box pipeline illustration
# ---------------------------------------------------------------------------

SERIAL_BOX_PIPELINE = r"""
  Content Data Serial Box Pipeline
  -----------------------------------------------------------------

   animations/*.yaml --+
   render_config.py ---+--> [ Generator ] --> [ Validator ] --> Box Store
   frame snapshots ----+         |                  |
                                 |                  |
                          UUID + checksum    schema + deps
                          SHA-256 payload    integrity check
  -----------------------------------------------------------------
"""


def print_banner() -> None:
    """Print the full Ambience Suites project banner."""
    print(PROJECT_BANNER)


def print_arch() -> None:
    """Print the host/client architecture diagram."""
    print(AMBIENCE_SUITES_ARCH)


def print_ai_badge() -> None:
    """Print the 1970ai badge."""
    print(AI_BADGE)


def print_all() -> None:
    """Print all banners and diagrams."""
    print(PROJECT_BANNER)
    print(AI_BADGE)
    print(AMBIENCE_SUITES_ARCH)
    print(SERIAL_BOX_PIPELINE)
    print(TVEV_GRADE_TABLE)


if __name__ == "__main__":
    print_all()
