import numpy as np

from building3d.geom.numba.points import new_point
from building3d.geom.numba.points import points_equal
from building3d.geom.numba.points import is_point_in_array
from building3d.geom.numba.points import are_points_collinear
from building3d.geom.numba.points import are_points_coplanar
from building3d.geom.numba.points import point_to_str
from building3d.geom.numba.points import roll_forward
from building3d.geom.numba.points import new_point_between_2_points
from building3d.geom.numba.points import many_new_points_between_2_points
from building3d.geom.numba.points import is_point_on_segment
from building3d.geom.numba.points.distance import distance_point_to_edge
from building3d.geom.numba.points.intersections import line_intersection
from building3d.geom.numba.points.intersections import line_segment_intersection
from building3d.geom.numba.vectors import new_vector
from building3d.geom.numba.types import FLOAT


def test_new_point():
    pt = new_point(0.0, 0.0, 0.0)
    assert isinstance(pt, np.ndarray)
    assert type(pt[0]) is FLOAT


def test_is_point_in_array():
    pt = new_point(0.0, 0.0, 0.0)

    arr = np.vstack(
        (
            new_point(1.0, 1.0, 1.0),
            new_point(-1.0, -1.0, -1.0),
            new_point(0.0, 0.0, 0.0),
        )
    )

    assert is_point_in_array(pt, arr) is True
    assert is_point_in_array(pt, arr[:2]) is False


def test_are_points_collinear():
    p1 = new_point(0.0, 0.0, 0.0)
    p2 = new_point(1.0, 0.0, 0.0)
    p3 = new_point(2.0, 0.0, 0.0)
    assert are_points_collinear(np.vstack([p1, p2, p3])) is True
    p3 = new_point(2.0, 1.0, 0.0)
    assert are_points_collinear(np.vstack([p1, p2, p3])) is False
    p3 = new_point(-2.0, 0.0, 0.0)
    assert are_points_collinear(np.vstack([p1, p2, p3])) is True


def test_are_points_coplanar():
    p1 = new_point(0.0, 0.0, 0.0)
    p2 = new_point(1.0, 0.5, 0.0)
    p3 = new_point(2.0, 0.0, 0.0)
    p4 = new_point(1.0, 1.0, 0.0)
    assert are_points_coplanar(np.vstack([p1, p2, p3, p4])) is True
    p4 = new_point(1.0, 1.0, 1.0)
    assert are_points_coplanar(np.vstack([p1, p2, p3, p4])) is False

    assert are_points_coplanar(np.vstack([p1, p2, p3])) is True
    assert are_points_coplanar(np.vstack([p1, p2])) is True
    assert are_points_coplanar(np.vstack([p1])) is True


def test_point_to_str():
    p = new_point(0.0, 0.0, 0.0)
    s = point_to_str(p)
    assert isinstance(s, str)
    assert "x=0.00" in s and "y=0.00" in s and "z=0.00" in s and "id=" in s


def test_roll_forward():
    p0 = new_point(0.0, 0.0, 0.0)
    p1 = new_point(1.0, 0.0, 0.0)
    p2 = new_point(2.0, 0.0, 0.0)
    pts = np.vstack((p0, p1, p2))
    assert np.allclose(pts[0], p0)
    assert np.allclose(pts[1], p1)
    assert np.allclose(pts[2], p2)
    pts = roll_forward(pts)
    assert np.allclose(pts[0], p2)
    assert np.allclose(pts[1], p0)
    assert np.allclose(pts[2], p1)


def test_new_point_between_2_points():
    p1 = new_point(0.0, 0.0, 0.0)
    p2 = new_point(1.0, 0.0, 0.0)
    rel_dist = 0.5
    pnew = new_point_between_2_points(p1, p2, rel_dist)
    assert np.allclose(pnew, new_point(0.5, 0.0, 0.0))
    rel_dist = 0.1
    pnew = new_point_between_2_points(p1, p2, rel_dist)
    assert np.allclose(pnew, new_point(0.1, 0.0, 0.0))
    rel_dist = 0.9
    pnew = new_point_between_2_points(p1, p2, rel_dist)
    assert np.allclose(pnew, new_point(0.9, 0.0, 0.0))


def test_many_new_points_between_2_points():
    pt1 = new_point(0, 0, 0)
    pt2 = new_point(1, 0, 0)
    num = 4
    pts = many_new_points_between_2_points(pt1, pt2, num)
    expected = np.array(
        [
            [0.0, 0, 0],
            [0.2, 0, 0],
            [0.4, 0, 0],
            [0.6, 0, 0],
            [0.8, 0, 0],
            [1.0, 0, 0],
        ],
        dtype=FLOAT,
    )
    assert np.allclose(pts, expected)


def test_is_point_on_segment():
    pt2 = new_point(2, 0, 0)
    pt1 = new_point(0, 0, 0)
    ptest = new_point(1, 0, 0)
    assert is_point_on_segment(ptest, pt1, pt2) is True
    ptest = new_point(1, 1, 0)
    assert is_point_on_segment(ptest, pt1, pt2) is False
    ptest = new_point(2, 0, 0)
    assert is_point_on_segment(ptest, pt1, pt2) is True
    ptest = new_point(0, 0, 0)
    assert is_point_on_segment(ptest, pt1, pt2) is True
    ptest = new_point(-0.001, 0, 0)
    assert is_point_on_segment(ptest, pt1, pt2) is False


