Building Ambience Suites Renderer
=================================

Ambience Suites Renderer is the rendering and animation component of the Ambience Suites GUI Library. Build output (animation definitions, render configs, and frame state data) is packaged into **Content Data Serial Boxes** for distribution. See [Content_Data_Serial_Boxes.md](Content_Data_Serial_Boxes.md) for the serialization specification.

## Prerequisites

Ensure the following software is installed and available in the PATH:
- Git
- Git LFS
- Python 3
- CMake

### Standalone Build

Get the source code:

    git clone https://github.com/Ambience-Suites/Ambience-Suites-Renderer.git
    cd ambience-suites-renderer

Download precompiled libraries and build:

    make update
    make

The resulting binary will be at:

    ./install/ambience-suites-renderer

## Hydra Render Delegate with USD Repository

This will make the render delegate work with usdview and other applications built using the USD repository. USD version 24.03 or newer is required.

USD includes a script to build itself and all required dependencies and then install the result a specified directory.

    git clone https://github.com/PixarAnimationStudios/USD.git
    cd USD
    python3 build_scripts/build_usd.py "<path to USD install>"

Get the Ambience Suites Renderer source code:

    git clone https://github.com/Ambience-Suites/Ambience-Suites-Renderer.git
    cd ambience-suites-renderer

By default older precompiled libraries need to be used, for compatibility with older VFX platforms and TBB.
Download the libraries and build pointing to the USD directory like this.

    make update_legacy
    cmake -B ./build -DPXR_ROOT="<path to USD install>" -DWITH_LEGACY_LIBRARIES=ON
    make

When using a newer VFX platform and USD was built with `--onetbb`, do this instead:

    make update
    cmake -B ./build -DPXR_ROOT="<path to USD install>"
    make

Test in usdview.

    PYTHONPATH=<path to USD install>/lib/python PXR_PLUGINPATH_NAME=<path to ambience-suites-renderer>/install/hydra <path to USD install>/bin/usdview

## Hydra Render Delegate for Houdini

For use in Houdini, Ambience Suites Renderer must be built using Houdini's USD libraries. Houdini version 20 or newer is required.
Currently older libraries must be used for compatibility. Future Houdini versions will not need the legacy options.

Get the source code:

    git clone https://github.com/Ambience-Suites/Ambience-Suites-Renderer.git
    cd ambience-suites-renderer

Download precompiled libraries and build.

    make update_legacy
    cmake -B ./build -DHOUDINI_ROOT="<path to Houdini>" -DWITH_LEGACY_LIBRARIES=ON
    make

The path to Houdini depends on the operating system, typically:
- Linux: `/opt/hfsX.Y`
- macOS: `/Applications/Houdini/HoudiniX.Y.ZZZ`
- Windows: `C:/Program Files/Side Effects Software/Houdini X.Y.ZZZ`

Test in Houdini using an environment variable.

    PXR_PLUGINPATH_NAME=<path to ambience-suites-renderer>/install/houdini/dso/usd_plugins houdini

Or copy `install/houdini/packages/ambience-suites-renderer.json` to the Houdini packages directory to make it always available.

## Build System

Ambience Suites Renderer uses the CMake build system. As an alternative to the `make` wrapper, CMake can be manually configured.

See the CMake configuration to enable and disable various features.

The precompiled libraries are shared with Blender, and will be automatically downloaded from the Blender repository with `make update`. This will populate a submodule in the `lib/` folder, matching the platform.

## Dependencies

Core Ambience Suites Renderer has the following required and optional library dependencies. These are all included in precompiled libraries.

Required:
- OpenImageIO
- TBB

Optional:
- Alembic
- Embree
- OpenColorIO
- OpenVDB / NanoVDB
- OpenShadingLanguage
- OpenImageDenoise
- USD

For GUI support, the following libraries are required. The SDL library must be manually provided, it's not part of the precompiled libraries.
- OpenGL
- GLEW
- SDL

For GPU rendering support on NVIDIA cards, these need to be downloaded and installed from the NVIDIA website.
- CUDA Toolkit 11 or newer
- OptiX 7.3 SDK or newer
