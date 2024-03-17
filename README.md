# building3d

I don't now where this project is heading, so there's no documentation yet.

# Installation
```
python3.10 -m venv venv
source venv/bin/activate
pip install -e .[dev]
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
- [ ] Delaunay triangulation of a polygon
- [ ] Delaunay triangulation of a solid
- [ ] Calculate solid volume
- [ ] Accurate center of weight for Solid
- [ ] Use mayavi instead of matplotlib: https://docs.enthought.com/mayavi/mayavi/index.html
