# building3d

I'm not sure where this project is heading, so there is not documentation yet.

# Assumptions

Geometry:
- a set of points is used to define polygons
- a set of polygons can be used to define a solid (volume, space)
- a solid must be fully enclosed with polygons
- a zone is a set of solids

In addition, polygons can be grouped together into assemblies called *walls*:
- a wall can consist of many polygons
- wall polygons do not have to be coplanar
- wall can have subpolygons (e.g. wall with a window)
- a set of walls can be used to define a solid within a zone

Mesh:
- three types of meshes exist:
    - polygon triangulation generated by ear-clipping algorithm
    - surface mesh generated by Delaunay tesselation
    - volume mesh generated by Delaunay tesselation
- these meshes do not necessarily share their vertices
- ear-clipping is used to triangulate polygons based on its vertices only
- Delaunay tesselation is used to make meshes with additional points suitable
  for numerical simulations (ray-tracing, Finite Volume Method)
- surface and volume meshes do not necessarily share their vertices (but typically they do)
- volume meshes of adjacent solids DO NOT share vertices at the adjacent surfaces


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
- [x] Constrained Delaunay tetrahedralization
- [ ] Subpolygons
- [ ] Test solid mesh with multiple solid instances
- [ ] Accurate center of weight for Solid
- [ ] Export/import to/from STL (and other formats?)
- [ ] Wall could be a collection of Polygons instead of a Polygon subclass
- [ ] Zone could be a collection of Solids instead of a Solid subclass
- [ ] Try plotly instead of mayavi2
- [ ] Try `triangle` 2D constrained Delaunay triangulation:
  https://rufat.be/triangle/
