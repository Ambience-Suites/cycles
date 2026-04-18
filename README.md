<!--
  Ambience Suites — Cycles Broadcast Production Platform
  Powered by 1970ai
-->

```
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
```

Cycles Renderer
===============

Cycles is a path tracing renderer focused on interactivity and ease of use, while supporting many production features.

https://www.cycles-renderer.org

## Ambience Suites GUI Library Integration

This repository is the **Cycles** rendering and animation component of the **Ambience Suites GUI Library** ecosystem — a broadcast-grade production platform for rendering technical and fundamental analysis visualisations powered by **1970ai**.

Cycles data is packaged and distributed via **Content Data Serial Boxes** (Python-native format).  See [Content_Data_Serial_Boxes.md](Content_Data_Serial_Boxes.md) for the full specification.

### Host / Client Architecture

```
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
             |  +--------+ +--------+ +--------+  |
             |  | content| | config | |  state |  |
             |  +--------+ +--------+ +--------+  |
             +-----------------------------------+
```

### Ambience Suites Folder Structure

```
ambience_suites/          Python package — host/client/AI components
  host/                   Host business machine (renderer + broadcast)
    config.py             Python dataclass configuration
    broadcast.py          Frame pipeline and Serial Box delivery
  client/                 Client business machine (display + analysis)
    config.py             Python dataclass configuration
    broadcast.py          Serial Box consumer and dispatch
  ai/                     1970ai — official AI component
    engine.py             Signal engine and emission bus
    analysis.py           Technical (RSI, MACD, BB, VWAP, EMA) and
                          fundamental (P/E, EPS, revenue, D/E) analysis

tools/
  serial_boxes/           Python-native Serial Box pipeline
    schema.py             Dataclass schema (replaces JSON schema)
    generator.py          Generator CLI
    validator.py          Validator CLI
  tvev/                   TV/EV performance grading
    scorer.py             Scorer (per TV-EV Specification.md)
    test_scorer.py        Unit tests

animations/               Animation cycle definitions (YAML → content boxes)
  fade_in.yaml
  fade_out.yaml

render_config.py          Render config expressed in Python (not JSON)
CMakePresets.json         Modern CMake build presets
```

### Serial Box Mapping

Cycles assets map to Content Data Serial Boxes as follows:

| Source | Box Type | Content Type |
|--------|----------|--------------|
| `animations/*.yaml` | `content` | `animation` |
| `render_config.py` | `config` | `style` |
| Frame state snapshots | `state` | `ui_component` |

Generate boxes:

```bash
python -m tools.serial_boxes.generator \
    --animations-dir ./animations \
    --render-config ./render_config.py \
    --output-dir ./serial_boxes
```

Validate boxes:

```bash
python -m tools.serial_boxes.validator --boxes-dir ./serial_boxes --strict
```

### 1970ai — AI Component

```
  +-------------------------------+
  |  1 9 7 0 a i   +  AI Engine  |
  |  * Technical Analysis         |
  |  * Fundamental Analysis       |
  |  * Broadcast Signal Engine    |
  +-------------------------------+
```

**1970ai** is the official AI component of Ambience Suites.  It drives
broadcast-grade rendering decisions through real-time market signals:

**Technical indicators:** RSI · MACD · Bollinger Bands · VWAP · EMA crossover

**Fundamental factors:** P/E ratio · EPS growth · Revenue growth · Debt-to-equity

```python
from ambience_suites.ai.engine import AI1970Engine
from ambience_suites.ai.analysis import TechnicalAnalysis, FundamentalAnalysis

engine = AI1970Engine()
engine.on_signal(lambda s: print(s.symbol, s.direction, s.strength))

ta = TechnicalAnalysis(engine)
for price in [440, 442, 441, 445, 448]:
    ta.push_price("SPY", price, volume=1_000_000)
signals = ta.compute("SPY")

fa = FundamentalAnalysis(engine)
fa.evaluate("AAPL", pe_ratio=28.5, eps_growth=0.12, revenue_growth=0.08)
```

### TV/EV Performance Grading

For trade engine performance grading and Beamology dashboard plotting guidance, see [TV-EV Specification](TV-EV%20Specification.md).

```
  TV/EV Grade Table
  -------------------------------------------------
  A+  97-100  Elite           Exceeds TV and EV
  A   93-97   Excellent       Very strong overall
  A-  90-93   High            Institutional-grade
  B+  87-90   Strong          Solid production
  B   83-87   Good            Meets standard
  -------------------------------------------------
```

Run the scorer:

```python
from tools.tvev.scorer import TVEVScorer, ScorerConfig, LatencyObservation

scorer = TVEVScorer(ScorerConfig(tv_target=10_000.0, ev_target_ms=5.0))
result = scorer.score(
    tv_observed=9_200.0,
    latency=LatencyObservation(p50=2.5, p95=4.8, p99=6.2),
    error_rate=0.00005,
)
print(result.report())
```

## Building

Cycles can be built as a standalone application or a Hydra render delegate. See [BUILDING.md](BUILDING.md) for instructions.

CMake presets are available for common configurations:

```bash
cmake --preset release   # optimised standalone
cmake --preset debug     # debug + NaN detection
cmake --preset hydra     # Hydra render delegate
cmake --preset tests     # release + GTest suite
cmake --preset native    # native CPU only (development)
```

## Examples

The repository contains example XML scenes which can be used for testing.

```bash
./cycles examples/scene_monkey.xml
./cycles --samples 100 --output ./image.png examples/scene_monkey.xml
./cycles --shadingsys osl examples/scene_osl_stripes.xml
```

## Contact

For help building or running Cycles, see the channels listed here:

https://www.cycles-renderer.org/development/

