import numpy as np

from building3d.geom.numba.points import new_point
from building3d.geom.numba.vectors import new_vector
from building3d.geom.numba.polygon.centroid import polygon_centroid
from building3d.geom.numba.polygon.edges import polygon_edges
from building3d.geom.numba.polygon.area import polygon_area
from building3d.geom.numba.polygon.plane import projection_coefficients
from building3d.geom.numba.polygon.plane import plane_coefficients
from building3d.geom.numba.polygon.ispointinside import is_point_inside
from building3d.geom.numba.polygon.ispointinside import is_point_inside_margin
from building3d.geom.numba.polygon.ispointinside import is_point_inside_ortho_projection
from building3d.geom.numba.polygon.ispointinside import is_point_inside_projection
from building3d.geom.numba.polygon.polygonsfacing import are_polygons_facing
from building3d.geom.numba.triangles import triangulate
from building3d.geom.numba.vectors import normal
from building3d.geom.numba.types import INT


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


def test_is_point_inside_margin():
    pt0 = new_point(0.0, 0.0, 0.0)
    pt1 = new_point(1.0, 0.0, 0.0)
    pt2 = new_point(1.0, 1.0, 0.0)
    pt3 = new_point(0.0, 1.0, 0.0)
    pts = np.vstack((pt0, pt1, pt2, pt3))
    tri = np.array([
            [0, 1, 2],
            [2, 3, 0],
    ])

    ptest = new_point(0.1, 0.1, 0.0)

    assert is_point_inside_margin(ptest, 0.099, pts, tri)
    assert not is_point_inside_margin(ptest, 0.11, pts, tri)


def test_is_point_inside_ortho_projection():  # TODO: Doesn't pass in njit mode
    pt0 = new_point(1.0, 0.0, 0.0)
    pt1 = new_point(1.0, 1.0, 0.0)
    pt2 = new_point(1.0, 1.0, 1.0)
    pt3 = new_point(1.0, 0.0, 1.0)
    pts = np.vstack((pt0, pt1, pt2, pt3))
    tri = np.array([
            [0, 1, 2],
            [2, 3, 0],
    ], dtype=INT)

    ptest = new_point(1.0, 0.5, 0.5)
    assert is_point_inside_ortho_projection(ptest, pts, tri) is True
    ptest = new_point(2.0, 0.99, 0.90)
    assert is_point_inside_ortho_projection(ptest, pts, tri) is True
    ptest = new_point(2.0, 0.01, 0.01)
    assert is_point_inside_ortho_projection(ptest, pts, tri) is True
    ptest = new_point(-1.0, 0.01, 0.90)
    assert is_point_inside_ortho_projection(ptest, pts, tri) is True
    ptest = new_point(-1.0, 0.99, 0.01)
    assert is_point_inside_ortho_projection(ptest, pts, tri) is True
    ptest = new_point(-1.0, 1.01, 0.99)
    assert is_point_inside_ortho_projection(ptest, pts, tri) is False
    ptest = new_point(1.0, -0.001, -0.001)
    assert is_point_inside_ortho_projection(ptest, pts, tri) is False


def test_is_point_inside_projection_fwd_only():
    pt0 = new_point(1.0, 0.0, 0.0)
    pt1 = new_point(1.0, 1.0, 0.0)
    pt2 = new_point(1.0, 1.0, 1.0)
    pt3 = new_point(1.0, 0.0, 1.0)
    pts = np.vstack((pt0, pt1, pt2, pt3))
    tri = np.array([
            [0, 1, 2],
            [2, 3, 0],
    ], dtype=INT)

    ptest = new_point(2.0, 0.5, 0.5)
    vec = np.array([1.0, 0.0, 0.0])
    fwd_only = False
    assert is_point_inside_projection(ptest, vec, pts, tri, fwd_only) is True
    ptest = new_point(2.0, 0.5, 0.5)
    vec = np.array([1.0, 0.0, 0.0])
    fwd_only = True
    assert is_point_inside_projection(ptest, vec, pts, tri, fwd_only) is False
    ptest = new_point(2.0, 0.5, 0.5)
    vec = np.array([0.0, 0.0, 1.0])
    fwd_only = False
    assert is_point_inside_projection(ptest, vec, pts, tri, fwd_only) is False

    ptest = new_point(1.0, 0.5, 0.5)  # This point is at the polygon's centroid
    vec = np.array([1.0, 0.0, 0.0])
    for vec in [
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([0.0, 0.0, 1.0]),
    ]:
        fwd_only = True
        assert is_point_inside_projection(ptest, vec, pts, tri, fwd_only) is True
        fwd_only = False
        assert is_point_inside_projection(ptest, vec, pts, tri, fwd_only) is True

    ptest = new_point(1.0, 0.0, 0.0)  # This point is at the polygon's corner
    vec = np.array([1.0, 0.0, 0.0])
    for vec in [
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([0.0, 0.0, 1.0]),
    ]:
        fwd_only = True
        assert is_point_inside_projection(ptest, vec, pts, tri, fwd_only) is True
        fwd_only = False
        assert is_point_inside_projection(ptest, vec, pts, tri, fwd_only) is True


