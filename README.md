# building3d

I don't now where this project is heading, so there's no documentation yet.

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

# Example
```
make example
```

# TODO:

- [x] Check if all points of a wall are coplanar
- [x] Triangle area: https://en.wikipedia.org/wiki/Heron%27s_formula
- [x] Triangulation:
- [x] Accurate center of weight for Wall
- [x] Tests are failing
- [x] Check whether a point lays on the surface of a polygon
- [x] Check whether a point is inside a Solid
- [x] Use mayavi instead of matplotlib: https://docs.enthought.com/mayavi/mayavi/index.html
- [x] Delaunay triangulation of a polygon -> Polygon.delaunay_triangulation()
- [x] Pretty mesh rendering
- [x] Mesh points on the edges should be shared across all connected polygons
- [x] one config
- [x] Mesh face polygons should have the same surface normals as the polygon
- [x] Add to PyPi to reserve the name
- [x] Discretize solid with tetrahedra (the mesh does not look correct)
- [x] Plot solid mesh
- [ ] Fix short edges in PolyMesh -> more tests needed (see example.py)
- [ ] Fix small area in PolyMesh (highly skewed triangles)
- [ ] Solid mesh statistics
- [ ] Fix short edges in SolidMesh
- [ ] Export to STL
- [ ] Polygon mesh faces should match solid mesh faces at the boundary
- [ ] Add logger
- [ ] Calculate solid volume
- [ ] Accurate center of weight for Solid
- [ ] Wall could be a collection of Polygons instead of a Polygon subclass
- [ ] Zone could be a collection of Solids instead of a Solid subclass
