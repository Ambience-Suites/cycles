# Ambience Suites Renderer

## [S1] Ambience Suites GUI Library Integration

This repository is the **Ambience Suites Renderer** rendering and animation component of the **Ambience Suites GUI Library** ecosystem — a broadcast-grade production platform for rendering technical and fundamental analysis visualisations powered by **1970ai**.

Ambience Suites Renderer data is packaged and distributed via **Content Data Serial Boxes** (Python-native format). See [Content_Data_Serial_Boxes.md](Content_Data_Serial_Boxes.md) for the full specification.

### [S1.1] Host / Client Architecture

```
  +-------------------------+     +-------------------------+
  |      HOST  NODE         |     |     CLIENT  NODE        |
  |                         |     |                         |
  |  +------------------+   |     |  +-----------------+    |
  |  | Ambience Suites  |   |     |  |  Display Layer  |    |
  |  | Renderer         |<------->|  | (consume boxes) |    |
  |  +--------+---------+   |     |  +--------+--------+    |
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

### [S1.2] Ambience Suites Folder Structure

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

### [S1.3] Serial Box Mapping

Ambience Suites Renderer assets map to Content Data Serial Boxes as follows:

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

### [S1.4] 1970ai — AI Component

```
  +-------------------------------+
  |  1 9 7 0 a i   +  AI Engine  |
  |  * Technical Analysis         |
  |  * Fundamental Analysis       |
  |  * Broadcast Signal Engine    |
  +-------------------------------+
```

**1970ai** is the official AI component of Ambience Suites. It drives broadcast-grade rendering decisions through real-time market signals:

**Technical indicators:** RSI · MACD · Bollinger Bands · VWAP · EMA crossover

**Fundamental factors:** P/E ratio · EPS growth · Revenue growth · Debt-to-equity

**Prompt feature stack (UI/UX LLM/SLM):**
- **Primary:** Billfold Technologies Ambience Suites
- **Additional 1970ai feature:** `Demonstock-Cinematic/Datos-Novelas-Technologies`

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

### [S1.5] TV/EV Performance Grading

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

### [S1.6] Permission Technology Rulesets (Content-Type Filtering)

Serial Box payloads now support a `permission_ruleset` that gates allowed
`content_type` values at schema-validation time.

Available rulesets:

- `default` (all standard content types)
- `billfold_primary_uiux_llm_slm`
- `datos_novelas_prompt_extension`

## [S2] Dependency Directory

### [S2.1] Core Build Dependencies

| Dependency | Type | Source |
|---|---|---|
| OpenImageIO | Required | [BUILDING.md](BUILDING.md) |
| TBB | Required | [BUILDING.md](BUILDING.md) |
| Alembic | Optional | [BUILDING.md](BUILDING.md) |
| Embree | Optional | [BUILDING.md](BUILDING.md) |
| OpenColorIO | Optional | [BUILDING.md](BUILDING.md) |
| OpenVDB / NanoVDB | Optional | [BUILDING.md](BUILDING.md) |
| OpenShadingLanguage | Optional | [BUILDING.md](BUILDING.md) |
| OpenImageDenoise | Optional | [BUILDING.md](BUILDING.md) |
| USD | Optional | [BUILDING.md](BUILDING.md) |

### [S2.2] Runtime / Platform Dependencies

| Dependency | Type | Source |
|---|---|---|
| OpenGL | GUI | [BUILDING.md](BUILDING.md) |
| GLEW | GUI | [BUILDING.md](BUILDING.md) |
| SDL | GUI | [BUILDING.md](BUILDING.md) |
| CUDA Toolkit 11+ | GPU (NVIDIA) | [BUILDING.md](BUILDING.md) |
| OptiX 7.3+ SDK | GPU (NVIDIA) | [BUILDING.md](BUILDING.md) |

### [S2.3] Python Tooling Dependencies

| Dependency | Used For | Source |
|---|---|---|
| PyYAML | Serial box generator | [`.github/workflows/ci.yaml`](.github/workflows/ci.yaml) |
| pyflakes | Python linting | [`.github/workflows/ci.yaml`](.github/workflows/ci.yaml) |
| pytest | TV/EV unit tests | [`.github/workflows/ci.yaml`](.github/workflows/ci.yaml) |

## [S3] Building

Ambience Suites Renderer can be built as a standalone application or a Hydra render delegate. See [BUILDING.md](BUILDING.md) for instructions.

CMake presets are available for common configurations:

```bash
cmake --preset release   # optimised standalone
cmake --preset debug     # debug + NaN detection
cmake --preset hydra     # Hydra render delegate
cmake --preset tests     # release + GTest suite
cmake --preset native    # native CPU only (development)
```

## [S4] Examples

The repository contains example XML scenes which can be used for testing.

```bash
./install/ambience-suites-renderer examples/scene_monkey.xml
./install/ambience-suites-renderer --samples 100 --output ./image.png examples/scene_monkey.xml
./install/ambience-suites-renderer --shadingsys osl examples/scene_osl_stripes.xml
```

## [S5] Contact

For help building or running Ambience Suites Renderer, see [BUILDING.md](BUILDING.md) and the repository issue tracker.
