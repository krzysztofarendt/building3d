import numpy as np
import pytest

from building3d import random_id
from building3d.geom.exceptions import GeometryError
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon


def test_too_few_points():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    with pytest.raises(GeometryError):
        _ = Polygon(random_id(), [p0, p1])


def test_points_not_coplanar():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(6.0, 6.0, 6.0)
    with pytest.raises(GeometryError):
        _ = Polygon(random_id(), [p0, p1, p2, p3])


def test_triangular_polygon():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(0.0, 1.0, 0.0)
    poly = Polygon(random_id(), [p0, p1, p2])
    assert len(poly.triangles) == 1
    assert set(poly.triangles[0]) == {0, 1, 2}


def test_points_copied():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(0.0, 1.0, 0.0)
    points = [p0, p1, p2]
    poly = Polygon(random_id(), points)
    assert points is not poly.points
    assert set(points) == set(poly.points)


def test_area():
    eps = 1e-8

    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    poly = Polygon(random_id(), [p0, p1, p2, p3])
    expected_area = 1.0
    assert np.abs(poly.area - expected_area) < eps

    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(0.0, 1.0, 0.0)
    poly = Polygon(random_id(), [p0, p1, p2])
    expected_area = 0.5
    assert np.abs(poly.area - expected_area) < eps

    p1 = Point(1.0, 0.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p5 = Point(1.0, 0.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)
    poly = Polygon(random_id(), [p1, p3, p7, p5])
    expected_area = np.sqrt(2)
    assert np.abs(poly.area - expected_area) < eps


def test_normal():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    poly = Polygon(random_id(), [p0, p1, p2, p3])
    assert np.isclose(poly.normal, [0, 0, 1]).all()

    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 1.0)
    p2 = Point(1.0, 1.0, 1.0)
    p3 = Point(0.0, 1.0, 0.0)
    poly = Polygon(random_id(), [p0, p1, p2, p3])
    expected = np.array([-1.0, 0.0, 1.0])
    expected /= np.sqrt(expected[0] ** 2 + expected[1] ** 2 + expected[2] ** 2)
    assert np.isclose(poly.normal, expected).all()

    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 5.0)
    p2 = Point(1.0, 1.0, 5.0)
    p3 = Point(0.0, 1.0, 0.0)
    poly = Polygon(random_id(), [p0, p1, p2, p3])
    expected = np.array([-5.0, 0.0, 1.0])
    expected /= np.sqrt(expected[0] ** 2 + expected[1] ** 2 + expected[2] ** 2)
    assert np.isclose(poly.normal, expected).all()


def test_centroid():
    eps = 1e-8

    p1 = Point(1.0, 0.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p5 = Point(1.0, 0.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)
    poly = Polygon(random_id(), [p1, p3, p7, p5])
    expected_centroid = np.array([0.5, 0.5, 0.5])
    assert np.sum(poly.centroid.vector() - expected_centroid) < eps


def test_triangulation_l_shape():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(2.0, 0.0, 0.0)
    p2 = Point(2.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(1.0, 2.0, 0.0)
    p5 = Point(0.0, 2.0, 0.0)
    poly = Polygon(random_id(), [p0, p1, p2, p3, p4, p5])
    triangles = [{i, j, k} for i, j, k in poly.triangles]
    assert {2, 3, 4} not in triangles


def test_triangulation_cross_shape_on_xy_plane():
    p0 = Point(-1.0, -1.0, 0.0)
    p1 = Point(-1.0, -2.0, 0.0)
    p2 = Point(1.0, -2.0, 0.0)
    p3 = Point(1.0, -1.0, 0.0)
    p4 = Point(2.0, -1.0, 0.0)
    p5 = Point(2.0, 1.0, 0.0)
    p6 = Point(1.0, 1.0, 0.0)
    p7 = Point(1.0, 2.0, 0.0)
    p8 = Point(-1.0, 2.0, 0.0)
    p9 = Point(-1.0, 1.0, 0.0)
    p10 = Point(-2.0, 1.0, 0.0)
    p11 = Point(-2.0, -1.0, 0.0)
    poly = Polygon(random_id(), [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p0])
    triangles = [{i, j, k} for i, j, k in poly.triangles]
    assert {10, 11, 0} not in triangles
    assert {1, 2, 3} not in triangles
    assert {4, 5, 6} not in triangles
    assert {7, 8, 9} not in triangles


def test_triangulation_cross_shape_on_yz_plane():
    p0 = Point(0.0, -1.0, -1.0)
    p1 = Point(0.0, -1.0, -2.0)
    p2 = Point(0.0, 1.0, -2.0)
    p3 = Point(0.0, 1.0, -1.0)
    p4 = Point(0.0, 2.0, -1.0)
    p5 = Point(0.0, 2.0, 1.0)
    p6 = Point(0.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 2.0)
    p8 = Point(0.0, -1.0, 2.0)
    p9 = Point(0.0, -1.0, 1.0)
    p10 = Point(0.0, -2.0, 1.0)
    p11 = Point(0.0, -2.0, -1.0)
    poly = Polygon(random_id(), [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p0])
    triangles = [{i, j, k} for i, j, k in poly.triangles]
    assert {10, 11, 0} not in triangles
    assert {1, 2, 3} not in triangles
    assert {4, 5, 6} not in triangles
    assert {7, 8, 9} not in triangles


def test_is_point_inside():
    # Test 1
    p1 = Point(1.0, 0.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p5 = Point(1.0, 0.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)
    poly = Polygon(random_id(), [p1, p3, p7, p5])
    p = Point(0.5, 0.5, 0.5)
    assert poly.is_point_inside(p)

    # Test 2
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.0, 1.0, 0.0)
    poly = Polygon(random_id(), [p1, p2, p3, p4])
    p = Point(0.0, 0.0, 0.0)
    assert poly.is_point_inside(p)

    # Test 2
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.0, 1.0, 0.0)
    poly = Polygon(random_id(), [p1, p2, p3, p4])
    p = Point(0.5, 0.5, 0.0)
    assert poly.is_point_inside(p)


def test_is_point_inside_ortho_projection():
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 1.0)
    p4 = Point(1.0, 0.0, 1.0)
    poly = Polygon(random_id(), [p1, p2, p3, p4])

    ptest = Point(1.0, 0.5, 0.5)
    assert poly.is_point_inside_ortho_projection(ptest) is True
    ptest = Point(2.0, 0.99, 0.90)
    assert poly.is_point_inside_ortho_projection(ptest) is True
    ptest = Point(2.0, 0.01, 0.01)
    assert poly.is_point_inside_ortho_projection(ptest) is True
    ptest = Point(-1.0, 0.01, 0.90)
    assert poly.is_point_inside_ortho_projection(ptest) is True
    ptest = Point(-1.0, 0.99, 0.01)
    assert poly.is_point_inside_ortho_projection(ptest) is True
    ptest = Point(-1.0, 1.01, 0.99)
    assert poly.is_point_inside_ortho_projection(ptest) is False
    ptest = Point(1.0, -0.001, -0.001)
    assert poly.is_point_inside_ortho_projection(ptest) is False


