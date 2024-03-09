import pytest

from building3d.geom.exceptions import GeometryError
from building3d.geom.point import Point
from building3d.geom.wall import Wall


def test_too_few_points():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    wall = Wall("wall0", [p0, p1])

    with pytest.raises(GeometryError):
        wall.verify()


def test_points_not_coplanar():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(6.0, 6.0, 6.0)
    wall = Wall("wall0", [p0, p1, p2, p3])
    with pytest.raises(GeometryError):
        wall.verify()
