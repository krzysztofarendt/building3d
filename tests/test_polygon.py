import numpy as np
import pytest

from building3d.geom.exceptions import GeometryError
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon


def test_multiple_points_along_single_edge():
    # These points have been causing some errors in the past
    # because some are placed along a single edge if if they are
    # used for calculating the normal vector, its length was 0.
    p0 = Point(x=0.00, y=0.00, z=0.00)
    p1 = Point(x=0.00, y=1.00, z=0.00)
    p2 = Point(x=1.00, y=1.00, z=0.00)
    p3 = Point(x=0.50, y=0.50, z=0.00)
    poly = Polygon([p0, p1, p2, p3])
    poly = poly.flip()  # This was causing error in the past


def test_num_edges():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p1, p2, p3, p4])
    assert len(poly.edges) == 4


def test_too_few_points():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    with pytest.raises(GeometryError):
        _ = Polygon([p0, p1])


def test_points_not_coplanar():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(6.0, 6.0, 6.0)
    with pytest.raises(GeometryError):
        _ = Polygon([p0, p1, p2, p3])


def test_triangular_polygon():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p0, p1, p2])
    assert len(poly.triangles) == 1
    assert set(poly.triangles[0]) == {0, 1, 2}


def test_points_copied():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(0.0, 1.0, 0.0)
    points = [p0, p1, p2]
    poly = Polygon(points)
    assert points is not poly.points
    assert set(points) == set(poly.points)


def test_area():
    eps = 1e-8

    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p0, p1, p2, p3])
    expected_area = 1.0
    assert np.abs(poly.area - expected_area) < eps

    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p0, p1, p2])
    expected_area = 0.5
    assert np.abs(poly.area - expected_area) < eps

    p1 = Point(1.0, 0.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p5 = Point(1.0, 0.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)
    poly = Polygon([p1, p3, p7, p5])
    expected_area = np.sqrt(2)
    assert np.abs(poly.area - expected_area) < eps


def test_normal():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p0, p1, p2, p3])
    assert np.isclose(poly.normal, [0, 0, 1]).all()

    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 1.0)
    p2 = Point(1.0, 1.0, 1.0)
    p3 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p0, p1, p2, p3])
    expected = np.array([-1.0, 0.0, 1.0])
    expected /= np.sqrt(expected[0] ** 2 + expected[1] ** 2 + expected[2] ** 2)
    assert np.isclose(poly.normal, expected).all()

    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 5.0)
    p2 = Point(1.0, 1.0, 5.0)
    p3 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p0, p1, p2, p3])
    expected = np.array([-5.0, 0.0, 1.0])
    expected /= np.sqrt(expected[0] ** 2 + expected[1] ** 2 + expected[2] ** 2)
    assert np.isclose(poly.normal, expected).all()


