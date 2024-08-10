import numpy as np

from building3d.geom.numba.triangles import triangle_area
from building3d.geom.numba.triangles import triangle_centroid
from building3d.geom.numba.triangles import is_point_on_same_side
from building3d.geom.numba.triangles import is_point_inside
from building3d.geom.numba.triangles import is_corner_convex


def test_triangle_area():
    pt1 = np.array([0.0, 0.0, 0.0])
    pt2 = np.array([1.0, 0.0, 0.0])
    pt3 = np.array([0.0, 1.0, 0.0])
    assert np.isclose(triangle_area(pt1, pt2, pt3), 0.5)


def test_triangle_centroid():
    pt1 = np.array([0.0, 0.0, 0.0])
    pt2 = np.array([1.0, 0.0, 0.0])
    pt3 = np.array([0.0, 1.0, 0.0])
    c = triangle_centroid(pt1, pt2, pt3)
    assert np.allclose(c, [1/3, 1/3, 0])


def test_is_point_on_same_side():
    pt1 = np.array([0.0, 0.0, 0.0])
    pt2 = np.array([1.0, 0.0, 0.0])
    ptest = np.array([0.5, 0.1, 0.0])
    ptref = np.array([0.75, 0.5, 0.0])
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is True
    ptest = np.array([0.5, 100.0, 0.0])
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is True
    ptest = np.array([0.0, 100.0, 0.0])
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is True
    ptest = np.array([10.0, 50.0, 0.0])
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is True
    ptest = np.array([0.0, -1.0, 0.0])
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is False
    ptest = np.array([0.0, -0.0001, 0.0])
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is False
    ptest = np.array([0.0, 0.0001, 0.0])
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is True
    ptest = np.array([0.2, 0.0, 0.0])
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is False
    ptest = np.array([2.0, 0.0, 0.0])
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is False
    ptest = np.array([2.0, 0.0, 0.0])
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is False


def test_is_point_inside():
    pt1 = np.array([1.0, 0.0, 0.0])
    pt2 = np.array([0.0, 0.0, 0.0])
    pt3 = np.array([0.0, 1.0, 0.0])

    ptest = np.array([0.1, 0.1, 0.0])  # inside
    assert is_point_inside(ptest, pt1, pt2, pt3) is True

    ptest = np.array([0.0, 0.0, 0.0])  # inside (at the corner)
    assert is_point_inside(ptest, pt1, pt2, pt3) is True

    ptest = np.array([1.0, 0.0, 0.0])  # inside (at the corner)
    assert is_point_inside(ptest, pt1, pt2, pt3) is True

    ptest = np.array([0.5, 0.5, 0.0])  # inside (on the edge)
    assert is_point_inside(ptest, pt1, pt2, pt3) is True

    ptest = np.array([0.51, 0.51, 0.0])  # outside
    assert is_point_inside(ptest, pt1, pt2, pt3) is False

    p0 = np.array([0.6, 0.0, 0.0])
    p1 = np.array([0.0, 0.0, 0.0])
    p2 = np.array([0.0, 0.6, 0.0])

    ptest = np.array([0.3, 0.3, 0.0])  # inside (on the edge)
    assert is_point_inside(ptest, p0, p1, p2) is True


def test_is_corner_convex():
    pt1 = np.array([0.0, 1.0, 0.0])
    pt2 = np.array([0.0, 0.0, 0.0])
    pt3 = np.array([1.0, 0.0, 0.0])
    vn = np.array([0.0, 0.0, 1.0])
    assert is_corner_convex(pt1, pt2, pt3, vn) is True
    assert is_corner_convex(pt1, pt2, pt3, -1. * vn) is False