def test_is_point_inside_ortho_projection_fwd_only():
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 1.0)
    p4 = Point(1.0, 0.0, 1.0)
    poly = Polygon(random_id(), [p1, p2, p3, p4])

    ptest = Point(2.0, 0.5, 0.5)
    vec = np.array([1.0, 0.0, 0.0])
    fwd_only = False
    assert poly.is_point_inside_projection(ptest, vec, fwd_only) is True
    ptest = Point(2.0, 0.5, 0.5)
    vec = np.array([1.0, 0.0, 0.0])
    fwd_only = True
    assert poly.is_point_inside_projection(ptest, vec, fwd_only) is False
    ptest = Point(2.0, 0.5, 0.5)
    vec = np.array([0.0, 0.0, 1.0])
    fwd_only = False
    assert poly.is_point_inside_projection(ptest, vec, fwd_only) is False


def test_is_point_behind():
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 1.0)
    p4 = Point(1.0, 0.0, 1.0)
    poly = Polygon(random_id(), [p1, p2, p3, p4])

    ptest = Point(0.99, 0.5, 0.5)
    assert poly.is_point_behind(ptest) is True
    ptest = Point(1.01, 0.5, 0.5)
    assert poly.is_point_behind(ptest) is False


def test_plane_equation_coefficients():
    p1 = Point(0.0, 4.0, -1.0)
    p2 = Point(1.0, -1.0, 2.0)
    p3 = Point(0.0, -2.0, 3.0)
    poly = Polygon(random_id(), [p1, p2, p3])
    a, b, c, d = poly.plane_equation_coefficients()

    # Equation 1*x + 2*y + 3*z - 5 = 0
    # a = 1
    # b = 2
    # c = 3
    # d = -5
    # However, the coefficients might be scaled linearly
    # so we need to compare how they are w.r.t. to each other
    # rather than checking the absolute values
    a_exp = 1.0
    b_exp = 2.0
    c_exp = 3.0
    d_exp = -5.0

    assert np.isclose(a / b, a_exp / b_exp)
    assert np.isclose(a / c, a_exp / c_exp)
    assert np.isclose(a / d, a_exp / d_exp)


def test_copy():
    p1 = Point(0.0, 4.0, -1.0)
    p2 = Point(1.0, -1.0, 2.0)
    p3 = Point(0.0, -2.0, 3.0)
    poly_a = Polygon(random_id(), [p1, p2, p3])
    poly_b = poly_a.copy(random_id())

    for i in range(3):
        assert poly_a.points[i] == poly_b.points[i]
        assert not (poly_a.points[i] is poly_b.points[i])

    assert not (poly_a is poly_b)


if __name__ == "__main__":
    test_is_point_inside_ortho_projection()
