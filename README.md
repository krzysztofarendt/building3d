# building3d

I don't now where this project is heading, so there's no documentation yet.

# Installation
```
python3.10 -m venv venv
source venv/bin/activate
pip install -e .[dev]
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

# Example
```
python example.py
```

# TODO:

- [x] Check if all points of a wall are coplanar
- [x] Triangle area: https://en.wikipedia.org/wiki/Heron%27s_formula
- [x] Triangulation:
    - https://www.geometrictools.com/Documentation/TriangulationByEarClipping.pdf
    - https://nils-olovsson.se/articles/ear_clipping_triangulation/
- [x] Accurate center of weight for Wall
- [x] Tests are failing
- [x] Check whether a point lays on the surface of a polygon
- [x] Check whether a point is inside a Solid
- [x] Use mayavi instead of matplotlib: https://docs.enthought.com/mayavi/mayavi/index.html
- [ ] Delaunay triangulation of a polygon -> Polygon.delaunay_triangulation()
- [ ] Delaunay triangulation of a solid
- [ ] Calculate solid volume
- [ ] Accurate center of weight for Solid