def test_centroid():
    eps = 1e-8

    p1 = Point(1.0, 0.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p5 = Point(1.0, 0.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)
    poly = Polygon([p1, p3, p7, p5])
    expected_centroid = np.array([0.5, 0.5, 0.5])
    assert np.sum(poly.centroid.vector() - expected_centroid) < eps


def test_triangulation_l_shape():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(2.0, 0.0, 0.0)
    p2 = Point(2.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(1.0, 2.0, 0.0)
    p5 = Point(0.0, 2.0, 0.0)
    poly = Polygon([p0, p1, p2, p3, p4, p5])
    triangles = [{i, j, k} for i, j, k in poly.triangles]
    assert {2, 3, 4} not in triangles


def test_triangulation_start_from_nonconvex_corner():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(2.0, 0.0, 0.0)
    p2 = Point(2.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)  # non-convex corner
    p4 = Point(1.0, 2.0, 0.0)
    p5 = Point(0.0, 2.0, 0.0)
    poly = Polygon([p3, p4, p5, p0, p1, p2])
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
    poly = Polygon([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p0])
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
    poly = Polygon([p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p0])
    triangles = [{i, j, k} for i, j, k in poly.triangles]
    assert {10, 11, 0} not in triangles
    assert {1, 2, 3} not in triangles
    assert {4, 5, 6} not in triangles
    assert {7, 8, 9} not in triangles


def test_distance_point_to_polygon():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    ptest1 = Point(0.5, 0.5, 1.0)  # distance = 1
    ptest2 = Point(1.0, 0.5, 1.0)  # distance = 1
    ptest3 = Point(1.0, 0.5, -1.0)  # distance = 1
    ptest4 = Point(1.0, 2.0, 0.0)  # distance = 1
    ptest5 = Point(2.0, 1.0, 1.0)  # distance = np.sqrt(2)
    ptest6 = Point(-1.0, -1.0, 0.0)  # distance = np.sqrt(2)
    ptest7 = Point(0.9, 0.1, 3.0)  # distance = 3
    ptest8 = Point(0.5, 2.0, 0.0)  # distance = 1 (TODO: must calc. dist. to edge, not to vertex)

    poly = Polygon([p0, p1, p2, p3])

    d = poly.distance_point_to_polygon(ptest1)
    assert np.isclose(d, 1.0)
    d = poly.distance_point_to_polygon(ptest2)
    assert np.isclose(d, 1.0)
    d = poly.distance_point_to_polygon(ptest3)
    assert np.isclose(d, 1.0)
    d = poly.distance_point_to_polygon(ptest4)
    assert np.isclose(d, 1.0)
    d = poly.distance_point_to_polygon(ptest5)
    assert np.isclose(d, np.sqrt(2))
    d = poly.distance_point_to_polygon(ptest6)
    assert np.isclose(d, np.sqrt(2))
    d = poly.distance_point_to_polygon(ptest7)
    assert np.isclose(d, 3)
    d = poly.distance_point_to_polygon(ptest8)
    assert np.isclose(d, 1)

    p0 = Point(1.0, 1.0, 0.0)
    p1 = Point(0.0, 1.0, 0.0)
    p2 = Point(0.0, 0.0, 1.0)
    p3 = Point(1.0, 0.0, 1.0)
    poly = Polygon([p0, p1, p2, p3])
    ptest8 = Point(0.5, 1.0, 1.0)  # distance = np.sqrt(2) / 2

    d = poly.distance_point_to_polygon(ptest8)
    assert np.isclose(d, np.sqrt(2) / 2)


def test_is_point_inside():
    # Test 1
    p1 = Point(1.0, 0.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p5 = Point(1.0, 0.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)
    poly = Polygon([p1, p3, p7, p5])
    p = Point(0.5, 0.5, 0.5)
    assert poly.is_point_inside(p)

    # Test 2
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p1, p2, p3, p4])
    p = Point(0.0, 0.0, 0.0)
    assert poly.is_point_inside(p)

    # Test 2
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p1, p2, p3, p4])
    p = Point(0.5, 0.5, 0.0)
    assert poly.is_point_inside(p)