def test_distance_point_to_edge():
    pt1 = new_point(0.0, 0.0, 0.0)
    pt2 = new_point(0.0, 1.0, 0.0)
    ptest1 = new_point(1.0, 0.0, 0.0)  # distance = 1
    ptest2 = new_point(1.0, 0.5, 0.0)  # distance = 1
    ptest3 = new_point(1.0, 1.0, 0.0)  # distance = 1
    ptest4 = new_point(1.0, 2.0, 0.0)  # distance = np.sqrt(2)
    ptest5 = new_point(0.0, 0.5, 0.0)  # distance = 0

    d = distance_point_to_edge(ptest1, pt1, pt2)
    assert np.isclose(d, 1)
    d = distance_point_to_edge(ptest2, pt1, pt2)
    assert np.isclose(d, 1)
    d = distance_point_to_edge(ptest3, pt1, pt2)
    assert np.isclose(d, 1)
    d = distance_point_to_edge(ptest4, pt1, pt2)
    assert np.isclose(d, np.sqrt(2))
    d = distance_point_to_edge(ptest5, pt1, pt2)
    assert np.isclose(d, 0)


def test_line_intersection():
    pt1 = new_point(0.0, 0.0, 0.0)
    d1 = new_vector(0.0, 1.0, 0.0)
    pt2 = new_point(1.0, 2.0, 0.0)
    d2 = new_vector(-0.1, 0.0, 0.0)
    ptest = line_intersection(pt1, d1, pt2, d2)
    assert points_equal(ptest, new_point(0.0, 2.0, 0.0))

    pt1 = new_point(0.0, 0.0, 0.0)
    d1 = new_vector(0.0, 1.0, 0.0)
    pt2 = new_point(2.0, 2.0, 0.0)
    d2 = new_vector(-0.1, 0.0, 0.0)
    ptest = line_intersection(pt1, d1, pt2, d2)
    assert points_equal(ptest, new_point(0.0, 2.0, 0.0))

    pt1 = new_point(0.0, 0.0, 0.0)
    d1 = new_vector(0.0, 1.0, 0.0)
    pt2 = new_point(2.0, 2.0, 0.0)
    d2 = new_vector(0.0, 1.0, 0.0)
    ptest = line_intersection(pt1, d1, pt2, d2)
    assert np.isnan(ptest).any()

    pt1 = new_point(0.0, 0.0, 0.0)
    d1 = new_vector(0.0, 1.0, 0.0)
    pt2 = new_point(2.0, 2.0, 0.0)
    d2 = new_vector(0.0, 0.0, 0.0)
    ptest = line_intersection(pt1, d1, pt2, d2)
    assert np.isnan(ptest).any()

    pt1 = new_point(0.0, 0.0, 0.0)
    d1 = new_vector(0.0, 1.0, 0.0)
    pt2 = new_point(0.0, 0.0, 0.0)
    d2 = new_vector(0.0, 1.0, 0.0)
    ptest = line_intersection(pt1, d1, pt2, d2)
    assert np.isnan(ptest).any()


def test_line_segment_intersection():
    pa1 = new_point(0.0, 0.0, 0.0)
    pb1 = new_point(2.0, 0.0, 0.0)
    pa2 = new_point(1.0, 1.0, 0.0)
    pb2 = new_point(1.0, -1.0, 0.0)
    ptest = line_segment_intersection(pa1, pb1, pa2, pb2)
    assert points_equal(ptest, new_point(1.0, 0.0, 0.0))

    pa1 = new_point(0.0, 0.0, 0.0)
    pb1 = new_point(2.0, 0.0, 0.0)
    pa2 = new_point(0.0, 1.0, 0.0)
    pb2 = new_point(0.0, -1.0, 0.0)
    ptest = line_segment_intersection(pa1, pb1, pa2, pb2)
    assert points_equal(ptest, new_point(0.0, 0.0, 0.0))

    pa1 = new_point(0.0, 0.0, 0.0)
    pb1 = new_point(2.0, 0.0, 0.0)
    pa2 = new_point(0.0, 0.0, 0.0)
    pb2 = new_point(0.0, 1.0, 0.0)
    ptest = line_segment_intersection(pa1, pb1, pa2, pb2)
    assert points_equal(ptest, new_point(0.0, 0.0, 0.0))

    pa1 = new_point(0.0, 0.0, 0.0)
    pb1 = new_point(2.0, 0.0, 0.0)
    pa2 = new_point(0.0, 0.0, 0.0)
    pb2 = new_point(-2.0, 0.0, 0.0)
    ptest = line_segment_intersection(pa1, pb1, pa2, pb2)
    assert np.isnan(ptest).any()  # Because same directions

    pa1 = new_point(0.0, 0.0, 0.0)
    pb1 = new_point(2.0, 0.0, 0.0)
    pa2 = new_point(1.0, 0.0, 0.0)
    pb2 = new_point(-2.0, 0.0, 0.0)
    ptest = line_segment_intersection(pa1, pb1, pa2, pb2)
    assert np.isnan(ptest).any()  # Because same directions

    pa1 = new_point(0.0, 0.0, 0.0)
    pb1 = new_point(2.0, 0.0, 0.0)
    pa2 = new_point(1.0, 1.0, 1.0)
    pb2 = new_point(1.0, -1.0, 1.0)
    ptest = line_segment_intersection(pa1, pb1, pa2, pb2)
    assert np.isnan(ptest).any()  # Because same directions
