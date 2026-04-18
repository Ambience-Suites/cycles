Cycles Renderer
===============

Cycles is a path tracing renderer focused on interactivity and ease of use, while supporting many production features.

https://www.cycles-renderer.org

## Ambience Suites GUI Library Integration

This repository serves as the **Cycles** rendering and animation component of the Ambience Suites GUI Library ecosystem. Cycles data is packaged and distributed via **Content Data Serial Boxes** — see [Content_Data_Serial_Boxes.md](Content_Data_Serial_Boxes.md) for the full specification.

### Serial Box Mapping

Cycles assets map to Content Data Serial Boxes as follows:

| Source | Box Type | Content Type |
|--------|----------|--------------|
| `cycles/animations/*.yaml` | `content` | `animation` |
| `cycles/render_config.json` | `config` | `style` |
| Frame state snapshots | `state` | `ui_component` |

Animation cycle definitions produce **Content boxes**, rendering pipeline configurations produce **Config boxes**, and frame state data is captured in **State boxes**. Refer to the [Content Data Serial Boxes Specification](Content_Data_Serial_Boxes.md) for schema details, generation process, and integration guidelines.

For trade engine performance grading and Beamology dashboard plotting guidance, see [TV-EV Specification](TV-EV%20Specification.md).

## Building

Cycles can be built as a standalone application or a Hydra render delegate. See [BUILDING.md](BUILDING.md) for instructions.

## Examples

The repository contains example xml scenes which could be used for testing.

Example usage:

    ./cycles scene_monkey.xml

You can also use optional parameters (see `./cycles --help`), like:

    ./cycles --samples 100 --output ./image.png scene_monkey.xml

For the OSL scene you need to enable the OSL shading system:

    ./cycles --shadingsys osl scene_osl_stripes.xml

## Contact

For help building or running Cycles, see the channels listed here:

https://www.cycles-renderer.org/development/
