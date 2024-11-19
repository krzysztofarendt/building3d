![Unit tests](https://github.com/krzysztofarendt/building3d/actions/workflows/unit_tests.yml/badge.svg)

# Building3D

## About

The long-term goal for this project is to develop a unified environment for
simulation of various phenomena in buildings, including:
- sound propagation,
- heat and mass transfer,
- solar analysis,
- lighting analysis.

All of these simulation types require buildings to be represented as 3D polygons
so why not have a single tool for all of them?

I used to be working with some simulation software for these types of analyzes
and my impression was that the landscape is very scattered. Some tools have a
very inflexible design coming from their long history of development, some are
focused only on one aspect (e.g. only lighting, only sound) despite having many
things in common (e.g. both sound and lighting needs ray tracing). If these
tools have GUIs, they are mostly very old-fashioned. If they don't have any
GUI, you need to write the model in some very specific language/format you'll
need to learn just for this tool. And if you find a software suite allowing for
multiple types of analyzes, it probably means that other open source engines
are glued together through some difficult to maintain interface. Finally, a lot
of tools is proprietary.

I think it would be nice to have some common base code for these simulation types.
This base could cover:
- geometry definition,
- configuration format (setting simulation parameters),
- some template engines (e.g. ray tracing, heat transfer through solids).

For this base code to be adopted by others the following supplementary goals must be met:
- easy installation (basically `pip install`).
- as few dependencies as possible.

The goal I set is too ambitious for one person. More realistically, I will
focus on building the foundation and develop some simple demos for each
simulation type.

I chose Python because:
- it facilitates fast development (fact),
- as of 2024, it is the most popular programming language (fact),
- it is one of the languages increasingly being used by non-software engineers (opinion),
- it can be compiled to machine code and in many cases run as fast as C/C++ (fact),
- I know it well (opinion).

Please note that at the moment this is just my hobby project which I do in my
limited free time. Given the scope I set, there are high chances it will never
reach maturity. I will try to keep documented the modules I feel are already
useful.

Also, do not hesitate to contact me in case you have in mind some application
in which this project could be useful.

## Status

What's kind of ready:
- geometry definition,
- reading and writing to `STL`, `.bim`, and my custom format `b3d`,
- simple ray tracing.

What's next in the pipeline:
- sound propagation.

## Examples

Below are the examples of ray tracing simulations. They are not usable yet -
just looking pretty.

[Cubes](https://github.com/user-attachments/assets/414a01c3-0274-4e7a-bf47-b1b1967a9b73)

[Sphere](https://github.com/user-attachments/assets/ad794a12-441b-4a4d-a580-1953599535ac)

[Teapot](https://github.com/user-attachments/assets/3f305489-429d-47e7-977c-ca8724029371)

## Installation

Currently the package on PyPi is not kept up to date, so it's best
to clone this repository and install with `pip`:

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -e .[dev]
```

Optional dependencies:
```
sudo apt install cloc  # for source code line counting
```

## Testing

Please note that the package has been tested only on Linux!

Run unit tests:
```
make test
```

Produce a coverage report:
```
make coverage
```

## Documentation

Most of the modules are documented via docstrings.
There is no real documentation yet, because things are still moving fast.

Anyway, to give you some idea of the concept I used for the geometry definition,
here's the outline:
- Polygon is a collection of points,
- Wall is a collection of polygons,
- Solid is a collection of walls,
- Zone is a collection of solids,
- Building is a collection of zones.

Each object (polygon, wall, solid, zone, building) has a name which doesn't
have to be globally unique, but needs to be locally unique (e.g. 2 walls within
a single solid must have different names, but 2 walls from different solids can
be named same).

Objects can be accessed in two ways:
- using a path composed with object names, e.g.
  `building.get("building_name/zone_name/solid_name/wall_name/polygon_name")`
  to get a particular polygon,
- using the square bracket operator, e.g.
  `building["solid_name"]["zone_name"]["solid_name"]` to get a particular
  solid.

At the moment the geometry can be defined by:
- manual definition of points, polygons, walls, solids, zones,
- through convenience functions like `box()` and `floor_plan()` to create solids
- reading external geometry files (`STL`, `.bim`, `b3d`).

Please check out the example scripts in `examples/`.

Short script are better to be run without just-in-time compilation, e.g.:
```
NUMBA_DISABLE_JIT=1 python examples/building_example.py
```

However, simulations should be run with it (simply do not use `NUMBA_DISABLE_JIT=1`).
The compilation of all functions implemented for Numba may take up to 1-2 minutes.

---------------------------------

## My scratchpad

Loose ideas, to be or not to be implemented, in no particular order:
- Export to OBJ: https://fegemo.github.io/cefet-cg/attachments/obj-spec.pdf
- Polygon slice extrusion
- Predefined wedge geometry
- Ray-tracing for light
- Extend ray-tracing to sound (scattering, diffraction)
- Finite/Control Volume Method for energy simulation
- Export mesh to VTK format to enable convertions with meshio:
  https://vtk.org/wp-content/uploads/2015/04/file-formats.pdf

Other cool projects:
- https://github.com/LCAV/pyroomacoustics
- https://gitlab.com/drj11/pypng
- https://glumpy.github.io/index.html
- https://vispy.org/
- https://github.com/pygfx/pygfx
- https://github.com/Kitware/trame
- https://github.com/meshpro/pygalmesh
- https://github.com/nschloe/meshio
- https://reuk.github.io/wayverb/
- https://github.com/pvlib/pvlib-python/tree/main
- https://github.com/mmatl/pyrender
- https://www.mesh2hrtf.org/

Commercial software:
- https://www.treble.tech/
- https://odeon.dk/
- https://www.dirac.com/live/

Might be useful for the validation of sound simulation:
- https://www.comsol.com/blogs/validating-an-acoustic-ray-tracing-simulation-of-a-chamber-music-hall
- Absorption coefficients: https://www.acoustic.ua/st/web_absorption_data_eng.pdf
- https://depositonce.tu-berlin.de/items/38410727-febb-4769-8002-9c710ba393c4

Open datasets:
- (VCTK) Speech: https://datashare.ed.ac.uk/handle/10283/3443
- (MUSAN) Music, speech, noise: https://www.openslr.org/17/
