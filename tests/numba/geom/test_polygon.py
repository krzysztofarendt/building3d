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


def test_polygon_bbox():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(1, 1, 0)
    pt3 = new_point(0, 1, 0)
    pts = np.vstack((pt0, pt1, pt2, pt3))
    poly = Polygon(pts, name="poly")
    bbox = poly.bbox()
    assert np.allclose(bbox[0], [0, 0, 0])
    assert np.allclose(bbox[1], [1, 1, 0])


def test_polygon_contains():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(1, 1, 0)
    pt3 = new_point(0, 1, 0)
    pts0 = np.vstack((pt0, pt1, pt2, pt3))
    poly0 = Polygon(pts0)

    pt0 = new_point(0.1, 0.1, 0)
    pt1 = new_point(0.9, 0.1, 0)
    pt2 = new_point(0.9, 0.9, 0)
    pt3 = new_point(0.1, 0.9, 0)
    pts1 = np.vstack((pt0, pt1, pt2, pt3))
    poly1 = Polygon(pts1)

    assert poly0.contains_polygon(poly1) is True
    assert poly1.contains_polygon(poly0) is False


def test_polygon_is_touching_other():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(1, 1, 0)
    pt3 = new_point(0, 1, 0)
    pts0 = np.vstack((pt0, pt1, pt2, pt3))
    poly0 = Polygon(pts0)

    pts1 = pts0 + np.array([1.0, 0.0, 0.0])
    poly1 = Polygon(pts1)
    assert poly0.is_touching_polygon(poly1) is True

    pts2 = pts0 + np.array([2.0, 0.0, 0.0])
    poly2 = Polygon(pts2)
    assert poly0.is_touching_polygon(poly2) is False

    pts3 = pts0 + np.array([0.5, 0.0, 0.0])
    poly3 = Polygon(pts3)
    assert poly0.is_touching_polygon(poly3) is False

    pts4 = pts0 + np.array([1.0, 0.5, 0.0])
    poly4 = Polygon(pts4)
    assert poly0.is_touching_polygon(poly4) is True