def test_is_point_inside_ortho_projection():
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 1.0)
    p4 = Point(1.0, 0.0, 1.0)
    poly = Polygon([p1, p2, p3, p4])

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
    poly = Polygon([p1, p2, p3, p4])

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

    ptest = Point(1.0, 0.5, 0.5)  # This point is at the polygon's centroid
    vec = np.array([1.0, 0.0, 0.0])
    for vec in [
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([0.0, 0.0, 1.0]),
    ]:
        fwd_only = True
        assert poly.is_point_inside_projection(ptest, vec, fwd_only) is True
        fwd_only = False
        assert poly.is_point_inside_projection(ptest, vec, fwd_only) is True

    ptest = Point(1.0, 0.0, 0.0)  # This point is at the polygon's corner
    vec = np.array([1.0, 0.0, 0.0])
    for vec in [
        np.array([1.0, 0.0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
        np.array([0.0, 0.0, 1.0]),
    ]:
        fwd_only = True
        assert poly.is_point_inside_projection(ptest, vec, fwd_only) is True
        fwd_only = False
        assert poly.is_point_inside_projection(ptest, vec, fwd_only) is True


def test_is_point_behind():
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 1.0)
    p4 = Point(1.0, 0.0, 1.0)
    poly = Polygon([p1, p2, p3, p4])

    ptest = Point(0.99, 0.5, 0.5)
    assert poly.is_point_behind(ptest) is True
    ptest = Point(1.01, 0.5, 0.5)
    assert poly.is_point_behind(ptest) is False


def test_plane_equation_coefficients():
    p1 = Point(0.0, 4.0, -1.0)
    p2 = Point(1.0, -1.0, 2.0)
    p3 = Point(0.0, -2.0, 3.0)
    poly = Polygon([p1, p2, p3])
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
    poly_a = Polygon([p1, p2, p3])
    poly_b = poly_a.copy()

    for i in range(3):
        assert poly_a.points[i] == poly_b.points[i]
        assert not (poly_a.points[i] is poly_b.points[i])

    assert not (poly_a is poly_b)


def test_is_facing_polygon_exact():
    p1 = Point(0.0, 4.0, -1.0)
    p2 = Point(1.0, -1.0, 2.0)
    p3 = Point(0.0, -2.0, 3.0)
    poly_a = Polygon([p1, p2, p3])
    poly_b = Polygon([p3, p2, p1])
    assert poly_a.is_facing_polygon(poly_b)  # exact=True by default
    assert poly_a.is_facing_polygon(poly_b, exact=True)
    assert poly_a.is_facing_polygon(poly_b, exact=False)


def test_is_facing_polygon_different_sizes():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    poly_a = Polygon([p1, p2, p3])

    scale = (2, 2, 2)
    p1 = Point(0.0, 0.0, 0.0) * scale
    p2 = Point(1.0, 0.0, 0.0) * scale
    p3 = Point(1.0, 1.0, 0.0) * scale
    poly_b = Polygon([p3, p2, p1])
    assert not poly_a.is_facing_polygon(poly_b)  # exact=True by default
    assert not poly_a.is_facing_polygon(poly_b, exact=True)
    assert poly_a.is_facing_polygon(poly_b, exact=False)


def test_equality():
    p1 = Point(0.0, 4.0, -1.0)
    p2 = Point(1.0, -1.0, 2.0)
    p3 = Point(0.0, -2.0, 3.0)
    p4 = Point(0.0, -3.0, 4.0)
    poly_a = Polygon([p1, p2, p3])
    poly_b = Polygon([p1, p2, p3])
    poly_c = Polygon([p2, p3, p1])
    poly_d = Polygon([p3, p2, p1])
    poly_e = Polygon([p1, p2, p4])
    assert poly_a == poly_b  # Same polygon
    assert poly_a == poly_c  # Same polygon, just different start vertex
    assert poly_a != poly_d  # Opposite normal vectors
    assert poly_a != poly_e  # One vertex different (p4)


def test_polygon_with_known_triangles():
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 1.0)
    p4 = Point(1.0, 0.0, 1.0)
    poly = Polygon(
        [p1, p2, p3, p4],
        triangles=[(0, 1, 2), (0, 2, 3)],
    )
    assert np.isclose(poly.area, 1)
    assert poly.centroid == Point(1.0, 0.5, 0.5)


def test_polygon_flip():
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(1.0, 1.0, 1.0)
    p4 = Point(1.0, 0.0, 1.0)
    poly = Polygon([p1, p2, p3, p4])
    flipped = poly.flip()
    assert np.isclose(flipped.area, poly.area)
    assert flipped.centroid == poly.centroid
    assert np.isclose(flipped.normal, -poly.normal).all()


def test_polygon_slice_start_and_end_at_same_edge():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p1, p2, p3, p4])

    slicing_points = [
        Point(0.3, 0.0, 0.0),
        Point(0.3, 0.5, 0.0),
        Point(0.6, 0.5, 0.0),
        Point(0.6, 0.0, 0.0),
    ]
    poly1_pt = Point(0.0, 0.0, 0.0)
    poly2_pt = Point(0.45, 0.25, 0.0)
    poly1, poly2 = poly.slice(
        slicing_points,
        name1="poly1",
        pt1=poly1_pt,
        name2="poly2",
        pt2=poly2_pt,
    )
    assert np.isclose(poly1.normal, poly.normal).all()
    assert np.isclose(poly2.normal, poly.normal).all()
    assert np.isclose(poly.area, poly1.area + poly2.area)
    assert poly1.is_point_inside(poly1_pt)
    assert poly2.is_point_inside(poly2_pt)

    # Reversed order
    slicing_points = slicing_points[::-1]
    poly1, poly2 = poly.slice(
        slicing_points,
        name1="poly1",
        pt1=poly1_pt,
        name2="poly2",
        pt2=poly2_pt,
    )
    assert np.isclose(poly1.normal, poly.normal).all()
    assert np.isclose(poly2.normal, poly.normal).all()
    assert np.isclose(poly.area, poly1.area + poly2.area)
    assert poly1.is_point_inside(poly1_pt)
    assert poly2.is_point_inside(poly2_pt)


