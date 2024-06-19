import numpy as np

from building3d.geom.line import create_point_between_2_points_at_distance
from building3d.geom.line import create_points_between_2_points
from building3d.geom.line import distance_point_to_edge
from building3d.geom.line import is_point_on_segment
from building3d.geom.line import line_intersection
from building3d.geom.line import line_segment_intersection
from building3d.geom.point import Point


def test_create_point_between_2_points_at_distance():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    distance = 0.5
    pnew = create_point_between_2_points_at_distance(p1, p2, distance)
    assert pnew == Point(0.5, 0.0, 0.0)
    distance = 0.1
    pnew = create_point_between_2_points_at_distance(p1, p2, distance)
    assert pnew == Point(0.1, 0.0, 0.0)
    distance = 0.9
    pnew = create_point_between_2_points_at_distance(p1, p2, distance)
    assert pnew == Point(0.9, 0.0, 0.0)


def test_create_points_between_2_points():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(1.0, 0.0, 0.0)
    num = 5
    points = create_points_between_2_points(p1, p2, num)

    xvals = set([p.x for p in points])
    assert {0.0, 0.2, 0.4, 0.6, 0.8, 1.0} == xvals


def test_distance_point_to_edge():
    p1 = Point(0.0, 0.0, 0.0)
    p2 = Point(0.0, 1.0, 0.0)
    ptest1 = Point(1.0, 0.0, 0.0)  # distance = 1
    ptest2 = Point(1.0, 0.5, 0.0)  # distance = 1
    ptest3 = Point(1.0, 1.0, 0.0)  # distance = 1
    ptest4 = Point(1.0, 2.0, 0.0)  # distance = np.sqrt(2)
    ptest5 = Point(0.0, 0.5, 0.0)  # distance = 0

    d = distance_point_to_edge(ptest1, p1, p2)
    assert np.isclose(d, 1)
    d = distance_point_to_edge(ptest2, p1, p2)
    assert np.isclose(d, 1)
    d = distance_point_to_edge(ptest3, p1, p2)
    assert np.isclose(d, 1)
    d = distance_point_to_edge(ptest4, p1, p2)
    assert np.isclose(d, np.sqrt(2))
    d = distance_point_to_edge(ptest5, p1, p2)
    assert np.isclose(d, 0)


def test_is_point_on_segment():
    pt2 = Point(2.0, 0.0, 0.0)
    pt1 = Point(0.0, 0.0, 0.0)

    ptest = Point(1.0, 0.0, 0.0)
    assert is_point_on_segment(ptest, pt1, pt2) is True
    ptest = Point(1.0, 1.0, 0.0)
    assert is_point_on_segment(ptest, pt1, pt2) is False
    ptest = Point(2.0, 0.0, 0.0)
    assert is_point_on_segment(ptest, pt1, pt2) is True
    ptest = Point(0.0, 0.0, 0.0)
    assert is_point_on_segment(ptest, pt1, pt2) is True
    ptest = Point(-0.001, 0.0, 0.0)
    assert is_point_on_segment(ptest, pt1, pt2) is False


def test_line_intersection():
    p1 = Point(0.0, 0.0, 0.0)
    d1 = np.array([0.0, 1.0, 0.0])
    p2 = Point(1.0, 2.0, 0.0)
    d2 = np.array([-0.1, 0.0, 0.0])
    ptest = line_intersection(p1, d1, p2, d2)
    assert ptest == Point(0.0, 2.0, 0.0)

    p1 = Point(0.0, 0.0, 0.0)
    d1 = np.array([0.0, 1.0, 0.0])
    p2 = Point(2.0, 2.0, 0.0)
    d2 = np.array([-0.1, 0.0, 0.0])
    ptest = line_intersection(p1, d1, p2, d2)
    assert ptest == Point(0.0, 2.0, 0.0)

    p1 = Point(0.0, 0.0, 0.0)
    d1 = np.array([0.0, 1.0, 0.0])
    p2 = Point(2.0, 2.0, 0.0)
    d2 = np.array([0.0, 1.0, 0.0])
    ptest = line_intersection(p1, d1, p2, d2)
    assert ptest is None

    p1 = Point(0.0, 0.0, 0.0)
    d1 = np.array([0.0, 1.0, 0.0])
    p2 = Point(2.0, 2.0, 0.0)
    d2 = np.array([0.0, 0.0, 0.0])
    ptest = line_intersection(p1, d1, p2, d2)
    assert ptest is None

    p1 = Point(0.0, 0.0, 0.0)
    d1 = np.array([0.0, 1.0, 0.0])
    p2 = Point(0.0, 0.0, 0.0)
    d2 = np.array([0.0, 1.0, 0.0])
    ptest = line_intersection(p1, d1, p2, d2)
    assert ptest is None


def test_line_segment_intersection():
    pa1 = Point(0.0, 0.0, 0.0)
    pb1 = Point(2.0, 0.0, 0.0)
    pa2 = Point(1.0, 1.0, 0.0)
    pb2 = Point(1.0, -1.0, 0.0)
    ptest = line_segment_intersection(pa1, pb1, pa2, pb2)
    assert ptest == Point(1.0, 0.0, 0.0)

    pa1 = Point(0.0, 0.0, 0.0)
    pb1 = Point(2.0, 0.0, 0.0)
    pa2 = Point(0.0, 1.0, 0.0)
    pb2 = Point(0.0, -1.0, 0.0)
    ptest = line_segment_intersection(pa1, pb1, pa2, pb2)
    assert ptest == Point(0.0, 0.0, 0.0)

    pa1 = Point(0.0, 0.0, 0.0)
    pb1 = Point(2.0, 0.0, 0.0)
    pa2 = Point(0.0, 0.0, 0.0)
    pb2 = Point(0.0, 1.0, 0.0)
    ptest = line_segment_intersection(pa1, pb1, pa2, pb2)
    assert ptest == Point(0.0, 0.0, 0.0)

    pa1 = Point(0.0, 0.0, 0.0)
    pb1 = Point(2.0, 0.0, 0.0)
    pa2 = Point(0.0, 0.0, 0.0)
    pb2 = Point(-2.0, 0.0, 0.0)
    ptest = line_segment_intersection(pa1, pb1, pa2, pb2)
    assert ptest is None  # Because same directions

    pa1 = Point(0.0, 0.0, 0.0)
    pb1 = Point(2.0, 0.0, 0.0)
    pa2 = Point(1.0, 0.0, 0.0)
    pb2 = Point(-2.0, 0.0, 0.0)
    ptest = line_segment_intersection(pa1, pb1, pa2, pb2)
    assert ptest is None  # Because same directions

    pa1 = Point(0.0, 0.0, 0.0)
    pb1 = Point(2.0, 0.0, 0.0)
    pa2 = Point(1.0, 1.0, 1.0)
    pb2 = Point(1.0, -1.0, 1.0)
    ptest = line_segment_intersection(pa1, pb1, pa2, pb2)
    assert ptest is None
