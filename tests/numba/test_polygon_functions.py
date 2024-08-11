import numpy as np

from building3d.geom.numba.points import new_point
from building3d.geom.numba.vectors import new_vector
from building3d.geom.numba.polygon.centroid import polygon_centroid
from building3d.geom.numba.polygon.edges import polygon_edges
from building3d.geom.numba.polygon.area import polygon_area
from building3d.geom.numba.polygon.plane import projection_coefficients
from building3d.geom.numba.polygon.plane import plane_coefficients
from building3d.geom.numba.polygon.ispointinside import is_point_inside


def test_polygon_centroid_square():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(1, 1, 0)
    pt3 = new_point(0, 1, 0)
    pts = np.vstack((pt0, pt1, pt2, pt3))
    tri = np.array([
            [0, 1, 2],
            [2, 3, 0],
    ])
    ctr = polygon_centroid(pts, tri)
    assert np.allclose(ctr, [0.5, 0.5, 0.0])


def test_polygon_edges():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(1, 1, 0)
    pt3 = new_point(0, 1, 0)
    pts = np.vstack((pt0, pt1, pt2, pt3))
    edges = polygon_edges(pts)
    assert edges.shape == (4, 2, 3)
    assert np.allclose(edges[0, 0, :], pt0)
    assert np.allclose(edges[0, 1, :], pt1)
    assert np.allclose(edges[1, 0, :], pt1)
    assert np.allclose(edges[1, 1, :], pt2)
    assert np.allclose(edges[2, 0, :], pt2)
    assert np.allclose(edges[2, 1, :], pt3)
    assert np.allclose(edges[3, 0, :], pt3)
    assert np.allclose(edges[3, 1, :], pt0)


def test_polygon_area():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(1, 1, 0)
    pt3 = new_point(0, 1, 0)
    pts = np.vstack((pt0, pt1, pt2, pt3))
    vn = new_vector(0, 0, 1)
    area = polygon_area(pts, vn)
    assert np.isclose(area, 1)


def test_projection_cofficients():
    pt = new_point(0.5, 0.5, 0.5)
    vn = new_vector(1, 1, 1)
    a, b, c, d = projection_coefficients(pt, vn)
    assert np.isclose(a, 1)
    assert np.isclose(b, 1)
    assert np.isclose(c, 1)
    assert np.isclose(d, -1.5)


def test_plane_cofficients():
    pt0 = new_point(1, 0, 0)
    pt1 = new_point(0, 1, 0)
    pt2 = new_point(0, 0, 1)
    pts = np.vstack((pt0, pt1, pt2))
    a, b, c, d = plane_coefficients(pts)

    assert np.isclose(a, b)
    assert np.isclose(a, c)
    assert np.isclose(a / d, b / d)
    assert np.isclose(a / d, c / d)


def test_is_point_inside():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(1, 1, 0)
    pt3 = new_point(0, 1, 0)
    pts = np.vstack((pt0, pt1, pt2, pt3))
    tri = np.array([
            [0, 1, 2],
            [2, 3, 0],
    ])
    ptest = new_point(0.5, 0.5, 0)
    assert is_point_inside(ptest, pts, tri) is True
    ptest = new_point(0.1, 0.9, 0)
    assert is_point_inside(ptest, pts, tri) is True
    ptest = new_point(1, 1, 0)
    assert is_point_inside(ptest, pts, tri) is True
    ptest = new_point(1, 0, 0)
    assert is_point_inside(ptest, pts, tri) is True
    ptest = new_point(0.5, 0.5, 0.01)
    assert is_point_inside(ptest, pts, tri) is False
    ptest = new_point(1.1, 0, 0)
    assert is_point_inside(ptest, pts, tri) is False
    ptest = new_point(-0.001, 0, 0)
    assert is_point_inside(ptest, pts, tri) is False
