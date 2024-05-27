![Unit tests](https://github.com/krzysztofarendt/building3d/actions/workflows/unit_tests.yml/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/krzysztofarendt/building3d/badge.svg)](https://coveralls.io/github/krzysztofarendt/building3d)

# building3d

I'm not sure where this project is heading, so there is not documentation yet, but it looks as follows:

![building3d_2024_04_21](https://github.com/krzysztofarendt/building3d/assets/16005748/1d81fe19-f07a-4087-b3d1-95dc0e2ed6cf)

# Assumptions

Geometry:
- a set of points defines a polygon
- a set of polygons defines a wall
- a set of walls defines a solid (3D space fully enclosed with polygons)
- a set of solids defines a zone
- a set of zones defines a building
- wall polygons do not have to be coplanar
- wall can have subpolygons (e.g. wall with a window)
- subpolygons do not have own meshes (yet)
- solids of a zone need to be adjacent
- but zones of a building do not need to be adjacent

Mesh:
- three types of meshes exist:
    - polygon triangulation generated by ear-clipping algorithm
    - surface mesh generated by Delaunay tesselation
    - volume mesh generated by Delaunay tesselation
- ear-clipping is used to triangulate polygons based on its vertices only
- Delaunay tesselation is used to make meshes with additional points suitable
  for numerical simulations (ray-tracing, Finite Volume Method)
- surface and volume meshes do not necessarily share their vertices (but
  mostly they do)
- volume meshes of adjacent solids do not necessarily share their vertices at
  the adjacent surfaces (but mostly they do)


# Installation
```
python3.10 -m venv venv
source venv/bin/activate
pip install -e .[dev]
sudo apt install cloc  # for source code line counting
```

If you see the following error when running `mayavi2`:
```
********************************************************************************
WARNING: Imported VTK version (9.3) does not match the one used
         to build the TVTK classes (9.2). This may cause problems.
         Please rebuild TVTK.
********************************************************************************
```
try updating `vtk` to the correct version:
```
pip install -U vtk==9.2
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
```
make example_1
make example_2
make example_3
```

# TODO:

- [x] Add predefined geometry: box
- [x] STL export/import
- [x] Try PyVista instead of mayavi2
- [x] Plot subpolygons
- [x] Building = set of zones
- [x] Read/write to .bim
- [x] Export/import to/from STL (and other formats?)
- [ ] Github Actions
- [ ] Model should be checking if all component names are unique (I removed name lists from Polygon and Solid)
- [ ] Figure out subpolygon meshing and general usage
- [ ] Own file format `*.b3d`
- [ ] `example_1` fails with `delta=0.5` and it takes 5 minutes to generate the mesh
- [ ] `Solid` should find polygons with reversed order of vertices and fix it
- [ ] Accurate center of weight for Solid (but is it even needed?)
- [ ] https://github.com/meshpro/pygalmesh
- [ ] https://github.com/nschloe/meshio
- [ ] `Polygon.__eq__()` can return wrong result for some non-convex polygons

Other cool projects:
- https://gitlab.com/drj11/pypng
- https://glumpy.github.io/index.html
- https://vispy.org/
- https://github.com/pygfx/pygfx
- https://github.com/Kitware/trame
