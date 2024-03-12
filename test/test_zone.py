import pytest

from building3d.geom.exceptions import GeometryError
from building3d.geom.point import Point
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone


def test_correct_space_geometry():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    floor = Wall("floor", [p0, p3, p2, p1])
    wall0 = Wall("wall0", [p0, p1, p5, p4])
    wall1 = Wall("wall1", [p1, p2, p6, p5])
    wall2 = Wall("wall2", [p3, p7, p6, p2])
    wall3 = Wall("wall3", [p0, p4, p7, p3])
    ceiling = Wall("ceiling", [p4, p5, p6, p7])

    room = Zone("room", [floor, wall0, wall1, wall2, wall3, ceiling])
    room.verify(throw=True)


def test_points_not_shared_by_2_walls():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)
    p4err = Point(0.0, 0.0, 2.0)
    p5err = Point(1.0, 0.0, 2.0)
    p6err = Point(1.0, 1.0, 2.0)
    p7err = Point(0.0, 1.0, 2.0)

    floor = Wall("floor", [p0, p3, p2, p1])
    wall0 = Wall("wall0", [p0, p1, p5, p4])
    wall1 = Wall("wall1", [p1, p2, p6, p5])
    wall2 = Wall("wall2", [p3, p7, p6, p2])
    wall3 = Wall("wall3", [p0, p4, p7, p3])
    # Make ceiling too high (not attached to walls)
    ceiling = Wall("ceiling", [p4err, p5err, p6err, p7err])

    room = Zone("room", [floor, wall0, wall1, wall2, wall3, ceiling])

    with pytest.raises(GeometryError):
        room.verify(throw=True)
