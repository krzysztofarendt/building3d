import numpy as np

from building3d.geom.numba.triangles import triangle_area
from building3d.geom.numba.triangles import triangle_centroid
from building3d.geom.numba.triangles import is_point_on_same_side
from building3d.geom.numba.triangles import is_point_inside
from building3d.geom.numba.triangles import is_corner_convex
from building3d.geom.numba.triangles import triangulate
from building3d.geom.numba.points import new_point
from building3d.geom.numba.vectors import new_vector


def test_triangle_area():
    pt1 = new_point(0.0, 0.0, 0.0)
    pt2 = new_point(1.0, 0.0, 0.0)
    pt3 = new_point(0.0, 1.0, 0.0)
    assert np.isclose(triangle_area(pt1, pt2, pt3), 0.5)


def test_triangle_centroid():
    pt1 = new_point(0.0, 0.0, 0.0)
    pt2 = new_point(1.0, 0.0, 0.0)
    pt3 = new_point(0.0, 1.0, 0.0)
    c = triangle_centroid(pt1, pt2, pt3)
    assert np.allclose(c, [1/3, 1/3, 0])


def test_is_point_on_same_side():
    pt1 = new_point(0.0, 0.0, 0.0)
    pt2 = new_point(1.0, 0.0, 0.0)
    ptest = new_point(0.5, 0.1, 0.0)
    ptref = new_point(0.75, 0.5, 0.0)
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is True
    ptest = new_point(0.5, 100.0, 0.0)
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is True
    ptest = new_point(0.0, 100.0, 0.0)
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is True
    ptest = new_point(10.0, 50.0, 0.0)
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is True
    ptest = new_point(0.0, -1.0, 0.0)
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is False
    ptest = new_point(0.0, -0.0001, 0.0)
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is False
    ptest = new_point(0.0, 0.0001, 0.0)
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is True
    ptest = new_point(0.2, 0.0, 0.0)
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is False
    ptest = new_point(2.0, 0.0, 0.0)
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is False
    ptest = new_point(2.0, 0.0, 0.0)
    assert is_point_on_same_side(pt1, pt2, ptest, ptref) is False


def test_is_point_inside():
    pt1 = new_point(1.0, 0.0, 0.0)
    pt2 = new_point(0.0, 0.0, 0.0)
    pt3 = new_point(0.0, 1.0, 0.0)

    ptest = new_point(0.1, 0.1, 0.0)  # inside
    assert is_point_inside(ptest, pt1, pt2, pt3) is True

    ptest = new_point(0.0, 0.0, 0.0)  # inside (at the corner)
    assert is_point_inside(ptest, pt1, pt2, pt3) is True

    ptest = new_point(1.0, 0.0, 0.0)  # inside (at the corner)
    assert is_point_inside(ptest, pt1, pt2, pt3) is True

    ptest = new_point(0.5, 0.5, 0.0)  # inside (on the edge)
    assert is_point_inside(ptest, pt1, pt2, pt3) is True

    ptest = new_point(0.51, 0.51, 0.0)  # outside
    assert is_point_inside(ptest, pt1, pt2, pt3) is False

    p0 = new_point(0.6, 0.0, 0.0)
    p1 = new_point(0.0, 0.0, 0.0)
    p2 = new_point(0.0, 0.6, 0.0)

    ptest = new_point(0.3, 0.3, 0.0)  # inside (on the edge)
    assert is_point_inside(ptest, p0, p1, p2) is True


def test_is_corner_convex():
    pt1 = new_point(0.0, 1.0, 0.0)
    pt2 = new_point(0.0, 0.0, 0.0)
    pt3 = new_point(1.0, 0.0, 0.0)
    vn = new_point(0.0, 0.0, 1.0)
    assert is_corner_convex(pt1, pt2, pt3, vn) is True
    assert is_corner_convex(pt1, pt2, pt3, -1. * vn) is False


def test_triangulate_square():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(1, 1, 0)
    pt3 = new_point(0, 1, 0)
    pts = np.vstack((pt0, pt1, pt2, pt3))
    vn = new_vector(0, 0, 1)
    tri = triangulate(pts, vn)
    assert len(tri) == 2


def test_triangulate_l_shape():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(1, 1, 0)
    pt3 = new_point(2, 1, 0)
    pt4 = new_point(2, 2, 0)
    pt5 = new_point(0, 2, 0)
    pts = np.vstack((pt0, pt1, pt2, pt3, pt4, pt5))
    vn = new_vector(0, 0, 1)
    tri = triangulate(pts, vn)
    assert len(tri) == 4
