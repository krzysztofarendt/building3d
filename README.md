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

- [x] Fix small area in PolyMesh (highly skewed triangles)
- [x] Fix short edges in SolidMesh (through `min_volume`)
- [x] Solid mesh statistics
- [x] When generating new points for mesh, make sure they are far from polygon edges
- [x] Solid mesh min. volume can lead to a removal of boundary elements -> removed this logic
- [x] Solid mesh vertices reindexing after element deletion due to low volume
- [x] Solid mesh and polygon mesh
- [x] PolyMesh does not work with non-convex polygons
- [ ] Polygon mesh faces should match solid mesh faces at the boundary -> done with joggling
- [ ] PolyMesh should check if edge vertices are shared by at least 2 polygons (corners will be shared by >= 2)
- [ ] Test solid mesh with multiple solid instances
- [ ] Export to STL
- [ ] Add logger
- [ ] Calculate solid volume
- [ ] Accurate center of weight for Solid
- [ ] Wall could be a collection of Polygons instead of a Polygon subclass
- [ ] Zone could be a collection of Solids instead of a Solid subclass
- [ ] Try plotly instead of mayavi2
- [ ] Try `triangle` 2D constrained Delaunay triangulation: https://rufat.be/triangle/
