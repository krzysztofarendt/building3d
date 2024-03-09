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
- [ ] Triangulation:
    - https://www.geometrictools.com/Documentation/TriangulationByEarClipping.pdf
    - https://nils-olovsson.se/articles/ear_clipping_triangulation/
- [ ] Accurate center of weight for Wall
- [ ] Accurate center of weight for Space
- [ ] Triangle area: https://en.wikipedia.org/wiki/Heron%27s_formula
