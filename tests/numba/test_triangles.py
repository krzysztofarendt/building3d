import numpy as np

from building3d.geom.numba.triangles import triangle_area
from building3d.geom.numba.triangles import triangle_centroid
from building3d.geom.numba.triangles import is_point_on_same_side


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
