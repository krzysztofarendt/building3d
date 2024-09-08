![Unit tests](https://github.com/krzysztofarendt/building3d/actions/workflows/unit_tests.yml/badge.svg)

# Building3D

I'm not sure where this project is heading, so there is no documentation yet, but it looks as follows:
<video src='https://github.com/user-attachments/assets/414a01c3-0274-4e7a-bf47-b1b1967a9b73'>

# Summary

- Polygon is a set of points
- Wall is a set of polygons
- Solid is a set of walls
- Zone is a set of solids
- Building is a set of zones
- Each object (polygon, wall, solid, zone, building) has a name
- Objects can be retrieved in two ways:
    - using path composed with object names, e.g. `building.get("building_name/zone_name/solid_name/wall_name/polygon_name")` to get a particular polygon
    - using square bracket operator, e.g. `building["solid_name"]["zone_name"]["solid_name"]` to get a particular solid

# Installation
```
python3.10 -m venv venv
source venv/bin/activate
pip install -e .[dev]
sudo apt install cloc  # for source code line counting
```

# Testing

Run unit tests:
```
make test
```

Produce a coverage report:
```
make coverage
```

# Examples

See the scripts in `examples/`.

# Roadmap

Loose ideas, to be or not to be implemented, in no particular order:

- Export to OBJ: https://fegemo.github.io/cefet-cg/attachments/obj-spec.pdf
- Polygon slice extrusion
- Predefined wedge geometry
- Ray-tracing for light
- Extend ray-tracing to sound (scattering, diffraction)
- Finite/Control Volume Method for energy simulation
- Export mesh to VTK format to enable convertions with meshio: https://vtk.org/wp-content/uploads/2015/04/file-formats.pdf

# Other projects I track

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

Commercial software:
- https://www.treble.tech/
- https://odeon.dk/
- https://www.dirac.com/live/

Might be useful for the validation of sound simulation:
- https://www.comsol.com/blogs/validating-an-acoustic-ray-tracing-simulation-of-a-chamber-music-hall
- Absorption coefficients: https://www.acoustic.ua/st/web_absorption_data_eng.pdf