def test_are_polygons_facing():
    pt1 = new_point(0.0, 4.0, -1.0)
    pt2 = new_point(1.0, -1.0, 2.0)
    pt3 = new_point(0.0, -2.0, 3.0)
    pts1 = np.array([pt1, pt2, pt3])
    pts2 = np.array([pt3, pt2, pt1])
    vn1 = normal(pts1[-1], pts1[0], pts1[1])
    vn2 = normal(pts2[-1], pts2[0], pts2[1])
    tri1 = triangulate(pts1, vn1)
    tri2 = triangulate(pts2, vn2)

    assert are_polygons_facing(pts1, tri1, vn1, pts2, tri2, vn2) is True  # exact=True by default
    assert are_polygons_facing(pts1, tri1, vn1, pts2, tri2, vn2, exact=True) is True
    assert are_polygons_facing(pts1, tri1, vn1, pts2, tri2, vn2, exact=False) is True
    assert are_polygons_facing(pts2, tri2, vn2, pts1, tri1, vn1) is True


def test_are_polygons_facing_different_sizes():
    pt1 = new_point(0.0, 0.0, 0.0)
    pt2 = new_point(1.0, 0.0, 0.0)
    pt3 = new_point(1.0, 1.0, 0.0)
    pts1 = np.array([pt1, pt2, pt3])

    scale = np.array([2.0, 2.0, 2.0])
    pt1 = new_point(0.0, 0.0, 0.0) * scale
    pt2 = new_point(1.0, 0.0, 0.0) * scale
    pt3 = new_point(1.0, 1.0, 0.0) * scale
    pts2 = np.array([pt3, pt2, pt1])

    vn1 = normal(pts1[-1], pts1[0], pts1[1])
    vn2 = normal(pts2[-1], pts2[0], pts2[1])
    tri1 = triangulate(pts1, vn1)
    tri2 = triangulate(pts2, vn2)

    assert are_polygons_facing(pts1, tri1, vn1, pts2, tri2, vn2) is False  # exact=True by default
    assert are_polygons_facing(pts1, tri1, vn1, pts2, tri2, vn2, exact=True) is False
    assert are_polygons_facing(pts1, tri1, vn1, pts2, tri2, vn2, exact=False) is True


def test_are_polygons_not_facing():
    pt1 = new_point(0.0, 0.0, 1.0)
    pt2 = new_point(1.0, 0.0, 1.0)
    pt3 = new_point(1.0, 1.0, 1.0)
    pts1 = np.array([pt1, pt2, pt3])

    scale = np.array([2.0, 2.0, 2.0])
    pt1 = new_point(0.0, 0.0, 0.0) * scale
    pt2 = new_point(1.0, 0.0, 0.0) * scale
    pt3 = new_point(1.0, 1.0, 0.0) * scale
    pts2 = np.array([pt3, pt2, pt1])

    vn1 = normal(pts1[-1], pts1[0], pts1[1])
    vn2 = normal(pts2[-1], pts2[0], pts2[1])
    tri1 = triangulate(pts1, vn1)
    tri2 = triangulate(pts2, vn2)

    assert are_polygons_facing(pts1, tri1, vn1, pts2, tri2, vn2) is False  # exact=True by default
    assert are_polygons_facing(pts1, tri1, vn1, pts2, tri2, vn2, exact=True) is False
    assert are_polygons_facing(pts1, tri1, vn1, pts2, tri2, vn2, exact=False) is False
