import numpy as np

from building3d.geom.line import create_points_between_2_points
from building3d.geom.line import distance_point_to_edge
from building3d.geom.point import Point


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

    d = distance_point_to_edge(ptest1, p1, p2)
    assert np.isclose(d, 1)
    d = distance_point_to_edge(ptest2, p1, p2)
    assert np.isclose(d, 1)
    d = distance_point_to_edge(ptest3, p1, p2)
    assert np.isclose(d, 1)
    d = distance_point_to_edge(ptest4, p1, p2)
    assert np.isclose(d, np.sqrt(2))