def test_polygon_slice_start_and_end_at_different_edges_vertical():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p1, p2, p3, p4])

    # Vertical slicing line
    slicing_points = [
        Point(0.5, 0.0, 0.0),
        Point(0.5, 1.0, 0.0),
    ]
    poly1_pt = Point(0.0, 0.0, 0.0)
    poly2_pt = Point(1.0, 0.5, 0.0)
    poly1, poly2 = poly.slice(
        slicing_points,
        name1="poly1",
        pt1=poly1_pt,
        name2="poly2",
        pt2=poly2_pt,
    )

    assert np.isclose(poly1.normal, poly.normal).all()
    assert np.isclose(poly2.normal, poly.normal).all()
    assert np.isclose(poly.area, poly1.area + poly2.area)
    assert poly1.is_point_inside(poly1_pt)
    assert poly2.is_point_inside(poly2_pt)

    # Try without name and pt arguments
    poly1, poly2 = poly.slice(slicing_points)

    assert np.isclose(poly1.normal, poly.normal).all()
    assert np.isclose(poly2.normal, poly.normal).all()
    assert np.isclose(poly.area, poly1.area + poly2.area)


def test_polygon_slice_start_and_end_at_different_edges_horizontal():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p1, p2, p3, p4])

    # horizontal slicing line
    slicing_points = [
        Point(0.0, 0.5, 0.0),
        Point(1.0, 0.5, 0.0),
    ]
    poly1_pt = Point(0.0, 0.0, 0.0)
    poly2_pt = Point(0.0, 1.0, 0.0)
    poly1, poly2 = poly.slice(
        slicing_points,
        name1="poly1",
        pt1=poly1_pt,
        name2="poly2",
        pt2=poly2_pt,
    )

    assert np.isclose(poly1.normal, poly.normal).all()
    assert np.isclose(poly2.normal, poly.normal).all()
    assert np.isclose(poly.area, poly1.area + poly2.area)
    assert poly1.is_point_inside(poly1_pt)
    assert poly2.is_point_inside(poly2_pt)


def test_polygon_slice_start_and_end_at_different_edges_horizontal_5points():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.2, 1.0, 0.0)
    p5 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p1, p2, p3, p4, p5])

    # Horizontal slicing line
    slicing_points = [
        Point(0.0, 0.5, 0.0),
        Point(1.0, 0.5, 0.0),
    ]
    poly1_pt = Point(0.0, 0.0, 0.0)
    poly2_pt = Point(0.0, 1.0, 0.0)
    poly1, poly2 = poly.slice(
        slicing_points,
        name1="poly1",
        pt1=poly1_pt,
        name2="poly2",
        pt2=poly2_pt,
    )

    assert np.isclose(poly1.normal, poly.normal).all()
    assert np.isclose(poly2.normal, poly.normal).all()
    assert np.isclose(poly.area, poly1.area + poly2.area)
    assert poly1.is_point_inside(poly1_pt)
    assert poly2.is_point_inside(poly2_pt)


def test_polygon_slice_start_and_end_at_a_vertex():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p1, p2, p3, p4])

    # Three slicing points
    slicing_points = [
        Point(0.0, 0.0, 0.0),
        Point(0.5, 0.5, 0.0),
        Point(1.0, 1.0, 0.0),
    ]
    poly1_pt = Point(1.0, 0.0, 0.0)
    poly2_pt = Point(0.0, 1.0, 0.0)
    poly1, poly2 = poly.slice(
        slicing_points,
        name1="poly1",
        pt1=poly1_pt,
        name2="poly2",
        pt2=poly2_pt,
    )

    assert np.isclose(poly1.normal, poly.normal).all()
    assert np.isclose(poly2.normal, poly.normal).all()
    assert np.isclose(poly.area, poly1.area + poly2.area)
    assert poly1.is_point_inside(poly1_pt)
    assert poly2.is_point_inside(poly2_pt)

    # Two slicing points
    slicing_points = [
        Point(0.0, 0.0, 0.0),
        Point(1.0, 1.0, 0.0),
    ]
    poly1_pt = Point(1.0, 0.0, 0.0)
    poly2_pt = Point(0.0, 1.0, 0.0)
    poly1, poly2 = poly.slice(
        slicing_points,
        name1="poly1",
        pt1=poly1_pt,
        name2="poly2",
        pt2=poly2_pt,
    )

    assert np.isclose(poly1.normal, poly.normal).all()
    assert np.isclose(poly2.normal, poly.normal).all()
    assert np.isclose(poly.area, poly1.area + poly2.area)
    assert poly1.is_point_inside(poly1_pt)
    assert poly2.is_point_inside(poly2_pt)


