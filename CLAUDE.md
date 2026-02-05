# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Test Commands

```bash
uv sync                                    # Install dependencies
uv run make format                         # Format code (black + isort)
uv run make test                           # Run tests (with and without JIT)
uv run make coverage                       # Coverage report

# Run specific test file
NUMBA_DISABLE_JIT=1 uv run pytest tests/geom/test_polygon.py -v

# Run examples (short scripts work without JIT)
NUMBA_DISABLE_JIT=1 uv run python examples/building_example.py
uv run python examples/ray_2_boxes.py      # Full JIT (1-2 min compile time)
```

## Architecture

Building3D is a framework for 3D building modeling and simulation. The core is a hierarchical geometry model:

**Building → Zone → Solid → Wall → Polygon**

- **Polygon**: Base unit - 2D area in 3D space defined by points, auto-triangulated via ear-clipping
- **Wall**: Collection of polygons (don't need to be coplanar)
- **Solid**: Enclosed volume from walls, provides volume/containment calculations
- **Zone**: Groups solids (organizational)
- **Building**: Top-level container with spatial adjacency graph

All objects have `name` (locally unique), `uid` (globally unique), `parent`, `children`, `path` properties. Access via path (`building.get("zone/solid/wall/polygon")`) or brackets (`building["zone"]["solid"]`).

## Key Modules

- `building3d/geom/` - Geometry: points, polygons, walls, solids, zones, buildings
- `building3d/sim/rays/` - Ray tracing simulation (Numba JIT-compiled)
- `building3d/io/` - File I/O: STL, .bim, b3d formats
- `building3d/display/` - PyVista-based 3D visualization
- `building3d/config.py` - Global tolerances and settings

## Critical Technical Notes

**Always use float64**: The codebase uses `np.float64` throughout. Never use float32.

**Numba JIT**: Performance-critical code in `sim/rays/` uses Numba. Tests run twice (JIT on/off) because JIT can hide bugs. First run takes 1-2 minutes to compile.

**Array format for simulation**: Building hierarchies must be converted to flat numpy arrays via `building3d/io/arrayformat.py` for Numba compatibility.

**Type definitions** in `building3d/geom/types.py`:
```python
PointType = NDArray[FLOAT]   # Shape (N, 3) or (3,)
VectorType = NDArray[FLOAT]  # Shape (N, 3) or (3,)
IndexType = NDArray[INT]     # Face indices
```

**Polygon normal**: Calculated from first 3 points. If first corner is non-convex, pass normal explicitly.

**Geometry tolerances**: `GEOM_ATOL = 1e-13`, `GEOM_RTOL = 1e-6` (from config.py)

## Code Style

- Black formatting with 100-character line length
- isort for imports (single-line mode)
- Run `uv run make format` before committing
