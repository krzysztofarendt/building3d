import numpy as np

from building3d.geom.operations.hole_polygon import hole_polygon
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon


def test_imprint_polygon_hole_inside():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p0, p1, p2, p3])

    h0 = Point(0.2, 0.2, 0.0)
    h1 = Point(0.8, 0.2, 0.0)
    h2 = Point(0.8, 0.8, 0.0)
    h3 = Point(0.2, 0.8, 0.0)
    hole = Polygon([h0, h1, h2, h3])

    polys = hole_polygon(poly, hole)
    assert len(polys) == 2

    for p in polys:
        assert not p.is_point_inside(hole.some_interior_point())

    # Make sure their normal vectors are equal
    n = None
    for p in polys:
        if n is None:
            n = p.normal
        else:
            assert np.allclose(p.normal, n)


def test_imprint_polygon_hole_touching_edge():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p0, p1, p2, p3])

    h0 = Point(0.2, 0.0, 0.0)
    h1 = Point(0.8, 0.0, 0.0)
    h2 = Point(0.8, 0.8, 0.0)
    h3 = Point(0.2, 0.8, 0.0)
    hole = Polygon([h0, h1, h2, h3])

    polys = hole_polygon(poly, hole)
    assert len(polys) == 1

    for p in polys:
        assert not p.is_point_inside(hole.some_interior_point())

    # Make sure their normal vectors are equal
    n = None
    for p in polys:
        if n is None:
            n = p.normal
        else:
            assert np.allclose(p.normal, n)

    # Reversed order
    hole = Polygon([h3, h2, h1, h0])

    polys = hole_polygon(poly, hole)
    assert len(polys) == 1

    for p in polys:
        assert not p.is_point_inside(hole.some_interior_point())

    # Make sure their normal vectors are equal
    n = None
    for p in polys:
        if n is None:
            n = p.normal
        else:
            assert np.allclose(p.normal, n)
