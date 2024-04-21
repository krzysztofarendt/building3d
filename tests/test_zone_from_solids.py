import pytest

from building3d.geom.exceptions import GeometryError
from building3d.geom.point import Point
from building3d.geom.polygon import Polygon
from building3d.geom.solid import Solid
from building3d.geom.wall import Wall
from building3d.geom.zone import Zone

MAIN_SOLID_NAME = "main_solid"
SUB_SOLID_NAME = "sub_solid"


def make_zone(subsolid_move=[0.0, 0.0, 0.0]) -> Zone:
    # Large solid, cube 1x1x1m3
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

    main_sld = Solid([floor, walls, ceiling], name=MAIN_SOLID_NAME)

    # Small solid, cube 0.5x0.5x0.5m3
    # Point p8 overlapping with point p0 (on purpose)
    translate = subsolid_move
    p8 = Point(0.0, 0.0, 0.0) + translate  # 0
    p9 = Point(0.5, 0.0, 0.0) + translate  # 1
    p10 = Point(0.5, 0.5, 0.0) + translate  # 2
    p11 = Point(0.0, 0.5, 0.0) + translate  # 3
    p12 = Point(0.0, 0.0, 0.5) + translate  # 4
    p13 = Point(0.5, 0.0, 0.5) + translate  # 5
    p14 = Point(0.5, 0.5, 0.5) + translate  # 6
    p15 = Point(0.0, 0.5, 0.5) + translate  # 7

    poly_floor_small = Polygon([p8, p11, p10, p9])
    poly_wall0_small = Polygon([p8, p9, p13, p12])
    poly_wall1_small = Polygon([p9, p10, p14, p13])
    poly_wall2_small = Polygon([p11, p15, p14, p10])
    poly_wall3_small = Polygon([p8, p12, p15, p11])
    poly_ceiling_small = Polygon([p12, p13, p14, p15])

    floor_small = Wall()
    floor_small.add_polygon(poly_floor_small)

    walls_small = Wall()
    walls_small.add_polygon(poly_wall0_small)
    walls_small.add_polygon(poly_wall1_small)
    walls_small.add_polygon(poly_wall2_small)
    walls_small.add_polygon(poly_wall3_small)

    ceiling_small = Wall()
    ceiling_small.add_polygon(poly_ceiling_small)

    sub_sld = Solid([floor_small, walls_small, ceiling_small], name=SUB_SOLID_NAME)

    zone = Zone()
    zone.add_solid_instance(main_sld)
    zone.add_solid_instance(sub_sld, parent=main_sld.name)

    return zone


def test_zone_subsolid_entirely_inside():
    zone = make_zone(subsolid_move=[0.1, 0.1, 0.1])
    assert len(zone.solids.keys()) == 2
    assert len(zone.solidgraph[MAIN_SOLID_NAME]) == 1


def test_zone_subsolid_shares_some_boundary():
    zone = make_zone()
    assert len(zone.solids.keys()) == 2
    assert len(zone.solidgraph[MAIN_SOLID_NAME]) == 1


def test_zone_incorrect_geometry():
    with pytest.raises(GeometryError):
        _ = make_zone(subsolid_move=[-0.1, -0.1, -0.1])
    with pytest.raises(GeometryError):
        _ = make_zone(subsolid_move=[5.0, 0.0, 0.0])
