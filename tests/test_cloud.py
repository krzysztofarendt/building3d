from building3d.geom.cloud import are_points_in_set
from building3d.geom.point import Point


def test_are_points_in_set():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 1.0, 1.0)
    p2 = Point(2.0, 2.0, 2.0)
    p3 = Point(3.0, 3.0, 3.0)
    cloud1 = [p0, p1]
    cloud2 = [p0, p1, p2, p3]
    assert are_points_in_set(cloud1, cloud2)
    assert not are_points_in_set(cloud2, cloud1)
