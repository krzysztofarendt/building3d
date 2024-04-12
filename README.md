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
- [ ] Solid mesh statistics
- [ ] Export to STL
- [ ] Polygon mesh faces should match solid mesh faces at the boundary
- [ ] Add logger
- [ ] Calculate solid volume
- [ ] Accurate center of weight for Solid
- [ ] Wall could be a collection of Polygons instead of a Polygon subclass
- [ ] Zone could be a collection of Solids instead of a Solid subclass