def test_polygon_slice_start_at_vertex_end_at_edge():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p1, p2, p3, p4])

    # Three slicing points
    slicing_points = [
        Point(0.0, 0.0, 0.0),
        Point(0.5, 0.5, 0.0),
        Point(0.5, 1.0, 0.0),
    ]
    poly1_pt = Point(1.0, 0.0, 0.0)
    poly2_pt = Point(0.0, 1.0, 0.0)
    poly1, poly2 = poly.slice(
        slicing_points,
        name1="poly1",
        pt1=poly1_pt,
        name2="poly2",
        pt2=poly2_pt,
    )

    assert np.isclose(poly1.normal, poly.normal).all()
    assert np.isclose(poly2.normal, poly.normal).all()
    assert np.isclose(poly.area, poly1.area + poly2.area)
    assert poly1.is_point_inside(poly1_pt)
    assert poly2.is_point_inside(poly2_pt)


def test_polygon_slice_multiple_points_at_edge():  # TODO
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p1, p2, p3, p4])

    # Three slicing points
    slicing_points = [
        Point(0.0, 0.0, 0.0),  # At vertex (edge is overidden with vertex)
        Point(0.1, 0.0, 0.0),  # At edge
        Point(0.2, 0.0, 0.0),  # At edge
        Point(0.5, 0.5, 0.0),  # Interior
        Point(0.5, 1.0, 0.0),  # At edge
        Point(0.6, 1.0, 0.0),  # At edge
    ]
    # Total number at edge = 4
    # Total number at vertex = 1
    poly1_pt = Point(1.0, 0.0, 0.0)
    poly2_pt = Point(0.0, 1.0, 0.0)
    poly1, poly2 = poly.slice(
        slicing_points,
        name1="poly1",
        pt1=poly1_pt,
        name2="poly2",
        pt2=poly2_pt,
    )

    assert np.isclose(poly1.normal, poly.normal).all()
    assert np.isclose(poly2.normal, poly.normal).all()
    assert np.isclose(poly.area, poly1.area + poly2.area)
    assert poly1.is_point_inside(poly1_pt)
    assert poly2.is_point_inside(poly2_pt)


def test_polygon_slice_with_1_point_raises_error():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p1, p2, p3, p4])

    # Three slicing points
    slicing_points = [
        Point(0.5, 0.5, 0.0),
    ]
    with pytest.raises(GeometryError):
        _ = poly.slice(slicing_points, name1="1", pt1=p1, name2="2", pt2=p2)


def test_polygon_slice_with_wrong_pt1_pt2_raises_error():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p1, p2, p3, p4])

    # Three slicing points
    slicing_points = [
        Point(0.0, 0.0, 0.0),
        Point(0.5, 1.0, 0.0),
    ]
    poly1_pt = Point(0.0, 0.0, 0.0)
    poly2_pt = Point(0.5, 1.0, 0.0)
    with pytest.raises(GeometryError):
        _ = poly.slice(
            slicing_points,
            name1="poly1",
            pt1=poly1_pt,
            name2="poly2",
            pt2=poly2_pt,
        )

    poly1_pt = Point(9.0, 0.0, 0.0)
    poly2_pt = Point(0.5, 1.0, 9.0)
    with pytest.raises(GeometryError):
        _ = poly.slice(
            slicing_points,
            name1="poly1",
            pt1=poly1_pt,
            name2="poly2",
            pt2=poly2_pt,
        )


def test_is_point_inside_margin():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    p3 = Point(1.0, 1.0, 0.0)
    p4 = Point(0.0, 1.0, 0.0)
    poly = Polygon([p1, p2, p3, p4])

    ptest = Point(0.1, 0.1, 0.0)
    assert poly.is_point_inside_margin(ptest, 0.099)
    assert not poly.is_point_inside_margin(ptest, 0.11)



if __name__ == "__main__":
    # test_polygon_slice_start_and_end_at_a_vertex()
    # test_polygon_slice_start_and_end_at_different_edges_vertical()
    # test_polygon_slice_start_and_end_at_different_edges_horizontal_5points()
    # test_polygon_slice_start_and_end_at_same_edge()
    test_polygon_slice_multiple_points_at_edge()
    # test_polygon_slice_with_wrong_pt1_pt2_raises_error()
