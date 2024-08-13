import numpy as np

from building3d.geom.numba.points import new_point
from building3d.geom.numba.polygon import Polygon


def test_polygon():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(1, 1, 0)
    pt3 = new_point(0, 1, 0)
    pts = np.vstack((pt0, pt1, pt2, pt3))
    poly = Polygon(pts, name="test_poly")
    # Check attributes
    assert np.allclose(poly.ctr, [0.5, 0.5, 0.0])
    assert len(poly.tri) == 2
    assert len(poly.pts) == 4
    assert np.allclose(poly.vn, [0, 0, 1])
    assert np.isclose(poly.area, 1)
    # Check if uid is random
    for _ in range(10):
        poly1 = Polygon(pts)
        poly2 = Polygon(pts)
        assert poly1.name != poly2.name
        assert poly1.uid != poly2.uid


def test_polygon_flip():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(1, 1, 0)
    pt3 = new_point(0, 1, 0)
    pts = np.vstack((pt0, pt1, pt2, pt3))
    poly1 = Polygon(pts, name="poly1")
    poly2 = poly1.flip("poly2")
    assert np.allclose(poly1.pts, poly2.pts[::-1])
