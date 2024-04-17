# building3d

I'm not sure where this project is heading, so there is not documentation yet.

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

- [x] Calculate solid volume
- [x] Mesh for non-convex solids
- [x] Make it possible to define Polygon starting from a non-convex vector (if
  the cross product of corner vertices points in the same direction as polygon
  normal, it is convex)
- [x] Constrained Delaunay triangulation
- [ ] Constrained Delaunay tetrahedralization
- [ ] Subpolygons
- [ ] Test solid mesh with multiple solid instances
- [ ] Accurate center of weight for Solid
- [ ] Export/import to/from STL (and other formats?)
- [ ] Wall could be a collection of Polygons instead of a Polygon subclass
- [ ] Zone could be a collection of Solids instead of a Solid subclass
- [ ] Try plotly instead of mayavi2
- [ ] Try `triangle` 2D constrained Delaunay triangulation:
  https://rufat.be/triangle/
