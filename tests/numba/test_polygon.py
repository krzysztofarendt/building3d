import numpy as np

from building3d.geom.numba.points import new_point
from building3d.geom.numba.vectors import new_vector
from building3d.geom.numba.polygon import Polygon
from building3d.geom.numba.polygon.centroid import polygon_centroid
from building3d.geom.numba.polygon.edges import polygon_edges
from building3d.geom.numba.polygon.area import polygon_area


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

def test_polygon_copy():
    pt0 = new_point(0, 0, 0)
    pt1 = new_point(1, 0, 0)
    pt2 = new_point(1, 1, 0)
    pt3 = new_point(0, 1, 0)
    pts = np.vstack((pt0, pt1, pt2, pt3))
    poly1 = Polygon(pts, name="poly1")
    poly2 = poly1.copy("poly2")
    assert np.allclose(poly1.pts, poly2.pts)
    assert poly1 is not poly2.pts
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
