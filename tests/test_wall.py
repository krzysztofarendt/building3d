from building3d import random_id
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall


def test_wall():
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    poly0 = Polygon(random_id(), [p0, p1, p2, p3])

    p4 = Point(0.25, 0.25, 0.0)
    p5 = Point(0.75, 0.25, 0.0)
    p6 = Point(0.75, 0.75, 0.0)
    p7 = Point(0.25, 0.75, 0.0)
    poly1 = Polygon(random_id(), [p4, p5, p6, p7])

    wall = Wall(random_id())
    wall.add_polygon(poly0)
    wall.add_polygon(poly1, parent=poly0.name)

    assert len(wall.polygons.keys()) == 2
    assert len(wall.polygraph[poly0.name]) == 1
