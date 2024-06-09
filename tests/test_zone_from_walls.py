from building3d import random_id
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone
from building3d.geom.solid import Solid


def test_zone_from_walls():
    # Cube 1x1x1m3
    p0 = Point(0.0, 0.0, 0.0)
    p1 = Point(1.0, 0.0, 0.0)
    p2 = Point(1.0, 1.0, 0.0)
    p3 = Point(0.0, 1.0, 0.0)
    p4 = Point(0.0, 0.0, 1.0)
    p5 = Point(1.0, 0.0, 1.0)
    p6 = Point(1.0, 1.0, 1.0)
    p7 = Point(0.0, 1.0, 1.0)

    poly_floor = Polygon([p0, p3, p2, p1])
    poly_wall0 = Polygon([p0, p1, p5, p4])
    poly_wall1 = Polygon([p1, p2, p6, p5])
    poly_wall2 = Polygon([p3, p7, p6, p2])
    poly_wall3 = Polygon([p0, p4, p7, p3])
    poly_ceiling = Polygon([p4, p5, p6, p7])

    floor = Wall()
    floor.add_polygon(poly_floor)

    walls = Wall()
    walls.add_polygon(poly_wall0)
    walls.add_polygon(poly_wall1)
    walls.add_polygon(poly_wall2)
    walls.add_polygon(poly_wall3)

    ceiling = Wall()
    ceiling.add_polygon(poly_ceiling)

    zone = Zone()
    solid = Solid([floor, walls, ceiling], name=random_id())
    zone.add_solid(solid)

    assert len(zone.solids) == 1
    assert len(zone.solids[solid.name].polygons()) == 6
